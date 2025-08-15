"""
Sistema de Health Checks para Omni Keywords Finder
Monitora a saúde da aplicação e seus componentes
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import text
from redis import Redis
import httpx

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Status de saúde dos componentes"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Resultado de um health check"""
    name: str
    status: HealthStatus
    response_time: float
    details: Dict[str, Any]
    timestamp: datetime
    error_message: Optional[str] = None


class HealthChecker:
    """Sistema principal de health checks"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.results_cache: Dict[str, HealthCheckResult] = {}
        self.cache_ttl = 30  # segundos
        
    def register_check(self, name: str, check_func: Callable):
        """Registra uma nova verificação de saúde"""
        self.checks[name] = check_func
        logger.info(f"Health check registrado: {name}")
    
    async def run_check(self, name: str) -> HealthCheckResult:
        """Executa uma verificação específica"""
        if name not in self.checks:
            raise ValueError(f"Health check '{name}' não encontrado")
        
        start_time = time.time()
        try:
            result = await self.checks[name]()
            response_time = time.time() - start_time
            
            return HealthCheckResult(
                name=name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                details=result,
                timestamp=datetime.now()
            )
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Health check '{name}' falhou: {str(e)}")
            
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                details={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Executa todas as verificações registradas"""
        tasks = [self.run_check(name) for name in self.checks.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (name, result) in enumerate(zip(self.checks.keys(), results)):
            if isinstance(result, Exception):
                self.results_cache[name] = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    response_time=0.0,
                    details={},
                    timestamp=datetime.now(),
                    error_message=str(result)
                )
            else:
                self.results_cache[name] = result
        
        return self.results_cache
    
    def get_overall_status(self) -> HealthStatus:
        """Determina o status geral baseado em todos os checks"""
        if not self.results_cache:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in self.results_cache.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


class DatabaseHealthCheck:
    """Health checks para banco de dados"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def check_database_connection(self) -> Dict[str, Any]:
        """Verifica conexão com banco de dados"""
        try:
            # Testa conexão com query simples
            result = await self.db_session.execute(text("SELECT 1"))
            result.fetchone()
            
            return {
                "connected": True,
                "database_type": "postgresql",
                "connection_pool_size": getattr(self.db_session.bind, 'pool_size', 'unknown')
            }
        except Exception as e:
            raise Exception(f"Falha na conexão com banco: {str(e)}")
    
    async def check_database_performance(self) -> Dict[str, Any]:
        """Verifica performance do banco de dados"""
        try:
            start_time = time.time()
            
            # Executa query de teste
            result = await self.db_session.execute(text("SELECT COUNT(*) FROM information_schema.tables"))
            count = result.scalar()
            
            response_time = time.time() - start_time
            
            return {
                "response_time": response_time,
                "table_count": count,
                "performance_status": "good" if response_time < 1.0 else "slow"
            }
        except Exception as e:
            raise Exception(f"Falha no teste de performance: {str(e)}")


class CacheHealthCheck:
    """Health checks para cache Redis"""
    
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
    
    async def check_cache_connection(self) -> Dict[str, Any]:
        """Verifica conexão com Redis"""
        try:
            # Testa conexão
            self.redis_client.ping()
            
            # Obtém informações do Redis
            info = self.redis_client.info()
            
            return {
                "connected": True,
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }
        except Exception as e:
            raise Exception(f"Falha na conexão com Redis: {str(e)}")
    
    async def check_cache_performance(self) -> Dict[str, Any]:
        """Verifica performance do cache"""
        try:
            start_time = time.time()
            
            # Testa operação de escrita
            test_key = f"health_check_{int(time.time())}"
            self.redis_client.set(test_key, "test_value", ex=60)
            
            # Testa operação de leitura
            value = self.redis_client.get(test_key)
            
            # Limpa teste
            self.redis_client.delete(test_key)
            
            response_time = time.time() - start_time
            
            return {
                "response_time": response_time,
                "write_success": True,
                "read_success": value == b"test_value",
                "performance_status": "good" if response_time < 0.1 else "slow"
            }
        except Exception as e:
            raise Exception(f"Falha no teste de performance do cache: {str(e)}")


class ExternalServiceHealthCheck:
    """Health checks para serviços externos"""
    
    def __init__(self):
        self.timeout = 10.0
    
    async def check_google_analytics_api(self) -> Dict[str, Any]:
        """Verifica conectividade com Google Analytics API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Testa endpoint básico (requer autenticação real)
                response = await client.get("https://www.googleapis.com/analytics/v3/metadata/columns")
                
                return {
                    "service": "google_analytics",
                    "status": "available" if response.status_code < 500 else "degraded",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            raise Exception(f"Falha na verificação do Google Analytics: {str(e)}")
    
    async def check_search_console_api(self) -> Dict[str, Any]:
        """Verifica conectividade com Search Console API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Testa endpoint básico
                response = await client.get("https://searchconsole.googleapis.com/v1/sites")
                
                return {
                    "service": "search_console",
                    "status": "available" if response.status_code < 500 else "degraded",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            raise Exception(f"Falha na verificação do Search Console: {str(e)}")
    
    async def check_serp_api(self) -> Dict[str, Any]:
        """Verifica conectividade com SERP API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Testa endpoint básico
                response = await client.get("https://serpapi.com/search.json?engine=google&q=test")
                
                return {
                    "service": "serp_api",
                    "status": "available" if response.status_code < 500 else "degraded",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            raise Exception(f"Falha na verificação da SERP API: {str(e)}")


class ApplicationHealthCheck:
    """Health checks específicos da aplicação"""
    
    async def check_memory_usage(self) -> Dict[str, Any]:
        """Verifica uso de memória da aplicação"""
        try:
            import psutil
            
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "memory_usage_mb": memory_info.rss / 1024 / 1024,
                "memory_percent": process.memory_percent(),
                "cpu_percent": process.cpu_percent(),
                "thread_count": process.num_threads()
            }
        except Exception as e:
            raise Exception(f"Falha na verificação de memória: {str(e)}")
    
    async def check_disk_space(self) -> Dict[str, Any]:
        """Verifica espaço em disco"""
        try:
            import psutil
            
            disk_usage = psutil.disk_usage('/')
            
            return {
                "total_gb": disk_usage.total / 1024 / 1024 / 1024,
                "used_gb": disk_usage.used / 1024 / 1024 / 1024,
                "free_gb": disk_usage.free / 1024 / 1024 / 1024,
                "usage_percent": disk_usage.percent
            }
        except Exception as e:
            raise Exception(f"Falha na verificação de disco: {str(e)}")


# Instância global do health checker
health_checker = HealthChecker()


def setup_health_checks(db_session, redis_client: Redis):
    """Configura todos os health checks"""
    # Database checks
    db_checks = DatabaseHealthCheck(db_session)
    health_checker.register_check("database_connection", db_checks.check_database_connection)
    health_checker.register_check("database_performance", db_checks.check_database_performance)
    
    # Cache checks
    cache_checks = CacheHealthCheck(redis_client)
    health_checker.register_check("cache_connection", cache_checks.check_cache_connection)
    health_checker.register_check("cache_performance", cache_checks.check_cache_performance)
    
    # External services checks
    external_checks = ExternalServiceHealthCheck()
    health_checker.register_check("google_analytics", external_checks.check_google_analytics_api)
    health_checker.register_check("search_console", external_checks.check_search_console_api)
    health_checker.register_check("serp_api", external_checks.check_serp_api)
    
    # Application checks
    app_checks = ApplicationHealthCheck()
    health_checker.register_check("memory_usage", app_checks.check_memory_usage)
    health_checker.register_check("disk_space", app_checks.check_disk_space)
    
    logger.info("Health checks configurados com sucesso")


async def get_health_status() -> Dict[str, Any]:
    """Endpoint para obter status de saúde da aplicação"""
    try:
        results = await health_checker.run_all_checks()
        overall_status = health_checker.get_overall_status()
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                name: {
                    "status": result.status.value,
                    "response_time": result.response_time,
                    "details": result.details,
                    "error": result.error_message
                }
                for name, result in results.items()
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter status de saúde: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no health check")


async def get_health_status_simple() -> Dict[str, Any]:
    """Endpoint simples para health check básico"""
    try:
        overall_status = health_checker.get_overall_status()
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no health check simples: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        } 