# Plan de mise à jour : {Techno} {last_version} → {version actuelle}

## Contexte

Mise à jour des leçons `{techno}` (format skill `lesson-doc`) entre la version des leçons et la version stable actuelle. Produit et validé en Phase 2 de `/update-lesson`, puis lu par `lesson/writer`, `lesson/auditor` et `lesson/coherence-auditor`.

> ℹ️ Date de référence : [AAAA-MM-JJ]. Version stable identifiée : **{Techno} {major.minor}** ([source]).

## Changements identifiés

Un changement par ligne, chacun tracé à une source officielle consultée (cf. skill lesson-doc § Règles leçon > Recherches, Traçabilité des sources). Un changement `non confirmé` n'est jamais assigné à une leçon.

| # | Changement | Version | Source | Extrait | Statut |
|---|------------|---------|--------|---------|--------|
| 1 | [Description factuelle courte] | [0.137] | [URL] | "[extrait verbatim court]" | confirmé / non confirmé |

## Écartés

Changements confirmés mais sans valeur pour une leçon (cf. skill lesson-doc § Conventions de format > Chapitres, Valeur avant exhaustivité). Aucun n'est assigné à une leçon.

| # | Changement | Raison |
|---|------------|--------|
| [3] | [Description courte] | [niche, défaut sans enjeu, historique, paraphrase de la doc] |

## Décisions de structure

| Leçon | Action | Changements | Justification |
|-------|--------|-------------|---------------|
| `[slug-lecon]` | modifier / créer / fusionner dans `[slug]` / supprimer / bump seul | [#1, #3] | [Pourquoi cette leçon est canonique pour ces changements] |

- **bump seul** : aucun contenu modifié, seule `last_version` change dans l'index
- **supprimer** / **fusionner** : le fichier source n'est retiré qu'après validation explicite, son contenu utile étant d'abord reporté dans la leçon cible

---

## Ordre d'exécution recommandé

Ordre complet des leçons de la techno après mise à jour (positionne les leçons créées dans l'index) :

```
1. slug-lecon-existante
2. slug-lecon-creee                    ← nouvelle
3. slug-lecon-existante
```

---

## Versions cibles

| Techno | Section index | Dossier | Leçons | `last_version` | Notes |
|--------|---------------|---------|--------|----------------|-------|
| `{slug}` | `{slug}` ou `{parent}.{slug}` | `lessons/{slug}/` ou `lessons/{parent}/{slug}/` | toutes, ou `[slug-lecon, ...]` | `"{major.minor}"` | [Note] |

Une ligne par version suivie : une leçon qui suit un outil distinct (cf. skill lesson-doc § Règles leçon > Index) a sa propre ligne, qui la cite dans la colonne Leçons, et garde le cycle de cet outil.

---

## Leçons {Techno} (techno={slug}, last_version="{major.minor}")

Seules les leçons à modifier ou à créer ont une section. La source d'une fusion n'en a pas : la section de sa cible liste les chapitres à reporter.

### 1. slug-lecon-modifiee

**Action** : modifier

**Changements à appliquer :**
- [#1] Chapitre [N. Titre] : [ce qu'il faut ajouter, corriger ou retirer, précisément]
- [#3] Nouveau chapitre après [N. Titre] : [contenu attendu] → renuméroter les suivants
- [Fusion] Reporter depuis `[slug-source]` : chapitres [N. Titre, ...] → [chapitre de destination]

**Points à garder en tête pour le skill :**
- [Piège, renvoi vers la leçon canonique, formulation de version durable]

---

### 2. slug-lecon-creee

**Action** : créer

```bash
/prof --techno={slug} --lecon="{Titre Leçon}" --concepts="concept1,concept2,..."
```

**Points à garder en tête pour le skill :**
- **[Concept clé]** : [précision, piège, changement de version] ([#2])

---

## Matrice concept → leçon canonique

Concepts touchés par la mise à jour et partagés entre plusieurs leçons :

| Concept | Canonique dans | Mentionné aussi dans |
|---------|----------------|----------------------|
| `[concept]` | `[slug-lecon]` | `[slug-lecon]` (renvoi) ou "(nulle part ailleurs)" |

---

## Dépréciations et breaking changes critiques à signaler

| Ancien | Nouveau | Version | Leçon impactée |
|--------|---------|---------|----------------|
| `[ancienne API ou comportement]` | `[nouvelle API ou comportement]` | [0.143] | `[slug-lecon]` |
