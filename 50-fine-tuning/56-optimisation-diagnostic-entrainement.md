# Optimisation & diagnostic d'entraînement — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #optimisation #deep-learning
Vérifié le : 7 octobre 2026
<!-- summary: perte et métrique métier, rétropropagation, learning rate, AdamW, courbes d'apprentissage, micro-lot de diagnostic, accumulation normalisée, clipping, précision mixte, modes PyTorch et masquage des labels. -->


À ne pas confondre : perte d'entraînement et métrique métier ? <!--anki:3036653364613531613036643462383261306238306563643263626633323664-->
?
La **perte** fournit un signal optimisable pour ajuster les paramètres ; la **métrique métier** mesure le résultat attendu. Réduire l'entropie croisée des tokens ne garantit pas davantage de factures correctement extraites : les nombreux tokens de format peuvent masquer les erreurs sur les montants.

Suivre les deux sur des données séparées. Choisir le checkpoint selon un protocole de validation fixé à l'avance, avec des contrôles sur les capacités à préserver. Le test final ne sert pas à choisir l'époque.

---

Que calcule la rétropropagation et que fait ensuite l'optimiseur ? <!--anki:6436636137376438303539333461666561613434383366626636363431326131-->
?
La **rétropropagation** applique la règle de dérivation en chaîne au graphe de calcul pour obtenir les gradients de la perte par rapport aux paramètres. L'**optimiseur** utilise ces gradients pour modifier les paramètres ; calculer les gradients ne met donc pas les poids à jour.

Pour une descente simple : `θ ← θ − η × gradient`, avec `η` le taux d'apprentissage. Vérifier qu'un paramètre censé apprendre reçoit un gradient et change après un pas, surtout quand une partie du modèle est gelée.

---

Comment diagnostiquer un taux d'apprentissage inadapté ? <!--anki:6561326133613134343133333432623662343232386638313263303730373138-->
?
Un taux trop élevé peut produire oscillations, divergence ou pertes non finies ; un taux trop faible peut donner une progression presque invisible. Ces symptômes ne suffisent pas au diagnostic : données invalides, normalisation et erreurs de gradient peuvent les imiter.

Comparer quelques taux sur le même petit jeu, avec configuration et budget constants. Observer perte, norme des gradients et amplitude des mises à jour. Un warmup augmente progressivement le taux initial ; il ne répare pas un jeu de labels incorrect.

---

À ne pas confondre : pénalité L2 et weight decay avec AdamW ? <!--anki:6336613737626566316436333438373961643331303939363732366366636364-->
?
La **pénalité L2** ajoute un terme à la perte et donc aux gradients. **AdamW** découple la contraction des poids de la transformation adaptative du gradient. Avec un optimiseur adaptatif, les deux opérations ne sont généralement pas équivalentes.

Le coefficient doit être choisi sur validation, avec les autres hyperparamètres. Documenter quels paramètres sont concernés : les biais ou paramètres de normalisation peuvent être exclus selon la recette. Changer le nom de l'optimiseur sans contrôler ces groupes modifie l'expérience de manière peu visible.

---

Que révèlent les courbes de perte train et validation ? <!--anki:3166663138303666616463373437656362313930643736663964666163393461-->
?
Une perte train qui baisse tandis que la validation remonte suggère du **surapprentissage**. Deux pertes élevées peuvent signaler sous-apprentissage, mauvaise représentation ou pipeline défectueux. Comparer les courbes suppose une définition et une normalisation cohérentes de la perte.

Le dropout ou l'augmentation peuvent rendre le train plus difficile que la validation ; un écart n'est donc pas une preuve automatique. Relier les courbes aux erreurs concrètes et sélectionner un checkpoint sur validation avant de toucher au test final.

---

Pourquoi essayer de surapprendre un minuscule lot avant un entraînement coûteux ? <!--anki:3762373161633066643138653434356539613933386633356165346664373135-->
?
C'est un **test de fonctionnement du pipeline** : sur quelques exemples propres et fixes, un modèle suffisamment flexible devrait pouvoir réduire fortement sa perte. Un échec oriente vers labels, masques, gradients, paramètres gelés ou optimiseur avant d'accuser le volume de données.

Désactiver temporairement les augmentations et simplifier la régularisation pour ce diagnostic. La réussite prouve une capacité de mémorisation locale, pas la généralisation. Remettre ensuite les réglages normaux et évaluer sur des observations indépendantes.

---

Calcul : quel batch effectif avec 4 exemples par GPU, 8 accumulations et 2 répliques de données ? <!--anki:3738336431346232313232633463613062383536373334336530323864613530-->
?
Le batch effectif contient **4 × 8 × 2 = 64 exemples** par mise à jour, si chaque réplique traite des exemples distincts et que tous les micro-batches sont complets.

L'accumulation réalise plusieurs rétropropagations avant un pas d'optimiseur pour limiter la mémoire des activations. Elle ne rend pas nécessairement l'entraînement identique à un batch physique de 64 : BatchNorm, aléas et normalisation peuvent différer. Les GPU de parallélisme tensoriel ne multiplient pas ce batch s'ils travaillent sur les mêmes exemples.

---

Pourquoi normaliser l'accumulation par les tokens réellement supervisés ? <!--anki:3038623765386562653162313437636638396263653538333563393630396361-->
?
Si deux micro-batches contiennent respectivement **100 et 900 tokens supervisés**, moyenner leurs pertes moyennes leur donne le même poids, au lieu de pondérer chaque token également. Pour un objectif moyen par token, accumuler les sommes de pertes avec un dénominateur total cohérent.

Exclure padding et labels masqués de ce dénominateur. En distribué, tenir compte de la réduction des gradients et des comptes globaux. Diviser seulement par le nombre d'accumulations convient aux micro-batches de même poids, pas à toutes les séquences variables.

---

Que protège le gradient clipping et que ne corrige-t-il pas ? <!--anki:3863346663646530373037323462646161356639373431323631613365313931-->
?
Le **clipping par norme** réduit un gradient dont la norme dépasse un seuil, en préservant sa direction lorsqu'il s'agit d'un redimensionnement global. Il limite l'effet d'un pic sur la mise à jour.

Journaliser la norme avant clipping et sa fréquence : une activation permanente invite à rechercher taux excessif, exemples aberrants ou perte mal normalisée. Avec des gradients mis à l'échelle, retirer cette échelle avant de clipper. Le clipping ne transforme pas des NaN en gradients valides et ne remplace pas le diagnostic.

---

À ne pas confondre : model.eval() et désactivation des gradients dans PyTorch ? <!--anki:6236346430303366383035613432356262323136626233386134303039373262-->
?
**`model.eval()`** change le comportement de modules comme dropout et BatchNorm. **`torch.no_grad()`** désactive l'enregistrement des opérations pour le calcul de gradients dans son contexte. Ces mécanismes sont indépendants : l'un ne déclenche pas automatiquement l'autre.

Pour une validation habituelle, combiner le mode évaluation et l'absence de gradients, puis restaurer le mode entraînement. Oublier `eval()` peut rendre les scores instables ; oublier `no_grad()` peut gaspiller de la mémoire. Une validation qui exige des dérivées constitue un autre cas d'usage.

---

Pourquoi la précision mixte peut-elle produire des NaN pendant l'entraînement ? <!--anki:3133323837303666366362353464303239643633323432306562306365323231-->
?
Certaines opérations dépassent la plage numérique du format choisi, ou leurs gradients deviennent trop petits pour être représentés. Le **FP16** et le **BF16** n'ont pas la même plage d'exposants ; leur comportement dépend aussi des opérations conservées en FP32.

Localiser la première valeur non finie et comparer un petit cas en FP32. Le gradient scaling aide notamment contre le sous-flux en FP16, mais ne corrige ni une division par zéro ni des données invalides. Réduire le taux sans identifier l'origine peut seulement masquer le problème.

---

## Mises en situation

Mise en situation : la perte de ton fine-tuning baisse, mais les montants extraits deviennent moins exacts. Que vérifies-tu ? <!--anki:3266386265386562656466353437306239653631353866313939313538303162-->
?
1. **Vérifier les labels supervisés** : assistant, montants, padding et tokens de consigne.
2. **Comparer le rendu des exemples** au format utilisé en inférence, troncature comprise.
3. **Mesurer l'exactitude des champs** sur validation, séparément de la perte moyenne par token.
4. **Inspecter les erreurs** : unités, décimales, exemples contradictoires ou trop répétitifs.
5. **Comparer les checkpoints** à la baseline et conserver le test final indépendant.

**Piège** : prolonger l'entraînement uniquement parce que la courbe train descend.

---

Mise en situation : après activation de l'accumulation de gradients, la perte explose sur les documents longs. Comment isoles-tu le problème ? <!--anki:3765343861363266383932623462343161373831323964613165323166643334-->
?
1. **Figer un lot reproductible** contenant documents courts et longs.
2. **Compter les tokens supervisés** dans chaque micro-batch et vérifier la normalisation.
3. **Contrôler les pas** : remise à zéro au bon moment, un pas d'optimiseur après l'accumulation.
4. **Comparer les gradients** avec un batch physique équivalent si la mémoire le permet.
5. **Examiner la précision numérique** et le clipping seulement après cette comparaison.

**Piège** : modifier simultanément learning rate, batch et loss, puis attribuer le résultat à une seule cause.

---

Mise en situation : un entraînement ne mémorise même pas 16 exemples propres. Par où commences-tu ? <!--anki:6234643731646365363866633431306339643632633665313561616661393664-->
?
1. **Lire les entrées et labels réellement tensorisés**, avec les masques et décalages de cible.
2. **Vérifier que la perte dépend des prédictions**, sans détachement accidentel du graphe.
3. **Inspecter gradients et poids** avant et après un pas pour les paramètres entraînables.
4. **Simplifier le calcul** : FP32, pas d'augmentation, configuration minimale.
5. **Comparer quelques taux d'apprentissage**, puis réintroduire les optimisations une à une.

**Piège** : lancer davantage de GPU avant d'avoir démontré que le pipeline apprend.

---

## Sources
- [PyTorch — boucle d'optimisation](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html)
- [PyTorch — autograd et modes d'évaluation](https://docs.pytorch.org/docs/main/notes/autograd.html)
- [PyTorch — précision mixte et clipping](https://docs.pytorch.org/tutorials/recipes/recipes/amp_recipe.html)
- [PyTorch — CrossEntropyLoss et labels ignorés](https://docs.pytorch.org/docs/2.14/generated/torch.nn.CrossEntropyLoss.html)
- [Loshchilov & Hutter — Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101)

- [PyTorch — accumulation des gradients en précision mixte](https://docs.pytorch.org/docs/main/notes/amp_examples.html)

## Connexions
- [[51-fine-tuning-adaptation|Fine-tuning]] — diagnostiquer une adaptation avant de la complexifier
- [[54-entrainement-distribue|Entraînement distribué]] — batch effectif et réduction des gradients
- [[172-validation-metriques-ml|Validation ML]] — séparer sélection et estimation finale
- [[00-moc-ai-engineering|MOC AI Engineering]]
