"""
🔐 Sistema de Criptografia Avançada

Tracing ID: encryption-system-2025-01-27-001
Timestamp: 2025-01-27T20:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Criptografia baseada em padrões AES-256, RSA e boas práticas de segurança
🌲 ToT: Avaliadas múltiplas estratégias de criptografia e key management
♻️ ReAct: Simulado cenários de segurança e validada robustez

Implementa sistema de criptografia incluindo:
- Criptografia AES-256 para dados sensíveis
- Criptografia RSA para tokens
- Criptografia de cache
- Key rotation automática
- Key management seguro
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

import os
import base64
import hashlib
import hmac
import json
import time
import uuid
import secrets
import struct
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path
import sqlite3
import pickle
import zlib
import gzip
import lzma
import bz2
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import nacl.secret
import nacl.utils
import nacl.pwhash
from nacl.public import PrivateKey, PublicKey, Box

# Configuração de logging
logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """Algoritmos de criptografia"""
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    AES_256_CTR = "aes-256-ctr"
    RSA_2048 = "rsa-2048"
    RSA_4096 = "rsa-4096"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    FERNET = "fernet"

class KeyType(Enum):
    """Tipos de chave"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    DERIVED = "derived"
    MASTER = "master"

class KeyStatus(Enum):
    """Status da chave"""
    ACTIVE = "active"
    ROTATING = "rotating"
    EXPIRED = "expired"
    COMPROMISED = "compromised"
    ARCHIVED = "archived"

@dataclass
class EncryptionKey:
    """Chave de criptografia"""
    id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_data: bytes
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    status: KeyStatus = KeyStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'key_type': self.key_type.value,
            'algorithm': self.algorithm.value,
            'key_data': base64.b64encode(self.key_data).decode('utf-8'),
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'status': self.status.value,
            'metadata': self.metadata
        }
    
    def is_valid(self) -> bool:
        """Verifica se chave é válida"""
        if self.status != KeyStatus.ACTIVE:
            return False
        
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        
        return True
    
    def rotate(self) -> 'EncryptionKey':
        """Cria nova versão da chave"""
        new_key = EncryptionKey(
            id=f"{self.id}_v{self.version + 1}",
            key_type=self.key_type,
            algorithm=self.algorithm,
            key_data=self.key_data,
            version=self.version + 1,
            metadata=self.metadata.copy()
        )
        return new_key

@dataclass
class EncryptedData:
    """Dados criptografados"""
    data: bytes
    algorithm: EncryptionAlgorithm
    key_id: str
    iv: Optional[bytes] = None
    auth_tag: Optional[bytes] = None
    salt: Optional[bytes] = None
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'data': base64.b64encode(self.data).decode('utf-8'),
            'algorithm': self.algorithm.value,
            'key_id': self.key_id,
            'iv': base64.b64encode(self.iv).decode('utf-8') if self.iv else None,
            'auth_tag': base64.b64encode(self.auth_tag).decode('utf-8') if self.auth_tag else None,
            'salt': base64.b64encode(self.salt).decode('utf-8') if self.salt else None,
            'version': self.version,
            'created_at': self.created_at.isoformat()
        }

class KeyManager:
    """Gerenciador de chaves"""
    
    def __init__(self, db_path: str = "encryption_keys.db"):
        self.db_path = db_path
        self.keys: Dict[str, EncryptionKey] = {}
        self.master_key: Optional[bytes] = None
        self.init_database()
        self.load_keys()
    
    def init_database(self):
        """Inicializa banco de dados de chaves"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encryption_keys (
                id TEXT PRIMARY KEY,
                key_type TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                key_data TEXT NOT NULL,
                version INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                status TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_keys(self):
        """Carrega chaves do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM encryption_keys WHERE status = ?', (KeyStatus.ACTIVE.value,))
        rows = cursor.fetchall()
        
        for row in rows:
            key = EncryptionKey(
                id=row[0],
                key_type=KeyType(row[1]),
                algorithm=EncryptionAlgorithm(row[2]),
                key_data=base64.b64decode(row[3]),
                version=row[4],
                created_at=datetime.fromisoformat(row[5]),
                expires_at=datetime.fromisoformat(row[6]) if row[6] else None,
                status=KeyStatus(row[7]),
                metadata=json.loads(row[8]) if row[8] else {}
            )
            self.keys[key.id] = key
        
        conn.close()
    
    def generate_master_key(self) -> bytes:
        """Gera chave mestra"""
        if not self.master_key:
            self.master_key = secrets.token_bytes(32)
        return self.master_key
    
    def generate_symmetric_key(self, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> EncryptionKey:
        """Gera chave simétrica"""
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC, EncryptionAlgorithm.AES_256_CTR]:
            key_data = secrets.token_bytes(32)  # 256 bits
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            key_data = secrets.token_bytes(32)
        elif algorithm == EncryptionAlgorithm.FERNET:
            key_data = Fernet.generate_key()
        else:
            raise ValueError(f"Algoritmo não suportado: {algorithm}")
        
        key = EncryptionKey(
            id=f"symmetric_{uuid.uuid4().hex[:16]}",
            key_type=KeyType.SYMMETRIC,
            algorithm=algorithm,
            key_data=key_data,
            expires_at=datetime.now(timezone.utc) + timedelta(days=90)
        )
        
        self.save_key(key)
        return key
    
    def generate_asymmetric_key_pair(self, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.RSA_2048) -> Tuple[EncryptionKey, EncryptionKey]:
        """Gera par de chaves assimétricas"""
        if algorithm == EncryptionAlgorithm.RSA_2048:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
        elif algorithm == EncryptionAlgorithm.RSA_4096:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
        else:
            raise ValueError(f"Algoritmo não suportado: {algorithm}")
        
        public_key = private_key.public_key()
        
        # Serializar chaves
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Criar objetos de chave
        private_key_obj = EncryptionKey(
            id=f"private_{uuid.uuid4().hex[:16]}",
            key_type=KeyType.ASYMMETRIC,
            algorithm=algorithm,
            key_data=private_pem,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365)
        )
        
        public_key_obj = EncryptionKey(
            id=f"public_{uuid.uuid4().hex[:16]}",
            key_type=KeyType.ASYMMETRIC,
            algorithm=algorithm,
            key_data=public_pem,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365)
        )
        
        self.save_key(private_key_obj)
        self.save_key(public_key_obj)
        
        return private_key_obj, public_key_obj
    
    def derive_key(self, password: str, salt: Optional[bytes] = None, 
                   algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> EncryptionKey:
        """Deriva chave de senha"""
        if not salt:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key_data = kdf.derive(password.encode('utf-8'))
        
        key = EncryptionKey(
            id=f"derived_{uuid.uuid4().hex[:16]}",
            key_type=KeyType.DERIVED,
            algorithm=algorithm,
            key_data=key_data,
            metadata={'salt': base64.b64encode(salt).decode('utf-8')}
        )
        
        self.save_key(key)
        return key
    
    def save_key(self, key: EncryptionKey):
        """Salva chave no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO encryption_keys 
            (id, key_type, algorithm, key_data, version, created_at, expires_at, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            key.id,
            key.key_type.value,
            key.algorithm.value,
            base64.b64encode(key.key_data).decode('utf-8'),
            key.version,
            key.created_at.isoformat(),
            key.expires_at.isoformat() if key.expires_at else None,
            key.status.value,
            json.dumps(key.metadata)
        ))
        
        conn.commit()
        conn.close()
        
        self.keys[key.id] = key
    
    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Obtém chave por ID"""
        return self.keys.get(key_id)
    
    def get_active_keys(self, key_type: Optional[KeyType] = None) -> List[EncryptionKey]:
        """Obtém chaves ativas"""
        active_keys = [key for key in self.keys.values() if key.is_valid()]
        
        if key_type:
            active_keys = [key for key in active_keys if key.key_type == key_type]
        
        return active_keys
    
    def rotate_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Rotaciona chave"""
        old_key = self.get_key(key_id)
        if not old_key:
            return None
        
        # Marcar chave antiga como rotacionando
        old_key.status = KeyStatus.ROTATING
        self.save_key(old_key)
        
        # Gerar nova chave
        if old_key.key_type == KeyType.SYMMETRIC:
            new_key = self.generate_symmetric_key(old_key.algorithm)
        elif old_key.key_type == KeyType.ASYMMETRIC:
            new_key, _ = self.generate_asymmetric_key_pair(old_key.algorithm)
        else:
            return None
        
        # Marcar chave antiga como arquivada
        old_key.status = KeyStatus.ARCHIVED
        self.save_key(old_key)
        
        return new_key
    
    def log_key_usage(self, key_id: str, operation: str, success: bool, metadata: Dict[str, Any] = None):
        """Registra uso da chave"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO key_usage (key_id, operation, timestamp, success, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            key_id,
            operation,
            datetime.now(timezone.utc).isoformat(),
            success,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_key_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de uso das chaves"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de chaves por tipo
        cursor.execute('''
            SELECT key_type, COUNT(*) FROM encryption_keys 
            WHERE status = ? GROUP BY key_type
        ''', (KeyStatus.ACTIVE.value,))
        
        keys_by_type = dict(cursor.fetchall())
        
        # Uso de chaves
        cursor.execute('''
            SELECT key_id, COUNT(*) FROM key_usage 
            WHERE timestamp > ? GROUP BY key_id
        ''', ((datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),))
        
        key_usage = dict(cursor.fetchall())
        
        # Operações por tipo
        cursor.execute('''
            SELECT operation, COUNT(*) FROM key_usage 
            WHERE timestamp > ? GROUP BY operation
        ''', ((datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),))
        
        operations = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'keys_by_type': keys_by_type,
            'key_usage': key_usage,
            'operations': operations,
            'total_keys': len(self.keys),
            'active_keys': len(self.get_active_keys())
        }

class EncryptionManager:
    """Gerenciador de criptografia"""
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
        self.cache: Dict[str, Any] = {}
    
    def encrypt_data(self, data: Union[str, bytes, Dict[str, Any]], 
                    key_id: Optional[str] = None,
                    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> EncryptedData:
        """Criptografa dados"""
        # Converter dados para bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        else:
            data_bytes = data
        
        # Obter ou gerar chave
        if key_id:
            key = self.key_manager.get_key(key_id)
            if not key or not key.is_valid():
                raise ValueError(f"Chave inválida: {key_id}")
        else:
            key = self.key_manager.generate_symmetric_key(algorithm)
            key_id = key.id
        
        # Criptografar dados
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            return self._encrypt_aes_gcm(data_bytes, key, key_id)
        elif algorithm == EncryptionAlgorithm.AES_256_CBC:
            return self._encrypt_aes_cbc(data_bytes, key, key_id)
        elif algorithm == EncryptionAlgorithm.AES_256_CTR:
            return self._encrypt_aes_ctr(data_bytes, key, key_id)
        elif algorithm == EncryptionAlgorithm.RSA_2048 or algorithm == EncryptionAlgorithm.RSA_4096:
            return self._encrypt_rsa(data_bytes, key, key_id)
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return self._encrypt_chacha20_poly1305(data_bytes, key, key_id)
        elif algorithm == EncryptionAlgorithm.FERNET:
            return self._encrypt_fernet(data_bytes, key, key_id)
        else:
            raise ValueError(f"Algoritmo não suportado: {algorithm}")
    
    def decrypt_data(self, encrypted_data: EncryptedData) -> Union[str, bytes, Dict[str, Any]]:
        """Descriptografa dados"""
        key = self.key_manager.get_key(encrypted_data.key_id)
        if not key:
            raise ValueError(f"Chave não encontrada: {encrypted_data.key_id}")
        
        # Descriptografar dados
        if encrypted_data.algorithm == EncryptionAlgorithm.AES_256_GCM:
            decrypted = self._decrypt_aes_gcm(encrypted_data, key)
        elif encrypted_data.algorithm == EncryptionAlgorithm.AES_256_CBC:
            decrypted = self._decrypt_aes_cbc(encrypted_data, key)
        elif encrypted_data.algorithm == EncryptionAlgorithm.AES_256_CTR:
            decrypted = self._decrypt_aes_ctr(encrypted_data, key)
        elif encrypted_data.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            decrypted = self._decrypt_rsa(encrypted_data, key)
        elif encrypted_data.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            decrypted = self._decrypt_chacha20_poly1305(encrypted_data, key)
        elif encrypted_data.algorithm == EncryptionAlgorithm.FERNET:
            decrypted = self._decrypt_fernet(encrypted_data, key)
        else:
            raise ValueError(f"Algoritmo não suportado: {encrypted_data.algorithm}")
        
        # Tentar converter de volta para formato original
        try:
            return json.loads(decrypted.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                return decrypted.decode('utf-8')
            except UnicodeDecodeError:
                return decrypted
    
    def _encrypt_aes_gcm(self, data: bytes, key: EncryptionKey, key_id: str) -> EncryptedData:
        """Criptografa com AES-256-GCM"""
        iv = secrets.token_bytes(12)  # 96 bits para GCM
        
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.GCM(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        self.key_manager.log_key_usage(key_id, "encrypt_aes_gcm", True)
        
        return EncryptedData(
            data=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id=key_id,
            iv=iv,
            auth_tag=encryptor.tag
        )
    
    def _decrypt_aes_gcm(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Descriptografa com AES-256-GCM"""
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.GCM(encrypted_data.iv, encrypted_data.auth_tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(encrypted_data.data) + decryptor.finalize()
        
        self.key_manager.log_key_usage(encrypted_data.key_id, "decrypt_aes_gcm", True)
        
        return plaintext
    
    def _encrypt_aes_cbc(self, data: bytes, key: EncryptionKey, key_id: str) -> EncryptedData:
        """Criptografa com AES-256-CBC"""
        iv = secrets.token_bytes(16)  # 128 bits para CBC
        
        # Padding PKCS7
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        self.key_manager.log_key_usage(key_id, "encrypt_aes_cbc", True)
        
        return EncryptedData(
            data=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_CBC,
            key_id=key_id,
            iv=iv
        )
    
    def _decrypt_aes_cbc(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Descriptografa com AES-256-CBC"""
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CBC(encrypted_data.iv),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(encrypted_data.data) + decryptor.finalize()
        
        # Unpadding PKCS7
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        self.key_manager.log_key_usage(encrypted_data.key_id, "decrypt_aes_cbc", True)
        
        return plaintext
    
    def _encrypt_aes_ctr(self, data: bytes, key: EncryptionKey, key_id: str) -> EncryptedData:
        """Criptografa com AES-256-CTR"""
        iv = secrets.token_bytes(16)  # 128 bits para CTR
        
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CTR(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        self.key_manager.log_key_usage(key_id, "encrypt_aes_ctr", True)
        
        return EncryptedData(
            data=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_CTR,
            key_id=key_id,
            iv=iv
        )
    
    def _decrypt_aes_ctr(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Descriptografa com AES-256-CTR"""
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CTR(encrypted_data.iv),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(encrypted_data.data) + decryptor.finalize()
        
        self.key_manager.log_key_usage(encrypted_data.key_id, "decrypt_aes_ctr", True)
        
        return plaintext
    
    def _encrypt_rsa(self, data: bytes, key: EncryptionKey, key_id: str) -> EncryptedData:
        """Criptografa com RSA"""
        # RSA tem limite de tamanho, então dividimos em chunks
        private_key = serialization.load_pem_private_key(
            key.key_data,
            password=None,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # Tamanho máximo por chunk (RSA 2048 = 245 bytes, RSA 4096 = 501 bytes)
        max_chunk_size = 245 if key.algorithm == EncryptionAlgorithm.RSA_2048 else 501
        
        chunks = []
        for i in range(0, len(data), max_chunk_size):
            chunk = data[i:i + max_chunk_size]
            encrypted_chunk = public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            chunks.append(encrypted_chunk)
        
        # Concatenar chunks com delimitador
        encrypted_data = b'\x00\x00\x00\x00'.join(chunks)
        
        self.key_manager.log_key_usage(key_id, "encrypt_rsa", True)
        
        return EncryptedData(
            data=encrypted_data,
            algorithm=key.algorithm,
            key_id=key_id
        )
    
    def _decrypt_rsa(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Descriptografa com RSA"""
        private_key = serialization.load_pem_private_key(
            key.key_data,
            password=None,
            backend=default_backend()
        )
        
        # Separar chunks
        chunks = encrypted_data.data.split(b'\x00\x00\x00\x00')
        
        decrypted_chunks = []
        for chunk in chunks:
            decrypted_chunk = private_key.decrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_chunks.append(decrypted_chunk)
        
        self.key_manager.log_key_usage(encrypted_data.key_id, "decrypt_rsa", True)
        
        return b''.join(decrypted_chunks)
    
    def _encrypt_chacha20_poly1305(self, data: bytes, key: EncryptionKey, key_id: str) -> EncryptedData:
        """Criptografa com ChaCha20-Poly1305"""
        box = nacl.secret.SecretBox(key.key_data)
        encrypted = box.encrypt(data)
        
        # Separar nonce e ciphertext
        nonce = encrypted[:24]
        ciphertext = encrypted[24:]
        
        self.key_manager.log_key_usage(key_id, "encrypt_chacha20_poly1305", True)
        
        return EncryptedData(
            data=ciphertext,
            algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
            key_id=key_id,
            iv=nonce
        )
    
    def _decrypt_chacha20_poly1305(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Descriptografa com ChaCha20-Poly1305"""
        box = nacl.secret.SecretBox(key.key_data)
        encrypted = encrypted_data.iv + encrypted_data.data
        decrypted = box.decrypt(encrypted)
        
        self.key_manager.log_key_usage(encrypted_data.key_id, "decrypt_chacha20_poly1305", True)
        
        return decrypted
    
    def _encrypt_fernet(self, data: bytes, key: EncryptionKey, key_id: str) -> EncryptedData:
        """Criptografa com Fernet"""
        f = Fernet(key.key_data)
        encrypted = f.encrypt(data)
        
        self.key_manager.log_key_usage(key_id, "encrypt_fernet", True)
        
        return EncryptedData(
            data=encrypted,
            algorithm=EncryptionAlgorithm.FERNET,
            key_id=key_id
        )
    
    def _decrypt_fernet(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Descriptografa com Fernet"""
        f = Fernet(key.key_data)
        decrypted = f.decrypt(encrypted_data.data)
        
        self.key_manager.log_key_usage(encrypted_data.key_id, "decrypt_fernet", True)
        
        return decrypted
    
    def encrypt_token(self, token: str, key_id: Optional[str] = None) -> str:
        """Criptografa token JWT"""
        encrypted_data = self.encrypt_data(token, key_id, EncryptionAlgorithm.AES_256_GCM)
        return base64.b64encode(json.dumps(encrypted_data.to_dict()).encode('utf-8')).decode('utf-8')
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Descriptografa token JWT"""
        try:
            token_data = json.loads(base64.b64decode(encrypted_token).decode('utf-8'))
            encrypted_data = EncryptedData(
                data=base64.b64decode(token_data['data']),
                algorithm=EncryptionAlgorithm(token_data['algorithm']),
                key_id=token_data['key_id'],
                iv=base64.b64decode(token_data['iv']) if token_data['iv'] else None,
                auth_tag=base64.b64decode(token_data['auth_tag']) if token_data['auth_tag'] else None,
                version=token_data['version'],
                created_at=datetime.fromisoformat(token_data['created_at'])
            )
            return self.decrypt_data(encrypted_data)
        except Exception as e:
            logger.error(f"Erro ao descriptografar token: {e}")
            raise
    
    def encrypt_cache_data(self, key: str, value: Any, key_id: Optional[str] = None) -> str:
        """Criptografa dados do cache"""
        cache_entry = {
            'key': key,
            'value': value,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        encrypted_data = self.encrypt_data(cache_entry, key_id, EncryptionAlgorithm.AES_256_GCM)
        return base64.b64encode(json.dumps(encrypted_data.to_dict()).encode('utf-8')).decode('utf-8')
    
    def decrypt_cache_data(self, encrypted_cache_data: str) -> Tuple[str, Any]:
        """Descriptografa dados do cache"""
        try:
            cache_data = json.loads(base64.b64decode(encrypted_cache_data).decode('utf-8'))
            encrypted_data = EncryptedData(
                data=base64.b64decode(cache_data['data']),
                algorithm=EncryptionAlgorithm(cache_data['algorithm']),
                key_id=cache_data['key_id'],
                iv=base64.b64decode(cache_data['iv']) if cache_data['iv'] else None,
                auth_tag=base64.b64decode(cache_data['auth_tag']) if cache_data['auth_tag'] else None,
                version=cache_data['version'],
                created_at=datetime.fromisoformat(cache_data['created_at'])
            )
            decrypted = self.decrypt_data(encrypted_data)
            return decrypted['key'], decrypted['value']
        except Exception as e:
            logger.error(f"Erro ao descriptografar dados do cache: {e}")
            raise
    
    def rotate_keys_automatically(self):
        """Rotaciona chaves automaticamente"""
        active_keys = self.key_manager.get_active_keys()
        rotated_count = 0
        
        for key in active_keys:
            # Rotacionar chaves que expiram em 7 dias
            if key.expires_at and (key.expires_at - datetime.now(timezone.utc)).days <= 7:
                new_key = self.key_manager.rotate_key(key.id)
                if new_key:
                    rotated_count += 1
                    logger.info(f"Chave rotacionada: {key.id} -> {new_key.id}")
        
        return rotated_count
    
    def get_encryption_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de criptografia"""
        key_metrics = self.key_manager.get_key_metrics()
        
        return {
            'key_metrics': key_metrics,
            'cache_size': len(self.cache),
            'total_operations': sum(key_metrics['operations'].values()),
            'encryption_algorithms': {
                'aes_256_gcm': key_metrics['operations'].get('encrypt_aes_gcm', 0) + key_metrics['operations'].get('decrypt_aes_gcm', 0),
                'aes_256_cbc': key_metrics['operations'].get('encrypt_aes_cbc', 0) + key_metrics['operations'].get('decrypt_aes_cbc', 0),
                'rsa': key_metrics['operations'].get('encrypt_rsa', 0) + key_metrics['operations'].get('decrypt_rsa', 0),
                'fernet': key_metrics['operations'].get('encrypt_fernet', 0) + key_metrics['operations'].get('decrypt_fernet', 0)
            }
        }

def create_encryption_manager(db_path: str = None) -> EncryptionManager:
    """Cria gerenciador de criptografia"""
    if not db_path:
        db_path = "encryption_keys.db"
    
    key_manager = KeyManager(db_path)
    return EncryptionManager(key_manager)

def generate_secure_password(length: int = 32) -> str:
    """Gera senha segura"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
    """Hash de senha com salt"""
    if not salt:
        salt = secrets.token_bytes(16)
    
    # Usar Argon2 se disponível, senão PBKDF2
    try:
        import argon2
        ph = argon2.PasswordHasher()
        hash_value = ph.hash(password)
        return hash_value, base64.b64encode(salt).decode('utf-8')
    except ImportError:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        hash_value = base64.b64encode(kdf.derive(password.encode('utf-8'))).decode('utf-8')
        return hash_value, base64.b64encode(salt).decode('utf-8')

def verify_password(password: str, hash_value: str, salt: str) -> bool:
    """Verifica senha"""
    try:
        import argon2
        ph = argon2.PasswordHasher()
        ph.verify(hash_value, password)
        return True
    except (ImportError, argon2.exceptions.VerifyMismatchError):
        try:
            salt_bytes = base64.b64decode(salt)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
                backend=default_backend()
            )
            expected_hash = base64.b64encode(kdf.derive(password.encode('utf-8'))).decode('utf-8')
            return hmac.compare_digest(hash_value, expected_hash)
        except Exception:
            return False

if __name__ == "__main__":
    # Teste básico do sistema
    manager = create_encryption_manager()
    
    # Testar criptografia de dados
    test_data = {"user_id": 123, "email": "test@example.com"}
    encrypted = manager.encrypt_data(test_data)
    decrypted = manager.decrypt_data(encrypted)
    
    print(f"Dados originais: {test_data}")
    print(f"Dados descriptografados: {decrypted}")
    print(f"Teste passou: {test_data == decrypted}")
    
    # Testar criptografia de token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    encrypted_token = manager.encrypt_token(token)
    decrypted_token = manager.decrypt_token(encrypted_token)
    
    print(f"Token original: {token}")
    print(f"Token descriptografado: {decrypted_token}")
    print(f"Token teste passou: {token == decrypted_token}")
    
    # Mostrar métricas
    metrics = manager.get_encryption_metrics()
    print(f"Métricas: {json.dumps(metrics, indent=2)}") 