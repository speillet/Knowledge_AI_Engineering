# Parsing de documents (PDF, OCR, layout) — Flashcards
Tags: #flashcards #ai-engineering #multimodal #document-parsing #rag
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: PDF natif ou scanné, analyse de layout, outils (Docling, Unstructured, services cloud, VLM), tableaux, figures, ColPali, chunking structurel, évaluation, exploitation, unités et en-têtes des tableaux. -->


Pourquoi le parsing de documents est-il souvent le goulot d'un RAG d'entreprise ? <!--anki:7038666a4c6a61724345-->
?
Parce que les documents réels sont des **PDF scannés, tableaux, slides, formulaires, colonnes multiples, en-têtes et pieds de page**. Un mauvais parsing (tableau aplati, colonnes mélangées, texte manquant) produit des chunks **inexploitables** : aucun modèle ni reranker ne rattrape une information **perdue à l'ingestion** ([[21-rag-fondamentaux|RAG]]).

Exemple : un contrat scanné ingéré sans OCR produit des chunks vides ; une question sur sa clause de résiliation ne peut plus trouver de preuve, quel que soit le modèle.

---

À ne pas confondre : PDF natif et PDF scanné ? <!--anki:4c4f575870682a745132-->
?
Un **PDF natif** contient généralement du texte extractible ; un **scan** représente la page par une image et peut déjà inclure une couche OCR. La structure logique et l'ordre de lecture ne sont pas garantis dans les deux cas.

Détecter page par page le texte exploitable, les zones image et la qualité de l'extraction. Un seuil de 20 caractères n'est qu'une heuristique : une page presque vide peut être correcte, et une couche OCR longue peut être corrompue. Appliquer l'OCR aux zones nécessaires, puis contrôler texte, unités et mise en page plutôt que compter seulement les caractères.

---

Qu'est-ce que l'analyse de layout ? <!--anki:752b69687c7e7867775a-->
?
Détecter les **zones** d'une page — titres, paragraphes, tableaux, figures, légendes, en-têtes, notes — et l'**ordre de lecture**. Elle permet de reconstruire la **structure** (hiérarchie des sections) et de traiter chaque zone avec le bon outil (OCR, extraction de tableau, description de figure).

Exemple : sur une page à deux colonnes, une extraction ligne par ligne mélange les deux textes ; l'ordre de lecture remet la colonne de gauche avant celle de droite. Les en-têtes et pieds de page répétés sont aussi repérés et retirés : sinon, ils polluent chaque chunk et faussent la recherche.

---

Quel outil de parsing selon le document : PDF natif simple, mise en page complexe, scans en volume, données confidentielles ? <!--anki:3963656532376466656136373464373061363131353338666435663437353963-->
?
- **PDF natif simple** : extraction textuelle, par exemple pdfplumber ou PyMuPDF, après vérification de licence.
- **Mise en page complexe** : analyse de layout, par exemple Docling ou Unstructured.
- **Scans en volume** : OCR local ou service documentaire, éventuellement VLM pour les cas difficiles.
- **Données confinées** : pipeline auto-hébergé dont les appels réseau sont maîtrisés.

Tester sur les erreurs qui comptent : un tableau lisible en Markdown peut associer le montant à la mauvaise ligne. Mesurer champs, ordre de lecture et provenance, puis coût et débit. Le cloud n'est pas obligatoire pour le volume ; l'open source ne garantit ni confidentialité ni exploitation gratuite.

---

Comment traiter les tableaux lors du parsing de documents ? <!--anki:4b3d5068593763564574-->
?
Les extraire en **structure** (markdown, HTML ou JSON), pas en texte aplati. Pour le RAG : garder le tableau **entier** dans un chunk avec son **titre et ses en-têtes de colonnes** ; pour un grand tableau, répéter les en-têtes dans chaque morceau.
```text
Tableau 3 — Tarifs 2026
| Offre    | Prix mensuel | Engagement |
|----------|--------------|------------|
| Standard | 12 €         | aucun      |
```
On peut aussi générer un **résumé textuel** du tableau pour l'embedding et fournir le tableau complet au LLM.

Conserver aussi unités, notes et coordonnées source. Vérifier cellules fusionnées et ruptures de page : un nombre correctement reconnu peut appartenir à la mauvaise ligne ou changer de sens si son unité disparaît.

---

Comment traiter les images et graphiques d'un document ? <!--anki:62734f492d5f7a4c7026-->
?
Les faire **décrire par un VLM** (description + données lisibles du graphique) et indexer cette description, en gardant un **lien vers l'image** pour pouvoir la fournir au modèle au moment de la réponse. Alternative : **retrieval multimodal** direct sur les images de pages ([[161-modeles-vision-langage|VLM]]).

Exemple : un graphique de chiffre d'affaires décrit comme « courbe en hausse » ne répond pas à « quel CA au troisième trimestre ? ». Demander au VLM les valeurs lisibles sous forme de tableau, avec une mention d'incertitude, et garder la page source pour vérification. Chaque figure coûte un appel VLM à l'ingestion : filtrer d'abord logos et éléments décoratifs.

---

Qu'est-ce que le retrieval sur images de pages (type ColPali) ? <!--anki:692e4d5d2665634c4768-->
?
On **n'extrait pas le texte** : chaque page est encodée **comme image** par un VLM en embeddings multi-vecteurs (late interaction), et la requête texte est comparée directement à ces pages. Robuste aux mises en page complexes et aux graphiques, au prix d'un **stockage** plus lourd et d'une réponse générée par un **VLM**.

Ordre de grandeur : ColPali produit environ un millier de vecteurs de 128 dimensions par page, soit quelques centaines de Ko, contre quelques Ko pour un embedding unique de passage.

---

Comment chunker en respectant la structure ? <!--anki:49576b5a755e527e6934-->
?
Découper **selon la hiérarchie** (sections, sous-sections) plutôt qu'à taille fixe, **ne jamais couper** un tableau ou une liste au milieu, et ajouter à chaque chunk son **contexte** : titre du document, chemin des titres (« Contrat > Article 5 > Résiliation »), date, source. Ce contexte améliore beaucoup le retrieval ([[22-rag-avance|RAG avancé]]).

Docling, par exemple, fournit un `HierarchicalChunker` qui suit la structure détectée, et un `HybridChunker` qui la combine à une limite de tokens.

---

Comment évaluer une chaîne de parsing ? <!--anki:7750667d2928215a777b-->
?
- Sur un **échantillon représentatif** de documents (y compris les pires : scans, tableaux complexes).
- Métriques : **taux d'erreur de caractères** (OCR), exactitude des **cellules** de tableau, ordre de lecture, **champs** extraits corrects.
- Et surtout l'effet **en aval** : recall du retrieval et qualité des réponses du RAG.

Exemple : 12 erreurs sur 1 000 caractères de référence donnent un taux d'erreur de 1,2 % ; une seule de ces erreurs dans un IBAN suffit pourtant à rendre le champ inutilisable.

---

Quels pièges d'exploitation dans une chaîne d'ingestion ? <!--anki:504a6b3c446331367152-->
?
- **Coût et durée** : un VLM ou un service cloud sur des millions de pages coûte cher → traitement **batch**, cache par hash de fichier.
- **Échecs silencieux** : pages vides, encodages cassés → contrôles de qualité automatiques, par exemple alerte sous 200 caractères ou sous 50 % de caractères alphanumériques sur une page de texte.
- **Mises à jour** : ré-ingestion incrémentale et suppression des anciennes versions.
- **Confidentialité** des documents envoyés à un service externe ([[152-pii-confidentialite|PII]]).

---

Pourquoi conserver unités, en-têtes et notes lors de l'extraction d'un tableau de document ? <!--anki:6233393965666636343566303439663138303839333561343838623234376662-->
?
Une **cellule isolée** perd souvent son sens : `125` peut désigner euros, milliers d'euros ou pourcentage selon l'en-tête et les notes.

Reconstruire lignes, colonnes et cellules fusionnées avec leur contexte, puis conserver page et coordonnées pour vérification. Tester tableaux sur plusieurs pages, parenthèses négatives et séparateurs décimaux. Vérifier des totaux connus sans supposer que toutes les lignes s'additionnent. Un texte OCR exact au caractère près peut produire une donnée métier fausse si l'unité ou le bon en-tête a été perdu.

---

## Mises en situation

Mise en situation : ton RAG répond mal sur les documents contenant des tableaux, alors que le retrieval semble correct. Où cherches-tu ? <!--anki:706d673e5b7368796370-->
?
1. **Regarder les chunks eux-mêmes** : un tableau aplati en texte perd les correspondances entre lignes et colonnes
2. **Extraire en structure** (markdown, HTML ou JSON) plutôt qu'en texte brut
3. **Garder le tableau entier** dans un chunk, avec son titre et ses en-têtes, et répéter les en-têtes si on doit le découper
4. **Enrichir l'index** : un résumé textuel du tableau pour l'embedding, le tableau complet fourni au modèle
5. **Mesurer en aval** : recall et exactitude des réponses sur les questions qui portent sur des tableaux

**Piège** : chercher la cause dans le modèle de génération alors que l'information a été perdue à l'ingestion.

---

Mise en situation : tu dois ingérer 500 000 PDF, dont beaucoup de scans, avec un budget limité. Comment conçois-tu la chaîne ? <!--anki:6d7e7b6f2367455a4132-->
?
1. **Trier par type** : PDF natifs traités par extraction directe, scans envoyés à l'OCR, cas complexes à un VLM
2. **Traiter en batch** et **cacher par empreinte de fichier**, pour ne jamais retraiter deux fois le même document
3. **Contrôles qualité automatiques** : pages vides, ratio de caractères valides, longueur anormale, pour détecter les échecs silencieux
4. **Évaluer la chaîne** sur un échantillon représentatif, en incluant les pires documents
5. **Vérifier la confidentialité** avant d'envoyer des documents à un service externe ([[152-pii-confidentialite|PII]])

**Piège** : envoyer les 500 000 documents au parseur le plus coûteux, alors que la majorité se traite avec une simple extraction.

---

## Sources

- [Docling — parsing et conversion de documents](https://docling-project.github.io/docling/)

- [PyMuPDF — OCR complet ou partiel des pages](https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_textpage_ocr) — vérification ciblée du 12 novembre 2026, sans renouvellement de la date globale de la fiche.

## Connexions
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — l'ingestion en amont du retrieval
- [[22-rag-avance|RAG avancé]] — chunking contextuel
- [[161-modeles-vision-langage|Modèles vision-langage]] — VLM comme parseurs
- [[133-embeddings-representations|Embeddings]] — late interaction
- [[145-cas-system-design|Cas de system design]] — recherche documentaire et extraction
- [[25-chunking-contextual-retrieval|Chunking avancé]] — du document structuré aux chunks contextualisés
- [[148-pipelines-batch-llm|Pipelines batch]] — traiter des millions de documents
- [[150-017-datasets-corpus-ia|Construction de datasets & corpus IA]] — contrôler les représentations dérivées
- [[00-moc-ai-engineering|MOC AI Engineering]]
