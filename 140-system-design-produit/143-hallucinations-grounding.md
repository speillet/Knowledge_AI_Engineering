# Hallucinations, grounding & abstention — Flashcards
Tags: #flashcards #ai-engineering #hallucinations #grounding #qualite #llm
<!-- summary: types d'hallucinations, leviers, citations vérifiées, abstention, arbitrage avec la couverture, détection, calibration, slopsquatting, communication de l'incertitude; température et factualité, conflits de sources, réponses partielles. -->


Qu'est-ce qu'une hallucination ? <!--anki:43342c5e784379766728-->
?
Une sortie **plausible mais fausse ou non étayée** : fait inventé, citation inexistante, fonction d'API imaginaire, chiffre erroné. Elle vient de la nature même du modèle, qui génère **ce qui est probable**, pas **ce qui est vrai**, et d'un entraînement qui récompense souvent **répondre plutôt que s'abstenir**.

---

À ne pas confondre : hallucination intrinsèque et extrinsèque ? <!--anki:68752d663634387a247b-->
?
- **Intrinsèque** : la sortie **contredit** la source fournie (résumé qui inverse un chiffre).
- **Extrinsèque** : la sortie **ajoute** une information **absente** de la source, vraie ou fausse — invérifiable à partir du contexte.

En RAG, les deux sont des échecs de **faithfulness** ([[96-evals-rag-agents|évaluation]]).

---

Quels leviers réduisent les hallucinations avant la génération ? <!--anki:68515d5d3f282d2d4d76-->
?
1. **Grounding** : fournir les faits via [[21-rag-fondamentaux|RAG]] ou outils.
2. **Consignes** : répondre **uniquement** à partir du contexte, sinon dire qu'on ne sait pas.
3. **Tâche plus étroite** et vérifications adaptées : contraindre le format aide à contrôler la sortie, mais ni JSON ni température basse ne garantissent la factualité.

Mesurer séparément variabilité, respect du format et exactitude. Une source erronée ou périmée peut produire une réponse fidèle mais fausse.

---

Quels leviers réduisent les hallucinations après la génération ? <!--anki:7749336061702e3c4131-->
?
1. **Citations** obligatoires, puis **vérifiées** côté code.
2. **Vérification** de la réponse : juge, NLI, ou règles métier sur les montants, dates et références.
3. **Escalade** vers un humain quand la vérification échoue, plutôt qu'une réponse non étayée.

---

Comment rendre les citations fiables ? <!--anki:7255287c6d622c66262a-->
?
Demander au modèle de citer des **identifiants de passages** (et non des URL ou titres qu'il pourrait inventer), puis **vérifier côté code** que chaque identifiant existe dans le contexte fourni, et idéalement que le passage **soutient** la phrase (juge ou NLI). Une citation inventée est **pire** que pas de citation : elle crée une fausse confiance.

---

Qu'est-ce que l'abstention et pourquoi est-elle difficile ? <!--anki:6d23262a5e6d66256b7c-->
?
La capacité à répondre **« je ne sais pas »** ou **« ce n'est pas dans les documents »**. Difficile car les modèles sont biaisés vers **répondre** ; il faut l'**exiger explicitement**, fournir des **exemples** d'abstention, et l'**évaluer** avec des questions **sans réponse** dans le jeu de test (sinon on optimise un système qui ne s'abstient jamais).

---

Comment arbitrer entre abstention et couverture ? <!--anki:762f2b51314c5a4a552a-->
?
Trop d'abstentions = système **inutile** ; trop peu = **réponses fausses**. On mesure les deux (taux de réponse, précision des réponses données) et on choisit le point selon le **coût d'une erreur** : un assistant médical ou juridique doit s'abstenir plus qu'un outil de brainstorming.

---

Comment détecter une hallucination après génération ? <!--anki:423a236456252a5e4e45-->
?
**Vérifier les affirmations contre une source de référence** : passages récupérés, données structurées ou règles métier. Un juge ou un modèle d'inférence textuelle peut aider, mais il doit être évalué sur des annotations fiables.

La divergence entre générations et les logprobs servent de signaux de triage, pas de preuves : plusieurs réponses peuvent répéter la même erreur, et une continuation probable peut être fausse. Mesurer faux positifs et faux négatifs du détecteur. En cas d'incertitude, déclencher abstention ou revue selon le risque.

---

Les LLM sont-ils calibrés : leur confiance reflète-t-elle leur taux de réponses justes ? <!--anki:65443c5a7252553d7a3a-->
?
**Pas automatiquement.** Il faut préciser l'événement mesuré : prochain token, classe prédite ou correction d'une réponse complète. Une bonne calibration sur l'un ne garantit pas celle des autres.

Les logprobs et la confiance exprimée en mots sont des signaux à valider sur une tâche et une population labellisées. Entraînement, prompt et changement de domaine peuvent modifier leur relation à l'exactitude. Avant d'afficher « confiance : 95 % », mesurer courbe de fiabilité, effectifs et segments ; définir un seuil d'abstention puis le tester indépendamment.

---

Pourquoi les hallucinations de code sont-elles un risque de sécurité ? <!--anki:4e43495d553d6e306131-->
?
Le modèle invente des **noms de paquets** qui n'existent pas ; des attaquants **enregistrent** ces noms avec du code malveillant (**slopsquatting**). Parade : vérifier l'existence et la réputation des dépendances, lockfiles, registres internes ([[106-securite-agents-code|agents de code]]).

---

Comment communiquer l'incertitude à l'utilisateur ? <!--anki:783a747339575a7d7537-->
?
- Afficher les **sources** et permettre de les ouvrir.
- Distinguer **ce qui vient des documents** de ce qui est **déduit**.
- Signaler les réponses **à vérifier** (confiance faible, pas de source).
- Ne pas sur-promettre dans l'interface (« réponse vérifiée » seulement si c'est vrai).

Voir [[144-ux-ia-human-in-the-loop|UX de l'IA]].

---

Pourquoi une température basse ne garantit-elle pas la factualité d'un LLM ? <!--anki:6436363963323235643535633431616538653434343230393137643133366330-->
?
La température modifie la **distribution de sélection des tokens**, pas la vérité des faits disponibles. Une réponse fausse très probable peut être reproduite avec assurance à température basse.

Une sortie structurée garantit éventuellement un format conforme, pas un chiffre exact. Mesurer la factualité sur des références fiables ; fournir des preuves adaptées, vérifier les calculs avec du code et prévoir l'abstention lorsque la source manque. Réduire la variabilité peut aider certaines tâches, mais son effet sur l'exactitude doit être évalué.

---

Comment répondre lorsque deux sources récupérées se contredisent ? <!--anki:6535366534346465373464653433323461663564393234363562343264616666-->
?
Appliquer une **règle de priorité documentée** selon le besoin : source de référence, version applicable, date d'effet et périmètre. La source la plus récente n'est pas forcément celle qui s'applique au cas demandé.

Si le conflit reste irrésolu, le rendre explicite et s'abstenir sur le point litigieux ou demander une clarification. Citer les passages concernés. Ne pas fusionner deux chiffres incompatibles ni laisser le modèle choisir la formulation la plus plausible. Conserver les versions utilisées pour permettre le diagnostic.

---

Quand une réponse partielle est-elle préférable à une abstention complète en RAG ? <!--anki:3762666538376539333832323464316138336132366665326439636237313864-->
?
Lorsque certaines parties sont **étayées et utiles indépendamment** des informations manquantes. Répondre à ces parties en citant leurs preuves et identifier précisément ce qui reste inconnu.

Exemple : la procédure décrit le délai de retour, mais pas les frais ; donner le délai sans inventer le tarif. Si l'information manquante conditionne toute la décision, une réponse partielle peut induire en erreur : demander une précision ou escalader. Évaluer séparément utilité de la réponse et respect des limites du contexte.

---

## Mises en situation

Mise en situation : ton assistant documentaire cite des pages qui n'existent pas, et les utilisateurs perdent confiance. Comment traites-tu le problème ? <!--anki:437050683d4d6b72512b-->
?
1. **Changer ce qu'on demande** : faire citer des **identifiants de passages** fournis dans le contexte, pas des titres ou des URL que le modèle peut inventer
2. **Vérifier côté code** que chaque identifiant cité existe réellement dans le contexte
3. **Vérifier le soutien** : la phrase est-elle réellement appuyée par le passage cité (juge ou NLI) ?
4. **Refuser de répondre** plutôt que de produire une réponse sans citation valide
5. **Mesurer** : taux de citations valides et faithfulness sur un jeu de test ([[96-evals-rag-agents|evals de RAG]])

**Piège** : afficher des citations non vérifiées, qui créent une fausse confiance pire que l'absence de source.

---

Mise en situation : le métier exige que ton assistant réponde toujours, jamais « je ne sais pas ». Comment réagis-tu ? <!--anki:4d562b243a672470396c-->
?
1. **Expliquer l'arbitrage** : supprimer l'abstention, c'est accepter des réponses fausses sur les questions hors périmètre
2. **Chiffrer le coût d'une erreur** dans ce domaine : conseil juridique ou médical, ou simple brainstorming ?
3. **Mesurer les deux dimensions** : taux de réponse et exactitude des réponses données
4. **Tester avec des questions sans réponse** dans le contexte, sinon on optimise un système qui ne s'abstient jamais
5. **Proposer un compromis** : répondre avec une **mention d'incertitude** et des sources, ou orienter vers un humain ([[144-ux-ia-human-in-the-loop|UX]])

**Piège** : régler le problème par une consigne de prompt, sans jamais mesurer le taux de réponses non étayées.

---

Mise en situation : deux documents donnent des délais de retour de 14 et 30 jours, et l'assistant choisit systématiquement 30. Comment corriges-tu ce comportement ? <!--anki:3637613436353566316337353432316438653533326162303064343263633036-->
?
1. **Identifier le périmètre** de chaque document : produit, pays, version et date d'effet.
2. **Définir la source applicable**, avec le métier, au lieu de choisir le délai le plus favorable.
3. **Transmettre ces métadonnées** et une règle de résolution au système.
4. **Prévoir une clarification ou une abstention** si les preuves ne permettent pas de trancher.
5. **Tester les deux régimes et le conflit**, avec citations et vérification des affirmations.

**Piège** : choisir automatiquement le document le plus récent sans vérifier son champ d'application.

---

## Sources

- [Liu et al. — soutien et couverture des citations](https://arxiv.org/abs/2304.09848)
- [Niu et al. — RAGTruth, hallucinations malgré un contexte récupéré](https://arxiv.org/abs/2401.00396)
- [Geifman & El-Yaniv — risque et couverture avec abstention](https://proceedings.neurips.cc/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html)

## Connexions
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — grounding et citations
- [[96-evals-rag-agents|Evals de RAG]] — mesurer la faithfulness
- [[95-llm-as-judge|LLM-as-a-judge]] — détecter après coup
- [[65-probabilites-sampling|Probabilités & sampling]] — logprobs et calibration
- [[101-securite-llm-guardrails|Guardrails]] — contrôles de sortie
- [[144-ux-ia-human-in-the-loop|UX de l'IA]] — montrer l'incertitude
- [[11-prompt-engineering-avance|Prompt engineering avancé]] — les techniques de base du prompt
- [[26-text-to-sql|Text-to-SQL]] — répondre aux questions chiffrées sur des tables
- [[27-agents-recherche-deep-research|Agents de recherche]] — la recherche en plusieurs étapes, avec citations
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[173-calibration-incertitude-abstention|Calibration, incertitude & abstention]] — ne pas confondre confiance et véracité
- [[00-moc-ai-engineering|MOC AI Engineering]]
