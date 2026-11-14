# Prefix caching & RadixAttention — Flashcards
Tags: #flashcards #ai-engineering #inference #kv-cache #caching #llm
Vérifié le : 12 novembre 2026 — mécanismes et limites confrontés aux articles et documentations cités ; performances à mesurer sur la cible.
<!-- summary: prefix caching de vLLM, arbre radix de SGLang, éviction, ordonnancement et routage cache-aware, offloading du KV cache (LMCache), limites, canal auxiliaire temporel, métriques par requête et token, gain de TTFT réel, affinité et surcharge, isolation par cache_salt, arbre compressé pas à pas, références et séparation des branches, calcul de partage, cache hybride et logits, alignement des blocs, invalidation du modèle. -->


Qu'est-ce que le prefix caching côté serveur ? <!--anki:703830706b2926403428-->
?
Le **prefix caching** réutilise les clés et valeurs déjà calculées pour le début exact d'une séquence, avec le même modèle et un état compatible. Il évite de recalculer les représentations de ces positions lors du prefill d'une autre requête.

Si 3 000 tokens initiaux d'un prompt de 3 200 sont réutilisables, les 200 nouveaux doivent encore traverser le modèle et consulter le passé. Le cache ne fournit ni une réponse finale ni une recherche sémantique. Le gain dépend du travail évité, des transferts et de la file ; le decode continue de lire le contexte et de calculer les tokens suivants.

---

Comment vLLM implémente-t-il l'automatic prefix caching ? <!--anki:4e4853344a45633c4345-->
?
vLLM associe des **blocs KV physiques** aux tokens de séquences logiques. Pour reconnaître un bloc de préfixe, son identifiant dépend notamment des tokens, du bloc parent et d'informations de compatibilité comme adapter, contenu multimodal ou sel de cache.

Deux blocs au texte identique mais précédés de contextes différents ne sont donc pas interchangeables. Une table permet de retrouver les blocs réutilisables ; la gestion de références et l'éviction contrôlent leur durée de vie. Granularité et comportement dépendent de la version : distinguer préfixe logique commun et tokens effectivement réutilisés. PagedAttention organise la mémoire ; le cache de préfixe décide de sa réutilisation.

---

Qu'est-ce que RadixAttention ? <!--anki:71516b533b7348404c3e-->
?
**RadixAttention** organise la réutilisation du KV cache dans SGLang au moyen d'un **arbre radix**, un arbre de préfixes dont les chemins sans bifurcation sont compressés en séquences de tokens.

Le moteur cherche le plus long préfixe déjà calculé et compatible, récupère ses références KV, puis calcule la suite et l'insère dans l'arbre. L'arbre contient des métadonnées de recherche ; les tenseurs vivent dans les pools mémoire du moteur. Le mot « attention » ne désigne pas une nouvelle formule de softmax : l'optimisation évite des calculs répétés entre requêtes, conversations ou branches partageant exactement leur début.

---

Comment SGLang évince-t-il les entrées de l'arbre radix ? <!--anki:746d6a686e7c2f454321-->
?
Dans le mécanisme classique décrit par RadixAttention, l'éviction choisit des **feuilles réutilisables selon leur ancienneté**, en protégeant par références les chemins utilisés par des requêtes actives. Libérer une feuille peut rendre son parent lui-même candidat.

Les suffixes peu utilisés disparaissent ainsi souvent avant un préfixe partagé. Ce n'est pas une garantie de conservation : si tout un sous-arbre devient inactif, il peut finir par être retiré. Les versions récentes proposent plusieurs politiques et caches hybrides ; vérifier la configuration. Ne jamais évincer un bloc encore nécessaire à un calcul actif pour améliorer artificiellement le hit rate.

---

Qu'est-ce que l'ordonnancement cache-aware ? <!--anki:736e6973636b5e717b7b-->
?
Un **scheduler sensible au cache** utilise la réutilisation possible pour ordonner les requêtes, au lieu de considérer uniquement leur arrivée. La politique longest-prefix-match favorise celles qui retrouvent un long préfixe compatible.

Cela peut amortir le traitement d'un document partagé avant son éviction. Ce n'est pas toujours le meilleur délai utilisateur : une requête sans hit peut attendre indéfiniment si de nouvelles requêtes chaudes arrivent. Combiner âge, échéance, charge et équité ; comparer le travail économisé au temps passé en file. À faible charge, le choix d'ordre compte souvent moins que coût du prompt et vitesse du modèle.

---

Quels workloads profitent le plus du prefix caching ? <!--anki:4c337b29762e50327361-->
?
- **Agents multi-tours** : l'historique grossit mais son début ne change pas
- Longs **system prompts et définitions d'outils** partagés
- **Few-shot**, **self-consistency**, arbres de raisonnement : un même préfixe, plusieurs branches
- **RAG** répété sur les mêmes documents
- Beaucoup d'utilisateurs sur un **même assistant**

Le gain dépend des tokens effectivement réutilisés, pas seulement du nombre de hits. Une requête avec 100 tokens partagés sur 10 000 profite peu du cache. Mesurer longueur du préfixe réutilisé et TTFT, avec l'isolation d'accès prévue.

---

Pourquoi le routage entre réplicas doit-il tenir compte du cache ? <!--anki:723d5362493f5e2c4929-->
?
Quand les caches résident **localement sur les réplicas**, répartir aveuglément les requêtes disperse les préfixes chauds. Un routeur peut préférer l'instance qui possède déjà le préfixe compatible, sous réserve des droits et de sa charge.

Comparer délai de file, prefill restant et transferts éventuels ; un hit sur une instance surchargée peut être moins utile qu'un calcul neuf ailleurs. Un cache hiérarchique ou partagé change ce compromis, sans supprimer les coûts de déplacement du KV. Mesurer par réplica les tokens réutilisés et la latence réelle, plutôt que supposer que toute affinité améliore le service.

---

Qu'est-ce que l'offloading du KV cache ? <!--anki:482b3a513b2b5b7e2545-->
?
L'**offloading** déplace ou sauvegarde des K/V hors de la mémoire GPU, par exemple en RAM hôte ou sur un stockage hiérarchique. Il augmente le volume conservable, mais la réutilisation exige un transfert vers le lieu du calcul.

Comparer coût de récupération, calcul évité et contention sur les liens. Un long préfixe peut être rentable à recharger ; quelques tokens peuvent coûter moins cher à recalculer. Lorsque des transferts sont recouvrables avec le calcul, une partie du délai peut être masquée, sans disparaître du budget de bande passante. Inclure allocations, synchronisation et isolation des données dans l'évaluation.

---

Quelles sont les limites du prefix caching ? <!--anki:7a28604f3a4f7871363e-->
?
- Correspondance **exacte depuis le début** : un token différent en tête, et rien n'est réutilisé
- **Granularité par bloc** (vLLM ne cache que les blocs pleins)
- Cache **borné** par la mémoire et évincé sous forte charge
- N'accélère que le **prefill**, pas la génération (decode)

Un horodatage placé avant les instructions stables peut invalider tout le préfixe à chaque appel. Déplacer les données variables après ce préfixe si la sémantique le permet, puis vérifier le gain sous la même charge et le même routage.

---

Quel risque de sécurité pose un prefix cache partagé entre plusieurs clients ? <!--anki:6b45506d623c422f4b4a-->
?
Un **canal temporel** peut révéler qu'un préfixe deviné se trouve déjà en cache : sa réutilisation réduit une partie du prefill. L'attaquant observe des temps, pas directement les tenseurs ni le texte du voisin.

Des essais répétés et des connaissances préalables peuvent rendre cet indice exploitable malgré le bruit. Définir une frontière de partage autorisée, puis imposer côté serveur une séparation adaptée, par exemple un sel secret de cache par groupe de confiance lorsque le moteur le permet. Vérifier l'offre et la fonctionnalité précises : aucune règle universelle d'isolation de tous les fournisseurs ne doit être présumée.

---

Comment mesurer l'efficacité du prefix cache ? <!--anki:79677d5a467a362a2129-->
?
Mesurer **tokens réutilisés**, TTFT et coût, pas seulement requêtes ayant un hit. Vérifier l'unité exacte des métriques du moteur ou fournisseur ([[123-caching-agressif|caching agressif]]).

Exemple simplifié : une requête de 100 tokens entièrement réutilisée et une autre de 9 900 tokens sans hit donnent **50 % de requêtes avec hit**, mais seulement **1 % des tokens réutilisés**.

Comparer cache froid/chaud à charge et longueurs identiques, en incluant évictions et mémoire occupée. Une chute peut venir d'un préfixe instable, mais aussi d'un changement de trafic, de routage ou de pression mémoire. Un hit élevé n'assure pas une baisse du TTFT si l'attente domine.

---

Calcul : pour un prompt de 10 000 tokens dont 9 000 réutilisés, supposer un prefill passant de 300 à 30 ms et 200 ms fixes d’attente/transport. Quel gain de TTFT, hors surcoûts du cache ? <!--anki:6365333934613162646331393439376661353639326434613561303631636664-->
?
Supposons un prefill de 300 ms sans cache, ramené à 30 ms pour le travail non caché, et **200 ms fixes** d'attente et de transport :
```text
TTFT sans cache = 200 + 300 = 500 ms
TTFT avec cache = 200 + 30  = 230 ms, avant surcoûts
accélération = 500 / 230 ≈ 2,17, et non 10
```
Les tokens nouveaux consultent encore les K/V du préfixe ; chargement et recherche du cache ajoutent éventuellement du temps. Le facteur dix sur le prefill simplifié ne se transpose pas à la latence complète ni au decode.

---

Calcul : neuf prompts de 100 tokens sont entièrement réutilisables en cache et un prompt de 9 100 tokens ne l’est pas. Quels taux de hit par requête et par token obtient-on ? <!--anki:3364316439313634633036333430353638346561626463623734633461366439-->
?
Neuf prompts de 100 tokens sont entièrement réutilisables, mais un prompt de 9 100 tokens ne l'est pas. Le taux de requêtes avec hit atteint **90 %**, tandis que la part de tokens réutilisables vaut seulement `900 / 10 000 = 9 %`.

Définir l'unité du compteur : requête avec hit partiel, bloc ou token ; vérifier celle du moteur. Calculer les ratios à partir des sommes, pas de la moyenne des ratios des réplicas. Même le taux par token ne mesure pas directement les millisecondes économisées : longueur, file et transferts interviennent.

---

Quand faut-il renoncer à l’affinité de cache lors du routage ? <!--anki:3661383866353637343861373430323761343465633631363938343461373764-->
?
Quand le temps économisé par le préfixe local devient inférieur à l'attente supplémentaire du réplica chaud. Comparer **délai prédit de file + prefill restant + transferts** aux alternatives, puis vérifier la prédiction en charge.

Une politique purement fondée sur le hit rate peut concentrer le trafic sur quelques instances et dégrader le p99. Prévoir un seuil d'écart de charge, l'équité entre clients et les frontières de confidentialité. Le cache améliore surtout le travail d'entrée ; il ne rend pas gratuits la lecture du contexte en decode ni les tokens de sortie.

---

Comment isoler le prefix cache vLLM entre tenants sans perdre tout partage à l'intérieur d'un tenant ? <!--anki:3431366139336134386564663464613639396632653131333339366263386235-->
?
La version documentée de vLLM permet un **`cache_salt`** par requête : il participe au hash du premier bloc, ce qui sépare la réutilisation entre valeurs différentes.

Faire attribuer par la gateway une valeur secrète stable pour chaque groupe de confiance, puis la transmettre à tous ses appels. Ne pas laisser un client choisir le sel d'un autre tenant. Un sel aléatoire à chaque requête supprimerait aussi le partage souhaité. Tester les hits et la séparation réelle ; ce mécanisme ne remplace pas les permissions sur les données et les autres caches.

---

À ne pas confondre : RadixAttention, PagedAttention et FlashAttention ? <!--anki:3638343633313466366663623439303138376531383064356131386566353362-->
?
**RadixAttention** identifie les préfixes déjà calculés pour réutiliser leur état. **PagedAttention** organise le KV en blocs physiques adressés par des séquences logiques. **FlashAttention** optimise le calcul de l'attention et ses transferts mémoire sans matérialiser toute la matrice des scores.

Ces rôles sont complémentaires : retrouver un préfixe, gérer ses pages et calculer efficacement les nouvelles positions. Aucun ne transforme un texte seulement ressemblant en cache réutilisable. Leur combinaison et les kernels disponibles dépendent du moteur ; mesurer le travail évité et le calcul restant au lieu de multiplier des facteurs d'accélération annoncés séparément.

---

Comment un arbre radix représente-t-il deux prompts qui divergent après trois tokens ? <!--anki:3066383534356432373639383465393061316435346433326565666362326235-->
?
Supposons les tokens symboliques `[S,A,B,C]` puis `[S,A,B,D,E]`. Le préfixe commun de longueur trois reste unique ; les suffixes se séparent :
```text
racine
  └─ [S A B]  → références KV communes
       ├─ [C]   → suffixe de la requête 1
       └─ [D E] → suffixe de la requête 2
```
Une arête porte plusieurs tokens, contrairement à un trie naïf avec un nœud par token. La seconde requête réutilise les états de `S,A,B`, puis calcule `D,E` en consultant ce passé. Ces lettres sont des identifiants de tokens pédagogiques, pas des caractères supposés correspondre aux tokens d'un vrai tokenizer.

---

Que se passe-t-il si un nouveau prompt diverge au milieu d'une arête radix existante ? <!--anki:3664383234653336326238643466616662353233396564326536333038333131-->
?
Le moteur **scinde l'arête** à la frontière du préfixe commun. Si l'arbre contient `[S,A,B]` et reçoit `[S,A,F]`, il crée un nœud après `[S,A]`, puis deux chemins `[B]` et `[F]`.

Les états KV déjà calculés de `S,A` restent réutilisables ; scinder les métadonnées ne signifie pas recalculer ces tokens. Les références doivent néanmoins respecter les contraintes de pages de l'allocateur. Ce découpage rend possibles de futurs partages plus courts et plusieurs branches. Une divergence du troisième token n'invalide pas les deux premiers, si modèle, positions et périmètre de cache correspondent.

---

Pourquoi des tokens identiques au milieu de deux prompts ne suffisent-ils pas à partager leur KV cache ? <!--anki:3161633764316361323036363437333839626532646334623131633237366235-->
?
Dans un **Transformer causal**, l'état d'un token dépend de ses prédécesseurs à travers les couches. Le mot « Paris » après deux contextes différents peut donc produire des clés et valeurs différentes, même avec le même identifiant de token.

Le partage sûr porte sur un début identique dans un état compatible, pas sur une sous-chaîne trouvée ailleurs. Les positions, le modèle, l'adapter et les entrées multimodales comptent aussi. RadixAttention cherche cette identité de préfixe ; il ne rapproche pas des paraphrases. Un cache sémantique de réponses répond à une autre question et demande d'autres validations.

---

Comment les références protègent-elles un préfixe partagé pendant un decode ? <!--anki:6237343037376338656364363432313138393961666466383365363037653336-->
?
Une requête active **retient les références** aux blocs dont son attention a encore besoin. Une seconde requête peut retenir les mêmes blocs de préfixe, tout en allouant ses propres suffixes.

Quand une requête se termine, elle libère ses références ; les blocs ne doivent pas être recyclés tant qu'un autre lecteur les utilise. Sans lecteur actif, ils peuvent rester en cache, puis être évincés selon la politique. Partager des blocs ne donne pas le droit d'y écrire arbitrairement : une divergence requiert des états distincts, avec copie si un bloc partiellement partagé doit être modifié.

---

Calcul : combien de tokens KV distincts pour les prompts [S,A,B,C], [S,A,B,D,E] et [S,A,F] avec partage idéal ? <!--anki:3435306465323963653338383466303862623737613262323966303436353764-->
?
Sans partage, les longueurs totalisent `4 + 5 + 3 = 12` positions. L'arbre idéal conserve :
```text
[S A] : 2 positions partagées par les trois prompts
[B]   : 1 partagée par les deux premiers
[C]   : 1 ; [D E] : 2 ; [F] : 1
total = 7 positions KV distinctes
économie logique = 5 / 12 ≈ 41,7 %
```
Le calcul suppose compatibilité et partage exact, hors pages partiellement remplies, métadonnées et sorties nouvelles. Il mesure le stockage logique évité, pas une baisse identique du temps total : les suffixes calculent encore leur attention sur le préfixe et les réponses restent à générer.

---

Pourquoi changer la température ne rend-il pas forcément un préfixe KV inutilisable ? <!--anki:3463383939633963313663333462356638353665323263663561643365383238-->
?
La **température de sampling** agit sur les logits utilisés pour choisir une sortie ; elle ne change pas les représentations d'un préfixe fixé lorsque le modèle et son calcul restent identiques.

Deux requêtes peuvent donc partager le même préfixe puis générer des suites différentes. En revanche, ces nouvelles suites ne partagent leur cache que tant que leurs tokens coïncident exactement. Modifier poids, adapter, positions ou entrées change potentiellement les états et demande une séparation appropriée. La décision de partage dépend aussi des clés et règles du moteur ; ne pas confondre éligibilité mathématique et comportement effectivement configuré.

---

Pourquoi une longue correspondance de tokens ne suffit-elle pas toujours avec un cache hybride récent ? <!--anki:3239343937633630313830633432663039353766333038316331356132366262-->
?
Un moteur hybride peut conserver **plusieurs types d'état** : attention complète, fenêtre glissante ou état récurrent. La présence d'un chemin de tokens ne prouve pas que chaque composant possède encore l'état nécessaire à cette frontière.

Le cache unifié de SGLang recherche une frontière de réutilisation acceptée par tous les composants requis. Un composant évincé ou sans checkpoint peut raccourcir cette frontière. Les schémas simples d'arbre radix décrivent donc le cas classique, pas toutes les garanties d'un modèle hybride. Vérifier l'architecture et les compteurs de réutilisation effective avant de convertir une longueur commune en gain attendu.

---

Pourquoi un hit complet du prefix cache peut-il encore demander un peu de calcul ? <!--anki:3561343831646530616437323465633862333831653032383932363830303534-->
?
Un **cache KV** conserve des clés et valeurs, pas nécessairement les logits finaux ou la distribution du prochain token. Même si tout le prompt correspond, le moteur peut devoir rejouer sa dernière position ou utiliser un autre état conservé pour obtenir cette distribution.

Recherche du cache, contrôles de compatibilité, allocation et éventuel transfert ajoutent aussi du délai. « Tous les tokens étaient déjà connus » ne signifie donc pas TTFT nul. Vérifier ce que compte le moteur comme hit et comme token recalculé ; distinguer réutilisation des représentations, disponibilité des logits et émission du premier token.

---

Calcul : un cache ne partage que des blocs complets de 16 tokens. Deux prompts partagent exactement leurs 30 premiers tokens puis divergent. Combien de tokens peuvent-ils réutiliser selon cette règle ? <!--anki:3161306464643963313063623438326561303738653264613238313339313939-->
?
Un seul bloc complet appartient au préfixe commun : **16 tokens**. Les 14 suivants ne constituent pas un second bloc entièrement identique.

Ce calcul décrit une règle d'alignement donnée, pas tous les moteurs radix ou caches hybrides. Le préfixe textuel peut donc surestimer le travail réutilisable. Mesurer les tokens effectivement servis depuis le cache et distinguer correspondance logique, allocation physique et calcul évité.

---

Pourquoi faut-il invalider ou séparer le prefix cache lors d'un changement de poids ou d'adapter ? <!--anki:3365366634333865316139353433306362386365323563643562386563303538-->
?
Les K/V dépendent **du calcul du modèle**, pas seulement des identifiants de tokens. Un même prompt traité avec des poids différents ne produit généralement pas les mêmes états.

La clé et le périmètre du cache doivent distinguer les configurations qui changent ces états, dont l'adapter applicable. Tester une bascule de modèle avec cache chaud. Partager des préfixes entre variantes incompatibles peut produire des sorties erronées sans erreur de format visible.

---

## Mises en situation

Mise en situation : ton assistant multi-tours affichait 70 % de hits sur le prefix cache. Après une mise à jour, le taux tombe à 5 % et le TTFT double. Que cherches-tu ? <!--anki:7964774643443c5a3328-->
?
1. **Comparer les entrées tokenisées** avant et après mise à jour : début du prompt, template, outils, variables et ordre des documents.
2. **Vérifier la compatibilité du cache** : modèle, adapter, positions, sel et périmètre de partage.
3. **Examiner l'exploitation** : réplicas froids, routage, évictions et pression des séquences actives.
4. **Restaurer un préfixe stable si le sens le permet**, puis rejouer le même trafic avec et sans réutilisation.
5. **Mesurer tokens réutilisés et délais**, en distinguant file et calcul du suffixe.

**Piège** : déplacer les données dans le prompt pour maximiser le hit sans vérifier les effets sur la qualité ni la confidentialité.

---

Mise en situation : tu passes de 1 à 4 réplicas vLLM derrière un load balancer classique, et le TTFT se dégrade alors que tu as plus de GPU. Pourquoi ? <!--anki:6e67712c2325372c714e-->
?
1. **Tester l'hypothèse de dispersion** : les caches locaux se réchauffent séparément et le trafic peut perdre son affinité.
2. **Comparer les réplicas** : longueurs réutilisées, files, évictions et démarrage des poids.
3. **Évaluer un routage sensible au cache**, qui arbitre gain de prefill et délai d'attente.
4. **Tester l'équité et les frontières de partage**, sans concentrer les tenants sur une instance saturée.
5. **Étudier un cache hiérarchique ou partagé** seulement si les transferts et la coordination s'amortissent.

**Piège** : attribuer toute dégradation au cache sans éliminer stockage saturé, générateur de charge limité ou changement du mix de requêtes.

---

Mise en situation : ton service multi-clients partage un même modèle, et un client s'inquiète que ses prompts puissent fuiter via le cache. Que réponds-tu ? <!--anki:7542547e2e756e342652-->
?
1. **Décrire le risque** : un temps de réponse peut fournir un indice sur un préfixe deviné déjà présent, sans lecture directe du cache.
2. **Définir le groupe autorisé à partager** : utilisateur, tenant ou autre frontière de confiance justifiée.
3. **Imposer la séparation côté serveur**, avec clés de cache appropriées ou instances distinctes ; un client ne choisit pas le périmètre d'un voisin.
4. **Tester les autres états partagés** : médias, index, mémoire et journaux.
5. **Mesurer le compromis** entre confidentialité, hits et capacité, avec les mécanismes de la version déployée.

**Piège** : généraliser les engagements d'une API commerciale à tous ses produits, ou supposer qu'un hash de tokens constitue une autorisation.

---

## Sources

- [vLLM — automatic prefix caching et limites](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/)
- [SGLang — documentation du serveur et de ses optimisations](https://docs.sglang.io/)

- [vLLM — isolation du cache et sécurité](https://docs.vllm.ai/en/latest/usage/security/) — approfondissement ciblé du 12 novembre 2026 ; les exemples pédagogiques sont construits pour cette revue.

- [Zheng et al. — RadixAttention, mécanisme classique et références](https://arxiv.org/html/2312.07104v2) — revue ciblée du 12 novembre 2026 : arbre compressé, partage, éviction et ordonnancement.

- [SGLang — politiques d’éviction du cache radix](https://github.com/sgl-project/sglang/blob/main/docs/docs/advanced_features/radix_eviction_policy.mdx) — revue ciblée du 12 novembre 2026 : politiques actuelles, à distinguer du mécanisme classique.

- [SGLang — cache radix unifié](https://www.sglang.io/blog/unified-radix-cache) — revue ciblée du 12 novembre 2026 : frontière de réutilisation commune aux composants des modèles hybrides.

- Complément du 14 novembre 2026 — Blocs complets, divergence et identité du cache : [vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/design/prefix_caching/).

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — PagedAttention et prefix caching
- [[62-optimisations-inference|Optimisations d'inférence]] — prefill et decode
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM et SGLang
- [[82-routing-llm|Routing LLM]] — affinité de préfixe entre réplicas
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT et débit
- [[123-caching-agressif|Caching agressif]] — concevoir les prompts pour le cache
- [[137-long-contexte|Long contexte]] — limites et coût des longues fenêtres
- [[51-fine-tuning-adaptation|Fine-tuning]] — adapter un modèle, LoRA et QLoRA
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — ce qui limite chaque phase de l'inférence
- [[60-011-capacite-ordonnancement-inference|Capacité & ordonnancement]] — relier mémoire, budgets et débit utile sous charge
- [[60-013-prefill-decode-pas-a-pas|Prefill & decode pas à pas]] — suivre les positions calculées, le cache et les délais
- [[00-moc-ai-engineering|MOC AI Engineering]]
