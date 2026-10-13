# RAG en production : droits, versions & abstention — Flashcards
Tags: #flashcards #ai-engineering #rag #securite #donnees #retrieval
Vérifié le : 13 octobre 2026
<!-- summary: identité et permissions, filtrage avant exposition, rappel sous filtres, validité temporelle, priorité des sources, suppressions et caches, citations versionnées, abstention et tests de régression. -->


Pourquoi la pertinence d'un passage RAG ne suffit-elle pas à l'utiliser comme preuve ? <!--anki:3961663861303264376631323462373538363333643236643561653032313563-->
?
Un passage doit être **pertinent, autorisé et applicable** à la question. Une forte similarité ne prouve ni le droit de le lire, ni sa validité à la date demandée, ni son autorité sur le sujet.

Exemple fictif : une ancienne politique de remboursement peut reprendre exactement les mots de la question tout en décrivant un délai remplacé. Vérifier ces conditions avant d'exposer le passage au modèle, puis contrôler le soutien de chaque affirmation dans la réponse.

---

D'où doivent venir le tenant et les permissions d'une requête RAG ? <!--anki:3361633361656338643265623466663462396334613936633231333336376166-->
?
Du **contexte d'identité authentifié**, vérifié par l'application et son système d'autorisation. Les arguments produits par un modèle ou un champ libre de la requête ne sont pas une preuve d'appartenance à un tenant.

Le service déduit le périmètre accessible et l'applique aux recherches, aux chargements de documents et aux citations. Une requête qui nomme une autre entreprise reste dans le périmètre autorisé. Les droits doivent aussi être revérifiés lorsqu'une conversation reprend après un changement de permissions.

---

Pourquoi activer la sécurité par ligne de PostgreSQL ne suffit-il pas à isoler un RAG ? <!--anki:3538636266303636643666323433643238386436373061653731613032333365-->
?
Les **superutilisateurs et rôles `BYPASSRLS`** contournent cette sécurité ; le propriétaire de la table la contourne normalement aussi, sauf configuration appropriée comme `FORCE ROW LEVEL SECURITY`.

Tester les requêtes avec le **rôle réellement utilisé par le service**, ses permissions et ses politiques, plutôt qu'avec un compte administratif. La sécurité par ligne protège les accès couverts par ces politiques ; elle ne contrôle pas automatiquement les copies déjà présentes dans un cache externe ou le contexte du modèle.

---

À ne pas confondre : filtrer les candidats RAG et masquer une réponse après génération ? <!--anki:6666646239353432613336333461663662353834383931333463643065646433-->
?
**Filtrer les candidats** empêche les contenus interdits d'atteindre le modèle, les rerankers externes et les caches exposés à l'utilisateur. **Masquer la réponse** intervient après que ces composants ont déjà pu recevoir ou réutiliser l'information.

Une recherche interne peut examiner des candidats puis les filtrer dans une frontière de confiance contrôlée. Le critère de sécurité porte sur l'absence d'exposition non autorisée ; il n'impose pas un ordre physique universel à tous les moteurs de recherche.

---

Pourquoi un top-k global suivi d'un filtre peut-il dégrader le rappel RAG ? <!--anki:3839393638336435303865393435336362646463303064646638373733356163-->
?
Des documents interdits peuvent **occuper les k premières places**. Les retirer laisse peu de résultats alors que des preuves autorisées existent plus loin.

Chercher dans le sous-ensemble admissible, augmenter le budget de candidats ou utiliser une recherche itérative selon le moteur. Dans pgvector avec index approximatif, le filtre est appliqué après le parcours de l'index : mesurer le rappel sous les filtres réels. Élargir la recherche ne doit jamais élargir les permissions.

---

Calcul : un classement RAG place quatre documents interdits avant deux preuves autorisées. On prend trois candidats puis filtre, ou on filtre tout le corpus puis prend trois résultats. Chaque preuve autorisée est pertinente. Combien de preuves et quel rappel obtient-on ? <!--anki:3634616431666432663664303465333738363638383530623566613663656634-->
?
**Top-3 puis filtre : zéro preuve**, donc `recall = 0/2 = 0 %`. **Filtre puis top-3 : deux preuves**, donc `recall = 2/2 = 100 %` ; seuls deux documents admissibles existent.

Le calcul suppose un classement exact et un corpus entièrement parcouru. Un index approximatif peut encore manquer des preuves après application des restrictions. Il faut mesurer son rappel et son coût, plutôt que déduire une garantie de la présence d'un filtre.

---

Comment représenter la validité temporelle d'une version de document RAG ? <!--anki:3039303833663566313231323439626439313039383736613930333430613461-->
?
Conserver un **intervalle métier**, par exemple `[valid_from, valid_until)`, distinct de la date d'ingestion. Une version est applicable si `valid_from <= date_question < valid_until` ; une borne de fin absente signifie qu'aucune fin n'est enregistrée.

Ce choix rend explicite le passage entre deux versions contiguës. Pour une question historique, appliquer la date demandée ; pour une question actuelle, utiliser une date de référence contrôlée. Les permissions restent celles de l'utilisateur au moment de l'accès, même si la question porte sur le passé.

---

À ne pas confondre : date d'ingestion et date d'effet d'un document RAG ? <!--anki:3434303262623835663439663465333961623766303764336165653838306362-->
?
La **date d'ingestion** indique quand le pipeline a reçu le document. La **date d'effet** indique quand son contenu s'applique au métier.

Une politique publiée aujourd'hui peut entrer en vigueur le mois prochain. Un document reçu tardivement peut décrire une règle déjà applicable. Choisir automatiquement le dernier fichier ingéré confond ces deux temporalités. Pour rejouer ce que le service savait à une date passée, conserver aussi la disponibilité du document dans les snapshots : la validité métier seule ne suffit pas.

---

Comment résoudre deux sources RAG contradictoires sans choisir arbitrairement la plus récente ? <!--anki:3964633038636337343033343435373539303231356461316336336535356135-->
?
Vérifier d'abord **périmètre, droits et date d'effet**, puis appliquer une règle métier documentée sur l'autorité des sources : par exemple, contrat applicable avant FAQ informative.

La priorité dépend du sujet ; un score de similarité n'est pas une autorité. Si deux sources de même autorité restent incompatibles, ne pas fusionner leurs valeurs : signaler l'incertitude permise ou demander une clarification. Conserver les références pour le diagnostic, sans exposer des sources interdites à l'utilisateur.

---

Que doit identifier une citation RAG pour rester vérifiable après une mise à jour ? <!--anki:6432653264373763633264643439346562343238323064323961656364656538-->
?
Le **document, sa version et le passage utilisé**. Une URL vers « la version courante » peut afficher demain un texte différent de celui qui soutenait la réponse.

Conserver un identifiant de chunk lié à une version ou une empreinte, et un emplacement vérifiable dans la source. La résolution de la citation doit contrôler les droits actuels. Une empreinte identifie du contenu ; elle ne prouve ni sa vérité, ni son applicabilité, ni l'autorisation de le divulguer.

---

Pourquoi retirer un document de la source ne suffit-il pas à le retirer d'un RAG ? <!--anki:3535316263393961333330303432333761643365633934653262333237646233-->
?
Des **copies dérivées** peuvent rester accessibles : chunks, embeddings, résumés, caches de réponses et contexte des conversations.

Propager un retrait ou une révocation aux consommateurs concernés, bloquer immédiatement les nouvelles expositions selon le contrat de service, puis vérifier la purge des copies persistantes. Une marque de retrait peut interdire la lecture pendant la reconstruction de l'index. Elle ne garantit pas à elle seule l'effacement physique de toutes les copies ni des réponses déjà reçues.

---

Comment éviter qu'un cache de réponses RAG contourne une révocation de droits ? <!--anki:3166616632303562663964313438666161623865376138323137313131333934-->
?
Associer les entrées au **périmètre d'autorisation**, aux versions des sources et à la politique utilisée. Invalider les résultats affectés, ou revérifier l'accès aux preuves au moment de servir une entrée.

Un cache indexé uniquement par question peut partager une réponse entre deux utilisateurs de droits différents. Une clé par utilisateur ne résout pas non plus un changement de ses droits. Une durée de vie limite une exposition dans le temps ; elle ne fournit pas une révocation immédiate.

---

Calcul : un cache RAG conserve une réponse privée à 10 h 00 pendant 15 minutes. Un droit est retiré à 10 h 04 ; aucune invalidation ni revérification n'existe. Jusqu'à quand le cache peut-il exposer la réponse et quelle est la fenêtre maximale restante ? <!--anki:3835326532303461366463363435373461343339376432626631643865303266-->
?
L'entrée expire à **10 h 15**. La fenêtre restante est `15 - 4 = 11 minutes`, pour des lectures servies avant l'expiration.

Cela suppose une expiration fixe depuis l'insertion, sans prolongation à chaque lecture et sans autre copie. Le TTL ne remplace donc pas un mécanisme de révocation. Une invalidation ou une revérification des permissions au service de la réponse réduit cette fenêtre selon ses propres délais et garanties.

---

Comment distinguer abstention utile et échec de recherche dans un RAG ? <!--anki:6430613537383432633665653464373338393938393466386538636561623664-->
?
Annoter si une **preuve autorisée et applicable existe dans le corpus de référence**. Si elle existe mais n'est pas récupérée, l'abstention protège la réponse tout en révélant un échec du retrieval. Si elle n'existe pas ou reste contradictoire, une réponse affirmée peut être injustifiée.

Suivre séparément rappel, réussite des questions répondables, réponses injustifiées sur les autres cas et taux d'abstention. Tout refuser peut minimiser les erreurs factuelles tout en rendant le service inutilisable.

---

Comment évaluer une réponse RAG partielle sans récompenser l'omission des questions difficiles ? <!--anki:3366616362633138393063323464376161306561663063303137613939383530-->
?
Définir à l'avance les **éléments demandés**, puis mesurer leur couverture et le soutien des affirmations émises. Une réponse peut citer correctement un seul élément et en omettre deux autres.

Pour chaque élément manquant, distinguer preuve absente, conflit et preuve non récupérée. Dans un corpus sans preuve pour un élément, une réponse partielle explicite peut respecter le contrat ; sur un cas entièrement répondable, la même omission est un échec de complétude. Le dénominateur ne doit pas dépendre uniquement de ce que le système choisit de dire.

---

Quels changements de corpus doivent déclencher une régression RAG ? <!--anki:3437396338373639613439363465333561626538333332383131626532373462-->
?
Les **mises à jour, suppressions, changements de droits et changements de traitement**. Vérifier les réponses sur une version remplacée, une frontière de date, deux tenants, deux rôles et une source retirée.

Ajouter des tests contrefactuels : modifier un fait puis retirer sa preuve. Le résultat doit suivre la modification, puis devenir partiel ou s'abstenir selon le contrat. Versionner corpus, questions et résultats pour distinguer une évolution attendue d'une régression de recherche ou de génération.

---

## Mises en situation

Mise en situation : un assistant de support répond « remboursement sous 14 jours » alors que le contrat courant indique 30 jours ; la FAQ à 14 jours a été réingérée hier. Comment diagnostiques-tu et corriges-tu le problème ? <!--anki:3761663539396461613832623464333938306135626664363733656239303366-->
?
1. **Tracer les passages réellement utilisés**, leurs versions et leurs dates d'effet.
2. **Contrôler le périmètre** du contrat et de la FAQ pour la question posée.
3. **Appliquer une priorité métier explicite** ; la dernière ingestion n'établit pas l'autorité.
4. **Rejouer la question** à la date actuelle et à une date historique.
5. **Invalider les réponses affectées** et ajouter ces cas aux régressions.

**Piège** : augmenter top-k sans modifier la sélection des preuves applicables.

---

Mise en situation : un salarié perd un droit financier, mais reçoit encore une réponse privée depuis le cache RAG. Comment traites-tu l'incident et vérifies-tu la correction ? <!--anki:3437326663313765376437343464386338303465333066643466316364343732-->
?
1. **Bloquer le service des entrées affectées** et revérifier le périmètre d'accès.
2. **Identifier les copies concernées** : réponses, passages, citations et contexte conservé.
3. **Propager la révocation** selon le contrat et retirer les entrées exposables.
4. **Rejouer avec le même utilisateur avant et après révocation**, puis avec un autre rôle et un autre tenant.
5. **Mesurer le délai de révocation** et vérifier les accès directs aux citations.

**Piège** : corriger seulement la recherche alors que le cache court-circuite cette recherche.

---

Mise en situation : un RAG s'abstient sur 40 % des questions et affiche 100 % de citations valides. Quelles mesures permettent de décider s'il est utile et fiable ? <!--anki:3837386235386632303363653439383061363734613061653639633038326239-->
?
1. **Séparer les cas répondables des cas sans preuve ou contradictoires** dans un jeu annoté.
2. **Mesurer le rappel sur les cas répondables**, avec droits et dates représentatifs.
3. **Vérifier le soutien des affirmations**, au-delà de la validité des liens.
4. **Mesurer la complétude et les réponses injustifiées**, y compris les cas d'abstention.
5. **Comparer à une baseline** selon les critères métier, la latence et le coût.

**Piège** : déduire la fiabilité de la seule présence de citations cliquables.

---

## Sources
- [PostgreSQL 18 — politiques de sécurité par ligne et limites des rôles privilégiés](https://www.postgresql.org/docs/18/ddl-rowsecurity.html)
- [pgvector 0.8.1 — filtrage et parcours itératif des index approximatifs](https://github.com/pgvector/pgvector/blob/v0.8.1/README.md#filtering)
- [Liu, Zhang et Liang — soutien et couverture des citations](https://arxiv.org/abs/2304.09848)

## Connexions
- [[22-rag-avance|RAG avancé]] — appliquer filtres et règles de sélection aux passages
- [[96-evals-rag-agents|Evals RAG]] — distinguer recherche, preuves et qualité de réponse
- [[150-017-datasets-corpus-ia|Datasets & corpus IA]] — identifier documents, versions et transformations
- [[123-caching-agressif|Caching]] — empêcher les caches de contourner fraîcheur et droits
- [[00-moc-ai-engineering|MOC AI Engineering]]
