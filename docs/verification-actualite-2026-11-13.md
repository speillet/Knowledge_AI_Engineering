# Vérification d'actualité — 13 novembre 2026

La documentation nécessitait des précisions. Les APIs MLflow récemment ajoutées sont cohérentes avec la documentation actuelle ; des formulations anciennes sur MCP, l'hébergement des agents et OWASP devaient être corrigées. Cette revue distingue les confirmations, les corrections et les limites du contrôle.

## Périmètre et méthode

Point de départ : `main` au commit `4d80c12`, après la PR 15. Le dossier de travail initial est sur un ancien commit avec des modifications non committées ; cette revue utilise un worktree séparé, sans les écraser.

L'inventaire porte sur les **150 fiches / 2 440 cartes**. **85 fiches** possèdent une date générale de vérification. Une date récente n'est pas une preuve que toutes les informations sont actuelles ; l'absence de date ne signifie pas non plus qu'un principe stable est faux.

Les sources ont été consultées les 12 et 13 novembre 2026. La vérification factuelle cible les références susceptibles d'évoluer des **neuf fiches MLOps**, puis leurs dépendances sur les plateformes d'agents, la sécurité et l'AI Act. Les affirmations sont confrontées aux pages primaires, spécifications versionnées, notes de version et textes normatifs. Context7 complète la consultation pour MLflow, MCP et Claude Managed Agents. Les snippets restent documentaires : aucun service MLflow, cloud ou fournisseur n'a été déployé pour cet audit.

**14 réponses sont corrigées ou précisées dans six fiches** : 38, 101, 105, 115, 117 et 155. Aucune carte n'est ajoutée ou retirée. Les questions et identifiants existants sont conservés. Les dates générales ne sont pas renouvelées artificiellement : les passages contrôlés et la date de cette revue figurent dans les Sources.

## Confirmations et corrections

| Sujet | Résultat au 13 novembre 2026 | Conséquence dans le vault |
| --- | --- | --- |
| MLflow 3 | `name=` et URI retournée par la journalisation restent la voie documentée ; les alias sont mutables. | Les exemples 111/117/118 sont conservés. Déplacer un alias ne recharge pas les modèles déjà chargés. [Migration](https://mlflow.org/docs/latest/ml/mlflow-3/), [registre](https://mlflow.org/docs/latest/ml/model-registry/workflow/). |
| Kubeflow Pipelines | Cache configurable par tâche et à d'autres niveaux ; un réglage de soumission peut écraser celui de la tâche. | La fiche 117 précise les overrides et la vérification du run effectif. [Documentation du cache](https://www.kubeflow.org/docs/components/pipelines/user-guides/core-functions/caching/). |
| Features et TTL | La fenêtre historique ne constitue pas, seule, une garantie de fraîcheur métier ou de disponibilité passée. | Les distinctions de la fiche 119 restent pertinentes. [Jointures historiques Feast](https://docs.feast.dev/getting-started/concepts/point-in-time-joins). |
| MCP 2026-07-28 | Suppression des sessions protocolaires et du handshake ; les capacités accompagnent les requêtes. | Le socle de la fiche 33 est confirmé, sans prétendre que l'état métier disparaît. [Changelog versionné](https://modelcontextprotocol.io/specification/2026-07-28/changelog). |
| Enregistrement OAuth MCP | Client ID Metadata Documents privilégiés ; pré-enregistrement et DCR demeurent documentés. DCR est déprécié, pas supprimé. | Correction de la fiche 115. [Enregistrement des clients](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration). |
| Autorisation d'entreprise MCP | Extension explicite avec support nécessaire des participants et politiques IdP. | La fiche 115 ne présente plus ce mécanisme comme une propriété automatique de toute connexion MCP. [Extension officielle](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization). |
| Identité AIMS/WIMSE | `draft-ietf-wimse-aims-01`, publié le 2 novembre, reste un Internet-Draft. | La fiche 115 distingue travail de standardisation, standard et produit. [Datatracker IETF](https://datatracker.ietf.org/doc/html/draft-ietf-wimse-aims-01). |
| Agent 365 | Disponibilité commerciale depuis le 1er mai 2026, avec prérequis et intégrations. | La fiche 115 borne la couverture annoncée aux agents effectivement intégrés ou découverts. [Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-agent-365/overview). |
| Registre AWS | La documentation actuelle emploie **AWS Agent Registry**. | Nom et différences de périmètre précisés dans la fiche 38. [Notes de version AWS](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.html). |
| Optimisation d'agents | Les recommandations ne prouvent pas un gain et n'autorisent pas une promotion. | La fiche 115 conserve validation indépendante et vérification du statut de chaque fonction. [AWS](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html), [Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform/). |
| Managed Agents hébergé | Statut bêta ; stockage de sessions côté service et non-éligibilité ZDR documentés. | Les fiches 38/115 séparent service hébergé et seules sandboxes auto-hébergées. [Vue d'ensemble Claude](https://platform.claude.com/docs/en/managed-agents/overview). |
| Managed Agents entièrement auto-hébergé | Mode accessible sur demande ; l'organisation conserve les sessions et les appels de modèles suivent le contrat du fournisseur. | Suppression d'une généralisation du non-ZDR à tous les modes. [Données et accès](https://platform.claude.com/docs/en/managed-agents/self-hosted-data-and-access). |
| Plan de contrôle OpenAI | **OpenClaw Enterprise** est présenté comme open source et encore en phase pilote ; l’objectif 1.0 ne constitue pas une disponibilité générale acquise. | Fiche 38 précisée. [Billet officiel OpenAI](https://developers.openai.com/blog/securing-persistent-agents-like-openclaw-at-openai). |
| Agent Builder | Dépréciation annoncée le 3 juin ; fermeture prévue le **30 novembre 2026**, encore future au jour de cette revue. | La fiche 38 donne l'échéance et rappelle que l'export demande reconfiguration et validation. [Documentation officielle OpenAI](https://developers.openai.com/api/docs/guides/agent-builder), [migration](https://developers.openai.com/api/docs/guides/agent-builder/migrate-from-agent-builder). |
| OWASP LLM | L'édition **2026** réordonne des identifiants et élargit l'exposition du contexte caché. | Fiches 101/105 actualisées ; la fiche 115 distingue les listes LLM et agentique ASI. [Ressource 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/), [PDF officiel](https://genai.owasp.org/download/56857/). |
| AI Act | Le calendrier amendé reste pertinent, avec des transitions distinctes par disposition et rôle. | Fiche 155 précisée pour les GPAI antérieurs au 2 août 2025 et le marquage de certains systèmes existants au 2 décembre 2026. [Article 111 amendé](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-111), [règlement modificatif](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng). |

## Points qui demandaient une lecture attentive des sources

**OWASP : une URL officielle peut exposer une ancienne édition.** L'[index historique](https://genai.owasp.org/llm-top-10/) affiche encore 2025, tandis que la ressource 2026 et son PDF sont publiés séparément. Le PDF contient aussi des champs de date encore à compléter : on s'appuie sur l'édition et le contenu servis, sans inventer une date de publication précise à partir de ces placeholders. Par exemple, Excessive Agency passe de **LLM06:2025 à LLM03:2026**, et System Prompt Leakage est élargi à **Hidden Context Exposure, LLM08:2026**. Conserver une ancienne analyse exige d'en préserver l'édition et de vérifier ses correspondances.

**Hébergement : localiser les sandboxes ne localise pas nécessairement les sessions.** Dans la configuration avec seules sandboxes auto-hébergées, l'orchestration reste chez Anthropic. Dans le service entièrement auto-hébergé, le stockage et l'exploitation changent de périmètre ; les appels de modèles restent soumis à leurs propres conditions. Un contrat ZDR pour ces appels n'efface pas les sessions, journaux et sauvegardes conservés par l'organisation. La page officielle détaillée a été récupérée directement en HTTP après échec de l'outil d'ouverture.

**AI Act : lire la disposition amendée plutôt que généraliser une date.** Le règlement (UE) 2026/1744 est un texte adopté, pas seulement une proposition. Il maintient des dates distinctes pour les catégories de haut risque et ajoute des dispositions transitoires ciblées. Le report de marquage de l'article 50(2) ne reporte pas toutes les obligations de transparence. Le calendrier cite aussi les nouvelles interdictions désignées à l'article 113(a) applicables au 2 décembre 2026 ; la qualification précise reste à vérifier dans le texte pour chaque usage.

## Ce que ce contrôle ne permet pas d'affirmer

Cette passe **ne certifie pas chaque affirmation des 150 fiches**. Elle ne revérifie pas intégralement tous les prix, limites de contexte, benchmarks, CVE, SDK et offres cités ailleurs. Les autres dates générales restent donc en place. Les versions `latest` des sites documentaires peuvent évoluer après cette consultation ; utiliser une version précise lors d'une implémentation.

Le seuil automatique de six mois est une alerte de maintenance. Un service peut changer avant ce délai. Avant un nouveau déploiement, vérifier changelog, dépréciations, conditions d'accès, régions et contrat de données des dépendances retenues. Un test de lint confirme structure et liens internes ; il ne prouve ni exactitude des sources externes ni conformité réglementaire.

## Validation de la livraison

Le contrôle comparatif retrouve les **2 440 questions et identifiants**, sans ajout ni retrait, et exactement les **14 réponses** décrites ci-dessus. `make check` réussit : **54 tests**, ruff, mypy, catalogues et deux ateliers. Le lint ne signale ni erreur ni avertissement.

L'export Anki est généré puis inspecté : **2 440 cartes actives** avec les identifiants attendus et **71 anciennes cartes retirées toujours suspendues**. Les dernières corrections figurent dans le paquet. La CI doit également réussir avant fusion ; ses résultats et la publication sont consignés dans la PR.
