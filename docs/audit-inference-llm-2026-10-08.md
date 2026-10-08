# Audit du parcours d’inférence LLM — 8 octobre 2026

Le parcours disposait déjà des mécanismes centraux : prefill/decode, KV cache, batching, quantification, spéculation, routage, SLO et coûts. L’audit a surtout révélé un manque de profondeur sur **la validité des mesures, les expériences de charge et le passage d’un diagnostic à une décision de capacité**. Certaines formulations promettaient également des gains trop systématiques.

Cette révision ajoute **63 cartes**, dont **12 cartes de calcul**, dans trois nouvelles fiches et cinq fiches existantes. Elle corrige ou précise **47 anciennes cartes**, sans supprimer leurs identifiants Anki. Les trois nouvelles fiches comportent chacune 16 cartes, dont trois mises en situation. Les cinq fiches ML ajoutées précédemment, soit 70 cartes, sont conservées dans un commit distinct.

Le résultat vise à maximiser les **tâches utiles réalisées sous contraintes de qualité, de délai et de coût**. Le débit brut de tokens, la VRAM pleine ou un GPU actif ne suffisent pas à choisir une configuration.

## Couverture vérifiée

« Existant » signifie que la notion disposait déjà d’une fiche dédiée ; « approfondi » signifie que ses limites, métriques ou critères de décision ont été complétés. Cette matrice couvre le socle d’ingénierie de l’inférence, pas chaque variante de kernel, de matériel ou d’architecture publiée.

| Problématique | État après audit et profondeur attendue | Fiches de référence |
|---|---|---|
| TTFT, TPOT, ITL et durée complète | Approfondi : formules, granularité des chunks, pondérations et sorties de moins de deux tokens | [64 — Métriques](../60-inference-llm/64-metriques-slo-inference.md), [93 — Monitoring](../90-observabilite-evals/93-monitoring-inference.md) |
| Raisonnement et expérience visible | Ajout : premier événement, premier contenu utile, tokens visibles ou internes | [64](../60-inference-llm/64-metriques-slo-inference.md), [138 — Raisonnement](../130-fondamentaux-llm/138-modeles-raisonnement.md) |
| Débits et critères de réussite | Approfondi : offert, admis, terminé, utile ; intersection des critères par requête | [64](../60-inference-llm/64-metriques-slo-inference.md) |
| Percentiles et histogrammes | Ajout : agrégation avant quantile, buckets aux seuils SLO, effectifs, segmentation et cardinalité | [93](../90-observabilite-evals/93-monitoring-inference.md) |
| Erreurs et observations manquantes | Ajout : timeouts, rejets, annulations et demandes inachevées ; éviter les métriques sur les seules réussites | [64](../60-inference-llm/64-metriques-slo-inference.md), [60-010 — Benchmarks](../60-inference-llm/60-010-benchmarks-charge-inference.md) |
| SLO et budgets d’erreur | Corrigé : burn rate d’une fraction d’événements non conformes ; pas d’un percentile | [64](../60-inference-llm/64-metriques-slo-inference.md), [116 — SRE](../110-mlops-cicd/116-sre-incidents-capacite-ia.md) |
| Mesure client, gateway et moteur | Ajout : jalons, horloges, buffering, tâches, appels et tentatives | [93](../90-observabilite-evals/93-monitoring-inference.md), [84 — Streaming](../80-api-layer-routing/84-streaming-integration-applicative.md) |
| Protocole de charge | Nouvelle fiche : boucles ouverte/fermée, omission coordonnée, générateur saturé et charge réellement émise | [60-010](../60-inference-llm/60-010-benchmarks-charge-inference.md) |
| Réalisme et reproductibilité | Ajout : distribution conjointe entrée/sortie, préfixes, rafales, manifeste, échauffement et vidange | [60-010](../60-inference-llm/60-010-benchmarks-charge-inference.md) |
| Incertitude des résultats | Ajout : répétitions, ordre des essais, dépendances temporelles et stabilité du p99 | [60-010](../60-inference-llm/60-010-benchmarks-charge-inference.md), [99 — Statistiques](../90-observabilite-evals/99-statistiques-decisions-experimentales.md) |
| Capacité et loi de Little | Corrigé : requêtes en vol ≠ séquences GPU ; moyennes ≠ dimensionnement des pointes | [64](../60-inference-llm/64-metriques-slo-inference.md), [60-011 — Capacité](../60-inference-llm/60-011-capacite-ordonnancement-inference.md) |
| Mémoire KV | Approfondi : octets/token, Gio/Kio, croissance, partage, marge par GPU, GQA/MQA et réplication | [61 — KV](../60-inference-llm/61-kv-cache-attention.md), [60-011](../60-inference-llm/60-011-capacite-ordonnancement-inference.md) |
| Architectures non classiques | Limites explicites : ne pas transposer la formule KV classique à MLA, fenêtres glissantes et états récurrents | [60-011](../60-inference-llm/60-011-capacite-ordonnancement-inference.md) |
| Ordonnancement | Nouvelle fiche : séquences, tokens par itération, contexte maximal, préemption et travail recalculé | [60-011](../60-inference-llm/60-011-capacite-ordonnancement-inference.md) |
| Admission, priorités et équité | Ajout : file bornée par délai et travail, vieillissement, clients et longs prompts | [60-011](../60-inference-llm/60-011-capacite-ordonnancement-inference.md) |
| Réplication et multi-GPU | Approfondi : DP/TP/PP, domaine de panne, communications, MoE et placement des experts | [60-011](../60-inference-llm/60-011-capacite-ordonnancement-inference.md), [136 — MoE](../130-fondamentaux-llm/136-mixture-of-experts.md) |
| Autoscaling et réserve | Approfondi : readiness réelle, cache froid, drainage, oscillation, panne et croissance de file | [64](../60-inference-llm/64-metriques-slo-inference.md), [60-011](../60-inference-llm/60-011-capacite-ordonnancement-inference.md) |
| Prefix caching | Approfondi : hit par requête/token, gain E2E réel, affinité contre surcharge ; isolation déjà traitée | [66 — Prefix caching](../60-inference-llm/66-prefix-caching-radix-attention.md) |
| Batching et interférence entre phases | Corrigé : gains conditionnels ; compromis batch, chunked prefill, TTFT et pauses du streaming | [62 — Optimisations](../60-inference-llm/62-optimisations-inference.md), [69 — Roofline](../60-inference-llm/69-roofline-prefill-decode.md) |
| Roofline et désagrégation | Approfondi : plafond théorique ≠ débit mesuré, hypothèses de prefill, transfert KV et recouvrement | [69](../60-inference-llm/69-roofline-prefill-decode.md) |
| Speculative decoding | Corrigé : distribution préservée sous conditions, coût de vérification, acceptation ≠ speedup | [67 — Spéculation](../60-inference-llm/67-speculative-decoding.md) |
| Quantification | Corrigé : poids/activations/KV indépendants, kernels et qualité par segment ; aucun format universellement sans perte | [68 — Quantification](../60-inference-llm/68-quantization.md) |
| Profilage et chemin critique | Nouvelle fiche : CPU/GPU, tokenization, médias, réseau, NUMA, chronologie et coût de l’instrumentation | [60-012 — Démarche](../60-inference-llm/60-012-demarche-optimisation-inference.md) |
| Graphes, compilation et kernels | Ajout : mécanismes distincts, formes, mémoire, démarrage et validation numérique | [60-012](../60-inference-llm/60-012-demarche-optimisation-inference.md) |
| Priorisation des optimisations | Ajout : Amdahl, hypothèse réfutable, interactions et frontière de compromis qualité/coût/délai | [60-012](../60-inference-llm/60-012-demarche-optimisation-inference.md) |
| API et amplification de charge | Ajout : RPM, tokens d’entrée/sortie, bursts, retries, hedging et annulation | [60-012](../60-inference-llm/60-012-demarche-optimisation-inference.md) |
| Réduction du travail applicatif | Existant et relié : contexte, modèle, cascade, cache de réponse, raisonnement et branches d’agents | [60-012](../60-inference-llm/60-012-demarche-optimisation-inference.md), [82 — Routage](../80-api-layer-routing/82-routing-llm.md) |
| Qualité et contrôle des sorties | Existant et intégré aux critères : evals, JSON, troncatures, sampling, canary et rollback | [63 — Sorties structurées](../60-inference-llm/63-guided-generation.md), [65 — Sampling](../60-inference-llm/65-probabilites-sampling.md), [112 — CI/CD](../110-mlops-cicd/112-cicd-modeles.md) |
| Coût, énergie et batch | Approfondi : coût par réponse conforme, réservation, calcul API, J/tâche ; batch asynchrone déjà traité | [121 — Coûts](../120-couts-finops/121-couts-inference.md), [148 — Batch](../140-system-design-produit/148-pipelines-batch-llm.md) |
| Multimodal | Ajout : résolution/durée, encodeur, unités processeur et facturation, mémoire de pointe | [60-012](../60-inference-llm/60-012-demarche-optimisation-inference.md) |

## Démarche de travail proposée

1. **Définir le résultat utile** : tâche, qualité minimale, proportions de conformité et budget de coût ; séparer interaction en streaming et traitement différé.
2. **Mesurer au bon périmètre** : client et moteur, erreurs incluses, volumes réconciliés, histogrammes et segments pertinents.
3. **Établir la capacité** : courbes de charge, file stable ou croissante, caches froids/chauds, rafales, annulations et perte de capacité.
4. **Choisir une hypothèse ciblée** : mémoire KV, calcul, bande passante, communications, CPU, quota ou travail applicatif superflu.
5. **Comparer et déployer** : essais répétés, qualité par segment, goodput et coût au trafic attendu, puis canary avec critères de rollback.

## Ateliers pour démontrer la maîtrise

### Mesure et SLO

Produire un petit jeu d’événements comprenant succès, refus, timeouts, réponses courtes, chunks contenant plusieurs tokens et reprises. Calculer séparément TPOT par requête, intervalles entre chunks, goodput et taux de conformité conjointe. Construire deux réplicas dont les volumes diffèrent pour montrer pourquoi leurs p95 ne se moyennent pas.

**Livrable** : définition des populations, unités et dénominateurs, avec vérification manuelle de quelques lignes. Les erreurs avant premier token restent dans les événements éligibles du contrat, même si elles n’apparaissent pas dans l’histogramme TTFT.

### Capacité sous charge

Sur un serveur de test disponible, comparer plusieurs charges avec mêmes données, version, tokenizer et paramètres de génération. Conserver arrivées prévues/réelles, résultats, longueurs, latences et état des caches. Séparer échauffement technique et réutilisation du contenu. Inclure la vidange, les erreurs et les requêtes abandonnées.

**Livrable** : courbes de goodput, latences, refus et croissance de file ; manifeste de chaque run et capacité retenue avec marge justifiée. Ajouter un pic et une perte de réplica. Une simulation de file peut préparer l’exercice mais ne démontre pas une capacité GPU réelle.

### Optimisation ciblée

Identifier le goulot dominant puis comparer une baseline, un levier et une combinaison justifiée : scheduler, préfixes, kernels, précision ou spéculation. Comparer sur tâches identiques et sur les longueurs réellement produites, en tenant compte des sorties interrompues.

**Livrable** : hypothèse, mesure qui pourrait la réfuter, contrôle qualité par segment, profil représentatif et résultats sans profilage lourd. Expliquer un cas où l’optimisation devient défavorable. La qualité est mesurée sur un jeu distinct de la calibration éventuelle.

### Coût et quotas

Construire une feuille de calcul ou un script avec volume horaire, taux de succès, reprises, quotas, réplicas de secours et prix fictifs clairement identifiés. Comparer un service plus cher à l’heure mais meilleur en goodput à un service moins cher et moins productif.

**Livrable** : coût par tâche conforme et couverture de la demande, à faible charge et à la charge cible. Si l’énergie est mesurée, préciser GPU/serveur/installation et intégrer les joules sur la même fenêtre. Ne pas convertir une activité GPU en coût ou en carbone par une règle de proportionnalité non validée.

## Références et limites

Les références primaires sont conservées dans les fiches : documentation vLLM pour les métriques, budgets et kernels ; NVIDIA pour DCGM et GenAI-Perf ; Prometheus pour histogrammes et instrumentation ; Google SRE pour les budgets d’erreur ; travaux Orca, PagedAttention, GQA, DistServe et speculative decoding pour les mécanismes. Les exemples de quotas sont fictifs ; les règles concrètes dépendent de l’API. Les exemples financiers ne sont pas des tarifs actuels.

Le socle traite désormais mesure, dimensionnement, optimisation, qualité et exploitation. Une spécialisation demandera encore une pratique sur le matériel cible : écriture de kernels, réglages précis des collectives, mécanismes internes de chaque architecture ou optimisation énergétique d’un site. Les listes d’options et noms de métriques doivent être confrontés à la version réellement déployée.

## Validation effectuée

- **Contenu** : 63 nouvelles cartes et 47 anciennes cartes précisées ; 34 résultats numériques recalculés en Python, couvrant notamment les 12 nouvelles cartes de calcul.
- **Navigation** : trois nouvelles fiches intégrées au MOC et au catalogue, connexions réciproques, résumés actualisés ; lint sans erreur ni avertissement.
- **Compatibilité** : les 1 793 identifiants de cartes actives présents avant cet audit sont conservés ; titres des sous-paquets existants inchangés.
- **Tests** : 40 tests existants réussissent ; catalogues synchronisés et `git diff --check` propre.
- **Export** : 1 856 cartes actives dans 129 fiches et 17 sections ; 293 mises en situation et 139 distinctions. Archive Anki et base SQLite vérifiées, anciens GUID et affectations aux sous-paquets conservés, 30 cartes retirées toujours suspendues.

Aucun benchmark GPU ou appel payant à une API n’a été exécuté pour cet audit. Les chiffres des cartes sont des calculs pédagogiques sous hypothèses explicites, pas des gains de production mesurés. L’export local `dist/ai-engineering.apkg` a été régénéré ; cet artefact reste exclu de Git.
