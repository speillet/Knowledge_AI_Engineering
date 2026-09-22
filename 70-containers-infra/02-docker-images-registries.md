# Docker, images et registries — Flashcards
Tags: #flashcards #conteneurs #docker

Docker et OCI sont-ils la même chose ?
?
**Non.** Docker est un écosystème/outillage de conteneurisation, l'outil de référence en développement : il **construit** les images (`Dockerfile`, `docker build`), les **distribue** (push/pull vers un registry) et les **exécute** (via [[03-containerd-runc|containerd et runc]]). [[01-oci|OCI]] définit des standards ouverts.

---

Une image construite avec Docker peut-elle être utilisée sans Docker Engine ?
?
**Oui.** Une image compatible OCI peut être utilisée par d'autres technologies compatibles.

---

Que signifie « Docker/OCI compatible » ?
?
Qu'une technologie peut interagir avec les formats et standards de l'écosystème OCI/Docker.

---

Quelle est la différence entre une image et un conteneur ?
?
Une **image** est un package/template contenant l'application et son environnement.

Un **conteneur** est une instance exécutée à partir de cette image.

---

Une même image peut-elle créer plusieurs conteneurs ?
?
**Oui.**

---

Qu'est-ce qu'un container registry ?
?
Un service permettant de **stocker et distribuer des images de conteneurs**.

---

Quel workflow utilise typiquement un registry ?
?
`build → image → push → registry → pull → runtime`

---

Docker Hub est-il un runtime ?
?
**Non.** Docker Hub est principalement un **registry d'images**.

---

## Connexions
- [[01-oci|OCI]] — les standards derrière Docker
- [[03-containerd-runc|containerd & runc]] — ce qui exécute les images
- [[08-linux-primitives-docker-fondamentaux|Primitives & fondamentaux]] — layers, volumes, Dockerfile
- [[10-images-modeles-poids|Images & poids de modèles]] — cas des gros modèles LLM
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
