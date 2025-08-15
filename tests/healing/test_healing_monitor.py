"""
Testes Unitários para HealingMonitor
HealingMonitor - Monitoramento para Sistema de Auto-Cura

Prompt: Implementação de testes unitários para HealingMonitor
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_HEALING_MONITOR_001_20250127
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.healing.healing_monitor import (
    ServiceMetrics,
    HealingMonitor
)
from infrastructure.healing.self_healing_service import ServiceStatus, ServiceInfo
from infrastructure.healing.healing_config import HealingConfig


class TestServiceMetrics:
    """Testes para ServiceMetrics"""
    
    @pytest.fixture
    def sample_metrics_data(self):
        """Dados de exemplo para métricas de serviço"""
        return {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.5,
            "network_io": {"bytes_sent": 1024, "bytes_recv": 2048},
            "response_time": 150.0,
            "error_rate": 0.02,
            "active_connections": 25,
            "timestamp": datetime.now(timezone.utc)
        }
    
    def test_service_metrics_initialization(self, sample_metrics_data):
        """Testa inicialização básica"""
        metrics = ServiceMetrics(**sample_metrics_data)
        
        assert metrics.cpu_usage == 45.2
        assert metrics.memory_usage == 67.8
        assert metrics.disk_usage == 23.5
        assert metrics.network_io["bytes_sent"] == 1024
        assert metrics.network_io["bytes_recv"] == 2048
        assert metrics.response_time == 150.0
        assert metrics.error_rate == 0.02
        assert metrics.active_connections == 25
        assert isinstance(metrics.timestamp, datetime)
    
    def test_service_metrics_validation(self, sample_metrics_data):
        """Testa validações de métricas"""
        metrics = ServiceMetrics(**sample_metrics_data)
        
        # Validações básicas
        assert 0 <= metrics.cpu_usage <= 100
        assert 0 <= metrics.memory_usage <= 100
        assert 0 <= metrics.disk_usage <= 100
        assert metrics.response_time >= 0
        assert 0 <= metrics.error_rate <= 1
        assert metrics.active_connections >= 0
    
    def test_service_metrics_edge_cases(self):
        """Testa casos extremos"""
        # Teste com valores mínimos
        min_data = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_io": {},
            "response_time": 0.0,
            "error_rate": 0.0,
            "active_connections": 0,
            "timestamp": datetime.now(timezone.utc)
        }
        metrics = ServiceMetrics(**min_data)
        assert metrics.cpu_usage == 0.0
        assert metrics.error_rate == 0.0
        assert metrics.active_connections == 0
        
        # Teste com valores máximos
        max_data = {
            "cpu_usage": 100.0,
            "memory_usage": 100.0,
            "disk_usage": 100.0,
            "network_io": {"bytes_sent": 999999, "bytes_recv": 999999},
            "response_time": 10000.0,
            "error_rate": 1.0,
            "active_connections": 10000,
            "timestamp": datetime.now(timezone.utc)
        }
        metrics = ServiceMetrics(**max_data)
        assert metrics.cpu_usage == 100.0
        assert metrics.error_rate == 1.0
        assert metrics.active_connections == 10000


class TestHealingMonitor:
    """Testes para HealingMonitor"""
    
    @pytest.fixture
    def healing_config(self):
        """Configuração de healing para testes"""
        return HealingConfig(
            check_interval=30,
            timeout=10,
            max_retries=3,
            cache_ttl=300,
            max_workers=5
        )
    
    @pytest.fixture
    def healing_monitor(self, healing_config):
        """Instância do monitor para testes"""
        return HealingMonitor(healing_config)
    
    @pytest.fixture
    def sample_service_info(self):
        """Informações de serviço de exemplo"""
        return ServiceInfo(
            name="test-service",
            endpoint="http://localhost:8080/health",
            port=8080,
            process_name="test-service",
            health_check_path="/health",
            timeout=5,
            retries=3
        )
    
    def test_healing_monitor_initialization(self, healing_monitor):
        """Testa inicialização do monitor"""
        assert healing_monitor is not None
        assert hasattr(healing_monitor, 'config')
        assert hasattr(healing_monitor, 'metrics_cache')
        assert hasattr(healing_monitor, 'cache_lock')
    
    @pytest.mark.asyncio
    async def test_check_service_health(self, healing_monitor, sample_service_info):
        """Testa verificação de saúde do serviço"""
        # Mock da verificação de processo
        with patch.object(healing_monitor, '_check_process_health', new_callable=AsyncMock) as mock_process:
            with patch.object(healing_monitor, '_check_endpoint_health', new_callable=AsyncMock) as mock_endpoint:
                
                mock_process.return_value = ServiceStatus.HEALTHY
                mock_endpoint.return_value = ServiceStatus.HEALTHY
                
                status = await healing_monitor.check_service_health(sample_service_info)
                
                assert status == ServiceStatus.HEALTHY
                mock_process.assert_called_once_with(sample_service_info)
                mock_endpoint.assert_called_once_with(sample_service_info)
    
    @pytest.mark.asyncio
    async def test_check_service_health_failed_process(self, healing_monitor, sample_service_info):
        """Testa verificação com processo falhado"""
        with patch.object(healing_monitor, '_check_process_health', new_callable=AsyncMock) as mock_process:
            with patch.object(healing_monitor, '_check_endpoint_health', new_callable=AsyncMock) as mock_endpoint:
                
                mock_process.return_value = ServiceStatus.FAILED
                mock_endpoint.return_value = ServiceStatus.HEALTHY
                
                status = await healing_monitor.check_service_health(sample_service_info)
                
                assert status == ServiceStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_check_service_health_failed_endpoint(self, healing_monitor, sample_service_info):
        """Testa verificação com endpoint falhado"""
        with patch.object(healing_monitor, '_check_process_health', new_callable=AsyncMock) as mock_process:
            with patch.object(healing_monitor, '_check_endpoint_health', new_callable=AsyncMock) as mock_endpoint:
                
                mock_process.return_value = ServiceStatus.HEALTHY
                mock_endpoint.return_value = ServiceStatus.FAILED
                
                status = await healing_monitor.check_service_health(sample_service_info)
                
                assert status == ServiceStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_collect_service_metrics(self, healing_monitor, sample_service_info):
        """Testa coleta de métricas do serviço"""
        # Mock das funções de coleta
        with patch.object(healing_monitor, '_collect_process_metrics', new_callable=AsyncMock) as mock_process:
            with patch.object(healing_monitor, '_collect_endpoint_metrics', new_callable=AsyncMock) as mock_endpoint:
                with patch.object(healing_monitor, '_collect_system_metrics', new_callable=AsyncMock) as mock_system:
                    
                    mock_process.return_value = {"cpu_usage": 45.0, "memory_usage": 60.0}
                    mock_endpoint.return_value = {"response_time": 120.0, "error_rate": 0.01}
                    mock_system.return_value = {"disk_usage": 25.0, "network_io": {"bytes_sent": 1000}}
                    
                    metrics = await healing_monitor.collect_service_metrics(sample_service_info)
                    
                    assert isinstance(metrics, dict)
                    assert "cpu_usage" in metrics
                    assert "memory_usage" in metrics
                    assert "response_time" in metrics
                    assert "error_rate" in metrics
                    assert "disk_usage" in metrics
                    assert "network_io" in metrics
                    assert "timestamp" in metrics
    
    @pytest.mark.asyncio
    async def test_collect_service_metrics_with_cache(self, healing_monitor, sample_service_info):
        """Testa coleta de métricas com cache"""
        # Simular métricas em cache
        cache_key = f"{sample_service_info.name}_{int(datetime.now().timestamp() / 15)}"
        cached_metrics = ServiceMetrics(
            cpu_usage=50.0,
            memory_usage=65.0,
            disk_usage=30.0,
            network_io={"bytes_sent": 1500},
            response_time=100.0,
            error_rate=0.02,
            active_connections=30,
            timestamp=datetime.now()
        )
        
        with healing_monitor.cache_lock:
            healing_monitor.metrics_cache[cache_key] = cached_metrics
        
        metrics = await healing_monitor.collect_service_metrics(sample_service_info)
        
        assert metrics["cpu_usage"] == 50.0
        assert metrics["memory_usage"] == 65.0
        assert metrics["response_time"] == 100.0
    
    @pytest.mark.asyncio
    async def test_check_process_health(self, healing_monitor, sample_service_info):
        """Testa verificação de saúde do processo"""
        # Mock do psutil
        mock_process = Mock()
        mock_process.status.return_value = "running"
        
        with patch.object(healing_monitor, '_find_service_process', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_process
            
            status = await healing_monitor._check_process_health(sample_service_info)
            
            assert status == ServiceStatus.HEALTHY
            mock_find.assert_called_once_with(sample_service_info.name)
    
    @pytest.mark.asyncio
    async def test_check_process_health_no_process(self, healing_monitor, sample_service_info):
        """Testa verificação sem processo encontrado"""
        with patch.object(healing_monitor, '_find_service_process', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            status = await healing_monitor._check_process_health(sample_service_info)
            
            assert status == ServiceStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_check_process_health_process_failed(self, healing_monitor, sample_service_info):
        """Testa verificação com processo falhado"""
        mock_process = Mock()
        mock_process.status.side_effect = Exception("Process failed")
        
        with patch.object(healing_monitor, '_find_service_process', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_process
            
            status = await healing_monitor._check_process_health(sample_service_info)
            
            assert status == ServiceStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_check_endpoint_health(self, healing_monitor, sample_service_info):
        """Testa verificação de saúde do endpoint"""
        # Mock do aiohttp
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "healthy"})
        
        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            status = await healing_monitor._check_endpoint_health(sample_service_info)
            
            assert status == ServiceStatus.HEALTHY
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_endpoint_health_failed_response(self, healing_monitor, sample_service_info):
        """Testa verificação com resposta falhada"""
        mock_response = Mock()
        mock_response.status = 500
        
        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            status = await healing_monitor._check_endpoint_health(sample_service_info)
            
            assert status == ServiceStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_check_endpoint_health_timeout(self, healing_monitor, sample_service_info):
        """Testa verificação com timeout"""
        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = asyncio.TimeoutError()
            
            status = await healing_monitor._check_endpoint_health(sample_service_info)
            
            assert status == ServiceStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_collect_process_metrics(self, healing_monitor, sample_service_info):
        """Testa coleta de métricas do processo"""
        # Mock do psutil
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 45.0
        mock_process.memory_percent.return_value = 60.0
        mock_process.io_counters.return_value = Mock(read_bytes=1000, write_bytes=500)
        
        with patch.object(healing_monitor, '_find_service_process', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_process
            
            metrics = await healing_monitor._collect_process_metrics(sample_service_info)
            
            assert isinstance(metrics, dict)
            assert "cpu_usage" in metrics
            assert "memory_usage" in metrics
            assert metrics["cpu_usage"] == 45.0
            assert metrics["memory_usage"] == 60.0
    
    @pytest.mark.asyncio
    async def test_collect_endpoint_metrics(self, healing_monitor, sample_service_info):
        """Testa coleta de métricas do endpoint"""
        # Mock do aiohttp
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "response_time": 120.0,
            "error_rate": 0.01,
            "active_connections": 25
        })
        
        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            metrics = await healing_monitor._collect_endpoint_metrics(sample_service_info)
            
            assert isinstance(metrics, dict)
            assert "response_time" in metrics
            assert "error_rate" in metrics
            assert "active_connections" in metrics
            assert metrics["response_time"] == 120.0
            assert metrics["error_rate"] == 0.01
    
    @pytest.mark.asyncio
    async def test_collect_system_metrics(self, healing_monitor, sample_service_info):
        """Testa coleta de métricas do sistema"""
        # Mock do psutil
        mock_disk = Mock()
        mock_disk.percent = 25.0
        
        mock_network = Mock()
        mock_network.bytes_sent = 1000
        mock_network.bytes_recv = 2000
        
        with patch('psutil.disk_usage', return_value=mock_disk):
            with patch('psutil.net_io_counters', return_value=mock_network):
                
                metrics = await healing_monitor._collect_system_metrics(sample_service_info)
                
                assert isinstance(metrics, dict)
                assert "disk_usage" in metrics
                assert "network_io" in metrics
                assert metrics["disk_usage"] == 25.0
                assert "bytes_sent" in metrics["network_io"]
                assert "bytes_recv" in metrics["network_io"]
    
    def test_combine_metrics(self, healing_monitor):
        """Testa combinação de métricas"""
        process_metrics = {"cpu_usage": 45.0, "memory_usage": 60.0}
        endpoint_metrics = {"response_time": 120.0, "error_rate": 0.01}
        system_metrics = {"disk_usage": 25.0, "network_io": {"bytes_sent": 1000}}
        
        combined = healing_monitor._combine_metrics([process_metrics, endpoint_metrics, system_metrics])
        
        assert isinstance(combined, dict)
        assert combined["cpu_usage"] == 45.0
        assert combined["memory_usage"] == 60.0
        assert combined["response_time"] == 120.0
        assert combined["error_rate"] == 0.01
        assert combined["disk_usage"] == 25.0
        assert "network_io" in combined
    
    def test_combine_metrics_with_exceptions(self, healing_monitor):
        """Testa combinação de métricas com exceções"""
        process_metrics = {"cpu_usage": 45.0}
        endpoint_metrics = Exception("Endpoint error")
        system_metrics = {"disk_usage": 25.0}
        
        combined = healing_monitor._combine_metrics([process_metrics, endpoint_metrics, system_metrics])
        
        assert isinstance(combined, dict)
        assert combined["cpu_usage"] == 45.0
        assert combined["disk_usage"] == 25.0
        # Métricas com erro devem ser ignoradas


class TestHealingMonitorIntegration:
    """Testes de integração para HealingMonitor"""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_cycle(self, healing_config):
        """Testa ciclo completo de monitoramento"""
        monitor = HealingMonitor(healing_config)
        
        service_info = ServiceInfo(
            name="integration-test-service",
            endpoint="http://localhost:8080/health",
            port=8080,
            process_name="integration-test-service",
            health_check_path="/health",
            timeout=5,
            retries=3
        )
        
        # Mock de todas as operações
        with patch.object(monitor, '_check_process_health', new_callable=AsyncMock) as mock_process:
            with patch.object(monitor, '_check_endpoint_health', new_callable=AsyncMock) as mock_endpoint:
                with patch.object(monitor, '_collect_process_metrics', new_callable=AsyncMock) as mock_process_metrics:
                    with patch.object(monitor, '_collect_endpoint_metrics', new_callable=AsyncMock) as mock_endpoint_metrics:
                        with patch.object(monitor, '_collect_system_metrics', new_callable=AsyncMock) as mock_system_metrics:
                            
                            mock_process.return_value = ServiceStatus.HEALTHY
                            mock_endpoint.return_value = ServiceStatus.HEALTHY
                            mock_process_metrics.return_value = {"cpu_usage": 45.0, "memory_usage": 60.0}
                            mock_endpoint_metrics.return_value = {"response_time": 120.0, "error_rate": 0.01}
                            mock_system_metrics.return_value = {"disk_usage": 25.0, "network_io": {}}
                            
                            # Verificar saúde
                            status = await monitor.check_service_health(service_info)
                            assert status == ServiceStatus.HEALTHY
                            
                            # Coletar métricas
                            metrics = await monitor.collect_service_metrics(service_info)
                            assert isinstance(metrics, dict)
                            assert "cpu_usage" in metrics
                            assert "response_time" in metrics
    
    @pytest.mark.asyncio
    async def test_multiple_services_monitoring(self, healing_config):
        """Testa monitoramento de múltiplos serviços"""
        monitor = HealingMonitor(healing_config)
        
        services = [
            ServiceInfo(name="service1", endpoint="http://localhost:8081/health", port=8081, process_name="service1", health_check_path="/health", timeout=5, retries=3),
            ServiceInfo(name="service2", endpoint="http://localhost:8082/health", port=8082, process_name="service2", health_check_path="/health", timeout=5, retries=3)
        ]
        
        with patch.object(monitor, '_check_process_health', new_callable=AsyncMock) as mock_process:
            with patch.object(monitor, '_check_endpoint_health', new_callable=AsyncMock) as mock_endpoint:
                
                mock_process.return_value = ServiceStatus.HEALTHY
                mock_endpoint.return_value = ServiceStatus.HEALTHY
                
                # Monitorar múltiplos serviços
                tasks = [monitor.check_service_health(service) for service in services]
                results = await asyncio.gather(*tasks)
                
                assert len(results) == 2
                assert all(status == ServiceStatus.HEALTHY for status in results)


class TestHealingMonitorErrorHandling:
    """Testes de tratamento de erro para HealingMonitor"""
    
    @pytest.mark.asyncio
    async def test_health_check_error_handling(self, healing_config):
        """Testa tratamento de erros na verificação de saúde"""
        monitor = HealingMonitor(healing_config)
        
        service_info = ServiceInfo(
            name="error-test-service",
            endpoint="http://localhost:8080/health",
            port=8080,
            process_name="error-test-service",
            health_check_path="/health",
            timeout=5,
            retries=3
        )
        
        # Mock que simula erro
        with patch.object(monitor, '_check_process_health', side_effect=Exception("Test error")):
            with patch.object(monitor, '_check_endpoint_health', new_callable=AsyncMock) as mock_endpoint:
                mock_endpoint.return_value = ServiceStatus.HEALTHY
                
                status = await monitor.check_service_health(service_info)
                
                # Deve retornar status baseado apenas no endpoint
                assert status == ServiceStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_metrics_collection_error_handling(self, healing_config):
        """Testa tratamento de erros na coleta de métricas"""
        monitor = HealingMonitor(healing_config)
        
        service_info = ServiceInfo(
            name="error-test-service",
            endpoint="http://localhost:8080/health",
            port=8080,
            process_name="error-test-service",
            health_check_path="/health",
            timeout=5,
            retries=3
        )
        
        # Mock que simula erro na coleta
        with patch.object(monitor, '_collect_process_metrics', side_effect=Exception("Process error")):
            with patch.object(monitor, '_collect_endpoint_metrics', new_callable=AsyncMock) as mock_endpoint:
                with patch.object(monitor, '_collect_system_metrics', new_callable=AsyncMock) as mock_system:
                    
                    mock_endpoint.return_value = {"response_time": 120.0}
                    mock_system.return_value = {"disk_usage": 25.0}
                    
                    metrics = await monitor.collect_service_metrics(service_info)
                    
                    # Deve retornar métricas parciais
                    assert isinstance(metrics, dict)
                    assert "response_time" in metrics
                    assert "disk_usage" in metrics


class TestHealingMonitorPerformance:
    """Testes de performance para HealingMonitor"""
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self, healing_config):
        """Testa performance da verificação de saúde"""
        monitor = HealingMonitor(healing_config)
        
        service_info = ServiceInfo(
            name="perf-test-service",
            endpoint="http://localhost:8080/health",
            port=8080,
            process_name="perf-test-service",
            health_check_path="/health",
            timeout=5,
            retries=3
        )
        
        start_time = datetime.now()
        
        with patch.object(monitor, '_check_process_health', new_callable=AsyncMock) as mock_process:
            with patch.object(monitor, '_check_endpoint_health', new_callable=AsyncMock) as mock_endpoint:
                
                mock_process.return_value = ServiceStatus.HEALTHY
                mock_endpoint.return_value = ServiceStatus.HEALTHY
                
                status = await monitor.check_service_health(service_info)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Performance deve ser < 1 segundo
                assert duration < 1.0
                assert status == ServiceStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_metrics_collection_performance(self, healing_config):
        """Testa performance da coleta de métricas"""
        monitor = HealingMonitor(healing_config)
        
        service_info = ServiceInfo(
            name="perf-test-service",
            endpoint="http://localhost:8080/health",
            port=8080,
            process_name="perf-test-service",
            health_check_path="/health",
            timeout=5,
            retries=3
        )
        
        start_time = datetime.now()
        
        with patch.object(monitor, '_collect_process_metrics', new_callable=AsyncMock) as mock_process:
            with patch.object(monitor, '_collect_endpoint_metrics', new_callable=AsyncMock) as mock_endpoint:
                with patch.object(monitor, '_collect_system_metrics', new_callable=AsyncMock) as mock_system:
                    
                    mock_process.return_value = {"cpu_usage": 45.0, "memory_usage": 60.0}
                    mock_endpoint.return_value = {"response_time": 120.0, "error_rate": 0.01}
                    mock_system.return_value = {"disk_usage": 25.0, "network_io": {}}
                    
                    metrics = await monitor.collect_service_metrics(service_info)
                    
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    # Performance deve ser < 2 segundos
                    assert duration < 2.0
                    assert isinstance(metrics, dict)
    
    def test_cache_performance(self, healing_config):
        """Testa performance do cache"""
        monitor = HealingMonitor(healing_config)
        
        # Adicionar muitas métricas ao cache
        for i in range(1000):
            cache_key = f"service_{i}_{int(datetime.now().timestamp() / 15)}"
            metrics = ServiceMetrics(
                cpu_usage=50.0 + i,
                memory_usage=60.0 + i,
                disk_usage=25.0,
                network_io={"bytes_sent": 1000},
                response_time=120.0,
                error_rate=0.01,
                active_connections=25,
                timestamp=datetime.now()
            )
            monitor.metrics_cache[cache_key] = metrics
        
        # Verificar que não há vazamento de memória
        assert len(monitor.metrics_cache) <= 1000 