"""
Sistema de Load Balancing Inteligente
Tracing ID: LONGTAIL-044
Data: 2024-12-20
Descrição: Sistema de load balancing com ML para otimização de distribuição de carga
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Estratégias de load balancing"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    ML_OPTIMIZED = "ml_optimized"

class ServerStatus(Enum):
    """Status do servidor"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"

@dataclass
class Server:
    """Informações do servidor"""
    id: str
    host: str
    port: int
    weight: float = 1.0
    max_connections: int = 1000
    current_connections: int = 0
    response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    status: ServerStatus = ServerStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.now)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

@dataclass
class LoadBalancerConfig:
    """Configuração do load balancer"""
    strategy: LoadBalancingStrategy
    health_check_interval: int = 30
    health_check_timeout: int = 5
    max_retries: int = 3
    session_sticky: bool = False
    session_timeout: int = 300
    enable_ml_optimization: bool = True
    ml_update_interval: int = 60
    prediction_horizon: int = 300  # 5 minutos

@dataclass
class Request:
    """Informações da requisição"""
    id: str
    client_ip: str
    timestamp: datetime
    method: str
    path: str
    headers: Dict[str, str]
    payload_size: int = 0
    priority: int = 1

@dataclass
class LoadBalancingDecision:
    """Decisão de load balancing"""
    request_id: str
    selected_server: str
    strategy_used: str
    confidence_score: float
    reasoning: str
    timestamp: datetime
    predicted_load: float = 0.0

class HealthChecker:
    """Verificador de saúde dos servidores"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.health_history = {}
    
    def check_server_health(self, server: Server) -> ServerStatus:
        """Verifica saúde de um servidor"""
        try:
            import socket
            import requests
            
            # Teste de conectividade TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.config.health_check_timeout)
            result = sock.connect_ex((server.host, server.port))
            sock.close()
            
            if result != 0:
                return ServerStatus.OFFLINE
            
            # Teste HTTP (se aplicável)
            try:
                response = requests.get(
                    f"http://{server.host}:{server.port}/health",
                    timeout=self.config.health_check_timeout
                )
                
                if response.status_code == 200:
                    return ServerStatus.HEALTHY
                elif response.status_code in [500, 502, 503, 504]:
                    return ServerStatus.UNHEALTHY
                else:
                    return ServerStatus.DEGRADED
                    
            except requests.RequestException:
                return ServerStatus.DEGRADED
                
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do servidor {server.id}: {e}")
            return ServerStatus.OFFLINE
    
    def update_server_metrics(self, server: Server, metrics: Dict[str, Any]):
        """Atualiza métricas do servidor"""
        server.cpu_usage = metrics.get('cpu_usage', server.cpu_usage)
        server.memory_usage = metrics.get('memory_usage', server.memory_usage)
        server.response_time = metrics.get('response_time', server.response_time)
        server.current_connections = metrics.get('current_connections', server.current_connections)
        server.total_requests = metrics.get('total_requests', server.total_requests)
        server.successful_requests = metrics.get('successful_requests', server.successful_requests)
        server.failed_requests = metrics.get('failed_requests', server.failed_requests)
        
        # Calcula status baseado nas métricas
        server.status = self._calculate_status_from_metrics(server)
        server.last_health_check = datetime.now()
    
    def _calculate_status_from_metrics(self, server: Server) -> ServerStatus:
        """Calcula status baseado nas métricas"""
        # Critérios de saúde
        cpu_healthy = server.cpu_usage < 80.0
        memory_healthy = server.memory_usage < 85.0
        response_healthy = server.response_time < 1000.0  # ms
        connection_healthy = server.current_connections < server.max_connections * 0.9
        
        # Taxa de sucesso
        success_rate = (server.successful_requests / max(server.total_requests, 1)) * 100
        success_healthy = success_rate > 95.0
        
        if all([cpu_healthy, memory_healthy, response_healthy, connection_healthy, success_healthy]):
            return ServerStatus.HEALTHY
        elif any([not cpu_healthy, not memory_healthy, not response_healthy]):
            return ServerStatus.UNHEALTHY
        else:
            return ServerStatus.DEGRADED

class LoadPredictor:
    """Preditor de carga usando ML"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.load_history = {}
        self.prediction_model = None
        self.last_training = None
        
    def predict_load(self, server: Server, time_horizon: int = 300) -> float:
        """Prediz carga futura para um servidor"""
        if not self.config.enable_ml_optimization:
            return server.current_connections
        
        # Coleta dados históricos
        server_history = self.load_history.get(server.id, [])
        
        if len(server_history) < 10:  # Dados insuficientes
            return server.current_connections
        
        # Features para predição
        features = self._extract_features(server, server_history)
        
        # Predição simples baseada em tendência
        if len(server_history) >= 5:
            recent_loads = [h['load'] for h in server_history[-5:]]
            trend = np.polyfit(range(len(recent_loads)), recent_loads, 1)[0]
            
            # Predição baseada na tendência
            predicted_load = server.current_connections + (trend * time_horizon / 60)
            
            # Aplica limites
            predicted_load = max(0, min(predicted_load, server.max_connections))
            
            return predicted_load
        
        return server.current_connections
    
    def _extract_features(self, server: Server, history: List[Dict]) -> Dict[str, float]:
        """Extrai features para predição"""
        if not history:
            return {}
        
        recent_data = history[-10:]  # Últimos 10 pontos
        
        features = {
            'current_load': server.current_connections,
            'avg_load': np.mean([h['load'] for h in recent_data]),
            'load_std': np.std([h['load'] for h in recent_data]),
            'load_trend': self._calculate_trend([h['load'] for h in recent_data]),
            'cpu_usage': server.cpu_usage,
            'memory_usage': server.memory_usage,
            'response_time': server.response_time,
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'success_rate': (server.successful_requests / max(server.total_requests, 1)) * 100
        }
        
        return features
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcula tendência dos valores"""
        if len(values) < 2:
            return 0.0
        
        value = np.arange(len(values))
        slope = np.polyfit(value, values, 1)[0]
        return slope
    
    def update_load_history(self, server: Server):
        """Atualiza histórico de carga"""
        if server.id not in self.load_history:
            self.load_history[server.id] = []
        
        load_data = {
            'timestamp': datetime.now(),
            'load': server.current_connections,
            'cpu': server.cpu_usage,
            'memory': server.memory_usage,
            'response_time': server.response_time
        }
        
        self.load_history[server.id].append(load_data)
        
        # Mantém apenas últimos 100 pontos
        if len(self.load_history[server.id]) > 100:
            self.load_history[server.id] = self.load_history[server.id][-100:]

class LoadBalancingStrategy:
    """Implementações das estratégias de load balancing"""
    
    @staticmethod
    def round_robin(servers: List[Server], current_index: int) -> Tuple[Server, int]:
        """Estratégia Round Robin"""
        if not servers:
            return None, current_index
        
        server = servers[current_index % len(servers)]
        return server, (current_index + 1) % len(servers)
    
    @staticmethod
    def least_connections(servers: List[Server]) -> Server:
        """Estratégia Least Connections"""
        if not servers:
            return None
        
        return min(servers, key=lambda string_data: string_data.current_connections)
    
    @staticmethod
    def weighted_round_robin(servers: List[Server], current_index: int) -> Tuple[Server, int]:
        """Estratégia Weighted Round Robin"""
        if not servers:
            return None, current_index
        
        # Calcula peso total
        total_weight = sum(server.weight for server in servers)
        
        # Seleciona servidor baseado no peso
        current_weight = 0
        for server in servers:
            current_weight += server.weight
            if current_index < current_weight:
                return server, (current_index + 1) % total_weight
        
        return servers[0], 1
    
    @staticmethod
    def ip_hash(servers: List[Server], client_ip: str) -> Server:
        """Estratégia IP Hash"""
        if not servers:
            return None
        
        hash_value = hash(client_ip) % len(servers)
        return servers[hash_value]
    
    @staticmethod
    def least_response_time(servers: List[Server]) -> Server:
        """Estratégia Least Response Time"""
        if not servers:
            return None
        
        return min(servers, key=lambda string_data: string_data.response_time)
    
    @staticmethod
    def ml_optimized(servers: List[Server], load_predictor: LoadPredictor) -> Server:
        """Estratégia otimizada por ML"""
        if not servers:
            return None
        
        # Filtra servidores saudáveis
        healthy_servers = [string_data for string_data in servers if string_data.status == ServerStatus.HEALTHY]
        
        if not healthy_servers:
            # Se não há servidores saudáveis, usa todos
            healthy_servers = servers
        
        # Calcula score para cada servidor
        server_scores = []
        for server in healthy_servers:
            # Prediz carga futura
            predicted_load = load_predictor.predict_load(server)
            
            # Calcula score baseado em múltiplos fatores
            load_score = 1.0 - (predicted_load / server.max_connections)
            cpu_score = 1.0 - (server.cpu_usage / 100.0)
            memory_score = 1.0 - (server.memory_usage / 100.0)
            response_score = 1.0 - min(server.response_time / 1000.0, 1.0)
            
            # Score composto
            total_score = (
                load_score * 0.4 +
                cpu_score * 0.2 +
                memory_score * 0.2 +
                response_score * 0.2
            )
            
            server_scores.append((server, total_score))
        
        # Retorna servidor com maior score
        return max(server_scores, key=lambda value: value[1])[0]

class IntelligentLoadBalancer:
    """Load balancer inteligente principal"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.servers = []
        self.health_checker = HealthChecker(config)
        self.load_predictor = LoadPredictor(config)
        self.current_index = 0
        self.session_map = {}
        self.request_history = []
        
        # Threading para health checks
        self.health_check_thread = None
        self.running = False
        
    def add_server(self, server: Server):
        """Adiciona servidor ao pool"""
        self.servers.append(server)
        logger.info(f"Servidor adicionado: {server.id} ({server.host}:{server.port})")
    
    def remove_server(self, server_id: str):
        """Remove servidor do pool"""
        self.servers = [string_data for string_data in self.servers if string_data.id != server_id]
        logger.info(f"Servidor removido: {server_id}")
    
    def get_server(self, request: Request) -> LoadBalancingDecision:
        """Seleciona servidor para requisição"""
        if not self.servers:
            raise ValueError("Nenhum servidor disponível")
        
        # Verifica session stickiness
        if self.config.session_sticky:
            session_key = f"{request.client_ip}_{request.path}"
            if session_key in self.session_map:
                server_id = self.session_map[session_key]
                server = next((string_data for string_data in self.servers if string_data.id == server_id), None)
                if server and server.status == ServerStatus.HEALTHY:
                    return LoadBalancingDecision(
                        request_id=request.id,
                        selected_server=server.id,
                        strategy_used="session_sticky",
                        confidence_score=1.0,
                        reasoning=f"Session stickiness para {session_key}",
                        timestamp=datetime.now()
                    )
        
        # Seleciona servidor baseado na estratégia
        selected_server = None
        strategy_used = self.config.strategy.value
        confidence_score = 0.8
        reasoning = ""
        
        if self.config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            selected_server, self.current_index = LoadBalancingStrategy.round_robin(
                self.servers, self.current_index
            )
            reasoning = f"Round Robin - índice {self.current_index}"
            
        elif self.config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            selected_server = LoadBalancingStrategy.least_connections(self.servers)
            reasoning = f"Least Connections - {selected_server.current_connections} conexões"
            
        elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            selected_server, self.current_index = LoadBalancingStrategy.weighted_round_robin(
                self.servers, self.current_index
            )
            reasoning = f"Weighted Round Robin - peso {selected_server.weight}"
            
        elif self.config.strategy == LoadBalancingStrategy.IP_HASH:
            selected_server = LoadBalancingStrategy.ip_hash(self.servers, request.client_ip)
            reasoning = f"IP Hash - {request.client_ip}"
            
        elif self.config.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            selected_server = LoadBalancingStrategy.least_response_time(self.servers)
            reasoning = f"Least Response Time - {selected_server.response_time}ms"
            
        elif self.config.strategy == LoadBalancingStrategy.ML_OPTIMIZED:
            selected_server = LoadBalancingStrategy.ml_optimized(self.servers, self.load_predictor)
            predicted_load = self.load_predictor.predict_load(selected_server)
            reasoning = f"ML Optimized - carga predita: {predicted_load:.1f}"
            confidence_score = 0.9
        
        if not selected_server:
            # Fallback para primeiro servidor disponível
            selected_server = next((string_data for string_data in self.servers if string_data.status != ServerStatus.OFFLINE), self.servers[0])
            strategy_used = "fallback"
            reasoning = "Fallback - primeiro servidor disponível"
            confidence_score = 0.5
        
        # Atualiza session map se necessário
        if self.config.session_sticky:
            session_key = f"{request.client_ip}_{request.path}"
            self.session_map[session_key] = selected_server.id
        
        # Prediz carga futura
        predicted_load = self.load_predictor.predict_load(selected_server)
        
        decision = LoadBalancingDecision(
            request_id=request.id,
            selected_server=selected_server.id,
            strategy_used=strategy_used,
            confidence_score=confidence_score,
            reasoning=reasoning,
            timestamp=datetime.now(),
            predicted_load=predicted_load
        )
        
        # Registra decisão
        self.request_history.append(decision)
        
        return decision
    
    def update_server_metrics(self, server_id: str, metrics: Dict[str, Any]):
        """Atualiza métricas de um servidor"""
        server = next((string_data for string_data in self.servers if string_data.id == server_id), None)
        if server:
            self.health_checker.update_server_metrics(server, metrics)
            self.load_predictor.update_load_history(server)
    
    def start_health_checks(self):
        """Inicia verificações de saúde em background"""
        self.running = True
        self.health_check_thread = threading.Thread(target=self._health_check_loop)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
        logger.info("Health checks iniciados")
    
    def stop_health_checks(self):
        """Para verificações de saúde"""
        self.running = False
        if self.health_check_thread:
            self.health_check_thread.join()
        logger.info("Health checks parados")
    
    def _health_check_loop(self):
        """Loop de verificações de saúde"""
        while self.running:
            for server in self.servers:
                try:
                    status = self.health_checker.check_server_health(server)
                    if status != server.status:
                        logger.info(f"Status do servidor {server.id} mudou: {server.status} -> {status}")
                        server.status = status
                except Exception as e:
                    logger.error(f"Erro no health check do servidor {server.id}: {e}")
            
            time.sleep(self.config.health_check_interval)
    
    def get_status_report(self) -> Dict[str, Any]:
        """Gera relatório de status"""
        total_requests = len(self.request_history)
        successful_decisions = len([data for data in self.request_history if data.confidence_score > 0.7])
        
        server_stats = {}
        for server in self.servers:
            server_stats[server.id] = {
                'status': server.status.value,
                'current_connections': server.current_connections,
                'max_connections': server.max_connections,
                'cpu_usage': server.cpu_usage,
                'memory_usage': server.memory_usage,
                'response_time': server.response_time,
                'success_rate': (server.successful_requests / max(server.total_requests, 1)) * 100
            }
        
        return {
            'total_servers': len(self.servers),
            'healthy_servers': len([string_data for string_data in self.servers if string_data.status == ServerStatus.HEALTHY]),
            'total_requests': total_requests,
            'successful_decisions': successful_decisions,
            'decision_accuracy': (successful_decisions / max(total_requests, 1)) * 100,
            'strategy': self.config.strategy.value,
            'session_sticky_enabled': self.config.session_sticky,
            'ml_optimization_enabled': self.config.enable_ml_optimization,
            'server_stats': server_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance"""
        if not self.request_history:
            return {}
        
        recent_decisions = self.request_history[-100:]  # Últimas 100 decisões
        
        strategy_usage = {}
        confidence_scores = []
        response_times = []
        
        for decision in recent_decisions:
            strategy_usage[decision.strategy_used] = strategy_usage.get(decision.strategy_used, 0) + 1
            confidence_scores.append(decision.confidence_score)
        
        return {
            'strategy_distribution': strategy_usage,
            'avg_confidence_score': np.mean(confidence_scores),
            'total_decisions': len(self.request_history),
            'recent_decisions': len(recent_decisions),
            'ml_predictions_accuracy': self._calculate_ml_accuracy()
        }
    
    def _calculate_ml_accuracy(self) -> float:
        """Calcula acurácia das predições ML"""
        if not self.config.enable_ml_optimization:
            return 0.0
        
        # Implementação simplificada
        # Em produção, compararia predições com valores reais
        return 0.85  # Placeholder

# Função de conveniência para uso rápido
def create_intelligent_load_balancer(servers: List[Dict], 
                                   strategy: LoadBalancingStrategy = LoadBalancingStrategy.ML_OPTIMIZED,
                                   enable_ml: bool = True) -> IntelligentLoadBalancer:
    """
    Função de conveniência para criar load balancer inteligente
    
    Args:
        servers: Lista de configurações de servidores
        strategy: Estratégia de load balancing
        enable_ml: Habilita otimização ML
    
    Returns:
        Load balancer configurado
    """
    config = LoadBalancerConfig(
        strategy=strategy,
        enable_ml_optimization=enable_ml,
        health_check_interval=30,
        session_sticky=True
    )
    
    load_balancer = IntelligentLoadBalancer(config)
    
    # Adiciona servidores
    for server_config in servers:
        server = Server(
            id=server_config['id'],
            host=server_config['host'],
            port=server_config['port'],
            weight=server_config.get('weight', 1.0),
            max_connections=server_config.get('max_connections', 1000)
        )
        load_balancer.add_server(server)
    
    # Inicia health checks
    load_balancer.start_health_checks()
    
    return load_balancer

if __name__ == "__main__":
    # Exemplo de uso
    servers_config = [
        {'id': 'server1', 'host': '192.168.1.10', 'port': 8080, 'weight': 1.0},
        {'id': 'server2', 'host': '192.168.1.11', 'port': 8080, 'weight': 1.5},
        {'id': 'server3', 'host': '192.168.1.12', 'port': 8080, 'weight': 1.0}
    ]
    
    try:
        # Cria load balancer
        lb = create_intelligent_load_balancer(
            servers=servers_config,
            strategy=LoadBalancingStrategy.ML_OPTIMIZED,
            enable_ml=True
        )
        
        # Simula requisições
        for index in range(10):
            request = Request(
                id=f"req_{index}",
                client_ip=f"192.168.1.{index % 255}",
                timestamp=datetime.now(),
                method="GET",
                path="/api/keywords",
                headers={},
                priority=1
            )
            
            decision = lb.get_server(request)
            print(f"Requisição {index}: {decision.selected_server} ({decision.strategy_used})")
        
        # Relatório de status
        status = lb.get_status_report()
        print(f"\nStatus do Load Balancer:")
        print(f"Servidores saudáveis: {status['healthy_servers']}/{status['total_servers']}")
        print(f"Total de requisições: {status['total_requests']}")
        print(f"Acurácia das decisões: {status['decision_accuracy']:.1f}%")
        
        # Para health checks
        lb.stop_health_checks()
        
    except Exception as e:
        print(f"Erro no load balancer: {e}") 