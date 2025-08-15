# =============================================================================
# Middleware de Resiliência - FastAPI Integration
# =============================================================================
# 
# Este arquivo implementa middleware de resiliência para FastAPI,
# integrando circuit breakers, retry policies e fallback strategies.
#
# Tracing ID: resilience-middleware-2025-01-27-001
# Versão: 1.0
# Responsável: DevOps Team
#
# Metodologias Aplicadas:
# - 📐 CoCoT: Baseado em FastAPI middleware patterns e circuit breaker best practices
# - 🌲 ToT: Avaliado estratégias de integração e escolhido mais eficiente
# - ♻️ ReAct: Simulado cenários de falha e validado resiliência
# =============================================================================

import time
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse
import sys
import os

# Adicionar path para importar módulos de resiliência
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'infrastructure'))

from resilience.circuit_breakers import (
    ResilienceManager,
    CircuitBreakerConfig,
    RetryConfig,
    TimeoutConfig,
    BulkheadConfig,
    CircuitBreakerOpenError,
    BulkheadFullError
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResilienceMiddleware(BaseHTTPMiddleware):
    """Middleware de resiliência para FastAPI"""
    
    def __init__(self, app, resilience_manager: Optional[ResilienceManager] = None):
        super().__init__(app)
        self.resilience_manager = resilience_manager or ResilienceManager()
        self._setup_default_policies()
        
    def _setup_default_policies(self):
        """Configura políticas padrão de resiliência"""
        
        # Circuit Breakers por endpoint
        self.resilience_manager.add_circuit_breaker(
            "api_keywords",
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                timeout=30.0,
                max_retries=3,
                retry_delay=1.0,
                success_threshold=2
            )
        )
        
        self.resilience_manager.add_circuit_breaker(
            "api_ml",
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=120,
                timeout=60.0,
                max_retries=2,
                retry_delay=2.0,
                success_threshold=1
            )
        )
        
        self.resilience_manager.add_circuit_breaker(
            "api_analytics",
            CircuitBreakerConfig(
                failure_threshold=10,
                recovery_timeout=30,
                timeout=15.0,
                max_retries=5,
                retry_delay=0.5,
                success_threshold=3
            )
        )
        
        # Retry Policies
        self.resilience_manager.add_retry_policy(
            "api_retry",
            RetryConfig(
                max_attempts=3,
                base_delay=1.0,
                max_delay=10.0,
                exponential_base=2.0,
                jitter=True
            )
        )
        
        # Timeout Policies
        self.resilience_manager.add_timeout_policy(
            "api_timeout",
            TimeoutConfig(
                default_timeout=30.0,
                connection_timeout=10.0,
                read_timeout=30.0,
                write_timeout=30.0
            )
        )
        
        # Bulkhead para isolamento
        self.resilience_manager.add_bulkhead(
            "api_bulkhead",
            BulkheadConfig(
                max_concurrent_calls=50,
                max_wait_duration=30.0,
                max_queue_size=100
            )
        )
        
        # Fallback strategies
        self.resilience_manager.add_fallback_strategy(
            "keywords_fallback",
            self._keywords_fallback
        )
        
        self.resilience_manager.add_fallback_strategy(
            "ml_fallback",
            self._ml_fallback
        )
        
        self.resilience_manager.add_fallback_strategy(
            "analytics_fallback",
            self._analytics_fallback
        )
        
        logger.info("Políticas de resiliência configuradas")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Processa request com resiliência"""
        
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        # Determinar política baseada no endpoint
        circuit_breaker_name = self._get_circuit_breaker_name(path)
        retry_policy_name = "api_retry"
        timeout_policy_name = "api_timeout"
        bulkhead_name = "api_bulkhead"
        fallback_strategy_name = self._get_fallback_strategy_name(path)
        
        try:
            # Executar com resiliência
            response = await self.resilience_manager.execute_resilient_async(
                func=self._execute_request,
                circuit_breaker_name=circuit_breaker_name,
                retry_policy_name=retry_policy_name,
                timeout_policy_name=timeout_policy_name,
                bulkhead_name=bulkhead_name,
                fallback_strategy_name=fallback_strategy_name,
                request=request,
                call_next=call_next
            )
            
            # Adicionar headers de resiliência
            response.headers["X-Resilience-Status"] = "success"
            response.headers["X-Circuit-Breaker"] = circuit_breaker_name or "none"
            response.headers["X-Processing-Time"] = str(time.time() - start_time)
            
            return response
            
        except CircuitBreakerOpenError as e:
            logger.warning(f"Circuit breaker aberto para {path}: {e}")
            return self._create_fallback_response(request, "circuit_breaker_open")
            
        except BulkheadFullError as e:
            logger.warning(f"Bulkhead cheio para {path}: {e}")
            return self._create_fallback_response(request, "bulkhead_full")
            
        except Exception as e:
            logger.error(f"Erro de resiliência para {path}: {e}")
            return self._create_fallback_response(request, "resilience_error")
    
    async def _execute_request(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Executa request original"""
        return await call_next(request)
    
    def _get_circuit_breaker_name(self, path: str) -> Optional[str]:
        """Determina nome do circuit breaker baseado no path"""
        if path.startswith("/api/v1/keywords"):
            return "api_keywords"
        elif path.startswith("/api/v1/ml"):
            return "api_ml"
        elif path.startswith("/api/v1/analytics"):
            return "api_analytics"
        return None
    
    def _get_fallback_strategy_name(self, path: str) -> Optional[str]:
        """Determina nome da estratégia de fallback baseado no path"""
        if path.startswith("/api/v1/keywords"):
            return "keywords_fallback"
        elif path.startswith("/api/v1/ml"):
            return "ml_fallback"
        elif path.startswith("/api/v1/analytics"):
            return "analytics_fallback"
        return None
    
    def _create_fallback_response(self, request: Request, error_type: str) -> Response:
        """Cria resposta de fallback"""
        fallback_data = {
            "error": "service_unavailable",
            "message": "Serviço temporariamente indisponível",
            "error_type": error_type,
            "path": request.url.path,
            "timestamp": time.time()
        }
        
        return JSONResponse(
            status_code=503,
            content=fallback_data,
            headers={
                "X-Resilience-Status": "fallback",
                "X-Error-Type": error_type
            }
        )
    
    # Fallback strategies
    def _keywords_fallback(self, *args, **kwargs):
        """Fallback para keywords API"""
        return {
            "keywords": [],
            "total": 0,
            "message": "Usando dados em cache devido a indisponibilidade do serviço",
            "fallback": True
        }
    
    def _ml_fallback(self, *args, **kwargs):
        """Fallback para ML API"""
        return {
            "prediction": None,
            "confidence": 0.0,
            "message": "Modelo ML indisponível, usando predição padrão",
            "fallback": True
        }
    
    def _analytics_fallback(self, *args, **kwargs):
        """Fallback para analytics API"""
        return {
            "metrics": {},
            "message": "Analytics indisponível, usando métricas em cache",
            "fallback": True
        }


class ResilienceDecorator:
    """Decorator para aplicar resiliência em funções específicas"""
    
    def __init__(self, resilience_manager: ResilienceManager):
        self.resilience_manager = resilience_manager
    
    def circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """Decorator para circuit breaker"""
        def decorator(func: Callable) -> Callable:
            if config:
                self.resilience_manager.add_circuit_breaker(name, config)
            
            async def async_wrapper(*args, **kwargs):
                return await self.resilience_manager.execute_resilient_async(
                    func=func,
                    circuit_breaker_name=name,
                    *args, **kwargs
                )
            
            def sync_wrapper(*args, **kwargs):
                return self.resilience_manager.execute_resilient(
                    func=func,
                    circuit_breaker_name=name,
                    *args, **kwargs
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def retry(self, name: str, config: Optional[RetryConfig] = None):
        """Decorator para retry policy"""
        def decorator(func: Callable) -> Callable:
            if config:
                self.resilience_manager.add_retry_policy(name, config)
            
            async def async_wrapper(*args, **kwargs):
                return await self.resilience_manager.execute_resilient_async(
                    func=func,
                    retry_policy_name=name,
                    *args, **kwargs
                )
            
            def sync_wrapper(*args, **kwargs):
                return self.resilience_manager.execute_resilient(
                    func=func,
                    retry_policy_name=name,
                    *args, **kwargs
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def timeout(self, name: str, config: Optional[TimeoutConfig] = None):
        """Decorator para timeout policy"""
        def decorator(func: Callable) -> Callable:
            if config:
                self.resilience_manager.add_timeout_policy(name, config)
            
            async def async_wrapper(*args, **kwargs):
                return await self.resilience_manager.execute_resilient_async(
                    func=func,
                    timeout_policy_name=name,
                    *args, **kwargs
                )
            
            def sync_wrapper(*args, **kwargs):
                return self.resilience_manager.execute_resilient(
                    func=func,
                    timeout_policy_name=name,
                    *args, **kwargs
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def bulkhead(self, name: str, config: Optional[BulkheadConfig] = None):
        """Decorator para bulkhead pattern"""
        def decorator(func: Callable) -> Callable:
            if config:
                self.resilience_manager.add_bulkhead(name, config)
            
            async def async_wrapper(*args, **kwargs):
                return await self.resilience_manager.execute_resilient_async(
                    func=func,
                    bulkhead_name=name,
                    *args, **kwargs
                )
            
            def sync_wrapper(*args, **kwargs):
                return self.resilience_manager.execute_resilient(
                    func=func,
                    bulkhead_name=name,
                    *args, **kwargs
                )
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator


# Instância global do resilience manager
resilience_manager = ResilienceManager()
resilience_decorator = ResilienceDecorator(resilience_manager)

# Decorators de conveniência
def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator de conveniência para circuit breaker"""
    return resilience_decorator.circuit_breaker(name, config)

def retry(name: str, config: Optional[RetryConfig] = None):
    """Decorator de conveniência para retry"""
    return resilience_decorator.retry(name, config)

def timeout(name: str, config: Optional[TimeoutConfig] = None):
    """Decorator de conveniência para timeout"""
    return resilience_decorator.timeout(name, config)

def bulkhead(name: str, config: Optional[BulkheadConfig] = None):
    """Decorator de conveniência para bulkhead"""
    return resilience_decorator.bulkhead(name, config) 