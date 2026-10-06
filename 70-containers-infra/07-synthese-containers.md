# Conteneurs — Synthèse
Tags: #flashcards #conteneurs #revision
<!-- summary: cartes de révision transverses (OCI, CRI et SIF, chaînes Kubernetes et image, accès GPU, serveurs d'inférence, stockage des poids). -->


OCI, CRI et SIF désignent-ils le même type de chose ? <!--anki:6d445f2c347a236f5d4c-->
?
**Non.**

- OCI → standards ouverts des conteneurs
- CRI → interface Kubernetes ↔ container runtime
- SIF → format d'image Singularity/Apptainer

Ils concernent trois niveaux : OCI favorise l'interopérabilité, CRI relie le kubelet à son runtime, SIF empaquette une image destinée à Apptainer. Par exemple, construire avec Docker puis exécuter dans Kubernetes concerne OCI et CRI ; convertir une image en fichier Apptainer concerne SIF. Aucun de ces noms ne remplace les deux autres.

---

Quelle chaîne Kubernetes faut-il savoir reconstruire ? <!--anki:6f705f3e4421453a6f2d-->
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

C'est une **chaîne possible**, fréquente : le kubelet demande l'exécution via la CRI, containerd gère le cycle de vie et délègue la création du processus à un runtime OCI tel que runc. Le noyau fournit isolation et contrôle des ressources. D'autres implémentations peuvent remplacer containerd ou runc tout en respectant les interfaces attendues.

---

Quelle chaîne représente un workflow classique d'image ? <!--anki:7232636a597439215430-->
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

Le Dockerfile décrit la construction ; l'image est l'artefact versionné ; le registry la distribue. Le runtime prépare ensuite une instance exécutable, le **conteneur**, avec processus, réseau et montages. Plusieurs conteneurs peuvent partir de la même image. Les données écrites pendant l'exécution ne deviennent pas automatiquement une nouvelle version de cette image.

---

Comment résumer Docker, Kubernetes, containerd et runc ? <!--anki:4a54653c552f697c7a31-->
?
**Docker construit/manipule les conteneurs, Kubernetes les orchestre, containerd les gère et runc réalise leur exécution bas niveau.**

Ces responsabilités se complètent : un développeur construit une image avec Docker, Kubernetes place des Pods, puis containerd et runc réalisent leur exécution sur le nœud. Ce schéma aide au diagnostic : une erreur de pull, une erreur de scheduling et un refus d'appel système ne se cherchent pas au même niveau.

---

Comment donne-t-on accès au GPU selon l'environnement ? <!--anki:434a6a212c3b70547052-->
?
- [[09-gpu-conteneurs|Docker]] → `--gpus`
- [[13-apptainer-inference-hpc|Apptainer]] → `--nv`
- [[12-kubernetes-gpu-inference|Kubernetes]] → ressource `nvidia.com/gpu`

Ces options expriment un accès ou une allocation, mais nécessitent une pile GPU fonctionnelle sur l'hôte. Sous Docker, configurer le Container Toolkit ; sous Kubernetes, publier les ressources via le device plugin ; en HPC, obtenir aussi l'allocation de l'ordonnanceur. Aucun de ces réglages n'augmente la VRAM disponible ni ne corrige une incompatibilité de driver.

---

Quel serveur d'inférence pour quel usage : production GPU, performance maximale NVIDIA, modèles hétérogènes, poste local ? <!--anki:3835303563363764303133313463393461306134623039613434386130383463-->
?
- **Production sur GPU**, API compatible OpenAI : **vLLM** ou **SGLang**
- **Performance maximale sur GPU NVIDIA** : **TensorRT-LLM**, souvent servi par **Triton**
- **Plusieurs types de modèles** (LLM, vision, modèles classiques) derrière un même serveur : **Triton**
- **Poste local** : **Ollama** ou llama.cpp

TGI est en mode maintenance ([[11-serveurs-inference-llm|serveurs d'inférence]]).

---

Où stocker les poids d'un modèle plutôt que dans l'image ? <!--anki:7a6525313b45373b7221-->
?
Dans un **[[08-linux-primitives-docker-fondamentaux|volume / bind mount]]** ou un **stockage externe** ; on évite de « baker » les poids dans l'image. → [[10-images-modeles-poids|Images & poids]]

Cela permet de mettre à jour le serveur et les poids séparément, de réutiliser un cache local et d'éviter de republier une image énorme. Épingler une révision ou une empreinte et vérifier l'intégrité au chargement. Un téléchargement au démarrage sans cache peut en revanche rallonger fortement le cold start.

---

Comment distinguer Apptainer, le runtime, et SIF, le format d'image ? <!--anki:77763777364e6b7a5674-->
?
- **Apptainer** : le runtime de conteneurs du **HPC** (ex-Singularity), sans démon et sans droits root ([[06-apptainer-singularity|Apptainer]])
- **SIF** : le format d'image d'Apptainer, un **fichier unique** et immuable

Le runtime lance les processus, tandis que SIF transporte leur environnement sous une forme facile à copier et vérifier. Un SIF est généralement utilisé en lecture seule ; les sorties peuvent aller dans des montages externes. Ne pas confondre image en lecture seule et impossibilité d'écrire sur l'hôte : les droits et montages de l'utilisateur restent déterminants.

---

## Mises en situation

Mise en situation : en entretien, on te demande de décrire ce qui se passe entre `kubectl apply` et un conteneur qui tourne sur un GPU. Que racontes-tu ? <!--anki:6936707d517d30363e60-->
?
1. **Côté control plane** : l'API server enregistre l'objet, le scheduler choisit un node qui satisfait les ressources demandées, dont `nvidia.com/gpu`
2. **Sur le node** : le kubelet reçoit le Pod et appelle le runtime par la **CRI**
3. **Chaîne d'exécution** : `containerd → runc → noyau Linux`, avec namespaces et cgroups
4. **GPU** : le NVIDIA Container Toolkit injecte devices et bibliothèques du driver de l'hôte
5. **Démarrage applicatif** : pull de l'image, chargement des poids, probes qui font passer le Pod prêt

**Piège** : sauter la CRI et parler de « Docker qui lance le conteneur » sur un cluster moderne.

---

Mise en situation : un nouvel arrivant confond OCI, CRI et SIF dans ses schémas d'architecture. Comment clarifies-tu en trois phrases ? <!--anki:687a5b75263a75293542-->
?
- **OCI** : les **standards** des conteneurs (image, runtime, distribution)
- **CRI** : l'**interface** entre le kubelet de Kubernetes et le runtime de conteneurs
- **SIF** : le **format d'image** d'Apptainer, utilisé en HPC

Repère utile : OCI dit à quoi ressemble une image, CRI dit comment Kubernetes demande son exécution, SIF est un format concurrent pour un autre contexte.

**Piège** : présenter CRI comme un format d'image, alors que c'est une API.

---

## Connexions
- [[00-index|Index Conteneurs (MOC)]] — carte complète du sujet
- [[01-oci|OCI]] — les standards d'image, de runtime et de distribution
- [[04-kubernetes-kubelet-cri|Kubernetes & CRI]] — le haut de la chaîne d'exécution
- [[00-moc-ai-engineering|MOC AI Engineering]]
