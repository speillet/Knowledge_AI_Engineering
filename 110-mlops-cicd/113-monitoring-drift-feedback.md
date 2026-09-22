# Monitoring, drift & boucle de feedback — Flashcards
Tags: #flashcards #ai-engineering #mlops #monitoring #drift #llm

Quelle différence entre data drift et concept drift ?
?
- **Data drift** : la distribution des **entrées** change (nouveaux sujets, jargon)
- **Concept drift** : la **relation entrée → sortie attendue** change (le « bon » comportement évolue)

---

Comment le drift se manifeste-t-il sur une app LLM ?
?
Par une **dégradation silencieuse** : requêtes hors distribution, réponses de moins en moins pertinentes — **invisible sans evals continues**.

---

Comment monitorer la qualité en production ?
?
**Scores sur échantillons** (LLM-as-judge), **feedback utilisateur**, taux de refus et d'erreurs d'outils — collectés dans les [[91-langfuse-observabilite|traces]].

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
**Sur signal**, pas sur calendrier : chute des scores, drift détecté, nouveaux cas d'usage ([[51-fine-tuning-adaptation|fine-tuning]]).

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
**Annotation d'échantillons, review des cas limites** : l'humain reste la source de vérité qui calibre les juges automatiques.

---

Comment alerter sur la qualité ?
?
Des **seuils sur les scores, refus et latences par segment**, reliés aux [[64-metriques-slo-inference|SLO]] — la qualité se surveille comme la disponibilité.

---

## Connexions
- [[91-langfuse-observabilite|Langfuse]] — traces, scores et datasets de prod
- [[92-chainforge-evals-prompts|Evals]] — les instruments de mesure
- [[112-cicd-modeles|CI/CD des modèles]] — redéployer après correction
- [[51-fine-tuning-adaptation|Fine-tuning]] — la réponse au drift comportemental
- [[22-rag-avance|RAG avancé]] — fraîcheur de l'index
- [[93-monitoring-inference|Monitoring de l'inférence]] — validations et signaux de qualité en production
- [[00-moc-ai-engineering|MOC AI Engineering]]
