# Agents — Tests de contrats, pannes & reprises — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Vérifié le : 9 octobre 2026 — API citées confrontées aux documentations officielles ; limites explicitées dans les cartes.
<!-- summary: pyramide de tests, modèles simulés, invariants métier, fenêtres de panne, doubles commandes, concurrence, migrations, traces, évaluations et qualification de release. -->


Comment répartir les tests d'une application agentique ? <!--anki:3039663565653632366637393463383639616232376264373038636630623864-->
?
Tester **services et outils isolés**, orchestration avec modèle contrôlé, puis intégrations et qualité avec les vrais modèles. Chaque niveau répond à une question différente.

Un test métier vérifie permissions et calculs ; un test de graphe vérifie transitions et reprise ; une évaluation mesure la réussite sur des demandes représentatives. La validation de l'ensemble demande ces preuves complémentaires. Garder beaucoup de tests locaux rapides et un ensemble ciblé d'expériences plus coûteuses.

---

À ne pas confondre : modèle simulé et modèle réellement évalué ? <!--anki:6333313165376134663731323430366639383963666132346563633333643665-->
?
Un **modèle simulé** renvoie des réponses contrôlées pour provoquer un chemin précis. Il vérifie le code qui traite ces réponses, sans prouver qu'un vrai modèle saurait les produire.

Utiliser des réponses invalides, des appels d'outils multiples et des refus pour tester l'orchestration. Mesurer séparément la qualité avec un fournisseur réel et un jeu de cas figé. Un atelier sans clé API peut démontrer la reprise et l'isolation, pas une performance linguistique.

---

Quels invariants vérifier après une exécution agentique avec effet métier ? <!--anki:3365396438386664653865613434336662393664613465353366633136633130-->
?
Vérifier **l'état du système concerné** : opération autorisée, bonne cible, bon montant et absence de doublon. Les messages de l'agent ne constituent pas une preuve d'exécution.

Par exemple, consulter le registre des avoirs et le solde de la commande après une reprise. Tester également l'invariant négatif : aucun effet avant approbation ni après refus. Définir les preuves attendues avant d'écrire les scénarios pour éviter des assertions qui répètent seulement le code.

---

Où injecter des pannes pour tester la reprise d'un agent ? <!--anki:6239323236346462363766303439636262373332343361653835623831633433-->
?
Aux **frontières de validation** : avant l'effet, après son acceptation mais avant réception de la réponse, puis après la réponse mais avant le checkpoint. Ajouter le redémarrage pendant une attente humaine.

Ces emplacements distinguent absence d'effet, résultat ambigu et travail accompli non mémorisé. Compter les effets persistés après reprise avec la même identité d'opération. Un test qui ne plante qu'avant tout appel externe ne couvre pas la fenêtre la plus dangereuse.

---

Pourquoi fermer puis rouvrir le stockage dans un test de reprise LangGraph ? <!--anki:3032386561303835356234353435333938393030303139626134386465626130-->
?
Pour vérifier que la reprise dépend des **données persistées**, et non d'objets restés en mémoire. Reconstruire graphe, clients et connexions avant de continuer le même thread.

Un test encore plus fort lance un nouveau processus. Documenter ce que démontre le test : une exception Python n'est pas exactement une coupure de courant, et rouvrir SQLite ne valide pas une panne réseau PostgreSQL. Choisir les pannes en fonction des garanties visées.

---

Comment tester l'authentification et l'isolation d'un run d'agent ? <!--anki:3164303962656361306130663465313762613036393930393963613032393630-->
?
Créer deux identités et tenter **lecture, reprise, approbation, annulation et accès aux artefacts** du dossier de l'autre. Vérifier refus et absence de fuite dans le message d'erreur.

Ajouter un cas où un droit est révoqué entre création et approbation. Tester aussi les outils directement : l'API ne doit pas être le seul lieu de contrôle si le moteur possède un autre chemin d'accès. Utiliser uniquement des données et identités de test.

---

Comment tester deux approbations concurrentes pour une même action d'agent ? <!--anki:3736633738653664386331653438356161623564653863346136303033623862-->
?
Faire partir les requêtes ensemble avec une **barrière de synchronisation**, puis observer réponses et effet métier final. Répéter avec deux décisions identiques et deux décisions contradictoires.

L'application doit appliquer sa règle explicite : une seule transition acceptée, ou réutilisation sûre du résultat déjà fixé. Vérifier l'absence de doublon dans le registre métier. Un test séquentiel de double clic ne couvre pas la course entre lecture du statut et écriture de la décision.

---

Comment tester une approbation devenue obsolète ? <!--anki:3537653732653766363161353462663462316431633632343737383939373631-->
?
Créer une proposition, conserver sa référence, puis modifier une **précondition métier** ou produire une nouvelle proposition avant de soumettre l'ancienne décision.

L'exécution doit refuser l'action devenue incompatible ou demander une nouvelle validation, selon la règle définie. Contrôler la cible et le montant réellement écrits. Tester aussi expiration et changement de droits. Un simple test « oui/non » ne valide pas que l'approbation porte sur la bonne version.

---

Comment tester l'annulation sans masquer un effet externe déjà réalisé ? <!--anki:6135323765636262353536383462636138636563386239626163646439316633-->
?
Injecter la demande d'annulation **avant**, **pendant** et **après** l'effet. Vérifier ce que le client apprend et si une réconciliation ou une compensation est nécessaire.

Un moteur peut interrompre les étapes futures sans annuler un paiement accepté. Le statut final doit refléter cette réalité. Dans les tests, utiliser un service simulé qui distingue réception, validation et réponse afin d'exposer la course temporelle.

---

Comment tester un consommateur d'événements agentiques ? <!--anki:3335363230613162623535373465616639356336323735326436326166646337-->
?
Lui fournir des événements **dupliqués, retardés, interrompus et repris** selon le contrat du transport. Vérifier que son affichage converge vers le snapshot public courant.

Une rediffusion ne doit pas déclencher d'action métier. Tester un curseur expiré et un schéma d'événement inconnu après déploiement. Les garanties d'ordre doivent être celles du système utilisé, pas une hypothèse implicite de l'interface.

---

Pourquoi conserver des checkpoints historiques comme fixtures de migration ? <!--anki:3838363065336566346163643435643361643663323865643337383238373139-->
?
Ils représentent les **états réellement repris** après une mise à jour : champs manquants, ancien nom de nœud, proposition en attente et erreurs partielles.

Nettoyer les données sensibles et conserver la version du code qui les a produits. Tester la reprise avec le candidat, puis le rollback prévu. Une fixture fabriquée uniquement selon le nouveau schéma peut masquer précisément l'incompatibilité qu'on cherche à détecter.

---

Comment vérifier automatiquement les traces d'un atelier agentique sans service distant ? <!--anki:3430393663363633303339633434613461376435393833343935343432306638-->
?
Brancher un **exporteur local en mémoire** sur le SDK ou collecteur de test, puis vérifier noms, parents, attributs et absence de secrets synthétiques.

Cela valide l'instrumentation et les payloads exportés. Cela ne valide pas l'authentification, l'ingestion ou l'affichage d'une instance distante. Ajouter un test d'intégration distinct sur l'environnement cible lorsque celui-ci est disponible, avec un jeu de données autorisé et une rétention définie.

---

Comment organiser une évaluation d'agent qui modifie son environnement ? <!--anki:6233313030633133643334643464666338643638623132306166366336396364-->
?
Réinitialiser une **fixture indépendante par essai** : base, fichiers, mémoire et outils. Vérifier le résultat final depuis une source indépendante des déclarations de l'agent.

L'essai suivant ne doit pas profiter du travail du précédent ni échouer parce que sa commande est déjà traitée. Conserver aussi des scénarios explicitement consacrés à la continuité multi-tours. Un environnement réaliste mais incontrôlé rend les comparaisons difficiles à interpréter.

---

Calcul : 60 dossiers sont chacun évalués 4 fois pour deux versions d'agent. Chaque essai coûte fictivement 0,03 €, hors juge. Combien d'essais et quel budget minimal prévoir ? <!--anki:3431366134363630623562353439363661383231373633316432643330333363-->
?
**60 × 4 × 2 = 480 essais**, soit **480 × 0,03 = 14,40 €**. Ajouter séparément le coût des juges, de l'environnement et des tentatives supplémentaires.

Les répétitions renseignent la variabilité, mais ne créent pas 480 dossiers indépendants. Pour comparer les versions, garder les résultats regroupés par dossier et utiliser une analyse adaptée à cette dépendance. Prévoir un plafond de budget et une politique pour les essais interrompus.

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

---

Mise en situation : une nouvelle version d'agent améliore la qualité moyenne mais échoue au test « aucun effet avant approbation ». Peut-elle être promue ? <!--anki:6165633863326538636231313465336539633436316263376365613762663839-->
?
1. Bloquer la promotion selon l'invariant critique fixé à l'avance.
2. Localiser le chemin qui contourne le contrôle : outil, middleware, reprise ou délégation.
3. Corriger puis rejouer le scénario et les cas voisins.
4. Refaire la comparaison qualité/coût sur la version corrigée.

**Piège** : compenser une violation de permission par un meilleur score linguistique moyen.

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
