# Automatisation code & no-code — Flashcards
Tags: #flashcards #ai-engineering #automatisation #workflow #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: n8n, triggers, Zapier et Make, Airflow, Prefect et Temporal, durable execution, limites du no-code, doublons et désordre des webhooks, fuseaux horaires, file d'échec. -->


Qu'est-ce que n8n ? <!--anki:5074357b48742c717130-->
?
Un outil d'**automatisation de workflows** visuel, **self-hostable** (licence fair-code) : des **nœuds** reliés (API, bases, LLM) déclenchés par des **triggers**, avec la possibilité d'insérer du code JavaScript ou Python.

Chaque nœud reçoit des données, réalise une opération et transmet sa sortie au suivant. Exemple : réception d'un formulaire, extraction de champs, validation et création d'un ticket. L'auto-hébergement donne le contrôle de l'infrastructure mais implique mises à jour, sauvegardes, secrets et supervision ; vérifier les conditions de licence pour l'usage prévu.

---

Qu'est-ce qu'un trigger dans un outil de workflow ? <!--anki:68544b7e4c744e677a2d-->
?
L'**événement qui lance un workflow** : webhook, horaire planifié, message ou changement de données. Il apporte généralement identifiant, date et contenu.

Exemple : un webhook de commande est enregistré durablement, puis traité en arrière-plan. L'accusé de réception confirme sa prise en charge, **pas la livraison de la commande**. Si le producteur renvoie le même événement après un timeout, une clé stable doit empêcher une seconde action métier.

Prévoir authentification de la source, déduplication et reprise après échec. Un déclenchement planifié exige aussi de définir fuseau horaire et comportement si l'exécution précédente n'est pas terminée.

---

Comment intègre-t-on un LLM dans un workflow n8n ? <!--anki:4b76742c3c456f2b2679-->
?
Par des **nœuds IA** : appel de modèle, extraction structurée, classification, ou nœud **AI Agent** avec outils et mémoire — l'agent devient **une étape** d'un workflow maîtrisé.

Entourer l'appel par des contrôles : schéma d'entrée, validation de sortie, timeout et branche d'erreur. Pour classer un ticket, limiter les catégories possibles puis vérifier la valeur obtenue avant de le router. Le reste du workflow conserve des règles explicites ; une réponse libre du modèle ne doit pas décider seule d'une action irréversible.

---

Comment choisir entre n8n, Zapier et Make pour un workflow ? <!--anki:78707c3f7a57534d4161-->
?
Comparer les outils sur le **besoin d'intégration et d'exploitation**. Zapier et Make proposent des services hébergés avec des connecteurs et un éditeur visuel ; n8n offre notamment une option d'auto-hébergement et l'insertion de code.

Vérifier les connecteurs réellement nécessaires, les conditions de licence, la localisation des données, les limites et le coût au volume prévu. Exemple : des données de santé à garder sur ses serveurs orientent vers n8n auto-hébergé ; vingt intégrations SaaS courantes sans équipe d'exploitation, vers un service hébergé. L'auto-hébergement n'est pas gratuit à exploiter et un grand catalogue ne garantit pas la bonne couverture d'une API.

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

Partir du besoin de reprise : recalculer une partition de données n'est pas équivalent à reprendre une attente d'approbation après trois jours. Tester les délais, retries et effets externes avec l'orchestrateur retenu. Une exécution durable conserve l'avancement, mais les activités rejouables doivent toujours gérer l'idempotence des écritures métier.

---

Pourquoi la durable execution intéresse-t-elle les agents ? <!--anki:624b5d7544713e7d2179-->
?
Elle permet de **reprendre un workflow à partir d'un historique durable**, sans refaire les étapes dont le résultat a déjà été enregistré. Avec le SDK Python de Temporal :
```python
await workflow.execute_activity(proposer_remboursement, dossier,
                                start_to_close_timeout=timedelta(minutes=5))
await workflow.wait_condition(lambda: self.decision is not None)  # signal humain, sans limite de durée
```
Après un redémarrage, le worker rejoue l'historique : l'activité terminée n'est pas relancée, son résultat est relu.

Une activité distante acceptée juste avant un crash peut toutefois être relancée si son résultat n'a pas été enregistré. Prévoir clés d'idempotence, vérification d'état et politique d'annulation ; un moteur ne transforme pas une API externe en transaction. Voir les [[45-langgraph-production|checkpoints]] pour comparer les frontières de persistance.

---

À ne pas confondre : orchestrateur de données et durable execution ? <!--anki:735f63646e702e615826-->
?
L’**orchestration de données** organise dépendances, partitions et disponibilité de résultats. La **durable execution** vise la reprise de workflows en s'appuyant sur un historique persistant des étapes et événements.

Exemple : Dagster recalcule la partition du 21 octobre d'un asset quand sa source change ; Temporal reprend le dossier D-123 à l'étape « attente de signature » après un redémarrage. Ces capacités se recouvrent selon les plateformes. Examiner granularité de reprise, délais, annulation, versioning et interactions externes. La persistance du workflow ne garantit pas qu'une activité distante s'exécute une seule fois : son idempotence ou un protocole adapté reste nécessaire.

---

Quelles limites du no-code en production ? <!--anki:4169365566313b657b25-->
?
**Versioning et diff** difficiles, **tests automatisés** limités, gestion des erreurs et des secrets à surveiller, et risque de **workflows « shadow IT »** que personne ne maintient.

Nommer un responsable, documenter les dépendances et prévoir sauvegarde, alertes et procédure de reprise. Tester la panne d'un connecteur et les notifications dupliquées. Un workflow visuellement simple peut engager des droits importants. Exemple : il utilise le jeton personnel d'un employé parti, révoqué un vendredi, et échoue chaque nuit sans alerte. Utiliser des identifiants de service limités et renouvelables, comme pour une application développée en code.

---

Pourquoi un webhook de workflow doit-il tolérer les événements livrés plusieurs fois ou dans le désordre ? <!--anki:6534373461653763386561313461363339656563643065393662616630623736-->
?
La **livraison d'un webhook** peut être répétée après une erreur ou retardée par le réseau. L'ordre d'arrivée ne garantit donc pas l'ordre métier.

Vérifier signature et fraîcheur, enregistrer un identifiant d'événement, puis dédupliquer avant l'effet. Pour un événement ancien, comparer la version de l'objet ou relire son état courant. Répondre après une prise en charge durable, selon le contrat du fournisseur. Tester doublon, retard et panne pendant l'écriture ; un workflow visuellement linéaire ne supprime pas ces cas distribués.

---

Pourquoi un déclenchement quotidien à heure locale demande-t-il une politique de changement d'heure ? <!--anki:6132663733613562646637663464386438383537643066303064653835363964-->
?
Au passage été/hiver, une heure locale peut **ne pas exister ou se produire deux fois**. « Tous les jours à 02 h 30 » n'est donc pas toujours une suite d'intervalles de 24 heures.

Définir le fuseau et la politique de saut ou doublon, puis identifier l'exécution par sa période métier. L'idempotence protège un doublon ; elle ne crée pas l'exécution manquante. Tester les transitions et les relances après arrêt du scheduler.

---

Que doit permettre une file d'échec pour un workflow automatisé ? <!--anki:6538373535376362333666383432353562373562363362353535353965396433-->
?
Elle doit conserver **l'événement, la cause et l'historique des tentatives** afin de diagnostiquer puis rejouer de façon contrôlée. Déplacer un message dans une file ne résout pas son problème.

Distinguer erreur corrigible de donnée invalide, corriger la cause puis rejouer avec le même identifiant métier si l'opération doit rester idempotente. Surveiller âge et volume de cette file. Un replay massif sans limite peut recréer la panne initiale.

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
- [[150-013-orchestration-pipelines-donnees|Transformations & orchestration des pipelines data]] — séparer orchestration et exécution des traitements
- [[00-moc-ai-engineering|MOC AI Engineering]]
