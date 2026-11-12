# Conteneurs & infra — Index — Flashcards
Tags: #flashcards #moc #conteneurs #docker #kubernetes #gpu
<!-- summary: sommaire des 13 fiches de la section, chaînes à retenir, et une carte sur l'intérêt des conteneurs pour servir des modèles, test de démarrage sur la cible réelle. -->


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

---

## Cartes

Pourquoi les conteneurs sont-ils devenus le standard pour servir des modèles ? <!--anki:45514a373c635d6d4a50-->
?
Ils regroupent **serveur et dépendances applicatives** dans un artefact versionné, transportable entre environnements compatibles et orchestrable, notamment sur Kubernetes. Ils **ne figent pas toute la machine** : noyau, driver GPU, matériel et volumes restent externes.

Exemple : remettre l'ancienne image ne restaure pas l'ancien modèle si les poids montés ont changé. Un rollback fiable doit identifier **image par digest, révision des poids, tokenizer et configuration**, puis vérifier leur compatibilité avec l'hôte.

Tester un démarrage et une inférence représentative sur la cible ; un build réussi ne valide ni l'accès au GPU ni la mémoire nécessaire ([[09-gpu-conteneurs|GPU en conteneur]]).

---

Quel test de démarrage distingue une image de conteneur valide d'un service d'inférence utilisable ? <!--anki:6239363366343864343265383437316639613834316334373436653763656665-->
?
Faire un **démarrage sur la cible réelle**, puis une inférence représentative. Vérifier chargement des poids, accès GPU, tokenizer, sortie attendue et marge mémoire ; un processus vivant ne prouve pas que le modèle est prêt.

Mesurer séparément téléchargement, initialisation et première requête, puis tester le redémarrage avec un cache froid. Conserver les versions de l'image, du modèle et du driver. Ce test de bout en bout complète la conformité du conteneur : une image correcte peut rester inutilisable faute de poids, de capacité ou de compatibilité matérielle.

---

## Connexions
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — la fiche d'application
- [[83-gateway-ingress|Ingress & API gateway]] — l'entrée réseau du cluster
- [[00-moc-ai-engineering|MOC AI Engineering]]
