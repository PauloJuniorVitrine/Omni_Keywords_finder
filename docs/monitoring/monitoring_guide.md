# 📊 Guia de Monitoramento - Omni Keywords Finder

**Criado em**: 2025-01-27  
**Tracing ID**: COMPLETUDE_CHECKLIST_20250127_001  
**Versão**: 1.0.0  

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura de Monitoramento](#arquitetura-de-monitoramento)
3. [Métricas Coletadas](#métricas-coletadas)
4. [SLOs e SLIs](#slos-e-slis)
5. [Alertas e Notificações](#alertas-e-notificações)
6. [Dashboards](#dashboards)
7. [Detecção de Anomalias](#detecção-de-anomalias)
8. [Troubleshooting](#troubleshooting)
9. [Manutenção](#manutenção)

---

## 🎯 Visão Geral

O sistema de monitoramento do Omni Keywords Finder é baseado em uma arquitetura moderna de observabilidade, utilizando ferramentas como Prometheus, Grafana, AlertManager e scripts customizados para garantir a saúde e performance do sistema.

### Objetivos

- **Disponibilidade**: 99.9% uptime
- **Performance**: Latência p95 < 200ms
- **Confiabilidade**: Taxa de erro < 0.1%
- **Observabilidade**: Visibilidade completa do sistema

---

## 🏗️ Arquitetura de Monitoramento

### Componentes Principais

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Aplicação     │    │   Prometheus    │    │     Grafana     │
│   (Instrumented)│───▶│   (Coleta)      │───▶│   (Visualização)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │  AlertManager   │              │
         │              │   (Alertas)     │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Logs          │    │   Notificações  │    │   Dashboards    │
│   (ELK Stack)   │    │   (Slack/Email) │    │   (Custom)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Fluxo de Dados

1. **Coleta**: Prometheus coleta métricas das aplicações
2. **Armazenamento**: Dados são armazenados em time-series database
3. **Processamento**: Alertas e agregações são calculados
4. **Visualização**: Grafana exibe dashboards e gráficos
5. **Notificação**: AlertManager envia alertas via canais configurados

---

## 📈 Métricas Coletadas

### Métricas de Sistema

#### CPU
- `node_cpu_seconds_total`: Tempo total de CPU por modo
- `node_cpu_usage_percent`: Percentual de uso de CPU
- `node_cpu_load_average`: Load average do sistema

#### Memória
- `node_memory_MemTotal_bytes`: Memória total
- `node_memory_MemAvailable_bytes`: Memória disponível
- `node_memory_usage_percent`: Percentual de uso de memória

#### Disco
- `node_filesystem_size_bytes`: Tamanho do filesystem
- `node_filesystem_free_bytes`: Espaço livre
- `node_filesystem_usage_percent`: Percentual de uso

#### Rede
- `node_network_receive_bytes_total`: Bytes recebidos
- `node_network_transmit_bytes_total`: Bytes transmitidos
- `node_network_receive_errs_total`: Erros de recepção

### Métricas de Aplicação

#### HTTP
- `http_requests_total`: Total de requisições HTTP
- `http_request_duration_seconds`: Duração das requisições
- `http_requests_in_flight`: Requisições em andamento

#### Banco de Dados
- `database_connections_total`: Conexões ativas
- `database_query_duration_seconds`: Duração das queries
- `database_errors_total`: Erros de banco

#### Cache
- `cache_hits_total`: Hits do cache
- `cache_misses_total`: Misses do cache
- `cache_size_bytes`: Tamanho do cache

### Métricas de Negócio

#### Keywords
- `keywords_analyzed_total`: Keywords analisadas
- `keyword_analysis_duration_seconds`: Tempo de análise
- `keyword_accuracy_percent`: Precisão da análise

#### Usuários
- `users_active_total`: Usuários ativos
- `user_sessions_total`: Sessões ativas
- `user_satisfaction_score`: Score de satisfação

---

## 🎯 SLOs e SLIs

### Service Level Objectives (SLOs)

#### Disponibilidade
- **Objetivo**: 99.9% uptime
- **Medição**: `up` metric
- **Janela**: 30 dias
- **Orçamento de Erro**: 43.2 minutos/mês

#### Latência
- **Objetivo**: p95 < 200ms
- **Medição**: `http_request_duration_seconds`
- **Janela**: 5 minutos
- **Orçamento de Erro**: 5% das requisições

#### Taxa de Erro
- **Objetivo**: < 0.1%
- **Medição**: `rate(http_requests_total{status=~"5.."}[5m])`
- **Janela**: 5 minutos
- **Orçamento de Erro**: 0.1% das requisições

### Service Level Indicators (SLIs)

#### SLI de Disponibilidade
```promql
sum(rate(up[30d])) / count(up)
```

#### SLI de Latência
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### SLI de Taxa de Erro
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

---

## 🚨 Alertas e Notificações

### Configuração de Alertas

#### Alertas Críticos (PagerDuty)
- **Disponibilidade**: Serviço down por > 5 minutos
- **Latência**: p95 > 1 segundo por > 2 minutos
- **Erro**: Taxa de erro > 5% por > 1 minuto

#### Alertas de Alta Severidade (Slack)
- **CPU**: Uso > 80% por > 5 minutos
- **Memória**: Uso > 85% por > 5 minutos
- **Disco**: Uso > 90% por > 5 minutos

#### Alertas de Média Severidade (Email)
- **Performance**: Latência p95 > 500ms
- **Cache**: Hit rate < 70%
- **Banco**: Conexões > 80% da capacidade

### Canais de Notificação

#### PagerDuty
- **Escalação**: 5 minutos
- **Política**: Critical
- **Auto-resolve**: Sim

#### Slack
- **Canal**: #alerts
- **Formato**: Rich messages com botões
- **Integração**: Grafana + AlertManager

#### Email
- **Destinatários**: team@company.com
- **Frequência**: Diária
- **Formato**: HTML com gráficos

---

## 📊 Dashboards

### Dashboard Principal - System Overview

**Localização**: `monitoring/dashboards/system_overview.json`

#### Painéis Incluídos

1. **System Health Overview**
   - Status de todos os serviços
   - Indicadores visuais (verde/vermelho)

2. **CPU Usage**
   - Uso de CPU por instância
   - Tendências e picos

3. **Memory Usage**
   - Uso de memória por instância
   - Alertas de vazamento

4. **Disk Usage**
   - Uso de disco por filesystem
   - Previsão de espaço

5. **HTTP Request Rate**
   - Taxa de requisições por serviço
   - Padrões de tráfego

6. **HTTP Error Rate**
   - Taxa de erro por serviço
   - Análise de falhas

7. **Response Time (p95)**
   - Latência p95 por serviço
   - Performance trends

8. **Database Connections**
   - Conexões ativas por database
   - Pool de conexões

9. **Cache Hit Rate**
   - Taxa de hit do cache
   - Eficiência do cache

10. **Network Traffic**
    - Tráfego de rede por interface
    - Análise de banda

### Dashboards Específicos

#### Dashboard de Performance
- Métricas de latência detalhadas
- Análise de bottlenecks
- Comparação de versões

#### Dashboard de Negócio
- Métricas de usuários
- Análise de keywords
- ROI e conversões

#### Dashboard de Segurança
- Tentativas de login
- Atividades suspeitas
- Violações de segurança

---

## 🔍 Detecção de Anomalias

### Script de Análise

**Localização**: `scripts/anomaly_detection.py`

#### Tipos de Anomalias Detectadas

1. **Spike Anomaly**
   - Picos súbitos em métricas
   - Threshold baseado em desvio padrão
   - Detecção em tempo real

2. **Drop Anomaly**
   - Quedas súbitas em métricas
   - Indicador de falhas
   - Alertas imediatos

3. **Trend Anomaly**
   - Mudanças de tendência
   - Análise de regressão linear
   - Detecção de degradação

4. **Seasonal Anomaly**
   - Padrões sazonais
   - Comparação com histórico
   - Detecção de mudanças

5. **Outlier Anomaly**
   - Valores atípicos
   - Análise IQR
   - Detecção de outliers

#### Uso do Script

```bash
# Análise de CPU
python scripts/anomaly_detection.py \
  --metric "cpu_usage" \
  --start-time "2025-01-27 00:00:00" \
  --end-time "2025-01-27 23:59:59" \
  --format markdown

# Análise de latência
python scripts/anomaly_detection.py \
  --metric "response_time" \
  --start-time "2025-01-27 00:00:00" \
  --end-time "2025-01-27 23:59:59" \
  --output "latency_anomalies.md"
```

---

## 🔧 Troubleshooting

### Problemas Comuns

#### Prometheus Não Coleta Métricas

**Sintomas**:
- Métricas não aparecem no Grafana
- Endpoints `/metrics` não respondem

**Soluções**:
1. Verificar conectividade de rede
2. Validar configuração de targets
3. Verificar logs do Prometheus
4. Testar endpoints manualmente

#### Alertas Não Funcionam

**Sintomas**:
- Alertas não são disparados
- Notificações não chegam

**Soluções**:
1. Verificar configuração do AlertManager
2. Validar regras de alerta
3. Testar conectividade com canais
4. Verificar templates de notificação

#### Dashboards Não Carregam

**Sintomas**:
- Grafana mostra "No data"
- Painéis vazios

**Soluções**:
1. Verificar datas dos painéis
2. Validar queries PromQL
3. Verificar permissões de acesso
4. Testar conectividade com Prometheus

### Comandos Úteis

#### Verificar Status do Prometheus
```bash
curl -s http://prometheus:9090/api/v1/status/targets | jq
```

#### Verificar Métricas Disponíveis
```bash
curl -s http://prometheus:9090/api/v1/label/__name__/values | jq
```

#### Testar Query PromQL
```bash
curl -s "http://prometheus:9090/api/v1/query?query=up" | jq
```

#### Verificar Alertas Ativos
```bash
curl -s http://alertmanager:9093/api/v1/alerts | jq
```

---

## 🛠️ Manutenção

### Tarefas Diárias

1. **Revisar Alertas**
   - Verificar alertas não resolvidos
   - Analisar falsos positivos
   - Ajustar thresholds se necessário

2. **Monitorar Dashboards**
   - Verificar métricas críticas
   - Analisar tendências
   - Identificar problemas proativos

3. **Validar SLOs**
   - Calcular compliance dos SLOs
   - Analisar orçamento de erro
   - Planejar melhorias

### Tarefas Semanais

1. **Análise de Performance**
   - Executar script de anomalias
   - Analisar relatórios
   - Identificar otimizações

2. **Revisão de Configuração**
   - Validar regras de alerta
   - Verificar dashboards
   - Atualizar documentação

3. **Backup de Configuração**
   - Backup do Prometheus
   - Backup do AlertManager
   - Backup dos dashboards

### Tarefas Mensais

1. **Análise de Tendências**
   - Relatório de performance
   - Análise de capacidade
   - Planejamento de escalabilidade

2. **Otimização**
   - Ajustar thresholds
   - Otimizar queries
   - Melhorar dashboards

3. **Treinamento**
   - Atualizar documentação
   - Treinar equipe
   - Revisar processos

---

## 📚 Recursos Adicionais

### Documentação
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

### Ferramentas
- [PromQL Cheat Sheet](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [Grafana Dashboard Templates](https://grafana.com/grafana/dashboards/)
- [AlertManager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)

### Comunidade
- [Prometheus Users](https://groups.google.com/forum/#!forum/prometheus-users)
- [Grafana Community](https://community.grafana.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/prometheus)

---

## 📞 Suporte

### Contatos
- **Equipe de SRE**: sre@company.com
- **On-Call**: +55 11 99999-9999
- **Slack**: #monitoring-support

### Escalação
1. **Nível 1**: Equipe de SRE
2. **Nível 2**: Engenheiros Senior
3. **Nível 3**: Arquitetos

---

*Última atualização: 2025-01-27* 