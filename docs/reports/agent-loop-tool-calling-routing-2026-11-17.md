# Agent loops, tool calling and routing review — 17 November 2026

The review checked whether existing topics clearly explain tool calling, routing, ReAct, agent execution and stopping criteria. The concepts were present, but scattered explanations and awkward translations obscured the distinction between generating a call, executing it and verifying task completion.

## Coverage

| Topic | Previous cards | Reviewed cards | Main changes |
| --- | ---: | ---: | --- |
| [Agent fundamentals](../../30-agents/31-agent-fundamentals.md) | 14 | 26 | ReAct, task state, runtime control, success evidence, stop outcomes, budget reserves, stagnation and cancellation |
| [Tool calling](../../30-agents/32-tool-calling.md) | 19 | 27 | Selection and dispatch, missing arguments, complete streamed calls, tool-choice modes, call IDs versus idempotency, results and recovery |
| [Workflow patterns](../../40-automation/48-agentic-workflow-patterns.md) | 16 | 23 | Branch versus model routing, multi-intent requests, handoffs, acceptance contracts, ReAct versus planning, bounded revision |
| [LLM routing](../../80-api-layer-routing/82-routing-llm.md) | 16 | 22 | Eligibility, calibrated score interpretation, cascades, fallback, shared budgets, per-step model selection and evaluation |

The update adds **33 cards** and preserves all **2,870 existing active note identifiers**. The repository contains **155 topics and 2,903 active cards**, including **387 scenarios** and **222 do-not-confuse cards**. The four reviewed topics contain 98 cards in total.

The [worked learning path](../paths/agent-loop-tool-calling-routing.md) connects the four topics through an invoice-export example. Tables distinguish decision responsibilities, observations, next actions and stopping outcomes. The existing learning-path index links to it.

## Corrections and review scope

ReAct is distinguished from RL training and from reasoning without external observations. It does not require a large model on every step or exposure of private reasoning. Plan-and-execute is not universally cheaper; voting does not guarantee improvement when failures correlate.

Model output, tool-call completion and business-task completion are separate events. Timeouts can leave effects unknown; cancellation does not imply rollback. Pending exports, incomplete pagination and missing evidence cannot justify a success claim. An unconditional required-tool setting can obstruct a normal final response.

Routing now distinguishes a workflow branch, a model backend and a tool operation. Handoffs retain task identity and budgets. Similarity and confidence scores are not automatically calibrated success probabilities. Cascades stop when missing information, eligibility or exhausted resources prevent useful escalation.

The review uses primary ReAct, Reflexion and RouteLLM papers; Anthropic's workflow and tool references; current Claude tool-result and stop-reason documentation; MCP 2025-11-25; vLLM's strictness documentation; and Python and AWS runtime guidance. Links are included in the topics. The tool-calling verification date covers the checked protocol and vLLM claims; implementations and defaults can change.

State labels, budgets, costs and traces are illustrative. The Python composition sketch assumes application functions and is not a complete runtime. No model-quality, latency or cost benchmark was performed.

## Validation

- Topic structure, cross-links, generated catalogs and repository statistics: no errors or warnings.
- Existing Anki note identifiers retained; the model and historical deck identity configuration is unchanged.
- Numerical examples independently recalculated, including budgets, cascade costs, chain success and majority voting.
- Full repository checks pass: Python lint, type checks, 72 unit tests and both executable workshops.
- Anki export contains 2,974 unique notes: 2,903 active and 71 suspended retired notes. All four historical deck IDs are retained.
- Hugo extended 0.169.0 builds without warnings, and validation finds no broken links across 218 pages. The four pages render 26, 27, 23 and 22 collapsed cards; the learning path renders five comparison or trace tables with collapsible subsections.

[Review reports](README.md) · [Learning paths](../paths/README.md)
