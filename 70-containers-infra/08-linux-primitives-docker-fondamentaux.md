# Primitives Linux & fondamentaux Docker — Flashcards
Tags: #flashcards #conteneurs #linux #docker
<!-- summary: namespaces et cgroups, conteneur ou VM, layers, ordre du Dockerfile et cache, volumes et bind mounts, port mapping. -->

Sur quelles primitives du kernel Linux reposent les conteneurs ?
?
<!--anki:6c342463685269653428-->
Les **namespaces** et les **cgroups**, complétés par des mécanismes de sécurité : **capabilities**, **seccomp** (filtrage des appels système), **AppArmor ou SELinux**, et un système de fichiers **overlay** pour les couches.

Un conteneur n'est donc **pas un objet du noyau** : c'est un **processus ordinaire** assemblé à partir de ces briques par un runtime comme [[03-containerd-runc|runc]].

---

À quoi servent les namespaces ?
?
<!--anki:6a65563352482663542e-->
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

---

À quoi servent les cgroups ?
?
<!--anki:4a2c613b3d4068604965-->
À **limiter et allouer les ressources** qu'un processus consomme (CPU, mémoire, I/O, accès aux devices comme le [[09-gpu-conteneurs|GPU]]).

---

Quelle phrase permet de retenir la différence namespaces / cgroups ?
?
<!--anki:4351766a67394b416049-->
**Les namespaces isolent (ce qu'on voit) ; les cgroups limitent (ce qu'on consomme).**

---

Un conteneur est-il une machine virtuelle ?
?
<!--anki:46582f686d7b712e5b5b-->
**Non.** Un conteneur **partage le kernel de l'hôte** et n'isole que des processus ; il n'émule pas de matériel ni de système d'exploitation complet, et démarre en secondes. Une **VM** embarque **son propre noyau** sur un hyperviseur : isolation plus forte, mais plus lourde.

---

Qu'est-ce qu'un layer d'image ?
?
<!--anki:735f7a393c5b29347d70-->
Une **couche en lecture seule** ; les layers sont empilés via un **union/overlay filesystem** pour former l'image finale. L'image est décrite par un **manifest** et identifiée par un **digest** (hash) ; les couches communes à plusieurs images sont **partagées et mises en cache**.

---

Pourquoi l'ordre des instructions d'un Dockerfile influence-t-il le build ?
?
<!--anki:48487e3d602d24354b28-->
Parce que chaque instruction crée un **layer mis en cache** : placer ce qui change rarement en premier maximise la réutilisation du cache et accélère les rebuilds.

---

À ne pas confondre : volume et bind mount ?
?
<!--anki:794d3870536e79555836-->
Les deux **persistent des données hors du cycle de vie du conteneur** ; un **volume** est géré par le runtime (emplacement, sauvegarde, pilotes), un **bind mount** monte un chemin précis de l'hôte.

---

À ne pas confondre : couche inscriptible et volume ?
?
<!--anki:4c2e7958784f645d4a5a-->
- **Couche inscriptible** du conteneur : tout ce qu'on y écrit **disparaît** à sa suppression, et les écritures passent par l'overlay, donc sont **plus lentes**
- **Volume ou bind mount** : les données **survivent** au conteneur et les écritures vont directement sur le système de fichiers

Pour un serveur d'inférence, les **poids et les caches** vont dans un volume : jamais dans la couche inscriptible, jamais dans l'image ([[10-images-modeles-poids|poids de modèles]]).

---

Qu'est-ce qu'un Dockerfile ?
?
<!--anki:6641264b537b71293034-->
Une **recette déclarative** décrivant comment construire une image (base, dépendances, code, commande de démarrage).

---

À quoi sert le port mapping (`-p`) ?
?
<!--anki:7366346b4c3365405e54-->
À **exposer un port du conteneur sur l'hôte**, par exemple pour rendre accessible un [[11-serveurs-inference-llm|endpoint d'inférence]].

```bash
docker run -p 8000:8000 my-inference-server
```

---

## Mises en situation

Mise en situation : chaque `docker build` de ton image d'inférence prend 12 minutes, même quand tu ne changes qu'une ligne de code Python. Que corriges-tu ?
?
<!--anki:4a296074577b5d2d6763-->
1. **Comprendre le cache** : chaque instruction crée un **layer**, et tout ce qui suit une instruction modifiée est reconstruit
2. **Réordonner** : installation des dépendances (rarement modifiée) **avant** la copie du code
3. **Copier finement** : d'abord le fichier de dépendances, puis le reste du code
4. **Multi-stage** : compiler dans une image lourde, livrer sur une image d'exécution légère
5. **Vérifier** ce qui entre dans le contexte de build (fichier d'exclusion), souvent la vraie cause des lenteurs

**Piège** : une instruction de copie du répertoire complet placée en tête, qui invalide tout le cache à chaque modification.

---

Mise en situation : un responsable sécurité demande d'exécuter le code généré par un agent « dans un conteneur, donc isolé ». Que précises-tu ?
?
<!--anki:513a6d74406e3c434175-->
1. **Rappeler la réalité** : un conteneur **partage le noyau** de l'hôte. Les namespaces isolent la vue, les cgroups limitent la consommation
2. **Ce qui manque** : une faille du noyau permet l'évasion, alors qu'une VM embarque son propre noyau
3. **Renforcer** : gVisor ou Kata pour du code non fiable, avec un noyau isolé ([[103-defenses-agents|défenses]])
4. **Compléter** : pas de secrets dans l'environnement, réseau sortant filtré, système de fichiers éphémère
5. **Limiter la consommation** : cgroups sur CPU, mémoire et accès aux devices

**Piège** : traiter « conteneurisé » comme synonyme de « sûr pour exécuter n'importe quel code ».

---

## Connexions
- [[03-containerd-runc|runc]] — configure namespaces & cgroups
- [[09-gpu-conteneurs|GPU en conteneur]] — cgroup devices pour le GPU
- [[10-images-modeles-poids|Images & poids]] — volumes pour monter les poids
- [[02-docker-images-registries|Docker & images]] — layers & Dockerfile
- [[07-synthese-containers|Synthèse conteneurs]] — les définitions en une phrase
- [[01-oci|OCI]] — les standards d'image, de runtime et de distribution
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
