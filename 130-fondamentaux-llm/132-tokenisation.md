# Tokenisation — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #tokenisation #llm

Qu'est-ce qu'un token ?
?
L'**unité de texte** que le modèle lit et produit : un mot fréquent, un morceau de mot, un signe de ponctuation ou un octet. En anglais, **1 token ≈ 4 caractères ≈ 0,75 mot** ; c'est l'unité de **facturation**, de **limite de contexte** et de **vitesse** de génération.

---

Comment fonctionne le BPE (Byte Pair Encoding) ?
?
On part des **caractères (ou octets)** et on **fusionne itérativement la paire la plus fréquente** du corpus d'entraînement en un nouveau symbole, jusqu'à atteindre la taille de vocabulaire voulue. Les séquences fréquentes deviennent un seul token, les rares se découpent en morceaux.

---

Pourquoi les tokenizers modernes travaillent-ils au niveau de l'octet ?
?
Le **byte-level BPE** part des **256 octets** : tout texte (emoji, langue rare, binaire) est représentable, **sans token inconnu** (`<unk>`). Le coût est qu'un caractère rare peut consommer **plusieurs tokens**.

---

Quelle est la taille typique d'un vocabulaire et quel est le compromis ?
?
De **32 k à plus de 200 k** tokens. Un gros vocabulaire **compresse mieux** le texte (moins de tokens par phrase, donc moins de coût et plus de contenu par contexte) mais agrandit la **matrice d'embedding** et la couche de sortie, et chaque token rare est moins bien appris.

---

Pourquoi le français coûte-t-il plus cher que l'anglais ?
?
Les tokenizers sont entraînés sur des corpus **majoritairement anglais** : le français se découpe en **plus de tokens** pour le même sens (souvent +20 à +50 % selon le tokenizer), et certaines langues bien davantage (×2 à ×4). Conséquences : **coût**, **latence** et **contexte utile** dégradés — à mesurer sur ses propres données ([[121-couts-inference|coûts]]).

---

Pourquoi les LLM échouent-ils à compter les lettres d'un mot ?
?
Le modèle ne voit **pas les caractères** mais des **identifiants de tokens** : « strawberry » peut être 2 ou 3 tokens opaques. Les tâches au niveau du caractère (épeler, inverser, compter) et une partie de l'**arithmétique** (nombres découpés de façon irrégulière) en souffrent.

---

Qu'est-ce que les tokens spéciaux ?
?
Des tokens réservés pour la **structure** : début et fin de séquence, **délimiteurs de rôles** (system, user, assistant), début d'appel d'outil, etc. Ils sont insérés par le **chat template** et ne devraient **jamais** pouvoir être produits par du texte utilisateur (sinon injection de rôle).

---

Qu'est-ce qu'un chat template et pourquoi est-il critique en self-hosting ?
?
Le **gabarit** (souvent Jinja, fourni avec le modèle) qui transforme la liste de messages en **séquence de tokens** avec les bons tokens spéciaux. Un template **erroné** (serveur mal configuré, mauvais format d'outils) dégrade silencieusement la qualité : le modèle voit un format **qu'il n'a pas appris** ([[11-serveurs-inference-llm|serveurs d'inférence]]).

---

Pourquoi un espace de fin dans le prompt peut-il dégrader la sortie ?
?
Les tokenizers intègrent souvent **l'espace au début du token** (« ▁chat »). Terminer le prompt par un espace force le modèle à produire un token **sans espace initial**, une configuration rare à l'entraînement → sorties étranges. Plus généralement, la **frontière de tokens** entre prompt et réponse compte.

---

Comment compter les tokens correctement ?
?
Avec **le tokenizer du modèle cible** (la bibliothèque du fournisseur ou son endpoint de comptage, ou le tokenizer Hugging Face du modèle) — jamais avec l'estimation « 4 caractères » pour du budget précis. Deux modèles différents donnent des **comptes différents** pour le même texte, ce qui change le coût d'une migration.

---

Quel lien entre tokenisation et sécurité ?
?
- **Tokens « glitch »** sous-entraînés qui provoquent des comportements anormaux.
- **Contournement de filtres** par variantes de découpage (espaces, homoglyphes, Unicode invisible) — voir [[102-menaces-agents|injection invisible]].
- **Injection de tokens spéciaux** si l'entrée utilisateur n'est pas échappée.

---

## Mises en situation

Mise en situation : ton estimation de coût, calculée en anglais, est dépassée de 40 % en production sur un service francophone. Que s'est-il passé ?
?
1. **Cause** : les tokenizers sont entraînés surtout sur de l'anglais. Le même texte en français consomme nettement plus de tokens
2. **Recalculer** avec le tokenizer du modèle cible, sur un échantillon de **vrai trafic**, jamais avec la règle des 4 caractères
3. **Comparer les modèles** sur ce critère : deux modèles ne découpent pas le même texte de la même façon
4. **Effet double** : plus de tokens en entrée et en sortie, donc coût **et** latence, plus un contexte utile réduit
5. **Refaire l'estimation** à chaque changement de modèle, car elle n'est pas transférable ([[121-couts-inference|coûts]])

**Piège** : annoncer un budget à partir d'un calcul fait sur des textes anglais.

---

Mise en situation : après le passage de ton serveur vLLM à une nouvelle version, la qualité des réponses chute alors que le modèle n'a pas changé. Quelle piste regardes-tu en premier ?
?
1. **Le chat template** : un gabarit mal appliqué ou remplacé fait voir au modèle un format qu'il n'a jamais appris
2. **Le vérifier concrètement** : afficher le prompt réellement tokenisé, avec ses tokens spéciaux
3. **Les outils** : le format d'appel d'outils fait partie du gabarit et casse souvent en premier
4. **Épingler** la version du serveur et du gabarit dans la configuration versionnée ([[111-mlops-llmops-fondamentaux|MLOps]])
5. **Détecter tôt** : un test qui compare le prompt rendu à une référence connue

**Piège** : chercher la cause dans le prompt applicatif, alors que le problème est dans la mise en forme des messages.

---

## Connexions
- [[131-transformer-architecture|Architecture Transformer]] — ce qui consomme les tokens
- [[121-couts-inference|Coûts d'inférence]] — le token comme unité de prix
- [[35-context-engineering|Context engineering]] — le contexte comme budget de tokens
- [[63-guided-generation|Guided generation]] — contraintes au niveau des tokens
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — chat templates
- [[00-moc-ai-engineering|MOC AI Engineering]]
