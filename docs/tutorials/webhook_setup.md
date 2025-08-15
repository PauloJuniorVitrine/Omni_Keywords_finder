# 🔗 **TUTORIAL DE CONFIGURAÇÃO DE WEBHOOKS - OMNİ KEYWORDS FINDER**

## 📋 **Visão Geral**

Este tutorial guia você através da configuração completa de webhooks para receber notificações em tempo real sobre mudanças de ranking, novas keywords, movimentos de concorrentes e outros eventos importantes.

---

## 🎯 **1. CONCEITOS BÁSICOS DE WEBHOOKS**

### **1.1 O que são Webhooks?**

Webhooks são URLs que recebem notificações HTTP em tempo real quando eventos específicos acontecem no Omni Keywords Finder. Eles permitem que seu sistema seja notificado automaticamente sobre:

- **Mudanças de ranking** de keywords monitoradas
- **Novas keywords** descobertas
- **Movimentos de concorrentes** importantes
- **Relatórios prontos** para download
- **Alertas de performance** críticos

### **1.2 Vantagens dos Webhooks**

✅ **Tempo real**: Notificações instantâneas  
✅ **Automação**: Integração com seus sistemas  
✅ **Eficiência**: Não precisa fazer polling  
✅ **Escalabilidade**: Suporte a múltiplos endpoints  
✅ **Confiabilidade**: Retry automático em caso de falha  

---

## 🔧 **2. CONFIGURAÇÃO BÁSICA**

### **2.1 Criando um Webhook**

#### **Via API**
```python
from omnikeywords import OmniKeywords

client = OmniKeywords(api_key="oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Criar webhook básico
webhook = client.create_webhook(
    url="https://seudominio.com/webhook/omnikeywords",
    events=["ranking_change", "new_keyword"],
    secret="seu_secret_webhook_123"
)

print(f"Webhook criado: {webhook.id}")
print(f"Status: {webhook.status}")
```

#### **Via Dashboard**
1. Acesse [app.omnikeywords.com](https://app.omnikeywords.com)
2. Vá para **Settings > Webhooks**
3. Clique em **Add New Webhook**
4. Configure:
   - **URL**: `https://seudominio.com/webhook/omnikeywords`
   - **Events**: Selecione os eventos desejados
   - **Secret**: Digite um secret para segurança
5. Clique em **Save**

### **2.2 Configuração Avançada**

```python
# Configuração avançada de webhook
webhook = client.create_webhook(
    url="https://seudominio.com/webhook/omnikeywords",
    events=[
        "ranking_change",
        "new_keyword", 
        "competitor_move",
        "report_ready",
        "alert_triggered"
    ],
    secret="seu_secret_webhook_123",
    retry_attempts=3,
    retry_delay=300,  # 5 minutos
    timeout=30,  # 30 segundos
    headers={
        "X-Custom-Header": "valor-customizado",
        "Authorization": "Bearer seu-token-interno"
    },
    filters={
        "ranking_change": {
            "position_threshold": 5,  # Só notificar mudanças > 5 posições
            "keywords": ["palavra-chave-critica"]  # Só keywords específicas
        },
        "new_keyword": {
            "min_search_volume": 1000,
            "max_difficulty": 70
        }
    }
)
```

---

## 🛡️ **3. SEGURANÇA E VALIDAÇÃO**

### **3.1 Verificação de Assinatura**

#### **Python (Flask)**
```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)

@app.route('/webhook/omnikeywords', methods=['POST'])
def webhook_handler():
    # Obter headers
    signature = request.headers.get('X-Omni-Signature')
    timestamp = request.headers.get('X-Omni-Timestamp')
    
    # Verificar timestamp (prevenir replay attacks)
    if not is_timestamp_valid(timestamp):
        return jsonify({'error': 'Invalid timestamp'}), 401
    
    # Verificar assinatura
    payload = request.get_data()
    expected_signature = generate_signature(payload, 'seu_secret_webhook_123')
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Processar evento
    event_data = request.json
    process_webhook_event(event_data)
    
    return jsonify({'status': 'success'}), 200

def generate_signature(payload, secret):
    """Gerar assinatura HMAC-SHA256"""
    return hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

def is_timestamp_valid(timestamp, tolerance=300):
    """Verificar se timestamp está dentro da tolerância (5 minutos)"""
    import time
    current_time = int(time.time())
    webhook_time = int(timestamp)
    return abs(current_time - webhook_time) <= tolerance

def process_webhook_event(event_data):
    """Processar evento do webhook"""
    event_type = event_data['event_type']
    
    if event_type == 'ranking_change':
        handle_ranking_change(event_data)
    elif event_type == 'new_keyword':
        handle_new_keyword(event_data)
    elif event_type == 'competitor_move':
        handle_competitor_move(event_data)
    elif event_type == 'report_ready':
        handle_report_ready(event_data)
    elif event_type == 'alert_triggered':
        handle_alert_triggered(event_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

#### **JavaScript (Express)**
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

app.post('/webhook/omnikeywords', (req, res) => {
  // Obter headers
  const signature = req.headers['x-omi-signature'];
  const timestamp = req.headers['x-omi-timestamp'];
  
  // Verificar timestamp
  if (!isTimestampValid(timestamp)) {
    return res.status(401).json({ error: 'Invalid timestamp' });
  }
  
  // Verificar assinatura
  const payload = JSON.stringify(req.body);
  const expectedSignature = generateSignature(payload, 'seu_secret_webhook_123');
  
  if (signature !== expectedSignature) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Processar evento
  const eventData = req.body;
  processWebhookEvent(eventData);
  
  res.json({ status: 'success' });
});

function generateSignature(payload, secret) {
  return crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
}

function isTimestampValid(timestamp, tolerance = 300) {
  const currentTime = Math.floor(Date.now() / 1000);
  const webhookTime = parseInt(timestamp);
  return Math.abs(currentTime - webhookTime) <= tolerance;
}

function processWebhookEvent(eventData) {
  const eventType = eventData.event_type;
  
  switch (eventType) {
    case 'ranking_change':
      handleRankingChange(eventData);
      break;
    case 'new_keyword':
      handleNewKeyword(eventData);
      break;
    case 'competitor_move':
      handleCompetitorMove(eventData);
      break;
    case 'report_ready':
      handleReportReady(eventData);
      break;
    case 'alert_triggered':
      handleAlertTriggered(eventData);
      break;
  }
}

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

### **3.2 Headers de Segurança**

```python
# Headers que você receberá
headers = {
    'X-Omni-Signature': 'sha256=abc123...',  # Assinatura HMAC-SHA256
    'X-Omni-Timestamp': '1643241600',        # Timestamp Unix
    'X-Omni-Event': 'ranking_change',        # Tipo do evento
    'X-Omni-Delivery': 'webhook_123',        # ID da entrega
    'User-Agent': 'OmniKeywords-Webhook/1.0', # User agent
    'Content-Type': 'application/json'        # Tipo de conteúdo
}
```

---

## 📊 **4. TIPOS DE EVENTOS**

### **4.1 Ranking Change Event**

```json
{
  "event_type": "ranking_change",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "domain": "seudominio.com",
    "keyword": "ferramenta seo",
    "old_position": 15,
    "new_position": 8,
    "position_change": 7,
    "search_engine": "google",
    "location": "BR",
    "device": "desktop",
    "url": "https://seudominio.com/ferramenta-seo",
    "search_volume": 12000,
    "cpc": 2.50,
    "competition": 0.65
  },
  "metadata": {
    "tracking_id": "track_123456",
    "alert_level": "positive",
    "significance": "high"
  }
}
```

### **4.2 New Keyword Event**

```json
{
  "event_type": "new_keyword",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "keyword": "ferramenta seo gratuita",
    "search_volume": 5400,
    "difficulty": 45,
    "cpc": 1.80,
    "competition": 0.55,
    "related_keywords": [
      "seo tools free",
      "ferramentas seo online"
    ],
    "search_intent": "informational",
    "seasonality": "stable"
  },
  "metadata": {
    "discovery_method": "competitor_analysis",
    "opportunity_score": 0.75,
    "recommended_action": "create_content"
  }
}
```

### **4.3 Competitor Move Event**

```json
{
  "event_type": "competitor_move",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "competitor_domain": "concorrente.com",
    "keyword": "ferramenta seo",
    "old_position": 12,
    "new_position": 3,
    "position_change": 9,
    "search_engine": "google",
    "location": "BR",
    "url": "https://concorrente.com/ferramenta-seo",
    "search_volume": 12000,
    "threat_level": "high"
  },
  "metadata": {
    "your_position": 8,
    "gap_analysis": "concorrente ultrapassou sua posição",
    "recommended_action": "analyze_competitor_content"
  }
}
```

### **4.4 Report Ready Event**

```json
{
  "event_type": "report_ready",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "report_id": "report_123456",
    "report_type": "seo_performance",
    "date_range": "last_30_days",
    "download_url": "https://api.omnikeywords.com/v1/reports/report_123456/download",
    "expires_at": "2025-02-27T10:30:00Z",
    "file_size": "2.5MB",
    "format": "pdf"
  },
  "metadata": {
    "sections_included": [
      "keyword_performance",
      "ranking_changes",
      "competitor_analysis"
    ],
    "generation_time": "45s"
  }
}
```

### **4.5 Alert Triggered Event**

```json
{
  "event_type": "alert_triggered",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "alert_id": "alert_123456",
    "alert_type": "ranking_drop",
    "severity": "high",
    "trigger_condition": "position_drop > 10",
    "affected_keywords": [
      {
        "keyword": "palavra-chave-critica",
        "old_position": 5,
        "new_position": 18,
        "position_change": -13
      }
    ]
  },
  "metadata": {
    "alert_rule": "ranking_drop_critical",
    "notification_channels": ["email", "slack", "webhook"]
  }
}
```

---

## 🔄 **5. PROCESSAMENTO DE EVENTOS**

### **5.1 Handler para Ranking Changes**

```python
def handle_ranking_change(event_data):
    """Processar mudanças de ranking"""
    data = event_data['data']
    
    # Log da mudança
    print(f"Ranking mudou para '{data['keyword']}': "
          f"{data['old_position']} → {data['new_position']} "
          f"({data['position_change']:+d})")
    
    # Determinar severidade
    if data['position_change'] < -10:
        severity = "CRÍTICO"
        action = "investigar_imediatamente"
    elif data['position_change'] < -5:
        severity = "ALTO"
        action = "analisar_conteúdo"
    elif data['position_change'] > 5:
        severity = "POSITIVO"
        action = "replicar_estrategia"
    else:
        severity = "NORMAL"
        action = "monitorar"
    
    # Enviar notificação
    send_notification(
        title=f"Ranking {severity}: {data['keyword']}",
        message=f"Posição {data['old_position']} → {data['new_position']}",
        severity=severity,
        action=action
    )
    
    # Atualizar dashboard
    update_dashboard_ranking(data)
    
    # Criar ticket se crítico
    if severity == "CRÍTICO":
        create_support_ticket(data)

def send_notification(title, message, severity, action):
    """Enviar notificação via múltiplos canais"""
    # Email
    if severity in ["CRÍTICO", "ALTO"]:
        send_email_notification(title, message, severity)
    
    # Slack
    send_slack_notification(title, message, severity, action)
    
    # SMS (apenas crítico)
    if severity == "CRÍTICO":
        send_sms_notification(title, message)

def update_dashboard_ranking(data):
    """Atualizar dashboard em tempo real"""
    # Atualizar cache
    cache_key = f"ranking:{data['keyword']}"
    cache.set(cache_key, {
        'position': data['new_position'],
        'change': data['position_change'],
        'updated_at': datetime.now()
    }, timeout=3600)
    
    # Enviar para WebSocket
    websocket_manager.broadcast('ranking_update', data)

def create_support_ticket(data):
    """Criar ticket de suporte para mudanças críticas"""
    ticket_data = {
        'title': f"Queda crítica de ranking: {data['keyword']}",
        'description': f"""
        Keyword: {data['keyword']}
        Mudança: {data['old_position']} → {data['new_position']} ({data['position_change']:+d})
        Volume de busca: {data['search_volume']}
        CPC: ${data['cpc']}
        URL: {data['url']}
        """,
        'priority': 'high',
        'category': 'ranking_issue'
    }
    
    # Integração com sistema de tickets
    ticket_system.create_ticket(ticket_data)
```

### **5.2 Handler para New Keywords**

```python
def handle_new_keyword(event_data):
    """Processar novas keywords descobertas"""
    data = event_data['data']
    
    print(f"Nova keyword descoberta: '{data['keyword']}' "
          f"(Volume: {data['search_volume']}, Dificuldade: {data['difficulty']})")
    
    # Avaliar oportunidade
    opportunity_score = calculate_opportunity_score(data)
    
    if opportunity_score > 0.7:
        # Alta oportunidade - criar conteúdo
        create_content_task(data)
        send_notification(
            title=f"Alta oportunidade: {data['keyword']}",
            message=f"Volume: {data['search_volume']}, Dificuldade: {data['difficulty']}",
            severity="ALTO",
            action="criar_conteúdo"
        )
    elif opportunity_score > 0.5:
        # Média oportunidade - adicionar à lista
        add_to_keyword_list(data)
        send_notification(
            title=f"Oportunidade: {data['keyword']}",
            message=f"Adicionada à lista de keywords",
            severity="MÉDIO",
            action="monitorar"
        )

def calculate_opportunity_score(data):
    """Calcular score de oportunidade"""
    # Fatores para cálculo
    volume_score = min(data['search_volume'] / 10000, 1.0)  # Normalizar volume
    difficulty_score = 1 - (data['difficulty'] / 100)  # Dificuldade inversa
    cpc_score = min(data['cpc'] / 5.0, 1.0)  # Normalizar CPC
    
    # Peso dos fatores
    weights = {
        'volume': 0.4,
        'difficulty': 0.4,
        'cpc': 0.2
    }
    
    score = (
        volume_score * weights['volume'] +
        difficulty_score * weights['difficulty'] +
        cpc_score * weights['cpc']
    )
    
    return score

def create_content_task(data):
    """Criar tarefa de criação de conteúdo"""
    task_data = {
        'title': f"Criar conteúdo para: {data['keyword']}",
        'description': f"""
        Keyword: {data['keyword']}
        Volume de busca: {data['search_volume']}
        Dificuldade: {data['difficulty']}
        CPC: ${data['cpc']}
        Intenção: {data['search_intent']}
        Keywords relacionadas: {', '.join(data['related_keywords'])}
        """,
        'priority': 'high',
        'deadline': datetime.now() + timedelta(days=7),
        'assignee': 'content_team'
    }
    
    # Integração com sistema de tarefas
    task_system.create_task(task_data)
```

### **5.3 Handler para Competitor Moves**

```python
def handle_competitor_move(event_data):
    """Processar movimentos de concorrentes"""
    data = event_data['data']
    
    print(f"Concorrente '{data['competitor_domain']}' moveu para "
          f"'{data['keyword']}': {data['old_position']} → {data['new_position']}")
    
    # Analisar ameaça
    threat_level = analyze_threat_level(data)
    
    if threat_level == "ALTO":
        # Concorrente ultrapassou sua posição
        analyze_competitor_content(data)
        send_notification(
            title=f"Concorrente ultrapassou: {data['keyword']}",
            message=f"{data['competitor_domain']} agora está na posição {data['new_position']}",
            severity="ALTO",
            action="analisar_concorrente"
        )
    elif threat_level == "MÉDIO":
        # Concorrente melhorou significativamente
        monitor_competitor_moves(data)
        send_notification(
            title=f"Concorrente melhorou: {data['keyword']}",
            message=f"{data['competitor_domain']} subiu {data['position_change']} posições",
            severity="MÉDIO",
            action="monitorar"
        )

def analyze_threat_level(data):
    """Analisar nível de ameaça do movimento do concorrente"""
    your_position = data.get('your_position', 999)
    competitor_position = data['new_position']
    position_change = data['position_change']
    
    # Concorrente ultrapassou sua posição
    if competitor_position < your_position:
        return "ALTO"
    
    # Concorrente melhorou significativamente
    elif position_change > 10:
        return "MÉDIO"
    
    # Movimento normal
    else:
        return "BAIXO"

def analyze_competitor_content(data):
    """Analisar conteúdo do concorrente"""
    competitor_url = data['url']
    
    # Extrair conteúdo
    content = extract_webpage_content(competitor_url)
    
    # Analisar com IA
    analysis = ai_analyzer.analyze_content(content)
    
    # Criar relatório
    report_data = {
        'competitor': data['competitor_domain'],
        'keyword': data['keyword'],
        'url': competitor_url,
        'analysis': analysis,
        'recommendations': generate_recommendations(analysis)
    }
    
    # Salvar relatório
    save_competitor_analysis(report_data)
    
    # Enviar para equipe
    send_competitor_analysis_report(report_data)
```

---

## 🔧 **6. CONFIGURAÇÃO AVANÇADA**

### **6.1 Filtros de Eventos**

```python
# Configurar webhook com filtros avançados
webhook = client.create_webhook(
    url="https://seudominio.com/webhook/omnikeywords",
    events=["ranking_change", "new_keyword", "competitor_move"],
    filters={
        "ranking_change": {
            "position_threshold": 5,  # Só mudanças > 5 posições
            "keywords": ["palavra-chave-critica", "termo-importante"],
            "search_engines": ["google"],  # Só Google
            "locations": ["BR"],  # Só Brasil
            "devices": ["desktop", "mobile"]
        },
        "new_keyword": {
            "min_search_volume": 1000,
            "max_difficulty": 70,
            "min_cpc": 0.5,
            "search_intent": ["informational", "commercial"]
        },
        "competitor_move": {
            "competitors": ["concorrente1.com", "concorrente2.com"],
            "position_threshold": 10,  # Só movimentos > 10 posições
            "threat_level": ["high", "medium"]
        }
    }
)
```

### **6.2 Retry e Timeout**

```python
# Configuração de retry
webhook = client.create_webhook(
    url="https://seudominio.com/webhook/omnikeywords",
    events=["ranking_change"],
    retry_attempts=5,  # 5 tentativas
    retry_delay=600,   # 10 minutos entre tentativas
    timeout=60,        # 60 segundos de timeout
    exponential_backoff=True  # Backoff exponencial
)
```

### **6.3 Headers Customizados**

```python
# Headers customizados
webhook = client.create_webhook(
    url="https://seudominio.com/webhook/omnikeywords",
    events=["ranking_change"],
    headers={
        "X-Custom-Header": "valor-customizado",
        "Authorization": "Bearer seu-token-interno",
        "X-Environment": "production",
        "X-Source": "omnikeywords-webhook"
    }
)
```

---

## 📊 **7. MONITORAMENTO E DEBUG**

### **7.1 Logs de Webhook**

```python
# Verificar logs de webhook
logs = client.get_webhook_logs(
    webhook_id="webhook_123456",
    date_range="last_7_days",
    status="all"  # ou "success", "failed"
)

for log in logs:
    print(f"Timestamp: {log.timestamp}")
    print(f"Status: {log.status}")
    print(f"Response Code: {log.response_code}")
    print(f"Response Time: {log.response_time}ms")
    print(f"Payload Size: {log.payload_size} bytes")
    print("---")
```

### **7.2 Teste de Webhook**

```python
# Testar webhook
test_result = client.test_webhook(
    webhook_id="webhook_123456",
    test_event="ranking_change",
    test_data={
        "keyword": "teste-webhook",
        "old_position": 20,
        "new_position": 15
    }
)

print(f"Teste realizado: {test_result.success}")
print(f"Response Code: {test_result.response_code}")
print(f"Response Time: {test_result.response_time}ms")
print(f"Response Body: {test_result.response_body}")
```

### **7.3 Dashboard de Webhooks**

```python
# Obter estatísticas de webhooks
stats = client.get_webhook_stats(
    webhook_id="webhook_123456",
    date_range="last_30_days"
)

print(f"Total de eventos: {stats.total_events}")
print(f"Sucessos: {stats.successful_deliveries}")
print(f"Falhas: {stats.failed_deliveries}")
print(f"Taxa de sucesso: {stats.success_rate:.2%}")
print(f"Tempo médio de resposta: {stats.avg_response_time}ms")
```

---

## 🚀 **8. CASOS DE USO AVANÇADOS**

### **8.1 Sistema de Alertas Inteligentes**

```python
class IntelligentAlertSystem:
    def __init__(self):
        self.alert_rules = {}
        self.escalation_levels = {
            'low': ['email'],
            'medium': ['email', 'slack'],
            'high': ['email', 'slack', 'sms'],
            'critical': ['email', 'slack', 'sms', 'phone']
        }
    
    def add_alert_rule(self, rule):
        """Adicionar regra de alerta"""
        self.alert_rules[rule['id']] = rule
    
    def process_webhook_event(self, event_data):
        """Processar evento e gerar alertas"""
        alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if self.should_trigger_alert(event_data, rule):
                alert = self.create_alert(event_data, rule)
                alerts.append(alert)
        
        return alerts
    
    def should_trigger_alert(self, event_data, rule):
        """Verificar se deve disparar alerta"""
        if event_data['event_type'] != rule['event_type']:
            return False
        
        data = event_data['data']
        
        if rule['event_type'] == 'ranking_change':
            return (
                data['position_change'] <= rule['position_threshold'] and
                data['keyword'] in rule['keywords']
            )
        
        return True
    
    def create_alert(self, event_data, rule):
        """Criar alerta"""
        severity = self.calculate_severity(event_data, rule)
        
        return {
            'id': f"alert_{int(time.time())}",
            'rule_id': rule['id'],
            'event_data': event_data,
            'severity': severity,
            'channels': self.escalation_levels[severity],
            'created_at': datetime.now(),
            'message': self.generate_alert_message(event_data, rule)
        }
    
    def calculate_severity(self, event_data, rule):
        """Calcular severidade do alerta"""
        data = event_data['data']
        
        if event_data['event_type'] == 'ranking_change':
            if data['position_change'] < -20:
                return 'critical'
            elif data['position_change'] < -10:
                return 'high'
            elif data['position_change'] < -5:
                return 'medium'
            else:
                return 'low'
        
        return rule.get('default_severity', 'medium')
    
    def generate_alert_message(self, event_data, rule):
        """Gerar mensagem do alerta"""
        data = event_data['data']
        
        if event_data['event_type'] == 'ranking_change':
            return (
                f"🚨 ALERTA: Ranking caiu para '{data['keyword']}'\n"
                f"Posição: {data['old_position']} → {data['new_position']} "
                f"({data['position_change']:+d})\n"
                f"Volume: {data['search_volume']:,} buscas/mês\n"
                f"CPC: ${data['cpc']:.2f}"
            )
        
        return f"Alerta disparado: {event_data['event_type']}"

# Configuração do sistema
alert_system = IntelligentAlertSystem()

# Adicionar regras
alert_system.add_alert_rule({
    'id': 'critical_ranking_drop',
    'event_type': 'ranking_change',
    'position_threshold': -10,
    'keywords': ['palavra-chave-critica'],
    'default_severity': 'critical'
})

alert_system.add_alert_rule({
    'id': 'competitor_overtake',
    'event_type': 'competitor_move',
    'default_severity': 'high'
})

# Processar evento
def handle_webhook_event(event_data):
    alerts = alert_system.process_webhook_event(event_data)
    
    for alert in alerts:
        send_alert(alert)
```

### **8.2 Integração com CRM**

```python
class CRMIntegration:
    def __init__(self, crm_client):
        self.crm = crm_client
    
    def handle_ranking_change(self, event_data):
        """Integrar mudança de ranking com CRM"""
        data = event_data['data']
        
        # Criar lead se ranking melhorou significativamente
        if data['position_change'] > 10:
            lead_data = {
                'source': 'omnikeywords_ranking_improvement',
                'keyword': data['keyword'],
                'search_volume': data['search_volume'],
                'cpc': data['cpc'],
                'position_change': data['position_change'],
                'notes': f"Ranking melhorou {data['position_change']} posições"
            }
            
            self.crm.create_lead(lead_data)
        
        # Atualizar oportunidades existentes
        opportunities = self.crm.find_opportunities_by_keyword(data['keyword'])
        for opp in opportunities:
            self.crm.update_opportunity(opp['id'], {
                'ranking_position': data['new_position'],
                'ranking_change': data['position_change'],
                'last_updated': datetime.now()
            })
    
    def handle_new_keyword(self, event_data):
        """Integrar nova keyword com CRM"""
        data = event_data['data']
        
        # Criar oportunidade para keywords de alto valor
        if data['search_volume'] > 5000 and data['cpc'] > 2.0:
            opportunity_data = {
                'name': f"Oportunidade: {data['keyword']}",
                'keyword': data['keyword'],
                'search_volume': data['search_volume'],
                'cpc': data['cpc'],
                'difficulty': data['difficulty'],
                'stage': 'prospecting',
                'value': data['search_volume'] * data['cpc'] * 0.01,  # Estimativa de valor
                'source': 'omnikeywords_discovery'
            }
            
            self.crm.create_opportunity(opportunity_data)
```

### **8.3 Integração com Slack**

```python
import requests

class SlackIntegration:
    def __init__(self, webhook_url, channel="#seo-alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    def send_ranking_alert(self, event_data):
        """Enviar alerta de ranking para Slack"""
        data = event_data['data']
        
        # Determinar cor baseada na mudança
        if data['position_change'] > 0:
            color = "good"  # Verde
            emoji = "📈"
        else:
            color = "danger"  # Vermelho
            emoji = "📉"
        
        # Criar mensagem
        message = {
            "channel": self.channel,
            "attachments": [{
                "color": color,
                "title": f"{emoji} Ranking Update: {data['keyword']}",
                "fields": [
                    {
                        "title": "Position Change",
                        "value": f"{data['old_position']} → {data['new_position']} ({data['position_change']:+d})",
                        "short": True
                    },
                    {
                        "title": "Search Volume",
                        "value": f"{data['search_volume']:,}",
                        "short": True
                    },
                    {
                        "title": "CPC",
                        "value": f"${data['cpc']:.2f}",
                        "short": True
                    },
                    {
                        "title": "URL",
                        "value": data['url'],
                        "short": False
                    }
                ],
                "footer": "Omni Keywords Finder",
                "ts": int(datetime.now().timestamp())
            }]
        }
        
        # Enviar para Slack
        response = requests.post(self.webhook_url, json=message)
        return response.status_code == 200

# Configuração
slack_integration = SlackIntegration(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    channel="#seo-alerts"
)

# Usar no handler
def handle_ranking_change(event_data):
    # Processar evento
    process_ranking_change(event_data)
    
    # Enviar para Slack
    slack_integration.send_ranking_alert(event_data)
```

---

## 📚 **9. RECURSOS ADICIONAIS**

### **9.1 Documentação Relacionada**
- [API Reference](../api/endpoints.md)
- [Authentication Guide](../api/authentication.md)
- [Rate Limiting](../api/rate_limiting.md)
- [Error Codes](../api/error_codes.md)

### **9.2 Ferramentas de Desenvolvimento**
- [Webhook Tester](https://webhook.site) - Para testar webhooks
- [ngrok](https://ngrok.com) - Para desenvolvimento local
- [Postman](https://postman.com) - Para testar APIs

### **9.3 Exemplos de Código**
- [Exemplos Python](https://github.com/omnikeywords/webhook-examples)
- [Exemplos JavaScript](https://github.com/omnikeywords/webhook-examples-js)
- [Exemplos PHP](https://github.com/omnikeywords/webhook-examples-php)

### **9.4 Suporte**
- [FAQ](../troubleshooting/faq.md)
- [Debug Guide](../troubleshooting/debug_guide.md)
- [Community Forum](https://community.omnikeywords.com)
- [Email Support](mailto:webhook-support@omnikeywords.com)

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Configure** seu primeiro webhook básico
2. **Implemente** a verificação de assinatura
3. **Configure** filtros para eventos específicos
4. **Integre** com seus sistemas existentes
5. **Monitore** o desempenho dos webhooks
6. **Implemente** sistema de alertas inteligentes

---

**💡 Dica**: Use ngrok durante o desenvolvimento para receber webhooks localmente: `ngrok http 3000`

---

*Última atualização: 2025-01-27*  
*Versão: 1.0.0* 