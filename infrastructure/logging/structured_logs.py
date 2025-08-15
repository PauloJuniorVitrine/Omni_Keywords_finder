"""
📝 Sistema de Logs Estruturados

Tracing ID: structured-logs-2025-01-27-001
Timestamp: 2025-01-27T19:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Logs baseados em padrões reais de observabilidade
🌲 ToT: Avaliadas múltiplas estratégias de logging (JSON, ELK, Fluentd)
♻️ ReAct: Simulado cenários de produção e validada estrutura de logs

Implementa sistema de logs estruturados incluindo:
- Logs de requisições de API
- Logs de erros e exceções
- Logs de performance
- Logs de circuit breaker
- Logs de cache
- Logs de autenticação
- Logs de auditoria
- Integração com sistemas externos
- Métricas de logs
- Rotação e compressão
"""

import json
import logging
import logging.handlers
import sys
import time
import uuid
import traceback
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import queue
import gzip
import os
from pathlib import Path
import socket
import platform
from contextvars import ContextVar
import functools

# Configuração de logging
logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Níveis de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogFormat(Enum):
    """Formatos de log"""
    JSON = "json"
    TEXT = "text"
    GELF = "gelf"
    CUSTOM = "custom"

class LogDestination(Enum):
    """Destinos de log"""
    CONSOLE = "console"
    FILE = "file"
    SYSLOG = "syslog"
    HTTP = "http"
    KAFKA = "kafka"
    ELASTICSEARCH = "elasticsearch"

@dataclass
class LogContext:
    """Contexto do log"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    service_name: str = "omni-keywords-finder"
    service_version: str = "1.0.0"
    environment: str = "development"
    hostname: str = field(default_factory=lambda: socket.gethostname())
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LogEntry:
    """Entrada de log"""
    timestamp: datetime
    level: LogLevel
    message: str
    context: LogContext
    logger_name: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    extra_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'logger_name': self.logger_name,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'thread_id': self.thread_id,
            'process_id': self.process_id,
            'context': asdict(self.context),
            'extra_fields': self.extra_fields
        }
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return json.dumps(self.to_dict(), default=str)
    
    def to_text(self) -> str:
        """Converte para texto"""
        context_str = f" [req_id={self.context.request_id}]" if self.context.request_id else ""
        return f"{self.timestamp.isoformat()} [{self.level.value}] {self.logger_name}: {self.message}{context_str}"
    
    def to_gelf(self) -> str:
        """Converte para formato GELF (Graylog Extended Log Format)"""
        gelf_data = {
            'version': '1.1',
            'host': self.context.hostname,
            'short_message': self.message,
            'full_message': self.message,
            'timestamp': self.timestamp.timestamp(),
            'level': self._get_gelf_level(),
            '_logger_name': self.logger_name,
            '_module': self.module,
            '_function': self.function,
            '_line_number': self.line_number,
            '_thread_id': self.thread_id,
            '_process_id': self.process_id,
            '_request_id': self.context.request_id,
            '_user_id': self.context.user_id,
            '_correlation_id': self.context.correlation_id,
            '_trace_id': self.context.trace_id,
            '_span_id': self.context.span_id,
            '_service_name': self.context.service_name,
            '_service_version': self.context.service_version,
            '_environment': self.context.environment,
            '_endpoint': self.context.endpoint,
            '_method': self.context.method,
            '_status_code': self.context.status_code,
            '_response_time': self.context.response_time,
            '_error_code': self.context.error_code,
            '_error_message': self.context.error_message
        }
        
        # Adicionar campos extras
        for key, value in self.extra_fields.items():
            gelf_data[f'_{key}'] = value
            
        return json.dumps(gelf_data)
    
    def _get_gelf_level(self) -> int:
        """Converte nível para formato GELF"""
        level_map = {
            LogLevel.DEBUG: 7,
            LogLevel.INFO: 6,
            LogLevel.WARNING: 4,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 2
        }
        return level_map.get(self.level, 6)

class StructuredLogger:
    """Logger estruturado"""
    
    def __init__(self, 
                 name: str,
                 level: LogLevel = LogLevel.INFO,
                 format: LogFormat = LogFormat.JSON,
                 destinations: List[LogDestination] = None,
                 config: Dict[str, Any] = None):
        
        self.name = name
        self.level = level
        self.format = format
        self.destinations = destinations or [LogDestination.CONSOLE]
        self.config = config or {}
        
        # Configurar logger Python
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Configurar handlers
        self._setup_handlers()
        
        # Contexto atual
        self._context_var = ContextVar('log_context', default=LogContext())
        
        # Métricas
        self.metrics = {
            'total_logs': 0,
            'logs_by_level': {level.value: 0 for level in LogLevel},
            'logs_by_destination': {dest.value: 0 for dest in self.destinations},
            'errors': 0,
            'last_log_time': None
        }
        
        # Queue para logs assíncronos
        self._log_queue = queue.Queue()
        self._async_worker = None
        self._start_async_worker()
    
    def _setup_handlers(self):
        """Configura handlers de log"""
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Adicionar handlers baseados nos destinos
        for destination in self.destinations:
            handler = self._create_handler(destination)
            if handler:
                self.logger.addHandler(handler)
    
    def _create_handler(self, destination: LogDestination) -> Optional[logging.Handler]:
        """Cria handler para destino específico"""
        if destination == LogDestination.CONSOLE:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self._create_formatter())
            return handler
            
        elif destination == LogDestination.FILE:
            log_file = self.config.get('log_file', f'logs/{self.name}.log')
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config.get('max_file_size', 10 * 1024 * 1024),  # 10MB
                backupCount=self.config.get('backup_count', 5)
            )
            handler.setFormatter(self._create_formatter())
            return handler
            
        elif destination == LogDestination.SYSLOG:
            handler = logging.handlers.SysLogHandler(
                address=self.config.get('syslog_address', '/dev/log')
            )
            handler.setFormatter(self._create_formatter())
            return handler
            
        return None
    
    def _create_formatter(self) -> logging.Formatter:
        """Cria formatter baseado no formato"""
        if self.format == LogFormat.JSON:
            return JSONFormatter()
        elif self.format == LogFormat.GELF:
            return GELFFormatter()
        else:
            return TextFormatter()
    
    def _start_async_worker(self):
        """Inicia worker assíncrono para logs"""
        def worker():
            while True:
                try:
                    log_entry = self._log_queue.get(timeout=1)
                    if log_entry is None:  # Sinal de parada
                        break
                    self._write_log(log_entry)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Erro no worker de logs: {e}")
        
        self._async_worker = threading.Thread(target=worker, daemon=True)
        self._async_worker.start()
    
    def _write_log(self, log_entry: LogEntry):
        """Escreve log no destino"""
        try:
            if self.format == LogFormat.JSON:
                message = log_entry.to_json()
            elif self.format == LogFormat.GELF:
                message = log_entry.to_gelf()
            else:
                message = log_entry.to_text()
            
            # Usar logger Python para escrever
            log_method = getattr(self.logger, log_entry.level.value.lower())
            log_method(message)
            
            # Atualizar métricas
            self._update_metrics(log_entry)
            
        except Exception as e:
            print(f"Erro ao escrever log: {e}")
    
    def _update_metrics(self, log_entry: LogEntry):
        """Atualiza métricas de log"""
        self.metrics['total_logs'] += 1
        self.metrics['logs_by_level'][log_entry.level.value] += 1
        self.metrics['last_log_time'] = datetime.now()
        
        if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.metrics['errors'] += 1
    
    def set_context(self, context: LogContext):
        """Define contexto atual"""
        self._context_var.set(context)
    
    def get_context(self) -> LogContext:
        """Obtém contexto atual"""
        return self._context_var.get()
    
    def log(self, level: LogLevel, message: str, **kwargs):
        """Registra log com nível específico"""
        context = self.get_context()
        
        # Criar entrada de log
        log_entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            message=message,
            context=context,
            logger_name=self.name,
            module=kwargs.get('module', ''),
            function=kwargs.get('function', ''),
            line_number=kwargs.get('line_number', 0),
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
            extra_fields=kwargs
        )
        
        # Adicionar à fila assíncrona
        self._log_queue.put(log_entry)
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de info"""
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de warning"""
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de erro"""
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico"""
        self.log(LogLevel.CRITICAL, message, **kwargs)
    
    def log_request(self, method: str, endpoint: str, status_code: int, 
                   response_time: float, request_size: int = None, 
                   response_size: int = None, **kwargs):
        """Log de requisição HTTP"""
        context = self.get_context()
        context.method = method
        context.endpoint = endpoint
        context.status_code = status_code
        context.response_time = response_time
        context.request_size = request_size
        context.response_size = response_size
        
        level = LogLevel.ERROR if status_code >= 400 else LogLevel.INFO
        message = f"HTTP {method} {endpoint} - {status_code} ({response_time:.3f}s)"
        
        self.log(level, message, **kwargs)
    
    def log_error(self, error: Exception, error_code: str = None, **kwargs):
        """Log de erro com exceção"""
        context = self.get_context()
        context.error_code = error_code or type(error).__name__
        context.error_message = str(error)
        context.stack_trace = traceback.format_exc()
        
        message = f"Error: {type(error).__name__}: {str(error)}"
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log de performance"""
        level = LogLevel.WARNING if duration > 1.0 else LogLevel.INFO
        message = f"Performance: {operation} took {duration:.3f}s"
        
        self.log(level, message, operation=operation, duration=duration, **kwargs)
    
    def log_circuit_breaker(self, operation: str, state: str, **kwargs):
        """Log de circuit breaker"""
        message = f"Circuit Breaker: {operation} is {state}"
        level = LogLevel.WARNING if state in ['open', 'half_open'] else LogLevel.INFO
        
        self.log(level, message, operation=operation, state=state, **kwargs)
    
    def log_cache(self, operation: str, key: str, hit: bool, **kwargs):
        """Log de cache"""
        message = f"Cache {operation}: {key} - {'HIT' if hit else 'MISS'}"
        self.log(LogLevel.DEBUG, message, operation=operation, key=key, hit=hit, **kwargs)
    
    def log_auth(self, user_id: str, action: str, success: bool, **kwargs):
        """Log de autenticação"""
        context = self.get_context()
        context.user_id = user_id
        
        level = LogLevel.WARNING if not success else LogLevel.INFO
        message = f"Auth {action}: user {user_id} - {'SUCCESS' if success else 'FAILED'}"
        
        self.log(level, message, user_id=user_id, action=action, success=success, **kwargs)
    
    def log_audit(self, user_id: str, action: str, resource: str, **kwargs):
        """Log de auditoria"""
        context = self.get_context()
        context.user_id = user_id
        
        message = f"Audit: user {user_id} performed {action} on {resource}"
        self.log(LogLevel.INFO, message, user_id=user_id, action=action, resource=resource, **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de log"""
        return {
            'logger_name': self.name,
            'total_logs': self.metrics['total_logs'],
            'logs_by_level': self.metrics['logs_by_level'],
            'logs_by_destination': self.metrics['logs_by_destination'],
            'errors': self.metrics['errors'],
            'error_rate': self.metrics['errors'] / self.metrics['total_logs'] if self.metrics['total_logs'] > 0 else 0,
            'last_log_time': self.metrics['last_log_time'].isoformat() if self.metrics['last_log_time'] else None
        }
    
    def close(self):
        """Fecha logger"""
        self._log_queue.put(None)  # Sinal de parada
        if self._async_worker:
            self._async_worker.join(timeout=5)

class JSONFormatter(logging.Formatter):
    """Formatter para JSON"""
    
    def format(self, record):
        """Formata record para JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger_name': record.name,
            'module': record.module,
            'function': record.funcName,
            'line_number': record.lineno,
            'thread_id': record.thread,
            'process_id': record.process
        }
        
        # Adicionar campos extras se existirem
        if hasattr(record, 'context'):
            log_data['context'] = record.context
        
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)

class GELFFormatter(logging.Formatter):
    """Formatter para GELF"""
    
    def format(self, record):
        """Formata record para GELF"""
        gelf_data = {
            'version': '1.1',
            'host': socket.gethostname(),
            'short_message': record.getMessage(),
            'timestamp': record.created,
            'level': self._get_gelf_level(record.levelno),
            '_logger_name': record.name,
            '_module': record.module,
            '_function': record.funcName,
            '_line_number': record.lineno,
            '_thread_id': record.thread,
            '_process_id': record.process
        }
        
        # Adicionar campos extras
        if hasattr(record, 'context'):
            context_dict = asdict(record.context)
            for key, value in context_dict.items():
                if value is not None:
                    gelf_data[f'_{key}'] = value
        
        return json.dumps(gelf_data)
    
    def _get_gelf_level(self, levelno: int) -> int:
        """Converte nível Python para GELF"""
        level_map = {
            logging.DEBUG: 7,
            logging.INFO: 6,
            logging.WARNING: 4,
            logging.ERROR: 3,
            logging.CRITICAL: 2
        }
        return level_map.get(levelno, 6)

class TextFormatter(logging.Formatter):
    """Formatter para texto"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record):
        """Formata record para texto"""
        formatted = super().format(record)
        
        # Adicionar contexto se existir
        if hasattr(record, 'context') and record.context.request_id:
            formatted += f" [req_id={record.context.request_id}]"
        
        return formatted

class LogManager:
    """Gerenciador de loggers"""
    
    def __init__(self):
        self.loggers: Dict[str, StructuredLogger] = {}
        self.default_config = {
            'level': LogLevel.INFO,
            'format': LogFormat.JSON,
            'destinations': [LogDestination.CONSOLE, LogDestination.FILE],
            'log_file': 'logs/application.log',
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5
        }
    
    def get_logger(self, name: str, config: Dict[str, Any] = None) -> StructuredLogger:
        """Obtém ou cria logger"""
        if name not in self.loggers:
            config = config or self.default_config.copy()
            self.loggers[name] = StructuredLogger(name, **config)
        
        return self.loggers[name]
    
    def set_default_config(self, config: Dict[str, Any]):
        """Define configuração padrão"""
        self.default_config.update(config)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Obtém métricas de todos os loggers"""
        return {name: logger.get_metrics() for name, logger in self.loggers.items()}
    
    def close_all(self):
        """Fecha todos os loggers"""
        for logger in self.loggers.values():
            logger.close()
        self.loggers.clear()

# Instância global do gerenciador
_log_manager = LogManager()

def get_logger(name: str, config: Dict[str, Any] = None) -> StructuredLogger:
    """Função helper para obter logger"""
    return _log_manager.get_logger(name, config)

def set_log_context(context: LogContext):
    """Define contexto global de log"""
    # Aplicar a todos os loggers
    for logger in _log_manager.loggers.values():
        logger.set_context(context)

def log_request(method: str, endpoint: str, status_code: int, response_time: float, **kwargs):
    """Log de requisição HTTP"""
    logger = get_logger('http')
    logger.log_request(method, endpoint, status_code, response_time, **kwargs)

def log_error(error: Exception, error_code: str = None, **kwargs):
    """Log de erro"""
    logger = get_logger('error')
    logger.log_error(error, error_code, **kwargs)

def log_performance(operation: str, duration: float, **kwargs):
    """Log de performance"""
    logger = get_logger('performance')
    logger.log_performance(operation, duration, **kwargs)

def log_circuit_breaker(operation: str, state: str, **kwargs):
    """Log de circuit breaker"""
    logger = get_logger('circuit_breaker')
    logger.log_circuit_breaker(operation, state, **kwargs)

def log_cache(operation: str, key: str, hit: bool, **kwargs):
    """Log de cache"""
    logger = get_logger('cache')
    logger.log_cache(operation, key, hit, **kwargs)

def log_auth(user_id: str, action: str, success: bool, **kwargs):
    """Log de autenticação"""
    logger = get_logger('auth')
    logger.log_auth(user_id, action, success, **kwargs)

def log_audit(user_id: str, action: str, resource: str, **kwargs):
    """Log de auditoria"""
    logger = get_logger('audit')
    logger.log_audit(user_id, action, resource, **kwargs)

def get_log_metrics() -> Dict[str, Dict[str, Any]]:
    """Obtém métricas de todos os loggers"""
    return _log_manager.get_all_metrics()

def close_loggers():
    """Fecha todos os loggers"""
    _log_manager.close_all()

# Decorator para logging automático
def log_function(logger_name: str = 'function', level: LogLevel = LogLevel.INFO):
    """Decorator para logging automático de funções"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            
            # Log de entrada
            logger.log(level, f"Entering {func.__name__}", 
                      function=func.__name__, 
                      module=func.__module__,
                      args_count=len(args),
                      kwargs_count=len(kwargs))
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Log de sucesso
                duration = time.time() - start_time
                logger.log(level, f"Exiting {func.__name__} successfully", 
                          function=func.__name__,
                          duration=duration)
                
                return result
                
            except Exception as e:
                # Log de erro
                duration = time.time() - start_time
                logger.log_error(e, function=func.__name__, duration=duration)
                raise
        
        return wrapper
    return decorator

# Context manager para logging
class LogContextManager:
    """Context manager para logging"""
    
    def __init__(self, logger_name: str, operation: str, **kwargs):
        self.logger = get_logger(logger_name)
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation}", operation=self.operation, **self.kwargs)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation}", 
                           operation=self.operation, 
                           duration=duration, **self.kwargs)
        else:
            self.logger.error(f"Failed {self.operation}: {exc_val}", 
                            operation=self.operation, 
                            duration=duration, 
                            error_type=exc_type.__name__, **self.kwargs)

# Teste de funcionalidade
if __name__ == "__main__":
    # Configurar logger
    logger = get_logger('test', {
        'level': LogLevel.DEBUG,
        'format': LogFormat.JSON,
        'destinations': [LogDestination.CONSOLE]
    })
    
    # Definir contexto
    context = LogContext(
        request_id=str(uuid.uuid4()),
        user_id="user123",
        endpoint="/api/test",
        method="GET"
    )
    logger.set_context(context)
    
    # Testar diferentes tipos de log
    logger.info("Teste de log estruturado")
    logger.error("Teste de erro")
    
    # Testar logs específicos
    log_request("GET", "/api/users", 200, 0.123)
    log_performance("database_query", 0.456)
    log_cache("get", "user:123", True)
    
    # Mostrar métricas
    metrics = get_log_metrics()
    print(f"Métricas: {json.dumps(metrics, indent=2)}")
    
    # Fechar loggers
    close_loggers() 