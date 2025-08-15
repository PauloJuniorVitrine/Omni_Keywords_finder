# Arquitetura de Infraestrutura

Este documento detalha a arquitetura de infraestrutura do Omni Keywords Finder.

## Clusters

### Kubernetes
```yaml
# k8s/cluster.yml
apiVersion: v1
kind: Namespace
metadata:
  name: omni-keywords-finder
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: omni-keywords-finder
  namespace: omni-keywords-finder
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: omni-keywords-finder
  namespace: omni-keywords-finder
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

### Nodes
```yaml
# k8s/nodes.yml
apiVersion: v1
kind: Node
metadata:
  name: worker-1
  labels:
    node-role.kubernetes.io/worker: "true"
    node-type: general
spec:
  taints:
  - key: node-type
    value: general
    effect: NoSchedule
```

## Serviços

### API
```yaml
# k8s/services/api.yml
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: omni-keywords-finder
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: api
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: omni-keywords-finder
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: omni-keywords-finder/api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
```

### ML
```yaml
# k8s/services/ml.yml
apiVersion: v1
kind: Service
metadata:
  name: ml
  namespace: omni-keywords-finder
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: ml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml
  namespace: omni-keywords-finder
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml
  template:
    metadata:
      labels:
        app: ml
    spec:
      containers:
      - name: ml
        image: omni-keywords-finder/ml:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "1000m"
            memory: "2Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
```

## Armazenamento

### MongoDB
```yaml
# k8s/storage/mongodb.yml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-data
  namespace: omni-keywords-finder
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: omni-keywords-finder
spec:
  serviceName: mongodb
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:4.4
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: data
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
```

### Redis
```yaml
# k8s/storage/redis.yml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-data
  namespace: omni-keywords-finder
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
  namespace: omni-keywords-finder
spec:
  serviceName: redis
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:6.2
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
```

## Rede

### Ingress
```yaml
# k8s/network/ingress.yml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: omni-keywords-finder
  namespace: omni-keywords-finder
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.omni-keywords-finder.com
    secretName: omni-keywords-finder-tls
  rules:
  - host: api.omni-keywords-finder.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
```

### Network Policies
```yaml
# k8s/network/policies.yml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
  namespace: omni-keywords-finder
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

## Observações

1. Alta disponibilidade
2. Escalabilidade horizontal
3. Isolamento de recursos
4. Backup automático
5. Monitoramento
6. Logs centralizados
7. Segurança reforçada
8. Performance otimizada
9. Custos controlados
10. Documentação atualizada 