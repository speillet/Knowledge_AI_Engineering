# Transactions, outbox & sagas pour les agents — Flashcards
Tags: #flashcards #ai-engineering #system-design #distribue #transactions
<!-- summary: invariants métier, double écriture, outbox et inbox, périmètre transactionnel, sagas et compensation, isolation des workflows, états inconnus, checkpoints, validation humaine et tests de panne. -->


Pourquoi commencer un workflow d'agent par ses invariants métier ? <!--anki:6130323438373235613561633435303762363666336239313661613163346336-->
?
Les **invariants** décrivent ce qui doit rester vrai malgré erreurs et concurrence : une commande ne doit pas être débitée deux fois, un stock ne doit pas devenir négatif, une action sensible doit correspondre aux paramètres approuvés.

Ils guident le stockage, les transitions et les contrôles. Un prompt demandant de « faire attention » n'impose aucune contrainte aux écritures. Pour chaque invariant, identifier où il est vérifié, quelles opérations concurrentes peuvent le menacer et ce qui se passe si le processus plante à cet endroit.

---

Quel problème pose une double écriture entre base métier et broker ? <!--anki:3335356335363537623034643434623138366330643232363266666135376536-->
?
Si l'on **valide en base puis publie un événement**, un crash entre les deux laisse un changement sans notification. Si l'on publie d'abord, l'événement peut annoncer une modification finalement annulée en base.

Changer l'ordre déplace le problème sans le résoudre. Il faut une coordination transactionnelle adaptée ou enregistrer durablement l'intention de publication avec la mutation métier. Les retries peuvent réparer certains échecs, mais exigent de savoir ce qui reste à publier et de supporter les doublons. Un bloc `try/except` ne couvre pas un arrêt brutal du processus.

---

Comment le pattern transactional outbox résout-il la double écriture ? <!--anki:3738363031656632333061323438653162666433346538613039663263616231-->
?
Écrire **la mutation métier et l'événement à publier dans la même transaction locale**. Un relais lit ensuite les entrées validées de l'outbox et les transmet au broker, avec reprise sur erreur.

Si la transaction échoue, ni mutation ni événement ne sont validés. Si le relais s'arrête, l'événement reste récupérable. Cela couple l'intention de publication à l'état métier, sans rendre l'envoi distant atomique. Surveiller l'âge des événements non publiés et prévoir leur rétention ainsi qu'une politique de nettoyage sûre.

---

Pourquoi le relais d'une outbox peut-il publier deux fois le même événement ? <!--anki:3635346334356362356136373464663161633463323539336438313261396566-->
?
Il peut **publier avec succès puis planter avant d'enregistrer ce succès**. À la reprise, l'entrée paraît encore à envoyer. La marquer comme envoyée avant publication créerait au contraire une fenêtre de perte.

Garder un identifiant stable d'événement et rendre les consommateurs tolérants à la relivraison. Pour un ordre par entité, porter aussi une séquence et organiser les relais en conséquence. L'outbox ne garantit ni ordre global ni effet unique chez chaque destinataire par sa seule présence.

---

Comment une inbox transactionnelle protège-t-elle un consommateur ? <!--anki:3430383365313537643539643430323939376562363230306266356365326535-->
?
Le consommateur stocke **l'identifiant de l'événement traité et sa mutation locale dans la même transaction**. Une contrainte unique empêche une relivraison de répéter cette mutation. Après commit, il peut acquitter le message ; une panne avant ack devient un rejeu reconnaissable.

Le périmètre est important : un e-mail ou un paiement exécuté en dehors de cette transaction n'est pas protégé par la seule inbox. Pour ces effets, utiliser une intention durable et une destination idempotente, ou une procédure de réconciliation lorsque le résultat reste inconnu.

---

À ne pas confondre : transaction distribuée et saga ? <!--anki:3466646234613861393631613461663261396532626634643835326633633262-->
?
Une **transaction distribuée** coordonne des participants capables de prendre part à un protocole commun de validation, par exemple en deux phases. Une **saga** enchaîne des transactions locales et prévoit des actions métier pour compenser les étapes déjà effectuées en cas d'échec.

Une saga rend visibles des états intermédiaires et ne fournit pas automatiquement l'isolation d'une transaction globale. Elle convient à des opérations longues avec compensations acceptables. Un fournisseur externe arbitraire ne peut pas être intégré à une transaction globale simplement en l'appelant depuis un bloc transactionnel local.

---

À ne pas confondre : rollback technique et compensation métier ? <!--anki:3837656434633238643236653433316162336534356533616634623533376262-->
?
Un **rollback** annule une transaction non validée dans son périmètre. Une **compensation** est une nouvelle opération qui corrige les conséquences d'une action déjà validée : remboursement, libération d'une réservation, message rectificatif.

Elle ne restaure pas toujours exactement le passé : un e-mail envoyé a pu être lu, un remboursement peut entraîner des frais. Elle peut aussi échouer et doit être suivie. Définir ces limites avec le métier avant d'automatiser le workflow ; une instruction « undo » ne rend pas une action réversible.

---

Comment concevoir une compensation qui peut elle-même être rejouée ? <!--anki:3331396262346265623232323436363539633138626639386561336330633333-->
?
Lui donner **sa propre identité stable**, liée à l'action originale, et enregistrer son état. Vérifier la situation actuelle avant de corriger : un remboursement total déjà effectué ne doit pas être répété, et une réservation expirée n'exige pas forcément la même action qu'une réservation active.

Prévoir résultats inconnus, retries bornés et intervention opérationnelle. L'ordre de compensation dépend des dépendances métier, pas toujours de l'ordre inverse mécanique. Conserver les références externes nécessaires pour vérifier le résultat, même après une reprise de l'orchestrateur.

---

Pourquoi une saga doit-elle gérer les interactions avec d'autres workflows ? <!--anki:3331663431383966636536333430336538353934333936616530343433336638-->
?
Ses étapes valident des états visibles **avant la fin de l'ensemble**. Un autre workflow peut donc prendre une décision sur une réservation provisoire ou un paiement en attente.

Utiliser des états métier explicites, réservations, contraintes et contrôles de version pour protéger les invariants. Par exemple, distinguer stock disponible, réservé et vendu plutôt que laisser chaque étape déduire sa propre disponibilité. Une compensation tardive ne doit pas écraser une modification légitime réalisée entre-temps. Tester ces interactions autant que l'échec d'une étape isolée.

---

Quels états conserver pour une action externe dont la réponse peut être perdue ? <!--anki:3630666665336530626530633466313961653133376664316562333136306631-->
?
Distinguer au moins **intention enregistrée, action en cours, réussite confirmée, échec confirmé et résultat inconnu**. Ce dernier état évite de convertir un timeout en certitude d'échec.

Conserver clé d'opération, paramètres autorisés, références du fournisseur et historique des tentatives. Les transitions doivent être contrôlées : un retour tardif ne doit pas écraser un état déjà réconcilié sans vérification. Exposer un statut récupérable permet au client et à l'opérateur de suivre l'action même après une déconnexion ou le redémarrage d'un agent.

---

Pourquoi un checkpoint d'agent ne suffit-il pas à sécuriser les effets externes ? <!--anki:3333323166376239613861633432613862333037376561316162666230633934-->
?
Le checkpoint décrit **l'état sauvegardé du workflow**, mais n'est pas nécessairement atomique avec l'action réalisée par un outil distant. Si l'action réussit puis que la sauvegarde échoue, la reprise peut revenir juste avant cette action.

Enregistrer son identité avant l'appel et réutiliser cette identité à la reprise. Consulter ou réconcilier son résultat au lieu de générer une nouvelle intention. La persistance du framework rend le calcul reprenable ; l'unicité des effets exige des garanties supplémentaires dans les outils et leurs destinations.

---

Comment empêcher qu'une approbation humaine valide des paramètres ensuite modifiés ? <!--anki:3635396366633138316430363438613962306666303362323137373862646338-->
?
Lier l'approbation à une **version ou empreinte de la demande exacte** : bénéficiaire, montant, ressource et conditions pertinentes. Au moment d'exécuter, vérifier que les paramètres correspondent toujours et que l'autorisation reste applicable.

Si l'agent modifie la proposition après approbation, il faut une nouvelle validation selon la politique. Éviter une permission vague attachée seulement à la conversation. Le contrôle doit être effectué au point d'exécution avec une identité fiable, car le modèle peut reformuler ou reconstruire les arguments entre deux tours.

---

Comment tester les garanties d'un workflow distribué au-delà du chemin heureux ? <!--anki:3632653736656631316438653439633738323635343439386630376137396362-->
?
Injecter des pannes **aux frontières entre effet, persistance et acquittement**. Rejouer le même événement, perdre une réponse, arrêter un worker après un commit, désordonner les messages et exécuter deux tentatives simultanées.

Vérifier les invariants métier et la capacité à retrouver un état terminal ou un état inconnu explicite. Un test qui contrôle seulement la réponse HTTP manque les doubles effets. Utiliser des simulateurs pour couvrir les scénarios, puis vérifier les garanties réelles des intégrations : un mock parfait peut masquer les limites du fournisseur.

---

## Mises en situation

Mise en situation : un agent a débité un client, puis le serveur s'est arrêté avant son checkpoint. Comment reprends-tu sans débiter à nouveau ? <!--anki:3964366538356535333233633464376439643866666266383932363933616635-->
?
1. **Retrouver l'intention persistée** et sa clé d'idempotence initiale.
2. **Interroger le fournisseur** pour obtenir le statut ou rejouer la même clé dans le cadre de sa garantie.
3. **Enregistrer le résultat confirmé** puis reprendre le workflow à partir de cet état.
4. **Conserver l'incertitude** et déclencher une réconciliation si le fournisseur ne permet pas de conclure.
5. **Tester cette fenêtre de panne** et vérifier l'unicité du débit dans le registre externe.

**Piège** : se fier au seul checkpoint qui indique encore « paiement à faire ».

---

Mise en situation : la création d'une commande réussit, mais son événement de traitement n'arrive parfois jamais dans la file. Comment corriges-tu l'architecture ? <!--anki:3135376531326265343464643465353761393966323438333730396331656366-->
?
1. **Identifier la double écriture** et la fenêtre entre commit en base et publication.
2. **Enregistrer commande et événement** dans une transaction avec outbox.
3. **Ajouter un relais reprenable**, conservant identité et politique d'ordre par commande.
4. **Dédupliquer chez le consommateur**, car le relais peut publier plusieurs fois.
5. **Surveiller et réconcilier** les événements en retard, puis tester les crashes avant et après publication.

**Piège** : ajouter des retries en mémoire alors que l'intention d'envoyer disparaît avec le processus.

---

Mise en situation : une réservation de stock réussit, le paiement échoue et la libération du stock tombe elle aussi en panne. Quel état doit exposer le système ? <!--anki:3436323335393733623033393463653638316363373766633465393737653534-->
?
1. **Conserver l'échec du paiement** et l'état distinct de compensation à terminer.
2. **Enregistrer durablement la libération**, avec une identité permettant son rejeu.
3. **Vérifier l'état de la réservation** avant chaque reprise afin de gérer expiration ou compensation déjà effectuée.
4. **Alerter après le délai prévu** et fournir à l'opérateur les références nécessaires.
5. **Clôturer seulement après confirmation** ou résolution métier documentée.

**Piège** : annoncer « tout annulé » alors qu'une ressource reste bloquée.

---

## Sources
- [AWS — transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [AWS — orchestration de sagas](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-orchestration.html)
- [Stripe — contrat des requêtes idempotentes](https://docs.stripe.com/api/idempotent_requests)
- [PostgreSQL — isolation et transactions concurrentes](https://www.postgresql.org/docs/current/transaction-iso.html)

## Connexions
- [[149-livraison-idempotence-concurrence|Livraison, idempotence & concurrence]] — garanties des briques du workflow
- [[45-langgraph-production|LangGraph en production]] — distinguer checkpoint et effet métier
- [[115-plateformes-agents-gouvernance|Gouvernance des agents]] — permissions, approbations et compensation
- [[144-ux-ia-human-in-the-loop|UX & validation humaine]] — approuver une demande exacte et suivre son résultat
- [[00-moc-ai-engineering|MOC AI Engineering]]
