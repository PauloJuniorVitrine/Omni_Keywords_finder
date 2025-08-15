"""
🔐 Sistema de 2FA (Two-Factor Authentication)

Tracing ID: TWO_FACTOR_AUTH_20250127_001
Data/Hora: 2025-01-27 16:25:00 UTC
Versão: 1.0
Status: 🔲 CRIADO MAS NÃO EXECUTADO

Sistema de autenticação de dois fatores usando TOTP (Time-based One-Time Password).
"""

import pyotp
import qrcode
import secrets
import hashlib
import base64
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import redis
import os

logger = logging.getLogger(__name__)


@dataclass
class TwoFactorSetup:
    """Dados de configuração do 2FA."""
    secret_key: str
    qr_code_url: str
    backup_codes: List[str]
    setup_complete: bool = False


@dataclass
class TwoFactorVerification:
    """Resultado da verificação 2FA."""
    is_valid: bool
    is_backup_code: bool
    remaining_attempts: int
    message: str


class TwoFactorAuth:
    """Sistema de autenticação de dois fatores."""
    
    def __init__(self):
        """Inicializa o sistema 2FA."""
        self.issuer_name = os.getenv('2FA_ISSUER_NAME', 'Omni Keywords Finder')
        self.backup_codes_count = int(os.getenv('2FA_BACKUP_CODES_COUNT', 10))
        self.backup_code_length = int(os.getenv('2FA_BACKUP_CODE_LENGTH', 8))
        self.max_attempts = int(os.getenv('2FA_MAX_ATTEMPTS', 5))
        self.lockout_duration = int(os.getenv('2FA_LOCKOUT_DURATION', 900))  # 15 minutos
        
        # Redis para controle de tentativas
        self.redis_client = self._init_redis()
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Inicializa conexão Redis para controle de tentativas."""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis não disponível para 2FA: {e}")
            return None
    
    def generate_secret_key(self, user_id: int, email: str) -> str:
        """
        Gera uma chave secreta única para o usuário.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            
        Returns:
            Chave secreta base32
        """
        # Gerar chave baseada em dados do usuário + random
        base_string = f"{user_id}:{email}:{secrets.token_hex(16)}"
        secret_bytes = hashlib.sha256(base_string.encode()).digest()
        return base64.b32encode(secret_bytes).decode('utf-8')
    
    def setup_2fa(self, user_id: int, email: str, username: str) -> TwoFactorSetup:
        """
        Configura 2FA para um usuário.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            username: Nome de usuário
            
        Returns:
            TwoFactorSetup com dados de configuração
        """
        # Gerar chave secreta
        secret_key = self.generate_secret_key(user_id, email)
        
        # Gerar backup codes
        backup_codes = self._generate_backup_codes()
        
        # Gerar URL do QR code
        qr_code_url = self._generate_qr_code_url(secret_key, email, username)
        
        return TwoFactorSetup(
            secret_key=secret_key,
            qr_code_url=qr_code_url,
            backup_codes=backup_codes
        )
    
    def verify_totp(self, secret_key: str, totp_code: str, user_id: int) -> TwoFactorVerification:
        """
        Verifica um código TOTP.
        
        Args:
            secret_key: Chave secreta do usuário
            totp_code: Código TOTP fornecido
            user_id: ID do usuário
            
        Returns:
            TwoFactorVerification com resultado da verificação
        """
        # Verificar se o usuário não está bloqueado
        if self._is_user_locked(user_id):
            remaining_time = self._get_lockout_remaining_time(user_id)
            return TwoFactorVerification(
                is_valid=False,
                is_backup_code=False,
                remaining_attempts=0,
                message=f"Conta temporariamente bloqueada. Tente novamente em {remaining_time} minutos."
            )
        
        # Verificar se é um backup code
        if self._is_backup_code(totp_code, user_id):
            self._use_backup_code(totp_code, user_id)
            return TwoFactorVerification(
                is_valid=True,
                is_backup_code=True,
                remaining_attempts=self.max_attempts,
                message="Backup code usado com sucesso."
            )
        
        # Verificar código TOTP
        totp = pyotp.TOTP(secret_key)
        
        if totp.verify(totp_code):
            # Código válido, resetar tentativas
            self._reset_attempts(user_id)
            return TwoFactorVerification(
                is_valid=True,
                is_backup_code=False,
                remaining_attempts=self.max_attempts,
                message="Código 2FA válido."
            )
        else:
            # Código inválido, incrementar tentativas
            remaining_attempts = self._increment_attempts(user_id)
            
            if remaining_attempts <= 0:
                # Bloquear usuário
                self._lock_user(user_id)
                return TwoFactorVerification(
                    is_valid=False,
                    is_backup_code=False,
                    remaining_attempts=0,
                    message="Muitas tentativas incorretas. Conta bloqueada por 15 minutos."
                )
            else:
                return TwoFactorVerification(
                    is_valid=False,
                    is_backup_code=False,
                    remaining_attempts=remaining_attempts,
                    message=f"Código 2FA inválido. Tentativas restantes: {remaining_attempts}"
                )
    
    def generate_qr_code(self, qr_code_url: str) -> str:
        """
        Gera QR code como string base64.
        
        Args:
            qr_code_url: URL para gerar o QR code
            
        Returns:
            QR code em base64
        """
        try:
            # Criar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_code_url)
            qr.make(fit=True)
            
            # Criar imagem
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converter para base64
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR code: {e}")
            return ""
    
    def _generate_qr_code_url(self, secret_key: str, email: str, username: str) -> str:
        """
        Gera URL para QR code.
        
        Args:
            secret_key: Chave secreta
            email: Email do usuário
            username: Nome de usuário
            
        Returns:
            URL para QR code
        """
        return pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=email,
            issuer_name=self.issuer_name
        )
    
    def _generate_backup_codes(self) -> List[str]:
        """
        Gera códigos de backup.
        
        Returns:
            Lista de códigos de backup
        """
        codes = []
        for _ in range(self.backup_codes_count):
            # Gerar código alfanumérico
            code = secrets.token_hex(self.backup_code_length // 2).upper()
            codes.append(code)
        return codes
    
    def _store_backup_codes(self, user_id: int, backup_codes: List[str]):
        """Armazena códigos de backup no Redis."""
        if self.redis_client:
            try:
                # Hash dos códigos para segurança
                hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes]
                
                key = f"2fa_backup_codes:{user_id}"
                self.redis_client.setex(
                    key,
                    86400 * 30,  # 30 dias
                    json.dumps(hashed_codes)
                )
            except Exception as e:
                logger.error(f"Erro ao armazenar backup codes: {e}")
    
    def _is_backup_code(self, code: str, user_id: int) -> bool:
        """Verifica se o código é um backup code válido."""
        if not self.redis_client:
            return False
        
        try:
            key = f"2fa_backup_codes:{user_id}"
            stored_codes_json = self.redis_client.get(key)
            
            if not stored_codes_json:
                return False
            
            stored_codes = json.loads(stored_codes_json)
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            
            return code_hash in stored_codes
            
        except Exception as e:
            logger.error(f"Erro ao verificar backup code: {e}")
            return False
    
    def _use_backup_code(self, code: str, user_id: int):
        """Remove um backup code usado."""
        if not self.redis_client:
            return
        
        try:
            key = f"2fa_backup_codes:{user_id}"
            stored_codes_json = self.redis_client.get(key)
            
            if stored_codes_json:
                stored_codes = json.loads(stored_codes_json)
                code_hash = hashlib.sha256(code.encode()).hexdigest()
                
                if code_hash in stored_codes:
                    stored_codes.remove(code_hash)
                    
                    # Atualizar lista
                    self.redis_client.setex(
                        key,
                        86400 * 30,  # 30 dias
                        json.dumps(stored_codes)
                    )
                    
                    logger.info(f"Backup code usado para usuário {user_id}")
                    
        except Exception as e:
            logger.error(f"Erro ao usar backup code: {e}")
    
    def _is_user_locked(self, user_id: int) -> bool:
        """Verifica se o usuário está bloqueado."""
        if not self.redis_client:
            return False
        
        key = f"2fa_lockout:{user_id}"
        return self.redis_client.exists(key) > 0
    
    def _lock_user(self, user_id: int):
        """Bloqueia o usuário temporariamente."""
        if self.redis_client:
            key = f"2fa_lockout:{user_id}"
            self.redis_client.setex(key, self.lockout_duration, str(int(datetime.utcnow().timestamp())))
            logger.warning(f"Usuário {user_id} bloqueado por 2FA")
    
    def _get_lockout_remaining_time(self, user_id: int) -> int:
        """Retorna tempo restante de bloqueio em minutos."""
        if not self.redis_client:
            return 0
        
        key = f"2fa_lockout:{user_id}"
        ttl = self.redis_client.ttl(key)
        return max(0, ttl // 60)
    
    def _increment_attempts(self, user_id: int) -> int:
        """Incrementa contador de tentativas."""
        if not self.redis_client:
            return 0
        
        key = f"2fa_attempts:{user_id}"
        current_attempts = self.redis_client.get(key)
        
        if current_attempts:
            attempts = int(current_attempts) + 1
        else:
            attempts = 1
        
        # Armazenar por 1 hora
        self.redis_client.setex(key, 3600, str(attempts))
        
        return max(0, self.max_attempts - attempts)
    
    def _reset_attempts(self, user_id: int):
        """Reseta contador de tentativas."""
        if self.redis_client:
            key = f"2fa_attempts:{user_id}"
            self.redis_client.delete(key)
    
    def get_remaining_backup_codes(self, user_id: int) -> int:
        """
        Retorna número de backup codes restantes.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Número de backup codes restantes
        """
        if not self.redis_client:
            return 0
        
        try:
            key = f"2fa_backup_codes:{user_id}"
            stored_codes_json = self.redis_client.get(key)
            
            if stored_codes_json:
                stored_codes = json.loads(stored_codes_json)
                return len(stored_codes)
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Erro ao contar backup codes: {e}")
            return 0
    
    def regenerate_backup_codes(self, user_id: int) -> List[str]:
        """
        Regenera códigos de backup.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de novos backup codes
        """
        new_codes = self._generate_backup_codes()
        self._store_backup_codes(user_id, new_codes)
        
        logger.info(f"Backup codes regenerados para usuário {user_id}")
        return new_codes
    
    def disable_2fa(self, user_id: int):
        """
        Desabilita 2FA para um usuário.
        
        Args:
            user_id: ID do usuário
        """
        if self.redis_client:
            # Remover backup codes
            self.redis_client.delete(f"2fa_backup_codes:{user_id}")
            
            # Remover tentativas
            self.redis_client.delete(f"2fa_attempts:{user_id}")
            
            # Remover bloqueio
            self.redis_client.delete(f"2fa_lockout:{user_id}")
            
            logger.info(f"2FA desabilitado para usuário {user_id}")


# Instância global do sistema 2FA
two_factor_auth = TwoFactorAuth()


# Funções de conveniência
def setup_2fa(user_id: int, email: str, username: str) -> TwoFactorSetup:
    """Configura 2FA para um usuário."""
    return two_factor_auth.setup_2fa(user_id, email, username)


def verify_2fa(secret_key: str, totp_code: str, user_id: int) -> TwoFactorVerification:
    """Verifica código 2FA."""
    return two_factor_auth.verify_totp(secret_key, totp_code, user_id)


def generate_qr_code(qr_code_url: str) -> str:
    """Gera QR code como base64."""
    return two_factor_auth.generate_qr_code(qr_code_url)


def get_remaining_backup_codes(user_id: int) -> int:
    """Retorna backup codes restantes."""
    return two_factor_auth.get_remaining_backup_codes(user_id)


def regenerate_backup_codes(user_id: int) -> List[str]:
    """Regenera backup codes."""
    return two_factor_auth.regenerate_backup_codes(user_id)


def disable_2fa(user_id: int):
    """Desabilita 2FA."""
    two_factor_auth.disable_2fa(user_id) 