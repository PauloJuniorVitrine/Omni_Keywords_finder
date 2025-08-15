"""
Testes unitários para ContractDriftPredictor
Tracing ID: ARCH-003
Prompt: INTEGRATION_EXTERNAL_CHECKLIST_V2.md
Ruleset: enterprise_control_layer.yaml
Data/Hora: 2024-12-20 01:30:00 UTC

Testes unitários abrangentes para o sistema de predição de drift de contratos.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Optional
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from scripts.ai.contract_drift_predictor import (
    ContractDriftPredictor,
    ContractAnalyzer,
    DriftPredictor,
    APIContract,
    APIChange,
    DriftPrediction,
    DriftReport,
    ChangeType,
    RiskLevel,
    DriftStatus
)


class TestAPIContract:
    """Testes para APIContract"""
    
    def test_api_contract_creation(self):
        """Testa criação de contrato de API"""
        contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={"/users": {"methods": ["GET"]}},
            schemas={"User": {"type": "object"}},
            headers={"Authorization": "Bearer"},
            authentication={"type": "bearer"},
            rate_limits={"requests_per_minute": 100}
        )
        
        assert contract.name == "test_api"
        assert contract.version == "1.0.0"
        assert contract.base_url == "https://api.test.com"
        assert len(contract.endpoints) == 1
        assert len(contract.schemas) == 1
        assert contract.hash is not None
    
    def test_api_contract_hash_consistency(self):
        """Testa consistência do hash do contrato"""
        contract1 = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        contract2 = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        assert contract1.hash == contract2.hash
    
    def test_api_contract_hash_different(self):
        """Testa que contratos diferentes têm hashes diferentes"""
        contract1 = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        contract2 = APIContract(
            name="test_api",
            version="1.1.0",  # Versão diferente
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        assert contract1.hash != contract2.hash


class TestAPIChange:
    """Testes para APIChange"""
    
    def test_api_change_creation(self):
        """Testa criação de mudança de API"""
        change = APIChange(
            change_type=ChangeType.REMOVAL,
            risk_level=RiskLevel.CRITICAL,
            endpoint="/users",
            description="Endpoint removido",
            impact_analysis="Integrações irão falhar",
            recommendations=["Implementar fallback"],
            confidence=0.9
        )
        
        assert change.change_type == ChangeType.REMOVAL
        assert change.risk_level == RiskLevel.CRITICAL
        assert change.endpoint == "/users"
        assert change.confidence == 0.9
        assert len(change.recommendations) == 1


class TestContractAnalyzer:
    """Testes para ContractAnalyzer"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.analyzer = ContractAnalyzer()
    
    def test_analyzer_initialization(self):
        """Testa inicialização do analisador"""
        config = {
            "breaking_patterns": [r"value\data+\.0\.0"],
            "warning_patterns": [r"value\data+\.\data+\.0"]
        }
        analyzer = ContractAnalyzer(config)
        
        assert len(analyzer.breaking_patterns) == 1
        assert len(analyzer.warning_patterns) == 1
    
    def test_analyze_endpoint_removal(self):
        """Testa análise de remoção de endpoint"""
        old_contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={"/users": {"methods": ["GET"]}},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        new_contract = APIContract(
            name="test_api",
            version="1.1.0",
            base_url="https://api.test.com",
            endpoints={},  # Endpoint removido
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        changes = self.analyzer.analyze_contract_changes(old_contract, new_contract)
        
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.REMOVAL
        assert changes[0].risk_level == RiskLevel.CRITICAL
        assert changes[0].endpoint == "/users"
    
    def test_analyze_endpoint_addition(self):
        """Testa análise de adição de endpoint"""
        old_contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        new_contract = APIContract(
            name="test_api",
            version="1.1.0",
            base_url="https://api.test.com",
            endpoints={"/users": {"methods": ["GET"]}},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        changes = self.analyzer.analyze_contract_changes(old_contract, new_contract)
        
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.ADDITION
        assert changes[0].risk_level == RiskLevel.LOW
        assert changes[0].endpoint == "/users"
    
    def test_analyze_schema_changes(self):
        """Testa análise de mudanças em schemas"""
        old_contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={
                "User": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {"id": {"type": "integer"}}
                }
            },
            headers={},
            authentication={},
            rate_limits={}
        )
        
        new_contract = APIContract(
            name="test_api",
            version="1.1.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={
                "User": {
                    "type": "object",
                    "required": ["id", "name"],  # Campo obrigatório adicionado
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    }
                }
            },
            headers={},
            authentication={},
            rate_limits={}
        )
        
        changes = self.analyzer.analyze_contract_changes(old_contract, new_contract)
        
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.MODIFICATION
        assert changes[0].risk_level == RiskLevel.HIGH
        assert "required" in changes[0].field
    
    def test_analyze_auth_changes(self):
        """Testa análise de mudanças em autenticação"""
        old_contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={"type": "bearer"},
            rate_limits={}
        )
        
        new_contract = APIContract(
            name="test_api",
            version="1.1.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={"type": "api_key"},  # Mudança de autenticação
            rate_limits={}
        )
        
        changes = self.analyzer.analyze_contract_changes(old_contract, new_contract)
        
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.MODIFICATION
        assert changes[0].risk_level == RiskLevel.CRITICAL
        assert changes[0].field == "authentication"


class TestDriftPredictor:
    """Testes para DriftPredictor"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.predictor = DriftPredictor()
    
    def test_predictor_initialization(self):
        """Testa inicialização do preditor"""
        config = {
            "confidence_threshold": 0.8,
            "prediction_horizon": 60
        }
        predictor = DriftPredictor(config)
        
        assert predictor.confidence_threshold == 0.8
        assert predictor.prediction_horizon == 60
    
    def test_add_historical_data(self):
        """Testa adição de dados históricos"""
        contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        changes = [
            APIChange(
                change_type=ChangeType.REMOVAL,
                risk_level=RiskLevel.CRITICAL,
                description="Test change"
            )
        ]
        
        self.predictor.add_historical_data(contract, changes)
        
        assert len(self.predictor.historical_data) == 1
        assert self.predictor.historical_data[0]["contract"] == contract
        assert self.predictor.historical_data[0]["changes"] == changes
    
    def test_analyze_change_patterns_insufficient_data(self):
        """Testa análise de padrões com dados insuficientes"""
        patterns = self.predictor.analyze_change_patterns()
        
        assert "error" in patterns
        assert "Dados históricos insuficientes" in patterns["error"]
    
    def test_analyze_change_patterns_with_data(self):
        """Testa análise de padrões com dados"""
        # Adicionar dados históricos
        contract1 = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        contract2 = APIContract(
            name="test_api",
            version="1.1.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        changes1 = [
            APIChange(
                change_type=ChangeType.ADDITION,
                risk_level=RiskLevel.LOW,
                description="Change 1"
            )
        ]
        
        changes2 = [
            APIChange(
                change_type=ChangeType.REMOVAL,
                risk_level=RiskLevel.CRITICAL,
                description="Change 2"
            )
        ]
        
        self.predictor.add_historical_data(contract1, changes1)
        self.predictor.add_historical_data(contract2, changes2)
        
        patterns = self.predictor.analyze_change_patterns()
        
        assert "change_frequency" in patterns
        assert "risk_distribution" in patterns
        assert patterns["change_frequency"]["total_changes"] == 2
        assert patterns["risk_distribution"]["critical"] == 1
        assert patterns["risk_distribution"]["low"] == 1
    
    def test_predict_drift_insufficient_data(self):
        """Testa predição com dados insuficientes"""
        contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        prediction = self.predictor.predict_drift(contract)
        
        assert prediction.confidence_score == 0.0
        assert prediction.risk_score == 0.0
        assert "Dados históricos insuficientes" in prediction.impact_analysis
    
    def test_predict_drift_with_data(self):
        """Testa predição com dados históricos"""
        # Adicionar dados históricos
        contract1 = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        contract2 = APIContract(
            name="test_api",
            version="1.1.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        changes = [
            APIChange(
                change_type=ChangeType.ADDITION,
                risk_level=RiskLevel.LOW,
                description="Test change"
            )
        ]
        
        self.predictor.add_historical_data(contract1, changes)
        self.predictor.add_historical_data(contract2, changes)
        
        current_contract = APIContract(
            name="test_api",
            version="1.2.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        prediction = self.predictor.predict_drift(current_contract)
        
        assert prediction.api_name == "test_api"
        assert prediction.current_version == "1.2.0"
        assert prediction.confidence_score > 0.0
        assert len(prediction.recommendations) > 0


class TestContractDriftPredictor:
    """Testes para ContractDriftPredictor"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.predictor = ContractDriftPredictor()
    
    def test_predictor_initialization(self):
        """Testa inicialização do preditor principal"""
        config = {
            "analyzer": {"breaking_patterns": [r"value\data+\.0\.0"]},
            "predictor": {"confidence_threshold": 0.8}
        }
        predictor = ContractDriftPredictor(config)
        
        assert predictor.analyzer is not None
        assert predictor.predictor is not None
    
    async def test_analyze_api_contract(self):
        """Testa análise de contrato de API"""
        contract_data = {
            "version": "1.0.0",
            "base_url": "https://api.test.com",
            "endpoints": {"/users": {"methods": ["GET"]}},
            "schemas": {"User": {"type": "object"}},
            "headers": {"Authorization": "Bearer"},
            "authentication": {"type": "bearer"},
            "rate_limits": {"requests_per_minute": 100}
        }
        
        contract = await self.predictor.analyze_api_contract("test_api", contract_data)
        
        assert contract.name == "test_api"
        assert contract.version == "1.0.0"
        assert contract.base_url == "https://api.test.com"
        assert len(contract.endpoints) == 1
        assert contract.hash is not None
    
    async def test_detect_changes_first_analysis(self):
        """Testa detecção de mudanças na primeira análise"""
        contract_data = {
            "version": "1.0.0",
            "base_url": "https://api.test.com",
            "endpoints": {},
            "schemas": {},
            "headers": {},
            "authentication": {},
            "rate_limits": {}
        }
        
        contract = await self.predictor.analyze_api_contract("test_api", contract_data)
        changes = await self.predictor.detect_changes("test_api", contract)
        
        assert len(changes) == 0  # Primeira análise não detecta mudanças
    
    async def test_detect_changes_with_differences(self):
        """Testa detecção de mudanças com diferenças"""
        # Primeiro contrato
        old_contract_data = {
            "version": "1.0.0",
            "base_url": "https://api.test.com",
            "endpoints": {"/users": {"methods": ["GET"]}},
            "schemas": {},
            "headers": {},
            "authentication": {},
            "rate_limits": {}
        }
        
        old_contract = await self.predictor.analyze_api_contract("test_api", old_contract_data)
        await self.predictor.detect_changes("test_api", old_contract)
        
        # Segundo contrato com mudanças
        new_contract_data = {
            "version": "1.1.0",
            "base_url": "https://api.test.com",
            "endpoints": {},  # Endpoint removido
            "schemas": {},
            "headers": {},
            "authentication": {},
            "rate_limits": {}
        }
        
        new_contract = await self.predictor.analyze_api_contract("test_api", new_contract_data)
        changes = await self.predictor.detect_changes("test_api", new_contract)
        
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.REMOVAL
        assert changes[0].risk_level == RiskLevel.CRITICAL
    
    async def test_predict_drift_no_history(self):
        """Testa predição de drift sem histórico"""
        prediction = await self.predictor.predict_drift("test_api")
        
        assert prediction.api_name == "test_api"
        assert prediction.confidence_score == 0.0
        assert "Dados insuficientes" in prediction.impact_analysis
    
    async def test_predict_drift_with_history(self):
        """Testa predição de drift com histórico"""
        # Adicionar dados históricos
        contract_data = {
            "version": "1.0.0",
            "base_url": "https://api.test.com",
            "endpoints": {},
            "schemas": {},
            "headers": {},
            "authentication": {},
            "rate_limits": {}
        }
        
        contract = await self.predictor.analyze_api_contract("test_api", contract_data)
        await self.predictor.detect_changes("test_api", contract)
        
        prediction = await self.predictor.predict_drift("test_api")
        
        assert prediction.api_name == "test_api"
        assert prediction.current_version == "1.0.0"
        assert len(prediction.recommendations) > 0
    
    async def test_generate_drift_report(self):
        """Testa geração de relatório de drift"""
        # Adicionar dados históricos
        contract_data = {
            "version": "1.0.0",
            "base_url": "https://api.test.com",
            "endpoints": {},
            "schemas": {},
            "headers": {},
            "authentication": {},
            "rate_limits": {}
        }
        
        contract = await self.predictor.analyze_api_contract("test_api", contract_data)
        await self.predictor.detect_changes("test_api", contract)
        
        report = await self.predictor.generate_drift_report("test_api")
        
        assert report.api_name == "test_api"
        assert report.current_contract is not None
        assert report.overall_risk in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert 0.0 <= report.stability_score <= 1.0
        assert len(report.recommendations) > 0
    
    async def test_generate_drift_report_no_contract(self):
        """Testa geração de relatório sem contrato"""
        with pytest.raises(ValueError, match="Contrato não encontrado"):
            await self.predictor.generate_drift_report("nonexistent_api")
    
    def test_get_historical_analysis(self):
        """Testa obtenção de análise histórica"""
        # Adicionar contrato ao histórico
        contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        self.predictor.contracts_history["test_api"] = contract
        
        analysis = self.predictor.get_historical_analysis("test_api")
        
        assert analysis["api_name"] == "test_api"
        assert analysis["current_version"] == "1.0.0"
        assert "patterns" in analysis
    
    def test_get_historical_analysis_no_api(self):
        """Testa obtenção de análise histórica sem API"""
        analysis = self.predictor.get_historical_analysis("nonexistent_api")
        
        assert "error" in analysis
        assert "API não encontrada" in analysis["error"]


class TestConvenienceFunctions:
    """Testes para funções de conveniência"""
    
    async def test_create_drift_predictor(self):
        """Testa função de conveniência create_drift_predictor"""
        config = {"test": "config"}
        predictor = await create_drift_predictor(config)
        
        assert isinstance(predictor, ContractDriftPredictor)
        assert predictor.config == config
    
    async def test_analyze_api_changes(self):
        """Testa função de conveniência analyze_api_changes"""
        old_contract = {
            "version": "1.0.0",
            "base_url": "https://api.test.com",
            "endpoints": {"/users": {"methods": ["GET"]}},
            "schemas": {},
            "headers": {},
            "authentication": {},
            "rate_limits": {}
        }
        
        new_contract = {
            "version": "1.1.0",
            "base_url": "https://api.test.com",
            "endpoints": {},  # Endpoint removido
            "schemas": {},
            "headers": {},
            "authentication": {},
            "rate_limits": {}
        }
        
        changes = await analyze_api_changes("test_api", old_contract, new_contract)
        
        assert len(changes) == 1
        assert changes[0].change_type == ChangeType.REMOVAL
        assert changes[0].risk_level == RiskLevel.CRITICAL
    
    async def test_predict_api_drift(self):
        """Testa função de conveniência predict_api_drift"""
        contract_data = {
            "version": "1.0.0",
            "base_url": "https://api.test.com",
            "endpoints": {},
            "schemas": {},
            "headers": {},
            "authentication": {},
            "rate_limits": {}
        }
        
        prediction = await predict_api_drift("test_api", contract_data)
        
        assert prediction.api_name == "test_api"
        assert prediction.current_version == "1.0.0"
        assert len(prediction.recommendations) > 0


class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_contract_analyzer_empty_contracts(self):
        """Testa análise com contratos vazios"""
        analyzer = ContractAnalyzer()
        
        empty_contract = APIContract(
            name="test_api",
            version="1.0.0",
            base_url="",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        changes = analyzer.analyze_contract_changes(empty_contract, empty_contract)
        assert len(changes) == 0
    
    def test_drift_predictor_invalid_version(self):
        """Testa preditor com versão inválida"""
        predictor = DriftPredictor()
        
        contract = APIContract(
            name="test_api",
            version="invalid_version",
            base_url="https://api.test.com",
            endpoints={},
            schemas={},
            headers={},
            authentication={},
            rate_limits={}
        )
        
        # Adicionar dados históricos
        predictor.add_historical_data(contract, [])
        
        prediction = predictor.predict_drift(contract)
        assert prediction.predicted_version == "invalid_version+1"


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 