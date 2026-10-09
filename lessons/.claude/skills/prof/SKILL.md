---
name: prof
description: Rédige ou met à jour une leçon de programmation (fiche de révision dense pour développeurs mid / senior). Utiliser quand l'utilisateur demande à créer une leçon ou à mettre à jour une leçon existante.
argument-hint: [--techno=<nom> --lecon=<titre> --concepts=<liste>]
disable-model-invocation: true
allowed-tools: Read, Write, Edit, WebSearch, WebFetch
---

# Prof - Professeur de Programmation

Ta mission est de rédiger ou mettre à jour une leçon de programmation, une à la fois, selon les conventions et règles du skill `lesson-doc`.

## Prérequis

Charger le skill `lesson-doc` pour connaître la structure, les conventions de format et les règles de recherche et d'index.

## Input

- `--techno=<nom>` : Techno ou sous-techno cible, telle que nommée dans l'index (ex : `nextjs`, `fastapi`) (OBLIGATOIRE, demandé si absent)
- `--lecon=<titre>` : Titre de la leçon (CREATE, l'`id` kebab-case en est déduit) ou leçon à mettre à jour (UPDATE) (OBLIGATOIRE, demandé si absent)
- `--concepts=<liste>` : Concepts à couvrir, séparés par des virgules (CREATE, demandé si absent) ou à ajouter / cibler (UPDATE, optionnel)

## Constantes

### Fixes

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `TEMPLATE_LECON` | `.claude/skills/lesson-doc/templates/lesson.md` | Structure d'une leçon |
| `EXEMPLES` | `.claude/skills/lesson-doc/examples/` | Leçons exemplaires, à lire pour calibrer style et densité |
| `INDEX` | `lessons/index.yaml` | Index des leçons |
| `DOSSIER_LECONS` | `lessons/<techno>/` ou `lessons/<techno>/<sous-techno>/` | Dossier de la (sous-)techno (cf. skill lesson-doc § Conventions de nommage) |

## Workflow

### Préparation

1. Mode : la leçon (`--techno` + `--lecon`) existe dans INDEX → UPDATE, sinon CREATE ; ambigu → demander
2. Demander les inputs manquants
3. Créer la todo list du mode

### Mode CREATE

1. Analyser les concepts : regrouper, hiérarchiser, ajouter les manquants indispensables
2. Recherches (cf. skill lesson-doc § Règles leçon > Recherches, CREATE), jamais de rédaction avant
3. Rédiger selon TEMPLATE_LECON, calibré sur EXEMPLES, dans l'ordre pédagogique optimal, `> ⚠️` sur les dépréciations et suppressions trouvées
4. **OBLIGATOIRE** : présenter la leçon et ses sources, attendre validation
5. Écrire `DOSSIER_LECONS/<id>.md`, puis INDEX (cf. skill lesson-doc § Règles leçon > Index)

### Mode UPDATE

Pour une techno entière (tableau des leçons outdated, cadrage multi-leçons, création ou fusion de leçons, audits) : `/update-lesson`.

1. Lire la leçon et sa `last_version` dans INDEX
2. Recherches (cf. skill lesson-doc § Règles leçon > Recherches, UPDATE) entre `last_version` et la version actuelle ; avec `--concepts`, cibler ces concepts à la version actuelle, même si la leçon est à jour (enrichissement)
3. **OBLIGATOIRE** : présenter chaque changement avec son chapitre de destination et sa source, attendre validation. Un changement canonique dans une autre leçon devient un renvoi bref ; un changement sans leçon d'accueil est signalé, pas rédigé (relève de `/update-lesson`)
4. Appliquer les changements validés par `Edit` ciblés : renuméroter si un chapitre est inséré, corriger les mentions de version devenues fausses
5. Mettre à jour INDEX (cf. skill lesson-doc § Règles leçon > Index)

## Règles

### TodoWrite

- **DEBUT** : créer les étapes du mode
- **PROGRESSION** : marquer `completed` IMMÉDIATEMENT après chaque étape
- **INTERDIT** : compacter ou renommer des todos

### Interactions user

- **Validation AVANT écriture** : ne jamais écrire sans feedback aux points **OBLIGATOIRE**
- **Sources visibles** : chaque fait présenté à la validation porte sa source (cf. skill lesson-doc § Règles leçon > Recherches, Traçabilité des sources)
