"""
Testes Unitários para Backup Service
Serviço de Backup Robusto - Omni Keywords Finder

Prompt: Implementação de testes unitários para serviço de backup
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import os
import shutil
import tempfile
import zipfile
import hashlib
import json
import time
import threading
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from backend.app.services.backup_service import (
    BackupService,
    BackupMetadata
)
from backend.app.models.prompt_system import LogOperacao


class TestBackupMetadata:
    """Testes para BackupMetadata"""
    
    def test_backup_metadata_creation(self):
        """Testa criação de BackupMetadata"""
        metadata = BackupMetadata(
            backup_id="test_backup_20250127",
            timestamp="2025-01-27T10:30:00",
            size_bytes=1024000,
            file_count=50,
            checksum="abc123def456",
            compression_ratio=25.5,
            status="completed",
            backup_type="manual"
        )
        
        assert metadata.backup_id == "test_backup_20250127"
        assert metadata.timestamp == "2025-01-27T10:30:00"
        assert metadata.size_bytes == 1024000
        assert metadata.file_count == 50
        assert metadata.checksum == "abc123def456"
        assert metadata.compression_ratio == 25.5
        assert metadata.status == "completed"
        assert metadata.backup_type == "manual"
        assert metadata.error_message is None
    
    def test_backup_metadata_with_error(self):
        """Testa criação de BackupMetadata com erro"""
        metadata = BackupMetadata(
            backup_id="failed_backup_20250127",
            timestamp="2025-01-27T10:30:00",
            size_bytes=0,
            file_count=0,
            checksum="",
            compression_ratio=0.0,
            status="failed",
            backup_type="manual",
            error_message="Disk space insufficient"
        )
        
        assert metadata.status == "failed"
        assert metadata.error_message == "Disk space insufficient"
        assert metadata.size_bytes == 0


class TestBackupService:
    """Testes para BackupService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def temp_backup_dir(self):
        """Diretório temporário para backups"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def backup_service(self, mock_db, temp_backup_dir):
        """Instância do BackupService para testes"""
        with patch('backend.app.services.backup_service.Path') as mock_path:
            mock_path.return_value = Path(temp_backup_dir)
            service = BackupService(mock_db)
            service.backup_dir = Path(temp_backup_dir)
            return service
    
    def test_backup_service_initialization(self, backup_service, mock_db):
        """Testa inicialização do BackupService"""
        assert backup_service.db == mock_db
        assert isinstance(backup_service.backup_dir, Path)
        assert isinstance(backup_service.config, dict)
        assert isinstance(backup_service.backup_history, list)
        assert backup_service.scheduler_thread is None
        assert backup_service.running is False
        
        # Verificar configurações padrão
        assert backup_service.config['retention_days'] == 30
        assert backup_service.config['compression_level'] == 9
        assert backup_service.config['max_backup_size_mb'] == 500
        assert backup_service.config['backup_schedule'] == '02:00'
        assert len(backup_service.config['critical_files']) > 0
        assert len(backup_service.config['exclude_patterns']) > 0
    
    def test_load_backup_history_existing(self, backup_service, temp_backup_dir):
        """Testa carregamento de histórico existente"""
        # Criar arquivo de metadados
        metadata_file = Path(temp_backup_dir) / 'backup_metadata.json'
        test_data = [
            {
                "backup_id": "test_backup_1",
                "timestamp": "2025-01-27T10:30:00",
                "size_bytes": 1024000,
                "file_count": 50,
                "checksum": "abc123",
                "compression_ratio": 25.5,
                "status": "completed",
                "backup_type": "manual"
            }
        ]
        
        with open(metadata_file, 'w') as f:
            json.dump(test_data, f)
        
        # Recarregar histórico
        backup_service._load_backup_history()
        
        assert len(backup_service.backup_history) == 1
        assert backup_service.backup_history[0].backup_id == "test_backup_1"
        assert backup_service.backup_history[0].status == "completed"
    
    def test_load_backup_history_nonexistent(self, backup_service):
        """Testa carregamento de histórico inexistente"""
        backup_service.backup_history = []
        backup_service._load_backup_history()
        
        assert len(backup_service.backup_history) == 0
    
    def test_save_backup_history(self, backup_service, temp_backup_dir):
        """Testa salvamento de histórico"""
        # Adicionar metadados de teste
        metadata = BackupMetadata(
            backup_id="test_backup_2",
            timestamp="2025-01-27T11:00:00",
            size_bytes=2048000,
            file_count=100,
            checksum="def456",
            compression_ratio=30.0,
            status="completed",
            backup_type="auto"
        )
        
        backup_service.backup_history.append(metadata)
        backup_service._save_backup_history()
        
        # Verificar se arquivo foi criado
        metadata_file = Path(temp_backup_dir) / 'backup_metadata.json'
        assert metadata_file.exists()
        
        # Verificar conteúdo
        with open(metadata_file, 'r') as f:
            saved_data = json.load(f)
        
        assert len(saved_data) == 1
        assert saved_data[0]['backup_id'] == "test_backup_2"
    
    def test_should_exclude(self, backup_service):
        """Testa verificação de exclusão de arquivos"""
        # Arquivos que devem ser excluídos
        assert backup_service._should_exclude("__pycache__/module.pyc") is True
        assert backup_service._should_exclude(".git/config") is True
        assert backup_service._should_exclude("node_modules/package.json") is True
        assert backup_service._should_exclude("file.tmp") is True
        assert backup_service._should_exclude("backups/backup.zip") is True
        
        # Arquivos que não devem ser excluídos
        assert backup_service._should_exclude("backend/app/main.py") is False
        assert backup_service._should_exclude("config.json") is False
        assert backup_service._should_exclude("docs/README.md") is False
    
    def test_get_files_to_backup(self, backup_service, temp_backup_dir):
        """Testa obtenção de arquivos para backup"""
        # Criar arquivos de teste
        test_files = [
            "backend/db.sqlite3",
            "backend/app/main.py",
            "config.json",
            "docs/README.md"
        ]
        
        for file_path in test_files:
            full_path = Path(temp_backup_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("test content")
        
        # Mock do método para usar diretório temporário
        with patch.object(backup_service, 'config') as mock_config:
            mock_config.__getitem__.side_effect = lambda key: {
                'critical_files': test_files,
                'exclude_patterns': ['__pycache__', '.git']
            }[key]
            
            files = backup_service._get_files_to_backup()
        
        # Verificar se arquivos foram encontrados
        assert len(files) >= len(test_files)
    
    def test_create_backup_filename(self, backup_service):
        """Testa criação de nome de arquivo de backup"""
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20250127T143000"
            
            filename = backup_service._create_backup_filename("manual")
            assert "backup_manual_20250127T143000.zip" in filename
            
            filename = backup_service._create_backup_filename("auto")
            assert "backup_auto_20250127T143000.zip" in filename
    
    def test_backup_database(self, backup_service, temp_backup_dir):
        """Testa backup do banco de dados"""
        # Criar banco SQLite de teste
        db_path = Path(temp_backup_dir) / "backend" / "db.sqlite3"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Criar banco SQLite simples
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES (?)", ("test",))
            conn.commit()
        
        # Mock do método para usar o banco de teste
        with patch.object(backup_service, 'config') as mock_config:
            mock_config.__getitem__.side_effect = lambda key: {
                'critical_files': [str(db_path)]
            }[key]
            
            result = backup_service._backup_database()
        
        assert result is True
        
        # Verificar se backup foi criado
        backup_path = Path(str(db_path) + ".backup")
        assert backup_path.exists()
    
    def test_compress_files(self, backup_service, temp_backup_dir):
        """Testa compressão de arquivos"""
        # Criar arquivos de teste
        test_files = []
        for i in range(3):
            file_path = Path(temp_backup_dir) / f"test_file_{i}.txt"
            file_path.write_text(f"Content of file {i} " * 100)  # Arquivo com conteúdo
            test_files.append(str(file_path))
        
        backup_path = Path(temp_backup_dir) / "test_backup.zip"
        
        total_size, compression_ratio = backup_service._compress_files(test_files, str(backup_path))
        
        assert backup_path.exists()
        assert total_size > 0
        assert compression_ratio >= 0
        assert compression_ratio <= 100
    
    def test_calculate_checksum(self, backup_service, temp_backup_dir):
        """Testa cálculo de checksum"""
        # Criar arquivo de teste
        test_file = Path(temp_backup_dir) / "test_file.txt"
        test_content = "This is test content for checksum calculation"
        test_file.write_text(test_content)
        
        checksum = backup_service._calculate_checksum(str(test_file))
        
        # Verificar se checksum é uma string hexadecimal válida
        assert isinstance(checksum, str)
        assert len(checksum) == 32  # MD5 hash length
        assert all(c in '0123456789abcdef' for c in checksum)
    
    def test_validate_backup_integrity_valid(self, backup_service, temp_backup_dir):
        """Testa validação de integridade de backup válido"""
        # Criar arquivo de backup de teste
        backup_path = Path(temp_backup_dir) / "test_backup.zip"
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            zipf.writestr("test.txt", "test content")
        
        metadata = BackupMetadata(
            backup_id="test_backup",
            timestamp="2025-01-27T10:30:00",
            size_bytes=backup_path.stat().st_size,
            file_count=1,
            checksum=backup_service._calculate_checksum(str(backup_path)),
            compression_ratio=10.0,
            status="completed",
            backup_type="manual"
        )
        
        result = backup_service._validate_backup_integrity(str(backup_path), metadata)
        assert result is True
    
    def test_validate_backup_integrity_invalid_size(self, backup_service, temp_backup_dir):
        """Testa validação de integridade com tamanho incorreto"""
        backup_path = Path(temp_backup_dir) / "test_backup.zip"
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            zipf.writestr("test.txt", "test content")
        
        metadata = BackupMetadata(
            backup_id="test_backup",
            timestamp="2025-01-27T10:30:00",
            size_bytes=999999,  # Tamanho incorreto
            file_count=1,
            checksum="abc123",
            compression_ratio=10.0,
            status="completed",
            backup_type="manual"
        )
        
        result = backup_service._validate_backup_integrity(str(backup_path), metadata)
        assert result is False
    
    def test_validate_backup_integrity_invalid_checksum(self, backup_service, temp_backup_dir):
        """Testa validação de integridade com checksum incorreto"""
        backup_path = Path(temp_backup_dir) / "test_backup.zip"
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            zipf.writestr("test.txt", "test content")
        
        metadata = BackupMetadata(
            backup_id="test_backup",
            timestamp="2025-01-27T10:30:00",
            size_bytes=backup_path.stat().st_size,
            file_count=1,
            checksum="invalid_checksum",  # Checksum incorreto
            compression_ratio=10.0,
            status="completed",
            backup_type="manual"
        )
        
        result = backup_service._validate_backup_integrity(str(backup_path), metadata)
        assert result is False
    
    def test_create_backup_success(self, backup_service, temp_backup_dir):
        """Testa criação de backup bem-sucedida"""
        # Criar arquivos de teste
        test_files = [
            "backend/app/main.py",
            "config.json",
            "docs/README.md"
        ]
        
        for file_path in test_files:
            full_path = Path(temp_backup_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("test content")
        
        # Mock de métodos dependentes
        with patch.object(backup_service, '_get_files_to_backup', return_value=[str(Path(temp_backup_dir) / f) for f in test_files]):
            with patch.object(backup_service, '_backup_database', return_value=True):
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.free = 1024 * 1024 * 1024  # 1GB livre
                    
                    metadata = backup_service.create_backup("manual")
        
        assert metadata is not None
        assert metadata.status == "completed"
        assert metadata.backup_type == "manual"
        assert metadata.size_bytes > 0
        assert metadata.file_count > 0
        assert metadata.checksum != ""
    
    def test_create_backup_insufficient_space(self, backup_service):
        """Testa criação de backup com espaço insuficiente"""
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk.return_value.free = 1024 * 1024  # 1MB livre (insuficiente)
            
            metadata = backup_service.create_backup("manual")
        
        assert metadata is not None
        assert metadata.status == "failed"
        assert "Espaço insuficiente" in metadata.error_message
    
    def test_create_backup_no_files(self, backup_service):
        """Testa criação de backup sem arquivos"""
        with patch.object(backup_service, '_get_files_to_backup', return_value=[]):
            with patch('psutil.disk_usage') as mock_disk:
                mock_disk.return_value.free = 1024 * 1024 * 1024
                
                metadata = backup_service.create_backup("manual")
        
        assert metadata is not None
        assert metadata.status == "failed"
        assert "Nenhum arquivo encontrado" in metadata.error_message
    
    def test_create_backup_database_failure(self, backup_service, temp_backup_dir):
        """Testa criação de backup com falha no banco"""
        # Criar arquivos de teste
        test_file = Path(temp_backup_dir) / "test.txt"
        test_file.write_text("test content")
        
        with patch.object(backup_service, '_get_files_to_backup', return_value=[str(test_file)]):
            with patch.object(backup_service, '_backup_database', return_value=False):
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.free = 1024 * 1024 * 1024
                    
                    metadata = backup_service.create_backup("manual")
        
        assert metadata is not None
        assert metadata.status == "failed"
        assert "Falha no backup do banco" in metadata.error_message
    
    def test_cleanup_old_backups(self, backup_service, temp_backup_dir):
        """Testa limpeza de backups antigos"""
        # Criar backups de teste com diferentes idades
        old_backup = Path(temp_backup_dir) / "backup_old_20240101.zip"
        new_backup = Path(temp_backup_dir) / "backup_new_20250127.zip"
        
        old_backup.write_text("old backup content")
        new_backup.write_text("new backup content")
        
        # Mock de tempo para simular backup antigo
        old_time = datetime.now() - timedelta(days=60)
        new_time = datetime.now()
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromtimestamp.side_effect = lambda ts: old_time if "old" in str(ts) else new_time
            
            backup_service._cleanup_old_backups()
        
        # Verificar se backup antigo foi removido
        assert not old_backup.exists()
        assert new_backup.exists()
    
    def test_restore_backup_success(self, backup_service, temp_backup_dir):
        """Testa restauração de backup bem-sucedida"""
        # Criar backup de teste
        backup_path = Path(temp_backup_dir) / "test_backup.zip"
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            zipf.writestr("test.txt", "restored content")
        
        # Criar metadados válidos
        metadata = BackupMetadata(
            backup_id="test_backup",
            timestamp="2025-01-27T10:30:00",
            size_bytes=backup_path.stat().st_size,
            file_count=1,
            checksum=backup_service._calculate_checksum(str(backup_path)),
            compression_ratio=10.0,
            status="completed",
            backup_type="manual"
        )
        
        backup_service.backup_history.append(metadata)
        
        # Mock de métodos dependentes
        with patch.object(backup_service, '_validate_backup_integrity', return_value=True):
            with patch.object(backup_service, 'create_backup') as mock_create:
                mock_create.return_value = BackupMetadata(
                    backup_id="pre_restore",
                    timestamp="2025-01-27T10:30:00",
                    size_bytes=1000,
                    file_count=1,
                    checksum="abc123",
                    compression_ratio=10.0,
                    status="completed",
                    backup_type="pre_restore"
                )
                
                result = backup_service.restore_backup("test_backup.zip", temp_backup_dir)
        
        assert result is True
        
        # Verificar se arquivo foi restaurado
        restored_file = Path(temp_backup_dir) / "test.txt"
        assert restored_file.exists()
        assert restored_file.read_text() == "restored content"
    
    def test_restore_backup_not_found(self, backup_service):
        """Testa restauração de backup inexistente"""
        result = backup_service.restore_backup("nonexistent_backup.zip")
        assert result is False
    
    def test_restore_backup_corrupted(self, backup_service, temp_backup_dir):
        """Testa restauração de backup corrompido"""
        # Criar backup de teste
        backup_path = Path(temp_backup_dir) / "corrupted_backup.zip"
        backup_path.write_text("corrupted content")
        
        # Criar metadados
        metadata = BackupMetadata(
            backup_id="corrupted_backup",
            timestamp="2025-01-27T10:30:00",
            size_bytes=1000,
            file_count=1,
            checksum="abc123",
            compression_ratio=10.0,
            status="completed",
            backup_type="manual"
        )
        
        backup_service.backup_history.append(metadata)
        
        with patch.object(backup_service, '_validate_backup_integrity', return_value=False):
            result = backup_service.restore_backup("corrupted_backup.zip")
        
        assert result is False
    
    def test_list_backups(self, backup_service, temp_backup_dir):
        """Testa listagem de backups"""
        # Criar backups de teste
        backup_files = [
            "backup_manual_20250127.zip",
            "backup_auto_20250126.zip"
        ]
        
        for filename in backup_files:
            backup_path = Path(temp_backup_dir) / filename
            backup_path.write_text("backup content")
        
        # Criar metadados
        metadata = BackupMetadata(
            backup_id="backup_manual_20250127",
            timestamp="2025-01-27T10:30:00",
            size_bytes=1000,
            file_count=5,
            checksum="abc123",
            compression_ratio=25.0,
            status="completed",
            backup_type="manual"
        )
        
        backup_service.backup_history.append(metadata)
        
        backups = backup_service.list_backups()
        
        assert len(backups) == 2
        assert any(b['filename'] == "backup_manual_20250127.zip" for b in backups)
        assert any(b['filename'] == "backup_auto_20250126.zip" for b in backups)
    
    def test_get_backup_statistics(self, backup_service):
        """Testa obtenção de estatísticas de backup"""
        # Adicionar backups de teste
        successful_backup = BackupMetadata(
            backup_id="success_1",
            timestamp="2025-01-27T10:30:00",
            size_bytes=1024000,
            file_count=50,
            checksum="abc123",
            compression_ratio=25.0,
            status="completed",
            backup_type="manual"
        )
        
        failed_backup = BackupMetadata(
            backup_id="failed_1",
            timestamp="2025-01-27T11:00:00",
            size_bytes=0,
            file_count=0,
            checksum="",
            compression_ratio=0.0,
            status="failed",
            backup_type="manual",
            error_message="Test error"
        )
        
        backup_service.backup_history.extend([successful_backup, failed_backup])
        
        stats = backup_service.get_backup_statistics()
        
        assert stats["total_backups"] == 2
        assert stats["successful_backups"] == 1
        assert stats["failed_backups"] == 1
        assert stats["success_rate"] == 0.5
        assert stats["total_size_mb"] > 0
        assert stats["average_compression_ratio"] > 0
        assert stats["daemon_running"] is False
    
    def test_log_backup_operation(self, backup_service, mock_db):
        """Testa registro de log de operação de backup"""
        metadata = BackupMetadata(
            backup_id="test_backup",
            timestamp="2025-01-27T10:30:00",
            size_bytes=1024000,
            file_count=50,
            checksum="abc123",
            compression_ratio=25.0,
            status="completed",
            backup_type="manual"
        )
        
        backup_service._log_backup_operation("create", metadata)
        
        # Verificar se log foi adicionado ao banco
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Verificar se o log adicionado é do tipo correto
        log_entry = mock_db.add.call_args[0][0]
        assert isinstance(log_entry, LogOperacao)
        assert log_entry.operacao == "backup_create"
        assert "test_backup" in log_entry.detalhes


class TestBackupServiceIntegration:
    """Testes de integração para BackupService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def temp_backup_dir(self):
        """Diretório temporário para backups"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def backup_service(self, mock_db, temp_backup_dir):
        """Instância do BackupService para testes"""
        with patch('backend.app.services.backup_service.Path') as mock_path:
            mock_path.return_value = Path(temp_backup_dir)
            service = BackupService(mock_db)
            service.backup_dir = Path(temp_backup_dir)
            return service
    
    def test_full_backup_restore_cycle(self, backup_service, temp_backup_dir):
        """Testa ciclo completo de backup e restauração"""
        # Criar arquivos de teste
        test_files = [
            "backend/app/main.py",
            "config.json",
            "docs/README.md"
        ]
        
        for file_path in test_files:
            full_path = Path(temp_backup_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"Content of {file_path}")
        
        # Mock de métodos dependentes
        with patch.object(backup_service, '_get_files_to_backup', return_value=[str(Path(temp_backup_dir) / f) for f in test_files]):
            with patch.object(backup_service, '_backup_database', return_value=True):
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.free = 1024 * 1024 * 1024
                    
                    # Criar backup
                    metadata = backup_service.create_backup("manual")
        
        assert metadata.status == "completed"
        
        # Listar backups
        backups = backup_service.list_backups()
        assert len(backups) == 1
        
        # Restaurar backup
        backup_filename = backups[0]['filename']
        restore_dir = Path(temp_backup_dir) / "restore"
        restore_dir.mkdir()
        
        with patch.object(backup_service, '_validate_backup_integrity', return_value=True):
            with patch.object(backup_service, 'create_backup') as mock_create:
                mock_create.return_value = BackupMetadata(
                    backup_id="pre_restore",
                    timestamp="2025-01-27T10:30:00",
                    size_bytes=1000,
                    file_count=1,
                    checksum="abc123",
                    compression_ratio=10.0,
                    status="completed",
                    backup_type="pre_restore"
                )
                
                result = backup_service.restore_backup(backup_filename, str(restore_dir))
        
        assert result is True
        
        # Verificar se arquivos foram restaurados
        for file_path in test_files:
            restored_file = restore_dir / file_path
            assert restored_file.exists()
            assert restored_file.read_text() == f"Content of {file_path}"


class TestBackupServiceErrorHandling:
    """Testes de tratamento de erros para BackupService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def backup_service(self, mock_db):
        """Instância do BackupService para testes"""
        return BackupService(mock_db)
    
    def test_database_error_handling(self, backup_service, mock_db):
        """Testa tratamento de erro de banco de dados"""
        # Simular erro de banco
        mock_db.add.side_effect = Exception("Database error")
        
        metadata = BackupMetadata(
            backup_id="test_backup",
            timestamp="2025-01-27T10:30:00",
            size_bytes=1000,
            file_count=1,
            checksum="abc123",
            compression_ratio=10.0,
            status="completed",
            backup_type="manual"
        )
        
        # Deve continuar funcionando sem quebrar
        backup_service._log_backup_operation("test", metadata)
        
        # Verificar se o erro foi tratado graciosamente
        assert True  # Se chegou aqui, não quebrou
    
    def test_file_operation_error_handling(self, backup_service):
        """Testa tratamento de erro em operações de arquivo"""
        # Testar com arquivo inexistente
        result = backup_service._calculate_checksum("nonexistent_file.txt")
        
        # Deve levantar exceção
        with pytest.raises(FileNotFoundError):
            backup_service._calculate_checksum("nonexistent_file.txt")


class TestBackupServicePerformance:
    """Testes de performance para BackupService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def temp_backup_dir(self):
        """Diretório temporário para backups"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def backup_service(self, mock_db, temp_backup_dir):
        """Instância do BackupService para testes"""
        with patch('backend.app.services.backup_service.Path') as mock_path:
            mock_path.return_value = Path(temp_backup_dir)
            service = BackupService(mock_db)
            service.backup_dir = Path(temp_backup_dir)
            return service
    
    def test_multiple_backups_performance(self, backup_service, temp_backup_dir):
        """Testa performance de múltiplos backups"""
        import time
        
        # Criar arquivos de teste
        test_files = []
        for i in range(10):
            file_path = Path(temp_backup_dir) / f"test_file_{i}.txt"
            file_path.write_text(f"Content of file {i} " * 100)
            test_files.append(str(file_path))
        
        start_time = time.time()
        
        # Criar múltiplos backups
        for i in range(5):
            with patch.object(backup_service, '_get_files_to_backup', return_value=test_files):
                with patch.object(backup_service, '_backup_database', return_value=True):
                    with patch('psutil.disk_usage') as mock_disk:
                        mock_disk.return_value.free = 1024 * 1024 * 1024
                        
                        metadata = backup_service.create_backup(f"test_{i}")
                        assert metadata.status == "completed"
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 30.0  # Menos de 30 segundos para 5 backups
        
        # Verificar se backups foram criados
        backup_files = list(Path(temp_backup_dir).glob("backup_*.zip"))
        assert len(backup_files) == 5


if __name__ == "__main__":
    pytest.main([__file__]) 