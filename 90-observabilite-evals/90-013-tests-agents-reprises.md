# Agents — Tests de contrats, pannes & reprises — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Vérifié le : 9 octobre 2026 — API citées confrontées aux documentations officielles ; limites explicitées dans les cartes.
<!-- summary: pyramide de tests, modèles simulés, invariants métier, fenêtres de panne, doubles commandes, concurrence, migrations, traces, évaluations et qualification de release, injection de panne après effet métier. -->


Comment répartir les tests d'une application agentique ? <!--anki:3039663565653632366637393463383639616232376264373038636630623864-->
?
Tester **services et outils isolés**, orchestration avec modèle contrôlé, puis intégrations et qualité avec les vrais modèles. Chaque niveau répond à une question différente.

Un test métier vérifie permissions et calculs ; un test de graphe vérifie transitions et reprise ; une évaluation mesure la réussite sur des demandes représentatives. Exemple : l'atelier `examples/agentic-support` exécute 18 tests sans clé API, puis déclare explicitement la qualité du vrai modèle `not_evaluated`. Garder beaucoup de tests locaux rapides et un ensemble ciblé d'expériences plus coûteuses.

---

À ne pas confondre : modèle simulé et modèle réellement évalué ? <!--anki:6333313165376134663731323430366639383963666132346563633333643665-->
?
Un **modèle simulé** renvoie des réponses contrôlées pour provoquer un chemin précis. Il vérifie le code qui traite ces réponses, sans prouver qu'un vrai modèle saurait les produire.

Utiliser des réponses invalides, des appels d'outils multiples et des refus pour tester l'orchestration. Exemple : un `GenericFakeChatModel` de LangChain renvoie `{"amount_cents": -1}` ; le test vérifie que la validation arrête ce montant avant toute approbation. Mesurer séparément la qualité avec un fournisseur réel et un jeu de cas figé. Un atelier sans clé API peut démontrer la reprise et l'isolation, pas une performance linguistique.

---

Quels invariants vérifier après une exécution agentique avec effet métier ? <!--anki:3365396438386664653865613434336662393664613465353366633136633130-->
?
Vérifier **l'état du système concerné** : opération autorisée, bonne cible, bon montant et absence de doublon. Les messages de l'agent ne constituent pas une preuve d'exécution.

Par exemple, après une reprise, `SELECT count(*) FROM refunds` doit valoir 1 pour ce dossier, et le solde de la commande baisser du seul montant approuvé. Tester également l'invariant négatif : aucun effet avant approbation ni après refus. Définir les preuves attendues avant d'écrire les scénarios pour éviter des assertions qui répètent seulement le code.

---

Où injecter des pannes pour tester la reprise d'un agent ? <!--anki:6239323236346462363766303439636262373332343361653835623831633433-->
?
Aux **frontières de validation** : avant l'effet, après son acceptation mais avant réception de la réponse, puis après la réponse mais avant le checkpoint. Ajouter le redémarrage pendant une attente humaine.

Pour un remboursement, chaque fenêtre a son résultat attendu : panne avant l'appel, zéro avoir ; après acceptation mais avant la réponse, un état inconnu à réconcilier ; après la réponse mais avant le checkpoint, un avoir que la reprise ne doit pas dupliquer. Compter les effets persistés avec la même identité d'opération. Un test qui ne plante qu'avant tout appel externe ne couvre pas la fenêtre la plus dangereuse.

---

Pourquoi fermer puis rouvrir le stockage dans un test de reprise LangGraph ? <!--anki:3032386561303835356234353435333938393030303139626134386465626130-->
?
Pour vérifier que la reprise dépend des **données persistées**, et non d'objets restés en mémoire. Reconstruire graphe, clients et connexions avant de continuer le même thread.

Un test encore plus fort lance un nouveau processus. Dans l'atelier support, un processus fils quitte avec le code 73 juste après le COMMIT métier ; le test reconstruit le moteur depuis les fichiers SQLite et exige un seul avoir. Documenter ce que démontre le test : rouvrir SQLite ne valide pas une panne réseau PostgreSQL.

---

Comment tester l'authentification et l'isolation d'un run d'agent ? <!--anki:3164303962656361306130663465313762613036393930393963613032393630-->
?
Créer deux identités et tenter **lecture, reprise, approbation, annulation et accès aux artefacts** du dossier de l'autre. Vérifier refus et absence de fuite : avec le jeton de Bob, `GET /runs/{id}` sur un dossier d'Alice renvoie la même réponse 404 qu'un identifiant inexistant.

Ajouter un cas où un droit est révoqué entre création et approbation. Tester aussi les outils directement : l'API ne doit pas être le seul lieu de contrôle si le moteur possède un autre chemin d'accès. Utiliser uniquement des données et identités de test.

---

Comment tester deux approbations concurrentes pour une même action d'agent ? <!--anki:3736633738653664386331653438356161623564653863346136303033623862-->
?
Faire partir les requêtes ensemble avec une **barrière de synchronisation**, puis observer réponses et effet métier final. Répéter avec deux décisions identiques et deux décisions contradictoires.
```python
barrier = threading.Barrier(2)
def approve():
    barrier.wait(timeout=5)          # les deux threads partent ensemble
    return engine.decide("alice", run_id, digest, True)
```
L'application doit appliquer sa règle explicite : une seule transition acceptée, ou réutilisation sûre du résultat déjà fixé. Vérifier l'absence de doublon dans le registre métier. Un test séquentiel de double clic ne couvre pas la course entre lecture du statut et écriture de la décision.

---

Comment tester une approbation devenue obsolète ? <!--anki:3537653732653766363161353462663462316431633632343737383939373631-->
?
Créer une proposition, conserver sa référence, puis modifier une **précondition métier** ou produire une nouvelle proposition avant de soumettre l'ancienne décision.

L'exécution doit refuser l'action devenue incompatible ou demander une nouvelle validation, selon la règle définie. Exemple : la décision porte l'empreinte de la proposition calculée sur la version 3 de la commande ; si la commande passe en version 4 avant l'exécution, aucun avoir ne doit être écrit. Tester aussi expiration et changement de droits. Un simple test « oui/non » ne valide pas que l'approbation porte sur la bonne version.

---

Comment tester l'annulation sans masquer un effet externe déjà réalisé ? <!--anki:6135323765636262353536383462636138636563386239626163646439316633-->
?
Injecter la demande d'annulation **avant**, **pendant** et **après** l'effet. Vérifier ce que le client apprend et si une réconciliation ou une compensation est nécessaire.

Un moteur peut interrompre les étapes futures sans annuler un paiement accepté. Exemple : l'annulation arrive 200 ms après l'acceptation du remboursement par le prestataire ; le statut final doit indiquer « remboursé, annulation trop tardive », pas « annulé ». Dans les tests, utiliser un service simulé qui distingue réception, validation et réponse afin d'exposer la course temporelle.

---

Comment tester un consommateur d'événements agentiques ? <!--anki:3335363230613162623535373465616639356336323735326436326166646337-->
?
Lui fournir des événements **dupliqués, retardés, interrompus et repris** selon le contrat du transport. Vérifier que son affichage converge vers le snapshot public courant.

Exemple : le consommateur reçoit les événements 41, 42, 42, 44 puis 43. Il ignore le doublon, comble le trou avant d'afficher 44 ou recharge le snapshot, et n'envoie jamais un second e-mail. Tester un curseur expiré et un schéma d'événement inconnu après déploiement. Les garanties d'ordre doivent être celles du système utilisé, pas une hypothèse implicite de l'interface.

---

Pourquoi conserver des checkpoints historiques comme fixtures de migration ? <!--anki:3838363065336566346163643435643361643663323865643337383238373139-->
?
Ils représentent les **états réellement repris** après une mise à jour : champs manquants, ancien nom de nœud, proposition en attente et erreurs partielles.

Exemple : un checkpoint de la v1, en attente d'approbation, ne contient pas le champ `policy_version` ajouté en v2. Repris par le candidat, il doit obtenir une valeur explicite ou un refus clair, pas un `KeyError` en production. Nettoyer les données sensibles et tester aussi le rollback prévu. Une fixture fabriquée uniquement selon le nouveau schéma peut masquer précisément l'incompatibilité qu'on cherche à détecter.

---

Comment vérifier automatiquement les traces d'un atelier agentique sans service distant ? <!--anki:3430393663363633303339633434613461376435393833343935343432306638-->
?
Brancher un **exporteur local en mémoire** sur le SDK ou collecteur de test, puis vérifier noms, parents, attributs et absence de secrets synthétiques.
```python
spans = exporter.get_finished_spans()     # InMemorySpanExporter d'OpenTelemetry
roots = {s.context.span_id for s in spans if s.name == "support-run"}
commits = [s for s in spans if s.name == "commit-refund"]
assert roots and commits
assert all(s.parent is not None and s.parent.span_id in roots for s in commits)
```
Cela valide l'instrumentation et les payloads exportés. Cela ne valide pas l'authentification, l'ingestion ou l'affichage d'une instance distante. Ajouter un test d'intégration distinct sur l'environnement cible lorsque celui-ci est disponible, avec un jeu de données autorisé et une rétention définie.

---

Comment organiser une évaluation d'agent qui modifie son environnement ? <!--anki:6233313030633133643334643464666338643638623132306166366336396364-->
?
Réinitialiser une **fixture indépendante par essai** : base, fichiers, mémoire et outils. Vérifier le résultat final depuis une source indépendante des déclarations de l'agent.

Sinon, l'essai 2 trouve la commande déjà remboursée par l'essai 1 et répond « déjà traité » : un succès apparent pour une mauvaise raison. Copier une base de référence dans un répertoire temporaire avant chaque essai évite ce biais. Conserver aussi des scénarios explicitement consacrés à la continuité multi-tours. Un environnement réaliste mais incontrôlé rend les comparaisons difficiles à interpréter.

---

Calcul : 60 dossiers sont chacun évalués 4 fois pour deux versions d'agent. Chaque essai coûte fictivement 0,03 €, hors juge. Combien d'essais et quel budget minimal prévoir ? <!--anki:3431366134363630623562353439363661383231373633316432643330333363-->
?
**60 × 4 × 2 = 480 essais**, soit **480 × 0,03 = 14,40 €**. Ajouter séparément le coût des juges, de l'environnement et des tentatives supplémentaires.

Les répétitions renseignent la variabilité, mais ne créent pas 480 dossiers indépendants. Pour comparer les versions, garder les résultats regroupés par dossier et utiliser une analyse adaptée à cette dépendance. Prévoir un plafond de budget et une politique pour les essais interrompus.

---

Comment un test par injection de panne peut-il vérifier l'idempotence réelle d'un agent ? <!--anki:6433373732643039336232633436346562316133313332623731636161396437-->
?
Placer une **panne contrôlée juste après l'effet métier**, avant son acquittement ou son checkpoint, puis reprendre la même opération avec la même identité logique.

Vérifier l'état final dans le système cible : un seul effet, résultat récupérable et statut cohérent. Répéter avant l'effet et après l'acquittement pour couvrir les frontières. Tester aussi deux reprises concurrentes. Compter seulement les appels d'outils ne suffit pas : plusieurs appels peuvent correctement retrouver le même effet, tandis qu'un seul appel peut en produire plusieurs si le service aval est mal conçu.

---

## Mises en situation

Mise en situation : tous les tests d'un agent passent avec un modèle simulé, mais le vrai modèle appelle le mauvais outil. Quel niveau de test manque ? <!--anki:6333663431633539646266663462666338313739643237643138626238343339-->
?
1. Garder les tests contrôlés qui prouvent le traitement correct des demandes.
2. Ajouter des évaluations du choix d'outil avec le vrai modèle sur des tâches représentatives.
3. Mesurer arguments, permissions, résultat final et coûts, avec plusieurs essais si nécessaire.
4. Transformer les erreurs observées en nouveaux cas de régression.

**Piège** : remplacer tous les tests locaux par des appels coûteux au modèle, sans isoler la cause.

---

Mise en situation : la reprise d'un agent passe en test, mais un arrêt du worker produit des doublons en production. Comment renforces-tu la preuve ? <!--anki:3534396162363766366566633464313339646666343936653631336266346432-->
?
1. Vérifier où le test injecte la panne par rapport à l'effet et au checkpoint.
2. Provoquer un arrêt après validation métier, avant sauvegarde du résultat.
3. Reconstruire le moteur depuis le stockage puis reprendre la même opération.
4. Contrôler le registre métier indépendamment du texte rendu par l'agent.

**Piège** : vérifier seulement que le graphe finit par retourner `success`.

Détruire l'instance du worker, puis la reconstruire comme en production, avec le même stockage et la même clé d'opération. Un test qui garde les variables en mémoire peut masquer précisément la fenêtre où naissent les doublons.

---

Mise en situation : une nouvelle version d'agent améliore la qualité moyenne mais échoue au test « aucun effet avant approbation ». Peut-elle être promue ? <!--anki:6165633863326538636231313465336539633436316263376365613762663839-->
?
1. **Bloquer la promotion** : « aucun effet avant approbation » est un invariant critique, pas une composante compensable de la moyenne.
2. **Confirmer l'effet réellement observé** avec le registre métier ou un double d'outil enregistrant les opérations ; ne pas se fier au texte de l'agent.
3. **Localiser le chemin fautif** : outil, middleware, reprise, délégation ou concurrence.
4. **Corriger au point d'exécution**, puis tester refus, absence d'approbation, expiration et proposition modifiée ; vérifier zéro effet dans chaque cas interdit.
5. **Rejouer les contrôles et les evals** sur la version corrigée, car la correction peut changer qualité, coût et délai.

**Piège** : relever le score de qualité global pour masquer une régression d'autorisation.

---

## Sources
- [LangGraph — tests des nœuds et graphes](https://docs.langchain.com/oss/python/langgraph/test)
- [LangChain — stratégie de tests](https://docs.langchain.com/oss/python/langchain/test)
- [Anthropic — évaluations d’agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [LangGraph — interruptions et reprise](https://docs.langchain.com/oss/python/langgraph/interrupts)

## Connexions
- [[96-evals-rag-agents|Évaluations RAG & agents]] — mesurer les résultats métier
- [[94-evals-methodologie|Méthodologie des évaluations]] — jeux et critères de réussite
- [[40-010-langchain-outils-middleware-production|LangChain — Production]] — tester outils et contrats
- [[40-011-langgraph-reprise-concurrence|LangGraph — Reprise]] — injecter des pannes
- [[40-012-crewai-execution-fiable|CrewAI — Production]] — tester tâches et reprises
- [[140-011-architecture-applications-agentiques|Architecture agentique]] — valider le cycle de vie
- [[00-moc-ai-engineering|MOC AI Engineering]]
