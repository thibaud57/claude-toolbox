---
description: Génère une ou plusieurs leçons pédagogiques à partir d'un plan (ex. next-plan.md, redis-plan.md). Orchestre writer + auditor individuel + coherence-auditor global, et consolide lessons/index.yaml.
argument-hint: [--plan=<chemin> --lessons=<id1,id2> --skip-audit]
allowed-tools: Read, Write, Edit, WebSearch, WebFetch
---

# Create Lesson - Orchestrateur de création de leçons

Ta mission est de générer une ou plusieurs leçons pédagogiques à partir d'un plan passé en input, en orchestrant les sub-agents `lesson/writer` + `lesson/auditor` en parallèle (rédaction et audit individuel), puis `lesson/coherence-auditor` pour l'audit global inter-leçons, et en consolidant `lessons/index.yaml` de manière centralisée.

## Prerequis

- Un fichier plan existant à la racine du repo (ex : `next-plan.md`, `redis-plan.md`) au format attendu (sections `### N. <id>` avec concepts + points clés, matrice anti-redondance, breaking changes, versions cibles)

## Input

- `--plan=<chemin>` : Chemin du plan pédagogique (OBLIGATOIRE)
- `--lessons=<ids>` : CSV d'ids à traiter (optionnel, défaut : toutes les leçons du plan non encore présentes dans l'index)
- `--skip-audit` : Désactive les deux audits (Phase 2 audit individuel ET Phase 3 audit cohérence inter-leçons). Optionnel, défaut : les deux audits sont activés

## Workflow

### Phase 0 : Préparation

0.1. **Parser `$ARGUMENTS`**
   - Extraire `--plan`, `--lessons`, `--skip-audit`
   - SI `--plan` absent → erreur et arrêter

0.2. **Lire le plan** avec `Read`
   - Extraire la techno cible depuis la section "Versions cibles" ou par détection du nom de fichier (ex : `next-plan.md` → `nextjs`)
   - Extraire l'ordre d'exécution depuis "Ordre d'exécution recommandé"
   - Parser les sections `### N. <id>` pour lister toutes les leçons du plan

0.3. **Lire `lessons/index.yaml`** avec `Read`
   - Identifier les leçons déjà écrites pour la techno cible

0.4. **Construire la liste `lessons_to_process`**
   - SI `--lessons` présent :
     - Valider que chaque id existe dans le plan (section `### N. <id>` présente)
     - SI un id est inconnu → erreur claire listant les ids invalides et arrêter
     - SINON → utiliser exactement ces ids (même si déjà dans l'index, l'utilisateur force)
   - SINON → toutes les leçons du plan non présentes dans l'index pour la techno
   - SI la liste est vide (aucune leçon à traiter) → afficher "Toutes les leçons du plan sont déjà dans l'index pour la techno <techno>" et arrêter proprement

0.5. **Présenter la liste au user** et attendre validation AVANT de lancer les agents
   - Afficher : techno, nombre de leçons à traiter, ids dans l'ordre du plan
   - Afficher : mode audit (activé/désactivé)

### Phase 1 : Rédaction parallèle

1.1. **Lancer les sub-agents `lesson/writer`** EN PARALLELE (1 par leçon)
   - Pour chaque `lesson_id` dans `lessons_to_process` :
     - Params : `plan_file`, `lesson_id`
   - Lancer tous les agents dans un même message multi-tool-use via `Task`

1.2. **Attendre que tous les writers terminent**

1.3. **Collecter les outputs JSON de chaque writer**
   - Champs attendus : `status`, `id`, `file`, `techno`, `concepts`, `last_version`, `last_updated`, `chapters`, `report`, `error_message` (si `status: error`)
   - Séparer les writers `success` vs `error`

1.4. **Bilan rédaction + dialogue user** (AVANT Phase 2)
   - Afficher le bilan : nombre de writers `success`, nombre `error`
   - Pour chaque writer en `error`, afficher `id` + `error_message`
   - Demander au user ce qu'il veut faire :
     - `continuer` → passer en Phase 2 avec les writers `success` uniquement (les `error` sont abandonnés, reportés en Phase 5)
     - `retry errors` → re-spawn les `lesson/writer` en erreur via `Task`, attendre, mettre à jour la liste success/error, reboucler sur ce même bilan
     - `abort` → arrêter le workflow complet, pas de Phase 2 ni 3, rapport final listant les écrits et les échecs
   - SI tous les writers sont en `error` : ne pas proposer `continuer`, uniquement `retry` ou `abort`
   - SI tous les writers sont `success` : passer directement en Phase 2 sans demander (pas de dialogue inutile)

### Phase 2 : Audit parallèle

2.1. **Déterminer si l'audit est activé**
   - SI `--skip-audit` présent → skipper entièrement Phase 2 ET Phase 3, passer directement à Phase 4
   - SINON → continuer avec 2.2

2.2. **Lancer les sub-agents `lesson/auditor`** EN PARALLELE (1 par leçon en success)
   - Pour chaque leçon `success` de Phase 1 :
     - Params : `lesson_path` = `<writer.file>`, `plan_file` = `<plan_file>`, `lesson_id` = `<writer.id>`
   - Lancer tous les agents dans un même message multi-tool-use via `Task`

2.3. **Attendre tous les auditors**

2.4. **Collecter les outputs JSON de chaque auditor**
   - Champs attendus : `status` (`pass` | `warn` | `fail` | `error`), `id`, `format_checks`, `plan_spec_checks`, `web_checks`, `blocking_issues`, `recommendations`, `error_message` (si `status: error`)
   - Distinction sémantique : `fail` = audit effectué avec issues bloquantes (corrigeable via re-run writer), `error` = audit impossible (problème système, pas corrigeable automatiquement)

2.5. **Présenter le bilan d'audit au user + demander la suite**
   - Afficher pour chaque leçon en `warn`, `fail` ou `error` : les `blocking_issues` / `recommendations` (pour `warn`/`fail`) ou `error_message` (pour `error`)
   - Pour les leçons en `error` (audit impossible, problème système) : reporter automatiquement dans Phase 5, pas de dialogue de correction possible
   - Pour les leçons en `warn` ou `fail`, demander au user ce qu'il veut faire, par leçon si nécessaire :
     - `continuer tel quel` → la leçon passe en Phase 3 (les `fail` sont exclus, les `warn`/`pass` inclus)
     - `corriger` → relancer `lesson/writer` pour la leçon via `Task` (le writer re-rédige depuis zéro en tenant compte des issues remontées), puis relancer `lesson/auditor` sur le nouveau fichier pour re-valider. L'auditor ne corrige JAMAIS lui-même, seul le writer peut modifier le fichier. Si le re-run writer retourne `error` (LLM timeout, erreur réseau, etc.) OU si le re-audit retourne à nouveau `fail`, re-ouvrir ce dialogue 2.5 pour la leçon (le user peut choisir `continuer tel quel`, re-tenter `corriger`, ou `exclure`). Pas de boucle auto, le user contrôle à chaque itération
     - `exclure` → marquer la leçon comme exclue de la consolidation quel que soit son statut auditor (le fichier reste sur disque mais non référencé dans l'index)
   - Attendre validation AVANT de passer à Phase 3

### Phase 3 : Audit de cohérence inter-leçons

**Note** : Phase 3 est entièrement skippée si `--skip-audit` est présent (voir Phase 2.1).

3.1. **Réutiliser le snapshot de `lessons/index.yaml`** lu en Phase 0.3 (pas besoin de re-lire : aucun sub-agent n'a touché à l'index entre Phase 0.3 et ici, seule cette commande écrit dans l'index et uniquement en Phase 4.3)

3.2. **Construire la liste complète des leçons de la techno pour l'audit inter-leçons**
   - Leçons nouvelles candidates à consolider : writer `success` + auditor `pass`/`warn` (ou `--skip-audit`) + non exclues user en Phase 2.5
   - Leçons existantes déjà présentes dans l'index pour la techno cible
   - Construire la liste `lessons_paths` : union des 2 listes ci-dessus avec les chemins relatifs de chaque fichier leçon

3.3. **Lancer `lesson/coherence-auditor`** via `Task` (1 seul spawn, pas de parallélisation car c'est un audit global unique)
   - Params : `plan_file`, `techno`, `lessons_paths`
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
     - `corriger` → re-run `lesson/writer` pour les leçons concernées (via `Task`), puis re-run `lesson/auditor` individuel sur ces leçons, puis re-run `lesson/coherence-auditor` global pour re-valider la cohérence. Si re-audit cohérence retourne encore `fail`, re-ouvrir ce dialogue 3.5 (pas de boucle auto, user contrôle à chaque itération). Note : ce dialogue n'a lieu qu'en mode audit activé (sinon toute la Phase 3 est skippée par `--skip-audit`)
     - `exclure` → marquer une ou plusieurs leçons comme exclues de la consolidation (fichiers restent sur disque, non référencés dans l'index)
   - SI `error` (audit cohérence impossible, problème système) → reporter dans Phase 5, pas de dialogue de correction. Consolider quand même si le user l'autorise (dialogue : `continuer sans audit cohérence` / `abort`)
   - Attendre validation AVANT de passer à Phase 4

### Phase 4 : Consolidation de l'index

4.1. **Déterminer les leçons à consolider (liste finale)**
   - SI `--skip-audit` présent (Phase 2 et Phase 3 ont été skippées) : condition = writer `success` uniquement (pas de filtrage par audit ni exclusions user, car les dialogues 2.5 et 3.5 n'ont pas eu lieu)
   - SINON : condition = writer `success` ET auditor `pass`/`warn` ET non exclue user en Phase 2.5 ET (coherence-auditor `pass`/`warn` OU user a validé `continuer tel quel` malgré `fail`/`error` en Phase 3.5) ET non exclue user en Phase 3.5
   - Exclure dans tous les cas : writer `error`. Exclure en mode audit activé : auditor `fail`/`error`, leçons marquées `exclure` en Phase 2.5 ou Phase 3.5

4.2. **Construire la nouvelle section techno de l'index**
   - SI la techno n'existe pas encore dans l'index → créer une nouvelle section avec `last_updated` et `lessons: []`
   - SINON → récupérer la section existante pour la techno ET **préserver tous ses champs existants** (ex : `notion_id` au niveau techno s'il est présent, ou autres métadonnées). Ne modifier QUE la liste `lessons` et `last_updated`
   - Fusionner les leçons existantes et les nouvelles leçons à consolider dans une seule liste
   - **Ré-ordonner toutes les leçons de la techno** selon l'ordre défini dans la section "Ordre d'exécution recommandé" du plan (pas un append simple : les nouvelles leçons doivent s'intercaler au bon endroit)
   - Pour chaque nouvelle entrée : `id`, `file`, `concepts`, `last_version`, `last_updated` (pas de `notion_id` au niveau leçon : les nouvelles leçons ne sont pas encore publiées sur Notion)
   - Mettre à jour le `last_updated` de la techno parente

4.3. **Écrire `lessons/index.yaml`**
   - Utiliser `Write` pour reconstruire le fichier complet (le ré-ordonnancement de Phase 4.2 impose une reconstruction, `Edit` ne suffit pas)
   - Une seule écriture atomique à la fin (zéro race condition car aucun sub-agent ne touche au fichier)

### Phase 5 : Rapport final

5.1. **Présenter au user**
   - Nombre et liste des leçons écrites avec succès et consolidées
   - Leçons échouées en rédaction (writer `error`) avec raison
   - Leçons avec warnings (auditor `warn`) avec issues mineures
   - Leçons bloquées par audit individuel (auditor `fail`) avec issues et suggestion de re-run
   - Leçons en erreur système d'audit individuel (auditor `error`) avec `error_message`
   - Leçons exclues manuellement par l'utilisateur en Phase 2.5
   - Bilan de l'audit cohérence inter-leçons (Phase 3.5) : `pass`/`warn`/`fail`/`error` + issues non résolues
   - Leçons exclues manuellement en Phase 3.5 suite à l'audit cohérence
   - État final de l'index (nombre d'entrées pour la techno)

## Regles

### TodoWrite

- **DEBUT** : créer les 6 phases (Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5)
- **A CHAQUE PHASE** : créer les todos avec les **numéros et titres EXACTS** du workflow
  - Exemple Phase 1 : "1.1 Lancer les lesson/writer EN PARALLELE", "1.2 Attendre que tous les writers terminent", "1.3 Collecter les outputs JSON", "1.4 Bilan rédaction + dialogue user"
  - Exemple Phase 3 : "3.1 Lire lessons/index.yaml", "3.2 Construire liste complète", "3.3 Lancer lesson/coherence-auditor", "3.4 Collecter output JSON", "3.5 Présenter bilan cohérence + dialogue user"
  - **NE PAS** reformuler, regrouper ou réinterpréter les étapes
  - Garder les phases précédentes (completed) et suivantes (pending) visibles
- **PROGRESSION** : marquer chaque sous-étape completed IMMEDIATEMENT après l'avoir terminée
- **TRANSITION** : ne passer à la phase suivante QUE si toutes les sous-étapes sont completed
- **INTERDIT** : compacter, simplifier, regrouper ou renommer des todos

### Interactions user

- **Validation AVANT lancement** : Phase 0.5 présente la liste des leçons et attend validation avant Phase 1
- **Bilan rédaction + dialogue** : en Phase 1.4, présenter le bilan writers (success/error) et demander au user (`continuer` / `retry errors` / `abort`) AVANT Phase 2
- **Warnings visibles audit individuel + dialogue** : en Phase 2.5, présenter le bilan d'audit individuel par leçon (`blocking_issues`, `recommendations`) et demander au user par leçon (`continuer tel quel` / `corriger` via re-run writer / `exclure`) AVANT Phase 3
- **Bilan cohérence inter-leçons + dialogue** : en Phase 3.5, présenter le bilan coherence-auditor (couverture, canonicité, duplication, renvois, versions) et demander au user (`continuer tel quel` / `corriger` via re-run writer+auditor+coherence / `exclure`) AVANT Phase 4
- **Corrections = re-run writer** : en Phase 2.5 et Phase 3.5, l'option `corriger` relance toujours `lesson/writer` (qui a `Write`/`Edit`), ni l'auditor ni le coherence-auditor ne modifient jamais directement les fichiers
- **Rapport final clair** : Phase 5 doit séparer succès, échecs rédaction, warnings/blocages audit individuel, issues cohérence inter-leçons, exclusions user

### Technique

- **Parallélisation maximale** : Phase 1 et Phase 2 lancent tous les agents dans un même message multi-tool-use
- **Index centralisé** : SEULE cette commande écrit dans `lessons/index.yaml`. Les 3 sub-agents `lesson/writer`, `lesson/auditor`, `lesson/coherence-auditor` ne le touchent JAMAIS
- **Gestion d'échec partiel** : si un writer échoue mais d'autres réussissent, consolider ce qui peut l'être et reporter les échecs sans bloquer le reste
- **Ordre dans l'index** : respecter strictement l'ordre défini dans la section "Ordre d'exécution recommandé" du plan

### Anti-doublon

- **Filtrage automatique** : si `--lessons` n'est pas spécifié, exclure automatiquement les leçons déjà dans l'index
- **Forçage explicite** : si `--lessons` force une leçon existante, le writer écrasera le fichier via `Write` (l'utilisateur est responsable)

### Gestion des erreurs

- **Plan inexistant** : SI `Read` sur `--plan` échoue → erreur claire avec le chemin testé et arrêter
- **Plan mal formé** : SI aucune section `### N. <id>` n'est détectée dans le plan → erreur "format de plan invalide, sections `### N. <id>` attendues" et arrêter
- **`--lessons` avec ids inconnus** : géré en Phase 0.4 (erreur listant les ids invalides)
- **Aucune leçon à traiter** : géré en Phase 0.4 (message informatif et arrêt propre)
- **Tous les writers en erreur** : Phase 1.4 propose `retry` ou `abort` (pas `continuer` car rien à continuer). Si `abort`, passer à Phase 5 avec rapport listant tous les échecs
- **Coherence-auditor `error`** (audit global impossible) : dialogue Phase 3.5 propose `continuer sans audit cohérence` ou `abort`. L'état sera reporté dans Phase 5
- **Écriture `lessons/index.yaml` échoue** : lever l'erreur, afficher l'état partiel au user (leçons écrites sur disque mais pas consolidées), proposer un re-run de Phase 4 uniquement
