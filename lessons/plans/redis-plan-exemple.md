# Plan pédagogique : Leçons Redis

## Contexte

Création de fiches de révision denses (format skill `prof`) pour développeurs mid/senior, basées sur le cours Udemy "Redis The Complete Developer's Guide" (22 dossiers), enrichies par des recherches sur les nouveautés Redis 7.x / 8.x non couvertes par le cours.

**Le cours compte 22 dossiers, regroupés en 12 leçons** selon un ordre pédagogique (fondations → data types → messagerie → patterns → production). Le contenu trop niche/obsolète/superflu pour un mid/senior généraliste a été éliminé.

**Principe de regroupement** : concepts techniquement liés ou se complétant (ex : `Sorted Sets & Geospatial` car GEO est bâti sur Sorted Sets ; `Sets & HyperLogLog` car tous deux gèrent l'unicité/la cardinalité).

> ℹ️ Date de référence : 2026-04-09. Dernière version stable identifiée : **Redis Open Source 8.6** (Redis 8.x a unifié Redis Stack dans le core : Search, JSON, TimeSeries, Bloom, Vector Sets intégrés par défaut).

### Décisions de cadrage validées

- **12 leçons** : 1 fondations + 5 data types + 1 messaging + 3 patterns/programmabilité + 1 recherche + 1 production
- Chaque leçon = un bloc mental cohérent que le dev doit maîtriser ensemble
- **Fusion TTL/éviction dans L2 Strings** : cache = string + TTL, fusion naturelle. Éviction ajoutée (hors cours)
- **Fusion Bitmaps dans L2 Strings** : bitmaps = strings techniquement (même encoding sous-jacent)
- **Fusion HyperLogLog dans L5 Sets** : tous deux traitent unicité/cardinalité
- **Fusion Geospatial dans L6 Sorted Sets** : GEO bâti sur sorted sets en interne
- **Fusion Pub/Sub dans L7 Streams** : les deux paradigmes de messagerie Redis, comparés naturellement
- **Fusion Pipelining + Transactions + Locks en L9** : patterns d'exécution multi-commandes et de concurrence
- **Vector Sets en section mineure de L11 Query Engine** : pas assez mature (beta Redis 8) pour une leçon dédiée
- **Persistence + Replication + Cluster + ACL + Client-side caching + Observability en L12** : bloc opérationnel cohérent
- **SORT rétrogradé en legacy pattern dans L8** : supplanté par Query Engine

### Cartographie cours Udemy → leçons

| Dossier cours | Thème dossier | Leçon cible |
|---|---|---|
| 01. Get Started Here! | Intro, why Redis, setup | L1 Fondamentaux |
| 02. Commands for Adding and Querying Data | Strings, SET options, numbers | L2 Strings/bitmaps/TTL |
| 03. E-Commerce App Setup | Client libs, design methodology, key naming | Fusionné L1 + L8 |
| 04. Local Redis Setup | Install | Fusionné L1 |
| 05. Hash Data Structures | HSET, HGETALL, HDEL, HINCRBY | L3 Hashes |
| 06. Redis Has Gotcha's! | Gotchas HSET/HGETALL | Fusionné L3 Hashes |
| 07. Powerful Design Patterns | Data type selection, serialization, sessions | Fusionné L8 Modélisation |
| 08. Pipelining Commands | Pipelines, batching | L9 Pipelining/transactions/locks |
| 09. Enforcing Uniqueness with Sets | SADD, SINTER, SDIFF, SSCAN | L5 Sets & HLL |
| 10. A Little Set Implementation | Unique usernames, like system | Fusionné L5 |
| 11. Organizing Data with Sorted Sets | ZADD, ZRANGE, ZINCRBY, ZPOPMIN/MAX | L6 Sorted Sets & Geo |
| 12. Practice Time with Sorted Sets! | Most viewed, ending soonest | Fusionné L6 |
| 13. From Relational Data to Redis | SORT, BY, GET patterns | L8 Modélisation (SORT en legacy) |
| 14. HyperLogLog Structures | PFADD, PFCOUNT, PFMERGE | Fusionné L5 Sets & HLL |
| 15. Storing Collections with Lists | LPUSH, RPUSH, LRANGE, LTRIM, LREM | L4 Lists |
| 16. More Practice with E-Commerce App | Transactions, WATCH, concurrency | L9 |
| 17. Extending Redis with Scripting | Lua, EVAL, SCRIPT LOAD | L10 Scripting & Functions |
| 18. Understanding and Solving Concurrency Issues | Distributed locks, WithLock | L9 (locks) |
| 19. Querying Data with RediSearch | Redis modules, FT.CREATE, FT.SEARCH | L11 Query Engine |
| 20. Search in Action | TF-IDF, weights, EXPLAIN, PROFILE | Fusionné L11 |
| 21. Service Communication with Streams | XADD, XREAD, XGROUP, XCLAIM | L7 Streams & Pub/Sub |
| 22. Bonus! | Lien html uniquement | Ignoré |

### Contenu coupé ou rétrogradé (mid/senior généraliste)

| Élément | Décision | Raison |
|---|---|---|
| Vector Sets (VADD/VSIM) | Section mineure dans L11, pas co-vedette | Redis 8 beta, niche ML/recommandation |
| Redlock algorithm | Mention + critiques dans L9, pas recette détaillée | Controversé (critique publique Kleppmann), mieux avec Zookeeper/etcd |
| Sentinel | Mention brève dans L12 | En déclin au profit de Cluster |
| Sharded Pub/Sub | Mention brève dans L7 | Cas bord uniquement en Cluster mode |
| `BITFIELD OVERFLOW WRAP/SAT/FAIL` | Supprimé | Niche extrême, les vrais cas = SETBIT/BITCOUNT |
| `LCS` (Longest Common Subsequence) | Supprimé | Commande bizarre, utilité marginale |
| `SORT` command | Rétrogradé en "legacy pattern" dans L8 avec ⚠️ | Largement supplanté par Redis Query Engine |
| `SRANDMEMBER`, `HRANDFIELD` deep dive | Mention uniquement | Rarement utilisés en prod |
| `DUMP`/`RESTORE`/`MIGRATE` | Mention dans L12 uniquement | Ops rare, rare en code applicatif |

---

## Ordre d'exécution recommandé

```
Fondations
└── 1. fondamentaux                          ← in-memory, key-value, redis-cli, SCAN, key naming

Data types
├── 2. strings-bitmaps-ttl                   ← SET/GET, bitmaps, TTL, éviction
├── 3. hashes                                ← HSET, HGETALL, HEXPIRE 7.4+, encoding
├── 4. lists                                 ← LPUSH/RPUSH, LMOVE 6.2+, queues
├── 5. sets-hyperloglog                      ← SADD, SINTER, SINTERCARD 7.0+, PFADD, HLL
└── 6. sorted-sets-geospatial                ← ZADD, ZRANGE unifié 6.2+, GEOSEARCH

Messaging
└── 7. streams-pubsub                        ← XADD, XREADGROUP, XAUTOCLAIM, PUBLISH/SUBSCRIBE

Patterns & programmabilité
├── 8. modelisation-relationnelle             ← key naming, data type selection, SORT legacy
├── 9. pipelining-transactions-locks          ← pipeline, MULTI/EXEC, WATCH, distributed locks
└── 10. scripting-lua-functions               ← EVAL, Redis Functions 7.0+, FCALL

Recherche
└── 11. redis-query-engine                    ← FT.CREATE, FT.SEARCH, Vector search, FT.HYBRID

Production
└── 12. production-redis                      ← persistence, replication, cluster, ACL, observabilité
```

**Pourquoi cet ordre :**
- Fondamentaux d'abord (commandes transversales, key naming, architecture Redis)
- Data types ensuite (de simple à complexe : strings → hashes → lists → sets → sorted sets)
- Messaging après les data types (Streams utilise des concepts de lists et sorted sets)
- Patterns après les data types (pipelining/transactions/locks supposent la connaissance des data types)
- Query Engine après les data types (indexe des HASH et JSON)
- Production en dernier (persistence, cluster, sécurité, observabilité)

---

## Versions cibles

| Techno | `last_version` | Notes |
|--------|----------------|-------|
| `redis` | `"8.6"` | Redis Open Source 8.6 stable avril 2026, Stack unifié dans le core |

Le champ `last_version` doit être écrit **par leçon** dans l'index. Toutes les leçons redis auront `last_version: "8.6"`.

---

## Leçons Redis (techno=redis, last_version="8.6")

### 1. fondamentaux

```bash
/prof --techno=redis --lecon="Fondamentaux de Redis" --concepts="in-memory,key-value store,single-thread,I/O threads,RESP2,RESP3,redis-cli,PING,INFO,CONFIG GET,CONFIG SET,SELECT,databases 0-15,DBSIZE,FLUSHDB,FLUSHALL,KEYS vs SCAN,SCAN MATCH COUNT TYPE,EXISTS,DEL,UNLINK,TYPE,RENAME,RENAMENX,COPY,OBJECT ENCODING,key naming conventions entity:id:field,Redis Open Source 8 Stack unifié,client libraries node-redis ioredis jedis lettuce redis-py"
```

**Points à garder en tête pour le skill :**
- Sources cours : 01, 03 (design methodology, key naming), 04, 07 (data type selection)
- **Single-thread** + I/O threads (Redis 6+) : expliquer pourquoi Redis est rapide malgré le single-thread
- **`KEYS` vs `SCAN`** : `KEYS` bloque le serveur, `SCAN` est non-bloquant avec curseur. Piège critique en prod
- **Key naming** : convention `entity:id:field` (ex : `user:42:email`), pas de standard imposé mais convention largement adoptée
- **Redis Open Source 8** : Stack (Search, JSON, TimeSeries, Bloom) unifié dans le core, plus besoin de modules séparés
- **Client libraries** : mentionner les principales par langage sans deep dive (node-redis/ioredis, jedis/lettuce, redis-py)

---

### 2. strings-bitmaps-ttl

```bash
/prof --techno=redis --lecon="Strings, bitmaps, TTL & éviction" --concepts="SET,GET,MSET,MGET,MSETNX,SETNX,options EX PX EXAT PXAT NX XX KEEPTTL GET IFEQ IFGT,GETDEL,GETEX,APPEND,STRLEN,GETRANGE,SETRANGE,INCR,DECR,INCRBY,DECRBY,INCRBYFLOAT,SETBIT,GETBIT,BITCOUNT BYTE BIT,BITPOS,BITOP AND OR XOR NOT,BITFIELD basics,EXPIRE,PEXPIRE,EXPIREAT,PEXPIREAT,TTL,PTTL,PERSIST,EXPIRETIME,PEXPIRETIME,EXPIRE NX XX GT LT,active vs passive expiration,maxmemory,eviction policies noeviction allkeys-lru allkeys-lfu volatile-lru volatile-lfu volatile-ttl,OBJECT FREQ IDLETIME,LFU vs LRU,maxmemory-samples,keyspace notifications,cache invalidation cross-service"
```

**Points à garder en tête pour le skill :**
- Sources cours : 02 + recherche (bitmaps, éviction hors cours)
- **`IFEQ`/`IFGT`** options de SET (Redis 8.4+) : conditional SET, vérifier sur sources officielles
- **Bitmaps** = strings techniquement (même encoding), expliquer le mapping bit ↔ offset
- **`BITFIELD`** : couvrir les basics (types `i8`/`u16`/`i64`, GET/SET/INCRBY), pas OVERFLOW WRAP/SAT/FAIL (supprimé, trop niche)
- **Active vs passive expiration** : passive = check au prochain accès, active = sampling périodique (10 keys/100ms)
- **Éviction policies** : tableau comparatif LRU vs LFU vs volatile vs allkeys
- **Keyspace notifications** : `notify-keyspace-events`, `__keyevent@db__:expired`, pattern cache invalidation cross-service
- Use cases : cache, compteurs atomiques, rate limiting, presence tracking, feature flags
- Dépréciations : `GETSET` → `SET ... GET` ; `SUBSTR` → `GETRANGE`

---

### 3. hashes

```bash
/prof --techno=redis --lecon="Hashes" --concepts="HSET variadique,HGET,HMGET,HGETALL gotcha gros hash,HDEL,HEXISTS,HKEYS,HVALS,HLEN,HSTRLEN,HINCRBY,HINCRBYFLOAT,HSETNX,HSCAN,HEXPIRE HPEXPIRE HEXPIREAT HPEXPIREAT HTTL HPTTL HPERSIST,encoding listpack vs hashtable,ziplist vers listpack Redis 7.2,hash-max-listpack-entries,hash-max-listpack-value,sessions avec TTL par champ,entity storage,partial updates"
```

**Points à garder en tête pour le skill :**
- Sources cours : 05, 06, 07 (sessions, create user)
- **`HGETALL` gotcha** : sur un hash de 10k+ champs, `HGETALL` bloque le serveur. Utiliser `HSCAN` ou `HMGET` ciblé
- **`HEXPIRE`/`HTTL` per-field TTL** (Redis 7.4+) : révolution pour les sessions (expirer un champ sans supprimer le hash entier)
- **Encoding** : `listpack` (compact, < seuils) vs `hashtable` (performant, > seuils). Historique `ziplist` → `listpack` en Redis 7.2
- **Seuils d'encoding** : `hash-max-listpack-entries` (défaut 128), `hash-max-listpack-value` (défaut 64)
- Use cases : entity storage, sessions avec TTL par champ, partial updates, user profiles
- Dépréciations : `HMSET` → `HSET` variadique ; `ziplist` → `listpack`

---

### 4. lists

```bash
/prof --techno=redis --lecon="Lists" --concepts="LPUSH,RPUSH,LPUSHX,RPUSHX,LPOP count,RPOP count,LLEN,LRANGE,LINDEX,LSET,LTRIM,LREM,LINSERT,LPOS,LMOVE,BLMOVE,BLPOP,BRPOP,LMPOP,BLMPOP,quicklist encoding,FIFO queue,LIFO stack,capped log LTRIM,activity feed"
```

**Points à garder en tête pour le skill :**
- Sources cours : 15, 16 (bid history)
- **`LMOVE`** (Redis 6.2+) remplace `RPOPLPUSH` : atomique, supporte source = destination (rotation)
- **`LMPOP`/`BLMPOP`** (Redis 7.0+) : pop depuis N listes, choisir LEFT ou RIGHT
- **`quicklist` encoding** : liste de listpacks, compromise entre mémoire et performance
- **Capped log** pattern : `LPUSH` + `LTRIM` pour garder les N derniers éléments
- Use cases : FIFO queue, LIFO stack, capped log via `LTRIM`, activity feed, bid history
- Dépréciations : `RPOPLPUSH`/`BRPOPLPUSH` → `LMOVE`/`BLMOVE`

---

### 5. sets-hyperloglog

```bash
/prof --techno=redis --lecon="Sets & HyperLogLog" --concepts="SADD,SREM,SMEMBERS,SISMEMBER,SMISMEMBER,SCARD,SPOP,SMOVE,SUNION,SINTER,SDIFF,SINTERCARD,SUNIONSTORE,SINTERSTORE,SDIFFSTORE,SSCAN,intset encoding,PFADD,PFCOUNT,PFMERGE,cardinalité probabiliste 0.81% erreur,12KB max par HLL,unicité,tags,relations,like system,amis communs,visiteurs uniques DAU MAU"
```

**Points à garder en tête pour le skill :**
- Sources cours : 09, 10, 14 (HLL)
- **`SMISMEMBER`** (Redis 6.2+) : vérifier N éléments d'un coup
- **`SINTERCARD`** (Redis 7.0+) : cardinalité de l'intersection SANS matérialiser le résultat (perf)
- **`intset` encoding** : quand tous les éléments sont des entiers et < seuil (`set-max-intset-entries`)
- **HyperLogLog** : cardinalité probabiliste (~0.81% erreur), 12KB max par structure. Expliquer le trade-off précision/mémoire
- Use cases : unicité, tags, relations, like system, amis communs, visiteurs uniques, DAU/MAU

---

### 6. sorted-sets-geospatial

```bash
/prof --techno=redis --lecon="Sorted Sets & Geospatial" --concepts="ZADD GT LT XX NX CH INCR,ZREM,ZRANGE unifié BYSCORE BYLEX REV LIMIT,ZSCORE,ZMSCORE,ZINCRBY,ZRANK WITHSCORE,ZREVRANK,ZCARD,ZCOUNT,ZLEXCOUNT,ZPOPMIN,ZPOPMAX,BZPOPMIN,BZPOPMAX,ZMPOP,BZMPOP,ZRANGESTORE,ZUNIONSTORE,ZINTERSTORE,ZDIFFSTORE,ZINTERCARD,lex ranges,skiplist encoding,GEOADD NX XX CH,GEOPOS,GEODIST,GEOHASH,GEOSEARCH FROMMEMBER FROMLONLAT BYRADIUS BYBOX,GEOSEARCHSTORE,leaderboard,priority queue,nearest-of,POI search"
```

**Points à garder en tête pour le skill :**
- Sources cours : 11, 12 + recherche (GEO hors cours)
- **`ZRANGE` unifié** (Redis 6.2+) : remplace `ZRANGEBYSCORE`, `ZREVRANGEBYSCORE`, `ZRANGEBYLEX`, `ZREVRANGEBYLEX`, `ZREVRANGE`. Syntaxe unique avec `BYSCORE`/`BYLEX`/`REV`/`LIMIT`
- **`ZRANK WITHSCORE`** (Redis 7.2+) : retourne rank + score en un appel
- **`ZINTERCARD`** (Redis 7.0+) : cardinalité de l'intersection sans matérialiser
- **Lex ranges** : `[`, `(`, `-`, `+` pour filtrage lexicographique
- **`skiplist` encoding** : structure interne des sorted sets (O(log N) insert/search)
- **GEO bâti sur sorted sets** : `GEOADD` encode longitude/latitude en score via geohash
- **`GEOSEARCH`** (Redis 6.2+) remplace `GEORADIUS`/`GEORADIUSBYMEMBER` : plus flexible (BYRADIUS + BYBOX)
- Use cases : leaderboard, priority queue, time-based index, nearest-of, POI search
- Dépréciations : `ZRANGEBYSCORE`/`ZREVRANGEBYSCORE`/`ZRANGEBYLEX`/`ZREVRANGEBYLEX`/`ZREVRANGE` → `ZRANGE` ; `GEORADIUS`/`GEORADIUSBYMEMBER` → `GEOSEARCH`

---

### 7. streams-pubsub

```bash
/prof --techno=redis --lecon="Streams & Pub/Sub" --concepts="XADD ID auto NOMKSTREAM MAXLEN MINID LIMIT,XREAD COUNT BLOCK,XRANGE,XREVRANGE,XLEN,XDEL,XTRIM,XINFO STREAM GROUPS CONSUMERS,XGROUP CREATE DESTROY CREATECONSUMER DELCONSUMER SETID,XREADGROUP,XACK,XPENDING,XCLAIM,XAUTOCLAIM,pending entries list PEL,at-least-once delivery,PUBLISH,SUBSCRIBE,UNSUBSCRIBE,PSUBSCRIBE,PUNSUBSCRIBE,PUBSUB CHANNELS NUMSUB NUMPAT,fire-and-forget,streams vs pub/sub durabilité vs éphémère,event sourcing,microservices messaging"
```

**Points à garder en tête pour le skill :**
- Sources cours : 21 + recherche (Pub/Sub hors cours)
- **`XAUTOCLAIM`** (Redis 6.2+) : combine `XPENDING` + `XCLAIM` en un appel atomique (récupération des messages idle)
- **Consumer groups** : `XGROUP CREATE`, `XREADGROUP GROUP <group> <consumer>`, `>` pour nouveaux messages, `0` pour pending
- **PEL** (Pending Entries List) : messages lus mais pas ACK, visible via `XPENDING`
- **At-least-once delivery** : garantie via PEL + `XACK`. Pas d'exactly-once natif
- **Pub/Sub** : fire-and-forget, pas de persistence, pas de replay. Si subscriber absent = message perdu
- **Sharded Pub/Sub** (`SPUBLISH`/`SSUBSCRIBE`) : mention brève, cas bord cluster uniquement
- **Streams vs Pub/Sub** : tableau comparatif (durabilité, replay, consumer groups vs fire-and-forget)
- Use cases : event sourcing, microservices messaging, realtime, notifications

---

### 8. modelisation-relationnelle

```bash
/prof --techno=redis --lecon="Modélisation relationnelle Redis" --concepts="design methodology reducing design to queries,data type selection per resource,key naming conventions entity:id:field,secondary indices via Sets Sorted Sets,denormalization vs normalization,sérialisation désérialisation JSON buffers Date,reference patterns entre clés,session pattern,SORT legacy BY GET LIMIT ALPHA STORE SORT_RO,join-via-GET,limitations cluster hash tags,quand migrer vers Query Engine"
```

**Points à garder en tête pour le skill :**
- Sources cours : 03 (key naming, design methodology), 07 (data type selection, serialization), 13 (SORT en legacy)
- **Design methodology** : partir des queries (comment sera lu le data) et choisir le data type en conséquence
- **Data type selection** : quand utiliser string vs hash vs set vs sorted set vs list pour une ressource
- **Secondary indices** : construire des index manuels via Sets/Sorted Sets pour filtrer/chercher
- **Denormalization** : Redis favorise la dénormalisation (dupliquer pour éviter les joins)
- **`SORT` comme pattern legacy** : `SORT BY hash->field GET hash->field` = pseudo-join, mais largement supplanté par Redis Query Engine. Marquer `> ⚠️`
- **`SORT_RO`** (Redis 7.0+) : version read-only de SORT
- **Limitations cluster** : `SORT` avec `BY`/`GET` nécessite que toutes les clés soient sur le même shard (hash tags `{...}`)
- **Quand migrer vers Query Engine** : dès que les queries deviennent complexes (filtres multiples, full-text, geo)

---

### 9. pipelining-transactions-locks

```bash
/prof --techno=redis --lecon="Pipelining, transactions & locks distribués" --concepts="pipelining RTT optimisation,pipeline vs atomique,socket output buffer,pipeline sur cluster hash slots,MULTI,EXEC,DISCARD,WATCH,UNWATCH,optimistic locking CAS,queued commands,EXECABORT,erreurs parsing vs runtime,pas de rollback,SET key token NX EX,token unique UUID,unlock script Lua atomique,lock expiration,lock renewal watchdog,Redlock mention critiques Kleppmann,accidental unlocks,clock drift,singleton task,section critique distribuée"
```

**Points à garder en tête pour le skill :**
- Sources cours : 08 (pipelining), 16 (transactions), 18 (locks)
- **Pipeline ≠ atomique** : les commandes pipelinées ne sont PAS exécutées de manière atomique (d'autres clients peuvent intercaler)
- **Pipeline sur cluster** : les commandes doivent cibler le même hash slot, sinon le client doit splitter
- **`WATCH` + `MULTI`/`EXEC`** : optimistic locking (CAS). Si une clé watchée change entre `WATCH` et `EXEC`, la transaction échoue (retourne `nil`)
- **Pas de rollback** : Redis n'a pas de rollback transactionnel. Si une commande échoue dans un `MULTI`, les autres s'exécutent quand même
- **Distributed lock** : `SET key token NX EX` + unlock via script Lua (check-and-delete atomique). Le token UUID empêche les accidental unlocks
- **Redlock** : mention + critiques (Kleppmann). Ne pas recommander en détail, indiquer que Zookeeper/etcd sont préférés pour les sections critiques
- **Lock renewal (watchdog)** : pattern pour prolonger le TTL du lock avant expiration (évite les cas de slow processing)

---

### 10. scripting-lua-functions

```bash
/prof --techno=redis --lecon="Scripting Lua & Redis Functions" --concepts="EVAL,EVALSHA,SCRIPT LOAD,SCRIPT EXISTS,SCRIPT FLUSH,KEYS table,ARGV table,redis.call vs redis.pcall,redis.error_reply,redis.status_reply,atomicité serveur bloqué,Lua basics tables arrays conditionals,FUNCTION LOAD,FCALL,FCALL_RO,FUNCTION LIST,FUNCTION DELETE,FUNCTION DUMP,FUNCTION RESTORE,FUNCTION STATS,FUNCTION KILL,redis.register_function,libraries,persistence RDB AOF,réplication automatique,scripts ad-hoc vs functions persistées,migration EVAL vers Functions"
```

**Points à garder en tête pour le skill :**
- Sources cours : 17 + recherche (Redis Functions hors cours)
- **Atomicité Lua** : le serveur est bloqué pendant l'exécution du script. Scripts courts obligatoires
- **`redis.call` vs `redis.pcall`** : `call` propage l'erreur, `pcall` la capture (protected call)
- **Redis Functions (7.0+)** : remplacement moderne de `EVAL` pour les scripts persistés. `FUNCTION LOAD` + `FCALL`
- **Persistence** : les functions sont persistées dans RDB/AOF et répliquées automatiquement (contrairement aux scripts EVAL qui sont ad-hoc)
- **Migration EVAL → Functions** : expliquer les avantages (persistence, naming, libraries) et le pattern de migration
- **Lua basics** : tables/arrays, conditions, string manipulation. Juste assez pour écrire des scripts Redis, pas un cours Lua

---

### 11. redis-query-engine

```bash
/prof --techno=redis --lecon="Redis Query Engine" --concepts="Query Engine renommage RediSearch intégré Redis 8,FT.CREATE,FT.SEARCH,FT.DROPINDEX,FT.ALTER,FT.INFO,FT.EXPLAIN,FT.PROFILE,FT.AGGREGATE,index sur HASH vs JSON,field types TEXT NUMERIC TAG GEO VECTOR,text queries,NUMERIC ranges,TAG filters,GEO search,fuzzy,prefix,TF-IDF vs BM25,WEIGHT,SORTBY,LIMIT,RETURN,HIGHLIGHT,SUMMARIZE,stemming,stopwords,VECTOR field FLAT HNSW,KNN queries,FT.HYBRID,Vector Sets section mineure VADD VSIM,cosine similarity,full-text search,e-commerce search,semantic search"
```

**Points à garder en tête pour le skill :**
- Sources cours : 19, 20 + recherche Redis 8
- **Renommage** : RediSearch → Redis Query Engine (intégré Redis 8, plus besoin de Stack séparé)
- **Index sur HASH vs JSON** : JSON natif dans Redis 8 (JSONPath queries), HASH pour données plates
- **Field types** : `TEXT` (full-text), `NUMERIC` (range queries), `TAG` (exact match, multi-valued), `GEO` (spatial), `VECTOR` (similarity search)
- **`FT.HYBRID`** (Redis 8.4+) : recherche hybride vecteur + métadonnées en un seul appel
- **Vector Sets (section mineure)** : `VADD`, `VSIM`, HNSW built-in, cosine similarity. Redis 8 beta, data type natif (distinct du VECTOR field dans les index du Query Engine). Mentionner le positionnement : Vector Sets = data type, VECTOR index = index sur HASH/JSON
- **TF-IDF vs BM25** : expliquer brièvement la différence de scoring
- Use cases : full-text search, e-commerce search (filtres + tri), semantic search (vectors)

---

### 12. production-redis

```bash
/prof --techno=redis --lecon="Production Redis : ops, sécurité & observabilité" --concepts="RDB snapshots,save directives,BGSAVE,LASTSAVE,AOF,appendonly,appendfsync always everysec no,AOF rewrite,BGREWRITEAOF,hybrid persistence aof-use-rdb-preamble,fork copy-on-write,RDB vs AOF trade-offs,REPLICAOF,async replication,PSYNC,replication backlog,WAIT,Sentinel mention brève,Cluster hash slots 16384,CLUSTER SHARDS NODES SLOTS,hash tags,MOVED ASK redirections,multi-key limitations,ACL SETUSER GETUSER LIST WHOAMI CAT LOG,categories read write admin dangerous,command patterns,key patterns,TLS,CLIENT TRACKING ON REDIRECT BCAST PREFIX,RESP3 push invalidation,SLOWLOG,LATENCY LATEST HISTORY DOCTOR,MEMORY USAGE STATS DOCTOR,CLIENT LIST KILL,INFO sections,MONITOR warning,OBJECT ENCODING tuning"
```

**Points à garder en tête pour le skill :**
- Sources cours : recherche uniquement (leçon entièrement hors cours)
- **Persistence** : RDB (snapshots), AOF (journal append-only), hybrid (`aof-use-rdb-preamble`). Expliquer fork + copy-on-write et ses implications mémoire
- **RDB vs AOF** : tableau comparatif (durabilité, performance, taille, recovery time)
- **Cluster** : 16384 hash slots, `MOVED`/`ASK` redirections, hash tags `{user:1}:profile`, limitations multi-key
- **Sentinel** : mention brève (monitoring, quorum), en déclin au profit de Cluster
- **ACL** (Redis 6+) : `ACL SETUSER`, catégories (`@read`, `@write`, `@admin`, `@dangerous`), key patterns (`~cache:*`)
- **Client-side caching** : `CLIENT TRACKING` avec RESP3 push invalidation. Deux modes : tracking (per-key) vs broadcasting (prefix-based)
- **Observabilité** : `SLOWLOG` (queries lentes), `LATENCY LATEST`/`DOCTOR` (latence), `MEMORY USAGE`/`DOCTOR` (mémoire), `CLIENT LIST` (connexions), `MONITOR` (⚠️ jamais en prod, impact perf majeur)
- **Encoding tuning** : `hash-max-listpack-entries`, `list-max-listpack-size`, `set-max-intset-entries`, `zset-max-listpack-entries`
- Dépréciations : `SLAVEOF` → `REPLICAOF` ; `requirepass` (legacy) → ACL users

---

## Dépréciations et breaking changes critiques à signaler

| Ancien | Nouveau | Leçon impactée |
|--------|---------|----------------|
| `GETSET` | `SET ... GET` (6.2+) | `strings-bitmaps-ttl` |
| `SUBSTR` | `GETRANGE` | `strings-bitmaps-ttl` |
| `HMSET` | `HSET` variadique (4.0+) | `hashes` |
| `ziplist` encoding | `listpack` (7.2+) | `hashes` |
| `RPOPLPUSH` / `BRPOPLPUSH` | `LMOVE` / `BLMOVE` (6.2+) | `lists` |
| `ZRANGEBYSCORE` / `ZREVRANGEBYSCORE` / `ZRANGEBYLEX` / `ZREVRANGEBYLEX` / `ZREVRANGE` | `ZRANGE` unifié (6.2+) | `sorted-sets-geospatial` |
| `GEORADIUS` / `GEORADIUSBYMEMBER` | `GEOSEARCH` (6.2+) | `sorted-sets-geospatial` |
| `SLAVEOF` | `REPLICAOF` (5.0+) | `production-redis` |
| `requirepass` (legacy) | ACL users (6.0+) | `production-redis` |
| Redis Stack (distribution séparée) | Redis Open Source 8 (unifié) | `fondamentaux` + `redis-query-engine` |
| `SORT` comme pattern de query | Redis Query Engine | `modelisation-relationnelle` |

---

## Fichiers critiques à consulter avant exécution

- `.claude/skills/prof/SKILL.md` : spec complète du skill `prof` (workflow CREATE, conventions de format, règles de recherche)
- `.claude/skills/prof/templates/lesson.md` : template de structure d'une leçon
- `lessons/index.yaml` : index global (à enrichir avec techno `redis`)
- `lessons/redis/` : dossier destination des 12 fichiers `<id>.md` (à créer)

## Vérification du plan (end-to-end)

1. **Structure fichiers** : `lessons/redis/` doit contenir 12 fichiers `.md` en kebab-case (`fondamentaux.md`, `strings-bitmaps-ttl.md`, `hashes.md`, `lists.md`, `sets-hyperloglog.md`, `sorted-sets-geospatial.md`, `streams-pubsub.md`, `modelisation-relationnelle.md`, `pipelining-transactions-locks.md`, `scripting-lua-functions.md`, `redis-query-engine.md`, `production-redis.md`)
2. **Index YAML** : `lessons/index.yaml` doit contenir une nouvelle entrée `redis:` au niveau racine avec 12 leçons, chacune avec `id`, `file`, `concepts`, `last_version: "8.6"`, `last_updated`
3. **Ordre recommandé de création** : L1 → L12 dans l'ordre (progression pédagogique)
4. **Sondage qualité** : relire L2 (strings+bitmaps+TTL, grosse fusion), L9 (pipelining+transactions+locks, 3 sujets), L11 (query engine avec Vector Sets en section), L12 (production, la plus dense) pour vérifier cohérence et équilibre
5. **Cohérence Redis 8** : chaque mention de Redis Stack doit pointer vers Redis Open Source 8 unifié (L1, L11) ; chaque leçon avec dépréciations (L2, L3, L4, L6, L8, L12) doit avoir les `> ⚠️` appropriés

## Notes opérationnelles

- Les listes de `--concepts` **cadrent** le skill, pas d'exhaustivité. Le skill `prof` effectue ses propres recherches et peut ajouter des concepts manquants essentiels identifiés lors des recherches
- Le skill `prof` demande **validation utilisateur AVANT** d'écrire chaque leçon (règle OBLIGATOIRE dans SKILL.md), sauf si lancé via `/create-lesson` qui override cette validation
