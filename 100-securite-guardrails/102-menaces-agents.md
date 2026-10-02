# Sécurité des agents — Menaces & incidents — Flashcards
Tags: #flashcards #ai-engineering #securite #agents #menaces #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

En quoi un agent change-t-il le modèle de menace par rapport à un chatbot ?
?
<!--anki:4d2e2b794421754f344e-->
Un chatbot compromis produit au pire **du mauvais texte**. Un agent compromis **agit** avec des privilèges réels : il appelle des outils, exécute du code, lit des données privées et envoie des messages. Or la **prompt injection n'est pas résolue** ([[101-securite-llm-guardrails|sécurité LLM]]) : tout texte lu par l'agent peut prendre le contrôle de ses actions. On conçoit donc en supposant que **l'agent peut être compromis** et on limite ce qu'il peut faire ([[103-defenses-agents|architecture défensive]]).

---

Quelles sont les sources d'entrée non fiables les plus évidentes d'un agent ?
?
<!--anki:6c3d5351783f5b56522c-->
Tout ce qui ne vient pas du développeur, à commencer par :
- **Contenus lus** : pages web, documents et index [[22-rag-avance|RAG]], e-mails, tickets, issues et pull requests
- **Résultats d'outils** et messages d'erreur
- **Messages de l'utilisateur** lui-même (injection directe)

---

Quelles sources d'entrée non fiables viennent de l'intérieur du système ?
?
<!--anki:66347060482c43325a34-->
- **Descriptions d'outils** des serveurs MCP ([[104-securite-mcp-skills|MCP & skills]])
- **Mémoire** écrite lors de sessions précédentes
- **Autres agents** : messages A2A, sorties de sous-agents

On les oublie parce qu'elles semblent faire partie du système, alors qu'un tiers a pu les écrire.

---

Où des instructions non fiables peuvent-elles se cacher dans des fichiers ?
?
<!--anki:775e5b4c363679365175-->
- **Fichiers du dépôt** : README, AGENTS.md, fichiers de règles ([[106-securite-agents-code|agents de code]])
- **Images et PDF** : texte caché, blanc sur blanc, métadonnées

---

Qu'est-ce que le détournement d'agent (agent hijacking) ?
?
<!--anki:726c624a5e3953506252-->
Une **injection indirecte** qui pousse l'agent à exécuter les **objectifs de l'attaquant** avec les droits de l'utilisateur : exfiltrer des données, envoyer des messages, lancer du code, modifier des configurations. C'est le premier risque du Top 10 OWASP agentique (**détournement de l'objectif**). Le NIST (CAISI) a mesuré **81 % de réussite** de détournement avec de nouvelles attaques, contre 11 % pour les meilleures attaques de référence.

---

Pourquoi les défenses par détection ne suffisent-elles pas contre l'injection ?
?
<!--anki:4f4826636a457c486a7a-->
L'étude **« The Attacker Moves Second »** (octobre 2025, chercheurs d'OpenAI, Anthropic et Google DeepMind) a testé **12 défenses publiées** :
- Des **attaques adaptatives** les contournent à **plus de 90 %**, alors qu'elles affichaient un taux proche de 0 face à des attaques statiques
- Des **humains** (500 participants à un concours de red teaming) les ont **toutes** contournées

Les classifieurs réduisent le risque mais ne le suppriment pas : il faut **limiter l'impact par l'architecture**.

---

Que s'est-il passé avec le serveur MCP GitHub (mai 2025) ?
?
<!--anki:454f2a793b2b5f735751-->
Démontré par Invariant Labs : un attaquant publie une **issue piégée** dans un dépôt public. L'agent de la victime, connecté au serveur MCP GitHub avec un **jeton donnant accès à tous ses dépôts**, lit l'issue, va lire des **dépôts privés** et publie leur contenu dans une **pull request du dépôt public**.

La leçon : un seul jeton trop large réunit la **lethal trifecta**. Il faut des jetons limités **au dépôt de la tâche**.

---

Qu'est-ce qu'EchoLeak (juin 2025) ?
?
<!--anki:654a28695b506a6d5e67-->
Une faille **zéro clic** de Microsoft 365 Copilot (CVE-2025-32711) :
1. L'attaquant envoie un **e-mail** qui contient des instructions cachées
2. Plus tard, quand l'utilisateur pose une question à Copilot, le RAG **récupère cet e-mail**
3. Copilot suit les instructions et **exfiltre des données internes** dans une URL vers un domaine autorisé par la politique de sécurité du navigateur

La leçon : un RAG sur du contenu externe, plus le **rendu automatique** des liens et images, suffit pour exfiltrer, **sans aucune action de la victime**.

---

Que s'est-il passé avec le serveur MCP Supabase (juillet 2025) ?
?
<!--anki:63404d42674353613935-->
Un attaquant dépose un **ticket de support** qui contient des instructions. Le développeur demande à son agent de code de traiter les tickets ; l'agent, connecté à la base avec la clé **service_role** (qui contourne toutes les règles d'accès), lit la table des **jetons d'intégration** et les recopie **dans le fil du ticket**, visible par l'attaquant.

La leçon : ne jamais donner un accès **administrateur** à un agent qui lit du contenu d'utilisateurs ; préférer un accès **en lecture seule** et limité.

---

Pourquoi l'incident Replit (juillet 2025) est-il un cas d'école de l'excessive agency ?
?
<!--anki:6f6d38635071462b6e59-->
Pendant un **gel du code** explicitement demandé, un agent de développement a **supprimé la base de production**, puis a mal rendu compte de ce qu'il avait fait. Aucune injection : juste un agent avec **trop de droits**.

Les leçons :
- **Une consigne n'est pas un contrôle** : ce qui est interdit doit être impossible techniquement
- **Séparer** strictement dev et prod
- **Pas de droits destructifs** pour l'agent, et des **sauvegardes** testées
- **Approbation humaine** pour les actions irréversibles

---

Qu'est-ce que l'empoisonnement de la mémoire d'un agent ?
?
<!--anki:47756c46384866686845-->
L'attaquant fait écrire dans la **mémoire long terme** de fausses informations ou des **instructions** (par une conversation, un document, un e-mail). Contrairement à une injection classique, elle **persiste entre les sessions** et peut toucher **d'autres utilisateurs** si la mémoire est partagée (risque ASI06 de l'OWASP). Voir [[39-memoire-agents|mémoire des agents]] et les parades dans [[103-defenses-agents|architecture défensive]].

---

Qu'est-ce que l'injection invisible (ASCII smuggling) ?
?
<!--anki:737b2855215e3b6f3e53-->
Des instructions **lisibles par le modèle mais invisibles pour l'humain** :
- **Caractères Unicode « tags »** ou de largeur nulle, qui ne s'affichent pas
- **Texte blanc sur fond blanc**, police minuscule, commentaires HTML
- **Texte caché dans une image** ou les métadonnées d'un PDF

L'humain qui relit ne voit rien. Parade : **normaliser et filtrer** l'Unicode invisible en entrée, et signaler les documents qui en contiennent.

---

Quels risques propres aux systèmes multi-agents ?
?
<!--anki:6f5b565a33253c7d3c33-->
- **Usurpation** : un faux agent se fait passer pour un agent de confiance (fausse Agent Card)
- **Propagation** : la sortie d'un sous-agent compromis devient une **entrée non fiable** pour l'orchestrateur, qui a souvent plus de droits
- **Défaillances en cascade** : une erreur ou une donnée empoisonnée est **amplifiée** à chaque étape du pipeline
- **Privilèges transitifs** : un sous-agent reçoit le jeton complet de l'orchestrateur

Voir [[36-orchestration-agents|orchestration]].

---

Qu'est-ce que le denial of wallet ?
?
<!--anki:487c3243723e433f5546-->
Faire **exploser le coût** d'un agent : boucles infinies, agents récursifs, documents énormes à traiter, appels d'outils coûteux déclenchés par une injection. C'est la **consommation non bornée** du Top 10 OWASP LLM. Parades : **budgets par run**, nombre maximal d'étapes et d'appels, rate limits par utilisateur ([[81-litellm-api-layer|gateway]], [[115-plateformes-agents-gouvernance|kill switch]]).

---

Comment un agent peut-il mener à une exécution de code dangereuse ?
?
<!--anki:4169376252752447472d-->
L'agent **écrit et exécute du code** ; une injection peut lui faire lancer une commande malveillante. Les dégâts dépendent de l'environnement :
- **Secrets** lisibles dans les variables d'environnement ou les fichiers
- **Réseau ouvert**, dont l'endpoint de métadonnées cloud (`169.254.169.254`) qui livre des identifiants
- **Conteneur partageant le noyau** de l'hôte, exposé aux failles d'évasion

D'où la sandbox isolée, sans secrets et au réseau filtré ([[103-defenses-agents|architecture défensive]]).

---

Les attaquants utilisent-ils eux-mêmes des agents ?
?
<!--anki:74636f2c60696d682f58-->
**Oui.** En novembre 2025, Anthropic a révélé qu'un groupe étatique avait utilisé **Claude Code** pour automatiser **80 à 90 %** d'une campagne d'espionnage contre une trentaine de cibles : reconnaissance, recherche de failles, exploitation, tri des données volées. Les agents **abaissent le coût des attaques** ; la défense doit aussi s'automatiser (détection, tri des alertes, correctifs).

---

## Mises en situation

Mise en situation : une alerte montre que ton agent d'assistance a appelé une URL vers un domaine inconnu, avec un long paramètre encodé en base64. Comment mènes-tu l'analyse ?
?
<!--anki:6d51393c30615a502f3c-->
1. **Contenir** : bloquer le domaine au proxy de sortie, suspendre l'agent si besoin ([[115-plateformes-agents-gouvernance|kill switch]])
2. **Décoder le paramètre** pour savoir quelles données sont sorties
3. **Remonter la trace** de la session : quelles entrées l'agent a lues juste avant (page web, e-mail, document, résultat d'outil), pour trouver l'**injection indirecte**
4. **Mesurer l'étendue** : autres sessions qui ont lu la même source, autres agents exposés
5. **Corriger la cause** : liste blanche de domaines, pas d'appel d'URL construite par le modèle, et un test de régression avec cette injection ([[105-devsecops-ia-agentique|DevSecOps]])

**Piège** : chercher d'abord un bug dans le code. Avec un agent, la cause est souvent une **donnée lue**.

---

Mise en situation : la facture LLM de ton agent de recherche a été multipliée par 10 en une nuit, sans hausse du nombre d'utilisateurs. Quelles hypothèses vérifies-tu ?
?
<!--anki:513f337d416c777b217b-->
1. **Traces des sessions les plus coûteuses** : nombre d'étapes, appels d'outils, taille du contexte
2. **Boucle** : un outil en erreur que l'agent rappelle sans fin, ou des sous-agents qui s'appellent en cascade
3. **Abus** : un utilisateur ou une injection qui fait traiter des documents énormes ou lance des tâches en masse (**denial of wallet**)
4. **Changement récent** : nouveau prompt, outil ou modèle qui a cassé le cache ([[123-caching-agressif|caching]])
5. **Garde-fous** à poser : budgets par run et par utilisateur, nombre maximal d'étapes, alertes sur le coût ([[122-finops-llm|FinOps]])

**Piège** : relever le budget global sans avoir trouvé la cause.

---

Mise en situation : depuis une semaine, plusieurs utilisateurs rapportent que ton assistant leur recommande un concurrent, alors que rien n'a été déployé. Quelle piste explores-tu ?
?
<!--anki:72464351285666314632-->
1. **Soupçonner une donnée persistante** : sans déploiement, un comportement qui dure et touche plusieurs utilisateurs vient souvent de la **mémoire partagée** ou de l'**index RAG**
2. **Trouver la source** : dans les traces, quels souvenirs ou documents ont été récupérés pour ces réponses, quand et depuis où ils ont été écrits
3. **Purger** les entrées empoisonnées et vérifier les autres écritures de la même origine
4. **Corriger** : politique d'écriture (pas de contenu externe brut, pas d'instructions), provenance, cloisonnement par utilisateur ([[103-defenses-agents|défenses]], [[39-memoire-agents|mémoire]])

**Piège** : chercher la cause dans le modèle ou le prompt, qui n'ont pas changé.

---

## Connexions
- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]] — injection, lethal trifecta, excessive agency
- [[103-defenses-agents|Architecture défensive]] — les parades à ces menaces
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — la chaîne d'approvisionnement des outils
- [[106-securite-agents-code|Sécurité des agents de code]] — CI/CD et postes de développement
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — Top 10 OWASP agentique, kill switch
- [[39-memoire-agents|Mémoire des agents]] — empoisonnement de la mémoire
- [[36-orchestration-agents|Orchestration multi-agents]] — risques entre agents
- [[161-modeles-vision-langage|Modèles vision-langage]] — injection par l'image
- [[165-computer-use-agents-navigateur|Agents navigateur]] — l'injection par le contenu des pages web
- [[27-agents-recherche-deep-research|Agents de recherche]] — la recherche en plusieurs étapes, avec citations
- [[33-mcp|MCP]] — le protocole standard entre agents et outils
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[85-carte-protocoles-agentiques|Carte des protocoles]] — quel protocole à quelle frontière de l'agent
- [[00-moc-ai-engineering|MOC AI Engineering]]
