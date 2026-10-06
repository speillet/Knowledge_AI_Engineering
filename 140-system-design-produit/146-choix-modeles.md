# Choisir un modèle — Flashcards
Tags: #flashcards #ai-engineering #choix-modele #benchmarks #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: critères, limites des leaderboards, benchmarks, fermé ou open weights, licences, coût par tâche, architecture multi-modèles, lock-in, migration, veille. -->


Quels critères techniques pour choisir un modèle ? <!--anki:4e76712b43634b3a5168-->
?
1. **Qualité sur sa tâche** (eval maison, pas le leaderboard).
2. **Coût** par tâche réussie (pas seulement le prix par token).
3. **Latence** : TTFT et débit.
4. **Capacités** : fenêtre de contexte utile, multimodalité, tool calling, structured outputs.

---

Quels critères non techniques pèsent sur le choix d'un modèle ? <!--anki:693e6d41763d4f6b3363-->
?
1. **Confidentialité** : où vont les données, rétention, région.
2. **Licence** et conditions d'usage.
3. **Fiabilité du fournisseur** : SLA, rate limits, dépréciations annoncées.

Vérifier ces exigences sur l'offre exacte : contrat, région et fonctionnalités activées peuvent changer les conditions. Une licence autorisant l'usage interne n'autorise pas nécessairement toute redistribution. Documenter les contraintes éliminatoires avant les benchmarks, puis prévoir une migration si le fournisseur retire le modèle ou modifie ses conditions.

---

Pourquoi un classement de benchmarks ne suffit-il pas pour choisir un modèle ? <!--anki:6d6d6943634d763c4d30-->
?
- Les benchmarks mesurent des **capacités générales**, pas **ta tâche**.
- **Contamination** : certains scores sont gonflés ([[135-pretraining-scaling-laws|contamination]]).
- Les **arènes de préférence** (votes humains à l'aveugle) favorisent le **style** (longueur, format) autant que l'exactitude.
- Les écarts de quelques points sont souvent **dans le bruit**.

Ils servent à faire une **liste courte**, que l'on départage avec son eval.

---

Quels benchmarks mesurent les connaissances et le raisonnement ? <!--anki:6e2958374a2d3a4e4d34-->
?
- **MMLU / MMLU-Pro** : connaissances générales en QCM (saturé pour les meilleurs modèles).
- **GPQA** : questions scientifiques de niveau doctorat.
- **AIME et autres benchmarks de maths** : raisonnement.
- **Humanity's Last Exam** : questions expertes très difficiles.

---

Quels benchmarks mesurent les capacités utiles en application ? <!--anki:515e6c40486e6f5e6030-->
?
- **SWE-bench (Verified)** : résolution de vrais tickets GitHub.
- **τ-bench** : agents de support avec outils et utilisateur simulé.
- **IFEval** : respect d'instructions vérifiables.
- **RULER** : exploitation réelle du long contexte.

Ils explorent des capacités distinctes ; un bon score sur l'un ne prédit pas tout le produit. Examiner version, protocole, outils autorisés et budget de calcul avant de comparer. Les résultats publiés servent à présélectionner, puis un jeu interne représentatif doit vérifier les erreurs, la latence et le coût sur le véritable usage.

---

Modèle fermé (API) ou open weights ? <!--anki:772b5b4b677551327068-->
?
- **Fermé** : souvent **le meilleur niveau**, zéro infra, mises à jour continues — mais données envoyées à un tiers, dépendance, **changements** et **dépréciations** imposés.
- **Open weights** : **contrôle** total (on-prem, souveraineté, fine-tuning complet, version figée), coût marginal bas à fort volume — mais **infra GPU** et compétences d'exploitation, et qualité souvent un cran en dessous du meilleur fermé.

Beaucoup d'entreprises utilisent **les deux** derrière une [[81-litellm-api-layer|gateway]].

---

À ne pas confondre : open weights et open source ? <!--anki:45583454626869623129-->
?
**Open weights** = les **poids** sont téléchargeables, mais pas forcément les **données** ni le **code d'entraînement**, et la licence peut **restreindre** l'usage (seuil d'utilisateurs, usages interdits, obligations d'attribution). Un modèle **open source** au sens strict (OSI) publie de quoi le **reproduire** et autorise tout usage. Toujours **lire la licence**.

---

Comment comparer le coût de deux modèles correctement ? <!--anki:4b3f394d40257e6f6577-->
?
Sur **le coût par tâche réussie** : un modèle moins cher par token peut consommer **plus de tokens** (tokenizer moins efficace, réponses plus longues, raisonnement), **échouer plus souvent** (retries, escalades) ou exiger un prompt plus long. On mesure les tokens **réels** sur son eval ([[121-couts-inference|coûts]]).

---

Pourquoi ne pas chercher « le meilleur modèle » unique ? <!--anki:4c62553c676731324f2f-->
?
Parce que les besoins varient **au sein d'une même application** : un petit modèle rapide pour la classification et le routage, un modèle fort pour la génération complexe, un modèle de raisonnement pour les cas difficiles, un modèle d'embedding pour le retrieval. L'architecture **multi-modèles** avec [[82-routing-llm|routage]] est la norme.

---

Comment éviter le lock-in fournisseur ? <!--anki:6a3132365f365e506038-->
?
- **Gateway** avec une interface unifiée (format compatible OpenAI, LiteLLM).
- **Prompts et evals versionnés** : on peut qualifier un autre modèle en quelques heures.
- Éviter de dépendre de fonctions **propriétaires** non essentielles, ou les **isoler** derrière une abstraction.
- Garder un **fallback** chez un autre fournisseur, testé régulièrement.

---

Comment limiter les risques lors d'une migration vers un nouveau modèle ? <!--anki:4d265f5f36683060794b-->
?
1. Faire tourner le **jeu d'eval** complet (qualité, format, coût, latence).
2. **Tester les prompts existants**, puis les ajuster si nécessaire : leur portabilité se mesure.
3. **Shadow** ou **canary** sur le trafic réel.
4. **A/B test** si l'enjeu produit est important.
5. Garder l'ancien modèle en **fallback** jusqu'à stabilisation ([[112-cicd-modeles|CI/CD des modèles]]).

---

Comment suivre un marché qui change tous les mois ? <!--anki:75334b5e4a6133343a3f-->
?
Garder un **processus** plutôt qu'une opinion figée : une **eval maison automatisée** qu'on relance à chaque sortie de modèle notable, une **grille de décision** partagée, et une **revue trimestrielle** des choix de modèles face au coût et à la qualité ([[147-leadership-technique-ia|leadership technique]]).

---

## Mises en situation

Mise en situation : un nouveau modèle sort, annoncé meilleur partout et 30 % moins cher. Ton équipe veut migrer cette semaine. Quel processus imposes-tu ? <!--anki:4b504f356c6a4d2e525f-->
?
1. **Rejouer l'eval maison** complète : qualité, format, tool calling, coût réel en tokens, latence
2. **Ajuster les prompts** : un prompt n'est pas portable tel quel d'un modèle à l'autre
3. **Comparer le coût par tâche réussie**, pas le prix par token : un modèle bavard peut coûter plus cher
4. **Shadow puis canary** sur le trafic réel, avec l'ancien modèle en repli ([[112-cicd-modeles|CI/CD]])
5. **Documenter la décision** et ce qui ferait revenir en arrière

**Piège** : migrer sur la foi d'un communiqué et découvrir la régression sur un segment en production.

---

Mise en situation : la direction impose que les données ne sortent pas de l'entreprise, mais l'équipe veut la qualité d'un modèle propriétaire. Comment traites-tu la contrainte ? <!--anki:6d4d79474d392149404e-->
?
1. **Prendre la contrainte comme un critère de choix**, pas comme un obstacle à contourner
2. **Vérifier les options** : offres régionales, engagements de non-entraînement et de rétention, déploiement chez un fournisseur cloud existant
3. **Évaluer les open weights** sur ta tâche : l'écart est parfois faible sur un périmètre restreint ([[164-llm-local-edge|LLM locaux]])
4. **Segmenter** : self-host pour les données sensibles, API pour le reste, derrière une gateway
5. **Chiffrer** le coût total du self-host, exploitation comprise ([[121-couts-inference|coûts]])

**Piège** : choisir un modèle d'abord et espérer que la conformité suivra.

---

## Sources

- [Hugging Face — méthodologie du Open LLM Leaderboard](https://huggingface.co/docs/leaderboards/open_llm_leaderboard/about)
- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

## Connexions
- [[94-evals-methodologie|Méthodologie d'évaluation]] — départager les candidats
- [[82-routing-llm|Routing LLM]] — combiner plusieurs modèles
- [[121-couts-inference|Coûts d'inférence]] — coût par tâche
- [[135-pretraining-scaling-laws|Pré-entraînement]] — contamination et cutoff
- [[164-llm-local-edge|LLM locaux & edge]] — les options open weights
- [[155-ai-act|AI Act]] — obligations des modèles à usage général
- [[13-prompts-production|Prompts en production]] — un prompt ne se transfère pas d'un modèle à l'autre
- [[12-optimisation-automatique-prompts|Optimisation automatique de prompts]] — laisser une métrique choisir la formulation
- [[141-system-design-llm|System design LLM]] — la méthode de conception
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[63-guided-generation|Guided generation]] — garantir des sorties structurées valides
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT, TPOT, débit et percentiles
- [[171-choisir-modele-ml|ML classique]] — comparer un LLM aux règles et modèles prédictifs
- [[00-moc-ai-engineering|MOC AI Engineering]]
