# RAG — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #llm

Qu'est-ce que le RAG ?
?
**Retrieval-Augmented Generation** : on **récupère des passages pertinents** dans une base de connaissances et on les **injecte dans le contexte** du LLM avant qu'il génère sa réponse.

---

Quel problème le RAG résout-il ?
?
Le modèle ne connaît ni les **données privées** ni les **faits postérieurs à son entraînement**, et il **hallucine** quand il ne sait pas : le RAG lui fournit des sources **à jour, citables et contrôlées**.

---

RAG ou fine-tuning pour apporter des connaissances ?
?
**RAG pour les connaissances** (fraîches, volumineuses, avec droits d'accès), **[[51-fine-tuning-adaptation|fine-tuning]] pour le comportement** (format, ton, tâche). Les deux se combinent.

---

Quelles sont les étapes d'un pipeline RAG ?
?
```text
Ingestion : documents → parsing → chunking → embeddings → vector store
Requête   : question → embedding → retrieval top-k → prompt augmenté → LLM → réponse
```

---

Qu'est-ce que le chunking et pourquoi est-il critique ?
?
Le **découpage des documents en passages** indexables. Trop gros : du bruit et du contexte gaspillé. Trop petit : on perd le sens. C'est souvent **le premier levier de qualité** du RAG.

---

Quelles stratégies de chunking existent ?
?
- **Taille fixe** (tokens) avec **chevauchement** (overlap)
- **Récursif / structurel** : titres, paragraphes, sections Markdown
- **Sémantique** : couper là où le sujet change
- **Parent-child** : indexer de petits chunks, renvoyer le bloc parent

---

Quels réglages de départ pour un RAG ?
?
```text
Taille de chunk      512 à 1 024 tokens   (structurel de préférence)
Chevauchement        10 à 20 % de la taille du chunk
top-k récupéré       20 à 50 avant reranking
top-k final          3 à 8 chunks dans le contexte
Contexte ajouté      titre du document + chemin des sections
```
Ce sont des **points de départ à mesurer**, pas des vérités : le bon réglage dépend des documents et se valide au recall@k ([[96-evals-rag-agents|evals de RAG]]).

---

Qu'est-ce qu'un embedding ?
?
Un **vecteur dense** qui représente le sens d'un texte : deux textes proches en sens ont des vecteurs proches (**similarité cosinus**). Documents et requêtes doivent être encodés **avec le même modèle** ([[133-embeddings-representations|embeddings en détail]]).

---

À ne pas confondre : similarité sémantique et pertinence ?
?
La recherche vectorielle classe par **proximité de sens**, ce qui n'est pas la même chose que **répondre à la question** :
- « symptômes de la grippe » et « traitement de la grippe » sont très proches, et l'un ne répond pas à l'autre
- une négation change le sens sans éloigner beaucoup le vecteur

D'où le **reranking** (qui évalue la paire question-passage) et la **recherche hybride** pour les termes exacts ([[22-rag-avance|RAG avancé]]).

---

Qu'est-ce qu'une base vectorielle ?
?
Un stockage qui indexe les embeddings pour une **recherche des plus proches voisins approximative** (ANN, ex. **HNSW**) en quelques ms, même sur des millions de vecteurs. Exemples : **pgvector, Qdrant, Weaviate, Milvus, Chroma**.

---

Comment choisir le top-k ?
?
C'est un compromis : **k trop petit** → information manquante (**recall** faible) ; **k trop grand** → bruit, coût et dilution du contexte. On récupère souvent large, puis on filtre ou on [[22-rag-avance|re-classe]].

---

Quelle est la limite principale du retrieval vectoriel seul ?
?
Il rate les **termes exacts** (codes produits, références, noms propres, sigles) → on passe à la **[[22-rag-avance|recherche hybride]]** (BM25 + vectoriel) et au reranking.

---

Comment rendre une réponse RAG vérifiable ?
?
En demandant au modèle de **citer ses sources** (identifiants de chunks) et de **répondre « je ne sais pas »** si le contexte ne contient pas l'information : c'est le **grounding**.

---

Comment évaluer un RAG ?
?
Séparément : le **retrieval** (**recall@k**, MRR : a-t-on récupéré le bon passage ?) et la **génération** (**faithfulness**, pertinence de la réponse), sur un [[92-chainforge-evals-prompts|golden dataset]] de questions.

---

## Mises en situation

Mise en situation : ton RAG sur la documentation interne répond « je ne trouve pas » sur des questions dont tu sais que la réponse existe. Comment diagnostiques-tu ?
?
1. **Isoler la couche fautive** : le bon passage est-il dans le top-k ? Si oui, le problème vient de la **génération** ; sinon, du **retrieval** ([[96-evals-rag-agents|evals de RAG]])
2. **Regarder les chunks** : découpage qui coupe les tableaux ou les titres, parsing qui perd la structure du PDF ([[162-document-parsing|parsing]])
3. **Tester les termes exacts** : si les questions contiennent des références ou des sigles, le vectoriel seul les rate → **recherche hybride** ([[22-rag-avance|RAG avancé]])
4. **Vérifier k et les filtres** : top-k trop petit, filtre de métadonnées trop strict, documents non réindexés
5. **Mesurer** : recall@k sur un golden dataset avant et après chaque correction

**Piège** : changer de modèle d'embedding en premier, alors que le chunking et le parsing expliquent la plupart des cas.

---

Mise en situation : le métier te demande un RAG sur 200 000 documents, dont des notes RH réservées à certains services. Quelles décisions prends-tu avant d'indexer ?
?
1. **Droits d'accès d'abord** : chaque chunk porte ses métadonnées de permissions, et le filtrage se fait **au retrieval**, jamais après coup ([[101-securite-llm-guardrails|sécurité]])
2. **Périmètre** : commencer par un corpus utile et bien maîtrisé plutôt que tout ingérer
3. **Fraîcheur** : pipeline de ré-ingestion et suppression, sinon l'index dérive ([[113-monitoring-drift-feedback|drift]])
4. **Chunking** adapté aux documents réels (structure, tableaux) et **citations** obligatoires dans les réponses
5. **Coût et volumétrie** : taille de l'index, coût des embeddings, base vectorielle adaptée

**Piège** : indexer d'abord et traiter les droits « plus tard ». Il faudra tout réindexer.

---

## Connexions
- [[22-rag-avance|RAG avancé]] — hybride, reranking, query rewriting
- [[11-prompt-engineering-avance|Prompt engineering]] — quand le prompt ne suffit plus
- [[35-context-engineering|Context engineering]] — placer les chunks dans le budget de contexte
- [[51-fine-tuning-adaptation|Fine-tuning]] — connaissances vs comportement
- [[92-chainforge-evals-prompts|Evals]] — évaluer le pipeline de retrieval
- [[133-embeddings-representations|Embeddings & représentations]] — modèles d'embedding en détail
- [[162-document-parsing|Parsing de documents]] — la qualité de l'ingestion
- [[96-evals-rag-agents|Evals de RAG]] — recall@k, faithfulness
- [[00-moc-ai-engineering|MOC AI Engineering]]
