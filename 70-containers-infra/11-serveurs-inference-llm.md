# Serveurs d'inférence LLM — Flashcards
Tags: #flashcards #ai-engineering #inference #serving #llm

À quoi sert un serveur d'inférence LLM ?
?
À **charger le modèle sur les GPU** et le servir efficacement à de nombreux utilisateurs : batching, gestion du [[61-kv-cache-attention|KV cache]], streaming, **API HTTP** et métriques.

---

Pourquoi ne pas servir un modèle avec un simple script Transformers ?
?
Parce qu'il traite les requêtes **une par une** ou en batch statique : GPU sous-utilisé, mémoire gaspillée, débit **10 à 20 fois inférieur** à un serveur optimisé.

---

Qu'est-ce que vLLM ?
?
Le serveur d'inférence open source de référence : **PagedAttention**, **continuous batching**, prefix caching, quantization, tensor parallelism, [[63-guided-generation|guided generation]] et **API compatible OpenAI**.

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --max-model-len 8192
```

---

Pourquoi l'API compatible OpenAI est-elle importante ?
?
Elle permet de **changer de backend sans modifier le code client** : SDK OpenAI, [[81-litellm-api-layer|LiteLLM]] et frameworks d'agents parlent au serveur auto-hébergé comme à une API cloud.

---

Qu'est-ce que le multi-LoRA en serving ?
?
Charger **plusieurs adapters [[51-fine-tuning-adaptation|LoRA]]** au-dessus d'un **seul modèle de base** en VRAM : chaque requête choisit son adapter, et on sert des dizaines de variantes fine-tunées pour le prix d'un modèle.

---

Qu'est-ce que SGLang ?
?
Un serveur concurrent de vLLM, très performant, avec **RadixAttention** (arbre de préfixes partagés en cache) : particulièrement efficace pour les workloads **agentiques** et multi-appels qui réutilisent de longs préfixes.

---

Qu'est-ce que TensorRT-LLM et Triton ?
?
- **TensorRT-LLM** : bibliothèque NVIDIA qui **compile** le modèle en moteurs optimisés pour ses GPU (performances maximales, moins flexible)
- **Triton Inference Server** : serveur NVIDIA **multi-framework** (TensorRT, PyTorch, ONNX) avec batching dynamique

---

Et TGI ?
?
**Text Generation Inference** (Hugging Face) : serveur historiquement très utilisé, aujourd'hui **en mode maintenance** ; Hugging Face oriente vers vLLM et SGLang.

---

Qu'utiliser pour l'inférence locale ?
?
**llama.cpp** et **Ollama** : modèles **GGUF quantizés**, CPU, Mac (Apple Silicon) ou GPU grand public. Parfaits pour le dev local, pas pour une forte concurrence en production.

---

Quels critères pour choisir un serveur ?
?
**Support du modèle** et du matériel, débit et latence mesurés sur **votre** charge ([[64-metriques-slo-inference|benchmark]]), fonctionnalités (LoRA, guided generation, prefix caching), métriques exposées, maturité et facilité d'opération sur Kubernetes.

---

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — PagedAttention
- [[62-optimisations-inference|Optimisations d'inférence]] — ce que le serveur implémente
- [[51-fine-tuning-adaptation|Fine-tuning]] — multi-LoRA en serving
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — le déploiement
- [[09-gpu-conteneurs|GPU en conteneur]] — l'accès au GPU
- [[10-images-modeles-poids|Images & poids]] — chargement des poids
- [[13-apptainer-inference-hpc|Apptainer & HPC]] — serving en cluster HPC
- [[00-index|Index Conteneurs]]
- [[66-prefix-caching-radix-attention|Prefix caching & RadixAttention]] — RadixAttention de SGLang
- [[67-speculative-decoding|Speculative decoding]] — activer et régler dans vLLM ou SGLang
- [[68-quantization|Quantization]] — servir des modèles FP8, AWQ, GPTQ ou GGUF
- [[93-monitoring-inference|Monitoring de l'inférence]] — exploiter `/metrics` et `/health`
- [[00-moc-ai-engineering|MOC AI Engineering]]
