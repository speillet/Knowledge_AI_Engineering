# IA responsable : biais, équité & transparence — Flashcards
Tags: #flashcards #ai-engineering #ia-responsable #biais #gouvernance
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que l'IA responsable, concrètement pour un AI Engineer ?
?
Un ensemble de **pratiques mesurables**, pas une déclaration de valeurs : **évaluer les biais** du système sur ses cas d'usage, **documenter** modèles et données, garantir une **supervision humaine** adaptée, être **transparent** avec les utilisateurs, et prévoir des **recours** en cas d'erreur.

---

D'où viennent les biais d'un système LLM ?
?
- **Données de pré-entraînement** : stéréotypes et surreprésentations du web.
- **Post-training** : préférences des annotateurs.
- **Données de l'application** : corpus RAG, exemples few-shot, données de fine-tuning.
- **Conception** : prompts, critères d'évaluation, population sur laquelle on a testé.
- **Usage** : automation bias des utilisateurs.

---

Comment tester les biais d'une application LLM ?
?
Par des **tests contrefactuels** : mêmes entrées où l'on ne change que l'**attribut sensible** (prénom, genre, origine, âge) et comparer les sorties (décision, score, ton, longueur). Un écart **systématique** révèle un biais. À faire sur **son cas d'usage** : un tri de CV, un scoring, une réponse de support.

---

Quelles métriques d'équité connaître ?
?
- **Parité démographique** : même taux de décision favorable entre groupes.
- **Égalité des chances** (equal opportunity) : même **taux de vrais positifs** entre groupes.
- **Égalité des taux d'erreur** (equalized odds) : mêmes taux de vrais **et** faux positifs.

Ces critères sont **mathématiquement incompatibles** en général : il faut **choisir** selon le contexte, et documenter ce choix.

---

Qu'est-ce qu'une model card ?
?
Une **fiche de documentation** d'un modèle : usages prévus et **hors périmètre**, données d'entraînement, **performances** (y compris par sous-groupe), limites connues, risques, évaluations de sécurité. Pour une application, on rédige l'équivalent : **system card** décrivant le système complet (modèles, données, garde-fous, supervision).

---

Qu'est-ce qu'une datasheet de jeu de données ?
?
La documentation d'un dataset : **motivation**, **composition** (qui est représenté, qui manque), **collecte** (consentement, sources), **prétraitements**, usages recommandés et déconseillés, **maintenance**. Elle rend visibles les biais et les **droits** attachés aux données.

---

Qu'est-ce que la sycophancy et pourquoi est-ce un problème de responsabilité ?
?
La tendance du modèle à **aller dans le sens de l'utilisateur** : approuver une idée fausse, changer une réponse correcte dès qu'on la conteste, flatter. Effet renforcé par l'alignement sur les **préférences humaines**. Risque réel en conseil, santé, éducation ; à tester par des evals où l'utilisateur **affirme une erreur** ou **conteste** une bonne réponse ([[52-post-training-alignement|post-training]]).

---

Comment trouver l'équilibre entre sécurité du contenu et utilité ?
?
Mesurer **les deux** : taux de réponses **nuisibles** sur un jeu de requêtes dangereuses, et taux de **refus injustifiés** (over-refusal) sur un jeu de requêtes **légitimes mais sensibles** (médicales, juridiques, sécurité informatique défensive). Un système qui refuse trop est **inutile** et pousse les utilisateurs vers des outils moins sûrs.

---

Quelle supervision humaine est « effective » ?
?
Une supervision où l'humain **comprend** ce que fait le système, **dispose du temps et de l'information** pour vérifier, peut **refuser ou corriger** sans pénalité, et n'est pas submergé de validations. Une case « validé par un humain » cochée par réflexe ne compte pas ([[144-ux-ia-human-in-the-loop|automation bias]]).

---

Quels référentiels de gouvernance de l'IA connaître ?
?
- **NIST AI RMF** : cadre de gestion des risques (Govern, Map, Measure, Manage).
- **ISO/IEC 42001** : système de management de l'IA, certifiable.
- **AI Act** pour l'UE ([[155-ai-act|AI Act]]).
- Principes de l'**OCDE**.

Ils structurent l'inventaire des systèmes, l'évaluation des risques et les rôles.

---

## Mises en situation

Mise en situation : ton outil de tri de candidatures est soupçonné de défavoriser certains profils. Comment le vérifies-tu ?
?
1. **Tests contrefactuels** : mêmes CV, en ne changeant que l'attribut sensible (prénom, genre, âge), et comparer les décisions et les scores
2. **Choisir une métrique d'équité** adaptée au contexte, en sachant que les critères sont incompatibles entre eux, et documenter ce choix
3. **Segmenter les résultats** par groupe plutôt que de se fier à un score global
4. **Chercher la cause** : données historiques biaisées, corpus, prompt, critères d'évaluation
5. **Corriger et re-mesurer**, puis documenter dans une fiche système ([[155-ai-act|obligations haut risque]])

**Piège** : retirer l'attribut sensible du prompt et croire le problème réglé, alors que des variables corrélées subsistent.

---

Mise en situation : pour éviter tout risque, la direction demande de brider fortement l'assistant. Il refuse désormais un quart des demandes légitimes. Comment ramènes-tu l'équilibre ?
?
1. **Mesurer les deux côtés** : taux de réponses nuisibles sur des requêtes dangereuses, et taux de **refus injustifiés** sur des requêtes légitimes mais sensibles
2. **Montrer le coût du sur-blocage** : les utilisateurs contournent l'outil et passent à des services non maîtrisés
3. **Affiner les guardrails** : règles ciblées plutôt qu'un filtrage large par mots-clés ([[101-securite-llm-guardrails|guardrails]])
4. **Rendre les refus actionnables** : expliquer pourquoi et proposer une alternative ([[144-ux-ia-human-in-the-loop|UX]])
5. **Suivre les deux taux** dans le temps, comme un arbitrage assumé et non comme un réglage ponctuel

**Piège** : considérer le refus comme toujours sans risque, alors qu'il a un coût réel d'usage.

---

## Connexions
- [[155-ai-act|AI Act]] — les obligations légales
- [[154-rgpd-llm|RGPD]] — décisions automatisées
- [[52-post-training-alignement|Post-training]] — l'origine de certains comportements
- [[94-evals-methodologie|Méthodologie d'évaluation]] — mesurer biais et refus
- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]] — contenu nuisible
- [[151-donnees-curation-annotation|Curation & annotation]] — documenter les données
- [[00-moc-ai-engineering|MOC AI Engineering]]
