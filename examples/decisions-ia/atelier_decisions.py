#!/usr/bin/env python3
"""Quatre exercices de décision IA, avec données fictives et bibliothèque standard.

python3 examples/decisions-ia/atelier_decisions.py --questions
python3 examples/decisions-ia/atelier_decisions.py

Les vérifications portent sur les résultats pédagogiques annoncés. Aucun modèle
n'est entraîné et aucune mesure de production n'est réalisée.
"""

import argparse
import math


QUESTIONS = """1. Prévalence : sur 10 000 cas, TPR = 90 % et FPR = 5 %, supposés
stables. Calculer VP, FP et précision avec 50 % puis 1 % de positifs.

2. Décision : probabilités calibrées p = 0,02 ; 0,10 ; 0,60 ; 0,99.
Un faux positif coûte 4 unités, un faux négatif 36, les décisions correctes
sont gratuites. Une revue parfaite coûte 1 unité, avec capacité suffisante.
Pour chaque p, choisir positif, négatif ou revue selon le coût attendu.

3. Modèles : même test et même charge, mesures traitées comme exactes.
A : succès 94 %, 0,010 €/requête, p95 0,8 s.
B : succès 95 %, 0,008 €/requête, p95 0,7 s.
C : succès 97 %, 0,012 €/requête, p95 1,4 s.
Exigences : succès >= 94 % et p95 <= 1 s. Retenir le candidat non dominé
parmi les candidats admissibles, puis calculer son coût par succès.

4. Documents : 100 documents de 20 champs, avec exactement 20 erreurs.
Lot dispersé : une erreur dans chacun des vingt premiers documents.
Lot concentré : vingt erreurs dans le premier document uniquement.
Calculer l'exactitude par champ et la réussite documentaire dans chaque lot.
Comparer à l'hypothèse de vingt champs indépendants, corrects chacun à 99 %.
"""


def precision_selon_prevalence():
    for prevalence, expected in ((0.50, (4500, 250)), (0.01, (90, 495))):
        true_positive = 10_000 * prevalence * 0.90
        false_positive = 10_000 * (1 - prevalence) * 0.05
        assert (true_positive, false_positive) == expected
        precision = true_positive / (true_positive + false_positive)
        print(f"  prévalence {prevalence:.0%} : VP={true_positive:.0f}, "
              f"FP={false_positive:.0f}, précision={precision:.2%}")
    print("  Le rappel reste 90 % dans l'hypothèse ; la précision change.")


def decisions_avec_revue():
    expected = ("négatif", "revue", "revue", "positif")
    for p, expected_decision in zip((0.02, 0.10, 0.60, 0.99), expected):
        costs = {"positif": (1 - p) * 4, "négatif": p * 36, "revue": 1.0}
        decision = min(costs, key=costs.get)
        assert decision == expected_decision
        print(f"  p={p:.2f} : {decision}, coût attendu={costs[decision]:.2f}")
    print("  Ces décisions supposent probabilités calibrées et revue parfaite.")


def choix_sous_contraintes():
    # nom, taux de succès, euros par requête, p95 en secondes
    candidates = (
        ("A", 0.94, 0.010, 0.8),
        ("B", 0.95, 0.008, 0.7),
        ("C", 0.97, 0.012, 1.4),
    )
    eligible = [m for m in candidates if m[1] >= 0.94 and m[3] <= 1.0]

    def dominates(a, b):
        weakly_better = a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]
        strictly_better = a[1] > b[1] or a[2] < b[2] or a[3] < b[3]
        return weakly_better and strictly_better

    frontier = [m for m in eligible if not any(dominates(other, m)
                                              for other in eligible)]
    assert [m[0] for m in eligible] == ["A", "B"]
    assert [m[0] for m in frontier] == ["B"]
    winner = frontier[0]
    cost_per_success = winner[2] / winner[1]
    assert math.isclose(cost_per_success, 0.008421052631578947)
    print(f"  admissibles : A, B ; front de Pareto : {winner[0]}")
    print(f"  B : {cost_per_success:.5f} € par succès, contre "
          f"{candidates[0][2] / candidates[0][1]:.5f} € pour A")
    print("  Le rapport répartit le coût total entre succès ; il ne simule pas des retries.")


def qualite_documentaire():
    dispersed = [[True] * 20 for _ in range(100)]
    concentrated = [[True] * 20 for _ in range(100)]
    for document in dispersed[:20]:
        document[0] = False
    concentrated[0] = [False] * 20
    for name, documents, expected_success in (
        ("dispersé", dispersed, 0.80),
        ("concentré", concentrated, 0.99),
    ):
        field_accuracy = sum(sum(doc) for doc in documents) / 2000
        document_success = sum(all(doc) for doc in documents) / len(documents)
        assert math.isclose(field_accuracy, 0.99)
        assert math.isclose(document_success, expected_success)
        print(f"  lot {name} : champs={field_accuracy:.1%}, "
              f"documents complets={document_success:.1%}")
    independent_success = 0.99 ** 20
    assert math.isclose(independent_success, 0.8179069375972308)
    print(f"  hypothèse indépendante : {independent_success:.1%} de documents complets")
    print("  Une même exactitude par champ peut cacher des réussites documentaires différentes.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", action="store_true",
                        help="afficher les énoncés sans les résultats")
    args = parser.parse_args()
    print(QUESTIONS)
    if args.questions:
        return
    for title, exercise in (
        ("1. Précision et prévalence", precision_selon_prevalence),
        ("2. Décision avec revue", decisions_avec_revue),
        ("3. Choix sous contraintes", choix_sous_contraintes),
        ("4. Qualité du document complet", qualite_documentaire),
    ):
        print(title)
        exercise()
        print()
    print("Quatre exercices vérifiés. Modifier une hypothèse sur brouillon pour tester le transfert.")


if __name__ == "__main__":
    main()
