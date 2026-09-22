# Kubernetes GPU & inférence — Flashcards
Tags: #flashcards #kubernetes #gpu #llm #inference

Comment [[04-kubernetes-kubelet-cri|Kubernetes]] alloue-t-il les GPU aux Pods ?
?
Via le **NVIDIA device plugin** (déployé en **DaemonSet**), qui expose les GPU comme ressources planifiables.

---

Comment demander un GPU pour un conteneur dans Kubernetes ?
?
En déclarant la ressource **`nvidia.com/gpu`** dans les `resources.limits`.

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

---

Un GPU peut-il être partagé entre plusieurs Pods par défaut ?
?
**Non.** Par défaut un Pod obtient un **GPU entier** ; le partage nécessite **MIG** ou le **time-slicing**.

---

Qu'est-ce que MIG (Multi-Instance GPU) ?
?
Une technologie NVIDIA qui **partitionne un GPU** (ex. A100/H100) en **instances isolées**, utilisables par des Pods distincts.

---

À quoi servent les node selectors, taints et tolerations pour le GPU ?
?
À **cibler et réserver les nodes GPU** afin que seuls les workloads adéquats y soient planifiés.

---

Que sont KServe et Kubeflow ?
?
Des **plateformes de serving de modèles sur Kubernetes** (déploiement, scaling, routage des requêtes d'inférence).

---

Comment gère-t-on la charge variable d'un service d'inférence sur Kubernetes ?
?
Par l'**autoscaling** (HPA/KEDA), parfois avec **scale-to-zero** pour libérer le GPU quand il n'est pas utilisé.

---

Pourquoi la gestion des GPU est-elle si importante en inférence sur Kubernetes ?
?
Parce que le **GPU est une ressource rare et coûteuse** : son allocation et son partage conditionnent le coût et la densité du service.

---

## Connexions
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — base d'orchestration
- [[09-gpu-conteneurs|GPU en conteneur]] — accès GPU
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — ce qu'on déploie
- [[10-images-modeles-poids|Images & poids]] — pull time des grosses images
- [[83-gateway-ingress|Ingress & API gateway]] — l'entrée réseau du serving
- [[64-metriques-slo-inference|Métriques & SLO]] — les signaux d'autoscaling
- [[122-finops-llm|FinOps LLM]] — le coût du GPU idle
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
