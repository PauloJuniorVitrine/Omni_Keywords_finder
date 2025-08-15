"""
Sistema de Backup Inteligente Avançado - Omni Keywords Finder

Funcionalidades:
- Backup incremental automático
- Integração com S3 para backup em nuvem
- Criptografia de backups
- Validação de integridade avançada
- Retenção configurável inteligente
- Detecção de mudanças
- Compressão adaptativa
- Métricas de performance

Autor: Sistema de Backup Inteligente
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: BACKUP_INTELIGENTE_001
"""

import os
import shutil
import hashlib
import datetime
import logging
import json
import zipfile
import threading
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
from enum import Enum

# Imports condicionais para dependências opcionais
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None

try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    Fernet = None

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None

# Configurações avançadas
BACKUP_INTELIGENTE_CONFIG = {
    'backup_dir': 'backups_inteligentes',
    'retention_policy': {
        'daily': 7,      # 7 backups diários
        'weekly': 4,     # 4 backups semanais
        'monthly': 12,   # 12 backups mensais
        'yearly': 5      # 5 backups anuais
    },
    'compression_levels': {
        'fast': 1,
        'balanced': 6,
        'maximum': 9
    },
    'encryption_enabled': True,
    'cloud_storage': {
        'enabled': True,
        'providers': ['s3'],
        'sync_interval_hours': 6
    },
    'incremental': {
        'enabled': True,
        'max_incremental_depth': 10,
        'full_backup_interval_days': 7
    },
    'performance': {
        'max_concurrent_uploads': 3,
        'chunk_size_mb': 50,
        'timeout_seconds': 300
    },
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
        'backups_inteligentes/',
        'coverage/',
        'htmlcov/',
        'cypress/screenshots/',
        '*.pyc',
        '.DS_Store'
    ]
}

class BackupType(Enum):
    """Tipos de backup disponíveis"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class BackupStatus(Enum):
    """Status dos backups"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"
    UPLOADED = "uploaded"

@dataclass
class BackupMetadata:
    """Metadados avançados do backup"""
    backup_id: str
    timestamp: str
    backup_type: BackupType
    size_bytes: int
    compressed_size_bytes: int
    file_count: int
    checksum: str
    compression_ratio: float
    encryption_key_id: Optional[str]
    status: BackupStatus
    incremental_base: Optional[str] = None
    cloud_sync_status: Optional[Dict[str, str]] = None
    performance_metrics: Optional[Dict[str, float]] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização"""
        data = asdict(self)
        data['backup_type'] = self.backup_type.value
        data['status'] = self.status.value
        return data

@dataclass
class FileChangeInfo:
    """Informações sobre mudanças em arquivos"""
    file_path: str
    last_modified: float
    size: int
    checksum: str
    change_type: str  # 'added', 'modified', 'deleted'

class ChangeDetector:
    """Detector de mudanças para backup incremental"""
    
    def __init__(self, state_file: str = 'backup_state.json'):
        self.state_file = Path(state_file)
        self.file_states: Dict[str, Dict] = self._load_state()
    
    def _load_state(self) -> Dict[str, Dict]:
        """Carrega estado anterior dos arquivos"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Erro ao carregar estado: {e}")
        return {}
    
    def _save_state(self):
        """Salva estado atual dos arquivos"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.file_states, f, indent=2)
        except Exception as e:
            logging.error(f"Erro ao salvar estado: {e}")
    
    def detect_changes(self, files: List[str]) -> List[FileChangeInfo]:
        """Detecta mudanças nos arquivos"""
        changes = []
        current_states = {}
        
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    current_state = {
                        'modified': stat.st_mtime,
                        'size': stat.st_size,
                        'checksum': self._calculate_file_checksum(file_path)
                    }
                    current_states[file_path] = current_state
                    
                    # Verificar mudanças
                    if file_path not in self.file_states:
                        changes.append(FileChangeInfo(
                            file_path=file_path,
                            last_modified=stat.st_mtime,
                            size=stat.st_size,
                            checksum=current_state['checksum'],
                            change_type='added'
                        ))
                    else:
                        old_state = self.file_states[file_path]
                        if (old_state['modified'] != stat.st_mtime or 
                            old_state['size'] != stat.st_size or
                            old_state['checksum'] != current_state['checksum']):
                            changes.append(FileChangeInfo(
                                file_path=file_path,
                                last_modified=stat.st_mtime,
                                size=stat.st_size,
                                checksum=current_state['checksum'],
                                change_type='modified'
                            ))
                else:
                    # Arquivo foi deletado
                    if file_path in self.file_states:
                        changes.append(FileChangeInfo(
                            file_path=file_path,
                            last_modified=0,
                            size=0,
                            checksum='',
                            change_type='deleted'
                        ))
                        
            except Exception as e:
                logging.error(f"Erro ao verificar arquivo {file_path}: {e}")
        
        # Atualizar estado
        self.file_states = current_states
        self._save_state()
        
        return changes
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calcula checksum do arquivo"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return ""

class EncryptionManager:
    """Gerenciador de criptografia para backups"""
    
    def __init__(self):
        if not CRYPTOGRAPHY_AVAILABLE or Fernet is None:
            logging.warning("Cryptography não disponível. Criptografia desabilitada.")
            self.key = None
            self.cipher = None
            return
            
        self.key_file = Path('backup_encryption.key')
        self.key = self._load_or_generate_key()
        if self.key:
            self.cipher = Fernet(self.key)
        else:
            self.cipher = None
    
    def _load_or_generate_key(self) -> Optional[bytes]:
        """Carrega chave existente ou gera nova"""
        if not CRYPTOGRAPHY_AVAILABLE or Fernet is None:
            return None
            
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Erro ao carregar chave: {e}")
        
        # Gerar nova chave
        key = Fernet.generate_key()
        try:
            with open(self.key_file, 'wb') as f:
                f.write(key)
            logging.info("Nova chave de criptografia gerada")
        except Exception as e:
            logging.error(f"Erro ao salvar chave: {e}")
        
        return key
    
    def encrypt_file(self, input_path: str, output_path: str) -> bool:
        """Criptografa arquivo"""
        if not CRYPTOGRAPHY_AVAILABLE or not self.cipher:
            logging.warning("Criptografia não disponível")
            return False
            
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.cipher.encrypt(data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            logging.error(f"Erro na criptografia: {e}")
            return False
    
    def decrypt_file(self, input_path: str, output_path: str) -> bool:
        """Descriptografa arquivo"""
        if not CRYPTOGRAPHY_AVAILABLE or not self.cipher:
            logging.warning("Criptografia não disponível")
            return False
            
        try:
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return True
        except Exception as e:
            logging.error(f"Erro na descriptografia: {e}")
            return False

class CloudStorageManager:
    """Gerenciador de armazenamento em nuvem"""
    
    def __init__(self):
        self.s3_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Inicializa clientes de nuvem"""
        try:
            # AWS S3
            if BOTO3_AVAILABLE and boto3 is not None and os.getenv('AWS_ACCESS_KEY_ID'):
                self.s3_client = boto3.client('s3')
                logging.info("Cliente S3 inicializado")
        except Exception as e:
            logging.warning(f"Erro ao inicializar S3: {e}")
    
    def upload_to_s3(self, file_path: str, bucket: str, key: str) -> bool:
        """Faz upload para S3"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.upload_file(file_path, bucket, key)
            logging.info(f"Upload S3 concluído: {key}")
            return True
        except Exception as e:
            logging.error(f"Erro no upload S3: {e}")
            return False
    
    def sync_backup_to_cloud(self, backup_path: str, backup_id: str) -> Dict[str, str]:
        """Sincroniza backup com nuvem"""
        results = {}
        
        # S3
        if self.s3_client:
            bucket = os.getenv('S3_BACKUP_BUCKET')
            if bucket:
                key = f"backups/{backup_id}/{Path(backup_path).name}"
                if self.upload_to_s3(backup_path, bucket, key):
                    results['s3'] = 'success'
                else:
                    results['s3'] = 'failed'
        
        return results

class BackupInteligenteManager:
    """Gerenciador principal do sistema de backup inteligente"""
    
    def __init__(self):
        self.backup_dir = Path(BACKUP_INTELIGENTE_CONFIG['backup_dir'])
        self.backup_dir.mkdir(exist_ok=True)
        self.metadata_file = self.backup_dir / 'backup_metadata.json'
        self.backup_history: List[BackupMetadata] = self._load_metadata()
        
        # Componentes
        self.change_detector = ChangeDetector()
        self.encryption_manager = EncryptionManager()
        self.cloud_manager = CloudStorageManager()
        
        self._setup_logging()
        self._setup_database()
    
    def _setup_logging(self):
        """Configura logging avançado"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)string_data [%(levelname)string_data] [BACKUP_INTELIGENTE] %(message)string_data',
            handlers=[
                logging.FileHandler(log_dir / 'backup_inteligente.log'),
                logging.StreamHandler()
            ]
        )
    
    def _setup_database(self):
        """Configura banco de dados para metadados"""
        self.db_path = self.backup_dir / 'backup_metadata.db'
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_metadata (
                    backup_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    backup_type TEXT,
                    size_bytes INTEGER,
                    compressed_size_bytes INTEGER,
                    file_count INTEGER,
                    checksum TEXT,
                    compression_ratio REAL,
                    encryption_key_id TEXT,
                    status TEXT,
                    incremental_base TEXT,
                    cloud_sync_status TEXT,
                    performance_metrics TEXT,
                    error_message TEXT
                )
            """)
    
    def _load_metadata(self) -> List[BackupMetadata]:
        """Carrega metadados dos backups"""
        metadata_list = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM backup_metadata ORDER BY timestamp DESC")
                for row in cursor.fetchall():
                    metadata = BackupMetadata(
                        backup_id=row[0],
                        timestamp=row[1],
                        backup_type=BackupType(row[2]),
                        size_bytes=row[3],
                        compressed_size_bytes=row[4],
                        file_count=row[5],
                        checksum=row[6],
                        compression_ratio=row[7],
                        encryption_key_id=row[8],
                        status=BackupStatus(row[9]),
                        incremental_base=row[10],
                        cloud_sync_status=json.loads(row[11]) if row[11] else {},
                        performance_metrics=json.loads(row[12]) if row[12] else {},
                        error_message=row[13]
                    )
                    metadata_list.append(metadata)
        except Exception as e:
            logging.error(f"Erro ao carregar metadados: {e}")
        
        return metadata_list
    
    def _save_metadata(self, metadata: BackupMetadata):
        """Salva metadados do backup"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO backup_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata.backup_id,
                    metadata.timestamp,
                    metadata.backup_type.value,
                    metadata.size_bytes,
                    metadata.compressed_size_bytes,
                    metadata.file_count,
                    metadata.checksum,
                    metadata.compression_ratio,
                    metadata.encryption_key_id,
                    metadata.status.value,
                    metadata.incremental_base,
                    json.dumps(metadata.cloud_sync_status or {}),
                    json.dumps(metadata.performance_metrics or {}),
                    metadata.error_message
                ))
        except Exception as e:
            logging.error(f"Erro ao salvar metadados: {e}")
    
    def _should_exclude(self, path: str) -> bool:
        """Verifica se arquivo deve ser excluído"""
        path_lower = path.lower()
        for pattern in BACKUP_INTELIGENTE_CONFIG['exclude_patterns']:
            if pattern in path_lower:
                return True
        return False
    
    def _get_files_to_backup(self) -> List[str]:
        """Obtém lista de arquivos para backup"""
        files = []
        
        for critical_file in BACKUP_INTELIGENTE_CONFIG['critical_files']:
            if os.path.exists(critical_file):
                if os.path.isfile(critical_file):
                    files.append(critical_file)
                elif os.path.isdir(critical_file):
                    for root, dirs, filenames in os.walk(critical_file):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            if not self._should_exclude(file_path):
                                files.append(file_path)
        
        return files
    
    def _create_backup_filename(self, backup_type: BackupType) -> str:
        """Cria nome do arquivo de backup"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{backup_type.value}_{timestamp}.zip"
    
    def _should_create_full_backup(self) -> bool:
        """Verifica se deve criar backup completo"""
        if not self.backup_history:
            return True
        
        last_full_backup = None
        for backup in self.backup_history:
            if backup.backup_type == BackupType.FULL and backup.status == BackupStatus.COMPLETED:
                last_full_backup = backup
                break
        
        if not last_full_backup:
            return True
        
        last_date = datetime.datetime.fromisoformat(last_full_backup.timestamp)
        days_since = (datetime.datetime.now() - last_date).days
        
        return days_since >= BACKUP_INTELIGENTE_CONFIG['incremental']['full_backup_interval_days']
    
    def _compress_files_intelligent(self, files: List[str], backup_path: str, 
                                  compression_level: str = 'balanced') -> Tuple[int, float]:
        """Comprime arquivos com compressão inteligente"""
        start_time = time.time()
        total_size = 0
        compressed_size = 0
        
        level = BACKUP_INTELIGENTE_CONFIG['compression_levels'][compression_level]
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=level) as zip_file:
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        # Adicionar ao ZIP
                        zip_file.write(file_path)
                        
                        # Obter tamanho comprimido
                        compressed_size = os.path.getsize(backup_path)
                        
                except Exception as e:
                    logging.error(f"Erro ao comprimir {file_path}: {e}")
        
        compression_ratio = (1 - compressed_size / total_size) * 100 if total_size > 0 else 0
        duration = time.time() - start_time
        
        logging.info(f"Compressão concluída: {len(files)} arquivos, "
                    f"razão: {compression_ratio:.1f}%, tempo: {duration:.2f}string_data")
        
        return total_size, compression_ratio
    
    def create_backup(self, backup_type: Optional[BackupType] = None) -> Optional[BackupMetadata]:
        """Cria backup inteligente"""
        start_time = time.time()
        
        # Determinar tipo de backup
        if backup_type is None:
            if self._should_create_full_backup():
                backup_type = BackupType.FULL
            else:
                backup_type = BackupType.INCREMENTAL
        
        # Gerar ID único
        backup_id = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_type.value}"
        
        # Criar metadados iniciais
        metadata = BackupMetadata(
            backup_id=backup_id,
            timestamp=datetime.datetime.now().isoformat(),
            backup_type=backup_type,
            size_bytes=0,
            compressed_size_bytes=0,
            file_count=0,
            checksum="",
            compression_ratio=0.0,
            encryption_key_id=None,
            status=BackupStatus.IN_PROGRESS,
            performance_metrics={}
        )
        
        try:
            logging.info(f"Iniciando backup {backup_type.value}: {backup_id}")
            
            # Obter arquivos para backup
            if backup_type == BackupType.FULL:
                files = self._get_files_to_backup()
            else:
                # Backup incremental - apenas arquivos modificados
                all_files = self._get_files_to_backup()
                changes = self.change_detector.detect_changes(all_files)
                files = [change.file_path for change in changes if change.change_type in ['added', 'modified']]
                
                if not files:
                    logging.info("Nenhuma mudança detectada para backup incremental")
                    return None
            
            if not files:
                logging.warning("Nenhum arquivo encontrado para backup")
                return None
            
            # Criar nome do arquivo
            backup_filename = self._create_backup_filename(backup_type)
            backup_path = self.backup_dir / backup_filename
            
            # Comprimir arquivos
            total_size, compression_ratio = self._compress_files_intelligent(
                files, str(backup_path)
            )
            
            # Criptografar se habilitado
            encryption_key_id = None
            if BACKUP_INTELIGENTE_CONFIG['encryption_enabled']:
                encrypted_path = str(backup_path) + '.enc'
                if self.encryption_manager.encrypt_file(str(backup_path), encrypted_path):
                    os.remove(backup_path)
                    backup_path = Path(encrypted_path)
                    encryption_key_id = "default"
            
            # Calcular checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Atualizar metadados
            metadata.size_bytes = total_size
            metadata.compressed_size_bytes = backup_path.stat().st_size
            metadata.file_count = len(files)
            metadata.checksum = checksum
            metadata.compression_ratio = compression_ratio
            metadata.encryption_key_id = encryption_key_id
            metadata.status = BackupStatus.COMPLETED
            metadata.performance_metrics = {
                'duration_seconds': time.time() - start_time,
                'files_per_second': len(files) / (time.time() - start_time),
                'compression_speed_mbps': (total_size / 1024 / 1024) / (time.time() - start_time)
            }
            
            # Salvar metadados
            self._save_metadata(metadata)
            self.backup_history.append(metadata)
            
            # Sincronizar com nuvem
            if BACKUP_INTELIGENTE_CONFIG['cloud_storage']['enabled']:
                cloud_results = self.cloud_manager.sync_backup_to_cloud(
                    str(backup_path), backup_id
                )
                metadata.cloud_sync_status = cloud_results
                metadata.status = BackupStatus.UPLOADED
                self._save_metadata(metadata)
            
            logging.info(f"Backup {backup_type.value} concluído: {backup_id}")
            return metadata
            
        except Exception as e:
            error_msg = f"Erro no backup {backup_id}: {str(e)}"
            logging.error(error_msg)
            metadata.status = BackupStatus.FAILED
            metadata.error_message = error_msg
            self._save_metadata(metadata)
            return None
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum do arquivo de backup"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def validate_backup(self, backup_id: str) -> bool:
        """Valida integridade do backup"""
        try:
            # Encontrar backup
            backup_metadata = None
            for backup in self.backup_history:
                if backup.backup_id == backup_id:
                    backup_metadata = backup
                    break
            
            if not backup_metadata:
                logging.error(f"Backup não encontrado: {backup_id}")
                return False
            
            # Encontrar arquivo
            backup_files = list(self.backup_dir.glob(f"*{backup_id}*"))
            if not backup_files:
                logging.error(f"Arquivo de backup não encontrado: {backup_id}")
                return False
            
            backup_file = backup_files[0]
            
            # Verificar tamanho
            actual_size = backup_file.stat().st_size
            if actual_size != backup_metadata.compressed_size_bytes:
                logging.error(f"Tamanho incorreto: esperado {backup_metadata.compressed_size_bytes}, "
                            f"atual {actual_size}")
                return False
            
            # Verificar checksum
            actual_checksum = self._calculate_checksum(backup_file)
            if actual_checksum != backup_metadata.checksum:
                logging.error(f"Checksum incorreto: esperado {backup_metadata.checksum}, "
                            f"atual {actual_checksum}")
                return False
            
            # Verificar se é ZIP válido (se não estiver criptografado)
            if not backup_file.name.endswith('.enc'):
                try:
                    with zipfile.ZipFile(backup_file, 'r') as zip_file:
                        zip_file.testzip()
                except zipfile.BadZipFile:
                    logging.error(f"Arquivo ZIP corrompido: {backup_file}")
                    return False
            
            # Atualizar status
            backup_metadata.status = BackupStatus.VALIDATED
            self._save_metadata(backup_metadata)
            
            logging.info(f"Backup validado com sucesso: {backup_id}")
            return True
            
        except Exception as e:
            logging.error(f"Erro na validação do backup {backup_id}: {str(e)}")
            return False
    
    def cleanup_old_backups(self):
        """Remove backups antigos baseado na política de retenção"""
        try:
            retention = BACKUP_INTELIGENTE_CONFIG['retention_policy']
            current_time = datetime.datetime.now()
            
            # Agrupar backups por tipo
            backups_by_type = {
                'daily': [],
                'weekly': [],
                'monthly': [],
                'yearly': []
            }
            
            for backup in self.backup_history:
                if backup.status != BackupStatus.COMPLETED:
                    continue
                
                backup_date = datetime.datetime.fromisoformat(backup.timestamp)
                days_old = (current_time - backup_date).days
                
                if days_old <= 7:
                    backups_by_type['daily'].append(backup)
                elif days_old <= 30:
                    backups_by_type['weekly'].append(backup)
                elif days_old <= 365:
                    backups_by_type['monthly'].append(backup)
                else:
                    backups_by_type['yearly'].append(backup)
            
            # Remover backups excedentes
            for backup_type, max_count in retention.items():
                backups = backups_by_type[backup_type]
                if len(backups) > max_count:
                    # Ordenar por data (mais antigos primeiro)
                    backups.sort(key=lambda value: value.timestamp)
                    
                    # Remover excedentes
                    to_remove = backups[:-max_count]
                    for backup in to_remove:
                        self._remove_backup(backup.backup_id)
            
            logging.info("Limpeza de backups antigos concluída")
            
        except Exception as e:
            logging.error(f"Erro na limpeza de backups: {e}")
    
    def _remove_backup(self, backup_id: str):
        """Remove backup específico"""
        try:
            # Encontrar arquivo
            backup_files = list(self.backup_dir.glob(f"*{backup_id}*"))
            for backup_file in backup_files:
                os.remove(backup_file)
            
            # Remover do banco
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM backup_metadata WHERE backup_id = ?", (backup_id,))
            
            # Remover da lista
            self.backup_history = [b for b in self.backup_history if b.backup_id != backup_id]
            
            logging.info(f"Backup removido: {backup_id}")
            
        except Exception as e:
            logging.error(f"Erro ao remover backup {backup_id}: {e}")
    
    def list_backups(self) -> List[Dict]:
        """Lista todos os backups"""
        backups = []
        for backup in self.backup_history:
            backup_info = {
                'id': backup.backup_id,
                'timestamp': backup.timestamp,
                'type': backup.backup_type.value,
                'status': backup.status.value,
                'size_mb': round(backup.compressed_size_bytes / 1024 / 1024, 2),
                'file_count': backup.file_count,
                'compression_ratio': f"{backup.compression_ratio:.1f}%",
                'encrypted': backup.encryption_key_id is not None,
                'cloud_sync': backup.cloud_sync_status or {}
            }
            backups.append(backup_info)
        
        return backups
    
    def get_backup_stats(self) -> Dict:
        """Obtém estatísticas dos backups"""
        if not self.backup_history:
            return {}
        
        total_backups = len(self.backup_history)
        successful_backups = len([b for b in self.backup_history if b.status == BackupStatus.COMPLETED])
        total_size_gb = sum(b.compressed_size_bytes for b in self.backup_history) / 1024 / 1024 / 1024
        
        return {
            'total_backups': total_backups,
            'successful_backups': successful_backups,
            'success_rate': f"{(successful_backups/total_backups)*100:.1f}%",
            'total_size_gb': round(total_size_gb, 2),
            'average_size_mb': round(sum(b.compressed_size_bytes for b in self.backup_history) / total_backups / 1024 / 1024, 2),
            'last_backup': max(b.timestamp for b in self.backup_history),
            'oldest_backup': min(b.timestamp for b in self.backup_history)
        }
    
    def start_scheduled_backup(self):
        """Inicia backup agendado"""
        if not SCHEDULE_AVAILABLE or schedule is None:
            logging.error("Schedule não disponível. Backup agendado desabilitado.")
            return
            
        schedule.every().day.at("02:00").do(self.create_backup)
        schedule.every().hour.do(self.cleanup_old_backups)
        
        logging.info("Backup agendado iniciado")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """Função principal para teste"""
    manager = BackupInteligenteManager()
    
    # Criar backup de teste
    print("Criando backup de teste...")
    backup = manager.create_backup()
    
    if backup:
        print(f"Backup criado: {backup.backup_id}")
        print(f"Status: {backup.status.value}")
        print(f"Tamanho: {backup.compressed_size_bytes / 1024 / 1024:.2f} MB")
        print(f"Arquivos: {backup.file_count}")
        print(f"Compressão: {backup.compression_ratio:.1f}%")
        
        # Validar backup
        print("\nValidando backup...")
        if manager.validate_backup(backup.backup_id):
            print("✅ Backup validado com sucesso!")
        else:
            print("❌ Falha na validação do backup")
        
        # Listar backups
        print("\nListando backups:")
        backups = manager.list_backups()
        for b in backups:
            print(f"- {b['id']}: {b['type']} ({b['size_mb']} MB)")
        
        # Estatísticas
        print("\nEstatísticas:")
        stats = manager.get_backup_stats()
        for key, value in stats.items():
            print(f"- {key}: {value}")
    else:
        print("❌ Falha na criação do backup")

if __name__ == "__main__":
    main()
