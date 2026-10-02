# Mixture of Experts (MoE) — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #moe #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce qu'un modèle Mixture of Experts ?
?
<!--anki:6a3348243e4677414e52-->
Un Transformer dont le **bloc MLP** est remplacé par **plusieurs MLP (« experts »)** et un **routeur** qui choisit, **pour chaque token**, quelques experts seulement (top-k, souvent 1 à 8 parmi des dizaines ou centaines). Seule une fraction des paramètres **travaille** à chaque token.

---

À ne pas confondre : paramètres totaux et paramètres actifs ?
?
<!--anki:744144745570536d772c-->
- **Totaux** : tous les experts — ils déterminent la **mémoire** nécessaire.
- **Actifs** : ceux utilisés **par token** — ils déterminent le **calcul** (FLOPs) et donc en partie la vitesse.

Exemple type : un modèle de ~**670 B paramètres totaux** mais ~**37 B actifs** (ordre de grandeur de DeepSeek-V3).

---

Pourquoi le MoE est-il devenu dominant pour les grands modèles ?
?
<!--anki:427b4855503445695067-->
Il découple **capacité** et **coût de calcul** : on obtient la qualité d'un modèle bien plus gros pour le coût de calcul d'un petit, à l'entraînement comme à l'inférence. À calcul égal, un MoE atteint une **loss plus basse** qu'un modèle dense.

---

Comment fonctionne le routeur ?
?
<!--anki:68243021393e6371397e-->
Une petite couche linéaire calcule un **score par expert** pour le token ; on garde les **top-k** et on combine leurs sorties **pondérées** par ces scores (après softmax). Le routage se fait **par token et par couche** : un même mot peut aller vers des experts différents à chaque couche.

---

Qu'est-ce que le load balancing et pourquoi est-il nécessaire ?
?
<!--anki:6b65265a7c4f75487231-->
Sans contrainte, le routeur **s'effondre** sur quelques experts (les autres ne sont jamais entraînés) et certains GPU sont surchargés. On ajoute une **loss auxiliaire d'équilibrage**, ou un **biais ajustable** par expert, et une **capacité maximale** de tokens par expert (les tokens en trop sont redirigés ou ignorés).

---

Qu'est-ce qu'un expert partagé (shared expert) ?
?
<!--anki:493542434e742e2c5045-->
Un expert **toujours actif** pour tous les tokens, en plus des experts routés. Il capture les **connaissances communes**, ce qui laisse les experts routés se **spécialiser** davantage (approche DeepSeekMoE).

---

Les experts sont-ils spécialisés par domaine (maths, code, français) ?
?
<!--anki:736f6c3572507c7c512c-->
**Pas vraiment.** L'analyse montre une spécialisation surtout **syntaxique ou lexicale** (ponctuation, types de tokens) plutôt que thématique. « Expert » est un nom trompeur : ce sont des **sous-réseaux appris** sans rôle humainement interprétable garanti.

---

Quel est le coût caché d'un MoE en inférence ?
?
<!--anki:706d666f3345467d2f48-->
La **mémoire** : il faut charger **tous les experts** même si peu sont actifs → plusieurs GPU ou nœuds pour un grand MoE. Et comme chaque token d'un batch va vers des experts différents, les **gros batchs** activent presque tous les experts : le gain de calcul reste, mais le décodage devient vite **limité par la bande passante mémoire**.

---

Qu'est-ce que l'expert parallelism ?
?
<!--anki:4c6f3a3e59624f4b3a62-->
Répartir **les experts sur différents GPU** : chaque token est **envoyé** (all-to-all) vers le GPU qui porte ses experts, puis le résultat revient. Il s'ajoute au tensor et au pipeline parallelism ; ses **communications all-to-all** exigent des interconnexions rapides (NVLink, InfiniBand) ([[62-optimisations-inference|parallélisme]], [[54-entrainement-distribue|entraînement distribué]]).

---

MoE ou dense : quoi choisir en self-hosting ?
?
<!--anki:6b30347c33712d463774-->
- **Dense** : plus simple à servir, prévisible, efficace à **faible trafic** et sur **un seul GPU**.
- **MoE** : meilleur rapport qualité/calcul à **fort trafic** si l'on dispose de la **mémoire** (plusieurs GPU) et d'un serveur bien optimisé.

La [[68-quantization|quantization]] (des experts surtout) réduit l'écart de mémoire.

---

## Mises en situation

Mise en situation : un modèle MoE annoncé « 37 milliards de paramètres actifs » ne tient pas sur tes deux GPU de 80 Go, alors qu'un modèle dense de 70 milliards y tenait. Explique.
?
<!--anki:6737702e68314b6e2a35-->
1. **Distinguer actif et total** : les paramètres actifs déterminent le **calcul**, les totaux déterminent la **mémoire**
2. **Conséquence** : il faut charger **tous les experts**, soit des centaines de milliards de paramètres
3. **Options** : plus de GPU, ou quantization des experts, qui portent l'essentiel des poids ([[68-quantization|quantization]])
4. **Anticiper l'expert parallelism** : les communications all-to-all exigent une interconnexion rapide
5. **Vérifier le gain réel** : à gros batch, presque tous les experts s'activent, et le décodage redevient limité par la mémoire

**Piège** : dimensionner la VRAM à partir du nombre de paramètres actifs.

---

Mise en situation : pour un service interne à faible trafic sur un seul GPU, on te propose un MoE récent plutôt qu'un modèle dense. Que recommandes-tu ?
?
<!--anki:6e4a266453757d695e37-->
1. **Regarder la contrainte dominante** : sur un seul GPU, c'est la mémoire, et le MoE en demande beaucoup
2. **Trafic faible** : le gain de calcul du MoE ne se transforme pas en gain visible
3. **Dense** : plus simple à servir, plus prévisible, et souvent suffisant à cette échelle
4. **Réévaluer si la charge monte** : à fort trafic et avec plusieurs GPU, le MoE devient intéressant
5. **Décider sur mesure** : qualité sur tes evals, latence et coût par requête ([[121-couts-inference|coûts]])

**Piège** : choisir une architecture pour sa réputation plutôt que pour la contrainte réelle du déploiement.

---

## Sources

- [Jiang et al. — Mixtral of Experts (2024)](https://arxiv.org/abs/2401.04088)

## Connexions
- [[131-transformer-architecture|Architecture Transformer]] — le bloc MLP remplacé
- [[135-pretraining-scaling-laws|Pré-entraînement & scaling laws]] — capacité vs calcul
- [[62-optimisations-inference|Optimisations d'inférence]] — parallélisme en serving
- [[12-kubernetes-gpu-inference|Kubernetes GPU & inférence]] — déployer sur plusieurs GPU
- [[121-couts-inference|Coûts d'inférence]] — mémoire vs calcul
- [[00-moc-ai-engineering|MOC AI Engineering]]
