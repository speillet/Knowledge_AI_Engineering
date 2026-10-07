# System design d'applications LLM — Méthode — Flashcards
Tags: #flashcards #ai-engineering #system-design #architecture #llm
<!-- summary: démarche, cadrage, échelle de complexité, triangle qualité-latence-coût, estimation de charge, composants, latence réelle ou perçue, synchrone ou asynchrone, multi-tenant, modes de défaillance, présentation des arbitrages. -->


Par quoi commence la démarche de system design d'une application LLM ? <!--anki:62787568774b543e5144-->
?
1. **Clarifier** le besoin : utilisateurs, tâche, volume, contraintes (latence, coût, confidentialité, langue).
2. **Définir le succès** : métriques produit et [[94-evals-methodologie|evals]].
3. Proposer **l'architecture la plus simple** qui peut marcher.

Par exemple, distinguer un brouillon relu d'un traitement automatique engageant une décision. Donner des hypothèses chiffrées sur trafic, longueur des demandes et coût acceptable, puis une baseline permettant de tester la valeur. Le choix du framework ou de la base vectorielle vient après les exigences, pas avant leur clarification.

---

Une fois l'architecture esquissée, que reste-t-il à traiter en system design ? <!--anki:504079722d576245485a-->
?
4. **Détailler** les composants critiques (retrieval, modèle, outils, garde-fous).
5. Traiter **fiabilité, sécurité, coûts, observabilité**.
6. Expliquer les **arbitrages** et comment le système **évolue**.

Dérouler une requête réelle et un échec concret : source absente, fournisseur lent ou outil indisponible. Pour chaque composant critique, préciser entrée, sortie, responsable et comportement dégradé. Justifier les choix par les exigences établies, puis indiquer quelles mesures déclencheraient une évolution plutôt que présenter une architecture définitive.

---

Quelles questions de cadrage poser sur l'usage et les contraintes produit ? <!--anki:7671295a6b3d2c7d6278-->
?
- **Qui** utilise, **combien** (requêtes/jour, pics) et **où** (langues, régions) ?
- Quelle **tolérance à l'erreur** ? (suggestion relue par un humain ≠ action automatique)
- Quelle **latence** acceptable ? Interactif, asynchrone, batch ?

Ces réponses déterminent le contrat produit : une suggestion peut être corrigée, alors qu'un paiement erroné a un coût immédiat. Quantifier les pics et les délais par segment, pas seulement en moyenne. Documenter les inconnues et proposer une mesure pilote pour éviter de dimensionner l'architecture sur des hypothèses cachées.

---

Quelles questions de cadrage poser sur les données et le cadre de l'entreprise ? <!--anki:6e255a234929572f2443-->
?
- Quelles **données** : volume, fraîcheur, sensibilité, droits d'accès ?
- **Budget** par requête ou par utilisateur ?
- **Contraintes** : on-prem, souveraineté, [[155-ai-act|réglementation]] ?

Cartographier aussi qui possède les sources, comment elles changent et qui peut y accéder. Une exigence de résidence peut exclure certains fournisseurs ; une source mise à jour chaque heure impose un mécanisme de synchronisation. Relier chaque contrainte à une décision d'architecture et à un contrôle vérifiable.

---

Quels sont les premiers barreaux de l'échelle de complexité d'un système LLM ? <!--anki:6f3a62406e2a4b7b716b-->
?
On monte d'un cran **seulement si le précédent ne suffit pas**, et **on le prouve par une eval** :
1. **Un appel LLM** bien prompté.
2. **Workflow** : chaîne d'appels déterministe, routage.
3. **RAG** ou outils en lecture.

---

Quels sont les derniers barreaux de l'échelle de complexité, et à quel prix ? <!--anki:64486d53634b69783433-->
?
Une **boucle agentique** aide quand les étapes ne sont pas connues à l'avance ; le **multi-agent** peut aider des sous-tâches réellement indépendantes. Ils ajoutent coordination, état et appels à diagnostiquer.

Le **fine-tuning est un autre axe**, adapté à un comportement répétitif insuffisamment obtenu par le prompt : ce n'est pas nécessairement l'étape après le multi-agent. Il coûte à entraîner et maintenir, mais peut réduire prompt et latence en service. Ajouter une complexité seulement pour résoudre une limite mesurée de la baseline ([[31-agents-fondamentaux|agents]]).

---

Quel est le triangle d'arbitrage central d'un système LLM ? <!--anki:772157213d79352c393c-->
?
**Qualité, latence et coût** doivent être mesurés ensemble sur la tâche cible. Un modèle plus gros ou un raisonnement plus long peut améliorer certains cas, mais peut aussi ajouter du délai, du coût ou des erreurs sans gain utile.

Comparer des configurations complètes à contraintes explicites, avec leurs résultats par segment. [[82-routing-llm|Routage]], [[123-caching-agressif|caching]] et [[53-donnees-synthetiques-distillation|distillation]] déplacent les compromis ; ils ont eux-mêmes des coûts et des risques. Le streaming réduit parfois l'attente perçue sans réduire la durée totale.

---

Comment faire une estimation de charge (back-of-the-envelope) ? <!--anki:4f77243c41575850796f-->
?
Exemple : 100 000 utilisateurs × 10 requêtes/jour = **1 M requêtes/jour ≈ 12 req/s** en moyenne, **pic ×3 à ×5**. Avec 3 000 tokens d'entrée et 500 de sortie par requête : **3,5 G tokens/jour**. On en déduit le **coût API** (prix × tokens) ou le **nombre de GPU** (débit en tokens/s par GPU), et on compare ([[121-couts-inference|break-even API vs self-host]]).

---

Quels composants une requête traverse-t-elle dans une architecture LLM de production ? <!--anki:74584e6f3d7123525955-->
?
- **Front / API** avec auth et rate limiting ([[83-gateway-ingress|gateway]]).
- **Orchestrateur** applicatif (workflow ou agent).
- **Guardrails** en entrée et en sortie.
- **Gateway LLM** : routage, fallbacks, budgets ([[81-litellm-api-layer|LiteLLM]]), puis les **modèles** (API ou self-hosted).

---

Quelles briques de support complètent une architecture LLM de production ? <!--anki:74727b49455b7442742c-->
?
- **Retrieval** : index vectoriel et lexical, reranker.
- **Caches** à tous les niveaux et **file de messages** pour l'asynchrone.
- **Observabilité** (traces, evals online) et **boucle de feedback**.

Ces briques répondent à des besoins précis et ne sont pas toutes obligatoires. Une extraction autonome n'exige pas nécessairement de retrieval ; une réponse dépendant de données privées exige des caches correctement isolés. Identifier le goulot ou le risque traité par chaque composant avant de l'ajouter à la baseline.

---

Comment réduire la latence perçue d'une application LLM, côté interface ? <!--anki:697a3f7d53485e56495f-->
?
- **Streaming** des tokens : le TTFT compte plus que la durée totale.
- **Paralléliser** les étapes indépendantes (retrieval et classification d'intention en même temps).
- Afficher la **progression** d'un agent plutôt qu'un spinner ([[144-ux-ia-human-in-the-loop|UX]]).

---

Comment réduire la latence réelle d'une application LLM, côté calcul ? <!--anki:6e49254259305f552c24-->
?
- **Petits modèles** pour les étapes intermédiaires (routage, réécriture).
- **Prompt caching** des préfixes longs ([[123-caching-agressif|caching]]).
- Réponses **pré-calculées** pour les questions fréquentes.

Mesurer d'abord le chemin critique : attente, retrieval, outils, prefill et decode. Les petits modèles n'aident que si leur qualité suffit et leur appel ne crée pas plus d'escalades. Paralléliser les étapes indépendantes et limiter la sortie peuvent aussi réduire la durée ; le streaming améliore surtout la perception du temps d'attente.

---

Quand choisir un traitement LLM synchrone ou asynchrone ? <!--anki:4c506377553d6f47263d-->
?
- **Synchrone** (streaming) : interaction humaine, réponse en secondes.
- **Asynchrone** (file + workers + notification) : tâches longues (agents, rapports, traitements de documents), pics de charge à **lisser**, **batch API** moins chère.

Une tâche d'agent de plusieurs minutes **ne doit pas** tenir une requête HTTP ouverte ([[142-fiabilite-resilience-llm|fiabilité]]).

---

Comment isoler les clients d'une application LLM multi-tenant ? <!--anki:45785b5e5036705d493b-->
?
- **Isolation des données** : filtre de tenant **obligatoire** dans le retrieval (idéalement imposé côté serveur, pas par le prompt), voire index séparés.
- **Quotas et budgets** par tenant.
- **Clés et configurations** (modèle, prompt) par tenant.
- **Pas de cache partagé** entre tenants pour des données privées ([[123-caching-agressif|sécurité du cache]]).

---

Quels modes de défaillance anticiper dès la conception ? <!--anki:656575326e2975292b3d-->
?
Panne ou **rate limit** du fournisseur, **latence** dégradée, **sortie invalide** (format), **hallucination**, **prompt injection**, **boucle d'agent**, **dérive de coût**, **mise à jour silencieuse** du modèle, **retrieval vide**. Pour chacun : **détection** + **réponse** (retry, fallback, abstention, escalade humaine).

---

Comment présenter les arbitrages de façon senior ? <!--anki:4e5d6f754e26452d754d-->
?
Pour chaque choix, dire **ce qu'on gagne, ce qu'on perd, et ce qui ferait changer d'avis** : « RAG plutôt que fine-tuning car le corpus change chaque semaine ; on reconsidérera si le style de réponse devient le problème principal ». Et **chiffrer** : coût par requête, latence p95, taux d'erreur cible.

---

À ne pas confondre : latence réelle et latence perçue ? <!--anki:6663657646534e482321-->
?
- **Latence réelle** : le temps de calcul jusqu'à la réponse complète, réduit côté serving (modèle plus petit, cache, moins de tokens de sortie)
- **Latence perçue** : le temps pendant lequel l'utilisateur **attend sans rien voir**, réduit côté interface (**streaming**, premier token rapide, étapes affichées, travail en arrière-plan)

Un agent de 40 secondes qui montre ses étapes peut paraître plus rapide qu'une réponse de 8 secondes sur écran blanc. Le **TTFT** pilote la perception, la durée totale pilote le coût ([[64-metriques-slo-inference|métriques]]).

---

## Mises en situation

Mise en situation : on te demande en entretien de concevoir un assistant interne pour 5 000 employés, sur la documentation de l'entreprise. Comment démarres-tu les dix premières minutes ? <!--anki:6a643d4d5663212f3323-->
?
1. **Cadrer avant de dessiner** : volume et pics, langues, tolérance à l'erreur, latence attendue, sensibilité des documents, budget
2. **Définir le succès** : que mesure-t-on, avec quelles evals et quelles métriques produit
3. **Poser l'architecture la plus simple** : un appel LLM plus un RAG, sans agent
4. **Chiffrer** : requêtes par seconde, tokens par requête, coût par mois, puis comparer API et self-host ([[121-couts-inference|coûts]])
5. **Annoncer les points critiques** : droits d'accès au retrieval, fraîcheur de l'index, observabilité

**Piège** : commencer par un schéma à huit composants avant d'avoir posé une seule question.

---

Mise en situation : ton architecture fonctionne à 12 requêtes par seconde en moyenne, mais tombe aux heures de pointe. Quels choix de conception réexamines-tu ? <!--anki:4831633d2e7e784a5462-->
?
1. **Le pic, pas la moyenne** : dimensionner sur un facteur 3 à 5 au-dessus de la moyenne
2. **Synchrone ou asynchrone** : les traitements longs passent en file avec notification, au lieu de tenir une requête ouverte
3. **Lisser** : file d'attente, quotas par client, et traitement différé pour ce qui n'est pas interactif
4. **Réduire le coût unitaire** : caching, routage vers un modèle plus petit sur les cas simples
5. **Vérifier le maillon faible** : quota du fournisseur, base vectorielle, ou concurrence du serveur d'inférence

**Piège** : ajouter des réplicas alors que la limite vient du quota du fournisseur de modèle.

---

Mise en situation : ton directeur technique te demande pourquoi tu as choisi le RAG plutôt qu'un fine-tuning. Comment présentes-tu l'arbitrage de façon senior ? <!--anki:70653f2c445d69663a59-->
?
1. **Dire ce qu'on gagne** : connaissances à jour, citations vérifiables, droits d'accès par document
2. **Dire ce qu'on perd** : latence du retrieval, complexité d'ingestion, qualité dépendante du chunking
3. **Dire ce qui ferait changer d'avis** : si le problème devient le **style** des réponses ou la longueur des prompts, un fine-tuning léger se justifie
4. **Chiffrer** : coût par requête, latence p95, qualité mesurée sur les evals
5. **Prévoir l'évolution** : les deux approches se combinent, le RAG pour les connaissances, le fine-tuning pour le comportement

**Piège** : justifier un choix d'architecture par une préférence technique plutôt que par des mesures et des contraintes.

---

## Connexions
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — faire tenir le système en production
- [[145-cas-system-design|Cas de system design]] — exemples concrets
- [[146-choix-modeles|Choix de modèle]] — le composant central
- [[31-agents-fondamentaux|Agents]] — workflow ou agent
- [[21-rag-fondamentaux|RAG]] — le composant de connaissances
- [[81-litellm-api-layer|LiteLLM]] et [[82-routing-llm|routing]] — la gateway
- [[121-couts-inference|Coûts d'inférence]] — chiffrer le design
- [[84-streaming-integration-applicative|Streaming & intégration]] — synchrone, streaming ou asynchrone
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection, exfiltration et guardrails
- [[147-leadership-technique-ia|Leadership technique]] — standards d'équipe et décisions
- [[148-pipelines-batch-llm|Pipelines batch]] — traiter des millions d'items à moindre coût
- [[22-rag-avance|RAG — Avancé]] — recherche hybride, reranking et filtres
- [[00-moc-ai-engineering|MOC AI Engineering]]
