---
description: Génère une ou plusieurs leçons pédagogiques à partir d'un plan (ex. next-plan.md, redis-plan.md). Orchestre writer + auditor individuel + coherence-auditor global, et consolide lessons/index.yaml.
argument-hint: [--plan=<chemin> --lessons=<id1,id2> --skip-audit]
allowed-tools: Read, Write, Edit, WebSearch, WebFetch
---

# Create Lesson - Orchestrateur de création de leçons

Ta mission est de générer une ou plusieurs leçons pédagogiques à partir d'un plan passé en input, en orchestrant les sub-agents `lesson/writer` + `lesson/auditor` en parallèle (rédaction et audit individuel), puis `lesson/coherence-auditor` pour l'audit global inter-leçons, et en consolidant `lessons/index.yaml` de manière centralisée.

## Prerequis

- Un fichier plan existant dans `plans/` (ex : `plans/redis-plan.md`) au format de `plans/template-create-plan.md` (sections `### N. <id>` avec concepts + points clés, "Matrice concept → leçon canonique", "Dépréciations et breaking changes critiques", "Versions cibles")

## Input

- `--plan=<chemin>` : Chemin du plan pédagogique (OBLIGATOIRE)
- `--lessons=<ids>` : CSV d'ids à traiter (optionnel, défaut : toutes les leçons du plan non encore présentes dans l'index)
- `--skip-audit` : Désactive les deux audits (Phase 2 audit individuel ET Phase 3 audit cohérence inter-leçons). Optionnel, défaut : les deux audits sont activés

## Workflow

### Phase 0 : Préparation

0.0. **Lire `.claude/skills/lesson-doc/SKILL.md`** : source des règles citées plus bas (index, nommage, versions)

0.1. **Parser `$ARGUMENTS`**
   - Extraire `--plan`, `--lessons`, `--skip-audit`
   - SI `--plan` absent → erreur et arrêter

0.2. **Lire le plan** avec `Read`
   - Extraire depuis "Versions cibles" chaque techno du plan avec sa section d'index (racine ou imbriquée sous une techno parente), son dossier et sa `last_version`. Un plan peut porter plusieurs technos (ex : React + Next.js)
   - Rattacher chaque leçon à sa techno via le titre `## Leçons {Techno} (techno=<slug>, ...)` qui la précède, puis calculer son `lesson_file` = `<dossier>/<id>.md`
   - SI "Versions cibles" est absente ou sans colonnes Section index / Dossier → demander au user la section d'index et le dossier de chaque techno
   - Extraire l'ordre d'exécution depuis "Ordre d'exécution recommandé"
   - Parser les sections `### N. <id>` pour lister toutes les leçons du plan
   - Noter les sections absentes du plan (ex : matrice) pour les signaler en 0.5

0.3. **Lire `lessons/index.yaml`** avec `Read`
   - Identifier les leçons déjà écrites dans chaque section d'index cible

0.4. **Construire la liste `lessons_to_process`**
   - SI `--lessons` présent :
     - Valider que chaque id existe dans le plan (section `### N. <id>` présente)
     - SI un id est inconnu → erreur claire listant les ids invalides et arrêter
     - SINON → utiliser exactement ces ids (même si déjà dans l'index, l'utilisateur force)
   - SINON → toutes les leçons du plan non présentes dans leur section d'index
   - SI la liste est vide (aucune leçon à traiter) → afficher "Toutes les leçons du plan sont déjà dans l'index" et arrêter proprement

0.5. **Présenter la liste au user** et attendre validation AVANT de lancer les agents
   - Afficher : par techno, section d'index et dossier, nombre de leçons à traiter, ids dans l'ordre du plan
   - Afficher : mode audit (activé/désactivé)
   - Afficher en warning les sections absentes du plan (les agents dégradent les contrôles correspondants)

### Phase 1 : Rédaction parallèle

1.1. **Lancer les sub-agents `lesson/writer`** EN PARALLELE (1 par leçon)
   - Pour chaque `lesson_id` dans `lessons_to_process` :
     - Params : `plan_file`, `lesson_id`, `lesson_file` (calculé en 0.2), `mode` = `"create"`
   - Lancer tous les agents dans un même message multi-tool-use via `Agent`

1.2. **Attendre que tous les writers terminent**

1.3. **Collecter les outputs JSON de chaque writer**
   - Champs attendus : `status`, `id`, `file`, `techno`, `concepts`, `last_version`, `last_updated`, `chapters`, `unconfirmed`, `sources`, `report`, `error_message` (si `status: error`)
   - Séparer les writers `success` vs `error`

1.4. **Bilan rédaction + dialogue user** (AVANT Phase 2)
   - Afficher le bilan : nombre de writers `success`, nombre `error`
   - Pour chaque writer en `error`, afficher `id` + `error_message`
   - Pour chaque writer en `success`, afficher ses `sources` et ses `unconfirmed` (faits non rédigés faute de source officielle)
   - Demander au user ce qu'il veut faire :
     - `continuer` → passer en Phase 2 avec les writers `success` uniquement (les `error` sont abandonnés, reportés en Phase 5)
     - `retry errors` → re-spawn les `lesson/writer` en erreur via `Agent`, attendre, mettre à jour la liste success/error, reboucler sur ce même bilan
     - `abort` → arrêter le workflow complet, pas de Phase 2 ni 3, rapport final listant les écrits et les échecs
   - SI tous les writers sont en `error` : ne pas proposer `continuer`, uniquement `retry` ou `abort`
   - SI tous les writers sont `success` sans `unconfirmed` : passer directement en Phase 2 sans demander (pas de dialogue inutile) ; avec des `unconfirmed`, demander `continuer` ou `abort`

### Phase 2 : Audit parallèle

2.1. **Déterminer si l'audit est activé**
   - SI `--skip-audit` présent → skipper entièrement Phase 2 ET Phase 3, passer directement à Phase 4
   - SINON → continuer avec 2.2

2.2. **Lancer les sub-agents `lesson/auditor`** EN PARALLELE (1 par leçon en success)
   - Pour chaque leçon `success` de Phase 1 :
     - Params : `lesson_path` = `<writer.file>`, `plan_file` = `<plan_file>`, `lesson_id` = `<writer.id>`, `writer_unconfirmed` = `<writer.unconfirmed>`
   - Lancer tous les agents dans un même message multi-tool-use via `Agent`

2.3. **Attendre tous les auditors**

2.4. **Collecter les outputs JSON de chaque auditor**
   - Champs attendus : `status` (`pass` | `warn` | `fail` | `error`), `id`, `format_checks`, `plan_spec_checks`, `web_checks`, `blocking_issues`, `recommendations`, `error_message` (si `status: error`)
   - Distinction sémantique : `fail` = audit effectué avec issues bloquantes (corrigeable via re-run writer), `error` = audit impossible (problème système, pas corrigeable automatiquement)

2.5. **Présenter le bilan d'audit au user + demander la suite**
   - Afficher pour chaque leçon en `warn`, `fail` ou `error` : les `blocking_issues` / `recommendations` (pour `warn`/`fail`) ou `error_message` (pour `error`)
   - Pour les leçons en `error` (audit impossible, problème système) : reporter automatiquement dans Phase 5, pas de dialogue de correction possible
   - Pour les leçons en `warn` ou `fail`, demander au user ce qu'il veut faire, par leçon si nécessaire :
     - `continuer tel quel` → la leçon passe en Phase 3 (les `fail` sont exclus, les `warn`/`pass` inclus)
     - `corriger` → relancer `lesson/writer` avec `audit_feedback` = `blocking_issues` + `recommendations` retenues, puis `lesson/auditor` sur le fichier corrigé. Si le writer retourne `error` ou l'audit encore `fail`, rouvrir ce dialogue : pas de boucle auto
     - `exclure` → marquer la leçon comme exclue de la consolidation quel que soit son statut auditor (le fichier reste sur disque mais non référencé dans l'index)
   - Attendre validation AVANT de passer à Phase 3

### Phase 3 : Audit de cohérence inter-leçons

**Note** : Phase 3 est entièrement skippée si `--skip-audit` est présent (voir Phase 2.1).

3.1. **Réutiliser le snapshot de `lessons/index.yaml`** lu en 0.3 (seule cette commande écrit l'index, en 4.3)

3.2. **Construire la liste complète des leçons pour l'audit inter-leçons**
   - Leçons nouvelles candidates à consolider : writer `success` + auditor `pass`/`warn` (ou `--skip-audit`) + non exclues user en Phase 2.5
   - Leçons existantes déjà présentes dans les sections d'index cibles
   - Construire la liste `lessons_paths` : union des 2 listes ci-dessus avec les chemins relatifs de chaque fichier leçon

3.3. **Lancer `lesson/coherence-auditor`** via `Agent` (1 seul spawn, pas de parallélisation car c'est un audit global unique)
   - Params : `plan_file`, `techno` (section d'index cible ; slugs séparés par des virgules si le plan en porte plusieurs), `lessons_paths`
   - Attendre le retour JSON

3.4. **Collecter l'output JSON du coherence-auditor**
   - Champs attendus : `status` (`pass` | `warn` | `fail` | `error`), `techno`, `lessons_audited`, `coverage_checks` (passed/failed), `canonical_checks` (passed/failed), `duplication_checks` (passed/failed), `cross_reference_checks` (passed/failed), `version_checks` (passed/failed), `blocking_issues`, `recommendations`, `error_message` (si `status: error`)

3.5. **Présenter le bilan cohérence inter-leçons au user + demander la suite**
   - Afficher les résultats des 5 catégories d'audit : couverture, canonicité, duplication, renvois, versions
   - Pour chaque issue trouvée, afficher le détail (concept orphelin, leçon dupliquée, renvoi cassé, etc.)
   - SI `pass` → continuer automatiquement vers Phase 4 (pas de dialogue inutile)
   - SI `warn` → afficher les `recommendations`, demander au user `continuer` ou `corriger certaines leçons`
   - SI `fail` → dialogue obligatoire :
     - `continuer tel quel` → passer à Phase 4 pour consolidation malgré les issues (user assume)
     - `corriger` → re-run `lesson/writer` (avec `audit_feedback` = issues de cohérence qui les concernent) puis `lesson/auditor` sur les leçons concernées, puis `lesson/coherence-auditor` global. Si encore `fail`, rouvrir ce dialogue : pas de boucle auto
     - `exclure` → marquer une ou plusieurs leçons comme exclues de la consolidation (fichiers restent sur disque, non référencés dans l'index)
   - SI `error` (audit cohérence impossible, problème système) → reporter dans Phase 5, pas de dialogue de correction. Consolider quand même si le user l'autorise (dialogue : `continuer sans audit cohérence` / `abort`)
   - Attendre validation AVANT de passer à Phase 4

### Phase 4 : Consolidation de l'index

4.1. **Déterminer les leçons à consolider (liste finale)**
   - `--skip-audit` : writer `success`
   - SINON : writer `success` ET auditor `pass`/`warn` ET cohérence `pass`/`warn` (ou `continuer tel quel` validé en 3.5) ET non exclue en 2.5 ni 3.5

4.2. **Construire la nouvelle section de chaque section d'index cible**
   - SI la section n'existe pas encore dans l'index → la créer avec `last_updated` et `lessons: []`, à la racine ou imbriquée sous sa techno parente selon "Versions cibles" (cf. skill lesson-doc § Conventions de nommage)
   - SINON → récupérer la section existante ET **préserver tous ses champs existants** (`notion_id`, `icon`, `cover`, sous-technos imbriquées). Ne modifier QUE la liste `lessons` et `last_updated`
   - Fusionner les leçons existantes et les nouvelles leçons à consolider dans une seule liste
   - **Ré-ordonner toutes les leçons de la section** selon l'ordre défini dans la section "Ordre d'exécution recommandé" du plan (pas un append simple : les nouvelles leçons doivent s'intercaler au bon endroit)
   - Pour chaque nouvelle entrée : `id`, `file` (= `lesson_file`), `concepts`, `last_version`, `last_updated` (pas de `notion_id` au niveau leçon : les nouvelles leçons ne sont pas encore publiées sur Notion)
   - Mettre à jour le `last_updated` de la section, et de la techno parente pour une sous-techno

4.3. **Écrire `lessons/index.yaml`**
   - `Read` l'index juste avant d'écrire : d'autres sessions peuvent l'avoir modifié depuis le snapshot de la Phase 0.3
   - Remplacer via `Edit` le seul bloc `lessons:` de chaque section cible (et ses `last_updated`) ; le reste de l'index n'est jamais réécrit. Une section créée est insérée par `Edit` à sa place (à la racine, dans l'ordre alphabétique des sections ; sous-techno, à la fin de sa techno parente)
   - `Write` sur l'index complet est interdit

### Phase 5 : Rapport final

5.1. **Présenter au user**
   - Leçons consolidées ; échecs de rédaction (writer `error`) avec raison ; `unconfirmed` des writers
   - Audits non résolus : auditor `warn`/`fail`/`error` avec issues, bilan cohérence et issues restantes
   - Leçons exclues par le user (2.5, 3.5)
   - État final de l'index (entrées par section)

## Regles

### TodoWrite

- **DEBUT** : créer les 6 phases (Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5)
- **A CHAQUE PHASE** : créer les todos avec les **numéros et titres EXACTS** du workflow (ex : "1.1 Lancer les lesson/writer EN PARALLELE", "1.2 Attendre que tous les writers terminent")
- **PROGRESSION** : marquer chaque sous-étape completed IMMEDIATEMENT après l'avoir terminée ; phase suivante seulement quand toutes le sont
- **INTERDIT** : compacter, simplifier, regrouper ou renommer des todos

### Interactions user

- **Validations obligatoires** : 0.5 (leçons à traiter), 1.4 (si erreurs ou `unconfirmed`), 2.5 et 3.5 (si issues) ; chaque bilan affiche les issues avant de demander
- **Corrections = re-run writer** : en Phase 2.5 et Phase 3.5, l'option `corriger` relance toujours `lesson/writer` avec `audit_feedback`, ni l'auditor ni le coherence-auditor ne modifient jamais directement les fichiers

### Technique

- **Parallélisation maximale** : Phase 1 et Phase 2 lancent tous les agents dans un même message multi-tool-use
- **Index centralisé** : SEULE cette commande écrit dans `lessons/index.yaml`. Les 3 sub-agents `lesson/writer`, `lesson/auditor`, `lesson/coherence-auditor` ne le touchent JAMAIS
- **Gestion d'échec partiel** : si un writer échoue mais d'autres réussissent, consolider ce qui peut l'être et reporter les échecs sans bloquer le reste
- **Ordre dans l'index** : respecter strictement l'ordre défini dans la section "Ordre d'exécution recommandé" du plan
- **Plan multi-techno** : chaque leçon suit la techno de son titre `## Leçons {Techno}` ; chaque section d'index cible est consolidée séparément

### Anti-doublon

- **Filtrage automatique** : si `--lessons` n'est pas spécifié, exclure automatiquement les leçons déjà dans l'index
- **Forçage explicite** : si `--lessons` force une leçon existante, le writer écrasera le fichier via `Write` (l'utilisateur est responsable)

### Gestion des erreurs

- **Plan inexistant** : SI `Read` sur `--plan` échoue → erreur claire avec le chemin testé et arrêter
- **Plan mal formé** : SI aucune section `### N. <id>` n'est détectée dans le plan → erreur "format de plan invalide, sections `### N. <id>` attendues" et arrêter
- **Écriture `lessons/index.yaml` échoue** : lever l'erreur, afficher l'état partiel au user (leçons écrites sur disque mais pas consolidées), proposer un re-run de Phase 4 uniquement
