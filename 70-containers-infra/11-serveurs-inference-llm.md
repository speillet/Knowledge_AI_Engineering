# Serveurs d'inférence LLM — Flashcards
Tags: #flashcards #ai-engineering #inference #serving #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: vLLM, API compatible OpenAI, multi-LoRA, SGLang, TensorRT-LLM et Triton, TGI, llama.cpp et Ollama. -->


À quoi sert un serveur d'inférence LLM ? <!--anki:495d704d38615143496f-->
?
À **charger le modèle sur les GPU** et le servir efficacement à de nombreux utilisateurs : batching, gestion du [[61-kv-cache-attention|KV cache]], streaming, **API HTTP** et métriques.

---

À ne pas confondre : serveur d'inférence et gateway LLM ? <!--anki:4441306c4a2b54426b3d-->
?
- **Serveur d'inférence** (vLLM, SGLang, TensorRT-LLM) : il **exécute le modèle** sur des GPU. Un serveur, un ou quelques modèles chargés en VRAM
- **Gateway LLM** ([[81-litellm-api-layer|LiteLLM]]) : il **ne calcule rien**. Il route vers des modèles, gère clés, budgets, quotas, fallbacks et traces

Chaîne complète : `client → Ingress → gateway LLM → serveur d'inférence → GPU`. Les deux exposent souvent la **même API compatible OpenAI**, ce qui explique la confusion.

---

Pourquoi ne pas servir un modèle avec un simple script Transformers ? <!--anki:7371754d53625342432e-->
?
Parce qu'il traite les requêtes **une par une** ou en batch statique : GPU sous-utilisé, mémoire gaspillée, débit **10 à 20 fois inférieur** à un serveur optimisé.

---

Qu'est-ce que vLLM ? <!--anki:6a7a656152266d58602f-->
?
Le serveur d'inférence open source de référence : **PagedAttention**, **continuous batching**, prefix caching, quantization, tensor parallelism, [[63-guided-generation|guided generation]] et **API compatible OpenAI**.

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --max-model-len 8192
```

---

Pourquoi l'API compatible OpenAI est-elle importante ? <!--anki:484b513771565d286c7b-->
?
Elle permet de **changer de backend sans modifier le code client** : SDK OpenAI, [[81-litellm-api-layer|LiteLLM]] et frameworks d'agents parlent au serveur auto-hébergé comme à une API cloud.

---

Qu'est-ce que le multi-LoRA en serving ? <!--anki:46362e6e346d5f39534d-->
?
Charger **plusieurs adapters [[51-fine-tuning-adaptation|LoRA]]** au-dessus d'un **seul modèle de base** en VRAM : chaque requête choisit son adapter, et on sert des dizaines de variantes fine-tunées pour le prix d'un modèle.

---

Qu'est-ce que SGLang ? <!--anki:483f5936213a34336e4e-->
?
Un serveur concurrent de vLLM, très performant, avec **RadixAttention** (arbre de préfixes partagés en cache) : particulièrement efficace pour les workloads **agentiques** et multi-appels qui réutilisent de longs préfixes.

---

Qu'est-ce que TensorRT-LLM et Triton ? <!--anki:703f3e3e306448765b68-->
?
- **TensorRT-LLM** : bibliothèque NVIDIA qui **compile** le modèle en moteurs optimisés pour ses GPU (performances maximales, moins flexible)
- **Triton Inference Server** : serveur NVIDIA **multi-framework** (TensorRT, PyTorch, ONNX) avec batching dynamique

---

Où en est TGI (Text Generation Inference) de Hugging Face ? <!--anki:62455d30213b665d742b-->
?
**Text Generation Inference** (Hugging Face) : serveur historiquement très utilisé, aujourd'hui **en mode maintenance** ; Hugging Face oriente vers vLLM et SGLang.

---

Quel serveur utiliser pour l'inférence LLM locale ? <!--anki:6f484e484e652c34492a-->
?
**llama.cpp** et **Ollama** : modèles **GGUF quantizés**, CPU, Mac (Apple Silicon) ou GPU grand public. Parfaits pour le dev local, pas pour une forte concurrence en production.
```bash
ollama run llama3.1:8b                       # local, un utilisateur
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --max-model-len 8192 --gpu-memory-utilization 0.9   # serveur, multi-utilisateurs
```
La bascule se fait dès que plusieurs utilisateurs arrivent en même temps : le **continuous batching** de vLLM change tout le débit ([[164-llm-local-edge|LLM locaux]]).

---

Quels critères pour choisir un serveur ? <!--anki:645063305f2e3f68515b-->
?
**Support du modèle** et du matériel, débit et latence mesurés sur **votre** charge ([[64-metriques-slo-inference|benchmark]]), fonctionnalités (LoRA, guided generation, prefix caching), métriques exposées, maturité et facilité d'opération sur Kubernetes.

---

## Mises en situation

Mise en situation : une équipe sert un modèle 8B avec un script Transformers derrière FastAPI. À 30 utilisateurs, tout s'effondre. Que proposes-tu, et quels gains annonces-tu ? <!--anki:6c3f6a2157402575507b-->
?
1. **Diagnostiquer** : traitement requête par requête, GPU sous-utilisé, pas de gestion du KV cache
2. **Passer à un serveur d'inférence** : vLLM ou SGLang, avec continuous batching et PagedAttention
3. **Annoncer un ordre de grandeur**, pas une promesse : un facteur 10 à 20 sur le débit est courant, à mesurer sur la charge réelle
4. **Garder l'API compatible OpenAI**, pour ne pas toucher au code client ([[81-litellm-api-layer|gateway]])
5. **Mesurer avant et après** : TTFT, TPOT, débit et concurrence tenue ([[64-metriques-slo-inference|SLO]])

**Piège** : ajouter des réplicas du script existant, ce qui multiplie le coût sans corriger le problème.

---

Mise en situation : ton entreprise a 15 variantes fine-tunées d'un même modèle 8B, une par client. Faut-il 15 déploiements ? <!--anki:6f3158764657234e4e3a-->
?
1. **Non, si ce sont des LoRA** : le **multi-LoRA** charge plusieurs adapters au-dessus d'un seul modèle de base en VRAM
2. **Chaque requête choisit son adapter**, ce qui permet de servir des dizaines de variantes pour le prix d'un modèle
3. **Attention à la VRAM** : les adapters sont petits, mais leur nombre et le KV cache restent à surveiller
4. **Cloisonner** : vérifier qu'une requête d'un client ne peut pas viser l'adapter d'un autre
5. **Si les variantes sont des fine-tunings complets** : là, il faut bien des déploiements séparés ([[51-fine-tuning-adaptation|fine-tuning]])

**Piège** : fusionner les adapters dans les poids de base « pour simplifier », et perdre le bénéfice du partage.

---

## Sources

- [SGLang — documentation du serveur et de ses optimisations](https://docs.sglang.io/)
- [vLLM — métriques de production](https://docs.vllm.ai/en/latest/usage/metrics/)

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
- [[164-llm-local-edge|LLM locaux & edge]] — Ollama, llama.cpp, MLX
- [[132-tokenisation|Tokenisation]] — chat templates
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — l'orchestration et son interface avec le runtime
- [[114-reproductibilite-variance|Reproductibilité & variance]] — non-déterminisme et statistiques d'evals
- [[148-pipelines-batch-llm|Pipelines batch]] — traiter des millions d'items à moindre coût
- [[65-probabilites-sampling|Probabilités & sampling]] — température, top-p et logprobs
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — ce qui limite chaque phase de l'inférence
- [[83-gateway-ingress|Ingress & API gateway]] — l'entrée réseau de la stack
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — quel protocole à quelle frontière de l'agent
- [[00-moc-ai-engineering|MOC AI Engineering]]
