"""
Sistema de Load Balancing
Distribui carga entre múltiplos servidores para melhorar performance e disponibilidade
"""

import asyncio
import time
import random
import hashlib
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json
import aiohttp
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class LoadBalancingAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    CONSISTENT_HASH = "consistent_hash"


class ServerStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"


@dataclass
class ServerInfo:
    id: str
    url: str
    weight: int = 1
    max_connections: int = 100
    current_connections: int = 0
    response_time: float = 0.0
    error_rate: float = 0.0
    status: ServerStatus = ServerStatus.HEALTHY
    last_health_check: datetime = None
    created_at: datetime = None
    metadata: Dict[str, Any] = None


@dataclass
class LoadBalancerMetrics:
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    active_connections: int
    server_count: int
    healthy_servers: int
    unhealthy_servers: int


class LoadBalancer:
    """
    Load balancer com múltiplos algoritmos de distribuição
    """
    
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
                 config: Optional[Dict] = None):
        self.algorithm = algorithm
        self.config = config or {}
        self.servers: Dict[str, ServerInfo] = {}
        self.current_index = 0
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.health_check_timeout = self.config.get('health_check_timeout', 5)
        self.max_retries = self.config.get('max_retries', 3)
        self.session_timeout = self.config.get('session_timeout', 300)
        
        # Métricas
        self.metrics = LoadBalancerMetrics(
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_response_time=0.0,
            active_connections=0,
            server_count=0,
            healthy_servers=0,
            unhealthy_servers=0
        )
        
        # Health check task
        self.health_check_task = None
        self.is_running = False
    
    async def start(self):
        """Inicia o load balancer"""
        if self.is_running:
            return
        
        self.is_running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Load balancer started")
    
    async def stop(self):
        """Para o load balancer"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Load balancer stopped")
    
    def add_server(self, server_id: str, url: str, weight: int = 1, 
                   max_connections: int = 100, metadata: Dict[str, Any] = None) -> bool:
        """Adiciona servidor ao load balancer"""
        try:
            # Validar URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"Invalid URL: {url}")
            
            server_info = ServerInfo(
                id=server_id,
                url=url,
                weight=weight,
                max_connections=max_connections,
                created_at=datetime.now(),
                metadata=metadata or {}
            )
            
            self.servers[server_id] = server_info
            self._update_metrics()
            
            logger.info(f"Server added: {server_id} ({url})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding server {server_id}: {e}")
            return False
    
    def remove_server(self, server_id: str) -> bool:
        """Remove servidor do load balancer"""
        if server_id in self.servers:
            del self.servers[server_id]
            self._update_metrics()
            logger.info(f"Server removed: {server_id}")
            return True
        return False
    
    def get_server(self, client_ip: str = None) -> Optional[ServerInfo]:
        """Seleciona servidor baseado no algoritmo"""
        healthy_servers = [
            server for server in self.servers.values()
            if server.status == ServerStatus.HEALTHY
        ]
        
        if not healthy_servers:
            logger.warning("No healthy servers available")
            return None
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash_select(healthy_servers, client_ip)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return self._least_response_time_select(healthy_servers)
        elif self.algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            return self._consistent_hash_select(healthy_servers, client_ip)
        else:
            return self._round_robin_select(healthy_servers)
    
    def _round_robin_select(self, servers: List[ServerInfo]) -> ServerInfo:
        """Seleção round robin"""
        if not servers:
            return None
        
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        return server
    
    def _least_connections_select(self, servers: List[ServerInfo]) -> ServerInfo:
        """Seleção por menor número de conexões"""
        if not servers:
            return None
        
        return min(servers, key=lambda s: s.current_connections)
    
    def _weighted_round_robin_select(self, servers: List[ServerInfo]) -> ServerInfo:
        """Seleção round robin ponderada"""
        if not servers:
            return None
        
        # Criar lista ponderada
        weighted_servers = []
        for server in servers:
            weighted_servers.extend([server] * server.weight)
        
        if not weighted_servers:
            return None
        
        server = weighted_servers[self.current_index % len(weighted_servers)]
        self.current_index += 1
        return server
    
    def _ip_hash_select(self, servers: List[ServerInfo], client_ip: str) -> ServerInfo:
        """Seleção por hash do IP"""
        if not servers or not client_ip:
            return self._round_robin_select(servers)
        
        # Hash do IP
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(servers)
        return servers[index]
    
    def _least_response_time_select(self, servers: List[ServerInfo]) -> ServerInfo:
        """Seleção por menor tempo de resposta"""
        if not servers:
            return None
        
        return min(servers, key=lambda s: s.response_time)
    
    def _consistent_hash_select(self, servers: List[ServerInfo], client_ip: str) -> ServerInfo:
        """Seleção por hash consistente"""
        if not servers or not client_ip:
            return self._round_robin_select(servers)
        
        # Hash consistente
        hash_value = int(hashlib.sha256(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(servers)
        return servers[index]
    
    async def forward_request(self, method: str, path: str, headers: Dict = None,
                            data: Any = None, client_ip: str = None) -> Dict[str, Any]:
        """Encaminha requisição para servidor selecionado"""
        start_time = time.time()
        
        # Selecionar servidor
        server = self.get_server(client_ip)
        if not server:
            return {
                'success': False,
                'error': 'No healthy servers available',
                'status_code': 503
            }
        
        # Incrementar conexões
        server.current_connections += 1
        self.metrics.active_connections += 1
        self.metrics.total_requests += 1
        
        try:
            # Fazer requisição
            async with aiohttp.ClientSession() as session:
                url = f"{server.url.rstrip('/')}/{path.lstrip('/')}"
                
                async with session.request(
                    method, url, headers=headers, data=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.read()
                    
                    # Atualizar métricas do servidor
                    response_time = time.time() - start_time
                    server.response_time = (
                        (server.response_time + response_time) / 2
                    )
                    
                    self.metrics.successful_requests += 1
                    self._update_avg_response_time(response_time)
                    
                    return {
                        'success': True,
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'data': response_data,
                        'server_id': server.id,
                        'response_time': response_time
                    }
        
        except Exception as e:
            # Atualizar métricas de erro
            server.error_rate = min(1.0, server.error_rate + 0.1)
            self.metrics.failed_requests += 1
            
            logger.error(f"Request failed to server {server.id}: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'status_code': 500,
                'server_id': server.id
            }
        
        finally:
            # Decrementar conexões
            server.current_connections = max(0, server.current_connections - 1)
            self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
    
    async def _health_check_loop(self):
        """Loop de verificação de saúde dos servidores"""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self):
        """Executa verificações de saúde"""
        tasks = []
        for server in self.servers.values():
            task = asyncio.create_task(self._check_server_health(server))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_server_health(self, server: ServerInfo):
        """Verifica saúde de um servidor"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{server.url}/health",
                    timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)
                ) as response:
                    if response.status == 200:
                        server.status = ServerStatus.HEALTHY
                        server.error_rate = max(0, server.error_rate - 0.05)
                    else:
                        server.status = ServerStatus.UNHEALTHY
                        server.error_rate = min(1.0, server.error_rate + 0.1)
            
            server.last_health_check = datetime.now()
            
        except Exception as e:
            server.status = ServerStatus.UNHEALTHY
            server.error_rate = min(1.0, server.error_rate + 0.2)
            server.last_health_check = datetime.now()
            
            logger.warning(f"Health check failed for server {server.id}: {e}")
    
    def _update_metrics(self):
        """Atualiza métricas do load balancer"""
        self.metrics.server_count = len(self.servers)
        self.metrics.healthy_servers = len([
            s for s in self.servers.values()
            if s.status == ServerStatus.HEALTHY
        ])
        self.metrics.unhealthy_servers = self.metrics.server_count - self.metrics.healthy_servers
    
    def _update_avg_response_time(self, response_time: float):
        """Atualiza tempo médio de resposta"""
        total_requests = self.metrics.successful_requests + self.metrics.failed_requests
        if total_requests > 0:
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * (total_requests - 1) + response_time) 
                / total_requests
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do load balancer"""
        return asdict(self.metrics)
    
    def get_server_list(self) -> List[Dict[str, Any]]:
        """Obtém lista de servidores"""
        return [
            {
                'id': server.id,
                'url': server.url,
                'weight': server.weight,
                'max_connections': server.max_connections,
                'current_connections': server.current_connections,
                'response_time': server.response_time,
                'error_rate': server.error_rate,
                'status': server.status.value,
                'last_health_check': server.last_health_check.isoformat() if server.last_health_check else None,
                'created_at': server.created_at.isoformat() if server.created_at else None
            }
            for server in self.servers.values()
        ]


class SessionAffinityLoadBalancer(LoadBalancer):
    """
    Load balancer com afinidade de sessão
    """
    
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.IP_HASH,
                 session_timeout: int = 300, **kwargs):
        super().__init__(algorithm, **kwargs)
        self.session_timeout = session_timeout
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_server(self, client_ip: str = None, session_id: str = None) -> Optional[ServerInfo]:
        """Seleciona servidor com afinidade de sessão"""
        # Verificar sessão existente
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            server_id = session.get('server_id')
            
            if server_id in self.servers:
                server = self.servers[server_id]
                if server.status == ServerStatus.HEALTHY:
                    return server
        
        # Selecionar novo servidor
        server = super().get_server(client_ip)
        
        # Criar sessão
        if server and session_id:
            self.sessions[session_id] = {
                'server_id': server.id,
                'created_at': datetime.now(),
                'last_accessed': datetime.now()
            }
        
        return server
    
    def update_session(self, session_id: str):
        """Atualiza timestamp da sessão"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_accessed'] = datetime.now()
    
    async def cleanup_expired_sessions(self):
        """Remove sessões expiradas"""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if (current_time - session['last_accessed']).total_seconds() > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


class AdaptiveLoadBalancer(LoadBalancer):
    """
    Load balancer adaptativo que ajusta algoritmo baseado em métricas
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.performance_history: List[Dict[str, Any]] = []
        self.algorithm_performance: Dict[LoadBalancingAlgorithm, float] = {}
    
    def get_server(self, client_ip: str = None) -> Optional[ServerInfo]:
        """Seleciona servidor com algoritmo adaptativo"""
        # Analisar performance e ajustar algoritmo
        self._analyze_performance()
        
        return super().get_server(client_ip)
    
    def _analyze_performance(self):
        """Analisa performance e ajusta algoritmo"""
        if len(self.performance_history) < 100:
            return
        
        # Calcular performance por algoritmo
        for algorithm in LoadBalancingAlgorithm:
            algorithm_metrics = [
                m for m in self.performance_history[-100:]
                if m.get('algorithm') == algorithm
            ]
            
            if algorithm_metrics:
                avg_response_time = sum(m['response_time'] for m in algorithm_metrics) / len(algorithm_metrics)
                success_rate = sum(1 for m in algorithm_metrics if m['success']) / len(algorithm_metrics)
                
                performance_score = success_rate / (avg_response_time + 0.1)
                self.algorithm_performance[algorithm] = performance_score
        
        # Selecionar melhor algoritmo
        if self.algorithm_performance:
            best_algorithm = max(self.algorithm_performance.items(), key=lambda x: x[1])[0]
            if best_algorithm != self.algorithm:
                logger.info(f"Switching algorithm from {self.algorithm} to {best_algorithm}")
                self.algorithm = best_algorithm
    
    def record_performance(self, algorithm: LoadBalancingAlgorithm, response_time: float, success: bool):
        """Registra performance para análise"""
        self.performance_history.append({
            'algorithm': algorithm,
            'response_time': response_time,
            'success': success,
            'timestamp': datetime.now()
        })
        
        # Manter apenas últimos 1000 registros
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]


# Funções utilitárias
def create_load_balancer(algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN,
                        config: Optional[Dict] = None) -> LoadBalancer:
    """Cria load balancer"""
    return LoadBalancer(algorithm, config)


def create_session_affinity_load_balancer(session_timeout: int = 300,
                                        config: Optional[Dict] = None) -> SessionAffinityLoadBalancer:
    """Cria load balancer com afinidade de sessão"""
    return SessionAffinityLoadBalancer(session_timeout=session_timeout, **(config or {}))


def create_adaptive_load_balancer(config: Optional[Dict] = None) -> AdaptiveLoadBalancer:
    """Cria load balancer adaptativo"""
    return AdaptiveLoadBalancer(**(config or {}))


# Instância global
load_balancer = LoadBalancer()


# Decorator para usar load balancer
def with_load_balancer(func):
    """Decorator para usar load balancer"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extrair informações da requisição
        request = kwargs.get('request')
        if request:
            client_ip = request.client.host if hasattr(request, 'client') else None
            method = request.method
            path = request.url.path
            headers = dict(request.headers)
            data = await request.body() if hasattr(request, 'body') else None
        else:
            client_ip = kwargs.get('client_ip')
            method = kwargs.get('method', 'GET')
            path = kwargs.get('path', '/')
            headers = kwargs.get('headers', {})
            data = kwargs.get('data')
        
        # Encaminhar via load balancer
        result = await load_balancer.forward_request(
            method, path, headers, data, client_ip
        )
        
        return result
    
    return wrapper 