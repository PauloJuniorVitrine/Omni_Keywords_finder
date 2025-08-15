# Guia de Deploy - Omni Keywords Finder

## Pré-requisitos

- Docker e Docker Compose
- Kubernetes (opcional)
- Terraform (opcional)
- AWS CLI (para deploy na AWS)

## Deploy Local

### 1. Docker Compose

```bash
# Clone o repositório
git clone https://github.com/your-org/omni-keywords-finder.git
cd omni-keywords-finder

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Inicie os serviços
docker-compose up -data

# Verifique os logs
docker-compose logs -f
```

### 2. Verificação

```bash
# Health check
curl http://localhost:8000/health

# API
curl http://localhost:8000/api/v1/keywords

# Frontend
open http://localhost:3000
```

## Deploy em Produção

### 1. AWS (Terraform)

```bash
# Configure AWS CLI
aws configure

# Deploy infraestrutura
cd terraform
terraform init
terraform plan
terraform apply

# Configure DNS
# Atualize registros DNS para apontar para o ALB
```

### 2. Kubernetes

```bash
# Configure kubectl
kubectl config use-context your-cluster

# Deploy aplicação
kubectl apply -f k8s/

# Verifique o status
kubectl get pods
kubectl get services
```

### 3. Monitoramento

```bash
# Acesse Grafana
open http://your-domain:3000

# Acesse Prometheus
open http://your-domain:9090

# Acesse Jaeger
open http://your-domain:16686
```

## Configurações de Produção

### 1. Variáveis de Ambiente

```bash
# Produção
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@host:5432/omni_keywords

# Redis
REDIS_URL=redis://host:6379

# APIs
OPENAI_API_KEY=your_production_key
GOOGLE_SEARCH_CONSOLE_CREDENTIALS=/path/to/credentials.json

# Segurança
SECRET_KEY=your_very_secure_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Monitoramento
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
JAEGER_PORT=16686
```

### 2. SSL/TLS

```bash
# Configure certificados SSL
# Use Let'string_data Encrypt ou certificados corporativos

# Nginx config
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Backup

```bash
# Backup do banco de dados
pg_dump omni_keywords > backup_$(date +%Y%m%data).sql

# Backup dos logs
tar -czf logs_backup_$(date +%Y%m%data).tar.gz logs/

# Backup das configurações
tar -czf config_backup_$(date +%Y%m%data).tar.gz config/
```

## Monitoramento e Alertas

### 1. Métricas Críticas

- **CPU**: > 80% por 5 minutos
- **Memória**: > 85% por 5 minutos
- **Disco**: > 90%
- **Latência**: > 1s (P95)
- **Error Rate**: > 5%

### 2. Alertas

```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'
```

### 3. Dashboards

- **Sistema**: CPU, memória, disco, rede
- **Aplicação**: Latência, throughput, error rate
- **Negócio**: Keywords processadas, usuários ativos
- **Segurança**: Tentativas de login, acessos suspeitos

## Troubleshooting

### 1. Problemas Comuns

**Aplicação não inicia:**
```bash
# Verifique logs
docker-compose logs app

# Verifique variáveis de ambiente
docker-compose config

# Verifique conectividade
docker-compose exec app ping database
```

**Performance lenta:**
```bash
# Verifique métricas
curl http://localhost:9090/metrics

# Verifique cache
docker-compose exec redis redis-cli info memory

# Verifique banco de dados
docker-compose exec database psql -U user -data omni_keywords -c "SELECT * FROM pg_stat_activity;"
```

**Erros 500:**
```bash
# Verifique logs da aplicação
docker-compose logs -f app

# Verifique logs do nginx
docker-compose logs -f nginx

# Verifique health checks
curl http://localhost:8000/health
```

### 2. Rollback

```bash
# Rollback de versão
docker-compose down
git checkout previous-version
docker-compose up -data

# Rollback de banco de dados
psql omni_keywords < backup_previous_version.sql
```

## Segurança

### 1. Checklist

- [ ] SSL/TLS configurado
- [ ] Firewall configurado
- [ ] Secrets gerenciados
- [ ] Logs de auditoria ativos
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Alertas configurados

### 2. Hardening

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade

# Configurar firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Configurar fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## Performance

### 1. Otimizações

- **Cache**: Redis configurado
- **CDN**: CloudFront/Akamai
- **Load Balancer**: ALB/NLB
- **Auto Scaling**: Baseado em métricas
- **Database**: Índices otimizados

### 2. Benchmarks

```bash
# Teste de carga
ab -n 1000 -c 10 http://your-domain/api/v1/keywords

# Teste de stress
stress-ng --cpu 4 --io 2 --vm 2 --vm-bytes 1G --timeout 60s
```

## Manutenção

### 1. Atualizações

```bash
# Backup antes da atualização
./scripts/backup.sh

# Atualizar código
git pull origin main

# Rebuild e restart
docker-compose down
docker-compose build --no-cache
docker-compose up -data

# Verificar saúde
./scripts/health_check.sh
```

### 2. Limpeza

```bash
# Limpar logs antigos
find logs/ -name "*.log" -mtime +30 -delete

# Limpar cache
docker-compose exec redis redis-cli FLUSHALL

# Limpar imagens Docker
docker system prune -a
```
