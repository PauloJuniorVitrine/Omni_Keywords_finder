# 🔧 **RUNBOOKS DE TROUBLESHOOTING - OMNİ KEYWORDS FINDER**

## **📋 CONTROLE DE EXECUÇÃO**

**Tracing ID**: RUNBOOKS_TROUBLESHOOTING_20250127_001  
**Data de Criação**: 2025-01-27  
**Versão**: 2.0.0  
**Status**: ✅ CONCLUÍDO  
**Responsável**: AI Assistant  

---

## **🎯 VISÃO GERAL**

Esta documentação contém runbooks detalhados para resolução de problemas comuns no sistema Omni Keywords Finder. Cada runbook segue um formato padronizado com diagnóstico, solução e verificação.

---

## **📋 ESTRUTURA DOS RUNBOOKS**

### **Formato Padronizado**
Cada runbook segue a seguinte estrutura:

1. **🔍 Diagnóstico**: Como identificar o problema
2. **🛠️ Solução**: Passos para resolver o problema
3. **✅ Verificação**: Como confirmar que foi resolvido
4. **📚 Referências**: Links e documentação adicional

---

## **🚨 PROBLEMAS CRÍTICOS**

### **1. Sistema Indisponível (503 Service Unavailable)**

#### **🔍 Diagnóstico**
```bash
# Verificar status dos serviços
curl -f http://localhost:8000/health
kubectl get pods -n omni-production
kubectl logs -f deployment/omni-api-gateway -n omni-production

# Verificar recursos do sistema
kubectl top pods -n omni-production
kubectl describe nodes
```

#### **🛠️ Solução**
```bash
# 1. Verificar se há pods em estado de erro
kubectl get pods -n omni-production | grep -E "(Error|CrashLoopBackOff|Pending)"

# 2. Reiniciar deployment se necessário
kubectl rollout restart deployment/omni-api-gateway -n omni-production

# 3. Verificar logs para identificar causa raiz
kubectl logs -f deployment/omni-api-gateway -n omni-production --tail=100

# 4. Escalar se necessário
kubectl scale deployment omni-api-gateway --replicas=3 -n omni-production
```

#### **✅ Verificação**
```bash
# Verificar se o serviço está respondendo
curl -f http://localhost:8000/health

# Verificar se todos os pods estão rodando
kubectl get pods -n omni-production | grep Running

# Verificar métricas de performance
kubectl top pods -n omni-production
```

#### **📚 Referências**
- [Documentação de Deployment](docs/deployment/README.md)
- [Monitoramento](docs/monitoring/README.md)

---

### **2. Erro de Banco de Dados (Database Connection Failed)**

#### **🔍 Diagnóstico**
```bash
# Verificar conectividade com banco
kubectl exec -it deployment/omni-api-gateway -n omni-production -- pg_isready -h postgres-service -p 5432

# Verificar logs de conexão
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "database\|connection"

# Verificar status do PostgreSQL
kubectl get pods -n omni-production | grep postgres
kubectl logs -f deployment/postgres -n omni-production
```

#### **🛠️ Solução**
```bash
# 1. Verificar se o PostgreSQL está rodando
kubectl get pods -n omni-production | grep postgres

# 2. Reiniciar PostgreSQL se necessário
kubectl rollout restart deployment/postgres -n omni-production

# 3. Verificar configurações de conexão
kubectl get configmap -n omni-production | grep database
kubectl describe configmap database-config -n omni-production

# 4. Verificar secrets
kubectl get secrets -n omni-production | grep postgres
kubectl describe secret postgres-secret -n omni-production
```

#### **✅ Verificação**
```bash
# Testar conexão com banco
kubectl exec -it deployment/omni-api-gateway -n omni-production -- python -c "
import psycopg2
conn = psycopg2.connect('postgresql://user:pass@postgres-service:5432/dbname')
print('Conexão OK')
conn.close()
"

# Verificar se a aplicação está funcionando
curl -f http://localhost:8000/health
```

#### **📚 Referências**
- [Configuração de Banco](docs/database/README.md)
- [Troubleshooting PostgreSQL](https://www.postgresql.org/docs/current/runtime-config.html)

---

### **3. Erro de Autenticação (401 Unauthorized)**

#### **🔍 Diagnóstico**
```bash
# Verificar logs de autenticação
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "auth\|unauthorized"

# Verificar configuração JWT
kubectl get secrets -n omni-production | grep jwt
kubectl describe secret jwt-secret -n omni-production

# Testar endpoint de login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

#### **🛠️ Solução**
```bash
# 1. Verificar se o secret JWT existe
kubectl get secrets -n omni-production | grep jwt

# 2. Recriar secret JWT se necessário
kubectl create secret generic jwt-secret \
  --from-literal=jwt-secret="new-secret-key" \
  -n omni-production

# 3. Reiniciar deployment para aplicar nova configuração
kubectl rollout restart deployment/omni-api-gateway -n omni-production

# 4. Verificar configuração de autenticação
kubectl get configmap -n omni-production | grep auth
```

#### **✅ Verificação**
```bash
# Testar login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Verificar se retorna token válido
# Testar endpoint protegido com token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/protected
```

#### **📚 Referências**
- [Configuração de Autenticação](docs/authentication/README.md)
- [JWT Documentation](https://jwt.io/)

---

## **⚠️ PROBLEMAS DE PERFORMANCE**

### **4. Tempo de Resposta Lento (High Response Time)**

#### **🔍 Diagnóstico**
```bash
# Verificar métricas de performance
kubectl top pods -n omni-production
kubectl exec -it deployment/omni-api-gateway -n omni-production -- free -h

# Verificar logs de performance
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "slow\|timeout"

# Testar tempo de resposta
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

#### **🛠️ Solução**
```bash
# 1. Verificar uso de recursos
kubectl top pods -n omni-production
kubectl describe nodes

# 2. Escalar horizontalmente se necessário
kubectl scale deployment omni-api-gateway --replicas=5 -n omni-production

# 3. Verificar configurações de cache
kubectl get configmap -n omni-production | grep cache
kubectl describe configmap cache-config -n omni-production

# 4. Verificar queries lentas no banco
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords
# Dentro do psql:
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

#### **✅ Verificação**
```bash
# Monitorar tempo de resposta
for i in {1..10}; do
  curl -w "Time: %{time_total}s\n" -o /dev/null -s http://localhost:8000/health
done

# Verificar métricas no Prometheus/Grafana
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# Acessar http://localhost:9090
```

#### **📚 Referências**
- [Otimização de Performance](docs/performance/README.md)
- [Monitoramento](docs/monitoring/README.md)

---

### **5. Alto Uso de Memória (Memory Leak)**

#### **🔍 Diagnóstico**
```bash
# Verificar uso de memória
kubectl top pods -n omni-production
kubectl exec -it deployment/omni-api-gateway -n omni-production -- cat /proc/meminfo

# Verificar logs de memória
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "memory\|oom"

# Verificar se há vazamentos
kubectl exec -it deployment/omni-api-gateway -n omni-production -- python -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
"
```

#### **🛠️ Solução**
```bash
# 1. Reiniciar pod para liberar memória
kubectl delete pod -l app=omni-api-gateway -n omni-production

# 2. Verificar configurações de memória
kubectl get deployment omni-api-gateway -n omni-production -o yaml | grep -A 5 resources

# 3. Ajustar limites de memória se necessário
kubectl patch deployment omni-api-gateway -n omni-production -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "api-gateway",
          "resources": {
            "limits": {
              "memory": "1Gi"
            },
            "requests": {
              "memory": "512Mi"
            }
          }
        }]
      }
    }
  }
}'

# 4. Verificar código por vazamentos de memória
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "memory\|gc"
```

#### **✅ Verificação**
```bash
# Monitorar uso de memória
watch -n 5 'kubectl top pods -n omni-production'

# Verificar se não há crescimento contínuo
kubectl exec -it deployment/omni-api-gateway -n omni-production -- python -c "
import psutil
import time
for i in range(5):
    print(f'Memory: {psutil.virtual_memory().percent}%')
    time.sleep(10)
"
```

#### **📚 Referências**
- [Debugging Memory Issues](docs/debugging/memory.md)
- [Python Memory Management](https://docs.python.org/3/library/gc.html)

---

## **🔒 PROBLEMAS DE SEGURANÇA**

### **6. Tentativas de Login Suspeitas**

#### **🔍 Diagnóstico**
```bash
# Verificar logs de autenticação
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "login\|auth\|failed"

# Verificar tentativas de login
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
SELECT email, COUNT(*) as attempts, MAX(created_at) as last_attempt
FROM login_attempts 
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY email 
HAVING COUNT(*) > 5
ORDER BY attempts DESC;
"

# Verificar IPs suspeitos
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}"
```

#### **🛠️ Solução**
```bash
# 1. Bloquear IPs suspeitos
kubectl exec -it deployment/omni-api-gateway -n omni-production -- iptables -A INPUT -s <IP_SUSPEITO> -j DROP

# 2. Implementar rate limiting
kubectl patch deployment omni-api-gateway -n omni-production -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "api-gateway",
          "env": [{
            "name": "RATE_LIMIT_LOGIN",
            "value": "5"
          }]
        }]
      }
    }
  }
}'

# 3. Notificar administrador
kubectl exec -it deployment/omni-api-gateway -n omni-production -- python -c "
import smtplib
from email.mime.text import MIMEText
msg = MIMEText('Tentativas de login suspeitas detectadas')
msg['Subject'] = 'Security Alert'
msg['From'] = 'security@omnikeywords.com'
msg['To'] = 'admin@omnikeywords.com'
s = smtplib.SMTP('smtp.company.com')
s.send_message(msg)
s.quit()
"
```

#### **✅ Verificação**
```bash
# Verificar se rate limiting está funcionando
for i in {1..10}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
done

# Verificar logs de segurança
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "security\|blocked"
```

#### **📚 Referências**
- [Security Best Practices](docs/security/README.md)
- [Rate Limiting](docs/security/rate-limiting.md)

---

## **📊 PROBLEMAS DE DADOS**

### **7. Inconsistência de Dados**

#### **🔍 Diagnóstico**
```bash
# Verificar integridade do banco
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
SELECT 
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
"

# Verificar constraints
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
SELECT 
  tc.table_name, 
  tc.constraint_name, 
  tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public';
"

# Verificar foreign keys
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
SELECT 
  tc.table_name, 
  kcu.column_name, 
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY';
"
```

#### **🛠️ Solução**
```bash
# 1. Executar verificação de integridade
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
REINDEX DATABASE omni_keywords;
VACUUM ANALYZE;
"

# 2. Verificar e corrigir foreign keys órfãs
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
-- Exemplo para tabela keywords
DELETE FROM keywords 
WHERE user_id NOT IN (SELECT id FROM users);

-- Exemplo para tabela analyses
DELETE FROM analyses 
WHERE keyword_id NOT IN (SELECT id FROM keywords);
"

# 3. Executar migrations pendentes
kubectl exec -it deployment/omni-api-gateway -n omni-production -- python manage.py migrate

# 4. Verificar logs de aplicação
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "error\|exception\|integrity"
```

#### **✅ Verificação**
```bash
# Verificar se não há mais erros de integridade
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
SELECT 
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
"

# Testar funcionalidades críticas
curl -f http://localhost:8000/api/keywords/analyze \
  -H "Content-Type: application/json" \
  -d '{"keyword":"test"}'
```

#### **📚 Referências**
- [Database Maintenance](docs/database/maintenance.md)
- [Data Integrity](docs/database/integrity.md)

---

## **🌐 PROBLEMAS DE REDE**

### **8. Problemas de Conectividade**

#### **🔍 Diagnóstico**
```bash
# Verificar conectividade entre pods
kubectl exec -it deployment/omni-api-gateway -n omni-production -- ping postgres-service
kubectl exec -it deployment/omni-api-gateway -n omni-production -- nslookup postgres-service

# Verificar network policies
kubectl get networkpolicies -n omni-production
kubectl describe networkpolicy api-network-policy -n omni-production

# Verificar serviços
kubectl get services -n omni-production
kubectl describe service postgres-service -n omni-production

# Verificar endpoints
kubectl get endpoints -n omni-production
kubectl describe endpoints postgres-service -n omni-production
```

#### **🛠️ Solução**
```bash
# 1. Verificar se os serviços estão funcionando
kubectl get services -n omni-production
kubectl get endpoints -n omni-production

# 2. Recriar endpoints se necessário
kubectl delete endpoints postgres-service -n omni-production
kubectl apply -f k8s/postgres-service.yaml

# 3. Verificar DNS
kubectl exec -it deployment/omni-api-gateway -n omni-production -- cat /etc/resolv.conf
kubectl exec -it deployment/omni-api-gateway -n omni-production -- nslookup postgres-service

# 4. Verificar network policies
kubectl get networkpolicies -n omni-production -o yaml
kubectl delete networkpolicy api-network-policy -n omni-production
kubectl apply -f k8s/network-policies.yaml
```

#### **✅ Verificação**
```bash
# Testar conectividade
kubectl exec -it deployment/omni-api-gateway -n omni-production -- curl -f http://postgres-service:5432

# Verificar se a aplicação está funcionando
curl -f http://localhost:8000/health

# Verificar logs de rede
kubectl logs -f deployment/omni-api-gateway -n omni-production | grep -i "connection\|network"
```

#### **📚 Referências**
- [Network Policies](docs/networking/README.md)
- [Service Discovery](docs/networking/service-discovery.md)

---

## **📋 PROCEDIMENTOS DE EMERGÊNCIA**

### **9. Rollback de Deploy**

#### **🔍 Diagnóstico**
```bash
# Verificar histórico de deployments
kubectl rollout history deployment/omni-api-gateway -n omni-production

# Verificar status atual
kubectl rollout status deployment/omni-api-gateway -n omni-production

# Verificar logs de erro
kubectl logs -f deployment/omni-api-gateway -n omni-production --tail=100
```

#### **🛠️ Solução**
```bash
# 1. Fazer rollback para versão anterior
kubectl rollout undo deployment/omni-api-gateway -n omni-production

# 2. Verificar status do rollback
kubectl rollout status deployment/omni-api-gateway -n omni-production

# 3. Se necessário, especificar versão específica
kubectl rollout undo deployment/omni-api-gateway -n omni-production --to-revision=2

# 4. Verificar se todos os pods estão rodando
kubectl get pods -n omni-production | grep omni-api-gateway
```

#### **✅ Verificação**
```bash
# Verificar se o serviço está funcionando
curl -f http://localhost:8000/health

# Verificar logs da nova versão
kubectl logs -f deployment/omni-api-gateway -n omni-production --tail=50

# Verificar métricas
kubectl top pods -n omni-production
```

#### **📚 Referências**
- [Deployment Strategy](docs/deployment/strategy.md)
- [Rollback Procedures](docs/deployment/rollback.md)

---

### **10. Recuperação de Desastre**

#### **🔍 Diagnóstico**
```bash
# Verificar status geral do cluster
kubectl get nodes
kubectl get pods --all-namespaces

# Verificar backups
kubectl exec -it deployment/postgres -n omni-production -- ls -la /backups/

# Verificar configurações de backup
kubectl get configmap -n omni-production | grep backup
```

#### **🛠️ Solução**
```bash
# 1. Restaurar banco de dados
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
DROP DATABASE omni_keywords;
CREATE DATABASE omni_keywords;
"
kubectl exec -it deployment/postgres -n omni-production -- pg_restore -U postgres -d omni_keywords /backups/latest_backup.sql

# 2. Restaurar configurações
kubectl apply -f k8s/configmaps.yaml
kubectl apply -f k8s/secrets.yaml

# 3. Reiniciar todos os deployments
kubectl rollout restart deployment --all -n omni-production

# 4. Verificar conectividade
kubectl get services -n omni-production
kubectl get endpoints -n omni-production
```

#### **✅ Verificação**
```bash
# Verificar se todos os serviços estão funcionando
curl -f http://localhost:8000/health
curl -f http://localhost:8000/api/keywords/analyze

# Verificar integridade dos dados
kubectl exec -it deployment/postgres -n omni-production -- psql -U postgres -d omni_keywords -c "
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM keywords;
"

# Verificar logs de todos os serviços
kubectl logs -f deployment/omni-api-gateway -n omni-production
kubectl logs -f deployment/postgres -n omni-production
```

#### **📚 Referências**
- [Disaster Recovery](docs/disaster-recovery/README.md)
- [Backup Procedures](docs/backup/README.md)

---

## **📞 CONTATOS DE EMERGÊNCIA**

### **Escalação de Problemas**
1. **Nível 1**: Desenvolvedor On-Call
   - Email: oncall@omnikeywords.com
   - Slack: #oncall-alerts
   - PagerDuty: Omni Keywords On-Call

2. **Nível 2**: Tech Lead
   - Email: techlead@omnikeywords.com
   - Slack: #tech-leads
   - PagerDuty: Tech Lead Escalation

3. **Nível 3**: CTO
   - Email: cto@omnikeywords.com
   - Slack: #cto-alerts
   - PagerDuty: CTO Escalation

### **Horários de Suporte**
- **24/7**: Problemas críticos (SLA: 15 minutos)
- **8h-18h**: Problemas não críticos (SLA: 4 horas)
- **Fins de semana**: Apenas problemas críticos

---

## **📚 RECURSOS ADICIONAIS**

### **Documentação Relacionada**
- [Monitoramento](docs/monitoring/README.md)
- [Logs](docs/logging/README.md)
- [Métricas](docs/metrics/README.md)
- [Alertas](docs/alerts/README.md)

### **Ferramentas Úteis**
- **Kubernetes Dashboard**: `kubectl proxy`
- **Prometheus**: `kubectl port-forward svc/prometheus 9090:9090 -n monitoring`
- **Grafana**: `kubectl port-forward svc/grafana 3000:3000 -n monitoring`
- **Jaeger**: `kubectl port-forward svc/jaeger 16686:16686 -n monitoring`

### **Comandos Úteis**
```bash
# Verificar status geral
kubectl get all -n omni-production

# Verificar eventos
kubectl get events -n omni-production --sort-by='.lastTimestamp'

# Verificar logs de múltiplos pods
kubectl logs -f -l app=omni-api-gateway -n omni-production

# Executar comando em pod
kubectl exec -it deployment/omni-api-gateway -n omni-production -- /bin/bash

# Copiar arquivo do pod
kubectl cp omni-production/omni-api-gateway-xxx:/app/logs/app.log ./app.log
```

---

**🎯 STATUS**: ✅ **RUNBOOKS DE TROUBLESHOOTING CONCLUÍDOS**  
**📅 Próxima Ação**: Implementação dos scripts de automação  
**👨‍💻 Responsável**: AI Assistant  
**📊 Progresso**: 100% da documentação 