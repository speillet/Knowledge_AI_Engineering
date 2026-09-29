# PII & confidentialité des données — Flashcards
Tags: #flashcards #ai-engineering #donnees #pii #confidentialite #securite

Où passent les données personnelles dans une application LLM ?
?
Partout : **prompts** des utilisateurs, **documents** indexés, **contexte** envoyé au fournisseur, **sorties**, **logs et traces**, **caches**, **mémoire** des agents, jeux d'**eval** et de **fine-tuning**, outils d'**annotation**. Chaque copie est une surface de fuite et une obligation de **suppression** potentielle.

---

Comment détecter les PII ?
?
- **Règles et regex** : e-mails, téléphones, IBAN, numéros de sécurité sociale (précis sur les formats structurés).
- **NER** (reconnaissance d'entités) : noms, adresses, organisations — outils type **Presidio**, spaCy, ou modèles dédiés.
- **LLM** pour les cas contextuels (« ma voisine qui a un cancer »).

Aucune méthode n'est parfaite : combiner et **mesurer le rappel** sur ses données.

---

À ne pas confondre : masquage, pseudonymisation et anonymisation ?
?
- **Masquage / suppression** : remplacer par `[EMAIL]` — l'information est perdue.
- **Pseudonymisation** : remplacer par un **jeton réversible** (`PERSON_1`) avec une table de correspondance protégée — **reste une donnée personnelle** au sens du RGPD.
- **Anonymisation** : **ré-identification impossible**, même en croisant — sort du champ du RGPD, mais bien plus difficile à atteindre qu'on ne le croit.

---

Comment utiliser un LLM externe sans lui envoyer de PII ?
?
**Pseudonymiser avant l'appel, ré-identifier après** : remplacer les entités par des jetons cohérents (`CLIENT_1`), appeler le modèle, puis remettre les vraies valeurs dans la réponse. Limites : le modèle perd du contexte (genre, lieu), et les jetons doivent rester **cohérents** au fil de la conversation.

---

Quels engagements vérifier chez un fournisseur de modèle ?
?
- **Pas d'entraînement** sur vos données (par défaut sur les offres entreprise/API, à vérifier contractuellement).
- **Durée de rétention** des requêtes (abus, sécurité), option **zero data retention**.
- **Localisation** du traitement (région UE) et sous-traitants.
- **DPA** (accord de traitement des données), certifications (SOC 2, ISO 27001).
- Conditions spécifiques des fonctions **stockées côté fournisseur** (fichiers, assistants, mémoire, batch).

---

Comment protéger les logs et traces ?
?
- **Masquer les PII** avant stockage, ou chiffrer les champs sensibles.
- **Rétention courte** et automatique.
- **Accès restreint** et journalisé (les traces LLM contiennent souvent plus d'informations sensibles que la base métier).
- Séparer l'accès aux **métriques** (large) de l'accès au **contenu** (restreint) — voir [[93-monitoring-inference|journalisation des prompts]].

---

Pourquoi un LLM peut-il « régurgiter » des données d'entraînement ?
?
Les modèles **mémorisent** une partie de leurs données, surtout les séquences **répétées** ou rares. Un modèle **fine-tuné sur des données clients** peut ressortir un e-mail ou un numéro à un autre utilisateur. D'où : **retirer les PII avant fine-tuning**, dédupliquer, et tester l'extraction.

---

Quels risques de fuite entre utilisateurs spécifiques aux LLM ?
?
- **RAG sans filtrage d'ACL** : un utilisateur obtient des extraits de documents qu'il n'a pas le droit de voir.
- **Cache partagé** (sémantique ou de réponses) entre utilisateurs.
- **Mémoire d'agent** mal isolée.
- **Prompt injection** qui exfiltre le contexte vers un tiers ([[101-securite-llm-guardrails|exfiltration]]).

---

Comment gérer les secrets (clés API, mots de passe) dans le contexte ?
?
Ils ne doivent **jamais** entrer dans le contexte du modèle : les outils s'authentifient **côté serveur** et le modèle ne manipule que des **références**. Scanner les documents indexés et les entrées pour détecter les secrets, et les **retirer** ([[103-defenses-agents|secrets]]).

---

Qu'est-ce que le privacy by design pour une application LLM ?
?
Intégrer la protection **dès la conception** : **minimisation** (n'envoyer au modèle que le nécessaire), **finalité** limitée, pseudonymisation par défaut, **rétention** minimale, cloisonnement par utilisateur, **analyse d'impact** (AIPD) quand le traitement est à risque, et capacité à **supprimer** sur demande ([[154-rgpd-llm|RGPD]]).

---

## Mises en situation

Mise en situation : ton service juridique interdit d'envoyer des données clients à un fournisseur externe, mais le cas d'usage l'exige. Quelles options présentes-tu ?
?
1. **Minimiser** : n'envoyer que les champs strictement nécessaires, jamais le dossier complet
2. **Pseudonymiser avant l'appel** et ré-identifier après, avec des jetons cohérents dans la conversation
3. **Vérifier les engagements** du fournisseur : pas d'entraînement, rétention nulle, traitement en région UE, accord de traitement signé
4. **Alternative** : modèle auto-hébergé pour les données sensibles, API pour le reste ([[164-llm-local-edge|LLM locaux]])
5. **Documenter** : analyse d'impact si le traitement est à risque ([[154-rgpd-llm|RGPD]])

**Piège** : considérer la pseudonymisation comme une anonymisation, alors qu'elle reste une donnée personnelle.

---

Mise en situation : un développeur demande l'accès aux traces de production pour déboguer un cas client. Que vérifies-tu avant de le donner ?
?
1. **Séparer les niveaux d'accès** : métriques sans contenu pour tous, contenu restreint et journalisé
2. **Masquage** : les PII devraient déjà avoir été retirées ou chiffrées avant stockage
3. **Finalité et durée** : accès limité au besoin réel et dans le temps
4. **Tracer l'accès** lui-même, car les traces LLM contiennent souvent plus d'informations sensibles que la base métier
5. **Vérifier la rétention** : les traces anciennes devraient déjà avoir été supprimées ([[93-monitoring-inference|journalisation]])

**Piège** : donner un accès large « le temps du débogage », qui ne se referme jamais.

---

## Connexions
- [[154-rgpd-llm|RGPD appliqué aux LLM]] — le cadre légal
- [[101-securite-llm-guardrails|Sécurité LLM]] — exfiltration et guardrails
- [[103-defenses-agents|Défenses des agents]] — secrets et moindre privilège
- [[93-monitoring-inference|Monitoring de l'inférence]] — journalisation des prompts
- [[123-caching-agressif|Caching agressif]] — sécurité des caches
- [[151-donnees-curation-annotation|Curation & annotation]] — données d'entraînement propres
- [[00-moc-ai-engineering|MOC AI Engineering]]
