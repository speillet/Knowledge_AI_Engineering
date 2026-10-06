# Monitoring, drift & boucle de feedback — Flashcards
Tags: #flashcards #ai-engineering #mlops #monitoring #drift #llm
<!-- summary: data drift et concept drift, drift d'une app LLM et d'un RAG, qualité en production, boucle de feedback, quand ré-entraîner, annotation régulière, mises à jour des modèles API, alertes sur tendance et par segment. -->


À ne pas confondre : data drift et concept drift ? <!--anki:693a4558422d7246257a-->
?
- **Data drift** : la distribution des **entrées** change (nouveaux sujets, jargon)
- **Concept drift** : la **relation entrée → sortie attendue** change (le « bon » comportement évolue)

Exemple de data drift : davantage de demandes dans une nouvelle langue. Exemple de concept drift : une règle commerciale change et une ancienne réponse correcte devient fausse. Une distribution d'entrée stable n'exclut donc pas une baisse de qualité. Mesurer les deux séparément et rechercher la cause avant de modifier ou réentraîner le modèle.

---

Comment le drift se manifeste-t-il sur une app LLM ? <!--anki:4477547a5d582b2a403a-->
?
Par une **dégradation silencieuse** : aucune erreur technique, mais des réponses de moins en moins pertinentes. Causes typiques :
- **Nouvelles questions** hors du périmètre prévu
- **Documents sources** qui changent
- **Modèle du fournisseur** mis à jour derrière un alias

Invisible sans **evals continues** sur des échantillons de production.

---

Comment monitorer la qualité d'une application LLM en production ? <!--anki:786d2e5876493b586624-->
?
- **Scores sur échantillons** par un juge calibré ([[95-llm-as-judge|LLM-as-a-judge]])
- **Feedback utilisateur** explicite et implicite (reformulations, abandons)
- **Taux de refus** et d'**erreurs d'outils**
- **Validations automatiques** : format, citations présentes

Tout est rattaché aux [[91-langfuse-observabilite|traces]], et **segmenté** (par sujet, langue, client) : une moyenne stable peut cacher un segment qui s'effondre.

---

Qu'est-ce que la boucle de feedback d'une application LLM ? <!--anki:7568493c4c666036326e-->
?
```text
traces prod → curation → golden datasets enrichis
→ evals plus fidèles → prompts/fine-tuning améliorés
```
Les données de production **nourrissent** l'amélioration continue.

La **curation** transforme un signal brut en exemple exploitable : vérifier l'erreur, enlever les données inutiles, produire une référence et choisir le bon jeu. Garder un test indépendant évite d'optimiser uniquement les incidents déjà vus. Mesurer après déploiement si la correction améliore réellement l'usage sans dégrader d'autres segments.

---

Quand réentraîner ou fine-tuner à nouveau un modèle en production ? <!--anki:69216450773565735339-->
?
**Sur signal**, pas sur calendrier :
- Chute des scores sur un segment
- Drift des entrées détecté
- Nouveaux cas d'usage ou nouvelles catégories
- Nouveau modèle de base plus performant

Avant de ré-entraîner, vérifier que le problème ne se règle pas plus simplement : prompt, retrieval ou fraîcheur de l'index ([[51-fine-tuning-adaptation|fine-tuning]]).

---

Quel est l'équivalent du drift pour un système RAG ? <!--anki:623f3a36415d4739725d-->
?
Un RAG peut dériver à plusieurs niveaux : **sources obsolètes**, index mal synchronisé, changement des questions, permissions modifiées ou perte de rappel après changement d'embeddings. La fraîcheur est donc une cause de dérive, pas son unique équivalent.

Suivre dates d'ingestion, suppressions, couverture des questions et qualité des passages récupérés. Si la bonne source existe mais n'est plus retrouvée, ré-ingérer davantage ne suffit pas : vérifier index, filtres, découpage et modèle de recherche ([[22-rag-avance|RAG en production]]).

---

Pourquoi les mises à jour des modèles API sont-elles un risque ? <!--anki:4a50656f363156493461-->
?
Le provider **met à jour ou déprécie** les modèles : le comportement change sans commit chez vous → **épingler les versions** et re-jouer les evals à chaque changement.

Un alias stable peut pointer vers une version différente, et un identifiant daté peut finir par être retiré. Maintenir une procédure de migration : comparer sur le même jeu d'evals, vérifier formats et outils, déployer progressivement et prévoir une solution de repli. L'épinglage réduit les changements implicites sans supprimer les dépréciations.

---

Quel rôle pour l'humain dans la boucle de production ? <!--anki:695e2a5b4b652e41353c-->
?
**Annoter des échantillons** et **revoir les cas limites** : l'humain reste la source de vérité. Ses annotations servent à la fois à mesurer la qualité, à **calibrer les juges automatiques** et à enrichir le golden dataset.

Pour tenir dans le temps : un volume fixe et régulier (par exemple 50 traces par semaine), choisi par échantillonnage plutôt qu'au hasard des signalements ([[151-donnees-curation-annotation|annotation]]).

---

Comment alerter sur une baisse de qualité d'une application LLM en production ? <!--anki:724b5141763b4c37746b-->
?
Comme sur la disponibilité : des **seuils** sur les scores de qualité, les taux de refus et d'erreurs, les latences, **par segment**, reliés aux [[64-metriques-slo-inference|SLO]].

Précautions : alerter sur une **tendance** (moyenne glissante sur plusieurs heures) plutôt que sur un point isolé, car les scores d'échantillons sont bruités, et joindre à l'alerte des **exemples de traces** pour diagnostiquer vite.

---

## Mises en situation

Mise en situation : ton assistant RH fonctionnait bien depuis six mois. Depuis trois semaines, les utilisateurs le trouvent « à côté de la plaque », sans qu'aucun déploiement n'ait eu lieu. Quelles causes explores-tu ? <!--anki:433d3b33593952674f29-->
?
1. **Drift des entrées** : de nouveaux sujets arrivent (réforme, nouvelle politique interne) et sortent du périmètre couvert
2. **Fraîcheur de l'index** : les documents ont changé, mais la ré-ingestion n'a pas suivi ([[22-rag-avance|RAG en prod]])
3. **Mise à jour côté fournisseur** : le modèle derrière l'alias a changé, sans commit chez toi
4. **Mesurer** : scores sur échantillon, taux de refus, feedback, segmentés par sujet
5. **Corriger puis prévenir** : épingler les versions, automatiser la ré-ingestion, alerter sur les scores par segment

**Piège** : conclure à une régression du modèle sans avoir regardé la fraîcheur des données.

---

Mise en situation : tu veux transformer les échecs de production en amélioration continue, sans y passer tes semaines. Comment organises-tu la boucle ? <!--anki:7732497b69286a71417d-->
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
- [[111-mlops-llmops-fondamentaux|MLOps & LLMOps]] — cycle de vie et versioning des systèmes LLM
- [[114-reproductibilite-variance|Reproductibilité & variance]] — non-déterminisme et statistiques d'evals
- [[157-contrats-qualite-donnees|Qualité opérationnelle]] — distinguer incident de données et dérive réelle
- [[159-donnees-temporelles-features|Données temporelles]] — interpréter les retards et labels incomplets
- [[00-moc-ai-engineering|MOC AI Engineering]]
