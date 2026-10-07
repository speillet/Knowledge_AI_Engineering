# Leadership technique en AI Engineering — Flashcards
Tags: #flashcards #ai-engineering #leadership #senior #produit
<!-- summary: ce qui fait un senior, choix des cas d'usage, ROI, échec des POC, RFC et ADR, build ou buy, go / no-go, standards d'équipe, mentorat, revue de conception, dette technique, communication et veille. -->


Qu'est-ce qui distingue un AI Engineer senior d'un confirmé ? <!--anki:684c3732252364496938-->
?
Un senior prend en charge un **résultat de bout en bout dans l'incertitude** : cadrage, preuve de valeur, choix techniques, livraison et exploitation. Il explicite les compromis, détecte une expérience trompeuse et sait arrêter une approche insuffisante.

Sa contribution se voit aussi dans l'autonomie des autres : décisions documentées, revues utiles, transmission et procédures réellement exécutables. Connaître les définitions de ce vault aide à raisonner ; démontrer ces compétences demande des réalisations, des incidents analysés et des arbitrages expliqués avec leurs limites.

---

Comment identifier un bon cas d'usage LLM ? <!--anki:4b2577697b426f3a4c41-->
?
- **Tâche fréquente**, coûteuse en temps humain, avec des **données disponibles**.
- **Tolérance à l'erreur** compatible (ou vérification humaine peu coûteuse).
- **Succès mesurable** (temps gagné, taux de résolution, qualité).
- Sponsor métier et **utilisateurs** identifiés.

À éviter : les cas où une **règle simple** ou un modèle ML classique suffisent, et les cas où une erreur est **grave et difficile à détecter**.

---

Comment estimer le ROI d'une fonctionnalité IA ? <!--anki:46336235733534795e37-->
?
**Valeur** : temps gagné × coût horaire × volume, revenus additionnels, erreurs évitées.
**Coûts** : développement, **inférence récurrente**, infra, **revue humaine** restante, maintenance (evals, migrations de modèles), risques.
Inclure le **taux d'adoption** réel et le coût des **erreurs** du système. Un POC impressionnant n'est pas un ROI.

---

Pourquoi tant de POC IA n'atteignent-ils jamais la production ? <!--anki:693a52455b6d31444b43-->
?
- Démontrés sur **quelques exemples choisis**, sans eval représentative.
- Écart entre **80 % en démo** et les **95 %+ exigés** en production.
- Sujets sous-estimés : **données réelles**, droits d'accès, sécurité, conformité, coûts à l'échelle, intégration dans les outils existants.
- Pas de **propriétaire** métier ni de métrique de succès.

Le senior pose ces questions **dès le cadrage**.

---

Qu'est-ce qu'un RFC / design doc pour une fonctionnalité IA doit contenir de spécifique ? <!--anki:4268716c3f7a326a2e6b-->
?
En plus du contenu classique (contexte, objectifs, architecture, alternatives) :
- la **stratégie d'évaluation** et les seuils de mise en production ;
- les **modes de défaillance** du modèle et leurs mitigations ;
- l'**analyse de risque** (sécurité, PII, [[155-ai-act|classification AI Act]]) ;
- l'**estimation de coût** d'inférence à l'échelle ;
- le **plan de rollout** (canary, A/B) et de **rollback**.

---

Qu'est-ce qu'un ADR et pourquoi en écrire pour les choix IA ? <!--anki:66767745303f396a214d-->
?
Un **Architecture Decision Record** : un court document qui fige **une décision, son contexte, les options écartées et ses conséquences**. Les choix IA (modèle, framework, RAG vs fine-tuning) sont **souvent remis en cause** quand le marché bouge : l'ADR permet de savoir **pourquoi** on a choisi et **à quelle condition** on doit reconsidérer.

---

Build ou buy pour une brique IA ? <!--anki:623f7e44644d5d2e292c-->
?
**Acheter** (SaaS, API managée) quand la brique est **non différenciante**, standard et que le fournisseur est meilleur et moins cher à l'échelle. **Construire** quand c'est **au cœur de la valeur**, quand les données ou contraintes (souveraineté, intégration) l'imposent, ou quand aucune offre ne convient. Critères : coût total, **lock-in**, confidentialité, vitesse, compétences internes ([[38-plateformes-agents|plateformes d'agents]]).

---

Comment piloter un projet IA dont la faisabilité est incertaine ? <!--anki:446a36356a5b543a253b-->
?
Par **étapes à décision** : prototype jetable (jours) → eval sur données réelles → pilote avec utilisateurs → production. À chaque étape, un **critère go / no-go chiffré** défini à l'avance. On accepte d'**arrêter** : un no-go rapide est un bon résultat.

---

Quels standards de développement un lead met-il en place pour l'équipe ? <!--anki:77473558776e6c7b3028-->
?
- **Prompts versionnés** et revus comme du code.
- **Evals obligatoires** en CI pour tout changement de prompt ou de modèle.
- **Templates** de design doc et d'ADR.

Le standard doit rendre une décision reproductible : artefacts identifiés, critères de réussite et trace de l'arbitrage. Adapter la profondeur de la revue au risque ; les petits changements ont besoin de contrôles ciblés et rapides. Le lead fournit exemples et outillage pour que ces pratiques soient effectivement utilisées, pas seulement documentées.

---

Quels standards d'exploitation et de sécurité un lead met-il en place ? <!--anki:6c386e6a59785458604f-->
?
- **Gateway unique** : clés, budgets, observabilité.
- **Checklist de sécurité** : injection, PII, permissions des outils.
- **Traces** systématiques et revue régulière d'échantillons.

Nommer les responsables des alertes, incidents, budgets et migrations de modèles. Tester arrêt d'urgence, révocation d'accès et reprise sur un scénario réaliste. Les traces doivent être utiles au diagnostic et proportionnées aux données sensibles ; une centralisation technique ne remplace pas la responsabilité des équipes pour les usages qu'elles livrent.

---

Comment expliquer les limites de l'IA à un décideur non technique ? <!--anki:79794d41516042715354-->
?
En termes de **risque et de probabilité**, pas de technologie : « sur 100 demandes, 92 sont traitées correctement, 5 sont escaladées, 3 contiennent une erreur que l'on détecte dans 2 cas sur 3 ». Montrer des **exemples réels** d'échecs, le **coût** et le **plan de mitigation**. Éviter aussi bien l'enthousiasme sans chiffres que le refus de principe.

---

Comment rester à jour sans courir après chaque nouveauté ? <!--anki:732f4a7c70342b334c40-->
?
- Séparer **principes durables** (evals, sécurité, architecture, coûts) et **outils éphémères**.
- Tester les nouveautés **sur ses propres evals**, pas sur des annonces.
- Réserver un **temps d'exploration** limité et partager les résultats (notes, démos internes).
- Maintenir des fiches comme ce vault, **corrigées** quand la réalité change.

---

Comment un senior développe-t-il l'autonomie d'un collègue sur un projet IA ? <!--anki:3534353366323764333364353439633739313730343038363562616362636436-->
?
Confier un **périmètre et un résultat vérifiable**, avec contraintes, accès et critères de réussite explicites. Faire expliquer le protocole d'évaluation et les options avant de proposer sa propre solution, puis organiser des points de revue proportionnés au risque.

Sur un premier déploiement, préparer ensemble un runbook puis laisser le collègue l'exécuter dans un exercice contrôlé. Le signe de progression est sa capacité à diagnostiquer et décider sans dépendance permanente au senior. Répondre soi-même à chaque problème peut accélérer aujourd'hui tout en bloquant cette progression.

---

Comment conduire une revue de conception IA qui aboutit à une décision ? <!--anki:3736656232363665373136663466663661366564373835333039623061323936-->
?
Partir des **contraintes et preuves**, puis comparer quelques options réalistes, baseline comprise. Identifier l'hypothèse qui pourrait inverser le choix : qualité sur un segment, coût de revue humaine, quota ou délai de reprise.

Transformer les désaccords testables en expériences bornées, avec responsable et critère de décision. Documenter le choix, ses limites et la condition de réexamen dans un ADR. Un consensus sur le framework ne suffit pas si personne n'a vérifié la disponibilité des données ou défini ce qui rendrait la solution inacceptable.

---

Comment prioriser une dette technique IA face à une nouvelle fonctionnalité ? <!--anki:6537306139656166653437613462663961346332663134316535376364653430-->
?
Décrire la **conséquence mesurable** de la dette : incidents récurrents, temps de migration, coût d'exploitation, erreurs non détectées ou dépendance à une personne. Comparer son coût de maintien et son risque à l'effort de correction et à la valeur de la fonctionnalité.

Une dépendance non versionnée qui invalide les evals peut justifier une action immédiate ; une abstraction imparfaite sans impact peut attendre. Préférer une correction limitée et vérifiable à une refonte générale. Associer responsable, échéance et preuve d'amélioration à la décision.

---

## Mises en situation

Mise en situation : ta direction veut « faire de l'IA » et te demande de lancer six projets en parallèle. Comment réponds-tu sans passer pour un frein ? <!--anki:67617e3b517835434e71-->
?
1. **Qualifier les cas** : fréquence, coût humain actuel, données disponibles, tolérance à l'erreur, succès mesurable
2. **Éliminer** ceux qu'une règle simple ou un modèle classique traiterait mieux, et ceux où une erreur grave passerait inaperçue
3. **Prioriser deux cas** avec sponsor métier identifié et métrique de succès claire
4. **Piloter par étapes à décision** : prototype, eval sur données réelles, pilote, production, avec des critères chiffrés
5. **Assumer l'arrêt** : un no-go rapide vaut mieux qu'un projet qui traîne un an

**Piège** : accepter les six projets et livrer six prototypes que personne n'utilise.

---

Mise en situation : un directeur te demande pourquoi l'assistant « se trompe encore », après une démonstration impressionnante il y a trois mois. Comment expliques-tu ? <!--anki:7a2a466d215f342b287e-->
?
1. **Parler en probabilités**, pas en technologie : sur 100 demandes, tant de réussites, tant d'escalades, tant d'erreurs, dont une part détectée
2. **Montrer des exemples réels** d'échecs, et non des moyennes abstraites
3. **Expliquer l'écart démo-production** : quelques exemples choisis contre des données réelles et variées
4. **Présenter le plan** : evals, corrections mesurées, garde-fous, vérification humaine là où le risque l'exige
5. **Chiffrer la valeur nette** malgré les erreurs : temps gagné, coût des erreurs, ROI ([[122-finops-llm|FinOps]])

**Piège** : promettre une fiabilité que le système n'atteindra pas, ou rejeter la responsabilité sur le modèle.

---

Mise en situation : tu es la seule personne capable de déployer et dépanner l'assistant, et chaque livraison attend ton retour. Que mets-tu en place ? <!--anki:3732376634316264343333373430393962333932396437373037376665336638-->
?
1. **Identifier les dépendances personnelles** : accès, commandes, décisions et connaissances implicites.
2. **Documenter un parcours reproductible**, de l'eval au rollback, avec exemples de panne.
3. **Automatiser les contrôles répétitifs** et attribuer les responsabilités d'exploitation.
4. **Faire exécuter le parcours par un collègue**, puis corriger les lacunes révélées.
5. **Mesurer l'autonomie acquise** : livraison et diagnostic réussis sans intervention indispensable.

**Piège** : écrire une documentation que personne n'a jamais utilisée, puis considérer le transfert terminé.

---

## Connexions
- [[141-system-design-llm|System design LLM]] — cadrer et arbitrer
- [[146-choix-modeles|Choix de modèle]] — décisions à documenter
- [[94-evals-methodologie|Méthodologie d'évaluation]] — critères go / no-go
- [[122-finops-llm|FinOps LLM]] — coûts et rôle du Lead
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps]] — rôle du Lead
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Gouvernance]] — paved road
- [[155-ai-act|AI Act]] — cadrage réglementaire
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[171-choisir-modele-ml|Choisir un modèle ML]] — justifier la complexité par la valeur métier
- [[116-sre-incidents-capacite-ia|SRE : incidents & capacité des services IA]] — responsabilités et suivi des corrections
- [[00-moc-ai-engineering|MOC AI Engineering]]
