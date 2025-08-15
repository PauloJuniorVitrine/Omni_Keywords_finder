from typing import Dict, List, Optional, Any
"""
Testes unitários para Hash-based Audit Trails
Tracing ID: METRICS-003
Data/Hora: 2024-12-20 02:00:00 UTC
Versão: 1.0
Status: IMPLEMENTAÇÃO INICIAL

20 testes unitários abrangentes para validar o sistema de trilhas de auditoria
com hash SHA-256 e verificação de integridade.
"""

import pytest
import json
import tempfile
import os
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import redis
import sqlite3

from infrastructure.audit.hash_trail import (
    HashBasedAuditTrail,
    AuditEntry,
    AuditChain,
    IntegrityReport,
    AuditLevel,
    AuditCategory,
    add_audit_entry,
    get_audit_entry,
    verify_chain_integrity,
    search_audit_entries
)


class TestAuditLevel:
    """Testes para níveis de auditoria"""
    
    def test_audit_levels(self):
        """Testa todos os níveis de auditoria"""
        levels = list(AuditLevel)
        
        assert AuditLevel.INFO in levels
        assert AuditLevel.WARNING in levels
        assert AuditLevel.ERROR in levels
        assert AuditLevel.CRITICAL in levels
        assert AuditLevel.SECURITY in levels
    
    def test_audit_level_values(self):
        """Testa valores dos níveis de auditoria"""
        assert AuditLevel.INFO.value == "info"
        assert AuditLevel.WARNING.value == "warning"
        assert AuditLevel.ERROR.value == "error"
        assert AuditLevel.CRITICAL.value == "critical"
        assert AuditLevel.SECURITY.value == "security"


class TestAuditCategory:
    """Testes para categorias de auditoria"""
    
    def test_audit_categories(self):
        """Testa todas as categorias de auditoria"""
        categories = list(AuditCategory)
        
        assert AuditCategory.AUTHENTICATION in categories
        assert AuditCategory.AUTHORIZATION in categories
        assert AuditCategory.DATA_ACCESS in categories
        assert AuditCategory.DATA_MODIFICATION in categories
        assert AuditCategory.SYSTEM_CONFIG in categories
        assert AuditCategory.INTEGRATION in categories
        assert AuditCategory.COMPLIANCE in categories
        assert AuditCategory.SECURITY in categories
    
    def test_audit_category_values(self):
        """Testa valores das categorias de auditoria"""
        assert AuditCategory.AUTHENTICATION.value == "authentication"
        assert AuditCategory.AUTHORIZATION.value == "authorization"
        assert AuditCategory.DATA_ACCESS.value == "data_access"
        assert AuditCategory.DATA_MODIFICATION.value == "data_modification"
        assert AuditCategory.SYSTEM_CONFIG.value == "system_config"
        assert AuditCategory.INTEGRATION.value == "integration"
        assert AuditCategory.COMPLIANCE.value == "compliance"
        assert AuditCategory.SECURITY.value == "security"


class TestAuditEntry:
    """Testes para entradas de auditoria"""
    
    def test_audit_entry_creation(self):
        """Testa criação de entrada de auditoria"""
        entry = AuditEntry(
            entry_id="test_entry_001",
            timestamp=datetime.utcnow(),
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            user_id="user123",
            session_id="session456",
            action="read",
            resource="/api/users",
            details={"user_id": "user123", "permissions": ["read"]},
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            hash_value="abc123",
            previous_hash="def456",
            chain_position=0
        )
        
        assert entry.entry_id == "test_entry_001"
        assert entry.level == AuditLevel.INFO
        assert entry.category == AuditCategory.DATA_ACCESS
        assert entry.user_id == "user123"
        assert entry.action == "read"
        assert entry.resource == "/api/users"
        assert entry.hash_value == "abc123"
        assert entry.chain_position == 0
    
    def test_audit_entry_to_dict(self):
        """Testa conversão para dicionário"""
        entry = AuditEntry(
            entry_id="test_entry_002",
            timestamp=datetime.utcnow(),
            level=AuditLevel.WARNING,
            category=AuditCategory.SECURITY,
            user_id="user456",
            session_id="session789",
            action="login_failed",
            resource="/auth/login",
            details={"reason": "invalid_password"},
            ip_address="10.0.0.1",
            user_agent="PostmanRuntime/7.0",
            hash_value="xyz789",
            previous_hash="abc123",
            chain_position=1
        )
        
        data = entry.to_dict()
        
        assert data['entry_id'] == "test_entry_002"
        assert data['level'] == "warning"
        assert data['category'] == "security"
        assert data['action'] == "login_failed"
        assert data['hash_value'] == "xyz789"
        assert 'timestamp' in data
    
    def test_audit_entry_to_hash_string(self):
        """Testa conversão para string de hash"""
        entry = AuditEntry(
            entry_id="test_entry_003",
            timestamp=datetime.utcnow(),
            level=AuditLevel.ERROR,
            category=AuditCategory.INTEGRATION,
            user_id="user789",
            session_id="session123",
            action="api_call_failed",
            resource="/api/external",
            details={"error": "timeout", "endpoint": "/external/api"},
            ip_address="172.16.0.1",
            user_agent="curl/7.0",
            hash_value="",
            previous_hash="xyz789",
            chain_position=2
        )
        
        hash_string = entry.to_hash_string()
        
        assert isinstance(hash_string, str)
        assert len(hash_string) > 0
        assert "test_entry_003" in hash_string
        assert "error" in hash_string
        assert "api_call_failed" in hash_string


class TestAuditChain:
    """Testes para cadeias de auditoria"""
    
    def test_audit_chain_creation(self):
        """Testa criação de cadeia de auditoria"""
        chain = AuditChain(
            chain_id="chain_1234567890",
            start_timestamp=datetime.utcnow(),
            end_timestamp=None,
            entry_count=0,
            root_hash="root_hash_abc123",
            current_hash="root_hash_abc123",
            is_complete=False,
            integrity_verified=True
        )
        
        assert chain.chain_id == "chain_1234567890"
        assert chain.entry_count == 0
        assert chain.root_hash == "root_hash_abc123"
        assert chain.current_hash == "root_hash_abc123"
        assert chain.is_complete is False
        assert chain.integrity_verified is True
    
    def test_audit_chain_to_dict(self):
        """Testa conversão para dicionário"""
        chain = AuditChain(
            chain_id="chain_0987654321",
            start_timestamp=datetime.utcnow(),
            end_timestamp=datetime.utcnow() + timedelta(hours=1),
            entry_count=100,
            root_hash="root_hash_def456",
            current_hash="current_hash_xyz789",
            is_complete=True,
            integrity_verified=True
        )
        
        data = chain.to_dict()
        
        assert data['chain_id'] == "chain_0987654321"
        assert data['entry_count'] == 100
        assert data['root_hash'] == "root_hash_def456"
        assert data['current_hash'] == "current_hash_xyz789"
        assert data['is_complete'] is True
        assert data['integrity_verified'] is True
        assert 'start_timestamp' in data
        assert 'end_timestamp' in data


class TestIntegrityReport:
    """Testes para relatórios de integridade"""
    
    def test_integrity_report_creation(self):
        """Testa criação de relatório de integridade"""
        report = IntegrityReport(
            report_id="INTEGRITY_chain_123_20241220_020000",
            timestamp=datetime.utcnow(),
            chain_id="chain_123",
            total_entries=100,
            verified_entries=95,
            corrupted_entries=3,
            missing_entries=2,
            integrity_score=95.0,
            violations=[
                {"type": "hash_mismatch", "entry_id": "entry_001"},
                {"type": "missing_entries", "expected_count": 100, "actual_count": 98}
            ],
            recommendations=[
                "Investigar entradas corrompidas",
                "Recuperar entradas faltando"
            ]
        )
        
        assert report.report_id == "INTEGRITY_chain_123_20241220_020000"
        assert report.chain_id == "chain_123"
        assert report.total_entries == 100
        assert report.verified_entries == 95
        assert report.corrupted_entries == 3
        assert report.missing_entries == 2
        assert report.integrity_score == 95.0
        assert len(report.violations) == 2
        assert len(report.recommendations) == 2
    
    def test_integrity_report_to_dict(self):
        """Testa conversão para dicionário"""
        report = IntegrityReport(
            report_id="INTEGRITY_chain_456_20241220_020000",
            timestamp=datetime.utcnow(),
            chain_id="chain_456",
            total_entries=50,
            verified_entries=50,
            corrupted_entries=0,
            missing_entries=0,
            integrity_score=100.0,
            violations=[],
            recommendations=[]
        )
        
        data = report.to_dict()
        
        assert data['report_id'] == "INTEGRITY_chain_456_20241220_020000"
        assert data['chain_id'] == "chain_456"
        assert data['total_entries'] == 50
        assert data['verified_entries'] == 50
        assert data['integrity_score'] == 100.0
        assert 'timestamp' in data


class TestHashBasedAuditTrail:
    """Testes para o sistema de trilhas de auditoria"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Fixture para banco de dados temporário"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Limpa arquivo temporário
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def audit_trail(self, temp_db_path):
        """Fixture para sistema de auditoria"""
        return HashBasedAuditTrail(db_path=temp_db_path)
    
    @pytest.fixture
    def mock_redis(self):
        """Fixture para Redis mock"""
        return Mock(spec=redis.Redis)
    
    def test_audit_trail_initialization(self, temp_db_path):
        """Testa inicialização do sistema de auditoria"""
        audit_trail = HashBasedAuditTrail(db_path=temp_db_path)
        
        assert audit_trail.db_path == temp_db_path
        assert audit_trail.current_chain is not None
        assert audit_trail.current_chain.entry_count == 0
        assert audit_trail.current_chain.is_complete is False
    
    def test_audit_trail_with_redis(self, temp_db_path, mock_redis):
        """Testa inicialização com Redis"""
        audit_trail = HashBasedAuditTrail(db_path=temp_db_path, redis_client=mock_redis)
        
        assert audit_trail.redis_client == mock_redis
        assert audit_trail.current_chain is not None
    
    def test_audit_trail_with_secret_key(self, temp_db_path):
        """Testa inicialização com chave secreta"""
        secret_key = "test_secret_key_123"
        audit_trail = HashBasedAuditTrail(db_path=temp_db_path, secret_key=secret_key)
        
        assert audit_trail.secret_key == secret_key
        assert audit_trail.current_chain is not None
    
    def test_add_audit_entry_info(self, audit_trail):
        """Testa adição de entrada de auditoria INFO"""
        entry = audit_trail.add_audit_entry(
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            action="read",
            resource="/api/users",
            details={"user_id": "user123", "permissions": ["read"]},
            user_id="user123",
            session_id="session456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        assert entry.level == AuditLevel.INFO
        assert entry.category == AuditCategory.DATA_ACCESS
        assert entry.action == "read"
        assert entry.user_id == "user123"
        assert entry.hash_value is not None
        assert len(entry.hash_value) > 0
        assert entry.chain_position == 0
        assert audit_trail.current_chain.entry_count == 1
    
    def test_add_audit_entry_security(self, audit_trail):
        """Testa adição de entrada de auditoria SECURITY"""
        entry = audit_trail.add_audit_entry(
            level=AuditLevel.SECURITY,
            category=AuditCategory.AUTHENTICATION,
            action="login_failed",
            resource="/auth/login",
            details={"reason": "invalid_password", "attempts": 3},
            user_id="user456",
            ip_address="10.0.0.1"
        )
        
        assert entry.level == AuditLevel.SECURITY
        assert entry.category == AuditCategory.AUTHENTICATION
        assert entry.action == "login_failed"
        assert entry.hash_value is not None
        assert entry.chain_position == 0
        assert audit_trail.current_chain.entry_count == 1
    
    def test_add_audit_entry_with_redis(self, temp_db_path, mock_redis):
        """Testa adição de entrada com cache Redis"""
        audit_trail = HashBasedAuditTrail(db_path=temp_db_path, redis_client=mock_redis)
        
        entry = audit_trail.add_audit_entry(
            level=AuditLevel.WARNING,
            category=AuditCategory.INTEGRATION,
            action="api_timeout",
            resource="/api/external",
            details={"timeout": 30, "endpoint": "/external/api"}
        )
        
        # Verifica se foi chamado o Redis
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"audit_entry:{entry.entry_id}"
        assert call_args[0][1] == 3600  # 1 hora
    
    def test_chain_integrity_verification(self, audit_trail):
        """Testa verificação de integridade da cadeia"""
        # Adiciona algumas entradas
        for index in range(3):
            audit_trail.add_audit_entry(
                level=AuditLevel.INFO,
                category=AuditCategory.DATA_ACCESS,
                action=f"action_{index}",
                resource=f"/api/resource_{index}",
                details={"index": index}
            )
        
        # Finaliza cadeia atual
        chain_id = audit_trail.current_chain.chain_id
        audit_trail._finalize_current_chain()
        
        # Verifica integridade
        report = audit_trail.verify_chain_integrity(chain_id)
        
        assert report.chain_id == chain_id
        assert report.total_entries == 3
        assert report.verified_entries == 3
        assert report.corrupted_entries == 0
        assert report.missing_entries == 0
        assert report.integrity_score == 100.0
        assert len(report.violations) == 0
    
    def test_get_audit_entry(self, audit_trail):
        """Testa obtenção de entrada de auditoria"""
        # Adiciona entrada
        original_entry = audit_trail.add_audit_entry(
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            action="read",
            resource="/api/users",
            details={"user_id": "user123"}
        )
        
        # Obtém entrada
        retrieved_entry = audit_trail.get_audit_entry(original_entry.entry_id)
        
        assert retrieved_entry is not None
        assert retrieved_entry.entry_id == original_entry.entry_id
        assert retrieved_entry.action == original_entry.action
        assert retrieved_entry.hash_value == original_entry.hash_value
    
    def test_get_audit_entry_from_cache(self, temp_db_path, mock_redis):
        """Testa obtenção de entrada do cache Redis"""
        mock_entry_data = {
            'entry_id': 'test_entry_001',
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'info',
            'category': 'data_access',
            'user_id': 'user123',
            'session_id': None,
            'action': 'read',
            'resource': '/api/users',
            'details': {'user_id': 'user123'},
            'ip_address': None,
            'user_agent': None,
            'hash_value': 'abc123',
            'previous_hash': None,
            'chain_position': 0
        }
        mock_redis.get.return_value = json.dumps(mock_entry_data)
        
        audit_trail = HashBasedAuditTrail(db_path=temp_db_path, redis_client=mock_redis)
        entry = audit_trail.get_audit_entry("test_entry_001")
        
        assert entry is not None
        assert entry.entry_id == "test_entry_001"
        assert entry.action == "read"
    
    def test_get_audit_entry_not_found(self, audit_trail):
        """Testa obtenção de entrada inexistente"""
        entry = audit_trail.get_audit_entry("nonexistent_entry")
        assert entry is None
    
    def test_search_audit_entries(self, audit_trail):
        """Testa busca de entradas de auditoria"""
        # Adiciona entradas com diferentes características
        audit_trail.add_audit_entry(
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            action="read",
            resource="/api/users",
            details={"user_id": "user123"},
            user_id="user123"
        )
        
        audit_trail.add_audit_entry(
            level=AuditLevel.WARNING,
            category=AuditCategory.SECURITY,
            action="login_failed",
            resource="/auth/login",
            details={"reason": "invalid_password"},
            user_id="user456"
        )
        
        # Busca por usuário
        user_entries = audit_trail.search_audit_entries(user_id="user123")
        assert len(user_entries) == 1
        assert user_entries[0].user_id == "user123"
        
        # Busca por nível
        warning_entries = audit_trail.search_audit_entries(level=AuditLevel.WARNING)
        assert len(warning_entries) == 1
        assert warning_entries[0].level == AuditLevel.WARNING
        
        # Busca por categoria
        security_entries = audit_trail.search_audit_entries(category=AuditCategory.SECURITY)
        assert len(security_entries) == 1
        assert security_entries[0].category == AuditCategory.SECURITY
    
    def test_search_audit_entries_with_date_range(self, audit_trail):
        """Testa busca de entradas com intervalo de datas"""
        # Adiciona entrada
        audit_trail.add_audit_entry(
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            action="read",
            resource="/api/users",
            details={"user_id": "user123"}
        )
        
        # Busca com intervalo de datas
        start_date = datetime.utcnow() - timedelta(hours=1)
        end_date = datetime.utcnow() + timedelta(hours=1)
        
        entries = audit_trail.search_audit_entries(
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(entries) == 1
    
    def test_get_audit_statistics(self, audit_trail):
        """Testa obtenção de estatísticas de auditoria"""
        # Adiciona entradas com diferentes características
        for index in range(5):
            audit_trail.add_audit_entry(
                level=AuditLevel.INFO if index % 2 == 0 else AuditLevel.WARNING,
                category=AuditCategory.DATA_ACCESS if index % 2 == 0 else AuditCategory.SECURITY,
                action=f"action_{index}",
                resource=f"/api/resource_{index}",
                details={"index": index},
                user_id=f"user_{index % 3}"
            )
        
        stats = audit_trail.get_audit_statistics()
        
        assert stats['total_entries'] == 5
        assert 'entries_by_level' in stats
        assert 'entries_by_category' in stats
        assert 'entries_by_user' in stats
        assert 'entries_by_action' in stats
        assert 'period' in stats
    
    def test_export_audit_trail_json(self, audit_trail):
        """Testa exportação de trilha em formato JSON"""
        # Adiciona algumas entradas
        for index in range(3):
            audit_trail.add_audit_entry(
                level=AuditLevel.INFO,
                category=AuditCategory.DATA_ACCESS,
                action=f"action_{index}",
                resource=f"/api/resource_{index}",
                details={"index": index}
            )
        
        # Exporta em JSON
        export_data = audit_trail.export_audit_trail(format="json")
        
        assert isinstance(export_data, str)
        data = json.loads(export_data)
        assert 'export_info' in data
        assert 'entries' in data
        assert len(data['entries']) == 3
    
    def test_export_audit_trail_csv(self, audit_trail):
        """Testa exportação de trilha em formato CSV"""
        # Adiciona algumas entradas
        for index in range(2):
            audit_trail.add_audit_entry(
                level=AuditLevel.INFO,
                category=AuditCategory.DATA_ACCESS,
                action=f"action_{index}",
                resource=f"/api/resource_{index}",
                details={"index": index}
            )
        
        # Exporta em CSV
        export_data = audit_trail.export_audit_trail(format="csv")
        
        assert isinstance(export_data, str)
        lines = export_data.strip().split('\n')
        assert len(lines) == 3  # Cabeçalho + 2 entradas
        assert 'entry_id' in lines[0]
        assert 'timestamp' in lines[0]
    
    def test_export_audit_trail_invalid_format(self, audit_trail):
        """Testa exportação com formato inválido"""
        with pytest.raises(ValueError):
            audit_trail.export_audit_trail(format="invalid_format")
    
    def test_chain_finalization(self, audit_trail):
        """Testa finalização automática de cadeia"""
        # Adiciona entradas até o limite (10k)
        # Para teste, vamos simular com um limite menor
        original_limit = audit_trail.current_chain.entry_count
        audit_trail.current_chain.entry_count = 9999  # Próximo ao limite
        
        # Adiciona uma entrada que deve finalizar a cadeia
        entry = audit_trail.add_audit_entry(
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            action="final_action",
            resource="/api/final",
            details={"final": True}
        )
        
        # Verifica se nova cadeia foi iniciada
        assert audit_trail.current_chain.entry_count == 0
        assert audit_trail.current_chain.chain_id != entry.chain_position


class TestConvenienceFunctions:
    """Testes para funções de conveniência"""
    
    @patch('infrastructure.audit.hash_trail.audit_trail')
    def test_add_audit_entry_function(self, mock_trail):
        """Testa função de conveniência add_audit_entry"""
        mock_entry = Mock(spec=AuditEntry)
        mock_trail.add_audit_entry.return_value = mock_entry
        
        result = add_audit_entry(
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            action="test_action",
            resource="/api/test",
            details={"test": True}
        )
        
        assert result == mock_entry
        mock_trail.add_audit_entry.assert_called_once()
    
    @patch('infrastructure.audit.hash_trail.audit_trail')
    def test_get_audit_entry_function(self, mock_trail):
        """Testa função de conveniência get_audit_entry"""
        mock_entry = Mock(spec=AuditEntry)
        mock_trail.get_audit_entry.return_value = mock_entry
        
        result = get_audit_entry("test_entry_id")
        
        assert result == mock_entry
        mock_trail.get_audit_entry.assert_called_once_with("test_entry_id")
    
    @patch('infrastructure.audit.hash_trail.audit_trail')
    def test_verify_chain_integrity_function(self, mock_trail):
        """Testa função de conveniência verify_chain_integrity"""
        mock_report = Mock(spec=IntegrityReport)
        mock_trail.verify_chain_integrity.return_value = mock_report
        
        result = verify_chain_integrity("test_chain_id")
        
        assert result == mock_report
        mock_trail.verify_chain_integrity.assert_called_once_with("test_chain_id")
    
    @patch('infrastructure.audit.hash_trail.audit_trail')
    def test_search_audit_entries_function(self, mock_trail):
        """Testa função de conveniência search_audit_entries"""
        mock_entries = [Mock(spec=AuditEntry), Mock(spec=AuditEntry)]
        mock_trail.search_audit_entries.return_value = mock_entries
        
        result = search_audit_entries(user_id="test_user")
        
        assert result == mock_entries
        mock_trail.search_audit_entries.assert_called_once_with(user_id="test_user") 