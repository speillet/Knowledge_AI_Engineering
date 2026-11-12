# Capacité & ordonnancement de l’inférence LLM — Flashcards
Tags: #flashcards #ai-engineering #inference #capacity #scheduling #gpu
Vérifié le : 8 octobre 2026
<!-- summary: budgets de séquences et de tokens, mémoire KV réelle, GQA et sharding, préemption, admission, priorités, files, réplication et parallélismes, capacité de secours et annulation, réservation KV pour les sorties. -->


À ne pas confondre : limite de contexte, budget de batch et capacité KV ? <!--anki:3362373534643136313937303463623238346633646336363064366238343532-->
?
La **limite de contexte** borne la longueur d'une séquence ; le **budget de batch** borne le travail planifié pour une itération ; la **capacité KV** borne les états résidents en mémoire.

Dans vLLM, `max_model_len`, `max_num_batched_tokens` et `max_num_seqs` jouent des rôles différents : longueur par séquence, tokens planifiés et nombre de séquences. Aucun ne donne à lui seul le total de tokens déjà stockés. Un batch peut générer seulement 32 nouveaux tokens tout en conservant des centaines de milliers de tokens de contexte. Vérifier aussi les limites de la version et de l'architecture.

---

Comment régler ensemble max_num_seqs et max_num_batched_tokens ? <!--anki:6236383933626232323836333435393439313637633131646563633230363966-->
?
**`max_num_seqs`** borne les séquences traitées ensemble ; **`max_num_batched_tokens`** borne le travail en tokens d'une itération. Avec chunked prefill, ce budget se partage entre prefill et decode.

Exemple : autoriser beaucoup de séquences ne garantit pas leur admission si leurs KV saturent la mémoire. Augmenter seulement le budget de tokens peut accélérer le prefill mais rallonger les itérations et dégrader l'ITL.

Balayer les deux paramètres sur un mix fixe, puis sur des pointes réalistes. Retenir le meilleur **goodput sous SLO**, pas le maximum de tokens/s. Suivre TTFT, ITL, préemptions, refus et mémoire ; consigner les valeurs effectives et la version.

---

Comment calculer la mémoire KV d’un ensemble de requêtes actives ? <!--anki:3035346430336531636264653436306338323332653965663263373239653236-->
?
Pour une attention classique à K/V explicites :
```text
KV = 2 × couches × têtes_KV × dimension_tête × octets_par_valeur
     × somme des longueurs résidentes
```
Ajouter arrondi aux blocs, métadonnées et croissance des sorties ; soustraire les blocs réellement partagés une seule fois. Les requêtes en file sans état calculé ne consomment pas ce KV.

Ne pas appliquer mécaniquement cette formule aux architectures MLA, hybrides, à fenêtre glissante ou avec état récurrent : leur stockage diffère. Partir de la configuration et des allocations mesurées, puis vérifier le budget **par GPU** après poids, activations et graphes.

---

Calcul : avec 32 couches, 8 têtes KV de dimension 128 et BF16, sans partage ni surcoût, combien de séquences de 8 192 tokens tiennent dans 40 Gio de KV, puis si chacune doit encore générer 1 024 tokens ? <!--anki:3532326462613730363863393431666562613063613831666137623434363739-->
?
Hypothèses : 32 couches, 8 têtes KV, dimension 128, BF16, pas de partage ni de surcoût.
```text
octets/token = 2 × 32 × 8 × 128 × 2 = 131 072 = 128 Kio
KV/séquence = 8 192 × 128 Kio = 1 Gio
capacité mémoire idéale = 40 Gio / 1 Gio = 40 séquences
```
Les 8 192 tokens incluent le contexte déjà généré. Si chaque séquence doit encore produire 1 024 tokens, compter 1,125 Gio et au plus 35 séquences, avant marge. La capacité respectant les délais peut être inférieure à ce plafond mémoire.

---

Pourquoi GQA et le tensor parallelism ne divisent-ils pas toujours le KV comme prévu ? <!--anki:6562633831303763333161303431626638326462383633366439346333303435-->
?
**GQA** utilise moins de têtes K/V que de têtes de requête ; **MQA** n'en utilise qu'une. La taille KV dépend des têtes K/V et du schéma d'attention, pas seulement du nombre de paramètres.

Le tensor parallelism répartit ces têtes entre GPU, mais pas en dessous d'une tête par rang. Exemple : un modèle à 8 têtes KV servi en TP=16 réplique chaque tête sur deux rangs ; le KV par GPU ne baisse plus au-delà de TP=8. Ne pas diviser aveuglément la mémoire KV totale par le nombre de GPU : vérifier les blocs disponibles sur chaque rang. GQA est une propriété du modèle, pas un simple bouton du serveur.

---

Comment les préemptions peuvent-elles provoquer une spirale de surcharge ? <!--anki:6665383431303464626231633466626139646535336665333961356461393738-->
?
Un manque de KV peut interrompre des séquences. Si leur état est abandonné, la reprise **recalcule** une partie du préfixe ; d'autres moteurs ou configurations peuvent déplacer l'état vers une mémoire plus lente.

Exemple : une séquence interrompue à 6 000 tokens de contexte repasse 6 000 tokens en prefill à sa reprise. Ce travail retarde les nouveaux prompts, la file s'allonge et d'autres séquences manquent de KV à leur tour. Suivre préemptions et goodput en distinguant le recalcul des nouveaux tokens utilisateur. Réduire l'admission ou la concurrence, ou réserver davantage de KV. Une préemption occasionnelle n'est pas une panne ; leur répétition appelle une mesure ciblée.

---

Pourquoi borner une file d’inférence en travail et en délai ? <!--anki:6365313337636366326361353438663838353335336434326539313636613036-->
?
Le nombre de requêtes masque leur coût : un long prefill et une longue génération pèsent différemment. Estimer tokens d'entrée non cachés, budget de sortie et temps de service par classe, sans supposer un coût identique pour tous les tokens.

Utiliser taille de file, âge et échéance pour l'admission. Exemple : avec un délai de réponse de 10 s et 25 s de travail estimé devant elle, une demande interactive ne peut plus réussir ; la refuser tout de suite ou la passer en différé, selon une politique produit explicite. Les longueurs de sortie étant incertaines, garder une marge. Une file illimitée transforme la surcharge en réponses devenues inutiles.

---

Comment éviter qu’un scheduler favorise toujours les mêmes requêtes ? <!--anki:3537336661643663313932623430623761363664313164626264373131653061-->
?
Prioriser les tâches courtes ou les préfixes chauds peut améliorer le débit et la moyenne, mais faire attendre indéfiniment les longues demandes ou les caches froids.

Ajouter quotas par client, classes de service et **vieillissement des priorités** ; mesurer attente maximale, refus et conformité par segment. Exemple : un client envoie 5 000 requêtes batch d'un coup ; en FIFO, les utilisateurs interactifs attendent derrière toute la rafale. Un quota par client ou une file pondérée, deux tours pour l'interactif et un pour le batch, borne cette attente. Ne pas confondre une meilleure moyenne obtenue par sélection avec une amélioration pour chaque catégorie.

---

À ne pas confondre : réplication, tensor parallelism et pipeline parallelism ? <!--anki:3435316663353362616166613463613839656633323261313734616664306631-->
?
La **réplication** répartit les requêtes entre copies indépendantes, chacune devant pouvoir servir le modèle. Le **tensor parallelism** partage des opérations d'une couche ; le **pipeline parallelism** distribue les couches en étages.

Les deux derniers aident à faire tenir le modèle, avec communications ou bulles de pipeline. Ils ne garantissent pas une baisse de latence. Exemple : avec 8 GPU de 80 Go et 60 Go de poids, comparer quatre réplicas TP=2 et une instance TP=8. La première option isole les pannes et multiplie les caches ; la seconde offre plus de KV par requête, avec des collectives entre 8 GPU. Mesurer goodput et SLO sur le mix réel.

---

Qu’ajoute un modèle MoE au dimensionnement de l’inférence ? <!--anki:6639623562343139636334643461616138666331393639373064336565316437-->
?
Les paramètres **actifs par token** influencent le calcul, mais les experts à conserver ou déplacer déterminent aussi la mémoire et les transferts. Deux MoE avec le même nombre de paramètres actifs peuvent avoir des performances très différentes.

L'expert parallelism répartit les experts et introduit des échanges de tokens entre GPU. Exemple : si le routeur envoie 30 % des tokens d'un batch à deux experts placés sur le même GPU, ce rang finit en dernier et toute l'itération l'attend. Suivre la charge par expert et la dispersion entre rangs, sur les routes réellement produites par le trafic.

---

Calcul : un réplica soutient 12 requêtes/s sous SLO, avec capacité additive et équilibrage parfait. Combien en faut-il pour servir 40 requêtes/s après la perte d’un réplica ? <!--anki:3230353961333839616538333432343738386665633536663137383738373763-->
?
Si chaque réplica soutient **12 requêtes/s sous les mêmes SLO et le même mix**, il faut `(n − 1) × 12 ≥ 40`, donc **n ≥ 5**. Quatre suffisent arithmétiquement sans panne, mais seulement trois resteraient après perte, soit 36 requêtes/s.

C'est une borne sous hypothèses d'équilibrage et de capacité additive. Vérifier caches froids, dépendances communes, transferts et pointes ; si la capacité mesurée n'inclut pas la marge nécessaire, en ajouter. Une panne de nœud supprimant plusieurs réplicas demande un autre scénario.

---

Que mesurer lors du scale-out et du scale-in d’un service LLM ? <!--anki:3832626163623039653034373461313162313735366162323034383239373339-->
?
En **scale-out**, mesurer temps jusqu'au premier travail réellement servi : ressources disponibles, poids chargés, compilation, échauffement et cache encore froid. Si ce délai est de 6 minutes, un pic de 3 minutes ne se couvre que par une réserve déjà chaude ou une admission bornée.

En **scale-in**, retirer le réplica du routage, drainer les demandes et borner cette phase selon leurs délais. Les états KV locaux et l'affinité des sessions peuvent être perdus. Stabiliser les décisions d'autoscaling pour éviter une oscillation où les instances disparaissent avant d'amortir leur démarrage.

---

Pourquoi l’annulation fait-elle partie de l’optimisation de capacité ? <!--anki:3134313338356131303230623462336362613862363032373266353534643463-->
?
Après abandon, timeout ou choix d'une autre réponse, un moteur peut continuer à générer si l'annulation ne lui parvient pas. Il consomme alors calcul, KV et quota sans produire de valeur.

Exemple : un utilisateur ferme l'onglet après 2 s ; sans propagation, le moteur produit encore les 1 500 tokens prévus, soit 30 s d'une place de decode à 50 tokens/s. Propager un budget de temps et un signal d'annulation à travers application, gateway et serveur, puis mesurer les tokens produits après abandon. Une limite de sortie évite aussi les générations sans fin, mais sa réduction excessive augmente troncatures et reprises.

---

Pourquoi réserver seulement les tokens d'entrée sous-estime-t-il la capacité KV nécessaire ? <!--anki:3530333337623339643261663432313238653438316232343661303830626135-->
?
Le **KV cache grandit pendant la génération**. Admettre les séquences uniquement selon leur prompt peut saturer la mémoire quand elles produisent simultanément leurs sorties.

Estimer une enveloppe entrée plus sortie, selon les longueurs observées et les limites contractuelles, puis conserver une marge pour les autres allocations. Suivre préemptions, sorties longues et distribution par requête. Une réservation maximale partout peut être trop conservatrice ; choisir une politique d'admission mesurée, avec préemption ou refus explicites. La mémoire libre au début n'est pas une garantie de capacité jusqu'à la fin.

---

## Mises en situation

Mise en situation : augmenter la concurrence fait baisser le débit utile alors qu’il reste de la VRAM. Que vérifies-tu ? <!--anki:6231306139313863363538643466363462326464356634393062323236303362-->
?
1. **Distinguer VRAM allouée et KV occupé**, puis mesurer préemptions et mémoire par rang.
2. **Observer les itérations** : davantage de séquences peut ralentir decode et communications.
3. **Examiner le mix** : longs contextes, préfixes manquants, nouveaux formats ou images.
4. **Balayer les budgets** de séquences et de tokens avec SLO constants.
5. **Conserver le point utile** et une admission bornée, au lieu de remplir la mémoire à tout prix.

**Piège** : assimiler capacité mémoire disponible et capacité de service dans les délais.

---

Mise en situation : les prompts courts respectent le SLO, mais les documents longs attendent indéfiniment. Comment corriges-tu ? <!--anki:3030383438313232393336663431323239336637633565633937303062343563-->
?
1. **Segmenter** l'attente, les refus et le goodput par longueur et client.
2. **Identifier la priorité** : préférence aux requêtes courtes, aux decodes ou aux préfixes chauds.
3. **Ajouter une règle d'équité** : vieillissement, quota ou budget réservé aux longs prefills.
4. **Tester le compromis** : ITL des streams actifs, TTFT des nouveaux prompts et débit global.
5. **Séparer le batch** si son échéance permet un autre pool ou une autre file.

**Piège** : publier uniquement le p95 global et rendre invisibles les demandes jamais admises.

---

Mise en situation : deux GPU ont assez de VRAM au total, mais le serveur échoue sur une seule carte. Comment diagnostiques-tu ? <!--anki:6632353263653433623830623438323062353530386231303666303430323737-->
?
1. **Inspecter chaque rang** : poids, experts, KV, activations, graphes et autres processus.
2. **Vérifier le partage réel** : têtes KV répliquées, couches ou experts inégalement distribués.
3. **Reproduire le pic** avec longueurs, modalité et batch identiques.
4. **Adapter le placement ou les budgets**, puis tester qualité et latence.
5. **Mesurer la marge par carte** avant d'augmenter la charge.

**Piège** : diviser un total mémoire par deux sans vérifier ce que le runtime alloue réellement.

---

## Sources

- [vLLM — réglage du scheduler et préemptions](https://docs.vllm.ai/en/latest/configuration/optimization/)
- [vLLM — parallélisme et passage à l’échelle](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/)
- [PagedAttention — gestion et partage de mémoire](https://arxiv.org/abs/2309.06180)
- [GQA — têtes de requête et têtes KV](https://arxiv.org/abs/2305.13245)
- [Orca — ordonnancement à l’itération](https://www.usenix.org/conference/osdi22/presentation/yu)

## Connexions
- [[61-kv-cache-attention|KV cache]] — calculer les octets avant de dimensionner
- [[60-010-benchmarks-charge-inference|Benchmarks de charge]] — valider la capacité et les transitions
- [[66-prefix-caching-radix-attention|Prefix caching]] — équilibrer localité et attente
- [[116-sre-incidents-capacite-ia|SRE des services IA]] — réserve, incidents et politiques d’admission
- [[136-mixture-of-experts|Mixture of Experts]] — placement des experts et communications
- [[60-012-demarche-optimisation-inference|Démarche d’optimisation]] — prioriser et vérifier les gains sous contraintes de service
- [[00-moc-ai-engineering|MOC AI Engineering]]
