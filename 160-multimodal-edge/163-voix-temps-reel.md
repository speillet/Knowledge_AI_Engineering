# Voix & agents temps réel — Flashcards
Tags: #flashcards #ai-engineering #multimodal #voix #temps-reel #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: cascade ou speech-to-speech, latence et chemin critique, fin de tour, barge-in, STT et limites du WER, interruptions et effets métier, évaluation et risques. -->


Quelles sont les deux architectures d'un agent vocal ? <!--anki:4e5654346978386b257c-->
?
Une **cascade** transforme la parole en texte (STT), produit une réponse avec un LLM, puis synthétise l'audio (TTS). Elle rend chaque étape inspectable et remplaçable, mais une erreur de transcription peut se propager.

Un modèle **speech-to-speech** traite directement l'audio et peut préserver davantage d'indices vocaux. Son gain de latence et les possibilités de contrôle dépendent de l'implémentation ; ils doivent être mesurés. Comparer qualité, tours de parole, outils, interruptions et traces disponibles. Des architectures hybrides peuvent aussi combiner ces approches.

---

Quel budget de latence vise-t-on pour une conversation naturelle ? <!--anki:495f262932252b41506c-->
?
Définir une cible **de bout en bout**, de la fin de parole de l'utilisateur au début de l'audio entendu. Une cible de 500 à 800 ms peut servir de repère de conception, pas de seuil universel de satisfaction.

Détection de fin de tour, transcription, LLM, synthèse, réseau et tampon de lecture contribuent au délai. Mesurer médiane et percentiles élevés par type de tour, avec appels d'outils ou interruptions. Un acquiescement rapide n'est pas forcément une réponse utile ; mesurer aussi le délai jusqu'à l'information demandée.

---

Comment réduire la latence d'un pipeline en cascade ? <!--anki:474f7845412a634d254f-->
?
- **Mesurer le chemin critique** avec des horodatages par tour.
- **Streamer** transcription, génération et synthèse lorsque les interfaces le permettent.
- **Réduire le travail utile** : prompt adapté, cache validé, modèle suffisamment rapide.
- **Rapprocher les services** et mesurer réseau, tampons et transport ; WebRTC n'efface pas les délais internes.
- **Informer pendant une attente** sans présenter une action comme accomplie.

Comparer qualité et interruptions avant/après. En streaming, les étapes peuvent se chevaucher : additionner des durées internes sans vérifier leurs frontières peut compter deux fois le même délai.

---

Qu'est-ce que la détection de fin de tour (turn detection) ? <!--anki:775f535e384c782f3130-->
?
Décider **quand l'utilisateur a fini de parler**. Un simple **VAD** (détection d'activité vocale) sur le silence coupe la parole lors d'une pause ou attend trop. Les systèmes récents combinent VAD et **modèle sémantique** qui estime si la phrase est **terminée**. C'est un réglage majeur du ressenti.

---

Qu'est-ce que le barge-in ? <!--anki:424839232e437e4b5e44-->
?
La capacité de l'utilisateur à **interrompre** l'agent pendant qu'il parle. Il faut **arrêter le TTS immédiatement**, **annuler** la génération en cours, et **mettre à jour l'historique** avec ce qui a réellement été prononcé (pas le texte complet prévu), sinon le modèle croit avoir dit des choses que l'utilisateur n'a pas entendues.

---

Pourquoi le texte destiné à la voix doit-il être écrit différemment ? <!--anki:4539556237465064596a-->
?
Pas de **markdown**, de listes, de tableaux ni d'URL ; des phrases **courtes** ; les nombres, dates, sigles et unités **écrits pour être prononcés** (« trois cent vingt euros »). On le précise dans le prompt et on normalise le texte avant le TTS.

Exemple : « RDV le 03/04 à 14h30, réf. FR-2219 » devient « rendez-vous le trois avril à quatorze heures trente, référence F R deux deux un neuf » ; sinon le TTS risque de lire « zéro trois barre zéro quatre ». L'auditeur ne peut pas relire : proposer peu d'options à la fois et répéter l'information clé en fin de phrase.

---

Quelles difficultés propres au STT ? <!--anki:4560567a56343c463437-->
?
**Noms propres**, termes métier, **accents**, bruit de fond, téléphonie à bande étroite (8 kHz), chevauchement de voix. Leviers : **vocabulaire personnalisé** (mots-clés, contexte), modèles adaptés au domaine, et confirmation orale des informations critiques (numéro de dossier, montant).

Exemple de confirmation : « J'ai noté le dossier quatre, sept, deux, un, c'est bien ça ? ». Énoncer chiffre par chiffre limite les confusions entre nombres proches, comme « six » et « dix » sur une ligne bruitée. Tester sur des enregistrements réels du canal : un modèle évalué sur de l'audio 16 kHz perd en précision sur la téléphonie à 8 kHz.

---

Comment évaluer un agent vocal ? <!--anki:633e2c6f5e44436b267b-->
?
- **Latence** perçue (p50, p95) de bout en bout.
- **Taux d'erreur de mots** (WER) du STT sur ses propres enregistrements.
- **Réussite de la tâche** via des conversations simulées (voix synthétique ou texte).
- Taux d'**interruptions** involontaires et de **silences** trop longs.
- Qualité et naturel de la voix (écoutes humaines).

---

Quels risques spécifiques à la voix ? <!--anki:6c253c2d3a31356b6f78-->
?
- **Clonage de voix** et usurpation : ne pas considérer la simple ressemblance vocale comme une preuve d’identité suffisante pour une action sensible.
- **Consentement** à l'enregistrement et durée de conservation des audios (données personnelles, voire **biométriques**).
- **Transparence** : informer qu'on parle à une IA ([[155-ai-act|AI Act]]).
- Injection par la parole ou par l'audio d'un contenu joué.

---

Pourquoi le WER ne suffit-il pas pour évaluer la transcription d'un agent vocal ? <!--anki:3061386436366634373032373439333839646663366563353661626438346261-->
?
Le **WER** compte substitutions, suppressions et insertions, divisées par le nombre de mots de référence. Il mesure l'écart textuel, pas directement la gravité métier.

Confondre « quinze » et « cinquante » peut modifier un paiement, alors que plusieurs erreurs sur des mots de liaison changent peu la décision. Mesurer aussi exactitude des entités critiques, négations, succès de tâche et besoin de clarification. Préciser normalisation et segmentation ; accents et ponctuation peuvent changer les scores sans modifier l'information utile.

---

Calcul : après la fin de parole, une cascade attend 400 ms de détection, puis 100 ms de transcription finale, 250 ms jusqu'au premier texte, 150 ms jusqu'au premier audio et 100 ms de transport/lecture. Sans chevauchement, quel délai total et quel gain si la détection passe à 200 ms ? <!--anki:6662626634333464636239313431373162343964303064316365666535616166-->
?
Sous l'hypothèse séquentielle donnée :
```text
délai initial = 400 + 100 + 250 + 150 + 100 = 1 000 ms
délai modifié = 200 + 100 + 250 + 150 + 100 = 800 ms
gain = 200 ms, soit 20 %
```
Une détection plus rapide peut couper une pause qui appartenait encore au tour utilisateur. Mesurer donc délai et interruptions involontaires ensemble. En streaming réel, identifier les intervalles qui se chevauchent avant d'additionner leurs durées.

Le poste le plus lourd n'est pas forcément le plus sûr à réduire : la détection pèse ici 40 % du délai, mais la raccourcir augmente les coupures. Réduire le temps jusqu'au premier texte, avec un modèle plus petit ou un prompt plus court, ne présente pas ce risque.

---

## Mises en situation

Mise en situation : ton agent vocal répond en 2,5 secondes et les utilisateurs raccrochent. Comment récupères-tu ce budget de latence ? <!--anki:497e664e72742332292c-->
?
1. **Décomposer** le budget : détection de fin de parole, STT, TTFT du LLM, premier morceau audio du TTS, réseau
2. **Streamer partout** : STT incrémental, LLM en streaming, TTS qui démarre dès la première phrase
3. **Réduire le travail du LLM** : prompt court, préfixe caché en cache, réponses brèves imposées par consigne
4. **Vérifier réseau et tampons** : rapprocher les services et mesurer l’effet du transport
5. **Masquer les attentes** : phrase d'attente pendant un appel d'outil lent ([[144-ux-ia-human-in-the-loop|UX]])

**Piège** : optimiser le modèle alors que la moitié du budget part dans la détection de fin de parole.

---

Mise en situation : ton agent vocal est régulièrement interrompu par les utilisateurs, et il répond ensuite à côté. Que corriges-tu ? <!--anki:7529616d66434374344f-->
?
1. **Gérer le barge-in** : arrêter le TTS immédiatement et annuler la génération en cours
2. **Corriger l'historique** : n'y consigner que ce qui a réellement été **prononcé**, pas le texte complet prévu
3. **Régler la détection de fin de tour** : un simple détecteur de silence coupe la parole ou attend trop
4. **Confirmer les informations critiques** oralement (numéro de dossier, montant)
5. **Mesurer** : taux d'interruptions involontaires et de silences trop longs

**Piège** : garder dans l'historique une réponse que l'utilisateur n'a jamais entendue, ce qui décale toute la suite.

---

Mise en situation : un utilisateur interrompt son agent vocal après qu'un remboursement a été envoyé à l'API, puis demande de l'annuler. Que doit faire le système ? <!--anki:6438643639353134383535663465353061626366323431373438393763383262-->
?
1. **Arrêter la parole en cours** et mettre à jour l'historique entendu.
2. **Distinguer interruption et annulation métier** : couper l'audio n'annule pas une opération déjà envoyée.
3. **Consulter le statut** du remboursement avec son identifiant.
4. **Appliquer une annulation ou compensation autorisée**, si le service le permet, sinon escalader.
5. **Expliquer l'état vérifié**, sans annoncer une annulation non confirmée.

**Piège** : supprimer le tour conversationnel et perdre la trace d'un effet déjà produit.

---

## Sources

- [LiveKit — tours de parole et interruptions](https://docs.livekit.io/agents/logic/turns/)
- [LiveKit — mesures de latence par tour](https://docs.livekit.io/testing/observability/data/)
- [Hugging Face Evaluate — définition du WER](https://huggingface.co/spaces/evaluate-metric/wer/blob/main/README.md)

- [LiveKit — architecture des agents vocaux](https://docs.livekit.io/agents/)

## Connexions
- [[161-modeles-vision-langage|Modèles vision-langage]] — les autres modalités
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT et latence
- [[145-cas-system-design|Cas de system design]] — l'assistant vocal
- [[144-ux-ia-human-in-the-loop|UX de l'IA]] — interruption et contrôle
- [[154-rgpd-llm|RGPD]] — données vocales
- [[84-streaming-integration-applicative|Streaming & intégration]] — SSE, annulation et tâches longues
- [[00-moc-ai-engineering|MOC AI Engineering]]
