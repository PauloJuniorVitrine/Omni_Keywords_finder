from typing import Dict, List, Optional, Any
"""
Testes Unitários para Shadow Testing
Tracing ID: TEST-002
Data: 2024-12-20
Versão: 1.0
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from tests.shadow.shadow_tester import (
    ShadowRequest,
    ShadowResponse,
    ShadowTestResult,
    ShadowAPIClient,
    ShadowTestGenerator,
    ShadowTester,
    RegressionDetector
)


class TestShadowRequest:
    """Testes para ShadowRequest"""
    
    def test_shadow_request_creation(self):
        """Testa criação de ShadowRequest"""
        request = ShadowRequest(
            request_id="REQ_12345678",
            endpoint="/api/v1/test",
            method="POST",
            payload={"test": "data"},
            headers={"Content-Type": "application/json"}
        )
        
        assert request.request_id == "REQ_12345678"
        assert request.endpoint == "/api/v1/test"
        assert request.method == "POST"
        assert request.payload == {"test": "data"}
        assert request.headers == {"Content-Type": "application/json"}
        assert isinstance(request.timestamp, datetime)
    
    def test_shadow_request_default_timestamp(self):
        """Testa timestamp padrão"""
        before = datetime.now()
        request = ShadowRequest(
            request_id="REQ_12345678",
            endpoint="/api/v1/test",
            method="GET"
        )
        after = datetime.now()
        
        assert before <= request.timestamp <= after
    
    def test_shadow_request_custom_timestamp(self):
        """Testa timestamp customizado"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        request = ShadowRequest(
            request_id="REQ_12345678",
            endpoint="/api/v1/test",
            method="GET",
            timestamp=custom_time
        )
        
        assert request.timestamp == custom_time


class TestShadowResponse:
    """Testes para ShadowResponse"""
    
    def test_shadow_response_creation(self):
        """Testa criação de ShadowResponse"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_response={"data": "prod"},
            shadow_response={"data": "shadow"},
            production_status=200,
            shadow_status=200,
            production_time=1.0,
            shadow_time=1.1
        )
        
        assert response.request_id == "REQ_12345678"
        assert response.production_response == {"data": "prod"}
        assert response.shadow_response == {"data": "shadow"}
        assert response.production_status == 200
        assert response.shadow_status == 200
        assert response.production_time == 1.0
        assert response.shadow_time == 1.1
    
    def test_is_match_identical_responses(self):
        """Testa correspondência de respostas idênticas"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_response={"data": "test"},
            shadow_response={"data": "test"},
            production_status=200,
            shadow_status=200
        )
        
        assert response.is_match is True
    
    def test_is_match_different_responses(self):
        """Testa correspondência de respostas diferentes"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_response={"data": "prod"},
            shadow_response={"data": "shadow"},
            production_status=200,
            shadow_status=200
        )
        
        assert response.is_match is False
    
    def test_is_match_different_status_codes(self):
        """Testa correspondência com status codes diferentes"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_response={"data": "test"},
            shadow_response={"data": "test"},
            production_status=200,
            shadow_status=404
        )
        
        assert response.is_match is False
    
    def test_is_match_both_errors(self):
        """Testa correspondência quando ambos têm erro"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_error="Connection timeout",
            shadow_error="Connection timeout"
        )
        
        assert response.is_match is True
    
    def test_is_match_different_errors(self):
        """Testa correspondência com erros diferentes"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_error="Connection timeout",
            shadow_error="Invalid response"
        )
        
        assert response.is_match is False
    
    def test_performance_diff_calculation(self):
        """Testa cálculo de diferença de performance"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_time=1.0,
            shadow_time=1.5
        )
        
        assert response.performance_diff == 0.5
    
    def test_performance_diff_zero(self):
        """Testa diferença de performance zero"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_time=1.0,
            shadow_time=1.0
        )
        
        assert response.performance_diff == 0.0
    
    def test_has_regression_error_introduced(self):
        """Testa detecção de regressão com erro introduzido"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            shadow_error="Connection timeout"
        )
        
        assert response.has_regression is True
    
    def test_has_regression_status_code_worse(self):
        """Testa detecção de regressão com status code pior"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_status=200,
            shadow_status=500
        )
        
        assert response.has_regression is True
    
    def test_has_regression_status_code_better(self):
        """Testa detecção de regressão com status code melhor"""
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_status=500,
            shadow_status=200
        )
        
        assert response.has_regression is False


class TestShadowTestResult:
    """Testes para ShadowTestResult"""
    
    def test_shadow_test_result_creation(self):
        """Testa criação de ShadowTestResult"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=5)
        
        responses = [
            ShadowResponse("REQ_1", production_status=200, shadow_status=200),
            ShadowResponse("REQ_2", production_status=200, shadow_status=404)
        ]
        
        result = ShadowTestResult(
            test_id="SHADOW_20241220_120000",
            total_requests=2,
            successful_requests=2,
            failed_requests=0,
            matching_responses=1,
            regressions_detected=1,
            avg_production_time=1.0,
            avg_shadow_time=1.1,
            avg_performance_diff=0.1,
            start_time=start_time,
            end_time=end_time,
            responses=responses
        )
        
        assert result.test_id == "SHADOW_20241220_120000"
        assert result.total_requests == 2
        assert result.successful_requests == 2
        assert result.matching_responses == 1
        assert result.regressions_detected == 1
    
    def test_success_rate_calculation(self):
        """Testa cálculo da taxa de sucesso"""
        result = ShadowTestResult(
            test_id="TEST",
            total_requests=10,
            successful_requests=8,
            failed_requests=2,
            matching_responses=7,
            regressions_detected=1,
            avg_production_time=1.0,
            avg_shadow_time=1.1,
            avg_performance_diff=0.1,
            start_time=datetime.now(),
            end_time=datetime.now(),
            responses=[]
        )
        
        assert result.success_rate == 0.8
    
    def test_success_rate_zero_requests(self):
        """Testa taxa de sucesso com zero requisições"""
        result = ShadowTestResult(
            test_id="TEST",
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            matching_responses=0,
            regressions_detected=0,
            avg_production_time=0.0,
            avg_shadow_time=0.0,
            avg_performance_diff=0.0,
            start_time=datetime.now(),
            end_time=datetime.now(),
            responses=[]
        )
        
        assert result.success_rate == 0.0
    
    def test_match_rate_calculation(self):
        """Testa cálculo da taxa de correspondência"""
        result = ShadowTestResult(
            test_id="TEST",
            total_requests=10,
            successful_requests=10,
            failed_requests=0,
            matching_responses=7,
            regressions_detected=3,
            avg_production_time=1.0,
            avg_shadow_time=1.1,
            avg_performance_diff=0.1,
            start_time=datetime.now(),
            end_time=datetime.now(),
            responses=[]
        )
        
        assert result.match_rate == 0.7
    
    def test_regression_rate_calculation(self):
        """Testa cálculo da taxa de regressão"""
        result = ShadowTestResult(
            test_id="TEST",
            total_requests=10,
            successful_requests=10,
            failed_requests=0,
            matching_responses=7,
            regressions_detected=3,
            avg_production_time=1.0,
            avg_shadow_time=1.1,
            avg_performance_diff=0.1,
            start_time=datetime.now(),
            end_time=datetime.now(),
            responses=[]
        )
        
        assert result.regression_rate == 0.3


class TestShadowAPIClient:
    """Testes para ShadowAPIClient"""
    
    @patch('tests.shadow.shadow_tester.requests.Session')
    def test_client_initialization(self, mock_session):
        """Testa inicialização do cliente"""
        production_config = {'base_url': 'https://prod.api.com', 'timeout': 30}
        shadow_config = {'base_url': 'https://shadow.api.com', 'timeout': 30}
        
        client = ShadowAPIClient(production_config, shadow_config)
        
        assert client.production_config == production_config
        assert client.shadow_config == shadow_config
        assert client.session is not None
    
    @patch('tests.shadow.shadow_tester.requests.Session')
    def test_make_production_request_success(self, mock_session):
        """Testa requisição de produção com sucesso"""
        # Mock da resposta
        mock_response = Mock()
        mock_response.json.return_value = {"data": "success"}
        mock_response.status_code = 200
        mock_response.content = b'{"data": "success"}'
        
        mock_session.return_value.request.return_value = mock_response
        
        production_config = {'base_url': 'https://prod.api.com', 'timeout': 30}
        shadow_config = {'base_url': 'https://shadow.api.com', 'timeout': 30}
        
        client = ShadowAPIClient(production_config, shadow_config)
        
        request = ShadowRequest(
            request_id="REQ_12345678",
            endpoint="/api/v1/test",
            method="GET"
        )
        
        result = client._make_production_request(request)
        
        assert result['data'] == {"data": "success"}
        assert result['status'] == 200
        assert 'time' in result
    
    @patch('tests.shadow.shadow_tester.requests.Session')
    def test_make_production_request_error(self, mock_session):
        """Testa requisição de produção com erro"""
        mock_session.return_value.request.side_effect = Exception("Connection error")
        
        production_config = {'base_url': 'https://prod.api.com', 'timeout': 30}
        shadow_config = {'base_url': 'https://shadow.api.com', 'timeout': 30}
        
        client = ShadowAPIClient(production_config, shadow_config)
        
        request = ShadowRequest(
            request_id="REQ_12345678",
            endpoint="/api/v1/test",
            method="GET"
        )
        
        with pytest.raises(Exception, match="Connection error"):
            client._make_production_request(request)
    
    @patch('tests.shadow.shadow_tester.requests.Session')
    def test_make_shadow_request_success(self, mock_session):
        """Testa requisição shadow com sucesso"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "shadow_success"}
        mock_response.status_code = 200
        mock_response.content = b'{"data": "shadow_success"}'
        
        mock_session.return_value.request.return_value = mock_response
        
        production_config = {'base_url': 'https://prod.api.com', 'timeout': 30}
        shadow_config = {'base_url': 'https://shadow.api.com', 'timeout': 30}
        
        client = ShadowAPIClient(production_config, shadow_config)
        
        request = ShadowRequest(
            request_id="REQ_12345678",
            endpoint="/api/v1/test",
            method="GET"
        )
        
        result = client._make_shadow_request(request)
        
        assert result['data'] == {"data": "shadow_success"}
        assert result['status'] == 200
        assert 'time' in result


class TestShadowTestGenerator:
    """Testes para ShadowTestGenerator"""
    
    def test_generator_initialization(self):
        """Testa inicialização do gerador"""
        generator = ShadowTestGenerator()
        
        assert len(generator.request_patterns) > 0
        assert all('endpoint' in pattern for pattern in generator.request_patterns)
        assert all('method' in pattern for pattern in generator.request_patterns)
    
    def test_generate_requests(self):
        """Testa geração de requisições"""
        generator = ShadowTestGenerator()
        requests = generator.generate_requests(count=10)
        
        assert len(requests) == 10
        assert all(isinstance(req, ShadowRequest) for req in requests)
        assert all(req.request_id.startswith('REQ_') for req in requests)
    
    def test_generate_requests_unique_ids(self):
        """Testa que IDs de requisição são únicos"""
        generator = ShadowTestGenerator()
        requests = generator.generate_requests(count=50)
        
        request_ids = [req.request_id for req in requests]
        assert len(request_ids) == len(set(request_ids))
    
    def test_vary_payload_string_variation(self):
        """Testa variação de payload com strings"""
        generator = ShadowTestGenerator()
        
        base_payload = {"query": "original query"}
        varied_payload = generator._vary_payload(base_payload)
        
        assert varied_payload["query"] != "original query"
        assert "test query" in varied_payload["query"]
    
    def test_vary_payload_list_variation(self):
        """Testa variação de payload com listas"""
        generator = ShadowTestGenerator()
        
        base_payload = {"metrics": ["impressions", "clicks", "conversions"]}
        varied_payload = generator._vary_payload(base_payload)
        
        assert len(varied_payload["metrics"]) == 2
        assert all(metric in ["impressions", "clicks", "conversions"] for metric in varied_payload["metrics"])
    
    def test_vary_payload_int_variation(self):
        """Testa variação de payload com inteiros"""
        generator = ShadowTestGenerator()
        
        base_payload = {"limit": 10}
        varied_payload = generator._vary_payload(base_payload)
        
        assert varied_payload["limit"] != 10
        assert 5 <= varied_payload["limit"] <= 50
    
    def test_vary_payload_none_input(self):
        """Testa variação de payload None"""
        generator = ShadowTestGenerator()
        
        result = generator._vary_payload(None)
        assert result is None


class TestRegressionDetector:
    """Testes para RegressionDetector"""
    
    def test_detector_initialization(self):
        """Testa inicialização do detector"""
        detector = RegressionDetector()
        
        assert len(detector.regression_patterns) > 0
        assert all(callable(pattern) for pattern in detector.regression_patterns)
    
    def test_detect_status_code_regression(self):
        """Testa detecção de regressão de status code"""
        detector = RegressionDetector()
        
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_status=200,
            shadow_status=500
        )
        
        assert detector._detect_status_code_regression(response) is True
    
    def test_detect_status_code_no_regression(self):
        """Testa que não detecta regressão quando shadow é melhor"""
        detector = RegressionDetector()
        
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_status=500,
            shadow_status=200
        )
        
        assert detector._detect_status_code_regression(response) is False
    
    def test_detect_error_regression(self):
        """Testa detecção de regressão de erro"""
        detector = RegressionDetector()
        
        response = ShadowResponse(
            request_id="REQ_12345678",
            shadow_error="Connection timeout"
        )
        
        assert detector._detect_error_regression(response) is True
    
    def test_detect_error_no_regression(self):
        """Testa que não detecta regressão quando ambos têm erro"""
        detector = RegressionDetector()
        
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_error="Connection timeout",
            shadow_error="Connection timeout"
        )
        
        assert detector._detect_error_regression(response) is False
    
    def test_detect_performance_regression(self):
        """Testa detecção de regressão de performance"""
        detector = RegressionDetector()
        
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_time=1.0,
            shadow_time=2.0  # 100% mais lento
        )
        
        assert detector._detect_performance_regression(response) is True
    
    def test_detect_performance_no_regression(self):
        """Testa que não detecta regressão de performance quando aceitável"""
        detector = RegressionDetector()
        
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_time=1.0,
            shadow_time=1.3  # 30% mais lento (aceitável)
        )
        
        assert detector._detect_performance_regression(response) is False
    
    def test_detect_data_structure_regression(self):
        """Testa detecção de regressão na estrutura de dados"""
        detector = RegressionDetector()
        
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_response={"field1": "value1", "field2": "value2"},
            shadow_response={"field1": "value1"}  # Perdeu field2
        )
        
        assert detector._detect_data_structure_regression(response) is True
    
    def test_detect_data_structure_no_regression(self):
        """Testa que não detecta regressão quando estruturas são iguais"""
        detector = RegressionDetector()
        
        response = ShadowResponse(
            request_id="REQ_12345678",
            production_response={"field1": "value1", "field2": "value2"},
            shadow_response={"field1": "value1", "field2": "value2"}
        )
        
        assert detector._detect_data_structure_regression(response) is False
    
    def test_detect_regressions_multiple_patterns(self):
        """Testa detecção de regressões com múltiplos padrões"""
        detector = RegressionDetector()
        
        responses = [
            ShadowResponse("REQ_1", production_status=200, shadow_status=500),  # Status regression
            ShadowResponse("REQ_2", shadow_error="Connection timeout"),  # Error regression
            ShadowResponse("REQ_3", production_time=1.0, shadow_time=2.0),  # Performance regression
            ShadowResponse("REQ_4", production_status=200, shadow_status=200)  # No regression
        ]
        
        regressions = detector.detect_regressions(responses)
        
        assert len(regressions) == 3
        assert all(resp.request_id in ["REQ_1", "REQ_2", "REQ_3"] for resp in regressions)


class TestShadowTester:
    """Testes para ShadowTester"""
    
    @patch('tests.shadow.shadow_tester.ShadowAPIClient')
    @patch('tests.shadow.shadow_tester.ShadowTestGenerator')
    def test_tester_initialization(self, mock_generator, mock_client):
        """Testa inicialização do tester"""
        production_config = {'base_url': 'https://prod.api.com'}
        shadow_config = {'base_url': 'https://shadow.api.com'}
        
        tester = ShadowTester(production_config, shadow_config)
        
        assert tester.production_config == production_config
        assert tester.shadow_config == shadow_config
        assert tester.client is not None
        assert tester.generator is not None
    
    @patch('tests.shadow.shadow_tester.ShadowAPIClient')
    @patch('tests.shadow.shadow_tester.ShadowTestGenerator')
    @patch('tests.shadow.shadow_tester.RegressionDetector')
    async def test_run_shadow_test_basic(self, mock_detector, mock_generator, mock_client):
        """Testa execução básica de shadow test"""
        # Mock do gerador
        mock_generator_instance = Mock()
        mock_generator_instance.generate_requests.return_value = [
            ShadowRequest("REQ_1", "/api/test", "GET"),
            ShadowRequest("REQ_2", "/api/test", "POST")
        ]
        mock_generator.return_value = mock_generator_instance
        
        # Mock do cliente
        mock_client_instance = Mock()
        mock_client_instance.make_request = AsyncMock(return_value=ShadowResponse("REQ_1"))
        mock_client.return_value = mock_client_instance
        
        # Mock do detector
        mock_detector_instance = Mock()
        mock_detector_instance.detect_regressions.return_value = []
        mock_detector.return_value = mock_detector_instance
        
        production_config = {'base_url': 'https://prod.api.com'}
        shadow_config = {'base_url': 'https://shadow.api.com'}
        
        tester = ShadowTester(production_config, shadow_config)
        
        result = await tester.run_shadow_test(request_count=2, concurrent_requests=1)
        
        assert result.total_requests == 2
        assert result.successful_requests == 2
        assert result.regressions_detected == 0
    
    def test_analyze_results_basic(self):
        """Testa análise básica de resultados"""
        production_config = {'base_url': 'https://prod.api.com'}
        shadow_config = {'base_url': 'https://shadow.api.com'}
        
        tester = ShadowTester(production_config, shadow_config)
        
        responses = [
            ShadowResponse("REQ_1", production_status=200, shadow_status=200, production_time=1.0, shadow_time=1.1),
            ShadowResponse("REQ_2", production_status=200, shadow_status=404, production_time=1.0, shadow_time=1.2)
        ]
        
        start_time = datetime.now()
        result = tester._analyze_results(responses, start_time)
        
        assert result.total_requests == 2
        assert result.successful_requests == 2
        assert result.matching_responses == 1
        assert result.avg_production_time == 1.0
        assert result.avg_shadow_time == 1.15
    
    def test_generate_report(self):
        """Testa geração de relatório"""
        with tempfile.TemporaryDirectory() as temp_dir:
            production_config = {'base_url': 'https://prod.api.com'}
            shadow_config = {'base_url': 'https://shadow.api.com'}
            
            tester = ShadowTester(production_config, shadow_config)
            
            responses = [
                ShadowResponse("REQ_1", production_status=200, shadow_status=200),
                ShadowResponse("REQ_2", production_status=200, shadow_status=404)
            ]
            
            result = ShadowTestResult(
                test_id="TEST_001",
                total_requests=2,
                successful_requests=2,
                failed_requests=0,
                matching_responses=1,
                regressions_detected=1,
                avg_production_time=1.0,
                avg_shadow_time=1.1,
                avg_performance_diff=0.1,
                start_time=datetime.now(),
                end_time=datetime.now(),
                responses=responses
            )
            
            output_file = Path(temp_dir) / "shadow_report.json"
            tester.generate_report(result, str(output_file))
            
            assert output_file.exists()
            
            # Verifica conteúdo do relatório
            with open(output_file, 'r') as f:
                report_data = json.load(f)
            
            assert report_data['summary']['total_requests'] == 2
            assert report_data['summary']['regressions_detected'] == 1
            assert len(report_data['regressions']) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 