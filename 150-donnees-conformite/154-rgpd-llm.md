# RGPD appliqué aux LLM — Flashcards
Tags: #flashcards #ai-engineering #rgpd #conformite #donnees
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: champ d'application, RGPD ou AI Act, principes, base légale de la réutilisation, responsable et sous-traitant, transferts hors UE, droit à l'effacement, AIPD, décisions automatisées, données dans le modèle, mesures concrètes. -->


Quand le RGPD s'applique-t-il à une application LLM ? <!--anki:75213c515379246a5375-->
?
Le RGPD concerne les **traitements de données personnelles entrant dans son champ territorial**, notamment dans le cadre d'un établissement dans l'UE, ou pour offrir des biens/services à des personnes dans l'UE ou suivre leur comportement. La nationalité seule ne décide pas de son application.

Prompts, documents RAG, traces et jeux d'entraînement peuvent identifier directement ou indirectement des personnes. Vérifier les données effectivement traitées et les rôles des acteurs ; le simple recours à un LLM ne suffit pas à qualifier chaque traitement.

---

Quels principes du RGPD encadrent la collecte et l'usage des données d'un système LLM ? <!--anki:7437656f6f2d723b2a49-->
?
- **Licéité** : une **base légale** pour chaque finalité.
- **Limitation des finalités** : les données collectées pour le support ne servent pas d'office à l'entraînement.
- **Minimisation** : n'envoyer au modèle que le nécessaire.

---

Quels principes du RGPD encadrent la qualité et la conservation des données d'un système LLM ? <!--anki:753340264b2d61287d4a-->
?
- **Exactitude** : un modèle qui **hallucine** des informations sur une personne pose problème.
- **Limitation de la conservation** : rétention des logs, caches et mémoire.
- **Sécurité** et **responsabilité** : pouvoir démontrer sa conformité.

---

Quelle base légale pour réutiliser des conversations afin d'améliorer le système ? <!--anki:6c753e692a2176406975-->
?
Définir d'abord la **finalité de réutilisation** et vérifier sa compatibilité avec la collecte initiale. Selon les circonstances, une base comme l'intérêt légitime peut demander une mise en balance documentée et un droit d'opposition ; un consentement doit être valable et révocable.

Informer les personnes, limiter les données et fixer leur conservation. Une option de retrait ne remplace pas une base légale, et le consentement ne se présume pas de l'usage du chatbot. Les données sensibles et les changements de finalité demandent une analyse spécifique.

---

Qui est responsable de traitement et qui est sous-traitant ? <!--anki:4a3170492e452a56653b-->
?
En général, l'**entreprise qui déploie** l'application est **responsable de traitement** ; le **fournisseur d'API** de modèle est **sous-traitant** (article 28) s'il traite les données uniquement pour son compte, d'où la nécessité d'un **DPA**. S'il réutilise les données pour ses propres fins (entraînement), il peut devenir **responsable** pour cette partie.

---

Quels problèmes posent les transferts hors UE ? <!--anki:77264354606a562d344b-->
?
Un transfert de données personnelles vers un pays tiers doit respecter le **chapitre V du RGPD** : décision d'adéquation applicable, garanties appropriées comme les clauses contractuelles types, ou dérogation encadrée. Selon le mécanisme, analyser le droit local et les mesures complémentaires nécessaires.

Une région d'hébergement dans l'UE ne suffit pas toujours : examiner accès d'administration depuis l'étranger et sous-traitants ultérieurs. Vérifier le statut et le périmètre de toute certification invoquée. L'auto-hébergement peut réduire certains transferts, sans supprimer les autres obligations du RGPD.

---

Comment gérer le droit à l'effacement dans un système LLM ? <!--anki:6f356c3f4c75294a4d3f-->
?
Qualifier la demande et les **conditions ou exceptions du droit à l'effacement**, puis localiser les données : sources, index, mémoire, caches, traces, jeux d'entraînement et dérivés. Propager les suppressions nécessaires et documenter le traitement des sauvegardes et obligations de conservation.

Pour les poids d'un modèle, ne pas promettre une suppression ciblée sans preuve : les techniques d'unlearning n'offrent pas une garantie générale. Évaluer les mesures adaptées avec le responsable de traitement, éventuellement le réentraînement, et vérifier le risque de restitution. Prévenir le problème par minimisation et traçabilité dès la collecte.

---

Quand faut-il une analyse d'impact (AIPD / DPIA) ? <!--anki:6c6a3239587567735849-->
?
Quand le traitement présente un **risque élevé** pour les personnes : **nouvelles technologies** (l'IA générative en fait souvent partie), **évaluation ou profilage**, données **sensibles** (santé, opinions), **surveillance** de salariés, **grande échelle**. L'AIPD documente risques et mesures, et s'articule avec les évaluations exigées par l'[[155-ai-act|AI Act]].

---

Que dit le RGPD sur les décisions automatisées ? <!--anki:7460602e37623c3b6d6c-->
?
L'**article 22** donne le droit de ne pas faire l'objet d'une décision **fondée exclusivement** sur un traitement automatisé produisant des **effets juridiques ou significatifs** (refus de crédit, rejet de candidature), sauf exceptions encadrées. Il faut une **intervention humaine réelle**, la possibilité de **contester** et une **information** sur la logique du traitement.

---

Le modèle lui-même contient-il des données personnelles ? <!--anki:79743c65434234557449-->
?
C'est **débattu**. Le Comité européen de la protection des données (avis de décembre 2024) considère qu'un modèle entraîné sur des données personnelles **n'est pas automatiquement anonyme** : il faut démontrer au cas par cas que l'**extraction** de données personnelles est improbable. Cela concerne surtout ceux qui **entraînent** ou **fine-tunent** des modèles.

---

Quelles mesures de conformité documentaires prévoir pour une application LLM ? <!--anki:4c6c4e6a393956363c35-->
?
- **Registre** des traitements à jour : finalités, données, sous-traitants.
- **Information** des utilisateurs, dont l'usage d'une IA.
- **DPA** signés et localisation des données vérifiée chez les fournisseurs.

Préciser les bases légales, les destinataires, les durées et les modalités d'exercice des droits dans la documentation pertinente. Le contrat de sous-traitance doit correspondre aux traitements réellement effectués. Une localisation annoncée ne suffit pas : examiner aussi sous-traitants ultérieurs, accès distants et éventuels transferts.

---

Quelles mesures techniques prévoir pour une application LLM conforme ? <!--anki:4f7d30362d3d792e4139-->
?
- **Pseudonymisation** avant envoi au modèle quand c'est possible ([[152-pii-confidentialite|PII]]).
- **Rétention** configurée sur logs, traces, caches et mémoire.
- **Procédure d'exercice des droits** (accès, effacement) couvrant **tous** les stockages.

Associer ces mesures à des contrôles d'accès, du chiffrement et une cartographie des données dérivées. Tester effectivement l'effacement d'un utilisateur dans les index, sauvegardes et caches selon les règles de conservation applicables. La pseudonymisation reste réversible ou ré-identifiable dans certains contextes : elle ne fait pas automatiquement sortir du RGPD.

---

À ne pas confondre : RGPD et AI Act ? <!--anki:514e6a7064447d49545e-->
?
- **RGPD** : protège les **personnes** dont on traite les **données personnelles**. Il s'applique dès qu'une PII passe dans le système, quel que soit le niveau de risque de l'IA
- **AI Act** : encadre les **systèmes d'IA** selon leur **niveau de risque** (usages interdits, haut risque, transparence, GPAI), même sans donnée personnelle ([[155-ai-act|AI Act]])

Les deux se cumulent : un chatbot RH traitant des CV relève du **haut risque** de l'AI Act **et** du RGPD. L'AIPD du RGPD et l'analyse de risques de l'AI Act gagnent à être menées ensemble.

---

## Mises en situation

Mise en situation : un client exerce son droit à l'effacement. Tes données sont dans l'index RAG, la mémoire de l'agent, les traces, les caches et un modèle fine-tuné. Que réponds-tu ? <!--anki:782b47475664446d4a32-->
?
1. **Qualifier la demande** : identifier la personne, le périmètre et les exceptions légales éventuelles.
2. **Cartographier les copies** : sources, index, mémoire, traces, caches, sauvegardes et données d'entraînement.
3. **Propager l'effacement nécessaire** aux données et dérivés, en vérifiant qu'une ré-ingestion ne les recrée pas.
4. **Évaluer le modèle fine-tuné** : risque de restitution, moyens de correction et éventuel réentraînement ; ne pas prétendre retirer un fait des poids sans validation.
5. **Documenter et répondre** dans les délais applicables, avec une trace minimale des opérations.

**Piège** : supprimer la source mais conserver ses résumés ou promettre un effacement des poids techniquement non démontré.

---

Mise en situation : le métier veut automatiser le tri des candidatures, avec rejet automatique sous un certain score. Quelles obligations signales-tu ? <!--anki:48304b7469563d3c5345-->
?
1. **Décision automatisée** : le RGPD encadre les décisions produisant des effets significatifs, comme un rejet de candidature
2. **Intervention humaine réelle** : pas une validation de façade, avec possibilité de contester
3. **Information** sur la logique du traitement et les critères
4. **AI Act** : le recrutement relève des usages à haut risque, avec ses propres obligations ([[155-ai-act|AI Act]])
5. **Biais** : mesurer l'équité entre groupes, documenter et corriger ([[156-ia-responsable|IA responsable]])

**Piège** : considérer qu'un humain qui valide 200 rejets par jour constitue une intervention humaine réelle.

---

## Sources

- [CNIL — intérêt légitime pour développer un système d’IA](https://www.cnil.fr/fr/base-legale-interet-legitime-developpement-systeme)

- [CNIL — mise en conformité des systèmes d’IA avec le RGPD](https://www.cnil.fr/fr/intelligence-artificielle/ia-comment-etre-en-conformite-avec-le-rgpd)

- [Union européenne — règlement (UE) 2016/679, RGPD](https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra)
- [CNIL — ressources sur l’IA et les données personnelles](https://www.cnil.fr/fr/intelligence-artificielle)

## Connexions
- [[152-pii-confidentialite|PII & confidentialité]] — les mesures techniques
- [[155-ai-act|AI Act]] — le règlement spécifique à l'IA
- [[156-ia-responsable|IA responsable]] — équité et transparence
- [[39-memoire-agents|Mémoire des agents]] — oubli et suppression
- [[134-recherche-vectorielle-ann|Recherche vectorielle]] — suppression dans l'index
- [[163-voix-temps-reel|Voix & temps réel]] — agents vocaux et budget de latence
- [[00-moc-ai-engineering|MOC AI Engineering]]
