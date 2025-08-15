"""
Testes Unitários para Health Checks
Sistema de Verificações de Saúde - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de health checks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import time
from typing import Dict, Any

from backend.app.monitoring.health_checks import (
    HealthChecker,
    HealthStatus,
    HealthCheckResult,
    DatabaseHealthCheck,
    CacheHealthCheck,
    ExternalServiceHealthCheck,
    ApplicationHealthCheck,
    setup_health_checks,
    get_health_status,
    get_health_status_simple
)


class TestHealthStatus:
    """Testes para enum HealthStatus"""
    
    def test_health_status_values(self):
        """Testa valores do enum HealthStatus"""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestHealthCheckResult:
    """Testes para classe HealthCheckResult"""
    
    def test_health_check_result_creation(self):
        """Testa criação de resultado de health check"""
        timestamp = datetime.now()
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY,
            response_time=0.5,
            details={"test": "data"},
            timestamp=timestamp,
            error_message=None
        )
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time == 0.5
        assert result.details == {"test": "data"}
        assert result.timestamp == timestamp
        assert result.error_message is None
    
    def test_health_check_result_with_error(self):
        """Testa criação de resultado com erro"""
        result = HealthCheckResult(
            name="failed_check",
            status=HealthStatus.UNHEALTHY,
            response_time=1.0,
            details={},
            timestamp=datetime.now(),
            error_message="Connection failed"
        )
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error_message == "Connection failed"


class TestHealthChecker:
    """Testes para classe HealthChecker"""
    
    @pytest.fixture
    def health_checker(self):
        """Instância do HealthChecker para testes"""
        return HealthChecker()
    
    def test_health_checker_initialization(self, health_checker):
        """Testa inicialização do HealthChecker"""
        assert health_checker.checks == {}
        assert health_checker.results_cache == {}
        assert health_checker.cache_ttl == 30
    
    def test_register_check(self, health_checker):
        """Testa registro de health check"""
        async def test_check():
            return {"status": "ok"}
        
        health_checker.register_check("test_check", test_check)
        
        assert "test_check" in health_checker.checks
        assert health_checker.checks["test_check"] == test_check
    
    @pytest.mark.asyncio
    async def test_run_check_success(self, health_checker):
        """Testa execução de health check com sucesso"""
        async def test_check():
            return {"status": "ok", "data": "test"}
        
        health_checker.register_check("test_check", test_check)
        
        result = await health_checker.run_check("test_check")
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.details == {"status": "ok", "data": "test"}
        assert result.error_message is None
        assert isinstance(result.response_time, float)
        assert isinstance(result.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_run_check_failure(self, health_checker):
        """Testa execução de health check com falha"""
        async def failing_check():
            raise Exception("Test error")
        
        health_checker.register_check("failing_check", failing_check)
        
        result = await health_checker.run_check("failing_check")
        
        assert result.name == "failing_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error_message == "Test error"
        assert result.details == {}
    
    @pytest.mark.asyncio
    async def test_run_check_nonexistent(self, health_checker):
        """Testa execução de health check inexistente"""
        with pytest.raises(ValueError, match="Health check 'nonexistent' não encontrado"):
            await health_checker.run_check("nonexistent")
    
    @pytest.mark.asyncio
    async def test_run_all_checks(self, health_checker):
        """Testa execução de todos os health checks"""
        async def success_check():
            return {"status": "ok"}
        
        async def failing_check():
            raise Exception("Test error")
        
        health_checker.register_check("success_check", success_check)
        health_checker.register_check("failing_check", failing_check)
        
        results = await health_checker.run_all_checks()
        
        assert len(results) == 2
        assert results["success_check"].status == HealthStatus.HEALTHY
        assert results["failing_check"].status == HealthStatus.UNHEALTHY
    
    def test_get_overall_status_empty(self, health_checker):
        """Testa status geral com cache vazio"""
        status = health_checker.get_overall_status()
        assert status == HealthStatus.UNKNOWN
    
    def test_get_overall_status_all_healthy(self, health_checker):
        """Testa status geral com todos os checks saudáveis"""
        health_checker.results_cache = {
            "check1": HealthCheckResult("check1", HealthStatus.HEALTHY, 0.1, {}, datetime.now()),
            "check2": HealthCheckResult("check2", HealthStatus.HEALTHY, 0.2, {}, datetime.now())
        }
        
        status = health_checker.get_overall_status()
        assert status == HealthStatus.HEALTHY
    
    def test_get_overall_status_degraded(self, health_checker):
        """Testa status geral com alguns checks degradados"""
        health_checker.results_cache = {
            "check1": HealthCheckResult("check1", HealthStatus.HEALTHY, 0.1, {}, datetime.now()),
            "check2": HealthCheckResult("check2", HealthStatus.DEGRADED, 0.2, {}, datetime.now())
        }
        
        status = health_checker.get_overall_status()
        assert status == HealthStatus.DEGRADED
    
    def test_get_overall_status_unhealthy(self, health_checker):
        """Testa status geral com checks não saudáveis"""
        health_checker.results_cache = {
            "check1": HealthCheckResult("check1", HealthStatus.HEALTHY, 0.1, {}, datetime.now()),
            "check2": HealthCheckResult("check2", HealthStatus.UNHEALTHY, 0.2, {}, datetime.now())
        }
        
        status = health_checker.get_overall_status()
        assert status == HealthStatus.UNHEALTHY


class TestDatabaseHealthCheck:
    """Testes para DatabaseHealthCheck"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock da sessão do banco de dados"""
        session_mock = Mock()
        session_mock.execute = AsyncMock()
        session_mock.bind = Mock()
        session_mock.bind.pool_size = 10
        return session_mock
    
    @pytest.fixture
    def db_health_check(self, mock_db_session):
        """Instância do DatabaseHealthCheck para testes"""
        return DatabaseHealthCheck(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_check_database_connection_success(self, db_health_check, mock_db_session):
        """Testa verificação de conexão com banco com sucesso"""
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)
        mock_db_session.execute.return_value = mock_result
        
        result = await db_health_check.check_database_connection()
        
        assert result["connected"] is True
        assert result["database_type"] == "postgresql"
        assert result["connection_pool_size"] == 10
    
    @pytest.mark.asyncio
    async def test_check_database_connection_failure(self, db_health_check, mock_db_session):
        """Testa verificação de conexão com banco com falha"""
        mock_db_session.execute.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Falha na conexão com banco"):
            await db_health_check.check_database_connection()
    
    @pytest.mark.asyncio
    async def test_check_database_performance_success(self, db_health_check, mock_db_session):
        """Testa verificação de performance do banco com sucesso"""
        mock_result = Mock()
        mock_result.scalar.return_value = 50
        mock_db_session.execute.return_value = mock_result
        
        result = await db_health_check.check_database_performance()
        
        assert "response_time" in result
        assert result["table_count"] == 50
        assert "performance_status" in result
    
    @pytest.mark.asyncio
    async def test_check_database_performance_failure(self, db_health_check, mock_db_session):
        """Testa verificação de performance do banco com falha"""
        mock_db_session.execute.side_effect = Exception("Performance test failed")
        
        with pytest.raises(Exception, match="Falha no teste de performance"):
            await db_health_check.check_database_performance()


class TestCacheHealthCheck:
    """Testes para CacheHealthCheck"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.ping = Mock()
        redis_mock.info = Mock()
        redis_mock.set = Mock()
        redis_mock.get = Mock()
        redis_mock.delete = Mock()
        return redis_mock
    
    @pytest.fixture
    def cache_health_check(self, mock_redis_client):
        """Instância do CacheHealthCheck para testes"""
        return CacheHealthCheck(mock_redis_client)
    
    @pytest.mark.asyncio
    async def test_check_cache_connection_success(self, cache_health_check, mock_redis_client):
        """Testa verificação de conexão com cache com sucesso"""
        mock_redis_client.info.return_value = {
            "redis_version": "6.0.0",
            "used_memory_human": "1.0M",
            "connected_clients": 5
        }
        
        result = await cache_health_check.check_cache_connection()
        
        assert result["connected"] is True
        assert result["redis_version"] == "6.0.0"
        assert result["used_memory"] == "1.0M"
        assert result["connected_clients"] == 5
    
    @pytest.mark.asyncio
    async def test_check_cache_connection_failure(self, cache_health_check, mock_redis_client):
        """Testa verificação de conexão com cache com falha"""
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")
        
        with pytest.raises(Exception, match="Falha na conexão com Redis"):
            await cache_health_check.check_cache_connection()
    
    @pytest.mark.asyncio
    async def test_check_cache_performance_success(self, cache_health_check, mock_redis_client):
        """Testa verificação de performance do cache com sucesso"""
        mock_redis_client.get.return_value = b"test_value"
        
        result = await cache_health_check.check_cache_performance()
        
        assert "response_time" in result
        assert result["write_success"] is True
        assert result["read_success"] is True
        assert "performance_status" in result
    
    @pytest.mark.asyncio
    async def test_check_cache_performance_failure(self, cache_health_check, mock_redis_client):
        """Testa verificação de performance do cache com falha"""
        mock_redis_client.set.side_effect = Exception("Redis operation failed")
        
        with pytest.raises(Exception, match="Falha no teste de performance do cache"):
            await cache_health_check.check_cache_performance()


class TestExternalServiceHealthCheck:
    """Testes para ExternalServiceHealthCheck"""
    
    @pytest.fixture
    def external_health_check(self):
        """Instância do ExternalServiceHealthCheck para testes"""
        return ExternalServiceHealthCheck()
    
    @pytest.mark.asyncio
    async def test_check_google_analytics_api_success(self, external_health_check):
        """Testa verificação da API do Google Analytics com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await external_health_check.check_google_analytics_api()
            
            assert result["service"] == "google_analytics"
            assert result["status"] == "available"
            assert result["response_time"] == 0.5
    
    @pytest.mark.asyncio
    async def test_check_google_analytics_api_failure(self, external_health_check):
        """Testa verificação da API do Google Analytics com falha"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")
            
            with pytest.raises(Exception, match="Falha na verificação do Google Analytics"):
                await external_health_check.check_google_analytics_api()
    
    @pytest.mark.asyncio
    async def test_check_search_console_api_success(self, external_health_check):
        """Testa verificação da API do Search Console com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.3
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await external_health_check.check_search_console_api()
            
            assert result["service"] == "search_console"
            assert result["status"] == "available"
            assert result["response_time"] == 0.3
    
    @pytest.mark.asyncio
    async def test_check_serp_api_success(self, external_health_check):
        """Testa verificação da SERP API com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.8
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await external_health_check.check_serp_api()
            
            assert result["service"] == "serp_api"
            assert result["status"] == "available"
            assert result["response_time"] == 0.8


class TestApplicationHealthCheck:
    """Testes para ApplicationHealthCheck"""
    
    @pytest.fixture
    def app_health_check(self):
        """Instância do ApplicationHealthCheck para testes"""
        return ApplicationHealthCheck()
    
    @pytest.mark.asyncio
    async def test_check_memory_usage_success(self, app_health_check):
        """Testa verificação de uso de memória com sucesso"""
        mock_process = Mock()
        mock_process.memory_info.return_value.rss = 1024 * 1024 * 100  # 100MB
        mock_process.memory_percent.return_value = 25.5
        mock_process.cpu_percent.return_value = 15.2
        mock_process.num_threads.return_value = 8
        
        with patch('psutil.Process', return_value=mock_process):
            result = await app_health_check.check_memory_usage()
            
            assert result["memory_usage_mb"] == 100.0
            assert result["memory_percent"] == 25.5
            assert result["cpu_percent"] == 15.2
            assert result["thread_count"] == 8
    
    @pytest.mark.asyncio
    async def test_check_memory_usage_failure(self, app_health_check):
        """Testa verificação de uso de memória com falha"""
        with patch('psutil.Process', side_effect=Exception("Process error")):
            with pytest.raises(Exception, match="Falha na verificação de memória"):
                await app_health_check.check_memory_usage()
    
    @pytest.mark.asyncio
    async def test_check_disk_space_success(self, app_health_check):
        """Testa verificação de espaço em disco com sucesso"""
        mock_disk_usage = Mock()
        mock_disk_usage.total = 1024 * 1024 * 1024 * 100  # 100GB
        mock_disk_usage.used = 1024 * 1024 * 1024 * 70    # 70GB
        mock_disk_usage.free = 1024 * 1024 * 1024 * 30    # 30GB
        mock_disk_usage.percent = 70.0
        
        with patch('psutil.disk_usage', return_value=mock_disk_usage):
            result = await app_health_check.check_disk_space()
            
            assert result["total_gb"] == 100.0
            assert result["used_gb"] == 70.0
            assert result["free_gb"] == 30.0
            assert result["usage_percent"] == 70.0
    
    @pytest.mark.asyncio
    async def test_check_disk_space_failure(self, app_health_check):
        """Testa verificação de espaço em disco com falha"""
        with patch('psutil.disk_usage', side_effect=Exception("Disk error")):
            with pytest.raises(Exception, match="Falha na verificação de disco"):
                await app_health_check.check_disk_space()


class TestHealthChecksIntegration:
    """Testes de integração para sistema de health checks"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock da sessão do banco de dados"""
        session_mock = Mock()
        session_mock.execute = AsyncMock()
        session_mock.bind = Mock()
        session_mock.bind.pool_size = 10
        return session_mock
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock do cliente Redis"""
        redis_mock = Mock()
        redis_mock.ping = Mock()
        redis_mock.info = Mock()
        redis_mock.set = Mock()
        redis_mock.get = Mock()
        redis_mock.delete = Mock()
        return redis_mock
    
    def test_setup_health_checks(self, mock_db_session, mock_redis_client):
        """Testa configuração dos health checks"""
        with patch('backend.app.monitoring.health_checks.health_checker') as mock_health_checker:
            setup_health_checks(mock_db_session, mock_redis_client)
            
            # Verifica se os checks foram registrados
            assert mock_health_checker.register_check.call_count == 8
    
    @pytest.mark.asyncio
    async def test_get_health_status_success(self, mock_db_session, mock_redis_client):
        """Testa obtenção de status de saúde com sucesso"""
        with patch('backend.app.monitoring.health_checks.health_checker') as mock_health_checker:
            # Mock dos resultados
            mock_results = {
                "database_connection": HealthCheckResult(
                    "database_connection", HealthStatus.HEALTHY, 0.1, {"connected": True}, datetime.now()
                ),
                "cache_connection": HealthCheckResult(
                    "cache_connection", HealthStatus.HEALTHY, 0.05, {"connected": True}, datetime.now()
                )
            }
            
            mock_health_checker.run_all_checks = AsyncMock(return_value=mock_results)
            mock_health_checker.get_overall_status.return_value = HealthStatus.HEALTHY
            
            result = await get_health_status()
            
            assert result["status"] == "healthy"
            assert "timestamp" in result
            assert "checks" in result
            assert len(result["checks"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_health_status_error(self, mock_db_session, mock_redis_client):
        """Testa obtenção de status de saúde com erro"""
        with patch('backend.app.monitoring.health_checks.health_checker') as mock_health_checker:
            mock_health_checker.run_all_checks.side_effect = Exception("Health check error")
            
            with pytest.raises(Exception):
                await get_health_status()
    
    @pytest.mark.asyncio
    async def test_get_health_status_simple_success(self, mock_db_session, mock_redis_client):
        """Testa obtenção de status de saúde simples com sucesso"""
        with patch('backend.app.monitoring.health_checks.health_checker') as mock_health_checker:
            mock_health_checker.get_overall_status.return_value = HealthStatus.HEALTHY
            
            result = await get_health_status_simple()
            
            assert result["status"] == "healthy"
            assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_get_health_status_simple_error(self, mock_db_session, mock_redis_client):
        """Testa obtenção de status de saúde simples com erro"""
        with patch('backend.app.monitoring.health_checks.health_checker') as mock_health_checker:
            mock_health_checker.get_overall_status.side_effect = Exception("Health check error")
            
            result = await get_health_status_simple()
            
            assert result["status"] == "unhealthy"
            assert "error" in result


class TestHealthChecksErrorHandling:
    """Testes de tratamento de erros para health checks"""
    
    @pytest.mark.asyncio
    async def test_health_checker_exception_handling(self):
        """Testa tratamento de exceções no health checker"""
        health_checker = HealthChecker()
        
        async def exception_check():
            raise Exception("Test exception")
        
        health_checker.register_check("exception_check", exception_check)
        
        result = await health_checker.run_check("exception_check")
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error_message == "Test exception"
    
    @pytest.mark.asyncio
    async def test_run_all_checks_with_exceptions(self):
        """Testa execução de todos os checks com exceções"""
        health_checker = HealthChecker()
        
        async def success_check():
            return {"status": "ok"}
        
        async def exception_check():
            raise Exception("Test exception")
        
        health_checker.register_check("success_check", success_check)
        health_checker.register_check("exception_check", exception_check)
        
        results = await health_checker.run_all_checks()
        
        assert results["success_check"].status == HealthStatus.HEALTHY
        assert results["exception_check"].status == HealthStatus.UNHEALTHY


class TestHealthChecksPerformance:
    """Testes de performance para health checks"""
    
    @pytest.mark.asyncio
    async def test_health_check_response_time(self):
        """Testa tempo de resposta dos health checks"""
        health_checker = HealthChecker()
        
        async def slow_check():
            await asyncio.sleep(0.1)
            return {"status": "ok"}
        
        health_checker.register_check("slow_check", slow_check)
        
        start_time = time.time()
        result = await health_checker.run_check("slow_check")
        end_time = time.time()
        
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time >= 0.1
        assert end_time - start_time >= 0.1
    
    @pytest.mark.asyncio
    async def test_multiple_health_checks_performance(self):
        """Testa performance de múltiplos health checks"""
        health_checker = HealthChecker()
        
        async def fast_check():
            return {"status": "ok"}
        
        # Registra múltiplos checks
        for i in range(10):
            health_checker.register_check(f"check_{i}", fast_check)
        
        start_time = time.time()
        results = await health_checker.run_all_checks()
        end_time = time.time()
        
        assert len(results) == 10
        assert end_time - start_time < 1.0  # Deve ser rápido


if __name__ == "__main__":
    pytest.main([__file__]) 