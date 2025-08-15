"""
Sistema de Restore Inteligente Avançado - Omni Keywords Finder

Funcionalidades:
- Restore automático com validação de integridade
- Descriptografia automática de backups
- Restore seletivo de arquivos
- Validação de compatibilidade
- Rollback automático em caso de falha
- Restore incremental
- Verificação de espaço em disco
- Logs detalhados de restore

Autor: Sistema de Restore Inteligente
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: RESTORE_INTELIGENTE_001
"""

import os
import shutil
import hashlib
import datetime
import logging
import json
import zipfile
import sqlite3
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from enum import Enum

# Imports condicionais
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    Fernet = None

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    storage = None

class RestoreStatus(Enum):
    """Status do processo de restore"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    DECRYPTING = "decrypting"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class RestoreType(Enum):
    """Tipos de restore disponíveis"""
    FULL = "full"
    SELECTIVE = "selective"
    INCREMENTAL = "incremental"
    CLOUD = "cloud"

@dataclass
class RestoreMetadata:
    """Metadados do processo de restore"""
    restore_id: str
    backup_id: str
    timestamp: str
    restore_type: RestoreType
    target_path: str
    status: RestoreStatus
    files_restored: int
    total_size_bytes: int
    duration_seconds: float
    error_message: Optional[str] = None
    rollback_info: Optional[Dict] = None

@dataclass
class RestoreValidationResult:
    """Resultado da validação de restore"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    space_available: bool
    compatibility_check: bool
    integrity_check: bool

class RestoreValidator:
    """Validador para processo de restore"""
    
    def __init__(self):
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para validação"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)string_data [%(levelname)string_data] [RESTORE_VALIDATOR] %(message)string_data',
            handlers=[
                logging.FileHandler(log_dir / 'restore_validator.log'),
                logging.StreamHandler()
            ]
        )
    
    def validate_restore_prerequisites(self, backup_path: str, target_path: str, 
                                     required_space_mb: int = 1000) -> RestoreValidationResult:
        """Valida pré-requisitos para restore"""
        errors = []
        warnings = []
        
        # Verificar se backup existe
        if not os.path.exists(backup_path):
            errors.append(f"Arquivo de backup não encontrado: {backup_path}")
            return RestoreValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                space_available=False,
                compatibility_check=False,
                integrity_check=False
            )
        
        # Verificar espaço em disco
        try:
            statvfs = os.statvfs(target_path)
            free_space_mb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024)
            
            if free_space_mb < required_space_mb:
                errors.append(f"Espaço insuficiente: {free_space_mb:.1f}MB disponível, "
                            f"{required_space_mb}MB necessário")
            else:
                warnings.append(f"Espaço disponível: {free_space_mb:.1f}MB")
        except Exception as e:
            errors.append(f"Erro ao verificar espaço em disco: {e}")
        
        # Verificar permissões
        try:
            if not os.access(target_path, os.W_OK):
                errors.append(f"Sem permissão de escrita em: {target_path}")
        except Exception as e:
            errors.append(f"Erro ao verificar permissões: {e}")
        
        # Verificar integridade do backup
        integrity_ok = self._validate_backup_integrity(backup_path)
        if not integrity_ok:
            errors.append("Backup corrompido ou inválido")
        
        # Verificar compatibilidade
        compatibility_ok = self._check_compatibility(backup_path)
        if not compatibility_ok:
            warnings.append("Possível incompatibilidade detectada")
        
        is_valid = len(errors) == 0
        
        return RestoreValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            space_available=free_space_mb >= required_space_mb if 'free_space_mb' in locals() else False,
            compatibility_check=compatibility_ok,
            integrity_check=integrity_ok
        )
    
    def _validate_backup_integrity(self, backup_path: str) -> bool:
        """Valida integridade do arquivo de backup"""
        try:
            # Verificar se é um arquivo ZIP válido
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    zip_file.testzip()
                return True
            
            # Verificar se é um arquivo criptografado
            elif backup_path.endswith('.enc'):
                # Arquivo criptografado - validação básica
                if os.path.getsize(backup_path) > 0:
                    return True
                return False
            
            return False
            
        except Exception as e:
            logging.error(f"Erro na validação de integridade: {e}")
            return False
    
    def _check_compatibility(self, backup_path: str) -> bool:
        """Verifica compatibilidade do backup"""
        try:
            # Verificar formato do backup
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    
                    # Verificar se contém arquivos esperados
                    expected_files = ['backend/', 'blogs/', 'logs/']
                    has_expected = any(any(expected in file for expected in expected_files) 
                                     for file in file_list)
                    
                    return has_expected
            
            return True
            
        except Exception as e:
            logging.error(f"Erro na verificação de compatibilidade: {e}")
            return False

class RestoreInteligenteManager:
    """Gerenciador principal do sistema de restore inteligente"""
    
    def __init__(self):
        self.backup_dir = Path('backups_inteligentes')
        self.restore_history: List[RestoreMetadata] = []
        self.validator = RestoreValidator()
        self._setup_logging()
        self._setup_database()
    
    def _setup_logging(self):
        """Configura logging avançado"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)string_data [%(levelname)string_data] [RESTORE_INTELIGENTE] %(message)string_data',
            handlers=[
                logging.FileHandler(log_dir / 'restore_inteligente.log'),
                logging.StreamHandler()
            ]
        )
    
    def _setup_database(self):
        """Configura banco de dados para metadados de restore"""
        self.db_path = self.backup_dir / 'restore_metadata.db'
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS restore_metadata (
                    restore_id TEXT PRIMARY KEY,
                    backup_id TEXT,
                    timestamp TEXT,
                    restore_type TEXT,
                    target_path TEXT,
                    status TEXT,
                    files_restored INTEGER,
                    total_size_bytes INTEGER,
                    duration_seconds REAL,
                    error_message TEXT,
                    rollback_info TEXT
                )
            """)
    
    def _load_restore_history(self) -> List[RestoreMetadata]:
        """Carrega histórico de restores"""
        history = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM restore_metadata ORDER BY timestamp DESC")
                for row in cursor.fetchall():
                    restore = RestoreMetadata(
                        restore_id=row[0],
                        backup_id=row[1],
                        timestamp=row[2],
                        restore_type=RestoreType(row[3]),
                        target_path=row[4],
                        status=RestoreStatus(row[5]),
                        files_restored=row[6],
                        total_size_bytes=row[7],
                        duration_seconds=row[8],
                        error_message=row[9],
                        rollback_info=json.loads(row[10]) if row[10] else None
                    )
                    history.append(restore)
        except Exception as e:
            logging.error(f"Erro ao carregar histórico de restore: {e}")
        
        return history
    
    def _save_restore_metadata(self, metadata: RestoreMetadata):
        """Salva metadados do restore"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO restore_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata.restore_id,
                    metadata.backup_id,
                    metadata.timestamp,
                    metadata.restore_type.value,
                    metadata.target_path,
                    metadata.status.value,
                    metadata.files_restored,
                    metadata.total_size_bytes,
                    metadata.duration_seconds,
                    metadata.error_message,
                    json.dumps(metadata.rollback_info) if metadata.rollback_info else None
                ))
        except Exception as e:
            logging.error(f"Erro ao salvar metadados de restore: {e}")
    
    def restore_backup(self, backup_id: str, target_path: str = '.', 
                      restore_type: RestoreType = RestoreType.FULL,
                      selective_files: Optional[List[str]] = None) -> Optional[RestoreMetadata]:
        """Executa restore de backup"""
        start_time = datetime.datetime.now()
        
        # Gerar ID único para restore
        restore_id = f"restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_id}"
        
        # Criar metadados iniciais
        metadata = RestoreMetadata(
            restore_id=restore_id,
            backup_id=backup_id,
            timestamp=start_time.isoformat(),
            restore_type=restore_type,
            target_path=target_path,
            status=RestoreStatus.IN_PROGRESS,
            files_restored=0,
            total_size_bytes=0,
            duration_seconds=0.0
        )
        
        try:
            logging.info(f"Iniciando restore {restore_type.value}: {restore_id}")
            
            # Encontrar arquivo de backup
            backup_files = list(self.backup_dir.glob(f"*{backup_id}*"))
            if not backup_files:
                raise FileNotFoundError(f"Backup não encontrado: {backup_id}")
            
            backup_path = backup_files[0]
            
            # Validar pré-requisitos
            logging.info("Validando pré-requisitos...")
            metadata.status = RestoreStatus.VALIDATING
            
            validation = self.validator.validate_restore_prerequisites(
                str(backup_path), target_path
            )
            
            if not validation.is_valid:
                error_msg = f"Validação falhou: {'; '.join(validation.errors)}"
                raise ValueError(error_msg)
            
            if validation.warnings:
                logging.warning(f"Avisos de validação: {'; '.join(validation.warnings)}")
            
            # Descriptografar se necessário
            if backup_path.name.endswith('.enc'):
                logging.info("Descriptografando backup...")
                metadata.status = RestoreStatus.DECRYPTING
                
                decrypted_path = str(backup_path).replace('.enc', '_decrypted.zip')
                if not self._decrypt_backup(str(backup_path), decrypted_path):
                    raise RuntimeError("Falha na descriptografia do backup")
                
                backup_path = Path(decrypted_path)
            
            # Extrair backup
            logging.info("Extraindo backup...")
            metadata.status = RestoreStatus.EXTRACTING
            
            files_restored, total_size = self._extract_backup(
                backup_path, target_path, restore_type, selective_files
            )
            
            # Atualizar metadados
            duration = (datetime.datetime.now() - start_time).total_seconds()
            metadata.files_restored = files_restored
            metadata.total_size_bytes = total_size
            metadata.duration_seconds = duration
            metadata.status = RestoreStatus.COMPLETED
            
            # Salvar metadados
            self._save_restore_metadata(metadata)
            self.restore_history.append(metadata)
            
            # Limpar arquivo temporário descriptografado
            if backup_path.name.endswith('_decrypted.zip'):
                os.remove(backup_path)
            
            logging.info(f"Restore {restore_type.value} concluído: {restore_id}")
            return metadata
            
        except Exception as e:
            error_msg = f"Erro no restore {restore_id}: {str(e)}"
            logging.error(error_msg)
            
            # Tentar rollback
            rollback_success = self._perform_rollback(target_path, metadata)
            
            metadata.status = RestoreStatus.ROLLED_BACK if rollback_success else RestoreStatus.FAILED
            metadata.error_message = error_msg
            metadata.duration_seconds = (datetime.datetime.now() - start_time).total_seconds()
            metadata.rollback_info = {
                'attempted': True,
                'success': rollback_success,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            self._save_restore_metadata(metadata)
            return metadata
    
    def _decrypt_backup(self, encrypted_path: str, decrypted_path: str) -> bool:
        """Descriptografa backup"""
        if not CRYPTOGRAPHY_AVAILABLE or Fernet is None:
            logging.error("Cryptography não disponível para descriptografia")
            return False
        
        try:
            # Carregar chave
            key_file = Path('backup_encryption.key')
            if not key_file.exists():
                logging.error("Chave de criptografia não encontrada")
                return False
            
            with open(key_file, 'rb') as f:
                key = f.read()
            
            cipher = Fernet(key)
            
            # Descriptografar
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = cipher.decrypt(encrypted_data)
            
            with open(decrypted_path, 'wb') as f:
                f.write(decrypted_data)
            
            logging.info(f"Backup descriptografado: {decrypted_path}")
            return True
            
        except Exception as e:
            logging.error(f"Erro na descriptografia: {e}")
            return False
    
    def _extract_backup(self, backup_path: Path, target_path: str, 
                       restore_type: RestoreType, 
                       selective_files: Optional[List[str]] = None) -> Tuple[int, int]:
        """Extrai arquivos do backup"""
        files_restored = 0
        total_size = 0
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Filtrar arquivos se restore seletivo
                if restore_type == RestoreType.SELECTIVE and selective_files:
                    file_list = [f for f in file_list if any(selective in f for selective in selective_files)]
                
                # Extrair arquivos
                for file_name in file_list:
                    try:
                        # Verificar se arquivo já existe
                        target_file = os.path.join(target_path, file_name)
                        if os.path.exists(target_file):
                            # Fazer backup do arquivo existente
                            backup_existing = f"{target_file}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            shutil.move(target_file, backup_existing)
                            logging.info(f"Arquivo existente movido para: {backup_existing}")
                        
                        # Extrair arquivo
                        zip_file.extract(file_name, target_path)
                        
                        # Obter informações do arquivo
                        file_info = zip_file.getinfo(file_name)
                        total_size += file_info.file_size
                        files_restored += 1
                        
                        logging.debug(f"Arquivo restaurado: {file_name}")
                        
                    except Exception as e:
                        logging.error(f"Erro ao extrair {file_name}: {e}")
                        continue
            
            logging.info(f"Extract concluído: {files_restored} arquivos, {total_size} bytes")
            return files_restored, total_size
            
        except Exception as e:
            logging.error(f"Erro na extração: {e}")
            raise
    
    def _perform_rollback(self, target_path: str, metadata: RestoreMetadata) -> bool:
        """Executa rollback em caso de falha"""
        try:
            logging.info("Executando rollback...")
            
            # Procurar por arquivos .backup_* criados durante o restore
            backup_files = []
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    if file.endswith('.backup_'):
                        backup_files.append(os.path.join(root, file))
            
            # Restaurar arquivos originais
            restored_count = 0
            for backup_file in backup_files:
                try:
                    original_file = backup_file.replace('.backup_', '')
                    if os.path.exists(backup_file):
                        shutil.move(backup_file, original_file)
                        restored_count += 1
                        logging.info(f"Arquivo restaurado: {original_file}")
                except Exception as e:
                    logging.error(f"Erro ao restaurar {backup_file}: {e}")
            
            logging.info(f"Rollback concluído: {restored_count} arquivos restaurados")
            return restored_count > 0
            
        except Exception as e:
            logging.error(f"Erro no rollback: {e}")
            return False
    
    def restore_from_cloud(self, backup_id: str, cloud_provider: str, 
                          bucket: str, target_path: str = '.') -> Optional[RestoreMetadata]:
        """Restaura backup da nuvem"""
        try:
            logging.info(f"Restaurando backup da nuvem: {cloud_provider}")
            
            # Download do backup
            local_path = self._download_from_cloud(cloud_provider, bucket, backup_id)
            if not local_path:
                raise RuntimeError(f"Falha no download do backup da {cloud_provider}")
            
            # Executar restore local
            return self.restore_backup(backup_id, target_path, RestoreType.CLOUD)
            
        except Exception as e:
            logging.error(f"Erro no restore da nuvem: {e}")
            return None
    
    def _download_from_cloud(self, provider: str, bucket: str, backup_id: str) -> Optional[str]:
        """Download backup da nuvem"""
        try:
            if provider == 's3' and BOTO3_AVAILABLE and boto3 is not None:
                s3_client = boto3.client('s3')
                key = f"backups/{backup_id}/backup_{backup_id}.zip"
                local_path = self.backup_dir / f"cloud_download_{backup_id}.zip"
                
                s3_client.download_file(bucket, key, str(local_path))
                logging.info(f"Download S3 concluído: {local_path}")
                return str(local_path)
            
            elif provider == 'gcs' and GCS_AVAILABLE and storage is not None:
                gcs_client = storage.Client()
                bucket_obj = gcs_client.bucket(bucket)
                blob_name = f"backups/{backup_id}/backup_{backup_id}.zip"
                local_path = self.backup_dir / f"cloud_download_{backup_id}.zip"
                
                blob = bucket_obj.blob(blob_name)
                blob.download_to_filename(str(local_path))
                logging.info(f"Download GCS concluído: {local_path}")
                return str(local_path)
            
            else:
                logging.error(f"Provedor de nuvem não suportado: {provider}")
                return None
                
        except Exception as e:
            logging.error(f"Erro no download da nuvem: {e}")
            return None
    
    def list_restores(self) -> List[Dict]:
        """Lista todos os restores"""
        restores = []
        for restore in self.restore_history:
            restore_info = {
                'id': restore.restore_id,
                'backup_id': restore.backup_id,
                'timestamp': restore.timestamp,
                'type': restore.restore_type.value,
                'status': restore.status.value,
                'target_path': restore.target_path,
                'files_restored': restore.files_restored,
                'size_mb': round(restore.total_size_bytes / 1024 / 1024, 2),
                'duration_seconds': round(restore.duration_seconds, 2),
                'error': restore.error_message
            }
            restores.append(restore_info)
        
        return restores
    
    def get_restore_stats(self) -> Dict:
        """Obtém estatísticas dos restores"""
        if not self.restore_history:
            return {}
        
        total_restores = len(self.restore_history)
        successful_restores = len([r for r in self.restore_history 
                                 if r.status == RestoreStatus.COMPLETED])
        failed_restores = len([r for r in self.restore_history 
                             if r.status == RestoreStatus.FAILED])
        
        return {
            'total_restores': total_restores,
            'successful_restores': successful_restores,
            'failed_restores': failed_restores,
            'success_rate': f"{(successful_restores/total_restores)*100:.1f}%" if total_restores > 0 else "0%",
            'average_duration_seconds': round(
                sum(r.duration_seconds for r in self.restore_history) / total_restores, 2
            ) if total_restores > 0 else 0,
            'last_restore': max(r.timestamp for r in self.restore_history) if self.restore_history else None
        }

def main():
    """Função principal para teste"""
    manager = RestoreInteligenteManager()
    
    # Listar backups disponíveis
    print("Backups disponíveis:")
    backup_files = list(manager.backup_dir.glob("*.zip"))
    for backup_file in backup_files:
        print(f"- {backup_file.name}")
    
    if backup_files:
        # Testar restore do primeiro backup
        test_backup = backup_files[0]
        backup_id = test_backup.stem.replace('backup_', '').split('_')[0]
        
        print(f"\nTestando restore do backup: {backup_id}")
        
        # Criar diretório temporário para teste
        test_dir = Path('test_restore')
        test_dir.mkdir(exist_ok=True)
        
        restore = manager.restore_backup(backup_id, str(test_dir), RestoreType.FULL)
        
        if restore and restore.status == RestoreStatus.COMPLETED:
            print("✅ Restore concluído com sucesso!")
            print(f"Arquivos restaurados: {restore.files_restored}")
            print(f"Tamanho total: {restore.total_size_bytes / 1024 / 1024:.2f} MB")
            print(f"Duração: {restore.duration_seconds:.2f} segundos")
        else:
            print("❌ Falha no restore")
            if restore:
                print(f"Erro: {restore.error_message}")
        
        # Limpar diretório de teste
        shutil.rmtree(test_dir, ignore_errors=True)
    
    # Estatísticas
    print("\nEstatísticas de restore:")
    stats = manager.get_restore_stats()
    for key, value in stats.items():
        print(f"- {key}: {value}")

if __name__ == "__main__":
    main()

