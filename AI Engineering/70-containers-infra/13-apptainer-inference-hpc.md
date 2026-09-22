# Apptainer & inférence HPC — Flashcards
Tags: #flashcards #conteneurs #apptainer #hpc #llm #inference

Pourquoi préfère-t-on Apptainer à Docker en environnement HPC ?
?
Parce qu'il est **rootless**, **sans daemon** et adapté à la **sécurité des clusters multi-utilisateurs**.

---

Quel est le modèle de sécurité d'Apptainer ?
?
Le conteneur s'exécute **avec les droits de l'utilisateur** qui le lance, sans démon privilégié en arrière-plan.

---

Comment Apptainer s'intègre-t-il avec Slurm ?
?
La commande Apptainer est **lancée à l'intérieur d'un job Slurm**, en héritant des ressources allouées (GPU, CPU, mémoire).

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

## Connexions
- [[06-apptainer-singularity|Apptainer & Singularity]] — bases & format SIF
- [[09-gpu-conteneurs|GPU en conteneur]] — `--nv` vs `--gpus`
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — ce qu'on exécute
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — alternative cloud/cluster
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
