# Plan pédagogique : Leçons {Techno}

## Contexte

Création de fiches de révision denses (format skill `prof`) pour développeurs mid/senior, basées sur [source : cours Udemy "..." / documentation officielle / autre], enrichies par des recherches sur les nouveautés [version cible] non couvertes par la source.

**[Résumer le périmètre retenu : ex "Le cours compte X sections, dont seules les sections Y à Z sont retenues."]**

**Principe de regroupement** : [expliquer la logique de fusion/découpage des leçons]

> ℹ️ Date de référence : [AAAA-MM-JJ]. Dernière version stable identifiée : **{Techno} {version}** ([note importante sur la version]).

### Décisions de cadrage validées

- **X leçons** : [décrire la structure générale]
- Chaque leçon = un bloc mental cohérent que le dev doit maîtriser ensemble
- **Fusion [A] + [B] → [C]** : [justification]
- **Séparation [X] / [Y]** : [justification]
- **[Autre décision notable]** : [justification]

### État de l'écosystème *(optionnel — si l'écosystème a beaucoup bougé)*

- **{Techno} {version}** stable, [note technique clé]
- **[Lib/outil déprécié]**, **[Nouvelle recommandation]** = recommandation {année}

### Cartographie cours → leçons *(optionnel — si source = cours structuré)*

| Dossier/section cours | Thème | Leçon cible |
|---|---|---|
| [01. Intro] | [Thème] | [L1 Fondamentaux] |
| [02. ...] | [Thème] | [Leçon cible ou "Fusionné L?"] |

### Contenu coupé ou rétrogradé *(optionnel — si des éléments ont été volontairement exclus)*

| Élément | Décision | Raison |
|---|---|---|
| [Feature / commande] | [Supprimé / Section mineure / Mention brève] | [Raison : niche, obsolète, controversé...] |

---

## Ordre d'exécution recommandé

```
[Groupe 1]
└── 1. slug-lecon-1                    ← [description courte]

[Groupe 2]
├── 2. slug-lecon-2                    ← [description courte]
├── 3. slug-lecon-3                    ← [description courte]
└── 4. slug-lecon-4                    ← [description courte]

[Groupe 3]
└── 5. slug-lecon-5                    ← [description courte]
```

**Pourquoi cet ordre :**
- [Justification de l'ordre général]
- [Dépendance entre groupes/leçons]

---

## Versions cibles *(optionnel — si plusieurs technos ou version non précisée dans le contexte)*

| Techno | `last_version` | Notes |
|--------|----------------|-------|
| `{techno}` | `"{version}"` | [Note] |

Le champ `last_version` doit être écrit **par leçon** dans l'index.

---

## Leçons {Techno} (techno={slug}, last_version="{version}")

### 1. slug-lecon-1

```bash
/prof --techno={slug} --lecon="{Titre Leçon}" --concepts="concept1,concept2,concept3,..."
```

**Points à garder en tête pour le skill :**
- Sources cours : [sections source concernées]
- **[Concept clé 1]** : [précision importante, piège, changement de version]
- **[Concept clé 2]** : [précision importante]
- Use cases : [liste courte des cas d'usage principaux]
- Dépréciations : `[ancienne API]` → `[nouvelle API]` *(si applicable)*

---

### 2. slug-lecon-2

```bash
/prof --techno={slug} --lecon="{Titre Leçon}" --concepts="concept1,concept2,..."
```

**Points à garder en tête pour le skill :**
- Sources cours : [sections source concernées]
- **[Concept clé]** : [précision]

---

## Dépréciations et breaking changes critiques à signaler *(optionnel — si nombreuses dépréciations)*

| Ancien | Nouveau | Leçon impactée |
|--------|---------|----------------|
| `[ancienne API]` | `[nouvelle API] ([version]+)` | `[slug-lecon]` |

---

## Fichiers critiques à consulter avant exécution

- `.claude/skills/prof/SKILL.md` : spec complète du skill `prof` (workflow CREATE, conventions de format, règles de recherche)
- `.claude/skills/prof/templates/lesson.md` : template de structure d'une leçon
- `lessons/index.yaml` : index global (à enrichir avec techno `{slug}`)
- `lessons/{slug}/` : dossier destination des [X] fichiers `<id>.md` (à créer)

## Vérification du plan (end-to-end)

1. **Structure fichiers** : `lessons/{slug}/` doit contenir [X] fichiers `.md` en kebab-case ([liste des slugs])
2. **Index YAML** : `lessons/index.yaml` doit contenir une nouvelle entrée `{slug}:` avec [X] leçons, chacune avec `id`, `file`, `concepts`, `last_version: "{version}"`, `last_updated`
3. **Ordre recommandé de création** : L1 → L[X] dans l'ordre (progression pédagogique)
4. **Sondage qualité** : relire [les leçons les plus denses ou les plus fusionnées] pour vérifier cohérence et équilibre
5. **Cohérence version** : chaque mention de [technologie/version clé] doit être cohérente entre toutes les leçons

## Notes opérationnelles

- Les listes de `--concepts` **cadrent** le skill, pas d'exhaustivité. Le skill `prof` effectue ses propres recherches et peut ajouter des concepts manquants essentiels identifiés lors des recherches
- Le skill `prof` demande **validation utilisateur AVANT** d'écrire chaque leçon (règle OBLIGATOIRE dans SKILL.md), sauf si lancé via `/create-lesson` qui override cette validation
