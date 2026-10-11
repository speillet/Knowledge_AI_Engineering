# Choisir un modèle — Flashcards
Tags: #flashcards #ai-engineering #choix-modele #benchmarks #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: critères et contraintes, benchmarks, hébergement et ouverture des poids, définition OSI, coût par succès, protocole comparable, front de Pareto, migration et lock-in. -->


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
Une **API** externalise le serving mais impose des conditions de traitement des données, quotas et changements de catalogue. Un modèle **open weights** permet de gérer soi-même le déploiement si sa licence et les ressources disponibles le permettent.

Aucun choix ne garantit le meilleur niveau de qualité ni le moindre coût. Comparer tâche, exigences de données, matériel, volume, exploitation et capacité de migration. L'API peut éviter un investissement initial ; l'auto-hébergement peut apporter contrôle et économie à certaines charges. Des modèles open weights sont aussi accessibles en service managé : disponibilité des poids et mode d'hébergement sont deux décisions distinctes.

---

À ne pas confondre : open weights et open source ? <!--anki:45583454626869623129-->
?
**Open weights** indique que les paramètres sont accessibles ; cela ne précise pas à lui seul les libertés d'usage ni les éléments publiés.

La définition **Open Source AI 1.0 de l'OSI** exige les libertés d'utiliser, étudier, modifier et partager, ainsi que paramètres, code et informations suffisamment détaillées sur les données pour construire un système substantiellement équivalent. Elle n'exige pas nécessairement la publication de toutes les données brutes ni une reproduction bit à bit. Vérifier les éléments disponibles et leurs conditions ; ne pas déduire cette qualification du seul téléchargement des poids.

---

Comment comparer le coût de deux modèles correctement ? <!--anki:4b3f394d40257e6f6577-->
?
Sur **le coût par tâche réussie** : un modèle moins cher par token peut consommer **plus de tokens** (tokenizer moins efficace, réponses plus longues, raisonnement), **échouer plus souvent** (retries, escalades) ou exiger un prompt plus long. On mesure les tokens **réels** sur son eval ([[121-couts-inference|coûts]]).

---

Pourquoi ne pas chercher « le meilleur modèle » unique ? <!--anki:4c62553c676731324f2f-->
?
Les sous-tâches peuvent demander des capacités différentes : classer, rechercher, extraire ou raisonner. Plusieurs modèles avec [[82-routing-llm|routage]] peuvent réduire le coût ou améliorer un segment.

Cette architecture ajoute aussi des composants à valider, des seuils, du monitoring et des replis. Un modèle unique peut suffire et simplifier l'exploitation. Comparer d'abord cette baseline, puis introduire un spécialiste lorsqu'un gain utile dépasse le coût de coordination. La diversité des besoins suggère une comparaison ; elle ne prescrit pas une architecture multi-modèles universelle.

---

Comment éviter le lock-in fournisseur ? <!--anki:6a3132365f365e506038-->
?
Isoler les dépendances dont une migration pourrait bloquer le produit : contrats d'appel, formats, outils hébergés, identifiants et données persistantes.

Une **gateway** et des prompts versionnés facilitent le remplacement, mais ne garantissent pas la compatibilité des comportements. Garder evals, schémas et données exportables ; tester un autre fournisseur sur format, outils, sécurité, quotas et coût. Prévoir les fonctions sans équivalent et le temps de qualification. Un fallback non testé peut déplacer la panne plutôt que la résoudre.

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

Comment utiliser un front de Pareto pour choisir un modèle LLM ? <!--anki:3265623433663661633161393463643061393366393734343638356539643931-->
?
Éliminer d'abord les candidats qui violent une **contrainte obligatoire**. Parmi les autres, un candidat est dominé si un autre est au moins aussi bon sur tous les critères retenus et strictement meilleur sur l'un.

Les candidats non dominés forment le **front de Pareto** : aucun ne gagne partout. Départager selon compromis produit, par exemple qualité contre coût et latence. Utiliser des mesures comparables et leur incertitude ; une différence minuscule et bruitée ne démontre pas une domination réelle. Une moyenne pondérée ne doit pas masquer une contrainte éliminatoire.

---

Pourquoi comparer des modèles LLM avec le même protocole et des budgets explicités ? <!--anki:3965626364333538623730393432323461636332393333376565373831626436-->
?
Outils, contexte, prompts, nombre d'essais et budget de génération influencent le résultat. Un candidat autorisé à chercher et à essayer dix fois n'est pas directement comparable à une réponse unique sans outil.

Définir si l'on compare la **capacité du modèle** à ressources contrôlées ou le **système déployable** sous contraintes produit. Un prompt adapté à chaque modèle peut être pertinent si le budget d'optimisation est documenté. Rapporter protocole et coûts réels ; égaliser seulement `max_tokens` n'égalise ni le temps ni le calcul.

---

Calcul : sur le même test, A réussit 94 % à 0,010 €/requête et p95 = 0,8 s ; B, 95 % à 0,008 € et 0,7 s ; C, 97 % à 0,012 € et 1,4 s. Les exigences sont succès ≥ 94 % et p95 ≤ 1 s. En traitant les mesures comme exactes, lequel retenir ? <!--anki:6338353134376464616165373434383961373639663166333263396561616539-->
?
**B** respecte les deux contraintes et domine A : meilleure réussite, moindre coût et latence plus basse. C est exclu par la contrainte de latence malgré sa meilleure réussite.
```text
A : coût par succès = 0,010 / 0,94 ≈ 0,01064 €
B : coût par succès = 0,008 / 0,95 ≈ 0,00842 €
```
Ces rapports répartissent le coût total entre les succès ; ils ne modélisent pas une politique de retries. En pratique, vérifier incertitude, segments critiques et comparabilité de charge avant de conclure. Les seuils et tarifs sont fictifs.

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

- [OSI — Open Source AI Definition 1.0](https://opensource.org/ai/open-source-ai-definition)

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
