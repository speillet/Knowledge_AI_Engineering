# Optimisations d'inférence — Flashcards
Tags: #flashcards #ai-engineering #inference #optimisation #llm
<!-- summary: prefill et decode, continuous batching, quantization (AWQ, GPTQ, FP8), FlashAttention, parallélisme tensor et pipeline, chunked prefill, désagrégation prefill/decode. -->


Quelles sont les deux phases de l'inférence d'un LLM ? <!--anki:482678244d584c28753b-->
?
- **Prefill** : traitement de **tout le prompt en parallèle** → produit le premier token et remplit le [[61-kv-cache-attention|KV cache]]
- **Decode** : génération **token par token**, chacun dépendant du précédent

Le prefill prépare les représentations de tous les tokens d'entrée ; le decode ajoute les nouvelles positions une à une. Un long document avec une réponse courte charge surtout le prefill ; une rédaction longue sollicite beaucoup le decode. Cette distinction aide à choisir l'optimisation et la métrique pertinentes.

---

Pourquoi prefill et decode ont-ils des goulots différents ? <!--anki:423164672b2b78664256-->
?
Le **prefill** expose beaucoup d'opérations matricielles parallèles et devient souvent limité par le calcul pour des prompts assez longs. Le **decode à petit batch** effectue peu de calcul par poids chargé et est souvent limité par la bande passante mémoire.

Ce sont des régimes typiques, pas des propriétés absolues : batch élevé, long contexte, architecture MoE ou communication entre GPU peuvent déplacer le goulot. Profiler le workload avant de choisir quantization, batching ou parallélisme.

---

À ne pas confondre : les leviers qui agissent sur le TTFT et ceux qui agissent sur le TPOT ? <!--anki:477c572b3f2d422a736d-->
?
```text
TTFT (prefill)          prefix caching, chunked prefill, contexte plus court,
                        désagrégation, plus de calcul
TPOT (decode)           quantization, speculative decoding, GQA, moins de
                        bande passante mémoire consommée
Débit total             continuous batching, batch plus gros, parallélisme
```
Un même changement peut **améliorer l'un et dégrader l'autre** : un gros batch peut augmenter le débit et allonger le TPOT ([[64-metriques-slo-inference|SLO]]).

Le TTFT inclut aussi attente en file et transport ; accélérer uniquement le prefill ne résout pas une saturation du service. Le chunked prefill protège surtout les requêtes déjà en decode et peut retarder la fin d'un nouveau prefill. Comparer les percentiles à charge identique pour éviter de confondre meilleur débit et meilleure expérience.

---

Qu'est-ce que le continuous batching ? <!--anki:6f76727c477c5a746c4d-->
?
Le **continuous batching** ordonnance à la granularité d'une itération : une séquence terminée libère sa place, et de nouvelles séquences peuvent rejoindre les suivantes sans attendre la fin de tout un lot.

Cette approche réduit les places inutilisées lorsque les longueurs varient. Elle ne garantit pas un GPU plein : demande insuffisante, limite KV, CPU ou communications peuvent encore restreindre le débit. Comparer au batch statique sur un même workload, avec les mêmes SLO. L'écart entre un script et un serveur dépend aussi des kernels, du cache et de la gestion mémoire ; aucun facteur dix n'est universel.

---

Qu'est-ce que la quantization ? <!--anki:712b5a5a4e2d6f442a35-->
?
La **quantization** représente les poids et parfois les activations ou le KV cache avec moins de bits : FP8, INT8 ou INT4, par exemple. Elle réduit l'empreinte mémoire et peut diminuer les transferts, ce qui accélère certains workloads.

Le gain dépend des kernels et du matériel ; déquantifier peut coûter du temps. La perte de qualité n'est pas toujours légère, notamment sur les valeurs extrêmes et certaines tâches. Mesurer qualité, mémoire et latence sur le modèle et la charge visés ([[68-quantization|quantization]]).

---

Quelles méthodes de quantization courantes ? <!--anki:796f767d2a297674625a-->
?
Distinguer **ce qui est quantifié** et **la méthode** : AWQ et GPTQ concernent notamment la quantification des poids, souvent en 4 bits ; W8A8 décrit des poids et activations sur 8 bits. FP8 désigne une famille de formats numériques dont le support dépend du GPU et des kernels.

**GGUF est un format de fichier**, qui peut contenir différents types de quantification pour des moteurs comme llama.cpp. Comparer des configurations complètes, pas seulement ces noms : précision, calibration, kernels et workload déterminent qualité et vitesse.

---

Qu'est-ce que FlashAttention ? <!--anki:4b232642746c452f422f-->
?
Une implémentation de l'attention **consciente de la hiérarchie mémoire du GPU** (calcul par tuiles en SRAM) : **résultat exact**, beaucoup moins d'accès à la HBM, donc plus rapide et moins gourmande en mémoire.

L'algorithme évite de matérialiser toute la matrice d'attention en mémoire externe. « Exact » signifie ici qu'il calcule la même opération, à l'arrondi numérique près, contrairement à une approximation de l'attention. Pour une attention dense, le nombre d'opérations reste quadratique avec la longueur au prefill ; les gains concernent surtout les accès mémoire et l'exécution.

---

Tensor parallelism ou pipeline parallelism ? <!--anki:514f686c4c5338235550-->
?
- **Tensor parallelism** : chaque couche est **découpée entre plusieurs GPU** (demande un interconnect rapide type **NVLink**)
- **Pipeline parallelism** : les **couches sont réparties** par étages sur plusieurs GPU ou nœuds

Le tensor parallelism échange des résultats intermédiaires fréquemment et souffre d'un réseau lent. Le pipeline parallelism transmet des activations entre étages et peut laisser des GPU inactifs si le pipeline est mal rempli. Choisir selon la mémoire nécessaire, les interconnexions et la charge ; ajouter des GPU n'accélère pas automatiquement une requête isolée.

---

Qu'est-ce que le chunked prefill ? <!--anki:674f44515326767c7e37-->
?
Découper un long prefill **en morceaux mélangés aux decodes** en cours : un gros prompt n'**interrompt plus** la génération des autres requêtes (latence inter-token plus stable).

Le scheduler attribue un budget de tokens au prefill puis intercale les autres travaux. Cela limite les longues pauses de streaming, sans faire disparaître le coût total du prompt. Des morceaux trop petits ajoutent des frais d'ordonnancement ; trop gros peuvent encore pénaliser les decodes. Mesurer TTFT et latence inter-token ensemble.

---

Qu'est-ce que la désagrégation prefill/decode ? <!--anki:51242a2437253078482b-->
?
Exécuter prefill et decode sur des **pools de GPU séparés**, avec transfert du KV cache entre eux : chaque pool est dimensionné pour son goulot et on optimise **TTFT et TPOT** indépendamment.

Cette séparation réduit certaines interférences entre gros prompts et générations en cours. Son coût est le transfert du cache et la coordination des pools, qui peuvent annuler le gain si le réseau est insuffisant. Évaluer la taille des K/V, le taux d'arrivée et les déséquilibres de charge avant de complexifier le déploiement.

---

## Mises en situation

Mise en situation : ton service d'inférence tient le SLO de latence à faible charge, mais aux heures de pointe le TTFT explose alors que le débit stagne. Quels leviers actionnes-tu ? <!--anki:6932733f3f45586b4746-->
?
1. **Décomposer le TTFT** : attente, traitement du prompt et transport ; corréler avec longueur des entrées.
2. **Distinguer la saturation** : préemptions et KV plein orientent vers la mémoire ; une file seule ne suffit pas.
3. **Réduire le travail ciblé** : préfixes stables, contexte pertinent, quantification validée sur le matériel.
4. **Régler le scheduler** : batch et chunked prefill, en surveillant aussi ITL et équité.
5. **Adapter la capacité** si nécessaire, avec admission bornée, réplicas ou désagrégation évaluée.

**Piège** : activer plusieurs leviers simultanément puis attribuer le gain au mauvais mécanisme.

---

Mise en situation : on te propose de passer de 2 GPU à 4 GPU en tensor parallelism pour accélérer un modèle 70B. Que vérifies-tu avant ? <!--anki:63652b765a21517a6169-->
?
1. **Mesurer la topologie** : bande passante et latence des collectives, liens intra-nœud et réseau.
2. **Définir l'objectif** : modèle qui doit tenir en mémoire, latence individuelle ou débit utile.
3. **Comparer à budget identique** : une instance TP4 contre deux instances TP2, si toutes tiennent en mémoire.
4. **Examiner chaque GPU** : poids, KV réparti ou répliqué, activations et déséquilibre.
5. **Tester sous charge** : goodput, délais, erreurs, qualité et coût.

**Piège** : supposer que le tensor parallelism réduit forcément la latence, ou que NVLink suffit à garantir le gain.

---

## Sources

- [Orca — continuous batching](https://www.usenix.org/conference/osdi22/presentation/yu)
- [vLLM — optimisation et compromis](https://docs.vllm.ai/en/latest/configuration/optimization/)

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — la mémoire que ces techniques gèrent
- [[64-metriques-slo-inference|Métriques & SLO]] — ce qu'on optimise (TTFT, TPOT, débit)
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — où ces optimisations sont implémentées
- [[51-fine-tuning-adaptation|Fine-tuning]] — quantization et QLoRA
- [[12-kubernetes-gpu-inference|Kubernetes GPU]] — multi-GPU en cluster
- [[63-guided-generation|Guided generation]] — contraindre la sortie
- [[65-probabilites-sampling|Probabilités & sampling]] — speculative decoding : même distribution de sortie
- [[114-reproductibilite-variance|Reproductibilité & variance]] — le batching comme source de non-déterminisme
- [[67-speculative-decoding|Speculative decoding]] — la technique en détail
- [[68-quantization|Quantization]] — formats et méthodes en détail
- [[136-mixture-of-experts|Mixture of Experts]] — expert parallelism
- [[54-entrainement-distribue|Entraînement distribué]] — les mêmes parallélismes à l'entraînement
- [[69-roofline-prefill-decode|Roofline & désagrégation]] — pourquoi chaque phase a son goulot
- [[121-couts-inference|Coûts d'inférence]] — structure du coût et unit economics
- [[148-pipelines-batch-llm|Pipelines batch]] — traiter des millions d'items à moindre coût
- [[60-012-demarche-optimisation-inference|Démarche d’optimisation]] — prioriser et vérifier les gains sous contraintes de service
- [[66-prefix-caching-radix-attention|Prefix caching]] — réduire le prefill selon la réutilisation réelle
- [[00-moc-ai-engineering|MOC AI Engineering]]
