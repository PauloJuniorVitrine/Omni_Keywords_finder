from typing import Dict, List, Optional, Any
"""
Testes Unitários para GCSProvider - Omni Keywords Finder

Testes abrangentes para o provedor GCS (Google Cloud Storage):
- Testes de configuração e inicialização
- Testes de upload/download de arquivos
- Testes de compressão e criptografia
- Testes de rate limiting e métricas
- Testes de tratamento de erros
- Testes de templates de configuração

Autor: Sistema de Integração Externa
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: INT-006
"""

import pytest
import asyncio
import tempfile
import os
import json
import gzip
import base64
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from cryptography.fernet import Fernet

from infrastructure.backup.inteligente.gcs_provider import (
    GCSProvider,
    GCSConfig,
    GCSBackupType,
    GCSCompressionType,
    GCSBackupMetadata,
    GCSBackupResult,
    GCSEncryption,
    GCSCompression,
    GCSRateLimiter,
    GCSMetrics,
    GCSTemplates
)


class TestGCSConfig:
    """Testes para configuração GCS"""
    
    def test_gcs_config_creation(self):
        """Testa criação de configuração GCS"""
        config = GCSConfig(
            project_id="test-project",
            bucket_name="test-bucket",
            region="us-central1",
            max_retries=3
        )
        
        assert config.project_id == "test-project"
        assert config.bucket_name == "test-bucket"
        assert config.region == "us-central1"
        assert config.max_retries == 3
        assert config.compression == GCSCompressionType.GZIP
    
    def test_gcs_config_with_credentials(self):
        """Testa configuração GCS com credenciais"""
        config = GCSConfig(
            project_id="test-project",
            bucket_name="test-bucket",
            credentials_path="/path/to/credentials.json",
            credentials_json='{"type": "service_account"}'
        )
        
        assert config.credentials_path == "/path/to/credentials.json"
        assert config.credentials_json == '{"type": "service_account"}'


class TestGCSEncryption:
    """Testes para criptografia GCS"""
    
    def test_encryption_creation(self):
        """Testa criação do gerenciador de criptografia"""
        encryption = GCSEncryption()
        assert encryption.encryption_key is not None
        assert encryption.cipher is not None
    
    def test_encryption_with_custom_key(self):
        """Testa criptografia com chave customizada"""
        key = Fernet.generate_key()
        encryption = GCSEncryption(key)
        assert encryption.encryption_key == key
    
    def test_encrypt_decrypt_data(self):
        """Testa criptografia e descriptografia de dados"""
        encryption = GCSEncryption()
        test_data = b"test data for encryption"
        
        encrypted = encryption.encrypt_data(test_data)
        decrypted = encryption.decrypt_data(encrypted)
        
        assert encrypted != test_data
        assert decrypted == test_data
    
    def test_get_key_base64(self):
        """Testa obtenção da chave em base64"""
        encryption = GCSEncryption()
        key_b64 = encryption.get_key_base64()
        
        # Verifica se é base64 válido
        decoded = base64.b64decode(key_b64)
        assert len(decoded) == 32  # Tamanho da chave Fernet


class TestGCSCompression:
    """Testes para compressão GCS"""
    
    def test_compress_none(self):
        """Testa compressão NONE"""
        test_data = b"test data for compression"
        compressed = GCSCompression.compress_data(test_data, GCSCompressionType.NONE)
        assert compressed == test_data
    
    def test_compress_gzip(self):
        """Testa compressão GZIP"""
        test_data = b"test data for compression" * 100
        compressed = GCSCompression.compress_data(test_data, GCSCompressionType.GZIP)
        
        assert compressed != test_data
        assert len(compressed) < len(test_data)
        
        # Verifica se pode descomprimir
        decompressed = GCSCompression.decompress_data(compressed, GCSCompressionType.GZIP)
        assert decompressed == test_data
    
    def test_compress_lzma(self):
        """Testa compressão LZMA"""
        test_data = b"test data for compression" * 100
        compressed = GCSCompression.compress_data(test_data, GCSCompressionType.LZMA)
        
        assert compressed != test_data
        assert len(compressed) < len(test_data)
        
        # Verifica se pode descomprimir
        decompressed = GCSCompression.decompress_data(compressed, GCSCompressionType.LZMA)
        assert decompressed == test_data
    
    def test_invalid_compression_type(self):
        """Testa tipo de compressão inválido"""
        test_data = b"test data"
        
        with pytest.raises(ValueError, match="Tipo de compressão não suportado"):
            GCSCompression.compress_data(test_data, "invalid_type")


class TestGCSRateLimiter:
    """Testes para rate limiting GCS"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        return Mock()
    
    @pytest.fixture
    def config(self):
        """Configuração de teste"""
        return GCSConfig(project_id="test", bucket_name="test")
    
    @pytest.fixture
    def rate_limiter(self, mock_redis, config):
        """Rate limiter de teste"""
        return GCSRateLimiter(mock_redis, config)
    
    def test_rate_limit_check_allowed(self, rate_limiter, mock_redis):
        """Testa verificação de rate limit permitido"""
        mock_redis.get.return_value = "50"  # Abaixo do limite
        
        result = rate_limiter.check_rate_limit("user123")
        assert result is True
    
    def test_rate_limit_check_exceeded_minute(self, rate_limiter, mock_redis):
        """Testa verificação de rate limit excedido por minuto"""
        mock_redis.get.return_value = "150"  # Acima do limite
        
        result = rate_limiter.check_rate_limit("user123")
        assert result is False
    
    def test_rate_limit_check_exceeded_hour(self, rate_limiter, mock_redis):
        """Testa verificação de rate limit excedido por hora"""
        mock_redis.get.side_effect = ["50", "1500"]  # Minuto OK, hora excedida
        
        result = rate_limiter.check_rate_limit("user123")
        assert result is False
    
    def test_rate_limit_increment(self, rate_limiter, mock_redis):
        """Testa incremento do rate limit"""
        rate_limiter.increment_rate_limit("user123")
        
        # Verifica se incrementou contadores
        assert mock_redis.incr.call_count >= 2  # Minuto e hora


class TestGCSMetrics:
    """Testes para métricas GCS"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        return Mock()
    
    @pytest.fixture
    def metrics(self, mock_redis):
        """Métricas de teste"""
        return GCSMetrics(mock_redis)
    
    def test_record_operation(self, metrics, mock_redis):
        """Testa registro de operação"""
        metrics.record_operation("user123", "upload", True, 1024, 1.5)
        
        # Verifica se registrou no Redis
        assert mock_redis.hincrby.call_count >= 1
    
    def test_get_metrics(self, metrics, mock_redis):
        """Testa obtenção de métricas"""
        mock_redis.hgetall.return_value = {
            "total_operations": "10",
            "successful_operations": "8",
            "total_size": "10240",
            "total_time": "15.5"
        }
        
        result = metrics.get_metrics("user123", 24)
        
        assert "total_operations" in result
        assert "success_rate" in result
        assert "avg_file_size" in result
        assert "avg_operation_time" in result


class TestGCSProvider:
    """Testes para provedor GCS"""
    
    @pytest.fixture
    def config(self):
        """Configuração de teste"""
        return GCSConfig(
            project_id="test-project",
            bucket_name="test-bucket",
            region="us-central1"
        )
    
    @pytest.fixture
    def mock_redis(self):
        """Mock do Redis"""
        return Mock()
    
    @pytest.fixture
    def provider(self, config, mock_redis):
        """Provedor GCS de teste"""
        with patch('infrastructure.backup.inteligente.gcs_provider.storage'):
            return GCSProvider(config, mock_redis)
    
    def test_provider_initialization(self, config, mock_redis):
        """Testa inicialização do provedor"""
        with patch('infrastructure.backup.inteligente.gcs_provider.storage') as mock_storage:
            provider = GCSProvider(config, mock_redis)
            
            assert provider.config == config
            assert provider.redis_client == mock_redis
            assert provider.encryption is not None
            assert provider.rate_limiter is not None
            assert provider.metrics is not None
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, provider):
        """Testa upload de arquivo com sucesso"""
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file_path = temp_file.name
        
        try:
            # Mock do bucket e blob
            mock_blob = AsyncMock()
            mock_blob.upload_from_filename.return_value = None
            mock_blob.public_url = "https://storage.googleapis.com/test-bucket/test.txt"
            
            mock_bucket = Mock()
            mock_bucket.blob.return_value = mock_blob
            
            provider.client = Mock()
            provider.client.bucket.return_value = mock_bucket
            
            # Mock do rate limiter
            provider.rate_limiter.check_rate_limit.return_value = True
            
            result = await provider.upload_file(
                source_path=temp_file_path,
                destination_path="test.txt",
                backup_type=GCSBackupType.FULL,
                user_id="user123"
            )
            
            assert result.success is True
            assert result.backup_id is not None
            assert result.file_size > 0
            assert result.url is not None
            
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_upload_file_rate_limit_exceeded(self, provider):
        """Testa upload com rate limit excedido"""
        # Mock do rate limiter retornando False
        provider.rate_limiter.check_rate_limit.return_value = False
        
        result = await provider.upload_file(
            source_path="/nonexistent/file.txt",
            user_id="user123"
        )
        
        assert result.success is False
        assert "rate limit" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_upload_file_not_found(self, provider):
        """Testa upload de arquivo inexistente"""
        provider.rate_limiter.check_rate_limit.return_value = True
        
        result = await provider.upload_file(
            source_path="/nonexistent/file.txt",
            user_id="user123"
        )
        
        assert result.success is False
        assert "não encontrado" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_download_file_success(self, provider):
        """Testa download de arquivo com sucesso"""
        # Mock do bucket e blob
        mock_blob = AsyncMock()
        mock_blob.download_to_filename.return_value = None
        mock_blob.metadata = {"checksum": "test-checksum"}
        
        mock_bucket = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        provider.client = Mock()
        provider.client.bucket.return_value = mock_bucket
        
        # Mock do rate limiter
        provider.rate_limiter.check_rate_limit.return_value = True
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_dest_path = temp_file.name
        
        try:
            result = await provider.download_file(
                source_path="test.txt",
                destination_path=temp_dest_path,
                user_id="user123"
            )
            
            assert result["success"] is True
            assert result["file_size"] >= 0
            
        finally:
            os.unlink(temp_dest_path)
    
    @pytest.mark.asyncio
    async def test_list_backups(self, provider):
        """Testa listagem de backups"""
        # Mock do bucket
        mock_blob1 = Mock()
        mock_blob1.name = "backups/backup1.txt"
        mock_blob1.size = 1024
        mock_blob1.time_created = datetime.utcnow()
        mock_blob1.metadata = {"backup_id": "backup1"}
        
        mock_blob2 = Mock()
        mock_blob2.name = "backups/backup2.txt"
        mock_blob2.size = 2048
        mock_blob2.time_created = datetime.utcnow()
        mock_blob2.metadata = {"backup_id": "backup2"}
        
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
        
        provider.client = Mock()
        provider.client.bucket.return_value = mock_bucket
        
        result = await provider.list_backups(prefix="backups/")
        
        assert len(result) == 2
        assert isinstance(result[0], GCSBackupMetadata)
        assert result[0].backup_id == "backup1"
        assert result[1].backup_id == "backup2"
    
    @pytest.mark.asyncio
    async def test_delete_backup(self, provider):
        """Testa exclusão de backup"""
        # Mock do bucket e blob
        mock_blob = AsyncMock()
        mock_blob.delete.return_value = None
        
        mock_bucket = Mock()
        mock_bucket.blob.return_value = mock_blob
        
        provider.client = Mock()
        provider.client.bucket.return_value = mock_bucket
        
        # Mock do rate limiter
        provider.rate_limiter.check_rate_limit.return_value = True
        
        result = await provider.delete_backup(
            backup_path="backups/test.txt",
            user_id="user123"
        )
        
        assert result["success"] is True
        assert result["deleted_path"] == "backups/test.txt"
    
    def test_calculate_checksum(self, provider):
        """Testa cálculo de checksum"""
        test_data = b"test data for checksum"
        checksum = provider._calculate_checksum(test_data)
        
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA-256 hash length
    
    def test_generate_backup_id(self, provider):
        """Testa geração de ID de backup"""
        backup_id = provider._generate_backup_id("/path/to/file.txt")
        
        assert isinstance(backup_id, str)
        assert len(backup_id) > 0
        assert "file.txt" in backup_id
    
    def test_is_available(self, provider):
        """Testa verificação de disponibilidade"""
        provider.client = Mock()
        assert provider.is_available() is True
    
    def test_get_name(self, provider):
        """Testa obtenção do nome do provedor"""
        assert provider.get_name() == "Google Cloud Storage"


class TestGCSTemplates:
    """Testes para templates de configuração GCS"""
    
    def test_production_config(self):
        """Testa configuração de produção"""
        config = GCSTemplates.production_config("prod-project", "prod-bucket")
        
        assert config.project_id == "prod-project"
        assert config.bucket_name == "prod-bucket"
        assert config.region == "us-central1"
        assert config.max_retries == 5
        assert config.retention_days == 90
        assert config.versioning_enabled is True
    
    def test_development_config(self):
        """Testa configuração de desenvolvimento"""
        config = GCSTemplates.development_config("dev-project", "dev-bucket")
        
        assert config.project_id == "dev-project"
        assert config.bucket_name == "dev-bucket"
        assert config.region == "us-central1"
        assert config.max_retries == 3
        assert config.retention_days == 7
        assert config.versioning_enabled is False
    
    def test_backup_config(self):
        """Testa configuração de backup"""
        config = GCSTemplates.backup_config("backup-project", "backup-bucket", 60)
        
        assert config.project_id == "backup-project"
        assert config.bucket_name == "backup-bucket"
        assert config.retention_days == 60
        assert config.compression == GCSCompressionType.GZIP
        assert config.encryption_key is not None


class TestGCSBackupMetadata:
    """Testes para metadados de backup GCS"""
    
    def test_backup_metadata_creation(self):
        """Testa criação de metadados de backup"""
        metadata = GCSBackupMetadata(
            backup_id="test-backup-123",
            backup_type=GCSBackupType.FULL,
            source_path="/path/to/source",
            destination_path="backups/test-backup-123",
            file_size=1024,
            checksum="test-checksum"
        )
        
        assert metadata.backup_id == "test-backup-123"
        assert metadata.backup_type == GCSBackupType.FULL
        assert metadata.file_size == 1024
        assert metadata.checksum == "test-checksum"
    
    def test_backup_metadata_with_compression(self):
        """Testa metadados com compressão"""
        metadata = GCSBackupMetadata(
            backup_id="test-backup-123",
            backup_type=GCSBackupType.FULL,
            source_path="/path/to/source",
            destination_path="backups/test-backup-123",
            file_size=1024,
            compressed_size=512,
            checksum="test-checksum",
            compression_type=GCSCompressionType.GZIP
        )
        
        assert metadata.compressed_size == 512
        assert metadata.compression_type == GCSCompressionType.GZIP


class TestGCSBackupResult:
    """Testes para resultado de backup GCS"""
    
    def test_backup_result_success(self):
        """Testa resultado de backup bem-sucedido"""
        result = GCSBackupResult(
            success=True,
            backup_id="test-backup-123",
            file_size=1024,
            upload_time=1.5,
            checksum="test-checksum",
            url="https://storage.googleapis.com/test-bucket/test.txt"
        )
        
        assert result.success is True
        assert result.backup_id == "test-backup-123"
        assert result.file_size == 1024
        assert result.upload_time == 1.5
        assert result.url is not None
        assert result.error is None
    
    def test_backup_result_failure(self):
        """Testa resultado de backup com falha"""
        result = GCSBackupResult(
            success=False,
            backup_id="test-backup-123",
            file_size=0,
            upload_time=0.0,
            checksum="",
            error="Arquivo não encontrado"
        )
        
        assert result.success is False
        assert result.error == "Arquivo não encontrado"
        assert result.url is None


if __name__ == "__main__":
    pytest.main([__file__]) 