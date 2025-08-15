# Guia de Monitoramento

Este documento detalha as práticas de monitoramento do Omni Keywords Finder.

## Métricas

### 1. Prometheus

```python
# infrastructure/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# API
api_requests = Counter(
    'api_requests_total',
    'Total de requisições',
    ['endpoint', 'method']
)

api_latency = Histogram(
    'api_latency_seconds',
    'Latência da API',
    ['endpoint']
)

# ML
model_predictions = Counter(
    'model_predictions_total',
    'Total de predições',
    ['model']
)

model_latency = Histogram(
    'model_latency_seconds',
    'Latência do modelo',
    ['model']
)

# Sistema
memory_usage = Gauge(
    'memory_usage_bytes',
    'Uso de memória'
)

cpu_usage = Gauge(
    'cpu_usage_percent',
    'Uso de CPU'
)
```

### 2. Grafana

```yaml
# dashboards/api.yaml
apiVersion: 1
providers:
  - name: 'API'
    orgId: 1
    folder: ''
    type: file
    options:
      path: /var/lib/grafana/dashboards

dashboard:
  title: API Metrics
  panels:
    - title: Requests
      type: graph
      targets:
        - expr: rate(api_requests_total[5m])
          legendFormat: "{{endpoint}}"
    
    - title: Latency
      type: graph
      targets:
        - expr: rate(api_latency_seconds_sum[5m]) / rate(api_latency_seconds_count[5m])
          legendFormat: "{{endpoint}}"
    
    - title: Model Performance
      type: graph
      targets:
        - expr: rate(model_predictions_total[5m])
          legendFormat: "{{model}}"
```

## Logs

### 1. Estrutura

```python
# infrastructure/monitoring/logging.py
import structlog

logger = structlog.get_logger()

def log_request(request):
    logger.info(
        "request_received",
        method=request.method,
        path=request.path,
        client=request.client,
        user=request.user
    )

def log_error(error):
    logger.error(
        "error_occurred",
        error=str(error),
        traceback=error.__traceback__
    )
```

### 2. ELK Stack

```yaml
# elasticsearch.yaml
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
spec:
  ports:
    - port: 9200
  selector:
    app: elasticsearch
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
        - name: elasticsearch
          image: docker.elastic.co/elasticsearch/elasticsearch:7.9.3
          ports:
            - containerPort: 9200
          env:
            - name: discovery.type
              value: single-node
```

## Alertas

### 1. Prometheus Rules

```yaml
# prometheus/rules.yaml
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: rate(api_requests_total{status=~"5.."}[5m]) / rate(api_requests_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          description: "Error rate is above 10% for 5 minutes"
      
      - alert: HighLatency
        expr: rate(api_latency_seconds_sum[5m]) / rate(api_latency_seconds_count[5m]) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency"
          description: "API latency is above 1s for 5 minutes"
```

### 2. AlertManager

```yaml
# alertmanager/config.yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/xxx'

route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack'

receivers:
  - name: 'slack'
    slack_configs:
      - channel: '#alerts'
        send_resolved: true
```

## Tracing

### 1. OpenTelemetry

```python
# infrastructure/monitoring/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

def setup_tracing():
    trace.set_tracer_provider(TracerProvider())
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

def trace_request(func):
    def wrapper(*args, **kwargs):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(func.__name__):
            return func(*args, **kwargs)
    return wrapper
```

### 2. Jaeger

```yaml
# jaeger.yaml
apiVersion: v1
kind: Service
metadata:
  name: jaeger
spec:
  ports:
    - port: 16686
  selector:
    app: jaeger
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:1.22
          ports:
            - containerPort: 16686
          env:
            - name: SPAN_STORAGE_TYPE
              value: elasticsearch
            - name: ES_SERVER_URLS
              value: http://elasticsearch:9200
```

## Observações

- Monitorar métricas
- Analisar logs
- Configurar alertas
- Rastrear requisições
- Visualizar dados
- Manter histórico
- Otimizar performance
- Documentar práticas
- Revisar periodicamente
- Manter compatibilidade 