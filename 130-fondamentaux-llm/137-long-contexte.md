# Long contexte — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #long-context #llm

Qu'est-ce que la fenêtre de contexte ?
?
Le **nombre maximal de tokens** (entrée + sortie) que le modèle traite en une requête. Elle va de quelques dizaines de milliers à **plus d'un million** de tokens selon les modèles. Une fenêtre annoncée n'est **pas** une garantie que le modèle **exploite** bien tout ce contenu.

---

Comment étend-on la fenêtre de contexte d'un modèle ?
?
Surtout en adaptant l'encodage de position **[[131-transformer-architecture|RoPE]]** : **position interpolation**, **NTK-aware scaling**, **YaRN** — on « étire » les angles de rotation pour couvrir plus de positions — puis un **entraînement additionnel sur des séquences longues**. Certains modèles combinent aussi attention **locale (fenêtre glissante)** et **globale**.

---

Qu'est-ce que le phénomène « lost in the middle » ?
?
Les modèles exploitent mieux l'information placée **au début et à la fin** du contexte que celle placée **au milieu**. Les modèles récents l'atténuent, mais la règle pratique reste : **mettre les consignes et les éléments clés aux extrémités** et limiter le bruit ([[35-context-engineering|context engineering]]).

---

Qu'est-ce que le test « needle in a haystack » et quelle est sa limite ?
?
Cacher une **phrase précise** dans un long texte et demander de la retrouver. La plupart des modèles récents le réussissent presque parfaitement — mais c'est une tâche de **simple repérage**. Des benchmarks plus exigeants (**RULER**, multi-aiguilles, raisonnement sur plusieurs passages, suivi de variables) montrent une **longueur effective** souvent bien inférieure à la fenêtre annoncée.

---

Pourquoi la qualité se dégrade-t-elle avant même d'atteindre la limite de la fenêtre ?
?
C'est le **context rot** : la **dégradation progressive** de la qualité quand le contexte grossit : attention diluée, distracteurs, instructions oubliées. Elle apparaît **bien avant** la limite de la fenêtre. D'où la compaction, les sous-agents et le chargement **au besoin** en [[35-context-engineering|context engineering]].

---

Long contexte ou RAG ?
?
- **Long contexte** : corpus **petit et stable** (un contrat, un dépôt de code), questions qui demandent une **vue d'ensemble**, prototype rapide. Avec le [[123-caching-agressif|prompt caching]], le coût peut rester raisonnable.
- **RAG** : corpus **grand** ou qui **change**, besoin de **citations**, de **contrôle d'accès** par document, de coût et de latence maîtrisés.

Souvent : **RAG pour sélectionner**, contexte large pour **raisonner** sur la sélection.

---

Quel est le coût d'un long contexte à l'inférence ?
?
- **Prefill** : calcul **quadratique** en longueur → **TTFT** élevé (plusieurs secondes pour des centaines de milliers de tokens).
- **KV cache** : mémoire **linéaire** en longueur → moins de requêtes simultanées par GPU.
- **Prix** : chaque appel re-facture tout le contexte, souvent avec un **tarif majoré** au-delà d'un seuil ([[121-couts-inference|coûts]], [[61-kv-cache-attention|KV cache]]).

---

Quelles techniques réduisent le coût du long contexte côté serving ?
?
**Prefix caching** (réutiliser le KV d'un préfixe commun), **chunked prefill**, **quantization du KV cache**, **offloading** du cache vers CPU ou SSD, attention à **fenêtre glissante** ou hybride, et **parallélisme de contexte** (découper la séquence entre GPU) — voir [[66-prefix-caching-radix-attention|prefix caching]].

---

Comment la limite de sortie diffère-t-elle de la limite d'entrée ?
?
La **sortie maximale** (max output tokens) est en général **bien plus petite** que la fenêtre (quelques milliers à quelques dizaines de milliers de tokens), et la génération est **séquentielle** donc lente. Produire un long document demande de **découper** la génération (plan puis sections).

---

Comment tester si un modèle gère son long contexte sur ma tâche ?
?
Construire une eval où l'on fait **varier la longueur du contexte** et la **position** de l'information utile, avec des **distracteurs réalistes** tirés de son corpus, et tracer la qualité en fonction de la longueur. On en déduit une **longueur de travail sûre** à respecter dans l'application ([[94-evals-methodologie|méthodologie d'évaluation]]).

---

## Mises en situation

Mise en situation : un chef de produit veut supprimer le RAG et « tout mettre dans le contexte », puisque le modèle accepte un million de tokens. Que réponds-tu ?
?
1. **Distinguer fenêtre annoncée et longueur effective** : les modèles se dégradent bien avant la limite, sauf sur le simple repérage d'information
2. **Coût** : chaque appel refacture tout le contexte, avec un prefill quadratique donc un TTFT élevé ([[121-couts-inference|coûts]])
3. **Contraintes fonctionnelles** : citations, contrôle d'accès par document, fraîcheur des données restent du ressort du RAG
4. **Approche mixte** : le RAG sélectionne, le contexte large sert à raisonner sur la sélection
5. **Mesurer** : faire varier la longueur et la position de l'information utile sur tes propres cas

**Piège** : valider l'idée avec un test « retrouve cette phrase », qui ne prouve pas la capacité de raisonner sur l'ensemble.

---

Mise en situation : ton assistant d'analyse de contrats devient lent et cher dès que les documents dépassent 200 pages. Quels leviers, côté application et côté serving ?
?
1. **Côté application** : ne pas tout charger, récupérer les sections utiles, résumer en amont, découper la génération en plan puis sections
2. **Prompt caching** : si le même contrat est analysé plusieurs fois, un préfixe stable évite de repayer le prefill ([[123-caching-agressif|caching]])
3. **Côté serving** : prefix caching, chunked prefill, quantization du KV cache ([[66-prefix-caching-radix-attention|prefix caching]])
4. **Limiter la sortie** : la limite de génération est bien plus basse que la fenêtre, et le decode est séquentiel
5. **Fixer une longueur de travail sûre**, déduite des mesures, et la respecter dans le produit

**Piège** : augmenter la fenêtre autorisée sans mesurer l'effet sur la qualité et sur la concurrence tenue par GPU.

---

## Connexions
- [[35-context-engineering|Context engineering]] — gérer le budget de contexte
- [[61-kv-cache-attention|KV cache & attention]] — le coût mémoire
- [[66-prefix-caching-radix-attention|Prefix caching]] — réutiliser les préfixes longs
- [[21-rag-fondamentaux|RAG]] — l'alternative au long contexte
- [[131-transformer-architecture|Architecture Transformer]] — RoPE et attention
- [[00-moc-ai-engineering|MOC AI Engineering]]
