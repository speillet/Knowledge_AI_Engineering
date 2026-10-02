# Prompts en production — Flashcards
Tags: #flashcards #ai-engineering #prompt-engineering #production #llm
<!-- summary: briques d'un prompt, placement des longs documents, consignes motivées, limites des rôles, prompter un modèle de raisonnement, templates et données utilisateur, registre et versioning, prompt dans le code ou dans un registre, portabilité entre modèles, langue, contrôle de la longueur. -->


Quelles sont les briques d'un prompt de production ? <!--anki:775f2e70434e484c4021-->
?
1. **Rôle et périmètre** : qui répond, pour qui, ce qui est hors sujet
2. **Contexte** : documents, données utilisateur, état de la conversation
3. **Tâche et critères de réussite** : ce qu'est une bonne réponse
4. **Contraintes** : ton, longueur, règles métier, conduite en cas de doute
5. **Format de sortie**, idéalement contraint ([[63-guided-generation|guided generation]])

Les **exemples** viennent en plus, quand le format ou le jugement attendu sont difficiles à décrire.

---

Où placer les longs documents dans un prompt ? <!--anki:635d604a5d2428323726-->
?
**Documents en haut, question et consignes en bas.** Sur de longs contextes, poser la question **après** les documents améliore nettement les réponses, et rappeler brièvement la tâche à la fin aide le modèle à ne pas la perdre ([[137-long-contexte|lost in the middle]]).

C'est aussi l'ordre compatible avec le cache : **stable en tête**, variable à la fin ([[123-caching-agressif|caching]]).

---

Pourquoi expliquer le **pourquoi** d'une consigne ? <!--anki:443d7560577e47674929-->
?
Une consigne motivée se **généralise** : « réponds en phrases courtes, car la réponse sera lue par une synthèse vocale » amène aussi le modèle à éviter listes et symboles, que la consigne seule n'interdisait pas. Une règle nue est appliquée **à la lettre**, et seulement aux cas prévus.

---

Pourquoi « Tu es un expert en… » ne suffit-il pas ? <!--anki:70402569663046525a73-->
?
Un **rôle** règle surtout le **ton et le registre** ; il n'apporte pas de connaissances et améliore peu l'exactitude. Ce qui change la qualité : le **contexte** (données, public, enjeu), les **critères de réussite** et les **exemples**. Un bon rôle est **précis** (« analyste crédit qui prépare une note pour un comité ») plutôt que flatteur.

---

Comment prompter un modèle de raisonnement ? <!--anki:725b7449614f33655476-->
?
- Décrire **l'objectif, les contraintes et les critères** plutôt que les étapes : le modèle planifie mieux seul
- Ne pas imposer « réfléchis étape par étape », déjà natif ([[138-modeles-raisonnement|modèles de raisonnement]])
- Régler le **budget de réflexion** selon la difficulté, pas au maximum par défaut
- Garder les exemples **cohérents** : ils influencent aussi le raisonnement

---

Comment injecter des données utilisateur dans un template sans risque ? <!--anki:63687347434c42302e68-->
?
- **Délimiter** les données (balises XML) et dire que ce qu'elles contiennent n'est **pas une instruction**
- **Échapper** ou refuser les balises de fermeture dans les données, pour qu'un utilisateur ne sorte pas de son bloc
- Ne jamais **concaténer** une entrée utilisateur dans le system prompt
- Rendre le template avec un moteur **sans exécution de code** (Jinja en bac à sable)

Cela limite l'injection accidentelle, sans remplacer les défenses contre l'injection volontaire ([[101-securite-llm-guardrails|sécurité]]).

---

Comment versionner et déployer un prompt ? <!--anki:45322d48647e3977733d-->
?
- **Registre de prompts** : chaque version est immuable et numérotée, avec des **étiquettes** d'environnement (`staging`, `production`) ([[91-langfuse-observabilite|Langfuse]])
- La version est **tracée** avec chaque réponse, pour relier une régression à un changement
- **Eval gate** avant de déplacer l'étiquette `production` ([[112-cicd-modeles|CI/CD]])
- **Retour arrière** en déplaçant l'étiquette, sans redéployer le code

Le prompt, le modèle et ses paramètres se versionnent **ensemble** : un prompt n'a de sens que pour un modèle donné.

---

À ne pas confondre : prompt dans le code et prompt dans un registre ? <!--anki:634257615e2a3559405e-->
?
- **Dans le code** (Git) : revue de code, tests et déploiement avec l'application. Simple, mais chaque changement demande une livraison
- **Dans un registre** : modifiable par des non-développeurs et déployable en minutes. Mais le prompt peut changer **sans commit**, donc il faut une eval gate et des traces

Choix courant : **code** pour les prompts couplés à la logique, **registre** pour ceux que le métier ajuste souvent.

---

Pourquoi un prompt ne se transfère-t-il pas tel quel d'un modèle à l'autre ? <!--anki:6f3d475e6263602d6e31-->
?
Chaque famille de modèles a été entraînée avec ses propres conventions : sensibilité aux **balises**, au **few-shot**, aux **majuscules** et aux consignes insistantes, verbosité par défaut. Une consigne en « TU DOIS » utile sur un ancien modèle fait **sur-réagir** un modèle récent plus obéissant.

Toute migration de modèle se traite comme un **changement de code** : on rejoue l'eval complète ([[146-choix-modeles|migration]], [[12-optimisation-automatique-prompts|recompilation]]).

---

Faut-il écrire le prompt en anglais pour une application francophone ? <!--anki:46342128794b4e28727b-->
?
**Pas forcément.** Les modèles récents suivent bien des consignes en français. Ce qui compte :
- Dire explicitement la **langue de réponse** (celle de l'utilisateur, ou toujours le français)
- Garder des **exemples dans la langue cible** : le modèle imite leur langue
- **Mesurer** sur son jeu d'eval les deux versions, en coût aussi : l'anglais consomme moins de tokens ([[132-tokenisation|tokenisation]])

---

Comment contrôler la longueur des réponses ? <!--anki:477e60346d663b39685b-->
?
- Donner une **cible concrète** (« 3 phrases », « moins de 120 mots ») plutôt que « sois concis »
- Montrer des **exemples** de la bonne longueur
- Fixer `max_tokens` comme **garde-fou**, pas comme réglage : une coupure produit une réponse tronquée
- Surveiller la **longueur moyenne en production**, qui dérive avec les changements de modèle et pèse sur coût et latence ([[121-couts-inference|coûts]])

---

## Mises en situation

Mise en situation : un changement de prompt « mineur » poussé le vendredi a fait chuter la satisfaction de 15 % pendant le week-end, et personne ne sait quelle version tournait. Que mets-tu en place ? <!--anki:693f694d2a3d5d354c25-->
?
1. **Registre versionné** : versions immuables, étiquette `production`, historique des changements
2. **Traçabilité** : la version du prompt et du modèle attachée à chaque trace ([[91-langfuse-observabilite|traces]])
3. **Eval gate** : aucun changement d'étiquette sans passer le jeu de non-régression ([[112-cicd-modeles|CI/CD]])
4. **Déploiement progressif** : canary sur 5 % du trafic, avec les métriques de satisfaction surveillées ([[97-evals-online-ab-testing|evals online]])
5. **Retour arrière en un clic** : redéplacer l'étiquette, sans redéploiement

**Piège** : considérer un prompt comme de la configuration anodine, modifiable sans revue.

---

Mise en situation : ton assistant, qui résume des comptes rendus de 80 pages, oublie régulièrement les décisions prises en fin de document et répond parfois en anglais. Comment reprends-tu le prompt ? <!--anki:4854264e543b60743843-->
?
1. **Réordonner** : document en haut, consignes et question à la fin, avec un rappel bref de la tâche ([[137-long-contexte|long contexte]])
2. **Structurer la sortie** : une section « décisions » obligatoire dans le schéma, pour forcer leur recherche
3. **Fixer la langue** explicitement et donner l'exemple de sortie en français
4. **Mesurer** sur 30 comptes rendus annotés : décisions retrouvées et langue correcte
5. **Découper si besoin** : extraire les décisions par section, puis synthétiser

**Piège** : ajouter « N'OUBLIE PAS LES DÉCISIONS » en majuscules sans changer la structure du prompt.

---

## Connexions
- [[11-prompt-engineering-avance|Prompt engineering avancé]] — les techniques de base
- [[12-optimisation-automatique-prompts|Optimisation automatique]] — générer les prompts plutôt que les écrire
- [[35-context-engineering|Context engineering]] — le prompt dans le budget de contexte
- [[91-langfuse-observabilite|Langfuse]] — registre et traçabilité
- [[112-cicd-modeles|CI/CD des modèles]] — eval gate avant production
- [[137-long-contexte|Long contexte]] — placement des documents
- [[138-modeles-raisonnement|Modèles de raisonnement]] — prompter l'objectif, pas les étapes
- [[101-securite-llm-guardrails|Sécurité LLM]] — données utilisateur dans les templates
- [[00-moc-ai-engineering|MOC AI Engineering]]
