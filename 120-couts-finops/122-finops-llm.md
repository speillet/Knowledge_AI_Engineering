# FinOps LLM — Flashcards
Tags: #flashcards #ai-engineering #finops #gouvernance #llm

Qu'est-ce que le FinOps appliqué aux LLM ?
?
La discipline de **gestion des dépenses IA** (tokens d'API et GPU), en quatre temps :
1. **Visibilité** : savoir ce qui coûte, au jour près
2. **Attribution** : à quelle équipe, quel produit, quelle fonctionnalité
3. **Optimisation** : caching, routing, batch, modèles plus petits
4. **Gouvernance** : budgets, alertes, arbitrages

La spécificité des LLM : un coût **variable** qui dépend du comportement des utilisateurs et des agents, pas d'une capacité réservée.

---

Quelle est la première étape FinOps d'une plateforme LLM ?
?
La **visibilité** : tracer le coût **par requête, équipe et feature** via la [[81-litellm-api-layer|gateway]] et les [[91-langfuse-observabilite|traces]] — on ne pilote pas ce qu'on ne voit pas.

---

Comment attribuer les coûts aux équipes ?
?
- **Virtual keys** par équipe ou produit dans la gateway, et **tags** par fonctionnalité ([[81-litellm-api-layer|LiteLLM]])
- **Showback** d'abord : chaque équipe voit sa consommation
- **Chargeback** ensuite : refacturation interne, une fois les chiffres fiables

Sans attribution, personne n'est responsable d'un coût qui double, et les optimisations restent des vœux pieux.

---

Comment encadrer les dépenses ?
?
**Budgets et quotas par clé/équipe** dans la gateway, **alertes** avant dépassement, **kill switch** en cas d'emballement.
```yaml
# exemple de garde-fous par clé virtuelle (gateway LLM)
key: equipe-support
max_budget: 500          # € par mois
budget_duration: 30d
rpm_limit: 600           # requêtes par minute
tpm_limit: 400000        # tokens par minute
models: [chat-petit, chat-fort]
```
Les deux limites comptent : **requêtes** contre les rafales, **tokens** contre une seule requête à 200 000 tokens ([[81-litellm-api-layer|LiteLLM]]).

---

Quels gains attendre des principaux leviers FinOps ?
?
```text
Routage vers un modèle plus petit   −30 à −70 % selon la part de cas simples
Prompt caching (préfixe stable)     tokens d'entrée lus ≈ 10 % du prix plein
Traitement différé (batch API)      ≈ −50 %
Cache de réponses exactes           gain = taux de hit (0 à 90 % selon l'usage)
Contexte mieux trié                 proportionnel aux tokens supprimés
Quantization (self-host)            moins de GPU par réplica
```
Ordre d'attaque recommandé : **routage**, puis **caching**, puis **contexte**. Les trois se cumulent ([[121-couts-inference|coûts d'inférence]]).

---

Quel est souvent le premier levier d'économie ?
?
Le **[[82-routing-llm|routing]]** : envoyer chaque requête au **modèle le moins cher qui suffit** (cascades) — souvent plusieurs dizaines de % de gain.

---

Quels caches actionner côté FinOps ?
?
Quatre niveaux, du plus rentable au plus spécifique :
- **Prompt caching** des préfixes : effet massif sur les agents, dont l'entrée domine le coût
- **Cache de réponses** pour les requêtes identiques : gain égal au taux de hit
- **Cache d'embeddings** : on ne ré-embedde jamais deux fois le même chunk
- **Cache des résultats d'outils et de retrieval**, avec un TTL adapté à leur fraîcheur

Chacun a son risque : réponses périmées, fuite entre clients si la clé oublie le tenant ([[123-caching-agressif|caching agressif]]).

---

Quelles pratiques FinOps côté GPU ?
?
- **Droit-dimensionnement** : le plus petit GPU ou la plus petite tranche **MIG** qui tient la charge
- **Objectif d'utilisation** suivi, par exemple au-dessus de 60 %
- **Spot ou préemptible** pour le non-critique (batch, evals), avec reprise sur interruption
- **Scale-to-zero** des modèles peu appelés
- **Réservations** pour la charge de base stable ([[12-kubernetes-gpu-inference|K8s GPU]])

---

Comment arbitrer coût, qualité et latence ?
?
C'est un **triangle** : on ne maximise pas les trois. Les [[92-chainforge-evals-prompts|evals]] et les [[64-metriques-slo-inference|SLO]] rendent l'arbitrage **objectif** :
1. Fixer un **plancher de qualité** et un **plafond de latence**
2. Parmi les options qui les respectent, choisir la **moins chère**
3. Réévaluer à chaque nouveau modèle, car les prix baissent vite

Sans plancher de qualité explicite, l'optimisation des coûts dégrade le produit sans que personne ne le décide.

---

Quel est le rôle du Lead sur le FinOps ?
?
Suivre les **unit economics par produit**, imposer les **standards d'attribution**, tenir des **revues de coûts** régulières — le coût est une métrique de premier ordre, pas une surprise de fin de mois.

---

## Mises en situation

Mise en situation : la facture IA de l'entreprise a triplé en un trimestre et la direction financière demande des explications que personne ne peut donner. Par où commences-tu ?
?
1. **Visibilité d'abord** : sans attribution, aucune décision n'est possible. Tout passe par la gateway, avec des clés par équipe et par projet
2. **Attribuer** : coût par équipe, application et fonctionnalité, puis showback avant chargeback
3. **Identifier les gros postes** : quelles routes, quels modèles, quels utilisateurs concentrent la dépense
4. **Poser des garde-fous** : budgets, quotas, alertes avant dépassement, coupure d'urgence
5. **Optimiser ensuite** : routage, caching, contexte, dans cet ordre ([[123-caching-agressif|caching]])

**Piège** : imposer des quotas avant d'avoir la visibilité, ce qui bloque des usages utiles sans traiter la cause.

---

Mise en situation : une équipe veut passer au modèle le plus puissant pour toutes ses requêtes, au motif que « la qualité prime ». Comment cadres-tu la discussion ?
?
1. **Sortir de l'opposition** : le sujet est un triangle coût, qualité, latence, pas un choix binaire
2. **Demander des mesures** : sur quels segments le modèle le plus puissant est-il réellement meilleur ? ([[94-evals-methodologie|evals]])
3. **Chiffrer** : coût par requête et par tâche réussie pour chaque option
4. **Proposer une cascade** : petit modèle avec vérification, escalade sur les cas difficiles ([[82-routing-llm|routing]])
5. **Relier à la valeur** : unit economics de la fonctionnalité, pas seulement sa facture

**Piège** : trancher sur des impressions, faute d'evals par segment.

---

## Connexions
- [[121-couts-inference|Coûts d'inférence]] — la mécanique des coûts
- [[81-litellm-api-layer|LiteLLM]] — budgets, quotas, attribution
- [[91-langfuse-observabilite|Langfuse]] — cost tracking par trace
- [[82-routing-llm|Routing LLM]] — le levier n°1
- [[38-plateformes-agents|Plateformes d'agents]] — la gouvernance à l'échelle
- [[123-caching-agressif|Caching agressif]] — les caches en pratique
- [[93-monitoring-inference|Monitoring de l'inférence]] — les métriques d'usage par équipe
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — le coût d'une flotte d'agents
- [[147-leadership-technique-ia|Leadership technique]] — ROI des fonctionnalités IA
- [[145-cas-system-design|Cas de system design]] — des architectures types commentées
- [[148-pipelines-batch-llm|Pipelines batch]] — traiter des millions d'items à moindre coût
- [[00-moc-ai-engineering|MOC AI Engineering]]
