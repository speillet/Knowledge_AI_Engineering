# Fine-tuning & adaptation de modèles — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #llm
<!-- summary: quand adapter, SFT, PEFT, LoRA et QLoRA, ressources, RLHF, DPO, distillation, multi-LoRA, régressions, calcul de rang et d’amortissement, versions d’un adapter. -->


Qu'est-ce que le fine-tuning ? <!--anki:71447a6c7b502c78475d-->
?
**Poursuivre l'entraînement d'un modèle pré-entraîné** pour adapter ses sorties à un objectif : comportement, format, tâche ou domaine. Le SFT sur des exemples annotés et les méthodes PEFT comme LoRA sont des options fréquentes.

Le volume nécessaire dépend de la diversité des cas et du niveau initial ; quelques centaines d'exemples ne constituent pas une recette universelle. L'adaptation peut apprendre des connaissances, mais leur restitution, mise à jour et effacement ne sont pas garantis. Pour des faits changeants à citer, comparer d'abord une recherche à l'exécution comme le [[21-rag-fondamentaux|RAG]].

---

Quand fine-tuner plutôt que prompter ou faire du RAG ? <!--anki:6758606d3f2a7e395547-->
?
Quand une adaptation répétée du **comportement ou de la tâche** apporte un gain mesurable : extraction spécialisée, style attendu, distillation ou réduction du contexte requis.

Comparer au [[11-prompt-engineering-avance|prompt]] avec exemples et au [[21-rag-fondamentaux|RAG]] si la difficulté vient de l'accès aux faits. Vérifier qu'un jeu représentatif et autorisé existe, avec un test indépendant. Mesurer gains, cas rares et régressions. Pour des connaissances fréquemment mises à jour, la recherche facilite généralement actualisation et traçabilité ; cela ne rend pas les méthodes mutuellement exclusives.

---

Qu'est-ce que le SFT ? <!--anki:6759363b4a296776615b-->
?
**Supervised Fine-Tuning** : entraînement sur des paires **instruction → réponse attendue** de qualité. Le format doit être **exactement celui de l'inférence**, chat template et outils compris ([[132-tokenisation|chat template]]).
```jsonl
{"messages": [
  {"role": "system", "content": "Tu extrais les champs d'une facture en JSON."},
  {"role": "user", "content": "Facture n°A-4471 du 12/03 : 1 240,50 € TTC…"},
  {"role": "assistant", "content": "{\"numero\":\"A-4471\",\"total\":1240.50}"}
]}
```
En entraînement **assistant-only**, on masque la perte sur les consignes pour apprendre les réponses. Ce masquage dépend du collator et de la configuration : le vérifier, car certains pipelines entraînent sur toute la séquence.

---

À ne pas confondre : full fine-tuning et PEFT ? <!--anki:666d6d6977395a684642-->
?
Le **full FT** met à jour tous les poids (coûteux en GPU et stockage) ; le **PEFT** (Parameter-Efficient FT) n'entraîne qu'une **petite fraction de paramètres**.

Le full fine-tuning conserve une grande flexibilité, mais doit stocker gradients et états d'optimiseur pour tous les paramètres entraînés. Une méthode PEFT comme LoRA réduit fortement ces états et permet plusieurs adaptations d'une même base. Le modèle de base reste nécessaire à l'inférence ; le petit adapter ne constitue pas un modèle autonome.

---

Qu'est-ce que LoRA ? <!--anki:634632767854463b7c5a-->
?
**LoRA** gèle une matrice de poids `W` et apprend une correction de bas rang `ΔW = B × A`. Pour une matrice `d × k`, cela entraîne environ `r × (d + k)` paramètres au lieu de `d × k`, avec un rang `r` bien plus petit que les dimensions.

L'adapter réduit mémoire d'entraînement et stockage des variantes, mais sa taille dépend du rang et des couches ciblées : elle peut dépasser quelques dizaines de Mo. Il faut la bonne version du modèle de base pour l'utiliser.

---

Qu'est-ce que QLoRA ? <!--anki:435021656c75503d585b-->
?
**LoRA sur un modèle quantizé en 4-bit** : fine-tuner un gros modèle sur un GPU modeste. Les poids de base restent figés en 4 bits (format NF4), seuls les adapters s'entraînent en précision plus haute ([[68-quantization|NF4]]).

Pendant le calcul, les poids quantifiés sont exploités avec une précision de calcul adaptée ; « 4 bits » décrit leur stockage, pas toutes les opérations. Il faut encore de la mémoire pour les activations, les adapters et leur optimiseur. Le gain rend certains entraînements possibles, sans garantir qu'un contexte long ou un grand batch tienne sur le même GPU.

---

De quelles hypothèses dépendent les ressources nécessaires à un fine-tuning ? <!--anki:457b75296778564c6056-->
?
Les ressources dépendent du **modèle, de la longueur des séquences, du batch, de l'optimiseur et des couches adaptées**.
```text
Full FT : poids + gradients + états d'optimiseur + activations
LoRA    : poids gelés + petits paramètres entraînés + activations
QLoRA   : base quantifiée + adapters entraînés + activations
```
À titre d'estimation, un 7B avec un budget de 16 octets par paramètre demande **112 Go hors activations**. Des configurations QLoRA rendent de grands modèles accessibles sur un GPU, sans garantir qu'un 70B tienne avec tout contexte. Mesurer la mémoire maximale et le temps sur un petit entraînement représentatif ; la qualité des exemples reste déterminante.

---

Qu'est-ce que le RLHF ? <!--anki:794a63615d3f7835663e-->
?
**Reinforcement Learning from Human Feedback** : un reward model entraîné sur des préférences humaines guide l'optimisation (PPO) du modèle — la base de l'alignement.

Dans le schéma classique, des humains comparent des réponses, un modèle de récompense apprend ces préférences, puis la politique est optimisée sous contrainte de rester proche d'une référence. La récompense est un proxy : le modèle peut apprendre à plaire au juge sans devenir plus exact. Évaluer les effets sur utilité, factualité et comportements indésirables.

---

Qu'est-ce que DPO ? <!--anki:492f54413476366b5246-->
?
**DPO** apprend à partir de paires de réponses préférée et rejetée pour un même prompt. Son objectif ajuste leurs probabilités relatives par rapport à un modèle de référence, **sans entraîner explicitement un modèle de récompense ni lancer une boucle de RL en ligne**.

Cela simplifie l'entraînement, mais ne garantit pas une meilleure qualité ou stabilité dans tous les cas. Les préférences doivent être cohérentes et représentatives ; des paires biaisées peuvent apprendre la longueur ou le style du gagnant plutôt que la qualité recherchée.

---

Comment obtenir un petit modèle aussi bon qu'un grand sur un domaine précis ? <!--anki:4a2c42346174694d706b-->
?
La **distillation** utilise un grand modèle comme enseignant pour produire des exemples, des distributions ou des signaux de supervision destinés à un plus petit modèle. Sur une tâche étroite, l'élève peut approcher la qualité utile de l'enseignant avec une inférence moins coûteuse.

Ce résultat n'est pas garanti : sélectionner des exemples divers, vérifier les sorties de l'enseignant et tester hors du jeu d'entraînement. Mesurer les cas difficiles et les régressions générales ; les erreurs de l'enseignant peuvent être transmises à l'élève ([[53-donnees-synthetiques-distillation|distillation en détail]]).

---

Comment servir plusieurs fine-tunings à moindre coût ? <!--anki:483c356d3755387d6c25-->
?
Le **multi-LoRA** partage un modèle de base entre plusieurs adapters, sélectionnés selon la requête. Cela évite de dupliquer tous les poids pour chaque adaptation.
```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --enable-lora \
  --lora-modules support=./lora-support juridique=./lora-juridique
```
Cet exemple suppose un serveur et une architecture compatibles. Vérifier versions de base, rangs et modules ciblés, puis mesurer mémoire, chargements d'adapters et débit sous concurrence. Le nombre de clients ne suffit pas à dimensionner les GPU : adapters simultanés, séquences actives et KV cache comptent aussi.

---

Quel est le principal risque du fine-tuning ? <!--anki:4a72233936695944475e-->
?
Un risque majeur est la **régression de capacités utiles** pendant la spécialisation : suivi d'instructions, autres langues ou tâches générales. Un jeu biaisé peut aussi apprendre des erreurs sans que la loss le révèle.

Geler la base avec **LoRA** ne garantit pas l'absence de régression quand l'adapter est actif. Comparer base et adaptation sur la tâche cible et des capacités à préserver ; sélectionner taux d'apprentissage, durée et éventuel mélange de données selon ces mesures. Retirer l'adapter permet de retrouver la base, mais ne corrige pas le comportement de la version spécialisée.

---

Calcul : pour une base 7B, comparer la mémoire brute des poids en LoRA avec BF16 et en QLoRA avec 4 bits. Pourquoi ces chiffres ne donnent-ils pas la mémoire totale du fine-tuning ? <!--anki:3337376463643866363135623439663561633937613466613932353937653533-->
?
La **mémoire des poids de base** fournit seulement un point de départ, en Go décimaux :
```text
LoRA, base BF16 : 7e9 × 2 octets = 14 Go
QLoRA, stockage brut 4 bits : 7e9 × 0,5 octet = 3,5 Go
```
Ajouter métadonnées de quantification, adapters, gradients et états d'optimiseur associés, activations et buffers temporaires. Leur coût dépend du rang, des couches ciblées, de la précision, du batch et des séquences. Un GPU de 16 ou 24 Go peut convenir à certaines recettes QLoRA 7B, sans garantie générale. Mesurer le pic mémoire d'un pas représentatif avant de dimensionner.

---

Calcul : LoRA adapte une matrice de 4 096 × 4 096 avec un rang 16, sans biais ni autres paramètres entraînés. Combien de paramètres sont appris et quelle fraction de la matrice complète cela représente-t-il ? <!--anki:6362383461646433373665393461356362623838643937616435383465623236-->
?
Les deux matrices de correction contiennent `r × (d + k)` paramètres :
```text
LoRA : 16 × (4 096 + 4 096) = 131 072
matrice complète : 4 096² = 16 777 216
fraction : 131 072 / 16 777 216 = 0,0078125 ≈ 0,78 %
```
Cette réduction concerne les paramètres entraînés de **cette matrice**. Elle ne divise pas toute la mémoire ni le temps de calcul par le même facteur : base, activations et autres modules restent présents. Le rang est un choix à valider sur la tâche.

---

Que faut-il versionner pour redéployer fidèlement un adapter LoRA ? <!--anki:3161663637373437313135313434343738373861323137353861636533393538-->
?
La **révision exacte de la base**, les poids et la configuration de l'adapter, le tokenizer, le template de conversation et les paramètres de serving.

Le rang et les modules ciblés doivent correspondre à l'architecture chargée. Un nom de modèle seul ne suffit pas si ses fichiers ont changé. Conserver aussi références des données et résultats d'eval pour comprendre l'adaptation. Tester le chargement et quelques cas de non-régression dans l'environnement cible ; un adapter est un composant du système, pas un modèle autonome.

---

Calcul : une adaptation coûte 1 200 € au départ et économise 0,004 € par requête à qualité comparable, sans coût récurrent supplémentaire. À 50 000 requêtes par mois, quel volume et délai amortissent cet investissement ? <!--anki:6539343261343363333263323438643339643432396335363361366535306637-->
?
Avec les coûts fictifs et hypothèses du recto :
```text
volume d'amortissement = 1 200 / 0,004 = 300 000 requêtes
économie mensuelle = 50 000 × 0,004 = 200 €
délai = 1 200 / 200 = 6 mois
```
Ce calcul n'est valable que si qualité, volume et économie restent comparables. Ajouter réentraînements, validation, exploitation et régressions au scénario réel. Si les gains mensuels ne dépassent pas les coûts récurrents, aucun délai d'amortissement fini n'existe dans ce modèle.

---

## Mises en situation

Mise en situation : le métier veut fine-tuner un modèle « pour qu'il connaisse nos procédures internes », qui changent chaque mois. Que réponds-tu ? <!--anki:6e332d72382e3d3f492e-->
?
1. **Séparer connaissances et comportement** : des procédures qui changent relèvent du **RAG**, pas du fine-tuning ([[21-rag-fondamentaux|RAG]])
2. **Rappeler le coût du cycle** : chaque mise à jour demanderait un nouvel entraînement, de nouvelles evals et un redéploiement
3. **Ce que le fine-tuning apporterait vraiment** : un format de réponse constant, un ton, une tâche répétitive, des prompts plus courts
4. **Proposer une étape intermédiaire** : prompt soigné plus RAG, mesuré sur un golden dataset
5. **Garder la porte ouverte** : si le format reste instable après optimisation, un fine-tuning léger (LoRA) se justifie

**Piège** : fine-tuner sur des documents internes et croire que le modèle « saura » les citer correctement.

---

Mise en situation : ton modèle fine-tuné est excellent sur l'extraction visée, mais les utilisateurs signalent qu'il répond n'importe quoi aux questions générales. Que s'est-il passé ? <!--anki:6961533e313a76446060-->
?
1. **Reproduire les erreurs** sur les mêmes cas avec la base et la version adaptée.
2. **Vérifier la chaîne** : tokenizer, template, configuration de génération et adapter chargé.
3. **Mesurer les régressions** hors tâche et les biais des données, avant de conclure à un oubli de capacités.
4. **Comparer des adaptations** moins agressives et un mélange de données générales ; LoRA seul ne garantit rien.
5. **Limiter le périmètre** ou router vers une base validée, puis réévaluer l'ensemble.

**Piège** : attribuer toute régression à l'entraînement sans vérifier le modèle effectivement servi.

---

## Sources

- [vLLM — serving multi-LoRA et contraintes de configuration](https://docs.vllm.ai/en/stable/features/lora/)

- [Hu et al. — LoRA et paramètres de bas rang](https://arxiv.org/abs/2106.09685)
- [Hugging Face TRL — masquage, troncature et SFT](https://huggingface.co/docs/trl/sft_trainer)
- [Hugging Face PEFT — configuration et chargement LoRA](https://huggingface.co/docs/peft/package_reference/lora)

## Connexions
- [[21-rag-fondamentaux|RAG]] — connaissances vs comportement
- [[11-prompt-engineering-avance|Prompt engineering]] — l'alternative légère
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — multi-LoRA en serving
- [[62-optimisations-inference|Optimisations]] — quantization (QLoRA)
- [[92-chainforge-evals-prompts|Evals]] — mesurer avant/après
- [[113-monitoring-drift-feedback|Monitoring & drift]] — quand ré-entraîner
- [[68-quantization|Quantization]] — NF4 et les formats de serving
- [[52-post-training-alignement|Post-training & alignement]] — RLHF, DPO, GRPO en détail
- [[53-donnees-synthetiques-distillation|Données synthétiques & distillation]] — générer et distiller
- [[54-entrainement-distribue|Entraînement distribué]] — FSDP, ZeRO, parallélismes
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps]] — cycle de vie et versioning des systèmes LLM
- [[114-reproductibilite-variance|Reproductibilité & variance]] — non-déterminisme et statistiques d'evals
- [[151-donnees-curation-annotation|Curation & annotation]] — données de qualité et jeux séparés
- [[55-rl-agentique|RL agentique]] — entraîner un modèle sur des tâches d'agent
- [[66-prefix-caching-radix-attention|Prefix caching]] — réutiliser le calcul des préfixes communs
- [[56-optimisation-diagnostic-entrainement|Optimisation & diagnostic d'entraînement]] — diagnostiquer une adaptation avant de la complexifier
- [[00-moc-ai-engineering|MOC AI Engineering]]
