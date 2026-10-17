# Ingress & API gateway — Flashcards
Tags: #flashcards #ai-engineering #kubernetes #ingress #networking
Vérifié le : 17 octobre 2026 — retrait d'ingress-nginx confronté aux annonces du projet Kubernetes.
<!-- summary: Ingress controller, retrait d'ingress-nginx, Ingress, API gateway et gateway LLM, TLS, Gateway API, rate limiting, streaming SSE, migration d'un controller. -->


Qu'est-ce qu'un Ingress dans Kubernetes ? <!--anki:49586e334f397c2c6740-->
?
La **porte d'entrée HTTP(S) du cluster** : il route le trafic externe vers les Services selon l'hôte et le chemin.

Un objet Ingress décrit des règles ; un **Ingress controller** doit les implémenter pour que le trafic soit effectivement routé. Les Services dirigent ensuite vers les Pods éligibles. L'Ingress ne décide pas automatiquement du bon modèle LLM et ne constitue pas, à lui seul, une politique d'authentification ou de budget.

---

Un Ingress fonctionne-t-il seul ? <!--anki:45497c54723d663e553e-->
?
**Non.** L'objet Ingress n'est qu'une **déclaration** ; il faut un **Ingress controller** (Traefik, HAProxy, Cilium…) qui l'observe et configure réellement un proxy. ingress-nginx, longtemps le plus répandu, n'est plus maintenu depuis mars 2026. Sans controller installé, l'objet est accepté par l'API et **rien ne se passe** : c'est une cause classique de « mon Ingress ne répond pas ».

---

Que gère typiquement un Ingress ? <!--anki:46493d40694175445866-->
?
- Routage **par hôte** (`api.example.com`) et **par chemin** (`/v1/...`)
- **Terminaison TLS** (HTTPS)

Par exemple, envoyer `api.example.com/v1` vers le Service de la gateway tout en présentant un certificat HTTPS. Certaines fonctions supplémentaires dépendent du controller et de sa configuration. Vérifier taille des corps, timeouts et streaming sur toute la chaîne ; une règle de routage correcte ne garantit pas qu'une longue réponse arrive intacte.

---

Qu'est-ce que la Gateway API ? <!--anki:4c73712d31366d6b342d-->
?
Le **successeur de l'Ingress** dans Kubernetes, avec des rôles séparés :
```text
GatewayClass → l'implémentation (choisie par la plateforme)
Gateway      → le point d'entrée : ports, TLS (équipe infra)
HTTPRoute    → le routage vers les Services (équipe applicative)
```
Apports : **délégation par équipe** sans annotations propriétaires, découpage du trafic **par poids** (canary), et prise en charge d'autres protocoles (gRPC, TCP). C'est la voie recommandée par Kubernetes pour remplacer ingress-nginx. Les projets de gateway pour agents s'appuient dessus ([[38-plateformes-agents|agentgateway]]).

---

À ne pas confondre : Ingress, API gateway et gateway LLM ? <!--anki:68587e30382d4f264f2a-->
?
```text
Ingress       → exposition HTTP(S), hôte, chemin, TLS
API gateway   → politiques d'API : auth, quotas, transformations
Gateway LLM   → modèles, tokens, budgets, fallbacks, traces LLM
```
Ce sont des **responsabilités**, pas nécessairement trois produits empilés. Une gateway généraliste peut intégrer des fonctions LLM ou une extension de comptage des tokens ; une gateway LLM peut aussi terminer TLS.

Choisir l'assemblage qui couvre les besoins sans dupliquer les contrôles, et désigner qui applique chaque quota ou timeout ([[81-litellm-api-layer|LiteLLM]]).

---

Pourquoi rate-limiter un endpoint LLM ? <!--anki:6b603e5625303c4c4a78-->
?
Parce que chaque requête consomme du **GPU coûteux** : sans limite, un client peut saturer le service et faire exploser les coûts.

Les requêtes n'ont pas toutes le même coût : une génération longue peut monopoliser beaucoup plus de ressources qu'une classification. Combiner limites de requêtes, tokens et concurrence, par identité et globalement. Retourner une erreur explicite avec une politique de retry adaptée et garder une file bornée pour protéger la latence des autres clients.

---

À quoi ressemble la chaîne réseau d'une stack LLM sur Kubernetes ? <!--anki:482648216e5375467761-->
?
```text
Client → Ingress (TLS, routage) → gateway/LiteLLM (auth, quotas) → Service vLLM → Pods GPU
```

L'Ingress expose le domaine ; la gateway authentifie et choisit le backend ; le Service fournit une destination stable vers les Pods prêts ; les Pods exécutent le modèle. Certains composants peuvent être fusionnés. Diagnostiquer chaque saut : résolution DNS, TLS, autorisation, routage, readiness et calcul, en gardant un identifiant commun dans les logs.

---

Pourquoi le streaming (SSE) impose-t-il des réglages particuliers ? <!--anki:715e606d2e4e6d786140-->
?
Les réponses LLM sont **longues et streamées** : il faut des **timeouts allongés** et désactiver le **buffering**, sinon le proxy garde la réponse et l'utilisateur attend tout le texte d'un coup.
```yaml
annotations:                       # ingress-nginx
  nginx.ingress.kubernetes.io/proxy-buffering: "off"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
```
Penser aussi aux **load balancers cloud** en amont, avec leur propre délai d'inactivité, et à la **compression**, à désactiver sur ces routes. Ces annotations sont propres à ingress-nginx, qui n'est plus maintenu depuis mars 2026 : avec un autre controller ou la Gateway API, chercher les réglages équivalents.

---

Quels repères de configuration pour un endpoint LLM ? <!--anki:6a586e4237583a6c5656-->
?
Définir les réglages à partir du **SLO et du profil des requêtes**, pas de valeurs universelles :
```text
délai total          budget de bout en bout côté client et serveur
timeout d'inactivité adapté aux pauses entre événements du stream
buffering            éviter d'accumuler les tokens avant envoi
taille de requête    plafonnée selon les formats réellement acceptés
quotas               requêtes, tokens et concurrence
```
Distinguer délai de connexion, délai entre lectures et durée totale. Tester un stream long, une période sans émission et une déconnexion client. Un timeout très élevé sans annulation peut laisser tourner du GPU inutilement ([[142-fiabilite-resilience-llm|fiabilité]]).

---

## Mises en situation

Mise en situation : ton assistant est exposé par ingress-nginx, qui n'est plus maintenu depuis mars 2026, avec des annotations qui désactivent le buffering et allongent les timeouts du streaming. Comment prépares-tu la migration ? <!--anki:6566363336623132396438643438623062396438343933313137363037623561-->
?
1. **Inventorier** les objets Ingress et leurs annotations : timeouts, buffering, TLS, taille des requêtes, réécritures
2. **Choisir la cible** : une implémentation de la Gateway API ou un autre controller maintenu, selon les fonctions réellement utilisées ([[04-kubernetes-kubelet-cri|Kubernetes]])
3. **Traduire chaque réglage** : aucun remplaçant n'accepte ces annotations telles quelles, les équivalents se configurent autrement
4. **Tester le streaming de bout en bout** : réponse longue, pause sans émission, déconnexion du client ([[84-streaming-integration-applicative|streaming]])
5. **Basculer progressivement** : deux points d'entrée en parallèle, trafic déplacé par étapes, retour arrière prêt

**Piège** : recopier les routes sans leurs annotations, et retrouver en production des réponses tamponnées ou coupées.

---

Mise en situation : un client unique sature ton service d'inférence en lançant des milliers de requêtes en parallèle. Où poses-tu les limites ? <!--anki:42676956437a5a6f296b-->
?
1. **À l'entrée** : rate limiting par clé ou par IP sur l'Ingress ou l'API gateway
2. **Dans la gateway LLM** : limites en requêtes et en **tokens** par minute, plus un budget ([[81-litellm-api-layer|LiteLLM]])
3. **Dans le serveur d'inférence** : concurrence maximale, pour préserver le SLO des autres utilisateurs
4. **Répondre proprement** : code 429 avec en-tête de reprise, plutôt qu'un timeout
5. **Surveiller** : taux de 429 par client, pour distinguer un abus d'une limite trop basse ([[93-monitoring-inference|monitoring]])

**Piège** : limiter uniquement le nombre de requêtes, alors qu'une seule requête à 100 000 tokens coûte bien plus cher.

---

## Sources

- [Kubernetes — retrait d'Ingress NGINX](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/)
- [Kubernetes — Gateway API](https://gateway-api.sigs.k8s.io/)

## Connexions
- [[04-kubernetes-kubelet-cri|Kubernetes]] — le socle
- [[64-metriques-slo-inference|Métriques & SLO]] — rate limiting et timeouts pilotés par le SLO
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — les Pods derrière l'Ingress
- [[81-litellm-api-layer|LiteLLM]] — la gateway applicative derrière l'Ingress
- [[84-streaming-integration-applicative|Streaming & intégration]] — tampons et timeouts sur les flux SSE
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM et leur réglage
- [[112-cicd-modeles|CI/CD des modèles]] — eval gates, canary et rollback
- [[144-ux-ia-human-in-the-loop|UX & human-in-the-loop]] — ce que voit et valide l'utilisateur
- [[00-moc-ai-engineering|MOC AI Engineering]]
