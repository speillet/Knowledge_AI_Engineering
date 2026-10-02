# Embeddings & représentations — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #embeddings #rag

Qu'est-ce qu'un modèle d'embedding ?
?
<!--anki:6b565249636a404c3878-->
Un modèle (souvent un **encodeur** type BERT, ou un LLM adapté) qui transforme un texte en **vecteur dense de taille fixe** (384 à 4 096 dimensions) tel que des textes **sémantiquement proches** aient des vecteurs **proches**. C'est la base de la recherche sémantique, du [[21-rag-fondamentaux|RAG]], du clustering et de la déduplication.

---

Comment un modèle d'embedding est-il entraîné ?
?
<!--anki:756445307677664a4864-->
Par **apprentissage contrastif** : on rapproche les paires **positives** (question ↔ passage qui y répond, paraphrases) et on éloigne les **négatives**, en général les autres exemples du batch (**in-batch negatives**) plus des **hard negatives** (passages proches mais faux). La loss typique est **InfoNCE**.

---

Quelles mesures de similarité utiliser ?
?
<!--anki:716c647e42323e3f283e-->
- **Cosinus** : angle entre vecteurs, insensible à la norme.
- **Produit scalaire** : identique au cosinus si les vecteurs sont **normalisés** (le cas le plus courant, et le plus rapide).
- **Distance euclidienne (L2)** : équivalente en classement pour des vecteurs normalisés.

Il faut utiliser **la mesure pour laquelle le modèle a été entraîné**.

---

À ne pas confondre : bi-encoder et cross-encoder ?
?
<!--anki:4c4b5539596c715d5251-->
- **Bi-encoder** : encode requête et document **séparément** → les documents sont indexés à l'avance, la recherche est rapide. C'est le modèle d'embedding.
- **Cross-encoder** : lit **requête et document ensemble** → bien plus précis mais un passage par paire, donc réservé au **reranking** de quelques dizaines de candidats ([[22-rag-avance|reranking]]).

---

Qu'est-ce que le late interaction (ColBERT) ?
?
<!--anki:4b736c5829233b5b7e76-->
Un compromis : on garde **un vecteur par token** du document, et le score est la somme, pour chaque token de la requête, de sa **similarité maximale** avec un token du document (**MaxSim**). Plus précis qu'un vecteur unique, pré-calculable, mais **bien plus lourd** à stocker.

---

Qu'est-ce que les embeddings Matryoshka ?
?
<!--anki:4a757a636a5735704d36-->
Des embeddings entraînés pour que **les premières dimensions** portent l'essentiel de l'information : on peut **tronquer** le vecteur (ex. 3 072 → 256 dimensions) avec une perte faible. Utile pour **réduire le stockage** et faire une **recherche en deux temps** (petit vecteur pour présélectionner, grand pour reclasser).

---

Pourquoi certains modèles demandent-ils un préfixe (instruction) ?
?
<!--anki:753d3929536a2937733e-->
Les modèles **asymétriques** distinguent **requête** et **document** (ex. préfixes « query: » et « passage: », ou une instruction de tâche). Oublier le préfixe, ou mettre le mauvais, **dégrade nettement le rappel** : la documentation du modèle fait foi.

---

Comment choisir un modèle d'embedding ?
?
<!--anki:4f7c267c5168495d2b74-->
- Le leaderboard **MTEB** pour un pré-tri, **filtré sur sa langue et sa tâche** (retrieval, pas classification).
- **Test sur son propre jeu** (recall@k), seul critère fiable.
- **Longueur max** d'entrée, **dimension** (coût de stockage), **multilingue**, **licence**, **API ou self-hosted**, latence.

---

Quand fine-tuner un modèle d'embedding ?
?
<!--anki:4a67347976475d723761-->
Quand le domaine a un **vocabulaire spécifique** (juridique, médical, code interne) et que les modèles génériques ratent des correspondances évidentes pour un expert. Avec **quelques milliers de paires** (question, passage), souvent **générées synthétiquement** puis filtrées, et des hard negatives, les gains de recall sont fréquemment de **plusieurs points**.

---

Que se passe-t-il quand on change de modèle d'embedding ?
?
<!--anki:467e29694e6252774e30-->
Les vecteurs de deux modèles **ne sont pas comparables** : il faut **ré-encoder tout le corpus** et reconstruire l'index. D'où l'intérêt de **versionner** le modèle d'embedding avec l'index, et de prévoir la **ré-indexation** (coût, temps, double index pendant la bascule).

---

Qu'est-ce que les embeddings sparse (SPLADE) ?
?
<!--anki:6d6f7272495a6b473372-->
Des représentations **creuses** sur le vocabulaire, apprises par un modèle : chaque dimension correspond à un **terme**, avec expansion vers des termes voisins. Elles combinent **l'exactitude lexicale** de BM25 (noms propres, codes, références) avec une part de **sémantique**, et se combinent bien avec les embeddings denses en **recherche hybride**.

---

Quelles sont les limites des embeddings denses ?
?
<!--anki:4741334661243f797b34-->
- Mauvais sur les **correspondances exactes** (identifiants, codes produits, négations).
- Un seul vecteur **résume mal** un long document → importance du [[21-rag-fondamentaux|chunking]].
- Sensibles au **décalage de domaine**.
- La proximité sémantique **n'est pas la pertinence** : « symptômes de la grippe » et « traitement de la grippe » sont proches.

---

## Mises en situation

Mise en situation : ton RAG juridique rate des correspondances qu'un juriste trouve évidentes, malgré un modèle d'embedding bien classé. Que fais-tu ?
?
<!--anki:4144587d52417c345f3f-->
1. **Vérifier le classement** : un bon score sur un leaderboard généraliste ne dit rien de ton domaine ni de ta langue
2. **Mesurer sur tes données** : recall@k sur un jeu de questions réelles, seul critère qui compte
3. **Vérifier les préfixes** : certains modèles attendent une instruction différente pour la requête et pour le document
4. **Ajouter le lexical** : la recherche hybride récupère les références et les articles de loi ([[22-rag-avance|hybride]])
5. **Envisager un fine-tuning** : quelques milliers de paires question-passage du domaine, avec des négatifs difficiles

**Piège** : choisir un modèle d'embedding sur son score global, sans filtrer par langue et par tâche.

---

Mise en situation : ton corpus de 20 millions de chunks coûte cher en stockage vectoriel, et la recherche ralentit. Quelles options avant d'acheter des serveurs ?
?
<!--anki:7878497b7b7e37685a4e-->
1. **Réduire la dimension** : un modèle Matryoshka permet de tronquer les vecteurs avec une perte faible
2. **Compresser** : quantization scalaire en int8, voire binaire avec re-scoring des meilleurs candidats ([[134-recherche-vectorielle-ann|index ANN]])
3. **Recherche en deux temps** : petit vecteur pour présélectionner, vecteur complet ou reranker pour classer
4. **Revoir le chunking** : des chunks trop petits multiplient inutilement le nombre de vecteurs
5. **Mesurer l'impact** sur le recall à chaque étape, pas seulement le gain de stockage

**Piège** : compresser les vecteurs sans jamais vérifier ce que le rappel devient.

---

## Connexions
- [[134-recherche-vectorielle-ann|Recherche vectorielle & index ANN]] — stocker et chercher les vecteurs
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — l'usage principal
- [[22-rag-avance|RAG avancé]] — recherche hybride et reranking
- [[131-transformer-architecture|Architecture Transformer]] — encodeurs et décodeurs
- [[96-evals-rag-agents|Evals de RAG]] — mesurer le rappel
- [[123-caching-agressif|Caching agressif]] — cache d'embeddings
- [[161-modeles-vision-langage|Modèles vision-langage]] — images et écrans en entrée
- [[162-document-parsing|Parsing de documents]] — transformer PDF et scans en texte structuré
- [[25-chunking-contextual-retrieval|Chunking avancé]] — rendre chaque chunk trouvable
- [[68-quantization|Quantization]] — réduire la précision pour gagner mémoire et vitesse
- [[00-moc-ai-engineering|MOC AI Engineering]]
