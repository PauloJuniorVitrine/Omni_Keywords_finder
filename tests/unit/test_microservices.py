"""
Testes Unitários para Microserviços
Sistema de Comunicação e Orquestração - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de microserviços
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.scaling.microservices import (
    ServiceDiscovery, MicroserviceClient, CircuitBreaker, CircuitBreakerState,
    ServiceStatus, ServiceEndpoint, ServiceInstance, CircuitBreakerConfig,
    create_microservice_client
)


class TestCircuitBreaker:
    """Testes para CircuitBreaker"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            success_threshold=2,
            monitor_interval=10
        )
    
    @pytest.fixture
    def circuit_breaker(self, sample_config):
        """Instância de CircuitBreaker para testes"""
        return CircuitBreaker(sample_config)
    
    def test_circuit_breaker_initialization(self, sample_config):
        """Testa inicialização do CircuitBreaker"""
        cb = CircuitBreaker(sample_config)
        
        assert cb.config == sample_config
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.last_failure_time is None
        assert cb.last_success_time is None
    
    def test_circuit_breaker_config_validation_failure_threshold(self):
        """Testa validação de failure threshold"""
        with pytest.raises(ValueError, match="Failure threshold deve ser pelo menos 1"):
            CircuitBreakerConfig(failure_threshold=0)
    
    def test_circuit_breaker_config_validation_recovery_timeout(self):
        """Testa validação de recovery timeout"""
        with pytest.raises(ValueError, match="Recovery timeout deve ser pelo menos 1 segundo"):
            CircuitBreakerConfig(recovery_timeout=0)
    
    def test_circuit_breaker_config_validation_success_threshold(self):
        """Testa validação de success threshold"""
        with pytest.raises(ValueError, match="Success threshold deve ser pelo menos 1"):
            CircuitBreakerConfig(success_threshold=0)
    
    def test_circuit_breaker_config_validation_monitor_interval(self):
        """Testa validação de monitor interval"""
        with pytest.raises(ValueError, match="Monitor interval deve ser pelo menos 1 segundo"):
            CircuitBreakerConfig(monitor_interval=0)
    
    def test_can_execute_closed_state(self, circuit_breaker):
        """Testa execução em estado fechado"""
        assert circuit_breaker.can_execute() is True
    
    def test_can_execute_open_state(self, circuit_breaker):
        """Testa execução em estado aberto"""
        circuit_breaker.state = CircuitBreakerState.OPEN
        circuit_breaker.last_failure_time = datetime.utcnow()
        
        assert circuit_breaker.can_execute() is False
    
    def test_can_execute_open_state_with_timeout(self, circuit_breaker):
        """Testa execução em estado aberto após timeout"""
        circuit_breaker.state = CircuitBreakerState.OPEN
        circuit_breaker.last_failure_time = datetime.utcnow() - timedelta(seconds=35)  # Mais que 30s
        
        assert circuit_breaker.can_execute() is True
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN
    
    def test_can_execute_half_open_state(self, circuit_breaker):
        """Testa execução em estado half-open"""
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        
        assert circuit_breaker.can_execute() is True
    
    def test_on_success_closed_state(self, circuit_breaker):
        """Testa sucesso em estado fechado"""
        circuit_breaker.on_success()
        
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 1
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    def test_on_success_half_open_state(self, circuit_breaker):
        """Testa sucesso em estado half-open"""
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        circuit_breaker.success_count = 1
        
        circuit_breaker.on_success()
        
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.success_count == 0
    
    def test_on_success_half_open_state_not_enough_successes(self, circuit_breaker):
        """Testa sucesso em estado half-open sem sucessos suficientes"""
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        circuit_breaker.success_count = 0
        
        circuit_breaker.on_success()
        
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN
        assert circuit_breaker.success_count == 1
    
    def test_on_failure_closed_state(self, circuit_breaker):
        """Testa falha em estado fechado"""
        exception = Exception("Test error")
        
        circuit_breaker.on_failure(exception)
        
        assert circuit_breaker.failure_count == 1
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    def test_on_failure_closed_state_threshold_reached(self, circuit_breaker):
        """Testa falha em estado fechado atingindo threshold"""
        exception = Exception("Test error")
        
        # Simular falhas até atingir threshold
        for _ in range(3):
            circuit_breaker.on_failure(exception)
        
        assert circuit_breaker.failure_count == 3
        assert circuit_breaker.state == CircuitBreakerState.OPEN
    
    def test_on_failure_half_open_state(self, circuit_breaker):
        """Testa falha em estado half-open"""
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        exception = Exception("Test error")
        
        circuit_breaker.on_failure(exception)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.success_count == 0
    
    def test_get_state(self, circuit_breaker):
        """Testa obtenção do estado"""
        assert circuit_breaker.get_state() == CircuitBreakerState.CLOSED
        
        circuit_breaker.state = CircuitBreakerState.OPEN
        assert circuit_breaker.get_state() == CircuitBreakerState.OPEN
    
    def test_reset(self, circuit_breaker):
        """Testa reset do circuit breaker"""
        # Modificar estado
        circuit_breaker.state = CircuitBreakerState.OPEN
        circuit_breaker.failure_count = 5
        circuit_breaker.success_count = 2
        circuit_breaker.last_failure_time = datetime.utcnow()
        circuit_breaker.last_success_time = datetime.utcnow()
        
        # Resetar
        circuit_breaker.reset()
        
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0
        assert circuit_breaker.last_failure_time is None
        assert circuit_breaker.last_success_time is None


class TestServiceEndpoint:
    """Testes para ServiceEndpoint"""
    
    def test_service_endpoint_initialization(self):
        """Testa inicialização de ServiceEndpoint"""
        endpoint = ServiceEndpoint(
            service_name="test-service",
            host="localhost",
            port=8080,
            protocol="https",
            path="/api",
            timeout=60,
            retries=5
        )
        
        assert endpoint.service_name == "test-service"
        assert endpoint.host == "localhost"
        assert endpoint.port == 8080
        assert endpoint.protocol == "https"
        assert endpoint.path == "/api"
        assert endpoint.timeout == 60
        assert endpoint.retries == 5
    
    def test_service_endpoint_validation_service_name_empty(self):
        """Testa validação de nome de serviço vazio"""
        with pytest.raises(ValueError, match="Nome do serviço não pode ser vazio"):
            ServiceEndpoint(service_name="", host="localhost", port=8080)
    
    def test_service_endpoint_validation_host_empty(self):
        """Testa validação de host vazio"""
        with pytest.raises(ValueError, match="Host não pode ser vazio"):
            ServiceEndpoint(service_name="test", host="", port=8080)
    
    def test_service_endpoint_validation_port_invalid(self):
        """Testa validação de porta inválida"""
        with pytest.raises(ValueError, match="Porta deve estar entre 1 e 65535"):
            ServiceEndpoint(service_name="test", host="localhost", port=0)
    
    def test_service_endpoint_validation_timeout_invalid(self):
        """Testa validação de timeout inválido"""
        with pytest.raises(ValueError, match="Timeout deve ser pelo menos 1 segundo"):
            ServiceEndpoint(service_name="test", host="localhost", port=8080, timeout=0)
    
    def test_service_endpoint_validation_retries_invalid(self):
        """Testa validação de retries inválido"""
        with pytest.raises(ValueError, match="Retries não pode ser negativo"):
            ServiceEndpoint(service_name="test", host="localhost", port=8080, retries=-1)
    
    def test_get_url(self):
        """Testa geração de URL"""
        endpoint = ServiceEndpoint(
            service_name="test-service",
            host="localhost",
            port=8080,
            protocol="https",
            path="/api"
        )
        
        url = endpoint.get_url()
        assert url == "https://localhost:8080/api"
        
        url = endpoint.get_url("/users")
        assert url == "https://localhost:8080/users"
    
    def test_get_health_url(self):
        """Testa geração de URL de health check"""
        endpoint = ServiceEndpoint(
            service_name="test-service",
            host="localhost",
            port=8080,
            health_check_path="/health"
        )
        
        health_url = endpoint.get_health_url()
        assert health_url == "http://localhost:8080/health"


class TestServiceInstance:
    """Testes para ServiceInstance"""
    
    @pytest.fixture
    def sample_endpoint(self):
        """Endpoint de exemplo para testes"""
        return ServiceEndpoint(
            service_name="test-service",
            host="localhost",
            port=8080
        )
    
    def test_service_instance_initialization(self, sample_endpoint):
        """Testa inicialização de ServiceInstance"""
        instance = ServiceInstance(
            id="instance-1",
            service_name="test-service",
            endpoint=sample_endpoint,
            status=ServiceStatus.HEALTHY,
            response_time=150.0,
            error_rate=0.02,
            load=0.3,
            version="1.0.0"
        )
        
        assert instance.id == "instance-1"
        assert instance.service_name == "test-service"
        assert instance.endpoint == sample_endpoint
        assert instance.status == ServiceStatus.HEALTHY
        assert instance.response_time == 150.0
        assert instance.error_rate == 0.02
        assert instance.load == 0.3
        assert instance.version == "1.0.0"
    
    def test_service_instance_validation_id_empty(self, sample_endpoint):
        """Testa validação de ID vazio"""
        with pytest.raises(ValueError, match="ID da instância não pode ser vazio"):
            ServiceInstance(id="", service_name="test", endpoint=sample_endpoint)
    
    def test_service_instance_validation_health_check_failures_negative(self, sample_endpoint):
        """Testa validação de health check failures negativo"""
        with pytest.raises(ValueError, match="Health check failures não pode ser negativo"):
            ServiceInstance(id="test", service_name="test", endpoint=sample_endpoint, health_check_failures=-1)
    
    def test_service_instance_validation_response_time_negative(self, sample_endpoint):
        """Testa validação de response time negativo"""
        with pytest.raises(ValueError, match="Response time não pode ser negativo"):
            ServiceInstance(id="test", service_name="test", endpoint=sample_endpoint, response_time=-1.0)
    
    def test_service_instance_validation_error_rate_invalid(self, sample_endpoint):
        """Testa validação de error rate inválido"""
        with pytest.raises(ValueError, match="Error rate deve estar entre 0 e 1"):
            ServiceInstance(id="test", service_name="test", endpoint=sample_endpoint, error_rate=1.5)
    
    def test_service_instance_validation_load_invalid(self, sample_endpoint):
        """Testa validação de load inválido"""
        with pytest.raises(ValueError, match="Load deve estar entre 0 e 1"):
            ServiceInstance(id="test", service_name="test", endpoint=sample_endpoint, load=1.5)
    
    def test_is_healthy(self, sample_endpoint):
        """Testa verificação de saúde"""
        healthy_instance = ServiceInstance(
            id="healthy",
            service_name="test",
            endpoint=sample_endpoint,
            status=ServiceStatus.HEALTHY
        )
        
        unhealthy_instance = ServiceInstance(
            id="unhealthy",
            service_name="test",
            endpoint=sample_endpoint,
            status=ServiceStatus.UNHEALTHY
        )
        
        assert healthy_instance.is_healthy() is True
        assert unhealthy_instance.is_healthy() is False
    
    def test_get_health_score(self, sample_endpoint):
        """Testa cálculo de score de saúde"""
        instance = ServiceInstance(
            id="test",
            service_name="test",
            endpoint=sample_endpoint,
            status=ServiceStatus.HEALTHY,
            response_time=1000.0,  # 1s
            error_rate=0.1,
            load=0.5
        )
        
        score = instance.get_health_score()
        assert 0.0 <= score <= 1.0
    
    def test_get_health_score_unhealthy(self, sample_endpoint):
        """Testa score de saúde de instância não saudável"""
        instance = ServiceInstance(
            id="test",
            service_name="test",
            endpoint=sample_endpoint,
            status=ServiceStatus.UNHEALTHY
        )
        
        score = instance.get_health_score()
        assert score == 0.0


class TestServiceDiscovery:
    """Testes para ServiceDiscovery"""
    
    @pytest.fixture
    def service_discovery(self):
        """Instância de ServiceDiscovery para testes"""
        return ServiceDiscovery()
    
    @pytest.fixture
    def sample_instance(self):
        """Instância de serviço de exemplo"""
        endpoint = ServiceEndpoint(
            service_name="test-service",
            host="localhost",
            port=8080
        )
        return ServiceInstance(
            id="instance-1",
            service_name="test-service",
            endpoint=endpoint,
            status=ServiceStatus.HEALTHY
        )
    
    def test_service_discovery_initialization(self):
        """Testa inicialização do ServiceDiscovery"""
        sd = ServiceDiscovery()
        
        assert len(sd.services) == 0
        assert sd.health_check_task is None
        assert sd.is_running is False
    
    def test_register_service(self, service_discovery, sample_instance):
        """Testa registro de serviço"""
        service_discovery.register_service(sample_instance)
        
        assert "test-service" in service_discovery.services
        assert len(service_discovery.services["test-service"]) == 1
        assert service_discovery.services["test-service"][0] == sample_instance
    
    def test_register_service_update_existing(self, service_discovery, sample_instance):
        """Testa atualização de serviço existente"""
        # Registrar primeira vez
        service_discovery.register_service(sample_instance)
        
        # Modificar e registrar novamente
        sample_instance.status = ServiceStatus.UNHEALTHY
        sample_instance.response_time = 500.0
        
        service_discovery.register_service(sample_instance)
        
        # Verificar se foi atualizado
        instances = service_discovery.services["test-service"]
        assert len(instances) == 1
        assert instances[0].status == ServiceStatus.UNHEALTHY
        assert instances[0].response_time == 500.0
    
    def test_unregister_service(self, service_discovery, sample_instance):
        """Testa remoção de serviço"""
        service_discovery.register_service(sample_instance)
        
        success = service_discovery.unregister_service("test-service", "instance-1")
        
        assert success is True
        assert len(service_discovery.services["test-service"]) == 0
    
    def test_unregister_service_not_found(self, service_discovery):
        """Testa remoção de serviço inexistente"""
        success = service_discovery.unregister_service("nonexistent", "instance-1")
        assert success is False
    
    def test_get_service_instances_all(self, service_discovery, sample_instance):
        """Testa obtenção de todas as instâncias"""
        service_discovery.register_service(sample_instance)
        
        instances = service_discovery.get_service_instances("test-service", healthy_only=False)
        assert len(instances) == 1
        assert instances[0] == sample_instance
    
    def test_get_service_instances_healthy_only(self, service_discovery):
        """Testa obtenção apenas de instâncias saudáveis"""
        endpoint = ServiceEndpoint(service_name="test-service", host="localhost", port=8080)
        
        healthy_instance = ServiceInstance(
            id="healthy",
            service_name="test-service",
            endpoint=endpoint,
            status=ServiceStatus.HEALTHY
        )
        
        unhealthy_instance = ServiceInstance(
            id="unhealthy",
            service_name="test-service",
            endpoint=endpoint,
            status=ServiceStatus.UNHEALTHY
        )
        
        service_discovery.register_service(healthy_instance)
        service_discovery.register_service(unhealthy_instance)
        
        instances = service_discovery.get_service_instances("test-service", healthy_only=True)
        assert len(instances) == 1
        assert instances[0].id == "healthy"
    
    def test_get_service_instances_not_found(self, service_discovery):
        """Testa obtenção de instâncias de serviço inexistente"""
        instances = service_discovery.get_service_instances("nonexistent")
        assert len(instances) == 0
    
    def test_get_best_instance(self, service_discovery):
        """Testa obtenção da melhor instância"""
        endpoint = ServiceEndpoint(service_name="test-service", host="localhost", port=8080)
        
        # Instância com melhor score
        good_instance = ServiceInstance(
            id="good",
            service_name="test-service",
            endpoint=endpoint,
            status=ServiceStatus.HEALTHY,
            response_time=100.0,
            error_rate=0.01,
            load=0.2
        )
        
        # Instância com pior score
        bad_instance = ServiceInstance(
            id="bad",
            service_name="test-service",
            endpoint=endpoint,
            status=ServiceStatus.HEALTHY,
            response_time=1000.0,
            error_rate=0.1,
            load=0.8
        )
        
        service_discovery.register_service(good_instance)
        service_discovery.register_service(bad_instance)
        
        best_instance = service_discovery.get_best_instance("test-service")
        assert best_instance.id == "good"
    
    def test_get_best_instance_no_healthy(self, service_discovery):
        """Testa obtenção da melhor instância sem instâncias saudáveis"""
        endpoint = ServiceEndpoint(service_name="test-service", host="localhost", port=8080)
        
        unhealthy_instance = ServiceInstance(
            id="unhealthy",
            service_name="test-service",
            endpoint=endpoint,
            status=ServiceStatus.UNHEALTHY
        )
        
        service_discovery.register_service(unhealthy_instance)
        
        best_instance = service_discovery.get_best_instance("test-service")
        assert best_instance is None
    
    @pytest.mark.asyncio
    async def test_start_stop_health_checks(self, service_discovery):
        """Testa início e parada de health checks"""
        await service_discovery.start_health_checks(interval=1)
        assert service_discovery.is_running is True
        assert service_discovery.health_check_task is not None
        
        await service_discovery.stop_health_checks()
        assert service_discovery.is_running is False


class TestMicroserviceClient:
    """Testes para MicroserviceClient"""
    
    @pytest.fixture
    def service_discovery(self):
        """ServiceDiscovery para testes"""
        return ServiceDiscovery()
    
    @pytest.fixture
    def circuit_breaker_config(self):
        """Configuração de circuit breaker para testes"""
        return CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=10,
            success_threshold=1
        )
    
    @pytest.fixture
    def microservice_client(self, service_discovery, circuit_breaker_config):
        """Instância de MicroserviceClient para testes"""
        return MicroserviceClient(service_discovery, circuit_breaker_config)
    
    @pytest.fixture
    def sample_instance(self):
        """Instância de serviço de exemplo"""
        endpoint = ServiceEndpoint(
            service_name="test-service",
            host="localhost",
            port=8080
        )
        return ServiceInstance(
            id="instance-1",
            service_name="test-service",
            endpoint=endpoint,
            status=ServiceStatus.HEALTHY
        )
    
    def test_microservice_client_initialization(self, service_discovery):
        """Testa inicialização do MicroserviceClient"""
        client = MicroserviceClient(service_discovery)
        
        assert client.service_discovery == service_discovery
        assert len(client.circuit_breakers) == 0
    
    def test_get_circuit_breaker(self, microservice_client):
        """Testa obtenção de circuit breaker"""
        cb = microservice_client._get_circuit_breaker("test-service")
        
        assert isinstance(cb, CircuitBreaker)
        assert "test-service" in microservice_client.circuit_breakers
        
        # Deve retornar o mesmo circuit breaker
        cb2 = microservice_client._get_circuit_breaker("test-service")
        assert cb is cb2
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession')
    async def test_call_service_success(self, mock_session, microservice_client, sample_instance):
        """Testa chamada de serviço bem-sucedida"""
        # Configurar mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"result": "success"})
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value = mock_session_instance
        mock_session_instance.__aexit__.return_value = None
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response
        
        mock_session.return_value = mock_session_instance
        
        # Registrar instância
        microservice_client.service_discovery.register_service(sample_instance)
        
        # Chamar serviço
        status_code, response_data = await microservice_client.call_service(
            "test-service", "GET", "/test"
        )
        
        assert status_code == 200
        assert response_data == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_call_service_no_instances(self, microservice_client):
        """Testa chamada de serviço sem instâncias disponíveis"""
        with pytest.raises(Exception, match="Nenhuma instância disponível para serviço test-service"):
            await microservice_client.call_service("test-service")
    
    @pytest.mark.asyncio
    async def test_call_service_circuit_breaker_open(self, microservice_client, sample_instance):
        """Testa chamada de serviço com circuit breaker aberto"""
        # Registrar instância
        microservice_client.service_discovery.register_service(sample_instance)
        
        # Abrir circuit breaker
        cb = microservice_client._get_circuit_breaker("test-service")
        cb.state = CircuitBreakerState.OPEN
        cb.last_failure_time = datetime.utcnow()
        
        with pytest.raises(Exception, match="Circuit breaker aberto para serviço test-service"):
            await microservice_client.call_service("test-service")
    
    @pytest.mark.asyncio
    async def test_call_service_with_fallback_success(self, microservice_client, sample_instance):
        """Testa chamada de serviço com fallback bem-sucedida"""
        # Configurar mock
        with patch('aiohttp.ClientSession'):
            # Registrar instância
            microservice_client.service_discovery.register_service(sample_instance)
            
            # Mock de fallback
            fallback_mock = AsyncMock(return_value={"fallback": "data"})
            
            # Chamar serviço com fallback
            result = await microservice_client.call_service_with_fallback(
                "test-service",
                fallback=fallback_mock
            )
            
            assert result == {"fallback": "data"}
    
    @pytest.mark.asyncio
    async def test_call_service_with_fallback_failure(self, microservice_client):
        """Testa chamada de serviço com fallback falhando"""
        # Mock de fallback que falha
        fallback_mock = AsyncMock(side_effect=Exception("Fallback failed"))
        
        with pytest.raises(Exception, match="Fallback também falhou"):
            await microservice_client.call_service_with_fallback(
                "test-service",
                fallback=fallback_mock
            )
    
    def test_get_service_status(self, microservice_client, sample_instance):
        """Testa obtenção de status do serviço"""
        # Registrar instância
        microservice_client.service_discovery.register_service(sample_instance)
        
        status = microservice_client.get_service_status("test-service")
        
        assert status["service_name"] == "test-service"
        assert status["total_instances"] == 1
        assert status["healthy_instances"] == 1
        assert status["circuit_breaker_state"] == "closed"
        assert len(status["instances"]) == 1
        assert status["instances"][0]["id"] == "instance-1"


class TestCreateFunctions:
    """Testes para funções de criação"""
    
    def test_create_microservice_client_default(self):
        """Testa criação de MicroserviceClient com configurações padrão"""
        client = create_microservice_client()
        
        assert isinstance(client, MicroserviceClient)
        assert isinstance(client.service_discovery, ServiceDiscovery)
    
    def test_create_microservice_client_with_service_discovery(self):
        """Testa criação de MicroserviceClient com ServiceDiscovery customizado"""
        service_discovery = ServiceDiscovery()
        client = create_microservice_client(service_discovery=service_discovery)
        
        assert client.service_discovery is service_discovery
    
    def test_create_microservice_client_with_circuit_breaker_config(self):
        """Testa criação de MicroserviceClient com configuração de circuit breaker"""
        config = CircuitBreakerConfig(failure_threshold=10)
        client = create_microservice_client(circuit_breaker_config=config)
        
        # Verificar se a configuração foi aplicada
        cb = client._get_circuit_breaker("test")
        assert cb.config.failure_threshold == 10


class TestMicroservicesIntegration:
    """Testes de integração para Microserviços"""
    
    @pytest.mark.asyncio
    async def test_complete_microservice_communication(self):
        """Testa comunicação completa entre microserviços"""
        # Criar service discovery
        service_discovery = ServiceDiscovery()
        
        # Criar instâncias de serviço
        endpoint1 = ServiceEndpoint(
            service_name="user-service",
            host="localhost",
            port=8081
        )
        endpoint2 = ServiceEndpoint(
            service_name="user-service",
            host="localhost",
            port=8082
        )
        
        instance1 = ServiceInstance(
            id="user-1",
            service_name="user-service",
            endpoint=endpoint1,
            status=ServiceStatus.HEALTHY
        )
        instance2 = ServiceInstance(
            id="user-2",
            service_name="user-service",
            endpoint=endpoint2,
            status=ServiceStatus.HEALTHY
        )
        
        # Registrar instâncias
        service_discovery.register_service(instance1)
        service_discovery.register_service(instance2)
        
        # Criar cliente
        client = create_microservice_client(service_discovery)
        
        # Verificar status
        status = client.get_service_status("user-service")
        assert status["total_instances"] == 2
        assert status["healthy_instances"] == 2
        
        # Obter melhor instância
        best_instance = service_discovery.get_best_instance("user-service")
        assert best_instance is not None
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Testa integração do circuit breaker"""
        # Criar service discovery
        service_discovery = ServiceDiscovery()
        
        # Criar instância
        endpoint = ServiceEndpoint(
            service_name="test-service",
            host="localhost",
            port=8080
        )
        instance = ServiceInstance(
            id="test-1",
            service_name="test-service",
            endpoint=endpoint,
            status=ServiceStatus.HEALTHY
        )
        service_discovery.register_service(instance)
        
        # Criar cliente com circuit breaker configurado
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=5)
        client = create_microservice_client(service_discovery, config)
        
        # Verificar estado inicial
        cb = client._get_circuit_breaker("test-service")
        assert cb.get_state() == CircuitBreakerState.CLOSED
        
        # Simular falhas
        for _ in range(2):
            cb.on_failure(Exception("Test error"))
        
        # Verificar se abriu
        assert cb.get_state() == CircuitBreakerState.OPEN
        
        # Aguardar recuperação
        cb.last_failure_time = datetime.utcnow() - timedelta(seconds=6)
        
        # Verificar se pode executar novamente
        assert cb.can_execute() is True
        assert cb.get_state() == CircuitBreakerState.HALF_OPEN


if __name__ == "__main__":
    pytest.main([__file__]) 