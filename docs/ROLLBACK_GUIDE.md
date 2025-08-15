# 🔄 **GUIA DE ROLLBACK - OMNİ KEYWORDS FINDER**

## **📋 METADADOS DO GUIA**

**Tracing ID**: ROLLBACK_GUIDE_20250127_001  
**Data de Criação**: 2025-01-27  
**Versão**: 1.0.0  
**Status**: ✅ PRONTO PARA USO  
**Responsável**: DevOps Team  
**Escopo**: Rollback Automático e Manual

---

## **🎯 EXECUTIVE SUMMARY**

### **Objetivo**
Fornecer procedimentos claros e eficientes para rollback do sistema Omni Keywords Finder em caso de problemas em produção.

### **Estratégia**
- **Rollback Automático**: Baseado em métricas e health checks
- **Rollback Manual**: Para situações específicas que requerem intervenção humana
- **Rollback Gradual**: Para minimizar impacto em usuários

### **Tempo de Recuperação**
- **Rollback Automático**: <2 minutos
- **Rollback Manual**: <5 minutos
- **Validação Completa**: <10 minutos

---

## **🚨 TRIGGERS DE ROLLBACK**

### **1. TRIGGERS AUTOMÁTICOS**

#### **1.1 Métricas de Performance**
```yaml
# Configuração de alertas (config/alerting.yaml)
triggers:
  - name: "high_error_rate"
    condition: "error_rate > 5%"
    duration: "5 minutes"
    action: "auto_rollback"
    
  - name: "high_response_time"
    condition: "response_time > 1000ms"
    duration: "3 minutes"
    action: "auto_rollback"
    
  - name: "health_check_failure"
    condition: "health_check != 200"
    duration: "2 minutes"
    action: "auto_rollback"
    
  - name: "database_connectivity"
    condition: "db_connection_failed"
    duration: "1 minute"
    action: "auto_rollback"
```

#### **1.2 Health Checks**
- [ ] **Application Health**: `/health` retorna != 200
- [ ] **Database Health**: Conexão com banco falha
- [ ] **Cache Health**: Redis não responde
- [ ] **External Services**: APIs externas indisponíveis

#### **1.3 Métricas de Negócio**
- [ ] **Error Rate**: >5% por 5 minutos
- [ ] **Response Time**: >1000ms por 3 minutos
- [ ] **Throughput**: <50% do baseline
- [ ] **User Complaints**: >10 em 10 minutos

### **2. TRIGGERS MANUAIS**

#### **2.1 Critérios de Negócio**
- [ ] **Funcionalidades críticas quebradas**
- [ ] **Problemas de segurança identificados**
- [ ] **Performance degradada significativa**
- [ ] **Feedback negativo de usuários**

#### **2.2 Critérios Técnicos**
- [ ] **Memory leaks detectados**
- [ ] **CPU usage >90%**
- [ ] **Database locks**
- [ ] **Cache corruption**

---

## **🤖 ROLLBACK AUTOMÁTICO**

### **1. SISTEMA DE DETECÇÃO**

#### **1.1 Monitoramento Contínuo**
```python
# scripts/monitoring/rollback_detector.py
class RollbackDetector:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerting = AlertingSystem()
        self.rollback = RollbackExecutor()
    
    def monitor(self):
        while True:
            # Coletar métricas
            error_rate = self.metrics.get_error_rate()
            response_time = self.metrics.get_response_time()
            health_status = self.metrics.get_health_status()
            
            # Verificar triggers
            if self.should_rollback(error_rate, response_time, health_status):
                self.trigger_rollback()
            
            time.sleep(30)  # Check a cada 30 segundos
```

#### **1.2 Configuração de Alertas**
```yaml
# config/rollback_triggers.yaml
automatic_rollback:
  enabled: true
  check_interval: 30s
  triggers:
    - name: "error_rate_threshold"
      metric: "error_rate"
      threshold: 5.0
      duration: "5m"
      action: "rollback"
      
    - name: "response_time_threshold"
      metric: "response_time_p95"
      threshold: 1000
      duration: "3m"
      action: "rollback"
      
    - name: "health_check_failure"
      metric: "health_status"
      threshold: "unhealthy"
      duration: "2m"
      action: "rollback"
```

### **2. EXECUÇÃO AUTOMÁTICA**

#### **2.1 Script de Rollback Automático**
```bash
#!/bin/bash
# scripts/auto_rollback.sh

set -e

# Configurações
CURRENT_VERSION=$(docker images omni-keywords --format "table {{.Tag}}" | grep current | awk '{print $2}')
BACKUP_VERSION=$(docker images omni-keywords --format "table {{.Tag}}" | grep backup | head -1 | awk '{print $2}')
LOG_FILE="/var/log/rollback/auto_rollback_$(date +%Y%m%d_%H%M%S).log"

# Log do início do rollback
echo "$(date): Iniciando rollback automático" >> $LOG_FILE
echo "$(date): Versão atual: $CURRENT_VERSION" >> $LOG_FILE
echo "$(date): Versão de backup: $BACKUP_VERSION" >> $LOG_FILE

# 1. Parar aplicação atual
echo "$(date): Parando aplicação atual..." >> $LOG_FILE
docker-compose -f docker-compose.prod.yml stop app

# 2. Verificar se backup existe
if [ -z "$BACKUP_VERSION" ]; then
    echo "$(date): ERRO: Nenhuma versão de backup encontrada" >> $LOG_FILE
    exit 1
fi

# 3. Fazer rollback
echo "$(date): Executando rollback para $BACKUP_VERSION..." >> $LOG_FILE
docker tag omni-keywords:$BACKUP_VERSION omni-keywords:current

# 4. Iniciar versão anterior
echo "$(date): Iniciando versão anterior..." >> $LOG_FILE
docker-compose -f docker-compose.prod.yml up -d app

# 5. Aguardar inicialização
echo "$(date): Aguardando inicialização..." >> $LOG_FILE
sleep 30

# 6. Verificar health
echo "$(date): Verificando health check..." >> $LOG_FILE
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): Health check OK" >> $LOG_FILE
        break
    fi
    sleep 10
done

# 7. Notificar equipe
echo "$(date): Rollback concluído. Notificando equipe..." >> $LOG_FILE
./scripts/notify_team.sh "Rollback automático executado - Versão: $BACKUP_VERSION"

echo "$(date): Rollback automático concluído com sucesso" >> $LOG_FILE
```

#### **2.2 Validação Pós-Rollback**
```python
# scripts/validation/post_rollback_validator.py
class PostRollbackValidator:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.notification = NotificationService()
    
    def validate_rollback(self):
        """Valida se o rollback foi bem-sucedido"""
        
        # Verificar health checks
        health_ok = self.check_health()
        if not health_ok:
            self.notification.send_alert("Rollback falhou - Health check")
            return False
        
        # Verificar métricas de performance
        performance_ok = self.check_performance()
        if not performance_ok:
            self.notification.send_alert("Rollback falhou - Performance")
            return False
        
        # Verificar funcionalidades críticas
        features_ok = self.check_critical_features()
        if not features_ok:
            self.notification.send_alert("Rollback falhou - Features críticas")
            return False
        
        # Log de sucesso
        self.log_success()
        return True
    
    def check_health(self):
        """Verifica health checks"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_performance(self):
        """Verifica métricas de performance"""
        error_rate = self.metrics.get_error_rate()
        response_time = self.metrics.get_response_time()
        
        return error_rate < 1.0 and response_time < 500
    
    def check_critical_features(self):
        """Verifica funcionalidades críticas"""
        features = [
            "/api/auth/login",
            "/api/keywords/search",
            "/api/analytics/dashboard"
        ]
        
        for feature in features:
            try:
                response = requests.get(f"http://localhost:8000{feature}", timeout=10)
                if response.status_code != 200:
                    return False
            except:
                return False
        
        return True
```

---

## **👨‍💻 ROLLBACK MANUAL**

### **1. PROCEDIMENTO MANUAL**

#### **1.1 Checklist de Rollback Manual**
```bash
#!/bin/bash
# scripts/manual_rollback.sh

echo "=== ROLLBACK MANUAL - OMNİ KEYWORDS FINDER ==="
echo "Data/Hora: $(date)"
echo ""

# 1. Confirmar necessidade
read -p "Confirmar necessidade de rollback? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Rollback cancelado."
    exit 0
fi

# 2. Coletar informações
echo "Coletando informações do sistema..."
CURRENT_VERSION=$(docker images omni-keywords --format "table {{.Tag}}" | grep current | awk '{print $2}')
AVAILABLE_BACKUPS=$(docker images omni-keywords --format "table {{.Tag}}" | grep backup)

echo "Versão atual: $CURRENT_VERSION"
echo "Backups disponíveis:"
echo "$AVAILABLE_BACKUPS"

# 3. Selecionar versão de destino
read -p "Digite a versão de backup para rollback: " BACKUP_VERSION

# 4. Executar rollback
echo "Executando rollback para $BACKUP_VERSION..."
./scripts/execute_rollback.sh $BACKUP_VERSION

# 5. Validar rollback
echo "Validando rollback..."
./scripts/validate_rollback.sh

echo "Rollback manual concluído."
```

#### **1.2 Script de Execução**
```bash
#!/bin/bash
# scripts/execute_rollback.sh

BACKUP_VERSION=$1
LOG_FILE="/var/log/rollback/manual_rollback_$(date +%Y%m%d_%H%M%S).log"

echo "$(date): Iniciando rollback manual para $BACKUP_VERSION" >> $LOG_FILE

# 1. Backup da configuração atual
echo "$(date): Fazendo backup da configuração atual..." >> $LOG_FILE
cp config/production.yaml config/production.yaml.backup.$(date +%Y%m%d_%H%M%S)

# 2. Parar aplicação
echo "$(date): Parando aplicação..." >> $LOG_FILE
docker-compose -f docker-compose.prod.yml stop app

# 3. Verificar se versão existe
if ! docker images omni-keywords:$BACKUP_VERSION > /dev/null 2>&1; then
    echo "$(date): ERRO: Versão $BACKUP_VERSION não encontrada" >> $LOG_FILE
    exit 1
fi

# 4. Executar rollback
echo "$(date): Executando rollback..." >> $LOG_FILE
docker tag omni-keywords:$BACKUP_VERSION omni-keywords:current

# 5. Iniciar aplicação
echo "$(date): Iniciando aplicação..." >> $LOG_FILE
docker-compose -f docker-compose.prod.yml up -d app

# 6. Aguardar inicialização
echo "$(date): Aguardando inicialização..." >> $LOG_FILE
sleep 30

# 7. Verificar health
echo "$(date): Verificando health..." >> $LOG_FILE
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): Health check OK" >> $LOG_FILE
        break
    fi
    echo "$(date): Tentativa $i de health check..." >> $LOG_FILE
    sleep 10
done

echo "$(date): Rollback manual concluído" >> $LOG_FILE
```

### **2. ROLLBACK GRADUAL**

#### **2.1 Blue-Green Deployment**
```yaml
# docker-compose.blue-green.yml
version: '3.8'

services:
  app-blue:
    image: omni-keywords:blue
    ports:
      - "8001:8000"
    environment:
      - ENVIRONMENT=production
      - VERSION=blue
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  app-green:
    image: omni-keywords:green
    ports:
      - "8002:8000"
    environment:
      - ENVIRONMENT=production
      - VERSION=green
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app-blue
      - app-green
```

#### **2.2 Script de Switch**
```bash
#!/bin/bash
# scripts/switch_environment.sh

TARGET_ENV=$1  # blue ou green

echo "Switching traffic to $TARGET_ENV environment..."

# Atualizar configuração do nginx
sed -i "s/proxy_pass http:\/\/app-.*:8000/proxy_pass http:\/\/app-$TARGET_ENV:8000/g" nginx.conf

# Reload nginx
docker-compose -f docker-compose.blue-green.yml exec nginx nginx -s reload

# Verificar switch
sleep 10
curl -f http://localhost/health

echo "Traffic switched to $TARGET_ENV environment"
```

---

## **📊 MONITORAMENTO PÓS-ROLLBACK**

### **1. MÉTRICAS DE RECUPERAÇÃO**

#### **1.1 KPIs de Rollback**
```python
# scripts/metrics/rollback_metrics.py
class RollbackMetrics:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.notification = NotificationService()
    
    def track_rollback_metrics(self):
        """Rastreia métricas pós-rollback"""
        
        # Tempo de recuperação
        recovery_time = self.calculate_recovery_time()
        
        # Taxa de sucesso
        success_rate = self.calculate_success_rate()
        
        # Impacto no usuário
        user_impact = self.calculate_user_impact()
        
        # Log das métricas
        self.log_metrics(recovery_time, success_rate, user_impact)
        
        # Alertar se métricas estão ruins
        if recovery_time > 300 or success_rate < 0.95:
            self.notification.send_alert(f"Rollback metrics degraded: RT={recovery_time}s, SR={success_rate}")
    
    def calculate_recovery_time(self):
        """Calcula tempo de recuperação"""
        # Implementação do cálculo
        pass
    
    def calculate_success_rate(self):
        """Calcula taxa de sucesso"""
        # Implementação do cálculo
        pass
    
    def calculate_user_impact(self):
        """Calcula impacto no usuário"""
        # Implementação do cálculo
        pass
```

#### **1.2 Dashboard de Rollback**
```yaml
# monitoring/dashboards/rollback_dashboard.json
{
  "dashboard": {
    "title": "Rollback Metrics",
    "panels": [
      {
        "title": "Rollback Frequency",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(rollback_total[1h])",
            "legendFormat": "Rollbacks per hour"
          }
        ]
      },
      {
        "title": "Recovery Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(rollback_recovery_time_bucket[5m]))",
            "legendFormat": "95th percentile recovery time"
          }
        ]
      },
      {
        "title": "Rollback Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(rollback_success_total[1h]) / rate(rollback_total[1h])",
            "legendFormat": "Success rate"
          }
        ]
      }
    ]
  }
}
```

### **2. ALERTAS PÓS-ROLLBACK**

#### **2.1 Configuração de Alertas**
```yaml
# config/post_rollback_alerts.yaml
alerts:
  - name: "rollback_frequency_high"
    condition: "rate(rollback_total[1h]) > 0.1"
    duration: "5m"
    severity: "warning"
    message: "High rollback frequency detected"
    
  - name: "recovery_time_slow"
    condition: "histogram_quantile(0.95, rate(rollback_recovery_time_bucket[5m])) > 300"
    duration: "2m"
    severity: "critical"
    message: "Slow rollback recovery time"
    
  - name: "rollback_failure"
    condition: "rate(rollback_failure_total[1h]) > 0"
    duration: "1m"
    severity: "critical"
    message: "Rollback failures detected"
```

---

## **📝 DOCUMENTAÇÃO E LOGS**

### **1. LOGS DE ROLLBACK**

#### **1.1 Estrutura de Logs**
```python
# scripts/logging/rollback_logger.py
import logging
import json
from datetime import datetime

class RollbackLogger:
    def __init__(self):
        self.logger = logging.getLogger('rollback')
        self.logger.setLevel(logging.INFO)
        
        # Handler para arquivo
        fh = logging.FileHandler('/var/log/rollback/rollback.log')
        fh.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
    
    def log_rollback_start(self, version_from, version_to, trigger_type):
        """Log do início do rollback"""
        log_data = {
            'event': 'rollback_started',
            'timestamp': datetime.now().isoformat(),
            'version_from': version_from,
            'version_to': version_to,
            'trigger_type': trigger_type,
            'status': 'started'
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_rollback_complete(self, version_from, version_to, success, duration):
        """Log da conclusão do rollback"""
        log_data = {
            'event': 'rollback_completed',
            'timestamp': datetime.now().isoformat(),
            'version_from': version_from,
            'version_to': version_to,
            'success': success,
            'duration_seconds': duration,
            'status': 'completed'
        }
        
        self.logger.info(json.dumps(log_data))
```

#### **1.2 Análise de Logs**
```bash
#!/bin/bash
# scripts/analyze_rollback_logs.sh

echo "=== ANÁLISE DE LOGS DE ROLLBACK ==="
echo ""

# Estatísticas gerais
echo "Estatísticas dos últimos 30 dias:"
echo "Total de rollbacks: $(grep "rollback_started" /var/log/rollback/rollback.log | wc -l)"
echo "Rollbacks automáticos: $(grep "rollback_started" /var/log/rollback/rollback.log | grep "auto" | wc -l)"
echo "Rollbacks manuais: $(grep "rollback_started" /var/log/rollback/rollback.log | grep "manual" | wc -l)"

echo ""
echo "Rollbacks por trigger:"
grep "rollback_started" /var/log/rollback/rollback.log | jq -r '.trigger_type' | sort | uniq -c

echo ""
echo "Tempo médio de recuperação:"
grep "rollback_completed" /var/log/rollback/rollback.log | jq -r '.duration_seconds' | awk '{sum+=$1} END {print sum/NR " segundos"}'

echo ""
echo "Taxa de sucesso:"
TOTAL=$(grep "rollback_completed" /var/log/rollback/rollback.log | wc -l)
SUCCESS=$(grep "rollback_completed" /var/log/rollback/rollback.log | grep '"success": true' | wc -l)
echo "scale=2; $SUCCESS * 100 / $TOTAL" | bc
echo "%"
```

### **2. DOCUMENTAÇÃO DE INCIDENTES**

#### **2.1 Template de Incident Report**
```markdown
# Incident Report - Rollback

## Informações Básicas
- **Data/Hora**: 2025-01-27 14:30 UTC
- **Tipo**: Rollback Automático/Manual
- **Versão Anterior**: v1.2.3
- **Versão Atual**: v1.2.2
- **Duração**: 5 minutos

## Detalhes do Incidente
- **Trigger**: Error rate > 5% por 5 minutos
- **Sintomas**: Aplicação lenta, erros 500
- **Impacto**: 15% dos usuários afetados

## Ações Tomadas
1. Rollback automático executado
2. Health checks validados
3. Equipe notificada
4. Monitoramento intensificado

## Root Cause Analysis
- **Causa**: Memory leak na nova versão
- **Detecção**: 5 minutos após deploy
- **Resolução**: Rollback para versão estável

## Lições Aprendidas
- Implementar memory profiling em CI/CD
- Adicionar alertas mais proativos
- Melhorar testes de carga

## Ações Corretivas
- [ ] Corrigir memory leak
- [ ] Implementar memory monitoring
- [ ] Adicionar testes de stress
- [ ] Revisar processo de deploy

## Status
- [x] Incidente resolvido
- [x] Usuários notificados
- [x] Documentação atualizada
- [ ] Ações corretivas em andamento
```

---

## **🎯 CONCLUSÃO**

### **Resumo dos Procedimentos**
1. **Rollback Automático**: Executado em <2 minutos baseado em métricas
2. **Rollback Manual**: Disponível para situações específicas
3. **Rollback Gradual**: Blue-green deployment para minimizar impacto
4. **Monitoramento**: Métricas e alertas em tempo real
5. **Documentação**: Logs estruturados e incident reports

### **Próximos Passos**
1. **Implementar rollback automático** em produção
2. **Configurar alertas** de rollback
3. **Treinar equipe** nos procedimentos
4. **Testar procedimentos** em ambiente de staging

---

**📅 Data de Criação**: 2025-01-27  
**👨‍💻 Responsável**: DevOps Team  
**📊 Status**: ✅ PRONTO PARA IMPLEMENTAÇÃO

---

*Guia salvo em: `docs/ROLLBACK_GUIDE.md`* 