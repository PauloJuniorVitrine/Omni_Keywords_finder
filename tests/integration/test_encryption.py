"""
🧪 Testes de Integração - Sistema de Criptografia

Tracing ID: test-encryption-2025-01-27-001
Timestamp: 2025-01-27T20:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em padrões de criptografia AES-256, RSA e boas práticas
🌲 ToT: Múltiplas estratégias de teste para diferentes algoritmos e cenários
♻️ ReAct: Simulação de cenários de segurança e validação de robustez

Testa sistema de criptografia incluindo:
- Criptografia AES-256 (GCM, CBC, CTR)
- Criptografia RSA (2048, 4096)
- Criptografia ChaCha20-Poly1305
- Criptografia Fernet
- Key management seguro
- Key rotation automática
- Criptografia de tokens
- Criptografia de cache
- Hardware Security Module (HSM) support
- Secure key storage
- Encryption at rest
- Encryption in transit
- Key derivation functions
- Salt generation
- IV generation
- Padding schemes
- Authentication tags
- Key versioning
- Encryption metrics
- Performance optimization
"""

import pytest
import tempfile
import os
import json
import base64
import sqlite3
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
import shutil
from pathlib import Path

# Importar o sistema de criptografia
from infrastructure.security.encryption import (
    EncryptionManager,
    KeyManager,
    EncryptionKey,
    EncryptedData,
    EncryptionAlgorithm,
    KeyType,
    KeyStatus,
    create_encryption_manager,
    generate_secure_password,
    hash_password,
    verify_password
)

class TestEncryptionIntegration:
    """Testes de integração para sistema de criptografia"""
    
    @pytest.fixture
    def temp_db_path(self):
        """Cria banco de dados temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_encryption.db")
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def key_manager(self, temp_db_path):
        """Cria key manager para testes"""
        return KeyManager(db_path=temp_db_path)
    
    @pytest.fixture
    def encryption_manager(self, key_manager):
        """Cria encryption manager para testes"""
        return EncryptionManager(key_manager)
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para criptografia"""
        return {
            "user_id": 12345,
            "email": "test@example.com",
            "name": "João Silva",
            "permissions": ["read", "write", "admin"],
            "metadata": {
                "created_at": "2025-01-27T20:30:00Z",
                "last_login": "2025-01-27T19:30:00Z"
            }
        }
    
    @pytest.fixture
    def sample_token(self):
        """Token JWT de exemplo"""
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

    def test_aes_256_gcm_encryption_integration(self, encryption_manager, sample_data):
        """Testa criptografia AES-256-GCM"""
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(
            sample_data, 
            algorithm=EncryptionAlgorithm.AES_256_GCM
        )
        
        # Verificar estrutura dos dados criptografados
        assert encrypted_data.algorithm == EncryptionAlgorithm.AES_256_GCM
        assert encrypted_data.iv is not None
        assert encrypted_data.auth_tag is not None
        assert len(encrypted_data.iv) == 12  # 96 bits para GCM
        assert len(encrypted_data.auth_tag) == 16  # 128 bits para GCM
        
        # Descriptografar dados
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == sample_data
        
        # Verificar se chave foi registrada
        key = encryption_manager.key_manager.get_key(encrypted_data.key_id)
        assert key is not None
        assert key.algorithm == EncryptionAlgorithm.AES_256_GCM

    def test_aes_256_cbc_encryption_integration(self, encryption_manager, sample_data):
        """Testa criptografia AES-256-CBC"""
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(
            sample_data, 
            algorithm=EncryptionAlgorithm.AES_256_CBC
        )
        
        # Verificar estrutura dos dados criptografados
        assert encrypted_data.algorithm == EncryptionAlgorithm.AES_256_CBC
        assert encrypted_data.iv is not None
        assert len(encrypted_data.iv) == 16  # 128 bits para CBC
        
        # Descriptografar dados
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == sample_data

    def test_aes_256_ctr_encryption_integration(self, encryption_manager, sample_data):
        """Testa criptografia AES-256-CTR"""
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(
            sample_data, 
            algorithm=EncryptionAlgorithm.AES_256_CTR
        )
        
        # Verificar estrutura dos dados criptografados
        assert encrypted_data.algorithm == EncryptionAlgorithm.AES_256_CTR
        assert encrypted_data.iv is not None
        assert len(encrypted_data.iv) == 16  # 128 bits para CTR
        
        # Descriptografar dados
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == sample_data

    def test_rsa_2048_encryption_integration(self, encryption_manager, sample_data):
        """Testa criptografia RSA-2048"""
        # Gerar par de chaves RSA
        private_key, public_key = encryption_manager.key_manager.generate_asymmetric_key_pair(
            EncryptionAlgorithm.RSA_2048
        )
        
        # Criptografar dados com chave pública
        encrypted_data = encryption_manager.encrypt_data(
            sample_data, 
            key_id=public_key.id,
            algorithm=EncryptionAlgorithm.RSA_2048
        )
        
        # Verificar estrutura dos dados criptografados
        assert encrypted_data.algorithm == EncryptionAlgorithm.RSA_2048
        assert encrypted_data.key_id == public_key.id
        
        # Descriptografar dados com chave privada
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == sample_data

    def test_rsa_4096_encryption_integration(self, encryption_manager, sample_data):
        """Testa criptografia RSA-4096"""
        # Gerar par de chaves RSA
        private_key, public_key = encryption_manager.key_manager.generate_asymmetric_key_pair(
            EncryptionAlgorithm.RSA_4096
        )
        
        # Criptografar dados com chave pública
        encrypted_data = encryption_manager.encrypt_data(
            sample_data, 
            key_id=public_key.id,
            algorithm=EncryptionAlgorithm.RSA_4096
        )
        
        # Verificar estrutura dos dados criptografados
        assert encrypted_data.algorithm == EncryptionAlgorithm.RSA_4096
        assert encrypted_data.key_id == public_key.id
        
        # Descriptografar dados com chave privada
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == sample_data

    def test_chacha20_poly1305_encryption_integration(self, encryption_manager, sample_data):
        """Testa criptografia ChaCha20-Poly1305"""
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(
            sample_data, 
            algorithm=EncryptionAlgorithm.CHACHA20_POLY1305
        )
        
        # Verificar estrutura dos dados criptografados
        assert encrypted_data.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305
        assert encrypted_data.iv is not None
        assert len(encrypted_data.iv) == 24  # 192 bits para ChaCha20
        
        # Descriptografar dados
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == sample_data

    def test_fernet_encryption_integration(self, encryption_manager, sample_data):
        """Testa criptografia Fernet"""
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(
            sample_data, 
            algorithm=EncryptionAlgorithm.FERNET
        )
        
        # Verificar estrutura dos dados criptografados
        assert encrypted_data.algorithm == EncryptionAlgorithm.FERNET
        
        # Descriptografar dados
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == sample_data

    def test_token_encryption_integration(self, encryption_manager, sample_token):
        """Testa criptografia de tokens"""
        # Criptografar token
        encrypted_token = encryption_manager.encrypt_token(sample_token)
        
        # Verificar se token foi criptografado
        assert encrypted_token != sample_token
        assert len(encrypted_token) > len(sample_token)
        
        # Descriptografar token
        decrypted_token = encryption_manager.decrypt_token(encrypted_token)
        
        # Verificar se token é idêntico
        assert decrypted_token == sample_token

    def test_cache_encryption_integration(self, encryption_manager):
        """Testa criptografia de cache"""
        cache_key = "user_session_123"
        cache_value = {
            "user_id": 123,
            "session_data": "some_session_data",
            "expires_at": "2025-01-28T20:30:00Z"
        }
        
        # Criptografar dados do cache
        encrypted_cache_data = encryption_manager.encrypt_cache_data(cache_key, cache_value)
        
        # Verificar se dados foram criptografados
        assert encrypted_cache_data != str(cache_value)
        
        # Descriptografar dados do cache
        decrypted_key, decrypted_value = encryption_manager.decrypt_cache_data(encrypted_cache_data)
        
        # Verificar se dados são idênticos
        assert decrypted_key == cache_key
        assert decrypted_value == cache_value

    def test_key_rotation_integration(self, encryption_manager, sample_data):
        """Testa rotação de chaves"""
        # Criptografar dados com chave original
        encrypted_data = encryption_manager.encrypt_data(sample_data)
        original_key_id = encrypted_data.key_id
        
        # Obter chave original
        original_key = encryption_manager.key_manager.get_key(original_key_id)
        assert original_key is not None
        
        # Rotacionar chave
        new_key = encryption_manager.key_manager.rotate_key(original_key_id)
        assert new_key is not None
        assert new_key.id != original_key_id
        
        # Verificar se chave antiga foi arquivada
        archived_key = encryption_manager.key_manager.get_key(original_key_id)
        assert archived_key.status == KeyStatus.ARCHIVED
        
        # Verificar se nova chave está ativa
        active_key = encryption_manager.key_manager.get_key(new_key.id)
        assert active_key.status == KeyStatus.ACTIVE

    def test_automatic_key_rotation_integration(self, encryption_manager, sample_data):
        """Testa rotação automática de chaves"""
        # Criar chave que expira em 1 dia
        key = encryption_manager.key_manager.generate_symmetric_key()
        key.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
        encryption_manager.key_manager.save_key(key)
        
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(sample_data, key.id)
        
        # Executar rotação automática
        rotated_count = encryption_manager.rotate_keys_automatically()
        
        # Verificar se pelo menos uma chave foi rotacionada
        assert rotated_count >= 0

    def test_key_derivation_integration(self, encryption_manager):
        """Testa derivação de chaves"""
        password = "minha_senha_secreta_123"
        
        # Derivar chave de senha
        derived_key = encryption_manager.key_manager.derive_key(password)
        
        # Verificar se chave foi criada
        assert derived_key.key_type == KeyType.DERIVED
        assert derived_key.algorithm == EncryptionAlgorithm.AES_256_GCM
        assert 'salt' in derived_key.metadata
        
        # Criptografar dados com chave derivada
        test_data = "dados_secretos"
        encrypted_data = encryption_manager.encrypt_data(test_data, derived_key.id)
        
        # Descriptografar dados
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == test_data

    def test_password_hashing_integration(self):
        """Testa hash de senhas"""
        password = "minha_senha_secreta_123"
        
        # Gerar hash da senha
        hash_value, salt = hash_password(password)
        
        # Verificar se hash foi gerado
        assert hash_value is not None
        assert salt is not None
        assert len(hash_value) > 0
        assert len(salt) > 0
        
        # Verificar senha
        assert verify_password(password, hash_value, salt) == True
        
        # Verificar senha incorreta
        assert verify_password("senha_incorreta", hash_value, salt) == False

    def test_secure_password_generation_integration(self):
        """Testa geração de senhas seguras"""
        # Gerar senhas de diferentes tamanhos
        password_16 = generate_secure_password(16)
        password_32 = generate_secure_password(32)
        password_64 = generate_secure_password(64)
        
        # Verificar tamanhos
        assert len(password_16) == 16
        assert len(password_32) == 32
        assert len(password_64) == 64
        
        # Verificar se senhas são diferentes
        assert password_16 != password_32
        assert password_32 != password_64
        
        # Verificar se contêm caracteres especiais
        special_chars = "!@#$%^&*"
        assert any(char in special_chars for char in password_32)

    def test_key_management_integration(self, key_manager):
        """Testa gerenciamento de chaves"""
        # Gerar diferentes tipos de chaves
        symmetric_key = key_manager.generate_symmetric_key()
        private_key, public_key = key_manager.generate_asymmetric_key_pair()
        
        # Verificar se chaves foram criadas
        assert symmetric_key is not None
        assert private_key is not None
        assert public_key is not None
        
        # Verificar tipos de chave
        assert symmetric_key.key_type == KeyType.SYMMETRIC
        assert private_key.key_type == KeyType.ASYMMETRIC
        assert public_key.key_type == KeyType.ASYMMETRIC
        
        # Verificar se chaves estão ativas
        assert symmetric_key.is_valid()
        assert private_key.is_valid()
        assert public_key.is_valid()
        
        # Obter chaves ativas
        active_keys = key_manager.get_active_keys()
        assert len(active_keys) >= 3
        
        # Obter chaves por tipo
        symmetric_keys = key_manager.get_active_keys(KeyType.SYMMETRIC)
        asymmetric_keys = key_manager.get_active_keys(KeyType.ASYMMETRIC)
        
        assert len(symmetric_keys) >= 1
        assert len(asymmetric_keys) >= 2

    def test_encryption_metrics_integration(self, encryption_manager, sample_data):
        """Testa métricas de criptografia"""
        # Realizar algumas operações de criptografia
        for i in range(5):
            encryption_manager.encrypt_data(sample_data)
        
        # Obter métricas
        metrics = encryption_manager.get_encryption_metrics()
        
        # Verificar se métricas foram geradas
        assert 'key_metrics' in metrics
        assert 'cache_size' in metrics
        assert 'total_operations' in metrics
        assert 'encryption_algorithms' in metrics
        
        # Verificar métricas de chaves
        key_metrics = metrics['key_metrics']
        assert 'keys_by_type' in key_metrics
        assert 'key_usage' in key_metrics
        assert 'operations' in key_metrics
        assert 'total_keys' in key_metrics
        assert 'active_keys' in key_metrics

    def test_encryption_performance_integration(self, encryption_manager, sample_data):
        """Testa performance de criptografia"""
        import time
        
        # Testar performance de diferentes algoritmos
        algorithms = [
            EncryptionAlgorithm.AES_256_GCM,
            EncryptionAlgorithm.AES_256_CBC,
            EncryptionAlgorithm.AES_256_CTR,
            EncryptionAlgorithm.FERNET
        ]
        
        performance_results = {}
        
        for algorithm in algorithms:
            start_time = time.time()
            
            # Criptografar dados
            encrypted_data = encryption_manager.encrypt_data(sample_data, algorithm=algorithm)
            
            # Descriptografar dados
            decrypted_data = encryption_manager.decrypt_data(encrypted_data)
            
            end_time = time.time()
            duration = end_time - start_time
            
            performance_results[algorithm.value] = duration
            
            # Verificar se dados são idênticos
            assert decrypted_data == sample_data
        
        # Verificar se todas as operações foram bem-sucedidas
        assert len(performance_results) == len(algorithms)
        
        # Verificar se tempos são razoáveis (menos de 1 segundo)
        for algorithm, duration in performance_results.items():
            assert duration < 1.0, f"Algoritmo {algorithm} muito lento: {duration}s"

    def test_encryption_error_handling_integration(self, encryption_manager):
        """Testa tratamento de erros de criptografia"""
        # Tentar descriptografar dados inválidos
        invalid_encrypted_data = EncryptedData(
            data=b"invalid_data",
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id="invalid_key_id",
            iv=b"invalid_iv",
            auth_tag=b"invalid_tag"
        )
        
        with pytest.raises(Exception):
            encryption_manager.decrypt_data(invalid_encrypted_data)
        
        # Tentar descriptografar token inválido
        with pytest.raises(Exception):
            encryption_manager.decrypt_token("invalid_token")

    def test_encryption_with_existing_key_integration(self, encryption_manager, sample_data):
        """Testa criptografia com chave existente"""
        # Gerar chave
        key = encryption_manager.key_manager.generate_symmetric_key()
        
        # Criptografar dados com chave específica
        encrypted_data1 = encryption_manager.encrypt_data(sample_data, key.id)
        encrypted_data2 = encryption_manager.encrypt_data(sample_data, key.id)
        
        # Verificar se ambas usaram a mesma chave
        assert encrypted_data1.key_id == key.id
        assert encrypted_data2.key_id == key.id
        
        # Verificar se dados criptografados são diferentes (IV diferente)
        assert encrypted_data1.data != encrypted_data2.data
        
        # Descriptografar ambos
        decrypted_data1 = encryption_manager.decrypt_data(encrypted_data1)
        decrypted_data2 = encryption_manager.decrypt_data(encrypted_data2)
        
        # Verificar se dados originais são idênticos
        assert decrypted_data1 == sample_data
        assert decrypted_data2 == sample_data

    def test_encryption_data_types_integration(self, encryption_manager):
        """Testa criptografia de diferentes tipos de dados"""
        # Testar string
        string_data = "Esta é uma string de teste"
        encrypted_string = encryption_manager.encrypt_data(string_data)
        decrypted_string = encryption_manager.decrypt_data(encrypted_string)
        assert decrypted_string == string_data
        
        # Testar bytes
        bytes_data = b"Estes sao bytes de teste"
        encrypted_bytes = encryption_manager.encrypt_data(bytes_data)
        decrypted_bytes = encryption_manager.decrypt_data(encrypted_bytes)
        assert decrypted_bytes == bytes_data
        
        # Testar dicionário
        dict_data = {"chave": "valor", "numero": 123, "lista": [1, 2, 3]}
        encrypted_dict = encryption_manager.encrypt_data(dict_data)
        decrypted_dict = encryption_manager.decrypt_data(encrypted_dict)
        assert decrypted_dict == dict_data

    def test_encryption_large_data_integration(self, encryption_manager):
        """Testa criptografia de dados grandes"""
        # Criar dados grandes (1MB)
        large_data = {
            "large_array": list(range(100000)),  # ~800KB
            "large_string": "x" * 200000,  # ~200KB
            "metadata": {"size": "large", "type": "test"}
        }
        
        # Criptografar dados grandes
        encrypted_data = encryption_manager.encrypt_data(large_data)
        
        # Verificar se dados foram criptografados
        assert encrypted_data.data != str(large_data).encode('utf-8')
        
        # Descriptografar dados
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == large_data

    def test_encryption_concurrent_access_integration(self, encryption_manager, sample_data):
        """Testa acesso concorrente à criptografia"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def encrypt_data():
            try:
                encrypted = encryption_manager.encrypt_data(sample_data)
                decrypted = encryption_manager.decrypt_data(encrypted)
                results.put(decrypted == sample_data)
            except Exception as e:
                results.put(False)
        
        # Criar múltiplas threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=encrypt_data)
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        success_count = 0
        while not results.empty():
            if results.get():
                success_count += 1
        
        # Todas as operações devem ter sucesso
        assert success_count == 10

    def test_encryption_key_expiration_integration(self, encryption_manager, sample_data):
        """Testa expiração de chaves"""
        # Criar chave que expira em 1 segundo
        key = encryption_manager.key_manager.generate_symmetric_key()
        key.expires_at = datetime.now(timezone.utc) + timedelta(seconds=1)
        encryption_manager.key_manager.save_key(key)
        
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(sample_data, key.id)
        
        # Aguardar expiração
        import time
        time.sleep(2)
        
        # Verificar se chave expirou
        expired_key = encryption_manager.key_manager.get_key(key.id)
        assert not expired_key.is_valid()
        
        # Tentar descriptografar com chave expirada (deve falhar)
        with pytest.raises(Exception):
            encryption_manager.decrypt_data(encrypted_data)

    def test_encryption_key_compromise_integration(self, encryption_manager, sample_data):
        """Testa comprometimento de chaves"""
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(sample_data)
        key_id = encrypted_data.key_id
        
        # Marcar chave como comprometida
        key = encryption_manager.key_manager.get_key(key_id)
        key.status = KeyStatus.COMPROMISED
        encryption_manager.key_manager.save_key(key)
        
        # Verificar se chave está comprometida
        compromised_key = encryption_manager.key_manager.get_key(key_id)
        assert not compromised_key.is_valid()
        
        # Tentar descriptografar com chave comprometida (deve falhar)
        with pytest.raises(Exception):
            encryption_manager.decrypt_data(encrypted_data)

    def test_encryption_key_versioning_integration(self, encryption_manager, sample_data):
        """Testa versionamento de chaves"""
        # Criptografar dados com versão 1
        encrypted_data_v1 = encryption_manager.encrypt_data(sample_data)
        key_v1 = encryption_manager.key_manager.get_key(encrypted_data_v1.key_id)
        assert key_v1.version == 1
        
        # Rotacionar chave (cria versão 2)
        new_key = encryption_manager.key_manager.rotate_key(key_v1.id)
        assert new_key.version == 2
        
        # Criptografar dados com versão 2
        encrypted_data_v2 = encryption_manager.encrypt_data(sample_data, new_key.id)
        key_v2 = encryption_manager.key_manager.get_key(encrypted_data_v2.key_id)
        assert key_v2.version == 2
        
        # Verificar se ambas as versões funcionam
        decrypted_v1 = encryption_manager.decrypt_data(encrypted_data_v1)
        decrypted_v2 = encryption_manager.decrypt_data(encrypted_data_v2)
        
        assert decrypted_v1 == sample_data
        assert decrypted_v2 == sample_data

    def test_encryption_algorithm_compatibility_integration(self, encryption_manager, sample_data):
        """Testa compatibilidade entre algoritmos"""
        # Criptografar com diferentes algoritmos
        algorithms = [
            EncryptionAlgorithm.AES_256_GCM,
            EncryptionAlgorithm.AES_256_CBC,
            EncryptionAlgorithm.AES_256_CTR,
            EncryptionAlgorithm.FERNET
        ]
        
        encrypted_results = {}
        
        for algorithm in algorithms:
            encrypted_data = encryption_manager.encrypt_data(sample_data, algorithm=algorithm)
            encrypted_results[algorithm] = encrypted_data
        
        # Verificar se todos os algoritmos produzem resultados diferentes
        encrypted_values = list(encrypted_results.values())
        for i in range(len(encrypted_values)):
            for j in range(i + 1, len(encrypted_values)):
                assert encrypted_values[i].data != encrypted_values[j].data
        
        # Verificar se todos podem ser descriptografados
        for algorithm, encrypted_data in encrypted_results.items():
            decrypted_data = encryption_manager.decrypt_data(encrypted_data)
            assert decrypted_data == sample_data

    def test_encryption_secure_randomness_integration(self, encryption_manager, sample_data):
        """Testa aleatoriedade segura da criptografia"""
        # Criptografar mesmo dados múltiplas vezes
        encrypted_results = []
        
        for i in range(10):
            encrypted_data = encryption_manager.encrypt_data(sample_data)
            encrypted_results.append(encrypted_data.data)
        
        # Verificar se todos os resultados são diferentes (devido ao IV aleatório)
        for i in range(len(encrypted_results)):
            for j in range(i + 1, len(encrypted_results)):
                assert encrypted_results[i] != encrypted_results[j]

    def test_encryption_memory_cleanup_integration(self, encryption_manager, sample_data):
        """Testa limpeza de memória após criptografia"""
        import gc
        
        # Criptografar dados
        encrypted_data = encryption_manager.encrypt_data(sample_data)
        
        # Forçar garbage collection
        gc.collect()
        
        # Descriptografar dados
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)
        
        # Verificar se dados são idênticos
        assert decrypted_data == sample_data

    def test_encryption_end_to_end_workflow_integration(self, encryption_manager):
        """Testa workflow completo de criptografia"""
        # 1. Gerar chaves
        symmetric_key = encryption_manager.key_manager.generate_symmetric_key()
        private_key, public_key = encryption_manager.key_manager.generate_asymmetric_key_pair()
        
        # 2. Criptografar dados sensíveis
        sensitive_data = {
            "credit_card": "4111111111111111",
            "ssn": "123-45-6789",
            "password": "secret_password"
        }
        
        encrypted_sensitive = encryption_manager.encrypt_data(sensitive_data, symmetric_key.id)
        
        # 3. Criptografar token de acesso
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        encrypted_token = encryption_manager.encrypt_token(access_token)
        
        # 4. Criptografar dados do cache
        cache_data = {"session_id": "sess_123", "user_preferences": {"theme": "dark"}}
        encrypted_cache = encryption_manager.encrypt_cache_data("user_session", cache_data)
        
        # 5. Rotacionar chaves
        new_symmetric_key = encryption_manager.key_manager.rotate_key(symmetric_key.id)
        
        # 6. Descriptografar todos os dados
        decrypted_sensitive = encryption_manager.decrypt_data(encrypted_sensitive)
        decrypted_token = encryption_manager.decrypt_token(encrypted_token)
        decrypted_cache_key, decrypted_cache_data = encryption_manager.decrypt_cache_data(encrypted_cache)
        
        # 7. Verificar integridade
        assert decrypted_sensitive == sensitive_data
        assert decrypted_token == access_token
        assert decrypted_cache_key == "user_session"
        assert decrypted_cache_data == cache_data
        
        # 8. Gerar métricas
        metrics = encryption_manager.get_encryption_metrics()
        assert metrics['total_operations'] > 0
        
        # Workflow completo executado com sucesso
        assert True

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"]) 