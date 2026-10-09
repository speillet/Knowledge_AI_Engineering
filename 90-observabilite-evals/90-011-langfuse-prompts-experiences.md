# Langfuse — Prompts, datasets & expériences — Flashcards
Tags: #flashcards #ai-engineering #agents #production
Vérifié le : 9 octobre 2026 — API citées confrontées aux documentations officielles ; limites explicitées dans les cartes.
<!-- summary: labels et versions, cache de prompts, fallback, promotion, jeux d’évaluation, exécutions comparables, scores manquants, coûts par réussite et feedback. -->


À ne pas confondre : version et label d'un prompt Langfuse ? <!--anki:6132653866646365356530343433393639353338323563656432313331306364-->
?
Une **version** identifie un contenu enregistré ; un **label** sélectionne une version et peut être déplacé. `production` est donc une référence mutable, utile pour promouvoir ou retirer un prompt.

Tracer la version effectivement récupérée, pas seulement le label demandé. Pour reproduire une expérience, fixer la version et les variables rendues. Un retour du label vers une ancienne version ne garantit pas que tous les processus ont déjà renouvelé leur cache.

---

Pourquoi versionner le contrat de variables d'un prompt Langfuse ? <!--anki:3837646234303261363235643437626238616234623763633265363834393930-->
?
Le template et le code qui le remplit partagent un **contrat** : noms, types et sens des variables. Renommer `question` en `demande` peut casser l'application même si le texte du prompt semble meilleur.

Tester compilation, variables manquantes et contenu rendu avant promotion. Relier le changement aux schémas d'outils et de sortie attendus. Si les anciennes versions du code restent déployées, conserver leur compatibilité ou coordonner la bascule.

---

À ne pas confondre : cache du registre de prompts Langfuse et prefix caching du modèle ? <!--anki:6230643233623462626432323465363938666431663531653366353463666333-->
?
Le **cache du registre** évite de télécharger le template à chaque appel. Le **prefix caching** réutilise des calculs d'inférence sur un préfixe compatible côté fournisseur ou serveur de modèle.

Le premier réduit la dépendance au registre et peut retarder une mise à jour ; le second peut réduire temps de préremplissage ou coût des entrées. Ils ont des clés, durées de vie et mesures différentes. Un cache hit Langfuse ne prouve aucun gain de calcul GPU.

---

Comment rendre un rollback de prompt observable malgré les caches Langfuse ? <!--anki:3231333264666633376632303436326462623938353034303438633465636239-->
?
Suivre la **version effectivement utilisée** par les requêtes après déplacement du label. Le cache du SDK peut encore servir une version antérieure pendant son renouvellement.

Définir le délai acceptable de propagation, précharger ou invalider selon les capacités retenues et vérifier plusieurs réplicas. Pour une correction urgente, prévoir un mécanisme de désactivation applicatif indépendant du registre. Une modification visible dans l'interface ne signifie pas une bascule instantanée de tout le trafic.

---

Quel contrat imposer à un prompt de secours si Langfuse est indisponible ? <!--anki:3863356565376662666561653463373538663138643464646536393436356135-->
?
Le fallback doit être **prévalidé**, compatible avec les variables, outils et schémas attendus, puis identifié dans les traces. Tester un démarrage à cache vide et une indisponibilité après remplissage du cache.

Pour une tâche sensible, refuser proprement peut être préférable à une consigne générique improvisée. Le fallback protège la disponibilité technique ; il ne garantit pas une qualité équivalente. Mesurer son taux d'utilisation et la qualité des résultats obtenus.

---

Pourquoi une expérience Langfuse doit-elle fixer plus que le prompt ? <!--anki:3035313633663562333364343465366338363566343438383064313730313635-->
?
La sortie dépend aussi du **modèle**, des outils, du corpus, de la configuration et de l'état initial. Enregistrer leurs versions avec l'identité du dataset et de l'évaluateur.

Si deux candidats n'accèdent pas aux mêmes documents ou si le second profite d'une mémoire créée par le premier, la comparaison est biaisée. Construire une fixture indépendante pour chaque essai, tout en conservant des conditions comparables. Les traces aident ensuite à expliquer les écarts observés.

---

Comment transformer une trace d'échec en item de dataset utile ? <!--anki:6531633130623330376339383462366661643635333535343161386465366533-->
?
Extraire une **entrée reproductible**, les données nécessaires et le résultat ou invariant attendu. Retirer les secrets, vérifier les droits de réutilisation et documenter ce qui manque pour rejouer les outils.

Une conversation brute ne suffit pas si elle dépend d'une commande aujourd'hui modifiée. Remplacer l'environnement mutable par une fixture lorsque c'est possible. Garder le lien de provenance dans un espace autorisé, et empêcher que la réponse attendue soit injectée dans le contexte du candidat.

---

Pourquoi garder un dataset de régression et un dataset représentatif pour les agents ? <!--anki:3832363764663666373265333438363739373830666361626230343464643937-->
?
Le premier contient des **échecs importants connus** ; le second reflète une distribution cible de demandes. Ils répondent à des questions différentes : ne pas réintroduire un bug et estimer la performance attendue.

Accumuler uniquement les incidents produit un jeu utile mais déséquilibré. Présenter les résultats séparément et segmenter les cas critiques. Réserver aussi des cas non utilisés pendant l'optimisation pour éviter de choisir un prompt qui mémorise les exemples de révision.

---

Comment rattacher un score Langfuse au bon niveau ? <!--anki:3135646161666634343433313438653162656433646461666463323965663337-->
?
Choisir l'objet correspondant au **critère mesuré** : observation pour un outil, trace pour une exécution, session pour une conversation complète. Un score global ne permet pas toujours d'identifier l'étape fautive.

Définir nom, type, sens et version du barème. Une correction humaine tardive doit référencer l'objet original, pas simplement la dernière requête de l'utilisateur. Prévenir les doublons si le producteur de scores renvoie le même événement après une erreur réseau.

---

Pourquoi distinguer score nul, score absent et erreur d'évaluateur dans Langfuse ? <!--anki:6635643430623732393735303461373338316164333231366465313238323931-->
?
**Zéro** peut être un verdict d'échec ; **absent** signifie non évalué ; une **erreur d'évaluateur** signifie que le jugement n'a pas pu être calculé. Les confondre fausse les comparaisons.

Publier la couverture d'évaluation et les erreurs avec les scores. Si un candidat produit des réponses qui font échouer le juge, les exclure silencieusement peut le favoriser. Fixer à l'avance le traitement des exécutions invalides et analyser leur fréquence par candidat.

---

Comment versionner un juge sans casser la lecture des scores historiques ? <!--anki:6232656333363865326132613465666539363735653837383336623266623561-->
?
Enregistrer **modèle, prompt, configuration et barème** du juge. Calibrer la nouvelle version sur des cas annotés puis faire une période de comparaison avec l'ancienne.

Un score `qualite=0,8` ne conserve pas le même sens si le rubric change. Séparer les séries ou recalculer un ensemble de référence explicitement identifié. Garder les désaccords et les exemples limites : une moyenne de juges ne résout pas automatiquement une ambiguïté de définition.

---

Comment décider de promouvoir un prompt avec les expériences Langfuse ? <!--anki:6431653166646365363338383431613562316462363535626438383864346566-->
?
Fixer avant comparaison des **critères d'acceptation** : réussite métier, absence de régression critique, coût et latence. Comparer les mêmes cas, inspecter les régressions et considérer l'incertitude.

Le meilleur score moyen peut masquer un échec sur les autorisations ou une hausse des abandons. Après validation hors ligne, déployer progressivement et relier les mesures en production à la version réellement servie. L'outil d'expérimentation apporte les données ; la règle de décision reste à définir.

---

Calcul : sur les mêmes 200 dossiers, le candidat A coûte 12 € et réussit 160 dossiers ; B coûte 15 € et en réussit 180. Quels sont leurs coûts par réussite, en incluant le coût des échecs ? <!--anki:3338613335393339663136373438623861653362643533373034396530383136-->
?
**A : 12 / 160 = 0,075 €** par réussite ; **B : 15 / 180 ≈ 0,0833 €**. Les taux de réussite sont respectivement 80 % et 90 %.

B réussit davantage mais son coût par réussite est plus élevé. Le choisir dépend de la valeur des dossiers supplémentaires, des contraintes de latence et des erreurs acceptables. Exclure les coûts des échecs ferait paraître artificiellement les candidats plus économiques.

---

Comment éviter que le feedback utilisateur manipule les scores d'une application agentique ? <!--anki:6435663531316637316162343438373938336638396566373964393037303862-->
?
Rattacher le feedback à une **exécution appartenant à l'utilisateur authentifié**, borner la fréquence et définir une règle de remplacement ou de déduplication. Ne pas accepter librement un `trace_id` externe comme preuve de propriété.

Séparer satisfaction, correction factuelle et réussite métier. Le silence ne vaut pas approbation, et certains utilisateurs répondent plus souvent que d'autres. Garder ce feedback comme un signal à croiser avec des contrôles objectifs et des annotations ciblées.

---

## Mises en situation

Mise en situation : après rollback du label production dans Langfuse, certains utilisateurs reçoivent encore l'ancien comportement. Que vérifies-tu ? <!--anki:3565393461396130356562623431323739343334636338363262323531636461-->
?
1. Lire la version effectivement attachée aux generations, par réplica et période.
2. Vérifier caches, préchargements et éventuels prompts de secours.
3. Contrôler que tous les chemins de code utilisent le registre attendu.
4. Tester la propagation et surveiller jusqu'au retour au comportement visé.

**Piège** : déclarer le rollback terminé sur la seule base du label affiché.

---

Mise en situation : un candidat gagne cinq points dans Langfuse mais 20 % de ses évaluations sont absentes. Peut-on conclure à une amélioration ? <!--anki:3137333733343833613539313431383561346636306330353234306435613561-->
?
1. Comparer la couverture et les erreurs d'évaluateur entre candidats.
2. Examiner les cas absents et leur éventuel lien avec des sorties invalides.
3. Appliquer la règle prévue pour les exécutions non évaluables, sans les masquer.
4. Relancer les évaluations réparables puis comparer les mêmes cas avec incertitude.

**Piège** : calculer la moyenne uniquement sur les réponses que le juge a réussi à lire.

---

Mise en situation : le prompt s'améliore sur les incidents historiques mais dégrade les demandes simples en production. Comment rééquilibres-tu les évaluations ? <!--anki:3137633634643732313339623435376462336238343866396434623436373735-->
?
1. Conserver les incidents dans un jeu de régression dédié.
2. Construire un échantillon représentatif des demandes courantes et de leurs segments.
3. Rapporter qualité, coût et latence sur les deux jeux.
4. Exiger les garanties critiques tout en vérifiant la performance du trafic habituel.

**Piège** : supprimer les cas difficiles pour embellir la moyenne ou ne tester qu'eux.

---

## Sources
- [Langfuse — gestion des prompts](https://langfuse.com/docs/prompt-management/get-started)
- [Langfuse — cache et fallback des prompts](https://langfuse.com/docs/prompt-management/features/caching)
- [Langfuse — datasets](https://langfuse.com/docs/evaluation/experiments/datasets)
- [Langfuse — scores via API et SDK](https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-sdk)

## Connexions
- [[91-langfuse-observabilite|Langfuse — Fondamentaux]] — relier prompts, traces et scores
- [[90-010-langfuse-instrumentation-production|Langfuse — Instrumentation]] — provenance et couverture des observations
- [[13-prompts-production|Prompts en production]] — versionner et promouvoir les contrats
- [[99-statistiques-decisions-experimentales|Statistiques]] — décider à partir des expériences
- [[95-llm-as-judge|LLM-as-judge]] — calibrer les évaluateurs
- [[00-moc-ai-engineering|MOC AI Engineering]]
