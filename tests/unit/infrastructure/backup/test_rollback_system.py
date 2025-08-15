from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Rollback Automático
Tracing ID: TEST_ROLLBACK_SYSTEM_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa testes unitários abrangentes para o sistema
de rollback automático, cobrindo todos os cenários de uso e
validações de segurança enterprise.
"""

import pytest
import tempfile
import shutil
import json
import os
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar o sistema a ser testado
from infrastructure.backup.rollback_system import RollbackSystem, BackupSnapshot, RollbackOperation

class TestRollbackSystem:
    """
    Testes para RollbackSystem.
    
    Cobre todos os métodos públicos e cenários de erro.
    """
    
    @pytest.fixture
    def temp_backup_dir(self):
        """Cria diretório temporário para backup de testes."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_files(self, temp_backup_dir):
        """Cria arquivos de exemplo para testes."""
        files = []
        
        # Criar arquivo 1
        file1_path = os.path.join(temp_backup_dir, "test_file1.txt")
        with open(file1_path, 'w') as f:
            f.write("Conteúdo do arquivo 1")
        files.append(file1_path)
        
        # Criar arquivo 2
        file2_path = os.path.join(temp_backup_dir, "test_file2.txt")
        with open(file2_path, 'w') as f:
            f.write("Conteúdo do arquivo 2")
        files.append(file2_path)
        
        # Criar arquivo em subdiretório
        subdir = os.path.join(temp_backup_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)
        file3_path = os.path.join(subdir, "test_file3.txt")
        with open(file3_path, 'w') as f:
            f.write("Conteúdo do arquivo 3")
        files.append(file3_path)
        
        return files
    
    @pytest.fixture
    def rollback_system(self, temp_backup_dir):
        """Cria instância do sistema de rollback para testes."""
        return RollbackSystem(
            backup_dir=temp_backup_dir,
            max_snapshots=5,
            max_age_hours=24,
            auto_rollback_on_divergence=True
        )
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        system = RollbackSystem()
        
        assert system.max_snapshots == 10
        assert system.max_age_hours == 24
        assert system.auto_rollback_on_divergence == True
        assert "snapshots" in system.backup_dir
        assert len(system.snapshots) == 0
        assert len(system.rollback_history) == 0
    
    def test_init_custom_values(self, temp_backup_dir):
        """Testa inicialização com valores customizados."""
        system = RollbackSystem(
            backup_dir=temp_backup_dir,
            max_snapshots=3,
            max_age_hours=12,
            auto_rollback_on_divergence=False
        )
        
        assert system.backup_dir == temp_backup_dir
        assert system.max_snapshots == 3
        assert system.max_age_hours == 12
        assert system.auto_rollback_on_divergence == False
    
    def test_create_snapshot_success(self, rollback_system, sample_files):
        """Testa criação de snapshot com sucesso."""
        description = "Teste de snapshot"
        
        snapshot = rollback_system.create_snapshot(sample_files, description)
        
        # Verificar que snapshot foi criado
        assert isinstance(snapshot, BackupSnapshot)
        assert snapshot.description == description
        assert len(snapshot.files_backed_up) == 3
        assert snapshot.total_size_bytes > 0
        assert snapshot.checksum is not None
        assert snapshot.timestamp is not None
        assert snapshot.snapshot_id is not None
        
        # Verificar que foi adicionado ao dicionário
        assert snapshot.snapshot_id in rollback_system.snapshots
        assert rollback_system.snapshots[snapshot.snapshot_id] == snapshot
        
        # Verificar que arquivos foram copiados
        snapshot_dir = Path(snapshot.backup_path)
        assert snapshot_dir.exists()
        
        for relative_path in snapshot.files_backed_up:
            backup_file = snapshot_dir / relative_path
            assert backup_file.exists()
    
    def test_create_snapshot_empty_files(self, rollback_system):
        """Testa criação de snapshot com lista vazia de arquivos."""
        with pytest.raises(ValueError, match="Lista de arquivos para backup não pode estar vazia"):
            rollback_system.create_snapshot([], "Teste")
    
    def test_create_snapshot_file_not_found(self, rollback_system):
        """Testa criação de snapshot com arquivo inexistente."""
        non_existent_file = "/path/to/non/existent/file.txt"
        
        with pytest.raises(FileNotFoundError):
            rollback_system.create_snapshot([non_existent_file], "Teste")
    
    def test_create_snapshot_error_cleanup(self, rollback_system, sample_files, temp_backup_dir):
        """Testa limpeza em caso de erro na criação de snapshot."""
        # Criar snapshot válido primeiro
        snapshot1 = rollback_system.create_snapshot(sample_files[:1], "Snapshot 1")
        
        # Tentar criar snapshot com arquivo inexistente
        files_with_error = sample_files + ["/non/existent/file.txt"]
        
        with pytest.raises(FileNotFoundError):
            rollback_system.create_snapshot(files_with_error, "Snapshot com erro")
        
        # Verificar que snapshot anterior ainda existe
        assert snapshot1.snapshot_id in rollback_system.snapshots
        assert Path(snapshot1.backup_path).exists()
    
    def test_restore_snapshot_success(self, rollback_system, sample_files, temp_backup_dir):
        """Testa restauração de snapshot com sucesso."""
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot para restaurar")
        
        # Modificar arquivos originais
        for file_path in sample_files:
            with open(file_path, 'w') as f:
                f.write("Conteúdo modificado")
        
        # Restaurar snapshot
        operation = rollback_system.restore_snapshot(snapshot.snapshot_id, "manual")
        
        # Verificar operação
        assert isinstance(operation, RollbackOperation)
        assert operation.success == True
        assert operation.snapshot_id == snapshot.snapshot_id
        assert operation.trigger == "manual"
        assert len(operation.files_restored) == 3
        assert operation.error_message is None
        assert operation.execution_time_seconds is not None
        
        # Verificar que arquivos foram restaurados
        for file_path in sample_files:
            with open(file_path, 'r') as f:
                content = f.read()
                assert "Conteúdo modificado" not in content
                assert "Conteúdo do arquivo" in content
        
        # Verificar que foi adicionado ao histórico
        assert len(rollback_system.rollback_history) == 1
        assert rollback_system.rollback_history[0] == operation
    
    def test_restore_snapshot_not_found(self, rollback_system):
        """Testa restauração de snapshot inexistente."""
        with pytest.raises(KeyError):
            rollback_system.restore_snapshot("snapshot_inexistente", "manual")
    
    def test_restore_snapshot_expired(self, rollback_system, sample_files):
        """Testa restauração de snapshot expirado."""
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot expirado")
        
        # Modificar timestamp para expirar
        snapshot.timestamp = (datetime.utcnow() - timedelta(hours=25)).isoformat()
        
        with pytest.raises(ValueError, match="Snapshot expirado"):
            rollback_system.restore_snapshot(snapshot.snapshot_id, "manual")
    
    def test_detect_divergence_and_rollback_with_divergence(self, rollback_system, sample_files):
        """Testa detecção de divergência e rollback automático."""
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot para divergência")
        
        # Modificar arquivos para criar divergência
        for file_path in sample_files:
            with open(file_path, 'w') as f:
                f.write("Conteúdo divergente")
        
        # Calcular checksums esperados (dos arquivos originais)
        expected_checksums = {}
        for relative_path in snapshot.files_backed_up:
            backup_file = Path(snapshot.backup_path) / relative_path
            with open(backup_file, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            expected_checksums[relative_path] = checksum
        
        # Detectar divergência e fazer rollback
        operation = rollback_system.detect_divergence_and_rollback(sample_files, expected_checksums)
        
        # Verificar que rollback foi executado
        assert operation is not None
        assert isinstance(operation, RollbackOperation)
        assert operation.success == True
        assert operation.trigger == "divergence_detected"
        assert operation.snapshot_id == snapshot.snapshot_id
        
        # Verificar que arquivos foram restaurados
        for file_path in sample_files:
            with open(file_path, 'r') as f:
                content = f.read()
                assert "Conteúdo divergente" not in content
                assert "Conteúdo do arquivo" in content
    
    def test_detect_divergence_and_rollback_no_divergence(self, rollback_system, sample_files):
        """Testa detecção de divergência quando não há divergência."""
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot sem divergência")
        
        # Calcular checksums atuais (que devem ser iguais aos esperados)
        current_checksums = {}
        for file_path in sample_files:
            with open(file_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            current_checksums[file_path] = checksum
        
        # Detectar divergência
        operation = rollback_system.detect_divergence_and_rollback(sample_files, current_checksums)
        
        # Verificar que não houve rollback
        assert operation is None
    
    def test_detect_divergence_and_rollback_auto_rollback_disabled(self, rollback_system, sample_files):
        """Testa detecção de divergência com rollback automático desabilitado."""
        # Desabilitar rollback automático
        rollback_system.auto_rollback_on_divergence = False
        
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot sem auto-rollback")
        
        # Modificar arquivos para criar divergência
        for file_path in sample_files:
            with open(file_path, 'w') as f:
                f.write("Conteúdo divergente")
        
        # Calcular checksums esperados
        expected_checksums = {}
        for relative_path in snapshot.files_backed_up:
            backup_file = Path(snapshot.backup_path) / relative_path
            with open(backup_file, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
            expected_checksums[relative_path] = checksum
        
        # Detectar divergência
        operation = rollback_system.detect_divergence_and_rollback(sample_files, expected_checksums)
        
        # Verificar que não houve rollback automático
        assert operation is None
        
        # Verificar que arquivos ainda estão modificados
        for file_path in sample_files:
            with open(file_path, 'r') as f:
                content = f.read()
                assert "Conteúdo divergente" in content
    
    def test_cleanup_old_snapshots(self, rollback_system, sample_files):
        """Testa limpeza de snapshots antigos e excedentes."""
        # Criar mais snapshots que o máximo permitido
        for index in range(7):  # Mais que max_snapshots (5)
            snapshot = rollback_system.create_snapshot(sample_files, f"Snapshot {index}")
        
        # Verificar que apenas os snapshots mais recentes foram mantidos
        assert len(rollback_system.snapshots) == 5
        
        # Verificar que os snapshots mais antigos foram removidos
        snapshot_ids = list(rollback_system.snapshots.keys())
        snapshot_ids.sort()  # Ordenar por ID (que inclui timestamp)
        
        # Os 5 snapshots restantes devem ser os mais recentes
        assert len(snapshot_ids) == 5
    
    def test_get_snapshot_info(self, rollback_system, sample_files):
        """Testa obtenção de informações de snapshot específico."""
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot para info")
        
        # Obter informações
        info = rollback_system.get_snapshot_info(snapshot.snapshot_id)
        
        # Verificar que informações foram retornadas
        assert info is not None
        assert info.snapshot_id == snapshot.snapshot_id
        assert info.description == snapshot.description
        assert info.files_backed_up == snapshot.files_backed_up
    
    def test_get_snapshot_info_not_found(self, rollback_system):
        """Testa obtenção de informações de snapshot inexistente."""
        info = rollback_system.get_snapshot_info("snapshot_inexistente")
        
        # Verificar que None foi retornado
        assert info is None
    
    def test_list_snapshots(self, rollback_system, sample_files):
        """Testa listagem de snapshots."""
        # Criar alguns snapshots
        for index in range(3):
            rollback_system.create_snapshot(sample_files, f"Snapshot {index}")
        
        # Listar snapshots
        snapshots_list = rollback_system.list_snapshots()
        
        # Verificar que lista foi retornada
        assert len(snapshots_list) == 3
        
        # Verificar estrutura dos dados
        for snapshot_info in snapshots_list:
            assert "snapshot_id" in snapshot_info
            assert "timestamp" in snapshot_info
            assert "description" in snapshot_info
            assert "files_count" in snapshot_info
            assert "total_size_mb" in snapshot_info
            assert "age_hours" in snapshot_info
            assert "is_valid" in snapshot_info
        
        # Verificar que está ordenado por timestamp (mais recentes primeiro)
        timestamps = [info["timestamp"] for info in snapshots_list]
        assert timestamps == sorted(timestamps, reverse=True)
    
    def test_get_rollback_history(self, rollback_system, sample_files):
        """Testa obtenção do histórico de rollback."""
        # Criar snapshot e fazer rollback
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot para histórico")
        
        # Modificar arquivos
        for file_path in sample_files:
            with open(file_path, 'w') as f:
                f.write("Conteúdo modificado")
        
        # Fazer rollback
        rollback_system.restore_snapshot(snapshot.snapshot_id, "manual")
        
        # Obter histórico
        history = rollback_system.get_rollback_history()
        
        # Verificar que histórico foi retornado
        assert len(history) == 1
        
        # Verificar estrutura dos dados
        operation_info = history[0]
        assert "operation_id" in operation_info
        assert "timestamp" in operation_info
        assert "trigger" in operation_info
        assert "snapshot_id" in operation_info
        assert "files_restored" in operation_info
        assert "success" in operation_info
        assert "execution_time_seconds" in operation_info
    
    def test_export_snapshot_zip(self, rollback_system, sample_files, temp_backup_dir):
        """Testa exportação de snapshot em formato ZIP."""
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot para exportar")
        
        # Exportar snapshot
        export_path = os.path.join(temp_backup_dir, "exported_snapshot.zip")
        result_path = rollback_system.export_snapshot(snapshot.snapshot_id, export_path, "zip")
        
        # Verificar que arquivo foi criado
        assert result_path == export_path
        assert os.path.exists(export_path)
        assert export_path.endswith(".zip")
        
        # Verificar tamanho do arquivo
        assert os.path.getsize(export_path) > 0
    
    def test_export_snapshot_tar(self, rollback_system, sample_files, temp_backup_dir):
        """Testa exportação de snapshot em formato TAR."""
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot para exportar TAR")
        
        # Exportar snapshot
        export_path = os.path.join(temp_backup_dir, "exported_snapshot.tar.gz")
        result_path = rollback_system.export_snapshot(snapshot.snapshot_id, export_path, "tar")
        
        # Verificar que arquivo foi criado
        assert result_path == export_path
        assert os.path.exists(export_path)
        assert export_path.endswith(".tar.gz")
        
        # Verificar tamanho do arquivo
        assert os.path.getsize(export_path) > 0
    
    def test_export_snapshot_invalid_format(self, rollback_system, sample_files, temp_backup_dir):
        """Testa exportação de snapshot com formato inválido."""
        # Criar snapshot
        snapshot = rollback_system.create_snapshot(sample_files, "Snapshot para exportar")
        
        # Tentar exportar com formato inválido
        export_path = os.path.join(temp_backup_dir, "exported_snapshot.rar")
        
        with pytest.raises(ValueError, match="Formato não suportado"):
            rollback_system.export_snapshot(snapshot.snapshot_id, export_path, "rar")
    
    def test_export_snapshot_not_found(self, rollback_system, temp_backup_dir):
        """Testa exportação de snapshot inexistente."""
        export_path = os.path.join(temp_backup_dir, "exported_snapshot.zip")
        
        with pytest.raises(KeyError):
            rollback_system.export_snapshot("snapshot_inexistente", export_path, "zip")

class TestBackupSnapshot:
    """
    Testes para BackupSnapshot.
    
    Cobre funcionalidades da estrutura de dados.
    """
    
    def test_snapshot_creation(self):
        """Testa criação de snapshot."""
        snapshot = BackupSnapshot(
            snapshot_id="test_snapshot_001",
            timestamp="2025-01-27T10:00:00",
            description="Teste de snapshot",
            files_backed_up=["file1.txt", "file2.txt"],
            total_size_bytes=1024,
            checksum="abc123",
            metadata={"test": "data"},
            backup_path="/path/to/backup"
        )
        
        assert snapshot.snapshot_id == "test_snapshot_001"
        assert snapshot.timestamp == "2025-01-27T10:00:00"
        assert snapshot.description == "Teste de snapshot"
        assert snapshot.files_backed_up == ["file1.txt", "file2.txt"]
        assert snapshot.total_size_bytes == 1024
        assert snapshot.checksum == "abc123"
        assert snapshot.metadata == {"test": "data"}
        assert snapshot.backup_path == "/path/to/backup"
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        snapshot = BackupSnapshot(
            snapshot_id="test_snapshot_001",
            timestamp="2025-01-27T10:00:00",
            description="Teste de snapshot",
            files_backed_up=["file1.txt"],
            total_size_bytes=512,
            checksum="abc123",
            metadata={"test": "data"},
            backup_path="/path/to/backup"
        )
        
        data = snapshot.to_dict()
        
        assert isinstance(data, dict)
        assert data["snapshot_id"] == "test_snapshot_001"
        assert data["timestamp"] == "2025-01-27T10:00:00"
        assert data["description"] == "Teste de snapshot"
        assert data["files_backed_up"] == ["file1.txt"]
        assert data["total_size_bytes"] == 512
        assert data["checksum"] == "abc123"
        assert data["metadata"] == {"test": "data"}
        assert data["backup_path"] == "/path/to/backup"
    
    def test_is_valid_recent(self):
        """Testa validação de snapshot recente."""
        recent_timestamp = datetime.utcnow().isoformat()
        snapshot = BackupSnapshot(
            snapshot_id="test_snapshot_001",
            timestamp=recent_timestamp,
            description="Teste",
            files_backed_up=[],
            total_size_bytes=0,
            checksum="abc123",
            metadata={},
            backup_path="/path/to/backup"
        )
        
        assert snapshot.is_valid(24) == True  # Válido para 24 horas
    
    def test_is_valid_expired(self):
        """Testa validação de snapshot expirado."""
        expired_timestamp = (datetime.utcnow() - timedelta(hours=25)).isoformat()
        snapshot = BackupSnapshot(
            snapshot_id="test_snapshot_001",
            timestamp=expired_timestamp,
            description="Teste",
            files_backed_up=[],
            total_size_bytes=0,
            checksum="abc123",
            metadata={},
            backup_path="/path/to/backup"
        )
        
        assert snapshot.is_valid(24) == False  # Expirado após 24 horas

class TestRollbackOperation:
    """
    Testes para RollbackOperation.
    
    Cobre funcionalidades da estrutura de dados.
    """
    
    def test_operation_creation(self):
        """Testa criação de operação de rollback."""
        operation = RollbackOperation(
            operation_id="rollback_001",
            timestamp="2025-01-27T10:00:00",
            trigger="manual",
            snapshot_id="snapshot_001",
            files_restored=["file1.txt", "file2.txt"],
            success=True,
            error_message=None,
            execution_time_seconds=1.5
        )
        
        assert operation.operation_id == "rollback_001"
        assert operation.timestamp == "2025-01-27T10:00:00"
        assert operation.trigger == "manual"
        assert operation.snapshot_id == "snapshot_001"
        assert operation.files_restored == ["file1.txt", "file2.txt"]
        assert operation.success == True
        assert operation.error_message is None
        assert operation.execution_time_seconds == 1.5
    
    def test_operation_creation_with_error(self):
        """Testa criação de operação de rollback com erro."""
        operation = RollbackOperation(
            operation_id="rollback_002",
            timestamp="2025-01-27T10:00:00",
            trigger="automatic",
            snapshot_id="snapshot_002",
            files_restored=[],
            success=False,
            error_message="Erro durante rollback",
            execution_time_seconds=0.5
        )
        
        assert operation.success == False
        assert operation.error_message == "Erro durante rollback"
        assert operation.files_restored == []
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        operation = RollbackOperation(
            operation_id="rollback_001",
            timestamp="2025-01-27T10:00:00",
            trigger="manual",
            snapshot_id="snapshot_001",
            files_restored=["file1.txt"],
            success=True,
            error_message=None,
            execution_time_seconds=1.0
        )
        
        data = operation.to_dict()
        
        assert isinstance(data, dict)
        assert data["operation_id"] == "rollback_001"
        assert data["timestamp"] == "2025-01-27T10:00:00"
        assert data["trigger"] == "manual"
        assert data["snapshot_id"] == "snapshot_001"
        assert data["files_restored"] == ["file1.txt"]
        assert data["success"] == True
        assert data["error_message"] is None
        assert data["execution_time_seconds"] == 1.0

class TestRollbackSystemIntegration:
    """
    Testes de integração para RollbackSystem.
    
    Testa cenários mais complexos e interações entre componentes.
    """
    
    @pytest.fixture
    def integration_system(self, temp_backup_dir):
        """Cria sistema de rollback para testes de integração."""
        return RollbackSystem(
            backup_dir=temp_backup_dir,
            max_snapshots=3,
            max_age_hours=1,  # Snapshots expiram rapidamente para testes
            auto_rollback_on_divergence=True
        )
    
    def test_full_workflow_with_multiple_snapshots(self, integration_system, sample_files):
        """Testa workflow completo com múltiplos snapshots."""
        # Criar snapshots sequenciais
        snapshots = []
        for index in range(3):
            snapshot = integration_system.create_snapshot(sample_files, f"Snapshot {index}")
            snapshots.append(snapshot)
        
        # Verificar que apenas os snapshots mais recentes foram mantidos
        assert len(integration_system.snapshots) == 3
        
        # Modificar arquivos
        for file_path in sample_files:
            with open(file_path, 'w') as f:
                f.write(f"Conteúdo modificado {datetime.utcnow()}")
        
        # Fazer rollback para snapshot intermediário
        middle_snapshot = snapshots[1]
        operation = integration_system.restore_snapshot(middle_snapshot.snapshot_id, "manual")
        
        # Verificar que rollback foi bem-sucedido
        assert operation.success == True
        assert operation.snapshot_id == middle_snapshot.snapshot_id
        
        # Verificar que arquivos foram restaurados
        for file_path in sample_files:
            with open(file_path, 'r') as f:
                content = f.read()
                assert "Conteúdo modificado" not in content
                assert "Conteúdo do arquivo" in content
    
    def test_error_recovery_scenarios(self, integration_system, sample_files):
        """Testa cenários de recuperação de erro."""
        # Criar snapshot inicial
        snapshot = integration_system.create_snapshot(sample_files, "Snapshot inicial")
        
        # Simular erro durante rollback (arquivo não encontrado)
        with patch.object(integration_system, '_backup_file', side_effect=Exception("Erro simulado")):
            with pytest.raises(Exception):
                integration_system.create_snapshot(sample_files, "Snapshot com erro")
        
        # Verificar que snapshot original ainda existe
        assert snapshot.snapshot_id in integration_system.snapshots
        assert Path(snapshot.backup_path).exists()
        
        # Verificar que rollback ainda funciona
        operation = integration_system.restore_snapshot(snapshot.snapshot_id, "manual")
        assert operation.success == True

if __name__ == "__main__":
    pytest.main([__file__]) 