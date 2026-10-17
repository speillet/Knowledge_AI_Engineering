# Recherche vectorielle & index ANN — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #vector-search #rag
<!-- summary: brute force ou ANN, rappel de l'index ou rappel du retrieval, calcul de la mémoire d'un index HNSW, HNSW et ses paramètres, IVF, Product Quantization, quantization scalaire et binaire, DiskANN, filtrage, recall de l'index, pgvector ou base dédiée, exploitation, dimensionnement. -->


Pourquoi ne pas faire une recherche exacte (brute force) des plus proches voisins ? <!--anki:434b37366f67544e55-->
?
La recherche exacte compare la requête à **tous les vecteurs** : coût **linéaire** en taille du corpus. Elle reste raisonnable jusqu'à **quelques centaines de milliers** de vecteurs (surtout sur GPU), mais au-delà on utilise un index **ANN** (Approximate Nearest Neighbors) qui sacrifie un peu de **rappel** pour une recherche **sous-linéaire**.

---

Comment fonctionne HNSW ? <!--anki:4a582545506f752e5a6e-->
?
**Hierarchical Navigable Small World** : un **graphe multi-niveaux** où chaque vecteur est relié à ses voisins proches. Les niveaux supérieurs, clairsemés, servent d'**autoroutes** ; la recherche descend de niveau en niveau en suivant **gloutonnement** le voisin le plus proche. Rappel élevé et latence faible, mais **gourmand en mémoire** (vecteurs + graphe en RAM).

---

Quels paramètres de HNSW règlent le compromis rappel / coût ? <!--anki:76525d40386e2f777647-->
?
- **M** : nombre de liens par nœud — plus de rappel, plus de mémoire.
- **ef_construction** : largeur de recherche à la construction — meilleur graphe, construction plus lente.
- **ef_search** (ou ef) : largeur de recherche à la requête — **le levier principal** au runtime : plus de rappel, plus de latence.

---

Comment fonctionne un index IVF ? <!--anki:72553a316c3773444028-->
?
**Inverted File** : on partitionne l'espace en **k clusters** (k-means). À la requête, on ne cherche que dans les **nprobe clusters** les plus proches. Moins de mémoire que HNSW et construction rapide ; rappel réglé par **nprobe**, qui chute si un voisin tombe dans un cluster non visité.

Augmenter **nprobe** explore davantage de listes : le rappel peut monter, mais le travail de recherche aussi. Si les données changent fortement, les centroïdes appris peuvent mal représenter le nouvel espace. Comparer les voisins trouvés à une recherche exacte sur un échantillon et mesurer latence et rappel ensemble, avec les mêmes filtres métier.

---

Qu'est-ce que la Product Quantization (PQ) ? <!--anki:484430554d377855643f-->
?
Une compression : chaque vecteur est découpé en **m sous-vecteurs**, chacun remplacé par l'**indice du centroïde** le plus proche dans un petit dictionnaire. Un vecteur de 768 floats (3 Ko) peut tenir en **quelques dizaines d'octets**. Les distances deviennent **approximatives** → on combine souvent avec un **re-scoring** sur les vecteurs complets. IVF-PQ est le classique des très gros corpus.

---

Quelles autres techniques de compression de vecteurs existent ? <!--anki:7328294347582a3e372a-->
?
- **Scalar quantization** : float32 → **int8** (÷4), perte minime.
- **Binary quantization** : 1 bit par dimension (÷32), recherche par **distance de Hamming** très rapide, puis **re-scoring** des meilleurs candidats en précision pleine.
- **Troncature** des embeddings [[133-embeddings-representations|Matryoshka]].

Les facteurs de réduction portent sur les **valeurs des vecteurs**, pas sur les métadonnées, le graphe ou une copie conservée pour le reclassement. La perte de qualité dépend du modèle et des données ; elle n'est pas toujours minime. Évaluer chaque compression avec une référence exacte et vérifier le coût du re-scoring des candidats.

---

Qu'est-ce que DiskANN et quand l'utiliser ? <!--anki:242e5d653b58264e72-->
?
Un index en graphe (famille **Vamana**) conçu pour vivre **sur SSD**, avec seulement des vecteurs compressés en RAM. Il permet de servir des **milliards de vecteurs** sur une machine à coût raisonnable, là où HNSW exigerait une RAM énorme.

Le compromis déplace une partie de la contrainte de la RAM vers les **lectures SSD et leur latence**. Il faut encore de la mémoire pour les structures chaudes et une stratégie de cache. Tester une charge froide puis concurrente : un bon résultat sur quelques requêtes ne garantit pas le même p99 lorsque beaucoup de recherches sollicitent le disque.

---

Pourquoi le filtrage par métadonnées est-il difficile avec un index ANN ? <!--anki:726234383c2e6259602a-->
?
- **Post-filtrage** (chercher top-k puis filtrer) : si le filtre est **sélectif**, il peut ne rester **aucun résultat**.
- **Pré-filtrage** (restreindre puis chercher) : casse la navigation du graphe HNSW et peut retomber en brute force.

Les bases modernes font du **filtrage intégré** à la traversée ; à tester avec des filtres **très sélectifs** (ACL, tenant) qui sont le cas critique ([[22-rag-avance|filtrage et ACL]]).

---

Comment mesurer la qualité d'un index ANN ? <!--anki:632f2b3f4d4d244e3332-->
?
Par le **recall@k de l'index** par rapport à la **recherche exacte** sur un échantillon de requêtes (quelle part des vrais k plus proches voisins est retrouvée), mis en regard de la **latence p95** et du **QPS**.

---

Base vectorielle dédiée ou extension d'une base existante ? <!--anki:68674461647c78563b3c-->
?
- **Extension** (pgvector dans PostgreSQL, OpenSearch/Elasticsearch) : **une seule base**, transactions, jointures, ACL et BM25 déjà là — suffisant jusqu'à des **dizaines de millions** de vecteurs.
- **Base dédiée** (Qdrant, Milvus, Weaviate, Pinecone…) : meilleures performances à grande échelle, quantization et filtrage avancés, multi-tenant.

Le choix par défaut raisonnable : **commencer avec ce qu'on opère déjà**.

---

Quels sujets d'exploitation une base vectorielle pose-t-elle ? <!--anki:75695a595f4272337c3e-->
?
- **Mises à jour et suppressions** (les graphes HNSW gèrent mal les suppressions massives → reconstruction).
- **Ré-indexation** lors d'un changement de modèle d'embedding.
- **Multi-tenant** : une collection par client ou un filtre de tenant.
- **Sauvegardes**, réplication, **mémoire** (dimensionnement RAM), et **droit à l'effacement** ([[154-rgpd-llm|RGPD]]).

Vérifier la **fraîcheur observable** après insertion, mise à jour et suppression, y compris dans les réplicas et caches. Une sauvegarde doit pouvoir restaurer index et métadonnées compatibles. Les stratégies de suppression varient selon l'implémentation ; tester accumulation de suppressions et reconstruction au lieu de supposer qu'un index fonctionnel restera performant sans maintenance.

---

Calcul : estimer la mémoire de 10 millions de vecteurs à 768 dimensions float32 et d’un graphe HNSW simplifié de 32 liens de 4 octets par vecteur. Quelle part varie si les vecteurs passent en int8 ? <!--anki:4b382a2f6a796f4b7621-->
?
Avec les hypothèses simplifiées de l'énoncé, en **Go décimaux** :
```text
vecteurs float32 = 10 000 000 × 768 × 4 = 30,72 Go
graphe = 10 000 000 × 32 × 4 = 1,28 Go
total simplifié float32 = 32,00 Go
vecteurs int8 = 10 000 000 × 768 × 1 = 7,68 Go
total simplifié int8 = 7,68 + 1,28 = 8,96 Go
```
Seule la part des vecteurs est divisée par quatre : le total diminue d'environ **3,57 fois**. Ajouter métadonnées, structures d'allocation, niveaux du graphe, buffers et éventuelle copie pleine précision. Ce calcul donne un plancher pédagogique, pas la RAM exacte d'une implémentation HNSW.

---

À ne pas confondre : le rappel d'un index ANN et le rappel du retrieval ? <!--anki:4e435f743a47466c2161-->
?
- **Rappel de l'index ANN** : la part des **vrais plus proches voisins** (au sens de la recherche exacte) que l'index retrouve. Il mesure **l'approximation** de l'index
- **Rappel du retrieval** (recall@k d'un RAG) : la part des **documents pertinents** pour la question qui sont remontés. Il mesure la **qualité de bout en bout** : chunking, modèle d'embedding, requête et index

Un index à 99 % de rappel ANN peut donner un mauvais RAG si l'**embedding** ne rapproche pas les bons passages. On règle `ef_search` avec le premier, on juge le système avec le second ([[96-evals-rag-agents|evals RAG]]).

---

## Mises en situation

Mise en situation : ton RAG multi-tenant renvoie parfois zéro résultat pour un client, alors que ses documents existent bien dans l'index. Quelle cause suspectes-tu ? <!--anki:4b34572d3f6c5d796e43-->
?
1. **Le filtrage par métadonnées** combiné à l'index ANN : en post-filtrage, le top-k peut ne contenir aucun document du client
2. **Tester avec des filtres très sélectifs**, qui sont le cas critique en multi-tenant
3. **Choisir la bonne stratégie** : filtrage intégré à la traversée, ou collection par client
4. **Ne jamais relâcher le filtre** pour « avoir des résultats » : ce serait une fuite entre clients ([[22-rag-avance|ACL]])
5. **Surveiller** le taux de requêtes sans résultat, par client

**Piège** : augmenter le top-k pour compenser, ce qui masque le problème sans le corriger.

---

Mise en situation : ton équipe hésite entre pgvector dans la base PostgreSQL existante et une base vectorielle dédiée. Comment tranches-tu ? <!--anki:41243453456f7523645d-->
?
1. **Estimer la volumétrie** : jusqu'à quelques dizaines de millions de vecteurs, l'extension suffit souvent
2. **Compter les avantages de l'existant** : une seule base à opérer, transactions, jointures, ACL et recherche lexicale déjà disponibles
3. **Regarder les besoins avancés** : quantization, filtrage performant, multi-tenant à grande échelle, mises à jour massives
4. **Tester sur ton corpus** : recall@k de l'index contre recherche exacte, latence p95 et QPS
5. **Ne pas oublier l'exploitation** : sauvegardes, ré-indexation, mémoire, effacement des données

**Piège** : choisir une base dédiée pour 200 000 vecteurs, et ajouter un composant à opérer sans bénéfice.

---

## Connexions
- [[133-embeddings-representations|Embeddings & représentations]] — ce qu'on indexe
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — pipeline d'ingestion et de requête
- [[22-rag-avance|RAG avancé]] — hybride, filtres, ACL
- [[96-evals-rag-agents|Evals de RAG]] — rappel du retrieval
- [[68-quantization|Quantization]] — les mêmes idées appliquées aux poids
- [[00-moc-ai-engineering|MOC AI Engineering]]
