# Data flywheel & versioning des données — Flashcards
Tags: #flashcards #ai-engineering #donnees #flywheel #versioning #mlops

Qu'est-ce qu'une data flywheel ?
?
Une **boucle d'amélioration continue** : le produit est utilisé → on collecte **traces et feedback** → on **analyse** les échecs → on améliore (prompts, retrieval, evals, fine-tuning) → le produit est meilleur → plus d'usage et de données. L'avantage concurrentiel durable vient de cette boucle, pas du modèle, que tout le monde peut acheter.

---

Comment commence un tour de data flywheel ?
?
1. **Collecter** traces et feedback, explicite comme implicite.
2. **Échantillonner** en priorité les échecs et les cas incertains.
3. **Analyser** et catégoriser les erreurs.

---

Comment se termine un tour de data flywheel ?
?
4. **Labelliser** et ajouter au golden dataset.
5. **Corriger**, en commençant par le levier le moins coûteux : prompt, puis retrieval, puis fine-tuning.
6. **Valider** offline, **déployer** en canary, **mesurer** online.

---

Pourquoi versionner les données ?
?
Pour **reproduire** une eval ou un entraînement (quelles données exactement ?), **comparer** des résultats dans le temps, **revenir en arrière** après une mauvaise modification, et prouver la **provenance** des données (audit, [[155-ai-act|AI Act]], droit d'auteur). Un score d'eval sans version du jeu de données n'a pas de sens.

---

Quels outils pour versionner les données ?
?
- **DVC** : versionne les fichiers de données à côté du code git (pointeurs dans git, contenu sur un stockage objet).
- **lakeFS** : branches et commits façon git **sur un data lake**.
- **Formats de table** avec historique (Delta Lake, Apache Iceberg : time travel).
- **Datasets versionnés** des plateformes d'eval ([[91-langfuse-observabilite|Langfuse]], Hugging Face Hub).

---

Que faut-il versionner ensemble pour qu'une eval soit reproductible ?
?
La **version du jeu de données**, du **prompt**, du **modèle** (identifiant daté), de la **configuration** (température, outils), de l'**index** RAG et du **modèle d'embedding**, du **code** des évaluateurs et du **prompt du juge**. C'est le **lineage** ([[111-mlops-llmops-fondamentaux|MLOps]], [[114-reproductibilite-variance|reproductibilité]]).

---

Comment versionner un index RAG ?
?
En enregistrant pour chaque index : la **liste des documents et leurs versions** (hash), les paramètres de **chunking**, le **modèle d'embedding**, la date de construction. Les mises à jour incrémentales gardent un **journal** ; une reconstruction complète crée une **nouvelle version** qu'on peut comparer à l'ancienne sur l'eval de retrieval avant de basculer.

---

Quels signaux de production alimentent la flywheel sans annotation humaine ?
?
- **Reformulations** de la même question (la première réponse a échoué).
- **Escalades** vers un humain et leur résolution.
- **Modifications** apportées par l'utilisateur à la sortie (la version finale est une correction).
- **Acceptation** ou rejet de suggestions.
- **Résultats** vérifiables (tests qui passent, ticket résolu).

---

Quels pièges menacent une data flywheel ?
?
- **Biais de sélection** : seuls certains utilisateurs donnent du feedback.
- **Boucle auto-renforçante** : on n'améliore que ce qu'on mesure déjà.
- **Dérive des labels** si le guide d'annotation change sans re-labelliser.
- **Consentement** et **finalité** : réutiliser les conversations pour entraîner exige une base légale ([[154-rgpd-llm|RGPD]]).

---

Comment prioriser les améliorations issues de la flywheel ?
?
Par **fréquence × gravité** de chaque catégorie d'échec, rapportées au **coût** de la correction. Une erreur rare mais grave (engagement financier) peut passer avant une erreur fréquente mais bénigne (ton). Tenir un **tableau des modes de défaillance** mis à jour à chaque tour.

---

## Mises en situation

Mise en situation : un concurrent utilise le même modèle que toi, avec les mêmes prompts publics. Où se construit ton avantage ?
?
1. **Pas dans le modèle** : il est achetable par tout le monde
2. **Dans les données** : traces, feedback, corrections d'utilisateurs, jeux d'eval propres à ton métier
3. **Dans la boucle** : capter les échecs, les analyser, corriger et mesurer, tour après tour
4. **Dans l'intégration** : accès aux systèmes internes, droits, contexte métier
5. **Condition** : collecter dès le premier jour, avec traces complètes et identifiants communs ([[151-donnees-curation-annotation|collecte]])

**Piège** : lancer sans instrumentation, puis découvrir six mois plus tard qu'on n'a rien pour s'améliorer.

---

Mise en situation : un score d'eval obtenu il y a trois mois est impossible à reproduire aujourd'hui. Qu'est-ce qui n'a pas été versionné ?
?
1. **Le jeu de données** lui-même, qui a été enrichi depuis
2. **Le prompt**, le **modèle** (identifiant daté) et la **configuration** de génération
3. **L'index RAG** et le **modèle d'embedding** utilisés à ce moment
4. **Le code des évaluateurs** et le **prompt du juge**
5. **La conséquence** : un score sans version du jeu et de la chaîne n'a pas de sens ([[114-reproductibilite-variance|reproductibilité]])

**Piège** : versionner le code et les prompts, mais laisser le jeu d'eval évoluer en continu sans étiquette de version.

---

## Connexions
- [[97-evals-online-ab-testing|Evals online]] — la collecte en production
- [[113-monitoring-drift-feedback|Monitoring, drift & feedback]] — la boucle de feedback
- [[151-donnees-curation-annotation|Curation & annotation]] — labelliser les échecs
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps]] — lineage et versioning
- [[114-reproductibilite-variance|Reproductibilité]] — rejouer une eval
- [[148-pipelines-batch-llm|Pipelines batch]] — lignage des sorties générées
- [[98-debogage-agents|Débogage des agents]] — trouver la cause d'un échec dans une trace
- [[00-moc-ai-engineering|MOC AI Engineering]]
