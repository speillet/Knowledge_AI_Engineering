# Données : curation & annotation — Flashcards
Tags: #flashcards #ai-engineering #donnees #annotation #qualite
<!-- summary: dimensions de qualité, déduplication, guide d'annotation, accord inter-annotateurs, qui annote, active learning, séparation dev et test, données de production, préparation d'un fine-tuning. -->


Pourquoi les données restent-elles décisives à l'ère des LLM pré-entraînés ? <!--anki:7a61323b38504268346f-->
?
Parce que la **différenciation** d'une application vient de ses données : documents du RAG, **jeux d'eval**, exemples few-shot, données de **fine-tuning**, feedback utilisateurs. Un modèle de pointe sur des documents mal parsés ou des evals mal labellisées donne un **mauvais système**.

---

Quelles dimensions de contenu vérifier sur un jeu de données ? <!--anki:473b29623d24767e4a36-->
?
- **Exactitude** des labels ou réponses.
- **Couverture** : tous les cas d'usage, langues, niveaux de difficulté.
- **Représentativité** par rapport au trafic réel.

Vérifier un échantillon par segment plutôt que seulement une moyenne globale. Un corpus exact mais limité aux demandes faciles n'apprend ni ne mesure correctement les exceptions. Écrire un guide d'annotation, examiner les désaccords et conserver des exemples difficiles ; la référence peut elle-même être ambiguë ou erronée.

---

Quelles dimensions d'hygiène et de conformité vérifier sur un jeu de données ? <!--anki:427675662e7457574a7c-->
?
- **Absence de doublons** et de fuites entre entraînement et test.
- **Fraîcheur** des données.
- **Conformité** : droits d'usage, PII, consentement.

Dédupliquer aussi les paraphrases et documents issus d'une même source avant de séparer entraînement et test. Tracer provenance, licence, finalité et base légale applicable ; le consentement n'est pas l'unique base possible. Définir mises à jour et effacement, car un jeu conforme et pertinent à sa création peut cesser de l'être.

---

Pourquoi et comment dédupliquer un jeu de données d'entraînement ou d'eval ? <!--anki:733b53586434355f6835-->
?
Les doublons **surpondèrent** certains exemples, **gonflent** les scores d'eval (le même cas en train et en test) et gaspillent du calcul. On déduplique en **exact** (hash du texte normalisé), en **quasi-doublon** (MinHash / LSH sur les n-grammes) et en **sémantique** (similarité d'embeddings au-dessus d'un seuil).

---

Qu'est-ce qu'un bon guide d'annotation ? <!--anki:716b3a504a62423d5e4b-->
?
- **Définitions** précises de chaque label, avec **exemples positifs et négatifs**.
- Traitement des **cas limites** et de l'**incertitude** (label « incertain » plutôt que forcer un choix).
- **Itéré** : on annote un pilote, on mesure le désaccord, on précise le guide, on recommence.

Un désaccord fréquent révèle souvent un **critère mal défini**, pas un mauvais annotateur.

---

Comment mesurer l'accord inter-annotateurs ? <!--anki:416b7945232c3f326648-->
?
Faire annoter un **même échantillon** par plusieurs personnes et calculer le **kappa de Cohen** (2 annotateurs) ou l'**alpha de Krippendorff** (plusieurs annotateurs, données manquantes). Ces mesures corrigent l'**accord dû au hasard**. Un accord humain faible fixe aussi un **plafond** : inutile d'exiger d'un [[95-llm-as-judge|juge LLM]] plus d'accord que les humains entre eux.

---

Qui doit annoter les données d'un projet LLM ? <!--anki:655759474a3971454429-->
?
- **Experts métier** pour les critères qui exigent de la compétence (médical, juridique, code) — chers mais indispensables sur le jeu d'eval de référence.
- **Annotateurs formés** (internes ou prestataires) pour les volumes.
- **LLM** pré-annotant, **humains qui valident** : accélère fortement mais introduit le biais du modèle (les humains tendent à accepter la proposition).

---

Qu'est-ce que l'active learning appliqué aux LLM ? <!--anki:797d785a307d35426a60-->
?
Faire annoter en priorité les exemples **les plus informatifs** : ceux où le système est **incertain**, où les juges **divergent**, où l'utilisateur a donné un **feedback négatif**, ou qui sont **sous-représentés**. On obtient plus de valeur par heure d'annotation qu'avec un échantillon aléatoire.

---

Pourquoi faut-il séparer strictement les jeux de développement et de test ? <!--anki:622f5d2e6a734231353e-->
?
Si l'on ajuste prompts, few-shot ou fine-tuning en regardant le jeu de test, celui-ci devient un **jeu d'entraînement déguisé** : les scores **surestiment** la performance réelle. On itère sur un **jeu de dev**, on ne consulte le **jeu de test** que pour les décisions finales, et on le **renouvelle** périodiquement.

---

Quelles données de production faut-il collecter dès le lancement ? <!--anki:77423d7b6a6a503e387d-->
?
Les **traces complètes** (entrées, contexte récupéré, appels d'outils, sorties, versions de prompt et de modèle), les **feedbacks** et les **corrections**, avec **identifiant de trace** commun — dans le respect de la [[152-pii-confidentialite|confidentialité]]. Sans elles, impossible de construire les evals et la [[153-data-flywheel-versioning|flywheel]].

---

Comment préparer des données pour un fine-tuning ? <!--anki:46607e4c3f4754636c5a-->
?
- Format **conversationnel** identique à celui de l'inférence (même [[132-tokenisation|chat template]], mêmes outils).
- **Qualité > quantité** : quelques centaines à quelques milliers d'exemples excellents suffisent souvent en SFT.
- **Diversité** des cas, y compris refus et abstentions souhaités.
- Retrait des **PII**, déduplication, **jeu de validation** séparé.

---

Calcul : combien coûte l'annotation de 2 000 exemples par des experts ? <!--anki:3334646132633937623364663461373839383536306436313733656235646261-->
?
Hypothèses : 3 minutes par exemple, expert à 80 €/h, double annotation de 20 % des exemples pour mesurer l'accord.
```text
annotation    : 2 000 × 3 min = 100 h × 80 €/h = 8 000 €
double (20 %) :   400 × 3 min =  20 h × 80 €/h = 1 600 €
total                                          ≈ 9 600 €, plus le guide d'annotation
```
C'est le prix d'un jeu d'eval de référence fiable : on réserve les experts aux cas où l'expertise compte, et on passe par des annotateurs formés ou un LLM pré-annotant pour le volume ([[94-evals-methodologie|golden dataset]]).

---

## Mises en situation

Mise en situation : deux annotateurs sont en désaccord sur un tiers des cas de ton jeu d'eval. Que fais-tu ? <!--anki:7868723a7777786f4966-->
?
1. **Ne pas blâmer les annotateurs** : un désaccord fréquent révèle surtout un **critère mal défini**
2. **Mesurer** l'accord avec une métrique qui corrige le hasard (kappa), plutôt qu'un pourcentage brut
3. **Reprendre le guide** : définitions, exemples positifs et négatifs, traitement des cas limites, option « incertain »
4. **Ré-annoter un pilote** et vérifier que l'accord remonte
5. **En tirer une borne** : un juge automatique ne peut pas faire mieux que l'accord humain ([[95-llm-as-judge|juge]])

**Piège** : trancher les désaccords soi-même et figer un jeu d'eval dont les critères restent flous.

---

Mise en situation : tu disposes de 40 heures d'expert métier pour annoter. Comment les emploies-tu au mieux ? <!--anki:6b4b4c7930443c425326-->
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
- [[156-ia-responsable|IA responsable]] — biais, équité et transparence
- [[00-moc-ai-engineering|MOC AI Engineering]]
