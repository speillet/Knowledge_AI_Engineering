# containerd & runc — Flashcards
Tags: #flashcards #conteneurs #containerd #runc

Qu'est-ce que containerd ?
?
Un **container runtime de haut niveau** qui gère notamment les images et le cycle de vie des conteneurs.

---

containerd et Docker sont-ils la même chose ?
?
**Non.** Docker fournit un écosystème plus large ; containerd est spécialisé dans la gestion/exécution des conteneurs.

---

Qu'est-ce que runc ?
?
Un **runtime OCI bas niveau** qui crée et exécute des conteneurs conformément à l'[[01-oci|OCI Runtime Specification]].

---

Quelle relation existe entre containerd et runc ?
?
Typiquement :

`containerd → runc → Linux kernel`

---

Quelle phrase permet de retenir la différence entre containerd et runc ?
?
**containerd gère ; runc exécute.**

---

## Connexions
- [[01-oci|OCI]] — runc implémente l'OCI Runtime Spec
- [[04-kubernetes-kubelet-cri|Kubernetes & CRI]] — containerd est appelé via CRI
- [[08-linux-primitives-docker-fondamentaux|Primitives Linux]] — runc configure namespaces & cgroups
- [[02-docker-images-registries|Docker & images]] — containerd gère les images
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
