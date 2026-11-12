# LLM locaux, on-prem & edge — Flashcards
Tags: #flashcards #ai-engineering #edge #local #self-hosting #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: motivations, capacité ou bande passante mémoire, llama.cpp et GGUF, outils locaux, Ollama ou vLLM, Apple Silicon, small language models, hybride local et cloud, flotte d'appareils, rentabilité du on-prem, mesure en régime thermique soutenu. -->


Pourquoi faire tourner un LLM en local ou sur site ? <!--anki:68767b39524b69526735-->
?
- **Confidentialité / souveraineté** : possibilité de garder les données sur site.
- **Hors ligne** ou réseau contraint (usine, terrain, embarqué).
- **Latence** sans aller-retour réseau.
- **Coût** marginal potentiellement faible sur du matériel déjà payé.
- **Contrôle** : version figée, pas de dépréciation imposée.

Ces bénéfices exigent des contrôles : désactiver ou maîtriser télémétrie, outils distants et téléchargements. L'énergie, l'usure et la capacité occupée restent des coûts. Tester le service réseau coupé : un modèle local peut encore dépendre d'une authentification ou d'une recherche externe.

---

Quel est le facteur limitant sur un poste ou un appareil ? <!--anki:67755876354173497641-->
?
La **capacité mémoire** détermine si poids, KV et allocations tiennent ; la **bande passante** peut ensuite limiter le decode, notamment à faible batch. Calcul, offload et température peuvent aussi devenir dominants.

Exemple simplifié : un modèle dense occupant 5 Go de poids et relu entièrement par token, avec 100 Go/s réellement disponibles pour ces lectures, a un plafond lié aux poids de **20 tokens/s**. Ce n'est pas une prédiction du débit mesuré : KV, déquantification, kernels et mémoire partagée ajoutent des coûts. Un MoE, un batch ou plusieurs niveaux de mémoire demandent un modèle de performance adapté.

---

Qu'est-ce que llama.cpp et le format GGUF ? <!--anki:647e555f4a2a7a723579-->
?
**llama.cpp** est un moteur d'inférence portable en C/C++, avec différents backends CPU et GPU. **GGUF** décrit un conteneur de poids et métadonnées ; les poids peuvent être quantifiés ou en précision flottante, et le modèle peut être réparti en shards.

Le tokenizer et le chat template doivent correspondre au modèle ; vérifier les métadonnées présentes. Exemple : `llama-server -m modele.gguf -c 8192 -ngl 99`. `-ngl 99` demande l'offload d'un nombre de couches ; le résultat dépend du modèle, du backend et de la mémoire. Vérifier les logs au lieu de supposer que tout le modèle tourne sur GPU.

---

Quel outil pour servir un LLM en local : développeur seul, Mac, interface graphique, équipe ? <!--anki:3462633762323030326236333435653361303765663234343061626430623137-->
?
- **Développeur seul** : **Ollama** (gestion des modèles et API locale, au-dessus de llama.cpp), ou directement le serveur **llama.cpp**, compatible OpenAI
- **Mac Apple Silicon** : **MLX**, optimisé pour la mémoire unifiée
- **Interface graphique** : **LM Studio**
- **Équipe, utilisateurs simultanés** : **vLLM** ou **SGLang** sur un serveur GPU on-prem ([[11-serveurs-inference-llm|serveurs d'inférence]])

Ces choix sont des points de départ, pas un classement universel. Vérifier modèle supporté, sorties structurées, concurrence et conditions de déploiement ; tester le parcours réel avant de choisir sur la seule facilité d'installation.

---

Pourquoi les Mac Apple Silicon sont-ils populaires pour les LLM locaux ? <!--anki:797c71366d393945402f-->
?
La **mémoire unifiée** donne au CPU et au GPU accès à un espace mémoire commun, ce qui peut faciliter le chargement de modèles plus volumineux sur certaines configurations Apple Silicon.

La mémoire annoncée n'est pas intégralement disponible au modèle : système, autres applications, KV et buffers en consomment aussi. Débit de decode et durée de prefill dépendent du modèle, de la quantification, du backend et du matériel comparé ; aucune hiérarchie universelle face aux GPU serveurs ne découle de la marque. Mesurer un workload soutenu sur la machine cible, notamment température et partage de bande passante.

---

Quels modèles viser pour l'edge ? <!--anki:79514e2a284664622c76-->
?
Partir des **contraintes du matériel et de la tâche**, puis tester de petits modèles, éventuellement quantifiés ou [[53-donnees-synthetiques-distillation|distillés]]. La plage 1–8 milliards de paramètres est un repère, pas une définition de l'edge.

Exemple : 3 milliards de poids à 4 bits représentent environ **1,5 Go décimaux bruts**, auxquels s'ajoutent métadonnées, activations, runtime et KV cache. Cela ne garantit pas de tenir confortablement dans 2 Go.

Mesurer qualité, temps de réponse, énergie et ralentissement thermique sur l'appareil cible. Un modèle spécialisé peut battre un plus gros sur sa tâche ; fine-tuning et distillation ne compensent pas automatiquement toutes ses limites.

---

Qu'est-ce qu'une architecture hybride local / cloud ? <!--anki:6c64257577297726536d-->
?
Traiter **localement** ce qui est simple, fréquent ou sensible (PII, classification, pré-filtrage), et **escalader vers le cloud** les requêtes difficiles, après **pseudonymisation** si nécessaire. Le routeur décide selon la **difficulté**, la **sensibilité** et la **connectivité** ([[82-routing-llm|routing]]).

Exemple : un assistant d'e-mails sur poste de travail classe et résume localement avec un petit modèle. Pour rédiger une réponse complexe, il envoie au cloud un texte où noms et adresses sont remplacés par des jetons, puis réinsère les valeurs localement. Prévoir le mode hors ligne : sans réseau, la fonction cloud se dégrade explicitement au lieu d'échouer.

---

Quels défis d'exploitation d'une flotte de modèles locaux ? <!--anki:255a2e4b704c7e2b6a-->
?
- **Distribution et mise à jour** des modèles (plusieurs Go) sur de nombreux appareils.
- **Hétérogénéité** matérielle → plusieurs variantes quantizées.
- **Observabilité** limitée (pas de logs centralisés par défaut).
- **Sécurité** : les poids sont **extractibles** de l'appareil, et le modèle local reste exposé à la prompt injection.
- **Evals** à refaire pour chaque quantization.

Prévoir une mise à jour progressive, une vérification d'intégrité et un rollback compatible avec les données locales. Tester un appareil hors ligne pendant la migration ; contrôler ensuite la version effectivement active, pas seulement celle téléchargée.

---

Quand le on-prem GPU devient-il rentable par rapport aux API ? <!--anki:63522c7c41676e3e78-->
?
Quand l'**utilisation** des GPU est **élevée et régulière**, que le modèle open weights atteint la **qualité** requise, et que l'équipe sait l'**exploiter**. Le calcul doit inclure matériel, énergie, hébergement, ingénieurs, et le **taux d'occupation** réel — un GPU inoccupé la nuit coûte autant ([[121-couts-inference|break-even API vs self-host]]).

Comparer plusieurs scénarios de volume et une réserve de panne, pas seulement la charge maximale théorique. Les coûts fixes continuent pendant l'inactivité, même si l'énergie diminue. Un modèle local moins cher mais souvent escaladé vers une API peut annuler l'économie attendue.

---

À ne pas confondre : capacité mémoire et bande passante mémoire ? <!--anki:782f576c373a7e467939-->
?
La **capacité** borne le volume de poids, KV cache et autres allocations qui peuvent résider dans une mémoire. La **bande passante** borne la vitesse des transferts ; elle contribue au débit lorsque ces transferts sont le goulot.

Comparer les deux sur le workload cible. Une grande mémoire permet de charger un modèle plus gros sans garantir une génération plus rapide ; une forte bande passante ne suffit pas si le modèle impose un offload coûteux. Calcul, batch, contexte, quantization et liens entre mémoires modifient le compromis. Les seuls Go annoncés ne permettent pas de classer les machines.

---

Calcul : à batch 1, un dense 8B occupe en moyenne 4,8 bits par poids en Q4_K_M. Quel plafond de decode lié aux seules lectures des poids, avec 400 Go/s et une lecture complète par token ? <!--anki:6662653665313639616561363434653162323664663362306565646566613361-->
?
Sous les hypothèses de lecture données :
```text
poids = 8e9 × 4,8 / 8 = 4,8 Go
plafond dû aux poids = 400 / 4,8 ≈ 83 tokens/s
```
Le débit mesuré peut être plus faible à cause du KV, des activations, des kernels, de la déquantification et du partage de bande passante avec le reste du système. Ce quotient ne garantit ni 50–60 tokens/s en pratique ni un goulot toujours mémoire. Vérifier également que le modèle complet tient dans la mémoire disponible et mesurer le workload réel.

---

Pourquoi un benchmark LLM local doit-il durer assez longtemps pour révéler les limites thermiques ? <!--anki:3434363562623530373734633439313261313463646438326364653463326538-->
?
Un **essai court** peut bénéficier d'une fréquence élevée que l'appareil ne maintient pas sous charge continue. Température, alimentation et tâches concurrentes peuvent réduire le débit après quelques minutes.

Mesurer démarrage, régime soutenu, mémoire et consommation sur l'appareil cible, avec contexte et qualité comparables. Tester sur batterie si cet usage est prévu. Vérifier la latence après plusieurs requêtes longues et en présence des applications habituelles. Un débit maximal obtenu machine froide ne suffit pas à dimensionner une expérience locale quotidienne.

---

## Mises en situation

Mise en situation : une équipe a mis Ollama en production pour 50 utilisateurs et se plaint que « les modèles locaux sont lents ». Que diagnostiques-tu ? <!--anki:43257c3f2b6670734c3b-->
?
1. **Mauvais outil pour l'usage** : llama.cpp et Ollama traitent peu de requêtes simultanées
2. **Passer à un serveur d'inférence** : vLLM ou SGLang, avec continuous batching et PagedAttention ([[11-serveurs-inference-llm|serveurs]])
3. **Vérifier le matériel** : le débit dépend surtout de la **bande passante mémoire**, pas seulement du nombre de cœurs
4. **Dimensionner** : mesurer le débit réel à la concurrence cible avant de conclure ([[64-metriques-slo-inference|SLO]])
5. **Garder Ollama** pour ce qu'il fait bien : postes de développement et prototypage

**Piège** : conclure que l'auto-hébergement ne fonctionne pas, alors que c'est le serveur qui n'est pas adapté.

---

Mise en situation : un client industriel veut un assistant qui fonctionne sans Internet, sur des postes d'atelier. Comment conçois-tu la solution ? <!--anki:5073454f71744f5d4025-->
?
1. **Cadrer la tâche** : un petit modèle (1 à 8 milliards de paramètres) réussit bien une tâche **ciblée**, pas une culture générale
2. **Quantizer en 4 bits** et vérifier que le modèle tient dans la mémoire des postes ([[68-quantization|quantization]])
3. **Spécialiser** : fine-tuning ou distillation sur la tâche, pour compenser la taille ([[53-donnees-synthetiques-distillation|distillation]])
4. **Prévoir l'exploitation** : distribution et mise à jour de plusieurs gigaoctets, variantes selon le matériel, evals refaites par variante
5. **Sécurité** : les poids sont extractibles du poste, et l'injection de prompt reste possible

**Piège** : promettre les capacités d'un grand modèle cloud sur un appareil qui n'en a ni la mémoire ni la bande passante.

---

## Sources

- [llama.cpp — formats, quantification et inférence locale](https://github.com/ggml-org/llama.cpp)
- [vLLM — quantification et matériels compatibles](https://docs.vllm.ai/en/latest/features/quantization/)

- [llama.cpp — options du serveur et offload des couches](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) — vérification ciblée du 12 novembre 2026, sans renouvellement de la date globale de la fiche.

## Connexions
- [[68-quantization|Quantization]] — faire tenir le modèle
- [[11-serveurs-inference-llm|Serveurs d'inférence LLM]] — vLLM, llama.cpp, Ollama
- [[10-images-modeles-poids|Images & poids de modèles]] — GGUF et distribution
- [[146-choix-modeles|Choix de modèle]] — open weights vs API
- [[121-couts-inference|Coûts d'inférence]] — break-even
- [[53-donnees-synthetiques-distillation|Distillation]] — petits modèles spécialisés
- [[101-securite-llm-guardrails|Sécurité LLM]] — injection, exfiltration et guardrails
- [[61-kv-cache-attention|KV cache]] — la mémoire qui limite la concurrence
- [[00-moc-ai-engineering|MOC AI Engineering]]
