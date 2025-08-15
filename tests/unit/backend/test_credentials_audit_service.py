"""
Testes unitários para CredentialsAuditService
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 1.4
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import tempfile
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.app.services.credentials_audit_service import (
    CredentialsAuditService,
    AuditEvent,
    AuditEventType,
    AuditSeverity,
    log_credential_event,
    log_security_event,
    get_audit_service
)

class TestCredentialsAuditService:
    """Testes para CredentialsAuditService baseados no código real."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Fixture para diretório de logs temporário."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def audit_service(self, temp_log_dir):
        """Fixture para serviço de auditoria com logs temporários."""
        return CredentialsAuditService(log_dir=temp_log_dir, max_log_size=1024)
    
    @pytest.fixture
    def sample_audit_event(self):
        """Fixture para evento de auditoria real."""
        return AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="credential_created",
            severity="info",
            user_id="user_123",
            session_id="session_456",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            provider="google",
            credential_id="cred_789",
            details={"action": "create", "platform": "web"},
            metadata={"source": "api", "version": "1.0"}
        )
    
    def test_init_service(self, temp_log_dir):
        """Testa inicialização do serviço."""
        service = CredentialsAuditService(log_dir=temp_log_dir)
        
        assert service.log_dir == Path(temp_log_dir)
        assert service.max_log_size == 10485760  # Valor padrão
        assert service.current_log_file is not None
        assert service.alert_thresholds['failed_validations'] == 5
        assert service.alert_thresholds['rate_limit_violations'] == 3
        assert service.alert_thresholds['security_events'] == 1
        assert service.event_counters['failed_validations'] == 0
        assert service.event_counters['rate_limit_violations'] == 0
        assert service.event_counters['security_events'] == 0
        assert len(service.alert_callbacks) == 0
        
        # Verificar se diretório foi criado
        assert os.path.exists(temp_log_dir)
    
    def test_init_service_custom_max_size(self, temp_log_dir):
        """Testa inicialização com tamanho máximo customizado."""
        service = CredentialsAuditService(log_dir=temp_log_dir, max_log_size=2048)
        assert service.max_log_size == 2048
    
    def test_get_current_log_file(self, audit_service):
        """Testa obtenção do arquivo de log atual."""
        log_file = audit_service._get_current_log_file()
        
        today = datetime.now().strftime("%Y-%m-%data")
        expected_name = f"credentials_audit_{today}.jsonl"
        
        assert log_file.name == expected_name
        assert log_file.parent == audit_service.log_dir
    
    def test_rotate_log_file_when_needed(self, audit_service):
        """Testa rotação do arquivo de log quando necessário."""
        # Criar arquivo de log com tamanho maior que o limite
        log_file = audit_service.current_log_file
        log_file.parent.mkdir(exist_ok=True)
        
        # Escrever dados para exceder o limite
        with open(log_file, 'w') as f:
            f.write('x' * (audit_service.max_log_size + 100))
        
        # Verificar que arquivo existe e tem tamanho grande
        assert log_file.exists()
        assert log_file.stat().st_size > audit_service.max_log_size
        
        # Executar rotação
        audit_service._rotate_log_file()
        
        # Verificar que arquivo original foi renomeado
        assert not log_file.exists()
        
        # Verificar que novo arquivo foi criado
        rotated_files = list(audit_service.log_dir.glob("credentials_audit_*.jsonl"))
        assert len(rotated_files) == 1
        assert rotated_files[0].name != log_file.name
    
    def test_write_audit_event(self, audit_service, sample_audit_event):
        """Testa escrita de evento de auditoria."""
        audit_service._write_audit_event(sample_audit_event)
        
        # Verificar se arquivo foi criado
        assert audit_service.current_log_file.exists()
        
        # Verificar conteúdo do arquivo
        with open(audit_service.current_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 1
            
            event_data = json.loads(lines[0])
            assert event_data['event_type'] == "credential_created"
            assert event_data['user_id'] == "user_123"
            assert event_data['provider'] == "google"
            assert event_data['details']['action'] == "create"
    
    def test_log_event_basic(self, audit_service):
        """Testa registro de evento básico."""
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            severity=AuditSeverity.INFO,
            user_id="user_123",
            provider="google",
            credential_id="cred_456"
        )
        
        # Verificar se evento foi registrado
        events = audit_service.get_audit_events(limit=10)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == "credential_created"
        assert event.severity == "info"
        assert event.user_id == "user_123"
        assert event.provider == "google"
        assert event.credential_id == "cred_456"
    
    def test_log_event_with_all_fields(self, audit_service):
        """Testa registro de evento com todos os campos."""
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_ATTEMPT,
            severity=AuditSeverity.WARNING,
            user_id="user_789",
            session_id="session_123",
            ip_address="10.0.0.1",
            user_agent="Mozilla/5.0 (Linux; Android 10)",
            provider="facebook",
            credential_id="cred_999",
            details={"attempt_count": 3, "reason": "invalid_password"},
            metadata={"browser": "chrome", "os": "android"}
        )
        
        # Verificar evento registrado
        events = audit_service.get_audit_events(limit=10)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == "login_attempt"
        assert event.severity == "warning"
        assert event.user_id == "user_789"
        assert event.session_id == "session_123"
        assert event.ip_address == "10.0.0.1"
        assert event.user_agent == "Mozilla/5.0 (Linux; Android 10)"
        assert event.provider == "facebook"
        assert event.credential_id == "cred_999"
        assert event.details["attempt_count"] == 3
        assert event.details["reason"] == "invalid_password"
        assert event.metadata["browser"] == "chrome"
        assert event.metadata["os"] == "android"
    
    def test_update_event_counters(self, audit_service):
        """Testa atualização de contadores de eventos."""
        # Contador inicial
        assert audit_service.event_counters['failed_validations'] == 0
        assert audit_service.event_counters['rate_limit_violations'] == 0
        assert audit_service.event_counters['security_events'] == 0
        
        # Evento de credencial inválida
        audit_service._update_event_counters(AuditEventType.CREDENTIAL_INVALID, AuditSeverity.WARNING)
        assert audit_service.event_counters['failed_validations'] == 1
        
        # Evento de rate limit excedido
        audit_service._update_event_counters(AuditEventType.RATE_LIMIT_EXCEEDED, AuditSeverity.WARNING)
        assert audit_service.event_counters['rate_limit_violations'] == 1
        
        # Evento de segurança crítico
        audit_service._update_event_counters(AuditEventType.SECURITY_ALERT, AuditSeverity.CRITICAL)
        assert audit_service.event_counters['security_events'] == 1
        
        # Evento de erro
        audit_service._update_event_counters(AuditEventType.SYSTEM_ERROR, AuditSeverity.ERROR)
        assert audit_service.event_counters['security_events'] == 2
    
    def test_check_alert_conditions_failed_validations(self, audit_service):
        """Testa verificação de condições de alerta para falhas de validação."""
        # Mock para callback de alerta
        alert_callback = Mock()
        audit_service.add_alert_callback(alert_callback)
        
        # Registrar falhas até o limite
        for _ in range(5):
            audit_service._update_event_counters(AuditEventType.CREDENTIAL_INVALID, AuditSeverity.WARNING)
        
        # Verificar se alerta foi disparado
        audit_service._check_alert_conditions(AuditEventType.CREDENTIAL_INVALID, AuditSeverity.WARNING)
        
        alert_callback.assert_called_once()
        alert = alert_callback.call_args[0][0]
        assert alert['type'] == 'failed_validations'
        assert 'Múltiplas falhas de validação detectadas: 5' in alert['message']
        assert alert['severity'] == 'warning'
        
        # Verificar se contador foi resetado
        assert audit_service.event_counters['failed_validations'] == 0
    
    def test_check_alert_conditions_rate_limit(self, audit_service):
        """Testa verificação de condições de alerta para rate limit."""
        alert_callback = Mock()
        audit_service.add_alert_callback(alert_callback)
        
        # Registrar violações até o limite
        for _ in range(3):
            audit_service._update_event_counters(AuditEventType.RATE_LIMIT_EXCEEDED, AuditSeverity.WARNING)
        
        # Verificar se alerta foi disparado
        audit_service._check_alert_conditions(AuditEventType.RATE_LIMIT_EXCEEDED, AuditSeverity.WARNING)
        
        alert_callback.assert_called_once()
        alert = alert_callback.call_args[0][0]
        assert alert['type'] == 'rate_limit_violations'
        assert 'Múltiplas violações de rate limit detectadas: 3' in alert['message']
        assert alert['severity'] == 'warning'
        
        # Verificar se contador foi resetado
        assert audit_service.event_counters['rate_limit_violations'] == 0
    
    def test_check_alert_conditions_critical_security(self, audit_service):
        """Testa verificação de condições de alerta para eventos críticos."""
        alert_callback = Mock()
        audit_service.add_alert_callback(alert_callback)
        
        # Evento crítico deve gerar alerta imediato
        audit_service._check_alert_conditions(AuditEventType.SECURITY_ALERT, AuditSeverity.CRITICAL)
        
        alert_callback.assert_called_once()
        alert = alert_callback.call_args[0][0]
        assert alert['type'] == 'security_critical'
        assert 'Evento de segurança crítico detectado: security_alert' in alert['message']
        assert alert['severity'] == 'critical'
    
    def test_trigger_alert_callbacks(self, audit_service):
        """Testa execução de callbacks de alerta."""
        callback1 = Mock()
        callback2 = Mock()
        
        audit_service.add_alert_callback(callback1)
        audit_service.add_alert_callback(callback2)
        
        alert = {
            'type': 'test_alert',
            'message': 'Test alert message',
            'severity': 'warning'
        }
        
        audit_service._trigger_alert_callbacks(alert)
        
        callback1.assert_called_once_with(alert)
        callback2.assert_called_once_with(alert)
    
    def test_trigger_alert_callbacks_with_exception(self, audit_service):
        """Testa execução de callbacks com exceção."""
        def failing_callback(alert):
            raise Exception("Callback failed")
        
        def working_callback(alert):
            pass
        
        audit_service.add_alert_callback(failing_callback)
        audit_service.add_alert_callback(working_callback)
        
        alert = {'type': 'test', 'message': 'test', 'severity': 'info'}
        
        # Não deve propagar exceção
        audit_service._trigger_alert_callbacks(alert)
        
        # Verificar que working_callback foi chamado mesmo com falha do primeiro
        assert len(audit_service.alert_callbacks) == 2
    
    def test_add_alert_callback(self, audit_service):
        """Testa adição de callback de alerta."""
        callback = Mock()
        
        assert len(audit_service.alert_callbacks) == 0
        audit_service.add_alert_callback(callback)
        assert len(audit_service.alert_callbacks) == 1
        assert audit_service.alert_callbacks[0] == callback
    
    def test_get_audit_events_empty(self, audit_service):
        """Testa obtenção de eventos quando não há logs."""
        events = audit_service.get_audit_events()
        assert len(events) == 0
    
    def test_get_audit_events_with_data(self, audit_service):
        """Testa obtenção de eventos com dados."""
        # Registrar alguns eventos
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user_1",
            provider="google"
        )
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="user_2",
            provider="facebook"
        )
        
        # Obter eventos
        events = audit_service.get_audit_events()
        assert len(events) == 2
        
        # Verificar ordenação (mais recente primeiro)
        assert events[0].timestamp >= events[1].timestamp
    
    def test_get_audit_events_with_filters(self, audit_service):
        """Testa obtenção de eventos com filtros."""
        # Registrar eventos diversos
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user_1",
            provider="google",
            severity=AuditSeverity.INFO
        )
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_FAILED,
            user_id="user_2",
            provider="facebook",
            severity=AuditSeverity.WARNING
        )
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user_1",
            provider="google",
            severity=AuditSeverity.INFO
        )
        
        # Filtrar por tipo de evento
        events = audit_service.get_audit_events(event_type=AuditEventType.CREDENTIAL_CREATED)
        assert len(events) == 2
        assert all(e.event_type == "credential_created" for e in events)
        
        # Filtrar por severidade
        events = audit_service.get_audit_events(severity=AuditSeverity.WARNING)
        assert len(events) == 1
        assert events[0].severity == "warning"
        
        # Filtrar por provedor
        events = audit_service.get_audit_events(provider="google")
        assert len(events) == 2
        assert all(e.provider == "google" for e in events)
        
        # Filtrar por usuário
        events = audit_service.get_audit_events(user_id="user_1")
        assert len(events) == 2
        assert all(e.user_id == "user_1" for e in events)
        
        # Filtrar por limite
        events = audit_service.get_audit_events(limit=1)
        assert len(events) == 1
    
    def test_get_audit_events_with_date_filters(self, audit_service):
        """Testa obtenção de eventos com filtros de data."""
        # Registrar evento
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user_1"
        )
        
        # Obter timestamp do evento
        events = audit_service.get_audit_events()
        event_timestamp = datetime.fromisoformat(events[0].timestamp.replace('Z', '+00:00'))
        
        # Filtrar por data de início
        start_date = event_timestamp - timedelta(minutes=1)
        events = audit_service.get_audit_events(start_date=start_date)
        assert len(events) == 1
        
        # Filtrar por data de fim
        end_date = event_timestamp + timedelta(minutes=1)
        events = audit_service.get_audit_events(end_date=end_date)
        assert len(events) == 1
        
        # Filtrar fora do range
        start_date = event_timestamp + timedelta(hours=1)
        events = audit_service.get_audit_events(start_date=start_date)
        assert len(events) == 0
    
    def test_apply_filters(self, audit_service, sample_audit_event):
        """Testa aplicação de filtros em eventos."""
        # Filtro por tipo de evento
        result = audit_service._apply_filters(
            sample_audit_event,
            None, None,
            AuditEventType.CREDENTIAL_CREATED,
            None, None, None
        )
        assert result is True
        
        result = audit_service._apply_filters(
            sample_audit_event,
            None, None,
            AuditEventType.LOGIN_FAILED,
            None, None, None
        )
        assert result is False
        
        # Filtro por severidade
        result = audit_service._apply_filters(
            sample_audit_event,
            None, None, None,
            AuditSeverity.INFO,
            None, None
        )
        assert result is True
        
        result = audit_service._apply_filters(
            sample_audit_event,
            None, None, None,
            AuditSeverity.ERROR,
            None, None
        )
        assert result is False
        
        # Filtro por provedor
        result = audit_service._apply_filters(
            sample_audit_event,
            None, None, None, None,
            "google",
            None
        )
        assert result is True
        
        result = audit_service._apply_filters(
            sample_audit_event,
            None, None, None, None,
            "facebook",
            None
        )
        assert result is False
        
        # Filtro por usuário
        result = audit_service._apply_filters(
            sample_audit_event,
            None, None, None, None, None,
            "user_123"
        )
        assert result is True
        
        result = audit_service._apply_filters(
            sample_audit_event,
            None, None, None, None, None,
            "user_999"
        )
        assert result is False
    
    def test_get_audit_statistics_empty(self, audit_service):
        """Testa estatísticas quando não há eventos."""
        stats = audit_service.get_audit_statistics()
        
        assert stats['total_events'] == 0
        assert stats['events_by_type'] == {}
        assert stats['events_by_severity'] == {}
        assert stats['events_by_provider'] == {}
        assert stats['events_by_user'] == {}
        assert stats['recent_events'] == []
    
    def test_get_audit_statistics_with_data(self, audit_service):
        """Testa estatísticas com dados."""
        # Registrar eventos diversos
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user_1",
            provider="google",
            severity=AuditSeverity.INFO
        )
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_FAILED,
            user_id="user_2",
            provider="facebook",
            severity=AuditSeverity.WARNING
        )
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user_1",
            provider="google",
            severity=AuditSeverity.INFO
        )
        
        stats = audit_service.get_audit_statistics()
        
        assert stats['total_events'] == 3
        assert stats['events_by_type']['credential_created'] == 2
        assert stats['events_by_type']['login_failed'] == 1
        assert stats['events_by_severity']['info'] == 2
        assert stats['events_by_severity']['warning'] == 1
        assert stats['events_by_provider']['google'] == 2
        assert stats['events_by_provider']['facebook'] == 1
        assert stats['events_by_user']['user_1'] == 2
        assert stats['events_by_user']['user_2'] == 1
        assert len(stats['recent_events']) == 3
    
    def test_cleanup_old_logs(self, audit_service):
        """Testa limpeza de logs antigos."""
        # Criar arquivo de log antigo
        old_log_file = audit_service.log_dir / "credentials_audit_2020-01-01.jsonl"
        old_log_file.parent.mkdir(exist_ok=True)
        old_log_file.touch()
        
        # Definir timestamp antigo
        old_timestamp = time.time() - (100 * 24 * 3600)  # 100 dias atrás
        os.utime(old_log_file, (old_timestamp, old_timestamp))
        
        # Criar arquivo de log recente
        recent_log_file = audit_service.log_dir / "credentials_audit_2025-01-27.jsonl"
        recent_log_file.touch()
        
        # Executar limpeza
        removed_count = audit_service.cleanup_old_logs(days_to_keep=90)
        
        assert removed_count == 1
        assert not old_log_file.exists()
        assert recent_log_file.exists()
    
    def test_export_audit_logs_jsonl(self, audit_service, temp_log_dir):
        """Testa exportação de logs em formato JSONL."""
        # Registrar eventos
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user_1",
            provider="google"
        )
        audit_service.log_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id="user_2",
            provider="facebook"
        )
        
        # Exportar logs
        output_file = os.path.join(temp_log_dir, "export.jsonl")
        success = audit_service.export_audit_logs(output_file, format="jsonl")
        
        assert success is True
        assert os.path.exists(output_file)
        
        # Verificar conteúdo
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 2
            
            event1 = json.loads(lines[0])
            event2 = json.loads(lines[1])
            
            assert event1['event_type'] == "credential_created"
            assert event2['event_type'] == "login_success"
    
    def test_export_audit_logs_csv(self, audit_service, temp_log_dir):
        """Testa exportação de logs em formato CSV."""
        # Registrar evento
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user_1",
            provider="google"
        )
        
        # Exportar logs
        output_file = os.path.join(temp_log_dir, "export.csv")
        success = audit_service.export_audit_logs(output_file, format="csv")
        
        assert success is True
        assert os.path.exists(output_file)
        
        # Verificar conteúdo CSV
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 2  # Header + 1 evento
            assert 'timestamp' in lines[0]
            assert 'event_type' in lines[0]
            assert 'credential_created' in lines[1]
    
    def test_export_audit_logs_invalid_format(self, audit_service, temp_log_dir):
        """Testa exportação com formato inválido."""
        output_file = os.path.join(temp_log_dir, "export.txt")
        success = audit_service.export_audit_logs(output_file, format="invalid")
        
        assert success is False

class TestAuditServiceFunctions:
    """Testes para funções auxiliares do serviço de auditoria."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Fixture para diretório de logs temporário."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_log_credential_event(self, temp_log_dir):
        """Testa função de conveniência para log de credenciais."""
        # Mock do serviço global
        with patch('backend.app.services.credentials_audit_service.audit_service') as mock_service:
            log_credential_event(
                event_type=AuditEventType.CREDENTIAL_CREATED,
                provider="google",
                credential_id="cred_123",
                user_id="user_456",
                details={"action": "create"},
                severity=AuditSeverity.INFO
            )
            
            mock_service.log_event.assert_called_once_with(
                event_type=AuditEventType.CREDENTIAL_CREATED,
                severity=AuditSeverity.INFO,
                user_id="user_456",
                provider="google",
                credential_id="cred_123",
                details={"action": "create"}
            )
    
    def test_log_security_event(self, temp_log_dir):
        """Testa função de conveniência para log de segurança."""
        with patch('backend.app.services.credentials_audit_service.audit_service') as mock_service:
            log_security_event(
                event_type=AuditEventType.LOGIN_FAILED,
                user_id="user_789",
                ip_address="192.168.1.100",
                details={"attempt_count": 3},
                severity=AuditSeverity.WARNING
            )
            
            mock_service.log_event.assert_called_once_with(
                event_type=AuditEventType.LOGIN_FAILED,
                severity=AuditSeverity.WARNING,
                user_id="user_789",
                ip_address="192.168.1.100",
                details={"attempt_count": 3}
            )
    
    def test_get_audit_service(self):
        """Testa obtenção da instância global do serviço."""
        service = get_audit_service()
        assert isinstance(service, CredentialsAuditService) 