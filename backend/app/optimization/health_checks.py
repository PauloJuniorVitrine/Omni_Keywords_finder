"""
Health Checks Implementation - Omni Keywords Finder
Tracing ID: HEALTH_CHECKS_20250127_001

Sistema de health checks automáticos para detecção de conexões inválidas
e monitoramento de saúde do banco de dados.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager
import psutil
import json

from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, OperationalError

# Configuração de logging
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Status de saúde das conexões"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Resultado de health check"""
    status: HealthStatus
    message: str
    response_time: float
    timestamp: float
    details: Dict[str, Any]

class DatabaseHealthChecker:
    """
    Verificador de saúde do banco de dados com detecção automática
    de conexões inválidas e monitoramento contínuo
    """
    
    def __init__(
        self,
        database_url: str,
        check_interval: int = 30,
        timeout: int = 10,
        max_retries: int = 3,
        enable_auto_repair: bool = True
    ):
        self.database_url = database_url
        self.check_interval = check_interval
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_auto_repair = enable_auto_repair
        
        # Estado do sistema
        self.is_running = False
        self.last_check = None
        self.check_history: List[HealthCheckResult] = []
        self.max_history_size = 1000
        
        # Threading
        self._lock = threading.RLock()
        self._health_check_thread = None
        self._stop_event = threading.Event()
        
        # Callbacks
        self._status_callbacks: List[Callable[[HealthCheckResult], None]] = []
        self._error_callbacks: List[Callable[[Exception], None]] = []
        
        # Métricas
        self.total_checks = 0
        self.failed_checks = 0
        self.avg_response_time = 0.0
        
        logger.info(f"Database health checker initialized: interval={check_interval}s, timeout={timeout}s")
    
    def add_status_callback(self, callback: Callable[[HealthCheckResult], None]):
        """Adiciona callback para mudanças de status"""
        self._status_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable[[Exception], None]):
        """Adiciona callback para erros"""
        self._error_callbacks.append(callback)
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        if self.is_running:
            logger.warning("Health checker already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        self._health_check_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="DatabaseHealthChecker"
        )
        self._health_check_thread.start()
        
        logger.info("Database health monitoring started")
    
    def stop_monitoring(self):
        """Para monitoramento contínuo"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)
        
        logger.info("Database health monitoring stopped")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while not self._stop_event.is_set():
            try:
                # Executar health check
                result = self._perform_health_check()
                
                # Armazenar resultado
                with self._lock:
                    self.check_history.append(result)
                    if len(self.check_history) > self.max_history_size:
                        self.check_history.pop(0)
                    
                    self.last_check = result
                    self.total_checks += 1
                    
                    if result.status == HealthStatus.CRITICAL:
                        self.failed_checks += 1
                
                # Atualizar métricas
                self._update_metrics(result)
                
                # Notificar callbacks
                self._notify_status_callbacks(result)
                
                # Auto-repair se necessário
                if self.enable_auto_repair and result.status == HealthStatus.CRITICAL:
                    self._attempt_auto_repair()
                
                # Aguardar próximo check
                self._stop_event.wait(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in health check monitoring: {e}")
                self._notify_error_callbacks(e)
                self._stop_event.wait(5)  # Aguardar 5 segundos em caso de erro
    
    def _perform_health_check(self) -> HealthCheckResult:
        """Executa health check completo"""
        start_time = time.time()
        
        try:
            # Teste básico de conectividade
            connectivity_result = self._test_connectivity()
            
            # Teste de performance
            performance_result = self._test_performance()
            
            # Teste de integridade
            integrity_result = self._test_integrity()
            
            # Determinar status geral
            status = self._determine_overall_status([
                connectivity_result, performance_result, integrity_result
            ])
            
            response_time = time.time() - start_time
            
            # Criar resultado
            result = HealthCheckResult(
                status=status,
                message=self._get_status_message(status),
                response_time=response_time,
                timestamp=start_time,
                details={
                    'connectivity': connectivity_result,
                    'performance': performance_result,
                    'integrity': integrity_result
                }
            )
            
            logger.debug(f"Health check completed: {status.value}, response_time={response_time:.3f}s")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Health check failed: {e}")
            
            return HealthCheckResult(
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                response_time=response_time,
                timestamp=start_time,
                details={'error': str(e)}
            )
    
    def _test_connectivity(self) -> Dict[str, Any]:
        """Testa conectividade básica"""
        try:
            engine = create_engine(self.database_url, pool_pre_ping=True)
            
            with engine.connect() as connection:
                # Teste simples de query
                result = connection.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                
                if row and row[0] == 1:
                    return {
                        'status': 'success',
                        'message': 'Database connection successful',
                        'details': {'query_result': row[0]}
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Unexpected query result',
                        'details': {'query_result': row[0] if row else None}
                    }
                    
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connectivity test failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _test_performance(self) -> Dict[str, Any]:
        """Testa performance do banco"""
        try:
            engine = create_engine(self.database_url)
            
            with engine.connect() as connection:
                start_time = time.time()
                
                # Teste de performance com query simples
                result = connection.execute(text("SELECT COUNT(*) FROM information_schema.tables"))
                count = result.fetchone()[0]
                
                response_time = time.time() - start_time
                
                # Avaliar performance
                if response_time < 0.1:
                    performance_status = 'excellent'
                elif response_time < 0.5:
                    performance_status = 'good'
                elif response_time < 1.0:
                    performance_status = 'acceptable'
                else:
                    performance_status = 'poor'
                
                return {
                    'status': 'success',
                    'message': f'Performance test completed: {performance_status}',
                    'details': {
                        'response_time': response_time,
                        'performance_status': performance_status,
                        'table_count': count
                    }
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Performance test failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _test_integrity(self) -> Dict[str, Any]:
        """Testa integridade do banco"""
        try:
            engine = create_engine(self.database_url)
            
            with engine.connect() as connection:
                # Verificar se tabelas críticas existem
                critical_tables = [
                    'users', 'keywords', 'analytics', 'sessions'
                ]
                
                existing_tables = []
                missing_tables = []
                
                for table in critical_tables:
                    try:
                        result = connection.execute(
                            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = :table"),
                            {'table': table}
                        )
                        count = result.fetchone()[0]
                        
                        if count > 0:
                            existing_tables.append(table)
                        else:
                            missing_tables.append(table)
                            
                    except Exception:
                        missing_tables.append(table)
                
                # Avaliar integridade
                if len(missing_tables) == 0:
                    integrity_status = 'complete'
                elif len(missing_tables) <= 2:
                    integrity_status = 'partial'
                else:
                    integrity_status = 'incomplete'
                
                return {
                    'status': 'success',
                    'message': f'Integrity test completed: {integrity_status}',
                    'details': {
                        'integrity_status': integrity_status,
                        'existing_tables': existing_tables,
                        'missing_tables': missing_tables,
                        'total_critical_tables': len(critical_tables)
                    }
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Integrity test failed: {str(e)}',
                'details': {'error': str(e)}
            }
    
    def _determine_overall_status(self, test_results: List[Dict[str, Any]]) -> HealthStatus:
        """Determina status geral baseado nos resultados dos testes"""
        error_count = sum(1 for result in test_results if result.get('status') == 'error')
        
        if error_count == 0:
            return HealthStatus.HEALTHY
        elif error_count == 1:
            return HealthStatus.WARNING
        else:
            return HealthStatus.CRITICAL
    
    def _get_status_message(self, status: HealthStatus) -> str:
        """Obtém mensagem descritiva para o status"""
        messages = {
            HealthStatus.HEALTHY: "Database is healthy and responding normally",
            HealthStatus.WARNING: "Database has minor issues but is operational",
            HealthStatus.CRITICAL: "Database has critical issues requiring attention",
            HealthStatus.UNKNOWN: "Database status is unknown"
        }
        return messages.get(status, "Unknown status")
    
    def _update_metrics(self, result: HealthCheckResult):
        """Atualiza métricas de performance"""
        if self.total_checks > 0:
            # Média móvel do tempo de resposta
            alpha = 0.1  # Fator de suavização
            self.avg_response_time = (
                alpha * result.response_time + 
                (1 - alpha) * self.avg_response_time
            )
    
    def _notify_status_callbacks(self, result: HealthCheckResult):
        """Notifica callbacks de status"""
        for callback in self._status_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def _notify_error_callbacks(self, error: Exception):
        """Notifica callbacks de erro"""
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
    
    def _attempt_auto_repair(self):
        """Tenta reparo automático"""
        logger.warning("Attempting auto-repair for database issues")
        
        try:
            # Implementar lógica de reparo automático
            # Por exemplo: reconectar, limpar conexões, etc.
            pass
            
        except Exception as e:
            logger.error(f"Auto-repair failed: {e}")
    
    def get_current_status(self) -> Optional[HealthCheckResult]:
        """Obtém status atual"""
        with self._lock:
            return self.last_check
    
    def get_status_history(self, limit: int = 100) -> List[HealthCheckResult]:
        """Obtém histórico de status"""
        with self._lock:
            return self.check_history[-limit:] if self.check_history else []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance"""
        with self._lock:
            success_rate = (
                (self.total_checks - self.failed_checks) / self.total_checks * 100
                if self.total_checks > 0 else 0
            )
            
            return {
                'total_checks': self.total_checks,
                'failed_checks': self.failed_checks,
                'success_rate': success_rate,
                'avg_response_time': self.avg_response_time,
                'is_running': self.is_running,
                'last_check': self.last_check.timestamp if self.last_check else None
            }
    
    def force_check(self) -> HealthCheckResult:
        """Força execução de health check"""
        logger.info("Forcing health check")
        return self._perform_health_check()

# Instância global do health checker
_health_checker: Optional[DatabaseHealthChecker] = None

def get_health_checker() -> DatabaseHealthChecker:
    """Obtém instância global do health checker"""
    global _health_checker
    if _health_checker is None:
        raise RuntimeError("Health checker not initialized")
    return _health_checker

def initialize_health_checker(database_url: str, **kwargs) -> DatabaseHealthChecker:
    """Inicializa health checker global"""
    global _health_checker
    if _health_checker is None:
        _health_checker = DatabaseHealthChecker(database_url, **kwargs)
    return _health_checker

def shutdown_health_checker():
    """Desliga health checker global"""
    global _health_checker
    if _health_checker:
        _health_checker.stop_monitoring()
        _health_checker = None 