# Prefill & decode — Exécution pas à pas — Flashcards
Tags: #flashcards #ai-engineering #inference #prefill #decode #attention #kv-cache
Vérifié le : 12 novembre 2026 — mécanismes du Transformer causal et ordonnancement documenté ; les calculs sont pédagogiques.
<!-- summary: positions connues et masque causal, projections Q/K/V, premier token, chronologie du cache, coût de l'attention, prefill partiel, mémoire temporaire, batching, chunked prefill, transfert KV et diagnostic de latence, logits du prochain token, masquage du padding. -->


Que fait exactement une passe de prefill sur quatre tokens connus ? <!--anki:3831643765326339613135663432333761376634353336326166366334353465-->
?
Pour un **Transformer causal decoder-only**, le prefill transforme les quatre tokens du prompt en états internes, couche après couche. Chaque couche calcule notamment projections d'attention, attention masquée et bloc MLP ; les résidus et normalisations participent aussi au résultat.

Les clés et valeurs des quatre positions sont conservées pour les étapes suivantes. L'état final de la dernière position passe par la tête de sortie pour obtenir les logits du prochain token. Le prefill n'apprend pas les poids et ne rédige pas quatre nouveaux tokens : il traite quatre entrées déjà connues pour préparer la continuation.

---

Pourquoi les positions du prompt peuvent-elles être calculées ensemble sans connaître les prochains tokens générés ? <!--anki:3661613834333137373535383462373438633032326566333332343263373534-->
?
Les **tokens d'entrée sont déjà fixés** : le modèle connaît leur identité avant le calcul. Dans une couche, leurs projections et interactions autorisées peuvent être exprimées en opérations matricielles, avec un masque causal.

Le token de position trois ne lit pas celui de position quatre, même si les deux sont calculés dans la même passe. Les couches restent successives : la suivante consomme les états de la précédente. En génération ordinaire, le prochain token n'est pas encore choisi ; on doit le sélectionner avant de le fournir à l'étape suivante. Parallélisme des positions connues et dépendance des sorties sont compatibles.

---

Comment lire le masque causal du prefill pour quatre positions ? <!--anki:6230316461313530623965353434313061396233396233333065376430323866-->
?
La **ligne** représente la position qui interroge ; la **colonne** la position consultée. Un masque causal autorise le passé et la position courante, selon la convention standard illustrée :
```text
           clés : x1 x2 x3 x4
requête x1        ✓  ×  ×  ×
requête x2        ✓  ✓  ×  ×
requête x3        ✓  ✓  ✓  ×
requête x4        ✓  ✓  ✓  ✓
```
Les scores interdits sont exclus du softmax ; les poids autorisés de chaque ligne sont normalisés. Il existe dix couples autorisés ici, soit `4×5/2`. Cette matrice pédagogique décrit l'attention causale dense ; fenêtres glissantes ou masques spécialisés changent les connexions et les besoins de cache.

---

Que représentent Q, K et V pendant le prefill d'une couche d'attention ? <!--anki:6239633438616530346163323430633562353166643536623236346262303761-->
?
À partir des états `H` de la couche, des **projections apprises** produisent les requêtes `Q`, clés `K` et valeurs `V`. Une requête compare ses caractéristiques aux clés autorisées pour pondérer les valeurs.
```text
scores = Q × Kᵀ / √dimension_de_tête + masque
sortie = softmax(scores) × V
```
C'est un schéma par tête ; les architectures multi-têtes ou GQA précisent les dimensions et partages. Les K/V ne sont ni le texte brut ni les poids du modèle : ce sont des états dérivés de cette entrée. Les conserver évite de recalculer la représentation du passé aux étapes suivantes.

---

Pourquoi conserver K et V plutôt que toutes les anciennes requêtes Q pour le decode ? <!--anki:6539376364303364353337663434633339626336393065363164376238616136-->
?
À une nouvelle position, le modèle calcule **sa propre requête Q** pour interroger les clés du contexte et combiner leurs valeurs. Les anciennes Q ont déjà servi à construire les états des anciennes positions ; elles ne sont pas nécessaires à cette nouvelle interrogation standard.

Les K/V restent utiles à chaque couche pour les positions encore accessibles. Le cache doit donc conserver plusieurs niveaux d'état, pas seulement une paire de matrices à la dernière couche. Des architectures particulières peuvent utiliser d'autres caches ; ce raisonnement porte sur l'attention causale classique. Il n'élimine ni les projections du nouveau token ni la lecture du passé.

---

D'où vient le tout premier token de sortie après le prefill ? <!--anki:3664356139383039343138393434346661356237343537393333376434353639-->
?
L'état de la **dernière position du prompt** est projeté vers les logits du vocabulaire. Sampling ou choix greedy sélectionne ensuite le premier token de sortie.

Après `[A,B,C]`, les logits de C proposent D ; traiter D permet ensuite de proposer E. Le KV du token choisi n'est calculé que lorsqu'il est traité comme entrée. Il n'y a donc pas systématiquement une passe supplémentaire avant de sélectionner le premier token.

Distinguer prompt encodé, distribution calculée et token sélectionné. Avec un prefix cache intégral, des K/V seules peuvent ne pas suffire à retrouver les logits finaux sans un peu de recalcul.

---

Comment évolue le cache pour un prompt de quatre tokens suivi de trois tokens générés ? <!--anki:3537323435386263383538363466376162323661626562666534323963316439-->
?
Dans une exécution standard simplifiée, hors EOS et optimisations, le calcul suit cette chronologie :
```text
prefill : traiter x1 x2 x3 x4 → KV longueur 4 → émettre y1
decode 1 : traiter y1          → KV longueur 5 → émettre y2
decode 2 : traiter y2          → KV longueur 6 → émettre y3
```
Émettre un token et calculer son état KV sont deux moments distincts. Si la génération s'arrête après `y3`, il n'est pas nécessaire de le traiter pour prédire un hypothétique `y4`. Les moteurs peuvent regrouper ou décaler certaines opérations ; suivre positions effectivement calculées et tokens émis permet d'interpréter leurs compteurs.

---

Que recalcule le decode malgré la présence du KV cache ? <!--anki:3532616138366364353164613431323138663837326339373865346137323435-->
?
Pour chaque nouvelle position, le **decode** traverse encore les couches : projections du nouveau token, attention sur le contexte accessible, MLP, normalisations et sortie vers le vocabulaire. Il ajoute les K/V de cette position.

Le cache évite de refaire toutes ces opérations pour les anciennes positions. Il ne rend pas gratuits les poids à lire ni l'attention sur le passé. À faible batch, le transfert des poids peut dominer ; avec un contexte très long, la lecture KV pèse davantage. Mesurer ces composantes explique pourquoi un préfixe réutilisé accélère l'entrée sans supprimer le coût des tokens de sortie.

---

Pourquoi le coût du prefill dense ne se résume-t-il pas à un coût constant par token ? <!--anki:3863653037643065383761633465356238643931396637306139396632636631-->
?
Les **projections et MLP** ont un travail qui croît approximativement avec le nombre de positions traitées, pour une architecture fixée. L'**attention dense** relie en plus des paires de positions : son nombre d'interactions croît quadratiquement avec la longueur du prompt.

Par couche, un repère schématique est `O(L×d²)` pour les projections et `O(L²×d)` pour l'attention, avec des constantes et variantes architecturales. Doubler `L` ne multiplie donc pas universellement toute la latence par deux ou quatre. FlashAttention réduit les transferts et la mémoire intermédiaire ; il ne supprime pas ces interactions de l'attention dense.

---

Pourquoi les nouveaux tokens d'un prefill doivent-ils encore lire un préfixe réutilisé ? <!--anki:3165376365623130613338643432666239386462396236306363663232363036-->
?
Leur **attention dépend du passé**. Réutiliser les K/V de `M` positions évite leur recalcul, mais chacune des `S` nouvelles positions peut encore interroger ce préfixe.

Pour une attention causale dense, le nombre d'interactions à traiter pour le suffixe suit schématiquement `S×M + S×(S+1)/2`, au lieu de recalculer toutes les interactions des `M+S` positions. Les projections et MLP des nouvelles positions restent également nécessaires. Un très long préfixe n'est donc pas gratuit après un hit : il continue d'occuper mémoire et bande passante. Comparer travail évité, travail restant et chargement éventuel du cache.

---

Calcul : un prompt neuf de 80 000 tokens est traité à 20 000 tokens/s, avec 0,5 s de file et 0,1 s d'autres délais. Quel TTFT simplifié ? <!--anki:6265366464396666333831353439383361356466656466396135663761326631-->
?
Sous l'hypothèse d'un débit de prefill effectivement soutenu sur ce prompt :
```text
prefill = 80 000 / 20 000 = 4 s
TTFT simplifié = 0,5 + 4 + 0,1 = 4,6 s
```
Ce n'est pas une loi universelle de débit : longueur, batch et matériel peuvent changer les tokens/s. Les 0,1 s regroupent ici les autres délais annoncés, y compris ce qui est nécessaire à l'émission observée. Pour comparer une optimisation, conserver la même définition du premier token utile et mesurer séparément file, calcul et transport. Un hit de cache change le travail réellement calculé, pas la taille logique affichée du prompt.

---

Pourquoi un prefill peut-il échouer en mémoire alors que les poids et le KV final semblent tenir ? <!--anki:6433633366323339363530633435353861393835363835616533393634613937-->
?
Le **pic de mémoire** comprend aussi activations temporaires, buffers de kernels, logits éventuels et opérations de communication. La somme poids plus KV final ne décrit pas nécessairement ce maximum pendant le traitement d'un long prompt.

Vérifier le profil mémoire pendant l'exécution et les allocations réservées par le moteur. Chunked prefill, kernels adaptés ou limites d'admission peuvent réduire certains pics ; ils ne diminuent pas tous les poids ni le KV persistant. Une erreur de RAM hôte au chargement est encore un autre problème. Identifier où la panne survient avant de réduire arbitrairement la précision du modèle.

---

À ne pas confondre : parallélisme des positions d'un prefill et batching de plusieurs requêtes ? <!--anki:6437613033303537393361633436653738646361636330623538613966616365-->
?
Le premier concerne les **positions connues d'une même séquence** ; le second regroupe le travail de **séquences différentes** pour utiliser le matériel. Les deux peuvent coexister dans une même exécution.

Les séquences d'un batch doivent rester isolées par leurs tables d'état et leurs masques. Leurs longueurs influencent padding, scheduling et mémoire ; une seule très longue entrée peut changer le compromis. Le continuous batching fait évoluer le groupe au fil des itérations. Mesurer tokens traités, séquences actives et délais séparément : « batch de huit » ne dit ni combien de positions sont calculées ni combien de mémoire KV elles occupent.

---

Pourquoi le chunked prefill ne doit-il pas traiter chaque morceau comme un document indépendant ? <!--anki:6633343438633064363535323461343762633530623331633134363665613536-->
?
Un **chunk de prefill** est une partie d'une même séquence causale. Les morceaux suivants doivent retrouver positions et K/V calculées pour les précédents, afin de poursuivre le même calcul logique.

Réinitialiser le cache ou repartir à la position zéro à chaque morceau change le contexte et donc le modèle exécuté. Ce découpage d'ordonnancement n'est pas le chunking RAG qui crée des unités de recherche indépendantes. Il permet d'intercaler d'autres travaux entre morceaux, avec un coût de coordination. Vérifier stabilité du résultat selon les tolérances numériques et comparer TTFT des nouvelles entrées et pauses des générations déjà actives.

---

Calcul : un budget d'itération de 2 048 tokens réserve 48 positions au decode. Combien d'itérations idéales pour un prefill de 6 000 tokens ? <!--anki:6466396437393938376637633431353062396163633138623662396339386236-->
?
Il reste `2 048 − 48 = 2 000` positions de prefill par itération. Le prompt exige donc `6 000 / 2 000 = 3` itérations dans ce scénario.

Supposer budget et 48 decodes inchangés, aucune autre admission ni overhead. Ce sont des **positions calculées à cette itération**, pas une limite de 2 048 tokens sur tout le KV résident. Les séquences en decode peuvent déjà avoir chacune des milliers de tokens en mémoire. Des arrivées, fins de requêtes ou préemptions changent le partage réel ; le calcul sert à distinguer budget de travail et capacité de cache.

---

Quel état doit passer du prefill au decode dans une architecture désagrégée ? <!--anki:3630333939386138613931343463386339623562333266616137376561626233-->
?
Le pool de decode doit retrouver les **K/V nécessaires à chaque couche**, leurs positions et les métadonnées de séquence, dans une représentation compatible avec sa cible. Selon le protocole, il récupère aussi ou recalcule ce qui permet de poursuivre le sampling.

Poids, adapter, tokenizer, positions, précision du cache et disposition des tenseurs doivent correspondre. Le fait d'utiliser le même nom commercial de modèle ne valide pas tout ce contrat. Mesurer transfert, allocation et synchronisation en plus du calcul. Le découplage peut réduire les interférences entre phases, mais ajoute une frontière distribuée à tester en charge et lors des pannes.

---

Calcul : 8 192 positions à 128 Kio de KV chacune traversent un lien de 32 Gio/s. Quel temps de transfert idéal ? <!--anki:3231653764653831656134633464633839386262353239333434393662303930-->
?
Le volume vaut `8 192 × 128 Kio = 1 048 576 Kio = 1 Gio`. À débit utile constant de 32 Gio/s, le temps vaut `1/32 s`, soit **31,25 ms**.

Cela exclut sérialisation, protocole, allocations, contention et synchronisation ; le transfert réel peut prendre davantage. Utiliser les mêmes unités binaires au numérateur et au dénominateur. La concurrence peut saturer le lien même si un transfert isolé est rapide. Comparer ce coût à l'interférence évitée et au calcul disponible : déplacer un gigaoctet n'est pas gratuit, même si le KV est déjà calculé.

---

Quels compteurs distinguer pour évaluer une optimisation du prefill ? <!--anki:3232616133373138356634393433353062623535343765323836333139626230-->
?
Séparer **tokens logiques reçus**, **tokens KV réellement réutilisés** et **positions effectivement calculées**, puis relier ces volumes au temps de calcul, à l'attente et au TTFT.

Un moteur servant beaucoup de tokens depuis le cache peut afficher un débit logique élevé sans avoir effectué autant de projections nouvelles. C'est un gain réel si les requêtes respectent le contrat, mais une comparaison de kernels doit isoler leur travail. Garder mix de longueurs, charge et état froid ou chaud identiques. Vérifier les définitions de compteurs et leurs frontières : un token rejoué pour récupérer les logits ne se compte pas comme une entrée utilisateur supplémentaire.

---

Comment distinguer une lenteur de prefill d'une lenteur de decode sur un cas concret ? <!--anki:6333643130383931373437353430336562303861303166356364623561306264-->
?
Comparer d'abord **temps avant première sortie utile** et **cadence après cette sortie**, puis décomposer l'attente. Si le délai croît fortement avec le prompt et le calcul d'entrée domine, examiner prefill, contexte et réutilisation du KV.

Si le premier token arrive vite mais les suivants tardent, examiner decode, contexte lu, batch et éventuelle spéculation. Une file peut ralentir les deux et une sortie de raisonnement cachée peut retarder l'information utile. Utiliser traces et tests contrôlés ; une seule mesure de durée totale ne permet pas d'attribuer la cause ni de choisir entre RadixAttention et speculative decoding.

---

Pourquoi le padding d'un batch de prefill ne doit-il pas devenir une preuve dans l'attention ? <!--anki:3632343765333864346336653433633739336566646366373338353431393736-->
?
Les tokens de remplissage servent à **aligner les formes**, pas à ajouter du contenu. Le masque d'attention et la gestion des positions doivent empêcher qu'ils modifient le sens des entrées utiles.

Vérifier les conventions du modèle et du moteur, notamment padding gauche/droite et sélection de la dernière position utile. Un test pertinent compare une requête seule et dans un batch avec longueurs différentes, en tolérant les variations numériques attendues.

---

## Mises en situation

Mise en situation : un prompt de 60 000 tokens provoque des pauses dans les streams des utilisateurs déjà en génération. Comment enquêtes-tu ? <!--anki:3636653435353836626564653434633338646334626631616634643061626463-->
?
1. **Corréler les pauses** avec les admissions de longs prompts, sans confondre buffering réseau et calcul.
2. **Mesurer le scheduler** : budget de tokens, taille des prefills et priorité des decodes.
3. **Tester le chunked prefill** sur le même mix, en suivant ITL des flux et TTFT des longs prompts.
4. **Vérifier mémoire et équité** : pics temporaires, préemptions et attente des entrées sans cache.
5. **Comparer le goodput** avant de retenir le réglage ; envisager la désagrégation si le coût des transferts reste acceptable.

**Piège** : réduire les chunks jusqu'à rendre la sortie fluide mais le premier token des documents longs excessivement tardif.

---

Mise en situation : le prefix cache retrouve 95 % du prompt, mais le premier token reste lent. Que mesures-tu avant d'augmenter le cache ? <!--anki:6562653438646439393464383434313661326532666232333731373833346632-->
?
1. **Lire la définition du hit** : tokens, blocs ou requêtes, et réutilisation réellement disponible sur le réplica choisi.
2. **Décomposer le délai** : file, préparation, transfert KV, calcul du suffixe et transport.
3. **Vérifier l'attention restante** : les nouvelles positions consultent encore le long préfixe.
4. **Tester à charge comparable**, avec préfixe chaud puis froid et mêmes suffixes.
5. **Agir sur le composant dominant**, pas seulement sur la taille du cache.

**Piège** : convertir 95 % de tokens réutilisés en promesse de TTFT divisé par vingt, alors qu'attente et accès au passé restent présents.

---

Mise en situation : séparer les GPU de prefill et decode améliore l'ITL mais dégrade le TTFT. Comment décides-tu ? <!--anki:3331616336373933346338623436616338326537306531393038663562343633-->
?
1. **Mesurer les étapes ajoutées** : transfert KV, allocation, admission du pool de decode et synchronisation.
2. **Comparer aux interférences évitées**, sur les mêmes longueurs et niveaux de charge.
3. **Vérifier le lien partagé** avec plusieurs transferts simultanés et les distributions de délai.
4. **Évaluer les SLO conjoints** : première réponse utile, pauses du stream, qualité et coût par tâche.
5. **Conserver ou ajuster l'architecture** selon l'objectif produit ; un pool moins saturé ne prouve pas une meilleure expérience complète.

**Piège** : valider uniquement les performances isolées de chaque pool en oubliant le passage entre les deux.

---

## Sources

- [Vaswani et al. — Attention Is All You Need](https://arxiv.org/abs/1706.03762) — projections, masque causal et architecture ; les architectures actuelles peuvent différer du Transformer original.
- [vLLM — optimisation, chunked prefill et priorités d'ordonnancement](https://docs.vllm.ai/en/latest/configuration/optimization/)
- [vLLM — désagrégation prefill/decode](https://docs.vllm.ai/en/latest/features/disagg_prefill/)
- [Dao et al. — FlashAttention](https://arxiv.org/abs/2205.14135) — interactions d'attention et transferts mémoire.
- [SGLang — RadixAttention, article fondateur](https://arxiv.org/abs/2312.07104) — réutilisation des K/V et travail restant sur le suffixe.

## Connexions
- [[61-kv-cache-attention|KV cache]] — taille et allocation de l'état conservé
- [[62-optimisations-inference|Optimisations d'inférence]] — choisir les leviers de calcul et d'ordonnancement
- [[64-metriques-slo-inference|Métriques & SLO]] — mesurer première sortie utile et cadence
- [[66-prefix-caching-radix-attention|RadixAttention]] — réutiliser le début exact du prompt
- [[67-speculative-decoding|Speculative decoding]] — accélérer les sorties après traitement de l'entrée
- [[69-roofline-prefill-decode|Roofline]] — interpréter les goulots de calcul et de mémoire
- [[131-transformer-architecture|Transformer]] — composants et attention causale
- [[00-moc-ai-engineering|MOC AI Engineering]]
