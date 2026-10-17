# LangGraph — Reprise, concurrence & évolution — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Vérifié le : 9 octobre 2026 — API citées confrontées aux documentations officielles ; limites explicitées dans les cartes.
<!-- summary: durabilité sync/async/exit, pending writes, effets externes, interruptions, concurrence par thread, reducers, sous-graphes, migrations et diagnostics de reprise. -->


À ne pas confondre : checkpoint LangGraph et transaction métier ? <!--anki:3363396132633461616334643439346639636339643337353264376462643830-->
?
Un **checkpoint** enregistre l'avancement du graphe. Une **transaction métier** rend atomiques les modifications prises en charge par son système de stockage. Les deux ne sont généralement pas validés ensemble.

Si un remboursement réussit puis que le processus meurt avant le checkpoint, le nœud peut le redemander. Utiliser une identité stable d'opération et une déduplication côté service, ou réconcilier son état. Mettre l'action dans une tâche facilite la reprise sans supprimer cette fenêtre de panne.

---

Comment choisir entre les modes de durabilité sync, async et exit de LangGraph ? <!--anki:3564343365396664613530663464383961353535313134326463393261386638-->
?
**`sync`** attend l'écriture du checkpoint avant de poursuivre ; **`async`** chevauche persistance et étape suivante ; **`exit`** persiste à la sortie du graphe, y compris erreur ou interruption prévue.

Le compromis porte sur le coût de persistance et le travail récupérable après crash. `exit` ne protège pas les étapes intermédiaires contre la mort brutale du processus. Aucun mode ne rend transactionnel un service externe. Tester les modes avec le backend et les pannes envisagés.

---

Que deviennent les branches LangGraph réussies si une autre branche du même super-step échoue ? <!--anki:3532373334353035303231373439306662333336386630643264373162386336-->
?
Avec la persistance appropriée, les **pending writes** conservent les résultats des nœuds terminés du super-step. À la reprise, ces nœuds n'ont pas nécessairement à être relancés : le travail restant peut reprendre.

Il faut distinguer un résultat enregistré d'un effet externe dont l'enregistrement n'a pas abouti. Injecter une panne dans une branche et compter les invocations après reprise. Ne pas déduire de ce mécanisme une garantie universelle d'exécution unique.

---

Pourquoi un nœud LangGraph contenant interrupt doit-il pouvoir recommencer ? <!--anki:3331333363616538363435613435666638373731366163643836643062346461-->
?
La reprise réexécute le nœud depuis son début, puis restitue la réponse humaine à l'appel d'**`interrupt`** correspondant. Les lectures, calculs et effets précédents peuvent donc être rejoués.

Conserver une proposition stable avant l'interruption ; placer l'exécution métier dans une étape ultérieure idempotente. Éviter d'englober l'interruption dans un bloc qui capture toute exception : son signal doit remonter au runtime. Tester le même scénario dans un nouveau processus.

---

Pourquoi ne pas réordonner des interrupt dans un nœud LangGraph déjà suspendu ? <!--anki:6633383838643766396165333437333438346533623933303738663035373638-->
?
Les valeurs de reprise sont associées aux interruptions selon leur ordre d'exécution dans le nœud. Ajouter, retirer ou permuter une interruption peut faire correspondre une réponse à la mauvaise question.

Conserver le chemin de code compatible pour les exécutions en attente, ou terminer/migrer explicitement celles-ci avant de déployer. Utiliser des étapes distinctes et des propositions versionnées facilite le suivi. Le déploiement d'un nouveau code ne supprime pas les anciens états persistés.

---

Comment traiter plusieurs interruptions LangGraph en attente simultanément ? <!--anki:6232346431373435633539363430616561646461396335613536316265343961-->
?
Identifier **chaque interruption** et rattacher la réponse à la bonne demande ; les API récentes acceptent une correspondance entre identifiants d'interruption et valeurs de reprise. Ne pas assimiler un « oui » global à l'approbation de toutes les branches.

L'application vérifie propriétaire, droits, version et expiration de chaque proposition. Une branche approuvée peut avancer tandis qu'une autre attend, selon le graphe. Tester approbations désordonnées, doublons et refus partiel sur la version du runtime retenue.

---

Comment reprendre un graphe LangGraph après une erreur sans lui soumettre une nouvelle requête ? <!--anki:3438303766373064653663643461376439636139633061383439333337306439-->
?
Recharger le même **`thread_id`**, inspecter son état puis reprendre le travail en attente. Pour une reprise d'erreur, l'invocation avec `None` peut continuer l'exécution ; une interruption humaine utilise `Command(resume=...)`.

```python
config = {"configurable": {"thread_id": dossier_id}}
snapshot = graph.get_state(config)
# Après diagnostic d'un échec, et avec le même stockage :
resultat = graph.invoke(None, config=config)
```

Ne pas reconstruire les entrées initiales et les injecter aveuglément : cela peut démarrer un nouveau tour ou accumuler de nouveau les messages. Distinguer erreur, interruption et exécution terminée.

---

Pourquoi un checkpointer LangGraph ne suffit-il pas à sérialiser deux requêtes sur le même thread ? <!--anki:6330643362343966643762663437366439396439333132306663303537343731-->
?
Il conserve des checkpoints, mais la politique d'admission des **exécutions concurrentes** relève aussi du runtime et de l'application. Deux requêtes peuvent lire un état ancien et produire des décisions incompatibles.

Choisir une règle explicite : rejeter, mettre en file ou remplacer la demande précédente avec les garanties prévues. En hébergement maison, assurer cette coordination entre réplicas ; un verrou Python ne protège qu'un processus. Les reducers du graphe ne règlent pas à eux seuls cette concurrence entre invocations.

---

Comment concevoir un reducer LangGraph pour une collecte parallèle fiable ? <!--anki:3964373335323535616462663431326438616439383165323363383139346430-->
?
Définir la **sémantique de fusion** avant la fonction : concaténation, ensemble, mise à jour par identifiant ou conflit explicite. Si l'ordre ne doit pas compter, rechercher une opération associative et commutative ; si les doublons sont possibles, prévoir une identité stable.

Deux résultats portant le même identifiant mais des contenus contradictoires ne doivent pas être écrasés silencieusement. Stocker les éléments par identifiant puis trier pour l'affichage est souvent plus robuste qu'une liste dont l'ordre dépend de l'arrivée des branches.

---

Pourquoi éviter les mutations en place dans un nœud LangGraph ? <!--anki:6233323231326532636662313435353939653730633361613239636238356233-->
?
Renvoyer une **mise à jour explicite** facilite le raisonnement sur les reducers et les snapshots. Modifier une liste de l'état puis la renvoyer avec un reducer de concaténation peut réintroduire des éléments déjà présents.

```python
# Une nouvelle contribution, pas toute la liste accumulée :
def noter(state):
    return {"notes": ["contrôle terminé"]}
```

La bonne forme dépend du reducer. Tester deux contributions successives et deux branches parallèles ; vérifier les éléments, leur identité et leur ordre utile, pas seulement la longueur finale.

---

Comment choisir la mémoire d'un sous-graphe LangGraph ? <!--anki:3835393364376666643936353436373439656339376532613439323832633066-->
?
Décider si l'agent délégué doit **repartir à chaque appel** ou conserver son propre historique. La configuration du checkpointer du sous-graphe et l'héritage du parent déterminent cette portée.

Un sous-agent de synthèse ponctuelle ne doit pas récupérer arbitrairement un dossier précédent. Un assistant spécialisé persistant demande des identifiants et namespaces stables. Tester appels répétés et parallèles : partager une mémoire peut créer des conflits ou des fuites si le périmètre n'est pas explicite.

---

Comment faire évoluer le schéma d'état d'un graphe LangGraph en production ? <!--anki:3539643263336230323163643437343462623664643464643430396565643030-->
?
Les checkpoints historiques restent lisibles par du **nouveau code** : prévoir valeurs par défaut, champs optionnels ou migrations explicites. Une annotation TypedDict ne convertit pas automatiquement les états déjà stockés.

Ajouter une version applicative au contrat, conserver des fixtures anciennes et tester leur reprise. Retirer un champ ou renommer un nœud encore attendu par un thread interrompu demande une stratégie de compatibilité. Prévoir aussi le chemin de rollback : l'ancien code peut ignorer ou mal interpréter le nouvel état.

---

Comment borner les reprises d'un nœud LangGraph ? <!--anki:3334376465383130656164323437633339386338383332396566636534666534-->
?
Configurer une **`RetryPolicy`** pour les erreurs transitoires ciblées, en plus des délais réseau et du budget global. Ne pas recommencer systématiquement une erreur de validation ou de permission.

```python
from langgraph.types import RetryPolicy
builder.add_node(
    "lire_source", lire_source,
    retry_policy=RetryPolicy(max_attempts=3, retry_on=ConnectionError),
)
```

Les trois tentatives incluent l'initiale. Vérifier les retries internes du client et l'idempotence avant de traiter une erreur d'écriture comme une simple indisponibilité.

---

Pourquoi la limite de récursion LangGraph ne remplace-t-elle pas un budget d'agent ? <!--anki:6665643733613362383263383463376362303637613430663830326535626436-->
?
Elle borne les **super-steps**, alors qu'une seule étape peut lancer beaucoup d'appels parallèles, traiter un long contexte ou attendre longtemps. Elle ne représente donc ni un montant ni un délai.

Cumuler plafond de branches actives, deadline et compteurs d'appels/tokens. Avant une délégation, réserver un budget partagé plutôt que donner à chaque branche le budget total. À l'épuisement, produire un résultat partiel explicite et conserver les éléments nécessaires au diagnostic.

---

Calcul : un graphe lance 24 branches indépendantes de 2 s chacune, avec au plus 6 branches actives. Sans overhead ni retry, quelle durée minimale pour terminer toutes les branches ? <!--anki:3165343066383066613030663461646439333838653135376465613664396335-->
?
**⌈24 / 6⌉ × 2 = 8 secondes**, soit quatre vagues. Sans limite de concurrence et avec une capacité illimitée, elles prendraient 2 secondes.

Le plafond protège quotas et ressources mais augmente l'attente. En pratique, des durées inégales, des retries et des limites de débit peuvent allonger le temps total. Mesurer les appels actifs et les tâches en attente séparément ; réduire le parallélisme ne réduit pas automatiquement le nombre de tokens consommés.

---

Comment empêcher qu'un time travel LangGraph rejoue des effets réels pendant le débogage ? <!--anki:6438313533383466623730363434646561333965393238623330653632316534-->
?
Rejouer dans un environnement où les **outils d'écriture sont simulés** ou strictement autorisés pour le test. Copier seulement les données nécessaires et conserver un lien vers le cas d'origine.

Un checkpoint décrit un état passé du graphe ; il ne restaure pas le solde d'un compte ou l'état d'un service tiers. Même si les clés d'idempotence protègent certaines actions, un nouveau chemin pourrait en générer d'autres. Séparer diagnostic et reprise opérationnelle autorisée.

---

## Mises en situation

Mise en situation : ton nœud LangGraph crée un avoir, puis plante avant l'enregistrement du checkpoint. Après reprise, deux avoirs existent. Que changes-tu ? <!--anki:3364353231383037663938313437336138383133303632303266383631343462-->
?
1. Identifier la fenêtre entre validation métier et persistance du graphe.
2. Générer l'identité de l'opération avant l'effet et la conserver lors des reprises.
3. Faire dédupliquer l'action atomiquement par le service des avoirs.
4. Tester un crash précisément après la validation métier, puis reprendre depuis le stockage.
5. Réconcilier les doublons déjà produits selon les règles métier.

**Piège** : croire que passer de `async` à `sync` rend l'API des avoirs transactionnelle avec le checkpoint.

---

Mise en situation : deux messages arrivent en même temps dans le même thread LangGraph et chacun modifie le panier. Comment évites-tu une réponse fondée sur un état périmé ? <!--anki:6666613261643133616462623462656661653934643566643234363234303239-->
?
1. Définir si la seconde requête attend, est rejetée ou remplace la première.
2. Appliquer la coordination sur tous les workers, avec une version de l'état métier.
3. Vérifier cette version avant l'écriture effective du panier.
4. Tester deux invocations concurrentes et l'expiration du mécanisme de coordination.

**Piège** : ajouter un reducer de liste alors que le conflit concerne deux exécutions indépendantes.

---

Mise en situation : un déploiement renomme le nœud LangGraph d'approbation alors que 400 dossiers attendent une réponse humaine. Comment prépares-tu la migration ? <!--anki:3566393761616536343764313462643862316339646634383735323031656233-->
?
1. Inventorier les états et versions en attente avant le changement.
2. Conserver le chemin ancien ou définir une migration contrôlée vers le nouveau.
3. Tester des checkpoints historiques avec approbation, refus et expiration.
4. Prévoir un rollback compatible et surveiller les reprises après déploiement.

**Piège** : valider uniquement les nouveaux dossiers créés après la mise à jour.

---

## Sources
- [LangGraph — checkpointers, pending writes et durabilité](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- [LangGraph — interruptions et règles de reprise](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangGraph — graphes et migrations](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph — politiques de retry](https://docs.langchain.com/oss/python/langgraph/use-graph-api)

## Connexions
- [[44-langgraph-fondamentaux|LangGraph — Fondamentaux]] — reducers et super-steps
- [[45-langgraph-production|LangGraph — Production]] — persistance et interruptions
- [[149-livraison-idempotence-concurrence|Livraison & idempotence]] — effets externes et exécutions concurrentes
- [[140-010-transactions-outbox-sagas|Transactions & sagas]] — frontières transactionnelles
- [[140-011-architecture-applications-agentiques|Applications agentiques — Architecture & cycle de vie]] — exploiter les états persistés
- [[90-013-tests-agents-reprises|Agents — Tests de contrats, pannes & reprises]] — injecter des pannes
- [[00-moc-ai-engineering|MOC AI Engineering]]
