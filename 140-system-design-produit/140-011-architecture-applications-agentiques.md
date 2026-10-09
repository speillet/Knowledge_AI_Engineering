# Applications agentiques — Architecture & cycle de vie — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Vérifié le : 9 octobre 2026 — API citées confrontées aux documentations officielles ; limites explicitées dans les cartes.
<!-- summary: choix des briques, contrats d’exécution, API et workers, admission, identité, approbations versionnées, annulation, événements, déploiement et capacité. -->


Comment choisir les briques nécessaires à une application agentique ? <!--anki:6264333961356665313630323462663361383062303936656332656432666539-->
?
Partir du **processus métier** : étapes, outils, état, critères de fin et contraintes d'exploitation. LangChain fournit des abstractions et une boucle d'agent ; LangGraph permet de contrôler un graphe ; CrewAI organise tâches et rôles ; Langfuse observe et évalue.

Ces rôles ne rendent pas obligatoire leur assemblage complet. Retenir les composants qui résolvent un besoin vérifié, avec une frontière claire entre eux. Un simple appel structuré peut suffire pour classifier ; la reprise et les validations longues justifient davantage d'orchestration.

---

Quel contrat définir entre l'API et le moteur d'un agent ? <!--anki:3861623432653065393030613435363161393439643862633131643463336433-->
?
Un contrat **d'exécution métier** : entrée validée, identité autorisée, statut, résultat et erreur structurée. Prévoir des opérations distinctes pour soumettre, consulter, approuver et annuler.

Garder les classes internes du framework derrière un adaptateur facilite tests et migrations. Le client ne devrait pas devoir comprendre tous les champs du graphe ni envoyer un `Command` arbitraire. Versionner les événements publics et les états visibles, car une interface peut rester ouverte pendant un déploiement.

---

Pourquoi un statut HTTP 202 ne prouve-t-il pas qu'un agent terminera sa tâche ? <!--anki:3432643964376361316164653430386238323966323839376264353135303734-->
?
Il signifie que la demande a été **acceptée pour traitement**, sans résultat final garanti. Avant de l'émettre, rendre la demande récupérable dans un stockage durable ou expliciter une garantie plus faible.

Renvoyer un identifiant et une URL de suivi. Le contrat doit expliquer échec, expiration et annulation. Un client qui reçoit 202 doit encore pouvoir consulter un état après redémarrage du serveur ; une simple tâche en mémoire peut disparaître entre-temps.

---

Pourquoi une tâche en arrière-plan FastAPI ne remplace-t-elle pas une file durable pour un agent ? <!--anki:6333353032356330366636623464326562356133633331623235376136376135-->
?
Elle peut exécuter un travail après la réponse dans le **processus applicatif**, sans fournir à elle seule stockage durable, reprise par un autre worker et coordination distribuée.

Pour un traitement qui doit survivre à un crash, persister demande et statut, puis organiser la consommation et les reprises. Réserver les tâches locales aux besoins compatibles avec leurs limites. Le caractère « background » décrit le moment d'exécution, pas une garantie de livraison ou de persistance.

---

Quels états publics exposer pour suivre un run d'agent ? <!--anki:3836303230303530343036323433313738626533613866323630636164643265-->
?
Définir une **machine à états explicite** : accepté, en cours, en attente d'approbation, puis terminé, échoué ou annulé selon les transitions permises. Conserver aussi les causes et l'éventuelle possibilité de reprise.

Une panne technique peut laisser une action externe dans un état inconnu ; exposer alors une phase de vérification plutôt qu'annoncer un échec sans effet. Distinguer « demande d'annulation reçue » et « travail effectivement arrêté ». Tester les transitions interdites et concurrentes.

---

Comment traiter une soumission répétée avec la même clé d'idempotence ? <!--anki:3466386264396533643734363439383662343236636236343335633839616635-->
?
Lier la clé à un **périmètre authentifié** et à une empreinte des entrées. Même clé et même contenu retrouvent l'opération ; même clé et contenu différent produisent un conflit explicite.

La réservation de la clé doit être atomique avec la création du dossier. Fixer durée de rétention et comportement pour une opération encore en cours. Cette protection à l'entrée ne suffit pas pour les outils : chaque effet métier doit aussi posséder une identité stable lors des reprises.

---

Pourquoi vérifier les droits à chaque consultation et reprise d'un agent ? <!--anki:3562336635343335663739313437353939393666346533613336646231653566-->
?
Un identifiant de run ou de thread désigne une **ressource**, pas son propriétaire. Vérifier les droits sur lecture, événements, téléchargement d'artefact, approbation et annulation.

Reconstruire l'identité depuis l'authentification ; ne pas faire confiance à un tenant fourni dans l'état par le client. Les droits peuvent changer pendant une attente humaine. Les revérifier avant une action sensible, même si le dossier avait été créé par une personne autorisée.

---

Que doit contenir une proposition d'action soumise à approbation humaine ? <!--anki:3935333239373430343839623439373038336333663934343065363566373031-->
?
Une **action précise et versionnée** : type, cible, arguments effectifs, conséquences et expiration. Associer la décision à son identifiant ou empreinte, à l'identité du décideur et à l'heure.

Si le montant ou le destinataire change, l'approbation précédente ne doit plus s'appliquer. Afficher ces éléments dans l'interface et vérifier leur correspondance côté serveur. Le modèle peut préparer la proposition ; il ne doit pas pouvoir fabriquer la preuve de son approbation.

---

Comment éviter qu'une approbation valide devienne dangereuse pendant l'attente ? <!--anki:3431653135316132386233393437396439376364616535633434353639653938-->
?
Revérifier les **préconditions métier au moment d'exécuter** : état courant, version de la ressource, droits et expiration. Une approbation concerne une proposition, pas un droit de modifier arbitrairement la ressource plus tard.

Par exemple, un autre opérateur peut avoir remboursé la commande pendant l'attente. Une écriture conditionnelle doit détecter ce changement et demander réconciliation ou nouvelle validation. Conserver l'approbation dans le checkpoint ne supprime pas cette course temporelle.

---

À ne pas confondre : déconnexion de l'interface et annulation du run agentique ? <!--anki:3565643836393762386136363439626462306136303531333830313763366461-->
?
La **déconnexion** arrête un canal de suivi ; l'**annulation** demande l'arrêt du travail. Une tâche longue peut continuer quand le navigateur se ferme, puis être consultée plus tard.

Définir cette politique par type de tâche. Une annulation doit être authentifiée, persistée et propagée aux composants capables de l'appliquer. Si une action externe a déjà été validée, annoncer son état réel et prévoir une compensation métier si nécessaire. Fermer un flux ne remonte pas le temps.

---

Comment publier des événements d'agent sans exposer son état interne complet ? <!--anki:3166333235316633336561343439303939623930623466353266663937363030-->
?
Transformer les mises à jour internes en **événements publics filtrés** : étape, progression, demande d'approbation, résultat ou erreur admissible. Définir un schéma et vérifier les droits avant émission.

L'état peut contenir secrets, instructions internes ou résultats d'outils appartenant à un autre périmètre. Une simple sérialisation de `state` est donc un mauvais contrat d'interface. Ne pas afficher des raisonnements internes comme preuve de vérité ; privilégier actions réalisées et sources utiles.

---

Que faire quand le curseur de reprise d'un flux d'agent a expiré ? <!--anki:6665663637613136623531653438633239386364343436623866353039343263-->
?
Détecter que les anciens événements ne sont **plus disponibles**, puis proposer un snapshot public courant et un nouveau point de reprise. Ne pas inventer les événements manquants ni relancer automatiquement le travail.

Le client doit pouvoir reconstruire son affichage depuis cet état. Documenter la rétention du journal d'événements séparément de celle des résultats et checkpoints. Tester reconnexion après expiration, doublons et événements arrivant pendant la récupération du snapshot.

---

Comment gérer un client lent qui consomme les événements d'un agent ? <!--anki:3931363834636564346563383437326339303533666135626233383565393332-->
?
Borner les **buffers par connexion** et choisir une politique : agréger la progression, couper le canal avec possibilité de reprise, ou ralentir le producteur lorsque c'est acceptable.

Un client lent ne doit pas épuiser la mémoire du worker ni bloquer tous les autres dossiers. Conserver les événements métier indispensables dans un journal approprié ; les fragments de texte intermédiaires peuvent avoir une politique différente. Mesurer taille des buffers, retard du consommateur et reconnexions.

---

Comment déployer une nouvelle version d'un agent alors que des runs sont actifs ? <!--anki:6637623834303762656266353438323162316432633161323937363139663965-->
?
Maintenir une **compatibilité de code, d'état et de contrats** pour les exécutions en cours. Selon le système, drainer les workers anciens, router les reprises vers leur version ou migrer explicitement les états.

Tester des dossiers interrompus avant et après chaque frontière importante. Un rollback de conteneur ne suffit pas si le stockage a déjà été transformé de façon incompatible. Tracer la version du workflow et conserver les artefacts nécessaires pour diagnostiquer les reprises.

---

Calcul : une application reçoit en moyenne 2 nouveaux dossiers agentiques par seconde ; chaque dossier attend 10 min une approbation, avec un régime stable. Combien de dossiers attendent en moyenne ? <!--anki:3134653638656362386132353463366339663161336135613561643033373162-->
?
Par la loi de Little, **2 × 600 = 1 200 dossiers** attendent en moyenne. L'hypothèse de stabilité signifie notamment que les approbations suivent ce débit sur la durée.

Cela dimensionne stockage, interface de revue et capacité humaine. Cela ne signifie pas qu'il faut 1 200 appels LLM ou connexions HTTP actifs : une pause durable doit libérer les ressources de calcul inutiles. Si les décisions arrivent moins vite que les dossiers, la file croît.

---

Comment choisir un indicateur de réussite pour une application agentique ? <!--anki:3530663737643839636232373437323561626434303939636262366435663638-->
?
Mesurer le **résultat métier vérifié**, avec coût et délai sur le même périmètre. Pour un agent support : dossier correctement résolu, sans action interdite, dans le délai prévu.

Un run techniquement terminé peut avoir renvoyé une réponse inutilisable ; une escalade justifiée peut au contraire être le résultat attendu. Définir catégories, dénominateurs et segments avant lancement. Relier traces et états métier pour expliquer les échecs sans confondre succès HTTP et succès utilisateur.

---

## Mises en situation

Mise en situation : un utilisateur approuve un remboursement de 20 €, mais le modèle modifie ensuite la proposition à 80 €. Quel contrôle doit empêcher l'exécution ? <!--anki:3731316438363064336638353463663839366236373134356265633036303964-->
?
1. Rendre la proposition approuvée immuable et identifiable par version ou empreinte.
2. Vérifier que l'action à exécuter correspond exactement à cette proposition.
3. Refuser la décision obsolète et demander une nouvelle validation si le contenu change.
4. Revérifier les préconditions métier au moment de l'écriture.

**Piège** : stocker seulement `approved=True` dans un état librement modifiable.

---

Mise en situation : l'API renvoie 202, puis le serveur redémarre et le dossier disparaît. Comment rends-tu la garantie d'acceptation réelle ? <!--anki:3062336239386663313035623463643338353637616334373362363466323865-->
?
1. Persister le dossier et sa clé d'idempotence avant l'accusé d'acceptation.
2. Rendre sa mise en traitement récupérable, par exemple avec un outbox ou un worker qui lit les dossiers en attente.
3. Exposer un statut consultable et une politique de reprise.
4. Tester le crash avant et après chaque validation de stockage.

**Piège** : ajouter uniquement une tâche asynchrone au processus qui vient de répondre.

---

Mise en situation : après une reconnexion SSE, le client reçoit de nouveau l'événement « proposition prête ». Comment évites-tu un second remboursement ? <!--anki:6530336362643662643162393431343361663536656531386338636139636531-->
?
1. Traiter l'événement comme une information d'affichage, jamais comme un ordre d'exécuter.
2. Dédupliquer l'affichage par identifiant d'événement.
3. Exiger une commande d'approbation authentifiée liée à la proposition.
4. Dédupliquer aussi l'opération métier, indépendamment du transport SSE.

**Piège** : déclencher un effet irréversible à chaque réception d'un événement de progression.

---

## Sources
- [FastAPI — portée des tâches en arrière-plan](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [LangGraph — persistance et reprise](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- [CrewAI — architecture de production](https://docs.crewai.com/v1.15.26/en/concepts/production-architecture)
- [MDN — événements SSE et reconnexion](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)

## Connexions
- [[141-system-design-llm|System design LLM]] — assembler les composants
- [[84-streaming-integration-applicative|Streaming]] — contrat public et reconnexions
- [[144-ux-ia-human-in-the-loop|UX & approbations]] — décisions liées aux propositions
- [[149-livraison-idempotence-concurrence|Livraison & idempotence]] — soumissions et effets métier
- [[40-011-langgraph-reprise-concurrence|LangGraph — Reprise]] — exploiter les états persistés
- [[40-012-crewai-execution-fiable|CrewAI — Production]] — placer les crews dans le service
- [[90-012-tests-agents-reprises|Agents — Tests de contrats, pannes & reprises]] — valider le cycle de vie
- [[00-moc-ai-engineering|MOC AI Engineering]]
