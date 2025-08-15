"""
Test Garbage Collection Optimizer - Omni Keywords Finder
Tracing ID: TEST_GC_OPTIMIZER_20250127_001
Data: 2025-01-27
Responsável: Backend Team

Testes para o sistema de otimização de garbage collection.
Valida otimizações de GC, weak references e detecção de referências circulares.
"""

import pytest
import gc
import time
import threading
import weakref
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import psutil

from backend.app.optimization.gc_optimizer import (
    GCOptimizer, GenerationalGCOptimizer, WeakRefManager, 
    CircularRefDetector, GCOptimizationConfig, GCMetrics,
    get_gc_optimizer, start_gc_optimization, stop_gc_optimization,
    force_gc_optimization, get_gc_stats, register_weak_ref_for_cleanup,
    gc_optimization_context
)


class TestGCOptimizationConfig:
    """Testa a configuração do otimizador de GC."""
    
    def test_default_config(self):
        """Testa configuração padrão."""
        config = GCOptimizationConfig()
        
        assert config.enable_auto_gc is True
        assert config.gc_threshold_percent == 75.0
        assert config.gc_interval_seconds == 300
        assert config.aggressive_gc_threshold_percent == 85.0
        assert config.enable_generational_gc is True
        assert config.enable_weakref_cleanup is True
        assert config.enable_circular_ref_detection is True
    
    def test_custom_config(self):
        """Testa configuração customizada."""
        config = GCOptimizationConfig(
            enable_auto_gc=False,
            gc_threshold_percent=80.0,
            aggressive_gc_threshold_percent=90.0,
            gc_debug_level=2
        )
        
        assert config.enable_auto_gc is False
        assert config.gc_threshold_percent == 80.0
        assert config.aggressive_gc_threshold_percent == 90.0
        assert config.gc_debug_level == 2


class TestGCMetrics:
    """Testa as métricas de garbage collection."""
    
    def test_gc_metrics_creation(self):
        """Testa criação de métricas."""
        metrics = GCMetrics()
        
        assert metrics.total_collections == 0
        assert metrics.total_objects_collected == 0
        assert metrics.avg_collection_time_ms == 0.0
        assert metrics.last_collection_time is None
        assert metrics.memory_before_mb == 0.0
        assert metrics.memory_after_mb == 0.0
        assert metrics.collection_efficiency == 0.0


class TestGenerationalGCOptimizer:
    """Testa o otimizador de GC generacional."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = GCOptimizationConfig()
        self.optimizer = GenerationalGCOptimizer(self.config)
    
    def test_setup_generational_gc(self):
        """Testa configuração inicial do GC generacional."""
        # Verifica se thresholds foram configurados
        thresholds = gc.get_threshold()
        assert len(thresholds) == 3
        assert thresholds[0] == 700  # threshold0
        assert thresholds[1] == 10   # threshold1
        assert thresholds[2] == 10   # threshold2
    
    def test_optimize_generation_thresholds_high_pressure(self):
        """Testa otimização de thresholds com pressão alta."""
        self.optimizer.optimize_generation_thresholds(85.0)
        
        thresholds = gc.get_threshold()
        assert thresholds[0] == 500  # Mais agressivo
        assert thresholds[1] == 7
        assert thresholds[2] == 7
    
    def test_optimize_generation_thresholds_medium_pressure(self):
        """Testa otimização de thresholds com pressão média."""
        self.optimizer.optimize_generation_thresholds(70.0)
        
        thresholds = gc.get_threshold()
        assert thresholds[0] == 700  # Balanceado
        assert thresholds[1] == 10
        assert thresholds[2] == 10
    
    def test_optimize_generation_thresholds_low_pressure(self):
        """Testa otimização de thresholds com pressão baixa."""
        self.optimizer.optimize_generation_thresholds(40.0)
        
        thresholds = gc.get_threshold()
        assert thresholds[0] == 1000  # Conservador
        assert thresholds[1] == 15
        assert thresholds[2] == 15
    
    def test_get_generation_stats(self):
        """Testa obtenção de estatísticas por geração."""
        stats = self.optimizer.get_generation_stats()
        
        assert 0 in stats
        assert 1 in stats
        assert 2 in stats
        
        for gen in [0, 1, 2]:
            assert "collections" in stats[gen]
            assert "objects" in stats[gen]
            assert "time" in stats[gen]


class TestWeakRefManager:
    """Testa o gerenciador de weak references."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.manager = WeakRefManager()
    
    def test_register_weak_ref(self):
        """Testa registro de weak reference."""
        test_obj = {"data": "test"}
        
        self.manager.register_weak_ref("test_key", test_obj)
        
        assert "test_key" in self.manager.weak_refs
        assert self.manager.weak_refs["test_key"]() == test_obj
    
    def test_register_weak_ref_with_callback(self):
        """Testa registro de weak reference com callback."""
        test_obj = {"data": "test"}
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        self.manager.register_weak_ref("test_key", test_obj, test_callback)
        
        assert "test_key" in self.manager.callbacks
        assert self.manager.callbacks["test_key"] == test_callback
    
    def test_cleanup_expired_refs(self):
        """Testa cleanup de referências expiradas."""
        # Registra referências
        obj1 = {"data": "test1"}
        obj2 = {"data": "test2"}
        
        self.manager.register_weak_ref("key1", obj1)
        self.manager.register_weak_ref("key2", obj2)
        
        # Remove referência para obj1
        del obj1
        
        # Força garbage collection para expirar weak ref
        gc.collect()
        
        cleaned_count = self.manager.cleanup_expired_refs()
        
        assert cleaned_count == 1
        assert "key1" not in self.manager.weak_refs
        assert "key2" in self.manager.weak_refs
    
    def test_get_active_refs_count(self):
        """Testa contagem de referências ativas."""
        # Registra referências
        obj1 = {"data": "test1"}
        obj2 = {"data": "test2"}
        
        self.manager.register_weak_ref("key1", obj1)
        self.manager.register_weak_ref("key2", obj2)
        
        active_count = self.manager.get_active_refs_count()
        assert active_count == 2
        
        # Remove uma referência
        del obj1
        gc.collect()
        
        active_count = self.manager.get_active_refs_count()
        assert active_count == 1


class TestCircularRefDetector:
    """Testa o detector de referências circulares."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = GCOptimizationConfig()
        self.detector = CircularRefDetector(self.config)
    
    def test_detect_circular_references_disabled(self):
        """Testa detecção com feature desabilitada."""
        self.config.enable_circular_ref_detection = False
        
        result = self.detector.detect_circular_references()
        
        assert result == []
    
    def test_detect_circular_references_enabled(self):
        """Testa detecção com feature habilitada."""
        # Cria alguns objetos para análise
        test_objects = []
        for i in range(5):
            obj = {"id": i, "data": f"test_data_{i}"}
            test_objects.append(obj)
        
        result = self.detector.detect_circular_references()
        
        # Resultado pode variar dependendo do estado do sistema
        assert isinstance(result, list)
    
    def test_get_circular_ref_stats(self):
        """Testa obtenção de estatísticas de referências circulares."""
        # Simula algumas detecções
        self.detector.detected_circular_refs = [
            {"object_type": "TestClass", "object_id": 123, "referrer_count": 5, "detected_at": datetime.now()},
            {"object_type": "TestClass", "object_id": 456, "referrer_count": 3, "detected_at": datetime.now()},
            {"object_type": "OtherClass", "object_id": 789, "referrer_count": 7, "detected_at": datetime.now() - timedelta(hours=2)}
        ]
        
        stats = self.detector.get_circular_ref_stats()
        
        assert stats["total_detected"] == 3
        assert stats["recent_detections"] == 2  # Apenas as últimas 2 horas
        assert stats["by_type"]["TestClass"] == 2
        assert stats["by_type"]["OtherClass"] == 1


class TestGCOptimizer:
    """Testa o sistema principal de otimização de GC."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = GCOptimizationConfig(
            gc_interval_seconds=1,  # Para testes
            max_gc_frequency_minutes=0  # Para testes
        )
        self.optimizer = GCOptimizer(self.config)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        if self.optimizer._running:
            self.optimizer.stop_optimization_service()
    
    def test_initialization(self):
        """Testa inicialização do otimizador."""
        assert self.optimizer.config == self.config
        assert isinstance(self.optimizer.metrics, GCMetrics)
        assert isinstance(self.optimizer.generational_optimizer, GenerationalGCOptimizer)
        assert isinstance(self.optimizer.weak_ref_manager, WeakRefManager)
        assert isinstance(self.optimizer.circular_ref_detector, CircularRefDetector)
    
    @patch('backend.app.optimization.gc_optimizer.psutil.virtual_memory')
    def test_perform_optimization_low_memory(self, mock_virtual_memory):
        """Testa otimização com memória baixa."""
        # Mock memória baixa
        mock_memory = Mock()
        mock_memory.percent = 50.0
        mock_virtual_memory.return_value = mock_memory
        
        with patch.object(self.optimizer, '_run_optimized_gc') as mock_gc:
            self.optimizer._perform_optimization()
            
            # Não deve executar GC com memória baixa
            mock_gc.assert_not_called()
    
    @patch('backend.app.optimization.gc_optimizer.psutil.virtual_memory')
    def test_perform_optimization_high_memory(self, mock_virtual_memory):
        """Testa otimização com memória alta."""
        # Mock memória alta
        mock_memory = Mock()
        mock_memory.percent = 80.0
        mock_virtual_memory.return_value = mock_memory
        
        with patch.object(self.optimizer, '_run_optimized_gc') as mock_gc:
            self.optimizer._perform_optimization()
            
            # Deve executar GC com memória alta
            mock_gc.assert_called_once_with(80.0)
    
    def test_run_optimized_gc_normal(self):
        """Testa GC normal."""
        with patch.object(self.optimizer.generational_optimizer, 'optimize_generation_thresholds') as mock_optimize:
            with patch('gc.collect') as mock_gc:
                mock_gc.return_value = 10
                
                self.optimizer._run_optimized_gc(70.0)
                
                mock_optimize.assert_called_once_with(70.0)
                mock_gc.assert_called_once()  # GC normal
    
    def test_run_optimized_gc_aggressive(self):
        """Testa GC agressivo."""
        with patch.object(self.optimizer.generational_optimizer, 'optimize_generation_thresholds') as mock_optimize:
            with patch('gc.collect') as mock_gc:
                mock_gc.return_value = 20
                
                self.optimizer._run_optimized_gc(90.0)
                
                mock_optimize.assert_called_once_with(90.0)
                mock_gc.assert_called_once_with(2)  # GC agressivo
    
    def test_continuous_optimizations(self):
        """Testa otimizações contínuas."""
        with patch.object(self.optimizer.weak_ref_manager, 'cleanup_expired_refs') as mock_cleanup:
            with patch.object(self.optimizer.circular_ref_detector, 'detect_circular_references') as mock_detect:
                mock_cleanup.return_value = 2
                mock_detect.return_value = [{"type": "test"}]
                
                self.optimizer._continuous_optimizations()
                
                mock_cleanup.assert_called_once()
                mock_detect.assert_called_once()
    
    def test_force_gc(self):
        """Testa GC forçado."""
        with patch('gc.collect') as mock_gc:
            with patch('time.time') as mock_time:
                with patch('psutil.virtual_memory') as mock_vm:
                    mock_gc.return_value = 15
                    mock_time.side_effect = [100.0, 100.5]  # 0.5 segundos
                    
                    mock_memory = Mock()
                    mock_memory.used = 6 * 1024 * 1024 * 1024  # 6GB antes
                    mock_vm.return_value = mock_memory
                    
                    result = self.optimizer.force_gc(generation=1)
                    
                    mock_gc.assert_called_once_with(1)
                    assert result["objects_collected"] == 15
                    assert result["duration_seconds"] == 0.5
                    assert result["generation"] == 1
    
    def test_get_optimization_stats(self):
        """Testa obtenção de estatísticas de otimização."""
        with patch('psutil.virtual_memory') as mock_vm:
            mock_memory = Mock()
            mock_memory.percent = 65.5
            mock_memory.available = 4 * 1024 * 1024 * 1024  # 4GB
            mock_memory.used = 6 * 1024 * 1024 * 1024  # 6GB
            mock_vm.return_value = mock_memory
            
            stats = self.optimizer.get_optimization_stats()
            
            assert "gc_metrics" in stats
            assert "memory_stats" in stats
            assert "generational_stats" in stats
            assert "weak_ref_stats" in stats
            assert "circular_ref_stats" in stats
            assert "configuration" in stats
            
            assert stats["memory_stats"]["current_percent"] == 65.5
            assert stats["memory_stats"]["available_mb"] == 4096.0
            assert stats["memory_stats"]["used_mb"] == 6144.0
    
    def test_register_weak_ref(self):
        """Testa registro de weak reference."""
        test_obj = {"data": "test"}
        
        self.optimizer.register_weak_ref("test_key", test_obj)
        
        assert "test_key" in self.optimizer.weak_ref_manager.weak_refs
        assert self.optimizer.weak_ref_manager.weak_refs["test_key"]() == test_obj
    
    def test_gc_context(self):
        """Testa context manager de GC."""
        with patch('gc.collect') as mock_gc:
            with self.optimizer.gc_context("test_context"):
                pass
            
            # Deve executar GC leve no final
            mock_gc.assert_called_once_with(0)


class TestGlobalFunctions:
    """Testa funções globais do módulo."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Reset global instance
        import backend.app.optimization.gc_optimizer as gc_module
        gc_module.gc_optimizer = GCOptimizer()
    
    def test_get_gc_optimizer(self):
        """Testa obtenção da instância global."""
        optimizer = get_gc_optimizer()
        assert isinstance(optimizer, GCOptimizer)
    
    def test_start_stop_gc_optimization(self):
        """Testa início e parada do serviço de otimização."""
        start_gc_optimization()
        
        # Verifica se serviço está rodando
        optimizer = get_gc_optimizer()
        assert optimizer._running is True
        assert optimizer._gc_thread is not None
        assert optimizer._gc_thread.is_alive()
        
        # Para o serviço
        stop_gc_optimization()
        
        # Verifica se serviço parou
        assert optimizer._running is False
    
    def test_force_gc_optimization(self):
        """Testa GC forçado global."""
        with patch('gc.collect') as mock_gc:
            mock_gc.return_value = 25
            
            result = force_gc_optimization(generation=2)
            
            mock_gc.assert_called_once_with(2)
            assert result["objects_collected"] == 25
            assert result["generation"] == 2
    
    def test_get_gc_stats(self):
        """Testa obtenção de estatísticas globais."""
        stats = get_gc_stats()
        
        assert isinstance(stats, dict)
        assert "gc_metrics" in stats
        assert "memory_stats" in stats
        assert "configuration" in stats
    
    def test_register_weak_ref_for_cleanup(self):
        """Testa registro de weak reference global."""
        test_obj = {"data": "test"}
        
        register_weak_ref_for_cleanup("test_key", test_obj)
        
        optimizer = get_gc_optimizer()
        assert "test_key" in optimizer.weak_ref_manager.weak_refs
    
    def test_gc_optimization_context(self):
        """Testa context manager global."""
        with patch('gc.collect') as mock_gc:
            with gc_optimization_context("test_context"):
                pass
            
            # Deve executar GC leve no final
            mock_gc.assert_called_once_with(0)


class TestIntegration:
    """Testes de integração do sistema de otimização de GC."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.optimizer = GCOptimizer()
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        if self.optimizer._running:
            self.optimizer.stop_optimization_service()
    
    @patch('backend.app.optimization.gc_optimizer.psutil.virtual_memory')
    def test_full_optimization_cycle(self, mock_virtual_memory):
        """Testa ciclo completo de otimização."""
        # Mock memória variável
        mock_memory = Mock()
        mock_memory.percent = 80.0
        mock_virtual_memory.return_value = mock_memory
        
        # Registra algumas weak references
        test_obj1 = {"data": "test1"}
        test_obj2 = {"data": "test2"}
        
        self.optimizer.register_weak_ref("key1", test_obj1)
        self.optimizer.register_weak_ref("key2", test_obj2)
        
        # Remove uma referência
        del test_obj1
        
        # Executa otimização
        with patch('gc.collect') as mock_gc:
            mock_gc.return_value = 10
            self.optimizer._perform_optimization()
            
            # Verifica se GC foi executado
            mock_gc.assert_called()
            
            # Verifica se weak refs foram limpas
            gc.collect()  # Força cleanup
            active_refs = self.optimizer.weak_ref_manager.get_active_refs_count()
            assert active_refs == 1  # Apenas key2 deve estar ativa
    
    def test_memory_pressure_response(self):
        """Testa resposta a diferentes níveis de pressão de memória."""
        optimizer = GCOptimizer()
        
        # Testa com pressão baixa
        with patch('psutil.virtual_memory') as mock_vm:
            mock_memory = Mock()
            mock_memory.percent = 50.0
            mock_vm.return_value = mock_memory
            
            with patch.object(optimizer, '_run_optimized_gc') as mock_gc:
                optimizer._perform_optimization()
                mock_gc.assert_not_called()
        
        # Testa com pressão alta
        with patch('psutil.virtual_memory') as mock_vm:
            mock_memory = Mock()
            mock_memory.percent = 90.0
            mock_vm.return_value = mock_memory
            
            with patch.object(optimizer, '_run_optimized_gc') as mock_gc:
                optimizer._perform_optimization()
                mock_gc.assert_called_once_with(90.0)


if __name__ == "__main__":
    pytest.main([__file__]) 