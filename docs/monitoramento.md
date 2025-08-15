# Monitoramento e Observabilidade — Prometheus

## Objetivo
Expor métricas de negócio e performance do Omni Keywords Finder para Prometheus/Grafana.

## Como Ativar
1. Importe e registre o blueprint no Flask:
```python
from infrastructure.monitoramento.metrics_exporter import metrics_bp
app.register_blueprint(metrics_bp)
```
2. O endpoint `/metrics` estará disponível para Prometheus.

## Métricas Expostas
- `keywords_processadas_total`: Total de keywords processadas
- `exportacoes_realizadas_total`: Total de exportações de keywords
- `tempo_processamento_keywords_segundos`: Tempo de processamento de keywords (histograma)
- `erros_processamento_total`: Total de erros no processamento

## Como Instrumentar
Use os decorators para instrumentar funções:
```python
from infrastructure.monitoramento.metrics_exporter import track_keywords_processadas, track_exportacao

@track_keywords_processadas
def processar_keywords(...):
    ...

@track_exportacao
def exportar_keywords(...):
    ...
```

## Exemplo de Configuração Prometheus
```yaml
scrape_configs:
  - job_name: 'omni_keywords_finder'
    static_configs:
      - targets: ['localhost:5000']
```

## Dashboard Grafana
- Importe o endpoint `/metrics` como fonte de dados Prometheus.
- Crie gráficos para keywords processadas, tempo de processamento, exportações e erros.

## Observações
- Métricas são resetadas a cada restart do processo.
- Para métricas persistentes, utilize Pushgateway ou storage externo. 