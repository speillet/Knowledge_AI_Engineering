# Kubernetes, kubelet & CRI — Flashcards
Tags: #flashcards #kubernetes #conteneurs #infra
<!-- summary: Pod, Deployment, Service, control plane, kubelet, CRI (containerd, CRI-O), scheduler, requests et limits, probes. -->

Qu'est-ce que Kubernetes ?
?
<!--anki:727e3f4d405d3b296743-->
Un **orchestrateur de conteneurs** : on déclare l'**état désiré** (quelles applications, combien de réplicas, quelles ressources) et des contrôleurs le **maintiennent en continu** (redémarrage, placement, scaling).

---

Qu'est-ce qu'un Pod ?
?
<!--anki:7850754b2339264c582f-->
La **plus petite unité déployable** : un ou plusieurs conteneurs qui partagent le **réseau** (même IP, même `localhost`) et des **volumes**, planifiés ensemble sur un même node. Un Pod est **éphémère et jamais modifié** : on le remplace. Les conteneurs annexes servent de **sidecars** (proxy, collecte de logs) ou d'**init containers**, par exemple pour télécharger les poids d'un modèle avant le démarrage du serveur ([[10-images-modeles-poids|poids]]).

---

Quel est le rôle d'un Deployment ?
?
<!--anki:62577b514a5248636034-->
Gérer un ensemble de **Pods identiques** (via un ReplicaSet) : nombre de réplicas, **rolling updates** et rollback.

---

À quoi sert un Service Kubernetes ?
?
<!--anki:4c2d5e652833592c4a4e-->
À fournir une **adresse stable** (IP virtuelle et nom DNS) devant des Pods éphémères, avec **répartition de charge** entre eux.

---

Que contient le control plane de Kubernetes ?
?
<!--anki:484723506a4126657e57-->
- **kube-apiserver** : point d'entrée de toutes les opérations
- **etcd** : base clé-valeur de l'état du cluster
- **kube-scheduler** : choisit le node de chaque Pod
- **controller-manager** : boucles de réconciliation

---

Quel est le rôle du kubelet ?
?
<!--anki:526151232c463e387774-->
L'**agent présent sur chaque node** : il reçoit les Pods assignés, demande au runtime de **lancer les conteneurs**, surveille leur santé (probes) et **remonte leur état** à l'API server.

---

Qu'est-ce que la CRI ?
?
<!--anki:792f3230294d735a244f-->
La **Container Runtime Interface** : l'API (gRPC) par laquelle le kubelet pilote **n'importe quel runtime** compatible, comme **containerd** ou **CRI-O**. Le support direct de Docker (dockershim) a été retiré en v1.24.

---

Comment le scheduler choisit-il un node ?
?
<!--anki:6f6d4e346d365b51612c-->
Il **filtre** les nodes capables d'accueillir le Pod (ressources demandées, node selectors, taints/tolerations, affinités), puis **note** les candidats restants et prend le meilleur.

---

À ne pas confondre : requests et limits ?
?
<!--anki:6257312a413972352b79-->
- **Requests** : ressources **réservées**, utilisées par le scheduler pour placer le Pod
- **Limits** : **plafond** d'usage ; dépassement mémoire → **OOMKilled**, dépassement CPU → ralenti (throttling)

---

Qu'est-ce qu'un DaemonSet ?
?
<!--anki:647c2c386d5138336533-->
Un contrôleur qui lance **un Pod sur chaque node** (ou chaque node sélectionné) : agents de logs, monitoring, ou le **NVIDIA device plugin** ([[12-kubernetes-gpu-inference|GPU]]).

---

Pourquoi les probes sont-elles importantes pour un serveur LLM ?
?
<!--anki:622e723e7a6d7d574d23-->
Un serveur d'inférence met **plusieurs minutes à charger les poids** : une **startupProbe** évite qu'il soit tué pendant le chargement, et la **readinessProbe** ne lui envoie du trafic qu'une fois prêt.
```yaml
startupProbe:                 # tolère 10 min de chargement
  httpGet: { path: /health, port: 8000 }
  failureThreshold: 60
  periodSeconds: 10
readinessProbe:               # n'envoie du trafic qu'une fois le modèle chargé
  httpGet: { path: /health, port: 8000 }
```
Sans startupProbe, la **livenessProbe** tue le conteneur en boucle avant qu'il ait fini de démarrer.

---

À ne pas confondre : Service et Ingress ?
?
<!--anki:4e357775664e4c37644a-->
- **Service** : une adresse stable **à l'intérieur** du cluster (IP virtuelle et nom DNS) devant des Pods éphémères, avec répartition de charge
- **Ingress** : l'entrée **depuis l'extérieur** en HTTP(S), qui route vers des Services selon l'hôte et le chemin ([[83-gateway-ingress|Ingress]])

Un Service seul n'expose rien sur Internet ; un Ingress sans Service ne sait pas où envoyer le trafic.

---

## Mises en situation

Mise en situation : ton Pod vLLM est tué et redémarré en boucle au démarrage, avant même d'avoir répondu à une requête. Que vérifies-tu ?
?
<!--anki:46422c54432f78477a62-->
1. **Les probes** : sans **startupProbe**, la livenessProbe tue le conteneur pendant le chargement des poids, qui prend plusieurs minutes
2. **La readinessProbe** : elle ne doit passer au vert qu'une fois le modèle chargé, pour ne pas recevoir de trafic trop tôt
3. **La mémoire** : un `OOMKilled` indique une limite mémoire trop basse, pas un problème de probe
4. **Les ressources** : requests et limits cohérentes, GPU bien demandé ([[12-kubernetes-gpu-inference|K8s GPU]])
5. **Les logs et événements** du Pod, pour distinguer échec de démarrage et échec de santé

**Piège** : allonger le délai de la livenessProbe au lieu d'utiliser une startupProbe.

---

Mise en situation : une équipe demande pourquoi ses Pods GPU restent en attente alors que le cluster « a des GPU libres ». Comment expliques-tu le placement ?
?
<!--anki:495e636128334b48256a-->
1. **Le scheduler filtre puis note** : il ne retient que les nodes capables d'accueillir le Pod
2. **Ressources demandées** : un GPU se demande explicitement comme ressource, et il n'est pas partageable par défaut
3. **Taints et tolerations** : les nodes GPU sont souvent teintés pour n'accueillir que les charges concernées
4. **Requests trop élevées** : mémoire ou CPU demandés au-delà de ce qu'un node peut offrir
5. **Vérifier** les événements du Pod, qui indiquent la raison exacte du rejet par node

**Piège** : regarder l'utilisation réelle des nodes plutôt que leurs ressources **réservées**.

---

## Connexions
- [[00-index|Index Conteneurs]] — conteneurs, OCI, Docker
- [[09-gpu-conteneurs|GPU en conteneur]] — ce que le runtime doit exposer
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — l'application aux LLM
- [[83-gateway-ingress|Ingress & API gateway]] — exposer les Services
- [[01-oci|OCI]] — à ne pas confondre avec CRI
- [[03-containerd-runc|containerd & runc]] — le runtime derrière CRI
- [[05-docker-kubernetes|Docker & Kubernetes]] — l'histoire de dockershim
- [[07-synthese-containers|Synthèse conteneurs]] — de `kubectl apply` au processus
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM et leur réglage
- [[00-moc-ai-engineering|MOC AI Engineering]]
