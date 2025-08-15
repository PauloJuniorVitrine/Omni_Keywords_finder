"""
Configuração do logger para o projeto - Fase 3.1 COMPLETA
Tracing ID: CHECKLIST_FINAL_20250127_003
Data: 2025-01-27
Status: ATUALIZADO PARA SISTEMA AVANÇADO

Sistema de logging unificado que integra:
- structlog para logging estruturado
- Correlation IDs automáticos
- Log rotation configurável
- Integração ELK Stack
- Performance otimizada
"""

import logging
import json
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional
from infrastructure.coleta.config import LOGGING_CONFIG

# Importar sistema avançado de logging
try:
    from infrastructure.logging.advanced_structured_logger import (
        get_logger as get_advanced_logger,
        set_correlation_id,
        set_user_context,
        clear_context,
        log_info,
        log_warning,
        log_error,
        log_critical,
        log_audit,
        log_security,
        log_performance,
        LogCategory
    )
    ADVANCED_LOGGING_AVAILABLE = True
except ImportError:
    ADVANCED_LOGGING_AVAILABLE = False
    print("Sistema avançado de logging não disponível. Usando logger básico.")
    
    # Criar enum dummy para compatibilidade
    from enum import Enum
    class LogCategory(Enum):
        SYSTEM = "system"
        API = "api"
        DATABASE = "database"
        CACHE = "cache"
        SECURITY = "security"
        PERFORMANCE = "performance"
        BUSINESS = "business"
        ERROR = "error"
        AUDIT = "audit"

class JSONFormatter(logging.Formatter):
    """Formatador de logs em JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o registro de log em JSON.
        
        Args:
            record: Registro de log
            
        Returns:
            String JSON formatada
        """
        # Extrai a mensagem original se for um dicionário
        msg = record.msg
        if isinstance(msg, dict):
            log_data = msg.copy()
        else:
            log_data = {"message": str(msg)}

        # Garante campos obrigatórios
        log_data["timestamp"] = datetime.utcnow().isoformat()
        log_data["level"] = record.levelname
        log_data["event"] = str(log_data.get("event", "log_message"))
        log_data["status"] = str(log_data.get("status", "info"))
        log_data["source"] = str(log_data.get("source", record.name))
        log_data["details"] = log_data.get("details", {})
            
        # Adiciona detalhes do erro se houver
        if record.exc_info:
            log_data["details"]["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }

        return json.dumps(log_data)

class LoggerWrapper:
    """Wrapper para o logger global que permite substituição."""
    
    def __init__(self):
        self._logger = None
        self._advanced_logger = None
    
    def __getattr__(self, name):
        if self._logger is None:
            self._logger = self._setup_logger()
        attr = getattr(self._logger, name)
        def safe_call(*args, **kwargs):
            try:
                msg = args[0] if len(args) > 0 else '[log vazio]'
                # Serializa dicionários para string JSON
                if isinstance(msg, dict):
                    msg = json.dumps(msg, ensure_ascii=False)
                # Não passa argumentos extras para evitar erro de formatação
                return attr(msg)
            except Exception as e:
                print(f'[LOGGER-ERRO] Falha ao logar: {e} | args={args} | kwargs={kwargs}')
                return None
        return safe_call
    
    def set_logger(self, logger: logging.Logger) -> None:
        """
        Define o logger global.
        
        Args:
            logger: Logger a ser usado
        """
        self._logger = logger
    
    def _setup_logger(self) -> logging.Logger:
        """
        Configura e retorna um novo logger.
        
        Returns:
            Logger configurado
        """
        logger = logging.getLogger("omni_keywords")
        logger.setLevel(LOGGING_CONFIG["nivel"])
        
        # Remove handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Configura handler apropriado
        if os.getenv("PYTEST_CURRENT_TEST"):
            # Em ambiente de teste, usa handler padrão
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('%(message)s'))
        else:
            # Em produção, usa handler JSON
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JSONFormatter())
        
        logger.addHandler(handler)
        
        # Remove handlers padrão
        logger.propagate = False
        
        return logger

# Logger global
logger = LoggerWrapper()

# Funções de conveniência para o sistema avançado
def get_advanced_logger_instance():
    """Obter instância do logger avançado."""
    if ADVANCED_LOGGING_AVAILABLE:
        return get_advanced_logger()
    return None

def log_with_correlation_id(correlation_id: str, level: str, message: str, **kwargs):
    """Log com correlation ID usando sistema avançado."""
    if ADVANCED_LOGGING_AVAILABLE:
        set_correlation_id(correlation_id)
        log_func = getattr(sys.modules[__name__], f"log_{level.lower()}", log_info)
        log_func(message, **kwargs)
    else:
        # Fallback para logger básico
        log_data = {
            "correlation_id": correlation_id,
            "message": message,
            **kwargs
        }
        logger.info(json.dumps(log_data))

def log_with_user_context(user_id: str, request_id: str, level: str, message: str, **kwargs):
    """Log com contexto do usuário usando sistema avançado."""
    if ADVANCED_LOGGING_AVAILABLE:
        set_user_context(user_id, request_id)
        log_func = getattr(sys.modules[__name__], f"log_{level.lower()}", log_info)
        log_func(message, **kwargs)
    else:
        # Fallback para logger básico
        log_data = {
            "user_id": user_id,
            "request_id": request_id,
            "message": message,
            **kwargs
        }
        logger.info(json.dumps(log_data))

def log_system_info(message: str, **kwargs):
    """Log de informação do sistema."""
    if ADVANCED_LOGGING_AVAILABLE:
        log_info(message, LogCategory.SYSTEM, **kwargs)
    else:
        log_data = {"message": message, "category": "system", **kwargs}
        logger.info(json.dumps(log_data))

def log_api_call(endpoint: str, method: str, status_code: int, response_time: float, **kwargs):
    """Log de chamada de API."""
    if ADVANCED_LOGGING_AVAILABLE:
        log_info(
            f"API Call: {method} {endpoint}",
            LogCategory.API,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time * 1000,
            **kwargs
        )
    else:
        log_data = {
            "message": f"API Call: {method} {endpoint}",
            "category": "api",
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": response_time * 1000,
            **kwargs
        }
        logger.info(json.dumps(log_data))

def log_database_operation(operation: str, table: str, duration: float, **kwargs):
    """Log de operação de banco de dados."""
    if ADVANCED_LOGGING_AVAILABLE:
        log_info(
            f"Database: {operation} on {table}",
            LogCategory.DATABASE,
            operation=operation,
            table=table,
            duration_ms=duration * 1000,
            **kwargs
        )
    else:
        log_data = {
            "message": f"Database: {operation} on {table}",
            "category": "database",
            "operation": operation,
            "table": table,
            "duration_ms": duration * 1000,
            **kwargs
        }
        logger.info(json.dumps(log_data))

def log_cache_operation(operation: str, key: str, hit: bool, **kwargs):
    """Log de operação de cache."""
    if ADVANCED_LOGGING_AVAILABLE:
        log_info(
            f"Cache: {operation} {key}",
            LogCategory.CACHE,
            operation=operation,
            key=key,
            hit=hit,
            **kwargs
        )
    else:
        log_data = {
            "message": f"Cache: {operation} {key}",
            "category": "cache",
            "operation": operation,
            "key": key,
            "hit": hit,
            **kwargs
        }
        logger.info(json.dumps(log_data))

def log_security_event(event: str, user_id: str = None, ip_address: str = None, **kwargs):
    """Log de evento de segurança."""
    if ADVANCED_LOGGING_AVAILABLE:
        log_security(
            f"Security: {event}",
            user_id=user_id,
            ip_address=ip_address,
            **kwargs
        )
    else:
        log_data = {
            "message": f"Security: {event}",
            "category": "security",
            "user_id": user_id,
            "ip_address": ip_address,
            **kwargs
        }
        logger.warning(json.dumps(log_data))

def log_performance_metric(metric: str, value: float, unit: str = "ms", **kwargs):
    """Log de métrica de performance."""
    if ADVANCED_LOGGING_AVAILABLE:
        log_performance(
            f"Performance: {metric} = {value}{unit}",
            metric=metric,
            value=value,
            unit=unit,
            **kwargs
        )
    else:
        log_data = {
            "message": f"Performance: {metric} = {value}{unit}",
            "category": "performance",
            "metric": metric,
            "value": value,
            "unit": unit,
            **kwargs
        }
        logger.info(json.dumps(log_data))

def log_business_event(event: str, user_id: str = None, **kwargs):
    """Log de evento de negócio."""
    if ADVANCED_LOGGING_AVAILABLE:
        log_info(
            f"Business: {event}",
            LogCategory.BUSINESS,
            user_id=user_id,
            **kwargs
        )
    else:
        log_data = {
            "message": f"Business: {event}",
            "category": "business",
            "user_id": user_id,
            **kwargs
        }
        logger.info(json.dumps(log_data))

def log_audit_event(event: str, user_id: str, action: str, resource: str, **kwargs):
    """Log de evento de auditoria."""
    if ADVANCED_LOGGING_AVAILABLE:
        log_audit(
            f"Audit: {event}",
            user_id=user_id,
            action=action,
            resource=resource,
            **kwargs
        )
    else:
        log_data = {
            "message": f"Audit: {event}",
            "category": "audit",
            "user_id": user_id,
            "action": action,
            "resource": resource,
            **kwargs
        }
        logger.info(json.dumps(log_data))

# Função para inicializar o sistema de logging
def initialize_logging_system():
    """Inicializar sistema de logging completo."""
    if ADVANCED_LOGGING_AVAILABLE:
        try:
            # Inicializar logger avançado
            advanced_logger = get_advanced_logger()
            
            # Inicializar rotador de logs
            from infrastructure.logging.log_rotation_config import get_log_rotator
            log_rotator = get_log_rotator()
            
            # Inicializar configuração ELK
            from infrastructure.logging.elk_stack_config import get_elk_manager
            elk_manager = get_elk_manager()
            
            # Log de inicialização
            log_info(
                "Sistema de logging completo inicializado",
                LogCategory.SYSTEM,
                advanced_logging=True,
                log_rotation=True,
                elk_integration=elk_manager.config.enabled
            )
            
            return True
            
        except Exception as e:
            print(f"Erro ao inicializar sistema avançado de logging: {e}")
            return False
    else:
        print("Sistema básico de logging inicializado")
        return True

# Inicializar automaticamente se não estiver em teste
if not os.getenv("PYTEST_CURRENT_TEST"):
    initialize_logging_system() 