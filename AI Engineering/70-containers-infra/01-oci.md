# OCI — Flashcards
Tags: #flashcards #conteneurs #oci

Que signifie OCI ?
?
**Open Container Initiative.**

---

Quel est le rôle d'OCI ?
?
Définir des **standards ouverts pour les technologies de conteneurisation** afin de favoriser leur interopérabilité : une image OCI tourne aussi bien sur Docker, Podman, containerd que Kubernetes.

---

OCI est-il un logiciel ?
?
**Non.** OCI définit des spécifications et standards.

---

Quelles sont les trois grandes spécifications OCI ?
?
- OCI Image Specification
- OCI Runtime Specification
- OCI Distribution Specification

---

À quoi sert l'OCI Image Specification ?
?
À standardiser le **format et la structure des images de conteneurs**.

---

À quoi sert l'OCI Runtime Specification ?
?
À définir comment un conteneur doit être **créé et exécuté** par un [[03-containerd-runc|runtime OCI]] (ex. **runc**).

---

À quoi sert l'OCI Distribution Specification ?
?
À standardiser la **distribution des images**, notamment via les [[02-docker-images-registries|registries]].

---

## Connexions
- [[02-docker-images-registries|Docker, images & registries]] — implémentation concrète des standards
- [[03-containerd-runc|containerd & runc]] — runc applique l'OCI Runtime Spec
- [[08-linux-primitives-docker-fondamentaux|Primitives Linux]] — ce que le runtime configure (namespaces, cgroups)
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
