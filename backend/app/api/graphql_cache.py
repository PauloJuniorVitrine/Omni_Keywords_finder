#!/usr/bin/env python3
"""
📦 GRAPHQL CACHE SYSTEM - OMNİ KEYWORDS FINDER

Tracing ID: GRAPHQL_CACHE_2025_001
Data/Hora: 2025-01-27 18:15:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Sistema de cache inteligente para GraphQL com invalidação automática.
"""

import os
import sys
import json
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] [GRAPHQL_CACHE] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/graphql_cache.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Estratégias de cache"""
    CACHE_FIRST = "cache_first"
    CACHE_AND_NETWORK = "cache_and_network"
    NETWORK_ONLY = "network_only"
    NO_CACHE = "no_cache"

class CacheEntry:
    """Entrada de cache"""
    
    def __init__(self, key: str, data: Any, ttl: int = 300):
        self.key = key
        self.data = data
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.ttl = ttl
        self.access_count = 0
        self.dependencies: Set[str] = set()
    
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl)
    
    def is_stale(self, stale_threshold: int = 60) -> bool:
        """Verifica se a entrada está obsoleta"""
        return datetime.now() - self.last_accessed > timedelta(seconds=stale_threshold)
    
    def access(self):
        """Registra acesso"""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def add_dependency(self, dependency: str):
        """Adiciona dependência"""
        self.dependencies.add(dependency)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'key': self.key,
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'ttl': self.ttl,
            'access_count': self.access_count,
            'dependencies': list(self.dependencies)
        }

class GraphQLCache:
    """Sistema de cache GraphQL"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.dependency_map: Dict[str, Set[str]] = defaultdict(set)
        self.access_order: List[str] = []
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'invalidations': 0
        }
        
        # Iniciar thread de limpeza
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def generate_key(self, query: str, variables: Optional[Dict] = None, operation_name: Optional[str] = None) -> str:
        """Gera chave de cache"""
        key_data = {
            'query': query,
            'variables': variables or {},
            'operation_name': operation_name or ''
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém dados do cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                if entry.is_expired():
                    # Remove entrada expirada
                    self._remove_entry(key)
                    self.stats['misses'] += 1
                    return None
                
                # Registra acesso
                entry.access()
                self._update_access_order(key)
                self.stats['hits'] += 1
                
                return entry.data
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None, dependencies: Optional[List[str]] = None) -> None:
        """Define dados no cache"""
        with self.lock:
            # Remove entrada existente se houver
            if key in self.cache:
                self._remove_entry(key)
            
            # Cria nova entrada
            entry = CacheEntry(key, data, ttl or self.default_ttl)
            
            # Adiciona dependências
            if dependencies:
                for dep in dependencies:
                    entry.add_dependency(dep)
                    self.dependency_map[dep].add(key)
            
            # Adiciona ao cache
            self.cache[key] = entry
            self._update_access_order(key)
            
            # Verifica limite de tamanho
            if len(self.cache) > self.max_size:
                self._evict_oldest()
    
    def invalidate(self, pattern: str) -> int:
        """Invalida entradas por padrão"""
        with self.lock:
            invalidated = 0
            
            # Invalida por dependência
            if pattern in self.dependency_map:
                for key in self.dependency_map[pattern]:
                    if key in self.cache:
                        self._remove_entry(key)
                        invalidated += 1
                del self.dependency_map[pattern]
            
            # Invalida por padrão de chave
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                self._remove_entry(key)
                invalidated += 1
            
            self.stats['invalidations'] += invalidated
            return invalidated
    
    def clear(self) -> int:
        """Limpa todo o cache"""
        with self.lock:
            count = len(self.cache)
            self.cache.clear()
            self.dependency_map.clear()
            self.access_order.clear()
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        with self.lock:
            hit_rate = 0
            if self.stats['hits'] + self.stats['misses'] > 0:
                hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': hit_rate,
                'evictions': self.stats['evictions'],
                'invalidations': self.stats['invalidations'],
                'dependencies': len(self.dependency_map)
            }
    
    def _remove_entry(self, key: str) -> None:
        """Remove entrada do cache"""
        if key in self.cache:
            entry = self.cache[key]
            
            # Remove dependências
            for dep in entry.dependencies:
                if dep in self.dependency_map:
                    self.dependency_map[dep].discard(key)
                    if not self.dependency_map[dep]:
                        del self.dependency_map[dep]
            
            # Remove da lista de acesso
            if key in self.access_order:
                self.access_order.remove(key)
            
            # Remove do cache
            del self.cache[key]
    
    def _update_access_order(self, key: str) -> None:
        """Atualiza ordem de acesso (LRU)"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _evict_oldest(self) -> None:
        """Remove entrada mais antiga (LRU)"""
        if self.access_order:
            oldest_key = self.access_order[0]
            self._remove_entry(oldest_key)
            self.stats['evictions'] += 1
    
    def _cleanup_loop(self) -> None:
        """Loop de limpeza automática"""
        while True:
            try:
                time.sleep(60)  # Executa a cada minuto
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"Erro no loop de limpeza: {e}")
    
    def _cleanup_expired(self) -> None:
        """Remove entradas expiradas"""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
            
            if expired_keys:
                logger.info(f"Removidas {len(expired_keys)} entradas expiradas")

class GraphQLCacheMiddleware:
    """Middleware de cache para GraphQL"""
    
    def __init__(self, cache: GraphQLCache):
        self.cache = cache
    
    def process_query(self, query: str, variables: Optional[Dict] = None, 
                     operation_name: Optional[str] = None, 
                     strategy: CacheStrategy = CacheStrategy.CACHE_FIRST) -> Optional[Any]:
        """Processa query com cache"""
        key = self.cache.generate_key(query, variables, operation_name)
        
        if strategy == CacheStrategy.NO_CACHE:
            return None
        
        if strategy == CacheStrategy.NETWORK_ONLY:
            return None
        
        # Tenta obter do cache
        cached_data = self.cache.get(key)
        
        if cached_data is not None:
            logger.info(f"Cache hit para query: {operation_name or 'anonymous'}")
            return cached_data
        
        logger.info(f"Cache miss para query: {operation_name or 'anonymous'}")
        return None
    
    def cache_result(self, query: str, variables: Optional[Dict] = None,
                    operation_name: Optional[str] = None, data: Any = None,
                    ttl: Optional[int] = None, dependencies: Optional[List[str]] = None) -> None:
        """Armazena resultado no cache"""
        key = self.cache.generate_key(query, variables, operation_name)
        
        # Extrai dependências da query
        if dependencies is None:
            dependencies = self._extract_dependencies(query)
        
        self.cache.set(key, data, ttl, dependencies)
        logger.info(f"Resultado armazenado no cache: {operation_name or 'anonymous'}")
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalida cache por padrão"""
        count = self.cache.invalidate(pattern)
        logger.info(f"Invalidadas {count} entradas do cache com padrão: {pattern}")
        return count
    
    def _extract_dependencies(self, query: str) -> List[str]:
        """Extrai dependências da query GraphQL"""
        dependencies = []
        
        # Extrai nomes de tipos da query
        import re
        
        # Padrões para extrair tipos
        patterns = [
            r'(\w+)\string_data*\{',  # Campos com subcampos
            r'(\w+)\string_data*\(',  # Campos com argumentos
            r'type\string_data+(\w+)',  # Definições de tipo
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            dependencies.extend(matches)
        
        return list(set(dependencies))

class GraphQLCacheManager:
    """Gerenciador de cache GraphQL"""
    
    def __init__(self):
        self.cache = GraphQLCache()
        self.middleware = GraphQLCacheMiddleware(self.cache)
        self.query_patterns = {
            'nichos': ['nicho', 'categoria'],
            'execucoes': ['execucao', 'keyword'],
            'metrics': ['metric', 'performance'],
            'logs': ['log', 'audit']
        }
    
    def get_cached_query(self, query: str, variables: Optional[Dict] = None,
                        operation_name: Optional[str] = None) -> Optional[Any]:
        """Obtém query do cache"""
        return self.middleware.process_query(query, variables, operation_name)
    
    def cache_query_result(self, query: str, variables: Optional[Dict] = None,
                          operation_name: Optional[str] = None, data: Any = None,
                          ttl: Optional[int] = None) -> None:
        """Armazena resultado de query no cache"""
        self.middleware.cache_result(query, variables, operation_name, data, ttl)
    
    def invalidate_by_operation(self, operation: str) -> int:
        """Invalida cache por operação"""
        patterns = self.query_patterns.get(operation, [operation])
        total_invalidated = 0
        
        for pattern in patterns:
            total_invalidated += self.middleware.invalidate_pattern(pattern)
        
        return total_invalidated
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        return self.cache.get_stats()
    
    def clear_cache(self) -> int:
        """Limpa todo o cache"""
        return self.cache.clear()
    
    def export_cache_data(self) -> Dict[str, Any]:
        """Exporta dados do cache"""
        return {
            'entries': [entry.to_dict() for entry in self.cache.cache.values()],
            'stats': self.cache.get_stats(),
            'dependencies': dict(self.cache.dependency_map)
        }
    
    def import_cache_data(self, data: Dict[str, Any]) -> None:
        """Importa dados para o cache"""
        self.cache.clear()
        
        for entry_data in data.get('entries', []):
            entry = CacheEntry(
                key=entry_data['key'],
                data=entry_data['data'],
                ttl=entry_data['ttl']
            )
            entry.created_at = datetime.fromisoformat(entry_data['created_at'])
            entry.last_accessed = datetime.fromisoformat(entry_data['last_accessed'])
            entry.access_count = entry_data['access_count']
            entry.dependencies = set(entry_data['dependencies'])
            
            self.cache.cache[entry.key] = entry
            
            # Restaura dependências
            for dep in entry.dependencies:
                self.cache.dependency_map[dep].add(entry.key)

# Instância global do cache
graphql_cache_manager = GraphQLCacheManager()

def get_graphql_cache() -> GraphQLCacheManager:
    """Obtém instância do cache GraphQL"""
    return graphql_cache_manager

def cache_graphql_query(query: str, variables: Optional[Dict] = None,
                       operation_name: Optional[str] = None, data: Any = None,
                       ttl: Optional[int] = None) -> None:
    """Função helper para cache de query"""
    graphql_cache_manager.cache_query_result(query, variables, operation_name, data, ttl)

def get_cached_graphql_query(query: str, variables: Optional[Dict] = None,
                           operation_name: Optional[str] = None) -> Optional[Any]:
    """Função helper para obter query do cache"""
    return graphql_cache_manager.get_cached_query(query, variables, operation_name)

def invalidate_graphql_cache(operation: str) -> int:
    """Função helper para invalidar cache"""
    return graphql_cache_manager.invalidate_by_operation(operation) 