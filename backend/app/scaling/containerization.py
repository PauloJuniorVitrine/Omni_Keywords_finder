"""
Sistema de Containerização
Facilita deploy e escalabilidade através de containerização
"""

import asyncio
import time
import json
import yaml
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class ContainerStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"


class ContainerType(Enum):
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    DOCKER_COMPOSE = "docker_compose"


@dataclass
class ContainerConfig:
    name: str
    image: str
    ports: List[str]
    environment: Dict[str, str]
    volumes: List[str]
    command: Optional[str] = None
    working_dir: Optional[str] = None
    user: Optional[str] = None
    restart_policy: str = "unless-stopped"
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None
    health_check: Optional[str] = None
    networks: List[str] = None


@dataclass
class ContainerInfo:
    id: str
    name: str
    image: str
    status: ContainerStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    ports: List[str]
    environment: Dict[str, str]
    memory_usage: Optional[str] = None
    cpu_usage: Optional[float] = None
    network_usage: Optional[str] = None


@dataclass
class DeploymentConfig:
    name: str
    replicas: int
    containers: List[ContainerConfig]
    strategy: str = "RollingUpdate"
    min_available: int = 1
    max_unavailable: int = 1
    resources: Dict[str, Any] = None
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None


class ContainerManager:
    """
    Gerenciador de containers
    """
    
    def __init__(self, container_type: ContainerType = ContainerType.DOCKER):
        self.container_type = container_type
        self.containers: Dict[str, ContainerInfo] = {}
        self.deployments: Dict[str, DeploymentConfig] = {}
        self.is_running = False
    
    async def start(self):
        """Inicia o gerenciador de containers"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Container manager started")
    
    async def stop(self):
        """Para o gerenciador de containers"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Container manager stopped")
    
    async def create_container(self, config: ContainerConfig) -> Optional[str]:
        """Cria um container"""
        try:
            if self.container_type == ContainerType.DOCKER:
                return await self._create_docker_container(config)
            elif self.container_type == ContainerType.KUBERNETES:
                return await self._create_kubernetes_container(config)
            else:
                raise ValueError(f"Unsupported container type: {self.container_type}")
                
        except Exception as e:
            logger.error(f"Error creating container {config.name}: {e}")
            return None
    
    async def _create_docker_container(self, config: ContainerConfig) -> Optional[str]:
        """Cria container Docker"""
        try:
            # Construir comando docker run
            cmd = ["docker", "run", "-d"]
            
            # Nome do container
            cmd.extend(["--name", config.name])
            
            # Portas
            for port in config.ports:
                cmd.extend(["-p", port])
            
            # Variáveis de ambiente
            for key, value in config.environment.items():
                cmd.extend(["-e", f"{key}={value}"])
            
            # Volumes
            for volume in config.volumes:
                cmd.extend(["-v", volume])
            
            # Redes
            if config.networks:
                for network in config.networks:
                    cmd.extend(["--network", network])
            
            # Limites de recursos
            if config.memory_limit:
                cmd.extend(["--memory", config.memory_limit])
            
            if config.cpu_limit:
                cmd.extend(["--cpus", config.cpu_limit])
            
            # Política de restart
            cmd.extend(["--restart", config.restart_policy])
            
            # Imagem
            cmd.append(config.image)
            
            # Comando
            if config.command:
                cmd.extend(config.command.split())
            
            # Executar comando
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                container_id = stdout.decode().strip()
                
                # Criar ContainerInfo
                container_info = ContainerInfo(
                    id=container_id,
                    name=config.name,
                    image=config.image,
                    status=ContainerStatus.CREATED,
                    created_at=datetime.now(),
                    ports=config.ports,
                    environment=config.environment
                )
                
                self.containers[container_id] = container_info
                
                logger.info(f"Docker container created: {config.name} ({container_id})")
                return container_id
            else:
                logger.error(f"Docker container creation failed: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Docker container: {e}")
            return None
    
    async def _create_kubernetes_container(self, config: ContainerConfig) -> Optional[str]:
        """Cria container Kubernetes"""
        try:
            # Gerar manifesto YAML
            manifest = self._generate_kubernetes_manifest(config)
            
            # Salvar manifesto temporariamente
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                manifest_path = f.name
            
            try:
                # Aplicar manifesto
                cmd = ["kubectl", "apply", "-f", manifest_path]
                
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    logger.info(f"Kubernetes container created: {config.name}")
                    return config.name
                else:
                    logger.error(f"Kubernetes container creation failed: {stderr.decode()}")
                    return None
                    
            finally:
                # Limpar arquivo temporário
                os.unlink(manifest_path)
                
        except Exception as e:
            logger.error(f"Error creating Kubernetes container: {e}")
            return None
    
    def _generate_kubernetes_manifest(self, config: ContainerConfig) -> Dict[str, Any]:
        """Gera manifesto Kubernetes"""
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": config.name,
                "labels": {
                    "app": config.name
                }
            },
            "spec": {
                "containers": [{
                    "name": config.name,
                    "image": config.image,
                    "ports": [
                        {"containerPort": int(port.split(":")[1])}
                        for port in config.ports
                    ],
                    "env": [
                        {"name": key, "value": value}
                        for key, value in config.environment.items()
                    ],
                    "volumeMounts": [
                        {"name": f"volume-{i}", "mountPath": volume.split(":")[1]}
                        for i, volume in enumerate(config.volumes)
                    ],
                    "resources": {
                        "limits": {
                            "memory": config.memory_limit,
                            "cpu": config.cpu_limit
                        } if config.memory_limit or config.cpu_limit else {}
                    }
                }],
                "volumes": [
                    {"name": f"volume-{i}", "hostPath": {"path": volume.split(":")[0]}}
                    for i, volume in enumerate(config.volumes)
                ]
            }
        }
    
    async def start_container(self, container_id: str) -> bool:
        """Inicia um container"""
        try:
            if self.container_type == ContainerType.DOCKER:
                return await self._start_docker_container(container_id)
            elif self.container_type == ContainerType.KUBERNETES:
                return await self._start_kubernetes_container(container_id)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error starting container {container_id}: {e}")
            return False
    
    async def _start_docker_container(self, container_id: str) -> bool:
        """Inicia container Docker"""
        try:
            cmd = ["docker", "start", container_id]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                if container_id in self.containers:
                    self.containers[container_id].status = ContainerStatus.RUNNING
                    self.containers[container_id].started_at = datetime.now()
                
                logger.info(f"Docker container started: {container_id}")
                return True
            else:
                logger.error(f"Docker container start failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Docker container: {e}")
            return False
    
    async def _start_kubernetes_container(self, container_id: str) -> bool:
        """Inicia container Kubernetes"""
        try:
            cmd = ["kubectl", "scale", "deployment", container_id, "--replicas=1"]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"Kubernetes container started: {container_id}")
                return True
            else:
                logger.error(f"Kubernetes container start failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting Kubernetes container: {e}")
            return False
    
    async def stop_container(self, container_id: str) -> bool:
        """Para um container"""
        try:
            if self.container_type == ContainerType.DOCKER:
                return await self._stop_docker_container(container_id)
            elif self.container_type == ContainerType.KUBERNETES:
                return await self._stop_kubernetes_container(container_id)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error stopping container {container_id}: {e}")
            return False
    
    async def _stop_docker_container(self, container_id: str) -> bool:
        """Para container Docker"""
        try:
            cmd = ["docker", "stop", container_id]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                if container_id in self.containers:
                    self.containers[container_id].status = ContainerStatus.EXITED
                
                logger.info(f"Docker container stopped: {container_id}")
                return True
            else:
                logger.error(f"Docker container stop failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping Docker container: {e}")
            return False
    
    async def _stop_kubernetes_container(self, container_id: str) -> bool:
        """Para container Kubernetes"""
        try:
            cmd = ["kubectl", "scale", "deployment", container_id, "--replicas=0"]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"Kubernetes container stopped: {container_id}")
                return True
            else:
                logger.error(f"Kubernetes container stop failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping Kubernetes container: {e}")
            return False
    
    async def remove_container(self, container_id: str) -> bool:
        """Remove um container"""
        try:
            if self.container_type == ContainerType.DOCKER:
                return await self._remove_docker_container(container_id)
            elif self.container_type == ContainerType.KUBERNETES:
                return await self._remove_kubernetes_container(container_id)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error removing container {container_id}: {e}")
            return False
    
    async def _remove_docker_container(self, container_id: str) -> bool:
        """Remove container Docker"""
        try:
            cmd = ["docker", "rm", "-f", container_id]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                if container_id in self.containers:
                    del self.containers[container_id]
                
                logger.info(f"Docker container removed: {container_id}")
                return True
            else:
                logger.error(f"Docker container removal failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing Docker container: {e}")
            return False
    
    async def _remove_kubernetes_container(self, container_id: str) -> bool:
        """Remove container Kubernetes"""
        try:
            cmd = ["kubectl", "delete", "deployment", container_id]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info(f"Kubernetes container removed: {container_id}")
                return True
            else:
                logger.error(f"Kubernetes container removal failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing Kubernetes container: {e}")
            return False
    
    async def get_container_status(self, container_id: str) -> Optional[ContainerInfo]:
        """Obtém status de um container"""
        try:
            if self.container_type == ContainerType.DOCKER:
                return await self._get_docker_container_status(container_id)
            elif self.container_type == ContainerType.KUBERNETES:
                return await self._get_kubernetes_container_status(container_id)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting container status {container_id}: {e}")
            return None
    
    async def _get_docker_container_status(self, container_id: str) -> Optional[ContainerInfo]:
        """Obtém status de container Docker"""
        try:
            cmd = ["docker", "inspect", container_id]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                data = json.loads(stdout.decode())
                container_data = data[0]
                
                # Atualizar ContainerInfo
                if container_id in self.containers:
                    container_info = self.containers[container_id]
                    container_info.status = ContainerStatus(container_data['State']['Status'])
                    
                    if container_data['State']['Running']:
                        container_info.started_at = datetime.fromisoformat(
                            container_data['State']['StartedAt'].replace('Z', '+00:00')
                        )
                    
                    # Obter métricas de recursos
                    stats_cmd = ["docker", "stats", container_id, "--no-stream", "--format", "json"]
                    stats_result = await asyncio.create_subprocess_exec(
                        *stats_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stats_stdout, _ = await stats_result.communicate()
                    if stats_result.returncode == 0:
                        stats_data = json.loads(stats_stdout.decode())
                        container_info.memory_usage = stats_data.get('MemUsage', 'N/A')
                        container_info.cpu_usage = float(stats_data.get('CPUPerc', '0%').rstrip('%'))
                    
                    return container_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Docker container status: {e}")
            return None
    
    async def _get_kubernetes_container_status(self, container_id: str) -> Optional[ContainerInfo]:
        """Obtém status de container Kubernetes"""
        try:
            cmd = ["kubectl", "get", "pod", container_id, "-o", "json"]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                data = json.loads(stdout.decode())
                pod_status = data['status']['phase']
                
                # Mapear status do Kubernetes para ContainerStatus
                status_mapping = {
                    'Pending': ContainerStatus.CREATED,
                    'Running': ContainerStatus.RUNNING,
                    'Succeeded': ContainerStatus.EXITED,
                    'Failed': ContainerStatus.DEAD,
                    'Unknown': ContainerStatus.DEAD
                }
                
                container_status = status_mapping.get(pod_status, ContainerStatus.DEAD)
                
                # Criar ou atualizar ContainerInfo
                container_info = ContainerInfo(
                    id=container_id,
                    name=container_id,
                    image=data['spec']['containers'][0]['image'],
                    status=container_status,
                    created_at=datetime.fromisoformat(data['metadata']['creationTimestamp'].replace('Z', '+00:00')),
                    ports=[],
                    environment={}
                )
                
                self.containers[container_id] = container_info
                return container_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Kubernetes container status: {e}")
            return None
    
    async def list_containers(self) -> List[ContainerInfo]:
        """Lista todos os containers"""
        containers = []
        
        for container_id in list(self.containers.keys()):
            status = await self.get_container_status(container_id)
            if status:
                containers.append(status)
        
        return containers
    
    async def create_deployment(self, config: DeploymentConfig) -> bool:
        """Cria um deployment"""
        try:
            if self.container_type == ContainerType.KUBERNETES:
                return await self._create_kubernetes_deployment(config)
            else:
                # Para Docker, criar múltiplos containers
                return await self._create_docker_deployment(config)
                
        except Exception as e:
            logger.error(f"Error creating deployment {config.name}: {e}")
            return False
    
    async def _create_kubernetes_deployment(self, config: DeploymentConfig) -> bool:
        """Cria deployment Kubernetes"""
        try:
            manifest = self._generate_kubernetes_deployment_manifest(config)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f)
                manifest_path = f.name
            
            try:
                cmd = ["kubectl", "apply", "-f", manifest_path]
                
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    self.deployments[config.name] = config
                    logger.info(f"Kubernetes deployment created: {config.name}")
                    return True
                else:
                    logger.error(f"Kubernetes deployment creation failed: {stderr.decode()}")
                    return False
                    
            finally:
                os.unlink(manifest_path)
                
        except Exception as e:
            logger.error(f"Error creating Kubernetes deployment: {e}")
            return False
    
    async def _create_docker_deployment(self, config: DeploymentConfig) -> bool:
        """Cria deployment Docker (múltiplos containers)"""
        try:
            created_containers = []
            
            for i in range(config.replicas):
                for container_config in config.containers:
                    # Criar nome único para cada réplica
                    replica_name = f"{container_config.name}-{i+1}"
                    container_config.name = replica_name
                    
                    container_id = await self.create_container(container_config)
                    if container_id:
                        created_containers.append(container_id)
                        await self.start_container(container_id)
            
            if created_containers:
                self.deployments[config.name] = config
                logger.info(f"Docker deployment created: {config.name} with {len(created_containers)} containers")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating Docker deployment: {e}")
            return False
    
    def _generate_kubernetes_deployment_manifest(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Gera manifesto de deployment Kubernetes"""
        containers = []
        
        for container_config in config.containers:
            container = {
                "name": container_config.name,
                "image": container_config.image,
                "ports": [
                    {"containerPort": int(port.split(":")[1])}
                    for port in container_config.ports
                ],
                "env": [
                    {"name": key, "value": value}
                    for key, value in container_config.environment.items()
                ]
            }
            
            if container_config.memory_limit or container_config.cpu_limit:
                container["resources"] = {
                    "limits": {
                        "memory": container_config.memory_limit,
                        "cpu": container_config.cpu_limit
                    }
                }
            
            containers.append(container)
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.name,
                "labels": config.labels or {}
            },
            "spec": {
                "replicas": config.replicas,
                "strategy": {
                    "type": config.strategy,
                    "rollingUpdate": {
                        "maxUnavailable": config.max_unavailable,
                        "maxSurge": config.min_available
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": config.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": config.name
                        }
                    },
                    "spec": {
                        "containers": containers
                    }
                }
            }
        }


# Funções utilitárias
def create_container_manager(container_type: ContainerType = ContainerType.DOCKER) -> ContainerManager:
    """Cria gerenciador de containers"""
    return ContainerManager(container_type)


def create_container_config(name: str, image: str, ports: List[str] = None,
                          environment: Dict[str, str] = None,
                          volumes: List[str] = None) -> ContainerConfig:
    """Cria configuração de container"""
    return ContainerConfig(
        name=name,
        image=image,
        ports=ports or [],
        environment=environment or {},
        volumes=volumes or []
    )


def create_deployment_config(name: str, replicas: int,
                           containers: List[ContainerConfig]) -> DeploymentConfig:
    """Cria configuração de deployment"""
    return DeploymentConfig(
        name=name,
        replicas=replicas,
        containers=containers
    )


# Instância global
container_manager = ContainerManager()


# Decorator para containerização
def containerized(image: str, ports: List[str] = None, environment: Dict[str, str] = None):
    """Decorator para containerização"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Criar configuração do container
            config = create_container_config(
                name=func.__name__,
                image=image,
                ports=ports or [],
                environment=environment or {}
            )
            
            # Criar e iniciar container
            container_id = await container_manager.create_container(config)
            if container_id:
                await container_manager.start_container(container_id)
            
            # Executar função
            result = await func(*args, **kwargs)
            
            return result
        
        return wrapper
    return decorator 