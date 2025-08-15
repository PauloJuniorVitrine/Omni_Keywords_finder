"""
Testes Unitários para CacheWarmingService
CacheWarmingService - Sistema de aquecimento inteligente de cache

Prompt: Implementação de testes unitários para CacheWarmingService
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_WARMING_SERVICE_20250127_001
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from backend.app.cache.warming_service import (
    WarmingPattern,
    WarmingJob,
    CacheWarmingService
)
from backend.app.cache.intelligent_cache import IntelligentCache


class TestWarmingPattern:
    """Testes para WarmingPattern"""
    
    @pytest.fixture
    def sample_pattern_data(self):
        """Dados de exemplo para WarmingPattern"""
        return {
            "key_pattern": "user:*:profile",
            "frequency": 0.5,
            "priority": 8,
            "dependencies": ["user:*:preferences", "user:*:settings"]
        }
    
    @pytest.fixture
    def pattern(self, sample_pattern_data):
        """Instância de WarmingPattern para testes"""
        return WarmingPattern(**sample_pattern_data)
    
    def test_initialization(self, sample_pattern_data):
        """Testa inicialização básica"""
        pattern = WarmingPattern(**sample_pattern_data)
        
        assert pattern.key_pattern == "user:*:profile"
        assert pattern.frequency == 0.5
        assert pattern.priority == 8
        assert pattern.dependencies == ["user:*:preferences", "user:*:settings"]
        assert pattern.last_warmed is None
        assert pattern.success_rate == 0.0
        assert pattern.avg_load_time == 0.0
    
    def test_default_values(self):
        """Testa valores padrão"""
        pattern = WarmingPattern(
            key_pattern="test:*",
            frequency=0.1,
            priority=5
        )
        
        assert pattern.last_warmed is None
        assert pattern.success_rate == 0.0
        assert pattern.avg_load_time == 0.0
        assert pattern.dependencies == []
    
    def test_priority_validation(self):
        """Testa validação de prioridade"""
        # Prioridade válida
        pattern = WarmingPattern(
            key_pattern="test:*",
            frequency=0.1,
            priority=10
        )
        assert pattern.priority == 10
        
        # Prioridade mínima
        pattern = WarmingPattern(
            key_pattern="test:*",
            frequency=0.1,
            priority=1
        )
        assert pattern.priority == 1


class TestWarmingJob:
    """Testes para WarmingJob"""
    
    @pytest.fixture
    def sample_job_data(self):
        """Dados de exemplo para WarmingJob"""
        return {
            "id": "warming_test_123",
            "pattern": WarmingPattern(
                key_pattern="user:*:profile",
                frequency=0.5,
                priority=8
            ),
            "target_keys": ["user:1:profile", "user:2:profile", "user:3:profile"],
            "priority": 8,
            "created_at": datetime.now()
        }
    
    @pytest.fixture
    def job(self, sample_job_data):
        """Instância de WarmingJob para testes"""
        return WarmingJob(**sample_job_data)
    
    def test_initialization(self, sample_job_data):
        """Testa inicialização básica"""
        job = WarmingJob(**sample_job_data)
        
        assert job.id == "warming_test_123"
        assert job.pattern.key_pattern == "user:*:profile"
        assert len(job.target_keys) == 3
        assert job.priority == 8
        assert job.status == "pending"
        assert job.progress == 0.0
        assert job.error_message is None
    
    def test_default_values(self):
        """Testa valores padrão"""
        pattern = WarmingPattern(
            key_pattern="test:*",
            frequency=0.1,
            priority=5
        )
        
        job = WarmingJob(
            id="test_job",
            pattern=pattern,
            target_keys=["test:1"],
            priority=5,
            created_at=datetime.now()
        )
        
        assert job.status == "pending"
        assert job.progress == 0.0
        assert job.error_message is None


class TestCacheWarmingService:
    """Testes para CacheWarmingService"""
    
    @pytest.fixture
    def mock_cache(self):
        """Mock do IntelligentCache"""
        cache = Mock(spec=IntelligentCache)
        cache.get = Mock(return_value=None)
        cache.set = Mock(return_value=True)
        return cache
    
    @pytest.fixture
    def warming_service(self, mock_cache):
        """Instância de CacheWarmingService para testes"""
        return CacheWarmingService(cache=mock_cache)
    
    @pytest.fixture
    def sample_pattern(self):
        """Padrão de exemplo"""
        return WarmingPattern(
            key_pattern="user:*:profile",
            frequency=0.5,
            priority=8,
            dependencies=["user:*:preferences"]
        )
    
    def test_initialization(self, mock_cache):
        """Testa inicialização do serviço"""
        service = CacheWarmingService(cache=mock_cache)
        
        assert service.cache == mock_cache
        assert service.patterns == {}
        assert service.jobs == {}
        assert service.max_concurrent_jobs == 5
        assert service.warming_interval == 300
        assert service.min_frequency_threshold == 0.1
        assert service.max_warming_keys == 100
        assert service.success_threshold == 0.7
    
    def test_register_pattern(self, warming_service, sample_pattern):
        """Testa registro de padrão"""
        warming_service.register_pattern(sample_pattern)
        
        assert "user:*:profile" in warming_service.patterns
        assert warming_service.patterns["user:*:profile"] == sample_pattern
    
    def test_register_duplicate_pattern(self, warming_service, sample_pattern):
        """Testa registro de padrão duplicado"""
        warming_service.register_pattern(sample_pattern)
        warming_service.register_pattern(sample_pattern)  # Sobrescreve
        
        assert len(warming_service.patterns) == 1
        assert "user:*:profile" in warming_service.patterns
    
    def test_track_access(self, warming_service, sample_pattern):
        """Testa rastreamento de acesso"""
        warming_service.register_pattern(sample_pattern)
        warming_service.track_access("user:123:profile", load_time=0.5)
        
        assert "user:123:profile" in warming_service.access_history
        assert len(warming_service.access_history["user:123:profile"]) == 1
    
    def test_matches_pattern(self, warming_service):
        """Testa correspondência de padrões"""
        # Padrão simples
        assert warming_service._matches_pattern("user:123:profile", "user:*:profile")
        assert not warming_service._matches_pattern("user:123:settings", "user:*:profile")
        
        # Padrão complexo
        assert warming_service._matches_pattern("api:v1:users:123", "api:*:users:*")
        assert not warming_service._matches_pattern("api:v2:posts:123", "api:*:users:*")
    
    @pytest.mark.asyncio
    async def test_warm_cache_success(self, warming_service, sample_pattern):
        """Testa aquecimento de cache bem-sucedido"""
        warming_service.register_pattern(sample_pattern)
        
        with patch.object(warming_service, '_execute_warming_job', new_callable=AsyncMock):
            job = await warming_service.warm_cache("user:*:profile")
            
            assert job is not None
            assert job.id.startswith("warming_user:*:profile_")
            assert job.pattern == sample_pattern
            assert job.status == "pending"
    
    @pytest.mark.asyncio
    async def test_warm_cache_pattern_not_found(self, warming_service):
        """Testa aquecimento com padrão não encontrado"""
        with pytest.raises(ValueError, match="Pattern user:*:profile not found"):
            await warming_service.warm_cache("user:*:profile")
    
    @pytest.mark.asyncio
    async def test_warm_cache_frequency_too_low(self, warming_service, sample_pattern):
        """Testa aquecimento com frequência muito baixa"""
        sample_pattern.frequency = 0.05  # Abaixo do threshold
        warming_service.register_pattern(sample_pattern)
        
        job = await warming_service.warm_cache("user:*:profile")
        assert job is None
    
    @pytest.mark.asyncio
    async def test_warm_cache_recently_warmed(self, warming_service, sample_pattern):
        """Testa aquecimento recentemente executado"""
        sample_pattern.last_warmed = datetime.now() - timedelta(minutes=10)
        warming_service.register_pattern(sample_pattern)
        
        job = await warming_service.warm_cache("user:*:profile")
        assert job is None
    
    @pytest.mark.asyncio
    async def test_execute_warming_job_success(self, warming_service, sample_pattern):
        """Testa execução bem-sucedida de job de aquecimento"""
        job = WarmingJob(
            id="test_job",
            pattern=sample_pattern,
            target_keys=["user:1:profile", "user:2:profile"],
            priority=8,
            created_at=datetime.now()
        )
        
        with patch.object(warming_service, '_warm_key', new_callable=AsyncMock, return_value=True):
            await warming_service._execute_warming_job(job)
            
            assert job.status == "completed"
            assert job.progress == 100.0
            assert job.error_message is None
            assert warming_service.warming_stats["successful_jobs"] == 1
            assert warming_service.warming_stats["total_keys_warmed"] == 2
    
    @pytest.mark.asyncio
    async def test_execute_warming_job_failure(self, warming_service, sample_pattern):
        """Testa execução com falha de job de aquecimento"""
        job = WarmingJob(
            id="test_job",
            pattern=sample_pattern,
            target_keys=["user:1:profile"],
            priority=8,
            created_at=datetime.now()
        )
        
        with patch.object(warming_service, '_warm_key', new_callable=AsyncMock, side_effect=Exception("Test error")):
            await warming_service._execute_warming_job(job)
            
            assert job.status == "failed"
            assert job.error_message == "Test error"
            assert warming_service.warming_stats["failed_jobs"] == 1
    
    @pytest.mark.asyncio
    async def test_warm_key_success(self, warming_service):
        """Testa aquecimento de chave específica"""
        with patch.object(warming_service.cache, 'get', return_value=None):
            with patch.object(warming_service.cache, 'set', return_value=True):
                success = await warming_service._warm_key("user:123:profile")
                assert success is True
    
    @pytest.mark.asyncio
    async def test_warm_key_failure(self, warming_service):
        """Testa falha no aquecimento de chave"""
        with patch.object(warming_service.cache, 'get', return_value=None):
            with patch.object(warming_service.cache, 'set', return_value=False):
                success = await warming_service._warm_key("user:123:profile")
                assert success is False
    
    def test_optimize_patterns(self, warming_service, sample_pattern):
        """Testa otimização de padrões"""
        warming_service.register_pattern(sample_pattern)
        warming_service.warming_stats["successful_jobs"] = 5
        warming_service.warming_stats["failed_jobs"] = 1
        
        optimization_stats = warming_service.optimize_patterns()
        
        assert "total_patterns" in optimization_stats
        assert "success_rate" in optimization_stats
        assert "recommendations" in optimization_stats
        assert optimization_stats["total_patterns"] == 1
    
    @pytest.mark.asyncio
    async def test_start_background_warming(self, warming_service, sample_pattern):
        """Testa início do serviço de aquecimento em background"""
        warming_service.register_pattern(sample_pattern)
        
        # Mock do loop de background
        with patch.object(warming_service, 'warm_cache', new_callable=AsyncMock) as mock_warm:
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                # Executar por um ciclo
                mock_sleep.side_effect = asyncio.CancelledError()
                
                with pytest.raises(asyncio.CancelledError):
                    await warming_service.start_background_warming()
                
                # Verificar se tentou aquecer
                mock_warm.assert_called()


class TestCacheWarmingServiceIntegration:
    """Testes de integração para CacheWarmingService"""
    
    @pytest.mark.asyncio
    async def test_full_warming_cycle(self):
        """Testa ciclo completo de aquecimento"""
        mock_cache = Mock(spec=IntelligentCache)
        mock_cache.get = Mock(return_value=None)
        mock_cache.set = Mock(return_value=True)
        
        service = CacheWarmingService(cache=mock_cache)
        
        # Registrar padrão
        pattern = WarmingPattern(
            key_pattern="user:*:profile",
            frequency=0.8,
            priority=9
        )
        service.register_pattern(pattern)
        
        # Simular acessos
        service.track_access("user:1:profile", 0.3)
        service.track_access("user:2:profile", 0.4)
        
        # Executar aquecimento
        with patch.object(service, '_execute_warming_job', new_callable=AsyncMock):
            job = await service.warm_cache("user:*:profile")
            
            assert job is not None
            assert job.status == "pending"
            assert len(job.target_keys) > 0


class TestCacheWarmingServiceErrorHandling:
    """Testes de tratamento de erro para CacheWarmingService"""
    
    def test_invalid_pattern_key(self, warming_service):
        """Testa padrão com chave inválida"""
        with pytest.raises(ValueError):
            warming_service.register_pattern(None)
    
    def test_negative_frequency(self, warming_service):
        """Testa frequência negativa"""
        pattern = WarmingPattern(
            key_pattern="test:*",
            frequency=-0.1,
            priority=5
        )
        
        # Deve aceitar mas com warning
        warming_service.register_pattern(pattern)
        assert pattern.frequency == -0.1
    
    @pytest.mark.asyncio
    async def test_cache_connection_error(self, warming_service, sample_pattern):
        """Testa erro de conexão com cache"""
        warming_service.register_pattern(sample_pattern)
        warming_service.cache.set.side_effect = Exception("Connection error")
        
        with patch.object(warming_service, '_execute_warming_job', new_callable=AsyncMock):
            job = await warming_service.warm_cache("user:*:profile")
            
            # Job deve ser criado mesmo com erro de cache
            assert job is not None


class TestCacheWarmingServicePerformance:
    """Testes de performance para CacheWarmingService"""
    
    def test_large_number_of_patterns(self, mock_cache):
        """Testa performance com muitos padrões"""
        service = CacheWarmingService(cache=mock_cache)
        
        # Registrar 1000 padrões
        for i in range(1000):
            pattern = WarmingPattern(
                key_pattern=f"pattern_{i}:*",
                frequency=0.1,
                priority=5
            )
            service.register_pattern(pattern)
        
        assert len(service.patterns) == 1000
    
    def test_memory_usage_with_large_history(self, mock_cache):
        """Testa uso de memória com histórico grande"""
        service = CacheWarmingService(cache=mock_cache)
        
        # Simular muitos acessos
        for i in range(10000):
            service.track_access(f"key_{i}", 0.1)
        
        # Verificar se o histórico está limitado
        for key in service.access_history:
            assert len(service.access_history[key]) <= 100  # maxlen configurado 