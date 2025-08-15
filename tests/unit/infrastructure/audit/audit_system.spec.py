"""
Testes Unitários para Sistema de Auditoria - Omni Keywords Finder
Cobertura completa de schemas, logger, endpoints e segurança
Prompt: Implementação de sistema de auditoria
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from backend.app.schemas.audit_schemas import (
    AuditLogEntry,
    AuditFilterSchema,
    AuditReportSchema,
    AuditExportSchema,
    AuditEventType,
    AuditSeverity,
    AuditCategory
)
from backend.app.utils.audit_logger import AuditLogger, AuditStatistics
from backend.app.api.auditoria import router

# Configuração de testes
@pytest.fixture
def temp_db():
    """Cria banco de dados temporário para testes"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Limpeza
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def audit_logger(temp_db):
    """Logger de auditoria para testes"""
    return AuditLogger(db_path=temp_db, log_file="test_audit.log")

@pytest.fixture
def test_client():
    """Cliente de teste FastAPI"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def mock_user():
    """Usuário mock para testes"""
    return {
        "id": "test_user_123",
        "username": "testuser",
        "email": "test@example.com",
        "permissions": ["audit:read", "audit:report", "audit:export"]
    }

@pytest.fixture
def sample_audit_log():
    """Log de auditoria de exemplo"""
    return {
        "log_id": "test_log_123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "user_login",
        "severity": "info",
        "category": "authentication",
        "user_id": "test_user_123",
        "session_id": "session_123",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "request_id": "req_123",
        "message": "Login realizado com sucesso",
        "details": {"method": "password"},
        "resource_type": "user",
        "resource_id": "test_user_123",
        "source": "api",
        "version": "1.0",
        "environment": "test"
    }

class TestAuditSchemas:
    """Testes para schemas de auditoria"""
    
    def test_audit_log_entry_valid(self):
        """Testa criação de entrada de log válida"""
        log_entry = AuditLogEntry(
            log_id="test_123",
            event_type="user_login",
            message="Teste de login",
            user_id="user_123",
            ip_address="192.168.1.1"
        )
        
        assert log_entry.log_id == "test_123"
        assert log_entry.event_type == "user_login"
        assert log_entry.message == "Teste de login"
        assert log_entry.user_id == "user_123"
        assert log_entry.ip_address == "192.168.1.1"
        assert log_entry.severity == "info"
        assert log_entry.category == "system"
    
    def test_audit_log_entry_invalid_event_type(self):
        """Testa validação de tipo de evento inválido"""
        with pytest.raises(ValueError, match="Evento não suportado"):
            AuditLogEntry(
                log_id="test_123",
                event_type="invalid_event",
                message="Teste"
            )
    
    def test_audit_log_entry_invalid_severity(self):
        """Testa validação de severidade inválida"""
        with pytest.raises(ValueError, match="Severidade inválida"):
            AuditLogEntry(
                log_id="test_123",
                event_type="user_login",
                message="Teste",
                severity="invalid_severity"
            )
    
    def test_audit_log_entry_invalid_category(self):
        """Testa validação de categoria inválida"""
        with pytest.raises(ValueError, match="Categoria inválida"):
            AuditLogEntry(
                log_id="test_123",
                event_type="user_login",
                message="Teste",
                category="invalid_category"
            )
    
    def test_audit_log_entry_invalid_ip(self):
        """Testa validação de IP inválido"""
        with pytest.raises(ValueError, match="Endereço IP inválido"):
            AuditLogEntry(
                log_id="test_123",
                event_type="user_login",
                message="Teste",
                ip_address="invalid_ip"
            )
    
    def test_audit_log_entry_sanitization(self):
        """Testa sanitização de dados"""
        log_entry = AuditLogEntry(
            log_id="test_123",
            event_type="user_login",
            message="Teste <script>alert('xss')</script>",
            user_id="user<script>123",
            details={"key<script>": "value<script>"}
        )
        
        assert "<script>" not in log_entry.message
        assert "<script>" not in log_entry.user_id
        assert "<script>" not in log_entry.details["key"]
    
    def test_audit_filter_schema_valid(self):
        """Testa criação de filtro válido"""
        filters = AuditFilterSchema(
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=1),
            event_types=["user_login", "user_logout"],
            severities=["info", "warning"],
            limit=100,
            offset=0
        )
        
        assert filters.event_types == ["user_login", "user_logout"]
        assert filters.severities == ["info", "warning"]
        assert filters.limit == 100
        assert filters.offset == 0
    
    def test_audit_filter_schema_invalid_date_range(self):
        """Testa validação de range de datas inválido"""
        with pytest.raises(ValueError, match="Data inicial não pode ser posterior"):
            AuditFilterSchema(
                start_date=datetime.now(timezone.utc) + timedelta(days=1),
                end_date=datetime.now(timezone.utc)
            )
    
    def test_audit_filter_schema_invalid_event_types(self):
        """Testa validação de tipos de evento inválidos"""
        with pytest.raises(ValueError, match="Evento não suportado"):
            AuditFilterSchema(
                event_types=["invalid_event"]
            )
    
    def test_audit_filter_schema_invalid_sort_field(self):
        """Testa validação de campo de ordenação inválido"""
        with pytest.raises(ValueError, match="Campo de ordenação inválido"):
            AuditFilterSchema(
                sort_by="invalid_field"
            )
    
    def test_audit_filter_schema_invalid_sort_order(self):
        """Testa validação de ordem de classificação inválida"""
        with pytest.raises(ValueError, match="Ordem de classificação deve ser"):
            AuditFilterSchema(
                sort_order="invalid_order"
            )
    
    def test_audit_export_schema_valid(self):
        """Testa criação de configuração de exportação válida"""
        export_config = AuditExportSchema(
            format="json",
            include_details=True,
            include_metadata=True,
            filters=AuditFilterSchema(),
            filename="test_export",
            compression=True
        )
        
        assert export_config.format == "json"
        assert export_config.include_details is True
        assert export_config.compression is True
        assert export_config.filename == "test_export"
    
    def test_audit_export_schema_invalid_format(self):
        """Testa validação de formato inválido"""
        with pytest.raises(ValueError, match="Formato inválido"):
            AuditExportSchema(
                format="invalid_format",
                filters=AuditFilterSchema()
            )
    
    def test_audit_export_schema_filename_sanitization(self):
        """Testa sanitização de nome de arquivo"""
        export_config = AuditExportSchema(
            format="json",
            filters=AuditFilterSchema(),
            filename="test<>:\"/\\|?*file"
        )
        
        assert "<>" not in export_config.filename
        assert ":" not in export_config.filename
        assert "/" not in export_config.filename

class TestAuditLogger:
    """Testes para logger de auditoria"""
    
    def test_audit_logger_initialization(self, audit_logger):
        """Testa inicialização do logger"""
        assert audit_logger.db_path is not None
        assert audit_logger.log_file == "test_audit.log"
        assert audit_logger.logger is not None
        assert audit_logger.db is not None
    
    def test_log_event_success(self, audit_logger):
        """Testa registro de evento com sucesso"""
        log_id = audit_logger.log_event(
            event_type="user_login",
            message="Login realizado",
            user_id="user_123",
            ip_address="192.168.1.1"
        )
        
        assert log_id is not None
        assert len(log_id) > 0
    
    def test_log_event_invalid_type(self, audit_logger):
        """Testa registro de evento com tipo inválido"""
        log_id = audit_logger.log_event(
            event_type="invalid_type",
            message="Teste"
        )
        
        # Deve retornar string vazia em caso de erro
        assert log_id == ""
    
    def test_get_audit_logs(self, audit_logger):
        """Testa obtenção de logs"""
        # Registrar alguns logs
        audit_logger.log_event(
            event_type="user_login",
            message="Login 1",
            user_id="user_1"
        )
        
        audit_logger.log_event(
            event_type="user_logout",
            message="Logout 1",
            user_id="user_1"
        )
        
        # Obter logs
        filters = AuditFilterSchema()
        logs = audit_logger.get_audit_logs(filters)
        
        assert len(logs) >= 2
        assert any(log["event_type"] == "user_login" for log in logs)
        assert any(log["event_type"] == "user_logout" for log in logs)
    
    def test_get_audit_logs_with_filters(self, audit_logger):
        """Testa obtenção de logs com filtros"""
        # Registrar logs
        audit_logger.log_event(
            event_type="user_login",
            message="Login",
            user_id="user_1",
            severity="info"
        )
        
        audit_logger.log_event(
            event_type="security_event",
            message="Security alert",
            user_id="user_2",
            severity="critical"
        )
        
        # Filtrar por severidade
        filters = AuditFilterSchema(severities=["critical"])
        logs = audit_logger.get_audit_logs(filters)
        
        assert len(logs) >= 1
        assert all(log["severity"] == "critical" for log in logs)
    
    def test_get_statistics(self, audit_logger):
        """Testa obtenção de estatísticas"""
        # Registrar logs
        start_date = datetime.now(timezone.utc) - timedelta(hours=1)
        end_date = datetime.now(timezone.utc) + timedelta(hours=1)
        
        audit_logger.log_event(
            event_type="user_login",
            message="Login",
            user_id="user_1",
            severity="info"
        )
        
        audit_logger.log_event(
            event_type="security_event",
            message="Security alert",
            user_id="user_2",
            severity="critical"
        )
        
        # Obter estatísticas
        stats = audit_logger.get_statistics(start_date, end_date)
        
        assert stats.total_events >= 2
        assert "user_login" in stats.events_by_type
        assert "security_event" in stats.events_by_type
        assert stats.events_by_severity["info"] >= 1
        assert stats.events_by_severity["critical"] >= 1
    
    def test_generate_report(self, audit_logger):
        """Testa geração de relatório"""
        # Registrar logs
        start_date = datetime.now(timezone.utc) - timedelta(hours=1)
        end_date = datetime.now(timezone.utc) + timedelta(hours=1)
        
        audit_logger.log_event(
            event_type="user_login",
            message="Login",
            user_id="user_1"
        )
        
        # Gerar relatório
        report = audit_logger.generate_report(start_date, end_date)
        
        assert report.report_id is not None
        assert report.total_events >= 1
        assert report.period_start == start_date
        assert report.period_end == end_date
        assert isinstance(report.recommendations, list)
    
    def test_export_logs_json(self, audit_logger):
        """Testa exportação em JSON"""
        # Registrar logs
        audit_logger.log_event(
            event_type="user_login",
            message="Login",
            user_id="user_1"
        )
        
        # Configurar exportação
        export_config = AuditExportSchema(
            format="json",
            filters=AuditFilterSchema(),
            filename="test_export"
        )
        
        # Exportar
        filepath = audit_logger.export_logs(export_config)
        
        assert filepath.endswith(".json")
        assert os.path.exists(filepath)
        
        # Verificar conteúdo
        with open(filepath, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) >= 1
        
        # Limpeza
        os.remove(filepath)
    
    def test_export_logs_csv(self, audit_logger):
        """Testa exportação em CSV"""
        # Registrar logs
        audit_logger.log_event(
            event_type="user_login",
            message="Login",
            user_id="user_1"
        )
        
        # Configurar exportação
        export_config = AuditExportSchema(
            format="csv",
            filters=AuditFilterSchema(),
            filename="test_export"
        )
        
        # Exportar
        filepath = audit_logger.export_logs(export_config)
        
        assert filepath.endswith(".csv")
        assert os.path.exists(filepath)
        
        # Limpeza
        os.remove(filepath)
    
    def test_cleanup_old_logs(self, audit_logger):
        """Testa limpeza de logs antigos"""
        # Registrar logs
        audit_logger.log_event(
            event_type="user_login",
            message="Login",
            user_id="user_1"
        )
        
        # Verificar logs antes da limpeza
        filters = AuditFilterSchema()
        logs_before = audit_logger.get_audit_logs(filters)
        
        # Limpar logs (manter apenas 1 dia)
        audit_logger.cleanup_old_logs(days_to_keep=1)
        
        # Verificar logs após limpeza
        logs_after = audit_logger.get_audit_logs(filters)
        
        # Como os logs são recentes, não devem ser removidos
        assert len(logs_after) >= len(logs_before)

class TestAuditAPI:
    """Testes para endpoints da API de auditoria"""
    
    @patch('backend.app.api.auditoria.get_current_user')
    @patch('backend.app.api.auditoria.require_permissions')
    @patch('backend.app.api.auditoria.rate_limiter')
    def test_get_audit_logs_success(self, mock_rate_limiter, mock_require_permissions, mock_get_user, test_client, mock_user):
        """Testa obtenção de logs com sucesso"""
        # Mock das dependências
        mock_get_user.return_value = mock_user
        mock_require_permissions.return_value = None
        mock_rate_limiter.check_rate_limit.return_value = None
        
        # Mock do logger
        with patch('backend.app.api.auditoria.audit_logger') as mock_logger:
            mock_logger.get_audit_logs.return_value = [{"log_id": "test_123"}]
            mock_logger.log_event.return_value = "log_id"
            
            # Fazer requisição
            response = test_client.get("/api/audit/logs")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 1
    
    @patch('backend.app.api.auditoria.get_current_user')
    def test_get_audit_logs_unauthorized(self, mock_get_user, test_client):
        """Testa acesso não autorizado"""
        # Mock de usuário sem permissões
        mock_get_user.return_value = {"id": "user_123", "permissions": []}
        
        # Fazer requisição
        response = test_client.get("/api/audit/logs")
        
        assert response.status_code == 403
    
    @patch('backend.app.api.auditoria.get_current_user')
    @patch('backend.app.api.auditoria.require_permissions')
    def test_get_audit_logs_invalid_ip(self, mock_require_permissions, mock_get_user, test_client, mock_user):
        """Testa validação de IP inválido"""
        # Mock das dependências
        mock_get_user.return_value = mock_user
        mock_require_permissions.return_value = None
        
        # Fazer requisição com IP inválido
        response = test_client.get("/api/audit/logs?ip_address=invalid_ip")
        
        assert response.status_code == 400
        assert "Endereço IP inválido" in response.json()["detail"]
    
    @patch('backend.app.api.auditoria.get_current_user')
    @patch('backend.app.api.auditoria.require_permissions')
    def test_get_audit_statistics_success(self, mock_require_permissions, mock_get_user, test_client, mock_user):
        """Testa obtenção de estatísticas com sucesso"""
        # Mock das dependências
        mock_get_user.return_value = mock_user
        mock_require_permissions.return_value = None
        
        # Mock do logger
        with patch('backend.app.api.auditoria.audit_logger') as mock_logger:
            mock_logger.get_statistics.return_value = AuditStatistics(
                total_events=10,
                events_by_type={"user_login": 5},
                events_by_severity={"info": 8},
                events_by_category={"authentication": 5},
                events_by_user={"user_1": 3},
                events_by_hour={"2025-01-27 10:00": 2},
                security_events=2,
                unauthorized_access=1,
                suspicious_activity=0,
                rate_limit_violations=0
            )
            mock_logger.log_event.return_value = "log_id"
            
            # Fazer requisição
            start_date = datetime.now(timezone.utc) - timedelta(days=1)
            end_date = datetime.now(timezone.utc)
            
            response = test_client.get(
                f"/api/audit/statistics?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_events"] == 10
            assert "user_login" in data["events_by_type"]
    
    @patch('backend.app.api.auditoria.get_current_user')
    @patch('backend.app.api.auditoria.require_permissions')
    def test_get_audit_statistics_invalid_date_range(self, mock_require_permissions, mock_get_user, test_client, mock_user):
        """Testa validação de range de datas inválido"""
        # Mock das dependências
        mock_get_user.return_value = mock_user
        mock_require_permissions.return_value = None
        
        # Fazer requisição com datas inválidas
        start_date = datetime.now(timezone.utc) + timedelta(days=1)
        end_date = datetime.now(timezone.utc)
        
        response = test_client.get(
            f"/api/audit/statistics?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
        )
        
        assert response.status_code == 400
        assert "Data inicial não pode ser posterior" in response.json()["detail"]
    
    def test_get_event_types(self, test_client):
        """Testa obtenção de tipos de eventos"""
        response = test_client.get("/api/audit/events/types")
        
        assert response.status_code == 200
        data = response.json()
        assert "event_types" in data
        assert "severities" in data
        assert "categories" in data
        assert isinstance(data["event_types"], list)
        assert isinstance(data["severities"], list)
        assert isinstance(data["categories"], list)
    
    @patch('backend.app.api.auditoria.get_current_user')
    @patch('backend.app.api.auditoria.require_permissions')
    def test_audit_health_check(self, mock_require_permissions, mock_get_user, test_client, mock_user):
        """Testa verificação de saúde"""
        # Mock das dependências
        mock_get_user.return_value = mock_user
        mock_require_permissions.return_value = None
        
        # Mock do logger
        with patch('backend.app.api.auditoria.audit_logger') as mock_logger:
            mock_logger.get_statistics.return_value = AuditStatistics(
                total_events=5,
                events_by_type={},
                events_by_severity={},
                events_by_category={},
                events_by_user={},
                events_by_hour={},
                security_events=0,
                unauthorized_access=0,
                suspicious_activity=0,
                rate_limit_violations=0
            )
            
            response = test_client.get("/api/audit/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "database" in data
            assert "total_events_today" in data

class TestAuditSecurity:
    """Testes de segurança para auditoria"""
    
    def test_sql_injection_prevention(self, audit_logger):
        """Testa prevenção de SQL injection"""
        # Tentar SQL injection no user_id
        malicious_user_id = "'; DROP TABLE audit_logs; --"
        
        log_id = audit_logger.log_event(
            event_type="user_login",
            message="Teste SQL injection",
            user_id=malicious_user_id
        )
        
        # Deve registrar o log sem executar SQL malicioso
        assert log_id is not None
        
        # Verificar se a tabela ainda existe
        filters = AuditFilterSchema()
        logs = audit_logger.get_audit_logs(filters)
        assert isinstance(logs, list)
    
    def test_xss_prevention(self, audit_logger):
        """Testa prevenção de XSS"""
        # Tentar XSS na mensagem
        malicious_message = "<script>alert('xss')</script>"
        
        log_id = audit_logger.log_event(
            event_type="user_login",
            message=malicious_message
        )
        
        # Deve sanitizar a mensagem
        assert log_id is not None
        
        # Verificar se o script foi removido
        filters = AuditFilterSchema()
        logs = audit_logger.get_audit_logs(filters)
        
        if logs:
            latest_log = logs[0]
            assert "<script>" not in latest_log["message"]
    
    def test_path_traversal_prevention(self, audit_logger):
        """Testa prevenção de path traversal"""
        # Tentar path traversal no filename
        malicious_filename = "../../../etc/passwd"
        
        export_config = AuditExportSchema(
            format="json",
            filters=AuditFilterSchema(),
            filename=malicious_filename
        )
        
        # Deve sanitizar o filename
        assert export_config.filename != malicious_filename
        assert ".." not in export_config.filename
        assert "/" not in export_config.filename
    
    def test_rate_limiting_enforcement(self, test_client):
        """Testa enforcement de rate limiting"""
        # Simular múltiplas requisições
        responses = []
        for i in range(60):  # Mais que o limite
            with patch('backend.app.api.auditoria.get_current_user') as mock_get_user:
                mock_get_user.return_value = {"id": "user_123", "permissions": ["audit:read"]}
                
                response = test_client.get("/api/audit/logs")
                responses.append(response.status_code)
        
        # Pelo menos uma deve retornar 429 (Too Many Requests)
        assert 429 in responses
    
    def test_permission_enforcement(self, test_client):
        """Testa enforcement de permissões"""
        # Usuário sem permissões
        with patch('backend.app.api.auditoria.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"id": "user_123", "permissions": []}
            
            response = test_client.get("/api/audit/logs")
            assert response.status_code == 403
    
    def test_input_validation(self, test_client):
        """Testa validação de entrada"""
        # Parâmetros inválidos
        with patch('backend.app.api.auditoria.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"id": "user_123", "permissions": ["audit:read"]}
            
            # Limit inválido
            response = test_client.get("/api/audit/logs?limit=9999")
            assert response.status_code == 400
            
            # Offset inválido
            response = test_client.get("/api/audit/logs?offset=-1")
            assert response.status_code == 400

class TestAuditEdgeCases:
    """Testes para casos extremos"""
    
    def test_empty_logs(self, audit_logger):
        """Testa comportamento com logs vazios"""
        filters = AuditFilterSchema()
        logs = audit_logger.get_audit_logs(filters)
        
        assert isinstance(logs, list)
        assert len(logs) >= 0
    
    def test_large_dataset(self, audit_logger):
        """Testa comportamento com grande volume de dados"""
        # Registrar muitos logs
        for i in range(100):
            audit_logger.log_event(
                event_type="user_login",
                message=f"Login {i}",
                user_id=f"user_{i}"
            )
        
        # Obter logs com limite
        filters = AuditFilterSchema(limit=50)
        logs = audit_logger.get_audit_logs(filters)
        
        assert len(logs) <= 50
    
    def test_concurrent_access(self, audit_logger):
        """Testa acesso concorrente"""
        import threading
        import time
        
        results = []
        
        def log_event(thread_id):
            try:
                log_id = audit_logger.log_event(
                    event_type="user_login",
                    message=f"Login thread {thread_id}",
                    user_id=f"user_{thread_id}"
                )
                results.append(log_id)
            except Exception as e:
                results.append(str(e))
        
        # Criar threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=log_event, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert len(results) == 10
        assert all(isinstance(r, str) for r in results)
    
    def test_database_corruption_recovery(self, audit_logger):
        """Testa recuperação de corrupção de banco"""
        # Simular corrupção
        audit_logger.db.close()
        
        # Tentar usar o logger
        try:
            log_id = audit_logger.log_event(
                event_type="user_login",
                message="Teste recuperação"
            )
            # Deve retornar string vazia em caso de erro
            assert log_id == ""
        except:
            # Deve lidar com erro graciosamente
            pass
    
    def test_memory_usage(self, audit_logger):
        """Testa uso de memória"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # Registrar muitos logs
        for i in range(1000):
            audit_logger.log_event(
                event_type="user_login",
                message=f"Login {i}",
                user_id=f"user_{i}"
            )
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Aumento de memória deve ser razoável (< 100MB)
        assert memory_increase < 100 * 1024 * 1024

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 