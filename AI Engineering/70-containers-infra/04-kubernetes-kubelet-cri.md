# Kubernetes, kubelet & CRI — Flashcards
Tags: #flashcards #kubernetes #conteneurs #infra

Qu'est-ce que Kubernetes ?
?
Un **orchestrateur de conteneurs** : on déclare l'**état désiré** (quelles applications, combien de réplicas, quelles ressources) et des contrôleurs le **maintiennent en continu** (redémarrage, placement, scaling).

---

Qu'est-ce qu'un Pod ?
?
La **plus petite unité déployable** : un ou plusieurs conteneurs qui partagent le **réseau** (même IP) et des **volumes**, planifiés ensemble sur un même node.

---

Quel est le rôle d'un Deployment ?
?
Gérer un ensemble de **Pods identiques** (via un ReplicaSet) : nombre de réplicas, **rolling updates** et rollback.

---

À quoi sert un Service ?
?
À fournir une **adresse stable** (IP virtuelle et nom DNS) devant des Pods éphémères, avec **répartition de charge** entre eux.

---

Que contient le control plane ?
?
- **kube-apiserver** : point d'entrée de toutes les opérations
- **etcd** : base clé-valeur de l'état du cluster
- **kube-scheduler** : choisit le node de chaque Pod
- **controller-manager** : boucles de réconciliation

---

Quel est le rôle du kubelet ?
?
L'**agent présent sur chaque node** : il reçoit les Pods assignés, demande au runtime de **lancer les conteneurs**, surveille leur santé (probes) et **remonte leur état** à l'API server.

---

Qu'est-ce que la CRI ?
?
La **Container Runtime Interface** : l'API (gRPC) par laquelle le kubelet pilote **n'importe quel runtime** compatible, comme **containerd** ou **CRI-O**. Le support direct de Docker (dockershim) a été retiré en v1.24.

---

Comment le scheduler choisit-il un node ?
?
Il **filtre** les nodes capables d'accueillir le Pod (ressources demandées, node selectors, taints/tolerations, affinités), puis **note** les candidats restants et prend le meilleur.

---

Quelle différence entre requests et limits ?
?
- **Requests** : ressources **réservées**, utilisées par le scheduler pour placer le Pod
- **Limits** : **plafond** d'usage ; dépassement mémoire → **OOMKilled**, dépassement CPU → ralenti (throttling)

---

Qu'est-ce qu'un DaemonSet ?
?
Un contrôleur qui lance **un Pod sur chaque node** (ou chaque node sélectionné) : agents de logs, monitoring, ou le **NVIDIA device plugin** ([[12-kubernetes-gpu-inference|GPU]]).

---

Pourquoi les probes sont-elles importantes pour un serveur LLM ?
?
Un serveur d'inférence met **plusieurs minutes à charger les poids** : une **startupProbe** évite qu'il soit tué pendant le chargement, et la **readinessProbe** ne lui envoie du trafic qu'une fois prêt.

---

## Connexions
- [[00-index|Index Conteneurs]] — conteneurs, OCI, Docker
- [[09-gpu-conteneurs|GPU en conteneur]] — ce que le runtime doit exposer
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — l'application aux LLM
- [[83-gateway-ingress|Ingress & API gateway]] — exposer les Services
- [[01-oci|OCI]] — à ne pas confondre avec CRI
- [[03-containerd-runc|containerd & runc]] — le runtime derrière CRI
- [[05-docker-kubernetes|Docker & Kubernetes]] — l'histoire de dockershim
- [[00-moc-ai-engineering|MOC AI Engineering]]
