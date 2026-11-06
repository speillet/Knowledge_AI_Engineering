# IA responsable : biais, équité & transparence — Flashcards
Tags: #flashcards #ai-engineering #ia-responsable #biais #gouvernance
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: safety ou security, sources de biais, tests contrefactuels, métriques d'équité, model cards et system cards, datasheets, sycophancy, sécurité ou utilité, supervision humaine effective. -->


Qu'est-ce que l'IA responsable, concrètement pour un AI Engineer ? <!--anki:4771215a794054786b55-->
?
Un ensemble de **pratiques mesurables**, pas une déclaration de valeurs : **évaluer les biais** du système sur ses cas d'usage, **documenter** modèles et données, garantir une **supervision humaine** adaptée, être **transparent** avec les utilisateurs, et prévoir des **recours** en cas d'erreur.

Exemple pour un assistant client bancaire : comparer la qualité des réponses par langue et par région, documenter les données et leurs lacunes, escalader les demandes sensibles vers un conseiller, indiquer qu'il s'agit d'une IA et offrir une voie de recours. Chaque pratique produit une preuve, comme un rapport d'évaluation ou une procédure ; sans preuve, l'engagement n'est pas vérifiable.

---

D'où viennent les biais d'un système LLM ? <!--anki:42403a7e3d6e7a7a2129-->
?
- **Données de pré-entraînement** : stéréotypes et surreprésentations du web.
- **Post-training** : préférences des annotateurs.
- **Données de l'application** : corpus RAG, exemples few-shot, données de fine-tuning.
- **Conception** : prompts, critères d'évaluation, population sur laquelle on a testé.
- **Usage** : automation bias des utilisateurs.

Un biais peut naître sans le modèle : un corpus RAG de procédures rédigées pour la métropole répond mal aux clients d'outre-mer, quel que soit le LLM utilisé.

---

Comment tester les biais d'une application LLM ? <!--anki:4e4f58497d51257e7d7c-->
?
Par des **tests contrefactuels** : mêmes entrées où l'on ne change que l'**attribut sensible** (prénom, genre, origine, âge) et comparer les sorties (décision, score, ton, longueur). Un écart **systématique** révèle un biais. À faire sur **son cas d'usage** : un tri de CV, un scoring, une réponse de support.

Exemple : 200 CV présentés deux fois, avec pour seule différence le prénom « Julien » ou « Karim ». Comparer les scores **par paire** : un écart moyen de 0,4 point sur 10, dont l'intervalle de confiance exclut zéro, est systématique ([[99-statistiques-decisions-experimentales|comparaison appariée]]).

---

Quelles métriques d'équité comparent les décisions entre groupes, et pourquoi faut-il en choisir une ? <!--anki:725d787d6d4b4c4c6c58-->
?
- **Parité démographique** : même taux de décision favorable entre groupes.
- **Égalité des chances** (equal opportunity) : même **taux de vrais positifs** entre groupes.
- **Égalité des taux d'erreur** (equalized odds) : mêmes taux de vrais **et** faux positifs.

Exemple : le groupe A obtient 40 % de décisions favorables, le groupe B 25 % ; la parité démographique est violée. Si 80 % des candidats réellement qualifiés sont retenus dans chaque groupe, l'égalité des chances est pourtant respectée.

Avec des taux de base différents, un classifieur informatif ne satisfait pas simultanément parité démographique et equalized odds. Choisir et documenter le compromis selon le contexte.

---

Qu'est-ce qu'une model card ? <!--anki:466933485e7a4251656f-->
?
Une **fiche de documentation** d'un modèle : usages prévus et **hors périmètre**, données d'entraînement, **performances** (y compris par sous-groupe), limites connues, risques, évaluations de sécurité. Pour une application, on rédige l'équivalent : **system card** décrivant le système complet (modèles, données, garde-fous, supervision).

Exemple d'usage : la model card d'un modèle ouvert indique des évaluations surtout en anglais ; avant de l'utiliser pour du support en français, une eval maison s'impose. Une system card se met à jour à chaque changement de modèle, de données ou de garde-fou : une fiche figée devient fausse sans que personne ne s'en aperçoive.

---

Qu'est-ce qu'une datasheet de jeu de données ? <!--anki:68283c64423653794434-->
?
La documentation d'un dataset : **motivation**, **composition** (qui est représenté, qui manque), **collecte** (consentement, sources), **prétraitements**, usages recommandés et déconseillés, **maintenance**. Elle rend visibles les biais et les **droits** attachés aux données.

Elle permet à une autre équipe de décider si les données conviennent à son usage. Par exemple, un jeu recueilli dans une seule langue peut mal représenter un service multilingue. Versionner la fiche avec le dataset et documenter ses limites connues ; une documentation complète ne corrige pas en elle-même les biais constatés.

---

Qu'est-ce que la sycophancy et pourquoi est-ce un problème de responsabilité ? <!--anki:4a4233782a503e797468-->
?
La tendance du modèle à **aller dans le sens de l'utilisateur** : approuver une idée fausse, changer une réponse correcte dès qu'on la conteste, flatter. Effet renforcé par l'alignement sur les **préférences humaines**. Risque réel en conseil, santé, éducation ; à tester par des evals où l'utilisateur **affirme une erreur** ou **conteste** une bonne réponse ([[52-post-training-alignement|post-training]]).

Exemple : le modèle répond « 17 × 24 = 408 », l'utilisateur rétorque « Non, c'est 418 ». Mesurer la part des réponses correctes abandonnées après ce type de contestation.

---

Comment trouver l'équilibre entre sécurité du contenu et utilité ? <!--anki:47404b7b3e362d327e78-->
?
Mesurer **les deux** : taux de réponses **nuisibles** sur un jeu de requêtes dangereuses, et taux de **refus injustifiés** (over-refusal) sur un jeu de requêtes **légitimes mais sensibles** (médicales, juridiques, sécurité informatique défensive). Un système qui refuse trop est **inutile** et pousse les utilisateurs vers des outils moins sûrs.

Exemple : 24 refus sur 300 questions légitimes, comme « quelle dose maximale de paracétamol pour un adulte ? », font 8 % de sur-refus. Suivre ce taux à côté de celui des réponses nuisibles, sur des jeux versionnés.

---

Quelle supervision humaine est « effective » ? <!--anki:4b4f7b442d264b33737b-->
?
Une supervision où l'humain **comprend** ce que fait le système, **dispose du temps et de l'information** pour vérifier, peut **refuser ou corriger** sans pénalité, et n'est pas submergé de validations. Une case « validé par un humain » cochée par réflexe ne compte pas ([[144-ux-ia-human-in-the-loop|automation bias]]).

Cela se mesure : un relecteur qui valide 400 décisions par heure leur consacre 9 secondes chacune. Glisser des cas piégés à la réponse connue dans sa file indique la part d'erreurs qu'il détecte réellement.

---

À ne pas confondre : safety et security ? <!--anki:4f462d3828282f2f755e-->
?
**Safety** vise la prévention des dommages causés par le système, y compris sans adversaire ; **security** vise sa protection contre les accès ou actions hostiles ([[101-securite-llm-guardrails|sécurité]]).

Exemple : une recommandation erronée donnée spontanément relève de la safety ; une instruction externe qui détourne l'agent vers une fuite de données relève de la security. Une attaque peut aussi provoquer un dommage de safety : les périmètres se recouvrent.

Définir scénarios, responsables et critères séparément, puis tester leurs interactions. Un filtre de contenu ne remplace pas les permissions ; une infrastructure protégée ne garantit pas des conseils exacts ou un traitement équitable.

---

## Mises en situation

Mise en situation : ton outil de tri de candidatures est soupçonné de défavoriser certains profils. Comment le vérifies-tu ? <!--anki:4e4b4d5f446755437270-->
?
1. **Tests contrefactuels** : mêmes CV, en ne changeant que l'attribut sensible (prénom, genre, âge), et comparer les décisions et les scores
2. **Choisir une métrique d'équité** adaptée au contexte, en sachant que les critères sont incompatibles entre eux, et documenter ce choix
3. **Segmenter les résultats** par groupe plutôt que de se fier à un score global
4. **Chercher la cause** : données historiques biaisées, corpus, prompt, critères d'évaluation
5. **Corriger et re-mesurer**, puis documenter dans une fiche système ([[155-ai-act|obligations haut risque]])

**Piège** : retirer l'attribut sensible du prompt et croire le problème réglé, alors que des variables corrélées subsistent.

---

Mise en situation : pour éviter tout risque, la direction demande de brider fortement l'assistant. Il refuse désormais un quart des demandes légitimes. Comment ramènes-tu l'équilibre ? <!--anki:4c532b3346427d6b7a46-->
?
1. **Mesurer les deux côtés** : taux de réponses nuisibles sur des requêtes dangereuses, et taux de **refus injustifiés** sur des requêtes légitimes mais sensibles
2. **Montrer le coût du sur-blocage** : les utilisateurs contournent l'outil et passent à des services non maîtrisés
3. **Affiner les guardrails** : règles ciblées plutôt qu'un filtrage large par mots-clés ([[101-securite-llm-guardrails|guardrails]])
4. **Rendre les refus actionnables** : expliquer pourquoi et proposer une alternative ([[144-ux-ia-human-in-the-loop|UX]])
5. **Suivre les deux taux** dans le temps, comme un arbitrage assumé et non comme un réglage ponctuel

**Piège** : considérer le refus comme toujours sans risque, alors qu'il a un coût réel d'usage.

---

## Sources

- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## Connexions
- [[155-ai-act|AI Act]] — les obligations légales
- [[154-rgpd-llm|RGPD]] — décisions automatisées
- [[52-post-training-alignement|Post-training]] — l'origine de certains comportements
- [[94-evals-methodologie|Méthodologie d'évaluation]] — mesurer biais et refus
- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]] — contenu nuisible
- [[151-donnees-curation-annotation|Curation & annotation]] — documenter les données
- [[177-explicabilite-modeles|Explicabilité & diagnostic des modèles]] — analyser les effets et les limites d'une explication
- [[00-moc-ai-engineering|MOC AI Engineering]]
