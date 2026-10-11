# Atelier local — Décider à partir de métriques IA

Quatre exercices sur données fictives pour passer du rappel d'une formule à sa conséquence : prévalence, décision avec revue, choix de modèle sous contraintes et qualité du document complet. L'atelier utilise uniquement la bibliothèque standard de Python 3.9 ou plus récent, sans API ni GPU.

## Déroulement

Depuis la racine du dépôt, afficher les énoncés :

```bash
python3 examples/decisions-ia/atelier_decisions.py --questions
```

Résoudre sur papier en donnant formule, unités et hypothèses. Afficher ensuite les résultats contrôlés :

```bash
python3 examples/decisions-ia/atelier_decisions.py
```

| Exercice | Résultat à expliquer | Fiches associées |
| --- | --- | --- |
| Prévalence | Une précision de 94,7 % tombe à 15,4 % quand les positifs passent de 50 % à 1 %, avec TPR et FPR supposés constants | [Validation ML](../../170-ml-classique/172-validation-metriques-ml.md) |
| Revue humaine | Pour p = 0,02 ; 0,10 ; 0,60 ; 0,99, les décisions de moindre coût sont négatif, revue, revue, positif | [Calibration et abstention](../../170-ml-classique/173-calibration-incertitude-abstention.md) |
| Modèles | B domine A ; C est éliminé par la latence. Le coût de B vaut environ 0,00842 € par succès | [Choix de modèles](../../140-system-design-produit/146-choix-modeles.md) |
| Documents | Deux lots à 99 % d'exactitude par champ ont respectivement 80 % et 99 % de documents complets corrects | [Vision-langage](../../160-multimodal-edge/161-modeles-vision-langage.md) |

## Variantes pour vérifier le transfert

1. **Prévalence** : remplacer 1 % par 2 %. Les 180 vrais positifs et 490 faux positifs donnent environ 26,9 % de précision. Expliquer pourquoi le rappel reste constant seulement dans le modèle de l'exercice.
2. **Revue** : si elle coûte 5 unités, avec les autres hypothèses inchangées, elle n'est jamais la décision de moindre coût : le meilleur coût entre positif et négatif ne dépasse pas 3,6. Si elle peut se tromper, ajouter son coût d'erreur attendu avant de décider.
3. **Modèles** : relâcher le plafond de latence à 1,5 s. B et C deviennent non dominés : C gagne en réussite, B en coût et latence. Il faut un arbitrage produit supplémentaire.
4. **Documents** : demander seulement dix champs indépendants corrects chacun à 99 % donne `0,99^10 ≈ 90,4 %` de réussite complète. Expliquer pourquoi ce calcul ne décrit pas forcément les deux lots déterministes de l'atelier.

**Preuve de maîtrise** : produire une courte décision avec les données utilisées, le dénominateur, une hypothèse dont dépend la conclusion et ce qu'il faudrait mesurer sur un service réel.

## Limites

Les coûts, probabilités et performances sont fictifs et les vérifications portent sur ces exemples. L'atelier n'estime pas l'incertitude, ne valide pas la calibration d'un modèle et ne mesure pas la qualité de la revue humaine. Les deux lots documentaires montrent précisément pourquoi un score par champ ne suffit pas à déduire le succès complet.
