# justfile-creator

Un skill [Claude Code](https://code.claude.com/docs/en/overview) qui génère un [`Justfile`](https://just.systems/man/en/) adapté aux caractéristiques de ton projet.

Au lieu d'un template figé, le skill lit ton projet (manifestes, fichiers de config, arborescence) et produit des recettes `just` cohérentes avec ta stack, ton gestionnaire de paquets, ton infra, ta stratégie de test et ton type de repo, mono ou multi-apps.

## Ce que ça génère

Un `Justfile` structuré en groupes, pour que `just --list` reste lisible :

- **Dev** : `dev`, `stop`, avec variantes `[windows]` et `[unix]`
- **Quality** : `build`, `lint`, `test`, plus `test-unit`, `test-integration`, `test-e2e` selon la stratégie détectée
- **Infrastructure** : `docker-up`, `docker-down`
- **DB** : `db-migrate`, `db-reset`, `db` qui enchaîne les services et les migrations
- **Setup** : `install`, `setup`, `check`

Les groupes sans objet sont omis : un projet sans base de données n'a pas de section DB. Le skill couvre aussi les cas moins triviaux, le cross-platform Windows et Unix, les monorepos multi-apps, la base de test isolée.

## Installation

Au niveau user, pour générer des Justfiles dans n'importe quel projet :

```bash
cp -r justfile-creator ~/.claude/skills/
```

Au niveau projet, pour ce dépôt uniquement :

```bash
cp -r justfile-creator .claude/skills/
```

> **Pattern conseillé** : garder `justfile-creator` au niveau user. Il sert à *générer* le Justfile, une fois par projet, et reste ainsi disponible partout. Créer ensuite dans chaque projet un ou plusieurs skills dédiés qui *pilotent* les recettes générées, lancer le bon `just`, orchestrer les commandes propres au projet. La génération reste globale, le pilotage reste local.

## Utilisation

Demander simplement à Claude Code :

> Génère-moi un Justfile pour ce projet

ou en précisant le contexte :

> Génère un Justfile pour mon monorepo FastAPI + Angular avec Postgres en Docker

Claude lit le projet, applique les conventions du skill et écrit le `Justfile` à la racine.

## Contenu

| Fichier | Rôle |
|---|---|
| `SKILL.md` | Les conventions et les règles de génération |
| `templates/Justfile` | Squelette de référence |
| `references/` | Référence `just` condensée : attributs, CLI, fonctions, modules, settings |
| `examples/fastapi-angular/Justfile` | Exemple monorepo Python et JavaScript |
| `examples/go-docker-pg/Justfile` | Exemple Go, Docker et Postgres |

## Prérequis

- [Just](https://just.systems/man/en/), pour exécuter les recettes générées
- [Claude Code](https://code.claude.com/docs/en/overview), pour utiliser le skill

## Licence

MIT
