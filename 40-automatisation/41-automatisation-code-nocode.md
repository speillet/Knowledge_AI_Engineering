# Automatisation code & no-code — Flashcards
Tags: #flashcards #ai-engineering #automatisation #workflow #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: n8n, triggers, Zapier et Make, Airflow, Prefect et Temporal, durable execution, limites du no-code. -->


Workflow ou agent : quelle différence ? <!--anki:633a44664441747c2432-->
?
Un **workflow** enchaîne des étapes **définies à l'avance** (déterministe, prévisible, testable) ; un **[[31-agents-fondamentaux|agent]]** décide lui-même de ses étapes. Beaucoup de besoins « IA » sont en fait des **workflows avec un appel LLM au milieu**.

---

Qu'est-ce que n8n ? <!--anki:5074357b48742c717130-->
?
Un outil d'**automatisation de workflows** visuel, **self-hostable** (licence fair-code) : des **nœuds** reliés (API, bases, LLM) déclenchés par des **triggers**, avec la possibilité d'insérer du code JavaScript ou Python.

Chaque nœud reçoit des données, réalise une opération et transmet sa sortie au suivant. Exemple : réception d'un formulaire, extraction de champs, validation et création d'un ticket. L'auto-hébergement donne le contrôle de l'infrastructure mais implique mises à jour, sauvegardes, secrets et supervision ; vérifier les conditions de licence pour l'usage prévu.

---

Qu'est-ce qu'un trigger dans un outil de workflow ? <!--anki:68544b7e4c744e677a2d-->
?
L'**événement qui lance le workflow** : webhook, planification (cron), nouveau mail, message Slack, ligne ajoutée dans une base…

Le trigger fournit généralement un événement avec ses données : identifiant, date et contenu utile. Une même notification peut arriver plusieurs fois ; prévoir une clé de déduplication avant une action comme créer une facture. Distinguer le déclenchement de la réussite du traitement et définir comment reprendre après un échec.

---

Comment intègre-t-on un LLM dans un workflow n8n ? <!--anki:4b76742c3c456f2b2679-->
?
Par des **nœuds IA** : appel de modèle, extraction structurée, classification, ou nœud **AI Agent** avec outils et mémoire — l'agent devient **une étape** d'un workflow maîtrisé.

Entourer l'appel par des contrôles : schéma d'entrée, validation de sortie, timeout et branche d'erreur. Pour classer un ticket, limiter les catégories possibles puis vérifier la valeur obtenue avant de le router. Le reste du workflow conserve des règles explicites ; une réponse libre du modèle ne doit pas décider seule d'une action irréversible.

---

Comment choisir entre n8n, Zapier et Make pour un workflow ? <!--anki:78707c3f7a57534d4161-->
?
Comparer les outils sur le **besoin d'intégration et d'exploitation**. Zapier et Make proposent des services hébergés avec des connecteurs et un éditeur visuel ; n8n offre notamment une option d'auto-hébergement et l'insertion de code.

Vérifier les connecteurs réellement nécessaires, les conditions de licence, la localisation des données, les limites et le coût au volume prévu. Tester aussi retries, export, revue et maintenance. L'auto-hébergement n'est pas gratuit à exploiter et un grand catalogue ne garantit pas la bonne couverture d'une API.

---

Quand passer du no-code au code ? <!--anki:4c5a477837435f66672d-->
?
Quand il faut **versionner, tester, faire de la revue de code**, gérer une logique complexe, de gros volumes ou des SLA stricts. Le no-code excelle pour **prototyper** et pour les intégrations simples.

Ces capacités existent à des degrés variables dans les plateformes : ce sont leurs limites concrètes qui motivent la transition. Par exemple, garder l'éditeur pour connecter des services et déplacer une règle métier complexe dans une API testée. Comparer le coût de maintenance et les compétences de l'équipe avant de réécrire tout le workflow.

---

Quel orchestrateur « code » pour des pipelines data planifiés, une orchestration Python moderne, ou des workflows longs qui survivent aux pannes ? <!--anki:3965646437363366373533343431323962373938366663616639633465636330-->
?
- **Pipelines batch planifiés** (DAG de traitements data) : **Airflow**
- **Orchestration Python plus moderne**, centrée sur les tâches ou les assets : **Prefect**, **Dagster**
- **Workflows longs qui doivent survivre aux pannes** (attentes humaines, agents) : **Temporal** et sa **durable execution**

---

Pourquoi la durable execution intéresse-t-elle les agents ? <!--anki:624b5d7544713e7d2179-->
?
Un agent long (minutes ou heures, avec validations humaines) doit **reprendre là où il s'est arrêté** après un crash ou une attente, sans rejouer les appels LLM et les actions déjà faites.
```python
# le moteur enregistre le résultat de chaque étape : au redémarrage,
# il rejoue le code mais renvoie les résultats déjà connus
async def traiter_dossier(id):
    donnees   = await etape(extraire, id)         # déjà fait → résultat rejoué
    analyse   = await etape(analyser_llm, donnees) # déjà fait → résultat rejoué
    decision  = await attendre_humain(analyse)     # reprend ici, 2 jours plus tard
    await etape(notifier, decision)                # exécuté une seule fois
```
Condition indispensable : des étapes **idempotentes**, sinon la reprise renvoie deux fois le même e-mail ([[45-langgraph-production|checkpoints]]).

---

À ne pas confondre : orchestrateur de données et durable execution ? <!--anki:735f63646e702e615826-->
?
- **Airflow, Dagster, Prefect** : pensés pour des **pipelines planifiés** (batch nocturne, ETL). Granularité : la tâche, l'exécution périodique
- **Temporal, Restate, DBOS** : pensés pour des **processus longs et événementiels**, avec état, attentes humaines et reprise **à l'instruction près**

Un agent qui attend une validation pendant deux jours relève du second, pas du premier.

---

Quelles limites du no-code en production ? <!--anki:4169365566313b657b25-->
?
**Versioning et diff** difficiles, **tests automatisés** limités, gestion des erreurs et des secrets à surveiller, et risque de **workflows « shadow IT »** que personne ne maintient.

Nommer un responsable, documenter les dépendances et prévoir sauvegarde, alertes et procédure de reprise. Tester la panne d'un connecteur et les notifications dupliquées. Un workflow visuellement simple peut engager des droits importants ; les identifiants de service doivent être limités et renouvelables, comme ceux d'une application développée en code.

---

## Mises en situation

Mise en situation : le service marketing a monté seul un workflow n8n qui envoie des e-mails clients avec un LLM, et il tourne déjà en production. Que fais-tu ? <!--anki:7773364f507c3d783c70-->
?
1. **Ne pas l'interdire sèchement** : il répond à un vrai besoin et il tourne. Le supprimer pousserait le sujet dans l'ombre
2. **Inventorier** : que fait-il, quelles données touche-t-il, quels secrets utilise-t-il, qui le maintient
3. **Sécuriser l'essentiel** : clés passées par la [[81-litellm-api-layer|gateway]], budgets, pas de données sensibles en clair, traces centralisées
4. **Encadrer** : validation humaine avant envoi, gestion des erreurs, propriétaire identifié
5. **Décider ensuite** : le garder en no-code s'il reste simple, ou le passer en code s'il devient critique (versioning, tests, revue)

**Piège** : laisser vivre un workflow « shadow IT » sans propriétaire, jusqu'au jour où il envoie mille e-mails erronés.

---

Mise en situation : ton processus d'onboarding client dure trois jours, avec deux validations humaines et un appel LLM par étape. Quel outillage choisis-tu ? <!--anki:4d30377563394d6f6c5f-->
?
1. **Reconnaître le besoin** : un processus long, avec attentes humaines, doit **survivre aux redémarrages**
2. **Durable execution** : Temporal ou un framework à checkpoints, pour reprendre sans rejouer les appels déjà faits ([[45-langgraph-production|LangGraph en production]])
3. **Idempotence** de chaque étape qui écrit ou envoie quelque chose
4. **Attentes humaines** modélisées comme des états, avec délais d'expiration et relances
5. **Observabilité** : où en est chaque dossier, quelles étapes ont échoué ([[93-monitoring-inference|monitoring]])

**Piège** : un script cron qui relance tout depuis le début après un incident, et qui renvoie les e-mails déjà partis.

---

## Sources

- [n8n — documentation des workflows](https://docs.n8n.io/)
- [Temporal — exécution durable](https://docs.temporal.io/)

## Connexions
- [[31-agents-fondamentaux|Agents]] — workflow vs agent
- [[36-orchestration-agents|Orchestration multi-agents]] — quand le workflow ne suffit plus
- [[32-tool-calling|Tool calling]] — un workflow peut servir d'outil à un agent
- [[44-langgraph-fondamentaux|LangGraph]] — workflows et agents en code, sous forme de graphe
- [[47-crewai-flows|CrewAI Flows]] — workflows événementiels qui orchestrent des crews
- [[81-litellm-api-layer|LiteLLM]] — point d'accès aux modèles
- [[91-langfuse-observabilite|Langfuse]] — les traces restent centralisées
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — les patterns derrière les workflows
- [[00-moc-ai-engineering|MOC AI Engineering]]
