# containerd & runc — Flashcards
Tags: #flashcards #conteneurs #containerd #runc
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: rôle de containerd, rôle de runc, relation entre les deux, containerd ou CRI-O, crun, RuntimeClass, outils `ctr`, `nerdctl` et `crictl`, place du GPU dans la chaîne. -->


Qu'est-ce que containerd ? <!--anki:482f38677a352a716331-->
?
Un **container runtime de haut niveau** (projet CNCF diplômé) qui gère : le **pull et le stockage des images**, les **snapshots** du système de fichiers, le **cycle de vie** des conteneurs, le réseau via des plugins. Il expose une API gRPC, utilisée par Docker comme par Kubernetes à travers la [[04-kubernetes-kubelet-cri|CRI]].

---

containerd et Docker sont-ils la même chose ? <!--anki:77337a5b6e5556322929-->
?
**Non.** Docker est une **suite d'outils** : CLI, construction d'images (BuildKit), réseau, Compose, Desktop. Sous le capot, Docker **délègue** l'exécution à containerd. Historiquement, containerd a d'ailleurs été **extrait de Docker** puis donné à la CNCF : on peut donc utiliser containerd **sans** Docker, ce que fait Kubernetes ([[05-docker-kubernetes|dockershim]]).

---

Qu'est-ce que runc ? <!--anki:702e5e602d5751585a4f-->
?
Un **runtime OCI bas niveau** : un binaire qui reçoit un **bundle** (système de fichiers + `config.json`) et demande au noyau de créer le conteneur, conformément à l'[[01-oci|OCI Runtime Specification]]. Il configure **namespaces, cgroups, capabilities, seccomp**, lance le premier processus… puis **se retire** : ce n'est pas un démon.

---

Quelle relation existe entre containerd et runc ? <!--anki:6579234d4f604d777d24-->
?
`containerd → shim → runc → Linux kernel`

containerd lance un **shim** par conteneur, qui appelle **runc** pour la création puis reste le **processus parent** du conteneur. C'est ce qui permet de **redémarrer containerd sans tuer les conteneurs** en cours.
```bash
ctr -n k8s.io containers list   # côté containerd
crictl ps                       # ce que voit le kubelet via la CRI
```

---

Quelle phrase permet de retenir la différence entre containerd et runc ? <!--anki:6d7c4b326064574e6644-->
?
**containerd gère ; runc exécute.**

Corollaire utile : on remplace **runc** pour changer d'isolation (gVisor, Kata Containers via une RuntimeClass), et on garde containerd. C'est ainsi qu'on durcit l'exécution du code généré par un agent ([[103-defenses-agents|isolation]]).

---

À ne pas confondre : containerd et CRI-O ? <!--anki:677a31493c373b323f5e-->
?
Deux **runtimes de haut niveau** qui implémentent la [[04-kubernetes-kubelet-cri|CRI]] et délèguent l'exécution à un runtime OCI (runc ou crun) :
- **containerd** : généraliste, utilisé par Docker **et** par Kubernetes, défaut de la plupart des distributions managées (EKS, GKE, AKS)
- **CRI-O** : conçu **uniquement pour Kubernetes**, sans fonctions superflues, défaut d'**OpenShift**

Pour une image et un Pod, le résultat est le même : c'est la standardisation [[01-oci|OCI]] qui le garantit.

---

Qu'est-ce que crun ? <!--anki:736d6a51574d495f543d-->
?
Un **runtime OCI bas niveau écrit en C**, alternative à runc (écrit en Go) : même rôle, même `config.json`, mais **démarrage plus rapide** et empreinte mémoire plus faible. Il est le défaut de **Podman** sur Fedora et RHEL. Il illustre l'intérêt de la spec OCI : on remplace le runtime sans changer ni les images ni containerd.

---

Comment déclarer un runtime alternatif avec une RuntimeClass ? <!--anki:4a66603832787c366435-->
?
La RuntimeClass associe un **nom** à un **handler** configuré dans containerd ; le Pod le choisit par `runtimeClassName`.
```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc            # runtime déclaré dans la config de containerd
---
apiVersion: v1
kind: Pod
metadata:
  name: code-agent
spec:
  runtimeClassName: gvisor
  containers:
    - name: sandbox
      image: registry.example.com/agent-sandbox:1.4
```
Seuls les Pods qui le demandent paient le surcoût de l'isolation renforcée ([[106-securite-agents-code|agents de code]]).

---

À ne pas confondre : ctr, nerdctl et crictl ? <!--anki:475279656c3947717c78-->
?
- **`ctr`** : client **bas niveau** livré avec containerd, pour le débogage. Attention aux **namespaces** containerd (`-n k8s.io` pour voir les conteneurs de Kubernetes)
- **`nerdctl`** : client **compatible avec la syntaxe Docker** (`nerdctl run`, `nerdctl build`), sans Docker Engine
- **`crictl`** : parle à containerd **via la CRI**, et montre donc ce que voit le **kubelet** (Pods, conteneurs, logs)

Sur un node Kubernetes, `crictl` est le réflexe de diagnostic.

---

Où le GPU entre-t-il dans la chaîne containerd → runc ? <!--anki:49616e4d622f4e78292d-->
?
Juste **avant runc** : le NVIDIA Container Toolkit **modifie la spécification OCI** du conteneur (par un hook ou par **CDI**, Container Device Interface) pour y ajouter les devices `/dev/nvidia*` et les bibliothèques du driver. runc crée ensuite le conteneur comme d'habitude, sans rien savoir du GPU ([[09-gpu-conteneurs|GPU & conteneurs]]).

---

## Mises en situation

Mise en situation : tu veux exécuter du code généré par un agent avec une isolation plus forte que le conteneur classique. Où intervient le runtime ? <!--anki:6a563a3e753231586361-->
?
1. **Comprendre la chaîne** : containerd gère, **runc exécute** avec les primitives du noyau, noyau partagé avec l'hôte
2. **Remplacer le runtime bas niveau** : gVisor ou Kata Containers s'utilisent à la place de runc, avec une isolation plus forte
3. **Déclarer** ce runtime alternatif, par exemple via une RuntimeClass dans Kubernetes
4. **Accepter le compromis** : démarrage plus lent et léger surcoût, contre un noyau isolé
5. **Compléter** : réseau sortant filtré, secrets hors du conteneur ([[103-defenses-agents|défenses]])

**Piège** : croire qu'un conteneur standard suffit à exécuter du code non fiable.

---

Mise en situation : un incident mentionne « containerd ne répond plus » et l'équipe se demande si Docker est en cause. Comment expliques-tu l'architecture ? <!--anki:682e51314d5e5669475f-->
?
1. **Séparer les rôles** : Docker est un outillage complet, containerd le runtime de haut niveau, runc le runtime bas niveau
2. **Rappeler la chaîne** : `containerd → runc → noyau Linux`, et dans Kubernetes le kubelet appelle containerd via la **CRI**
3. **En conséquence** : un cluster Kubernetes moderne n'a pas besoin de Docker Engine ([[05-docker-kubernetes|dockershim]])
4. **Diagnostiquer au bon niveau** : conteneurs qui ne démarrent plus, images qui ne se pullent plus, ou processus qui ne s'exécutent plus
5. **Retenir la formule** : **containerd gère, runc exécute**

**Piège** : chercher un démon Docker sur un node qui n'en a pas.

---

## Sources

- [containerd — documentation du projet et architecture](https://github.com/containerd/containerd)

## Connexions
- [[01-oci|OCI]] — runc implémente l'OCI Runtime Spec
- [[04-kubernetes-kubelet-cri|Kubernetes & CRI]] — containerd est appelé via CRI
- [[08-linux-primitives-docker-fondamentaux|Primitives Linux]] — runc configure namespaces & cgroups
- [[02-docker-images-registries|Docker & images]] — containerd gère les images
- [[49-agents-de-code|Agents de code]] — utiliser et intégrer les agents de code
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
