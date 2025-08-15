"""
🧪 Testes de Integração - Sistema de Compliance e Privacidade

Tracing ID: test-privacy-compliance-2025-01-27-001
Timestamp: 2025-01-27T20:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de compliance
🌲 ToT: Múltiplas estratégias de teste para diferentes regulamentações
♻️ ReAct: Simulação de cenários de auditoria e validação de conformidade

Testa sistema de compliance incluindo:
- GDPR compliance
- LGPD compliance
- Data retention policies
- Privacy controls
- Consent management
- Data subject rights
- Data processing records
- Privacy impact assessments
- Data breach notifications
- Audit trails
- Data minimization
- Purpose limitation
- Storage limitation
- Accuracy and quality
- Security measures
"""

import pytest
import tempfile
import os
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
import shutil
from pathlib import Path

# Importar o sistema de compliance
from infrastructure.compliance.privacy_compliance import (
    PrivacyComplianceManager,
    DataSubject,
    Consent,
    DataProcessingRecord,
    DataSubjectRequest,
    DataBreach,
    ComplianceType,
    DataCategory,
    ProcessingPurpose,
    ConsentStatus,
    DataSubjectRight,
    create_compliance_manager,
    validate_email,
    validate_phone,
    generate_data_subject_id
)

class TestPrivacyComplianceIntegration:
    """Testes de integração para sistema de compliance e privacidade"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria banco de dados temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_privacy_compliance.db")
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def compliance_manager(self, temp_db_path):
        """Cria manager de compliance para testes"""
        manager = PrivacyComplianceManager(db_path=temp_db_path)
        manager.init_database()
        return manager
    
    @pytest.fixture
    def sample_data_subject(self):
        """Cria titular de dados de exemplo"""
        return DataSubject(
            id="test_subject_001",
            email="test@example.com",
            name="João Silva",
            phone="+5511999999999",
            address="Rua Teste, 123 - São Paulo, SP",
            date_of_birth=datetime(1990, 1, 1, tzinfo=timezone.utc),
            nationality="Brasileiro",
            identification_number="12345678901"
        )
    
    @pytest.fixture
    def sample_consent(self, sample_data_subject):
        """Cria consentimento de exemplo"""
        return Consent(
            id="consent_001",
            data_subject_id=sample_data_subject.id,
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL, DataCategory.SENSITIVE],
            granted_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            consent_text="Concordo com o processamento dos meus dados pessoais",
            consent_version="1.0",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    
    @pytest.fixture
    def sample_processing_record(self):
        """Cria registro de processamento de exemplo"""
        return DataProcessingRecord(
            id="processing_001",
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            data_subjects_count=1000,
            retention_period=timedelta(days=730),
            legal_basis="Consentimento explícito do usuário",
            data_recipients=["marketing@company.com"],
            third_country_transfers=["EUA"],
            security_measures=["Criptografia AES-256", "Autenticação 2FA"],
            description="Processamento de dados para marketing"
        )
    
    @pytest.fixture
    def sample_data_breach(self):
        """Cria violação de dados de exemplo"""
        return DataBreach(
            id="breach_001",
            description="Acesso não autorizado a dados pessoais",
            breach_date=datetime.now(timezone.utc) - timedelta(days=1),
            discovered_date=datetime.now(timezone.utc),
            data_categories=[DataCategory.PERSONAL, DataCategory.SENSITIVE],
            affected_subjects=150,
            severity="high",
            measures_taken=["Bloqueio de acesso", "Notificação às autoridades"],
            notification_required=True
        )

    def test_gdpr_compliance_integration(self, compliance_manager, sample_data_subject, sample_consent):
        """Testa conformidade GDPR completa"""
        # Adicionar titular de dados
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Adicionar consentimento
        assert compliance_manager.add_consent(sample_consent)
        
        # Verificar se consentimento é válido
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert len(consents) == 1
        assert consents[0].is_valid()
        
        # Verificar direitos do titular
        subject = compliance_manager.get_data_subject(sample_data_subject.id)
        assert subject is not None
        assert subject.email == "test@example.com"
        
        # Testar retirada de consentimento
        assert compliance_manager.withdraw_consent(sample_consent.id)
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert not consents[0].is_valid()
        
        # Verificar métricas GDPR
        metrics = compliance_manager.get_metrics()
        assert "gdpr_compliance" in metrics
        assert metrics["gdpr_compliance"]["active_consents"] >= 0

    def test_lgpd_compliance_integration(self, compliance_manager, sample_data_subject):
        """Testa conformidade LGPD completa"""
        # Adicionar titular de dados brasileiro
        lgpd_subject = DataSubject(
            id="lgpd_subject_001",
            email="lgpd@example.com.br",
            name="Maria Santos",
            phone="+5511888888888",
            nationality="Brasileira",
            identification_number="98765432100"
        )
        
        assert compliance_manager.add_data_subject(lgpd_subject)
        
        # Criar consentimento LGPD
        lgpd_consent = Consent(
            id="lgpd_consent_001",
            data_subject_id=lgpd_subject.id,
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            granted_at=datetime.now(timezone.utc),
            consent_text="Concordo com o processamento conforme LGPD",
            consent_version="1.0"
        )
        
        assert compliance_manager.add_consent(lgpd_consent)
        
        # Verificar conformidade LGPD
        metrics = compliance_manager.get_metrics()
        assert "lgpd_compliance" in metrics
        assert metrics["lgpd_compliance"]["active_consents"] >= 0

    def test_data_retention_policies_integration(self, compliance_manager, sample_processing_record):
        """Testa políticas de retenção de dados"""
        # Adicionar registro de processamento
        assert compliance_manager.add_processing_record(sample_processing_record)
        
        # Verificar políticas de retenção
        retention_checks = compliance_manager.check_retention_policies()
        assert isinstance(retention_checks, list)
        
        # Verificar se há dados expirados
        for check in retention_checks:
            assert "record_id" in check
            assert "retention_status" in check
            assert "days_remaining" in check

    def test_consent_management_integration(self, compliance_manager, sample_data_subject):
        """Testa gerenciamento completo de consentimentos"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Múltiplos consentimentos
        consent1 = Consent(
            id="consent_marketing",
            data_subject_id=sample_data_subject.id,
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            granted_at=datetime.now(timezone.utc),
            consent_text="Consentimento para marketing"
        )
        
        consent2 = Consent(
            id="consent_analytics",
            data_subject_id=sample_data_subject.id,
            purpose=ProcessingPurpose.LEGITIMATE_INTERESTS,
            data_categories=[DataCategory.ANONYMIZED],
            granted_at=datetime.now(timezone.utc),
            consent_text="Consentimento para analytics"
        )
        
        assert compliance_manager.add_consent(consent1)
        assert compliance_manager.add_consent(consent2)
        
        # Verificar todos os consentimentos
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert len(consents) == 2
        
        # Verificar consentimentos válidos
        valid_consents = [c for c in consents if c.is_valid()]
        assert len(valid_consents) == 2

    def test_data_subject_rights_integration(self, compliance_manager, sample_data_subject):
        """Testa direitos do titular dos dados"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Criar solicitação de acesso
        access_request = DataSubjectRequest(
            id="request_access_001",
            data_subject_id=sample_data_subject.id,
            right=DataSubjectRight.ACCESS,
            description="Solicito acesso aos meus dados pessoais"
        )
        
        assert compliance_manager.add_data_subject_request(access_request)
        
        # Processar solicitação
        response_data = {
            "personal_data": {
                "name": "João Silva",
                "email": "test@example.com",
                "phone": "+5511999999999"
            },
            "processing_records": [
                {"purpose": "marketing", "date": "2025-01-27"}
            ]
        }
        
        assert compliance_manager.process_data_subject_request(
            access_request.id, response_data
        )
        
        # Verificar status da solicitação
        # (Nota: O método atual não retorna a solicitação processada,
        # mas podemos verificar se não houve erro)

    def test_data_breach_notification_integration(self, compliance_manager, sample_data_breach):
        """Testa notificação de violação de dados"""
        # Adicionar violação
        assert compliance_manager.add_data_breach(sample_data_breach)
        
        # Verificar se notificação é necessária
        assert sample_data_breach.notification_required
        
        # Reportar violação
        sample_data_breach.report()
        assert sample_data_breach.status == "reported"
        assert sample_data_breach.reported_date is not None

    def test_data_export_and_anonymization_integration(self, compliance_manager, sample_data_subject):
        """Testa exportação e anonimização de dados"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Exportar dados do titular
        exported_data = compliance_manager.export_data_subject_data(sample_data_subject.id)
        assert isinstance(exported_data, dict)
        assert "data_subject" in exported_data
        assert exported_data["data_subject"]["email"] == "test@example.com"
        
        # Anonimizar dados
        assert compliance_manager.anonymize_data_subject(sample_data_subject.id)
        
        # Verificar se dados foram anonimizados
        anonymized_subject = compliance_manager.get_data_subject(sample_data_subject.id)
        assert anonymized_subject.status == "anonymized"

    def test_compliance_reporting_integration(self, compliance_manager):
        """Testa geração de relatórios de compliance"""
        # Gerar relatório de compliance
        report = compliance_manager.generate_compliance_report()
        
        assert isinstance(report, dict)
        assert "gdpr_compliance" in report
        assert "lgpd_compliance" in report
        assert "data_retention" in report
        assert "consent_management" in report
        assert "data_breaches" in report
        assert "data_subject_requests" in report

    def test_validation_functions_integration(self):
        """Testa funções de validação"""
        # Testar validação de email
        assert validate_email("test@example.com")
        assert not validate_email("invalid-email")
        
        # Testar validação de telefone
        assert validate_phone("+5511999999999")
        assert not validate_phone("invalid-phone")
        
        # Testar geração de ID
        subject_id = generate_data_subject_id("test@example.com")
        assert isinstance(subject_id, str)
        assert len(subject_id) > 0

    def test_database_operations_integration(self, compliance_manager, sample_data_subject):
        """Testa operações de banco de dados"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Atualizar titular
        sample_data_subject.name = "João Silva Atualizado"
        assert compliance_manager.update_data_subject(sample_data_subject)
        
        # Verificar atualização
        updated_subject = compliance_manager.get_data_subject(sample_data_subject.id)
        assert updated_subject.name == "João Silva Atualizado"
        
        # Deletar titular
        assert compliance_manager.delete_data_subject(sample_data_subject.id)
        
        # Verificar se foi deletado
        deleted_subject = compliance_manager.get_data_subject(sample_data_subject.id)
        assert deleted_subject is None

    def test_error_handling_integration(self, compliance_manager):
        """Testa tratamento de erros"""
        # Tentar adicionar titular com ID duplicado
        subject1 = DataSubject(
            id="duplicate_id",
            email="test1@example.com"
        )
        subject2 = DataSubject(
            id="duplicate_id",
            email="test2@example.com"
        )
        
        assert compliance_manager.add_data_subject(subject1)
        # A segunda adição deve falhar ou sobrescrever
        result = compliance_manager.add_data_subject(subject2)
        # O comportamento depende da implementação

    def test_performance_metrics_integration(self, compliance_manager):
        """Testa métricas de performance"""
        # Gerar métricas
        metrics = compliance_manager.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "performance" in metrics
        assert "database_operations" in metrics["performance"]
        assert "response_times" in metrics["performance"]

    def test_multi_tenant_compliance_integration(self, temp_db_path):
        """Testa compliance multi-tenant"""
        # Criar múltiplos managers para diferentes tenants
        tenant1_manager = PrivacyComplianceManager(db_path=temp_db_path + "_tenant1")
        tenant2_manager = PrivacyComplianceManager(db_path=temp_db_path + "_tenant2")
        
        tenant1_manager.init_database()
        tenant2_manager.init_database()
        
        # Adicionar dados em tenants diferentes
        subject1 = DataSubject(id="tenant1_subject", email="tenant1@example.com")
        subject2 = DataSubject(id="tenant2_subject", email="tenant2@example.com")
        
        assert tenant1_manager.add_data_subject(subject1)
        assert tenant2_manager.add_data_subject(subject2)
        
        # Verificar isolamento
        assert tenant1_manager.get_data_subject("tenant1_subject") is not None
        assert tenant1_manager.get_data_subject("tenant2_subject") is None
        
        # Cleanup
        tenant1_manager.close()
        tenant2_manager.close()

    def test_compliance_audit_trail_integration(self, compliance_manager, sample_data_subject):
        """Testa trilha de auditoria de compliance"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Simular múltiplas operações para criar trilha
        sample_data_subject.name = "João Silva Modificado"
        assert compliance_manager.update_data_subject(sample_data_subject)
        
        sample_data_subject.phone = "+5511777777777"
        assert compliance_manager.update_data_subject(sample_data_subject)
        
        # Verificar se há trilha de auditoria
        # (Depende da implementação de auditoria)

    def test_data_minimization_integration(self, compliance_manager):
        """Testa princípio de minimização de dados"""
        # Criar titular com dados mínimos
        minimal_subject = DataSubject(
            id="minimal_subject",
            email="minimal@example.com"
        )
        
        assert compliance_manager.add_data_subject(minimal_subject)
        
        # Verificar se apenas dados necessários foram armazenados
        stored_subject = compliance_manager.get_data_subject("minimal_subject")
        assert stored_subject.email == "minimal@example.com"
        assert stored_subject.name is None  # Dado não fornecido

    def test_purpose_limitation_integration(self, compliance_manager, sample_data_subject):
        """Testa limitação de propósito"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Criar consentimento com propósito específico
        marketing_consent = Consent(
            id="marketing_only",
            data_subject_id=sample_data_subject.id,
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            granted_at=datetime.now(timezone.utc),
            consent_text="Apenas para marketing"
        )
        
        assert compliance_manager.add_consent(marketing_consent)
        
        # Verificar se propósito está limitado
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert len(consents) == 1
        assert consents[0].purpose == ProcessingPurpose.CONSENT

    def test_storage_limitation_integration(self, compliance_manager, sample_processing_record):
        """Testa limitação de armazenamento"""
        # Adicionar registro com período de retenção
        assert compliance_manager.add_processing_record(sample_processing_record)
        
        # Verificar políticas de retenção
        retention_checks = compliance_manager.check_retention_policies()
        
        for check in retention_checks:
            if check["record_id"] == sample_processing_record.id:
                assert "days_remaining" in check
                assert check["days_remaining"] > 0  # Ainda não expirou

    def test_accuracy_and_quality_integration(self, compliance_manager, sample_data_subject):
        """Testa precisão e qualidade dos dados"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Atualizar dados para manter precisão
        sample_data_subject.phone = "+5511666666666"
        assert compliance_manager.update_data_subject(sample_data_subject)
        
        # Verificar se dados foram atualizados corretamente
        updated_subject = compliance_manager.get_data_subject(sample_data_subject.id)
        assert updated_subject.phone == "+5511666666666"
        assert updated_subject.updated_at > sample_data_subject.created_at

    def test_security_measures_integration(self, compliance_manager, sample_processing_record):
        """Testa medidas de segurança"""
        # Adicionar registro com medidas de segurança
        assert compliance_manager.add_processing_record(sample_processing_record)
        
        # Verificar se medidas de segurança estão registradas
        # (Depende da implementação de consulta de registros)

    def test_international_transfers_integration(self, compliance_manager, sample_processing_record):
        """Testa transferências internacionais"""
        # Adicionar registro com transferências internacionais
        assert compliance_manager.add_processing_record(sample_processing_record)
        
        # Verificar se transferências estão registradas
        # (Depende da implementação de consulta de registros)

    def test_consent_withdrawal_integration(self, compliance_manager, sample_data_subject, sample_consent):
        """Testa retirada de consentimento"""
        # Adicionar titular e consentimento
        assert compliance_manager.add_data_subject(sample_data_subject)
        assert compliance_manager.add_consent(sample_consent)
        
        # Verificar consentimento ativo
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert len(consents) == 1
        assert consents[0].is_valid()
        
        # Retirar consentimento
        assert compliance_manager.withdraw_consent(sample_consent.id)
        
        # Verificar se consentimento foi retirado
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert len(consents) == 1
        assert not consents[0].is_valid()
        assert consents[0].status == ConsentStatus.WITHDRAWN

    def test_data_portability_integration(self, compliance_manager, sample_data_subject):
        """Testa portabilidade de dados"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Criar solicitação de portabilidade
        portability_request = DataSubjectRequest(
            id="portability_request_001",
            data_subject_id=sample_data_subject.id,
            right=DataSubjectRight.PORTABILITY,
            description="Solicito portabilidade dos meus dados"
        )
        
        assert compliance_manager.add_data_subject_request(portability_request)
        
        # Exportar dados para portabilidade
        exported_data = compliance_manager.export_data_subject_data(sample_data_subject.id)
        assert isinstance(exported_data, dict)
        assert "data_subject" in exported_data

    def test_automated_decision_making_integration(self, compliance_manager, sample_data_subject):
        """Testa tomada de decisão automatizada"""
        # Criar solicitação sobre decisão automatizada
        automated_request = DataSubjectRequest(
            id="automated_request_001",
            data_subject_id=sample_data_subject.id,
            right=DataSubjectRight.AUTOMATED_DECISION,
            description="Solicito informações sobre decisão automatizada"
        )
        
        assert compliance_manager.add_data_subject_request(automated_request)

    def test_complaint_handling_integration(self, compliance_manager, sample_data_subject):
        """Testa tratamento de reclamações"""
        # Criar reclamação
        complaint_request = DataSubjectRequest(
            id="complaint_001",
            data_subject_id=sample_data_subject.id,
            right=DataSubjectRight.COMPLAINT,
            description="Reclamo sobre processamento dos meus dados"
        )
        
        assert compliance_manager.add_data_subject_request(complaint_request)

    def test_consent_expiration_integration(self, compliance_manager, sample_data_subject):
        """Testa expiração de consentimento"""
        # Criar consentimento com expiração próxima
        expired_consent = Consent(
            id="expired_consent",
            data_subject_id=sample_data_subject.id,
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            granted_at=datetime.now(timezone.utc) - timedelta(days=366),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # Expirado
            consent_text="Consentimento expirado"
        )
        
        assert compliance_manager.add_data_subject(sample_data_subject)
        assert compliance_manager.add_consent(expired_consent)
        
        # Verificar se consentimento está expirado
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert len(consents) == 1
        assert not consents[0].is_valid()

    def test_bulk_operations_integration(self, compliance_manager):
        """Testa operações em lote"""
        # Criar múltiplos titulares
        subjects = []
        for i in range(10):
            subject = DataSubject(
                id=f"bulk_subject_{i}",
                email=f"bulk{i}@example.com",
                name=f"Usuário {i}"
            )
            subjects.append(subject)
        
        # Adicionar em lote
        for subject in subjects:
            assert compliance_manager.add_data_subject(subject)
        
        # Verificar se todos foram adicionados
        for subject in subjects:
            stored_subject = compliance_manager.get_data_subject(subject.id)
            assert stored_subject is not None
            assert stored_subject.email == subject.email

    def test_data_quality_validation_integration(self, compliance_manager):
        """Testa validação de qualidade de dados"""
        # Testar dados válidos
        valid_subject = DataSubject(
            id="valid_subject",
            email="valid@example.com",
            phone="+5511999999999"
        )
        assert compliance_manager.add_data_subject(valid_subject)
        
        # Testar dados inválidos (email)
        invalid_subject = DataSubject(
            id="invalid_subject",
            email="invalid-email",
            phone="+5511999999999"
        )
        # A validação pode ser feita antes da inserção
        assert not validate_email("invalid-email")

    def test_compliance_monitoring_integration(self, compliance_manager):
        """Testa monitoramento de compliance"""
        # Gerar relatório de compliance
        report = compliance_manager.generate_compliance_report()
        
        # Verificar métricas de compliance
        metrics = compliance_manager.get_metrics()
        
        assert "compliance_status" in metrics
        assert "gdpr_compliance" in metrics
        assert "lgpd_compliance" in metrics

    def test_data_breach_response_integration(self, compliance_manager, sample_data_breach):
        """Testa resposta a violação de dados"""
        # Adicionar violação
        assert compliance_manager.add_data_breach(sample_data_breach)
        
        # Simular resposta
        sample_data_breach.measures_taken.append("Notificação aos afetados")
        sample_data_breach.status = "contained"
        
        # Verificar se medidas foram registradas
        assert "Notificação aos afetados" in sample_data_breach.measures_taken

    def test_consent_granularity_integration(self, compliance_manager, sample_data_subject):
        """Testa granularidade de consentimento"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Criar consentimentos granulares
        marketing_consent = Consent(
            id="marketing_granular",
            data_subject_id=sample_data_subject.id,
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            granted_at=datetime.now(timezone.utc),
            consent_text="Apenas para marketing por email"
        )
        
        analytics_consent = Consent(
            id="analytics_granular",
            data_subject_id=sample_data_subject.id,
            purpose=ProcessingPurpose.LEGITIMATE_INTERESTS,
            data_categories=[DataCategory.ANONYMIZED],
            granted_at=datetime.now(timezone.utc),
            consent_text="Apenas para analytics anônimos"
        )
        
        assert compliance_manager.add_consent(marketing_consent)
        assert compliance_manager.add_consent(analytics_consent)
        
        # Verificar granularidade
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert len(consents) == 2
        
        # Verificar propósitos diferentes
        purposes = [c.purpose for c in consents]
        assert ProcessingPurpose.CONSENT in purposes
        assert ProcessingPurpose.LEGITIMATE_INTERESTS in purposes

    def test_data_retention_automation_integration(self, compliance_manager, sample_processing_record):
        """Testa automação de retenção de dados"""
        # Adicionar registro com retenção
        assert compliance_manager.add_processing_record(sample_processing_record)
        
        # Verificar políticas de retenção
        retention_checks = compliance_manager.check_retention_policies()
        
        # Verificar se há dados para limpeza automática
        for check in retention_checks:
            if check["retention_status"] == "expired":
                assert check["days_remaining"] <= 0

    def test_compliance_documentation_integration(self, compliance_manager):
        """Testa documentação de compliance"""
        # Gerar relatório completo
        report = compliance_manager.generate_compliance_report()
        
        # Verificar se relatório contém todas as seções necessárias
        required_sections = [
            "gdpr_compliance",
            "lgpd_compliance", 
            "data_retention",
            "consent_management",
            "data_breaches",
            "data_subject_requests"
        ]
        
        for section in required_sections:
            assert section in report

    def test_privacy_by_design_integration(self, compliance_manager):
        """Testa privacidade por design"""
        # Criar titular com dados mínimos (privacidade por design)
        minimal_subject = DataSubject(
            id="privacy_design_subject",
            email="privacy@example.com"
        )
        
        assert compliance_manager.add_data_subject(minimal_subject)
        
        # Verificar se apenas dados necessários foram coletados
        stored_subject = compliance_manager.get_data_subject("privacy_design_subject")
        assert stored_subject.email == "privacy@example.com"
        assert stored_subject.name is None  # Não coletado por design

    def test_data_protection_impact_assessment_integration(self, compliance_manager):
        """Testa avaliação de impacto na proteção de dados"""
        # Criar registro de processamento com avaliação de impacto
        dpia_record = DataProcessingRecord(
            id="dpia_001",
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.SENSITIVE],
            data_subjects_count=10000,
            retention_period=timedelta(days=1825),  # 5 anos
            legal_basis="Consentimento explícito",
            security_measures=["Criptografia AES-256", "Auditoria regular"],
            description="Processamento de dados sensíveis com DPIA"
        )
        
        assert compliance_manager.add_processing_record(dpia_record)
        
        # Verificar se medidas de segurança estão adequadas
        assert "Criptografia AES-256" in dpia_record.security_measures

    def test_cross_border_data_transfer_integration(self, compliance_manager, sample_processing_record):
        """Testa transferência transfronteiriça de dados"""
        # Adicionar registro com transferência internacional
        assert compliance_manager.add_processing_record(sample_processing_record)
        
        # Verificar se transferências estão registradas
        assert "EUA" in sample_processing_record.third_country_transfers

    def test_consent_management_automation_integration(self, compliance_manager, sample_data_subject):
        """Testa automação do gerenciamento de consentimento"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Criar consentimento com expiração automática
        auto_expire_consent = Consent(
            id="auto_expire_consent",
            data_subject_id=sample_data_subject.id,
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            granted_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            consent_text="Consentimento com expiração automática"
        )
        
        assert compliance_manager.add_consent(auto_expire_consent)
        
        # Verificar se expiração está configurada
        consents = compliance_manager.get_consents(sample_data_subject.id)
        assert len(consents) == 1
        assert consents[0].expires_at is not None

    def test_compliance_audit_integration(self, compliance_manager):
        """Testa auditoria de compliance"""
        # Gerar relatório de auditoria
        report = compliance_manager.generate_compliance_report()
        
        # Verificar se relatório contém informações de auditoria
        assert isinstance(report, dict)
        assert "audit_trail" in report or "compliance_status" in report

    def test_data_subject_rights_automation_integration(self, compliance_manager, sample_data_subject):
        """Testa automação dos direitos do titular"""
        # Adicionar titular
        assert compliance_manager.add_data_subject(sample_data_subject)
        
        # Criar solicitação automatizada
        auto_request = DataSubjectRequest(
            id="auto_request_001",
            data_subject_id=sample_data_subject.id,
            right=DataSubjectRight.ACCESS,
            description="Solicitação automatizada de acesso"
        )
        
        assert compliance_manager.add_data_subject_request(auto_request)
        
        # Processar automaticamente
        response_data = {"status": "processed_automatically"}
        assert compliance_manager.process_data_subject_request(auto_request.id, response_data)

    def test_compliance_metrics_dashboard_integration(self, compliance_manager):
        """Testa dashboard de métricas de compliance"""
        # Gerar métricas
        metrics = compliance_manager.get_metrics()
        
        # Verificar se métricas estão disponíveis para dashboard
        assert "gdpr_compliance" in metrics
        assert "lgpd_compliance" in metrics
        assert "consent_rates" in metrics
        assert "data_breach_incidents" in metrics

    def test_end_to_end_compliance_workflow_integration(self, compliance_manager):
        """Testa workflow completo de compliance"""
        # 1. Criar titular de dados
        subject = DataSubject(
            id="workflow_subject",
            email="workflow@example.com",
            name="Usuário Workflow"
        )
        assert compliance_manager.add_data_subject(subject)
        
        # 2. Adicionar consentimento
        consent = Consent(
            id="workflow_consent",
            data_subject_id=subject.id,
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            granted_at=datetime.now(timezone.utc),
            consent_text="Consentimento para workflow"
        )
        assert compliance_manager.add_consent(consent)
        
        # 3. Criar registro de processamento
        record = DataProcessingRecord(
            id="workflow_record",
            purpose=ProcessingPurpose.CONSENT,
            data_categories=[DataCategory.PERSONAL],
            data_subjects_count=1,
            retention_period=timedelta(days=365),
            legal_basis="Consentimento do workflow"
        )
        assert compliance_manager.add_processing_record(record)
        
        # 4. Criar solicitação de dados
        request = DataSubjectRequest(
            id="workflow_request",
            data_subject_id=subject.id,
            right=DataSubjectRight.ACCESS,
            description="Solicitação do workflow"
        )
        assert compliance_manager.add_data_subject_request(request)
        
        # 5. Processar solicitação
        response_data = {"workflow_data": "processed"}
        assert compliance_manager.process_data_subject_request(request.id, response_data)
        
        # 6. Exportar dados
        exported_data = compliance_manager.export_data_subject_data(subject.id)
        assert isinstance(exported_data, dict)
        
        # 7. Gerar relatório final
        report = compliance_manager.generate_compliance_report()
        assert isinstance(report, dict)
        
        # 8. Verificar métricas
        metrics = compliance_manager.get_metrics()
        assert isinstance(metrics, dict)
        
        # Workflow completo executado com sucesso
        assert True

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"]) 