# Apptainer & inférence HPC — Flashcards
Tags: #flashcards #conteneurs #apptainer #hpc #llm #inference
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Pourquoi préfère-t-on Apptainer à Docker en environnement HPC ?
?
Parce qu'il est **rootless** et **sans démon** : aucun service privilégié à faire tourner sur des nœuds partagés entre des centaines d'utilisateurs. À cela s'ajoute l'intégration naturelle avec l'existant : **images sur le système de fichiers partagé**, lancement dans un job **Slurm**, accès direct aux **GPU** et aux interconnexions (MPI, InfiniBand).

Donner l'accès à Docker sur un cluster partagé équivaudrait à donner **root** à tout le monde.

---

Quel est le modèle de sécurité d'Apptainer ?
?
Le conteneur s'exécute **avec les droits de l'utilisateur** qui le lance, sans démon privilégié en arrière-plan.

---

Comment Apptainer s'intègre-t-il avec Slurm ?
?
La commande Apptainer est **lancée à l'intérieur d'un job Slurm**, en héritant des ressources allouées (GPU, CPU, mémoire) : il n'y a **rien à installer côté ordonnanceur**, puisqu'il n'existe pas de démon.
```bash
#!/bin/bash
#SBATCH --gres=gpu:1 --cpus-per-task=8 --mem=64G --time=02:00:00
apptainer exec --nv \
  --bind /scratch/models:/models \
  vllm.sif python -m vllm.entrypoints.openai.api_server --model /models/llama-8b
```
Les variables `SLURM_*` et `CUDA_VISIBLE_DEVICES` sont **héritées** par le conteneur.

---

Que fait précisément l'option `--nv` d'Apptainer ?
?
Elle **monte les bibliothèques et le driver NVIDIA de l'hôte** dans le conteneur pour permettre l'[[09-gpu-conteneurs|accès GPU]].

```bash
apptainer exec --nv model.sif python inference.py
```

---

Comment fournir les poids d'un modèle à un conteneur Apptainer ?
?
En **montant le système de fichiers partagé** avec `--bind`.

```bash
apptainer exec --nv --bind /data/models:/models model.sif python serve.py
```

---

Pourquoi le format SIF (fichier unique) est-il pratique en HPC ?
?
Parce que l'image est **un seul fichier**, facile à stocker, copier et partager sur un **système de fichiers partagé**.

---

Comment récupérer une image Docker au format Apptainer ?
?
Avec `apptainer pull` et le préfixe `docker://` (voir [[06-apptainer-singularity|Apptainer & Singularity]]).

```bash
apptainer pull vllm.sif docker://vllm/vllm-openai:latest
```

---

Comment construire une image Apptainer à partir d'un fichier de définition ?
?
Un fichier `.def` part d'une image existante et la complète :
```text
Bootstrap: docker
From: vllm/vllm-openai:v0.10.1

%environment
    export HF_HUB_OFFLINE=1

%runscript
    exec vllm serve "$@"
```
```bash
apptainer build vllm.sif vllm.def      # souvent possible sans root (--fakeroot)
apptainer run --nv --bind /data/models:/models vllm.sif /models/llama-70b
```
Le fichier `.def` se **versionne** dans Git, et le SIF produit est un artefact immuable.

---

Comment servir un modèle sur plusieurs nœuds avec Slurm et Apptainer ?
?
- **Tensor parallelism dans le nœud** (NVLink), **pipeline parallelism entre nœuds**, car le réseau inter-nœuds est plus lent ([[54-entrainement-distribue|parallélismes]])
- Une allocation Slurm de N nœuds, où `srun` démarre un conteneur par nœud et un **cluster Ray** qui relie les workers de vLLM
- Le conteneur doit voir le réseau rapide : **InfiniBand** et bibliothèques associées, que `--nv` ne fournit pas, pour que **NCCL** ne retombe pas sur Ethernet

Vérifier le débit NCCL avant d'accuser le modèle d'être lent.

---

Comment exposer un serveur d'inférence lancé dans un job Slurm ?
?
Le serveur écoute sur un **nœud de calcul** dont le nom change à chaque job :
- Le job **publie son adresse** (fichier partagé, service de découverte) ou un **reverse proxy** sur un nœud d'accès route vers lui
- Pour un usage personnel : **tunnel SSH** via le nœud de login
- Le **walltime** limite la durée : prévoir une resoumission automatique et un **health check** côté client

Ces contournements montrent la limite du HPC pour un service permanent ([[12-kubernetes-gpu-inference|Kubernetes GPU]]).

---

## Mises en situation

Mise en situation : tu dois servir un modèle 70B sur un cluster HPC en Slurm, sans droits root et sans accès Internet depuis les nœuds de calcul. Comment t'organises-tu ?
?
1. **Préparer l'image ailleurs** : `apptainer pull` depuis un nœud qui a le réseau, puis copier le SIF sur le système de fichiers partagé
2. **Poids à part** : téléchargés une fois et montés par `--bind`, jamais embarqués dans l'image
3. **Job Slurm** : réserver GPU, CPU et mémoire, puis lancer `apptainer exec --nv` dans le job
4. **Vérifier CUDA et driver** : l'image doit être compatible avec le driver des nœuds ([[09-gpu-conteneurs|GPU en conteneur]])
5. **Exposer le service** : port accessible depuis le nœud de connexion, ou traitement en batch plutôt qu'en service permanent

**Piège** : lancer un serveur d'inférence permanent sur un cluster dont les jobs ont une durée maximale.

---

Mise en situation : ton laboratoire hésite entre un cluster HPC en Slurm et un cluster Kubernetes pour servir des modèles. Quels critères proposes-tu ?
?
1. **Nature de la charge** : batch et calcul planifié pour le HPC, service permanent et trafic continu pour Kubernetes
2. **Modèle de sécurité** : Apptainer est rootless et sans démon, pensé pour des clusters multi-utilisateurs
3. **Ce qui manque en HPC** : autoscaling, ingress, redémarrage automatique, déploiements progressifs ([[12-kubernetes-gpu-inference|K8s GPU]])
4. **Ce qui existe déjà** : matériel, équipe, ordonnanceur et compétences en place pèsent souvent plus que la technique
5. **Solution mixte fréquente** : entraînement et batch en HPC, service en ligne sur Kubernetes

**Piège** : transformer un cluster HPC en plateforme de service en ligne, avec des jobs relancés en boucle.

---

## Connexions
- [[06-apptainer-singularity|Apptainer & Singularity]] — bases & format SIF
- [[09-gpu-conteneurs|GPU en conteneur]] — `--nv` vs `--gpus`
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — ce qu'on exécute
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — alternative cloud/cluster
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
