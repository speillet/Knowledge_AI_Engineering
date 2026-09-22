# Docker & Kubernetes — Flashcards
Tags: #flashcards #docker #kubernetes

Historiquement, comment Kubernetes communiquait-il avec Docker Engine ?
?
Via une couche appelée **dockershim**.

---

Pourquoi dockershim existait-il ?
?
Parce que Docker Engine n'exposait pas directement l'interface **CRI** attendue par Kubernetes.

---

Kubernetes utilise-t-il encore dockershim nativement ?
?
**Non.** dockershim a été retiré de Kubernetes.

---

Quelle architecture est aujourd'hui courante ?
?
`kubelet → CRI → containerd → runc`

---

Docker Engine est-il nécessaire pour exécuter dans Kubernetes une image construite avec Docker ?
?
**Non.** Une image compatible [[01-oci|OCI]] peut être exécutée via [[03-containerd-runc|containerd]] et un runtime OCI.

---

## Connexions
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — le contexte CRI
- [[03-containerd-runc|containerd & runc]] — le remplaçant de dockershim
- [[02-docker-images-registries|Docker & images]] — images OCI portables
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
