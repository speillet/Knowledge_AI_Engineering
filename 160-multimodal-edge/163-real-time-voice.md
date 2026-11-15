# Voice & real-time agents — Flashcards
Tags: #flashcards #ai-engineering #multimodal #voice #real-time #llm
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: cascade or speech-to-speech, latency and critical path, end of turn, barge-in, STT and WER limits, interruptions and business effects, evaluation and risks, audio interruption and business cancellation, provisional transcription, critical words. -->


What are the two architectures of a voice agent? <!--anki:4e5654346978386b257c-->
?
A **cascade** turns speech into text (STT), produces a response with a LLM, and then synthesizes audio (TTS). It makes each step inspectable and replaceable, but a transcription error can spread.

A **speech-to-speech** model directly processes audio and can preserve more voice cues. Its latency gain and control possibilities depend on the implementation; they need to be measured. Compare quality, speaking turns, tools, interruptions and traces available. Hybrid architectures can also combine these approaches.

---

What is the latency budget for a natural conversation? <!--anki:495f262932252b41506c-->
?
Set a target **from end to end**, from the end of the user's speech to the start of the audio being heard. A target from 500 to 800 ms can serve as a design benchmark, not a universal threshold of satisfaction.

End of turn detection, transcription, LLM, synthesis, network and read buffer contribute to the delay. Measure median and high percentiles by tower type, with tool calls or interruptions. A quick acquiescence is not necessarily a useful answer; also measure the delay up to the requested information.

---

How to reduce the latency of a cascading pipeline? <!--anki:474f7845412a634d254f-->
?
- **Measure the critical path** with timestamps per turn.
- **Streamer** transcription, generation and synthesis when interfaces allow.
- **Reduce useful work**: adapted prompt, validated cache, sufficiently fast model.
- **Reconcile services** and measure network, buffers and transport; WebRTC does not erase internal delays.
- **Inform during a wait** without presenting an action as completed.

Compare quality and before/after interruptions. Streaming, the steps can overlap: adding internal durations without checking their borders can count twice the same delay.

---

What is turn detection? <!--anki:775f535e384c782f3130-->
?
Decide **when the user has finished speaking**. A simple **VAD** (voice activity detection) on silence cuts off speech during a pause or waits too long. Recent systems combine VAD and **semantic model** which estimates whether the sentence is **completed**. This is a major setting of feeling.

Test hesitations, dictated numbers, noise and several accents. Reducing the silence threshold accelerates the response but increases premature interruptions; measure both, with the → first useful audio end-of-speech time.

---

What is barge-in? <!--anki:424839232e437e4b5e44-->
?
The ability of the user to **interrupt** the agent while speaking. **Stop the TTS immediately**, **cancel** the current generation, and **update the history** with what has actually been uttered (not the full text intended), otherwise the model believes that it has said things that the user has not heard.

Empty the client-side playback buffers as well. A server cancellation accused does not guarantee the silence of the speaker. Test an interruption during a significant amount or instruction, and then check what the agent assumes to have communicated.

---

Why should voice text be written differently? <!--anki:4539556237465064596a-->
?
No **markdown**, lists, tables or URLs; **short sentences**; numbers, dates, acronyms and units **written to be pronounced** (“three hundred and twenty euros”). This is specified in the prompt and the text is normalized before the TTS.

Example: "REV the 03/04 to 14h30, ref. FR-2219" becomes "rendez-vous on April three at 2:30 p.m., reference F R two one nine"; otherwise the TTS may read "zero three bar zero four". The listener cannot reread: offer few options at once and repeat the key information at the end of the sentence.

---

What are the specific difficulties of the STT? <!--anki:4560567a56343c463437-->
?
**Specific names**, business terms, **accents**, background noise, narrowband telephony (8 kHz), voice overlap. Leverages: **custom vocabulary** (keywords, context), domain-specific models, and oral confirmation of critical information (case number, amount).

Example of confirmation: "I have noted the record four, seven, two, one, is that it?" Spelling digit by digit limits the confusion between close numbers, such as "six" and "ten" on a noisy line. Test on real recordings of the channel: a model evaluated on audio 16 kHz loses precision on telephony at 8 kHz.

---

How to evaluate a voice agent? <!--anki:633e2c6f5e44436b267b-->
?
Evaluate **business success, audio quality and conversation dynamics**:
- Latency between end of speech and first useful sound, with p50/p95.
- WER of the STT, but also errors on names, amounts and negations.
- Unintentional interruptions, silences and voice stops when the user resumes.
- Success and naturalness judged on representative conversations.

For example, "don't block my card" can be worse than many forgotten articles. Break down by accent, noise, and device. Text simulations test logic, not microphone, end-of-speech detection, or overlaps; complete with real-world audio tests.

---

What are the specific risks of voice? <!--anki:6c253c2d3a31356b6f78-->
?
- **Cloning of Voices** and usurpation: do not consider mere vocal resemblance as sufficient proof of identity for sensitive action.
- **Legal framework of the recording**, information and retention period of the audios (personal data, even **biometric** according to their treatment).
- **Transparency**: inform that we are talking to an AI ([[155-ai-act|AI Act]]).
- Speech or audio injection of played content.

The legal basis depends on the processing; consent is not a universal solution. Also define text alternative, independent identity control and deletion of recordings; a similar voice may come from a replayed recording.

---

Why is WER not enough to evaluate the transcription of a voice agent? <!--anki:3061386436366634373032373439333839646663366563353661626438346261-->
?
The **WER** counts substitutions, deletions and insertions, divided by the number of reference words. It measures the textual deviation, not directly the business gravity.

Confusing "fifteen" and "fifty" can change a payment, while several errors on linking words change the decision little. Also measure the accuracy of critical entities, negations, task success and need for clarification. Specify normalization and segmentation; accents and punctuation can change scores without changing useful information.

Segment also by noise and accent; a stable average can mask the degradation of a population.

---

Calculation: After the end of the speech, A waterfall awaits. 400 ms detection, then 100 ms final transcription, 250 ms to the first text, 150 ms to the first audio and 100 ms of transport/reading. Without overlap, what total delay and what gain if the detection goes to 200 ms? <!--anki:6662626634333464636239313431373162343964303064316365666535616166-->
?
Under the given sequential hypothesis:
```text
initial delay = 400 + 100 + 250 + 150 + 100 = 1,000 ms
= 200 + 100 + 250 + 150 + 100 = 800 ms
gain = 200 ms, or 20%
```
Faster detection can cut a pause that still belonged to the user lap, so measure delay and unintentional interruptions together. In real streaming, identify overlapping intervals before adding up their durations.

The heaviest station is not necessarily the safest to reduce: the detection here weighs 40% of the delay, but shortening it increases the cuts. Reducing the time to the first text, with a smaller model or a shorter prompt, does not present this risk.

---

Why should an agent's voice interrupt not be confused with the cancellation of a business action? <!--anki:6236306134626232376239633434326539393234646266396564653232653864-->
?
The **barge-in** stops or replaces an audio response, but a tool may have already made the reservation or payment advertised.

Distinguish between audio playback, generation and business operation. When the user interrupts, check the status of the action before claiming that it is canceled; apply compensation if it exists and remains allowed. Do not repeat an action only because its announcement has not been heard. Test an interruption before the call, during its waiting and after confirmation. The interface must return the confirmed state of the system.

---

Why not trigger a business action on a still-provisional voice transcription? <!--anki:6564653832373462386165363432353738376461353538316533383332303136-->
?
The STT engine can **review words already displayed**, including negations, names, or amounts. "Not valid" must not be processed from the only "valid" fragment.

Wait for a suitable completion condition and confirmation when the action requires it. Separate progressive display and execution. Test hesitations, self-corrections and interruptions, with verification of the effect actually produced.

---

## Scenarios

Scenario: your voice agent responds in 2.5 seconds and users hang up. How do you recover this latency budget? <!--anki:497e664e72742332292c-->
?
1. **Decompose** the budget: end of speech detection, STT, TTFT of the LLM, first audio track of the TTS, network
2. **Streamer everywhere**: Incremental STT, LLM streaming, TTS starting from the first sentence
3. **Reduce the work of the LLM**: prompt short, cached hidden prefix, brief responses imposed by instruction
4. **Check network and buffers**: bring services closer together and measure the effect of transport
5. **Hide expectations**: Waiting phrase during a slow tool call ([[144-ai-ux-human-in-the-loop|UX]])

**Trap**: Optimize the model while half of the budget goes into end-of-speech detection.

---

Scenario: your voice agent is regularly interrupted by users, and then it responds next to it. What do you fix? <!--anki:7529616d66434374344f-->
?
1. **Managing the barge-in** : stop the TTS immediately and cancel the current generation
2. **Correct history**: Record only what has actually been **pronounced**, not the full text provided
3. **Setting end-of-turn detection**: A simple silence detector cuts speech or waits too long
4. **Confirm critical information** orally (case number, amount)
5. **Measure**: rate of involuntary interruptions and too long silences

**Trap**: Keep in the history a response that the user has never heard, which shifts the whole suite.

---

Scenario: a user interrupts their voice agent after a refund has been sent to the API, and then requests to cancel it. What should the system do? <!--anki:6438643639353134383535663465353061626366323431373438393763383262-->
?
1. **Stop the current speech** and update the heard history.
2. **Distinguish business interruption and cancellation**: muting the audio does not cancel an operation already sent.
3. **Check the refund status** with your ID.
4. **Apply for an authorized cancellation or compensation**, if the service allows it, otherwise escalate.
5. **Explain verified status**, without announcing an unconfirmed cancellation.

**Trap**: Remove the conversational turn and lose track of an effect that has already been produced.

---

## Sources

- [LiveKit — Speech Turns and Interruptions](https://docs.livekit.io/agents/logic/turns/)
- [LiveKit — Latency Measurements per Turn](https://docs.livekit.io/testing/observability/data/)
- [Hugging Face Evaluate — WER Definition](https://huggingface.co/spaces/evaluate-metric/wer/blob/main/README.md)

- [LiveKit — voice agent architecture](https://docs.livekit.io/agents/)

## Connections
- [[161-vision-language-models|Vision-language models]] — other terms
- [[64-inference-metrics-slo|Metrics & SLO]] — TTFT and latency
- [[145-system-design-cases|Case of system design]] — Voice Assistant
- [[144-ai-ux-human-in-the-loop|UX of AI]] — interruption and control
- [[154-gdpr-llm|RGPD]] —
- [[84-streaming-application-integration|Streaming & integration]] — SSE, cancellation and long tasks
- [[00-moc-ai-engineering|MOC AI Engineering]]
