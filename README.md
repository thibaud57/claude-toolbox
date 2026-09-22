# claude-toolbox

Mes outils [Claude Code](https://code.claude.com/docs/en/overview) partagés, un dossier par projet.

| Dossier | Ce que c'est |
|---|---|
| [lessons/](lessons/) | Skill `prof`, commande `/create-lesson` et agents `lesson/*` : leçons de programmation denses pour développeurs mid/senior, générées et auditées par Claude Code. Voir son [README](lessons/README.md) |
| [justfile-creator/](justfile-creator/) | Skill qui génère un `Justfile` adapté au projet (stack, gestionnaire de paquets, infra, tests, mono ou multi-apps). Tout est dans son [SKILL.md](justfile-creator/SKILL.md) |
| [claude-inject-rules/](claude-inject-rules/) | Hook `PreToolUse` qui injecte les rules `.claude/rules/**/*.md` au moment où Claude écrit un fichier, pas seulement quand il le lit. Voir son [README](claude-inject-rules/README.md) |

## Installation

- **prof** : cloner le repo, ouvrir `lessons/` dans Claude Code, suivre son README
- **justfile-creator** : `cp -r justfile-creator ~/.claude/skills/` pour l'avoir dans tous les projets, ou dans le `.claude/skills/` d'un projet
- **inject-rules** : copier le script et le déclarer dans `settings.json`, détail dans son README

## Licence

MIT
