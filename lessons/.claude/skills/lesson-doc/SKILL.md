---
name: lesson-doc
description: Schémas et formats pour les leçons de programmation (fiches de révision denses pour développeurs mid / senior) : structure, conventions de rédaction, règles de recherche et d'index. Utilisé pour rédiger, mettre à jour ou auditer une leçon.
---

# Skill Lesson Doc

Référence pour la structure, les conventions et les règles des leçons de programmation.

## Structure

```
lesson.md
├── # N. Chapitre
│   ├── bullet points
│   ├── bloc(s) de code (optionnel)
│   └── ## Sous-section (optionnel)
│       ├── bullet points
│       ├── bloc(s) de code (optionnel)
│       └── ### Sous-sous-section (optionnel)
│           ├── bullet points
│           └── bloc(s) de code (optionnel)
├── # N+1. Chapitre
│   └── ...
```

## Fichiers de référence

| Élément | Template | Exemples |
|---------|----------|----------|
| Leçon | `templates/lesson.md` | `examples/routing-navigation.md`, `examples/configuration.md`, `examples/spring-data-jpa.md` |
| Index des leçons | `lessons/index-example.yaml` | `lessons/index.yaml` |

## Conventions de nommage

- Fichiers et dossiers : kebab-case, minuscules, sans accents, sans espaces
- Leçons : `{sujet}.md` (ex : `lazy-loading.md`, `guards-authentication.md`)
- **Sous-techno** : techno rattachée à une techno parente (ex : `fastapi` sous `python`). Dossier `lessons/<techno>/<sous-techno>/`, section imbriquée sous la techno parente dans l'index, mêmes champs qu'une techno. `--techno` désigne l'une ou l'autre : la position dans `lessons/index.yaml` fait foi. Une nouvelle techno n'est créée en sous-techno que sur validation du user
- Images : dans le dossier de la (sous-)techno, sous `assets/`, nommées `{lecon}-{description}.png` (ex : `kustomize-diagram.png`)
- Dossier `assets/` : créer uniquement si la techno a des images (pas de dossier vide)

## Conventions de format

### Sections optionnelles

Si une section marquée `(optionnel)` n'est pas nécessaire → omettre la section entière.
- Blocs de code : omettre entièrement si aucun exemple n'est nécessaire — le nombre est libre selon le besoin
- `##` Sous-section : omettre si le chapitre reste lisible à plat
- `###` Sous-sous-section : omettre si la sous-section ne nécessite pas de subdivision

### Chapitres

**Titre de chapitre**
- Format : `# N. Titre` (numérotation séquentielle à partir de 1)
- **Pas de backticks dans les titres** : même pour les termes techniques, jamais de backticks dans `#`, `##`, `###`. Exemple correct : `# 5. State local & Events` — incorrect : ``# 5. State local avec `useState` & Events``. Le contenu du chapitre rétablit ensuite les backticks normalement.
- Pour lister deux termes côte à côte : `&` au lieu de `et` (ex : BufferedReader & Scanner, State local & Events)

**Contenu de chapitre**
- 7 bullet points par chapitre est un seuil d'alerte — au-delà, vérifier que chaque bullet apporte quelque chose de distinct (notion différente, piège, cas d'usage). Si c'est le cas, le dépassement est justifié. Si des bullets couvrent la même notion avec des variations mineures, regrouper.
- Chapitre < 3 bullet points : envisager de fusionner avec un chapitre adjacent si pertinent (sauf exception justifiée)
- **Positionnement des bullets** : tous les bullets d'un niveau (`#`, `##`, `###`) sont regroupés en bloc continu AVANT les blocs de code de ce même niveau. Ne jamais intercaler un bullet isolé entre deux blocs de code. Si un bullet est lié à un bloc de code spécifique qui n'est pas le premier, créer une `##` ou `###` sous-section pour regrouper ce bullet avec son bloc
- **Terme technique** : tout artefact qu'on écrit dans le code (classe, méthode, annotation, propriété de config, flag CLI...). Toujours en `backticks` dans le contenu, jamais traduit.
- **Label conceptuel** : terme qui décrit un comportement, un pattern ou une catégorie sans être un artefact de code (getter, Upcasting, First-level cache...) — pas de backticks.
- Bold (`**`) pour emphase contextuelle ou comme label structurant en début de bullet — jamais comme substitut de titre (`##`/`###`)
- Pattern label obligatoire : quand un bullet commence par un mot-clé suivi de ` : `, le mot-clé est en bold. Terme technique → `- **`terme`** : description`. Label conceptuel → `- **Label** : description`
- Ajouter une notion manquante seulement si un dev mid / senior resterait bloqué sans elle
- Pas d'explications que tout développeur connaît (ex : "un service centralise la logique", "une boucle répète des instructions", ...), sauf si c'est le thème de la leçon — les pièges, comportements non-évidents et le "pourquoi" des règles restent toujours attendus
- **Valeur avant exhaustivité** : une leçon garde ce qui change la façon d'écrire ou de déboguer le code (pièges, choix de conception, comportements non évidents, ruptures récentes) et laisse à la doc officielle les cas de niche (provider marginal, paramètre rarement utile), les valeurs par défaut sans enjeu, les listes exhaustives (paramètres, providers, flags, commandes CLI), l'historique de versions et la paraphrase de la doc. Test : un dev mid / senior perdrait-il quelque chose si la ligne disparaissait ?
- Intégrer les pièges et bonnes pratiques dans les chapitres concernés en priorité. Un chapitre BP transversal en fin de leçon est acceptable s'il combine des concepts de plusieurs chapitres
- Un chapitre de règles générales transversales (setup, fondamentaux, conventions) peut être placé **en début de leçon** si plusieurs chapitres en dépendent et que les règles ne trouvent pas leur place ailleurs
- Liberté totale de réorganiser les éléments selon l'ordre pédagogique le plus pertinent

### Blocs de code

- 20 lignes par bloc est un seuil d'alerte — au-delà, vérifier que chaque ligne apporte quelque chose de distinct (comportement différent, cas d'usage, pattern). Si c'est le cas, le dépassement est justifié. Si des lignes répètent la même structure avec des variations mineures, simplifier.
- Séparer en plusieurs blocs de code si les extraits proviennent de fichiers ou contextes distincts (ex : un bloc pour le repository, un bloc pour le service) — exception : si les fichiers forment un pattern bidirectionnel ou relationnel qui nécessite de voir toutes les parties ensemble pour comprendre (ex : dépendance circulaire entre deux services, ou séquence définition → enregistrement → injection d'un même concept)
- Vérifier que chaque exemple est syntaxiquement valide
- Pas d'imports dans les blocs de code — retirer sans exception
- Ajouter un commentaire quand le comportement ne se déduit pas visuellement : piège, effet de bord, valeur de retour non-évidente (ex : `list.remove(0)  // par index, pas par valeur`, `map.put("k", v)  // retourne l'ancienne valeur ou null`)
- Pas de commentaires qui répètent les bullets ou expliquent ce que le code montre déjà clairement (ex : `// Incrémente de 1` sur `count++`)
- Toujours conserver : structurants/comparatifs (`// Avant :` / `// Après :`, `// ✅` / `// ❌`, `// Cold :` / `// Hot :`), labels de contexte — valides même si techniquement incorrects pour le langage (ex : `// angular.json` en tête d'un bloc `json`, `// Dans un composant` dans un bloc `typescript`)
- Pas de code répétitif — ne pas montrer 3 fois la même structure avec des variations mineures
- Pas de titre "Exemples de Code" — juste le bloc directement
- Langage déduit du contexte, obligatoirement un identifiant valide Notion : `abap`, `arduino`, `bash`, `basic`, `c`, `clojure`, `coffeescript`, `c++`, `c#`, `css`, `dart`, `diff`, `docker`, `elixir`, `elm`, `erlang`, `flow`, `fortran`, `f#`, `gherkin`, `glsl`, `go`, `graphql`, `groovy`, `haskell`, `html`, `java`, `javascript`, `json`, `julia`, `kotlin`, `latex`, `less`, `lisp`, `livescript`, `lua`, `makefile`, `markdown`, `markup`, `matlab`, `mermaid`, `nix`, `objective-c`, `ocaml`, `pascal`, `perl`, `php`, `plain text`, `powershell`, `prolog`, `protobuf`, `python`, `r`, `reason`, `ruby`, `rust`, `sass`, `scala`, `scheme`, `scss`, `shell`, `sql`, `swift`, `typescript`, `vb.net`, `verilog`, `vhdl`, `visual basic`, `webassembly`, `xml`, `yaml`
- Utiliser uniquement un langage de cette liste. En cas de doute, utiliser `plain text`
- Indiquer la version de la techno ciblée dans les exemples quand c'est pertinent (ex : Python 3.13, Angular 19), jamais l'historique de ses versions

### Hiérarchie des titres

- `#` : chapitres (toujours présent)
- `##` : sous-sections (optionnel — si chapitre dense ou si les items forment 2+ thèmes sémantiquement distincts)
- `###` : sous-sous-sections (optionnel — si subdivision supplémentaire)
- Au-delà de `###` : utiliser du bold (`**Sous-titre**`) en début de paragraphe
- Pas de `---` entre sections

### Tables (optionnel)

- Pour comparaisons de caractéristiques, complexités Big O, checklists, ...
- Préférer une table à une liste quand plusieurs propriétés sont comparées en parallèle

### Avertissements et notes

- Dépréciation : `> ⚠️ Dépréciée depuis X.Y : <ancien> → utiliser <nouveau>`
- Changement de comportement qui casse du code : `> ⚠️ Depuis X.Y : <ancien> → <nouveau>` (`X.Y.Z` pour un patch)
- Feature stable : aucun marqueur de version, le contenu décrit l'état actuel
- API supprimée : ne pas la documenter, la retirer si présente dans une version précédente de la leçon
- Avertissement critique ou piège : `> ⚠️ <note courte>`
- Info contextuelle ou conseil : `> ℹ️ <contexte>`

### Anti-redondance (CRITIQUE)

- Un concept = expliqué une seule fois dans toute la leçon
- Éviter les chapitres récapitulatifs qui répètent du contenu déjà montré (une synthèse comparative ou un tableau récapitulatif peut avoir de la valeur)
- Pas de variantes d'une même approche sauf si essentiel
- Pas de séparation artificielle de concepts liés

## Règles leçon

### Recherches

- Toujours AVANT de rédiger ; autant de sources que nécessaire ; date courante du système, jamais d'année en dur
- **Traçabilité des sources** : tout fait technique retenu (API, comportement, version, dépréciation) vient d'une source officielle effectivement consultée : doc, changelog, release notes, guide de migration, code source, PR. Une déduction ou un résumé tiers n'est pas une source. Ce qui n'a pas pu être confirmé est signalé à l'utilisateur, jamais rédigé comme un fait. La preuve (URL + extrait) est présentée au point de validation, jamais dans la leçon, dont le style reste inchangé
- **Granularité des versions** : toute version écrite dans l'index ou comparée est au format `major.minor` (ex : `"3.14"`) ; un patch ne rend pas une leçon outdated. Majeur seul si la techno ne publie que des majeures (ex : Java `"26"`). Dans le contenu d'une leçon, une rupture ou un fix liés à un patch gardent leur numéro complet (ex : « depuis 0.140.13 », cf. § Conventions de format > Avertissements et notes)
- **Ce que suit une leçon** : la techno, ou un outil distinct à cycle propre quand il est au cœur du contenu (ex : Hibernate, Maven, Pydantic dans une techno FastAPI, React dans une techno Next.js) ; objet si plusieurs composants : `{framework: "7.0", boot: "4.0"}` ; `null` si indéterminable. Le déduire du sujet et de la `last_version` existante, demander en cas de doute
- **CREATE** : objectif version stable actuelle, syntaxe recommandée, dépréciations récentes ; sources prioritaires doc officielle et changelog ; `last_version` = version stable de ce que la leçon suit
- **UPDATE** : objectif syntaxe recommandée aujourd'hui, breaking changes depuis `last_version`, dépréciations et suppressions ; sources prioritaires doc officielle, guide de migration, changelog. Outdated si `last_version` < version actuelle de ce que la leçon suit ; `null` → toujours outdated, recherche sans borne inférieure ; objet → outdated si un composant l'est. `last_version` à écrire = version actuelle identifiée, sinon conserver l'existante

### Index

- `id` (kebab-case du titre) et `file` (`lessons/<techno>/<id>.md` ou `lessons/<techno>/<sous-techno>/<id>.md`) : CREATE uniquement, dans la section de la (sous-)techno, jamais dupliquée à la racine
- `concepts` : termes techniques clés du contenu actuel, mis à jour dès que le `.md` change
- `last_version` : par leçon (cf. § Règles leçon > Recherches). En UPDATE, bumper aussi les leçons examinées mais non modifiées qui suivent la même version ; une leçon non examinée garde la sienne
- `last_updated` : date du jour, sur la leçon si son `.md` change, sur la (sous-)techno dès qu'une leçon est touchée
