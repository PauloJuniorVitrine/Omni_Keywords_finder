"""
Sistema de Backup e Recuperação Automática - Omni Keywords Finder

Funcionalidades:
- Backup automático diário
- Retenção de 30 dias
- Compressão de backups
- Sistema de recuperação automática
- Validação de integridade
- Testes de backup/restore

Autor: Sistema de Backup Automático
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
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

# Configurações
BACKUP_CONFIG = {
    'backup_dir': 'backups',
    'retention_days': 30,
    'compression_level': 9,
    'max_backup_size_mb': 500,
    'backup_schedule': '02:00',  # 2 AM
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

@dataclass
class BackupMetadata:
    """Metadados do backup para validação e rastreabilidade"""
    backup_id: str
    timestamp: str
    size_bytes: int
    file_count: int
    checksum: str
    compression_ratio: float
    status: str
    error_message: Optional[str] = None

class BackupIntegrityValidator:
    """Validador de integridade dos backups"""
    
    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        """Calcula checksum SHA-256 do arquivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def validate_backup_integrity(backup_path: str, metadata: BackupMetadata) -> bool:
        """Valida integridade do backup"""
        try:
            # Verificar se arquivo existe
            if not os.path.exists(backup_path):
                logging.error(f"Backup não encontrado: {backup_path}")
                return False
            
            # Verificar tamanho
            actual_size = os.path.getsize(backup_path)
            if actual_size != metadata.size_bytes:
                logging.error(f"Tamanho do backup incorreto: esperado {metadata.size_bytes}, atual {actual_size}")
                return False
            
            # Verificar checksum
            actual_checksum = BackupIntegrityValidator.calculate_checksum(backup_path)
            if actual_checksum != metadata.checksum:
                logging.error(f"Checksum do backup incorreto: esperado {metadata.checksum}, atual {actual_checksum}")
                return False
            
            # Verificar se é um arquivo ZIP válido
            try:
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    zip_file.testzip()
            except zipfile.BadZipFile:
                logging.error(f"Arquivo ZIP corrompido: {backup_path}")
                return False
            
            logging.info(f"Backup validado com sucesso: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"Erro na validação do backup {backup_path}: {str(e)}")
            return False

class DatabaseBackupManager:
    """Gerenciador específico para backup de banco de dados"""
    
    @staticmethod
    def backup_sqlite_database(db_path: str, backup_path: str) -> bool:
        """Faz backup seguro do banco SQLite"""
        try:
            # Verificar se banco existe
            if not os.path.exists(db_path):
                logging.warning(f"Banco de dados não encontrado: {db_path}")
                return False
            
            # Criar backup usando SQLite
            with sqlite3.connect(db_path) as source_conn:
                with sqlite3.connect(backup_path) as backup_conn:
                    source_conn.backup(backup_conn)
            
            logging.info(f"Backup do banco criado: {db_path} -> {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"Erro no backup do banco {db_path}: {str(e)}")
            return False
    
    @staticmethod
    def validate_database_backup(backup_path: str) -> bool:
        """Valida backup do banco de dados"""
        try:
            with sqlite3.connect(backup_path) as conn:
                # Verificar se consegue conectar
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                if not tables:
                    logging.warning(f"Backup do banco não contém tabelas: {backup_path}")
                    return False
                
                logging.info(f"Backup do banco validado: {len(tables)} tabelas encontradas")
                return True
                
        except Exception as e:
            logging.error(f"Erro na validação do backup do banco {backup_path}: {str(e)}")
            return False

class AutoBackupSystem:
    """Sistema principal de backup automático"""
    
    def __init__(self):
        self.backup_dir = Path(BACKUP_CONFIG['backup_dir'])
        self.backup_dir.mkdir(exist_ok=True)
        self.metadata_file = self.backup_dir / 'backup_metadata.json'
        self.backup_history: List[BackupMetadata] = self._load_metadata()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para o sistema de backup"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)string_data [%(levelname)string_data] [AUTO_BACKUP] %(message)string_data',
            handlers=[
                logging.FileHandler(log_dir / 'auto_backup.log'),
                logging.StreamHandler()
            ]
        )
    
    def _load_metadata(self) -> List[BackupMetadata]:
        """Carrega metadados dos backups existentes"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    return [BackupMetadata(**item) for item in data]
            except Exception as e:
                logging.error(f"Erro ao carregar metadados: {str(e)}")
        return []
    
    def _save_metadata(self):
        """Salva metadados dos backups"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump([vars(metadata) for metadata in self.backup_history], f, indent=2)
        except Exception as e:
            logging.error(f"Erro ao salvar metadados: {str(e)}")
    
    def _should_exclude(self, path: str) -> bool:
        """Verifica se arquivo/diretório deve ser excluído do backup"""
        for pattern in BACKUP_CONFIG['exclude_patterns']:
            if pattern in path:
                return True
        return False
    
    def _get_files_to_backup(self) -> List[str]:
        """Obtém lista de arquivos para backup"""
        files_to_backup = []
        
        for item in BACKUP_CONFIG['critical_files']:
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
        
        logging.info(f"Encontrados {len(files_to_backup)} arquivos para backup")
        return files_to_backup
    
    def _create_backup_filename(self) -> str:
        """Cria nome único para o arquivo de backup"""
        timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        return f"backup_auto_{timestamp}.zip"
    
    def _compress_files(self, files: List[str], backup_path: str) -> Tuple[int, float]:
        """Comprime arquivos em ZIP com alta compressão"""
        total_size = 0
        original_size = 0
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=BACKUP_CONFIG['compression_level']) as zipf:
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        original_size += file_size
                        
                        # Adicionar ao ZIP
                        zipf.write(file_path, file_path)
                        total_size += file_size
                        
                except Exception as e:
                    logging.warning(f"Erro ao adicionar arquivo {file_path}: {str(e)}")
        
        compression_ratio = (1 - (total_size / original_size)) * 100 if original_size > 0 else 0
        return total_size, compression_ratio
    
    def create_backup(self) -> Optional[BackupMetadata]:
        """Cria backup completo do sistema"""
        try:
            logging.info("Iniciando backup automático...")
            
            # Verificar espaço em disco
            disk_usage = psutil.disk_usage('.')
            if disk_usage.free < BACKUP_CONFIG['max_backup_size_mb'] * 1024 * 1024:
                logging.error("Espaço insuficiente em disco para backup")
                return None
            
            # Obter arquivos para backup
            files_to_backup = self._get_files_to_backup()
            if not files_to_backup:
                logging.warning("Nenhum arquivo encontrado para backup")
                return None
            
            # Criar nome do arquivo de backup
            backup_filename = self._create_backup_filename()
            backup_path = self.backup_dir / backup_filename
            
            # Fazer backup do banco de dados primeiro
            db_backup_success = True
            for db_path in ['backend/db.sqlite3', 'backend/instance/db.sqlite3', 'instance/db.sqlite3']:
                if os.path.exists(db_path):
                    db_backup_path = f"{db_path}.backup"
                    if not DatabaseBackupManager.backup_sqlite_database(db_path, db_backup_path):
                        db_backup_success = False
                        break
                    files_to_backup.append(db_backup_path)
            
            if not db_backup_success:
                logging.error("Falha no backup do banco de dados")
                return None
            
            # Comprimir arquivos
            start_time = time.time()
            total_size, compression_ratio = self._compress_files(files_to_backup, str(backup_path))
            compression_time = time.time() - start_time
            
            # Calcular checksum
            checksum = BackupIntegrityValidator.calculate_checksum(str(backup_path))
            
            # Criar metadados
            metadata = BackupMetadata(
                backup_id=backup_filename.replace('.zip', ''),
                timestamp=datetime.datetime.now().isoformat(),
                size_bytes=os.path.getsize(backup_path),
                file_count=len(files_to_backup),
                checksum=checksum,
                compression_ratio=compression_ratio,
                status='completed'
            )
            
            # Validar integridade
            if not BackupIntegrityValidator.validate_backup_integrity(str(backup_path), metadata):
                metadata.status = 'failed'
                metadata.error_message = 'Falha na validação de integridade'
                logging.error("Backup falhou na validação de integridade")
                return metadata
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            # Salvar metadados
            self.backup_history.append(metadata)
            self._save_metadata()
            
            # Limpar backups temporários do banco
            for db_backup in [f for f in files_to_backup if f.endswith('.backup')]:
                try:
                    os.remove(db_backup)
                except:
                    pass
            
            logging.info(f"Backup concluído com sucesso: {backup_filename}")
            logging.info(f"Tamanho: {metadata.size_bytes / 1024 / 1024:.2f} MB")
            logging.info(f"Compressão: {compression_ratio:.1f}%")
            logging.info(f"Tempo: {compression_time:.2f}string_data")
            
            return metadata
            
        except Exception as e:
            logging.error(f"Erro durante backup: {str(e)}")
            return BackupMetadata(
                backup_id=f"failed_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}",
                timestamp=datetime.datetime.now().isoformat(),
                size_bytes=0,
                file_count=0,
                checksum="",
                compression_ratio=0,
                status='failed',
                error_message=str(e)
            )
    
    def _cleanup_old_backups(self):
        """Remove backups antigos baseado na política de retenção"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=BACKUP_CONFIG['retention_days'])
        
        for backup_file in self.backup_dir.glob('backup_auto_*.zip'):
            try:
                file_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    logging.info(f"Backup antigo removido: {backup_file.name}")
            except Exception as e:
                logging.error(f"Erro ao remover backup antigo {backup_file}: {str(e)}")
    
    def restore_backup(self, backup_filename: str, target_dir: str = '.') -> bool:
        """Restaura backup específico"""
        try:
            backup_path = self.backup_dir / backup_filename
            if not backup_path.exists():
                logging.error(f"Backup não encontrado: {backup_filename}")
                return False
            
            # Encontrar metadados
            metadata = next((m for m in self.backup_history if m.backup_id in backup_filename), None)
            if metadata and not BackupIntegrityValidator.validate_backup_integrity(str(backup_path), metadata):
                logging.error("Backup corrompido, não é seguro restaurar")
                return False
            
            # Fazer backup do estado atual antes da restauração
            current_backup = self.create_backup()
            if current_backup and current_backup.status == 'failed':
                logging.warning("Não foi possível fazer backup do estado atual")
            
            # Restaurar arquivos
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(target_dir)
            
            # Restaurar banco de dados se necessário
            for db_backup in zipf.namelist():
                if db_backup.endswith('.backup'):
                    original_db = db_backup.replace('.backup', '')
                    if os.path.exists(db_backup):
                        shutil.move(db_backup, original_db)
                        logging.info(f"Banco restaurado: {original_db}")
            
            logging.info(f"Restauração concluída: {backup_filename}")
            return True
            
        except Exception as e:
            logging.error(f"Erro durante restauração: {str(e)}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """Lista todos os backups disponíveis"""
        backups = []
        for backup_file in sorted(self.backup_dir.glob('backup_auto_*.zip'), reverse=True):
            try:
                stat = backup_file.stat()
                metadata = next((m for m in self.backup_history if m.backup_id in backup_file.name), None)
                
                backup_info = {
                    'filename': backup_file.name,
                    'size_mb': stat.st_size / 1024 / 1024,
                    'created': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'status': metadata.status if metadata else 'unknown',
                    'file_count': metadata.file_count if metadata else 0,
                    'compression_ratio': metadata.compression_ratio if metadata else 0
                }
                backups.append(backup_info)
                
            except Exception as e:
                logging.error(f"Erro ao obter informações do backup {backup_file}: {str(e)}")
        
        return backups
    
    def start_scheduled_backup(self):
        """Inicia backup agendado"""
        schedule.every().day.at(BACKUP_CONFIG['backup_schedule']).do(self.create_backup)
        
        logging.info(f"Backup agendado para {BACKUP_CONFIG['backup_schedule']} diariamente")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
    
    def start_backup_daemon(self):
        """Inicia daemon de backup em thread separada"""
        def daemon_worker():
            self.start_scheduled_backup()
        
        daemon_thread = threading.Thread(target=daemon_worker, daemon=True)
        daemon_thread.start()
        logging.info("Daemon de backup iniciado")

def main():
    """Função principal para execução manual"""
    import sys
    
    backup_system = AutoBackupSystem()
    
    if len(sys.argv) < 2:
        print("Uso: python auto_backup.py [backup|restore|list|daemon] [arquivo_backup]")
        return
    
    command = sys.argv[1]
    
    if command == 'backup':
        metadata = backup_system.create_backup()
        if metadata and metadata.status == 'completed':
            print(f"✅ Backup criado: {metadata.backup_id}")
        else:
            print(f"❌ Backup falhou: {metadata.error_message if metadata else 'Erro desconhecido'}")
    
    elif command == 'restore' and len(sys.argv) > 2:
        success = backup_system.restore_backup(sys.argv[2])
        if success:
            print("✅ Restauração concluída")
        else:
            print("❌ Restauração falhou")
    
    elif command == 'list':
        backups = backup_system.list_backups()
        print("Backups disponíveis:")
        for backup in backups:
            print(f"- {backup['filename']} ({backup['size_mb']:.1f} MB, {backup['status']})")
    
    elif command == 'daemon':
        backup_system.start_backup_daemon()
        print("Daemon de backup iniciado. Pressione Ctrl+C para parar.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDaemon de backup parado.")
    
    else:
        print("Comando inválido.")

if __name__ == '__main__':
    main() 