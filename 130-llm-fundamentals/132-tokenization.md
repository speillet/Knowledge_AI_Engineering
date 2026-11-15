# Tokenisation — Flashcards
Tags: #flashcards #ai-engineering #fundamentals #tokenization #llm
<!-- summary: token or word, BPE, byte-level, vocabulary size, extra cost of French, character limits, special tokens, chat templates, tokens borders, counting, security, structured truncation and budget of tokens, Unicode and standardization, special tokens. -->


What is a token? <!--anki:3f72253a587d60376a-->
?
The **text unit** read and produced by the model: frequent word, word piece, punctuation or byte depending on the tokenizer. It is used to count context, generation and often billing.

The English mark "about four characters per token" is not a universal rule. Language, code and unusual characters change the cut-up; two texts of the same length can consume different budgets.

For a specific budget, use the model's effective tokenizer and template, including role markers and other serialized items. Check the API's usage counters when available.

---

How does BPE (Byte Pair Encoding) work? <!--anki:483e336061385047454a-->
?
We start from **characters (or bytes)** and we **Iteratively merges the most common pair** of the training corpus into a new symbol, until you reach the desired vocabulary size. Frequent sequences become one token, The few are cut into pieces.

Once the tokenizer is learned, the merges and vocabulary are fixed: encoding a new text does not lead to BPE again. An unknown word can be composed of units already available. Frequent splitting reflects the learning corpus, so it is not necessarily aligned with the syllables, morphology or words of another language.

---

Why do modern tokenizers work at the byte level? <!--anki:4c39395e4c4a45662433-->
?
A **Full coverage of bytes** can represent any UTF text-8 without token unknown for a rare character. The BPE byte-level starts with units of bytes and then merges frequent sequences; other tokenizers only use a fallback on bytes.

Example: "e" occupies two bytes in UTF-8, but can form a token, be fragmented or belong to a token longer. **Byte, Character and token They are not interchangeable.**. Infrequent writing can consume more tokens for a visually short text. Measure with the target tokenizer; this cover does not allow sending raw binary files to a API Textual.

---

What is the typical size of a vocabulary and what is the compromise? <!--anki:69662b444d3f5a552f6b-->
?
From **32 k to more than 200 k** tokens, a large vocabulary **compresses text better** (less than tokens per sentence, so less cost and more content per context) but enlarges the **matrix of embedding** and the output layer, and each rare token is less well learned.

The table size of embedding is approximately **vocabulary × hidden dimension × bytes per value**. Increasing vocabulary can shorten sequences while increasing this table and the work of the final projection. Compromise depends on languages and corpus; compare the number of tokens on representative data, not just the advertised size.

---

Why is French more expensive than English? <!--anki:77302b52755f516a7d50-->
?
Tokenizers are trained on corpus **Mostly English** : French is divided into **more than tokens** for the same meaning (often +20 to +50% according to the tokenizer, and many more languages (×2 TB ×4). Consequences: **Cost**, **Latency** and **Useful context** Gradient — to measure on its own data ([[121-inference-costs|costs]]).

This is not an intrinsic property of French: the vocabulary learned and the domain change the ratio. Compare equivalent tasks, with accents, numbers and real terminology; translate artificially into English can lose meaning and add a call.

---

Why do LLMs fail to count the letters of a word? <!--anki:71382c39575d78735952-->
?
The model does not see **not the characters** but of **IDs of tokens** "Strawberry" can be 2 or 3 tokens Opaque. Tasks at the character level (spell, Invert, count) and part of the **Arithmetic** (numbers cut irregularly) suffer from it.

The exact division varies according to the tokenizer and does not absolutely prevent counting: the model can learn regularities or break down the word. For an exact answer, use a tool that counts the characters according to the desired definition. Attention to the combined accents: displayed character, Unicode code point and byte are different units.

---

What are special tokens? <!--anki:43234c5d264c6c23753d-->
?
tokens reserved for the **structure**: start and end of sequence, **role delimiters** (system, user, assistant), tool call start, etc. They are inserted by the **chat template** and should **never** be produced by user text (otherwise role injection).

It is necessary to distinguish the **visible string** representing a marker from its reserved identifier in the tokenizer. The application must assemble the roles by the intended interface and avoid concatenating raw messages as if they were already structured. Even without injection of token special, a malicious instruction in natural language remains possible.

---

What is a chat template and why is it critical for self-hosting? <!--anki:5079604669715668237d-->
?
The **gabarit** (often Jinja, provided with the template) that turns the message list into a **sequence of tokens** with the right special tokens. A **erroneous** template (misconfigured server, wrong tool format) silently degrades the quality: the template sees a **format that it has not learned** ([[11-llm-inference-servers|Inference Servers]]).

The same history can become a different sequence depending on the separators, end of turn and generation prefix. Check the template that comes with the checkpoint and test a tool exchange if the service uses one. Keep template, tokenizer and template together so that an update does not silently change entries.

---

Why can an end space in the prompt degrade the output? <!--anki:65762c3e4d4b3d582425-->
?
A final space can **change the tokenization at the boundary between prompt and continuation**. Some tokenizers represent a word with its initial space in a single token; moving this space in the prompt therefore modifies the possible continuations and their probabilities.

The effect depends on the tokenizer, model and chat template: this is not a universal cause of bad response. In case of strange output, inspect the tokens actually produced and compare with or without space in the same conversation format. Avoid arbitrarily modifying the markers expected by the model.

---

How to count tokens correctly? <!--anki:6c4a7138347c4535453c-->
?
With **the tokenizer of the target model** (the provider's library or its counting endpoint, or the Hugging Face tokenizer of the model) — “Never with the estimate.” 4 Characters for a specific budget. Two different models give **different accounts** for the same text, This changes the cost of a migration.

Count the query rendered complete: chat template, messages, tool schemas and context, and then book the output. Compare to the usage returned by the API on a sample; count only the user text underestimates the cost of an agent.

---

What is the link between tokenization and security? <!--anki:463f243f397a232c5732-->
?
- **Under-trained “glitch” tokens** that cause abnormal behavior.
- **Filter bypass** by trim variants (spaces, homoglyphs, invisible Unicode) — see [[102-agent-threats|injection invisible]].
- **Special tokens injection** if user input is not escaped.

Inspect both **text rendered and actual representation** when a filter and the model interpret an entry differently. A Unicode normalization may help some controls, but must preserve meaning and useful identifiers. Limitations of action remain necessary: no tokens slicing should allow to bypass a verified authorization in the code.

---

Do not confuse: token and word? <!--anki:75754b3923673b2a6863-->
?
- **Mot**: the unity of the human reader
- **Token**: the unit of the model, fixed by its tokenizer. A common word often makes **1 token**, a rare word, a number or a proper name **several**

Points: in English **≈ 0.75 Word by token**, In French rather **1.5 TB 2 tokens by word** according to the tokenizer. The limits of context, Prices and rates are expressed in **tokens** : estimate "in words" underestimates the bill in French. Two models do not have the same tokenizer, Therefore, not the same account for the same text.

---

Why can a character truncation cut a prompt at a location different from its tokens budget? <!--anki:3264306133343432643336313438623738323137323731623830646237353031-->
?
The **number of tokens** varies with language, spaces, numbers and technical content, so a character cap does not guarantee to respect a context window or preserve the structure of a message.

Count with the tokenizer and the template actually used, book the output and remove coherent units: messages, passages or table lines. Keep the necessary instructions and references. Test accents, emoji and code. A truncation that respects the size can still break a proof or separate a tool call from its result.

---

Why can two visually identical channels have different tokenizations? <!--anki:6631653066366138383836303434313562373831376539363362656530343364-->
?
An accented character may have **several Unicode representations**, for example a precomposed character or a letter followed by a combination accent. The normalization applied depends on the tokenizer.

Compare strings and tokens actually sent, especially for exact search and cache. Normalizing can help, but must preserve the meaning and requirements of the domain. A visual equality is not an equality of bytes nor necessarily an equality of tokens.

---

## Scenarios

Scenario: your cost estimate, calculated in English, is exceeded by 40% in production on a francophone service. What happened? <!--anki:663259637351603d4f5a-->
?
1. **Cause**: Tokenizers are trained mostly on English. The same French text consumes significantly more tokens
2. **Recalculate** with target model tokenizer, on a sample of **real traffic**, never with 4 rule
3. **Compare models** on this criterion: two models do not cut the same text in the same way
4. **Double effect**: more tokens input and output, so cost **and** latency, plus reduced useful context
5. **Redo the estimate** with each model change, as it is not transferable ([[121-inference-costs|costs]])

**Trap**: announce a budget based on a calculation made on English texts.

---

Scenario: after your vLLM server has moved to a new version, the quality of the responses drops while the model has not changed. Which track do you look at first? <!--anki:68465b377035613b6577-->
?
1. **The chat template**: a poorly applied or replaced template makes the model see a format he never learned
2. **Check it concretely**: display the real tokenized prompt, with its special tokens
3. **Tools**: The tool call format is part of the template and often breaks first
4. **Pinch** the server and template version in the versioned configuration ([[111-mlops-llmops-fundamentals|MLOps]])
5. **Early detection**: a test that compares the prompt rendered to a known reference

**Trap**: find the cause in the prompt application, while the problem is in the formatting of the messages.

---

## Connections
- [[131-transformer-architecture|Architecture Transformer]] — what consumes the tokens
- [[121-inference-costs|Inference costs]] — the token as price unit
- [[35-context-engineering|Context engineering]] — context as tokens budget
- [[63-guided-generation|Guided generation]] — stresses at the tokens level
- [[11-llm-inference-servers|Inference Servers]] — chat templates
- [[00-moc-ai-engineering|MOC AI Engineering]]
