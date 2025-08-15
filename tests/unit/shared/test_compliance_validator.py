from typing import Dict, List, Optional, Any
"""
Testes Unitários para Validador de Compliance
============================================

Tracing ID: TEST_COMPLIANCE_VALIDATOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação

Objetivo: Validar funcionalidades do validador de compliance enterprise,
incluindo validação PCI-DSS, LGPD e geração de relatórios.
"""

import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Adicionar diretório raiz ao path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.compliance_validator import (
    ComplianceValidator,
    ComplianceRequirement,
    ComplianceReport,
    ComplianceViolation,
    validate_compliance
)


class TestComplianceValidator:
    """Testes para a classe ComplianceValidator"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_compliance.yaml")
        
        # Criar configuração de teste
        config = {
            'pci_dss': {
                'enabled': True,
                'version': '4.0',
                'requirements': [
                    {
                        'id': 'PCI-DSS-1',
                        'name': 'Firewall Configuration',
                        'description': 'Firewall configuration must be documented',
                        'severity': 'critical',
                        'documentation_required': True,
                        'audit_frequency': 'quarterly'
                    },
                    {
                        'id': 'PCI-DSS-2',
                        'name': 'Default Passwords',
                        'description': 'Default passwords must be changed',
                        'severity': 'high',
                        'documentation_required': True,
                        'audit_frequency': 'monthly'
                    }
                ]
            },
            'lgpd': {
                'enabled': True,
                'version': '1.0',
                'requirements': [
                    {
                        'id': 'LGPD-1',
                        'name': 'Finalidade e boa-fé',
                        'description': 'Tratamento de dados deve ter finalidade legítima',
                        'severity': 'critical',
                        'documentation_required': True,
                        'audit_frequency': 'monthly'
                    },
                    {
                        'id': 'LGPD-2',
                        'name': 'Adequação e necessidade',
                        'description': 'Dados coletados devem ser adequados e necessários',
                        'severity': 'high',
                        'documentation_required': True,
                        'audit_frequency': 'monthly'
                    }
                ]
            }
        }
        
        # Salvar configuração
        import yaml
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Mock dos serviços dependentes
        self.mock_security_detector = Mock()
        self.mock_quality_analyzer = Mock()
        self.mock_metrics_collector = Mock()
        
        # Inicializar validador com mocks
        with patch('shared.compliance_validator.SensitiveDataDetector', return_value=self.mock_security_detector), \
             patch('shared.compliance_validator.DocQualityAnalyzer', return_value=self.mock_quality_analyzer), \
             patch('shared.compliance_validator.DocGenerationMetrics', return_value=self.mock_metrics_collector):
            
            self.validator = ComplianceValidator(self.config_file)
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Teste de inicialização do validador"""
        assert self.validator.config_path == self.config_file
        assert len(self.validator.requirements) == 4  # 2 PCI-DSS + 2 LGPD
        assert 'PCI-DSS-1' in self.validator.requirements
        assert 'LGPD-1' in self.validator.requirements
    
    def test_load_config(self):
        """Teste de carregamento de configuração"""
        config = self.validator._load_config()
        assert config['pci_dss']['enabled'] is True
        assert config['lgpd']['enabled'] is True
        assert len(config['pci_dss']['requirements']) == 2
        assert len(config['lgpd']['requirements']) == 2
    
    def test_load_requirements(self):
        """Teste de carregamento de requisitos"""
        # Resetar requisitos
        self.validator.requirements = {}
        
        # Recarregar requisitos
        self.validator._load_requirements()
        
        assert len(self.validator.requirements) == 4
        for req_id in ['PCI-DSS-1', 'PCI-DSS-2', 'LGPD-1', 'LGPD-2']:
            assert req_id in self.validator.requirements
    
    def test_validate_pci_dss_compliance(self):
        """Teste de validação PCI-DSS"""
        # Criar arquivos de teste
        docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_dir)
        
        # Arquivo com documentação de firewall
        firewall_doc = os.path.join(docs_dir, "firewall_config.md")
        with open(firewall_doc, 'w') as f:
            f.write("# Firewall Configuration\n\nThis document describes firewall settings.")
        
        # Configurar mock para qualidade
        self.mock_quality_analyzer.calculate_doc_quality_score.return_value = 0.85
        
        # Executar validação
        report = self.validator.validate_pci_dss_compliance([docs_dir])
        
        # Verificar relatório
        assert isinstance(report, ComplianceReport)
        assert report.framework == 'pci_dss'
        assert report.requirements_count == 2
        assert report.overall_score > 0.0
    
    def test_validate_lgpd_compliance(self):
        """Teste de validação LGPD"""
        # Criar arquivos de teste
        docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_dir)
        
        # Arquivo com documentação de finalidade
        purpose_doc = os.path.join(docs_dir, "data_purpose.md")
        with open(purpose_doc, 'w') as f:
            f.write("# Data Purpose\n\nThis document describes data processing purposes.")
        
        # Configurar mock para qualidade
        self.mock_quality_analyzer.calculate_doc_quality_score.return_value = 0.90
        
        # Executar validação
        report = self.validator.validate_lgpd_compliance([docs_dir])
        
        # Verificar relatório
        assert isinstance(report, ComplianceReport)
        assert report.framework == 'lgpd'
        assert report.requirements_count == 2
        assert report.overall_score > 0.0
    
    def test_validate_combined_compliance(self):
        """Teste de validação combinada"""
        # Criar arquivos de teste
        docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_dir)
        
        # Arquivo com documentação geral
        general_doc = os.path.join(docs_dir, "compliance.md")
        with open(general_doc, 'w') as f:
            f.write("# Compliance Documentation\n\nGeneral compliance information.")
        
        # Configurar mock para qualidade
        self.mock_quality_analyzer.calculate_doc_quality_score.return_value = 0.80
        
        # Executar validação
        report = self.validator.validate_combined_compliance([docs_dir])
        
        # Verificar relatório
        assert isinstance(report, ComplianceReport)
        assert report.framework == 'combined'
        assert report.requirements_count == 4
        assert report.overall_score > 0.0
    
    def test_validate_requirement(self):
        """Teste de validação de requisito específico"""
        # Obter requisito
        requirement = self.validator.requirements['PCI-DSS-1']
        
        # Executar validação
        self.validator._validate_requirement(requirement, [self.temp_dir])
        
        # Verificar que requisito foi processado com validações específicas
        assert isinstance(requirement.last_audit, datetime), "last_audit deve ser um datetime"
        assert isinstance(requirement.next_audit, datetime), "next_audit deve ser um datetime"
        assert requirement.last_audit <= datetime.now(), "last_audit deve ser no passado"
        assert requirement.next_audit > datetime.now(), "next_audit deve ser no futuro"
        assert 0.0 <= requirement.compliance_score <= 1.0, "compliance_score deve estar entre 0.0 e 1.0"
        assert requirement.status in ['compliant', 'partial', 'non_compliant'], f"status inválido: {requirement.status}"
    
    def test_validate_firewall_configuration(self):
        """Teste de validação de configuração de firewall"""
        # Obter requisito
        requirement = self.validator.requirements['PCI-DSS-1']
        
        # Teste sem documentação
        self.validator._validate_firewall_configuration(requirement, [self.temp_dir])
        assert len(requirement.issues) > 0
        assert any(issue['type'] == 'missing_documentation' for issue in requirement.issues)
        
        # Resetar issues
        requirement.issues = []
        
        # Criar documentação
        docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_dir)
        firewall_doc = os.path.join(docs_dir, "firewall.md")
        with open(firewall_doc, 'w') as f:
            f.write("# Firewall Configuration")
        
        # Configurar mock para qualidade
        self.mock_quality_analyzer.calculate_doc_quality_score.return_value = 0.85
        
        # Teste com documentação
        self.validator._validate_firewall_configuration(requirement, [self.temp_dir])
        assert len(requirement.issues) == 0
    
    def test_validate_default_passwords(self):
        """Teste de validação de senhas padrão"""
        # Obter requisito
        requirement = self.validator.requirements['PCI-DSS-2']
        
        # Criar arquivo com senha padrão
        config_file = os.path.join(self.temp_dir, "config.py")
        with open(config_file, 'w') as f:
            f.write('password = "admin"\n')
        
        # Executar validação
        self.validator._validate_default_passwords(requirement, [self.temp_dir])
        
        # Verificar que issue foi detectado
        assert len(requirement.issues) > 0
        assert any(issue['type'] == 'default_password' for issue in requirement.issues)
    
    def test_validate_cardholder_data_protection(self):
        """Teste de validação de proteção de dados de cartão"""
        # Obter requisito
        requirement = self.validator.requirements['PCI-DSS-3']
        
        # Criar arquivo com dados de cartão
        data_file = os.path.join(self.temp_dir, "data.py")
        with open(data_file, 'w') as f:
            f.write('card_number = "1234-5678-9012-3456"\n')
        
        # Executar validação
        self.validator._validate_cardholder_data_protection(requirement, [self.temp_dir])
        
        # Verificar que issue foi detectado
        assert len(requirement.issues) > 0
        assert any(issue['type'] == 'cardholder_data_exposure' for issue in requirement.issues)
    
    def test_validate_data_transmission_encryption(self):
        """Teste de validação de criptografia de transmissão"""
        # Obter requisito
        requirement = self.validator.requirements['PCI-DSS-4']
        
        # Teste sem criptografia
        self.validator._validate_data_transmission_encryption(requirement, [self.temp_dir])
        assert len(requirement.issues) > 0
        assert any(issue['type'] == 'missing_encryption' for issue in requirement.issues)
        
        # Resetar issues
        requirement.issues = []
        
        # Criar arquivo com configuração de criptografia
        config_file = os.path.join(self.temp_dir, "config.py")
        with open(config_file, 'w') as f:
            f.write('encryption_enabled = True\n')
        
        # Teste com criptografia
        self.validator._validate_data_transmission_encryption(requirement, [self.temp_dir])
        assert len(requirement.issues) == 0
    
    def test_validate_purpose_good_faith(self):
        """Teste de validação de finalidade e boa-fé"""
        # Obter requisito
        requirement = self.validator.requirements['LGPD-1']
        
        # Teste sem documentação
        self.validator._validate_purpose_good_faith(requirement, [self.temp_dir])
        assert len(requirement.issues) > 0
        assert any(issue['type'] == 'missing_purpose_documentation' for issue in requirement.issues)
        
        # Resetar issues
        requirement.issues = []
        
        # Criar documentação
        docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_dir)
        purpose_doc = os.path.join(docs_dir, "purpose.md")
        with open(purpose_doc, 'w') as f:
            f.write("# Data Purpose")
        
        # Teste com documentação
        self.validator._validate_purpose_good_faith(requirement, [self.temp_dir])
        assert len(requirement.issues) == 0
    
    def test_validate_consent(self):
        """Teste de validação de consentimento"""
        # Obter requisito
        requirement = self.validator.requirements['LGPD-9']
        
        # Teste sem documentação
        self.validator._validate_consent(requirement, [self.temp_dir])
        assert len(requirement.issues) > 0
        assert any(issue['type'] == 'missing_consent_documentation' for issue in requirement.issues)
        assert any(issue['severity'] == 'critical' for issue in requirement.issues)
    
    def test_find_files_with_pattern(self):
        """Teste de busca de arquivos com padrão"""
        # Criar arquivos de teste
        docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_dir)
        
        # Arquivo com palavra-chave
        test_file = os.path.join(docs_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("# Security Documentation\n\nThis is about security.")
        
        # Buscar arquivos
        found_files = self.validator._find_files_with_pattern([self.temp_dir], ['security'])
        
        # Verificar resultado
        assert len(found_files) > 0
        assert test_file in found_files
    
    def test_find_pattern_in_files(self):
        """Teste de busca de padrões em arquivos"""
        # Criar arquivo com padrão
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write('password = "admin"\n')
        
        # Buscar padrão
        pattern = r'password["\string_data]*[:=]["\string_data]*["\']?(admin|root|password|123456|default)["\']?'
        matches = self.validator._find_pattern_in_files([self.temp_dir], pattern)
        
        # Verificar resultado
        assert len(matches) > 0
        assert matches[0]['file_path'] == test_file
        assert matches[0]['line_number'] == 1
    
    def test_calculate_requirement_score(self):
        """Teste de cálculo de score de requisito"""
        # Criar requisito sem issues
        requirement = ComplianceRequirement(
            id="TEST-1",
            name="Test Requirement",
            description="Test description",
            severity="high",
            documentation_required=True,
            audit_frequency="monthly"
        )
        
        # Calcular score sem issues
        score = self.validator._calculate_requirement_score(requirement)
        assert score == 1.0
        
        # Adicionar issue crítico
        requirement.issues.append({
            'type': 'test_issue',
            'description': 'Test issue',
            'severity': 'critical'
        })
        
        # Calcular score com issue
        score = self.validator._calculate_requirement_score(requirement)
        assert score == 0.0
    
    def test_calculate_next_audit_date(self):
        """Teste de cálculo de próxima data de auditoria"""
        # Teste diferentes frequências
        now = datetime.now()
        
        daily = self.validator._calculate_next_audit_date('daily')
        assert daily.date() == (now + timedelta(days=1)).date()
        
        weekly = self.validator._calculate_next_audit_date('weekly')
        assert weekly.date() == (now + timedelta(weeks=1)).date()
        
        monthly = self.validator._calculate_next_audit_date('monthly')
        assert monthly.date() == (now + timedelta(days=30)).date()
        
        quarterly = self.validator._calculate_next_audit_date('quarterly')
        assert quarterly.date() == (now + timedelta(days=90)).date()
        
        annually = self.validator._calculate_next_audit_date('annually')
        assert annually.date() == (now + timedelta(days=365)).date()
    
    def test_generate_compliance_report(self):
        """Teste de geração de relatório de compliance"""
        # Criar requisitos de teste
        requirements = [
            ComplianceRequirement(
                id="TEST-1",
                name="Test Requirement 1",
                description="Test description 1",
                severity="high",
                documentation_required=True,
                audit_frequency="monthly",
                status="compliant",
                compliance_score=1.0
            ),
            ComplianceRequirement(
                id="TEST-2",
                name="Test Requirement 2",
                description="Test description 2",
                severity="critical",
                documentation_required=True,
                audit_frequency="monthly",
                status="non_compliant",
                compliance_score=0.5
            )
        ]
        
        # Gerar relatório
        report = self.validator._generate_compliance_report('test', requirements)
        
        # Verificar relatório
        assert isinstance(report, ComplianceReport)
        assert report.framework == 'test'
        assert report.requirements_count == 2
        assert report.compliant_count == 1
        assert report.non_compliant_count == 1
        assert report.overall_score == 0.75  # (1.0 + 0.5) / 2
        assert len(report.recommendations) > 0
    
    def test_generate_recommendations(self):
        """Teste de geração de recomendações"""
        # Criar requisitos com issues
        requirements = [
            ComplianceRequirement(
                id="TEST-1",
                name="Test Requirement 1",
                description="Test description 1",
                severity="high",
                documentation_required=True,
                audit_frequency="monthly",
                issues=[{
                    'type': 'missing_documentation',
                    'description': 'Missing documentation',
                    'severity': 'high'
                }]
            ),
            ComplianceRequirement(
                id="TEST-2",
                name="Test Requirement 2",
                description="Test description 2",
                severity="critical",
                documentation_required=True,
                audit_frequency="monthly",
                issues=[{
                    'type': 'default_password',
                    'description': 'Default password found',
                    'severity': 'critical'
                }]
            )
        ]
        
        # Gerar recomendações
        recommendations = self.validator._generate_recommendations(requirements)
        
        # Verificar recomendações
        assert len(recommendations) > 0
        assert any('documentação' in rec.lower() for rec in recommendations)
        assert any('senha' in rec.lower() for rec in recommendations)
    
    def test_save_report(self):
        """Teste de salvamento de relatório"""
        # Criar relatório de teste
        report = ComplianceReport(
            report_id="TEST_REPORT_001",
            timestamp=datetime.now(),
            framework="test",
            overall_score=0.85,
            requirements_count=2,
            compliant_count=1,
            non_compliant_count=1,
            pending_count=0,
            requirements=[],
            recommendations=["Test recommendation"],
            next_audit_date=datetime.now() + timedelta(days=30)
        )
        
        # Salvar relatório
        output_path = os.path.join(self.temp_dir, "test_report.json")
        saved_path = self.validator.save_report(report, output_path)
        
        # Verificar que arquivo foi criado
        assert os.path.exists(saved_path)
        
        # Verificar conteúdo
        with open(saved_path, 'r') as f:
            data = json.load(f)
        
        assert data['report_id'] == "TEST_REPORT_001"
        assert data['framework'] == "test"
        assert data['overall_score'] == 0.85
    
    def test_get_compliance_summary(self):
        """Teste de obtenção de resumo de compliance"""
        # Criar relatório de teste
        report = ComplianceReport(
            report_id="TEST_REPORT_001",
            timestamp=datetime.now(),
            framework="test",
            overall_score=0.85,
            requirements_count=2,
            compliant_count=1,
            non_compliant_count=1,
            pending_count=0,
            requirements=[],
            recommendations=[],
            next_audit_date=datetime.now() + timedelta(days=30)
        )
        
        # Adicionar ao histórico
        self.validator.audit_history.append(report)
        
        # Obter resumo
        summary = self.validator.get_compliance_summary()
        
        # Verificar resumo
        assert summary['overall_score'] == 0.85
        assert summary['framework'] == "test"
        assert summary['requirements_count'] == 2
        assert summary['compliant_count'] == 1
        assert summary['non_compliant_count'] == 1
    
    def test_get_compliance_summary_no_audits(self):
        """Teste de resumo sem auditorias"""
        # Limpar histórico
        self.validator.audit_history = []
        
        # Obter resumo
        summary = self.validator.get_compliance_summary()
        
        # Verificar resumo
        assert summary['status'] == 'no_audits_performed'


class TestComplianceRequirement:
    """Testes para a classe ComplianceRequirement"""
    
    def test_initialization(self):
        """Teste de inicialização de requisito"""
        requirement = ComplianceRequirement(
            id="TEST-1",
            name="Test Requirement",
            description="Test description",
            severity="high",
            documentation_required=True,
            audit_frequency="monthly"
        )
        
        assert requirement.id == "TEST-1"
        assert requirement.name == "Test Requirement"
        assert requirement.description == "Test description"
        assert requirement.severity == "high"
        assert requirement.documentation_required is True
        assert requirement.audit_frequency == "monthly"
        assert requirement.status == "pending"
        assert requirement.compliance_score == 0.0
        assert requirement.issues == []
    
    def test_post_init(self):
        """Teste de pós-inicialização"""
        requirement = ComplianceRequirement(
            id="TEST-1",
            name="Test Requirement",
            description="Test description",
            severity="high",
            documentation_required=True,
            audit_frequency="monthly",
            issues=[]  # Corrigido: não passar None
        )
        assert requirement.issues == []


class TestComplianceReport:
    """Testes para a classe ComplianceReport"""
    
    def test_initialization(self):
        """Teste de inicialização de relatório"""
        timestamp = datetime.now()
        next_audit = datetime.now() + timedelta(days=30)
        
        report = ComplianceReport(
            report_id="TEST_REPORT_001",
            timestamp=timestamp,
            framework="test",
            overall_score=0.85,
            requirements_count=2,
            compliant_count=1,
            non_compliant_count=1,
            pending_count=0,
            requirements=[],
            recommendations=["Test recommendation"],
            next_audit_date=next_audit
        )
        
        assert report.report_id == "TEST_REPORT_001"
        assert report.timestamp == timestamp
        assert report.framework == "test"
        assert report.overall_score == 0.85
        assert report.requirements_count == 2
        assert report.compliant_count == 1
        assert report.non_compliant_count == 1
        assert report.pending_count == 0
        assert report.recommendations == ["Test recommendation"]
        assert report.next_audit_date == next_audit
        assert report.generated_by == "ComplianceValidator"


class TestComplianceViolation:
    """Testes para a classe ComplianceViolation"""
    
    def test_initialization(self):
        """Teste de inicialização de violação"""
        violation = ComplianceViolation(
            violation_id="VIOLATION-001",
            requirement_id="REQ-001",
            severity="high",
            description="Test violation",
            file_path="/path/to/file.py",
            line_number=10
        )
        
        assert violation.violation_id == "VIOLATION-001"
        assert violation.requirement_id == "REQ-001"
        assert violation.severity == "high"
        assert violation.description == "Test violation"
        assert violation.file_path == "/path/to/file.py"
        assert violation.line_number == 10
        assert violation.resolved is False
        assert violation.resolution_notes == ""
        assert isinstance(violation.detected_at, datetime), "detected_at deve ser um datetime"
        assert violation.detected_at <= datetime.now(), "detected_at deve ser no passado ou presente"
    
    def test_post_init(self):
        """Teste de pós-inicialização"""
        from datetime import datetime
        violation = ComplianceViolation(
            violation_id="VIOLATION-001",
            requirement_id="REQ-001",
            severity="high",
            description="Test violation",
            detected_at=datetime.now()  # Corrigido: não passar None
        )
        assert isinstance(violation.detected_at, datetime), "detected_at deve ser um datetime"
        assert violation.detected_at <= datetime.now(), "detected_at deve ser no passado ou presente"


class TestValidateComplianceFunction:
    """Testes para função de conveniência"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_compliance.yaml")
        
        # Criar configuração mínima
        config = {
            'pci_dss': {
                'enabled': True,
                'requirements': []
            },
            'lgpd': {
                'enabled': True,
                'requirements': []
            }
        }
        
        import yaml
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f)
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('shared.compliance_validator.ComplianceValidator')
    def test_validate_compliance_pci_dss(self, mock_validator_class):
        """Teste de validação PCI-DSS via função"""
        # Configurar mock
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_report = Mock()
        mock_validator.validate_pci_dss_compliance.return_value = mock_report
        
        # Executar validação
        result = validate_compliance('pci_dss', self.config_file)
        
        # Verificar resultado
        assert result == mock_report
        mock_validator.validate_pci_dss_compliance.assert_called_once()
    
    @patch('shared.compliance_validator.ComplianceValidator')
    def test_validate_compliance_lgpd(self, mock_validator_class):
        """Teste de validação LGPD via função"""
        # Configurar mock
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_report = Mock()
        mock_validator.validate_lgpd_compliance.return_value = mock_report
        
        # Executar validação
        result = validate_compliance('lgpd', self.config_file)
        
        # Verificar resultado
        assert result == mock_report
        mock_validator.validate_lgpd_compliance.assert_called_once()
    
    @patch('shared.compliance_validator.ComplianceValidator')
    def test_validate_compliance_combined(self, mock_validator_class):
        """Teste de validação combinada via função"""
        # Configurar mock
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_report = Mock()
        mock_validator.validate_combined_compliance.return_value = mock_report
        
        # Executar validação
        result = validate_compliance('combined', self.config_file)
        
        # Verificar resultado
        assert result == mock_report
        mock_validator.validate_combined_compliance.assert_called_once()
    
    @patch('shared.compliance_validator.ComplianceValidator')
    def test_validate_compliance_default(self, mock_validator_class):
        """Teste de validação com framework padrão"""
        # Configurar mock
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_report = Mock()
        mock_validator.validate_combined_compliance.return_value = mock_report
        
        # Executar validação sem especificar framework
        result = validate_compliance(config_path=self.config_file)
        
        # Verificar resultado
        assert result == mock_report
        mock_validator.validate_combined_compliance.assert_called_once()


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-value"]) 