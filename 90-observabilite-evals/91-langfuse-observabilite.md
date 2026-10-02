# Langfuse & observabilité LLM — Flashcards
Tags: #flashcards #ai-engineering #observability #langfuse #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: périmètre et alternatives (LangSmith, Phoenix, Braintrust), traces, spans et generations, sessions, prompt management, scores, LLM-as-judge, datasets. -->


Qu'est-ce que Langfuse ? <!--anki:66646977482431392c37-->
?
Une plateforme **open source d'observabilité LLM**, auto-hébergeable ou en SaaS, qui couvre :
- **Traces** des appels LLM, outils et étapes d'agent
- **Coûts et latences** par trace, utilisateur ou fonctionnalité
- **Prompt management** versionné
- **Évaluations** : scores automatiques, annotations humaines, datasets

Alternatives : LangSmith, Arize Phoenix, Braintrust, ou des traces OpenTelemetry dans un outil d'observabilité existant ([[93-monitoring-inference|monitoring]]).

---

Pourquoi l'observabilité LLM diffère-t-elle de l'APM classique ? <!--anki:6678545e5a4b5374595b-->
?
Parce que les sorties sont **non déterministes** et le coût est **par token** : il faut tracer prompts, réponses, tokens et qualité, pas seulement latence/erreurs.

---

Qu'est-ce qu'une trace dans Langfuse ? <!--anki:7741552c30265d676839-->
?
L'**enregistrement complet d'une requête** : un arbre de **spans** (étapes) et de **generations** (appels LLM), avec entrées, sorties, latence, tokens et coût.
```text
trace : "question support #4212"          1,8 s   0,004 €
├─ span      retrieval (hybride + rerank)  240 ms  12 chunks
├─ generation gpt-classe-intention          180 ms  310 → 8 tokens
├─ span      appel outil statut_commande     90 ms
└─ generation réponse finale (streaming)    1,2 s   3 400 → 180 tokens
```
C'est cette granularité qui permet de dire **où** le temps et l'argent partent, et de rejouer un cas précis ([[93-monitoring-inference|métriques agrégées]]).

---

Que permet le suivi des sessions et des users ? <!--anki:63492c7126682c43374f-->
?
De **regrouper les traces par conversation ou par utilisateur** : suivre un parcours de bout en bout, retrouver l'historique d'un cas signalé au support, repérer les utilisateurs qui reformulent sans cesse (signal d'échec) et attribuer les coûts par client ou par équipe ([[122-finops-llm|FinOps]]).

Attention : un identifiant utilisateur est une **donnée personnelle**. On préfère un identifiant **pseudonyme** ([[152-pii-confidentialite|PII]]).

---

Qu'est-ce que le prompt management de Langfuse ? <!--anki:466a4f293328754834-->
?
Des **prompts versionnés, stockés hors du code** et récupérés par l'application à l'exécution, avec des **étiquettes** (`production`, `staging`).

Intérêts : itérer et faire un rollback **sans redéployer**, comparer deux versions en A/B, et relier chaque trace à la version du prompt utilisée. Contrepartie : un prompt peut changer sans commit, d'où la nécessité d'une eval avant de déplacer l'étiquette ([[13-prompts-production|prompts en production]]).

---

Comment Langfuse évalue-t-il la qualité des réponses ? <!--anki:755f48612d6276607357-->
?
Via des **scores attachés aux traces**, de trois origines :
- **Utilisateur** : pouce haut ou bas, note, commentaire, renvoyés par l'application
- **Automatique** : règles ou code (JSON valide, citations présentes, longueur)
- **[[95-llm-as-judge|LLM-as-judge]]** : un évaluateur exécuté sur un échantillon du trafic

Un score porte un **nom**, une **valeur** et éventuellement un **commentaire**, ce qui permet de filtrer les traces échouées et de suivre la qualité dans le temps ([[113-monitoring-drift-feedback|drift]]).

---

À quoi servent les datasets dans Langfuse ? <!--anki:7162585f2c4d7240345a-->
?
À constituer des **jeux de test à partir des traces réelles** : on ajoute une trace intéressante (surtout un échec) au dataset en un clic, avec son entrée et la sortie attendue. On **rejoue** ensuite ce dataset à chaque changement de prompt ou de modèle, et on compare les scores entre exécutions.

C'est le pont entre la production et les evals : les échecs observés deviennent des **tests de non-régression** ([[94-evals-methodologie|golden dataset]], [[153-data-flywheel-versioning|flywheel]]).

---

Comment instrumenter une app avec Langfuse ? <!--anki:6b713c4c794f4b26255a-->
?
Trois voies, de la plus fine à la plus globale :
```python
from langfuse import observe

@observe()          # SDK : un décorateur par étape à tracer
def repondre(question: str):
    ...
```
- **Intégrations natives** : callbacks LangChain ou [[81-litellm-api-layer|LiteLLM]], sans toucher au code applicatif
- **OpenTelemetry** : les traces émises par le serveur ou la gateway remontent automatiquement ([[93-monitoring-inference|conventions GenAI]])

Le plus rentable en premier : brancher la **gateway**, ce qui couvre toutes les applications d'un coup.

---

À ne pas confondre : trace, métrique et eval ? <!--anki:752431622a3e7d525a51-->
?
- **Trace** : un **cas précis**, avec tout son contexte. Sert à **enquêter**
- **Métrique** : un **agrégat** (latence p95, coût par jour, taux d'erreur). Sert à **alerter**
- **Eval** : un **jugement de qualité** sur une sortie, attaché à une trace ou à un dataset. Sert à **décider** ([[94-evals-methodologie|méthodologie]])

Les trois sont nécessaires : une métrique dit qu'il y a un problème, une trace dit lequel, une eval dit si un changement l'a corrigé.

---

## Mises en situation

Mise en situation : un utilisateur signale « une réponse fausse hier après-midi ». Tu n'as que les logs applicatifs classiques. Que te manque-t-il, et que mets-tu en place ? <!--anki:7375784c423966706d21-->
?
1. **Ce qui manque** : le prompt réellement envoyé, les documents récupérés, les appels d'outils, la version du prompt et du modèle
2. **Tracer** chaque requête comme un arbre de spans et de generations, avec entrées, sorties, tokens et coût
3. **Identifier** : session et utilisateur, pour retrouver la conversation complète
4. **Versionner les prompts** hors du code, afin de savoir lequel tournait à ce moment ([[111-mlops-llmops-fondamentaux|MLOps]])
5. **Attention aux données personnelles** : masquage et rétention définis dès le départ ([[152-pii-confidentialite|PII]])

**Piège** : ne journaliser que la réponse finale, ce qui rend toute enquête impossible.

---

Mise en situation : ton équipe veut passer des impressions (« ça marche plutôt bien ») à une mesure de la qualité en production. Comment t'y prends-tu ? <!--anki:4d7a4b59692846604b-->
?
1. **Collecter du signal** : pouce haut ou bas, reformulations, abandons, escalades vers un humain
2. **Scorer un échantillon** de traces avec un juge automatique, calibré sur des annotations humaines ([[95-llm-as-judge|LLM-as-a-judge]])
3. **Constituer des datasets** à partir des traces réelles, surtout les échecs
4. **Rejouer** ces datasets à chaque changement de prompt ou de modèle ([[112-cicd-modeles|CI/CD]])
5. **Suivre dans le temps** et segmenter par tâche, langue et client ([[113-monitoring-drift-feedback|drift]])

**Piège** : juger la qualité sur les seuls cas remontés par le support, très biaisés.

---

## Sources

- [Langfuse — traces, évaluations et gestion des prompts](https://langfuse.com/docs)

## Connexions
- [[92-chainforge-evals-prompts|ChainForge & evals]] — l'évaluation hors production
- [[64-metriques-slo-inference|Métriques & SLO]] — du système à l'application
- [[81-litellm-api-layer|LiteLLM]] — source naturelle des traces
- [[82-routing-llm|Routing LLM]] — décider grâce aux données observées
- [[38-plateformes-agents|Plateformes d'agents]] — brique observabilité
- [[113-monitoring-drift-feedback|Monitoring & drift]] — la boucle de feedback prod
- [[122-finops-llm|FinOps LLM]] — le cost tracking
- [[93-monitoring-inference|Monitoring de l'inférence]] — métriques serveur, GPU et usage
- [[94-evals-methodologie|Méthodologie d'évaluation]] — golden dataset, analyse d'erreurs
- [[95-llm-as-judge|LLM-as-a-judge]] — biais et validation du juge
- [[13-prompts-production|Prompts en production]] — registre, étiquettes et retour arrière
- [[98-debogage-agents|Débogage des agents]] — lire les traces avec méthode
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection, exfiltration et guardrails
- [[11-prompt-engineering-avance|Prompt engineering avancé]] — les techniques de base du prompt
- [[114-reproductibilite-variance|Reproductibilité & variance]] — non-déterminisme et statistiques d'evals
- [[41-automatisation-code-nocode|Automatisation code & no-code]] — workflows et outils no-code
- [[45-langgraph-production|LangGraph — Production]] — persistance, reprise et supervision humaine
- [[00-moc-ai-engineering|MOC AI Engineering]]
