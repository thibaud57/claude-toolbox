# Lessons

Base de leçons de programmation pour développeurs mid/senior, générées et maintenues via Agent IA.
Chaque leçon est une fiche de révision dense : concepts clés, pièges, dépréciations, blocs de code. Pas de tutoriel pas à pas, mais de la substance directement exploitable en entretien ou en production.

## Structure

```
.claude/
├── skills/prof/          # Skill de rédaction/mise à jour de leçons
├── agents/lesson/        # Sub-agents (writer, auditor, coherence-auditor)
└── commands/             # Commandes orchestrées (/create-lesson)

lessons/
├── index-example.yaml    # Format attendu de l'index (à copier en index.yaml)
├── {techno}/             # Créé localement — gitignored
│   └── {lecon}.md
└── ...

plans/
├── template-plan.md      # Template pour créer un nouveau plan pédagogique
├── {techno}-plan.md      # Plan d'une techno (exemples inclus)
└── ...
```

## Démarrage

Cloner le repo, ouvrir dans Claude Code. Les leçons (`lessons/*/`) et l'index (`lessons/index.yaml`) sont gitignorés : chaque utilisateur crée les siens.

Copier le fichier d'amorce pour créer l'index local :

```bash
cp lessons/index-example.yaml lessons/index.yaml
```

---

## Créer des leçons

### Workflow A : plan complet + `/create-lesson` (recommandé pour une nouvelle techno)

**1. Rédiger un plan pédagogique**

S'appuyer sur `plans/template-plan.md` et les exemples existants. Le plan définit toutes les leçons d'une techno : découpage, ordre, concepts par leçon, points clés pour le skill.

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

Le skill `prof` détecte automatiquement si une leçon existe déjà dans l'index et bascule en mode UPDATE.

```bash
# Mettre à jour toutes les leçons d'une techno
/prof --techno=angular

# Mettre à jour une leçon spécifique
/prof --techno=nestjs --lecon="Guards & Authentication"

# Cibler des concepts précis dans la mise à jour
/prof --techno=redis --lecon="Streams" --concepts="XAUTOCLAIM,consumer groups"
```

Le mode UPDATE compare la `last_version` de chaque leçon dans l'index avec la version actuelle de la techno, présente un tableau des leçons outdated, et attend validation avant de modifier quoi que ce soit.

---

## L'index (`lessons/index.yaml`)

L'index référence toutes les leçons existantes. Il est maintenu automatiquement par le skill `prof` et la commande `/create-lesson`.

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

Utilisés automatiquement par `/create-lesson`, jamais invoqués directement.

| Agent | Rôle |
|-------|------|
| `lesson/writer` | Rédige une leçon à partir du plan |
| `lesson/auditor` | Audite une leçon (format, exactitude technique, cohérence avec le plan) |
| `lesson/coherence-auditor` | Audite la cohérence globale de toutes les leçons d'une techno (doublons, couverture, renvois) |
