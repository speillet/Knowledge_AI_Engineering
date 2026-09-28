# GPU en conteneur — Flashcards
Tags: #flashcards #conteneurs #gpu #cuda #infra

Un conteneur voit-il le GPU de l'hôte par défaut ?
?
**Non.** Il faut exposer explicitement les **périphériques GPU** (`/dev/nvidia*`) et les **bibliothèques du driver** dans le conteneur.

---

Qu'est-ce que le NVIDIA Container Toolkit ?
?
Le composant qui **injecte le GPU dans les conteneurs** au démarrage : il monte les devices `/dev/nvidia*` et les **bibliothèques du driver de l'hôte** (dont `libcuda.so`), pour Docker, containerd, CRI-O ou Podman. Il s'insère comme un **hook du runtime** OCI, ou déclare le matériel via **CDI** (Container Device Interface), la voie standardisée qui fonctionne aussi en rootless.

Sans lui, l'image a bien CUDA mais le conteneur ne voit **aucun GPU**.

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

Seul garde-fou applicatif : les serveurs d'inférence **préallouent** une fraction de la VRAM (`--gpu-memory-utilization` de vLLM, 0,9 par défaut), ce qui plafonne leur propre usage mais ne protège de rien d'autre.

---

Quels repères de VRAM pour les GPU courants ?
?
```text
RTX 4090 / 5090   24 à 32 Go   poste de travail
L4                 24 Go       inférence économe
L40S               48 Go       inférence, pas de NVLink
A100               40 ou 80 Go  génération précédente, pas de FP8
H100               80 Go       FP8 natif, NVLink
H200              141 Go       idéal pour les contextes longs
B200              ~180 Go      Blackwell, FP4 natif
```
À croiser avec la règle « paramètres × octets par paramètre », plus le [[61-kv-cache-attention|KV cache]] : un 70B en BF16 (140 Go) ne tient pas sur un H100, mais tient sur un H200.

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

## Mises en situation

Mise en situation : ton conteneur d'inférence démarre mais `nvidia-smi` n'y répond pas, alors que le GPU est bien visible sur l'hôte. Comment procèdes-tu ?
?
1. **Vérifier l'exposition** : le conteneur a-t-il été lancé avec `--gpus` (ou la ressource GPU sous Kubernetes) ?
2. **Vérifier le toolkit** : sans NVIDIA Container Toolkit, ni les devices ni les bibliothèques du driver ne sont injectés
3. **Vérifier les versions** : une image CUDA plus récente que le driver de l'hôte échoue. Le driver reste **sur l'hôte**, CUDA **dans l'image**
4. **Sur Kubernetes** : device plugin présent, node correctement étiqueté, ressource GPU demandée ([[12-kubernetes-gpu-inference|K8s GPU]])
5. **Simplifier le test** : lancer une image CUDA de base avec `nvidia-smi`, avant de déboguer l'application

**Piège** : installer le driver NVIDIA dans l'image, ce qui entre en conflit avec celui de l'hôte.

---

Mise en situation : deux équipes se partagent un GPU pour leurs services d'inférence, et l'une sature régulièrement la VRAM, faisant tomber l'autre. Que proposes-tu ?
?
1. **Expliquer la limite** : les cgroups ne limitent pas la VRAM. Un conteneur avec accès au GPU peut la consommer entièrement
2. **MIG** : partitionner le GPU en instances **isolées**, avec mémoire dédiée, sur les GPU qui le supportent
3. **Time-slicing** : partage possible, mais sans isolation mémoire, donc le problème resterait
4. **Ou dédier** : un GPU par service, si la charge le justifie
5. **Surveiller** : VRAM et erreurs par GPU, avec l'exporter DCGM ([[93-monitoring-inference|monitoring]])

**Piège** : croire qu'une limite mémoire de conteneur protège la mémoire du GPU.

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
