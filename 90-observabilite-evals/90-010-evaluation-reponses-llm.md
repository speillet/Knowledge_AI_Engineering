# Évaluation des outputs & des réponses LLM — Flashcards
Tags: #flashcards #ai-engineering #evals #reponses #qualite #llm
<!-- summary: grille par dimension, exactitude et complétude, pertinence et consignes, références multiples, normalisation, BLEU et ROUGE, BERTScore, résumés, réponses numériques, critères bloquants et agrégation par affirmation. -->


Comment définir une grille d'évaluation d'une réponse LLM ? <!--anki:6631303738646665313965663463613262386165393030353031373061313738-->
?
Partir de la **demande et du contrat de la tâche**, puis définir des critères observables : résultat exact, éléments demandés présents, consignes respectées et limites des preuves annoncées. Pour chaque critère, préciser les données nécessaires, le vérificateur et les cas de réussite ou d'échec.

Garder les dimensions séparées : une réponse claire peut être fausse, une réponse exacte peut être incomplète. Identifier les critères bloquants avant de noter le style. La [[94-evals-methodologie|méthodologie]] organise le jeu de test ; un [[95-llm-as-judge|juge]] doit être validé pour la rubrique utilisée.

---

À ne pas confondre : exactitude des affirmations et complétude d'une réponse ? <!--anki:6266653465333165663233333465633538643032353065313035343032336362-->
?
L'**exactitude** examine si les affirmations produites sont correctes au regard de références fiables. La **complétude** examine si la réponse traite les éléments nécessaires de la demande.

À « donne le statut, la cause confirmée et le prochain point », répondre uniquement avec l'heure du prochain point peut être exact et incomplet. Définir les éléments attendus avant l'évaluation ; une absence de preuve doit pouvoir être annoncée explicitement. La longueur ne mesure pas la complétude, et une réponse vide ne devient pas utile parce qu'elle ne contient aucune erreur factuelle.

---

À ne pas confondre : pertinence et respect des consignes d'une réponse ? <!--anki:3931316634333135373630353434646562383539613139656664383430353062-->
?
La **pertinence** mesure si la réponse répond au besoin exprimé. Le **respect des consignes** vérifie les contraintes explicites : langue, longueur, structure ou périmètre des informations autorisées.

Une réponse pertinente de 500 mots échoue à une limite de 100 mots. Un texte français de 80 mots peut respecter ces contraintes tout en répondant à une autre question. Définir une règle de comptage et des exemples d'ancrage ; ne pas donner à une propriété mécanique le sens d'une réussite métier complète.

---

Pourquoi une seule réponse de référence peut-elle pénaliser des réponses correctes ? <!--anki:3266306332623938643062353464306338383233363036323065356538656431-->
?
Une référence textuelle illustre souvent **une formulation parmi plusieurs**. Un exact match brut rejette alors une paraphrase correcte ou un autre raisonnement conduisant au même résultat.

Pour une question ouverte, annoter faits requis, formulations admissibles et contradictions interdites, ou utiliser plusieurs références relues. Pour une cible réellement unique, comme un identifiant, conserver une comparaison stricte. Un juge sémantique peut aider mais doit être validé ; multiplier les références ne transforme pas une information erronée en vérité. Versionner aussi les annotations et leurs corrections.

---

Quand normaliser une sortie avant un exact match ? <!--anki:3631313133633933373165323436353362613163376334393534353436626236-->
?
Lorsque le **contrat considère les variantes comme équivalentes** : espaces superflus, ordre des clés d'un objet JSON ou notation décimale compatible. Définir et versionner ces transformations avant la comparaison.

Préserver ce qui porte le sens : unités, devise, signe, négation, fuseau et ordre des éléments lorsqu'il compte. `1,00 EUR` et `1 EUR` peuvent être équivalents ; `1 USD` ne l'est pas. Pour une sortie structurée, parser puis comparer des valeurs typées ; une normalisation qui retire les unités peut masquer une erreur métier.

---

Que mesurent BLEU et ROUGE, et quand les utiliser ? <!--anki:3939396430383565306332373439663238313263656535623739333735396635-->
?
**BLEU** combine des précisions modifiées de n-grammes avec une pénalité de brièveté, historiquement pour la traduction. **ROUGE** compare des unités communes avec des résumés de référence ; ROUGE-N utilise des n-grammes et ROUGE-L des sous-séquences communes.

Ces scores mesurent un recouvrement avec des références, pas directement la vérité, la sécurité ou l'utilité métier. Fixer variante, tokenisation, références et agrégation ; un BLEU de corpus ne se confond pas avec une moyenne de scores par phrase. Les utiliser comme signaux complémentaires sur une tâche validée, avec contrôle des faits et des omissions.

---

Pourquoi BERTScore ne suffit-il pas à vérifier l'exactitude d'une réponse ? <!--anki:3966386639396665323464303464633461386563666536613562666666386564-->
?
**BERTScore** compare candidat et référence par similarités entre embeddings contextuels de tokens. Il peut reconnaître des variantes lexicales que le recouvrement exact pénalise.

Une similarité élevée ne prouve pas que dates, nombres ou entités sont corrects. L'article original présente notamment une confusion entre lundi et mardi que la métrique détecte mal. Contrôler ces valeurs contre une référence fiable et valider la métrique sur les erreurs de la tâche. Fixer modèle d'embeddings, configuration et langue ; aucun seuil universel ne certifie une réponse factuelle.

---

Comment évaluer des consignes vérifiables sans les confondre avec la qualité métier ? <!--anki:3463656462333761376565653439663139346162663361656131363962363433-->
?
Transformer chaque contrainte explicite en **vérificateur documenté** : nombre de mots, présence de sections, schéma ou liste autorisée. **IFEval** illustre cette approche avec des instructions vérifiables automatiquement.

Tester aussi le vérificateur sur des cas limites : titres, mots composés ou citations peuvent changer le comptage. Publier respect par contrainte et respect conjoint. Un texte qui répète un mot demandé peut réussir ce contrôle tout en étant faux ou inutile ; les critères sémantiques demandent leurs propres preuves. Une instruction contradictoire ou impossible doit être traitée selon une règle annoncée.

---

Comment évaluer un résumé produit par un LLM ? <!--anki:3438623531356165643333393464623538346431643264353137373533393164-->
?
Vérifier séparément **préservation des faits**, couverture des éléments essentiels pour l'usage et contraintes de présentation. Annoter les informations nécessaires avant de lire le résumé, en autorisant plusieurs formulations.

Contrôler nombres, dates, acteurs, causalité et incertitude : « cause suspectée » ne devient pas « cause confirmée ». Rechercher les ajouts non soutenus et les omissions qui changent une décision. Un score ROUGE peut compléter la comparaison, mais une reprise des mêmes mots ne prouve pas la fidélité. Adapter la sélection des informations à la longueur et à l'objectif du résumé.

---

Que vérifier dans une réponse numérique d'un LLM ? <!--anki:3863663331626135333439343464623462633938633766623138613733623237-->
?
Comparer **valeur, unité et périmètre** au résultat attendu, puis vérifier les hypothèses demandées et la règle d'arrondi. Utiliser du code pour un calcul vérifiable, avec une tolérance définie selon la tâche.

Une tolérance absolue et une tolérance relative n'ont pas le même sens ; préciser leur combinaison, notamment près de zéro. `100 g` et `0,1 kg` peuvent être équivalents après conversion autorisée, tandis que `100 kg` est faux. Pour les montants, utiliser une représentation décimale ou des unités monétaires entières adaptées au contrat ; ne pas effacer la devise.

---

Pourquoi une moyenne de scores peut-elle cacher une réponse inacceptable ? <!--anki:3063346366393362343866303465366539343732383936383262626162383738-->
?
Une moyenne autorise une **compensation entre dimensions** : excellent style et bonne structure peuvent masquer un montant faux ou une information privée révélée. Définir des critères bloquants pour les erreurs incompatibles avec le service.

Publier le profil par dimension, les violations critiques et la fraction de réponses respectant tous les critères requis. Un score agrégé peut servir à classer les réponses admissibles, avec pondérations explicites ; il ne doit pas annuler un échec bloquant. Mesurer aussi les segments, car un bon résultat global peut cacher une population mal servie.

---

Comment traiter une réponse vide, un refus et une affirmation invérifiable dans une eval ? <!--anki:6466313737363932633336363462313238376162393238306534316566386138-->
?
Le verdict dépend de la **tâche et des preuves disponibles**. Un refus attendu sur une demande interdite peut réussir ; une réponse vide sur une demande réalisable échoue à l'utilité ou à la complétude.

Une affirmation sans preuve accessible n'est pas automatiquement fausse dans le monde. Elle peut néanmoins violer un contrat imposant une réponse soutenue par le contexte. Distinguer information non soutenue, contradiction et vérification impossible, puis définir leur traitement. Publier les dénominateurs et ne pas exclure silencieusement les cas difficiles. Voir [[143-hallucinations-grounding|grounding et abstention]].

---

Calcul : A contient une affirmation soutenue sur une ; B en contient cinq sur neuf. Quels scores obtient-on avec une moyenne par réponse puis un regroupement de toutes les affirmations, sans pondération de gravité ? <!--anki:3731313532356461626432643465636139383333643434373066643234363165-->
?
Les deux agrégations répondent à des questions différentes :
```text
moyenne par réponse : (1/1 + 5/9) / 2 = 7/9 ≈ 77,8 %
regroupement        : (1 + 5) / (1 + 9) = 6/10 = 60 %
```
La première donne le même poids à chaque réponse ; la seconde donne le même poids à chaque affirmation et davantage aux réponses longues. Fixer la granularité de découpage et le traitement des réponses sans affirmation. Aucun score ne mesure les informations attendues mais omises, ni ne rend acceptable une erreur critique. Voir [[96-evals-rag-agents|évaluation des preuves]].

---

## Mises en situation

Mise en situation : un nouveau résumé reprend davantage les mots de la référence et obtient un meilleur ROUGE, mais inverse la date d'une échéance. Comment décides-tu s'il est meilleur ? <!--anki:6366633431363630303137303434386362636462646433383031326337323335-->
?
1. **Vérifier la date** contre la source fiable, avec le fuseau et le périmètre nécessaires.
2. **Classer l'erreur** selon le contrat : une échéance opérationnelle fausse peut être bloquante.
3. **Mesurer séparément** fidélité, informations essentielles et présentation sur les mêmes cas.
4. **Comparer les régressions** et leur gravité, avec répétitions et incertitude adaptées.
5. **Promouvoir seulement** si les critères requis sont satisfaits ; le gain lexical reste un signal complémentaire.

**Piège** : laisser une hausse du score de recouvrement compenser une erreur factuelle critique.

---

Mise en situation : une réponse donne correctement l'heure du prochain point, mais la question demandait aussi le statut du ticket et sa cause confirmée. Ton juge d'exactitude lui donne pass. Que complètes-tu ? <!--anki:6539353432356461363838613464616439323662363431656566373636633333-->
?
1. **Décomposer la demande** en trois éléments attendus, annotés avant les jugements.
2. **Évaluer la complétude** séparément de l'exactitude des affirmations produites.
3. **Autoriser une limite explicite** : si la cause est inconnue, « aucune cause confirmée » répond à cet élément sans inventer.
4. **Valider la grille** sur réponses complètes, partielles, contradictoires et vides.
5. **Rejouer le test indépendant** et publier les deux dimensions ainsi que la conformité conjointe.

**Piège** : rendre le juge d'exactitude plus sévère sans lui donner un critère pour les omissions.

---

Mise en situation : le contrat impose un montant en euros. Un exact match rejette « 1 € » et « 100 centimes d'euro » face à « 1,00 EUR », tandis qu'une normalisation supprimant les devises accepte « 1,00 USD ». Comment corriges-tu l'évaluateur ? <!--anki:3731663835303930326565303465613661623131323165323236393238333435-->
?
1. **Définir les équivalences** autorisées par le contrat, sans modifier la règle après lecture des scores.
2. **Extraire valeur et devise**, avec statut distinct en cas de parsing impossible.
3. **Convertir les unités autorisées** en conservant la devise et une représentation numérique adaptée.
4. **Tester positifs et négatifs** : paraphrases valides, mauvaise devise, signe inversé et montant erroné.
5. **Comparer les valeurs typées**, puis contrôler les autres critères de réponse sur un test indépendant.

**Piège** : choisir une normalisation qui maximise le score en supprimant les informations nécessaires à détecter une erreur.

---

## Sources

- [Papineni et al. — BLEU](https://aclanthology.org/P02-1040.pdf)
- [Lin — ROUGE](https://aclanthology.org/W04-1013.pdf)
- [Zhang et al. — BERTScore et limites sur les erreurs factuelles](https://arxiv.org/abs/1904.09675)
- [Zhou et al. — IFEval et consignes vérifiables](https://arxiv.org/abs/2311.07911)
- [Min et al. — FActScore et précision par fait atomique](https://arxiv.org/abs/2305.14251)

## Connexions
- [[94-evals-methodologie|Méthodologie d'évaluation]] — jeux, critères, références et décisions
- [[95-llm-as-judge|LLM-as-a-judge]] — valider les évaluateurs sémantiques de la grille
- [[96-evals-rag-agents|Evals de RAG & d'agents]] — preuves, citations et résultat métier
- [[92-chainforge-evals-prompts|Évaluation des prompts]] — assertions et comparaison des sorties
- [[63-guided-generation|Sorties structurées]] — séparer format, schéma et valeurs métier
- [[143-hallucinations-grounding|Grounding & abstention]] — limites des preuves et réponses partielles
- [[00-moc-ai-engineering|MOC AI Engineering]]
