"""
Service Mesh Detection System
Tracing ID: ARCH-001
Prompt: INTEGRATION_EXTERNAL_CHECKLIST_V2.md
Ruleset: enterprise_control_layer.yaml
Data/Hora: 2024-12-20 01:00:00 UTC

Sistema de detecção e validação de service mesh (Istio/Linkerd)
para integrações externas enterprise.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
from urllib.parse import urljoin

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MeshType(Enum):
    """Tipos de service mesh suportados"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    UNKNOWN = "unknown"


class ValidationStatus(Enum):
    """Status de validação"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_AVAILABLE = "not_available"


@dataclass
class MeshValidationResult:
    """Resultado de validação de service mesh"""
    mesh_type: MeshType
    is_detected: bool
    version: Optional[str]
    circuit_breaker: ValidationStatus
    rate_limit: ValidationStatus
    tracing: ValidationStatus
    health_score: float
    details: Dict[str, any]


class ServiceMeshDetector:
    """
    Detector de service mesh para validação de integrações externas
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o detector de service mesh
        
        Args:
            config: Configuração opcional
        """
        self.config = config or {}
        self.istio_endpoints = {
            "pilot": "http://istiod.istio-system.svc.cluster.local:15014/ready",
            "proxy": "http://localhost:15000/stats",
            "config": "http://localhost:15000/config_dump"
        }
        self.linkerd_endpoints = {
            "admin": "http://localhost:4191/metrics",
            "proxy": "http://localhost:4140/metrics",
            "tap": "http://localhost:4191/tap"
        }
        self.timeout = self.config.get("timeout", 5)
        self.retry_attempts = self.config.get("retry_attempts", 3)
        
    def detect_mesh_type(self) -> MeshType:
        """
        Detecta o tipo de service mesh em execução
        
        Returns:
            MeshType: Tipo de service mesh detectado
        """
        logger.info("[ServiceMeshDetector] Iniciando detecção de service mesh")
        
        # Verificar Istio
        if self._check_istio():
            logger.info("[ServiceMeshDetector] Istio detectado")
            return MeshType.ISTIO
            
        # Verificar Linkerd
        if self._check_linkerd():
            logger.info("[ServiceMeshDetector] Linkerd detectado")
            return MeshType.LINKERD
            
        logger.warning("[ServiceMeshDetector] Nenhum service mesh detectado")
        return MeshType.UNKNOWN
    
    def _check_istio(self) -> bool:
        """Verifica se Istio está ativo"""
        try:
            # Verificar variáveis de ambiente
            if os.getenv("ISTIO_META_WORKLOAD_NAME"):
                return True
                
            # Verificar endpoints do Istio
            for name, endpoint in self.istio_endpoints.items():
                try:
                    response = requests.get(endpoint, timeout=self.timeout)
                    if response.status_code == 200:
                        logger.info(f"[ServiceMeshDetector] Istio endpoint {name} respondendo")
                        return True
                except requests.RequestException:
                    continue
                    
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro ao verificar Istio: {e}")
            
        return False
    
    def _check_linkerd(self) -> bool:
        """Verifica se Linkerd está ativo"""
        try:
            # Verificar variáveis de ambiente
            if os.getenv("LINKERD_PROXY_ID"):
                return True
                
            # Verificar endpoints do Linkerd
            for name, endpoint in self.linkerd_endpoints.items():
                try:
                    response = requests.get(endpoint, timeout=self.timeout)
                    if response.status_code == 200:
                        logger.info(f"[ServiceMeshDetector] Linkerd endpoint {name} respondendo")
                        return True
                except requests.RequestException:
                    continue
                    
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro ao verificar Linkerd: {e}")
            
        return False
    
    def validate_circuit_breaker(self, mesh_type: MeshType) -> ValidationStatus:
        """
        Valida configuração de circuit breaker
        
        Args:
            mesh_type: Tipo de service mesh
            
        Returns:
            ValidationStatus: Status da validação
        """
        logger.info(f"[ServiceMeshDetector] Validando circuit breaker para {mesh_type.value}")
        
        try:
            if mesh_type == MeshType.ISTIO:
                return self._validate_istio_circuit_breaker()
            elif mesh_type == MeshType.LINKERD:
                return self._validate_linkerd_circuit_breaker()
            else:
                return ValidationStatus.NOT_AVAILABLE
                
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação de circuit breaker: {e}")
            return ValidationStatus.FAILED
    
    def _validate_istio_circuit_breaker(self) -> ValidationStatus:
        """Valida circuit breaker do Istio"""
        try:
            # Verificar configuração de destination rule
            config_endpoint = self.istio_endpoints["config"]
            response = requests.get(config_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                config_data = response.json()
                # Verificar se há configurações de circuit breaker
                if "outbound" in config_data:
                    for outbound in config_data["outbound"]:
                        if "circuit_breaker" in outbound:
                            logger.info("[ServiceMeshDetector] Circuit breaker Istio configurado")
                            return ValidationStatus.PASSED
                            
            return ValidationStatus.WARNING
            
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação Istio circuit breaker: {e}")
            return ValidationStatus.FAILED
    
    def _validate_linkerd_circuit_breaker(self) -> ValidationStatus:
        """Valida circuit breaker do Linkerd"""
        try:
            # Verificar métricas de circuit breaker
            metrics_endpoint = self.linkerd_endpoints["admin"]
            response = requests.get(metrics_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                metrics = response.text
                # Verificar métricas de circuit breaker
                if "circuit_breaker" in metrics.lower():
                    logger.info("[ServiceMeshDetector] Circuit breaker Linkerd configurado")
                    return ValidationStatus.PASSED
                    
            return ValidationStatus.WARNING
            
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação Linkerd circuit breaker: {e}")
            return ValidationStatus.FAILED
    
    def validate_rate_limit(self, mesh_type: MeshType) -> ValidationStatus:
        """
        Valida configuração de rate limit
        
        Args:
            mesh_type: Tipo de service mesh
            
        Returns:
            ValidationStatus: Status da validação
        """
        logger.info(f"[ServiceMeshDetector] Validando rate limit para {mesh_type.value}")
        
        try:
            if mesh_type == MeshType.ISTIO:
                return self._validate_istio_rate_limit()
            elif mesh_type == MeshType.LINKERD:
                return self._validate_linkerd_rate_limit()
            else:
                return ValidationStatus.NOT_AVAILABLE
                
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação de rate limit: {e}")
            return ValidationStatus.FAILED
    
    def _validate_istio_rate_limit(self) -> ValidationStatus:
        """Valida rate limit do Istio"""
        try:
            # Verificar configuração de envoy filter
            config_endpoint = self.istio_endpoints["config"]
            response = requests.get(config_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                config_data = response.json()
                # Verificar se há configurações de rate limit
                if "envoy_filters" in config_data:
                    logger.info("[ServiceMeshDetector] Rate limit Istio configurado")
                    return ValidationStatus.PASSED
                    
            return ValidationStatus.WARNING
            
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação Istio rate limit: {e}")
            return ValidationStatus.FAILED
    
    def _validate_linkerd_rate_limit(self) -> ValidationStatus:
        """Valida rate limit do Linkerd"""
        try:
            # Verificar métricas de rate limit
            metrics_endpoint = self.linkerd_endpoints["admin"]
            response = requests.get(metrics_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                metrics = response.text
                # Verificar métricas de rate limit
                if "rate_limit" in metrics.lower():
                    logger.info("[ServiceMeshDetector] Rate limit Linkerd configurado")
                    return ValidationStatus.PASSED
                    
            return ValidationStatus.WARNING
            
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação Linkerd rate limit: {e}")
            return ValidationStatus.FAILED
    
    def validate_tracing(self, mesh_type: MeshType) -> ValidationStatus:
        """
        Valida configuração de tracing
        
        Args:
            mesh_type: Tipo de service mesh
            
        Returns:
            ValidationStatus: Status da validação
        """
        logger.info(f"[ServiceMeshDetector] Validando tracing para {mesh_type.value}")
        
        try:
            if mesh_type == MeshType.ISTIO:
                return self._validate_istio_tracing()
            elif mesh_type == MeshType.LINKERD:
                return self._validate_linkerd_tracing()
            else:
                return ValidationStatus.NOT_AVAILABLE
                
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação de tracing: {e}")
            return ValidationStatus.FAILED
    
    def _validate_istio_tracing(self) -> ValidationStatus:
        """Valida tracing do Istio"""
        try:
            # Verificar configuração de tracing
            config_endpoint = self.istio_endpoints["config"]
            response = requests.get(config_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                config_data = response.json()
                # Verificar se há configurações de tracing
                if "tracing" in config_data or "zipkin" in str(config_data):
                    logger.info("[ServiceMeshDetector] Tracing Istio configurado")
                    return ValidationStatus.PASSED
                    
            return ValidationStatus.WARNING
            
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação Istio tracing: {e}")
            return ValidationStatus.FAILED
    
    def _validate_linkerd_tracing(self) -> ValidationStatus:
        """Valida tracing do Linkerd"""
        try:
            # Verificar métricas de tracing
            metrics_endpoint = self.linkerd_endpoints["admin"]
            response = requests.get(metrics_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                metrics = response.text
                # Verificar métricas de tracing
                if "tracing" in metrics.lower():
                    logger.info("[ServiceMeshDetector] Tracing Linkerd configurado")
                    return ValidationStatus.PASSED
                    
            return ValidationStatus.WARNING
            
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro na validação Linkerd tracing: {e}")
            return ValidationStatus.FAILED
    
    def get_mesh_version(self, mesh_type: MeshType) -> Optional[str]:
        """
        Obtém versão do service mesh
        
        Args:
            mesh_type: Tipo de service mesh
            
        Returns:
            Optional[str]: Versão do service mesh
        """
        try:
            if mesh_type == MeshType.ISTIO:
                return self._get_istio_version()
            elif mesh_type == MeshType.LINKERD:
                return self._get_linkerd_version()
            else:
                return None
                
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro ao obter versão: {e}")
            return None
    
    def _get_istio_version(self) -> Optional[str]:
        """Obtém versão do Istio"""
        try:
            # Verificar variável de ambiente
            version = os.getenv("ISTIO_VERSION")
            if version:
                return version
                
            # Verificar endpoint de versão
            version_endpoint = "http://istiod.istio-system.svc.cluster.local:15014/version"
            response = requests.get(version_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json().get("version")
                
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro ao obter versão Istio: {e}")
            
        return None
    
    def _get_linkerd_version(self) -> Optional[str]:
        """Obtém versão do Linkerd"""
        try:
            # Verificar variável de ambiente
            version = os.getenv("LINKERD_VERSION")
            if version:
                return version
                
            # Verificar endpoint de versão
            version_endpoint = "http://localhost:4191/version"
            response = requests.get(version_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json().get("version")
                
        except Exception as e:
            logger.error(f"[ServiceMeshDetector] Erro ao obter versão Linkerd: {e}")
            
        return None
    
    def calculate_health_score(self, result: MeshValidationResult) -> float:
        """
        Calcula score de saúde do service mesh
        
        Args:
            result: Resultado de validação
            
        Returns:
            float: Score de saúde (0-100)
        """
        if not result.is_detected:
            return 0.0
            
        score = 0.0
        total_checks = 0
        
        # Circuit breaker (30%)
        if result.circuit_breaker == ValidationStatus.PASSED:
            score += 30
        elif result.circuit_breaker == ValidationStatus.WARNING:
            score += 15
        total_checks += 1
        
        # Rate limit (30%)
        if result.rate_limit == ValidationStatus.PASSED:
            score += 30
        elif result.rate_limit == ValidationStatus.WARNING:
            score += 15
        total_checks += 1
        
        # Tracing (40%)
        if result.tracing == ValidationStatus.PASSED:
            score += 40
        elif result.tracing == ValidationStatus.WARNING:
            score += 20
        total_checks += 1
        
        return score
    
    def validate_mesh(self) -> MeshValidationResult:
        """
        Executa validação completa do service mesh
        
        Returns:
            MeshValidationResult: Resultado da validação
        """
        logger.info("[ServiceMeshDetector] Iniciando validação completa do service mesh")
        
        # Detectar tipo de mesh
        mesh_type = self.detect_mesh_type()
        is_detected = mesh_type != MeshType.UNKNOWN
        
        # Obter versão
        version = self.get_mesh_version(mesh_type) if is_detected else None
        
        # Validar componentes
        circuit_breaker = self.validate_circuit_breaker(mesh_type)
        rate_limit = self.validate_rate_limit(mesh_type)
        tracing = self.validate_tracing(mesh_type)
        
        # Criar resultado
        result = MeshValidationResult(
            mesh_type=mesh_type,
            is_detected=is_detected,
            version=version,
            circuit_breaker=circuit_breaker,
            rate_limit=rate_limit,
            tracing=tracing,
            health_score=0.0,
            details={}
        )
        
        # Calcular score de saúde
        result.health_score = self.calculate_health_score(result)
        
        # Adicionar detalhes
        result.details = {
            "detection_time": time.time(),
            "config": self.config,
            "endpoints_checked": {
                "istio": list(self.istio_endpoints.keys()),
                "linkerd": list(self.linkerd_endpoints.keys())
            }
        }
        
        logger.info(f"[ServiceMeshDetector] Validação concluída - Score: {result.health_score}")
        return result
    
    def generate_report(self, result: MeshValidationResult) -> Dict:
        """
        Gera relatório de validação
        
        Args:
            result: Resultado de validação
            
        Returns:
            Dict: Relatório estruturado
        """
        return {
            "tracing_id": "ARCH-001",
            "timestamp": time.time(),
            "mesh_type": result.mesh_type.value,
            "is_detected": result.is_detected,
            "version": result.version,
            "health_score": result.health_score,
            "validations": {
                "circuit_breaker": {
                    "status": result.circuit_breaker.value,
                    "description": "Validação de circuit breaker"
                },
                "rate_limit": {
                    "status": result.rate_limit.value,
                    "description": "Validação de rate limit"
                },
                "tracing": {
                    "status": result.tracing.value,
                    "description": "Validação de tracing"
                }
            },
            "recommendations": self._generate_recommendations(result),
            "details": result.details
        }
    
    def _generate_recommendations(self, result: MeshValidationResult) -> List[str]:
        """
        Gera recomendações baseadas no resultado
        
        Args:
            result: Resultado de validação
            
        Returns:
            List[str]: Lista de recomendações
        """
        recommendations = []
        
        if not result.is_detected:
            recommendations.append("Implementar service mesh (Istio ou Linkerd) para melhor controle de tráfego")
            return recommendations
        
        if result.circuit_breaker == ValidationStatus.FAILED:
            recommendations.append("Configurar circuit breaker para resiliência")
        elif result.circuit_breaker == ValidationStatus.WARNING:
            recommendations.append("Revisar configuração de circuit breaker")
            
        if result.rate_limit == ValidationStatus.FAILED:
            recommendations.append("Configurar rate limiting para proteção")
        elif result.rate_limit == ValidationStatus.WARNING:
            recommendations.append("Revisar configuração de rate limit")
            
        if result.tracing == ValidationStatus.FAILED:
            recommendations.append("Configurar tracing distribuído")
        elif result.tracing == ValidationStatus.WARNING:
            recommendations.append("Revisar configuração de tracing")
        
        if result.health_score < 70:
            recommendations.append("Melhorar configuração geral do service mesh")
            
        return recommendations


# Função de conveniência para uso global
def detect_service_mesh(config: Optional[Dict] = None) -> MeshValidationResult:
    """
    Função de conveniência para detecção de service mesh
    
    Args:
        config: Configuração opcional
        
    Returns:
        MeshValidationResult: Resultado da validação
    """
    detector = ServiceMeshDetector(config)
    return detector.validate_mesh()


def generate_mesh_report(config: Optional[Dict] = None) -> Dict:
    """
    Função de conveniência para gerar relatório de service mesh
    
    Args:
        config: Configuração opcional
        
    Returns:
        Dict: Relatório estruturado
    """
    detector = ServiceMeshDetector(config)
    result = detector.validate_mesh()
    return detector.generate_report(result)


if __name__ == "__main__":
    # Exemplo de uso
    detector = ServiceMeshDetector()
    result = detector.validate_mesh()
    report = detector.generate_report(result)
    
    print(json.dumps(report, indent=2)) 