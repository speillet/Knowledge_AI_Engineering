# Fondamentaux des agents — Flashcards
Tags: #flashcards #ai-engineering #agents #llm

Qu'est-ce qu'un agent LLM ?
?
Un **LLM doté d'outils et d'une boucle d'exécution** (percevoir → raisonner → agir) qui poursuit un **objectif** en décidant lui-même de ses étapes.

---

À ne pas confondre : workflow et agent ?
?
Un **workflow** suit des étapes prédéfinies par le développeur ; un **agent** décide dynamiquement de ses actions — distinction popularisée par Anthropic (« Building effective agents »).

---

Qu'est-ce que le pattern ReAct ?
?
Une boucle **Reasoning + Acting** : le modèle alterne raisonnement, appel d'outil et observation du résultat jusqu'à la réponse finale.
```text
Pensée      : il me faut le statut de la commande
Action      : statut_commande(commande_id="CMD-004212")
Observation : { "statut": "expédiée", "date": "2026-09-22" }
Pensée      : j'ai l'information, je peux répondre
Réponse     : votre commande est partie le 22 septembre
```
En pratique, avec le [[32-tool-calling|tool calling]] natif, ce cycle n'a plus besoin d'être écrit dans le prompt : il est porté par le **format des messages** et par la boucle du [[34-harness-plugins|harness]].

---

De quoi est composé un agent minimal ?
?
- Un **modèle** qui décide
- Des **[[32-tool-calling|outils]]** qui agissent
- Une **boucle** de contrôle : tant que le modèle demande un outil, on l'exécute et on lui renvoie le résultat
- Un **[[35-context-engineering|contexte]]** : instructions, historique, mémoire
- Un **critère d'arrêt** : réponse finale, budget d'étapes, ou demande d'aide

La boucle tient en vingt lignes de code. La difficulté est ailleurs : la qualité des outils, le tri du contexte et les conditions d'arrêt.

---

Quand ne faut-il PAS construire un agent ?
?
Quand la tâche est **prévisible** : un workflow fixe est plus fiable, moins cher et plus simple à déboguer. **L'agent se justifie quand le chemin est inconnu à l'avance.**

---

Qu'est-ce que le human-in-the-loop ?
?
Des **points de validation humaine** insérés dans la boucle de l'agent, là où une erreur coûterait cher. Trois formes :
- **Approbation avant action** : paiement, envoi d'e-mail, suppression. L'agent s'arrête et attend
- **Demande de précision** : l'agent pose une question plutôt que de deviner
- **Revue après coup** : un humain vérifie un échantillon des actions réversibles

Trop d'approbations produit de la **fatigue** et des validations à l'aveugle : on les réserve aux actions à risque ([[144-ux-ia-human-in-the-loop|UX du human-in-the-loop]]).

---

Quels sont les principaux risques d'un agent ?
?
- **Boucles infinies** : même action répétée sans progrès. Parade : budget d'étapes et détection de répétition
- **Dérive d'objectif** : l'agent poursuit un autre but, parfois après une injection. Parade : outils étroits, politiques hors du modèle ([[103-defenses-agents|défenses]])
- **Actions destructives** : suppression, envoi, paiement. Parade : permissions minimales et approbation humaine
- **Coût incontrôlé** : l'historique grossit à chaque tour. Parade : plafonds par tâche ([[121-couts-inference|coûts]])
- **Échec silencieux** : l'agent déclare avoir fini sans vérifier. Parade : vérification explicite du résultat

---

Quels ordres de grandeur pour le coût d'un agent ?
?
```text
chat simple                      1 ×   référence
agent avec outils               ~4 ×   (historique renvoyé à chaque tour)
système multi-agents           ~15 ×   (chaque agent a son contexte)
```
Ces repères, mesurés par Anthropic, expliquent pourquoi un agent se justifie par la **valeur de la tâche** et non par élégance technique. À compenser par le prompt caching, dont l'effet est massif sur ce profil de charge ([[123-caching-agressif|caching]], [[122-finops-llm|FinOps]]).

---

Comment un agent sait-il quand s'arrêter ?
?
Quand le modèle **répond sans appeler d'outil** (ou émet un signal de fin), ou quand le harnais atteint une **limite** (itérations, budget).

---

## Mises en situation

Mise en situation : le métier veut « un agent IA » pour traiter les demandes de congés, qui suivent toujours les mêmes règles. Que réponds-tu ?
?
1. **Qualifier la tâche** : le chemin est-il connu à l'avance ? Ici oui, donc un **workflow** est plus fiable, moins cher et plus simple à déboguer ([[41-automatisation-code-nocode|automatisation]])
2. **Placer le LLM là où il apporte de la valeur** : comprendre la demande en langage naturel et extraire les champs, le reste étant du code déterministe
3. **Garder une porte de sortie** : les cas hors règles partent vers un humain
4. **Mesurer** : taux de traitement automatique, erreurs, coût par demande
5. **Réserver l'agent** aux tâches dont les étapes varient vraiment d'un cas à l'autre

**Piège** : un agent autonome sur un processus réglementé, impossible à auditer et à reproduire.

---

Mise en situation : ton agent d'analyse tourne parfois 40 étapes, coûte cher et finit sans réponse utile. Quelles limites poses-tu ?
?
1. **Plafonds** : nombre maximal d'itérations, budget en tokens et durée par tâche ([[122-finops-llm|FinOps]])
2. **Conditions d'arrêt claires** : critères de succès explicites dans le prompt et, si possible, vérifiables par du code
3. **Détecter les boucles** : mêmes appels d'outils répétés, absence de progrès entre deux étapes
4. **Découper** : sous-tâches avec un contexte propre plutôt qu'une longue trajectoire qui sature le contexte ([[35-context-engineering|context engineering]])
5. **Échec propre** : rendre la main à l'humain avec l'état d'avancement plutôt que d'insister

**Piège** : relever la limite d'itérations quand l'agent échoue, au lieu de comprendre pourquoi il n'avance plus.

---

## Connexions
- [[32-tool-calling|Tool calling]] — les mains de l'agent
- [[34-harness-plugins|Harness]] — le cadre d'exécution
- [[35-context-engineering|Context engineering]] — la mémoire de travail
- [[36-orchestration-agents|Orchestration multi-agents]] — passage à l'échelle
- [[41-automatisation-code-nocode|Automatisation]] — workflow vs agent
- [[96-evals-rag-agents|Evals d'agents]] — trajectoire, état final, pass^k
- [[141-system-design-llm|System design LLM]] — workflow ou agent
- [[165-computer-use-agents-navigateur|Computer use & agents navigateur]] — quand l'outil est une interface graphique
- [[48-patterns-workflows-agentiques|Patterns de workflows]] — composer avant de rendre autonome
- [[00-moc-ai-engineering|MOC AI Engineering]]
