# Métriques d'inférence & SLO — Flashcards
Tags: #flashcards #ai-engineering #inference #slo #llm
<!-- summary: TTFT, TPOT et ITL, contenu utile et raisonnement, débits offert/admis/utile, SLO conjoints, timeouts, burn rate, loi de Little, autoscaling et benchmarks. -->


Qu'est-ce que le TTFT ? <!--anki:68355e7b7b31743d5d46-->
?
**Time To First Token** : délai entre l'envoi de la requête et le **premier token reçu**. Il dépend de la file d'attente et du **prefill** (longueur du prompt). C'est la réactivité perçue en streaming.

Préciser le point de mesure : le TTFT côté client inclut réseau et intermédiaires, celui du moteur peut les exclure. Le premier événement du protocole n'est pas nécessairement un token affichable. Un TTFT élevé peut venir d'une file saturée, d'un cache manquant ou du calcul d'entrée ; séparer ces composantes pour diagnostiquer.

---

À ne pas confondre : TPOT et ITL ? <!--anki:68424b38777e6e2a472f-->
?
Le **TPOT** est le temps moyen par token après le premier : `(durée − TTFT) / (tokens de sortie − 1)`, pour au moins deux tokens. L'**ITL** décrit les intervalles entre émissions successives ; sa granularité dépend de l'instrumentation.

Un TPOT de 30 ms peut cacher une longue pause. Le percentile des TPOT par requête diffère du percentile de tous les intervalles, auquel les réponses longues contribuent davantage. Un chunk réseau peut contenir plusieurs tokens. Exclure ou distinguer les sorties de zéro ou un token, et documenter la convention de l'outil.

---

Quels repères de latence viser selon l'usage ? <!--anki:6f5537494a4a4244263c-->
?
Les cibles dépendent de l'expérience attendue ; voici des **exemples de budgets à valider avec les utilisateurs** :
```text
autocomplétion       quelques centaines de millisecondes
voix interactive    viser une prise de parole rapide, autour d'une seconde
chat en streaming   premier texte en moins d'une seconde si possible
agent asynchrone    progression visible et délai de fin annoncé
batch               échéance de traitement, débit et coût prioritaires
```
Mesurer côté client, sous charge et en percentiles. La vitesse de lecture varie selon langue et contenu. Même en batch, la latence compte si le traitement doit finir avant une heure limite ([[144-ux-ia-human-in-the-loop|UX]]).

---

Comment se décompose la latence end-to-end ? <!--anki:797160634d527b2e5e4d-->
?
```text
latence E2E ≈ TTFT + TPOT × (nb tokens de sortie − 1)
```
Une réponse longue est donc dominée par le TPOT, une réponse courte sur un long prompt par le TTFT.

Avec un TTFT de 0,5 s, 101 tokens et un TPOT moyen de 0,03 s, la génération dure environ **3,5 s**. Cette formule suppose une mesure cohérente du premier au dernier token ; outils, rendu et traitements après génération s'ajoutent pour mesurer toute l'expérience applicative.

---

Qu'est-ce que le throughput d'un service d'inférence ? <!--anki:49216f726b2d6a6f292d-->
?
Le **débit** du service : **tokens de sortie par seconde** (tous utilisateurs confondus) ou **requêtes par seconde**. C'est lui qui détermine le **coût par token**.

Préciser quels tokens sont comptés : entrée, sortie ou les deux. Deux services au même nombre de requêtes par seconde peuvent avoir des charges très différentes si les réponses n'ont pas la même longueur. Le coût unitaire dépend aussi du prix de l'infrastructure, de son utilisation et de la part des réponses réellement exploitables.

---

Quel compromis entre latence et débit ? <!--anki:7a332c303b47545233-->
?
Un batch plus gros peut augmenter le **débit agrégé** en réutilisant les poids, mais chaque itération finit par coûter davantage et les attentes peuvent s'allonger. L'effet sur le TPOT n'est ni constant ni toujours monotone : il dépend du régime mémoire/calcul, des longueurs et du scheduler.

Balayer les charges et les budgets de batch. Retenir le débit utile maximal qui respecte les objectifs de latence et de qualité, avec une marge pour les variations de trafic. Inclure la file d'attente ; un moteur rapide derrière une file saturée reste lent pour l'utilisateur.

---

Qu'est-ce que le goodput ? <!--anki:4b7157417d2d3c3f7e39-->
?
Le débit **des seules requêtes qui respectent le SLO** (TTFT et TPOT sous les seuils). Plus honnête que le throughput brut : servir vite des requêtes hors SLO ne compte pas.

Définir précisément l'unité : requêtes réussies par seconde, ou tokens associés à ces requêtes, avec tous les critères applicables. Si 100 requêtes/s sont servies mais que seulement 70 respectent qualité et délai exigés, le débit utile est 70 requêtes/s selon cette définition. Comparer les variantes avec les mêmes seuils.

---

Pourquoi raisonner en percentiles pour la latence d'inférence ? <!--anki:4b306636786f4b446d71-->
?
Parce que la moyenne cache la **queue de distribution** : on fixe les SLO sur **p95/p99**. Un p50 excellent avec un p99 de 20 s reste une mauvaise expérience pour 1 % des utilisateurs.

Le p95 indique qu'environ 95 % des observations sont sous cette valeur, pas que toute requête aura ce délai. Définir fenêtre et segment de trafic, puis vérifier qu'il y a assez d'observations pour estimer la queue. Séparer prompts courts et longs aide à éviter qu'un changement de mix masque une régression.

---

À quoi ressemble un SLO d'inférence ? <!--anki:6b77706546525e735472-->
?
Un objectif chiffré sur une fenêtre de temps, par exemple :
```text
p95 TTFT < 800 ms, p95 TPOT < 50 ms, disponibilité ≥ 99,5 % sur 30 jours
```
Il pilote le dimensionnement, les [[83-gateway-ingress|timeouts et le rate limiting]].

Préciser quelles requêtes entrent dans le calcul, comment traiter erreurs et annulations, et où les temps sont mesurés. Définir aussi le budget d'erreur et les alertes qui déclenchent une action. Les valeurs ci-dessus sont un exemple de contrat produit ; elles ne constituent pas une norme valable pour tous les usages.

---

Qu'est-ce qui limite la concurrence d'un serveur ? <!--anki:4e7d7c3d6a4c3c4f5f3b-->
?
Surtout la **VRAM disponible pour le [[61-kv-cache-attention|KV cache]]** : chaque requête active y occupe une place proportionnelle à son contexte. Quand le cache est plein, les requêtes **attendent en file** ou sont préemptées.

Prévoir la croissance des sorties et les allocations temporaires, pas seulement les prompts déjà présents. Un serveur peut aussi manquer de bande passante ou dépasser le SLO avant de remplir la VRAM. Une limite de concurrence associée à une file bornée évite d'accepter une quantité de travail impossible à terminer dans le délai attendu.

---

Quels signaux utiliser pour l'autoscaling d'un serveur d'inférence LLM ? <!--anki:6e46644e3e766a2e4a7d-->
?
Combiner **attente du plus ancien travail**, taille de file, tokens restant à traiter, occupation KV, préemptions et respect du SLO. Dix longs prompts ne représentent pas la même charge que dix messages courts.

L'activité GPU complète le diagnostic ; seule, elle ne distingue pas les goulots. Calibrer les seuils par modèle et mix de trafic, anticiper chargement des poids et échauffement, puis vérifier la readiness réelle. Conserver une réserve adaptée aux pics et drainer les requêtes avant réduction du nombre de réplicas. Tester aussi la perte d'un réplica.

---

Comment mesurer les performances d'un déploiement d'inférence LLM ? <!--anki:505e777663703b53257c-->
?
Par des **benchmarks de charge** réalistes (distribution des longueurs de prompt/sortie, taux d'arrivée) : `vllm bench serve`, **GuideLLM**, **genai-perf** (NVIDIA). On trace la **courbe latence vs débit**.

Inclure un échauffement, les erreurs, le cache froid ou chaud et les pointes de charge. Un test à taux d'arrivée imposé montre comment la file grossit lorsque le service sature. Reporter les hypothèses et la distribution du trafic avec les résultats pour que la comparaison entre configurations soit reproductible.

---

Calcul : combien de requêtes simultanées faut-il servir pour 10 requêtes/s qui durent 8 secondes ? <!--anki:44597b556d555a6b6b32-->
?
**Loi de Little** en régime stable, avec débit et durée mesurés au même périmètre :
```text
L = λ × W = 10 req/s × 8 s = 80 requêtes en vol en moyenne
```
Si les 8 secondes incluent l'attente, ces 80 requêtes comprennent **file et exécution**. Cela ne signifie pas 80 séquences actives en GPU, ni une réservation KV déterminée.

Dimensionner séparément la mémoire des tokens effectivement résidents, leur croissance et les blocs partagés. Cette relation porte sur des moyennes ; elle ne fournit ni concurrence p99, ni marge de capacité, ni garantie de délai en surcharge.

---

À ne pas confondre : débit offert, admis, terminé et utile ? <!--anki:3666356538323836666565633432333239346636646538626530383234313834-->
?
Le **débit offert** compte les demandes arrivant au périmètre choisi ; l'**admis**, celles acceptées ; le **terminé**, celles ayant atteint un état final ; le **goodput**, les réussites satisfaisant les critères fixés.

Suivre aussi refus, abandons et évolution du nombre de requêtes en vol. Un serveur peut afficher une excellente latence après avoir rejeté la moitié des demandes. Compter séparément tentatives techniques et tâches utilisateur : trois retries ne créent pas trois tâches réussies. Conserver le même périmètre et la même fenêtre pour comparer les configurations.

---

Calcul : deux critères respectés chacun par 95 % des requêtes garantissent-ils 95 % de conformité conjointe ? <!--anki:3766323866373230643236353432626339323037616335643366326434643963-->
?
Non. Sur 1 000 requêtes, 50 peuvent rater le TTFT et **50 autres** le TPOT : seules 900 respectent les deux, soit **90 %**. Si les deux groupes d'échecs coïncident, le résultat est 95 %.

Mesurer l'intersection **par requête**, avec succès technique et qualité lorsque cette dernière est observable. Si ces 1 000 requêtes arrivent en 100 secondes en régime stable, et que 900 sont conformes, le goodput vaut 9 requêtes/s. Des histogrammes marginaux ne suffisent pas à reconstruire cette intersection.

---

Quel délai mesurer quand un modèle raisonne avant de répondre ? <!--anki:3465373330633361393930363435363139323162313330633838623137333461-->
?
Distinguer **premier événement**, premier token généré ou reçu, **premier contenu utile visible**, et réponse terminée. Nommer explicitement le délai au premier contenu utile, par exemple TTFU dans le contrat local : ce sigle n'est pas une convention universelle.

Un événement de métadonnées ou un raisonnement masqué ne satisfait pas nécessairement l'attente de l'utilisateur. Suivre séparément tokens visibles, tokens de raisonnement exposés dans l'usage et tokens facturés ; les conventions varient. Une réponse courte à l'écran peut consommer beaucoup de calcul et arriver tard.

---

Comment compter les timeouts et annulations dans les métriques de latence ? <!--anki:3038353239383363653338613432633638363964326533626637666331363136-->
?
Un timeout est un **résultat inachevé**, pas une latence de réussite égale au seuil. Publier sa fréquence et son temps observé séparément ; la durée qu'aurait exigée une réponse complète reste inconnue.

Garder ces demandes dans le dénominateur du SLO selon le contrat. Distinguer abandon volontaire, délai dépassé, rejet et déconnexion après erreur. Les percentiles des seules réussites peuvent s'améliorer quand les demandes les plus lentes échouent. Vérifier aussi que l'annulation libère réellement calcul et KV, sinon la charge continue malgré la disparition du client.

---

Calcul : quel burn rate pour 4 % de violations avec un SLO à 99 % ? <!--anki:3832346261303930623339333434316638626232646663323934326266663865-->
?
Le budget autorisé est **1 %** d'événements non conformes. Un taux observé de 4 % donne `4 / 1 = 4` : consommation quatre fois plus rapide que le rythme compatible avec l'objectif, à trafic et périmètre comparables.

Ce calcul utilise les événements éligibles, y compris les erreurs prévues au contrat, pas la valeur du p95. Combiner fenêtres courte et longue pour distinguer incident rapide et dégradation persistante. Le temps jusqu'à épuisement dépend du budget restant et du trafic futur ; il ne se déduit pas du seul ratio.

---

## Mises en situation

Mise en situation : le produit demande « une réponse en moins de 2 secondes » pour un assistant qui streame des réponses de 400 tokens. Comment traduis-tu ce besoin en SLO ? <!--anki:772b352d2f4c5b694141-->
?
1. **Clarifier le délai** : premier texte utile ou réponse entièrement disponible, côté utilisateur.
2. **Calculer le budget** : avec 800 ms de TTFT et 400 tokens, finir en 2 s demande un TPOT moyen au plus égal à `(2 − 0,8) / 399 ≈ 3 ms`.
3. **Évaluer les leviers** : sortie plus concise, modèle plus rapide, speculative decoding ou infrastructure ; valider qualité et coût.
4. **Définir le contrat** : proportion de requêtes respectant ensemble les seuils, fenêtre, erreurs et segments.
5. **Tester sous charge** avant de promettre ces délais.

**Piège** : additionner des percentiles comme s'ils décrivaient une même requête.

---

Mise en situation : ton dashboard affiche 100 % d'utilisation GPU et l'équipe conclut qu'il faut acheter des GPU. Comment vérifies-tu ? <!--anki:4a3363746c6836453d3b-->
?
1. **Interpréter l'activité** : un kernel en cours ne signifie pas que calcul ou mémoire atteignent leur débit maximal.
2. **Localiser le goulot** : files, KV, préemptions, temps par phase, activité mémoire et communications.
3. **Tracer la courbe de charge** avec latences, erreurs et goodput au même mix de requêtes.
4. **Tester un levier ciblé** : batch, cache, quantization ou contexte ; mesurer ses contreparties.
5. **Dimensionner la réserve** selon pics attendus, démarrage, panne et politique d'admission.

**Piège** : traiter un percentile de trafic comme une règle universelle de capacité, ou promettre des optimisations sans coût ni risque qualité.

---

Mise en situation : ton autoscaling se déclenche trop tard, et des requêtes attendent plusieurs secondes avant d'être traitées. Sur quoi le règles-tu ? <!--anki:6c6759312a4c4c493574-->
?
1. **Anticiper** avec âge de file, travail en tokens, occupation KV et tendance de charge.
2. **Mesurer le démarrage réel** : chargement, compilation, échauffement, puis readiness.
3. **Garder une réserve** cohérente avec ce délai et les pointes à absorber.
4. **Borner la file** et appliquer une dégradation prévue si les requêtes ne peuvent plus tenir leur échéance.
5. **Alerter sur le burn rate** : fraction de requêtes violant le SLO divisée par le budget d'erreur autorisé.

**Piège** : calculer un « burn rate du p95 ». Un percentile n'est pas une fraction d'événements défaillants.

---

## Sources

- [Google SRE — alertes et budgets d’erreur](https://sre.google/workbook/alerting-on-slos/)
- [vLLM — définitions des métriques](https://docs.vllm.ai/en/latest/design/metrics/)
- [DistServe — goodput et SLO conjoints](https://arxiv.org/abs/2401.09670)

## Connexions
- [[61-kv-cache-attention|KV cache]] — la concurrence plafonnée par la VRAM
- [[62-optimisations-inference|Optimisations d'inférence]] — les leviers sur TTFT et TPOT
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — autoscaling piloté par ces signaux
- [[83-gateway-ingress|Ingress & API gateway]] — rate limiting et timeouts
- [[91-langfuse-observabilite|Langfuse]] — du système à l'application
- [[121-couts-inference|Coûts d'inférence]] — goodput ↔ coût par token
- [[67-speculative-decoding|Speculative decoding]] — réduire le TPOT
- [[68-quantization|Quantization]] — plus de débit et de concurrence par GPU
- [[93-monitoring-inference|Monitoring de l'inférence]] — les métriques concrètes (vLLM, GPU, usage)
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — l'interférence prefill/decode derrière les pics de TPOT
- [[163-voix-temps-reel|Voix & agents temps réel]] — le TTFT dans un budget de latence conversationnel
- [[112-cicd-modeles|CI/CD des modèles]] — eval gates, canary et rollback
- [[138-modeles-raisonnement|Modèles de raisonnement]] — test-time compute et budget de réflexion
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — timeouts, retries, fallbacks et dégradation
- [[66-prefix-caching-radix-attention|Prefix caching]] — réutiliser le calcul des préfixes communs
- [[81-litellm-api-layer|LiteLLM]] — la gateway entre applications et modèles
- [[82-routing-llm|Routing LLM]] — choisir le modèle par requête, fallbacks et cache sémantique
- [[84-streaming-integration-applicative|Streaming & intégration]] — SSE, annulation et tâches longues
- [[137-long-contexte|Long contexte]] — limites et coût des longues fenêtres
- [[146-choix-modeles|Choix de modèles]] — critères, benchmarks et migration
- [[116-sre-incidents-capacite-ia|SRE : incidents & capacité des services IA]] — relier capacité et expérience utilisateur
- [[60-010-benchmarks-charge-inference|Benchmarks de charge LLM]] — mesurer la capacité sans masquer files et échecs
- [[00-moc-ai-engineering|MOC AI Engineering]]
