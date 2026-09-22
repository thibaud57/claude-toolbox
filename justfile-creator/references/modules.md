# Modules et imports

Vérifié contre Just 1.58.0 le 2026-09-06.

## `mod`

`mod api` charge `api/justfile` (ou `api.just`, `api/mod.just`) comme sous-module : `just api dev`, `just api::dev`. Stable depuis 1.31.0.

- **Rien n'est partagé** : « Recipes, aliases, and variables defined in one submodule cannot be used in another, and each module uses its own settings. » Chaque module redéclare `set shell`, `set ignore-comments`, ses variables. Seules les variables d'environnement d'un `.env` chargé par un parent sont visibles dans l'enfant, et `justfile_directory()` pointe toujours vers la racine
- `set default-list` est par module : `just api` liste les recettes du module
- `mod? api` (1.21.0) : module optionnel, les recettes qui en dépendent sont désactivées s'il manque
- Alias de module (1.55.0) : `alias a := api` permet `just a dev`
- `[group]` (1.33.0) et `[doc]` (1.32.0) s'appliquent à un `mod` comme à une recette : le module apparaît dans son groupe de `just --list`
- Les variables d'un sous-module peuvent être surchargées depuis la ligne de commande (1.48.0) : `just api::PORT=9000 dev`

**Décision du skill** : le pattern `-<app>` avec alias globaux `[parallel]` reste le défaut d'un dépôt multi-apps, un seul fichier, un seul jeu de settings, `just --list` complet. `mod` se justifie quand chaque app a besoin de ses propres settings (un `dotenv-path` ou un `shell` différents) ou de son propre justfile maintenu par une autre équipe.

## `import`

`import 'common.just'` fusionne le fichier dans l'espace de noms courant : mêmes settings, variables et recettes accessibles directement, insensible à l'ordre. Stable depuis 1.18.0, `import?` pour un fichier optionnel.

- Piège documenté et assumé comme bug permanent : l'ordre de résolution des doublons entre imports de même profondeur est contre-intuitif
- Usage : un socle de recettes partagé entre plusieurs justfiles indépendants (`_common.just`), pas une découpe par app

## Justfile en markdown

Depuis 1.53.0, `just --justfile README.md` exécute les blocs de code `just` non indentés d'un markdown, détection par nom depuis 1.57.0. Le format n'est pas couvert par la garantie de compatibilité. Documentation exécutable, pas un Justfile de projet : écarté.

## Justfile global

`just -g` (1.27.0) cherche un justfile personnel dans `~/.config/just/`. Hors périmètre d'un Justfile de projet : écarté.
