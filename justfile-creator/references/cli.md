# Ligne de commande

Vérifié contre Just 1.58.0 le 2026-09-06. Ce qui sert à un développeur ou à la CI sur un Justfile de projet.

| Commande | Depuis | Rôle | Décision du skill |
|----------|--------|------|-------------------|
| `just` | — | Avec `set default-list`, liste les recettes | Point d'entrée du README |
| `just --list`, `--list --unsorted`, `--groups` | ancien, 1.30.0 | Liste par groupe, dans l'ordre du fichier, ou les groupes seuls ; `--list <module>` pour un sous-module | — |
| `just --list --group dev` | 1.47.0 | Filtre `--list` sur un groupe ; `--group` seul est refusé | Confort |
| `just --dry-run <recette>` | ancien | Affiche les commandes sans les exécuter, commentaires de corps exclus avec `ignore-comments` | Vérifier une recette avant de la lancer, tester le Justfile |
| `just --yes <recette>` | ancien | Confirme tous les `[confirm]` | CI, script non interactif |
| `just --jobs N` | 1.56.0 | Borne le parallélisme des `[parallel]` | Poste modeste |
| `just --time` | 1.49.0 | Durée d'exécution de chaque recette | Chasse aux recettes lentes |
| `just --timestamp`, `--timestamp-format` | 1.28.0 | Horodate chaque ligne | Debug d'un run long, sans modifier le Justfile |
| `just --evaluate [VAR]` | ancien (format : 1.49.0) | Valeur des variables du justfile | Debug d'une variable |
| `just --set VAR valeur`, `just VAR=valeur` | ancien | Surcharge une variable, chemins `mod::VAR` acceptés | Un port différent le temps d'un run |
| `just --fmt`, `--fmt --check` | stable 1.50.0 | Formate le Justfile en forme canonique (`{{ VAR }}`, attributs triés, booléens sans `:= true`), ou vérifie | Local seulement : le format n'est pas garanti stable entre versions, un gate CI casserait à une montée de `just` |
| `just --dump`, `--dump --dump-format json` | ancien | Justfile normalisé, ou en JSON avec les `[metadata]` | Outillage externe, non retenu |
| `just --usage <recette>` | 1.46.0 | Aide détaillée d'une recette à paramètres `[arg]` | Non retenu avec `[arg]` |
| `just --completions bash` | ancien | Script de complétion du shell | Onboarding développeur |
| `just --choose` | ancien | Sélecteur interactif (fzf) | Alternative à `default-list`, non retenue |
| `just --clean` | 1.54.0 | Vide le cache `[cache]` | Non retenu avec `[cache]` |
| `just --one` | 1.36.0 | Interdit d'invoquer plusieurs recettes en une commande | Non retenu, l'usage multi-recettes est voulu |

## En CI

`extractions/setup-just` installe la dernière version publiée, aucune version à épingler tant que le gate ne dépend pas du format. Les workflows appellent les recettes (`just lint`, `just typecheck`, `just test`), jamais les commandes qu'elles contiennent : une divergence entre local et CI est la première source de « ça passe chez moi ».
