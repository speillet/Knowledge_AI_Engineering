# CrewAI — Crews — Flashcards
Tags: #flashcards #ai-engineering #agents #crewai #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: agents (role, goal, backstory), tâches, process séquentiel ou hiérarchique, délégation, sorties structurées, guardrails de tâche, LLM et outils, mémoire unifiée, structure d'un projet. -->


Qu'est-ce que CrewAI ? <!--anki:773073683f6e7832596e-->
?
Un framework Python **multi-agents par rôles**, écrit **indépendamment de LangChain**. On décrit une équipe (**crew**) d'agents spécialisés et les **tâches** qu'ils doivent accomplir ; les **Flows** ([[47-crewai-flows|CrewAI Flows]]) orchestrent le tout.

Le rôle décrit une spécialisation, tandis que les outils déterminent ce que l'agent peut réellement faire. Une crew peut réaliser une analyse en plusieurs tâches ; un Flow encadre ses déclenchements et ses branches. Mesurer l'intérêt de la coopération par rapport à un pipeline plus simple avant de multiplier les agents.

---

Comment définit-on un agent CrewAI ? <!--anki:5064625e6870296b515a-->
?
Par trois champs en langage naturel qui forment son prompt :
- **role** : sa fonction (« Analyste veille IA »)
- **goal** : son objectif
- **backstory** : son contexte et son style
Plus ses `tools`, son `llm` et des réglages (`max_iter`, `reasoning`, `verbose`…).

---

Comment définit-on une tâche CrewAI ? <!--anki:412a4645332e30695766-->
?
Par une **`description`** (quoi faire), un **`expected_output`** (à quoi ressemble le résultat attendu) et l'**`agent`** responsable. Le champ `context` liste les **tâches dont la sortie** doit être fournie à celle-ci.

Une bonne tâche nomme les sources, le périmètre et les critères de réussite. `expected_output` est une consigne au modèle, pas à lui seul une garantie de conformité : ajouter un schéma ou un validateur si le résultat alimente du code. Éviter de transmettre toutes les tâches précédentes lorsqu'une seule suffit.

---

Comment construire et lancer une crew minimale avec CrewAI ? <!--anki:7129717e4e6e464e4c69-->
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

L'exemple comporte un agent et une tâche : une crew n'exige pas plusieurs agents. `search_tool` doit être défini, et le modèle ainsi que ses identifiants configurés. Le rôle et la biographie orientent la génération mais ne prouvent pas la véracité des annonces ; vérifier dates et sources dans le résultat.

---

Quels modes d'exécution (process) propose un crew CrewAI ? <!--anki:4f623b5a442b527c2b4d-->
?
- **Sequential** : les tâches s'exécutent **dans l'ordre**, chaque sortie alimente la suivante
- **Hierarchical** : un **agent manager** (`manager_llm` ou `manager_agent` obligatoire) **répartit** les tâches et **valide** les résultats

Le séquentiel convient lorsque les dépendances sont connues ; le hiérarchique ajoute une décision de coordination par modèle. Ce manager augmente les appels et peut mal déléguer. Dans les deux cas, expliciter le contexte nécessaire aux tâches et vérifier le résultat final avec des critères métier indépendants du rôle des agents.

---

Qu'est-ce que la délégation dans CrewAI ? <!--anki:67436a665f6224415725-->
?
Avec `allow_delegation=True` (désactivé par défaut), un agent peut **confier une sous-tâche ou poser une question** à un autre agent de la crew. Pratique, mais cela multiplie les appels et rend l'exécution moins prévisible.

Réserver cette capacité aux tâches qui gagnent réellement à demander une expertise complémentaire. Donner une question précise, des limites d'appels et un format de retour évite les échanges circulaires. Une délégation ne doit pas contourner les permissions : l'agent sollicité ne peut agir que dans le périmètre autorisé du système.

---

Comment obtenir une sortie structurée d'une tâche CrewAI ? <!--anki:4e2826512a3b38495426-->
?
Avec **`output_pydantic`** (ou `output_json`) sur la tâche : le résultat est validé contre le modèle. `output_file` écrit en plus le résultat dans un fichier.

Définir un modèle de résultat, par exemple une liste de constats avec source et gravité. Traiter explicitement l'échec de conversion ou de validation ; ne pas laisser un texte libre passer pour un objet valide. Le fichier produit reste un artefact à contrôler et sa destination doit être limitée au répertoire prévu.

---

Qu'est-ce qu'un guardrail de tâche dans CrewAI ? <!--anki:6761785230593f39772d-->
?
Une **validation de la sortie avant de passer à la suite** :
- **Fonction** Python qui renvoie `(succès, résultat_ou_erreur)`
- **Texte** décrivant la règle, vérifié par un LLM
En cas d'échec, l'agent **recommence** avec le message d'erreur.

---

Comment CrewAI se connecte-t-il aux LLM ? <!--anki:79632352695739716b3a-->
?
Par la classe **`LLM`** et des chaînes `fournisseur/modèle` (ex. `"openai/gpt-4o"`, `"ollama/llama3:70b"`). SDK natifs pour les grands fournisseurs (OpenAI, Anthropic, Gemini, Azure, Bedrock), **LiteLLM** pour les autres — on peut donc aussi viser un [[81-litellm-api-layer|proxy LiteLLM]].

---

Comment fonctionnent les outils dans CrewAI ? <!--anki:73416c25474152545177-->
?
Le paquet **`crewai-tools`** fournit des outils prêts (recherche web, scraping, lecture de fichiers, RAG…) ; on crée les siens avec le décorateur **`@tool`** ou en héritant de `BaseTool`. Les serveurs [[33-mcp|MCP]] sont aussi utilisables.

Un outil doit exposer un contrat clair : arguments, résultat, cas d'erreur et effets éventuels. Limiter les permissions du compte utilisé et les destinations réseau. Tester les fonctions séparément des agents ; une réponse plausible du LLM peut masquer un outil qui n'a jamais consulté la source ou qui a échoué.

---

Comment fonctionne la mémoire dans CrewAI ? <!--anki:4e7d6e76596a3b63702c-->
?
Une classe **`Memory` unifiée** (qui remplace les anciennes mémoires court terme, long terme et entités) : `memory=True` sur la crew suffit. Les souvenirs sont retrouvés par **score combiné** (similarité sémantique, récence, importance), stockés par défaut en local (LanceDB).

---

Comment est organisé un projet CrewAI ? <!--anki:432d2c4b733677595a61-->
?
La CLI (`crewai create`, `crewai install`, `crewai run`) génère un projet. Les versions récentes décrivent agents et crew en **JSONC** (`crew.jsonc`, dossier `agents/`) ; beaucoup d'exemples utilisent encore l'ancienne forme **YAML** (`agents.yaml`, `tasks.yaml`) avec les décorateurs `@CrewBase`, `@agent`, `@task`, `@crew`.

---

Quelles sont les limites des crews de CrewAI ? <!--anki:4b30352368505d537624-->
?
Le comportement repose sur des **prompts de rôle** : moins de contrôle fin que [[44-langgraph-fondamentaux|LangGraph]], exécution **moins prévisible** en mode hiérarchique, et **coût en tokens** élevé. D'où l'usage de **Flows** pour encadrer les crews en production.

---

## Mises en situation

Mise en situation : ta crew de veille produit de bons résultats en démonstration, mais en production elle invente parfois des sources et coûte trois fois le budget prévu. Que corriges-tu ? <!--anki:654e6e2d6840715d293c-->
?
1. **Contraindre les sorties** : `output_pydantic` sur les tâches, avec les champs source et date obligatoires
2. **Guardrails de tâche** : une fonction qui vérifie que chaque source est une URL atteignable, sinon l'agent recommence
3. **Réduire l'autonomie** : désactiver la délégation, limiter `max_iter`, préciser `expected_output`
4. **Encadrer par un Flow** : étapes déterministes autour de la partie ouverte ([[47-crewai-flows|Flows]])
5. **Mesurer** : coût par exécution et taux de sources valides, avant et après ([[122-finops-llm|FinOps]])

**Piège** : enrichir les backstories pour « demander plus de rigueur », sans aucune vérification automatique.

---

Mise en situation : un collègue propose de passer ta crew en mode hiérarchique pour améliorer la qualité. Quelles questions poses-tu ? <!--anki:4c776f6e2849474f357d-->
?
1. **Quel problème résout-on ?** Le mode hiérarchique ajoute un agent manager qui répartit et valide, donc **plus d'appels** et moins de prévisibilité
2. **Le séquentiel est-il vraiment insuffisant ?** Souvent, un `context` bien défini entre tâches suffit
3. **Quel modèle pour le manager ?** Un `manager_llm` faible dégrade tout le reste
4. **Comment mesurer ?** Même jeu de tâches, comparaison qualité, coût et latence ([[96-evals-rag-agents|evals d'agents]])
5. **Comment déboguer ?** En hiérarchique, retrouver l'origine d'une erreur est nettement plus difficile

**Piège** : adopter le mode hiérarchique parce qu'il « ressemble à une vraie équipe », sans mesure.

---

## Sources

- [CrewAI — crews](https://docs.crewai.com/en/concepts/crews)

- [CrewAI — Crews, documentation v1.15.23](https://docs.crewai.com/v1.15.23/en/concepts/crews)

## Connexions
- [[47-crewai-flows|CrewAI — Flows]] — orchestrer les crews en production
- [[36-orchestration-agents|Orchestration multi-agents]] — sequential, hierarchical, délégation
- [[37-frameworks-agents|Frameworks d'agents]] — comparer avec LangGraph et ADK
- [[81-litellm-api-layer|LiteLLM]] — la couche d'accès aux modèles
- [[101-securite-llm-guardrails|Sécurité LLM]] — guardrails et outils
- [[39-memoire-agents|Mémoire des agents]] — les concepts derrière la mémoire unifiée
- [[00-moc-ai-engineering|MOC AI Engineering]]
