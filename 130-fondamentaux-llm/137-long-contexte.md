# Long contexte — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #long-context #llm
<!-- summary: extension de RoPE, lost in the middle, needle in a haystack et RULER, context rot, long contexte ou RAG, coût, techniques de serving, limite de sortie, test sur sa tâche. -->


Qu'est-ce que la fenêtre de contexte ? <!--anki:6d7324252c743d7a6c7d-->
?
Le **nombre maximal de tokens** (entrée + sortie) que le modèle traite en une requête. Elle va de quelques dizaines de milliers à **plus d'un million** de tokens selon les modèles. Une fenêtre annoncée n'est **pas** une garantie que le modèle **exploite** bien tout ce contenu.

Le budget comprend aussi **instructions, historique et schémas d'outils**, pas seulement le document fourni. Si l'entrée occupe presque toute la capacité, il peut manquer de place pour la sortie ou un résultat d'outil supplémentaire. Consulter les limites distinctes du modèle et du service, puis fixer une marge adaptée à la tâche.

---

Comment étend-on la fenêtre de contexte d'un modèle ? <!--anki:513e6d3c793a695b673c-->
?
Surtout en adaptant l'encodage de position **[[131-transformer-architecture|RoPE]]** : **position interpolation**, **NTK-aware scaling**, **YaRN** — on « étire » les angles de rotation pour couvrir plus de positions — puis un **entraînement additionnel sur des séquences longues**. Certains modèles combinent aussi attention **locale (fenêtre glissante)** et **globale**.

Changer l'échelle des positions ne suffit pas à démontrer une bonne utilisation des longues séquences. Évaluer récupération d'informations, raisonnement entre passages distants et qualité sur les contextes courts après extension. Une fenêtre glissante réduit certains coûts mais restreint les dépendances directes ; les capacités obtenues dépendent de l'architecture et de l'entraînement associés.

---

Qu'est-ce que le phénomène « lost in the middle » ? <!--anki:723c2f282b7629302f5a-->
?
Les modèles exploitent mieux l'information placée **au début et à la fin** du contexte que celle placée **au milieu**. Les modèles récents l'atténuent, mais la règle pratique reste : **mettre les consignes et les éléments clés aux extrémités** et limiter le bruit ([[35-context-engineering|context engineering]]).

Le phénomène dépend du modèle et de la tâche, notamment lorsqu'il faut retrouver une information parmi des distracteurs. Déplacer un passage tout en gardant la question identique permet de mesurer cette sensibilité. Ne pas supposer qu'une consigne répétée aux extrémités corrige tout : filtrer les passages inutiles et tester plusieurs positions reste nécessaire.

---

Qu'est-ce que le test « needle in a haystack » et quelle est sa limite ? <!--anki:6666417e472b57515f29-->
?
Cacher une **phrase précise** dans un long texte et demander de la retrouver. La plupart des modèles récents le réussissent presque parfaitement — mais c'est une tâche de **simple repérage**. Des benchmarks plus exigeants (**RULER**, multi-aiguilles, raisonnement sur plusieurs passages, suivi de variables) montrent une **longueur effective** souvent bien inférieure à la fenêtre annoncée.

---

Pourquoi la qualité se dégrade-t-elle avant même d'atteindre la limite de la fenêtre ? <!--anki:7a6f47267b447c417071-->
?
C'est le **context rot** : la **dégradation progressive** de la qualité quand le contexte grossit : attention diluée, distracteurs, instructions oubliées. Elle apparaît **bien avant** la limite de la fenêtre. D'où la compaction, les sous-agents et le chargement **au besoin** en [[35-context-engineering|context engineering]].

Une fenêtre plus grande augmente la quantité de contenu admissible, pas forcément la capacité à sélectionner les éléments pertinents. Pour diagnostiquer, garder les preuves utiles constantes et ajouter progressivement des distracteurs. Distinguer surcharge de contenu, contradiction entre sources et mauvaise position des preuves ; chaque cause peut appeler un ajustement différent du contexte.

---

Long contexte ou RAG ? <!--anki:4f3c556b3e682f4e3b40-->
?
- **Long contexte** : corpus **petit et stable** (un contrat, un dépôt de code), questions qui demandent une **vue d'ensemble**, prototype rapide. Avec le [[123-caching-agressif|prompt caching]], le coût peut rester raisonnable.
- **RAG** : corpus **grand** ou qui **change**, besoin de **citations**, de **contrôle d'accès** par document, de coût et de latence maîtrisés.

Souvent : **RAG pour sélectionner**, contexte large pour **raisonner** sur la sélection.

---

Quel est le coût d'un long contexte à l'inférence ? <!--anki:6f402e3c566b7770777e-->
?
- **Prefill** : calcul **quadratique** en longueur → **TTFT** élevé (plusieurs secondes pour des centaines de milliers de tokens).
- **KV cache** : mémoire **linéaire** en longueur → moins de requêtes simultanées par GPU.
- **Prix** : chaque appel re-facture tout le contexte, souvent avec un **tarif majoré** au-delà d'un seuil ([[121-couts-inference|coûts]], [[61-kv-cache-attention|KV cache]]).

---

Quelles techniques réduisent le coût du long contexte côté serving ? <!--anki:66435d6f36567a3b6255-->
?
**Prefix caching** (réutiliser le KV d'un préfixe commun), **chunked prefill**, **quantization du KV cache**, **offloading** du cache vers CPU ou SSD, attention à **fenêtre glissante** ou hybride, et **parallélisme de contexte** (découper la séquence entre GPU) — voir [[66-prefix-caching-radix-attention|prefix caching]].

Ces techniques n'agissent pas sur le même poste : le caching évite un calcul répété, le chunked prefill partage mieux le temps GPU, et la quantification réduit le volume du cache. L'offloading ajoute des transferts ; l'attention locale modifie ce que le modèle consulte. Vérifier compatibilité, qualité et latence avant de les combiner.

---

À ne pas confondre : limite d'entrée (fenêtre de contexte) et limite de sortie ? <!--anki:6b3d3026794e255e4b21-->
?
La **sortie maximale** (max output tokens) est en général **bien plus petite** que la fenêtre (quelques milliers à quelques dizaines de milliers de tokens), et la génération est **séquentielle** donc lente. Produire un long document demande de **découper** la génération (plan puis sections).

Vérifier si le service impose un **budget total partagé** et une borne de sortie séparée. Une entrée acceptée de 100 000 tokens n'autorise pas nécessairement une sortie de même taille. Lors d'une génération par sections, garder un plan et des références communes, puis contrôler cohérence et omissions ; le découpage peut introduire répétitions et contradictions.

---

Comment tester si un modèle gère son long contexte sur ma tâche ? <!--anki:6c59292359433b455432-->
?
Construire une eval où l'on fait **varier la longueur du contexte** et la **position** de l'information utile, avec des **distracteurs réalistes** tirés de son corpus, et tracer la qualité en fonction de la longueur. On en déduit une **longueur de travail sûre** à respecter dans l'application ([[94-evals-methodologie|méthodologie d'évaluation]]).

Maintenir la difficulté de la question et les preuves nécessaires comparables entre longueurs. Ajouter des cas où plusieurs passages doivent être combinés, car retrouver une phrase unique ne teste pas toute la compréhension. Rapporter erreurs, coût et latence par position et longueur ; la borne de travail retenue dépend aussi de la tolérance métier aux échecs.

---

## Mises en situation

Mise en situation : un chef de produit veut supprimer le RAG et « tout mettre dans le contexte », puisque le modèle accepte un million de tokens. Que réponds-tu ? <!--anki:432957427b36502e3f52-->
?
1. **Distinguer fenêtre annoncée et longueur effective** : les modèles se dégradent bien avant la limite, sauf sur le simple repérage d'information
2. **Coût** : chaque appel refacture tout le contexte, avec un prefill quadratique donc un TTFT élevé ([[121-couts-inference|coûts]])
3. **Contraintes fonctionnelles** : citations, contrôle d'accès par document, fraîcheur des données restent du ressort du RAG
4. **Approche mixte** : le RAG sélectionne, le contexte large sert à raisonner sur la sélection
5. **Mesurer** : faire varier la longueur et la position de l'information utile sur tes propres cas

**Piège** : valider l'idée avec un test « retrouve cette phrase », qui ne prouve pas la capacité de raisonner sur l'ensemble.

---

Mise en situation : ton assistant d'analyse de contrats devient lent et cher dès que les documents dépassent 200 pages. Quels leviers, côté application et côté serving ? <!--anki:4437756d4641515e533a-->
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
- [[13-prompts-production|Prompts en production]] — structure, versioning et portabilité des prompts
- [[36-orchestration-agents|Orchestration multi-agents]] — sous-agents, handoffs et A2A
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT, TPOT, débit et percentiles
- [[68-quantization|Quantization]] — réduire la précision pour gagner mémoire et vitesse
- [[00-moc-ai-engineering|MOC AI Engineering]]
