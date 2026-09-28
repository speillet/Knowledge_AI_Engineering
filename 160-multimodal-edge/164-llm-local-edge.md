# LLM locaux, on-prem & edge — Flashcards
Tags: #flashcards #ai-engineering #edge #local #self-hosting #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Pourquoi faire tourner un LLM en local ou sur site ?
?
- **Confidentialité / souveraineté** : les données ne sortent pas.
- **Hors ligne** ou réseau contraint (usine, terrain, embarqué).
- **Latence** sans aller-retour réseau.
- **Coût** marginal nul à fort volume sur du matériel déjà payé.
- **Contrôle** : version figée, pas de dépréciation imposée.

---

Quel est le facteur limitant sur un poste ou un appareil ?
?
La **mémoire** (VRAM, RAM unifiée) et sa **bande passante**. Le décodage lit **tous les poids actifs à chaque token** : débit ≈ bande passante mémoire / taille des poids. Un modèle de 8 B en 4 bits (~5 Go) sur 100 Go/s de bande passante donne au mieux ~**20 tokens/s**.

---

Qu'est-ce que llama.cpp et le format GGUF ?
?
**llama.cpp** : moteur d'inférence en C/C++ très portable (CPU, GPU NVIDIA/AMD, Apple Metal), référence du local. **GGUF** : son format de fichier, qui contient **poids quantizés + tokenizer + métadonnées** en un seul fichier, avec de nombreux niveaux de quantization (Q4_K_M, Q5_K_M, Q8_0…) ([[68-quantization|quantization]]).

---

Quels outils pour servir un modèle local ?
?
- **Ollama** : gestion simple des modèles et API locale (au-dessus de llama.cpp).
- **LM Studio** : interface graphique.
- **llama.cpp server** : API compatible OpenAI.
- **MLX** (Apple Silicon) : framework optimisé pour la mémoire unifiée des Mac.
- **vLLM / SGLang** sur un serveur GPU on-prem pour le **multi-utilisateur** ([[11-serveurs-inference-llm|serveurs d'inférence]]).

---

Ollama ou vLLM en entreprise ?
?
- **Ollama / llama.cpp** : un utilisateur ou quelques-uns, poste de développement, prototypage, matériel hétérogène.
- **vLLM / SGLang** : **beaucoup d'utilisateurs simultanés** grâce au continuous batching et au PagedAttention — débit total très supérieur sur GPU.

Erreur fréquente : mettre Ollama en production pour une équipe entière et constater l'**effondrement** du débit.

---

Pourquoi les Mac Apple Silicon sont-ils populaires pour les LLM locaux ?
?
La **mémoire unifiée** partagée CPU/GPU permet de charger des modèles de **plusieurs dizaines à centaines de Go** sur une seule machine, avec une bande passante élevée. Le **débit** reste inférieur à un GPU serveur, et le **prefill** (long prompt) est lent, mais c'est une solution compacte pour le développement et les petits déploiements.

---

Quels modèles viser pour l'edge ?
?
Les **small language models** (≈ 1 à 8 B paramètres), souvent **distillés** de plus gros, en **quantization 4 bits**. Ils sont bons en tâches **ciblées** (classification, extraction, reformulation, autocomplétion) mais faibles en connaissances générales et en raisonnement long. Un **fine-tuning** ou une distillation sur la tâche compense beaucoup ([[53-donnees-synthetiques-distillation|distillation]]).

---

Qu'est-ce qu'une architecture hybride local / cloud ?
?
Traiter **localement** ce qui est simple, fréquent ou sensible (PII, classification, pré-filtrage), et **escalader vers le cloud** les requêtes difficiles, après **pseudonymisation** si nécessaire. Le routeur décide selon la **difficulté**, la **sensibilité** et la **connectivité** ([[82-routing-llm|routing]]).

---

Quels défis d'exploitation d'une flotte de modèles locaux ?
?
- **Distribution et mise à jour** des modèles (plusieurs Go) sur de nombreux appareils.
- **Hétérogénéité** matérielle → plusieurs variantes quantizées.
- **Observabilité** limitée (pas de logs centralisés par défaut).
- **Sécurité** : les poids sont **extractibles** de l'appareil, et le modèle local reste exposé à la prompt injection.
- **Evals** à refaire pour chaque quantization.

---

Quand le on-prem GPU devient-il rentable par rapport aux API ?
?
Quand l'**utilisation** des GPU est **élevée et régulière**, que le modèle open weights atteint la **qualité** requise, et que l'équipe sait l'**exploiter**. Le calcul doit inclure matériel, énergie, hébergement, ingénieurs, et le **taux d'occupation** réel — un GPU inoccupé la nuit coûte autant ([[121-couts-inference|break-even API vs self-host]]).

---

## Mises en situation

Mise en situation : une équipe a mis Ollama en production pour 50 utilisateurs et se plaint que « les modèles locaux sont lents ». Que diagnostiques-tu ?
?
1. **Mauvais outil pour l'usage** : llama.cpp et Ollama traitent peu de requêtes simultanées
2. **Passer à un serveur d'inférence** : vLLM ou SGLang, avec continuous batching et PagedAttention ([[11-serveurs-inference-llm|serveurs]])
3. **Vérifier le matériel** : le débit dépend surtout de la **bande passante mémoire**, pas seulement du nombre de cœurs
4. **Dimensionner** : mesurer le débit réel à la concurrence cible avant de conclure ([[64-metriques-slo-inference|SLO]])
5. **Garder Ollama** pour ce qu'il fait bien : postes de développement et prototypage

**Piège** : conclure que l'auto-hébergement ne fonctionne pas, alors que c'est le serveur qui n'est pas adapté.

---

Mise en situation : un client industriel veut un assistant qui fonctionne sans Internet, sur des postes d'atelier. Comment conçois-tu la solution ?
?
1. **Cadrer la tâche** : un petit modèle (1 à 8 milliards de paramètres) réussit bien une tâche **ciblée**, pas une culture générale
2. **Quantizer en 4 bits** et vérifier que le modèle tient dans la mémoire des postes ([[68-quantization|quantization]])
3. **Spécialiser** : fine-tuning ou distillation sur la tâche, pour compenser la taille ([[53-donnees-synthetiques-distillation|distillation]])
4. **Prévoir l'exploitation** : distribution et mise à jour de plusieurs gigaoctets, variantes selon le matériel, evals refaites par variante
5. **Sécurité** : les poids sont extractibles du poste, et l'injection de prompt reste possible

**Piège** : promettre les capacités d'un grand modèle cloud sur un appareil qui n'en a ni la mémoire ni la bande passante.

---

## Connexions
- [[68-quantization|Quantization]] — faire tenir le modèle
- [[11-serveurs-inference-llm|Serveurs d'inférence LLM]] — vLLM, llama.cpp, Ollama
- [[10-images-modeles-poids|Images & poids de modèles]] — GGUF et distribution
- [[146-choix-modeles|Choix de modèle]] — open weights vs API
- [[121-couts-inference|Coûts d'inférence]] — break-even
- [[53-donnees-synthetiques-distillation|Distillation]] — petits modèles spécialisés
- [[00-moc-ai-engineering|MOC AI Engineering]]
