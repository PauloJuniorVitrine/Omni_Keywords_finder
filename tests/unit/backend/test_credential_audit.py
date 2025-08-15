#!/usr/bin/env python3
"""
Testes Unitários - Credential Audit Service
==========================================

Tracing ID: TEST_CREDENTIAL_AUDIT_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: backend/app/services/credential_audit.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 5.3
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import time
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import os

from backend.app.services.credential_audit import (
    CredentialAuditService, AuditEvent, AuditEventType, AuditSeverity
)


class TestCredentialAuditService:
    @pytest.fixture
    def temp_log_dir(self):
        """Cria diretório temporário para logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def audit_service(self, temp_log_dir):
        """Cria instância do serviço de auditoria."""
        return CredentialAuditService(log_directory=temp_log_dir, max_file_size_mb=1)

    def test_audit_event_type_enum(self):
        """Testa enum AuditEventType."""
        assert AuditEventType.CREDENTIAL_CREATED.value == "credential_created"
        assert AuditEventType.CREDENTIAL_UPDATED.value == "credential_updated"
        assert AuditEventType.CREDENTIAL_DELETED.value == "credential_deleted"
        assert AuditEventType.CREDENTIAL_VALIDATED.value == "credential_validated"
        assert AuditEventType.CREDENTIAL_ENCRYPTED.value == "credential_encrypted"
        assert AuditEventType.CREDENTIAL_DECRYPTED.value == "credential_decrypted"
        assert AuditEventType.RATE_LIMIT_EXCEEDED.value == "rate_limit_exceeded"
        assert AuditEventType.ANOMALY_DETECTED.value == "anomaly_detected"
        assert AuditEventType.ACCESS_GRANTED.value == "access_granted"
        assert AuditEventType.ACCESS_DENIED.value == "access_denied"
        assert AuditEventType.PROVIDER_BLOCKED.value == "provider_blocked"
        assert AuditEventType.PROVIDER_UNBLOCKED.value == "provider_unblocked"

    def test_audit_severity_enum(self):
        """Testa enum AuditSeverity."""
        assert AuditSeverity.LOW.value == "low"
        assert AuditSeverity.MEDIUM.value == "medium"
        assert AuditSeverity.HIGH.value == "high"
        assert AuditSeverity.CRITICAL.value == "critical"

    def test_audit_event_dataclass(self):
        """Testa criação de objeto AuditEvent."""
        event = AuditEvent(
            event_id="test-123",
            event_type=AuditEventType.CREDENTIAL_CREATED,
            timestamp=datetime.utcnow(),
            user_id="user123",
            provider="google",
            credential_type="api_key",
            severity=AuditSeverity.HIGH,
            details={"action": "test"},
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        assert event.event_id == "test-123"
        assert event.event_type == AuditEventType.CREDENTIAL_CREATED
        assert event.user_id == "user123"
        assert event.provider == "google"
        assert event.credential_type == "api_key"
        assert event.severity == AuditSeverity.HIGH
        assert event.details == {"action": "test"}
        assert event.ip_address == "192.168.1.1"
        assert event.user_agent == "test-agent"
        assert event.session_id == "session123"
        assert event.correlation_id == "corr123"
        assert event.source == "credential_audit_service"
        assert event.version == "1.0"

    def test_audit_service_initialization(self, temp_log_dir):
        """Testa inicialização do CredentialAuditService."""
        service = CredentialAuditService(log_directory=temp_log_dir, max_file_size_mb=5)
        
        assert service.log_directory == Path(temp_log_dir)
        assert service.max_file_size_bytes == 5 * 1024 * 1024
        assert service.current_log_file is not None
        assert service.current_file_size == 0
        assert service.total_events == 0
        assert service.events_by_type == {}
        assert service.events_by_severity == {}
        
        # Verificar se diretório foi criado
        assert Path(temp_log_dir).exists()

    def test_audit_service_default_initialization(self):
        """Testa inicialização com valores padrão."""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            service = CredentialAuditService()
            
            assert service.log_directory == Path("logs/audit")
            assert service.max_file_size_bytes == 10 * 1024 * 1024
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_initialize_log_file(self, audit_service):
        """Testa inicialização do arquivo de log."""
        # Verificar se arquivo foi criado
        assert audit_service.current_log_file.exists()
        
        # Verificar formato do nome do arquivo
        filename = audit_service.current_log_file.name
        assert filename.startswith("credential_audit_")
        assert filename.endswith(".jsonl")

    def test_should_rotate_log_false(self, audit_service):
        """Testa verificação de rotação quando não necessária."""
        assert audit_service._should_rotate_log() is False

    def test_should_rotate_log_true(self, audit_service):
        """Testa verificação de rotação quando necessária."""
        # Simular arquivo grande
        audit_service.current_file_size = audit_service.max_file_size_bytes + 1
        
        assert audit_service._should_rotate_log() is True

    def test_rotate_log(self, audit_service):
        """Testa rotação do arquivo de log."""
        original_file = audit_service.current_log_file
        
        # Simular arquivo grande para forçar rotação
        audit_service.current_file_size = audit_service.max_file_size_bytes + 1
        
        audit_service._rotate_log()
        
        # Verificar se novo arquivo foi criado
        assert audit_service.current_log_file != original_file
        assert audit_service.current_file_size == 0

    def test_compress_log_file(self, audit_service):
        """Testa compressão de arquivo de log."""
        # Criar arquivo de teste
        test_file = audit_service.log_directory / "test.jsonl"
        test_file.write_text("test content")
        
        audit_service._compress_log_file(test_file)
        
        # Verificar se arquivo foi renomeado com extensão .gz
        compressed_file = test_file.with_suffix('.jsonl.gz')
        assert compressed_file.exists()

    def test_write_event_success(self, audit_service):
        """Testa escrita bem-sucedida de evento."""
        event = AuditEvent(
            event_id="test-123",
            event_type=AuditEventType.CREDENTIAL_CREATED,
            timestamp=datetime.utcnow(),
            user_id="user123",
            provider="google",
            severity=AuditSeverity.HIGH
        )
        
        audit_service._write_event(event)
        
        # Verificar se evento foi escrito no arquivo
        with open(audit_service.current_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "test-123" in content
            assert "credential_created" in content
            assert "user123" in content

    def test_write_event_with_rotation(self, audit_service):
        """Testa escrita de evento com rotação automática."""
        # Simular arquivo grande
        audit_service.current_file_size = audit_service.max_file_size_bytes - 100
        
        event = AuditEvent(
            event_id="test-123",
            event_type=AuditEventType.CREDENTIAL_CREATED,
            timestamp=datetime.utcnow(),
            user_id="user123",
            provider="google",
            severity=AuditSeverity.HIGH
        )
        
        audit_service._write_event(event)
        
        # Verificar se rotação ocorreu
        assert audit_service.current_file_size > 0

    def test_update_metrics(self, audit_service):
        """Testa atualização de métricas."""
        event = AuditEvent(
            event_id="test-123",
            event_type=AuditEventType.CREDENTIAL_CREATED,
            timestamp=datetime.utcnow(),
            user_id="user123",
            provider="google",
            severity=AuditSeverity.HIGH
        )
        
        audit_service._update_metrics(event)
        
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["credential_created"] == 1
        assert audit_service.events_by_severity["high"] == 1

    def test_log_event(self, audit_service):
        """Testa logging de evento genérico."""
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user123",
            provider="google",
            credential_type="api_key",
            severity=AuditSeverity.HIGH,
            details={"action": "test"},
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        # Verificar se evento foi registrado
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["credential_created"] == 1

    def test_log_credential_created(self, audit_service):
        """Testa logging de criação de credencial."""
        audit_service.log_credential_created(
            user_id="user123",
            provider="google",
            credential_type="api_key",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["credential_created"] == 1
        assert audit_service.events_by_severity["high"] == 1

    def test_log_credential_updated(self, audit_service):
        """Testa logging de atualização de credencial."""
        audit_service.log_credential_updated(
            user_id="user123",
            provider="google",
            credential_type="api_key",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["credential_updated"] == 1
        assert audit_service.events_by_severity["high"] == 1

    def test_log_credential_validated_success(self, audit_service):
        """Testa logging de validação bem-sucedida."""
        audit_service.log_credential_validated(
            user_id="user123",
            provider="google",
            credential_type="api_key",
            is_valid=True,
            validation_time=0.5,
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["credential_validated"] == 1
        assert audit_service.events_by_severity["low"] == 1  # LOW para sucesso

    def test_log_credential_validated_failure(self, audit_service):
        """Testa logging de validação falhada."""
        audit_service.log_credential_validated(
            user_id="user123",
            provider="google",
            credential_type="api_key",
            is_valid=False,
            validation_time=0.5,
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["credential_validated"] == 1
        assert audit_service.events_by_severity["medium"] == 1  # MEDIUM para falha

    def test_log_rate_limit_exceeded(self, audit_service):
        """Testa logging de excedência de rate limit."""
        audit_service.log_rate_limit_exceeded(
            user_id="user123",
            provider="google",
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["rate_limit_exceeded"] == 1
        assert audit_service.events_by_severity["medium"] == 1

    def test_log_anomaly_detected(self, audit_service):
        """Testa logging de detecção de anomalia."""
        details = {"anomaly_type": "brute_force", "attempts": 100}
        
        audit_service.log_anomaly_detected(
            user_id="user123",
            provider="google",
            anomaly_type="brute_force",
            details=details,
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["anomaly_detected"] == 1
        assert audit_service.events_by_severity["high"] == 1

    def test_log_provider_blocked(self, audit_service):
        """Testa logging de bloqueio de provider."""
        audit_service.log_provider_blocked(
            user_id="user123",
            provider="google",
            reason="rate_limit_exceeded",
            block_duration=300,
            ip_address="192.168.1.1",
            user_agent="test-agent",
            session_id="session123",
            correlation_id="corr123"
        )
        
        assert audit_service.total_events == 1
        assert audit_service.events_by_type["provider_blocked"] == 1
        assert audit_service.events_by_severity["high"] == 1

    def test_search_events_no_filters(self, audit_service):
        """Testa busca de eventos sem filtros."""
        # Criar alguns eventos
        audit_service.log_credential_created("user1", "google", "api_key")
        audit_service.log_credential_updated("user2", "facebook", "oauth")
        
        events = audit_service.search_events()
        
        assert len(events) == 2

    def test_search_events_with_time_filter(self, audit_service):
        """Testa busca de eventos com filtro de tempo."""
        # Criar eventos
        audit_service.log_credential_created("user1", "google", "api_key")
        
        # Buscar eventos de hoje
        start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        events = audit_service.search_events(start_time=start_time, end_time=end_time)
        
        assert len(events) == 1

    def test_search_events_with_event_type_filter(self, audit_service):
        """Testa busca de eventos com filtro de tipo."""
        # Criar eventos
        audit_service.log_credential_created("user1", "google", "api_key")
        audit_service.log_credential_updated("user2", "facebook", "oauth")
        
        events = audit_service.search_events(
            event_types=[AuditEventType.CREDENTIAL_CREATED]
        )
        
        assert len(events) == 1
        assert events[0]["event_type"] == "credential_created"

    def test_search_events_with_user_filter(self, audit_service):
        """Testa busca de eventos com filtro de usuário."""
        # Criar eventos
        audit_service.log_credential_created("user1", "google", "api_key")
        audit_service.log_credential_created("user2", "facebook", "oauth")
        
        events = audit_service.search_events(user_id="user1")
        
        assert len(events) == 1
        assert events[0]["user_id"] == "user1"

    def test_search_events_with_provider_filter(self, audit_service):
        """Testa busca de eventos com filtro de provider."""
        # Criar eventos
        audit_service.log_credential_created("user1", "google", "api_key")
        audit_service.log_credential_created("user2", "facebook", "oauth")
        
        events = audit_service.search_events(provider="google")
        
        assert len(events) == 1
        assert events[0]["provider"] == "google"

    def test_search_events_with_severity_filter(self, audit_service):
        """Testa busca de eventos com filtro de severidade."""
        # Criar eventos
        audit_service.log_credential_created("user1", "google", "api_key")  # HIGH
        audit_service.log_credential_validated("user2", "facebook", "oauth", True, 0.5)  # LOW
        
        events = audit_service.search_events(severity=AuditSeverity.HIGH)
        
        assert len(events) == 1
        assert events[0]["severity"] == "high"

    def test_search_events_with_limit(self, audit_service):
        """Testa busca de eventos com limite."""
        # Criar muitos eventos
        for i in range(10):
            audit_service.log_credential_created(f"user{i}", "google", "api_key")
        
        events = audit_service.search_events(limit=5)
        
        assert len(events) == 5

    def test_matches_filters_all_true(self, audit_service):
        """Testa filtros quando todos os critérios são atendidos."""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "credential_created",
            "user_id": "user123",
            "provider": "google",
            "severity": "high"
        }
        
        result = audit_service._matches_filters(
            event_data=event_data,
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=1),
            event_types=[AuditEventType.CREDENTIAL_CREATED],
            user_id="user123",
            provider="google",
            severity=AuditSeverity.HIGH
        )
        
        assert result is True

    def test_matches_filters_time_false(self, audit_service):
        """Testa filtros quando tempo não corresponde."""
        event_data = {
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "event_type": "credential_created",
            "user_id": "user123",
            "provider": "google",
            "severity": "high"
        }
        
        result = audit_service._matches_filters(
            event_data=event_data,
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow() + timedelta(hours=1),
            event_types=None,
            user_id=None,
            provider=None,
            severity=None
        )
        
        assert result is False

    def test_matches_filters_event_type_false(self, audit_service):
        """Testa filtros quando tipo de evento não corresponde."""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "credential_updated",
            "user_id": "user123",
            "provider": "google",
            "severity": "high"
        }
        
        result = audit_service._matches_filters(
            event_data=event_data,
            start_time=None,
            end_time=None,
            event_types=[AuditEventType.CREDENTIAL_CREATED],
            user_id=None,
            provider=None,
            severity=None
        )
        
        assert result is False

    def test_get_metrics(self, audit_service):
        """Testa obtenção de métricas."""
        # Criar alguns eventos
        audit_service.log_credential_created("user1", "google", "api_key")
        audit_service.log_credential_updated("user2", "facebook", "oauth")
        
        metrics = audit_service.get_metrics()
        
        assert metrics["total_events"] == 2
        assert metrics["events_by_type"]["credential_created"] == 1
        assert metrics["events_by_type"]["credential_updated"] == 1
        assert metrics["events_by_severity"]["high"] == 2
        assert "current_log_file" in metrics
        assert "current_file_size_bytes" in metrics
        assert "max_file_size_bytes" in metrics

    def test_cleanup_old_logs(self, audit_service):
        """Testa limpeza de logs antigos."""
        # Criar arquivo antigo
        old_file = audit_service.log_directory / "old_file.jsonl"
        old_file.write_text("old content")
        
        # Simular arquivo antigo (modificar timestamp)
        old_timestamp = datetime.utcnow() - timedelta(days=100)
        os.utime(old_file, (old_timestamp.timestamp(), old_timestamp.timestamp()))
        
        # Criar arquivo recente
        new_file = audit_service.log_directory / "new_file.jsonl"
        new_file.write_text("new content")
        
        audit_service.cleanup_old_logs(retention_days=90)
        
        # Verificar se arquivo antigo foi removido
        assert not old_file.exists()
        # Verificar se arquivo recente foi mantido
        assert new_file.exists()

    def test_is_healthy_success(self, audit_service):
        """Testa health check bem-sucedido."""
        assert audit_service.is_healthy() is True

    def test_is_healthy_failure(self, audit_service):
        """Testa health check com falha."""
        # Simular falha na escrita
        with patch.object(audit_service, '_write_event', side_effect=Exception("Test error")):
            assert audit_service.is_healthy() is False

    def test_edge_cases(self, audit_service):
        """Testa casos edge."""
        # Teste com dados opcionais nulos
        audit_service.log_event(
            event_type=AuditEventType.CREDENTIAL_CREATED,
            user_id="user123",
            provider="google",
            credential_type=None,
            severity=AuditSeverity.MEDIUM,
            details=None,
            ip_address=None,
            user_agent=None,
            session_id=None,
            correlation_id=None
        )
        
        assert audit_service.total_events == 1

    def test_multiple_events_same_type(self, audit_service):
        """Testa múltiplos eventos do mesmo tipo."""
        for i in range(5):
            audit_service.log_credential_created(f"user{i}", "google", "api_key")
        
        assert audit_service.total_events == 5
        assert audit_service.events_by_type["credential_created"] == 5

    def test_different_severities(self, audit_service):
        """Testa eventos com diferentes severidades."""
        audit_service.log_credential_created("user1", "google", "api_key")  # HIGH
        audit_service.log_credential_validated("user2", "facebook", "oauth", True, 0.5)  # LOW
        audit_service.log_rate_limit_exceeded("user3", "twitter")  # MEDIUM
        
        assert audit_service.events_by_severity["high"] == 1
        assert audit_service.events_by_severity["low"] == 1
        assert audit_service.events_by_severity["medium"] == 1

    def test_log_file_rotation_performance(self, audit_service):
        """Testa performance da rotação de logs."""
        # Simular arquivo grande
        audit_service.current_file_size = audit_service.max_file_size_bytes - 100
        
        # Criar evento que deve causar rotação
        event = AuditEvent(
            event_id="test-123",
            event_type=AuditEventType.CREDENTIAL_CREATED,
            timestamp=datetime.utcnow(),
            user_id="user123",
            provider="google",
            severity=AuditSeverity.HIGH
        )
        
        # Medir tempo de escrita com rotação
        start_time = time.time()
        audit_service._write_event(event)
        end_time = time.time()
        
        # Verificar se rotação ocorreu rapidamente (< 1 segundo)
        assert end_time - start_time < 1.0


if __name__ == "__main__":
    pytest.main([__file__]) 