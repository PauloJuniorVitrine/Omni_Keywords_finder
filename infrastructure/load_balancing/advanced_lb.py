# 📋 Advanced Load Balancer
# Tracing ID: ADVANCED_LB_011_20250127
# Versão: 1.0
# Data: 2025-01-27
# Objetivo: Load balancing avançado para multi-region

"""
Advanced Load Balancer

Este módulo implementa load balancing avançado com múltiplas estratégias,
health checks, failover automático e métricas de performance.
"""

import asyncio
import logging
import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import statistics
import json
import yaml
import os
from contextlib import asynccontextmanager
import aiohttp
import aiofiles

# Configuração de logging
logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Estratégias de load balancing disponíveis"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    IP_HASH = "ip_hash"
    CONSISTENT_HASH = "consistent_hash"
    GEOGRAPHIC = "geographic"
    ADAPTIVE = "adaptive"

class BackendStatus(Enum):
    """Status possíveis para backends"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    FAILING_OVER = "failing_over"

@dataclass
class BackendServer:
    """Configuração de um servidor backend"""
    id: str
    host: str
    port: int
    protocol: str = "http"
    weight: int = 1
    max_connections: int = 100
    region: str = "us-east-1"
    datacenter: str = "primary"
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_check_timeout: int = 5
    health_check_threshold: int = 3
    failover_threshold: int = 3
    enabled: bool = True
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.host or not self.id:
            raise ValueError("Host e ID são obrigatórios")
        if self.port < 1 or self.port > 65535:
            raise ValueError("Porta deve estar entre 1 e 65535")
        if self.weight < 1:
            raise ValueError("Weight deve ser >= 1")

@dataclass
class BackendMetrics:
    """Métricas de performance de um backend"""
    response_time: float = 0.0
    connection_count: int = 0
    active_requests: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    last_health_check: Optional[datetime] = None
    last_response_time: Optional[datetime] = None
    status: BackendStatus = BackendStatus.UNHEALTHY
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    uptime_percentage: float = 0.0
    error_rate: float = 0.0

class AdvancedLoadBalancer:
    """
    Load Balancer Avançado
    
    Implementa múltiplas estratégias de load balancing com health checks,
    failover automático e métricas de performance.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o load balancer avançado
        
        Args:
            config_path: Caminho para arquivo de configuração YAML
        """
        self.config_path = config_path or "config/load_balancer_config.yaml"
        self.backends: Dict[str, BackendServer] = {}
        self.metrics: Dict[str, BackendMetrics] = {}
        self.strategy = LoadBalancingStrategy.ROUND_ROBIN
        self.current_index = 0
        self.health_check_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
        # Configuração de circuit breaker
        self.circuit_breaker_enabled = True
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60
        
        # Configuração de sticky sessions
        self.sticky_sessions_enabled = True
        self.session_timeout = 3600
        self.session_store: Dict[str, Tuple[str, datetime]] = {}
        
        # Configuração de rate limiting
        self.rate_limiting_enabled = True
        self.rate_limit_per_second = 1000
        self.rate_limit_per_minute = 60000
        self.rate_limit_store: Dict[str, List[datetime]] = {}
        
        # Configuração de failover
        self.failover_enabled = True
        self.failover_strategy = "automatic"
        self.primary_datacenter = "primary"
        self.backup_datacenter = "backup"
        
        # Inicialização
        self._load_configuration()
        self._initialize_backends()
        self._start_health_monitoring()
        self._start_metrics_collection()
        
        logger.info("AdvancedLoadBalancer inicializado com sucesso")
    
    def _load_configuration(self) -> None:
        """Carrega configuração do arquivo YAML"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    config = yaml.safe_load(file)
                
                # Configuração geral
                lb_config = config.get('load_balancer', {})
                self.strategy = LoadBalancingStrategy(lb_config.get('strategy', 'round_robin'))
                self.circuit_breaker_enabled = lb_config.get('circuit_breaker_enabled', True)
                self.sticky_sessions_enabled = lb_config.get('sticky_sessions_enabled', True)
                self.rate_limiting_enabled = lb_config.get('rate_limiting_enabled', True)
                self.failover_enabled = lb_config.get('failover_enabled', True)
                
                # Configuração de backends
                backends_config = config.get('backends', [])
                for backend_config in backends_config:
                    backend = BackendServer(
                        id=backend_config['id'],
                        host=backend_config['host'],
                        port=backend_config['port'],
                        protocol=backend_config.get('protocol', 'http'),
                        weight=backend_config.get('weight', 1),
                        max_connections=backend_config.get('max_connections', 100),
                        region=backend_config.get('region', 'us-east-1'),
                        datacenter=backend_config.get('datacenter', 'primary'),
                        health_check_path=backend_config.get('health_check_path', '/health'),
                        health_check_interval=backend_config.get('health_check_interval', 30),
                        health_check_timeout=backend_config.get('health_check_timeout', 5),
                        health_check_threshold=backend_config.get('health_check_threshold', 3),
                        failover_threshold=backend_config.get('failover_threshold', 3),
                        enabled=backend_config.get('enabled', True)
                    )
                    self.backends[backend.id] = backend
                
                logger.info(f"Configuração carregada: {len(self.backends)} backends")
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                self._load_from_environment()
                
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Carrega configuração das variáveis de ambiente"""
        try:
            # Configuração de backends do ambiente
            backend_hosts = os.getenv('LB_BACKEND_HOSTS', '').split(',')
            backend_ports = os.getenv('LB_BACKEND_PORTS', '').split(',')
            backend_regions = os.getenv('LB_BACKEND_REGIONS', '').split(',')
            
            for i, (host, port, region) in enumerate(zip(backend_hosts, backend_ports, backend_regions)):
                if host and port and region:
                    backend = BackendServer(
                        id=f"backend_{i+1}",
                        host=host.strip(),
                        port=int(port.strip()),
                        region=region.strip(),
                        weight=int(os.getenv(f'LB_BACKEND_{i+1}_WEIGHT', '1')),
                        datacenter=os.getenv(f'LB_BACKEND_{i+1}_DATACENTER', 'primary')
                    )
                    self.backends[backend.id] = backend
            
            logger.info(f"Configuração carregada do ambiente: {len(self.backends)} backends")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração do ambiente: {e}")
            raise
    
    def _initialize_backends(self) -> None:
        """Inicializa métricas para todos os backends"""
        for backend_id, backend in self.backends.items():
            self.metrics[backend_id] = BackendMetrics(
                status=BackendStatus.UNHEALTHY if backend.enabled else BackendStatus.MAINTENANCE
            )
    
    def _start_health_monitoring(self) -> None:
        """Inicia monitoramento de saúde dos backends"""
        self.health_check_task = asyncio.create_task(self._health_monitor_loop())
    
    def _start_metrics_collection(self) -> None:
        """Inicia coleta de métricas"""
        self.metrics_task = asyncio.create_task(self._metrics_collection_loop())
    
    async def _health_monitor_loop(self) -> None:
        """Loop de monitoramento de saúde"""
        while True:
            try:
                await self._check_all_backends_health()
                await asyncio.sleep(30)  # Verifica a cada 30 segundos
            except Exception as e:
                logger.error(f"Erro no monitoramento de saúde: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_collection_loop(self) -> None:
        """Loop de coleta de métricas"""
        while True:
            try:
                await self._update_metrics()
                await asyncio.sleep(60)  # Atualiza a cada minuto
            except Exception as e:
                logger.error(f"Erro na coleta de métricas: {e}")
                await asyncio.sleep(30)
    
    async def _check_all_backends_health(self) -> None:
        """Verifica saúde de todos os backends"""
        tasks = []
        for backend_id in self.backends.keys():
            if self.backends[backend_id].enabled:
                task = asyncio.create_task(self._check_backend_health(backend_id))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_backend_health(self, backend_id: str) -> None:
        """Verifica saúde de um backend específico"""
        backend = self.backends[backend_id]
        metrics = self.metrics[backend_id]
        
        try:
            start_time = time.time()
            
            # Faz health check HTTP
            url = f"{backend.protocol}://{backend.host}:{backend.port}{backend.health_check_path}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=backend.health_check_timeout) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        
                        # Atualiza métricas
                        metrics.response_time = response_time
                        metrics.last_health_check = datetime.now()
                        metrics.last_response_time = datetime.now()
                        metrics.consecutive_successes += 1
                        metrics.consecutive_failures = 0
                        metrics.status = BackendStatus.HEALTHY
                        
                        logger.debug(f"Health check {backend_id}: OK ({response_time:.3f}s)")
                    else:
                        raise Exception(f"HTTP {response.status}")
            
        except Exception as e:
            logger.warning(f"Health check {backend_id} falhou: {e}")
            
            # Atualiza métricas de falha
            metrics.consecutive_failures += 1
            metrics.consecutive_successes = 0
            metrics.last_health_check = datetime.now()
            
            # Verifica se precisa marcar como não saudável
            if metrics.consecutive_failures >= backend.health_check_threshold:
                metrics.status = BackendStatus.UNHEALTHY
                
                # Verifica se precisa fazer failover
                if (self.failover_enabled and 
                    backend.datacenter == self.primary_datacenter and
                    metrics.consecutive_failures >= backend.failover_threshold):
                    await self._trigger_failover(backend_id)
    
    async def _trigger_failover(self, failed_backend_id: str) -> None:
        """Dispara processo de failover"""
        logger.warning(f"Iniciando failover - backend {failed_backend_id} não está saudável")
        
        try:
            # Marca status de failover
            self.metrics[failed_backend_id].status = BackendStatus.FAILING_OVER
            
            # Encontra backends de backup disponíveis
            backup_backends = [
                bid for bid, backend in self.backends.items()
                if (backend.datacenter == self.backup_datacenter and
                    self.metrics[bid].status == BackendStatus.HEALTHY)
            ]
            
            if backup_backends:
                logger.info(f"Failover concluído: usando backends de backup {backup_backends}")
            else:
                logger.error("Nenhum backend de backup disponível para failover")
                
        except Exception as e:
            logger.error(f"Erro durante failover: {e}")
    
    async def _update_metrics(self) -> None:
        """Atualiza métricas de performance"""
        for backend_id, metrics in self.metrics.items():
            # Calcula uptime percentage
            if metrics.total_requests > 0:
                metrics.uptime_percentage = (
                    (metrics.total_requests - metrics.failed_requests) / 
                    metrics.total_requests * 100
                )
                metrics.error_rate = metrics.failed_requests / metrics.total_requests * 100
            else:
                metrics.uptime_percentage = 0.0
                metrics.error_rate = 0.0
    
    def select_backend(self, client_ip: Optional[str] = None, session_id: Optional[str] = None) -> Optional[str]:
        """
        Seleciona um backend baseado na estratégia configurada
        
        Args:
            client_ip: IP do cliente (para IP hash e sticky sessions)
            session_id: ID da sessão (para sticky sessions)
            
        Returns:
            ID do backend selecionado ou None se nenhum disponível
        """
        # Filtra backends saudáveis e habilitados
        healthy_backends = [
            bid for bid, backend in self.backends.items()
            if (backend.enabled and 
                self.metrics[bid].status == BackendStatus.HEALTHY)
        ]
        
        if not healthy_backends:
            logger.warning("Nenhum backend saudável disponível")
            return None
        
        # Verifica sticky sessions
        if self.sticky_sessions_enabled and session_id:
            if session_id in self.session_store:
                backend_id, timestamp = self.session_store[session_id]
                if (backend_id in healthy_backends and 
                    datetime.now() - timestamp < timedelta(seconds=self.session_timeout)):
                    return backend_id
                else:
                    # Remove sessão expirada
                    del self.session_store[session_id]
        
        # Aplica estratégia de load balancing
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            selected = self._round_robin_select(healthy_backends)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            selected = self._least_connections_select(healthy_backends)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            selected = self._weighted_round_robin_select(healthy_backends)
        elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            selected = self._least_response_time_select(healthy_backends)
        elif self.strategy == LoadBalancingStrategy.IP_HASH:
            selected = self._ip_hash_select(healthy_backends, client_ip)
        elif self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
            selected = self._consistent_hash_select(healthy_backends, client_ip)
        elif self.strategy == LoadBalancingStrategy.GEOGRAPHIC:
            selected = self._geographic_select(healthy_backends, client_ip)
        elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
            selected = self._adaptive_select(healthy_backends)
        else:
            selected = self._round_robin_select(healthy_backends)
        
        # Atualiza sticky session se habilitado
        if self.sticky_sessions_enabled and session_id and selected:
            self.session_store[session_id] = (selected, datetime.now())
        
        return selected
    
    def _round_robin_select(self, healthy_backends: List[str]) -> str:
        """Seleção round-robin"""
        if not healthy_backends:
            return None
        
        selected = healthy_backends[self.current_index % len(healthy_backends)]
        self.current_index += 1
        return selected
    
    def _least_connections_select(self, healthy_backends: List[str]) -> str:
        """Seleção por menor número de conexões"""
        if not healthy_backends:
            return None
        
        return min(healthy_backends, 
                  key=lambda bid: self.metrics[bid].connection_count)
    
    def _weighted_round_robin_select(self, healthy_backends: List[str]) -> str:
        """Seleção round-robin com pesos"""
        if not healthy_backends:
            return None
        
        # Calcula peso total
        total_weight = sum(self.backends[bid].weight for bid in healthy_backends)
        
        # Seleciona baseado em peso
        current_weight = 0
        for backend_id in healthy_backends:
            current_weight += self.backends[backend_id].weight
            if self.current_index < current_weight:
                self.current_index += 1
                return backend_id
        
        # Reset se chegou ao final
        self.current_index = 0
        return self._weighted_round_robin_select(healthy_backends)
    
    def _least_response_time_select(self, healthy_backends: List[str]) -> str:
        """Seleção por menor tempo de resposta"""
        if not healthy_backends:
            return None
        
        return min(healthy_backends, 
                  key=lambda bid: self.metrics[bid].response_time or float('inf'))
    
    def _ip_hash_select(self, healthy_backends: List[str], client_ip: Optional[str]) -> str:
        """Seleção por hash do IP"""
        if not healthy_backends or not client_ip:
            return self._round_robin_select(healthy_backends)
        
        # Calcula hash do IP
        hash_value = hash(client_ip) % len(healthy_backends)
        return healthy_backends[hash_value]
    
    def _consistent_hash_select(self, healthy_backends: List[str], client_ip: Optional[str]) -> str:
        """Seleção por hash consistente"""
        if not healthy_backends or not client_ip:
            return self._round_robin_select(healthy_backends)
        
        # Implementação simplificada de hash consistente
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return healthy_backends[hash_value % len(healthy_backends)]
    
    def _geographic_select(self, healthy_backends: List[str], client_ip: Optional[str]) -> str:
        """Seleção geográfica (simplificada)"""
        if not healthy_backends or not client_ip:
            return self._round_robin_select(healthy_backends)
        
        # Implementação simplificada - usa IP hash como proxy para localização
        return self._ip_hash_select(healthy_backends, client_ip)
    
    def _adaptive_select(self, healthy_backends: List[str]) -> str:
        """Seleção adaptativa baseada em múltiplos fatores"""
        if not healthy_backends:
            return None
        
        # Calcula score para cada backend
        scores = {}
        for backend_id in healthy_backends:
            metrics = self.metrics[backend_id]
            backend = self.backends[backend_id]
            
            # Score baseado em múltiplos fatores
            response_time_score = 1.0 / (metrics.response_time + 0.001)
            connection_score = 1.0 / (metrics.connection_count + 1)
            uptime_score = metrics.uptime_percentage / 100.0
            weight_score = backend.weight
            
            total_score = (
                response_time_score * 0.3 +
                connection_score * 0.2 +
                uptime_score * 0.3 +
                weight_score * 0.2
            )
            
            scores[backend_id] = total_score
        
        # Retorna backend com maior score
        return max(scores.keys(), key=lambda bid: scores[bid])
    
    def record_request(self, backend_id: str, response_time: float, success: bool = True) -> None:
        """
        Registra métricas de uma requisição
        
        Args:
            backend_id: ID do backend
            response_time: Tempo de resposta em segundos
            success: Se a requisição foi bem-sucedida
        """
        if backend_id not in self.metrics:
            return
        
        metrics = self.metrics[backend_id]
        metrics.total_requests += 1
        metrics.response_time = response_time
        metrics.last_response_time = datetime.now()
        
        if success:
            metrics.consecutive_successes += 1
            metrics.consecutive_failures = 0
        else:
            metrics.failed_requests += 1
            metrics.consecutive_failures += 1
            metrics.consecutive_successes = 0
    
    def increment_connection(self, backend_id: str) -> None:
        """Incrementa contador de conexões"""
        if backend_id in self.metrics:
            self.metrics[backend_id].connection_count += 1
    
    def decrement_connection(self, backend_id: str) -> None:
        """Decrementa contador de conexões"""
        if backend_id in self.metrics:
            self.metrics[backend_id].connection_count = max(0, self.metrics[backend_id].connection_count - 1)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de todos os backends"""
        return {
            backend_id: {
                "id": backend_id,
                "host": backend.host,
                "port": backend.port,
                "region": backend.region,
                "datacenter": backend.datacenter,
                "status": metrics.status.value,
                "response_time": metrics.response_time,
                "connection_count": metrics.connection_count,
                "total_requests": metrics.total_requests,
                "failed_requests": metrics.failed_requests,
                "uptime_percentage": metrics.uptime_percentage,
                "error_rate": metrics.error_rate,
                "consecutive_failures": metrics.consecutive_failures,
                "consecutive_successes": metrics.consecutive_successes,
                "last_health_check": metrics.last_health_check.isoformat() if metrics.last_health_check else None,
                "last_response_time": metrics.last_response_time.isoformat() if metrics.last_response_time else None
            }
            for backend_id, backend in self.backends.items()
            for metrics in [self.metrics[backend_id]]
        }
    
    def get_healthy_backends(self) -> List[str]:
        """Retorna lista de backends saudáveis"""
        return [
            bid for bid, backend in self.backends.items()
            if (backend.enabled and 
                self.metrics[bid].status == BackendStatus.HEALTHY)
        ]
    
    def get_backend_url(self, backend_id: str, path: str = "") -> Optional[str]:
        """Retorna URL completa de um backend"""
        if backend_id not in self.backends:
            return None
        
        backend = self.backends[backend_id]
        return f"{backend.protocol}://{backend.host}:{backend.port}{path}"
    
    async def close(self) -> None:
        """Fecha o load balancer"""
        if self.health_check_task:
            self.health_check_task.cancel()
        if self.metrics_task:
            self.metrics_task.cancel()
        
        logger.info("AdvancedLoadBalancer fechado")

# Singleton instance
_lb_instance: Optional[AdvancedLoadBalancer] = None

def get_load_balancer() -> AdvancedLoadBalancer:
    """Retorna instância singleton do load balancer"""
    global _lb_instance
    if _lb_instance is None:
        _lb_instance = AdvancedLoadBalancer()
    return _lb_instance

async def close_load_balancer() -> None:
    """Fecha o load balancer"""
    global _lb_instance
    if _lb_instance:
        await _lb_instance.close()
        _lb_instance = None 