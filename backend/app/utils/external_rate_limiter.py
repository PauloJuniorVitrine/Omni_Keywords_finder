"""
Rate Limiter Específico para Consumo Externo - Omni Keywords Finder
Rate limiting diferenciado por IP, API key e tipo de requisição
Prompt: Rate limiting para consumo externo
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import time
import hashlib
import logging
import json
from typing import Dict, Optional, Tuple, List, Any
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import redis
import os

from app.utils.security_logger import SecurityLogger

# Configuração de logging
logger = logging.getLogger(__name__)
security_logger = SecurityLogger()

class ExternalRateLimiter:
    """
    Rate Limiter especializado para APIs de consumo externo
    Implementa diferenciação por IP, API key e tipo de requisição
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Inicializa o rate limiter
        
        Args:
            redis_url: URL do Redis (opcional)
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = self._init_redis()
        
        # Configurações padrão
        self.default_limits = {
            'get': {'requests': 60, 'window': 60},      # 60 req/min para GET
            'post': {'requests': 30, 'window': 60},     # 30 req/min para POST
            'put': {'requests': 20, 'window': 60},      # 20 req/min para PUT
            'delete': {'requests': 10, 'window': 60},   # 10 req/min para DELETE
            'patch': {'requests': 20, 'window': 60}     # 20 req/min para PATCH
        }
        
        # Limites por tipo de cliente
        self.client_limits = {
            'free': {'multiplier': 0.5},      # 50% dos limites padrão
            'basic': {'multiplier': 1.0},     # 100% dos limites padrão
            'premium': {'multiplier': 2.0},   # 200% dos limites padrão
            'enterprise': {'multiplier': 5.0} # 500% dos limites padrão
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Inicializa conexão com Redis"""
        try:
            # Parse da URL do Redis
            if self.redis_url.startswith('redis://'):
                # redis://username:password@host:port/db
                parts = self.redis_url.replace('redis://', '').split('@')
                if len(parts) == 2:
                    auth, host_port_db = parts
                    username, password = auth.split(':')
                    host_port, db = host_port_db.split('/')
                    host, port = host_port.split(':')
                else:
                    host_port_db = parts[0]
                    host_port, db = host_port_db.split('/')
                    host, port = host_port.split(':')
                    username = password = None
                
                redis_client = redis.Redis(
                    host=host,
                    port=int(port),
                    db=int(db),
                    username=username,
                    password=password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            else:
                # Fallback para configuração manual
                redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=int(os.getenv('REDIS_DB', 0)),
                    password=os.getenv('REDIS_PASSWORD'),
                    decode_responses=True
                )
            
            # Teste de conexão
            redis_client.ping()
            logger.info("Redis conectado para rate limiting externo")
            return redis_client
            
        except Exception as e:
            logger.error(f"Erro ao conectar Redis para rate limiting: {e}")
            return None
    
    def get_client_identifier(self, request_obj) -> str:
        """
        Obtém identificador único do cliente
        
        Args:
            request_obj: Objeto request do Flask
            
        Returns:
            Identificador único do cliente
        """
        # Priorizar X-Forwarded-For para proxies
        client_ip = request_obj.headers.get('X-Forwarded-For', request_obj.remote_addr)
        
        # Extrair API key se disponível
        api_key = request_obj.headers.get('X-API-Key') or request_obj.headers.get('Authorization', '')
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]  # Remove 'Bearer '
        
        # User-Agent para maior precisão
        user_agent = request_obj.headers.get('User-Agent', '')
        
        # Criar hash único
        identifier_parts = [client_ip, api_key, user_agent]
        identifier = ":".join(filter(None, identifier_parts))
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def get_client_type(self, request_obj) -> str:
        """
        Determina o tipo de cliente baseado em headers ou API key
        
        Args:
            request_obj: Objeto request do Flask
            
        Returns:
            Tipo de cliente (free, basic, premium, enterprise)
        """
        # Verificar header específico
        client_type = request_obj.headers.get('X-Client-Type', '').lower()
        if client_type in self.client_limits:
            return client_type
        
        # Verificar API key (simulado - em produção seria verificado no banco)
        api_key = request_obj.headers.get('X-API-Key') or request_obj.headers.get('Authorization', '')
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        
        # Simulação de verificação de API key
        if api_key.startswith('sk_enterprise_'):
            return 'enterprise'
        elif api_key.startswith('sk_premium_'):
            return 'premium'
        elif api_key.startswith('sk_basic_'):
            return 'basic'
        else:
            return 'free'
    
    def get_rate_limit_config(self, method: str, client_type: str) -> Dict[str, int]:
        """
        Obtém configuração de rate limit baseada no método e tipo de cliente
        
        Args:
            method: Método HTTP
            client_type: Tipo de cliente
            
        Returns:
            Configuração de rate limit
        """
        method = method.lower()
        base_config = self.default_limits.get(method, self.default_limits['get'])
        multiplier = self.client_limits.get(client_type, {'multiplier': 1.0})['multiplier']
        
        return {
            'requests': int(base_config['requests'] * multiplier),
            'window': base_config['window']
        }
    
    def check_rate_limit(self, key: str, method: str, client_type: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifica se o cliente excedeu o rate limit
        
        Args:
            key: Chave única para o rate limit
            method: Método HTTP
            client_type: Tipo de cliente
            
        Returns:
            (permitido, informações do rate limit)
        """
        if not self.redis_client:
            # Fallback: permitir se Redis não estiver disponível
            config = self.get_rate_limit_config(method, client_type)
            return True, {
                'remaining': config['requests'],
                'reset_time': int(time.time()) + config['window'],
                'limit': config['requests'],
                'window': config['window'],
                'client_type': client_type
            }
        
        config = self.get_rate_limit_config(method, client_type)
        current_time = int(time.time())
        window_start = current_time - (current_time % config['window'])
        
        # Chave Redis para esta janela
        redis_key = f"external_rate_limit:{key}:{method}:{window_start}"
        
        try:
            # Incrementar contador
            current_count = self.redis_client.incr(redis_key)
            
            # Definir expiração
            if current_count == 1:
                self.redis_client.expire(redis_key, config['window'])
            
            # Verificar se excedeu o limite
            if current_count > config['requests']:
                retry_after = window_start + config['window'] - current_time
                
                # Log de rate limit excedido
                self._log_rate_limit_exceeded(key, method, client_type, config, current_count)
                
                return False, {
                    'remaining': 0,
                    'reset_time': window_start + config['window'],
                    'retry_after': retry_after,
                    'limit': config['requests'],
                    'window': config['window'],
                    'client_type': client_type,
                    'current_count': current_count
                }
            
            return True, {
                'remaining': config['requests'] - current_count,
                'reset_time': window_start + config['window'],
                'limit': config['requests'],
                'window': config['window'],
                'client_type': client_type,
                'current_count': current_count
            }
            
        except Exception as e:
            logger.error(f"Erro no rate limiting externo: {e}")
            # Fallback: permitir em caso de erro
            return True, {
                'remaining': config['requests'],
                'reset_time': current_time + config['window'],
                'limit': config['requests'],
                'window': config['window'],
                'client_type': client_type
            }
    
    def _log_rate_limit_exceeded(self, key: str, method: str, client_type: str, 
                                config: Dict, current_count: int):
        """
        Registra log de rate limit excedido
        
        Args:
            key: Chave do rate limit
            method: Método HTTP
            client_type: Tipo de cliente
            config: Configuração do rate limit
            current_count: Contador atual
        """
        log_data = {
            "component": "external_rate_limiter",
            "event_type": "rate_limit_exceeded",
            "key": key,
            "method": method,
            "client_type": client_type,
            "limit": config['requests'],
            "current_count": current_count,
            "window": config['window'],
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        security_logger.log_security_event(
            event_type="rate_limit_exceeded",
            severity="warning",
            details=log_data
        )
        
        logger.warning(f"Rate limit excedido: {key}, método: {method}, tipo: {client_type}, "
                      f"limite: {config['requests']}, atual: {current_count}")
    
    def get_rate_limit_stats(self, key: str, method: str = None) -> Dict[str, Any]:
        """
        Obtém estatísticas de rate limit para um cliente
        
        Args:
            key: Chave do cliente
            method: Método HTTP (opcional)
            
        Returns:
            Estatísticas de rate limit
        """
        if not self.redis_client:
            return {"error": "Redis não disponível"}
        
        try:
            current_time = int(time.time())
            stats = {}
            
            if method:
                methods = [method]
            else:
                methods = ['get', 'post', 'put', 'delete', 'patch']
            
            for method in methods:
                # Buscar chaves Redis para este cliente e método
                pattern = f"external_rate_limit:{key}:{method}:*"
                keys = self.redis_client.keys(pattern)
                
                method_stats = {
                    'current_count': 0,
                    'windows': []
                }
                
                for redis_key in keys:
                    count = self.redis_client.get(redis_key)
                    if count:
                        count = int(count)
                        method_stats['current_count'] += count
                        
                        # Extrair timestamp da janela da chave
                        window_start = int(redis_key.split(':')[-1])
                        method_stats['windows'].append({
                            'window_start': window_start,
                            'count': count
                        })
                
                stats[method] = method_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de rate limit: {e}")
            return {"error": str(e)}

def external_rate_limit(method: str = None, client_type: str = None):
    """
    Decorator para aplicar rate limiting em APIs externas
    
    Args:
        method: Método HTTP específico (opcional)
        client_type: Tipo de cliente específico (opcional)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = ExternalRateLimiter()
            
            # Determinar método HTTP
            request_method = method or request.method.lower()
            
            # Obter identificador do cliente
            client_id = limiter.get_client_identifier(request)
            
            # Determinar tipo de cliente
            client_type_detected = client_type or limiter.get_client_type(request)
            
            # Verificar rate limit
            allowed, rate_info = limiter.check_rate_limit(client_id, request_method, client_type_detected)
            
            if not allowed:
                # Criar resposta de rate limit excedido
                response_data = {
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Try again later.',
                    'retry_after': rate_info.get('retry_after', rate_info['window']),
                    'limit': rate_info['limit'],
                    'window': rate_info['window'],
                    'client_type': rate_info['client_type']
                }
                
                response = jsonify(response_data), 429
                
                # Adicionar headers de rate limit
                if isinstance(response, tuple):
                    response_obj, status_code = response
                else:
                    response_obj, status_code = response, 429
                
                if hasattr(response_obj, 'headers'):
                    response_obj.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                    response_obj.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                    response_obj.headers['X-RateLimit-Reset'] = str(rate_info['reset_time'])
                    response_obj.headers['Retry-After'] = str(rate_info.get('retry_after', rate_info['window']))
                    response_obj.headers['X-RateLimit-ClientType'] = rate_info['client_type']
                
                return response_obj, status_code
            
            # Executar função original
            response = f(*args, **kwargs)
            
            # Adicionar headers de rate limit
            if isinstance(response, tuple):
                response_obj, status_code = response
            else:
                response_obj, status_code = response, 200
            
            if hasattr(response_obj, 'headers'):
                response_obj.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                response_obj.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response_obj.headers['X-RateLimit-Reset'] = str(rate_info['reset_time'])
                response_obj.headers['X-RateLimit-ClientType'] = rate_info['client_type']
            
            return response_obj, status_code
        
        return decorated_function
    return decorator

# Decorators específicos para diferentes tipos de requisição
def external_get_rate_limit(f):
    """Rate limiting específico para requisições GET externas"""
    return external_rate_limit(method='get')(f)

def external_post_rate_limit(f):
    """Rate limiting específico para requisições POST externas"""
    return external_rate_limit(method='post')(f)

def external_put_rate_limit(f):
    """Rate limiting específico para requisições PUT externas"""
    return external_rate_limit(method='put')(f)

def external_delete_rate_limit(f):
    """Rate limiting específico para requisições DELETE externas"""
    return external_rate_limit(method='delete')(f)

def external_premium_rate_limit(f):
    """Rate limiting para clientes premium"""
    return external_rate_limit(client_type='premium')(f)

def external_enterprise_rate_limit(f):
    """Rate limiting para clientes enterprise"""
    return external_rate_limit(client_type='enterprise')(f) 