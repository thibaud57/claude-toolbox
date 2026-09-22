# Plan pédagogique : Leçons React & Next.js

## Contexte

Création de fiches de révision denses (format skill `prof`) pour développeurs mid/senior, basées sur le cours Udemy "Next.js 15 & React - The Complete Guide" (2025), enrichies par 4 recherches parallèles couvrant l'état de l'écosystème en avril 2026, puis consolidées après audit critique.

**Le cours Udemy compte 23 sections, dont seules les sections 1 à 10 (App Router moderne) sont retenues.** Les sections 11 à 23 (Pages Router legacy) sont ignorées.

### Décisions de cadrage validées

- Découpage **thématique** par concept technique, cohérent avec les leçons Angular existantes (`routing-navigation`, `services-pipes-directives`, `deploiement-csr-ssr-ssg`...)
- **2 leçons React** (refresher mid/senior) + **13 leçons Next.js**
- Chaque leçon = un bloc mental cohérent que le dev doit maîtriser ensemble
- **Fusion `caching` + `rendering-strategies` → `rendering-caching`** (en Next 16, PPR est absorbé dans Cache Components, les deux modèles convergent, modèle Angular `deploiement-csr-ssr-ssg`)
- **Séparation `routing-navigation` + `api-middleware`** : routing frontend (UI/layouts) vs HTTP layer (handlers + middleware réseau). Les deux modèles mentaux sont distincts et les fusionner donnerait une leçon trop dense
- **`authentication` positionnée #9 (après mutations)** car elle utilise Server Actions, cookies async et middleware
- **`authentication` élaguée** : focus Better Auth + patterns pragmatiques (utilisateur gère l'auth plutôt côté backend habituellement), retrait de MCP/SSO/SAML/rate limiting détaillé

### État de l'écosystème (avril 2026)

- **Next.js 16.2.x** stable, Turbopack par défaut (dev + build)
- **React 19.2.5**, React Compiler v1.0 stable
- **Lucia Auth déprécié**, **Better Auth 1.6.x** = recommandation 2026
- **Tailwind CSS v4**, **shadcn/ui v4 CLI**, **Vercel Fluid Compute**

**Technos cibles :**
- `react` : 2 leçons, `last_version: "19.2"`
- `nextjs` : 13 leçons, `last_version: "16.2"`

---

## Ordre d'exécution recommandé

```
React (refresher)
├── 1. bases-react
└── 2. hooks-modernes-react-19          ← React 19.x + React Compiler

Next.js Core
├── 3. cli-configuration                ← CLI, Turbopack, next.config.ts
├── 4. server-client-components         ← RSC, 'use client', Taint API
├── 5. routing-navigation               ← file-based, parallel, intercepting, View Transitions
├── 6. api-middleware                   ← route handlers + proxy.ts + streaming
├── 7. data-fetching                    ← fetch RSC, use(), Prisma/Drizzle, async APIs
├── 8. mutations-server-actions         ← useActionState, useOptimistic, updateTag, refresh
├── 9. authentification                 ← ⬆ Better Auth + patterns pragmatiques
└── 10. rendering-caching               ← ⬆ FUSION 4 cache layers + Cache Components + SSG/SSR/ISR/PPR

Next.js Transverses
├── 11. images-fonts                    ← next/image, next/font (Next 16 restrictions)
├── 12. metadata-seo                    ← Metadata API + Document metadata natif
├── 13. internationalisation            ← next-intl
├── 14. tests                           ← Vitest, MSW, Playwright (pyramide)
└── 15. deploiement-production          ← Vercel Fluid Compute, self-hosting, Sentry
```

**Pourquoi cet ordre :**
- React d'abord (refresher hooks R19 qui servent dans toutes les leçons Next.js)
- `cli-configuration` → `server-client-components` : modèle mental fondamental avant de toucher au routing
- `routing-navigation` → `api-middleware` : d'abord l'UI/navigation user-facing, ensuite le HTTP layer
- `data-fetching` → `mutations-server-actions` → `authentification` : flux read → write → protection (auth utilise les actions + middleware vus juste avant)
- `rendering-caching` après auth : on optimise une fois que les features fonctionnent
- Transverses (images, metadata, i18n, tests) en fin de parcours features
- `deploiement-production` en dernier (passage en prod)

---

## Leçons React (techno=react, last_version="19.2")

### 1. bases-react

```bash
/prof --techno=react --lecon="Bases React" --concepts="JSX,composants fonctionnels,props,children,useState,events,event handlers,conditional rendering,listes et keys,formulaires contrôlés,formulaires non contrôlés,lifting state up,CSS Modules,component composition,fragments,key prop pièges,createRoot,hydrateRoot,form action key reset pattern,StrictMode double render"
```

**Points à garder en tête pour le skill :**
- Cibler mid/senior : pas d'explications triviales, focus pièges et "pourquoi"
- **Pas de class components** (hors scope moderne), **pas de `PropTypes`** (supprimé R19), **pas de `defaultProps`** sur function components (supprimé R19)
- `ReactDOM.render`/`hydrate`/`findDOMNode` **supprimés** R19 → `createRoot`/`hydrateRoot`/refs
- Pièges critiques : key prop mauvaise (re-mount), state initialization dans render, événements synthétiques
- **Strict Mode** : double render en dev, double mount Effects, double ref callback (nouveau R19)
- Controlled vs uncontrolled inputs : perf tradeoffs, quand utiliser `useRef` à la place
- **Pattern `<form action>` reset via key prop** : changer la `key` du form pour le reset après succès
- Langue : noms en backticks, français pour labels conceptuels

---

### 2. hooks-modernes-react-19

```bash
/prof --techno=react --lecon="Hooks Modernes & React 19" --concepts="useEffect,cleanup,dependency array,useContext,useRef,useMemo,useCallback,useReducer,custom hooks,use,useActionState,useOptimistic,useFormStatus,useTransition,useTransition async,useDeferredValue,useDeferredValue initialValue,useEffectEvent,useId,useSyncExternalStore,Actions,Activity component,ref as prop,Context value prop,element.props.ref,React Compiler,babel-plugin-react-compiler,eslint-plugin-react-hooks v6,preload,preinit,preconnect,prefetchDNS,Document metadata,stylesheet precedence,captureOwnerStack,forwardRef deprecated"
```

**Points à garder en tête pour le skill :**
- **`use()` hook** : unwrap Promise ou Context, utilisable **conditionnellement** (unique parmi les hooks)
- **`useActionState`** : remplace `useFormState` (déprécié), import depuis `react` (pas `react-dom`), retourne `[state, dispatchFn, isPending]`
- **`useOptimistic`** : updates optimistes avec rollback auto, pattern avec Server Actions
- **`useFormStatus`** : DOIT être dans un composant ENFANT du form (pas directement dans le form parent)
- **`useTransition` avec async function** = pattern "Action" : gestion auto de `isPending`, erreurs remontent à ErrorBoundary. Piège : les `setState` dans l'async sont batchés différemment
- **`useEffectEvent`** (R19.2) : extraire la logique non-réactive d'un Effect, **ne PAS inclure dans les deps**
- **`useDeferredValue(value, initialValue)`** : nouveau second argument pour valeur au premier render
- **`useId`** : préfixe `_r_` (R19.2) pour compatibilité `view-transition-name` et XML 1.0
- **React Compiler v1.0 stable** (oct 2025) : memoïsation auto, élimine besoin de `useMemo`/`useCallback` manuels, compile-time, Babel plugin, compile times plus élevés en dev
- **`eslint-plugin-react-hooks` v6** intégré avec règles Compiler
- **`<Context value={...}>`** remplace `<Context.Provider value={...}>` (déprécié)
- **Ref as prop** : plus besoin de `forwardRef` pour function components
- **Ref callback cleanup** : retourner une fonction de cleanup (TypeScript impose expression bloc `{ return () => {} }`)
- **`element.ref` déprécié** → `element.props.ref`
- **Resource preloading** depuis `react-dom` : `preload`, `preinit`, `preconnect`, `prefetchDNS`
- **Document metadata natif** : `<title>`, `<meta>`, `<link>` hoistés dans `<head>` automatiquement
- **Stylesheet natif** : `<link rel="stylesheet" precedence="...">` avec dedup auto
- **`<script async>`** dédupliqué automatiquement
- **`captureOwnerStack()`** (R19.1) dev-only pour debug
- **`<Activity mode="visible|hidden">`** (R19.2) : composant pour masquer/restaurer une UI avec son état interne préservé. Mode `hidden` : effects démontés, updates différées. Remplace les patterns `display: none` manuels. Utilisé par Next.js 16 en interne pour préserver l'état pendant navigation

---

## Leçons Next.js (techno=nextjs, last_version="16.2")

### 3. cli-configuration

```bash
/prof --techno=nextjs --lecon="CLI & Configuration" --concepts="create-next-app,project structure,app directory,src directory,page.tsx,layout.tsx,next.config.ts,NextConfig type,next dev,next build,next start,Turbopack default,next lint removed,ESLint Biome,tsconfig paths,environment variables,.env files,NEXT_PUBLIC_ prefix,build-time vs runtime env,t3-oss env-nextjs,basePath,assetPrefix,rewrites,redirects,Static Route Indicator,App Router vs Pages Router,Node 20.9 minimum,TypeScript 5.1 minimum,next upgrade command,next typegen,Typed Routes config,Turbopack File System Caching,reactCompiler config"
```

**Points à garder en tête pour le skill :**
- **`next.config.ts`** : TypeScript natif Next 15, type `NextConfig` depuis `next`
- **Turbopack = défaut** en Next 16 (dev + build). Plus besoin de flag, revenir à webpack via `--webpack`
- **Turbopack File System Caching** stable en 16.1 (5-14x plus rapide au redémarrage)
- **`next lint` supprimé** (Next 16) → ESLint CLI direct ou **Biome**
- **Node 20.9+** et **TypeScript 5.1+** obligatoires
- **`next upgrade`** (16.1) : mise à jour simplifiée
- **`next typegen`** (15.5) + **`typedRoutes: true`** : vérification compile-time des `<Link href>`
- **Static Route Indicator** (Next 15) : badge dev signalant static vs dynamic
- **`@t3-oss/env-nextjs`** + Zod : pattern standard 2026 pour validation env au build (bloque build si invalide)
- **`basePath`, `assetPrefix`** : déploiement sous sous-chemin/CDN
- **`rewrites` et `redirects` statiques** dans `next.config.ts` (distincts des Server redirects runtime)
- **`reactCompiler: true`** pour activer React Compiler (opt-in, non activé par défaut)
- **Env vars** : `.env.local` gitignoré par défaut, `NEXT_PUBLIC_` inlined au build, server vars résolues runtime
- **`serverRuntimeConfig`/`publicRuntimeConfig` supprimés** Next 16 : utiliser env vars
- Structure type : `src/app/` + `src/components/` + `src/lib/` + `src/env.ts`
- App Router vs Pages Router : expliquer brièvement pourquoi App Router en 2026

---

### 4. server-client-components

```bash
/prof --techno=nextjs --lecon="Server & Client Components" --concepts="React Server Components,Client Components,use client,use server,server-only,client-only,composition patterns,passing server components as children,props serialization rules,async components,hooks interdits dans RSC,context interdit dans RSC,boundary client-server,interleaving,leaf client component pattern,import boundaries,experimental_taintObjectReference,experimental_taintUniqueValue,taint API,secret values protection,Suspense boundaries,direct database access,RSC payload,React Server DOM"
```

**Points à garder en tête pour le skill :**
- **Règles de sérialisation** Server → Client : Date/Map/Set OK, functions NON (sauf Server Actions)
- **Pattern critique** : passer un RSC en `children` d'un Client Component pour maintenir le RSC côté serveur
- **`'use client'`** est un **boundary** : tous les imports descendants deviennent client (sauf ceux passés en `children`)
- **`server-only`** et **`client-only`** packages : garde-fous import-time
- **Async Server Components** : `async function Page()`, `await` directement dans le render
- **Hooks React interdits dans RSC** : `useState`, `useEffect`, `useRef`, `useContext` ne fonctionnent pas côté serveur
- **Context** ne traverse pas la frontière RSC (pas de runtime React serveur global)
- **Pattern leaf client** : pousser `'use client'` le plus bas possible
- **`'use server'` différent** : marque des Server Actions (fonctions), pas des Client Components (fichier)
- **Direct DB access** : Prisma/Drizzle directement dans Server Components (pas besoin de layer API)
- **⚠️ Taint API (experimental mais recommandé)** : `experimental_taintObjectReference(message, object)` et `experimental_taintUniqueValue(message, lifetime, value)` pour empêcher qu'un objet ou une valeur (ex : token, password hash, user object complet) traverse la frontière RSC → Client. Lève une erreur au runtime si le taint est violé. Activer via `experimental.taint: true` dans config
- Protection secrets : les valeurs serveur (env sans `NEXT_PUBLIC_`) ne doivent JAMAIS être passées en props à un Client Component
- RSC payload : format sérialisé streamé du serveur vers le client pour reconstituer l'arbre RSC (interne mais utile de savoir que ça existe)

---

### 5. routing-navigation

```bash
/prof --techno=nextjs --lecon="Routing & Navigation" --concepts="file-based routing,app directory,page.tsx,layout.tsx,template.tsx,loading.tsx,error.tsx,not-found.tsx,global-error.tsx,global-not-found.tsx,unauthorized.tsx,forbidden.tsx,dynamic segments,catch-all segments,optional catch-all,route groups,parallel routes,slot convention,default.js obligatoire,intercepting routes,Link component,prefetch,incremental prefetching,useRouter,usePathname,useSearchParams,useSearchParams Suspense wrap,useLinkStatus,redirect,permanentRedirect,notFound,unauthorized,forbidden,unstable_rethrow,connection,params async,searchParams async,Typed Routes,ViewTransition,transitionTypes,navigation programmatique,active links,nested layouts,metadata colocation,generateStaticParams,layout deduplication"
```

**Points à garder en tête pour le skill :**
- **Breaking change Next 15** : `params` et `searchParams` sont **async** (Promise), `await params` obligatoire. En Next 16 : **hard error** si accès sync
- **File conventions** : `page.tsx`, `layout.tsx` (persiste entre navs), `template.tsx` (re-mount à chaque nav), `loading.tsx`, `error.tsx`, `not-found.tsx`, `global-error.tsx`, **`global-not-found.tsx`** (catch-all not found), **`unauthorized.tsx`** (Next 15.1+), **`forbidden.tsx`** (Next 15.1+)
- **`global-error.tsx`** DOIT inclure `<html>` et `<body>` (remplace le root layout en cas d'erreur)
- **`error.tsx`** est forcément Client Component (`'use client'`), reçoit `error` + `reset` props. `reset()` pour retry sans refresh de la page
- **⚠️ `useSearchParams` Suspense piège critique** : force le bailout client rendering de toute la route si pas wrapé. Sur pages statiques, DOIT être wrappé dans `<Suspense>` sinon erreur au build
- **`unauthorized()` / `forbidden()`** (Next 15.1+) : jettent des erreurs 401/403 consommées par `unauthorized.tsx`/`forbidden.tsx`. Pendant sémantique de `notFound()` pour les cas auth
- **`unstable_rethrow()`** : quand on wrap `notFound()`/`redirect()`/`unauthorized()` dans try/catch, il faut re-throw les erreurs spéciales de Next pour qu'elles soient catchées par la convention, sinon elles sont silencieusement avalées
- **Dynamic routes** : `[slug]`, catch-all `[...slug]`, optional `[[...slug]]`
- **Route groups** `(group)` : organisent sans affecter l'URL, peuvent avoir leur propre layout
- **Parallel routes `@slot` folders** : rendus simultanément dans un layout, **`default.js` OBLIGATOIRE** Next 16 (sinon build échoue)
- **Intercepting routes** : `(.)`, `(..)`, `(...)`, pattern modal overlay classique combiné avec parallel routes
- **`Link`** : prefetching automatique, `prefetch={false}`, `scroll`, `replace`
- **Incremental prefetching** (Next 16) : prefetch progressif des segments
- **`useLinkStatus`** hook (Next 15.3+) : état pending d'un `<Link>` pour afficher loading state par lien
- **`<ViewTransition>`** (React 19.2) : animations natives entre routes, combiné avec **`transitionTypes`** prop sur `<Link>` (Next 16.2)
- **Navigation client** : `useRouter`, `usePathname`, `useSearchParams` (Client Components only)
- **Navigation server** : `redirect()`, `permanentRedirect()`, `notFound()`, `unauthorized()`, `forbidden()` (jettent, à utiliser HORS try/catch ou avec `unstable_rethrow`)
- **`connection()`** : remplace `unstable_noStore()` (Next 15), force le rendu dynamique sans lire request data
- **Typed Routes** (activé dans `cli-configuration`) : `import type { Route } from 'next'` pour `<Link href>` type-safe
- **Layout deduplication** (Next 16) : optimisation automatique

---

### 6. api-middleware

```bash
/prof --techno=nextjs --lecon="API & Middleware" --concepts="route handlers,route.ts,GET POST PUT DELETE PATCH OPTIONS HEAD,NextRequest,NextResponse,streaming responses,ReadableStream,Server-Sent Events,SSE,CORS,revalidate export route handler,dynamic export route handler,runtime export,proxy.ts,middleware.ts deprecated,middleware matcher,matcher source,matcher missing,matcher has,matcher regex,Node.js runtime middleware,edge runtime middleware,cookies en middleware,headers en middleware,rewrite,redirect middleware,serverActions allowedOrigins,GET handler uncached par défaut,request.formData,request.json,adapters API"
```

**Points à garder en tête pour le skill :**
- **Route handlers `route.ts`** : remplacent API routes du Pages Router, export par méthode HTTP (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)
- **Breaking change Next 15** : GET Route Handlers **ne sont plus cachés par défaut**, opt-in avec `cache: 'force-cache'` ou `'use cache'` (Next 16)
- **`NextRequest`** : extends `Request`, ajoute `.cookies`, `.nextUrl`, `.geo`, `.ip`
- **`NextResponse`** : `.next()`, `.redirect()`, `.rewrite()`, `.json()`, cookies/headers manipulation
- **Pas de body parsing automatique** : `await request.json()`, `await request.formData()`, `await request.text()`
- **Streaming responses** : retourner un `Response` avec `ReadableStream` pour chunked transfer
- **Server-Sent Events (SSE)** : pattern avec `ReadableStream` + `text/event-stream` content-type pour push server → client
- **`export const revalidate = 60`** et **`export const dynamic = 'force-dynamic'`** dans route handlers (route segment config)
- **`export const runtime = 'edge' | 'nodejs'`** pour choisir le runtime par handler
- **CORS** : à gérer manuellement dans route handlers (pas de config globale), pattern `NextResponse` avec headers
- **⚠️ `middleware.ts` déprécié Next 16** → **`proxy.ts`** avec export `proxy` au lieu de `middleware`
- **`proxy.ts`** tourne sur **Node.js runtime par défaut** (Edge était le seul runtime avant)
- **`middleware.ts` encore supporté** en Edge runtime avec warnings de dépréciation
- **Node.js runtime middleware** stable Next 15.5 : `export const config = { runtime: 'nodejs' }`
- **Matcher config CRITIQUE** : sinon middleware s'exécute sur TOUTES les routes (y compris `_next/static`, assets)
- **Matcher regex avancé** : `{ source: '/:path*', missing: [{ type: 'header', key: 'next-action' }], has: [{ type: 'cookie', key: 'session' }] }`
- **Exclusion standard** : `'/((?!api|_next/static|_next/image|favicon.ico).*)'`
- **Ne pas faire d'appel DB dans middleware edge** : limitations runtime
- **Cas d'usage middleware/proxy** : auth redirect, i18n locale, A/B testing, rewrite, header injection, geolocation routing, bot detection
- **`serverActions.allowedOrigins`** dans `next.config.ts` pour reverse proxy (CSRF)
- **Adapters API** stable Next 16.2 : personnalisation du build pour plateformes de déploiement

---

### 7. data-fetching

```bash
/prof --techno=nextjs --lecon="Data Fetching" --concepts="fetch en Server Components,async page components,cookies async,headers async,draftMode async,draft mode preview CMS,Suspense,streaming,loading.tsx,parallel data fetching,sequential data fetching,preloading pattern,Promise.all parallel,request memoization,cache fonction React,use hook,SWR,TanStack Query,client-side fetching,error handling,notFound,unstable_rethrow,connection,force-dynamic,force-static,dynamic functions,Prisma singleton,connection_limit serverless,Prisma Accelerate,Drizzle,Drizzle Edge,connection pooling,Neon,PlanetScale,Supabase,direct DB access,preload preinit preconnect prefetchDNS,after,waterfall detection"
```

**Points à garder en tête pour le skill :**
- **Breaking change Next 15** : `fetch()` n'est PLUS caché par défaut, opt-in via `cache: 'force-cache'` (approfondi dans `rendering-caching`)
- **Breaking change Next 15** : `cookies()`, `headers()`, `draftMode()` sont **async** (Promise), `await` obligatoire
- **Async Server Components** : `async function Page()` avec `await` directement
- **Request Memoization** (React cache, per-request, auto pour `fetch()`) vs **Data Cache** (persistent, couvert en détail dans `rendering-caching`)
- **`cache()` de React** : mémoïsation per-request pour fonctions custom (DB queries)
- **Pattern `preload()`** : fonction exportée qui kick off le fetch en amont (hors render) pour éviter waterfalls
- **Parallel vs sequential fetching** : `Promise.all([fetch1, fetch2])` pour parallèle, détecter les waterfalls accidentelles
- **Streaming avec Suspense** : granulaire, fallback par zone indépendante
- **`use()` hook** : unwrap Promise dans Client Component pour du fetching déclaratif
- **DB direct depuis Server Components** : plus besoin de layer API/REST intermédiaire
- **Prisma patterns** : singleton global (`globalThis.prisma`) pour éviter pool exhaustion en dev, **`connection_limit=1`** en serverless, **Prisma Accelerate** pour Edge Runtime (proxy de connexion)
- **Drizzle patterns** : 30-40% plus rapide que Prisma, **Edge native** (pas de singleton nécessaire), instanciation module-level
- **Connection pooling** : **Neon** (serverless natif, Edge-compatible), **PlanetScale**, **Supabase** (PgBouncer exposé), **PgBouncer** self-hosted
- **⚠️ ATTENTION** : Prisma/Drizzle queries **ne participent PAS** au Data Cache Next.js → wrapper avec `'use cache'` (Next 16) ou `cache()` React
- **Resource preloading** : `preload`, `preinit`, `preconnect`, `prefetchDNS` depuis `react-dom` pour ressources externes critiques
- **`after()` stable** Next 15.1 : exécuter code après réponse streamée (analytics, logs non bloquants)
- **`connection()`** pour forcer dynamic rendering sans lire cookies/headers
- **`unstable_rethrow()`** : dans try/catch qui pourrait avaler `notFound()` / `redirect()`, rethrow pour que la convention Next catche
- **`draftMode()`** : preview mode pour CMS headless, active un cookie qui désactive le cache data pour voir le contenu non publié. Pattern : route handler enable/disable + consommation avec `(await draftMode()).isEnabled`
- **SWR vs TanStack Query** : pour client fetching avec refetch auto, stale-while-revalidate côté client, alternative au pattern `use()` + Server Component

---

### 8. mutations-server-actions

```bash
/prof --techno=nextjs --lecon="Mutations & Server Actions" --concepts="Server Actions,use server,inline actions,external actions,form action prop,formAction prop,useActionState,useFormStatus,useOptimistic,progressive enhancement,FormData,Zod validation,revalidatePath,revalidateTag new signature,updateTag,refresh,read-your-writes,redirect dans action,cookies mutations,file uploads,XSS protection,sanitization,next/form,startTransition async,bind arguments,error handling,CSRF auto protection,Origin Host check,cacheLife profile in revalidateTag"
```

**Points à garder en tête pour le skill :**
- **`useActionState`** remplace `useFormState` (déprécié). Import depuis `react`. Retourne `[state, dispatchFn, isPending]`
- **`useFormStatus`** : dans composant ENFANT du form, pas dans le form directement. Expose `pending`, `data`, `method`, `action`
- **`useOptimistic`** : updates optimistes avec rollback auto à la résolution
- **`'use server'`** : en haut de fichier (toutes exports = actions) OU inline dans RSC
- **Actions appelables** : via `<form action={}>`, via `formAction` sur `<button>`, via `startTransition`, directement (button `onClick` dans Client Component)
- **`bind()`** : passer arguments supplémentaires aux actions (alternative aux hidden inputs)
- **⚠️ Breaking Next 16** : `revalidateTag(tag, profile)` requiert **SECOND argument `cacheLife` profile** (ex `'max'`, `'days'`). Signature 1-arg dépréciée
- **Next 16 nouvelles APIs** : **`updateTag(tag)`** et **`refresh()`** avec sémantique **read-your-writes** (cache coherence immédiate après mutation). Différent de `revalidateTag` qui est lazy/background
- **CSRF auto-protection** Server Actions : (1) POST only, (2) comparaison `Origin` vs `Host` header. Pas de token CSRF explicite nécessaire
- **`serverActions.allowedOrigins`** dans `next.config.ts` pour reverse proxy setups
- **`next/form`** (Next 15) : component pour navigation client-side + prefetching + progressive enhancement pour formulaires de navigation (search bar, filters)
- **⚠️ `redirect()` dans action DOIT être HORS try/catch** (ou utiliser `unstable_rethrow` dans le catch), sinon catché silencieusement
- **Zod validation** côté serveur obligatoire pour tout input user
- **Sanitization XSS** : échapper les contenus user-generated avant storage ou render dangereux
- **File uploads** via `FormData` et stockage externe (S3, Cloudinary, Vercel Blob), JAMAIS sur filesystem en production
- **Progressive enhancement** : le form fonctionne sans JS si action externe et sans state complexe
- **Error handling** : erreurs non catchées remontent à `error.tsx` ou React `ErrorBoundary`
- **`startTransition` avec async function** = automatic pending state tracking
- **Cookies mutations** : `(await cookies()).set(...)` dans Server Actions

---

### 9. authentification

```bash
/prof --techno=nextjs --lecon="Authentification" --concepts="Better Auth,Lucia deprecated,Auth.js v5 maintenance,Clerk mention,password hashing,Argon2id,OWASP 2026,bcrypt legacy,jose,iron-session,session-based auth,JWT stateless,HTTP-only cookies,Secure cookies,SameSite Lax,cookies API async,proxy.ts auth protection,middleware matcher auth,route protection,auth layouts,RBAC,permissions,unauthorized,forbidden,CSRF Server Actions,Origin Host check,rotation session,email verification,OAuth providers,experimental_taintUniqueValue,Server Actions auth patterns,getCurrentUser helper"
```

**Points à garder en tête pour le skill :**
- **⚠️ Lucia deprecated mars 2025** (annonce GitHub #1714). NE PAS recommander, mentionner le statut historique
- **Better Auth 1.6.x = référence 2026** (l'équipe Auth.js a rejoint Better Auth en sept 2025, Auth.js en mode maintenance)
- **Better Auth features clés** : TypeScript-first, sessions DB, credentials + OAuth (50+ providers), 2FA, Passkeys (WebAuthn), Magic Links, plugin ecosystem, Edge Native
- **Auth.js v5 beta perpétuelle** : mentionner en 1 ligne (mode maintenance sécurité uniquement)
- **Clerk** : mention rapide en 1 ligne (SaaS avec UI pré-construite, lock-in mais zéro friction)
- **Context pragmatique** : utilisateur gère souvent l'auth côté backend (Spring Security, NestJS). Côté Next.js, focus sur :
  1. Consommer une auth externe (stocker JWT/session en cookie HTTP-only, vérifier au milieu)
  2. Protéger des routes via middleware/proxy.ts
  3. Sécuriser Server Actions (CSRF auto + user check)
  4. Better Auth pour le cas full-stack Next.js
- **Password hashing OWASP 2026** : **Argon2id** recommandé (19-128 MiB mémoire, 2-5 iterations), bcrypt legacy acceptable (cost 13-14) pour migrations
- **`jose`** : librairie JWT Edge-compatible (vs `jsonwebtoken` qui est Node-only)
- **`iron-session`** : sessions chiffrées stateless (alternative à DB sessions)
- **Cookies** : **`HttpOnly`** (anti-XSS), **`Secure`** (HTTPS only), **`SameSite=Lax`** (anti-CSRF par défaut), `Strict` si pas de cross-site legitimate
- **`cookies()` async** (Next 15) : `const cookieStore = await cookies()` pour set/get/delete
- **Protection routes** : `proxy.ts` (Next 16) ou `middleware.ts` avec matcher config (early redirect pour performance), ne PAS faire de DB call en middleware edge (limitations runtime)
- **Server-side route protection dans layouts** : check auth synchrone pour protéger un segment entier
- **RBAC** : rôles en session + helper `requireRole(role)`, check au niveau action + route
- **`unauthorized()` / `forbidden()`** (Next 15.1+) : pendants de `notFound()` pour auth. Consommés par `unauthorized.tsx`/`forbidden.tsx`
- **CSRF auto-protection Server Actions** : POST only + `Origin` vs `Host` check. `serverActions.allowedOrigins` pour reverse proxy
- **Rotation de session** : générer nouveau session ID après login (anti-session fixation) et après élévation de privilèges
- **Email verification** : token opaque (pas JWT), DB storage, expiry 15-30 min, usage unique, supprimé après vérif. Jamais révéler si email existe
- **OAuth providers** via Better Auth : Google, GitHub, Apple, Discord, Microsoft, etc.
- **`experimental_taintUniqueValue(message, lifetime, passwordHash)`** : empêcher qu'un hash password, token secret, session ID traverse vers un Client Component
- **Pattern `getCurrentUser()` helper** réutilisable : wrap `cookies()` + session verify, utilisé dans layouts/actions/route handlers

---

### 10. rendering-caching

```bash
/prof --techno=nextjs --lecon="Rendering & Caching" --concepts="static rendering,dynamic rendering,streaming,Request Memoization,Data Cache,Full Route Cache,Router Cache,4 layers cache,fetch cache options,force-cache,no-store,next.revalidate,next.tags,cache function React,revalidatePath,revalidateTag new signature,updateTag,refresh,unstable_cache deprecated,use cache directive,cacheLife,cacheTag,cacheComponents config,cacheSignal,staleTimes config,stale-while-revalidate,on-demand revalidation,time-based revalidation,cache poisoning,generateStaticParams,dynamicParams,Suspense boundaries,loading.tsx,SSG,SSR,ISR,Partial Prerendering,PPR absorbé Cache Components,force-static,force-dynamic,route segment config,runtime export,fetchCache export,dynamic export,preferredRegion,build output analysis,edge runtime,nodejs runtime,dynamic functions,connection"
```

**Points à garder en tête pour le skill :**
- **Fusion justifiée** : en Next 16, Cache Components absorbe PPR, le modèle de cache DÉCIDE du static vs dynamic. Caching et rendering convergent.
- **4 layers de cache** à expliquer clairement :
  1. **Request Memoization** (React `cache()`, per-request, auto pour `fetch()` avec mêmes args)
  2. **Data Cache** (persistent, survit aux déploiements sauf invalidation)
  3. **Full Route Cache** (build-time, HTML + RSC payload pour routes statiques)
  4. **Router Cache** (client-side, mémoire navigateur, RSC payload)
- **⚠️ Breaking Next 15** : Data Cache par défaut OFF pour `fetch()` (avant : force-cache par défaut)
- **⚠️ Breaking Next 15** : Client Router Cache sans staleTime par défaut pour segments page. Config `staleTimes: { dynamic, static }`
- **`cache()` de React** : per-request memoization pour fonctions custom (DB queries)
- **⚠️ `unstable_cache` déprécié** Next 16 → remplacé par directive `'use cache'`
- **Cache Components STABLE Next 16** : modèle opt-in explicite
  - Activer via **`cacheComponents: true`** dans `next.config.ts`
  - **`'use cache'`** directive en tête de fichier, fonction ou composant
  - **`cacheLife(profile)`** : durée de vie (`'seconds'`, `'minutes'`, `'hours'`, `'days'`, `'weeks'`, `'max'`, ou profil custom)
  - **`cacheTag(tag)`** : associe tag pour invalidation via `revalidateTag`/`updateTag`
- **`dynamicIO` flag renommé `cacheComponents`** Next 16
- **`experimental.ppr` supprimé Next 16** : PPR absorbé dans Cache Components
- **Revalidation** : time-based (`revalidate: 60`, `cacheLife`) vs on-demand (`revalidateTag`, `revalidatePath`, `updateTag`, `refresh`)
- **`revalidateTag(tag, cacheLifeProfile)`** : nouvelle signature 2-args Next 16
- **`updateTag(tag)` et `refresh()`** (Next 16) : sémantique **read-your-writes** dans Server Actions (vs `revalidateTag` lazy/background)
- **`cacheSignal`** (React 19.2, Server Components only) : savoir quand un `cache()` expire pour cleanup ressources externes
- **Dynamic functions** : `cookies()`, `headers()`, `searchParams`, `connection()` forcent dynamic rendering
- **`generateStaticParams`** pour pré-rendre routes dynamiques au build
- **`dynamicParams = false`** pour 404 sur params non générés
- **Route Segment Config** : `dynamic`, `dynamicParams`, `revalidate`, `fetchCache`, `runtime`, `preferredRegion` exports
- **Streaming avec Suspense** : HTML progressif, fallback par zone
- **Terminologie** : SSG = static build time, SSR = dynamic per request, ISR = time/tag revalidation
- **Build output indicators** : `○ Static`, `ƒ Dynamic`, `● SSG`
- **Edge vs Node runtime** : Edge = pas de `fs`, bundle 1-4MB. Node = tout disponible, bundle 50MB
- **`preferredRegion`** : régions de déploiement (Vercel)
- **Quand choisir quoi** : checklist décisionnelle (content type, update frequency, personalization level, auth-gated)
- **Cache poisoning** : ne jamais stocker de données user-specific dans un scope cachable global
- **Debugging** : `logging: { fetches: { fullUrl: true } }` dans config
- **Migration** : `unstable_cache` → `'use cache'`, `experimental.ppr` → `cacheComponents`

---

### 11. images-fonts

```bash
/prof --techno=nextjs --lecon="Images & Fonts" --concepts="next/image,Image component,width height,fill,sizes,priority,placeholder blur,placeholder empty,loader,remotePatterns,localPatterns,Cloudinary,quality restrictions,formats avif webp,responsive images,next/font,localFont,Google Fonts,font subsetting,font display swap,CSS variables,public folder,static assets,SVG strategies,sharp,images.qualities 75,images.minimumCacheTTL 4h,domains deprecated,legacy image deprecated"
```

**Points à garder en tête pour le skill :**
- **`next/image`** : CLS évité auto, lazy loading auto, formats modernes auto (avif, webp)
- **`width`/`height` obligatoires** OU **`fill`** (parent `position: relative`/`absolute`)
- **`sizes` prop CRITIQUE** pour responsive (sinon charge l'image full width)
- **`priority`** pour images LCP (above the fold, hero)
- **Placeholder** : `blur` (statique auto-généré), `empty`, custom data URL
- **Remote images** : `images.remotePatterns` dans config (**`images.domains` déprécié** Next 16)
- **⚠️ Breaking Next 16** : `images.qualities` restreint à `[75]` par défaut (opt-in pour autres valeurs)
- **⚠️ Breaking Next 16** : `images.minimumCacheTTL` passe de 60s à **4h**
- **⚠️ Breaking Next 16** : **`images.localPatterns` requis** pour images locales avec query strings
- **Breaking Next 16** : `images.imageSizes` perd la valeur `16`
- **`next/legacy/image` déprécié** Next 16
- **Custom loader** (`loader` prop) : Cloudinary, Imgix, etc.
- **Sharp obligatoire** en self-hosted pour Image Optimization. Depuis Next 15+, auto-installé
- **`next/font/google`** : fetch au build, pas de requête runtime, pas de FOIT
- **`next/font/local`** : fichiers locaux avec `src`
- **CSS variables pattern** pour fonts : `variable: '--font-inter'` + consommation CSS/Tailwind
- **Font subsetting** : `latin` uniquement pour réduire la taille
- **`public/` folder** : accessible via `/filename.ext`
- **SVG** : import comme React component (via `@svgr/webpack`) OU comme `src`
- **File-based metadata images** : `opengraph-image.tsx`, `twitter-image.tsx`, `icon.tsx`, `apple-icon.tsx` (approfondis dans `metadata-seo`)

---

### 12. metadata-seo

```bash
/prof --techno=nextjs --lecon="Metadata & SEO" --concepts="Metadata API,metadata object,generateMetadata,async metadata,generateViewport,title template,title default,title absolute,description,openGraph,twitter,icons,robots,viewport export,themeColor,canonical,alternates languages,metadata inheritance,parent metadata merge,sitemap.ts,robots.ts,manifest.ts,opengraph-image.tsx,twitter-image.tsx,icon.tsx,apple-icon.tsx,JSON-LD,structured data,metadataBase,ImageResponse,ImageResponse fonts,Document metadata React 19 natif,hreflang"
```

**Points à garder en tête pour le skill :**
- **Metadata object export** vs **`generateMetadata` async function** (pour metadata dynamique basée sur params/DB)
- **`metadataBase: new URL(...)`** pour URLs absolues dans OG/Twitter (sinon warnings)
- **Title template** : `{ template: '%s | Site', default: 'Site' }`, `{ absolute: 'Title' }` pour bypass
- **Inheritance** : metadata remonte du layout vers pages (merge deep sur fields mergeables). Pattern `generateMetadata({ params }, parent)` pour merge avec parent via `await parent`
- **`viewport` export SÉPARÉ** Next 15 (avant dans metadata). Peut être statique OU dynamique via **`generateViewport`** (async, same pattern que `generateMetadata`)
- **Document metadata natif React 19** : `<title>`, `<meta>`, `<link>` dans le JSX sont hoistés automatiquement dans `<head>`. Alternative à Metadata API pour metadata locale à un composant
- **File-based metadata** : `icon.tsx`, `apple-icon.tsx`, `opengraph-image.tsx`, `twitter-image.tsx`, `robots.ts`, `sitemap.ts`, `manifest.ts`
- **`ImageResponse`** de `next/og` : génération d'images OG dynamiques via JSX (runtime Edge). Supporte custom fonts via `fonts` option (chargement runtime, attention au poids)
- **`sitemap.ts`** : fonction exportée retournant `MetadataRoute.Sitemap` (`{ url, lastModified, changeFrequency, priority }[]`)
- **`robots.ts`** : fonction retournant `MetadataRoute.Robots`
- **`manifest.ts`** : fonction retournant `MetadataRoute.Manifest` (PWA)
- **JSON-LD** : injecté via `<script type="application/ld+json">` en JSX
- **SEO best practices** : `canonical`, `alternates.canonical`, `alternates.languages` pour **hreflang**, `openGraph.locale`, `openGraph.type`
- **Pattern inheritance + merge parent** : pour éviter de redéfinir `metadataBase` dans chaque page

---

### 13. internationalisation

```bash
/prof --techno=nextjs --lecon="Internationalisation" --concepts="next-intl,defineRouting,setRequestLocale,locale segment dynamic,NextIntlClientProvider,useTranslations,getTranslations,useFormatter,getFormatter,async locale message loading,type-safe messages,ICU message format,plurals,select,dates formatting,numbers formatting,currency formatting,relative time,routing localized,middleware locale detection,Accept-Language header,locale cookie,alternates languages SEO,static generation per locale,client vs server translations,locale switcher,fallback locale"
```

**Points à garder en tête pour le skill :**
- **`next-intl`** = référence 2026 pour App Router (~2KB, support natif Server Components)
- **`next-i18next` v16** : alternative mais moins conseillée pour nouveaux projets App Router
- **⚠️ Config `i18n` dans `next.config.js` est Pages Router only** : warning depuis 15.2 en App Router
- **Pattern routing** : segment dynamique `[locale]` à la racine (`app/[locale]/page.tsx`)
- **`defineRouting()`** : config partagée entre middleware et navigation APIs (`Link`, `useRouter`)
- **`setRequestLocale()`** : requis pour le rendu statique par locale dans Server Components
- **Middleware** gère détection locale (`Accept-Language` header, cookie) + redirect
- **`NextIntlClientProvider`** : provider pour Client Components descendants
- **`useTranslations`** (Client) vs **`getTranslations`** (Server) : importer selon contexte
- **`useFormatter`** / **`getFormatter`** : dates, nombres, monnaies, relative time (API `Intl` native)
- **Async message loading** : import dynamique `import('./messages/en.json')`
- **Type-safe messages** : génération auto de types depuis fichier de référence
- **ICU message format** : plurals (`{count, plural, one {...} other {...}}`), select (`{gender, select, ...}`)
- **Static generation par locale** : `generateStaticParams` retourne `[{ locale: 'en' }, { locale: 'fr' }]`
- **SEO i18n** : `alternates.languages` dans metadata pour `hreflang`, `openGraph.locale`
- **Locale switcher component** : pattern avec `useRouter().push()` + `usePathname()`
- **Fallback locale** : config de fallback si traduction manquante

---

### 14. tests

```bash
/prof --techno=nextjs --lecon="Tests" --concepts="Vitest,Jest legacy,testing-library,render,screen,userEvent,waitFor,findByRole,getByRole,queryByRole,vi.mock,vi.spyOn,test isolation,test fixtures,unit tests,Client Components testing,Server Components sync,Server Components async,Server Actions testing,integration tests,MSW,Mock Service Worker,fetch mocking,Next.js proxy mode,Playwright E2E,Playwright Component Testing,component testing,Suspense testing,accessibility testing"
```

**Points à garder en tête pour le skill :**
- **Pyramide** (ordre d'apprentissage et de déploiement) : Vitest (unit, beaucoup) → intégration (Vitest/Playwright) → Playwright (E2E, peu)
- **Vitest** : référence 2026 pour unit + Client Components + Server Components **synchrones**. ESM natif, perf top. Commencer par là
- **Jest** : fonctionnel mais Vitest privilégié en 2026 (ESM, vitesse)
- **Playwright** : référence 2026 pour E2E et pour tester les **Server Components asynchrones** (non supportés par Vitest)
- **Playwright Component Testing** : tester des composants isolés dans un vrai browser (alternative à Vitest + jsdom pour les composants qui dépendent du DOM réel)
- **`@testing-library/react`** : render + queries accessibles (screen.getByRole, etc.)
- **`@testing-library/user-event`** : simuler interactions utilisateur (clicks, typing)
- **Server Components testing** :
  - Sync → Vitest avec import direct
  - Async → Playwright (ou extraire data fetching en fonction pure testable)
- **Server Actions testing** : extraire logique en fonction pure testable + Playwright pour flux E2E complet
- **MSW (Mock Service Worker)** : mocker `fetch()` client ET serveur. Pour Server Components, utiliser `@mswjs/http-middleware` ou mode proxy Next 15
- **Next.js 15 proxy mode** : mode expérimental pour fetch mocking avec Playwright
- **Pattern `test.describe`**, `test`, `expect`, `beforeEach`, `afterEach`
- **`vi.mock()`** : mocker modules dans Vitest
- **Test isolation** : chaque test indépendant, pas de state partagé entre tests
- **Async queries** : `findByRole` (Promise) vs `getByRole` (sync, throw si absent) vs `queryByRole` (sync, null si absent)
- **`waitFor`** pour assertions asynchrones
- **Accessibilité first** : prioriser queries par rôle (accessibles) vs `testId`
- **Snapshot testing** : à éviter en général (trop fragile)

---

### 15. deploiement-production

```bash
/prof --techno=nextjs --lecon="Déploiement & Production" --concepts="next build,output standalone,output export,Vercel Fluid Compute,in-function concurrency,bytecode caching,Dockerfile multi-stage,node 20 alpine,sharp installation,cacheHandler,Redis cache handler,Upstash,ISR self-hosted,next start,reverse proxy headers,X-Forwarded-For,t3-oss env-nextjs,runtime vs build-time env,secrets management,Edge runtime,Node.js runtime,instrumentation.ts,onRequestError,Sentry,@sentry/nextjs,OpenTelemetry,@vercel/otel,pino winston,health check,bundle analyzer,optimizePackageImports,serverExternalPackages,Turbopack build,rate limiting Arcjet,Upstash Ratelimit"
```

**Points à garder en tête pour le skill :**
- **`next build`** : analyser le output (`○ Static`, `ƒ Dynamic`, `● SSG` par route)
- **`output: 'standalone'`** : build minimal pour Docker, réduit taille image jusqu'à 80%
- **Dockerfile recommandé** : multi-stage `node:20-alpine` (base → deps → builder → runner), copier `.next/standalone`, `.next/static`, `public`
- **`sharp` obligatoire** en self-hosted pour Image Optimization (auto-installé Next 15+)
- **`output: 'export'`** : SSG only, PAS de Server Actions/ISR/Middleware/Route handlers Node
- **Vercel Fluid Compute** (avril 2025, défaut) : instances partagées, **in-function concurrency**, -30 à 50% invocations, bytecode caching entre invocations en prod, config `{ "fluid": true }`
- **ISR self-hosted multi-replicas** : filesystem default fragmenté → implémenter **`cacheHandler`** custom (stable Next 15). **Redis** backend recommandé (atomicité, TTL, tag-based via `refreshTags()`), Upstash Redis alternative
- **`next start`** : port 3000 default, `--port`, `--hostname`. Pas de `--workers` natif (PM2 ou Node cluster externe)
- **Reverse proxy** : `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`. Nginx : `proxy_set_header Host $host`. Caddy gère auto
- **Env validation 2026** : **`@t3-oss/env-nextjs`** avec Zod, `createEnv({ server, client })`, validation au build (bloque build si invalide)
- **Secrets management** : Vercel Env Vars chiffrées, AWS Secrets Manager, Azure Key Vault. **JAMAIS** dans Dockerfile ou `.env.production` committé
- **Edge runtime** : bundle 1-4MB, pas de `fs`, `crypto` partiel. Idéal : redirects, JWT vérif légère, A/B, geo
- **Node.js runtime** : bundle 50MB, tout disponible. Idéal : DB, crypto complexe, logique lourde
- **`instrumentation.ts`** stable Next 15 : `register()` au démarrage serveur + **`onRequestError()`** pour capturer erreurs (middleware, RSC, actions, handlers)
- **Sentry** : `@sentry/nextjs` >= 8.28.0, intégration via `onRequestError` : `export { onRequestError } = Sentry.captureRequestError`. Sentry SDK utilise OpenTelemetry interne
- **OpenTelemetry** natif Next.js : spans auto pour requêtes, renders, fetch. **`@vercel/otel`** sur Vercel, exporteur OTLP en self-hosted (SigNoz, Jaeger)
- **`@vercel/analytics`** et **`@vercel/speed-insights`** : packages client dans root layout
- **Logs structurés** : **`pino`** ou **`winston`** en self-hosted, `console.log` JSON auto sur Vercel
- **Health check** : Route Handler `GET /api/health` retournant `{ status: 'ok', version }`, exclu du middleware auth
- **`@next/bundle-analyzer`** : `ANALYZE=true next build` → 3 rapports HTML (client, nodejs, edge)
- **`optimizePackageImports`** : optimise barrel files (`lucide-react`, `@heroicons/react`, `date-fns`) : 15-70% vitesse dev, 40% cold start
- **`serverExternalPackages`** (renommé depuis `serverComponentsExternalPackages`) : exclut packages du bundle RSC (binaires natifs, packages lourds)
- **Turbopack build** : défaut Next 16, 2-5x plus rapide qu'webpack. Revenir : `next build --webpack`
- **`scroll-behavior: smooth`** retiré auto Next 16, opt-in via `data-scroll-behavior="smooth"` sur `<html>`
- **Rate limiting en prod** : **Arcjet** (all-in-one security), **Upstash Ratelimit** (Redis-based), à mettre en middleware pour `/api/auth/*` et `/api/*` endpoints critiques
- **Codemod de migration** : `npx @next/codemod@canary upgrade latest`

---

## Matrice "concept → leçon canonique"

Pour éviter la redondance cross-leçon, chaque concept est **canonique dans UNE leçon** et peut être mentionné brièvement ailleurs si pertinent. Liste des concepts partagés :

| Concept | Canonique dans | Mentionné aussi dans |
|---------|----------------|----------------------|
| `useActionState` | `hooks-modernes-react-19` | `mutations-server-actions` (usage) |
| `useFormStatus` | `hooks-modernes-react-19` | `mutations-server-actions` (usage) |
| `useOptimistic` | `hooks-modernes-react-19` | `mutations-server-actions` (usage) |
| `use()` hook | `hooks-modernes-react-19` | `data-fetching` (pattern client) |
| React Compiler | `hooks-modernes-react-19` | `cli-configuration` (config Next) |
| `cacheSignal` | `rendering-caching` | (nulle part ailleurs) |
| `cache()` React | `data-fetching` | `rendering-caching` (Request Memoization layer) |
| `'use cache'` directive | `rendering-caching` | `data-fetching` (mention rapide pour DB queries) |
| `cacheLife` / `cacheTag` | `rendering-caching` | (nulle part ailleurs) |
| `revalidateTag(tag, profile)` | `rendering-caching` | `mutations-server-actions` (usage) |
| `updateTag()` / `refresh()` | `mutations-server-actions` | `rendering-caching` (mention) |
| `after()` | `data-fetching` | (nulle part ailleurs) |
| `connection()` | `data-fetching` | `routing-navigation` (mention), `rendering-caching` (dynamic functions) |
| Async request APIs (cookies, headers, params) | `data-fetching` | `routing-navigation` (async params), `authentification` (cookies) |
| `fetch()` uncached default | `data-fetching` | `rendering-caching` (Data Cache layer) |
| Taint API (`experimental_taint*`) | `server-client-components` | `authentification` (protection hashes) |
| `proxy.ts` / `middleware.ts` | `api-middleware` | `authentification` (route protection), `internationalisation` (locale detection) |
| CSRF Server Actions | `mutations-server-actions` | `authentification` (mention) |
| `serverActions.allowedOrigins` | `mutations-server-actions` | `api-middleware` (mention) |
| `unauthorized()` / `forbidden()` | `routing-navigation` | `authentification` (usage) |
| `unstable_rethrow()` | `routing-navigation` | `data-fetching` (pattern try/catch) |
| `notFound()` | `routing-navigation` | `data-fetching` (pattern) |
| `generateStaticParams` | `rendering-caching` | `routing-navigation` (mention) |
| `next/form` | `mutations-server-actions` | (nulle part ailleurs) |
| `instrumentation.ts` / `onRequestError` | `deploiement-production` | (nulle part ailleurs) |
| Typed Routes | `cli-configuration` (setup) | `routing-navigation` (usage) |
| `<ViewTransition>` + `transitionTypes` | `routing-navigation` | `hooks-modernes-react-19` (mention R19.2) |
| `useLinkStatus` | `routing-navigation` | (nulle part ailleurs) |
| `<Activity>` | `hooks-modernes-react-19` | `routing-navigation` (usage Next 16 nav) |
| Prisma/Drizzle/connection pooling | `data-fetching` | `deploiement-production` (self-hosted DB) |
| `@t3-oss/env-nextjs` | `cli-configuration` | `deploiement-production` (usage prod) |
| Cookies `HttpOnly`, `Secure`, `SameSite` | `authentification` | (nulle part ailleurs) |
| Argon2id / bcrypt / `jose` / `iron-session` | `authentification` | (nulle part ailleurs) |
| Better Auth | `authentification` | (nulle part ailleurs) |
| Rate limiting (Arcjet, Upstash Ratelimit) | `deploiement-production` | `authentification` (mention pour auth endpoints) |

**Règle pour le skill `prof`** : quand un concept est mentionné dans une leçon non-canonique, il doit être **brièvement décrit** (1-2 bullets) avec un renvoi implicite vers la leçon canonique, pas réexpliqué intégralement.

---

## Versions cibles pour l'index

| Techno | `last_version` | Notes |
|--------|----------------|-------|
| `react` | `"19.2"` | React 19.2.5 stable avril 2026 |
| `nextjs` | `"16.2"` | Next.js 16.2.x stable avril 2026 |

Le champ `last_version` doit être écrit **par leçon** dans l'index (pas au niveau techno) selon la spec du SKILL.md. Toutes les leçons react auront `last_version: "19.2"`, toutes les leçons nextjs auront `last_version: "16.2"`.

---

## Dépréciations et breaking changes critiques à signaler (via `> ⚠️` dans les leçons)

### Next.js 16 dépréciations/suppressions

| Ancien | Nouveau | Leçon impactée |
|--------|---------|----------------|
| `middleware.ts` | **`proxy.ts`** | `api-middleware`, `authentification` |
| `experimental.ppr`, `experimental_ppr` export | **`cacheComponents: true`** | `rendering-caching` |
| `experimental.dynamicIO` | `cacheComponents: true` (renommé) | `rendering-caching` |
| `unstable_cache` | **`'use cache'`** directive | `rendering-caching`, `data-fetching` |
| `unstable_noStore()` | **`connection()`** | `data-fetching`, `routing-navigation` |
| `unstable_after` | **`after`** (depuis 15.1) | `data-fetching` |
| `next lint` command | ESLint CLI ou Biome | `cli-configuration` |
| `<Link legacyBehavior>` | supprimé | `routing-navigation` |
| `next/legacy/image` | `next/image` | `images-fonts` |
| `images.domains` | **`images.remotePatterns`** | `images-fonts` |
| `serverRuntimeConfig`/`publicRuntimeConfig` | env vars | `cli-configuration` |
| `serverComponentsExternalPackages` | **`serverExternalPackages`** | `deploiement-production` |
| `revalidateTag(tag)` 1-arg | **`revalidateTag(tag, cacheLifeProfile)`** | `rendering-caching`, `mutations-server-actions` |
| AMP support | supprimé totalement | |
| Accès sync à `params`/`searchParams`/`cookies()`/`headers()` | **HARD ERROR** en 16 | `routing-navigation`, `data-fetching` |

### React 19 dépréciations/suppressions

| Ancien | Nouveau | Leçon impactée |
|--------|---------|----------------|
| `useFormState` (react-dom) | **`useActionState`** (react) | `hooks-modernes-react-19`, `mutations-server-actions` |
| `<Context.Provider>` | **`<Context value={...}>`** | `hooks-modernes-react-19` |
| `forwardRef` | **`ref` as prop** | `hooks-modernes-react-19`, `bases-react` |
| `element.ref` | **`element.props.ref`** | `hooks-modernes-react-19` |
| `propTypes` | **TypeScript** (supprimé) | `bases-react` |
| `defaultProps` sur function components | **ES6 default params** (supprimé) | `bases-react` |
| `ReactDOM.render`/`hydrate`/`findDOMNode` | **`createRoot`/`hydrateRoot`/refs** (supprimés) | `bases-react` |
| Legacy context, string refs | supprimés | |
| `react-test-renderer` | `@testing-library/react` | `tests` |

### Auth écosystème

| Statut | Leçon impactée |
|--------|----------------|
| **Lucia deprecated** (mars 2025) → Better Auth | `authentification` |
| **Auth.js v5 en mode maintenance** (équipe fusionnée avec Better Auth sept 2025) | `authentification` |

---

## Fichiers critiques à consulter avant exécution

- `.claude/skills/prof/SKILL.md` : spec complète du skill `prof` (workflow CREATE, conventions de format, règles de recherche)
- `lessons/index.yaml` : index global (à enrichir avec technos `react` et `nextjs`)
- `lessons/angular/routing-navigation.md` : référence format routing
- `lessons/angular/deploiement-csr-ssr-ssg.md` : référence fusion multi-concepts en une leçon (modèle pour `rendering-caching`)
- `lessons/java/spring/spring-security.md` : référence format auth dense (477 lignes, 1 leçon)
- `lessons/nestjs/guards-authentication.md` : référence auth backend Node (413 lignes)

## Vérification du plan (end-to-end)

1. **Lancer la première leçon** : `/prof --techno=react --lecon="Bases React"` pour valider que le skill prend bien les concepts depuis la commande ou les redemande
2. **Vérifier le format de sortie** : densité comparable à `angular/routing-navigation.md` (5-12 chapitres, 3-7 bullets par chapitre, blocs de code < 20 lignes)
3. **Vérifier l'index** : après chaque leçon, `lessons/index.yaml` doit contenir la nouvelle entrée avec `id`, `file`, `concepts`, `last_version`, `last_updated`
4. **Boucle d'itération** : exécuter les 15 commandes dans l'ordre recommandé, en validant chaque leçon avant de passer à la suivante
5. **Contrôle qualité par leçon** :
   - Les concepts de la commande `--concepts` sont présents
   - Les dépréciations de la matrice ci-dessus sont signalées via `> ⚠️`
   - Les breaking changes Next 15/16 sont explicites
   - Les concepts marqués "canonique" ne sont PAS dupliqués dans d'autres leçons
   - La langue est cohérente (français avec termes techniques en anglais/backticks)

## Notes opérationnelles

- Les listes de `--concepts` **cadrent** le skill, pas d'exhaustivité. Le skill `prof` effectue ses propres recherches et peut/doit ajouter des concepts manquants essentiels identifiés lors des recherches.
- Les **sections 11 à 23 du cours Udemy (Pages Router)** sont totalement ignorées.
- Le skill `prof` demande **validation utilisateur AVANT** d'écrire chaque leçon (règle OBLIGATOIRE dans SKILL.md). Prévoir d'être disponible pour valider 15 leçons.
- Les commandes `/prof` dans ce plan peuvent être exécutées une par une dans l'ordre. Si une leçon nécessite un ajustement, éditer sa commande localement avant exécution.
