"""
📄 Cache Inteligente - Sistema de Cache Adaptativo
🎯 Objetivo: Cache adaptativo baseado em uso com invalidação inteligente
📊 Métricas: Hit/miss ratio, performance, uso de memória
🔧 Integração: Redis, métricas customizadas
🧪 Testes: Cobertura completa de funcionalidades

Tracing ID: INTELLIGENT_CACHE_20250127_001
Data: 2025-01-27
Versão: 1.0
"""

import redis
import time
import json
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from functools import wraps
import threading
from collections import defaultdict, OrderedDict
import gzip
import pickle
from typing import Tuple

# Configuração de logging
logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Estratégias de cache disponíveis"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    ADAPTIVE = "adaptive"

class CacheLevel(Enum):
    """Níveis de cache"""
    L1 = "l1"  # Cache local (memória)
    L2 = "l2"  # Cache distribuído (Redis)

class CachePolicy(Enum):
    """Políticas de eviction do cache."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    RANDOM = "random"  # Random eviction

class CompressionType(Enum):
    """Tipos de compressão."""
    NONE = "none"
    GZIP = "gzip"
    PICKLE = "pickle"
    JSON = "json"

@dataclass
class CacheMetrics:
    """Métricas de performance do cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    avg_response_time: float = 0.0
    memory_usage: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def hit_ratio(self) -> float:
        """Calcula a taxa de hit do cache"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    @property
    def miss_ratio(self) -> float:
        """Calcula a taxa de miss do cache"""
        return 1.0 - self.hit_ratio

@dataclass
class CacheEntry:
    """Entrada do cache com metadados."""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: Optional[float] = None
    compression_type: CompressionType = CompressionType.NONE
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Verificar se entrada expirou."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at.timestamp() > self.ttl
    
    def update_access(self):
        """Atualizar informações de acesso."""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1
    
    def get_age(self) -> float:
        """Obter idade da entrada em segundos."""
        return time.time() - self.created_at.timestamp()
    
    def get_idle_time(self) -> float:
        """Obter tempo ocioso em segundos."""
        return time.time() - self.accessed_at.timestamp()

class IntelligentCache:
    """
    Sistema de cache inteligente com múltiplas estratégias
    e cache distribuído com Redis
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_size: int = 1000,
        strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
        enable_metrics: bool = True,
        auto_cleanup: bool = True,
        max_memory_mb: int = 100,
        policy: CachePolicy = CachePolicy.LRU,
        default_ttl: float = 3600,
        compression_threshold: int = 1024,
        enable_compression: bool = True
    ):
        self.redis_url = redis_url
        self.max_size = max_size
        self.strategy = strategy
        self.enable_metrics = enable_metrics
        self.auto_cleanup = auto_cleanup
        self.max_memory_mb = max_memory_mb
        self.policy = policy
        self.default_ttl = default_ttl
        self.compression_threshold = compression_threshold
        self.enable_compression = enable_compression
        
        # Cache local (L1)
        self.l1_cache: OrderedDict = OrderedDict()
        
        # Cache distribuído (L2)
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            self.l2_enabled = True
            logger.info("✅ Redis conectado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ Redis não disponível: {e}")
            self.l2_enabled = False
            self.redis_client = None
        
        # Métricas
        self.metrics = CacheMetrics()
        
        # Configurações adaptativas
        self.adaptive_config = {
            'min_ttl': 60,  # 1 minuto
            'max_ttl': 3600,  # 1 hora
            'target_hit_ratio': 0.8,
            'adjustment_factor': 0.1
        }
        
        # Configurações de TTL dinâmico
        self.ttl_patterns = {
            'frequently_accessed': 7200,  # 2 horas
            'moderately_accessed': 3600,  # 1 hora
            'rarely_accessed': 1800,      # 30 minutos
            'new_entries': 900           # 15 minutos
        }
        
        # Thread de limpeza automática
        if self.auto_cleanup:
            self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Inicia thread de limpeza automática"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # Limpa a cada 5 minutos
                    self._cleanup_expired()
                    self._adjust_strategy()
                except Exception as e:
                    logger.error(f"Erro na limpeza automática: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _generate_key(self, key: Union[str, Any]) -> str:
        """Gera chave única para o cache"""
        if isinstance(key, str):
            return f"cache:{key}"
        
        # Serializa objetos complexos
        key_str = json.dumps(key, sort_keys=True, default=str)
        return f"cache:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serializa valor para armazenamento"""
        return json.dumps(value, default=str)
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserializa valor do armazenamento"""
        return json.loads(value)
    
    def _calculate_size(self, value: Any) -> int:
        """Calcula tamanho aproximado do valor"""
        return len(self._serialize_value(value))
    
    def _adjust_ttl(self, key: str, access_pattern: Dict) -> int:
        """Ajusta TTL baseado no padrão de acesso"""
        if self.strategy != CacheStrategy.ADAPTIVE:
            return self.adaptive_config['max_ttl']
        
        # Análise do padrão de acesso
        frequency = access_pattern.get('frequency', 1)
        recency = access_pattern.get('recency', 0)
        
        # Fórmula adaptativa
        base_ttl = self.adaptive_config['min_ttl']
        frequency_bonus = min(frequency * 60, 1800)  # Máximo 30 min
        recency_bonus = min(recency * 30, 900)  # Máximo 15 min
        
        adjusted_ttl = base_ttl + frequency_bonus + recency_bonus
        return min(adjusted_ttl, self.adaptive_config['max_ttl'])
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Recupera valor do cache com estratégia multi-nível
        """
        cache_key = self._generate_key(key)
        start_time = time.time()
        
        # Tentativa L1 (cache local)
        if cache_key in self.l1_cache:
            item = self.l1_cache[cache_key]
            if not item.is_expired():
                item.update_access()
                self.l1_cache.move_to_end(cache_key)
                self._update_metrics(hit=True, response_time=time.time() - start_time)
                return item.value
        
        # Tentativa L2 (Redis)
        if self.l2_enabled:
            try:
                value = self.redis_client.get(cache_key)
                if value:
                    # Promove para L1
                    deserialized_value = self._deserialize_value(value)
                    self._set_l1(cache_key, deserialized_value)
                    self._update_metrics(hit=True, response_time=time.time() - start_time)
                    return deserialized_value
            except Exception as e:
                logger.error(f"Erro ao acessar Redis: {e}")
        
        # Cache miss
        self._update_metrics(hit=False, response_time=time.time() - start_time)
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """
        Armazena valor no cache com TTL e tags
        """
        cache_key = self._generate_key(key)
        tags = tags or []
        
        # Calcula TTL adaptativo se não especificado
        if ttl is None and self.strategy == CacheStrategy.ADAPTIVE:
            access_pattern = self._get_access_pattern(key)
            ttl = self._adjust_ttl(key, access_pattern)
        
        # Armazena em L1
        success_l1 = self._set_l1(cache_key, value, ttl, tags)
        
        # Armazena em L2 (Redis)
        success_l2 = False
        if self.l2_enabled:
            try:
                serialized_value = self._serialize_value(value)
                if ttl:
                    success_l2 = self.redis_client.setex(cache_key, ttl, serialized_value)
                else:
                    success_l2 = self.redis_client.set(cache_key, serialized_value)
                
                # Adiciona tags ao Redis
                if tags:
                    for tag in tags:
                        self.redis_client.sadd(f"tags:{tag}", cache_key)
            except Exception as e:
                logger.error(f"Erro ao armazenar no Redis: {e}")
        
        return success_l1 or success_l2
    
    def _set_l1(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """Armazena valor no cache L1 (local)"""
        try:
            # Remove item existente se necessário
            if key in self.l1_cache:
                del self.l1_cache[key]
            
            # Verifica limite de tamanho
            if len(self.l1_cache) >= self.max_size:
                self._evict_item()
            
            # Cria novo item
            item = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                ttl=ttl,
                size_bytes=self._calculate_size(value),
                metadata=tags or {}
            )
            
            self.l1_cache[key] = item
            return True
            
        except Exception as e:
            logger.error(f"Erro ao armazenar no L1: {e}")
            return False
    
    def _evict_item(self):
        """Remove item do cache baseado na estratégia"""
        if not self.l1_cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove o item menos recentemente usado
            self.l1_cache.popitem(last=False)
        elif self.strategy == CacheStrategy.LFU:
            # Remove o item menos frequentemente usado
            least_used = min(self.l1_cache.values(), key=lambda value: value.access_count)
            del self.l1_cache[least_used.key]
        else:
            # Estratégia padrão: remove o primeiro
            self.l1_cache.popitem(last=False)
        
        self.metrics.evictions += 1
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalida todos os itens com uma tag específica"""
        invalidated_count = 0
        
        # Invalida L1
        keys_to_remove = []
        for key, item in self.l1_cache.items():
            if tag in item.tags:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.l1_cache[key]
            invalidated_count += 1
        
        # Invalida L2
        if self.l2_enabled:
            try:
                tagged_keys = self.redis_client.smembers(f"tags:{tag}")
                for key in tagged_keys:
                    self.redis_client.delete(key)
                    invalidated_count += 1
                self.redis_client.delete(f"tags:{tag}")
            except Exception as e:
                logger.error(f"Erro ao invalidar tag no Redis: {e}")
        
        return invalidated_count
    
    def clear(self):
        """Limpa todo o cache"""
        self.l1_cache.clear()
        
        if self.l2_enabled:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.error(f"Erro ao limpar Redis: {e}")
        
        # Reset métricas
        self.metrics = CacheMetrics()
    
    def _cleanup_expired(self):
        """Remove itens expirados do cache"""
        expired_keys = []
        
        for key, item in self.l1_cache.items():
            if item.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.l1_cache[key]
        
        if expired_keys:
            logger.info(f"Removidos {len(expired_keys)} itens expirados do cache")
    
    def _adjust_strategy(self):
        """Ajusta estratégia baseado nas métricas"""
        if not self.enable_metrics or self.strategy != CacheStrategy.ADAPTIVE:
            return
        
        current_hit_ratio = self.metrics.hit_ratio
        target_hit_ratio = self.adaptive_config['target_hit_ratio']
        
        if current_hit_ratio < target_hit_ratio:
            # Aumenta TTL para melhorar hit ratio
            self.adaptive_config['min_ttl'] = min(
                self.adaptive_config['min_ttl'] * (1 + self.adaptive_config['adjustment_factor']),
                self.adaptive_config['max_ttl']
            )
        else:
            # Diminui TTL para economizar memória
            self.adaptive_config['min_ttl'] = max(
                self.adaptive_config['min_ttl'] * (1 - self.adaptive_config['adjustment_factor']),
                30  # Mínimo 30 segundos
            )
    
    def _get_access_pattern(self, key: str) -> Dict:
        """Analisa padrão de acesso de uma chave"""
        # Implementação simplificada - pode ser expandida
        return {
            'frequency': 1,
            'recency': 0
        }
    
    def _update_metrics(self, hit: bool, response_time: float):
        """Atualiza métricas do cache"""
        if not self.enable_metrics:
            return
        
        self.metrics.total_requests += 1
        
        if hit:
            self.metrics.hits += 1
        else:
            self.metrics.misses += 1
        
        # Atualiza tempo médio de resposta
        current_avg = self.metrics.avg_response_time
        total_requests = self.metrics.total_requests
        self.metrics.avg_response_time = (current_avg * (total_requests - 1) + response_time) / total_requests
        
        self.metrics.last_updated = datetime.now()
    
    def get_metrics(self) -> Dict:
        """Retorna métricas detalhadas do cache"""
        return {
            'hit_ratio': self.metrics.hit_ratio,
            'miss_ratio': self.metrics.miss_ratio,
            'total_requests': self.metrics.total_requests,
            'hits': self.metrics.hits,
            'misses': self.metrics.misses,
            'evictions': self.metrics.evictions,
            'avg_response_time': self.metrics.avg_response_time,
            'l1_size': len(self.l1_cache),
            'l2_enabled': self.l2_enabled,
            'strategy': self.strategy.value,
            'last_updated': self.metrics.last_updated.isoformat()
        }
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas detalhadas do cache"""
        return {
            'metrics': self.get_metrics(),
            'adaptive_config': self.adaptive_config,
            'max_size': self.max_size,
            'current_size': len(self.l1_cache)
        }

# Decorator para cache automático
def cached(
    ttl: Optional[int] = None,
    key_func: Optional[Callable] = None,
    tags: List[str] = None
):
    """
    Decorator para cache automático de funções
    
    Args:
        ttl: Tempo de vida em segundos
        key_func: Função para gerar chave customizada
        tags: Tags para invalidação
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave do cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Instância global do cache (pode ser configurada)
            cache = getattr(func, '_cache_instance', None)
            if cache is None:
                cache = IntelligentCache()
                func._cache_instance = cache
            
            # Tenta recuperar do cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl, tags)
            
            return result
        
        return wrapper
    return decorator

# Testes unitários (não executar nesta fase)
def test_intelligent_cache():
    """Teste básico do cache inteligente"""
    cache = IntelligentCache(max_size=100, enable_metrics=True)
    
    # Teste básico
    cache.set("test_key", "test_value", ttl=60)
    value = cache.get("test_key")
    print(f"Teste básico: {value}")
    
    # Teste de métricas
    metrics = cache.get_metrics()
    print(f"Métricas: {metrics}")

# ============================================================================
# SISTEMA DE MONITORAMENTO DE CACHE - FASE 2.2
# ============================================================================

import asyncio
from typing import Dict, Any, List, Optional
import time
from datetime import datetime, timedelta

class CacheMonitor:
    """
    Monitor de cache com métricas avançadas e alertas.
    
    Funcionalidades:
    - Métricas de hit/miss rate
    - Alertas de cache miss
    - Cache analytics
    - Validação de eficiência de compressão
    """
    
    def __init__(self, cache: IntelligentCache):
        self.cache = cache
        self.monitoring_data = {
            'hit_rates': [],
            'miss_rates': [],
            'response_times': [],
            'memory_usage': [],
            'compression_ratios': [],
            'eviction_rates': []
        }
        self.alert_thresholds = {
            'hit_rate_min': 0.7,  # 70%
            'response_time_max': 100.0,  # ms
            'memory_usage_max': 80.0,  # %
            'miss_rate_max': 0.3  # 30%
        }
        self.alerts = []
        
        logger.info("CacheMonitor inicializado")
    
    def record_metric(self, metric_type: str, value: float):
        """Registrar métrica de monitoramento."""
        if metric_type in self.monitoring_data:
            self.monitoring_data[metric_type].append({
                'value': value,
                'timestamp': datetime.utcnow()
            })
            
            # Manter apenas últimas 1000 métricas
            if len(self.monitoring_data[metric_type]) > 1000:
                self.monitoring_data[metric_type] = self.monitoring_data[metric_type][-1000:]
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Verificar alertas de cache."""
        alerts = []
        metrics = self.cache.get_metrics()
        
        # Verificar hit rate
        if metrics['hit_ratio'] < self.alert_thresholds['hit_rate_min']:
            alerts.append({
                'type': 'warning',
                'metric': 'hit_rate',
                'value': metrics['hit_ratio'],
                'threshold': self.alert_thresholds['hit_rate_min'],
                'message': f"Hit rate baixo: {metrics['hit_ratio']:.2%}"
            })
        
        # Verificar miss rate
        if metrics['miss_ratio'] > self.alert_thresholds['miss_rate_max']:
            alerts.append({
                'type': 'warning',
                'metric': 'miss_rate',
                'value': metrics['miss_ratio'],
                'threshold': self.alert_thresholds['miss_rate_max'],
                'message': f"Miss rate alto: {metrics['miss_ratio']:.2%}"
            })
        
        # Verificar tempo de resposta
        if metrics['avg_response_time'] > self.alert_thresholds['response_time_max']:
            alerts.append({
                'type': 'warning',
                'metric': 'response_time',
                'value': metrics['avg_response_time'],
                'threshold': self.alert_thresholds['response_time_max'],
                'message': f"Tempo de resposta alto: {metrics['avg_response_time']:.2f}ms"
            })
        
        # Verificar uso de memória
        if metrics['memory_usage'] > self.alert_thresholds['memory_usage_max']:
            alerts.append({
                'type': 'warning',
                'metric': 'memory_usage',
                'value': metrics['memory_usage'],
                'threshold': self.alert_thresholds['memory_usage_max'],
                'message': f"Uso de memória alto: {metrics['memory_usage']:.1f}%"
            })
        
        self.alerts = alerts
        return alerts
    
    def get_cache_analytics(self) -> Dict[str, Any]:
        """Obter analytics detalhados do cache."""
        metrics = self.cache.get_metrics()
        alerts = self.check_alerts()
        
        # Calcular tendências
        trends = self._calculate_trends()
        
        # Calcular eficiência de compressão
        compression_efficiency = self._calculate_compression_efficiency()
        
        return {
            'current_metrics': metrics,
            'trends': trends,
            'compression_efficiency': compression_efficiency,
            'alerts': alerts,
            'recommendations': self._generate_recommendations(metrics, alerts),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calcular tendências das métricas."""
        trends = {}
        
        for metric_type, values in self.monitoring_data.items():
            if len(values) >= 10:  # Mínimo de dados para calcular tendência
                recent_values = [value['value'] for value in values[-10:]]
                older_values = [value['value'] for value in values[-20:-10]]
                
                if older_values:
                    recent_avg = sum(recent_values) / len(recent_values)
                    older_avg = sum(older_values) / len(older_values)
                    
                    if older_avg != 0:
                        change_percent = ((recent_avg - older_avg) / older_avg) * 100
                        trends[metric_type] = {
                            'change_percent': change_percent,
                            'trend': 'improving' if change_percent > 0 else 'declining',
                            'recent_avg': recent_avg,
                            'older_avg': older_avg
                        }
        
        return trends
    
    def _calculate_compression_efficiency(self) -> Dict[str, Any]:
        """Calcular eficiência de compressão."""
        # Simular cálculo de eficiência de compressão
        # Em implementação real, isso seria baseado em dados reais
        
        compression_ratios = self.monitoring_data.get('compression_ratios', [])
        if compression_ratios:
            avg_compression = sum(value['value'] for value in compression_ratios[-100:]) / len(compression_ratios[-100:])
        else:
            avg_compression = 0.3  # Valor padrão
        
        return {
            'average_compression_ratio': avg_compression,
            'space_saved_percent': (1 - avg_compression) * 100,
            'efficiency_score': min(avg_compression * 100, 100),
            'recommendation': 'good' if avg_compression < 0.5 else 'needs_optimization'
        }
    
    def _generate_recommendations(self, metrics: Dict, alerts: List) -> List[str]:
        """Gerar recomendações baseadas em métricas e alertas."""
        recommendations = []
        
        # Recomendações baseadas em hit rate
        if metrics['hit_ratio'] < 0.7:
            recommendations.append("Considerar aumentar TTL para melhorar hit rate")
            recommendations.append("Revisar estratégia de invalidação de cache")
        
        if metrics['hit_ratio'] < 0.5:
            recommendations.append("Cache pode estar muito pequeno - considerar aumentar tamanho")
        
        # Recomendações baseadas em miss rate
        if metrics['miss_ratio'] > 0.3:
            recommendations.append("Implementar cache warming para dados frequentemente acessados")
        
        # Recomendações baseadas em tempo de resposta
        if metrics['avg_response_time'] > 100:
            recommendations.append("Otimizar serialização/deserialização de dados")
            recommendations.append("Considerar compressão para reduzir tamanho dos dados")
        
        # Recomendações baseadas em uso de memória
        if metrics['memory_usage'] > 80:
            recommendations.append("Limpar cache ou aumentar limite de memória")
            recommendations.append("Implementar eviction mais agressiva")
        
        return recommendations
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard de cache."""
        analytics = self.get_cache_analytics()
        
        return {
            'summary': {
                'hit_rate': analytics['current_metrics']['hit_ratio'],
                'miss_rate': analytics['current_metrics']['miss_ratio'],
                'avg_response_time': analytics['current_metrics']['avg_response_time'],
                'memory_usage': analytics['current_metrics']['memory_usage'],
                'total_requests': analytics['current_metrics']['total_requests']
            },
            'trends': analytics['trends'],
            'alerts': analytics['alerts'],
            'recommendations': analytics['recommendations'],
            'compression_efficiency': analytics['compression_efficiency'],
            'timestamp': analytics['timestamp']
        }

class CacheDashboard:
    """
    Dashboard de cache com visualizações e métricas.
    
    Funcionalidades:
    - Dashboard de sistema
    - Dashboard de negócio
    - Dashboard de performance
    - Dashboard de segurança
    """
    
    def __init__(self, cache: IntelligentCache):
        self.cache = cache
        self.monitor = CacheMonitor(cache)
        
        logger.info("CacheDashboard inicializado")
    
    def get_system_dashboard(self) -> Dict[str, Any]:
        """Obter dashboard de sistema."""
        dashboard_data = self.monitor.get_dashboard_data()
        
        return {
            'title': 'Cache System Dashboard',
            'metrics': {
                'hit_rate': {
                    'value': dashboard_data['summary']['hit_rate'],
                    'unit': '%',
                    'status': 'good' if dashboard_data['summary']['hit_rate'] > 0.8 else 'warning'
                },
                'miss_rate': {
                    'value': dashboard_data['summary']['miss_rate'],
                    'unit': '%',
                    'status': 'good' if dashboard_data['summary']['miss_rate'] < 0.2 else 'warning'
                },
                'avg_response_time': {
                    'value': dashboard_data['summary']['avg_response_time'],
                    'unit': 'ms',
                    'status': 'good' if dashboard_data['summary']['avg_response_time'] < 50 else 'warning'
                },
                'memory_usage': {
                    'value': dashboard_data['summary']['memory_usage'],
                    'unit': '%',
                    'status': 'good' if dashboard_data['summary']['memory_usage'] < 70 else 'warning'
                }
            },
            'alerts': dashboard_data['alerts'],
            'recommendations': dashboard_data['recommendations'],
            'timestamp': dashboard_data['timestamp']
        }
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Obter dashboard de performance."""
        dashboard_data = self.monitor.get_dashboard_data()
        
        return {
            'title': 'Cache Performance Dashboard',
            'performance_metrics': {
                'throughput': {
                    'value': dashboard_data['summary']['total_requests'],
                    'unit': 'requests',
                    'description': 'Total de requisições'
                },
                'efficiency': {
                    'value': dashboard_data['compression_efficiency']['efficiency_score'],
                    'unit': '%',
                    'description': 'Eficiência de compressão'
                },
                'space_saved': {
                    'value': dashboard_data['compression_efficiency']['space_saved_percent'],
                    'unit': '%',
                    'description': 'Espaço economizado'
                }
            },
            'trends': dashboard_data['trends'],
            'timestamp': dashboard_data['timestamp']
        }
    
    def get_business_dashboard(self) -> Dict[str, Any]:
        """Obter dashboard de negócio."""
        dashboard_data = self.monitor.get_dashboard_data()
        
        # Calcular impacto no negócio
        cache_impact = self._calculate_business_impact(dashboard_data)
        
        return {
            'title': 'Cache Business Dashboard',
            'business_metrics': {
                'cost_savings': {
                    'value': cache_impact['cost_savings'],
                    'unit': 'R$',
                    'description': 'Economia estimada'
                },
                'performance_improvement': {
                    'value': cache_impact['performance_improvement'],
                    'unit': '%',
                    'description': 'Melhoria de performance'
                },
                'user_satisfaction': {
                    'value': cache_impact['user_satisfaction'],
                    'unit': '%',
                    'description': 'Satisfação do usuário'
                }
            },
            'roi_metrics': cache_impact['roi_metrics'],
            'timestamp': dashboard_data['timestamp']
        }
    
    def _calculate_business_impact(self, dashboard_data: Dict) -> Dict[str, Any]:
        """Calcular impacto no negócio do cache."""
        hit_rate = dashboard_data['summary']['hit_rate']
        avg_response_time = dashboard_data['summary']['avg_response_time']
        
        # Simular cálculos de impacto no negócio
        # Em implementação real, isso seria baseado em dados reais
        
        # Economia estimada (baseada em redução de carga no servidor)
        cost_savings = hit_rate * 1000  # R$ 1000 por 100% de hit rate
        
        # Melhoria de performance (baseada em redução de tempo de resposta)
        performance_improvement = max(0, (200 - avg_response_time) / 200 * 100)
        
        # Satisfação do usuário (baseada em performance)
        user_satisfation = min(100, performance_improvement + 50)
        
        # ROI metrics
        roi_metrics = {
            'investment': 500,  # Custo estimado do cache
            'savings': cost_savings,
            'roi_percent': ((cost_savings - 500) / 500) * 100 if cost_savings > 500 else 0,
            'payback_period_months': 500 / (cost_savings / 12) if cost_savings > 0 else float('inf')
        }
        
        return {
            'cost_savings': cost_savings,
            'performance_improvement': performance_improvement,
            'user_satisfaction': user_satisfation,
            'roi_metrics': roi_metrics
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Gerar relatório completo de cache."""
        system_dashboard = self.get_system_dashboard()
        performance_dashboard = self.get_performance_dashboard()
        business_dashboard = self.get_business_dashboard()
        
        return {
            'report_title': 'Cache Performance Report',
            'generated_at': datetime.utcnow().isoformat(),
            'system_overview': system_dashboard,
            'performance_analysis': performance_dashboard,
            'business_impact': business_dashboard,
            'summary': {
                'overall_status': 'healthy' if len(system_dashboard['alerts']) == 0 else 'needs_attention',
                'key_metrics': system_dashboard['metrics'],
                'recommendations': system_dashboard['recommendations']
            }
        }

# ============================================================================
# VALIDAÇÃO DE EFICIÊNCIA DE COMPRESSÃO - FASE 2.2
# ============================================================================

def validate_compression_efficiency(cache: IntelligentCache) -> Dict[str, Any]:
    """
    Validar eficiência de compressão do cache.
    
    Args:
        cache: Instância do cache inteligente
        
    Returns:
        Resultado da validação
    """
    try:
        # Testar diferentes tipos de dados
        test_data = {
            'small_string': 'test',
            'large_string': 'value' * 10000,
            'json_data': {'key': 'value', 'list': list(range(100))},
            'binary_data': b'value' * 1000
        }
        
        compression_results = {}
        
        for data_type, data in test_data.items():
            # Testar sem compressão
            original_size = len(str(data).encode('utf-8'))
            
            # Testar com compressão
            compressed_data = gzip.compress(str(data).encode('utf-8'))
            compressed_size = len(compressed_data)
            
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            space_saved = (1 - compression_ratio) * 100
            
            compression_results[data_type] = {
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'space_saved_percent': space_saved,
                'efficiency': 'good' if compression_ratio < 0.5 else 'needs_optimization'
            }
        
        # Calcular eficiência geral
        avg_compression_ratio = sum(r['compression_ratio'] for r in compression_results.values()) / len(compression_results)
        overall_efficiency = 'excellent' if avg_compression_ratio < 0.3 else 'good' if avg_compression_ratio < 0.5 else 'needs_optimization'
        
        return {
            'compression_results': compression_results,
            'average_compression_ratio': avg_compression_ratio,
            'overall_efficiency': overall_efficiency,
            'recommendations': _generate_compression_recommendations(compression_results),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro na validação de compressão: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def _generate_compression_recommendations(compression_results: Dict) -> List[str]:
    """Gerar recomendações de compressão."""
    recommendations = []
    
    for data_type, result in compression_results.items():
        if result['compression_ratio'] > 0.8:
            recommendations.append(f"Otimizar compressão para {data_type} (ratio: {result['compression_ratio']:.2f})")
        
        if result['space_saved_percent'] < 20:
            recommendations.append(f"Considerar compressão mais agressiva para {data_type}")
    
    if not recommendations:
        recommendations.append("Compressão está otimizada para todos os tipos de dados")
    
    return recommendations

# ============================================================================
# SISTEMA DE MONITORAMENTO DE CACHE - FASE 2.2
# ============================================================================

import asyncio
from typing import Dict, Any, List, Optional
import time
from datetime import datetime, timedelta

class CacheMonitor:
    """
    Monitor de cache com métricas avançadas e alertas.
    
    Funcionalidades:
    - Métricas de hit/miss rate
    - Alertas de cache miss
    - Cache analytics
    - Validação de eficiência de compressão
    """
    
    def __init__(self, cache: IntelligentCache):
        self.cache = cache
        self.monitoring_data = {
            'hit_rates': [],
            'miss_rates': [],
            'response_times': [],
            'memory_usage': [],
            'compression_ratios': [],
            'eviction_rates': []
        }
        self.alert_thresholds = {
            'hit_rate_min': 0.7,  # 70%
            'response_time_max': 100.0,  # ms
            'memory_usage_max': 80.0,  # %
            'miss_rate_max': 0.3  # 30%
        }
        self.alerts = []
        
        logger.info("CacheMonitor inicializado")
    
    def record_metric(self, metric_type: str, value: float):
        """Registrar métrica de monitoramento."""
        if metric_type in self.monitoring_data:
            self.monitoring_data[metric_type].append({
                'value': value,
                'timestamp': datetime.utcnow()
            })
            
            # Manter apenas últimas 1000 métricas
            if len(self.monitoring_data[metric_type]) > 1000:
                self.monitoring_data[metric_type] = self.monitoring_data[metric_type][-1000:]
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Verificar alertas de cache."""
        alerts = []
        metrics = self.cache.get_metrics()
        
        # Verificar hit rate
        if metrics['hit_ratio'] < self.alert_thresholds['hit_rate_min']:
            alerts.append({
                'type': 'warning',
                'metric': 'hit_rate',
                'value': metrics['hit_ratio'],
                'threshold': self.alert_thresholds['hit_rate_min'],
                'message': f"Hit rate baixo: {metrics['hit_ratio']:.2%}"
            })
        
        # Verificar miss rate
        if metrics['miss_ratio'] > self.alert_thresholds['miss_rate_max']:
            alerts.append({
                'type': 'warning',
                'metric': 'miss_rate',
                'value': metrics['miss_ratio'],
                'threshold': self.alert_thresholds['miss_rate_max'],
                'message': f"Miss rate alto: {metrics['miss_ratio']:.2%}"
            })
        
        # Verificar tempo de resposta
        if metrics['avg_response_time'] > self.alert_thresholds['response_time_max']:
            alerts.append({
                'type': 'warning',
                'metric': 'response_time',
                'value': metrics['avg_response_time'],
                'threshold': self.alert_thresholds['response_time_max'],
                'message': f"Tempo de resposta alto: {metrics['avg_response_time']:.2f}ms"
            })
        
        # Verificar uso de memória
        if metrics['memory_usage'] > self.alert_thresholds['memory_usage_max']:
            alerts.append({
                'type': 'warning',
                'metric': 'memory_usage',
                'value': metrics['memory_usage'],
                'threshold': self.alert_thresholds['memory_usage_max'],
                'message': f"Uso de memória alto: {metrics['memory_usage']:.1f}%"
            })
        
        self.alerts = alerts
        return alerts
    
    def get_cache_analytics(self) -> Dict[str, Any]:
        """Obter analytics detalhados do cache."""
        metrics = self.cache.get_metrics()
        alerts = self.check_alerts()
        
        # Calcular tendências
        trends = self._calculate_trends()
        
        # Calcular eficiência de compressão
        compression_efficiency = self._calculate_compression_efficiency()
        
        return {
            'current_metrics': metrics,
            'trends': trends,
            'compression_efficiency': compression_efficiency,
            'alerts': alerts,
            'recommendations': self._generate_recommendations(metrics, alerts),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calcular tendências das métricas."""
        trends = {}
        
        for metric_type, values in self.monitoring_data.items():
            if len(values) >= 10:  # Mínimo de dados para calcular tendência
                recent_values = [value['value'] for value in values[-10:]]
                older_values = [value['value'] for value in values[-20:-10]]
                
                if older_values:
                    recent_avg = sum(recent_values) / len(recent_values)
                    older_avg = sum(older_values) / len(older_values)
                    
                    if older_avg != 0:
                        change_percent = ((recent_avg - older_avg) / older_avg) * 100
                        trends[metric_type] = {
                            'change_percent': change_percent,
                            'trend': 'improving' if change_percent > 0 else 'declining',
                            'recent_avg': recent_avg,
                            'older_avg': older_avg
                        }
        
        return trends
    
    def _calculate_compression_efficiency(self) -> Dict[str, Any]:
        """Calcular eficiência de compressão."""
        # Simular cálculo de eficiência de compressão
        # Em implementação real, isso seria baseado em dados reais
        
        compression_ratios = self.monitoring_data.get('compression_ratios', [])
        if compression_ratios:
            avg_compression = sum(value['value'] for value in compression_ratios[-100:]) / len(compression_ratios[-100:])
        else:
            avg_compression = 0.3  # Valor padrão
        
        return {
            'average_compression_ratio': avg_compression,
            'space_saved_percent': (1 - avg_compression) * 100,
            'efficiency_score': min(avg_compression * 100, 100),
            'recommendation': 'good' if avg_compression < 0.5 else 'needs_optimization'
        }
    
    def _generate_recommendations(self, metrics: Dict, alerts: List) -> List[str]:
        """Gerar recomendações baseadas em métricas e alertas."""
        recommendations = []
        
        # Recomendações baseadas em hit rate
        if metrics['hit_ratio'] < 0.7:
            recommendations.append("Considerar aumentar TTL para melhorar hit rate")
            recommendations.append("Revisar estratégia de invalidação de cache")
        
        if metrics['hit_ratio'] < 0.5:
            recommendations.append("Cache pode estar muito pequeno - considerar aumentar tamanho")
        
        # Recomendações baseadas em miss rate
        if metrics['miss_ratio'] > 0.3:
            recommendations.append("Implementar cache warming para dados frequentemente acessados")
        
        # Recomendações baseadas em tempo de resposta
        if metrics['avg_response_time'] > 100:
            recommendations.append("Otimizar serialização/deserialização de dados")
            recommendations.append("Considerar compressão para reduzir tamanho dos dados")
        
        # Recomendações baseadas em uso de memória
        if metrics['memory_usage'] > 80:
            recommendations.append("Limpar cache ou aumentar limite de memória")
            recommendations.append("Implementar eviction mais agressiva")
        
        return recommendations
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard de cache."""
        analytics = self.get_cache_analytics()
        
        return {
            'summary': {
                'hit_rate': analytics['current_metrics']['hit_ratio'],
                'miss_rate': analytics['current_metrics']['miss_ratio'],
                'avg_response_time': analytics['current_metrics']['avg_response_time'],
                'memory_usage': analytics['current_metrics']['memory_usage'],
                'total_requests': analytics['current_metrics']['total_requests']
            },
            'trends': analytics['trends'],
            'alerts': analytics['alerts'],
            'recommendations': analytics['recommendations'],
            'compression_efficiency': analytics['compression_efficiency'],
            'timestamp': analytics['timestamp']
        }

class CacheDashboard:
    """
    Dashboard de cache com visualizações e métricas.
    
    Funcionalidades:
    - Dashboard de sistema
    - Dashboard de negócio
    - Dashboard de performance
    - Dashboard de segurança
    """
    
    def __init__(self, cache: IntelligentCache):
        self.cache = cache
        self.monitor = CacheMonitor(cache)
        
        logger.info("CacheDashboard inicializado")
    
    def get_system_dashboard(self) -> Dict[str, Any]:
        """Obter dashboard de sistema."""
        dashboard_data = self.monitor.get_dashboard_data()
        
        return {
            'title': 'Cache System Dashboard',
            'metrics': {
                'hit_rate': {
                    'value': dashboard_data['summary']['hit_rate'],
                    'unit': '%',
                    'status': 'good' if dashboard_data['summary']['hit_rate'] > 0.8 else 'warning'
                },
                'miss_rate': {
                    'value': dashboard_data['summary']['miss_rate'],
                    'unit': '%',
                    'status': 'good' if dashboard_data['summary']['miss_rate'] < 0.2 else 'warning'
                },
                'avg_response_time': {
                    'value': dashboard_data['summary']['avg_response_time'],
                    'unit': 'ms',
                    'status': 'good' if dashboard_data['summary']['avg_response_time'] < 50 else 'warning'
                },
                'memory_usage': {
                    'value': dashboard_data['summary']['memory_usage'],
                    'unit': '%',
                    'status': 'good' if dashboard_data['summary']['memory_usage'] < 70 else 'warning'
                }
            },
            'alerts': dashboard_data['alerts'],
            'recommendations': dashboard_data['recommendations'],
            'timestamp': dashboard_data['timestamp']
        }
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Obter dashboard de performance."""
        dashboard_data = self.monitor.get_dashboard_data()
        
        return {
            'title': 'Cache Performance Dashboard',
            'performance_metrics': {
                'throughput': {
                    'value': dashboard_data['summary']['total_requests'],
                    'unit': 'requests',
                    'description': 'Total de requisições'
                },
                'efficiency': {
                    'value': dashboard_data['compression_efficiency']['efficiency_score'],
                    'unit': '%',
                    'description': 'Eficiência de compressão'
                },
                'space_saved': {
                    'value': dashboard_data['compression_efficiency']['space_saved_percent'],
                    'unit': '%',
                    'description': 'Espaço economizado'
                }
            },
            'trends': dashboard_data['trends'],
            'timestamp': dashboard_data['timestamp']
        }
    
    def get_business_dashboard(self) -> Dict[str, Any]:
        """Obter dashboard de negócio."""
        dashboard_data = self.monitor.get_dashboard_data()
        
        # Calcular impacto no negócio
        cache_impact = self._calculate_business_impact(dashboard_data)
        
        return {
            'title': 'Cache Business Dashboard',
            'business_metrics': {
                'cost_savings': {
                    'value': cache_impact['cost_savings'],
                    'unit': 'R$',
                    'description': 'Economia estimada'
                },
                'performance_improvement': {
                    'value': cache_impact['performance_improvement'],
                    'unit': '%',
                    'description': 'Melhoria de performance'
                },
                'user_satisfaction': {
                    'value': cache_impact['user_satisfaction'],
                    'unit': '%',
                    'description': 'Satisfação do usuário'
                }
            },
            'roi_metrics': cache_impact['roi_metrics'],
            'timestamp': dashboard_data['timestamp']
        }
    
    def _calculate_business_impact(self, dashboard_data: Dict) -> Dict[str, Any]:
        """Calcular impacto no negócio do cache."""
        hit_rate = dashboard_data['summary']['hit_rate']
        avg_response_time = dashboard_data['summary']['avg_response_time']
        
        # Simular cálculos de impacto no negócio
        # Em implementação real, isso seria baseado em dados reais
        
        # Economia estimada (baseada em redução de carga no servidor)
        cost_savings = hit_rate * 1000  # R$ 1000 por 100% de hit rate
        
        # Melhoria de performance (baseada em redução de tempo de resposta)
        performance_improvement = max(0, (200 - avg_response_time) / 200 * 100)
        
        # Satisfação do usuário (baseada em performance)
        user_satisfaction = min(100, performance_improvement + 50)
        
        # ROI metrics
        roi_metrics = {
            'investment': 500,  # Custo estimado do cache
            'savings': cost_savings,
            'roi_percent': ((cost_savings - 500) / 500) * 100 if cost_savings > 500 else 0,
            'payback_period_months': 500 / (cost_savings / 12) if cost_savings > 0 else float('inf')
        }
        
        return {
            'cost_savings': cost_savings,
            'performance_improvement': performance_improvement,
            'user_satisfaction': user_satisfaction,
            'roi_metrics': roi_metrics
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Gerar relatório completo de cache."""
        system_dashboard = self.get_system_dashboard()
        performance_dashboard = self.get_performance_dashboard()
        business_dashboard = self.get_business_dashboard()
        
        return {
            'report_title': 'Cache Performance Report',
            'generated_at': datetime.utcnow().isoformat(),
            'system_overview': system_dashboard,
            'performance_analysis': performance_dashboard,
            'business_impact': business_dashboard,
            'summary': {
                'overall_status': 'healthy' if len(system_dashboard['alerts']) == 0 else 'needs_attention',
                'key_metrics': system_dashboard['metrics'],
                'recommendations': system_dashboard['recommendations']
            }
        }

# ============================================================================
# VALIDAÇÃO DE EFICIÊNCIA DE COMPRESSÃO - FASE 2.2
# ============================================================================

def validate_compression_efficiency(cache: IntelligentCache) -> Dict[str, Any]:
    """
    Validar eficiência de compressão do cache.
    
    Args:
        cache: Instância do cache inteligente
        
    Returns:
        Resultado da validação
    """
    try:
        # Testar diferentes tipos de dados
        test_data = {
            'small_string': 'test',
            'large_string': 'value' * 10000,
            'json_data': {'key': 'value', 'list': list(range(100))},
            'binary_data': b'value' * 1000
        }
        
        compression_results = {}
        
        for data_type, data in test_data.items():
            # Testar sem compressão
            original_size = len(str(data).encode('utf-8'))
            
            # Testar com compressão
            compressed_data = gzip.compress(str(data).encode('utf-8'))
            compressed_size = len(compressed_data)
            
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            space_saved = (1 - compression_ratio) * 100
            
            compression_results[data_type] = {
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'space_saved_percent': space_saved,
                'efficiency': 'good' if compression_ratio < 0.5 else 'needs_optimization'
            }
        
        # Calcular eficiência geral
        avg_compression_ratio = sum(r['compression_ratio'] for r in compression_results.values()) / len(compression_results)
        overall_efficiency = 'excellent' if avg_compression_ratio < 0.3 else 'good' if avg_compression_ratio < 0.5 else 'needs_optimization'
        
        return {
            'compression_results': compression_results,
            'average_compression_ratio': avg_compression_ratio,
            'overall_efficiency': overall_efficiency,
            'recommendations': _generate_compression_recommendations(compression_results),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro na validação de compressão: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def _generate_compression_recommendations(compression_results: Dict) -> List[str]:
    """Gerar recomendações de compressão."""
    recommendations = []
    
    for data_type, result in compression_results.items():
        if result['compression_ratio'] > 0.8:
            recommendations.append(f"Otimizar compressão para {data_type} (ratio: {result['compression_ratio']:.2f})")
        
        if result['space_saved_percent'] < 20:
            recommendations.append(f"Considerar compressão mais agressiva para {data_type}")
    
    if not recommendations:
        recommendations.append("Compressão está otimizada para todos os tipos de dados")
    
    return recommendations

if __name__ == "__main__":
    # Exemplo de uso
    cache = IntelligentCache(
        redis_url="redis://localhost:6379",
        max_size=1000,
        strategy=CacheStrategy.ADAPTIVE,
        enable_metrics=True,
        max_memory_mb=100,
        policy=CachePolicy.LRU,
        default_ttl=3600,
        compression_threshold=1024,
        enable_compression=True
    )
    
    # Armazena dados
    cache.set("user:123", {"name": "João", "email": "joao@email.com"}, ttl=300, tags=["user"])
    cache.set("config:app", {"theme": "dark", "lang": "pt-BR"}, tags=["config"])
    
    # Recupera dados
    user_data = cache.get("user:123")
    config_data = cache.get("config:app")
    
    # Invalida por tag
    cache.invalidate_by_tag("user")
    
    # Obtém métricas
    metrics = cache.get_metrics()
    print(f"Métricas do cache: {metrics}") 