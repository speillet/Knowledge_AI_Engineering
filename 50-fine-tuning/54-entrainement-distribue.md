# Entraînement distribué — Flashcards
Tags: #flashcards #ai-engineering #fine-tuning #distributed-training #gpu
<!-- summary: calcul de la mémoire d'un fine-tuning 7B avec Adam, data ou model parallelism, DDP, ZeRO et FSDP, tensor et pipeline parallelism, parallélisme 3D, gradient checkpointing, accumulation de gradients, précision mixte BF16, réseau, pannes et checkpoints. -->


Que faut-il stocker en mémoire GPU pendant l'entraînement ? <!--anki:4b3540475374235a42-->
?
1. **Poids** du modèle.
2. **Gradients** (même taille que les poids).
3. **États de l'optimiseur** : Adam garde **deux moments** par paramètre, souvent en FP32, plus une copie FP32 des poids.
4. **Activations** conservées pour la passe arrière — elles croissent avec la **taille du batch et la longueur des séquences**.

---

Calcul : un fine-tuning complet 7B utilise poids et gradients BF16, une copie maîtresse FP32 et deux moments Adam FP32. Quelle mémoire pour ces états, hors activations et buffers ? <!--anki:4f713b3f5d38403a325b-->
?
En précision mixte, environ **16 octets par paramètre** avant activations :
```text
poids BF16                         2 octets
gradients BF16                     2 octets
copie FP32 + deux moments d'Adam  12 octets
total ≈ 16 octets × 7e9          ≈ 112 Go (+ activations)
```
Cette enveloppe dépasse une carte de 80 Go ; une carte plus grande, plusieurs GPU avec sharding ou une adaptation légère sont des options. Les seuls poids d’inférence occupent environ 14 Go. D'où l'intérêt de [[51-fine-tuning-adaptation|LoRA / QLoRA]] ou du sharding ZeRO/FSDP.

---

Qu'est-ce que le data parallelism (DDP) ? <!--anki:7a643e4b316b7a3a7526-->
?
Chaque GPU a une **copie complète du modèle** et traite **une partie du batch** ; les gradients sont **moyennés entre GPU** (all-reduce) avant chaque mise à jour. Simple et efficace, mais le modèle doit **tenir entièrement** sur un GPU.

Il faut aussi répartir les **données** : DDP synchronise les gradients mais ne garantit pas à lui seul des exemples distincts sur chaque rang. Avec quatre GPU et huit exemples par GPU, un pas couvre normalement 32 exemples. Le modèle, ses gradients et les états d'optimiseur restent répliqués dans le DDP classique, ce qui limite le gain mémoire.

---

Qu'est-ce que ZeRO et FSDP ? <!--anki:45643a7d4866595d5b4e-->
?
Des variantes du data parallelism qui **répartissent (sharding) les états** entre GPU au lieu de les dupliquer :
- **ZeRO-1** : états de l'optimiseur ;
- **ZeRO-2** : + gradients ;
- **ZeRO-3 / FSDP** : + poids (rassemblés couche par couche au moment du calcul).

La mémoire par GPU est divisée par le **nombre de GPU**, au prix de **plus de communications**. Implémentations : DeepSpeed, PyTorch FSDP.

---

Qu'est-ce que le tensor parallelism ? <!--anki:755a7e2d324d60357763-->
?
Le **tensor parallelism** répartit les opérations de certaines couches, notamment leurs matrices, sur plusieurs GPU. Chacun calcule une partie du résultat ; des communications réunissent les contributions nécessaires à la suite du réseau. Cela permet de distribuer des poids et des calculs trop volumineux pour un seul GPU.

Comme les échanges sont fréquents, une interconnexion rapide, souvent à l'intérieur d'un nœud, est particulièrement utile. Le multi-nœud reste possible selon le matériel et l'implémentation. Augmenter le degré de parallélisme réduit le travail local, mais peut augmenter la part de temps consacrée aux communications.

---

Qu'est-ce que le pipeline parallelism ? <!--anki:68393a736c62713e4645-->
?
Répartir **les couches** entre GPU (couches 1-20 sur le GPU 1, 21-40 sur le GPU 2…). Le batch est découpé en **micro-batchs** qui avancent en chaîne pour limiter les **bulles** (GPU inactifs en attente). Communications modérées → utilisable **entre nœuds**.

Pendant qu'un GPU traite un micro-batch, le suivant peut travailler sur un micro-batch précédent. Il reste des phases de remplissage et de vidage, ainsi que des déséquilibres si une étape est plus lente. Découper selon le **coût mesuré des couches**, pas uniquement leur nombre, et mesurer mémoire d'activations et temps perdu dans les bulles.

---

Qu'est-ce que le parallélisme 3D ? <!--anki:62293e267d6e7d3a7a4d-->
?
La **combinaison** des trois : tensor parallelism **dans le nœud**, pipeline parallelism **entre nœuds**, data parallelism (FSDP/ZeRO) **par-dessus**, plus parfois le **context** parallelism (séquences longues) et l'**expert** parallelism ([[136-mixture-of-experts|MoE]]). C'est la configuration des grands pré-entraînements (Megatron-LM, TorchTitan).

Par exemple, 8 GPU en tensor parallelism, 4 étages de pipeline et 2 répliques de données mobilisent **8 × 4 × 2 = 64 GPU**, dans cette décomposition. Chaque axe répond à une limite différente : taille d'une couche, profondeur du modèle ou débit. Leur combinaison doit respecter mémoire, topologie réseau et taille du batch global.

---

Qu'est-ce que le gradient checkpointing ? <!--anki:4b623d76394a25253056-->
?
Ne garder qu'**une partie des activations** pendant la passe avant et **recalculer** les autres pendant la passe arrière. On échange environ **30 % de calcul en plus** contre une **forte réduction de mémoire** d'activations — indispensable pour les longues séquences.

Le surcoût exact dépend des segments recalculés ; 30 % est un repère, pas une constante. Cette technique réduit surtout les **activations sauvegardées**, pas les poids ni tous les états de l'optimiseur. Si ceux-ci saturent déjà la mémoire, il faut agir sur un autre poste. Mesurer le compromis entre mémoire économisée et temps par pas.

---

Qu'est-ce que l'accumulation de gradients ? <!--anki:4132692b52472140715d-->
?
Additionner les gradients de **plusieurs petits batchs** avant de faire une mise à jour : on simule un **grand batch effectif** sans la mémoire correspondante. Batch effectif = micro-batch × pas d'accumulation × nombre de GPU.

Par exemple, 4 exemples par micro-batch, 8 accumulations et 2 répliques de données donnent **64 exemples par mise à jour**. Le multiplicateur GPU concerne les répliques de données, pas les GPU de tensor parallelism. Normaliser correctement la loss et n'avancer l'optimiseur qu'au moment prévu ; l'équivalence avec un grand batch dépend aussi des opérations du modèle.

---

Qu'est-ce que la précision mixte et pourquoi BF16 plutôt que FP16 ? <!--anki:665a7a642e456235383a-->
?
Calculer en **16 bits** (plus rapide, moins de mémoire) tout en gardant une copie **FP32** des poids pour les mises à jour. **BF16** a la même **plage de valeurs** que FP32 (8 bits d'exposant) : les débordements sont bien plus rares qu'en FP16 et le **loss scaling** n'est généralement pas nécessaire, au prix d'une mantisse moins précise. Les GPU récents entraînent aussi en **FP8**.

---

Pourquoi le réseau compte-t-il autant en entraînement distribué ? <!--anki:443d775a5e4440455875-->
?
Chaque pas exige des **all-reduce / all-gather** de gigaoctets entre GPU. Sans **NVLink** dans le nœud et **InfiniBand / RoCE** entre nœuds, les GPU **attendent** et le [[135-pretraining-scaling-laws|MFU]] s'effondre. La topologie du cluster conditionne le choix de parallélisme.

Le volume échangé dépend de la stratégie : DDP agrège des gradients, tandis que FSDP doit aussi rassembler des paramètres. Examiner bande passante effective, latence des collectives et chevauchement avec le calcul. Ajouter des GPU n'accélère pas forcément le pas si les communications ou un lien lent deviennent la nouvelle limite.

---

Quels problèmes d'exploitation pose un entraînement sur beaucoup de GPU ? <!--anki:6545723a4169537c663f-->
?
- **Pannes** fréquentes (GPU, nœuds, réseau) → **checkpoints** réguliers et reprise automatique.
- **Pics de loss** (loss spikes) → surveillance et retour au checkpoint précédent.
- **Stragglers** : un GPU lent ralentit tous les autres.
- **Ordonnancement** du cluster (Slurm, Kubernetes avec Kueue/Volcano) — voir [[13-apptainer-inference-hpc|HPC & Slurm]].

Un checkpoint exploitable conserve aussi optimiseur, scheduler et état nécessaire à la lecture des données. Tester sa restauration avant un long entraînement et choisir la fréquence selon le coût d'écriture et le travail perdu acceptable. Pour un ralentissement, distinguer GPU défaillant, réseau saturé et alimentation en données insuffisante avant de relancer tout le job.

---

À ne pas confondre : data parallelism et model parallelism ? <!--anki:643b6f29754f79465e4b-->
?
- **Data parallelism** (DDP, FSDP) : chaque GPU traite **des données différentes** avec une copie (ou un fragment) du modèle, et les gradients sont moyennés
- **Model parallelism** : le **modèle lui-même** est découpé entre GPU, par couches (**pipeline**) ou à l'intérieur des couches (**tensor**)

Le premier accélère l'entraînement d'un modèle qui tient déjà en mémoire ; le second devient nécessaire quand il **ne tient plus**. Les grands entraînements combinent les deux.

---

Calcul : sous C ≈ 6ND, combien de GPU-heures utiles pour une époque de fine-tuning dense 7B sur 100 millions de tokens, à 4 × 10^14 FLOP/s utiles par GPU ? <!--anki:6264366332636363363433613463316539343266666164623039333564333938-->
?
```text
C ≈ 6 × N × D = 6 × 7e9 × 1e8   = 4,2e18 FLOP
H100 à 40 % de MFU              ≈ 4e14 FLOP/s
4,2e18 / 4e14                   ≈ 10 500 s ≈ 3 GPU-heures par époque
```
Le calcul d'un fine-tuning se compte en **GPU-heures**, pas en GPU-années. La contrainte est la **mémoire** (≈ 112 Go pour un 7B avec Adam), qui peut nécessiter sharding ou [[51-fine-tuning-adaptation|LoRA]].

C'est une estimation de calcul utile, pas un délai promis : transferts, checkpoints, padding et efficacité réelle s'ajoutent. Avec plusieurs GPU, la durée idéale diminue mais les GPU-heures ne disparaissent pas. Les 112 Go excluent notamment les activations et supposent un schéma précis de précision et d'états Adam.

---

Que se passe-t-il si un GPU tombe en panne au milieu d'un entraînement distribué ? <!--anki:3236353836376335663738323437393161333434323538316365383736326463-->
?
L'entraînement est **synchrone** : chaque étape attend les gradients de tous les GPU, donc **tout le job s'arrête**. On le relance depuis le dernier **checkpoint**, et tout ce qui a été calculé depuis est perdu.

À l'échelle de milliers de GPU, les pannes surviennent **plusieurs fois par jour** : on sauvegarde souvent (checkpoints asynchrones, pour ne pas bloquer le calcul), on relance automatiquement, et on garde des nœuds de rechange.

---

## Mises en situation

Mise en situation : ton modèle de 7 milliards de paramètres tourne sans problème en inférence sur un GPU de 80 Go, mais le fine-tuning complet échoue en mémoire. Explique et propose une solution. <!--anki:4b2b71595771393f3e60-->
?
1. **Comprendre l'écart** : l'entraînement stocke poids, gradients, états de l'optimiseur et activations, soit environ 16 octets par paramètre avant activations
2. **Calculer** : environ 112 Go pour 7 milliards de paramètres, donc plusieurs GPU
3. **La réponse la plus simple** : **LoRA** ou **QLoRA**, qui n'entraînent qu'une petite fraction des paramètres ([[51-fine-tuning-adaptation|LoRA]])
4. **Sinon, réduire la mémoire** : gradient checkpointing, accumulation de gradients, précision mixte BF16
5. **En dernier recours, distribuer** : FSDP ou ZeRO-3 pour répartir les états entre GPU

**Piège** : dimensionner un entraînement à partir de la mémoire nécessaire à l'inférence.

---

Mise en situation : ton entraînement sur 32 GPU n'utilise que 20 % de leur puissance théorique. Où cherches-tu ? <!--anki:6c2e39332b675d795755-->
?
1. **Le réseau d'abord** : sans NVLink dans le nœud et interconnexion rapide entre nœuds, les GPU attendent les communications
2. **La stratégie de parallélisme** : le tensor parallelism doit rester **dans** un nœud, le pipeline entre nœuds
3. **Les bulles du pipeline** : micro-batchs trop peu nombreux laissent des GPU inactifs
4. **Les stragglers** : un nœud lent ou dégradé ralentit tout le collectif
5. **Le profil** : mesurer le temps passé en calcul et en communication avant de changer quoi que ce soit

**Piège** : augmenter la taille du batch pour « occuper les GPU », et se heurter à la mémoire d'activations.

---

## Connexions
- [[51-fine-tuning-adaptation|Fine-tuning & adaptation]] — LoRA pour éviter le distribué
- [[135-pretraining-scaling-laws|Pré-entraînement & scaling laws]] — MFU, budget de calcul
- [[136-mixture-of-experts|Mixture of Experts]] — expert parallelism
- [[62-optimisations-inference|Optimisations d'inférence]] — parallélisme en serving
- [[09-gpu-conteneurs|GPU en conteneur]] et [[13-apptainer-inference-hpc|Apptainer & HPC]] — l'infrastructure
- [[114-reproductibilite-variance|Reproductibilité]] — fine-tuning reproductible
- [[55-rl-agentique|RL agentique]] — entraîner un modèle sur des tâches d'agent
- [[56-optimisation-diagnostic-entrainement|Optimisation & diagnostic d'entraînement]] — batch effectif et réduction des gradients
- [[00-moc-ai-engineering|MOC AI Engineering]]
