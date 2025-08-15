from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Restore Inteligente

Autor: Sistema de Testes
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: TEST_RESTORE_INTELIGENTE_001
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

from infrastructure.backup.inteligente.restore_manager import (
    RestoreInteligenteManager,
    RestoreType,
    RestoreStatus,
    RestoreMetadata,
    RestoreValidator,
    RestoreValidationResult
)

class TestRestoreType:
    """Testes para enum RestoreType"""
    
    def test_restore_type_values(self):
        """Testa valores do enum RestoreType"""
        assert RestoreType.FULL.value == "full"
        assert RestoreType.SELECTIVE.value == "selective"
        assert RestoreType.INCREMENTAL.value == "incremental"
        assert RestoreType.CLOUD.value == "cloud"

class TestRestoreStatus:
    """Testes para enum RestoreStatus"""
    
    def test_restore_status_values(self):
        """Testa valores do enum RestoreStatus"""
        assert RestoreStatus.PENDING.value == "pending"
        assert RestoreStatus.IN_PROGRESS.value == "in_progress"
        assert RestoreStatus.VALIDATING.value == "validating"
        assert RestoreStatus.DECRYPTING.value == "decrypting"
        assert RestoreStatus.EXTRACTING.value == "extracting"
        assert RestoreStatus.COMPLETED.value == "completed"
        assert RestoreStatus.FAILED.value == "failed"
        assert RestoreStatus.ROLLED_BACK.value == "rolled_back"

class TestRestoreMetadata:
    """Testes para classe RestoreMetadata"""
    
    def test_restore_metadata_creation(self):
        """Testa criação de RestoreMetadata"""
        metadata = RestoreMetadata(
            restore_id="restore_001",
            backup_id="backup_001",
            timestamp="2024-12-19T12:00:00",
            restore_type=RestoreType.FULL,
            target_path="/restore/path",
            status=RestoreStatus.COMPLETED,
            files_restored=10,
            total_size_bytes=1024,
            duration_seconds=5.5
        )
        
        assert metadata.restore_id == "restore_001"
        assert metadata.backup_id == "backup_001"
        assert metadata.restore_type == RestoreType.FULL
        assert metadata.status == RestoreStatus.COMPLETED
        assert metadata.files_restored == 10
        assert metadata.duration_seconds == 5.5

class TestRestoreValidationResult:
    """Testes para classe RestoreValidationResult"""
    
    def test_restore_validation_result_creation(self):
        """Testa criação de RestoreValidationResult"""
        result = RestoreValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Low disk space"],
            space_available=True,
            compatibility_check=True,
            integrity_check=True
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert result.space_available is True
        assert result.compatibility_check is True
        assert result.integrity_check is True

class TestRestoreValidator:
    """Testes para classe RestoreValidator"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_restore_validator_initialization(self):
        """Testa inicialização do RestoreValidator"""
        validator = RestoreValidator()
        assert validator is not None
    
    def test_validate_restore_prerequisites_backup_not_found(self, temp_dir):
        """Testa validação com backup não encontrado"""
        validator = RestoreValidator()
        
        result = validator.validate_restore_prerequisites(
            "/nonexistent/backup.zip", temp_dir
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "não encontrado" in result.errors[0]
    
    def test_validate_restore_prerequisites_valid_zip(self, temp_dir):
        """Testa validação com ZIP válido"""
        # Criar backup ZIP válido
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        with zipfile.ZipFile(backup_path, 'w') as zip_file:
            zip_file.writestr("backend/app.py", "print('Hello')")
            zip_file.writestr("logs/app.log", "2024-12-19 INFO: Started")
        
        validator = RestoreValidator()
        
        result = validator.validate_restore_prerequisites(backup_path, temp_dir)
        
        assert result.is_valid is True
        assert result.integrity_check is True
        assert result.compatibility_check is True
    
    def test_validate_restore_prerequisites_corrupted_zip(self, temp_dir):
        """Testa validação com ZIP corrompido"""
        # Criar arquivo que não é um ZIP válido
        backup_path = os.path.join(temp_dir, "corrupted_backup.zip")
        with open(backup_path, 'w') as f:
            f.write("This is not a ZIP file")
        
        validator = RestoreValidator()
        
        result = validator.validate_restore_prerequisites(backup_path, temp_dir)
        
        assert result.is_valid is False
        assert result.integrity_check is False
    
    def test_validate_restore_prerequisites_insufficient_space(self, temp_dir):
        """Testa validação com espaço insuficiente"""
        # Criar backup ZIP válido
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        with zipfile.ZipFile(backup_path, 'w') as zip_file:
            zip_file.writestr("test.txt", "content")
        
        validator = RestoreValidator()
        
        # Testar com espaço mínimo muito alto
        result = validator.validate_restore_prerequisites(
            backup_path, temp_dir, required_space_mb=1000000  # 1TB
        )
        
        assert result.is_valid is False
        assert "insuficiente" in result.errors[0]
    
    def test_validate_backup_integrity_valid_zip(self, temp_dir):
        """Testa validação de integridade de ZIP válido"""
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        with zipfile.ZipFile(backup_path, 'w') as zip_file:
            zip_file.writestr("test.txt", "content")
        
        validator = RestoreValidator()
        result = validator._validate_backup_integrity(backup_path)
        
        assert result is True
    
    def test_validate_backup_integrity_corrupted_zip(self, temp_dir):
        """Testa validação de integridade de ZIP corrompido"""
        backup_path = os.path.join(temp_dir, "corrupted_backup.zip")
        with open(backup_path, 'w') as f:
            f.write("Not a ZIP file")
        
        validator = RestoreValidator()
        result = validator._validate_backup_integrity(backup_path)
        
        assert result is False
    
    def test_validate_backup_integrity_encrypted_file(self, temp_dir):
        """Testa validação de integridade de arquivo criptografado"""
        backup_path = os.path.join(temp_dir, "test_backup.enc")
        with open(backup_path, 'wb') as f:
            f.write(b"encrypted data")
        
        validator = RestoreValidator()
        result = validator._validate_backup_integrity(backup_path)
        
        assert result is True
    
    def test_check_compatibility_valid_backup(self, temp_dir):
        """Testa verificação de compatibilidade de backup válido"""
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        with zipfile.ZipFile(backup_path, 'w') as zip_file:
            zip_file.writestr("backend/app.py", "print('Hello')")
            zip_file.writestr("logs/app.log", "2024-12-19 INFO: Started")
            zip_file.writestr("blogs/post.txt", "Blog content")
        
        validator = RestoreValidator()
        result = validator._check_compatibility(backup_path)
        
        assert result is True
    
    def test_check_compatibility_incompatible_backup(self, temp_dir):
        """Testa verificação de compatibilidade de backup incompatível"""
        backup_path = os.path.join(temp_dir, "incompatible_backup.zip")
        with zipfile.ZipFile(backup_path, 'w') as zip_file:
            zip_file.writestr("random_file.txt", "content")
            zip_file.writestr("another_file.txt", "more content")
        
        validator = RestoreValidator()
        result = validator._check_compatibility(backup_path)
        
        assert result is False

class TestRestoreInteligenteManager:
    """Testes para classe RestoreInteligenteManager"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def restore_manager(self, temp_dir):
        """Cria instância do RestoreInteligenteManager para testes"""
        with patch('infrastructure.backup.inteligente.restore_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = RestoreInteligenteManager()
            manager.backup_dir = Path(temp_dir)
            return manager
    
    def test_restore_manager_initialization(self, temp_dir):
        """Testa inicialização do RestoreInteligenteManager"""
        with patch('infrastructure.backup.inteligente.restore_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = RestoreInteligenteManager()
            
            assert manager.backup_dir == mock_backup_dir
            assert isinstance(manager.restore_history, list)
            assert manager.validator is not None
    
    def test_restore_backup_backup_not_found(self, restore_manager):
        """Testa restore com backup não encontrado"""
        result = restore_manager.restore_backup("nonexistent_backup")
        
        assert result is not None
        assert result.status == RestoreStatus.FAILED
        assert "não encontrado" in result.error_message
    
    def test_restore_backup_success(self, restore_manager, temp_dir):
        """Testa restore bem-sucedido"""
        # Criar backup de teste
        backup_id = "test_backup_001"
        backup_file = os.path.join(temp_dir, f"backup_{backup_id}_20241219_120000.zip")
        
        with zipfile.ZipFile(backup_file, 'w') as zip_file:
            zip_file.writestr("backend/app.py", "print('Hello World')")
            zip_file.writestr("logs/app.log", "2024-12-19 INFO: Started")
            zip_file.writestr("blogs/post.txt", "Blog content")
        
        # Criar diretório de destino
        target_dir = os.path.join(temp_dir, "restore_target")
        os.makedirs(target_dir, exist_ok=True)
        
        result = restore_manager.restore_backup(backup_id, target_dir, RestoreType.FULL)
        
        assert result is not None
        assert result.status == RestoreStatus.COMPLETED
        assert result.files_restored == 3
        assert result.total_size_bytes > 0
        
        # Verificar se arquivos foram restaurados
        assert os.path.exists(os.path.join(target_dir, "backend", "app.py"))
        assert os.path.exists(os.path.join(target_dir, "logs", "app.log"))
        assert os.path.exists(os.path.join(target_dir, "blogs", "post.txt"))
    
    def test_restore_backup_selective(self, restore_manager, temp_dir):
        """Testa restore seletivo"""
        # Criar backup de teste
        backup_id = "test_backup_002"
        backup_file = os.path.join(temp_dir, f"backup_{backup_id}_20241219_120000.zip")
        
        with zipfile.ZipFile(backup_file, 'w') as zip_file:
            zip_file.writestr("backend/app.py", "print('Hello World')")
            zip_file.writestr("logs/app.log", "2024-12-19 INFO: Started")
            zip_file.writestr("blogs/post.txt", "Blog content")
        
        # Criar diretório de destino
        target_dir = os.path.join(temp_dir, "restore_target_selective")
        os.makedirs(target_dir, exist_ok=True)
        
        # Restore seletivo - apenas arquivos do backend
        result = restore_manager.restore_backup(
            backup_id, target_dir, RestoreType.SELECTIVE, ["backend"]
        )
        
        assert result is not None
        assert result.status == RestoreStatus.COMPLETED
        assert result.files_restored == 1  # Apenas app.py
        
        # Verificar se apenas arquivo do backend foi restaurado
        assert os.path.exists(os.path.join(target_dir, "backend", "app.py"))
        assert not os.path.exists(os.path.join(target_dir, "logs", "app.log"))
        assert not os.path.exists(os.path.join(target_dir, "blogs", "post.txt"))
    
    def test_restore_backup_with_existing_files(self, restore_manager, temp_dir):
        """Testa restore com arquivos existentes"""
        # Criar backup de teste
        backup_id = "test_backup_003"
        backup_file = os.path.join(temp_dir, f"backup_{backup_id}_20241219_120000.zip")
        
        with zipfile.ZipFile(backup_file, 'w') as zip_file:
            zip_file.writestr("test.txt", "new content")
        
        # Criar diretório de destino com arquivo existente
        target_dir = os.path.join(temp_dir, "restore_target_existing")
        os.makedirs(target_dir, exist_ok=True)
        
        existing_file = os.path.join(target_dir, "test.txt")
        with open(existing_file, 'w') as f:
            f.write("old content")
        
        result = restore_manager.restore_backup(backup_id, target_dir, RestoreType.FULL)
        
        assert result is not None
        assert result.status == RestoreStatus.COMPLETED
        
        # Verificar se arquivo foi restaurado
        with open(existing_file, 'r') as f:
            content = f.read()
        assert content == "new content"
        
        # Verificar se backup do arquivo original foi criado
        backup_files = [f for f in os.listdir(target_dir) if f.endswith('.backup_')]
        assert len(backup_files) == 1
    
    def test_decrypt_backup_success(self, restore_manager, temp_dir):
        """Testa descriptografia de backup bem-sucedida"""
        # Mock da criptografia
        with patch('infrastructure.backup.inteligente.restore_manager.CRYPTOGRAPHY_AVAILABLE', True):
            with patch('infrastructure.backup.inteligente.restore_manager.Fernet') as mock_fernet:
                # Criar arquivo criptografado de teste
                encrypted_path = os.path.join(temp_dir, "test_backup.enc")
                with open(encrypted_path, 'wb') as f:
                    f.write(b"encrypted_data")
                
                # Mock da chave e cipher
                mock_key = b"test_key_32_bytes_long_key_here"
                mock_cipher = Mock()
                mock_cipher.decrypt.return_value = b"decrypted_data"
                mock_fernet.return_value = mock_cipher
                
                # Mock do arquivo de chave
                key_file = os.path.join(temp_dir, "backup_encryption.key")
                with open(key_file, 'wb') as f:
                    f.write(mock_key)
                
                decrypted_path = os.path.join(temp_dir, "test_backup_decrypted.zip")
                result = restore_manager._decrypt_backup(encrypted_path, decrypted_path)
                
                assert result is True
                assert os.path.exists(decrypted_path)
                mock_cipher.decrypt.assert_called_once()
    
    def test_decrypt_backup_no_cryptography(self, restore_manager, temp_dir):
        """Testa descriptografia sem cryptography disponível"""
        with patch('infrastructure.backup.inteligente.restore_manager.CRYPTOGRAPHY_AVAILABLE', False):
            result = restore_manager._decrypt_backup("input.enc", "output.zip")
            assert result is False
    
    def test_extract_backup_success(self, restore_manager, temp_dir):
        """Testa extração de backup bem-sucedida"""
        # Criar backup ZIP de teste
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        with zipfile.ZipFile(backup_path, 'w') as zip_file:
            zip_file.writestr("file1.txt", "content 1")
            zip_file.writestr("file2.txt", "content 2")
            zip_file.writestr("subdir/file3.txt", "content 3")
        
        target_path = os.path.join(temp_dir, "extract_target")
        os.makedirs(target_path, exist_ok=True)
        
        files_restored, total_size = restore_manager._extract_backup(
            Path(backup_path), target_path, RestoreType.FULL
        )
        
        assert files_restored == 3
        assert total_size > 0
        
        # Verificar se arquivos foram extraídos
        assert os.path.exists(os.path.join(target_path, "file1.txt"))
        assert os.path.exists(os.path.join(target_path, "file2.txt"))
        assert os.path.exists(os.path.join(target_path, "subdir", "file3.txt"))
    
    def test_extract_backup_selective(self, restore_manager, temp_dir):
        """Testa extração seletiva de backup"""
        # Criar backup ZIP de teste
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        with zipfile.ZipFile(backup_path, 'w') as zip_file:
            zip_file.writestr("backend/app.py", "print('Hello')")
            zip_file.writestr("logs/app.log", "2024-12-19 INFO: Started")
            zip_file.writestr("blogs/post.txt", "Blog content")
        
        target_path = os.path.join(temp_dir, "extract_target_selective")
        os.makedirs(target_path, exist_ok=True)
        
        # Extração seletiva
        files_restored, total_size = restore_manager._extract_backup(
            Path(backup_path), target_path, RestoreType.SELECTIVE, ["backend"]
        )
        
        assert files_restored == 1  # Apenas app.py
        assert total_size > 0
        
        # Verificar se apenas arquivo do backend foi extraído
        assert os.path.exists(os.path.join(target_path, "backend", "app.py"))
        assert not os.path.exists(os.path.join(target_path, "logs", "app.log"))
        assert not os.path.exists(os.path.join(target_path, "blogs", "post.txt"))
    
    def test_perform_rollback_success(self, restore_manager, temp_dir):
        """Testa rollback bem-sucedido"""
        # Criar arquivos de backup para rollback
        backup_file1 = os.path.join(temp_dir, "file1.txt.backup_20241219_120000")
        backup_file2 = os.path.join(temp_dir, "file2.txt.backup_20241219_120000")
        
        with open(backup_file1, 'w') as f:
            f.write("backup content 1")
        with open(backup_file2, 'w') as f:
            f.write("backup content 2")
        
        # Criar metadados de teste
        metadata = RestoreMetadata(
            restore_id="test_restore",
            backup_id="test_backup",
            timestamp="2024-12-19T12:00:00",
            restore_type=RestoreType.FULL,
            target_path=temp_dir,
            status=RestoreStatus.FAILED,
            files_restored=0,
            total_size_bytes=0,
            duration_seconds=0.0
        )
        
        result = restore_manager._perform_rollback(temp_dir, metadata)
        
        assert result is True
        
        # Verificar se arquivos originais foram restaurados
        assert os.path.exists(os.path.join(temp_dir, "file1.txt"))
        assert os.path.exists(os.path.join(temp_dir, "file2.txt"))
        
        # Verificar se arquivos de backup foram removidos
        assert not os.path.exists(backup_file1)
        assert not os.path.exists(backup_file2)
    
    def test_perform_rollback_no_backup_files(self, restore_manager, temp_dir):
        """Testa rollback sem arquivos de backup"""
        metadata = RestoreMetadata(
            restore_id="test_restore",
            backup_id="test_backup",
            timestamp="2024-12-19T12:00:00",
            restore_type=RestoreType.FULL,
            target_path=temp_dir,
            status=RestoreStatus.FAILED,
            files_restored=0,
            total_size_bytes=0,
            duration_seconds=0.0
        )
        
        result = restore_manager._perform_rollback(temp_dir, metadata)
        
        assert result is False
    
    def test_list_restores(self, restore_manager):
        """Testa listagem de restores"""
        # Adicionar restores de teste
        restore1 = RestoreMetadata(
            restore_id="restore_001",
            backup_id="backup_001",
            timestamp="2024-12-19T12:00:00",
            restore_type=RestoreType.FULL,
            target_path="/restore/path",
            status=RestoreStatus.COMPLETED,
            files_restored=10,
            total_size_bytes=1024,
            duration_seconds=5.5
        )
        restore_manager.restore_history.append(restore1)
        
        restores = restore_manager.list_restores()
        
        assert len(restores) == 1
        assert restores[0]['id'] == "restore_001"
        assert restores[0]['backup_id'] == "backup_001"
        assert restores[0]['type'] == "full"
        assert restores[0]['status'] == "completed"
        assert restores[0]['files_restored'] == 10
    
    def test_get_restore_stats(self, restore_manager):
        """Testa obtenção de estatísticas de restore"""
        # Adicionar restores de teste
        restore1 = RestoreMetadata(
            restore_id="restore_001",
            backup_id="backup_001",
            timestamp="2024-12-19T12:00:00",
            restore_type=RestoreType.FULL,
            target_path="/restore/path",
            status=RestoreStatus.COMPLETED,
            files_restored=10,
            total_size_bytes=1024,
            duration_seconds=5.0
        )
        restore2 = RestoreMetadata(
            restore_id="restore_002",
            backup_id="backup_002",
            timestamp="2024-12-19T13:00:00",
            restore_type=RestoreType.SELECTIVE,
            target_path="/restore/path2",
            status=RestoreStatus.FAILED,
            files_restored=5,
            total_size_bytes=512,
            duration_seconds=3.0
        )
        restore_manager.restore_history.extend([restore1, restore2])
        
        stats = restore_manager.get_restore_stats()
        
        assert stats['total_restores'] == 2
        assert stats['successful_restores'] == 1
        assert stats['failed_restores'] == 1
        assert stats['success_rate'] == "50.0%"
        assert stats['average_duration_seconds'] == 4.0

class TestCloudRestore:
    """Testes para restore da nuvem"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def restore_manager(self, temp_dir):
        """Cria instância do RestoreInteligenteManager para testes"""
        with patch('infrastructure.backup.inteligente.restore_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = RestoreInteligenteManager()
            manager.backup_dir = Path(temp_dir)
            return manager
    
    @patch('infrastructure.backup.inteligente.restore_manager.BOTO3_AVAILABLE', True)
    @patch('infrastructure.backup.inteligente.restore_manager.boto3')
    def test_download_from_s3_success(self, mock_boto3, restore_manager, temp_dir):
        """Testa download bem-sucedido do S3"""
        mock_client = Mock()
        mock_boto3.client.return_value = mock_client
        
        restore_manager.s3_client = mock_client
        
        result = restore_manager._download_from_cloud('s3', 'test-bucket', 'test-backup')
        
        assert result is not None
        mock_client.download_file.assert_called_once()
    
    @patch('infrastructure.backup.inteligente.restore_manager.GCS_AVAILABLE', True)
    @patch('infrastructure.backup.inteligente.restore_manager.storage')
    def test_download_from_gcs_success(self, mock_storage, restore_manager, temp_dir):
        """Testa download bem-sucedido do GCS"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        restore_manager.gcs_client = mock_client
        
        result = restore_manager._download_from_cloud('gcs', 'test-bucket', 'test-backup')
        
        assert result is not None
        mock_blob.download_to_filename.assert_called_once()
    
    def test_download_from_cloud_unsupported_provider(self, restore_manager):
        """Testa download de provedor não suportado"""
        result = restore_manager._download_from_cloud('unsupported', 'bucket', 'backup')
        
        assert result is None
    
    @patch('infrastructure.backup.inteligente.restore_manager.BOTO3_AVAILABLE', True)
    @patch('infrastructure.backup.inteligente.restore_manager.boto3')
    def test_restore_from_cloud_success(self, mock_boto3, restore_manager, temp_dir):
        """Testa restore da nuvem bem-sucedido"""
        # Mock do download
        restore_manager._download_from_cloud = Mock(return_value="local_backup.zip")
        
        # Mock do restore local
        restore_manager.restore_backup = Mock(return_value=RestoreMetadata(
            restore_id="cloud_restore",
            backup_id="cloud_backup",
            timestamp="2024-12-19T12:00:00",
            restore_type=RestoreType.CLOUD,
            target_path="/restore/path",
            status=RestoreStatus.COMPLETED,
            files_restored=5,
            total_size_bytes=1024,
            duration_seconds=10.0
        ))
        
        result = restore_manager.restore_from_cloud("cloud_backup", "s3", "test-bucket")
        
        assert result is not None
        assert result.status == RestoreStatus.COMPLETED
        assert result.restore_type == RestoreType.CLOUD

class TestIntegration:
    """Testes de integração"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_restore_workflow(self, temp_dir):
        """Testa workflow completo de restore"""
        # Criar backup de teste
        backup_id = "integration_test_001"
        backup_file = os.path.join(temp_dir, f"backup_{backup_id}_20241219_120000.zip")
        
        with zipfile.ZipFile(backup_file, 'w') as zip_file:
            zip_file.writestr("backend/app.py", "print('Hello World')")
            zip_file.writestr("backend/config.py", "DEBUG = True")
            zip_file.writestr("logs/app.log", "2024-12-19 INFO: Application started")
            zip_file.writestr("blogs/post1.txt", "Blog post content 1")
            zip_file.writestr("blogs/post2.txt", "Blog post content 2")
        
        with patch('infrastructure.backup.inteligente.restore_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = RestoreInteligenteManager()
            manager.backup_dir = Path(temp_dir)
            
            # Criar diretório de destino
            target_dir = os.path.join(temp_dir, "restore_target")
            os.makedirs(target_dir, exist_ok=True)
            
            # Executar restore
            result = manager.restore_backup(backup_id, target_dir, RestoreType.FULL)
            
            assert result is not None
            assert result.status == RestoreStatus.COMPLETED
            assert result.files_restored == 5
            assert result.total_size_bytes > 0
            assert result.duration_seconds > 0
            
            # Verificar se todos os arquivos foram restaurados
            expected_files = [
                "backend/app.py",
                "backend/config.py",
                "logs/app.log",
                "blogs/post1.txt",
                "blogs/post2.txt"
            ]
            
            for expected_file in expected_files:
                file_path = os.path.join(target_dir, expected_file)
                assert os.path.exists(file_path), f"Arquivo não encontrado: {expected_file}"
    
    def test_selective_restore_workflow(self, temp_dir):
        """Testa workflow de restore seletivo"""
        # Criar backup de teste
        backup_id = "integration_test_002"
        backup_file = os.path.join(temp_dir, f"backup_{backup_id}_20241219_120000.zip")
        
        with zipfile.ZipFile(backup_file, 'w') as zip_file:
            zip_file.writestr("backend/app.py", "print('Hello World')")
            zip_file.writestr("logs/app.log", "2024-12-19 INFO: Started")
            zip_file.writestr("blogs/post.txt", "Blog content")
        
        with patch('infrastructure.backup.inteligente.restore_manager.Path') as mock_path:
            mock_backup_dir = Mock()
            mock_backup_dir.mkdir.return_value = None
            mock_path.return_value = mock_backup_dir
            
            manager = RestoreInteligenteManager()
            manager.backup_dir = Path(temp_dir)
            
            # Criar diretório de destino
            target_dir = os.path.join(temp_dir, "restore_target_selective")
            os.makedirs(target_dir, exist_ok=True)
            
            # Restore seletivo - apenas backend
            result = manager.restore_backup(
                backup_id, target_dir, RestoreType.SELECTIVE, ["backend"]
            )
            
            assert result is not None
            assert result.status == RestoreStatus.COMPLETED
            assert result.files_restored == 1
            
            # Verificar se apenas arquivo do backend foi restaurado
            assert os.path.exists(os.path.join(target_dir, "backend", "app.py"))
            assert not os.path.exists(os.path.join(target_dir, "logs", "app.log"))
            assert not os.path.exists(os.path.join(target_dir, "blogs", "post.txt"))

def main():
    """Função principal para execução dos testes"""
    print("Executando testes do sistema de restore inteligente...")
    
    # Executar testes específicos
    test_classes = [
        TestRestoreType,
        TestRestoreStatus,
        TestRestoreMetadata,
        TestRestoreValidationResult,
        TestRestoreValidator,
        TestRestoreInteligenteManager,
        TestCloudRestore,
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