# Docker & Kubernetes — Flashcards
Tags: #flashcards #docker #kubernetes
Vérifié le : 29 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: dockershim et sa suppression, architecture actuelle, images Docker exécutées sans Docker Engine, cri-dockerd, vérifications avant de retirer Docker Engine, construction d'images sans démon (BuildKit rootless, Buildah), validation des conditions d'exécution Kubernetes, UID et permissions, dérive des configurations. -->


Historiquement, comment Kubernetes communiquait-il avec Docker Engine ? <!--anki:41645a73796a5a6f502a-->
?
Par **dockershim**, un adaptateur intégré au kubelet qui traduisait la [[04-kubernetes-kubelet-cri|CRI]] vers l'API Docker Engine : `kubelet → dockershim → Docker Engine → containerd → runc`.

Cette adaptation était nécessaire parce que Docker Engine n'implémentait pas directement la CRI. Retirer ce maillon intégré ne signifie pas retirer la compatibilité des images construites avec Docker : un runtime CRI compatible peut les utiliser.

Exemple : migrer un node vers containerd change la couche d'exécution et ses outils de diagnostic, pas nécessairement les Dockerfiles des applications. Vérifier toutefois les dépendances au socket Docker, aux chemins de logs et à la configuration runtime.

---

Pourquoi dockershim existait-il ? <!--anki:746b7c73773064733f75-->
?
Parce que Docker Engine, antérieur à Kubernetes, n'expose pas l'interface **CRI**. Quand la CRI est apparue (pour ouvrir Kubernetes à plusieurs runtimes), il fallait bien continuer à faire fonctionner les clusters existants, tous basés sur Docker.

Dockershim traduisait les demandes du kubelet vers Docker Engine. Cet adaptateur concernait le **pilotage de l'exécution**, pas le format des images. Sa présence ajoutait une couche à maintenir entre Kubernetes et le runtime sous-jacent.

---

Kubernetes utilise-t-il encore dockershim nativement ? <!--anki:4d476c304a577c7d336d-->
?
**Non**, il a été retiré dans la **version 1.24** (2022). Les clusters parlent désormais directement à un runtime compatible CRI. Ce qui a disparu, c'est **le raccourci vers Docker Engine**, pas la compatibilité avec les images Docker.

Lors d'une migration, rechercher surtout les dépendances au socket Docker, aux chemins de logs et aux outils d'exploitation. Une image applicative standard peut rester identique, tandis qu'un agent qui monte `/var/run/docker.sock` nécessite une adaptation.

---

Sans dockershim, quelle chaîne d'exécution est aujourd'hui courante sur un node Kubernetes ? <!--anki:464d5d4f407e2a234050-->
?
`kubelet → CRI → containerd (ou CRI-O) → runc → noyau Linux`

Conséquence pratique : sur un node, on débogue avec **`crictl`** et non `docker ps`, et il n'y a **pas de démon Docker** à interroger.

Pour savoir ce qui tourne réellement, `kubectl get nodes -o wide` affiche dans la colonne `CONTAINER-RUNTIME` le runtime de chaque nœud et sa version, comme `containerd://…` ou `cri-o://…`. Les journaux se lisent avec `crictl logs` ou dans `/var/log/pods/`, et non plus avec `docker logs`.

---

À ne pas confondre : « Kubernetes ne supporte plus Docker » et « les images Docker ne marchent plus » ? <!--anki:6b3f563246555e212c79-->
?
- Ce qui a été retiré : **dockershim**, donc le support de **Docker Engine comme runtime** de node
- Ce qui n'a jamais changé : les **images**, conformes à l'[[01-oci|OCI]], s'exécutent parfaitement via containerd

C'est la confusion la plus fréquente sur le sujet : elle porte sur le **runtime**, pas sur le **format d'image**.

Docker Engine reste utilisable avec un adaptateur CRI externe approprié. Vérifier architecture, système et accès GPU avant de promettre qu'une image fonctionne : compatibilité du format ne signifie pas compatibilité avec toute machine ou configuration.

---

Qu'est-ce que cri-dockerd ? <!--anki:45314f337346634d2a34-->
?
**cri-dockerd** est un adaptateur externe qui traduit les demandes CRI de Kubernetes vers Docker Engine. Il permet de continuer à utiliser ce moteur après le retrait du dockershim intégré à Kubernetes.

Cette option peut répondre à une dépendance existante ; elle ajoute un composant à configurer et maintenir. Comparer avec containerd ou une autre implémentation CRI selon support, exploitation et besoin réel. Un outil qui utilise le socket Docker ne fonctionne pas automatiquement dans tous les environnements Kubernetes. Le choix du runtime n'impose pas de reconstruire une image compatible OCI, mais les contraintes de plateforme et dépendances externes restent à tester.

---

Que vérifier avant de retirer Docker Engine des nodes d'un cluster ? <!--anki:4c7424507a3764573976-->
?
Tout ce qui dépend **du démon Docker** plutôt que de Kubernetes :
- **Montages de `/var/run/docker.sock`** : agents de monitoring, collecteurs de logs, jobs de CI qui construisent des images
- **Outils qui lisent les logs** au format `json-file` de Docker, alors que la CRI écrit dans son propre format
- **Scripts d'exploitation** qui appellent `docker ps` sur les nodes, à remplacer par `crictl`

Les **images**, elles, ne changent pas ([[03-containerd-runc|outils containerd]]).

---

Comment construire des images dans un cluster sans Docker Engine ? <!--anki:4a432a255d78575b7b42-->
?
Avec un constructeur qui **n'a pas besoin du démon Docker** ni du socket du node :
- **BuildKit** en mode **rootless**, en Pod ou en service partagé
- **Buildah**, sans démon, courant dans l'écosystème Red Hat

Tous produisent des **images OCI** standard, poussées dans le registry comme avant ([[02-docker-images-registries|registries]]). On évite ainsi de monter `docker.sock`, qui donne en pratique un accès root au node.

---

Pourquoi un test Docker local ne suffit-il pas à valider un déploiement Kubernetes ? <!--anki:3361376364343835653661643437306539636330343432366538643933663831-->
?
Le **contexte d'exécution** change : identité, système de fichiers, réseau, ressources et cycle de vie. Un conteneur local lancé avec tous les privilèges peut échouer dans un Pod restreint.

Rejouer les conditions prévues : utilisateur non privilégié, volumes et droits réels, limites mémoire, secrets injectés et arrêt gracieux. Tester téléchargement des poids et accès GPU sur le cluster cible. Vérifier enfin Service et probes. Une image commune facilite le transfert, mais ne reproduit pas automatiquement les contrats que Kubernetes impose autour du processus.

---

Pourquoi un conteneur qui fonctionne en root localement peut-il échouer sous Kubernetes avec un utilisateur non privilégié ? <!--anki:3761323631653039303330313437393762356238336235616636373339643761-->
?
L'application peut essayer d'écrire dans **un répertoire appartenant à root**, d'accéder à un périphérique ou d'utiliser une capacité non accordée.

Tester le même UID, les mêmes montages et restrictions avant déploiement. Préparer explicitement les répertoires inscriptibles nécessaires. Rétablir root pour « réparer » le démarrage peut dissimuler une dépendance évitable ; corriger les permissions au périmètre utile.

---

Pourquoi conserver les manifests Kubernetes en plus du Dockerfile pour reproduire un service ? <!--anki:3430373035333938303961353436376662353338623261323364346531336638-->
?
Le Dockerfile ne décrit pas **les secrets injectés, ressources, montages, probes et règles réseau** du déploiement. Ces paramètres peuvent changer le comportement sans modifier l'image.

Versionner les manifests et références de configuration, puis vérifier l'état effectif du cluster. Conserver les valeurs sensibles dans un mécanisme adapté plutôt que dans Git. Une différence entre configuration déclarée et configuration appliquée doit être détectable.

---

## Mises en situation

Mise en situation : un développeur affirme qu'il faut réécrire les images en « format Kubernetes », puisque Docker n'est plus supporté. Que réponds-tu ? <!--anki:7454446b3b373b56544b-->
?
1. **Distinguer** : ce qui a été retiré, c'est **dockershim**, la couche qui permettait au kubelet de piloter Docker Engine
2. **Rappeler l'architecture actuelle** : `kubelet → CRI → containerd → runc`
3. **Conclure** : les images restent des **images OCI**, construites avec Docker ou autre chose, et tournent sans Docker Engine
4. **Ce qui change réellement** : les commandes de débogage sur les nodes, et les outils qui parlaient au démon Docker
5. **Ce qu'il faut vérifier** : pas d'usage du socket Docker dans les Pods, pratique à bannir de toute façon

**Piège** : confondre le format d'image et le runtime qui l'exécute.

---

Mise en situation : un job de CI construit des images en montant le socket Docker du node dans un Pod. Quels risques et quelles alternatives ? <!--anki:456a383b786342397943-->
?
1. **Risque majeur** : accéder au socket du node revient à un accès root sur ce node, pour tous les conteneurs qui y tournent
2. **Dépendance obsolète** : les nodes modernes n'ont souvent plus de démon Docker
3. **Alternatives** : constructeurs sans démon, en espace utilisateur (Kaniko, Buildah, BuildKit en mode rootless)
4. **Isoler** : construire sur des nodes dédiés, avec des jetons de registry limités
5. **Signer** les images produites et épingler les digests ([[105-devsecops-ia-agentique|chaîne d'approvisionnement]])

**Piège** : considérer ce montage comme un simple détail d'implémentation de la CI.

---

## Sources

- [Kubernetes — FAQ officielle de suppression de dockershim](https://kubernetes.io/blog/2022/02/17/dockershim-faq/)

## Connexions
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — le contexte CRI
- [[03-containerd-runc|containerd & runc]] — le remplaçant de dockershim
- [[02-docker-images-registries|Docker & images]] — images OCI portables
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
