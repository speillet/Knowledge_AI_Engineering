# GDPR applied to LLM — Flashcards
Tags: #flashcards #ai-engineering #gdpr #compliance #data
Verified on: 25 September 2026 — This factsheet lists products, versions or regulatory texts that are evolving quickly.
<!-- summary: scope, GDPR or AI Act, principles, legal basis for re-use, controller and processor, transfers outside the EU, right to erasure, AIPD, automated decisions, data in the model, concrete measures, separate purposes between service and training, retention by purpose, proof of erasure. -->


When does the GDPR apply to a LLM application? <!--anki:75213c515379246a5375-->
?
The GDPR concerns the **processing of personal data entering its territorial field**, particularly in the context of an establishment in the EU, or to offer goods/services to people in the EU or to monitor their behaviour. Nationality alone does not decide on its application.

Prompts, RAG documents, traces and training sets can directly or indirectly identify people. Checking the data actually processed and the roles of the actors; the simple use of a LLM is not enough to qualify each treatment.

---

What GDPR principles govern the collection and use of data from a LLM system? <!--anki:7437656f6f2d723b2a49-->
?
- **Licitity**: a **legal basis** for each purpose.
- **Limitation of purposes**: the data collected for the support does not serve as an office for training.
- **Minimization**: only send to the model what you need.

In concrete terms, the minimization is reflected in the code: select the fields of the file useful to the question rather than injecting the entire history of the customer, and do not transmit the attachments unnecessarily. Each purpose, such as responding, improving the system or producing statistics, is documented with its legal basis in the register of treatments.

---

What GDPR principles govern the quality and data retention of a LLM system? <!--anki:753340264b2d61287d4a-->
?
- **Exactness**: A model that **hallucinates** information about a person is problematic.
- **Limitation of retention**: retention of logs, caches and memory.
- **Security** and **responsibility**: to be able to demonstrate compliance.

Examples: complete traces kept for a few weeks for debugging, metadata aggregated longer, agent memory deleted at account closure, each duration being justified. For accuracy, a person can request the correction of false information produced about him: it is necessary to be able to correct the source or block the answer, since we do not correct a weight of the model.

---

What is the legal basis for reusing conversations to improve the system? <!--anki:6c753e692a2176406975-->
?
First define the **purpose of reuse** and verify its compatibility with the initial collection. Depending on the circumstances, a basis such as legitimate interest may require a documented balancing and a right of opposition; a consent must be valid and revocable.

Inform people, limit data and set their retention. A withdrawal option does not replace a legal basis, and consent is not assumed from the use of the chatbot. Sensitive data and changes in purpose require specific analysis.

---

Who is the controller and who is the processor? <!--anki:4a3170492e452a56653b-->
?
In general, the **Company that deploys** The application is **Data controller** ; on the **Supplier ofAPI** The model is **Subcontractor** (Article 28) if he processes the data only on his behalf, Hence the need for an **DPA**. If he reuses the data for his own purposes (training), he can become **Responsible** for this part.

Qualify roles by actual processing, not only by contractual label. Mapping purposes, instructions, sub-contractors and transfers; the same actor may have different roles depending on the operation. Validate ambiguous cases with the DPO or the legal.

---

What are the problems with non-EU transfers? <!--anki:77264354606a562d344b-->
?
A transfer of personal data to a third country must comply with the **Chapter V of the GDPR**: applicable adequacy decision, appropriate safeguards such as standard contractual clauses, or framed derogation. Depending on the mechanism, analyze local law and the necessary additional measures.

A hosting region in the EU is not always enough: review administrative access from abroad and subsequent sub-contractors. Check the status and scope of any invoked certification. Self-hosting can reduce some transfers, without removing other obligations of the GDPR.

---

How to manage the right to erasure in a LLM system? <!--anki:6f356c3f4c75294a4d3f-->
?
Qualify the request and the **conditions or exceptions of the right to erasure**, then locate the data: sources, indexes, memory, caches, traces, training sets and derivatives. Spread the necessary deletions and document the processing of backups and retention obligations.

For the weight of a model, do not promise a targeted removal without proof: the techniques of onelearning do not offer a general guarantee. Evaluate the appropriate measures with the data controller, possibly retraining, and check the risk of return. Prevent the problem by minimization and traceability from the moment of collection.

---

When do I need an impact assessment (AIPD / DPIA)? <!--anki:6c6a3239587567735849-->
?
If the treatment has an **High risk** for people: **new technologies** (Generative AI is often one of them.) **evaluation or profiling**, Data **Sensitive** (Health, opinions), **Monitoring** of employees, **Large Scale**. The DPA documents risks and measures, and is linked to the assessments required by the[[155-ai-act|AI Act]].

These elements guide the analysis, without making any use of a LLM automatically submitted to AIPD. Examine criteria and lists of the competent authority before deployment; re-evaluate when changing purpose, population or data.

---

What does the GDPR say about automated decisions? <!--anki:7460602e37623c3b6d6c-->
?
The **Article 22** establishes the right not to be subject to an exclusively automated decision with a significant legal or similar effect, as a refusal of credit. It provides exceptions: contractual necessity, framed legal authorization or explicit consent.

For contractual and consent exceptions, the guarantees include human intervention, expression of the point of view and contestation; the legal exception must also provide adequate protections.

Example: a human validation of pure form is not sufficient to demonstrate that the decision is no longer exclusively automated. Examine the real role of the reviewer, information provided and sensitive data. Have the concrete device qualified, not only its label "assistant".

---

Does the model itself contain personal data? <!--anki:79743c65434234557449-->
?
A model trained on personal data is not **automatically anonymous**. The opinion 28/2024 of the EDPS requires an assessment on a case-by-case basis of the means reasonably likely to be used.

In particular, the probability of extracting personal data from the people in the corpus and obtaining it through requests, whether voluntarily or not, must be insignificant. Documenting access to the model, realistic attacks and measures of limitation; a few prompts without leaks are not enough. Development and deployment each require an analysis of their treatment. The mere deletion of the source dataset does not demonstrate either anonymity of the model or erasure of what it has memorized.

---

What document compliance measures are required for a LLM application? <!--anki:4c6c4e6a393956363c35-->
?
- **Register** of up-to-date processing: purposes, data, subcontractors.
- **Information** from users, including the use of an AI.
- **DPA** signed and verified data location at suppliers.

Specify the legal bases, the recipients, the durations and the modalities of exercise of rights in the relevant documentation. The subcontract must correspond to the processing actually carried out. An announced location is not enough: examine also sub-contractors later, remote access and possible transfers.

---

What technical measures should be taken for a LLM compliant application? <!--anki:4f7d30362d3d792e4139-->
?
- **Pseudonymization** before sending to the model when possible ([[152-pii-privacy|PII]]).
- **Retention** configured on logs, traces, caches, and memory.
- **Procedure for exercising rights** (access, deletion) covering **all** storage.

Combine these measures with access controls, encryption and mapping of derived data. Effectively test a user’s deletion in indexes, backups and caches according to the applicable retention rules. Pseudonymization remains reversible or re-identifiable in certain contexts: it does not automatically break the GDPR.

---

Do not confuse: GDPR and AI Act? <!--anki:514e6a7064447d49545e-->
?
- **GDPR** : protect them **People** which we treat them **personal data**. It applies as soon as a PII enters the system, Regardless of the risk level of AI
- **AI Act**: frames **AI systems** according to their **risk level** (prohibited uses, high risk, transparency, GPAI), even without personal data ([[155-ai-act|AI Act]])

The two are cumulative: an HR chatbot dealing with CVs is the **High Risk** the AI Act **and** of the GDPR. The GDPR’s AI and the AI Act’s risk analysis benefit from being conducted together.

---

Why does a consent to use an assistant not automatically cover the reuse of its conversations to train a model? <!--anki:3363333634366361656363663462656538636164636262626435666335626363-->
?
The **use of the service** and the **Improvement by training** They can be separate purposes. It is necessary to determine and document the legal basis adapted to each, then inform people in accordance with the applicable framework.

If consent is withheld, check its conditions of validity and withdrawal; do not assume that a general box regulates all processing. Examine minimization, sensitive data, retention and rights with the DPO. A supplier clause "no training" does not, in itself, regulate the legality of the collection nor that of internal processing.

---

Why set separate retention times for conversations, traces, and improvement datasets? <!--anki:6332656330653866386531333463623962356663663839623061333439363366-->
?
This data may serve **different purposes**, with different needs and risks. Technical convenience does not justify indefinite retention of all content.

Define the durations according to each purpose, limit the retained data and apply the deletion to the copies concerned. The CNIL stresses that the performance measurement alone is not enough to justify a long retention of all data. Document the choices with the competent managers.

---

Why should a backup restore take into account deletion requests that have already been processed? <!--anki:3866336236393332376539633461626262353539613064373362636534373939-->
?
An old backup can **re-introduce data deleted from the active system**. Provide, in the applicable framework, a minimum log of withdrawals and a procedure to re-apply them before re-commissioning.

Limit access to backups, their duration and permitted uses; test the restoration without republishing the data concerned. Keep only the information necessary to prevent this reintroduction. The specific obligations and exceptions depend on the processing: document them with the data protection officers.

---

## Scenarios

Scenario: a customer exercises his right to erasure. Your data is in the index RAG, the agent memory, traces, caches and a fine-tuned model. What do you answer? <!--anki:782b47475664446d4a32-->
?
1. **Qualify the request**: identify the person, the perimeter and any legal exceptions.
2. **Mapping copies**: sources, indexes, memory, traces, caches, backups and training data.
3. **Propagate the necessary deletion** to the data and derivatives, verifying that a re-ingestion does not recreate them.
4. **Evaluate the fine-tuned model**: risk of restitution, means of correction and possible retraining; do not claim to withdraw a fact of weights without validation.
5. **Document and reply** within applicable deadlines, with minimal trace of operations.

**Trap**: remove the source but keep its summaries or promise technically unproven weight removal.

---

Scenario: the trade wants to automate the sorting of applications, with automatic rejection under a certain score. What obligations do you report? <!--anki:48304b7469563d3c5345-->
?
1. **Automated decision**: the GDPR regulates decisions that produce significant effects, such as a rejection of an application
2. **Real human intervention**: not a rubber-stamp approval, with possibility to challenge
3. **Information** on the logic of the treatment and the criteria
4. **AI Act**: recruitment is a high-risk practice, with its own obligations ([[155-ai-act|AI Act]])
5. **Biais**: measuring group equity, documenting and correcting ([[156-responsible-ai|IA responsable]])

**Trap**: Consider that a human who validates 200 releases per day is a real human intervention.

---

## Sources

- [CNIL — legitimate interest in developing an AI system](https://www.cnil.fr/fr/base-legale-interet-legitime-developpement-systeme)

- [CNIL — brings AI systems into compliance with GDPR](https://www.cnil.fr/fr/intelligence-artificielle/ia-comment-etre-en-conformite-avec-le-rgpd)

- [European Union – Regulation (EU) 2016/679, GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra)
- [CNIL — text of articles 12 to 23, including automated decisions](https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre3) — article 22 accessed 6 November 2026; verification limited to this card.
- [CNIL — resources on AI and personal data](https://www.cnil.fr/fr/intelligence-artificielle)

- [European Union — GDPR, Articles 5 to 7 and 13](https://eur-lex.europa.eu/eli/reg/2016/679/oj/fra) — targeted deepening of the 12 November 2026; educational examples are built for this review.

- [EDPS — reviews 28/2024 on AI models](https://www.edpb.europa.eu/system/files/documents/2024-12/edpb_opinion_202428_ai-models_en.pdf) — targeted review of the 12 November 2026: anonymity appreciated on a case-by-case basis, extraction and obtaining by requests.

- Supplement to 14 November 2026 — Purposes, conservation and rights; restoration procedures are design implications: [CNIL — AI and GDPR](https://www.cnil.fr/fr/intelligence-artificielle/ia-comment-etre-en-conformite-avec-le-rgpd).

## Connections
- [[152-pii-privacy|PII & Privacy]] — technical measures
- [[155-ai-act|AI Act]] — the AI specific regulation
- [[156-responsible-ai|IA responsable]] — fairness and transparency
- [[39-agent-memory|Memorandum of agents]] — Forgetting and deleting
- [[134-vector-search-ann|Vector search]] — deletion in index
- [[163-real-time-voice|Voice & Real Time]] — voice agents and latency budget
- [[00-moc-ai-engineering|MOC AI Engineering]]
