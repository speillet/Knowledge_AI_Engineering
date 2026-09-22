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

Qu'est-ce qu'un embedding ?
?
Un **vecteur dense** qui représente le sens d'un texte : deux textes proches en sens ont des vecteurs proches (**similarité cosinus**). Documents et requêtes doivent être encodés **avec le même modèle**.

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

## Connexions
- [[22-rag-avance|RAG avancé]] — hybride, reranking, query rewriting
- [[11-prompt-engineering-avance|Prompt engineering]] — quand le prompt ne suffit plus
- [[35-context-engineering|Context engineering]] — placer les chunks dans le budget de contexte
- [[51-fine-tuning-adaptation|Fine-tuning]] — connaissances vs comportement
- [[92-chainforge-evals-prompts|Evals]] — évaluer le pipeline de retrieval
- [[00-moc-ai-engineering|MOC AI Engineering]]
