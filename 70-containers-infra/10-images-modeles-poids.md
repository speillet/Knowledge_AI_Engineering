# Images & poids de modèles — Flashcards
Tags: #flashcards #conteneurs #modeles #stockage #infra

Combien pèsent les poids d'un LLM ?
?
Environ **nombre de paramètres × octets par paramètre** : un modèle de 8B en BF16 (2 octets) ≈ **16 Go**, un 70B ≈ **140 Go** (≈ 35-40 Go en INT4).

---

Faut-il mettre les poids dans l'image du conteneur ?
?
- **Dans l'image** : artefact **autonome et immuable**, mais image énorme, pull lent et rebuild à chaque version de modèle
- **Séparés** (recommandé pour les gros modèles) : image légère avec le runtime, poids chargés depuis un stockage

---

Où stocker les poids quand ils sont séparés de l'image ?
?
- **Volume partagé** (PVC, NFS) monté dans les Pods
- **Stockage objet** (S3, GCS) téléchargé au démarrage
- **Hugging Face Hub** (ou miroir interne), avec un **cache persistant** (`HF_HOME`)
- **Cache local** sur le disque du node

---

Qu'est-ce que le cold start d'un serveur de modèle ?
?
Le temps avant la première réponse : **pull de l'image + téléchargement des poids + chargement en VRAM** (+ compilation éventuelle). Il peut atteindre **plusieurs minutes**, ce qui pénalise le scale-from-zero.

---

Comment réduire le cold start ?
?
**Pré-puller les images** sur les nodes GPU (DaemonSet), garder les poids en **cache local**, télécharger via un **init container**, streamer les poids directement vers le GPU, garder un minimum de réplicas chauds.

---

Pourquoi préférer le format safetensors ?
?
Parce qu'il ne contient **que des tenseurs** : pas de code exécuté au chargement, contrairement aux fichiers **pickle** PyTorch (`.bin`, `.pt`) qui peuvent **exécuter du code arbitraire**. Il est aussi plus rapide à charger (mmap).

---

Qu'est-ce que le format GGUF ?
?
Le format **fichier unique** de llama.cpp (et Ollama) : poids **quantizés** + métadonnées (tokenizer, architecture). Adapté à l'inférence **locale ou sur CPU**.

---

Comment garder une image de serveur d'inférence raisonnable ?
?
**Multi-stage build** (compiler dans une image `devel`, livrer sur `runtime`), dépendances minimales, couches ordonnées pour **maximiser le cache**, et surtout **pas de poids** dans l'image.

---

Comment garantir la traçabilité des modèles déployés ?
?
En **versionnant les poids** (révision/commit Hugging Face, digest, registre de modèles) et en les **épinglant** dans la configuration de déploiement, comme on épingle le digest d'une image.

---

Quelle tendance pour distribuer les modèles ?
?
Distribuer les poids comme **artefacts OCI** dans un registry, puis les monter comme volumes (volumes d'image Kubernetes, KitOps) : même outillage que les images (versioning, cache, signature).

---

## Connexions
- [[00-index|Index Conteneurs]] — images et couches OCI
- [[09-gpu-conteneurs|GPU en conteneur]] — images CUDA
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — pull time et scaling
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — ce qui charge les poids
- [[02-docker-images-registries|Registries & images]] — stockage & distribution
- [[08-linux-primitives-docker-fondamentaux|Volumes & bind mounts]] — monter les poids
- [[111-mlops-llmops-fondamentaux|MLOps]] — le model registry approfondi
- [[68-quantization|Quantization]] — réduire la taille des poids
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — signature des modèles et AI-BOM
- [[00-moc-ai-engineering|MOC AI Engineering]]
