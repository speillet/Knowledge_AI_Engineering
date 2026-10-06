# RAG — Fondamentaux — Flashcards
Tags: #flashcards #ai-engineering #rag #retrieval #llm
<!-- summary: RAG ou fine-tuning, pipeline d'ingestion et de requête, stratégies de chunking, embeddings, bases vectorielles (HNSW, pgvector, Qdrant), top-k, grounding et citations, recall@k, quand ne pas faire de RAG. -->


Qu'est-ce que le RAG ? <!--anki:45677223625926775b30-->
?
**Retrieval-Augmented Generation** : on **récupère des passages pertinents** dans une base de connaissances et on les **injecte dans le contexte** du LLM avant qu'il génère sa réponse.

Par exemple, un assistant retrouve la procédure de remboursement avant de répondre en citant le passage. Les documents sont consultés à l'exécution : **les poids du modèle ne changent pas**. La qualité dépend à la fois de la recherche et de l'utilisation des sources ; un RAG n'empêche pas automatiquement les hallucinations.

---

Quel problème le RAG résout-il ? <!--anki:6d5e59414b626f25585e-->
?
Le modèle ne connaît ni les **données privées** ni les **faits postérieurs à son entraînement**, et il **hallucine** quand il ne sait pas : le RAG lui fournit des sources **à jour, citables et contrôlées**.

---

RAG ou fine-tuning pour apporter des connaissances ? <!--anki:4c7d4823364c5e317e31-->
?
**RAG pour les connaissances** (fraîches, volumineuses, avec droits d'accès), **[[51-fine-tuning-adaptation|fine-tuning]] pour le comportement** (format, ton, tâche). Les deux se combinent.

Le RAG permet de mettre à jour ou retirer une source sans réentraîner le modèle et facilite les citations. Le fine-tuning apprend des régularités à partir d'exemples, sans garantir la restitution fidèle d'un fait ni son effacement ultérieur. Exemple : retrouver une politique commerciale par RAG et adapter par fine-tuning la façon de structurer la réponse.

---

Quelles sont les étapes d'un pipeline RAG ? <!--anki:416b4c68676631527378-->
?
```text
Ingestion : documents → parsing → chunking → embeddings → vector store
Requête   : question → embedding → retrieval top-k → prompt augmenté → LLM → réponse
```

L'**ingestion** prépare les passages et leurs métadonnées ; elle se relance quand les sources changent. À chaque **requête**, la recherche sélectionne les passages autorisés, éventuellement reclassés, puis le modèle construit une réponse sourcée. Conserver les identifiants de documents et les versions permet de diagnostiquer une erreur. La recherche peut aussi être lexicale ou hybride : une base vectorielle n'est pas obligatoire.

---

Qu'est-ce que le chunking et pourquoi est-il critique ? <!--anki:4165744b3d31647a653d-->
?
Le **découpage des documents en passages** indexables. Trop gros : du bruit et du contexte gaspillé. Trop petit : on perd le sens. C'est souvent **le premier levier de qualité** du RAG.

Préserver les unités de sens : un titre avec son paragraphe, un tableau avec ses en-têtes, une règle avec ses exceptions. Évaluer plusieurs découpages sur des questions réelles et vérifier si le passage récupéré suffit à répondre. Le chevauchement limite les coupures mais augmente le stockage et les doublons.

---

Quelles stratégies de chunking existent ? <!--anki:5062235d2c4f48603f28-->
?
- **Taille fixe** (tokens) avec **chevauchement** (overlap)
- **Récursif / structurel** : titres, paragraphes, sections Markdown
- **Sémantique** : couper là où le sujet change
- **Parent-child** : indexer de petits chunks, renvoyer le bloc parent

---

Quels réglages de départ pour un RAG ? <!--anki:755f707256696747215b-->
?
```text
Taille de chunk      512 à 1 024 tokens   (structurel de préférence)
Chevauchement        10 à 20 % de la taille du chunk
top-k récupéré       20 à 50 avant reranking
top-k final          3 à 8 chunks dans le contexte
Contexte ajouté      titre du document + chemin des sections
```
Ce sont des **points de départ à mesurer**, pas des vérités : le bon réglage dépend des documents et se valide au recall@k ([[96-evals-rag-agents|evals de RAG]]).

Faire varier un paramètre à la fois sur un jeu fixe de questions. Mesurer aussi la précision des passages, la fidélité de la réponse, la latence et le nombre de tokens transmis. Un meilleur rappel ne suffit pas si les passages supplémentaires noient l'information ou dépassent le budget de contexte.

---

Qu'est-ce qu'un embedding ? <!--anki:714a71323d3b2f513621-->
?
Un **embedding** est un vecteur numérique appris pour représenter un texte dans un espace où une mesure de proximité aide à retrouver des contenus pertinents. La similarité cosinus est fréquente, mais dépend de l'entraînement du modèle.

Requêtes et documents doivent utiliser des **encodeurs compatibles dans le même espace**, parfois avec des préfixes ou encodeurs distincts prévus par le modèle. Une proximité élevée n'est ni une preuve d'identité ni une probabilité de vérité. Changer de modèle exige généralement de recalculer les vecteurs ([[133-embeddings-representations|embeddings en détail]]).

---

À ne pas confondre : similarité sémantique et pertinence ? <!--anki:724f3423233a34542d60-->
?
La recherche vectorielle classe par **proximité de sens**, ce qui n'est pas la même chose que **répondre à la question** :
- « symptômes de la grippe » et « traitement de la grippe » sont très proches, et l'un ne répond pas à l'autre
- une négation change le sens sans éloigner beaucoup le vecteur

D'où le **reranking** (qui évalue la paire question-passage) et la **recherche hybride** pour les termes exacts ([[22-rag-avance|RAG avancé]]).

---

Qu'est-ce qu'une base vectorielle ? <!--anki:77764970652b4b3d5857-->
?
Une **base vectorielle** stocke des vecteurs, leurs identifiants et des métadonnées, puis retrouve les éléments proches d'une requête selon une métrique. Un index approximatif, comme **HNSW**, échange un peu de rappel contre moins de calcul ; une recherche exacte reste possible sur de petits corpus.

Évaluer conjointement rappel, latence, mémoire, mises à jour et filtres d'accès. Le nombre de vecteurs seul ne garantit pas une réponse en quelques millisecondes : la dimension, les filtres et le matériel comptent aussi.

---

Comment choisir le top-k d'un RAG ? <!--anki:6b342c707e4867592653-->
?
C'est un compromis : **k trop petit** → information manquante (**recall** faible) ; **k trop grand** → bruit, coût et dilution du contexte. On récupère souvent large, puis on filtre ou on [[22-rag-avance|re-classe]].

Distinguer le nombre de **candidats récupérés** de celui des passages réellement envoyés au modèle. Sur un jeu annoté, augmenter le premier jusqu'à obtenir un rappel satisfaisant, puis limiter le second selon la précision et le budget de tokens. Dédupliquer les passages évite de dépenser ce budget plusieurs fois pour la même preuve.

---

Quelle est la limite principale du retrieval vectoriel seul ? <!--anki:4d2f444e6238555b4c3b-->
?
Il rate les **termes exacts** (codes produits, références, noms propres, sigles) → on passe à la **[[22-rag-avance|recherche hybride]]** (BM25 + vectoriel) et au reranking.

Par exemple, une recherche sur `AB-123` peut remonter un produit au nom proche au lieu de la référence exacte. La branche lexicale préserve ces correspondances ; la branche vectorielle retrouve les paraphrases. Fusionner leurs candidats puis mesurer le rappel par type de requête permet de vérifier que l'hybride apporte réellement un gain.

---

Comment rendre une réponse RAG vérifiable ? <!--anki:737874235b314a4a3373-->
?
En demandant au modèle de **citer ses sources** (identifiants de chunks) et de **répondre « je ne sais pas »** si le contexte ne contient pas l'information : c'est le **grounding**.

L'application doit vérifier que chaque identifiant cité existe et renvoie à un passage accessible. Ensuite, contrôler que le passage **étaye réellement l'affirmation** : une citation valide peut être hors sujet. Présenter la source et sa date aide l'utilisateur à vérifier ; une consigne de citation seule ne garantit pas la fidélité.

---

Comment évaluer un RAG ? <!--anki:79282e50452d245d4c69-->
?
Séparément : le **retrieval** (**recall@k**, MRR : a-t-on récupéré le bon passage ?) et la **génération** (**faithfulness**, pertinence de la réponse), sur un [[92-chainforge-evals-prompts|golden dataset]] de questions.

Ajouter des questions sans réponse dans le corpus pour tester l'abstention et des cas avec restrictions d'accès. Si la preuve manque dans les passages récupérés, corriger la recherche ; si elle est présente mais mal utilisée, corriger la génération. Mesurer aussi latence et coût afin de comparer des variantes déployables.

---

Quand ne pas faire de RAG ? <!--anki:495f6e2451306c4a7269-->
?
- **Corpus petit et stable** (quelques centaines de milliers de tokens) : tout mettre en contexte avec **prompt caching** est plus simple et souvent plus fiable ([[137-long-contexte|long contexte]])
- **Besoin de style, de format ou de comportement** : c'est un problème de prompt ou de fine-tuning, pas de connaissances
- **Données structurées et agrégations** (« combien de commandes en mars ? ») : une requête SQL via un outil répond juste, le retrieval de chunks non ([[26-text-to-sql|text-to-SQL]])
- **Connaissances générales** que le modèle possède déjà

**Piège** : ajouter un RAG par réflexe, puis passer des semaines sur le chunking d'un corpus qui tenait dans le contexte.

---

Calcul : combien coûte l'indexation de 50 000 documents de 10 pages ? <!--anki:3339373433333537663864353435373962653930323631643639396438623461-->
?
Hypothèses : 500 tokens par page, chunks de 500 tokens, embeddings par API à 0,02 € par million de tokens, vecteurs de 1 024 dimensions en float32.
```text
tokens    : 50 000 × 10 × 500    = 250 M
embedding : 250 M × 0,02 €/M     = 5 €
vecteurs  : 250 M / 500          = 500 000
stockage  : 500 000 × 1 024 × 4 o ≈ 2 Go, plus l'index HNSW
```
L'embedding est presque gratuit. Ce qui coûte : le **parsing** des documents, le **contextual retrieval** (un appel LLM par chunk) et la **ré-indexation** complète à chaque changement de modèle d'embedding ([[25-chunking-contextual-retrieval|contextual retrieval]]).

---

## Mises en situation

Mise en situation : ton RAG sur la documentation interne répond « je ne trouve pas » sur des questions dont tu sais que la réponse existe. Comment diagnostiques-tu ? <!--anki:44667c316e40784c526c-->
?
1. **Isoler la couche fautive** : le bon passage est-il dans le top-k ? Si oui, le problème vient de la **génération** ; sinon, du **retrieval** ([[96-evals-rag-agents|evals de RAG]])
2. **Regarder les chunks** : découpage qui coupe les tableaux ou les titres, parsing qui perd la structure du PDF ([[162-document-parsing|parsing]])
3. **Tester les termes exacts** : si les questions contiennent des références ou des sigles, le vectoriel seul les rate → **recherche hybride** ([[22-rag-avance|RAG avancé]])
4. **Vérifier k et les filtres** : top-k trop petit, filtre de métadonnées trop strict, documents non réindexés
5. **Mesurer** : recall@k sur un golden dataset avant et après chaque correction

**Piège** : changer de modèle d'embedding en premier, alors que le chunking et le parsing expliquent la plupart des cas.

---

Mise en situation : le métier te demande un RAG sur 200 000 documents, dont des notes RH réservées à certains services. Quelles décisions prends-tu avant d'indexer ? <!--anki:6e6c53594f5f666e487c-->
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
- [[25-chunking-contextual-retrieval|Chunking avancé & contextual retrieval]] — rendre chaque chunk trouvable
- [[26-text-to-sql|Text-to-SQL]] — les questions chiffrées que le RAG ne sait pas traiter
- [[123-caching-agressif|Caching]] — prompt caching et caches de réponses
- [[134-recherche-vectorielle-ann|Recherche vectorielle]] — index ANN, HNSW et quantization des vecteurs
- [[141-system-design-llm|System design LLM]] — la méthode de conception
- [[143-hallucinations-grounding|Hallucinations & grounding]] — citations, abstention et vérification
- [[23-knowledge-graphs-ontologies|Knowledge graphs]] — GraphRAG et données reliées
- [[27-agents-recherche-deep-research|Agents de recherche]] — la recherche en plusieurs étapes, avec citations
- [[42-langchain-fondamentaux|LangChain]] — les briques de base du framework
- [[00-moc-ai-engineering|MOC AI Engineering]]
