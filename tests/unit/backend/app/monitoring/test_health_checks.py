"""
Testes Unitários para HealthChecks
HealthChecks - Sistema de verificação de saúde de componentes

Prompt: Implementação de testes unitários para HealthChecks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_HEALTH_CHECKS_20250127_001
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

from backend.app.monitoring.health_checks import (
    HealthStatus,
    HealthCheckResult,
    HealthChecker
)


class TestHealthStatus:
    """Testes para HealthStatus (Enum)"""
    
    def test_enum_values(self):
        """Testa valores do enum HealthStatus"""
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        assert HealthStatus.DEGRADED == "degraded"
        assert HealthStatus.UNKNOWN == "unknown"
    
    def test_enum_membership(self):
        """Testa pertencimento ao enum"""
        assert "healthy" in HealthStatus
        assert "unhealthy" in HealthStatus
        assert "degraded" in HealthStatus
        assert "unknown" in HealthStatus
        assert "invalid_status" not in HealthStatus


class TestHealthCheckResult:
    """Testes para HealthCheckResult"""
    
    @pytest.fixture
    def sample_result_data(self):
        """Dados de exemplo para HealthCheckResult"""
        return {
            "name": "database_connection",
            "status": HealthStatus.HEALTHY,
            "response_time": 0.15,
            "details": {"connections": 5, "max_connections": 100},
            "timestamp": datetime.now(),
            "error_message": None
        }
    
    @pytest.fixture
    def result(self, sample_result_data):
        """Instância de HealthCheckResult para testes"""
        return HealthCheckResult(**sample_result_data)
    
    def test_initialization(self, sample_result_data):
        """Testa inicialização básica"""
        result = HealthCheckResult(**sample_result_data)
        
        assert result.name == "database_connection"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time == 0.15
        assert result.details == {"connections": 5, "max_connections": 100}
        assert result.timestamp == sample_result_data["timestamp"]
        assert result.error_message is None
    
    def test_default_values(self):
        """Testa valores padrão"""
        result = HealthCheckResult(
            name="test_check",
            status=HealthStatus.HEALTHY
        )
        
        assert result.response_time == 0.0
        assert result.details == {}
        assert result.timestamp is None
        assert result.error_message is None
    
    def test_healthy_result(self):
        """Testa resultado saudável"""
        result = HealthCheckResult(
            name="healthy_check",
            status=HealthStatus.HEALTHY,
            response_time=0.1,
            details={"metric": "value"}
        )
        
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time == 0.1
        assert result.details == {"metric": "value"}
        assert result.error_message is None
    
    def test_unhealthy_result(self):
        """Testa resultado não saudável"""
        result = HealthCheckResult(
            name="unhealthy_check",
            status=HealthStatus.UNHEALTHY,
            response_time=5.0,
            details={},
            error_message="Connection timeout"
        )
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.response_time == 5.0
        assert result.error_message == "Connection timeout"
    
    def test_degraded_result(self):
        """Testa resultado degradado"""
        result = HealthCheckResult(
            name="degraded_check",
            status=HealthStatus.DEGRADED,
            response_time=2.5,
            details={"warning": "High latency"}
        )
        
        assert result.status == HealthStatus.DEGRADED
        assert result.response_time == 2.5
        assert result.details == {"warning": "High latency"}
    
    def test_unknown_result(self):
        """Testa resultado desconhecido"""
        result = HealthCheckResult(
            name="unknown_check",
            status=HealthStatus.UNKNOWN,
            response_time=0.0
        )
        
        assert result.status == HealthStatus.UNKNOWN
        assert result.response_time == 0.0


class TestHealthChecker:
    """Testes para HealthChecker"""
    
    @pytest.fixture
    def health_checker(self):
        """Instância de HealthChecker para testes"""
        return HealthChecker()
    
    @pytest.fixture
    def mock_check_function(self):
        """Função de check mock"""
        return Mock(return_value={"status": "ok", "connections": 5})
    
    @pytest.fixture
    def async_mock_check_function(self):
        """Função de check async mock"""
        async def async_check():
            return {"status": "ok", "connections": 5}
        return async_check
    
    def test_initialization(self):
        """Testa inicialização do HealthChecker"""
        checker = HealthChecker()
        
        assert checker.checks == {}
        assert checker.results_cache == {}
        assert checker.cache_ttl == 30
    
    def test_register_check(self, health_checker, mock_check_function):
        """Testa registro de health check"""
        health_checker.register_check("test_check", mock_check_function)
        
        assert "test_check" in health_checker.checks
        assert health_checker.checks["test_check"] == mock_check_function
    
    def test_register_duplicate_check(self, health_checker, mock_check_function):
        """Testa registro de check duplicado"""
        health_checker.register_check("test_check", mock_check_function)
        health_checker.register_check("test_check", mock_check_function)  # Sobrescreve
        
        assert len(health_checker.checks) == 1
        assert "test_check" in health_checker.checks
    
    def test_register_invalid_check(self, health_checker):
        """Testa registro de check inválido"""
        with pytest.raises(ValueError):
            health_checker.register_check("test_check", None)
    
    @pytest.mark.asyncio
    async def test_run_check_success(self, health_checker, mock_check_function):
        """Testa execução bem-sucedida de health check"""
        health_checker.register_check("test_check", mock_check_function)
        
        result = await health_checker.run_check("test_check")
        
        assert result is not None
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time > 0
        assert result.details == {"status": "ok", "connections": 5}
        assert result.error_message is None
        
        mock_check_function.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_check_not_found(self, health_checker):
        """Testa execução de check não encontrado"""
        with pytest.raises(ValueError, match="Health check 'nonexistent' not found"):
            await health_checker.run_check("nonexistent")
    
    @pytest.mark.asyncio
    async def test_run_check_exception(self, health_checker):
        """Testa execução de check com exceção"""
        def failing_check():
            raise Exception("Check failed")
        
        health_checker.register_check("failing_check", failing_check)
        
        result = await health_checker.run_check("failing_check")
        
        assert result is not None
        assert result.name == "failing_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.response_time > 0
        assert result.error_message == "Check failed"
    
    @pytest.mark.asyncio
    async def test_run_check_timeout(self, health_checker):
        """Testa execução de check com timeout"""
        async def slow_check():
            await asyncio.sleep(2.0)  # Mais que o timeout padrão
            return {"status": "ok"}
        
        health_checker.register_check("slow_check", slow_check)
        
        result = await health_checker.run_check("slow_check")
        
        assert result is not None
        assert result.name == "slow_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert "timeout" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_run_all_checks(self, health_checker):
        """Testa execução de todos os checks"""
        def check1():
            return {"status": "ok"}
        
        def check2():
            return {"connections": 10}
        
        health_checker.register_check("check1", check1)
        health_checker.register_check("check2", check2)
        
        results = await health_checker.run_all_checks()
        
        assert len(results) == 2
        assert "check1" in results
        assert "check2" in results
        assert results["check1"].status == HealthStatus.HEALTHY
        assert results["check2"].status == HealthStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_run_all_checks_with_failures(self, health_checker):
        """Testa execução de todos os checks com falhas"""
        def healthy_check():
            return {"status": "ok"}
        
        def failing_check():
            raise Exception("Failed")
        
        health_checker.register_check("healthy", healthy_check)
        health_checker.register_check("failing", failing_check)
        
        results = await health_checker.run_all_checks()
        
        assert len(results) == 2
        assert results["healthy"].status == HealthStatus.HEALTHY
        assert results["failing"].status == HealthStatus.UNHEALTHY
        assert "Failed" in results["failing"].error_message
    
    def test_get_cached_result(self, health_checker):
        """Testa obtenção de resultado em cache"""
        cached_result = HealthCheckResult(
            name="cached_check",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now()
        )
        
        health_checker.results_cache["cached_check"] = cached_result
        
        result = health_checker.get_cached_result("cached_check")
        assert result == cached_result
    
    def test_get_cached_result_not_found(self, health_checker):
        """Testa obtenção de resultado não encontrado em cache"""
        result = health_checker.get_cached_result("nonexistent")
        assert result is None
    
    def test_get_cached_result_expired(self, health_checker):
        """Testa obtenção de resultado expirado em cache"""
        expired_result = HealthCheckResult(
            name="expired_check",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now() - timedelta(seconds=60)  # Mais que TTL
        )
        
        health_checker.results_cache["expired_check"] = expired_result
        
        result = health_checker.get_cached_result("expired_check")
        assert result is None  # Deve retornar None para cache expirado
    
    def test_clear_cache(self, health_checker):
        """Testa limpeza do cache"""
        # Adicionar alguns resultados ao cache
        result1 = HealthCheckResult(name="check1", status=HealthStatus.HEALTHY)
        result2 = HealthCheckResult(name="check2", status=HealthStatus.HEALTHY)
        
        health_checker.results_cache["check1"] = result1
        health_checker.results_cache["check2"] = result2
        
        assert len(health_checker.results_cache) == 2
        
        health_checker.clear_cache()
        
        assert len(health_checker.results_cache) == 0
    
    def test_get_cache_stats(self, health_checker):
        """Testa obtenção de estatísticas do cache"""
        # Adicionar alguns resultados ao cache
        recent_result = HealthCheckResult(
            name="recent",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now()
        )
        expired_result = HealthCheckResult(
            name="expired",
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now() - timedelta(seconds=60)
        )
        
        health_checker.results_cache["recent"] = recent_result
        health_checker.results_cache["expired"] = expired_result
        
        stats = health_checker.get_cache_stats()
        
        assert "total_entries" in stats
        assert "valid_entries" in stats
        assert "expired_entries" in stats
        assert stats["total_entries"] == 2
        assert stats["valid_entries"] == 1
        assert stats["expired_entries"] == 1


class TestHealthCheckerIntegration:
    """Testes de integração para HealthChecker"""
    
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Testa health check de banco de dados"""
        checker = HealthChecker()
        
        def database_check():
            # Simular verificação de banco de dados
            return {
                "connections": 5,
                "max_connections": 100,
                "response_time": 0.05,
                "status": "connected"
            }
        
        checker.register_check("database", database_check)
        
        result = await checker.run_check("database")
        
        assert result.name == "database"
        assert result.status == HealthStatus.HEALTHY
        assert result.details["connections"] == 5
        assert result.details["max_connections"] == 100
    
    @pytest.mark.asyncio
    async def test_cache_health_check(self):
        """Testa health check de cache"""
        checker = HealthChecker()
        
        def cache_check():
            # Simular verificação de cache
            return {
                "hit_rate": 0.85,
                "memory_usage": "512MB",
                "keys": 10000,
                "status": "operational"
            }
        
        checker.register_check("cache", cache_check)
        
        result = await checker.run_check("cache")
        
        assert result.name == "cache"
        assert result.status == HealthStatus.HEALTHY
        assert result.details["hit_rate"] == 0.85
        assert result.details["keys"] == 10000
    
    @pytest.mark.asyncio
    async def test_external_service_health_check(self):
        """Testa health check de serviço externo"""
        checker = HealthChecker()
        
        async def external_service_check():
            # Simular verificação de serviço externo
            await asyncio.sleep(0.1)  # Simular latência de rede
            return {
                "endpoint": "https://api.example.com/health",
                "response_time": 150,
                "status_code": 200,
                "status": "available"
            }
        
        checker.register_check("external_service", external_service_check)
        
        result = await checker.run_check("external_service")
        
        assert result.name == "external_service"
        assert result.status == HealthStatus.HEALTHY
        assert result.details["status_code"] == 200
        assert result.details["status"] == "available"
    
    @pytest.mark.asyncio
    async def test_application_health_check(self):
        """Testa health check da aplicação"""
        checker = HealthChecker()
        
        def application_check():
            # Simular verificação da aplicação
            import psutil
            
            return {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "uptime": time.time(),
                "status": "running"
            }
        
        checker.register_check("application", application_check)
        
        result = await checker.run_check("application")
        
        assert result.name == "application"
        assert result.status == HealthStatus.HEALTHY
        assert "cpu_usage" in result.details
        assert "memory_usage" in result.details
        assert "disk_usage" in result.details
        assert result.details["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_check(self):
        """Testa verificação de saúde abrangente"""
        checker = HealthChecker()
        
        # Registrar múltiplos checks
        def db_check():
            return {"connections": 5, "status": "ok"}
        
        def cache_check():
            return {"hit_rate": 0.9, "status": "ok"}
        
        def api_check():
            return {"endpoints": 10, "status": "ok"}
        
        checker.register_check("database", db_check)
        checker.register_check("cache", cache_check)
        checker.register_check("api", api_check)
        
        # Executar todos os checks
        results = await checker.run_all_checks()
        
        assert len(results) == 3
        assert all(result.status == HealthStatus.HEALTHY for result in results.values())
        
        # Verificar cache
        cached_db = checker.get_cached_result("database")
        assert cached_db is not None
        assert cached_db.status == HealthStatus.HEALTHY


class TestHealthCheckerErrorHandling:
    """Testes de tratamento de erro para HealthChecker"""
    
    def test_invalid_check_name(self, health_checker):
        """Testa nome de check inválido"""
        def valid_check():
            return {"status": "ok"}
        
        # Nome vazio
        with pytest.raises(ValueError):
            health_checker.register_check("", valid_check)
        
        # Nome None
        with pytest.raises(ValueError):
            health_checker.register_check(None, valid_check)
    
    def test_check_function_exception_handling(self, health_checker):
        """Testa tratamento de exceção em função de check"""
        def exception_check():
            raise ValueError("Invalid configuration")
        
        health_checker.register_check("exception_check", exception_check)
        
        # Deve capturar a exceção e retornar resultado unhealthy
        result = asyncio.run(health_checker.run_check("exception_check"))
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "Invalid configuration" in result.error_message
    
    def test_check_function_timeout_handling(self, health_checker):
        """Testa tratamento de timeout em função de check"""
        async def timeout_check():
            await asyncio.sleep(10.0)  # Muito longo
            return {"status": "ok"}
        
        health_checker.register_check("timeout_check", timeout_check)
        
        # Deve timeout e retornar resultado unhealthy
        result = asyncio.run(health_checker.run_check("timeout_check"))
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "timeout" in result.error_message.lower()
    
    def test_cache_corruption_handling(self, health_checker):
        """Testa tratamento de corrupção de cache"""
        # Simular cache corrompido
        health_checker.results_cache["corrupted"] = "invalid_object"
        
        # Deve lidar graciosamente com cache corrompido
        result = health_checker.get_cached_result("corrupted")
        assert result is None
    
    def test_concurrent_check_execution(self, health_checker):
        """Testa execução concorrente de checks"""
        import threading
        import time
        
        results = []
        lock = threading.Lock()
        
        def concurrent_check():
            with lock:
                results.append(threading.current_thread().name)
            time.sleep(0.1)
            return {"status": "ok"}
        
        health_checker.register_check("concurrent", concurrent_check)
        
        # Executar checks concorrentemente
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=lambda: asyncio.run(health_checker.run_check("concurrent"))
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que todos os threads executaram
        assert len(results) == 5


class TestHealthCheckerPerformance:
    """Testes de performance para HealthChecker"""
    
    def test_large_number_of_checks(self):
        """Testa performance com muitos checks"""
        checker = HealthChecker()
        
        # Registrar 1000 checks
        for i in range(1000):
            def make_check(check_id):
                def check():
                    return {"id": check_id, "status": "ok"}
                return check
            
            checker.register_check(f"check_{i}", make_check(i))
        
        assert len(checker.checks) == 1000
    
    def test_cache_performance(self, health_checker):
        """Testa performance do cache"""
        # Adicionar muitos resultados ao cache
        for i in range(10000):
            result = HealthCheckResult(
                name=f"check_{i}",
                status=HealthStatus.HEALTHY,
                timestamp=datetime.now()
            )
            health_checker.results_cache[f"check_{i}"] = result
        
        # Testar acesso ao cache
        start_time = time.time()
        for i in range(1000):
            health_checker.get_cached_result(f"check_{i}")
        end_time = time.time()
        
        # Deve ser rápido
        assert (end_time - start_time) < 1.0  # Menos de 1 segundo
    
    def test_concurrent_cache_access(self, health_checker):
        """Testa acesso concorrente ao cache"""
        import threading
        
        def cache_worker(worker_id):
            for i in range(100):
                result = HealthCheckResult(
                    name=f"check_{worker_id}_{i}",
                    status=HealthStatus.HEALTHY,
                    timestamp=datetime.now()
                )
                health_checker.results_cache[f"check_{worker_id}_{i}"] = result
                
                # Acessar cache
                cached = health_checker.get_cached_result(f"check_{worker_id}_{i}")
                assert cached is not None
        
        # Executar workers concorrentemente
        threads = []
        for i in range(10):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verificar que todos os dados foram armazenados
        assert len(health_checker.results_cache) == 1000 