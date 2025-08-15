"""
Sistema de Rollback Automático para Documentação Enterprise
Tracing ID: ROLLBACK_SYSTEM_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa o sistema de rollback automático para documentação,
permitindo reverter mudanças quando divergências são detectadas,
seguindo padrões enterprise de segurança e confiabilidade.
"""

import os
import json
import shutil
import hashlib
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
import tempfile
import zipfile
import tarfile

from shared.logger import logger
from shared.config import BASE_DIR

@dataclass
class BackupSnapshot:
    """
    Snapshot de backup para rollback.
    
    Implementa estrutura de dados imutável para garantir
    integridade dos snapshots de backup.
    """
    snapshot_id: str
    timestamp: str
    description: str
    files_backed_up: List[str]
    total_size_bytes: int
    checksum: str
    metadata: Dict[str, Any]
    backup_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return asdict(self)
    
    def is_valid(self, max_age_hours: int = 24) -> bool:
        """
        Verifica se o snapshot ainda é válido.
        
        Args:
            max_age_hours: Idade máxima em horas
            
        Returns:
            True se válido, False caso contrário
        """
        snapshot_time = datetime.fromisoformat(self.timestamp)
        age_hours = (datetime.utcnow() - snapshot_time).total_seconds() / 3600
        return age_hours <= max_age_hours

@dataclass
class RollbackOperation:
    """
    Operação de rollback.
    
    Registra detalhes de uma operação de rollback para auditoria.
    """
    operation_id: str
    timestamp: str
    trigger: str  # 'manual', 'automatic', 'divergence_detected'
    snapshot_id: str
    files_restored: List[str]
    success: bool
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return asdict(self)

class RollbackSystem:
    """
    Sistema de rollback automático para documentação.
    
    Implementa funcionalidades de:
    - Criação de snapshots automáticos
    - Detecção de divergências
    - Rollback automático/manual
    - Auditoria de operações
    - Limpeza de snapshots antigos
    """
    
    def __init__(self, 
                 backup_dir: Optional[str] = None,
                 max_snapshots: int = 10,
                 max_age_hours: int = 24,
                 auto_rollback_on_divergence: bool = True):
        """
        Inicializa o sistema de rollback.
        
        Args:
            backup_dir: Diretório para armazenar snapshots
            max_snapshots: Número máximo de snapshots mantidos
            max_age_hours: Idade máxima dos snapshots em horas
            auto_rollback_on_divergence: Se deve fazer rollback automático
        """
        self.backup_dir = backup_dir or str(BASE_DIR / "infrastructure" / "backup" / "snapshots")
        self.max_snapshots = max_snapshots
        self.max_age_hours = max_age_hours
        self.auto_rollback_on_divergence = auto_rollback_on_divergence
        self.snapshots: Dict[str, BackupSnapshot] = {}
        self.rollback_history: List[RollbackOperation] = []
        
        # Criar diretório de backup se não existir
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Carregar snapshots existentes
        self._load_existing_snapshots()
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "rollback_system_initialized",
            "status": "success",
            "source": "RollbackSystem.__init__",
            "details": {
                "backup_dir": self.backup_dir,
                "max_snapshots": self.max_snapshots,
                "max_age_hours": self.max_age_hours,
                "auto_rollback": auto_rollback_on_divergence,
                "existing_snapshots": len(self.snapshots)
            }
        })
    
    def _load_existing_snapshots(self) -> None:
        """
        Carrega snapshots existentes do disco.
        """
        try:
            metadata_file = Path(self.backup_dir) / "snapshots_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    
                for snapshot_data in data.get('snapshots', []):
                    snapshot = BackupSnapshot(**snapshot_data)
                    if snapshot.is_valid(self.max_age_hours):
                        self.snapshots[snapshot.snapshot_id] = snapshot
                    else:
                        # Remover snapshot expirado
                        self._remove_snapshot_files(snapshot)
                
                logger.info({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "existing_snapshots_loaded",
                    "status": "success",
                    "source": "RollbackSystem._load_existing_snapshots",
                    "details": {"snapshots_loaded": len(self.snapshots)}
                })
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "snapshots_load_failed",
                "status": "error",
                "source": "RollbackSystem._load_existing_snapshots",
                "details": {"error": str(e)}
            })
    
    def _save_snapshots_metadata(self) -> None:
        """
        Salva metadados dos snapshots em arquivo.
        """
        try:
            metadata_file = Path(self.backup_dir) / "snapshots_metadata.json"
            data = {
                "last_updated": datetime.utcnow().isoformat(),
                "snapshots": [snapshot.to_dict() for snapshot in self.snapshots.values()]
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "snapshots_metadata_save_failed",
                "status": "error",
                "source": "RollbackSystem._save_snapshots_metadata",
                "details": {"error": str(e)}
            })
    
    def _generate_snapshot_id(self, description: str) -> str:
        """
        Gera ID único para snapshot.
        
        Args:
            description: Descrição do snapshot
            
        Returns:
            ID único do snapshot
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        description_hash = hashlib.md5(description.encode()).hexdigest()[:8]
        return f"snapshot_{timestamp}_{description_hash}"
    
    def _calculate_checksum(self, file_path: str) -> str:
        """
        Calcula checksum SHA-256 de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Checksum SHA-256
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _backup_file(self, source_path: str, backup_path: str) -> Tuple[int, str]:
        """
        Faz backup de um arquivo.
        
        Args:
            source_path: Caminho do arquivo original
            backup_path: Caminho do backup
            
        Returns:
            Tupla (tamanho_bytes, checksum)
        """
        # Criar diretório de destino se não existir
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar arquivo
        shutil.copy2(source_path, backup_path)
        
        # Calcular tamanho e checksum
        file_size = os.path.getsize(backup_path)
        checksum = self._calculate_checksum(backup_path)
        
        return file_size, checksum
    
    def create_snapshot(self, 
                       files_to_backup: List[str],
                       description: str = "Backup automático") -> BackupSnapshot:
        """
        Cria um novo snapshot de backup.
        
        Args:
            files_to_backup: Lista de arquivos para fazer backup
            description: Descrição do snapshot
            
        Returns:
            Snapshot criado
            
        Raises:
            FileNotFoundError: Se algum arquivo não for encontrado
            ValueError: Se lista de arquivos estiver vazia
        """
        if not files_to_backup:
            raise ValueError("Lista de arquivos para backup não pode estar vazia")
        
        start_time = datetime.utcnow()
        snapshot_id = self._generate_snapshot_id(description)
        snapshot_dir = Path(self.backup_dir) / snapshot_id
        
        # Criar diretório do snapshot
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        files_backed_up = []
        total_size = 0
        checksums = []
        
        try:
            # Fazer backup de cada arquivo
            for file_path in files_to_backup:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
                
                # Determinar caminho de destino no backup
                relative_path = os.path.relpath(file_path, BASE_DIR)
                backup_path = snapshot_dir / relative_path
                
                # Fazer backup
                file_size, checksum = self._backup_file(file_path, str(backup_path))
                
                files_backed_up.append(relative_path)
                total_size += file_size
                checksums.append(checksum)
            
            # Calcular checksum total do snapshot
            total_checksum = hashlib.sha256(''.join(checksums).encode()).hexdigest()
            
            # Criar snapshot
            snapshot = BackupSnapshot(
                snapshot_id=snapshot_id,
                timestamp=datetime.utcnow().isoformat(),
                description=description,
                files_backed_up=files_backed_up,
                total_size_bytes=total_size,
                checksum=total_checksum,
                metadata={
                    "source_files": files_to_backup,
                    "checksums": dict(zip(files_backed_up, checksums)),
                    "creation_time_seconds": (datetime.utcnow() - start_time).total_seconds()
                },
                backup_path=str(snapshot_dir)
            )
            
            # Adicionar ao dicionário de snapshots
            self.snapshots[snapshot_id] = snapshot
            
            # Salvar metadados
            self._save_snapshots_metadata()
            
            # Limpar snapshots antigos se necessário
            self._cleanup_old_snapshots()
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "snapshot_created",
                "status": "success",
                "source": "RollbackSystem.create_snapshot",
                "details": {
                    "snapshot_id": snapshot_id,
                    "description": description,
                    "files_backed_up": len(files_backed_up),
                    "total_size_bytes": total_size,
                    "creation_time_seconds": (datetime.utcnow() - start_time).total_seconds()
                }
            })
            
            return snapshot
            
        except Exception as e:
            # Limpar snapshot parcial em caso de erro
            if snapshot_dir.exists():
                shutil.rmtree(snapshot_dir)
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "snapshot_creation_failed",
                "status": "error",
                "source": "RollbackSystem.create_snapshot",
                "details": {
                    "snapshot_id": snapshot_id,
                    "error": str(e),
                    "files_to_backup": files_to_backup
                }
            })
            raise
    
    def _remove_snapshot_files(self, snapshot: BackupSnapshot) -> None:
        """
        Remove arquivos de um snapshot.
        
        Args:
            snapshot: Snapshot a ser removido
        """
        try:
            snapshot_path = Path(snapshot.backup_path)
            if snapshot_path.exists():
                shutil.rmtree(snapshot_path)
                
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "snapshot_files_removed",
                "status": "success",
                "source": "RollbackSystem._remove_snapshot_files",
                "details": {"snapshot_id": snapshot.snapshot_id}
            })
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "snapshot_files_removal_failed",
                "status": "error",
                "source": "RollbackSystem._remove_snapshot_files",
                "details": {
                    "snapshot_id": snapshot.snapshot_id,
                    "error": str(e)
                }
            })
    
    def _cleanup_old_snapshots(self) -> None:
        """
        Remove snapshots antigos e excedentes.
        """
        # Ordenar snapshots por timestamp (mais antigos primeiro)
        sorted_snapshots = sorted(
            self.snapshots.values(),
            key=lambda string_data: datetime.fromisoformat(string_data.timestamp)
        )
        
        # Remover snapshots excedentes
        while len(sorted_snapshots) > self.max_snapshots:
            oldest_snapshot = sorted_snapshots.pop(0)
            self._remove_snapshot_files(oldest_snapshot)
            del self.snapshots[oldest_snapshot.snapshot_id]
        
        # Remover snapshots expirados
        current_time = datetime.utcnow()
        expired_snapshots = []
        
        for snapshot in self.snapshots.values():
            snapshot_time = datetime.fromisoformat(snapshot.timestamp)
            age_hours = (current_time - snapshot_time).total_seconds() / 3600
            
            if age_hours > self.max_age_hours:
                expired_snapshots.append(snapshot)
        
        for snapshot in expired_snapshots:
            self._remove_snapshot_files(snapshot)
            del self.snapshots[snapshot.snapshot_id]
        
        if expired_snapshots:
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "old_snapshots_cleaned",
                "status": "success",
                "source": "RollbackSystem._cleanup_old_snapshots",
                "details": {
                    "removed_count": len(expired_snapshots),
                    "remaining_count": len(self.snapshots)
                }
            })
    
    def restore_snapshot(self, 
                        snapshot_id: str,
                        trigger: str = "manual") -> RollbackOperation:
        """
        Restaura um snapshot específico.
        
        Args:
            snapshot_id: ID do snapshot para restaurar
            trigger: Gatilho da operação ('manual', 'automatic', 'divergence_detected')
            
        Returns:
            Operação de rollback
            
        Raises:
            KeyError: Se snapshot não for encontrado
            ValueError: Se snapshot não for válido
        """
        if snapshot_id not in self.snapshots:
            raise KeyError(f"Snapshot não encontrado: {snapshot_id}")
        
        snapshot = self.snapshots[snapshot_id]
        if not snapshot.is_valid(self.max_age_hours):
            raise ValueError(f"Snapshot expirado: {snapshot_id}")
        
        start_time = datetime.utcnow()
        operation_id = f"rollback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        files_restored = []
        success = False
        error_message = None
        
        try:
            # Restaurar cada arquivo do snapshot
            for relative_path in snapshot.files_backed_up:
                backup_path = Path(snapshot.backup_path) / relative_path
                target_path = BASE_DIR / relative_path
                
                if backup_path.exists():
                    # Criar diretório de destino se não existir
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Restaurar arquivo
                    shutil.copy2(str(backup_path), str(target_path))
                    files_restored.append(relative_path)
                else:
                    logger.warning({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "backup_file_not_found",
                        "status": "warning",
                        "source": "RollbackSystem.restore_snapshot",
                        "details": {
                            "backup_path": str(backup_path),
                            "relative_path": relative_path
                        }
                    })
            
            success = True
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "snapshot_restored",
                "status": "success",
                "source": "RollbackSystem.restore_snapshot",
                "details": {
                    "snapshot_id": snapshot_id,
                    "trigger": trigger,
                    "files_restored": len(files_restored),
                    "execution_time_seconds": execution_time
                }
            })
            
        except Exception as e:
            success = False
            error_message = str(e)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "snapshot_restore_failed",
                "status": "error",
                "source": "RollbackSystem.restore_snapshot",
                "details": {
                    "snapshot_id": snapshot_id,
                    "trigger": trigger,
                    "error": str(e),
                    "execution_time_seconds": execution_time
                }
            })
        
        # Criar operação de rollback
        operation = RollbackOperation(
            operation_id=operation_id,
            timestamp=datetime.utcnow().isoformat(),
            trigger=trigger,
            snapshot_id=snapshot_id,
            files_restored=files_restored,
            success=success,
            error_message=error_message,
            execution_time_seconds=execution_time
        )
        
        # Adicionar ao histórico
        self.rollback_history.append(operation)
        
        return operation
    
    def detect_divergence_and_rollback(self, 
                                     current_files: List[str],
                                     expected_checksums: Dict[str, str]) -> Optional[RollbackOperation]:
        """
        Detecta divergências e faz rollback automático se configurado.
        
        Args:
            current_files: Lista de arquivos atuais
            expected_checksums: Checksums esperados dos arquivos
            
        Returns:
            Operação de rollback se realizada, None caso contrário
        """
        divergences = []
        
        # Verificar divergências
        for file_path in current_files:
            if file_path in expected_checksums:
                try:
                    current_checksum = self._calculate_checksum(file_path)
                    expected_checksum = expected_checksums[file_path]
                    
                    if current_checksum != expected_checksum:
                        divergences.append({
                            "file": file_path,
                            "expected": expected_checksum,
                            "current": current_checksum
                        })
                except FileNotFoundError:
                    divergences.append({
                        "file": file_path,
                        "error": "Arquivo não encontrado"
                    })
        
        if divergences:
            logger.warning({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "divergences_detected",
                "status": "warning",
                "source": "RollbackSystem.detect_divergence_and_rollback",
                "details": {
                    "divergences_count": len(divergences),
                    "divergences": divergences
                }
            })
            
            # Fazer rollback automático se configurado
            if self.auto_rollback_on_divergence and self.snapshots:
                # Usar snapshot mais recente
                latest_snapshot = max(
                    self.snapshots.values(),
                    key=lambda string_data: datetime.fromisoformat(string_data.timestamp)
                )
                
                logger.info({
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "auto_rollback_triggered",
                    "status": "info",
                    "source": "RollbackSystem.detect_divergence_and_rollback",
                    "details": {
                        "snapshot_id": latest_snapshot.snapshot_id,
                        "divergences_count": len(divergences)
                    }
                })
                
                return self.restore_snapshot(
                    latest_snapshot.snapshot_id,
                    trigger="divergence_detected"
                )
        
        return None
    
    def get_snapshot_info(self, snapshot_id: str) -> Optional[BackupSnapshot]:
        """
        Retorna informações de um snapshot específico.
        
        Args:
            snapshot_id: ID do snapshot
            
        Returns:
            Snapshot se encontrado, None caso contrário
        """
        return self.snapshots.get(snapshot_id)
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """
        Lista todos os snapshots disponíveis.
        
        Returns:
            Lista de informações dos snapshots
        """
        snapshots_info = []
        
        for snapshot in self.snapshots.values():
            snapshot_time = datetime.fromisoformat(snapshot.timestamp)
            age_hours = (datetime.utcnow() - snapshot_time).total_seconds() / 3600
            
            snapshots_info.append({
                "snapshot_id": snapshot.snapshot_id,
                "timestamp": snapshot.timestamp,
                "description": snapshot.description,
                "files_count": len(snapshot.files_backed_up),
                "total_size_mb": snapshot.total_size_bytes / (1024 * 1024),
                "age_hours": age_hours,
                "is_valid": snapshot.is_valid(self.max_age_hours)
            })
        
        # Ordenar por timestamp (mais recentes primeiro)
        snapshots_info.sort(key=lambda value: value["timestamp"], reverse=True)
        
        return snapshots_info
    
    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """
        Retorna histórico de operações de rollback.
        
        Returns:
            Lista de operações de rollback
        """
        return [operation.to_dict() for operation in self.rollback_history]
    
    def export_snapshot(self, 
                       snapshot_id: str, 
                       export_path: str,
                       format: str = "zip") -> str:
        """
        Exporta um snapshot para arquivo compactado.
        
        Args:
            snapshot_id: ID do snapshot
            export_path: Caminho do arquivo de exportação
            format: Formato de exportação ('zip' ou 'tar')
            
        Returns:
            Caminho do arquivo exportado
            
        Raises:
            KeyError: Se snapshot não for encontrado
        """
        if snapshot_id not in self.snapshots:
            raise KeyError(f"Snapshot não encontrado: {snapshot_id}")
        
        snapshot = self.snapshots[snapshot_id]
        snapshot_path = Path(snapshot.backup_path)
        
        if format.lower() == "zip":
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in snapshot_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(snapshot_path)
                        zipf.write(file_path, arcname)
        elif format.lower() == "tar":
            with tarfile.open(export_path, 'w:gz') as tarf:
                tarf.add(snapshot_path, arcname=snapshot_id)
        else:
            raise ValueError(f"Formato não suportado: {format}")
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "snapshot_exported",
            "status": "success",
            "source": "RollbackSystem.export_snapshot",
            "details": {
                "snapshot_id": snapshot_id,
                "export_path": export_path,
                "format": format
            }
        })
        
        return export_path 