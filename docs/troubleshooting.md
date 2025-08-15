# Guia de Troubleshooting

Este documento detalha os procedimentos para diagnóstico e resolução de problemas comuns no Omni Keywords Finder.

## Problemas de Performance

### Alta Latência
1. **Sintomas**
   - Respostas lentas da API (>200ms)
   - Timeouts em requisições
   - Aumento de erros 504

2. **Diagnóstico**
   ```bash
   # Verificar métricas de latência
   curl http://localhost:9090/metrics | grep api_latency_seconds
   
   # Verificar uso de recursos
   kubectl top pods -n omni-keywords-finder
   ```

3. **Soluções**
   - Aumentar recursos do pod
   - Verificar queries lentas no MongoDB
   - Otimizar cache Redis
   - Ajustar auto-scaling

### Erros de Memória
1. **Sintomas**
   - OOMKilled nos pods
   - Aumento de erros 500
   - Degradação de performance

2. **Diagnóstico**
   ```bash
   # Verificar logs de OOM
   kubectl logs -n omni-keywords-finder -l app=api | grep OOM
   
   # Verificar uso de memória
   kubectl top pods -n omni-keywords-finder
   ```

3. **Soluções**
   - Aumentar limites de memória
   - Otimizar uso de memória
   - Implementar garbage collection
   - Verificar memory leaks

## Problemas de Banco de Dados

### MongoDB
1. **Sintomas**
   - Erros de conexão
   - Queries lentas
   - Replicação atrasada

2. **Diagnóstico**
   ```bash
   # Verificar status do cluster
   kubectl exec -n omni-keywords-finder mongodb-0 -- mongo --eval "rs.status()"
   
   # Verificar logs
   kubectl logs -n omni-keywords-finder -l app=mongodb
   ```

3. **Soluções**
   - Verificar conectividade
   - Otimizar índices
   - Ajustar configurações
   - Resincronizar réplicas

### Redis
1. **Sintomas**
   - Cache misses
   - Erros de conexão
   - Alta latência

2. **Diagnóstico**
   ```bash
   # Verificar status
   kubectl exec -n omni-keywords-finder redis-0 -- redis-cli info
   
   # Verificar memória
   kubectl exec -n omni-keywords-finder redis-0 -- redis-cli info memory
   ```

3. **Soluções**
   - Limpar cache
   - Ajustar TTL
   - Aumentar memória
   - Verificar eviction policy

## Problemas de ML

### Modelo
1. **Sintomas**
   - Previsões incorretas
   - Alta latência
   - Erros de inferência

2. **Diagnóstico**
   ```bash
   # Verificar logs do modelo
   kubectl logs -n omni-keywords-finder -l app=ml
   
   # Verificar métricas
   curl http://localhost:9090/metrics | grep ml_
   ```

3. **Soluções**
   - Retreinar modelo
   - Ajustar parâmetros
   - Verificar dados de entrada
   - Otimizar inferência

### Embeddings
1. **Sintomas**
   - Erros de geração
   - Variação de qualidade
   - Alta latência

2. **Diagnóstico**
   ```bash
   # Verificar cache
   kubectl exec -n omni-keywords-finder redis-0 -- redis-cli keys "embedding:*"
   
   # Verificar métricas
   curl http://localhost:9090/metrics | grep embedding_
   ```

3. **Soluções**
   - Limpar cache
   - Verificar modelo
   - Ajustar batch size
   - Otimizar pipeline

## Problemas de Rede

### API
1. **Sintomas**
   - Erros 502/504
   - Timeouts
   - Conexões recusadas

2. **Diagnóstico**
   ```bash
   # Verificar ingress
   kubectl get ingress -n omni-keywords-finder
   
   # Verificar serviços
   kubectl get svc -n omni-keywords-finder
   ```

3. **Soluções**
   - Verificar configuração
   - Ajustar timeouts
   - Verificar load balancer
   - Aumentar recursos

### Rate Limiting
1. **Sintomas**
   - Erros 429
   - Bloqueios frequentes
   - Degradação de serviço

2. **Diagnóstico**
   ```bash
   # Verificar limites
   kubectl exec -n omni-keywords-finder redis-0 -- redis-cli keys "rate:*"
   
   # Verificar métricas
   curl http://localhost:9090/metrics | grep rate_limit
   ```

3. **Soluções**
   - Ajustar limites
   - Verificar configuração
   - Implementar backoff
   - Otimizar cache

## Procedimentos de Recuperação

### Backup
1. **MongoDB**
   ```bash
   # Backup
   kubectl exec -n omni-keywords-finder mongodb-0 -- mongodump --out /backup
   
   # Restore
   kubectl exec -n omni-keywords-finder mongodb-0 -- mongorestore /backup
   ```

2. **Redis**
   ```bash
   # Backup
   kubectl exec -n omni-keywords-finder redis-0 -- redis-cli SAVE
   
   # Restore
   kubectl exec -n omni-keywords-finder redis-0 -- redis-cli FLUSHALL
   kubectl cp backup.rdb omni-keywords-finder/redis-0:/data/dump.rdb
   ```

### Rollback
1. **Deploy**
   ```bash
   # Rollback
   kubectl rollout undo deployment/api -n omni-keywords-finder
   kubectl rollout undo deployment/ml -n omni-keywords-finder
   ```

2. **Configuração**
   ```bash
   # Rollback
   kubectl apply -f k8s/previous-config/
   ```

## Monitoramento

### Alertas
1. **Configuração**
   ```yaml
   # alerts/rules.yml
   groups:
   - name: omni-keywords-finder
     rules:
     - alert: HighLatency
       expr: api_latency_seconds > 0.2
       for: 5m
       labels:
         severity: warning
     - alert: HighErrorRate
       expr: rate(api_errors_total[5m]) > 0.1
       for: 5m
       labels:
         severity: critical
   ```

2. **Notificações**
   - Email
   - Slack
   - PagerDuty

### Logs
1. **Estrutura**
   ```json
   {
     "timestamp": "2024-03-20T10:00:00Z",
     "level": "ERROR",
     "service": "api",
     "trace_id": "abc123",
     "error": "Connection refused",
     "metadata": {
       "endpoint": "/keywords/process",
       "client": "1.2.3.4"
     }
   }
   ```

2. **Análise**
   ```bash
   # Logs por serviço
   kubectl logs -n omni-keywords-finder -l app=api
   
   # Logs por erro
   kubectl logs -n omni-keywords-finder -l app=api | grep ERROR
   ```

## Contatos

- **DevOps**: [Email]
- **Suporte**: [Email]
- **On-Call**: [Phone]

## Links Úteis

- [Documentação](README.md)
- [Métricas](metrics_and_monitoring.md)
- [Logs](monitoring_architecture.md)
- [Segurança](security_architecture.md) 