"""
Módulo de Microserviços para Sistemas Enterprise
Sistema de comunicação e orquestração de microserviços - Omni Keywords Finder

Prompt: Implementação de sistema de microserviços enterprise
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import asyncio
import json
import logging
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import statistics
from concurrent.futures import ThreadPoolExecutor
import hashlib

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Status dos serviços."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class CircuitBreakerState(Enum):
    """Estados do circuit breaker."""
    CLOSED = "closed"  # Funcionando normalmente
    OPEN = "open"      # Falhas detectadas, bloqueando requests
    HALF_OPEN = "half_open"  # Testando se o serviço se recuperou


@dataclass
class ServiceEndpoint:
    """Endpoint de um serviço."""
    service_name: str
    host: str
    port: int
    protocol: str = "http"
    path: str = "/"
    timeout: int = 30
    retries: int = 3
    health_check_path: str = "/health"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.service_name or len(self.service_name.strip()) == 0:
            raise ValueError("Nome do serviço não pode ser vazio")
        if not self.host or len(self.host.strip()) == 0:
            raise ValueError("Host não pode ser vazio")
        if not 1 <= self.port <= 65535:
            raise ValueError("Porta deve estar entre 1 e 65535")
        if self.timeout < 1:
            raise ValueError("Timeout deve ser pelo menos 1 segundo")
        if self.retries < 0:
            raise ValueError("Retries não pode ser negativo")
        
        # Normalizar campos
        self.service_name = self.service_name.strip()
        self.host = self.host.strip()
        self.protocol = self.protocol.lower()
    
    def get_url(self, path: str = None) -> str:
        """Gera URL completa do endpoint."""
        base_path = path or self.path
        return f"{self.protocol}://{self.host}:{self.port}{base_path}"
    
    def get_health_url(self) -> str:
        """Gera URL do health check."""
        return self.get_url(self.health_check_path)


@dataclass
class ServiceInstance:
    """Instância de um serviço."""
    id: str
    service_name: str
    endpoint: ServiceEndpoint
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    health_check_failures: int = 0
    response_time: float = 0.0  # em ms
    error_rate: float = 0.0  # taxa de erro (0-1)
    load: float = 0.0  # carga atual (0-1)
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.id or len(self.id.strip()) == 0:
            raise ValueError("ID da instância não pode ser vazio")
        if self.health_check_failures < 0:
            raise ValueError("Health check failures não pode ser negativo")
        if self.response_time < 0:
            raise ValueError("Response time não pode ser negativo")
        if not 0 <= self.error_rate <= 1:
            raise ValueError("Error rate deve estar entre 0 e 1")
        if not 0 <= self.load <= 1:
            raise ValueError("Load deve estar entre 0 e 1")
        
        # Normalizar campos
        self.id = self.id.strip()
    
    def is_healthy(self) -> bool:
        """Verifica se a instância está saudável."""
        return self.status == ServiceStatus.HEALTHY
    
    def get_health_score(self) -> float:
        """Calcula score de saúde da instância (0-1)."""
        if not self.is_healthy():
            return 0.0
        
        # Fatores que afetam a saúde
        response_factor = max(0.0, 1.0 - (self.response_time / 5000.0))  # 5s como referência
        error_factor = 1.0 - self.error_rate
        load_factor = 1.0 - self.load
        
        # Score combinado
        score = (response_factor * 0.4 + 
                error_factor * 0.4 + 
                load_factor * 0.2)
        
        return max(0.0, min(1.0, score))


@dataclass
class CircuitBreakerConfig:
    """Configuração do circuit breaker."""
    failure_threshold: int = 5  # Número de falhas para abrir
    recovery_timeout: int = 60  # Tempo em segundos para tentar recuperar
    expected_exception: type = Exception  # Tipo de exceção esperada
    success_threshold: int = 2  # Número de sucessos para fechar
    monitor_interval: int = 10  # Intervalo de monitoramento em segundos

    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.failure_threshold < 1:
            raise ValueError("Failure threshold deve ser pelo menos 1")
        if self.recovery_timeout < 1:
            raise ValueError("Recovery timeout deve ser pelo menos 1 segundo")
        if self.success_threshold < 1:
            raise ValueError("Success threshold deve ser pelo menos 1")
        if self.monitor_interval < 1:
            raise ValueError("Monitor interval deve ser pelo menos 1 segundo")


class CircuitBreaker:
    """Implementação de circuit breaker para resiliência."""
    
    def __init__(self, config: CircuitBreakerConfig):
        """
        Inicializa o circuit breaker.
        
        Args:
            config: Configuração do circuit breaker
        """
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
        logger.info(f"CircuitBreaker inicializado - Config: {config}")
    
    def can_execute(self) -> bool:
        """Verifica se pode executar a operação."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Verificar se já passou tempo suficiente para tentar recuperar
            if (self.last_failure_time and 
                datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.config.recovery_timeout)):
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def on_success(self) -> None:
        """Chamado quando uma operação é bem-sucedida."""
        self.failure_count = 0
        self.success_count += 1
        self.last_success_time = datetime.utcnow()
        
        if self.state == CircuitBreakerState.HALF_OPEN and self.success_count >= self.config.success_threshold:
            self.state = CircuitBreakerState.CLOSED
            self.success_count = 0
            logger.info("CircuitBreaker fechado - Serviço recuperado")
    
    def on_failure(self, exception: Exception) -> None:
        """Chamado quando uma operação falha."""
        if isinstance(exception, self.config.expected_exception):
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"CircuitBreaker aberto - {self.failure_count} falhas consecutivas")
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                self.success_count = 0
                logger.warning("CircuitBreaker reaberto após falha")
    
    def get_state(self) -> CircuitBreakerState:
        """Retorna o estado atual do circuit breaker."""
        return self.state
    
    def reset(self) -> None:
        """Reseta o circuit breaker para o estado fechado."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        logger.info("CircuitBreaker resetado")


class ServiceDiscovery:
    """Sistema de descoberta de serviços."""
    
    def __init__(self):
        """Inicializa o service discovery."""
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.health_check_task = None
        self.is_running = False
        
        logger.info("ServiceDiscovery inicializado")
    
    def register_service(self, instance: ServiceInstance) -> None:
        """
        Registra uma instância de serviço.
        
        Args:
            instance: Instância do serviço
        """
        if instance.service_name not in self.services:
            self.services[instance.service_name] = []
        
        # Verificar se já existe
        existing = next((s for s in self.services[instance.service_name] if s.id == instance.id), None)
        if existing:
            # Atualizar instância existente
            existing.status = instance.status
            existing.endpoint = instance.endpoint
            existing.response_time = instance.response_time
            existing.error_rate = instance.error_rate
            existing.load = instance.load
            existing.version = instance.version
            existing.metadata = instance.metadata
        else:
            # Adicionar nova instância
            self.services[instance.service_name].append(instance)
        
        logger.info(f"Serviço registrado: {instance.service_name} ({instance.id})")
    
    def unregister_service(self, service_name: str, instance_id: str) -> bool:
        """
        Remove registro de uma instância de serviço.
        
        Args:
            service_name: Nome do serviço
            instance_id: ID da instância
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        if service_name not in self.services:
            return False
        
        instances = self.services[service_name]
        for i, instance in enumerate(instances):
            if instance.id == instance_id:
                del instances[i]
                logger.info(f"Serviço removido: {service_name} ({instance_id})")
                return True
        
        return False
    
    def get_service_instances(self, service_name: str, healthy_only: bool = True) -> List[ServiceInstance]:
        """
        Obtém instâncias de um serviço.
        
        Args:
            service_name: Nome do serviço
            healthy_only: Retornar apenas instâncias saudáveis
            
        Returns:
            Lista de instâncias do serviço
        """
        if service_name not in self.services:
            return []
        
        instances = self.services[service_name]
        
        if healthy_only:
            instances = [i for i in instances if i.is_healthy()]
        
        return instances
    
    def get_best_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """
        Obtém a melhor instância de um serviço baseado em saúde e carga.
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            Melhor instância ou None se não houver
        """
        instances = self.get_service_instances(service_name, healthy_only=True)
        
        if not instances:
            return None
        
        # Selecionar instância com melhor score de saúde
        best_instance = max(instances, key=lambda i: i.get_health_score())
        return best_instance
    
    async def start_health_checks(self, interval: int = 30) -> None:
        """
        Inicia health checks periódicos.
        
        Args:
            interval: Intervalo entre health checks em segundos
        """
        if self.is_running:
            return
        
        self.is_running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop(interval))
        logger.info(f"Health checks iniciados - Intervalo: {interval}s")
    
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
    
    async def _health_check_loop(self, interval: int) -> None:
        """Loop principal de health checks."""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no health check loop: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_checks(self) -> None:
        """Executa health checks em todos os serviços."""
        tasks = []
        
        for service_name, instances in self.services.items():
            for instance in instances:
                task = asyncio.create_task(self._check_instance_health(instance))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_instance_health(self, instance: ServiceInstance) -> None:
        """Verifica saúde de uma instância específica."""
        try:
            health_url = instance.endpoint.get_health_url()
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(health_url, timeout=instance.endpoint.timeout) as response:
                    response_time = (time.time() - start_time) * 1000  # Converter para ms
                    
                    if response.status == 200:
                        instance.status = ServiceStatus.HEALTHY
                        instance.health_check_failures = 0
                        instance.response_time = response_time
                        instance.last_health_check = datetime.utcnow()
                    else:
                        instance.health_check_failures += 1
                        if instance.health_check_failures >= 3:
                            instance.status = ServiceStatus.UNHEALTHY
                        else:
                            instance.status = ServiceStatus.DEGRADED
                        
                        instance.last_health_check = datetime.utcnow()
                        
        except Exception as e:
            instance.health_check_failures += 1
            if instance.health_check_failures >= 3:
                instance.status = ServiceStatus.UNHEALTHY
            else:
                instance.status = ServiceStatus.DEGRADED
            
            instance.last_health_check = datetime.utcnow()
            logger.warning(f"Health check falhou para {instance.service_name} ({instance.id}): {e}")


class MicroserviceClient:
    """Cliente para comunicação com microserviços."""
    
    def __init__(self, service_discovery: ServiceDiscovery, 
                 circuit_breaker_config: CircuitBreakerConfig = None):
        """
        Inicializa o cliente de microserviços.
        
        Args:
            service_discovery: Sistema de descoberta de serviços
            circuit_breaker_config: Configuração do circuit breaker
        """
        self.service_discovery = service_discovery
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.default_circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        
        logger.info("MicroserviceClient inicializado")
    
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Obtém ou cria circuit breaker para um serviço."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(self.default_circuit_breaker_config)
        
        return self.circuit_breakers[service_name]
    
    async def call_service(self, service_name: str, method: str = "GET", 
                          path: str = "/", data: Dict[str, Any] = None,
                          headers: Dict[str, str] = None, 
                          timeout: int = 30) -> Tuple[int, Dict[str, Any]]:
        """
        Chama um serviço.
        
        Args:
            service_name: Nome do serviço
            method: Método HTTP
            path: Caminho da requisição
            data: Dados da requisição
            headers: Headers da requisição
            timeout: Timeout em segundos
            
        Returns:
            Tupla (status_code, response_data)
        """
        circuit_breaker = self._get_circuit_breaker(service_name)
        
        if not circuit_breaker.can_execute():
            raise Exception(f"Circuit breaker aberto para serviço {service_name}")
        
        try:
            # Obter melhor instância do serviço
            instance = self.service_discovery.get_best_instance(service_name)
            if not instance:
                raise Exception(f"Nenhuma instância disponível para serviço {service_name}")
            
            # Fazer requisição
            url = instance.endpoint.get_url(path)
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                if method.upper() == "GET":
                    async with session.get(url, headers=headers, timeout=timeout) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_data = await response.json()
                        
                        # Atualizar métricas da instância
                        instance.response_time = response_time
                        if response.status >= 400:
                            instance.error_rate = min(1.0, instance.error_rate + 0.1)
                        else:
                            instance.error_rate = max(0.0, instance.error_rate - 0.05)
                        
                        circuit_breaker.on_success()
                        return response.status, response_data
                
                elif method.upper() == "POST":
                    async with session.post(url, json=data, headers=headers, timeout=timeout) as response:
                        response_time = (time.time() - start_time) * 1000
                        response_data = await response.json()
                        
                        # Atualizar métricas da instância
                        instance.response_time = response_time
                        if response.status >= 400:
                            instance.error_rate = min(1.0, instance.error_rate + 0.1)
                        else:
                            instance.error_rate = max(0.0, instance.error_rate - 0.05)
                        
                        circuit_breaker.on_success()
                        return response.status, response_data
                
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")
                    
        except Exception as e:
            circuit_breaker.on_failure(e)
            raise
    
    async def call_service_with_fallback(self, service_name: str, method: str = "GET",
                                        path: str = "/", data: Dict[str, Any] = None,
                                        headers: Dict[str, str] = None,
                                        fallback: Callable = None) -> Dict[str, Any]:
        """
        Chama um serviço com fallback.
        
        Args:
            service_name: Nome do serviço
            method: Método HTTP
            path: Caminho da requisição
            data: Dados da requisição
            headers: Headers da requisição
            fallback: Função de fallback
            
        Returns:
            Dados da resposta ou resultado do fallback
        """
        try:
            status_code, response_data = await self.call_service(
                service_name, method, path, data, headers
            )
            return response_data
        except Exception as e:
            logger.warning(f"Falha ao chamar serviço {service_name}: {e}")
            
            if fallback:
                try:
                    return await fallback()
                except Exception as fallback_error:
                    logger.error(f"Fallback também falhou: {fallback_error}")
                    raise
            
            raise
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """
        Obtém status de um serviço.
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            Status do serviço
        """
        instances = self.service_discovery.get_service_instances(service_name, healthy_only=False)
        circuit_breaker = self._get_circuit_breaker(service_name)
        
        return {
            "service_name": service_name,
            "total_instances": len(instances),
            "healthy_instances": len([i for i in instances if i.is_healthy()]),
            "circuit_breaker_state": circuit_breaker.get_state().value,
            "instances": [
                {
                    "id": i.id,
                    "status": i.status.value,
                    "response_time": i.response_time,
                    "error_rate": i.error_rate,
                    "load": i.load,
                    "health_score": i.get_health_score()
                }
                for i in instances
            ]
        }


# Função de conveniência para criar cliente de microserviços
def create_microservice_client(service_discovery: ServiceDiscovery = None,
                              circuit_breaker_config: CircuitBreakerConfig = None) -> MicroserviceClient:
    """
    Cria um cliente de microserviços com configurações padrão.
    
    Args:
        service_discovery: Sistema de descoberta de serviços
        circuit_breaker_config: Configuração do circuit breaker
        
    Returns:
        Instância configurada do MicroserviceClient
    """
    if service_discovery is None:
        service_discovery = ServiceDiscovery()
    
    return MicroserviceClient(service_discovery, circuit_breaker_config) 