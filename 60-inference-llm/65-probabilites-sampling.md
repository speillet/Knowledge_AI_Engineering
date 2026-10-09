# Probabilités & sampling — Flashcards
Tags: #flashcards #ai-engineering #inference #sampling #probabilites #llm
<!-- summary: logits, température, greedy, top-k, top-p et min-p, probabilités conditionnelles, logprobs, perplexité, exercices de renormalisation, sampling et limites de la confiance. -->


Que produit un LLM à chaque pas de génération ? <!--anki:7a6f51326e26623f245b-->
?
Un **vecteur de logits** (un score par token du vocabulaire), transformé en **distribution de probabilité** par un **softmax**. Le token suivant est **choisi** dans cette distribution, ajouté au contexte, et on recommence : c'est la génération **autorégressive**.
```text
contexte → logits → softmax → P(token) → choix → contexte + token → …
```

---

Pourquoi deux appels identiques donnent-ils des réponses différentes ? <!--anki:494e50217049554b3f66-->
?
Le **sampling** peut choisir des tokens différents dans une même distribution ; le préfixe change ensuite et les continuations peuvent diverger.

Ce n'est pas la seule cause : révision du modèle, documents récupérés, template, paramètres, calculs numériques et batching peuvent varier. Même sans sampling, le résultat dépend de l'environnement. Pour diagnostiquer, vérifier d'abord que l'entrée complète et la configuration sont identiques, puis distinguer aléa d'échantillonnage et variations du système. « Même question utilisateur » ne signifie pas « même problème effectivement envoyé au modèle ».

---

Quel est le rôle de la température ? <!--anki:7a675f34445f53796f43-->
?
Pour **T > 0**, la température divise les logits avant softmax :
```text
P(i) = exp(z_i / T) / somme_j exp(z_j / T)
```
T < 1 concentre davantage la masse sur les logits élevés ; T > 1 l'étale ; T = 1 conserve la distribution avant d'autres traitements éventuels. En limite T → 0, la masse se concentre sur le maximum ; les API utilisent souvent zéro pour demander greedy.

Ces effets concernent la **diversité des tirages**, pas la vérité. Une distribution concentrée peut répéter une erreur avec assurance ; évaluer exactitude et répétitions séparément.

---

Qu'est-ce que le décodage greedy ? <!--anki:6f593a673f4456597d3a-->
?
Prendre **à chaque pas le token le plus probable** (température 0). Simple et stable, mais il peut **tourner en boucle** (répétitions) et ne donne **pas** forcément la séquence la plus probable dans son ensemble.

Le choix est local : le token préféré maintenant peut conduire à une suite globalement moins probable qu'un autre début. Température zéro n'assure pas non plus une identité parfaite entre infrastructures, à cause des arrondis et de l'implémentation. Évaluer répétitions et exactitude, sans assimiler absence de sampling et vérité.

---

Qu'est-ce que le top-k sampling ? <!--anki:74476e34764847357059-->
?
Ne garder que les **k tokens les plus probables**, **renormaliser** leurs probabilités, puis échantillonner. Limite : k est **fixe**, que le modèle soit sûr de lui (un seul bon candidat) ou qu'il hésite (des dizaines).

---

Qu'est-ce que le top-p (nucleus sampling) ? <!--anki:46793e5f305777615e5f-->
?
Garder le **plus petit ensemble de tokens dont la probabilité cumulée atteint p** (ex. 0,9), renormaliser, échantillonner. L'ensemble **s'adapte** : étroit quand le modèle est sûr, large quand il hésite.

Pour des probabilités 0,6, 0,25, 0,1 et 0,05, un seuil de 0,8 garde les deux premiers tokens, qui cumulent 0,85. On renormalise avant tirage. Le seuil réduit les options peu probables mais ne mesure pas la confiance factuelle ; un modèle peut être très concentré sur une réponse erronée.

---

Qu'est-ce que le min-p ? <!--anki:63343a6840684d475a3f-->
?
Le **min-p** conserve les tokens dont la probabilité est au moins `min_p × p_max`, puis renormalise avant le tirage. Avec `p_max = 0,5` et `min_p = 0,1`, le seuil vaut 0,05.

C'est un seuil relatif au token le mieux classé, tandis que top-p utilise une masse cumulée. Le support et l'ordre des traitements dépendent du moteur. Une meilleure performance à haute température doit être évaluée sur la tâche ; le seuil suit la concentration de la distribution, pas une confiance factuelle déjà calibrée.

---

Quels réglages de sampling selon le cas d'usage ? <!--anki:627032625674675b7b24-->
?
Partir des **réglages prévus pour le modèle**, puis comparer sur la tâche. Une faible température ou greedy est un candidat pour une extraction stable ; davantage de diversité peut aider la recherche de plusieurs solutions.

Ces choix ne garantissent ni exactitude ni créativité utile. Mesurer qualité, répétitions, validité du format et coût ; vérifier si le modèle impose certains paramètres. Modifier un réglage à la fois aide le diagnostic, puis tester les interactions. Les valeurs numériques d'un autre modèle ne sont pas une recette universelle.

---

Que sont les logprobs et à quoi servent-ils ? <!--anki:4c453a62566a77455729-->
?
Les **logprobs** sont les logarithmes des probabilités attribuées aux tokens, pour les événements et traitements définis par l'API. Elles servent à calculer une vraisemblance ou à construire un score de classification.

Comparer « oui » et « non » suppose de définir les labels, leur tokenisation et la normalisation ; certains labels utilisent plusieurs tokens. Une logprob faible peut simplement correspondre à un nom rare. Ni sa valeur ni l'assurance verbale ne constituent directement une probabilité d'hallucination. Valider le score sur des exemples annotés avant d'en faire un seuil d'abstention.

---

Comment calcule-t-on la probabilité d'une séquence ? <!--anki:785f373940723d475669-->
?
Par la **règle de chaîne** : multiplier les probabilités de chaque token conditionnellement au préfixe ; en logarithmes, les additionner.
```text
P(t1,…,tn | contexte) = produit_i P(ti | contexte,t1,…,t{i−1})
```
Pour une séquence complète terminée, préciser si EOS entre dans l'événement. La moyenne des logprobs par token sert à comparer des scores normalisés, mais **n'est plus la log-probabilité de la séquence entière**. Choisir le score selon l'objectif : la normalisation change le classement possible et ne transforme pas la vraisemblance en exactitude métier.

---

Qu'est-ce que la perplexité ? <!--anki:447e6435633669525170-->
?
La **perplexité** est l'exponentielle de la moyenne des log-probabilités négatives des tokens de référence, avec logarithmes naturels :
```text
PPL = exp(− somme_i log P(ti | préfixe) / N)
```
Elle mesure la prédictibilité d'un texte sous le modèle. Pour comparer, garder corpus, tokenisation, masque des positions évaluées et politique de contexte comparables. Une tokenisation différente peut changer l'échelle sans progrès utile. La perplexité n'évalue directement ni factualité, ni respect d'instructions, ni qualité d'une réponse isolée ; compléter par des critères de tâche.

---

Les probabilités d'un LLM sont-elles fiables (calibration) ? <!--anki:454b32677a482d2d2925-->
?
La **calibration dépend de l'événement et de la population évalués**. La probabilité du prochain token n'est pas directement celle qu'une réponse entière soit correcte. Une phrase fréquente mais fausse peut être très probable.

Le post-training, le prompt et le domaine peuvent modifier la calibration ; la confiance verbalisée n'est pas une mesure validée par défaut. Construire un score pour une tâche précise, le confronter à des labels indépendants et vérifier ses segments. Ne pas transformer automatiquement une logprob élevée en indicateur de factualité.

---

Le speculative decoding modifie-t-il la distribution des sorties ? <!--anki:745b47483e2155344a39-->
?
Le **speculative sampling exact** préserve mathématiquement la distribution de la cible grâce à une règle d'acceptation/rejet et à un tirage corrigé en cas de rejet. En greedy, la vérification vise les mêmes choix que le modèle cible seul.

Cette propriété concerne l'algorithme et ses hypothèses, pas toutes les variantes approximatives ni une égalité bit à bit de toute implémentation. Les arrondis, kernels et modes de vérification peuvent produire des écarts. Valider la méthode activée et tester la qualité sur la charge réelle ([[62-optimisations-inference|optimisations d'inférence]]).

---

À ne pas confondre : température et top-p ? <!--anki:70332c3a5d2f2c2b6961-->
?
La **température** modifie les probabilités relatives via les logits ; **top-p** sélectionne, dans l'ordre décroissant, le plus petit préfixe de tokens atteignant la masse cumulée p, puis renormalise.

Modifier les deux change à la fois distribution et ensemble admissible. Pour attribuer un effet, commencer par une seule variable, puis tester une combinaison si nécessaire. Il n'existe pas d'interdiction mathématique de les combiner ; vérifier leur support et leur ordre dans le moteur. Aucun des deux ne règle directement la vérité ou la sécurité des réponses.

---

Que se passe-t-il si on combine une température élevée (1,5) et un top-p à 1 ? <!--anki:3263666230666563316166313465656538393562646233623835343166666633-->
?
T = 1,5 **aplatit la distribution** par rapport à T = 1 ; top-p = 1 ne retire aucun candidat par troncature de masse. Les tokens initialement moins probables peuvent donc être tirés plus souvent, sans que chaque sortie doive devenir incohérente.

L'effet dépend du modèle et des autres traitements. Comparer diversité utile, erreurs et répétitions sur les mêmes tâches. Réduire la température ou tronquer la distribution sont des candidats à tester, pas une garantie de qualité. Une erreur précoce peut aussi influencer les continuations suivantes.

---

Calcul : quatre tokens ont les probabilités 0,50, 0,30, 0,15 et 0,05. Avec top-p = 0,75 appliqué seul, lesquels restent et avec quelles probabilités après renormalisation ? <!--anki:6465663762656366643837343433363162626362623533656132343239356336-->
?
Garder le plus petit préfixe trié dont la masse atteint **0,75** : le premier token ne suffit pas ; les deux premiers totalisent 0,80.
```text
P₁ après filtrage = 0,50 / 0,80 = 0,625
P₂ après filtrage = 0,30 / 0,80 = 0,375
P₃ = P₄ = 0
```
Le seuil est une masse à atteindre, pas un nombre de tokens ni une probabilité minimale par token. La masse retenue peut dépasser le seuil. On tire ensuite un token dans cette distribution ; conserver deux candidats ne signifie pas les produire tous les deux.

---

Calcul : deux tokens de référence ont les probabilités conditionnelles 0,5 puis 0,25. Hors EOS, quelle est la probabilité de leur séquence et sa perplexité sur ces deux tokens ? <!--anki:3831613766666264346431313433313261646537653733636530313265303561-->
?
Appliquer la règle de chaîne, puis normaliser le logarithme pour la perplexité :
```text
P(séquence) = 0,5 × 0,25 = 0,125
PPL = exp(−(ln 0,5 + ln 0,25)/2) = √8 ≈ 2,83
```
Les probabilités sont déjà conditionnelles aux préfixes : leur multiplication ne suppose pas des tokens indépendants. La moyenne `(0,5 + 0,25)/2` n'est pas la probabilité de la séquence. La perplexité décrit la vraisemblance moyenne des tokens retenus pour ce calcul ; elle ne mesure pas la véracité de leur contenu.

---

## Mises en situation

Mise en situation : ton extraction de champs à partir de contrats donne des résultats différents à chaque exécution sur le même document. Quels réglages changes-tu ? <!--anki:67437644407968463477-->
?
1. **Température basse** (0 à 0,3) : l'extraction n'a pas besoin de créativité
2. **Isoler les effets** : modifier un paramètre à la fois, puis tester les combinaisons utiles
3. **Contraindre la sortie** par un schéma, pour supprimer la variabilité de forme ([[63-guided-generation|guided generation]])
4. **Mesurer la variabilité résiduelle** : même à température 0, les calculs GPU peuvent varier selon l’environnement ([[114-reproductibilite-variance|reproductibilité]])
5. **Tester sur des propriétés** (bon montant extrait) plutôt que sur une chaîne exacte

**Piège** : croire que `temperature=0` garantit des sorties identiques d'un jour à l'autre.

---

Mise en situation : ton classifieur doit envoyer les cas incertains à un humain. Comment mesures-tu la confiance du modèle ? <!--anki:634925695a74604d7079-->
?
1. **Logprobs** : demander les probabilités des tokens de la réponse et comparer les classes candidates
2. **Seuil d'escalade** : au-dessous d'une probabilité donnée, la demande part vers un humain ([[144-ux-ia-human-in-the-loop|human-in-the-loop]])
3. **Calibrer le seuil** sur un jeu annoté : mesurer l'exactitude réelle par tranche de confiance
4. **Se méfier de la confiance verbalisée** (« je suis sûr à 90 % »), peu fiable
5. **Surveiller** la dérive du taux d'escalade en production ([[93-monitoring-inference|monitoring]])

**Piège** : utiliser la perplexité comme score de qualité d'une réponse, ce qu'elle ne mesure pas.

---

## Sources

- [Hugging Face — perplexité et tokenisation](https://huggingface.co/docs/transformers/en/perplexity)
- [Hugging Face — paramètres de génération](https://huggingface.co/docs/transformers/en/main_classes/text_generation)

- [vLLM — speculative decoding et limites de reproductibilité numérique](https://docs.vllm.ai/en/latest/features/speculative_decoding/index.html)

## Connexions
- [[61-kv-cache-attention|KV cache & attention]] — la génération token par token
- [[62-optimisations-inference|Optimisations d'inférence]] — speculative decoding
- [[63-guided-generation|Guided generation]] — masquer des logits avant l'échantillonnage
- [[11-prompt-engineering-avance|Prompt engineering]] — self-consistency : plusieurs échantillons, vote majoritaire
- [[114-reproductibilite-variance|Reproductibilité & variance]] — pourquoi les sorties varient même à température 0
- [[92-chainforge-evals-prompts|Evals]] — mesurer l'effet des réglages
- [[67-speculative-decoding|Speculative decoding]] — la règle d'acceptation qui préserve la distribution
- [[131-transformer-architecture|Architecture Transformer]] — d'où viennent les logits
- [[143-hallucinations-grounding|Hallucinations]] — calibration et détection
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM et leur réglage
- [[52-post-training-alignement|Post-training & alignement]] — RLHF, DPO, GRPO et RLVR
- [[00-moc-ai-engineering|MOC AI Engineering]]
