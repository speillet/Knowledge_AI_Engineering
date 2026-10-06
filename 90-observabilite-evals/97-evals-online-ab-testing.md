# Evals online & A/B testing — Flashcards
Tags: #flashcards #ai-engineering #evals #ab-testing #production #llm
<!-- summary: signaux explicites et implicites, A/B test, guardrail metrics, shadow testing, canary ou A/B, peeking, effet de nouveauté, métriques produit, boucle online-offline, confidentialité, calcul de la taille d'échantillon. -->


Pourquoi les evals offline ne suffisent-elles pas ? <!--anki:6b62287a2a6d53773a7b-->
?
Le jeu offline est **figé et incomplet** : il ne capture ni la **distribution réelle** des requêtes, ni leur **évolution**, ni l'effet sur les **utilisateurs** (satisfaction, rétention). Seule la mesure **en production** dit si le changement crée de la valeur.

---

Quels signaux de qualité collecter en production ? <!--anki:7957626f517230716c-->
?
- **Explicites** : pouces haut/bas, notes, commentaires — rares et biaisés vers les mécontents.
- **Implicites** : **reformulation** de la question, **copie** de la réponse, **acceptation** d'une suggestion de code, abandon, escalade vers un humain.
- **Automatiques** : [[95-llm-as-judge|juges]] sans référence sur un échantillon, validations de format, détecteurs.

---

Qu'est-ce qu'un A/B test sur une application LLM ? <!--anki:4c3830253b43347c7138-->
?
Répartir **aléatoirement** les utilisateurs entre la version **A** (contrôle) et **B** (variante : prompt, modèle, retrieval), puis comparer une **métrique principale** définie **à l'avance**, avec un test statistique. La randomisation par **utilisateur** (et non par requête) évite qu'un même utilisateur voie les deux versions.

---

Qu'est-ce qu'une guardrail metric dans un A/B test ? <!--anki:6f6666764a3551592569-->
?
Une métrique qui **ne doit pas se dégrader** même si la métrique principale progresse : **latence p95, coût par requête, taux d'erreur, taux de refus, signalements de sécurité**. Une variante qui gagne 2 % de satisfaction mais double le coût peut être **rejetée**.

---

Qu'est-ce que le shadow testing ? <!--anki:4a6f2b436e3958626d33-->
?
Le **shadow testing** envoie une copie du trafic à une variante dont la réponse reste invisible à l'utilisateur. Il aide à comparer sorties, erreurs et latence avec la version active sans remplacer ses réponses.

Isoler ou simuler les outils d'écriture et vérifier le traitement des données ainsi que la charge supplémentaire. Le coût augmente selon le volume dupliqué et les modèles, sans facteur universel. Le test ne mesure pas la satisfaction ou le comportement causés par la réponse cachée ; un test exposé reste nécessaire pour cela ([[112-cicd-modeles|shadow deployment]]).

---

À ne pas confondre : canary et A/B test ? <!--anki:703c247d5246697c554a-->
?
- **Canary** : exposer la nouvelle version à **un petit % du trafic** pour détecter **les pannes** (erreurs, latence) avant d'élargir — objectif **sécurité du déploiement**.
- **A/B test** : mesurer **statistiquement** laquelle des versions est **meilleure** — objectif **décision produit**.

---

Pourquoi faut-il fixer à l'avance la taille d'échantillon et la durée ? <!--anki:643c68246355213a393a-->
?
Pour éviter le **peeking** : regarder le résultat tous les jours et **arrêter dès que c'est significatif** gonfle fortement le taux de faux positifs. On calcule la taille nécessaire (effet minimal détectable, puissance) avant de lancer, ou on utilise des **tests séquentiels** conçus pour le suivi continu.

---

Qu'est-ce que l'effet de nouveauté dans un A/B test ? <!--anki:782c3c2e4b3e40457e26-->
?
Les utilisateurs réagissent au **changement lui-même** (curiosité, méfiance) plutôt qu'à sa qualité ; l'effet s'estompe en quelques jours ou semaines. D'où la nécessité de faire tourner le test **assez longtemps** et de regarder l'évolution de l'écart dans le temps.

---

Quelles métriques produit relier aux métriques LLM ? <!--anki:6f4d4b523c2d764c7c4c-->
?
Les **métriques business** que le système est censé améliorer : taux de **résolution sans humain** (support), **taux d'acceptation** des suggestions (code), **conversion**, **temps gagné**, rétention. Une métrique LLM (faithfulness) n'a de valeur que si elle **corrèle** avec l'une d'elles.

---

Comment boucler entre online et offline ? <!--anki:4f572f26404b2e515241-->
?
1. Échantillonner les **échecs** détectés en ligne (feedback négatif, juge en échec).
2. Les **analyser** et les labelliser.
3. Les ajouter au **golden dataset** ([[94-evals-methodologie|non-régression]]).
4. Corriger, valider offline, redéployer en canary puis A/B.

C'est la [[153-data-flywheel-versioning|data flywheel]] appliquée aux evals.

---

Quelles précautions de confidentialité pour les evals online ? <!--anki:483c79285a236e7d7a47-->
?
Définir la **finalité et la base légale appropriée**, dont le consentement peut être une option selon le contexte ; la collecte pour le service n'autorise pas automatiquement toute réutilisation. Limiter les contenus collectés, [[152-pii-confidentialite|masquer les données personnelles]] et restreindre l'accès aux annotateurs.

Fixer une durée de rétention et vérifier les sous-traitants, transferts et possibilités d'effacement. La pseudonymisation ne rend pas nécessairement les traces anonymes. Documenter le protocole avant de transmettre des conversations à un juge externe ou à une équipe de relecture ([[154-rgpd-llm|RGPD]]).

---

Calcul : combien d'utilisateurs par bras pour détecter +2 points sur un taux de succès de 70 % ? <!--anki:51317d402a63415f794c-->
?
Règle de Lehr (risque α 5 %, puissance 80 %) :
```text
n ≈ 16 × p(1 − p) / δ²  =  16 × 0,7 × 0,3 / 0,02²  ≈ 8 400 par bras
```
Diviser l'effet cherché par 2 **multiplie par 4** l'échantillon : détecter +1 point demande ≈ 34 000 par bras. Si le trafic ne le permet pas, viser un effet plus gros, une métrique moins bruitée, ou s'appuyer sur les evals offline ([[114-reproductibilite-variance|variance]]).

---

## Mises en situation

Mise en situation : un chef de produit veut arrêter un A/B test au bout de deux jours parce que la variante gagne de 3 %. Que réponds-tu ? <!--anki:6a62463a447e37326561-->
?
1. **Expliquer le peeking** : regarder les résultats en continu et s'arrêter dès que c'est significatif gonfle fortement les faux positifs
2. **Rappeler le protocole** : taille d'échantillon et durée fixées **avant** le lancement, à partir de l'effet minimal à détecter
3. **Effet de nouveauté** : les premiers jours mesurent la réaction au changement, pas la qualité
4. **Vérifier les guardrail metrics** : latence p95, coût, taux d'erreur et de refus ne doivent pas se dégrader
5. **Alternative si l'urgence est réelle** : utiliser un test séquentiel, conçu pour le suivi continu

**Piège** : conclure sur une métrique choisie après coup parce qu'elle est favorable.

---

Mise en situation : tu veux changer le modèle de ton assistant sans risquer de dégrader l'expérience. Quelle séquence de validation mets-tu en place ? <!--anki:49405a5e697236447a4c-->
?
1. **Offline d'abord** : golden dataset rejoué, comparaison appariée, seuils de non-régression ([[94-evals-methodologie|evals]])
2. **Shadow** : le trafic réel part aussi vers la nouvelle version, sans être montré, pour comparer les sorties. Isoler les effets externes et mesurer le surcoût
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
