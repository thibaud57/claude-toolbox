# 1. Configuration et Concepts de Base

- Configuration moderne avec `provideRouter()` dans `app.config.ts` (standalone) remplace `RouterModule.forRoot()` (NgModule)
- Le `<router-outlet>` agit comme placeholder dynamique qui affiche le composant correspondant à la route active
- Les `RouterFeatures` activent des fonctionnalités optionnelles (ex : `withComponentInputBinding()`, `withViewTransitions()`)

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
- `RouterLink` expose `isActive` comme `Signal<boolean>` réactif aux changements de navigation ; remplace `Router.isActive()` déprécié

```html
<nav>
  <a routerLink="/home" routerLinkActive="active"
     [routerLinkActiveOptions]="{exact: true}">Home</a>
  <a [routerLink]="['/products', productId]" routerLinkActive="active">Product</a>
</nav>
```

## Navigation Programmatique

- `Router.navigate()` accepte un tableau de segments de route et des options (ex : `relativeTo`, `queryParams`)
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

- `Router.events` est un `Observable` émettant les événements du cycle de navigation : `NavigationStart` → guards → resolvers → `NavigationEnd`
- Toute navigation se termine par un event terminal, dont `NavigationSkipped` émis quand `onSameUrlNavigation: 'ignore'` (défaut) et l'URL cible est identique à l'URL courante
- **`router.currentNavigation()`** : `Signal<Navigation | null>` réactif dans les templates ; remplace `getCurrentNavigation()` déprécié (alternative RxJS : filtrer `Router.events` sur `NavigationStart` et les events terminaux)

```typescript
export class AppComponent {
  router = inject(Router);
  isNavigating = computed(() => !!this.router.currentNavigation());
}
```

# 3. Routes Dynamiques et Paramètres

## Définition et Extraction des Paramètres

- **Méthode moderne** : `input()` signal avec `withComponentInputBinding()` pour injection automatique des paramètres
- **Méthode classique** : `ActivatedRoute.params` observable ou `ActivatedRoute.snapshot.paramMap`

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

- `relativeTo: ActivatedRoute` dans la navigation permet de construire des chemins relatifs au contexte actuel
- L'accès aux données du parent depuis l'enfant nécessite `withRouterConfig({paramsInheritanceStrategy: 'always'})`
- `routerOutletData` input sur `<router-outlet>` permet de passer des données du parent au composant de la route via le token `ROUTER_OUTLET_DATA`

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

- Extraction identique aux paramètres de route : `input()` avec `withComponentInputBinding()`, ou `ActivatedRoute.queryParamMap`
- `queryParamsHandling` (ex : `'merge'`) contrôle la propagation des query params lors de la navigation

> ⚠️ Depuis 19 : `UrlTree` combiné avec `queryParams` ou `fragment` sur `routerLink` lève une erreur → embarquer les options dans le `UrlTree`

```html
<a [routerLink]="['/products']"
   [queryParams]="{category: 'books', sort: 'price'}">Products</a>
```

## Data Statique

- La propriété `data` d'une route est accessible via `ActivatedRoute.data` ou directement comme `input()` avec `withComponentInputBinding()`

```typescript
export const routes: Routes = [
  {
    path: 'admin',
    component: AdminComponent,
    data: { role: 'admin', requiresAuth: true }
  }
];
```

## Titres de Page

- `title` accepte un string ou un `ResolveFn<string>` pour inclure des données de route ; `TitleStrategy` formate les titres globalement

```typescript
export const routes: Routes = [
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
- Les resolvers s'exécutent en parallèle si plusieurs sont définis sur la même route ; un seul resolver lent bloque l'activation de toute la route
- En cas d'erreur, retourner `RedirectCommand` pour rediriger ou laisser l'erreur se propager vers `NavigationError`
- Les données résolues sont accessibles via `ActivatedRoute.data` ou comme `input()` du même nom que la clé de `resolve`

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

- **`RedirectCommand`** : redirige avec options avancées (`skipLocationChange`, `replaceUrl`)
- **`withNavigationErrorHandler(fn)`** : handler global dans `provideRouter()` ; peut retourner `RedirectCommand` pour convertir une erreur resolver en redirection propre (émet `NavigationCancel` au lieu de `NavigationError`)

# 8. Routes Spéciales et Organisation

## Route 404 et Redirections

- `redirectTo` avec `pathMatch: 'full'` pour les redirections exactes
- `redirectTo` peut être une fonction, y compris asynchrone (`Observable`, `Promise`)

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

## onSameUrlNavigation

- Par défaut (`'ignore'`) : naviguer vers l'URL courante émet `NavigationSkipped` sans ré-exécuter guards ni resolvers
- `'reload'` : force la ré-exécution des guards et resolvers sans recréer les composants (nécessite aussi `RouteReuseStrategy` pour recréer les composants)
- Configurable globalement via `withRouterConfig({ onSameUrlNavigation: 'reload' })`
- `runGuardsAndResolvers` au niveau de la route permet un contrôle plus fin que `onSameUrlNavigation` global (ex : `'paramsChange'`, ou fonction personnalisée)
