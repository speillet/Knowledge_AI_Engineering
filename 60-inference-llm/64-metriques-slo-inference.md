# Métriques d'inférence & SLO — Flashcards
Tags: #flashcards #ai-engineering #inference #slo #llm
<!-- summary: TTFT, TPOT, throughput, goodput, percentiles, définition d'un SLO, calcul de concurrence par la loi de Little, signaux d'autoscaling, benchmarks. -->


Qu'est-ce que le TTFT ? <!--anki:68355e7b7b31743d5d46-->
?
**Time To First Token** : délai entre l'envoi de la requête et le **premier token reçu**. Il dépend de la file d'attente et du **prefill** (longueur du prompt). C'est la réactivité perçue en streaming.

Préciser le point de mesure : le TTFT côté client inclut réseau et intermédiaires, celui du moteur peut les exclure. Le premier événement du protocole n'est pas nécessairement un token affichable. Un TTFT élevé peut venir d'une file saturée, d'un cache manquant ou du calcul d'entrée ; séparer ces composantes pour diagnostiquer.

---

Qu'est-ce que le TPOT (ou ITL) ? <!--anki:68424b38777e6e2a472f-->
?
Le **TPOT** est généralement le temps moyen par token après le premier : `(durée totale − TTFT) / (nombre de tokens − 1)`, pour au moins deux tokens. L'**ITL** mesure les intervalles individuels entre tokens ou émissions successives selon l'instrumentation.

À 30 ms par token en moyenne, le débit individuel approche 33 tokens/s. Cette moyenne peut cacher des pauses ; examiner aussi la distribution des ITL. Un événement réseau peut contenir plusieurs tokens, donc les timestamps de chunks ne mesurent pas exactement chaque token.

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
Un **batch plus gros** augmente le débit (GPU mieux rempli) mais **dégrade le TPOT** de chaque requête. On règle la **concurrence maximale** pour tenir le SLO de latence.

Le gain vient de la réutilisation des poids et du travail parallèle, mais chaque pas peut durer davantage. Le compromis varie avec longueur des requêtes et matériel. Balayer plusieurs niveaux de concurrence, puis retenir le débit maximal qui respecte les percentiles de latence attendus, en incluant l'attente en file.

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
La **longueur de la file d'attente** (requêtes en attente) et le **taux d'occupation du KV cache**, exposés en métriques Prometheus par le serveur ([[11-serveurs-inference-llm|vLLM]]). **Pas l'utilisation GPU**, souvent proche de 100 % et peu discriminante.

---

Comment mesurer les performances d'un déploiement d'inférence LLM ? <!--anki:505e777663703b53257c-->
?
Par des **benchmarks de charge** réalistes (distribution des longueurs de prompt/sortie, taux d'arrivée) : `vllm bench serve`, **GuideLLM**, **genai-perf** (NVIDIA). On trace la **courbe latence vs débit**.

Inclure un échauffement, les erreurs, le cache froid ou chaud et les pointes de charge. Un test à taux d'arrivée imposé montre comment la file grossit lorsque le service sature. Reporter les hypothèses et la distribution du trafic avec les résultats pour que la comparaison entre configurations soit reproductible.

---

Calcul : combien de requêtes simultanées faut-il servir pour 10 requêtes/s qui durent 8 secondes ? <!--anki:44597b556d555a6b6b32-->
?
**Loi de Little** : concurrence = débit × durée.
```text
L = λ × W = 10 req/s × 8 s = 80 requêtes en vol en moyenne
```
Avec 8 000 tokens de contexte par requête sur un 8B, c'est **≈ 80 Go de KV cache** : plus d'un H100 ([[61-kv-cache-attention|calcul du KV cache]]). Réduire la **durée** (moins de tokens de sortie, decode plus rapide) réduit la concurrence nécessaire autant qu'ajouter des GPU.

---

## Mises en situation

Mise en situation : le produit demande « une réponse en moins de 2 secondes » pour un assistant qui streame des réponses de 400 tokens. Comment traduis-tu ce besoin en SLO ? <!--anki:772b352d2f4c5b694141-->
?
1. **Décomposer** : en streaming, l'utilisateur perçoit d'abord le **TTFT**, puis la vitesse de lecture (**TPOT**)
2. **Poser des cibles** : par exemple p95 TTFT < 800 ms et p95 TPOT < 50 ms, soit environ 20 tokens par seconde
3. **Vérifier la cohérence** : 400 tokens à 50 ms font 20 s au total. Si le besoin est « tout en 2 s », il faut raccourcir la réponse, pas accélérer le GPU
4. **Choisir les percentiles** et la fenêtre (p95 sur 30 jours), pas la moyenne
5. **Valider par un benchmark** de charge réaliste avant de s'engager ([[93-monitoring-inference|monitoring]])

**Piège** : s'engager sur une latence totale sans fixer la longueur des réponses.

---

Mise en situation : ton dashboard affiche 100 % d'utilisation GPU et l'équipe conclut qu'il faut acheter des GPU. Comment vérifies-tu ? <!--anki:4a3363746c6836453d3b-->
?
1. **Se méfier de cette métrique** : elle indique qu'un kernel tourne, pas que le GPU est bien exploité
2. **Regarder les vraies causes** : file d'attente, occupation du KV cache, préemptions ([[93-monitoring-inference|métriques vLLM]])
3. **Tracer la courbe latence-débit** : à quel niveau de charge le SLO casse-t-il vraiment ?
4. **Mesurer le goodput** : le débit des seules requêtes qui respectent le SLO
5. **Chercher les gains gratuits** avant d'acheter : quantization, prefix caching, chunked prefill, limitation du contexte

**Piège** : dimensionner sur le pic absolu plutôt que sur le p95 du trafic réel.

---

Mise en situation : ton autoscaling se déclenche trop tard, et des requêtes attendent plusieurs secondes avant d'être traitées. Sur quoi le règles-tu ? <!--anki:6c6759312a4c4c493574-->
?
1. **Pas sur la seule utilisation GPU**, qui peut être élevée sans saturation du calcul
2. **Signaux utiles** : longueur de la file d'attente et taux d'occupation du KV cache, exposés en métriques par le serveur
3. **Anticiper le temps de démarrage** : un réplica LLM met plusieurs minutes à charger ses poids ([[10-images-modeles-poids|cold start]])
4. **Garder un coussin** : réplicas chauds ou pool préchauffé pour absorber les pics
5. **Alerter sur le SLO** plutôt que sur la cause : burn rate du TTFT p95

**Piège** : un scale-to-zero agressif qui fait payer un cold start de plusieurs minutes au premier utilisateur.

---

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
- [[00-moc-ai-engineering|MOC AI Engineering]]
