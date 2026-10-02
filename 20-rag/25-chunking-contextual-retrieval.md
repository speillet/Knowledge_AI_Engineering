# Chunking avancé & contextual retrieval — Flashcards
Tags: #flashcards #ai-engineering #rag #chunking #retrieval #llm
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Pourquoi un chunk isolé est-il souvent introuvable ?
?
<!--anki:7a544f517c5831297e3c-->
Parce qu'il a **perdu son contexte** en étant découpé. « Le chiffre d'affaires a progressé de 3 % » ne dit ni **quelle entreprise** ni **quel trimestre** : ni son embedding ni ses mots-clés ne correspondent à la question « CA d'ACME au T2 2025 ». Le problème n'est pas l'index, c'est **ce qu'on a indexé**.

---

Qu'est-ce que le contextual retrieval ?
?
<!--anki:5052216e2d52403b2b54-->
Une technique publiée par Anthropic (2024) : avant l'indexation, un LLM rédige pour **chaque chunk** une courte phrase de contexte (50 à 100 tokens) tirée du **document entier**, qu'on **préfixe au chunk**. On calcule ensuite l'embedding **et** l'index BM25 sur ce texte enrichi.
```text
[Contexte : extrait du rapport trimestriel d'ACME, T2 2025,
section résultats financiers.]
Le chiffre d'affaires a progressé de 3 % par rapport au trimestre précédent.
```

---

Quel gain et quel coût pour le contextual retrieval ?
?
<!--anki:727b7357643b706e5729-->
**Gain** mesuré par Anthropic : **−49 % d'échecs de retrieval** (embeddings et BM25 contextualisés), **−67 %** en ajoutant un reranker.

**Coût** : un appel LLM par chunk, à l'ingestion seulement. Le document entier est envoyé à chaque appel, donc le **[[123-caching-agressif|prompt caching]]** est indispensable : le document est mis en cache une fois, seuls le chunk et la réponse changent. Ré-ingérer un document modifié repaie ce coût.

---

Qu'est-ce que le late chunking ?
?
<!--anki:52446439345e515e6d-->
Inverser l'ordre habituel : on passe **le document entier** (ou une large fenêtre) dans un modèle d'embedding à **long contexte**, puis on découpe **les vecteurs de tokens** en chunks et on les moyenne (pooling). Chaque vecteur de chunk a « vu » le reste du document, **sans appel LLM**. Proposé par Jina AI (2024).

Limite : il faut un modèle d'embedding qui expose les vecteurs par token et accepte des documents longs ([[133-embeddings-representations|embeddings]]).

---

À ne pas confondre : contextual retrieval et late chunking ?
?
<!--anki:483b40683c78345a3126-->
- **Contextual retrieval** : ajoute du contexte **en texte**, rédigé par un LLM. Profite aussi à **BM25**, reste lisible et vérifiable, mais coûte un appel LLM par chunk
- **Late chunking** : ajoute du contexte **dans le vecteur**, par l'encodeur. Pas d'appel LLM, mais aucun effet sur la recherche lexicale et dépend du modèle d'embedding

Le premier est plus cher et plus robuste, le second plus économique.

---

Quels sont les effets d'une taille de chunk trop petite ou trop grande ?
?
<!--anki:436e5231376f26446864-->
- **Trop petit** (moins de 100 tokens) : précis mais **sans contexte**, et la réponse est éclatée entre plusieurs chunks
- **Trop grand** (plus de 1 000 tokens) : l'embedding **moyenne plusieurs sujets** et devient flou, et chaque chunk remonté coûte cher en contexte

Point de départ courant : **300 à 800 tokens** avec 10 à 20 % de chevauchement, puis **mesurer** plusieurs tailles sur ses propres questions ([[21-rag-fondamentaux|réglages de départ]]).

---

Qu'est-ce que le pattern small-to-big (parent-child) ?
?
<!--anki:6f4d265d7a2f3e534a41-->
**Chercher petit, renvoyer grand** : on indexe de **petits chunks** (phrases, paragraphes) pour une recherche précise, et on renvoie au LLM leur **bloc parent** (section, page) pour qu'il ait le contexte. Variante **sentence window** : renvoyer la phrase trouvée avec les N phrases voisines.

Il découple deux besoins contradictoires : la **précision** de la recherche et la **complétude** du contexte.

---

Le chunking sémantique vaut-il son coût ?
?
<!--anki:67377e70797147715e59-->
**Pas systématiquement.** Couper là où les embeddings de phrases consécutives divergent semble plus intelligent, mais des évaluations publiées (2024) ne montrent **pas de gain constant** sur un découpage récursif bien réglé, pour un coût d'ingestion supérieur. La **structure du document** (titres, sections) est souvent un meilleur signal que la similarité ([[162-document-parsing|chunking structurel]]).

---

Qu'est-ce que le chunking par propositions ?
?
<!--anki:79456d2e71752a256331-->
Faire réécrire le texte par un LLM en **propositions atomiques et autonomes** (« ACME a réalisé un CA de 12 M€ au T2 2025 »), chacune indexée séparément. Très précis pour les questions factuelles, mais **coûteux**, et la réécriture peut **déformer** le texte source : on garde toujours le lien vers le passage original pour la citation.

---

Pourquoi enrichir les chunks avec des métadonnées ?
?
<!--anki:433a363b4023495b3046-->
- **Fil d'Ariane** préfixé au texte (titre du document > section > sous-section) : du contexte **gratuit**, sans appel LLM
- **Champs filtrables** (date, source, langue, droits d'accès) : filtrer **avant** la recherche vectorielle ([[22-rag-avance|filtrage et ACL]])
- **Identifiants stables** (document, page, position) : citations et mises à jour incrémentales

C'est la première amélioration à essayer : peu chère, souvent efficace.

---

Comment comparer deux stratégies de chunking ?
?
<!--anki:6d51784b656f656e423a-->
1. Un jeu de **questions réelles** avec, pour chacune, les **passages attendus**
2. Ré-indexer le **même corpus** avec chaque stratégie
3. Comparer le **recall@k** et le **MRR** du retrieval, puis la qualité des réponses finales ([[96-evals-rag-agents|evals RAG]])
4. Comparer aussi le **coût d'ingestion** et le **nombre de tokens** injectés par réponse

Comme les chunks changent entre stratégies, on juge « passage attendu retrouvé » par **recouvrement de texte**, pas par identifiant de chunk.

---

## Mises en situation

Mise en situation : ton RAG sur 3 000 rapports financiers répond souvent « information non trouvée » alors que le chiffre figure dans le corpus. Les chunks font 400 tokens. Comment procèdes-tu ?
?
<!--anki:7126512e53305a26792c-->
1. **Diagnostiquer** : sur 50 questions ratées, le bon passage est-il dans le top 20 ? Si non, c'est le retrieval
2. **Lire les chunks** : ils disent souvent « le chiffre d'affaires » sans nom d'entreprise ni période
3. **Ajouter le fil d'Ariane** (entreprise, année, section) à chaque chunk, sans coût LLM
4. **Tester le contextual retrieval** avec prompt caching, puis ajouter un **reranker** ([[22-rag-avance|reranking]])
5. **Mesurer** le recall@k avant et après, et le coût d'ingestion total

**Piège** : augmenter le top-k pour « tout ramener », ce qui noie le modèle sans rendre les chunks plus trouvables.

---

Mise en situation : on te demande de passer tout le corpus en chunking sémantique « parce que c'est l'état de l'art ». Le corpus est de la documentation technique bien structurée en Markdown. Que réponds-tu ?
?
<!--anki:7a253f545f55776c6c67-->
1. **Rappeler l'objectif** : le chunking se juge au recall@k sur nos questions, pas à la mode
2. **Constater l'atout du corpus** : les titres Markdown donnent déjà des frontières de sens fiables
3. **Proposer un comparatif** : découpage par sections avec fil d'Ariane, contre chunking sémantique, sur le même jeu de questions
4. **Chiffrer** le coût d'ingestion et de ré-ingestion de chaque option
5. **Décider sur les mesures**, et documenter le choix dans un ADR ([[147-leadership-technique-ia|ADR]])

**Piège** : changer de stratégie de chunking sans jeu d'eval, et découvrir la régression par les utilisateurs.

---

## Connexions
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — les stratégies de chunking de base
- [[22-rag-avance|RAG — Avancé]] — hybride, reranking, filtres
- [[162-document-parsing|Parsing de documents]] — la structure avant le découpage
- [[133-embeddings-representations|Embeddings]] — modèles à long contexte et late interaction
- [[123-caching-agressif|Caching]] — rendre le contextual retrieval abordable
- [[96-evals-rag-agents|Évaluation des RAG]] — juger une stratégie au recall@k
- [[00-moc-ai-engineering|MOC AI Engineering]]
