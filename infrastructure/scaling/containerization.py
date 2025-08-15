"""
Módulo de Containerização para Sistemas Enterprise
Sistema de containers e orquestração - Omni Keywords Finder

Prompt: Implementação de sistema de containerização enterprise
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import asyncio
import json
import logging
import subprocess
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
import tempfile
import shutil

logger = logging.getLogger(__name__)


class ContainerStatus(Enum):
    """Status dos containers."""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    CREATED = "created"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"


class ContainerType(Enum):
    """Tipos de containers."""
    APPLICATION = "application"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    MONITORING = "monitoring"
    LOAD_BALANCER = "load_balancer"


@dataclass
class ContainerConfig:
    """Configuração de um container."""
    name: str
    image: str
    container_type: ContainerType
    ports: Dict[str, str] = field(default_factory=dict)  # host_port: container_port
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)  # host_path: container_path
    networks: List[str] = field(default_factory=list)
    restart_policy: str = "unless-stopped"
    memory_limit: str = "512m"
    cpu_limit: str = "0.5"
    health_check: Dict[str, Any] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    command: List[str] = field(default_factory=list)
    working_dir: str = "/app"
    user: str = ""
    privileged: bool = False
    read_only: bool = False

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Nome do container não pode ser vazio")
        if not self.image or len(self.image.strip()) == 0:
            raise ValueError("Imagem do container não pode ser vazia")
        if self.memory_limit and not self._is_valid_memory_limit(self.memory_limit):
            raise ValueError("Memory limit deve ser um valor válido (ex: 512m, 1g)")
        if self.cpu_limit and not self._is_valid_cpu_limit(self.cpu_limit):
            raise ValueError("CPU limit deve ser um valor válido (ex: 0.5, 1.0)")
        
        # Normalizar campos
        self.name = self.name.strip()
        self.image = self.image.strip()
    
    def _is_valid_memory_limit(self, limit: str) -> bool:
        """Valida formato de memory limit."""
        if not limit:
            return True
        
        try:
            # Verificar se termina com unidades válidas
            if limit.endswith(('b', 'k', 'm', 'g')):
                value = limit[:-1]
                float(value)
                return True
            else:
                # Apenas número
                float(limit)
                return True
        except ValueError:
            return False
    
    def _is_valid_cpu_limit(self, limit: str) -> bool:
        """Valida formato de CPU limit."""
        if not limit:
            return True
        
        try:
            value = float(limit)
            return value >= 0
        except ValueError:
            return False


@dataclass
class Container:
    """Representa um container."""
    id: str
    name: str
    image: str
    status: ContainerStatus
    container_type: ContainerType
    created_at: datetime
    ports: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    volumes: Dict[str, str] = field(default_factory=dict)
    networks: List[str] = field(default_factory=list)
    memory_usage: str = "0b"
    cpu_usage: float = 0.0
    network_io: str = "0b"
    health_status: str = "healthy"
    restart_count: int = 0
    exit_code: Optional[int] = None
    last_health_check: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.id or len(self.id.strip()) == 0:
            raise ValueError("ID do container não pode ser vazio")
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Nome do container não pode ser vazio")
        if not self.image or len(self.image.strip()) == 0:
            raise ValueError("Imagem do container não pode ser vazia")
        if self.restart_count < 0:
            raise ValueError("Restart count não pode ser negativo")
        
        # Normalizar campos
        self.id = self.id.strip()
        self.name = self.name.strip()
        self.image = self.image.strip()
    
    def is_running(self) -> bool:
        """Verifica se o container está rodando."""
        return self.status == ContainerStatus.RUNNING
    
    def is_healthy(self) -> bool:
        """Verifica se o container está saudável."""
        return self.health_status == "healthy"
    
    def get_uptime(self) -> timedelta:
        """Calcula tempo de atividade do container."""
        return datetime.utcnow() - self.created_at


@dataclass
class KubernetesConfig:
    """Configuração do Kubernetes."""
    namespace: str = "default"
    replicas: int = 1
    image_pull_policy: str = "IfNotPresent"
    service_type: str = "ClusterIP"
    service_port: int = 80
    target_port: int = 8080
    resource_limits: Dict[str, str] = field(default_factory=dict)
    resource_requests: Dict[str, str] = field(default_factory=dict)
    liveness_probe: Dict[str, Any] = field(default_factory=dict)
    readiness_probe: Dict[str, Any] = field(default_factory=dict)
    node_selector: Dict[str, str] = field(default_factory=dict)
    tolerations: List[Dict[str, Any]] = field(default_factory=list)
    affinity: Dict[str, Any] = field(default_factory=dict)
    security_context: Dict[str, Any] = field(default_factory=dict)
    service_account: str = ""

    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self.namespace or len(self.namespace.strip()) == 0:
            raise ValueError("Namespace não pode ser vazio")
        if self.replicas < 1:
            raise ValueError("Replicas deve ser pelo menos 1")
        if self.service_port < 1 or self.service_port > 65535:
            raise ValueError("Service port deve estar entre 1 e 65535")
        if self.target_port < 1 or self.target_port > 65535:
            raise ValueError("Target port deve estar entre 1 e 65535")
        
        # Normalizar campos
        self.namespace = self.namespace.strip()


class ContainerManager:
    """Gerenciador de containers para sistemas enterprise."""
    
    def __init__(self, docker_socket: str = "/var/run/docker.sock"):
        """
        Inicializa o gerenciador de containers.
        
        Args:
            docker_socket: Caminho para o socket do Docker
        """
        self.docker_socket = docker_socket
        self.containers: Dict[str, Container] = {}
        self.networks: List[str] = []
        self.volumes: List[str] = []
        
        logger.info(f"ContainerManager inicializado - Docker socket: {docker_socket}")
    
    async def create_container(self, config: ContainerConfig) -> Container:
        """
        Cria um novo container.
        
        Args:
            config: Configuração do container
            
        Returns:
            Container criado
        """
        try:
            # Simular criação de container
            container_id = f"container_{len(self.containers) + 1}"
            
            container = Container(
                id=container_id,
                name=config.name,
                image=config.image,
                status=ContainerStatus.CREATED,
                container_type=config.container_type,
                created_at=datetime.utcnow(),
                ports=config.ports.copy(),
                environment=config.environment.copy(),
                volumes=config.volumes.copy(),
                networks=config.networks.copy(),
                labels=config.labels.copy()
            )
            
            self.containers[container_id] = container
            
            logger.info(f"Container criado: {config.name} ({container_id})")
            return container
            
        except Exception as e:
            logger.error(f"Erro ao criar container {config.name}: {e}")
            raise
    
    async def start_container(self, container_id: str) -> bool:
        """
        Inicia um container.
        
        Args:
            container_id: ID do container
            
        Returns:
            True se iniciado com sucesso, False caso contrário
        """
        try:
            container = self.containers.get(container_id)
            if not container:
                raise ValueError(f"Container {container_id} não encontrado")
            
            # Simular início do container
            container.status = ContainerStatus.RUNNING
            container.last_health_check = datetime.utcnow()
            
            logger.info(f"Container iniciado: {container.name} ({container_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar container {container_id}: {e}")
            return False
    
    async def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        """
        Para um container.
        
        Args:
            container_id: ID do container
            timeout: Timeout em segundos
            
        Returns:
            True se parado com sucesso, False caso contrário
        """
        try:
            container = self.containers.get(container_id)
            if not container:
                raise ValueError(f"Container {container_id} não encontrado")
            
            # Simular parada do container
            container.status = ContainerStatus.STOPPED
            
            logger.info(f"Container parado: {container.name} ({container_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar container {container_id}: {e}")
            return False
    
    async def restart_container(self, container_id: str) -> bool:
        """
        Reinicia um container.
        
        Args:
            container_id: ID do container
            
        Returns:
            True se reiniciado com sucesso, False caso contrário
        """
        try:
            container = self.containers.get(container_id)
            if not container:
                raise ValueError(f"Container {container_id} não encontrado")
            
            # Simular reinício
            container.status = ContainerStatus.RESTARTING
            container.restart_count += 1
            
            # Aguardar um pouco
            await asyncio.sleep(0.1)
            
            container.status = ContainerStatus.RUNNING
            container.last_health_check = datetime.utcnow()
            
            logger.info(f"Container reiniciado: {container.name} ({container_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reiniciar container {container_id}: {e}")
            return False
    
    async def remove_container(self, container_id: str, force: bool = False) -> bool:
        """
        Remove um container.
        
        Args:
            container_id: ID do container
            force: Forçar remoção mesmo se estiver rodando
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            container = self.containers.get(container_id)
            if not container:
                raise ValueError(f"Container {container_id} não encontrado")
            
            if container.is_running() and not force:
                raise ValueError(f"Container {container_id} está rodando. Use force=True para forçar remoção.")
            
            # Simular remoção
            del self.containers[container_id]
            
            logger.info(f"Container removido: {container.name} ({container_id})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover container {container_id}: {e}")
            return False
    
    async def get_container_status(self, container_id: str) -> Optional[ContainerStatus]:
        """
        Obtém status de um container.
        
        Args:
            container_id: ID do container
            
        Returns:
            Status do container ou None se não encontrado
        """
        container = self.containers.get(container_id)
        return container.status if container else None
    
    async def get_container_logs(self, container_id: str, tail: int = 100) -> List[str]:
        """
        Obtém logs de um container.
        
        Args:
            container_id: ID do container
            tail: Número de linhas para retornar
            
        Returns:
            Lista de logs
        """
        try:
            container = self.containers.get(container_id)
            if not container:
                raise ValueError(f"Container {container_id} não encontrado")
            
            # Simular logs
            logs = [
                f"[{datetime.utcnow().isoformat()}] Container {container.name} started",
                f"[{datetime.utcnow().isoformat()}] Application initialized",
                f"[{datetime.utcnow().isoformat()}] Health check passed"
            ]
            
            return logs[-tail:] if tail > 0 else logs
            
        except Exception as e:
            logger.error(f"Erro ao obter logs do container {container_id}: {e}")
            return []
    
    async def execute_command(self, container_id: str, command: List[str]) -> Tuple[int, str, str]:
        """
        Executa comando em um container.
        
        Args:
            container_id: ID do container
            command: Comando a ser executado
            
        Returns:
            Tupla (exit_code, stdout, stderr)
        """
        try:
            container = self.containers.get(container_id)
            if not container:
                raise ValueError(f"Container {container_id} não encontrado")
            
            if not container.is_running():
                raise ValueError(f"Container {container_id} não está rodando")
            
            # Simular execução de comando
            command_str = " ".join(command)
            stdout = f"Command executed: {command_str}"
            stderr = ""
            exit_code = 0
            
            logger.info(f"Comando executado em {container.name}: {command_str}")
            return exit_code, stdout, stderr
            
        except Exception as e:
            logger.error(f"Erro ao executar comando no container {container_id}: {e}")
            return 1, "", str(e)
    
    async def update_container_metrics(self, container_id: str, 
                                     memory_usage: str = None,
                                     cpu_usage: float = None,
                                     network_io: str = None) -> None:
        """
        Atualiza métricas de um container.
        
        Args:
            container_id: ID do container
            memory_usage: Uso de memória
            cpu_usage: Uso de CPU
            network_io: I/O de rede
        """
        container = self.containers.get(container_id)
        if not container:
            return
        
        if memory_usage is not None:
            container.memory_usage = memory_usage
        if cpu_usage is not None:
            container.cpu_usage = cpu_usage
        if network_io is not None:
            container.network_io = network_io
    
    def get_containers(self, status: ContainerStatus = None, 
                      container_type: ContainerType = None) -> List[Container]:
        """
        Obtém lista de containers com filtros opcionais.
        
        Args:
            status: Filtrar por status
            container_type: Filtrar por tipo
            
        Returns:
            Lista de containers
        """
        containers = list(self.containers.values())
        
        if status:
            containers = [c for c in containers if c.status == status]
        
        if container_type:
            containers = [c for c in containers if c.container_type == container_type]
        
        return containers
    
    def get_container_by_name(self, name: str) -> Optional[Container]:
        """
        Obtém container por nome.
        
        Args:
            name: Nome do container
            
        Returns:
            Container ou None se não encontrado
        """
        for container in self.containers.values():
            if container.name == name:
                return container
        return None


class KubernetesManager:
    """Gerenciador de Kubernetes para sistemas enterprise."""
    
    def __init__(self, kubeconfig: str = None, context: str = None):
        """
        Inicializa o gerenciador de Kubernetes.
        
        Args:
            kubeconfig: Caminho para o arquivo kubeconfig
            context: Contexto do Kubernetes
        """
        self.kubeconfig = kubeconfig
        self.context = context
        self.namespaces: List[str] = []
        self.deployments: Dict[str, Dict[str, Any]] = {}
        self.services: Dict[str, Dict[str, Any]] = {}
        self.pods: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"KubernetesManager inicializado - Context: {context}")
    
    async def create_deployment(self, name: str, image: str, 
                               config: KubernetesConfig) -> bool:
        """
        Cria um deployment no Kubernetes.
        
        Args:
            name: Nome do deployment
            image: Imagem do container
            config: Configuração do Kubernetes
            
        Returns:
            True se criado com sucesso, False caso contrário
        """
        try:
            # Simular criação de deployment
            deployment = {
                "name": name,
                "namespace": config.namespace,
                "image": image,
                "replicas": config.replicas,
                "status": "created",
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.deployments[name] = deployment
            
            # Criar pods correspondentes
            for i in range(config.replicas):
                pod_name = f"{name}-{i}"
                pod = {
                    "name": pod_name,
                    "namespace": config.namespace,
                    "status": "running",
                    "created_at": datetime.utcnow().isoformat()
                }
                self.pods[pod_name] = pod
            
            logger.info(f"Deployment criado: {name} em {config.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar deployment {name}: {e}")
            return False
    
    async def create_service(self, name: str, deployment_name: str,
                           config: KubernetesConfig) -> bool:
        """
        Cria um service no Kubernetes.
        
        Args:
            name: Nome do service
            deployment_name: Nome do deployment
            config: Configuração do Kubernetes
            
        Returns:
            True se criado com sucesso, False caso contrário
        """
        try:
            # Simular criação de service
            service = {
                "name": name,
                "namespace": config.namespace,
                "type": config.service_type,
                "port": config.service_port,
                "target_port": config.target_port,
                "deployment": deployment_name,
                "status": "created",
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.services[name] = service
            
            logger.info(f"Service criado: {name} em {config.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar service {name}: {e}")
            return False
    
    async def scale_deployment(self, name: str, replicas: int) -> bool:
        """
        Escala um deployment.
        
        Args:
            name: Nome do deployment
            replicas: Número de réplicas
            
        Returns:
            True se escalado com sucesso, False caso contrário
        """
        try:
            deployment = self.deployments.get(name)
            if not deployment:
                raise ValueError(f"Deployment {name} não encontrado")
            
            old_replicas = deployment["replicas"]
            deployment["replicas"] = replicas
            
            # Ajustar pods
            if replicas > old_replicas:
                # Adicionar pods
                for i in range(old_replicas, replicas):
                    pod_name = f"{name}-{i}"
                    pod = {
                        "name": pod_name,
                        "namespace": deployment["namespace"],
                        "status": "running",
                        "created_at": datetime.utcnow().isoformat()
                    }
                    self.pods[pod_name] = pod
            elif replicas < old_replicas:
                # Remover pods
                for i in range(replicas, old_replicas):
                    pod_name = f"{name}-{i}"
                    if pod_name in self.pods:
                        del self.pods[pod_name]
            
            logger.info(f"Deployment escalado: {name} -> {replicas} réplicas")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao escalar deployment {name}: {e}")
            return False
    
    async def delete_deployment(self, name: str) -> bool:
        """
        Remove um deployment.
        
        Args:
            name: Nome do deployment
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            if name not in self.deployments:
                raise ValueError(f"Deployment {name} não encontrado")
            
            # Remover pods associados
            pods_to_remove = [pod_name for pod_name in self.pods.keys() if pod_name.startswith(name)]
            for pod_name in pods_to_remove:
                del self.pods[pod_name]
            
            # Remover deployment
            del self.deployments[name]
            
            logger.info(f"Deployment removido: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover deployment {name}: {e}")
            return False
    
    def get_deployments(self, namespace: str = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de deployments.
        
        Args:
            namespace: Filtrar por namespace
            
        Returns:
            Lista de deployments
        """
        deployments = list(self.deployments.values())
        
        if namespace:
            deployments = [d for d in deployments if d["namespace"] == namespace]
        
        return deployments
    
    def get_services(self, namespace: str = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de services.
        
        Args:
            namespace: Filtrar por namespace
            
        Returns:
            Lista de services
        """
        services = list(self.services.values())
        
        if namespace:
            services = [s for s in services if s["namespace"] == namespace]
        
        return services
    
    def get_pods(self, namespace: str = None, deployment: str = None) -> List[Dict[str, Any]]:
        """
        Obtém lista de pods.
        
        Args:
            namespace: Filtrar por namespace
            deployment: Filtrar por deployment
            
        Returns:
            Lista de pods
        """
        pods = list(self.pods.values())
        
        if namespace:
            pods = [p for p in pods if p["namespace"] == namespace]
        
        if deployment:
            pods = [p for p in pods if p["name"].startswith(deployment)]
        
        return pods


# Função de conveniência para criar container manager
def create_container_manager(docker_socket: str = "/var/run/docker.sock") -> ContainerManager:
    """
    Cria um gerenciador de containers com configurações padrão.
    
    Args:
        docker_socket: Caminho para o socket do Docker
        
    Returns:
        Instância configurada do ContainerManager
    """
    return ContainerManager(docker_socket)


# Função de conveniência para criar kubernetes manager
def create_kubernetes_manager(kubeconfig: str = None, context: str = None) -> KubernetesManager:
    """
    Cria um gerenciador de Kubernetes com configurações padrão.
    
    Args:
        kubeconfig: Caminho para o arquivo kubeconfig
        context: Contexto do Kubernetes
        
    Returns:
        Instância configurada do KubernetesManager
    """
    return KubernetesManager(kubeconfig, context) 