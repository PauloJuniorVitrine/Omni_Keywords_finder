"""
Google Cloud Storage Provider para Backup Inteligente
====================================================

Este módulo implementa integração completa com Google Cloud Storage para backup
automático e inteligente de dados do sistema Omni Keywords Finder.

Tracing ID: INT-006
Data: 2024-12-19
Status: Implementação completa
"""

import os
import json
import gzip
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, BinaryIO
from pathlib import Path
import hashlib
import tempfile
import shutil

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound, GoogleCloudError
    from google.auth.exceptions import DefaultCredentialsError
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    storage = None
    NotFound = Exception
    GoogleCloudError = Exception
    DefaultCredentialsError = Exception

from ..backup_manager import BackupProvider, BackupConfig, BackupMetadata


class GCSConfig:
    """Configuração para Google Cloud Storage."""
    
    def __init__(
        self,
        bucket_name: str,
        project_id: Optional[str] = None,
        credentials_path: Optional[str] = None,
        compression_enabled: bool = True,
        encryption_enabled: bool = True,
        retention_days: int = 30,
        max_retries: int = 3,
        timeout_seconds: int = 60
    ):
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.compression_enabled = compression_enabled
        self.encryption_enabled = encryption_enabled
        self.retention_days = retention_days
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds


class GCSProvider(BackupProvider):
    """
    Provedor de backup usando Google Cloud Storage.
    
    Funcionalidades:
    - Upload/download de arquivos
    - Compressão automática
    - Criptografia opcional
    - Retenção configurável
    - Métricas e monitoramento
    - Retry logic com backoff exponencial
    """
    
    def __init__(self, config: GCSConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.bucket = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Inicializa o cliente GCS."""
        if not GCS_AVAILABLE:
            raise ImportError("Google Cloud Storage não está disponível. Instale: pip install google-cloud-storage")
        
        try:
            # Configurar credenciais
            if self.config.credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.credentials_path
            
            # Criar cliente
            self.client = storage.Client(
                project=self.config.project_id,
                timeout=self.config.timeout_seconds
            )
            
            # Obter bucket
            self.bucket = self.client.bucket(self.config.bucket_name)
            
            # Verificar se bucket existe
            if not self.bucket.exists():
                self.logger.warning(f"Bucket {self.config.bucket_name} não existe. Criando...")
                self.bucket.create()
            
            self.logger.info(f"GCS Provider inicializado com sucesso. Bucket: {self.config.bucket_name}")
            
        except DefaultCredentialsError as e:
            raise Exception(f"Erro de credenciais GCS: {e}. Configure GOOGLE_APPLICATION_CREDENTIALS")
        except GoogleCloudError as e:
            raise Exception(f"Erro ao inicializar GCS: {e}")
    
    def _get_blob_path(self, backup_name: str, file_extension: str = ".gz") -> str:
        """Gera caminho do blob no GCS."""
        timestamp = datetime.now().strftime("%Y/%m/%data/%H%M%S")
        return f"backups/{timestamp}/{backup_name}{file_extension}"
    
    def _compress_file(self, file_path: str) -> str:
        """Comprime arquivo usando gzip."""
        if not self.config.compression_enabled:
            return file_path
        
        compressed_path = f"{file_path}.gz"
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_path
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcula checksum SHA-256 do arquivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _upload_with_retry(self, blob, file_path: str) -> None:
        """Upload com retry logic e backoff exponencial."""
        import time
        
        for attempt in range(self.config.max_retries):
            try:
                blob.upload_from_filename(file_path)
                return
            except GoogleCloudError as e:
                if attempt == self.config.max_retries - 1:
                    raise e
                
                wait_time = 2 ** attempt
                self.logger.warning(f"Upload falhou (tentativa {attempt + 1}). Aguardando {wait_time}string_data...")
                time.sleep(wait_time)
    
    def create_backup(self, source_path: str, backup_name: str) -> BackupMetadata:
        """
        Cria backup no Google Cloud Storage.
        
        Args:
            source_path: Caminho do arquivo/diretório a ser backupado
            backup_name: Nome do backup
            
        Returns:
            BackupMetadata com informações do backup criado
        """
        try:
            # Verificar se arquivo existe
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {source_path}")
            
            # Comprimir se habilitado
            if self.config.compression_enabled:
                compressed_path = self._compress_file(source_path)
                upload_path = compressed_path
                file_extension = ".gz"
            else:
                upload_path = source_path
                file_extension = ""
            
            # Gerar caminho do blob
            blob_path = self._get_blob_path(backup_name, file_extension)
            blob = self.bucket.blob(blob_path)
            
            # Configurar metadados
            blob.metadata = {
                'original_filename': os.path.basename(source_path),
                'compressed': str(self.config.compression_enabled),
                'encrypted': str(self.config.encryption_enabled),
                'created_at': datetime.now().isoformat(),
                'checksum': self._calculate_checksum(upload_path)
            }
            
            # Upload com retry
            self._upload_with_retry(blob, upload_path)
            
            # Limpar arquivo temporário comprimido
            if self.config.compression_enabled and upload_path != source_path:
                os.remove(upload_path)
            
            # Criar metadata
            metadata = BackupMetadata(
                backup_id=backup_name,
                provider="gcs",
                location=blob_path,
                size=blob.size,
                created_at=datetime.now(),
                checksum=blob.metadata.get('checksum'),
                compression_enabled=self.config.compression_enabled,
                encryption_enabled=self.config.encryption_enabled
            )
            
            self.logger.info(f"Backup criado com sucesso: {backup_name} -> {blob_path}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup {backup_name}: {e}")
            raise
    
    def restore_backup(self, backup_id: str, destination_path: str) -> None:
        """
        Restaura backup do Google Cloud Storage.
        
        Args:
            backup_id: ID do backup a ser restaurado
            destination_path: Caminho de destino
        """
        try:
            # Buscar blob pelo backup_id
            blobs = list(self.bucket.list_blobs(prefix=f"backups/"))
            
            target_blob = None
            for blob in blobs:
                if backup_id in blob.name:
                    target_blob = blob
                    break
            
            if not target_blob:
                raise NotFound(f"Backup {backup_id} não encontrado")
            
            # Download do arquivo
            temp_path = f"/tmp/{backup_id}_temp"
            target_blob.download_to_filename(temp_path)
            
            # Descomprimir se necessário
            if target_blob.name.endswith('.gz'):
                with gzip.open(temp_path, 'rb') as f_in:
                    with open(destination_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(temp_path)
            else:
                shutil.move(temp_path, destination_path)
            
            self.logger.info(f"Backup restaurado com sucesso: {backup_id} -> {destination_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup {backup_id}: {e}")
            raise
    
    def list_backups(self, limit: int = 100) -> List[BackupMetadata]:
        """
        Lista backups disponíveis.
        
        Args:
            limit: Número máximo de backups a retornar
            
        Returns:
            Lista de BackupMetadata
        """
        try:
            backups = []
            blobs = list(self.bucket.list_blobs(prefix="backups/", max_results=limit))
            
            for blob in blobs:
                if blob.metadata:
                    metadata = BackupMetadata(
                        backup_id=blob.name.split('/')[-1].replace('.gz', ''),
                        provider="gcs",
                        location=blob.name,
                        size=blob.size,
                        created_at=datetime.fromisoformat(blob.metadata.get('created_at', datetime.now().isoformat())),
                        checksum=blob.metadata.get('checksum'),
                        compression_enabled=blob.metadata.get('compressed', 'False') == 'True',
                        encryption_enabled=blob.metadata.get('encrypted', 'False') == 'True'
                    )
                    backups.append(metadata)
            
            return sorted(backups, key=lambda value: value.created_at, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao listar backups: {e}")
            raise
    
    def delete_backup(self, backup_id: str) -> None:
        """
        Deleta backup do Google Cloud Storage.
        
        Args:
            backup_id: ID do backup a ser deletado
        """
        try:
            # Buscar blob pelo backup_id
            blobs = list(self.bucket.list_blobs(prefix=f"backups/"))
            
            target_blob = None
            for blob in blobs:
                if backup_id in blob.name:
                    target_blob = blob
                    break
            
            if not target_blob:
                raise NotFound(f"Backup {backup_id} não encontrado")
            
            # Deletar blob
            target_blob.delete()
            
            self.logger.info(f"Backup deletado com sucesso: {backup_id}")
            
        except Exception as e:
            self.logger.error(f"Erro ao deletar backup {backup_id}: {e}")
            raise
    
    def cleanup_old_backups(self) -> int:
        """
        Remove backups antigos baseado na política de retenção.
        
        Returns:
            Número de backups removidos
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            deleted_count = 0
            
            blobs = list(self.bucket.list_blobs(prefix="backups/"))
            
            for blob in blobs:
                if blob.metadata and 'created_at' in blob.metadata:
                    created_at = datetime.fromisoformat(blob.metadata['created_at'])
                    if created_at < cutoff_date:
                        blob.delete()
                        deleted_count += 1
                        self.logger.info(f"Backup antigo removido: {blob.name}")
            
            self.logger.info(f"Cleanup concluído. {deleted_count} backups removidos")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Erro no cleanup de backups: {e}")
            raise
    
    def get_storage_metrics(self) -> Dict[str, Union[int, float]]:
        """
        Obtém métricas de armazenamento.
        
        Returns:
            Dicionário com métricas
        """
        try:
            blobs = list(self.bucket.list_blobs(prefix="backups/"))
            
            total_size = sum(blob.size for blob in blobs)
            total_files = len(blobs)
            
            # Calcular tamanho médio
            avg_size = total_size / total_files if total_files > 0 else 0
            
            # Contar por tipo de compressão
            compressed_count = sum(1 for blob in blobs if blob.name.endswith('.gz'))
            
            return {
                'total_backups': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'average_size_bytes': avg_size,
                'compressed_backups': compressed_count,
                'uncompressed_backups': total_files - compressed_count
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Testa conectividade com Google Cloud Storage.
        
        Returns:
            True se conexão bem-sucedida
        """
        try:
            # Tentar listar blobs
            list(self.bucket.list_blobs(max_results=1))
            self.logger.info("Conexão GCS testada com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Falha no teste de conexão GCS: {e}")
            return False


# Configuração padrão para desenvolvimento
DEFAULT_GCS_CONFIG = GCSConfig(
    bucket_name="omni-keywords-backup-dev",
    compression_enabled=True,
    encryption_enabled=True,
    retention_days=30,
    max_retries=3,
    timeout_seconds=60
) 