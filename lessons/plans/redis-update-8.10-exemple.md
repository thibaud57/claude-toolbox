# Plan de mise à jour : Redis 8.6 → 8.10

## Contexte

Mise à jour des leçons `redis` (format skill `lesson-doc`) entre la version des leçons et la version stable actuelle. Produit et validé en Phase 2 de `/update-lesson`, puis lu par `lesson/writer`, `lesson/auditor` et `lesson/coherence-auditor`.

> ℹ️ Date de référence : 2026-10-08. Version stable identifiée : **Redis Open Source 8.10** ([version management](https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/) : "Redis 8.10 | Standard | GA" ; [GitHub releases](https://github.com/redis/redis/releases) : "8.10.2", badge "Latest").

Release notes de référence :
- 8.8 : https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.8-release-notes/ ("Redis Open Source 8.8.0 (May 2026)")
- 8.10 : https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.10-release-notes/ ("Redis Open Source 8.10.0 (July 2026)")
- What's new : https://redis.io/docs/latest/develop/whats-new/8-8/ et https://redis.io/docs/latest/develop/whats-new/8-10/

Aucun breaking change ni suppression de commande entre 8.6 et 8.10. Seule suppression : le rate limiter GCRA ("Remove GCRA rate limiter", #15191), retiré entre 8.8-M03 et 8.8-RC1, jamais publié en GA ni présent dans les leçons.

## Changements identifiés

| # | Changement | Version | Source | Extrait | Statut |
|---|------------|---------|--------|---------|--------|
| 1 | Nouveau type de données Array (18 commandes `AR*`) | 8.8 | https://redis.io/docs/latest/develop/data-types/arrays/ | "sparse, index-addressable structures mapping integer indexes to string values" ; "18 commands in this group" | confirmé |
| 2 | `INCREX` : incrément borné avec expiration, window counter rate limiter | 8.8 | https://redis.io/docs/latest/commands/increx/ | "INCREX key [BYFLOAT increment \| BYINT increment] [LBOUND lowerbound] [UBOUND upperbound] [SATURATE] [EX ... \| PERSIST] [ENX]" | confirmé |
| 3 | Subkey notifications pour les fields de hash (flags `S`/`T`/`I`/`V`) | 8.8 | https://redis.io/docs/latest/develop/pubsub/subkeyspace-notifications/ | "Subkey notifications, added in Redis 8.8, extend Redis's existing keyspace notification system" | confirmé |
| 4 | Flag keyspace `a` (Array commands), alias `A` = `g$lshztdxea` | 8.8 | https://redis.io/docs/latest/develop/pubsub/keyspace-notifications/ | "a     Array commands" ; "A     Alias for \"g$lshztdxea\"" | confirmé |
| 5 | `XNACK` : relâcher des messages pending sans les acquitter (modes `SILENT`/`FAIL`/`FATAL`) | 8.8 | https://redis.io/docs/latest/commands/xnack/ | "XNACK key group <SILENT \| FAIL \| FATAL> IDS numids id [id ...] [RETRYCOUNT count] [FORCE]" | confirmé |
| 6 | `XREADGROUP ... CLAIM` : messages NACKés prioritaires | 8.8 | https://redis.io/docs/latest/commands/xreadgroup/ | "Among pending entries, messages released via XNACK are prioritized and reported first" | confirmé |
| 7 | `AGGREGATE COUNT` sur `ZUNION`/`ZINTER`/`ZUNIONSTORE`/`ZINTERSTORE` | 8.8 | https://redis.io/docs/latest/commands/zunionstore/ | "When AGGREGATE COUNT is specified, the original element scores are ignored entirely" | confirmé |
| 8 | `FT.HYBRID` : argument `SHARD_K_RATIO` dans la clause `KNN` | 8.8 | https://redis.io/docs/latest/commands/ft.hybrid/ | "SHARD_K_RATIO controls the number of results each shard retrieves relative to the requested top_k in cluster setups" | confirmé |
| 9 | `FT.PROFILE` supporte `FT.HYBRID` | 8.8 | release notes 8.8 | "FT.PROFILE HYBRID: profiling support for FT.HYBRID" | confirmé |
| 10 | Reducer `COLLECT` (in-group sorting) pour `FT.AGGREGATE` : déroule les documents groupés après `GROUPBY` et les trie dans chaque groupe | 8.8 | what's new 8.8 ; https://redis.io/docs/latest/develop/ai/search-and-query/advanced-concepts/aggregations/ | "New in-group sorting reducer - COLLECT for FT.AGGREGATE" ; "The COLLECT reducer was introduced in version 8.8.0" | confirmé |
| 11 | `slowlog-entry-max-argc` / `slowlog-entry-max-string-len` | 8.8 | release notes 8.8 | "slowlog-entry-max-argc: maximum number of command arguments kept in a slowlog entry" | confirmé |
| 12 | Compact hashes (encoding à templates) + `HIMPORT` + configs de conversion | 8.10 | https://redis.io/docs/latest/develop/data-types/hashes/ ; https://redis.io/docs/latest/commands/himport/ | "a new hash encoding that reduces memory usage by storing hash field names just once for keys that share a schema" | confirmé |
| 13 | `LMOVEM` / `BLMOVEM` : déplacement multi-éléments entre lists | 8.10 | https://redis.io/docs/latest/commands/lmovem/ | "LMOVEM source destination <LEFT \| RIGHT> <LEFT \| RIGHT> [<COUNT count \| EXACTLY exactly> <OBO \| BULK>]" | confirmé |
| 14 | `SUNIONCARD` (`APPROX`, `LIMIT`) | 8.10 | https://redis.io/docs/latest/commands/sunioncard/ | "SUNIONCARD numkeys key [key ...] [APPROX] [LIMIT limit]" | confirmé |
| 15 | `SDIFFCARD` (`LIMIT`) | 8.10 | https://redis.io/docs/latest/commands/sdiffcard/ | "SDIFFCARD numkeys key [key ...] [LIMIT limit]" | confirmé |
| 16 | Famille `BACKUP` (MP-AOF) + restauration `preload-file` | 8.10 | https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/ | "Since Redis 8.10.0, the BACKUP command family produces a self-contained, restorable backup without stopping writes" | confirmé |
| 17 | `XREAD` / `XREADGROUP` : `MAXCOUNT` et `MAXSIZE` | 8.10 | https://redis.io/docs/latest/commands/xreadgroup/ | "the MAXCOUNT and MAXSIZE options cap the cumulative reply across all streams named in a single command" | confirmé |
| 18 | `search-on-timeout` : `FAIL` / `RETURN` / `RETURN_STRICT`, timeout strict | 8.10 | release notes 8.10 | "RETURN_STRICT (new) — return best-effort partial results while enforcing the timeout through the post-processing (result) pipeline" | confirmé |
| 19 | `FT.HYBRID` supporte `EXPLAINSCORE` | 8.10 | release notes 8.10 | "FT.HYBRID supports EXPLAINSCORE, exposing the fusion method (RRF or LINEAR)" | confirmé |
| 20 | `COLLECT` : exécution séparée remote / local en cluster (détail interne, même reducer que #10) | 8.10 | release notes 8.10 | "FT.AGGREGATE - new COLLECT reducer: separate remote and local reducer invocations" | confirmé (non rédigé : interne) |
| 21 | `FT.ALIASLIST` | 8.10 | release notes 8.10 | "New command: FT.ALIASLIST - get all aliases for the index" | confirmé |
| 22 | `SLOWLOG GET` : nombre total d'arguments dans la réponse | 8.10 | release notes 8.10 | "SLOWLOG GET - new reply argument: total argument count" | confirmé |
| 23 | Authentification server-to-server par certificat TLS pair | 8.10 | release notes 8.10 | "TLS peer certificate-based server-to-server authentication" | confirmé |
| 24 | `redis-cli --latency-percentiles` ; reshard/rebalance via atomic slot migration | 8.10 | release notes 8.10 | "Adds --latency-percentiles <p1,p2,...> to --latency / --latency-history" | confirmé |
| 25 | Modèle de release Standard / Extended | doc | https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/ | "Extended releases ... receive security updates and critical bug fixes for 5 years after their release date" | confirmé |
| 26 | Valeur retournée par `TYPE` pour un array | 8.8 | https://redis.io/docs/latest/commands/type/ | La page ne liste que "string, list, set, zset, hash, stream, and vectorset" | non confirmé |
| 27 | Syntaxe complète de `BLMOVEM` (timeout avant le bloc how-many ; avec `COUNT` bloque tant que la source est vide, avec `EXACTLY` jusqu'à n éléments ; ne bloque pas dans `MULTI`/Lua) | 8.10 | https://redis.io/docs/latest/commands/blmovem/ | "BLMOVEM source destination <LEFT \| RIGHT> <LEFT \| RIGHT> timeout [<COUNT count \| EXACTLY exactly> <OBO \| BULK>]" | confirmé |
| 28 | Compatibilité Redis Software / Cloud de `HIMPORT` | 8.10 | page HIMPORT sans table de compat | : | non confirmé |
| 29 | Directive de config de l'authentification TLS server-to-server | 8.10 | release notes sans détail | : | non confirmé |
| 30 | `ARLASTITEMS` lit depuis le curseur d'insertion (résultat différent après `ARSEEK` ou sur un array rempli par `ARSET`) | 8.8 | https://raw.githubusercontent.com/redis/redis/8.8/src/t_array.c (`arlastitemsCommand`) | "Returns the most recent positions from the current insert anchor" | confirmé |
| 31 | node-redis 6.0 : RESP3 protocole par défaut, Node.js 20 minimum ; dernière minor 6.2 | client | https://github.com/redis/node-redis/releases | "RESP3 is now the default protocol" ; "Node.js 20 is now the minimum supported version" | confirmé |
| 32 | redis-py 8.0 : RESP3 par défaut sur le fil, formes de réponse Python compatibles RESP2 conservées ; dernière minor 8.1 (juillet 2026), Python 3.10+ | client | https://pypi.org/project/redis/ | "clients use RESP3 on the wire by default" | confirmé |
| 33 | Jedis 8.0 : RESP3 par défaut (auto-négociation, fallback RESP2) ; dernière minor 8.0 | client | https://github.com/redis/jedis/releases | "Switch to RESP3 as default protocol version" | confirmé |
| 34 | Dernières minors : Lettuce 7.8, go-redis 9.23, StackExchange.Redis 3.3 | client | https://github.com/redis/lettuce/releases ; https://github.com/redis/go-redis/releases ; https://github.com/StackExchange/StackExchange.Redis/releases | "7.8.0.RELEASE" (Latest) ; "9.23.0" (latest) ; "3.3.1" (Latest) | confirmé |
| 35 | Protocole par défaut de StackExchange.Redis 3.x | client | releases sans mention | : | non confirmé |
| 36 | ioredis 6.0 (juillet 2026) : RESP3 par défaut, Node.js 20+, `protocol: 2` pour rester en RESP2 ; maintenance best-effort inchangée | client | https://github.com/redis/ioredis/releases/tag/v6.0.0 | "ioredis now requires Node.js 20 or newer and uses RESP3 by default" | confirmé |
| 37 | Lettuce utilise RESP3 par défaut depuis la 6 (pas la 7) ; go-redis v9 RESP3 par défaut | client | https://redis.io/docs/latest/operate/rs/references/compatibility/resp/ | "Lettuce versions 6 and later use RESP3 by default" | confirmé |
| 38 | Subkey notifications des hashes : le flag de classe `h` est requis en plus de S/T/I/V (l'exemple `ST` seul de la doc ne produit rien) | 8.8 | https://raw.githubusercontent.com/redis/redis/8.10/src/notify.c ; https://raw.githubusercontent.com/redis/redis/8.10/tests/unit/pubsub.tcl | `if (!(server.notify_keyspace_events & type)) return;` avant le bloc subkey ; tests en `Sh`, `Th`, `STIVh` | confirmé (code source, contredit l'exemple de la doc) |

## Écartés

Changements confirmés mais sans valeur pour une leçon (cf. skill lesson-doc § Conventions de format > Chapitres, Valeur avant exhaustivité). Aucun n'est assigné à une leçon.

| # | Changement | Raison |
|---|------------|--------|
| 9 | `FT.PROFILE` supporte `FT.HYBRID` | Niche : même commande de profiling, argument de plus, paraphrase de la doc |
| 11 | `slowlog-entry-max-argc` / `slowlog-entry-max-string-len` | Défaut sans enjeu : deux paramètres de troncature d'entrée, rarement ajustés |
| 20 | `COLLECT` : exécution séparée remote / local en cluster | Détail interne, même reducer que #10 |
| 21 | `FT.ALIASLIST` | Liste exhaustive de commandes : aucune leçon ne traite les alias d'index |
| 22 | `SLOWLOG GET` : nombre total d'arguments dans la réponse | Détail de format de réponse sans effet sur la façon d'écrire ou de déboguer |
| 24 | `redis-cli --latency-percentiles` ; reshard/rebalance via atomic slot migration | Liste de flags CLI : aucune leçon ne traite `redis-cli --latency` / `--cluster` |

## Décisions de structure

| Leçon | Action | Changements | Justification |
|-------|--------|-------------|---------------|
| `fondamentaux` | modifier | #1, #25, #31 à #34, #36, #37 | Leçon d'entrée : version stable, cycle de release, liste des types natifs |
| `strings-bitmaps-ttl` | modifier | #2, #4 | Canonique pour les commandes numériques, le rate limiting fixed-window et les keyspace notifications |
| `hashes` | modifier | #3, #12, #38 | Canonique pour le field TTL, `hexpired` et l'encoding des hashes |
| `lists` | modifier | #13 | Canonique pour `LMOVE` / `BLMOVE` |
| `arrays` | créer | #1, #4 | Nouveau type avec 18 commandes, bloc mental cohérent qu'aucune leçon existante ne porte |
| `sets-hyperloglog` | modifier | #14, #15 | Canonique pour `SINTERCARD` et la cardinalité sans matérialiser |
| `sorted-sets-geospatial` | modifier | #7 | Canonique pour `ZUNION` / `AGGREGATE` |
| `streams-pubsub` | modifier | #5, #6, #17 | Canonique pour consumer groups, PEL, `XCLAIM`, DLQ |
| `modelisation-relationnelle` | modifier | #1 | Table de sélection du data type |
| `pipelining-transactions-locks` | bump seul | : | Aucun changement 8.8 / 8.10 ne la concerne |
| `scripting-lua-functions` | modifier | #2 | Le rate limiter Lua est couvert nativement par `INCREX` : renvoi `> ℹ️` |
| `redis-query-engine` | modifier | #8, #10, #18, #19 | Canonique pour `FT.HYBRID`, `FT.AGGREGATE` |
| `production-redis` | modifier | #12 (renvoi), #16, #23 | Canonique pour persistence, TLS, tuning des encodings |

- **bump seul** : aucun contenu modifié, seule `last_version` change dans l'index
- Insertion de `arrays` en L5 : les renvois « Lx » des autres leçons sont renumérotés (L5 → L6 ... L12 → L13)

---

## Ordre d'exécution recommandé

```
1. fondamentaux
2. strings-bitmaps-ttl
3. hashes
4. lists
5. arrays                              ← nouvelle
6. sets-hyperloglog
7. sorted-sets-geospatial
8. streams-pubsub
9. modelisation-relationnelle
10. pipelining-transactions-locks
11. scripting-lua-functions
12. redis-query-engine
13. production-redis
```

---

## Versions cibles

| Techno | Section index | Dossier | Leçons | `last_version` | Notes |
|--------|---------------|---------|--------|----------------|-------|
| `redis` | `redis` | `lessons/redis/` | toutes | `"8.10"` | Query Engine, JSON et Vector Sets sont intégrés au binaire Redis Open Source : même cycle de release |

---

## Leçons Redis (techno=redis, last_version="8.10")

### 1. fondamentaux

**Action** : modifier

**Changements à appliquer :**
- [#25] Chapitre version : version stable 8.10 (GA juillet 2026), modèle Standard / Extended
- [#1] Liste des types natifs et bullet `TYPE` : ajouter Array (8.8+), renvoi L5
- [#31 à #34] Chapitre 3 (support client RESP3) et chapitre clients (table + exemples de code) : node-redis 6 et redis-py 8 et Jedis 8 passent RESP3 par défaut ; versions de la table alignées (node-redis 6.2, redis-py 8.1, Jedis 8.0, Lettuce 7.8, go-redis v9.23, StackExchange.Redis 3.3) ; commentaires « RESP3 opt-in » des blocs de code corrigés

**Points à garder en tête pour le skill :**
- Ne pas donner de valeur `TYPE` pour un array (#26 non confirmé)
- Ne pas affirmer le protocole par défaut de StackExchange.Redis 3.x (#35 non confirmé)
- redis-py 8 : RESP3 sur le fil mais formes de réponse Python RESP2-compatibles par défaut (piège)
- Formulation de version durable (datée)

---

### 2. strings-bitmaps-ttl

**Action** : modifier

**Changements à appliquer :**
- [#2] Chapitre commandes numériques : nouvelle section `INCREX` (options, retour `[valeur, incrément appliqué]`, hors bornes vs `SATURATE`, piège `BYINT` sur un float, `ENX`)
- [#2] Pattern rate limiting fixed-window : réécrit autour de `INCREX ... UBOUND n EX s ENX`
- [#4] Chapitre keyspace notifications : flag `a`, alias `A` corrigé, renvoi subkey notifications (L3)

**Points à garder en tête pour le skill :**
- `INCREX` expliqué uniquement ici ; L11 renvoie
- `INCREX` non supporté sur Redis Software / Cloud

---

### 3. hashes

**Action** : modifier

**Changements à appliquer :**
- [#3] Chapitre field TTL : retirer la « limitation connue, roadmap 8.8 » sur `hexpired`, ajouter une section subkey notifications (flags, canaux, payload length-prefixed, exemple)
- [#12] Nouveau chapitre compact hashes après l'encoding : principe, bon / mauvais fit, `HIMPORT`, conversion automatique, métriques → renuméroter les suivants

**Points à garder en tête pour le skill :**
- Un hash avec field expiration n'est pas converti en compact hash
- Ne pas affirmer la compatibilité Redis Software / Cloud de `HIMPORT` (#28)

---

### 4. lists

**Action** : modifier

**Changements à appliquer :**
- [#13] Section `LMOVE` : `LMOVEM` / `BLMOVEM` (`COUNT` / `EXACTLY`, `OBO` / `BULK`), piège source = destination
- [#1] Comparaison list vs stream : renvoi vers L5 pour l'accès par index

**Points à garder en tête pour le skill :**
- [#27] Syntaxe complète de `BLMOVEM` (timeout avant le bloc how-many) et comportement bloquant selon `COUNT` / `EXACTLY`

---

### 5. arrays

**Action** : créer

```bash
/prof --techno=redis --lecon="Arrays" --concepts="ARSET,ARGET,ARMSET,ARMGET,ARLEN,ARCOUNT,ARGETRANGE,ARSCAN,ARDEL,ARDELRANGE,ARINSERT,ARNEXT,ARSEEK,ARRING,ARLASTITEMS,AROP,ARGREP,ARINFO,array-slice-size,array vs list/hash/stream"
```

**Points à garder en tête pour le skill :**
- **Modèle** : sparse, index 0 à 2^64−1, encoding sliced-array, `ARLEN` vs `ARCOUNT` (#1)
- **Limites** : `ARGETRANGE` plafonné à 1 000 000 éléments par appel (#1)
- **Compatibilité** : `AR*` non supporté sur Redis Software / Cloud (#1)
- **Notifications** : flag `a` détaillé en L2 (#4)
- **ARLASTITEMS** : lit depuis le curseur d'insertion, résultat différent après `ARSEEK` ou sur un array rempli par `ARSET` (#30)

---

### 6. sets-hyperloglog

**Action** : modifier

**Changements à appliquer :**
- [#14, #15] Section cardinalité sans matérialiser : `SUNIONCARD` (`APPROX`, `LIMIT`) et `SDIFFCARD` (`LIMIT`)

**Points à garder en tête pour le skill :**
- `SUNIONCARD APPROX` utilise un HLL interne mais garde les sets exacts en mémoire : pas le gain mémoire d'un HLL

---

### 7. sorted-sets-geospatial

**Action** : modifier

**Changements à appliquer :**
- [#7] Chapitre opérations ensemblistes : `AGGREGATE COUNT` (scores ignorés, 1 par set ou weight)

---

### 8. streams-pubsub

**Action** : modifier

**Changements à appliquer :**
- [#5, #6] Chapitre reprise de messages : section `XNACK` (modes, effet sur PEL et delivery counter, priorité dans les claims, différence avec `XACK`, lien DLQ)
- [#17] Chapitres XREAD / XREADGROUP : `MAXCOUNT` / `MAXSIZE`
- Label « Syntaxe Redis 8.6 complète » sur `XADD` : formulation durable

---

### 9. modelisation-relationnelle

**Action** : modifier

**Changements à appliquer :**
- [#1] Table de sélection du data type : ligne `array`

---

### 10. scripting-lua-functions

**Action** : modifier

**Changements à appliquer :**
- [#2] Section rate limiter atomique : `> ℹ️` renvoi vers `INCREX` (L2)

---

### 11. redis-query-engine

**Action** : modifier

**Changements à appliquer :**
- [#8, #19] Section FT.HYBRID : `SHARD_K_RATIO`, `EXPLAINSCORE`
- [#10] Chapitre FT.AGGREGATE : un seul reducer `COLLECT` (8.8+) qui déroule et trie les documents dans chaque groupe
- [#18] Chapitre diagnostic : politique `search-on-timeout`

---

### 12. production-redis

**Action** : modifier

**Changements à appliquer :**
- [#16] Chapitre persistence : famille `BACKUP` et `preload-file`
- [#23] Chapitre TLS : mention courte, sans directive (#29)
- [#12] Tuning des encodings : renvoi compact hashes (L3)
- Checklist : ligne backup

---

## Matrice concept → leçon canonique

| Concept | Canonique dans | Mentionné aussi dans |
|---------|----------------|----------------------|
| `INCREX` | `strings-bitmaps-ttl` | `scripting-lua-functions` (renvoi) |
| Subkey notifications | `hashes` | `strings-bitmaps-ttl`, `arrays` (renvoi) |
| Flag keyspace `a` | `strings-bitmaps-ttl` | `arrays` (renvoi) |
| Array | `arrays` | `fondamentaux`, `lists`, `modelisation-relationnelle` (renvoi) |
| Compact hashes | `hashes` | `production-redis` (renvoi) |
| `XNACK` | `streams-pubsub` | (nulle part ailleurs) |
| `BACKUP` | `production-redis` | (nulle part ailleurs) |

---

## Dépréciations et breaking changes critiques à signaler

| Ancien | Nouveau | Version | Leçon impactée |
|--------|---------|---------|----------------|
| `INCR` + `EXPIRE NX` (ou script Lua) pour un rate limiter fixed-window | `INCREX ... UBOUND n EX s ENX` (recommandé, pas une dépréciation) | 8.8 | `strings-bitmaps-ttl`, `scripting-lua-functions` |
| Backup AOF-only en désactivant les rewrites | `BACKUP START` / `SEAL` (recommandé, pas une dépréciation) | 8.10 | `production-redis` |
