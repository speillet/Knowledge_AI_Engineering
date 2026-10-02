# Hallucinations, grounding & abstention — Flashcards
Tags: #flashcards #ai-engineering #hallucinations #grounding #qualite #llm

Qu'est-ce qu'une hallucination ?
?
<!--anki:43342c5e784379766728-->
Une sortie **plausible mais fausse ou non étayée** : fait inventé, citation inexistante, fonction d'API imaginaire, chiffre erroné. Elle vient de la nature même du modèle, qui génère **ce qui est probable**, pas **ce qui est vrai**, et d'un entraînement qui récompense souvent **répondre plutôt que s'abstenir**.

---

À ne pas confondre : hallucination intrinsèque et extrinsèque ?
?
<!--anki:68752d663634387a247b-->
- **Intrinsèque** : la sortie **contredit** la source fournie (résumé qui inverse un chiffre).
- **Extrinsèque** : la sortie **ajoute** une information **absente** de la source, vraie ou fausse — invérifiable à partir du contexte.

En RAG, les deux sont des échecs de **faithfulness** ([[96-evals-rag-agents|évaluation]]).

---

Quels leviers réduisent les hallucinations avant la génération ?
?
<!--anki:68515d5d3f282d2d4d76-->
1. **Grounding** : fournir les faits via [[21-rag-fondamentaux|RAG]] ou outils.
2. **Consignes** : répondre **uniquement** à partir du contexte, sinon dire qu'on ne sait pas.
3. **Tâche plus étroite**, sorties **structurées** et **température basse** pour les tâches factuelles.

---

Quels leviers réduisent les hallucinations après la génération ?
?
<!--anki:7749336061702e3c4131-->
1. **Citations** obligatoires, puis **vérifiées** côté code.
2. **Vérification** de la réponse : juge, NLI, ou règles métier sur les montants, dates et références.
3. **Escalade** vers un humain quand la vérification échoue, plutôt qu'une réponse non étayée.

---

Comment rendre les citations fiables ?
?
<!--anki:7255287c6d622c66262a-->
Demander au modèle de citer des **identifiants de passages** (et non des URL ou titres qu'il pourrait inventer), puis **vérifier côté code** que chaque identifiant existe dans le contexte fourni, et idéalement que le passage **soutient** la phrase (juge ou NLI). Une citation inventée est **pire** que pas de citation : elle crée une fausse confiance.

---

Qu'est-ce que l'abstention et pourquoi est-elle difficile ?
?
<!--anki:6d23262a5e6d66256b7c-->
La capacité à répondre **« je ne sais pas »** ou **« ce n'est pas dans les documents »**. Difficile car les modèles sont biaisés vers **répondre** ; il faut l'**exiger explicitement**, fournir des **exemples** d'abstention, et l'**évaluer** avec des questions **sans réponse** dans le jeu de test (sinon on optimise un système qui ne s'abstient jamais).

---

Comment arbitrer entre abstention et couverture ?
?
<!--anki:762f2b51314c5a4a552a-->
Trop d'abstentions = système **inutile** ; trop peu = **réponses fausses**. On mesure les deux (taux de réponse, précision des réponses données) et on choisit le point selon le **coût d'une erreur** : un assistant médical ou juridique doit s'abstenir plus qu'un outil de brainstorming.

---

Comment détecter une hallucination après génération ?
?
<!--anki:423a236456252a5e4e45-->
- **Vérification contre le contexte** : découpage en affirmations + juge/NLI ([[95-llm-as-judge|LLM-as-a-judge]]).
- **Self-consistency** : générer plusieurs réponses ; si elles **divergent**, la confiance est faible.
- **Logprobs** : tokens à faible probabilité sur les faits clés ([[65-probabilites-sampling|calibration]]).
- **Règles** : références, montants, dates vérifiés contre une source de vérité.

---

Les modèles sont-ils calibrés ?
?
<!--anki:65443c5a7252553d7a3a-->
Partiellement : les **logprobs** d'un modèle de base sont souvent assez bien calibrés, mais le **post-training** dégrade cette calibration, et la **confiance exprimée en mots** (« je suis sûr ») est peu fiable. On ne peut pas afficher « confiance : 95 % » sans avoir **mesuré** sur un jeu labellisé que ce score correspond à 95 % de réponses justes.

---

Pourquoi les hallucinations de code sont-elles un risque de sécurité ?
?
<!--anki:4e43495d553d6e306131-->
Le modèle invente des **noms de paquets** qui n'existent pas ; des attaquants **enregistrent** ces noms avec du code malveillant (**slopsquatting**). Parade : vérifier l'existence et la réputation des dépendances, lockfiles, registres internes ([[106-securite-agents-code|agents de code]]).

---

Comment communiquer l'incertitude à l'utilisateur ?
?
<!--anki:783a747339575a7d7537-->
- Afficher les **sources** et permettre de les ouvrir.
- Distinguer **ce qui vient des documents** de ce qui est **déduit**.
- Signaler les réponses **à vérifier** (confiance faible, pas de source).
- Ne pas sur-promettre dans l'interface (« réponse vérifiée » seulement si c'est vrai).

Voir [[144-ux-ia-human-in-the-loop|UX de l'IA]].

---

## Mises en situation

Mise en situation : ton assistant documentaire cite des pages qui n'existent pas, et les utilisateurs perdent confiance. Comment traites-tu le problème ?
?
<!--anki:437050683d4d6b72512b-->
1. **Changer ce qu'on demande** : faire citer des **identifiants de passages** fournis dans le contexte, pas des titres ou des URL que le modèle peut inventer
2. **Vérifier côté code** que chaque identifiant cité existe réellement dans le contexte
3. **Vérifier le soutien** : la phrase est-elle réellement appuyée par le passage cité (juge ou NLI) ?
4. **Refuser de répondre** plutôt que de produire une réponse sans citation valide
5. **Mesurer** : taux de citations valides et faithfulness sur un jeu de test ([[96-evals-rag-agents|evals de RAG]])

**Piège** : afficher des citations non vérifiées, qui créent une fausse confiance pire que l'absence de source.

---

Mise en situation : le métier exige que ton assistant réponde toujours, jamais « je ne sais pas ». Comment réagis-tu ?
?
<!--anki:4d562b243a672470396c-->
1. **Expliquer l'arbitrage** : supprimer l'abstention, c'est accepter des réponses fausses sur les questions hors périmètre
2. **Chiffrer le coût d'une erreur** dans ce domaine : conseil juridique ou médical, ou simple brainstorming ?
3. **Mesurer les deux dimensions** : taux de réponse et exactitude des réponses données
4. **Tester avec des questions sans réponse** dans le contexte, sinon on optimise un système qui ne s'abstient jamais
5. **Proposer un compromis** : répondre avec une **mention d'incertitude** et des sources, ou orienter vers un humain ([[144-ux-ia-human-in-the-loop|UX]])

**Piège** : régler le problème par une consigne de prompt, sans jamais mesurer le taux de réponses non étayées.

---

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
- [[00-moc-ai-engineering|MOC AI Engineering]]
