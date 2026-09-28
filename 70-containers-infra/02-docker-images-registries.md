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
Qu'une technologie parle les mêmes **formats et protocoles** : elle sait lire une **image OCI**, dialoguer avec un **registry** selon la spec de distribution, et exécuter un **bundle** conforme à la spec runtime. C'est ce qui permet de remplacer un composant sans toucher aux autres ([[01-oci|OCI]]).

---

Quels ordres de grandeur pour la taille des images ?
?
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

Quelle est la différence entre une image et un conteneur ?
?
Une **image** est un package/template contenant l'application et son environnement.

Un **conteneur** est une instance exécutée à partir de cette image.

---

Une même image peut-elle créer plusieurs conteneurs ?
?
**Oui**, autant qu'on veut. Les couches de l'image sont en **lecture seule et partagées** ; chaque conteneur n'ajoute qu'une **couche inscriptible** par-dessus. Dix conteneurs de la même image ne dupliquent donc **pas** ses couches sur le disque, et démarrent en quelques centaines de millisecondes.

---

Qu'est-ce qu'un container registry ?
?
Un service qui **stocke et distribue des images**, selon l'API de l'[[01-oci|OCI Distribution Specification]] : il conserve les **manifests** et les **couches**, adressées par digest, et les sert sur pull. Exemples : Docker Hub, GitHub Container Registry, Harbor, Amazon ECR, Google Artifact Registry.

En entreprise, il porte aussi le **contrôle d'accès**, l'**analyse de vulnérabilités**, la **signature** et la rétention. C'est un composant critique : si le registry est indisponible, plus aucun Pod ne démarre sur une image non déjà présente sur le node.

---

Quel workflow utilise typiquement un registry ?
?
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
**Non**, c'est un **registry** : il stocke et distribue des images, il n'en exécute aucune. L'exécution revient à [[03-containerd-runc|containerd et runc]].

En pratique, deux conséquences : Docker Hub applique des **limites de pull** aux comptes anonymes, et ses images publiques ne sont pas auditées. D'où l'usage d'un **registry interne** ou d'un miroir en CI et sur les nodes.

---

À ne pas confondre : tag et digest ?
?
- **Tag** (`app:1.2.0`, `app:latest`) : une **étiquette mutable**. Elle peut être **réécrite** et pointer demain vers une autre image
- **Digest** (`app@sha256:9f2c…`) : l'**empreinte du contenu**, donc **immuable** et vérifiable

En production, on **épingle le digest** : c'est ce qui garantit que le déploiement d'aujourd'hui exécute exactement ce qui a été testé hier.

---

## Mises en situation

Mise en situation : le déploiement de ton serveur d'inférence prend 20 minutes, dont 18 de pull d'image, parce que les poids du modèle sont dans l'image. Que changes-tu ?
?
1. **Sortir les poids de l'image** : image légère avec le runtime, poids montés depuis un volume ou un stockage objet ([[10-images-modeles-poids|images & poids]])
2. **Pré-puller** l'image sur les nodes GPU, avec un DaemonSet
3. **Optimiser les couches** : dépendances stables en bas, code applicatif en haut, pour maximiser le cache
4. **Registry proche** : miroir interne ou cache régional, plutôt qu'un pull depuis l'extérieur
5. **Épingler par digest** plutôt que par tag mouvant

**Piège** : reconstruire l'image entière à chaque changement de version de modèle.

---

Mise en situation : une équipe pousse ses images sur Docker Hub avec le tag `latest`, et la production redémarre parfois avec une version inattendue. Que mets-tu en place ?
?
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
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
