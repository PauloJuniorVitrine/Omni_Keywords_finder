# 🚀 **GUIA DE DEPLOYMENT - OMNİ KEYWORDS FINDER**

## **📋 CONTROLE DE EXECUÇÃO**

**Tracing ID**: DEPLOYMENT_GUIDE_20250127_001  
**Data de Criação**: 2025-01-27  
**Versão**: 2.0.0  
**Status**: ✅ CONCLUÍDO  
**Responsável**: AI Assistant  

---

## **🎯 VISÃO GERAL**

Este guia fornece instruções completas para deploy do sistema Omni Keywords Finder em diferentes ambientes: desenvolvimento, staging e produção.

### **Ambientes Suportados**
- **🖥️ Local Development**: Docker Compose
- **🧪 Staging**: Kubernetes (GKE/AKS/EKS)
- **🏭 Production**: Kubernetes + Terraform
- **☁️ Cloud**: AWS, GCP, Azure

---

## **📋 PRÉ-REQUISITOS**

### **Ferramentas Necessárias**
```bash
# Version Control
git >= 2.30.0

# Container
docker >= 20.10.0
docker-compose >= 2.0.0

# Kubernetes
kubectl >= 1.24.0
helm >= 3.10.0

# Infrastructure
terraform >= 1.3.0
aws-cli >= 2.8.0 (para AWS)
gcloud >= 400.0.0 (para GCP)
az >= 2.40.0 (para Azure)

# Development
python >= 3.9.0
node >= 18.0.0
npm >= 8.0.0
```

### **Contas e Credenciais**
- **Cloud Provider**: AWS/GCP/Azure account
- **Container Registry**: Docker Hub, ECR, GCR, ACR
- **Domain**: DNS configurado
- **SSL Certificate**: Let's Encrypt ou comercial
- **Monitoring**: Grafana Cloud, DataDog, New Relic

---

## **🏠 DEPLOYMENT LOCAL (DEVELOPMENT)**

### **1. Clone do Repositório**
```bash
git clone https://github.com/your-org/omni-keywords-finder.git
cd omni-keywords-finder
```

### **2. Configuração de Ambiente**
```bash
# Copiar arquivos de configuração
cp .env.example .env
cp docker-compose.override.example.yml docker-compose.override.yml

# Editar variáveis de ambiente
nano .env
```

### **3. Variáveis de Ambiente (Development)**
```env
# Application
NODE_ENV=development
APP_ENV=local
APP_PORT=3000
API_PORT=8000

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=omni_keywords_dev
POSTGRES_USER=omni_user
POSTGRES_PASSWORD=dev_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT
JWT_SECRET=your-dev-secret-key
JWT_EXPIRES_IN=24h

# External APIs
GOOGLE_API_KEY=your-google-api-key
SEMRUSH_API_KEY=your-semrush-api-key
AHREFS_API_KEY=your-ahrefs-api-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### **4. Deploy com Docker Compose**
```bash
# Build das imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Logs em tempo real
docker-compose logs -f
```

### **5. Verificação**
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Frontend
open http://localhost:3000
```

---

## **🧪 DEPLOYMENT STAGING**

### **1. Configuração do Cluster Kubernetes**

#### **GKE (Google Cloud)**
```bash
# Criar cluster
gcloud container clusters create omni-staging \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10

# Configurar kubectl
gcloud container clusters get-credentials omni-staging --zone=us-central1-a
```

#### **EKS (AWS)**
```bash
# Criar cluster
eksctl create cluster \
  --name omni-staging \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 10 \
  --managed
```

### **2. Configuração de Namespace**
```bash
# Criar namespace
kubectl create namespace omni-staging

# Configurar context
kubectl config set-context --current --namespace=omni-staging
```

### **3. Configuração de Secrets**
```bash
# Criar secrets
kubectl create secret generic omni-secrets \
  --from-literal=postgres-password=staging-password \
  --from-literal=jwt-secret=staging-jwt-secret \
  --from-literal=google-api-key=your-google-api-key \
  --from-literal=semrush-api-key=your-semrush-api-key \
  --from-literal=ahrefs-api-key=your-ahrefs-api-key

# Verificar secrets
kubectl get secrets
```

### **4. Deploy com Helm**
```bash
# Adicionar repositório Helm
helm repo add omni https://charts.omni-keywords.com
helm repo update

# Instalar aplicação
helm install omni-staging omni/omni-keywords-finder \
  --namespace omni-staging \
  --values values-staging.yaml \
  --set environment=staging \
  --set domain=staging.omnikeywords.com

# Verificar deployment
helm list -n omni-staging
kubectl get pods -n omni-staging
```

### **5. Configuração de Ingress**
```yaml
# ingress-staging.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: omni-staging-ingress
  namespace: omni-staging
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - staging.omnikeywords.com
    secretName: omni-staging-tls
  rules:
  - host: staging.omnikeywords.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: omni-frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: omni-api-gateway
            port:
              number: 80
```

```bash
# Aplicar ingress
kubectl apply -f ingress-staging.yaml
```

---

## **🏭 DEPLOYMENT PRODUCTION**

### **1. Infraestrutura como Código (Terraform)**

#### **Configuração AWS**
```hcl
# main.tf
terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
module "vpc" {
  source = "./modules/vpc"
  
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
  azs         = var.availability_zones
}

# EKS Cluster
module "eks" {
  source = "./modules/eks"
  
  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  node_groups     = var.node_groups
}

# RDS Database
module "rds" {
  source = "./modules/rds"
  
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.database_subnets
  instance_class  = var.db_instance_class
  allocated_storage = var.db_allocated_storage
}

# ElastiCache Redis
module "redis" {
  source = "./modules/redis"
  
  environment = var.environment
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnets
  node_type   = var.redis_node_type
  num_cache_nodes = var.redis_num_nodes
}
```

#### **Variáveis de Produção**
```hcl
# variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "omni-production"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.xlarge"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.r6g.large"
}
```

### **2. Deploy da Infraestrutura**
```bash
# Inicializar Terraform
terraform init

# Planejar mudanças
terraform plan -var-file=production.tfvars

# Aplicar infraestrutura
terraform apply -var-file=production.tfvars

# Configurar kubectl
aws eks update-kubeconfig --region us-west-2 --name omni-production
```

### **3. Configuração de CI/CD**

#### **GitHub Actions Workflow**
```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
        coverage report --fail-under=85
    
    - name: Run security scan
      run: |
        bandit -r app/ -f json -o bandit-report.json
        safety check

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker images
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Update kubeconfig
      run: aws eks update-kubeconfig --region us-west-2 --name omni-production
    
    - name: Deploy to Kubernetes
      run: |
        helm upgrade --install omni-production omni/omni-keywords-finder \
          --namespace omni-production \
          --create-namespace \
          --values values-production.yaml \
          --set image.tag=${{ github.sha }} \
          --set environment=production \
          --set domain=omnikeywords.com
```

### **4. Configuração de Monitoramento**

#### **Prometheus Configuration**
```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "alert_rules.yml"
    
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
    
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name
```

#### **Grafana Dashboards**
```json
{
  "dashboard": {
    "title": "Omni Keywords Finder - Production",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ]
  }
}
```

---

## **🔧 CONFIGURAÇÕES ESPECÍFICAS**

### **Configuração de Banco de Dados**

#### **PostgreSQL**
```yaml
# postgres-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
data:
  postgresql.conf: |
    # Memory Configuration
    shared_buffers = 256MB
    effective_cache_size = 1GB
    work_mem = 4MB
    maintenance_work_mem = 64MB
    
    # WAL Configuration
    wal_buffers = 16MB
    checkpoint_completion_target = 0.9
    
    # Query Planner
    random_page_cost = 1.1
    effective_io_concurrency = 200
    
    # Logging
    log_statement = 'all'
    log_min_duration_statement = 1000
    log_checkpoints = on
    log_connections = on
    log_disconnections = on
```

#### **Redis**
```yaml
# redis-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
data:
  redis.conf: |
    # Memory Management
    maxmemory 512mb
    maxmemory-policy allkeys-lru
    
    # Persistence
    save 900 1
    save 300 10
    save 60 10000
    
    # Performance
    tcp-keepalive 300
    timeout 0
    tcp-backlog 511
    
    # Security
    requirepass ${REDIS_PASSWORD}
```

### **Configuração de Load Balancer**

#### **NGINX Ingress Controller**
```yaml
# nginx-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: ingress-nginx
data:
  proxy-body-size: "10m"
  proxy-connect-timeout: "30s"
  proxy-send-timeout: "300s"
  proxy-read-timeout: "300s"
  proxy-buffer-size: "4k"
  proxy-buffers-number: "8"
  client-max-body-size: "10m"
  use-gzip: "true"
  gzip-types: "application/json application/javascript text/css text/javascript"
```

---

## **📊 MONITORAMENTO E ALERTAS**

### **Alertas Críticos**
```yaml
# critical-alerts.yaml
groups:
  - name: critical
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"
      
      - alert: DatabaseConnectionFailing
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failing"
          description: "PostgreSQL is not responding"
```

### **Dashboards de Monitoramento**
- **Application Metrics**: Request rate, response time, error rate
- **Infrastructure Metrics**: CPU, memory, disk, network
- **Business Metrics**: User registrations, keyword analyses, API usage
- **Security Metrics**: Failed logins, suspicious activities

---

## **🔄 PROCEDIMENTOS DE MANUTENÇÃO**

### **Backup Automático**
```bash
#!/bin/bash
# backup-script.sh

# Database backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > /backups/db_$(date +%Y%m%d_%H%M%S).sql.gz

# File backup
tar -czf /backups/files_$(date +%Y%m%d_%H%M%S).tar.gz /app/uploads/

# Upload to S3
aws s3 cp /backups/ s3://omni-backups/ --recursive --exclude "*" --include "*.gz" --include "*.tar.gz"

# Clean old backups (keep 30 days)
find /backups -name "*.gz" -mtime +30 -delete
```

### **Rollback Procedure**
```bash
# Rollback to previous version
helm rollback omni-production 1

# Verify rollback
kubectl get pods -n omni-production
kubectl logs -f deployment/omni-api-gateway -n omni-production

# Check application health
curl -f https://omnikeywords.com/health
```

### **Scaling Procedures**
```bash
# Scale up during high traffic
kubectl scale deployment omni-api-gateway --replicas=10 -n omni-production

# Scale down during low traffic
kubectl scale deployment omni-api-gateway --replicas=3 -n omni-production

# Check resource usage
kubectl top pods -n omni-production
```

---

## **🔒 SEGURANÇA**

### **SSL/TLS Configuration**
```yaml
# cert-manager configuration
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@omnikeywords.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### **Network Policies**
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: omni-production
spec:
  podSelector:
    matchLabels:
      app: omni-api
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
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
```

---

## **📋 CHECKLIST DE DEPLOYMENT**

### **✅ Pré-Deployment**
- [ ] Código testado e aprovado
- [ ] Imagens Docker construídas e testadas
- [ ] Configurações de ambiente validadas
- [ ] Backup do ambiente atual
- [ ] Equipe notificada sobre o deployment

### **✅ Durante o Deployment**
- [ ] Deploy em staging primeiro
- [ ] Testes de smoke em staging
- [ ] Deploy em produção
- [ ] Verificação de health checks
- [ ] Monitoramento de métricas

### **✅ Pós-Deployment**
- [ ] Verificação de funcionalidades críticas
- [ ] Monitoramento de logs e alertas
- [ ] Validação de performance
- [ ] Documentação atualizada
- [ ] Equipe notificada sobre conclusão

---

## **🚨 TROUBLESHOOTING**

### **Problemas Comuns**

#### **Pods não iniciam**
```bash
# Verificar logs
kubectl logs -f pod/pod-name -n namespace

# Verificar eventos
kubectl get events -n namespace --sort-by='.lastTimestamp'

# Verificar recursos
kubectl describe pod pod-name -n namespace
```

#### **Problemas de conectividade**
```bash
# Testar conectividade entre pods
kubectl exec -it pod-name -n namespace -- curl service-name:port

# Verificar DNS
kubectl exec -it pod-name -n namespace -- nslookup service-name

# Verificar network policies
kubectl get networkpolicies -n namespace
```

#### **Problemas de performance**
```bash
# Verificar uso de recursos
kubectl top pods -n namespace

# Verificar métricas do Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Analisar logs de performance
kubectl logs -f deployment/app-name -n namespace | grep -i performance
```

---

**🎯 STATUS**: ✅ **GUIA DE DEPLOYMENT CONCLUÍDO**  
**📅 Próxima Ação**: Implementação dos scripts de automação  
**👨‍💻 Responsável**: AI Assistant  
**📊 Progresso**: 100% da documentação 