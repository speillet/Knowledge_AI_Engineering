# Knowledge graphs & ontologies — Flashcards
Tags: #flashcards #ai-engineering #rag #knowledge-graph #ontologie #llm
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: triplets, RDF ou property graph (Cypher, GQL), ontologie et taxonomie, extraction par LLM sous schéma, résolution d'entités, graphe ou vecteurs, GraphRAG local et global, Text2Cypher, context graph, coûts, provenance des relations, monde ouvert, négation des relations. -->


Qu'est-ce qu'un knowledge graph ? <!--anki:75794e4c4c3a65215f7b-->
?
Une représentation des connaissances sous forme de **graphe** : des **entités** (nœuds : personnes, produits, contrats…) reliées par des **relations typées** (arêtes), chacune pouvant porter des propriétés. L'unité de base est le **triplet** :
```text
(Marie Curie) —[NÉE_À]→ (Varsovie)
   sujet          prédicat      objet
```

L'intérêt est de pouvoir suivre les relations : retrouver les personnes liées à une organisation, puis les contrats concernés. Conserver la source et, si nécessaire, la période de validité des faits. Un graphe représente ce qui a été enregistré ; il ne garantit pas que chaque relation extraite soit vraie.

---

RDF ou property graph ? <!--anki:6f6a784b296a54416f74-->
?
- **RDF** (standard W3C) : tout est triplet, identifié par des URI, interrogé en **SPARQL**, décrit par des ontologies **OWL**. Fort pour l'interopérabilité et le raisonnement.
- **Property graph** (Neo4j, FalkorDB, Amazon Neptune…) : nœuds et arêtes portent directement des propriétés, interrogés en **Cypher** ou en **GQL** (norme ISO depuis 2024). Plus pratique pour les applications, c'est le choix courant des stacks LLM.

---

Qu'est-ce qu'une ontologie ? <!--anki:473f21414c2b645b3135-->
?
Le **schéma formel d'un domaine** : les **classes** (Personne, Entreprise), leur **hiérarchie** (un Fournisseur *est une* Entreprise), les **types de relations** autorisés entre classes et leurs contraintes. Elle permet de valider les données et d'**inférer** des faits.
- **Taxonomie** : seulement la hiérarchie des classes
- **Ontologie** : le schéma complet, avec relations et règles
- **Knowledge graph** : les **instances** (les données) conformes à ce schéma

---

Pourquoi une ontologie quand un LLM construit le graphe ? <!--anki:66354d4240287b307542-->
?
Sans schéma, l'extraction **dérive** : doublons (« Paris », « Ville de Paris »), relations synonymes (TRAVAILLE_POUR, EMPLOYÉ_DE), types inventés, et le graphe devient impossible à interroger. L'ontologie **contraint l'extraction** (types d'entités et de relations autorisés, en [[63-guided-generation|sortie structurée]]) et ramène les entités à des **termes canoniques**.

Par exemple, imposer une relation `EMPLOYE_PAR` évite trois noms pour le même lien. Cela ne prouve toutefois ni que l'emploi existe ni que deux personnes homonymes sont identiques. Conserver la source de chaque relation et contrôler séparément **validité du schéma, résolution d'identité et exactitude factuelle**.

---

Comment construire un knowledge graph avec un LLM ? <!--anki:7645732d313e6c377d63-->
?
```text
documents → passages → extraction d'entités et relations sous schéma
→ résolution d'entités → validation → stockage du graphe
```
Définir d'abord les types d'entités et de relations autorisés. L'extracteur doit associer chaque fait à un passage source ; la **résolution d'entités** fusionne ensuite les mentions désignant le même objet sans confondre les homonymes.

Vérifier contraintes, doublons et relations douteuses avant chargement. Des embeddings peuvent faciliter la recherche, mais ne sont pas obligatoires. Des outils comme [[24-cognee|Cognee]] automatisent une partie du pipeline ; ils ne remplacent pas la validation des faits.

---

Qu'est-ce que la résolution d'entités ? <!--anki:70586539675d5f58613a-->
?
Reconnaître que plusieurs mentions désignent **la même entité réelle** et les **fusionner** : normalisation, similarité d'embeddings, règles métier (même SIREN), puis un LLM pour trancher les cas ambigus. Trop timide, le graphe est **fragmenté** ; trop agressive, elle **fusionne à tort** des entités distinctes.

Deux établissements portant le même nom ne doivent pas être fusionnés sur la seule ressemblance textuelle. Préférer un identifiant stable lorsqu'il existe, conserver les mentions et la provenance, puis prévoir une revue des cas incertains. Une fusion erronée propage des attributs et relations à la mauvaise entité ; elle doit pouvoir être annulée.

---

Quand un graphe bat-il la recherche vectorielle ? <!--anki:696f362a64337e444e58-->
?
- Questions **multi-hop** (« quels fournisseurs des filiales de X sont en retard ? »)
- **Relations explicites** et chemins entre entités
- **Agrégations** et comptages (« combien de contrats par client ? »)
- **Provenance** et explicabilité : on montre le chemin parcouru

La recherche vectorielle reste meilleure pour la **proximité de sens** dans du texte non structuré : on combine souvent les deux.

---

Comment combiner graphe et vecteurs ? <!--anki:5268263e733e2e3f7d6a-->
?
1. **Recherche vectorielle** pour trouver les chunks ou les nœuds d'entrée pertinents
2. **Parcours du graphe** à k sauts autour de ces nœuds (voisins, relations)
3. Assemblage du **sous-graphe et des chunks** dans le contexte du LLM

C'est le principe du GraphRAG « local », utile quand la réponse est répartie entre plusieurs documents liés.

Exemple : retrouver un composant par sa description, puis suivre les liens vers ses fournisseurs. Borner profondeur et nombre de voisins : un nœud très connecté peut remplir le contexte de relations inutiles. Conserver la provenance des relations pour vérifier la réponse.

---

Comment fonctionne GraphRAG de Microsoft ? <!--anki:7a516429687c6a513b6d-->
?
À l'indexation : extraction des entités et relations, détection de **communautés** (algorithme de Leiden), puis **résumés hiérarchiques** de chaque communauté. À la requête :
- **Local search** : partir des entités de la question et de leur voisinage
- **Global search** : map-reduce sur les résumés de communautés, pour les questions sur **tout le corpus** (« quels sont les thèmes principaux ? »)

L'indexation est **coûteuse** ; LazyGraphRAG repousse le travail LLM au moment de la requête pour la réduire fortement.

---

Qu'est-ce que Text2Cypher et quels sont ses risques ? <!--anki:4450547e3f4856545139-->
?
Le LLM **traduit la question en requête Cypher**, avec le schéma du graphe dans le prompt. Risques : requête fausse, labels inventés, requête coûteuse ou **destructrice** (injection). Parades : utilisateur de base **en lecture seule**, validation de la requête, timeouts et limites de résultats, requêtes **paramétrées** pour les cas fréquents.

Une requête syntaxiquement valide peut traverser le mauvais type de relation. Tester sur un petit graphe dont la réponse est connue, puis contrôler le plan d'exécution. Un `LIMIT` borne les lignes retournées, pas nécessairement le travail effectué avant ce retour.

---

Qu'est-ce qu'un context graph ? <!--anki:7256243e362425497749-->
?
Un terme récent, **non standardisé**, avec deux sens :
- **Traces de décision** (Foundation Capital, fin 2025) : un graphe qui relie les entités métier aux **décisions prises** (règle appliquée, exception accordée, qui a validé, quel précédent), pour que les agents retrouvent les précédents et qu'on puisse auditer leurs choix.
- **Graphe temporel** (Graphiti, Zep) : un knowledge graph où chaque fait a une **fenêtre de validité** et remonte aux **épisodes** (données brutes) qui l'ont produit.

---

Quels sont les coûts et les pièges d'un knowledge graph ? <!--anki:64642c3535557229767e-->
?
Le coût comprend **extraction, maintenance et évaluation**, pas seulement le stockage du graphe. Une relation erronée peut contaminer plusieurs réponses multi-hop.

Exemple : transformer « fournisseur envisagé » en « fournisseur agréé » crée une arête plausible mais fausse. Conserver le passage justificatif, le type et la période de validité de la relation permet de la contrôler et de la retirer quand la source change.

Démarrer avec une **ontologie restreinte** ; mesurer qualité des entités, des relations et des réponses. Comparer le gain à un [[21-rag-fondamentaux|RAG vectoriel]] sur les mêmes [[92-chainforge-evals-prompts|evals]], en intégrant le coût de correction humaine.

---

Pourquoi conserver la provenance de chaque relation extraite dans un knowledge graph ? <!--anki:3866343838343766326361623433336262323237373366623366393334363032-->
?
Une **relation extraite** reste une affirmation issue d'une source, parfois incertaine. Conserver document, passage, date de validité et version d'extracteur permet de vérifier, corriger ou retirer cette affirmation.

Si deux rapports attribuent des dirigeants différents à une société, garder leurs périodes et preuves évite d'écraser arbitrairement l'une des relations. Une suppression doit pouvoir retrouver les relations dérivées du document. Le graphe gagne en traçabilité ; il ne devient pas vrai par construction. Distinguer relation observée, relation inférée et fait validé.

---

À ne pas confondre : absence de relation dans un graphe et preuve que la relation est fausse ? <!--anki:6665303530386666656164313464313162653766626631376135653063313662-->
?
Dans une sémantique de **monde ouvert**, ne pas connaître une relation ne signifie pas sa négation. Un graphe sans lien « possède » entre une société et une filiale peut simplement être incomplet.

Une règle de monde fermé n'est défendable que pour un périmètre déclaré complet, avec date et provenance. Un agent doit donc distinguer relation confirmée, réfutée et inconnue. La convention du moteur de requête ne transforme pas l'incomplétude des sources en certitude métier.

---

Comment éviter de transformer une relation hypothétique extraite par LLM en fait du knowledge graph ? <!--anki:3934356638626430663463313466363138326637623836653834353263613063-->
?
Conserver **modalité, négation et attribution** : « envisage de racheter » ne signifie pas « possède ». Modéliser l'affirmation avec sa source, sa date et son statut avant d'en dériver une relation exploitable.

Valider les règles de promotion sur des exemples négatifs et conditionnels. Deux mentions répétées d'une même rumeur ne constituent pas deux confirmations indépendantes. Une relation sans ces qualifications peut rendre les parcours multi-hop cohérents en apparence mais factuellement faux.

---

## Mises en situation

Mise en situation : ton graphe extrait par LLM contient « Société Générale », « Societe Generale » et « SG » comme trois entités distinctes, et les requêtes multi-hop échouent. Comment corriges-tu ? <!--anki:6670413d484e4a557b4d-->
?
1. **Cause** : extraction sans ontologie ni résolution d'entités, donc un graphe **fragmenté**
2. **Ontologie restreinte** : types d'entités et de relations autorisés, extraction en sortie structurée ([[63-guided-generation|guided generation]])
3. **Résolution d'entités** : normalisation, similarité d'embeddings, règles métier (même SIREN), LLM en arbitre sur les cas douteux
4. **Fusionner l'existant** plutôt que tout ré-extraire, si le corpus est coûteux à retraiter
5. **Mesurer** : requêtes de test connues, et surveiller le nombre d'entités par concept

**Piège** : une résolution trop agressive qui fusionne une filiale et sa maison mère.

---

Mise en situation : un chef de projet veut exposer Text2Cypher aux utilisateurs métier, pour qu'ils interrogent le graphe en langage naturel. Quelles conditions poses-tu ? <!--anki:4a3b4c694f233a516228-->
?
1. **Utilisateur de base en lecture seule** : aucune requête ne doit pouvoir modifier ou supprimer le graphe
2. **Validation de la requête générée** avant exécution, avec labels et relations vérifiés contre le schéma
3. **Timeouts et limites** de résultats, contre les requêtes qui balayent tout le graphe
4. **Requêtes paramétrées** pour les questions fréquentes, le LLM ne remplissant que les paramètres
5. **Afficher la requête et le chemin** parcouru, pour que l'utilisateur juge la réponse ([[102-menaces-agents|menaces]])

**Piège** : donner au générateur un compte d'administration « le temps des tests ».

---

## Sources

- [Microsoft — GraphRAG, indexation et recherche](https://microsoft.github.io/graphrag/)

- [W3C — modèle de provenance PROV](https://www.w3.org/TR/prov-overview/) — approfondissement ciblé du 12 novembre 2026 ; les exemples pédagogiques sont construits pour cette revue.

- Complément du 14 novembre 2026 — Monde ouvert et assertions : [W3C — OWL 2 Primer](https://www.w3.org/TR/owl2-primer/).

## Connexions
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — la recherche vectorielle de base
- [[22-rag-avance|RAG avancé]] — recherche hybride et agentic RAG
- [[24-cognee|Cognee]] — une mémoire d'agent bâtie sur un graphe et une ontologie
- [[39-memoire-agents|Mémoire des agents]] — graphes temporels pour se souvenir
- [[63-guided-generation|Guided generation]] — extraire sous schéma
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection dans les requêtes générées
- [[26-text-to-sql|Text-to-SQL]] — le même problème que Text2Cypher, sur une base relationnelle
- [[00-moc-ai-engineering|MOC AI Engineering]]
