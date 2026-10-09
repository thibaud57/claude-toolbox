# 1. Configuration Kubernetes : Commandes & Arguments

- Le champ `command` dans Kubernetes remplace l'`ENTRYPOINT` du Dockerfile et définit la commande principale à exécuter dans le conteneur
- Le champ `args` remplace la directive `CMD` du Dockerfile et fournit les arguments passés à la commande principale
- Si seul `command` est spécifié, il sera exécuté sans arguments supplémentaires, ignorant complètement les paramètres du Dockerfile
- Lorsque seul `args` est défini, les arguments sont ajoutés à l'`ENTRYPOINT` existant de l'image Docker ; si l'image n'a pas d'`ENTRYPOINT`, utiliser `command` + `args` ensemble
- La combinaison `command` + `args` permet un contrôle total sur l'exécution, remplaçant à la fois `ENTRYPOINT` et `CMD`
- Les arguments peuvent être passés sous forme de liste ou de chaîne de caractères, la syntaxe liste étant recommandée pour éviter les problèmes d'échappement
- L'utilisation de variables d'environnement dans les commandes et arguments est possible avec la syntaxe `$(VARIABLE_NAME)`, résolue par le kubelet avant le lancement (pas par le shell), et uniquement si la variable référencée est déclarée dans le même bloc `env`

```yaml
# Exemple basique avec command et args séparés
apiVersion: v1
kind: Pod
metadata:
  name: command-demo
spec:
  containers:
  - name: command-demo-container
    image: debian
    command: ["printenv"]
    args: ["HOSTNAME", "KUBERNETES_PORT"]
```

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

```bash
# Vérification du pod en cours d'exécution
kubectl get pods command-demo

# Consultation des logs pour voir la sortie de la commande
kubectl logs command-demo

# Exécution interactive pour tester différentes commandes
kubectl exec -it print-greeting -- /bin/sh
```

# 2. Variables d'Environnement

- Les variables d'environnement dans Kubernetes se définissent via le champ `env` dans la spécification du conteneur, permettant de passer des configurations à l'application
- La méthode `value` permet de définir directement une valeur statique pour la variable, idéale pour les paramètres de configuration simples
- L'utilisation de `valueFrom` offre des sources dynamiques permettant de découpler la configuration des spécifications de pod
- L'`envFrom` permet d'importer en masse toutes les clés d'une source externe comme variables d'environnement, simplifiant la gestion des configurations complexes
- En cas de collision de clés : `env` est prioritaire sur `envFrom` ; entre deux sources `envFrom`, la dernière déclarée l'emporte
- Les variables peuvent référencer d'autres variables d'environnement ou des métadonnées du pod grâce à la syntaxe `$(VARIABLE_NAME)`

```yaml
# Exemple avec des variables d'environnement directes
apiVersion: v1
kind: Pod
metadata:
  name: env-demo
spec:
  containers:
  - name: app-container
    image: nginx
    env:
    - name: DATABASE_URL
      value: "postgresql://localhost:5432/myapp"
    - name: LOG_LEVEL
      value: "INFO"
    - name: PORT
      value: "8080"
```

# 3. ConfigMap : Gestion des Configurations Non-Sensibles

- `ConfigMap` stocke des données de configuration non-sensibles (paires clé-valeur ou fichiers entiers) ; séparation config/image, pas de rebuild nécessaire pour changer la config
- Injection dans un Pod : variable par variable via `valueFrom.configMapKeyRef`, en masse via `envFrom.configMapRef`, ou montée comme fichier via `volumeMounts`
- **`immutable: true`** (stable v1.21) : empêche toute modification ; améliore les performances en désactivant le watch de l'objet par le kubelet
- **Mise à jour à chaud** : une ConfigMap montée via `volumeMount` est propagée automatiquement aux Pods en cours (~1 minute) ; injectée via `env` ou `envFrom`, elle n'est **jamais** propagée automatiquement : redémarrage du Pod obligatoire

> ⚠️ `immutable: true` est irréversible : impossible de repasser à mutable, il faut supprimer et recréer la ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
immutable: true  # stable v1.21
data:
  DATABASE_HOST: "mysql.example.com"
  DATABASE_PORT: "3306"
  LOG_LEVEL: "info"
---
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: app-container
    image: my-app:latest
    envFrom:
    - configMapRef:
        name: app-config
```

```bash
# Créer une ConfigMap depuis des valeurs directes
kubectl create configmap app-config --from-literal=DATABASE_HOST=mysql.example.com --from-literal=LOG_LEVEL=info

# Créer une ConfigMap depuis un fichier
kubectl create configmap app-config --from-file=config.properties

# Lister toutes les ConfigMaps
kubectl get configmaps

# Afficher le détail d'une ConfigMap
kubectl describe configmap app-config

# Modifier une ConfigMap existante
kubectl edit configmap app-config

# Supprimer une ConfigMap
kubectl delete configmap app-config
```

# 4. Secret : Gestion des Données Sensibles

- `Secret` stocke des données sensibles (mots de passe, tokens, certificats) ; encodage base64, **pas un chiffrement** : `kubectl get secret -o yaml` expose les valeurs immédiatement décodables. Vraie protection = RBAC (restreindre qui peut lire les Secrets) + chiffrement etcd-at-rest en production
- Trois types courants : `Opaque` (générique), `kubernetes.io/dockerconfigjson` (registry privé), `kubernetes.io/tls` (certificats TLS)
- **`immutable: true`** (stable v1.21) : même bénéfice que pour les ConfigMaps ; empêche les modifications accidentelles de secrets critiques

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
immutable: true  # stable v1.21
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
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
```

```bash
# Créer un Secret générique avec des valeurs directes
kubectl create secret generic db-credentials --from-literal=username=admin --from-literal=password=secret123

# Créer un Secret depuis un fichier
kubectl create secret generic ssl-certs --from-file=cert.pem --from-file=key.pem

# Créer un Secret pour Docker registry
kubectl create secret docker-registry regcred --docker-server=registry.example.com --docker-username=user --docker-password=pass

# Lister tous les Secrets
kubectl get secrets

# Afficher le détail d'un Secret (données masquées)
kubectl describe secret db-credentials

# Décoder les valeurs d'un Secret
kubectl get secret db-credentials -o jsonpath='{.data.username}' | base64 --decode

# Supprimer un Secret
kubectl delete secret db-credentials
```

# 5. Security Contexts

- Peut être défini au niveau `Pod` (s'applique à tous ses conteneurs) ou au niveau `Container` (prioritaire sur le Pod), utiles en combinaison
- **`runAsUser`** / **`runAsGroup`** / **`fsGroup`** : contrôle l'UID, GID des processus, et le groupe propriétaire des volumes montés ; `fsGroup` s'applique uniquement aux volumes (pas aux processus) : sans lui, une app non-root ne peut pas écrire dans un volume monté
- **Linux Capabilities** : pattern recommandé = `capabilities.drop: [ALL]` + `add: [NET_BIND_SERVICE]`, pour un accès précis sans droits root globaux. `NET_BIND_SERVICE` est nécessaire pour écouter sur un port < 1024 ; alternative : configurer l'app sur un port > 1024 et faire la translation dans le Service
- **`readOnlyRootFilesystem: true`** : système de fichiers racine en lecture seule, empêche les modifications non autorisées ; bloque aussi l'écriture dans `/tmp` : les JVM et frameworks qui génèrent des fichiers temporaires crashent, monter un `emptyDir` sur ces paths (`/tmp`, `/var/cache`...)
- **`seccompProfile`** (stable v1.19) : filtre les appels système ; `type: RuntimeDefault` offre une baseline sécurisée sans configuration spécifique
- **`appArmorProfile`** (GA v1.31) : champ natif `securityContext.appArmorProfile` remplace les annotations `container.apparmor.security.beta.kubernetes.io/...`
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
      type: RuntimeDefault  # stable v1.19
  containers:
  - name: demo-container
    image: nginx
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      appArmorProfile:
        type: RuntimeDefault  # GA v1.31, remplace les annotations
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-level-security
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
  containers:
  - name: app-container
    image: alpine
    command: ["sleep", "3600"]
```

```bash
# Vérifier sous quel utilisateur s'exécute un processus dans le conteneur
kubectl exec security-context-demo -- whoami

# Examiner l'ID utilisateur et les groupes actifs
kubectl exec security-context-demo -- id

# Vérifier les permissions sur les fichiers montés
kubectl exec security-context-demo -- ls -la /var/run/

# Tester l'accès en écriture sur le système de fichiers racine
kubectl exec security-context-demo -- touch /test-file

# Vérifier les capacités Linux actives du conteneur
kubectl exec security-context-demo -- grep Cap /proc/self/status

# Examiner les détails complets du security context appliqué
kubectl describe pod security-context-demo

# Vérifier si un conteneur s'exécute en mode privilégié
kubectl get pod security-context-demo -o jsonpath='{.spec.containers[0].securityContext}'
```

# 6. Resource Requirements

- Les Resource Requirements permettent de spécifier les besoins en ressources (`cpu` et `memory`) pour chaque conteneur, garantissant une allocation appropriée et évitant la surcharge des nœuds
- La section `requests` définit la quantité minimale de ressources garantie au conteneur, utilisée par le `scheduler` pour décider sur quel nœud placer le `Pod`
- La section `limits` établit la quantité maximale de ressources qu'un conteneur peut consommer, empêchant qu'il monopolise les ressources du nœud
- Les unités de `CPU` peuvent être exprimées en millicores (`m`) où `1000m = 1 CPU`, ou en décimales (`0.5 = 500m`), permettant une granularité fine dans l'allocation
- La `memory` s'exprime en bytes avec des suffixes comme `Mi` (mébioctets), `Gi` (gibioctets), ou `Ki` (kibioctets), suivant la notation binaire standard
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

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: development
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
```

```bash
# Vérifier la consommation de ressources d'un pod en temps réel
kubectl top pod resource-demo

# Observer les métriques détaillées d'un pod
kubectl describe pod resource-demo

# Vérifier les quotas d'un namespace
kubectl describe resourcequota compute-quota -n development

# Surveiller l'utilisation des nœuds
kubectl top nodes

# Examiner les événements liés aux ressources (OOMKilled, etc.)
kubectl get events --field-selector reason=Killing
```

# 7. Service Accounts

- Un `Service Account` fournit une identité pour les processus qui s'exécutent dans un `Pod`, permettant d'authentifier et d'autoriser l'accès aux ressources de l'`API Server` Kubernetes
- Chaque `namespace` possède un Service Account par défaut nommé `default`, automatiquement assigné aux Pods qui n'en spécifient pas explicitement un autre
- Depuis K8s 1.22, les tokens sont des **tokens éphémères** générés via la `TokenRequest API` (rotation automatique, expiration configurable) montés via un `projected volume` ; plus de Secrets long-lived auto-créés
- L'attribut `automountServiceAccountToken` peut être défini à `false` au niveau du Pod ou du Service Account pour empêcher le montage automatique du token, renforçant la sécurité ; règle pratique : mettre `false` par défaut sur toutes les apps métier qui n'appellent pas l'API Kubernetes directement
- Les Role-Based Access Control (RBAC) s'appliquent aux Service Accounts via des `ClusterRoleBinding` ou `RoleBinding`, définissant précisément quelles actions sont autorisées sur quelles ressources : `Role` = limité à un namespace ; `ClusterRole` = cluster-wide. Règle : Role pour les apps métier, ClusterRole pour les composants d'infra (monitoring, ingress controllers)
- Un Service Account peut être associé à des `ImagePullSecrets` pour permettre l'extraction d'images depuis des registries privés nécessitant une authentification
- Les `annotations` sur les Service Accounts permettent l'intégration avec des systèmes d'identité externes comme AWS IAM via des mécanismes comme `eks.amazonaws.com/role-arn`

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: default
  annotations:
    # Exemple d'annotation pour AWS EKS IAM Role
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/MyRole
imagePullSecrets:
- name: my-registry-secret  # Secret pour accéder à un registry privé
automountServiceAccountToken: false  # Désactiver par défaut, monter explicitement via projected volume si besoin
```

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

```yaml
# Exemple de RBAC pour autoriser un Service Account
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]        # API group vide pour les ressources core
  resources: ["pods"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-service-account  # Le Service Account qui reçoit les permissions
  namespace: default
roleRef:
  kind: Role
  name: pod-reader         # Le Role qui définit les permissions
  apiGroup: rbac.authorization.k8s.io
```

```bash
# Lister tous les Service Accounts du namespace courant
kubectl get serviceaccounts

# Examiner les détails d'un Service Account spécifique
kubectl describe serviceaccount my-service-account

# Vérifier le token monté dans un Pod
kubectl exec pod-with-sa -- cat /var/run/secrets/kubernetes.io/serviceaccount/token

# Tester l'accès à l'API depuis l'intérieur du Pod
kubectl exec pod-with-sa -- curl -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" https://kubernetes.default.svc/api/v1/namespaces/default/pods

# Créer un Service Account rapidement
kubectl create serviceaccount monitoring-sa

# Vérifier les permissions effectives d'un Service Account
kubectl auth can-i get pods --as=system:serviceaccount:default:my-service-account

# Examiner les secrets associés à un Service Account
kubectl get serviceaccount my-service-account -o yaml
```

# 8. Taints & Tolerations

- Les `Taints` (littéralement "souillures" ou "taches") sont des marqueurs appliqués aux nœuds qui repoussent certains Pods, empêchant leur planification sur ces nœuds sauf si les Pods possèdent les `Tolerations` correspondantes
- Les `Tolerations` sont des attributs configurés au niveau des Pods qui leur permettent d'être planifiés sur des nœuds ayant des `Taints` spécifiques, créant ainsi un système de correspondance explicite
- Chaque `Taint` est composée de trois éléments : une `key` (clé), une `value` (valeur optionnelle), et un `effect` qui détermine le comportement (`NoSchedule`, `PreferNoSchedule`, ou `NoExecute`)
- L'effet `NoSchedule` empêche complètement la planification de nouveaux Pods sur le nœud, tandis que `PreferNoSchedule` décourage cette planification sans l'interdire formellement
- L'effet `NoExecute` va plus loin en expulsant les Pods déjà en cours d'exécution qui n'ont pas de `Toleration` correspondante, permettant une éviction active des charges de travail
- Une `Toleration` peut être exacte (correspondance parfaite de la clé et valeur) ou utiliser l'opérateur `Exists` pour tolérer toute valeur associée à une clé donnée
- Les `Taints` sont couramment utilisées pour dédier des nœuds à des usages spécifiques (GPU, stockage haute performance) ou pour marquer des nœuds en maintenance ou défaillants
- Une `Toleration` autorise un Pod à être planifié sur un nœud tainté, elle ne le force pas à y aller : pour forcer le placement, combiner taint + toleration + `nodeAffinity`

```yaml
# Application d'une Taint sur un nœud (via kubectl)
# kubectl taint nodes node1 gpu=nvidia:NoSchedule
# Cette commande marque le nœud avec une taint indiquant qu'il est réservé aux workloads GPU

apiVersion: v1
kind: Pod
metadata:
  name: gpu-workload
spec:
  tolerations:
  - key: "gpu"              # Clé correspondant à la taint du nœud
    operator: "Equal"       # Opérateur de comparaison (Equal ou Exists)
    value: "nvidia"         # Valeur qui doit correspondre exactement
    effect: "NoSchedule"    # Effet que cette toleration peut gérer
  - key: "special-node"     # Exemple avec opérateur Exists
    operator: "Exists"      # Tolère n'importe quelle valeur pour cette clé
    effect: "NoSchedule"
  containers:
  - name: cuda-app
    image: nvidia/cuda:latest
```

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

```yaml
# Configuration pour un Pod système qui doit tourner partout
apiVersion: v1
kind: Pod
metadata:
  name: system-monitor
spec:
  tolerations:
  - operator: "Exists"      # Tolère toutes les taints existantes
    effect: "NoSchedule"    # Pour tous les effets NoSchedule
  - operator: "Exists"      # Séparé car on veut aussi gérer NoExecute
    effect: "NoExecute"
  containers:
  - name: monitoring-agent
    image: prometheus/node-exporter
```

```bash
# Appliquer une taint sur un nœud spécifique
kubectl taint nodes worker-1 dedicated=database:NoSchedule

# Voir les taints actuelles d'un nœud
kubectl describe node worker-1 | grep -i taint

# Retirer une taint d'un nœud (noter le - à la fin)
kubectl taint nodes worker-1 dedicated=database:NoSchedule-

# Lister tous les nœuds avec leurs taints
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints[*].key

# Appliquer une taint avec effet NoExecute pour maintenance
kubectl taint nodes worker-2 maintenance=planned:NoExecute

# Vérifier quels Pods sont planifiés sur un nœud avec taint
kubectl get pods --field-selector spec.nodeName=worker-1

# Drainer un nœud avant maintenance (combiné avec taints)
kubectl drain worker-1 --ignore-daemonsets --delete-emptydir-data

# Marquer un nœud comme non planifiable (ajoute une taint spéciale)
kubectl cordon worker-1
```

# 9. Node Selectors

- Les `Node Selectors` constituent le mécanisme le plus simple pour contraindre un Pod à s'exécuter sur des nœuds possédant des caractéristiques spécifiques, en utilisant un système de correspondance basé sur les `labels` des nœuds
- Cette fonctionnalité repose entièrement sur les `labels` Kubernetes, qui sont des paires clé-valeur attachées aux nœuds pour identifier leurs propriétés physiques ou logiques (type de hardware, zone géographique, environnement)
- Un `nodeSelector` dans la spécification d'un Pod fonctionne comme un filtre : seuls les nœuds possédant **tous** les labels spécifiés peuvent héberger ce Pod, créant une logique ET obligatoire
- Kubernetes applique automatiquement certains labels standards sur les nœuds, notamment `kubernetes.io/hostname`, `kubernetes.io/os`, et `kubernetes.io/arch`, permettant un ciblage immédiat sans configuration supplémentaire
- Les labels personnalisés permettent de catégoriser les nœuds selon vos besoins métier, comme `environment=production`, `disk-type=ssd`, ou `gpu=tesla-v100`, offrant une flexibilité totale dans l'organisation
- Contrairement aux `Taints/Tolerations` qui repoussent par défaut, les Node Selectors attirent positivement les Pods vers les nœuds correspondants, créant une approche complémentaire de placement
- Cette méthode présente une limitation importante : elle ne supporte que des correspondances exactes et des opérations ET, sans possibilité de logique plus complexe (OU, NOT, expressions conditionnelles)
- Si aucun nœud ne possède les labels requis, le Pod reste en `Pending` indéfiniment sans message d'erreur dans `kubectl get pods` : diagnostiquer avec `kubectl describe pod` (section Events)

```yaml
# Premier exemple : ciblage d'un environnement spécifique
# Ce Pod ne pourra s'exécuter que sur des nœuds étiquetés comme "production"
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
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
```

```yaml
# Deuxième exemple : sélection basée sur le type de hardware
# Utilisation pour des workloads nécessitant des ressources spécifiques
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-training
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml-training
  template:
    metadata:
      labels:
        app: ml-training
    spec:
      nodeSelector:
        accelerator: nvidia-tesla-v100  # Nœuds avec GPU spécifique
        disk-type: ssd                  # ET stockage SSD haute performance
        zone: us-west-2a               # ET dans une zone géographique précise
      containers:
      - name: tensorflow
        image: tensorflow/tensorflow:latest-gpu
        resources:
          limits:
            nvidia.com/gpu: 1  # Réservation d'un GPU
```

```yaml
# Troisième exemple : utilisation des labels Kubernetes standards
# Ciblage basé sur l'architecture et le système d'exploitation
apiVersion: v1
kind: Pod
metadata:
  name: architecture-specific
spec:
  nodeSelector:
    kubernetes.io/os: linux           # Système d'exploitation Linux
    kubernetes.io/arch: amd64         # Architecture 64 bits
    node.kubernetes.io/instance-type: c5.large  # Type d'instance cloud spécifique
  containers:
  - name: system-monitor
    image: prometheus/node-exporter
    ports:
    - containerPort: 9100
```

```bash
# Lister tous les nœuds avec leurs labels pour comprendre les options disponibles
kubectl get nodes --show-labels

# Examiner les labels d'un nœud spécifique de manière détaillée
kubectl describe node worker-1

# Ajouter un label personnalisé à un nœud pour le catégoriser
kubectl label nodes worker-1 disk-type=ssd

# Ajouter plusieurs labels en une fois pour caractériser complètement un nœud
kubectl label nodes worker-2 environment=production tier=database zone=us-east-1a

# Vérifier qu'un Pod utilise correctement son nodeSelector
kubectl describe pod web-frontend

# Voir sur quels nœuds vos Pods sont actuellement planifiés
kubectl get pods -o wide

# Supprimer un label d'un nœud (noter le - à la fin)
kubectl label nodes worker-1 disk-type-

# Filtrer les nœuds selon un label spécifique
kubectl get nodes -l environment=production

# Vérifier pourquoi un Pod reste en état Pending (souvent lié aux nodeSelectors)
kubectl describe pod web-frontend | grep -A 10 Events

# Lister tous les Pods utilisant un nodeSelector spécifique
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeSelector}{"\n"}{end}'
```

# 10. Node Affinity

- La `Node Affinity` est l'évolution avancée des Node Selectors, permettant des règles de placement plus sophistiquées avec des opérateurs comme `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, et `Lt`
- Les règles `requiredDuringSchedulingIgnoredDuringExecution` fonctionnent comme des contraintes obligatoires que le `scheduler` doit respecter, bloquant la planification si aucun nœud ne correspond ; le suffixe `IgnoredDuringExecution` signifie que si un nœud perd son label après le placement du Pod, ce dernier n'est pas expulsé
- Les règles `preferredDuringSchedulingIgnoredDuringExecution` expriment des préférences avec des `weights` (1-100), influençant le choix sans bloquer la planification si les critères ne peuvent être satisfaits
- L'opérateur `In` permet de spécifier une liste de valeurs acceptables, créant une logique OU au sein d'un même critère, tandis que `NotIn` exclut explicitement certaines valeurs
- Les `nodeSelectorTerms` peuvent contenir plusieurs `matchExpressions` : plusieurs expressions dans un même terme = logique **ET** (toutes doivent être vraies) ; plusieurs termes dans `nodeSelectorTerms` = logique **OU** (un seul terme doit être satisfait)
- Les opérateurs numériques `Gt` (greater than) et `Lt` (less than) permettent des comparaisons sur des valeurs numériques stockées dans les labels des nœuds
- La `Node Affinity` offre une expressivité bien supérieure aux Node Selectors mais avec une complexité de configuration proportionnellement plus élevée

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
# Examiner les règles d'affinité appliquées à un Pod
kubectl describe pod web-app | grep -A 10 "Node-Selectors\|Affinity"

# Voir la répartition des Pods selon les nœuds
kubectl get pods -o wide

# Analyser pourquoi un Pod reste Pending (contraintes d'affinité non satisfaites)
kubectl describe pod web-app | grep Events

# Lister les nœuds avec leurs labels pour comprendre les critères disponibles
kubectl get nodes --show-labels

# Tester quels nœuds correspondent à un critère spécifique
kubectl get nodes -l environment=production

# Déboguer les échecs de planification liés à l'affinité
kubectl get events --field-selector reason=FailedScheduling
```