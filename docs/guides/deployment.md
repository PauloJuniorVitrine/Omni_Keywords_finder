# Guia de Deployment

## Visão Geral

Este guia descreve o processo de deployment do Omni Keywords Finder em diferentes ambientes.

## Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.20+ (opcional)
- AWS CLI (para AWS)
- GCloud CLI (para GCP)
- Azure CLI (para Azure)

## Deployment Local

### 1. Usando Docker Compose

```bash
# Clone o repositório
git clone https://github.com/your-org/omni_keywords_finder.git
cd omni_keywords_finder

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env

# Inicie os serviços
docker-compose up -d
```

### 2. Verificação

```bash
# Verifique os logs
docker-compose logs -f

# Teste a API
curl http://localhost:8000/health
```

## Deployment em Produção

### 1. AWS (ECS)

```bash
# Configure as credenciais AWS
aws configure

# Crie o cluster ECS
aws ecs create-cluster --cluster-name omni-keywords

# Faça deploy
./scripts/deploy-aws.sh
```

### 2. GCP (GKE)

```bash
# Configure as credenciais GCP
gcloud auth login

# Crie o cluster GKE
gcloud container clusters create omni-keywords

# Faça deploy
./scripts/deploy-gcp.sh
```

### 3. Azure (AKS)

```bash
# Configure as credenciais Azure
az login

# Crie o cluster AKS
az aks create --name omni-keywords

# Faça deploy
./scripts/deploy-azure.sh
```

## Kubernetes

### 1. Configuração

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-keywords
spec:
  replicas: 3
  selector:
    matchLabels:
      app: omni-keywords
  template:
    metadata:
      labels:
        app: omni-keywords
    spec:
      containers:
      - name: api
        image: omni-keywords:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: uri
```

### 2. Deploy

```bash
# Aplique as configurações
kubectl apply -f kubernetes/

# Verifique o status
kubectl get pods
```

## CI/CD

### 1. GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build and Push
      run: ./scripts/build.sh
    - name: Deploy
      run: ./scripts/deploy.sh
```

### 2. GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - ./scripts/build.sh

test:
  stage: test
  script:
    - ./scripts/test.sh

deploy:
  stage: deploy
  script:
    - ./scripts/deploy.sh
```

## Monitoramento

### 1. Prometheus

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'omni-keywords'
    static_configs:
      - targets: ['localhost:8000']
```

### 2. Grafana

```bash
# Instale o Grafana
docker run -d -p 3000:3000 grafana/grafana

# Configure o dashboard
./scripts/configure-grafana.sh
```

## Backup

### 1. MongoDB

```bash
# Backup diário
./scripts/backup-mongodb.sh

# Restore
./scripts/restore-mongodb.sh
```

### 2. Redis

```bash
# Backup
./scripts/backup-redis.sh

# Restore
./scripts/restore-redis.sh
```

## Rollback

### 1. Kubernetes

```bash
# Rollback para versão anterior
kubectl rollout undo deployment/omni-keywords

# Verifique o status
kubectl rollout status deployment/omni-keywords
```

### 2. Docker Compose

```bash
# Rollback
docker-compose down
git checkout <previous-version>
docker-compose up -d
```

## Troubleshooting

### 1. Logs

```bash
# Kubernetes
kubectl logs -f deployment/omni-keywords

# Docker Compose
docker-compose logs -f
```

### 2. Métricas

```bash
# Prometheus
curl http://localhost:9090/metrics

# Grafana
http://localhost:3000
```

## Segurança

### 1. SSL/TLS

```bash
# Gere certificados
./scripts/generate-ssl.sh

# Configure nginx
./scripts/configure-nginx.sh
```

### 2. Firewall

```bash
# Configure regras
./scripts/configure-firewall.sh
```

## Manutenção

### 1. Updates

```bash
# Atualize imagens
./scripts/update-images.sh

# Verifique status
./scripts/check-status.sh
```

### 2. Limpeza

```bash
# Limpe logs antigos
./scripts/cleanup-logs.sh

# Limpe cache
./scripts/cleanup-cache.sh
``` 