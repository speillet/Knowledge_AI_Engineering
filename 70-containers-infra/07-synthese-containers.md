# Conteneurs — Synthèse
Tags: #flashcards #conteneurs #revision

OCI, CRI et SIF désignent-ils le même type de chose ?
?
**Non.**

- OCI → standards ouverts des conteneurs
- CRI → interface Kubernetes ↔ container runtime
- SIF → format d'image Singularity/Apptainer

---

Quelle chaîne Kubernetes faut-il savoir reconstruire ?
?
```text
Kubernetes
    ↓
kubelet
    ↓
CRI
    ↓
containerd
    ↓
runc
    ↓
Linux Kernel
```

---

Quelle chaîne représente un workflow classique d'image ?
?
```text
Dockerfile
    ↓
docker build
    ↓
Image OCI
    ↓
Registry
    ↓
pull
    ↓
Runtime
    ↓
Container
```

---

Comment résumer Docker, Kubernetes, containerd et runc ?
?
**Docker construit/manipule les conteneurs, Kubernetes les orchestre, containerd les gère et runc réalise leur exécution bas niveau.**

---

Comment distinguer namespaces et cgroups ?
?
**Les [[08-linux-primitives-docker-fondamentaux|namespaces]] isolent (ce qu'un processus voit) ; les [[08-linux-primitives-docker-fondamentaux|cgroups]] limitent (ce qu'un processus consomme).**

---

Comment donne-t-on accès au GPU selon l'environnement ?
?
- [[09-gpu-conteneurs|Docker]] → `--gpus`
- [[13-apptainer-inference-hpc|Apptainer]] → `--nv`
- [[12-kubernetes-gpu-inference|Kubernetes]] → ressource `nvidia.com/gpu`

---

Quels serveurs d'inférence LLM conteneurisés faut-il connaître ?
?
**[[11-serveurs-inference-llm|vLLM, NVIDIA Triton, TGI]]** (et TensorRT-LLM, Ollama).

---

Où stocker les poids d'un modèle plutôt que dans l'image ?
?
Dans un **[[08-linux-primitives-docker-fondamentaux|volume / bind mount]]** ou un **stockage externe** ; on évite de « baker » les poids dans l'image. → [[10-images-modeles-poids|Images & poids]]

---

Définis en une phrase : OCI, image, conteneur, registry.
?
- **OCI** : l'initiative qui standardise le format des images, le runtime et la distribution des conteneurs ([[01-oci|OCI]])
- **Image** : un paquet **immuable en couches** qui contient une application et ses dépendances
- **Conteneur** : une **instance en cours d'exécution** d'une image, isolée du reste du système
- **Registry** : le serveur qui **stocke et distribue** les images (push, pull)

---

Définis en une phrase : Kubernetes, kubelet, CRI.
?
- **Kubernetes** : l'orchestrateur qui déploie et maintient des conteneurs sur un **cluster**
- **kubelet** : l'agent de **chaque nœud**, qui fait tourner les Pods qu'on lui assigne
- **CRI** : l'**interface standard** entre le kubelet et le runtime de conteneurs ([[04-kubernetes-kubelet-cri|Kubernetes & CRI]])

---

Définis en une phrase : containerd, runc.
?
- **containerd** : le runtime de **haut niveau** qui gère les images et le cycle de vie des conteneurs (appelé par le kubelet via le CRI)
- **runc** : le runtime **bas niveau**, conforme OCI, qui crée réellement le conteneur avec les primitives du noyau ([[03-containerd-runc|containerd & runc]])

---

Définis en une phrase : Apptainer, SIF.
?
- **Apptainer** : le runtime de conteneurs du **HPC** (ex-Singularity), sans démon et sans droits root ([[06-apptainer-singularity|Apptainer]])
- **SIF** : le format d'image d'Apptainer, un **fichier unique** et immuable

---

Définis en une phrase : NVIDIA Container Toolkit, device plugin, MIG.
?
- **NVIDIA Container Toolkit** : ce qui **expose les GPU et le driver** de l'hôte à l'intérieur d'un conteneur ([[09-gpu-conteneurs|GPU en conteneur]])
- **Device plugin** : le composant qui **annonce les GPU à Kubernetes**, sous la ressource `nvidia.com/gpu`
- **MIG** : le **partitionnement d'un GPU** (A100, H100) en instances isolées ([[12-kubernetes-gpu-inference|Kubernetes GPU]])

---

Définis en une phrase : vLLM, Triton, TGI.
?
- **vLLM** : le serveur d'inférence LLM open source **de référence** (PagedAttention, continuous batching, API compatible OpenAI)
- **Triton** : le serveur d'inférence **multi-framework** de NVIDIA
- **TGI** : le serveur de Hugging Face, historiquement très utilisé, aujourd'hui **en mode maintenance** ([[11-serveurs-inference-llm|serveurs d'inférence]])

---

Définis en une phrase : KV cache, cold start.
?
- **KV cache** : les **clés et valeurs d'attention** gardées en mémoire, pour ne pas recalculer tout le contexte à chaque token ([[61-kv-cache-attention|KV cache]])
- **Cold start** : le **délai avant la première réponse** d'un nouveau réplica : pull de l'image, téléchargement des poids, chargement en VRAM ([[10-images-modeles-poids|images & poids]])

---

## Mises en situation

Mise en situation : en entretien, on te demande de décrire ce qui se passe entre `kubectl apply` et un conteneur qui tourne sur un GPU. Que racontes-tu ?
?
1. **Côté control plane** : l'API server enregistre l'objet, le scheduler choisit un node qui satisfait les ressources demandées, dont `nvidia.com/gpu`
2. **Sur le node** : le kubelet reçoit le Pod et appelle le runtime par la **CRI**
3. **Chaîne d'exécution** : `containerd → runc → noyau Linux`, avec namespaces et cgroups
4. **GPU** : le NVIDIA Container Toolkit injecte devices et bibliothèques du driver de l'hôte
5. **Démarrage applicatif** : pull de l'image, chargement des poids, probes qui font passer le Pod prêt

**Piège** : sauter la CRI et parler de « Docker qui lance le conteneur » sur un cluster moderne.

---

Mise en situation : un nouvel arrivant confond OCI, CRI et SIF dans ses schémas d'architecture. Comment clarifies-tu en trois phrases ?
?
- **OCI** : les **standards** des conteneurs (image, runtime, distribution)
- **CRI** : l'**interface** entre le kubelet de Kubernetes et le runtime de conteneurs
- **SIF** : le **format d'image** d'Apptainer, utilisé en HPC

Repère utile : OCI dit à quoi ressemble une image, CRI dit comment Kubernetes demande son exécution, SIF est un format concurrent pour un autre contexte.

**Piège** : présenter CRI comme un format d'image, alors que c'est une API.

---

## Connexions
- [[00-index|Index Conteneurs (MOC)]] — carte complète du sujet
- [[00-moc-ai-engineering|MOC AI Engineering]]
