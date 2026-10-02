# Parsing de documents (PDF, OCR, layout) — Flashcards
Tags: #flashcards #ai-engineering #multimodal #document-parsing #rag
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: PDF natif ou scanné, analyse de layout, outils (Docling, Unstructured, services cloud, VLM), tableaux, figures, ColPali, chunking structurel, évaluation, exploitation. -->

Pourquoi le parsing de documents est-il souvent le goulot d'un RAG d'entreprise ?
?
<!--anki:7038666a4c6a61724345-->
Parce que les documents réels sont des **PDF scannés, tableaux, slides, formulaires, colonnes multiples, en-têtes et pieds de page**. Un mauvais parsing (tableau aplati, colonnes mélangées, texte manquant) produit des chunks **inexploitables** : aucun modèle ni reranker ne rattrape une information **perdue à l'ingestion** ([[21-rag-fondamentaux|RAG]]).

---

À ne pas confondre : PDF natif et PDF scanné ?
?
<!--anki:4c4f575870682a745132-->
- **Natif** (généré numériquement) : contient une **couche texte** extractible directement (pypdf, pdfplumber, PyMuPDF), mais **sans structure** fiable (ordre de lecture, tableaux).
- **Scanné** : une **image** de page → nécessite de l'**OCR**.

Beaucoup de PDF sont **mixtes** ; il faut détecter page par page.

---

Qu'est-ce que l'analyse de layout ?
?
<!--anki:752b69687c7e7867775a-->
Détecter les **zones** d'une page — titres, paragraphes, tableaux, figures, légendes, en-têtes, notes — et l'**ordre de lecture**. Elle permet de reconstruire la **structure** (hiérarchie des sections) et de traiter chaque zone avec le bon outil (OCR, extraction de tableau, description de figure).

---

Quel outil de parsing selon le document : PDF natif simple, mise en page complexe, scans en volume, données confidentielles ?
?
<!--anki:3963656532376466656136373464373061363131353338666435663437353963-->
- **PDF natif au texte simple** : une bibliothèque classique (**PyMuPDF**, pdfplumber), rapide et gratuite
- **Mise en page complexe, tableaux** : un pipeline avec analyse de layout (**Docling**, **Unstructured**, **Marker**, MinerU)
- **Scans et formulaires en volume** : un service cloud (AWS Textract, Azure Document Intelligence, Google Document AI) ou un **VLM** qui convertit chaque page en Markdown
- **Données qui ne doivent pas sortir** : un pipeline open source auto-hébergé, avec Tesseract pour l'OCR de base

On tranche sur la qualité **mesurée sur ses propres documents**, puis sur le coût.

---

Comment traiter les tableaux lors du parsing de documents ?
?
<!--anki:4b3d5068593763564574-->
Les extraire en **structure** (markdown, HTML ou JSON), pas en texte aplati. Pour le RAG : garder le tableau **entier** dans un chunk avec son **titre et ses en-têtes de colonnes** ; pour un grand tableau, répéter les en-têtes dans chaque morceau. On peut aussi générer un **résumé textuel** du tableau pour l'embedding et fournir le tableau complet au LLM.

---

Comment traiter les images et graphiques d'un document ?
?
<!--anki:62734f492d5f7a4c7026-->
Les faire **décrire par un VLM** (description + données lisibles du graphique) et indexer cette description, en gardant un **lien vers l'image** pour pouvoir la fournir au modèle au moment de la réponse. Alternative : **retrieval multimodal** direct sur les images de pages ([[161-modeles-vision-langage|VLM]]).

---

Qu'est-ce que le retrieval sur images de pages (type ColPali) ?
?
<!--anki:692e4d5d2665634c4768-->
On **n'extrait pas le texte** : chaque page est encodée **comme image** par un VLM en embeddings multi-vecteurs (late interaction), et la requête texte est comparée directement à ces pages. Robuste aux mises en page complexes et aux graphiques, au prix d'un **stockage** plus lourd et d'une réponse générée par un **VLM**.

---

Comment chunker en respectant la structure ?
?
<!--anki:49576b5a755e527e6934-->
Découper **selon la hiérarchie** (sections, sous-sections) plutôt qu'à taille fixe, **ne jamais couper** un tableau ou une liste au milieu, et ajouter à chaque chunk son **contexte** : titre du document, chemin des titres (« Contrat > Article 5 > Résiliation »), date, source. Ce contexte améliore beaucoup le retrieval ([[22-rag-avance|RAG avancé]]).

---

Comment évaluer une chaîne de parsing ?
?
<!--anki:7750667d2928215a777b-->
- Sur un **échantillon représentatif** de documents (y compris les pires : scans, tableaux complexes).
- Métriques : **taux d'erreur de caractères** (OCR), exactitude des **cellules** de tableau, ordre de lecture, **champs** extraits corrects.
- Et surtout l'effet **en aval** : recall du retrieval et qualité des réponses du RAG.

---

Quels pièges d'exploitation dans une chaîne d'ingestion ?
?
<!--anki:504a6b3c446331367152-->
- **Coût et durée** : un VLM ou un service cloud sur des millions de pages coûte cher → traitement **batch**, cache par hash de fichier.
- **Échecs silencieux** : pages vides, encodages cassés → contrôles de qualité automatiques (longueur, ratio de caractères valides).
- **Mises à jour** : ré-ingestion incrémentale et suppression des anciennes versions.
- **Confidentialité** des documents envoyés à un service externe ([[152-pii-confidentialite|PII]]).

---

## Mises en situation

Mise en situation : ton RAG répond mal sur les documents contenant des tableaux, alors que le retrieval semble correct. Où cherches-tu ?
?
<!--anki:706d673e5b7368796370-->
1. **Regarder les chunks eux-mêmes** : un tableau aplati en texte perd les correspondances entre lignes et colonnes
2. **Extraire en structure** (markdown, HTML ou JSON) plutôt qu'en texte brut
3. **Garder le tableau entier** dans un chunk, avec son titre et ses en-têtes, et répéter les en-têtes si on doit le découper
4. **Enrichir l'index** : un résumé textuel du tableau pour l'embedding, le tableau complet fourni au modèle
5. **Mesurer en aval** : recall et exactitude des réponses sur les questions qui portent sur des tableaux

**Piège** : chercher la cause dans le modèle de génération alors que l'information a été perdue à l'ingestion.

---

Mise en situation : tu dois ingérer 500 000 PDF, dont beaucoup de scans, avec un budget limité. Comment conçois-tu la chaîne ?
?
<!--anki:6d7e7b6f2367455a4132-->
1. **Trier par type** : PDF natifs traités par extraction directe, scans envoyés à l'OCR, cas complexes à un VLM
2. **Traiter en batch** et **cacher par empreinte de fichier**, pour ne jamais retraiter deux fois le même document
3. **Contrôles qualité automatiques** : pages vides, ratio de caractères valides, longueur anormale, pour détecter les échecs silencieux
4. **Évaluer la chaîne** sur un échantillon représentatif, en incluant les pires documents
5. **Vérifier la confidentialité** avant d'envoyer des documents à un service externe ([[152-pii-confidentialite|PII]])

**Piège** : envoyer les 500 000 documents au parseur le plus coûteux, alors que la majorité se traite avec une simple extraction.

---

## Sources

- [Docling — parsing et conversion de documents](https://docling-project.github.io/docling/)

## Connexions
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — l'ingestion en amont du retrieval
- [[22-rag-avance|RAG avancé]] — chunking contextuel
- [[161-modeles-vision-langage|Modèles vision-langage]] — VLM comme parseurs
- [[133-embeddings-representations|Embeddings]] — late interaction
- [[145-cas-system-design|Cas de system design]] — recherche documentaire et extraction
- [[25-chunking-contextual-retrieval|Chunking avancé]] — du document structuré aux chunks contextualisés
- [[148-pipelines-batch-llm|Pipelines batch]] — traiter des millions de documents
- [[00-moc-ai-engineering|MOC AI Engineering]]
