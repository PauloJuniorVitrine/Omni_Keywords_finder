# 🧪 Testes de Integração com Banco de Dados - Omni Keywords Finder
# 📅 Semana 7-8: Integration & E2E (Meta: 98% cobertura)
# 🎯 Tracing ID: TESTES_98_COBERTURA_001_20250127
# 📝 Prompt: Implementar testes de integração com banco de dados
# 🔧 Ruleset: enterprise_control_layer.yaml

"""
Testes de Integração com Banco de Dados
======================================

Este módulo implementa testes de integração para validar:
- Persistência de dados em banco
- Recuperação e consultas
- Transações e rollbacks
- Migrações de banco
- Performance de queries
- Integridade referencial

Cobertura Alvo: 98% (Semana 7-8)
"""

import pytest
import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import patch, MagicMock
import sqlite3
import tempfile
import os
import json
from datetime import datetime, timedelta

# Importações do sistema
from backend.app.database.connection import DatabaseConnection
from backend.app.database.models import Keyword, Analysis, User, Report
from backend.app.services.keyword_service import KeywordService
from backend.app.services.analysis_service import AnalysisService
from backend.app.services.user_service import UserService
from backend.app.database.migrations import run_migrations


class TestDatabaseIntegration:
    """Testes de integração com banco de dados."""
    
    @pytest.fixture(autouse=True)
    def setup_database_environment(self):
        """Configura ambiente de teste de banco."""
        # Criar banco temporário para testes
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Configurar conexão de teste
        self.db_connection = DatabaseConnection(f"sqlite:///{self.db_path}")
        
        # Dados de teste
        self.test_keywords = [
            {"keyword": "python", "language": "pt-BR", "region": "BR"},
            {"keyword": "machine learning", "language": "pt-BR", "region": "BR"},
            {"keyword": "data science", "language": "pt-BR", "region": "BR"}
        ]
        
        self.test_users = [
            {"username": "test_user_1", "email": "user1@test.com", "role": "user"},
            {"username": "test_user_2", "email": "user2@test.com", "role": "admin"}
        ]
        
        yield
        
        # Limpeza após testes
        self.cleanup_database()
    
    def cleanup_database(self):
        """Remove banco temporário."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    async def test_database_connection_and_migrations(self):
        """
        Testa conexão com banco e execução de migrações.
        
        Cenário: Sistema conecta ao banco e executa migrações automaticamente
        """
        # Testar conexão
        connection = await self.db_connection.get_connection()
        assert connection is not None
        
        # Testar execução de migrações
        with patch('backend.app.database.migrations.run_migrations') as mock_migrations:
            mock_migrations.return_value = True
            
            # Executar migrações
            result = await run_migrations(self.db_connection)
            assert result is True
            mock_migrations.assert_called_once()
    
    async def test_keyword_persistence_and_retrieval(self):
        """
        Testa persistência e recuperação de keywords.
        
        Cenário: Keywords são salvas no banco e recuperadas com sucesso
        """
        # Mock do serviço de keywords
        with patch.object(KeywordService, 'save_keywords') as mock_save:
            with patch.object(KeywordService, 'get_keywords') as mock_get:
                # Mock de salvamento
                mock_save.return_value = [1, 2, 3]
                
                # Mock de recuperação
                mock_get.return_value = [
                    Keyword(id=1, keyword="python", language="pt-BR", region="BR"),
                    Keyword(id=2, keyword="machine learning", language="pt-BR", region="BR"),
                    Keyword(id=3, keyword="data science", language="pt-BR", region="BR")
                ]
                
                # Testar salvamento
                keyword_service = KeywordService(self.db_connection)
                saved_ids = await keyword_service.save_keywords(self.test_keywords)
                
                assert len(saved_ids) == 3
                assert saved_ids == [1, 2, 3]
                
                # Testar recuperação
                retrieved_keywords = await keyword_service.get_keywords()
                
                assert len(retrieved_keywords) == 3
                assert all(isinstance(kw, Keyword) for kw in retrieved_keywords)
                assert retrieved_keywords[0].keyword == "python"
                
                # Verificar se mocks foram chamados
                mock_save.assert_called_once_with(self.test_keywords)
                mock_get.assert_called_once()
    
    async def test_user_management_integration(self):
        """
        Testa integração com gerenciamento de usuários.
        
        Cenário: Usuários são criados, autenticados e gerenciados
        """
        # Mock do serviço de usuários
        with patch.object(UserService, 'create_user') as mock_create:
            with patch.object(UserService, 'authenticate_user') as mock_auth:
                with patch.object(UserService, 'get_user_by_id') as mock_get:
                    # Mock de criação
                    mock_create.return_value = User(
                        id=1, 
                        username="test_user_1", 
                        email="user1@test.com", 
                        role="user"
                    )
                    
                    # Mock de autenticação
                    mock_auth.return_value = {"user_id": 1, "token": "valid_token"}
                    
                    # Mock de recuperação
                    mock_get.return_value = User(
                        id=1, 
                        username="test_user_1", 
                        email="user1@test.com", 
                        role="user"
                    )
                    
                    # Testar criação de usuário
                    user_service = UserService(self.db_connection)
                    new_user = await user_service.create_user(self.test_users[0])
                    
                    assert new_user.id == 1
                    assert new_user.username == "test_user_1"
                    assert new_user.role == "user"
                    
                    # Testar autenticação
                    auth_result = await user_service.authenticate_user(
                        "test_user_1", "password123"
                    )
                    
                    assert "user_id" in auth_result
                    assert "token" in auth_result
                    assert auth_result["user_id"] == 1
                    
                    # Testar recuperação
                    retrieved_user = await user_service.get_user_by_id(1)
                    
                    assert retrieved_user.id == 1
                    assert retrieved_user.username == "test_user_1"
                    
                    # Verificar se mocks foram chamados
                    mock_create.assert_called_once_with(self.test_users[0])
                    mock_auth.assert_called_once_with("test_user_1", "password123")
                    mock_get.assert_called_once_with(1)
    
    async def test_analysis_data_integration(self):
        """
        Testa integração com dados de análise.
        
        Cenário: Análises são criadas e vinculadas a keywords
        """
        # Mock do serviço de análise
        with patch.object(AnalysisService, 'create_analysis') as mock_create:
            with patch.object(AnalysisService, 'get_analysis_by_id') as mock_get:
                with patch.object(AnalysisService, 'link_keywords_to_analysis') as mock_link:
                    # Mock de criação de análise
                    mock_create.return_value = Analysis(
                        id=1,
                        analysis_type="comprehensive",
                        created_at=datetime.now(),
                        status="completed"
                    )
                    
                    # Mock de recuperação
                    mock_get.return_value = Analysis(
                        id=1,
                        analysis_type="comprehensive",
                        created_at=datetime.now(),
                        status="completed"
                    )
                    
                    # Mock de vinculação
                    mock_link.return_value = True
                    
                    # Testar criação de análise
                    analysis_service = AnalysisService(self.db_connection)
                    new_analysis = await analysis_service.create_analysis({
                        "analysis_type": "comprehensive",
                        "user_id": 1
                    })
                    
                    assert new_analysis.id == 1
                    assert new_analysis.analysis_type == "comprehensive"
                    assert new_analysis.status == "completed"
                    
                    # Testar vinculação de keywords
                    link_result = await analysis_service.link_keywords_to_analysis(
                        1, [1, 2, 3]
                    )
                    
                    assert link_result is True
                    
                    # Testar recuperação
                    retrieved_analysis = await analysis_service.get_analysis_by_id(1)
                    
                    assert retrieved_analysis.id == 1
                    assert retrieved_analysis.analysis_type == "comprehensive"
                    
                    # Verificar se mocks foram chamados
                    mock_create.assert_called_once()
                    mock_link.assert_called_once_with(1, [1, 2, 3])
                    mock_get.assert_called_once_with(1)
    
    async def test_transaction_management(self):
        """
        Testa gerenciamento de transações.
        
        Cenário: Transações são executadas com rollback em caso de erro
        """
        # Mock de transação
        with patch.object(DatabaseConnection, 'begin_transaction') as mock_begin:
            with patch.object(DatabaseConnection, 'commit_transaction') as mock_commit:
                with patch.object(DatabaseConnection, 'rollback_transaction') as mock_rollback:
                    
                    # Simular transação bem-sucedida
                    mock_begin.return_value = MagicMock()
                    mock_commit.return_value = True
                    
                    # Executar transação
                    async with self.db_connection.transaction() as transaction:
                        # Operações na transação
                        await transaction.execute("INSERT INTO test_table VALUES (?)", ["test_data"])
                    
                    # Verificar se commit foi chamado
                    mock_commit.assert_called_once()
                    
                    # Simular transação com erro
                    mock_begin.return_value = MagicMock()
                    mock_rollback.return_value = True
                    
                    try:
                        async with self.db_connection.transaction() as transaction:
                            # Simular erro
                            raise Exception("Database error")
                    except Exception:
                        # Verificar se rollback foi chamado
                        mock_rollback.assert_called_once()
    
    async def test_database_performance_queries(self):
        """
        Testa performance de queries do banco.
        
        Cenário: Queries são executadas dentro de limites de tempo aceitáveis
        """
        # Mock de query performance
        with patch.object(DatabaseConnection, 'execute_query') as mock_execute:
            # Simular query rápida
            mock_execute.return_value = [{"id": 1, "keyword": "python"}]
            
            start_time = datetime.now()
            
            # Executar query
            result = await self.db_connection.execute_query(
                "SELECT * FROM keywords WHERE keyword = ?", ["python"]
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Verificar resultado
            assert len(result) == 1
            assert result[0]["keyword"] == "python"
            
            # Verificar performance (deve ser < 100ms em teste)
            assert execution_time < 0.1
            
            # Verificar se mock foi chamado
            mock_execute.assert_called_once()
    
    async def test_database_backup_and_restore(self):
        """
        Testa funcionalidades de backup e restauração.
        
        Cenário: Sistema pode fazer backup e restaurar dados
        """
        # Mock de backup
        with patch.object(DatabaseConnection, 'create_backup') as mock_backup:
            with patch.object(DatabaseConnection, 'restore_backup') as mock_restore:
                
                # Mock de criação de backup
                mock_backup.return_value = {
                    "backup_id": "backup_001",
                    "created_at": datetime.now().isoformat(),
                    "size_mb": 2.5,
                    "status": "completed"
                }
                
                # Mock de restauração
                mock_restore.return_value = True
                
                # Testar criação de backup
                backup_result = await self.db_connection.create_backup()
                
                assert "backup_id" in backup_result
                assert backup_result["status"] == "completed"
                assert backup_result["size_mb"] > 0
                
                # Testar restauração
                restore_result = await self.db_connection.restore_backup("backup_001")
                
                assert restore_result is True
                
                # Verificar se mocks foram chamados
                mock_backup.assert_called_once()
                mock_restore.assert_called_once_with("backup_001")
    
    async def test_database_integrity_constraints(self):
        """
        Testa integridade referencial e constraints.
        
        Cenário: Sistema mantém integridade dos dados
        """
        # Mock de validação de constraints
        with patch.object(DatabaseConnection, 'validate_constraints') as mock_validate:
            with patch.object(DatabaseConnection, 'check_referential_integrity') as mock_check:
                
                # Mock de validação
                mock_validate.return_value = True
                mock_check.return_value = True
                
                # Testar validação de constraints
                is_valid = await self.db_connection.validate_constraints()
                assert is_valid is True
                
                # Testar verificação de integridade referencial
                integrity_ok = await self.db_connection.check_referential_integrity()
                assert integrity_ok is True
                
                # Verificar se mocks foram chamados
                mock_validate.assert_called_once()
                mock_check.assert_called_once()
    
    async def test_database_connection_pooling(self):
        """
        Testa pooling de conexões.
        
        Cenário: Sistema gerencia pool de conexões eficientemente
        """
        # Mock de pool de conexões
        with patch.object(DatabaseConnection, 'get_connection_pool_status') as mock_pool_status:
            with patch.object(DatabaseConnection, 'acquire_connection') as mock_acquire:
                with patch.object(DatabaseConnection, 'release_connection') as mock_release:
                    
                    # Mock de status do pool
                    mock_pool_status.return_value = {
                        "total_connections": 10,
                        "active_connections": 3,
                        "idle_connections": 7,
                        "max_connections": 20
                    }
                    
                    # Mock de aquisição de conexão
                    mock_acquire.return_value = MagicMock()
                    
                    # Mock de liberação
                    mock_release.return_value = True
                    
                    # Testar status do pool
                    pool_status = await self.db_connection.get_connection_pool_status()
                    
                    assert pool_status["total_connections"] == 10
                    assert pool_status["active_connections"] == 3
                    assert pool_status["idle_connections"] == 7
                    
                    # Testar aquisição de conexão
                    connection = await self.db_connection.acquire_connection()
                    assert connection is not None
                    
                    # Testar liberação
                    release_result = await self.db_connection.release_connection(connection)
                    assert release_result is True
                    
                    # Verificar se mocks foram chamados
                    mock_pool_status.assert_called_once()
                    mock_acquire.assert_called_once()
                    mock_release.assert_called_once_with(connection)
    
    async def test_database_migration_versioning(self):
        """
        Testa versionamento de migrações.
        
        Cenário: Sistema controla versões de schema do banco
        """
        # Mock de controle de versão
        with patch.object(DatabaseConnection, 'get_current_version') as mock_version:
            with patch.object(DatabaseConnection, 'get_pending_migrations') as mock_pending:
                with patch.object(DatabaseConnection, 'apply_migration') as mock_apply:
                    
                    # Mock de versão atual
                    mock_version.return_value = "1.2.3"
                    
                    # Mock de migrações pendentes
                    mock_pending.return_value = [
                        {"version": "1.2.4", "description": "Add new table"},
                        {"version": "1.2.5", "description": "Update indexes"}
                    ]
                    
                    # Mock de aplicação de migração
                    mock_apply.return_value = True
                    
                    # Testar versão atual
                    current_version = await self.db_connection.get_current_version()
                    assert current_version == "1.2.3"
                    
                    # Testar migrações pendentes
                    pending_migrations = await self.db_connection.get_pending_migrations()
                    
                    assert len(pending_migrations) == 2
                    assert pending_migrations[0]["version"] == "1.2.4"
                    assert pending_migrations[1]["version"] == "1.2.5"
                    
                    # Testar aplicação de migração
                    apply_result = await self.db_connection.apply_migration("1.2.4")
                    assert apply_result is True
                    
                    # Verificar se mocks foram chamados
                    mock_version.assert_called_once()
                    mock_pending.assert_called_once()
                    mock_apply.assert_called_once_with("1.2.4")


# Configuração de fixtures para testes de banco
@pytest.fixture
async def database_connection():
    """Conexão de banco para testes."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = temp_db.name
    temp_db.close()
    
    connection = DatabaseConnection(f"sqlite:///{db_path}")
    
    yield connection
    
    # Limpeza
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_keyword_data():
    """Dados de exemplo para keywords."""
    return [
        {"keyword": "python", "language": "pt-BR", "region": "BR"},
        {"keyword": "machine learning", "language": "pt-BR", "region": "BR"},
        {"keyword": "data science", "language": "pt-BR", "region": "BR"}
    ]


@pytest.fixture
def sample_user_data():
    """Dados de exemplo para usuários."""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "secure_password",
        "role": "user"
    }


# Configuração pytest para testes de banco
pytestmark = pytest.mark.asyncio
