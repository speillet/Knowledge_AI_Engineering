# Apptainer & Singularity — Flashcards
Tags: #flashcards #conteneurs #apptainer #singularity #hpc
<!-- summary: usage en HPC, filiation Singularity → Apptainer, format SIF et conversion des images Docker, `--nv`, permissions des bind mounts, environnement hôte, image immuable. -->


Dans quel environnement Apptainer est-il particulièrement utilisé ? <!--anki:755e35286742334e2d28-->
?
Dans les environnements **HPC**, calcul scientifique, clusters partagés (Slurm, MPI) et workloads GPU : pas de démon root, le conteneur s'exécute **avec l'identité de l'utilisateur** (détails dans [[13-apptainer-inference-hpc|Apptainer & inférence HPC]]).

Cette intégration facilite l'accès aux répertoires partagés et aux ressources allouées par l'ordonnanceur. Elle n'accorde pas de droits supplémentaires sur ces données. Le niveau d'isolation et les mécanismes de privilège dépendent de l'installation ; examiner la configuration du cluster avant de considérer le conteneur comme une sandbox de code non fiable.

---

Quelle relation existe entre Singularity et Apptainer ? <!--anki:75255f5a4e5e676b2342-->
?
**Apptainer est la continuation du projet Singularity** : le projet a été renommé en 2021 en rejoignant la **Linux Foundation**, tandis que le nom Singularity a été conservé par une offre commerciale. Conséquence pratique : de la documentation et des scripts circulent encore avec la commande `singularity`, qui reste souvent disponible en alias.

Le nom seul ne suffit pas à identifier le logiciel : SingularityCE et les offres commerciales ont aussi leur trajectoire. Relever binaire, version et documentation correspondante avant de transposer une option ou un comportement de montage.

---

Quel est le format d'image historiquement natif d'Apptainer/Singularity ? <!--anki:4e496b6d7331432b713f-->
?
**SIF — Singularity Image Format** : un **fichier unique**, contrairement aux couches empilées d'une image OCI. Il peut être **signé** et exécuté directement, ce qui le rend facile à copier, archiver et partager sur un système de fichiers de cluster.

Un SIF est monté **en lecture seule** : pour écrire, on monte un répertoire de l'hôte avec `--bind` ou une couche temporaire avec `--writable-tmpfs`. Sur un système de fichiers parallèle comme Lustre, lire un seul gros fichier coûte bien moins cher que d'ouvrir des milliers de petits fichiers de couches : c'est un atout décisif en HPC.

---

Une image SIF est-elle simplement une image OCI ? <!--anki:4d7c436a753d627a6e3c-->
?
**Non.** Une image [[01-oci|OCI]] décrit configuration et couches ; un **SIF** regroupe dans un fichier des objets, généralement dont un système de fichiers compressé en lecture seule.

Apptainer peut convertir une image récupérée via `docker://` en SIF. Ce SIF peut aussi être publié dans un registre OCI compatible via **`oras://`**, comme artefact : cela ne le transforme pas en image directement exécutable par Docker.

Exemple : partager `modele.sif` par registre évite un transfert manuel sur chaque cluster, mais les consommateurs doivent comprendre le format SIF. Distinguer **format d'exécution et canal de distribution**, puis vérifier provenance et compatibilité de la conversion.

---

À ne pas confondre : Apptainer et Docker sur le plan de la sécurité ? <!--anki:6e52296f4e61242e4541-->
?
- **Docker en mode rootful** : l'accès au socket du démon donne des pouvoirs équivalents à root. Le mode **rootless** change ce modèle.
- **Apptainer** : pas de démon permanent, exécution généralement avec l'identité et les droits de l'utilisateur, adaptée aux politiques [[13-apptainer-inference-hpc|HPC]].

Cela ne rend pas une image inoffensive : elle peut lire ou modifier les fichiers montés accessibles à l'utilisateur. Vérifier montages, réseau et configuration locale ; l'admission sur un cluster dépend de sa politique, pas seulement du produit.

---

Comment exécuter une commande dans une image Apptainer ? <!--anki:785338455e3a71633e63-->
?
```bash
apptainer exec image.sif python train.py     # une commande
apptainer shell image.sif                    # un shell interactif
apptainer run image.sif                      # le runscript de l'image
```
Par défaut, le **répertoire courant et le dossier personnel sont montés** et les variables d'environnement sont héritées : un script peut donc marcher chez vous et échouer ailleurs. Pour isoler, on utilise `--cleanenv` et `--no-home`.

Aucun démon ne garde de conteneur actif : chaque `exec` démarre un conteneur pour la durée de la commande. Pour un service durable, comme un serveur d'inférence, `apptainer instance start image.sif nom` lance une instance en arrière-plan, que l'on arrête avec `apptainer instance stop nom`.

---

À quoi sert `--nv` avec Apptainer ? <!--anki:78416b386d2b283c4c2f-->
?
À fournir au conteneur l'accès nécessaire à l'environnement **[[09-gpu-conteneurs|NVIDIA/GPU]]** de la machine hôte.

```bash
apptainer exec --nv model.sif python inference.py
```

L'option rend accessibles les périphériques et les bibliothèques NVIDIA nécessaires, tandis que le module noyau reste celui de l'hôte. Elle n'installe pas un driver manquant et ne réserve pas un GPU dans Slurm. Il faut une allocation valide, une compatibilité CUDA/driver et les dépendances applicatives dans l'image.

Tester un petit calcul avec le framework du modèle puis une inférence représentative. Voir le GPU avec un outil système ne prouve pas que tous les kernels nécessaires fonctionnent ni qu'il reste assez de VRAM pour le contexte prévu.

---

Pourquoi un bind mount Apptainer doit-il être revu comme une permission d'accès aux données hôtes ? <!--anki:6663353433363966343166303438636461383836343031343864373330346366-->
?
Un **bind mount** rend un chemin de l'hôte visible dans le conteneur avec les droits effectifs applicables. L'image SIF ne suffit donc pas à décrire les données accessibles pendant le job.

Inspecter montages explicites et automatiques, limiter les chemins et utiliser la lecture seule lorsque l'écriture n'est pas nécessaire. Tester avec l'identité du job et le système de fichiers partagé réel. Un montage trop large peut exposer résultats d'autres expériences ou secrets du répertoire personnel. L'immutabilité de l'image ne protège pas un répertoire hôte monté en écriture.

---

Pourquoi une image SIF identique peut-elle produire des résultats différents sur deux machines ? <!--anki:3938383534356265633737633432303239393435333238653530333532393636-->
?
L'exécution dépend aussi **du kernel, des bibliothèques exposées, de l'environnement et des fichiers montés**. L'image ne fige pas tout l'hôte.

Documenter les dépendances nécessaires et vérifier les variables et montages effectifs. Pour le GPU, tester la compatibilité sur chaque cible. La reproductibilité demande un manifeste d'exécution ; conserver seulement le fichier SIF ne suffit pas à reproduire tous les résultats numériques et accès aux données.

---

Pourquoi séparer les sorties d'un calcul Apptainer du contenu immuable de l'image SIF ? <!--anki:3137663866346338343435643437373039326464663731313666353061323330-->
?
Les résultats et caches sont **des données d'exécution**, tandis que l'image décrit l'environnement. Utiliser des répertoires de sortie explicitement montés facilite traçabilité, permissions et conservation.

Attribuer un espace par job pour éviter les collisions. Vérifier les droits réels de l'utilisateur et les montages automatiques. Une image en lecture seule ne rend pas les répertoires hôtes montés en écriture inoffensifs.

---

## Mises en situation

Mise en situation : tes expérimentations tournent dans une image Docker, mais le cluster de calcul de ton laboratoire n'autorise que Apptainer. Comment procèdes-tu ? <!--anki:714676425960586c7734-->
?
1. **Convertir** : `apptainer pull mon.sif docker://mon-image:tag`, ce qui produit un fichier SIF unique
2. **Comprendre le modèle** : pas de démon root, le conteneur tourne **avec ton identité**, ce qui explique l'autorisation
3. **Accès GPU** : ajouter `--nv` pour exposer le driver NVIDIA de la machine hôte
4. **Données et poids** : montés depuis le système de fichiers partagé, jamais embarqués dans l'image
5. **Vérifier** : version de CUDA compatible avec le driver du cluster ([[13-apptainer-inference-hpc|Apptainer & HPC]])

**Piège** : supposer que les chemins et les utilisateurs de l'image Docker existent tels quels dans le conteneur Apptainer.

---

Mise en situation : un collègue veut stocker les poids d'un modèle de 40 Go dans le fichier SIF « pour que tout soit reproductible ». Qu'en penses-tu ? <!--anki:755257727d5f58674535-->
?
1. **Avantage réel** : un fichier unique et immuable, facile à copier et à archiver
2. **Inconvénients** : image énorme, reconstruction complète à chaque version de modèle, stockage dupliqué sur le cluster
3. **Pratique courante** : image avec le runtime, poids sur le **système de fichiers partagé**, montés à l'exécution
4. **Reproductibilité autrement** : version des poids épinglée et vérifiée par empreinte ([[10-images-modeles-poids|images & poids]])
5. **Cas où le SIF gagne** : nœuds sans accès réseau, ou besoin d'un artefact autoportant

**Piège** : confondre immuabilité et reproductibilité, qui s'obtient aussi par le versionnage.

---

## Sources

- [Apptainer — accès aux périphériques et bibliothèques GPU](https://apptainer.org/docs/user/main/gpu.html)
- [Apptainer — publication de SIF avec push et ORAS](https://apptainer.org/docs/user/latest/cli/apptainer_push.html) — consultation ciblée du 6 novembre 2026.

- Complément du 14 novembre 2026 — Montages et dépendances hôtes : [Apptainer — Bind Paths and Mounts](https://apptainer.org/docs/user/latest/bind_paths_and_mounts.html).

## Connexions
- [[13-apptainer-inference-hpc|Apptainer & inférence HPC]] — usage avancé pour le serving LLM
- [[09-gpu-conteneurs|GPU en conteneur]] — équivalent `--gpus` / `--nv`
- [[02-docker-images-registries|Docker & images]] — interopérabilité `docker://`
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
