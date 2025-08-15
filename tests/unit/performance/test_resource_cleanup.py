"""
Test Resource Cleanup System - Omni Keywords Finder
Tracing ID: TEST_RESOURCE_CLEANUP_20250127_001
Data: 2025-01-27
Responsável: Backend Team

Testes para o sistema de cleanup automático de recursos.
Valida cleanup de modelos ML/NLP, conexões de banco e objetos grandes.
"""

import pytest
import time
import threading
import gc
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import psutil

from backend.app.optimization.resource_cleanup import (
    ResourceCleanup, ResourceTracker, MLModelCleaner, 
    DatabaseConnectionCleaner, CleanupConfig, ResourceInfo,
    get_resource_cleanup, start_cleanup_service, stop_cleanup_service,
    cleanup_resources
)


class TestResourceInfo:
    """Testa a classe ResourceInfo."""
    
    def test_resource_info_creation(self):
        """Testa criação de ResourceInfo."""
        resource = ResourceInfo(
            resource_id="test_model_001",
            resource_type="ml_model",
            size_bytes=1024 * 1024,  # 1MB
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            is_critical=True
        )
        
        assert resource.resource_id == "test_model_001"
        assert resource.resource_type == "ml_model"
        assert resource.size_bytes == 1024 * 1024
        assert resource.is_critical is True
        assert resource.cleanup_priority == 5


class TestCleanupConfig:
    """Testa a configuração do sistema de cleanup."""
    
    def test_default_config(self):
        """Testa configuração padrão."""
        config = CleanupConfig()
        
        assert config.memory_threshold_percent == 70.0
        assert config.cleanup_interval_seconds == 300
        assert config.max_resource_age_hours == 24
        assert config.critical_memory_threshold_percent == 85.0
        assert config.preserve_critical_resources is True
    
    def test_custom_config(self):
        """Testa configuração customizada."""
        config = CleanupConfig(
            memory_threshold_percent=80.0,
            cleanup_interval_seconds=600,
            enable_aggressive_cleanup=True
        )
        
        assert config.memory_threshold_percent == 80.0
        assert config.cleanup_interval_seconds == 600
        assert config.enable_aggressive_cleanup is True


class TestResourceTracker:
    """Testa o rastreador de recursos."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.tracker = ResourceTracker()
    
    def test_register_resource(self):
        """Testa registro de recursos."""
        self.tracker.register_resource(
            "test_resource_001",
            "ml_model",
            2048 * 1024,  # 2MB
            is_critical=True
        )
        
        assert "test_resource_001" in self.tracker.resources
        assert self.tracker.resources["test_resource_001"].resource_type == "ml_model"
        assert self.tracker.resources["test_resource_001"].is_critical is True
        assert "ml_model" in self.tracker.resource_types
    
    def test_update_access(self):
        """Testa atualização de acesso."""
        self.tracker.register_resource("test_resource_002", "cache", 1024)
        
        # Simula acesso
        self.tracker.update_access("test_resource_002")
        
        resource = self.tracker.resources["test_resource_002"]
        assert resource.access_count == 1
        assert resource.last_accessed > datetime.now() - timedelta(seconds=1)
    
    def test_get_old_resources(self):
        """Testa obtenção de recursos antigos."""
        # Registra recursos com diferentes idades
        self.tracker.register_resource("old_resource", "cache", 1024)
        self.tracker.register_resource("new_resource", "cache", 1024)
        
        # Simula que old_resource não foi acessado há muito tempo
        self.tracker.resources["old_resource"].last_accessed = datetime.now() - timedelta(hours=25)
        
        old_resources = self.tracker.get_old_resources(max_age_hours=24)
        
        assert len(old_resources) == 1
        assert old_resources[0].resource_id == "old_resource"
    
    def test_get_large_resources(self):
        """Testa obtenção de recursos grandes."""
        # Registra recursos com diferentes tamanhos
        self.tracker.register_resource("small_resource", "cache", 1024)  # 1KB
        self.tracker.register_resource("large_resource", "ml_model", 20 * 1024 * 1024)  # 20MB
        
        large_resources = self.tracker.get_large_resources(min_size_mb=10)
        
        assert len(large_resources) == 1
        assert large_resources[0].resource_id == "large_resource"
    
    def test_remove_resource(self):
        """Testa remoção de recursos."""
        self.tracker.register_resource("test_resource_003", "cache", 1024)
        
        removed = self.tracker.remove_resource("test_resource_003")
        
        assert removed is not None
        assert removed.resource_id == "test_resource_003"
        assert "test_resource_003" not in self.tracker.resources


class TestMLModelCleaner:
    """Testa o cleaner específico para modelos ML."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.tracker = ResourceTracker()
        self.cleaner = MLModelCleaner(self.tracker)
    
    def test_register_model(self):
        """Testa registro de modelo ML."""
        mock_model = Mock()
        self.cleaner.register_model("test_model_001", mock_model, 50 * 1024 * 1024)  # 50MB
        
        assert "test_model_001" in self.tracker.resources
        resource = self.tracker.resources["test_model_001"]
        assert resource.resource_type == "ml_model"
        assert resource.is_critical is True
        assert resource.size_bytes == 50 * 1024 * 1024
    
    def test_cleanup_unused_models(self):
        """Testa cleanup de modelos não utilizados."""
        # Registra modelos
        mock_model1 = Mock()
        mock_model2 = Mock()
        
        self.cleaner.register_model("active_model", mock_model1, 1024 * 1024)
        self.cleaner.register_model("inactive_model", mock_model2, 1024 * 1024)
        
        # Marca inactive_model como não crítico e antigo
        self.tracker.resources["inactive_model"].is_critical = False
        self.tracker.resources["inactive_model"].last_accessed = datetime.now() - timedelta(hours=3)
        
        cleaned_count = self.cleaner.cleanup_unused_models(max_idle_hours=2)
        
        assert cleaned_count == 1
        assert "inactive_model" not in self.tracker.resources
        assert "active_model" in self.tracker.resources


class TestDatabaseConnectionCleaner:
    """Testa o cleaner específico para conexões de banco."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.tracker = ResourceTracker()
        self.cleaner = DatabaseConnectionCleaner(self.tracker)
    
    def test_register_connection_pool(self):
        """Testa registro de pool de conexões."""
        mock_pool = Mock()
        self.cleaner.register_connection_pool("main_pool", mock_pool, 50)
        
        assert "main_pool" in self.tracker.resources
        resource = self.tracker.resources["main_pool"]
        assert resource.resource_type == "db_pool"
        assert resource.size_bytes == 50 * 1024  # Estimativa
    
    def test_cleanup_idle_connections(self):
        """Testa cleanup de conexões ociosas."""
        mock_pool = Mock()
        mock_pool.cleanup_idle_connections.return_value = 3
        
        self.cleaner.register_connection_pool("test_pool", mock_pool, 20)
        
        cleaned_count = self.cleaner.cleanup_idle_connections(max_idle_seconds=300)
        
        assert cleaned_count == 3
        mock_pool.cleanup_idle_connections.assert_called_once_with(300)


class TestResourceCleanup:
    """Testa o sistema principal de cleanup."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.config = CleanupConfig(
            memory_threshold_percent=70.0,
            cleanup_interval_seconds=1,  # Para testes
            max_resource_age_hours=1
        )
        self.cleanup = ResourceCleanup(self.config)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        if self.cleanup._running:
            self.cleanup.stop_cleanup_service()
    
    @patch('backend.app.optimization.resource_cleanup.psutil.virtual_memory')
    def test_normal_cleanup(self, mock_virtual_memory):
        """Testa cleanup normal."""
        # Mock memória baixa
        mock_memory = Mock()
        mock_memory.percent = 50.0
        mock_virtual_memory.return_value = mock_memory
        
        # Registra recursos
        self.cleanup.tracker.register_resource("large_resource", "cache", 15 * 1024 * 1024)  # 15MB
        self.cleanup.tracker.register_resource("small_resource", "cache", 1024)  # 1KB
        
        # Marca large_resource como não crítico e pouco acessado
        self.cleanup.tracker.resources["large_resource"].is_critical = False
        self.cleanup.tracker.resources["large_resource"].access_count = 2
        
        self.cleanup._normal_cleanup()
        
        # Verifica se large_resource foi removido
        assert "large_resource" not in self.cleanup.tracker.resources
        assert "small_resource" in self.cleanup.tracker.resources
    
    @patch('backend.app.optimization.resource_cleanup.psutil.virtual_memory')
    def test_aggressive_cleanup(self, mock_virtual_memory):
        """Testa cleanup agressivo."""
        # Mock memória alta
        mock_memory = Mock()
        mock_memory.percent = 80.0
        mock_virtual_memory.return_value = mock_memory
        
        # Registra recursos
        self.cleanup.tracker.register_resource("critical_resource", "ml_model", 1024, is_critical=True)
        self.cleanup.tracker.register_resource("normal_resource", "cache", 1024, is_critical=False)
        
        with patch.object(self.cleanup, 'cache') as mock_cache:
            self.cleanup._aggressive_cleanup()
            
            # Verifica se normal_resource foi removido
            assert "normal_resource" not in self.cleanup.tracker.resources
            # Verifica se critical_resource foi preservado
            assert "critical_resource" in self.cleanup.tracker.resources
            # Verifica se cache foi limpo
            mock_cache.clear_old_entries.assert_called_once_with(age_hours=1)
    
    def test_cleanup_old_resources(self):
        """Testa cleanup de recursos antigos."""
        # Registra recursos
        self.cleanup.tracker.register_resource("old_resource", "cache", 1024)
        self.cleanup.tracker.register_resource("new_resource", "cache", 1024)
        
        # Marca old_resource como antigo
        self.cleanup.tracker.resources["old_resource"].last_accessed = datetime.now() - timedelta(hours=2)
        
        self.cleanup._cleanup_old_resources()
        
        # Verifica se old_resource foi removido
        assert "old_resource" not in self.cleanup.tracker.resources
        assert "new_resource" in self.cleanup.tracker.resources
    
    def test_force_garbage_collection(self):
        """Testa garbage collection forçado."""
        with patch('gc.collect') as mock_gc:
            mock_gc.return_value = 10
            self.cleanup._force_garbage_collection()
            mock_gc.assert_called_once()
    
    def test_resource_context(self):
        """Testa context manager para recursos."""
        with self.cleanup.resource_context("test_context", "cache", 1024):
            assert "test_context" in self.cleanup.tracker.resources
        
        # Verifica se acesso foi atualizado
        resource = self.cleanup.tracker.resources["test_context"]
        assert resource.access_count == 1
    
    @patch('backend.app.optimization.resource_cleanup.psutil.virtual_memory')
    @patch('backend.app.optimization.resource_cleanup.tracemalloc.take_snapshot')
    def test_get_memory_stats(self, mock_snapshot, mock_virtual_memory):
        """Testa obtenção de estatísticas de memória."""
        # Mock memória
        mock_memory = Mock()
        mock_memory.percent = 65.5
        mock_memory.available = 4 * 1024 * 1024 * 1024  # 4GB
        mock_memory.used = 6 * 1024 * 1024 * 1024  # 6GB
        mock_virtual_memory.return_value = mock_memory
        
        # Mock snapshot
        mock_snapshot_instance = Mock()
        mock_snapshot_instance.statistics.return_value = [Mock(), Mock()]
        mock_snapshot.return_value = mock_snapshot_instance
        
        # Registra alguns recursos
        self.cleanup.tracker.register_resource("test_resource", "cache", 1024)
        
        stats = self.cleanup.get_memory_stats()
        
        assert stats["memory_percent"] == 65.5
        assert stats["memory_available_mb"] == 4096.0
        assert stats["memory_used_mb"] == 6144.0
        assert stats["tracked_resources_count"] == 1
        assert "cache" in stats["resource_types"]


class TestGlobalFunctions:
    """Testa funções globais do módulo."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Reset global instance
        import backend.app.optimization.resource_cleanup as cleanup_module
        cleanup_module.resource_cleanup = ResourceCleanup()
    
    def test_get_resource_cleanup(self):
        """Testa obtenção da instância global."""
        cleanup = get_resource_cleanup()
        assert isinstance(cleanup, ResourceCleanup)
    
    def test_start_stop_cleanup_service(self):
        """Testa início e parada do serviço de cleanup."""
        start_cleanup_service()
        
        # Verifica se serviço está rodando
        cleanup = get_resource_cleanup()
        assert cleanup._running is True
        assert cleanup._cleanup_thread is not None
        assert cleanup._cleanup_thread.is_alive()
        
        # Para o serviço
        stop_cleanup_service()
        
        # Verifica se serviço parou
        assert cleanup._running is False
    
    def test_cleanup_resources(self):
        """Testa cleanup manual de recursos."""
        # Registra alguns recursos
        cleanup = get_resource_cleanup()
        cleanup.tracker.register_resource("test_resource", "cache", 1024)
        
        result = cleanup_resources()
        
        assert "before" in result
        assert "after" in result
        assert isinstance(result["before"], dict)
        assert isinstance(result["after"], dict)


class TestIntegration:
    """Testes de integração do sistema de cleanup."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.cleanup = ResourceCleanup()
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        if self.cleanup._running:
            self.cleanup.stop_cleanup_service()
    
    @patch('backend.app.optimization.resource_cleanup.psutil.virtual_memory')
    def test_full_cleanup_cycle(self, mock_virtual_memory):
        """Testa ciclo completo de cleanup."""
        # Mock memória variável
        mock_memory = Mock()
        mock_memory.percent = 75.0  # Acima do threshold
        mock_virtual_memory.return_value = mock_memory
        
        # Registra diferentes tipos de recursos
        self.cleanup.register_ml_model("test_model", Mock(), 100 * 1024 * 1024)  # 100MB
        self.cleanup.register_db_pool("test_pool", Mock(), 20)
        self.cleanup.tracker.register_resource("old_cache", "cache", 1024)
        
        # Marca cache como antigo
        self.cleanup.tracker.resources["old_cache"].last_accessed = datetime.now() - timedelta(hours=2)
        
        # Executa cleanup
        self.cleanup._perform_cleanup()
        
        # Verifica se recursos antigos foram removidos
        assert "old_cache" not in self.cleanup.tracker.resources
        # Verifica se recursos críticos foram preservados
        assert "test_model" in self.cleanup.tracker.resources
        assert "test_pool" in self.cleanup.tracker.resources
    
    def test_memory_threshold_behavior(self):
        """Testa comportamento baseado em threshold de memória."""
        cleanup = ResourceCleanup()
        
        # Testa com memória baixa
        with patch('psutil.virtual_memory') as mock_vm:
            mock_memory = Mock()
            mock_memory.percent = 50.0
            mock_vm.return_value = mock_memory
            
            with patch.object(cleanup, '_normal_cleanup') as mock_normal:
                with patch.object(cleanup, '_aggressive_cleanup') as mock_aggressive:
                    cleanup._perform_cleanup()
                    
                    mock_normal.assert_called_once()
                    mock_aggressive.assert_not_called()
        
        # Testa com memória alta
        with patch('psutil.virtual_memory') as mock_vm:
            mock_memory = Mock()
            mock_memory.percent = 80.0
            mock_vm.return_value = mock_memory
            
            with patch.object(cleanup, '_normal_cleanup') as mock_normal:
                with patch.object(cleanup, '_aggressive_cleanup') as mock_aggressive:
                    cleanup._perform_cleanup()
                    
                    mock_normal.assert_not_called()
                    mock_aggressive.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 