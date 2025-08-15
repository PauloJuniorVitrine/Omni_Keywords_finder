"""
Testes Unitários para Containerização
Sistema de Containers e Orquestração - Omni Keywords Finder

Prompt: Implementação de testes unitários para sistema de containerização
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.scaling.containerization import (
    ContainerManager, KubernetesManager, ContainerStatus, ContainerType,
    ContainerConfig, Container, KubernetesConfig,
    create_container_manager, create_kubernetes_manager
)


class TestContainerManager:
    """Testes para ContainerManager"""
    
    @pytest.fixture
    def sample_container_config(self):
        """Configuração de container de exemplo para testes"""
        return ContainerConfig(
            name="test-app",
            image="nginx:latest",
            container_type=ContainerType.APPLICATION,
            ports={"8080": "80"},
            environment={"NODE_ENV": "production"},
            volumes={"/host/data": "/app/data"},
            networks=["bridge"],
            memory_limit="512m",
            cpu_limit="0.5"
        )
    
    @pytest.fixture
    def container_manager(self):
        """Instância de ContainerManager para testes"""
        return ContainerManager()
    
    def test_container_manager_initialization(self):
        """Testa inicialização do ContainerManager"""
        manager = ContainerManager("/custom/docker.sock")
        
        assert manager.docker_socket == "/custom/docker.sock"
        assert len(manager.containers) == 0
        assert len(manager.networks) == 0
        assert len(manager.volumes) == 0
    
    @pytest.mark.asyncio
    async def test_create_container(self, container_manager, sample_container_config):
        """Testa criação de container"""
        container = await container_manager.create_container(sample_container_config)
        
        assert container is not None
        assert container.name == "test-app"
        assert container.image == "nginx:latest"
        assert container.container_type == ContainerType.APPLICATION
        assert container.status == ContainerStatus.CREATED
        assert container.ports == {"8080": "80"}
        assert container.environment == {"NODE_ENV": "production"}
        assert container.volumes == {"/host/data": "/app/data"}
        assert container.networks == ["bridge"]
        
        # Verificar se foi adicionado ao gerenciador
        assert len(container_manager.containers) == 1
        assert container.id in container_manager.containers
    
    @pytest.mark.asyncio
    async def test_create_container_invalid_config(self, container_manager):
        """Testa criação de container com configuração inválida"""
        invalid_config = ContainerConfig(
            name="",  # Nome vazio
            image="nginx:latest",
            container_type=ContainerType.APPLICATION
        )
        
        with pytest.raises(ValueError, match="Nome do container não pode ser vazio"):
            await container_manager.create_container(invalid_config)
    
    @pytest.mark.asyncio
    async def test_start_container(self, container_manager, sample_container_config):
        """Testa início de container"""
        # Criar container
        container = await container_manager.create_container(sample_container_config)
        
        # Iniciar container
        success = await container_manager.start_container(container.id)
        
        assert success is True
        assert container.status == ContainerStatus.RUNNING
        assert container.is_running() is True
    
    @pytest.mark.asyncio
    async def test_start_nonexistent_container(self, container_manager):
        """Testa início de container inexistente"""
        success = await container_manager.start_container("nonexistent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_stop_container(self, container_manager, sample_container_config):
        """Testa parada de container"""
        # Criar e iniciar container
        container = await container_manager.create_container(sample_container_config)
        await container_manager.start_container(container.id)
        
        # Parar container
        success = await container_manager.stop_container(container.id)
        
        assert success is True
        assert container.status == ContainerStatus.STOPPED
        assert container.is_running() is False
    
    @pytest.mark.asyncio
    async def test_restart_container(self, container_manager, sample_container_config):
        """Testa reinício de container"""
        # Criar e iniciar container
        container = await container_manager.create_container(sample_container_config)
        await container_manager.start_container(container.id)
        
        # Reiniciar container
        success = await container_manager.restart_container(container.id)
        
        assert success is True
        assert container.status == ContainerStatus.RUNNING
        assert container.restart_count == 1
        assert container.is_running() is True
    
    @pytest.mark.asyncio
    async def test_remove_container(self, container_manager, sample_container_config):
        """Testa remoção de container"""
        # Criar container
        container = await container_manager.create_container(sample_container_config)
        container_id = container.id
        
        # Remover container
        success = await container_manager.remove_container(container_id)
        
        assert success is True
        assert container_id not in container_manager.containers
    
    @pytest.mark.asyncio
    async def test_remove_running_container_without_force(self, container_manager, sample_container_config):
        """Testa remoção de container rodando sem force"""
        # Criar e iniciar container
        container = await container_manager.create_container(sample_container_config)
        await container_manager.start_container(container.id)
        
        # Tentar remover sem force
        success = await container_manager.remove_container(container.id, force=False)
        
        assert success is False
        assert container.id in container_manager.containers
    
    @pytest.mark.asyncio
    async def test_remove_running_container_with_force(self, container_manager, sample_container_config):
        """Testa remoção de container rodando com force"""
        # Criar e iniciar container
        container = await container_manager.create_container(sample_container_config)
        await container_manager.start_container(container.id)
        
        # Remover com force
        success = await container_manager.remove_container(container.id, force=True)
        
        assert success is True
        assert container.id not in container_manager.containers
    
    @pytest.mark.asyncio
    async def test_get_container_status(self, container_manager, sample_container_config):
        """Testa obtenção de status do container"""
        # Criar container
        container = await container_manager.create_container(sample_container_config)
        
        # Obter status
        status = await container_manager.get_container_status(container.id)
        
        assert status == ContainerStatus.CREATED
    
    @pytest.mark.asyncio
    async def test_get_container_logs(self, container_manager, sample_container_config):
        """Testa obtenção de logs do container"""
        # Criar container
        container = await container_manager.create_container(sample_container_config)
        
        # Obter logs
        logs = await container_manager.get_container_logs(container.id, tail=10)
        
        assert isinstance(logs, list)
        assert len(logs) > 0
        assert all(isinstance(log, str) for log in logs)
    
    @pytest.mark.asyncio
    async def test_execute_command(self, container_manager, sample_container_config):
        """Testa execução de comando no container"""
        # Criar e iniciar container
        container = await container_manager.create_container(sample_container_config)
        await container_manager.start_container(container.id)
        
        # Executar comando
        exit_code, stdout, stderr = await container_manager.execute_command(
            container.id, ["ls", "-la"]
        )
        
        assert exit_code == 0
        assert "Command executed: ls -la" in stdout
        assert stderr == ""
    
    @pytest.mark.asyncio
    async def test_execute_command_in_stopped_container(self, container_manager, sample_container_config):
        """Testa execução de comando em container parado"""
        # Criar container (não iniciar)
        container = await container_manager.create_container(sample_container_config)
        
        # Tentar executar comando
        exit_code, stdout, stderr = await container_manager.execute_command(
            container.id, ["ls", "-la"]
        )
        
        assert exit_code == 1
        assert "não está rodando" in stderr
    
    @pytest.mark.asyncio
    async def test_update_container_metrics(self, container_manager, sample_container_config):
        """Testa atualização de métricas do container"""
        # Criar container
        container = await container_manager.create_container(sample_container_config)
        
        # Atualizar métricas
        await container_manager.update_container_metrics(
            container.id,
            memory_usage="256m",
            cpu_usage=0.3,
            network_io="1.5MB"
        )
        
        assert container.memory_usage == "256m"
        assert container.cpu_usage == 0.3
        assert container.network_io == "1.5MB"
    
    def test_get_containers_no_filters(self, container_manager, sample_container_config):
        """Testa obtenção de containers sem filtros"""
        # Criar alguns containers
        asyncio.run(container_manager.create_container(sample_container_config))
        
        containers = container_manager.get_containers()
        assert len(containers) == 1
    
    def test_get_containers_with_status_filter(self, container_manager, sample_container_config):
        """Testa obtenção de containers com filtro de status"""
        # Criar container
        asyncio.run(container_manager.create_container(sample_container_config))
        
        # Filtrar por status
        containers = container_manager.get_containers(status=ContainerStatus.CREATED)
        assert len(containers) == 1
        
        containers = container_manager.get_containers(status=ContainerStatus.RUNNING)
        assert len(containers) == 0
    
    def test_get_containers_with_type_filter(self, container_manager):
        """Testa obtenção de containers com filtro de tipo"""
        # Criar containers de diferentes tipos
        app_config = ContainerConfig(
            name="app",
            image="nginx:latest",
            container_type=ContainerType.APPLICATION
        )
        db_config = ContainerConfig(
            name="db",
            image="postgres:latest",
            container_type=ContainerType.DATABASE
        )
        
        asyncio.run(container_manager.create_container(app_config))
        asyncio.run(container_manager.create_container(db_config))
        
        # Filtrar por tipo
        app_containers = container_manager.get_containers(container_type=ContainerType.APPLICATION)
        assert len(app_containers) == 1
        
        db_containers = container_manager.get_containers(container_type=ContainerType.DATABASE)
        assert len(db_containers) == 1
    
    def test_get_container_by_name(self, container_manager, sample_container_config):
        """Testa obtenção de container por nome"""
        # Criar container
        asyncio.run(container_manager.create_container(sample_container_config))
        
        # Buscar por nome
        container = container_manager.get_container_by_name("test-app")
        assert container is not None
        assert container.name == "test-app"
        
        # Buscar por nome inexistente
        container = container_manager.get_container_by_name("nonexistent")
        assert container is None


class TestKubernetesManager:
    """Testes para KubernetesManager"""
    
    @pytest.fixture
    def sample_k8s_config(self):
        """Configuração de Kubernetes de exemplo para testes"""
        return KubernetesConfig(
            namespace="test-namespace",
            replicas=3,
            service_type="ClusterIP",
            service_port=80,
            target_port=8080
        )
    
    @pytest.fixture
    def kubernetes_manager(self):
        """Instância de KubernetesManager para testes"""
        return KubernetesManager()
    
    def test_kubernetes_manager_initialization(self):
        """Testa inicialização do KubernetesManager"""
        manager = KubernetesManager("/path/to/kubeconfig", "test-context")
        
        assert manager.kubeconfig == "/path/to/kubeconfig"
        assert manager.context == "test-context"
        assert len(manager.namespaces) == 0
        assert len(manager.deployments) == 0
        assert len(manager.services) == 0
        assert len(manager.pods) == 0
    
    @pytest.mark.asyncio
    async def test_create_deployment(self, kubernetes_manager, sample_k8s_config):
        """Testa criação de deployment"""
        success = await kubernetes_manager.create_deployment(
            "test-deployment",
            "nginx:latest",
            sample_k8s_config
        )
        
        assert success is True
        assert "test-deployment" in kubernetes_manager.deployments
        
        deployment = kubernetes_manager.deployments["test-deployment"]
        assert deployment["name"] == "test-deployment"
        assert deployment["namespace"] == "test-namespace"
        assert deployment["image"] == "nginx:latest"
        assert deployment["replicas"] == 3
        
        # Verificar se os pods foram criados
        assert len(kubernetes_manager.pods) == 3
        for i in range(3):
            pod_name = f"test-deployment-{i}"
            assert pod_name in kubernetes_manager.pods
    
    @pytest.mark.asyncio
    async def test_create_service(self, kubernetes_manager, sample_k8s_config):
        """Testa criação de service"""
        # Criar deployment primeiro
        await kubernetes_manager.create_deployment("test-deployment", "nginx:latest", sample_k8s_config)
        
        # Criar service
        success = await kubernetes_manager.create_service(
            "test-service",
            "test-deployment",
            sample_k8s_config
        )
        
        assert success is True
        assert "test-service" in kubernetes_manager.services
        
        service = kubernetes_manager.services["test-service"]
        assert service["name"] == "test-service"
        assert service["namespace"] == "test-namespace"
        assert service["type"] == "ClusterIP"
        assert service["port"] == 80
        assert service["target_port"] == 8080
        assert service["deployment"] == "test-deployment"
    
    @pytest.mark.asyncio
    async def test_scale_deployment(self, kubernetes_manager, sample_k8s_config):
        """Testa escalonamento de deployment"""
        # Criar deployment
        await kubernetes_manager.create_deployment("test-deployment", "nginx:latest", sample_k8s_config)
        
        # Escalar para 5 réplicas
        success = await kubernetes_manager.scale_deployment("test-deployment", 5)
        
        assert success is True
        deployment = kubernetes_manager.deployments["test-deployment"]
        assert deployment["replicas"] == 5
        
        # Verificar se os pods foram adicionados
        assert len(kubernetes_manager.pods) == 5
    
    @pytest.mark.asyncio
    async def test_scale_deployment_down(self, kubernetes_manager, sample_k8s_config):
        """Testa redução de deployment"""
        # Criar deployment
        await kubernetes_manager.create_deployment("test-deployment", "nginx:latest", sample_k8s_config)
        
        # Escalar para 1 réplica
        success = await kubernetes_manager.scale_deployment("test-deployment", 1)
        
        assert success is True
        deployment = kubernetes_manager.deployments["test-deployment"]
        assert deployment["replicas"] == 1
        
        # Verificar se os pods foram removidos
        assert len(kubernetes_manager.pods) == 1
    
    @pytest.mark.asyncio
    async def test_scale_nonexistent_deployment(self, kubernetes_manager):
        """Testa escalonamento de deployment inexistente"""
        success = await kubernetes_manager.scale_deployment("nonexistent", 5)
        assert success is False
    
    @pytest.mark.asyncio
    async def test_delete_deployment(self, kubernetes_manager, sample_k8s_config):
        """Testa remoção de deployment"""
        # Criar deployment
        await kubernetes_manager.create_deployment("test-deployment", "nginx:latest", sample_k8s_config)
        
        # Remover deployment
        success = await kubernetes_manager.delete_deployment("test-deployment")
        
        assert success is True
        assert "test-deployment" not in kubernetes_manager.deployments
        assert len(kubernetes_manager.pods) == 0  # Pods também devem ser removidos
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_deployment(self, kubernetes_manager):
        """Testa remoção de deployment inexistente"""
        success = await kubernetes_manager.delete_deployment("nonexistent")
        assert success is False
    
    def test_get_deployments_no_filter(self, kubernetes_manager, sample_k8s_config):
        """Testa obtenção de deployments sem filtro"""
        # Criar alguns deployments
        asyncio.run(kubernetes_manager.create_deployment("deploy1", "nginx:latest", sample_k8s_config))
        asyncio.run(kubernetes_manager.create_deployment("deploy2", "postgres:latest", sample_k8s_config))
        
        deployments = kubernetes_manager.get_deployments()
        assert len(deployments) == 2
    
    def test_get_deployments_with_namespace_filter(self, kubernetes_manager, sample_k8s_config):
        """Testa obtenção de deployments com filtro de namespace"""
        # Criar deployments em diferentes namespaces
        config1 = KubernetesConfig(namespace="ns1", replicas=1)
        config2 = KubernetesConfig(namespace="ns2", replicas=1)
        
        asyncio.run(kubernetes_manager.create_deployment("deploy1", "nginx:latest", config1))
        asyncio.run(kubernetes_manager.create_deployment("deploy2", "postgres:latest", config2))
        
        # Filtrar por namespace
        deployments = kubernetes_manager.get_deployments(namespace="ns1")
        assert len(deployments) == 1
        assert deployments[0]["namespace"] == "ns1"
    
    def test_get_services(self, kubernetes_manager, sample_k8s_config):
        """Testa obtenção de services"""
        # Criar deployment e service
        asyncio.run(kubernetes_manager.create_deployment("test-deployment", "nginx:latest", sample_k8s_config))
        asyncio.run(kubernetes_manager.create_service("test-service", "test-deployment", sample_k8s_config))
        
        services = kubernetes_manager.get_services()
        assert len(services) == 1
        assert services[0]["name"] == "test-service"
    
    def test_get_pods(self, kubernetes_manager, sample_k8s_config):
        """Testa obtenção de pods"""
        # Criar deployment
        asyncio.run(kubernetes_manager.create_deployment("test-deployment", "nginx:latest", sample_k8s_config))
        
        pods = kubernetes_manager.get_pods()
        assert len(pods) == 3  # 3 réplicas
        
        # Filtrar por deployment
        pods = kubernetes_manager.get_pods(deployment="test-deployment")
        assert len(pods) == 3
        
        # Filtrar por namespace
        pods = kubernetes_manager.get_pods(namespace="test-namespace")
        assert len(pods) == 3


class TestContainerConfig:
    """Testes para ContainerConfig"""
    
    def test_container_config_initialization(self):
        """Testa inicialização de ContainerConfig"""
        config = ContainerConfig(
            name="test-app",
            image="nginx:latest",
            container_type=ContainerType.APPLICATION,
            ports={"8080": "80"},
            environment={"NODE_ENV": "production"},
            memory_limit="1g",
            cpu_limit="1.0"
        )
        
        assert config.name == "test-app"
        assert config.image == "nginx:latest"
        assert config.container_type == ContainerType.APPLICATION
        assert config.ports == {"8080": "80"}
        assert config.environment == {"NODE_ENV": "production"}
        assert config.memory_limit == "1g"
        assert config.cpu_limit == "1.0"
    
    def test_container_config_validation_name_empty(self):
        """Testa validação de nome vazio"""
        with pytest.raises(ValueError, match="Nome do container não pode ser vazio"):
            ContainerConfig(
                name="",
                image="nginx:latest",
                container_type=ContainerType.APPLICATION
            )
    
    def test_container_config_validation_image_empty(self):
        """Testa validação de imagem vazia"""
        with pytest.raises(ValueError, match="Imagem do container não pode ser vazia"):
            ContainerConfig(
                name="test-app",
                image="",
                container_type=ContainerType.APPLICATION
            )
    
    def test_container_config_validation_memory_limit_invalid(self):
        """Testa validação de memory limit inválido"""
        with pytest.raises(ValueError, match="Memory limit deve ser um valor válido"):
            ContainerConfig(
                name="test-app",
                image="nginx:latest",
                container_type=ContainerType.APPLICATION,
                memory_limit="invalid"
            )
    
    def test_container_config_validation_cpu_limit_invalid(self):
        """Testa validação de CPU limit inválido"""
        with pytest.raises(ValueError, match="CPU limit deve ser um valor válido"):
            ContainerConfig(
                name="test-app",
                image="nginx:latest",
                container_type=ContainerType.APPLICATION,
                cpu_limit="-1.0"
            )


class TestContainer:
    """Testes para Container"""
    
    def test_container_initialization(self):
        """Testa inicialização de Container"""
        container = Container(
            id="container123",
            name="test-app",
            image="nginx:latest",
            status=ContainerStatus.RUNNING,
            container_type=ContainerType.APPLICATION,
            created_at=datetime.utcnow(),
            ports={"8080": "80"},
            memory_usage="256m",
            cpu_usage=0.5,
            restart_count=2
        )
        
        assert container.id == "container123"
        assert container.name == "test-app"
        assert container.image == "nginx:latest"
        assert container.status == ContainerStatus.RUNNING
        assert container.container_type == ContainerType.APPLICATION
        assert container.ports == {"8080": "80"}
        assert container.memory_usage == "256m"
        assert container.cpu_usage == 0.5
        assert container.restart_count == 2
    
    def test_container_validation_id_empty(self):
        """Testa validação de ID vazio"""
        with pytest.raises(ValueError, match="ID do container não pode ser vazio"):
            Container(
                id="",
                name="test-app",
                image="nginx:latest",
                status=ContainerStatus.RUNNING,
                container_type=ContainerType.APPLICATION,
                created_at=datetime.utcnow()
            )
    
    def test_container_is_running(self):
        """Testa verificação se container está rodando"""
        running_container = Container(
            id="container123",
            name="test-app",
            image="nginx:latest",
            status=ContainerStatus.RUNNING,
            container_type=ContainerType.APPLICATION,
            created_at=datetime.utcnow()
        )
        
        stopped_container = Container(
            id="container456",
            name="test-app",
            image="nginx:latest",
            status=ContainerStatus.STOPPED,
            container_type=ContainerType.APPLICATION,
            created_at=datetime.utcnow()
        )
        
        assert running_container.is_running() is True
        assert stopped_container.is_running() is False
    
    def test_container_is_healthy(self):
        """Testa verificação se container está saudável"""
        healthy_container = Container(
            id="container123",
            name="test-app",
            image="nginx:latest",
            status=ContainerStatus.RUNNING,
            container_type=ContainerType.APPLICATION,
            created_at=datetime.utcnow(),
            health_status="healthy"
        )
        
        unhealthy_container = Container(
            id="container456",
            name="test-app",
            image="nginx:latest",
            status=ContainerStatus.RUNNING,
            container_type=ContainerType.APPLICATION,
            created_at=datetime.utcnow(),
            health_status="unhealthy"
        )
        
        assert healthy_container.is_healthy() is True
        assert unhealthy_container.is_healthy() is False
    
    def test_container_get_uptime(self):
        """Testa cálculo de tempo de atividade"""
        container = Container(
            id="container123",
            name="test-app",
            image="nginx:latest",
            status=ContainerStatus.RUNNING,
            container_type=ContainerType.APPLICATION,
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        uptime = container.get_uptime()
        assert isinstance(uptime, timedelta)
        assert uptime.total_seconds() >= 3600  # Pelo menos 1 hora


class TestKubernetesConfig:
    """Testes para KubernetesConfig"""
    
    def test_kubernetes_config_initialization(self):
        """Testa inicialização de KubernetesConfig"""
        config = KubernetesConfig(
            namespace="test-namespace",
            replicas=5,
            service_type="LoadBalancer",
            service_port=443,
            target_port=8443
        )
        
        assert config.namespace == "test-namespace"
        assert config.replicas == 5
        assert config.service_type == "LoadBalancer"
        assert config.service_port == 443
        assert config.target_port == 8443
    
    def test_kubernetes_config_validation_namespace_empty(self):
        """Testa validação de namespace vazio"""
        with pytest.raises(ValueError, match="Namespace não pode ser vazio"):
            KubernetesConfig(namespace="")
    
    def test_kubernetes_config_validation_replicas_invalid(self):
        """Testa validação de réplicas inválidas"""
        with pytest.raises(ValueError, match="Replicas deve ser pelo menos 1"):
            KubernetesConfig(replicas=0)
    
    def test_kubernetes_config_validation_service_port_invalid(self):
        """Testa validação de service port inválido"""
        with pytest.raises(ValueError, match="Service port deve estar entre 1 e 65535"):
            KubernetesConfig(service_port=0)
    
    def test_kubernetes_config_validation_target_port_invalid(self):
        """Testa validação de target port inválido"""
        with pytest.raises(ValueError, match="Target port deve estar entre 1 e 65535"):
            KubernetesConfig(target_port=70000)


class TestCreateFunctions:
    """Testes para funções de criação"""
    
    def test_create_container_manager(self):
        """Testa criação de ContainerManager"""
        manager = create_container_manager("/custom/socket")
        assert isinstance(manager, ContainerManager)
        assert manager.docker_socket == "/custom/socket"
    
    def test_create_kubernetes_manager(self):
        """Testa criação de KubernetesManager"""
        manager = create_kubernetes_manager("/path/to/kubeconfig", "test-context")
        assert isinstance(manager, KubernetesManager)
        assert manager.kubeconfig == "/path/to/kubeconfig"
        assert manager.context == "test-context"


class TestContainerizationIntegration:
    """Testes de integração para Containerização"""
    
    @pytest.mark.asyncio
    async def test_complete_container_lifecycle(self):
        """Testa ciclo completo de vida do container"""
        manager = create_container_manager()
        
        # Configuração do container
        config = ContainerConfig(
            name="integration-test",
            image="alpine:latest",
            container_type=ContainerType.APPLICATION,
            command=["sleep", "3600"]
        )
        
        # Criar container
        container = await manager.create_container(config)
        assert container.status == ContainerStatus.CREATED
        
        # Iniciar container
        success = await manager.start_container(container.id)
        assert success is True
        assert container.status == ContainerStatus.RUNNING
        
        # Executar comando
        exit_code, stdout, stderr = await manager.execute_command(container.id, ["echo", "hello"])
        assert exit_code == 0
        
        # Parar container
        success = await manager.stop_container(container.id)
        assert success is True
        assert container.status == ContainerStatus.STOPPED
        
        # Remover container
        success = await manager.remove_container(container.id)
        assert success is True
        assert container.id not in manager.containers
    
    @pytest.mark.asyncio
    async def test_kubernetes_deployment_lifecycle(self):
        """Testa ciclo completo de deployment no Kubernetes"""
        manager = create_kubernetes_manager()
        
        # Configuração
        config = KubernetesConfig(
            namespace="integration-test",
            replicas=2,
            service_type="ClusterIP"
        )
        
        # Criar deployment
        success = await manager.create_deployment("test-deployment", "nginx:latest", config)
        assert success is True
        
        # Criar service
        success = await manager.create_service("test-service", "test-deployment", config)
        assert success is True
        
        # Escalar deployment
        success = await manager.scale_deployment("test-deployment", 4)
        assert success is True
        
        # Verificar estado
        deployments = manager.get_deployments(namespace="integration-test")
        assert len(deployments) == 1
        assert deployments[0]["replicas"] == 4
        
        services = manager.get_services(namespace="integration-test")
        assert len(services) == 1
        
        pods = manager.get_pods(namespace="integration-test")
        assert len(pods) == 4
        
        # Remover deployment
        success = await manager.delete_deployment("test-deployment")
        assert success is True
        assert len(manager.get_deployments()) == 0


if __name__ == "__main__":
    pytest.main([__file__]) 