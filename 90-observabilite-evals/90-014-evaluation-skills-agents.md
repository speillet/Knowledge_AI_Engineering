# Évaluer des skills d'agent — Flashcards
Tags: #flashcards #ai-engineering #evals #agents #skills #llm
Vérifié le : 14 novembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: conformité, déclenchement et utilité, rôle de la description, demandes trop simples, jeu de déclenchement et near-misses, détection dans les traces, bruit à trois essais, entraînement et validation, exécutions appariées, référence sans skill ou ancienne version, assertions et preuves, coût par succès, SkillsBench (skills curées, auto-générées, taille, gain normalisé), fuite de solution, skill invoquée ou utile. -->


Quelles questions faut-il séparer pour évaluer une skill d'agent ? <!--anki:3537303338616330316165633438636639386134396332626163613831343164-->
?
Trois questions, testées par des moyens différents :
1. **Conformité** : le dossier respecte-t-il le format Agent Skills ? Contrôle statique, par exemple avec [[90-015-agent-skills-format-skills-ref|skills-ref]].
2. **Déclenchement** : l'agent charge-t-il la skill quand elle sert, et seulement alors ?
3. **Utilité** : avec la skill, la tâche réussit-elle plus souvent qu'avec une référence, et à quel coût ?

Une skill valide peut ne jamais se déclencher ; une skill bien déclenchée peut dégrader le résultat. Un score global unique masque l'étape qui échoue. La sûreté du contenu se traite à part ([[104-securite-mcp-skills|sécurité des skills]]).

---

Pourquoi la description d'une skill décide-t-elle de son déclenchement ? <!--anki:3365343534333430616636343462663061376132333737303463666461303636-->
?
Par [[34-harness-plugins|divulgation progressive]] : au démarrage, l'agent ne voit que le `name` et la `description` de chaque skill, soit environ 50 à 100 tokens chacune. Il ne lit le `SKILL.md` complet qu'après avoir jugé la skill pertinente. La description porte donc seule la décision.

Une description efficace dit ce que fait la skill **et quand l'utiliser**, en termes d'intention : « Utiliser quand l'utilisateur veut explorer un tableur, même sans dire CSV ». Le corps du fichier, aussi bon soit-il, n'aide pas une skill que l'agent ne charge jamais.

---

Pourquoi une skill pertinente peut-elle ne pas se déclencher sur une demande simple ? <!--anki:3737636464666633316633343465306438333339653837373036326335383530-->
?
Les agents consultent surtout les skills pour des tâches qui dépassent ce qu'ils savent faire seuls. « Lis ce PDF » se traite avec les outils de base, même si la description d'une skill PDF correspond parfaitement.

Pour l'eval, les requêtes positives doivent donc exiger le savoir de la skill — API interne, format rare, procédure métier — et pas seulement contenir ses mots-clés. Sinon, un faible taux de déclenchement accuse à tort la description. Ne pas charger la skill n'est un échec que si le résultat en souffre.

---

Comment construire un jeu de requêtes pour tester le déclenchement d'une skill ? <!--anki:3031636231383437393831613461316362626334663630353333373038336261-->
?
Environ **20 requêtes étiquetées** `should_trigger`, moitié positives, moitié négatives :
- **positives variées** : ton formel ou familier, domaine nommé ou seulement décrit, tâche courte ou enfouie dans un flux à plusieurs étapes ;
- **négatives proches** (*near-misses*) : mêmes mots-clés, besoin différent ;
- **contexte réaliste** : chemins de fichiers, noms de colonnes, fautes de frappe.

Les positives les plus utiles sont celles où le lien avec la skill n'est pas évident : si la requête décrit exactement la skill, n'importe quelle description la déclenche.

---

Qu'est-ce qu'une requête négative « near-miss » dans un eval de déclenchement de skill ? <!--anki:6565373337663737303561633432616139393934386365303039383965383333-->
?
Une requête qui **partage les mots-clés ou le domaine** de la skill mais demande autre chose. Pour une skill d'analyse de CSV, « écris un script qui charge chaque ligne d'un CSV dans Postgres » relève de l'ETL, pas de l'analyse.

« Quelle météo demain ? » ne teste rien : aucune description raisonnable ne s'y déclenche. Les near-misses mesurent la **précision** de la description, comme les cas sans outil mesurent les faux appels en [[96-evals-rag-agents|tool calling]]. Une description qui gagne des positifs en devenant vague se trahit sur ces cas.

---

Comment détecter qu'une skill s'est déclenchée pendant un essai ? <!--anki:3332623937373534623761343433623362316265343966303964663138346633-->
?
Dans la **trace de l'agent** : appel de l'outil de chargement de skill ou lecture du `SKILL.md`. Le guide Agent Skills donne cet exemple pour Claude Code en mode headless :

```bash
claude -p "$QUERY" --output-format json \
  | jq -e --arg s "$SKILL" 'any(.messages[].content[];
      .type == "tool_use" and .name == "Skill" and .input.skill == $s)'
```

`jq -e` renvoie 0 si un appel `Skill` vise la skill testée. Le format de sortie dépend du client et de sa version : valider le détecteur sur un cas positif connu avant la série. On peut arrêter l'essai dès que l'issue est claire.

---

Calcul : une requête positive déclenche réellement la skill dans 40 % des essais. Avec 3 essais indépendants et la règle « taux observé > 0,5 », quelle est la probabilité de la compter comme réussie ? <!--anki:3438353634313032646332383437663438383430366565643464333736656636-->
?
Il faut au moins 2 déclenchements sur 3 :
```text
P(X ≥ 2) = 3 × 0,4² × 0,6 + 0,4³ = 0,288 + 0,064 = 0,352
```
Une requête faible passe donc **environ une fois sur trois**. Avec 3 essais, le taux observé ne prend que quatre valeurs (0, 1/3, 2/3, 1) : c'est un filtre grossier, utile pour repérer les échecs nets. Pour départager deux descriptions proches, augmenter les essais ou les requêtes et comparer sur les mêmes requêtes ([[99-statistiques-decisions-experimentales|décisions expérimentales]]).

---

Pourquoi séparer entraînement et validation quand on optimise la description d'une skill ? <!--anki:6532353735343935346136643462366139383036366366646334353062303065-->
?
Parce qu'on peut **sur-ajuster** la description aux formulations testées, par exemple en y recopiant les mots des requêtes ratées. Le guide Agent Skills propose environ **60 % d'entraînement et 40 % de validation**, avec la même proportion de positifs de chaque côté et une partition fixe.

Les échecs d'entraînement guident les modifications ; la validation sert seulement à choisir la **meilleure itération**, qui n'est pas forcément la dernière. Cinq itérations suffisent souvent. Finir par 5 à 10 requêtes neuves. Même logique qu'en [[12-optimisation-automatique-prompts|optimisation automatique de prompts]].

---

Comment mesurer l'utilité d'une skill sur une tâche ? <!--anki:3162636334353065633865393434323039313063356530646665376431313634-->
?
Par des **exécutions appariées** : chaque cas de test tourne avec la skill et sans elle, ou avec la version précédente, à prompt, fichiers d'entrée et modèle identiques, chacun dans un **contexte neuf** (sous-agent ou session séparée). On compare réussite, tokens et durée.

Le contexte neuf garantit que l'agent ne suit que le `SKILL.md`, pas des souvenirs de la session où la skill a été écrite. L'appariement retire de la comparaison la difficulté propre de chaque cas : on regarde ce que la skill change, cas par cas, avant la moyenne.

---

À ne pas confondre : référence sans skill et référence ancienne version pour évaluer une skill ? <!--anki:6332383263363764646161353463346239626134623634343765336638633663-->
?
La référence **sans skill** mesure la **valeur absolue** : la skill apporte-t-elle quelque chose au modèle nu ? La référence **ancienne version** mesure l'**effet d'une modification** : la nouvelle rédaction fait-elle mieux que celle qui est déployée ?

Pour la seconde, figer une copie avant de modifier (`cp -r ma-skill/ workspace/skill-snapshot/`) et lancer la référence sur cette copie. Une nouvelle version peut battre l'ancienne tout en restant inutile face au modèle nu, si l'ancienne dégradait déjà le résultat. Lors d'une refonte, garder les deux mesures.

---

Qu'est-ce qu'une bonne assertion pour noter la sortie d'une skill ? <!--anki:3738616236303738306462653465306561633862636234306231363238386165-->
?
Un énoncé **vérifiable** sur la sortie : « le fichier produit est un JSON valide », « le graphique a deux axes étiquetés », « le rapport contient au moins trois recommandations ».

À éviter : le vague (« la sortie est bonne ») et le fragile (« contient exactement la phrase Total Revenue »), qui rejette une sortie correcte autrement formulée. Écrire les assertions **après un premier essai**, quand on voit à quoi ressemble une bonne sortie. Confier les contrôles mécaniques à un script, les critères de lecture à un [[95-llm-as-judge|juge LLM]] et le style à la revue humaine.

---

Comment noter les assertions d'un eval de skill avec un juge LLM sans complaisance ? <!--anki:6664636133336662373933333435353238336365653130363032663338303630-->
?
Exiger une **preuve citée** pour chaque PASS : le juge renseigne `passed` et une `evidence` qui cite ou désigne la sortie. Un titre « Résumé » suivi d'une phrase vague est un FAIL : l'étiquette est là, pas le contenu.

Pendant la notation, juger aussi les assertions : trop faciles, impossibles ou invérifiables à partir de la sortie. Pour comparer deux versions sur des qualités globales, utiliser une **comparaison à l'aveugle** où le juge ignore quelle version a produit quelle sortie. Deux sorties qui passent toutes les assertions peuvent encore différer nettement.

---

Quelles assertions retirer ou corriger après une itération d'eval de skill ? <!--anki:6464376138346662613533623463633038643831376265623632343133343030-->
?
Lire les résultats **par assertion et par configuration** :
- **réussie avec et sans skill** : n'apprend rien et gonfle le score avec skill ; la retirer ou la durcir ;
- **échouée avec et sans skill** : assertion cassée, cas trop dur ou mauvaise cible ; corriger d'abord ;
- **réussie avec, échouée sans** : là se trouve l'apport ; identifier l'instruction ou le script décisif ;
- **instable d'un essai à l'autre** : consigne ambiguë ou eval sensible au hasard ; ajouter un exemple.

---

Calcul : avec la skill, 83 % de réussite pour 3 800 tokens par essai ; sans, 33 % pour 2 100 tokens. Combien de tokens coûte un succès dans chaque configuration ? <!--anki:3764333164633334613337643437626439363831306534386130366263376365-->
?
Tokens dépensés par tâche réussie :
```text
avec skill : 3 800 / 0,83 ≈ 4 580 tokens par succès
sans skill : 2 100 / 0,33 ≈ 6 360 tokens par succès
delta par essai : +50 points de réussite, +1 700 tokens
```
La skill coûte plus **par essai** mais moins **par succès**. Le calcul suppose qu'un échec n'a pas d'autre coût ; s'il entraîne une reprise humaine, l'écart se creuse. À l'inverse, doubler les tokens pour +2 points ne se justifie que si chaque succès vaut cher. Compléter par la durée et la variance entre essais.

---

Que mesure SkillsBench et que montre-t-il sur les skills curées ? <!--anki:3239316636363464646531623430363062333334323765646533656134316266-->
?
**SkillsBench** (version 4, juin 2026) compare 87 tâches de 8 domaines **sans skill** et **avec skills curées**, sur 18 couples modèle-harness, avec des vérificateurs déterministes et trois essais par cellule. La réussite moyenne passe de **33,9 % à 50,5 %** (+16,6 points).

Les 18 configurations progressent, de +4,1 à +25,7 points, mais **13 tâches sur 87** reculent : un gain moyen ne garantit pas un gain par tâche. Par domaine, le gain va de +9,7 points (mathématiques et recherche opérationnelle) à +28,8 (sciences naturelles). Les tâches sont au format [[90-016-harbor-evaluation-agents|Harbor]].

---

Pourquoi les skills auto-générées par l'agent n'aident-elles pas dans SkillsBench ? <!--anki:6337656231656538646634623464663462356562663930626537316661303934-->
?
Quand l'agent rédige ses propres skills avant de résoudre la tâche, le résultat passe **sous la référence sans skill** sur les trois configurations testées, de −8,1 à −11,5 points, alors que les skills curées y apportent +18,2 à +24,8 points.

L'audit des trajectoires relève des skills jamais découvertes, du temps passé à écrire au lieu de résoudre, et un contenu **faux mais affirmé**. Un modèle ne s'enseigne pas un savoir procédural qu'il n'a pas : la valeur vient d'une connaissance extérieure et vérifiée. Toute skill générée se teste donc avant d'être partagée.

---

Quelle taille de skill donne le meilleur gain dans SkillsBench ? <!--anki:3738393666333335666264653462383938346166373762336163386265626465-->
?
Des skills **ciblées** : une skill apporte +18,0 points et deux ou trois +19,0, contre +10,1 à partir de quatre. Côté longueur, les formats compact (+19,0) et standard (+21,5) dépassent le détaillé (+14,5) ; la documentation exhaustive n'apporte presque rien (+0,7).

Ce sont des corrélations observées sur un banc de tâches, pas une loi : une procédure longue est parfois nécessaire. Elles rejoignent le guide Agent Skills : garder la skill **sobre**, expliquer le pourquoi des consignes et retirer celles dont les traces montrent qu'elles font travailler l'agent pour rien.

---

Calcul : sans skill, 33,9 % de réussite ; avec, 50,5 %. Quel est le gain normalisé g = (p_avec − p_sans) / (1 − p_sans) ? <!--anki:3566663366313435376536303430343262333236393565646332666339633434-->
?
Le gain normalisé rapporte le progrès à la marge restante :
```text
g = (0,505 − 0,339) / (1 − 0,339) = 0,166 / 0,661 ≈ 0,251
```
La skill comble environ **25 % des échecs** de la référence. Ce calcul sur les moyennes globales diffère des 25,5 % publiés par SkillsBench, qui calcule g **par configuration puis fait la moyenne** : l'ordre d'agrégation change le résultat. Le gain normalisé compare des configurations de niveaux différents, mais devient instable quand la référence approche 100 %.

---

Comment éviter qu'une skill évaluée contienne la solution de la tâche ? <!--anki:3161303163616633383030343462323062363439393563623335656363303166-->
?
En traitant la **fuite** comme un critère d'acceptation. SkillsBench refuse les skills qui contiennent des noms de fichiers ou chemins propres à la tâche, la séquence exacte de commandes qui la résout, des constantes de l'énoncé ou des références aux tests.

Les skills sont écrites indépendamment des tâches, et l'instruction ne nomme jamais la skill à utiliser. Un contrôle automatique cherche les fuites de la skill vers la solution, avant la revue humaine. Sans cela, on mesure la capacité de l'agent à recopier une réponse, pas la valeur d'un savoir réutilisable.

---

À ne pas confondre : skill invoquée et skill utile ? <!--anki:6662663365636162383132623434613138313639393762663062346135643438-->
?
**Invoquée** : la trajectoire montre que l'agent a lu ou appelé la skill. **Utile** : le résultat vérifié s'améliore par rapport à la référence.

Une skill peut être lue puis ignorée : SkillsBench observe des harness qui accusent réception du contenu sans l'appliquer. Elle peut aussi être lue et nuire si son contenu est faux. Mesurer les deux : taux d'invocation, puis réussite **conditionnelle** à l'invocation. Découverte rare : travailler la description. Lecture sans effet : travailler le corps de la skill.

---

## Mises en situation

Mise en situation : d'après les traces, la skill interne « migration-schema » de ton équipe n'est chargée que dans 3 sessions sur 10 où elle aurait servi. Comment améliores-tu son déclenchement sans la faire charger partout ? <!--anki:6131643030396466666235313465353039656130653939336531353262356435-->
?
1. **Construire le jeu** : 20 requêtes réalistes tirées des traces, dont 8 à 10 near-misses, comme une requête SQL simple ou une correction de données.
2. **Mesurer** : 3 essais par requête, taux de déclenchement par requête, partition fixe 60/40.
3. **Diagnostiquer** les positifs manqués : intention non couverte, ou tâche que l'agent juge faisable seul.
4. **Réécrire** la description à l'impératif, centrée sur l'intention, en précisant ce que la skill ne couvre pas.
5. **Retenir** l'itération au meilleur score de validation, puis tester 5 à 10 requêtes neuves.
6. **Vérifier l'utilité** : les sessions qui chargent la skill réussissent-elles mieux ?

**Piège** : recopier les mots des requêtes ratées dans la description.

---

Mise en situation : une nouvelle version d'une skill de rédaction de rapports passe de 72 % à 80 % de réussite sur 25 cas, avec un seul essai par cas. Ton équipe veut la publier. Que vérifies-tu ? <!--anki:3234373564376632646337303433396661633833373865363836366264336135-->
?
1. **Ramener à l'échelle** : 8 points sur 25 cas, c'est 2 cas ; regarder lesquels changent de statut, dans les deux sens.
2. **Apparier** : comparer cas par cas ancienne et nouvelle version, et lister les régressions.
3. **Répéter** : 3 à 5 essais par cas et par version pour séparer l'effet de la [[114-reproductibilite-variance|variance]].
4. **Contrôler le coût** : tokens et durée par succès.
5. **Relire** les sorties en comparaison à l'aveugle et retirer les assertions toujours vraies.
6. **Décider** selon un seuil fixé avant l'essai ([[99-statistiques-decisions-experimentales|décisions expérimentales]]).

**Piège** : publier sur un écart de deux cas.

---

Mise en situation : ta plateforme veut laisser les agents écrire eux-mêmes des skills à partir de leurs sessions réussies, puis les partager à toute l'équipe. Quelles conditions poses-tu ? <!--anki:3561303130366662306336303433633862656130653761323839336235323264-->
?
1. **Ne pas présumer de gain** : dans SkillsBench, les skills auto-générées font moins bien que l'absence de skill.
2. **Valider le format** avec `skills-ref validate`, puis relire le contenu et les scripts ([[104-securite-mcp-skills|sécurité des skills]]).
3. **Évaluer avant partage** : exécutions appariées avec et sans skill, sur des tâches autres que la session d'origine.
4. **Chercher la fuite** : chemins, constantes ou commandes propres à une seule tâche.
5. **Publier en quarantaine** : version, auteur, digest, puis suivi du déclenchement et de l'utilité en production.
6. **Retirer** les skills sans gain mesuré.

**Piège** : juger la skill sur la tâche qui l'a produite.

---

## Sources

- [Agent Skills — spécification](https://agentskills.io/specification)
- [Agent Skills — Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)
- [Agent Skills — Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [SkillsBench — Benchmarking How Well Agent Skills Work Across Diverse Tasks, arXiv 2602.12670, version 4 du 14 juin 2026](https://arxiv.org/abs/2602.12670v4)
- [Harbor — Skills](https://docs.harborframework.com/jobs/skills)

## Connexions
- [[90-015-agent-skills-format-skills-ref|Agent Skills & skills-ref]] — le contrôle statique du format, avant tout essai
- [[90-016-harbor-evaluation-agents|Harbor]] — exécuter en conteneurs les essais avec et sans skill
- [[34-harness-plugins|Harness & plugins]] — ce qu'est une skill et comment le harness la charge
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — les risques d'une skill partagée
- [[96-evals-rag-agents|Évaluation des RAG & des agents]] — résultat, trajectoire et environnements d'eval
- [[94-evals-methodologie|Méthodologie des evals]] — jeux de test, références et régressions
- [[95-llm-as-judge|LLM-as-a-judge]] — noter les assertions qui exigent une lecture
- [[99-statistiques-decisions-experimentales|Statistiques & décisions expérimentales]] — décider sur peu de cas appariés
- [[12-optimisation-automatique-prompts|Optimisation automatique de prompts]] — le même risque de sur-ajustement que la description
- [[35-context-engineering|Context engineering]] — le catalogue de skills comme budget de contexte
- [[00-moc-ai-engineering|MOC AI Engineering]]
