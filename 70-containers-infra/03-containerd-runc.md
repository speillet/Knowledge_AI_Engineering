# containerd & runc — Flashcards
Tags: #flashcards #conteneurs #containerd #runc

Qu'est-ce que containerd ?
?
Un **container runtime de haut niveau** (projet CNCF diplômé) qui gère : le **pull et le stockage des images**, les **snapshots** du système de fichiers, le **cycle de vie** des conteneurs, le réseau via des plugins. Il expose une API gRPC, utilisée par Docker comme par Kubernetes à travers la [[04-kubernetes-kubelet-cri|CRI]].

---

containerd et Docker sont-ils la même chose ?
?
**Non.** Docker est une **suite d'outils** : CLI, construction d'images (BuildKit), réseau, Compose, Desktop. Sous le capot, Docker **délègue** l'exécution à containerd. Historiquement, containerd a d'ailleurs été **extrait de Docker** puis donné à la CNCF : on peut donc utiliser containerd **sans** Docker, ce que fait Kubernetes ([[05-docker-kubernetes|dockershim]]).

---

Qu'est-ce que runc ?
?
Un **runtime OCI bas niveau** : un binaire qui reçoit un **bundle** (système de fichiers + `config.json`) et demande au noyau de créer le conteneur, conformément à l'[[01-oci|OCI Runtime Specification]]. Il configure **namespaces, cgroups, capabilities, seccomp**, lance le premier processus… puis **se retire** : ce n'est pas un démon.

---

Quelle relation existe entre containerd et runc ?
?
`containerd → shim → runc → Linux kernel`

containerd lance un **shim** par conteneur, qui appelle **runc** pour la création puis reste le **processus parent** du conteneur. C'est ce qui permet de **redémarrer containerd sans tuer les conteneurs** en cours.
```bash
ctr -n k8s.io containers list   # côté containerd
crictl ps                       # ce que voit le kubelet via la CRI
```

---

Quelle phrase permet de retenir la différence entre containerd et runc ?
?
**containerd gère ; runc exécute.**

Corollaire utile : on remplace **runc** pour changer d'isolation (gVisor, Kata Containers via une RuntimeClass), et on garde containerd. C'est ainsi qu'on durcit l'exécution du code généré par un agent ([[103-defenses-agents|isolation]]).

---

## Mises en situation

Mise en situation : tu veux exécuter du code généré par un agent avec une isolation plus forte que le conteneur classique. Où intervient le runtime ?
?
1. **Comprendre la chaîne** : containerd gère, **runc exécute** avec les primitives du noyau, noyau partagé avec l'hôte
2. **Remplacer le runtime bas niveau** : gVisor ou Kata Containers s'utilisent à la place de runc, avec une isolation plus forte
3. **Déclarer** ce runtime alternatif, par exemple via une RuntimeClass dans Kubernetes
4. **Accepter le compromis** : démarrage plus lent et léger surcoût, contre un noyau isolé
5. **Compléter** : réseau sortant filtré, secrets hors du conteneur ([[103-defenses-agents|défenses]])

**Piège** : croire qu'un conteneur standard suffit à exécuter du code non fiable.

---

Mise en situation : un incident mentionne « containerd ne répond plus » et l'équipe se demande si Docker est en cause. Comment expliques-tu l'architecture ?
?
1. **Séparer les rôles** : Docker est un outillage complet, containerd le runtime de haut niveau, runc le runtime bas niveau
2. **Rappeler la chaîne** : `containerd → runc → noyau Linux`, et dans Kubernetes le kubelet appelle containerd via la **CRI**
3. **En conséquence** : un cluster Kubernetes moderne n'a pas besoin de Docker Engine ([[05-docker-kubernetes|dockershim]])
4. **Diagnostiquer au bon niveau** : conteneurs qui ne démarrent plus, images qui ne se pullent plus, ou processus qui ne s'exécutent plus
5. **Retenir la formule** : **containerd gère, runc exécute**

**Piège** : chercher un démon Docker sur un node qui n'en a pas.

---

## Connexions
- [[01-oci|OCI]] — runc implémente l'OCI Runtime Spec
- [[04-kubernetes-kubelet-cri|Kubernetes & CRI]] — containerd est appelé via CRI
- [[08-linux-primitives-docker-fondamentaux|Primitives Linux]] — runc configure namespaces & cgroups
- [[02-docker-images-registries|Docker & images]] — containerd gère les images
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
