"""
🧪 Testes de Cobertura Completa - Serviços Backend
🎯 Objetivo: Garantir cobertura >90% para todos os serviços
📅 Data: 2025-01-27
🔗 Tracing ID: BACKEND_COVERAGE_001
📋 Ruleset: enterprise_control_layer.yaml

Testes unitários para serviços que ainda não têm cobertura adequada.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Any

# Importar serviços que precisam de cobertura
from backend.app.services.credential_encryption import CredentialEncryptionService
from backend.app.services.credential_audit import CredentialAuditService, AuditEvent, AuditEventType, AuditSeverity
from backend.app.services.credentials_audit_service import CredentialsAuditService
from backend.app.services.compliance_report_v1 import gerar_relatorio_conformidade
from backend.app.services.performance_utils_v1 import medir_tempo_execucao
from backend.app.services.export_templates_v1 import ExportTemplatesService
from backend.app.services.export_zip_v1 import ExportZipService
from backend.app.services.distributed_processing_v1 import DistributedProcessingService
from backend.app.services.security_utils_v1 import SecurityUtilsService
from backend.app.services.cleanup_v1 import CleanupService
from backend.app.services.export_integrity_notify_v1 import ExportIntegrityNotifyService
from backend.app.services.keyword_gap_suggestion_v1 import KeywordGapSuggestionService
from backend.app.services.keyword_classification_rules_v1 import KeywordClassificationRulesService
from backend.app.services.ranking_explain_v1 import RankingExplainService
from backend.app.services.custom_filters_v1 import CustomFiltersService
from backend.app.services.ranking_config_v1 import RankingConfigService
from backend.app.services.ranking_feedback_v1 import RankingFeedbackService
from backend.app.services.external_api_service import ExternalApiService
from backend.app.services.payments_service import PaymentsService


class TestCredentialEncryptionService:
    """Testes para o serviço de criptografia de credenciais"""
    
    @pytest.fixture
    def encryption_service(self):
        """Cria instância do serviço de criptografia"""
        with patch.dict(os.environ, {'CREDENTIAL_MASTER_KEY': 'test_master_key_32_chars_long'}):
            return CredentialEncryptionService()
    
    def test_initialization(self, encryption_service):
        """Testa inicialização do serviço"""
        assert encryption_service.master_key == 'test_master_key_32_chars_long'
        assert encryption_service.algorithm == 'AES'
        assert encryption_service.key_size == 256
        assert encryption_service.kdf_iterations == 100000
    
    def test_initialization_missing_key(self):
        """Testa inicialização sem chave mestra"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="CREDENTIAL_MASTER_KEY deve ser fornecida"):
                CredentialEncryptionService()
    
    def test_encrypt_decrypt_credential(self, encryption_service):
        """Testa criptografia e descriptografia de credencial"""
        test_credential = "test_api_key_12345"
        provider = "test_provider"
        
        # Criptografar
        encrypted = encryption_service.encrypt_credential(test_credential, provider)
        assert encrypted != test_credential
        assert len(encrypted) > len(test_credential)
        
        # Descriptografar
        decrypted = encryption_service.decrypt_credential(encrypted, provider)
        assert decrypted == test_credential
    
    def test_encrypt_decrypt_with_metadata(self, encryption_service):
        """Testa criptografia com metadados"""
        test_credential = "test_api_key_12345"
        provider = "test_provider"
        metadata = {"user_id": "123", "created_at": "2025-01-27"}
        
        # Criptografar com metadados
        encrypted = encryption_service.encrypt_credential_with_metadata(
            test_credential, provider, metadata
        )
        
        # Descriptografar e verificar metadados
        decrypted, retrieved_metadata = encryption_service.decrypt_credential_with_metadata(
            encrypted, provider
        )
        
        assert decrypted == test_credential
        assert retrieved_metadata == metadata
    
    def test_rotate_master_key(self, encryption_service):
        """Testa rotação da chave mestra"""
        old_key = encryption_service.master_key
        new_key = "new_master_key_32_chars_long_123"
        
        # Criptografar com chave antiga
        test_credential = "test_api_key_12345"
        encrypted = encryption_service.encrypt_credential(test_credential, "test_provider")
        
        # Rotacionar chave
        encryption_service.rotate_master_key(new_key)
        assert encryption_service.master_key == new_key
        
        # Verificar que ainda consegue descriptografar
        decrypted = encryption_service.decrypt_credential(encrypted, "test_provider")
        assert decrypted == test_credential
    
    def test_is_healthy(self, encryption_service):
        """Testa verificação de saúde do serviço"""
        assert encryption_service.is_healthy() == True
    
    def test_get_metrics(self, encryption_service):
        """Testa obtenção de métricas"""
        # Fazer algumas operações
        test_credential = "test_api_key_12345"
        encryption_service.encrypt_credential(test_credential, "test_provider")
        
        metrics = encryption_service.get_metrics()
        assert "encryption_count" in metrics
        assert "decryption_count" in metrics
        assert "error_count" in metrics
        assert metrics["encryption_count"] > 0


class TestCredentialAuditService:
    """Testes para o serviço de auditoria de credenciais"""
    
    @pytest.fixture
    def audit_service(self):
        """Cria instância do serviço de auditoria"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('[]')
            audit_file = f.name
        
        service = CredentialAuditService(audit_file_path=audit_file)
        yield service
        
        # Cleanup
        os.unlink(audit_file)
    
    def test_initialization(self, audit_service):
        """Testa inicialização do serviço"""
        assert audit_service.audit_file_path is not None
        assert audit_service.max_events == 10000
        assert audit_service.retention_days == 90
    
    def test_log_credential_access(self, audit_service):
        """Testa log de acesso a credencial"""
        event = audit_service.log_credential_access(
            user_id="test_user",
            provider="test_provider",
            action="read",
            success=True
        )
        
        assert event.event_type == AuditEventType.CREDENTIAL_ACCESSED
        assert event.user_id == "test_user"
        assert event.provider == "test_provider"
        assert event.success == True
    
    def test_log_credential_validation(self, audit_service):
        """Testa log de validação de credencial"""
        event = audit_service.log_credential_validation(
            user_id="test_user",
            provider="test_provider",
            success=True,
            error_message=None
        )
        
        assert event.event_type == AuditEventType.CREDENTIAL_VALIDATED
        assert event.user_id == "test_user"
        assert event.provider == "test_provider"
        assert event.success == True
    
    def test_log_credential_creation(self, audit_service):
        """Testa log de criação de credencial"""
        event = audit_service.log_credential_creation(
            user_id="test_user",
            provider="test_provider",
            success=True
        )
        
        assert event.event_type == AuditEventType.CREDENTIAL_CREATED
        assert event.user_id == "test_user"
        assert event.provider == "test_provider"
        assert event.success == True
    
    def test_log_credential_deletion(self, audit_service):
        """Testa log de exclusão de credencial"""
        event = audit_service.log_credential_deletion(
            user_id="test_user",
            provider="test_provider",
            success=True
        )
        
        assert event.event_type == AuditEventType.CREDENTIAL_DELETED
        assert event.user_id == "test_user"
        assert event.provider == "test_provider"
        assert event.success == True
    
    def test_get_audit_events(self, audit_service):
        """Testa obtenção de eventos de auditoria"""
        # Criar alguns eventos
        audit_service.log_credential_access("user1", "provider1", "read", True)
        audit_service.log_credential_validation("user2", "provider2", True)
        
        events = audit_service.get_audit_events(
            user_id="user1",
            provider="provider1",
            event_type=AuditEventType.CREDENTIAL_ACCESSED,
            start_date=datetime.now(timezone.utc) - timedelta(days=1),
            end_date=datetime.now(timezone.utc) + timedelta(days=1)
        )
        
        assert len(events) > 0
        assert all(event.user_id == "user1" for event in events)
    
    def test_get_audit_statistics(self, audit_service):
        """Testa obtenção de estatísticas de auditoria"""
        # Criar eventos de teste
        audit_service.log_credential_access("user1", "provider1", "read", True)
        audit_service.log_credential_access("user1", "provider1", "write", False)
        audit_service.log_credential_validation("user2", "provider2", True)
        
        stats = audit_service.get_audit_statistics(
            start_date=datetime.now(timezone.utc) - timedelta(days=1),
            end_date=datetime.now(timezone.utc) + timedelta(days=1)
        )
        
        assert "total_events" in stats
        assert "successful_events" in stats
        assert "failed_events" in stats
        assert "events_by_type" in stats
        assert "events_by_provider" in stats
        assert "events_by_user" in stats
    
    def test_cleanup_old_events(self, audit_service):
        """Testa limpeza de eventos antigos"""
        # Criar evento antigo
        old_event = AuditEvent(
            event_id="old_event",
            event_type=AuditEventType.CREDENTIAL_ACCESSED,
            timestamp=datetime.now(timezone.utc) - timedelta(days=100),
            user_id="old_user",
            provider="old_provider",
            severity=AuditSeverity.LOW
        )
        
        audit_service._write_event(old_event)
        
        # Limpar eventos antigos
        audit_service.cleanup_old_events()
        
        # Verificar se evento antigo foi removido
        events = audit_service.get_audit_events()
        assert not any(event.event_id == "old_event" for event in events)
    
    def test_is_healthy(self, audit_service):
        """Testa verificação de saúde do serviço"""
        assert audit_service.is_healthy() == True


class TestComplianceReportService:
    """Testes para o serviço de relatórios de conformidade"""
    
    def test_gerar_relatorio_conformidade_success(self):
        """Testa geração de relatório com sucesso"""
        with tempfile.TemporaryDirectory() as tmp:
            report_path = os.path.join(tmp, 'compliance_report.json')
            
            metricas = {
                'execucoes': 100,
                'usuarios_ativos': 50,
                'taxa_sucesso': 0.95
            }
            
            cobertura = {
                'unit': 95,
                'integration': 85,
                'e2e': 70
            }
            
            falhas = []
            
            result = gerar_relatorio_conformidade(metricas, cobertura, falhas)
            
            assert os.path.exists(result)
            
            with open(result, 'r') as f:
                data = json.load(f)
                assert data['status'] == 'ok'
                assert data['metricas'] == metricas
                assert data['cobertura'] == cobertura
                assert data['falhas'] == falhas
    
    def test_gerar_relatorio_conformidade_falhas(self):
        """Testa geração de relatório com falhas"""
        with tempfile.TemporaryDirectory() as tmp:
            report_path = os.path.join(tmp, 'compliance_report.json')
            
            metricas = {'execucoes': 100}
            cobertura = {'unit': 50}  # Baixa cobertura
            falhas = ['Cobertura de testes insuficiente']
            
            result = gerar_relatorio_conformidade(metricas, cobertura, falhas)
            
            with open(result, 'r') as f:
                data = json.load(f)
                assert data['status'] == 'falha'
                assert data['falhas'] == falhas


class TestPerformanceUtilsService:
    """Testes para utilitários de performance"""
    
    def test_medir_tempo_execucao(self):
        """Testa medição de tempo de execução"""
        @medir_tempo_execucao
        def funcao_teste():
            import time
            time.sleep(0.1)
            return "resultado"
        
        resultado, tempo = funcao_teste()
        
        assert resultado == "resultado"
        assert tempo >= 0.1
        assert tempo < 0.2  # Com margem de tolerância
    
    def test_medir_tempo_execucao_com_erro(self):
        """Testa medição de tempo com erro"""
        @medir_tempo_execucao
        def funcao_com_erro():
            raise ValueError("Erro de teste")
        
        with pytest.raises(ValueError):
            funcao_com_erro()


class TestExportServices:
    """Testes para serviços de exportação"""
    
    @pytest.fixture
    def export_templates_service(self):
        """Cria instância do serviço de templates de exportação"""
        return ExportTemplatesService()
    
    @pytest.fixture
    def export_zip_service(self):
        """Cria instância do serviço de exportação ZIP"""
        return ExportZipService()
    
    def test_export_templates_service(self, export_templates_service):
        """Testa serviço de templates de exportação"""
        templates = export_templates_service.get_available_templates()
        assert isinstance(templates, list)
        
        # Testar criação de template
        template_data = {
            'name': 'test_template',
            'format': 'csv',
            'fields': ['keyword', 'volume', 'difficulty']
        }
        
        template_id = export_templates_service.create_template(template_data)
        assert template_id is not None
        
        # Testar obtenção de template
        template = export_templates_service.get_template(template_id)
        assert template['name'] == 'test_template'
    
    def test_export_zip_service(self, export_zip_service):
        """Testa serviço de exportação ZIP"""
        with tempfile.TemporaryDirectory() as tmp:
            # Criar arquivos de teste
            test_files = [
                ('file1.txt', 'conteudo1'),
                ('file2.txt', 'conteudo2'),
                ('data.json', '{"key": "value"}')
            ]
            
            file_paths = []
            for filename, content in test_files:
                file_path = os.path.join(tmp, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
                file_paths.append(file_path)
            
            # Criar ZIP
            zip_path = os.path.join(tmp, 'export.zip')
            result = export_zip_service.create_zip(file_paths, zip_path)
            
            assert result == zip_path
            assert os.path.exists(zip_path)
            assert os.path.getsize(zip_path) > 0


class TestDistributedProcessingService:
    """Testes para serviço de processamento distribuído"""
    
    @pytest.fixture
    def distributed_service(self):
        """Cria instância do serviço de processamento distribuído"""
        return DistributedProcessingService()
    
    def test_distributed_service_initialization(self, distributed_service):
        """Testa inicialização do serviço"""
        assert distributed_service is not None
        assert hasattr(distributed_service, 'process_tasks')
    
    def test_process_tasks(self, distributed_service):
        """Testa processamento de tarefas"""
        tasks = [
            {'id': 1, 'data': 'task1'},
            {'id': 2, 'data': 'task2'},
            {'id': 3, 'data': 'task3'}
        ]
        
        results = distributed_service.process_tasks(tasks)
        assert isinstance(results, list)
        assert len(results) == len(tasks)


class TestSecurityUtilsService:
    """Testes para utilitários de segurança"""
    
    @pytest.fixture
    def security_service(self):
        """Cria instância do serviço de segurança"""
        return SecurityUtilsService()
    
    def test_security_service_initialization(self, security_service):
        """Testa inicialização do serviço"""
        assert security_service is not None
    
    def test_validate_input(self, security_service):
        """Testa validação de entrada"""
        # Teste com entrada válida
        assert security_service.validate_input("test_input") == True
        
        # Teste com entrada suspeita
        assert security_service.validate_input("<script>alert('xss')</script>") == False
    
    def test_sanitize_output(self, security_service):
        """Testa sanitização de saída"""
        input_data = "<script>alert('xss')</script>"
        sanitized = security_service.sanitize_output(input_data)
        
        assert "<script>" not in sanitized
        assert "alert" not in sanitized


class TestCleanupService:
    """Testes para serviço de limpeza"""
    
    @pytest.fixture
    def cleanup_service(self):
        """Cria instância do serviço de limpeza"""
        return CleanupService()
    
    def test_cleanup_service_initialization(self, cleanup_service):
        """Testa inicialização do serviço"""
        assert cleanup_service is not None
    
    def test_cleanup_old_files(self, cleanup_service):
        """Testa limpeza de arquivos antigos"""
        with tempfile.TemporaryDirectory() as tmp:
            # Criar arquivo antigo
            old_file = os.path.join(tmp, 'old_file.txt')
            with open(old_file, 'w') as f:
                f.write('old content')
            
            # Modificar timestamp para ser antigo
            old_time = datetime.now(timezone.utc) - timedelta(days=10)
            os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
            
            # Executar limpeza
            result = cleanup_service.cleanup_old_files(tmp, days=7)
            
            assert result > 0
            assert not os.path.exists(old_file)


class TestExportIntegrityNotifyService:
    """Testes para serviço de notificação de integridade de exportação"""
    
    @pytest.fixture
    def integrity_service(self):
        """Cria instância do serviço de integridade"""
        return ExportIntegrityNotifyService()
    
    def test_integrity_service_initialization(self, integrity_service):
        """Testa inicialização do serviço"""
        assert integrity_service is not None
    
    def test_verify_export_integrity(self, integrity_service):
        """Testa verificação de integridade de exportação"""
        with tempfile.TemporaryDirectory() as tmp:
            # Criar arquivo de teste
            test_file = os.path.join(tmp, 'test_export.csv')
            with open(test_file, 'w') as f:
                f.write('keyword,volume,difficulty\n')
                f.write('test,100,0.5\n')
            
            # Verificar integridade
            result = integrity_service.verify_export_integrity(test_file)
            assert result['is_valid'] == True
            assert result['file_size'] > 0
            assert result['line_count'] > 0


class TestKeywordServices:
    """Testes para serviços de keywords"""
    
    @pytest.fixture
    def gap_service(self):
        """Cria instância do serviço de sugestões de gap"""
        return KeywordGapSuggestionService()
    
    @pytest.fixture
    def classification_service(self):
        """Cria instância do serviço de classificação"""
        return KeywordClassificationRulesService()
    
    @pytest.fixture
    def ranking_service(self):
        """Cria instância do serviço de ranking"""
        return RankingExplainService()
    
    def test_gap_suggestion_service(self, gap_service):
        """Testa serviço de sugestões de gap"""
        keywords = ['seo', 'marketing', 'digital']
        suggestions = gap_service.suggest_keyword_gaps(keywords)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    def test_classification_service(self, classification_service):
        """Testa serviço de classificação"""
        keyword = 'seo optimization'
        classification = classification_service.classify_keyword(keyword)
        
        assert isinstance(classification, dict)
        assert 'category' in classification
        assert 'confidence' in classification
    
    def test_ranking_service(self, ranking_service):
        """Testa serviço de ranking"""
        keyword = 'seo optimization'
        explanation = ranking_service.explain_ranking(keyword)
        
        assert isinstance(explanation, dict)
        assert 'factors' in explanation
        assert 'score' in explanation


class TestCustomFiltersService:
    """Testes para serviço de filtros customizados"""
    
    @pytest.fixture
    def filters_service(self):
        """Cria instância do serviço de filtros"""
        return CustomFiltersService()
    
    def test_filters_service_initialization(self, filters_service):
        """Testa inicialização do serviço"""
        assert filters_service is not None
    
    def test_create_filter(self, filters_service):
        """Testa criação de filtro"""
        filter_config = {
            'name': 'test_filter',
            'conditions': [
                {'field': 'volume', 'operator': '>', 'value': 1000}
            ]
        }
        
        filter_id = filters_service.create_filter(filter_config)
        assert filter_id is not None
    
    def test_apply_filter(self, filters_service):
        """Testa aplicação de filtro"""
        data = [
            {'keyword': 'test1', 'volume': 500},
            {'keyword': 'test2', 'volume': 1500},
            {'keyword': 'test3', 'volume': 2000}
        ]
        
        filter_config = {
            'conditions': [
                {'field': 'volume', 'operator': '>', 'value': 1000}
            ]
        }
        
        filtered_data = filters_service.apply_filter(data, filter_config)
        assert len(filtered_data) == 2
        assert all(item['volume'] > 1000 for item in filtered_data)


class TestRankingServices:
    """Testes para serviços de ranking"""
    
    @pytest.fixture
    def ranking_config_service(self):
        """Cria instância do serviço de configuração de ranking"""
        return RankingConfigService()
    
    @pytest.fixture
    def ranking_feedback_service(self):
        """Cria instância do serviço de feedback de ranking"""
        return RankingFeedbackService()
    
    def test_ranking_config_service(self, ranking_config_service):
        """Testa serviço de configuração de ranking"""
        config = ranking_config_service.get_default_config()
        assert isinstance(config, dict)
        assert 'weights' in config
    
    def test_ranking_feedback_service(self, ranking_feedback_service):
        """Testa serviço de feedback de ranking"""
        feedback = {
            'keyword': 'test keyword',
            'rating': 5,
            'comment': 'Great ranking!'
        }
        
        result = ranking_feedback_service.submit_feedback(feedback)
        assert result['success'] == True


class TestExternalApiService:
    """Testes para serviço de APIs externas"""
    
    @pytest.fixture
    def external_api_service(self):
        """Cria instância do serviço de APIs externas"""
        return ExternalApiService()
    
    def test_external_api_service_initialization(self, external_api_service):
        """Testa inicialização do serviço"""
        assert external_api_service is not None
    
    @patch('requests.get')
    def test_fetch_external_data(self, mock_get, external_api_service):
        """Testa busca de dados externos"""
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = external_api_service.fetch_data('https://api.example.com/data')
        assert result['data'] == 'test_data'


class TestPaymentsService:
    """Testes para serviço de pagamentos"""
    
    @pytest.fixture
    def payments_service(self):
        """Cria instância do serviço de pagamentos"""
        return PaymentsService()
    
    def test_payments_service_initialization(self, payments_service):
        """Testa inicialização do serviço"""
        assert payments_service is not None
    
    def test_process_payment(self, payments_service):
        """Testa processamento de pagamento"""
        payment_data = {
            'amount': 100.00,
            'currency': 'BRL',
            'method': 'credit_card'
        }
        
        result = payments_service.process_payment(payment_data)
        assert isinstance(result, dict)
        assert 'status' in result


# Testes de integração para cobrir cenários complexos
class TestIntegrationScenarios:
    """Testes de integração para cenários complexos"""
    
    def test_credential_workflow(self):
        """Testa workflow completo de credenciais"""
        # 1. Criptografar credencial
        with patch.dict(os.environ, {'CREDENTIAL_MASTER_KEY': 'test_master_key_32_chars_long'}):
            encryption_service = CredentialEncryptionService()
            audit_service = CredentialAuditService()
            
            # 2. Criar credencial
            test_credential = "test_api_key_12345"
            encrypted = encryption_service.encrypt_credential(test_credential, "test_provider")
            
            # 3. Log de criação
            audit_service.log_credential_creation("test_user", "test_provider", True)
            
            # 4. Validar credencial
            decrypted = encryption_service.decrypt_credential(encrypted, "test_provider")
            audit_service.log_credential_validation("test_user", "test_provider", True)
            
            # 5. Verificar resultados
            assert decrypted == test_credential
            
            events = audit_service.get_audit_events(user_id="test_user")
            assert len(events) >= 2
    
    def test_export_workflow(self):
        """Testa workflow completo de exportação"""
        with tempfile.TemporaryDirectory() as tmp:
            # 1. Criar dados de teste
            test_data = [
                {'keyword': 'test1', 'volume': 1000},
                {'keyword': 'test2', 'volume': 2000}
            ]
            
            # 2. Criar arquivo CSV
            csv_file = os.path.join(tmp, 'test_export.csv')
            with open(csv_file, 'w') as f:
                f.write('keyword,volume\n')
                for item in test_data:
                    f.write(f"{item['keyword']},{item['volume']}\n")
            
            # 3. Verificar integridade
            integrity_service = ExportIntegrityNotifyService()
            integrity_result = integrity_service.verify_export_integrity(csv_file)
            
            # 4. Criar ZIP
            zip_service = ExportZipService()
            zip_file = os.path.join(tmp, 'export.zip')
            zip_result = zip_service.create_zip([csv_file], zip_file)
            
            # 5. Verificar resultados
            assert integrity_result['is_valid'] == True
            assert os.path.exists(zip_result)
            assert os.path.getsize(zip_result) > 0


# Testes de performance para validar eficiência
class TestPerformanceScenarios:
    """Testes de performance"""
    
    def test_encryption_performance(self):
        """Testa performance de criptografia"""
        with patch.dict(os.environ, {'CREDENTIAL_MASTER_KEY': 'test_master_key_32_chars_long'}):
            encryption_service = CredentialEncryptionService()
            
            import time
            start_time = time.time()
            
            # Criptografar 100 credenciais
            for i in range(100):
                encryption_service.encrypt_credential(f"key_{i}", f"provider_{i}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Deve ser rápido (< 1 segundo para 100 operações)
            assert duration < 1.0
    
    def test_audit_performance(self):
        """Testa performance de auditoria"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('[]')
            audit_file = f.name
        
        audit_service = CredentialAuditService(audit_file_path=audit_file)
        
        import time
        start_time = time.time()
        
        # Criar 1000 eventos
        for i in range(1000):
            audit_service.log_credential_access(f"user_{i}", f"provider_{i}", "read", True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Deve ser rápido (< 2 segundos para 1000 eventos)
        assert duration < 2.0
        
        # Cleanup
        os.unlink(audit_file)


# Testes de segurança para validar proteções
class TestSecurityScenarios:
    """Testes de segurança"""
    
    def test_encryption_security(self):
        """Testa segurança da criptografia"""
        with patch.dict(os.environ, {'CREDENTIAL_MASTER_KEY': 'test_master_key_32_chars_long'}):
            encryption_service = CredentialEncryptionService()
            
            # Testar que a mesma credencial gera criptografias diferentes
            credential = "test_api_key"
            encrypted1 = encryption_service.encrypt_credential(credential, "provider1")
            encrypted2 = encryption_service.encrypt_credential(credential, "provider1")
            
            # Devem ser diferentes devido ao nonce único
            assert encrypted1 != encrypted2
            
            # Mas ambas devem descriptografar para o mesmo valor
            decrypted1 = encryption_service.decrypt_credential(encrypted1, "provider1")
            decrypted2 = encryption_service.decrypt_credential(encrypted2, "provider1")
            
            assert decrypted1 == credential
            assert decrypted2 == credential
    
    def test_input_validation_security(self):
        """Testa validação de entrada para segurança"""
        security_service = SecurityUtilsService()
        
        # Testar entradas maliciosas
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "javascript:alert('xss')"
        ]
        
        for malicious_input in malicious_inputs:
            assert security_service.validate_input(malicious_input) == False
        
        # Testar entradas válidas
        valid_inputs = [
            "normal text",
            "keyword with spaces",
            "test123",
            "valid-input"
        ]
        
        for valid_input in valid_inputs:
            assert security_service.validate_input(valid_input) == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 