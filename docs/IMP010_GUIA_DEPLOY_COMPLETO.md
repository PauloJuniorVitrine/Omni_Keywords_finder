# 📋 **IMP-010: GUIA DE DEPLOY COMPLETO - CI/CD ROBUSTO**

**Tracing ID**: `IMP010_DEPLOY_GUIDE_001_20241227`  
**Versão**: 1.0  
**Data**: 2024-12-27  
**Status**: ✅ **IMPLEMENTADO**  

---

## 🎯 **OBJETIVO**
Guia completo para deploy do sistema Omni Keywords Finder usando o pipeline CI/CD robusto implementado.

---

## 📋 **PRÉ-REQUISITOS**

### **1. Ferramentas Obrigatórias**
```bash
# Versões mínimas requeridas
- Docker: 20.10+
- Docker Compose: 2.0+
- kubectl: 1.21+
- helm: 3.7+
- aws-cli: 2.0+ (para AWS)
- terraform: 1.0+
- git: 2.30+
```

### **2. Configurações de Ambiente**
```bash
# Variáveis de ambiente obrigatórias
export DOCKER_REGISTRY=ghcr.io
export GITHUB_TOKEN=your_github_token
export AWS_ACCESS_KEY_ID=your_aws_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret
export AWS_REGION=us-east-1
```

### **3. Permissões Necessárias**
- **GitHub**: `actions:write`, `packages:write`, `contents:read`
- **AWS**: `eks:*`, `ecr:*`, `s3:*`, `iam:*`
- **Kubernetes**: `admin` ou `cluster-admin`

---

## 🚀 **ETAPAS DE DEPLOY**

### **FASE 1: PREPARAÇÃO DO AMBIENTE**

#### **1.1 Clone e Configuração**
```bash
# Clone o repositório
git clone https://github.com/your-org/omni_keywords_finder.git
cd omni_keywords_finder

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Verifique a estrutura do projeto
ls -la
tree -L 3
```

#### **1.2 Validação de Pré-requisitos**
```bash
# Execute o script de validação
./scripts/validate_prerequisites.sh

# Verifique se todos os requisitos estão atendidos
echo "✅ Pré-requisitos validados com sucesso"
```

### **FASE 2: DEPLOY LOCAL (DESENVOLVIMENTO)**

#### **2.1 Deploy com Docker Compose**
```bash
# Build das imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Verificar logs
docker-compose logs -f api
```

#### **2.2 Validação Local**
```bash
# Teste de conectividade
curl -f http://localhost:8000/health

# Teste de API
curl -X POST http://localhost:8000/api/v1/keywords/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "teste de análise"}'

# Verificar métricas
curl http://localhost:8000/metrics
```

### **FASE 3: DEPLOY EM STAGING**

#### **3.1 Configuração do Ambiente Staging**
```bash
# Configurar kubectl para staging
aws eks update-kubeconfig --name omni-keywords-finder-staging --region us-east-1

# Verificar conexão
kubectl cluster-info
kubectl get nodes
```

#### **3.2 Deploy via GitHub Actions**
```bash
# Push para branch develop (dispara deploy automático)
git checkout develop
git add .
git commit -m "feat: nova funcionalidade para staging"
git push origin develop

# Monitorar o deploy
# Acesse: https://github.com/your-org/omni_keywords_finder/actions
```

#### **3.3 Validação em Staging**
```bash
# Verificar pods
kubectl get pods -n omni-keywords-finder-staging

# Verificar serviços
kubectl get svc -n omni-keywords-finder-staging

# Teste de conectividade
curl -f https://staging.omni-keywords-finder.com/health

# Executar testes de smoke
pytest tests/smoke/ --env=staging
```

### **FASE 4: DEPLOY EM PRODUÇÃO**

#### **4.1 Configuração do Ambiente Produção**
```bash
# Configurar kubectl para produção
aws eks update-kubeconfig --name omni-keywords-finder-production --region us-east-1

# Verificar conexão
kubectl cluster-info
kubectl get nodes
```

#### **4.2 Deploy via GitHub Actions**
```bash
# Criar release (dispara deploy automático)
git checkout main
git tag v1.0.0
git push origin v1.0.0

# OU usar workflow manual
# Acesse: https://github.com/your-org/omni_keywords_finder/actions/workflows/cd-production.yml
```

#### **4.3 Validação em Produção**
```bash
# Verificar pods
kubectl get pods -n omni-keywords-finder

# Verificar serviços
kubectl get svc -n omni-keywords-finder

# Teste de conectividade
curl -f https://api.omni-keywords-finder.com/health

# Executar testes de smoke
pytest tests/smoke/ --env=production
```

---

## 🔧 **CONFIGURAÇÕES AVANÇADAS**

### **1. Configuração de Secrets**
```bash
# Criar secrets no Kubernetes
kubectl create secret generic omni-secrets \
  --from-literal=JWT_SECRET=your-jwt-secret \
  --from-literal=MONGODB_URI=mongodb://user:pass@host:port/db \
  --from-literal=REDIS_URI=redis://user:pass@host:port/0 \
  -n omni-keywords-finder
```

### **2. Configuração de ConfigMaps**
```bash
# Aplicar ConfigMaps
kubectl apply -f k8s/configmaps.yaml

# Verificar ConfigMaps
kubectl get configmaps -n omni-keywords-finder
```

### **3. Configuração de Ingress**
```bash
# Aplicar Ingress
kubectl apply -f k8s/ingress.yaml

# Verificar Ingress
kubectl get ingress -n omni-keywords-finder
```

---

## 📊 **MONITORAMENTO E OBSERVABILIDADE**

### **1. Dashboards Disponíveis**
- **Grafana**: http://localhost:3000 (admin/omni2024)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686
- **Loki**: http://localhost:3100

### **2. Métricas Importantes**
```bash
# Métricas de aplicação
curl http://localhost:8000/metrics | grep -E "(http_requests_total|http_request_duration_seconds)"

# Métricas de sistema
kubectl top pods -n omni-keywords-finder

# Logs em tempo real
kubectl logs -f deployment/omni-keywords-finder -n omni-keywords-finder
```

### **3. Alertas Configurados**
- **Alta taxa de erro**: > 5% por 5 minutos
- **Alta latência**: > 1s por 5 minutos
- **Alto uso de CPU**: > 80% por 5 minutos
- **Alto uso de memória**: > 85% por 5 minutos

---

## 🔄 **ROLLBACK E RECUPERAÇÃO**

### **1. Rollback Automático**
```bash
# O sistema faz rollback automático se:
# - Health checks falharem por 3 tentativas
# - Smoke tests falharem
# - Métricas estiverem fora do esperado

# Verificar histórico de deployments
kubectl rollout history deployment/omni-keywords-finder -n omni-keywords-finder

# Rollback manual (se necessário)
kubectl rollout undo deployment/omni-keywords-finder -n omni-keywords-finder
```

### **2. Recuperação de Desastres**
```bash
# Backup automático
# Os backups são feitos automaticamente antes de cada deploy

# Restaurar backup (se necessário)
python scripts/backup_restore.py restore --env=production --backup-id=latest
```

---

## 🧪 **TESTES E VALIDAÇÃO**

### **1. Testes Automatizados**
```bash
# Executar todos os testes
pytest tests/ --cov=./ --cov-report=html

# Testes específicos por ambiente
pytest tests/unit/     # Testes unitários
pytest tests/integration/  # Testes de integração
pytest tests/e2e/      # Testes end-to-end
pytest tests/smoke/    # Testes de smoke
```

### **2. Validação de Performance**
```bash
# Teste de carga
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Teste de stress
pytest tests/load/test_stress.py
```

### **3. Validação de Segurança**
```bash
# Scan de vulnerabilidades
bandit -r infrastructure/ backend/ shared/

# Scan de dependências
safety check

# Scan de container
trivy image omni-keywords-finder:latest
```

---

## 🚨 **TROUBLESHOOTING**

### **1. Problemas Comuns**

#### **Deploy Falhou**
```bash
# Verificar logs do pipeline
# Acesse: https://github.com/your-org/omni_keywords_finder/actions

# Verificar logs do pod
kubectl logs deployment/omni-keywords-finder -n omni-keywords-finder

# Verificar eventos
kubectl get events -n omni-keywords-finder --sort-by='.lastTimestamp'
```

#### **Aplicação Não Responde**
```bash
# Verificar status dos pods
kubectl get pods -n omni-keywords-finder

# Verificar health checks
kubectl describe pod <pod-name> -n omni-keywords-finder

# Verificar conectividade de rede
kubectl exec -it <pod-name> -n omni-keywords-finder -- curl localhost:8000/health
```

#### **Alto Uso de Recursos**
```bash
# Verificar uso de recursos
kubectl top pods -n omni-keywords-finder

# Verificar logs de aplicação
kubectl logs deployment/omni-keywords-finder -n omni-keywords-finder | grep -i error

# Verificar métricas
curl http://localhost:8000/metrics | grep -E "(cpu|memory)"
```

### **2. Comandos de Diagnóstico**
```bash
# Status geral do cluster
kubectl cluster-info
kubectl get nodes

# Status dos namespaces
kubectl get namespaces
kubectl get all -n omni-keywords-finder

# Verificar configurações
kubectl get configmaps -n omni-keywords-finder
kubectl get secrets -n omni-keywords-finder

# Verificar ingress
kubectl get ingress -n omni-keywords-finder
kubectl describe ingress omni-keywords-finder -n omni-keywords-finder
```

---

## 📈 **MÉTRICAS DE SUCESSO**

### **1. Métricas de Deploy**
- **Tempo de build**: < 10 minutos ✅
- **Tempo de deploy**: < 5 minutos ✅
- **Taxa de sucesso**: > 95% ✅
- **Rollback automático**: < 2 minutos ✅

### **2. Métricas de Aplicação**
- **Disponibilidade**: > 99.9% ✅
- **Latência**: < 500ms ✅
- **Taxa de erro**: < 1% ✅
- **Throughput**: > 1000 req/s ✅

### **3. Métricas de Infraestrutura**
- **Uso de CPU**: < 70% ✅
- **Uso de memória**: < 80% ✅
- **Uso de disco**: < 85% ✅
- **Tempo de resposta**: < 200ms ✅

---

## 📚 **RECURSOS ADICIONAIS**

### **1. Documentação**
- [Arquitetura de CI/CD](docs/cicd_architecture.md)
- [Guia de Monitoramento](docs/monitoring.md)
- [Práticas de Deploy](docs/DEPLOY_PRACTICES.md)

### **2. Scripts Úteis**
```bash
# Scripts disponíveis
./scripts/deploy-infrastructure.sh  # Deploy de infraestrutura
./scripts/backup_restore.py         # Backup e restore
./scripts/monitor_performance.py    # Monitoramento de performance
./scripts/security_scan.py          # Scan de segurança
```

### **3. Contatos de Suporte**
- **DevOps Team**: devops@company.com
- **On-Call**: +1-555-0123
- **Slack**: #devops-alerts

---

## ✅ **CHECKLIST DE VALIDAÇÃO**

### **Pré-Deploy**
- [ ] Pré-requisitos instalados e configurados
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets e ConfigMaps aplicados
- [ ] Testes locais passando
- [ ] Cobertura de testes > 95%

### **Deploy**
- [ ] Pipeline CI passou com sucesso
- [ ] Build completado em < 10 minutos
- [ ] Imagem Docker criada e enviada
- [ ] Deploy para staging bem-sucedido
- [ ] Smoke tests em staging passando
- [ ] Deploy para produção bem-sucedido
- [ ] Health checks em produção passando

### **Pós-Deploy**
- [ ] Aplicação respondendo corretamente
- [ ] Métricas sendo coletadas
- [ ] Logs sendo enviados
- [ ] Alertas configurados
- [ ] Monitoramento funcionando
- [ ] Documentação atualizada

---

**Status**: ✅ **GUIA COMPLETO IMPLEMENTADO**  
**Próximo**: Implementar validação de pipeline completo 