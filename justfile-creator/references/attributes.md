# Attributs de recette

Vérifié contre Just 1.58.0 le 2026-09-06. Un attribut se place sur la ligne au-dessus de la recette, après son commentaire de description ; `just --fmt` trie les attributs empilés par ordre alphabétique (`[confirm]` avant `[group]` avant `[script]` avant `[working-directory]`).

| Attribut | Depuis | Rôle | Piège | Décision du skill |
|----------|--------|------|-------|-------------------|
| `[group('nom')]` | 1.27.0 (recette), 1.33.0 (module) | Regroupe dans `just --list` et `--groups` | Plusieurs `[group]` empilables | Toutes les recettes : `dev`, `quality`, `infra`, `db`, `setup` |
| `[windows]`, `[unix]`, `[linux]`, `[macos]`, `[openbsd]`, `[freebsd]`, `[netbsd]`, `[dragonfly]`, `[android]` | 1.8.0 (les quatre premiers), 1.38.0 à 1.50.0 (les autres) ; sur tout item du fichier depuis 1.56.0 | Active l'item selon l'OS | Deux recettes du même nom, une par OS ; sur `set`, seulement depuis 1.56.0 | `stop` et toute commande qui diffère par OS |
| `[confirm]`, `[confirm('message')]` | 1.17.0, 1.23.0 (expression : 1.49.0) | Demande confirmation ; `--yes` la court-circuite en CI | Un outil qui a sa propre confirmation interactive entre en conflit : la désactiver (`--force`) | `db-reset`, `db-test-reset` |
| `[parallel]` | 1.42.0 | Dépendances exécutées en parallèle, la recette attend leur fin ; `--jobs N` borne | Sorties entrelacées sans préfixe ; comportement non documenté pour des processus qui ne se terminent jamais | Alias `lint`, `typecheck`, `test`, `build`, `install` en multi-apps ; jamais `dev` |
| `[working-directory('dir')]` | 1.38.0 (expression : 1.51.0) | Toutes les lignes s'exécutent dans `dir` | Sans effet sur la recherche dotenv ni sur `shell()` | Recettes d'un sous-dossier, à la place de `cd dir &&` répété |
| `[script]`, `[script('cmd')]` | 1.44.0 stable (1.32.0 instable) | Le corps entier passe en un seul processus à `script-interpreter`, ou à `cmd` | Ignore `set shell` et `set ignore-comments` ; silencieux par défaut ; sous Windows évite cygpath, plus robuste qu'un shebang | Sourcing d'un `.env.<scope>`, logique multi-lignes |
| `[shell]` | 1.52.0 | Recette shell classique malgré `set default-script` | — | Écarté avec `default-script` |
| `[default]` | 1.43.0 | Recette exécutée par `just` sans argument | Prime sur « première recette du fichier » | Écarté, `set default-list` liste au lieu d'exécuter |
| `[private]` | 1.9.0 (recette), 1.10.0 (alias), 1.35.0 (variable) | Masquée de `--list` sans préfixe `_` | Pas documenté pour un module entier | Recettes utilitaires internes, si le nom `_x` gêne |
| `[doc('texte')]` | 1.27.0 (recette), 1.32.0 (module) | Remplace le commentaire de description dans `--list` ; `[doc]` vide le supprime | — | Écarté, le commentaire au-dessus de la recette suffit |
| `[no-cd]` | 1.9.0 | Exécution depuis le répertoire d'invocation | Sans effet sur dotenv ni `shell()` | Recette qui opère sur le cwd de l'utilisateur |
| `[env('NOM', 'valeur')]` | 1.47.0 | Une variable d'environnement pour la recette | Une variable, pas un fichier | Flag ponctuel (`RUST_BACKTRACE`) |
| `[positional-arguments]` | 1.29.0 | `$1`, `$@` pour cette recette | Casse PowerShell sauf pwsh 7.4 | Écarté, `{{ ARGS }}` suffit |
| `[no-exit-message]`, `[exit-message]` | 1.7.0, 1.39.0 | Supprime ou réactive le message Just après l'échec d'une commande | — | Wrapper CLI (`git *args:`) |
| `[no-quiet]` | 1.23.0 | Exempte une recette de `set quiet` | — | Écarté avec `set quiet` |
| `[continue]`, `[continue(SIGNALS)]` | 1.54.0 | Continue après un signal si la commande sort proprement | SIGINT seul par défaut | Écarté, aucun processus du projet ne gère Ctrl+C lui-même |
| `[timestamp]`, `[timestamp(FORMAT)]` | 1.58.0 | Horodatage de chaque ligne de la recette | — | Écarté, `just --timestamp` à la demande suffit |
| `[metadata(...)]` | 1.42.0 | Métadonnées lisibles par `--dump --dump-format json` | Sans effet sur l'exécution | Écarté, aucun outillage externe ne lit le dump |
| `[cache]` | 1.54.0, instable, recettes `[script]` seulement | Saute une recette si ses entrées n'ont pas changé | Le manuel le qualifie lui-même de fragile | Écarté tant qu'instable |
| `[arg(NOM, pattern, long, short, help, multiple, min, max)]` | 1.45.0 à 1.56.0 | Validation et options nommées des paramètres, aide via `--usage` | `min` et `max` exigent `set lists`, instable | Écarté, les recettes du projet n'ont pas de paramètres complexes |
| `[extension('.ext')]` | 1.32.0 | Extension du fichier temporaire d'une recette shebang | — | Écarté, cas de niche |

## Sigils de ligne

- `@` : n'affiche pas la commande ; `check` l'emploie sur chaque ligne pour rester muet
- `-` : ignore l'échec de la ligne ; `stop` l'emploie devant `taskkill` ou `pkill`, rien à arrêter n'est pas une erreur
- `?` (1.47.0) : garde, inactif sans `set guards` ; écarté
