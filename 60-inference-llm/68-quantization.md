# Quantization — Flashcards
Tags: #flashcards #ai-engineering #inference #quantization #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: intérêt en mémoire et en vitesse, quantization des poids, des activations ou du KV cache, formats (FP8, INT8, INT4, NVFP4, MXFP4), weight-only ou W8A8, granularité des échelles, outliers d'activation (SmoothQuant, rotations), PTQ ou QAT, GPTQ, AWQ, GGUF, NF4, choix de la méthode selon le matériel, calibration, mesure de la perte, divergence KL et flips, validation avant déploiement, suivi en production, outils (llm-compressor, Model Optimizer, vLLM). -->


Qu'est-ce que la quantization (quantification) d'un LLM ? <!--anki:723d7149494058234777-->
?
Représenter les nombres du modèle avec **moins de bits** : chaque valeur est ramenée sur une petite grille, avec un **facteur d'échelle** (scale) pour retrouver l'ordre de grandeur d'origine.
```text
x ≈ scale × (q − z)      q sur 8 ou 4 bits (entier ou petit flottant)
                         z = zero-point, nul en quantization symétrique
```
On peut quantizer les **poids**, les **activations** et le [[61-kv-cache-attention|KV cache]].

---

Pourquoi quantizer un LLM ? <!--anki:703678237b5b54653950-->
?
Réduire l'empreinte des **poids**, des **activations** ou du **KV cache**, selon la méthode. Des poids moins volumineux peuvent libérer du KV, réduire les lectures mémoire et permettre moins de GPU par instance.
```text
70 milliards de valeurs : BF16 ≈ 140 Go ; 8 bits ≈ 70 Go ; 4 bits ≈ 35 Go
```
Ajouter échelles, métadonnées et tenseurs conservés en précision supérieure. Le gain de vitesse dépend des kernels et de la charge : déquantification ou conversions peuvent l'annuler. Mesurer qualité par tâche, mémoire de pointe, latence et coût par réussite avant de retenir la variante.

---

Quels formats numériques rencontre-t-on ? <!--anki:4b245f5862716c2a7e75-->
?
- **BF16/FP16** : formats 16 bits, souvent utilisés comme références ; ils arrondissent eux aussi les valeurs.
- **FP8** : formats comme E4M3 et E5M2, avec compromis plage/précision.
- **INT8** : valeurs entières quantifiées, avec échelles adaptées aux tenseurs.
- **INT4** : courant pour les poids seuls, avec calcul souvent dans une précision supérieure.
- **FP4** : formats et schémas par blocs comme MXFP4 et NVFP4.

Le nom du format ne garantit ni support des kernels, ni précision des accumulations, ni qualité. Vérifier la combinaison modèle, matériel, moteur et méthode.

---

Weight-only (W4A16) ou poids + activations (W8A8) : quelle différence ? <!--anki:6b39775e3a7726676030-->
?
**WxAy** décrit la précision des poids et activations. **W4A16** réduit surtout le stockage et les lectures des poids ; les kernels déquantifient ou traitent ces représentations avec activations 16 bits. Cela peut aider le decode à petit batch.

**W8A8** réduit aussi les activations et peut exploiter des opérations matricielles en basse précision, utiles au prefill ou à batch élevé. Le détail des accumulations et conversions dépend du kernel. Aucun de ces noms ne garantit une accélération : mesurer par phase sur le matériel cible, avec la qualité comme contrainte.

---

Qu'est-ce que la granularité de quantization ? <!--anki:715b716529555e2f695a-->
?
Le nombre de valeurs qui **partagent un même facteur d'échelle** :
- **Par tenseur** : une échelle pour toute la matrice, simple mais sensible aux valeurs extrêmes
- **Par canal** : une échelle par ligne ou par colonne
- **Par groupe ou par bloc** : une échelle tous les **16 à 128 poids** (ex. groupes de 128 en INT4, blocs de 16 en NVFP4)

Plus c'est fin, plus c'est **précis**, mais les échelles occupent de la place : un INT4 par groupes de 128 coûte en réalité **≈ 4,1 à 4,25 bits par poids**.

---

Pourquoi les activations sont-elles plus difficiles à quantizer que les poids ? <!--anki:4b4355607366724d7b2a-->
?
À cause des **outliers** : dans les LLM, quelques **canaux d'activation** prennent des valeurs **bien plus grandes** que les autres. Une échelle commune écrase alors toutes les petites valeurs. Les parades :
- **SmoothQuant** : transférer la difficulté des activations vers les poids, par une mise à l'échelle par canal mathématiquement équivalente
- **Rotations** (QuaRot, SpinQuant) : multiplier par une matrice orthogonale (Hadamard) qui **étale les outliers** sur tous les canaux
- Garder ces canaux en **plus haute précision** (LLM.int8())

---

PTQ ou QAT ? <!--anki:4d4276533f3f3c26692e-->
?
- **PTQ** (post-training quantization) : on quantize un modèle **déjà entraîné**, sans données ou avec un petit jeu de **calibration**. Rapide (quelques minutes à quelques heures) : GPTQ et AWQ sont des méthodes de PTQ ; FP8 est un format utilisable dans différents schémas
- **QAT** (quantization-aware training) : on **simule la quantization pendant l'entraînement** pour que le modèle s'y adapte. Plus coûteux, mais peut mieux préserver la qualité aux précisions très basses

Des modèles sont désormais **publiés quantizés nativement**, par QAT ou post-entraînement en basse précision : gpt-oss (MXFP4), Kimi K2 Thinking (INT4).

---

Comment fonctionne GPTQ ? <!--anki:4f366a575e4973377544-->
?
Une PTQ des **poids, couche par couche** (souvent INT4 par groupes de 128). Sur un jeu de calibration, GPTQ quantize les poids **colonne par colonne** et **corrige les poids restants** pour compenser l'erreur commise, grâce à une information de second ordre (une approximation de la **hessienne**). Bonne qualité en 4 bits, avec un risque de **sur-ajuster le jeu de calibration**.

---

Comment fonctionne AWQ ? <!--anki:6f356c62755260316047-->
?
**Activation-aware Weight Quantization** : environ **1 % des poids sont décisifs**, ceux qui multiplient les **activations les plus fortes**. AWQ les repère sur un jeu de calibration et **agrandit ces canaux avant la quantization** (en compensant côté activations) pour les protéger. Il n'y a ni rétropropagation ni reconstruction : c'est rapide, et **moins dépendant du jeu de calibration** que GPTQ.

---

Quand FP8 est-il un bon candidat pour l’inférence en production ? <!--anki:505f6a2158383c2f3164-->
?
FP8 est un **candidat** lorsque le matériel et les kernels le supportent efficacement : les valeurs occupent moins de mémoire qu'en BF16 et certaines opérations peuvent être accélérées.

Ce n'est pas un défaut universel. Vérifier schéma d'échelles, checkpoint, calibration éventuelle, attention et compatibilité du runtime. Quantifier les poids n'active pas automatiquement la quantification du KV cache, qui se règle et s'évalue séparément. Comparer à une baseline sur les tâches critiques, puis mesurer goodput et mémoire de pointe ; une faible perte moyenne peut cacher une régression importante sur un segment.

---

Que sont NVFP4 et MXFP4 ? <!--anki:6d213f642a5d7670466f-->
?
Deux formats **flottants 4 bits** (E2M1) avec des **échelles par petits blocs**, exécutés nativement par les GPU **Blackwell** (≈ 2 fois le débit du FP8) :
- **MXFP4** (standard OCP) : blocs de **32** valeurs, échelle en puissance de deux. Exemple : gpt-oss
- **NVFP4** (NVIDIA) : blocs de **16** valeurs, échelle FP8 plus une échelle globale par tenseur, donc **plus précis** que MXFP4

Ils visent le **W4A4**, poids et activations en 4 bits, là où l'INT4 classique se limite aux poids.

---

Qu'est-ce que la quantization GGUF de llama.cpp ? <!--anki:4279436741614c7e3e4f-->
?
Le format de [[10-images-modeles-poids|llama.cpp et Ollama]] propose des niveaux nommés d'après leur nombre de bits :
- **Q8_0** : quasi sans perte
- **Q5_K_M, Q4_K_M** : le compromis courant (Q4_K_M ≈ 4,8 bits par poids)
- **IQ2, IQ3** : très compressés, avec une nette perte de qualité

Les **K-quants** gardent certains tenseurs en plus haute précision, et une **importance matrix** (imatrix), calculée sur des données de calibration, améliore les niveaux bas. GGUF vise le **CPU, le Mac et le local**, pas le serving à forte concurrence.

---

Qu'est-ce que NF4 et quand l'utiliser ? <!--anki:79393c4d63614f3a6148-->
?
**NormalFloat 4 bits**, le format de **bitsandbytes** : ses 16 niveaux sont placés selon une **loi normale**, la distribution typique des poids. C'est la base de **QLoRA** ([[51-fine-tuning-adaptation|fine-tuning]]) : charger un gros modèle en 4 bits pour l'adapter sur un petit GPU. Pour le **serving**, on préfère FP8, AWQ ou GPTQ, qui ont des noyaux bien plus rapides.

---

Quelle méthode de quantization choisir selon le contexte ? <!--anki:66505d4d5421646f257b-->
?
- **GPU Hopper ou Blackwell en production** : **FP8** (W8A8) à évaluer ; **NVFP4** sur Blackwell si les evals tiennent
- **GPU Ampere (A100) ou grand public, mémoire serrée** : **INT4 weight-only** (AWQ ou GPTQ, avec les noyaux Marlin) ; **INT8 W8A8** (SmoothQuant) pour le débit
- **CPU, Mac, poste local** : **GGUF de Q4_K_M à Q8_0**, ou MLX sur Apple Silicon
- **Fine-tuning sur un petit GPU** : **NF4** avec QLoRA
- **Modèle publié déjà quantizé** (QAT) : garder son **format natif**

---

Que garde-t-on généralement en haute précision ? <!--anki:652a504b395d47797b63-->
?
Les parties petites mais sensibles : **embeddings**, **lm_head** (la couche de sortie), **normalisations**, et dans les **MoE** le **routeur**, souvent l'attention aussi. On quantize d'abord les **couches linéaires**, et en priorité les **experts des MoE**, qui représentent l'essentiel des poids.

---

Pourquoi le jeu de calibration compte-t-il ? <!--anki:486856647e3f6424266b-->
?
GPTQ, AWQ, SmoothQuant ou le FP8 statique fixent leurs échelles à partir de **quelques centaines d'exemples**. S'ils ne ressemblent pas au trafic réel (autre langue, code, contexte long, format de chat), la qualité baisse **précisément sur ce trafic**. Il faut des exemples **représentatifs du domaine**, formatés avec le **chat template** du modèle.

---

Comment mesurer la perte de qualité d'un modèle quantizé ? <!--anki:64773d654d3b283f5942-->
?
Comparer à la **variante de référence** sur un jeu métier distinct des données de calibration, avec évaluations appariées. Mesurer format, exactitude, outils, langues, raisonnement et contextes longs par segment.

Définir à l'avance la perte acceptable et rapporter l'incertitude ; une perplexité similaire ou un score global stable ne suffit pas. Observer aussi les réponses devenues fausses, les corrections et les changements de longueur. Il n'existe pas de perte universelle de « 1 à 3 % » en INT4, ni de garantie de quasi-équivalence en FP8 : modèle, données et kernels déterminent le résultat.

---

Quelles métriques comparent directement un modèle quantizé à sa version BF16 ? <!--anki:782d547b304c23294b65-->
?
On fait tourner les deux modèles sur les **mêmes textes** et on compare leurs sorties token par token :
- **Divergence KL** moyenne entre les deux distributions de probabilités (0 = identiques) : la mesure la plus sensible
- **Accord du top-1** : part des positions où les deux modèles choisissent le même token
- **Δ perplexité** : l'écart de perplexité, utile mais grossier
- **Flips** : réponses d'eval qui passent de juste à faux (ou l'inverse), alors que le score global peut rester identique

llama.cpp calcule la divergence KL et l'accord du top-1 avec `llama-perplexity --kl-divergence`.

---

Comment valider un modèle quantizé avant de le déployer ? <!--anki:4e602c2f2d606e6e4977-->
?
Avec un **eval gate**, en comparant au modèle BF16 ([[112-cicd-modeles|CI/CD des modèles]]) :
1. **Evals métier** question par question, avec un seuil fixé à l'avance (ex. ≥ 99 % du score BF16 sur chaque tâche critique)
2. **Tests de format** : validité du JSON et des appels d'outils, contexte long
3. **Benchmark de charge** sur le matériel cible : le gain en TPOT, débit ou nombre de GPU est-il réel ?
4. **Canary ou shadow** sur du trafic réel avant la bascule complète

---

Que surveiller en production après une quantization ? <!--anki:48663f2b752d297e6f7d-->
?
- **Performance**, pour confirmer le gain : TPOT, TTFT, débit, occupation du KV cache et concurrence atteinte
- **Qualité**, pour repérer une perte que les evals n'ont pas vue : taux d'échec de validation (JSON, outils), taux de `finish_reason=length` (boucles), taux de refus, longueur des réponses, feedback et scores LLM-as-judge **par segment** (langue, tâche)

Chaque métrique est étiquetée avec la **variante du modèle** pour comparer à la version BF16 ([[93-monitoring-inference|monitoring de l'inférence]]).

---

À mémoire égale, vaut-il mieux un grand modèle quantizé ou un petit modèle en pleine précision ? <!--anki:78244434472d6f667748-->
?
Comparer les deux options **sur la tâche et sous la même contrainte de service**. Un modèle plus grand quantifié peut mieux répondre, mais conserve parfois davantage de calcul, de KV ou de communication ; il peut perdre son avantage en latence ou en concurrence.

Un petit modèle récent ou spécialisé peut être préférable. Mesurer qualité par segment, longueur des réponses, mémoire de pointe, goodput et coût par tâche réussie. Le nombre de bits et de paramètres ne permet pas, seul, de désigner le gagnant. Inclure une référence commune et un protocole de charge reproductible.

---

Avec quel outil produire un checkpoint quantizé pour vLLM, pour TensorRT-LLM ou pour llama.cpp ? <!--anki:3433393265393632646633333430666638643537616161333766356464343137-->
?
- **vLLM ou SGLang** : **llm-compressor** (projet vLLM : GPTQ, AWQ, SmoothQuant, FP8, NVFP4, au format *compressed-tensors*)
- **TensorRT-LLM** : **NVIDIA Model Optimizer** (FP8, NVFP4, INT4 AWQ), dont les checkpoints servent aussi à vLLM et SGLang
- **llama.cpp et Ollama** : `llama-quantize` vers GGUF
- **Souvent rien à faire** : des checkpoints déjà quantizés existent sur Hugging Face (`-FP8`, `-AWQ`, `-GPTQ-Int4`, `-GGUF`)

Autres : GPTQModel, bitsandbytes. AutoAWQ et AutoGPTQ ne sont plus maintenus.

---

Comment servir un checkpoint quantizé avec vLLM ? <!--anki:3836366337646562333134363438346162663163383366663563393835353332-->
?
vLLM **lit la méthode dans la configuration du checkpoint**, et sait aussi quantizer en FP8 **à la volée** ([[11-serveurs-inference-llm|serveurs d'inférence]]) :
```bash
vllm serve org/modele-AWQ                     # méthode détectée automatiquement
vllm serve org/modele --quantization fp8 \
           --kv-cache-dtype fp8               # poids FP8 à la volée + KV cache FP8
```

Vérifier la compatibilité entre checkpoint, GPU et kernels avant lancement. Le FP8 à la volée peut nécessiter de charger une base plus volumineuse au démarrage ; tenir après conversion ne garantit pas de passer ce pic. Évaluer séparément la qualité des poids et du KV cache quantifiés, puis mesurer le gain sous charge.

---

À ne pas confondre : quantization des poids, des activations et du KV cache ? <!--anki:472f61333a5d544d7225-->
?
- **Poids** (W4A16, W8) : réduit la **mémoire du modèle** et accélère le **decode** memory-bound
- **Activations** (W8A8, FP8) : permet les calculs en basse précision sur les unités dédiées, et accélère aussi le **prefill** compute-bound
- **KV cache** (FP8) : réduit la mémoire **par requête**, donc augmente la **concurrence** et la longueur de contexte servable ([[61-kv-cache-attention|KV cache]])

Trois réglages indépendants, à valider séparément ([[69-roofline-prefill-decode|roofline]]).

---

## Mises en situation

Mise en situation : tu dois servir un modèle 70B sur des GPU A100 de 80 Go, avec un budget de deux GPU. Quelle quantization choisis-tu ? <!--anki:786c3b6c673a2d742b6b-->
?
1. **Budgéter** : environ 140 Go de poids BF16 sur 160 Go nominaux laissent une marge étroite ; vérifier réserves, activations et KV par GPU, sans déclarer cela impossible par principe.
2. **Vérifier les kernels** : les A100 n'ont pas de calcul Tensor Core FP8 natif.
3. **Comparer les candidats supportés** : INT4 weight-only, INT8 ou BF16 si le budget suffit.
4. **Tester le workload** : longs prompts, contexte résident, concurrence et délais attendus.
5. **Valider qualité et goodput** avant de retenir le format.

**Piège** : choisir une quantification uniquement à partir de la taille des fichiers ou d'un gain théorique.

---

Mise en situation : après le passage en INT4, tes evals globales perdent seulement 1 %, mais le support signale des réponses fausses en allemand et sur les longs documents. Que fais-tu ? <!--anki:733a714d6e3255376136-->
?
1. **Ne pas se fier à la moyenne** : les pertes se concentrent sur des segments précis
2. **Évaluer par segment** : langue, longueur de contexte, type de tâche, appels d'outils
3. **Mesurer finement** : divergence KL et accord du top-1 contre le modèle BF16 sur ces cas
4. **Corriger** : granularité plus fine, calibration représentative (allemand, documents longs), ou passage en FP8
5. **Router** : garder le modèle non quantizé pour les segments sensibles, le temps de corriger ([[82-routing-llm|routing]])

**Piège** : calibrer sur un corpus anglais générique pour un service multilingue.

---

Mise en situation : ton fournisseur publie le même modèle en BF16, FP8 et GGUF Q4_K_M. Trois équipes te demandent lequel prendre : production GPU, poste de développeur, démonstration hors ligne. Que réponds-tu ? <!--anki:4645564758673a5d7750-->
?
1. **Production GPU récent** : **FP8 à évaluer**, avec kernels compatibles et mesure séparée de la qualité et de la mémoire
2. **Poste de développeur** : **GGUF Q4_K_M** avec llama.cpp ou Ollama, qui tourne sur CPU ou Mac
3. **Démonstration hors ligne** : GGUF aussi, en privilégiant Q5_K_M ou Q8_0 si la machine le permet
4. **Rappeler** que ces variantes ne donnent pas les mêmes sorties : les evals doivent être refaites par variante
5. **Tracer** la variante servie dans les métriques et les traces ([[93-monitoring-inference|monitoring]])

**Piège** : valider la qualité sur le poste du développeur en GGUF, puis déployer une autre variante en production.

---

## Sources

- [vLLM — quantification et matériels compatibles](https://docs.vllm.ai/en/latest/features/quantization/)
- [llama.cpp — formats, quantification et inférence locale](https://github.com/ggml-org/llama.cpp)

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
- [[164-llm-local-edge|LLM locaux & edge]] — GGUF et petits appareils
- [[69-roofline-prefill-decode|Roofline]] — pourquoi la quantization accélère surtout le decode
- [[134-recherche-vectorielle-ann|Recherche vectorielle]] — index ANN, HNSW et quantization des vecteurs
- [[136-mixture-of-experts|Mixture of Experts]] — paramètres totaux et actifs
- [[95-llm-as-judge|LLM-as-a-judge]] — noter automatiquement, et valider le juge
- [[133-embeddings-representations|Embeddings]] — représenter le sens par des vecteurs
- [[137-long-contexte|Long contexte]] — limites et coût des longues fenêtres
- [[00-moc-ai-engineering|MOC AI Engineering]]
