"""
Garbage Collection Optimizer - Omni Keywords Finder
Tracing ID: GC_OPTIMIZER_20250127_001
Data: 2025-01-27
Responsável: Backend Team

Sistema de otimização de garbage collection para melhorar performance de memória.
Implementa estratégias inteligentes de GC baseadas em padrões de uso.
"""

import gc
import logging
import threading
import time
import weakref
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
import psutil
import tracemalloc
import sys

from ..monitoring.memory_profiler import MemoryProfiler

logger = logging.getLogger(__name__)


@dataclass
class GCOptimizationConfig:
    """Configuração do otimizador de GC."""
    enable_auto_gc: bool = True
    gc_threshold_percent: float = 75.0
    gc_interval_seconds: int = 300  # 5 minutos
    aggressive_gc_threshold_percent: float = 85.0
    max_gc_frequency_minutes: int = 5
    enable_generational_gc: bool = True
    enable_weakref_cleanup: bool = True
    enable_circular_ref_detection: bool = True
    gc_debug_level: int = 0  # 0=off, 1=basic, 2=detailed


@dataclass
class GCMetrics:
    """Métricas de garbage collection."""
    total_collections: int = 0
    total_objects_collected: int = 0
    avg_collection_time_ms: float = 0.0
    last_collection_time: Optional[datetime] = None
    memory_before_mb: float = 0.0
    memory_after_mb: float = 0.0
    collection_efficiency: float = 0.0  # MB freed per second


class GenerationalGCOptimizer:
    """Otimizador de GC generacional."""
    
    def __init__(self, config: GCOptimizationConfig):
        self.config = config
        self.generation_stats: Dict[int, Dict[str, Any]] = {
            0: {"collections": 0, "objects": 0, "time": 0.0},
            1: {"collections": 0, "objects": 0, "time": 0.0},
            2: {"collections": 0, "objects": 0, "time": 0.0}
        }
        self._setup_generational_gc()
    
    def _setup_generational_gc(self) -> None:
        """Configura GC generacional otimizado."""
        if self.config.enable_generational_gc:
            # Configura thresholds para diferentes gerações
            gc.set_threshold(700, 10, 10)  # (threshold0, threshold1, threshold2)
            logger.info("Generational GC configured with optimized thresholds")
    
    def optimize_generation_thresholds(self, memory_pressure: float) -> None:
        """Ajusta thresholds baseado na pressão de memória."""
        if memory_pressure > 80.0:
            # Pressão alta - GC mais agressivo
            gc.set_threshold(500, 7, 7)
        elif memory_pressure > 60.0:
            # Pressão média - GC balanceado
            gc.set_threshold(700, 10, 10)
        else:
            # Pressão baixa - GC conservador
            gc.set_threshold(1000, 15, 15)
        
        logger.debug(f"GC thresholds adjusted for memory pressure: {memory_pressure:.1f}%")
    
    def get_generation_stats(self) -> Dict[int, Dict[str, Any]]:
        """Retorna estatísticas por geração."""
        stats = gc.get_stats()
        for gen in range(3):
            if gen < len(stats):
                self.generation_stats[gen].update({
                    "collections": stats[gen]["collections"],
                    "objects": stats[gen]["collections"],
                    "time": stats[gen]["collections"]
                })
        return self.generation_stats


class WeakRefManager:
    """Gerenciador de weak references para evitar memory leaks."""
    
    def __init__(self):
        self.weak_refs: Dict[str, weakref.ref] = {}
        self.callbacks: Dict[str, Callable] = {}
        self._lock = threading.RLock()
    
    def register_weak_ref(self, key: str, obj: Any, callback: Optional[Callable] = None) -> None:
        """Registra uma weak reference com callback opcional."""
        with self._lock:
            if callback:
                self.callbacks[key] = callback
            
            def finalizer(ref):
                if key in self.callbacks:
                    try:
                        self.callbacks[key]()
                    except Exception as e:
                        logger.error(f"Error in weak ref callback for {key}: {e}")
                    finally:
                        self._cleanup_ref(key)
            
            self.weak_refs[key] = weakref.ref(obj, finalizer)
            logger.debug(f"Weak reference registered: {key}")
    
    def _cleanup_ref(self, key: str) -> None:
        """Remove referência e callback."""
        with self._lock:
            self.weak_refs.pop(key, None)
            self.callbacks.pop(key, None)
            logger.debug(f"Weak reference cleaned up: {key}")
    
    def cleanup_expired_refs(self) -> int:
        """Remove referências expiradas."""
        with self._lock:
            expired_keys = []
            for key, ref in self.weak_refs.items():
                if ref() is None:  # Referência expirada
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._cleanup_ref(key)
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired weak references")
            
            return len(expired_keys)
    
    def get_active_refs_count(self) -> int:
        """Retorna número de referências ativas."""
        with self._lock:
            return len([ref for ref in self.weak_refs.values() if ref() is not None])


class CircularRefDetector:
    """Detector de referências circulares."""
    
    def __init__(self, config: GCOptimizationConfig):
        self.config = config
        self.detected_circular_refs: List[Dict[str, Any]] = []
    
    def detect_circular_references(self) -> List[Dict[str, Any]]:
        """Detecta referências circulares no sistema."""
        if not self.config.enable_circular_ref_detection:
            return []
        
        circular_refs = []
        
        # Coleta objetos suspeitos
        suspicious_objects = []
        for obj in gc.get_objects():
            if hasattr(obj, '__dict__') and len(obj.__dict__) > 10:
                suspicious_objects.append(obj)
        
        # Analisa referências circulares
        for obj in suspicious_objects[:100]:  # Limita análise
            try:
                refs = gc.get_referrers(obj)
                if len(refs) > 5:  # Muitas referências podem indicar circular ref
                    circular_refs.append({
                        "object_type": type(obj).__name__,
                        "object_id": id(obj),
                        "referrer_count": len(refs),
                        "detected_at": datetime.now()
                    })
            except Exception as e:
                logger.debug(f"Error analyzing object {id(obj)}: {e}")
        
        self.detected_circular_refs.extend(circular_refs)
        return circular_refs
    
    def get_circular_ref_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de referências circulares."""
        return {
            "total_detected": len(self.detected_circular_refs),
            "recent_detections": len([ref for ref in self.detected_circular_refs 
                                    if ref["detected_at"] > datetime.now() - timedelta(hours=1)]),
            "by_type": self._group_by_type()
        }
    
    def _group_by_type(self) -> Dict[str, int]:
        """Agrupa detecções por tipo de objeto."""
        type_counts = {}
        for ref in self.detected_circular_refs:
            obj_type = ref["object_type"]
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        return type_counts


class GCOptimizer:
    """Sistema principal de otimização de garbage collection."""
    
    def __init__(self, config: Optional[GCOptimizationConfig] = None):
        self.config = config or GCOptimizationConfig()
        self.metrics = GCMetrics()
        self.memory_profiler = MemoryProfiler()
        
        # Componentes especializados
        self.generational_optimizer = GenerationalGCOptimizer(self.config)
        self.weak_ref_manager = WeakRefManager()
        self.circular_ref_detector = CircularRefDetector(self.config)
        
        # Controle de execução
        self._gc_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        self._last_gc_time = datetime.now()
        
        # Configuração inicial
        self._setup_gc()
    
    def _setup_gc(self) -> None:
        """Configura garbage collection inicial."""
        # Habilita debug se configurado
        if self.config.gc_debug_level > 0:
            gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_LEAK)
        
        # Configura callbacks para monitoramento
        gc.callbacks.append(self._gc_callback)
        
        logger.info("GC Optimizer initialized with configuration")
    
    def _gc_callback(self, phase: str, info: Dict[str, Any]) -> None:
        """Callback para monitorar execuções de GC."""
        if phase == "start":
            self.metrics.memory_before_mb = psutil.virtual_memory().used / (1024 * 1024)
            self.metrics.last_collection_time = datetime.now()
        elif phase == "stop":
            self.metrics.total_collections += 1
            self.metrics.total_objects_collected += info.get("collected", 0)
            
            # Calcula métricas
            memory_after = psutil.virtual_memory().used / (1024 * 1024)
            self.metrics.memory_after_mb = memory_after
            
            if self.metrics.last_collection_time:
                duration = (datetime.now() - self.metrics.last_collection_time).total_seconds()
                memory_freed = self.metrics.memory_before_mb - memory_after
                
                if duration > 0:
                    self.metrics.collection_efficiency = memory_freed / duration
                
                # Atualiza tempo médio
                if self.metrics.total_collections > 1:
                    self.metrics.avg_collection_time_ms = (
                        (self.metrics.avg_collection_time_ms * (self.metrics.total_collections - 1) + duration * 1000) /
                        self.metrics.total_collections
                    )
                else:
                    self.metrics.avg_collection_time_ms = duration * 1000
            
            logger.debug(f"GC completed: {info.get('collected', 0)} objects collected, "
                        f"{self.metrics.memory_before_mb - memory_after:.1f}MB freed")
    
    def start_optimization_service(self) -> None:
        """Inicia o serviço de otimização em background."""
        if self._running:
            logger.warning("GC optimization service already running")
            return
        
        self._stop_event.clear()
        self._running = True
        self._gc_thread = threading.Thread(
            target=self._optimization_loop,
            name="GCOptimizationThread",
            daemon=True
        )
        self._gc_thread.start()
        logger.info("GC optimization service started")
    
    def stop_optimization_service(self) -> None:
        """Para o serviço de otimização."""
        if not self._running:
            return
        
        self._stop_event.set()
        self._running = False
        
        if self._gc_thread and self._gc_thread.is_alive():
            self._gc_thread.join(timeout=10)
        
        logger.info("GC optimization service stopped")
    
    def _optimization_loop(self) -> None:
        """Loop principal de otimização."""
        while not self._stop_event.is_set():
            try:
                self._perform_optimization()
                time.sleep(self.config.gc_interval_seconds)
            except Exception as e:
                logger.error(f"Error in GC optimization loop: {e}")
                time.sleep(60)
    
    def _perform_optimization(self) -> None:
        """Executa otimizações de GC."""
        current_memory_percent = psutil.virtual_memory().percent
        time_since_last_gc = datetime.now() - self._last_gc_time
        
        # Verifica se deve executar GC
        should_run_gc = (
            current_memory_percent > self.config.gc_threshold_percent and
            time_since_last_gc.total_seconds() > self.config.max_gc_frequency_minutes * 60
        )
        
        if should_run_gc:
            self._run_optimized_gc(current_memory_percent)
        
        # Otimizações contínuas
        self._continuous_optimizations()
    
    def _run_optimized_gc(self, memory_pressure: float) -> None:
        """Executa GC otimizado baseado na pressão de memória."""
        logger.info(f"Running optimized GC (memory pressure: {memory_pressure:.1f}%)")
        
        # Ajusta thresholds generacionais
        self.generational_optimizer.optimize_generation_thresholds(memory_pressure)
        
        # Executa GC apropriado baseado na pressão
        if memory_pressure > self.config.aggressive_gc_threshold_percent:
            # GC agressivo
            collected = gc.collect(2)  # Força coleta de todas as gerações
            logger.warning(f"Aggressive GC completed: {collected} objects collected")
        else:
            # GC normal
            collected = gc.collect()
            logger.info(f"Normal GC completed: {collected} objects collected")
        
        self._last_gc_time = datetime.now()
    
    def _continuous_optimizations(self) -> None:
        """Otimizações contínuas que não requerem GC completo."""
        # Cleanup de weak references
        if self.config.enable_weakref_cleanup:
            cleaned_refs = self.weak_ref_manager.cleanup_expired_refs()
            if cleaned_refs > 0:
                logger.debug(f"Weak ref cleanup: {cleaned_refs} references removed")
        
        # Detecção de referências circulares
        if self.config.enable_circular_ref_detection:
            circular_refs = self.circular_ref_detector.detect_circular_references()
            if circular_refs:
                logger.warning(f"Circular references detected: {len(circular_refs)}")
    
    def force_gc(self, generation: int = 2) -> Dict[str, Any]:
        """Força execução de GC e retorna métricas."""
        logger.info(f"Forcing GC (generation {generation})")
        
        memory_before = psutil.virtual_memory().used / (1024 * 1024)
        start_time = time.time()
        
        collected = gc.collect(generation)
        
        duration = time.time() - start_time
        memory_after = psutil.virtual_memory().used / (1024 * 1024)
        memory_freed = memory_before - memory_after
        
        result = {
            "objects_collected": collected,
            "memory_freed_mb": memory_freed,
            "duration_seconds": duration,
            "efficiency_mb_per_second": memory_freed / duration if duration > 0 else 0,
            "generation": generation
        }
        
        logger.info(f"Force GC completed: {collected} objects, {memory_freed:.1f}MB freed in {duration:.2f}s")
        return result
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas de otimização."""
        memory = psutil.virtual_memory()
        
        return {
            "gc_metrics": {
                "total_collections": self.metrics.total_collections,
                "total_objects_collected": self.metrics.total_objects_collected,
                "avg_collection_time_ms": self.metrics.avg_collection_time_ms,
                "collection_efficiency": self.metrics.collection_efficiency,
                "last_collection": self.metrics.last_collection_time.isoformat() if self.metrics.last_collection_time else None
            },
            "memory_stats": {
                "current_percent": memory.percent,
                "available_mb": memory.available / (1024 * 1024),
                "used_mb": memory.used / (1024 * 1024)
            },
            "generational_stats": self.generational_optimizer.get_generation_stats(),
            "weak_ref_stats": {
                "active_refs": self.weak_ref_manager.get_active_refs_count(),
                "total_registered": len(self.weak_ref_manager.weak_refs)
            },
            "circular_ref_stats": self.circular_ref_detector.get_circular_ref_stats(),
            "configuration": {
                "auto_gc_enabled": self.config.enable_auto_gc,
                "gc_threshold_percent": self.config.gc_threshold_percent,
                "aggressive_threshold_percent": self.config.aggressive_gc_threshold_percent
            }
        }
    
    def register_weak_ref(self, key: str, obj: Any, callback: Optional[Callable] = None) -> None:
        """Registra uma weak reference para cleanup automático."""
        self.weak_ref_manager.register_weak_ref(key, obj, callback)
    
    @contextmanager
    def gc_context(self, description: str = ""):
        """Context manager para execução de GC controlado."""
        logger.debug(f"GC context started: {description}")
        
        try:
            yield
        finally:
            # Executa GC leve no final do contexto
            if self.config.enable_auto_gc:
                gc.collect(0)  # Apenas geração 0
                logger.debug(f"GC context completed: {description}")


# Instância global do otimizador
gc_optimizer = GCOptimizer()


def get_gc_optimizer() -> GCOptimizer:
    """Retorna a instância global do otimizador de GC."""
    return gc_optimizer


def start_gc_optimization() -> None:
    """Inicia o serviço de otimização de GC global."""
    gc_optimizer.start_optimization_service()


def stop_gc_optimization() -> None:
    """Para o serviço de otimização de GC global."""
    gc_optimizer.stop_optimization_service()


def force_gc_optimization(generation: int = 2) -> Dict[str, Any]:
    """Força execução de GC otimizado."""
    return gc_optimizer.force_gc(generation)


def get_gc_stats() -> Dict[str, Any]:
    """Retorna estatísticas de otimização de GC."""
    return gc_optimizer.get_optimization_stats()


def register_weak_ref_for_cleanup(key: str, obj: Any, callback: Optional[Callable] = None) -> None:
    """Registra uma weak reference para cleanup automático."""
    gc_optimizer.register_weak_ref(key, obj, callback)


@contextmanager
def gc_optimization_context(description: str = ""):
    """Context manager para otimização de GC."""
    with gc_optimizer.gc_context(description):
        yield 