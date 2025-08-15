# 📚 **SISTEMA DE CACHE DISTRIBUÍDO - DOCUMENTAÇÃO**

**Tracing ID**: `IMP001_CACHE_DOCS_001`  
**Data**: 2025-01-27  
**Versão**: 1.0  
**Status**: Em Implementação

---

## 🎯 **VISÃO GERAL**

O Sistema de Cache Distribuído do Omni Keywords Finder implementa uma arquitetura de cache em camadas (L1: Memory, L2: Redis) para otimizar performance e reduzir latência em até 70%.

### **📊 Benefícios Esperados**
- **Latência**: Redução de 70% (P95: 500ms → 150ms)
- **Throughput**: Aumento de 200% (1000 → 3000 req/s)
- **Cache Hit Ratio**: > 90%
- **Disponibilidade**: 99.9% uptime

---

## 🏗️ **ARQUITETURA**

### **📐 Diagrama de Camadas**

```
┌─────────────────────────────────────────────────────────────┐
│                    APLICAÇÃO                                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Cache L1      │  │   Cache L2      │  │  Database   │ │
│  │   (Memory)      │  │   (Redis)       │  │  (SQLite)   │ │
│  │                 │  │                 │  │             │ │
│  │ • TTL: 1h       │  │ • TTL: 1h       │  │ • Fallback  │ │
│  │ • Size: 100MB   │  │ • Distributed   │  │ • Persistent│ │
│  │ • Fast Access   │  │ • Shared        │  │ • Slow      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **🔄 Fluxo de Cache**

1. **Request** → Aplicação
2. **L1 Check** → Memory Cache
3. **L2 Check** → Redis Cache
4. **Database** → SQLite (fallback)
5. **Cache Update** → L1 + L2
6. **Response** → Cliente

---

## ⚙️ **CONFIGURAÇÃO**

### **📋 Configuração Básica**

```python
from infrastructure.cache.distributed_cache import CacheConfig, DistributedCache

# Configuração padrão
config = CacheConfig(
    redis_host="localhost",
    redis_port=6379,
    redis_db=0,
    redis_password=None,
    default_ttl=3600,  # 1 hora
    max_memory_size=100 * 1024 * 1024,  # 100MB
    enable_cache_warming=True,
    cache_warming_threshold=10,
    enable_metrics=True,
    fallback_to_db=True
)

# Inicialização
cache = DistributedCache(config)
```

### **🔧 Configuração Avançada**

```python
# Configuração para produção
production_config = CacheConfig(
    redis_host="redis-cluster.example.com",
    redis_port=6379,
    redis_password="secure_password",
    default_ttl=7200,  # 2 horas
    max_memory_size=500 * 1024 * 1024,  # 500MB
    enable_cache_warming=True,
    cache_warming_threshold=5,
    enable_metrics=True,
    fallback_to_db=True
)
```

---

## 🚀 **USO BÁSICO**

### **📝 Operações Principais**

```python
from infrastructure.cache.distributed_cache import get_cache

# Obtém instância global
cache = get_cache()

# Set - Define valor no cache
cache.set("user:123", {"name": "João", "email": "joao@example.com"}, 3600)

# Get - Obtém valor do cache
user_data = cache.get("user:123")

# Delete - Remove valor do cache
cache.delete("user:123")

# Clear - Limpa todo o cache
cache.clear()
```

### **🎯 Decorator de Cache**

```python
from infrastructure.cache.distributed_cache import cache_decorator

@cache_decorator("user_profile", 3600)
def get_user_profile(user_id: str):
    """Busca perfil do usuário no database"""
    # Lógica de busca no database
    return {"id": user_id, "name": "João", "email": "joao@example.com"}

# Uso automático do cache
profile = get_user_profile("123")  # Primeira vez: busca no DB
profile = get_user_profile("123")  # Segunda vez: usa cache
```

---

## 📊 **ESTRATÉGIAS DE CACHE**

### **🎯 Cache Warming Automático**

O sistema implementa cache warming baseado em padrões de acesso:

```python
# Configuração
config = CacheConfig(
    enable_cache_warming=True,
    cache_warming_threshold=10  # Warming após 10 acessos
)

# Funcionamento automático
for i in range(15):
    cache.get("frequently_accessed_key")  # Warming executado no 10º acesso
```

### **⏰ TTL Inteligente**

```python
# TTL baseado no tipo de dado
cache.set("user_session", session_data, 1800)      # 30 min
cache.set("user_profile", profile_data, 3600)      # 1 hora
cache.set("static_content", content_data, 86400)   # 24 horas
```

### **🔄 Invalidação Inteligente**

```python
# Invalidação por padrão
cache.delete("user:123")

# Invalidação em lote
cache.delete("user:*")  # Remove todos os usuários

# Invalidação por tempo
cache.set("temp_data", data, 300)  # Expira em 5 minutos
```

---

## 📈 **MÉTRICAS E MONITORAMENTO**

### **📊 Métricas Disponíveis**

```python
# Obtém estatísticas completas
stats = cache.get_stats()

print(f"L1 Cache Size: {stats['l1_cache']['size']} bytes")
print(f"L1 Hit Ratio: {stats['l1_cache']['hit_ratio']:.2%}")
print(f"L2 Connected: {stats['l2_cache']['connected']}")
print(f"Redis Memory: {stats['l2_cache']['used_memory']} bytes")
```

### **📈 Métricas Prometheus**

```yaml
# Métricas automáticas
cache_hits_total{level="l1_memory"} 1234
cache_misses_total{level="l2_redis"} 56
cache_operations_duration_seconds{operation="get"} 0.001
cache_size_bytes{level="l1_memory"} 52428800
```

### **🚨 Alertas Recomendados**

```yaml
# Alertas para monitoramento
- alert: CacheHitRatioLow
  expr: rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Cache hit ratio baixo"

- alert: RedisConnectionDown
  expr: cache_size_bytes{level="l2_redis"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Redis não conectado"
```

---

## 🔧 **PADRÕES DE USO**

### **🎯 Padrão Repository com Cache**

```python
class UserRepository:
    def __init__(self):
        self.cache = get_cache()
    
    def get_user(self, user_id: str):
        # Tenta cache primeiro
        cache_key = f"user:{user_id}"
        user_data = self.cache.get(cache_key)
        
        if user_data:
            return user_data
        
        # Busca no database
        user_data = self._fetch_from_database(user_id)
        
        # Cacheia resultado
        if user_data:
            self.cache.set(cache_key, user_data, 3600)
        
        return user_data
    
    def update_user(self, user_id: str, user_data: dict):
        # Atualiza database
        self._update_database(user_id, user_data)
        
        # Invalida cache
        cache_key = f"user:{user_id}"
        self.cache.delete(cache_key)
```

### **🎯 Padrão Service com Cache**

```python
class UserService:
    def __init__(self):
        self.cache = get_cache()
        self.repository = UserRepository()
    
    @cache_decorator("user_profile", 3600)
    def get_user_profile(self, user_id: str):
        return self.repository.get_user(user_id)
    
    def update_user_profile(self, user_id: str, profile_data: dict):
        # Atualiza
        self.repository.update_user(user_id, profile_data)
        
        # Invalida cache manualmente se necessário
        self.cache.delete(f"user_profile:{user_id}")
```

---

## 🛡️ **SEGURANÇA E RESILIÊNCIA**

### **🔐 Segurança**

```python
# Configuração segura para produção
secure_config = CacheConfig(
    redis_host="redis.example.com",
    redis_password="strong_password_here",
    redis_ssl=True,
    redis_ssl_cert_reqs="required"
)
```

### **🔄 Fallback Robusto**

```python
# O sistema automaticamente faz fallback para database
try:
    data = cache.get("key")
    if data is None:
        # Fallback para database
        data = database.fetch("key")
        cache.set("key", data, 3600)
except Exception as e:
    # Log error e usa database diretamente
    logger.error(f"Cache error: {e}")
    data = database.fetch("key")
```

### **⚡ Circuit Breaker**

```python
# Implementação de circuit breaker para Redis
class CacheCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e
```

---

## 📋 **CHECKLIST DE IMPLEMENTAÇÃO**

### **✅ Configuração Básica**
- [ ] Redis instalado e configurado
- [ ] Configuração de cache definida
- [ ] Instância global inicializada
- [ ] Testes unitários criados

### **✅ Padrões de Uso**
- [ ] Repository pattern implementado
- [ ] Service pattern implementado
- [ ] Decorators aplicados
- [ ] Invalidação configurada

### **✅ Monitoramento**
- [ ] Métricas configuradas
- [ ] Alertas definidos
- [ ] Dashboards criados
- [ ] Logs estruturados

### **✅ Segurança**
- [ ] Autenticação Redis configurada
- [ ] SSL/TLS habilitado
- [ ] Fallback implementado
- [ ] Circuit breaker configurado

---

## 🚀 **PRÓXIMOS PASSOS**

### **📅 Roadmap de Melhorias**

1. **Fase 1** (Mês 1): Implementação básica ✅
2. **Fase 2** (Mês 2): Cache warming avançado
3. **Fase 3** (Mês 3): Cache distribuído multi-região
4. **Fase 4** (Mês 4): Cache inteligente com ML

### **🎯 Métricas de Sucesso**

- [ ] **Latência P95**: < 200ms
- [ ] **Cache Hit Ratio**: > 90%
- [ ] **Throughput**: +200%
- [ ] **Uptime**: 99.9%

---

## 📞 **SUPORTE**

### **🔧 Troubleshooting**

**Problema**: Cache não está funcionando
```bash
# Verifica conexão Redis
redis-cli ping

# Verifica logs
tail -f logs/cache.log

# Verifica métricas
curl http://localhost:9090/metrics | grep cache
```

**Problema**: Performance baixa
```python
# Verifica estatísticas
stats = cache.get_stats()
print(f"Hit ratio: {stats['l1_cache']['hit_ratio']:.2%}")
print(f"Memory usage: {stats['l1_cache']['size']} bytes")
```

### **📚 Recursos Adicionais**

- [Documentação Redis](https://redis.io/documentation)
- [Padrões de Cache](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Métricas de Performance](https://prometheus.io/docs/practices/naming/)

---

**📅 Última Atualização**: 2025-01-27  
**👤 Responsável**: AI Assistant  
**📋 Status**: 🚀 **IMPLEMENTAÇÃO EM ANDAMENTO** 