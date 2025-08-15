"""
Testes unitários para ServiceMeshDetector
Tracing ID: ARCH-001
Prompt: INTEGRATION_EXTERNAL_CHECKLIST_V2.md
Ruleset: enterprise_control_layer.yaml
Data/Hora: 2024-12-20 01:00:00 UTC

Testes unitários abrangentes para o sistema de detecção de service mesh.
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Optional

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from infrastructure.service_mesh.mesh_detector import (
    ServiceMeshDetector,
    MeshType,
    ValidationStatus,
    MeshValidationResult,
    detect_service_mesh,
    generate_mesh_report
)


class TestServiceMeshDetector:
    """Testes para ServiceMeshDetector"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = {
            "timeout": 5,
            "retry_attempts": 3
        }
        self.detector = ServiceMeshDetector(self.config)
    
    def test_init_with_config(self):
        """Testa inicialização com configuração"""
        detector = ServiceMeshDetector(self.config)
        assert detector.config == self.config
        assert detector.timeout == 5
        assert detector.retry_attempts == 3
    
    def test_init_without_config(self):
        """Testa inicialização sem configuração"""
        detector = ServiceMeshDetector()
        assert detector.config == {}
        assert detector.timeout == 5  # valor padrão
        assert detector.retry_attempts == 3  # valor padrão
    
    def test_istio_endpoints_configured(self):
        """Testa se endpoints do Istio estão configurados"""
        expected_endpoints = ["pilot", "proxy", "config"]
        assert all(endpoint in self.detector.istio_endpoints for endpoint in expected_endpoints)
    
    def test_linkerd_endpoints_configured(self):
        """Testa se endpoints do Linkerd estão configurados"""
        expected_endpoints = ["admin", "proxy", "tap"]
        assert all(endpoint in self.detector.linkerd_endpoints for endpoint in expected_endpoints)
    
    @patch('os.getenv')
    def test_detect_mesh_type_istio_env(self, mock_getenv):
        """Testa detecção de Istio via variável de ambiente"""
        mock_getenv.return_value = "test-workload"
        
        mesh_type = self.detector.detect_mesh_type()
        assert mesh_type == MeshType.ISTIO
    
    @patch('os.getenv')
    def test_detect_mesh_type_linkerd_env(self, mock_getenv):
        """Testa detecção de Linkerd via variável de ambiente"""
        mock_getenv.side_effect = lambda value: "test-proxy-id" if value == "LINKERD_PROXY_ID" else None
        
        mesh_type = self.detector.detect_mesh_type()
        assert mesh_type == MeshType.LINKERD
    
    @patch('requests.get')
    def test_detect_mesh_type_istio_endpoint(self, mock_get):
        """Testa detecção de Istio via endpoint"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        mesh_type = self.detector.detect_mesh_type()
        assert mesh_type == MeshType.ISTIO
    
    @patch('requests.get')
    def test_detect_mesh_type_linkerd_endpoint(self, mock_get):
        """Testa detecção de Linkerd via endpoint"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        mesh_type = self.detector.detect_mesh_type()
        assert mesh_type == MeshType.LINKERD
    
    @patch('requests.get')
    @patch('os.getenv')
    def test_detect_mesh_type_unknown(self, mock_getenv, mock_get):
        """Testa detecção quando nenhum mesh está disponível"""
        mock_getenv.return_value = None
        mock_get.side_effect = Exception("Connection failed")
        
        mesh_type = self.detector.detect_mesh_type()
        assert mesh_type == MeshType.UNKNOWN
    
    @patch('requests.get')
    def test_validate_circuit_breaker_istio_success(self, mock_get):
        """Testa validação de circuit breaker do Istio com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outbound": [
                {"circuit_breaker": {"max_requests": 100}}
            ]
        }
        mock_get.return_value = mock_response
        
        status = self.detector.validate_circuit_breaker(MeshType.ISTIO)
        assert status == ValidationStatus.PASSED
    
    @patch('requests.get')
    def test_validate_circuit_breaker_istio_warning(self, mock_get):
        """Testa validação de circuit breaker do Istio com warning"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"outbound": []}
        mock_get.return_value = mock_response
        
        status = self.detector.validate_circuit_breaker(MeshType.ISTIO)
        assert status == ValidationStatus.WARNING
    
    @patch('requests.get')
    def test_validate_circuit_breaker_linkerd_success(self, mock_get):
        """Testa validação de circuit breaker do Linkerd com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "circuit_breaker_total 10"
        mock_get.return_value = mock_response
        
        status = self.detector.validate_circuit_breaker(MeshType.LINKERD)
        assert status == ValidationStatus.PASSED
    
    @patch('requests.get')
    def test_validate_circuit_breaker_linkerd_warning(self, mock_get):
        """Testa validação de circuit breaker do Linkerd com warning"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "no circuit breaker metrics"
        mock_get.return_value = mock_response
        
        status = self.detector.validate_circuit_breaker(MeshType.LINKERD)
        assert status == ValidationStatus.WARNING
    
    @patch('requests.get')
    def test_validate_rate_limit_istio_success(self, mock_get):
        """Testa validação de rate limit do Istio com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"envoy_filters": [{"name": "rate-limit"}]}
        mock_get.return_value = mock_response
        
        status = self.detector.validate_rate_limit(MeshType.ISTIO)
        assert status == ValidationStatus.PASSED
    
    @patch('requests.get')
    def test_validate_rate_limit_linkerd_success(self, mock_get):
        """Testa validação de rate limit do Linkerd com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "rate_limit_total 5"
        mock_get.return_value = mock_response
        
        status = self.detector.validate_rate_limit(MeshType.LINKERD)
        assert status == ValidationStatus.PASSED
    
    @patch('requests.get')
    def test_validate_tracing_istio_success(self, mock_get):
        """Testa validação de tracing do Istio com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tracing": {"zipkin": {"address": "localhost:9411"}}}
        mock_get.return_value = mock_response
        
        status = self.detector.validate_tracing(MeshType.ISTIO)
        assert status == ValidationStatus.PASSED
    
    @patch('requests.get')
    def test_validate_tracing_linkerd_success(self, mock_get):
        """Testa validação de tracing do Linkerd com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "tracing_spans_total 100"
        mock_get.return_value = mock_response
        
        status = self.detector.validate_tracing(MeshType.LINKERD)
        assert status == ValidationStatus.PASSED
    
    @patch('os.getenv')
    def test_get_mesh_version_istio_env(self, mock_getenv):
        """Testa obtenção de versão do Istio via variável de ambiente"""
        mock_getenv.return_value = "1.18.0"
        
        version = self.detector.get_mesh_version(MeshType.ISTIO)
        assert version == "1.18.0"
    
    @patch('requests.get')
    def test_get_mesh_version_istio_endpoint(self, mock_get):
        """Testa obtenção de versão do Istio via endpoint"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "1.18.0"}
        mock_get.return_value = mock_response
        
        version = self.detector.get_mesh_version(MeshType.ISTIO)
        assert version == "1.18.0"
    
    def test_calculate_health_score_perfect(self):
        """Testa cálculo de score de saúde perfeito"""
        result = MeshValidationResult(
            mesh_type=MeshType.ISTIO,
            is_detected=True,
            version="1.18.0",
            circuit_breaker=ValidationStatus.PASSED,
            rate_limit=ValidationStatus.PASSED,
            tracing=ValidationStatus.PASSED,
            health_score=0.0,
            details={}
        )
        
        score = self.detector.calculate_health_score(result)
        assert score == 100.0
    
    def test_calculate_health_score_partial(self):
        """Testa cálculo de score de saúde parcial"""
        result = MeshValidationResult(
            mesh_type=MeshType.ISTIO,
            is_detected=True,
            version="1.18.0",
            circuit_breaker=ValidationStatus.PASSED,
            rate_limit=ValidationStatus.WARNING,
            tracing=ValidationStatus.FAILED,
            health_score=0.0,
            details={}
        )
        
        score = self.detector.calculate_health_score(result)
        assert score == 45.0  # 30 + 15 + 0
    
    def test_calculate_health_score_not_detected(self):
        """Testa cálculo de score quando mesh não é detectado"""
        result = MeshValidationResult(
            mesh_type=MeshType.UNKNOWN,
            is_detected=False,
            version=None,
            circuit_breaker=ValidationStatus.NOT_AVAILABLE,
            rate_limit=ValidationStatus.NOT_AVAILABLE,
            tracing=ValidationStatus.NOT_AVAILABLE,
            health_score=0.0,
            details={}
        )
        
        score = self.detector.calculate_health_score(result)
        assert score == 0.0
    
    @patch('requests.get')
    @patch('os.getenv')
    def test_validate_mesh_complete_istio(self, mock_getenv, mock_get):
        """Testa validação completa do mesh Istio"""
        mock_getenv.return_value = "test-workload"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outbound": [{"circuit_breaker": {"max_requests": 100}}],
            "envoy_filters": [{"name": "rate-limit"}],
            "tracing": {"zipkin": {"address": "localhost:9411"}}
        }
        mock_response.text = "circuit_breaker_total 10"
        mock_get.return_value = mock_response
        
        result = self.detector.validate_mesh()
        
        assert result.mesh_type == MeshType.ISTIO
        assert result.is_detected is True
        assert result.circuit_breaker == ValidationStatus.PASSED
        assert result.rate_limit == ValidationStatus.PASSED
        assert result.tracing == ValidationStatus.PASSED
        assert result.health_score == 100.0
    
    def test_generate_recommendations_no_mesh(self):
        """Testa geração de recomendações quando não há mesh"""
        result = MeshValidationResult(
            mesh_type=MeshType.UNKNOWN,
            is_detected=False,
            version=None,
            circuit_breaker=ValidationStatus.NOT_AVAILABLE,
            rate_limit=ValidationStatus.NOT_AVAILABLE,
            tracing=ValidationStatus.NOT_AVAILABLE,
            health_score=0.0,
            details={}
        )
        
        recommendations = self.detector._generate_recommendations(result)
        assert len(recommendations) == 1
        assert "Implementar service mesh" in recommendations[0]
    
    def test_generate_recommendations_with_issues(self):
        """Testa geração de recomendações com problemas"""
        result = MeshValidationResult(
            mesh_type=MeshType.ISTIO,
            is_detected=True,
            version="1.18.0",
            circuit_breaker=ValidationStatus.FAILED,
            rate_limit=ValidationStatus.WARNING,
            tracing=ValidationStatus.PASSED,
            health_score=70.0,
            details={}
        )
        
        recommendations = self.detector._generate_recommendations(result)
        assert len(recommendations) >= 2
        assert any("circuit breaker" in rec.lower() for rec in recommendations)
        assert any("rate limit" in rec.lower() for rec in recommendations)
    
    def test_generate_report_structure(self):
        """Testa estrutura do relatório gerado"""
        result = MeshValidationResult(
            mesh_type=MeshType.ISTIO,
            is_detected=True,
            version="1.18.0",
            circuit_breaker=ValidationStatus.PASSED,
            rate_limit=ValidationStatus.PASSED,
            tracing=ValidationStatus.PASSED,
            health_score=100.0,
            details={"test": "data"}
        )
        
        report = self.detector.generate_report(result)
        
        assert "tracing_id" in report
        assert "timestamp" in report
        assert "mesh_type" in report
        assert "is_detected" in report
        assert "version" in report
        assert "health_score" in report
        assert "validations" in report
        assert "recommendations" in report
        assert "details" in report
        
        assert report["tracing_id"] == "ARCH-001"
        assert report["mesh_type"] == "istio"
        assert report["is_detected"] is True
        assert report["health_score"] == 100.0


class TestConvenienceFunctions:
    """Testes para funções de conveniência"""
    
    @patch('infrastructure.service_mesh.mesh_detector.ServiceMeshDetector')
    def test_detect_service_mesh(self, mock_detector_class):
        """Testa função de conveniência detect_service_mesh"""
        mock_detector = Mock()
        mock_result = Mock()
        mock_detector.validate_mesh.return_value = mock_result
        mock_detector_class.return_value = mock_detector
        
        result = detect_service_mesh({"timeout": 10})
        
        mock_detector_class.assert_called_once_with({"timeout": 10})
        mock_detector.validate_mesh.assert_called_once()
        assert result == mock_result
    
    @patch('infrastructure.service_mesh.mesh_detector.ServiceMeshDetector')
    def test_generate_mesh_report(self, mock_detector_class):
        """Testa função de conveniência generate_mesh_report"""
        mock_detector = Mock()
        mock_result = Mock()
        mock_report = {"test": "report"}
        
        mock_detector.validate_mesh.return_value = mock_result
        mock_detector.generate_report.return_value = mock_report
        mock_detector_class.return_value = mock_detector
        
        report = generate_mesh_report({"timeout": 10})
        
        mock_detector_class.assert_called_once_with({"timeout": 10})
        mock_detector.validate_mesh.assert_called_once()
        mock_detector.generate_report.assert_called_once_with(mock_result)
        assert report == mock_report


class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.detector = ServiceMeshDetector()
    
    @patch('requests.get')
    def test_validate_circuit_breaker_request_exception(self, mock_get):
        """Testa tratamento de erro na validação de circuit breaker"""
        mock_get.side_effect = Exception("Network error")
        
        status = self.detector.validate_circuit_breaker(MeshType.ISTIO)
        assert status == ValidationStatus.FAILED
    
    @patch('requests.get')
    def test_validate_rate_limit_request_exception(self, mock_get):
        """Testa tratamento de erro na validação de rate limit"""
        mock_get.side_effect = Exception("Network error")
        
        status = self.detector.validate_rate_limit(MeshType.ISTIO)
        assert status == ValidationStatus.FAILED
    
    @patch('requests.get')
    def test_validate_tracing_request_exception(self, mock_get):
        """Testa tratamento de erro na validação de tracing"""
        mock_get.side_effect = Exception("Network error")
        
        status = self.detector.validate_tracing(MeshType.ISTIO)
        assert status == ValidationStatus.FAILED
    
    def test_validate_circuit_breaker_unknown_mesh(self):
        """Testa validação de circuit breaker para mesh desconhecido"""
        status = self.detector.validate_circuit_breaker(MeshType.UNKNOWN)
        assert status == ValidationStatus.NOT_AVAILABLE
    
    def test_validate_rate_limit_unknown_mesh(self):
        """Testa validação de rate limit para mesh desconhecido"""
        status = self.detector.validate_rate_limit(MeshType.UNKNOWN)
        assert status == ValidationStatus.NOT_AVAILABLE
    
    def test_validate_tracing_unknown_mesh(self):
        """Testa validação de tracing para mesh desconhecido"""
        status = self.detector.validate_tracing(MeshType.UNKNOWN)
        assert status == ValidationStatus.NOT_AVAILABLE


class TestIntegrationScenarios:
    """Testes de cenários de integração"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.detector = ServiceMeshDetector()
    
    @patch('requests.get')
    @patch('os.getenv')
    def test_full_istio_detection_scenario(self, mock_getenv, mock_get):
        """Testa cenário completo de detecção do Istio"""
        # Mock variável de ambiente
        mock_getenv.return_value = "test-workload"
        
        # Mock respostas dos endpoints
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outbound": [{"circuit_breaker": {"max_requests": 100}}],
            "envoy_filters": [{"name": "rate-limit"}],
            "tracing": {"zipkin": {"address": "localhost:9411"}}
        }
        mock_response.text = "circuit_breaker_total 10"
        mock_get.return_value = mock_response
        
        # Executar validação completa
        result = self.detector.validate_mesh()
        
        # Verificar resultados
        assert result.mesh_type == MeshType.ISTIO
        assert result.is_detected is True
        assert result.circuit_breaker == ValidationStatus.PASSED
        assert result.rate_limit == ValidationStatus.PASSED
        assert result.tracing == ValidationStatus.PASSED
        assert result.health_score == 100.0
        
        # Verificar detalhes
        assert "detection_time" in result.details
        assert "config" in result.details
        assert "endpoints_checked" in result.details
    
    @patch('requests.get')
    @patch('os.getenv')
    def test_full_linkerd_detection_scenario(self, mock_getenv, mock_get):
        """Testa cenário completo de detecção do Linkerd"""
        # Mock variável de ambiente
        mock_getenv.side_effect = lambda value: "test-proxy-id" if value == "LINKERD_PROXY_ID" else None
        
        # Mock respostas dos endpoints
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "circuit_breaker_total 10\nrate_limit_total 5\ntracing_spans_total 100"
        mock_get.return_value = mock_response
        
        # Executar validação completa
        result = self.detector.validate_mesh()
        
        # Verificar resultados
        assert result.mesh_type == MeshType.LINKERD
        assert result.is_detected is True
        assert result.circuit_breaker == ValidationStatus.PASSED
        assert result.rate_limit == ValidationStatus.PASSED
        assert result.tracing == ValidationStatus.PASSED
        assert result.health_score == 100.0
    
    @patch('requests.get')
    @patch('os.getenv')
    def test_partial_configuration_scenario(self, mock_getenv, mock_get):
        """Testa cenário com configuração parcial"""
        # Mock variável de ambiente
        mock_getenv.return_value = "test-workload"
        
        # Mock respostas dos endpoints com configuração parcial
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "outbound": [],  # Sem circuit breaker
            "envoy_filters": [{"name": "rate-limit"}],  # Com rate limit
            "tracing": {"zipkin": {"address": "localhost:9411"}}  # Com tracing
        }
        mock_response.text = "no circuit breaker metrics"
        mock_get.return_value = mock_response
        
        # Executar validação completa
        result = self.detector.validate_mesh()
        
        # Verificar resultados
        assert result.mesh_type == MeshType.ISTIO
        assert result.is_detected is True
        assert result.circuit_breaker == ValidationStatus.WARNING
        assert result.rate_limit == ValidationStatus.PASSED
        assert result.tracing == ValidationStatus.PASSED
        assert result.health_score == 85.0  # 15 + 30 + 40


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 