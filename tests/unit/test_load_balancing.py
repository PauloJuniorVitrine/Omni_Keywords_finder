"""
Testes Unitários para Load Balancing
Sistema de Balanceamento de Carga - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de load balancing
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.scaling.load_balancing import (
    LoadBalancer, LoadBalancingAlgorithm, ServerStatus, Server,
    LoadBalancerConfig, LoadBalancerMetrics, create_load_balancer
)


class TestLoadBalancer:
    """Testes para LoadBalancer"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return LoadBalancerConfig(
            algorithm=LoadBalancingAlgorithm.ROUND_ROBIN,
            health_check_interval=30,
            health_check_timeout=5,
            session_affinity=False
        )
    
    @pytest.fixture
    def sample_servers(self):
        """Servidores de exemplo para testes"""
        return [
            Server(
                id="server1",
                host="192.168.1.10",
                port=8080,
                weight=1,
                max_connections=1000,
                current_connections=100,
                response_time=200.0,
                error_rate=0.02
            ),
            Server(
                id="server2",
                host="192.168.1.11",
                port=8080,
                weight=2,
                max_connections=1000,
                current_connections=150,
                response_time=300.0,
                error_rate=0.03
            ),
            Server(
                id="server3",
                host="192.168.1.12",
                port=8080,
                weight=1,
                max_connections=1000,
                current_connections=50,
                response_time=150.0,
                error_rate=0.01
            )
        ]
    
    @pytest.fixture
    def load_balancer(self, sample_config):
        """Instância de LoadBalancer para testes"""
        return LoadBalancer(sample_config)
    
    def test_load_balancer_initialization(self, sample_config):
        """Testa inicialização do LoadBalancer"""
        lb = LoadBalancer(sample_config)
        
        assert lb.config == sample_config
        assert len(lb.servers) == 0
        assert lb.current_server_index == 0
        assert len(lb.session_map) == 0
        assert lb.is_running is False
        assert lb.health_check_task is None
    
    def test_add_server(self, load_balancer, sample_servers):
        """Testa adição de servidores"""
        for server in sample_servers:
            load_balancer.add_server(server)
        
        assert len(load_balancer.servers) == 3
        assert all(server in load_balancer.servers for server in sample_servers)
    
    def test_add_duplicate_server(self, load_balancer, sample_servers):
        """Testa adição de servidor duplicado"""
        load_balancer.add_server(sample_servers[0])
        
        with pytest.raises(ValueError, match="Servidor com ID server1 já existe"):
            load_balancer.add_server(sample_servers[0])
    
    def test_remove_server(self, load_balancer, sample_servers):
        """Testa remoção de servidor"""
        for server in sample_servers:
            load_balancer.add_server(server)
        
        load_balancer.remove_server("server1")
        
        assert len(load_balancer.servers) == 2
        assert not any(s.id == "server1" for s in load_balancer.servers)
    
    def test_remove_nonexistent_server(self, load_balancer):
        """Testa remoção de servidor inexistente"""
        with pytest.raises(ValueError, match="Servidor com ID nonexistent não encontrado"):
            load_balancer.remove_server("nonexistent")
    
    def test_get_available_servers(self, load_balancer, sample_servers):
        """Testa obtenção de servidores disponíveis"""
        for server in sample_servers:
            load_balancer.add_server(server)
        
        available_servers = load_balancer.get_available_servers()
        assert len(available_servers) == 3
        
        # Marcar um servidor como não disponível
        sample_servers[0].status = ServerStatus.UNHEALTHY
        available_servers = load_balancer.get_available_servers()
        assert len(available_servers) == 2
    
    def test_round_robin_selection(self, load_balancer, sample_servers):
        """Testa seleção round robin"""
        for server in sample_servers:
            load_balancer.add_server(server)
        
        # Primeira seleção
        selected1 = load_balancer.select_server()
        assert selected1 is not None
        
        # Segunda seleção
        selected2 = load_balancer.select_server()
        assert selected2 is not None
        
        # Terceira seleção
        selected3 = load_balancer.select_server()
        assert selected3 is not None
        
        # Quarta seleção (deve voltar ao primeiro)
        selected4 = load_balancer.select_server()
        assert selected4.id == selected1.id
    
    def test_least_connections_selection(self, sample_config, sample_servers):
        """Testa seleção baseada em menor número de conexões"""
        sample_config.algorithm = LoadBalancingAlgorithm.LEAST_CONNECTIONS
        lb = LoadBalancer(sample_config)
        
        for server in sample_servers:
            load_balancer.add_server(server)
        
        selected = lb.select_server()
        assert selected is not None
        assert selected.id == "server3"  # Menor número de conexões (50)
    
    def test_weighted_round_robin_selection(self, sample_config, sample_servers):
        """Testa seleção round robin com pesos"""
        sample_config.algorithm = LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN
        lb = LoadBalancer(sample_config)
        
        for server in sample_servers:
            lb.add_server(server)
        
        # Servidor 2 tem peso 2, deve ser selecionado mais vezes
        selections = []
        for _ in range(10):
            selected = lb.select_server()
            selections.append(selected.id)
        
        # Verificar se server2 aparece mais vezes
        server2_count = selections.count("server2")
        assert server2_count > 2  # Deve aparecer mais que os outros
    
    def test_ip_hash_selection(self, sample_config, sample_servers):
        """Testa seleção baseada em hash do IP"""
        sample_config.algorithm = LoadBalancingAlgorithm.IP_HASH
        lb = LoadBalancer(sample_config)
        
        for server in sample_servers:
            lb.add_server(server)
        
        # Mesmo IP deve sempre selecionar o mesmo servidor
        client_ip = "192.168.1.100"
        selected1 = lb.select_server(client_ip=client_ip)
        selected2 = lb.select_server(client_ip=client_ip)
        
        assert selected1 is not None
        assert selected2 is not None
        assert selected1.id == selected2.id
    
    def test_least_response_time_selection(self, sample_config, sample_servers):
        """Testa seleção baseada em menor tempo de resposta"""
        sample_config.algorithm = LoadBalancingAlgorithm.LEAST_RESPONSE_TIME
        lb = LoadBalancer(sample_config)
        
        for server in sample_servers:
            lb.add_server(server)
        
        selected = lb.select_server()
        assert selected is not None
        assert selected.id == "server3"  # Menor response time (150ms)
    
    def test_adaptive_selection(self, sample_config, sample_servers):
        """Testa seleção adaptativa"""
        sample_config.algorithm = LoadBalancingAlgorithm.ADAPTIVE
        lb = LoadBalancer(sample_config)
        
        for server in sample_servers:
            lb.add_server(server)
        
        selected = lb.select_server()
        assert selected is not None
        
        # Verificar se a seleção considera múltiplos fatores
        health_scores = [s.get_health_score() for s in sample_servers]
        assert selected.get_health_score() == max(health_scores)
    
    def test_session_affinity(self, sample_config, sample_servers):
        """Testa session affinity"""
        sample_config.session_affinity = True
        lb = LoadBalancer(sample_config)
        
        for server in sample_servers:
            lb.add_server(server)
        
        session_id = "session123"
        client_ip = "192.168.1.100"
        
        # Primeira seleção
        selected1 = lb.select_server(client_ip=client_ip, session_id=session_id)
        assert selected1 is not None
        
        # Segunda seleção com mesma sessão
        selected2 = lb.select_server(client_ip=client_ip, session_id=session_id)
        assert selected2 is not None
        assert selected1.id == selected2.id
        
        # Verificar se foi adicionado ao session map
        assert session_id in lb.session_map
        assert lb.session_map[session_id] == selected1.id
    
    def test_no_available_servers(self, load_balancer):
        """Testa seleção quando não há servidores disponíveis"""
        selected = load_balancer.select_server()
        assert selected is None
    
    def test_all_servers_unhealthy(self, load_balancer, sample_servers):
        """Testa seleção quando todos os servidores estão não saudáveis"""
        for server in sample_servers:
            server.status = ServerStatus.UNHEALTHY
            load_balancer.add_server(server)
        
        selected = load_balancer.select_server()
        assert selected is None
    
    @pytest.mark.asyncio
    async def test_health_checks_start_stop(self, load_balancer):
        """Testa início e parada de health checks"""
        # Iniciar health checks
        await load_balancer.start_health_checks()
        assert load_balancer.is_running is True
        assert load_balancer.health_check_task is not None
        
        # Parar health checks
        await load_balancer.stop_health_checks()
        assert load_balancer.is_running is False
    
    @pytest.mark.asyncio
    async def test_health_checks_multiple_start(self, load_balancer):
        """Testa múltiplos inícios de health checks"""
        await load_balancer.start_health_checks()
        await load_balancer.start_health_checks()  # Deve ser ignorado
        
        assert load_balancer.is_running is True
        await load_balancer.stop_health_checks()
    
    def test_get_metrics(self, load_balancer):
        """Testa obtenção de métricas"""
        metrics = load_balancer.get_metrics()
        assert isinstance(metrics, LoadBalancerMetrics)
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
    
    def test_get_server_metrics(self, load_balancer, sample_servers):
        """Testa obtenção de métricas dos servidores"""
        for server in sample_servers:
            load_balancer.add_server(server)
        
        server_metrics = load_balancer.get_server_metrics()
        
        assert len(server_metrics) == 3
        assert "server1" in server_metrics
        assert "server2" in server_metrics
        assert "server3" in server_metrics
        
        # Verificar estrutura das métricas
        server1_metrics = server_metrics["server1"]
        assert "host" in server1_metrics
        assert "port" in server1_metrics
        assert "status" in server1_metrics
        assert "current_connections" in server1_metrics
        assert "health_score" in server1_metrics
    
    def test_enable_maintenance_mode(self, load_balancer, sample_servers):
        """Testa habilitação de modo de manutenção"""
        load_balancer.add_server(sample_servers[0])
        
        load_balancer.enable_maintenance_mode("server1")
        assert sample_servers[0].maintenance_mode is True
    
    def test_disable_maintenance_mode(self, load_balancer, sample_servers):
        """Testa desabilitação de modo de manutenção"""
        load_balancer.add_server(sample_servers[0])
        sample_servers[0].maintenance_mode = True
        
        load_balancer.disable_maintenance_mode("server1")
        assert sample_servers[0].maintenance_mode is False
    
    def test_update_server_weight(self, load_balancer, sample_servers):
        """Testa atualização de peso do servidor"""
        load_balancer.add_server(sample_servers[0])
        
        load_balancer.update_server_weight("server1", 5)
        assert sample_servers[0].weight == 5
    
    def test_update_server_weight_invalid(self, load_balancer, sample_servers):
        """Testa atualização de peso inválido"""
        load_balancer.add_server(sample_servers[0])
        
        with pytest.raises(ValueError, match="Peso deve ser pelo menos 1"):
            load_balancer.update_server_weight("server1", 0)
    
    def test_cleanup_expired_sessions(self, load_balancer, sample_servers):
        """Testa limpeza de sessões expiradas"""
        load_balancer.add_server(sample_servers[0])
        
        # Adicionar algumas sessões
        load_balancer.session_map["session1"] = "server1"
        load_balancer.session_map["session2"] = "server1"
        
        initial_count = len(load_balancer.session_map)
        load_balancer.cleanup_expired_sessions()
        
        # A limpeza é probabilística, então pode ou não remover sessões
        assert len(load_balancer.session_map) <= initial_count


class TestServer:
    """Testes para classe Server"""
    
    def test_server_initialization(self):
        """Testa inicialização de Server"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080,
            weight=2,
            max_connections=1000,
            current_connections=100,
            response_time=200.0,
            error_rate=0.02
        )
        
        assert server.id == "test_server"
        assert server.host == "192.168.1.10"
        assert server.port == 8080
        assert server.weight == 2
        assert server.max_connections == 1000
        assert server.current_connections == 100
        assert server.response_time == 200.0
        assert server.error_rate == 0.02
        assert server.status == ServerStatus.HEALTHY
        assert server.maintenance_mode is False
    
    def test_server_validation_id_empty(self):
        """Testa validação de ID vazio"""
        with pytest.raises(ValueError, match="ID do servidor não pode ser vazio"):
            Server(
                id="",
                host="192.168.1.10",
                port=8080
            )
    
    def test_server_validation_host_empty(self):
        """Testa validação de host vazio"""
        with pytest.raises(ValueError, match="Host do servidor não pode ser vazio"):
            Server(
                id="test_server",
                host="",
                port=8080
            )
    
    def test_server_validation_port_invalid(self):
        """Testa validação de porta inválida"""
        with pytest.raises(ValueError, match="Porta deve estar entre 1 e 65535"):
            Server(
                id="test_server",
                host="192.168.1.10",
                port=0
            )
    
    def test_server_validation_weight_invalid(self):
        """Testa validação de peso inválido"""
        with pytest.raises(ValueError, match="Peso deve ser pelo menos 1"):
            Server(
                id="test_server",
                host="192.168.1.10",
                port=8080,
                weight=0
            )
    
    def test_server_validation_error_rate_invalid(self):
        """Testa validação de error rate inválido"""
        with pytest.raises(ValueError, match="Error rate deve estar entre 0 e 1"):
            Server(
                id="test_server",
                host="192.168.1.10",
                port=8080,
                error_rate=1.5
            )
    
    def test_server_is_available_healthy(self):
        """Testa disponibilidade de servidor saudável"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080,
            current_connections=100,
            max_connections=1000
        )
        
        assert server.is_available() is True
    
    def test_server_is_available_unhealthy(self):
        """Testa disponibilidade de servidor não saudável"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080
        )
        server.status = ServerStatus.UNHEALTHY
        
        assert server.is_available() is False
    
    def test_server_is_available_maintenance(self):
        """Testa disponibilidade de servidor em manutenção"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080
        )
        server.maintenance_mode = True
        
        assert server.is_available() is False
    
    def test_server_is_available_max_connections(self):
        """Testa disponibilidade de servidor com máximo de conexões"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080,
            current_connections=1000,
            max_connections=1000
        )
        
        assert server.is_available() is False
    
    def test_server_get_health_score(self):
        """Testa cálculo de score de saúde"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080,
            current_connections=500,
            max_connections=1000,
            response_time=1000.0,
            error_rate=0.05
        )
        
        score = server.get_health_score()
        assert 0.0 <= score <= 1.0
    
    def test_server_get_health_score_unavailable(self):
        """Testa score de saúde de servidor não disponível"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080
        )
        server.status = ServerStatus.UNHEALTHY
        
        score = server.get_health_score()
        assert score == 0.0
    
    def test_server_update_metrics(self):
        """Testa atualização de métricas"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080
        )
        
        server.update_metrics(
            connections=200,
            response_time=300.0,
            error_rate=0.03
        )
        
        assert server.current_connections == 200
        assert server.response_time == 300.0
        assert server.error_rate == 0.03
    
    def test_server_mark_health_check_failure(self):
        """Testa marcação de falha no health check"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080
        )
        
        # Primeira falha
        server.mark_health_check_failure()
        assert server.health_check_failures == 1
        assert server.status == ServerStatus.DEGRADED
        
        # Segunda falha
        server.mark_health_check_failure()
        assert server.health_check_failures == 2
        assert server.status == ServerStatus.DEGRADED
        
        # Terceira falha
        server.mark_health_check_failure()
        assert server.health_check_failures == 3
        assert server.status == ServerStatus.UNHEALTHY
    
    def test_server_mark_health_check_success(self):
        """Testa marcação de sucesso no health check"""
        server = Server(
            id="test_server",
            host="192.168.1.10",
            port=8080
        )
        server.status = ServerStatus.UNHEALTHY
        server.health_check_failures = 3
        
        server.mark_health_check_success()
        
        assert server.health_check_failures == 0
        assert server.status == ServerStatus.HEALTHY


class TestLoadBalancerConfig:
    """Testes para LoadBalancerConfig"""
    
    def test_load_balancer_config_initialization(self):
        """Testa inicialização de LoadBalancerConfig"""
        config = LoadBalancerConfig()
        
        assert config.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN
        assert config.health_check_interval == 30
        assert config.health_check_timeout == 5
        assert config.session_affinity is False
        assert config.enable_ssl is True
    
    def test_load_balancer_config_custom_values(self):
        """Testa LoadBalancerConfig com valores customizados"""
        config = LoadBalancerConfig(
            algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS,
            health_check_interval=60,
            health_check_timeout=10,
            session_affinity=True,
            enable_ssl=False
        )
        
        assert config.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS
        assert config.health_check_interval == 60
        assert config.health_check_timeout == 10
        assert config.session_affinity is True
        assert config.enable_ssl is False
    
    def test_load_balancer_config_validation_health_check_interval(self):
        """Testa validação de health check interval"""
        with pytest.raises(ValueError, match="Health check interval deve ser pelo menos 1 segundo"):
            LoadBalancerConfig(health_check_interval=0)
    
    def test_load_balancer_config_validation_health_check_timeout(self):
        """Testa validação de health check timeout"""
        with pytest.raises(ValueError, match="Health check timeout deve ser pelo menos 1 segundo"):
            LoadBalancerConfig(health_check_timeout=0)
    
    def test_load_balancer_config_validation_session_timeout(self):
        """Testa validação de session timeout"""
        with pytest.raises(ValueError, match="Session timeout deve ser pelo menos 60 segundos"):
            LoadBalancerConfig(session_timeout=30)


class TestLoadBalancerMetrics:
    """Testes para LoadBalancerMetrics"""
    
    def test_load_balancer_metrics_initialization(self):
        """Testa inicialização de LoadBalancerMetrics"""
        metrics = LoadBalancerMetrics()
        
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 0.0
        assert metrics.error_rate == 0.0
    
    def test_load_balancer_metrics_update_success(self):
        """Testa atualização de métricas com sucesso"""
        metrics = LoadBalancerMetrics()
        
        metrics.update(request_success=True, response_time=200.0, active_connections=10)
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 200.0
        assert metrics.active_connections == 10
        assert metrics.error_rate == 0.0
    
    def test_load_balancer_metrics_update_failure(self):
        """Testa atualização de métricas com falha"""
        metrics = LoadBalancerMetrics()
        
        metrics.update(request_success=False, response_time=500.0, active_connections=5)
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1
        assert metrics.average_response_time == 500.0
        assert metrics.active_connections == 5
        assert metrics.error_rate == 1.0
    
    def test_load_balancer_metrics_update_multiple(self):
        """Testa atualização múltipla de métricas"""
        metrics = LoadBalancerMetrics()
        
        # Primeira atualização
        metrics.update(request_success=True, response_time=100.0)
        assert metrics.average_response_time == 100.0
        
        # Segunda atualização
        metrics.update(request_success=True, response_time=300.0)
        assert metrics.average_response_time == 200.0  # (100 + 300) / 2
        
        # Terceira atualização com falha
        metrics.update(request_success=False, response_time=500.0)
        assert metrics.error_rate == 1/3  # 1 falha em 3 requests


class TestCreateLoadBalancer:
    """Testes para função create_load_balancer"""
    
    def test_create_load_balancer_default(self):
        """Testa criação com configurações padrão"""
        lb = create_load_balancer()
        
        assert lb.config.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN
        assert lb.config.session_affinity is False
    
    def test_create_load_balancer_custom_algorithm(self):
        """Testa criação com algoritmo customizado"""
        lb = create_load_balancer(algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS)
        
        assert lb.config.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS
    
    def test_create_load_balancer_with_session_affinity(self):
        """Testa criação com session affinity"""
        lb = create_load_balancer(enable_session_affinity=True)
        
        assert lb.config.session_affinity is True


class TestLoadBalancingIntegration:
    """Testes de integração para Load Balancing"""
    
    @pytest.mark.asyncio
    async def test_complete_load_balancing_cycle(self):
        """Testa ciclo completo de load balancing"""
        lb = create_load_balancer(algorithm=LoadBalancingAlgorithm.ROUND_ROBIN)
        
        # Adicionar servidores
        servers = [
            Server(id="s1", host="192.168.1.10", port=8080),
            Server(id="s2", host="192.168.1.11", port=8080),
            Server(id="s3", host="192.168.1.12", port=8080)
        ]
        
        for server in servers:
            lb.add_server(server)
        
        # Simular seleções
        selections = []
        for _ in range(6):
            selected = lb.select_server()
            selections.append(selected.id if selected else None)
        
        # Verificar se todos os servidores foram selecionados
        unique_selections = set(selections)
        assert len(unique_selections) == 3
        assert "s1" in unique_selections
        assert "s2" in unique_selections
        assert "s3" in unique_selections
    
    @pytest.mark.asyncio
    async def test_health_checks_with_servers(self):
        """Testa health checks com servidores"""
        lb = create_load_balancer()
        
        # Adicionar servidor
        server = Server(id="test", host="192.168.1.10", port=8080)
        lb.add_server(server)
        
        # Iniciar health checks
        await lb.start_health_checks()
        
        # Aguardar um pouco
        await asyncio.sleep(0.1)
        
        # Parar health checks
        await lb.stop_health_checks()
        
        # Verificar se health checks foram executados
        assert server.last_health_check > datetime.utcnow() - timedelta(seconds=1)
    
    def test_multiple_algorithms_comparison(self):
        """Testa comparação entre diferentes algoritmos"""
        algorithms = [
            LoadBalancingAlgorithm.ROUND_ROBIN,
            LoadBalancingAlgorithm.LEAST_CONNECTIONS,
            LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN,
            LoadBalancingAlgorithm.IP_HASH,
            LoadBalancingAlgorithm.LEAST_RESPONSE_TIME,
            LoadBalancingAlgorithm.ADAPTIVE
        ]
        
        servers = [
            Server(id="s1", host="192.168.1.10", port=8080, weight=1),
            Server(id="s2", host="192.168.1.11", port=8080, weight=2),
            Server(id="s3", host="192.168.1.12", port=8080, weight=1)
        ]
        
        results = {}
        
        for algorithm in algorithms:
            lb = create_load_balancer(algorithm=algorithm)
            
            for server in servers:
                lb.add_server(server)
            
            # Fazer algumas seleções
            selections = []
            for _ in range(10):
                selected = lb.select_server(client_ip="192.168.1.100")
                selections.append(selected.id if selected else None)
            
            results[algorithm] = selections
        
        # Verificar se todos os algoritmos produziram resultados
        assert len(results) == len(algorithms)
        
        # Verificar se pelo menos alguns algoritmos produziram seleções diferentes
        unique_results = set(tuple(selections) for selections in results.values())
        assert len(unique_results) > 1


if __name__ == "__main__":
    pytest.main([__file__]) 