# Settings

Vérifié contre Just 1.58.0 le 2026-09-06 (manuel et changelog). Un setting vaut pour tout le module : un sous-module `mod` redéclare les siens.

| Setting | Depuis | Rôle | Piège | Décision du skill |
|---------|--------|------|-------|-------------------|
| `minimum-version := "X.Y.Z"` | 1.55.0 | Erreur explicite si le `just` installé est plus ancien | Doit précéder toute fonctionnalité gardée ; sur un `just` antérieur à 1.55 la ligne elle-même est une erreur de parsing, l'échec reste net | Première ligne, `"1.58.0"` |
| `dotenv-load` | ancien | Charge `.env` s'il existe et exporte ses variables avant chaque recette | Par module, jamais par recette. Une apostrophe seule dans un commentaire de **fin de ligne** du `.env` ouvre une chaîne : le fichier entier est refusé, donc toutes les recettes. En tête de ligne, aucun risque | Toujours |
| `dotenv-required` | 1.28.0 | Erreur si `.env` absent | Bloque toutes les recettes, `check` compris : le hook SessionStart teste le fichier avant `just check` | Si un service passe sa connexion par `.env` |
| `dotenv-override` | 1.41.0 | Le `.env` prime sur les variables déjà exportées | Ne charge pas un second fichier : ne résout pas le besoin d'un `.env.<scope>` | Écarté, `[script]` couvre le besoin |
| `dotenv-filename`, `dotenv-path` | 1.16.0 | Nom ou chemin dotenv différent ; `filename` est cherché en remontant les dossiers parents, `path` est relatif au cwd | `dotenv-path` échoue si le fichier manque | Écartés, un seul `.env` à la racine |
| `dotenv-command` | 1.54.0 | Charge la sortie d'une commande comme fichier d'environnement | Module racine seulement (fix 1.57.0) | Écarté (secrets via un vault) |
| `default-list` | 1.52.0 | `just` sans argument liste les recettes | Par module | Toujours, remplace la recette `default: @just --list` |
| `ignore-comments` | ancien, restreint en 1.56.0 | Une ligne `#` dans le corps d'une recette shell n'est ni passée au shell ni affichée | Sans effet sur les recettes `[script]` ni shebang, où l'interpréteur gère ses commentaires | Toujours |
| `shell := ["bash", "-cu"]` | ancien | Exécute chaque ligne de recette et les backticks, sur tous les OS | Une ligne = un sous-shell : `cd` et `source` ne persistent pas d'une ligne à l'autre | Toujours ; deux shells selon l'OS → `[unix]` et `[windows]` sur deux `set shell` (attributs sur `set` depuis 1.56.0) |
| `windows-shell`, `windows-powershell` | dépréciés 1.56.0 | Shell propre à Windows | Aucun avertissement à l'exécution | Ne plus écrire, migrer vers `set shell` |
| `script-interpreter := ["bash", "-eu"]` | 1.33.0 | Interpréteur des recettes `[script]` (défaut `sh -eu`) | Indépendant de `set shell` | Dès qu'une recette porte `[script]` |
| `default-script` | 1.52.0 | Toutes les recettes du module en `[script]` | `[shell]` exempte une recette ; perd l'écho ligne à ligne partout | Écarté, `[script]` au cas par cas |
| `quiet` | 1.23.0 | Aucune commande n'est affichée avant exécution | `[no-quiet]` par recette pour réactiver ; les recettes `[script]` sont déjà silencieuses | Écarté : l'écho aide à lire un run, `check` garde ses `@` |
| `working-directory`, `no-cd` | 1.33.0, 1.51.0 | Répertoire d'exécution de tout le module | Sans effet sur la recherche dotenv ni sur `shell()` | Écartés, `[working-directory]` par recette est plus lisible |
| `positional-arguments` | ancien | `$1`, `$2`, `$@` dans les recettes shell | Casse PowerShell sauf pwsh 7.4 | Écarté, `{{ ARGS }}` d'un paramètre variadique suffit |
| `indentation` | 1.56.0 | Indentation de `--fmt` et `--dump` (défaut quatre espaces) | Format non garanti stable entre versions | Écarté, le défaut convient |
| `unstable`, `lists` | 1.31.0, 1.53.0 (instable) | Fonctionnalités instables, valeurs liste | `which()` et `[arg(min, max)]` exigent `lists` | Écartés tant qu'instables |
| `export` | ancien | Exporte toutes les variables Just comme variables d'environnement | Non exporté vers les backticks du même scope | Écarté, `dotenv-load` exporte déjà ce qui doit l'être |
| `fallback` | stable 1.11.0 | Cherche un justfile parent si la recette n'existe pas localement | S'arrête au premier justfile sans `fallback` | Écarté, la racine du projet est connue |
| `allow-duplicate-recipes`, `allow-duplicate-variables` | ancien, 1.27.0 | Autorise les redéfinitions au lieu d'une erreur | Piège documenté avec les imports | Écartés, une erreur de compilation vaut mieux |
| `guards`, `lazy` | 1.47.0 | Sigil `?` en tête de ligne ; variables évaluées seulement si utilisées | Sans `guards`, `?` est du texte | Écartés, aucun besoin rencontré |
| `tempdir` | 1.7.0 | Répertoire des fichiers temporaires des recettes `[script]` et shebang | Précédence CLI > setting > `XDG_RUNTIME_DIR` > défaut OS | Écarté, cas de niche (système de fichiers en lecture seule) |
| `no-exit-message` | 1.39.0 | Supprime les messages d'erreur de recette pour tout le module | `[exit-message]` réactive sur une recette | Écarté, `[no-exit-message]` par recette si besoin |
