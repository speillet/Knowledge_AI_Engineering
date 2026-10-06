# Coûts d'inférence — Flashcards
Tags: #flashcards #ai-engineering #finops #couts #inference #llm
<!-- summary: structure du coût d'un appel, calcul du coût d'un agent de 20 tours avec et sans cache, prix input et output, prompt caching, coût du self-hosting, break-even API ou self-host, batch API, leviers techniques, contexte long, unit economics, GPU idle. -->


Comment se structure le coût d'un appel LLM API ? <!--anki:4f444670265626663e6d-->
?
**Prix par million de tokens**, différencié **input / output** (l'output est plus cher), avec surcoûts éventuels (raisonnement, contexte long).
```text
coût = (tokens_in × prix_in + tokens_out × prix_out) / 1 000 000

Exemple (prix illustratifs : 3 €/M en entrée, 15 €/M en sortie)
  3 000 tokens d'entrée + 500 de sortie
  = (3 000 × 3 + 500 × 15) / 1e6 = 0,009 + 0,0075 ≈ 0,017 €/requête
  × 1 million de requêtes par mois ≈ 17 000 €
```
Deux enseignements : l'**entrée domine** dès qu'on envoie du contexte, et un calcul au dos d'une enveloppe suffit à cadrer un projet ([[141-system-design-llm|system design]]).

---

À ne pas confondre : prix par token et coût par tâche réussie ? <!--anki:44393742637863294c-->
?
- **Prix par token** : ce qu'affiche le fournisseur. Facile à comparer, mais trompeur
- **Coût par tâche réussie** : ce que vous payez réellement, en incluant les **tokens réels** (tokenizer, verbosité, raisonnement), les **reprises**, les **escalades** et la **vérification humaine**

Un modèle 30 % moins cher par token qui échoue deux fois plus souvent coûte **plus cher** ([[146-choix-modeles|choix de modèle]]).

---

Pourquoi les tokens d'output coûtent-ils plus cher que l'input ? <!--anki:62606640475e324b5f71-->
?
Parce que le **decode est séquentiel** (un passage du modèle par token généré), alors que le **prefill traite tout le prompt en parallèle** ([[69-roofline-prefill-decode|prefill et decode]]). Un token de sortie mobilise donc bien plus de temps GPU.

Repère : la sortie coûte souvent **3 à 5 fois** plus cher que l'entrée. Limiter la verbosité (`max_tokens`, format concis) est l'un des leviers les plus directs.

---

Quel effet du prompt caching sur la facture ? <!--anki:796c756e764b716c6232-->
?
Les **tokens de préfixe déjà en cache sont facturés à prix réduit** : gros gains sur les system prompts et définitions d'outils répétés ([[35-context-engineering|prompt caching]]).

Le gain réel dépend du taux de réutilisation, des tokens admissibles, du TTL et d'un éventuel prix d'écriture. La sortie reste généralement facturée comme une nouvelle génération. Mesurer les champs d'usage et la facture : un préfixe répété ne garantit pas un hit, et un cache peu relu peut ne pas être rentable.

---

Comment se calcule le coût du self-hosting ? <!--anki:455d7b3a6f6040737e3c-->
?
Utiliser des **unités cohérentes** :
```text
coût/token = coût total par heure / tokens utiles par heure
          = coût horaire / (débit moyen en tokens/s × 3 600)
Exemple fictif : 3,60 €/h et 100 tokens/s → 0,00001 €/token
```
Inclure GPU, CPU, stockage, réseau, exploitation et périodes d'inactivité. Le débit retenu doit correspondre à la charge réelle et aux [[64-metriques-slo-inference|SLO]], pas au pic théorique. Comparer ensuite le coût par tâche réussie, car un token peu cher ne garantit pas une réponse utile.

---

API ou self-host : où est le break-even ? <!--anki:4f5871495e2e6540443a-->
?
- **Self-host** rentable à **fort volume constant** et forte utilisation GPU
- **API** gagne à faible volume ou charge irrégulière (pas de GPU idle, scale-to-zero implicite)

Comparer à qualité, latence et disponibilité équivalentes, avec coût d'exploitation et capacité de secours inclus. Les pointes imposent parfois de payer une réserve inutilisée le reste du temps. Le seuil se calcule sur le profil de charge et les tarifs réels ; un modèle hybride peut absorber la base localement et les pointes par API.

---

Qu'est-ce qu'une batch API ? <!--anki:434167563b555a475567-->
?
Une **batch API** accepte un lot de requêtes pour un traitement asynchrone, avec une fenêtre de traitement, des quotas et des tarifs propres au fournisseur. Elle convient aux evals, extractions et enrichissements qui supportent un délai.

Une remise de 50 % et une fenêtre de 24 heures sont des exemples d'offre, **pas une garantie universelle de réussite de chaque ligne**. Certaines requêtes échouent ou expirent. Associer un identifiant à chaque entrée, récupérer les statuts et reprendre seulement les lignes nécessaires ([[148-pipelines-batch-llm|pipelines batch]]).

---

Quels leviers techniques réduisent le coût d'inférence d'un LLM ? <!--anki:4a616c7c46297d3f3e52-->
?
- **[[82-routing-llm|Routing]]** vers un modèle moins cher pour les requêtes simples
- **Prompt caching** du préfixe stable ([[123-caching-agressif|caching]])
- **Prompts plus courts** et contexte trié, `max_tokens` limité
- **Batch API** pour le non-interactif
- En auto-hébergé : **[[68-quantization|quantization]]** et GPU bien remplis

Toujours mesurer l'effet sur la qualité : une économie qui fait chuter le taux de réussite augmente le **coût par tâche réussie**.

---

Que coûte réellement le contexte long ? <!--anki:70715578642e522529-->
?
Chaque token de contexte coûte **trois fois** : en argent (facturation), en latence (prefill) et en VRAM ([[61-kv-cache-attention|KV cache]]) — trier son contexte, c'est économiser.

Ces trois dimensions ne se traduisent pas forcément par trois lignes de facture : la VRAM est surtout un coût de capacité en self-hosting. Le cache peut réduire une partie du prefill et du prix d'entrée, mais le contexte reste à gérer lors du décodage. Supprimer le bruit aide ; retirer une preuve nécessaire dégrade le résultat.

---

Qu'est-ce que les unit economics d'une feature LLM ? <!--anki:7135367b5678255e2b5b-->
?
Le **coût par requête / utilisateur / feature rapporté à la valeur produite** — la métrique qui décide si une feature IA est viable.

Par exemple, rapporter le coût total d'un dossier traité au temps effectivement économisé ou à la marge générée. Inclure retries, échecs, vérification humaine et outils externes. Une moyenne par requête peut masquer un petit nombre de tâches très coûteuses ; segmenter par usage et suivre aussi les percentiles.

---

Pourquoi un GPU inutilisé coûte-t-il autant qu'un GPU actif ? <!--anki:692b24734c473647792f-->
?
Un GPU **alloué est facturé pareil, utilisé ou non** : à 20 % d'utilisation, chaque token coûte en réalité cinq fois plus cher qu'à pleine charge.

Leviers : **consolider** les modèles, partager le GPU (**MIG**, time-slicing), **autoscaling** sur la charge réelle et **scale-to-zero** pour les modèles peu utilisés, au prix d'un démarrage à froid ([[12-kubernetes-gpu-inference|K8s GPU]]).

---

Calcul : combien coûte une tâche d'agent de 20 tours, avec et sans prompt caching ? <!--anki:43757a68396e6c7c3d49-->
?
Hypothèses : 5 000 tokens au départ, +2 000 par tour (résultats d'outils), 300 tokens de sortie par tour, 3 €/M en entrée, 15 €/M en sortie.
```text
entrée cumulée = 20 × 5 000 + 2 000 × (0 + 1 + … + 19) = 480 000 tokens
sans cache : 480 k × 3 €/M + 6 k × 15 €/M     ≈ 1,53 €
avec cache : ~43 k nouveaux tokens au plein tarif
             + ~437 k relus à 10 % du prix     ≈ 0,35 €
```
Le coût croît comme le **carré** du nombre de tours : 40 tours coûtent environ 3,5 fois plus que 20. D'où la **compaction** et le cache ([[123-caching-agressif|caching]]). Le surcoût d'écriture en cache est négligé ici.

---

Calcul : combien coûte par mois un assistant interne utilisé par 2 000 personnes ? <!--anki:6165653035666139373336363437383461383262393763386636316462633865-->
?
Hypothèses : 10 requêtes par personne et par jour ouvré, 22 jours, 2 000 tokens d'entrée et 400 de sortie par requête, 3 €/M en entrée, 15 €/M en sortie.
```text
requêtes : 2 000 × 10 × 22                       = 440 000 par mois
entrée   : 440 k × 2 000 = 880 M tokens × 3 €/M  ≈ 2 640 €
sortie   : 440 k ×   400 = 176 M tokens × 15 €/M ≈ 2 640 €
total                                            ≈ 5 300 € par mois, ≈ 2,60 € par personne
```
Entrée et sortie pèsent autant, car la sortie coûte 5 fois plus cher au token. Un RAG qui porte l'entrée à 8 000 tokens par requête multiplierait la part d'entrée par 4 ([[122-finops-llm|FinOps]]).

---

Calcul : à partir de quel volume un GPU loué devient-il moins cher qu'une API ? <!--anki:3165666632316363393062643430633161363538303761346166313231356365-->
?
Hypothèses : un H100 loué 2,50 €/h, qui sert un petit modèle open weights ; une API équivalente à 0,20 € par million de tokens, entrée et sortie confondues.
```text
GPU 24 h/24 : 2,50 € × 720 h            = 1 800 € par mois
break-even  : 1 800 € / 0,20 €/M        = 9 000 M tokens par mois
soit        : 9e9 / (30 × 86 400 s)     ≈ 3 500 tokens/s, en continu
```
Il faut une charge **soutenue jour et nuit** pour battre une API bon marché ; à 20 % d'utilisation, l'API reste gagnante. Et ce calcul oublie l'exploitation : ingénieurs, supervision, mises à jour ([[164-llm-local-edge|on-prem]]).

---

## Mises en situation

Mise en situation : ta direction demande s'il faut passer de l'API à des modèles auto-hébergés pour économiser. Comment calcules-tu ? <!--anki:625447595134405e4423-->
?
1. **Mesurer le volume réel** : tokens d'entrée et de sortie par mois, profil horaire, pics
2. **Coût API** : prix par million de tokens, en tenant compte des tokens lus en cache et des traitements différés
3. **Coût self-host** : coût GPU horaire amorti ÷ débit réel obtenu sur ta charge, plus l'exploitation (astreinte, mises à jour)
4. **Comparer au bon endroit** : le self-host gagne à **fort volume constant** et forte utilisation, l'API à volume faible ou irrégulier
5. **Ne pas oublier la qualité** : un modèle auto-hébergé moins bon peut coûter plus cher en reprises ([[146-choix-modeles|choix de modèle]])

**Piège** : comparer un prix GPU horaire à un prix par token sans mesurer le débit réel.

---

Mise en situation : le coût de ton assistant est dominé par les tokens d'entrée, à cause d'un long contexte envoyé à chaque tour. Quels leviers, dans quel ordre ? <!--anki:6950405a5263647b3734-->
?
1. **Prompt caching** : un préfixe stable rend la majeure partie de l'entrée bien moins chère ([[123-caching-agressif|caching]])
2. **Trier le contexte** : moins de documents récupérés, compaction de l'historique ([[35-context-engineering|context engineering]])
3. **Router** les requêtes simples vers un modèle moins cher ([[82-routing-llm|routing]])
4. **Limiter la sortie** : `max_tokens` adapté, réponses concises, puisque l'output coûte plus cher
5. **Traitement différé** pour tout ce qui n'est pas interactif (evals, enrichissement)

**Piège** : commencer par changer de modèle, alors que le contexte envoyé est le vrai poste de coût.

---

## Sources

- [Anthropic — traitement batch, échecs et expiration des requêtes](https://platform.claude.com/docs/en/build-with-claude/batch-processing)

## Connexions
- [[122-finops-llm|FinOps LLM]] — la gouvernance de ces coûts
- [[64-metriques-slo-inference|Métriques & SLO]] — goodput ↔ coût par token
- [[62-optimisations-inference|Optimisations d'inférence]] — les leviers techniques
- [[35-context-engineering|Context engineering]] — le coût du contexte
- [[82-routing-llm|Routing LLM]] — payer le juste modèle
- [[123-caching-agressif|Caching agressif]] — maximiser le taux de hit
- [[68-quantization|Quantization]] — moins de GPU par réplica
- [[132-tokenisation|Tokenisation]] — coût selon la langue
- [[146-choix-modeles|Choix de modèle]] — coût par tâche réussie
- [[164-llm-local-edge|LLM locaux]] — on-prem et break-even
- [[148-pipelines-batch-llm|Pipelines batch]] — mettre la batch API en œuvre à grande échelle
- [[136-mixture-of-experts|Mixture of Experts]] — paramètres totaux et actifs
- [[138-modeles-raisonnement|Modèles de raisonnement]] — test-time compute et budget de réflexion
- [[00-moc-ai-engineering|MOC AI Engineering]]
