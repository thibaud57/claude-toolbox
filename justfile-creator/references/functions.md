# Fonctions

Vérifié contre Just 1.58.0 le 2026-09-06. Une fonction s'évalue à l'évaluation de l'assignation ou de l'interpolation `{{ }}`, jamais différée à l'exécution de la ligne.

| Fonction | Depuis | Rôle | Piège | Décision du skill |
|----------|--------|------|-------|-------------------|
| `env("NOM")`, `env("NOM", "défaut")` | 1.15.0 | Variable d'environnement, avec ou sans défaut | Sans défaut, halt si absente | `PORT := env("PORT", "8000")` |
| `os_family()`, `os()`, `arch()` | ancien | `"windows"` ou `"unix"`, OS et architecture | — | Chemin de venv : `if os_family() == "windows" { ".venv/Scripts" } else { ".venv/bin" }` |
| `justfile()`, `justfile_directory()` | ancien | Chemin du justfile racine, même depuis un sous-module | — | Chemin absolu vers une zone |
| `invocation_directory()`, `invocation_directory_native()` | ancien, 1.13.0 | Répertoire d'où `just` a été lancé | La première est traduite par cygpath sous Windows | Recette qui opère sur le cwd de l'utilisateur |
| `source_file()`, `source_directory()` | 1.27.0 | Fichier source courant, différent de `justfile()` dans un import | — | Justfile multi-fichiers avec imports |
| `module_file()`, `module_directory()`, `module_path()` | 1.28.0, 1.28.0, 1.50.0 | Chemin et nom du module courant | — | Justfile multi-apps avec `mod` |
| `path_exists("chemin")` | ancien | `"true"` ou `"false"` | Chaîne, pas booléen | Précondition dans une expression `if` |
| `shell("cmd", args…)` | 1.27.0 | Exécute une commande avec arguments positionnels, dans `set shell` | `cmd` doit référencer `$1` | Remplace un backtick qui a besoin d'arguments |
| `require("exe")` | 1.39.0 | Chemin d'un exécutable, halt sinon | Halt de tout le justfile, pas de la recette : `check` deviendrait inutilisable | Écarté dans `check`, qui teste par `command -v` |
| `which("exe")` | 1.39.0 | Chemin ou liste vide | Exige `set lists`, instable en 1.58 | Écarté tant qu'instable |
| `num_cpus()`, `num_jobs()` | 1.15.0, 1.56.0 | Cœurs logiques, valeur de `--jobs` | — | Paramétrer un outil parallèle |
| `recipe_name()`, `is_dependency()` | 1.53.0, 1.29.0 | Nom de la recette courante, appelée en dépendance ou non | Chaînes | Écartés, aucune recette générique |
| `just_executable()`, `just_pid()`, `just_version()` | ancien, 1.23.0, 1.55.0 | Métadonnées du processus `just` | — | Écartés, `set minimum-version` fait le travail |
| `semver_matches("v", "req")` | 1.16.0 | Teste une version contre un requirement semver | Chaînes `"true"` / `"false"` | Écarté, cf. `minimum-version` |
| `datetime("%Y-%m-%d")`, `datetime_utc()` | 1.30.0 | Horodatage formaté (strftime) | — | Nom d'un fichier de sauvegarde |
| `style("error")`, `style("error", "texte")` | 1.37.0, 1.55.0 | Couleur terminal | La forme à un argument doit être suivie de `NORMAL` | Sorties de `check` si on veut de la couleur, non retenu |
| `error("message")`, `assert(cond, "message")` | ancien, 1.27.0 | Halt avec message | — | Précondition explicite d'une recette |
| `read("chemin")` | 1.39.0 | Contenu d'un fichier | Halt si absent | Lire une version dans un fichier |
| `blake3()`, `blake3_file()`, `sha256()`, `sha256_file()`, `uuid()` | 1.25.0, ancien | Hachages et identifiant | — | Écartés, sans usage dans un Justfile de projet |

## Interpolation dans une recette

`{{ VAR }}` est substitué avant que la ligne parte au shell : `{{ PORT }}` dans un `taskkill` ou un `netstat` est du texte, pas une variable shell. Une valeur venue de `.env` se lit par contre en `$VAR`, exportée par `dotenv-load`. Depuis 1.58, `just --fmt` écrit l'interpolation avec des espaces, `{{ VAR }}`.
