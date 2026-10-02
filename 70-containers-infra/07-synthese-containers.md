# Conteneurs — Synthèse
Tags: #flashcards #conteneurs #revision
<!-- summary: cartes de révision transverses (OCI, CRI et SIF, chaînes Kubernetes et image, accès GPU, serveurs d'inférence, stockage des poids). -->

OCI, CRI et SIF désignent-ils le même type de chose ?
?
<!--anki:6d445f2c347a236f5d4c-->
**Non.**

- OCI → standards ouverts des conteneurs
- CRI → interface Kubernetes ↔ container runtime
- SIF → format d'image Singularity/Apptainer

---

Quelle chaîne Kubernetes faut-il savoir reconstruire ?
?
<!--anki:6f705f3e4421453a6f2d-->
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
<!--anki:7232636a597439215430-->
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
<!--anki:4a54653c552f697c7a31-->
**Docker construit/manipule les conteneurs, Kubernetes les orchestre, containerd les gère et runc réalise leur exécution bas niveau.**

---

Comment distinguer namespaces et cgroups ?
?
<!--anki:7230625557696a456f63-->
**Les [[08-linux-primitives-docker-fondamentaux|namespaces]] isolent (ce qu'un processus voit) ; les [[08-linux-primitives-docker-fondamentaux|cgroups]] limitent (ce qu'un processus consomme).**

---

Comment donne-t-on accès au GPU selon l'environnement ?
?
<!--anki:434a6a212c3b70547052-->
- [[09-gpu-conteneurs|Docker]] → `--gpus`
- [[13-apptainer-inference-hpc|Apptainer]] → `--nv`
- [[12-kubernetes-gpu-inference|Kubernetes]] → ressource `nvidia.com/gpu`

---

Quel serveur d'inférence pour quel usage : production GPU, performance maximale NVIDIA, modèles hétérogènes, poste local ?
?
<!--anki:3835303563363764303133313463393461306134623039613434386130383463-->
- **Production sur GPU**, API compatible OpenAI : **vLLM** ou **SGLang**
- **Performance maximale sur GPU NVIDIA** : **TensorRT-LLM**, souvent servi par **Triton**
- **Plusieurs types de modèles** (LLM, vision, modèles classiques) derrière un même serveur : **Triton**
- **Poste local** : **Ollama** ou llama.cpp

TGI est en mode maintenance ([[11-serveurs-inference-llm|serveurs d'inférence]]).

---

Où stocker les poids d'un modèle plutôt que dans l'image ?
?
<!--anki:7a6525313b45373b7221-->
Dans un **[[08-linux-primitives-docker-fondamentaux|volume / bind mount]]** ou un **stockage externe** ; on évite de « baker » les poids dans l'image. → [[10-images-modeles-poids|Images & poids]]

---

Définis en une phrase : OCI, image, conteneur, registry.
?
<!--anki:73492d33343547474e48-->
- **OCI** : l'initiative qui standardise le format des images, le runtime et la distribution des conteneurs ([[01-oci|OCI]])
- **Image** : un paquet **immuable en couches** qui contient une application et ses dépendances
- **Conteneur** : une **instance en cours d'exécution** d'une image, isolée du reste du système
- **Registry** : le serveur qui **stocke et distribue** les images (push, pull)

---

Définis en une phrase : Kubernetes, kubelet, CRI.
?
<!--anki:516c7c5379535d552f54-->
- **Kubernetes** : l'orchestrateur qui déploie et maintient des conteneurs sur un **cluster**
- **kubelet** : l'agent de **chaque nœud**, qui fait tourner les Pods qu'on lui assigne
- **CRI** : l'**interface standard** entre le kubelet et le runtime de conteneurs ([[04-kubernetes-kubelet-cri|Kubernetes & CRI]])

---

Définis en une phrase : containerd, runc.
?
<!--anki:4a3a2141514b24426a64-->
- **containerd** : le runtime de **haut niveau** qui gère les images et le cycle de vie des conteneurs (appelé par le kubelet via le CRI)
- **runc** : le runtime **bas niveau**, conforme OCI, qui crée réellement le conteneur avec les primitives du noyau ([[03-containerd-runc|containerd & runc]])

---

Définis en une phrase : Apptainer, SIF.
?
<!--anki:77763777364e6b7a5674-->
- **Apptainer** : le runtime de conteneurs du **HPC** (ex-Singularity), sans démon et sans droits root ([[06-apptainer-singularity|Apptainer]])
- **SIF** : le format d'image d'Apptainer, un **fichier unique** et immuable

---

Définis en une phrase : NVIDIA Container Toolkit, device plugin, MIG.
?
<!--anki:463e2f2d4074386c7a2d-->
- **NVIDIA Container Toolkit** : ce qui **expose les GPU et le driver** de l'hôte à l'intérieur d'un conteneur ([[09-gpu-conteneurs|GPU en conteneur]])
- **Device plugin** : le composant qui **annonce les GPU à Kubernetes**, sous la ressource `nvidia.com/gpu`
- **MIG** : le **partitionnement d'un GPU** (A100, H100) en instances isolées ([[12-kubernetes-gpu-inference|Kubernetes GPU]])

---

Définis en une phrase : vLLM, Triton, TGI.
?
<!--anki:7860645e5e44623d6a3b-->
- **vLLM** : le serveur d'inférence LLM open source **de référence** (PagedAttention, continuous batching, API compatible OpenAI)
- **Triton** : le serveur d'inférence **multi-framework** de NVIDIA
- **TGI** : le serveur de Hugging Face, historiquement très utilisé, aujourd'hui **en mode maintenance** ([[11-serveurs-inference-llm|serveurs d'inférence]])

---

Définis en une phrase : KV cache, cold start.
?
<!--anki:6370427b363d21607d52-->
- **KV cache** : les **clés et valeurs d'attention** gardées en mémoire, pour ne pas recalculer tout le contexte à chaque token ([[61-kv-cache-attention|KV cache]])
- **Cold start** : le **délai avant la première réponse** d'un nouveau réplica : pull de l'image, téléchargement des poids, chargement en VRAM ([[10-images-modeles-poids|images & poids]])

---

## Mises en situation

Mise en situation : en entretien, on te demande de décrire ce qui se passe entre `kubectl apply` et un conteneur qui tourne sur un GPU. Que racontes-tu ?
?
<!--anki:6936707d517d30363e60-->
1. **Côté control plane** : l'API server enregistre l'objet, le scheduler choisit un node qui satisfait les ressources demandées, dont `nvidia.com/gpu`
2. **Sur le node** : le kubelet reçoit le Pod et appelle le runtime par la **CRI**
3. **Chaîne d'exécution** : `containerd → runc → noyau Linux`, avec namespaces et cgroups
4. **GPU** : le NVIDIA Container Toolkit injecte devices et bibliothèques du driver de l'hôte
5. **Démarrage applicatif** : pull de l'image, chargement des poids, probes qui font passer le Pod prêt

**Piège** : sauter la CRI et parler de « Docker qui lance le conteneur » sur un cluster moderne.

---

Mise en situation : un nouvel arrivant confond OCI, CRI et SIF dans ses schémas d'architecture. Comment clarifies-tu en trois phrases ?
?
<!--anki:687a5b75263a75293542-->
- **OCI** : les **standards** des conteneurs (image, runtime, distribution)
- **CRI** : l'**interface** entre le kubelet de Kubernetes et le runtime de conteneurs
- **SIF** : le **format d'image** d'Apptainer, utilisé en HPC

Repère utile : OCI dit à quoi ressemble une image, CRI dit comment Kubernetes demande son exécution, SIF est un format concurrent pour un autre contexte.

**Piège** : présenter CRI comme un format d'image, alors que c'est une API.

---

## Connexions
- [[00-index|Index Conteneurs (MOC)]] — carte complète du sujet
- [[00-moc-ai-engineering|MOC AI Engineering]]
