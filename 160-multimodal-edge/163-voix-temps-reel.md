# Voix & agents temps réel — Flashcards
Tags: #flashcards #ai-engineering #multimodal #voix #temps-reel #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: cascade ou speech-to-speech, budget de latence, réduction de latence, détection de fin de tour, barge-in, texte pour la voix, STT, évaluation, risques. -->


Quelles sont les deux architectures d'un agent vocal ? <!--anki:4e5654346978386b257c-->
?
1. **Pipeline en cascade** : **STT** (speech-to-text) → **LLM** → **TTS** (text-to-speech). Modulaire, chaque brique est remplaçable, le texte intermédiaire est **inspectable** et on garde les outils et guardrails textuels.
2. **Speech-to-speech natif** : un modèle unique qui écoute et parle. **Latence** plus faible et **prosodie** (émotion, intonation) conservée, mais moins de contrôle et d'observabilité.

---

Quel budget de latence vise-t-on pour une conversation naturelle ? <!--anki:495f262932252b41506c-->
?
Environ **500 à 800 ms** entre la fin de la parole de l'utilisateur et le début de la réponse. Au-delà d'une seconde, la conversation paraît **lente**. Le budget se répartit entre détection de fin de parole, STT, **TTFT** du LLM, premier morceau audio du TTS et réseau.

---

Comment réduire la latence d'un pipeline en cascade ? <!--anki:474f7845412a634d254f-->
?
- **Streaming partout** : STT incrémental, LLM en streaming, TTS qui commence dès la **première phrase**.
- **Modèle LLM rapide** (faible TTFT), prompts courts, [[123-caching-agressif|prompt caching]].
- Serveurs **proches** de l'utilisateur, transport **WebRTC** plutôt que HTTP.
- Réponses **courtes** par consigne.
- Phrases d'attente (« je regarde ») pendant les appels d'outils lents.

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

---

Quelles difficultés propres au STT ? <!--anki:4560567a56343c463437-->
?
**Noms propres**, termes métier, **accents**, bruit de fond, téléphonie à bande étroite (8 kHz), chevauchement de voix. Leviers : **vocabulaire personnalisé** (mots-clés, contexte), modèles adaptés au domaine, et confirmation orale des informations critiques (numéro de dossier, montant).

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
- **Clonage de voix** et usurpation : ne jamais utiliser la voix comme **authentification**.
- **Consentement** à l'enregistrement et durée de conservation des audios (données personnelles, voire **biométriques**).
- **Transparence** : informer qu'on parle à une IA ([[155-ai-act|AI Act]]).
- Injection par la parole ou par l'audio d'un contenu joué.

---

## Mises en situation

Mise en situation : ton agent vocal répond en 2,5 secondes et les utilisateurs raccrochent. Comment récupères-tu ce budget de latence ? <!--anki:497e664e72742332292c-->
?
1. **Décomposer** le budget : détection de fin de parole, STT, TTFT du LLM, premier morceau audio du TTS, réseau
2. **Streamer partout** : STT incrémental, LLM en streaming, TTS qui démarre dès la première phrase
3. **Réduire le travail du LLM** : prompt court, préfixe caché en cache, réponses brèves imposées par consigne
4. **Rapprocher et changer de transport** : serveurs proches, WebRTC plutôt que HTTP
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

## Sources

- [LiveKit — architecture des agents vocaux](https://docs.livekit.io/agents/)

## Connexions
- [[161-modeles-vision-langage|Modèles vision-langage]] — les autres modalités
- [[64-metriques-slo-inference|Métriques & SLO]] — TTFT et latence
- [[145-cas-system-design|Cas de system design]] — l'assistant vocal
- [[144-ux-ia-human-in-the-loop|UX de l'IA]] — interruption et contrôle
- [[154-rgpd-llm|RGPD]] — données vocales
- [[84-streaming-integration-applicative|Streaming & intégration]] — SSE, annulation et tâches longues
- [[00-moc-ai-engineering|MOC AI Engineering]]
