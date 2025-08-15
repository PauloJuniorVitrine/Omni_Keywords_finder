"""
🔄 Gerenciador de Refresh Tokens

Tracing ID: REFRESH_TOKEN_MANAGER_20250127_001
Data/Hora: 2025-01-27 16:20:00 UTC
Versão: 1.0
Status: 🔲 CRIADO MAS NÃO EXECUTADO

Gerenciador de refresh tokens com rotação, blacklist e segurança aprimorada.
"""

import jwt
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import logging
import redis
import os

logger = logging.getLogger(__name__)


@dataclass
class TokenPair:
    """Par de tokens (access + refresh)."""
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime
    user_id: int
    token_family: str


@dataclass
class TokenInfo:
    """Informações do token."""
    user_id: int
    token_family: str
    created_at: datetime
    expires_at: datetime
    is_revoked: bool = False


class RefreshTokenManager:
    """Gerenciador de refresh tokens com rotação e segurança."""
    
    def __init__(self):
        """Inicializa o gerenciador de refresh tokens."""
        self.refresh_secret = os.getenv('JWT_REFRESH_SECRET_KEY', 'refresh-secret-key-change-in-production')
        self.access_secret = os.getenv('JWT_SECRET_KEY', 'access-secret-key-change-in-production')
        
        # Configurações de tempo
        self.access_token_expires = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora
        self.refresh_token_expires = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800))  # 7 dias
        
        # Configuração Redis para blacklist
        self.redis_client = self._init_redis()
        
        # Configurações de segurança
        self.max_refresh_tokens_per_user = int(os.getenv('MAX_REFRESH_TOKENS_PER_USER', 5))
        self.enable_token_rotation = os.getenv('ENABLE_TOKEN_ROTATION', 'true').lower() == 'true'
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Inicializa conexão Redis para blacklist."""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis não disponível para blacklist: {e}")
            return None
    
    def create_token_pair(self, user_id: int, additional_claims: Dict = None) -> TokenPair:
        """
        Cria um novo par de tokens (access + refresh).
        
        Args:
            user_id: ID do usuário
            additional_claims: Claims adicionais para o token
            
        Returns:
            TokenPair com access e refresh tokens
        """
        # Gerar família de tokens para rotação
        token_family = str(uuid.uuid4())
        
        # Claims base
        access_claims = {
            'user_id': user_id,
            'token_family': token_family,
            'token_type': 'access',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.access_token_expires)
        }
        
        refresh_claims = {
            'user_id': user_id,
            'token_family': token_family,
            'token_type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.refresh_token_expires)
        }
        
        # Adicionar claims extras
        if additional_claims:
            access_claims.update(additional_claims)
            refresh_claims.update(additional_claims)
        
        # Gerar tokens
        access_token = jwt.encode(access_claims, self.access_secret, algorithm='HS256')
        refresh_token = jwt.encode(refresh_claims, self.refresh_secret, algorithm='HS256')
        
        # Armazenar refresh token no Redis
        self._store_refresh_token(refresh_token, user_id, token_family)
        
        # Limpar tokens antigos se necessário
        self._cleanup_old_tokens(user_id)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_claims['exp'],
            refresh_expires_at=refresh_claims['exp'],
            user_id=user_id,
            token_family=token_family
        )
    
    def refresh_access_token(self, refresh_token: str) -> Optional[TokenPair]:
        """
        Renova o access token usando um refresh token válido.
        
        Args:
            refresh_token: Refresh token válido
            
        Returns:
            TokenPair com novos tokens ou None se inválido
        """
        try:
            # Decodificar refresh token
            payload = jwt.decode(refresh_token, self.refresh_secret, algorithms=['HS256'])
            
            # Verificar se é um refresh token
            if payload.get('token_type') != 'refresh':
                logger.warning("Token não é um refresh token")
                return None
            
            # Verificar se não expirou
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                logger.warning("Refresh token expirado")
                return None
            
            # Verificar se não está na blacklist
            if self._is_token_blacklisted(refresh_token):
                logger.warning("Refresh token na blacklist")
                return None
            
            user_id = payload['user_id']
            token_family = payload['token_family']
            
            # Se rotação está habilitada, invalidar refresh token atual
            if self.enable_token_rotation:
                self._blacklist_token(refresh_token, user_id, token_family)
            
            # Criar novo par de tokens
            return self.create_token_pair(user_id, {
                'token_family': token_family,
                'rotated_from': refresh_token[:10] + '...'  # Log parcial do token anterior
            })
            
        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token expirado")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Refresh token inválido: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao renovar access token: {e}")
            return None
    
    def revoke_token(self, token: str, user_id: int = None) -> bool:
        """
        Revoga um token (access ou refresh).
        
        Args:
            token: Token a ser revogado
            user_id: ID do usuário (opcional)
            
        Returns:
            True se revogado com sucesso, False caso contrário
        """
        try:
            # Tentar decodificar como access token primeiro
            try:
                payload = jwt.decode(token, self.access_secret, algorithms=['HS256'])
                token_type = 'access'
            except jwt.InvalidTokenError:
                # Tentar como refresh token
                try:
                    payload = jwt.decode(token, self.refresh_secret, algorithms=['HS256'])
                    token_type = 'refresh'
                except jwt.InvalidTokenError:
                    logger.warning("Token inválido para revogação")
                    return False
            
            # Verificar se o user_id corresponde
            if user_id and payload.get('user_id') != user_id:
                logger.warning("User ID não corresponde ao token")
                return False
            
            # Adicionar à blacklist
            return self._blacklist_token(token, payload.get('user_id'), payload.get('token_family'))
            
        except Exception as e:
            logger.error(f"Erro ao revogar token: {e}")
            return False
    
    def revoke_all_user_tokens(self, user_id: int) -> bool:
        """
        Revoga todos os tokens de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se revogado com sucesso, False caso contrário
        """
        try:
            if self.redis_client:
                # Buscar todos os refresh tokens do usuário
                pattern = f"refresh_token:{user_id}:*"
                keys = self.redis_client.keys(pattern)
                
                for key in keys:
                    self.redis_client.delete(key)
                
                # Adicionar usuário à blacklist geral
                self.redis_client.setex(
                    f"user_blacklist:{user_id}",
                    self.refresh_token_expires,
                    str(int(time.time()))
                )
                
                logger.info(f"Todos os tokens do usuário {user_id} foram revogados")
                return True
            else:
                logger.warning("Redis não disponível para revogação")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao revogar todos os tokens do usuário {user_id}: {e}")
            return False
    
    def validate_access_token(self, access_token: str) -> Optional[Dict]:
        """
        Valida um access token.
        
        Args:
            access_token: Access token a ser validado
            
        Returns:
            Payload do token se válido, None caso contrário
        """
        try:
            # Verificar se está na blacklist
            if self._is_token_blacklisted(access_token):
                logger.warning("Access token na blacklist")
                return None
            
            # Decodificar token
            payload = jwt.decode(access_token, self.access_secret, algorithms=['HS256'])
            
            # Verificar se é um access token
            if payload.get('token_type') != 'access':
                logger.warning("Token não é um access token")
                return None
            
            # Verificar se não expirou
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                logger.warning("Access token expirado")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Access token expirado")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Access token inválido: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao validar access token: {e}")
            return None
    
    def _store_refresh_token(self, refresh_token: str, user_id: int, token_family: str):
        """Armazena refresh token no Redis."""
        if self.redis_client:
            key = f"refresh_token:{user_id}:{token_family}"
            self.redis_client.setex(
                key,
                self.refresh_token_expires,
                refresh_token
            )
    
    def _is_token_blacklisted(self, token: str) -> bool:
        """Verifica se um token está na blacklist."""
        if self.redis_client:
            # Hash do token para usar como chave
            token_hash = str(hash(token))
            return self.redis_client.exists(f"blacklist:{token_hash}") > 0
        return False
    
    def _blacklist_token(self, token: str, user_id: int, token_family: str) -> bool:
        """Adiciona um token à blacklist."""
        if self.redis_client:
            try:
                # Hash do token para usar como chave
                token_hash = str(hash(token))
                
                # Adicionar à blacklist com TTL baseado no tempo de expiração
                self.redis_client.setex(
                    f"blacklist:{token_hash}",
                    self.refresh_token_expires,
                    f"{user_id}:{token_family}:{int(time.time())}"
                )
                
                # Remover da lista de refresh tokens ativos
                self.redis_client.delete(f"refresh_token:{user_id}:{token_family}")
                
                return True
            except Exception as e:
                logger.error(f"Erro ao adicionar token à blacklist: {e}")
                return False
        return False
    
    def _cleanup_old_tokens(self, user_id: int):
        """Remove tokens antigos do usuário se exceder o limite."""
        if self.redis_client:
            try:
                # Buscar todos os refresh tokens do usuário
                pattern = f"refresh_token:{user_id}:*"
                keys = self.redis_client.keys(pattern)
                
                # Se exceder o limite, remover os mais antigos
                if len(keys) > self.max_refresh_tokens_per_user:
                    # Ordenar por timestamp (assumindo que está no valor)
                    keys_with_timestamp = []
                    for key in keys:
                        token = self.redis_client.get(key)
                        if token:
                            # Extrair timestamp do token (simplificado)
                            keys_with_timestamp.append((key, time.time()))
                    
                    # Ordenar e remover os mais antigos
                    keys_with_timestamp.sort(key=lambda x: x[1])
                    keys_to_remove = keys_with_timestamp[:-self.max_refresh_tokens_per_user]
                    
                    for key, _ in keys_to_remove:
                        self.redis_client.delete(key)
                        logger.info(f"Token antigo removido: {key}")
                        
            except Exception as e:
                logger.error(f"Erro ao limpar tokens antigos: {e}")
    
    def get_user_active_tokens(self, user_id: int) -> List[Dict]:
        """
        Retorna lista de tokens ativos do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de informações dos tokens ativos
        """
        if not self.redis_client:
            return []
        
        try:
            pattern = f"refresh_token:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            
            tokens = []
            for key in keys:
                token = self.redis_client.get(key)
                if token:
                    # Extrair informações do token
                    try:
                        payload = jwt.decode(token, self.refresh_secret, algorithms=['HS256'])
                        tokens.append({
                            'token_family': payload.get('token_family'),
                            'created_at': datetime.fromtimestamp(payload.get('iat', 0)),
                            'expires_at': datetime.fromtimestamp(payload.get('exp', 0)),
                            'is_active': True
                        })
                    except jwt.InvalidTokenError:
                        # Token inválido, remover
                        self.redis_client.delete(key)
            
            return tokens
            
        except Exception as e:
            logger.error(f"Erro ao buscar tokens ativos do usuário {user_id}: {e}")
            return []
    
    def get_blacklist_stats(self) -> Dict:
        """
        Retorna estatísticas da blacklist.
        
        Returns:
            Dicionário com estatísticas
        """
        if not self.redis_client:
            return {'error': 'Redis não disponível'}
        
        try:
            blacklist_keys = self.redis_client.keys("blacklist:*")
            user_blacklist_keys = self.redis_client.keys("user_blacklist:*")
            
            return {
                'total_blacklisted_tokens': len(blacklist_keys),
                'total_blacklisted_users': len(user_blacklist_keys),
                'redis_available': True
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas da blacklist: {e}")
            return {'error': str(e)}


# Instância global do gerenciador
refresh_token_manager = RefreshTokenManager()


# Funções de conveniência
def create_token_pair(user_id: int, additional_claims: Dict = None) -> TokenPair:
    """Cria um novo par de tokens."""
    return refresh_token_manager.create_token_pair(user_id, additional_claims)


def refresh_access_token(refresh_token: str) -> Optional[TokenPair]:
    """Renova o access token usando refresh token."""
    return refresh_token_manager.refresh_access_token(refresh_token)


def revoke_token(token: str, user_id: int = None) -> bool:
    """Revoga um token."""
    return refresh_token_manager.revoke_token(token, user_id)


def revoke_all_user_tokens(user_id: int) -> bool:
    """Revoga todos os tokens de um usuário."""
    return refresh_token_manager.revoke_all_user_tokens(user_id)


def validate_access_token(access_token: str) -> Optional[Dict]:
    """Valida um access token."""
    return refresh_token_manager.validate_access_token(access_token) 