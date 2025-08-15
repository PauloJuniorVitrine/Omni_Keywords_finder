"""
Middleware de Rate Limiting para Flask e FastAPI.
Integra o sistema de rate limiting inteligente com frameworks web.
"""
import time
import asyncio
from typing import Optional, Dict, Any, Callable
from functools import wraps
import json

from infrastructure.security.rate_limiting import (
    AdaptiveRateLimiter, 
    RequestInfo, 
    RateLimitConfig,
    RateLimitStrategy,
    ThreatLevel
)
from shared.logger import logger

class FlaskRateLimitMiddleware:
    """Middleware de rate limiting para Flask."""
    
    def __init__(self, app, config: Optional[RateLimitConfig] = None):
        self.app = app
        self.config = config or RateLimitConfig()
        self.rate_limiter = AdaptiveRateLimiter(self.config)
        
        # Registra middleware
        self.app.before_request(self._before_request)
        self.app.after_request(self._after_request)
    
    def _extract_request_info(self, request) -> RequestInfo:
        """Extrai informações da requisição Flask."""
        # Obtém IP real (considerando proxies)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        
        return RequestInfo(
            timestamp=time.time(),
            ip=ip,
            user_agent=request.headers.get('User-Agent', ''),
            endpoint=request.endpoint or request.path,
            method=request.method,
            response_time=0.0,  # Será atualizado no after_request
            status_code=200,
            payload_size=len(request.get_data())
        )
    
    def _before_request(self):
        """Executado antes de cada requisição."""
        try:
            # Extrai informações da requisição
            request_info = self._extract_request_info(self.app.request)
            
            # Armazena para uso no after_request
            self.app.request._rate_limit_info = request_info
            self.app.request._start_time = time.time()
            
            # Processa rate limiting
            allowed, info = asyncio.run(
                self.rate_limiter.process_request(request_info)
            )
            
            if not allowed:
                # Retorna erro de rate limit
                response = self.app.response_class(
                    response=json.dumps({
                        'error': 'Rate limit exceeded',
                        'details': info,
                        'retry_after': info.get('reset_time', 60)
                    }),
                    status=429,
                    mimetype='application/json'
                )
                response.headers['Retry-After'] = str(info.get('reset_time', 60))
                response.headers['X-RateLimit-Limit'] = str(self.config.requests_per_minute)
                response.headers['X-RateLimit-Remaining'] = str(info.get('remaining', 0))
                response.headers['X-RateLimit-Reset'] = str(info.get('reset_time', 0))
                
                return response
            
            # Armazena informações para uso posterior
            self.app.request._rate_limit_allowed = True
            self.app.request._rate_limit_info = info
            
        except Exception as e:
            logger.error({
                "event": "rate_limit_middleware_error",
                "status": "error",
                "source": "FlaskRateLimitMiddleware._before_request",
                "details": {"error": str(e)}
            })
            # Em caso de erro, permite a requisição
            self.app.request._rate_limit_allowed = True
    
    def _after_request(self, response):
        """Executado após cada requisição."""
        try:
            if hasattr(self.app.request, '_rate_limit_info'):
                # Atualiza tempo de resposta
                end_time = time.time()
                start_time = getattr(self.app.request, '_start_time', end_time)
                response_time = end_time - start_time
                
                # Atualiza informações da requisição
                request_info = self.app.request._rate_limit_info
                request_info.response_time = response_time
                request_info.status_code = response.status_code
                
                # Adiciona headers de rate limit
                if hasattr(self.app.request, '_rate_limit_info'):
                    info = self.app.request._rate_limit_info
                    response.headers['X-RateLimit-Limit'] = str(self.config.requests_per_minute)
                    response.headers['X-RateLimit-Remaining'] = str(info.get('remaining', 0))
                    response.headers['X-RateLimit-Reset'] = str(info.get('reset_time', 0))
                    response.headers['X-RateLimit-ThreatLevel'] = info.get('threat_level', 'low')
                    response.headers['X-RateLimit-AnomalyScore'] = str(info.get('anomaly_score', 0))
            
        except Exception as e:
            logger.error({
                "event": "rate_limit_middleware_after_error",
                "status": "error",
                "source": "FlaskRateLimitMiddleware._after_request",
                "details": {"error": str(e)}
            })
        
        return response

class FastAPIRateLimitMiddleware:
    """Middleware de rate limiting para FastAPI."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.rate_limiter = AdaptiveRateLimiter(self.config)
    
    async def __call__(self, request, call_next):
        """Middleware principal para FastAPI."""
        try:
            # Extrai informações da requisição
            request_info = await self._extract_request_info(request)
            start_time = time.time()
            
            # Processa rate limiting
            allowed, info = await self.rate_limiter.process_request(request_info)
            
            if not allowed:
                # Retorna erro de rate limit
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={
                        'error': 'Rate limit exceeded',
                        'details': info,
                        'retry_after': info.get('reset_time', 60)
                    },
                    headers={
                        'Retry-After': str(info.get('reset_time', 60)),
                        'X-RateLimit-Limit': str(self.config.requests_per_minute),
                        'X-RateLimit-Remaining': str(info.get('remaining', 0)),
                        'X-RateLimit-Reset': str(info.get('reset_time', 0))
                    }
                )
            
            # Executa requisição
            response = await call_next(request)
            
            # Atualiza tempo de resposta
            end_time = time.time()
            response_time = end_time - start_time
            request_info.response_time = response_time
            request_info.status_code = response.status_code
            
            # Adiciona headers de rate limit
            response.headers['X-RateLimit-Limit'] = str(self.config.requests_per_minute)
            response.headers['X-RateLimit-Remaining'] = str(info.get('remaining', 0))
            response.headers['X-RateLimit-Reset'] = str(info.get('reset_time', 0))
            response.headers['X-RateLimit-ThreatLevel'] = info.get('threat_level', 'low')
            response.headers['X-RateLimit-AnomalyScore'] = str(info.get('anomaly_score', 0))
            
            return response
            
        except Exception as e:
            logger.error({
                "event": "rate_limit_middleware_error",
                "status": "error",
                "source": "FastAPIRateLimitMiddleware.__call__",
                "details": {"error": str(e)}
            })
            # Em caso de erro, permite a requisição
            return await call_next(request)
    
    async def _extract_request_info(self, request) -> RequestInfo:
        """Extrai informações da requisição FastAPI."""
        # Obtém IP real (considerando proxies)
        ip = request.headers.get('value-forwarded-for', request.client.host)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        
        # Obtém tamanho do payload
        body = await request.body()
        payload_size = len(body)
        
        return RequestInfo(
            timestamp=time.time(),
            ip=ip,
            user_agent=request.headers.get('user-agent', ''),
            endpoint=request.url.path,
            method=request.method,
            response_time=0.0,
            status_code=200,
            payload_size=payload_size
        )

# Decorators para uso direto
def flask_rate_limited(requests_per_minute: int = 60, strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE):
    """
    Decorator para rate limiting em rotas Flask.
    
    Args:
        requests_per_minute: Limite de requisições por minuto
        strategy: Estratégia de rate limiting
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                from flask import request, current_app
                
                # Extrai informações da requisição
                ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip and ',' in ip:
                    ip = ip.split(',')[0].strip()
                
                request_info = RequestInfo(
                    timestamp=time.time(),
                    ip=ip,
                    user_agent=request.headers.get('User-Agent', ''),
                    endpoint=f.__name__,
                    method=request.method,
                    response_time=0.0,
                    status_code=200,
                    payload_size=len(request.get_data())
                )
                
                # Obtém rate limiter da aplicação
                rate_limiter = getattr(current_app, '_rate_limiter', None)
                if rate_limiter is None:
                    # Cria rate limiter se não existir
                    config = RateLimitConfig(requests_per_minute=requests_per_minute)
                    rate_limiter = AdaptiveRateLimiter(config)
                    current_app._rate_limiter = rate_limiter
                
                # Processa rate limiting
                allowed, info = asyncio.run(
                    rate_limiter.process_request(request_info)
                )
                
                if not allowed:
                    from flask import jsonify
                    response = jsonify({
                        'error': 'Rate limit exceeded',
                        'details': info,
                        'retry_after': info.get('reset_time', 60)
                    })
                    response.status_code = 429
                    response.headers['Retry-After'] = str(info.get('reset_time', 60))
                    return response
                
                # Executa função original
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error({
                    "event": "flask_rate_limit_decorator_error",
                    "status": "error",
                    "source": "flask_rate_limited",
                    "details": {"error": str(e)}
                })
                # Em caso de erro, permite a requisição
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def fastapi_rate_limited(requests_per_minute: int = 60, strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE):
    """
    Decorator para rate limiting em rotas FastAPI.
    
    Args:
        requests_per_minute: Limite de requisições por minuto
        strategy: Estratégia de rate limiting
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                from fastapi import Request, HTTPException
                
                # Extrai request dos argumentos
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if request is None:
                    # Se não encontrar request, permite a requisição
                    return await func(*args, **kwargs)
                
                # Extrai informações da requisição
                ip = request.headers.get('value-forwarded-for', request.client.host)
                if ip and ',' in ip:
                    ip = ip.split(',')[0].strip()
                
                body = await request.body()
                request_info = RequestInfo(
                    timestamp=time.time(),
                    ip=ip,
                    user_agent=request.headers.get('user-agent', ''),
                    endpoint=request.url.path,
                    method=request.method,
                    response_time=0.0,
                    status_code=200,
                    payload_size=len(body)
                )
                
                # Cria rate limiter
                config = RateLimitConfig(requests_per_minute=requests_per_minute)
                rate_limiter = AdaptiveRateLimiter(config)
                
                # Processa rate limiting
                allowed, info = await rate_limiter.process_request(request_info)
                
                if not allowed:
                    raise HTTPException(
                        status_code=429,
                        detail={
                            'error': 'Rate limit exceeded',
                            'details': info,
                            'retry_after': info.get('reset_time', 60)
                        }
                    )
                
                # Executa função original
                return await func(*args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error({
                    "event": "fastapi_rate_limit_decorator_error",
                    "status": "error",
                    "source": "fastapi_rate_limited",
                    "details": {"error": str(e)}
                })
                # Em caso de erro, permite a requisição
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Função de configuração para Flask
def configure_flask_rate_limiting(app, config: Optional[RateLimitConfig] = None):
    """
    Configura rate limiting para aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
        config: Configuração do rate limiting
    """
    middleware = FlaskRateLimitMiddleware(app, config)
    app._rate_limit_middleware = middleware
    return middleware

# Função de configuração para FastAPI
def configure_fastapi_rate_limiting(app, config: Optional[RateLimitConfig] = None):
    """
    Configura rate limiting para aplicação FastAPI.
    
    Args:
        app: Instância da aplicação FastAPI
        config: Configuração do rate limiting
    """
    middleware = FastAPIRateLimitMiddleware(config)
    app.add_middleware(middleware)
    return middleware 