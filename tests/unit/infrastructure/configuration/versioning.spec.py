from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Versionamento de Configurações

Este módulo contém testes abrangentes para o sistema de versionamento
de configurações, cobrindo todas as funcionalidades principais:
- Criação de versões
- Ativação e rollback
- Comparação de versões
- Aprovação de mudanças
- Exportação e importação
- Backup e restauração

Autor: Sistema Omni Keywords Finder
Data: 2024-12-19
Versão: 1.0.0
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from shared.config_versioning import (
    ConfigVersioningSystem,
    ConfigStatus,
    ConfigType,
    ConfigVersion,
    ConfigChange,
    create_config_version,
    get_active_config,
    activate_config_version,
    rollback_config,
    export_config,
    import_config
)


class TestConfigVersioningSystem:
    """Testes para o sistema principal de versionamento"""
    
    @pytest.fixture
    def temp_db(self):
        """Cria banco de dados temporário para testes"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Limpa após os testes
        try:
            Path(db_path).unlink()
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def temp_backup_dir(self):
        """Cria diretório temporário para backups"""
        backup_dir = Path(tempfile.mkdtemp())
        yield backup_dir
        shutil.rmtree(backup_dir)
    
    @pytest.fixture
    def versioning_system(self, temp_db, temp_backup_dir):
        """Sistema de versionamento para testes"""
        return ConfigVersioningSystem(db_path=temp_db, backup_dir=str(temp_backup_dir))
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "test_db",
                "pool_size": 5
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            },
            "api": {
                "rate_limit": 100,
                "timeout": 30,
                "max_retries": 3
            }
        }
    
    @pytest.fixture
    def sample_config_v2(self):
        """Configuração modificada para testes de comparação"""
        return {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "test_db",
                "pool_size": 10  # Modificado
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            },
            "api": {
                "rate_limit": 200,  # Modificado
                "timeout": 30,
                "max_retries": 3
            },
            "logging": {  # Nova seção
                "level": "INFO",
                "format": "json"
            }
        }
    
    def test_init_database(self, versioning_system):
        """Testa inicialização do banco de dados"""
        # Verifica se as tabelas foram criadas
        with versioning_system._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('config_versions', 'config_changes', 'config_approvals')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            assert "config_versions" in tables
            assert "config_changes" in tables
            assert "config_approvals" in tables
    
    def test_create_version(self, versioning_system, sample_config):
        """Testa criação de versão de configuração"""
        version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user",
            description="Configuração de teste",
            tags=["test", "initial"]
        )
        
        assert version.id is not None
        assert version.config_name == "test_config"
        assert version.config_type == ConfigType.SYSTEM
        assert version.content == sample_config
        assert version.status == ConfigStatus.DRAFT
        assert version.created_by == "test_user"
        assert version.description == "Configuração de teste"
        assert "test" in version.tags
        assert "initial" in version.tags
    
    def test_create_duplicate_version(self, versioning_system, sample_config):
        """Testa criação de versão duplicada (mesmo conteúdo)"""
        # Cria primeira versão
        version1 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Tenta criar versão idêntica
        version2 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Deve retornar a mesma versão
        assert version1.id == version2.id
    
    def test_get_version(self, versioning_system, sample_config):
        """Testa obtenção de versão específica"""
        created_version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        retrieved_version = versioning_system.get_version(created_version.id)
        
        assert retrieved_version is not None
        assert retrieved_version.id == created_version.id
        assert retrieved_version.content == sample_config
    
    def test_get_version_by_hash(self, versioning_system, sample_config):
        """Testa obtenção de versão por hash"""
        created_version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        retrieved_version = versioning_system.get_version_by_hash(created_version.hash)
        
        assert retrieved_version is not None
        assert retrieved_version.id == created_version.id
    
    def test_get_active_version(self, versioning_system, sample_config):
        """Testa obtenção de versão ativa"""
        # Cria versão
        version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Ativa versão
        versioning_system.activate_version(version.id, "admin")
        
        # Obtém versão ativa
        active_version = versioning_system.get_active_version("test_config")
        
        assert active_version is not None
        assert active_version.id == version.id
        assert active_version.status == ConfigStatus.ACTIVE
    
    def test_get_version_history(self, versioning_system, sample_config, sample_config_v2):
        """Testa obtenção de histórico de versões"""
        # Cria múltiplas versões
        version1 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        version2 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config_v2,
            created_by="test_user"
        )
        
        # Obtém histórico
        history = versioning_system.get_version_history("test_config")
        
        assert len(history) >= 2
        assert any(value.id == version1.id for value in history)
        assert any(value.id == version2.id for value in history)
    
    def test_update_status(self, versioning_system, sample_config):
        """Testa atualização de status"""
        version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Atualiza status
        success = versioning_system.update_status(
            version.id, 
            ConfigStatus.PENDING_APPROVAL, 
            "approver"
        )
        
        assert success
        
        # Verifica se foi atualizado
        updated_version = versioning_system.get_version(version.id)
        assert updated_version.status == ConfigStatus.PENDING_APPROVAL
        assert updated_version.approved_by == "approver"
    
    def test_activate_version(self, versioning_system, sample_config, sample_config_v2):
        """Testa ativação de versão"""
        # Cria duas versões
        version1 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        version2 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config_v2,
            created_by="test_user"
        )
        
        # Ativa primeira versão
        versioning_system.activate_version(version1.id, "admin")
        
        # Ativa segunda versão (deve desativar a primeira)
        success = versioning_system.activate_version(version2.id, "admin")
        
        assert success
        
        # Verifica status
        active_version = versioning_system.get_active_version("test_config")
        assert active_version.id == version2.id
        assert active_version.status == ConfigStatus.ACTIVE
        
        # Verifica que primeira versão foi desativada
        old_version = versioning_system.get_version(version1.id)
        assert old_version.status == ConfigStatus.DEPRECATED
    
    def test_compare_versions(self, versioning_system, sample_config, sample_config_v2):
        """Testa comparação de versões"""
        # Cria duas versões diferentes
        version1 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        version2 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config_v2,
            created_by="test_user"
        )
        
        # Compara versões
        comparison = versioning_system.compare_versions(version1.id, version2.id)
        
        assert comparison["version1"]["id"] == version1.id
        assert comparison["version2"]["id"] == version2.id
        assert "diff_text" in comparison
        assert "changes" in comparison
        assert "summary" in comparison
        
        # Verifica mudanças detectadas
        changes = comparison["changes"]
        assert "database.pool_size" in changes["modified"]
        assert "api.rate_limit" in changes["modified"]
        assert "logging" in changes["added"]
        
        # Verifica resumo
        summary = comparison["summary"]
        assert summary["added_keys"] >= 1  # logging
        assert summary["modified_keys"] >= 2  # pool_size, rate_limit
    
    def test_rollback_to_version(self, versioning_system, sample_config, sample_config_v2):
        """Testa rollback para versão anterior"""
        # Cria duas versões
        version1 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        version2 = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config_v2,
            created_by="test_user"
        )
        
        # Ativa segunda versão
        versioning_system.activate_version(version2.id, "admin")
        
        # Faz rollback para primeira versão
        success = versioning_system.rollback_to_version(
            "test_config", 
            version1.id, 
            "admin"
        )
        
        assert success
        
        # Verifica que nova versão foi criada e ativada
        active_version = versioning_system.get_active_version("test_config")
        assert active_version.content == sample_config
        assert "rollback" in active_version.tags
    
    def test_export_configuration(self, versioning_system, sample_config):
        """Testa exportação de configuração"""
        version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Exporta em JSON
        json_export = versioning_system.export_configuration(version.id, "json")
        exported_data = json.loads(json_export)
        
        assert exported_data["metadata"]["id"] == version.id
        assert exported_data["content"] == sample_config
        
        # Exporta em YAML
        yaml_export = versioning_system.export_configuration(version.id, "yaml")
        assert "test_config" in yaml_export
        assert "database" in yaml_export
    
    def test_import_configuration(self, versioning_system, sample_config):
        """Testa importação de configuração"""
        # Cria dados de exportação
        export_data = {
            "metadata": {
                "config_name": "imported_config",
                "config_type": "system",
                "version": "v1.0.0",
                "created_by": "import_user",
                "description": "Configuração importada"
            },
            "content": sample_config
        }
        
        json_data = json.dumps(export_data)
        
        # Importa configuração
        imported_version = versioning_system.import_configuration(
            json_data, 
            "json", 
            "import_user"
        )
        
        assert imported_version.config_name == "imported_config"
        assert imported_version.content == sample_config
        assert "imported" in imported_version.tags
    
    def test_get_pending_approvals(self, versioning_system, sample_config):
        """Testa obtenção de versões pendentes de aprovação"""
        # Cria versão pendente
        version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        versioning_system.update_status(
            version.id, 
            ConfigStatus.PENDING_APPROVAL
        )
        
        # Obtém pendências
        pending = versioning_system.get_pending_approvals()
        
        assert len(pending) >= 1
        assert any(value.id == version.id for value in pending)
    
    def test_approve_version(self, versioning_system, sample_config):
        """Testa aprovação/rejeição de versão"""
        version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        versioning_system.update_status(
            version.id, 
            ConfigStatus.PENDING_APPROVAL
        )
        
        # Aprova versão
        success = versioning_system.approve_version(
            version.id, 
            "approver", 
            True, 
            "Aprovado para produção"
        )
        
        assert success
        
        # Verifica status
        approved_version = versioning_system.get_version(version.id)
        assert approved_version.status == ConfigStatus.APPROVED
        assert approved_version.approved_by == "approver"
    
    def test_create_backup(self, versioning_system, sample_config):
        """Testa criação de backup"""
        # Cria versão
        version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Cria backup
        backup_file = versioning_system.create_backup()
        
        assert Path(backup_file).exists()
        
        # Verifica conteúdo do backup
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        assert "backup_info" in backup_data
        assert "versions" in backup_data
        assert len(backup_data["versions"]) >= 1
    
    def test_restore_from_backup(self, versioning_system, sample_config):
        """Testa restauração de backup"""
        # Cria versão
        version = versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Cria backup
        backup_file = versioning_system.create_backup()
        
        # Limpa sistema
        versioning_system = ConfigVersioningSystem(
            db_path=versioning_system.db_path,
            backup_dir=str(versioning_system.backup_dir)
        )
        
        # Restaura backup
        restored_count = versioning_system.restore_from_backup(
            backup_file, 
            "restore_user"
        )
        
        assert restored_count >= 1
        
        # Verifica se versão foi restaurada
        restored_version = versioning_system.get_version(version.id)
        assert restored_version is not None
        assert restored_version.content == sample_config
    
    def test_get_statistics(self, versioning_system, sample_config):
        """Testa obtenção de estatísticas"""
        # Cria algumas versões
        versioning_system.create_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        versioning_system.create_version(
            config_name="test_config2",
            config_type=ConfigType.USER,
            content=sample_config,
            created_by="test_user"
        )
        
        # Obtém estatísticas
        stats = versioning_system.get_statistics()
        
        assert "total_versions" in stats
        assert "unique_configurations" in stats
        assert "status_distribution" in stats
        assert "type_distribution" in stats
        assert stats["total_versions"] >= 2
        assert stats["unique_configurations"] >= 2


class TestConfigVersioningFunctions:
    """Testes para funções de conveniência"""
    
    @pytest.fixture
    def temp_db(self):
        """Cria banco de dados temporário para testes"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        try:
            Path(db_path).unlink()
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def temp_backup_dir(self):
        """Cria diretório temporário para backups"""
        backup_dir = Path(tempfile.mkdtemp())
        yield backup_dir
        shutil.rmtree(backup_dir)
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return {
            "database": {"host": "localhost", "port": 5432},
            "api": {"timeout": 30}
        }
    
    def test_create_config_version_function(self, temp_db, temp_backup_dir, sample_config):
        """Testa função create_config_version"""
        # Configura sistema global
        import shared.config_versioning as cv
        cv.config_versioning = ConfigVersioningSystem(
            db_path=temp_db, 
            backup_dir=str(temp_backup_dir)
        )
        
        # Testa função
        version = create_config_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        assert version is not None
        assert version.config_name == "test_config"
        assert version.content == sample_config
    
    def test_get_active_config_function(self, temp_db, temp_backup_dir, sample_config):
        """Testa função get_active_config"""
        # Configura sistema global
        import shared.config_versioning as cv
        cv.config_versioning = ConfigVersioningSystem(
            db_path=temp_db, 
            backup_dir=str(temp_backup_dir)
        )
        
        # Cria e ativa versão
        version = create_config_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        activate_config_version(version.id, "admin")
        
        # Testa função
        active_config = get_active_config("test_config")
        
        assert active_config == sample_config
    
    def test_activate_config_version_function(self, temp_db, temp_backup_dir, sample_config):
        """Testa função activate_config_version"""
        # Configura sistema global
        import shared.config_versioning as cv
        cv.config_versioning = ConfigVersioningSystem(
            db_path=temp_db, 
            backup_dir=str(temp_backup_dir)
        )
        
        # Cria versão
        version = create_config_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Testa função
        success = activate_config_version(version.id, "admin")
        
        assert success
        
        # Verifica se foi ativada
        active_config = get_active_config("test_config")
        assert active_config == sample_config
    
    def test_rollback_config_function(self, temp_db, temp_backup_dir, sample_config):
        """Testa função rollback_config"""
        # Configura sistema global
        import shared.config_versioning as cv
        cv.config_versioning = ConfigVersioningSystem(
            db_path=temp_db, 
            backup_dir=str(temp_backup_dir)
        )
        
        # Cria duas versões
        version1 = create_config_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        modified_config = {**sample_config, "api": {"timeout": 60}}
        version2 = create_config_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=modified_config,
            created_by="test_user"
        )
        
        # Ativa segunda versão
        activate_config_version(version2.id, "admin")
        
        # Testa rollback
        success = rollback_config("test_config", version1.id, "admin")
        
        assert success
        
        # Verifica se voltou para primeira versão
        active_config = get_active_config("test_config")
        assert active_config == sample_config
    
    def test_export_config_function(self, temp_db, temp_backup_dir, sample_config):
        """Testa função export_config"""
        # Configura sistema global
        import shared.config_versioning as cv
        cv.config_versioning = ConfigVersioningSystem(
            db_path=temp_db, 
            backup_dir=str(temp_backup_dir)
        )
        
        # Cria versão
        version = create_config_version(
            config_name="test_config",
            config_type=ConfigType.SYSTEM,
            content=sample_config,
            created_by="test_user"
        )
        
        # Testa exportação
        exported = export_config(version.id, "json")
        exported_data = json.loads(exported)
        
        assert exported_data["metadata"]["id"] == version.id
        assert exported_data["content"] == sample_config
    
    def test_import_config_function(self, temp_db, temp_backup_dir, sample_config):
        """Testa função import_config"""
        # Configura sistema global
        import shared.config_versioning as cv
        cv.config_versioning = ConfigVersioningSystem(
            db_path=temp_db, 
            backup_dir=str(temp_backup_dir)
        )
        
        # Cria dados de exportação
        export_data = {
            "metadata": {
                "config_name": "imported_config",
                "config_type": "system",
                "version": "v1.0.0",
                "created_by": "import_user"
            },
            "content": sample_config
        }
        
        json_data = json.dumps(export_data)
        
        # Testa importação
        imported_version = import_config(json_data, "json", "import_user")
        
        assert imported_version.config_name == "imported_config"
        assert imported_version.content == sample_config


class TestConfigVersioningEdgeCases:
    """Testes para casos extremos e edge cases"""
    
    @pytest.fixture
    def temp_db(self):
        """Cria banco de dados temporário para testes"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        try:
            Path(db_path).unlink()
        except FileNotFoundError:
            pass
    
    @pytest.fixture
    def temp_backup_dir(self):
        """Cria diretório temporário para backups"""
        backup_dir = Path(tempfile.mkdtemp())
        yield backup_dir
        shutil.rmtree(backup_dir)
    
    @pytest.fixture
    def versioning_system(self, temp_db, temp_backup_dir):
        """Sistema de versionamento para testes"""
        return ConfigVersioningSystem(db_path=temp_db, backup_dir=str(temp_backup_dir))
    
    def test_empty_config(self, versioning_system):
        """Testa criação de configuração vazia"""
        version = versioning_system.create_version(
            config_name="empty_config",
            config_type=ConfigType.SYSTEM,
            content={},
            created_by="test_user"
        )
        
        assert version.content == {}
        assert version.hash is not None
    
    def test_large_config(self, versioning_system):
        """Testa configuração com muitos dados"""
        large_config = {
            "section_" + str(index): {
                "key_" + str(counter): f"value_{index}_{counter}"
                for counter in range(100)
            }
            for index in range(10)
        }
        
        version = versioning_system.create_version(
            config_name="large_config",
            config_type=ConfigType.SYSTEM,
            content=large_config,
            created_by="test_user"
        )
        
        assert version.content == large_config
    
    def test_nested_config(self, versioning_system):
        """Testa configuração com estrutura aninhada profunda"""
        nested_config = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "value": "deep_value"
                            }
                        }
                    }
                }
            }
        }
        
        version = versioning_system.create_version(
            config_name="nested_config",
            config_type=ConfigType.SYSTEM,
            content=nested_config,
            created_by="test_user"
        )
        
        assert version.content == nested_config
    
    def test_special_characters(self, versioning_system):
        """Testa configuração com caracteres especiais"""
        special_config = {
            "unicode": "café ☕ 🚀",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "newlines": "line1\nline2\nline3",
            "tabs": "col1\tcol2\tcol3"
        }
        
        version = versioning_system.create_version(
            config_name="special_config",
            config_type=ConfigType.SYSTEM,
            content=special_config,
            created_by="test_user"
        )
        
        assert version.content == special_config
    
    def test_invalid_version_id(self, versioning_system):
        """Testa obtenção de versão com ID inválido"""
        version = versioning_system.get_version("invalid_id")
        assert version is None
    
    def test_invalid_hash(self, versioning_system):
        """Testa obtenção de versão com hash inválido"""
        version = versioning_system.get_version_by_hash("invalid_hash")
        assert version is None
    
    def test_activate_nonexistent_version(self, versioning_system):
        """Testa ativação de versão inexistente"""
        success = versioning_system.activate_version("invalid_id", "admin")
        assert not success
    
    def test_rollback_nonexistent_version(self, versioning_system):
        """Testa rollback para versão inexistente"""
        success = versioning_system.rollback_to_version(
            "test_config", 
            "invalid_id", 
            "admin"
        )
        assert not success
    
    def test_export_nonexistent_version(self, versioning_system):
        """Testa exportação de versão inexistente"""
        with pytest.raises(ValueError):
            versioning_system.export_configuration("invalid_id", "json")
    
    def test_import_invalid_format(self, versioning_system):
        """Testa importação com formato inválido"""
        with pytest.raises(ValueError):
            versioning_system.import_configuration("data", "invalid_format", "user")
    
    def test_import_invalid_data(self, versioning_system):
        """Testa importação de dados inválidos"""
        with pytest.raises(ValueError):
            versioning_system.import_configuration("invalid json", "json", "user")
    
    def test_concurrent_access(self, versioning_system, sample_config):
        """Testa acesso concorrente ao sistema"""
        import threading
        import time
        
        results = []
        
        def create_version_thread():
            try:
                version = versioning_system.create_version(
                    config_name="concurrent_config",
                    config_type=ConfigType.SYSTEM,
                    content=sample_config,
                    created_by=f"user_{threading.current_thread().ident}"
                )
                results.append(version.id)
            except Exception as e:
                results.append(f"error: {e}")
        
        # Cria múltiplas threads
        threads = []
        for index in range(5):
            thread = threading.Thread(target=create_version_thread)
            threads.append(thread)
            thread.start()
        
        # Aguarda conclusão
        for thread in threads:
            thread.join()
        
        # Verifica resultados
        assert len(results) == 5
        # Pelo menos uma versão deve ter sido criada com sucesso
        assert any(not result.startswith("error:") for result in results)


if __name__ == "__main__":
    # Executa testes
    pytest.main([__file__, "-value"]) 