# Apptainer & Singularity — Flashcards
Tags: #flashcards #conteneurs #apptainer #singularity #hpc

Dans quel environnement Apptainer est-il particulièrement utilisé ?
?
Dans les environnements **HPC**, calcul scientifique, clusters partagés (Slurm, MPI) et workloads GPU : pas de démon root, le conteneur s'exécute **avec l'identité de l'utilisateur** (détails dans [[13-apptainer-inference-hpc|Apptainer & inférence HPC]]).

---

Quelle relation existe entre Singularity et Apptainer ?
?
**Apptainer est issu du projet Singularity.**

---

Quel est le format d'image historiquement natif d'Apptainer/Singularity ?
?
**SIF — Singularity Image Format.**

---

Une image SIF est-elle simplement une image OCI ?
?
**Non.** SIF est un format différent, même si Apptainer interopère avec l'écosystème OCI/Docker.

---

Apptainer peut-il récupérer une image Docker ?
?
**Oui.**

Exemple :

```bash
apptainer pull pytorch.sif docker://pytorch/pytorch:latest
```

---

Comment exécuter une commande dans une image Apptainer ?
?
```bash
apptainer exec image.sif command
```

---

À quoi sert `--nv` avec Apptainer ?
?
À fournir au conteneur l'accès nécessaire à l'environnement **[[09-gpu-conteneurs|NVIDIA/GPU]]** de la machine hôte.

```bash
apptainer exec --nv model.sif python inference.py
```

---

## Connexions
- [[13-apptainer-inference-hpc|Apptainer & inférence HPC]] — usage avancé pour le serving LLM
- [[09-gpu-conteneurs|GPU en conteneur]] — équivalent `--gpus` / `--nv`
- [[02-docker-images-registries|Docker & images]] — interopérabilité `docker://`
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
