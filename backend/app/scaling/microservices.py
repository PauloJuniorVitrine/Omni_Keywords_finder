"""
Sistema de Arquitetura de Microserviços
Melhora escalabilidade e manutenibilidade através de microserviços
"""

import asyncio
import time
import json
import uuid
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import aiohttp
import socket
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    MAINTENANCE = "maintenance"


class ServiceType(Enum):
    API = "api"
    WORKER = "worker"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    MONITORING = "monitoring"


class CommunicationProtocol(Enum):
    HTTP = "http"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MESSAGE_QUEUE = "message_queue"


@dataclass
class ServiceInfo:
    id: str
    name: str
    service_type: ServiceType
    version: str
    host: str
    port: int
    protocol: CommunicationProtocol
    status: ServiceStatus
    health_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"
    created_at: datetime = None
    last_heartbeat: datetime = None
    metadata: Dict[str, Any] = None


@dataclass
class ServiceMetrics:
    request_count: int
    error_count: int
    avg_response_time: float
    active_connections: int
    memory_usage: float
    cpu_usage: float
    uptime: float


@dataclass
class ServiceRequest:
    id: str
    service_id: str
    method: str
    endpoint: str
    headers: Dict[str, str]
    data: Any
    timestamp: datetime
    timeout: int = 30


class ServiceRegistry:
    """
    Registro de serviços para descoberta
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.service_instances: Dict[str, List[ServiceInfo]] = {}
        self.health_check_task = None
        self.is_running = False
    
    async def start(self):
        """Inicia o registro de serviços"""
        if self.is_running:
            return
        
        self.is_running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Service registry started")
    
    async def stop(self):
        """Para o registro de serviços"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Service registry stopped")
    
    def register_service(self, service: ServiceInfo) -> bool:
        """Registra um serviço"""
        try:
            self.services[service.id] = service
            
            if service.name not in self.service_instances:
                self.service_instances[service.name] = []
            
            self.service_instances[service.name].append(service)
            
            logger.info(f"Service registered: {service.name} ({service.id})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering service {service.id}: {e}")
            return False
    
    def unregister_service(self, service_id: str) -> bool:
        """Remove registro de serviço"""
        if service_id in self.services:
            service = self.services[service_id]
            
            # Remover de service_instances
            if service.name in self.service_instances:
                self.service_instances[service.name] = [
                    s for s in self.service_instances[service.name]
                    if s.id != service_id
                ]
                
                if not self.service_instances[service.name]:
                    del self.service_instances[service.name]
            
            del self.services[service_id]
            
            logger.info(f"Service unregistered: {service_id}")
            return True
        
        return False
    
    def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Obtém serviço por ID"""
        return self.services.get(service_id)
    
    def get_service_instances(self, service_name: str) -> List[ServiceInfo]:
        """Obtém instâncias de um serviço"""
        return self.service_instances.get(service_name, [])
    
    def get_healthy_instances(self, service_name: str) -> List[ServiceInfo]:
        """Obtém instâncias saudáveis de um serviço"""
        instances = self.get_service_instances(service_name)
        return [i for i in instances if i.status == ServiceStatus.HEALTHY]
    
    async def _health_check_loop(self):
        """Loop de verificação de saúde"""
        while self.is_running:
            try:
                await self._check_services_health()
                await asyncio.sleep(30)  # Verificar a cada 30 segundos
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_services_health(self):
        """Verifica saúde dos serviços"""
        for service in list(self.services.values()):
            try:
                if service.protocol == CommunicationProtocol.HTTP:
                    await self._check_http_service_health(service)
                # Adicionar outros protocolos conforme necessário
                
            except Exception as e:
                logger.error(f"Health check failed for service {service.id}: {e}")
    
    async def _check_http_service_health(self, service: ServiceInfo):
        """Verifica saúde de serviço HTTP"""
        try:
            url = f"http://{service.host}:{service.port}{service.health_endpoint}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        service.status = ServiceStatus.HEALTHY
                        service.last_heartbeat = datetime.now()
                    else:
                        service.status = ServiceStatus.UNHEALTHY
        except Exception as e:
            service.status = ServiceStatus.UNHEALTHY
            logger.warning(f"Health check failed for {service.id}: {e}")


class ServiceDiscovery:
    """
    Descoberta de serviços
    """
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.load_balancer = None  # Pode ser integrado com load balancer
    
    def discover_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Descobre um serviço"""
        healthy_instances = self.registry.get_healthy_instances(service_name)
        
        if not healthy_instances:
            return None
        
        # Implementar estratégia de seleção (round robin, least connections, etc.)
        return healthy_instances[0]  # Simplificado
    
    def discover_all_services(self, service_name: str) -> List[ServiceInfo]:
        """Descobre todas as instâncias de um serviço"""
        return self.registry.get_healthy_instances(service_name)


class ServiceClient:
    """
    Cliente para comunicação com microserviços
    """
    
    def __init__(self, service_discovery: ServiceDiscovery):
        self.service_discovery = service_discovery
        self.session = aiohttp.ClientSession()
        self.request_timeout = 30
        self.retry_attempts = 3
        self.retry_delay = 1
    
    async def close(self):
        """Fecha o cliente"""
        await self.session.close()
    
    async def request(self, service_name: str, method: str, endpoint: str,
                     headers: Dict[str, str] = None, data: Any = None,
                     timeout: int = None) -> Dict[str, Any]:
        """Faz requisição para um serviço"""
        service = self.service_discovery.discover_service(service_name)
        if not service:
            return {
                'success': False,
                'error': f'Service {service_name} not found',
                'status_code': 503
            }
        
        url = f"http://{service.host}:{service.port}{endpoint}"
        timeout = timeout or self.request_timeout
        
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.request(
                    method, url, headers=headers, json=data,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    response_data = await response.read()
                    
                    return {
                        'success': True,
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'data': response_data,
                        'service_id': service.id
                    }
            
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    return {
                        'success': False,
                        'error': str(e),
                        'status_code': 500,
                        'service_id': service.id
                    }
                
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return {
            'success': False,
            'error': 'Max retry attempts reached',
            'status_code': 500
        }


class CircuitBreaker:
    """
    Circuit breaker para resiliência
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Executa função com circuit breaker"""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Chamado em caso de sucesso"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Chamado em caso de falha"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar reset"""
        if not self.last_failure_time:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() > self.recovery_timeout


class ServiceMesh:
    """
    Service mesh para gerenciamento de comunicação entre serviços
    """
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.service_clients: Dict[str, ServiceClient] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def get_service_client(self, service_name: str) -> ServiceClient:
        """Obtém cliente para um serviço"""
        if service_name not in self.service_clients:
            discovery = ServiceDiscovery(self.registry)
            self.service_clients[service_name] = ServiceClient(discovery)
        
        return self.service_clients[service_name]
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Obtém circuit breaker para um serviço"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        
        return self.circuit_breakers[service_name]
    
    async def request(self, service_name: str, method: str, endpoint: str,
                     headers: Dict[str, str] = None, data: Any = None) -> Dict[str, Any]:
        """Faz requisição com circuit breaker"""
        client = self.get_service_client(service_name)
        circuit_breaker = self.get_circuit_breaker(service_name)
        
        start_time = time.time()
        
        try:
            result = await circuit_breaker.call(
                client.request, service_name, method, endpoint, headers, data
            )
            
            # Registrar métricas
            self._record_metrics(service_name, time.time() - start_time, result['success'])
            
            return result
            
        except Exception as e:
            self._record_metrics(service_name, time.time() - start_time, False)
            raise e
    
    def _record_metrics(self, service_name: str, response_time: float, success: bool):
        """Registra métricas"""
        if service_name not in self.metrics:
            self.metrics[service_name] = {
                'request_count': 0,
                'success_count': 0,
                'error_count': 0,
                'total_response_time': 0.0,
                'avg_response_time': 0.0
            }
        
        metrics = self.metrics[service_name]
        metrics['request_count'] += 1
        metrics['total_response_time'] += response_time
        metrics['avg_response_time'] = metrics['total_response_time'] / metrics['request_count']
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['error_count'] += 1
    
    def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Obtém métricas de um serviço"""
        return self.metrics.get(service_name, {})
    
    async def close(self):
        """Fecha o service mesh"""
        for client in self.service_clients.values():
            await client.close()


class MicroserviceManager:
    """
    Gerenciador de microserviços
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.registry = ServiceRegistry()
        self.service_mesh = ServiceMesh(self.registry)
        self.services: Dict[str, Any] = {}
        self.is_running = False
    
    async def start(self):
        """Inicia o gerenciador"""
        if self.is_running:
            return
        
        await self.registry.start()
        self.is_running = True
        logger.info("Microservice manager started")
    
    async def stop(self):
        """Para o gerenciador"""
        if not self.is_running:
            return
        
        await self.service_mesh.close()
        await self.registry.stop()
        self.is_running = False
        logger.info("Microservice manager stopped")
    
    def register_service(self, service_info: ServiceInfo) -> bool:
        """Registra um serviço"""
        return self.registry.register_service(service_info)
    
    async def call_service(self, service_name: str, method: str, endpoint: str,
                          headers: Dict[str, str] = None, data: Any = None) -> Dict[str, Any]:
        """Chama um serviço"""
        return await self.service_mesh.request(service_name, method, endpoint, headers, data)
    
    def get_service_status(self, service_name: str) -> List[Dict[str, Any]]:
        """Obtém status de um serviço"""
        instances = self.registry.get_service_instances(service_name)
        return [
            {
                'id': instance.id,
                'name': instance.name,
                'host': instance.host,
                'port': instance.port,
                'status': instance.status.value,
                'last_heartbeat': instance.last_heartbeat.isoformat() if instance.last_heartbeat else None
            }
            for instance in instances
        ]
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Obtém todos os serviços"""
        return [
            {
                'id': service.id,
                'name': service.name,
                'type': service.service_type.value,
                'version': service.version,
                'status': service.status.value,
                'instances': len(self.registry.get_service_instances(service.name))
            }
            for service in self.registry.services.values()
        ]


# Funções utilitárias
def create_microservice_manager(config: Optional[Dict] = None) -> MicroserviceManager:
    """Cria gerenciador de microserviços"""
    return MicroserviceManager(config)


def create_service_info(name: str, service_type: ServiceType, host: str, port: int,
                       protocol: CommunicationProtocol = CommunicationProtocol.HTTP,
                       version: str = "1.0.0") -> ServiceInfo:
    """Cria informações de serviço"""
    return ServiceInfo(
        id=str(uuid.uuid4()),
        name=name,
        service_type=service_type,
        version=version,
        host=host,
        port=port,
        protocol=protocol,
        status=ServiceStatus.STARTING,
        created_at=datetime.now()
    )


# Instância global
microservice_manager = MicroserviceManager()


# Decorator para chamadas de serviço
def service_call(service_name: str, method: str = "GET", endpoint: str = "/"):
    """Decorator para chamadas de serviço"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair dados da função
            data = kwargs.get('data')
            headers = kwargs.get('headers', {})
            
            # Chamar serviço
            result = await microservice_manager.call_service(
                service_name, method, endpoint, headers, data
            )
            
            if not result['success']:
                raise Exception(f"Service call failed: {result['error']}")
            
            return result['data']
        
        return wrapper
    return decorator


# Decorator para registro de serviço
def register_service(service_type: ServiceType, version: str = "1.0.0"):
    """Decorator para registro de serviço"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Criar informações do serviço
            service_info = create_service_info(
                name=func.__name__,
                service_type=service_type,
                host=socket.gethostname(),
                port=kwargs.get('port', 8000),
                version=version
            )
            
            # Registrar serviço
            microservice_manager.register_service(service_info)
            
            # Executar função
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator 