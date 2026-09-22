# Quantization — Flashcards
Tags: #flashcards #ai-engineering #inference #quantization #llm

Qu'est-ce que la quantization (quantification) d'un LLM ?
?
Représenter les nombres du modèle avec **moins de bits** : chaque valeur est ramenée sur une petite grille, avec un **facteur d'échelle** (scale) pour retrouver l'ordre de grandeur d'origine.
```text
x ≈ scale × (q − z)      q sur 8 ou 4 bits (entier ou petit flottant)
                         z = zero-point, nul en quantization symétrique
```
On peut quantizer les **poids**, les **activations** et le [[61-kv-cache-attention|KV cache]].

---

Pourquoi quantizer un LLM ?
?
- **Moins de VRAM** : les poids sont divisés par 2 (8 bits) ou par 4 (4 bits) par rapport au BF16
- **Decode plus rapide** : il est limité par la bande passante mémoire, et on relit moins d'octets à chaque token
- **Plus de place pour le KV cache**, donc plus de requêtes en parallèle
- **Moins de GPU par réplica**, donc un coût par token plus bas ([[121-couts-inference|coûts]])
```text
70B : BF16 ≈ 140 Go · FP8 ≈ 70 Go · INT4 ≈ 35-40 Go
```

---

Quels formats numériques rencontre-t-on ?
?
- **BF16 / FP16** (16 bits) : la référence, considérée sans perte
- **FP8** (8 bits) : le défaut en production sur les GPU récents. **E4M3** (plus de précision) pour l'inférence, **E5M2** (plus de plage) pour les gradients
- **INT8** (8 bits) : poids et activations sur les GPU sans FP8 (Ampere)
- **INT4** (4 bits) : surtout pour les poids seuls (AWQ, GPTQ, GGUF)
- **FP4** (4 bits : NVFP4, MXFP4) : poids et activations sur Blackwell

---

Weight-only (W4A16) ou poids + activations (W8A8) : quelle différence ?
?
La notation **WxAy** donne le nombre de bits des poids (W) et des activations (A).
- **W4A16** (weight-only) : poids stockés en 4 bits, **déquantizés à la volée**, calcul en 16 bits. Accélère le **decode à petit batch**, limité par la mémoire, mais pas le prefill ; à gros batch, le gain disparaît
- **W8A8** (FP8 ou INT8) : le **calcul lui-même** se fait en 8 bits sur les tensor cores, ce qui accélère aussi le **prefill** et les **gros batchs**

Voir [[62-optimisations-inference|prefill et decode]] et [[64-metriques-slo-inference|TTFT et TPOT]].

---

Qu'est-ce que la granularité de quantization ?
?
Le nombre de valeurs qui **partagent un même facteur d'échelle** :
- **Par tenseur** : une échelle pour toute la matrice, simple mais sensible aux valeurs extrêmes
- **Par canal** : une échelle par ligne ou par colonne
- **Par groupe ou par bloc** : une échelle tous les **16 à 128 poids** (ex. groupes de 128 en INT4, blocs de 16 en NVFP4)

Plus c'est fin, plus c'est **précis**, mais les échelles occupent de la place : un INT4 par groupes de 128 coûte en réalité **≈ 4,1 à 4,25 bits par poids**.

---

Pourquoi les activations sont-elles plus difficiles à quantizer que les poids ?
?
À cause des **outliers** : dans les LLM, quelques **canaux d'activation** prennent des valeurs **bien plus grandes** que les autres. Une échelle commune écrase alors toutes les petites valeurs. Les parades :
- **SmoothQuant** : transférer la difficulté des activations vers les poids, par une mise à l'échelle par canal mathématiquement équivalente
- **Rotations** (QuaRot, SpinQuant) : multiplier par une matrice orthogonale (Hadamard) qui **étale les outliers** sur tous les canaux
- Garder ces canaux en **plus haute précision** (LLM.int8())

---

PTQ ou QAT ?
?
- **PTQ** (post-training quantization) : on quantize un modèle **déjà entraîné**, sans données ou avec un petit jeu de **calibration**. Rapide (quelques minutes à quelques heures) : GPTQ, AWQ et FP8 sont des PTQ
- **QAT** (quantization-aware training) : on **simule la quantization pendant l'entraînement** pour que le modèle s'y adapte. Plus coûteux, mais **nettement meilleur en 4 bits et en dessous**

Des modèles sont désormais **publiés quantizés nativement**, par QAT ou post-entraînement en basse précision : gpt-oss (MXFP4), Kimi K2 Thinking (INT4).

---

Comment fonctionne GPTQ ?
?
Une PTQ des **poids, couche par couche** (souvent INT4 par groupes de 128). Sur un jeu de calibration, GPTQ quantize les poids **colonne par colonne** et **corrige les poids restants** pour compenser l'erreur commise, grâce à une information de second ordre (une approximation de la **hessienne**). Bonne qualité en 4 bits, avec un risque de **sur-ajuster le jeu de calibration**.

---

Comment fonctionne AWQ ?
?
**Activation-aware Weight Quantization** : environ **1 % des poids sont décisifs**, ceux qui multiplient les **activations les plus fortes**. AWQ les repère sur un jeu de calibration et **agrandit ces canaux avant la quantization** (en compensant côté activations) pour les protéger. Il n'y a ni rétropropagation ni reconstruction : c'est rapide, et **moins dépendant du jeu de calibration** que GPTQ.

---

Pourquoi FP8 est-il le choix par défaut en production ?
?
- **Quasi sans perte** sur la plupart des tâches, avec des poids et un KV cache **divisés par deux**
- **Calcul natif sur les tensor cores** des GPU récents (H100, H200, L40S, B200, MI300) : gain en **débit** et en **TTFT**, pas seulement en mémoire
- **Peu d'effort** : dans vLLM, `--quantization fp8` quantize à la volée, **sans calibration**, avec des échelles d'activation calculées dynamiquement

---

Que sont NVFP4 et MXFP4 ?
?
Deux formats **flottants 4 bits** (E2M1) avec des **échelles par petits blocs**, exécutés nativement par les GPU **Blackwell** (≈ 2 fois le débit du FP8) :
- **MXFP4** (standard OCP) : blocs de **32** valeurs, échelle en puissance de deux. Exemple : gpt-oss
- **NVFP4** (NVIDIA) : blocs de **16** valeurs, échelle FP8 plus une échelle globale par tenseur, donc **plus précis** que MXFP4

Ils visent le **W4A4**, poids et activations en 4 bits, là où l'INT4 classique se limite aux poids.

---

Qu'est-ce que la quantization GGUF de llama.cpp ?
?
Le format de [[10-images-modeles-poids|llama.cpp et Ollama]] propose des niveaux nommés d'après leur nombre de bits :
- **Q8_0** : quasi sans perte
- **Q5_K_M, Q4_K_M** : le compromis courant (Q4_K_M ≈ 4,8 bits par poids)
- **IQ2, IQ3** : très compressés, avec une nette perte de qualité

Les **K-quants** gardent certains tenseurs en plus haute précision, et une **importance matrix** (imatrix), calculée sur des données de calibration, améliore les niveaux bas. GGUF vise le **CPU, le Mac et le local**, pas le serving à forte concurrence.

---

Qu'est-ce que NF4 et quand l'utiliser ?
?
**NormalFloat 4 bits**, le format de **bitsandbytes** : ses 16 niveaux sont placés selon une **loi normale**, la distribution typique des poids. C'est la base de **QLoRA** ([[51-fine-tuning-adaptation|fine-tuning]]) : charger un gros modèle en 4 bits pour l'adapter sur un petit GPU. Pour le **serving**, on préfère FP8, AWQ ou GPTQ, qui ont des noyaux bien plus rapides.

---

Quelle méthode de quantization choisir selon le contexte ?
?
- **GPU Hopper ou Blackwell en production** : **FP8** (W8A8) par défaut ; **NVFP4** sur Blackwell si les evals tiennent
- **GPU Ampere (A100) ou grand public, mémoire serrée** : **INT4 weight-only** (AWQ ou GPTQ, avec les noyaux Marlin) ; **INT8 W8A8** (SmoothQuant) pour le débit
- **CPU, Mac, poste local** : **GGUF de Q4_K_M à Q8_0**, ou MLX sur Apple Silicon
- **Fine-tuning sur un petit GPU** : **NF4** avec QLoRA
- **Modèle publié déjà quantizé** (QAT) : garder son **format natif**

---

Que garde-t-on généralement en haute précision ?
?
Les parties petites mais sensibles : **embeddings**, **lm_head** (la couche de sortie), **normalisations**, et dans les **MoE** le **routeur**, souvent l'attention aussi. On quantize d'abord les **couches linéaires**, et en priorité les **experts des MoE**, qui représentent l'essentiel des poids.

---

Pourquoi le jeu de calibration compte-t-il ?
?
GPTQ, AWQ, SmoothQuant ou le FP8 statique fixent leurs échelles à partir de **quelques centaines d'exemples**. S'ils ne ressemblent pas au trafic réel (autre langue, code, contexte long, format de chat), la qualité baisse **précisément sur ce trafic**. Il faut des exemples **représentatifs du domaine**, formatés avec le **chat template** du modèle.

---

Comment mesurer la perte de qualité d'un modèle quantizé ?
?
La **perplexité** ne suffit pas ([[65-probabilites-sampling|probabilités]]). On compare le modèle quantizé à la **version BF16 sur ses propres evals**, question par question ([[114-reproductibilite-variance|comparaison appariée]]), en surveillant les zones fragiles : **raisonnement long, maths, code, contexte long, langues autres que l'anglais, tool calling**, et les **petits modèles**. Ordres de grandeur :
- **FP8 et INT8** : quasi sans perte
- **INT4 weight-only** : à 1 à 3 % près sur les gros modèles
- **Sous 4 bits** : dégradation nette

---

Quelles métriques comparent directement un modèle quantizé à sa version BF16 ?
?
On fait tourner les deux modèles sur les **mêmes textes** et on compare leurs sorties token par token :
- **Divergence KL** moyenne entre les deux distributions de probabilités (0 = identiques) : la mesure la plus sensible
- **Accord du top-1** : part des positions où les deux modèles choisissent le même token
- **Δ perplexité** : l'écart de perplexité, utile mais grossier
- **Flips** : réponses d'eval qui passent de juste à faux (ou l'inverse), alors que le score global peut rester identique

llama.cpp calcule la divergence KL et l'accord du top-1 avec `llama-perplexity --kl-divergence`.

---

Comment valider un modèle quantizé avant de le déployer ?
?
Avec un **eval gate**, en comparant au modèle BF16 ([[112-cicd-modeles|CI/CD des modèles]]) :
1. **Evals métier** question par question, avec un seuil fixé à l'avance (ex. ≥ 99 % du score BF16 sur chaque tâche critique)
2. **Tests de format** : validité du JSON et des appels d'outils, contexte long
3. **Benchmark de charge** sur le matériel cible : le gain en TPOT, débit ou nombre de GPU est-il réel ?
4. **Canary ou shadow** sur du trafic réel avant la bascule complète

---

Que surveiller en production après une quantization ?
?
- **Performance**, pour confirmer le gain : TPOT, TTFT, débit, occupation du KV cache et concurrence atteinte
- **Qualité**, pour repérer une perte que les evals n'ont pas vue : taux d'échec de validation (JSON, outils), taux de `finish_reason=length` (boucles), taux de refus, longueur des réponses, feedback et scores LLM-as-judge **par segment** (langue, tâche)

Chaque métrique est étiquetée avec la **variante du modèle** pour comparer à la version BF16 ([[93-monitoring-inference|monitoring de l'inférence]]).

---

À mémoire égale, vaut-il mieux un grand modèle quantizé ou un petit modèle en pleine précision ?
?
En général **le grand modèle quantizé** : à budget mémoire fixe, **4 bits** est souvent le meilleur compromis entre taille et précision. En dessous, la perte finit par annuler l'avantage de taille. Nuance : les modèles récents, **entraînés sur beaucoup plus de tokens**, supportent moins bien une quantization agressive, d'où la montée du QAT.

---

Quels outils pour quantizer et servir un modèle quantizé ?
?
- **llm-compressor** (projet vLLM) : GPTQ, AWQ, SmoothQuant, FP8, NVFP4, au format *compressed-tensors*
- **NVIDIA Model Optimizer** : FP8, NVFP4, INT4 AWQ pour TensorRT-LLM, vLLM et SGLang
- **GPTQModel**, **bitsandbytes**, `llama-quantize` pour GGUF (AutoAWQ et AutoGPTQ ne sont plus maintenus)
- Des **checkpoints déjà quantizés** sur Hugging Face (suffixes `-FP8`, `-AWQ`, `-GPTQ-Int4`, `-GGUF`)

Le [[11-serveurs-inference-llm|serveur d'inférence]] lit la méthode dans la configuration du checkpoint :
```bash
vllm serve org/modele-AWQ                     # méthode détectée automatiquement
vllm serve org/modele --quantization fp8 \
           --kv-cache-dtype fp8               # poids FP8 à la volée + KV cache FP8
```

---

## Connexions
- [[62-optimisations-inference|Optimisations d'inférence]] — prefill, decode et bande passante mémoire
- [[61-kv-cache-attention|KV cache & attention]] — quantizer le cache
- [[64-metriques-slo-inference|Métriques & SLO]] — l'effet sur TTFT, TPOT et débit
- [[10-images-modeles-poids|Images & poids de modèles]] — taille des poids, format GGUF
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, TensorRT-LLM, llama.cpp
- [[51-fine-tuning-adaptation|Fine-tuning]] — QLoRA et NF4
- [[121-couts-inference|Coûts d'inférence]] — moins de GPU par réplica
- [[114-reproductibilite-variance|Reproductibilité & variance]] — comparer avant et après quantization
- [[67-speculative-decoding|Speculative decoding]] — l'autre levier pour accélérer le decode
- [[93-monitoring-inference|Monitoring de l'inférence]] — suivre le modèle quantizé en production
- [[00-moc-ai-engineering|MOC AI Engineering]]
