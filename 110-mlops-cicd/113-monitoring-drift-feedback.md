# Monitoring, drift & boucle de feedback — Flashcards
Tags: #flashcards #ai-engineering #mlops #monitoring #drift #llm
<!-- summary: data drift et concept drift, PSI et calcul, test KS sur gros volumes, dérive multivariée, distribution des scores, drift d'une app LLM et d'un RAG, qualité en production, boucle de feedback, quand ré-entraîner, annotation régulière, mises à jour des modèles API, alertes sur tendance et par segment. -->


À ne pas confondre : data drift et concept drift ? <!--anki:693a4558422d7246257a-->
?
- **Data drift** : la distribution des **entrées** change (nouveaux sujets, jargon)
- **Concept drift** : la **relation entrée → sortie attendue** change (le « bon » comportement évolue)

Exemple de data drift : davantage de demandes dans une nouvelle langue. Exemple de concept drift : une règle commerciale change et une ancienne réponse correcte devient fausse. Une distribution d'entrée stable n'exclut donc pas une baisse de qualité. Mesurer les deux séparément et rechercher la cause avant de modifier ou réentraîner le modèle.

---

Comment le Population Stability Index (PSI) mesure-t-il la dérive d'une variable ? <!--anki:3839353839393939643139353462396362656138386437353365636534333832-->
?
On découpe la variable en classes, souvent les déciles de la période de référence, puis on compare la proportion de référence *e* et la proportion actuelle *a* de chaque classe :
```text
PSI = Σ (a_i − e_i) × ln(a_i / e_i)
```
Repères usuels, hérités du scoring crédit : sous 0,1, population stable ; de 0,1 à 0,25, à surveiller ; au-delà de 0,25, dérive marquée. Ce sont des conventions, pas un test statistique.

Le résultat dépend du découpage. Une classe vide rend le logarithme infini : lisser les proportions par une petite constante. Le PSI est univarié : il ne voit ni un changement de corrélation entre variables, ni une baisse de performance.

---

Calcul : avec PSI = Σ (a − e) × ln(a / e), quel indice pour une variable dont les trois classes passent de 50 / 30 / 20 % à 40 / 30 / 30 % ? La population est-elle stable ? <!--anki:3938656564616631313236303437343839646338666166616664333161326363-->
?
```text
(0,40 − 0,50) × ln(0,40 / 0,50) = −0,10 × −0,223 ≈ 0,022
(0,30 − 0,30) × ln(1)            = 0
(0,30 − 0,20) × ln(0,30 / 0,20) =  0,10 ×  0,405 ≈ 0,041
PSI ≈ 0,063
```
Sous le repère de 0,1, on parlerait de population **stable**. Pourtant la dernière classe a gagné la moitié de son poids, de 20 à 30 %. Si elle regroupe les gros montants, où le modèle se trompe le plus, l'effet métier peut être important.

Un indice global se complète donc par l'examen des classes qui bougent et de leur part dans les erreurs du modèle.

---

Calcul : avec 100 000 observations dans chaque fenêtre, quel écart de Kolmogorov-Smirnov devient significatif à 5 %, si D_crit ≈ 1,36 × √((n + m) / (n × m)) ? Qu'en conclure ? <!--anki:3761623161306136393831653465323938323161346461613065613732366361-->
?
```text
D_crit ≈ 1,36 × √(200 000 / 10¹⁰) = 1,36 × 0,0045 ≈ 0,006
```
Un écart maximal de **0,6 point** entre les deux fonctions de répartition suffit à rejeter l'égalité. Sur de gros volumes, presque chaque variable « dérive » au sens du test, même quand l'écart n'a aucun effet.

À l'inverse, avec 50 observations par fenêtre, le seuil monte à 1,36 × √(100 / 2 500) ≈ 0,27 : une dérive importante passe inaperçue. La p-valeur dit si les distributions diffèrent, pas si l'écart compte. Suivre plutôt une taille d'effet, comme D, le PSI ou la distance de Wasserstein, avec un seuil métier.

---

Comment détecter une dérive multivariée que les contrôles variable par variable ne voient pas ? <!--anki:3963393735306536386535613433613239383466366437643030343639303937-->
?
Entraîner un **classifieur de domaine** : étiqueter 0 les exemples de la période de référence et 1 ceux de la période récente, puis mesurer son AUC en validation croisée. Une AUC proche de 0,5 signifie que les deux périodes sont indiscernables. Une AUC nettement supérieure signale un changement, et les importances de variables indiquent lesquelles le portent.

Exemple : l'âge et le revenu gardent chacun leur distribution, mais la combinaison « jeune et revenu élevé » triple. Exclure identifiants, horodatages et compteurs, qui séparent trivialement les périodes. L'AUC mesure la détectabilité du changement, pas son effet sur la performance.

---

Pourquoi surveiller la distribution des scores d'un modèle en plus de ses variables d'entrée ? <!--anki:3731316566643535353330663439373962336264626566383836366234356634-->
?
La **distribution des scores** résume les dérives qui comptent pour ce modèle : une variable peu utilisée peut bouger sans effet, alors qu'un déplacement des scores touche directement les décisions. Elle est disponible tout de suite, sans attendre les labels.

Suivre en particulier la **part au-dessus du seuil de décision** : si elle passe de 2 à 5 %, la file de revue humaine est multipliée par 2,5, même si la qualité reste correcte. Limite : des scores stables n'excluent pas une dérive de concept, où les mêmes scores correspondent à d'autres issues. Seuls les labels, même tardifs, la révèlent.

---

Comment le drift se manifeste-t-il sur une app LLM ? <!--anki:4477547a5d582b2a403a-->
?
Par une **dégradation silencieuse** : aucune erreur technique, mais des réponses de moins en moins pertinentes. Causes typiques :
- **Nouvelles questions** hors du périmètre prévu
- **Documents sources** qui changent
- **Modèle du fournisseur** mis à jour derrière un alias

Invisible sans **evals continues** sur des échantillons de production.

Pour repérer les nouveaux sujets avant la baisse des scores, suivre la **part des questions éloignées de tous les groupes connus** dans l'espace des embeddings : de 3 à 12 % après un lancement, le périmètre a changé. Un changement de modèle chez le fournisseur se voit plutôt dans la forme : longueur, JSON invalide, refus.

---

Comment monitorer la qualité d'une application LLM en production ? <!--anki:786d2e5876493b586624-->
?
- **Scores sur échantillons** par un juge calibré ([[95-llm-as-judge|LLM-as-a-judge]])
- **Feedback utilisateur** explicite et implicite (reformulations, abandons)
- **Taux de refus** et d'**erreurs d'outils**
- **Validations automatiques** : format, citations présentes

Tout est rattaché aux [[91-langfuse-observabilite|traces]], et **segmenté** (par sujet, langue, client) : une moyenne stable peut cacher un segment qui s'effondre.

Dimensionner l'échantillon jugé **par segment**, pas globalement. 1 000 jugements par semaine répartis sur 20 segments n'en laissent que 50 chacun : sur un taux de 80 %, l'incertitude atteint environ ±11 points ([[114-reproductibilite-variance|variance]]). Concentrer les jugements sur les segments à fort risque, et compléter par les validations automatiques, qui couvrent tout le trafic.

---

Qu'est-ce que la boucle de feedback d'une application LLM ? <!--anki:7568493c4c666036326e-->
?
```text
traces prod → curation → golden datasets enrichis
→ evals plus fidèles → prompts/fine-tuning améliorés
```
Les données de production **nourrissent** l'amélioration continue.

La **curation** transforme un signal brut en exemple exploitable : vérifier l'erreur, enlever les données inutiles, produire une référence et choisir le bon jeu. Garder un test indépendant évite d'optimiser uniquement les incidents déjà vus. Mesurer après déploiement si la correction améliore réellement l'usage sans dégrader d'autres segments.

---

Quand réentraîner ou fine-tuner à nouveau un modèle en production ? <!--anki:69216450773565735339-->
?
**Sur signal**, ou à un rythme justifié par l'arrivée régulière de labels ([[117-pipelines-entrainement-continu|planifié ou déclenché]]) :
- Chute des scores sur un segment
- Drift des entrées détecté
- Nouveaux cas d'usage ou nouvelles catégories
- Nouveau modèle de base plus performant

Avant de ré-entraîner, vérifier que le problème ne se règle pas plus simplement : prompt, retrieval ou fraîcheur de l'index ([[51-fine-tuning-adaptation|fine-tuning]]).

Vérifier aussi que le signal ne vient pas d'un incident de données : réentraîner sur une source cassée fait apprendre l'erreur au modèle. Le réentraînement produit un **candidat** ; sa mise en production reste soumise à la comparaison avec la version en place.

---

Quel est l'équivalent du drift pour un système RAG ? <!--anki:623f3a36415d4739725d-->
?
Un RAG peut dériver à plusieurs niveaux : **sources obsolètes**, index mal synchronisé, changement des questions, permissions modifiées ou perte de rappel après changement d'embeddings. La fraîcheur est donc une cause de dérive, pas son unique équivalent.

Suivre dates d'ingestion, suppressions, couverture des questions et qualité des passages récupérés. Si la bonne source existe mais n'est plus retrouvée, ré-ingérer davantage ne suffit pas : vérifier index, filtres, découpage et modèle de recherche ([[22-rag-avance|RAG en production]]).

---

Pourquoi les mises à jour des modèles API sont-elles un risque ? <!--anki:4a50656f363156493461-->
?
Le provider **met à jour ou déprécie** les modèles : le comportement change sans commit chez vous → **épingler les versions** et re-jouer les evals à chaque changement.

Un alias stable peut pointer vers une version différente, et un identifiant daté peut finir par être retiré. Maintenir une procédure de migration : comparer sur le même jeu d'evals, vérifier formats et outils, déployer progressivement et prévoir une solution de repli. L'épinglage réduit les changements implicites sans supprimer les dépréciations.

---

Quel rôle pour l'humain dans la boucle de production ? <!--anki:695e2a5b4b652e41353c-->
?
**Annoter des échantillons** et **revoir les cas limites** : l'humain reste la source de vérité. Ses annotations servent à la fois à mesurer la qualité, à **calibrer les juges automatiques** et à enrichir le golden dataset.

Pour tenir dans le temps : un volume fixe et régulier (par exemple 50 traces par semaine), choisi par échantillonnage plutôt qu'au hasard des signalements ([[151-donnees-curation-annotation|annotation]]).

---

Comment alerter sur une baisse de qualité d'une application LLM en production ? <!--anki:724b5141763b4c37746b-->
?
Comme sur la disponibilité : des **seuils** sur les scores de qualité, les taux de refus et d'erreurs, les latences, **par segment**, reliés aux [[64-metriques-slo-inference|SLO]].

Précautions : alerter sur une **tendance** (moyenne glissante sur plusieurs heures) plutôt que sur un point isolé, car les scores d'échantillons sont bruités, et joindre à l'alerte des **exemples de traces** pour diagnostiquer vite.

---

## Mises en situation

Mise en situation : ton assistant RH fonctionnait bien depuis six mois. Depuis trois semaines, les utilisateurs le trouvent « à côté de la plaque », sans qu'aucun déploiement n'ait eu lieu. Quelles causes explores-tu ? <!--anki:433d3b33593952674f29-->
?
1. **Drift des entrées** : de nouveaux sujets arrivent (réforme, nouvelle politique interne) et sortent du périmètre couvert
2. **Fraîcheur de l'index** : les documents ont changé, mais la ré-ingestion n'a pas suivi ([[22-rag-avance|RAG en prod]])
3. **Mise à jour côté fournisseur** : le modèle derrière l'alias a changé, sans commit chez toi
4. **Mesurer** : scores sur échantillon, taux de refus, feedback, segmentés par sujet
5. **Corriger puis prévenir** : épingler les versions, automatiser la ré-ingestion, alerter sur les scores par segment

**Piège** : conclure à une régression du modèle sans avoir regardé la fraîcheur des données.

---

Mise en situation : tu veux transformer les échecs de production en amélioration continue, sans y passer tes semaines. Comment organises-tu la boucle ? <!--anki:7732497b69286a71417d-->
?
1. **Capter** : feedback négatif, échecs de validation, faible confiance, escalades ([[93-monitoring-inference|signaux]])
2. **Échantillonner** plutôt que tout traiter, en priorisant les segments à fort volume ou à fort risque
3. **Annoter** un lot régulier avec un expert métier, ce qui calibre aussi les juges automatiques
4. **Verser** ces cas au golden dataset, en distinguant non-régression et cas durs ([[94-evals-methodologie|evals]])
5. **Déclencher les corrections sur signal**, pas au calendrier : prompt, retrieval, ou fine-tuning selon la cause

**Piège** : collecter du feedback sans jamais rien en faire, ce qui décourage les utilisateurs de le donner.

---

Mise en situation : ton tableau de bord de dérive affiche quarante variables en rouge chaque lundi, et l'équipe a cessé de le regarder. Comment le rends-tu utile ? <!--anki:3732316464366435656539343430386639376433366131613165306561653466-->
?
1. **Remplacer les p-valeurs** par des tailles d'effet, avec des seuils fixés selon l'impact métier.
2. **Prioriser selon le modèle** : variables importantes, distribution des scores, part au-dessus du seuil de décision.
3. **Choisir une référence comparable** : même jour de la semaine ou même saison, pour ne pas alerter sur un rythme normal.
4. **Vérifier d'abord le pipeline** : schéma, volume, unités, avant de conclure à une évolution réelle ([[157-contrats-qualite-donnees|dérive ou incident]]).
5. **Relier chaque alerte** à un propriétaire, à une estimation d'impact et à une action prévue.

**Piège** : relever tous les seuils jusqu'au silence, et manquer la vraie dérive.

---

## Connexions
- [[91-langfuse-observabilite|Langfuse]] — traces, scores et datasets de prod
- [[92-chainforge-evals-prompts|Evals]] — les instruments de mesure
- [[112-cicd-modeles|CI/CD des modèles]] — redéployer après correction
- [[51-fine-tuning-adaptation|Fine-tuning]] — la réponse au drift comportemental
- [[22-rag-avance|RAG avancé]] — fraîcheur de l'index
- [[93-monitoring-inference|Monitoring de l'inférence]] — validations et signaux de qualité en production
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — SLO et métriques d'un agent
- [[153-data-flywheel-versioning|Data flywheel]] — boucler sur les échecs
- [[97-evals-online-ab-testing|Evals online]] — signaux de production
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps]] — cycle de vie et versioning des systèmes LLM
- [[114-reproductibilite-variance|Reproductibilité & variance]] — non-déterminisme et statistiques d'evals
- [[157-contrats-qualite-donnees|Qualité opérationnelle]] — distinguer incident de données et dérive réelle
- [[159-donnees-temporelles-features|Données temporelles]] — interpréter les retards et labels incomplets
- [[173-calibration-incertitude-abstention|Calibration, incertitude & abstention]] — surveiller la validité des probabilités
- [[176-detection-anomalies|Détection d'anomalies]] — distinguer incident et évolution de la référence
- [[117-pipelines-entrainement-continu|Pipelines d'entraînement & entraînement continu]] — du signal de dérive au réentraînement contrôlé
- [[00-moc-ai-engineering|MOC AI Engineering]]
