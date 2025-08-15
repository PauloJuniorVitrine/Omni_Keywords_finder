from typing import Dict, List, Optional, Any
"""
Testes Unitários para Chaos Engineering Engine
Tracing ID: TEST-003
Data: 2024-12-20
Versão: 1.0
"""

import pytest
import asyncio
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from tests.chaos.chaos_engine import (
    ChaosType,
    ChaosSeverity,
    ChaosScenario,
    ChaosResult,
    ChaosReport,
    ChaosInjector,
    ChaosAPIClient,
    ChaosEngine
)


class TestChaosType:
    """Testes para enum ChaosType"""
    
    def test_chaos_type_values(self):
        """Testa valores do enum ChaosType"""
        assert ChaosType.TIMEOUT.value == "timeout"
        assert ChaosType.CONNECTION_ERROR.value == "connection_error"
        assert ChaosType.HTTP_ERROR.value == "http_error"
        assert ChaosType.SSL_ERROR.value == "ssl_error"
        assert ChaosType.DNS_ERROR.value == "dns_error"
        assert ChaosType.RATE_LIMIT.value == "rate_limit"
        assert ChaosType.TOKEN_EXPIRED.value == "token_expired"
        assert ChaosType.SERVICE_UNAVAILABLE.value == "service_unavailable"
        assert ChaosType.SLOW_RESPONSE.value == "slow_response"
        assert ChaosType.PARTIAL_RESPONSE.value == "partial_response"


class TestChaosSeverity:
    """Testes para enum ChaosSeverity"""
    
    def test_chaos_severity_values(self):
        """Testa valores do enum ChaosSeverity"""
        assert ChaosSeverity.LOW.value == "low"
        assert ChaosSeverity.MEDIUM.value == "medium"
        assert ChaosSeverity.HIGH.value == "high"
        assert ChaosSeverity.CRITICAL.value == "critical"


class TestChaosScenario:
    """Testes para ChaosScenario"""
    
    def test_chaos_scenario_creation(self):
        """Testa criação de ChaosScenario"""
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test Scenario",
            description="Test description",
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.MEDIUM,
            probability=0.5,
            duration=60,
            parameters={"timeout": 30},
            target_endpoints=["/api/test"],
            enabled=True
        )
        
        assert scenario.scenario_id == "TEST_001"
        assert scenario.name == "Test Scenario"
        assert scenario.chaos_type == ChaosType.TIMEOUT
        assert scenario.severity == ChaosSeverity.MEDIUM
        assert scenario.probability == 0.5
        assert scenario.duration == 60
        assert scenario.parameters == {"timeout": 30}
        assert scenario.target_endpoints == ["/api/test"]
        assert scenario.enabled is True
    
    def test_chaos_scenario_defaults(self):
        """Testa valores padrão de ChaosScenario"""
        scenario = ChaosScenario(
            scenario_id="TEST_002",
            name="Test Scenario",
            description="Test description",
            chaos_type=ChaosType.HTTP_ERROR,
            severity=ChaosSeverity.HIGH,
            probability=0.3
        )
        
        assert scenario.duration is None
        assert scenario.parameters == {}
        assert scenario.target_endpoints == []
        assert scenario.enabled is True


class TestChaosResult:
    """Testes para ChaosResult"""
    
    def test_chaos_result_creation(self):
        """Testa criação de ChaosResult"""
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=5)
        
        result = ChaosResult(
            scenario_id="TEST_001",
            start_time=start_time,
            end_time=end_time,
            success=True,
            error_message=None,
            affected_requests=1,
            recovery_time=5.0,
            metrics={"status_code": 200}
        )
        
        assert result.scenario_id == "TEST_001"
        assert result.start_time == start_time
        assert result.end_time == end_time
        assert result.success is True
        assert result.error_message is None
        assert result.affected_requests == 1
        assert result.recovery_time == 5.0
        assert result.metrics == {"status_code": 200}
    
    def test_chaos_result_defaults(self):
        """Testa valores padrão de ChaosResult"""
        start_time = datetime.now()
        
        result = ChaosResult(
            scenario_id="TEST_002",
            start_time=start_time
        )
        
        assert result.end_time is None
        assert result.success is False
        assert result.error_message is None
        assert result.affected_requests == 0
        assert result.recovery_time is None
        assert result.metrics == {}


class TestChaosReport:
    """Testes para ChaosReport"""
    
    def test_chaos_report_creation(self):
        """Testa criação de ChaosReport"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=5)
        
        results = [
            ChaosResult("TEST_1", start_time, success=True),
            ChaosResult("TEST_2", start_time, success=False)
        ]
        
        report = ChaosReport(
            test_id="CHAOS_20241220_120000",
            start_time=start_time,
            end_time=end_time,
            total_scenarios=5,
            executed_scenarios=2,
            successful_scenarios=1,
            failed_scenarios=1,
            total_affected_requests=2,
            avg_recovery_time=2.5,
            resilience_score=0.8,
            results=results
        )
        
        assert report.test_id == "CHAOS_20241220_120000"
        assert report.total_scenarios == 5
        assert report.executed_scenarios == 2
        assert report.successful_scenarios == 1
        assert report.failed_scenarios == 1
        assert report.total_affected_requests == 2
        assert report.avg_recovery_time == 2.5
        assert report.resilience_score == 0.8
        assert len(report.results) == 2
    
    def test_success_rate_calculation(self):
        """Testa cálculo da taxa de sucesso"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=1)
        
        results = [
            ChaosResult("TEST_1", start_time, success=True),
            ChaosResult("TEST_2", start_time, success=True),
            ChaosResult("TEST_3", start_time, success=False)
        ]
        
        report = ChaosReport(
            test_id="TEST",
            start_time=start_time,
            end_time=end_time,
            total_scenarios=3,
            executed_scenarios=3,
            successful_scenarios=2,
            failed_scenarios=1,
            total_affected_requests=3,
            avg_recovery_time=1.0,
            resilience_score=0.67,
            results=results
        )
        
        assert report.success_rate == 2/3
        assert report.success_rate == 0.6666666666666666
    
    def test_success_rate_zero_executions(self):
        """Testa taxa de sucesso com zero execuções"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=1)
        
        report = ChaosReport(
            test_id="TEST",
            start_time=start_time,
            end_time=end_time,
            total_scenarios=5,
            executed_scenarios=0,
            successful_scenarios=0,
            failed_scenarios=0,
            total_affected_requests=0,
            avg_recovery_time=0.0,
            resilience_score=0.0,
            results=[]
        )
        
        assert report.success_rate == 0.0
    
    def test_impact_score_calculation(self):
        """Testa cálculo do score de impacto"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=1)
        
        report = ChaosReport(
            test_id="TEST",
            start_time=start_time,
            end_time=end_time,
            total_scenarios=5,
            executed_scenarios=10,
            successful_scenarios=8,
            failed_scenarios=2,
            total_affected_requests=500,
            avg_recovery_time=1.0,
            resilience_score=0.8,
            results=[]
        )
        
        assert report.impact_score == 0.5  # 500/1000 = 0.5
    
    def test_impact_score_maximum(self):
        """Testa score de impacto máximo"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=1)
        
        report = ChaosReport(
            test_id="TEST",
            start_time=start_time,
            end_time=end_time,
            total_scenarios=5,
            executed_scenarios=10,
            successful_scenarios=8,
            failed_scenarios=2,
            total_affected_requests=2000,  # Acima do limite
            avg_recovery_time=1.0,
            resilience_score=0.8,
            results=[]
        )
        
        assert report.impact_score == 1.0  # Máximo normalizado


class TestChaosInjector:
    """Testes para ChaosInjector"""
    
    def test_injector_initialization(self):
        """Testa inicialização do injector"""
        injector = ChaosInjector()
        
        assert len(injector.active_scenarios) == 0
        assert len(injector.injection_hooks) > 0
        assert all(chaos_type in injector.injection_hooks for chaos_type in ChaosType)
    
    def test_inject_chaos_disabled_scenario(self):
        """Testa injeção com cenário desabilitado"""
        injector = ChaosInjector()
        
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0,
            enabled=False
        )
        
        request_data = {"endpoint": "/api/test", "method": "GET"}
        result = injector.inject_chaos(scenario, request_data)
        
        assert result == request_data  # Não modificado
    
    def test_inject_chaos_low_probability(self):
        """Testa injeção com baixa probabilidade"""
        injector = ChaosInjector()
        
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.MEDIUM,
            probability=0.0  # Zero probabilidade
        )
        
        request_data = {"endpoint": "/api/test", "method": "GET"}
        result = injector.inject_chaos(scenario, request_data)
        
        assert result == request_data  # Não modificado
    
    def test_inject_chaos_target_endpoint_mismatch(self):
        """Testa injeção com endpoint não alvo"""
        injector = ChaosInjector()
        
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0,
            target_endpoints=["/api/specific"]
        )
        
        request_data = {"endpoint": "/api/different", "method": "GET"}
        result = injector.inject_chaos(scenario, request_data)
        
        assert result == request_data  # Não modificado
    
    def test_inject_timeout(self):
        """Testa injeção de timeout"""
        injector = ChaosInjector()
        
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0,
            parameters={"timeout": 5}
        )
        
        request_data = {"endpoint": "/api/test", "method": "GET"}
        result = injector._inject_timeout(scenario, request_data)
        
        assert result["timeout"] == 5
        assert result["_chaos_injected"] is True
        assert result["_chaos_type"] == "timeout"
    
    def test_inject_connection_error(self):
        """Testa injeção de erro de conexão"""
        injector = ChaosInjector()
        
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.CONNECTION_ERROR,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0
        )
        
        request_data = {"endpoint": "/api/test", "method": "GET"}
        result = injector._inject_connection_error(scenario, request_data)
        
        assert result["_chaos_injected"] is True
        assert result["_chaos_type"] == "connection_error"
        assert isinstance(result["_chaos_raise"], ConnectionError)
    
    def test_inject_http_error(self):
        """Testa injeção de erro HTTP"""
        injector = ChaosInjector()
        
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.HTTP_ERROR,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0,
            parameters={"status_codes": [500, 502]}
        )
        
        request_data = {"endpoint": "/api/test", "method": "GET"}
        result = injector._inject_http_error(scenario, request_data)
        
        assert result["_chaos_injected"] is True
        assert result["_chaos_type"] == "http_error"
        assert result["_chaos_status_code"] in [500, 502]
    
    def test_inject_rate_limit(self):
        """Testa injeção de rate limit"""
        injector = ChaosInjector()
        
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.RATE_LIMIT,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0
        )
        
        request_data = {"endpoint": "/api/test", "method": "GET"}
        result = injector._inject_rate_limit(scenario, request_data)
        
        assert result["_chaos_injected"] is True
        assert result["_chaos_type"] == "rate_limit"
        assert result["_chaos_status_code"] == 429
        assert result["_chaos_headers"]["Retry-After"] == "60"
    
    def test_inject_slow_response(self):
        """Testa injeção de resposta lenta"""
        injector = ChaosInjector()
        
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.SLOW_RESPONSE,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0,
            parameters={"delay": 3.0}
        )
        
        request_data = {"endpoint": "/api/test", "method": "GET"}
        result = injector._inject_slow_response(scenario, request_data)
        
        assert result["_chaos_injected"] is True
        assert result["_chaos_type"] == "slow_response"
        assert result["_chaos_delay"] == 3.0


class TestChaosAPIClient:
    """Testes para ChaosAPIClient"""
    
    def test_client_initialization(self):
        """Testa inicialização do cliente"""
        injector = ChaosInjector()
        client = ChaosAPIClient("https://api.example.com", injector)
        
        assert client.base_url == "https://api.example.com"
        assert client.injector == injector
        assert client.session is not None
        assert client.request_count == 0
        assert client.error_count == 0
    
    @patch('tests.chaos.chaos_engine.requests.Session')
    def test_handle_chaos_request_timeout(self, mock_session):
        """Testa requisição com caos de timeout"""
        injector = ChaosInjector()
        client = ChaosAPIClient("https://api.example.com", injector)
        
        request_data = {
            "endpoint": "/api/test",
            "method": "GET",
            "_chaos_injected": True,
            "_chaos_type": "timeout",
            "timeout": 5
        }
        
        result = client._handle_chaos_request(request_data)
        
        assert result["chaos_injected"] is True
        assert result["chaos_type"] == "timeout"
    
    @patch('tests.chaos.chaos_engine.requests.Session')
    def test_handle_chaos_request_connection_error(self, mock_session):
        """Testa requisição com caos de erro de conexão"""
        injector = ChaosInjector()
        client = ChaosAPIClient("https://api.example.com", injector)
        
        request_data = {
            "endpoint": "/api/test",
            "method": "GET",
            "_chaos_injected": True,
            "_chaos_type": "connection_error",
            "_chaos_raise": ConnectionError("Connection refused")
        }
        
        with pytest.raises(ConnectionError, match="Connection refused"):
            client._handle_chaos_request(request_data)
    
    @patch('tests.chaos.chaos_engine.requests.Session')
    def test_handle_chaos_request_http_error(self, mock_session):
        """Testa requisição com caos de erro HTTP"""
        injector = ChaosInjector()
        client = ChaosAPIClient("https://api.example.com", injector)
        
        request_data = {
            "endpoint": "/api/test",
            "method": "GET",
            "_chaos_injected": True,
            "_chaos_type": "http_error",
            "_chaos_status_code": 500
        }
        
        result = client._handle_chaos_request(request_data)
        
        assert result["success"] is False
        assert result["status_code"] == 500
        assert result["chaos_injected"] is True
        assert result["chaos_type"] == "http_error"
    
    @patch('tests.chaos.chaos_engine.requests.Session')
    def test_handle_chaos_request_partial_response(self, mock_session):
        """Testa requisição com caos de resposta parcial"""
        injector = ChaosInjector()
        client = ChaosAPIClient("https://api.example.com", injector)
        
        request_data = {
            "endpoint": "/api/test",
            "method": "GET",
            "_chaos_injected": True,
            "_chaos_type": "partial_response",
            "_chaos_partial": True
        }
        
        result = client._handle_chaos_request(request_data)
        
        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["data"]["partial"] is True
        assert result["chaos_injected"] is True
        assert result["chaos_type"] == "partial_response"


class TestChaosEngine:
    """Testes para ChaosEngine"""
    
    def test_engine_initialization(self):
        """Testa inicialização do engine"""
        engine = ChaosEngine("https://api.example.com")
        
        assert engine.base_url == "https://api.example.com"
        assert engine.injector is not None
        assert engine.client is not None
        assert len(engine.scenarios) > 0  # Cenários padrão carregados
        assert len(engine.results) == 0
    
    def test_add_scenario(self):
        """Testa adição de cenário"""
        engine = ChaosEngine("https://api.example.com")
        
        scenario = ChaosScenario(
            scenario_id="CUSTOM_001",
            name="Custom Scenario",
            description="Custom description",
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.HIGH,
            probability=0.5
        )
        
        engine.add_scenario(scenario)
        
        assert "CUSTOM_001" in engine.scenarios
        assert engine.scenarios["CUSTOM_001"] == scenario
    
    def test_enable_scenario(self):
        """Testa habilitação de cenário"""
        engine = ChaosEngine("https://api.example.com")
        
        # Adiciona cenário
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0
        )
        engine.add_scenario(scenario)
        
        # Habilita cenário
        engine.enable_scenario("TEST_001")
        
        assert "TEST_001" in engine.injector.active_scenarios
        assert engine.injector.active_scenarios["TEST_001"] == scenario
    
    def test_disable_scenario(self):
        """Testa desabilitação de cenário"""
        engine = ChaosEngine("https://api.example.com")
        
        # Adiciona e habilita cenário
        scenario = ChaosScenario(
            scenario_id="TEST_001",
            name="Test",
            description="Test",
            chaos_type=ChaosType.TIMEOUT,
            severity=ChaosSeverity.MEDIUM,
            probability=1.0
        )
        engine.add_scenario(scenario)
        engine.enable_scenario("TEST_001")
        
        # Desabilita cenário
        engine.disable_scenario("TEST_001")
        
        assert "TEST_001" not in engine.injector.active_scenarios
    
    def test_calculate_resilience_score_perfect(self):
        """Testa cálculo de score de resiliência perfeito"""
        engine = ChaosEngine("https://api.example.com")
        
        # Resultados perfeitos
        results = [
            ChaosResult("TEST_1", datetime.now(), success=True, recovery_time=1.0),
            ChaosResult("TEST_2", datetime.now(), success=True, recovery_time=1.0),
            ChaosResult("TEST_3", datetime.now(), success=True, recovery_time=1.0)
        ]
        
        score = engine._calculate_resilience_score(results)
        
        assert score == 1.0  # Score perfeito
    
    def test_calculate_resilience_score_poor(self):
        """Testa cálculo de score de resiliência ruim"""
        engine = ChaosEngine("https://api.example.com")
        
        # Resultados ruins
        results = [
            ChaosResult("TEST_1", datetime.now(), success=False, recovery_time=15.0),
            ChaosResult("TEST_2", datetime.now(), success=False, recovery_time=20.0),
            ChaosResult("TEST_3", datetime.now(), success=False, recovery_time=25.0)
        ]
        
        score = engine._calculate_resilience_score(results)
        
        assert score < 0.5  # Score baixo
    
    def test_generate_report(self):
        """Testa geração de relatório"""
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = ChaosEngine("https://api.example.com")
            
            # Cria cenário
            scenario = ChaosScenario(
                scenario_id="TEST_001",
                name="Test",
                description="Test",
                chaos_type=ChaosType.TIMEOUT,
                severity=ChaosSeverity.MEDIUM,
                probability=1.0
            )
            engine.add_scenario(scenario)
            
            # Cria resultado
            result = ChaosResult(
                scenario_id="TEST_001",
                start_time=datetime.now(),
                success=True,
                recovery_time=1.0
            )
            
            # Cria relatório
            report = ChaosReport(
                test_id="TEST_001",
                start_time=datetime.now(),
                end_time=datetime.now(),
                total_scenarios=1,
                executed_scenarios=1,
                successful_scenarios=1,
                failed_scenarios=0,
                total_affected_requests=1,
                avg_recovery_time=1.0,
                resilience_score=1.0,
                results=[result]
            )
            
            output_file = Path(temp_dir) / "chaos_report.json"
            engine.generate_report(report, str(output_file))
            
            assert output_file.exists()
            
            # Verifica conteúdo do relatório
            with open(output_file, 'r') as f:
                report_data = json.load(f)
            
            assert report_data['summary']['test_id'] == "TEST_001"
            assert report_data['summary']['total_scenarios'] == 1
            assert len(report_data['scenarios']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 