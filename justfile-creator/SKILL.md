---
name: justfile-creator
description: Schémas et formats pour générer un Justfile projet, avec recettes just adaptées au stack, gestionnaire de paquets, infra, stratégie de test et type de repo. Utilisé quand un projet a besoin d'un Justfile.
allowed-tools: Read, Write, WebSearch, WebFetch
---

# Skill Justfile-Creator

Référence pour générer un `Justfile` à la racine du projet, adapté au contexte (STACK, PM, INFRA, TEST_STRATEGY, REPO_TYPE).

Version cible : Just 1.58.0, vérifié le 2026-09-06. Le Justfile généré l'impose par `set minimum-version`. Le catalogue des fonctionnalités de Just, avec version, piège et raison de l'avoir retenue ou écartée, vit dans `references/`.

## Structure

```
Justfile
├── Header
│   ├── set minimum-version
│   ├── set dotenv-load
│   ├── set dotenv-required    (optionnel)
│   ├── set default-list
│   ├── set ignore-comments
│   ├── set shell
│   ├── set script-interpreter (optionnel, dès qu'une recette porte [script])
│   └── <VAR> :=               (optionnel)
├── Dev                        (optionnel, absent pour une bibliothèque sans point d'entrée)
│   ├── dev
│   └── stop                   (optionnel)
├── Quality
│   ├── build                  (optionnel)
│   ├── lint
│   ├── format                 (optionnel, si le formateur sait réécrire)
│   ├── typecheck              (optionnel)
│   ├── lint-workflows         (optionnel, si .github/workflows existe)
│   ├── test
│   ├── test-*                 (optionnel)
│   └── audit                  (optionnel, si le PM a une commande de vulnérabilités)
├── Infrastructure             (optionnel)
│   ├── docker-up
│   ├── docker-down
│   └── docker-*               (optionnel, logs…)
├── DB                         (optionnel)
│   ├── db
│   ├── db-migrate
│   ├── db-reset
│   ├── db-*                   (optionnel, outil de l'ORM : studio, seed…)
│   └── db-test*               (optionnel, DB de test séparée)
└── Setup
    ├── install
    ├── setup
    └── check
```

## Documentation officielle

- [Just Manual](https://just.systems/man/en/)
- [Changelog](https://github.com/casey/just/blob/master/CHANGELOG.md)

## Fichiers de référence

| Élément | Template | Exemples |
|---------|----------|---------|
| Justfile | `templates/Justfile` | `examples/fastapi-angular/Justfile`, `examples/go-docker-pg/Justfile` |
| Settings | `references/settings.md` | - |
| Attributs et sigils | `references/attributes.md` | - |
| Fonctions | `references/functions.md` | - |
| Modules et imports | `references/modules.md` | - |
| Ligne de commande | `references/cli.md` | - |

## Conventions de format

- **Placeholders** : `<texte>` pour les champs à remplir, distinct de l'interpolation Just `{{ NOM }}` d'une variable du header
- **Description par recette** : un commentaire court sur la ligne juste au-dessus, avant les attributs — `just` l'affiche dans `just --list`, c'est la doc automatique du projet
- **Commentaire en corps de recette** : uniquement pour un pourquoi non déductible de la ligne qu'il précède (flag imposé par un piège d'outil, ordre obligatoire, seuil justifié), indenté comme la commande
- **Séparateurs de section** `# ── Dev ──` : laisser une ligne vide après, sinon le séparateur devient la description de la recette suivante
- **Booléens en forme canonique** : `set default-list`, `set ignore-comments`, sans `:= true` (ce que produit `just --fmt`)
- **Pas de recette `default`** : `set default-list` fait lister les recettes par `just` seul

## Output

Fichier `Justfile` à la racine du projet.

## Règles

### Sections optionnelles

Recettes et sections marquées `(optionnel)` dans la Structure → omettre si non applicable selon les règles ci-dessous.

### Header

- `set minimum-version := "1.58.0"` : première ligne — message net au lieu d'une erreur de parsing sur un poste en retard
- `set dotenv-load` : toujours, inoffensif sans `.env`
- `set dotenv-required` : **optionnel**, si un service INFRA passe sa connexion par `.env` — bloque toutes les recettes si `.env` manque, `check` compris, d'où le test du fichier par le hook SessionStart avant `just check`
- `set default-list` : toujours
- `set ignore-comments` : toujours — sans lui un commentaire en corps de recette part au shell et s'affiche, `check` cesserait d'être muet et le hook le lirait comme un avertissement
- `set shell := ["bash", "-cu"]` : toujours, tous OS confondus — sans lui Just prend `sh` ; `set windows-shell` est déprécié depuis 1.56 et ne s'écrit plus. Deux shells selon l'OS : `[unix]` et `[windows]` sur deux `set shell` (cf. `references/settings.md`). bash devient un prérequis du projet, à écrire dans son README et son CLAUDE.md, pas dans `check` : sans bash aucune recette ne s'exécute, `check` compris
- `set script-interpreter := ["bash", "-eu"]` : **optionnel**, dès qu'une recette porte `[script]`
- Variables (**optionnel**) : `PORT := env("PORT", "<défaut>")` pour un serveur (omettre si CLI ou mobile), une variable par composant en multi-apps, un chemin binaire OS-dépendant via `if os_family() == "windows" { … } else { … }`. Jamais de variable `DOTENV_<SCOPE>`, cf. § Règles > Override d'env par recette

### Dev

- **`stop`** : inclure si serveur web/API, SPA, app desktop, ou bundler mobile persistant sur un port (Metro d'Expo et React Native, kill par port comme un dev-server web) — omettre si CLI (se termine seule) ou mobile sans bundler local (Flutter, processus géré par le framework). Variantes `[windows]` et `[unix]`, sauf si ARCHITECTURE.md ne déclare qu'un seul OS de développement : une recette sans attribut, l'autre variante serait du code mort
- **Serveur avec `PORT` dans le header** : `[windows]` kill par port, `netstat -ano | awk '/:{{ PORT }} .*LISTENING/ {print $NF}' | sort -u | xargs -r -I{} taskkill //PID {} //T //F` ; `[unix]` kill par motif de commande, `pkill -f "<process>"`. **Kill par nom** sinon (desktop, worker) : `taskkill //IM <process>.exe //T //F` ou `pkill -f "<process>"`. Sigil `-` devant chaque ligne : rien à arrêter n'est pas une erreur. Le `//` est obligatoire depuis Git Bash, MSYS convertirait `/PID` en chemin Windows. PowerShell ne sert que pour retrouver un processus par sa ligne de commande (`Get-CimInstance Win32_Process`), quand ni le port ni le nom ne suffisent
- **CLI** : `dev *ARGS:` et passer `{{ ARGS }}` (ex: `cargo run -- {{ ARGS }}`)
- **Python** : `uv run <script>` si le paquet déclare sa CLI dans `[project.scripts]`, `uv run python -m <paquet>` si le livrable est un binaire PyInstaller construit sur `__main__.py`

### Quality

- **`build`** : omettre si le STACK ne compile ni n'empaquette (Python, PHP, Ruby) — omettre aussi si le build est délégué à une toolchain externe (EAS, Xcode, CI cloud), n'inclure que la part locale. Un package publié sur un registre garde son `build` local (`uv build`, `pnpm pack`, `cargo package`) ; la publication est le rôle du workflow CI déclenché par le tag, jamais d'une recette, un `publish` lancé d'un poste échappe à la CI et au tag
- **`lint` et `format`** : `lint` vérifie sans rien réécrire (`ruff check` + `ruff format --check`, `eslint` + `prettier --check`), c'est ce que la CI appelle. `format` réécrit (`ruff format` + `ruff check --fix`, `prettier --write`) : recette séparée, jamais dans `lint`, et à omettre si le formateur du STACK ne sait que vérifier. Même partage pour un validateur de schéma : `prisma validate` dans `lint`, `prisma format` dans `format`, faute de mode vérification
- **`typecheck`** : inclure si un vérificateur de types existe hors du build (mypy, `tsc --noEmit`) — omettre si le compilateur le fait (Go, Rust)
- **`lint-workflows`** (ou repliée dans `lint` en repo mono-zone) : `actionlint` sur `.github/workflows/*.yml` dès qu'un tel dossier existe, ajoutée à l'alias `lint`. `check` avertit s'il manque (`command -v actionlint`), sans bloquer
- **`audit`** : inclure dès que le PM expose une commande de vulnérabilités sans outil à installer (`uv audit`, `pnpm audit`, `govulncheck` ; `cargo audit` exige `cargo install`, donc non) — seuil et flags identiques à la CI quand PRODUCTION.md documente une politique de dépendances, valeurs par défaut sinon
- **Tests** : nommage depuis TEST_STRATEGY (`test-unit`, `test-integration`, `test-e2e`), `test` enchaîne tout. Un seul type → `test:` directe, sans alias redondant. Multi-apps : `test-<app>` prime, même à type unique
- **Seuil de couverture** : porté par la recette `test` (`--cov-fail-under=<seuil>`), jamais par la config du runner — sur un run ciblé la couverture globale est basse et l'habitude deviendrait de la désactiver. Une recette `coverage` séparée si la CI mesure autrement que `test` (ex: `coverage run -m pytest` puis `coverage report`), pour que le développeur reproduise exactement ce qu'elle fait
- **Env de test isolé** : une recette qui a besoin d'un `.env.<scope>` est une recette `[script]`, cf. § Règles > Override d'env par recette

### Infrastructure

- Inclure si INFRA contient Docker : `docker-up` (`docker compose up -d`) et `docker-down`, plus `docker-logs` si l'image du projet est elle-même dans le compose
- Service sous `profiles:` dans le compose : `docker compose --profile <name> up -d`

### DB

**Périmètre**
- **DB au sens Justfile** = service avec migrations manuelles (Prisma, Alembic, golang-migrate…). Tout autre service stateful (Redis, Kafka, Mongo) relève de `docker-up` seul, avec sa ligne dans `check`
- Migrations automatiques au démarrage (Flyway, Spring Boot) : pas de section DB, `db:` lance seulement le service
- La section DB ne dépend pas de `.env` : une base fichier peut avoir des migrations sans variable d'environnement

**Recettes**
- **`db`** (readiness) : lance les services backing **et** applique les migrations existantes, idempotent — `docker compose up -d --wait <db-service>` puis la migration deploy de l'ORM (ex: `prisma migrate deploy`, `alembic upgrade head`). Sans Docker : la migration seule. C'est cette recette que `setup` appelle, jamais `docker-up`, réservé à la validation d'image
- **`db-migrate`** : création interactive d'une migration (ex: `prisma migrate dev --name <label>`, qui demande un nom sans `--name`), jamais appelée par `setup`
- **`db-reset`** : `[confirm('…')]`, drop et recreate et migrate, **sans seed** — vérifier que la commande recrée bien le schéma, et neutraliser la confirmation propre à l'outil (`--force`) qui entrerait en conflit avec `[confirm]`

**DB de test séparée (optionnel)**
- Inclure si les tests d'intégration tournent sur une base distincte de la dev (Postgres ou MySQL partagés, où le wipe gênerait le dev) — inutile pour une base fichier ou un container éphémère par worker
- Recettes jumelles de celles de la dev, en `[script]` sourçant `.env.test` en première ligne ; `db-test-reset` neutralise le seed automatique si le CLI de l'ORM en a un (`--skip-seed` chez Prisma), les tests créant leurs fixtures

### Setup

- **`setup`** : tout ce qu'il faut pour que le projet tourne, dans l'ordre et sans `[parallel]` — `install`, puis `db` si base, puis la recette de build d'un **artefact croisé** s'il en existe un (binaire déclaré en `externalBin` Tauri, client généré par un ORM, package partagé), puis `db-seed` si le code lit des données au démarrage ou au build. C'est ce que `/setup-dev` lance : la recette doit rendre le projet runnable à elle seule
- **`install`** : commande du PM, ou fetch des dépendances pour un runtime sans phase d'installation (`cargo fetch`, `go mod download`)
- **`check`** : ne modifie rien, n'échoue jamais, chaque ligne préfixée `@` pour ne pas échoer la commande. Pas de `set quiet` global, l'écho reste utile ailleurs
  - **Une ligne de sortie par anomalie seulement**, préfixée du marqueur `⚠️` que le hook SessionStart grep, et portant le correctif (`⚠️ venv absent, lancer just install`). Pas de ligne de confirmation quand tout va bien : la sortie vide est le signal de succès, et c'est elle que le développeur lit
  - Présence d'un outil : `command -v <outil> >/dev/null 2>&1 || echo "⚠️ …"`, jamais `require()` qui ferait échouer tout le justfile (cf. `references/functions.md`)
  - Couvrir chaque prérequis du projet : runtime, dépendances installées, variables requises (`[ -n "${VAR:-}" ]`, jamais `[ -f .env ]` avec `set dotenv-required`, qui a déjà refusé de lancer `check` si le fichier manque), chaque service INFRA (`docker info`, `nc -z localhost <port>`), chaque artefact croisé attendu

### Override d'env par recette

`set dotenv-load` exporte `.env` avant chaque recette, et les settings `dotenv-*` sont par module : Just ne sait pas charger un `.env.<scope>` sur une seule recette. Une variable déjà exportée prime d'ailleurs sur tout `.env.<scope>` que le loader du langage chargerait ensuite, qui l'ignore en silence.

La recette devient donc une recette `[script]` : son corps s'exécute dans un seul `bash -eu`, le sourcing de la première ligne vaut pour les suivantes, là où une recette shell relance un sous-shell à chaque ligne.

```just
set script-interpreter := ["bash", "-eu"]

[script]
test-integration:
    set -a && . ./.env.test && set +a
    <commande>
```

Fichier optionnel : `if [ -f ./.env.test ]; then set -a && . ./.env.test && set +a; fi`. Réserver ce pattern aux recettes qui consomment réellement cet env (`test-integration`, `db-test`), inutile sur `lint`, `typecheck` ou `build`.

### Multi-apps

Plusieurs apps, ou plusieurs zones dans un monolithe (front, sidecar, coquille native), ou un worker séparé : décliner chaque recette en `-<app>` et ajouter un alias global. Si un orchestrateur de monorepo est déjà en place (Turborepo, Nx), les alias lui délèguent (`lint: turbo run lint`) : il connaît le graphe et le cache, le pattern `-<app>` les réimplémenterait à la main.

- **`dev`** : alias avec `&` dans le corps (`just dev-api & just dev-web`), jamais dans les dépendances, qui n'acceptent pas `&`. Pas de `[parallel]` ici : le manuel ne couvre pas des dépendances qui ne se terminent jamais, la propagation du Ctrl+C n'est pas garantie
- **`lint`, `format`, `typecheck`, `test`, `audit`, `build`, `install`** : alias en `[parallel]`. Sortie entrelacée, la ligne finale `error: recipe X failed` nomme la zone fautive, `--jobs N` borne sur un poste modeste. Deux exceptions : un workspace PM (pnpm, npm, yarn) garde un `install` unique à la racine, et `build` reste séquentiel quand une cible en consomme une autre (package partagé avant l'app qui l'importe)
- **`stop`** : `stop-<app>` avec ses variantes OS, alias global ; rien pour une app mobile
- **Sous-dossier** : `[working-directory('<app>')]` sur chaque recette concernée, jamais `cd <app> &&` répété, que le sous-shell par ligne obligerait à écrire partout
- **Multi-PM** : chaque recette `-<app>` utilise le PM de son manifeste (`pnpm install` ici, `uv sync` là) ; la table `Apps & Packages` d'ARCHITECTURE.md (format du skill architecture-doc) donne le PM par app, à défaut le manifeste de chaque dossier
- **Packages partagés** : hors des alias `test` et `build`, sauf s'ils ont les leurs
- **Workers** (Celery, BullMQ) : `dev-<worker>` dans l'alias `dev`, `stop-<worker>` par nom de processus
- **Alternative `mod`** : un justfile par app, sans settings ni variables partagés, à réserver aux apps qui ont besoin de settings différents (cf. `references/modules.md`)

### Commande incertaine

Si une commande n'apparaît ni dans les scripts du manifeste ni dans les standards connus du STACK, la confirmer sur la doc officielle de l'outil pour la version ciblée (flags, effets de bord, confirmation interactive) : WebSearch puis WebFetch.

### Montée de version de Just

Une nouveauté n'entre dans le skill que si elle remplace un contournement ou change une règle, comme l'ont fait `default-list`, `[script]` et `[working-directory]`. Mettre alors à jour la ligne Version cible, le `set minimum-version` du template et la table concernée dans `references/`.
