# Context engineering — Flashcards
Tags: #flashcards #ai-engineering #agents #context-engineering #llm

Qu'est-ce que le context engineering ?
?
L'art de **choisir, à chaque appel, l'ensemble minimal de tokens le plus utile** dans la fenêtre de contexte : instructions, outils, historique, mémoire, documents récupérés.

---

À ne pas confondre : context engineering et prompt engineering ?
?
Le **[[11-prompt-engineering-avance|prompt engineering]]** optimise la **formulation** d'une instruction ; le **context engineering** gère **tout ce qui entre dans le contexte**, sur la durée d'une session ou d'un agent.

---

Pourquoi traiter la fenêtre de contexte comme un budget ?
?
Chaque token **coûte** (prix, latence, VRAM du [[61-kv-cache-attention|KV cache]]) et **dilue l'attention** : plus le contexte grossit, moins le modèle exploite bien chaque information.
```text
Budget d'un tour d'agent (exemple) :
  system prompt              600 tokens   stable → mis en cache
  définitions de 12 outils  2 400 tokens  stable → mis en cache
  mémoire et préférences      300 tokens
  documents récupérés       3 000 tokens  variable
  historique (8 tours)      4 500 tokens  croît sans cesse ← à compacter
  question                    120 tokens
                           ──────────────
                          ~10 900 tokens par appel, dont 70 % réutilisables
```
Le poste qui grossit tout seul est l'**historique** : c'est lui qu'on compacte en premier.

---

Qu'est-ce que le context rot ?
?
La **dégradation des performances quand le contexte s'allonge** : informations anciennes contradictoires, bruit accumulé, effet [[22-rag-avance|« lost in the middle »]]. Une grande fenêtre n'est pas un contexte bien utilisé.

---

Quelles sont les composantes du contexte d'un agent ?
?
- **Instructions** (system prompt)
- **Définitions d'outils**
- **Historique** de la conversation et des résultats d'outils
- **Mémoire** (faits persistés)
- **Connaissances récupérées** ([[21-rag-fondamentaux|RAG]])

---

Qu'est-ce que la compaction ?
?
**Résumer l'historique** quand on approche de la limite, pour repartir avec un contexte plus court qui garde décisions, état et tâches en cours. Variante légère : **effacer les vieux résultats d'outils**.

Deux effets de bord à connaître : la compaction **casse le cache de préfixe** (tout ce qui suit change), et elle **perd des détails** — d'où l'intérêt d'écrire l'essentiel dans un fichier ou une mémoire **avant** de compacter ([[39-memoire-agents|mémoire]]).

---

À ne pas confondre : compaction, troncature et mémoire ?
?
- **Troncature** : on **coupe** les messages les plus anciens. Gratuit, mais on perd tout ce qui est coupé, y compris les décisions prises
- **Compaction** : on **résume** l'historique. Coûte un appel LLM, conserve l'essentiel, mais perd les détails et invalide le cache
- **Mémoire** : on **écrit hors du contexte** les faits durables, et on les relit à la demande. Seule solution qui survit à la session

Les trois se combinent : mémoire pour ce qui doit durer, compaction pour tenir la session, troncature en dernier recours.

---

Mémoire court terme vs long terme ?
?
- **Court terme** : le contexte de la session en cours
- **Long terme** : des faits **écrits hors du contexte** (fichiers, base) et relus à la demande — ex. un fichier de notes que l'agent met à jour

---

Comment les sous-agents aident-ils à gérer le contexte ?
?
Un [[36-orchestration-agents|sous-agent]] explore dans **son propre contexte** et ne renvoie qu'un **résumé condensé** : le contexte de l'agent principal reste propre.

---

Pourquoi garder un préfixe de prompt stable ?
?
Pour profiter du **prompt caching** : le fournisseur réutilise le calcul (KV cache) d'un **préfixe identique**. On met le contenu stable (instructions, outils) **au début** et le contenu variable **à la fin**.

---

Qu'est-ce que le just-in-time context ?
?
Ne pas tout charger d'avance : donner à l'agent des **références légères** (chemins de fichiers, requêtes, outils de recherche) et le laisser **récupérer l'information au moment où il en a besoin**.

---

## Mises en situation

Mise en situation : ton agent de support donne de bonnes réponses au début des conversations, puis se dégrade et se contredit au bout d'une heure. Que fais-tu ?
?
1. **Reconnaître le context rot** : le contexte a gonflé, les informations anciennes et contradictoires s'accumulent
2. **Compacter** : résumer l'historique en gardant décisions, état et tâches en cours ; supprimer les vieux résultats d'outils
3. **Sortir les faits durables** vers une mémoire relue à la demande ([[39-memoire-agents|mémoire]])
4. **Just-in-time** : donner des références et laisser l'agent récupérer ce dont il a besoin, plutôt que tout précharger
5. **Mesurer** : longueur de contexte, qualité et coût par tour au fil de la conversation ([[93-monitoring-inference|monitoring]])

**Piège** : passer à un modèle à très grande fenêtre sans rien changer. Le problème est la **qualité** du contexte, pas sa taille.

---

Mise en situation : ton assistant coûte deux fois plus cher que prévu, alors que le system prompt et les définitions d'outils sont identiques à chaque appel. Quelle piste ?
?
1. **Vérifier le prompt caching** : le préfixe est-il réellement stable, ou y insères-tu la date, l'ID de session ou des outils réordonnés ?
2. **Réorganiser** : contenu stable (instructions, outils) au début, contenu variable à la fin ([[123-caching-agressif|caching]])
3. **Mesurer** le taux de tokens lus en cache dans les traces, avant et après
4. **Réduire** ce qui est envoyé à chaque tour : outils inutiles, documents récupérés trop nombreux
5. **Surveiller** le coût par conversation, pas seulement par appel ([[122-finops-llm|FinOps]])

**Piège** : ajouter l'historique complet en tête de prompt, ce qui invalide le cache à chaque tour.

---

Mise en situation : ton agent doit analyser 300 pages de documentation technique pour répondre à une question précise. Comment organises-tu son contexte ?
?
1. **Ne pas tout charger** : 300 pages saturent le contexte, coûtent cher et diluent l'attention
2. **Recherche d'abord** : RAG ou outil de recherche pour ne récupérer que les passages utiles ([[21-rag-fondamentaux|RAG]])
3. **Sous-agents** : si plusieurs sections doivent être explorées, chacun travaille dans son contexte et ne remonte qu'un résumé ([[36-orchestration-agents|sous-agents]])
4. **Références plutôt que contenu** : donner la table des matières et des outils de lecture ciblée
5. **Citer** les passages utilisés, pour vérifier la réponse

**Piège** : découper mécaniquement en 10 appels sans mémoire entre eux, et perdre le fil du raisonnement.

---

## Connexions
- [[11-prompt-engineering-avance|Prompt engineering]] — le prompt dans son budget global
- [[22-rag-avance|RAG avancé]] — placement des chunks
- [[31-agents-fondamentaux|Agents]] — la mémoire de travail de l'agent
- [[61-kv-cache-attention|KV cache]] — le coût mémoire du contexte
- [[36-orchestration-agents|Orchestration multi-agents]] — isoler les contextes
- [[34-harness-plugins|Harness]] — qui assemble le contexte
- [[39-memoire-agents|Mémoire des agents]] — la mémoire long terme en détail
- [[123-caching-agressif|Caching agressif]] — concevoir le contexte pour le cache
- [[137-long-contexte|Long contexte]] — lost in the middle, longueur effective
- [[121-couts-inference|Coûts d'inférence]] — structure du coût et unit economics
- [[13-prompts-production|Prompts en production]] — structure, versioning et portabilité des prompts
- [[132-tokenisation|Tokenisation]] — ce qu'est un token et ce qu'il coûte
- [[43-langchain-agents|LangChain — Agents]] — agents et middleware LangChain
- [[45-langgraph-production|LangGraph — Production]] — persistance, reprise et supervision humaine
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — gouvernance]] — identité, politiques, audit et coûts d'une flotte d'agents
- [[00-moc-ai-engineering|MOC AI Engineering]]
