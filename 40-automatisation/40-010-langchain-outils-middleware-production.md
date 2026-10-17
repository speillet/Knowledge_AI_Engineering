# LangChain — Contrats, outils & middleware en production — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Vérifié le : 9 octobre 2026 — API citées confrontées aux documentations officielles ; limites explicitées dans les cartes.
<!-- summary: contrats métier, ToolRuntime, ToolMessage, sorties structurées, erreurs, async, middleware, budgets, isolation, tests et mises à niveau. -->


Pourquoi séparer un service métier de son outil LangChain ? <!--anki:3135346462363938313364363461623739393665643963303534346663363931-->
?
L'outil est un **adaptateur pour le modèle** ; le service porte les règles métier et les accès aux données. Le même service peut être appelé par une API, un agent ou un test sans dépendre d'un historique de messages.

Par exemple, `proposer_remboursement` produit une proposition, tandis qu'un service autorisé valide puis exécute le remboursement. Garder les permissions, plafonds et clés d'idempotence dans ce service évite qu'un changement de framework modifie les garanties métier.

---

Comment rendre un schéma d'outil LangChain utile au raisonnement du modèle ? <!--anki:6636343636313162646365323462336138326337663230343633653261373632-->
?
Donner des noms explicites, unités, bornes et descriptions qui indiquent **quand appeler l'outil**. Un champ `montant_centimes` est moins ambigu que `valeur`. Utiliser des enums pour les choix fermés et rejeter les champs inattendus si le contrat l'exige.

La validation de forme précède les contrôles métier : un montant entier positif peut encore dépasser le solde remboursable. Tester le schéma réellement transmis au fournisseur, car son sous-ensemble de JSON Schema peut différer du validateur local.

---

À ne pas confondre : ToolRuntime et arguments d'outil choisis par le modèle ? <!--anki:6236303864336633656361373438656262393064333731633930333662323362-->
?
Les **arguments publics** décrivent ce que le modèle peut demander. **`ToolRuntime`** injecte des informations contrôlées par l'application : contexte, état, store et identifiant d'appel, sans les exposer comme arguments à générer.

Un `tenant_id` authentifié doit venir du contexte, puis être vérifié dans le service métier. Cacher ce champ au modèle ne garantit pas l'isolation si la fonction SQL ou le stockage oublie ensuite le filtre de tenant.

---

Pourquoi conserver le lien entre AIMessage.tool_calls et ToolMessage dans LangChain ? <!--anki:3635316236366330613934663436313662633735653136663935396236323736-->
?
Chaque résultat d'outil doit référencer le **`tool_call_id`** de la demande correspondante. Ce lien permet au modèle de comprendre quelle observation répond à quel appel, notamment quand plusieurs outils sont demandés ensemble.

Lors d'une réduction de l'historique, préserver les échanges cohérents : supprimer la demande tout en gardant son résultat peut invalider la conversation pour certains fournisseurs. Un résultat d'outil est une donnée, pas une nouvelle instruction système.

---

À ne pas confondre : ProviderStrategy et ToolStrategy pour une sortie LangChain ? <!--anki:3930656239613133643064393462663761666439313965613233666134333561-->
?
**`ProviderStrategy`** utilise le mécanisme de sortie structurée du fournisseur ; **`ToolStrategy`** représente la réponse attendue par un appel d'outil structuré. Leur disponibilité dépend du modèle et de l'intégration.

Le même schéma Pydantic peut conduire à des chemins d'exécution différents. Vérifier refus, sortie absente, erreur de validation et coexistence avec les vrais outils. La conformité au schéma garantit une structure, pas la justesse d'une décision.

---

Comment gérer une sortie structurée LangChain correcte en forme mais fausse métier ? <!--anki:6230336635653838653961633437336339386363666462376231363935386431-->
?
Ajouter un **validateur métier indépendant** après l'extraction. Pour une proposition de remboursement, vérifier commande, devise, montant restant et pièces justificatives avant toute écriture.

Retourner une erreur exploitable pour une correction bornée, ou escalader si les données manquent. Une nouvelle génération ne résout pas un accès refusé ni une règle métier violée. Mesurer séparément erreurs de parsing, violations métier et réponses impossibles à établir.

---

Quelles erreurs d'outil un agent LangChain peut-il essayer de corriger ? <!--anki:6665393764383133353363663438323161363666666334346131356164376264-->
?
Distinguer **arguments réparables**, indisponibilité transitoire, refus d'autorisation et résultat métier négatif. Un identifiant mal formé peut être corrigé ; un timeout demande une politique de reprise ; un accès interdit doit rester interdit.

Renvoyer un code stable et une explication minimale, sans secrets ni stack trace. Ne pas transformer silencieusement une exception en « aucun résultat » : cela ferait prendre une panne pour une absence de données.

---

Pourquoi ainvoke ne garantit-il pas qu'un outil LangChain ne bloque pas le serveur ? <!--anki:6633376261353139306566373436346162316262393133646533313731663966-->
?
Une interface asynchrone ne rend pas tout son contenu non bloquant. Une bibliothèque synchrone peut bloquer la boucle d'événements ; un adaptateur peut la déporter dans un thread, sans pouvoir arrêter immédiatement le travail lancé.

Utiliser les clients async disponibles, borner les appels simultanés et configurer des timeouts au niveau réseau. Tester avec un outil lent et plusieurs requêtes concurrentes. L'annulation d'une coroutine ne prouve pas qu'une action distante a été annulée.

---

Comment tester l'ordre des middlewares d'un agent LangChain ? <!--anki:6365323332643231303138323430636361666563303035663064356363633135-->
?
Construire un cas où l'ordre change le résultat : une vérification d'autorisation, un cache et un retry autour du même outil. Enregistrer entrée, sortie et nombre d'invocations de chaque couche.

L'autorisation doit rester appliquée lors d'un cache hit et d'une reprise. Un retry peut répéter des middlewares internes ; vérifier leur idempotence et le budget total. Tester les chemins synchrones et asynchrones utilisés par l'application, plutôt que supposer que leurs hooks sont interchangeables.

---

Calcul : un appel d'outil LangChain peut être tenté 3 fois par le middleware ; chaque tentative autorise 2 tentatives HTTP au total. Quel maximum d'appels HTTP peut provoquer un seul appel d'outil ? <!--anki:3439383762663435636466343433386661653335343231643334613832393832-->
?
**3 × 2 = 6 tentatives HTTP**, si toutes les tentatives échouent de façon retriable. Les nombres incluent ici la tentative initiale de chaque couche.

Un budget global doit couvrir les tentatives réellement envoyées, pas seulement la demande d'outil produite par le modèle. Ajouter encore un retry au niveau du workflow peut multiplier ce plafond. Choisir la couche responsable des reprises et observer les tentatives au plus près de l'appel réseau.

---

Comment limiter les outils accessibles à un agent LangChain selon l'étape ? <!--anki:3533313634613135313432653438306438323666636533383732393732343336-->
?
Exposer le **sous-ensemble nécessaire** à l'étape courante : recherche pendant l'enquête, proposition pendant l'analyse, exécution après validation. Les mécanismes de sélection dynamique doivent conserver des schémas cohérents avec l'exécuteur.

Cette réduction aide le modèle à choisir et réduit le contexte. Elle complète les contrôles côté outil : une demande interdite issue d'un ancien message ou d'un appel direct doit aussi être refusée. Tester les changements de droits entre deux tours.

---

Comment router un agent LangChain vers un autre modèle sans casser ses contrats ? <!--anki:6363613966383433393865613430643138363164656632656630663663343139-->
?
Définir les capacités requises : appels d'outils, schéma structuré, contexte, contenu multimodal éventuel. Le modèle de secours doit respecter ces contrats ou produire un état d'échec explicite.

Tracer le modèle réellement utilisé et réévaluer qualité, latence et coûts. Une erreur d'arguments ne justifie pas forcément un modèle plus puissant. Éviter qu'un fallback relance une action métier déjà effectuée ou recommence une boucle sans conserver son budget.

---

Pourquoi séparer les données de test et les secrets dans les fixtures d'agents LangChain ? <!--anki:3037346437653234653636313433393738383731316431313332323366313539-->
?
Les fixtures doivent reproduire messages, résultats d'outils et états utiles avec des **données synthétiques ou minimisées**. Injecter les clients et identités de test, au lieu de lire automatiquement des identifiants de production.

Un test unitaire doit pouvoir tourner sans réseau et vérifier qu'un outil interdit n'a pas été exécuté. Réserver les vrais fournisseurs à des tests d'intégration explicitement configurés, dont on maîtrise le coût et la destination des données.

---

Comment préparer une mise à niveau de LangChain et de ses intégrations ? <!--anki:3330666137653734373735303436636438623166633238333661616138393439-->
?
Épingler un ensemble compatible de versions, puis tester la **frontière réellement utilisée** : schémas d'outils, messages, structured outputs, middleware et streaming. Les paquets du framework, du fournisseur et du runtime peuvent évoluer séparément.

Comparer quelques traces de référence et les critères métier avant promotion. Garder un rollback du code et des contrats de persistance. Une installation qui résout les dépendances n'est pas une preuve de compatibilité comportementale.

---

## Mises en situation

Mise en situation : un outil LangChain accepte un tenant_id généré par le modèle et peut consulter les commandes d'un autre client. Comment corriges-tu le contrat ? <!--anki:3666643161343134393335643431363339653638623438623365316438346162-->
?
1. Retirer le tenant des arguments publics et construire le contexte depuis l'identité authentifiée.
2. Appliquer l'autorisation et le filtre de tenant dans le service métier.
3. Vérifier les caches et mémoires partagés, qui doivent respecter la même frontière.
4. Tester une demande malveillante, un accès direct à l'outil et un changement de droits.

**Piège** : remplacer seulement la description de l'outil par « ne consulte pas les autres clients ».

---

Mise en situation : après ajout d'un middleware de retry, les requêtes LangChain coûtent quatre fois plus cher et certaines dépassent leur délai. Comment enquêtes-tu ? <!--anki:3737336165646364343964373463643738326637316233373065646237306637-->
?
1. Compter les appels réels par modèle, outil, intégration et tentative HTTP.
2. Identifier les couches qui recommencent la même opération.
3. Choisir les erreurs retriables et une responsabilité de reprise claire.
4. Faire respecter un budget et une deadline communs, puis tester une panne prolongée.

**Piège** : limiter uniquement le nombre de tours de l'agent, alors que les tentatives internes restent invisibles.

---

Mise en situation : un fallback LangChain renvoie du texte libre là où l'application attend une proposition Pydantic. Comment évites-tu une action métier incorrecte ? <!--anki:6531336565343837666633373463343161653836626366353933663738343434-->
?
1. Vérifier la compatibilité du modèle de secours avec les outils et la sortie structurée.
2. Refuser l'exécution tant que structure et règles métier ne sont pas validées.
3. Retourner un état explicite d'échec ou de demande d'aide.
4. Ajouter ce cas au test d'intégration et tracer la stratégie réellement utilisée.

**Piège** : extraire un montant du texte avec une expression régulière puis exécuter automatiquement.

---

## Sources
- [LangChain — outils et ToolRuntime](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain — sorties structurées](https://docs.langchain.com/oss/python/langchain/structured-output)
- [LangChain — middleware personnalisé](https://docs.langchain.com/oss/python/langchain/middleware/custom)
- [LangChain — tests](https://docs.langchain.com/oss/python/langchain/test)

## Connexions
- [[42-langchain-fondamentaux|LangChain — Fondamentaux]] — contrats des composants
- [[43-langchain-agents|LangChain — Agents]] — composition des middlewares
- [[32-tool-calling|Tool calling]] — valider demandes et résultats
- [[103-defenses-agents|Défenses des agents]] — permissions appliquées par le service
- [[90-013-tests-agents-reprises|Agents — Tests de contrats, pannes & reprises]] — tester outils et contrats
- [[00-moc-ai-engineering|MOC AI Engineering]]
