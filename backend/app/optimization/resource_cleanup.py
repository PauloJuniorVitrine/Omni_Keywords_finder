"""
Resource Cleanup System - Omni Keywords Finder
Tracing ID: RESOURCE_CLEANUP_20250127_001
Data: 2025-01-27
Responsável: Backend Team

Sistema de cleanup automático de recursos para otimização de memória.
Gerencia cleanup de modelos NLP/ML, conexões de banco e objetos grandes.
"""

import gc
import logging
import threading
import time
import weakref
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
import psutil
import tracemalloc

from ..monitoring.memory_profiler import MemoryProfiler
from ..cache.intelligent_cache import IntelligentCache

logger = logging.getLogger(__name__)


@dataclass
class ResourceInfo:
    """Informações sobre um recurso gerenciado."""
    resource_id: str
    resource_type: str
    size_bytes: int
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    is_critical: bool = False
    cleanup_priority: int = 1  # 1=baixa, 5=alta


@dataclass
class CleanupConfig:
    """Configuração do sistema de cleanup."""
    memory_threshold_percent: float = 70.0
    cleanup_interval_seconds: int = 300  # 5 minutos
    max_resource_age_hours: int = 24
    critical_memory_threshold_percent: float = 85.0
    enable_aggressive_cleanup: bool = False
    preserve_critical_resources: bool = True


class ResourceTracker:
    """Rastreador de recursos para monitoramento."""
    
    def __init__(self):
        self.resources: Dict[str, ResourceInfo] = {}
        self.resource_types: Dict[str, Set[str]] = {}
        self._lock = threading.RLock()
    
    def register_resource(self, resource_id: str, resource_type: str, 
                         size_bytes: int, is_critical: bool = False) -> None:
        """Registra um novo recurso para monitoramento."""
        with self._lock:
            now = datetime.now()
            resource_info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                size_bytes=size_bytes,
                created_at=now,
                last_accessed=now,
                is_critical=is_critical,
                cleanup_priority=5 if is_critical else 1
            )
            
            self.resources[resource_id] = resource_info
            
            if resource_type not in self.resource_types:
                self.resource_types[resource_type] = set()
            self.resource_types[resource_type].add(resource_id)
            
            logger.info(f"Resource registered: {resource_id} ({resource_type}) - {size_bytes} bytes")
    
    def update_access(self, resource_id: str) -> None:
        """Atualiza informações de acesso do recurso."""
        with self._lock:
            if resource_id in self.resources:
                self.resources[resource_id].last_accessed = datetime.now()
                self.resources[resource_id].access_count += 1
    
    def get_old_resources(self, max_age_hours: int) -> List[ResourceInfo]:
        """Retorna recursos antigos baseado na idade."""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            return [
                resource for resource in self.resources.values()
                if resource.last_accessed < cutoff_time and not resource.is_critical
            ]
    
    def get_large_resources(self, min_size_mb: int) -> List[ResourceInfo]:
        """Retorna recursos grandes baseado no tamanho."""
        with self._lock:
            min_size_bytes = min_size_mb * 1024 * 1024
            return [
                resource for resource in self.resources.values()
                if resource.size_bytes > min_size_bytes
            ]
    
    def remove_resource(self, resource_id: str) -> Optional[ResourceInfo]:
        """Remove um recurso do rastreamento."""
        with self._lock:
            if resource_id in self.resources:
                resource_info = self.resources.pop(resource_id)
                resource_type = resource_info.resource_type
                
                if resource_type in self.resource_types:
                    self.resource_types[resource_type].discard(resource_id)
                    if not self.resource_types[resource_type]:
                        del self.resource_types[resource_type]
                
                return resource_info
            return None


class MLModelCleaner:
    """Cleaner específico para modelos ML/NLP."""
    
    def __init__(self, tracker: ResourceTracker):
        self.tracker = tracker
        self.model_cache: Dict[str, Any] = {}
    
    def register_model(self, model_id: str, model: Any, size_bytes: int) -> None:
        """Registra um modelo ML para cleanup."""
        self.tracker.register_resource(model_id, "ml_model", size_bytes, is_critical=True)
        self.model_cache[model_id] = weakref.ref(model)
    
    def cleanup_unused_models(self, max_idle_hours: int = 2) -> int:
        """Remove modelos não utilizados."""
        cleaned_count = 0
        cutoff_time = datetime.now() - timedelta(hours=max_idle_hours)
        
        for resource_id, resource_info in list(self.tracker.resources.items()):
            if (resource_info.resource_type == "ml_model" and 
                resource_info.last_accessed < cutoff_time and 
                not resource_info.is_critical):
                
                # Remove referência fraca
                if resource_id in self.model_cache:
                    del self.model_cache[resource_id]
                
                # Remove do tracker
                self.tracker.remove_resource(resource_id)
                cleaned_count += 1
                
                logger.info(f"ML model cleaned: {resource_id}")
        
        return cleaned_count


class DatabaseConnectionCleaner:
    """Cleaner específico para conexões de banco."""
    
    def __init__(self, tracker: ResourceTracker):
        self.tracker = tracker
        self.connection_pools: Dict[str, Any] = {}
    
    def register_connection_pool(self, pool_id: str, pool: Any, max_connections: int) -> None:
        """Registra um pool de conexões."""
        # Estimativa de tamanho baseada no número de conexões
        estimated_size = max_connections * 1024  # ~1KB por conexão
        self.tracker.register_resource(pool_id, "db_pool", estimated_size)
        self.connection_pools[pool_id] = pool
    
    def cleanup_idle_connections(self, max_idle_seconds: int = 300) -> int:
        """Fecha conexões ociosas."""
        cleaned_count = 0
        
        for pool_id, pool in self.connection_pools.items():
            try:
                # Assumindo que o pool tem método para limpar conexões ociosas
                if hasattr(pool, 'cleanup_idle_connections'):
                    cleaned = pool.cleanup_idle_connections(max_idle_seconds)
                    cleaned_count += cleaned
                    logger.info(f"DB connections cleaned from pool {pool_id}: {cleaned}")
            except Exception as e:
                logger.error(f"Error cleaning DB connections from pool {pool_id}: {e}")
        
        return cleaned_count


class ResourceCleanup:
    """Sistema principal de cleanup de recursos."""
    
    def __init__(self, config: Optional[CleanupConfig] = None):
        self.config = config or CleanupConfig()
        self.tracker = ResourceTracker()
        self.ml_cleaner = MLModelCleaner(self.tracker)
        self.db_cleaner = DatabaseConnectionCleaner(self.tracker)
        self.memory_profiler = MemoryProfiler()
        self.cache = IntelligentCache()
        
        self._cleanup_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        
        # Inicializa tracemalloc para análise detalhada
        tracemalloc.start()
    
    def start_cleanup_service(self) -> None:
        """Inicia o serviço de cleanup em background."""
        if self._running:
            logger.warning("Cleanup service already running")
            return
        
        self._stop_event.clear()
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            name="ResourceCleanupThread",
            daemon=True
        )
        self._cleanup_thread.start()
        logger.info("Resource cleanup service started")
    
    def stop_cleanup_service(self) -> None:
        """Para o serviço de cleanup."""
        if not self._running:
            return
        
        self._stop_event.set()
        self._running = False
        
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=10)
        
        logger.info("Resource cleanup service stopped")
    
    def _cleanup_loop(self) -> None:
        """Loop principal do serviço de cleanup."""
        while not self._stop_event.is_set():
            try:
                self._perform_cleanup()
                time.sleep(self.config.cleanup_interval_seconds)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(60)  # Espera 1 minuto em caso de erro
    
    def _perform_cleanup(self) -> None:
        """Executa o processo de cleanup."""
        current_memory_percent = psutil.virtual_memory().percent
        
        logger.debug(f"Memory usage: {current_memory_percent:.1f}%")
        
        # Cleanup baseado em threshold de memória
        if current_memory_percent > self.config.memory_threshold_percent:
            self._aggressive_cleanup()
        else:
            self._normal_cleanup()
        
        # Cleanup de recursos antigos
        self._cleanup_old_resources()
        
        # Cleanup de conexões ociosas
        self._cleanup_idle_connections()
        
        # Força garbage collection se necessário
        if current_memory_percent > self.config.critical_memory_threshold_percent:
            self._force_garbage_collection()
    
    def _normal_cleanup(self) -> None:
        """Cleanup normal - recursos não críticos."""
        cleaned_count = 0
        
        # Limpa recursos grandes não utilizados
        large_resources = self.tracker.get_large_resources(min_size_mb=10)
        for resource in large_resources:
            if not resource.is_critical and resource.access_count < 5:
                if self._cleanup_resource(resource.resource_id):
                    cleaned_count += 1
        
        # Limpa cache se necessário
        if cleaned_count > 0:
            self.cache.cleanup_old_entries()
        
        logger.info(f"Normal cleanup completed: {cleaned_count} resources cleaned")
    
    def _aggressive_cleanup(self) -> None:
        """Cleanup agressivo - quando memória está alta."""
        cleaned_count = 0
        
        # Limpa todos os recursos não críticos
        for resource_id, resource_info in list(self.tracker.resources.items()):
            if not resource_info.is_critical:
                if self._cleanup_resource(resource_id):
                    cleaned_count += 1
        
        # Limpa cache agressivamente
        self.cache.clear_old_entries(age_hours=1)
        
        # Força garbage collection
        gc.collect()
        
        logger.warning(f"Aggressive cleanup completed: {cleaned_count} resources cleaned")
    
    def _cleanup_old_resources(self) -> None:
        """Remove recursos antigos."""
        old_resources = self.tracker.get_old_resources(self.config.max_resource_age_hours)
        
        for resource in old_resources:
            if not resource.is_critical:
                self._cleanup_resource(resource.resource_id)
        
        if old_resources:
            logger.info(f"Old resources cleanup: {len(old_resources)} resources removed")
    
    def _cleanup_idle_connections(self) -> None:
        """Limpa conexões ociosas."""
        cleaned = self.db_cleaner.cleanup_idle_connections()
        if cleaned > 0:
            logger.info(f"Idle connections cleanup: {cleaned} connections closed")
    
    def _cleanup_resource(self, resource_id: str) -> bool:
        """Remove um recurso específico."""
        resource_info = self.tracker.remove_resource(resource_id)
        if resource_info:
            logger.info(f"Resource cleaned: {resource_id} ({resource_info.resource_type})")
            return True
        return False
    
    def _force_garbage_collection(self) -> None:
        """Força garbage collection."""
        collected = gc.collect()
        logger.warning(f"Force garbage collection: {collected} objects collected")
    
    @contextmanager
    def resource_context(self, resource_id: str, resource_type: str, 
                        size_bytes: int, is_critical: bool = False):
        """Context manager para gerenciar recursos automaticamente."""
        self.tracker.register_resource(resource_id, resource_type, size_bytes, is_critical)
        
        try:
            yield
        finally:
            # Atualiza acesso ao final do contexto
            self.tracker.update_access(resource_id)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de memória."""
        memory = psutil.virtual_memory()
        snapshot = tracemalloc.take_snapshot()
        
        return {
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "memory_used_mb": memory.used / (1024 * 1024),
            "tracked_resources_count": len(self.tracker.resources),
            "resource_types": list(self.tracker.resource_types.keys()),
            "top_memory_allocations": snapshot.statistics('lineno')[:5]
        }
    
    def register_ml_model(self, model_id: str, model: Any, size_bytes: int) -> None:
        """Registra um modelo ML para cleanup."""
        self.ml_cleaner.register_model(model_id, model, size_bytes)
    
    def register_db_pool(self, pool_id: str, pool: Any, max_connections: int) -> None:
        """Registra um pool de conexões para cleanup."""
        self.db_cleaner.register_connection_pool(pool_id, pool, max_connections)


# Instância global do sistema de cleanup
resource_cleanup = ResourceCleanup()


def get_resource_cleanup() -> ResourceCleanup:
    """Retorna a instância global do sistema de cleanup."""
    return resource_cleanup


def start_cleanup_service() -> None:
    """Inicia o serviço de cleanup global."""
    resource_cleanup.start_cleanup_service()


def stop_cleanup_service() -> None:
    """Para o serviço de cleanup global."""
    resource_cleanup.stop_cleanup_service()


def cleanup_resources() -> Dict[str, Any]:
    """Executa cleanup manual e retorna estatísticas."""
    stats = resource_cleanup.get_memory_stats()
    
    # Executa cleanup
    resource_cleanup._perform_cleanup()
    
    # Retorna estatísticas atualizadas
    return {
        "before": stats,
        "after": resource_cleanup.get_memory_stats()
    } 