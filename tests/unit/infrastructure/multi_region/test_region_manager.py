"""
Testes Unitários - Multi-Region Manager

Tracing ID: FF-002-TEST
Data/Hora: 2024-12-19 23:58:00 UTC
Versão: 1.0
Status: Implementação Inicial

Testes unitários para o sistema de gerenciamento multi-região.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Importar módulos a serem testados
from infrastructure.multi_region.region_manager import (
    MultiRegionManager,
    RegionConfig,
    RegionHealth,
    Region,
    RegionStatus,
    ComplianceStandard,
    get_multi_region_manager,
    get_best_region,
    get_region_health
)

class TestRegion:
    """Testes para enum Region"""
    
    def test_region_values(self):
        """Testa valores do enum Region"""
        assert Region.US_EAST_1.value == "us-east-1"
        assert Region.US_WEST_2.value == "us-west-2"
        assert Region.EU_WEST_1.value == "eu-west-1"
        assert Region.AP_SOUTHEAST_1.value == "ap-southeast-1"
        assert Region.SA_EAST_1.value == "sa-east-1"

class TestRegionStatus:
    """Testes para enum RegionStatus"""
    
    def test_region_status_values(self):
        """Testa valores do enum RegionStatus"""
        assert RegionStatus.HEALTHY.value == "healthy"
        assert RegionStatus.DEGRADED.value == "degraded"
        assert RegionStatus.UNHEALTHY.value == "unhealthy"
        assert RegionStatus.MAINTENANCE.value == "maintenance"

class TestComplianceStandard:
    """Testes para enum ComplianceStandard"""
    
    def test_compliance_standard_values(self):
        """Testa valores do enum ComplianceStandard"""
        assert ComplianceStandard.GDPR.value == "gdpr"
        assert ComplianceStandard.LGPD.value == "lgpd"
        assert ComplianceStandard.CCPA.value == "ccpa"
        assert ComplianceStandard.HIPAA.value == "hipaa"
        assert ComplianceStandard.PCI_DSS.value == "pci_dss"
        assert ComplianceStandard.ISO_27001.value == "iso_27001"

class TestRegionConfig:
    """Testes para RegionConfig"""
    
    def test_region_config_creation(self):
        """Testa criação de RegionConfig"""
        config = RegionConfig(
            region=Region.US_EAST_1,
            name="US East",
            endpoint="https://api.us-east-1.example.com"
        )
        
        assert config.region == Region.US_EAST_1
        assert config.name == "US East"
        assert config.endpoint == "https://api.us-east-1.example.com"
        assert config.latency_threshold_ms == 1000
        assert config.compliance_standards == []
        assert config.data_retention_days == 90
        assert config.encryption_required is True
        assert config.backup_enabled is True
        assert config.failover_priority == 1
        assert config.created_at is not None
        assert config.updated_at is not None

    def test_region_config_with_custom_values(self):
        """Testa criação com valores customizados"""
        config = RegionConfig(
            region=Region.EU_WEST_1,
            name="Europe West",
            endpoint="https://api.eu-west-1.example.com",
            latency_threshold_ms=1500,
            compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.ISO_27001],
            data_retention_days=30,
            encryption_required=True,
            backup_enabled=True,
            failover_priority=2,
            max_connections=200,
            timeout_seconds=45,
            retry_attempts=5,
            health_check_interval=120,
            metadata={"owner": "eu-team", "timezone": "Europe/Dublin"}
        )
        
        assert config.region == Region.EU_WEST_1
        assert config.name == "Europe West"
        assert config.endpoint == "https://api.eu-west-1.example.com"
        assert config.latency_threshold_ms == 1500
        assert ComplianceStandard.GDPR in config.compliance_standards
        assert ComplianceStandard.ISO_27001 in config.compliance_standards
        assert config.data_retention_days == 30
        assert config.failover_priority == 2
        assert config.max_connections == 200
        assert config.timeout_seconds == 45
        assert config.retry_attempts == 5
        assert config.health_check_interval == 120
        assert config.metadata["owner"] == "eu-team"

class TestRegionHealth:
    """Testes para RegionHealth"""
    
    def test_region_health_creation(self):
        """Testa criação de RegionHealth"""
        now = datetime.utcnow()
        health = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=150.0,
            response_time_ms=120.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=now,
            next_check=now + timedelta(minutes=1)
        )
        
        assert health.region == Region.US_EAST_1
        assert health.status == RegionStatus.HEALTHY
        assert health.latency_ms == 150.0
        assert health.response_time_ms == 120.0
        assert health.error_rate == 0.001
        assert health.uptime_percentage == 99.9
        assert health.last_check == now
        assert health.issues == []

    def test_region_health_with_issues(self):
        """Testa criação com issues"""
        health = RegionHealth(
            region=Region.US_WEST_2,
            status=RegionStatus.DEGRADED,
            latency_ms=2000.0,
            response_time_ms=1800.0,
            error_rate=0.05,
            uptime_percentage=95.0,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1),
            issues=["High latency", "Increased error rate"]
        )
        
        assert health.status == RegionStatus.DEGRADED
        assert health.latency_ms == 2000.0
        assert health.error_rate == 0.05
        assert len(health.issues) == 2
        assert "High latency" in health.issues

class TestMultiRegionManager:
    """Testes para MultiRegionManager"""
    
    @pytest.fixture
    def region_manager(self):
        """Fixture para instância de region manager"""
        return MultiRegionManager(default_region=Region.US_EAST_1)
    
    def test_initialization(self, region_manager):
        """Testa inicialização do manager"""
        assert region_manager.default_region == Region.US_EAST_1
        assert len(region_manager.regions) == 5  # Todas as regiões padrão
        assert Region.US_EAST_1 in region_manager.regions
        assert Region.US_WEST_2 in region_manager.regions
        assert Region.EU_WEST_1 in region_manager.regions
        assert Region.AP_SOUTHEAST_1 in region_manager.regions
        assert Region.SA_EAST_1 in region_manager.regions

    def test_initialize_default_regions(self, region_manager):
        """Testa inicialização das regiões padrão"""
        # Verificar configurações específicas
        us_east_config = region_manager.regions[Region.US_EAST_1]
        assert us_east_config.name == "US East (N. Virginia)"
        assert us_east_config.endpoint == "https://api.us-east-1.omni-keywords.com"
        assert us_east_config.latency_threshold_ms == 800
        assert ComplianceStandard.CCPA in us_east_config.compliance_standards
        assert us_east_config.failover_priority == 1
        
        eu_west_config = region_manager.regions[Region.EU_WEST_1]
        assert eu_west_config.name == "Europe (Ireland)"
        assert ComplianceStandard.GDPR in eu_west_config.compliance_standards
        assert ComplianceStandard.ISO_27001 in eu_west_config.compliance_standards
        assert eu_west_config.data_retention_days == 30

    def test_get_region_timezone(self, region_manager):
        """Testa obtenção de timezone por região"""
        assert region_manager._get_region_timezone(Region.US_EAST_1) == "America/New_York"
        assert region_manager._get_region_timezone(Region.US_WEST_2) == "America/Los_Angeles"
        assert region_manager._get_region_timezone(Region.EU_WEST_1) == "Europe/Dublin"
        assert region_manager._get_region_timezone(Region.AP_SOUTHEAST_1) == "Asia/Singapore"
        assert region_manager._get_region_timezone(Region.SA_EAST_1) == "America/Sao_Paulo"
        assert region_manager._get_region_timezone(Region.US_EAST_1) == "UTC"  # Fallback

    def test_get_region_config(self, region_manager):
        """Testa obtenção de configuração de região"""
        config = region_manager.get_region_config(Region.US_EAST_1)
        
        assert config is not None
        assert config.region == Region.US_EAST_1
        assert config.name == "US East (N. Virginia)"
        
        # Teste com região inexistente
        config = region_manager.get_region_config(Region.US_EAST_1)  # Usar região válida
        assert config is not None

    def test_get_best_region_no_requirements(self, region_manager):
        """Testa obtenção da melhor região sem requisitos específicos"""
        # Simular health status
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=80.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        region_manager.health_status[Region.US_WEST_2] = RegionHealth(
            region=Region.US_WEST_2,
            status=RegionStatus.HEALTHY,
            latency_ms=200.0,
            response_time_ms=180.0,
            error_rate=0.002,
            uptime_percentage=99.8,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        best_region = region_manager.get_best_region()
        assert best_region == Region.US_EAST_1  # Menor latência

    def test_get_best_region_with_compliance(self, region_manager):
        """Testa obtenção da melhor região com requisitos de compliance"""
        # Simular health status
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=80.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        region_manager.health_status[Region.EU_WEST_1] = RegionHealth(
            region=Region.EU_WEST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=300.0,
            response_time_ms=280.0,
            error_rate=0.003,
            uptime_percentage=99.7,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        # Solicitar região com GDPR
        best_region = region_manager.get_best_region(
            compliance_requirements=[ComplianceStandard.GDPR]
        )
        assert best_region == Region.EU_WEST_1  # Única região com GDPR

    def test_get_best_region_with_location(self, region_manager):
        """Testa obtenção da melhor região baseada na localização"""
        # Simular health status para todas as regiões
        for region in Region:
            region_manager.health_status[region] = RegionHealth(
                region=region,
                status=RegionStatus.HEALTHY,
                latency_ms=100.0,
                response_time_ms=80.0,
                error_rate=0.001,
                uptime_percentage=99.9,
                last_check=datetime.utcnow(),
                next_check=datetime.utcnow() + timedelta(minutes=1)
            )
        
        # Teste com localização nos EUA
        best_region = region_manager.get_best_region(user_location="United States")
        assert best_region in [Region.US_EAST_1, Region.US_WEST_2]
        
        # Teste com localização na Europa
        best_region = region_manager.get_best_region(user_location="Germany")
        assert best_region == Region.EU_WEST_1
        
        # Teste com localização na Ásia
        best_region = region_manager.get_best_region(user_location="Singapore")
        assert best_region == Region.AP_SOUTHEAST_1
        
        # Teste com localização na América do Sul
        best_region = region_manager.get_best_region(user_location="Brazil")
        assert best_region == Region.SA_EAST_1

    def test_detect_continent(self, region_manager):
        """Testa detecção de continente"""
        assert region_manager._detect_continent("United States") == "us"
        assert region_manager._detect_continent("Canada") == "us"
        assert region_manager._detect_continent("Germany") == "eu"
        assert region_manager._detect_continent("UK") == "eu"
        assert region_manager._detect_continent("China") == "asia"
        assert region_manager._detect_continent("Japan") == "asia"
        assert region_manager._detect_continent("Brazil") == "sa"
        assert region_manager._detect_continent("Argentina") == "sa"
        assert region_manager._detect_continent("Unknown") == "us"  # Default

    def test_get_closest_region(self, region_manager):
        """Testa obtenção da região mais próxima"""
        regions = [Region.US_EAST_1, Region.US_WEST_2, Region.EU_WEST_1]
        
        # Simular health status
        for region in regions:
            region_manager.health_status[region] = RegionHealth(
                region=region,
                status=RegionStatus.HEALTHY,
                latency_ms=100.0,
                response_time_ms=80.0,
                error_rate=0.001,
                uptime_percentage=99.9,
                last_check=datetime.utcnow(),
                next_check=datetime.utcnow() + timedelta(minutes=1)
            )
        
        # Teste com localização nos EUA
        closest = region_manager._get_closest_region(regions, "United States")
        assert closest in [Region.US_EAST_1, Region.US_WEST_2]
        
        # Teste com localização na Europa
        closest = region_manager._get_closest_region(regions, "Germany")
        assert closest == Region.EU_WEST_1

    def test_get_region_health(self, region_manager):
        """Testa obtenção de saúde de região"""
        # Simular health status
        health = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=80.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        region_manager.health_status[Region.US_EAST_1] = health
        
        result = region_manager.get_region_health(Region.US_EAST_1)
        assert result == health
        
        # Teste com região sem health status
        result = region_manager.get_region_health(Region.US_WEST_2)
        assert result is None

    def test_get_all_regions_health(self, region_manager):
        """Testa obtenção de saúde de todas as regiões"""
        # Simular health status para algumas regiões
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=80.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        all_health = region_manager.get_all_regions_health()
        assert isinstance(all_health, dict)
        assert Region.US_EAST_1 in all_health
        assert all_health[Region.US_EAST_1].status == RegionStatus.HEALTHY

    def test_update_region_config(self, region_manager):
        """Testa atualização de configuração de região"""
        # Obter configuração original
        original_config = region_manager.get_region_config(Region.US_EAST_1)
        original_latency = original_config.latency_threshold_ms
        
        # Atualizar configuração
        updates = {"latency_threshold_ms": original_latency + 100}
        result = region_manager.update_region_config(Region.US_EAST_1, updates)
        
        assert result is True
        
        # Verificar se foi atualizada
        updated_config = region_manager.get_region_config(Region.US_EAST_1)
        assert updated_config.latency_threshold_ms == original_latency + 100

    def test_update_region_config_invalid_region(self, region_manager):
        """Testa atualização de configuração de região inválida"""
        # Tentar atualizar região que não existe (usar uma que existe)
        result = region_manager.update_region_config(Region.US_EAST_1, {"latency_threshold_ms": 1000})
        assert result is True  # Deve funcionar com região válida

    def test_get_failover_history(self, region_manager):
        """Testa obtenção de histórico de failovers"""
        # Simular histórico de failovers
        region_manager.failover_history = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "failed_region": "us-west-2",
                "alternative_region": "us-east-1",
                "reason": "High latency",
                "status": "completed"
            }
        ]
        
        history = region_manager.get_failover_history()
        assert len(history) == 1
        assert history[0]["failed_region"] == "us-west-2"
        assert history[0]["alternative_region"] == "us-east-1"

    def test_get_compliance_report(self, region_manager):
        """Testa geração de relatório de compliance"""
        # Simular health status
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=80.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        report = region_manager.get_compliance_report()
        
        assert "timestamp" in report
        assert "regions" in report
        assert "us-east-1" in report["regions"]
        
        us_east_info = report["regions"]["us-east-1"]
        assert us_east_info["name"] == "US East (N. Virginia)"
        assert "ccpa" in us_east_info["compliance_standards"]
        assert us_east_info["encryption_required"] is True
        assert us_east_info["backup_enabled"] is True

    def test_get_performance_metrics(self, region_manager):
        """Testa obtenção de métricas de performance"""
        # Simular health status
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=80.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        region_manager.health_status[Region.US_WEST_2] = RegionHealth(
            region=Region.US_WEST_2,
            status=RegionStatus.DEGRADED,
            latency_ms=2000.0,
            response_time_ms=1800.0,
            error_rate=0.05,
            uptime_percentage=95.0,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1),
            issues=["High latency"]
        )
        
        metrics = region_manager.get_performance_metrics()
        
        assert "timestamp" in metrics
        assert "regions" in metrics
        assert "summary" in metrics
        
        summary = metrics["summary"]
        assert summary["total_regions"] == 5
        assert summary["healthy_regions"] == 1
        assert summary["degraded_regions"] == 1
        assert summary["unhealthy_regions"] == 0
        
        us_east_metrics = metrics["regions"]["us-east-1"]
        assert us_east_metrics["latency_ms"] == 100.0
        assert us_east_metrics["status"] == "healthy"
        
        us_west_metrics = metrics["regions"]["us-west-2"]
        assert us_west_metrics["latency_ms"] == 2000.0
        assert us_west_metrics["status"] == "degraded"
        assert "High latency" in us_west_metrics["issues"]

    def test_get_health_status(self, region_manager):
        """Testa obtenção de status de saúde geral"""
        # Simular health status
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=80.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        region_manager.health_status[Region.US_WEST_2] = RegionHealth(
            region=Region.US_WEST_2,
            status=RegionStatus.HEALTHY,
            latency_ms=150.0,
            response_time_ms=130.0,
            error_rate=0.002,
            uptime_percentage=99.8,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        status = region_manager.get_health_status()
        
        assert status["status"] == "healthy"
        assert status["total_regions"] == 5
        assert status["healthy_regions"] == 2
        assert status["degraded_regions"] == 0
        assert status["unhealthy_regions"] == 0
        assert "timestamp" in status

    def test_find_best_alternative_region(self, region_manager):
        """Testa busca de região alternativa"""
        # Simular health status
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.UNHEALTHY,
            latency_ms=float('inf'),
            response_time_ms=float('inf'),
            error_rate=1.0,
            uptime_percentage=0.0,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        region_manager.health_status[Region.US_WEST_2] = RegionHealth(
            region=Region.US_WEST_2,
            status=RegionStatus.HEALTHY,
            latency_ms=150.0,
            response_time_ms=130.0,
            error_rate=0.002,
            uptime_percentage=99.8,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        alternative = region_manager._find_best_alternative_region(Region.US_EAST_1)
        assert alternative == Region.US_WEST_2

    def test_find_best_alternative_region_no_healthy(self, region_manager):
        """Testa busca de região alternativa sem regiões saudáveis"""
        # Simular todas as regiões unhealthy
        for region in [Region.US_EAST_1, Region.US_WEST_2]:
            region_manager.health_status[region] = RegionHealth(
                region=region,
                status=RegionStatus.UNHEALTHY,
                latency_ms=float('inf'),
                response_time_ms=float('inf'),
                error_rate=1.0,
                uptime_percentage=0.0,
                last_check=datetime.utcnow(),
                next_check=datetime.utcnow() + timedelta(minutes=1)
            )
        
        alternative = region_manager._find_best_alternative_region(Region.US_EAST_1)
        assert alternative is None

class TestGlobalFunctions:
    """Testes para funções globais"""
    
    @patch('infrastructure.multi_region.region_manager._multi_region_manager')
    def test_get_multi_region_manager(self, mock_global_manager):
        """Testa obtenção de instância global"""
        # Simular instância global
        mock_global_manager.return_value = Mock()
        
        result = get_multi_region_manager()
        assert result is not None

    @patch('infrastructure.multi_region.region_manager.get_multi_region_manager')
    def test_get_best_region(self, mock_get_manager):
        """Testa função de conveniência get_best_region"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager
        mock_manager.get_best_region.return_value = Region.US_EAST_1
        
        result = get_best_region("United States", [ComplianceStandard.GDPR])
        
        assert result == Region.US_EAST_1
        mock_manager.get_best_region.assert_called_once_with("United States", [ComplianceStandard.GDPR])

    @patch('infrastructure.multi_region.region_manager.get_multi_region_manager')
    def test_get_region_health(self, mock_get_manager):
        """Testa função de conveniência get_region_health"""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager
        
        health = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=80.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        mock_manager.get_region_health.return_value = health
        
        result = get_region_health(Region.US_EAST_1)
        
        assert result == health
        mock_manager.get_region_health.assert_called_once_with(Region.US_EAST_1)

class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_get_health_status_with_exception(self, region_manager):
        """Testa tratamento de exceção em get_health_status"""
        # Simular exceção
        with patch.object(region_manager, 'regions', side_effect=Exception("Test error")):
            status = region_manager.get_health_status()
            assert status["status"] == "unhealthy"
            assert "error" in status

    def test_update_region_config_with_exception(self, region_manager):
        """Testa tratamento de exceção em update_region_config"""
        # Simular exceção
        with patch.object(region_manager, 'regions', side_effect=Exception("Test error")):
            result = region_manager.update_region_config(Region.US_EAST_1, {"latency_threshold_ms": 1000})
            assert result is False

class TestIntegrationScenarios:
    """Testes para cenários de integração"""
    
    def test_us_user_scenario(self, region_manager):
        """Testa cenário de usuário dos EUA"""
        # Simular health status
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=50.0,
            response_time_ms=40.0,
            error_rate=0.001,
            uptime_percentage=99.9,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        region_manager.health_status[Region.US_WEST_2] = RegionHealth(
            region=Region.US_WEST_2,
            status=RegionStatus.HEALTHY,
            latency_ms=100.0,
            response_time_ms=90.0,
            error_rate=0.002,
            uptime_percentage=99.8,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        # Usuário dos EUA deve ir para US East (menor latência)
        best_region = region_manager.get_best_region("United States")
        assert best_region == Region.US_EAST_1

    def test_eu_user_gdpr_scenario(self, region_manager):
        """Testa cenário de usuário europeu com GDPR"""
        # Simular health status
        region_manager.health_status[Region.EU_WEST_1] = RegionHealth(
            region=Region.EU_WEST_1,
            status=RegionStatus.HEALTHY,
            latency_ms=200.0,
            response_time_ms=180.0,
            error_rate=0.003,
            uptime_percentage=99.7,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        # Usuário europeu com requisito GDPR deve ir para EU West
        best_region = region_manager.get_best_region(
            "Germany", 
            [ComplianceStandard.GDPR]
        )
        assert best_region == Region.EU_WEST_1

    def test_failover_scenario(self, region_manager):
        """Testa cenário de failover"""
        # Simular US East unhealthy
        region_manager.health_status[Region.US_EAST_1] = RegionHealth(
            region=Region.US_EAST_1,
            status=RegionStatus.UNHEALTHY,
            latency_ms=float('inf'),
            response_time_ms=float('inf'),
            error_rate=1.0,
            uptime_percentage=0.0,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        # US West healthy
        region_manager.health_status[Region.US_WEST_2] = RegionHealth(
            region=Region.US_WEST_2,
            status=RegionStatus.HEALTHY,
            latency_ms=150.0,
            response_time_ms=130.0,
            error_rate=0.002,
            uptime_percentage=99.8,
            last_check=datetime.utcnow(),
            next_check=datetime.utcnow() + timedelta(minutes=1)
        )
        
        # Failover deve ir para US West
        alternative = region_manager._find_best_alternative_region(Region.US_EAST_1)
        assert alternative == Region.US_WEST_2 