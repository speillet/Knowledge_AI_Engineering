# Agents de recherche (deep research) — Flashcards
Tags: #flashcards #ai-engineering #rag #agents #deep-research #llm
Vérifié le : 30 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: RAG ou agent de recherche, boucle de recherche, sous-agents parallèles, outils de recherche, citations fiables, risques (sources, injection, biais), évaluation (couverture, BrowseComp), calcul du coût d'un rapport, quand ne pas l'utiliser. -->


Qu'est-ce qu'un agent de recherche (deep research) ? <!--anki:315f783362537c352a-->
?
Un agent qui répond à une question complexe en **menant lui-même une recherche** : il planifie, lance des dizaines de requêtes (web ou documents internes), lit les sources, **creuse** les pistes prometteuses, puis rédige un **rapport cité**. Il dure de quelques minutes à une heure, contre quelques secondes pour un RAG.

Toutes les grandes offres grand public en proposent un depuis 2025.

---

À ne pas confondre : RAG classique et agent de recherche ? <!--anki:6d437d676a3c354d443e-->
?
- **RAG** : **une** recherche, top-k passages, une réponse. Rapide et bon marché, mais limité à ce que la première requête trouve ([[21-rag-fondamentaux|RAG]])
- **Agent de recherche** : **boucle** de requêtes qui dépendent de ce qui a déjà été lu, sur de nombreuses sources, avec synthèse. Couvre les questions **ouvertes ou à plusieurs sauts**, mais coûte 10 à 100 fois plus

Entre les deux, l'**agentic RAG** : quelques recherches décidées par le modèle ([[22-rag-avance|RAG avancé]]).

---

Comment se déroule la boucle d'un agent de recherche ? <!--anki:4c7b53673262534b5173-->
?
1. **Clarifier** la question, parfois en interrogeant l'utilisateur
2. **Planifier** : décomposer en sous-questions
3. **Chercher et lire** : requêtes, sélection des résultats, lecture des pages utiles
4. **Évaluer** : qu'est-ce qui manque, qu'est-ce qui se contredit ? Puis nouvelles requêtes
5. **Rédiger** le rapport, chaque affirmation reliée à sa source

L'arrêt se décide sur **couverture suffisante** ou **budget épuisé**.

---

Pourquoi les agents de recherche utilisent-ils souvent plusieurs agents ? <!--anki:4831403a517c48356826-->
?
Parce que la recherche se **parallélise** bien : un orchestrateur lance des **sous-agents** sur des sous-questions indépendantes, chacun avec son propre contexte, qui ne renvoient qu'un **résumé**. Anthropic rapporte un gain important de son système multi-agents sur un agent seul, au prix d'environ **15 fois plus de tokens** qu'un chat ([[36-orchestration-agents|orchestration]]).

À réserver aux questions **larges** : pour une question étroite, un seul agent suffit.

---

Quels types d'outils donner à un agent de recherche ? <!--anki:6a416525792b62536b65-->
?
- **API de recherche web** conçues pour les agents (résultats nettoyés, extraits pertinents), ou recherche web intégrée au fournisseur du modèle
- **Récupération de page** qui renvoie du texte propre, pas du HTML brut
- **Recherche interne** : index documentaire, SharePoint, tickets, via [[33-mcp|MCP]]
- Une **mémoire de travail** (notes, liste des sources lues) pour ne pas relire la même page

Des résultats **courts et denses** comptent plus que le nombre d'outils ([[49-agents-de-code|ACI]]).

---

Comment rendre les citations d'un rapport fiables ? <!--anki:77332e51657671396742-->
?
- Attacher **chaque affirmation** à un passage précis d'une source lue, pas seulement à une URL
- Faire vérifier, par un appel séparé, que le **passage soutient bien** l'affirmation
- Signaler les **sources contradictoires** au lieu d'en choisir une en silence
- Préférer les **sources primaires** (étude, texte officiel) aux reprises

Une citation vers une page qui ne dit pas ce qu'on lui prête est pire qu'aucune ([[143-hallucinations-grounding|citations]]).

---

Quels risques spécifiques pose un agent de recherche ? <!--anki:435a7b2d2f7670487140-->
?
- **Sources peu fiables ou générées par IA** citées comme autorités
- **Prompt injection** par les pages lues, qui peuvent orienter la synthèse ou tenter d'exfiltrer ([[102-menaces-agents|menaces]])
- **Biais de confirmation** : l'agent cherche ce qui confirme sa première hypothèse
- **Fausse exhaustivité** : un rapport long et cité donne une impression de couverture complète

D'où des sources autorisées ou priorisées, et un rapport qui dit **ce qui n'a pas été trouvé**.

---

Comment évaluer un agent de recherche ? <!--anki:50402c6137552b754438-->
?
- **Exactitude** sur des questions à réponse vérifiable, dont des questions **difficiles à trouver** (benchmarks comme BrowseComp)
- **Couverture** : part des points clés attendus présents dans le rapport, listés par un expert
- **Fidélité des citations** : chaque affirmation est-elle soutenue par sa source ?
- **Coût et durée** par rapport

Un **juge calibré** note couverture et citations ; l'exactitude se vérifie par référence ([[96-evals-rag-agents|evals d'agents]]).

---

Calcul : 5 sous-agents lisent 15 pages de 4 000 tokens chacun ; supposer ces tokens envoyés deux fois, plus 100 000 tokens d’entrée d’orchestration. À 3 €/M, quel coût d’entrée par rapport, hors outils et sorties ? <!--anki:7332246760345a2c3f25-->
?
Hypothèses : 5 sous-agents, 15 pages lues chacun, 4 000 tokens par page, plus l'orchestrateur et la rédaction.
```text
lecture : 5 × 15 × 4 000         = 300 000 tokens d'entrée
contexte re-envoyé entre les tours ≈ ×2      → ~600 000
orchestrateur + rédaction          ≈ 100 000
à 3 €/M en entrée                  ≈ 2 € par rapport, hors sortie
```
Raisonnable pour une note d'analyse, prohibitif pour une question de support. D'où le **routage** entre RAG et recherche approfondie ([[82-routing-llm|routing]]).

---

Quand ne pas utiliser d'agent de recherche ? <!--anki:777e6c2d5123333b7074-->
?
- **Question factuelle simple**, à laquelle un RAG ou une recherche unique répond
- **Latence attendue en secondes** : chat de support, assistant vocal
- **Corpus fermé et petit**, qui tient dans le contexte
- **Décision engageante** sans relecture humaine du rapport

Il sert les questions **ouvertes, larges et à forte valeur** : veille, due diligence, état de l'art.

---

## Mises en situation

Mise en situation : l'équipe juridique veut un agent qui prépare des notes de veille réglementaire à partir du web et de la base documentaire interne. Comment le conçois-tu ? <!--anki:6e2c4d595d2f65235548-->
?
1. **Sources** : textes officiels et sites institutionnels en priorité, base interne via un outil de recherche, liste de domaines de confiance
2. **Architecture** : plan validé par le juriste, sous-agents par sous-question, rédaction finale avec citations au passage près
3. **Vérification** : contrôle séparé que chaque passage soutient l'affirmation, contradictions signalées
4. **Sécurité** : contenu web traité comme non fiable, aucun outil d'écriture ni d'envoi ([[103-defenses-agents|défenses]])
5. **Évaluation** : 20 questions déjà traitées par l'équipe, notées sur couverture et fidélité des citations

**Piège** : présenter le rapport comme exhaustif, alors que l'agent n'a lu que ce que ses requêtes ont trouvé.

---

Mise en situation : ton agent de recherche produit de bons rapports, mais coûte 8 € et 25 minutes par question, et les utilisateurs l'emploient pour des questions simples. Que fais-tu ? <!--anki:45436375787a3d634c5f-->
?
1. **Mesurer** la répartition des questions : simples, moyennes, vraiment ouvertes
2. **Router** : RAG ou recherche unique pour les questions simples, agent seulement pour les autres ([[82-routing-llm|routing]])
3. **Budgéter** : nombre maximal de sous-agents, de pages et de tokens par question
4. **Réutiliser** : cache des pages déjà lues et des rapports récents sur le même sujet ([[123-caching-agressif|caching]])
5. **Afficher** l'estimation de durée avant de lancer une recherche approfondie

**Piège** : réduire le budget pour tout le monde, et dégrader les questions qui justifiaient l'agent.

---

## Sources

- [Anthropic — architecture du système de recherche multi-agents](https://www.anthropic.com/engineering/multi-agent-research-system)

## Connexions
- [[21-rag-fondamentaux|RAG — Fondamentaux]] — la recherche en un coup
- [[22-rag-avance|RAG — Avancé]] — agentic RAG et reranking
- [[36-orchestration-agents|Orchestration multi-agents]] — orchestrateur et sous-agents
- [[143-hallucinations-grounding|Hallucinations & grounding]] — citations fiables
- [[102-menaces-agents|Menaces sur les agents]] — injection par les pages lues
- [[96-evals-rag-agents|Évaluation des RAG & des agents]] — mesurer couverture et fidélité
- [[165-computer-use-agents-navigateur|Agents navigateur]] — quand la recherche demande de naviguer
- [[00-moc-ai-engineering|MOC AI Engineering]]
