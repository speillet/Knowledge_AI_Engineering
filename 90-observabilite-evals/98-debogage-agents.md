# Débogage & analyse d'échecs des agents — Flashcards
Tags: #flashcards #ai-engineering #agents #evals #observabilite #debogage

Pourquoi un agent est-il plus difficile à déboguer qu'un appel LLM ?
?
- L'échec apparaît souvent **loin de sa cause** : un mauvais résultat d'outil à l'étape 3 produit une réponse fausse à l'étape 15
- Le comportement est **non déterministe** : l'échec ne se reproduit pas à chaque essai ([[114-reproductibilite-variance|variance]])
- La trace est **longue** : des dizaines d'appels, d'outils et de milliers de tokens

Il faut donc des **traces complètes** et une méthode, pas seulement des logs d'erreurs ([[91-langfuse-observabilite|traces]]).

---

Qu'est-ce que l'analyse d'erreurs (error analysis) ?
?
Une méthode **qualitative d'abord** : lire des dizaines de traces ratées, noter librement ce qui cloche (**open coding**), puis regrouper ces notes en **catégories** d'échec (**axial coding**) et les compter.

Elle révèle les **vrais** modes d'échec du système, avant de choisir quoi mesurer. Les métriques génériques (« utilité », « pertinence ») passent souvent à côté ([[94-evals-methodologie|méthodologie]]).

---

À ne pas confondre : symptôme et cause d'un échec d'agent ?
?
- **Symptôme** : ce que l'utilisateur voit. « Réponse fausse », « l'agent tourne en rond »
- **Cause** : la **première étape** où la trace dévie. Recherche mal formulée, description d'outil ambiguë, résultat d'outil tronqué, consigne contradictoire

On corrige la **première erreur** de la trace : les suivantes en découlent souvent.

---

Quelles catégories d'échec rencontre-t-on le plus souvent ?
?
- **Spécification** : consigne ambiguë ou contradictoire, critère de fin absent
- **Outils** : mauvais choix d'outil, arguments invalides, résultat mal interprété ([[32-tool-calling|tool calling]])
- **Contexte** : information manquante, noyée ou périmée ([[35-context-engineering|context engineering]])
- **Vérification** : l'agent déclare avoir fini sans vérifier
- **Boucles** : répétition de la même action sans progrès

Le classement indique **où agir** : prompt, outil, retrieval, garde-fous ou modèle.

---

Que dit la taxonomie MAST sur les échecs des systèmes multi-agents ?
?
Une étude de 2025 (« Why Do Multi-Agent LLM Systems Fail? ») classe les échecs observés en **trois familles** :
- **Conception et spécification** : rôles mal définis, consignes non respectées
- **Désalignement entre agents** : informations non transmises, travail ignoré ou dupliqué
- **Vérification et terminaison** : arrêt prématuré, vérification absente ou superficielle

Conclusion utile : beaucoup d'échecs viennent de la **conception du système**, pas des limites du modèle ([[36-orchestration-agents|multi-agents]]).

---

Comment détecter qu'un agent tourne en boucle ?
?
- **Répétition** : même outil avec les mêmes arguments plusieurs fois de suite
- **Absence de progrès** : aucun nouvel état (fichier, donnée) depuis N étapes
- **Dépassement** du nombre d'étapes ou du budget prévus

Réaction : interrompre, renvoyer au modèle un message qui **décrit la boucle**, ou escalader. Et analyser la cause : souvent une erreur d'outil **mal expliquée** au modèle ([[142-fiabilite-resilience-llm|résilience]]).

---

Comment reproduire un échec d'agent ?
?
- **Rejouer la trace** : réinjecter les mêmes entrées et les **mêmes résultats d'outils enregistrés**, pour isoler la décision du modèle
- **Figer** modèle, prompt et paramètres ; température basse pour le diagnostic
- **Relancer N fois** l'état juste avant la déviation, pour mesurer la fréquence de l'erreur
- **Outils simulés** (mocks) pour les actions non rejouables : paiement, e-mail

Un échec vu une fois sur dix n'est pas corrigé tant qu'on ne mesure pas cette fréquence.

---

Que faire d'un échec une fois compris ?
?
1. **Corriger** au bon endroit : prompt, description d'outil, retrieval, garde-fou en code
2. **Ajouter le cas** au jeu de non-régression, avec le critère de réussite ([[153-data-flywheel-versioning|flywheel]])
3. **Vérifier** que la correction n'en casse pas d'autres, sur le jeu complet
4. **Surveiller** en production la catégorie d'échec correspondante

Sans l'étape 2, le même échec revient au prochain changement de modèle.

---

Quels signaux de production pointent vers les traces à lire ?
?
- **Feedback négatif** et escalades vers un humain
- **Erreurs d'outils** et refus de politique ([[115-plateformes-agents-gouvernance|gateway]])
- **Traces anormalement longues** ou coûteuses
- **Reformulations** de l'utilisateur juste après une réponse
- **Échantillon aléatoire**, pour trouver les échecs silencieux

Lire chaque semaine un lot de traces reste l'activité la plus rentable pour améliorer un agent ([[93-monitoring-inference|monitoring]]).

---

Quand ne pas accuser le modèle ?
?
Tant que la trace montre un problème **en amont** : l'information n'était pas dans le contexte, l'outil a renvoyé une erreur illisible, deux consignes se contredisaient, ou le critère de fin n'existait pas. Changer de modèle masque parfois ces défauts, sans les corriger.

On accuse le modèle quand il échoue **avec** un contexte correct et des outils clairs, et que d'autres modèles réussissent sur le même cas ([[146-choix-modeles|choix de modèle]]).

---

## Mises en situation

Mise en situation : ton agent de support a un taux de réussite de 72 %, et l'équipe propose de passer au modèle supérieur, trois fois plus cher. Comment décides-tu ?
?
1. **Lire 50 traces ratées** et noter librement ce qui cloche, sans catégories préétablies
2. **Regrouper et compter** : par exemple 40 % d'outil mal choisi, 30 % d'information absente du contexte, 15 % d'arrêt sans vérification
3. **Corriger les causes non liées au modèle** : descriptions d'outils, retrieval, étape de vérification
4. **Remesurer**, puis tester le modèle supérieur sur les échecs restants seulement
5. **Décider au coût par tâche réussie** ([[121-couts-inference|coûts]])

**Piège** : payer trois fois plus pour masquer des défauts de conception.

---

Mise en situation : un utilisateur signale qu'un agent multi-agents a produit un rapport « complètement à côté ». La trace fait 140 étapes. Par où commences-tu ?
?
1. **Relire la demande et la réponse finale** pour décrire précisément l'écart
2. **Remonter aux décisions de l'orchestrateur** : plan et consignes données à chaque sous-agent
3. **Chercher la première déviation** : consigne mal transmise, sous-agent qui a répondu à une autre question, résumé qui a perdu l'essentiel
4. **Rejouer** l'étape fautive avec les mêmes entrées, plusieurs fois, pour mesurer la fréquence
5. **Corriger et ajouter le cas** au jeu de non-régression

**Piège** : lire la trace dans l'ordre depuis le début, et s'y perdre avant d'atteindre l'étape fautive.

---

## Connexions
- [[91-langfuse-observabilite|Langfuse & observabilité]] — les traces à lire
- [[94-evals-methodologie|Évaluation — méthodologie]] — des échecs observés aux métriques
- [[96-evals-rag-agents|Évaluation des agents]] — mesurer après correction
- [[36-orchestration-agents|Orchestration multi-agents]] — les échecs de coordination
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — des étapes plus faciles à diagnostiquer
- [[114-reproductibilite-variance|Reproductibilité & variance]] — rejouer et mesurer la fréquence
- [[153-data-flywheel-versioning|Data flywheel]] — transformer les échecs en cas de test
- [[00-moc-ai-engineering|MOC AI Engineering]]
