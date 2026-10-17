# Tokenisation — Flashcards
Tags: #flashcards #ai-engineering #fondamentaux #tokenisation #llm
<!-- summary: token ou mot, BPE, byte-level, taille de vocabulaire, surcoût du français, limites au niveau des caractères, tokens spéciaux, chat templates, frontières de tokens, comptage, sécurité. -->


Qu'est-ce qu'un token ? <!--anki:3f72253a587d60376a-->
?
L'**unité de texte** que le modèle lit et produit : un mot fréquent, un morceau de mot, un signe de ponctuation ou un octet. En anglais, **1 token ≈ 4 caractères ≈ 0,75 mot** ; c'est l'unité de **facturation**, de **limite de contexte** et de **vitesse** de génération.

Le découpage dépend du **tokenizer du modèle**, de la langue et du type de contenu. Un identifiant rare, du code ou des caractères inhabituels peuvent coûter davantage de tokens qu'une phrase courante de même longueur. Pour un budget précis, compter le texte avec le bon tokenizer plutôt que convertir systématiquement caractères ou mots.

---

Comment fonctionne le BPE (Byte Pair Encoding) ? <!--anki:483e336061385047454a-->
?
On part des **caractères (ou octets)** et on **fusionne itérativement la paire la plus fréquente** du corpus d'entraînement en un nouveau symbole, jusqu'à atteindre la taille de vocabulaire voulue. Les séquences fréquentes deviennent un seul token, les rares se découpent en morceaux.

Une fois le tokenizer appris, les fusions et le vocabulaire sont fixés : encoder un nouveau texte n'entraîne pas à nouveau BPE. Un mot inconnu peut être composé d'unités déjà disponibles. Le découpage fréquent reflète le corpus d'apprentissage ; il n'est donc pas nécessairement aligné sur les syllabes, la morphologie ou les mots d'une autre langue.

---

Pourquoi les tokenizers modernes travaillent-ils au niveau de l'octet ? <!--anki:4c39395e4c4a45662433-->
?
Un tokenizer à couverture d'octets, comme le **byte-level BPE**, peut représenter les textes encodés en UTF-8 en partant de 256 valeurs d'octet, puis fusionner des séquences fréquentes. Cela évite un token inconnu pour les caractères rares, mais ceux-ci peuvent nécessiter plusieurs tokens.

Tous les tokenizers ne suivent pas exactement cet algorithme ; certains utilisent un mécanisme de repli sur les octets. Cela ne signifie pas qu'une API de texte accepte n'importe quel fichier binaire brut : il faut respecter son format d'entrée.

---

Quelle est la taille typique d'un vocabulaire et quel est le compromis ? <!--anki:69662b444d3f5a552f6b-->
?
De **32 k à plus de 200 k** tokens. Un gros vocabulaire **compresse mieux** le texte (moins de tokens par phrase, donc moins de coût et plus de contenu par contexte) mais agrandit la **matrice d'embedding** et la couche de sortie, et chaque token rare est moins bien appris.

La taille de la table d'embedding est approximativement **vocabulaire × dimension cachée × octets par valeur**. Augmenter le vocabulaire peut raccourcir les séquences tout en augmentant cette table et le travail de la projection finale. Le compromis dépend des langues et du corpus ; comparer le nombre de tokens sur des données représentatives, pas seulement la taille annoncée.

---

Pourquoi le français coûte-t-il plus cher que l'anglais ? <!--anki:77302b52755f516a7d50-->
?
Les tokenizers sont entraînés sur des corpus **majoritairement anglais** : le français se découpe en **plus de tokens** pour le même sens (souvent +20 à +50 % selon le tokenizer), et certaines langues bien davantage (×2 à ×4). Conséquences : **coût**, **latence** et **contexte utile** dégradés — à mesurer sur ses propres données ([[121-couts-inference|coûts]]).

---

Pourquoi les LLM échouent-ils à compter les lettres d'un mot ? <!--anki:71382c39575d78735952-->
?
Le modèle ne voit **pas les caractères** mais des **identifiants de tokens** : « strawberry » peut être 2 ou 3 tokens opaques. Les tâches au niveau du caractère (épeler, inverser, compter) et une partie de l'**arithmétique** (nombres découpés de façon irrégulière) en souffrent.

Le découpage exact varie selon le tokenizer et n'empêche pas absolument le comptage : le modèle peut apprendre des régularités ou décomposer le mot. Pour une réponse exacte, utiliser un outil qui compte les caractères selon la définition voulue. Attention aux accents combinés : caractère affiché, point de code Unicode et octet sont des unités différentes.

---

Qu'est-ce que les tokens spéciaux ? <!--anki:43234c5d264c6c23753d-->
?
Des tokens réservés pour la **structure** : début et fin de séquence, **délimiteurs de rôles** (system, user, assistant), début d'appel d'outil, etc. Ils sont insérés par le **chat template** et ne devraient **jamais** pouvoir être produits par du texte utilisateur (sinon injection de rôle).

Il faut distinguer la **chaîne visible** représentant un marqueur de son identifiant réservé dans le tokenizer. L'application doit assembler les rôles par l'interface prévue et éviter de concaténer des messages bruts comme s'ils étaient déjà structurés. Même sans injection de token spécial, une instruction malveillante en langage naturel reste possible.

---

Qu'est-ce qu'un chat template et pourquoi est-il critique en self-hosting ? <!--anki:5079604669715668237d-->
?
Le **gabarit** (souvent Jinja, fourni avec le modèle) qui transforme la liste de messages en **séquence de tokens** avec les bons tokens spéciaux. Un template **erroné** (serveur mal configuré, mauvais format d'outils) dégrade silencieusement la qualité : le modèle voit un format **qu'il n'a pas appris** ([[11-serveurs-inference-llm|serveurs d'inférence]]).

Le même historique peut devenir une séquence différente selon les séparateurs, la fin de tour et le préfixe de génération. Vérifier le template livré avec le checkpoint et tester un échange avec outil si le service en utilise. Conserver modèle, tokenizer et template ensemble pour qu'une mise à jour ne change pas silencieusement les entrées.

---

Pourquoi un espace de fin dans le prompt peut-il dégrader la sortie ? <!--anki:65762c3e4d4b3d582425-->
?
Un espace final peut **changer la tokenisation à la frontière entre prompt et continuation**. Certains tokenizers représentent un mot avec son espace initial dans un seul token ; déplacer cet espace dans le prompt modifie donc les continuations possibles et leurs probabilités.

L'effet dépend du tokenizer, du modèle et du chat template : ce n'est pas une cause universelle de mauvaise réponse. En cas de sortie étrange, inspecter les tokens réellement produits et comparer avec ou sans espace dans le même format de conversation. Éviter de modifier arbitrairement les marqueurs attendus par le modèle.

---

Comment compter les tokens correctement ? <!--anki:6c4a7138347c4535453c-->
?
Avec **le tokenizer du modèle cible** (la bibliothèque du fournisseur ou son endpoint de comptage, ou le tokenizer Hugging Face du modèle) — jamais avec l'estimation « 4 caractères » pour du budget précis. Deux modèles différents donnent des **comptes différents** pour le même texte, ce qui change le coût d'une migration.

---

Quel lien entre tokenisation et sécurité ? <!--anki:463f243f397a232c5732-->
?
- **Tokens « glitch »** sous-entraînés qui provoquent des comportements anormaux.
- **Contournement de filtres** par variantes de découpage (espaces, homoglyphes, Unicode invisible) — voir [[102-menaces-agents|injection invisible]].
- **Injection de tokens spéciaux** si l'entrée utilisateur n'est pas échappée.

Inspecter à la fois **texte rendu et représentation réelle** lorsqu'un filtre et le modèle interprètent différemment une entrée. Une normalisation Unicode peut aider certains contrôles, mais doit préserver le sens et les identifiants utiles. Les limites d'action restent nécessaires : aucun découpage de tokens ne doit permettre de contourner une autorisation vérifiée dans le code.

---

À ne pas confondre : token et mot ? <!--anki:75754b3923673b2a6863-->
?
- **Mot** : l'unité du lecteur humain
- **Token** : l'unité du modèle, fixée par son tokenizer. Un mot courant fait souvent **1 token**, un mot rare, un nombre ou un nom propre **plusieurs**

Repères : en anglais **≈ 0,75 mot par token**, en français plutôt **1,5 à 2 tokens par mot** selon le tokenizer. Les limites de contexte, les prix et les débits s'expriment en **tokens** : estimer « en mots » sous-estime la facture en français. Deux modèles n'ont pas le même tokenizer, donc pas le même compte pour un même texte.

---

## Mises en situation

Mise en situation : ton estimation de coût, calculée en anglais, est dépassée de 40 % en production sur un service francophone. Que s'est-il passé ? <!--anki:663259637351603d4f5a-->
?
1. **Cause** : les tokenizers sont entraînés surtout sur de l'anglais. Le même texte en français consomme nettement plus de tokens
2. **Recalculer** avec le tokenizer du modèle cible, sur un échantillon de **vrai trafic**, jamais avec la règle des 4 caractères
3. **Comparer les modèles** sur ce critère : deux modèles ne découpent pas le même texte de la même façon
4. **Effet double** : plus de tokens en entrée et en sortie, donc coût **et** latence, plus un contexte utile réduit
5. **Refaire l'estimation** à chaque changement de modèle, car elle n'est pas transférable ([[121-couts-inference|coûts]])

**Piège** : annoncer un budget à partir d'un calcul fait sur des textes anglais.

---

Mise en situation : après le passage de ton serveur vLLM à une nouvelle version, la qualité des réponses chute alors que le modèle n'a pas changé. Quelle piste regardes-tu en premier ? <!--anki:68465b377035613b6577-->
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
