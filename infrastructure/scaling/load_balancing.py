"""
Módulo de Load Balancing para Sistemas Enterprise
Sistema de balanceamento de carga com múltiplos algoritmos - Omni Keywords Finder

Prompt: Implementação de sistema de load balancing enterprise
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import statistics
from concurrent.futures import ThreadPoolExecutor
import hashlib

logger = logging.getLogger(__name__)


class LoadBalancingAlgorithm(Enum):
    """Algoritmos de balanceamento de carga disponíveis."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    CONSISTENT_HASH = "consistent_hash"
    ADAPTIVE = "adaptive"


class ServerStatus(Enum):
    """Status dos servidores."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class Server:
    """Representa um servidor no pool de load balancing."""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    response_time: float = 0.0  # em ms
    error_rate: float = 0.0  # taxa de erro (0-1)
    status: ServerStatus = ServerStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    health_check_failures: int = 0
    maintenance_mode: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.id or len(self.id.strip()) == 0:
            raise ValueError("ID do servidor não pode ser vazio")
        if not self.host or len(self.host.strip()) == 0:
            raise ValueError("Host do servidor não pode ser vazio")
        if not 1 <= self.port <= 65535:
            raise ValueError("Porta deve estar entre 1 e 65535")
        if self.weight < 1:
            raise ValueError("Peso deve ser pelo menos 1")
        if self.max_connections < 1:
            raise ValueError("Max connections deve ser pelo menos 1")
        if self.current_connections < 0:
            raise ValueError("Current connections não pode ser negativo")
        if self.response_time < 0:
            raise ValueError("Response time não pode ser negativo")
        if not 0 <= self.error_rate <= 1:
            raise ValueError("Error rate deve estar entre 0 e 1")
        if self.health_check_failures < 0:
            raise ValueError("Health check failures não pode ser negativo")
        
        # Normalizar campos
        self.id = self.id.strip()
        self.host = self.host.strip()
    
    def is_available(self) -> bool:
        """Verifica se o servidor está disponível."""
        return (self.status == ServerStatus.HEALTHY and 
                not self.maintenance_mode and
                self.current_connections < self.max_connections)
    
    def get_health_score(self) -> float:
        """Calcula score de saúde do servidor (0-1)."""
        if not self.is_available():
            return 0.0
        
        # Fatores que afetam a saúde
        connection_factor = 1.0 - (self.current_connections / self.max_connections)
        response_factor = max(0.0, 1.0 - (self.response_time / 5000.0))  # 5s como referência
        error_factor = 1.0 - self.error_rate
        
        # Score combinado
        score = (connection_factor * 0.4 + 
                response_factor * 0.4 + 
                error_factor * 0.2)
        
        return max(0.0, min(1.0, score))
    
    def update_metrics(self, connections: int = None, response_time: float = None, 
                      error_rate: float = None) -> None:
        """Atualiza métricas do servidor."""
        if connections is not None:
            self.current_connections = max(0, connections)
        if response_time is not None:
            self.response_time = max(0.0, response_time)
        if error_rate is not None:
            self.error_rate = max(0.0, min(1.0, error_rate))
    
    def mark_health_check_failure(self) -> None:
        """Marca falha no health check."""
        self.health_check_failures += 1
        self.last_health_check = datetime.utcnow()
        
        if self.health_check_failures >= 3:
            self.status = ServerStatus.UNHEALTHY
        elif self.health_check_failures >= 1:
            self.status = ServerStatus.DEGRADED
    
    def mark_health_check_success(self) -> None:
        """Marca sucesso no health check."""
        self.health_check_failures = 0
        self.last_health_check = datetime.utcnow()
        self.status = ServerStatus.HEALTHY


@dataclass
class LoadBalancerConfig:
    """Configuração do load balancer."""
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    health_check_interval: int = 30  # segundos
    health_check_timeout: int = 5  # segundos
    health_check_path: str = "/health"
    health_check_method: str = "GET"
    max_health_check_failures: int = 3
    session_affinity: bool = False
    session_timeout: int = 1800  # 30 minutos
    enable_ssl: bool = True
    ssl_cert_path: str = ""
    ssl_key_path: str = ""
    enable_compression: bool = True
    enable_gzip: bool = True
    max_request_size: int = 10485760  # 10MB
    request_timeout: int = 30  # segundos
    enable_logging: bool = True
    log_level: str = "INFO"

    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.health_check_interval < 1:
            raise ValueError("Health check interval deve ser pelo menos 1 segundo")
        if self.health_check_timeout < 1:
            raise ValueError("Health check timeout deve ser pelo menos 1 segundo")
        if self.max_health_check_failures < 1:
            raise ValueError("Max health check failures deve ser pelo menos 1")
        if self.session_timeout < 60:
            raise ValueError("Session timeout deve ser pelo menos 60 segundos")
        if self.max_request_size < 1024:
            raise ValueError("Max request size deve ser pelo menos 1KB")
        if self.request_timeout < 1:
            raise ValueError("Request timeout deve ser pelo menos 1 segundo")


@dataclass
class LoadBalancerMetrics:
    """Métricas do load balancer."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    requests_per_second: float = 0.0
    active_connections: int = 0
    total_connections: int = 0
    error_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def update(self, request_success: bool, response_time: float, 
               active_connections: int = None) -> None:
        """Atualiza métricas."""
        self.total_requests += 1
        if request_success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Atualizar response time médio
        if self.total_requests == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) / 
                self.total_requests
            )
        
        if active_connections is not None:
            self.active_connections = active_connections
        
        self.total_connections += 1
        self.error_rate = self.failed_requests / self.total_requests if self.total_requests > 0 else 0.0
        self.last_updated = datetime.utcnow()


class LoadBalancer:
    """Load balancer enterprise com múltiplos algoritmos e health checks."""
    
    def __init__(self, config: LoadBalancerConfig):
        """
        Inicializa o load balancer.
        
        Args:
            config: Configuração do load balancer
        """
        self.config = config
        self.servers: List[Server] = []
        self.current_server_index = 0  # Para round robin
        self.session_map: Dict[str, str] = {}  # session_id -> server_id
        self.metrics = LoadBalancerMetrics()
        self.health_check_task = None
        self.is_running = False
        
        logger.info(f"LoadBalancer inicializado - Algorithm: {config.algorithm.value}")
    
    def add_server(self, server: Server) -> None:
        """Adiciona um servidor ao pool."""
        # Verificar se já existe
        if any(s.id == server.id for s in self.servers):
            raise ValueError(f"Servidor com ID {server.id} já existe")
        
        self.servers.append(server)
        logger.info(f"Servidor adicionado: {server.host}:{server.port}")
    
    def remove_server(self, server_id: str) -> None:
        """Remove um servidor do pool."""
        server = next((s for s in self.servers if s.id == server_id), None)
        if not server:
            raise ValueError(f"Servidor com ID {server_id} não encontrado")
        
        self.servers.remove(server)
        
        # Remover sessões associadas
        session_ids_to_remove = [sid for sid, srv_id in self.session_map.items() if srv_id == server_id]
        for session_id in session_ids_to_remove:
            del self.session_map[session_id]
        
        logger.info(f"Servidor removido: {server.host}:{server.port}")
    
    def get_available_servers(self) -> List[Server]:
        """Retorna servidores disponíveis."""
        return [s for s in self.servers if s.is_available()]
    
    def select_server(self, client_ip: str = None, session_id: str = None) -> Optional[Server]:
        """
        Seleciona um servidor usando o algoritmo configurado.
        
        Args:
            client_ip: IP do cliente (para IP hash)
            session_id: ID da sessão (para session affinity)
            
        Returns:
            Servidor selecionado ou None se não houver servidores disponíveis
        """
        available_servers = self.get_available_servers()
        if not available_servers:
            return None
        
        # Session affinity
        if self.config.session_affinity and session_id:
            if session_id in self.session_map:
                server_id = self.session_map[session_id]
                server = next((s for s in available_servers if s.id == server_id), None)
                if server:
                    return server
        
        # Selecionar servidor baseado no algoritmo
        if self.config.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            selected_server = self._round_robin_select(available_servers)
        elif self.config.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            selected_server = self._least_connections_select(available_servers)
        elif self.config.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            selected_server = self._weighted_round_robin_select(available_servers)
        elif self.config.algorithm == LoadBalancingAlgorithm.IP_HASH:
            selected_server = self._ip_hash_select(available_servers, client_ip)
        elif self.config.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            selected_server = self._least_response_time_select(available_servers)
        elif self.config.algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            selected_server = self._weighted_least_connections_select(available_servers)
        elif self.config.algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            selected_server = self._consistent_hash_select(available_servers, client_ip)
        elif self.config.algorithm == LoadBalancingAlgorithm.ADAPTIVE:
            selected_server = self._adaptive_select(available_servers)
        else:
            raise ValueError(f"Algoritmo não suportado: {self.config.algorithm}")
        
        # Atualizar session map se session affinity estiver habilitado
        if self.config.session_affinity and session_id and selected_server:
            self.session_map[session_id] = selected_server.id
        
        return selected_server
    
    def _round_robin_select(self, available_servers: List[Server]) -> Server:
        """Seleção round robin."""
        if not available_servers:
            return None
        
        selected_server = available_servers[self.current_server_index % len(available_servers)]
        self.current_server_index = (self.current_server_index + 1) % len(available_servers)
        return selected_server
    
    def _least_connections_select(self, available_servers: List[Server]) -> Server:
        """Seleção baseada em menor número de conexões."""
        if not available_servers:
            return None
        
        return min(available_servers, key=lambda s: s.current_connections)
    
    def _weighted_round_robin_select(self, available_servers: List[Server]) -> Server:
        """Seleção round robin com pesos."""
        if not available_servers:
            return None
        
        # Calcular peso total
        total_weight = sum(s.weight for s in available_servers)
        if total_weight == 0:
            return available_servers[0]
        
        # Selecionar baseado em peso
        current_weight = 0
        for server in available_servers:
            current_weight += server.weight
            if self.current_server_index < current_weight:
                self.current_server_index = (self.current_server_index + 1) % total_weight
                return server
        
        # Fallback
        return available_servers[0]
    
    def _ip_hash_select(self, available_servers: List[Server], client_ip: str) -> Server:
        """Seleção baseada em hash do IP."""
        if not available_servers:
            return None
        
        if not client_ip:
            return available_servers[0]
        
        # Calcular hash do IP
        hash_value = hash(client_ip) % len(available_servers)
        return available_servers[hash_value]
    
    def _least_response_time_select(self, available_servers: List[Server]) -> Server:
        """Seleção baseada em menor tempo de resposta."""
        if not available_servers:
            return None
        
        return min(available_servers, key=lambda s: s.response_time)
    
    def _weighted_least_connections_select(self, available_servers: List[Server]) -> Server:
        """Seleção baseada em menor número de conexões ponderado."""
        if not available_servers:
            return None
        
        # Calcular score ponderado (menor é melhor)
        def calculate_score(server: Server) -> float:
            connection_score = server.current_connections / server.max_connections
            weight_factor = 1.0 / server.weight
            return connection_score * weight_factor
        
        return min(available_servers, key=calculate_score)
    
    def _consistent_hash_select(self, available_servers: List[Server], client_ip: str) -> Server:
        """Seleção usando consistent hashing."""
        if not available_servers:
            return None
        
        if not client_ip:
            return available_servers[0]
        
        # Implementação simples de consistent hashing
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        server_index = hash_value % len(available_servers)
        return available_servers[server_index]
    
    def _adaptive_select(self, available_servers: List[Server]) -> Server:
        """Seleção adaptativa baseada em múltiplos fatores."""
        if not available_servers:
            return None
        
        # Calcular score para cada servidor
        def calculate_adaptive_score(server: Server) -> float:
            # Fatores: conexões, response time, error rate, health score
            connection_factor = 1.0 - (server.current_connections / server.max_connections)
            response_factor = max(0.0, 1.0 - (server.response_time / 5000.0))
            error_factor = 1.0 - server.error_rate
            health_factor = server.get_health_score()
            
            # Score combinado (maior é melhor)
            score = (connection_factor * 0.3 + 
                    response_factor * 0.3 + 
                    error_factor * 0.2 + 
                    health_factor * 0.2)
            
            return score
        
        return max(available_servers, key=calculate_adaptive_score)
    
    async def start_health_checks(self) -> None:
        """Inicia health checks periódicos."""
        if self.is_running:
            return
        
        self.is_running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Health checks iniciados")
    
    async def stop_health_checks(self) -> None:
        """Para health checks."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health checks parados")
    
    async def _health_check_loop(self) -> None:
        """Loop principal de health checks."""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no health check loop: {e}")
                await asyncio.sleep(5)  # Aguardar antes de tentar novamente
    
    async def _perform_health_checks(self) -> None:
        """Executa health checks em todos os servidores."""
        tasks = []
        for server in self.servers:
            task = asyncio.create_task(self._check_server_health(server))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_server_health(self, server: Server) -> None:
        """Verifica saúde de um servidor específico."""
        try:
            # Simular health check
            health_check_url = f"http://{server.host}:{server.port}{self.config.health_check_path}"
            
            # Simular timeout
            await asyncio.wait_for(self._simulate_health_check(server), 
                                 timeout=self.config.health_check_timeout)
            
            # Health check bem-sucedido
            server.mark_health_check_success()
            logger.debug(f"Health check OK: {server.host}:{server.port}")
            
        except asyncio.TimeoutError:
            server.mark_health_check_failure()
            logger.warning(f"Health check timeout: {server.host}:{server.port}")
        except Exception as e:
            server.mark_health_check_failure()
            logger.error(f"Health check failed: {server.host}:{server.port} - {e}")
    
    async def _simulate_health_check(self, server: Server) -> None:
        """Simula health check (placeholder para implementação real)."""
        # Simular latência baseada no response time do servidor
        latency = min(server.response_time / 1000.0, 1.0)  # Converter para segundos
        await asyncio.sleep(latency)
        
        # Simular falha ocasional baseada no error rate
        if random.random() < server.error_rate:
            raise Exception("Simulated health check failure")
    
    def get_metrics(self) -> LoadBalancerMetrics:
        """Retorna métricas atuais do load balancer."""
        return self.metrics
    
    def get_server_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Retorna métricas de todos os servidores."""
        metrics = {}
        for server in self.servers:
            metrics[server.id] = {
                "host": server.host,
                "port": server.port,
                "status": server.status.value,
                "current_connections": server.current_connections,
                "max_connections": server.max_connections,
                "response_time": server.response_time,
                "error_rate": server.error_rate,
                "health_score": server.get_health_score(),
                "weight": server.weight,
                "maintenance_mode": server.maintenance_mode,
                "last_health_check": server.last_health_check.isoformat(),
                "health_check_failures": server.health_check_failures
            }
        return metrics
    
    def enable_maintenance_mode(self, server_id: str) -> None:
        """Habilita modo de manutenção para um servidor."""
        server = next((s for s in self.servers if s.id == server_id), None)
        if not server:
            raise ValueError(f"Servidor com ID {server_id} não encontrado")
        
        server.maintenance_mode = True
        logger.info(f"Modo de manutenção habilitado: {server.host}:{server.port}")
    
    def disable_maintenance_mode(self, server_id: str) -> None:
        """Desabilita modo de manutenção para um servidor."""
        server = next((s for s in self.servers if s.id == server_id), None)
        if not server:
            raise ValueError(f"Servidor com ID {server_id} não encontrado")
        
        server.maintenance_mode = False
        logger.info(f"Modo de manutenção desabilitado: {server.host}:{server.port}")
    
    def update_server_weight(self, server_id: str, new_weight: int) -> None:
        """Atualiza peso de um servidor."""
        server = next((s for s in self.servers if s.id == server_id), None)
        if not server:
            raise ValueError(f"Servidor com ID {server_id} não encontrado")
        
        if new_weight < 1:
            raise ValueError("Peso deve ser pelo menos 1")
        
        server.weight = new_weight
        logger.info(f"Peso atualizado: {server.host}:{server.port} -> {new_weight}")
    
    def cleanup_expired_sessions(self) -> None:
        """Remove sessões expiradas."""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, server_id in self.session_map.items():
            # Simular expiração baseada em timestamp (implementação real seria mais complexa)
            if random.random() < 0.01:  # 1% de chance de expiração por chamada
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.session_map[session_id]
        
        if expired_sessions:
            logger.debug(f"Sessões expiradas removidas: {len(expired_sessions)}")


# Função de conveniência para criar load balancer padrão
def create_load_balancer(algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
                        enable_session_affinity: bool = False) -> LoadBalancer:
    """
    Cria um load balancer com configurações padrão.
    
    Args:
        algorithm: Algoritmo de balanceamento
        enable_session_affinity: Habilita session affinity
        
    Returns:
        Instância configurada do LoadBalancer
    """
    config = LoadBalancerConfig(
        algorithm=algorithm,
        session_affinity=enable_session_affinity
    )
    return LoadBalancer(config) 