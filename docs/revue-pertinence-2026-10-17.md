# Revue de pertinence des cartes — 17 octobre 2026

Le vault reste pertinent pour un AI Engineer : les fiches sont exactes dans leur grande majorité, à jour sur la stack agentique et riches en cas d'application. Le défaut principal n'était pas l'erreur mais la **redondance** : une même notion était définie dans deux, trois ou quatre fiches, ce qui fait réviser plusieurs fois la même réponse. Viennent ensuite quelques faits datés, des incohérences entre cartes voisines et des questions qui font réciter des catalogues.

## Périmètre

- **Lecture complète** des 144 fiches de la copie locale au 17 octobre, y compris une passe d'enrichissement alors non commitée qui ajoute environ 175 paragraphes à 46 fiches des sections 10 à 54.
- **Analyses automatiques** : similarité TF-IDF entre cartes, questions de type catalogue, questions courtes qui ne nomment pas leur sujet, formulations proscrites par le README.
- **Vérification en ligne** de quatre faits datés : hooks de Claude Code, retrait d'ingress-nginx, mémoire du GPU B300, prompt caching d'Anthropic.
- **Intégration** : le dépôt distant contenait sept commits du 11 au 13 octobre, absents de la copie relue. Ils apportent la [revue de pertinence du 11 octobre](revue-pertinence-2026-10-11.md), deux fiches nouvelles et des modifications dans 25 fiches. Les modifications de cette revue ont été rejouées sur cet état, carte par carte.

Cette revue ne revérifie pas chaque produit, version ou texte réglementaire. Les faits postérieurs à juin 2026 cités par les fiches, comme la spécification MCP 2026-07-28, A2A 1.0 ou l'AI Omnibus, n'ont pas été recontrôlés. Seules trois dates `Vérifié le` changent, sur les fiches dont les affirmations ont effectivement été confrontées aux sources : 34, 83 et 123. Les deux fiches arrivées avec le dépôt distant, sur les droits et versions en RAG et sur l'évaluation des réponses, n'ont pas été relues ; seul le lint les couvre.

## Constats

### Redondance entre fiches

La similarité lexicale ne repère qu'une dizaine de doublons, car les cartes répétées sont reformulées. La lecture en a trouvé une quarantaine. Exemples :

| Notion | Où elle était définie |
| --- | --- |
| Option `--nv` d'Apptainer | 06, 09 et 13 |
| KV cache | deux cartes quasi identiques dans 61 |
| Prefix caching | 61 et 66 |
| Ollama ou vLLM | 11 et trois cartes de 164 |
| Utilisation GPU trompeuse | 64, 69 et 93 |
| pass@k et pass^k | 96 et 114 |
| RLHF et DPO | 51 et 52 |
| Shadow deployment | 97 et 112 |
| Calendrier de l'AI Act | 115 et 155 |

Une carte en double coûte du temps de révision sans renforcer la compréhension. Elle peut aussi diverger : le calendrier de l'AI Act parlait de « Digital Omnibus » dans une fiche et d'« AI Omnibus » dans l'autre.

### Faits datés ou inexacts

- **Hooks de Claude Code** : la carte affirmait qu'un code de sortie non nul bloque l'action. Seul le code 2 bloque ; un code 1 laisse l'appel se faire.
- **ingress-nginx** : la fiche Ingress le présentait comme contrôleur de référence et utilisait ses annotations, alors que sa maintenance devait s'arrêter en mars 2026.
- **Prompt caching** : la lecture du cache est moins chère que 0,1× sur certains modèles récents.
- **Repères de VRAM** : le B300, environ 288 Go, manquait.

### Incohérences entre cartes

- **Taille des chunks** : 512 à 1 024 tokens dans la fiche 21, 300 à 800 dans la fiche 25, qui juge « trop grand » au-delà de 1 000.
- **Lost in the middle** : une mise en situation imposait les meilleurs passages en début et en fin, la carte voisine refuse d'en faire une règle universelle.
- **Rate limits** : une mise en situation conseillait de multiplier les clés, la carte de la même fiche met en garde contre ce contournement.
- **Artefact déployé** : trois versions à tracer dans la fiche 112, quatre dans la fiche 111, qui ajoute l'index RAG.
- **Exemples qui donnent la réponse** : les cartes « accumulation de gradients » et « loi 6ND » citaient exactement les données et le résultat d'une carte de calcul voisine.

### Questions difficiles à noter

- **Catalogues** : « Quels benchmarks de text-to-SQL connaître ? », « Quels services de sandbox pour agents connaître ? » ou des listes de composants cloud se notent mal et vieillissent vite.
- **Sujet absent** : « De quoi dépend le gain de vitesse ? » ou « Quand ne pas accuser le modèle ? » ne se comprennent pas une fois les cartes mélangées.
- **Formulation proscrite** : trois cartes utilisaient « X ou Y : quelle différence ? », que le lint ne détectait pas.

### Passe d'enrichissement

Les paragraphes ajoutés sont justes et apportent souvent une nuance utile : idempotence après reprise, permissions vérifiées à l'exécution, mesure avant décision. Ils suivent toutefois un même gabarit de mise en garde.

| Indicateur | Avant la passe | Après la passe et la revue |
| --- | ---: | ---: |
| Mots moyens par réponse | 71,9 | 75,9 |
| Réponses contenant un impératif « Vérifier, Mesurer, Tester, Comparer… » | 18 % | 21 % |

Quatre additions posaient un problème concret : deux révélaient la réponse d'une carte de calcul, deux répétaient la carte voisine. Elles ont été allégées. Deux autres reprenaient une nuance que le dépôt distant avait publiée entre-temps, sur le cache des schémas d'outils et le serving multi-LoRA. Elles ont été retirées à l'intégration. Pour poursuivre cette passe sur les sections 55 à 170, ajouter un paragraphe seulement s'il apporte un mécanisme, un contre-exemple ou un critère de décision absent de la carte et de ses voisines.

## Modifications

| Type | Volume | Exemples |
| --- | ---: | --- |
| Cartes retirées | 41 | doublons ci-dessus, deux catalogues sans critère de réponse |
| Questions reformulées | 29 | benchmarks posés comme un choix, sujet nommé, « À ne pas confondre » |
| Cartes ajoutées | 2 | migration hors d'ingress-nginx, cas d'un assistant d'analyse de données |
| Autres remplacements dans les fiches | 49 | faits datés, incohérences, coquilles, additions allégées, résumés et sources |

Les identifiants des cartes reformulées sont conservés : leur historique de révision suit. Chaque carte retirée figure dans `scripts/retired_cards.json` avec sa raison, et l'export la republie suspendue avec le tag `retired`. Dans AnkiDroid, chercher `tag:retired`, tout sélectionner puis supprimer. La carte conservée garde son propre historique.

Deux retraits sont remplacés pour conserver la couverture : la mise en situation « réponses coupées à 60 secondes » de la fiche 83, doublon de la fiche 84, devient une migration hors d'ingress-nginx, et le « Cas 4 » de la fiche 145, doublon de sa propre mise en situation, devient un assistant d'analyse de données en langage naturel.

Cinq remplacements prévus étaient déjà faits par la revue du 11 octobre ou n'avaient plus d'objet. La carte de la fiche 32 ne prétend plus que MCP exige le tool calling. La mise en situation de la fiche 63 n'impute plus d'emblée la régression à l'ordre des champs. Le résumé de la fiche 161 ne cite plus les autres modalités.

## Outillage et conventions

- **Lint** : il signale désormais « X ou Y : quelle différence ? » et les questions de catalogue en « Quels benchmarks… », « Quels services… », « Quelles offres… » ou « … connaître ? ». Un test couvre ces deux règles.
- **README** : deux conventions ajoutées. Une notion se définit dans sa fiche dédiée et se mobilise ailleurs par un lien ou une carte d'application. Une carte voisine ne doit pas donner en exemple le résultat d'une carte de calcul.

## Vérifications

- Lint sur tout le vault : aucune erreur, aucun avertissement, y compris avec les règles étendues.
- 52 tests du dépôt réussis sous Python 3.10, dépendances épinglées, y compris ceux de l'atelier RAG ; export Anki généré avec 2 163 cartes actives et 71 cartes retirées suspendues.
- Catalogues du README et du MOC synchronisés ; ligne « État au » mise à jour.
- Sources consultées : [documentation des hooks de Claude Code](https://code.claude.com/docs/en/hooks), [annonce du retrait d'Ingress NGINX](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/), [prompt caching d'Anthropic](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [GB300 NVL72 de NVIDIA](https://www.nvidia.com/en-us/data-center/gb300-nvl72/).

Ces contrôles portent sur la cohérence et le bon fonctionnement du vault. Ils ne mesurent pas un gain d'apprentissage chez les utilisateurs.

## Suite proposée

- **Fiches arrivées avec le dépôt distant** : relire 20-010 et 90-010 avec les mêmes critères de redondance et de formulation.
- **Fiches à revérifier en priorité** : 38 et 115, qui citent beaucoup d'offres cloud et de dates d'annonce ; 33, 36 et 85 pour MCP et A2A.
- **Section conteneurs** : la fiche 05 consacre trois cartes à l'histoire de dockershim, retiré en 2022. Elles pourraient se réduire à la carte « à ne pas confondre ».
- **Fiches récentes très abstraites** : plusieurs cartes de 60-010 à 60-012 répondent par une liste de vérifications. Les compléter par un exemple chiffré faciliterait la notation en révision.
