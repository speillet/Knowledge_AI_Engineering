# Context engineering — Flashcards
Tags: #flashcards #ai-engineering #agents #context-engineering #llm

Qu'est-ce que le context engineering ?
?
L'art de **choisir, à chaque appel, l'ensemble minimal de tokens le plus utile** dans la fenêtre de contexte : instructions, outils, historique, mémoire, documents récupérés.

---

Quelle différence avec le prompt engineering ?
?
Le **[[11-prompt-engineering-avance|prompt engineering]]** optimise la **formulation** d'une instruction ; le **context engineering** gère **tout ce qui entre dans le contexte**, sur la durée d'une session ou d'un agent.

---

Pourquoi traiter la fenêtre de contexte comme un budget ?
?
Chaque token **coûte** (prix, latence, VRAM du [[61-kv-cache-attention|KV cache]]) et **dilue l'attention** : plus le contexte grossit, moins le modèle exploite bien chaque information.

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

## Connexions
- [[11-prompt-engineering-avance|Prompt engineering]] — le prompt dans son budget global
- [[22-rag-avance|RAG avancé]] — placement des chunks
- [[31-agents-fondamentaux|Agents]] — la mémoire de travail de l'agent
- [[61-kv-cache-attention|KV cache]] — le coût mémoire du contexte
- [[36-orchestration-agents|Orchestration multi-agents]] — isoler les contextes
- [[34-harness-plugins|Harness]] — qui assemble le contexte
- [[00-moc-ai-engineering|MOC AI Engineering]]
