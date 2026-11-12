# Speculative decoding — Flashcards
Tags: #flashcards #ai-engineering #inference #speculative-decoding #llm
Vérifié le : 12 novembre 2026 — mécanismes et limites confrontés aux articles et documentations cités ; performances à mesurer sur la cible.
<!-- summary: brouillon et vérification en une passe, conditions d’amortissement des lectures, règle d'acceptation sans perte, gain selon le taux d'acceptation, choix de k, types de brouillons (petit modèle, n-grammes, EAGLE, Medusa, MTP), vérification en arbre, quand ça aide ou nuit, configuration vLLM, coûts, métriques d'acceptation, validation d'un déploiement, calcul d'amortissement de la spéculation, vérification causale parallèle, exemple p/q, démonstration de correction, restauration du cache, compteurs et streaming par groupes. -->


Quel est le principe du speculative decoding ? <!--anki:735b235457367c524b6a-->
?
Un **draft** peu coûteux propose plusieurs tokens ; la **cible** évalue ces positions ensemble, puis un mécanisme de vérification conserve un préfixe admissible et produit une correction ou un token supplémentaire.
```text
propositions : a b c d
vérification : a accepté, b accepté, c rejeté
émission     : a b x ; d est abandonné
```
Le schéma linéaire exact produit normalement au moins un token par vérification, sous réserve d'arrêt. Ce gain n'abolit pas la causalité : le draft propose des dépendances déjà connues au vérificateur. La qualité de la cible reste la référence ; la règle d'acceptation, pas la seule présence d'un second modèle, détermine la garantie.

---

Pourquoi vérifier k tokens coûte-t-il presque autant que d'en générer un ? <!--anki:643b3476537b31506257-->
?
À petit batch, quand lire les poids domine, vérifier plusieurs positions ensemble **amortit une lecture des poids**. Le calcul supplémentaire peut rester modeste par rapport à cette lecture, ce qui rend la spéculation intéressante.

Cela n'implique pas une vérification gratuite : attention, KV, calcul et brouillon ajoutent du travail. Si le GPU est déjà limité par le calcul à forte charge, ce travail peut réduire le débit. Mesurer durée du brouillon, vérification, tokens acceptés par passe et goodput, pour les longueurs et concurrences réellement visées.

---

Comment décide-t-on d'accepter un token proposé ? <!--anki:4457756f687577352a63-->
?
En **greedy**, comparer au choix de la cible au même préfixe validé. En sampling exact, une proposition `x` tirée selon `q` est acceptée avec `min(1, p(x)/q(x))`, où `p` est la distribution cible.

Comparer un tirage uniforme à ce seuil. À la première proposition rejetée, tirer une correction dans la distribution proportionnelle à `max(p−q, 0)` et abandonner la suite proposée. Si toutes sont acceptées, tirer un token supplémentaire selon la cible au préfixe complété. Les distributions doivent correspondre aux transformations réellement appliquées ; confondre scores bruts et probabilités filtrées invalide l'argument d'exactitude.

---

Le speculative decoding dégrade-t-il la qualité ? <!--anki:47393e6c375564426d2e-->
?
Le **speculative sampling exact**, avec acceptation/rejet et distribution résiduelle correctes, préserve théoriquement la distribution de la cible ; en greedy, la vérification doit préserver son choix.

Cette propriété ne couvre pas automatiquement toutes les variantes appelées « spéculatives », ni une cible elle-même quantifiée par rapport à son modèle d'origine. Vérifier l'algorithme et les modes supportés. Les arrondis et variations de batch peuvent aussi changer des sorties individuelles. Évaluer qualité et performance en pratique ; même graine ne signifie pas nécessairement même texte, malgré une distribution théorique préservée.

---

De quoi dépend le gain de vitesse du speculative decoding ? <!--anki:657749397926736d7a6f-->
?
Dans un modèle simplifié avec probabilité d'acceptation conditionnelle constante α et k propositions, on produit en moyenne :
```text
E = 1 + α + … + α^k = (1 − α^(k+1)) / (1 − α)
α = 0,8 ; k = 4 → E = 3,3616 tokens par passe
```
Pour α = 1, la limite vaut k + 1. Le speedup dépend aussi du temps : `E × temps_decode_standard / (temps_brouillon + temps_vérification + surcoûts)`. Un bon taux d'acceptation ne suffit pas si le brouillon coûte trop cher. Les dépendances réelles et EOS limitent ce modèle ; mesurer le gain sous charge.

---

Comment choisir le nombre de tokens proposés (k) en speculative decoding ? <!--anki:46282560713f4b67613d-->
?
Augmenter **k** ajoute des propositions mais aussi du coût de draft, de vérification et de cache temporaire. Un rejet précoce rend inutile toute la suite : le rendement marginal diminue lorsque les longues suites sont rarement acceptées.

Tester plusieurs valeurs au même trafic et comparer tokens utiles par unité de temps, pas seulement taux d'acceptation. Une adaptation par charge ou catégorie de requêtes peut aider si elle est supportée et validée. Il n'existe pas une plage universellement optimale : longueur de sortie, méthode de draft, matériel et concurrence changent le compromis. Garder une baseline sans spéculation et la possibilité de désactivation.

---

Quelles sont les façons de produire le brouillon d'un speculative decoding ? <!--anki:507674457b374c6c452c-->
?
Un **draft** peut provenir d'un petit modèle, d'une recherche dans le contexte ou d'un module associé à la cible. Distinguer :

- **Modèle séparé** : proposition autorégressive avec coût et cache propres.
- **Lookup de tokens** : continuations déjà présentes dans le prompt ou un corpus de suffixes.
- **Têtes ou modules auxiliaires** : familles Medusa, EAGLE, MTP, avec dépendances d'entraînement et algorithmes différents.

Le draft n'a pas besoin d'être aussi compétent que la cible ; il doit proposer assez vite des continuations souvent utiles. La méthode de vérification reste décisive pour préserver la distribution : toutes les combinaisons de têtes et d'acceptation ne sont pas automatiquement exactes.

---

Quand le prompt lookup (n-grammes) est-il efficace ? <!--anki:75357b292e2173597c45-->
?
Le **prompt lookup** propose des continuations déjà rencontrées après une séquence de tokens correspondante. Il peut aider lorsqu'une sortie reprend beaucoup l'entrée, par exemple une édition de code ou une extraction, mais pas nécessairement sur toute tâche portant ces noms.

Si le contexte contient `return total / len(items)` et que la sortie rejoint `return total /`, le moteur peut proposer `len(items)`. La cible doit encore vérifier selon l'algorithme retenu. Il n'y a pas de second réseau à charger, mais recherche, index et buffers consomment des ressources. Mesurer le taux de reprises réellement utiles et le coût de leurs vérifications.

---

Qu'est-ce que la vérification en arbre en speculative decoding ? <!--anki:7548316562267e3a7176-->
?
Un **arbre de propositions** conserve plusieurs continuations possibles plutôt qu'une seule chaîne. La cible peut évaluer ses nœuds dans une passe utilisant un masque qui laisse chaque nœud consulter son préfixe et ses ancêtres, sans mélanger les branches incompatibles.

Le choix du chemin émis dépend ensuite de l'algorithme de vérification et de sampling. Plus de branches augmente les chances d'une continuation utile, mais aussi positions vérifiées, mémoire temporaire et coordination. Le simple fait d'explorer un arbre ne garantit ni gain de temps ni exactitude de distribution. Mesurer le coût par token confirmé et préciser la variante utilisée.

---

Quand le speculative decoding aide-t-il et quand nuit-il ? <!--anki:515b7d72714b55672d64-->
?
- **Aide** : petits batchs et services sensibles à la latence, où le GPU attend la mémoire ; texte prévisible (code, JSON, recopie) ; température basse
- **Nuit** : **gros batchs** où le GPU est déjà saturé en calcul (la vérification consomme ce calcul et fait baisser le débit total) ; température élevée ou texte très créatif (faible acceptation)

Ce sont des tendances, pas des critères suffisants. Comparer au decode normal à concurrence égale : un meilleur TPOT pour une requête isolée peut s'accompagner d'un moins bon débit et de files plus longues en production.

---

Quelles métriques d'inférence le speculative decoding améliore-t-il ? <!--anki:503836423d712d492f3d-->
?
Il vise surtout le **temps par token de sortie** et la durée des réponses longues. Il ne supprime pas le prefill du prompt ; draft, compilation ou ordonnancement peuvent aussi modifier le TTFT observé.

Avec TTFT de 400 ms et 20 ms entre tokens, une réponse de `N` tokens dure `400 + (N−1) × 20` ms. Diviser ces intervalles par deux donne **780 → 590 ms pour 20 tokens**, et **10,38 → 5,39 s pour 500**. Ce calcul suppose cadence constante et TTFT inchangé. En streaming réel, mesurer aussi les pauses entre groupes de tokens et le débit sous charge.

---

Comment activer le speculative decoding dans un serveur d'inférence ? <!--anki:676979656b57647b6226-->
?
Les principaux moteurs le supportent : vLLM, SGLang, TensorRT-LLM, llama.cpp. Dans vLLM :
```bash
vllm serve <modèle-cible> --speculative-config '{
  "method": "ngram", "num_speculative_tokens": 4,
  "prompt_lookup_min": 2, "prompt_lookup_max": 5 }'
```
Autres valeurs de `method` : `draft_model`, `eagle3`, `mtp`, `suffix`…

La commande est un exemple à adapter à la version installée ; vérifier les méthodes compatibles avec modèle, parallélisme et matériel. Le mode n-gram propose des suites issues du contexte sans charger de petit modèle. Mesurer taux d'acceptation, latence et débit : une proposition souvent rejetée peut ralentir le service.

---

Quels coûts et quelles contraintes le speculative decoding impose-t-il ? <!--anki:4d413c2a2c4a61556e39-->
?
Compter **calcul du draft**, vérification, synchronisation, cache temporaire et éventuel modèle supplémentaire. Un petit modèle distinct a ses poids et son état ; un lookup utilise plutôt index et buffers, sans second réseau neuronal.

Le schéma standard à espace de tokens commun suppose un tokenizer compatible ; des techniques inter-tokenizers existent mais demandent un mécanisme spécifique. Des têtes entraînées doivent correspondre à la cible et au mode utilisé. Vérifier contraintes de parallélisme, quantification et génération structurée. L'acceptation ne tranche pas seule : une méthode qui garde beaucoup de tokens peut consommer la capacité nécessaire aux autres requêtes.

---

Quelles métriques suivre pour le speculative decoding ? <!--anki:732143772f26244d7852-->
?
Séparer **acceptation du draft**, **tokens utiles émis par vérification**, latence et capacité globale. Un token de correction ou bonus compte dans les sorties utiles, sans être une proposition acceptée.

Dans le schéma linéaire standard, hors arrêt anticipé : longueur émise moyenne = `1 + propositions acceptées / vérifications`. Le ratio `acceptées / proposées` répond à une autre question. Suivre aussi acceptation par position, temps de draft et vérification, mémoire et goodput. Les noms de compteurs dépendent du moteur et de la version ; contrôler leur définition. EOS, propositions de longueur variable et contraintes de sortie demandent un décompte explicite.

---

Comment valider un déploiement avec speculative decoding ? <!--anki:6c70435e57353c775b6d-->
?
1. **Fixer la référence** : cible, tokenizer, sampling, contraintes et matériel ; identifier si la variante annonce une vérification exacte.
2. **Contrôler les résultats** : comparer greedy avec analyse des écarts numériques ; en sampling, examiner distributions pertinentes et qualité avec incertitude.
3. **Tester plusieurs charges** : draft, vérification, TTFT, pauses de stream, goodput et mémoire, sur les mêmes longueurs.
4. **Vérifier les arrêts** : EOS, limite de sortie, refus et rejet précoce avec cache correctement restauré.
5. **Décider selon le SLO** et conserver un retour au decode normal.

Une évaluation stable complète la validation algorithmique ; elle ne démontre pas, à elle seule, que deux distributions sont identiques.

---

Calcul : un draft coûte 2 ms pour un bloc, sa vérification 10 ms et accepte en moyenne trois tokens utiles. Quel gain idéal face à 6 ms par token sans spéculation ? <!--anki:3234653339366662386438313464663039353764653432633838636563643462-->
?
Le bloc coûte `2 + 10 = 12 ms`. Si « trois tokens utiles » signifie **trois tokens émis au total**, correction ou bonus inclus :
```text
temps = 12/3 = 4 ms/token ; accélération = 6/4 = 1,5×
```
Si l'on comptait au contraire trois propositions acceptées **plus** un bonus, quatre tokens seraient émis : `12/4 = 3 ms/token`, soit `2×`. Préciser donc le compteur avant de calculer le gain.

Ces résultats supposent coûts constants, aucune fin anticipée et conditions comparables. Inclure mémoire du draft, synchronisation et charge réelle pour une décision de déploiement ; un gain par séquence ne garantit pas davantage de requêtes utiles par seconde.

---

Pourquoi la cible peut-elle vérifier plusieurs positions sans connaître les futurs vrais tokens ? <!--anki:3232636563643463316334383431643862396565303838373464393862383235-->
?
Elle reçoit une **continuation proposée déjà explicite** et calcule les distributions conditionnelles sous masque causal, comme lorsqu'elle traite un prompt connu.
```text
position 1 : p(a | préfixe)
position 2 : p(b | préfixe, a)
position 3 : p(c | préfixe, a, b)
```
Ces calculs peuvent être regroupés dans une passe sur les positions ; les couches restent ordonnées. Tant que `a,b` sont acceptés, leurs conditionnements conviennent. Si `b` est rejeté, la distribution calculée après `a,b` ne décrit plus la continuation réellement émise : il faut jeter les propositions suivantes. « Parallèle » signifie ici scores sur hypothèses connues, pas prédiction indépendante du futur.

---

Calcul : avec p=(0,6; 0,3; 0,1) et q=(0,2; 0,3; 0,5) sur A,B,C, quelles probabilités d'acceptation ? <!--anki:3633616434326637336366643463653661653836346235383533653432363865-->
?
Appliquer `min(1,p/q)` à chaque proposition :
```text
A : min(1, 0,6/0,2) = 1
B : min(1, 0,3/0,3) = 1
C : min(1, 0,1/0,5) = 0,2
```
Le draft propose `C` avec probabilité 0,5, mais seulement un cinquième de ces propositions est accepté. La masse totale acceptée vaut `0,2 + 0,3 + 0,1 = 0,6` ; la masse rejetée vaut 0,4. Les trois composantes sont des probabilités au même préfixe, après les réglages de sampling retenus. Une acceptation égale à un ne signifie pas que ce token sera systématiquement proposé ou émis.

---

Calcul : dans l'exemple p=(0,6; 0,3; 0,1), q=(0,2; 0,3; 0,5), que tirer après un rejet ? <!--anki:6263393163343864323865343465396261386237326263623763613564313561-->
?
La **masse résiduelle positive** vaut :
```text
max(p−q,0) = (0,4 ; 0 ; 0)
après normalisation : r = (1 ; 0 ; 0)
```
La correction est donc `A`. En agrégeant les propositions acceptées `(0,2;0,3;0,1)` et la masse de rejet `0,4` redirigée vers `A`, on retrouve exactement `(0,6;0,3;0,1)`.

Cet exemple utilise le même préfixe et les distributions normalisées indiquées. Il montre pourquoi tirer simplement dans `p` après rejet serait faux : certaines masses de `p` ont déjà été apportées par les tokens acceptés. Si `p=q`, aucun rejet ne survient théoriquement ; la résiduelle n'a pas à être normalisée.

---

Pourquoi la correction résiduelle préserve-t-elle la distribution cible dans le sampling spéculatif exact ? <!--anki:3266636462356239346462303434383539643535633831363834343436363938-->
?
La probabilité d'émettre `x` via une proposition acceptée est `q(x) × min(1,p(x)/q(x)) = min(p(x),q(x))` sur le support du draft.

La masse manquante pour atteindre `p(x)` est donc `max(p(x)−q(x),0)`. La probabilité totale de rejet est la somme de ces manques ; y tirer une correction normalisée les réinjecte exactement. Ainsi :
```text
masse acceptée pour x + masse corrigée pour x
= min(p(x),q(x)) + max(p(x)−q(x),0) = p(x)
```
Appliquer ce raisonnement successivement aux préfixes validés donne la garantie du schéma. Arrondis et implémentations approximatives demandent un contrôle distinct ; la démonstration suppose les distributions réellement utilisées.

---

Pourquoi faut-il retirer du KV cache les propositions situées après un rejet ? <!--anki:3163353664666432396164393461306339663265663264346664366335323739-->
?
Les K/V calculées pour une proposition appartiennent à un **préfixe hypothétique**. Après la première divergence, la suite ne correspond plus aux tokens réellement émis.

Si `a,b` sont acceptés mais `c` remplacé par `x`, les états de `c,d` ne doivent pas rester comme s'ils décrivaient `x` et sa suite. Rétablir longueurs et tables de blocs, puis intégrer la correction avant les prochaines propositions. Le draft et la cible doivent être resynchronisés, selon la méthode. Ne pas libérer un bloc encore partagé ailleurs : gestion logique du rejet et allocation physique sont deux responsabilités distinctes.

---

Pourquoi un taux d'acceptation de 80 % ne signifie-t-il pas une accélération de cinq ? <!--anki:6365323832323936386137623438313638353933613235623561313735613838-->
?
Le **ratio de propositions acceptées** ne mesure ni le temps du draft ni la vérification. Même lorsque beaucoup de propositions passent, les produire peut être coûteux.

Dans le modèle à acceptation conditionnelle constante `α=0,8` et quatre propositions, le nombre moyen émis vaut `1+0,8+0,8²+0,8³+0,8⁴ = 3,3616`. Si une itération spéculative coûte deux fois une étape normale, le gain idéal n'est que `3,3616/2 ≈ 1,68`. Ce modèle ignore EOS et dépendances réelles. Ne pas déduire directement `α` d'un compteur dont le dénominateur inclut des propositions jamais atteintes après rejet.

---

Que vérifier avant d'affirmer qu'une variante de speculative decoding est sans perte ? <!--anki:3766663732336130383630323437373838633361666266373635386232306638-->
?
Identifier **l'algorithme de vérification exact**, ses réglages et sa cible de référence. Certaines méthodes relâchent volontairement la vérification pour gagner du temps ; le nom « speculative » ne garantit pas la conservation de distribution.

Comparer même cible, tokenizer, filtres et contraintes, puis tester greedy et sampling selon leur protocole. La documentation actuelle de vLLM distingue notamment le rejet standard de variantes approximatives comme FLy. Une évaluation métier inchangée n'est pas une preuve mathématique d'identité de distribution ; réciproquement, des textes différents pour une même graine ne réfutent pas seuls la garantie théorique. Mesurer qualité, distributions pertinentes et écarts numériques.

---

Pourquoi les tokens spéculatifs peuvent-ils arriver en petits groupes dans un stream ? <!--anki:3662343236653065666364663462323138326463363730306564393633346230-->
?
La **validation se fait par itération** : plusieurs tokens deviennent publiables ensemble après une même vérification. Le client peut recevoir un groupe, puis attendre l'itération suivante.

Un meilleur temps moyen par token ne garantit donc pas une cadence parfaitement régulière. Mesurer les intervalles de réception, les tailles de groupes et les pauses visibles, en distinguant regroupement du moteur et buffering réseau. Pour la voix ou l'affichage interactif, une longue pause entre deux groupes peut rester gênante malgré un bon débit moyen. Les tokens rejetés ne doivent pas être affichés comme texte confirmé avant correction.

---

## Mises en situation

Mise en situation : tu actives le speculative decoding sur ton assistant. En test à un utilisateur, la génération est deux fois plus rapide ; en production aux heures de pointe, le débit total baisse. Pourquoi ? <!--anki:72653f2439376372473a-->
?
1. **Comparer à trafic égal** : mêmes longueurs, qualité et concurrence ; mesurer le débit utile plutôt que seulement tokens/s.
2. **Profiler les phases** : un draft et une vérification amortis à faible batch peuvent consommer du calcul supplémentaire au pic.
3. **Examiner la mémoire** : poids et KV du draft peuvent réduire la concurrence disponible pour la cible.
4. **Tester plusieurs k et politiques d'activation**, si le moteur le permet, en incluant files et pauses visibles.
5. **Choisir selon les SLO conjoints** : latence, débit et coût.

**Piège** : conclure d'avance que toute charge faible est limitée par la mémoire, ou que toute charge forte doit désactiver la spéculation.

---

Mise en situation : ton taux d'acceptation plafonne à 45 % avec un petit modèle de brouillon, et le gain est décevant. Quelles options ? <!--anki:4e214843397e5f573d46-->
?
1. **Vérifier la métrique** : propositions comptées, positions atteintes, corrections et éventuels arrêts anticipés.
2. **Segmenter les résultats** selon entrées, sorties, longueur et sampling, sans supposer qu'une catégorie garantit un taux élevé.
3. **Mesurer le coût du draft** et la longueur réellement confirmée par vérification.
4. **Comparer d'autres propositions compatibles** : modèle mieux aligné, modules dédiés ou lookup lorsque des répétitions existent.
5. **Régler k ou désactiver par route** d'après le temps utile et la qualité mesurés.

**Piège** : augmenter le nombre de propositions pour compenser une mauvaise acceptation précoce ; la suite rejetée peut ajouter du travail sans aucune sortie utile.

---

Mise en situation : un responsable qualité s'inquiète que le speculative decoding change les réponses du modèle. Comment le rassures-tu, preuve à l'appui ? <!--anki:6f23684542583862703a-->
?
1. **Identifier la variante et sa référence** : le rejet standard exact et une vérification relâchée n'offrent pas la même garantie.
2. **Expliquer la correction résiduelle**, qui restaure la masse de probabilité manquante dans le schéma exact.
3. **Tester greedy et sampling** avec même cible et paramètres, en distinguant écarts numériques, bug et variance normale.
4. **Couvrir les cas limites** : EOS, JSON contraint, rejets, cache et limite de sortie.
5. **Surveiller qualité et performance** par segment après déploiement.

**Piège** : annoncer une garantie pour toutes les techniques dites spéculatives, ou présenter quelques réponses identiques comme une preuve générale de conservation de distribution.

---

## Sources

- [vLLM — speculative decoding et limites de reproductibilité numérique](https://docs.vllm.ai/en/latest/features/speculative_decoding/index.html)

- [Leviathan et al. — Fast Inference from Transformers via Speculative Decoding](https://proceedings.mlr.press/v202/leviathan23a.html) — revue ciblée du 12 novembre 2026 : acceptation, correction résiduelle et espérance de longueur.

- [Chen et al. — Accelerating Large Language Model Decoding with Speculative Sampling](https://arxiv.org/abs/2302.01318) — revue ciblée du 12 novembre 2026 : conservation de la distribution et limites numériques.

- [vLLM — configuration et garanties du décodage spéculatif](https://docs.vllm.ai/en/latest/features/speculative_decoding/) — revue ciblée du 12 novembre 2026 : schéma exact, variantes approximatives et commande n-gram.

- [vLLM — métriques d’acceptation par requête](https://docs.vllm.ai/en/latest/features/speculative_decoding/acceptance_metrics/) — revue ciblée du 12 novembre 2026 : propositions acceptées, tokens bonus et longueur émise.

## Connexions
- [[62-optimisations-inference|Optimisations d'inférence]] — prefill, decode et bande passante mémoire
- [[65-probabilites-sampling|Probabilités & sampling]] — pourquoi la distribution est préservée
- [[64-metriques-slo-inference|Métriques & SLO]] — l'effet sur TPOT et TTFT
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM
- [[114-reproductibilite-variance|Reproductibilité & variance]] — les écarts numériques
- [[68-quantization|Quantization]] — l'autre levier pour accélérer le decode
- [[93-monitoring-inference|Monitoring de l'inférence]] — suivre l'acceptation en production
- [[61-kv-cache-attention|KV cache]] — la mémoire qui limite la concurrence
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — ce qui limite chaque phase de l'inférence
- [[60-013-prefill-decode-pas-a-pas|Prefill & decode pas à pas]] — suivre les positions calculées, le cache et les délais
- [[00-moc-ai-engineering|MOC AI Engineering]]
