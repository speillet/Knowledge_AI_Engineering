# Coûts d'inférence — Flashcards
Tags: #flashcards #ai-engineering #finops #couts #inference #llm

Comment se structure le coût d'un appel LLM API ?
?
<!--anki:4f444670265626663e6d-->
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

À ne pas confondre : prix par token et coût par tâche réussie ?
?
<!--anki:44393742637863294c-->
- **Prix par token** : ce qu'affiche le fournisseur. Facile à comparer, mais trompeur
- **Coût par tâche réussie** : ce que vous payez réellement, en incluant les **tokens réels** (tokenizer, verbosité, raisonnement), les **reprises**, les **escalades** et la **vérification humaine**

Un modèle 30 % moins cher par token qui échoue deux fois plus souvent coûte **plus cher** ([[146-choix-modeles|choix de modèle]]).

---

Pourquoi les tokens d'output coûtent-ils plus cher que l'input ?
?
<!--anki:62606640475e324b5f71-->
Parce que le **decode est séquentiel** (un passage du modèle par token généré), alors que le **prefill traite tout le prompt en parallèle** ([[69-roofline-prefill-decode|prefill et decode]]). Un token de sortie mobilise donc bien plus de temps GPU.

Repère : la sortie coûte souvent **3 à 5 fois** plus cher que l'entrée. Limiter la verbosité (`max_tokens`, format concis) est l'un des leviers les plus directs.

---

Quel effet du prompt caching sur la facture ?
?
<!--anki:796c756e764b716c6232-->
Les **tokens de préfixe déjà en cache sont facturés à prix réduit** : gros gains sur les system prompts et définitions d'outils répétés ([[35-context-engineering|prompt caching]]).

---

Comment se calcule le coût du self-hosting ?
?
<!--anki:455d7b3a6f6040737e3c-->
**Coût par token = coût GPU (par heure ou amorti) ÷ débit (tokens/s)** : maximiser l'utilisation et le [[64-metriques-slo-inference|goodput]] fait mécaniquement baisser le coût unitaire.

---

API ou self-host : où est le break-even ?
?
<!--anki:4f5871495e2e6540443a-->
- **Self-host** rentable à **fort volume constant** et forte utilisation GPU
- **API** gagne à faible volume ou charge irrégulière (pas de GPU idle, scale-to-zero implicite)

---

Qu'est-ce qu'une batch API ?
?
<!--anki:434167563b555a475567-->
Un traitement **différé**, avec des résultats garantis sous **24 heures**, facturé environ **50 % moins cher** et avec des quotas séparés du trafic en ligne.

Idéal pour tout ce qui n'est pas interactif : evals massives, ingestion, enrichissement de catalogue, classification d'un historique ([[148-pipelines-batch-llm|pipelines batch]]).

---

Quels leviers techniques réduisent le coût ?
?
<!--anki:4a616c7c46297d3f3e52-->
- **[[82-routing-llm|Routing]]** vers un modèle moins cher pour les requêtes simples
- **Prompt caching** du préfixe stable ([[123-caching-agressif|caching]])
- **Prompts plus courts** et contexte trié, `max_tokens` limité
- **Batch API** pour le non-interactif
- En auto-hébergé : **[[68-quantization|quantization]]** et GPU bien remplis

Toujours mesurer l'effet sur la qualité : une économie qui fait chuter le taux de réussite augmente le **coût par tâche réussie**.

---

Que coûte réellement le contexte long ?
?
<!--anki:70715578642e522529-->
Chaque token de contexte coûte **trois fois** : en argent (facturation), en latence (prefill) et en VRAM ([[61-kv-cache-attention|KV cache]]) — trier son contexte, c'est économiser.

---

Qu'est-ce que les unit economics d'une feature LLM ?
?
<!--anki:7135367b5678255e2b5b-->
Le **coût par requête / utilisateur / feature rapporté à la valeur produite** — la métrique qui décide si une feature IA est viable.

---

Pourquoi un GPU inutilisé coûte-t-il autant qu'un GPU actif ?
?
<!--anki:692b24734c473647792f-->
Un GPU **alloué est facturé pareil, utilisé ou non** : à 20 % d'utilisation, chaque token coûte en réalité cinq fois plus cher qu'à pleine charge.

Leviers : **consolider** les modèles, partager le GPU (**MIG**, time-slicing), **autoscaling** sur la charge réelle et **scale-to-zero** pour les modèles peu utilisés, au prix d'un démarrage à froid ([[12-kubernetes-gpu-inference|K8s GPU]]).

---

Calcul : combien coûte une tâche d'agent de 20 tours, avec et sans prompt caching ?
?
<!--anki:43757a68396e6c7c3d49-->
Hypothèses : 5 000 tokens au départ, +2 000 par tour (résultats d'outils), 300 tokens de sortie par tour, 3 €/M en entrée, 15 €/M en sortie.
```text
entrée cumulée = 20 × 5 000 + 2 000 × (0 + 1 + … + 19) = 480 000 tokens
sans cache : 480 k × 3 €/M + 6 k × 15 €/M     ≈ 1,53 €
avec cache : ~43 k nouveaux tokens au plein tarif
             + ~437 k relus à 10 % du prix     ≈ 0,35 €
```
Le coût croît comme le **carré** du nombre de tours : 40 tours coûtent environ 3,5 fois plus que 20. D'où la **compaction** et le cache ([[123-caching-agressif|caching]]). Le surcoût d'écriture en cache est négligé ici.

---

## Mises en situation

Mise en situation : ta direction demande s'il faut passer de l'API à des modèles auto-hébergés pour économiser. Comment calcules-tu ?
?
<!--anki:625447595134405e4423-->
1. **Mesurer le volume réel** : tokens d'entrée et de sortie par mois, profil horaire, pics
2. **Coût API** : prix par million de tokens, en tenant compte des tokens lus en cache et des traitements différés
3. **Coût self-host** : coût GPU horaire amorti ÷ débit réel obtenu sur ta charge, plus l'exploitation (astreinte, mises à jour)
4. **Comparer au bon endroit** : le self-host gagne à **fort volume constant** et forte utilisation, l'API à volume faible ou irrégulier
5. **Ne pas oublier la qualité** : un modèle auto-hébergé moins bon peut coûter plus cher en reprises ([[146-choix-modeles|choix de modèle]])

**Piège** : comparer un prix GPU horaire à un prix par token sans mesurer le débit réel.

---

Mise en situation : le coût de ton assistant est dominé par les tokens d'entrée, à cause d'un long contexte envoyé à chaque tour. Quels leviers, dans quel ordre ?
?
<!--anki:6950405a5263647b3734-->
1. **Prompt caching** : un préfixe stable rend la majeure partie de l'entrée bien moins chère ([[123-caching-agressif|caching]])
2. **Trier le contexte** : moins de documents récupérés, compaction de l'historique ([[35-context-engineering|context engineering]])
3. **Router** les requêtes simples vers un modèle moins cher ([[82-routing-llm|routing]])
4. **Limiter la sortie** : `max_tokens` adapté, réponses concises, puisque l'output coûte plus cher
5. **Traitement différé** pour tout ce qui n'est pas interactif (evals, enrichissement)

**Piège** : commencer par changer de modèle, alors que le contexte envoyé est le vrai poste de coût.

---

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
