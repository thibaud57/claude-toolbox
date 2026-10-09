# 1. Configuration et Concepts de Base

- Configuration moderne avec `provideRouter()` dans `app.config.ts` (standalone) remplace `RouterModule.forRoot()` (NgModule)
- Le `<router-outlet>` agit comme placeholder dynamique qui affiche le composant correspondant à la route active
- `RouterFeatures` permettent d'activer des fonctionnalités optionnelles : `withComponentInputBinding()`, `withNavigationErrorHandler()`, `withViewTransitions()`, `withDebugTracing()`, etc.

```typescript
// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding())
  ]
};
```

```typescript
// app.routes.ts
export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'products', component: ProductsComponent },
  { path: '**', component: NotFoundComponent }
];
```

# 2. Navigation et Liens

- `routerLink` préserve le contexte SPA et déclenche la navigation via le `Router`, contrairement à `href` qui force un rechargement complet
- `routerLinkActive` applique automatiquement une classe CSS quand la route est active, avec option `routerLinkActiveOptions` pour contrôler la correspondance exacte
- `ariaCurrentWhenActive` sur `routerLinkActive` applique automatiquement `aria-current` sur le lien actif (Angular 21)
- `RouterLink` expose `isActive` comme `Signal<boolean>` réactif aux changements de navigation (Angular 21.1) ; remplace `Router.isActive()` déprécié

```html
<nav>
  <a routerLink="/home" routerLinkActive="active" ariaCurrentWhenActive="page"
     [routerLinkActiveOptions]="{exact: true}">Home</a>
  <a [routerLink]="['/products', productId]" routerLinkActive="active">Product</a>
</nav>
```

## Navigation Programmatique

- `Router.navigate()` accepte un tableau de segments de route et des options : `relativeTo`, `queryParams`, `fragment`, `queryParamsHandling`, `onSameUrlNavigation`
- `Router.navigateByUrl()` navigue vers une URL complète ; préférer `navigate()` pour les routes relatives
- Rechargement du composant courant : naviguer vers `/` avec `skipLocationChange: true` puis revenir à l'URL courante

```typescript
export class NavComponent {
  router = inject(Router);

  goToProduct(id: number) {
    this.router.navigate(['/products', id], {
      queryParams: { category: 'electronics' }
    });
  }

  refresh() {
    const currentUrl = this.router.url;
    this.router.navigateByUrl('/', { skipLocationChange: true })
      .then(() => this.router.navigateByUrl(currentUrl));
  }
}
```

## Événements de Navigation

- `Router.events` est un `Observable` émettant les événements du cycle de navigation : `NavigationStart` → `GuardsCheckStart` → `GuardsCheckEnd` → `ResolveStart` → `ResolveEnd` → `NavigationEnd`
- Toute navigation se termine par un des quatre events terminaux : `NavigationEnd`, `NavigationCancel`, `NavigationError`, `NavigationSkipped`
- `NavigationSkipped` est émis quand `onSameUrlNavigation: 'ignore'` (défaut) et l'URL cible est identique à l'URL courante
- **`router.currentNavigation()`** : signal `Signal<Navigation | null>` disponible depuis Angular 20.2, réactif dans les templates ; remplace `getCurrentNavigation()` déprécié

```typescript
// Approche signal (Angular 20.2+)
export class AppComponent {
  router = inject(Router);
  isNavigating = computed(() => !!this.router.currentNavigation());
}
```

```typescript
// Approche classique RxJS
export class AppComponent {
  router = inject(Router);
  loading = false;

  constructor() {
    this.router.events.pipe(
      filter(e =>
        e instanceof NavigationStart ||
        e instanceof NavigationEnd ||
        e instanceof NavigationCancel ||
        e instanceof NavigationError
      ),
      takeUntilDestroyed()
    ).subscribe(e => this.loading = e instanceof NavigationStart);
  }
}
```

# 3. Routes Dynamiques et Paramètres

## Définition et Extraction des Paramètres

- Les paramètres de route se définissent avec `:paramName` dans le `path`
- **Méthode moderne (Angular 16+)** : `input()` signal avec `withComponentInputBinding()` pour injection automatique des paramètres
- **Méthode classique** : `ActivatedRoute.params` observable ou `ActivatedRoute.snapshot.paramMap`
- Les `input()` supportent les transformations et validations de type, y compris `input.required<Type>()`

```typescript
// Composant avec input() signal
export class ProductDetailComponent {
  id = input.required<string>();

  product = computed(() =>
    this.productService.getProduct(this.id())
  );
}
```

## ActivatedRoute vs ActivatedRouteSnapshot

- `ActivatedRoute` est un observable permettant de réagir aux changements de paramètres sans recréer le composant
- `ActivatedRouteSnapshot` est une capture statique de l'état de la route à un instant T, utile dans les guards et resolvers
- Utiliser `ActivatedRoute.params` observable quand le même composant peut être réutilisé avec des paramètres différents

```typescript
export class ProductComponent {
  route = inject(ActivatedRoute);

  ngOnInit() {
    // Observable : réagit aux changements de paramètres
    this.route.params.subscribe(params => {
      const id = params['id'];
      this.loadProduct(id);
    });

    // Snapshot : valeur unique à l'initialisation
    const id = this.route.snapshot.paramMap.get('id');
  }
}
```

# 4. Routes Imbriquées

- Les routes enfants se définissent via la propriété `children` dans la configuration de la route parent
- Chaque niveau de routes imbriquées nécessite son propre `<router-outlet>` dans le template du parent
- `relativeTo: ActivatedRoute` dans la navigation permet de construire des chemins relatifs au contexte actuel
- L'accès aux données du parent depuis l'enfant nécessite `withRouterConfig({paramsInheritanceStrategy: 'always'})`
- `routerOutletData` input sur `<router-outlet>` permet de passer des données du parent au composant de la route via le token `ROUTER_OUTLET_DATA` (Angular 19)

```typescript
export const routes: Routes = [
  {
    path: 'products',
    component: ProductsComponent,
    children: [
      { path: '', component: ProductListComponent },
      { path: ':id', component: ProductDetailComponent },
      { path: ':id/edit', component: ProductEditComponent }
    ]
  }
];
```

```html
<!-- Parent -->
<router-outlet [routerOutletData]="{ userId: currentUser.id }" />
```

```typescript
export class ProductDetailComponent {
  outletData = inject<Signal<{ userId: string }>>(ROUTER_OUTLET_DATA);

  router = inject(Router);
  route = inject(ActivatedRoute);

  editProduct() {
    this.router.navigate(['edit'], { relativeTo: this.route });
  }
}
```

# 5. Query Parameters et Data Statique

## Query Parameters

- Les query params (`?key=value`) se définissent via `queryParams` dans `routerLink` ou `Router.navigate()`
- Extraction moderne via `input()` avec `withComponentInputBinding()` activé
- Extraction classique via `ActivatedRoute.queryParams` observable ou `queryParamMap`
- `queryParamsHandling: 'preserve' | 'merge'` contrôle la propagation des query params lors de la navigation

> ⚠️ Angular 19 : passer un `UrlTree` à `routerLink` combiné avec `queryParams` ou `fragment` lève une erreur ; les options doivent être embarquées dans le `UrlTree`

```html
<a [routerLink]="['/products']"
   [queryParams]="{category: 'books', sort: 'price'}">Products</a>
```

```typescript
export class ProductsComponent {
  category = input<string>();
  sort = input<string>();

  filteredProducts = computed(() =>
    this.applyFilters(this.category(), this.sort())
  );
}
```

## Data Statique

- La propriété `data` sur une route permet d'attacher des métadonnées statiques accessibles dans le composant
- Utile pour configurer le comportement du composant sans dupliquer la logique (ex: mode édition vs création)
- Accessible via `ActivatedRoute.data` ou directement comme `input()` avec `withComponentInputBinding()`

```typescript
export const routes: Routes = [
  {
    path: 'admin',
    component: AdminComponent,
    data: { role: 'admin', requiresAuth: true }
  }
];
```

```typescript
export class AdminComponent {
  role = input<string>();
}
```

## Titres de Page

- Configuration du titre via la propriété `title` dans la route (string ou `ResolveFn<string>`)
- Titres dynamiques avec `ResolveFn<string>` pour inclure des données de route
- Stratégie personnalisée via `TitleStrategy` pour formatter les titres globalement

```typescript
export const routes: Routes = [
  { path: 'home', component: HomeComponent, title: 'Home' },
  {
    path: 'products/:id',
    component: ProductDetailComponent,
    title: (route) => {
      const id = route.paramMap.get('id');
      return `Product ${id}`;
    }
  }
];
```

# 6. Resolvers

- Les `ResolveFn` chargent des données avant l'activation de la route, garantissant que le composant reçoit les données complètes
- Remplacent les class-based resolvers (dépréciés Angular 15+) par des fonctions utilisant `inject()`
- Retournent `Observable<T>`, `Promise<T>` ou `T` directement, le router attend automatiquement la résolution
- Les resolvers s'exécutent en parallèle si plusieurs sont définis sur la même route ; un seul resolver lent bloque l'activation de toute la route
- En cas d'erreur, retourner `RedirectCommand` pour rediriger ou laisser l'erreur se propager vers `NavigationError`

```typescript
export const productResolver: ResolveFn<Product> = (route) => {
  const productService = inject(ProductService);
  const id = route.paramMap.get('id')!;
  return productService.getProduct(id);
};

export const routes: Routes = [
  {
    path: 'products/:id',
    component: ProductDetailComponent,
    resolve: { product: productResolver }
  }
];
```

## Accès aux Données Résolues

- Données disponibles via `ActivatedRoute.data` ou comme `input()` avec `withComponentInputBinding()`
- Le nom de la clé dans `resolve: { product: ... }` devient le nom de la propriété accessible

```typescript
export class ProductDetailComponent {
  product = input.required<Product>(); // Injection automatique
}
```

## Contrôle et Gestion d'Erreurs

- `runGuardsAndResolvers: 'always' | 'paramsChange' | 'paramsOrQueryParamsChange'` contrôle quand les resolvers s'exécutent
- Gestion d'erreurs via `catchError()` avec `RedirectCommand` ou écoute des événements `NavigationError`

```typescript
export const safeProductResolver: ResolveFn<Product | RedirectCommand> = (route) => {
  const productService = inject(ProductService);
  const router = inject(Router);
  const id = route.paramMap.get('id')!;

  return productService.getProduct(id).pipe(
    catchError(() => of(new RedirectCommand(router.parseUrl('/products'))))
  );
};
```

# 7. Guards et Protection des Routes

## Guards Fonctionnels

- Les guards fonctionnels (`CanActivateFn`, `CanDeactivateFn`, `CanMatchFn`) remplacent les class-based guards (dépréciés depuis Angular 15.2)
- `CanActivateFn` contrôle l'accès à une route, `CanActivateChildFn` protège toutes les routes enfants
- `CanDeactivateFn` empêche de quitter une route (ex: formulaire non sauvegardé)
- **`CanMatchFn`** : détermine si une route peut être matchée pendant la résolution du path (utile pour feature flags) ; contrairement à `CanActivateFn`, empêche le lazy-loading du bundle si la route ne matche pas

```typescript
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

export const routes: Routes = [
  {
    path: 'admin',
    component: AdminComponent,
    canActivate: [authGuard]
  }
];
```

## CanDeactivate

- `CanDeactivateFn<ComponentType>` reçoit le composant comme premier paramètre pour accéder à son état
- Pattern courant : interface `CanComponentDeactivate` avec méthode `canDeactivate()` implémentée par le composant

```typescript
export interface CanComponentDeactivate {
  canDeactivate: () => Observable<boolean> | Promise<boolean> | boolean;
}

export const unsavedChangesGuard: CanDeactivateFn<CanComponentDeactivate> =
  (component) => {
    return component.canDeactivate ? component.canDeactivate() : true;
  };

export class FormComponent implements CanComponentDeactivate {
  form = inject(FormBuilder).nonNullable.group({});

  canDeactivate(): boolean {
    if (this.form.dirty) {
      return confirm('Unsaved changes. Leave?');
    }
    return true;
  }
}
```

## Valeurs de Retour des Guards

- **`true`** : autorise la navigation
- **`false`** : bloque la navigation
- **`UrlTree`** : redirige vers une autre route
- **`RedirectCommand`** (Angular 18+) : redirige avec options avancées (`skipLocationChange`, `replaceUrl`)
- **`withNavigationErrorHandler(fn)`** : handler global dans `provideRouter()` ; peut retourner `RedirectCommand` pour convertir une erreur resolver en redirection propre (émet `NavigationCancel` au lieu de `NavigationError`)

# 8. Routes Spéciales et Organisation

## Route 404 et Redirections

- Route wildcard `**` capture toutes les URLs non matchées, doit être en dernière position
- `redirectTo` avec `pathMatch: 'full'` pour les redirections exactes
- `redirectTo` peut être une fonction retournant `string | UrlTree | Observable<...> | Promise<...>` depuis Angular 20 (redirections asynchrones)

```typescript
export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  {
    path: 'old-products',
    redirectTo: () => {
      const auth = inject(AuthService);
      return auth.isAuthorized() ? '/products' : '/login';
    }
  },
  { path: '**', component: NotFoundComponent }
];
```

## Organisation Multi-fichiers

- Séparation des routes par feature dans des fichiers dédiés (ex: `products.routes.ts`, `admin.routes.ts`)
- Import et composition dans `app.routes.ts` pour maintenir la maintenabilité

```typescript
// products.routes.ts
export const PRODUCT_ROUTES: Routes = [
  { path: '', component: ProductListComponent },
  { path: ':id', component: ProductDetailComponent }
];

// app.routes.ts
export const routes: Routes = [
  { path: 'products', children: PRODUCT_ROUTES },
];
```

## onSameUrlNavigation

- Par défaut (`'ignore'`) : naviguer vers l'URL courante émet `NavigationSkipped` sans ré-exécuter guards ni resolvers
- `'reload'` : force la ré-exécution des guards et resolvers sans recréer les composants (nécessite aussi `RouteReuseStrategy` pour recréer les composants)
- Configurable globalement via `withRouterConfig({ onSameUrlNavigation: 'reload' })`
- `runGuardsAndResolvers` au niveau de la route permet un contrôle plus fin que `onSameUrlNavigation` global : `'paramsChange'`, `'paramsOrQueryParamsChange'`, `'always'` ou fonction personnalisée
