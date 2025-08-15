# Práticas de Monitoramento

Este documento detalha as práticas de monitoramento do Omni Keywords Finder.

## Métricas

### 1. Prometheus

```python
# api/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, List
import time

# Métricas da API
api_requests_total = Counter(
    'api_requests_total',
    'Total de requisições da API',
    ['endpoint', 'method', 'status']
)

api_latency_seconds = Histogram(
    'api_latency_seconds',
    'Latência das requisições da API',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Métricas do Modelo
model_predictions_total = Counter(
    'model_predictions_total',
    'Total de predições do modelo',
    ['model', 'status']
)

model_latency_seconds = Histogram(
    'model_latency_seconds',
    'Latência das predições do modelo',
    ['model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Métricas do Sistema
memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Uso de memória em bytes'
)

cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'Uso de CPU em percentual'
)

def track_api_request(endpoint: str, method: str, status: int, duration: float):
    api_requests_total.labels(
        endpoint=endpoint,
        method=method,
        status=status
    ).inc()
    
    api_latency_seconds.labels(
        endpoint=endpoint
    ).observe(duration)

def track_model_prediction(model: str, status: str, duration: float):
    model_predictions_total.labels(
        model=model,
        status=status
    ).inc()
    
    model_latency_seconds.labels(
        model=model
    ).observe(duration)

def update_system_metrics():
    import psutil
    
    process = psutil.Process()
    memory_usage_bytes.set(process.memory_info().rss)
    cpu_usage_percent.set(process.cpu_percent())
```

### 2. Grafana

```yaml
# monitoring/grafana/dashboards/api.yaml
apiVersion: 1
dashboard:
  title: API Metrics
  panels:
    - title: Requests per Second
      type: graph
      targets:
        - expr: rate(api_requests_total[5m])
          legendFormat: "{{endpoint}} - {{method}}"
    
    - title: API Latency
      type: graph
      targets:
        - expr: rate(api_latency_seconds_sum[5m]) / rate(api_latency_seconds_count[5m])
          legendFormat: "{{endpoint}}"
    
    - title: Model Predictions
      type: graph
      targets:
        - expr: rate(model_predictions_total[5m])
          legendFormat: "{{model}}"
    
    - title: System Resources
      type: gauge
      targets:
        - expr: memory_usage_bytes
          legendFormat: "Memory"
        - expr: cpu_usage_percent
          legendFormat: "CPU"
```

## Logs

### 1. Estrutura

```python
# api/monitoring/logging.py
import structlog
from typing import Dict, Any
import time

logger = structlog.get_logger()

def log_request(
    method: str,
    path: str,
    client: str,
    user: str,
    duration: float,
    status: int,
    error: str = None
):
    logger.info(
        "api_request",
        method=method,
        path=path,
        client=client,
        user=user,
        duration=duration,
        status=status,
        error=error
    )

def log_error(
    error: Exception,
    context: Dict[str, Any]
):
    logger.error(
        "error",
        error_type=type(error).__name__,
        error_message=str(error),
        **context
    )

def log_model_prediction(
    model: str,
    input_text: str,
    duration: float,
    status: str,
    error: str = None
):
    logger.info(
        "model_prediction",
        model=model,
        input_text=input_text,
        duration=duration,
        status=status,
        error=error
    )
```

### 2. ELK Stack

```yaml
# monitoring/elk/elasticsearch.yaml
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
spec:
  ports:
    - port: 9200
      name: http
    - port: 9300
      name: transport
  selector:
    app: elasticsearch
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
spec:
  replicas: 3
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
            - containerPort: 9300
          env:
            - name: discovery.type
              value: single-node
            - name: ES_JAVA_OPTS
              value: "-Xms512m -Xmx512m"
```

## Alertas

### 1. Prometheus Rules

```yaml
# monitoring/prometheus/rules.yaml
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: rate(api_requests_total{status=~"5.."}[5m]) / rate(api_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de erros na API"
          description: "Taxa de erros acima de 5% nos últimos 5 minutos"
      
      - alert: HighLatency
        expr: rate(api_latency_seconds_sum[5m]) / rate(api_latency_seconds_count[5m]) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alta latência na API"
          description: "Latência média acima de 1s nos últimos 5 minutos"
```

### 2. AlertManager

```yaml
# monitoring/alertmanager/config.yaml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/...'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        send_resolved: true
        title: '{{ template "slack.title" . }}'
        text: '{{ template "slack.text" . }}'
```

## Tracing

### 1. OpenTelemetry

```python
# api/monitoring/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing(app):
    trace.set_tracer_provider(TracerProvider())
    
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    FastAPIInstrumentor.instrument_app(app)

def trace_request(func):
    def wrapper(*args, **kwargs):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(func.__name__) as span:
            span.set_attribute("function", func.__name__)
            try:
                result = func(*args, **kwargs)
                span.set_status(Status(StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise
    return wrapper
```

### 2. Jaeger

```yaml
# monitoring/jaeger/jaeger.yaml
apiVersion: v1
kind: Service
metadata:
  name: jaeger
spec:
  ports:
    - port: 16686
      name: query
    - port: 6831
      name: agent
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
            - containerPort: 6831
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
- Garantir compatibilidade 