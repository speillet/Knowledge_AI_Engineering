# Statistiques pour décider en IA — Flashcards
Tags: #flashcards #ai-engineering #evals #statistiques #experimentation
<!-- summary: effet utile et significativité, p-valeur, intervalle de confiance, comparaison appariée, unité indépendante, zéro échec, tests multiples, puissance, causalité, biais de sélection et sample ratio mismatch. -->


À ne pas confondre : significativité statistique et importance pratique ? <!--anki:6261623137333138643566323438393961653766356166626633366465653635-->
?
La **significativité** indique une incompatibilité des observations avec une hypothèse nulle, selon le test et ses hypothèses. L'**importance pratique** dépend de l'amplitude du gain, de son coût et du risque acceptable.

Un gain minuscule peut devenir significatif avec beaucoup de données tout en ne justifiant pas une migration. Fixer un effet minimal utile avant l'expérience, puis rapporter estimation et intervalle de confiance. Un résultat incertain demande une décision explicitant cette incertitude, pas une lecture binaire « p inférieur à 0,05 donc déployer ».

---

Que signifie une p-valeur de 0,03 dans une comparaison de modèles ? <!--anki:6561656235626662376234663463343561326563666435336662613531643437-->
?
Sous l'**hypothèse nulle** et les hypothèses du test, c'est la probabilité d'obtenir une statistique au moins aussi extrême que celle observée. Ce n'est ni la probabilité que l'hypothèse nulle soit vraie ni 97 % de chances que le nouveau modèle soit meilleur.

La conclusion dépend du protocole : indépendance, appariement, arrêt et nombre de comparaisons. Rapporter aussi la différence mesurée et son intervalle. Une p-valeur calculée après sélection opportuniste de la métrique n'a plus l'interprétation du test initialement prévu.

---

Comment interpréter un intervalle de confiance fréquentiste à 95 % ? <!--anki:6330313635323635663539613431626362643534653664386333346364326337-->
?
Une **procédure** valide produirait des intervalles contenant le paramètre réel dans 95 % des répétitions du plan d'échantillonnage. Après observation, ce n'est pas une probabilité de 95 % attribuée au paramètre fixe à l'intérieur de cet intervalle particulier.

L'intervalle traduit l'incertitude due à l'échantillonnage selon les hypothèses retenues. Il ne couvre pas automatiquement biais de collecte, labels faux ou nouvelle population. Un intervalle très étroit peut donc décrire avec précision une mesure qui ne répond pas à la bonne question.

---

Pourquoi comparer deux modèles sur les mêmes cas avec un bootstrap apparié ? <!--anki:3561393263656665373738353430323562613063313138353064373863623366-->
?
L'**appariement** exploite le fait qu'une même question peut être difficile pour les deux modèles. Rééchantillonner les mêmes indices pour leurs deux résultats et recalculer la différence conserve cette dépendance.

En rééchantillonnant chaque modèle séparément, on perd l'information commune. Choisir l'unité indépendante pertinente : document, utilisateur ou client, plutôt que chaque token. Le bootstrap estime l'incertitude pour le protocole représenté ; il ne répare pas un test contaminé ni un échantillon de cas faciles. Pour le temps, préserver les dépendances avec une méthode adaptée.

---

Pourquoi 10 000 messages provenant de 100 utilisateurs ne font-ils pas 10 000 observations indépendantes ? <!--anki:3839666662323831373966353433353962363863303232623731316562663464-->
?
Les messages d'un utilisateur partagent préférences, contexte et parfois mémoire. Les traiter comme indépendants peut **sous-estimer l'incertitude**, surtout si l'expérience assigne une variante par utilisateur.

Choisir une métrique et une analyse compatibles avec l'unité d'assignation : agrégation par utilisateur, méthode tenant compte des groupes ou rééchantillonnage des utilisateurs. Préciser aussi la pondération : l'utilisateur moyen et le message moyen ne représentent pas la même cible. Un utilisateur très actif ne doit pas dominer le résultat par accident.

---

Calcul : zéro échec sur 300 essais permet-il d'annoncer un risque inférieur à 0,1 % ? <!--anki:3137303038393761333632613462623439663963373835316539313636323331-->
?
**Non.** Pour des essais de Bernoulli indépendants, représentatifs et de risque constant, une borne supérieure unilatérale à 95 % après zéro échec vaut :
```text
p_max = 1 − 0,05^(1/n)
Pour n = 300 : p_max ≈ 0,00994 ≈ 1 %
Approximation : 3/n ; viser 0,1 % demande environ 3 000 essais sans échec.
```
Ce calcul ne garantit rien sur un scénario absent des essais. Des variantes quasi identiques d'une même question n'apportent pas nécessairement autant d'information que des cas indépendants.

---

Quel risque crée la recherche du meilleur résultat parmi 20 tests ? <!--anki:3937313162656165326133633434623638303530316139656434323565313036-->
?
Sous 20 hypothèses nulles vraies, avec tests indépendants chacun au seuil de 5 %, la probabilité d'au moins un faux positif vaut **1 − 0,95²⁰ ≈ 64 %**. Sélectionner seulement le résultat favorable masque ce mécanisme.

Définir la famille de comparaisons et l'objectif avant l'analyse. Bonferroni utilise par exemple un seuil de 0,05 / 20 = 0,0025 pour contrôler le risque familial, sans exiger l'indépendance. Il peut être conservateur ; une analyse exploratoire doit être distinguée d'une confirmation sur de nouvelles données.

---

À ne pas confondre : absence de différence significative et équivalence ? <!--anki:6232346235343439363038313462316238303165366164336238303435666634-->
?
Un test non significatif peut simplement manquer de **puissance**. Il ne démontre pas que les systèmes sont équivalents. Une démarche d'équivalence ou de non-infériorité définit à l'avance une marge acceptable et utilise une procédure adaptée.

Pour remplacer un modèle par un autre moins cher, fixer la perte de qualité tolérable et examiner la borne pertinente de l'intervalle de différence. Avec un intervalle de −8 à +3 points, un gain de coût ne permet pas d'affirmer que la qualité est conservée à un point près.

---

Comment choisir l'unité de randomisation d'une expérience IA ? <!--anki:6561363937623036623037383435316462343638333131303438633135646137-->
?
Choisir la plus petite unité limitant la **contamination entre variantes** : utilisateur si l'historique persiste, équipe si les réponses sont partagées, parfois requête pour une tâche sans effet durable. L'analyse doit respecter ce regroupement.

Une assignation stable évite de changer la variante d'un utilisateur en cours de conversation. Les interactions entre unités peuvent encore violer les hypothèses, par exemple si les équipes partagent des documents générés. La randomisation par utilisateur est un choix fréquent, pas une règle suffisante dans tous les produits.

---

Qu'est-ce qu'un sample ratio mismatch dans un A/B test ? <!--anki:3461313736393834306564303434356361333635356164373663373737616163-->
?
Un **SRM** est un écart statistiquement suspect entre les effectifs observés par variante et le ratio d'assignation prévu. Un test conçu à 50/50 ne doit pas être interprété naïvement si la collecte fait disparaître davantage d'utilisateurs d'un bras.

Examiner randomisation, éligibilité, exposition, télémétrie et filtres avant de comparer les résultats métier. Un écart brut minuscule est normal ; l'évaluer selon les effectifs. Corriger les volumes par pondération sans comprendre leur origine peut laisser intact un biais de sélection.

---

Pourquoi une amélioration avant/après ne prouve-t-elle pas l'effet causal d'un nouveau modèle ? <!--anki:6434306138326366303238313434343462316566613436383833616232343231-->
?
Entre deux périodes changent souvent **population, saison, interface ou procédure métier**. Une hausse du taux de résolution peut venir de demandes plus simples plutôt que du modèle déployé.

Un groupe contrôle contemporain randomisé aide à isoler l'effet, si les hypothèses d'assignation et d'absence d'interférence sont plausibles. Sinon, documenter les facteurs concurrents et les hypothèses d'une méthode quasi expérimentale. Une corrélation entre un score offline et le résultat produit fournit un indice, pas une preuve que toute hausse de ce score créera de la valeur.

---

## Mises en situation

Mise en situation : la variante gagne sur les messages, mais l'expérience a été randomisée par utilisateur. Comment vérifies-tu le résultat ? <!--anki:3163653465626537633336373431626138343030376636393234326235336439-->
?
1. **Identifier l'unité cible** : message moyen ou utilisateur moyen.
2. **Contrôler les effectifs et l'assignation**, avant de calculer le gain.
3. **Analyser la dépendance** entre messages d'un même utilisateur.
4. **Recalculer l'incertitude** au niveau des groupes, avec une pondération explicite.
5. **Rapporter gain, intervalle et garde-fous**, sans sélectionner la méthode la plus favorable.

**Piège** : augmenter artificiellement la taille d'échantillon en comptant chaque message comme indépendant.

---

Mise en situation : une équipe annonce un agent fiable à 99,9 % après 300 tâches sans erreur. Que réponds-tu ? <!--anki:6636363934386436346566633437323362363333373236373030636335616566-->
?
1. **Définir l'échec** : résultat métier, permissions, effets externes et cas abandonnés.
2. **Vérifier représentativité et indépendance** des tâches testées.
3. **Calculer la borne du risque** : environ 1 % à 95 % sous hypothèse binomiale.
4. **Dimensionner la suite** selon le risque visé, sans changer le protocole après chaque résultat.
5. **Ajouter des scénarios ciblés** pour les risques rares, puis prévoir surveillance et repli.

**Piège** : transformer une absence d'incident observé en garantie de fiabilité universelle.

---

Mise en situation : parmi 40 prompts, un seul progresse de deux points sur le test historique. Peut-on le déployer ? <!--anki:3366393030326464393061373466323039333663636239303535653537303661-->
?
1. **Considérer ce jeu comme sélectionné** : il a servi à choisir le gagnant.
2. **Examiner les erreurs appariées** et les changements par segment.
3. **Documenter tous les essais**, ainsi que le coût et les métriques recherchées.
4. **Confirmer sur un jeu indépendant** dimensionné pour le gain utile, ou un protocole confirmatoire adapté.
5. **Décider selon valeur et incertitude**, puis appliquer les contrôles de déploiement habituels.

**Piège** : présenter le score maximal d'une recherche comme une mesure indépendante de généralisation.

---

## Sources
- [NIST — interprétation des intervalles de confiance](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm)
- [NIST — intervalles pour une proportion](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm)
- [NIST — comparaisons multiples et Bonferroni](https://www.itl.nist.gov/div898/handbook/prc/section4/prc473.htm)
- [SciPy — bootstrap et appariement](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)
- [Microsoft Research — diagnostic du sample ratio mismatch](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/)
- [Microsoft Research — inférence après sélection en A/B testing](https://www.microsoft.com/en-us/research/uploads/prod/2021/06/PostSelectionKDD2021.pdf)

- [ASA — principes d’interprétation des p-valeurs](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Microsoft Research — protocole, métriques et interférences](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/)
- [Microsoft Research — unité indépendante et analyse des A/B tests](https://www.microsoft.com/en-us/research/publication/trustworthy-analysis-of-online-a-b-tests-pitfalls-challenges-and-solutions/)
- [Microsoft Research — expérimentation et causalité](https://www.microsoft.com/en-us/research/publication/online-experimentation-at-microsoft/)

## Connexions
- [[94-evals-methodologie|Méthodologie d'évaluation]] — passer d'un score à une décision justifiée
- [[97-evals-online-ab-testing|A/B testing]] — vérifier la validité du protocole online
- [[172-validation-metriques-ml|Validation ML]] — comparer les modèles sans biais de sélection
- [[00-moc-ai-engineering|MOC AI Engineering]]
