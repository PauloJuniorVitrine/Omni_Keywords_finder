"""
Logger Especializado para Webhooks - Omni Keywords Finder
Logs estruturados de segurança para webhooks
Prompt: Revisão de segurança de webhooks
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class WebhookLogLevel(Enum):
    """Níveis de log para webhooks"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SECURITY = "security"
    AUDIT = "audit"

class WebhookEventType(Enum):
    """Tipos de eventos de webhook"""
    CREATED = "webhook_created"
    UPDATED = "webhook_updated"
    DELETED = "webhook_deleted"
    TRIGGERED = "webhook_triggered"
    DELIVERED = "webhook_delivered"
    FAILED = "webhook_failed"
    RETRY = "webhook_retry"
    SIGNATURE_VALIDATED = "signature_validated"
    SIGNATURE_INVALID = "signature_invalid"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    MALFORMED = "malformed_payload"

@dataclass
class WebhookLogEntry:
    """Estrutura de log para webhooks"""
    
    # Identificação
    log_id: str
    timestamp: str
    level: str
    
    # Contexto
    event_type: str
    endpoint_id: Optional[str] = None
    event_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Dados do evento
    message: str
    details: Optional[Dict[str, Any]] = None
    
    # Segurança
    signature_valid: Optional[bool] = None
    rate_limited: Optional[bool] = None
    security_score: Optional[int] = None
    
    # Performance
    response_time: Optional[float] = None
    payload_size: Optional[int] = None
    
    # Metadados
    source: str = "webhook_system"
    version: str = "1.0"
    environment: str = "production"

class WebhookLogger:
    """Logger especializado para webhooks com logs estruturados"""
    
    def __init__(self, log_file: str = "logs/webhooks.log"):
        """Inicializa o logger de webhooks"""
        self.log_file = log_file
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Configura o logger"""
        logger = logging.getLogger("webhook_logger")
        logger.setLevel(logging.INFO)
        
        # Evitar duplicação de handlers
        if not logger.handlers:
            # Handler para arquivo
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.INFO)
            
            # Formato estruturado
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            
            # Handler para console (apenas em desenvolvimento)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _create_log_entry(
        self,
        level: WebhookLogLevel,
        event_type: WebhookEventType,
        message: str,
        **kwargs
    ) -> WebhookLogEntry:
        """Cria uma entrada de log estruturada"""
        return WebhookLogEntry(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level.value,
            event_type=event_type.value,
            message=message,
            **kwargs
        )
    
    def _log_entry(self, entry: WebhookLogEntry):
        """Registra uma entrada de log"""
        try:
            # Converter para JSON estruturado
            log_data = asdict(entry)
            log_json = json.dumps(log_data, ensure_ascii=False, default=str)
            
            # Log baseado no nível
            if entry.level == WebhookLogLevel.ERROR.value:
                self.logger.error(log_json)
            elif entry.level == WebhookLogLevel.WARNING.value:
                self.logger.warning(log_json)
            elif entry.level == WebhookLogLevel.SECURITY.value:
                self.logger.warning(f"[SECURITY] {log_json}")
            elif entry.level == WebhookLogLevel.AUDIT.value:
                self.logger.info(f"[AUDIT] {log_json}")
            else:
                self.logger.info(log_json)
                
        except Exception as e:
            # Fallback para log simples em caso de erro
            self.logger.error(f"Erro ao registrar log estruturado: {str(e)}")
            self.logger.info(f"Log simples: {entry.message}")
    
    def log_webhook_created(
        self,
        endpoint_id: str,
        name: str,
        url: str,
        events: List[str],
        user_id: str,
        ip_address: str,
        **kwargs
    ):
        """Log de webhook criado"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.AUDIT,
            event_type=WebhookEventType.CREATED,
            message=f"Webhook criado: {name}",
            endpoint_id=endpoint_id,
            user_id=user_id,
            ip_address=ip_address,
            details={
                "name": name,
                "url": url,
                "events": events,
                "security_level": kwargs.get("security_level", "unknown")
            },
            security_score=self._calculate_security_score(url, kwargs.get("security_level"))
        )
        self._log_entry(entry)
    
    def log_webhook_updated(
        self,
        endpoint_id: str,
        changes: Dict[str, Any],
        user_id: str,
        ip_address: str,
        **kwargs
    ):
        """Log de webhook atualizado"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.AUDIT,
            event_type=WebhookEventType.UPDATED,
            message=f"Webhook atualizado: {endpoint_id}",
            endpoint_id=endpoint_id,
            user_id=user_id,
            ip_address=ip_address,
            details={"changes": changes}
        )
        self._log_entry(entry)
    
    def log_webhook_deleted(
        self,
        endpoint_id: str,
        name: str,
        user_id: str,
        ip_address: str,
        **kwargs
    ):
        """Log de webhook deletado"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.AUDIT,
            event_type=WebhookEventType.DELETED,
            message=f"Webhook deletado: {name}",
            endpoint_id=endpoint_id,
            user_id=user_id,
            ip_address=ip_address,
            details={"name": name}
        )
        self._log_entry(entry)
    
    def log_webhook_triggered(
        self,
        endpoint_id: str,
        event_id: str,
        event_type: str,
        payload_size: int,
        ip_address: str,
        user_agent: str,
        **kwargs
    ):
        """Log de webhook disparado"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.INFO,
            event_type=WebhookEventType.TRIGGERED,
            message=f"Webhook disparado: {event_type}",
            endpoint_id=endpoint_id,
            event_id=event_id,
            ip_address=ip_address,
            user_agent=user_agent,
            payload_size=payload_size,
            details={"event_type": event_type}
        )
        self._log_entry(entry)
    
    def log_webhook_delivered(
        self,
        endpoint_id: str,
        event_id: str,
        response_status: int,
        response_time: float,
        **kwargs
    ):
        """Log de webhook entregue com sucesso"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.INFO,
            event_type=WebhookEventType.DELIVERED,
            message=f"Webhook entregue: {response_status}",
            endpoint_id=endpoint_id,
            event_id=event_id,
            response_status=response_status,
            response_time=response_time,
            details={"status_code": response_status}
        )
        self._log_entry(entry)
    
    def log_webhook_failed(
        self,
        endpoint_id: str,
        event_id: str,
        error_message: str,
        attempt_count: int,
        **kwargs
    ):
        """Log de falha na entrega do webhook"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.ERROR,
            event_type=WebhookEventType.FAILED,
            message=f"Falha na entrega: {error_message}",
            endpoint_id=endpoint_id,
            event_id=event_id,
            details={
                "error": error_message,
                "attempt_count": attempt_count
            }
        )
        self._log_entry(entry)
    
    def log_webhook_retry(
        self,
        endpoint_id: str,
        event_id: str,
        attempt_count: int,
        next_retry: datetime,
        **kwargs
    ):
        """Log de retry de webhook"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.WARNING,
            event_type=WebhookEventType.RETRY,
            message=f"Retry agendado: tentativa {attempt_count}",
            endpoint_id=endpoint_id,
            event_id=event_id,
            details={
                "attempt_count": attempt_count,
                "next_retry": next_retry.isoformat()
            }
        )
        self._log_entry(entry)
    
    def log_signature_validated(
        self,
        endpoint_id: str,
        signature_valid: bool,
        timestamp: str,
        **kwargs
    ):
        """Log de validação de assinatura"""
        level = WebhookLogLevel.SECURITY if signature_valid else WebhookLogLevel.SECURITY
        event_type = WebhookEventType.SIGNATURE_VALIDATED if signature_valid else WebhookEventType.SIGNATURE_INVALID
        
        entry = self._create_log_entry(
            level=level,
            event_type=event_type,
            message=f"Assinatura {'válida' if signature_valid else 'inválida'}",
            endpoint_id=endpoint_id,
            signature_valid=signature_valid,
            details={
                "timestamp": timestamp,
                "tolerance": kwargs.get("tolerance", 300)
            },
            security_score=100 if signature_valid else 0
        )
        self._log_entry(entry)
    
    def log_rate_limited(
        self,
        endpoint_id: str,
        ip_address: str,
        rate_limit: int,
        current_count: int,
        **kwargs
    ):
        """Log de rate limiting"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.WARNING,
            event_type=WebhookEventType.RATE_LIMITED,
            message=f"Rate limit excedido: {current_count}/{rate_limit}",
            endpoint_id=endpoint_id,
            ip_address=ip_address,
            rate_limited=True,
            details={
                "rate_limit": rate_limit,
                "current_count": current_count,
                "window": kwargs.get("window", "1h")
            },
            security_score=50
        )
        self._log_entry(entry)
    
    def log_unauthorized(
        self,
        endpoint_id: Optional[str],
        ip_address: str,
        user_agent: str,
        reason: str,
        **kwargs
    ):
        """Log de acesso não autorizado"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.SECURITY,
            event_type=WebhookEventType.UNAUTHORIZED,
            message=f"Acesso não autorizado: {reason}",
            endpoint_id=endpoint_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"reason": reason},
            security_score=0
        )
        self._log_entry(entry)
    
    def log_malformed_payload(
        self,
        endpoint_id: Optional[str],
        ip_address: str,
        errors: List[str],
        **kwargs
    ):
        """Log de payload malformado"""
        entry = self._create_log_entry(
            level=WebhookLogLevel.WARNING,
            event_type=WebhookEventType.MALFORMED,
            message=f"Payload malformado: {len(errors)} erros",
            endpoint_id=endpoint_id,
            ip_address=ip_address,
            details={"errors": errors},
            security_score=25
        )
        self._log_entry(entry)
    
    def _calculate_security_score(self, url: str, security_level: str) -> int:
        """Calcula score de segurança do webhook"""
        score = 0
        
        # Score baseado na URL
        if url.startswith('https://'):
            score += 30
        elif url.startswith('http://'):
            score += 10
        
        # Score baseado no nível de segurança
        if security_level == 'both':
            score += 40
        elif security_level == 'hmac':
            score += 30
        elif security_level == 'api_key':
            score += 20
        elif security_level == 'none':
            score += 0
        
        # Score baseado no domínio
        if 'localhost' in url or '127.0.0.1' in url:
            score -= 20
        
        return max(0, min(100, score))
    
    def get_security_report(
        self,
        start_date: datetime,
        end_date: datetime,
        endpoint_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera relatório de segurança de webhooks"""
        # Esta função seria implementada para analisar logs
        # e gerar relatórios de segurança
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "endpoint_id": endpoint_id,
            "total_events": 0,
            "security_events": 0,
            "failed_deliveries": 0,
            "rate_limit_violations": 0,
            "unauthorized_access": 0,
            "average_security_score": 0,
            "recommendations": []
        }
    
    def export_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        event_types: Optional[List[WebhookEventType]] = None,
        endpoint_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Exporta logs filtrados"""
        # Esta função seria implementada para exportar logs
        # para análise externa ou auditoria
        return [] 