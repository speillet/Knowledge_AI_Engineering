# GPU en conteneur — Flashcards
Tags: #flashcards #conteneurs #gpu #cuda #infra

Un conteneur voit-il le GPU de l'hôte par défaut ?
?
**Non.** Il faut exposer explicitement les **périphériques GPU** (`/dev/nvidia*`) et les **bibliothèques du driver** dans le conteneur.

---

Qu'est-ce que le NVIDIA Container Toolkit ?
?
Le composant qui **injecte le GPU dans les conteneurs** au démarrage : il monte les devices et les bibliothèques du driver de l'hôte, pour Docker, containerd, CRI-O ou Podman (y compris via **CDI**, Container Device Interface).

---

Comment lancer un conteneur avec GPU sous Docker ?
?
```bash
docker run --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```
`--gpus all` (ou `--gpus '"device=0,1"'`) ; `nvidia-smi` dans le conteneur vérifie l'accès.

---

Où se trouvent le driver et CUDA ?
?
- **Driver NVIDIA** (module noyau) : **sur l'hôte**, jamais dans l'image
- **CUDA toolkit / runtime** et bibliothèques (cuDNN, NCCL) : **dans l'image**

---

Quelle contrainte de compatibilité entre driver et CUDA ?
?
Le **driver de l'hôte doit être assez récent** pour la version de CUDA de l'image. Une image CUDA 12.x sur un hôte au driver trop ancien échoue au démarrage : on aligne les versions de CUDA des images sur le parc de drivers.

---

Quelles images de base NVIDIA existent ?
?
- **base** : le minimum CUDA
- **runtime** : + bibliothèques CUDA pour exécuter
- **devel** : + compilateurs et en-têtes pour **compiler**
Bon réflexe : compiler dans `devel`, livrer sur `runtime` (**multi-stage build**).

---

Peut-on limiter la VRAM d'un conteneur comme la RAM ?
?
**Non**, les cgroups ne gèrent pas la VRAM : un conteneur qui a accès au GPU peut en utiliser toute la mémoire. Le partage propre passe par **MIG** ou le time-slicing ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

---

Qu'est-ce que le NVIDIA GPU Operator ?
?
Un opérateur Kubernetes qui **installe et gère toute la pile GPU** sur les nodes : driver, Container Toolkit, **device plugin**, exporter de métriques **DCGM**, configuration MIG.

---

Comment utilise-t-on le GPU avec Apptainer ?
?
Avec l'option **`--nv`** (ex. `apptainer exec --nv image.sif python train.py`), qui monte le driver NVIDIA de l'hôte dans le conteneur.

---

Et pour les GPU AMD ?
?
Avec **ROCm** : on expose les devices `/dev/kfd` et `/dev/dri` au conteneur et on utilise des images ROCm. vLLM et PyTorch supportent ROCm.

---

## Connexions
- [[00-index|Index Conteneurs]] — les bases des conteneurs
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — allouer et partager les GPU
- [[61-kv-cache-attention|KV cache]] — ce qui consomme la VRAM
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — ce qui tourne sur le GPU
- [[08-linux-primitives-docker-fondamentaux|Primitives Linux]] — cgroup devices
- [[10-images-modeles-poids|Images & poids]] — images CUDA volumineuses
- [[13-apptainer-inference-hpc|Apptainer & HPC]] — `--nv` en HPC
- [[00-moc-ai-engineering|MOC AI Engineering]]
