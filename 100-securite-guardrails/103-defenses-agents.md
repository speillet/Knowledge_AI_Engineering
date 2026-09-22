# Sécurité des agents — Architecture défensive — Flashcards
Tags: #flashcards #ai-engineering #securite #agents #defense #llm

Quel principe directeur pour sécuriser un agent face à l'injection ?
?
**Supposer la compromission** : n'importe quel texte lu par l'agent peut prendre le contrôle du modèle. La sécurité doit donc être appliquée **hors du modèle**, par du code déterministe, et viser à **limiter ce qu'un agent détourné peut faire** (le rayon d'impact). On empile plusieurs couches (**défense en profondeur**), car aucune n'est parfaite ([[102-menaces-agents|menaces]]).

---

Qu'est-ce que l'Agents Rule of Two de Meta ?
?
Publiée en octobre 2025 : dans une même session, un agent ne doit cumuler **que deux** de ces trois propriétés :
- **[A]** traiter des **entrées non fiables**
- **[B]** accéder à des **données privées ou systèmes sensibles**
- **[C]** **changer un état ou communiquer vers l'extérieur**

Si les trois sont nécessaires, l'agent ne doit **pas agir en autonomie** : supervision humaine au minimum. C'est la version opérationnelle de la [[101-securite-llm-guardrails|lethal trifecta]].

---

Comment appliquer la Rule of Two concrètement ?
?
On retire une propriété selon le cas d'usage :
- **Sans [A]** : l'agent ne lit que des sources de confiance (ex. e-mails d'expéditeurs connus seulement)
- **Sans [B]** : l'agent n'accède à aucune donnée sensible (ex. environnement de test)
- **Sans [C]** : l'agent n'envoie rien seul (ex. brouillon validé par un humain, destinataires limités à une liste)

On peut aussi **découper la tâche en sessions** qui respectent chacune la règle.

---

Quels sont les six design patterns contre l'injection (Beurer-Kellner et al., 2025) ?
?
- **Action-Selector** : l'agent choisit dans une **liste fixe d'actions** et ne voit jamais leur résultat
- **Plan-Then-Execute** : le plan d'appels d'outils est **figé avant** de lire des données non fiables
- **LLM Map-Reduce** : chaque document non fiable est traité par un **sous-agent isolé** sans outils ; seul un résultat structuré remonte
- **Dual LLM** : un LLM **privilégié** (outils, entrées de confiance) et un LLM **en quarantaine** (lit les données, sans outils)
- **Code-Then-Execute** : l'agent écrit un **programme** exécuté ensuite sous contrôle
- **Context-Minimization** : retirer du contexte ce qui n'est plus nécessaire, dont la requête initiale

Le principe : **sacrifier de la généralité** pour une sécurité démontrable.

---

Comment fonctionnent le pattern Dual LLM et CaMeL ?
?
- **Dual LLM** : le LLM privilégié ne voit **jamais** le texte non fiable. Il manipule des **références** (`$email1`) vers les résultats du LLM en quarantaine, qui lit les données mais n'a **aucun outil**
- **CaMeL** (Google DeepMind, 2025) va plus loin : le LLM privilégié écrit un **programme** à partir de la seule demande de l'utilisateur. Un interpréteur **trace la provenance** de chaque valeur et applique des **politiques** avant chaque appel d'outil (ex. interdit d'envoyer un e-mail à une adresse venue d'une donnée non fiable)

---

Comment appliquer le moindre privilège aux outils d'un agent ?
?
- **Outils étroits** plutôt que génériques : `envoyer_au_support()` plutôt que `envoyer_email(destinataire, texte)`
- **Lecture seule par défaut**, écriture activée outil par outil
- **Jetons limités** à la tâche et à la ressource (un dépôt, un dossier), de **courte durée**
- **Droits de l'utilisateur**, jamais un compte administrateur ou de service
- **Liste blanche d'outils** par agent, et identifiants de prod absents des environnements de dev

---

Pourquoi contrôler le réseau sortant d'un agent ?
?
Parce que c'est le canal d'**exfiltration** (la propriété [C]). Les règles :
- **Refus par défaut**, liste blanche de domaines
- **Proxy de sortie** qui bloque les IP privées et l'endpoint de métadonnées cloud (`169.254.169.254`)
- **Pas de chargement automatique** d'images ou de liens externes dans les réponses affichées
- **Filtrage des URL** produites par le modèle, surtout celles qui portent des paramètres

---

Comment gérer les secrets d'un agent ?
?
- **Jamais dans le prompt, le contexte ou la sandbox** : un agent détourné les lirait ou les recopierait
- **Coffre à secrets** et jetons de **courte durée**
- **Injection par la plateforme** : un proxy ou la gateway ajoute l'authentification au moment de l'appel, sans que l'agent voie le jeton (principe « cerveau, mains, session » de [[115-plateformes-agents-gouvernance|la fiche gouvernance]])
- **Masquage** des secrets dans les traces et les logs, et **rotation** immédiate en cas de fuite

---

Comment valider les appels d'outils d'un agent ?
?
Avant exécution, par du code déterministe :
1. **Schéma** : types, formats, bornes ([[32-tool-calling|tool calling]])
2. **Règles métier** : montant maximal, destinataires autorisés, périmètre de données
3. **Moteur de politiques** : Cedar ou OPA, refus par défaut ([[115-plateformes-agents-gouvernance|gouvernance]])
4. **Provenance** : un paramètre sensible (destinataire, URL, commande) ne doit pas venir d'une donnée non fiable
5. **Quotas** et, pour les actions à risque, **prévisualisation** puis approbation

---

Pourquoi l'approbation humaine peut-elle échouer et comment la rendre fiable ?
?
Elle échoue par **fatigue** (tout valider sans lire) et parce qu'un agent détourné peut **décrire faussement** son action (« j'envoie le rapport à l'équipe »). Pour la fiabiliser :
- Afficher les **paramètres réels** calculés par le code, pas le résumé du modèle
- Ne demander l'approbation que pour les **actions à risque**
- Confirmation **hors bande** (notification, second canal) pour les plus sensibles
- Un agent ne doit **jamais** pouvoir déclencher ou simuler l'approbation lui-même

---

Quel rôle pour les guardrails et classifieurs d'injection ?
?
Une **couche utile mais contournable** ([[102-menaces-agents|attaques adaptatives]]) :
- **Classifieurs d'entrée** : Prompt Guard, Azure Prompt Shields, Lakera…
- **Spotlighting** : délimiter ou marquer les données non fiables pour que le modèle les traite comme des données
- **Hiérarchie d'instructions** apprise par le modèle (système > développeur > utilisateur > outils)
- **Filtres de sortie** : fuite de données, contenu, format

Ils réduisent le taux de réussite et fournissent des **signaux de détection**, mais ne remplacent jamais les contrôles d'architecture.

---

Comment protéger la mémoire d'un agent ?
?
- **Politique d'écriture** : quoi mémoriser, et à partir de quelles sources (pas de contenu externe brut)
- **Provenance** attachée à chaque souvenir, **cloisonnement** par utilisateur
- **Pas d'instructions** en mémoire, seulement des faits et des préférences
- **Analyse** des écritures (injection, données sensibles), **expiration** et **purge** possibles

Voir [[39-memoire-agents|mémoire des agents]].

---

Comment sécuriser les échanges entre agents ?
?
- **Une identité et des droits minimaux par agent** ; pas de transmission du jeton complet : **échange de jeton** avec des droits réduits pour chaque sous-agent
- **Authentification mutuelle** (mTLS, OAuth) et **Agent Cards signées** (A2A 1.0)
- **Sorties des autres agents traitées comme non fiables**
- **Coupe-circuits** pour arrêter une cascade

Voir [[36-orchestration-agents|orchestration]].

---

Quelles couches forment la défense en profondeur d'un agent ?
?
```text
1. Conception  : Rule of Two, design patterns, outils étroits
2. Identité    : droits de l'utilisateur, jetons courts et limités
3. Contrôle    : validation, moteur de politiques, provenance
4. Isolation   : sandbox, réseau sortant filtré, secrets hors de portée
5. Humain      : approbation des actions à risque
6. Filtres     : guardrails en entrée et en sortie
7. Exploitation: traces, détection, kill switch
8. Vérification: tests adversariaux en CI, red teaming
```
Les couches 6 à 8 sont détaillées dans [[105-devsecops-ia-agentique|DevSecOps]].

---

## Connexions
- [[102-menaces-agents|Menaces & incidents]] — ce contre quoi on se défend
- [[101-securite-llm-guardrails|Sécurité LLM & guardrails]] — lethal trifecta, guardrails
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — sécuriser les outils eux-mêmes
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — tests, détection et réponse
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — identité, politiques, HITL
- [[38-plateformes-agents|Plateformes d'agents]] — sandbox et gateway d'outils
- [[34-harness-plugins|Harness & plugins]] — permissions et sandbox du harness
- [[32-tool-calling|Tool calling]] — valider avant d'exécuter
- [[00-moc-ai-engineering|MOC AI Engineering]]
