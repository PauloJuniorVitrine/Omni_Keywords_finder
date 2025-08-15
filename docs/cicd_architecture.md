# Arquitetura de CI/CD

Este documento detalha a arquitetura de CI/CD do Omni Keywords Finder.

## Pipelines

### Desenvolvimento
```yaml
# .github/workflows/development.yml
name: Development Pipeline
on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install
      - name: Run tests
        run: |
          pytest
          npm test
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Run linters
        run: |
          flake8
          black --check .
          mypy .
          eslint .
          prettier --check .
```

### Produção
```yaml
# .github/workflows/production.yml
name: Production Pipeline
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker images
        run: |
          docker build -t omni-keywords-finder:latest .
      - name: Push to registry
        run: |
          docker push ${{ secrets.REGISTRY }}/omni-keywords-finder:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          kubectl apply -f k8s/production/
```

## Ambientes

### Desenvolvimento
```yaml
# k8s/development/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-keywords-finder
  namespace: development
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: app
        image: omni-keywords-finder:dev
        env:
        - name: ENVIRONMENT
          value: development
        - name: DEBUG
          value: "true"
```

### Staging
```yaml
# k8s/staging/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-keywords-finder
  namespace: staging
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: app
        image: omni-keywords-finder:staging
        env:
        - name: ENVIRONMENT
          value: staging
        - name: DEBUG
          value: "false"
```

### Produção
```yaml
# k8s/production/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-keywords-finder
  namespace: production
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: omni-keywords-finder:latest
        env:
        - name: ENVIRONMENT
          value: production
        - name: DEBUG
          value: "false"
```

## Estratégias de Deploy

### Blue-Green
```yaml
# k8s/production/blue-green.yml
apiVersion: networking.k8s.io/v1
kind: Service
metadata:
  name: omni-keywords-finder
spec:
  selector:
    app: omni-keywords-finder
    version: blue
  ports:
  - port: 80
    targetPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-keywords-finder-blue
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: omni-keywords-finder
        version: blue
```

### Canary
```yaml
# k8s/production/canary.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-keywords-finder-canary
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: omni-keywords-finder
        version: canary
---
apiVersion: networking.k8s.io/v1
kind: Service
metadata:
  name: omni-keywords-finder-canary
spec:
  selector:
    app: omni-keywords-finder
    version: canary
```

## Monitoramento

### Health Checks
```yaml
# k8s/production/health.yml
apiVersion: v1
kind: Service
metadata:
  name: omni-keywords-finder
spec:
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: omni-keywords-finder
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: omni-keywords-finder
  annotations:
    nginx.ingress.kubernetes.io/healthcheck-path: /health
    nginx.ingress.kubernetes.io/healthcheck-interval: "10s"
```

### Métricas
```yaml
# k8s/production/metrics.yml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: omni-keywords-finder
spec:
  selector:
    matchLabels:
      app: omni-keywords-finder
  endpoints:
  - port: metrics
    interval: 15s
```

## Observações

1. Pipelines automatizados
2. Ambientes isolados
3. Deploy gradual
4. Rollback automático
5. Monitoramento contínuo
6. Testes automatizados
7. Linting e formatação
8. Cobertura de código
9. Documentação atualizada
10. Segurança reforçada 