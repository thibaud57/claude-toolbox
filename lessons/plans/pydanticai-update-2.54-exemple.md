# Plan de mise à jour : PydanticAI 2.0 → 2.54

## Contexte

Mise à jour des leçons `pydanticai` (format skill `lesson-doc`) entre la version des leçons et la version stable actuelle. Produit et validé en Phase 2 de `/update-lesson`, puis lu par `lesson/writer`, `lesson/auditor` et `lesson/coherence-auditor`.

> ℹ️ Date de référence : 2026-10-08. Version stable identifiée : **pydantic-ai 2.54** ([PyPI](https://pypi.org/project/pydantic-ai/), « Released: Oct 3, 2026 ») ; **pydantic-ai-harness 0.54** ([PyPI](https://pypi.org/project/pydantic-ai-harness/), dépend de `pydantic-ai-slim==2.54.0`).

Inventaire : les 54 releases GitHub de v2.1.0 à v2.54.0 ont été lues (v2.35.2 n'existe pas). Le changelog `pydantic.dev/docs/ai/changelog/` s'arrête à 2.0.0 ; la doc de référence est celle du dépôt au tag `v2.54.0`.

## Changements identifiés

Un changement par ligne, chacun tracé à une source officielle consultée (cf. skill lesson-doc § Règles leçon > Recherches, Traçabilité des sources). Un changement `non confirmé` n'est jamais assigné à une leçon.

Abréviations : `R:x.y.z` = `https://github.com/pydantic/pydantic-ai/releases/tag/vx.y.z` ; `D:chemin` = `https://github.com/pydantic/pydantic-ai/blob/v2.54.0/docs/chemin`.

| # | Changement | Version | Source | Extrait | Statut |
|---|------------|---------|--------|---------|--------|
| 1 | Stable V2 publiée : retirer les mentions beta `2.0.0b3` | 2.0 | https://pydantic.dev/docs/ai/changelog/ | "v2.0.0 (2026-06-23) The stable V2.0 release." | confirmé |
| 2 | Politique de version : pas de breaking volontaire en mineure, modules `beta` exclus | 2.0 | D:version-policy.md | "We will not intentionally make breaking changes in minor releases" | confirmé |
| 3 | Budget de retries des tools surchargeable par run / `override()` | 2.15 | R:2.15.0 | "Support overriding the tool-retry budget at `run`/`iter`/`override` time" | confirmé |
| 4 | `AnthropicModel` : `max_tokens` par défaut = max output du modèle, streaming interne | 2.52 | R:2.52.0, D:models/anthropic.md | "Default `AnthropicModel`'s `max_tokens` to the model's maximum output, streaming such requests behind the scenes" | confirmé |
| 5 | `AnthropicProvider(http_client=)` exige un `httpx2.AsyncClient` | 2.33 | R:2.33.0 | "it must now be an `httpx2.AsyncClient`" | confirmé |
| 6 | `run_id=` fourni par l'application, exposé sur `RunContext.run_id` | 2.16 | R:2.16.0, D:message-history.md | "Add optional `run_id=` to agent runs, durable wrappers, and UI adapters" | confirmé |
| 7 | `RunContext.usage_limits` lisible par tools et capabilities | 2.9 | R:2.9.0 | "expose the run's `usage_limits` to tools and capabilities" | confirmé |
| 8 | Annulation : `CancellationToken`, `RunContext.cancel()`, `AgentRun.cancel()`, `RunCancelled` | 2.26 | R:2.26.0, D:agent.md | "Add first-party run cancellation: `AgentRun.cancel()`, `RunContext.cancel()`, `RunCancelled`" | confirmé |
| 9 | `RunUsage.cost` (`Decimal | None`) et `UsageLimits(cost_limit=)` | 2.23 | R:2.23.0, `pydantic_ai_slim/pydantic_ai/usage.py` | "Add `cost` to `RunUsage` and `cost_limit` to `UsageLimits`" | confirmé |
| 10 | `cache_hit_ratio` sur `RequestUsage` / `RunUsage` | 2.13 | R:2.13.0 | "add `cache_hit_ratio` property to `RequestUsage` and `RunUsage`" | confirmé |
| 11 | Hooks : `wrap_*` enveloppe tout le cycle d'une étape | 2.54 | R:2.54.0, D:hooks.md | "Make `wrap_*` hooks enclose complete stage lifecycles" | confirmé |
| 12 | Capabilities : `id` par défaut et fusion des répétitions via `combine()` | 2.38 | R:2.38.0, D:capabilities/custom.md | "Give one-off capabilities a default `id` and a `combine` rule for repeats" | confirmé |
| 13 | Événements typés `CustomEvent` / `CapabilityEvent`, `@agent.on_event` | 2.38 / 2.40 | R:2.38.0, R:2.40.0 | "Add `@agent.on_event` for registering event listeners on an `Agent`" | confirmé |
| 14 | Hooks de capability `get_model()` / `resolve_model_id()` | 2.13 | R:2.13.0 | "Add `get_model`, `resolve_model_id`, and `for_agent` capability hooks" | confirmé |
| 15 | `pydantic-ai-harness` intégré au dépôt, publié avec chaque release | 2.52 | R:2.52.0 | "`pydantic-ai-harness` now lives in this repository and ships with every Pydantic AI release" | confirmé |
| 16 | `ToolFailed` : échec visible du modèle sans consommer les retries | 2.16 | R:2.16.0, D:tools-advanced.md | "Add `ToolFailed` for model-visible failures without retries" | confirmé |
| 17 | `MCPToolset(tool_error_behavior='retry' / 'failed' / 'error')` | 2.16 | D:mcp/client.md | "Raises `ToolFailed`, which is recorded as a tool result with `outcome='failed'`" | confirmé |
| 18 | `MCPToolset` compatible FastMCP 4 et MCP SDK v2 | 2.29 | R:2.29.0 | "Support FastMCP 4 and MCP SDK v2 in `MCPToolset` alongside FastMCP 3" | confirmé |
| 19 | `args_validator` peut lever `ApprovalRequired` / `CallDeferred` | 2.22 | R:2.22.0, D:tools-advanced.md | "Support requesting approval or deferring a call from a tool's `args_validator`" | confirmé |
| 20 | `HandleDeferredToolCalls` résout les appels différés en ligne | 2.54 (doc) | D:tools-advanced.md | "resolved inline by a `HandleDeferredToolCalls` handler" | confirmé |
| 21 | `output_type=[Foo, Bar, None]` typé `| None` | 2.49 | R:2.49.0 | "Type `None` in a list of output types as `| None`" | confirmé |
| 22 | `run_stream_events()` retourne un handle `AgentRunEvents` | 2.26 | R:2.26.0 | "Promote `run_stream_events()` iterator to public `AgentRunEvents` handle with `cancel()`" | confirmé |
| 23 | Réparation automatique de l'historique, `repair_messages` | 2.10 / 2.53 | R:2.10.0, R:2.53.0, D:message-history.md | "Make `message_history` provider-valid out of the box (repair tool-call/result pairing)" | confirmé |
| 24 | `sanitize_messages` pour un historique non fiable | 2.5 | R:2.5.0, D:message-history.md | "Add `sanitize_messages` for inbound message-history hardening" | confirmé |
| 25 | `UsageLimits(per_request_input_tokens_limit=)` | 2.21 | R:2.21.0, D:agent.md | "add `per_request_input_tokens_limit` to `UsageLimits`" | confirmé |
| 26 | Délégation : `SubAgents` (harness) recommandé, délégation manuelle pour les cas sur-mesure | 2.54 (doc) | D:multi-agent-applications.md | "`SubAgents` capability that is the most convenient way to delegate" | confirmé |
| 27 | `run_sync()` interdit depuis un callback sync dans un run | 2.32 | R:2.32.1 | "Reject `Agent.run_sync()` from synchronous callbacks inside agent runs" | confirmé |
| 28 | pydantic-graph : `GraphBuilder` sorti de `beta`, `Graph(nodes=[...])` supprimé, `BaseNode` via `g.node()` | 2.0 | D:migration.md, D:graph.md, D:graph/builder/index.md | "`from pydantic_graph.beta import GraphBuilder` → `from pydantic_graph import GraphBuilder`" | confirmé |
| 29 | `pydantic_graph.persistence` et `pydantic_graph.mermaid` supprimés, `Graph.render()` | 2.0 | D:migration.md, D:graph/builder/index.md | "`pydantic_graph.persistence` was removed in V2" | confirmé |
| 30 | Capabilities `TemporalDurability` / `DBOSDurability` / `PrefectDurability`, wrappers `*Agent` dépréciés (retrait v3) | 2.14 | R:2.14.0, D:durable_execution/temporal.md | "will be removed in v3. New code should use the `TemporalDurability` capability" | confirmé |
| 31 | Un seul moteur durable par agent | 2.54 | R:2.54.0 | "Refuse a second durable execution engine on an agent before either binds" | confirmé |
| 32 | `@durable_operation` pour les auteurs de capabilities | 2.36 | R:2.36.0, D:capabilities/custom.md | "Add `@durable_operation` for capabilities" | confirmé |
| 33 | Sous Temporal, le `RunContext` d'une activity est une copie (`usage` non remonté) | 2.54 (doc) | D:durable_execution/temporal.md | "`usage` is a snapshot of the run's usage at the time the activity was scheduled" | confirmé |
| 34 | `RestateAgent` fourni par le SDK Restate | 2.54 (doc) | D:durable_execution/restate.md | "wrapping it with `RestateAgent` from the Restate SDK" | confirmé |
| 35 | Préfixe `google-gla:` remplacé par `google:` | 2.0 | D:migration.md | "| `google-gla:` | `google:` |" | confirmé |
| 36 | UI adapters : `allow_uploaded_files` remplace `preserve_file_data` côté sécurité | 2.4 | R:2.4.0, D:ui/ag-ui.md | "Split `preserve_file_data` into `allow_uploaded_files` (inbound security)" | confirmé |
| 37 | UI adapters : `Content-Type` JSON obligatoire | 2.44 | R:2.44.0 | "Require a JSON `Content-Type` on UI adapter requests" | confirmé |
| 38 | Faille AG-UI GHSA-jpr8-2v3g-wgf9 corrigée | 2.5 | R:2.5.0 | "a dropped trailing client message could re-expose a preceding unresolved tool call" | confirmé |
| 39 | `GEval` et evaluators agentiques (`ToolCorrectness`, `TrajectoryMatch`...) | 2.4 | R:2.4.0, D:evals/evaluators/agentic.md | "Add `GEval` evaluator and standard quality metric rubrics for `LLMJudge`" | confirmé |
| 40 | Instrumentation v6 opt-in, v2 à v4 dépréciées, v5 par défaut | 2.32 | R:2.32.0, D:logfire.md | "Versions 2, 3, and 4 are deprecated compatibility formats" | confirmé |
| 41 | `include_content=False` exclut aussi exceptions et instructions | 2.44 | R:2.44.0, D:logfire.md | "spans still carried exceptions, error statuses, instructions and the output template" | confirmé |
| 42 | `WebSearch` / `WebFetch` native-only par défaut, repli local via `local=` | 2.54 (doc) | D:capabilities/web-search.md, D:capabilities/web-fetch.md | "`WebSearch` defaults to native-only." | confirmé |
| 43 | `PrepareTools` : retourner `None` lève `TypeError` | 2.0 | D:migration.md | "returning `None` now raises `TypeError` instead of stripping all tools" | confirmé |
| 44 | `AgentSpec` : `model` optionnel, champ `instrument` supprimé, `custom_capability_types` | 2.0 | D:agent-spec.md, D:migration.md, D:capabilities/custom.md | "The spec may omit `model`" | confirmé |
| 45 | Node hooks déclenchés quel que soit le mode de pilotage, sauf dernier nœud sous `run_stream()` | 2.54 (doc) | D:hooks.md | "The final streamed `ModelRequestNode` skips `wrap_node_run` and `after_node_run`" | confirmé |
| 46 | Realtime speech-to-speech `agent.realtime()` | 2.28 | R:2.28.0, D:realtime/overview.md | "Add realtime speech-to-speech support with `Agent.realtime()`" | confirmé |
| 47 | Realtime : `async_tool_call_mode` remplace `supports_async_tool_calls` | 2.52 | R:2.52.0, `pydantic_ai_slim/pydantic_ai/realtime/profiles.py` | "Deprecated: use `async_tool_call_mode` instead" | confirmé |
| 48 | Realtime : `tool_choice` forçant un tool lève `UserError` | 2.51 | R:2.51.0 | "Raise a `UserError` for a realtime `tool_choice` that forces a tool call" | confirmé |
| 49 | Harness : workspaces (`ctx.workspace`, `LocalWorkspace` core, `Coder` / `FileSystem` / `Shell`) | 2.52 | R:2.52.0, D:workspace.md | "Add workspaces: `ctx.workspace` gives tools one API for files and commands" | confirmé |
| 50 | Harness : `SubAgents` sans chargement disque implicite, `inherit_tools` déprécié | 2.52 | R:2.52.0 | "Stop `SubAgents` loading agent files by default, and deprecate `inherit_tools`" | confirmé |
| 51 | Harness : `ModalSandboxBackend` remplace `ModalSandboxSession` | 2.52 | R:2.52.0 | "`ModalSandboxBackend` replaces `ModalSandboxSession`" | confirmé |
| 52 | Harness : `ExaSearch(native=)` / `YouSearch(native=)`, `web_search_tool()` | 2.54 | R:2.54.0 | "Add `native` to `ExaSearch` and `YouSearch` to prefer the model's native web search" | confirmé |
| 53 | Harness : une exception inattendue d'un tool `BackgroundTools` termine le run | 2.54 | R:2.54.0 | "End the run when a `BackgroundTools` tool raises an unexpected exception" | confirmé |
| 54 | `RestateDurability` | — | recherche au tag v2.54.0 | aucune occurrence | non confirmé |
| 55 | Changement de défaut de `ConversationSearch` (`scope='all'` → `'conversation'`) | — | D:harness/conversation-search.md | non daté dans la doc | non confirmé |
| 56 | Chaîne de modèle `xai:...` pour le realtime | — | D:realtime/xai.md | seule l'instanciation directe est documentée | non confirmé |

Non confirmés : #54 introuvable (Restate reste sur `RestateAgent`, #34) ; #55 et #56 laissés hors leçons (la leçon harness cite le défaut actuel sans version, la leçon realtime n'utilise que `XaiRealtimeModel(...)`).

## Écartés

Changements confirmés mais sans valeur pour une leçon (cf. skill lesson-doc § Conventions de format > Chapitres, Valeur avant exhaustivité). Aucun n'est assigné à une leçon.

| # | Changement | Raison |
|---|------------|--------|
| 14 | Hooks de capability `get_model()` / `resolve_model_id()` | Niche : hooks rarement utiles, réservés à l'auteur de capability avancée |
| 18 | `MCPToolset` compatible FastMCP 4 et MCP SDK v2 | Détail de compatibilité de dépendance, sans effet sur le code écrit |
| 37 | UI adapters : `Content-Type` JSON obligatoire | Détail sans enjeu : un client standard envoie déjà du JSON |
| 52 | Harness : `ExaSearch(native=)` / `YouSearch(native=)`, `web_search_tool()` | Niche : option d'un provider de recherche marginal, à laisser à la doc officielle |

## Décisions de structure

| Leçon | Action | Changements | Justification |
|-------|--------|-------------|---------------|
| `fondamentaux-agents` | modifier | #1, #2, #3, #4, #5, #6, #7, #8, #9, #10 | Canonique pour `Agent`, providers, `RunContext`, exécution, `RunUsage` |
| `capabilities-hooks-specs` | modifier | #1, #11, #12, #13, #15, #42, #43, #44, #45 | Canonique pour la primitive capability, les hooks et les Agent Specs |
| `tools-toolsets-mcp` | modifier | #1, #16, #17, #19, #20, #42 | Canonique pour tools, toolsets, native tools, MCP et deferred tools |
| `output-messages-streaming-multimodal` | modifier | #1, #21, #22, #23, #24 | Canonique pour output, streaming et message history ; doublon `RunUsage` retiré (canonique dans fondamentaux-agents) |
| `multi-agent-graphs-durable` | modifier | #1, #9, #25, #26, #27, #28, #29, #30, #31, #32, #33, #34, #35 | Canonique pour délégation, `UsageLimits`, pydantic-graph, durable execution, A2A |
| `harness` | créer | #15, #26, #29, #49, #50, #51, #53 | Package séparé de 50+ capabilities, bloc mental qu'aucune leçon ne porte |
| `interfaces-evals-observabilite` | modifier | #1, #36, #38, #39, #40, #41 | Canonique pour UI adapters, pydantic-evals, Logfire |
| `realtime` | créer | #2, #46, #47, #48 | Domaine voix (5 providers, 3 transports, tours, barge-in) qu'aucune leçon ne porte ; API hors module `beta` |

- **bump seul** : aucun contenu modifié, seule `last_version` change dans l'index
- **supprimer** / **fusionner** : le fichier source n'est retiré qu'après validation explicite, son contenu utile étant d'abord reporté dans la leçon cible

Aucune suppression ni fusion. Écartés : leçon dédiée à pydantic-graph (la doc le réserve aux cas où le flux de contrôle est la difficulté) et leçon dédiée au durable (un chapitre suffit).

---

## Ordre d'exécution recommandé

Ordre complet des leçons de la techno après mise à jour (positionne les leçons créées dans l'index) :

```
1. fondamentaux-agents
2. capabilities-hooks-specs
3. tools-toolsets-mcp
4. output-messages-streaming-multimodal
5. multi-agent-graphs-durable
6. harness                              ← nouvelle
7. interfaces-evals-observabilite
8. realtime                             ← nouvelle
```

---

## Versions cibles

| Techno | Section index | Dossier | Leçons | `last_version` | Notes |
|--------|---------------|---------|--------|----------------|-------|
| `pydanticai` | `python.pydanticai` | `lessons/python/pydanticai/` | toutes sauf `harness` | `"2.54"` | |
| `pydanticai` (harness) | `python.pydanticai` | `lessons/python/pydanticai/` | `harness` | `{core: "2.54", harness: "0.54"}` | harness 0.x aligné sur la mineure du core |

Une ligne par version suivie : une leçon qui suit un outil distinct (cf. skill lesson-doc § Règles leçon > Index) a sa propre ligne, qui la cite dans la colonne Leçons, et garde le cycle de cet outil.

---

## Leçons PydanticAI (techno=pydanticai, last_version="2.54")

Seules les leçons à modifier ou à créer ont une section. La source d'une fusion n'en a pas : la section de sa cible liste les chapitres à reporter.

### 1. fondamentaux-agents

**Action** : modifier

**Changements à appliquer :**
- [#1, #2] Chapitre 1. Installation & Setup V2 : retirer l'avertissement beta et les pins `2.0.0b3`, ajouter la politique de version en `> ℹ️`
- [#3] Chapitre 2. Agent : `retries` surchargeable par run et via `agent.override()`
- [#4, #5] Chapitre 3. Models & Providers : bullet `max_tokens` Anthropic, `> ⚠️` `httpx2.AsyncClient`
- [#6, #7] Chapitre 5. Dependencies & RunContext : champs `ctx.run_id`, `ctx.usage`, `ctx.usage_limits`
- [#8] Chapitre 6. Exécuter un agent : sous-section Annulation (`CancellationToken`, `RunCancelled`, `ctx.cancel()`, annulation externe et `from_cancellation()`)
- [#9, #10] Chapitre 7. RunResult, output & usage : `usage.cost` (`None` si non tarifable), `cache_hit_ratio`

**Points à garder en tête pour le skill :**
- `cost_limit` est canonique dans multi-agent-graphs-durable (renvoi)

---

### 2. capabilities-hooks-specs

**Action** : modifier

**Changements à appliquer :**
- [#1, #15] Chapitre 1 : retrait beta, bullet harness réduite à un renvoi vers la leçon harness ; préciser que seul l'argument constructeur `event_stream_handler=` est supprimé
- [#42] Chapitre 1 : bullet Provider-adaptive alignée (repli local seulement avec `local=`, renvoi tools-toolsets-mcp)
- [#43] Chapitre 2 : signature `PrepareTools` sans `| None`
- [#11, #45] Chapitre 3. Lifecycle hooks : 7 étapes × 4 variantes, ordre `wrap` → `before` → opération → `after` → `wrap`, `> ⚠️` breaking 2.54, portée de `on_*_error`, node hooks et exception `run_stream()`
- [#13] Chapitre 3 : sous-section Événements typés
- [#12] Chapitre 4. Écrire une capability custom : `id` et `combine()`, `> ⚠️` breaking 2.38
- [#44] Chapitre 6. Agent Specs : champs réels (`model` optionnel, sans `instrument`), templating validé contre `deps_type` / `deps_schema`, sous-section Capability custom dans une spec (`custom_capability_types`)

**Points à garder en tête pour le skill :**
- API V1 supprimées (décision user) : bloc de code V1 retiré du chapitre 2, correspondance V1 → V2 gardée en bullets et en notes `> ⚠️` courtes ; les renommages antérieurs à V2 (v0.6 : `result_type`, `.data`) ne sont plus cités

---

### 3. tools-toolsets-mcp

**Action** : modifier

**Changements à appliquer :**
- [#1] Chapitre 1 : retrait beta
- [#16] Chapitre 2 : `ToolFailed` vs `ModelRetry`
- [#42] Chapitre 4. Native Tools : `WebSearch` / `WebFetch` native-only par défaut, `local=` et exemple portable
- [#17] Chapitre 5. MCP : `tool_error_behavior`
- [#19, #20] Chapitre 6 : sous-section Approbation conditionnelle via args_validator, `HandleDeferredToolCalls`

---

### 4. output-messages-streaming-multimodal

**Action** : modifier

**Changements à appliquer :**
- [#1] Chapitre 1 : retrait beta, label `# pydantic-ai 2.54`
- [#21] Chapitre 1 : `output_type=[Foo, Bar, None]`
- [#22] Chapitre 4. Streaming : `run_stream_events()` / `AgentRunEvents`
- Chapitre 5 « Usage & tokens » supprimé (doublon de fondamentaux-agents) → renuméroter
- [#23, #24] Chapitre Message history : sous-section Réparation & historique non fiable, renvois harness (compaction, `StepPersistence`, workspace refs)

---

### 5. multi-agent-graphs-durable

**Action** : modifier

**Changements à appliquer :**
- [#1, #35] Toutes : retrait beta, labels 2.54, `google-gla:` → `google:`
- [#26] Chapitre 1 : `SubAgents` (harness) et critères de la délégation manuelle
- [#9, #27] Chapitre 2 : coût via `usage.cost`, tool délégant `async def`
- [#7, #9, #25] Chapitre 3. UsageLimits : `per_request_input_tokens_limit`, `cost_limit`, `ctx.usage_limits`, portée réelle sur les délégués (`usage_limits=ctx.usage_limits`)
- [#28, #29] Chapitre 5 : réécriture sur `GraphBuilder` (steps, edges, run / iter / render), sous-sections décisions, `.map()`, joins et reducers, `BaseNode` via `g.node()` ; `> ⚠️` suppressions V2
- [#30, #31, #32, #33, #34] Chapitre 6. Durable execution : capabilities `*Durability`, durabilité limitée au conteneur du moteur, unités durables par moteur, restrictions ; `> ⚠️` dépréciation des wrappers et piège Temporal ; `> ℹ️` Restate et `@durable_operation`
- Chapitre 7. A2A : `fasta2a[pydantic-ai]>=0.6.1`

---

### 6. harness

**Action** : créer

```bash
/prof --techno=pydanticai --lecon="Harness" --concepts="pydantic-ai-harness,LocalWorkspace,ctx.workspace,Coder,FileSystem,Shell,sandboxes,SubAgents,Planning,BackgroundTools,Advisor,compaction,TieredCompaction,CodeMode,ToolOutputLimits,Memory,StepPersistence,ConversationSearch,Skills,RepoContext,InputGuardrail,OutputGuardrail,ToolGuardrail,ToolCallJudge,TrajectoryJudge,SpendLimits,PromptInjectionDefender,ExaSearch,YouSearch"
```

**Points à garder en tête pour le skill :**
- **Positionnement** : core suffit pour un agent simple, harness pour un agent qui touche des fichiers, exécute du code, se souvient, délègue ou tient des runs longs (#15)
- **Install** : package séparé, épinglé en `==` sur `pydantic-ai-slim` de même mineure, versionnage 0.x (#15)
- **Workspaces** : `LocalWorkspace` / `ctx.workspace` sont du core, `Coder` / `FileSystem` / `Shell` et sandboxes du harness ; `LocalWorkspace` n'est pas une sandbox (#49, #51)
- **SubAgents** : `delegate_task`, deps et usage forwardés, plus de chargement disque implicite, `inherit_tools` déprécié (#26, #50)
- **Compaction** : `TieredCompaction` par défaut recommandé, `ProcessHistory` reste la voie core (renvoi capabilities-hooks-specs)
- **StepPersistence** : remplace `pydantic_graph.persistence` côté agent runs, complète la durable execution sans la remplacer (#29)
- **BackgroundTools** : une exception inattendue termine le run (#53)

---

### 7. interfaces-evals-observabilite

**Action** : modifier

**Changements à appliquer :**
- [#1] Chapitre 1 : retrait beta, label 2.54
- [#36, #38] Chapitre 2. Interfaces frontend : `sdk_version`, `on_cancel`, `> ⚠️` sécurité des adapters
- [#39] Chapitre 3. Evals : `GEval`, evaluators agentiques
- [#40, #41] Chapitre 5. Logfire : versions d'instrumentation (v5 défaut, v6 opt-in, v2 à v4 dépréciées), portée de `include_content=False`

---

### 8. realtime

**Action** : créer

```bash
/prof --techno=pydanticai --lecon="Realtime" --concepts="agent.realtime,AgentRealtime,RealtimeSession,session(),providers realtime,OpenAIRealtimeModel,OpenAILiveModel,GoogleRealtimeModel,PCM16,send_audio,stream_audio,wait_for_playback,stream_transcripts,turn detection,barge-in,handle_barge_in,interrupt,push-to-talk,send(respond=),async_tool_call_mode,enqueue,WebSocket relay,WebRTC sideband,ReconnectPolicy,RealtimeError"
```

**Points à garder en tête pour le skill :**
- **Statut** : module hors `beta`, couvert par la politique de version (#2) ; dater la leçon en 2.54, ne pas figer de liste de modèles (#46)
- **Tools** : `async_tool_call_mode` (#47) ; `tool_choice` forçant un tool → `UserError` (#48)
- **Transports** : WebRTC sideband réservé à OpenAI / Azure (hors Azure Voice Live)
- Renvois : `UsageLimits` (multi-agent-graphs-durable), `RunUsage.cost` (fondamentaux-agents), Logfire (interfaces-evals-observabilite)

---

## Matrice concept → leçon canonique

Concepts touchés par la mise à jour et partagés entre plusieurs leçons :

| Concept | Canonique dans | Mentionné aussi dans |
|---------|----------------|----------------------|
| `RunUsage`, `usage.cost` | `fondamentaux-agents` | `multi-agent-graphs-durable`, `realtime` (renvoi) |
| `RunCancelled`, annulation | `fondamentaux-agents` | `output-messages-streaming-multimodal`, `realtime` (renvoi) |
| `UsageLimits`, `cost_limit` | `multi-agent-graphs-durable` | `fondamentaux-agents`, `tools-toolsets-mcp`, `realtime` (renvoi) |
| `WebSearch` / `WebFetch`, `local=` | `tools-toolsets-mcp` | `capabilities-hooks-specs`, `harness` (renvoi) |
| lifecycle hooks, `@agent.on_event` | `capabilities-hooks-specs` | `harness`, `realtime` (renvoi) |
| `ProcessHistory` | `capabilities-hooks-specs` | `output-messages-streaming-multimodal`, `harness` (renvoi) |
| deferred tools, `HandleDeferredToolCalls` | `tools-toolsets-mcp` | `realtime` (renvoi) |
| `sanitize_messages`, message history | `output-messages-streaming-multimodal` | `interfaces-evals-observabilite`, `realtime` (renvoi) |
| `SubAgents`, compaction, `StepPersistence`, workspaces | `harness` | `multi-agent-graphs-durable`, `output-messages-streaming-multimodal`, `capabilities-hooks-specs` (renvoi) |
| délégation manuelle, durable execution | `multi-agent-graphs-durable` | `harness` (renvoi) |
| Logfire, `InstrumentationSettings` | `interfaces-evals-observabilite` | `realtime` (renvoi) |

---

## Dépréciations et breaking changes critiques à signaler

| Ancien | Nouveau | Version | Leçon impactée |
|--------|---------|---------|----------------|
| `httpx.AsyncClient` passé à `AnthropicProvider` | `httpx2.AsyncClient` | 2.33 | `fondamentaux-agents` |
| `wrap_*` n'enveloppant que l'opération | `wrap_*` enveloppe `before_*` / opération / `after_*` | 2.54 | `capabilities-hooks-specs` |
| capabilities répétées coexistant (ids `_2`) | fusion par `id` par défaut + `combine()` | 2.38 | `capabilities-hooks-specs` |
| `PrepareTools` retournant `None` | retourner `[]` (`None` lève `TypeError`) | 2.0 | `capabilities-hooks-specs` |
| `Graph(nodes=[...])`, `pydantic_graph.beta.GraphBuilder` | `pydantic_graph.GraphBuilder` | 2.0 | `multi-agent-graphs-durable` |
| `pydantic_graph.persistence`, `pydantic_graph.mermaid` | `StepPersistence` (harness) / durable execution, `Graph.render()` | 2.0 | `multi-agent-graphs-durable` |
| `TemporalAgent`, `DBOSAgent`, `PrefectAgent` | `TemporalDurability`, `DBOSDurability`, `PrefectDurability` (retrait v3) | 2.14 | `multi-agent-graphs-durable` |
| préfixe `google-gla:` | `google:` | 2.0 | `multi-agent-graphs-durable` |
| `preserve_file_data` (sécurité entrante) | `allow_uploaded_files` | 2.4 | `interfaces-evals-observabilite` |
| instrumentation v2 à v4 | v5 (défaut) ou v6 | 2.32 | `interfaces-evals-observabilite` |
| `SubAgents` chargeant les agents depuis le disque, `inherit_tools=True` | `agent_folders='agents'`, `include_self=True` / `tool_resolver` | 2.52 | `harness` |
| `ModalSandboxSession` | `ModalSandboxBackend` | 2.52 | `harness` |
| `RealtimeModelProfile.supports_async_tool_calls` | `async_tool_call_mode` | 2.52 | `realtime` |
| `tool_choice` forçant un tool en realtime | `UserError` sur OpenAI / Azure / xAI | 2.51 | `realtime` |
