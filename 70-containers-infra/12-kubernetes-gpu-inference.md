# Kubernetes GPU & inférence — Flashcards
Tags: #flashcards #kubernetes #gpu #llm #inference
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Comment [[04-kubernetes-kubelet-cri|Kubernetes]] alloue-t-il les GPU aux Pods ?
?
<!--anki:782d706f674268736979-->
Via le **NVIDIA device plugin**, déployé en **DaemonSet** : il découvre les GPU de chaque node, les **annonce au kubelet** comme ressource `nvidia.com/gpu`, et fournit au runtime les devices à injecter quand un Pod en demande. Le scheduler ne fait ensuite que de l'**arithmétique entière** sur cette ressource.

En pratique, on l'installe via le **GPU Operator**, qui gère aussi driver, toolkit, métriques DCGM et configuration MIG ([[09-gpu-conteneurs|GPU en conteneur]]).

---

Comment demander un GPU pour un conteneur dans Kubernetes ?
?
<!--anki:6f716621355b686f6048-->
En déclarant la ressource **`nvidia.com/gpu`** dans les `resources.limits`.

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

---

Un GPU peut-il être partagé entre plusieurs Pods par défaut ?
?
<!--anki:4f2d4d2f21696245696b-->
**Non.** La ressource `nvidia.com/gpu` est **entière et exclusive** : on ne peut pas demander « 0,5 GPU ». Un Pod qui obtient le GPU le garde pour lui, même s'il ne l'utilise qu'à 10 %.

Trois façons de partager :
- **MIG** : partitions **matériellement isolées** (mémoire et calcul dédiés)
- **Time-slicing** : plusieurs Pods se relaient sur le GPU, **sans isolation mémoire**
- **MPS** : exécution concurrente des noyaux, pour des charges qui se font confiance

---

Qu'est-ce que MIG (Multi-Instance GPU) ?
?
<!--anki:6e4870724d693d6c2b2a-->
Une technologie NVIDIA qui **partitionne physiquement** un GPU (A100, H100, H200, B200) en **instances isolées**, chacune avec sa mémoire et ses unités de calcul. Chaque instance apparaît comme un GPU distinct, donc allouable à un Pod différent.
```text
A100 80 Go → jusqu'à 7 instances (profils 1g.10gb, 2g.20gb, 3g.40gb…)
```
Intérêt : servir plusieurs **petits modèles** ou environnements de test sans qu'ils se gênent. Limite : les profils sont **fixés à l'avance** et le reconfigurer demande de vider le node.

---

À ne pas confondre : MIG et time-slicing ?
?
<!--anki:6b3b5f755d694f4f6851-->
- **MIG** : isolation **matérielle**. Mémoire dédiée, performances prévisibles, nombre d'instances limité par les profils
- **Time-slicing** : simple **partage temporel**. Aucune isolation mémoire, un Pod peut saturer la VRAM et faire tomber les autres, mais le partage est souple et sans reconfiguration

Règle : **MIG pour la production multi-tenant**, time-slicing pour du développement ou des charges tolérantes.

---

À quoi servent les node selectors, taints et tolerations pour le GPU ?
?
<!--anki:786472704640764f4057-->
À **cibler et réserver les nodes GPU** :
- **Node selector ou affinité** : « place-moi sur un node qui a des H100 ». C'est le Pod qui **choisit**
- **Taint sur le node** : « personne ne vient ici sans y être invité ». C'est le node qui **repousse**
- **Toleration sur le Pod** : le laissez-passer qui permet d'ignorer le taint

Sans taint, des charges sans GPU viennent occuper la mémoire et le CPU de machines à plusieurs dizaines de milliers d'euros. Le GPU Operator pose des **labels** (modèle de GPU, profil MIG) directement exploitables par les sélecteurs.

---

Que sont KServe et Kubeflow ?
?
<!--anki:63503c706e2e62445352-->
- **KServe** : une couche de **serving de modèles** sur Kubernetes. Une ressource `InferenceService` décrit le modèle et son runtime, et KServe gère endpoint, autoscaling (jusqu'au scale-to-zero), versions et découpage du trafic (canary)
- **Kubeflow** : une **suite MLOps** plus large (notebooks, pipelines, entraînement, tuning), dont KServe a été extrait

Alternative fréquente pour les LLM : un Deployment vLLM classique, plus un routeur conscient du cache ([[66-prefix-caching-radix-attention|routage cache-aware]]).

---

Comment gère-t-on la charge variable d'un service d'inférence sur Kubernetes ?
?
<!--anki:4b5451773748245e6355-->
Par l'**autoscaling** : le **HPA** sur des métriques personnalisées, ou **KEDA** pour se brancher directement sur Prometheus. On scale sur la **file d'attente** et l'**occupation du KV cache**, pas sur l'utilisation GPU ([[93-monitoring-inference|métriques]]).
```yaml
resources:
  limits:
    nvidia.com/gpu: 1        # entier, exclusif
nodeSelector:
  nvidia.com/gpu.product: NVIDIA-H100-80GB-HBM3
tolerations:
  - key: nvidia.com/gpu
    operator: Exists
```
Le **scale-to-zero** ne vaut que si l'on accepte un **cold start** de plusieurs minutes ([[10-images-modeles-poids|cold start]]).

---

Pourquoi la gestion des GPU est-elle si importante en inférence sur Kubernetes ?
?
<!--anki:697851257b26396e486d-->
Parce que le **GPU est une ressource rare et coûteuse** : son allocation et son partage conditionnent le coût et la densité du service.

---

## Mises en situation

Mise en situation : ton service d'inférence tourne sur 4 GPU A100 réservés en permanence, mais le trafic est concentré sur les heures de bureau. Comment réduis-tu la facture sans casser le service ?
?
<!--anki:474124573d3839286841-->
1. **Mesurer le profil réel** : trafic par heure, concurrence de pointe, SLO à tenir ([[64-metriques-slo-inference|SLO]])
2. **Autoscaling** sur la file d'attente et l'occupation du KV cache, pas sur l'utilisation GPU
3. **Anticiper le cold start** : plusieurs minutes pour charger les poids, donc garder un socle de réplicas chauds ([[10-images-modeles-poids|cold start]])
4. **Scale-to-zero** uniquement pour les environnements non critiques (préproduction, batch)
5. **Densifier** : MIG pour les petits modèles, quantization pour tenir sur moins de GPU ([[68-quantization|quantization]])

**Piège** : un scale-to-zero en production qui fait payer plusieurs minutes d'attente au premier utilisateur du matin.

---

Mise en situation : plusieurs équipes veulent déployer leurs modèles sur le même cluster GPU, et se disputent les ressources. Comment organises-tu le partage ?
?
<!--anki:76356329543d292b5349-->
1. **Réserver les nodes GPU** aux charges concernées avec taints et tolerations
2. **Quotas par namespace** : nombre de GPU par équipe, plutôt qu'une course au premier arrivé
3. **Partage fin** : MIG pour isoler des instances, time-slicing seulement pour les charges tolérantes
4. **Priorités** : classes de priorité et préemption pour les charges critiques
5. **Visibilité** : consommation et coût par équipe, sinon rien ne change ([[122-finops-llm|FinOps]])

**Piège** : laisser chaque équipe demander « 1 GPU » pour des services inactifs la moitié du temps.

---

## Sources

- [Kubernetes — planification des GPU](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)

## Connexions
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — base d'orchestration
- [[09-gpu-conteneurs|GPU en conteneur]] — accès GPU
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — ce qu'on déploie
- [[10-images-modeles-poids|Images & poids]] — pull time des grosses images
- [[83-gateway-ingress|Ingress & API gateway]] — l'entrée réseau du serving
- [[64-metriques-slo-inference|Métriques & SLO]] — les signaux d'autoscaling
- [[122-finops-llm|FinOps LLM]] — le coût du GPU idle
- [[00-index|Index Conteneurs]]
- [[93-monitoring-inference|Monitoring de l'inférence]] — métriques GPU (DCGM) et signaux d'autoscaling
- [[69-roofline-prefill-decode|Désagrégation prefill/decode]] — deux pools à autoscaler séparément
- [[112-cicd-modeles|CI/CD des modèles]] — eval gates, canary et rollback
- [[13-apptainer-inference-hpc|Apptainer & inférence HPC]] — servir un modèle sur un cluster Slurm
- [[136-mixture-of-experts|Mixture of Experts]] — paramètres totaux et actifs
- [[61-kv-cache-attention|KV cache]] — la mémoire qui limite la concurrence
- [[62-optimisations-inference|Optimisations d'inférence]] — les leviers de latence et de débit
- [[00-moc-ai-engineering|MOC AI Engineering]]
