# Langfuse — Instrumentation en production — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Vérifié le : 9 octobre 2026 — API citées confrontées aux documentations officielles ; limites explicitées dans les cartes.
<!-- summary: traces applicatives complètes, observations, corrélation distribuée, async, tokens et coûts, streaming, sampling, masquage, export, doublons et diagnostic. -->


Pourquoi tracer seulement la gateway LLM ne suffit-il pas pour observer un agent ? <!--anki:6135383431373137353435663462366261663235326663333433313134666563-->
?
La gateway voit les **appels de modèles qui la traversent**. Elle ne décrit pas nécessairement le retrieval, les outils métier, les décisions d'approbation ou l'attente dans une file.

Créer une trace applicative qui relie ces étapes et lui rattacher les appels LLM. Sans cette structure, on peut connaître le coût de génération tout en ignorant pourquoi le dossier a échoué. La couverture réelle doit se vérifier sur une exécution avec outil, erreur et reprise.

---

Comment choisir le périmètre d'une trace Langfuse pour une conversation ? <!--anki:6236366136393265353463663439346539663939653932633433616439396530-->
?
Une trace représente une **unité de travail inspectable**, par exemple un tour de conversation ou un run d'agent. Une session regroupe les traces liées au parcours.

Un même dossier peut produire plusieurs traces lors de pauses humaines et de reprises, avec un identifiant métier commun. Éviter de maintenir artificiellement une observation ouverte plusieurs jours uniquement pour garder un arbre unique. Distinguer temps d'exécution actif, attente humaine et durée totale du dossier.

---

À ne pas confondre : thread_id, run_id et trace_id dans une application agentique ? <!--anki:3731393534663439613837393430656538383238656463663035353262613730-->
?
Le **thread** porte la continuité de l'état, le **run** identifie une exécution et la **trace** relie ses observations techniques. Leur correspondance dépend de l'architecture : un thread peut contenir plusieurs runs et traces.

Conserver des références explicites, en métadonnées, avec l'identité du dossier. Aucune de ces valeurs ne constitue une autorisation d'accès. Ne pas utiliser l'identifiant de trace comme clé d'idempotence d'une action : une reprise peut produire une nouvelle trace pour la même opération métier.

---

Comment structurer les observations Langfuse d'une boucle d'agent ? <!--anki:3031316337333931316263323431393238636463386531393366376266386632-->
?
Créer un parent pour l'exécution, puis distinguer **appels LLM, outils et étapes de recherche ou de validation**. Chaque invocation de modèle doit rester identifiable avec son usage et son résultat.

Ne pas envelopper toute la boucle dans une seule generation : cela masque l'appel qui a grossi le contexte ou demandé un outil incorrect. Utiliser des noms stables et des métadonnées pour les identifiants variables, afin de garder des filtres et des évaluations comparables.

---

Comment propager une trace entre une API et un worker ? <!--anki:3766396665323336396562643466333661366663303634383533313331373862-->
?
Injecter le **contexte de traçage** dans le message de la file, puis l'extraire dans le worker avec les mécanismes compatibles OpenTelemetry. Selon la durée et la causalité, créer un enfant ou une nouvelle trace reliée par un lien et les identifiants applicatifs.

Le transport de contexte ne doit contenir ni secret ni preuve d'autorisation. Le worker doit reconstruire ses droits depuis une source fiable. Tester la file réelle : une propagation qui marche entre fonctions peut disparaître à la frontière de processus.

---

Pourquoi des observations Langfuse deviennent-elles orphelines en async ou dans des threads ? <!--anki:6436326433633838323936373466656439663436636438613435326465346162-->
?
Le **contexte actif** peut ne pas être transmis à la tâche, au thread ou au processus exécutant le travail. Le span est alors créé sous un mauvais parent, ou dans une trace indépendante.

Vérifier où les tâches sont créées, combien de temps le parent reste actif et comment l'intégration propage le contexte. Ajouter un test qui lance deux requêtes intercalées et contrôle leurs relations parent-enfant. Copier globalement « le dernier trace_id » mélange les utilisateurs.

---

Quelles données faut-il fournir pour interpréter le coût d'une generation Langfuse ? <!--anki:6531383263633931653631643461383238646633373466653866643863333661-->
?
Le **modèle réellement appelé**, les unités d'usage disponibles et une tarification adaptée. Distinguer notamment entrées, sorties et tokens mis en cache lorsque le fournisseur les expose.

Une valeur absente ne doit pas devenir silencieusement un coût nul. Vérifier les alias de modèle, tarifs personnalisés et compteurs spécifiques du fournisseur. Réconcilier périodiquement les estimations avec la facturation, en conservant le périmètre : certains frais d'outils ou d'infrastructure sont hors coût LLM.

---

Comment mesurer correctement une génération streamée avec Langfuse ? <!--anki:3165313938623363666230653464303338313733333931653563306539333863-->
?
L'observation doit couvrir la **consommation réelle du flux**, pas seulement la création du générateur. Enregistrer premier contenu utile, fin ou annulation et usage final lorsqu'il est disponible.

Une réponse interrompue peut avoir consommé des tokens même si aucun total n'a été reçu. Marquer l'usage comme incomplet plutôt que zéro. La latence de génération et le délai perçu par l'utilisateur diffèrent si une file, un retrieval ou un proxy retarde l'affichage.

---

À ne pas confondre : sampling des traces et sampling de génération ? <!--anki:3166643861616465623234363466383438313161616663376139653963353934-->
?
Le **sampling des traces** choisit quelles exécutions sont conservées pour l'observabilité. Le **sampling de génération** choisit les tokens du modèle selon sa distribution.

Réduire le premier économise du stockage mais peut masquer des incidents ; modifier le second change les réponses. Documenter la probabilité de conservation et les filtres. Un tableau de coûts construit sur 10 % des traces ne représente pas le coût total sans estimation adaptée ou autre compteur exhaustif.

---

Calcul : parmi 100 000 runs quotidiens, chacun a indépendamment 5 % de chances d'être tracé. Quelle quantité moyenne de traces est attendue, et quelle probabilité de ne conserver aucune trace parmi 10 runs défaillants ? <!--anki:3235333764326665633935393435666461636235303330663738386431353339-->
?
On attend **100 000 × 0,05 = 5 000 traces**. Pour les dix échecs, la probabilité de n'en garder aucun est **0,95¹⁰ ≈ 59,9 %**.

La moyenne globale peut donc sembler suffisante tout en laissant un incident rare sans preuve. Envisager une collecte ciblée ou une conservation décidée après observation du résultat, en tenant compte des capacités de l'infrastructure et des biais introduits dans les tableaux de bord.

---

Où masquer les données sensibles avant envoi à Langfuse ? <!--anki:3838316261663163646131663461313762303236646566653364316136616164-->
?
Au plus près de la **source instrumentée**, avant export, en couvrant entrées, sorties, messages d'outils et métadonnées. Les fonctions de masquage du SDK peuvent aider, mais leur portée doit être testée sur les intégrations utilisées.

Une règle sur le prompt ne masque pas automatiquement une erreur réseau ou un document placé dans les métadonnées. Préférer une collecte minimale et des identifiants pseudonymes. Vérifier les payloads exportés avec des secrets synthétiques, plutôt que seulement leur affichage dans l'interface.

---

Pourquoi un script court peut-il perdre ses dernières traces Langfuse ? <!--anki:3361373339386663393233373434383262313231643965373965643534633235-->
?
Les observations peuvent être **mises en file puis exportées en arrière-plan**. Le processus peut finir avant cet export, surtout dans un script court ou un environnement interrompu rapidement.

Prévoir un flush ou un arrêt propre du client à la frontière de vie du processus, avec un délai borné. Un flush déclenche ou attend l'export selon le SDK ; il ne prouve pas à lui seul que toute donnée est devenue interrogeable. Tester erreurs réseau et arrêt brutal.

---

Comment éviter de compter deux fois les appels LLM dans Langfuse ? <!--anki:6238373733656630356433613433346261366232346637383366656338363239-->
?
Cartographier les **instrumentations actives** : callback du framework, SDK du fournisseur, wrapper manuel et gateway. Un même appel peut être observé à plusieurs frontières.

Choisir une observation de référence pour les tokens et le coût, ou relier explicitement les autres sans additionner deux usages identiques. Une trace parent résumant un coût ne doit pas être comptée en plus de tous ses enfants. Vérifier un exemple dont le nombre d'appels et les tokens sont connus.

---

Quel comportement prévoir si Langfuse devient indisponible ? <!--anki:3238313361373463646664343466626562646566636237633439353734316466-->
?
Distinguer **télémétrie de diagnostic** et journal métier exigé pour autoriser une action. Pour la première, borner files, retries et mémoire afin qu'une panne d'observabilité ne bloque pas toutes les requêtes.

Mesurer les pertes et signaler la période aveugle. Si un audit durable est nécessaire avant une action sensible, l'enregistrer dans le système métier avec une politique explicite. Le SDK d'observabilité n'est pas automatiquement cette garantie d'audit.

---

Comment vérifier la couverture d'instrumentation d'un agent ? <!--anki:3339383631663663623762373463656138326632386331663166616332643632-->
?
Construire une exécution de référence avec **retrieval, deux appels LLM, un outil, un échec et une reprise**. Comparer les observations attendues aux observations exportées, leurs parents et leurs identifiants.

Vérifier aussi coûts non doublés, résultat racine lisible et absence de secrets synthétiques. Une trace visible ne prouve pas qu'elle est complète. Répéter ce contrôle lors d'un changement d'intégration, particulièrement sur les chemins async et streaming.

---

## Mises en situation

Mise en situation : Langfuse montre tous les appels au modèle, mais aucun remboursement ni temps d'attente humaine. Comment complètes-tu l'instrumentation ? <!--anki:6163366532316136613164383464323439643835326132653139666237653865-->
?
1. Identifier les étapes hors gateway : outils, validation, file et approbation.
2. Ajouter leurs observations et un identifiant stable de dossier.
3. Relier les reprises au parcours sans garder un span ouvert pendant toute l'attente.
4. Comparer la trace au journal métier sur un dossier de test.

**Piège** : assimiler couverture des appels LLM et couverture de l'application.

---

Mise en situation : deux utilisateurs simultanés apparaissent dans le même arbre Langfuse après un passage par des threads. Comment corriges-tu ? <!--anki:3961393232326663653466383464623262376133316338316133663136326436-->
?
1. Vérifier le stockage du contexte de trace et supprimer les variables globales partagées.
2. Propager le contexte propre à chaque tâche au franchissement du thread.
3. Vérifier session, run et parent des observations dans un test concurrent.
4. Contrôler aussi le masquage et les accès aux traces concernées.

**Piège** : changer seulement le nom des observations alors que le parent est erroné.

---

Mise en situation : le coût affiché dans Langfuse a doublé après activation d'une intégration, sans hausse de trafic. Que vérifies-tu ? <!--anki:3630613334343835343764383431333962333334396537633262393766333334-->
?
1. Comparer nombre d'appels facturés et nombre de generations exportées.
2. Rechercher une double instrumentation SDK, framework ou gateway.
3. Vérifier tokens, noms de modèles, tarifs et agrégation parent-enfants.
4. Rejouer un scénario à usage connu avant de conclure à une hausse réelle.

**Piège** : diviser arbitrairement tous les coûts par deux au lieu de corriger leur provenance.

---

## Sources
- [Langfuse — bonnes pratiques de traces](https://langfuse.com/docs/observability/best-practices)
- [Langfuse — identifiants et tracing distribué](https://langfuse.com/docs/observability/features/trace-ids-and-distributed-tracing)
- [OpenTelemetry — propagation de contexte](https://opentelemetry.io/docs/concepts/context-propagation/)
- [Langfuse — masquage](https://langfuse.com/docs/observability/features/masking)
- [Langfuse — échantillonnage](https://langfuse.com/docs/observability/features/sampling)
- [Langfuse — fonctionnalités avancées du SDK](https://langfuse.com/docs/observability/sdk/advanced-features)

## Connexions
- [[91-langfuse-observabilite|Langfuse — Fondamentaux]] — instrumentation des traces
- [[93-monitoring-inference|Monitoring]] — relier traces et mesures agrégées
- [[84-streaming-integration-applicative|Streaming]] — observer la consommation du flux
- [[152-pii-confidentialite|Confidentialité]] — minimiser les données exportées
- [[90-011-langfuse-prompts-experiences|Langfuse — Prompts, datasets & expériences]] — provenance et couverture des observations
- [[00-moc-ai-engineering|MOC AI Engineering]]
