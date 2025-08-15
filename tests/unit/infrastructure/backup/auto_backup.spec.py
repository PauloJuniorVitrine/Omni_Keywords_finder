from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Backup Automático

Testes abrangentes para validar todas as funcionalidades do sistema
de backup e recuperação automática.

Autor: Sistema de Testes
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import pytest
import tempfile
import shutil
import os
import zipfile
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from infrastructure.backup.auto_backup import (
    AutoBackupSystem,
    BackupMetadata,
    BackupIntegrityValidator,
    DatabaseBackupManager,
    BACKUP_CONFIG
)

class TestBackupIntegrityValidator:
    """Testes para validador de integridade"""
    
    def test_calculate_checksum(self):
        """Testa cálculo de checksum"""
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            checksum = BackupIntegrityValidator.calculate_checksum(temp_file)
            assert len(checksum) == 64  # SHA-256 tem 64 caracteres hex
            assert isinstance(checksum, str)
        finally:
            os.unlink(temp_file)
    
    def test_validate_backup_integrity_success(self):
        """Testa validação de integridade bem-sucedida"""
        # Criar arquivo ZIP válido
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            temp_zip = f.name
        
        try:
            with zipfile.ZipFile(temp_zip, 'w') as zipf:
                zipf.writestr('test.txt', 'test content')
            
            # Criar metadados
            size = os.path.getsize(temp_zip)
            checksum = BackupIntegrityValidator.calculate_checksum(temp_zip)
            metadata = BackupMetadata(
                backup_id='test',
                timestamp=datetime.now().isoformat(),
                size_bytes=size,
                file_count=1,
                checksum=checksum,
                compression_ratio=10.0,
                status='completed'
            )
            
            # Validar
            result = BackupIntegrityValidator.validate_backup_integrity(temp_zip, metadata)
            assert result is True
            
        finally:
            os.unlink(temp_zip)
    
    def test_validate_backup_integrity_failure(self):
        """Testa validação de integridade com falha"""
        # Criar arquivo ZIP válido
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            temp_zip = f.name
        
        try:
            with zipfile.ZipFile(temp_zip, 'w') as zipf:
                zipf.writestr('test.txt', 'test content')
            
            # Criar metadados com checksum incorreto
            size = os.path.getsize(temp_zip)
            metadata = BackupMetadata(
                backup_id='test',
                timestamp=datetime.now().isoformat(),
                size_bytes=size,
                file_count=1,
                checksum='invalid_checksum',
                compression_ratio=10.0,
                status='completed'
            )
            
            # Validar
            result = BackupIntegrityValidator.validate_backup_integrity(temp_zip, metadata)
            assert result is False
            
        finally:
            os.unlink(temp_zip)

class TestDatabaseBackupManager:
    """Testes para gerenciador de backup de banco"""
    
    def test_backup_sqlite_database_success(self):
        """Testa backup bem-sucedido do banco SQLite"""
        # Criar banco de dados temporário
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Criar tabela de teste
            with sqlite3.connect(db_path) as conn:
                conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
                conn.execute("INSERT INTO test (name) VALUES (?)", ("test_value",))
                conn.commit()
            
            # Fazer backup
            backup_path = db_path + '.backup'
            result = DatabaseBackupManager.backup_sqlite_database(db_path, backup_path)
            
            assert result is True
            assert os.path.exists(backup_path)
            
            # Verificar se backup é válido
            with sqlite3.connect(backup_path) as conn:
                cursor = conn.execute("SELECT name FROM test WHERE id = 1")
                row = cursor.fetchone()
                assert row[0] == "test_value"
            
        finally:
            os.unlink(db_path)
            if os.path.exists(backup_path):
                os.unlink(backup_path)
    
    def test_backup_sqlite_database_not_found(self):
        """Testa backup de banco inexistente"""
        result = DatabaseBackupManager.backup_sqlite_database('nonexistent.db', 'backup.db')
        assert result is False
    
    def test_validate_database_backup_success(self):
        """Testa validação bem-sucedida de backup do banco"""
        # Criar banco de dados temporário
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Criar tabela de teste
            with sqlite3.connect(db_path) as conn:
                conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
                conn.commit()
            
            # Validar
            result = DatabaseBackupManager.validate_database_backup(db_path)
            assert result is True
            
        finally:
            os.unlink(db_path)
    
    def test_validate_database_backup_empty(self):
        """Testa validação de banco vazio"""
        # Criar banco de dados vazio
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Validar
            result = DatabaseBackupManager.validate_database_backup(db_path)
            assert result is False  # Banco vazio deve falhar
            
        finally:
            os.unlink(db_path)

class TestAutoBackupSystem:
    """Testes para sistema principal de backup"""
    
    @pytest.fixture
    def temp_backup_dir(self):
        """Fixture para diretório temporário de backup"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def backup_system(self, temp_backup_dir):
        """Fixture para sistema de backup com diretório temporário"""
        with patch('infrastructure.backup.auto_backup.BACKUP_CONFIG') as mock_config:
            mock_config['backup_dir'] = temp_backup_dir
            mock_config['retention_days'] = 30
            mock_config['compression_level'] = 9
            mock_config['max_backup_size_mb'] = 500
            mock_config['backup_schedule'] = '02:00'
            mock_config['critical_files'] = ['test_file.txt']
            mock_config['exclude_patterns'] = ['__pycache__', '.git']
            
            system = AutoBackupSystem()
            return system
    
    def test_init_creates_backup_dir(self, temp_backup_dir):
        """Testa criação do diretório de backup"""
        with patch('infrastructure.backup.auto_backup.BACKUP_CONFIG') as mock_config:
            mock_config['backup_dir'] = temp_backup_dir
            mock_config['retention_days'] = 30
            mock_config['compression_level'] = 9
            mock_config['max_backup_size_mb'] = 500
            mock_config['backup_schedule'] = '02:00'
            mock_config['critical_files'] = []
            mock_config['exclude_patterns'] = []
            
            system = AutoBackupSystem()
            assert os.path.exists(temp_backup_dir)
    
    def test_should_exclude_patterns(self, backup_system):
        """Testa exclusão de padrões"""
        assert backup_system._should_exclude('__pycache__/file.py') is True
        assert backup_system._should_exclude('.git/config') is True
        assert backup_system._should_exclude('normal_file.py') is False
    
    def test_create_backup_filename(self, backup_system):
        """Testa criação de nome de arquivo de backup"""
        filename = backup_system._create_backup_filename()
        assert filename.startswith('backup_auto_')
        assert filename.endswith('.zip')
        assert len(filename) > 20  # Deve ter timestamp
    
    def test_compress_files_success(self, backup_system, temp_backup_dir):
        """Testa compressão de arquivos"""
        # Criar arquivo de teste
        test_file = os.path.join(temp_backup_dir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('test content' * 100)  # Arquivo com algum conteúdo
        
        files = [test_file]
        backup_path = os.path.join(temp_backup_dir, 'test_backup.zip')
        
        total_size, compression_ratio = backup_system._compress_files(files, backup_path)
        
        assert os.path.exists(backup_path)
        assert total_size > 0
        assert compression_ratio >= 0
        
        # Verificar se ZIP contém o arquivo
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            assert 'test_file.txt' in zipf.namelist()
    
    def test_create_backup_success(self, backup_system, temp_backup_dir):
        """Testa criação de backup completo"""
        # Criar arquivo de teste
        test_file = os.path.join(temp_backup_dir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        # Mock para simular arquivo crítico existente
        with patch.object(backup_system, '_get_files_to_backup') as mock_get_files:
            mock_get_files.return_value = [test_file]
            
            # Mock para simular espaço suficiente em disco
            with patch('psutil.disk_usage') as mock_disk:
                mock_disk.return_value = Mock(free=1024*1024*1024)  # 1GB livre
                
                metadata = backup_system.create_backup()
                
                assert metadata is not None
                assert metadata.status == 'completed'
                assert metadata.file_count == 1
                assert metadata.size_bytes > 0
                assert len(metadata.checksum) == 64
    
    def test_create_backup_insufficient_space(self, backup_system):
        """Testa criação de backup com espaço insuficiente"""
        with patch('psutil.disk_usage') as mock_disk:
            mock_disk.return_value = Mock(free=1024)  # Pouco espaço
            
            metadata = backup_system.create_backup()
            assert metadata is None
    
    def test_create_backup_no_files(self, backup_system):
        """Testa criação de backup sem arquivos"""
        with patch.object(backup_system, '_get_files_to_backup') as mock_get_files:
            mock_get_files.return_value = []
            
            with patch('psutil.disk_usage') as mock_disk:
                mock_disk.return_value = Mock(free=1024*1024*1024)
                
                metadata = backup_system.create_backup()
                assert metadata is None
    
    def test_cleanup_old_backups(self, backup_system, temp_backup_dir):
        """Testa limpeza de backups antigos"""
        # Criar backups antigos e recentes
        old_date = datetime.now() - timedelta(days=31)
        recent_date = datetime.now() - timedelta(days=1)
        
        old_backup = os.path.join(temp_backup_dir, 'backup_auto_old.zip')
        recent_backup = os.path.join(temp_backup_dir, 'backup_auto_recent.zip')
        
        # Criar arquivos ZIP vazios
        with zipfile.ZipFile(old_backup, 'w'):
            pass
        with zipfile.ZipFile(recent_backup, 'w'):
            pass
        
        # Alterar timestamp do backup antigo
        os.utime(old_backup, (old_date.timestamp(), old_date.timestamp()))
        
        # Executar limpeza
        backup_system._cleanup_old_backups()
        
        # Verificar se backup antigo foi removido
        assert not os.path.exists(old_backup)
        assert os.path.exists(recent_backup)
    
    def test_restore_backup_success(self, backup_system, temp_backup_dir):
        """Testa restauração de backup"""
        # Criar arquivo de teste
        test_file = os.path.join(temp_backup_dir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        # Criar backup
        backup_path = os.path.join(temp_backup_dir, 'test_backup.zip')
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            zipf.write(test_file, 'test_file.txt')
        
        # Mock metadados
        backup_system.backup_history = [BackupMetadata(
            backup_id='test_backup',
            timestamp=datetime.now().isoformat(),
            size_bytes=os.path.getsize(backup_path),
            file_count=1,
            checksum=BackupIntegrityValidator.calculate_checksum(backup_path),
            compression_ratio=10.0,
            status='completed'
        )]
        
        # Restaurar
        success = backup_system.restore_backup('test_backup.zip', temp_backup_dir)
        assert success is True
    
    def test_restore_backup_not_found(self, backup_system):
        """Testa restauração de backup inexistente"""
        success = backup_system.restore_backup('nonexistent.zip')
        assert success is False
    
    def test_list_backups(self, backup_system, temp_backup_dir):
        """Testa listagem de backups"""
        # Criar alguns backups
        for index in range(3):
            backup_path = os.path.join(temp_backup_dir, f'backup_auto_test_{index}.zip')
            with zipfile.ZipFile(backup_path, 'w') as zipf:
                zipf.writestr('test.txt', 'content')
        
        # Mock metadados
        backup_system.backup_history = [
            BackupMetadata(
                backup_id=f'test_{index}',
                timestamp=datetime.now().isoformat(),
                size_bytes=100,
                file_count=1,
                checksum='test_checksum',
                compression_ratio=10.0,
                status='completed'
            ) for index in range(3)
        ]
        
        backups = backup_system.list_backups()
        assert len(backups) == 3
        assert all('filename' in backup for backup in backups)
        assert all('size_mb' in backup for backup in backups)

class TestBackupMetadata:
    """Testes para metadados de backup"""
    
    def test_backup_metadata_creation(self):
        """Testa criação de metadados"""
        metadata = BackupMetadata(
            backup_id='test',
            timestamp=datetime.now().isoformat(),
            size_bytes=1024,
            file_count=5,
            checksum='test_checksum',
            compression_ratio=15.5,
            status='completed'
        )
        
        assert metadata.backup_id == 'test'
        assert metadata.size_bytes == 1024
        assert metadata.file_count == 5
        assert metadata.compression_ratio == 15.5
        assert metadata.status == 'completed'
        assert metadata.error_message is None
    
    def test_backup_metadata_with_error(self):
        """Testa metadados com erro"""
        metadata = BackupMetadata(
            backup_id='test',
            timestamp=datetime.now().isoformat(),
            size_bytes=0,
            file_count=0,
            checksum='',
            compression_ratio=0,
            status='failed',
            error_message='Test error'
        )
        
        assert metadata.status == 'failed'
        assert metadata.error_message == 'Test error'

if __name__ == '__main__':
    pytest.main([__file__, '-value']) 