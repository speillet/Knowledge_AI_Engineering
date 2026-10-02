# RGPD appliqué aux LLM — Flashcards
Tags: #flashcards #ai-engineering #rgpd #conformite #donnees
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Quand le RGPD s'applique-t-il à une application LLM ?
?
<!--anki:75213c515379246a5375-->
Dès qu'elle **traite des données personnelles** de personnes situées dans l'UE : prompts contenant des noms ou informations sur des personnes, documents RH ou clients indexés, logs liés à un compte utilisateur, données de fine-tuning. En pratique, **presque toujours**.

---

Quels principes du RGPD encadrent la collecte et l'usage des données d'un système LLM ?
?
<!--anki:7437656f6f2d723b2a49-->
- **Licéité** : une **base légale** pour chaque finalité.
- **Limitation des finalités** : les données collectées pour le support ne servent pas d'office à l'entraînement.
- **Minimisation** : n'envoyer au modèle que le nécessaire.

---

Quels principes du RGPD encadrent la qualité et la conservation des données d'un système LLM ?
?
<!--anki:753340264b2d61287d4a-->
- **Exactitude** : un modèle qui **hallucine** des informations sur une personne pose problème.
- **Limitation de la conservation** : rétention des logs, caches et mémoire.
- **Sécurité** et **responsabilité** : pouvoir démontrer sa conformité.

---

Quelle base légale pour réutiliser des conversations afin d'améliorer le système ?
?
<!--anki:6c753e692a2176406975-->
Selon le contexte, l'**intérêt légitime** (avec mise en balance et droit d'opposition simple) ou le **consentement**. Il faut **informer** clairement les utilisateurs, **minimiser** (pseudonymiser, filtrer) et proposer un **opt-out**. Réutiliser des données pour entraîner un modèle est une **finalité distincte** du service rendu.

---

Qui est responsable de traitement et qui est sous-traitant ?
?
<!--anki:4a3170492e452a56653b-->
En général, l'**entreprise qui déploie** l'application est **responsable de traitement** ; le **fournisseur d'API** de modèle est **sous-traitant** (article 28) s'il traite les données uniquement pour son compte, d'où la nécessité d'un **DPA**. S'il réutilise les données pour ses propres fins (entraînement), il peut devenir **responsable** pour cette partie.

---

Quels problèmes posent les transferts hors UE ?
?
<!--anki:77264354606a562d344b-->
Envoyer des données à un fournisseur hors UE est un **transfert** qui exige un cadre : **décision d'adéquation** (ex. Data Privacy Framework UE–États-Unis pour les entreprises certifiées), ou **clauses contractuelles types** avec analyse d'impact du transfert. Solutions pratiques : **régions de traitement UE**, modèles **hébergés en UE** ou **on-prem**.

---

Comment gérer le droit à l'effacement dans un système LLM ?
?
<!--anki:6f356c3f4c75294a4d3f-->
- **RAG, mémoire, caches, logs** : supprimables si l'on sait **où** sont les données (index par personne, métadonnées de source) → suppression propagée et **ré-indexation**.
- **Poids d'un modèle fine-tuné** : on ne sait pas « retirer » une donnée de façon fiable (le **machine unlearning** reste immature) → ne pas fine-tuner sur des données personnelles, ou prévoir de **ré-entraîner** sans elles.

---

Quand faut-il une analyse d'impact (AIPD / DPIA) ?
?
<!--anki:6c6a3239587567735849-->
Quand le traitement présente un **risque élevé** pour les personnes : **nouvelles technologies** (l'IA générative en fait souvent partie), **évaluation ou profilage**, données **sensibles** (santé, opinions), **surveillance** de salariés, **grande échelle**. L'AIPD documente risques et mesures, et s'articule avec les évaluations exigées par l'[[155-ai-act|AI Act]].

---

Que dit le RGPD sur les décisions automatisées ?
?
<!--anki:7460602e37623c3b6d6c-->
L'**article 22** donne le droit de ne pas faire l'objet d'une décision **fondée exclusivement** sur un traitement automatisé produisant des **effets juridiques ou significatifs** (refus de crédit, rejet de candidature), sauf exceptions encadrées. Il faut une **intervention humaine réelle**, la possibilité de **contester** et une **information** sur la logique du traitement.

---

Le modèle lui-même contient-il des données personnelles ?
?
<!--anki:79743c65434234557449-->
C'est **débattu**. Le Comité européen de la protection des données (avis de décembre 2024) considère qu'un modèle entraîné sur des données personnelles **n'est pas automatiquement anonyme** : il faut démontrer au cas par cas que l'**extraction** de données personnelles est improbable. Cela concerne surtout ceux qui **entraînent** ou **fine-tunent** des modèles.

---

Quelles mesures de conformité documentaires prévoir pour une application LLM ?
?
<!--anki:4c6c4e6a393956363c35-->
- **Registre** des traitements à jour : finalités, données, sous-traitants.
- **Information** des utilisateurs, dont l'usage d'une IA.
- **DPA** signés et localisation des données vérifiée chez les fournisseurs.

---

Quelles mesures techniques prévoir pour une application LLM conforme ?
?
<!--anki:4f7d30362d3d792e4139-->
- **Pseudonymisation** avant envoi au modèle quand c'est possible ([[152-pii-confidentialite|PII]]).
- **Rétention** configurée sur logs, traces, caches et mémoire.
- **Procédure d'exercice des droits** (accès, effacement) couvrant **tous** les stockages.

---

À ne pas confondre : RGPD et AI Act ?
?
<!--anki:514e6a7064447d49545e-->
- **RGPD** : protège les **personnes** dont on traite les **données personnelles**. Il s'applique dès qu'une PII passe dans le système, quel que soit le niveau de risque de l'IA
- **AI Act** : encadre les **systèmes d'IA** selon leur **niveau de risque** (usages interdits, haut risque, transparence, GPAI), même sans donnée personnelle ([[155-ai-act|AI Act]])

Les deux se cumulent : un chatbot RH traitant des CV relève du **haut risque** de l'AI Act **et** du RGPD. L'AIPD du RGPD et l'analyse de risques de l'AI Act gagnent à être menées ensemble.

---

## Mises en situation

Mise en situation : un client exerce son droit à l'effacement. Tes données sont dans l'index RAG, la mémoire de l'agent, les traces, les caches et un modèle fine-tuné. Que réponds-tu ?
?
<!--anki:782b47475664446d4a32-->
1. **Les stockages identifiables** : index, mémoire, traces et caches se purgent si l'on sait où sont les données (métadonnées de source, index par personne)
2. **Propager** : suppression puis ré-indexation, y compris des structures dérivées (résumés, souvenirs consolidés)
3. **Le modèle fine-tuné** est le vrai problème : on ne sait pas retirer une donnée des poids de façon fiable
4. **La bonne pratique** est préventive : ne pas fine-tuner sur des données personnelles, ou prévoir un ré-entraînement sans elles
5. **Tracer** la suppression effectuée, sans conserver les données supprimées

**Piège** : promettre un effacement complet alors que les données ont servi à entraîner un modèle en production.

---

Mise en situation : le métier veut automatiser le tri des candidatures, avec rejet automatique sous un certain score. Quelles obligations signales-tu ?
?
<!--anki:48304b7469563d3c5345-->
1. **Décision automatisée** : le RGPD encadre les décisions produisant des effets significatifs, comme un rejet de candidature
2. **Intervention humaine réelle** : pas une validation de façade, avec possibilité de contester
3. **Information** sur la logique du traitement et les critères
4. **AI Act** : le recrutement relève des usages à haut risque, avec ses propres obligations ([[155-ai-act|AI Act]])
5. **Biais** : mesurer l'équité entre groupes, documenter et corriger ([[156-ia-responsable|IA responsable]])

**Piège** : considérer qu'un humain qui valide 200 rejets par jour constitue une intervention humaine réelle.

---

## Connexions
- [[152-pii-confidentialite|PII & confidentialité]] — les mesures techniques
- [[155-ai-act|AI Act]] — le règlement spécifique à l'IA
- [[156-ia-responsable|IA responsable]] — équité et transparence
- [[39-memoire-agents|Mémoire des agents]] — oubli et suppression
- [[134-recherche-vectorielle-ann|Recherche vectorielle]] — suppression dans l'index
- [[163-voix-temps-reel|Voix & temps réel]] — agents vocaux et budget de latence
- [[00-moc-ai-engineering|MOC AI Engineering]]
