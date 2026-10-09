---
description: Met à jour les leçons d'une techno vers sa version stable actuelle. Recherche les changements sur sources officielles, cadre leur placement dans un plan de mise à jour (modifier, créer, fusionner, supprimer, bump seul), puis orchestre writer + auditor individuel + coherence-auditor et consolide lessons/index.yaml.
argument-hint: [--techno=<slug|toutes> --lessons=<id1,id2> --concepts=<liste> --skip-audit]
allowed-tools: Read, Write, Edit, WebSearch, WebFetch, Bash(git status *), Bash(git restore *), Bash(git rm *), Bash(rm lessons/*)
---

# Update Lesson - Orchestrateur de mise à jour de leçons

Ta mission est de mettre à jour les leçons d'une techno entre leur `last_version` et la version stable actuelle : rechercher les changements sur sources officielles, les cadrer dans un plan de mise à jour validé par le user, puis orchestrer les sub-agents `lesson/writer` + `lesson/auditor` en parallèle et `lesson/coherence-auditor` pour l'audit global, en consolidant `lessons/index.yaml` de manière centralisée.

## Input

- `--techno=<slug|toutes>` : Techno ou sous-techno cible, telle que nommée dans `lessons/index.yaml` (ex : `redis`, `fastapi`) ; `toutes` dresse l'inventaire de toutes les technos en Phase 0, puis une seule est traitée (OBLIGATOIRE)
- `--lessons=<ids>` : CSV d'ids à restreindre (optionnel, défaut : toutes les leçons de la techno)
- `--concepts=<liste>` : Concepts à cibler en priorité. Avec `--lessons`, inclut ces leçons même à jour (enrichissement) (optionnel)
- `--skip-audit` : Désactive la Phase 4 (audits individuel et inter-leçons) (optionnel, défaut : audits activés)

## Constantes

- **TEMPLATE_UPDATE_PLAN** : `plans/template-update-plan.md`
- **UPDATE_PLAN_FILE** : `plans/<techno>-update-<version actuelle>.md` (ex : `plans/fastapi-update-0.143.md`). Exemples conservés : `plans/*-update-*-exemple.md`. S'il existe déjà (enrichissement à version identique, relance) : demander au user d'écraser ou de suffixer par la date (`-<AAAA-MM-JJ>`)

## Workflow

### Phase 0 : Préparation

0.0. **Lire `.claude/skills/lesson-doc/SKILL.md`** : source des règles citées plus bas (versions, index, nommage)

0.1. **Parser `$ARGUMENTS`**
   - Extraire `--techno`, `--lessons`, `--concepts`, `--skip-audit`
   - SI `--techno` absent → demander la techno au user

0.2. **Lire `lessons/index.yaml`** avec `Read`
   - Localiser la section de la techno, à la racine ou imbriquée sous une techno parente (cf. skill lesson-doc § Conventions de nommage) ; `toutes` → toutes les sections, sous-technos comprises
   - SI introuvable → erreur listant les technos et sous-technos de l'index, et arrêter
   - Pour chaque leçon : `id`, `file`, `concepts`, `last_version`. SI `--lessons` présent → valider les ids (erreur listant les ids inconnus) et restreindre la liste

0.3. **Identifier les versions actuelles**
   - Version stable actuelle de la techno, et de chaque outil distinct suivi par une leçon (cf. skill lesson-doc § Règles leçon > Index)
   - Source : registre de packages ou release officielle, version au format `major.minor` (cf. skill lesson-doc § Règles leçon > Recherches)

0.4. **Construire le tableau des leçons**
   - Statut par leçon : `outdated` (`last_version` < version actuelle de ce qu'elle suit), `à jour`, ou `enrichissement` (`--lessons` + `--concepts` sur une leçon à jour)
   - `last_version: null` et versions objet : appliquer la comparaison du skill (cf. skill lesson-doc § Règles leçon > Recherches) (`null` toujours inclus ; objet outdated si un composant l'est)
   - SI aucune leçon `outdated` ni `enrichissement` → informer le user et arrêter proprement

0.5. **Présenter le tableau au user** (techno | leçon | version leçon | version actuelle | statut | source) et attendre validation
   - Demander quelles leçons inclure (défaut : toutes les `outdated` et `enrichissement`) ; avec `toutes`, demander d'abord la techno à traiter (une par run)
   - Afficher : mode audit (activé/désactivé)

### Phase 1 : Recherche des changements

1.1. **Collecter les changements entre la plus petite `last_version` incluse et la version actuelle**
   - Sources dans cet ordre : release notes ou changelog complets (version brute de préférence, ex : fichier markdown du dépôt plutôt que page rendue tronquée), guide de migration, doc officielle des nouveautés, puis code source ou PR quand la doc ne tranche pas
   - Chaque changement retenu porte sa version, son URL et un extrait verbatim court (cf. skill lesson-doc § Règles leçon > Recherches, Traçabilité des sources)
   - SI `--concepts` présent → concentrer la recherche sur ces concepts, à version actuelle pour un enrichissement
   - Leçon en `last_version: null` : pas de borne inférieure, confronter son contenu à la doc actuelle (APIs citées, dépréciations, suppressions)
   - Version objet : collecter par composant, chacun depuis sa propre version

1.2. **Croiser avec le contenu des leçons incluses**
   - `Grep` sur les dossiers de la techno pour les APIs et versions touchées par chaque changement, `Read` ciblé sur les passages concernés
   - Repérer aussi les mentions devenues fausses (labels de version, « depuis X », formulations datées)

1.3. **Classer chaque changement** : `confirmé` (source officielle lue) ou `non confirmé` (déduction, source tierce, page tronquée). Un `non confirmé` n'est jamais assigné à une leçon

### Phase 2 : Cadrage

2.1. **Décider le placement de chaque changement confirmé**
   - Leçon et chapitre canoniques (un concept = une leçon canonique, renvoi bref ailleurs)
   - Action par leçon : `modifier`, `créer`, `fusionner dans <slug>`, `supprimer` ou `bump seul`
   - Une nouvelle leçon se justifie quand les changements forment un bloc mental cohérent qu'aucune leçon existante ne porte ; sinon un chapitre ou des bullets dans la leçon canonique suffisent

2.2. **Écrire UPDATE_PLAN_FILE** à partir de TEMPLATE_UPDATE_PLAN (`Read` du template d'abord)
   - Remplir toutes ses sections, dont "Versions cibles" (section d'index et dossier) et "Ordre d'exécution recommandé" (position des leçons créées)

2.3. **Présenter le plan au user** et attendre validation AVANT la Phase 3
   - Afficher : tableau des décisions de structure, changements par leçon avec leur source, changements `non confirmé` (et pourquoi), chemin de UPDATE_PLAN_FILE
   - Le user peut amender le plan directement : relire UPDATE_PLAN_FILE après sa validation

2.4. **Router selon les actions validées**
   - SI au moins une leçon est à `modifier`, `créer` ou cible de `fusionner` → Phase 3 sur ces leçons
   - SINON SI des leçons sont à `supprimer` → passer en 4.3 (sauf `--skip-audit`), puis Phase 5
   - SINON (uniquement des `bump seul`) → passer directement en Phase 5

### Phase 3 : Rédaction parallèle

3.0. **Repérer l'état git des leçons à modifier** : `git status --short -- <files>`, noter celles qui ont déjà des modifications non commitées (cf. § Règles > Annulation)

3.1. **Lancer les sub-agents `lesson/writer`** EN PARALLELE (1 par leçon à modifier ou créer)
   - Params : `plan_file` = UPDATE_PLAN_FILE, `lesson_id`, `lesson_file` (champ `file` de l'index, ou `<dossier>/<id>.md` pour une leçon créée), `mode` = `"update"` ou `"create"`
   - Lancer tous les agents dans un même message multi-tool-use via `Agent`

3.2. **Attendre que tous les writers terminent**

3.3. **Collecter les outputs JSON** : `status`, `mode`, `id`, `file`, `concepts`, `last_version`, `chapters`, `changes_applied`, `unconfirmed`, `sources`, `report`, `error_message` (si `status: error`)

3.4. **Bilan rédaction + dialogue user** (AVANT Phase 4)
   - Afficher : writers `success` / `error`, et pour chaque writer ses `sources` et ses `unconfirmed` (changements du plan non rédigés faute de confirmation)
   - SI des writers sont en `error` → demander : `continuer` (sans eux) / `retry errors` / `abort`
   - SI tous en `error` → proposer uniquement `retry` ou `abort`
   - SI des `unconfirmed` → demander : `accepter` (ces changements restent hors leçon et partent au rapport) / `amender le plan` (corriger ou sourcer les changements dans UPDATE_PLAN_FILE, puis relancer les writers concernés)
   - SI tous en `success` sans `unconfirmed` → passer directement en Phase 4

### Phase 4 : Audit

**Note** : Phase 4 entièrement skippée si `--skip-audit` est présent.

4.1. **Lancer les sub-agents `lesson/auditor`** EN PARALLELE (1 par leçon `success`)
   - Params : `lesson_path` = `<writer.file>`, `plan_file` = UPDATE_PLAN_FILE, `lesson_id`, `writer_unconfirmed` = `<writer.unconfirmed>`

4.2. **Bilan d'audit individuel + dialogue user**, par leçon en `warn`, `fail` ou `error`
   - `continuer tel quel`
   - `corriger` → relancer `lesson/writer` avec `audit_feedback` = `blocking_issues` + `recommendations` retenues, puis relancer `lesson/auditor`. Pas de boucle auto : rouvrir ce dialogue tant que le user le demande
   - `annuler` → restaurer la leçon (cf. § Règles > Annulation) et l'exclure de la consolidation
   - Attendre validation AVANT 4.3

4.3. **Lancer `lesson/coherence-auditor`** SI la structure change (leçon créée, fusionnée ou supprimée) ou si des renvois entre leçons ont été modifiés
   - Params : `plan_file` = UPDATE_PLAN_FILE, `techno`, `lessons_paths` = toutes les leçons de la section d'index après mise à jour (hors leçons à supprimer)

4.4. **Bilan cohérence + dialogue user**
   - SI `pass` → Phase 5 sans dialogue
   - SINON → afficher les 5 catégories et proposer `continuer tel quel` / `corriger` (writer avec `audit_feedback`, puis auditor, puis coherence-auditor) / `annuler` certaines leçons

### Phase 5 : Consolidation

5.1. **Appliquer les suppressions et fusions validées**
   - Confirmer explicitement avec le user, fichier par fichier, avant toute suppression
   - Leçon fusionnée ou supprimée : retirer le fichier (`git rm` s'il est suivi, sinon `rm`) et son entrée d'index
   - Source d'une fusion : ne la supprimer que si sa leçon cible est en `success` et non annulée ; sinon la conserver telle quelle et le signaler au rapport

5.2. **Mettre à jour `lessons/index.yaml`** (cf. skill lesson-doc § Règles leçon > Index)
   - `Read` l'index juste avant d'écrire : d'autres sessions peuvent l'avoir modifié depuis la Phase 0.2
   - Leçons modifiées ou créées (writer `success`, non annulées) : `concepts` (output writer), `last_version`, `last_updated`
   - Leçons créées : insérées selon "Ordre d'exécution recommandé" du plan, avec `id`, `file`, `concepts`, `last_version`, `last_updated` (pas de `notion_id`)
   - Bump de `last_version` sur les leçons incluses en 0.5 qui suivent la même version, même non modifiées ; les leçons non incluses et celles qui suivent un outil distinct non mis à jour gardent leur `last_version`
   - `last_updated` de la section, et de la techno parente pour une sous-techno
   - Modifications via `Edit` sur la seule section concernée ; `Write` sur l'index complet est interdit

### Phase 6 : Rapport final

6.1. **Présenter au user**
   - Leçons modifiées, créées, fusionnées, supprimées, bumpées seules
   - Changements `non confirmé` (Phase 1.3 et `unconfirmed` des writers) restés hors des leçons
   - Bilans d'audit non résolus (`warn`, `fail` acceptés, `error`), leçons annulées
   - Chemin de UPDATE_PLAN_FILE

## Règles

### TodoWrite

- **DEBUT** : créer les 7 phases (Phase 0 à Phase 6)
- **A CHAQUE PHASE** : créer les todos avec les **numéros et titres EXACTS** du workflow (ex : "1.1 Collecter les changements", "1.2 Croiser avec le contenu des leçons incluses")
- **PROGRESSION** : marquer chaque sous-étape completed IMMEDIATEMENT après l'avoir terminée
- **INTERDIT** : compacter, simplifier, regrouper ou renommer des todos

### Interactions user

- **Validations obligatoires** : 0.5 (leçons incluses), 2.3 (plan de mise à jour), 3.4 (si erreurs ou `unconfirmed`), 4.2 et 4.4 (si issues), 5.1 (toute suppression)
- **Corrections = re-run writer** : seul `lesson/writer` modifie les leçons, toujours avec `audit_feedback` ; les auditors ne modifient jamais rien

### Recherche

- **Traçabilité** : appliquer la règle Traçabilité des sources (cf. skill lesson-doc § Règles leçon > Recherches). Les preuves vont dans UPDATE_PLAN_FILE et dans les bilans, jamais dans les leçons
- **Contenu partiel** : une page rendue tronquée ou un résumé d'outil ne vaut pas lecture. Chercher la version brute (markdown du dépôt, release GitHub) avant de conclure qu'une info est absente
- **Centralisée** : la recherche est faite une fois en Phase 1 et figée dans le plan ; les writers vérifient les sources citées, ils ne refont pas l'inventaire des changements

### Technique

- **Parallélisation maximale** : Phases 3 et 4.1 lancent tous les agents dans un même message multi-tool-use
- **Index centralisé** : SEULE cette commande écrit dans `lessons/index.yaml`, uniquement en Phase 5.2
- **Gestion d'échec partiel** : consolider ce qui a réussi, reporter les échecs sans bloquer le reste

### Annulation

- Leçon modifiée suivie par git, sans modification non commitée avant la Phase 3 : `git restore -- <file>` après confirmation du user
- Leçon qui avait déjà des modifications non commitées (relevées en 3.0) : jamais de `git restore`, qui les effacerait ; signaler au user, qui restaure lui-même
- Leçon créée : supprimer le fichier après confirmation du user
- Une leçon annulée n'est pas consolidée dans l'index
