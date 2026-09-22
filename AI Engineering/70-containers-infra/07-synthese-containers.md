# Conteneurs — Synthèse
Tags: #flashcards #conteneurs #revision

OCI, CRI et SIF désignent-ils le même type de chose ?
?
**Non.**

- OCI → standards ouverts des conteneurs
- CRI → interface Kubernetes ↔ container runtime
- SIF → format d'image Singularity/Apptainer

---

Quelle chaîne Kubernetes faut-il savoir reconstruire ?
?
```text
Kubernetes
    ↓
kubelet
    ↓
CRI
    ↓
containerd
    ↓
runc
    ↓
Linux Kernel
```

---

Quelle chaîne représente un workflow classique d'image ?
?
```text
Dockerfile
    ↓
docker build
    ↓
Image OCI
    ↓
Registry
    ↓
pull
    ↓
Runtime
    ↓
Container
```

---

Comment résumer Docker, Kubernetes, containerd et runc ?
?
**Docker construit/manipule les conteneurs, Kubernetes les orchestre, containerd les gère et runc réalise leur exécution bas niveau.**

---

Comment distinguer namespaces et cgroups ?
?
**Les [[08-linux-primitives-docker-fondamentaux|namespaces]] isolent (ce qu'un processus voit) ; les [[08-linux-primitives-docker-fondamentaux|cgroups]] limitent (ce qu'un processus consomme).**

---

Comment donne-t-on accès au GPU selon l'environnement ?
?
- [[09-gpu-conteneurs|Docker]] → `--gpus`
- [[13-apptainer-inference-hpc|Apptainer]] → `--nv`
- [[12-kubernetes-gpu-inference|Kubernetes]] → ressource `nvidia.com/gpu`

---

Quels serveurs d'inférence LLM conteneurisés faut-il connaître ?
?
**[[11-serveurs-inference-llm|vLLM, NVIDIA Triton, TGI]]** (et TensorRT-LLM, Ollama).

---

Où stocker les poids d'un modèle plutôt que dans l'image ?
?
Dans un **[[08-linux-primitives-docker-fondamentaux|volume / bind mount]]** ou un **stockage externe** ; on évite de « baker » les poids dans l'image. → [[10-images-modeles-poids|Images & poids]]

---

Quelles notions faut-il pouvoir définir instantanément ?
?
- OCI
- image
- conteneur
- registry
- Kubernetes
- kubelet
- CRI
- containerd
- runc
- Apptainer
- SIF
- namespaces
- cgroups
- NVIDIA Container Toolkit
- vLLM
- Triton
- TGI
- MIG
- device plugin
- KV cache
- cold start

---

## Connexions
- [[00-index|Index Conteneurs (MOC)]] — carte complète du sujet
- [[00-moc-ai-engineering|MOC AI Engineering]]
