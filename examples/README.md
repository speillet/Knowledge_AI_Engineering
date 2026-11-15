# Practical workshops

Run these workshops from the repository root with **Python 3.10 or newer**. They use synthetic data and run locally; no API key or GPU is needed. The support-agent workshop requires a one-time dependency installation with internet access.

| Workshop | Prerequisites | Command | Expected result |
| --- | --- | --- | --- |
| [AI decisions](ai-decisions/README.md) | Basic arithmetic; [validation and metrics](../170-classical-ml/172-ml-validation-metrics.md) | `python3 examples/ai-decisions/decisions_workshop.py` | Four checked exercises: precision, human review, model choice and document quality |
| [Data engineering](data-engineering/README.md) | Basic SQL; [grain and keys](../150-data-compliance/150-010-analytical-data-modeling.md) | `python3 examples/data-engineering/sql_workshop.py` | Seven cases, 14 verified SQL results |
| [Verifiable RAG](verifiable-rag/README.md) | [RAG fundamentals](../20-rag/21-rag-fundamentals.md); evidence and access rules | `python3 examples/verifiable-rag/rag_workshop.py` | Filtered policy passes 10/10 contracts; baseline passes 0/10 on the supplied cases |
| [Support agent](agentic-support/README.md) | [Tool calling](../30-agents/32-tool-calling.md), [LangGraph](../40-automation/44-langgraph-fundamentals.md); install dependencies below | `.venv-agentic/bin/python examples/agentic-support/demo.py` | Approval, refusal and crash recovery produce 1, 0 and 1 effects; model quality remains unevaluated |

New to the vault? The [first session](../START_HERE.md) walks through one AI decision exercise.

## Predict, run, explain

For AI decisions and RAG, append `--questions` to read the exercises before the solutions. For SQL, inspect the schema and queries before running them. For the support agent, predict the effect of a crash between the business transaction and the graph checkpoint.

After running a workshop, change one assumption and explain the result. Each workshop guide specifies a deliverable and the limits of its simulation.

## Install the support-agent dependencies

From the repository root:

```bash
python3 -m venv .venv-agentic
.venv-agentic/bin/python -m pip install -r examples/agentic-support/requirements-lock.txt
.venv-agentic/bin/python examples/agentic-support/demo.py
.venv-agentic/bin/python -m unittest discover -s examples/agentic-support -p 'test_*.py' -v
```

On Windows, use `.venv-agentic\Scripts\python.exe` in place of `.venv-agentic/bin/python`. The demo uses temporary SQLite databases, a simulated model and an in-memory trace exporter. The optional local API and its storage are documented in the [support-agent guide](agentic-support/README.md).

## Check your changes

`make workshops` runs the SQL and AI decision assertions. `make test` includes the RAG tests and requires the [development dependencies](../CONTRIBUTING.md#maintenance). The 18 support-agent tests use their separate dependency environment and command above.

[Learning paths](../docs/paths/README.md) · [Learning guide](../docs/guides/learning-with-flashcards.md) · [Home](../README.md)
