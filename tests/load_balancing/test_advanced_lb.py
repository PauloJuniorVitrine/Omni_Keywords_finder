# 📋 Testes para Advanced Load Balancer
# Tracing ID: TEST_ADVANCED_LB_012_20250127
# Versão: 1.0
# Data: 2025-01-27
# Objetivo: Testes para load balancing avançado

"""
Testes para Advanced Load Balancer

Testa funcionalidades de load balancing, health checks, failover e métricas.
"""

import pytest
import asyncio
import tempfile
import yaml
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import aiohttp

from infrastructure.load_balancing.advanced_lb import (
    AdvancedLoadBalancer,
    BackendServer,
    BackendMetrics,
    LoadBalancingStrategy,
    BackendStatus,
    get_load_balancer,
    close_load_balancer
)

class TestBackendServer:
    """Testes para a classe BackendServer"""
    
    def test_valid_backend_creation(self):
        """Testa criação de backend válido"""
        backend = BackendServer(
            id="test_backend",
            host="localhost",
            port=8080,
            protocol="http",
            weight=2,
            max_connections=50,
            region="us-east-1",
            datacenter="primary"
        )
        
        assert backend.id == "test_backend"
        assert backend.host == "localhost"
        assert backend.port == 8080
        assert backend.protocol == "http"
        assert backend.weight == 2
        assert backend.max_connections == 50
        assert backend.region == "us-east-1"
        assert backend.datacenter == "primary"
    
    def test_invalid_port(self):
        """Testa validação de porta inválida"""
        with pytest.raises(ValueError, match="Porta deve estar entre 1 e 65535"):
            BackendServer(
                id="test",
                host="localhost",
                port=0,
                weight=1
            )
    
    def test_invalid_weight(self):
        """Testa validação de weight inválido"""
        with pytest.raises(ValueError, match="Weight deve ser >= 1"):
            BackendServer(
                id="test",
                host="localhost",
                port=8080,
                weight=0
            )
    
    def test_missing_required_fields(self):
        """Testa validação de campos obrigatórios"""
        with pytest.raises(ValueError, match="Host e ID são obrigatórios"):
            BackendServer(
                id="",
                host="",
                port=8080,
                weight=1
            )

class TestBackendMetrics:
    """Testes para a classe BackendMetrics"""
    
    def test_metrics_creation(self):
        """Testa criação de métricas"""
        now = datetime.now()
        metrics = BackendMetrics(
            response_time=0.1,
            connection_count=5,
            active_requests=2,
            total_requests=100,
            failed_requests=5,
            last_health_check=now,
            last_response_time=now,
            status=BackendStatus.HEALTHY,
            consecutive_failures=0,
            consecutive_successes=10,
            uptime_percentage=95.0,
            error_rate=5.0
        )
        
        assert metrics.response_time == 0.1
        assert metrics.connection_count == 5
        assert metrics.active_requests == 2
        assert metrics.total_requests == 100
        assert metrics.failed_requests == 5
        assert metrics.last_health_check == now
        assert metrics.last_response_time == now
        assert metrics.status == BackendStatus.HEALTHY
        assert metrics.consecutive_failures == 0
        assert metrics.consecutive_successes == 10
        assert metrics.uptime_percentage == 95.0
        assert metrics.error_rate == 5.0

class TestAdvancedLoadBalancer:
    """Testes para o AdvancedLoadBalancer"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Cria arquivo de configuração temporário"""
        config = {
            'load_balancer': {
                'strategy': 'round_robin',
                'circuit_breaker_enabled': True,
                'sticky_sessions_enabled': True,
                'rate_limiting_enabled': True,
                'failover_enabled': True
            },
            'backends': [
                {
                    'id': 'backend_1',
                    'host': 'backend1.example.com',
                    'port': 8080,
                    'protocol': 'http',
                    'weight': 2,
                    'max_connections': 100,
                    'region': 'us-east-1',
                    'datacenter': 'primary',
                    'health_check_path': '/health',
                    'health_check_interval': 30,
                    'health_check_timeout': 5,
                    'health_check_threshold': 3,
                    'failover_threshold': 3,
                    'enabled': True
                },
                {
                    'id': 'backend_2',
                    'host': 'backend2.example.com',
                    'port': 8080,
                    'protocol': 'http',
                    'weight': 1,
                    'max_connections': 50,
                    'region': 'us-west-2',
                    'datacenter': 'backup',
                    'health_check_path': '/health',
                    'health_check_interval': 30,
                    'health_check_timeout': 5,
                    'health_check_threshold': 3,
                    'failover_threshold': 3,
                    'enabled': True
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            yield f.name
        
        os.unlink(f.name)
    
    @pytest.fixture
    def lb_instance(self, temp_config_file):
        """Cria instância do load balancer"""
        with patch('infrastructure.load_balancing.advanced_lb.asyncio.create_task'):
            lb = AdvancedLoadBalancer(temp_config_file)
            yield lb
            # Cleanup
            asyncio.create_task(lb.close())
    
    def test_load_configuration_from_file(self, temp_config_file):
        """Testa carregamento de configuração do arquivo"""
        with patch('infrastructure.load_balancing.advanced_lb.asyncio.create_task'):
            lb = AdvancedLoadBalancer(temp_config_file)
            
            assert len(lb.backends) == 2
            assert "backend_1" in lb.backends
            assert "backend_2" in lb.backends
            
            # Verifica configuração do primeiro backend
            backend1 = lb.backends["backend_1"]
            assert backend1.host == "backend1.example.com"
            assert backend1.port == 8080
            assert backend1.weight == 2
            assert backend1.region == "us-east-1"
            assert backend1.datacenter == "primary"
            
            # Verifica configuração do segundo backend
            backend2 = lb.backends["backend_2"]
            assert backend2.host == "backend2.example.com"
            assert backend2.port == 8080
            assert backend2.weight == 1
            assert backend2.region == "us-west-2"
            assert backend2.datacenter == "backup"
            
            # Verifica configuração geral
            assert lb.strategy == LoadBalancingStrategy.ROUND_ROBIN
            assert lb.circuit_breaker_enabled is True
            assert lb.sticky_sessions_enabled is True
            assert lb.rate_limiting_enabled is True
            assert lb.failover_enabled is True
    
    def test_load_configuration_from_environment(self):
        """Testa carregamento de configuração do ambiente"""
        env_vars = {
            'LB_BACKEND_HOSTS': 'env-backend1.com,env-backend2.com',
            'LB_BACKEND_PORTS': '8080,8081',
            'LB_BACKEND_REGIONS': 'us-east-1,us-west-2',
            'LB_BACKEND_1_WEIGHT': '3',
            'LB_BACKEND_2_WEIGHT': '1',
            'LB_BACKEND_1_DATACENTER': 'primary',
            'LB_BACKEND_2_DATACENTER': 'backup'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('infrastructure.load_balancing.advanced_lb.asyncio.create_task'):
                lb = AdvancedLoadBalancer("nonexistent.yaml")
                
                assert len(lb.backends) == 2
                assert "backend_1" in lb.backends
                assert "backend_2" in lb.backends
                
                backend1 = lb.backends["backend_1"]
                assert backend1.host == "env-backend1.com"
                assert backend1.port == 8080
                assert backend1.weight == 3
                assert backend1.region == "us-east-1"
                assert backend1.datacenter == "primary"
                
                backend2 = lb.backends["backend_2"]
                assert backend2.host == "env-backend2.com"
                assert backend2.port == 8081
                assert backend2.weight == 1
                assert backend2.region == "us-west-2"
                assert backend2.datacenter == "backup"
    
    def test_initialize_backends(self, lb_instance):
        """Testa inicialização dos backends"""
        assert len(lb_instance.metrics) == 2
        assert "backend_1" in lb_instance.metrics
        assert "backend_2" in lb_instance.metrics
        
        # Verifica se as métricas foram inicializadas
        for backend_id in ["backend_1", "backend_2"]:
            metrics = lb_instance.metrics[backend_id]
            assert metrics.status == BackendStatus.UNHEALTHY
            assert metrics.response_time == 0.0
            assert metrics.connection_count == 0
            assert metrics.total_requests == 0
            assert metrics.failed_requests == 0
    
    @pytest.mark.asyncio
    async def test_check_backend_health_success(self, lb_instance):
        """Testa health check bem-sucedido"""
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.status = 200
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            await lb_instance._check_backend_health("backend_1")
            
            # Verifica se o status foi atualizado
            metrics = lb_instance.metrics["backend_1"]
            assert metrics.status == BackendStatus.HEALTHY
            assert metrics.response_time > 0
            assert metrics.consecutive_successes == 1
            assert metrics.consecutive_failures == 0
            assert metrics.last_health_check is not None
            assert metrics.last_response_time is not None
    
    @pytest.mark.asyncio
    async def test_check_backend_health_failure(self, lb_instance):
        """Testa health check com falha"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = Exception("Connection failed")
            
            await lb_instance._check_backend_health("backend_1")
            
            # Verifica se o status foi atualizado
            metrics = lb_instance.metrics["backend_1"]
            assert metrics.consecutive_failures == 1
            assert metrics.consecutive_successes == 0
            assert metrics.last_health_check is not None
    
    @pytest.mark.asyncio
    async def test_trigger_failover(self, lb_instance):
        """Testa processo de failover"""
        # Configura backends
        lb_instance.metrics["backend_1"].status = BackendStatus.UNHEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        
        await lb_instance._trigger_failover("backend_1")
        
        # Verifica se o status foi atualizado
        assert lb_instance.metrics["backend_1"].status == BackendStatus.FAILING_OVER
    
    def test_round_robin_select(self, lb_instance):
        """Testa seleção round-robin"""
        # Configura backends saudáveis
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        
        # Primeira seleção
        selected1 = lb_instance._round_robin_select(["backend_1", "backend_2"])
        assert selected1 == "backend_1"
        
        # Segunda seleção
        selected2 = lb_instance._round_robin_select(["backend_1", "backend_2"])
        assert selected2 == "backend_2"
        
        # Terceira seleção (volta para primeira)
        selected3 = lb_instance._round_robin_select(["backend_1", "backend_2"])
        assert selected3 == "backend_1"
    
    def test_least_connections_select(self, lb_instance):
        """Testa seleção por menor número de conexões"""
        # Configura backends saudáveis com diferentes números de conexões
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_1"].connection_count = 5
        
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].connection_count = 2
        
        # Deve selecionar backend_2 (menos conexões)
        selected = lb_instance._least_connections_select(["backend_1", "backend_2"])
        assert selected == "backend_2"
    
    def test_weighted_round_robin_select(self, lb_instance):
        """Testa seleção round-robin com pesos"""
        # Configura backends saudáveis
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        
        # backend_1 tem weight=2, backend_2 tem weight=1
        # Deve selecionar backend_1 duas vezes, depois backend_2 uma vez
        selected1 = lb_instance._weighted_round_robin_select(["backend_1", "backend_2"])
        assert selected1 == "backend_1"
        
        selected2 = lb_instance._weighted_round_robin_select(["backend_1", "backend_2"])
        assert selected2 == "backend_1"
        
        selected3 = lb_instance._weighted_round_robin_select(["backend_1", "backend_2"])
        assert selected3 == "backend_2"
    
    def test_least_response_time_select(self, lb_instance):
        """Testa seleção por menor tempo de resposta"""
        # Configura backends saudáveis com diferentes tempos de resposta
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_1"].response_time = 0.2
        
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].response_time = 0.1
        
        # Deve selecionar backend_2 (menor tempo de resposta)
        selected = lb_instance._least_response_time_select(["backend_1", "backend_2"])
        assert selected == "backend_2"
    
    def test_ip_hash_select(self, lb_instance):
        """Testa seleção por hash do IP"""
        # Configura backends saudáveis
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        
        # Mesmo IP deve sempre selecionar o mesmo backend
        client_ip = "192.168.1.100"
        selected1 = lb_instance._ip_hash_select(["backend_1", "backend_2"], client_ip)
        selected2 = lb_instance._ip_hash_select(["backend_1", "backend_2"], client_ip)
        assert selected1 == selected2
    
    def test_consistent_hash_select(self, lb_instance):
        """Testa seleção por hash consistente"""
        # Configura backends saudáveis
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        
        # Mesmo IP deve sempre selecionar o mesmo backend
        client_ip = "192.168.1.100"
        selected1 = lb_instance._consistent_hash_select(["backend_1", "backend_2"], client_ip)
        selected2 = lb_instance._consistent_hash_select(["backend_1", "backend_2"], client_ip)
        assert selected1 == selected2
    
    def test_adaptive_select(self, lb_instance):
        """Testa seleção adaptativa"""
        # Configura backends saudáveis com diferentes métricas
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_1"].response_time = 0.1
        lb_instance.metrics["backend_1"].connection_count = 5
        lb_instance.metrics["backend_1"].uptime_percentage = 95.0
        
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].response_time = 0.2
        lb_instance.metrics["backend_2"].connection_count = 10
        lb_instance.metrics["backend_2"].uptime_percentage = 90.0
        
        # Deve selecionar backend_1 (melhor score)
        selected = lb_instance._adaptive_select(["backend_1", "backend_2"])
        assert selected == "backend_1"
    
    def test_select_backend_round_robin(self, lb_instance):
        """Testa seleção de backend com estratégia round-robin"""
        lb_instance.strategy = LoadBalancingStrategy.ROUND_ROBIN
        
        # Configura backends saudáveis
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        
        # Testa seleção
        selected1 = lb_instance.select_backend()
        selected2 = lb_instance.select_backend()
        
        # Deve alternar entre backends
        assert selected1 != selected2
        assert selected1 in ["backend_1", "backend_2"]
        assert selected2 in ["backend_1", "backend_2"]
    
    def test_select_backend_no_healthy_backends(self, lb_instance):
        """Testa seleção quando não há backends saudáveis"""
        # Configura todos os backends como não saudáveis
        lb_instance.metrics["backend_1"].status = BackendStatus.UNHEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.UNHEALTHY
        
        selected = lb_instance.select_backend()
        assert selected is None
    
    def test_select_backend_sticky_sessions(self, lb_instance):
        """Testa seleção com sticky sessions"""
        lb_instance.sticky_sessions_enabled = True
        
        # Configura backends saudáveis
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.HEALTHY
        
        session_id = "test_session_123"
        
        # Primeira seleção
        selected1 = lb_instance.select_backend(session_id=session_id)
        
        # Segunda seleção com mesmo session_id
        selected2 = lb_instance.select_backend(session_id=session_id)
        
        # Deve retornar o mesmo backend
        assert selected1 == selected2
    
    def test_record_request(self, lb_instance):
        """Testa registro de métricas de requisição"""
        backend_id = "backend_1"
        
        # Registra requisição bem-sucedida
        lb_instance.record_request(backend_id, 0.1, success=True)
        
        metrics = lb_instance.metrics[backend_id]
        assert metrics.total_requests == 1
        assert metrics.response_time == 0.1
        assert metrics.failed_requests == 0
        assert metrics.consecutive_successes == 1
        assert metrics.consecutive_failures == 0
        
        # Registra requisição com falha
        lb_instance.record_request(backend_id, 0.2, success=False)
        
        metrics = lb_instance.metrics[backend_id]
        assert metrics.total_requests == 2
        assert metrics.response_time == 0.2
        assert metrics.failed_requests == 1
        assert metrics.consecutive_successes == 0
        assert metrics.consecutive_failures == 1
    
    def test_connection_management(self, lb_instance):
        """Testa gerenciamento de conexões"""
        backend_id = "backend_1"
        
        # Incrementa conexão
        lb_instance.increment_connection(backend_id)
        assert lb_instance.metrics[backend_id].connection_count == 1
        
        # Incrementa novamente
        lb_instance.increment_connection(backend_id)
        assert lb_instance.metrics[backend_id].connection_count == 2
        
        # Decrementa conexão
        lb_instance.decrement_connection(backend_id)
        assert lb_instance.metrics[backend_id].connection_count == 1
        
        # Decrementa até zero
        lb_instance.decrement_connection(backend_id)
        assert lb_instance.metrics[backend_id].connection_count == 0
        
        # Não deve ficar negativo
        lb_instance.decrement_connection(backend_id)
        assert lb_instance.metrics[backend_id].connection_count == 0
    
    def test_get_metrics(self, lb_instance):
        """Testa obtenção de métricas"""
        metrics = lb_instance.get_metrics()
        
        assert len(metrics) == 2
        assert "backend_1" in metrics
        assert "backend_2" in metrics
        
        # Verifica estrutura das métricas
        backend1_metrics = metrics["backend_1"]
        assert "id" in backend1_metrics
        assert "host" in backend1_metrics
        assert "port" in backend1_metrics
        assert "region" in backend1_metrics
        assert "datacenter" in backend1_metrics
        assert "status" in backend1_metrics
        assert "response_time" in backend1_metrics
        assert "connection_count" in backend1_metrics
        assert "total_requests" in backend1_metrics
        assert "failed_requests" in backend1_metrics
        assert "uptime_percentage" in backend1_metrics
        assert "error_rate" in backend1_metrics
    
    def test_get_healthy_backends(self, lb_instance):
        """Testa obtenção de backends saudáveis"""
        # Configura status dos backends
        lb_instance.metrics["backend_1"].status = BackendStatus.HEALTHY
        lb_instance.metrics["backend_2"].status = BackendStatus.UNHEALTHY
        
        healthy_backends = lb_instance.get_healthy_backends()
        assert len(healthy_backends) == 1
        assert "backend_1" in healthy_backends
    
    def test_get_backend_url(self, lb_instance):
        """Testa obtenção de URL do backend"""
        backend_id = "backend_1"
        path = "/api/v1"
        
        url = lb_instance.get_backend_url(backend_id, path)
        expected_url = "http://backend1.example.com:8080/api/v1"
        assert url == expected_url
        
        # Testa com backend inexistente
        url = lb_instance.get_backend_url("nonexistent", path)
        assert url is None

class TestSingletonFunctions:
    """Testes para funções singleton"""
    
    @pytest.mark.asyncio
    async def test_get_load_balancer_singleton(self):
        """Testa que get_load_balancer retorna sempre a mesma instância"""
        with patch('infrastructure.load_balancing.advanced_lb.AdvancedLoadBalancer') as mock_lb:
            mock_instance = Mock()
            mock_lb.return_value = mock_instance
            
            # Primeira chamada
            lb1 = get_load_balancer()
            assert lb1 == mock_instance
            
            # Segunda chamada (deve retornar a mesma instância)
            lb2 = get_load_balancer()
            assert lb2 == mock_instance
            
            # Verifica que o construtor foi chamado apenas uma vez
            mock_lb.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_load_balancer(self):
        """Testa fechamento do load balancer singleton"""
        with patch('infrastructure.load_balancing.advanced_lb.AdvancedLoadBalancer') as mock_lb:
            mock_instance = Mock()
            mock_lb.return_value = mock_instance
            
            # Obtém instância
            get_load_balancer()
            
            # Fecha
            await close_load_balancer()
            
            # Verifica se close foi chamado
            mock_instance.close.assert_called_once()

class TestIntegrationScenarios:
    """Testes de cenários de integração"""
    
    @pytest.mark.asyncio
    async def test_load_balancing_scenario(self, temp_config_file):
        """Testa cenário completo de load balancing"""
        with patch('infrastructure.load_balancing.advanced_lb.asyncio.create_task'):
            lb = AdvancedLoadBalancer(temp_config_file)
            
            # Configura backends saudáveis
            lb.metrics["backend_1"].status = BackendStatus.HEALTHY
            lb.metrics["backend_2"].status = BackendStatus.HEALTHY
            
            # Testa diferentes estratégias
            strategies = [
                LoadBalancingStrategy.ROUND_ROBIN,
                LoadBalancingStrategy.LEAST_CONNECTIONS,
                LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
                LoadBalancingStrategy.LEAST_RESPONSE_TIME
            ]
            
            for strategy in strategies:
                lb.strategy = strategy
                selected = lb.select_backend()
                assert selected in ["backend_1", "backend_2"]
    
    @pytest.mark.asyncio
    async def test_failover_scenario(self, temp_config_file):
        """Testa cenário de failover"""
        with patch('infrastructure.load_balancing.advanced_lb.asyncio.create_task'):
            lb = AdvancedLoadBalancer(temp_config_file)
            
            # Configura cenário inicial
            lb.metrics["backend_1"].status = BackendStatus.HEALTHY
            lb.metrics["backend_2"].status = BackendStatus.HEALTHY
            
            # Simula falhas no backend primário
            lb.metrics["backend_1"].consecutive_failures = 3
            lb.metrics["backend_1"].status = BackendStatus.UNHEALTHY
            
            # Verifica se failover foi disparado
            await lb._trigger_failover("backend_1")
            assert lb.metrics["backend_1"].status == BackendStatus.FAILING_OVER
    
    @pytest.mark.asyncio
    async def test_sticky_sessions_scenario(self, temp_config_file):
        """Testa cenário de sticky sessions"""
        with patch('infrastructure.load_balancing.advanced_lb.asyncio.create_task'):
            lb = AdvancedLoadBalancer(temp_config_file)
            
            # Configura backends saudáveis
            lb.metrics["backend_1"].status = BackendStatus.HEALTHY
            lb.metrics["backend_2"].status = BackendStatus.HEALTHY
            
            session_id = "user_session_123"
            
            # Primeira requisição
            backend1 = lb.select_backend(session_id=session_id)
            
            # Requisições subsequentes devem usar o mesmo backend
            for _ in range(5):
                backend = lb.select_backend(session_id=session_id)
                assert backend == backend1

# Testes de performance
class TestPerformance:
    """Testes de performance"""
    
    @pytest.mark.asyncio
    async def test_backend_selection_performance(self, temp_config_file):
        """Testa performance da seleção de backends"""
        with patch('infrastructure.load_balancing.advanced_lb.asyncio.create_task'):
            lb = AdvancedLoadBalancer(temp_config_file)
            
            # Configura backends saudáveis
            lb.metrics["backend_1"].status = BackendStatus.HEALTHY
            lb.metrics["backend_2"].status = BackendStatus.HEALTHY
            
            start_time = datetime.now()
            
            # Simula 1000 seleções
            for _ in range(1000):
                lb.select_backend()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Deve completar em menos de 1 segundo
            assert duration < 1.0
    
    @pytest.mark.asyncio
    async def test_metrics_recording_performance(self, temp_config_file):
        """Testa performance do registro de métricas"""
        with patch('infrastructure.load_balancing.advanced_lb.asyncio.create_task'):
            lb = AdvancedLoadBalancer(temp_config_file)
            
            start_time = datetime.now()
            
            # Simula 1000 registros de métricas
            for _ in range(1000):
                lb.record_request("backend_1", 0.1, success=True)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Deve completar em menos de 1 segundo
            assert duration < 1.0 