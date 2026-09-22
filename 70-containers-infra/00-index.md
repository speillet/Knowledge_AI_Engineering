# Conteneurs & infra — Index — Flashcards
Tags: #flashcards #moc #conteneurs #docker #kubernetes #gpu

Sous-carte de la section **70 — Conteneurs & Infra** : du conteneur au GPU, pour déployer des modèles.

## Fiches de la série

### Fondamentaux
- [[01-oci|01 — OCI]] — le standard des images et des runtimes
- [[02-docker-images-registries|02 — Docker, images & registries]] — construire et distribuer
- [[08-linux-primitives-docker-fondamentaux|08 — Primitives Linux & fondamentaux Docker]] — namespaces, cgroups, volumes

### Runtimes & orchestration
- [[03-containerd-runc|03 — containerd & runc]] — la chaîne d'exécution
- [[04-kubernetes-kubelet-cri|04 — Kubernetes, kubelet & CRI]] — l'orchestration
- [[05-docker-kubernetes|05 — Docker & Kubernetes]] — l'histoire de dockershim

### Inférence LLM
- [[09-gpu-conteneurs|09 — GPU en conteneur]] — donner accès au GPU
- [[10-images-modeles-poids|10 — Images & poids de modèles]] — packager des modèles de plusieurs Go
- [[11-serveurs-inference-llm|11 — Serveurs d'inférence LLM]] — ce qu'on fait tourner (vLLM, TGI…)
- [[12-kubernetes-gpu-inference|12 — Kubernetes GPU & inférence]] — allouer et partager les GPU

### HPC
- [[06-apptainer-singularity|06 — Apptainer & Singularity]] — les conteneurs du HPC
- [[13-apptainer-inference-hpc|13 — Apptainer & inférence HPC]] — servir des modèles sur cluster

### Révision
- [[07-synthese-containers|07 — Synthèse]]

## Chaînes à retenir
```text
Kubernetes → kubelet → CRI → containerd → runc → Linux kernel
Dockerfile → build → image OCI → registry → pull → runtime → conteneur
```

Accès GPU : Docker `--gpus` · Apptainer `--nv` · Kubernetes `nvidia.com/gpu`

## Pourquoi des conteneurs

Pourquoi les conteneurs sont-ils devenus le standard pour servir des modèles ?
?
Ils figent **l'environnement complet** (CUDA, bibliothèques, serveur d'inférence) : le même artefact tourne en dev, en CI et en production, et s'orchestre sur Kubernetes.

---

## Connexions
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — la fiche d'application
- [[83-gateway-ingress|Ingress & API gateway]] — l'entrée réseau du cluster
- [[00-moc-ai-engineering|MOC AI Engineering]]
