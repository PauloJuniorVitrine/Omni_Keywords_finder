from typing import Dict, List, Optional, Any
"""
Testes unitários para Data Sensitivity Matrix
Tracing ID: METRICS-002
Data/Hora: 2024-12-20 02:00:00 UTC
Versão: 1.0
Status: IMPLEMENTAÇÃO INICIAL

20 testes unitários abrangentes para validar o sistema de matriz de sensibilidade
de dados e compliance com regulamentações.
"""

import pytest
import json
import re
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import redis

from scripts.security.data_sensitivity import (
    DataSensitivityMatrix,
    DataField,
    IntegrationDataMap,
    ComplianceReport,
    DataSensitivityLevel,
    DataCategory,
    classify_field_sensitivity,
    create_integration_data_map,
    scan_data_for_sensitive_content,
    generate_compliance_report
)


class TestDataSensitivityLevel:
    """Testes para níveis de sensibilidade"""
    
    def test_sensitivity_levels(self):
        """Testa todos os níveis de sensibilidade"""
        levels = list(DataSensitivityLevel)
        
        assert DataSensitivityLevel.PUBLIC in levels
        assert DataSensitivityLevel.INTERNAL in levels
        assert DataSensitivityLevel.CONFIDENTIAL in levels
        assert DataSensitivityLevel.RESTRICTED in levels
        assert DataSensitivityLevel.HIGHLY_SENSITIVE in levels
    
    def test_sensitivity_level_values(self):
        """Testa valores dos níveis de sensibilidade"""
        assert DataSensitivityLevel.PUBLIC.value == "public"
        assert DataSensitivityLevel.INTERNAL.value == "internal"
        assert DataSensitivityLevel.CONFIDENTIAL.value == "confidential"
        assert DataSensitivityLevel.RESTRICTED.value == "restricted"
        assert DataSensitivityLevel.HIGHLY_SENSITIVE.value == "highly_sensitive"


class TestDataCategory:
    """Testes para categorias de dados"""
    
    def test_data_categories(self):
        """Testa todas as categorias de dados"""
        categories = list(DataCategory)
        
        assert DataCategory.PERSONAL_INFO in categories
        assert DataCategory.FINANCIAL in categories
        assert DataCategory.HEALTH in categories
        assert DataCategory.LEGAL in categories
        assert DataCategory.TECHNICAL in categories
        assert DataCategory.BUSINESS in categories
        assert DataCategory.AUTHENTICATION in categories
    
    def test_data_category_values(self):
        """Testa valores das categorias de dados"""
        assert DataCategory.PERSONAL_INFO.value == "personal_info"
        assert DataCategory.FINANCIAL.value == "financial"
        assert DataCategory.HEALTH.value == "health"
        assert DataCategory.LEGAL.value == "legal"
        assert DataCategory.TECHNICAL.value == "technical"
        assert DataCategory.BUSINESS.value == "business"
        assert DataCategory.AUTHENTICATION.value == "authentication"


class TestDataField:
    """Testes para campos de dados"""
    
    def test_data_field_creation(self):
        """Testa criação de campo de dados"""
        field = DataField(
            field_name="user_email",
            field_path="user.personal.email",
            sensitivity_level=DataSensitivityLevel.CONFIDENTIAL,
            category=DataCategory.PERSONAL_INFO,
            description="Email do usuário",
            encryption_required=True,
            retention_days=1095,
            compliance_frameworks=['lgpd', 'gdpr']
        )
        
        assert field.field_name == "user_email"
        assert field.field_path == "user.personal.email"
        assert field.sensitivity_level == DataSensitivityLevel.CONFIDENTIAL
        assert field.category == DataCategory.PERSONAL_INFO
        assert field.encryption_required is True
        assert field.retention_days == 1095
        assert 'lgpd' in field.compliance_frameworks
        assert 'gdpr' in field.compliance_frameworks
    
    def test_data_field_to_dict(self):
        """Testa conversão para dicionário"""
        field = DataField(
            field_name="credit_card",
            field_path="payment.card_number",
            sensitivity_level=DataSensitivityLevel.RESTRICTED,
            category=DataCategory.FINANCIAL,
            description="Número do cartão de crédito",
            encryption_required=True,
            retention_days=730,
            compliance_frameworks=['sox']
        )
        
        data = field.to_dict()
        
        assert data['field_name'] == "credit_card"
        assert data['sensitivity_level'] == "restricted"
        assert data['category'] == "financial"
        assert data['encryption_required'] is True
        assert data['retention_days'] == 730


class TestDataSensitivityMatrix:
    """Testes para o sistema de matriz de sensibilidade"""
    
    @pytest.fixture
    def sensitivity_matrix(self):
        """Fixture para matriz de sensibilidade"""
        return DataSensitivityMatrix()
    
    @pytest.fixture
    def mock_redis(self):
        """Fixture para Redis mock"""
        return Mock(spec=redis.Redis)
    
    def test_sensitivity_matrix_initialization(self, sensitivity_matrix):
        """Testa inicialização da matriz de sensibilidade"""
        assert sensitivity_matrix.integration_maps == {}
        assert len(sensitivity_matrix.compliance_frameworks) > 0
        assert len(sensitivity_matrix.sensitive_patterns) > 0
    
    def test_sensitivity_matrix_with_redis(self, mock_redis):
        """Testa inicialização com Redis"""
        matrix = DataSensitivityMatrix(redis_client=mock_redis)
        assert matrix.redis_client == mock_redis
    
    def test_classify_field_sensitivity_personal_info(self, sensitivity_matrix):
        """Testa classificação de campo de informação pessoal"""
        field = sensitivity_matrix.classify_field_sensitivity(
            field_name="user_email",
            field_path="user.personal.email",
            sample_data="user@example.com"
        )
        
        assert field.category == DataCategory.PERSONAL_INFO
        assert field.sensitivity_level == DataSensitivityLevel.CONFIDENTIAL
        assert field.encryption_required is True
        assert 'lgpd' in field.compliance_frameworks
        assert 'gdpr' in field.compliance_frameworks
    
    def test_classify_field_sensitivity_financial(self, sensitivity_matrix):
        """Testa classificação de campo financeiro"""
        field = sensitivity_matrix.classify_field_sensitivity(
            field_name="credit_card_number",
            field_path="payment.card_number",
            sample_data="1234-5678-9012-3456"
        )
        
        assert field.category == DataCategory.FINANCIAL
        assert field.sensitivity_level == DataSensitivityLevel.RESTRICTED
        assert field.encryption_required is True
        assert 'sox' in field.compliance_frameworks
    
    def test_classify_field_sensitivity_health(self, sensitivity_matrix):
        """Testa classificação de campo de saúde"""
        field = sensitivity_matrix.classify_field_sensitivity(
            field_name="medical_record",
            field_path="patient.medical.record",
            sample_data="Diagnóstico: Hipertensão"
        )
        
        assert field.category == DataCategory.HEALTH
        assert field.sensitivity_level == DataSensitivityLevel.HIGHLY_SENSITIVE
        assert field.encryption_required is True
    
    def test_classify_field_sensitivity_authentication(self, sensitivity_matrix):
        """Testa classificação de campo de autenticação"""
        field = sensitivity_matrix.classify_field_sensitivity(
            field_name="api_key",
            field_path="auth.api_key",
            sample_data="sk_test_1234567890abcdef"
        )
        
        assert field.category == DataCategory.AUTHENTICATION
        assert field.sensitivity_level == DataSensitivityLevel.HIGHLY_SENSITIVE
        assert field.encryption_required is True
    
    def test_classify_field_sensitivity_technical(self, sensitivity_matrix):
        """Testa classificação de campo técnico"""
        field = sensitivity_matrix.classify_field_sensitivity(
            field_name="ip_address",
            field_path="request.ip",
            sample_data="192.168.1.1"
        )
        
        assert field.category == DataCategory.TECHNICAL
        assert field.sensitivity_level == DataSensitivityLevel.INTERNAL
        assert field.encryption_required is False
    
    def test_classify_field_sensitivity_error_handling(self, sensitivity_matrix):
        """Testa tratamento de erro na classificação"""
        field = sensitivity_matrix.classify_field_sensitivity(
            field_name="invalid_field",
            field_path="invalid.path",
            sample_data=None
        )
        
        # Deve retornar classificação padrão segura
        assert field.sensitivity_level == DataSensitivityLevel.CONFIDENTIAL
        assert field.category == DataCategory.PERSONAL_INFO
        assert field.encryption_required is True
    
    def test_create_integration_data_map(self, sensitivity_matrix):
        """Testa criação de mapeamento de integração"""
        field_definitions = [
            {
                'name': 'user_email',
                'path': 'user.email',
                'sample_data': 'user@example.com'
            },
            {
                'name': 'credit_card',
                'path': 'payment.card',
                'sample_data': '1234-5678-9012-3456'
            }
        ]
        
        data_map = sensitivity_matrix.create_integration_data_map(
            "payment_api",
            field_definitions
        )
        
        assert data_map.integration_name == "payment_api"
        assert len(data_map.fields) == 2
        assert data_map.compliance_score > 0
        assert data_map.risk_level in ["low", "medium", "high"]
        assert "payment_api" in sensitivity_matrix.integration_maps
    
    def test_create_integration_data_map_with_redis(self, mock_redis):
        """Testa criação de mapeamento com cache Redis"""
        matrix = DataSensitivityMatrix(redis_client=mock_redis)
        
        field_definitions = [
            {
                'name': 'user_email',
                'path': 'user.email',
                'sample_data': 'user@example.com'
            }
        ]
        
        data_map = matrix.create_integration_data_map("test_api", field_definitions)
        
        # Verifica se foi chamado o Redis
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "data_map:test_api"
        assert call_args[0][1] == 3600  # 1 hora
    
    def test_scan_data_for_sensitive_content(self, sensitivity_matrix):
        """Testa escaneamento de dados sensíveis"""
        # Cria mapeamento primeiro
        field_definitions = [
            {
                'name': 'user_email',
                'path': 'user.email',
                'sample_data': 'user@example.com'
            }
        ]
        sensitivity_matrix.create_integration_data_map("test_api", field_definitions)
        
        # Dados com conteúdo sensível
        test_data = {
            'user': {
                'email': 'user@example.com',
                'cpf': '123.456.789-00',
                'credit_card': '1234-5678-9012-3456'
            },
            'unmapped_field': 'some_value'
        }
        
        violations = sensitivity_matrix.scan_data_for_sensitive_content(
            test_data, "test_api"
        )
        
        assert len(violations) > 0
        
        # Verifica se encontrou padrões sensíveis
        pattern_types = [value['pattern_type'] for value in violations]
        assert 'email' in pattern_types
        assert 'cpf' in pattern_types
        assert 'credit_card' in pattern_types
        assert 'unmapped_field' in pattern_types
    
    def test_scan_data_for_sensitive_content_no_mapping(self, sensitivity_matrix):
        """Testa escaneamento sem mapeamento existente"""
        test_data = {'email': 'user@example.com'}
        
        violations = sensitivity_matrix.scan_data_for_sensitive_content(
            test_data, "nonexistent_api"
        )
        
        assert len(violations) == 0
    
    def test_generate_compliance_report(self, sensitivity_matrix):
        """Testa geração de relatório de compliance"""
        # Cria mapeamento com campos sensíveis
        field_definitions = [
            {
                'name': 'user_email',
                'path': 'user.email',
                'sample_data': 'user@example.com'
            },
            {
                'name': 'credit_card',
                'path': 'payment.card',
                'sample_data': '1234-5678-9012-3456'
            }
        ]
        sensitivity_matrix.create_integration_data_map("payment_api", field_definitions)
        
        report = sensitivity_matrix.generate_compliance_report("payment_api")
        
        assert report.integration_name == "payment_api"
        assert report.overall_score > 0
        assert len(report.compliance_frameworks) > 0
        assert 'risk_assessment' in report.to_dict()
        assert report.report_id.startswith("COMP_payment_api")
    
    def test_generate_compliance_report_nonexistent(self, sensitivity_matrix):
        """Testa geração de relatório para integração inexistente"""
        with pytest.raises(ValueError):
            sensitivity_matrix.generate_compliance_report("nonexistent_api")
    
    def test_get_integration_data_map_from_cache(self, mock_redis):
        """Testa obtenção de mapeamento do cache Redis"""
        mock_data = {
            'integration_name': 'test_api',
            'fields': [],
            'last_audit': datetime.utcnow().isoformat(),
            'compliance_score': 85.0,
            'risk_level': 'medium',
            'encryption_status': {}
        }
        mock_redis.get.return_value = json.dumps(mock_data)
        
        matrix = DataSensitivityMatrix(redis_client=mock_redis)
        data_map = matrix.get_integration_data_map("test_api")
        
        assert data_map is not None
        assert data_map.integration_name == "test_api"
        assert data_map.compliance_score == 85.0
    
    def test_get_integration_data_map_not_found(self, sensitivity_matrix):
        """Testa obtenção de mapeamento inexistente"""
        data_map = sensitivity_matrix.get_integration_data_map("nonexistent_api")
        assert data_map is None
    
    def test_get_all_integrations_summary(self, sensitivity_matrix):
        """Testa geração de resumo de todas as integrações"""
        # Cria algumas integrações
        integrations = ["api1", "api2"]
        for index, name in enumerate(integrations):
            field_definitions = [
                {
                    'name': f'field_{index}',
                    'path': f'data.field_{index}',
                    'sample_data': f'value_{index}'
                }
            ]
            sensitivity_matrix.create_integration_data_map(name, field_definitions)
        
        summary = sensitivity_matrix.get_all_integrations_summary()
        
        assert summary['total_integrations'] == 2
        assert summary['total_fields'] == 2
        assert 'risk_distribution' in summary
        assert 'compliance_scores' in summary
        assert 'average_compliance_score' in summary
    
    def test_sensitive_patterns_detection(self, sensitivity_matrix):
        """Testa detecção de padrões sensíveis"""
        test_cases = [
            ('email', 'user@example.com', True),
            ('cpf', '123.456.789-00', True),
            ('cnpj', '12.345.678/0001-90', True),
            ('credit_card', '1234-5678-9012-3456', True),
            ('phone', '(11) 99999-9999', True),
            ('ip_address', '192.168.1.1', True),
            ('api_key', 'sk_test_1234567890abcdef', True),
            ('invalid', 'not_a_pattern', False)
        ]
        
        for pattern_name, test_data, should_match in test_cases:
            pattern = sensitivity_matrix.sensitive_patterns.get(pattern_name)
            if pattern:
                matches = re.findall(pattern, test_data)
                assert (len(matches) > 0) == should_match, f"Pattern {pattern_name} failed"
    
    def test_compliance_frameworks_validation(self, sensitivity_matrix):
        """Testa validação de frameworks de compliance"""
        frameworks = sensitivity_matrix.compliance_frameworks
        
        assert 'lgpd' in frameworks
        assert 'gdpr' in frameworks
        assert 'ccpa' in frameworks
        assert 'sox' in frameworks
        
        # Verifica estrutura dos frameworks
        for framework_name, framework_data in frameworks.items():
            assert 'name' in framework_data
            assert 'country' in framework_data
            assert 'requirements' in framework_data
            assert isinstance(framework_data['requirements'], list)


class TestIntegrationDataMap:
    """Testes para mapeamento de integração"""
    
    def test_integration_data_map_creation(self):
        """Testa criação de mapeamento de integração"""
        fields = [
            DataField(
                field_name="user_email",
                field_path="user.email",
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL,
                category=DataCategory.PERSONAL_INFO,
                description="Email do usuário",
                encryption_required=True,
                retention_days=1095,
                compliance_frameworks=['lgpd', 'gdpr']
            )
        ]
        
        data_map = IntegrationDataMap(
            integration_name="test_api",
            fields=fields,
            last_audit=datetime.utcnow(),
            compliance_score=85.0,
            risk_level="medium",
            encryption_status={"user.email": True}
        )
        
        assert data_map.integration_name == "test_api"
        assert len(data_map.fields) == 1
        assert data_map.compliance_score == 85.0
        assert data_map.risk_level == "medium"
        assert data_map.encryption_status["user.email"] is True
    
    def test_integration_data_map_to_dict(self):
        """Testa conversão para dicionário"""
        fields = [
            DataField(
                field_name="user_email",
                field_path="user.email",
                sensitivity_level=DataSensitivityLevel.CONFIDENTIAL,
                category=DataCategory.PERSONAL_INFO,
                description="Email do usuário",
                encryption_required=True,
                retention_days=1095,
                compliance_frameworks=['lgpd']
            )
        ]
        
        data_map = IntegrationDataMap(
            integration_name="test_api",
            fields=fields,
            last_audit=datetime.utcnow(),
            compliance_score=85.0,
            risk_level="medium",
            encryption_status={"user.email": True}
        )
        
        data = data_map.to_dict()
        
        assert data['integration_name'] == "test_api"
        assert data['compliance_score'] == 85.0
        assert data['risk_level'] == "medium"
        assert len(data['fields']) == 1
        assert 'last_audit' in data


class TestComplianceReport:
    """Testes para relatório de compliance"""
    
    def test_compliance_report_creation(self):
        """Testa criação de relatório de compliance"""
        report = ComplianceReport(
            report_id="COMP_TEST_20241220_020000",
            timestamp=datetime.utcnow(),
            integration_name="test_api",
            overall_score=85.0,
            compliance_frameworks=['lgpd', 'gdpr'],
            violations=[],
            recommendations=["Implementar criptografia"],
            risk_assessment={"overall_risk": "medium"}
        )
        
        assert report.report_id == "COMP_TEST_20241220_020000"
        assert report.integration_name == "test_api"
        assert report.overall_score == 85.0
        assert len(report.compliance_frameworks) == 2
        assert len(report.recommendations) == 1
        assert report.risk_assessment["overall_risk"] == "medium"
    
    def test_compliance_report_to_dict(self):
        """Testa conversão para dicionário"""
        report = ComplianceReport(
            report_id="COMP_TEST_20241220_020000",
            timestamp=datetime.utcnow(),
            integration_name="test_api",
            overall_score=85.0,
            compliance_frameworks=['lgpd'],
            violations=[],
            recommendations=[],
            risk_assessment={}
        )
        
        data = report.to_dict()
        
        assert data['report_id'] == "COMP_TEST_20241220_020000"
        assert data['integration_name'] == "test_api"
        assert data['overall_score'] == 85.0
        assert 'timestamp' in data


class TestConvenienceFunctions:
    """Testes para funções de conveniência"""
    
    @patch('scripts.security.data_sensitivity.data_sensitivity_matrix')
    def test_classify_field_sensitivity_function(self, mock_matrix):
        """Testa função de conveniência classify_field_sensitivity"""
        mock_field = Mock(spec=DataField)
        mock_matrix.classify_field_sensitivity.return_value = mock_field
        
        result = classify_field_sensitivity("test_field", "test.path", "sample_data")
        
        assert result == mock_field
        mock_matrix.classify_field_sensitivity.assert_called_once_with(
            "test_field", "test.path", "sample_data"
        )
    
    @patch('scripts.security.data_sensitivity.data_sensitivity_matrix')
    def test_create_integration_data_map_function(self, mock_matrix):
        """Testa função de conveniência create_integration_data_map"""
        mock_data_map = Mock(spec=IntegrationDataMap)
        mock_matrix.create_integration_data_map.return_value = mock_data_map
        
        field_definitions = [{'name': 'test', 'path': 'test.path'}]
        result = create_integration_data_map("test_api", field_definitions)
        
        assert result == mock_data_map
        mock_matrix.create_integration_data_map.assert_called_once_with(
            "test_api", field_definitions
        )
    
    @patch('scripts.security.data_sensitivity.data_sensitivity_matrix')
    def test_scan_data_for_sensitive_content_function(self, mock_matrix):
        """Testa função de conveniência scan_data_for_sensitive_content"""
        mock_violations = [{'type': 'test_violation'}]
        mock_matrix.scan_data_for_sensitive_content.return_value = mock_violations
        
        test_data = {'test': 'data'}
        result = scan_data_for_sensitive_content(test_data, "test_api")
        
        assert result == mock_violations
        mock_matrix.scan_data_for_sensitive_content.assert_called_once_with(
            test_data, "test_api"
        )
    
    @patch('scripts.security.data_sensitivity.data_sensitivity_matrix')
    def test_generate_compliance_report_function(self, mock_matrix):
        """Testa função de conveniência generate_compliance_report"""
        mock_report = Mock(spec=ComplianceReport)
        mock_matrix.generate_compliance_report.return_value = mock_report
        
        result = generate_compliance_report("test_api")
        
        assert result == mock_report
        mock_matrix.generate_compliance_report.assert_called_once_with("test_api") 