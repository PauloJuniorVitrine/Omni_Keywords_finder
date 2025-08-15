# Práticas de Deploy

Este documento detalha as práticas de deploy do Omni Keywords Finder.

## Kubernetes

### 1. Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: omni-keywords
  labels:
    name: omni-keywords
    environment: production
```

### 2. ConfigMaps

```yaml
# k8s/configmaps.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: omni-keywords-config
  namespace: omni-keywords
data:
  APP_NAME: "Omni Keywords Finder"
  API_PREFIX: "/api/v1"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  MODEL_PATH: "/app/models/keyword_model"
  BATCH_SIZE: "32"
  DEVICE: "cpu"
```

### 3. Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: omni-keywords-secrets
  namespace: omni-keywords
type: Opaque
data:
  SECRET_KEY: <base64-encoded>
  MONGODB_URL: <base64-encoded>
  REDIS_URL: <base64-encoded>
```

### 4. Deployments

```yaml
# k8s/deployments.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-keywords-api
  namespace: omni-keywords
spec:
  replicas: 3
  selector:
    matchLabels:
      app: omni-keywords-api
  template:
    metadata:
      labels:
        app: omni-keywords-api
    spec:
      containers:
        - name: api
          image: omni-keywords/api:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: omni-keywords-config
            - secretRef:
                name: omni-keywords-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-keywords-ml
  namespace: omni-keywords
spec:
  replicas: 2
  selector:
    matchLabels:
      app: omni-keywords-ml
  template:
    metadata:
      labels:
        app: omni-keywords-ml
    spec:
      containers:
        - name: ml
          image: omni-keywords/ml:latest
          ports:
            - containerPort: 8001
          envFrom:
            - configMapRef:
                name: omni-keywords-config
            - secretRef:
                name: omni-keywords-secrets
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8001
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8001
            initialDelaySeconds: 5
            periodSeconds: 5
```

### 5. Services

```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: omni-keywords-api
  namespace: omni-keywords
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
      name: http
  selector:
    app: omni-keywords-api
---
apiVersion: v1
kind: Service
metadata:
  name: omni-keywords-ml
  namespace: omni-keywords
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 8001
      protocol: TCP
      name: http
  selector:
    app: omni-keywords-ml
```

### 6. Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: omni-keywords
  namespace: omni-keywords
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - api.omni-keywords.com
      secretName: omni-keywords-tls
  rules:
    - host: api.omni-keywords.com
      http:
        paths:
          - path: /api/v1
            pathType: Prefix
            backend:
              service:
                name: omni-keywords-api
                port:
                  number: 80
```

## Helm

### 1. Chart

```yaml
# helm/omni-keywords/Chart.yaml
apiVersion: v2
name: omni-keywords
description: Omni Keywords Finder
type: application
version: 1.0.0
appVersion: "1.0.0"
```

### 2. Values

```yaml
# helm/omni-keywords/values.yaml
replicaCount: 3

image:
  repository: omni-keywords
  tag: latest
  pullPolicy: IfNotPresent

api:
  name: api
  port: 8000
  resources:
    requests:
      memory: 512Mi
      cpu: 250m
    limits:
      memory: 1Gi
      cpu: 500m

ml:
  name: ml
  port: 8001
  resources:
    requests:
      memory: 1Gi
      cpu: 500m
    limits:
      memory: 2Gi
      cpu: 1000m

ingress:
  enabled: true
  host: api.omni-keywords.com
  tls: true
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
```

### 3. Templates

```yaml
# helm/omni-keywords/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-{{ .Values.api.name }}
  namespace: {{ .Release.Namespace }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}-{{ .Values.api.name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-{{ .Values.api.name }}
    spec:
      containers:
        - name: {{ .Values.api.name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.api.port }}
          resources:
            {{- toYaml .Values.api.resources | nindent 12 }}
```

## Terraform

### 1. Provider

```hcl
# terraform/provider.tf
provider "kubernetes" {
  config_path = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}
```

### 2. Variables

```hcl
# terraform/variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "replica_count" {
  description = "Number of replicas"
  type        = number
  default     = 3
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}
```

### 3. Resources

```hcl
# terraform/main.tf
resource "kubernetes_namespace" "omni_keywords" {
  metadata {
    name = "omni-keywords"
    labels = {
      name        = "omni-keywords"
      environment = var.environment
    }
  }
}

resource "helm_release" "omni_keywords" {
  name       = "omni-keywords"
  repository = "https://charts.omni-keywords.com"
  chart      = "omni-keywords"
  namespace  = kubernetes_namespace.omni_keywords.metadata[0].name

  set {
    name  = "replicaCount"
    value = var.replica_count
  }

  set {
    name  = "image.tag"
    value = var.image_tag
  }
}
```

## Observações

- Seguir padrões
- Manter documentação
- Testar adequadamente
- Otimizar performance
- Garantir segurança
- Monitorar sistema
- Revisar código
- Manter histórico
- Documentar decisões
- Revisar periodicamente 