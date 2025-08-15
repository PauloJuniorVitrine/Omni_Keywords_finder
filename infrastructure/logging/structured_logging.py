"""
Sistema de Logging Estruturado
Responsável por logging estruturado, correlation IDs e log levels adequados.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 3.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import structlog
import logging
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import os
from pathlib import Path
import threading
from contextvars import ContextVar

# Context variables para correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class LogLevel(Enum):
    """Níveis de log padronizados."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogCategory(Enum):
    """Categorias de log para organização."""
    SYSTEM = "system"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AUDIT = "audit"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL = "external"

@dataclass
class LogContext:
    """Contexto de log com metadados."""
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    service_name: str = "omni_keywords_finder"
    environment: str = "production"
    version: str = "1.0.0"
    timestamp: Optional[datetime] = None
    category: LogCategory = LogCategory.SYSTEM
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class StructuredLogger:
    """
    Sistema de logging estruturado com structlog.
    
    Funcionalidades:
    - Logging estruturado com JSON
    - Correlation IDs
    - Log levels adequados
    - Log rotation
    - Centralização de logs
    """
    
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: str = "INFO",
        enable_json: bool = True,
        enable_console: bool = True,
        enable_file: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        Inicializar sistema de logging estruturado.
        
        Args:
            log_dir: Diretório de logs
            log_level: Nível de log
            enable_json: Habilitar formato JSON
            enable_console: Habilitar output no console
            enable_file: Habilitar logs em arquivo
            max_file_size: Tamanho máximo do arquivo
            backup_count: Número de backups
        """
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.enable_json = enable_json
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Criar diretório de logs
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar structlog
        self._configure_structlog()
        
        # Logger principal
        self.logger = structlog.get_logger()
        
        # Estatísticas de log
        self.log_stats = {
            'total_logs': 0,
            'logs_by_level': {},
            'logs_by_category': {},
            'errors': 0,
            'warnings': 0
        }
        
        self._log_startup()
    
    def _configure_structlog(self):
        """Configurar structlog com processadores."""
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            self._add_correlation_id,
            self._add_user_context,
            structlog.processors.JSONRenderer() if self.enable_json else structlog.dev.ConsoleRenderer()
        ]
        
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Configurar logging padrão
        logging.basicConfig(
            format="%(message)string_data",
            stream=open(os.devnull, "w") if not self.enable_console else None,
            level=getattr(logging, self.log_level.upper())
        )
    
    def _add_correlation_id(self, logger, method_name, event_dict):
        """Adicionar correlation ID ao log."""
        if correlation_id.get():
            event_dict['correlation_id'] = correlation_id.get()
        if user_id.get():
            event_dict['user_id'] = user_id.get()
        if request_id.get():
            event_dict['request_id'] = request_id.get()
        return event_dict
    
    def _add_user_context(self, logger, method_name, event_dict):
        """Adicionar contexto do usuário."""
        event_dict['service'] = 'omni_keywords_finder'
        event_dict['environment'] = os.getenv('ENVIRONMENT', 'development')
        event_dict['version'] = '1.0.0'
        return event_dict
    
    def _log_startup(self):
        """Log de inicialização do sistema."""
        self.logger.info(
            "Sistema de logging estruturado inicializado",
            log_dir=str(self.log_dir),
            log_level=self.log_level,
            enable_json=self.enable_json,
            enable_console=self.enable_console,
            enable_file=self.enable_file
        )
    
    def set_correlation_id(self, correlation_id_value: str):
        """Definir correlation ID para o contexto atual."""
        correlation_id.set(correlation_id_value)
    
    def set_user_context(self, user_id_value: str, request_id_value: Optional[str] = None):
        """Definir contexto do usuário."""
        user_id.set(user_id_value)
        if request_id_value:
            request_id.set(request_id_value)
    
    def log(
        self,
        level: LogLevel,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        **kwargs
    ):
        """
        Log estruturado com metadados.
        
        Args:
            level: Nível do log
            message: Mensagem do log
            category: Categoria do log
            **kwargs: Metadados adicionais
        """
        # Preparar contexto
        context = LogContext(
            correlation_id=correlation_id.get(),
            user_id=user_id.get(),
            request_id=request_id.get(),
            category=category,
            metadata=kwargs
        )
        
        # Adicionar metadados ao log
        log_data = {
            'message': message,
            'category': category.value,
            'context': asdict(context),
            **kwargs
        }
        
        # Log baseado no nível
        if level == LogLevel.DEBUG:
            self.logger.debug(**log_data)
        elif level == LogLevel.INFO:
            self.logger.info(**log_data)
        elif level == LogLevel.WARNING:
            self.logger.warning(**log_data)
        elif level == LogLevel.ERROR:
            self.logger.error(**log_data)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(**log_data)
        
        # Atualizar estatísticas
        self._update_stats(level, category)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log de debug."""
        self.log(LogLevel.DEBUG, message, category, **kwargs)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log de informação."""
        self.log(LogLevel.INFO, message, category, **kwargs)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log de aviso."""
        self.log(LogLevel.WARNING, message, category, **kwargs)
    
    def error(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log de erro."""
        self.log(LogLevel.ERROR, message, category, **kwargs)
    
    def critical(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log crítico."""
        self.log(LogLevel.CRITICAL, message, category, **kwargs)
    
    def _update_stats(self, level: LogLevel, category: LogCategory):
        """Atualizar estatísticas de log."""
        self.log_stats['total_logs'] += 1
        
        # Estatísticas por nível
        level_name = level.value
        self.log_stats['logs_by_level'][level_name] = self.log_stats['logs_by_level'].get(level_name, 0) + 1
        
        # Estatísticas por categoria
        category_name = category.value
        self.log_stats['logs_by_category'][category_name] = self.log_stats['logs_by_category'].get(category_name, 0) + 1
        
        # Contadores específicos
        if level == LogLevel.ERROR:
            self.log_stats['errors'] += 1
        elif level == LogLevel.WARNING:
            self.log_stats['warnings'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de log."""
        return self.log_stats.copy()
    
    def clear_stats(self):
        """Limpar estatísticas de log."""
        self.log_stats = {
            'total_logs': 0,
            'logs_by_level': {},
            'logs_by_category': {},
            'errors': 0,
            'warnings': 0
        }

class LogRotator:
    """Sistema de rotação de logs."""
    
    def __init__(self, log_dir: Path, max_file_size: int, backup_count: int):
        self.log_dir = log_dir
        self.max_file_size = max_file_size
        self.backup_count = backup_count
    
    def rotate_if_needed(self, log_file: Path):
        """Rotacionar arquivo de log se necessário."""
        if not log_file.exists():
            return
        
        if log_file.stat().st_size < self.max_file_size:
            return
        
        # Rotacionar arquivos existentes
        for index in range(self.backup_count - 1, 0, -1):
            old_file = log_file.with_suffix(f'.{index}')
            new_file = log_file.with_suffix(f'.{index + 1}')
            if old_file.exists():
                old_file.rename(new_file)
        
        # Rotacionar arquivo principal
        backup_file = log_file.with_suffix('.1')
        log_file.rename(backup_file)
        
        # Criar novo arquivo
        log_file.touch()

class AuditLogger:
    """Logger específico para auditoria."""
    
    def __init__(self, structured_logger: StructuredLogger):
        self.logger = structured_logger
    
    def log_user_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log de ação do usuário para auditoria."""
        self.logger.info(
            f"User action: {action}",
            category=LogCategory.AUDIT,
            user_id=user_id,
            action=action,
            resource=resource,
            success=success,
            details=details or {}
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        source_ip: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log de evento de segurança."""
        level = LogLevel.ERROR if severity == 'high' else LogLevel.WARNING
        self.logger.log(
            level,
            f"Security event: {event_type}",
            category=LogCategory.SECURITY,
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            details=details or {}
        )
    
    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        threshold: Optional[float] = None
    ):
        """Log de métrica de performance."""
        level = LogLevel.WARNING if threshold and value > threshold else LogLevel.INFO
        self.logger.log(
            level,
            f"Performance metric: {metric_name}",
            category=LogCategory.PERFORMANCE,
            metric_name=metric_name,
            value=value,
            unit=unit,
            threshold=threshold,
            exceeds_threshold=threshold and value > threshold
        )

# Instância global do logger
_structured_logger: Optional[StructuredLogger] = None
_audit_logger: Optional[AuditLogger] = None

def get_logger() -> StructuredLogger:
    """Obter instância global do logger estruturado."""
    global _structured_logger
    if _structured_logger is None:
        _structured_logger = StructuredLogger()
    return _structured_logger

def get_audit_logger() -> AuditLogger:
    """Obter instância global do audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(get_logger())
    return _audit_logger

def set_correlation_id(correlation_id_value: str):
    """Definir correlation ID global."""
    get_logger().set_correlation_id(correlation_id_value)

def set_user_context(user_id_value: str, request_id_value: Optional[str] = None):
    """Definir contexto do usuário global."""
    get_logger().set_user_context(user_id_value, request_id_value)

# Decorator para logging automático
def log_function_call(category: LogCategory = LogCategory.SYSTEM):
    """Decorator para log automático de chamadas de função."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            func_name = func.__name__
            correlation_id_value = str(uuid.uuid4())
            
            logger.set_correlation_id(correlation_id_value)
            
            logger.info(
                f"Function call started: {func_name}",
                category=category,
                function_name=func_name,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"Function call completed: {func_name}",
                    category=category,
                    function_name=func_name,
                    execution_time=execution_time,
                    success=True
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Function call failed: {func_name}",
                    category=category,
                    function_name=func_name,
                    execution_time=execution_time,
                    error=str(e),
                    error_type=type(e).__name__,
                    success=False
                )
                
                raise
        
        return wrapper
    return decorator 