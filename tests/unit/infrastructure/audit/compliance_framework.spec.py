from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
🧪 TESTES UNITÁRIOS - COMPLIANCE FRAMEWORK

Tracing ID: TEST_COMPLIANCE_2025_001
Data/Hora: 2025-01-27 16:15:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Testes unitários para o framework completo de compliance.
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Adicionar scripts ao path
sys.path.append('scripts/compliance')

# Importar módulos de compliance
from setup_compliance import ComplianceManager, ComplianceFramework, ComplianceStatus
from dpo_system import DPOSystem, DataSubjectRequest, ComplianceIncident, IncidentSeverity
from consent_manager import ConsentManager, ConsentRecord, ConsentType, ConsentStatus
from data_subject_rights import DataSubjectRightsManager, DataRightType, RequestStatus
from breach_notification import BreachNotificationSystem, DataBreach, BreachSeverity, BreachType

class TestComplianceFramework(unittest.TestCase):
    """Testes para o framework de compliance"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Criar diretórios necessários
        os.makedirs('data/compliance', exist_ok=True)
        os.makedirs('logs/compliance', exist_ok=True)
        os.makedirs('config/compliance', exist_ok=True)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_compliance_manager_initialization(self):
        """Testa inicialização do ComplianceManager"""
        manager = ComplianceManager()
        
        self.assertIsNotNone(manager.tracing_id)
        self.assertIsInstance(manager.requirements, dict)
        self.assertIsInstance(manager.reports, dict)
        
        # Verificar se diretórios foram criados
        self.assertTrue(os.path.exists('docs/compliance'))
        self.assertTrue(os.path.exists('scripts/compliance'))
    
    def test_gdpr_requirements_initialization(self):
        """Testa inicialização dos requisitos GDPR"""
        manager = ComplianceManager()
        manager.initialize_gdpr_requirements()
        
        # Verificar se requisitos foram criados
        gdpr_requirements = [
            req for req in manager.requirements.values()
            if req.framework == ComplianceFramework.GDPR
        ]
        
        self.assertGreater(len(gdpr_requirements), 0)
        
        # Verificar requisitos específicos
        requirement_ids = [req.id for req in gdpr_requirements]
        expected_ids = ['GDPR-001', 'GDPR-002', 'GDPR-003', 'GDPR-004']
        
        for expected_id in expected_ids:
            self.assertIn(expected_id, requirement_ids)
    
    def test_lgpd_requirements_initialization(self):
        """Testa inicialização dos requisitos LGPD"""
        manager = ComplianceManager()
        manager.initialize_lgpd_requirements()
        
        lgpd_requirements = [
            req for req in manager.requirements.values()
            if req.framework == ComplianceFramework.LGPD
        ]
        
        self.assertGreater(len(lgpd_requirements), 0)
        
        # Verificar requisitos específicos
        requirement_ids = [req.id for req in lgpd_requirements]
        expected_ids = ['LGPD-001', 'LGPD-002', 'LGPD-003', 'LGPD-004', 'LGPD-005']
        
        for expected_id in expected_ids:
            self.assertIn(expected_id, requirement_ids)
    
    def test_compliance_report_generation(self):
        """Testa geração de relatórios de compliance"""
        manager = ComplianceManager()
        manager.initialize_gdpr_requirements()
        manager.generate_compliance_reports()
        
        # Verificar se relatório GDPR foi gerado
        self.assertIn(ComplianceFramework.GDPR, manager.reports)
        
        report = manager.reports[ComplianceFramework.GDPR]
        self.assertIsNotNone(report.overall_score)
        self.assertGreater(len(report.requirements), 0)
        self.assertIsInstance(report.recommendations, list)
    
    def test_compliance_data_saving(self):
        """Testa salvamento de dados de compliance"""
        manager = ComplianceManager()
        manager.initialize_gdpr_requirements()
        manager.generate_compliance_reports()
        manager.save_compliance_data()
        
        # Verificar se arquivos foram criados
        self.assertTrue(os.path.exists('config/compliance/requirements.json'))
        self.assertTrue(os.path.exists('config/compliance/reports.json'))
        self.assertTrue(os.path.exists('config/compliance/dashboard.json'))
    
    def test_compliance_setup_complete(self):
        """Testa setup completo de compliance"""
        manager = ComplianceManager()
        success = manager.run_compliance_setup()
        
        self.assertTrue(success)
        
        # Verificar se todos os frameworks foram inicializados
        expected_frameworks = [
            ComplianceFramework.GDPR,
            ComplianceFramework.LGPD,
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001,
            ComplianceFramework.PCI_DSS
        ]
        
        for framework in expected_frameworks:
            self.assertIn(framework, manager.reports)

class TestDPOSystem(unittest.TestCase):
    """Testes para o sistema DPO"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/compliance', exist_ok=True)
        os.makedirs('logs/compliance', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_dpo_system_initialization(self):
        """Testa inicialização do sistema DPO"""
        dpo = DPOSystem()
        
        self.assertIsNotNone(dpo.tracing_id)
        self.assertIsInstance(dpo.data_subject_requests, dict)
        self.assertIsInstance(dpo.incidents, dict)
        self.assertIsInstance(dpo.audits, dict)
    
    def test_data_subject_request_creation(self):
        """Testa criação de solicitação de titular"""
        dpo = DPOSystem()
        
        request_id = dpo.create_data_subject_request(
            user_id="user123",
            request_type="access",
            description="Solicitação de acesso"
        )
        
        self.assertIsNotNone(request_id)
        self.assertIn(request_id, dpo.data_subject_requests)
        
        request = dpo.data_subject_requests[request_id]
        self.assertEqual(request.user_id, "user123")
        self.assertEqual(request.status, "pending")
    
    def test_incident_creation(self):
        """Testa criação de incidente"""
        dpo = DPOSystem()
        
        incident_id = dpo.create_compliance_incident(
            title="Test Incident",
            description="Test description",
            severity=IncidentSeverity.MEDIUM,
            framework="GDPR",
            affected_users=10
        )
        
        self.assertIsNotNone(incident_id)
        self.assertIn(incident_id, dpo.incidents)
        
        incident = dpo.incidents[incident_id]
        self.assertEqual(incident.title, "Test Incident")
        self.assertEqual(incident.severity, IncidentSeverity.MEDIUM)
    
    def test_audit_scheduling(self):
        """Testa agendamento de auditoria"""
        dpo = DPOSystem()
        
        audit_date = datetime.now() + timedelta(days=30)
        audit_id = dpo.schedule_compliance_audit(
            framework="GDPR",
            auditor="Test Auditor",
            audit_date=audit_date
        )
        
        self.assertIsNotNone(audit_id)
        self.assertIn(audit_id, dpo.audits)
        
        audit = dpo.audits[audit_id]
        self.assertEqual(audit.framework, "GDPR")
        self.assertEqual(audit.auditor, "Test Auditor")

class TestConsentManager(unittest.TestCase):
    """Testes para o gerenciador de consentimento"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/compliance/consent', exist_ok=True)
        os.makedirs('logs/compliance', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_consent_manager_initialization(self):
        """Testa inicialização do gerenciador de consentimento"""
        manager = ConsentManager()
        
        self.assertIsNotNone(manager.tracing_id)
        self.assertIsInstance(manager.consent_records, dict)
        self.assertIsInstance(manager.consent_templates, dict)
        
        # Verificar se templates padrão foram criados
        self.assertGreater(len(manager.consent_templates), 0)
    
    def test_consent_record_creation(self):
        """Testa criação de registro de consentimento"""
        manager = ConsentManager()
        
        record_id = manager.create_consent_record(
            user_id="user123",
            consent_type=ConsentType.ANALYTICS,
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )
        
        self.assertIsNotNone(record_id)
        self.assertIn(record_id, manager.consent_records)
        
        record = manager.consent_records[record_id]
        self.assertEqual(record.user_id, "user123")
        self.assertEqual(record.consent_type, ConsentType.ANALYTICS)
        self.assertEqual(record.status, ConsentStatus.GRANTED)
    
    def test_consent_withdrawal(self):
        """Testa revogação de consentimento"""
        manager = ConsentManager()
        
        # Criar consentimento
        record_id = manager.create_consent_record(
            user_id="user123",
            consent_type=ConsentType.MARKETING
        )
        
        # Verificar se consentimento está ativo
        has_consent = manager.check_consent("user123", ConsentType.MARKETING)
        self.assertTrue(has_consent)
        
        # Revogar consentimento
        success = manager.withdraw_consent("user123", ConsentType.MARKETING)
        self.assertTrue(success)
        
        # Verificar se consentimento foi revogado
        has_consent_after = manager.check_consent("user123", ConsentType.MARKETING)
        self.assertFalse(has_consent_after)
    
    def test_consent_statistics(self):
        """Testa geração de estatísticas de consentimento"""
        manager = ConsentManager()
        
        # Criar alguns consentimentos
        manager.create_consent_record("user1", ConsentType.ANALYTICS)
        manager.create_consent_record("user2", ConsentType.MARKETING)
        manager.create_consent_record("user3", ConsentType.ANALYTICS)
        
        stats = manager.get_consent_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_records', stats)
        self.assertIn('by_type', stats)
        self.assertGreater(stats['total_records'], 0)

class TestDataSubjectRights(unittest.TestCase):
    """Testes para direitos dos titulares"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/compliance/rights', exist_ok=True)
        os.makedirs('data/compliance/exports', exist_ok=True)
        os.makedirs('logs/compliance', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_rights_manager_initialization(self):
        """Testa inicialização do gerenciador de direitos"""
        manager = DataSubjectRightsManager()
        
        self.assertIsNotNone(manager.tracing_id)
        self.assertIsInstance(manager.requests, dict)
        self.assertIsInstance(manager.data_inventory, dict)
    
    def test_data_request_creation(self):
        """Testa criação de solicitação de dados"""
        manager = DataSubjectRightsManager()
        
        request_id = manager.create_data_request(
            user_id="user123",
            right_type=DataRightType.ACCESS,
            description="Solicitação de acesso"
        )
        
        self.assertIsNotNone(request_id)
        self.assertIn(request_id, manager.requests)
        
        request = manager.requests[request_id]
        self.assertEqual(request.user_id, "user123")
        self.assertEqual(request.right_type, DataRightType.ACCESS)
        self.assertEqual(request.status, RequestStatus.PENDING)
    
    def test_access_request_processing(self):
        """Testa processamento de solicitação de acesso"""
        manager = DataSubjectRightsManager()
        
        request_id = manager.create_data_request(
            user_id="user123",
            right_type=DataRightType.ACCESS
        )
        
        # Verificar solicitação
        manager.verify_request(request_id, "email_verification")
        
        # Processar solicitação
        user_data = manager.process_access_request(request_id)
        
        self.assertIsInstance(user_data, dict)
        self.assertIn('profile', user_data)
        self.assertIn('preferences', user_data)
        
        # Verificar se solicitação foi completada
        request = manager.requests[request_id]
        self.assertEqual(request.status, RequestStatus.COMPLETED)
    
    def test_portability_request_processing(self):
        """Testa processamento de solicitação de portabilidade"""
        manager = DataSubjectRightsManager()
        
        request_id = manager.create_data_request(
            user_id="user123",
            right_type=DataRightType.PORTABILITY
        )
        
        # Processar portabilidade
        export_file = manager.process_portability_request(request_id, "json")
        
        self.assertIsNotNone(export_file)
        self.assertTrue(os.path.exists(export_file))
        
        # Verificar se solicitação foi completada
        request = manager.requests[request_id]
        self.assertEqual(request.status, RequestStatus.COMPLETED)

class TestBreachNotification(unittest.TestCase):
    """Testes para sistema de notificação de violações"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('data/compliance/breaches', exist_ok=True)
        os.makedirs('logs/compliance', exist_ok=True)
        os.makedirs('notifications/compliance', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_breach_system_initialization(self):
        """Testa inicialização do sistema de violações"""
        system = BreachNotificationSystem()
        
        self.assertIsNotNone(system.tracing_id)
        self.assertIsInstance(system.breaches, dict)
        self.assertIsInstance(system.notifications, dict)
    
    def test_breach_detection(self):
        """Testa detecção de violação"""
        system = BreachNotificationSystem()
        
        breach_id = system.detect_breach(
            title="Test Breach",
            description="Test description",
            breach_type=BreachType.UNAUTHORIZED_ACCESS,
            severity=BreachSeverity.MEDIUM,
            affected_users=50
        )
        
        self.assertIsNotNone(breach_id)
        self.assertIn(breach_id, system.breaches)
        
        breach = system.breaches[breach_id]
        self.assertEqual(breach.title, "Test Breach")
        self.assertEqual(breach.severity, BreachSeverity.MEDIUM)
        self.assertEqual(breach.affected_users, 50)
    
    def test_breach_impact_assessment(self):
        """Testa avaliação de impacto da violação"""
        system = BreachNotificationSystem()
        
        breach_id = system.detect_breach(
            title="Critical Breach",
            description="Critical description",
            breach_type=BreachType.DATA_EXFILTRATION,
            severity=BreachSeverity.CRITICAL,
            affected_users=1000,
            affected_data_categories=["personal_data", "financial_data"]
        )
        
        impact = system.assess_breach_impact(breach_id)
        
        self.assertIsInstance(impact, dict)
        self.assertIn('severity_score', impact)
        self.assertIn('compliance_impact', impact)
        self.assertIn('financial_impact', impact)
        self.assertIn('notification_required', impact)
        
        # Verificar se score de severidade foi calculado
        self.assertGreater(impact['severity_score'], 0)
    
    def test_breach_status_update(self):
        """Testa atualização de status da violação"""
        system = BreachNotificationSystem()
        
        breach_id = system.detect_breach(
            title="Test Breach",
            description="Test description",
            breach_type=BreachType.SYSTEM_COMPROMISE,
            severity=BreachSeverity.HIGH
        )
        
        # Atualizar status
        success = system.update_breach_status(
            breach_id, 
            BreachStatus.CONTAINED, 
            "Violação contida com sucesso"
        )
        
        self.assertTrue(success)
        
        breach = system.breaches[breach_id]
        self.assertEqual(breach.status, BreachStatus.CONTAINED)
        self.assertIsNotNone(breach.contained_at)
    
    def test_breach_report_generation(self):
        """Testa geração de relatório de violação"""
        system = BreachNotificationSystem()
        
        breach_id = system.detect_breach(
            title="Report Test Breach",
            description="Test for report generation",
            breach_type=BreachType.CONFIGURATION_ERROR,
            severity=BreachSeverity.LOW,
            affected_users=10
        )
        
        report = system.generate_breach_report(breach_id)
        
        self.assertIsInstance(report, dict)
        self.assertEqual(report['breach_id'], breach_id)
        self.assertIn('title', report)
        self.assertIn('timeline', report)
        self.assertIn('impact_assessment', report)

class TestComplianceIntegration(unittest.TestCase):
    """Testes de integração do framework de compliance"""
    
    def setUp(self):
        """Configuração inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Criar estrutura completa
        os.makedirs('data/compliance', exist_ok=True)
        os.makedirs('logs/compliance', exist_ok=True)
        os.makedirs('config/compliance', exist_ok=True)
        os.makedirs('docs/compliance', exist_ok=True)
    
    def tearDown(self):
        """Limpeza"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_compliance_workflow(self):
        """Testa workflow completo de compliance"""
        # 1. Setup do compliance framework
        compliance_manager = ComplianceManager()
        success = compliance_manager.run_compliance_setup()
        self.assertTrue(success)
        
        # 2. Sistema DPO
        dpo = DPOSystem()
        
        # 3. Gerenciador de consentimento
        consent_manager = ConsentManager()
        
        # 4. Direitos dos titulares
        rights_manager = DataSubjectRightsManager()
        
        # 5. Sistema de violações
        breach_system = BreachNotificationSystem()
        
        # Testar integração: criar consentimento e depois solicitar dados
        user_id = "test_user_123"
        
        # Criar consentimento
        consent_id = consent_manager.create_consent_record(
            user_id=user_id,
            consent_type=ConsentType.ANALYTICS
        )
        
        # Verificar se consentimento está ativo
        has_consent = consent_manager.check_consent(user_id, ConsentType.ANALYTICS)
        self.assertTrue(has_consent)
        
        # Criar solicitação de dados
        request_id = rights_manager.create_data_request(
            user_id=user_id,
            right_type=DataRightType.ACCESS
        )
        
        # Processar solicitação
        user_data = rights_manager.process_access_request(request_id)
        self.assertIsInstance(user_data, dict)
        
        # Criar incidente se necessário
        if not has_consent:
            breach_id = breach_system.detect_breach(
                title="Consentimento não obtido",
                description="Usuário acessou dados sem consentimento",
                breach_type=BreachType.UNAUTHORIZED_ACCESS,
                severity=BreachSeverity.MEDIUM,
                affected_users=1
            )
            self.assertIsNotNone(breach_id)
    
    def test_compliance_dashboard_data(self):
        """Testa geração de dados para dashboard"""
        # Setup inicial
        compliance_manager = ComplianceManager()
        compliance_manager.run_compliance_setup()
        
        dpo = DPOSystem()
        consent_manager = ConsentManager()
        rights_manager = DataSubjectRightsManager()
        breach_system = BreachNotificationSystem()
        
        # Gerar dados de teste
        consent_manager.create_consent_record("user1", ConsentType.ANALYTICS)
        consent_manager.create_consent_record("user2", ConsentType.MARKETING)
        
        rights_manager.create_data_request("user1", DataRightType.ACCESS)
        
        breach_system.detect_breach(
            title="Test Breach",
            description="Test",
            breach_type=BreachType.UNAUTHORIZED_ACCESS,
            severity=BreachSeverity.LOW
        )
        
        # Obter dados do dashboard
        compliance_dashboard = compliance_manager.get_dashboard_data()
        consent_dashboard = consent_manager.get_dashboard_data()
        rights_dashboard = rights_manager.get_dashboard_data()
        breach_dashboard = breach_system.get_dashboard_data()
        
        # Verificar se todos os dashboards retornam dados válidos
        self.assertIsInstance(compliance_dashboard, dict)
        self.assertIsInstance(consent_dashboard, dict)
        self.assertIsInstance(rights_dashboard, dict)
        self.assertIsInstance(breach_dashboard, dict)
        
        # Verificar se têm campos obrigatórios
        for dashboard in [compliance_dashboard, consent_dashboard, rights_dashboard, breach_dashboard]:
            self.assertIn('tracing_id', dashboard)
            self.assertIn('timestamp', dashboard)

if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2) 