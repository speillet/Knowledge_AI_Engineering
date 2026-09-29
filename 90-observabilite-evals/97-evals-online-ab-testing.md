# Evals online & A/B testing — Flashcards
Tags: #flashcards #ai-engineering #evals #ab-testing #production #llm

Pourquoi les evals offline ne suffisent-elles pas ?
?
Le jeu offline est **figé et incomplet** : il ne capture ni la **distribution réelle** des requêtes, ni leur **évolution**, ni l'effet sur les **utilisateurs** (satisfaction, rétention). Seule la mesure **en production** dit si le changement crée de la valeur.

---

Quels signaux de qualité collecter en production ?
?
- **Explicites** : pouces haut/bas, notes, commentaires — rares et biaisés vers les mécontents.
- **Implicites** : **reformulation** de la question, **copie** de la réponse, **acceptation** d'une suggestion de code, abandon, escalade vers un humain.
- **Automatiques** : [[95-llm-as-judge|juges]] sans référence sur un échantillon, validations de format, détecteurs.

---

Qu'est-ce qu'un A/B test sur une application LLM ?
?
Répartir **aléatoirement** les utilisateurs entre la version **A** (contrôle) et **B** (variante : prompt, modèle, retrieval), puis comparer une **métrique principale** définie **à l'avance**, avec un test statistique. La randomisation par **utilisateur** (et non par requête) évite qu'un même utilisateur voie les deux versions.

---

Qu'est-ce qu'une guardrail metric dans un A/B test ?
?
Une métrique qui **ne doit pas se dégrader** même si la métrique principale progresse : **latence p95, coût par requête, taux d'erreur, taux de refus, signalements de sécurité**. Une variante qui gagne 2 % de satisfaction mais double le coût peut être **rejetée**.

---

Qu'est-ce que le shadow testing ?
?
Envoyer le trafic réel **aussi** à la nouvelle version **sans montrer sa réponse** à l'utilisateur, puis comparer les sorties (juge, diff, métriques). **Aucun risque utilisateur**, mais il **double le coût** d'inférence et ne mesure **pas** l'effet sur le comportement des utilisateurs ([[112-cicd-modeles|shadow deployment]]).

---

À ne pas confondre : canary et A/B test ?
?
- **Canary** : exposer la nouvelle version à **un petit % du trafic** pour détecter **les pannes** (erreurs, latence) avant d'élargir — objectif **sécurité du déploiement**.
- **A/B test** : mesurer **statistiquement** laquelle des versions est **meilleure** — objectif **décision produit**.

---

Pourquoi faut-il fixer à l'avance la taille d'échantillon et la durée ?
?
Pour éviter le **peeking** : regarder le résultat tous les jours et **arrêter dès que c'est significatif** gonfle fortement le taux de faux positifs. On calcule la taille nécessaire (effet minimal détectable, puissance) avant de lancer, ou on utilise des **tests séquentiels** conçus pour le suivi continu.

---

Qu'est-ce que l'effet de nouveauté ?
?
Les utilisateurs réagissent au **changement lui-même** (curiosité, méfiance) plutôt qu'à sa qualité ; l'effet s'estompe en quelques jours ou semaines. D'où la nécessité de faire tourner le test **assez longtemps** et de regarder l'évolution de l'écart dans le temps.

---

Quelles métriques produit relier aux métriques LLM ?
?
Les **métriques business** que le système est censé améliorer : taux de **résolution sans humain** (support), **taux d'acceptation** des suggestions (code), **conversion**, **temps gagné**, rétention. Une métrique LLM (faithfulness) n'a de valeur que si elle **corrèle** avec l'une d'elles.

---

Comment boucler entre online et offline ?
?
1. Échantillonner les **échecs** détectés en ligne (feedback négatif, juge en échec).
2. Les **analyser** et les labelliser.
3. Les ajouter au **golden dataset** ([[94-evals-methodologie|non-régression]]).
4. Corriger, valider offline, redéployer en canary puis A/B.

C'est la [[153-data-flywheel-versioning|data flywheel]] appliquée aux evals.

---

Quelles précautions de confidentialité pour les evals online ?
?
Les traces contiennent des **données personnelles** : **consentement** ou base légale, **minimisation** et [[152-pii-confidentialite|masquage des PII]] avant relecture humaine, **durée de rétention** limitée, accès restreint aux annotateurs ([[154-rgpd-llm|RGPD]]).

---

Calcul : combien d'utilisateurs par bras pour détecter +2 points sur un taux de succès de 70 % ?
?
Règle de Lehr (risque α 5 %, puissance 80 %) :
```text
n ≈ 16 × p(1 − p) / δ²  =  16 × 0,7 × 0,3 / 0,02²  ≈ 8 400 par bras
```
Diviser l'effet cherché par 2 **multiplie par 4** l'échantillon : détecter +1 point demande ≈ 34 000 par bras. Si le trafic ne le permet pas, viser un effet plus gros, une métrique moins bruitée, ou s'appuyer sur les evals offline ([[114-reproductibilite-variance|variance]]).

---

## Mises en situation

Mise en situation : un chef de produit veut arrêter un A/B test au bout de deux jours parce que la variante gagne de 3 %. Que réponds-tu ?
?
1. **Expliquer le peeking** : regarder les résultats en continu et s'arrêter dès que c'est significatif gonfle fortement les faux positifs
2. **Rappeler le protocole** : taille d'échantillon et durée fixées **avant** le lancement, à partir de l'effet minimal à détecter
3. **Effet de nouveauté** : les premiers jours mesurent la réaction au changement, pas la qualité
4. **Vérifier les guardrail metrics** : latence p95, coût, taux d'erreur et de refus ne doivent pas se dégrader
5. **Alternative si l'urgence est réelle** : utiliser un test séquentiel, conçu pour le suivi continu

**Piège** : conclure sur une métrique choisie après coup parce qu'elle est favorable.

---

Mise en situation : tu veux changer le modèle de ton assistant sans risquer de dégrader l'expérience. Quelle séquence de validation mets-tu en place ?
?
1. **Offline d'abord** : golden dataset rejoué, comparaison appariée, seuils de non-régression ([[94-evals-methodologie|evals]])
2. **Shadow** : le trafic réel part aussi vers la nouvelle version, sans être montré, pour comparer les sorties. Le coût double pendant ce temps
3. **Canary** : un petit pourcentage d'utilisateurs, pour détecter les pannes, la latence et les erreurs
4. **A/B test** : décider avec une métrique principale définie à l'avance et des guardrail metrics
5. **Boucler** : les échecs détectés en ligne alimentent le golden dataset ([[153-data-flywheel-versioning|flywheel]])

**Piège** : passer directement au déploiement complet parce que « les evals offline sont bonnes ».

---

## Connexions
- [[94-evals-methodologie|Méthodologie d'évaluation]] — offline vs online
- [[112-cicd-modeles|CI/CD des modèles]] — canary, shadow, rollback
- [[113-monitoring-drift-feedback|Monitoring & feedback]] — boucle de feedback
- [[93-monitoring-inference|Monitoring de l'inférence]] — signaux de qualité sans vérité terrain
- [[114-reproductibilite-variance|Reproductibilité & variance]] — tests statistiques
- [[144-ux-ia-human-in-the-loop|UX de l'IA]] — concevoir la collecte de feedback
- [[00-moc-ai-engineering|MOC AI Engineering]]
