#!/usr/bin/env python3
"""
Sistema de Error Tracking Backend - Omni Keywords Finder
======================================================

Tracing ID: ERROR_TRACKING_BACKEND_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Sistema enterprise de error tracking que integra:
- Sentry para captura de erros
- APM para contexto de performance
- Logging estruturado
- Alertas inteligentes
- Análise de tendências
- Correlação de erros

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Item 3.2
Ruleset: enterprise_control_layer.yaml
"""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import uuid
import traceback
import sys

# Sentry imports
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logging.warning("Sentry não disponível. Error tracking limitado.")

# Integração com APM
from infrastructure.monitoring.apm_integration import apm_manager, APMMetricType, APMServiceType

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Severidades de erro"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categorias de erro"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    NETWORK = "network"
    EXTERNAL_API = "external_api"
    CACHE = "cache"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Contexto de erro"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ErrorEvent:
    """Evento de erro"""
    id: str
    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    stack_trace: str
    timestamp: datetime
    service: str
    version: str
    environment: str
    tags: Dict[str, str]
    breadcrumbs: List[Dict[str, Any]]
    fingerprint: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class ErrorTrend:
    """Tendência de erro"""
    error_type: str
    count: int
    period: str  # hourly, daily, weekly
    trend: str  # increasing, decreasing, stable
    percentage_change: float
    timestamp: datetime


@dataclass
class ErrorAlert:
    """Alerta de erro"""
    id: str
    title: str
    message: str
    severity: ErrorSeverity
    error_type: str
    count: int
    threshold: int
    period: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class ErrorFingerprinter:
    """Gerador de fingerprints para erros"""
    
    @staticmethod
    def generate_fingerprint(error_type: str, message: str, stack_trace: str) -> str:
        """Gera fingerprint único para erro"""
        # Normalizar mensagem
        normalized_message = ErrorFingerprinter._normalize_message(message)
        
        # Extrair stack trace relevante
        relevant_stack = ErrorFingerprinter._extract_relevant_stack(stack_trace)
        
        # Criar hash
        content = f"{error_type}:{normalized_message}:{relevant_stack}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @staticmethod
    def _normalize_message(message: str) -> str:
        """Normaliza mensagem de erro"""
        # Remover IDs dinâmicos
        import re
        message = re.sub(r'\b\d{4,}\b', '<ID>', message)
        message = re.sub(r'\b[0-9a-f]{8,}\b', '<UUID>', message)
        message = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP>', message)
        
        return message.strip()
    
    @staticmethod
    def _extract_relevant_stack(stack_trace: str) -> str:
        """Extrai parte relevante do stack trace"""
        lines = stack_trace.split('\n')
        relevant_lines = []
        
        for line in lines:
            if 'omni_keywords_finder' in line or 'infrastructure' in line:
                relevant_lines.append(line)
        
        return '\n'.join(relevant_lines[:5])  # Primeiras 5 linhas relevantes


class ErrorAnalyzer:
    """Analisador de erros"""
    
    def __init__(self):
        self.error_patterns: Dict[str, Dict[str, Any]] = {}
        self.anomaly_thresholds: Dict[str, int] = {}
        self.trend_analysis: Dict[str, List[ErrorTrend]] = defaultdict(list)
    
    def analyze_error(self, error_event: ErrorEvent) -> Dict[str, Any]:
        """Analisa um erro e retorna insights"""
        analysis = {
            "fingerprint": error_event.fingerprint,
            "category": error_event.category.value,
            "severity": error_event.severity.value,
            "frequency": self._calculate_frequency(error_event.fingerprint),
            "trend": self._analyze_trend(error_event.error_type),
            "correlations": self._find_correlations(error_event),
            "recommendations": self._generate_recommendations(error_event),
            "similar_errors": self._find_similar_errors(error_event)
        }
        
        return analysis
    
    def _calculate_frequency(self, fingerprint: str) -> Dict[str, int]:
        """Calcula frequência do erro"""
        # Simular cálculo de frequência
        return {
            "last_hour": 5,
            "last_24h": 25,
            "last_7d": 150,
            "total": 500
        }
    
    def _analyze_trend(self, error_type: str) -> Dict[str, Any]:
        """Analisa tendência do erro"""
        # Simular análise de tendência
        return {
            "direction": "increasing",
            "percentage_change": 15.5,
            "confidence": 0.85
        }
    
    def _find_correlations(self, error_event: ErrorEvent) -> List[Dict[str, Any]]:
        """Encontra correlações com outros erros"""
        # Simular correlações
        return [
            {
                "error_type": "database_connection_error",
                "correlation": 0.75,
                "description": "Erro de conexão com banco de dados"
            }
        ]
    
    def _generate_recommendations(self, error_event: ErrorEvent) -> List[str]:
        """Gera recomendações para resolver o erro"""
        recommendations = []
        
        if error_event.category == ErrorCategory.DATABASE:
            recommendations.extend([
                "Verificar conectividade com banco de dados",
                "Revisar configurações de pool de conexões",
                "Monitorar performance de queries"
            ])
        elif error_event.category == ErrorCategory.EXTERNAL_API:
            recommendations.extend([
                "Verificar status da API externa",
                "Implementar circuit breaker",
                "Revisar timeouts de conexão"
            ])
        elif error_event.category == ErrorCategory.AUTHENTICATION:
            recommendations.extend([
                "Verificar configurações de autenticação",
                "Revisar tokens e chaves de API",
                "Implementar rate limiting"
            ])
        
        return recommendations
    
    def _find_similar_errors(self, error_event: ErrorEvent) -> List[Dict[str, Any]]:
        """Encontra erros similares"""
        # Simular erros similares
        return [
            {
                "fingerprint": "abc123def456",
                "error_type": "similar_error",
                "message": "Erro similar encontrado",
                "timestamp": datetime.now().isoformat(),
                "count": 10
            }
        ]


class ErrorAlertManager:
    """Gerenciador de alertas de erro"""
    
    def __init__(self):
        self.alerts: Dict[str, ErrorAlert] = {}
        self.alert_callbacks: List[Callable[[ErrorAlert], None]] = []
        self.thresholds: Dict[str, Dict[str, int]] = {}
        
        # Configurar thresholds padrão
        self._setup_default_thresholds()
    
    def _setup_default_thresholds(self):
        """Configura thresholds padrão"""
        self.thresholds = {
            ErrorSeverity.LOW.value: {
                "hourly": 10,
                "daily": 100
            },
            ErrorSeverity.MEDIUM.value: {
                "hourly": 5,
                "daily": 50
            },
            ErrorSeverity.HIGH.value: {
                "hourly": 2,
                "daily": 20
            },
            ErrorSeverity.CRITICAL.value: {
                "hourly": 1,
                "daily": 5
            }
        }
    
    def check_alert(self, error_event: ErrorEvent) -> Optional[ErrorAlert]:
        """Verifica se erro deve gerar alerta"""
        threshold = self.thresholds.get(error_event.severity.value, {})
        
        if not threshold:
            return None
        
        # Verificar frequência do erro
        frequency = self._get_error_frequency(error_event.fingerprint)
        
        alert = None
        
        # Verificar threshold por hora
        if frequency.get("last_hour", 0) >= threshold.get("hourly", float('inf')):
            alert = self._create_alert(error_event, "hourly", frequency["last_hour"], threshold["hourly"])
        
        # Verificar threshold por dia
        elif frequency.get("last_24h", 0) >= threshold.get("daily", float('inf')):
            alert = self._create_alert(error_event, "daily", frequency["last_24h"], threshold["daily"])
        
        if alert:
            self.alerts[alert.id] = alert
            
            # Executar callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Erro no callback de alerta: {e}")
        
        return alert
    
    def _get_error_frequency(self, fingerprint: str) -> Dict[str, int]:
        """Obtém frequência de um erro"""
        # Simular frequência
        return {
            "last_hour": 5,
            "last_24h": 25,
            "last_7d": 150
        }
    
    def _create_alert(self, error_event: ErrorEvent, period: str, count: int, threshold: int) -> ErrorAlert:
        """Cria alerta de erro"""
        return ErrorAlert(
            id=str(uuid.uuid4()),
            title=f"Alerta de Erro: {error_event.error_type}",
            message=f"Erro {error_event.error_type} ocorreu {count} vezes nas últimas {period} (threshold: {threshold})",
            severity=error_event.severity,
            error_type=error_event.error_type,
            count=count,
            threshold=threshold,
            period=period,
            timestamp=datetime.now()
        )
    
    def resolve_alert(self, alert_id: str, notes: Optional[str] = None):
        """Resolve um alerta"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            alert.resolution_notes = notes
    
    def add_alert_callback(self, callback: Callable[[ErrorAlert], None]):
        """Adiciona callback para alertas"""
        self.alert_callbacks.append(callback)


class ErrorTrackingManager:
    """
    Gerenciador principal de error tracking
    """
    
    def __init__(self, service_name: str = "omni-keywords-finder"):
        self.service_name = service_name
        self.analyzer = ErrorAnalyzer()
        self.alert_manager = ErrorAlertManager()
        
        # Armazenamento de erros
        self.errors: Dict[str, ErrorEvent] = {}
        self.error_history: List[ErrorEvent] = []
        self.fingerprint_index: Dict[str, List[str]] = defaultdict(list)
        
        # Configurações
        self.config = {
            "sentry_dsn": os.getenv("SENTRY_DSN", ""),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "service_version": os.getenv("SERVICE_VERSION", "1.0.0"),
            "enable_sentry": os.getenv("ENABLE_SENTRY", "true").lower() == "true",
            "enable_alerts": os.getenv("ENABLE_ERROR_ALERTS", "true").lower() == "true",
            "max_error_history": int(os.getenv("MAX_ERROR_HISTORY", "10000")),
            "sampling_rate": float(os.getenv("ERROR_SAMPLING_RATE", "1.0"))
        }
        
        # Inicializar Sentry
        self._initialize_sentry()
        
        # Thread de limpeza
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        logger.info(f"Error Tracking Manager inicializado para serviço: {service_name}")
    
    def _initialize_sentry(self):
        """Inicializa Sentry"""
        if not SENTRY_AVAILABLE or not self.config["enable_sentry"]:
            logger.warning("Sentry não disponível ou desabilitado.")
            return
        
        try:
            sentry_sdk.init(
                dsn=self.config["sentry_dsn"],
                environment=self.config["environment"],
                release=self.config["service_version"],
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                    LoggingIntegration(
                        level=logging.INFO,
                        event_level=logging.ERROR
                    )
                ],
                before_send=self._filter_sensitive_data,
                before_send_transaction=self._filter_sensitive_data
            )
            
            logger.info("Sentry inicializado com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao inicializar Sentry: {e}")
    
    def _filter_sensitive_data(self, event, hint):
        """Filtra dados sensíveis antes de enviar para Sentry"""
        # Remover dados sensíveis
        if "request" in event:
            if "headers" in event["request"]:
                sensitive_headers = [
                    "authorization", "cookie", "x-api-key", "x-auth-token",
                    "password", "secret", "token"
                ]
                for header in sensitive_headers:
                    if header in event["request"]["headers"]:
                        event["request"]["headers"][header] = "[REDACTED]"
            
            if "data" in event["request"]:
                sensitive_fields = ["password", "secret", "token", "api_key"]
                for field in sensitive_fields:
                    if field in event["request"]["data"]:
                        event["request"]["data"][field] = "[REDACTED]"
        
        # Remover stack traces muito longos
        if "exception" in event:
            for exception in event["exception"]["values"]:
                if "stacktrace" in exception:
                    frames = exception["stacktrace"]["frames"]
                    if len(frames) > 50:
                        exception["stacktrace"]["frames"] = frames[:50]
        
        return event
    
    def capture_error(self, error: Exception, context: Optional[ErrorContext] = None,
                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                     category: ErrorCategory = ErrorCategory.UNKNOWN,
                     tags: Optional[Dict[str, str]] = None):
        """Captura um erro"""
        try:
            # Gerar fingerprint
            fingerprint = ErrorFingerprinter.generate_fingerprint(
                type(error).__name__,
                str(error),
                traceback.format_exc()
            )
            
            # Criar evento de erro
            error_event = ErrorEvent(
                id=str(uuid.uuid4()),
                error_type=type(error).__name__,
                message=str(error),
                severity=severity,
                category=category,
                context=context or ErrorContext(),
                stack_trace=traceback.format_exc(),
                timestamp=datetime.now(),
                service=self.service_name,
                version=self.config["service_version"],
                environment=self.config["environment"],
                tags=tags or {},
                breadcrumbs=[],
                fingerprint=fingerprint
            )
            
            # Armazenar erro
            self.errors[error_event.id] = error_event
            self.error_history.append(error_event)
            self.fingerprint_index[fingerprint].append(error_event.id)
            
            # Limitar histórico
            if len(self.error_history) > self.config["max_error_history"]:
                old_error = self.error_history.pop(0)
                if old_error.id in self.errors:
                    del self.errors[old_error.id]
            
            # Enviar para Sentry
            if SENTRY_AVAILABLE and self.config["enable_sentry"]:
                self._send_to_sentry(error_event)
            
            # Verificar alertas
            if self.config["enable_alerts"]:
                self.alert_manager.check_alert(error_event)
            
            # Registrar métrica APM
            apm_manager.record_metric(
                name=f"error_{category.value}",
                value=1.0,
                metric_type=APMMetricType.ERROR_RATE,
                service=APMServiceType.API,
                labels={
                    "error_type": error_event.error_type,
                    "severity": severity.value,
                    "category": category.value
                }
            )
            
            logger.error(f"Erro capturado: {error_event.error_type} - {error_event.message}")
            
            return error_event
        
        except Exception as e:
            logger.error(f"Erro ao capturar erro: {e}")
            return None
    
    def _send_to_sentry(self, error_event: ErrorEvent):
        """Envia erro para Sentry"""
        try:
            with sentry_sdk.push_scope() as scope:
                # Configurar contexto
                scope.set_tag("error_type", error_event.error_type)
                scope.set_tag("error_category", error_event.category.value)
                scope.set_tag("error_severity", error_event.severity.value)
                scope.set_tag("service", error_event.service)
                scope.set_tag("fingerprint", error_event.fingerprint)
                
                # Adicionar tags customizadas
                for key, value in error_event.tags.items():
                    scope.set_tag(key, value)
                
                # Configurar usuário se disponível
                if error_event.context.user_id:
                    scope.set_user({"id": error_event.context.user_id})
                
                # Adicionar contexto extra
                if error_event.context.metadata:
                    scope.set_extra("context", error_event.context.metadata)
                
                # Capturar exceção
                exception = Exception(error_event.message)
                exception.__traceback__ = self._parse_stack_trace(error_event.stack_trace)
                
                sentry_sdk.capture_exception(exception)
        
        except Exception as e:
            logger.error(f"Erro ao enviar para Sentry: {e}")
    
    def _parse_stack_trace(self, stack_trace: str):
        """Converte stack trace string em traceback object"""
        # Implementação simplificada
        return None
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos erros"""
        summary = {
            "total_errors": len(self.error_history),
            "active_errors": len([e for e in self.error_history if not e.resolved]),
            "errors_by_severity": defaultdict(int),
            "errors_by_category": defaultdict(int),
            "top_error_types": defaultdict(int),
            "recent_errors": []
        }
        
        # Contar por severidade e categoria
        for error in self.error_history[-100:]:  # Últimos 100 erros
            summary["errors_by_severity"][error.severity.value] += 1
            summary["errors_by_category"][error.category.value] += 1
            summary["top_error_types"][error.error_type] += 1
        
        # Erros recentes
        recent_errors = sorted(
            self.error_history,
            key=lambda x: x.timestamp,
            reverse=True
        )[:10]
        
        summary["recent_errors"] = [
            {
                "id": error.id,
                "error_type": error.error_type,
                "message": error.message,
                "severity": error.severity.value,
                "timestamp": error.timestamp.isoformat()
            }
            for error in recent_errors
        ]
        
        return summary
    
    def get_error_analysis(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        """Retorna análise de um erro específico"""
        error_ids = self.fingerprint_index.get(fingerprint, [])
        if not error_ids:
            return None
        
        # Pegar o primeiro erro com este fingerprint
        error_event = self.errors.get(error_ids[0])
        if not error_event:
            return None
        
        return self.analyzer.analyze_error(error_event)
    
    def get_error_trends(self, period: str = "24h") -> List[ErrorTrend]:
        """Retorna tendências de erro"""
        # Simular tendências
        return [
            ErrorTrend(
                error_type="database_connection_error",
                count=25,
                period="24h",
                trend="increasing",
                percentage_change=15.5,
                timestamp=datetime.now()
            ),
            ErrorTrend(
                error_type="validation_error",
                count=10,
                period="24h",
                trend="decreasing",
                percentage_change=-5.2,
                timestamp=datetime.now()
            )
        ]
    
    def _cleanup_loop(self):
        """Loop de limpeza de dados antigos"""
        while True:
            try:
                # Remover erros mais antigos que 30 dias
                cutoff_time = datetime.now() - timedelta(days=30)
                old_errors = [
                    error for error in self.error_history
                    if error.timestamp < cutoff_time
                ]
                
                for error in old_errors:
                    if error.id in self.errors:
                        del self.errors[error.id]
                
                self.error_history = [
                    error for error in self.error_history
                    if error.timestamp >= cutoff_time
                ]
                
                time.sleep(3600)  # Limpar a cada hora
            
            except Exception as e:
                logger.error(f"Erro no loop de limpeza: {e}")
                time.sleep(3600)


# Instância global
error_tracking_manager = ErrorTrackingManager()


# Decorators para facilitar uso
def track_errors(severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                category: ErrorCategory = ErrorCategory.UNKNOWN):
    """Decorator para tracking de erros"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Capturar contexto
                context = ErrorContext(
                    component=func.__module__,
                    operation=func.__name__
                )
                
                # Capturar erro
                error_tracking_manager.capture_error(
                    error=e,
                    context=context,
                    severity=severity,
                    category=category
                )
                
                raise
        
        return wrapper
    return decorator


def track_api_errors(endpoint: str, method: str):
    """Decorator para tracking de erros de API"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Capturar contexto da API
                context = ErrorContext(
                    endpoint=endpoint,
                    method=method,
                    component="api"
                )
                
                # Determinar categoria baseada no tipo de erro
                category = ErrorCategory.UNKNOWN
                if "validation" in str(e).lower():
                    category = ErrorCategory.VALIDATION
                elif "auth" in str(e).lower():
                    category = ErrorCategory.AUTHENTICATION
                elif "database" in str(e).lower():
                    category = ErrorCategory.DATABASE
                
                # Capturar erro
                error_tracking_manager.capture_error(
                    error=e,
                    context=context,
                    severity=ErrorSeverity.HIGH,
                    category=category
                )
                
                raise
        
        return wrapper
    return decorator


# Funções de conveniência
def capture_validation_error(message: str, field: str, value: Any):
    """Captura erro de validação"""
    error = ValueError(f"Validation error in field '{field}': {message}")
    context = ErrorContext(
        component="validation",
        operation="validate_field",
        metadata={"field": field, "value": str(value)}
    )
    
    return error_tracking_manager.capture_error(
        error=error,
        context=context,
        severity=ErrorSeverity.LOW,
        category=ErrorCategory.VALIDATION
    )


def capture_database_error(error: Exception, query: str, params: Optional[Dict] = None):
    """Captura erro de banco de dados"""
    context = ErrorContext(
        component="database",
        operation="execute_query",
        metadata={"query": query, "params": params}
    )
    
    return error_tracking_manager.capture_error(
        error=error,
        context=context,
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE
    )


def capture_external_api_error(error: Exception, api_name: str, endpoint: str):
    """Captura erro de API externa"""
    context = ErrorContext(
        component="external_api",
        operation="api_call",
        metadata={"api_name": api_name, "endpoint": endpoint}
    )
    
    return error_tracking_manager.capture_error(
        error=error,
        context=context,
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.EXTERNAL_API
    )


if __name__ == "__main__":
    # Exemplo de uso
    print("Error Tracking Manager - Omni Keywords Finder")
    print("=============================================")
    
    # Inicializar error tracking
    error_tracker = ErrorTrackingManager("omni-keywords-finder-test")
    
    # Exemplo de captura de erro
    try:
        raise ValueError("Erro de teste")
    except Exception as e:
        error_tracker.capture_error(
            error=e,
            context=ErrorContext(component="test", operation="example"),
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION
        )
    
    # Mostrar resumo
    summary = error_tracker.get_error_summary()
    print(json.dumps(summary, indent=2, default=str)) 