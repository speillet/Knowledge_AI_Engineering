# GPU en conteneur — Flashcards
Tags: #flashcards #conteneurs #gpu #cuda #infra
<!-- summary: NVIDIA Container Toolkit, driver et CUDA, images CUDA, GPU Operator, Apptainer `--nv`, ROCm. -->


Un conteneur voit-il le GPU de l'hôte par défaut ? <!--anki:7278436c2c57552b3c74-->
?
**Non.** Il faut exposer explicitement les **périphériques GPU** (`/dev/nvidia*`) et les **bibliothèques du driver** dans le conteneur.

Le moteur doit être configuré pour transmettre cet accès, par exemple via le NVIDIA Container Toolkit. Le driver noyau fonctionne sur l'hôte ; l'image fournit l'environnement applicatif compatible. Vérifier d'abord le GPU côté hôte, puis dans le conteneur, afin de distinguer un problème de driver d'un problème d'exposition.

---

Qu'est-ce que le NVIDIA Container Toolkit ? <!--anki:464b64547e593d74596f-->
?
Le composant qui **injecte le GPU dans les conteneurs** au démarrage : il monte les devices `/dev/nvidia*` et les **bibliothèques du driver de l'hôte** (dont `libcuda.so`), pour Docker, containerd, CRI-O ou Podman. Il s'insère comme un **hook du runtime** OCI, ou déclare le matériel via **CDI** (Container Device Interface), la voie standardisée qui fonctionne aussi en rootless.

Sans lui, l'image a bien CUDA mais le conteneur ne voit **aucun GPU**.

---

Comment lancer un conteneur avec GPU sous Docker ? <!--anki:6826774e63433865767d-->
?
```bash
docker run --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```
`--gpus all` (ou `--gpus '"device=0,1"'`) ; `nvidia-smi` dans le conteneur vérifie l'accès.

Cette commande suppose un driver hôte compatible et le NVIDIA Container Toolkit configuré pour Docker. Le tag CUDA est un exemple versionné. `nvidia-smi` valide la visibilité et l'accès au driver, mais pas toute la pile de calcul ; lancer ensuite un petit calcul avec le framework utilisé pour vérifier CUDA et les kernels nécessaires.

---

Où se trouvent le driver et CUDA ? <!--anki:5136266a643a60475856-->
?
- **Driver NVIDIA** (module noyau) : **sur l'hôte**, jamais dans l'image
- **CUDA toolkit / runtime** et bibliothèques (cuDNN, NCCL) : **dans l'image**

Le conteneur utilise le noyau et le module NVIDIA de l'hôte ; des bibliothèques utilisateur du driver lui sont rendues accessibles. L'image applicative apporte les bibliothèques dont elle a besoin, pas nécessairement le toolkit complet. Choisir des versions compatibles : installer CUDA dans l'image ne peut pas réparer un driver hôte absent.

---

Quelle contrainte de compatibilité entre driver et CUDA ? <!--anki:6f476a253b514c4a3043-->
?
Le **driver de l'hôte doit être assez récent** pour la version de CUDA de l'image. Une image CUDA 12.x sur un hôte au driver trop ancien échoue au démarrage : on aligne les versions de CUDA des images sur le parc de drivers.

---

Quelles images de base NVIDIA existent ? <!--anki:4c6f73773453635d4e79-->
?
- **base** : le minimum CUDA
- **runtime** : + bibliothèques CUDA pour exécuter
- **devel** : + compilateurs et en-têtes pour **compiler**
Bon réflexe : compiler dans `devel`, livrer sur `runtime` (**multi-stage build**).

Une image `devel` aide à construire une extension CUDA, mais embarquer compilateurs et en-têtes augmente taille et surface de maintenance. Copier seulement les artefacts nécessaires dans l'étape finale et vérifier les bibliothèques dynamiques requises. Certaines applications compilent au démarrage : tester ce comportement avant de retirer les outils de compilation.

---

Peut-on limiter la VRAM d'un conteneur comme la RAM ? <!--anki:4743213f66743c323749-->
?
**Non**, les cgroups ne gèrent pas la VRAM : un conteneur qui a accès au GPU peut en utiliser toute la mémoire. Le partage propre passe par **MIG** ou le time-slicing ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

Seul garde-fou applicatif : les serveurs d'inférence **préallouent** une fraction de la VRAM (`--gpu-memory-utilization` de vLLM, 0,9 par défaut), ce qui plafonne leur propre usage mais ne protège de rien d'autre.

---

Quels repères de VRAM pour les GPU courants ? <!--anki:6c37477e77387b442667-->
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
Ces capacités sont des repères de variantes matérielles ; vérifier la fiche exacte du GPU. Comparer **poids + KV cache + allocations du moteur** à la mémoire réellement utilisable, avec des unités cohérentes. Les seuls poids d'un 70B en BF16 représentent environ 140 Go : cela ne garantit pas un serving exploitable sur un H200 de 141 Go, faute de marge suffisante selon la configuration.

---

Qu'est-ce que le NVIDIA GPU Operator ? <!--anki:6a3f28646d4a55596924-->
?
Un opérateur Kubernetes qui **installe et gère toute la pile GPU** sur les nodes : driver, Container Toolkit, **device plugin**, exporter de métriques **DCGM**, configuration MIG.

Il automatise le déploiement et la maintenance de composants compatibles, dont certains peuvent être déjà fournis par l'administrateur. Son installation ne suffit pas à fixer une politique de partage, de quota ou de placement. Vérifier la santé des composants, les ressources annoncées et la stratégie choisie pour les différents types de nœuds.

---

Comment utilise-t-on le GPU avec Apptainer ? <!--anki:77556b3d6648472f756b-->
?
L'option **`--nv`** expose les périphériques NVIDIA et les bibliothèques utilisateur nécessaires dans le conteneur :
```bash
apptainer exec --nv image.sif python train.py
```
Le module noyau du driver reste chargé sur l'hôte. Cette option ne réserve pas de GPU auprès de Slurm et n'assure pas toute compatibilité CUDA. Utiliser les GPU alloués par le cluster, puis vérifier leur visibilité et un calcul réel avec le framework de l'image.

---

Comment donner accès à un GPU AMD à un conteneur ? <!--anki:507e28233f496e5a7523-->
?
Avec **ROCm** : on expose les devices `/dev/kfd` et `/dev/dri` au conteneur et on utilise des images ROCm. vLLM et PyTorch supportent ROCm.

Vérifier la matrice de support du GPU, du système et de la version ROCm, ainsi que les permissions sur les devices. Le support d'un framework ne signifie pas que toutes les architectures de modèles ou optimisations CUDA soient disponibles. Tester un calcul élémentaire puis le modèle cible avant de comparer les performances.

---

Calcul : estimer la VRAM pour un 8B avec 30 séquences actives de 4 000 tokens chacune, 16 Go de poids BF16, 128 Kio de KV/token et 3 Go d’autres allocations, avant marge ? <!--anki:6131653231643037393661613436643938623330323430663339666230626637-->
?
```text
poids 8B en BF16                 ≈ 16 Go
KV : 30 × 4 000 tokens × 128 Ko  ≈ 15,7 Go
activations, graphes CUDA        ≈  3 Go
total                            ≈ 35 Go → 48 Go (L40S) ou 80 Go ; 24 Go ne suffit pas
en FP8 (poids et KV cache)       ≈ 19 Go → budget nominal compatible avec 24 Go, à vérifier
```
On dimensionne sur la **concurrence** et la **longueur de contexte**, pas seulement sur la taille du modèle ([[61-kv-cache-attention|KV cache]]).

Les 128 Ko sont ici environ **128 Kio**, pour une architecture précise et un cache BF16 ; tous les 8B n'ont pas cette taille de cache. Ajouter les tokens de sortie et les marges. Le total FP8 de 19 Go suggère une faisabilité mémoire, mais ne garantit ni le pic de chargement ni le respect de la latence cible.

---

## Mises en situation

Mise en situation : ton conteneur d'inférence démarre mais `nvidia-smi` n'y répond pas, alors que le GPU est bien visible sur l'hôte. Comment procèdes-tu ? <!--anki:4f613c7a75292524322a-->
?
1. **Vérifier l'exposition** : le conteneur a-t-il été lancé avec `--gpus` (ou la ressource GPU sous Kubernetes) ?
2. **Vérifier le toolkit** : sans NVIDIA Container Toolkit, ni les devices ni les bibliothèques du driver ne sont injectés
3. **Vérifier les versions** : une image CUDA plus récente que le driver de l'hôte échoue. Le driver reste **sur l'hôte**, CUDA **dans l'image**
4. **Sur Kubernetes** : device plugin présent, node correctement étiqueté, ressource GPU demandée ([[12-kubernetes-gpu-inference|K8s GPU]])
5. **Simplifier le test** : lancer une image CUDA de base avec `nvidia-smi`, avant de déboguer l'application

**Piège** : installer le driver NVIDIA dans l'image, ce qui entre en conflit avec celui de l'hôte.

---

Mise en situation : deux équipes se partagent un GPU pour leurs services d'inférence, et l'une sature régulièrement la VRAM, faisant tomber l'autre. Que proposes-tu ? <!--anki:6c7a70385b75254f5d2d-->
?
1. **Expliquer la limite** : les cgroups ne limitent pas la VRAM. Un conteneur avec accès au GPU peut la consommer entièrement
2. **MIG** : partitionner le GPU en instances **isolées**, avec mémoire dédiée, sur les GPU qui le supportent
3. **Time-slicing** : partage possible, mais sans isolation mémoire, donc le problème resterait
4. **Ou dédier** : un GPU par service, si la charge le justifie
5. **Surveiller** : VRAM et erreurs par GPU, avec l'exporter DCGM ([[93-monitoring-inference|monitoring]])

**Piège** : croire qu'une limite mémoire de conteneur protège la mémoire du GPU.

---

## Sources

- [NVIDIA — capacités mémoire des systèmes HGX H100, H200 et B200](https://docs.nvidia.com/enterprise-reference-architectures/hgx-ai-factory-h100-h200-b200/latest/components.html)

- [Apptainer — accès aux périphériques et bibliothèques GPU](https://apptainer.org/docs/user/main/gpu.html)

## Connexions
- [[00-index|Index Conteneurs]] — les bases des conteneurs
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — allouer et partager les GPU
- [[61-kv-cache-attention|KV cache]] — ce qui consomme la VRAM
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — ce qui tourne sur le GPU
- [[08-linux-primitives-docker-fondamentaux|Primitives Linux]] — cgroup devices
- [[10-images-modeles-poids|Images & poids]] — images CUDA volumineuses
- [[13-apptainer-inference-hpc|Apptainer & HPC]] — `--nv` en HPC
- [[03-containerd-runc|containerd & runc]] — où le toolkit s'insère dans la chaîne
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — l'orchestration et son interface avec le runtime
- [[06-apptainer-singularity|Apptainer & Singularity]] — les conteneurs du monde HPC
- [[54-entrainement-distribue|Entraînement distribué]] — mémoire et parallélismes d'entraînement
- [[00-moc-ai-engineering|MOC AI Engineering]]
