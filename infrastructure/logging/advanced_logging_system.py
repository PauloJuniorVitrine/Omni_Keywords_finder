"""
Sistema de Logs Avançado e Estruturado - Omni Keywords Finder
============================================================

Sistema enterprise para logging estruturado com:
- Logs em formato JSON estruturado
- Rotação automática de logs
- Integração com observabilidade
- Filtros e níveis configuráveis
- Performance monitoring
- Audit trails

Prompt: CHECKLIST_SISTEMA_PREENCHIMENTO_LACUNAS.md - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 1.0.0
Tracing ID: LOGGING_SYSTEM_001
"""

import json
import logging
import logging.handlers
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict, deque
import hashlib
import hmac
import base64

# Integração com observabilidade
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager


class LogLevel(Enum):
    """Níveis de log customizados"""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    AUDIT = 60
    SECURITY = 70


class LogCategory(Enum):
    """Categorias de log"""
    SYSTEM = "system"
    USER = "user"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    AUDIT = "audit"
    ERROR = "error"
    DEBUG = "debug"


@dataclass
class LogContext:
    """Contexto estruturado para logs"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LogEntry:
    """Entrada de log estruturada"""
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    context: LogContext
    data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    hash_signature: Optional[str] = None


class StructuredFormatter(logging.Formatter):
    """Formatador estruturado para logs JSON"""
    
    def __init__(self, include_trace: bool = True, include_hash: bool = True):
        super().__init__()
        self.include_trace = include_trace
        self.include_hash = include_hash
        self.secret_key = os.getenv("LOG_SECRET_KEY", "default-log-key-change-in-production")
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata registro de log em JSON estruturado"""
        
        # Extrair dados do registro
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "logger": record.name
        }
        
        # Adicionar contexto se disponível
        if hasattr(record, 'context') and record.context:
            log_data['context'] = asdict(record.context)
        
        # Adicionar dados extras
        if hasattr(record, 'data') and record.data:
            log_data['data'] = record.data
        
        # Adicionar categoria
        if hasattr(record, 'category'):
            log_data['category'] = record.category.value
        else:
            log_data['category'] = LogCategory.SYSTEM.value
        
        # Adicionar tracing se habilitado
        if self.include_trace:
            if hasattr(record, 'trace_id') and record.trace_id:
                log_data['trace_id'] = record.trace_id
            if hasattr(record, 'span_id') and record.span_id:
                log_data['span_id'] = record.span_id
        
        # Adicionar hash de integridade se habilitado
        if self.include_hash:
            hash_signature = self._generate_hash_signature(log_data)
            log_data['hash_signature'] = hash_signature
        
        # Adicionar exceção se presente
        if record.exc_info:
            log_data['error'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        return json.dumps(log_data, ensure_ascii=False, default=str)
    
    def _generate_hash_signature(self, log_data: Dict[str, Any]) -> str:
        """Gera hash de integridade para o log"""
        # Remover hash existente para calcular novo
        data_to_hash = {key: value for key, value in log_data.items() if key != 'hash_signature'}
        data_str = json.dumps(data_to_hash, sort_keys=True, ensure_ascii=False)
        
        return hmac.new(
            self.secret_key.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()


class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Handler de arquivo com rotação e compressão"""
    
    def __init__(self, filename: str, max_bytes: int = 10*1024*1024, 
                 backup_count: int = 5, compress: bool = True):
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count)
        self.compress = compress
    
    def doRollover(self):
        """Executa rotação com compressão"""
        super().doRollover()
        
        if self.compress and self.backup_count > 0:
            # Comprimir arquivo anterior
            import gzip
            for index in range(self.backup_count - 1, 0, -1):
                sfn = f"{self.baseFilename}.{index}"
                dfn = f"{self.baseFilename}.{index+1}"
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            
            # Comprimir arquivo mais antigo
            if os.path.exists(f"{self.baseFilename}.1"):
                with open(f"{self.baseFilename}.1", 'rb') as f_in:
                    with gzip.open(f"{self.baseFilename}.1.gz", 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(f"{self.baseFilename}.1")


class AdvancedLoggingSystem:
    """Sistema de logging avançado e estruturado"""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: LogLevel = LogLevel.INFO,
                 max_file_size: int = 10*1024*1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_remote: bool = False):
        
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_remote = enable_remote
        
        # Criar diretório de logs
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar observabilidade
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
        
        # Cache de logs para análise
        self.log_cache = deque(maxlen=1000)
        self.error_cache = deque(maxlen=100)
        self.performance_cache = deque(maxlen=500)
        
        # Estatísticas
        self.stats = {
            'total_logs': 0,
            'logs_by_level': defaultdict(int),
            'logs_by_category': defaultdict(int),
            'errors_count': 0,
            'performance_issues': 0
        }
        
        # Configurar loggers
        self._setup_loggers()
        
        # Thread para processamento assíncrono
        self.processing_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.processing_thread.start()
        
        # Log de inicialização
        self.info("Sistema de logging avançado inicializado", 
                 category=LogCategory.SYSTEM,
                 context=LogContext(operation="system_init"))
    
    def _setup_loggers(self):
        """Configura loggers para diferentes categorias"""
        
        # Logger principal
        self.logger = logging.getLogger("omni_keywords_finder")
        self.logger.setLevel(self.log_level.value)
        
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Formatter estruturado
        formatter = StructuredFormatter()
        
        # Handler para console
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Handler para arquivo
        if self.enable_file:
            # Log geral
            general_handler = RotatingFileHandler(
                self.log_dir / "general.log",
                max_bytes=self.max_file_size,
                backup_count=self.backup_count
            )
            general_handler.setFormatter(formatter)
            self.logger.addHandler(general_handler)
            
            # Log de erros
            error_handler = RotatingFileHandler(
                self.log_dir / "errors.log",
                max_bytes=self.max_file_size,
                backup_count=self.backup_count
            )
            error_handler.setLevel(LogLevel.ERROR.value)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)
            
            # Log de auditoria
            audit_handler = RotatingFileHandler(
                self.log_dir / "audit.log",
                max_bytes=self.max_file_size,
                backup_count=self.backup_count
            )
            audit_handler.setLevel(LogLevel.AUDIT.value)
            audit_handler.setFormatter(formatter)
            self.logger.addHandler(audit_handler)
            
            # Log de segurança
            security_handler = RotatingFileHandler(
                self.log_dir / "security.log",
                max_bytes=self.max_file_size,
                backup_count=self.backup_count
            )
            security_handler.setLevel(LogLevel.SECURITY.value)
            security_handler.setFormatter(formatter)
            self.logger.addHandler(security_handler)
        
        # Configurar propagação
        self.logger.propagate = False
    
    def _log(self, level: LogLevel, message: str, category: LogCategory = LogCategory.SYSTEM,
             context: Optional[LogContext] = None, data: Optional[Dict[str, Any]] = None,
             error: Optional[Exception] = None):
        """Método interno para logging"""
        
        # Gerar IDs de tracing
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())[:8]
        
        # Criar registro customizado
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=level.value,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=(type(error), error, error.__traceback__) if error else None
        )
        
        # Adicionar atributos customizados
        record.category = category
        record.context = context
        record.data = data
        record.trace_id = trace_id
        record.span_id = span_id
        
        # Registrar log
        self.logger.handle(record)
        
        # Atualizar estatísticas
        self.stats['total_logs'] += 1
        self.stats['logs_by_level'][level.name] += 1
        self.stats['logs_by_category'][category.value] += 1
        
        # Adicionar ao cache
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            context=context or LogContext(),
            data=data,
            error=error,
            trace_id=trace_id,
            span_id=span_id
        )
        
        self.log_cache.append(log_entry)
        
        # Cache específico para erros
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.stats['errors_count'] += 1
            self.error_cache.append(log_entry)
        
        # Cache específico para performance
        if category == LogCategory.PERFORMANCE:
            self.performance_cache.append(log_entry)
        
        # Registrar métricas
        self.metrics.record_counter(f"logs_total", 1, {"level": level.name, "category": category.value})
        
        # Verificar performance issues
        if context and context.duration_ms and context.duration_ms > 1000:
            self.stats['performance_issues'] += 1
            self.metrics.record_counter("performance_issues", 1)
    
    def trace(self, message: str, **kwargs):
        """Log de trace"""
        self._log(LogLevel.TRACE, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de info"""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de warning"""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de error"""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico"""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def audit(self, message: str, **kwargs):
        """Log de auditoria"""
        self._log(LogLevel.AUDIT, message, **kwargs)
    
    def security(self, message: str, **kwargs):
        """Log de segurança"""
        self._log(LogLevel.SECURITY, message, **kwargs)
    
    def performance(self, message: str, duration_ms: float, **kwargs):
        """Log de performance"""
        context = kwargs.get('context', LogContext())
        context.duration_ms = duration_ms
        kwargs['context'] = context
        kwargs['category'] = LogCategory.PERFORMANCE
        self._log(LogLevel.INFO, message, **kwargs)
    
    def business(self, message: str, **kwargs):
        """Log de negócio"""
        kwargs['category'] = LogCategory.BUSINESS
        self._log(LogLevel.INFO, message, **kwargs)
    
    def _process_logs(self):
        """Processa logs em background"""
        while True:
            try:
                # Processar logs do cache
                while self.log_cache:
                    log_entry = self.log_cache.popleft()
                    self._analyze_log_entry(log_entry)
                
                # Aguardar próximo processamento
                time.sleep(1)
                
            except Exception as e:
                # Log de erro no processamento (sem recursão)
                print(f"Erro no processamento de logs: {e}")
                time.sleep(5)
    
    def _analyze_log_entry(self, log_entry: LogEntry):
        """Analisa entrada de log para insights"""
        
        # Detectar padrões de erro
        if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self._detect_error_patterns(log_entry)
        
        # Detectar problemas de performance
        if log_entry.category == LogCategory.PERFORMANCE:
            self._detect_performance_issues(log_entry)
        
        # Detectar problemas de segurança
        if log_entry.category == LogCategory.SECURITY:
            self._detect_security_issues(log_entry)
    
    def _detect_error_patterns(self, log_entry: LogEntry):
        """Detecta padrões de erro"""
        # Implementar lógica de detecção de padrões
        pass
    
    def _detect_performance_issues(self, log_entry: LogEntry):
        """Detecta problemas de performance"""
        if log_entry.context.duration_ms and log_entry.context.duration_ms > 5000:
            self.warning("Performance issue detectada", 
                        category=LogCategory.PERFORMANCE,
                        data={'duration_ms': log_entry.context.duration_ms})
    
    def _detect_security_issues(self, log_entry: LogEntry):
        """Detecta problemas de segurança"""
        # Implementar lógica de detecção de segurança
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de logs"""
        return {
            'total_logs': self.stats['total_logs'],
            'logs_by_level': dict(self.stats['logs_by_level']),
            'logs_by_category': dict(self.stats['logs_by_category']),
            'errors_count': self.stats['errors_count'],
            'performance_issues': self.stats['performance_issues'],
            'cache_size': len(self.log_cache),
            'error_cache_size': len(self.error_cache),
            'performance_cache_size': len(self.performance_cache)
        }
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna logs recentes"""
        return [asdict(entry) for entry in list(self.log_cache)[-limit:]]
    
    def get_error_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna logs de erro recentes"""
        return [asdict(entry) for entry in list(self.error_cache)[-limit:]]
    
    def get_performance_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna logs de performance recentes"""
        return [asdict(entry) for entry in list(self.performance_cache)[-limit:]]
    
    def clear_caches(self):
        """Limpa caches de logs"""
        self.log_cache.clear()
        self.error_cache.clear()
        self.performance_cache.clear()
        
        self.info("Caches de logs limpos", category=LogCategory.SYSTEM)
    
    def export_logs(self, start_date: datetime, end_date: datetime, 
                   level: Optional[LogLevel] = None, 
                   category: Optional[LogCategory] = None) -> List[Dict[str, Any]]:
        """Exporta logs para análise"""
        # Implementar exportação de logs
        return []
    
    def close(self):
        """Fecha o sistema de logs"""
        self.info("Sistema de logging sendo finalizado", category=LogCategory.SYSTEM)
        
        # Aguardar processamento final
        time.sleep(2)
        
        # Fechar handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


# Instância global do sistema de logs
logging_system = AdvancedLoggingSystem()


def get_logger(name: str = None) -> AdvancedLoggingSystem:
    """Retorna instância do sistema de logs"""
    return logging_system


# Decorator para logging automático
def log_operation(operation: str, category: LogCategory = LogCategory.SYSTEM):
    """Decorator para logging automático de operações"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            context = LogContext(
                operation=operation,
                module=func.__module__,
                function=func.__name__
            )
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                context.duration_ms = duration_ms
                
                logging_system.info(
                    f"Operação {operation} executada com sucesso",
                    category=category,
                    context=context,
                    data={'result_type': type(result).__name__}
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                context.duration_ms = duration_ms
                
                logging_system.error(
                    f"Erro na operação {operation}",
                    category=category,
                    context=context,
                    error=e
                )
                raise
        
        return wrapper
    return decorator 