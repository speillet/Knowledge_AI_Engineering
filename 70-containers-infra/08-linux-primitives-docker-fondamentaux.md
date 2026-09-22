# Primitives Linux & fondamentaux Docker — Flashcards
Tags: #flashcards #conteneurs #linux #docker

Sur quelles primitives du kernel Linux reposent les conteneurs ?
?
Les **namespaces** et les **cgroups**.

---

À quoi servent les namespaces ?
?
À **isoler ce qu'un processus voit** (PID, réseau, montages, hostname, IPC, utilisateurs).

---

À quoi servent les cgroups ?
?
À **limiter et allouer les ressources** qu'un processus consomme (CPU, mémoire, I/O, accès aux devices comme le [[09-gpu-conteneurs|GPU]]).

---

Quelle phrase permet de retenir la différence namespaces / cgroups ?
?
**Les namespaces isolent (ce qu'on voit) ; les cgroups limitent (ce qu'on consomme).**

---

Un conteneur est-il une machine virtuelle ?
?
**Non.** Un conteneur **partage le kernel de l'hôte** et n'isole que des processus ; il n'émule pas de matériel ni de système d'exploitation complet, et démarre en secondes. Une **VM** embarque **son propre noyau** sur un hyperviseur : isolation plus forte, mais plus lourde.

---

Qu'est-ce qu'un layer d'image ?
?
Une **couche en lecture seule** ; les layers sont empilés via un **union/overlay filesystem** pour former l'image finale. L'image est décrite par un **manifest** et identifiée par un **digest** (hash) ; les couches communes à plusieurs images sont **partagées et mises en cache**.

---

Pourquoi l'ordre des instructions d'un Dockerfile influence-t-il le build ?
?
Parce que chaque instruction crée un **layer mis en cache** : placer ce qui change rarement en premier maximise la réutilisation du cache et accélère les rebuilds.

---

Quelle est la différence entre un volume et un bind mount ?
?
Les deux **persistent des données hors du cycle de vie du conteneur** ; un **volume** est géré par le runtime, un **bind mount** monte un chemin précis de l'hôte.

---

Qu'est-ce qu'un Dockerfile ?
?
Une **recette déclarative** décrivant comment construire une image (base, dépendances, code, commande de démarrage).

---

À quoi sert le port mapping (`-p`) ?
?
À **exposer un port du conteneur sur l'hôte**, par exemple pour rendre accessible un [[11-serveurs-inference-llm|endpoint d'inférence]].

```bash
docker run -p 8000:8000 my-inference-server
```

---

## Connexions
- [[03-containerd-runc|runc]] — configure namespaces & cgroups
- [[09-gpu-conteneurs|GPU en conteneur]] — cgroup devices pour le GPU
- [[10-images-modeles-poids|Images & poids]] — volumes pour monter les poids
- [[02-docker-images-registries|Docker & images]] — layers & Dockerfile
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
