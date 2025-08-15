# Cache Distribuído - Implementação Completa

## 📋 Visão Geral

O sistema de cache distribuído foi implementado seguindo as melhores práticas da indústria, com foco em performance, confiabilidade e escalabilidade.

## 🏗️ Arquitetura

### **Componentes Principais**

1. **AsyncCache** - Classe principal do cache distribuído
2. **LocalCache** - Cache local como fallback
3. **CacheConfig** - Configuração centralizada
4. **Decorators** - Cache automático para funções

### **Fluxo de Funcionamento**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Aplicação     │───▶│   AsyncCache    │───▶│     Redis       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LocalCache    │
                       │   (Fallback)    │
                       └─────────────────┘
```

## 🔧 Configuração

### **Variáveis de Ambiente**

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false

# Cache
CACHE_TTL_DEFAULT=3600
CACHE_TTL_KEYWORDS=86400
CACHE_TTL_METRICS=43200
CACHE_TTL_TRENDS=21600
CACHE_FALLBACK_ENABLED=true
CACHE_FALLBACK_TTL=300
CACHE_MAX_MEMORY_MB=100
CACHE_COMPRESSION_THRESHOLD=1024
```

### **TTLs Específicos**

- **Keywords**: 24 horas (86400s)
- **Métricas**: 12 horas (43200s)
- **Tendências**: 6 horas (21600s)
- **Padrão**: 1 hora (3600s)

## 📊 Métricas e Monitoramento

### **Métricas Coletadas**

```python
{
    'hits': 1000,              # Cache hits
    'misses': 100,             # Cache misses
    'sets': 500,               # Operações de set
    'deletes': 50,             # Operações de delete
    'errors': 5,               # Erros
    'hit_rate_percent': 90.91, # Taxa de hit
    'total_requests': 1100,    # Total de requisições
    'redis_available': True,   # Status do Redis
    'fallback_enabled': True,  # Fallback habilitado
    'namespace': 'keywords'    # Namespace
}
```

### **Health Check**

```python
{
    'redis_connected': True,
    'local_cache_available': True,
    'overall_healthy': True
}
```

## 🚀 Uso Prático

### **Uso Básico**

```python
from shared.cache import get_cache

# Obter instância do cache
cache = await get_cache("keywords")

# Operações básicas
await cache.set("key", "value", 3600)
value = await cache.get("key")
deleted = await cache.delete("key")
```

### **Decorators Especializados**

```python
from infrastructure.coleta.utils.cache import cached_keywords, cached_metrics

@cached_keywords()
async def coletar_keywords(termo: str):
    # Função com cache automático de 24h
    pass

@cached_metrics()
async def calcular_metricas(dominio: str):
    # Função com cache automático de 12h
    pass
```

### **Cache Especializado para Coletores**

```python
from infrastructure.coleta.utils.cache import CacheDistribuido

# Inicializar cache especializado
cache = CacheDistribuido(namespace="amazon", ttl_padrao=86400)

# Usar cache
await cache.set("keyword_data", data)
result = await cache.get("keyword_data")

# Verificar métricas
metrics = cache.get_metrics()
health = await cache.health_check()
```

## 🔒 Segurança e Confiabilidade

### **Fallback Automático**

- Se Redis falhar, automaticamente usa cache local
- Cache local com TTL reduzido (5 minutos)
- Logs detalhados de todas as operações

### **Tratamento de Erros**

- Timeout configurável (5s)
- Retry automático em timeouts
- Health check periódico (30s)

### **Serialização Segura**

- JSON para tipos básicos (mais eficiente)
- Pickle para objetos complexos (fallback)
- Validação de dados

## 📈 Performance

### **Benchmarks Esperados**

- **Latência**: < 1ms para cache hit
- **Throughput**: 10.000+ ops/segundo
- **Hit Rate**: > 80% em produção
- **Memory**: < 100MB para cache local

### **Otimizações Implementadas**

1. **Namespace Isolation** - Evita conflitos
2. **TTL Dinâmico** - Baseado no tipo de dado
3. **Compressão** - Para dados grandes
4. **Connection Pooling** - Reutilização de conexões
5. **Lazy Loading** - Inicialização sob demanda

## 🧪 Testes

### **Cobertura de Testes**

- ✅ Configuração
- ✅ Cache Local
- ✅ Cache Distribuído
- ✅ Fallback
- ✅ Métricas
- ✅ Health Check
- ✅ Decorators
- ✅ Integração

### **Executar Testes**

```bash
# Testes unitários
pytest tests/unit/test_cache_distributed.py -v

# Testes com cobertura
pytest tests/unit/test_cache_distributed.py --cov=shared.cache --cov-report=html
```

## 🔄 Migração

### **Compatibilidade**

- ✅ API compatível com implementação anterior
- ✅ Migração transparente
- ✅ Rollback possível
- ✅ Configuração via ambiente

### **Passos de Migração**

1. **Instalar dependências**
   ```bash
   pip install redis aioredis redis-py-cluster
   ```

2. **Configurar variáveis de ambiente**
   ```bash
   cp env.example .env
   # Editar .env com configurações do Redis
   ```

3. **Testar implementação**
   ```bash
   pytest tests/unit/test_cache_distributed.py
   ```

4. **Monitorar métricas**
   - Verificar hit rate
   - Monitorar erros
   - Acompanhar performance

## 🚨 Troubleshooting

### **Problemas Comuns**

#### **Redis Connection Failed**
```bash
# Verificar se Redis está rodando
redis-cli ping

# Verificar configurações
echo $REDIS_HOST
echo $REDIS_PORT
```

#### **Cache Miss Alto**
- Verificar TTLs
- Analisar padrões de acesso
- Ajustar estratégia de cache

#### **Performance Degradada**
- Monitorar métricas do Redis
- Verificar uso de memória
- Analisar logs de erro

### **Logs Importantes**

```python
# Conexão Redis
"event": "redis_connected"
"event": "redis_connection_failed"

# Operações
"event": "cache_hit"
"event": "cache_miss"
"event": "cache_set"

# Erros
"event": "redis_get_error"
"event": "local_cache_error"
```

## 📚 Referências

- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Redis Best Practices](https://redis.io/topics/best-practices)
- [Cache Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

## 🎯 Próximos Passos

1. **Monitoramento Avançado**
   - Dashboards Grafana
   - Alertas automáticos
   - Métricas customizadas

2. **Otimizações**
   - Cache warming
   - Prefetch inteligente
   - Compressão avançada

3. **Escalabilidade**
   - Redis Cluster
   - Cache distribuído geograficamente
   - Load balancing 