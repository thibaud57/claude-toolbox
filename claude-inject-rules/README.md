# claude-inject-rules

Hook `PreToolUse` pour Claude Code qui injecte les rules `.claude/rules/**/*.md` au moment où l'IA **écrit** un fichier, et pas seulement quand elle le lit.

## Le problème

Claude Code permet de placer des conventions dans `.claude/rules/`, chaque fichier portant un frontmatter YAML qui liste les fichiers concernés :

```yaml
---
paths:
  - "src/**/*.service.ts"
---
... Contenu de la rule
```

Le mécanisme natif n'injecte cette rule que sur une **lecture** de fichier. Sur un `Write`, un `Edit` ou un `MultiEdit`, rien n'est injecté. Autrement dit, les conventions de création, celles qui comptent le plus, ne s'appliquent jamais.

C'est l'issue [anthropics/claude-code#23478](https://github.com/anthropics/claude-code/issues/23478), ouverte le 5 février 2026 et fermée en `not planned` : le comportement ne sera pas corrigé.

Ce hook comble le trou.

## Installation

Prérequis : [uv](https://docs.astral.sh/uv/). Le script déclare ses dépendances en PEP 723, `uv` installe `pyyaml` tout seul à l'exécution.

Copier le script au niveau **user**, dans `~/.claude/`, pour qu'il s'applique à tous vos projets :

```bash
mkdir -p ~/.claude/hooks/PreToolUse
cp .claude/hooks/PreToolUse/inject_rules.py ~/.claude/hooks/PreToolUse/
```

Puis l'enregistrer dans `~/.claude/settings.json` :

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run --script ~/.claude/hooks/PreToolUse/inject_rules.py"
          }
        ]
      }
    ]
  }
}
```

Le hook peut aussi être déclaré au niveau projet, dans le `.claude/settings.json` du dépôt. C'est le seul emplacement partageable : il se commit, donc toute l'équipe bénéficie de l'injection sans installation individuelle.

## Ce que fait le hook

À chaque `Write`, `Edit` ou `MultiEdit`, il cherche les rules dont le pattern correspond au fichier visé et injecte leur contenu dans le contexte via `additionalContext`.

### Déduplication par session

Des rules nombreuses et volumineuses réinjectées à chaque fichier touché coûteraient très cher en tokens. Un cache sur disque, indexé par `session_id`, garantit qu'une rule donnée n'est injectée qu'**une fois par session**, ce qui reproduit le comportement du mécanisme natif sur `Read`.

Le cache vit dans `~/.claude/cache/.inject-rules-cache/<session_id>.json`, avec une durée de vie de 24 heures et un nettoyage opportuniste des sessions expirées.

### Prise en charge des monorepos

Les rules appartiennent à leur paquet, pas au dossier depuis lequel Claude Code est lancé. Le hook remonte du fichier édité jusqu'au répertoire de travail et collecte chaque dossier portant un `.claude/rules/`.

L'injection va du plus général au plus spécifique, pour qu'une rule de paquet précise une rule de racine. Les patterns de chaque racine sont matchés contre le chemin du fichier **relatif à cette racine** : `src/**/*.service.ts` dans `packages/api/.claude/rules/` vise bien le `src/` de `packages/api`, quel que soit le répertoire courant.

La clé de cache est qualifiée par racine, sans quoi deux rules homonymes dans deux paquets se masqueraient mutuellement.

### Matching des patterns

Les globs sont compilés en expressions régulières, avec la sémantique attendue :

| Motif | Sens |
|---|---|
| `**/` | zéro ou plusieurs segments |
| `*` | ne traverse jamais un `/` |
| `?` | un caractère, hors `/` |
| `{a,b}` | accolades expansées, comme le mécanisme natif |

Un pattern sans `/` vise le nom de fichier à n'importe quelle profondeur, comme dans un `.gitignore`. Un pattern contenant un `/` est ancré à la racine de ses propres rules. La casse est ignorée sous Windows.

Les deux clés `paths:` et `globs:` sont acceptées. Une rule sans l'une ni l'autre est ignorée.

### Convention fail-open

Toute erreur se solde par une sortie silencieuse en code 0, sans rien injecter.

Le hook signale donc une réussite alors qu'il a échoué, et c'est délibéré. L'écriture ne serait de toute façon pas bloquée, seul un code de sortie 2 interrompt un `PreToolUse`, mais un code d'erreur ferait remonter une alerte à chaque fichier touché. Un outil de confort qui pollue la sortie finit désactivé.

## Débogage

```bash
INJECT_RULES_DEBUG=1
```

Trace le déroulement sur `stderr` : racines retenues, chemin relatif calculé, rules matchées et par quel pattern, rules déjà injectées dans la session. `stdout` reste réservé au JSON attendu par Claude Code.

En cas d'erreur, la variable affiche aussi la traceback au lieu de l'avaler.

## Note d'encodage

La sortie JSON est produite avec `ensure_ascii=True`. Sous Windows, `stdout` est en `cp1252` et toute rule contenant un emoji lèverait un `UnicodeEncodeError`, avalé par le fail-open, donc aucune injection. Ne pas retirer ce paramètre.

## Licence

MIT
