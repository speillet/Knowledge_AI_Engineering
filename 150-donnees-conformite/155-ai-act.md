# AI Act (règlement européen sur l'IA) — Flashcards
Tags: #flashcards #ai-engineering #ai-act #conformite #reglementation
Vérifié le : 25 septembre 2026 — cette fiche cite des produits, versions ou textes réglementaires qui évoluent vite.
<!-- summary: approche par les risques, pratiques interdites, haut risque et obligations, fournisseur ou déployeur, transparence, modèles à usage général, calendrier, sanctions, plan d'action. -->

Qu'est-ce que l'AI Act ?
?
<!--anki:4a5b34484f4550646148-->
Le **règlement (UE) 2024/1689**, premier cadre juridique complet sur l'IA, entré en vigueur le **1er août 2024** avec une application **progressive**. Il suit une **approche par les risques** : plus un système peut nuire aux personnes, plus les obligations sont lourdes. Il s'applique à quiconque met un système d'IA **sur le marché ou en service dans l'UE**, même depuis l'étranger.

---

Quels sont les niveaux de risque de l'AI Act ?
?
<!--anki:722d2145524261493c49-->
1. **Inacceptable** : pratiques **interdites**.
2. **Haut risque** : obligations lourdes (gestion des risques, données, documentation, supervision humaine, conformité).
3. **Risque de transparence** : obligations d'**information** (chatbots, contenus générés, deepfakes).
4. **Risque minimal** : pas d'obligation spécifique (codes de conduite volontaires).

S'y ajoute un régime propre aux **modèles d'IA à usage général** (GPAI).

---

Quelles pratiques d'IA l'AI Act interdit-il ?
?
<!--anki:6e6f4a2c7d6c3c7c4856-->
Notamment : la **manipulation** subliminale ou l'exploitation des vulnérabilités causant un préjudice, la **notation sociale**, la **reconnaissance des émotions** au **travail** et à l'**école** (sauf raisons médicales ou de sécurité), le **moissonnage non ciblé** d'images faciales pour bâtir des bases de reconnaissance, la catégorisation biométrique sur des **caractéristiques sensibles**, et, sauf exceptions strictes, l'**identification biométrique à distance en temps réel** dans l'espace public par les forces de l'ordre. Interdictions applicables depuis le **2 février 2025**.

---

Qu'est-ce qu'un système à haut risque ?
?
<!--anki:633821384664284a3071-->
- Un système qui est un **composant de sécurité** d'un produit déjà réglementé (dispositifs médicaux, machines, jouets…).
- Un système utilisé dans les **domaines de l'annexe III** : biométrie, infrastructures critiques, **éducation** (admission, notation), **emploi** (tri de CV, évaluation de salariés), accès aux **services essentiels** (crédit, assurance, prestations sociales), forces de l'ordre, migrations, justice et processus démocratiques.

Un chatbot RH qui **classe des candidats** est haut risque ; un assistant de rédaction interne ne l'est pas.

---

Quelles obligations pour un système à haut risque ?
?
<!--anki:754c3a4e344f493f6f29-->
Système de **gestion des risques**, **gouvernance des données** (qualité, biais), **documentation technique**, **journalisation** automatique, **transparence** envers les déployeurs, **supervision humaine** effective, **exactitude, robustesse et cybersécurité**, système de gestion de la qualité, **évaluation de conformité** et marquage CE, enregistrement dans la base de l'UE, **surveillance après commercialisation**.

---

À ne pas confondre : fournisseur et déployeur ?
?
<!--anki:6a68263531675a333877-->
- **Fournisseur** : celui qui **développe** le système (ou le fait développer) et le met sur le marché sous son nom — porte l'essentiel des obligations.
- **Déployeur** : celui qui **utilise** le système dans son activité — obligations d'**usage conforme**, de **supervision humaine**, d'information des personnes, parfois d'**analyse d'impact sur les droits fondamentaux**.

Attention : **modifier substantiellement** un système ou l'utiliser pour une finalité à haut risque peut faire **devenir fournisseur**.

---

Quelles obligations de transparence pour les applications LLM courantes ?
?
<!--anki:4a2a496d2b5769366f51-->
- Informer les personnes qu'elles **interagissent avec une IA** (chatbot), sauf si c'est évident.
- **Marquer** les contenus synthétiques (texte, image, audio, vidéo) de façon **lisible par machine**.
- Signaler les **deepfakes** et les textes générés publiés pour **informer le public** sur des sujets d'intérêt public.

Ces obligations s'appliquent à partir d'**août 2026** ([[144-ux-ia-human-in-the-loop|UX]]).

---

Quelles obligations pour les modèles d'IA à usage général (GPAI) ?
?
<!--anki:465e51482b414f48404f-->
Applicables depuis le **2 août 2025** aux **fournisseurs de modèles** : **documentation technique**, informations pour les intégrateurs en aval, **politique de respect du droit d'auteur** (dont les opt-out de fouille de textes), **résumé public** des données d'entraînement. Les modèles à **risque systémique** (présumé au-delà de **10²⁵ FLOPs** d'entraînement) doivent en plus : **évaluations** et tests adversariaux, gestion des risques, **signalement des incidents graves**, cybersécurité. Un **code de bonnes pratiques** sert de référence pour démontrer la conformité.

---

Quel est le calendrier d'application à connaître ?
?
<!--anki:4c30777735412e43217c-->
- **Août 2024** : entrée en vigueur.
- **Février 2025** : pratiques interdites + obligation de **maîtrise de l'IA** (AI literacy) des personnels.
- **Août 2025** : obligations GPAI, gouvernance, sanctions.
- **Août 2026** : la plupart des autres obligations (dont transparence et haut risque de l'annexe III, dans le calendrier initial).
- **Août 2027** : haut risque lié aux produits réglementés.

La Commission a proposé fin 2025 (« Digital Omnibus ») de **reporter** une partie des obligations haut risque : **vérifier le calendrier en vigueur**.

---

Quelles sanctions prévoit l'AI Act ?
?
<!--anki:714d7b7e6959667d2b6f-->
Jusqu'à **35 M€ ou 7 %** du chiffre d'affaires mondial pour les pratiques **interdites** ; jusqu'à **15 M€ ou 3 %** pour les autres manquements (dont les obligations GPAI) ; jusqu'à **7,5 M€ ou 1 %** pour des informations inexactes fournies aux autorités. Montants plafonnés plus bas pour les PME.

---

Face à l'AI Act, par quoi commence un AI Engineer ?
?
<!--anki:66347c2e784c3d563250-->
1. **Inventorier** les systèmes et cas d'usage IA.
2. **Classer** chacun (interdit, haut risque, transparence, minimal) et identifier son **rôle** : fournisseur ou déployeur.
3. Obtenir la **documentation** des fournisseurs de modèles GPAI.

---

Que met-on en place ensuite, selon la classification AI Act ?
?
<!--anki:6538416e7056465a5358-->
1. Pour les cas simples : **transparence** (mention IA, marquage des contenus générés).
2. Pour le haut risque : gestion des risques, **journalisation**, **supervision humaine**, documentation et evals **dès la conception**.
3. Articuler avec le [[154-rgpd-llm|RGPD]] et les normes comme ISO 42001 ([[105-devsecops-ia-agentique|référentiels]]).

---

## Mises en situation

Mise en situation : ton entreprise déploie trois systèmes IA : un assistant de rédaction interne, un chatbot client et un outil de présélection de candidatures. Comment les classes-tu ?
?
<!--anki:4943714a5b34316b7d70-->
1. **Assistant de rédaction interne** : risque minimal, pas d'obligation spécifique
2. **Chatbot client** : obligation de **transparence**, informer qu'on parle à une IA
3. **Présélection de candidatures** : **haut risque** (emploi, annexe III), avec gestion des risques, journalisation, supervision humaine effective, documentation
4. **Déterminer le rôle** : déployeur d'un système acheté, ou fournisseur si vous le développez ou le modifiez substantiellement
5. **Vérifier le calendrier en vigueur**, qui a été amendé depuis le texte initial

**Piège** : classer par technologie plutôt que par **usage** : c'est le contexte d'emploi qui rend un système à haut risque.

---

Mise en situation : une équipe veut utiliser la détection d'émotions sur les appels d'un centre de contact, pour évaluer les conseillers. Que réponds-tu ?
?
<!--anki:66633f6f37312a535b6a-->
1. **Signal d'alerte immédiat** : la reconnaissance des émotions **sur le lieu de travail** fait partie des pratiques **interdites**, sauf raisons médicales ou de sécurité
2. **Interdiction applicable** depuis février 2025, avec les sanctions les plus élevées du règlement
3. **Proposer une alternative** : analyse **agrégée et anonyme** de la satisfaction client, sans évaluation individuelle des salariés
4. **Impliquer** juridique et représentants du personnel avant toute décision
5. **Vérifier aussi le RGPD** : base légale, information, décisions automatisées ([[154-rgpd-llm|RGPD]])

**Piège** : traiter l'interdiction comme un risque de conformité à arbitrer, alors que c'est une interdiction pure et simple.

---

## Sources

- [Union européenne — règlement (UE) 2024/1689, AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/fra)
- [Commission européenne — cadre réglementaire et calendrier AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

## Connexions
- [[154-rgpd-llm|RGPD appliqué aux LLM]] — le cadre de protection des données
- [[156-ia-responsable|IA responsable]] — biais, transparence, documentation
- [[115-plateformes-agents-gouvernance|Plateformes d'agents — Gouvernance]] — AI Act et agents
- [[105-devsecops-ia-agentique|DevSecOps IA]] — NIST, ISO 42001
- [[144-ux-ia-human-in-the-loop|UX de l'IA]] — informer l'utilisateur
- [[147-leadership-technique-ia|Leadership technique]] — cadrage réglementaire des projets
- [[146-choix-modeles|Choix de modèles]] — critères, benchmarks et migration
- [[103-defenses-agents|Défenses des agents]] — isolation, politiques et moindre privilège
- [[00-moc-ai-engineering|MOC AI Engineering]]
