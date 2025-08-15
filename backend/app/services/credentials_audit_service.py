"""
CredentialsAuditService

Serviço para auditoria de credenciais e monitoramento de segurança
Implementa logs estruturados em JSONL e alertas em tempo real

Tracing ID: AUDIT-001
Data/Hora: 2024-12-27 17:30:00 UTC
Versão: 1.0
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Tipos de eventos de auditoria"""
    CREDENTIAL_CREATED = "credential_created"
    CREDENTIAL_UPDATED = "credential_updated"
    CREDENTIAL_DELETED = "credential_deleted"
    CREDENTIAL_VALIDATED = "credential_validated"
    CREDENTIAL_INVALID = "credential_invalid"
    CREDENTIAL_EXPIRED = "credential_expired"
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SECURITY_ALERT = "security_alert"
    SYSTEM_ERROR = "system_error"

class AuditSeverity(Enum):
    """Níveis de severidade para eventos de auditoria"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Estrutura de dados para eventos de auditoria"""
    timestamp: str
    event_type: str
    severity: str
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    provider: Optional[str]
    credential_id: Optional[str]
    details: Dict[str, Any]
    metadata: Dict[str, Any]

class CredentialsAuditService:
    """Serviço de auditoria para credenciais e segurança"""
    
    def __init__(self, log_dir: str = "logs", max_log_size: int = 10485760):
        """
        Inicializa o serviço de auditoria
        
        Args:
            log_dir: Diretório para armazenar logs
            max_log_size: Tamanho máximo do arquivo de log em bytes
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.max_log_size = max_log_size
        self.current_log_file = self._get_current_log_file()
        
        # Configuração de alertas
        self.alert_thresholds = {
            'failed_validations': 5,  # Alertas após 5 falhas
            'rate_limit_violations': 3,  # Alertas após 3 violações
            'security_events': 1,  # Alertas imediatos para eventos de segurança
        }
        
        # Contadores para alertas
        self.event_counters = {
            'failed_validations': 0,
            'rate_limit_violations': 0,
            'security_events': 0,
        }
        
        # Callbacks para alertas
        self.alert_callbacks: List[callable] = []
        
        logger.info(f"CredentialsAuditService inicializado - Log dir: {self.log_dir}")
    
    def _get_current_log_file(self) -> Path:
        """Retorna o arquivo de log atual baseado na data"""
        today = datetime.now().strftime("%Y-%m-%data")
        return self.log_dir / f"credentials_audit_{today}.jsonl"
    
    def _rotate_log_file(self) -> None:
        """Rotaciona o arquivo de log se necessário"""
        if self.current_log_file.exists() and self.current_log_file.stat().st_size > self.max_log_size:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file = self.log_dir / f"credentials_audit_{timestamp}.jsonl"
            self.current_log_file.rename(new_file)
            logger.info(f"Log file rotated: {new_file}")
    
    def _write_audit_event(self, event: AuditEvent) -> None:
        """Escreve um evento de auditoria no arquivo de log"""
        try:
            self._rotate_log_file()
            
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                json.dump(asdict(event), f, ensure_ascii=False)
                f.write('\n')
                
        except Exception as e:
            logger.error(f"Erro ao escrever evento de auditoria: {e}")
    
    def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity = AuditSeverity.INFO,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        provider: Optional[str] = None,
        credential_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra um evento de auditoria
        
        Args:
            event_type: Tipo do evento
            severity: Severidade do evento
            user_id: ID do usuário
            session_id: ID da sessão
            ip_address: Endereço IP
            user_agent: User agent do navegador
            provider: Provedor de credenciais
            credential_id: ID da credencial
            details: Detalhes adicionais do evento
            metadata: Metadados do evento
        """
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type.value,
            severity=severity.value,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            provider=provider,
            credential_id=credential_id,
            details=details or {},
            metadata=metadata or {}
        )
        
        # Escreve o evento no log
        self._write_audit_event(event)
        
        # Atualiza contadores para alertas
        self._update_event_counters(event_type, severity)
        
        # Verifica se deve gerar alerta
        self._check_alert_conditions(event_type, severity)
        
        logger.info(f"Evento de auditoria registrado: {event_type.value} - {severity.value}")
    
    def _update_event_counters(self, event_type: AuditEventType, severity: AuditSeverity) -> None:
        """Atualiza contadores de eventos para alertas"""
        if event_type == AuditEventType.CREDENTIAL_INVALID:
            self.event_counters['failed_validations'] += 1
        elif event_type == AuditEventType.RATE_LIMIT_EXCEEDED:
            self.event_counters['rate_limit_violations'] += 1
        elif severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            self.event_counters['security_events'] += 1
    
    def _check_alert_conditions(self, event_type: AuditEventType, severity: AuditSeverity) -> None:
        """Verifica condições para gerar alertas"""
        alerts = []
        
        # Verifica falhas de validação
        if self.event_counters['failed_validations'] >= self.alert_thresholds['failed_validations']:
            alerts.append({
                'type': 'failed_validations',
                'message': f"Múltiplas falhas de validação detectadas: {self.event_counters['failed_validations']}",
                'severity': 'warning'
            })
            self.event_counters['failed_validations'] = 0  # Reset counter
        
        # Verifica violações de rate limit
        if self.event_counters['rate_limit_violations'] >= self.alert_thresholds['rate_limit_violations']:
            alerts.append({
                'type': 'rate_limit_violations',
                'message': f"Múltiplas violações de rate limit detectadas: {self.event_counters['rate_limit_violations']}",
                'severity': 'warning'
            })
            self.event_counters['rate_limit_violations'] = 0  # Reset counter
        
        # Verifica eventos de segurança críticos
        if severity == AuditSeverity.CRITICAL:
            alerts.append({
                'type': 'security_critical',
                'message': f"Evento de segurança crítico detectado: {event_type.value}",
                'severity': 'critical'
            })
        
        # Executa callbacks de alerta
        for alert in alerts:
            self._trigger_alert_callbacks(alert)
    
    def _trigger_alert_callbacks(self, alert: Dict[str, Any]) -> None:
        """Executa callbacks de alerta registrados"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Erro ao executar callback de alerta: {e}")
    
    def add_alert_callback(self, callback: callable) -> None:
        """Adiciona um callback para alertas"""
        self.alert_callbacks.append(callback)
        logger.info("Callback de alerta registrado")
    
    def get_audit_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        provider: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """
        Recupera eventos de auditoria com filtros
        
        Args:
            start_date: Data de início para filtro
            end_date: Data de fim para filtro
            event_type: Tipo de evento para filtro
            severity: Severidade para filtro
            provider: Provedor para filtro
            user_id: ID do usuário para filtro
            limit: Limite de resultados
            
        Returns:
            Lista de eventos de auditoria
        """
        events = []
        
        try:
            # Lista todos os arquivos de log
            log_files = sorted(self.log_dir.glob("credentials_audit_*.jsonl"))
            
            for log_file in log_files:
                if not log_file.exists():
                    continue
                
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if len(events) >= limit:
                            break
                        
                        try:
                            event_data = json.loads(line.strip())
                            event = AuditEvent(**event_data)
                            
                            # Aplica filtros
                            if self._apply_filters(event, start_date, end_date, event_type, severity, provider, user_id):
                                events.append(event)
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Linha inválida no arquivo de log: {line.strip()}")
                            continue
            
            # Ordena por timestamp (mais recente primeiro)
            events.sort(key=lambda value: value.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Erro ao recuperar eventos de auditoria: {e}")
        
        return events[:limit]
    
    def _apply_filters(
        self,
        event: AuditEvent,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        event_type: Optional[AuditEventType],
        severity: Optional[AuditSeverity],
        provider: Optional[str],
        user_id: Optional[str]
    ) -> bool:
        """Aplica filtros em um evento de auditoria"""
        # Filtro por data
        if start_date or end_date:
            event_timestamp = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
            if start_date and event_timestamp < start_date:
                return False
            if end_date and event_timestamp > end_date:
                return False
        
        # Filtro por tipo de evento
        if event_type and event.event_type != event_type.value:
            return False
        
        # Filtro por severidade
        if severity and event.severity != severity.value:
            return False
        
        # Filtro por provedor
        if provider and event.provider != provider:
            return False
        
        # Filtro por usuário
        if user_id and event.user_id != user_id:
            return False
        
        return True
    
    def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Retorna estatísticas de auditoria
        
        Args:
            start_date: Data de início para estatísticas
            end_date: Data de fim para estatísticas
            
        Returns:
            Dicionário com estatísticas
        """
        events = self.get_audit_events(start_date, end_date, limit=10000)
        
        stats = {
            'total_events': len(events),
            'events_by_type': {},
            'events_by_severity': {},
            'events_by_provider': {},
            'events_by_user': {},
            'recent_events': events[:10] if events else []
        }
        
        for event in events:
            # Conta por tipo
            stats['events_by_type'][event.event_type] = stats['events_by_type'].get(event.event_type, 0) + 1
            
            # Conta por severidade
            stats['events_by_severity'][event.severity] = stats['events_by_severity'].get(event.severity, 0) + 1
            
            # Conta por provedor
            if event.provider:
                stats['events_by_provider'][event.provider] = stats['events_by_provider'].get(event.provider, 0) + 1
            
            # Conta por usuário
            if event.user_id:
                stats['events_by_user'][event.user_id] = stats['events_by_user'].get(event.user_id, 0) + 1
        
        return stats
    
    def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """
        Remove logs antigos
        
        Args:
            days_to_keep: Número de dias para manter logs
            
        Returns:
            Número de arquivos removidos
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0
        
        try:
            for log_file in self.log_dir.glob("credentials_audit_*.jsonl"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    removed_count += 1
                    logger.info(f"Log file removido: {log_file}")
        except Exception as e:
            logger.error(f"Erro ao limpar logs antigos: {e}")
        
        return removed_count
    
    def export_audit_logs(
        self,
        output_file: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "jsonl"
    ) -> bool:
        """
        Exporta logs de auditoria
        
        Args:
            output_file: Arquivo de saída
            start_date: Data de início
            end_date: Data de fim
            format: Formato de saída (jsonl, csv)
            
        Returns:
            True se exportação foi bem-sucedida
        """
        try:
            events = self.get_audit_events(start_date, end_date, limit=100000)
            
            if format.lower() == "jsonl":
                with open(output_file, 'w', encoding='utf-8') as f:
                    for event in events:
                        json.dump(asdict(event), f, ensure_ascii=False)
                        f.write('\n')
            
            elif format.lower() == "csv":
                import csv
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    if events:
                        writer = csv.DictWriter(f, fieldnames=asdict(events[0]).keys())
                        writer.writeheader()
                        for event in events:
                            writer.writerow(asdict(event))
            
            logger.info(f"Logs exportados para: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar logs: {e}")
            return False

# Instância global do serviço
audit_service = CredentialsAuditService()

# Funções de conveniência para uso em outros módulos
def log_credential_event(
    event_type: AuditEventType,
    provider: str,
    credential_id: str,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    severity: AuditSeverity = AuditSeverity.INFO
) -> None:
    """Função de conveniência para log de eventos de credenciais"""
    audit_service.log_event(
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        provider=provider,
        credential_id=credential_id,
        details=details
    )

def log_security_event(
    event_type: AuditEventType,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    severity: AuditSeverity = AuditSeverity.WARNING
) -> None:
    """Função de conveniência para log de eventos de segurança"""
    audit_service.log_event(
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        details=details
    )

def get_audit_service() -> CredentialsAuditService:
    """Retorna a instância global do serviço de auditoria"""
    return audit_service 