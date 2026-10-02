# Apptainer & Singularity — Flashcards
Tags: #flashcards #conteneurs #apptainer #singularity #hpc
<!-- summary: usage en HPC, filiation Singularity → Apptainer, format SIF et conversion des images Docker, `--nv`. -->


Dans quel environnement Apptainer est-il particulièrement utilisé ? <!--anki:755e35286742334e2d28-->
?
Dans les environnements **HPC**, calcul scientifique, clusters partagés (Slurm, MPI) et workloads GPU : pas de démon root, le conteneur s'exécute **avec l'identité de l'utilisateur** (détails dans [[13-apptainer-inference-hpc|Apptainer & inférence HPC]]).

---

Quelle relation existe entre Singularity et Apptainer ? <!--anki:75255f5a4e5e676b2342-->
?
**Apptainer est la continuation du projet Singularity** : le projet a été renommé en 2021 en rejoignant la **Linux Foundation**, tandis que le nom Singularity a été conservé par une offre commerciale. Conséquence pratique : de la documentation et des scripts circulent encore avec la commande `singularity`, qui reste souvent disponible en alias.

---

Quel est le format d'image historiquement natif d'Apptainer/Singularity ? <!--anki:4e496b6d7331432b713f-->
?
**SIF — Singularity Image Format** : un **fichier unique**, contrairement aux couches empilées d'une image OCI. Il peut être **signé** et exécuté directement, ce qui le rend facile à copier, archiver et partager sur un système de fichiers de cluster.

---

Une image SIF est-elle simplement une image OCI ? <!--anki:4d7c436a753d627a6e3c-->
?
**Non.** Une image [[01-oci|OCI]] est un **empilement de couches** décrit par un manifest ; un SIF est un **fichier unique** contenant un système de fichiers en lecture seule. La conversion se fait à la récupération (`docker://`), et elle est **à sens unique** en pratique : on ne repart pas d'un SIF pour alimenter un registry de conteneurs.

---

À ne pas confondre : Apptainer et Docker sur le plan de la sécurité ? <!--anki:6e52296f4e61242e4541-->
?
- **Docker** : un **démon qui tourne en root**. Appartenir au groupe `docker` équivaut, de fait, à un accès root sur la machine
- **Apptainer** : **pas de démon**, le conteneur s'exécute **avec votre identité** et vos droits. C'est précisément pourquoi les clusters partagés l'autorisent ([[13-apptainer-inference-hpc|HPC]])

---

Comment exécuter une commande dans une image Apptainer ? <!--anki:785338455e3a71633e63-->
?
```bash
apptainer exec image.sif python train.py     # une commande
apptainer shell image.sif                    # un shell interactif
apptainer run image.sif                      # le runscript de l'image
```
Par défaut, le **répertoire courant et le dossier personnel sont montés** et les variables d'environnement sont héritées : un script peut donc marcher chez vous et échouer ailleurs. Pour isoler, on utilise `--cleanenv` et `--no-home`.

---

À quoi sert `--nv` avec Apptainer ? <!--anki:78416b386d2b283c4c2f-->
?
À fournir au conteneur l'accès nécessaire à l'environnement **[[09-gpu-conteneurs|NVIDIA/GPU]]** de la machine hôte.

```bash
apptainer exec --nv model.sif python inference.py
```

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

## Connexions
- [[13-apptainer-inference-hpc|Apptainer & inférence HPC]] — usage avancé pour le serving LLM
- [[09-gpu-conteneurs|GPU en conteneur]] — équivalent `--gpus` / `--nv`
- [[02-docker-images-registries|Docker & images]] — interopérabilité `docker://`
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
