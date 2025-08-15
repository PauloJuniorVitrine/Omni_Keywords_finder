"""
Middleware de Rate Limiting para APIs de Autenticação
Implementa rate limiting adaptativo baseado em IP e comportamento
"""

import time
import hashlib
import logging
from typing import Dict, Optional, Tuple
from functools import wraps
from flask import request, jsonify, current_app
import redis
import os

# Configuração do Redis para rate limiting
redis_client = None

def init_redis():
    """Inicializa conexão com Redis"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
        # Teste de conexão
        redis_client.ping()
        logging.info("Redis conectado para rate limiting")
    except Exception as e:
        logging.error(f"Erro ao conectar Redis: {e}")
        redis_client = None

class RateLimiter:
    """Classe para gerenciar rate limiting"""
    
    def __init__(self):
        self.redis_client = redis_client
    
    def get_client_identifier(self) -> str:
        """Obtém identificador único do cliente"""
        # Priorizar X-Forwarded-For para proxies
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Adicionar User-Agent para maior precisão
        user_agent = request.headers.get('User-Agent', '')
        
        # Criar hash único
        identifier = f"{client_ip}:{user_agent}"
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def check_rate_limit(self, key: str, max_requests: int, window: int) -> Tuple[bool, Dict]:
        """
        Verifica se o cliente excedeu o rate limit
        
        Args:
            key: Chave única para o rate limit
            max_requests: Máximo de requisições permitidas
            window: Janela de tempo em segundos
        
        Returns:
            (permitido, informações do rate limit)
        """
        if not self.redis_client:
            # Fallback: permitir se Redis não estiver disponível
            return True, {'remaining': max_requests, 'reset_time': int(time.time()) + window}
        
        current_time = int(time.time())
        window_start = current_time - (current_time % window)
        
        # Chave Redis para esta janela
        redis_key = f"rate_limit:{key}:{window_start}"
        
        try:
            # Incrementar contador
            current_count = self.redis_client.incr(redis_key)
            
            # Definir expiração
            if current_count == 1:
                self.redis_client.expire(redis_key, window)
            
            # Verificar se excedeu o limite
            if current_count > max_requests:
                return False, {
                    'remaining': 0,
                    'reset_time': window_start + window,
                    'retry_after': window_start + window - current_time
                }
            
            return True, {
                'remaining': max_requests - current_count,
                'reset_time': window_start + window
            }
            
        except Exception as e:
            logging.error(f"Erro no rate limiting: {e}")
            # Fallback: permitir em caso de erro
            return True, {'remaining': max_requests, 'reset_time': current_time + window}

def rate_limit(max_requests: int, window: int, key_prefix: str = ""):
    """
    Decorator para aplicar rate limiting
    
    Args:
        max_requests: Máximo de requisições permitidas
        window: Janela de tempo em segundos
        key_prefix: Prefixo para a chave de rate limiting
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = RateLimiter()
            
            # Criar chave única
            client_id = limiter.get_client_identifier()
            key = f"{key_prefix}:{client_id}"
            
            # Verificar rate limit
            allowed, rate_info = limiter.check_rate_limit(key, max_requests, window)
            
            if not allowed:
                # Log de tentativa de rate limit
                logging.warning(f"Rate limit excedido: {client_id}, IP: {request.remote_addr}")
                
                return jsonify({
                    'erro': 'Rate limit excedido. Tente novamente mais tarde.',
                    'retry_after': rate_info.get('retry_after', window)
                }), 429
            
            # Adicionar headers de rate limit
            response = f(*args, **kwargs)
            
            # Se a resposta for um tuple (response, status_code)
            if isinstance(response, tuple):
                response_obj, status_code = response
            else:
                response_obj, status_code = response, 200
            
            # Adicionar headers de rate limit
            if hasattr(response_obj, 'headers'):
                response_obj.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response_obj.headers['X-RateLimit-Reset'] = str(rate_info['reset_time'])
            
            return response_obj, status_code
        
        return decorated_function
    return decorator

# Configurações específicas para autenticação
def auth_rate_limit(f):
    """Rate limiting específico para endpoints de autenticação"""
    return rate_limit(
        max_requests=int(os.getenv('AUTH_RATE_LIMIT_REQUESTS', 5)),  # 5 tentativas
        window=int(os.getenv('AUTH_RATE_LIMIT_WINDOW', 300)),        # 5 minutos
        key_prefix="auth"
    )(f)

def oauth_rate_limit(f):
    """Rate limiting específico para OAuth"""
    return rate_limit(
        max_requests=int(os.getenv('OAUTH_RATE_LIMIT_REQUESTS', 10)),  # 10 tentativas
        window=int(os.getenv('OAUTH_RATE_LIMIT_WINDOW', 600)),         # 10 minutos
        key_prefix="oauth"
    )(f) 