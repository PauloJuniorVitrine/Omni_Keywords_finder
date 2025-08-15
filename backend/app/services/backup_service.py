"""
Serviço de Backup Robusto
=========================

Sistema de backup integrado ao Omni Keywords Finder com
backup automático, recuperação e validação de integridade.

Tracing ID: BACKUP_SERVICE_001
Data: 2024-12-27
Autor: Sistema de Backup
"""

import os
import shutil
import sqlite3
import hashlib
import datetime
import logging
import json
import zipfile
import schedule
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import psutil

from sqlalchemy.orm import Session
from ..models.prompt_system import LogOperacao

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BackupMetadata:
    """Metadados do backup"""
    backup_id: str
    timestamp: str
    size_bytes: int
    file_count: int
    checksum: str
    compression_ratio: float
    status: str
    backup_type: str
    error_message: Optional[str] = None


class BackupService:
    """Serviço principal de backup"""
    
    def __init__(self, db: Session):
        self.db = db
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurações
        self.config = {
            'retention_days': 30,
            'compression_level': 9,
            'max_backup_size_mb': 500,
            'backup_schedule': '02:00',
            'critical_files': [
                'backend/db.sqlite3',
                'backend/instance/db.sqlite3',
                'instance/db.sqlite3',
                'blogs/',
                'logs/',
                'uploads/',
                'relatorio_performance.json',
                'docs/relatorio_negocio.html',
                '.env',
                'env.example'
            ],
            'exclude_patterns': [
                '__pycache__',
                '.git',
                'node_modules',
                '*.tmp',
                '*.log',
                'backups/',
                'coverage/',
                'htmlcov/',
                'cypress/screenshots/'
            ]
        }
        
        self.backup_history: List[BackupMetadata] = []
        self.scheduler_thread: Optional[threading.Thread] = None
        self.running = False
        
        self._load_backup_history()
    
    def _load_backup_history(self):
        """Carrega histórico de backups"""
        try:
            metadata_file = self.backup_dir / 'backup_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    self.backup_history = [BackupMetadata(**item) for item in data]
            
            logger.info(f"Carregados {len(self.backup_history)} backups do histórico")
            
        except Exception as e:
            logger.error(f"Erro ao carregar histórico: {str(e)}")
    
    def _save_backup_history(self):
        """Salva histórico de backups"""
        try:
            metadata_file = self.backup_dir / 'backup_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump([vars(metadata) for metadata in self.backup_history], f, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {str(e)}")
    
    def _should_exclude(self, path: str) -> bool:
        """Verifica se arquivo/diretório deve ser excluído"""
        for pattern in self.config['exclude_patterns']:
            if pattern in path:
                return True
        return False
    
    def _get_files_to_backup(self) -> List[str]:
        """Obtém lista de arquivos para backup"""
        files_to_backup = []
        
        for item in self.config['critical_files']:
            if os.path.exists(item):
                if os.path.isfile(item):
                    files_to_backup.append(item)
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        # Filtrar diretórios excluídos
                        dirs[:] = [data for data in dirs if not self._should_exclude(os.path.join(root, data))]
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            if not self._should_exclude(file_path):
                                files_to_backup.append(file_path)
        
        logger.info(f"Encontrados {len(files_to_backup)} arquivos para backup")
        return files_to_backup
    
    def _create_backup_filename(self, backup_type: str = "auto") -> str:
        """Cria nome único para o arquivo de backup"""
        timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        return f"backup_{backup_type}_{timestamp}.zip"
    
    def _backup_database(self) -> bool:
        """Faz backup do banco de dados"""
        try:
            db_paths = ['backend/db.sqlite3', 'backend/instance/db.sqlite3', 'instance/db.sqlite3']
            
            for db_path in db_paths:
                if os.path.exists(db_path):
                    backup_path = f"{db_path}.backup"
                    
                    # Fazer backup usando SQLite
                    with sqlite3.connect(db_path) as conn:
                        backup_conn = sqlite3.connect(backup_path)
                        conn.backup(backup_conn)
                        backup_conn.close()
                    
                    logger.info(f"Backup do banco criado: {db_path} -> {backup_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no backup do banco: {str(e)}")
            return False
    
    def _compress_files(self, files: List[str], backup_path: str) -> Tuple[int, float]:
        """Comprime arquivos em ZIP"""
        total_size = 0
        original_size = 0
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, 
                           compresslevel=self.config['compression_level']) as zipf:
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        original_size += file_size
                        
                        # Adicionar ao ZIP
                        zipf.write(file_path, file_path)
                        total_size += file_size
                        
                except Exception as e:
                    logger.warning(f"Erro ao adicionar arquivo {file_path}: {str(e)}")
        
        compression_ratio = (1 - (total_size / original_size)) * 100 if original_size > 0 else 0
        return total_size, compression_ratio
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcula checksum do arquivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _validate_backup_integrity(self, backup_path: str, metadata: BackupMetadata) -> bool:
        """Valida integridade do backup"""
        try:
            # Verificar se arquivo existe
            if not os.path.exists(backup_path):
                return False
            
            # Verificar tamanho
            actual_size = os.path.getsize(backup_path)
            if actual_size != metadata.size_bytes:
                logger.warning(f"Tamanho do backup não confere: esperado {metadata.size_bytes}, atual {actual_size}")
                return False
            
            # Verificar checksum
            actual_checksum = self._calculate_checksum(backup_path)
            if actual_checksum != metadata.checksum:
                logger.warning(f"Checksum do backup não confere")
                return False
            
            # Verificar se ZIP é válido
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.testzip()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de integridade: {str(e)}")
            return False
    
    def create_backup(self, backup_type: str = "manual") -> Optional[BackupMetadata]:
        """Cria backup completo do sistema"""
        try:
            logger.info(f"Iniciando backup {backup_type}...")
            
            # Verificar espaço em disco
            disk_usage = psutil.disk_usage('.')
            if disk_usage.free < self.config['max_backup_size_mb'] * 1024 * 1024:
                error_msg = "Espaço insuficiente em disco para backup"
                logger.error(error_msg)
                return BackupMetadata(
                    backup_id=f"failed_{int(time.time())}",
                    timestamp=datetime.datetime.now().isoformat(),
                    size_bytes=0,
                    file_count=0,
                    checksum="",
                    compression_ratio=0,
                    status='failed',
                    backup_type=backup_type,
                    error_message=error_msg
                )
            
            # Obter arquivos para backup
            files_to_backup = self._get_files_to_backup()
            if not files_to_backup:
                error_msg = "Nenhum arquivo encontrado para backup"
                logger.warning(error_msg)
                return BackupMetadata(
                    backup_id=f"failed_{int(time.time())}",
                    timestamp=datetime.datetime.now().isoformat(),
                    size_bytes=0,
                    file_count=0,
                    checksum="",
                    compression_ratio=0,
                    status='failed',
                    backup_type=backup_type,
                    error_message=error_msg
                )
            
            # Criar nome do arquivo de backup
            backup_filename = self._create_backup_filename(backup_type)
            backup_path = self.backup_dir / backup_filename
            
            # Fazer backup do banco de dados primeiro
            if not self._backup_database():
                error_msg = "Falha no backup do banco de dados"
                logger.error(error_msg)
                return BackupMetadata(
                    backup_id=f"failed_{int(time.time())}",
                    timestamp=datetime.datetime.now().isoformat(),
                    size_bytes=0,
                    file_count=0,
                    checksum="",
                    compression_ratio=0,
                    status='failed',
                    backup_type=backup_type,
                    error_message=error_msg
                )
            
            # Adicionar backups do banco à lista
            for db_path in ['backend/db.sqlite3', 'backend/instance/db.sqlite3', 'instance/db.sqlite3']:
                backup_db_path = f"{db_path}.backup"
                if os.path.exists(backup_db_path):
                    files_to_backup.append(backup_db_path)
            
            # Comprimir arquivos
            start_time = time.time()
            total_size, compression_ratio = self._compress_files(files_to_backup, str(backup_path))
            compression_time = time.time() - start_time
            
            # Calcular checksum
            checksum = self._calculate_checksum(str(backup_path))
            
            # Criar metadados
            metadata = BackupMetadata(
                backup_id=backup_filename.replace('.zip', ''),
                timestamp=datetime.datetime.now().isoformat(),
                size_bytes=os.path.getsize(backup_path),
                file_count=len(files_to_backup),
                checksum=checksum,
                compression_ratio=compression_ratio,
                status='completed',
                backup_type=backup_type
            )
            
            # Validar integridade
            if not self._validate_backup_integrity(str(backup_path), metadata):
                metadata.status = 'failed'
                metadata.error_message = 'Falha na validação de integridade'
                logger.error("Backup falhou na validação de integridade")
                return metadata
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            # Salvar metadados
            self.backup_history.append(metadata)
            self._save_backup_history()
            
            # Limpar backups temporários do banco
            for db_backup in [f for f in files_to_backup if f.endswith('.backup')]:
                try:
                    os.remove(db_backup)
                except:
                    pass
            
            # Log da operação
            self._log_backup_operation("create", metadata)
            
            logger.info(f"Backup concluído com sucesso: {backup_filename}")
            logger.info(f"Tamanho: {metadata.size_bytes / 1024 / 1024:.2f} MB")
            logger.info(f"Compressão: {compression_ratio:.1f}%")
            logger.info(f"Tempo: {compression_time:.2f}string_data")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Erro durante backup: {str(e)}")
            return BackupMetadata(
                backup_id=f"failed_{int(time.time())}",
                timestamp=datetime.datetime.now().isoformat(),
                size_bytes=0,
                file_count=0,
                checksum="",
                compression_ratio=0,
                status='failed',
                backup_type=backup_type,
                error_message=str(e)
            )
    
    def _cleanup_old_backups(self):
        """Remove backups antigos baseado na política de retenção"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.config['retention_days'])
        
        for backup_file in self.backup_dir.glob('backup_*.zip'):
            try:
                file_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"Backup antigo removido: {backup_file.name}")
            except Exception as e:
                logger.error(f"Erro ao remover backup antigo {backup_file}: {str(e)}")
    
    def restore_backup(self, backup_filename: str, target_dir: str = '.') -> bool:
        """Restaura backup específico"""
        try:
            backup_path = self.backup_dir / backup_filename
            if not backup_path.exists():
                logger.error(f"Backup não encontrado: {backup_filename}")
                return False
            
            # Encontrar metadados
            metadata = next((m for m in self.backup_history if m.backup_id in backup_filename), None)
            if metadata and not self._validate_backup_integrity(str(backup_path), metadata):
                logger.error("Backup corrompido, não é seguro restaurar")
                return False
            
            # Fazer backup do estado atual antes da restauração
            current_backup = self.create_backup("pre_restore")
            if current_backup and current_backup.status == 'failed':
                logger.warning("Não foi possível fazer backup do estado atual")
            
            # Restaurar arquivos
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(target_dir)
            
            # Restaurar banco de dados se necessário
            for db_backup in zipf.namelist():
                if db_backup.endswith('.backup'):
                    original_db = db_backup.replace('.backup', '')
                    if os.path.exists(db_backup):
                        shutil.move(db_backup, original_db)
                        logger.info(f"Banco restaurado: {original_db}")
            
            # Log da operação
            self._log_backup_operation("restore", metadata)
            
            logger.info(f"Restauração concluída: {backup_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Erro durante restauração: {str(e)}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """Lista todos os backups disponíveis"""
        backups = []
        for backup_file in sorted(self.backup_dir.glob('backup_*.zip'), reverse=True):
            try:
                stat = backup_file.stat()
                metadata = next((m for m in self.backup_history if m.backup_id in backup_file.name), None)
                
                backup_info = {
                    'filename': backup_file.name,
                    'size_mb': stat.st_size / 1024 / 1024,
                    'created': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'status': metadata.status if metadata else 'unknown',
                    'file_count': metadata.file_count if metadata else 0,
                    'compression_ratio': metadata.compression_ratio if metadata else 0,
                    'backup_type': metadata.backup_type if metadata else 'unknown'
                }
                backups.append(backup_info)
                
            except Exception as e:
                logger.error(f"Erro ao obter informações do backup {backup_file}: {str(e)}")
        
        return backups
    
    def start_scheduled_backup(self):
        """Inicia backup agendado"""
        schedule.every().day.at(self.config['backup_schedule']).do(self.create_backup, "scheduled")
        
        logger.info(f"Backup agendado para {self.config['backup_schedule']} diariamente")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    
    def start_backup_daemon(self):
        """Inicia daemon de backup em thread separada"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Daemon de backup já está rodando")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self.start_scheduled_backup, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Daemon de backup iniciado")
    
    def stop_backup_daemon(self):
        """Para o daemon de backup"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Daemon de backup parado")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de backup"""
        total_backups = len(self.backup_history)
        successful_backups = len([b for b in self.backup_history if b.status == 'completed'])
        failed_backups = len([b for b in self.backup_history if b.status == 'failed'])
        
        total_size_mb = sum(b.size_bytes for b in self.backup_history) / 1024 / 1024
        avg_compression = sum(b.compression_ratio for b in self.backup_history) / total_backups if total_backups > 0 else 0
        
        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "success_rate": successful_backups / total_backups if total_backups > 0 else 0,
            "total_size_mb": total_size_mb,
            "average_compression_ratio": avg_compression,
            "daemon_running": self.running
        }
    
    def _log_backup_operation(self, operation: str, metadata: BackupMetadata):
        """Registra log de operação de backup"""
        try:
            log_entry = LogOperacao(
                operacao=f"backup_{operation}",
                detalhes=json.dumps({
                    "backup_id": metadata.backup_id,
                    "backup_type": metadata.backup_type,
                    "size_bytes": metadata.size_bytes,
                    "file_count": metadata.file_count,
                    "status": metadata.status,
                    "timestamp": metadata.timestamp
                }),
                timestamp=datetime.datetime.utcnow()
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar log: {str(e)}") 