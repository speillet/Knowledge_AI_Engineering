# CrewAI — Crews — Flashcards
Tags: #flashcards #ai-engineering #agents #crewai #llm

Qu'est-ce que CrewAI ?
?
Un framework Python **multi-agents par rôles**, écrit **indépendamment de LangChain**. On décrit une équipe (**crew**) d'agents spécialisés et les **tâches** qu'ils doivent accomplir ; les **Flows** ([[47-crewai-flows|CrewAI Flows]]) orchestrent le tout.

---

Comment définit-on un agent CrewAI ?
?
Par trois champs en langage naturel qui forment son prompt :
- **role** : sa fonction (« Analyste veille IA »)
- **goal** : son objectif
- **backstory** : son contexte et son style
Plus ses `tools`, son `llm` et des réglages (`max_iter`, `reasoning`, `verbose`…).

---

Comment définit-on une tâche ?
?
Par une **`description`** (quoi faire), un **`expected_output`** (à quoi ressemble le résultat attendu) et l'**`agent`** responsable. Le champ `context` liste les **tâches dont la sortie** doit être fournie à celle-ci.

---

À quoi ressemble une crew minimale ?
?
```python
from crewai import Agent, Task, Crew, Process

analyste = Agent(
    role="Analyste veille IA",
    goal="Trouver les annonces importantes sur {topic}",
    backstory="Tu suis l'actualité IA et tu vérifies toujours tes sources.",
    tools=[search_tool],
)
veille = Task(
    description="Liste les 5 annonces majeures de la semaine sur {topic}.",
    expected_output="Liste à puces : titre, date, source, résumé en une phrase.",
    agent=analyste,
)
crew = Crew(agents=[analyste], tasks=[veille], process=Process.sequential)
resultat = crew.kickoff(inputs={"topic": "agents LLM"})
```
Les `{variables}` sont remplacées par les `inputs` du kickoff.

---

Quels modes d'exécution (process) existent ?
?
- **Sequential** : les tâches s'exécutent **dans l'ordre**, chaque sortie alimente la suivante
- **Hierarchical** : un **agent manager** (`manager_llm` ou `manager_agent` obligatoire) **répartit** les tâches et **valide** les résultats

---

Qu'est-ce que la délégation ?
?
Avec `allow_delegation=True` (désactivé par défaut), un agent peut **confier une sous-tâche ou poser une question** à un autre agent de la crew. Pratique, mais cela multiplie les appels et rend l'exécution moins prévisible.

---

Comment obtenir une sortie structurée d'une tâche ?
?
Avec **`output_pydantic`** (ou `output_json`) sur la tâche : le résultat est validé contre le modèle. `output_file` écrit en plus le résultat dans un fichier.

---

Qu'est-ce qu'un guardrail de tâche ?
?
Une **validation de la sortie avant de passer à la suite** :
- **Fonction** Python qui renvoie `(succès, résultat_ou_erreur)`
- **Texte** décrivant la règle, vérifié par un LLM
En cas d'échec, l'agent **recommence** avec le message d'erreur.

---

Comment CrewAI se connecte-t-il aux LLM ?
?
Par la classe **`LLM`** et des chaînes `fournisseur/modèle` (ex. `"openai/gpt-4o"`, `"ollama/llama3:70b"`). SDK natifs pour les grands fournisseurs (OpenAI, Anthropic, Gemini, Azure, Bedrock), **LiteLLM** pour les autres — on peut donc aussi viser un [[81-litellm-api-layer|proxy LiteLLM]].

---

Comment fonctionnent les outils dans CrewAI ?
?
Le paquet **`crewai-tools`** fournit des outils prêts (recherche web, scraping, lecture de fichiers, RAG…) ; on crée les siens avec le décorateur **`@tool`** ou en héritant de `BaseTool`. Les serveurs [[33-mcp|MCP]] sont aussi utilisables.

---

Comment fonctionne la mémoire dans CrewAI ?
?
Une classe **`Memory` unifiée** (qui remplace les anciennes mémoires court terme, long terme et entités) : `memory=True` sur la crew suffit. Les souvenirs sont retrouvés par **score combiné** (similarité sémantique, récence, importance), stockés par défaut en local (LanceDB).

---

Comment est organisé un projet CrewAI ?
?
La CLI (`crewai create`, `crewai install`, `crewai run`) génère un projet. Les versions récentes décrivent agents et crew en **JSONC** (`crew.jsonc`, dossier `agents/`) ; beaucoup d'exemples utilisent encore l'ancienne forme **YAML** (`agents.yaml`, `tasks.yaml`) avec les décorateurs `@CrewBase`, `@agent`, `@task`, `@crew`.

---

Quelles sont les limites des crews ?
?
Le comportement repose sur des **prompts de rôle** : moins de contrôle fin que [[44-langgraph-fondamentaux|LangGraph]], exécution **moins prévisible** en mode hiérarchique, et **coût en tokens** élevé. D'où l'usage de **Flows** pour encadrer les crews en production.

---

## Connexions
- [[47-crewai-flows|CrewAI — Flows]] — orchestrer les crews en production
- [[36-orchestration-agents|Orchestration multi-agents]] — sequential, hierarchical, délégation
- [[37-frameworks-agents|Frameworks d'agents]] — comparer avec LangGraph et ADK
- [[81-litellm-api-layer|LiteLLM]] — la couche d'accès aux modèles
- [[101-securite-llm-guardrails|Sécurité LLM]] — guardrails et outils
- [[00-moc-ai-engineering|MOC AI Engineering]]
