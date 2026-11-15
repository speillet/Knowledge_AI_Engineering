# News Check — 13 November 2026

The documentation needed clarification. The recently added MLflow APIs are consistent with the current documentation; old formulations on MCP, agent hosting, and OWASP needed to be fixed. This review distinguishes between confirmations, corrections, and control limits.

## Perimeter and method

Starting point: `main` to commit `4d80c12`, after PR 15. The initial working folder is on an old commit with uncommitted changes; this review uses a separate worktree, without overwriting them.

The inventory covers the **150 cards / 2,440 cards**. **85 cards** have a general verification date. A recent date is not proof that all information is current; the absence of a date also does not mean that a stable principle is false.

The sources have been consulted on the 12 and 13 November 2026. Factual verification targets references likely to evolve from the **nine MLOps** topics, then their dependencies on the agent platforms, security and AI Act. The assertions are confronted with the primary pages, versioned specifications, release notes and normative texts. Context7 completes the consultation for MLflow, MCP and nXQ0004.

**14 answers are corrected or specified in six sheets**: 38, 101, 105, 115, 117 and 155. No cards are added or removed. Existing questions and identifiers are retained. General dates are not artificially renewed: the controlled passages and the date of this review are in the Sources.

## Confirmations and corrections

| Subject | Results at 13 November 2026 | Consequences in the Vault |
| --- | --- | --- |
| MLflow 3 | `name=` and URI returned by logging remain the documented path; aliases are mutable. | The 111/117/118 examples are retained. Moving an alias does not reload already loaded models. [Migration](https://mlflow.org/docs/latest/ml/mlflow-3/), [registry](https://mlflow.org/docs/latest/ml/model-registry/workflow/). |
| Kubeflow Pipelines | Cache configurable by task and at other levels; a submission setting can override that of the task. | The 117 topic specifies the overrides and the verification of the effective run. [Documentation of the cache](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/). |
| Features and TTL | The historic window alone is not a guarantee of business freshness or past availability. | The distinctions in the 119 form remain relevant. [Historic Feast Joints](https://docs.feast.dev/getting-started/concepts/point-in-time-joins). |
| MCP 2026-07-28 | Remove protocol sessions and handshake; capabilities accompany requests. | The base of the 33 plug is confirmed, without claiming that the business state disappears. [Changelog Versioned](https://modelcontextprotocol.io/specification/2026-07-28/changelog). |
| Enregistrement OAuth MCP | Client ID Metadata Privileged documents; pre-registration and DCR remain documented. DCR is deprecated, not deleted. | Fixed 115. [Registration of customers](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration). |
| Business authorization MCP | Explicit extension with necessary support of participants and IdP policies. | The 115 no longer presents this mechanism as an automatic property of any connection MCP. [Extension officielle](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization). |
| Identity AIMS/WIMSE | `draft-ietf-wimse-aims-01`, published on 2 November, It is an Internet-Draft. | The 115 topic distinguishes standardization work, standard and product. [Datatracker IETF](https://datatracker.ietf.org/doc/html/draft-ietf-wimse-aims-01). |
| Agent 365 | Commercial availability since the 1 May 2026, with prerequisites and integrations. | The 115 topic limits the coverage announced to agents actually integrated or discovered. [Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-agent-365/overview). |
| AWS Registry | Current documentation uses **AWS Agent Registry**. | Name and perimeter differences specified in the form 38. [AWS Release Notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html). |
| Optimization of agents | The recommendations do not prove a win and do not authorize a promotion. | The 115 topic keeps independent validation and verification of the status of each function. [AWS](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html), [Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform/). |
| Managed Agents | Beta status; service-side session storage and documented ZDR non-eligibility. | The 38/115 topics separate hosted service and only self-hosted sandboxes. [Overview Claude](https://platform.claude.com/docs/en/managed-agents/overview). |
| Managed Agents fully self-hosted | Accessible mode on request; the organization retains sessions and model calls follow the vendor's contract. | Removal of non-ZDR generalization to all modes. [Data and access](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access). |
| OpenAI Control Plane | **OpenClaw Enterprise** is presented as open source and still in the pilot phase; the 1.0 lens does not constitute an acquired general availability. | 38 file specified. [Billet officiel OpenAI](https://developers.openai.com/blog/securing-persistent-agents-like-openclaw-at-openai). |
| Agent Builder | Depreciation announced on the 3 June; closure scheduled on **30 November 2026**, still future on the day of this review. | The 38 topic gives the deadline and reminds that the export requires reconfiguration and validation. [Documentation officielle OpenAI](https://developers.openai.com/api/docs/guides/agent-builder), [migration](https://developers.openai.com/api/docs/guides/agent-builder/migrate-from-agent-builder). |
| OWASP LLM | The edition **2026** reorders identifiers and expands the exposure of the hidden context. | Updated 101/105 topics; 115 topic distinguishes between LLM and ASI agent lists. [Ressource 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/), [PDF officiel](https://genai.owasp.org/download/56857/). |
| AI Act | The amended timetable remains relevant, with distinct transitions by disposition and role. | 155 topic specified for GPAIs prior to 2 August 2025 and the marking of certain existing systems at 2 December 2026. [Amended Article 111](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-111), [Amending Regulation](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng). |

## Points that required careful reading of the sources

**OWASP: An official URL can expose an old edition.** The[index historical](https://genai.owasp.org/llm-top-10/) Poster again 2025, While the resource 2026 and its PDF are published separately. The PDF also contains date fields still to be completed: we rely on the edition and the content served, without inventing a precise publication date from these placeholders. For example, Excessive Agency Passes **LLM06:2025 by LLM03:2026**, and System Prompt Leakage is expanded to **Hidden Context Exposure, LLM08:2026**. Maintaining an old analysis requires preserving its editing and checking its correspondences.

**Hosting: locating the sandboxes does not necessarily locate the sessions.** In the configuration with only self-hosted sandboxes, the orchestration remains at Anthropic. In the fully self-hosted service, the storage and operation change perimeter; model calls remain subject to their own conditions. A ZDR contract for these calls does not erase the sessions, logs and backups kept by the organization.

**AI Act: read the amended provision rather than generalize a date.** Regulation (EU) 2026/1744 is an adopted text, Not just a proposal. It maintains separate dates for high-risk categories and adds targeted transitional provisions. Postponement of marking of the article 50(2) does not defer all transparency obligations. The schedule also cites the new prohibitions identified in the article. 113(a) applicable to 2 December 2026 ; the precise qualification remains to be checked in the text for each use.

## What this control does not allow to affirm

This Pass **does not certify each statement of 150 topics**. It does not fully recheck all prices, limits of context, benchmarks, CVE, SDK and offers mentioned elsewhere. The other general dates remain in place. The versions `latest` documentary sites may evolve after this consultation; Use a specific version during an implementation.

The six-month automatic threshold is a maintenance alert. A service may change before this time. Before a new deployment, check changelog, depreciation, access conditions, regions and data contract of the retained dependencies. A lint test confirms structure and internal links; it does not prove the accuracy of external sources or regulatory compliance.

## Validation of delivery

The comparative control finds the **2,440 questions and identifiers**, without addition or withdrawal, and exactly the **14 answers** described above. `make check` passes: **54 tests**, ruff, mypy, catalogs and two workshops. The lint does not signal any error or warning.

The Anki export is generated and then inspected: **2,440 active cards** with the expected IDs and **71 old cards removed always suspended**. The last corrections are included in the package. The CI must also succeed before merging; its results and publication are recorded in the PR.
