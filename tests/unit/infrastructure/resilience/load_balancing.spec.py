from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Testes Unitários - Load Balancing Avançado
Tracing ID: IMP004_LOAD_BALANCING_TESTS_001
Data: 2025-01-27
Versão: 1.0
Status: Em Implementação

Testes abrangentes para o sistema de load balancing avançado
"""

import pytest
import unittest.mock as mock
from unittest.mock import Mock, patch, MagicMock
import json
import yaml
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path

# Importa o módulo a ser testado
import sys
sys.path.append('infrastructure/load_balancing')
from intelligent_load_balancer import (
    IntelligentLoadBalancer, 
    LoadBalancerConfig, 
    Server, 
    ServerStatus,
    LoadBalancingStrategy,
    Request,
    LoadBalancingDecision
)

class TestIntelligentLoadBalancer:
    """Testes para IntelligentLoadBalancer"""
    
    @pytest.fixture
    def mock_config(self):
        """Configuração mock para testes"""
        return LoadBalancerConfig(
            strategy=LoadBalancingStrategy.ROUND_ROBIN,
            health_check_interval=30,
            health_check_timeout=5,
            max_retries=3,
            session_sticky=True,
            session_timeout=300,
            enable_ml_optimization=True,
            ml_update_interval=60,
            prediction_horizon=300
        )
    
    @pytest.fixture
    def mock_servers(self):
        """Servidores mock para testes"""
        return [
            Server(
                id="server-1",
                host="192.168.1.10",
                port=8080,
                weight=1.0,
                max_connections=1000,
                current_connections=50,
                response_time=100.0,
                cpu_usage=30.0,
                memory_usage=40.0,
                status=ServerStatus.HEALTHY
            ),
            Server(
                id="server-2",
                host="192.168.1.11",
                port=8080,
                weight=2.0,
                max_connections=1000,
                current_connections=30,
                response_time=80.0,
                cpu_usage=25.0,
                memory_usage=35.0,
                status=ServerStatus.HEALTHY
            ),
            Server(
                id="server-3",
                host="192.168.1.12",
                port=8080,
                weight=1.5,
                max_connections=1000,
                current_connections=80,
                response_time=150.0,
                cpu_usage=60.0,
                memory_usage=70.0,
                status=ServerStatus.DEGRADED
            )
        ]
    
    @pytest.fixture
    def mock_request(self):
        """Request mock para testes"""
        return Request(
            id="req-001",
            client_ip="10.0.0.1",
            timestamp=datetime.now(),
            method="GET",
            path="/api/test",
            headers={"User-Agent": "test-client"},
            payload_size=1024,
            priority=1
        )
    
    def test_init(self, mock_config):
        """Testa inicialização do load balancer"""
        lb = IntelligentLoadBalancer(mock_config)
        
        assert lb.config == mock_config
        assert len(lb.servers) == 0
        assert lb.current_index == 0
        assert lb.health_checker is not None
        assert lb.load_predictor is not None
    
    def test_add_server(self, mock_config, mock_servers):
        """Testa adição de servidor"""
        lb = IntelligentLoadBalancer(mock_config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        assert len(lb.servers) == 3
        assert lb.servers[0].id == "server-1"
        assert lb.servers[1].id == "server-2"
        assert lb.servers[2].id == "server-3"
    
    def test_remove_server(self, mock_config, mock_servers):
        """Testa remoção de servidor"""
        lb = IntelligentLoadBalancer(mock_config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        lb.remove_server("server-2")
        
        assert len(lb.servers) == 2
        assert lb.servers[0].id == "server-1"
        assert lb.servers[1].id == "server-3"
    
    def test_round_robin_strategy(self, mock_config, mock_servers, mock_request):
        """Testa estratégia round robin"""
        lb = IntelligentLoadBalancer(mock_config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        # Primeira requisição
        decision1 = lb.get_server(mock_request)
        assert decision1.selected_server == "server-1"
        assert decision1.strategy_used == "round_robin"
        
        # Segunda requisição
        decision2 = lb.get_server(mock_request)
        assert decision2.selected_server == "server-2"
        
        # Terceira requisição
        decision3 = lb.get_server(mock_request)
        assert decision3.selected_server == "server-3"
        
        # Quarta requisição (volta ao início)
        decision4 = lb.get_server(mock_request)
        assert decision4.selected_server == "server-1"
    
    def test_least_connections_strategy(self, mock_config, mock_servers, mock_request):
        """Testa estratégia least connections"""
        config = LoadBalancerConfig(
            strategy=LoadBalancingStrategy.LEAST_CONNECTIONS,
            health_check_interval=30,
            health_check_timeout=5,
            max_retries=3,
            session_sticky=False,
            session_timeout=300,
            enable_ml_optimization=False,
            ml_update_interval=60,
            prediction_horizon=300
        )
        
        lb = IntelligentLoadBalancer(config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        decision = lb.get_server(mock_request)
        assert decision.selected_server == "server-2"  # Menos conexões (30)
        assert decision.strategy_used == "least_connections"
    
    def test_weighted_round_robin_strategy(self, mock_config, mock_servers, mock_request):
        """Testa estratégia weighted round robin"""
        config = LoadBalancerConfig(
            strategy=LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
            health_check_interval=30,
            health_check_timeout=5,
            max_retries=3,
            session_sticky=False,
            session_timeout=300,
            enable_ml_optimization=False,
            ml_update_interval=60,
            prediction_horizon=300
        )
        
        lb = IntelligentLoadBalancer(config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        # Com pesos: server-1 (1.0), server-2 (2.0), server-3 (1.5)
        # Padrão esperado: server-2, server-2, server-3, server-1, server-2, server-2, server-3...
        
        decisions = []
        for _ in range(10):
            decision = lb.get_server(mock_request)
            decisions.append(decision.selected_server)
        
        # Verificar que server-2 (peso 2.0) aparece mais vezes
        server2_count = decisions.count("server-2")
        server1_count = decisions.count("server-1")
        server3_count = decisions.count("server-3")
        
        assert server2_count > server1_count
        assert server2_count > server3_count
    
    def test_ip_hash_strategy(self, mock_config, mock_servers):
        """Testa estratégia IP hash"""
        config = LoadBalancerConfig(
            strategy=LoadBalancingStrategy.IP_HASH,
            health_check_interval=30,
            health_check_timeout=5,
            max_retries=3,
            session_sticky=False,
            session_timeout=300,
            enable_ml_optimization=False,
            ml_update_interval=60,
            prediction_horizon=300
        )
        
        lb = IntelligentLoadBalancer(config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        # Mesmo IP deve sempre ir para o mesmo servidor
        request1 = Request(
            id="req-001",
            client_ip="10.0.0.1",
            timestamp=datetime.now(),
            method="GET",
            path="/api/test",
            headers={},
            payload_size=0,
            priority=1
        )
        
        request2 = Request(
            id="req-002",
            client_ip="10.0.0.1",
            timestamp=datetime.now(),
            method="POST",
            path="/api/test",
            headers={},
            payload_size=0,
            priority=1
        )
        
        decision1 = lb.get_server(request1)
        decision2 = lb.get_server(request2)
        
        assert decision1.selected_server == decision2.selected_server
        assert decision1.strategy_used == "ip_hash"
    
    def test_least_response_time_strategy(self, mock_config, mock_servers, mock_request):
        """Testa estratégia least response time"""
        config = LoadBalancerConfig(
            strategy=LoadBalancingStrategy.LEAST_RESPONSE_TIME,
            health_check_interval=30,
            health_check_timeout=5,
            max_retries=3,
            session_sticky=False,
            session_timeout=300,
            enable_ml_optimization=False,
            ml_update_interval=60,
            prediction_horizon=300
        )
        
        lb = IntelligentLoadBalancer(config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        decision = lb.get_server(mock_request)
        assert decision.selected_server == "server-2"  # Menor response time (80ms)
        assert decision.strategy_used == "least_response_time"
    
    @patch('infrastructure.load_balancing.intelligent_load_balancer.LoadPredictor')
    def test_ml_optimized_strategy(self, mock_load_predictor, mock_config, mock_servers, mock_request):
        """Testa estratégia ML otimizada"""
        config = LoadBalancerConfig(
            strategy=LoadBalancingStrategy.ML_OPTIMIZED,
            health_check_interval=30,
            health_check_timeout=5,
            max_retries=3,
            session_sticky=False,
            session_timeout=300,
            enable_ml_optimization=True,
            ml_update_interval=60,
            prediction_horizon=300
        )
        
        lb = IntelligentLoadBalancer(config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        # Mock do preditor
        mock_predictor_instance = Mock()
        mock_predictor_instance.predict_load.return_value = 50.0
        lb.load_predictor = mock_predictor_instance
        
        decision = lb.get_server(mock_request)
        assert decision.strategy_used == "ml_optimized"
        assert decision.confidence_score > 0
    
    def test_health_check_exclusion(self, mock_config, mock_servers, mock_request):
        """Testa exclusão de servidores não saudáveis"""
        lb = IntelligentLoadBalancer(mock_config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        # Marcar servidor como unhealthy
        lb.servers[0].status = ServerStatus.UNHEALTHY
        
        decision = lb.get_server(mock_request)
        # Não deve selecionar servidor unhealthy
        assert decision.selected_server != "server-1"
    
    def test_session_sticky(self, mock_config, mock_servers):
        """Testa sticky sessions"""
        config = LoadBalancerConfig(
            strategy=LoadBalancingStrategy.ROUND_ROBIN,
            health_check_interval=30,
            health_check_timeout=5,
            max_retries=3,
            session_sticky=True,
            session_timeout=300,
            enable_ml_optimization=False,
            ml_update_interval=60,
            prediction_horizon=300
        )
        
        lb = IntelligentLoadBalancer(config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        # Mesmo cliente deve ir para o mesmo servidor
        request1 = Request(
            id="req-001",
            client_ip="10.0.0.1",
            timestamp=datetime.now(),
            method="GET",
            path="/api/test",
            headers={},
            payload_size=0,
            priority=1
        )
        
        request2 = Request(
            id="req-002",
            client_ip="10.0.0.1",
            timestamp=datetime.now(),
            method="POST",
            path="/api/test",
            headers={},
            payload_size=0,
            priority=1
        )
        
        decision1 = lb.get_server(request1)
        decision2 = lb.get_server(request2)
        
        assert decision1.selected_server == decision2.selected_server
    
    def test_update_server_metrics(self, mock_config, mock_servers):
        """Testa atualização de métricas do servidor"""
        lb = IntelligentLoadBalancer(mock_config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        metrics = {
            'cpu_usage': 45.0,
            'memory_usage': 55.0,
            'response_time': 120.0,
            'current_connections': 75,
            'total_requests': 1000,
            'successful_requests': 950,
            'failed_requests': 50
        }
        
        lb.update_server_metrics("server-1", metrics)
        
        server = next(string_data for string_data in lb.servers if string_data.id == "server-1")
        assert server.cpu_usage == 45.0
        assert server.memory_usage == 55.0
        assert server.response_time == 120.0
        assert server.current_connections == 75
        assert server.total_requests == 1000
        assert server.successful_requests == 950
        assert server.failed_requests == 50
    
    def test_get_status_report(self, mock_config, mock_servers):
        """Testa relatório de status"""
        lb = IntelligentLoadBalancer(mock_config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        report = lb.get_status_report()
        
        assert "total_servers" in report
        assert "healthy_servers" in report
        assert "unhealthy_servers" in report
        assert "degraded_servers" in report
        assert "total_connections" in report
        assert "average_response_time" in report
        assert "servers" in report
        
        assert report["total_servers"] == 3
        assert report["healthy_servers"] == 2
        assert report["degraded_servers"] == 1
        assert report["unhealthy_servers"] == 0
    
    def test_get_performance_metrics(self, mock_config, mock_servers):
        """Testa métricas de performance"""
        lb = IntelligentLoadBalancer(mock_config)
        
        for server in mock_servers:
            lb.add_server(server)
        
        # Simular algumas requisições
        request = Request(
            id="req-001",
            client_ip="10.0.0.1",
            timestamp=datetime.now(),
            method="GET",
            path="/api/test",
            headers={},
            payload_size=0,
            priority=1
        )
        
        for _ in range(10):
            lb.get_server(request)
        
        metrics = lb.get_performance_metrics()
        
        assert "total_requests" in metrics
        assert "requests_per_second" in metrics
        assert "average_response_time" in metrics
        assert "success_rate" in metrics
        assert "ml_accuracy" in metrics
        
        assert metrics["total_requests"] == 10
    
    @patch('threading.Thread')
    def test_start_health_checks(self, mock_thread, mock_config):
        """Testa início dos health checks"""
        lb = IntelligentLoadBalancer(mock_config)
        
        lb.start_health_checks()
        
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_stop_health_checks(self, mock_config):
        """Testa parada dos health checks"""
        lb = IntelligentLoadBalancer(mock_config)
        
        # Simular health checks ativos
        lb.health_check_thread = Mock()
        lb.health_check_running = True
        
        lb.stop_health_checks()
        
        assert lb.health_check_running is False
        lb.health_check_thread.join.assert_called_once()

class TestLoadBalancingStrategy:
    """Testes para estratégias de load balancing"""
    
    def test_round_robin(self):
        """Testa estratégia round robin"""
        servers = [
            Server(id="s1", host="192.168.1.10", port=8080),
            Server(id="s2", host="192.168.1.11", port=8080),
            Server(id="s3", host="192.168.1.12", port=8080)
        ]
        
        # Primeira chamada
        server, index = LoadBalancingStrategy.round_robin(servers, 0)
        assert server.id == "s1"
        assert index == 1
        
        # Segunda chamada
        server, index = LoadBalancingStrategy.round_robin(servers, 1)
        assert server.id == "s2"
        assert index == 2
        
        # Terceira chamada
        server, index = LoadBalancingStrategy.round_robin(servers, 2)
        assert server.id == "s3"
        assert index == 0  # Volta ao início
    
    def test_least_connections(self):
        """Testa estratégia least connections"""
        servers = [
            Server(id="s1", host="192.168.1.10", port=8080, current_connections=50),
            Server(id="s2", host="192.168.1.11", port=8080, current_connections=30),
            Server(id="s3", host="192.168.1.12", port=8080, current_connections=80)
        ]
        
        server = LoadBalancingStrategy.least_connections(servers)
        assert server.id == "s2"  # Menos conexões
    
    def test_weighted_round_robin(self):
        """Testa estratégia weighted round robin"""
        servers = [
            Server(id="s1", host="192.168.1.10", port=8080, weight=1.0),
            Server(id="s2", host="192.168.1.11", port=8080, weight=2.0),
            Server(id="s3", host="192.168.1.12", port=8080, weight=1.5)
        ]
        
        # Com pesos diferentes, server-2 deve ser selecionado mais vezes
        selections = []
        current_index = 0
        
        for _ in range(10):
            server, current_index = LoadBalancingStrategy.weighted_round_robin(servers, current_index)
            selections.append(server.id)
        
        # Verificar distribuição
        s1_count = selections.count("s1")
        s2_count = selections.count("s2")
        s3_count = selections.count("s3")
        
        # server-2 deve ter mais seleções devido ao peso maior
        assert s2_count >= s1_count
        assert s2_count >= s3_count
    
    def test_ip_hash(self):
        """Testa estratégia IP hash"""
        servers = [
            Server(id="s1", host="192.168.1.10", port=8080),
            Server(id="s2", host="192.168.1.11", port=8080),
            Server(id="s3", host="192.168.1.12", port=8080)
        ]
        
        # Mesmo IP deve sempre ir para o mesmo servidor
        server1 = LoadBalancingStrategy.ip_hash(servers, "10.0.0.1")
        server2 = LoadBalancingStrategy.ip_hash(servers, "10.0.0.1")
        
        assert server1.id == server2.id
        
        # IPs diferentes podem ir para servidores diferentes
        server3 = LoadBalancingStrategy.ip_hash(servers, "10.0.0.2")
        # Não necessariamente diferente, mas possível
    
    def test_least_response_time(self):
        """Testa estratégia least response time"""
        servers = [
            Server(id="s1", host="192.168.1.10", port=8080, response_time=100.0),
            Server(id="s2", host="192.168.1.11", port=8080, response_time=80.0),
            Server(id="s3", host="192.168.1.12", port=8080, response_time=150.0)
        ]
        
        server = LoadBalancingStrategy.least_response_time(servers)
        assert server.id == "s2"  # Menor response time

class TestHealthChecker:
    """Testes para HealthChecker"""
    
    @pytest.fixture
    def mock_config(self):
        return LoadBalancerConfig(
            strategy=LoadBalancingStrategy.ROUND_ROBIN,
            health_check_interval=30,
            health_check_timeout=5,
            max_retries=3
        )
    
    @pytest.fixture
    def mock_server(self):
        return Server(
            id="test-server",
            host="192.168.1.10",
            port=8080,
            status=ServerStatus.HEALTHY
        )
    
    @patch('socket.socket')
    @patch('requests.get')
    def test_check_server_health_healthy(self, mock_requests_get, mock_socket, mock_config, mock_server):
        """Testa health check para servidor saudável"""
        from infrastructure.load_balancing.intelligent_load_balancer import HealthChecker
        
        # Mock socket conecta com sucesso
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_socket_instance
        
        # Mock HTTP response 200
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response
        
        checker = HealthChecker(mock_config)
        status = checker.check_server_health(mock_server)
        
        assert status == ServerStatus.HEALTHY
    
    @patch('socket.socket')
    def test_check_server_health_offline(self, mock_socket, mock_config, mock_server):
        """Testa health check para servidor offline"""
        from infrastructure.load_balancing.intelligent_load_balancer import HealthChecker
        
        # Mock socket falha na conexão
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 1
        mock_socket.return_value = mock_socket_instance
        
        checker = HealthChecker(mock_config)
        status = checker.check_server_health(mock_server)
        
        assert status == ServerStatus.OFFLINE
    
    @patch('socket.socket')
    @patch('requests.get')
    def test_check_server_health_unhealthy(self, mock_requests_get, mock_socket, mock_config, mock_server):
        """Testa health check para servidor unhealthy"""
        from infrastructure.load_balancing.intelligent_load_balancer import HealthChecker
        
        # Mock socket conecta com sucesso
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_socket_instance
        
        # Mock HTTP response 500
        mock_response = Mock()
        mock_response.status_code = 500
        mock_requests_get.return_value = mock_response
        
        checker = HealthChecker(mock_config)
        status = checker.check_server_health(mock_server)
        
        assert status == ServerStatus.UNHEALTHY
    
    def test_update_server_metrics(self, mock_config, mock_server):
        """Testa atualização de métricas do servidor"""
        from infrastructure.load_balancing.intelligent_load_balancer import HealthChecker
        
        checker = HealthChecker(mock_config)
        
        metrics = {
            'cpu_usage': 45.0,
            'memory_usage': 55.0,
            'response_time': 120.0,
            'current_connections': 75,
            'total_requests': 1000,
            'successful_requests': 950,
            'failed_requests': 50
        }
        
        checker.update_server_metrics(mock_server, metrics)
        
        assert mock_server.cpu_usage == 45.0
        assert mock_server.memory_usage == 55.0
        assert mock_server.response_time == 120.0
        assert mock_server.current_connections == 75
        assert mock_server.total_requests == 1000
        assert mock_server.successful_requests == 950
        assert mock_server.failed_requests == 50
    
    def test_calculate_status_from_metrics_healthy(self, mock_config, mock_server):
        """Testa cálculo de status para servidor saudável"""
        from infrastructure.load_balancing.intelligent_load_balancer import HealthChecker
        
        checker = HealthChecker(mock_config)
        
        # Métricas saudáveis
        mock_server.cpu_usage = 30.0
        mock_server.memory_usage = 40.0
        mock_server.response_time = 80.0
        mock_server.current_connections = 500
        mock_server.max_connections = 1000
        mock_server.total_requests = 1000
        mock_server.successful_requests = 980
        
        status = checker._calculate_status_from_metrics(mock_server)
        assert status == ServerStatus.HEALTHY
    
    def test_calculate_status_from_metrics_unhealthy(self, mock_config, mock_server):
        """Testa cálculo de status para servidor unhealthy"""
        from infrastructure.load_balancing.intelligent_load_balancer import HealthChecker
        
        checker = HealthChecker(mock_config)
        
        # Métricas não saudáveis
        mock_server.cpu_usage = 90.0  # CPU alta
        mock_server.memory_usage = 40.0
        mock_server.response_time = 80.0
        mock_server.current_connections = 500
        mock_server.max_connections = 1000
        mock_server.total_requests = 1000
        mock_server.successful_requests = 980
        
        status = checker._calculate_status_from_metrics(mock_server)
        assert status == ServerStatus.UNHEALTHY
    
    def test_calculate_status_from_metrics_degraded(self, mock_config, mock_server):
        """Testa cálculo de status para servidor degradado"""
        from infrastructure.load_balancing.intelligent_load_balancer import HealthChecker
        
        checker = HealthChecker(mock_config)
        
        # Métricas degradadas (taxa de sucesso baixa)
        mock_server.cpu_usage = 30.0
        mock_server.memory_usage = 40.0
        mock_server.response_time = 80.0
        mock_server.current_connections = 500
        mock_server.max_connections = 1000
        mock_server.total_requests = 1000
        mock_server.successful_requests = 900  # Taxa de sucesso 90%
        
        status = checker._calculate_status_from_metrics(mock_server)
        assert status == ServerStatus.DEGRADED

class TestLoadPredictor:
    """Testes para LoadPredictor"""
    
    @pytest.fixture
    def mock_config(self):
        return LoadBalancerConfig(
            strategy=LoadBalancingStrategy.ML_OPTIMIZED,
            enable_ml_optimization=True,
            ml_update_interval=60,
            prediction_horizon=300
        )
    
    @pytest.fixture
    def mock_server(self):
        return Server(
            id="test-server",
            host="192.168.1.10",
            port=8080,
            current_connections=50
        )
    
    def test_predict_load_without_ml(self, mock_config, mock_server):
        """Testa predição sem ML"""
        from infrastructure.load_balancing.intelligent_load_balancer import LoadPredictor
        
        config = LoadBalancerConfig(
            strategy=LoadBalancingStrategy.ML_OPTIMIZED,
            enable_ml_optimization=False,
            ml_update_interval=60,
            prediction_horizon=300
        )
        
        predictor = LoadPredictor(config)
        predicted_load = predictor.predict_load(mock_server)
        
        assert predicted_load == 50  # Retorna conexões atuais
    
    def test_predict_load_with_insufficient_data(self, mock_config, mock_server):
        """Testa predição com dados insuficientes"""
        from infrastructure.load_balancing.intelligent_load_balancer import LoadPredictor
        
        predictor = LoadPredictor(mock_config)
        predicted_load = predictor.predict_load(mock_server)
        
        assert predicted_load == 50  # Retorna conexões atuais
    
    def test_update_load_history(self, mock_config, mock_server):
        """Testa atualização do histórico de carga"""
        from infrastructure.load_balancing.intelligent_load_balancer import LoadPredictor
        
        predictor = LoadPredictor(mock_config)
        predictor.update_load_history(mock_server)
        
        assert mock_server.id in predictor.load_history
        assert len(predictor.load_history[mock_server.id]) == 1
        assert predictor.load_history[mock_server.id][0]['load'] == 50

if __name__ == '__main__':
    pytest.main([__file__, '-value']) 