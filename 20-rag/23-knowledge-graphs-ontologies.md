# Knowledge graphs & ontologies — Flashcards
Tags: #flashcards #ai-engineering #rag #knowledge-graph #ontologie #llm

Qu'est-ce qu'un knowledge graph ?
?
Une représentation des connaissances sous forme de **graphe** : des **entités** (nœuds : personnes, produits, contrats…) reliées par des **relations typées** (arêtes), chacune pouvant porter des propriétés. L'unité de base est le **triplet** :
```text
(Marie Curie) —[NÉE_À]→ (Varsovie)
   sujet          prédicat      objet
```

---

RDF ou property graph ?
?
- **RDF** (standard W3C) : tout est triplet, identifié par des URI, interrogé en **SPARQL**, décrit par des ontologies **OWL**. Fort pour l'interopérabilité et le raisonnement.
- **Property graph** (Neo4j, FalkorDB, Amazon Neptune…) : nœuds et arêtes portent directement des propriétés, interrogés en **Cypher** ou en **GQL** (norme ISO depuis 2024). Plus pratique pour les applications, c'est le choix courant des stacks LLM.

---

Qu'est-ce qu'une ontologie ?
?
Le **schéma formel d'un domaine** : les **classes** (Personne, Entreprise), leur **hiérarchie** (un Fournisseur *est une* Entreprise), les **types de relations** autorisés entre classes et leurs contraintes. Elle permet de valider les données et d'**inférer** des faits.
- **Taxonomie** : seulement la hiérarchie des classes
- **Ontologie** : le schéma complet, avec relations et règles
- **Knowledge graph** : les **instances** (les données) conformes à ce schéma

---

Pourquoi une ontologie quand un LLM construit le graphe ?
?
Sans schéma, l'extraction **dérive** : doublons (« Paris », « Ville de Paris »), relations synonymes (TRAVAILLE_POUR, EMPLOYÉ_DE), types inventés, et le graphe devient impossible à interroger. L'ontologie **contraint l'extraction** (types d'entités et de relations autorisés, en [[63-guided-generation|sortie structurée]]) et ramène les entités à des **termes canoniques**.

---

Comment construire un knowledge graph avec un LLM ?
?
```text
documents → chunking → extraction (entités + relations, sous schéma)
→ résolution d'entités → chargement dans la base graphe → embeddings des nœuds
```
Outils : LLMGraphTransformer (LangChain), PropertyGraphIndex (LlamaIndex), Neo4j LLM Graph Builder, [[24-cognee|Cognee]], Graphiti.

---

Qu'est-ce que la résolution d'entités ?
?
Reconnaître que plusieurs mentions désignent **la même entité réelle** et les **fusionner** : normalisation, similarité d'embeddings, règles métier (même SIREN), puis un LLM pour trancher les cas ambigus. Trop timide, le graphe est **fragmenté** ; trop agressive, elle **fusionne à tort** des entités distinctes.

---

Quand un graphe bat-il la recherche vectorielle ?
?
- Questions **multi-hop** (« quels fournisseurs des filiales de X sont en retard ? »)
- **Relations explicites** et chemins entre entités
- **Agrégations** et comptages (« combien de contrats par client ? »)
- **Provenance** et explicabilité : on montre le chemin parcouru

La recherche vectorielle reste meilleure pour la **proximité de sens** dans du texte non structuré : on combine souvent les deux.

---

Comment combiner graphe et vecteurs ?
?
1. **Recherche vectorielle** pour trouver les chunks ou les nœuds d'entrée pertinents
2. **Parcours du graphe** à k sauts autour de ces nœuds (voisins, relations)
3. Assemblage du **sous-graphe et des chunks** dans le contexte du LLM

C'est le principe du GraphRAG « local », utile quand la réponse est répartie entre plusieurs documents liés.

---

Comment fonctionne GraphRAG de Microsoft ?
?
À l'indexation : extraction des entités et relations, détection de **communautés** (algorithme de Leiden), puis **résumés hiérarchiques** de chaque communauté. À la requête :
- **Local search** : partir des entités de la question et de leur voisinage
- **Global search** : map-reduce sur les résumés de communautés, pour les questions sur **tout le corpus** (« quels sont les thèmes principaux ? »)

L'indexation est **coûteuse** ; LazyGraphRAG repousse le travail LLM au moment de la requête pour la réduire fortement.

---

Qu'est-ce que Text2Cypher et quels sont ses risques ?
?
Le LLM **traduit la question en requête Cypher**, avec le schéma du graphe dans le prompt. Risques : requête fausse, labels inventés, requête coûteuse ou **destructrice** (injection). Parades : utilisateur de base **en lecture seule**, validation de la requête, timeouts et limites de résultats, requêtes **paramétrées** pour les cas fréquents.

---

Qu'est-ce qu'un context graph ?
?
Un terme récent, **non standardisé**, avec deux sens :
- **Traces de décision** (Foundation Capital, fin 2025) : un graphe qui relie les entités métier aux **décisions prises** (règle appliquée, exception accordée, qui a validé, quel précédent), pour que les agents retrouvent les précédents et qu'on puisse auditer leurs choix.
- **Graphe temporel** (Graphiti, Zep) : un knowledge graph où chaque fait a une **fenêtre de validité** et remonte aux **épisodes** (données brutes) qui l'ont produit.

---

Quels sont les coûts et les pièges d'un knowledge graph ?
?
- **Extraction LLM** sur tout le corpus : coûteuse et bruitée
- **Maintenance** : mises à jour incrémentales, faits qui changent, dérive du schéma
- **Évaluation** difficile : qualité de l'extraction et des réponses

Démarrer avec une **ontologie restreinte** aux besoins réels, et comparer à un [[21-rag-fondamentaux|RAG vectoriel]] sur les mêmes [[92-chainforge-evals-prompts|evals]] avant de généraliser.

---

## Connexions
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — la recherche vectorielle de base
- [[22-rag-avance|RAG avancé]] — recherche hybride et agentic RAG
- [[24-cognee|Cognee]] — une mémoire d'agent bâtie sur un graphe et une ontologie
- [[39-memoire-agents|Mémoire des agents]] — graphes temporels pour se souvenir
- [[63-guided-generation|Guided generation]] — extraire sous schéma
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection dans les requêtes générées
- [[00-moc-ai-engineering|MOC AI Engineering]]
