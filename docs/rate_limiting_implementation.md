# Rate Limiting Inteligente - Implementação Completa

## 📋 Visão Geral

O sistema de rate limiting inteligente foi implementado seguindo as melhores práticas de segurança, com foco em proteção adaptativa contra abuso e detecção de padrões suspeitos.

## 🏗️ Arquitetura

### **Componentes Principais**

1. **AdaptiveRateLimiter** - Rate limiter principal com detecção adaptativa
2. **PatternDetector** - Detector de padrões suspeitos
3. **RateLimitConfig** - Configuração centralizada
4. **Middleware** - Integração com Flask e FastAPI

### **Fluxo de Funcionamento**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Requisição    │───▶│  Rate Limiter   │───▶│  Pattern Det.   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Cache Redis   │
                       │   (Métricas)    │
                       └─────────────────┘
```

## 🔧 Configuração

### **Variáveis de Ambiente**

```bash
# Rate Limiting Inteligente
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_REQUESTS_PER_DAY=10000
RATE_LIMIT_BURST_LIMIT=10
RATE_LIMIT_WINDOW_SIZE=60
RATE_LIMIT_COOLDOWN_PERIOD=300
RATE_LIMIT_ADAPTIVE_ENABLED=true
RATE_LIMIT_LEARNING_PERIOD=3600
RATE_LIMIT_ANOMALY_THRESHOLD=2.0
RATE_LIMIT_ALERT_THRESHOLD=100
RATE_LIMIT_ALERT_COOLDOWN=3600
```

### **Estratégias de Rate Limiting**

- **FIXED**: Limite fixo por minuto
- **SLIDING_WINDOW**: Janela deslizante
- **TOKEN_BUCKET**: Bucket de tokens
- **ADAPTIVE**: Adaptativo com detecção de padrões

## 🧠 Detecção de Padrões

### **Análises Implementadas**

1. **Frequência de Requisições**
   - Detecta padrões muito regulares (bot-like)
   - Analisa intervalos entre requisições
   - Calcula variância temporal

2. **Padrão Temporal**
   - Detecta atividade 24/7 (suspeito)
   - Identifica horários suspeitos (2-6 AM)
   - Analisa distribuição por hora

3. **Padrão de Payload**
   - Detecta payloads idênticos
   - Identifica tamanhos suspeitos
   - Analisa variação de conteúdo

4. **Padrão de User Agent**
   - Detecta user agents suspeitos
   - Identifica múltiplos user agents
   - Analisa padrões de navegador

5. **Padrão de Resposta**
   - Detecta muitos erros
   - Analisa tempos de resposta consistentes
   - Identifica padrões de status code

### **Níveis de Ameaça**

- **LOW**: Comportamento normal
- **MEDIUM**: Padrão levemente suspeito
- **HIGH**: Padrão muito suspeito
- **CRITICAL**: Bloqueio automático

## 📊 Métricas e Monitoramento

### **Métricas Coletadas**

```python
{
    'total_requests': 10000,
    'blocked_requests': 150,
    'rate_limited_requests': 300,
    'anomalies_detected': 50,
    'alerts_sent': 10,
    'block_rate': 1.5,           # %
    'rate_limit_rate': 3.0,      # %
    'anomaly_rate': 0.5,         # %
    'alert_rate': 0.1,           # %
    'blocked_ips_count': 25
}
```

### **Headers de Resposta**

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
X-RateLimit-ThreatLevel: low
X-RateLimit-AnomalyScore: 0.15
Retry-After: 60
```

## 🚀 Uso Prático

### **Configuração Básica**

```python
from infrastructure.security.rate_limiting import AdaptiveRateLimiter, RateLimitConfig

# Configuração customizada
config = RateLimitConfig(
    requests_per_minute=30,
    burst_limit=5,
    adaptive_enabled=True
)

# Criar rate limiter
rate_limiter = AdaptiveRateLimiter(config)
```

### **Processamento de Requisições**

```python
from infrastructure.security.rate_limiting import RequestInfo

# Criar informações da requisição
request_info = RequestInfo(
    timestamp=time.time(),
    ip="192.168.1.1",
    user_agent="Mozilla/5.0",
    endpoint="/api/keywords",
    method="GET",
    response_time=0.1,
    status_code=200,
    payload_size=100
)

# Processar rate limiting
allowed, info = await rate_limiter.process_request(request_info)

if not allowed:
    print(f"Rate limit exceeded: {info}")
else:
    print(f"Request allowed. Remaining: {info['remaining']}")
```

### **Middleware Flask**

```python
from flask import Flask
from infrastructure.security.rate_limiting_middleware import configure_flask_rate_limiting

app = Flask(__name__)

# Configurar rate limiting
configure_flask_rate_limiting(app)

@app.route('/api/keywords')
def get_keywords():
    return {"keywords": ["python", "flask", "api"]}
```

### **Middleware FastAPI**

```python
from fastapi import FastAPI
from infrastructure.security.rate_limiting_middleware import configure_fastapi_rate_limiting

app = FastAPI()

# Configurar rate limiting
configure_fastapi_rate_limiting(app)

@app.get("/api/keywords")
async def get_keywords():
    return {"keywords": ["python", "fastapi", "api"]}
```

### **Decorators**

```python
from infrastructure.security.rate_limiting_middleware import flask_rate_limited, fastapi_rate_limited

# Flask
@app.route('/api/sensitive')
@flask_rate_limited(requests_per_minute=10)
def sensitive_endpoint():
    return {"data": "sensitive"}

# FastAPI
@app.get("/api/sensitive")
@fastapi_rate_limited(requests_per_minute=10)
async def sensitive_endpoint():
    return {"data": "sensitive"}
```

## 🔒 Segurança e Proteção

### **Whitelist/Blacklist**

```python
config = RateLimitConfig(
    whitelist_ips=["192.168.1.100", "10.0.0.1"],
    blacklist_ips=["192.168.1.200", "10.0.0.2"]
)
```

### **Bloqueio Temporário**

- **Ameaça CRÍTICA**: Bloqueio automático por 5 minutos
- **Ameaça ALTA**: Rate limit muito restritivo (5 req/min)
- **Ameaça MÉDIA**: Rate limit moderado (10 req/min)

### **Alertas Automáticos**

- Enviados quando detecta atividade suspeita
- Cooldown de 1 hora para evitar spam
- Logs estruturados com contexto completo

## 📈 Performance

### **Benchmarks Esperados**

- **Latência**: < 1ms para verificação
- **Throughput**: 10.000+ req/segundo
- **Precisão**: > 95% detecção de bots
- **Falsos Positivos**: < 1%

### **Otimizações Implementadas**

1. **Cache Distribuído** - Métricas em Redis
2. **Análise Incremental** - Processamento em tempo real
3. **Lazy Loading** - Inicialização sob demanda
4. **Connection Pooling** - Reutilização de conexões

## 🧪 Testes

### **Cobertura de Testes**

- ✅ Configuração
- ✅ Detecção de Padrões
- ✅ Rate Limiting Adaptativo
- ✅ Whitelist/Blacklist
- ✅ Métricas
- ✅ Middleware
- ✅ Integração

### **Executar Testes**

```bash
# Testes unitários
pytest tests/unit/test_rate_limiting.py -v

# Testes com cobertura
pytest tests/unit/test_rate_limiting.py --cov=infrastructure.security.rate_limiting --cov-report=html
```

## 🔄 Integração

### **Flask**

```python
# app.py
from flask import Flask
from infrastructure.security.rate_limiting_middleware import configure_flask_rate_limiting

app = Flask(__name__)

# Configurar rate limiting global
configure_flask_rate_limiting(app)

# Rotas com rate limiting específico
@app.route('/api/keywords')
@flask_rate_limited(requests_per_minute=30)
def get_keywords():
    return {"keywords": []}
```

### **FastAPI**

```python
# main.py
from fastapi import FastAPI
from infrastructure.security.rate_limiting_middleware import configure_fastapi_rate_limiting

app = FastAPI()

# Configurar rate limiting global
configure_fastapi_rate_limiting(app)

# Rotas com rate limiting específico
@app.get("/api/keywords")
@fastapi_rate_limited(requests_per_minute=30)
async def get_keywords():
    return {"keywords": []}
```

## 🚨 Troubleshooting

### **Problemas Comuns**

#### **Rate Limit Muito Restritivo**
```python
# Ajustar configurações
config = RateLimitConfig(
    requests_per_minute=120,  # Aumentar limite
    anomaly_threshold=3.0     # Aumentar threshold
)
```

#### **Falsos Positivos**
```python
# Adicionar IPs à whitelist
config.whitelist_ips.append("192.168.1.100")
```

#### **Performance Degradada**
- Verificar conexão com Redis
- Monitorar uso de memória
- Ajustar janela de análise

### **Logs Importantes**

```python
# Conexão
"event": "rate_limiter_initialized"

# Rate limiting
"event": "rate_limit_exceeded"
"event": "ip_blocked_critical"

# Alertas
"event": "rate_limit_alert"
"event": "anomaly_detected"
```

## 📚 Referências

- [OWASP Rate Limiting](https://owasp.org/www-project-api-security-top-10/)
- [Redis Rate Limiting](https://redis.io/topics/patterns/distributed-locks)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/)
- [FastAPI Rate Limiting](https://fastapi.tiangolo.com/tutorial/security/)

## 🎯 Próximos Passos

1. **Machine Learning**
   - Detecção de padrões com ML
   - Aprendizado contínuo
   - Modelos personalizados

2. **Geolocalização**
   - Rate limiting por região
   - Detecção de VPN/Proxy
   - Bloqueio geográfico

3. **Integração Avançada**
   - WAF (Web Application Firewall)
   - SIEM (Security Information and Event Management)
   - Dashboards de segurança 