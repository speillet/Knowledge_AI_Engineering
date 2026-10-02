# Pipelines batch à grande échelle — Flashcards
Tags: #flashcards #ai-engineering #batch #system-design #couts #llm
Vérifié le : 30 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: batch ou en ligne, batch API (JSONL, `custom_id`, 24 h), batch API ou continuous batching, architecture reprenable, calculs de coût et de durée sous quota, classement des erreurs, contrôle qualité statistique, versions enregistrées avec chaque résultat, auto-hébergement hors ligne, quand ne pas utiliser de batch API. -->


Quand traiter des données par LLM en batch plutôt qu'en ligne ? <!--anki:73254754575550477a61-->
?
Quand **personne n'attend la réponse** : extraction sur un stock de documents, classification d'un historique de tickets, enrichissement d'un catalogue, génération d'embeddings, evals massives. On optimise alors le **coût et le débit**, plus la latence.

Gains typiques : **−50 %** avec une batch API, GPU auto-hébergés à **pleine charge**, et aucune contrainte de SLO de latence ([[121-couts-inference|coûts]]).

---

Comment fonctionne une batch API de fournisseur ? <!--anki:6f605b3045597429645b-->
?
1. Préparer un fichier **JSONL**, une requête par ligne, chacune avec un **`custom_id`**
2. Soumettre le lot, traité de façon asynchrone sous **24 heures**
3. Récupérer un fichier de résultats, **dans le désordre**, rapprochés par `custom_id`
4. Retraiter les lignes **en erreur**

Prix réduit d'environ **50 %**, et des quotas séparés du trafic en ligne. Le `custom_id` doit être l'identifiant **métier** de l'item, pas un numéro de ligne.

---

À ne pas confondre : batch API et batching du serveur d'inférence ? <!--anki:4c374d2b252d29546352-->
?
- **Batch API** : un **mode de facturation et de livraison** du fournisseur. On soumet un lot, résultats sous 24 h, prix réduit
- **Batching du serveur** (continuous batching) : une **technique d'exécution** du GPU, qui regroupe les requêtes en cours pour partager la lecture des poids. Elle tourne en permanence, en ligne comme hors ligne ([[62-optimisations-inference|continuous batching]])

Le premier se choisit, le second est automatique dans vLLM ou SGLang.

---

Quelle architecture pour un pipeline batch de plusieurs millions d'items ? <!--anki:4d3f24336e7d3844763e-->
?
```text
source → découpage en items (id stable) → file de travail
       → workers : prompt + appel modèle + validation
       → résultats (avec statut, versions) → contrôle qualité
       ↘ erreurs → file de rejets (dead letter) → reprise
```
Chaque item a un **statut** (à faire, fait, en erreur) persisté : on peut interrompre, reprendre et relancer seulement ce qui a échoué. Orchestration : Airflow, Dagster, Prefect, ou Ray Data et Spark pour le gros volume.

---

Calcul : combien coûte l'extraction de 2 millions de documents ? <!--anki:797842345d605833776e-->
?
Hypothèses : 3 000 tokens d'entrée (dont 1 000 d'instructions communes), 300 en sortie, 3 €/M en entrée, 15 €/M en sortie.
```text
entrée : 2 M × 3 000 = 6 G tokens  × 3 €/M  = 18 000 €
sortie : 2 M ×   300 = 0,6 G       × 15 €/M =  9 000 €
en ligne                                    ≈ 27 000 €
batch API (−50 %)                           ≈ 13 500 €
+ petit modèle 5 fois moins cher, si l'eval le permet ≈ 2 700 €
```
Le choix du **modèle** pèse plus que tout le reste : on le valide sur un échantillon avant le lancement ([[146-choix-modeles|choix de modèle]]).

---

Calcul : combien de temps prend ce traitement avec une limite de 2 millions de tokens par minute ? <!--anki:694f677b2d714b26386d-->
?
```text
6,6 G tokens / 2 M tokens par minute = 3 300 minutes ≈ 55 heures
```
Les **quotas** (tokens et requêtes par minute) fixent la durée, pas la vitesse du modèle. Leviers : batch API aux quotas séparés, hausse de quota négociée, répartition sur plusieurs régions ou fournisseurs via une gateway ([[81-litellm-api-layer|LiteLLM]]), ou GPU auto-hébergés.

---

Comment rendre un pipeline batch reprenable ? <!--anki:6c4c614f3d3267766f48-->
?
- **Identifiant stable** par item, et écriture du résultat **idempotente** (réécrire le même item ne crée pas de doublon)
- **Statut persisté** par item, mis à jour après chaque réussite
- **Reprise** : relancer ne traite que les items non faits ou en erreur
- **Lots de taille moyenne**, pour qu'une panne ne coûte qu'un lot

Sur des GPU **préemptibles** (spot), c'est ce qui rend l'économie possible : une interruption ne perd presque rien.

---

Comment traiter les erreurs d'un pipeline batch ? <!--anki:75475e6c31627a623d5a-->
?
Les **classer**, car elles ne se traitent pas pareil :
- **Transitoires** (réseau, quota) : retry avec backoff
- **Sortie invalide** (JSON cassé, champ manquant) : nouvel essai, avec contrainte de schéma ou un modèle plus fort ([[63-guided-generation|guided generation]])
- **Contenu problématique** (document illisible, trop long, refus du modèle) : file de rejets pour traitement à part

Suivre le **taux d'erreur par catégorie** : un pic signale souvent un changement de format de la source.

---

Comment contrôler la qualité de millions de sorties ? <!--anki:50582f6b425974584d35-->
?
1. **Pilote** sur 1 % des items, évalué sur un jeu annoté, avant de tout lancer ([[94-evals-methodologie|evals]])
2. **Validation automatique** de chaque sortie : schéma, règles métier, valeurs plausibles
3. **Échantillonnage aléatoire** relu par un humain ou un juge calibré, **par lot**
4. **Surveillance des distributions** : proportion de chaque classe, champs vides. Une dérive brutale trahit un problème

Impossible de tout relire : on contrôle par **statistique**, pas par exhaustivité.

---

Pourquoi enregistrer les versions avec chaque résultat ? <!--anki:45596b32693846726f53-->
?
Chaque sortie doit porter le **modèle, la version du prompt et la date** qui l'ont produite. Sans cela, impossible de savoir quels items **retraiter** quand on corrige un prompt ou qu'un modèle est déprécié, ni d'expliquer un résultat six mois plus tard.

C'est le **lignage** des données générées, aussi utile en audit qu'en maintenance ([[153-data-flywheel-versioning|versioning]]).

---

Quand auto-héberger le traitement batch plutôt qu'utiliser une API ? <!--anki:69234355312640396e2f-->
?
- **Volume très élevé et récurrent** : des GPU occupés à 100 % pendant des jours amortissent vite leur coût
- **Données sensibles** qui ne doivent pas sortir ([[152-pii-confidentialite|confidentialité]])
- **Petit modèle suffisant**, ou modèle fine-tuné pour la tâche

Le mode **hors ligne** de vLLM (`LLM.generate` sur une grande liste de prompts) maximise le débit ; le **prefix caching** profite des instructions communes ([[66-prefix-caching-radix-attention|prefix caching]]).

---

Quand ne pas utiliser une batch API ? <!--anki:4b552b3350372d2f6a78-->
?
- **Résultats nécessaires en moins de quelques heures** : le délai est garanti sous 24 h, pas plus tôt
- **Étapes dépendantes** : un agent ou une chaîne où chaque appel dépend du précédent ne se soumet pas en un lot
- **Itérations rapides** sur le prompt : pendant la mise au point, l'appel en ligne sur un échantillon est plus pratique
- **Très petits volumes** : la gestion des lots coûte plus que l'économie

---

## Mises en situation

Mise en situation : on te demande d'extraire 15 champs de 3 millions de contrats scannés, pour une migration dans six semaines, avec un budget de 20 000 €. Comment organises-tu le projet ? <!--anki:6b69527d595330333274-->
?
1. **Pilote** : 2 000 contrats annotés, comparaison de trois modèles en qualité et en coût par contrat ([[162-document-parsing|parsing]])
2. **Chiffrer** : tokens par contrat, coût en batch API ou en auto-hébergé, durée selon les quotas
3. **Construire le pipeline reprenable** : identifiant par contrat, statut persisté, file de rejets, versions enregistrées
4. **Contrôler** : validation de schéma et règles métier, échantillon relu par lot, suivi des distributions
5. **Planifier une marge** pour retraiter les rejets et un éventuel second passage

**Piège** : lancer les 3 millions d'un coup sans pilote, et découvrir un défaut de prompt après avoir dépensé le budget.

---

Mise en situation : ton pipeline de classification tourne depuis trois jours. Tu découvres qu'une consigne ambiguë a mal classé une catégorie sur 30 % des items déjà traités. Que fais-tu ? <!--anki:466c77294a6c3f742445-->
?
1. **Arrêter** le traitement pour ne pas aggraver le problème
2. **Corriger le prompt** et le valider sur un échantillon annoté, en particulier sur la catégorie fautive
3. **Identifier les items à retraiter** grâce à la version du prompt enregistrée avec chaque résultat
4. **Retraiter seulement** les items concernés, pas tout le stock, si la correction ne touche qu'une catégorie
5. **Ajouter un contrôle** sur la distribution des classes, qui aurait détecté l'anomalie dès le premier lot

**Piège** : ne pas avoir enregistré la version du prompt, et devoir tout retraiter faute de savoir quoi.

---

## Sources

- [Anthropic — traitement par lots, résultats et expiration](https://platform.claude.com/docs/en/build-with-claude/batch-processing)

## Connexions
- [[145-cas-system-design|Cas de system design]] — l'extraction massive de documents
- [[121-couts-inference|Coûts d'inférence]] — batch API et unit economics
- [[62-optimisations-inference|Optimisations d'inférence]] — continuous batching et débit
- [[153-data-flywheel-versioning|Data flywheel & versioning]] — lignage des sorties
- [[94-evals-methodologie|Évaluation — méthodologie]] — pilote et échantillonnage
- [[63-guided-generation|Guided generation]] — sorties valides à grande échelle
- [[162-document-parsing|Parsing de documents]] — la première étape des pipelines documentaires
- [[11-serveurs-inference-llm|Serveurs d'inférence]] — vLLM, SGLang, TensorRT-LLM et leur réglage
- [[122-finops-llm|FinOps LLM]] — attribuer et piloter les dépenses IA
- [[141-system-design-llm|System design LLM]] — la méthode de conception
- [[00-moc-ai-engineering|MOC AI Engineering]]
