# Arquitetura de Monitoramento

Este documento detalha a arquitetura de monitoramento do Omni Keywords Finder.

## Métricas

### Performance
```python
# metrics/performance.py
class PerformanceMetrics:
    def __init__(self):
        self.latency = Histogram(
            'api_latency_seconds',
            'API request latency in seconds',
            ['endpoint', 'method']
        )
        self.requests = Counter(
            'api_requests_total',
            'Total number of API requests',
            ['endpoint', 'method', 'status']
        )
        self.errors = Counter(
            'api_errors_total',
            'Total number of API errors',
            ['endpoint', 'method', 'error_type']
        )
```

### Negócio
```python
# metrics/business.py
class BusinessMetrics:
    def __init__(self):
        self.keywords_processed = Counter(
            'keywords_processed_total',
            'Total number of keywords processed',
            ['language', 'status']
        )
        self.clusters_created = Counter(
            'clusters_created_total',
            'Total number of clusters created',
            ['size', 'score_range']
        )
        self.user_actions = Counter(
            'user_actions_total',
            'Total number of user actions',
            ['action_type', 'user_type']
        )
```

### Infraestrutura
```python
# metrics/infrastructure.py
class InfrastructureMetrics:
    def __init__(self):
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            ['instance']
        )
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['instance']
        )
        self.disk_usage = Gauge(
            'disk_usage_bytes',
            'Disk usage in bytes',
            ['instance', 'mount']
        )
```

## Alertas

### Performance
```yaml
# alerts/performance.yml
groups:
  - name: performance
    rules:
      - alert: HighLatency
        expr: api_latency_seconds > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency detected
          description: "Endpoint {{ $labels.endpoint }} has high latency"

      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          description: "Endpoint {{ $labels.endpoint }} has high error rate"
```

### Infraestrutura
```yaml
# alerts/infrastructure.yml
groups:
  - name: infrastructure
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High CPU usage
          description: "Instance {{ $labels.instance }} has high CPU usage"

      - alert: HighMemoryUsage
        expr: memory_usage_bytes / memory_total_bytes > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High memory usage
          description: "Instance {{ $labels.instance }} has high memory usage"
```

## Dashboards

### Operacional
```json
// dashboards/operational.json
{
  "panels": [
    {
      "title": "API Performance",
      "type": "graph",
      "metrics": [
        "rate(api_latency_seconds[5m])",
        "rate(api_requests_total[5m])",
        "rate(api_errors_total[5m])"
      ]
    },
    {
      "title": "System Resources",
      "type": "graph",
      "metrics": [
        "cpu_usage_percent",
        "memory_usage_bytes",
        "disk_usage_bytes"
      ]
    }
  ]
}
```

### Negócio
```json
// dashboards/business.json
{
  "panels": [
    {
      "title": "Keyword Processing",
      "type": "graph",
      "metrics": [
        "rate(keywords_processed_total[5m])",
        "rate(clusters_created_total[5m])"
      ]
    },
    {
      "title": "User Engagement",
      "type": "graph",
      "metrics": [
        "rate(user_actions_total[5m])"
      ]
    }
  ]
}
```

## Logs

### Estrutura
```python
# logging/config.py
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        }
    },
    'handlers': {
        'json': {
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['json']
    }
}
```

### Exemplo
```json
{
  "timestamp": "2024-03-20T10:00:00Z",
  "level": "INFO",
  "service": "keyword_processor",
  "trace_id": "abc123",
  "message": "Processing keyword",
  "metadata": {
    "keyword": "seo optimization",
    "language": "en",
    "duration_ms": 150
  }
}
```

## Observações

1. Métricas em tempo real
2. Alertas proativos
3. Dashboards atualizados
4. Logs estruturados
5. Retenção adequada
6. Backup de dados
7. Análise de tendências
8. Relatórios periódicos
9. Ajustes contínuos
10. Documentação atualizada 