"""
Structured Logger - JSON Format Implementation

Prompt: CHECKLIST_RESOLUCAO_GARGALOS.md - Fase 3.3.1
Ruleset: enterprise_control_layer.yaml
Date: 2025-01-27
Tracing ID: CHECKLIST_RESOLUCAO_GARGALOS_20250127_001
"""

import json
import logging
import time
import uuid
import traceback
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading
from pathlib import Path

class LogLevel(Enum):
    """Níveis de log padronizados"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Categorias de log para organização"""
    SYSTEM = "system"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    EXTERNAL = "external"

@dataclass
class LogContext:
    """Contexto estruturado para logs"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    service_name: str = "omni-keywords-finder"
    environment: str = "development"
    version: str = "1.0.0"

@dataclass
class LogMetadata:
    """Metadados estruturados para logs"""
    timestamp: str
    level: str
    category: str
    message: str
    context: LogContext
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    extra_fields: Optional[Dict[str, Any]] = None

class StructuredFormatter(logging.Formatter):
    """Formatador estruturado para logs JSON"""
    
    def __init__(self, include_traceback: bool = True, include_extra: bool = True):
        super().__init__()
        self.include_traceback = include_traceback
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata log record em JSON estruturado"""
        # Extrai contexto do record
        context = getattr(record, 'context', LogContext())
        category = getattr(record, 'category', LogCategory.SYSTEM.value)
        trace_id = getattr(record, 'trace_id', None)
        span_id = getattr(record, 'span_id', None)
        duration_ms = getattr(record, 'duration_ms', None)
        error_code = getattr(record, 'error_code', None)
        error_type = getattr(record, 'error_type', None)
        
        # Constrói metadados
        metadata = LogMetadata(
            timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            level=record.levelname,
            category=category,
            message=record.getMessage(),
            context=context,
            trace_id=trace_id,
            span_id=span_id,
            duration_ms=duration_ms,
            error_code=error_code,
            error_type=error_type,
            extra_fields={} if not self.include_extra else {}
        )
        
        # Adiciona stack trace se necessário
        if self.include_traceback and record.exc_info:
            metadata.stack_trace = self.formatException(record.exc_info)
        
        # Adiciona campos extras
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'getMessage', 'exc_info', 
                              'exc_text', 'stack_info', 'context', 'category', 
                              'trace_id', 'span_id', 'duration_ms', 'error_code', 
                              'error_type']:
                    metadata.extra_fields[key] = value
        
        return json.dumps(asdict(metadata), ensure_ascii=False, default=str)

class StructuredLogger:
    """Logger estruturado com suporte a contexto e categorização"""
    
    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        formatter: Optional[StructuredFormatter] = None,
        handlers: Optional[List[logging.Handler]] = None
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Configura formatter padrão se não fornecido
        if not formatter:
            formatter = StructuredFormatter()
        
        # Configura handlers padrão se não fornecidos
        if not handlers:
            handlers = [self._create_default_handler(formatter)]
        
        # Remove handlers existentes e adiciona novos
        self.logger.handlers.clear()
        for handler in handlers:
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Contexto local por thread
        self._local_context = threading.local()
    
    def _create_default_handler(self, formatter: StructuredFormatter) -> logging.Handler:
        """Cria handler padrão (console)"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        return handler
    
    def set_context(self, context: LogContext) -> None:
        """Define contexto para logs da thread atual"""
        self._local_context.context = context
    
    def get_context(self) -> LogContext:
        """Obtém contexto da thread atual"""
        return getattr(self._local_context, 'context', LogContext())
    
    def _log(
        self,
        level: LogLevel,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        extra: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        duration_ms: Optional[float] = None
    ) -> None:
        """Método interno para logging"""
        context = self.get_context()
        
        # Prepara record extra
        record_extra = {
            'context': context,
            'category': category.value,
            'trace_id': getattr(context, 'correlation_id', None),
            'span_id': str(uuid.uuid4())[:8],
            'duration_ms': duration_ms
        }
        
        # Adiciona informações de erro se fornecidas
        if error:
            record_extra['error_type'] = type(error).__name__
            record_extra['error_code'] = getattr(error, 'code', None)
        
        # Adiciona campos extras
        if extra:
            record_extra.update(extra)
        
        # Loga com nível apropriado
        if level == LogLevel.DEBUG:
            self.logger.debug(message, extra=record_extra, exc_info=error is not None)
        elif level == LogLevel.INFO:
            self.logger.info(message, extra=record_extra, exc_info=error is not None)
        elif level == LogLevel.WARNING:
            self.logger.warning(message, extra=record_extra, exc_info=error is not None)
        elif level == LogLevel.ERROR:
            self.logger.error(message, extra=record_extra, exc_info=error is not None)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(message, extra=record_extra, exc_info=error is not None)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log de debug"""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log de informação"""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log de aviso"""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log de erro"""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log crítico"""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    @contextmanager
    def log_operation(
        self,
        operation_name: str,
        category: LogCategory = LogCategory.SYSTEM,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Context manager para logging de operações com duração"""
        start_time = time.time()
        operation_id = str(uuid.uuid4())[:8]
        
        try:
            self.info(
                f"Starting operation: {operation_name}",
                category=category,
                extra={'operation_id': operation_id, **(extra or {})}
            )
            yield operation_id
            duration_ms = (time.time() - start_time) * 1000
            self.info(
                f"Completed operation: {operation_name}",
                category=category,
                duration_ms=duration_ms,
                extra={'operation_id': operation_id, **(extra or {})}
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.error(
                f"Failed operation: {operation_name}",
                category=category,
                error=e,
                duration_ms=duration_ms,
                extra={'operation_id': operation_id, **(extra or {})}
            )
            raise

class LogManager:
    """Gerenciador centralizado de loggers estruturados"""
    
    def __init__(self):
        self.loggers: Dict[str, StructuredLogger] = {}
        self.default_context = LogContext()
    
    def get_logger(self, name: str) -> StructuredLogger:
        """Obtém ou cria logger estruturado"""
        if name not in self.loggers:
            self.loggers[name] = StructuredLogger(name)
        return self.loggers[name]
    
    def set_global_context(self, context: LogContext) -> None:
        """Define contexto global para todos os loggers"""
        self.default_context = context
        for logger in self.loggers.values():
            logger.set_context(context)
    
    def configure_file_handler(
        self,
        log_file: Union[str, Path],
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> None:
        """Configura handler de arquivo com rotação"""
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(StructuredFormatter())
        
        # Adiciona handler a todos os loggers
        for logger in self.loggers.values():
            logger.logger.addHandler(file_handler)
    
    def configure_syslog_handler(self, address: str = '/dev/log') -> None:
        """Configura handler Syslog"""
        from logging.handlers import SysLogHandler
        
        syslog_handler = SysLogHandler(address=address)
        syslog_handler.setFormatter(StructuredFormatter())
        
        # Adiciona handler a todos os loggers
        for logger in self.loggers.values():
            logger.logger.addHandler(syslog_handler)

# Instância global do gerenciador de logs
log_manager = LogManager()

def get_logger(name: str) -> StructuredLogger:
    """Função conveniente para obter logger estruturado"""
    return log_manager.get_logger(name)

def set_log_context(context: LogContext) -> None:
    """Função conveniente para definir contexto de log"""
    log_manager.set_global_context(context)

# Decorator para logging automático de funções
def log_function(
    category: LogCategory = LogCategory.SYSTEM,
    log_args: bool = False,
    log_result: bool = False
):
    """Decorator para logging automático de funções"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            
            # Log de entrada
            extra = {}
            if log_args:
                extra['args'] = str(args)
                extra['kwargs'] = str(kwargs)
            
            with logger.log_operation(
                f"{func.__module__}.{func.__name__}",
                category=category,
                extra=extra
            ) as operation_id:
                try:
                    result = func(*args, **kwargs)
                    
                    # Log de resultado
                    if log_result:
                        logger.info(
                            f"Function {func.__name__} completed successfully",
                            category=category,
                            extra={'result': str(result), 'operation_id': operation_id}
                        )
                    
                    return result
                except Exception as e:
                    logger.error(
                        f"Function {func.__name__} failed",
                        category=category,
                        error=e,
                        extra={'operation_id': operation_id}
                    )
                    raise
        
        return wrapper
    return decorator

# Exemplo de uso
"""
# Configuração básica
logger = get_logger("api.users")

# Logging simples
logger.info("User created successfully", category=LogCategory.BUSINESS)

# Logging com contexto
context = LogContext(
    request_id="req-123",
    user_id="user-456",
    correlation_id="corr-789"
)
logger.set_context(context)

# Logging de operação com duração
with logger.log_operation("database_query", LogCategory.DATABASE) as op_id:
    # ... operação ...
    pass

# Decorator para logging automático
@log_function(LogCategory.API, log_args=True, log_result=True)
def create_user(user_data: dict):
    # ... lógica da função ...
    return user_id
"""

# Configurações predefinidas
LOGGING_CONFIGS = {
    'development': {
        'level': LogLevel.DEBUG,
        'include_traceback': True,
        'include_extra': True
    },
    'production': {
        'level': LogLevel.INFO,
        'include_traceback': True,
        'include_extra': False
    },
    'minimal': {
        'level': LogLevel.WARNING,
        'include_traceback': False,
        'include_extra': False
    }
} 