# UX de l'IA & human-in-the-loop — Flashcards
Tags: #flashcards #ai-engineering #ux #produit #human-in-the-loop #llm

Pourquoi l'UX est-elle un sujet d'AI Engineer et pas seulement de designer ?
?
<!--anki:473c3c77237b4b533a6b-->
Parce que les choix d'interface **compensent les limites du modèle** (erreurs, latence, incertitude) et **produisent les données** d'amélioration (feedback, corrections). Un modèle moyen avec une bonne UX de vérification peut battre un meilleur modèle présenté comme infaillible.

---

À ne pas confondre : IA qui assiste (copilote) et IA qui agit (autopilote) ?
?
<!--anki:7a327b7b494e59375778-->
- **Copilote** : l'IA **propose**, l'humain **décide** (suggestion de code, brouillon d'e-mail) — tolère des erreurs, puisque l'humain filtre.
- **Autopilote** : l'IA **exécute** seule — exige une fiabilité bien plus élevée et des **garde-fous**.

On commence souvent en copilote, on **mesure** le taux d'acceptation, puis on automatise les cas où il est très élevé.

---

Comment concevoir un human-in-the-loop efficace ?
?
<!--anki:6b3241637143484d6449-->
- Demander une validation **seulement** pour les actions **risquées ou irréversibles** (sinon fatigue d'approbation, l'humain clique « oui » sans lire).
- Montrer **exactement** ce qui va être fait (diff, destinataire, montant), pas un résumé rédigé par le modèle.
- Permettre de **modifier** avant d'approuver, pas seulement accepter/refuser.
- **Journaliser** qui a approuvé quoi ([[103-defenses-agents|approbation humaine fiable]]).

---

Pourquoi le streaming change-t-il l'expérience ?
?
<!--anki:7a2c4128527e442d467d-->
Un temps de réponse de 10 s est **inacceptable en attente muette**, mais **tolérable** si le texte apparaît après 500 ms. Le **TTFT** devient la métrique perçue. Contrepartie : il faut gérer l'**affichage progressif** du markdown, les **erreurs en cours de flux** et les contrôles de sortie **après** l'affichage (ou par morceaux).

---

Comment rendre visible le travail d'un agent ?
?
<!--anki:5040712a5e662864245e-->
Afficher les **étapes** en cours (« recherche dans les documents », « exécution des tests »), les **outils appelés**, et permettre d'**interrompre** ou de **réorienter**. L'utilisateur tolère une longue durée s'il **voit la progression** et garde le contrôle.

---

Comment collecter du feedback utile ?
?
<!--anki:6f52726d5e2c6f7d3d67-->
- **Explicite léger** : pouce haut/bas **au niveau de la réponse**, avec raison optionnelle en un clic.
- **Implicite** : copie, acceptation, modification, régénération, abandon.
- **Corrections** : quand l'utilisateur modifie la sortie, la version corrigée est une **donnée d'entraînement** précieuse.

Relier chaque feedback à la **trace complète** ([[91-langfuse-observabilite|Langfuse]]) pour pouvoir l'analyser.

---

Comment gérer les attentes des utilisateurs ?
?
<!--anki:5165422e7e717c7b467e-->
- Annoncer **ce que le système sait faire et ne sait pas faire** (périmètre, fraîcheur des données).
- Proposer des **exemples de requêtes** pour guider l'usage.
- Afficher **les sources** et la possibilité d'erreur, sans avertissement générique ignoré de tous.
- Indiquer qu'on parle à une **IA** (obligation de transparence de l'[[155-ai-act|AI Act]] pour les chatbots).

---

Chat ou interface dédiée ?
?
<!--anki:642d7846327c23796a26-->
Le **chat** est flexible mais oblige l'utilisateur à **savoir quoi demander** et à écrire. Pour une tâche **récurrente et bien définie**, une interface dédiée (bouton « résumer », formulaire, action intégrée dans l'outil existant) est plus rapide, plus **évaluable** et plus fiable. Le chat convient à l'**exploration**.

---

Qu'est-ce que l'automation bias ?
?
<!--anki:4264612378684778734c-->
La tendance des humains à **faire trop confiance** à une suggestion automatique et à **ne plus vérifier**, surtout quand le système a souvent raison. Il rend le human-in-the-loop **illusoire**. Parades : rendre la vérification **facile** (sources à portée de clic), signaler les cas **incertains**, auditer par échantillonnage les décisions validées.

---

Comment gérer les erreurs et refus dans l'interface ?
?
<!--anki:67445f4276753a4d3569-->
Des messages **actionnables** : dire **pourquoi** (hors périmètre, information absente, contenu bloqué) et **quoi faire** (reformuler, contacter un humain). Éviter les refus secs sans explication, et prévoir une **escalade vers un humain** pour les cas bloquants.

---

## Mises en situation

Mise en situation : ton outil demande une validation humaine avant chaque action, et les utilisateurs cliquent « approuver » sans lire. Comment corriges-tu ?
?
<!--anki:6c632d5f7b2e3f5a245e-->
1. **Réduire le nombre de demandes** : validation réservée aux actions risquées ou irréversibles
2. **Montrer le concret** : diff, destinataire, montant, calculés par le code et non résumés par le modèle
3. **Permettre de modifier** avant d'approuver, pas seulement accepter ou refuser
4. **Signaler les cas incertains** pour concentrer l'attention là où elle sert
5. **Auditer par échantillonnage** les décisions validées, car l'automation bias rend la validation illusoire

**Piège** : mesurer le succès au taux d'approbation, qui monte justement quand les gens ne lisent plus.

---

Mise en situation : ton assistant met 12 secondes à répondre et les utilisateurs l'abandonnent, alors que la qualité est bonne. Que changes-tu sans toucher au modèle ?
?
<!--anki:5265462a43554f23484f-->
1. **Streamer** : un premier token en moins d'une seconde rend l'attente acceptable
2. **Afficher la progression** d'un agent, étape par étape, plutôt qu'un simple indicateur d'attente
3. **Paralléliser** ce qui peut l'être et pré-calculer les réponses fréquentes
4. **Permettre d'interrompre** ou de réorienter en cours de route
5. **Mesurer le ressenti** : TTFT p95 et taux d'abandon, pas seulement la durée totale ([[64-metriques-slo-inference|SLO]])

**Piège** : afficher la réponse d'un bloc à la fin, en pensant que seule la durée totale compte.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — human-in-the-loop
- [[103-defenses-agents|Défenses des agents]] — approbation humaine fiable
- [[97-evals-online-ab-testing|Evals online]] — feedback et métriques produit
- [[143-hallucinations-grounding|Hallucinations & grounding]] — montrer l'incertitude
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT et latence perçue
- [[83-gateway-ingress|Gateway]] — streaming SSE
- [[163-voix-temps-reel|Voix & agents temps réel]] — l'UX quand l'interface est la voix
- [[84-streaming-integration-applicative|Streaming & intégration]] — la mécanique derrière le streaming
- [[00-moc-ai-engineering|MOC AI Engineering]]
