# CrewAI — Exécution fiable & intégration — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Vérifié le : 9 octobre 2026 — API citées confrontées aux documentations officielles ; limites explicitées dans les cartes.
<!-- summary: contrats de tâches, dépendances, guardrails bornés, budgets, async, persistance et checkpointing, délégation, isolation, instrumentation et tests. -->


Comment découper une crew CrewAI en tâches vérifiables ? <!--anki:3437303864316466363737393435623261313739336130656362623036353132-->
?
Donner à chaque tâche une **entrée identifiable**, un résultat attendu et un critère vérifiable. Séparer collecte de preuves, proposition et validation permet de localiser les erreurs.

Un découpage en « chercheur », « expert » et « directeur » ne suffit pas si leurs responsabilités se recouvrent. Pour un dossier support, demander des faits sourcés au premier agent et une proposition conforme à la politique au second. Garder l'exécution du geste commercial dans un service contrôlé.

---

Comment expliciter les dépendances entre tâches CrewAI ? <!--anki:6335633433623237333763653430313638363963656261363466393763616337-->
?
Utiliser le **`context`** de la tâche pour sélectionner les sorties amont nécessaires. Ne pas dépendre implicitement de tout l'historique ou supposer que deux tâches asynchrones terminent dans l'ordre de déclaration.

Dessiner le graphe des dépendances et repérer les étapes indépendantes. Une synthèse doit attendre toutes les analyses requises, ou annoncer explicitement les analyses manquantes. Tester une tâche amont lente, échouée ou ignorée pour vérifier le comportement réel.

---

À ne pas confondre : sortie brute, sortie structurée et preuve métier dans CrewAI ? <!--anki:3039373438323265646230353465353738326632396164386438663139366333-->
?
Une sortie **brute** est du texte ; une sortie **structurée** respecte un modèle lorsqu'elle est effectivement disponible ; une **preuve métier** établit que son contenu est correct dans le contexte de la tâche.

Après une tâche configurée avec `output_pydantic`, vérifier la présence de l'objet structuré dans `TaskOutput` et ses invariants. Une liste d'URL valides ne prouve pas que les pages soutiennent les affirmations. Conserver les identifiants des sources et vérifier les passages pertinents.

---

Comment écrire un guardrail CrewAI qui aide à corriger une proposition ? <!--anki:6530613565396335386363653439613762653839306236383435316232303537-->
?
Produire un verdict explicite et un **motif actionnable**. Un guardrail fonctionnel reçoit la sortie de tâche et renvoie un couple `(succès, résultat_ou_erreur)`.

Vérifier par exemple que toutes les références citées appartiennent aux sources fournies. En cas d'échec, préciser les références inconnues sans exposer de données sensibles. Le guardrail doit rester sans effet métier : il peut être appelé plusieurs fois et ne doit pas lui-même envoyer un e-mail ou créer un avoir.

---

Pourquoi borner séparément les corrections de guardrail et les reprises techniques CrewAI ? <!--anki:6136323939653263376461623462306239323264636633393330613530396237-->
?
Une **correction de contenu** sollicite de nouveau l'agent ; un **retry technique** recommence un appel ayant échoué. Ils répondent à des causes différentes et peuvent se cumuler.

Configurer notamment `guardrail_max_retries`, puis prévoir un état terminal quand aucune sortie acceptable n'est obtenue. Garder un budget partagé avec les retries du fournisseur. Ne pas assouplir automatiquement un validateur parce que l'agent échoue à le satisfaire : une tâche peut réellement être impossible.

---

Que mesurent max_iter, max_rpm et max_execution_time dans CrewAI ? <!--anki:6134373630306433333862313434663762663430323161623437316437353737-->
?
Ces paramètres bornent respectivement les **itérations**, le **débit d'appels** et la **durée d'exécution** selon leur périmètre dans le framework. Aucun n'est à lui seul un plafond financier pour tout un workflow.

Une itération peut traiter beaucoup de tokens ; un manager et des agents délégués peuvent ajouter leurs propres appels. Mesurer les coûts réels et imposer le budget global au niveau application/gateway. Tester l'épuisement de chaque limite et le résultat rendu au client.

---

À ne pas confondre : lancement asynchrone d'une crew et exécution durable ? <!--anki:3539376536343138363931613438623039343262396235386637343732636236-->
?
Un lancement **asynchrone** libère l'appelant pour d'autres tâches. Une exécution **durable** conserve assez d'informations pour récupérer après la disparition du processus.

Un objet awaitable ne constitue donc pas une file persistante. Pour un traitement long, enregistrer la demande, définir la stratégie de reprise et utiliser un stockage accessible au worker suivant. Vérifier l'API async de la version installée et les comportements des outils synchrones, qui peuvent continuer malgré l'annulation de l'appelant.

---

Comment éviter qu'une exécution CrewAI par lot sature les fournisseurs ? <!--anki:3637643838666537316462343432313262376436346332343461663437383630-->
?
Borner le **nombre de dossiers actifs**, en plus des limites par agent. Un lot de 100 dossiers contenant chacun plusieurs agents peut multiplier brutalement les appels.

Faire respecter quotas et équité entre clients avec une file et un budget partagés. Mesurer attente, appels simultanés et retries. Pour les dossiers indépendants, isoler état, mémoire et résultats ; l'échec d'un élément doit avoir un statut propre plutôt que rendre tout le lot opaque.

---

À ne pas confondre : persist d'un Flow CrewAI et checkpoint d'exécution ? <!--anki:6239373931636131373734353438393338376638613662626431306632366438-->
?
**`@persist`** sauvegarde l'état du Flow aux points configurés. Le **checkpointing** des versions récentes peut enregistrer des informations d'exécution pour reprendre ou bifurquer crews, flows et agents.

Réhydrater un état ne prouve pas que toutes les étapes déjà achevées seront sautées. Choisir un mécanisme en fonction de sa granularité, du stockage et de la version utilisée ; tester la mort du processus entre une action externe et sa sauvegarde. Les deux nécessitent des effets métier idempotents.

---

Pourquoi vérifier l'existence d'un état avant une reprise de Flow CrewAI ? <!--anki:6637386362613135363432643466346138666635643738336336386262303663-->
?
Une reprise doit retrouver **le dossier attendu**. Dans la documentation versionnée consultée, un identifiant de restauration introuvable peut conduire à repartir sans l'état attendu plutôt qu'à échouer explicitement.

Le service applicatif doit donc valider existence, propriétaire et version avant la reprise. Distinguer reprise du même dossier et fork vers une nouvelle identité. Ne pas utiliser un fichier local perdu au redéploiement comme seule preuve que le dossier existe.

---

Comment limiter les risques d'une délégation CrewAI ? <!--anki:3530323039346339356331323432366638613439323839616465613064313132-->
?
Définir une **mission bornée**, des outils autorisés, un format de retour et un budget pour l'agent délégué. Le manager doit pouvoir distinguer échec, manque de preuve et réussite.

Éviter les délégations circulaires en limitant profondeur et répétitions. Vérifier que la délégation ne confère pas davantage de droits que l'appelant. Comparer au même workflow sans délégation : une collaboration qui ajoute coût et ambiguïté sans améliorer la réussite doit être simplifiée.

---

Comment isoler deux clients qui utilisent la même configuration CrewAI ? <!--anki:3061373565343965346532613435656461636233663537316365346533366631-->
?
Séparer leurs **états, mémoires, accès aux sources et destinations d'artefacts**. Les objets mutables et caches réutilisés entre requêtes demandent une attention particulière.

Injecter les identités depuis le service authentifié et contrôler les droits dans les outils. Une préférence mémorisée pour un client ne doit pas être rappelée chez un autre. Tester deux dossiers intercalés, avec une même formulation de question, puis vérifier résultats, stockage et traces.

---

Que faut-il instrumenter dans une application CrewAI au-delà de kickoff ? <!--anki:3132326134333863653331663430353738633639643334616166373739323934-->
?
Relier **Flow, crew, tâches, appels de modèles et outils** à une exécution applicative. Enregistrer les reprises, corrections de guardrail, délégations et résultats métier permet de localiser coûts et échecs.

Les listeners d'événements et intégrations d'observabilité servent à cette instrumentation ; vérifier qu'ils couvrent les chemins async et les branches d'erreur. Un callback de fin ne remplace pas un journal métier durable. Ne pas compter deux fois un appel capturé à la fois par le framework et par la gateway.

---

Calcul : une crew utilise 3 agents ; chacun fait exactement 4 appels à 0,01 € par appel, et le manager en ajoute 3 au même tarif. Quel est le coût d'une exécution, puis de 500 exécutions sans retry ? <!--anki:3164616533336461353932623430303338356136373764653632666138353933-->
?
**(3 × 4 + 3) × 0,01 = 0,15 €** par exécution, puis **500 × 0,15 = 75 €**. Les tarifs sont fictifs et supposent des appels de coût identique.

Ce calcul montre le coût de coordination : le manager ajoute ici 0,03 €, soit 25 % du coût des agents seuls. Les appels réels varient avec les tokens, la mémoire, les corrections et les retries ; mesurer ces postes avant de généraliser.

---

## Mises en situation

Mise en situation : une crew CrewAI cite des pages accessibles mais qui ne soutiennent pas ses conclusions. Quel contrôle ajoutes-tu ? <!--anki:3764323465323664373863393434656439306430393163616162623163623465-->
?
1. Conserver les preuves récupérées avec identifiants et passages pertinents.
2. Vérifier que les références produites correspondent à ces preuves.
3. Évaluer le soutien de chaque affirmation importante par son passage cité.
4. Borner les corrections et permettre l'abstention en l'absence de preuve.

**Piège** : assimiler HTTP 200 à une vérification de vérité.

---

Mise en situation : après un redéploiement, un Flow CrewAI retrouve ses variables mais recommence une étape de facturation. Comment diagnostiques-tu le problème ? <!--anki:3034633234356663346161353435373038616332643537383230346561396235-->
?
1. Identifier le mécanisme utilisé : réhydratation d'état ou checkpoint d'exécution.
2. Vérifier l'identité du dossier, les marqueurs d'avancement et le stockage partagé.
3. Protéger la facturation par une identité métier stable et une déduplication atomique.
4. Reproduire un arrêt après facturation mais avant persistance.

**Piège** : considérer que retrouver le montant dans l'état signifie que la facture a été enregistrée dans le graphe d'exécution.

---

Mise en situation : une crew hiérarchique produit de meilleurs rapports mais dépasse régulièrement le budget. Comment décides-tu de la conserver ? <!--anki:3035633832313862663335323466313939303231616262313934313939613838-->
?
1. Comparer les mêmes dossiers au séquentiel, avec évaluateur et critères fixes.
2. Mesurer coût par réussite, latence et taux de dépassement, pas seulement la moyenne des scores.
3. Attribuer le surcoût aux délégations, au manager et aux corrections.
4. Réserver le mode hiérarchique aux cas où le gain justifie son coût, avec arrêt borné.

**Piège** : considérer le manager comme gratuit parce qu'il ne produit pas le document final.

---

## Sources
- [CrewAI — tâches, documentation 1.15.26](https://docs.crewai.com/v1.15.26/en/concepts/tasks)
- [CrewAI — agents et limites](https://docs.crewai.com/v1.15.26/en/concepts/agents)
- [CrewAI — Flows et restauration](https://docs.crewai.com/v1.15.26/en/concepts/flows)
- [CrewAI — checkpointing](https://docs.crewai.com/v1.15.26/en/concepts/checkpointing)
- [CrewAI — architecture de production](https://docs.crewai.com/v1.15.26/en/concepts/production-architecture)

## Connexions
- [[46-crewai-crews|CrewAI — Crews]] — contrats et exécution des tâches
- [[47-crewai-flows|CrewAI — Flows]] — reprise et intégration applicative
- [[36-orchestration-agents|Orchestration multi-agents]] — dépendances et délégation
- [[98-debogage-agents|Débogage des agents]] — attribuer les erreurs aux étapes
- [[140-011-architecture-applications-agentiques|Applications agentiques — Architecture & cycle de vie]] — placer les crews dans le service
- [[90-013-tests-agents-reprises|Agents — Tests de contrats, pannes & reprises]] — tester tâches et reprises
- [[00-moc-ai-engineering|MOC AI Engineering]]
