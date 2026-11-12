# AI Act (règlement européen sur l'IA) — Flashcards
Tags: #flashcards #ai-engineering #ai-act #conformite #reglementation
Vérifié le : 25 septembre 2026 — date globale conservée ; revue ciblée du 13 novembre 2026 détaillée dans les Sources.
<!-- summary: approche par les risques, pratiques interdites, haut risque et obligations, fournisseur ou déployeur, transparence, modèles à usage général, calendrier, sanctions, plan d'action, limites d'une validation humaine pour la qualification. -->


Qu'est-ce que l'AI Act ? <!--anki:4a5b34484f4550646148-->
?
Le **règlement (UE) 2024/1689**, entré en vigueur le **1er août 2024**, encadre l'IA avec une application progressive. Les obligations dépendent notamment de l'usage, du rôle de l'acteur et de la catégorie du système ou modèle.

Exemple : fournir un modèle généraliste et déployer un système de recrutement ne correspondent pas au même rôle ni aux mêmes obligations. Une entreprise hors UE peut être concernée lorsqu'elle fournit le marché européen ou que les sorties sont utilisées dans l'UE.

Vérifier **champ d'application, exclusions, qualification et calendrier** dans les textes à jour ; ni hébergement hors UE ni licence ouverte ne suffisent à conclure à une exemption.

---

Quels sont les niveaux de risque de l'AI Act ? <!--anki:722d2145524261493c49-->
?
1. **Inacceptable** : pratiques **interdites**.
2. **Haut risque** : obligations lourdes (gestion des risques, données, documentation, supervision humaine, conformité).
3. **Risque de transparence** : obligations d'**information** (chatbots, contenus générés, deepfakes).
4. **Risque minimal** : pas de régime haut risque ; vérifier les obligations transversales et les autres textes applicables.

S'y ajoute un régime propre aux **modèles d'IA à usage général** (GPAI).

---

Quelles pratiques d'IA l'AI Act interdit-il ? <!--anki:6e6f4a2c7d6c3c7c4856-->
?
Notamment : la **manipulation** subliminale ou l'exploitation des vulnérabilités causant un préjudice, la **notation sociale**, la **reconnaissance des émotions** au **travail** et à l'**école** (sauf raisons médicales ou de sécurité), le **moissonnage non ciblé** d'images faciales pour bâtir des bases de reconnaissance, la catégorisation biométrique sur des **caractéristiques sensibles**, et, sauf exceptions strictes, l'**identification biométrique à distance en temps réel** dans l'espace public par les forces de l'ordre. Interdictions applicables depuis le **2 février 2025**.

---

Qu'est-ce qu'un système à haut risque ? <!--anki:633821384664284a3071-->
?
Deux voies principales à l'article 6 :

- **Produits de l'annexe I** : l'IA est un produit ou composant de sécurité concerné et le produit doit subir une évaluation de conformité par un tiers.
- **Usages de l'annexe III** : notamment certaines applications d'emploi, éducation, biométrie, crédit, justice ou services publics.

La finalité et l'influence réelle sur la décision comptent ; l'article 6 prévoit des conditions et exceptions à examiner, avec un régime particulier pour le profilage. Un outil de classement de candidatures est un exemple caractéristique. La simple présence d'IA dans un secteur ne suffit pas à qualifier tous ses usages.

---

Quelles obligations pour un système à haut risque ? <!--anki:754c3a4e344f493f6f29-->
?
Système de **gestion des risques**, **gouvernance des données** (qualité, biais), **documentation technique**, **journalisation** automatique, **transparence** envers les déployeurs, **supervision humaine** effective, **exactitude, robustesse et cybersécurité**, système de gestion de la qualité, **évaluation de conformité** et marquage CE, enregistrement dans la base de l'UE, **surveillance après commercialisation**.

Répartir les obligations selon le rôle et la catégorie applicables. Exemple : une supervision de recrutement exige un humain compétent, informé et capable de contester le classement, pas seulement un bouton d'approbation. Relier chaque exigence à une preuve maintenue et vérifier le calendrier applicable.

---

À ne pas confondre : fournisseur et déployeur ? <!--anki:6a68263531675a333877-->
?
- **Fournisseur** : celui qui **développe** le système (ou le fait développer) et le met sur le marché sous son nom — porte l'essentiel des obligations.
- **Déployeur** : celui qui **utilise** le système dans son activité — obligations d'**usage conforme**, de **supervision humaine**, d'information des personnes, parfois d'**analyse d'impact sur les droits fondamentaux**.

Attention : **modifier substantiellement** un système ou l'utiliser pour une finalité à haut risque peut faire **devenir fournisseur**.

---

Quelles obligations de transparence pour les applications LLM courantes ? <!--anki:4a2a496d2b5769366f51-->
?
L'**article 50** distingue les rôles : information sur l'interaction avec une IA pour certains systèmes, marquage détectable par machine pour certains fournisseurs de génération synthétique, et divulgation de certains deepfakes ou textes d'information publique par les déployeurs.

Les exceptions dépendent de la disposition et de l'usage ; une relecture humaine n'exonère pas universellement tous les contenus. L'application générale débute au **2 août 2026**. L'article 111(4) accorde jusqu'au **2 décembre 2026** pour respecter le marquage de l'article 50(2) aux systèmes déjà mis sur le marché avant le 2 août 2026. Ce report ciblé ne suspend pas toutes les obligations de transparence ni celles du RGPD.

---

Quelles obligations pour les modèles d'IA à usage général (GPAI) ? <!--anki:465e51482b414f48404f-->
?
Les **fournisseurs GPAI** sont concernés par documentation technique, informations aux intégrateurs, politique de droit d'auteur et résumé public des données d'entraînement, selon les obligations et exceptions applicables.

L'application débute au **2 août 2025**, mais les modèles déjà mis sur le marché avant cette date disposent d'une transition jusqu'au **2 août 2027** selon l'article 111(3). Ne pas confondre date générale et échéance de chaque modèle.

Le **risque systémique**, notamment présumé au-delà de 10²⁵ FLOPs d'entraînement, ajoute évaluations, gestion des risques, signalement d'incidents graves et cybersécurité. Identifier rôle, date et catégorie ; le code de bonnes pratiques aide à démontrer la conformité sans remplacer le règlement.

---

Quel calendrier d'application de l'AI Act retenir au 6 octobre 2026 ? <!--anki:4c30777735412e43217c-->
?
Calendrier **recontrôlé le 13 novembre 2026**, règlement (UE) 2026/1744 inclus :
- **2 février 2025** : premières interdictions et maîtrise de l'IA.
- **2 août 2025** : gouvernance et obligations GPAI, selon transitions.
- **2 août 2026** : application générale, dont transparence, sous réserves.
- **2 décembre 2026** : nouvelles interdictions désignées à l'article 113(a), et fin de la transition de marquage de l'article 50(2) pour les systèmes antérieurs au 2 août 2026.
- **2 décembre 2027** : sections 1 à 3 du chapitre III pour l'annexe III ; **2 août 2028** pour l'annexe I, hors article 6(5).

Vérifier disposition, rôle et date de mise sur le marché.

---

Quelles sanctions prévoit l'AI Act ? <!--anki:714d7b7e6959667d2b6f-->
?
Les **articles 99 et 101** distinguent notamment :
- **Pratiques interdites** : 35 M€ ou 7 % du chiffre d'affaires mondial annuel.
- **Obligations visées à l'article 99(4)** : 15 M€ ou 3 %.
- **Informations incorrectes, incomplètes ou trompeuses** aux autorités nationales ou organismes notifiés : 7,5 M€ ou 1 %.
- **Fournisseurs GPAI**, sanctionnés par la Commission selon l'article 101 : 15 M€ ou 3 %.

Pour une entreprise, retenir normalement le plafond le plus élevé ; l'article 99 prévoit le plus bas pour les PME et certains manquements des SMC. Ce sont des plafonds, pas des amendes automatiques : circonstances et proportionnalité comptent.

---

Face à l'AI Act, par quoi commence un AI Engineer ? <!--anki:66347c2e784c3d563250-->
?
1. **Inventorier** les systèmes et cas d'usage IA.
2. **Classer** chacun (interdit, haut risque, transparence, minimal) et identifier son **rôle** : fournisseur ou déployeur.
3. Obtenir la **documentation** des fournisseurs de modèles GPAI.

Décrire la finalité réelle, les personnes concernées et l'effet de la sortie sur leurs droits. Une même technologie peut soutenir une simple rédaction ou une sélection de candidats, avec des obligations différentes. Documenter la qualification avec le juridique et identifier les preuves à produire ; le nom commercial du modèle ne détermine pas la catégorie.

---

Que met-on en place ensuite, selon la classification AI Act ? <!--anki:6538416e7056465a5358-->
?
1. Pour les cas simples : **transparence** (mention IA, marquage des contenus générés).
2. Pour le haut risque : gestion des risques, **journalisation**, **supervision humaine**, documentation et evals **dès la conception**.
3. Articuler avec le [[154-rgpd-llm|RGPD]] et les normes comme ISO 42001 ([[105-devsecops-ia-agentique|référentiels]]).

Pour un système à haut risque, les journaux doivent permettre de retracer le fonctionnement : version du modèle, entrée, résultat et intervention humaine. Revoir la classification à chaque changement d'usage : un assistant interne qui se met à évaluer les salariés relève de l'emploi, un domaine à haut risque, sans qu'une ligne de code ait changé.

---

Pourquoi ajouter une validation humaine ne suffit-il pas à soustraire un système de recrutement au régime de haut risque de l'AI Act ? <!--anki:6531323530623364343638393435333738346366373835306438383866336637-->
?
La **classification** dépend de la finalité et des conditions de l'article 6 et de l'annexe III, pas simplement de la présence d'un clic humain. Un classement de candidatures peut influencer fortement la décision même si un recruteur la confirme.

Décrire l'usage réel, les exceptions éventuelles et le rôle de chaque acteur avec le juridique. Concevoir une supervision effective et conserver les preuves de qualification. Le contrôle humain fait partie des mesures de maîtrise ; il ne constitue pas une exemption générale ni une garantie que la décision reste indépendante du score.

---

## Mises en situation

Mise en situation : ton entreprise déploie trois systèmes IA : un assistant de rédaction interne, un chatbot client et un outil de présélection de candidatures. Comment les classes-tu ? <!--anki:4943714a5b34316b7d70-->
?
1. **Assistant de rédaction interne** : généralement hors haut risque ; vérifier usage réel, maîtrise de l'IA et autres règles applicables
2. **Chatbot client** : obligation de **transparence**, informer qu'on parle à une IA
3. **Présélection de candidatures** : **haut risque** (emploi, annexe III), avec gestion des risques, journalisation, supervision humaine effective, documentation
4. **Déterminer le rôle** : déployeur d'un système acheté, ou fournisseur si vous le développez ou le modifiez substantiellement
5. **Vérifier le calendrier en vigueur**, qui a été amendé depuis le texte initial

**Piège** : classer par technologie plutôt que par **usage** : c'est le contexte d'emploi qui rend un système à haut risque.

---

Mise en situation : une équipe veut utiliser la détection d'émotions sur les appels d'un centre de contact, pour évaluer les conseillers. Que réponds-tu ? <!--anki:66633f6f37312a535b6a-->
?
1. **Qualifier la fonction réelle** : inférer les émotions de salariés à partir de signaux biométriques, dont la voix, relève de l'interdiction au travail, sauf exception médicale ou de sécurité applicable.
2. **Suspendre ce dispositif** et faire confirmer la qualification par le juridique ; une agrégation finale n'efface pas une inférence interdite en amont.
3. **Étudier une autre collecte**, par exemple un questionnaire de satisfaction, sans réintroduire cette inférence ni une surveillance disproportionnée.
4. **Vérifier les obligations restantes** : finalité, base légale, information, minimisation et consultation des instances compétentes.
5. **Documenter la décision** et tester que le produit ne conserve pas une fonction équivalente sous un autre nom.

**Piège** : présenter anonymisation ou consentement comme une exemption automatique à une interdiction.

---

## Sources

- [Commission européenne — article 99, sanctions](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-99) et [article 101, fournisseurs GPAI](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-101) — dispositions de sanction consultées le 5 novembre 2026 ; pas de revérification intégrale de la fiche.

Revue ciblée du 6 octobre 2026 : calendrier, qualification du haut risque et obligations de transparence confrontés aux sources institutionnelles ci-dessous.

- [Commission européenne — obligations de transparence, article 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50)
- [Commission européenne — champ d'application, article 2](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-2) — consultation ciblée du 6 novembre 2026.

- [Commission européenne — classification haut risque, article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6)

- [Conseil de l’Union européenne — calendrier et évolution de l’AI Act](https://www.consilium.europa.eu/en/policies/artificial-intelligence-act/timeline-artificial-intelligence/)

- [Union européenne — règlement (UE) 2024/1689, AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/fra)
- [Commission européenne — cadre réglementaire et calendrier AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

- [Commission européenne — qualification du haut risque, article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6) — approfondissement ciblé du 12 novembre 2026 ; les exemples pédagogiques sont construits pour cette revue.

- [Commission européenne — pratiques interdites, article 5](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-5) — vérification ciblée du 12 novembre 2026, sans renouvellement de la date globale de la fiche.

Revue ciblée du 13 novembre 2026 : affirmations précisées dans cette passe ; les autres contenus ne sont pas intégralement revérifiés.

- [EUR-Lex — règlement modificatif (UE) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng) — texte normatif des amendements et calendrier.
- [Commission européenne — article 111 amendé](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-111) — transitions GPAI et marquage des systèmes existants.
- [Commission européenne — article 113 amendé](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-113) — dates d’application par dispositions.

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
