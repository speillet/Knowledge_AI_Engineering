# Tool calling — Flashcards
Tags: #flashcards #ai-engineering #agents #tool-calling #llm
<!-- summary: définition des outils, appels parallèles contrôlés, tool calling ou MCP, validation des arguments, erreurs et timeouts, statuts d’opération, pagination et coût des schémas. -->


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
Par une définition comprenant **nom, description et schéma des paramètres**, selon le format du fournisseur. Exemple au format Anthropic :
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
Les contraintes supportées (types, motifs, énumérations) décrivent les arguments attendus ; leur application dépend du mode utilisé ([[63-guided-generation|guided generation]]). Ces définitions occupent du contexte à chaque appel : 40 outils, c'est des milliers de tokens à chaque tour ([[123-caching-agressif|caching]]).

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
Plusieurs demandes d'outils émises lors d'une même réponse du modèle. L'application peut les exécuter simultanément **après avoir vérifié leur indépendance** : deux recherches sans dépendance peuvent se paralléliser ; une écriture suivie d'une lecture de son résultat doit attendre.

Le modèle peut proposer des appels incompatibles ou concurrents sur la même ressource. Respecter le protocole des résultats, les permissions et les limites de concurrence, puis transmettre les succès et échecs partiels avec leurs identifiants. Le gain de latence dépend des dépendances et de la capacité des services appelés.

---

À ne pas confondre : tool calling et MCP ? <!--anki:7154542972474730592e-->
?
Le **tool calling** est le mécanisme par lequel un modèle propose un nom d'outil et ses arguments ; l'application contrôle puis exécute la demande. **MCP** organise les échanges entre clients et serveurs pour exposer outils, ressources et prompts.

On peut utiliser des outils codés directement sans MCP. Inversement, un client peut lire une ressource ou invoquer un outil MCP depuis du code ou une interface, sans décision d'un LLM. MCP ne dépend donc pas du tool calling natif d'un modèle ; les deux se combinent dans un agent.

---

Que faire quand un outil échoue ? <!--anki:4d4a3b542c376265564f-->
?
Distinguer **arguments invalides, refus d'autorisation, panne temporaire et résultat inconnu**. Fournir une erreur structurée et actionnable lorsque le modèle peut corriger sa demande.
```text
INVALID_ARGUMENT : commande_id doit suivre CMD-000000.
Utiliser rechercher_commandes si l'identifiant est inconnu.
```
Borner les relances ; ne pas exposer secrets ni traces internes. Un timeout après une écriture peut cacher un succès : vérifier l'état ou le statut de l'opération avant de la répéter. Un refus de permission ne se contourne pas par un autre outil. Le harness doit pouvoir arrêter ou escalader les échecs non récupérables.

---

Pourquoi la description des outils est-elle critique ? <!--anki:457254495d344e7c3357-->
?
Le **nom, la description et le schéma** orientent le choix de l'outil et de ses arguments, avec la consigne, l'historique et les observations déjà disponibles.
- Vague : `search(q)` — « Recherche. »
- Explicite : `rechercher_commandes(email_client)` — « Liste les commandes, les plus récentes d'abord ; ne fournit pas le suivi du colis. »

Préciser cas d'usage, limites et structure du résultat aide le modèle à choisir. Mesurer les erreurs sur des tâches représentatives ; une bonne description n'accorde aucun droit et ne dispense pas de valider l'appel.

---

Sur quoi repose la fiabilité syntaxique des arguments ? <!--anki:446e47724d4a2d696c7b-->
?
Un **décodage contraint** peut imposer un schéma supporté lors de la génération. Cette propriété dépend du modèle, du mode et des contraintes réellement prises en charge ; déclarer un JSON Schema ne suffit pas à l'activer.

Vérifier que l'appel est complet et exploitable : refus, erreur ou troncature exigent un traitement distinct. Puis valider les arguments côté serveur. Leur **validité sémantique** reste indépendante du format : un identifiant bien formé peut viser un autre client, un montant dépasser un plafond. Voir la [[63-guided-generation|guided generation]].

---

Calcul : 40 schémas d’outils de 300 tokens sont renvoyés à chacun des 25 appels d’un agent. Quel volume et coût à 3 €/M en entrée, puis quel coût si tous ces tokens sont lus à 10 % du tarif depuis un cache déjà chaud ? <!--anki:3232623534646231383763363464303539666437323536306133333231383237-->
?
Hypothèses : 300 tokens par schéma d'outil, renvoyés à chaque appel, 3 €/M en entrée.
```text
schémas   : 40 × 300          = 12 000 tokens à chaque appel
par tâche : 12 000 × 25 tours = 300 000 tokens ≈ 0,90 €
avec prompt caching (≈ 0,1×)  ≈ 0,09 €, mais le contexte reste occupé
```
Au-delà du coût, 12 000 tokens de schémas occupent du contexte et peuvent compliquer le choix d'outil : on n'expose que les outils utiles à la tâche, ou on les charge à la demande ([[35-context-engineering|context engineering]]).

---

Que doit exposer le résultat d'un outil pour éviter un faux succès d'agent ? <!--anki:6464383461663535363034323436316639313236656439633664643934316637-->
?
Un **statut exploitable**, les données nécessaires et leurs limites : erreur, résultat partiel, version consultée ou opération encore en cours.
```json
{"status": "pending", "operation_id": "op-42", "completed": false}
```
Un accusé de réception ne prouve pas que l'action est terminée. Prévoir une consultation de statut ou un vérificateur métier, et associer chaque résultat au bon appel. Le contrat doit permettre de distinguer « aucune donnée », « recherche incomplète » et « service indisponible », sinon le modèle peut inventer une conclusion.

---

Pourquoi la pagination d'un outil peut-elle fausser la conclusion d'un agent ? <!--anki:3330393863376537633037333466303339633164323932626139346537333561-->
?
Un résultat **limité à une page** ne représente pas nécessairement toute la collection. L'agent peut conclure « aucune commande récente » après avoir lu seulement les premiers éléments d'un autre tri.

Indiquer filtres, ordre, limite, présence d'une suite et curseur de continuation. Préférer un filtre ou une agrégation côté service pour une question globale. Si le budget ne permet pas de parcourir toutes les pages, annoncer le périmètre réellement consulté. Évaluer les tâches dont la preuve se trouve après la première page.

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
1. **Qualifier l'opération** : lecture sans effet ou écriture dont le résultat est inconnu.
2. **Réconcilier l'état** après une écriture : consulter le statut avant de répéter.
3. **Borner les relances** réessayables, avec échéance, backoff et clé d'idempotence si le service la gère.
4. **Transmettre un statut clair** au modèle ; les refus et paramètres invalides ne se traitent pas comme une panne réseau.
5. **Vérifier le résultat métier**, puis arrêter ou escalader si l'incertitude persiste.

**Piège** : supposer qu'un timeout signifie que l'action n'a pas eu lieu.

---

Mise en situation : un agent affirme qu'un client n'a aucune facture impayée après avoir lu 20 factures, mais l'outil renvoie aussi un curseur de continuation. Comment corriges-tu ? <!--anki:3339626162663531323736303465376139363334636464656665643732633261-->
?
1. **Vérifier le contrat** : filtre, tri et signification du curseur.
2. **Chercher côté service** les impayés, ou parcourir les pages si aucune requête ciblée n'existe.
3. **Distinguer complet et partiel**, avec un budget et un statut explicites.
4. **Vérifier la conclusion** sur des clients dont l'impayé se trouve sur une page ultérieure.
5. **Restituer l'incertitude** si la vérification reste incomplète.

**Piège** : transformer l'absence d'un élément dans la page lue en preuve de son absence globale.

---

## Sources

- [MCP 2025-11-25 — outils et invocation par le client](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- [MCP 2025-11-25 — ressources pilotées par l’application](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)
- [Anthropic — définir des outils](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
- [Anthropic — concevoir les résultats et évaluer les outils](https://www.anthropic.com/engineering/writing-tools-for-agents)

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
