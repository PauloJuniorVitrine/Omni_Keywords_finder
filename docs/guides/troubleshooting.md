# Guia de Troubleshooting

## Problemas Comuns

### 1. API não responde

#### Sintomas
- Timeout nas requisições
- Erro 503 Service Unavailable
- Alta latência

#### Verificação
```bash
# Verifique se a API está rodando
curl http://localhost:8000/health

# Verifique os logs
tail -f logs/api.log

# Verifique métricas
curl http://localhost:8000/metrics
```

#### Soluções
1. Reinicie a API:
```bash
docker-compose restart api
```

2. Verifique recursos:
```bash
# CPU
top

# Memória
free -m

# Disco
df -h
```

3. Verifique conexões:
```bash
# Conexões ativas
netstat -an | grep 8000

# Conexões MongoDB
mongo --eval "db.serverStatus().connections"
```

### 2. Erro de Conexão MongoDB

#### Sintomas
- Erro "Connection refused"
- Timeout ao acessar banco
- Erro 500 Internal Server Error

#### Verificação
```bash
# Verifique se MongoDB está rodando
docker-compose ps mongodb

# Teste conexão
mongo mongodb://localhost:27017/keywords_db
```

#### Soluções
1. Reinicie MongoDB:
```bash
docker-compose restart mongodb
```

2. Verifique logs:
```bash
tail -f logs/mongodb.log
```

3. Verifique configuração:
```bash
# Verifique URI
echo $MONGODB_URI

# Verifique permissões
ls -l /data/db
```

### 3. Erro de Cache Redis

#### Sintomas
- Erro "Connection refused"
- Cache miss frequente
- Alta latência

#### Verificação
```bash
# Verifique se Redis está rodando
docker-compose ps redis

# Teste conexão
redis-cli ping
```

#### Soluções
1. Reinicie Redis:
```bash
docker-compose restart redis
```

2. Limpe cache:
```bash
redis-cli FLUSHALL
```

3. Verifique memória:
```bash
redis-cli info memory
```

### 4. Erro de ML

#### Sintomas
- Erro ao extrair keywords
- Baixa precisão
- Timeout no processamento

#### Verificação
```bash
# Verifique modelo
python scripts/check_model.py

# Teste extração
curl -X POST http://localhost:8000/api/v1/keywords/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "language": "pt"}'
```

#### Soluções
1. Retreine modelo:
```bash
python scripts/retrain_model.py
```

2. Verifique recursos:
```bash
# GPU
nvidia-smi

# CPU
top
```

3. Ajuste batch size:
```bash
# Edite .env
BATCH_SIZE=16
```

### 5. Erro de Autenticação

#### Sintomas
- Erro 401 Unauthorized
- Token inválido
- Sessão expirada

#### Verificação
```bash
# Verifique token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me

# Verifique logs
tail -f logs/auth.log
```

#### Soluções
1. Gere novo token:
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

2. Verifique JWT:
```bash
# Verifique secret
echo $JWT_SECRET

# Verifique algoritmo
echo $JWT_ALGORITHM
```

### 6. Erro de Rate Limit

#### Sintomas
- Erro 429 Too Many Requests
- Bloqueio temporário
- Headers de rate limit

#### Verificação
```bash
# Verifique limites
curl -I http://localhost:8000/api/v1/keywords

# Verifique Redis
redis-cli GET rate_limit:ip:127.0.0.1
```

#### Soluções
1. Ajuste limites:
```bash
# Edite .env
RATE_LIMIT_PER_MINUTE=200
RATE_LIMIT_PER_HOUR=2000
```

2. Limpe contadores:
```bash
redis-cli DEL rate_limit:ip:127.0.0.1
```

### 7. Erro de Logs

#### Sintomas
- Logs não aparecem
- Erro ao escrever logs
- Disco cheio

#### Verificação
```bash
# Verifique permissões
ls -l logs/

# Verifique espaço
df -h

# Verifique rotação
ls -l logs/api.log*
```

#### Soluções
1. Limpe logs antigos:
```bash
./scripts/cleanup-logs.sh
```

2. Ajuste rotação:
```bash
# Edite logrotate.conf
/var/log/api.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

### 8. Erro de Métricas

#### Sintomas
- Métricas não aparecem
- Erro no Prometheus
- Grafana sem dados

#### Verificação
```bash
# Verifique Prometheus
curl http://localhost:9090/-/healthy

# Verifique Grafana
curl http://localhost:3000/api/health
```

#### Soluções
1. Reinicie serviços:
```bash
docker-compose restart prometheus grafana
```

2. Verifique configuração:
```bash
# Verifique targets
curl http://localhost:9090/api/v1/targets

# Verifique scrape
curl http://localhost:9090/api/v1/scrape
```

## Scripts Úteis

### 1. Diagnóstico Completo
```bash
./scripts/diagnose.sh
```

### 2. Verificação de Saúde
```bash
./scripts/health-check.sh
```

### 3. Limpeza de Sistema
```bash
./scripts/cleanup.sh
```

## Contatos

### 1. Suporte
- Email: support@example.com
- Slack: #omni-keywords-support
- Jira: OMNI-KW

### 2. Emergência
- On-call: +55 11 99999-9999
- PagerDuty: omni-keywords
- Status: status.example.com 