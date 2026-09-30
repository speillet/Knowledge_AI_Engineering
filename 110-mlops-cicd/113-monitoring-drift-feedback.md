# Monitoring, drift & boucle de feedback — Flashcards
Tags: #flashcards #ai-engineering #mlops #monitoring #drift #llm

À ne pas confondre : data drift et concept drift ?
?
- **Data drift** : la distribution des **entrées** change (nouveaux sujets, jargon)
- **Concept drift** : la **relation entrée → sortie attendue** change (le « bon » comportement évolue)

---

Comment le drift se manifeste-t-il sur une app LLM ?
?
Par une **dégradation silencieuse** : aucune erreur technique, mais des réponses de moins en moins pertinentes. Causes typiques :
- **Nouvelles questions** hors du périmètre prévu
- **Documents sources** qui changent
- **Modèle du fournisseur** mis à jour derrière un alias

Invisible sans **evals continues** sur des échantillons de production.

---

Comment monitorer la qualité en production ?
?
- **Scores sur échantillons** par un juge calibré ([[95-llm-as-judge|LLM-as-a-judge]])
- **Feedback utilisateur** explicite et implicite (reformulations, abandons)
- **Taux de refus** et d'**erreurs d'outils**
- **Validations automatiques** : format, citations présentes

Tout est rattaché aux [[91-langfuse-observabilite|traces]], et **segmenté** (par sujet, langue, client) : une moyenne stable peut cacher un segment qui s'effondre.

---

Qu'est-ce que la boucle de feedback ?
?
```text
traces prod → curation → golden datasets enrichis
→ evals plus fidèles → prompts/fine-tuning améliorés
```
Les données de production **nourrissent** l'amélioration continue.

---

Quand ré-entraîner ou re-fine-tuner ?
?
**Sur signal**, pas sur calendrier :
- Chute des scores sur un segment
- Drift des entrées détecté
- Nouveaux cas d'usage ou nouvelles catégories
- Nouveau modèle de base plus performant

Avant de ré-entraîner, vérifier que le problème ne se règle pas plus simplement : prompt, retrieval ou fraîcheur de l'index ([[51-fine-tuning-adaptation|fine-tuning]]).

---

Quel est l'équivalent du drift pour un système RAG ?
?
La **fraîcheur de l'index** : sans ré-ingestion continue, les réponses deviennent obsolètes même si le modèle n'a pas changé ([[22-rag-avance|RAG en prod]]).

---

Pourquoi les mises à jour des modèles API sont-elles un risque ?
?
Le provider **met à jour ou déprécie** les modèles : le comportement change sans commit chez vous → **épingler les versions** et re-jouer les evals à chaque changement.

---

Quel rôle pour l'humain dans la boucle de production ?
?
**Annoter des échantillons** et **revoir les cas limites** : l'humain reste la source de vérité. Ses annotations servent à la fois à mesurer la qualité, à **calibrer les juges automatiques** et à enrichir le golden dataset.

Pour tenir dans le temps : un volume fixe et régulier (par exemple 50 traces par semaine), choisi par échantillonnage plutôt qu'au hasard des signalements ([[151-donnees-curation-annotation|annotation]]).

---

Comment alerter sur la qualité ?
?
Comme sur la disponibilité : des **seuils** sur les scores de qualité, les taux de refus et d'erreurs, les latences, **par segment**, reliés aux [[64-metriques-slo-inference|SLO]].

Précautions : alerter sur une **tendance** (moyenne glissante sur plusieurs heures) plutôt que sur un point isolé, car les scores d'échantillons sont bruités, et joindre à l'alerte des **exemples de traces** pour diagnostiquer vite.

---

## Mises en situation

Mise en situation : ton assistant RH fonctionnait bien depuis six mois. Depuis trois semaines, les utilisateurs le trouvent « à côté de la plaque », sans qu'aucun déploiement n'ait eu lieu. Quelles causes explores-tu ?
?
1. **Drift des entrées** : de nouveaux sujets arrivent (réforme, nouvelle politique interne) et sortent du périmètre couvert
2. **Fraîcheur de l'index** : les documents ont changé, mais la ré-ingestion n'a pas suivi ([[22-rag-avance|RAG en prod]])
3. **Mise à jour côté fournisseur** : le modèle derrière l'alias a changé, sans commit chez toi
4. **Mesurer** : scores sur échantillon, taux de refus, feedback, segmentés par sujet
5. **Corriger puis prévenir** : épingler les versions, automatiser la ré-ingestion, alerter sur les scores par segment

**Piège** : conclure à une régression du modèle sans avoir regardé la fraîcheur des données.

---

Mise en situation : tu veux transformer les échecs de production en amélioration continue, sans y passer tes semaines. Comment organises-tu la boucle ?
?
1. **Capter** : feedback négatif, échecs de validation, faible confiance, escalades ([[93-monitoring-inference|signaux]])
2. **Échantillonner** plutôt que tout traiter, en priorisant les segments à fort volume ou à fort risque
3. **Annoter** un lot régulier avec un expert métier, ce qui calibre aussi les juges automatiques
4. **Verser** ces cas au golden dataset, en distinguant non-régression et cas durs ([[94-evals-methodologie|evals]])
5. **Déclencher les corrections sur signal**, pas au calendrier : prompt, retrieval, ou fine-tuning selon la cause

**Piège** : collecter du feedback sans jamais rien en faire, ce qui décourage les utilisateurs de le donner.

---

## Connexions
- [[91-langfuse-observabilite|Langfuse]] — traces, scores et datasets de prod
- [[92-chainforge-evals-prompts|Evals]] — les instruments de mesure
- [[112-cicd-modeles|CI/CD des modèles]] — redéployer après correction
- [[51-fine-tuning-adaptation|Fine-tuning]] — la réponse au drift comportemental
- [[22-rag-avance|RAG avancé]] — fraîcheur de l'index
- [[93-monitoring-inference|Monitoring de l'inférence]] — validations et signaux de qualité en production
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — SLO et métriques d'un agent
- [[153-data-flywheel-versioning|Data flywheel]] — boucler sur les échecs
- [[97-evals-online-ab-testing|Evals online]] — signaux de production
- [[00-moc-ai-engineering|MOC AI Engineering]]
