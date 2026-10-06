# Tool calling — Flashcards
Tags: #flashcards #ai-engineering #agents #tool-calling #llm
<!-- summary: déclaration par JSON Schema, exécution contrôlée par l'application, boucle d'appel, parallel tool calls, tool calling ou MCP, erreurs d'outil actionnables, bonne et mauvaise description d'outil, validité syntaxique et sémantique des arguments. -->


Qu'est-ce que le tool calling (function calling) ? <!--anki:4c434c62492628352f4a-->
?
Le mécanisme par lequel un LLM **émet un appel structuré** (nom d'outil + arguments JSON) que **l'application exécute** avant de renvoyer le résultat au modèle.

Le modèle ne lance pas directement la fonction. L'application valide les arguments, l'autorisation et les limites, puis associe le résultat à l'identifiant d'appel attendu. Exemple : `statut_commande(id)` fournit un fait à utiliser dans la réponse. Une sortie conforme au schéma n'implique pas que les arguments soient légitimes ou corrects.

---

Le modèle exécute-t-il lui-même les outils ? <!--anki:672f7363513542412f2f-->
?
**Non.** Le modèle ne fait que **générer l'intention d'appel** (nom et arguments) ; c'est l'application, le harnais, qui exécute et renvoie le résultat.

Conséquence essentielle : c'est **dans l'application** qu'on contrôle ce qui s'exécute vraiment. Validation des arguments, permissions, approbation humaine et journalisation se placent entre l'intention du modèle et l'exécution ([[34-harness-plugins|harness]]).

---

Comment déclare-t-on un outil au modèle ? <!--anki:745d3a6878654160442b-->
?
Par un **JSON Schema** : nom, description et paramètres typés, envoyés à chaque requête.
```json
{
  "name": "statut_commande",
  "description": "Donne le statut d'une commande du client connecté.",
  "input_schema": {
    "type": "object",
    "properties": {
      "commande_id": { "type": "string", "pattern": "^CMD-[0-9]{6}$" }
    },
    "required": ["commande_id"]
  }
}
```
Les **contraintes du schéma** (types, motifs, énumérations) réduisent fortement les arguments invalides ([[63-guided-generation|guided generation]]). Ces définitions occupent du contexte à chaque appel : 40 outils, c'est des milliers de tokens à chaque tour ([[123-caching-agressif|caching]]).

---

À quoi ressemble la boucle de tool calling ? <!--anki:474750306946343634-->
?
```text
prompt → le modèle émet tool_call(name, args)
→ l'app exécute → résultat renvoyé au modèle
→ nouveau tool_call ou réponse finale
```

À chaque tour, l'application **valide le nom et les arguments**, contrôle les permissions, exécute avec un timeout et renvoie un résultat ou une erreur structurée. Le modèle peut alors corriger sa demande ou répondre. Conserver les identifiants d'appels et limiter les itérations. Pour une action avec effet externe, prévoir l'idempotence afin qu'une reprise ne crée pas de doublon.

---

Que sont les parallel tool calls ? <!--anki:482f5a41654854453b58-->
?
L'émission de **plusieurs appels d'outils indépendants en une seule réponse**, que l'application peut exécuter **simultanément** : trois recherches au lieu de trois allers-retours, donc une latence bien moindre.

Points d'attention : renvoyer **tous** les résultats avant de redonner la main au modèle, gérer les **échecs partiels**, et vérifier que les actions sont réellement **indépendantes** (deux écritures sur la même ressource ne le sont pas).

---

À ne pas confondre : tool calling et MCP ? <!--anki:7154542972474730592e-->
?
- **Tool calling** : le **mécanisme du modèle**. Il émet `nom + arguments`, l'application exécute
- **MCP** : le **protocole de mise à disposition** des outils. Il dit comment un serveur **déclare** ses outils et comment un client les **découvre** ([[33-mcp|MCP]])

Autrement dit : MCP **fournit** le catalogue, le tool calling **s'en sert**. On peut faire du tool calling sans MCP (outils codés en dur), mais pas l'inverse.

---

Que faire quand un outil échoue ? <!--anki:4d4a3b542c376265564f-->
?
**Renvoyer l'erreur au modèle** comme résultat d'outil, plutôt que de lever une exception : il peut corriger ses arguments, réessayer ou changer d'approche. Le message doit être **actionnable** :
```text
Erreur : commande_id "12345" invalide. Format attendu : CMD-000000
(6 chiffres). Utilise d'abord rechercher_commandes(email) si tu ne
connais pas l'identifiant.
```
Une trace brute (stack trace de 80 lignes) consomme du contexte et n'aide pas le modèle. Limiter aussi le nombre de tentatives par outil.

---

Pourquoi la description des outils est-elle critique ? <!--anki:457254495d344e7c3357-->
?
C'est du **prompt engineering** : le modèle choisit l'outil et remplit les arguments d'après le **nom**, la **description** et le **schéma**, rien d'autre.
- Mauvais : `search(q)` — « Recherche. »
- Bon : `rechercher_commandes(email_client)` — « Liste les commandes d'un client, les plus récentes d'abord. À utiliser avant tout remboursement. Ne donne pas le statut de livraison : utiliser suivi_colis. »

Dire **quand l'utiliser**, **quand ne pas l'utiliser** et à quoi ressemble le résultat réduit les erreurs de choix d'outil.

---

Sur quoi repose la fiabilité syntaxique des arguments ? <!--anki:446e47724d4a2d696c7b-->
?
Sur la **[[63-guided-generation|guided generation]]** : en mode strict, les arguments sont **contraints** par le JSON Schema de l'outil pendant la génération, donc toujours valides syntaxiquement.

La validité **sémantique** reste à vérifier par l'application : un identifiant bien formé peut ne pas exister, un montant peut dépasser la limite, une date peut être dans le passé. Valider côté serveur, et renvoyer une erreur explicite au modèle.

---

Calcul : combien de tokens coûtent les schémas de 40 outils sur une tâche d'agent de 25 tours ? <!--anki:3232623534646231383763363464303539666437323536306133333231383237-->
?
Hypothèses : 300 tokens par schéma d'outil, renvoyés à chaque appel, 3 €/M en entrée.
```text
schémas   : 40 × 300          = 12 000 tokens à chaque appel
par tâche : 12 000 × 25 tours = 300 000 tokens ≈ 0,90 €
avec prompt caching (≈ 0,1×)  ≈ 0,09 €, mais le contexte reste occupé
```
Au-delà du coût, 12 000 tokens de schémas **diluent l'attention** et dégradent le choix d'outil : on n'expose que les outils utiles à la tâche, ou on les charge à la demande ([[35-context-engineering|context engineering]]).

---

## Mises en situation

Mise en situation : ton agent dispose de 40 outils et se trompe souvent d'outil ou invente des paramètres. Comment améliores-tu la situation ? <!--anki:45503a33472d5921333f-->
?
1. **Réduire le choix** : n'exposer que les outils utiles à la tâche en cours, quitte à les filtrer dynamiquement
2. **Soigner les descriptions** : nom explicite, cas d'usage, ce que l'outil ne fait pas. C'est du prompt engineering
3. **Fusionner ou séparer** : regrouper des outils redondants, séparer ceux qui font trop de choses
4. **Contraindre les arguments** par le JSON Schema, avec des énumérations plutôt que du texte libre ([[63-guided-generation|guided generation]])
5. **Mesurer** : taux d'appels valides et de bons outils choisis, par outil, avant et après ([[96-evals-rag-agents|evals d'agents]])

**Piège** : ajouter un outil supplémentaire pour corriger les erreurs des précédents.

---

Mise en situation : un appel d'outil échoue en production avec un timeout, et ton agent réessaie en boucle avec les mêmes arguments. Que corriges-tu ? <!--anki:423c3d21382d71634132-->
?
1. **Renvoyer l'erreur au modèle** dans un message clair, avec la cause et la marche à suivre, plutôt qu'une trace brute
2. **Limiter les tentatives** par outil, avec backoff, et changer de stratégie après deux échecs
3. **Rendre l'appel idempotent** (clé d'idempotence), pour qu'un retry ne crée pas deux fois la même action ([[115-plateformes-agents-gouvernance|exécution durable]])
4. **Distinguer les erreurs** : réessayable (réseau, quota) ou définitive (droits, paramètre invalide)
5. **Surveiller** le taux d'erreurs par outil, signal classique de dérive ([[93-monitoring-inference|monitoring]])

**Piège** : masquer l'erreur au modèle, qui continue alors comme si l'action avait réussi.

---

## Connexions
- [[31-agents-fondamentaux|Agents]] — la boucle qui consomme les outils
- [[63-guided-generation|Guided generation]] — la garantie syntaxique
- [[33-mcp|MCP]] — standardiser l'accès aux outils
- [[34-harness-plugins|Harness]] — qui exécute réellement
- [[101-securite-llm-guardrails|Sécurité LLM]] — valider avant d'exécuter
- [[103-defenses-agents|Sécurité des agents — Architecture défensive]] — valider les appels d'outils
- [[165-computer-use-agents-navigateur|Computer use & agents navigateur]] — agents qui utilisent des interfaces
- [[22-rag-avance|RAG — Avancé]] — recherche hybride, reranking et filtres
- [[26-text-to-sql|Text-to-SQL]] — répondre aux questions chiffrées sur des tables
- [[37-frameworks-agents|Frameworks d'agents]] — panorama des frameworks
- [[41-automatisation-code-nocode|Automatisation code & no-code]] — workflows et outils no-code
- [[42-langchain-fondamentaux|LangChain]] — les briques de base du framework
- [[00-moc-ai-engineering|MOC AI Engineering]]
