# Comprendre le prefill, RadixAttention et le speculative decoding

Ces trois mécanismes interviennent à des endroits différents d'une même requête. Le **prefill** calcule l'état du prompt connu. **RadixAttention** évite de recalculer des états de préfixe déjà disponibles. Le **speculative decoding** essaie de confirmer plusieurs tokens de sortie par vérification de la cible. Comprendre cette chronologie aide à choisir une optimisation et à interpréter ses limites.

Le parcours de flashcards suit cet ordre : [prefill et decode pas à pas](../60-inference-llm/60-013-prefill-decode-pas-a-pas.md), [prefix caching et RadixAttention](../60-inference-llm/66-prefix-caching-radix-attention.md), puis [speculative decoding](../60-inference-llm/67-speculative-decoding.md). Les exemples ci-dessous utilisent un Transformer causal classique ; une architecture hybride peut demander d'autres états.

## 1. Le prefill calcule les positions déjà connues

Un prompt tokenisé est une suite d'identifiants. Avant le prefill, le modèle connaît cette suite, mais pas encore ses représentations internes. À chaque couche, il calcule les projections d'attention, les interactions permises par le masque, puis les autres transformations, dont le MLP. Les poids restent fixes : il s'agit d'inférence, pas d'entraînement.

Les positions sont calculables ensemble dans une couche parce que leurs entrées sont connues. Le masque causal interdit pourtant à une position de regarder le futur. Pour quatre tokens, la troisième position peut consulter les trois premières, jamais la quatrième. La couche suivante attend les états de la précédente : « parallèle » ne signifie pas que toute la profondeur du modèle disparaît.

Les clés et valeurs utiles sont conservées par couche. La dernière position du prompt fournit les logits qui permettent de choisir le premier token de sortie. L'émission de ce token et le calcul de son état KV sont deux moments différents :

```text
prompt connu : x1 x2 x3 x4

prefill   traite x1 x2 x3 x4 → cache de 4 positions → choisit y1
decode 1  traite y1          → cache de 5 positions → choisit y2
decode 2  traite y2          → cache de 6 positions → choisit y3
```

Si l'on s'arrête après `y3`, il n'est pas nécessaire de traiter ce dernier token pour prédire un `y4` inexistant. C'est aussi pourquoi une réponse de `N` tokens, dont le premier arrive après un TTFT, comporte `N−1` intervalles jusqu'au dernier token.

À chaque étape de decode, le nouveau token traverse encore les couches et consulte les K/V du passé. Le cache évite le recalcul des anciennes représentations ; il ne supprime pas la lecture des poids, les nouvelles projections ou l'attention sur le contexte. L'[article fondateur du Transformer](https://arxiv.org/abs/1706.03762) décrit les projections et le masquage ; les moteurs et architectures actuels ajoutent leurs propres mécanismes.

### Ce que le chunked prefill change

Un prompt long peut monopoliser une itération et interrompre la cadence des autres requêtes. Le découper en morceaux permet au scheduler d'intercaler prefill et decode. Les morceaux conservent positions et cache communs : les traiter comme des documents indépendants changerait le calcul.

Avec un budget fictif de 2 048 positions par itération, dont 48 occupées par des decodes, il reste 2 000 positions pour le prefill. Un prompt de 6 000 tokens demande trois itérations idéales si cette répartition reste constante. Ce budget porte sur le travail de l'itération, pas sur la longueur totale du cache résident. Une séquence traitée à cette itération peut déjà avoir des milliers de positions en mémoire.

La [documentation vLLM sur le chunked prefill](https://docs.vllm.ai/en/latest/configuration/optimization/) explique les priorités d'ordonnancement et leurs compromis. Réduire la taille des morceaux peut protéger les streams tout en retardant la première sortie du long prompt ; mesurer les deux populations.

## 2. RadixAttention retrouve un état calculé

Supposons trois prompts compatibles, dont les lettres représentent des identifiants de tokens :

```text
R1 = [S A B C]
R2 = [S A B D E]
R3 = [S A F]
```

Leur longueur cumulée vaut douze positions. Un arbre radix factorise leur début :

```text
racine
  └─ [S A]                 2 positions communes
       ├─ [B]              1 position commune à R1 et R2
       │    ├─ [C]         1 position propre à R1
       │    └─ [D E]       2 positions propres à R2
       └─ [F]              1 position propre à R3
```

On conserve idéalement sept états de position distincts, au lieu de douze copies. Le calcul ignore arrondis de pages, métadonnées et sorties ultérieures. Le partage logique n'est pas une mesure directe du temps ni de la VRAM d'une implémentation.

### Recherche, bifurcation et durée de vie

Pour `R2`, le moteur retrouve `S,A,B`, puis calcule `D,E`. Pour insérer `R3`, il peut devoir scinder une arête existante après `S,A` : il réorganise les métadonnées et les références, sans devoir recalculer ces deux états communs.

Chaque branche active retient les références dont son attention a besoin. Quand une requête finit, elle les libère ; les états peuvent rester en cache pour une autre demande. Sous pression mémoire, les états sans lecteur deviennent candidats à l'éviction selon la politique. Un préfixe partagé est souvent intéressant à garder, mais aucune règle ne promet qu'il restera éternellement disponible.

RadixAttention ne remplace pas le calcul d'attention par une recherche approximative. L'arbre reconnaît des préfixes exacts et renvoie des références vers leur état. Les tenseurs restent gérés par les pools mémoire et les kernels du moteur. L'[article de SGLang](https://arxiv.org/html/2312.07104v2) explique le mécanisme classique ; le [cache unifié récent](https://www.sglang.io/blog/unified-radix-cache) ajoute la vérification des états nécessaires aux différentes composantes d'un modèle hybride.

### Pourquoi une ressemblance ne suffit pas

Une clé ou valeur dépend du contexte antérieur. Retrouver les mêmes tokens après un début différent ne rend pas leurs K/V interchangeables. Les conditions de partage incluent aussi modèle, adapter, positions, médias et frontière d'isolation pertinente.

Les nouvelles positions continuent de consulter le passé. Pour `M` positions réutilisées et `S` nouvelles, l'attention dense du suffixe comporte schématiquement `S×M + S×(S+1)/2` interactions. Le prefill évité n'est donc pas toute l'attention restante. Enfin, un cache KV n'inclut pas nécessairement les logits finaux : un hit complet peut demander un peu de recalcul pour choisir le prochain token.

## 3. La spéculation soumet des hypothèses à la cible

Un draft propose une suite peu coûteuse. La cible peut l'évaluer en bloc parce que les tokens proposés sont maintenant connus, comme les positions d'un petit prefill. Mais leurs distributions sont conditionnelles : la distribution après une proposition rejetée n'est plus celle du texte réellement émis.

```text
draft :         a   b   c   d
vérification :  oui oui non
sortie :        a   b   x

c,d : propositions abandonnées
x   : correction à intégrer avant la suite
```

Il faut restaurer les longueurs et références de cache correspondant au préfixe confirmé. Les états hypothétiques de `c,d` ne peuvent pas être réutilisés comme s'ils décrivaient `x` et sa continuation. Après acceptation de toutes les propositions, le schéma standard peut produire un token supplémentaire de la cible.

### Pourquoi le sampling exact demande une correction

Notons `p` la distribution cible et `q` celle du draft au même préfixe. Une proposition `x` tirée de `q` est acceptée avec `min(1,p(x)/q(x))`. Exemple construit sur trois tokens :

| Token | Cible p | Draft q | Probabilité d'acceptation de la proposition |
| --- | ---: | ---: | ---: |
| A | 0,6 | 0,2 | 1 |
| B | 0,3 | 0,3 | 1 |
| C | 0,1 | 0,5 | 0,2 |

La masse produite par les propositions acceptées vaut `(0,2; 0,3; 0,1)`, soit 0,6 au total. Il manque 0,4 sur `A`. Après un rejet, la correction se tire donc dans `max(p−q,0)` normalisée : ici `(1;0;0)`. On reconstitue bien `p` en ajoutant la masse rejetée redirigée vers `A`.

Tirer simplement dans `p` après rejet ajouterait des masses déjà présentes : on obtiendrait dans cet exemple `(0,44;0,42;0,14)`, qui n'est pas la cible. Ce calcul original illustre la nécessité de la correction ; la démonstration générale et le protocole séquentiel figurent dans les articles de [Leviathan et al.](https://proceedings.mlr.press/v202/leviathan23a.html) et [Chen et al.](https://arxiv.org/abs/2302.01318).

### Mesurer le gain sans confondre les compteurs

Le ratio de propositions acceptées n'est pas le nombre de tokens émis par passe. Correction et bonus sont des sorties utiles, sans être des propositions acceptées. Dans le schéma linéaire standard, hors arrêt anticipé, la longueur émise moyenne vaut `1 + acceptées/vérifications`.

Avec quatre propositions et une probabilité conditionnelle constante d'acceptation de 0,8, l'espérance simplifiée est `1+0,8+0,8²+0,8³+0,8⁴ = 3,3616`. Si draft et vérification coûtent ensemble deux fois une étape normale, le gain idéal vaut seulement `3,3616/2 ≈ 1,68`. Il faut encore vérifier mémoire, contention, latence du stream et goodput.

La garantie de distribution dépend du mécanisme exact de vérification. La [documentation vLLM](https://docs.vllm.ai/en/latest/features/speculative_decoding/) distingue le rejet standard de variantes relâchées. Un résultat métier stable sur quelques exemples ne démontre pas l'identité générale des distributions ; un texte différent pour la même graine n'est pas non plus une réfutation suffisante.

## 4. Choisir l'expérience qui répond au symptôme

| Symptôme observé | Mesure qui départage les causes | Piste à tester |
| --- | --- | --- |
| Première sortie lente sur longs prompts | File, calcul d'entrée, réutilisation effective | Contexte utile, prefill, cache de préfixes |
| Streams interrompus lors des gros prompts | ITL corrélée aux admissions | Chunked prefill et équité du scheduler |
| Premier token rapide, réponse longue lente | Temps de decode, lectures de poids et KV | Kernels, quantification validée, spéculation |
| Hit élevé mais TTFT encore mauvais | Attente et transferts, pas seulement hits | Routage, admission, coût du suffixe |
| Gain isolé mais capacité réduite au pic | Goodput et coût par tâche sous plusieurs charges | Réglage de k, mémoire du draft, politique d'activation |

Ces pistes sont des hypothèses à mesurer. Un même changement peut déplacer le goulot. La comparaison utile conserve qualité, longueurs et charge, inclut les erreurs et distingue une requête isolée d'un service partagé.

## Bilan de l'enrichissement du 12 novembre 2026

Cette seconde passe part du commit `d37a212`, après la revue transversale. Elle développe les **110 réponses initialement comprises entre 45 et 60 mots**, dans 62 fiches, avec des compléments propres à leur sujet : explication, exemple, hypothèse ou limite. Après enrichissement, ces réponses contiennent entre **75 et 102 mots hors code**. Le seuil sert au repérage des cartes à relire ; il ne devient pas une règle générale de qualité ou de longueur minimale.

Au total, **132 réponses existantes sont modifiées dans 63 fiches**, avec **39 nouvelles cartes** : 22 dans la nouvelle fiche prefill/decode, neuf sur le cache radix et huit sur le décodage spéculatif. Les trois fiches d'inférence totalisent **76 cartes**. Le vault compte désormais **148 fiches et 2 372 cartes**, dont 357 mises en situation et 184 cartes « à ne pas confondre ».

Les **2 333 questions et identifiants historiques sont conservés**. Aucune carte n'est retirée. Les liens, résumés et catalogues sont mis à jour, avec une liaison réciproque entre la nouvelle fiche et ses prérequis. Les dates de vérification des fiches 66 et 67 sont renouvelées après leur revue de mécanismes, exemples, configurations et limites ; les autres consultations restent signalées comme ciblées dans les sources.

Les réponses courtes ont aussi fait ressortir des généralisations corrigées : anonymisation et moyens raisonnables de réidentification, analyse des données personnelles dans un modèle selon l'avis du CEPD, rôle des échelles AWQ, permissions des agents et comparaison de stockages vectoriels. Les références primaires correspondantes figurent dans les fiches concernées. Il ne s'agit pas d'une revérification de toutes les affirmations historiques du vault.

### Vérifications

- Lint : **zéro erreur et zéro avertissement**, avec lecture compatible Obsidian et Anki.
- Catalogues : synchronisation du README et du MOC contrôlée.
- Identifiants : comparaison exhaustive avant/après et conservation des 2 333 identités existantes.
- Calculs : chronologie du premier token, partage logique 12 → 7, correction de probabilité, espérance de longueur, budgets de chunks et transfert de 1 Gio recalculés séparément.
- `make check` : ruff, mypy, 54 tests et deux ateliers locaux.
- `make export` : paquet Anki généré, puis contrôle des notes actives, des cartes retirées suspendues et des identifiants historiques dans sa base SQLite.

Les exercices et démonstrations ne constituent pas des mesures sur un GPU. Les versions de serving et leurs variantes doivent être testées avec le matériel, la charge et les contraintes réellement déployés. Les tests du dépôt protègent la structure, la navigation et l'export ; la pertinence du contenu reste issue de la relecture et des sources citées.
