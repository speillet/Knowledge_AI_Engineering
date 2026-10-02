# Docker, images et registries — Flashcards
Tags: #flashcards #conteneurs #docker
<!-- summary: rôle de Docker et différence avec OCI, image ou conteneur (instance, état, volumes), compatibilité « Docker/OCI », registries et workflow push/pull. -->

Docker et OCI sont-ils la même chose ?
?
<!--anki:473c39416b3845714e37-->
**Non.** Docker est un écosystème/outillage de conteneurisation, l'outil de référence en développement : il **construit** les images (`Dockerfile`, `docker build`), les **distribue** (push/pull vers un registry) et les **exécute** (via [[03-containerd-runc|containerd et runc]]). [[01-oci|OCI]] définit des standards ouverts.

---

Une image construite avec Docker peut-elle être utilisée sans Docker Engine ?
?
<!--anki:4c543262645e38635a65-->
**Oui.** Une image compatible OCI peut être utilisée par d'autres technologies compatibles.

---

Que signifie « Docker/OCI compatible » ?
?
<!--anki:494f576456637d502555-->
Qu'une technologie parle les mêmes **formats et protocoles** : elle sait lire une **image OCI**, dialoguer avec un **registry** selon la spec de distribution, et exécuter un **bundle** conforme à la spec runtime. C'est ce qui permet de remplacer un composant sans toucher aux autres ([[01-oci|OCI]]).

---

Quels ordres de grandeur pour la taille des images ?
?
<!--anki:482a30374c4f77287a3f-->
```text
alpine                  ~  8 Mo
debian-slim             ~ 75 Mo
python:3.x-slim         ~130 Mo
image CUDA runtime      ~2 à 3 Go
serveur d'inférence LLM ~8 à 12 Go
poids d'un modèle 8B    ~16 Go   ← à garder hors de l'image
```
Retenir l'ordre de grandeur : une image applicative se compte en **centaines de Mo**, une image GPU en **Go**, et les **poids** ne doivent pas y entrer ([[10-images-modeles-poids|poids de modèles]]).

---

À ne pas confondre : image et conteneur ?
?
<!--anki:676649472e342573532b-->
- **Image** : un **modèle immuable**, en couches, qui contient l'application et son environnement. Elle se stocke et se partage dans un registry
- **Conteneur** : une **instance en cours d'exécution** d'une image, avec son propre état modifiable, ses processus et son réseau

Une image donne autant de conteneurs qu'on veut, comme une classe donne des objets. Ce qu'un conteneur écrit disparaît avec lui, sauf dans un **volume**.

---

Une même image peut-elle créer plusieurs conteneurs ?
?
<!--anki:654344583059492e3349-->
**Oui**, autant qu'on veut. Les couches de l'image sont en **lecture seule et partagées** ; chaque conteneur n'ajoute qu'une **couche inscriptible** par-dessus. Dix conteneurs de la même image ne dupliquent donc **pas** ses couches sur le disque, et démarrent en quelques centaines de millisecondes.

---

Qu'est-ce qu'un container registry ?
?
<!--anki:4b706936536a6b482f4e-->
Un service qui **stocke et distribue des images**, selon l'API de l'[[01-oci|OCI Distribution Specification]] : il conserve les **manifests** et les **couches**, adressées par digest, et les sert sur pull. Exemples : Docker Hub, GitHub Container Registry, Harbor, Amazon ECR, Google Artifact Registry.

En entreprise, il porte aussi le **contrôle d'accès**, l'**analyse de vulnérabilités**, la **signature** et la rétention. C'est un composant critique : si le registry est indisponible, plus aucun Pod ne démarre sur une image non déjà présente sur le node.

---

Quel workflow utilise typiquement un registry ?
?
<!--anki:42337a5b48555930447d-->
`build → image → push → registry → pull → runtime`
```bash
docker build -t registry.interne/app:1.2.0 .
docker push registry.interne/app:1.2.0
docker pull registry.interne/app@sha256:9f2c…   # par digest : immuable
```
En production, on déploie par **digest** et non par tag ([[112-cicd-modeles|CI/CD]]).

---

Docker Hub est-il un runtime ?
?
<!--anki:715d2f71583467563355-->
**Non**, c'est un **registry** : il stocke et distribue des images, il n'en exécute aucune. L'exécution revient à [[03-containerd-runc|containerd et runc]].

En pratique, deux conséquences : Docker Hub applique des **limites de pull** aux comptes anonymes, et ses images publiques ne sont pas auditées. D'où l'usage d'un **registry interne** ou d'un miroir en CI et sur les nodes.

---

À ne pas confondre : tag et digest ?
?
<!--anki:72692e4142293e5a457b-->
- **Tag** (`app:1.2.0`, `app:latest`) : une **étiquette mutable**. Elle peut être **réécrite** et pointer demain vers une autre image
- **Digest** (`app@sha256:9f2c…`) : l'**empreinte du contenu**, donc **immuable** et vérifiable

En production, on **épingle le digest** : c'est ce qui garantit que le déploiement d'aujourd'hui exécute exactement ce qui a été testé hier.

---

## Mises en situation

Mise en situation : le déploiement de ton serveur d'inférence prend 20 minutes, dont 18 de pull d'image, parce que les poids du modèle sont dans l'image. Que changes-tu ?
?
<!--anki:794e496a3e5e64635b5a-->
1. **Sortir les poids de l'image** : image légère avec le runtime, poids montés depuis un volume ou un stockage objet ([[10-images-modeles-poids|images & poids]])
2. **Pré-puller** l'image sur les nodes GPU, avec un DaemonSet
3. **Optimiser les couches** : dépendances stables en bas, code applicatif en haut, pour maximiser le cache
4. **Registry proche** : miroir interne ou cache régional, plutôt qu'un pull depuis l'extérieur
5. **Épingler par digest** plutôt que par tag mouvant

**Piège** : reconstruire l'image entière à chaque changement de version de modèle.

---

Mise en situation : une équipe pousse ses images sur Docker Hub avec le tag `latest`, et la production redémarre parfois avec une version inattendue. Que mets-tu en place ?
?
<!--anki:76772d7e25723a7b5829-->
1. **Interdire `latest`** en production : chaque déploiement référence un **digest** ou une version immuable
2. **Registry interne** : contrôle d'accès, rétention, analyse de vulnérabilités
3. **Traçabilité** : quelle image tourne, construite depuis quel commit
4. **Signature** des images et vérification à l'admission
5. **Nettoyage** : politique de rétention, sinon le registry devient ingérable

**Piège** : croire qu'un tag est immuable. Il peut être réécrit à tout moment.

---

## Connexions
- [[01-oci|OCI]] — les standards derrière Docker
- [[03-containerd-runc|containerd & runc]] — ce qui exécute les images
- [[08-linux-primitives-docker-fondamentaux|Primitives & fondamentaux]] — layers, volumes, Dockerfile
- [[10-images-modeles-poids|Images & poids de modèles]] — cas des gros modèles LLM
- [[05-docker-kubernetes|Docker & Kubernetes]] — pourquoi Kubernetes n'a plus besoin de Docker Engine
- [[06-apptainer-singularity|Apptainer & Singularity]] — les conteneurs du monde HPC
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
