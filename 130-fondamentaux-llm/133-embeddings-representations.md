# Embeddings & représentations — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #embeddings #rag
<!-- summary: apprentissage contrastif, similarités, bi-encoder ou cross-encoder, ColBERT, Matryoshka, préfixes, choix (MTEB), fine-tuning d'embeddings, changement de modèle, SPLADE, limites, calcul du lien entre cosinus et distance L2, norme des vecteurs, négatifs difficiles. -->


Qu'est-ce qu'un modèle d'embedding ? <!--anki:6b565249636a404c3878-->
?
Un modèle (souvent un **encodeur** type BERT, ou un LLM adapté) qui transforme un texte en **vecteur dense de taille fixe** (384 à 4 096 dimensions) tel que des textes **sémantiquement proches** aient des vecteurs **proches**. C'est la base de la recherche sémantique, du [[21-rag-fondamentaux|RAG]], du clustering et de la déduplication.

Ces dimensions sont des exemples, pas des limites universelles. Deux modèles produisant chacun 1 024 dimensions n'ont pas nécessairement un espace compatible : après migration, réencoder documents et requêtes avec le couple prévu, puis mesurer le rappel.

---

Comment un modèle d'embedding est-il entraîné ? <!--anki:756445307677664a4864-->
?
Par **apprentissage contrastif** : on rapproche les paires **positives** (question ↔ passage qui y répond, paraphrases) et on éloigne les **négatives**, en général les autres exemples du batch (**in-batch negatives**) plus des **hard negatives** (passages proches mais faux). La loss typique est **InfoNCE**.

Un bon négatif est plausible mais ne répond pas à la question, par exemple une procédure concernant un autre produit. Un passage réellement pertinent traité comme négatif envoie un signal contradictoire. Soigner les paires et les faux négatifs ; optimiser uniquement la loss d'entraînement ne suffit pas à garantir un meilleur retrieval sur de nouvelles questions.

---

Quelles mesures de similarité utiliser entre embeddings ? <!--anki:716c647e42323e3f283e-->
?
Le **cosinus** compare les directions, le **produit scalaire** dépend aussi des normes et la **distance euclidienne** mesure l'écart géométrique. Utiliser la mesure et la normalisation recommandées pour le modèle et vérifier leur prise en charge par l'index.

Pour des vecteurs de norme 1, produit scalaire et cosinus coïncident ; la distance L2 donne le même classement par la relation `L2² = 2 − 2 × cosinus`. Sans normalisation, cette équivalence disparaît. Le coût de calcul dépend du moteur et des données : aucune mesure n'est universellement la plus rapide ni un score de confiance métier.

---

À ne pas confondre : bi-encoder et cross-encoder ? <!--anki:4c4b5539596c715d5251-->
?
- **Bi-encoder** : encode requête et document **séparément** → les documents sont indexés à l'avance, la recherche est rapide. C'est le modèle d'embedding.
- **Cross-encoder** : lit **requête et document ensemble** → bien plus précis mais un passage par paire, donc réservé au **reranking** de quelques dizaines de candidats ([[22-rag-avance|reranking]]).

Le gain de précision doit être mesuré sur le domaine. Le cross-encoder ne peut pas retrouver une preuve absente des candidats : si le bon document n'entre jamais dans le top-50, améliorer seulement le reranker ne corrigera pas cet échec.

---

Qu'est-ce que le late interaction (ColBERT) ? <!--anki:4b736c5829233b5b7e76-->
?
Un compromis : on garde **un vecteur par token** du document, et le score est la somme, pour chaque token de la requête, de sa **similarité maximale** avec un token du document (**MaxSim**). Plus précis qu'un vecteur unique, pré-calculable, mais **bien plus lourd** à stocker.

Cela préserve plusieurs indices d'un document au lieu de tout condenser dans un seul vecteur. Par exemple, deux mots précis d'une question peuvent correspondre à deux endroits distincts du passage. Les vecteurs documentaires sont calculés à l'avance, mais leur agrégation dépend de la requête ; prévoir le coût de stockage et de recherche des représentations multiples.

---

Qu'est-ce que les embeddings Matryoshka ? <!--anki:4a757a636a5735704d36-->
?
Des embeddings entraînés pour que **les premières dimensions** portent l'essentiel de l'information : on peut **tronquer** le vecteur (ex. 3 072 → 256 dimensions) avec une perte faible. Utile pour **réduire le stockage** et faire une **recherche en deux temps** (petit vecteur pour présélectionner, grand pour reclasser).

La propriété doit être **apprise par le modèle** : couper arbitrairement un embedding ordinaire n'offre pas la même garantie. Après troncature, appliquer la normalisation attendue et mesurer le rappel à chaque dimension candidate. Une présélection trop courte peut perdre le bon document avant le reclassement, même si le vecteur complet serait capable de le retrouver.

---

Pourquoi certains modèles demandent-ils un préfixe (instruction) ? <!--anki:753d3929536a2937733e-->
?
Les modèles **asymétriques** distinguent **requête** et **document** (ex. préfixes « query: » et « passage: », ou une instruction de tâche). Oublier le préfixe, ou mettre le mauvais, **dégrade nettement le rappel** : la documentation du modèle fait foi.

Le préfixe indique au modèle le **rôle du texte à encoder**, conformément à son entraînement. Par exemple, une question courte et le paragraphe qui y répond n'ont pas la même forme, mais doivent devenir proches. Versionner cette préparation avec l'index et éviter de comparer un nouveau préfixe de requête à un corpus encodé selon une convention incompatible.

---

Comment choisir un modèle d'embedding ? <!--anki:4f7c267c5168495d2b74-->
?
- Le leaderboard **MTEB** pour un pré-tri, **filtré sur sa langue et sa tâche** (retrieval, pas classification).
- **Test sur son propre jeu** (recall@k), seul critère fiable.
- **Longueur max** d'entrée, **dimension** (coût de stockage), **multilingue**, **licence**, **API ou self-hosted**, latence.

Conserver corpus, questions et méthode d'indexation comparables pour isoler l'effet du modèle. Examiner aussi les segments difficiles : références exactes, requêtes courtes et documents longs. Un bon score moyen peut masquer un échec métier récurrent. Le choix final combine pertinence et contraintes d'exploitation ; gagner un point de rappel peut coûter beaucoup de mémoire ou de latence.

---

Quand fine-tuner un modèle d'embedding ? <!--anki:4a67347976475d723761-->
?
Quand le domaine a un **vocabulaire spécifique** (juridique, médical, code interne) et que les modèles génériques ratent des correspondances évidentes pour un expert. Avec **quelques milliers de paires** (question, passage), souvent **générées synthétiquement** puis filtrées, et des hard negatives, les gains de recall sont fréquemment de **plusieurs points**.

Avant l'entraînement, vérifier parsing, chunking, préfixes et qualité des labels : un défaut d'ingestion ne se corrige pas forcément dans les poids. Séparer entraînement et test par familles de documents pour éviter les quasi-doublons. Le volume nécessaire et le gain ne sont pas garantis ; comparer au modèle initial et surveiller les régressions hors du domaine spécialisé.

---

Que se passe-t-il quand on change de modèle d'embedding ? <!--anki:467e29694e6252774e30-->
?
Les vecteurs de deux modèles **ne sont pas comparables** : il faut **ré-encoder tout le corpus** et reconstruire l'index. D'où l'intérêt de **versionner** le modèle d'embedding avec l'index, et de prévoir la **ré-indexation** (coût, temps, double index pendant la bascule).

Deux vecteurs de même dimension peuvent représenter des **espaces différents** ; la taille identique ne suffit pas à les mélanger. Pendant la migration, router chaque requête vers l'encodeur correspondant à son index, tester le rappel et conserver un retour arrière. Inclure aussi prétraitement, préfixes et normalisation dans la version, car ils influencent les représentations.

---

Qu'est-ce que les embeddings sparse (SPLADE) ? <!--anki:6d6f7272495a6b473372-->
?
Des représentations **creuses** sur le vocabulaire, apprises par un modèle : chaque dimension correspond à un **terme**, avec expansion vers des termes voisins. Elles combinent **l'exactitude lexicale** de BM25 (noms propres, codes, références) avec une part de **sémantique**, et se combinent bien avec les embeddings denses en **recherche hybride**.

La représentation attribue des poids à un petit nombre de dimensions lexicales et peut activer des termes absents du texte initial. Elle s'exploite avec un index inversé adapté. Cette expansion rapproche certaines reformulations, mais peut introduire du bruit ; mesurer l'effet sur références rares et vocabulaire métier au lieu d'assimiler toute expansion à une amélioration.

---

Quelles sont les limites des embeddings denses ? <!--anki:4741334661243f797b34-->
?
Un vecteur dense compresse le texte : il peut perdre détails, contraintes ou distinctions rares. La **proximité sémantique n'est ni une égalité ni une preuve**.

Exemple : `AB-120` et `AB-102` peuvent sembler proches tout en désignant deux pièces incompatibles ; « autorisé » et « non autorisé » partagent aussi beaucoup de contexte. Combiner recherche lexicale, filtres exacts et reranking selon la tâche.

Un long document dilue parfois un fait local : utiliser le [[21-rag-fondamentaux|chunking]]. Tester négations, identifiants et vocabulaire métier sur ses données ; un bon score général ne garantit pas le rappel dans un domaine différent.

---

Calcul : pour deux vecteurs normalisés de cosinus 0,8, quelle distance euclidienne obtient-on et pourquoi le classement peut-il être équivalent ? <!--anki:6465313239333534643634613465343862643836633239383463356235386337-->
?
Pour deux vecteurs de norme 1, `||u − v||² = 2 − 2 × cos(u,v)`. Avec un cosinus de 0,8, la distance vaut `√0,4 ≈ 0,632`.

Minimiser cette distance revient donc à maximiser le cosinus **si tous les vecteurs sont effectivement normalisés**. Sans cette hypothèse, les normes influencent le produit scalaire et la distance, et les classements peuvent changer. Vérifier la normalisation à l'indexation et à la requête ; un seuil de similarité n'est pas directement un seuil de probabilité de pertinence.

---

Pourquoi le produit scalaire peut-il classer différemment deux embeddings que le cosinus ? <!--anki:6264303934396465653338323464663439623030613138333932616361373766-->
?
Le produit scalaire dépend **de l'angle et des normes** ; le cosinus ne garde que l'angle. Un vecteur de grande norme peut obtenir un score élevé sans être le plus proche en direction.

Lorsque tous les vecteurs sont normalisés à norme un, les deux classements coïncident. Vérifier ce que le modèle et l'index attendent avant de normaliser : la norme peut être porteuse d'information dans certains entraînements.

---

Pourquoi les faux négatifs sont-ils dangereux dans l'entraînement contrastif d'embeddings ? <!--anki:3263333165656165343837643466623462383164623438393332303235326337-->
?
Un passage étiqueté négatif peut être **une autre réponse pertinente**. L'objectif entraîne alors le modèle à éloigner des éléments qui devraient rester proches.

Contrôler les négatifs difficiles, dédupliquer et accepter plusieurs positifs quand la tâche le permet. Les négatifs aléatoires sont parfois trop faciles ; les négatifs proches demandent davantage de validation. Mesurer le retrieval sur des questions et sources indépendantes de la construction des paires.

---

## Mises en situation

Mise en situation : ton RAG juridique rate des correspondances qu'un juriste trouve évidentes, malgré un modèle d'embedding bien classé. Que fais-tu ? <!--anki:4144587d52417c345f3f-->
?
1. **Vérifier le classement** : un bon score sur un leaderboard généraliste ne dit rien de ton domaine ni de ta langue
2. **Mesurer sur tes données** : recall@k sur un jeu de questions réelles, seul critère qui compte
3. **Vérifier les préfixes** : certains modèles attendent une instruction différente pour la requête et pour le document
4. **Ajouter le lexical** : la recherche hybride récupère les références et les articles de loi ([[22-rag-avance|hybride]])
5. **Envisager un fine-tuning** : quelques milliers de paires question-passage du domaine, avec des négatifs difficiles

**Piège** : choisir un modèle d'embedding sur son score global, sans filtrer par langue et par tâche.

---

Mise en situation : ton corpus de 20 millions de chunks coûte cher en stockage vectoriel, et la recherche ralentit. Quelles options avant d'acheter des serveurs ? <!--anki:7878497b7b7e37685a4e-->
?
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
- [[174-recommandation-ranking|Recommandation & learning to rank]] — représentations pour rechercher les candidats
- [[00-moc-ai-engineering|MOC AI Engineering]]
