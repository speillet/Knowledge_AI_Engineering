# Mixture of Experts (MoE) — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #moe #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: paramètres totaux et actifs, routeur, load balancing, expert partagé, spécialisation réelle, coût mémoire, expert parallelism, MoE ou dense, calcul des experts distincts actifs dans un batch, communication all-to-all, déséquilibre du routeur. -->


Qu'est-ce qu'un modèle Mixture of Experts ? <!--anki:6a3348243e4677414e52-->
?
Un Transformer dont le **bloc MLP** est remplacé par **plusieurs MLP (« experts »)** et un **routeur** qui choisit, **pour chaque token**, quelques experts seulement (top-k, souvent 1 à 8 parmi des dizaines ou centaines). Seule une fraction des paramètres **travaille** à chaque token.

L'activation est **sparse**, mais les experts restent des poids à stocker quelque part. Deux tokens d'une même phrase peuvent solliciter des experts différents, et un batch peut en mobiliser beaucoup au total. Distinguer donc calcul par token, mémoire du modèle et communications de routage pour comprendre l'intérêt et le coût du MoE.

---

À ne pas confondre : paramètres totaux et paramètres actifs ? <!--anki:744144745570536d772c-->
?
- **Totaux** : tous les experts — ils déterminent la **mémoire** nécessaire.
- **Actifs** : ceux utilisés **par token** — ils déterminent le **calcul** (FLOPs) et donc en partie la vitesse.

Exemple type : un modèle de ~**670 B paramètres totaux** mais ~**37 B actifs** (ordre de grandeur de DeepSeek-V3).

Peu de paramètres actifs ne signifie donc pas « tient sur le GPU d'un modèle dense de 37 B ». Les experts inactifs doivent rester disponibles, éventuellement répartis ou déchargés ; ajouter KV cache, buffers et communications au dimensionnement.

---

Pourquoi le MoE est-il attractif pour les grands modèles ? <!--anki:427b4855503445695067-->
?
Le MoE est attractif parce qu'il augmente la **capacité totale du modèle** sans activer tous ses paramètres pour chaque token. Cette activation sparse peut offrir un meilleur compromis qualité/calcul que certaines architectures denses, selon les données, l'entraînement et le budget comparés.

Ce n'est pas une garantie universelle de qualité ni de vitesse. Les experts occupent de la mémoire, le routage ajoute des communications et la charge peut être déséquilibrée. Pour un déploiement, comparer des modèles sur les mêmes tâches et SLO, avec le coût des GPU et du réseau, plutôt que seulement les paramètres actifs.

---

Comment fonctionne le routeur d'un modèle MoE ? <!--anki:68243021393e6371397e-->
?
Une petite couche linéaire calcule un **score par expert** pour le token ; on garde les **top-k** et on combine leurs sorties **pondérées** par ces scores (après softmax). Le routage se fait **par token et par couche** : un même mot peut aller vers des experts différents à chaque couche.

Les variantes peuvent utiliser d'autres normalisations ou des experts partagés. Surveiller la charge : si la majorité des tokens choisit les mêmes experts, certains GPU deviennent le goulot. Un score de routage n'est pas une étiquette métier interprétable.

---

Qu'est-ce que le load balancing et pourquoi est-il nécessaire ? <!--anki:6b65265a7c4f75487231-->
?
Sans contrainte, le routeur **s'effondre** sur quelques experts (les autres ne sont jamais entraînés) et certains GPU sont surchargés. On ajoute une **loss auxiliaire d'équilibrage**, ou un **biais ajustable** par expert, et une **capacité maximale** de tokens par expert (les tokens en trop sont redirigés ou ignorés).

Le but est d'éviter à la fois des experts sous-entraînés et des files d'attente concentrées sur quelques GPU. Les mécanismes précis varient selon l'architecture, notamment le traitement d'un dépassement de capacité. Surveiller la distribution des tokens et les temps par expert ; un bon équilibre moyen peut masquer un batch temporairement très déséquilibré.

---

Qu'est-ce qu'un expert partagé (shared expert) ? <!--anki:493542434e742e2c5045-->
?
Un expert **toujours actif** pour tous les tokens, en plus des experts routés. Il capture les **connaissances communes**, ce qui laisse les experts routés se **spécialiser** davantage (approche DeepSeekMoE).

Le partage évite de demander à chaque expert routé de réapprendre toutes les régularités communes. Il ajoute toutefois du calcul systématique : même si seuls quelques experts routés sont choisis, l'expert partagé reste exécuté. Son contenu n'est pas une base de faits explicitement étiquetée ; la répartition des connaissances est apprise et imparfaitement interprétable.

---

Les experts sont-ils spécialisés par domaine (maths, code, français) ? <!--anki:736f6c3572507c7c512c-->
?
**Pas vraiment.** L'analyse montre une spécialisation surtout **syntaxique ou lexicale** (ponctuation, types de tokens) plutôt que thématique. « Expert » est un nom trompeur : ce sont des **sous-réseaux appris** sans rôle humainement interprétable garanti.

La spécialisation observée dépend du modèle, de la couche et des données étudiées ; il ne faut pas généraliser un résultat à tous les MoE. Le routage peut suivre des régularités locales plutôt qu'une expertise métier. On ne peut donc pas désactiver un « expert juridique » supposé pour retirer proprement toutes les connaissances juridiques.

---

Quel est le coût caché d'un MoE en inférence ? <!--anki:706d666f3345467d2f48-->
?
La **mémoire totale des poids** et les **communications de routage**. Activer peu d'experts par token réduit le calcul, pas le nombre d'experts à stocker quelque part.

Exemple : un modèle à 48 milliards de paramètres totaux mais 6 milliards actifs n'a pas l'empreinte de poids d'un dense de 6 milliards. Offloader des experts réduit la VRAM résidente au prix de transferts et de latence.

Un batch diversifié peut solliciter beaucoup d'experts ; déséquilibre de charge et échanges entre GPU deviennent alors déterminants. Le goulot peut être mémoire, réseau ou calcul : mesurer plutôt que déduire la vitesse des seuls paramètres actifs.

---

Qu'est-ce que l'expert parallelism ? <!--anki:4c6f3a3e59624f4b3a62-->
?
Répartir **les experts sur différents GPU** : chaque token est **envoyé** (all-to-all) vers le GPU qui porte ses experts, puis le résultat revient. Il s'ajoute au tensor et au pipeline parallelism ; ses **communications all-to-all** exigent des interconnexions rapides (NVLink, InfiniBand) ([[62-optimisations-inference|parallélisme]], [[54-entrainement-distribue|entraînement distribué]]).

Un GPU peut héberger plusieurs experts, et un expert peut lui-même être réparti selon l'architecture. L'enjeu est d'équilibrer tokens reçus, calcul et communications. Un expert populaire crée une attente pour les autres ; mesurer le débit global et les échanges réseau, car l'ajout de GPU peut augmenter la communication sans accélérer le traitement.

---

MoE ou dense : quoi choisir en self-hosting ? <!--anki:6b30347c33712d463774-->
?
- **Dense** : plus simple à servir, prévisible, efficace à **faible trafic** et sur **un seul GPU**.
- **MoE** : meilleur rapport qualité/calcul à **fort trafic** si l'on dispose de la **mémoire** (plusieurs GPU) et d'un serveur bien optimisé.

La [[68-quantization|quantization]] (des experts surtout) réduit l'écart de mémoire.

Ces tendances ne remplacent pas une mesure : certains MoE compacts tiennent sur une seule machine, et un dense peut aussi exiger plusieurs GPU. Fixer mémoire disponible, qualité minimale et distribution de charge, puis comparer démarrage, débit et latence. La quantification des poids réduit le stockage mais ne supprime pas les communications ni le KV cache.

---

Calcul : pour un MoE de 235B paramètres stockés à 1 octet chacun, dont 22B actifs par token, estimer le stockage brut des poids et le calcul linéaire sous l’approximation 2 FLOP par paramètre actif ? <!--anki:3665376632613631663333623433376161366631326166316565366464376231-->
?
Sous les approximations de l'énoncé :
```text
poids résidents : 235e9 × 1 octet = 235 Go décimaux
calcul linéaire : 2 × 22e9 = 44 GFLOP par token
```
Le stockage dépend des paramètres **totaux**, le calcul activé des paramètres **actifs**. Ajouter mémoire du runtime, KV cache et marge avant de dimensionner les GPU. Les 44 GFLOP excluent notamment le coût dépendant du contexte, le routage et les communications : ce n'est ni une latence, ni la garantie d'une vitesse identique à un dense 22B. Mesurer débit utile et [[121-couts-inference|coût]] sur la charge visée.

---

Calcul : 16 tokens choisissent chacun deux experts parmi huit, sans expert partagé. Combien d'experts distincts le batch peut-il solliciter ? <!--anki:3236363137376135636562633431303039616636623536663639353433646331-->
?
Le minimum est **deux experts**, si tous les tokens choisissent la même paire. Le maximum est **huit**, si les 32 affectations couvrent tous les experts disponibles.

Le nombre d'experts actifs par token reste deux dans les deux cas. La couverture du batch change pourtant les poids sollicités et la répartition des communications. Le calcul suppose deux experts distincts par token et ignore toute contrainte de capacité ou routage supplémentaire. Il illustre pourquoi « deux experts actifs » ne signifie pas que seuls deux experts du modèle sont nécessaires en mémoire pour tout le batch.

---

Que révèle un expert MoE recevant beaucoup plus de tokens que les autres ? <!--anki:6333333137316539663732353430393462313538313436383038613831643132-->
?
Il peut devenir **un goulot de calcul ou de capacité**, tandis que d'autres experts restent peu occupés. Cette concentration peut refléter les données ou un problème du routage.

Examiner la distribution par couche et par type de requête, ainsi que les mécanismes d'équilibrage du modèle. Les implémentations diffèrent sur la gestion du dépassement de capacité. Ne pas conclure à une spécialisation utile à partir du seul volume reçu.

---

## Mises en situation

Mise en situation : un modèle MoE annoncé « 37 milliards de paramètres actifs » ne tient pas sur tes deux GPU de 80 Go, alors qu'un modèle dense de 70 milliards y tenait. Explique. <!--anki:6737702e68314b6e2a35-->
?
1. **Distinguer actif et total** : les paramètres actifs déterminent le **calcul**, les totaux déterminent la **mémoire**
2. **Conséquence** : il faut charger **tous les experts**, soit des centaines de milliards de paramètres
3. **Options** : plus de GPU, ou quantization des experts, qui portent l'essentiel des poids ([[68-quantization|quantization]])
4. **Anticiper l'expert parallelism** : les communications all-to-all exigent une interconnexion rapide
5. **Vérifier le gain réel** : à gros batch, presque tous les experts s'activent, et le décodage redevient limité par la mémoire

**Piège** : dimensionner la VRAM à partir du nombre de paramètres actifs.

---

Mise en situation : pour un service interne à faible trafic sur un seul GPU, on te propose un MoE récent plutôt qu'un modèle dense. Que recommandes-tu ? <!--anki:6e4a266453757d695e37-->
?
1. **Regarder la contrainte dominante** : sur un seul GPU, c'est la mémoire, et le MoE en demande beaucoup
2. **Trafic faible** : le gain de calcul du MoE ne se transforme pas en gain visible
3. **Dense** : plus simple à servir, plus prévisible, et souvent suffisant à cette échelle
4. **Réévaluer si la charge monte** : à fort trafic et avec plusieurs GPU, le MoE devient intéressant
5. **Décider sur mesure** : qualité sur tes evals, latence et coût par requête ([[121-couts-inference|coûts]])

**Piège** : choisir une architecture pour sa réputation plutôt que pour la contrainte réelle du déploiement.

---

## Sources

- [Jiang et al. — Mixtral of Experts (2024)](https://arxiv.org/abs/2401.04088)

- Complément du 14 novembre 2026 — Routage et coûts des experts : [Fedus et al. — Switch Transformers](https://arxiv.org/abs/2101.03961).

## Connexions
- [[131-transformer-architecture|Architecture Transformer]] — le bloc MLP remplacé
- [[135-pretraining-scaling-laws|Pré-entraînement & scaling laws]] — capacité vs calcul
- [[62-optimisations-inference|Optimisations d'inférence]] — parallélisme en serving
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — déployer sur plusieurs GPU
- [[121-couts-inference|Coûts d'inférence]] — mémoire vs calcul
- [[60-011-capacite-ordonnancement-inference|Capacité & ordonnancement]] — relier mémoire, budgets et débit utile sous charge
- [[00-moc-ai-engineering|MOC AI Engineering]]
