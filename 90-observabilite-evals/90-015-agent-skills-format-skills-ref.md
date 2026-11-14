# Agent Skills : format & validation avec skills-ref — Flashcards
Tags: #flashcards #ai-engineering #agents #skills #evals #ci
Vérifié le : 14 novembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: spécification ouverte Agent Skills, emplacement non imposé, champs obligatoires et facultatifs, règles du nom et de la description, budget de divulgation progressive, skills-ref (validate, read-properties, to-prompt), contrôles de structure et de champs, angles morts du validateur, champs inconnus, noms Unicode, catalogue et coût en tokens, allowed-tools, intégration en CI. -->


Qu'est-ce que la spécification Agent Skills ? <!--anki:6437336336333664616561303462663162313566383262343633346238653566-->
?
Un **format ouvert** qui définit le contenu d'un dossier de skill : un `SKILL.md` obligatoire, avec un frontmatter YAML puis des instructions Markdown, et des dossiers facultatifs `scripts/`, `references/` et `assets/`. Publiée sur agentskills.io sous licence Apache 2.0, elle suit une gouvernance adoptée le 4 novembre 2026, qui prévoit son rattachement à LF Projects.

Le format permet d'écrire une skill une fois et de la faire charger par plusieurs clients. Il ne fixe ni la décision d'activation ni les permissions : un fichier portable ne garantit pas un comportement identique d'un agent à l'autre. La notion de skill elle-même est définie dans [[34-harness-plugins|Harness & plugins]].

---

La spécification Agent Skills impose-t-elle l'emplacement des skills ? <!--anki:3334383034623237633038623438346561353665636661643333393565663030-->
?
**Non** : elle définit le contenu d'un dossier de skill, pas l'endroit où le client le cherche. Chaque client a son répertoire natif ; la convention `.agents/skills/`, au niveau du projet ou de l'utilisateur, s'est imposée pour partager des skills entre clients.

Un client découvre une skill en cherchant des **sous-dossiers contenant exactement `SKILL.md`**, en ignorant `.git/` ou `node_modules/`. Une skill valide peut donc rester invisible si elle est rangée ailleurs que là où l'agent regarde. Tester la découverte dans chaque client visé, pas seulement le format.

---

Quels champs du frontmatter d'un SKILL.md sont obligatoires ? <!--anki:6166303831373335613962613462306339323730316135623036336662303936-->
?
Deux : **`name`** et **`description`**. Les champs facultatifs sont `license`, `compatibility` (exigences d'environnement, 500 caractères au plus), `metadata` (table de clés et valeurs texte) et `allowed-tools`, expérimental.

```markdown
---
name: analyse-csv
description: Analyse des fichiers CSV et produit des graphiques. Utiliser quand l'utilisateur fournit un CSV ou un tableur à explorer, même sans dire CSV.
metadata:
  version: "1.2"
---
```

Réserver `compatibility` aux besoins réels : paquets système, accès réseau, produit visé. Les informations propres à une équipe, comme la version ou le propriétaire, vont dans `metadata`.

---

Quelles règles doit respecter le champ name d'une skill ? <!--anki:6637373863643732613765323438633339313565306538656537383138386663-->
?
Selon la spécification : **1 à 64 caractères**, minuscules, chiffres et tirets seulement, sans tiret au début ni à la fin, sans double tiret, et **identique au nom du dossier**.

`pdf-processing` est valide ; `PDF-Processing`, `-pdf`, `pdf--processing` et `pdf_processing` ne le sont pas. La correspondance avec le dossier est la règle la plus facile à casser : renommer le dossier sans modifier le frontmatter invalide la skill. Le nom sert d'identifiant ; c'est la description qui décide du déclenchement.

---

Que doit contenir la description d'une skill selon la spécification Agent Skills ? <!--anki:3465666463643461303735383435326461666263393765663362613165643764-->
?
**Ce que fait la skill et quand l'utiliser**, avec des mots-clés qu'un utilisateur emploierait. Elle compte 1 à **1 024 caractères**.

« Aide avec les PDF » est trop pauvre. « Extrait texte et tableaux de PDF, remplit des formulaires, fusionne des fichiers. Utiliser quand l'utilisateur manipule des PDF ou parle de formulaires » donne à l'agent de quoi décider. Un validateur contrôle la longueur ; la qualité du déclenchement ne se juge qu'en essayant des requêtes ([[90-014-evaluation-skills-agents|eval de déclenchement]]).

---

Quel budget de contexte la spécification Agent Skills recommande-t-elle pour chaque niveau d'une skill ? <!--anki:6661313736373864623665323466323838373230336238366266643863396366-->
?
Trois niveaux de [[34-harness-plugins|divulgation progressive]] :
1. **Métadonnées** (`name`, `description`) : environ 100 tokens, chargées au démarrage pour toutes les skills.
2. **Instructions**, le corps du `SKILL.md` : moins de 5 000 tokens recommandés, chargées à l'activation ; fichier sous **500 lignes**.
3. **Ressources** (`scripts/`, `references/`, `assets/`) : chargées seulement si les instructions y renvoient.

Les renvois se font en chemins relatifs, **à un seul niveau** depuis `SKILL.md`. Une chaîne de renvois imbriqués oblige l'agent à ouvrir plusieurs fichiers pour trouver une consigne, ou à s'arrêter avant.

---

Qu'est-ce que skills-ref ? <!--anki:3066306630323336303930633434663738663162363137336438623639393961-->
?
La **bibliothèque de référence** de la spécification Agent Skills, en Python 3.11 ou plus, sous licence Apache 2.0. Elle offre une API et une CLI :
- `skills-ref validate <dossier>` : contrôle le frontmatter et le nommage ;
- `skills-ref read-properties <dossier>` : affiche les propriétés en JSON ;
- `skills-ref to-prompt <dossiers…>` : génère le bloc `<available_skills>` d'un prompt.

Son README la destine à la **démonstration**, pas à la production. Elle sert de définition exécutable des règles ; une chaîne de publication y ajoute ses propres contrôles.

---

Que vérifie skills-ref validate sur la structure d'un dossier de skill ? <!--anki:3162323035306264336232393433393039613263373031663236613762353664-->
?
Avant les champs, la structure :
- le chemin existe et désigne un **dossier** ; un chemin vers `SKILL.md` est ramené à son dossier ;
- il contient `SKILL.md`, ou à défaut `skill.md` ;
- le fichier **commence par `---`** et le frontmatter est refermé ;
- le YAML se lit avec **strictyaml** et forme une table.

La commande sort avec le code **0** si la skill est valide, **1** sinon, et liste les problèmes sur la sortie d'erreur. Ce code suffit pour bloquer un commit ou une CI.

---

Quels contrôles skills-ref validate applique-t-il aux champs du frontmatter ? <!--anki:6566656234653837303330643430313362356237313631633039336135626530-->
?
- **Champs connus seulement** : tout champ hors `name`, `description`, `license`, `allowed-tools`, `metadata` et `compatibility` est une erreur.
- **`name`** présent et non vide, normalisé en Unicode NFKC, puis contrôlé : longueur, minuscules, tirets, nom du dossier.
- **`description`** présente, non vide, 1 024 caractères au plus.
- **`compatibility`** : texte de 500 caractères au plus.

Aucun contrôle ne porte sur le contenu de `license`, `allowed-tools` ou des valeurs de `metadata`, ni sur le corps du fichier.

---

Que ne vérifie pas skills-ref validate ? <!--anki:3436343764643935656537323461636538373438313366396537663661663539-->
?
Tout ce qui dépasse le frontmatter :
- la **taille du corps** : 500 lignes et 5 000 tokens recommandés ;
- les **liens** vers `references/` ou `scripts/`, qui peuvent être cassés ;
- l'exécution et la sûreté des **scripts** ;
- la **qualité de la description** et son déclenchement ;
- la **sécurité** : instructions cachées, exfiltration, dépendances.

Une skill « valide » est seulement **lisible** par un client conforme. Le déclenchement et l'utilité se mesurent par des essais ([[90-014-evaluation-skills-agents|évaluation des skills]]) ; le risque se traite par revue ([[104-securite-mcp-skills|sécurité des skills]]).

---

Pourquoi skills-ref rejette-t-il un champ version placé à la racine du frontmatter ? <!--anki:6364336336306366306463613439393062373935366536366136386530303131-->
?
Parce que le validateur n'accepte que les **six champs** de la spécification : `version: 1.2` à la racine produit « Unexpected fields in frontmatter ». Une donnée propre à une équipe ou à un client va dans `metadata`, table de clés et valeurs texte :

```yaml
metadata:
  version: "1.2"
  owner: equipe-data
```

Le même raisonnement vaut pour l'extension d'un client : un champ propre à un produit, placé à la racine, échoue au validateur de référence. Soit on documente cet écart, soit on garde la skill portable. Préfixer les clés de `metadata` limite les collisions entre clients.

---

À ne pas confondre : skills-ref read-properties et skills-ref validate ? <!--anki:6436646364333035663566313433383738313436393632613535636431643861-->
?
**`read-properties`** lit le frontmatter et renvoie les propriétés en JSON ; il exige seulement un YAML lisible, un `name` et une `description` non vides. **`validate`** applique toutes les règles : champs autorisés, format du nom, correspondance avec le dossier, longueurs.

Une skill nommée `Analyse-CSV` dans un dossier `analyse-csv` passe `read-properties` mais échoue à `validate`. Employer `read-properties` pour extraire des métadonnées dans un script, `validate` comme porte de qualité. `to-prompt` repose sur la même lecture que `read-properties` : il ne valide pas non plus.

---

Quelle divergence existe entre la spécification Agent Skills et skills-ref sur les caractères du nom ? <!--anki:3062616536643966653031393434393439633666386665623766663166316361-->
?
La spécification parle de caractères alphanumériques minuscules en citant `a-z`, `0-9` et le tiret. Le validateur accepte toute **lettre Unicode** minuscule après normalisation NFKC : ses tests valident `мой-навык` ou `技能`, et refusent `НАВЫК`, écrit en majuscules.

Conséquence : `données-csv` passe `skills-ref validate` mais peut être refusé par un client qui applique la règle ASCII. Pour une skill partagée, s'en tenir à l'**ASCII minuscule** et ajouter ce contrôle en CI. Un validateur de référence ne remplace pas un essai dans chaque client visé.

---

Que produit skills-ref to-prompt et à quoi sert-il ? <!--anki:3133356439623536316239623430356638303563616331326438363737336134-->
?
Un bloc XML `<available_skills>` qui donne, pour chaque skill, `<name>`, `<description>` et `<location>`, le chemin absolu du `SKILL.md` :

```xml
<available_skills>
<skill>
<name>analyse-csv</name>
<description>Analyse des fichiers CSV…</description>
<location>/home/u/.agents/skills/analyse-csv/SKILL.md</location>
</skill>
</available_skills>
```

C'est le **catalogue** qu'un harness maison place dans le prompt ; le README le recommande pour les modèles d'Anthropic, d'autres clients formatent autrement. Il permet aussi de mesurer le coût du catalogue et de voir, hors client, ce que lit le modèle au démarrage.

---

Calcul : un agent charge 40 skills dont la description fait en moyenne 600 caractères. En comptant environ 4 caractères par token et 30 tokens de balises et de chemin par skill, combien de tokens coûte le catalogue à chaque session ? <!--anki:3365623434316532313665303463306261373064323766333430306664663439-->
?
```text
description : 600 / 4 = 150 tokens
par skill : 150 + 30 = 180 tokens
catalogue : 40 × 180 = 7 200 tokens
```
Environ **7 200 tokens** présents dans chaque session, avant toute tâche. Le ratio de 4 caractères par token est une approximation pour l'anglais ; le français ou le code coûtent souvent davantage : mesurer avec le tokenizer du modèle. Avec des descriptions de 1 024 caractères, le catalogue dépasserait 11 000 tokens. Le [[35-context-engineering|prompt caching]] réduit le coût d'un préfixe stable, pas la place prise dans le contexte.

---

Le champ allowed-tools d'une skill restreint-il ce que l'agent peut faire ? <!--anki:3762333234343435623264653430663039353839616666396639353136353037-->
?
**Non**, d'après la spécification : c'est une liste d'outils **pré-approuvés** que la skill peut utiliser, séparés par des espaces, par exemple `Bash(git:*) Bash(jq:*) Read`. Le champ est **expérimental** et son support varie selon les clients.

Il réduit donc des demandes de confirmation plutôt qu'il n'ajoute une barrière. Une skill tierce qui pré-approuve un shell sans restriction élargit ce que l'agent exécute sans demander. Les restrictions relèvent des **permissions du [[34-harness-plugins|harness]]**, et une skill téléchargée se relit comme du code ([[104-securite-mcp-skills|sécurité des skills]]).

---

Où placer skills-ref validate dans la chaîne de livraison d'un dépôt de skills ? <!--anki:3832376530373632613861663430323262633032666539326234316264643235-->
?
En **pré-commit** et en **CI**, sur chaque dossier de skill :

```bash
fail=0
for d in skills/*/; do
  skills-ref validate "$d" || fail=1
done
exit $fail
```

La boucle valide toutes les skills avant d'échouer, pour afficher toutes les erreurs d'un coup ; le code 1 bloque la fusion. Ajouter ensuite ce que `validate` ignore : lignes du corps, liens relatifs, scripts exécutables, secrets, noms ASCII. Épingler la version de skills-ref : un changement de règle ne doit pas casser la CI sans revue ([[105-devsecops-ia-agentique|DevSecOps]]).

---

## Mises en situation

Mise en situation : une skill passe `skills-ref validate` en CI, mais l'agent de code de ton équipe ne la charge jamais, même sur des demandes évidentes. Comment cherches-tu la cause ? <!--anki:3864363162326234383934303462633438643132373831663965663937323532-->
?
1. **Découverte** : le dossier est-il dans un répertoire que ce client parcourt, `.agents/skills/` ou répertoire natif, au niveau du projet ou de l'utilisateur ?
2. **Catalogue** : la skill figure-t-elle dans la liste que l'agent expose ? Comparer avec la sortie de `to-prompt`.
3. **Règles du client** : un nom non ASCII ou un champ racine propre à un autre client peut être refusé.
4. **Description** : dit-elle quand utiliser la skill, en termes d'intention ?
5. **Mesurer** : jeu de déclenchement avec near-misses et plusieurs essais ([[90-014-evaluation-skills-agents|évaluation des skills]]).

**Piège** : conclure que la skill est correcte parce que le validateur passe.

---

Mise en situation : ton équipe maintient 30 skills partagées entre deux agents de code de fournisseurs différents. Quelles règles de dépôt et de CI mets-tu en place ? <!--anki:3931656531636238663461653461386462383866333837313664613935393765-->
?
1. **Format commun** : les six champs de la spécification seulement, extensions dans `metadata` avec des clés préfixées.
2. **Noms ASCII** minuscules, identiques aux dossiers, contrôlés en plus de `skills-ref validate`.
3. **Budget** : corps sous 500 lignes, renvois à un niveau, liens vérifiés.
4. **Revue** des scripts et de `allowed-tools` comme du code ([[104-securite-mcp-skills|chaîne d'approvisionnement]]).
5. **Test par client** : découverte et déclenchement dans chacun des deux agents, sur le même jeu de requêtes.
6. **Versionner** : version de skills-ref épinglée et digest publié pour chaque skill.

**Piège** : tester dans un seul client et supposer la portabilité.

---

## Sources

- [Agent Skills — spécification](https://agentskills.io/specification)
- [Agent Skills — ajouter le support des skills à un agent](https://agentskills.io/client-implementation/adding-skills-support)
- [skills-ref — code source et tests, commit 83021e2 du 4 novembre 2026](https://github.com/agentskills/agentskills/tree/83021e2be457a9b6679148719c1f6074f0ad975e/skills-ref)
- [Agent Skills — gouvernance adoptée le 4 novembre 2026](https://github.com/agentskills/agentskills/blob/83021e2be457a9b6679148719c1f6074f0ad975e/GOVERNANCE.md)

## Connexions
- [[90-014-evaluation-skills-agents|Évaluer des skills d'agent]] — après le format : déclenchement et utilité
- [[90-016-harbor-evaluation-agents|Harbor]] — injecter les skills validées dans des essais en conteneurs
- [[34-harness-plugins|Harness & plugins]] — la notion de skill et les permissions du harness
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — ce que la validation du format ne couvre pas
- [[35-context-engineering|Context engineering]] — le coût du catalogue et la divulgation progressive
- [[105-devsecops-ia-agentique|DevSecOps IA]] — les contrôles en CI d'un dépôt de skills
- [[00-moc-ai-engineering|MOC AI Engineering]]
