# Cas de system design LLM — Flashcards
Tags: #flashcards #ai-engineering #system-design #entretien #llm

Cas 1 — Assistant de support client : par quoi passe la requête ?
?
1. **Classification d'intention** (petit modèle) : question, action sur compte, réclamation, hors périmètre.
2. **RAG** sur la base de connaissances (hybride + reranker), filtré par produit et langue.
3. **Outils en lecture** (statut de commande) via API authentifiée **au nom du client**.

---

Cas 1 — Assistant de support client : comment encadre-t-on la réponse ?
?
1. Génération avec **citations** et **abstention**.
2. **Escalade** vers un humain avec résumé de la conversation.
3. Evals : taux de **résolution sans humain**, faithfulness, CSAT.

---

Cas 1 — Quels risques spécifiques au support client ?
?
- **Engagements inventés** (remboursement promis à tort) → le modèle n'a **pas le droit** de promettre ; les actions passent par des outils avec règles métier.
- **Prompt injection** par le message client ou un ticket.
- **Fuite de données** d'un autre client → filtre d'identité **côté serveur**.
- **Ton** inadapté sur un client en colère → détection et escalade.

---

Cas 2 — Recherche documentaire interne (« chat avec nos documents ») : les points durs ?
?
- **Droits d'accès** : chaque chunk porte les **ACL** du document source, filtrées au retrieval selon l'utilisateur (jamais « tout indexer puis demander au modèle de filtrer »).
- **Ingestion hétérogène** : PDF, slides, tableaux, wikis → [[162-document-parsing|parsing de documents]].
- **Fraîcheur** : synchronisation incrémentale, suppression propagée.
- **Documents contradictoires ou obsolètes** : métadonnées de date, priorité aux sources de référence.

---

Cas 3 — Assistant de code intégré à l'IDE : quelles contraintes ?
?
- **Autocomplétion** : latence **< 200-300 ms** → petit modèle spécialisé (fill-in-the-middle), cache, annulation des requêtes obsolètes.
- **Chat / agent** : modèle fort, **contexte** construit à partir du dépôt (fichiers ouverts, recherche de symboles, index du code).
- Sécurité : **secrets** exclus du contexte, exécution en **sandbox**, revue des changements ([[106-securite-agents-code|agents de code]]).
- Métrique clé : **taux d'acceptation** et code conservé à J+N.

---

Cas 4 — Extraction de données de millions de documents : quel design ?
?
- Traitement **asynchrone en batch** (batch API ou GPU self-hosted à pleine charge) — la latence ne compte pas, le **coût** oui.
- **Structured outputs** + validation par schéma et règles.
- **Petit modèle** fine-tuné ou distillé si le volume le justifie ([[53-donnees-synthetiques-distillation|distillation]]).
- **Échantillonnage** et relecture humaine pour mesurer la précision, **file d'exceptions** pour les cas à faible confiance.
- Idempotence et reprise sur erreur.

---

Cas 5 — Agent qui effectue des actions (réservations, tickets, opérations) : que faut-il ajouter ?
?
- **Outils à permissions minimales**, identité **déléguée** de l'utilisateur.
- **Confirmation humaine** pour les actions irréversibles ou coûteuses.
- **Limites** : étapes, budget, montant maximal.
- **Journal d'audit** complet et **kill switch**.
- Environnement d'**eval en sandbox** avant production ([[115-plateformes-agents-gouvernance|gouvernance]], [[103-defenses-agents|défenses]]).

---

Cas 6 — Chatbot grand public à fort trafic : priorités de coût ?
?
- **Routage** : la majorité des messages vers un **petit modèle**, les difficiles vers un gros ([[82-routing-llm|routing]]).
- **Prompt caching** du system prompt, **cache sémantique** des questions fréquentes.
- **Limites** de longueur d'historique (résumé glissant).
- **Quotas par utilisateur** contre les abus (denial of wallet).
- Modération en entrée et sortie à coût minimal (classifieur léger).

---

Cas 7 — Assistant vocal temps réel : quelles contraintes dominent ?
?
La **latence de bout en bout** (< 1 s ressentie) : pipeline **STT → LLM → TTS** en streaming à chaque étape, ou modèle **speech-to-speech** natif ; détection de fin de parole et **gestion des interruptions** (barge-in). Réponses **courtes** et sans markdown ([[163-voix-temps-reel|voix temps réel]]).

---

Quelle est la première moitié de la trame de réponse en system design ?
?
1. **Clarifier** besoin et contraintes, **chiffrer** la charge.
2. **Baseline simple** + critères de succès mesurables.
3. **Architecture** (schéma) et **flux** d'une requête.
4. **Données** : ingestion, fraîcheur, accès.

---

Quelle est la seconde moitié de la trame de réponse en system design ?
?
5. **Modèles** : choix, routage, fallbacks.
6. **Sécurité et conformité**.
7. **Evals** offline et online, **observabilité**.
8. **Coûts** et **évolution** (v2, v3).

---

Quelles erreurs éviter en entretien de system design LLM ?
?
- Proposer **directement un multi-agent** ou un fine-tuning sans justifier.
- Oublier les **evals** et la mesure du succès.
- Ignorer **droits d'accès, PII et prompt injection**.
- Ne donner **aucun chiffre** (volume, coût, latence).
- Présenter le modèle comme **fiable** sans plan pour ses erreurs.

---

## Mises en situation

Mise en situation : un candidat propose, pour un assistant de support, une architecture à cinq agents autonomes avec un modèle fine-tuné. Comment réagis-tu en tant qu'évaluateur ?
?
1. **Demander la justification** : qu'est-ce qu'un workflow avec RAG ne couvrirait pas ?
2. **Pointer le coût** : cinq agents multiplient tokens, latence et difficulté de débogage
3. **Interroger le fine-tuning** : quelles données, quel comportement visé, quelle alternative par prompt ?
4. **Chercher les manques** : droits d'accès, prompt injection par les messages clients, evals, escalade
5. **Ce qu'on attend d'un senior** : commencer simple et **prouver** par une eval le besoin de monter d'un cran

**Piège** : juger l'architecture proposée sur sa sophistication plutôt que sur son adéquation.

---

Mise en situation : on te demande de concevoir une extraction de données sur 20 millions de documents, avec un budget serré et aucune contrainte de latence. Quelle architecture proposes-tu ?
?
1. **Asynchrone en batch** : traitement différé, moins cher, GPU maintenus à pleine charge
2. **Sorties contraintes** par schéma, avec validation métier ensuite ([[63-guided-generation|guided generation]])
3. **Petit modèle** fine-tuné ou distillé, si le volume justifie l'investissement ([[53-donnees-synthetiques-distillation|distillation]])
4. **File d'exceptions** : les cas à faible confiance partent vers une relecture humaine
5. **Idempotence et reprise** : un incident ne doit pas faire retraiter les 20 millions de documents

**Piège** : dimensionner ce traitement comme un service interactif, avec des appels synchrones un par un.

---

## Connexions
- [[141-system-design-llm|System design LLM]] — la méthode
- [[142-fiabilite-resilience-llm|Fiabilité & résilience]] — tenir en production
- [[22-rag-avance|RAG avancé]] — ACL et recherche hybride
- [[36-orchestration-agents|Orchestration]] — quand plusieurs agents se justifient
- [[162-document-parsing|Parsing de documents]] — ingestion des corpus réels
- [[163-voix-temps-reel|Voix temps réel]] — le cas vocal
- [[122-finops-llm|FinOps LLM]] — maîtriser le coût à l'échelle
- [[148-pipelines-batch-llm|Pipelines batch]] — le cas 4 en détail
- [[00-moc-ai-engineering|MOC AI Engineering]]
