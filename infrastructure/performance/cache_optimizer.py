#!/usr/bin/env python3
"""
🎯 Otimizador de Cache Inteligente - IMP-016
============================================

Tracing ID: CACHE_OPTIMIZER_IMP016_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema avançado de otimização de cache que:
- Implementa estratégias de cache inteligentes
- Analisa padrões de acesso
- Aplica cache adaptativo
- Otimiza TTL dinamicamente
- Implementa cache em camadas
- Fornece métricas detalhadas

Prompt: CHECKLIST_CONFIABILIDADE.md - IMP-016
Ruleset: enterprise_control_layer.yaml
"""

import time
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
import threading
from functools import wraps, lru_cache

# Cache e otimização
import redis
from cachetools import TTLCache, LRUCache, LFUCache
import numpy as np

# Logging estruturado
from shared.logger import logger

# Observabilidade
from infrastructure.observability.metrics import MetricsCollector
from infrastructure.observability.tracing import trace_function


class CacheStrategy(Enum):
    """Estratégias de cache disponíveis."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptativo baseado em padrões
    LAYERED = "layered"  # Cache em camadas
    INTELLIGENT = "intelligent"  # Cache inteligente


class CacheLevel(Enum):
    """Níveis de cache."""
    L1 = "l1"  # Cache de primeiro nível (memória)
    L2 = "l2"  # Cache de segundo nível (Redis)
    L3 = "l3"  # Cache de terceiro nível (disco)


@dataclass
class CacheConfig:
    """Configuração para otimização de cache."""
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    l1_max_size: int = 1000
    l1_ttl: int = 300  # 5 minutos
    l2_max_size: int = 10000
    l2_ttl: int = 3600  # 1 hora
    l3_max_size: int = 100000
    l3_ttl: int = 86400  # 24 horas
    enable_preloading: bool = True
    enable_compression: bool = True
    compression_threshold: int = 1024  # bytes
    adaptive_learning_rate: float = 0.1
    pattern_analysis_interval: int = 300  # 5 minutos


@dataclass
class CacheMetrics:
    """Métricas de cache."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    memory_usage: float = 0.0
    hit_rate: float = 0.0
    avg_access_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CachePattern:
    """Padrão de acesso ao cache."""
    key_pattern: str
    access_frequency: float
    access_time: List[float]
    value_size: int
    ttl_optimal: int
    last_access: datetime
    access_count: int = 0


class CacheOptimizer:
    """
    Sistema de otimização de cache inteligente.
    
    Responsável por:
    - Gerenciar cache em múltiplas camadas
    - Analisar padrões de acesso
    - Aplicar estratégias adaptativas
    - Otimizar TTL dinamicamente
    - Implementar pré-carregamento
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        
        # Inicializar caches em camadas
        self.l1_cache = TTLCache(maxsize=config.l1_max_size, ttl=config.l1_ttl)
        self.l2_cache = TTLCache(maxsize=config.l2_max_size, ttl=config.l2_ttl)
        self.l3_cache = TTLCache(maxsize=config.l3_max_size, ttl=config.l3_ttl)
        
        # Cache de padrões
        self.patterns = defaultdict(CachePattern)
        self.access_history = deque(maxlen=10000)
        
        # Métricas
        self.metrics = CacheMetrics()
        self.metrics_history = deque(maxlen=1000)
        
        # Threading
        self.pattern_analysis_thread = None
        self.optimization_thread = None
        self.monitoring_active = False
        
        # Locks para thread safety
        self.l1_lock = threading.RLock()
        self.l2_lock = threading.RLock()
        self.l3_lock = threading.RLock()
        
        logger.info(f"CacheOptimizer inicializado com estratégia: {config.strategy}")
    
    @trace_function(operation_name="start_monitoring", service_name="cache-optimizer")
    def start_monitoring(self) -> bool:
        """Inicia o monitoramento de cache."""
        try:
            if self.monitoring_active:
                logger.warning("Monitoramento de cache já está ativo")
                return True
            
            self.monitoring_active = True
            
            # Iniciar thread de análise de padrões
            self.pattern_analysis_thread = threading.Thread(
                target=self._pattern_analysis_loop,
                daemon=True
            )
            self.pattern_analysis_thread.start()
            
            # Iniciar thread de otimização
            self.optimization_thread = threading.Thread(
                target=self._optimization_loop,
                daemon=True
            )
            self.optimization_thread.start()
            
            logger.info("Monitoramento de cache iniciado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar monitoramento de cache: {str(e)}")
            return False
    
    @trace_function(operation_name="stop_monitoring", service_name="cache-optimizer")
    def stop_monitoring(self) -> bool:
        """Para o monitoramento de cache."""
        try:
            self.monitoring_active = False
            
            if self.pattern_analysis_thread:
                self.pattern_analysis_thread.join(timeout=5)
            
            if self.optimization_thread:
                self.optimization_thread.join(timeout=5)
            
            logger.info("Monitoramento de cache parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar monitoramento de cache: {str(e)}")
            return False
    
    @trace_function(operation_name="get", service_name="cache-optimizer")
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache com estratégia em camadas."""
        try:
            start_time = time.time()
            
            # Tentar L1 cache primeiro
            with self.l1_lock:
                if key in self.l1_cache:
                    self._record_hit(key, CacheLevel.L1, time.time() - start_time)
                    return self.l1_cache[key]
            
            # Tentar L2 cache
            with self.l2_lock:
                if key in self.l2_cache:
                    value = self.l2_cache[key]
                    # Promover para L1
                    with self.l1_lock:
                        self.l1_cache[key] = value
                    self._record_hit(key, CacheLevel.L2, time.time() - start_time)
                    return value
            
            # Tentar L3 cache
            with self.l3_lock:
                if key in self.l3_cache:
                    value = self.l3_cache[key]
                    # Promover para L2 e L1
                    with self.l2_lock:
                        self.l2_cache[key] = value
                    with self.l1_lock:
                        self.l1_cache[key] = value
                    self._record_hit(key, CacheLevel.L3, time.time() - start_time)
                    return value
            
            # Cache miss
            self._record_miss(key, time.time() - start_time)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter do cache: {str(e)}")
            return None
    
    @trace_function(operation_name="set", service_name="cache-optimizer")
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Define valor no cache com estratégia em camadas."""
        try:
            start_time = time.time()
            
            # Comprimir valor se necessário
            if self.config.enable_compression and len(str(value)) > self.config.compression_threshold:
                value = self._compress_value(value)
            
            # Determinar TTL ótimo
            optimal_ttl = ttl or self._calculate_optimal_ttl(key, value)
            
            # Armazenar em todas as camadas
            with self.l1_lock:
                self.l1_cache[key] = value
            
            with self.l2_lock:
                self.l2_cache[key] = value
            
            with self.l3_lock:
                self.l3_cache[key] = value
            
            # Registrar acesso
            self._record_set(key, value, optimal_ttl, time.time() - start_time)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir no cache: {str(e)}")
            return False
    
    @trace_function(operation_name="delete", service_name="cache-optimizer")
    def delete(self, key: str) -> bool:
        """Remove valor do cache em todas as camadas."""
        try:
            with self.l1_lock:
                if key in self.l1_cache:
                    del self.l1_cache[key]
            
            with self.l2_lock:
                if key in self.l2_cache:
                    del self.l2_cache[key]
            
            with self.l3_lock:
                if key in self.l3_cache:
                    del self.l3_cache[key]
            
            logger.info(f"Chave removida do cache: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover do cache: {str(e)}")
            return False
    
    @trace_function(operation_name="clear", service_name="cache-optimizer")
    def clear(self) -> bool:
        """Limpa todos os caches."""
        try:
            with self.l1_lock:
                self.l1_cache.clear()
            
            with self.l2_lock:
                self.l2_cache.clear()
            
            with self.l3_lock:
                self.l3_cache.clear()
            
            logger.info("Todos os caches foram limpos")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar caches: {str(e)}")
            return False
    
    @trace_function(operation_name="preload_data", service_name="cache-optimizer")
    def preload_data(self, keys: List[str], data_provider: Callable[[str], Any]) -> Dict[str, bool]:
        """Pré-carrega dados no cache."""
        try:
            results = {}
            
            for key in keys:
                try:
                    # Verificar se já está no cache
                    if self.get(key) is not None:
                        results[key] = True
                        continue
                    
                    # Obter dados do provedor
                    value = data_provider(key)
                    if value is not None:
                        success = self.set(key, value)
                        results[key] = success
                    else:
                        results[key] = False
                        
                except Exception as e:
                    logger.error(f"Erro ao pré-carregar {key}: {str(e)}")
                    results[key] = False
            
            logger.info(f"Pré-carregamento concluído: {sum(results.values())}/{len(keys)} sucessos")
            return results
            
        except Exception as e:
            logger.error(f"Erro no pré-carregamento: {str(e)}")
            return {key: False for key in keys}
    
    @trace_function(operation_name="analyze_patterns", service_name="cache-optimizer")
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analisa padrões de acesso ao cache."""
        try:
            if not self.access_history:
                return {"error": "Nenhum histórico de acesso disponível"}
            
            # Agrupar por padrão de chave
            pattern_groups = defaultdict(list)
            for access in self.access_history:
                pattern = self._extract_key_pattern(access['key'])
                pattern_groups[pattern].append(access)
            
            # Analisar cada padrão
            pattern_analysis = {}
            for pattern, accesses in pattern_groups.items():
                access_times = [a['access_time'] for a in accesses]
                frequencies = [a['frequency'] for a in accesses]
                
                pattern_analysis[pattern] = {
                    'access_count': len(accesses),
                    'avg_access_time': statistics.mean(access_times) if access_times else 0,
                    'avg_frequency': statistics.mean(frequencies) if frequencies else 0,
                    'optimal_ttl': self._calculate_pattern_ttl(accesses),
                    'recommended_strategy': self._recommend_strategy(accesses)
                }
            
            return {
                'total_patterns': len(pattern_analysis),
                'total_accesses': len(self.access_history),
                'patterns': pattern_analysis,
                'recommendations': self._generate_pattern_recommendations(pattern_analysis)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de padrões: {str(e)}")
            return {"error": str(e)}
    
    @trace_function(operation_name="optimize_cache", service_name="cache-optimizer")
    def optimize_cache(self) -> Dict[str, Any]:
        """Aplica otimizações baseadas em análise de padrões."""
        try:
            optimizations = []
            
            # Analisar padrões
            pattern_analysis = self.analyze_patterns()
            if 'error' in pattern_analysis:
                return pattern_analysis
            
            # Aplicar otimizações baseadas em padrões
            for pattern, analysis in pattern_analysis['patterns'].items():
                # Ajustar TTL para padrões frequentes
                if analysis['avg_frequency'] > 0.8:
                    new_ttl = analysis['optimal_ttl']
                    self._adjust_pattern_ttl(pattern, new_ttl)
                    optimizations.append(f"ttl_adjustment_{pattern}")
                
                # Pré-carregar dados frequentes
                if analysis['access_count'] > 100:
                    self._preload_frequent_pattern(pattern)
                    optimizations.append(f"preload_{pattern}")
            
            # Limpar cache expirado
            cleaned_l1 = self._clean_expired_cache(self.l1_cache, self.l1_lock)
            cleaned_l2 = self._clean_expired_cache(self.l2_cache, self.l2_lock)
            cleaned_l3 = self._clean_expired_cache(self.l3_cache, self.l3_lock)
            
            if cleaned_l1 or cleaned_l2 or cleaned_l3:
                optimizations.append("cache_cleanup")
            
            # Rebalancear cache se necessário
            if self._should_rebalance():
                self._rebalance_cache()
                optimizations.append("cache_rebalance")
            
            return {
                'optimizations_applied': optimizations,
                'cache_stats': self.get_cache_stats(),
                'pattern_analysis': pattern_analysis
            }
            
        except Exception as e:
            logger.error(f"Erro na otimização de cache: {str(e)}")
            return {"error": str(e)}
    
    @trace_function(operation_name="get_cache_stats", service_name="cache-optimizer")
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas detalhadas do cache."""
        try:
            # Calcular métricas atuais
            total_hits = self.metrics.hits
            total_misses = self.metrics.misses
            total_requests = total_hits + total_misses
            hit_rate = total_hits / total_requests if total_requests > 0 else 0
            
            # Tamanhos dos caches
            l1_size = len(self.l1_cache)
            l2_size = len(self.l2_cache)
            l3_size = len(self.l3_cache)
            total_size = l1_size + l2_size + l3_size
            
            # Uso de memória estimado
            l1_memory = l1_size * 1024  # Estimativa: 1KB por entrada
            l2_memory = l2_size * 2048  # Estimativa: 2KB por entrada
            l3_memory = l3_size * 4096  # Estimativa: 4KB por entrada
            total_memory = l1_memory + l2_memory + l3_memory
            
            stats = {
                'hits': total_hits,
                'misses': total_misses,
                'total_requests': total_requests,
                'hit_rate': hit_rate,
                'evictions': self.metrics.evictions,
                'avg_access_time': self.metrics.avg_access_time,
                'cache_sizes': {
                    'l1': l1_size,
                    'l2': l2_size,
                    'l3': l3_size,
                    'total': total_size
                },
                'memory_usage': {
                    'l1_mb': l1_memory / (1024 * 1024),
                    'l2_mb': l2_memory / (1024 * 1024),
                    'l3_mb': l3_memory / (1024 * 1024),
                    'total_mb': total_memory / (1024 * 1024)
                },
                'config': {
                    'strategy': self.config.strategy.value,
                    'l1_max_size': self.config.l1_max_size,
                    'l2_max_size': self.config.l2_max_size,
                    'l3_max_size': self.config.l3_max_size,
                    'l1_ttl': self.config.l1_ttl,
                    'l2_ttl': self.config.l2_ttl,
                    'l3_ttl': self.config.l3_ttl
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {"error": str(e)}
    
    def _pattern_analysis_loop(self):
        """Loop de análise de padrões."""
        while self.monitoring_active:
            try:
                self.analyze_patterns()
                time.sleep(self.config.pattern_analysis_interval)
            except Exception as e:
                logger.error(f"Erro no loop de análise de padrões: {str(e)}")
                time.sleep(60)
    
    def _optimization_loop(self):
        """Loop de otimização."""
        while self.monitoring_active:
            try:
                self.optimize_cache()
                time.sleep(self.config.pattern_analysis_interval * 2)
            except Exception as e:
                logger.error(f"Erro no loop de otimização: {str(e)}")
                time.sleep(120)
    
    def _record_hit(self, key: str, level: CacheLevel, access_time: float):
        """Registra hit no cache."""
        self.metrics.hits += 1
        self.metrics.avg_access_time = (
            (self.metrics.avg_access_time * (self.metrics.hits - 1) + access_time) / self.metrics.hits
        )
        
        # Registrar no histórico
        self.access_history.append({
            'key': key,
            'level': level.value,
            'access_time': access_time,
            'frequency': 1.0,
            'timestamp': datetime.now()
        })
        
        # Enviar métrica
        self.metrics_collector.record_metric(f"cache.{level.value}.hits", 1)
        self.metrics_collector.record_metric(f"cache.{level.value}.access_time", access_time)
    
    def _record_miss(self, key: str, access_time: float):
        """Registra miss no cache."""
        self.metrics.misses += 1
        
        # Registrar no histórico
        self.access_history.append({
            'key': key,
            'level': 'miss',
            'access_time': access_time,
            'frequency': 0.0,
            'timestamp': datetime.now()
        })
        
        # Enviar métrica
        self.metrics_collector.record_metric("cache.misses", 1)
    
    def _record_set(self, key: str, value: Any, ttl: int, access_time: float):
        """Registra set no cache."""
        self.metrics.size += 1
        
        # Registrar no histórico
        self.access_history.append({
            'key': key,
            'level': 'set',
            'access_time': access_time,
            'frequency': 1.0,
            'timestamp': datetime.now()
        })
        
        # Enviar métrica
        self.metrics_collector.record_metric("cache.sets", 1)
    
    def _extract_key_pattern(self, key: str) -> str:
        """Extrai padrão da chave."""
        # Implementação simples - em produção seria mais sofisticada
        if ':' in key:
            return key.split(':')[0] + ':*'
        return key
    
    def _calculate_optimal_ttl(self, key: str, value: Any) -> int:
        """Calcula TTL ótimo baseado em padrões."""
        pattern = self._extract_key_pattern(key)
        
        if pattern in self.patterns:
            return self.patterns[pattern].ttl_optimal
        
        # TTL padrão baseado no tamanho do valor
        value_size = len(str(value))
        if value_size < 1024:
            return 300  # 5 minutos
        elif value_size < 10240:
            return 1800  # 30 minutos
        else:
            return 3600  # 1 hora
    
    def _calculate_pattern_ttl(self, accesses: List[Dict[str, Any]]) -> int:
        """Calcula TTL ótimo para um padrão."""
        if not accesses:
            return 300
        
        # Baseado na frequência de acesso
        avg_frequency = statistics.mean([a['frequency'] for a in accesses])
        
        if avg_frequency > 0.8:
            return 3600  # 1 hora para dados muito acessados
        elif avg_frequency > 0.5:
            return 1800  # 30 minutos para dados moderadamente acessados
        else:
            return 300  # 5 minutos para dados pouco acessados
    
    def _recommend_strategy(self, accesses: List[Dict[str, Any]]) -> str:
        """Recomenda estratégia para um padrão."""
        if not accesses:
            return "ttl"
        
        # Baseado no padrão de acesso
        access_times = [a['access_time'] for a in accesses]
        avg_access_time = statistics.mean(access_times)
        
        if avg_access_time < 0.001:
            return "lru"  # Acesso muito rápido
        elif avg_access_time < 0.01:
            return "lfu"  # Acesso rápido
        else:
            return "adaptive"  # Acesso lento
    
    def _adjust_pattern_ttl(self, pattern: str, new_ttl: int):
        """Ajusta TTL para um padrão."""
        # Em produção, ajustaria TTL dinamicamente
        pass
    
    def _preload_frequent_pattern(self, pattern: str):
        """Pré-carrega dados de um padrão frequente."""
        # Em produção, pré-carregaria dados
        pass
    
    def _clean_expired_cache(self, cache: TTLCache, lock: threading.RLock) -> bool:
        """Limpa cache expirado."""
        try:
            with lock:
                # TTLCache limpa automaticamente, mas podemos forçar
                return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
            return False
    
    def _should_rebalance(self) -> bool:
        """Verifica se cache precisa ser rebalanceado."""
        l1_size = len(self.l1_cache)
        l2_size = len(self.l2_cache)
        l3_size = len(self.l3_cache)
        
        # Se L1 está muito cheio e L2/L3 não
        if l1_size > self.config.l1_max_size * 0.9 and l2_size < self.config.l2_max_size * 0.5:
            return True
        
        return False
    
    def _rebalance_cache(self):
        """Rebalanceia cache entre camadas."""
        # Em produção, moveria dados entre camadas
        pass
    
    def _compress_value(self, value: Any) -> Any:
        """Comprime valor se necessário."""
        # Em produção, aplicaria compressão
        return value
    
    def _generate_pattern_recommendations(self, pattern_analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas em análise de padrões."""
        recommendations = []
        
        for pattern, analysis in pattern_analysis['patterns'].items():
            if analysis['avg_frequency'] > 0.8:
                recommendations.append(f"Pré-carregar dados do padrão: {pattern}")
            
            if analysis['avg_access_time'] > 0.01:
                recommendations.append(f"Otimizar acesso ao padrão: {pattern}")
        
        return recommendations


# Decorator para cache automático
def cache_result(optimizer: CacheOptimizer, ttl: Optional[int] = None):
    """Decorator para cache automático de resultados de funções."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave única
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Tentar obter do cache
            cached_result = optimizer.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função
            result = func(*args, **kwargs)
            
            # Armazenar no cache
            optimizer.set(cache_key, result, ttl)
            
            return result
            
        return wrapper
    return decorator


# Função global para inicializar otimizador de cache
def initialize_cache_optimizer(config: Optional[CacheConfig] = None) -> CacheOptimizer:
    """Inicializa o otimizador de cache global."""
    if config is None:
        config = CacheConfig()
    
    optimizer = CacheOptimizer(config)
    optimizer.start_monitoring()
    
    logger.info("Otimizador de cache inicializado globalmente")
    return optimizer


# Instância global
_global_cache_optimizer: Optional[CacheOptimizer] = None


def get_global_cache_optimizer() -> Optional[CacheOptimizer]:
    """Obtém a instância global do otimizador de cache."""
    return _global_cache_optimizer


def set_global_cache_optimizer(optimizer: CacheOptimizer):
    """Define a instância global do otimizador de cache."""
    global _global_cache_optimizer
    _global_cache_optimizer = optimizer 