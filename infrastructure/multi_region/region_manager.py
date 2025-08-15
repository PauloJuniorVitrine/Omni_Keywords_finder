"""
Multi-Region Manager - Omni Keywords Finder

Tracing ID: FF-002
Data/Hora: 2024-12-19 23:55:00 UTC
Versão: 1.0
Status: Implementação Inicial

Sistema de gerenciamento multi-região para integrações externas,
permitindo configuração por região, failover automático, compliance local e latência otimizada.
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
import threading

# Configuração de logging
logger = logging.getLogger(__name__)

class Region(Enum):
    """Regiões suportadas"""
    US_EAST_1 = "us-east-1"
    US_WEST_2 = "us-west-2"
    EU_WEST_1 = "eu-west-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"
    SA_EAST_1 = "sa-east-1"

class ComplianceStandard(Enum):
    """Padrões de compliance suportados"""
    GDPR = "gdpr"
    LGPD = "lgpd"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"

class RegionStatus(Enum):
    """Status de região"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

@dataclass
class RegionConfig:
    """Configuração de região"""
    region: Region
    name: str
    endpoint: str
    latency_threshold_ms: int = 1000
    compliance_standards: List[ComplianceStandard] = None
    data_retention_days: int = 90
    encryption_required: bool = True
    backup_enabled: bool = True
    monitoring_enabled: bool = True
    failover_priority: int = 1
    max_connections: int = 100
    timeout_seconds: int = 30
    retry_attempts: int = 3
    health_check_interval: int = 60
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.compliance_standards is None:
            self.compliance_standards = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class RegionHealth:
    """Status de saúde de região"""
    region: Region
    status: RegionStatus
    latency_ms: float
    response_time_ms: float
    error_rate: float
    uptime_percentage: float
    last_check: datetime
    next_check: datetime
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []

class MultiRegionManager:
    """
    Gerenciador de múltiplas regiões para integrações externas
    """
    
    def __init__(self, default_region: Region = Region.US_EAST_1):
        """
        Inicializa o gerenciador multi-região
        
        Args:
            default_region: Região padrão
        """
        self.default_region = default_region
        self.regions: Dict[Region, RegionConfig] = {}
        self.health_status: Dict[Region, RegionHealth] = {}
        self.failover_history: List[Dict[str, Any]] = []
        self.lock = threading.RLock()
        
        # Configurações padrão por região
        self._initialize_default_regions()
        
        # Iniciar monitoramento de saúde
        self._start_health_monitoring()
        
        logger.info(f"[FF-002] Multi-Region Manager inicializado - Região padrão: {default_region.value}")

    def _initialize_default_regions(self):
        """Inicializa configurações padrão por região"""
        default_configs = {
            Region.US_EAST_1: {
                "name": "US East (N. Virginia)",
                "endpoint": "https://api.us-east-1.omni-keywords.com",
                "latency_threshold_ms": 800,
                "compliance_standards": [ComplianceStandard.CCPA],
                "data_retention_days": 90,
                "encryption_required": True,
                "backup_enabled": True,
                "failover_priority": 1
            },
            Region.US_WEST_2: {
                "name": "US West (Oregon)",
                "endpoint": "https://api.us-west-2.omni-keywords.com",
                "latency_threshold_ms": 1200,
                "compliance_standards": [ComplianceStandard.CCPA],
                "data_retention_days": 90,
                "encryption_required": True,
                "backup_enabled": True,
                "failover_priority": 2
            },
            Region.EU_WEST_1: {
                "name": "Europe (Ireland)",
                "endpoint": "https://api.eu-west-1.omni-keywords.com",
                "latency_threshold_ms": 1500,
                "compliance_standards": [ComplianceStandard.GDPR, ComplianceStandard.ISO_27001],
                "data_retention_days": 30,
                "encryption_required": True,
                "backup_enabled": True,
                "failover_priority": 3
            },
            Region.AP_SOUTHEAST_1: {
                "name": "Asia Pacific (Singapore)",
                "endpoint": "https://api.ap-southeast-1.omni-keywords.com",
                "latency_threshold_ms": 2000,
                "compliance_standards": [],
                "data_retention_days": 90,
                "encryption_required": True,
                "backup_enabled": True,
                "failover_priority": 4
            },
            Region.SA_EAST_1: {
                "name": "South America (São Paulo)",
                "endpoint": "https://api.sa-east-1.omni-keywords.com",
                "latency_threshold_ms": 1800,
                "compliance_standards": [ComplianceStandard.LGPD],
                "data_retention_days": 60,
                "encryption_required": True,
                "backup_enabled": True,
                "failover_priority": 5
            }
        }
        
        for region, config in default_configs.items():
            self.regions[region] = RegionConfig(
                region=region,
                **config,
                metadata={
                    "description": f"Região {config['name']}",
                    "owner": "infrastructure-team",
                    "timezone": self._get_region_timezone(region)
                }
            )

    def _get_region_timezone(self, region: Region) -> str:
        """Retorna timezone da região"""
        timezones = {
            Region.US_EAST_1: "America/New_York",
            Region.US_WEST_2: "America/Los_Angeles",
            Region.EU_WEST_1: "Europe/Dublin",
            Region.AP_SOUTHEAST_1: "Asia/Singapore",
            Region.SA_EAST_1: "America/Sao_Paulo"
        }
        return timezones.get(region, "UTC")

    def _start_health_monitoring(self):
        """Inicia monitoramento de saúde das regiões"""
        def monitor_health():
            while True:
                try:
                    self._check_all_regions_health()
                    time.sleep(60)  # Verificar a cada minuto
                except Exception as e:
                    logger.error(f"[FF-002] Erro no monitoramento de saúde: {e}")
                    time.sleep(30)
        
        # Iniciar thread de monitoramento
        monitor_thread = threading.Thread(target=monitor_health, daemon=True)
        monitor_thread.start()
        logger.info("[FF-002] Monitoramento de saúde iniciado")

    def _check_all_regions_health(self):
        """Verifica saúde de todas as regiões"""
        with self.lock:
            for region in self.regions:
                try:
                    health = self._check_region_health(region)
                    self.health_status[region] = health
                    
                    # Verificar se precisa de failover
                    if health.status == RegionStatus.UNHEALTHY:
                        self._trigger_failover(region)
                        
                except Exception as e:
                    logger.error(f"[FF-002] Erro ao verificar saúde da região {region.value}: {e}")

    def _check_region_health(self, region: Region) -> RegionHealth:
        """Verifica saúde de uma região específica"""
        config = self.regions[region]
        start_time = time.time()
        
        try:
            # Simular health check (em produção seria uma chamada real)
            response_time = self._simulate_health_check(config.endpoint)
            latency = response_time * 1000  # Converter para ms
            
            # Calcular métricas
            error_rate = 0.0  # Simulado
            uptime = 99.9  # Simulado
            
            # Determinar status
            if latency <= config.latency_threshold_ms and error_rate < 0.01:
                status = RegionStatus.HEALTHY
            elif latency <= config.latency_threshold_ms * 2 and error_rate < 0.05:
                status = RegionStatus.DEGRADED
            else:
                status = RegionStatus.UNHEALTHY
            
            # Identificar issues
            issues = []
            if latency > config.latency_threshold_ms:
                issues.append(f"Latency {latency:.2f}ms exceeds threshold {config.latency_threshold_ms}ms")
            if error_rate > 0.01:
                issues.append(f"Error rate {error_rate:.2%} is too high")
            
            return RegionHealth(
                region=region,
                status=status,
                latency_ms=latency,
                response_time_ms=response_time * 1000,
                error_rate=error_rate,
                uptime_percentage=uptime,
                last_check=datetime.utcnow(),
                next_check=datetime.utcnow() + timedelta(seconds=config.health_check_interval),
                issues=issues
            )
            
        except Exception as e:
            logger.error(f"[FF-002] Health check failed for {region.value}: {e}")
            return RegionHealth(
                region=region,
                status=RegionStatus.UNHEALTHY,
                latency_ms=float('inf'),
                response_time_ms=float('inf'),
                error_rate=1.0,
                uptime_percentage=0.0,
                last_check=datetime.utcnow(),
                next_check=datetime.utcnow() + timedelta(seconds=config.health_check_interval),
                issues=[f"Health check failed: {str(e)}"]
            )

    def _simulate_health_check(self, endpoint: str) -> float:
        """Simula health check de uma região"""
        # Em produção, isso seria uma chamada HTTP real
        import random
        time.sleep(random.uniform(0.01, 0.1))  # Simular latência
        return random.uniform(0.05, 0.5)  # 50-500ms

    def _trigger_failover(self, failed_region: Region):
        """Dispara failover para região alternativa"""
        try:
            # Encontrar região alternativa mais próxima
            alternative_region = self._find_best_alternative_region(failed_region)
            
            if alternative_region:
                failover_record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "failed_region": failed_region.value,
                    "alternative_region": alternative_region.value,
                    "reason": "Health check failed",
                    "status": "initiated"
                }
                
                self.failover_history.append(failover_record)
                
                logger.warning(f"[FF-002] Failover triggered: {failed_region.value} -> {alternative_region.value}")
                
                # Em produção, aqui seria feita a mudança de roteamento
                self._update_routing(failed_region, alternative_region)
                
        except Exception as e:
            logger.error(f"[FF-002] Erro no failover: {e}")

    def _find_best_alternative_region(self, failed_region: Region) -> Optional[Region]:
        """Encontra a melhor região alternativa"""
        with self.lock:
            # Filtrar regiões saudáveis
            healthy_regions = [
                region for region in self.regions
                if region != failed_region and 
                self.health_status.get(region, RegionHealth(
                    region=region,
                    status=RegionStatus.UNHEALTHY,
                    latency_ms=float('inf'),
                    response_time_ms=float('inf'),
                    error_rate=1.0,
                    uptime_percentage=0.0,
                    last_check=datetime.utcnow(),
                    next_check=datetime.utcnow()
                )).status in [RegionStatus.HEALTHY, RegionStatus.DEGRADED]
            ]
            
            if not healthy_regions:
                return None
            
            # Ordenar por prioridade de failover e latência
            def sort_key(region):
                config = self.regions[region]
                health = self.health_status.get(region)
                latency = health.latency_ms if health else float('inf')
                return (config.failover_priority, latency)
            
            return sorted(healthy_regions, key=sort_key)[0]

    def _update_routing(self, failed_region: Region, alternative_region: Region):
        """Atualiza roteamento para região alternativa"""
        # Em produção, isso atualizaria DNS, load balancers, etc.
        logger.info(f"[FF-002] Routing updated: {failed_region.value} -> {alternative_region.value}")

    def get_best_region(self, user_location: Optional[str] = None, 
                       compliance_requirements: Optional[List[ComplianceStandard]] = None) -> Region:
        """
        Obtém a melhor região baseada em localização e compliance
        
        Args:
            user_location: Localização do usuário (opcional)
            compliance_requirements: Requisitos de compliance (opcional)
            
        Returns:
            Melhor região para o usuário
        """
        with self.lock:
            # Filtrar regiões por compliance
            available_regions = list(self.regions.keys())
            
            if compliance_requirements:
                available_regions = [
                    region for region in available_regions
                    if all(req in self.regions[region].compliance_standards 
                          for req in compliance_requirements)
                ]
            
            if not available_regions:
                logger.warning("[FF-002] Nenhuma região disponível para compliance requirements")
                return self.default_region
            
            # Filtrar por saúde
            healthy_regions = [
                region for region in available_regions
                if self.health_status.get(region, RegionHealth(
                    region=region,
                    status=RegionStatus.UNHEALTHY,
                    latency_ms=float('inf'),
                    response_time_ms=float('inf'),
                    error_rate=1.0,
                    uptime_percentage=0.0,
                    last_check=datetime.utcnow(),
                    next_check=datetime.utcnow()
                )).status in [RegionStatus.HEALTHY, RegionStatus.DEGRADED]
            ]
            
            if not healthy_regions:
                logger.warning("[FF-002] Nenhuma região saudável disponível")
                return self.default_region
            
            # Se não há localização específica, usar região com menor latência
            if not user_location:
                return min(healthy_regions, 
                          key=lambda r: self.health_status.get(r, RegionHealth(
                              region=r,
                              status=RegionStatus.UNHEALTHY,
                              latency_ms=float('inf'),
                              response_time_ms=float('inf'),
                              error_rate=1.0,
                              uptime_percentage=0.0,
                              last_check=datetime.utcnow(),
                              next_check=datetime.utcnow()
                          )).latency_ms)
            
            # Com localização, usar lógica de proximidade
            return self._get_closest_region(healthy_regions, user_location)

    def _get_closest_region(self, regions: List[Region], user_location: str) -> Region:
        """Obtém região mais próxima baseada na localização"""
        # Mapeamento simplificado de localização para região
        location_mapping = {
            "us": [Region.US_EAST_1, Region.US_WEST_2],
            "eu": [Region.EU_WEST_1],
            "asia": [Region.AP_SOUTHEAST_1],
            "sa": [Region.SA_EAST_1]
        }
        
        # Determinar continente baseado na localização
        continent = self._detect_continent(user_location)
        preferred_regions = location_mapping.get(continent, [])
        
        # Filtrar regiões preferidas que estão disponíveis
        available_preferred = [r for r in preferred_regions if r in regions]
        
        if available_preferred:
            # Retornar a região preferida com menor latência
            return min(available_preferred, 
                      key=lambda r: self.health_status.get(r, RegionHealth(
                          region=r,
                          status=RegionStatus.UNHEALTHY,
                          latency_ms=float('inf'),
                          response_time_ms=float('inf'),
                          error_rate=1.0,
                          uptime_percentage=0.0,
                          last_check=datetime.utcnow(),
                          next_check=datetime.utcnow()
                      )).latency_ms)
        
        # Se não há região preferida disponível, usar a com menor latência
        return min(regions, 
                  key=lambda r: self.health_status.get(r, RegionHealth(
                      region=r,
                      status=RegionStatus.UNHEALTHY,
                      latency_ms=float('inf'),
                      response_time_ms=float('inf'),
                      error_rate=1.0,
                      uptime_percentage=0.0,
                      last_check=datetime.utcnow(),
                      next_check=datetime.utcnow()
                  )).latency_ms)

    def _detect_continent(self, location: str) -> str:
        """Detecta continente baseado na localização"""
        location_lower = location.lower()
        
        if any(country in location_lower for country in ["us", "united states", "canada", "mexico"]):
            return "us"
        elif any(country in location_lower for country in ["uk", "germany", "france", "spain", "italy", "europe"]):
            return "eu"
        elif any(country in location_lower for country in ["china", "japan", "korea", "singapore", "asia"]):
            return "asia"
        elif any(country in location_lower for country in ["brazil", "argentina", "chile", "south america"]):
            return "sa"
        else:
            return "us"  # Default

    def get_region_config(self, region: Region) -> Optional[RegionConfig]:
        """Obtém configuração de uma região"""
        return self.regions.get(region)

    def get_region_health(self, region: Region) -> Optional[RegionHealth]:
        """Obtém status de saúde de uma região"""
        return self.health_status.get(region)

    def get_all_regions_health(self) -> Dict[Region, RegionHealth]:
        """Obtém status de saúde de todas as regiões"""
        return self.health_status.copy()

    def update_region_config(self, region: Region, updates: Dict[str, Any]) -> bool:
        """
        Atualiza configuração de uma região
        
        Args:
            region: Região a ser atualizada
            updates: Atualizações a serem aplicadas
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            with self.lock:
                if region not in self.regions:
                    return False
                
                config = self.regions[region]
                
                # Aplicar atualizações
                for key, value in updates.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                
                config.updated_at = datetime.utcnow()
                
                logger.info(f"[FF-002] Configuração da região {region.value} atualizada")
                return True
                
        except Exception as e:
            logger.error(f"[FF-002] Erro ao atualizar configuração da região {region.value}: {e}")
            return False

    def get_failover_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém histórico de failovers"""
        return self.failover_history[-limit:]

    def get_compliance_report(self) -> Dict[str, Any]:
        """Gera relatório de compliance por região"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "regions": {}
        }
        
        for region, config in self.regions.items():
            health = self.health_status.get(region)
            
            report["regions"][region.value] = {
                "name": config.name,
                "compliance_standards": [std.value for std in config.compliance_standards],
                "data_retention_days": config.data_retention_days,
                "encryption_required": config.encryption_required,
                "backup_enabled": config.backup_enabled,
                "status": health.status.value if health else "unknown",
                "uptime_percentage": health.uptime_percentage if health else 0.0
            }
        
        return report

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance por região"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "regions": {},
            "summary": {
                "total_regions": len(self.regions),
                "healthy_regions": 0,
                "degraded_regions": 0,
                "unhealthy_regions": 0,
                "average_latency_ms": 0.0
            }
        }
        
        total_latency = 0.0
        healthy_count = 0
        
        for region, health in self.health_status.items():
            metrics["regions"][region.value] = {
                "latency_ms": health.latency_ms,
                "response_time_ms": health.response_time_ms,
                "error_rate": health.error_rate,
                "uptime_percentage": health.uptime_percentage,
                "status": health.status.value,
                "last_check": health.last_check.isoformat(),
                "issues": health.issues
            }
            
            if health.status == RegionStatus.HEALTHY:
                metrics["summary"]["healthy_regions"] += 1
                healthy_count += 1
            elif health.status == RegionStatus.DEGRADED:
                metrics["summary"]["degraded_regions"] += 1
            else:
                metrics["summary"]["unhealthy_regions"] += 1
            
            total_latency += health.latency_ms
        
        if healthy_count > 0:
            metrics["summary"]["average_latency_ms"] = total_latency / len(self.health_status)
        
        return metrics

    def get_health_status(self) -> Dict[str, Any]:
        """Obtém status de saúde geral do sistema"""
        try:
            healthy_count = sum(1 for health in self.health_status.values() 
                              if health.status == RegionStatus.HEALTHY)
            total_regions = len(self.regions)
            
            return {
                "status": "healthy" if healthy_count > total_regions // 2 else "degraded",
                "total_regions": total_regions,
                "healthy_regions": healthy_count,
                "degraded_regions": sum(1 for health in self.health_status.values() 
                                      if health.status == RegionStatus.DEGRADED),
                "unhealthy_regions": sum(1 for health in self.health_status.values() 
                                       if health.status == RegionStatus.UNHEALTHY),
                "last_failover": self.failover_history[-1] if self.failover_history else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[FF-002] Erro ao obter status de saúde: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Instância global
_multi_region_manager: Optional[MultiRegionManager] = None

def get_multi_region_manager() -> MultiRegionManager:
    """Obtém instância global do gerenciador multi-região"""
    global _multi_region_manager
    
    if _multi_region_manager is None:
        default_region = Region(os.getenv('DEFAULT_REGION', 'us-east-1'))
        _multi_region_manager = MultiRegionManager(default_region)
    
    return _multi_region_manager

def get_best_region(user_location: Optional[str] = None, 
                   compliance_requirements: Optional[List[ComplianceStandard]] = None) -> Region:
    """
    Função de conveniência para obter melhor região
    
    Args:
        user_location: Localização do usuário
        compliance_requirements: Requisitos de compliance
        
    Returns:
        Melhor região para o usuário
    """
    manager = get_multi_region_manager()
    return manager.get_best_region(user_location, compliance_requirements)

def get_region_health(region: Region) -> Optional[RegionHealth]:
    """
    Função de conveniência para obter saúde de região
    
    Args:
        region: Região a ser verificada
        
    Returns:
        Status de saúde da região
    """
    manager = get_multi_region_manager()
    return manager.get_region_health(region) 