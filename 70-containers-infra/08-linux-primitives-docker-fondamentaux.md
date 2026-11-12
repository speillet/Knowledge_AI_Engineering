# Primitives Linux & fondamentaux Docker — Flashcards
Tags: #flashcards #conteneurs #linux #docker
<!-- summary: namespaces et cgroups, conteneur ou VM, layers, ordre du Dockerfile et cache, volumes et bind mounts, port mapping, distinction entre RAM et VRAM. -->


Sur quelles primitives du kernel Linux reposent les conteneurs ? <!--anki:6c342463685269653428-->
?
Les **namespaces** et les **cgroups**, complétés par des mécanismes de sécurité : **capabilities**, **seccomp** (filtrage des appels système), **AppArmor ou SELinux**, et un système de fichiers **overlay** pour les couches.

Un conteneur n'est donc **pas un objet du noyau** : c'est un **processus ordinaire** assemblé à partir de ces briques par un runtime comme [[03-containerd-runc|runc]].

Il partage le noyau de l'hôte : empaqueter un espace utilisateur Ubuntu ne fournit pas un noyau Ubuntu distinct. Une fonctionnalité ou faille du noyau reste donc un sujet d'hôte, contrairement à une dépendance Python contenue dans l'image.

---

À quoi servent les namespaces ? <!--anki:6a65563352482663542e-->
?
À **isoler ce qu'un processus voit**, chaque type couvrant une ressource :
```text
pid     → l'arbre des processus (le conteneur voit son propre PID 1)
net     → interfaces, ports, table de routage
mnt     → les points de montage, donc l'arborescence de fichiers
uts     → le hostname
ipc     → mémoire partagée, files de messages
user    → la correspondance des UID (base du mode rootless)
cgroup  → la vue des cgroups
```
C'est pour cela que deux conteneurs peuvent écouter le **port 8000** sans conflit.

L'absence de conflit suppose des **namespaces réseau distincts**. Avec un réseau partagé, notamment entre conteneurs d'un même Pod, les ports peuvent entrer en conflit. Les namespaces ne constituent pas une virtualisation complète : les processus partagent le noyau de l'hôte et l'isolation dépend des espaces effectivement configurés.

---

À quoi servent les cgroups ? <!--anki:4a2c613b3d4068604965-->
?
À **limiter et allouer les ressources** qu'un processus consomme (CPU, mémoire, I/O, accès aux devices comme le [[09-gpu-conteneurs|GPU]]).

Les cgroups regroupent des processus pour leur appliquer des contrôles et mesurer leur consommation. Une limite CPU peut provoquer du throttling ; une limite mémoire peut conduire à un arrêt pour manque de mémoire. Le contrôle d'accès aux devices ne partitionne pas automatiquement la VRAM ou le calcul GPU : ce partage demande des mécanismes spécifiques.

---

Quelle phrase permet de retenir la différence namespaces / cgroups ? <!--anki:4351766a67394b416049-->
?
**Les namespaces isolent (ce qu'on voit) ; les cgroups limitent (ce qu'on consomme).**

Exemple : un namespace PID masque les processus d'autres groupes, tandis qu'un cgroup mémoire borne la quantité utilisable. Un conteneur peut donc avoir une vue isolée sans limite stricte de mémoire, ou une limite sans réseau isolé. Les deux mécanismes se complètent avec permissions, capabilities et filtrage d'appels système.

Un processus peut voir peu de voisins tout en consommant toute la RAM autorisée. Pour un OOM, examiner la limite du cgroup et son usage, pas seulement la mémoire libre affichée sur l'hôte.

---

Un conteneur est-il une machine virtuelle ? <!--anki:46582f686d7b712e5b5b-->
?
**Non.** Un conteneur **partage le kernel de l'hôte** et n'isole que des processus ; il n'émule pas de matériel ni de système d'exploitation complet, et démarre en secondes. Une **VM** embarque **son propre noyau** sur un hyperviseur : isolation plus forte, mais plus lourde.

Conséquences du noyau partagé : un conteneur Linux ne tourne pas nativement sur Windows ou macOS, où Docker Desktop démarre une VM Linux. Une faille du noyau concerne tous les conteneurs de l'hôte. Et un module noyau, comme le driver GPU, se trouve sur l'hôte : on ne peut pas en embarquer une version différente par conteneur.

---

Qu'est-ce qu'un layer d'image ? <!--anki:735f7a393c5b29347d70-->
?
Une **couche en lecture seule** ; les layers sont empilés via un **union/overlay filesystem** pour former l'image finale. L'image est décrite par un **manifest** et identifiée par un **digest** (hash) ; les couches communes à plusieurs images sont **partagées et mises en cache**.

Chaque instruction `RUN`, `COPY` ou `ADD` crée une couche. Supprimer un fichier dans une couche ultérieure le **masque** sans réduire l'image : un `RUN wget modele.bin` suivi d'un `RUN rm modele.bin` laisse le fichier dans la couche précédente, téléchargé à chaque pull. Nettoyer dans la même instruction `RUN`, ou ne copier que le résultat final.

---

Pourquoi l'ordre des instructions d'un Dockerfile influence-t-il le build ? <!--anki:48487e3d602d24354b28-->
?
Le builder réutilise les résultats d'étapes dont les instructions et dépendances n'ont pas changé. Une modification invalide l'étape concernée et les étapes qui en dépendent. Les instructions **RUN, COPY ou ADD** peuvent modifier le système de fichiers ; toutes les instructions ne créent pas une couche de fichiers.

Copier d'abord le fichier de dépendances, installer, puis copier le code évite de réinstaller à chaque modification applicative. Épingler aussi les versions : un cache efficace n'est pas une garantie de reproductibilité.

---

À ne pas confondre : volume et bind mount ? <!--anki:794d3870536e79555836-->
?
Les deux **persistent des données hors du cycle de vie du conteneur** ; un **volume** est géré par le runtime (emplacement, sauvegarde, pilotes), un **bind mount** monte un chemin précis de l'hôte.

Un volume simplifie la gestion du stockage par le moteur ; un bind mount convient pour un chemin local précis, mais couple le conteneur à l'hôte. Les données ne sont pas sauvegardées automatiquement du seul fait d'être dans un volume. Pour des poids de modèle non modifiables, préférer un montage en lecture seule.

---

À ne pas confondre : couche inscriptible et volume ? <!--anki:4c2e7958784f645d4a5a-->
?
La **couche inscriptible** appartient au cycle de vie du conteneur ; ses données sont perdues à sa suppression. Un **volume ou bind mount** conserve des données hors de cette couche, sous réserve de sa propre politique de suppression.

Les surcoûts dépendent du driver et des accès : le copy-on-write peut pénaliser certaines écritures, tandis qu'un volume réseau peut lui-même être lent. Mesurer le stockage réel. Pour des poids volumineux partagés et des caches persistants, préférer un stockage externe adapté ; embarquer des poids immuables dans l'image reste un choix possible avec des compromis de distribution ([[10-images-modeles-poids|poids de modèles]]).

---

Qu'est-ce qu'un Dockerfile ? <!--anki:6641264b537b71293034-->
?
Une **recette de construction d'image** : `FROM` choisit la base, `COPY` ajoute des fichiers, `RUN` exécute une étape du build, `CMD` fournit une commande par défaut au démarrage.

Exemple : installer les dépendances avec `RUN` les inscrit dans l'image ; lancer le serveur avec `CMD` le démarre lors de la création du conteneur, pas pendant le build. `CMD` peut être remplacé au lancement.

Épingler base et dépendances, et limiter le contexte de build. Copier un secret puis le supprimer dans une couche ultérieure ne l'efface pas de l'historique de l'image ; utiliser les mécanismes de secrets du build plutôt que `COPY`.

---

À quoi sert le port mapping (`-p`) ? <!--anki:7366346b4c3365405e54-->
?
À **exposer un port du conteneur sur l'hôte**, par exemple pour rendre accessible un [[11-serveurs-inference-llm|endpoint d'inférence]].

```bash
docker run -p 8000:8000 my-inference-server
```

Le premier nombre est le port de l'hôte, le second celui du conteneur. L'application doit écouter sur une adresse joignable dans le conteneur. Sans adresse explicite, le port peut être publié sur toutes les interfaces ; pour un usage local, utiliser `-p 127.0.0.1:8000:8000` et garder l'authentification adaptée au service.

---

Pourquoi une limite mémoire de conteneur ne réserve-t-elle pas automatiquement de la mémoire GPU ? <!--anki:3032646263336463396331373433393038333039336564353430376462666535-->
?
Les **limites de mémoire habituelles du conteneur** portent sur la mémoire gérée par le système hôte. La VRAM et son allocation dépendent du GPU, du runtime et des mécanismes de partage retenus.

Un processus peut respecter sa limite RAM tout en échouant en VRAM, ou l'inverse pendant le chargement des poids. Surveiller séparément RAM, mémoire épinglée et VRAM. Définir les limites et l'isolation GPU avec les composants adaptés, puis tester plusieurs workloads concurrents. Le seul champ mémoire du conteneur ne constitue pas un quota de VRAM.

---

## Mises en situation

Mise en situation : chaque `docker build` de ton image d'inférence prend 12 minutes, même quand tu ne changes qu'une ligne de code Python. Que corriges-tu ? <!--anki:4a296074577b5d2d6763-->
?
1. **Comprendre le cache** : chaque instruction crée un **layer**, et tout ce qui suit une instruction modifiée est reconstruit
2. **Réordonner** : installation des dépendances (rarement modifiée) **avant** la copie du code
3. **Copier finement** : d'abord le fichier de dépendances, puis le reste du code
4. **Multi-stage** : compiler dans une image lourde, livrer sur une image d'exécution légère
5. **Vérifier** ce qui entre dans le contexte de build (fichier d'exclusion), souvent la vraie cause des lenteurs

**Piège** : une instruction de copie du répertoire complet placée en tête, qui invalide tout le cache à chaque modification.

---

Mise en situation : un responsable sécurité demande d'exécuter le code généré par un agent « dans un conteneur, donc isolé ». Que précises-tu ? <!--anki:513a6d74406e3c434175-->
?
1. **Rappeler la réalité** : un conteneur **partage le noyau** de l'hôte. Les namespaces isolent la vue, les cgroups limitent la consommation
2. **Ce qui manque** : une faille du noyau permet l'évasion, alors qu'une VM embarque son propre noyau
3. **Renforcer** : gVisor ou Kata pour du code non fiable, avec un noyau isolé ([[103-defenses-agents|défenses]])
4. **Compléter** : pas de secrets dans l'environnement, réseau sortant filtré, système de fichiers éphémère
5. **Limiter la consommation** : cgroups sur CPU, mémoire et accès aux devices

**Piège** : traiter « conteneurisé » comme synonyme de « sûr pour exécuter n'importe quel code ».

---

## Sources

- [Kubernetes — gestion des ressources des conteneurs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) — approfondissement ciblé du 12 novembre 2026 ; les exemples pédagogiques sont construits pour cette revue.

- [Docker — stockage, couches inscriptibles et drivers](https://docs.docker.com/engine/storage/drivers/) — vérification ciblée du 12 novembre 2026, sans renouvellement de la date globale de la fiche.

## Connexions
- [[03-containerd-runc|runc]] — configure namespaces & cgroups
- [[09-gpu-conteneurs|GPU en conteneur]] — cgroup devices pour le GPU
- [[10-images-modeles-poids|Images & poids]] — volumes pour monter les poids
- [[02-docker-images-registries|Docker & images]] — layers & Dockerfile
- [[07-synthese-containers|Synthèse conteneurs]] — les définitions en une phrase
- [[01-oci|OCI]] — les standards d'image, de runtime et de distribution
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
