#!/usr/bin/env python3
"""
Middleware de Rate Limiting Avançado
Baseado em código real do sistema Omni Keywords Finder

Tracing ID: RATE_LIMITING_20250127_001
Data: 2025-01-27
Versão: 1.0
"""

import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from functools import wraps
import redis
from flask import request, jsonify, g, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import structlog

logger = structlog.get_logger(__name__)

class AdvancedRateLimiter:
    """
    Rate Limiter Avançado baseado em código real do sistema
    Protege contra abuso e ataques DDoS
    """
    
    def __init__(self, redis_url: str = None):
        """Inicializa o rate limiter com configurações baseadas em uso real"""
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        
        # Configurações baseadas em análise real do sistema
        self.limits = {
            # APIs de keywords - baseado em uso real
            "/api/keywords": {
                "limit": 50,
                "window": 60,  # 50 requests por minuto
                "burst": 10
            },
            "/api/keywords/analyze": {
                "limit": 20,
                "window": 60,  # 20 requests por minuto
                "burst": 5
            },
            "/api/keywords/export": {
                "limit": 10,
                "window": 60,  # 10 requests por minuto
                "burst": 3
            },
            "/api/keywords/search": {
                "limit": 30,
                "window": 60,  # 30 requests por minuto
                "burst": 8
            },
            
            # APIs de autenticação
            "/api/auth/login": {
                "limit": 5,
                "window": 60,  # 5 tentativas por minuto
                "burst": 2
            },
            "/api/auth/register": {
                "limit": 3,
                "window": 300,  # 3 registros por 5 minutos
                "burst": 1
            },
            "/api/auth/refresh": {
                "limit": 10,
                "window": 60,  # 10 refresh por minuto
                "burst": 3
            },
            
            # APIs de relatórios
            "/api/reports": {
                "limit": 30,
                "window": 60,  # 30 relatórios por minuto
                "burst": 5
            },
            "/api/reports/export": {
                "limit": 15,
                "window": 60,  # 15 exports por minuto
                "burst": 3
            },
            
            # APIs de ML/AI
            "/api/ml/predict": {
                "limit": 15,
                "window": 60,  # 15 predições por minuto
                "burst": 3
            },
            "/api/ml/train": {
                "limit": 5,
                "window": 300,  # 5 treinos por 5 minutos
                "burst": 1
            },
            
            # APIs de análise
            "/api/analysis": {
                "limit": 25,
                "window": 60,  # 25 análises por minuto
                "burst": 6
            },
            "/api/analysis/batch": {
                "limit": 10,
                "window": 300,  # 10 análises em lote por 5 minutos
                "burst": 2
            },
            
            # Default para endpoints não configurados
            "default": {
                "limit": 100,
                "window": 60,  # 100 requests por minuto
                "burst": 20
            }
        }
        
        # Configurações de segurança
        self.security_config = {
            "block_suspicious_ips": True,
            "block_user_agents": [
                "sqlmap", "nikto", "nmap", "w3af", "burp", "zap"
            ],
            "max_concurrent_requests": 10,
            "suspicious_patterns": [
                "UNION SELECT", "DROP TABLE", "<script>", "javascript:",
                "data:text/html", "eval(", "exec(", "system("
            ]
        }
        
        # Cache de IPs bloqueados
        self.blocked_ips = set()
        self.suspicious_ips = {}
        
        logger.info("Rate limiter inicializado", 
                   limits_count=len(self.limits),
                   redis_url=self.redis_url)
    
    def get_client_identifier(self) -> str:
        """Gera identificador único do cliente baseado em múltiplos fatores"""
        # Baseado em código real do sistema
        client_ip = get_remote_address()
        user_agent = request.headers.get('User-Agent', '')
        user_id = getattr(g, 'user_id', None)
        
        # Hash do identificador
        identifier_parts = [
            client_ip,
            user_agent[:50],  # Primeiros 50 chars do User-Agent
            str(user_id) if user_id else 'anonymous'
        ]
        
        identifier = hashlib.sha256(
            '|'.join(identifier_parts).encode()
        ).hexdigest()
        
        return f"rate_limit:{identifier}"
    
    def get_endpoint_config(self, endpoint: str) -> Dict[str, Any]:
        """Retorna configuração de rate limit para endpoint específico"""
        # Busca configuração específica
        for path, config in self.limits.items():
            if endpoint.startswith(path):
                return config
        
        # Retorna configuração padrão
        return self.limits["default"]
    
    def check_security(self, client_ip: str, user_agent: str, payload: str = "") -> Tuple[bool, str]:
        """Verifica segurança da requisição baseada em padrões reais"""
        # Verificar User-Agent suspeito
        for suspicious_ua in self.security_config["block_user_agents"]:
            if suspicious_ua.lower() in user_agent.lower():
                logger.warning("User-Agent suspeito detectado",
                             ip=client_ip,
                             user_agent=user_agent,
                             suspicious=suspicious_ua)
                return False, f"User-Agent suspeito: {suspicious_ua}"
        
        # Verificar padrões suspeitos no payload
        for pattern in self.security_config["suspicious_patterns"]:
            if pattern.lower() in payload.lower():
                logger.warning("Padrão suspeito detectado",
                             ip=client_ip,
                             pattern=pattern)
                return False, f"Padrão suspeito detectado: {pattern}"
        
        # Verificar se IP está bloqueado
        if client_ip in self.blocked_ips:
            logger.warning("IP bloqueado tentou acessar",
                         ip=client_ip)
            return False, "IP bloqueado"
        
        return True, "OK"
    
    def is_rate_limited(self, identifier: str, endpoint: str) -> Tuple[bool, Dict[str, Any]]:
        """Verifica se cliente atingiu limite de rate"""
        config = self.get_endpoint_config(endpoint)
        current_time = int(time.time())
        window_start = current_time - config["window"]
        
        # Chave Redis para tracking
        redis_key = f"{identifier}:{endpoint}"
        
        try:
            # Obter requisições na janela atual
            pipeline = self.redis_client.pipeline()
            pipeline.zremrangebyscore(redis_key, 0, window_start)
            pipeline.zadd(redis_key, {str(current_time): current_time})
            pipeline.zcard(redis_key)
            pipeline.expire(redis_key, config["window"])
            results = pipeline.execute()
            
            current_requests = results[2]
            
            # Verificar se excedeu limite
            if current_requests > config["limit"]:
                # Verificar burst allowance
                if current_requests <= config["limit"] + config["burst"]:
                    logger.info("Burst allowance usado",
                               identifier=identifier,
                               endpoint=endpoint,
                               requests=current_requests,
                               limit=config["limit"])
                    return False, {
                        "limited": False,
                        "current": current_requests,
                        "limit": config["limit"],
                        "burst_used": True
                    }
                else:
                    logger.warning("Rate limit excedido",
                                 identifier=identifier,
                                 endpoint=endpoint,
                                 requests=current_requests,
                                 limit=config["limit"])
                    return True, {
                        "limited": True,
                        "current": current_requests,
                        "limit": config["limit"],
                        "retry_after": config["window"]
                    }
            
            return False, {
                "limited": False,
                "current": current_requests,
                "limit": config["limit"]
            }
            
        except redis.RedisError as e:
            logger.error("Erro Redis no rate limiting",
                        error=str(e),
                        identifier=identifier,
                        endpoint=endpoint)
            # Em caso de erro Redis, permitir requisição
            return False, {"limited": False, "error": "redis_error"}
    
    def track_suspicious_activity(self, client_ip: str, reason: str) -> None:
        """Rastreia atividade suspeita para análise"""
        current_time = int(time.time())
        
        if client_ip not in self.suspicious_ips:
            self.suspicious_ips[client_ip] = []
        
        self.suspicious_ips[client_ip].append({
            "timestamp": current_time,
            "reason": reason,
            "endpoint": request.endpoint,
            "user_agent": request.headers.get('User-Agent', ''),
            "payload": request.get_data(as_text=True)[:200]  # Primeiros 200 chars
        })
        
        # Manter apenas últimas 10 atividades
        self.suspicious_ips[client_ip] = self.suspicious_ips[client_ip][-10:]
        
        # Se muitas atividades suspeitas, considerar bloquear IP
        if len(self.suspicious_ips[client_ip]) >= 5:
            self.blocked_ips.add(client_ip)
            logger.warning("IP bloqueado por múltiplas atividades suspeitas",
                         ip=client_ip,
                         activities_count=len(self.suspicious_ips[client_ip]))
    
    def get_rate_limit_headers(self, rate_info: Dict[str, Any]) -> Dict[str, str]:
        """Gera headers de rate limit para resposta"""
        headers = {
            "X-RateLimit-Limit": str(rate_info.get("limit", 0)),
            "X-RateLimit-Remaining": str(max(0, rate_info.get("limit", 0) - rate_info.get("current", 0))),
            "X-RateLimit-Reset": str(int(time.time()) + rate_info.get("retry_after", 60))
        }
        
        if rate_info.get("burst_used"):
            headers["X-RateLimit-Burst-Used"] = "true"
        
        return headers

def rate_limit_middleware():
    """Middleware Flask para rate limiting"""
    rate_limiter = AdvancedRateLimiter()
    
    def middleware():
        # Obter informações da requisição
        client_ip = get_remote_address()
        user_agent = request.headers.get('User-Agent', '')
        endpoint = request.endpoint or request.path
        payload = request.get_data(as_text=True)
        
        # Verificar segurança
        is_safe, security_message = rate_limiter.check_security(
            client_ip, user_agent, payload
        )
        
        if not is_safe:
            rate_limiter.track_suspicious_activity(client_ip, security_message)
            return jsonify({
                "error": "Security violation",
                "message": security_message,
                "tracing_id": f"SECURITY_{int(time.time())}"
            }), 403
        
        # Verificar rate limit
        identifier = rate_limiter.get_client_identifier()
        is_limited, rate_info = rate_limiter.is_rate_limited(identifier, endpoint)
        
        if is_limited:
            # Adicionar headers de rate limit
            headers = rate_limiter.get_rate_limit_headers(rate_info)
            
            return jsonify({
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {rate_info['limit']} per minute",
                "retry_after": rate_info["retry_after"],
                "tracing_id": f"RATE_LIMIT_{int(time.time())}"
            }), 429, headers
        
        # Requisição permitida
        g.rate_limit_info = rate_info
        
        # Log da requisição
        logger.info("Requisição processada",
                   ip=client_ip,
                   endpoint=endpoint,
                   method=request.method,
                   rate_info=rate_info)
        
        return None  # Continuar processamento
    
    return middleware

def rate_limit_decorator(endpoint: str = None):
    """Decorator para aplicar rate limiting em rotas específicas"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rate_limiter = AdvancedRateLimiter()
            
            # Obter informações da requisição
            client_ip = get_remote_address()
            user_agent = request.headers.get('User-Agent', '')
            current_endpoint = endpoint or request.endpoint
            payload = request.get_data(as_text=True)
            
            # Verificar segurança
            is_safe, security_message = rate_limiter.check_security(
                client_ip, user_agent, payload
            )
            
            if not is_safe:
                rate_limiter.track_suspicious_activity(client_ip, security_message)
                return jsonify({
                    "error": "Security violation",
                    "message": security_message,
                    "tracing_id": f"SECURITY_{int(time.time())}"
                }), 403
            
            # Verificar rate limit
            identifier = rate_limiter.get_client_identifier()
            is_limited, rate_info = rate_limiter.is_rate_limited(identifier, current_endpoint)
            
            if is_limited:
                headers = rate_limiter.get_rate_limit_headers(rate_info)
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {rate_info['limit']} per minute",
                    "retry_after": rate_info["retry_after"],
                    "tracing_id": f"RATE_LIMIT_{int(time.time())}"
                }), 429, headers
            
            # Armazenar informações de rate limit no contexto
            g.rate_limit_info = rate_info
            
            # Executar função original
            response = f(*args, **kwargs)
            
            # Adicionar headers de rate limit à resposta
            if hasattr(response, 'headers'):
                headers = rate_limiter.get_rate_limit_headers(rate_info)
                for key, value in headers.items():
                    response.headers[key] = value
            
            return response
        
        return decorated_function
    return decorator

# Configuração do Flask-Limiter para compatibilidade
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute", "1000 per hour"],
    storage_uri="redis://localhost:6379/0",
    strategy="fixed-window"
)

# Função para configurar rate limiting no app Flask
def configure_rate_limiting(app):
    """Configura rate limiting no app Flask"""
    # Registrar middleware
    app.before_request(rate_limit_middleware())
    
    # Configurar Flask-Limiter
    limiter.init_app(app)
    
    # Configurar logging
    logger.info("Rate limiting configurado",
               app_name=app.name,
               limits_count=len(AdvancedRateLimiter().limits))
    
    return limiter

# Testes baseados em código real (NÃO executados automaticamente)
def create_rate_limit_tests():
    """Cria testes de rate limiting baseados em código real"""
    test_code = '''
import pytest
from unittest.mock import Mock, patch
from backend.app.middleware.rate_limiting import AdvancedRateLimiter

class TestAdvancedRateLimiter:
    """Testes de rate limiting baseados em código real"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.rate_limiter = AdvancedRateLimiter()
        self.test_identifier = "test_client_123"
        self.test_endpoint = "/api/keywords"
    
    def test_get_endpoint_config(self):
        """Testa obtenção de configuração de endpoint"""
        config = self.rate_limiter.get_endpoint_config("/api/keywords")
        assert config["limit"] == 50
        assert config["window"] == 60
        
        config = self.rate_limiter.get_endpoint_config("/api/auth/login")
        assert config["limit"] == 5
        assert config["window"] == 60
    
    def test_check_security_suspicious_user_agent(self):
        """Testa detecção de User-Agent suspeito"""
        is_safe, message = self.rate_limiter.check_security(
            "192.168.1.1",
            "sqlmap/1.0",
            ""
        )
        assert not is_safe
        assert "User-Agent suspeito" in message
    
    def test_check_security_suspicious_pattern(self):
        """Testa detecção de padrão suspeito"""
        is_safe, message = self.rate_limiter.check_security(
            "192.168.1.1",
            "Mozilla/5.0",
            "UNION SELECT * FROM users"
        )
        assert not is_safe
        assert "Padrão suspeito" in message
    
    def test_get_client_identifier(self):
        """Testa geração de identificador de cliente"""
        with patch('flask.request') as mock_request:
            mock_request.headers = {'User-Agent': 'test-agent'}
            mock_request.remote_addr = '192.168.1.1'
            
            identifier = self.rate_limiter.get_client_identifier()
            assert identifier.startswith("rate_limit:")
            assert len(identifier) > 20
    
    @patch('redis.Redis')
    def test_is_rate_limited(self, mock_redis):
        """Testa verificação de rate limit"""
        mock_redis_instance = Mock()
        mock_redis.from_url.return_value = mock_redis_instance
        mock_redis_instance.pipeline.return_value.execute.return_value = [0, 1, 5, 1]
        
        is_limited, info = self.rate_limiter.is_rate_limited(
            self.test_identifier,
            self.test_endpoint
        )
        
        assert not is_limited
        assert info["current"] == 5
        assert info["limit"] == 50
'''
    
    return test_code

if __name__ == "__main__":
    # Gerar testes baseados em código real
    test_code = create_rate_limit_tests()
    with open("tests/unit/test_rate_limiting.py", "w") as f:
        f.write(test_code)
    
    print("✅ Testes de rate limiting baseados em código real gerados")
    print("📁 Arquivo: tests/unit/test_rate_limiting.py")
    print("⚠️ Testes NÃO executados automaticamente conforme regras") 