from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Backup Inteligente

Autor: Sistema de Testes
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: TEST_BACKUP_INTELIGENTE_001
"""

import pytest
import tempfile
import shutil
import os
import json
import zipfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Importar módulos a serem testados
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from infrastructure.backup.inteligente.backup_manager import (
    BackupInteligenteManager,
    BackupType,
    BackupStatus,
    BackupMetadata,
    ChangeDetector,
    EncryptionManager,
    CloudStorageManager,
    FileChangeInfo
)

class TestBackupType:
    """Testes para enum BackupType"""
    
    def test_backup_type_values(self):
        """Testa valores do enum BackupType"""
        assert BackupType.FULL.value == "full"
        assert BackupType.INCREMENTAL.value == "incremental"
        assert BackupType.DIFFERENTIAL.value == "differential"

class TestBackupStatus:
    """Testes para enum BackupStatus"""
    
    def test_backup_status_values(self):
        """Testa valores do enum BackupStatus"""
        assert BackupStatus.PENDING.value == "pending"
        assert BackupStatus.IN_PROGRESS.value == "in_progress"
        assert BackupStatus.COMPLETED.value == "completed"
        assert BackupStatus.FAILED.value == "failed"
        assert BackupStatus.VALIDATED.value == "validated"
        assert BackupStatus.UPLOADED.value == "uploaded"

class TestBackupMetadata:
    """Testes para classe BackupMetadata"""
    
    def test_backup_metadata_creation(self):
        """Testa criação de BackupMetadata"""
        metadata = BackupMetadata(
            backup_id="test_001",
            timestamp="2024-12-19T12:00:00",
            backup_type=BackupType.FULL,
            size_bytes=1024,
            compressed_size_bytes=512,
            file_count=10,
            checksum="abc123",
            compression_ratio=50.0,
            encryption_key_id="key_001",
            status=BackupStatus.COMPLETED
        )
        
        assert metadata.backup_id == "test_001"
        assert metadata.backup_type == BackupType.FULL
        assert metadata.status == BackupStatus.COMPLETED
        assert metadata.compression_ratio == 50.0
    
    def test_backup_metadata_to_dict(self):
        """Testa conversão para dicionário"""
        metadata = BackupMetadata(
            backup_id="test_002",
            timestamp="2024-12-19T12:00:00",
            backup_type=BackupType.INCREMENTAL,
            size_bytes=2048,
            compressed_size_bytes=1024,
            file_count=5,
            checksum="def456",
            compression_ratio=50.0,
            encryption_key_id=None,
            status=BackupStatus.COMPLETED
        )
        
        data = metadata.to_dict()
        assert data['backup_id'] == "test_002"
        assert data['backup_type'] == "incremental"
        assert data['status'] == "completed"
        assert data['encryption_key_id'] is None

class TestFileChangeInfo:
    """Testes para classe FileChangeInfo"""
    
    def test_file_change_info_creation(self):
        """Testa criação de FileChangeInfo"""
        change_info = FileChangeInfo(
            file_path="/test/file.txt",
            last_modified=1640995200.0,
            size=1024,
            checksum="abc123",
            change_type="modified"
        )
        
        assert change_info.file_path == "/test/file.txt"
        assert change_info.change_type == "modified"
        assert change_info.size == 1024

class TestChangeDetector:
    """Testes para classe ChangeDetector"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_change_detector_initialization(self, temp_dir):
        """Testa inicialização do ChangeDetector"""
        state_file = os.path.join(temp_dir, "backup_state.json")
        detector = ChangeDetector(state_file)
        
        assert detector.state_file == Path(state_file)
        assert detector.file_states == {}
    
    def test_detect_changes_new_file(self, temp_dir):
        """Testa detecção de arquivo novo"""
        # Criar arquivo de teste
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        detector = ChangeDetector()
        changes = detector.detect_changes([test_file])
        
        assert len(changes) == 1
        assert changes[0].file_path == test_file
        assert changes[0].change_type == "added"
    
    def test_detect_changes_modified_file(self, temp_dir):
        """Testa detecção de arquivo modificado"""
        # Criar arquivo inicial
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("initial content")
        
        detector = ChangeDetector()
        
        # Primeira detecção
        changes1 = detector.detect_changes([test_file])
        assert len(changes1) == 1
        assert changes1[0].change_type == "added"
        
        # Modificar arquivo
        with open(test_file, 'w') as f:
            f.write("modified content")
        
        # Segunda detecção
        changes2 = detector.detect_changes([test_file])
        assert len(changes2) == 1
        assert changes2[0].change_type == "modified"
    
    def test_detect_changes_deleted_file(self, temp_dir):
        """Testa detecção de arquivo deletado"""
        # Criar arquivo inicial
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("content")
        
        detector = ChangeDetector()
        
        # Primeira detecção
        detector.detect_changes([test_file])
        
        # Deletar arquivo
        os.remove(test_file)
        
        # Segunda detecção
        changes = detector.detect_changes([test_file])
        assert len(changes) == 1
        assert changes[0].change_type == "deleted"
    
    def test_save_and_load_state(self, temp_dir):
        """Testa salvamento e carregamento do estado"""
        state_file = os.path.join(temp_dir, "backup_state.json")
        detector = ChangeDetector(state_file)
        
        # Criar arquivo e detectar mudanças
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("content")
        
        detector.detect_changes([test_file])
        
        # Verificar se estado foi salvo
        assert os.path.exists(state_file)
        
        # Criar novo detector e carregar estado
        detector2 = ChangeDetector(state_file)
        assert len(detector2.file_states) > 0

class TestEncryptionManager:
    """Testes para classe EncryptionManager"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @patch('infrastructure.backup.inteligente.backup_manager.CRYPTOGRAPHY_AVAILABLE', True)
    @patch('infrastructure.backup.inteligente.backup_manager.Fernet')
    def test_encryption_manager_initialization(self, mock_fernet, temp_dir):
        """Testa inicialização do EncryptionManager"""
        key_file = os.path.join(temp_dir, "backup_encryption.key")
        
        # Mock da geração de chave
        mock_key = b"test_key_32_bytes_long_key_here"
        mock_fernet.generate_key.return_value = mock_key
        
        # Mock do cipher
        mock_cipher = Mock()
        mock_fernet.return_value = mock_cipher
        
        manager = EncryptionManager()
        
        # Verificar se chave foi gerada
        assert manager.key == mock_key
        assert manager.cipher == mock_cipher
    
    @patch('infrastructure.backup.inteligente.backup_manager.CRYPTOGRAPHY_AVAILABLE', False)
    def test_encryption_manager_no_cryptography(self):
        """Testa inicialização sem cryptography disponível"""
        manager = EncryptionManager()
        
        assert manager.key is None
        assert manager.cipher is None
    
    @patch('infrastructure.backup.inteligente.backup_manager.CRYPTOGRAPHY_AVAILABLE', True)
    @patch('infrastructure.backup.inteligente.backup_manager.Fernet')
    def test_encrypt_file(self, mock_fernet, temp_dir):
        """Testa criptografia de arquivo"""
        # Criar arquivo de teste
        input_file = os.path.join(temp_dir, "input.txt")
        output_file = os.path.join(temp_dir, "output.enc")
        
        with open(input_file, 'w') as f:
            f.write("test content")
        
        # Mock do cipher
        mock_cipher = Mock()
        mock_cipher.encrypt.return_value = b"encrypted_data"
        mock_fernet.return_value = mock_cipher
        
        manager = EncryptionManager()
        manager.cipher = mock_cipher
        
        result = manager.encrypt_file(input_file, output_file)
        
        assert result is True
        assert os.path.exists(output_file)
        mock_cipher.encrypt.assert_called_once()
    
    @patch('infrastructure.backup.inteligente.backup_manager.CRYPTOGRAPHY_AVAILABLE', True)
    @patch('infrastructure.backup.inteligente.backup_manager.Fernet')
    def test_decrypt_file(self, mock_fernet, temp_dir):
        """Testa descriptografia de arquivo"""
        # Criar arquivo criptografado de teste
        input_file = os.path.join(temp_dir, "input.enc")
        output_file = os.path.join(temp_dir, "output.txt")
        
        with open(input_file, 'wb') as f:
            f.write(b"encrypted_data")
        
        # Mock do cipher
        mock_cipher = Mock()
        mock_cipher.decrypt.return_value = b"decrypted_data"
        mock_fernet.return_value = mock_cipher
        
        manager = EncryptionManager()
        manager.cipher = mock_cipher
        
        result = manager.decrypt_file(input_file, output_file)
        
        assert result is True
        assert os.path.exists(output_file)
        mock_cipher.decrypt.assert_called_once()

class TestCloudStorageManager:
    """Testes para classe CloudStorageManager"""
    
    def test_cloud_storage_manager_initialization(self):
        """Testa inicialização do CloudStorageManager"""
        manager = CloudStorageManager()
        
        assert manager.s3_client is None
        assert manager.gcs_client is None
    
    @patch('infrastructure.backup.inteligente.backup_manager.BOTO3_AVAILABLE', True)
    @patch('infrastructure.backup.inteligente.backup_manager.boto3')
    @patch.dict(os.environ, {'AWS_ACCESS_KEY_ID': 'test_key'})
    def test_initialize_s3_client(self, mock_boto3):
        """Testa inicialização do cliente S3"""
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client
        
        manager = CloudStorageManager()
        
        assert manager.s3_client == mock_client
        mock_boto3.client.assert_called_once_with('s3')
    
    @patch('infrastructure.backup.inteligente.backup_manager.GCS_AVAILABLE', True)
    @patch('infrastructure.backup.inteligente.backup_manager.storage')
    @patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': 'test_creds'})
    def test_initialize_gcs_client(self, mock_storage):
        """Testa inicialização do cliente GCS"""
        mock_client = Mock()
        mock_storage.Client.return_value = mock_client
        
        manager = CloudStorageManager()
        
        assert manager.gcs_client == mock_client
        mock_storage.Client.assert_called_once()
    
    def test_upload_to_s3_no_client(self):
        """Testa upload S3 sem cliente inicializado"""
        manager = CloudStorageManager()
        result = manager.upload_to_s3("test_file", "test_bucket", "test_key")
        
        assert result is False
    
    def test_upload_to_gcs_no_client(self):
        """Testa upload GCS sem cliente inicializado"""
        manager = CloudStorageManager()
        result = manager.upload_to_gcs("test_file", "test_bucket", "test_blob")
        
        assert result is False
    
    def test_sync_backup_to_cloud_no_clients(self):
        """Testa sincronização sem clientes de nuvem"""
        manager = CloudStorageManager()
        results = manager.sync_backup_to_cloud("test_backup", "test_id")
        
        assert results == {}

class TestBackupInteligenteManager:
    """Testes para classe BackupInteligenteManager"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def backup_manager(self, temp_dir):
        """Cria instância do BackupInteligenteManager para testes"""
        # Mock do diretório de backup
        with patch('infrastructure.backup.inteligente.backup_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = BackupInteligenteManager()
            manager.backup_dir = Path(temp_dir)
            return manager
    
    def test_backup_manager_initialization(self, temp_dir):
        """Testa inicialização do BackupInteligenteManager"""
        with patch('infrastructure.backup.inteligente.backup_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = BackupInteligenteManager()
            
            assert manager.backup_dir == mock_backup_dir
            assert isinstance(manager.backup_history, list)
    
    def test_should_exclude(self, backup_manager):
        """Testa função should_exclude"""
        # Arquivo que deve ser excluído
        assert backup_manager._should_exclude("__pycache__/file.py") is True
        assert backup_manager._should_exclude(".git/config") is True
        assert backup_manager._should_exclude("node_modules/package.json") is True
        
        # Arquivo que não deve ser excluído
        assert backup_manager._should_exclude("backend/app.py") is False
        assert backup_manager._should_exclude("logs/app.log") is False
    
    def test_create_backup_filename(self, backup_manager):
        """Testa criação de nome de arquivo de backup"""
        filename = backup_manager._create_backup_filename(BackupType.FULL)
        
        assert filename.startswith("backup_full_")
        assert filename.endswith(".zip")
        
        filename = backup_manager._create_backup_filename(BackupType.INCREMENTAL)
        assert filename.startswith("backup_incremental_")
    
    def test_should_create_full_backup_no_history(self, backup_manager):
        """Testa decisão de backup completo sem histórico"""
        result = backup_manager._should_create_full_backup()
        assert result is True
    
    def test_should_create_full_backup_with_history(self, backup_manager):
        """Testa decisão de backup completo com histórico"""
        # Adicionar backup completo recente
        recent_backup = BackupMetadata(
            backup_id="recent_001",
            timestamp=datetime.now().isoformat(),
            backup_type=BackupType.FULL,
            size_bytes=1024,
            compressed_size_bytes=512,
            file_count=10,
            checksum="abc123",
            compression_ratio=50.0,
            encryption_key_id=None,
            status=BackupStatus.COMPLETED
        )
        backup_manager.backup_history.append(recent_backup)
        
        result = backup_manager._should_create_full_backup()
        assert result is False
    
    def test_compress_files_intelligent(self, backup_manager, temp_dir):
        """Testa compressão inteligente de arquivos"""
        # Criar arquivos de teste
        test_files = []
        for index in range(3):
            test_file = os.path.join(temp_dir, f"test_{index}.txt")
            with open(test_file, 'w') as f:
                f.write(f"test content {index}" * 100)  # Conteúdo repetitivo para compressão
            test_files.append(test_file)
        
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        
        total_size, compression_ratio = backup_manager._compress_files_intelligent(
            test_files, backup_path
        )
        
        assert total_size > 0
        assert compression_ratio >= 0
        assert os.path.exists(backup_path)
        
        # Verificar se é um ZIP válido
        with zipfile.ZipFile(backup_path, 'r') as zip_file:
            assert len(zip_file.namelist()) == 3
    
    def test_calculate_checksum(self, backup_manager, temp_dir):
        """Testa cálculo de checksum"""
        # Criar arquivo de teste
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        checksum = backup_manager._calculate_checksum(Path(test_file))
        
        assert len(checksum) == 64  # SHA-256 tem 64 caracteres hex
        assert isinstance(checksum, str)
    
    def test_validate_backup_success(self, backup_manager, temp_dir):
        """Testa validação de backup bem-sucedida"""
        # Criar backup de teste
        backup_file = os.path.join(temp_dir, "test_backup.zip")
        with zipfile.ZipFile(backup_file, 'w') as zip_file:
            zip_file.writestr("test.txt", "test content")
        
        # Criar metadados de teste
        metadata = BackupMetadata(
            backup_id="test_001",
            timestamp=datetime.now().isoformat(),
            backup_type=BackupType.FULL,
            size_bytes=1024,
            compressed_size_bytes=os.path.getsize(backup_file),
            file_count=1,
            checksum=backup_manager._calculate_checksum(Path(backup_file)),
            compression_ratio=50.0,
            encryption_key_id=None,
            status=BackupStatus.COMPLETED
        )
        backup_manager.backup_history.append(metadata)
        
        result = backup_manager.validate_backup("test_001")
        assert result is True
    
    def test_validate_backup_not_found(self, backup_manager):
        """Testa validação de backup não encontrado"""
        result = backup_manager.validate_backup("nonexistent")
        assert result is False
    
    def test_list_backups(self, backup_manager):
        """Testa listagem de backups"""
        # Adicionar backups de teste
        backup1 = BackupMetadata(
            backup_id="test_001",
            timestamp="2024-12-19T12:00:00",
            backup_type=BackupType.FULL,
            size_bytes=1024,
            compressed_size_bytes=512,
            file_count=10,
            checksum="abc123",
            compression_ratio=50.0,
            encryption_key_id=None,
            status=BackupStatus.COMPLETED
        )
        backup_manager.backup_history.append(backup1)
        
        backups = backup_manager.list_backups()
        
        assert len(backups) == 1
        assert backups[0]['id'] == "test_001"
        assert backups[0]['type'] == "full"
        assert backups[0]['status'] == "completed"
    
    def test_get_backup_stats(self, backup_manager):
        """Testa obtenção de estatísticas de backup"""
        # Adicionar backups de teste
        backup1 = BackupMetadata(
            backup_id="test_001",
            timestamp="2024-12-19T12:00:00",
            backup_type=BackupType.FULL,
            size_bytes=1024,
            compressed_size_bytes=512,
            file_count=10,
            checksum="abc123",
            compression_ratio=50.0,
            encryption_key_id=None,
            status=BackupStatus.COMPLETED
        )
        backup2 = BackupMetadata(
            backup_id="test_002",
            timestamp="2024-12-19T13:00:00",
            backup_type=BackupType.INCREMENTAL,
            size_bytes=2048,
            compressed_size_bytes=1024,
            file_count=5,
            checksum="def456",
            compression_ratio=50.0,
            encryption_key_id=None,
            status=BackupStatus.FAILED
        )
        backup_manager.backup_history.extend([backup1, backup2])
        
        stats = backup_manager.get_backup_stats()
        
        assert stats['total_backups'] == 2
        assert stats['successful_backups'] == 1
        assert stats['success_rate'] == "50.0%"
        assert stats['total_size_gb'] > 0

class TestIntegration:
    """Testes de integração"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_backup_workflow(self, temp_dir):
        """Testa workflow completo de backup"""
        # Criar estrutura de arquivos de teste
        test_structure = {
            'backend': {
                'app.py': 'print("Hello World")',
                'config.py': 'DEBUG = True'
            },
            'logs': {
                'app.log': '2024-12-19 INFO: Application started'
            },
            'blogs': {
                'post1.txt': 'Blog post content 1',
                'post2.txt': 'Blog post content 2'
            }
        }
        
        # Criar arquivos
        for dir_path, files in test_structure.items():
            os.makedirs(os.path.join(temp_dir, dir_path), exist_ok=True)
            for filename, content in files.items():
                file_path = os.path.join(temp_dir, dir_path, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
        
        # Mock do diretório de backup
        with patch('infrastructure.backup.inteligente.backup_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = BackupInteligenteManager()
            manager.backup_dir = Path(temp_dir)
            
            # Mock das configurações para incluir arquivos de teste
            manager._get_files_to_backup = lambda: [
                os.path.join(temp_dir, 'backend', 'app.py'),
                os.path.join(temp_dir, 'backend', 'config.py'),
                os.path.join(temp_dir, 'logs', 'app.log'),
                os.path.join(temp_dir, 'blogs', 'post1.txt'),
                os.path.join(temp_dir, 'blogs', 'post2.txt')
            ]
            
            # Executar backup
            backup = manager.create_backup(BackupType.FULL)
            
            assert backup is not None
            assert backup.backup_type == BackupType.FULL
            assert backup.status == BackupStatus.COMPLETED
            assert backup.file_count == 5
            assert backup.size_bytes > 0
            assert backup.compression_ratio >= 0
    
    def test_incremental_backup_workflow(self, temp_dir):
        """Testa workflow de backup incremental"""
        # Criar arquivo inicial
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("initial content")
        
        with patch('infrastructure.backup.inteligente.backup_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = BackupInteligenteManager()
            manager.backup_dir = Path(temp_dir)
            
            # Mock das configurações
            manager._get_files_to_backup = lambda: [test_file]
            
            # Primeiro backup (completo)
            backup1 = manager.create_backup(BackupType.FULL)
            assert backup1 is not None
            assert backup1.backup_type == BackupType.FULL
            
            # Modificar arquivo
            with open(test_file, 'w') as f:
                f.write("modified content")
            
            # Segundo backup (incremental)
            backup2 = manager.create_backup(BackupType.INCREMENTAL)
            assert backup2 is not None
            assert backup2.backup_type == BackupType.INCREMENTAL

def main():
    """Função principal para execução dos testes"""
    print("Executando testes do sistema de backup inteligente...")
    
    # Executar testes específicos
    test_classes = [
        TestBackupType,
        TestBackupStatus,
        TestBackupMetadata,
        TestFileChangeInfo,
        TestChangeDetector,
        TestEncryptionManager,
        TestCloudStorageManager,
        TestBackupInteligenteManager,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\nTestando {test_class.__name__}...")
        
        # Executar métodos de teste da classe
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    # Criar instância e executar teste
                    test_instance = test_class()
                    test_method = getattr(test_instance, method_name)
                    test_method()
                    print(f"  ✅ {method_name}")
                    passed_tests += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {e}")
    
    print(f"\nResultado: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️ Alguns testes falharam")

if __name__ == "__main__":
    main() 