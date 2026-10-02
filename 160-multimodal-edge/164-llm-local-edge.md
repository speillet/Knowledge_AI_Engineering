# LLM locaux, on-prem & edge — Flashcards
Tags: #flashcards #ai-engineering #edge #local #self-hosting #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: motivations, capacité ou bande passante mémoire, llama.cpp et GGUF, outils locaux, Ollama ou vLLM, Apple Silicon, small language models, hybride local et cloud, flotte d'appareils, rentabilité du on-prem. -->

Pourquoi faire tourner un LLM en local ou sur site ?
?
<!--anki:68767b39524b69526735-->
- **Confidentialité / souveraineté** : les données ne sortent pas.
- **Hors ligne** ou réseau contraint (usine, terrain, embarqué).
- **Latence** sans aller-retour réseau.
- **Coût** marginal nul à fort volume sur du matériel déjà payé.
- **Contrôle** : version figée, pas de dépréciation imposée.

---

Quel est le facteur limitant sur un poste ou un appareil ?
?
<!--anki:67755876354173497641-->
La **mémoire** (VRAM, RAM unifiée) et sa **bande passante**. Le décodage lit **tous les poids actifs à chaque token** : débit ≈ bande passante mémoire / taille des poids. Un modèle de 8 B en 4 bits (~5 Go) sur 100 Go/s de bande passante donne au mieux ~**20 tokens/s**.

---

Qu'est-ce que llama.cpp et le format GGUF ?
?
<!--anki:647e555f4a2a7a723579-->
**llama.cpp** : moteur d'inférence en C/C++ très portable (CPU, GPU NVIDIA/AMD, Apple Metal), référence du local. **GGUF** : son format de fichier, qui contient **poids quantizés + tokenizer + métadonnées** en un seul fichier, avec de nombreux niveaux de quantization (Q4_K_M, Q5_K_M, Q8_0…) ([[68-quantization|quantization]]).

---

Quel outil pour servir un LLM en local : développeur seul, Mac, interface graphique, équipe ?
?
<!--anki:3462633762323030326236333435653361303765663234343061626430623137-->
- **Développeur seul** : **Ollama** (gestion des modèles et API locale, au-dessus de llama.cpp), ou directement le serveur **llama.cpp**, compatible OpenAI
- **Mac Apple Silicon** : **MLX**, optimisé pour la mémoire unifiée
- **Interface graphique** : **LM Studio**
- **Équipe, utilisateurs simultanés** : **vLLM** ou **SGLang** sur un serveur GPU on-prem ([[11-serveurs-inference-llm|serveurs d'inférence]])

---

Ollama ou vLLM en entreprise ?
?
<!--anki:45635b4b45313f3a3278-->
- **Ollama / llama.cpp** : un utilisateur ou quelques-uns, poste de développement, prototypage, matériel hétérogène.
- **vLLM / SGLang** : **beaucoup d'utilisateurs simultanés** grâce au continuous batching et au PagedAttention — débit total très supérieur sur GPU.

Erreur fréquente : mettre Ollama en production pour une équipe entière et constater l'**effondrement** du débit.

---

Pourquoi les Mac Apple Silicon sont-ils populaires pour les LLM locaux ?
?
<!--anki:797c71366d393945402f-->
La **mémoire unifiée** partagée CPU/GPU permet de charger des modèles de **plusieurs dizaines à centaines de Go** sur une seule machine, avec une bande passante élevée. Le **débit** reste inférieur à un GPU serveur, et le **prefill** (long prompt) est lent, mais c'est une solution compacte pour le développement et les petits déploiements.

---

Quels modèles viser pour l'edge ?
?
<!--anki:79514e2a284664622c76-->
Les **small language models** (≈ 1 à 8 B paramètres), souvent **distillés** de plus gros, en **quantization 4 bits**. Ils sont bons en tâches **ciblées** (classification, extraction, reformulation, autocomplétion) mais faibles en connaissances générales et en raisonnement long. Un **fine-tuning** ou une distillation sur la tâche compense beaucoup ([[53-donnees-synthetiques-distillation|distillation]]).

---

Qu'est-ce qu'une architecture hybride local / cloud ?
?
<!--anki:6c64257577297726536d-->
Traiter **localement** ce qui est simple, fréquent ou sensible (PII, classification, pré-filtrage), et **escalader vers le cloud** les requêtes difficiles, après **pseudonymisation** si nécessaire. Le routeur décide selon la **difficulté**, la **sensibilité** et la **connectivité** ([[82-routing-llm|routing]]).

---

Quels défis d'exploitation d'une flotte de modèles locaux ?
?
<!--anki:255a2e4b704c7e2b6a-->
- **Distribution et mise à jour** des modèles (plusieurs Go) sur de nombreux appareils.
- **Hétérogénéité** matérielle → plusieurs variantes quantizées.
- **Observabilité** limitée (pas de logs centralisés par défaut).
- **Sécurité** : les poids sont **extractibles** de l'appareil, et le modèle local reste exposé à la prompt injection.
- **Evals** à refaire pour chaque quantization.

---

Quand le on-prem GPU devient-il rentable par rapport aux API ?
?
<!--anki:63522c7c41676e3e78-->
Quand l'**utilisation** des GPU est **élevée et régulière**, que le modèle open weights atteint la **qualité** requise, et que l'équipe sait l'**exploiter**. Le calcul doit inclure matériel, énergie, hébergement, ingénieurs, et le **taux d'occupation** réel — un GPU inoccupé la nuit coûte autant ([[121-couts-inference|break-even API vs self-host]]).

---

À ne pas confondre : capacité mémoire et bande passante mémoire ?
?
<!--anki:782f576c373a7e467939-->
- **Capacité** (Go) : décide **si le modèle tient**. Poids + KV cache doivent entrer en VRAM ou en RAM unifiée
- **Bande passante** (Go/s) : décide **à quelle vitesse il génère**. Chaque token relit tous les poids actifs

Un Mac avec 128 Go de RAM unifiée charge un 70B en 4 bits, mais le génère plus lentement qu'un GPU de 24 Go ne génère un 8B. Pour comparer deux machines, regarder les **deux** chiffres ([[68-quantization|quantization]]).

---

Calcul : quelle vitesse de génération pour un 8B en Q4_K_M sur un Mac à 400 Go/s de bande passante mémoire ?
?
<!--anki:6662653665313639616561363434653162323664663362306565646566613361-->
Le decode relit tous les poids à chaque token ([[69-roofline-prefill-decode|roofline]]) :
```text
poids 8B en Q4_K_M : 8e9 × 4,8 bits / 8 ≈ 4,8 Go
plafond            : 400 / 4,8          ≈ 83 tokens/s → 50 à 60 en pratique
70B en Q4_K_M      : ≈ 42 Go            → plafond ≈ 9,5 tokens/s
```
Sur un poste local, c'est la **bande passante mémoire**, pas la puissance de calcul, qui fixe la vitesse : un 70B reste utilisable, mais lent.

---

## Mises en situation

Mise en situation : une équipe a mis Ollama en production pour 50 utilisateurs et se plaint que « les modèles locaux sont lents ». Que diagnostiques-tu ?
?
<!--anki:43257c3f2b6670734c3b-->
1. **Mauvais outil pour l'usage** : llama.cpp et Ollama traitent peu de requêtes simultanées
2. **Passer à un serveur d'inférence** : vLLM ou SGLang, avec continuous batching et PagedAttention ([[11-serveurs-inference-llm|serveurs]])
3. **Vérifier le matériel** : le débit dépend surtout de la **bande passante mémoire**, pas seulement du nombre de cœurs
4. **Dimensionner** : mesurer le débit réel à la concurrence cible avant de conclure ([[64-metriques-slo-inference|SLO]])
5. **Garder Ollama** pour ce qu'il fait bien : postes de développement et prototypage

**Piège** : conclure que l'auto-hébergement ne fonctionne pas, alors que c'est le serveur qui n'est pas adapté.

---

Mise en situation : un client industriel veut un assistant qui fonctionne sans Internet, sur des postes d'atelier. Comment conçois-tu la solution ?
?
<!--anki:5073454f71744f5d4025-->
1. **Cadrer la tâche** : un petit modèle (1 à 8 milliards de paramètres) réussit bien une tâche **ciblée**, pas une culture générale
2. **Quantizer en 4 bits** et vérifier que le modèle tient dans la mémoire des postes ([[68-quantization|quantization]])
3. **Spécialiser** : fine-tuning ou distillation sur la tâche, pour compenser la taille ([[53-donnees-synthetiques-distillation|distillation]])
4. **Prévoir l'exploitation** : distribution et mise à jour de plusieurs gigaoctets, variantes selon le matériel, evals refaites par variante
5. **Sécurité** : les poids sont extractibles du poste, et l'injection de prompt reste possible

**Piège** : promettre les capacités d'un grand modèle cloud sur un appareil qui n'en a ni la mémoire ni la bande passante.

---

## Sources

- [llama.cpp — formats, quantification et inférence locale](https://github.com/ggml-org/llama.cpp)
- [vLLM — quantification et matériels compatibles](https://docs.vllm.ai/en/latest/features/quantization/)

## Connexions
- [[68-quantization|Quantization]] — faire tenir le modèle
- [[11-serveurs-inference-llm|Serveurs d'inférence LLM]] — vLLM, llama.cpp, Ollama
- [[10-images-modeles-poids|Images & poids de modèles]] — GGUF et distribution
- [[146-choix-modeles|Choix de modèle]] — open weights vs API
- [[121-couts-inference|Coûts d'inférence]] — break-even
- [[53-donnees-synthetiques-distillation|Distillation]] — petits modèles spécialisés
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection, exfiltration et guardrails
- [[61-kv-cache-attention|KV cache]] — la mémoire qui limite la concurrence
- [[00-moc-ai-engineering|MOC AI Engineering]]
