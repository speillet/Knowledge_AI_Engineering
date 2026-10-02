# Images & poids de modèles — Flashcards
Tags: #flashcards #conteneurs #modeles #stockage #infra
<!-- summary: calcul du temps de chargement des poids d'un 70B, poids dans l'image ou séparés, cold start, safetensors ou pickle, safetensors ou GGUF, modèles distribués comme artefacts OCI. -->

Calcul : combien de temps pour charger les poids d'un 70B au démarrage d'un pod ?
?
<!--anki:4e2e2a7a3e49745e523f-->
Les poids pèsent **paramètres × octets par paramètre** : ≈ **140 Go** pour un 70B en BF16 ([[131-transformer-architecture|mémoire des poids]]).
```text
140 Go × 8 = 1 120 Gbit
réseau à  1 Gbit/s  → ≈ 19 min
réseau à 10 Gbit/s  → ≈  2 min
cache local NVMe    → quelques dizaines de secondes
```
D'où les poids **hors de l'image**, sur un volume partagé ou mis en cache sur le nœud, pour éviter un démarrage à froid de plusieurs minutes à chaque mise à l'échelle.

---

Faut-il mettre les poids dans l'image du conteneur ?
?
<!--anki:707d512f4d7270214938-->
- **Dans l'image** : artefact **autonome et immuable**, mais image énorme, pull lent et rebuild à chaque version de modèle
- **Séparés** (recommandé pour les gros modèles) : image légère avec le runtime, poids chargés depuis un stockage

---

Où stocker les poids quand ils sont séparés de l'image ?
?
<!--anki:6d5d53393124313f7072-->
- **Volume partagé** (PVC, NFS) monté dans les Pods
- **Stockage objet** (S3, GCS) téléchargé au démarrage
- **Hugging Face Hub** (ou miroir interne), avec un **cache persistant** (`HF_HOME`)
- **Cache local** sur le disque du node
```yaml
env:
  - { name: HF_HOME, value: /cache/hf }      # cache partagé entre Pods
  - { name: HF_HUB_OFFLINE, value: "1" }     # interdit tout téléchargement surprise
volumeMounts:
  - { name: model-cache, mountPath: /cache/hf }
```
Le **cache local sur le node** est le plus rapide, le **volume partagé** le plus simple à mutualiser.

---

À ne pas confondre : container registry et model registry ?
?
<!--anki:666631384e6473424e60-->
- **Container registry** (Docker Hub, Harbor, ECR) : stocke des **images** OCI, adressées par tag ou digest
- **Model registry** (MLflow, W&B, Hugging Face) : stocke des **versions de modèles** avec leurs **métadonnées** : métriques, lineage, étape (staging, production), auteur

Les deux se complètent : l'image contient le **runtime**, le model registry dit **quels poids** déployer ([[111-mlops-llmops-fondamentaux|MLOps]]). La tendance des artefacts OCI brouille la frontière, mais les métadonnées restent l'apport du model registry.

---

Qu'est-ce que le cold start d'un serveur de modèle ?
?
<!--anki:655d3c2f5b7a6d6e494b-->
Le temps avant la première réponse : **pull de l'image + téléchargement des poids + chargement en VRAM** (+ compilation éventuelle). Il peut atteindre **plusieurs minutes**, ce qui pénalise le scale-from-zero.
```text
pull image (10 Go)        30 s à 3 min selon le réseau et le cache
poids 8B depuis S3        1 à 3 min
poids 8B depuis le node   10 à 30 s
chargement en VRAM        10 s à 1 min
compilation (TensorRT)    plusieurs minutes, à faire une fois
```
Retenir l'ordre de grandeur : **une à cinq minutes**, à comparer aux secondes d'un service web classique. C'est ce qui interdit un autoscaling purement réactif ([[12-kubernetes-gpu-inference|autoscaling GPU]]).

---

Comment réduire le cold start d'un pod d'inférence ?
?
<!--anki:643a67575b6d6a61735d-->
**Pré-puller les images** sur les nodes GPU (DaemonSet), garder les poids en **cache local**, télécharger via un **init container**, streamer les poids directement vers le GPU, garder un minimum de réplicas chauds.

---

Pourquoi préférer le format safetensors ?
?
<!--anki:6a617730764d4a24792f-->
Parce qu'il ne contient **que des tenseurs** : pas de code exécuté au chargement, contrairement aux fichiers **pickle** PyTorch (`.bin`, `.pt`) qui peuvent **exécuter du code arbitraire**. Il est aussi plus rapide à charger (mmap).

---

À ne pas confondre : safetensors et GGUF ?
?
<!--anki:3636316535383632616663663462353961326137313766323332643535323562-->
- **safetensors** : le format standard des checkpoints Hugging Face, en BF16 ou déjà quantizés (FP8, AWQ, GPTQ), que chargent **vLLM, SGLang et Transformers** pour le serving GPU
- **GGUF** : le format **fichier unique** de llama.cpp et Ollama, qui embarque poids **quantizés** (Q4_K_M, Q8_0…), tokenizer et métadonnées, pour l'inférence **locale ou sur CPU**

Un même modèle est souvent publié dans les deux formats ([[164-llm-local-edge|LLM locaux]], [[68-quantization|quantization]]).

---

Comment garder une image de serveur d'inférence raisonnable ?
?
<!--anki:483132742f7d464d5863-->
**Multi-stage build** (compiler dans une image `devel`, livrer sur `runtime`), dépendances minimales, couches ordonnées pour **maximiser le cache**, et surtout **pas de poids** dans l'image.

---

Comment garantir la traçabilité des modèles déployés ?
?
<!--anki:722b4e75573023266877-->
En **versionnant les poids** (révision/commit Hugging Face, digest, registre de modèles) et en les **épinglant** dans la configuration de déploiement, comme on épingle le digest d'une image.

---

Quelle tendance pour distribuer les modèles ?
?
<!--anki:426c59524537246c475d-->
Distribuer les poids comme **artefacts OCI** dans un registry, puis les monter comme volumes (volumes d'image Kubernetes, KitOps) : même outillage que les images (versioning, cache, signature).

---

## Mises en situation

Mise en situation : ton autoscaling ajoute un réplica au pic de charge, mais le nouveau Pod met 7 minutes à servir sa première requête. Comment réduis-tu ce délai ?
?
<!--anki:664c5d31717646235664-->
1. **Décomposer le cold start** : pull de l'image, téléchargement des poids, chargement en VRAM, éventuelle compilation
2. **Pré-puller** l'image sur les nodes GPU, avec un DaemonSet
3. **Mettre les poids en cache local** sur le node, ou les servir depuis un volume partagé rapide
4. **Télécharger en init container**, ou streamer les poids directement vers le GPU
5. **Garder un socle chaud** : l'autoscaling doit anticiper, pas réagir ([[12-kubernetes-gpu-inference|K8s GPU]])

**Piège** : dimensionner l'autoscaling sur des métriques applicatives sans tenir compte du temps de démarrage.

---

Mise en situation : un collègue télécharge un modèle depuis un dépôt public et veut le déployer en production dès demain. Quels contrôles imposes-tu ?
?
<!--anki:464963526d393250565e-->
1. **Format** : privilégier **safetensors**. Un fichier pickle peut exécuter du code au chargement
2. **Provenance** : éditeur officiel, révision épinglée par empreinte, signature vérifiée si disponible ([[105-devsecops-ia-agentique|chaîne d'approvisionnement]])
3. **Licence** : usage commercial autorisé, conditions sur les modèles dérivés
4. **Evals** : qualité sur tes propres cas, pas seulement les scores annoncés
5. **Traçabilité** : version enregistrée dans le registre de modèles et épinglée dans le déploiement ([[111-mlops-llmops-fondamentaux|MLOps]])

**Piège** : charger des poids au format pickle depuis un dépôt inconnu, directement sur un serveur de production.

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
- [[164-llm-local-edge|LLM locaux & edge]] — faire tourner un modèle en local
- [[00-moc-ai-engineering|MOC AI Engineering]]
