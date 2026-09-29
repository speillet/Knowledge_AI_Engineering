# OCI — Flashcards
Tags: #flashcards #conteneurs #oci

Que signifie OCI ?
?
**Open Container Initiative** : un projet de la **Linux Foundation**, lancé en 2015 à l'initiative de Docker, pour éviter que chaque éditeur impose son propre format de conteneur.

---

Quel est le rôle d'OCI ?
?
Définir des **standards ouverts pour les technologies de conteneurisation** afin de favoriser leur interopérabilité : une image OCI tourne aussi bien sur Docker, Podman, containerd que Kubernetes.

---

OCI est-il un logiciel ?
?
**Non**, c'est un **organisme de normalisation** : il publie des **spécifications**, c'est-à-dire des documents. Les logiciels les **implémentent** : [[03-containerd-runc|runc]] pour le runtime (donné par Docker comme implémentation de référence), containerd, Podman, CRI-O.

---

Quelles sont les trois grandes spécifications OCI ?
?
- OCI Image Specification
- OCI Runtime Specification
- OCI Distribution Specification

---

À quoi sert l'OCI Image Specification ?
?
À standardiser le **format et la structure des images**. Concrètement, une image est un ensemble de fichiers reliés par des empreintes **sha256** :
```text
manifest    → liste les couches et pointe vers la config
config      → entrypoint, variables d'env, architecture, OS
couches     → archives tar compressées du système de fichiers
```
Chaque élément est identifié par son **digest**, ce qui rend l'image **vérifiable** et **déduplicable** ([[08-linux-primitives-docker-fondamentaux|layers]]).

---

À quoi sert l'OCI Runtime Specification ?
?
À définir comment un conteneur est **créé et exécuté** par un [[03-containerd-runc|runtime OCI]] comme **runc** : un **bundle** (système de fichiers extrait + fichier `config.json`) et un **cycle de vie** normalisé (`create`, `start`, `kill`, `delete`). Le `config.json` décrit les **namespaces**, les **cgroups**, les montages et les capabilities à appliquer ([[08-linux-primitives-docker-fondamentaux|primitives Linux]]).

---

À quoi sert l'OCI Distribution Specification ?
?
À standardiser la **distribution des images** : une API HTTP (`/v2/…`) pour pousser et récupérer manifests et couches, par **tag** ou par **digest**. C'est elle qui rend les [[02-docker-images-registries|registries]] interchangeables, et elle sert aujourd'hui à distribuer bien plus que des images : charts Helm, politiques, et même des **poids de modèles** comme artefacts OCI ([[10-images-modeles-poids|poids de modèles]]).

---

À ne pas confondre : Dockerfile et image OCI ?
?
- **Dockerfile** : la **recette de construction**, un fichier texte propre à l'outillage Docker et BuildKit. Il ne fait **pas** partie des spécifications OCI
- **Image OCI** : le **résultat** de la construction, au format normalisé (manifest, config, couches)

D'où le fait qu'on puisse produire une image OCI **sans Dockerfile** (Buildpacks, Bazel, Nix, `apptainer build`) et l'exécuter partout.

---

## Mises en situation

Mise en situation : un client impose Podman, alors que vos images de serveurs d'inférence sont construites avec Docker. Faut-il tout refaire ?
?
1. **Non** : une image conforme à l'**OCI Image Specification** s'exécute sur Docker, Podman, containerd ou Kubernetes
2. **Vérifier la distribution** : le registry doit parler l'**OCI Distribution Specification**, ce qui est le cas des registries courants
3. **Vérifier le runtime** : Podman utilise un runtime conforme à l'**OCI Runtime Specification** (crun ou runc)
4. **Tester quand même** : options spécifiques à Docker dans les scripts, mode rootless, accès GPU ([[09-gpu-conteneurs|GPU]])
5. **Garder la construction reproductible** : mêmes digests d'images, pas de `latest`

**Piège** : confondre le **format** (standardisé) et l'**outillage** (spécifique), et croire qu'une image est liée à Docker.

---

Mise en situation : un audit demande de prouver que vos conteneurs de production reposent sur des standards ouverts et non sur un seul fournisseur. Que présentes-tu ?
?
1. **Les trois spécifications OCI** : image, runtime, distribution, et ce que chacune couvre
2. **La chaîne réelle** : registry conforme, containerd via la CRI, runc conforme à la spec runtime
3. **La preuve de portabilité** : la même image exécutée sur un autre runtime, en test
4. **Les artefacts** : digests épinglés, signatures, provenance ([[105-devsecops-ia-agentique|chaîne d'approvisionnement]])
5. **La limite honnête** : le standard porte sur les conteneurs, pas sur l'orchestrateur ni sur les services managés

**Piège** : présenter OCI comme un logiciel, alors que c'est un ensemble de spécifications.

---

## Connexions
- [[02-docker-images-registries|Docker, images & registries]] — implémentation concrète des standards
- [[03-containerd-runc|containerd & runc]] — runc applique l'OCI Runtime Spec
- [[08-linux-primitives-docker-fondamentaux|Primitives Linux]] — ce que le runtime configure (namespaces, cgroups)
- [[07-synthese-containers|Synthèse conteneurs]] — les chaînes à savoir reconstruire
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
