# Données : curation & annotation — Flashcards
Tags: #flashcards #ai-engineering #donnees #annotation #qualite

Pourquoi les données restent-elles décisives à l'ère des LLM pré-entraînés ?
?
Parce que la **différenciation** d'une application vient de ses données : documents du RAG, **jeux d'eval**, exemples few-shot, données de **fine-tuning**, feedback utilisateurs. Un modèle de pointe sur des documents mal parsés ou des evals mal labellisées donne un **mauvais système**.

---

Quelles dimensions de contenu vérifier sur un jeu de données ?
?
- **Exactitude** des labels ou réponses.
- **Couverture** : tous les cas d'usage, langues, niveaux de difficulté.
- **Représentativité** par rapport au trafic réel.

---

Quelles dimensions d'hygiène et de conformité vérifier sur un jeu de données ?
?
- **Absence de doublons** et de fuites entre entraînement et test.
- **Fraîcheur** des données.
- **Conformité** : droits d'usage, PII, consentement.

---

Pourquoi et comment dédupliquer ?
?
Les doublons **surpondèrent** certains exemples, **gonflent** les scores d'eval (le même cas en train et en test) et gaspillent du calcul. On déduplique en **exact** (hash du texte normalisé), en **quasi-doublon** (MinHash / LSH sur les n-grammes) et en **sémantique** (similarité d'embeddings au-dessus d'un seuil).

---

Qu'est-ce qu'un bon guide d'annotation ?
?
- **Définitions** précises de chaque label, avec **exemples positifs et négatifs**.
- Traitement des **cas limites** et de l'**incertitude** (label « incertain » plutôt que forcer un choix).
- **Itéré** : on annote un pilote, on mesure le désaccord, on précise le guide, on recommence.

Un désaccord fréquent révèle souvent un **critère mal défini**, pas un mauvais annotateur.

---

Comment mesurer l'accord inter-annotateurs ?
?
Faire annoter un **même échantillon** par plusieurs personnes et calculer le **kappa de Cohen** (2 annotateurs) ou l'**alpha de Krippendorff** (plusieurs annotateurs, données manquantes). Ces mesures corrigent l'**accord dû au hasard**. Un accord humain faible fixe aussi un **plafond** : inutile d'exiger d'un [[95-llm-as-judge|juge LLM]] plus d'accord que les humains entre eux.

---

Qui doit annoter ?
?
- **Experts métier** pour les critères qui exigent de la compétence (médical, juridique, code) — chers mais indispensables sur le jeu d'eval de référence.
- **Annotateurs formés** (internes ou prestataires) pour les volumes.
- **LLM** pré-annotant, **humains qui valident** : accélère fortement mais introduit le biais du modèle (les humains tendent à accepter la proposition).

---

Qu'est-ce que l'active learning appliqué aux LLM ?
?
Faire annoter en priorité les exemples **les plus informatifs** : ceux où le système est **incertain**, où les juges **divergent**, où l'utilisateur a donné un **feedback négatif**, ou qui sont **sous-représentés**. On obtient plus de valeur par heure d'annotation qu'avec un échantillon aléatoire.

---

Pourquoi faut-il séparer strictement les jeux de développement et de test ?
?
Si l'on ajuste prompts, few-shot ou fine-tuning en regardant le jeu de test, celui-ci devient un **jeu d'entraînement déguisé** : les scores **surestiment** la performance réelle. On itère sur un **jeu de dev**, on ne consulte le **jeu de test** que pour les décisions finales, et on le **renouvelle** périodiquement.

---

Quelles données de production faut-il collecter dès le lancement ?
?
Les **traces complètes** (entrées, contexte récupéré, appels d'outils, sorties, versions de prompt et de modèle), les **feedbacks** et les **corrections**, avec **identifiant de trace** commun — dans le respect de la [[152-pii-confidentialite|confidentialité]]. Sans elles, impossible de construire les evals et la [[153-data-flywheel-versioning|flywheel]].

---

Comment préparer des données pour un fine-tuning ?
?
- Format **conversationnel** identique à celui de l'inférence (même [[132-tokenisation|chat template]], mêmes outils).
- **Qualité > quantité** : quelques centaines à quelques milliers d'exemples excellents suffisent souvent en SFT.
- **Diversité** des cas, y compris refus et abstentions souhaités.
- Retrait des **PII**, déduplication, **jeu de validation** séparé.

---

## Mises en situation

Mise en situation : deux annotateurs sont en désaccord sur un tiers des cas de ton jeu d'eval. Que fais-tu ?
?
1. **Ne pas blâmer les annotateurs** : un désaccord fréquent révèle surtout un **critère mal défini**
2. **Mesurer** l'accord avec une métrique qui corrige le hasard (kappa), plutôt qu'un pourcentage brut
3. **Reprendre le guide** : définitions, exemples positifs et négatifs, traitement des cas limites, option « incertain »
4. **Ré-annoter un pilote** et vérifier que l'accord remonte
5. **En tirer une borne** : un juge automatique ne peut pas faire mieux que l'accord humain ([[95-llm-as-judge|juge]])

**Piège** : trancher les désaccords soi-même et figer un jeu d'eval dont les critères restent flous.

---

Mise en situation : tu disposes de 40 heures d'expert métier pour annoter. Comment les emploies-tu au mieux ?
?
1. **Ne pas tirer au hasard** : privilégier les exemples les plus informatifs
2. **Cibler** les cas où le système est incertain, où les juges divergent, où les utilisateurs ont signalé un problème
3. **Couvrir les segments sous-représentés**, pour éviter un jeu d'eval qui ignore des pans du trafic
4. **Pré-annoter avec un LLM** et faire valider, en sachant que cela biaise vers l'acceptation
5. **Protéger le jeu de test** : itérer sur un jeu de dev, ne consulter le test que pour les décisions finales

**Piège** : dépenser l'expertise sur des cas faciles que le système traite déjà bien.

---

## Connexions
- [[94-evals-methodologie|Méthodologie d'évaluation]] — le golden dataset
- [[53-donnees-synthetiques-distillation|Données synthétiques]] — compléter les données réelles
- [[152-pii-confidentialite|PII & confidentialité]] — protéger les données
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — faire vivre les données
- [[51-fine-tuning-adaptation|Fine-tuning]] — l'usage d'entraînement
- [[95-llm-as-judge|LLM-as-a-judge]] — labels automatiques à valider
- [[00-moc-ai-engineering|MOC AI Engineering]]
