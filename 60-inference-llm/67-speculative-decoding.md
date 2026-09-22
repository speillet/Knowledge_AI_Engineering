# Speculative decoding — Flashcards
Tags: #flashcards #ai-engineering #inference #speculative-decoding #llm

Quel est le principe du speculative decoding ?
?
Un **brouillon rapide** propose k tokens d'avance, puis le **grand modèle (cible) les vérifie tous en une seule passe**. On garde le plus long début accepté, plus un token produit par la cible elle-même : **au moins un token par passe**, souvent plusieurs.
```text
brouillon : propose t1 t2 t3 t4
cible     : vérifie les 4 en parallèle → accepte t1 t2, corrige t3 → 3 tokens en une passe
```

---

Pourquoi vérifier k tokens coûte-t-il presque autant que d'en générer un ?
?
Parce que le **decode est limité par la bande passante mémoire** : à chaque pas, on relit tous les poids du modèle pour un seul token et le GPU calcule peu. Vérifier k tokens en une passe relit les poids **une seule fois**, comme un petit prefill : le calcul supplémentaire est presque gratuit ([[62-optimisations-inference|optimisations d'inférence]]).

---

Comment décide-t-on d'accepter un token proposé ?
?
- **Greedy** : accepté s'il est égal au token le plus probable de la cible
- **Sampling** (speculative sampling) : accepté avec la probabilité **min(1, p(x) / q(x))**, où p est la probabilité selon la cible et q selon le brouillon. En cas de rejet, on retire un token dans la distribution corrigée **max(0, p − q)** renormalisée

Cette règle garantit que la sortie suit **exactement la distribution de la cible** ([[65-probabilites-sampling|probabilités & sampling]]).

---

Le speculative decoding dégrade-t-il la qualité ?
?
**Non, en théorie** : il est sans perte, la sortie suit la même distribution que la cible seule (identique en greedy). En pratique, de petits écarts restent possibles à cause de la **précision flottante** et des variations de batch, comme pour toute inférence ([[114-reproductibilite-variance|reproductibilité]]).

---

De quoi dépend le gain de vitesse ?
?
Du **taux d'acceptation** α (probabilité qu'un token proposé soit accepté) et du nombre k de tokens proposés. Nombre moyen de tokens produits par passe de la cible :
```text
E = (1 − α^(k+1)) / (1 − α)      ex. α = 0,8 et k = 4 → ≈ 3,4 tokens par passe
```
Le gain réel est plus faible, car il faut retrancher le coût du brouillon : typiquement **×2 à ×3** sur la vitesse de génération.

---

Comment choisir le nombre de tokens proposés (k) ?
?
Trop **grand** : on gaspille du travail de brouillon, car un rejet précoce jette toute la suite. Trop **petit** : peu de gain. On règle k selon le taux d'acceptation mesuré (souvent **3 à 5**), ou on laisse le moteur l'**adapter dynamiquement**.

---

Quelles sont les façons de produire le brouillon ?
?
- **Petit modèle de la même famille**, avec le même tokenizer (ex. un 1B pour un 70B)
- **N-grammes / prompt lookup** : recopier des passages du prompt, sans aucun modèle
- **Têtes de décodage** ajoutées à la cible : **Medusa**, **EAGLE** (qui prédit à partir des états internes de la cible)
- **MTP** (multi-token prediction) : des modules entraînés avec le modèle pour prédire plusieurs tokens (ex. DeepSeek-V3)
- **Suffix decoding** : réutiliser des séquences déjà générées, efficace sur les workloads d'agents répétitifs

---

Quand le prompt lookup (n-grammes) est-il efficace ?
?
Quand la sortie **recopie beaucoup l'entrée** : RAG avec citations, résumé, extraction, **édition de code** (le fichier modifié reprend l'original). Il n'y a ni modèle ni VRAM supplémentaires, mais le gain est faible sur du texte vraiment nouveau.

---

Qu'est-ce que la vérification en arbre ?
?
Au lieu d'une seule suite de tokens, le brouillon propose **plusieurs continuations possibles organisées en arbre**, que la cible vérifie **en une passe** grâce à un masque d'attention en arbre. On augmente ainsi la longueur acceptée : c'est ce qu'utilisent Medusa et EAGLE.

---

Quand le speculative decoding aide-t-il et quand nuit-il ?
?
- **Aide** : petits batchs et services sensibles à la latence, où le GPU attend la mémoire ; texte prévisible (code, JSON, recopie) ; température basse
- **Nuit** : **gros batchs** où le GPU est déjà saturé en calcul (la vérification consomme ce calcul et fait baisser le débit total) ; température élevée ou texte très créatif (faible acceptation)

---

Quelles métriques d'inférence améliore-t-il ?
?
Le **TPOT** (temps par token généré) et donc la **latence totale** des réponses longues. Pas le **TTFT** : le prefill n'est pas accéléré, et le brouillon ajoute même un peu de travail au départ ([[64-metriques-slo-inference|métriques & SLO]]).

---

Comment l'activer dans un serveur d'inférence ?
?
Les principaux moteurs le supportent : vLLM, SGLang, TensorRT-LLM, llama.cpp. Dans vLLM :
```bash
vllm serve <modèle-cible> --speculative-config '{
  "method": "ngram", "num_speculative_tokens": 4,
  "prompt_lookup_min": 2, "prompt_lookup_max": 5 }'
```
Autres valeurs de `method` : `draft_model`, `eagle3`, `mtp`, `suffix`…

---

Quels coûts et quelles contraintes faut-il prévoir ?
?
- **VRAM** pour le brouillon et son propre KV cache (sauf n-grammes)
- **Tokenizer compatible** entre brouillon et cible
- Têtes EAGLE ou Medusa **à entraîner** pour chaque modèle cible, ou à trouver toutes faites
- **Réglages à mesurer** : taux d'acceptation, longueur acceptée moyenne et TPOT, sur le trafic réel

---

Quelles métriques suivre pour le speculative decoding ?
?
- **Taux d'acceptation** = tokens acceptés ÷ tokens proposés
- **Longueur acceptée moyenne** = 1 + tokens acceptés ÷ nombre de passes de vérification : le nombre de tokens produits par passe de la cible
- **Acceptation par position** : si elle s'effondre après 2 tokens, k est trop grand
- **TPOT et débit** comparés à un déploiement sans speculative decoding

Dans vLLM : `vllm:spec_decode_num_draft_tokens_total`, `vllm:spec_decode_num_accepted_tokens_total`, `vllm:spec_decode_num_drafts_total`. On segmente par type de trafic, car l'acceptation varie beaucoup entre code, chat et texte créatif.

---

Comment valider un déploiement avec speculative decoding ?
?
1. **Exactitude** : en greedy, les sorties doivent être **identiques** à celles de la cible seule sur un jeu de prompts (aux écarts numériques près) ; en sampling, les evals ne doivent pas bouger
2. **Gain** : benchmark de charge à **plusieurs niveaux de concurrence**. Le TPOT doit baisser à faible charge, et le débit ne doit pas s'effondrer au pic
3. **Réglage** : ajuster k, ou désactiver la technique au-delà d'une certaine taille de batch, selon ces mesures ([[93-monitoring-inference|monitoring de l'inférence]])

---

## Connexions
- [[62-optimisations-inference|Optimisations d'inférence]] — prefill, decode et bande passante mémoire
- [[65-probabilites-sampling|Probabilités & sampling]] — pourquoi la distribution est préservée
- [[64-metriques-slo-inference|Métriques & SLO]] — l'effet sur TPOT et TTFT
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM
- [[114-reproductibilite-variance|Reproductibilité & variance]] — les écarts numériques
- [[68-quantization|Quantization]] — l'autre levier pour accélérer le decode
- [[93-monitoring-inference|Monitoring de l'inférence]] — suivre l'acceptation en production
- [[00-moc-ai-engineering|MOC AI Engineering]]
