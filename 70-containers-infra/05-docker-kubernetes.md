# Docker & Kubernetes — Flashcards
Tags: #flashcards #docker #kubernetes

Historiquement, comment Kubernetes communiquait-il avec Docker Engine ?
?
Via une couche d'adaptation appelée **dockershim**, **intégrée au kubelet** : elle traduisait les appels [[04-kubernetes-kubelet-cri|CRI]] vers l'API de Docker Engine. Un maillon de plus à maintenir, pour un chemin déjà tortueux (`kubelet → dockershim → Docker Engine → containerd → runc`).

---

Pourquoi dockershim existait-il ?
?
Parce que Docker Engine, antérieur à Kubernetes, n'expose pas l'interface **CRI**. Quand la CRI est apparue (pour ouvrir Kubernetes à plusieurs runtimes), il fallait bien continuer à faire fonctionner les clusters existants, tous basés sur Docker.

---

Kubernetes utilise-t-il encore dockershim nativement ?
?
**Non**, il a été retiré dans la **version 1.24** (2022). Les clusters parlent désormais directement à un runtime compatible CRI. Ce qui a disparu, c'est **le raccourci vers Docker Engine**, pas la compatibilité avec les images Docker.

---

Quelle architecture est aujourd'hui courante ?
?
`kubelet → CRI → containerd (ou CRI-O) → runc → noyau Linux`

Conséquence pratique : sur un node, on débogue avec **`crictl`** et non `docker ps`, et il n'y a **pas de démon Docker** à interroger.

---

À ne pas confondre : « Kubernetes ne supporte plus Docker » et « les images Docker ne marchent plus » ?
?
- Ce qui a été retiré : **dockershim**, donc le support de **Docker Engine comme runtime** de node
- Ce qui n'a jamais changé : les **images**, conformes à l'[[01-oci|OCI]], s'exécutent parfaitement via containerd

C'est la confusion la plus fréquente sur le sujet : elle porte sur le **runtime**, pas sur le **format d'image**.

---

Docker Engine est-il nécessaire pour exécuter dans Kubernetes une image construite avec Docker ?
?
**Non.** Une image compatible [[01-oci|OCI]] peut être exécutée via [[03-containerd-runc|containerd]] et un runtime OCI.

---

## Mises en situation

Mise en situation : un développeur affirme qu'il faut réécrire les images en « format Kubernetes », puisque Docker n'est plus supporté. Que réponds-tu ?
?
1. **Distinguer** : ce qui a été retiré, c'est **dockershim**, la couche qui permettait au kubelet de piloter Docker Engine
2. **Rappeler l'architecture actuelle** : `kubelet → CRI → containerd → runc`
3. **Conclure** : les images restent des **images OCI**, construites avec Docker ou autre chose, et tournent sans Docker Engine
4. **Ce qui change réellement** : les commandes de débogage sur les nodes, et les outils qui parlaient au démon Docker
5. **Ce qu'il faut vérifier** : pas d'usage du socket Docker dans les Pods, pratique à bannir de toute façon

**Piège** : confondre le format d'image et le runtime qui l'exécute.

---

Mise en situation : un job de CI construit des images en montant le socket Docker du node dans un Pod. Quels risques et quelles alternatives ?
?
1. **Risque majeur** : accéder au socket du node revient à un accès root sur ce node, pour tous les conteneurs qui y tournent
2. **Dépendance obsolète** : les nodes modernes n'ont souvent plus de démon Docker
3. **Alternatives** : constructeurs sans démon, en espace utilisateur (Kaniko, Buildah, BuildKit en mode rootless)
4. **Isoler** : construire sur des nodes dédiés, avec des jetons de registry limités
5. **Signer** les images produites et épingler les digests ([[105-devsecops-ia-agentique|chaîne d'approvisionnement]])

**Piège** : considérer ce montage comme un simple détail d'implémentation de la CI.

---

## Connexions
- [[04-kubernetes-kubelet-cri|Kubernetes, kubelet & CRI]] — le contexte CRI
- [[03-containerd-runc|containerd & runc]] — le remplaçant de dockershim
- [[02-docker-images-registries|Docker & images]] — images OCI portables
- [[00-index|Index Conteneurs]]
- [[00-moc-ai-engineering|MOC AI Engineering]]
