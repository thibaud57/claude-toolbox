# 1. Configuration Kubernetes : Commandes & Arguments

- `command` remplace l'`ENTRYPOINT` du Dockerfile, `args` remplace son `CMD`
- `command` seul s'exécute sans argument et ignore complètement les paramètres du Dockerfile ; `args` seul est ajouté à l'`ENTRYPOINT` de l'image
- L'utilisation de variables d'environnement dans les commandes et arguments est possible avec la syntaxe `$(VARIABLE_NAME)`, résolue par le kubelet avant le lancement (pas par le shell), et uniquement si la variable référencée est déclarée dans le même bloc `env`

```yaml
# Exemple avec une commande complexe utilisant des variables d'environnement
apiVersion: v1
kind: Pod
metadata:
  name: print-greeting
spec:
  containers:
  - name: greeting-container
    image: busybox
    env:
    - name: MESSAGE
      value: "Bonjour Kubernetes"
    command: ["/bin/sh"]
    args: ["-c", "echo $(MESSAGE) && sleep 3600"]
```

# 2. Variables d'Environnement

- Le champ `env` définit une valeur statique (`value`) ou une source dynamique (`valueFrom`) ; `envFrom` importe en masse toutes les clés d'une source externe
- En cas de collision de clés : `env` est prioritaire sur `envFrom` ; entre deux sources `envFrom`, la dernière déclarée l'emporte

# 3. ConfigMap : Gestion des Configurations Non-Sensibles

- `ConfigMap` stocke des données de configuration non-sensibles (paires clé-valeur ou fichiers entiers) ; séparation config/image, pas de rebuild nécessaire pour changer la config
- Injection dans un Pod : variable par variable via `valueFrom.configMapKeyRef`, en masse via `envFrom.configMapRef`, ou montée comme fichier via `volumeMounts`
- **`immutable: true`** : empêche toute modification ; améliore les performances en désactivant le watch de l'objet par le kubelet
- **Mise à jour à chaud** : une ConfigMap montée via `volumeMount` est propagée automatiquement aux Pods en cours (~1 minute) ; injectée via `env` ou `envFrom`, elle n'est **jamais** propagée automatiquement : redémarrage du Pod obligatoire

> ⚠️ `immutable: true` est irréversible : impossible de repasser à mutable, il faut supprimer et recréer la ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
immutable: true
data:
  DATABASE_HOST: "mysql.example.com"
  DATABASE_PORT: "3306"
  LOG_LEVEL: "info"
```

# 4. Secret : Gestion des Données Sensibles

- `Secret` stocke des données sensibles (mots de passe, tokens, certificats) ; encodage base64, **pas un chiffrement** : `kubectl get secret -o yaml` expose les valeurs immédiatement décodables. Vraie protection = RBAC (restreindre qui peut lire les Secrets) + chiffrement etcd-at-rest en production
- **`immutable: true`** : même bénéfice que pour les ConfigMaps ; empêche les modifications accidentelles de secrets critiques

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
immutable: true
type: Opaque
data:
  username: YWRtaW4=  # base64 de "admin"
  password: cGFzc3dvcmQ=  # base64 de "password"
---
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: app-container
    image: my-app:latest
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:  # visible dans kubectl describe pod et /proc/self/environ : préférer volumeMount pour les secrets critiques
          name: db-credentials
          key: username
```

```bash
# Décoder les valeurs d'un Secret
kubectl get secret db-credentials -o jsonpath='{.data.username}' | base64 --decode
```

# 5. Security Contexts

- Peut être défini au niveau `Pod` (s'applique à tous ses conteneurs) ou au niveau `Container` (prioritaire sur le Pod), utiles en combinaison
- **`runAsUser`** / **`runAsGroup`** / **`fsGroup`** : contrôle l'UID, GID des processus, et le groupe propriétaire des volumes montés ; `fsGroup` s'applique uniquement aux volumes (pas aux processus) : sans lui, une app non-root ne peut pas écrire dans un volume monté
- **Linux Capabilities** : pattern recommandé = `capabilities.drop: [ALL]` + `add: [NET_BIND_SERVICE]`, pour un accès précis sans droits root globaux. `NET_BIND_SERVICE` est nécessaire pour écouter sur un port < 1024 ; alternative : configurer l'app sur un port > 1024 et faire la translation dans le Service
- **`readOnlyRootFilesystem: true`** : système de fichiers racine en lecture seule, empêche les modifications non autorisées ; bloque aussi l'écriture dans `/tmp` : les JVM et frameworks qui génèrent des fichiers temporaires crashent, monter un `emptyDir` sur ces paths (`/tmp`, `/var/cache`...)
- **`seccompProfile`** : filtre les appels système ; `type: RuntimeDefault` offre une baseline sécurisée sans configuration spécifique
- **`appArmorProfile`** : profil AppArmor via le champ natif `securityContext.appArmorProfile`
- **`runAsNonRoot: true`** + **`allowPrivilegeEscalation: false`** : combinaison minimale recommandée pour tous les conteneurs de production

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: demo-container
    image: nginx
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      appArmorProfile:
        type: RuntimeDefault
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
```

```bash
# Doit échouer avec readOnlyRootFilesystem: true
kubectl exec security-context-demo -- touch /test-file

# Vérifier les capacités Linux actives du conteneur
kubectl exec security-context-demo -- grep Cap /proc/self/status
```

# 6. Resource Requirements

- Un conteneur qui dépasse sa limite `memory` est terminé immédiatement par `OOMKilled`
- Un dépassement de limite `CPU` entraîne du `throttling` : pas d'erreur, pas de redémarrage, juste des latences anormales. Symptôme : `kubectl top pod` normal en apparence, métriques `cpu_throttled_seconds` élevées
- Les `ResourceQuotas` au niveau du `namespace` permettent de limiter la consommation totale des ressources, évitant qu'un projet monopolise le cluster : si le quota est dépassé, les Pods refusent de démarrer ; l'erreur est visible dans `kubectl describe replicaset` (section Events), pas dans `kubectl get pods`
- **`LimitRange`** : complète le `ResourceQuota` en appliquant des valeurs `requests`/`limits` par défaut sur les Pods qui n'en déclarent pas ; sans lui, un Pod sans `requests` peut consommer toutes les ressources d'un nœud

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app-container
    image: nginx
    resources:
      requests:        # Ressources garanties au démarrage
        memory: "128Mi"
        cpu: "250m"    # 25% d'un CPU
      limits:          # Limites maximales autorisées
        memory: "256Mi"
        cpu: "500m"    # 50% d'un CPU
```

# 7. Service Accounts

- L'attribut `automountServiceAccountToken` peut être défini à `false` au niveau du Pod ou du Service Account pour empêcher le montage automatique du token, renforçant la sécurité ; règle pratique : mettre `false` par défaut sur toutes les apps métier qui n'appellent pas l'API Kubernetes directement
- Les Role-Based Access Control (RBAC) s'appliquent aux Service Accounts via des `ClusterRoleBinding` ou `RoleBinding`, définissant précisément quelles actions sont autorisées sur quelles ressources : `Role` = limité à un namespace ; `ClusterRole` = cluster-wide. Règle : Role pour les apps métier, ClusterRole pour les composants d'infra (monitoring, ingress controllers)

> ⚠️ Depuis 1.22 : plus de Secrets long-lived auto-créés → **tokens éphémères** générés via la `TokenRequest API` (rotation automatique, expiration configurable) et montés via un `projected volume`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-sa
spec:
  serviceAccountName: my-service-account  # Utilisation explicite du Service Account
  automountServiceAccountToken: false    # Désactive le montage du token pour ce Pod
  containers:
  - name: app-container
    image: nginx
```

```bash
# Vérifier les permissions effectives d'un Service Account
kubectl auth can-i get pods --as=system:serviceaccount:default:my-service-account
```

# 8. Taints & Tolerations

- Une `Taint` (`key`, `value` optionnelle, `effect`) repousse les Pods sans `Toleration` correspondante ; `NoSchedule` et `PreferNoSchedule` n'agissent qu'à la planification, `NoExecute` expulse aussi les Pods déjà en cours d'exécution
- Une `Toleration` autorise un Pod à être planifié sur un nœud tainté, elle ne le force pas à y aller : pour forcer le placement, combiner taint + toleration + `nodeAffinity`

```yaml
# Exemple avec effet NoExecute et tolerationSeconds
apiVersion: v1
kind: Pod
metadata:
  name: resilient-app
spec:
  tolerations:
  - key: "node.kubernetes.io/unreachable"  # Taint automatique pour nœud inaccessible
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 300  # Attendre 5 minutes avant éviction ; laisse le temps à une coupure réseau temporaire de se rétablir avant de replanifier
  - key: "node.kubernetes.io/not-ready"    # Taint automatique pour nœud non prêt
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 300
  containers:
  - name: web-server
    image: nginx
```

```bash
# Appliquer une taint sur un nœud
kubectl taint nodes worker-1 dedicated=database:NoSchedule

# Retirer une taint d'un nœud (noter le - à la fin)
kubectl taint nodes worker-1 dedicated=database:NoSchedule-
```

# 9. Node Selectors

- Un `nodeSelector` fonctionne comme un filtre sur les `labels` des nœuds : seuls les nœuds possédant **tous** les labels spécifiés peuvent héberger le Pod (logique ET obligatoire)
- Correspondances exactes et opérations ET uniquement, sans logique plus complexe (OU, NOT, expressions conditionnelles)
- Si aucun nœud ne possède les labels requis, le Pod reste en `Pending` indéfiniment sans message d'erreur dans `kubectl get pods` : diagnostiquer avec `kubectl describe pod` (section Events)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-frontend
spec:
  nodeSelector:
    environment: production  # Le nœud DOIT avoir ce label exact
    tier: web               # ET ce label aussi (logique AND)
  containers:
  - name: nginx
    image: nginx:1.27
```

```bash
# Ajouter un label à un nœud
kubectl label nodes worker-1 disk-type=ssd

# Supprimer un label d'un nœud (noter le - à la fin)
kubectl label nodes worker-1 disk-type-
```

# 10. Node Affinity

- Les règles `requiredDuringSchedulingIgnoredDuringExecution` fonctionnent comme des contraintes obligatoires que le `scheduler` doit respecter, bloquant la planification si aucun nœud ne correspond ; le suffixe `IgnoredDuringExecution` signifie que si un nœud perd son label après le placement du Pod, ce dernier n'est pas expulsé
- L'opérateur `In` accepte une liste de valeurs, avec une logique OU au sein d'un même critère
- Les `nodeSelectorTerms` peuvent contenir plusieurs `matchExpressions` : plusieurs expressions dans un même terme = logique **ET** (toutes doivent être vraies) ; plusieurs termes dans `nodeSelectorTerms` = logique **OU** (un seul terme doit être satisfait)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: environment
            operator: In
            values: ["production", "staging"]  # Prod OU staging
          - key: maintenance
            operator: DoesNotExist  # Pas en maintenance
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values: ["us-west-2a"]  # Préfère cette zone
  containers:
  - name: nginx
    image: nginx
```

```bash
# Déboguer les échecs de planification liés à l'affinité
kubectl get events --field-selector reason=FailedScheduling
```