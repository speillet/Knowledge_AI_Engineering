# PII & Data Privacy — Flashcards
Tags: #flashcards #ai-engineering #data #pii #privacy #security
<!-- summary: where data pass, detection, masking, pseudonymization and anonymization, pseudonymization before the call, commitments of providers, logs, memorization, leaks between users, secrets, privacy by design, reidentification by indirect attributes, hash and pseudonym, trace minimization. -->


Where does personal data go in a LLM application? <!--anki:75613b6d24494663604d-->
?
Everywhere: **prompts** from users, **indexed documents**, **context** sent to supplier, **exits**, **logs and traces**, **caches**, **agent memory**,**eval** and **fine-tuning** sets,**annotation tools**. Each copy is a leaking surface and a potential **deletion obligation**.

Method: draw a **flow map** that indicates, for each copy, its place of storage, its shelf life, who accesses it and how to delete it. The forgotten copies are often out of production: an evaluation set exported on the workstation of an annotator or in a shared notebook escapes any deletion procedure.

---

How to detect PII? <!--anki:4f4c4432325f3e343633-->
?
- **Rules and regex**: e-mails, telephones, IBANs, social security numbers (specificated on structured formats).
- **NER** (entity recognition): names, addresses, organizations — tools type **Presidio**, spaCy, or dedicated models.
- **LLM** for contextual cases (“my neighbor who has cancer”).

No method is perfect: combine and **measure the recall** on its data.

Build an annotated game covering languages, formats and indirect identifiers. Also measure false positives: masking a useful product code can degrade the RAG, while an undetected name can remain in the tracks.

---

Do not confuse: masking, pseudonymisation and anonymisation? <!--anki:4f25732d4e2c39303178-->
?
The **hide** hides or removes a visible value, but the other attributes can still identify the person. The **pseudonymization** replaces identifiers and protects the additional information allowing the reconciliation; the data remains personal.

**Anonymization** requires an assessment of the risk of re-identification with the means reasonably likely to be used, including by cross-checking. It does not simply remove the name or prove an absolute mathematical impossibility. For example, a rare date and place can identify someone behind `PERSON_1`. Re-assess this risk when new data or techniques make reconciliations easier.

---

How to use an external LLM without sending it PII? <!--anki:7146545960793666793a-->
?
**Minimize and transform before the call**, checking what remains identifiable. Replacing a name with `CLIENT_1` is a pseudonymization, not a guarantee of absence of personal data: rare profession, address or event can re-identify.

Keep the correspondence table locally, limit its scope and re-identify only for an authorized recipient. Test the residual data, including metadata and attachments. If the absence of personal data is imperative and not demonstrable, do not send the content to the external service; choose a treatment adapted to this constraint.

---

What commitments to check at a model supplier? <!--anki:4f3e476d2856386f6c4e-->
?
Examine **the contract and the functioning of the offer actually used**: processing purposes, possible training, retention, deletion, location and subcontractors. A general commercial promise does not necessarily cover each feature.

Verify DPA, account settings, operator access and retention exceptions. Files, batch processing and persistent functions may have different rules than ephemeral calls. Test the available technical options and keep the version of approved commitments. An EU compute region or certification alone is not sufficient to demonstrate the absence of transfer or compliance of your own use.

---

How to protect logs and traces? <!--anki:42425a31576f6c566c77-->
?
**Minimize before collection**, then hide, control access, encrypt, and apply justified retention. Separate aggregated metrics and detailed content ([[93-monitoring-inference|Journaling of Prompts]]).

Example: The prompt is hidden in the main trace, but an exception message copies the raw request. Also test errors, fetches, attachments and exports with synthetic secrets that can be found.

Encryption does not replace minimization: people who are allowed to decrypt always see the data. A stable hash can remain a personal identifier; it does not guarantee anonymity. Check deletion and retention in caches, replicas and backups according to the planned policies, not just in the lookup interface.

---

Why can a LLM "regurgitate" training data? <!--anki:463d2c3b6d6d3d696a6a-->
?
Models **memorize** some of their data, especially repeated **or rare** sequences. A **fine-tuned model on customer data** can pull an email or number to another user. Hence: **remove PII before fine-tuning**, deduplicate, and test extraction.

To test, insert into the fine-tuning data of **canaris**: unique and fictitious strings, such as a fake account number. We then check if the model completes them from their beginning. The risk increases with repetitions and the number of epochs: an email signature repeated a thousand times is much more exposed than an example seen once.

---

What are the risks of leaks between LLM users? <!--anki:46376c33395556583063-->
?
- **RAG without ACL filtering**: A user gets snippets of documents that they are not allowed to see.
- **Shared cache** (semantic or replies) between users.
- **Agent memory** poorly isolated.
- **Prompt injection** that exfiltrates the context to a third party ([[101-llm-security-guardrails|exfiltration]]).

Test the same question with two identities and after revoking a right. Also check download links, quotes and logs: Hide the displayed answer does not repair information already sent to an unauthorized component.

---

How to manage secrets (API keys, passwords) in context? <!--anki:7838657a306e5d327e2f-->
?
They must not **never** enter the context of the model: the tools are authenticated **Server-side** The model manipulates only **References**. Scan indexed documents and entries to detect secrets, and the **withdraw** ([[103-agent-defenses|secrets]]).

For detection, combine known patterns, such as `AKIA` prefixes of AWS keys or `ghp_` of GitHub tokens, and high entropy strings, with tools like gitleaks or detect-secrets. A key found in an indexed document must be **revoked**, not just removed: it could be read, cached, or logged.

---

What is privacy by design for a LLM application? <!--anki:4c4f677e4b4325622f2f-->
?
Incorporate protection **from design**: **minimization** (send to model only as necessary), **limited purpose**, default pseudonymization, **minimum retention**, partitioning by user, **impact analysis** (AIPD) when processing is at risk, and ability to **delete** on request ([[154-gdpr-llm|RGPD]]).

For example, an HR assistant receives the employee's ID rather than the employee's name, retrieves only the documents applicable to his or her country, keeps conversations for a limited time, and sends the provider only pseudonymous text. Each choice is verified by a test: another employee's request must not find any of his or her documents.

---

Why does replacing names with stable identifiers still allow for re-identification? <!--anki:6630326539386137336338663462653362373766366566323964663165613733-->
?
The **Stable identifiers** It connects the events of a person. Combined with dates, places, profession or rare events, They can find it even without its name.

Evaluate all attributes and the possibilities of reconciliation, then reduce accuracy, retention and access according to the purpose. Separately protect the correspondence table when it exists. Do not automatically qualify these data as anonymous: pseudonymization remains a processing of personal data. Test the risks on traces and exports, not only on the text sent to the model.

---

Why doesn't hash an email address automatically anonymize it? <!--anki:6538326333326239303637313434333861393562663031666365663264333832-->
?
An attacker can **test candidate addresses and compare their fingerprints**, especially if the domain and population are known. A stable identifier can also be used to link events.

Proper cryptographic protection can reduce some risks, but it is necessary to consider re-identification possibilities and ancillary information. Treat this data according to their real risk. Pseudonymization does not automatically remove the obligations related to personal data.

---

How to keep useful traces of an agent without saving all the private documents? <!--anki:6532363035313838303632623434313538653238396334393537376132306437-->
?
Log **required identifiers, versions, statuses and metrics**, with extracts minimized when their usefulness is justified. Keep the originals in storage subject to their own rights.

Define access and retention, then test masking on normal outputs and exceptions. An identifier or metadata can also be personal. The minimization covers the entire telemetry path, including external tools.

---

## Scenarios

Scenario: your legal department prohibits sending customer data to an external provider, but the use case requires it. What options do you have? <!--anki:4c2a2352337659677e4b-->
?
1. **Minimize**: send only the strictly necessary fields, never the complete file
2. **Pseudonymize before the call** and re-identify afterwards, with consistent tokens in the conversation
3. **Check supplier's commitments**: no training, zero retention, treatment in EU region, signed treatment agreement
4. **Alternative**: Self-hosted model for sensitive data, API for the rest ([[164-local-edge-llm|Local LLM]])
5. **Document**: Impact assessment if treatment is at risk ([[154-gdpr-llm|RGPD]])

**Trap** : consider pseudonymization as an anonymization, while it remains a personal data.

---

Scenario: a developer requests access to production traces to debug a customer case. What do you check before giving it? <!--anki:742b3d4a535d77405b56-->
?
1. **Separate access levels**: Content-free metrics for all, restricted and logged content
2. **Hide**: PII should have already been removed or encrypted before storage
3. **Financiality and duration**: limited access to actual needs and in time
4. **Track access** itself, as LLM traces often contain more sensitive information than the business base
5. **Check for retention**: Old traces should have already been removed ([[93-monitoring-inference|Logging]])

**Trap**: give a wide access “the time of debugging”, which never closes.

---

## Sources

- [CNIL — personal data and indirect identification](https://www.cnil.fr/fr/rgpd-de-quoi-parle-t-on) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- [CNIL — anonymisation of personal data](https://cnil.fr/fr/technologies/lanonymisation-de-donnees-personnelles) — targeted review of 12 November 2026: masking, pseudonymization and reasonable means of re-identification.

## Connections
- [[154-gdpr-llm|GDPR applied to LLMs]] — legal framework
- [[101-llm-security-guardrails|LLM Security]] — exfiltration and guardrails
- [[103-agent-defenses|Defenses of agents]] — secrets and least privilege
- [[93-monitoring-inference|Monitoring of inference]] — prompt logging
- [[123-aggressive-caching|Caching agressif]] — cache security
- [[151-data-curation-annotation|Curation & annotation]] — clean drive data
- [[90-011-langfuse-instrumentation-production|Langfuse — Production instrumentation]] — minimize exported data
- [[00-moc-ai-engineering|MOC AI Engineering]]
