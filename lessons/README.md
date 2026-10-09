# Lessons

Base de leçons de programmation pour développeurs mid/senior, générées et maintenues via Agent IA.
Chaque leçon est une fiche de révision dense : concepts clés, pièges, dépréciations, blocs de code. Pas de tutoriel pas à pas, mais de la substance directement exploitable en entretien ou en production.

## Structure

```
.claude/
├── skills/lesson-doc/    # Référence : structure, conventions et règles des leçons (templates, exemples)
├── skills/prof/          # Skill actionnable : rédaction ou mise à jour d'une leçon
├── agents/lesson/        # Sub-agents (writer, auditor, coherence-auditor)
└── commands/             # Commandes orchestrées (/create-lesson, /update-lesson)

lessons/
├── index-example.yaml    # Format attendu de l'index (à copier en index.yaml)
├── {techno}/
│   ├── {lecon}.md
│   └── {sous-techno}/    # Ex : python/fastapi/, imbriquée dans l'index sous sa techno parente
└── ...

plans/
├── template-create-plan.md       # Template d'un plan pédagogique (création)
├── template-update-plan.md       # Template du plan de mise à jour produit par /update-lesson
├── {techno}-plan-exemple.md      # Exemples de plans de création (next, redis)
└── {techno}-update-<v>-exemple.md  # Exemples de plans de mise à jour (pydanticai, redis)
```

## Démarrage

Cloner le repo, ouvrir dans Claude Code. Les leçons, les plans et l'index restent dans ce dépôt privé : seule la partie outillage est publiée (cf. § Partage). Chaque utilisateur de l'outillage crée les siens.

Copier le fichier d'amorce pour créer l'index local :

```bash
cp lessons/index-example.yaml lessons/index.yaml
```

---

## Créer des leçons

### Workflow A : plan complet + `/create-lesson` (recommandé pour une nouvelle techno)

**1. Rédiger un plan pédagogique**

S'appuyer sur `plans/template-create-plan.md` et les exemples existants. Le plan définit toutes les leçons d'une techno : découpage, ordre, concepts par leçon, points clés pour le skill.

```
plans/redis-plan.md
plans/nextjs-plan.md
...
```

**2. Lancer la commande `/create-lesson`**

```bash
/create-lesson --plan=plans/redis-plan.md
```

Options disponibles :

| Option | Description |
|--------|-------------|
| `--plan=<chemin>` | Plan pédagogique à utiliser (obligatoire) |
| `--lessons=<ids>` | Leçons spécifiques à générer (ex : `fondamentaux,hashes`) |
| `--skip-audit` | Désactive les audits individuels et inter-leçons |

La commande orchestre automatiquement :
- **Phase 1** : rédaction de toutes les leçons en parallèle (agents `lesson/writer`)
- **Phase 2** : audit individuel de chaque leçon (agents `lesson/auditor`)
- **Phase 3** : audit de cohérence inter-leçons (agent `lesson/coherence-auditor`)
- **Phase 4** : consolidation de `lessons/index.yaml`
- Validation utilisateur entre chaque phase

---

### Workflow B : skill `prof` directement (leçon par leçon)

Pour créer une leçon isolée sans plan préalable :

```bash
/prof --techno=python --lecon="Générateurs & Itérateurs" --concepts="yield,send,throw,close,itertools,generator expression,yield from"
```

Le skill effectue ses propres recherches, présente la structure proposée, attend validation, puis écrit le fichier et met à jour l'index.

Arguments :

| Argument | Description |
|----------|-------------|
| `--techno` | Technologie cible (ex : `python`, `nestjs`) |
| `--lecon` | Titre de la leçon |
| `--concepts` | Concepts à couvrir, séparés par des virgules |

---

## Mettre à jour des leçons

### Workflow A : `/update-lesson` (recommandé pour une techno)

```bash
/update-lesson --techno=fastapi
```

| Option | Description |
|--------|-------------|
| `--techno=<slug\|toutes>` | Techno ou sous-techno de l'index, ou `toutes` pour l'inventaire des technos outdated (obligatoire) |
| `--lessons=<ids>` | Restreindre à certaines leçons |
| `--concepts=<liste>` | Concepts à cibler ; avec `--lessons`, enrichit même une leçon à jour |
| `--skip-audit` | Désactive les audits individuels et inter-leçons |

La commande orchestre :
- **Phase 0** : tableau des leçons outdated (version de la leçon vs stable actuelle)
- **Phase 1** : recherche des changements, chacun tracé à une source officielle
- **Phase 2** : cadrage dans `plans/<techno>-update-<version>.md` (modifier, créer, fusionner, supprimer, bump seul). Un simple bump saute directement à l'index
- **Phases 3 et 4** : writers en parallèle (modifications ciblées), audits individuels et de cohérence
- **Phase 5** : consolidation de `lessons/index.yaml`
- Validation utilisateur entre chaque phase

### Workflow B : skill `prof` directement (leçon par leçon)

Le skill `prof` détecte si la leçon existe déjà dans l'index et bascule en mode UPDATE : une leçon à la fois, sans audit.

```bash
# Mettre à jour une leçon spécifique
/prof --techno=nestjs --lecon="Guards & Authentication"

# Enrichir une leçon, même à jour, sur des concepts précis
/prof --techno=redis --lecon="Streams" --concepts="XAUTOCLAIM,consumer groups"
```

Le mode UPDATE cherche les changements entre la `last_version` de la leçon et la version actuelle, présente chacun avec son chapitre de destination et sa source, et attend validation avant de modifier quoi que ce soit.

---

## L'index (`lessons/index.yaml`)

L'index référence toutes les leçons existantes. Il est maintenu automatiquement par le skill `prof` et les commandes `/create-lesson` et `/update-lesson`.

```yaml
python:
  notion_id: "..."          # optionnel — ID page Notion parente
  last_updated: "2026-04-11"
  lessons:
    - id: generateurs-iterateurs
      file: lessons/python/generateurs-iterateurs.md
      concepts: [yield, send, throw, itertools, generator expression]
      last_version: "3.13"
      last_updated: "2026-04-11"
```

Voir `lessons/index-example.yaml` pour le format complet.

---

## Les agents

Utilisés automatiquement par `/create-lesson` et `/update-lesson`, jamais invoqués directement.

| Agent | Rôle |
|-------|------|
| `lesson/writer` | Rédige une leçon à partir du plan, ou applique les changements ciblés d'un plan de mise à jour |
| `lesson/auditor` | Audite une leçon (format, exactitude technique, cohérence avec le plan) |
| `lesson/coherence-auditor` | Audite la cohérence globale de toutes les leçons d'une techno (doublons, couverture, renvois) |

---

## Partage

Les skills, les commandes et les agents de ce depot sont publies dans [claude-toolbox](https://github.com/thibaud57/claude-toolbox), sous `lessons/`. La publication se fait toute seule au merge d'une PR sur ce depot : les lecons, les plans et l'index restent prives, seule la partie outillage part.
