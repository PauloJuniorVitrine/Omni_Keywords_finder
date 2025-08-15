"""
Sistema de Logging de Segurança para Auditoria
Implementa logs estruturados para detecção de ataques e compliance
"""

import json
import logging
import time
import hashlib
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
import threading
from dataclasses import dataclass, asdict
from flask import request, g

class SecurityEventType(Enum):
    """Tipos de eventos de segurança"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGIN_BLOCKED = "login_blocked"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    OAUTH_LOGIN = "oauth_login"
    OAUTH_FAILED = "oauth_failed"
    SESSION_EXPIRED = "session_expired"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ADMIN_ACTION = "admin_action"

class SecurityLevel(Enum):
    """Níveis de segurança"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ALERT = "alert"

@dataclass
class SecurityEvent:
    """Estrutura de evento de segurança"""
    event_type: SecurityEventType
    timestamp: str
    user_id: Optional[str]
    username: Optional[str]
    ip_address: str
    user_agent: str
    session_id: Optional[str]
    details: Dict[str, Any]
    security_level: SecurityLevel
    risk_score: int
    correlation_id: Optional[str]
    source: str = "auth_api"

class SecurityAuditLogger:
    """Logger de auditoria de segurança"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.risk_patterns = self._load_risk_patterns()
        self.alert_threshold = int(os.getenv('SECURITY_ALERT_THRESHOLD', 7))
        self._lock = threading.Lock()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura o logger de segurança"""
        logger = logging.getLogger('security_audit')
        logger.setLevel(logging.INFO)
        
        # Evitar duplicação de handlers
        if not logger.handlers:
            # Handler para arquivo
            log_file = os.getenv('SECURITY_LOG_FILE', 'logs/security_audit.log')
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # Formato estruturado JSON
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            
            # Handler para console em desenvolvimento
            if os.getenv('FLASK_ENV') == 'development':
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
        
        return logger
    
    def _load_risk_patterns(self) -> Dict[str, int]:
        """Carrega padrões de risco"""
        return {
            'multiple_failed_logins': 5,
            'suspicious_ip': 3,
            'unusual_time': 2,
            'suspicious_user_agent': 4,
            'rate_limit_exceeded': 6,
            'admin_action': 1,
            'oauth_failure': 3,
            'session_hijacking': 8,
            'brute_force': 9
        }
    
    def _calculate_risk_score(self, event: SecurityEvent) -> int:
        """Calcula score de risco do evento"""
        base_score = 0
        
        # Análise de padrões de risco
        details = event.details
        
        # Múltiplas tentativas falhadas
        if details.get('failed_attempts', 0) > 3:
            base_score += self.risk_patterns['multiple_failed_logins']
        
        # IP suspeito
        if details.get('suspicious_ip', False):
            base_score += self.risk_patterns['suspicious_ip']
        
        # Horário incomum
        if details.get('unusual_time', False):
            base_score += self.risk_patterns['unusual_time']
        
        # User-Agent suspeito
        if details.get('suspicious_user_agent', False):
            base_score += self.risk_patterns['suspicious_user_agent']
        
        # Rate limit excedido
        if event.event_type == SecurityEventType.RATE_LIMIT_EXCEEDED:
            base_score += self.risk_patterns['rate_limit_exceeded']
        
        # Ação administrativa
        if event.event_type == SecurityEventType.ADMIN_ACTION:
            base_score += self.risk_patterns['admin_action']
        
        # Falha OAuth
        if event.event_type == SecurityEventType.OAUTH_FAILED:
            base_score += self.risk_patterns['oauth_failure']
        
        return min(base_score, 10)  # Máximo 10
    
    def _detect_anomalies(self, event: SecurityEvent) -> List[str]:
        """Detecta anomalias no evento"""
        anomalies = []
        details = event.details
        
        # Detectar tentativas de força bruta
        if details.get('failed_attempts', 0) > 5:
            anomalies.append('brute_force_attempt')
        
        # Detectar IP suspeito
        if details.get('suspicious_ip', False):
            anomalies.append('suspicious_ip_address')
        
        # Detectar horário incomum
        if details.get('unusual_time', False):
            anomalies.append('unusual_access_time')
        
        # Detectar User-Agent suspeito
        if details.get('suspicious_user_agent', False):
            anomalies.append('suspicious_user_agent')
        
        return anomalies
    
    def _should_alert(self, event: SecurityEvent) -> bool:
        """Determina se deve gerar alerta"""
        return event.risk_score >= self.alert_threshold
    
    def _get_client_info(self) -> Dict[str, str]:
        """Obtém informações do cliente"""
        return {
            'ip_address': request.headers.get('X-Forwarded-For', request.remote_addr),
            'user_agent': request.headers.get('User-Agent', ''),
            'referer': request.headers.get('Referer', ''),
            'origin': request.headers.get('Origin', '')
        }
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Verifica se IP é suspeito"""
        # Lista de IPs suspeitos (exemplo)
        suspicious_ips = os.getenv('SUSPICIOUS_IPS', '').split(',')
        return ip in suspicious_ips
    
    def _is_unusual_time(self) -> bool:
        """Verifica se é horário incomum"""
        current_hour = datetime.now().hour
        # Horário incomum: entre 23h e 6h
        return current_hour >= 23 or current_hour <= 6
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Verifica se User-Agent é suspeito"""
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper',
            'curl', 'wget', 'python-requests',
            'sqlmap', 'nikto', 'nmap'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(pattern in user_agent_lower for pattern in suspicious_patterns)
    
    def log_event(self, event_type: SecurityEventType, user_id: Optional[str] = None,
                  username: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                  security_level: SecurityLevel = SecurityLevel.INFO) -> SecurityEvent:
        """Registra evento de segurança"""
        
        client_info = self._get_client_info()
        
        # Detectar anomalias
        detected_anomalies = []
        if details is None:
            details = {}
        
        # Verificar IP suspeito
        if self._is_suspicious_ip(client_info['ip_address']):
            details['suspicious_ip'] = True
            detected_anomalies.append('suspicious_ip')
        
        # Verificar horário incomum
        if self._is_unusual_time():
            details['unusual_time'] = True
            detected_anomalies.append('unusual_time')
        
        # Verificar User-Agent suspeito
        if self._is_suspicious_user_agent(client_info['user_agent']):
            details['suspicious_user_agent'] = True
            detected_anomalies.append('suspicious_user_agent')
        
        # Criar evento
        event = SecurityEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id,
            username=username,
            ip_address=client_info['ip_address'],
            user_agent=client_info['user_agent'],
            session_id=g.get('session_id'),
            details=details,
            security_level=security_level,
            risk_score=0,  # Será calculado
            correlation_id=g.get('correlation_id')
        )
        
        # Calcular score de risco
        event.risk_score = self._calculate_risk_score(event)
        
        # Detectar anomalias adicionais
        event_anomalies = self._detect_anomalies(event)
        detected_anomalies.extend(event_anomalies)
        
        if detected_anomalies:
            event.details['anomalies'] = detected_anomalies
            event.security_level = SecurityLevel.WARNING
        
        # Verificar se deve gerar alerta
        if self._should_alert(event):
            event.security_level = SecurityLevel.ALERT
            self._send_alert(event)
        
        # Log estruturado
        with self._lock:
            log_entry = asdict(event)
            log_entry['event_type'] = event.event_type.value
            log_entry['security_level'] = event.security_level.value
            
            self.logger.info(json.dumps(log_entry, ensure_ascii=False))
        
        return event
    
    def _send_alert(self, event: SecurityEvent):
        """Envia alerta de segurança"""
        alert_data = {
            'timestamp': event.timestamp,
            'event_type': event.event_type.value,
            'risk_score': event.risk_score,
            'ip_address': event.ip_address,
            'username': event.username,
            'details': event.details,
            'correlation_id': event.correlation_id
        }
        
        # Log de alerta separado
        alert_logger = logging.getLogger('security_alerts')
        alert_logger.warning(json.dumps(alert_data, ensure_ascii=False))
        
        # TODO: Integrar com sistema de notificação (email, Slack, etc.)
        print(f"🚨 ALERTA DE SEGURANÇA: {event.event_type.value} - Score: {event.risk_score}")

# Instância global
security_logger = SecurityAuditLogger()

# Decorators para facilitar uso
def log_security_event(event_type: SecurityEventType, security_level: SecurityLevel = SecurityLevel.INFO):
    """Decorator para logar eventos de segurança"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Extrair informações do request
                user_id = g.get('user_id')
                username = g.get('username')
                details = {
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'status_code': 200
                }
                
                security_logger.log_event(
                    event_type=event_type,
                    user_id=user_id,
                    username=username,
                    details=details,
                    security_level=security_level
                )
                
                return result
            except Exception as e:
                # Log de erro
                details = {
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'error': str(e),
                    'status_code': 500
                }
                
                security_logger.log_event(
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    details=details,
                    security_level=SecurityLevel.WARNING
                )
                raise
        return wrapper
    return decorator 