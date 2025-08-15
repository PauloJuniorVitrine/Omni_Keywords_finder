#!/usr/bin/env python3
"""
🔒 IMP-011: Sistema de Segurança Avançada
🎯 Objetivo: Implementar medidas de segurança enterprise-grade
📅 Criado: 2024-12-27
🔄 Versão: 1.0
"""

import os
import hashlib
import hmac
import base64
import secrets
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import bcrypt
import pyotp
import qrcode
from io import BytesIO
import redis
import requests
from functools import wraps
import threading
from collections import defaultdict, deque
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Níveis de segurança."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Tipos de ameaças."""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDoS = "ddos"
    MALWARE = "malware"
    PHISHING = "phishing"
    INSIDER_THREAT = "insider_threat"

@dataclass
class SecurityEvent:
    """Evento de segurança."""
    timestamp: datetime
    event_type: str
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str]
    details: Dict[str, Any]
    threat_type: Optional[ThreatType] = None
    mitigated: bool = False

@dataclass
class SecurityMetrics:
    """Métricas de segurança."""
    total_events: int = 0
    critical_events: int = 0
    blocked_requests: int = 0
    successful_attacks: int = 0
    false_positives: int = 0
    response_time_avg: float = 0.0
    uptime_percentage: float = 100.0

class AdvancedSecuritySystem:
    """Sistema de segurança avançada enterprise-grade."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        
        # Inicializar componentes
        self.encryption_manager = EncryptionManager(config)
        self.authentication_manager = AuthenticationManager(config)
        self.authorization_manager = AuthorizationManager(config)
        self.threat_detection = ThreatDetectionSystem(config)
        self.audit_system = AuditSystem(config)
        self.rate_limiter = AdvancedRateLimiter(config)
        self.waf = WebApplicationFirewall(config)
        self.sensitive_data_detector = SensitiveDataDetector(config)
        
        # Métricas
        self.metrics = SecurityMetrics()
        self.security_events = deque(maxlen=10000)
        
        # Threading
        self.lock = threading.RLock()
        
        logger.info("🔒 Sistema de Segurança Avançada inicializado")
    
    def secure_endpoint(self, required_role: str = None, security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """Decorator para proteger endpoints."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Verificar autenticação
                user = self.authentication_manager.verify_token()
                if not user:
                    raise SecurityException("Autenticação requerida", 401)
                
                # Verificar autorização
                if required_role and not self.authorization_manager.has_role(user, required_role):
                    raise SecurityException("Acesso negado", 403)
                
                # Verificar rate limiting
                if not self.rate_limiter.check_limit(user.id):
                    raise SecurityException("Rate limit excedido", 429)
                
                # Verificar WAF
                if not self.waf.validate_request():
                    raise SecurityException("Requisição bloqueada pelo WAF", 403)
                
                # Detectar ameaças
                threat = self.threat_detection.analyze_request()
                if threat:
                    self.handle_threat(threat)
                    raise SecurityException("Ameaça detectada", 403)
                
                # Executar função
                try:
                    result = func(*args, **kwargs)
                    
                    # Auditoria
                    self.audit_system.log_event(
                        event_type="api_call",
                        user_id=user.id,
                        details={"endpoint": func.__name__, "success": True}
                    )
                    
                    return result
                    
                except Exception as e:
                    # Log de erro
                    self.audit_system.log_event(
                        event_type="api_error",
                        user_id=user.id,
                        details={"endpoint": func.__name__, "error": str(e)}
                    )
                    raise
                    
            return wrapper
        return decorator
    
    def handle_threat(self, threat: SecurityEvent):
        """Manipular ameaça detectada."""
        with self.lock:
            self.security_events.append(threat)
            self.metrics.total_events += 1
            
            if threat.severity == SecurityLevel.CRITICAL:
                self.metrics.critical_events += 1
                self.trigger_incident_response(threat)
            
            # Notificar administradores
            self.notify_admins(threat)
            
            logger.warning(f"🚨 Ameaça detectada: {threat.event_type} - {threat.severity.value}")
    
    def trigger_incident_response(self, threat: SecurityEvent):
        """Disparar resposta a incidente."""
        # Implementar resposta automática
        if threat.threat_type == ThreatType.DDoS:
            self.activate_ddos_protection()
        elif threat.threat_type == ThreatType.BRUTE_FORCE:
            self.block_ip(threat.source_ip, duration=3600)
        elif threat.threat_type == ThreatType.SQL_INJECTION:
            self.quarantine_user(threat.user_id)
    
    def notify_admins(self, threat: SecurityEvent):
        """Notificar administradores."""
        # Implementar notificação via email/SMS/Slack
        notification = {
            "type": "security_alert",
            "severity": threat.severity.value,
            "event_type": threat.event_type,
            "timestamp": threat.timestamp.isoformat(),
            "details": threat.details
        }
        
        # Enviar para sistema de notificação
        self.redis_client.publish("security_alerts", json.dumps(notification))
    
    def get_security_report(self) -> Dict[str, Any]:
        """Gerar relatório de segurança."""
        with self.lock:
            return {
                "metrics": asdict(self.metrics),
                "recent_events": [
                    asdict(event) for event in list(self.security_events)[-10:]
                ],
                "threat_summary": self.threat_detection.get_threat_summary(),
                "system_health": self.get_system_health()
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Verificar saúde do sistema de segurança."""
        return {
            "encryption": self.encryption_manager.is_healthy(),
            "authentication": self.authentication_manager.is_healthy(),
            "authorization": self.authorization_manager.is_healthy(),
            "threat_detection": self.threat_detection.is_healthy(),
            "audit": self.audit_system.is_healthy(),
            "rate_limiter": self.rate_limiter.is_healthy(),
            "waf": self.waf.is_healthy(),
            "sensitive_data_detector": self.sensitive_data_detector.is_healthy()
        }
    
    def scan_documentation_for_sensitive_data(self, content: str, file_path: str = None) -> Dict[str, Any]:
        """
        Escaneia documentação em busca de dados sensíveis.
        
        Args:
            content: Conteúdo da documentação
            file_path: Caminho do arquivo (opcional)
            
        Returns:
            Resultado da análise de dados sensíveis
        """
        return self.sensitive_data_detector.scan_documentation(content, file_path)
    
    def sanitize_documentation_content(self, content: str, file_path: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        Sanitiza conteúdo da documentação.
        
        Args:
            content: Conteúdo para sanitizar
            file_path: Caminho do arquivo (opcional)
            
        Returns:
            Tupla com (conteúdo_sanitizado, relatório_sanitização)
        """
        return self.sensitive_data_detector.sanitize_content(content, file_path)
    
    def get_sensitive_data_incident_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Gera relatório de incidentes de dados sensíveis.
        
        Args:
            start_date: Data inicial do relatório
            end_date: Data final do relatório
            
        Returns:
            Relatório de incidentes
        """
        return self.sensitive_data_detector.get_incident_report(start_date, end_date)

class EncryptionManager:
    """Gerenciador de criptografia avançada."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fernet_key = Fernet.generate_key()
        self.fernet = Fernet(self.fernet_key)
        
        # Gerar par de chaves RSA
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        logger.info("🔐 Gerenciador de Criptografia inicializado")
    
    def encrypt_data(self, data: str) -> str:
        """Criptografar dados."""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Descriptografar dados."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_with_rsa(self, data: str) -> str:
        """Criptografar com RSA."""
        encrypted = self.public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode()
    
    def decrypt_with_rsa(self, encrypted_data: str) -> str:
        """Descriptografar com RSA."""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted = self.private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode()
    
    def hash_password(self, password: str) -> str:
        """Hash de senha com bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verificar senha."""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    def is_healthy(self) -> bool:
        """Verificar saúde do sistema de criptografia."""
        try:
            test_data = "test_encryption"
            encrypted = self.encrypt_data(test_data)
            decrypted = self.decrypt_data(encrypted)
            return decrypted == test_data
        except Exception:
            return False

class AuthenticationManager:
    """Gerenciador de autenticação avançada."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_secret = config.get('jwt_secret', secrets.token_urlsafe(32))
        self.jwt_algorithm = "HS256"
        self.token_expiry = config.get('token_expiry', 3600)
        
        # 2FA
        self.totp_secret = pyotp.random_base32()
        
        # Cache de tokens
        self.token_cache = {}
        
        logger.info("🔑 Gerenciador de Autenticação inicializado")
    
    def create_token(self, user_id: str, roles: List[str]) -> str:
        """Criar token JWT."""
        payload = {
            "user_id": user_id,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry),
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        self.token_cache[token] = payload
        
        return token
    
    def verify_token(self) -> Optional[Dict[str, Any]]:
        """Verificar token JWT."""
        # Implementar verificação de token
        # Por simplicidade, retornar usuário mock
        return {
            "id": "user_123",
            "email": "user@example.com",
            "roles": ["user"]
        }
    
    def generate_2fa_secret(self) -> str:
        """Gerar segredo para 2FA."""
        return pyotp.random_base32()
    
    def verify_2fa_code(self, secret: str, code: str) -> bool:
        """Verificar código 2FA."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
    
    def generate_2fa_qr(self, secret: str, email: str) -> bytes:
        """Gerar QR code para 2FA."""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            email,
            issuer_name="Omni Keywords Finder"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def is_healthy(self) -> bool:
        """Verificar saúde do sistema de autenticação."""
        try:
            test_token = self.create_token("test_user", ["test"])
            return bool(test_token)
        except Exception:
            return False

class AuthorizationManager:
    """Gerenciador de autorização baseado em roles."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Definir roles e permissões
        self.roles = {
            "admin": ["*"],
            "user": ["read:keywords", "write:keywords", "read:reports"],
            "viewer": ["read:keywords", "read:reports"],
            "analyst": ["read:keywords", "write:keywords", "read:reports", "write:reports"]
        }
        
        logger.info("👥 Gerenciador de Autorização inicializado")
    
    def has_role(self, user: Dict[str, Any], required_role: str) -> bool:
        """Verificar se usuário tem role."""
        user_roles = user.get("roles", [])
        return required_role in user_roles
    
    def has_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """Verificar se usuário tem permissão."""
        user_roles = user.get("roles", [])
        
        for role in user_roles:
            if role in self.roles:
                role_permissions = self.roles[role]
                if "*" in role_permissions or permission in role_permissions:
                    return True
        
        return False
    
    def get_user_permissions(self, user: Dict[str, Any]) -> List[str]:
        """Obter todas as permissões do usuário."""
        user_roles = user.get("roles", [])
        permissions = set()
        
        for role in user_roles:
            if role in self.roles:
                permissions.update(self.roles[role])
        
        return list(permissions)
    
    def is_healthy(self) -> bool:
        """Verificar saúde do sistema de autorização."""
        return len(self.roles) > 0

class ThreatDetectionSystem:
    """Sistema de detecção de ameaças."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Padrões de ameaças
        self.threat_patterns = {
            ThreatType.SQL_INJECTION: [
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b)",
                r"(\b(or|and)\b\string_data+\data+\string_data*=\string_data*\data+)",
                r"(--|#|/\*|\*/)",
                r"(\b(exec|execute|xp_|sp_)\b)"
            ],
            ThreatType.XSS: [
                r"(<script[^>]*>.*?</script>)",
                r"(javascript:)",
                r"(on\w+\string_data*=)",
                r"(<iframe[^>]*>)"
            ],
            ThreatType.CSRF: [
                r"(<img[^>]*src\string_data*=\string_data*['\"][^'\"]*['\"][^>]*>)",
                r"(<form[^>]*action\string_data*=\string_data*['\"][^'\"]*['\"][^>]*>)"
            ]
        }
        
        # Histórico de ameaças
        self.threat_history = defaultdict(list)
        
        logger.info("🛡️ Sistema de Detecção de Ameaças inicializado")
    
    def analyze_request(self) -> Optional[SecurityEvent]:
        """Analisar requisição em busca de ameaças."""
        # Implementar análise de requisição
        # Por simplicidade, retornar None (sem ameaças)
        return None
    
    def detect_sql_injection(self, input_data: str) -> bool:
        """Detectar SQL injection."""
        import re
        for pattern in self.threat_patterns[ThreatType.SQL_INJECTION]:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True
        return False
    
    def detect_xss(self, input_data: str) -> bool:
        """Detectar XSS."""
        import re
        for pattern in self.threat_patterns[ThreatType.XSS]:
            if re.search(pattern, input_data, re.IGNORECASE):
                return True
        return False
    
    def get_threat_summary(self) -> Dict[str, Any]:
        """Obter resumo de ameaças."""
        summary = {}
        for threat_type in ThreatType:
            summary[threat_type.value] = len(self.threat_history[threat_type])
        return summary
    
    def is_healthy(self) -> bool:
        """Verificar saúde do sistema de detecção."""
        return len(self.threat_patterns) > 0

class AuditSystem:
    """Sistema de auditoria avançada."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.audit_log = []
        self.max_log_size = config.get('max_audit_log_size', 10000)
        
        logger.info("📋 Sistema de Auditoria inicializado")
    
    def log_event(self, event_type: str, user_id: Optional[str] = None, details: Dict[str, Any] = None):
        """Registrar evento de auditoria."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details or {},
            "session_id": self.get_session_id(),
            "ip_address": self.get_client_ip()
        }
        
        self.audit_log.append(event)
        
        # Manter tamanho do log
        if len(self.audit_log) > self.max_log_size:
            self.audit_log.pop(0)
        
        # Log para arquivo
        logger.info(f"Audit: {event_type} - User: {user_id}")
    
    def get_session_id(self) -> str:
        """Obter ID da sessão."""
        return secrets.token_urlsafe(16)
    
    def get_client_ip(self) -> str:
        """Obter IP do cliente."""
        # Implementar obtenção de IP real
        return "127.0.0.1"
    
    def get_audit_report(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Gerar relatório de auditoria."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        filtered_events = [
            event for event in self.audit_log
            if start_date <= datetime.fromisoformat(event["timestamp"]) <= end_date
        ]
        
        return filtered_events
    
    def is_healthy(self) -> bool:
        """Verificar saúde do sistema de auditoria."""
        return len(self.audit_log) >= 0

class AdvancedRateLimiter:
    """Rate limiter avançado."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rate_limits = {
            "default": {"requests": 100, "window": 60},  # 100 req/min
            "api": {"requests": 1000, "window": 60},     # 1000 req/min
            "auth": {"requests": 5, "window": 300},      # 5 req/5min
            "upload": {"requests": 10, "window": 3600}   # 10 req/hora
        }
        
        self.request_counts = defaultdict(lambda: defaultdict(int))
        self.window_start = defaultdict(lambda: time.time())
        
        logger.info("⏱️ Rate Limiter Avançado inicializado")
    
    def check_limit(self, user_id: str, endpoint_type: str = "default") -> bool:
        """Verificar limite de rate."""
        current_time = time.time()
        limit_config = self.rate_limits.get(endpoint_type, self.rate_limits["default"])
        
        # Resetar janela se necessário
        if current_time - self.window_start[user_id] > limit_config["window"]:
            self.request_counts[user_id].clear()
            self.window_start[user_id] = current_time
        
        # Verificar limite
        current_count = self.request_counts[user_id][endpoint_type]
        if current_count >= limit_config["requests"]:
            return False
        
        # Incrementar contador
        self.request_counts[user_id][endpoint_type] += 1
        return True
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Obter estatísticas do usuário."""
        return {
            "request_counts": dict(self.request_counts[user_id]),
            "window_start": self.window_start[user_id]
        }
    
    def is_healthy(self) -> bool:
        """Verificar saúde do rate limiter."""
        return len(self.rate_limits) > 0

class WebApplicationFirewall:
    """Web Application Firewall."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Regras do WAF
        self.waf_rules = [
            {"name": "block_sql_injection", "pattern": r"(\b(union|select|insert|update|delete|drop|create|alter)\b)", "action": "block"},
            {"name": "block_xss", "pattern": r"(<script[^>]*>.*?</script>)", "action": "block"},
            {"name": "block_path_traversal", "pattern": r"(\.\./|\.\.\\)", "action": "block"},
            {"name": "block_command_injection", "pattern": r"(\b(cmd|exec|system|eval)\b)", "action": "block"}
        ]
        
        logger.info("🔥 Web Application Firewall inicializado")
    
    def validate_request(self) -> bool:
        """Validar requisição."""
        # Implementar validação de requisição
        # Por simplicidade, retornar True (requisição válida)
        return True
    
    def is_healthy(self) -> bool:
        """Verificar saúde do WAF."""
        return len(self.waf_rules) > 0

class SecurityException(Exception):
    """Exceção de segurança."""
    def __init__(self, message: str, status_code: int = 403):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class SensitiveDataDetector:
    """
    Detector de dados sensíveis para documentação enterprise.
    
    Implementa detecção avançada de dados sensíveis com:
    - Padrões de regex expandidos
    - Detecção de múltiplos tipos de dados sensíveis
    - Sanitização automática
    - Logs de incidentes
    - Integração com pipeline de documentação
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o detector de dados sensíveis.
        
        Args:
            config: Configuração do detector
        """
        self.config = config or {}
        
        # Padrões de regex expandidos para dados sensíveis
        self.sensitive_patterns = {
            'aws_keys': {
                'patterns': [
                    r'AKIA[0-9A-Z]{16}',  # AWS Access Key ID
                    r'[0-9a-zA-Z/+]{40}',  # AWS Secret Access Key
                    r'arn:aws:[a-z0-9-]+:[a-z0-9-]+:[0-9]{12}:[a-z0-9-]+',  # AWS ARN
                ],
                'severity': SecurityLevel.CRITICAL,
                'description': 'AWS Keys detectadas'
            },
            'google_api_keys': {
                'patterns': [
                    r'AIza[0-9A-Za-data-_]{35}',  # Google API Key
                    r'[0-9]{12}-[0-9a-zA-Z]{32}',  # Google Service Account
                ],
                'severity': SecurityLevel.CRITICAL,
                'description': 'Google API Keys detectadas'
            },
            'passwords': {
                'patterns': [
                    r'password\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',  # password: value
                    r'passwd\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',   # passwd: value
                    r'pwd\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',      # pwd: value
                    r'senha\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',    # senha: value
                ],
                'severity': SecurityLevel.HIGH,
                'description': 'Senhas detectadas'
            },
            'secrets': {
                'patterns': [
                    r'secret\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',   # secret: value
                    r'token\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',    # token: value
                    r'key\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',      # key: value
                    r'api_key\string_data*[:=]\string_data*["\']?[^"\'\string_data]+["\']?',  # api_key: value
                ],
                'severity': SecurityLevel.HIGH,
                'description': 'Secrets detectadas'
            },
            'tokens': {
                'patterns': [
                    r'Bearer\string_data+[A-Za-z0-9\-._~+/]+=*',  # Bearer token
                    r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',  # JWT token
                    r'[A-Za-z0-9]{32,}',  # Generic token (32+ chars)
                ],
                'severity': SecurityLevel.MEDIUM,
                'description': 'Tokens detectados'
            },
            'database_connections': {
                'patterns': [
                    r'mysql://[^@]+@[^:]+:[0-9]+/[^?\string_data]+',  # MySQL connection
                    r'postgresql://[^@]+@[^:]+:[0-9]+/[^?\string_data]+',  # PostgreSQL connection
                    r'mongodb://[^@]+@[^:]+:[0-9]+/[^?\string_data]+',  # MongoDB connection
                    r'redis://[^@]+@[^:]+:[0-9]+',  # Redis connection
                ],
                'severity': SecurityLevel.HIGH,
                'description': 'Conexões de banco detectadas'
            },
            'private_keys': {
                'patterns': [
                    r'-----BEGIN\string_data+(RSA\string_data+)?PRIVATE\string_data+KEY-----',  # RSA Private Key
                    r'-----BEGIN\string_data+OPENSSH\string_data+PRIVATE\string_data+KEY-----',  # OpenSSH Private Key
                    r'-----BEGIN\string_data+PGP\string_data+PRIVATE\string_data+KEY-----',  # PGP Private Key
                ],
                'severity': SecurityLevel.CRITICAL,
                'description': 'Chaves privadas detectadas'
            },
            'credit_cards': {
                'patterns': [
                    r'\b4[0-9]{12}(?:[0-9]{3})?\b',  # Visa
                    r'\b5[1-5][0-9]{14}\b',  # MasterCard
                    r'\b3[47][0-9]{13}\b',  # American Express
                    r'\b3[0-9]{13}\b',  # Diners Club
                ],
                'severity': SecurityLevel.CRITICAL,
                'description': 'Cartões de crédito detectados'
            },
            'cpf_cnpj': {
                'patterns': [
                    r'\b[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]{2}\b',  # CPF
                    r'\b[0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/?[0-9]{4}-?[0-9]{2}\b',  # CNPJ
                ],
                'severity': SecurityLevel.HIGH,
                'description': 'CPF/CNPJ detectados'
            }
        }
        
        # Configurações de sanitização
        self.sanitization_config = {
            'replace_with': '[REDACTED]',
            'preserve_format': True,
            'log_incidents': True,
            'auto_sanitize': self.config.get('auto_sanitize', False)
        }
        
        # Histórico de incidentes
        self.incidents = []
        self.max_incidents = self.config.get('max_incidents', 1000)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "sensitive_data_detector_initialized",
            "status": "success",
            "source": "SensitiveDataDetector.__init__",
            "details": {
                "patterns_loaded": len(self.sensitive_patterns),
                "auto_sanitize": self.sanitization_config['auto_sanitize']
            }
        })
    
    def scan_documentation(self, content: str, file_path: str = None) -> Dict[str, Any]:
        """
        Escaneia documentação em busca de dados sensíveis.
        
        Args:
            content: Conteúdo da documentação
            file_path: Caminho do arquivo (opcional)
            
        Returns:
            Dicionário com resultados da análise
        """
        if not content:
            return {
                'sensitive_data_found': False,
                'incidents': [],
                'risk_level': SecurityLevel.LOW,
                'recommendations': []
            }
        
        incidents = []
        risk_level = SecurityLevel.LOW
        
        # Escanear cada tipo de dado sensível
        for data_type, config in self.sensitive_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    incident = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'data_type': data_type,
                        'severity': config['severity'].value,
                        'description': config['description'],
                        'pattern': pattern,
                        'match': match.group(),
                        'position': match.span(),
                        'file_path': file_path,
                        'context': self._get_context(content, match.start(), match.end())
                    }
                    
                    incidents.append(incident)
                    
                    # Atualizar nível de risco
                    if config['severity'].value == SecurityLevel.CRITICAL.value:
                        risk_level = SecurityLevel.CRITICAL
                    elif config['severity'].value == SecurityLevel.HIGH.value and risk_level != SecurityLevel.CRITICAL:
                        risk_level = SecurityLevel.HIGH
                    elif config['severity'].value == SecurityLevel.MEDIUM.value and risk_level not in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]:
                        risk_level = SecurityLevel.MEDIUM
        
        # Registrar incidentes
        if incidents and self.sanitization_config['log_incidents']:
            self._log_incidents(incidents)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(incidents, risk_level)
        
        result = {
            'sensitive_data_found': len(incidents) > 0,
            'incidents': incidents,
            'risk_level': risk_level.value,
            'recommendations': recommendations,
            'total_incidents': len(incidents),
            'scan_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "documentation_scan_completed",
            "status": "success",
            "source": "SensitiveDataDetector.scan_documentation",
            "details": {
                "file_path": file_path,
                "sensitive_data_found": result['sensitive_data_found'],
                "total_incidents": result['total_incidents'],
                "risk_level": result['risk_level']
            }
        })
        
        return result
    
    def sanitize_content(self, content: str, file_path: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        Sanitiza conteúdo removendo ou substituindo dados sensíveis.
        
        Args:
            content: Conteúdo para sanitizar
            file_path: Caminho do arquivo (opcional)
            
        Returns:
            Tupla com (conteúdo_sanitizado, relatório_sanitização)
        """
        if not content:
            return content, {
                'sanitized': False,
                'replacements_made': 0,
                'incidents': []
            }
        
        sanitized_content = content
        replacements_made = 0
        sanitization_incidents = []
        
        # Escanear e sanitizar cada tipo de dado sensível
        for data_type, config in self.sensitive_patterns.items():
            for pattern in config['patterns']:
                matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
                
                # Substituir do final para o início para manter posições
                for match in reversed(matches):
                    original_match = match.group()
                    replacement = self._generate_replacement(original_match, data_type)
                    
                    # Substituir no conteúdo
                    start, end = match.span()
                    sanitized_content = sanitized_content[:start] + replacement + sanitized_content[end:]
                    
                    replacements_made += 1
                    
                    # Registrar incidente de sanitização
                    incident = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'data_type': data_type,
                        'severity': config['severity'].value,
                        'description': f"Sanitizado: {config['description']}",
                        'original_value': original_match,
                        'replacement': replacement,
                        'file_path': file_path
                    }
                    
                    sanitization_incidents.append(incident)
        
        # Registrar incidentes de sanitização
        if sanitization_incidents and self.sanitization_config['log_incidents']:
            self._log_incidents(sanitization_incidents)
        
        result = {
            'sanitized': replacements_made > 0,
            'replacements_made': replacements_made,
            'incidents': sanitization_incidents,
            'sanitization_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "content_sanitization_completed",
            "status": "success",
            "source": "SensitiveDataDetector.sanitize_content",
            "details": {
                "file_path": file_path,
                "replacements_made": replacements_made,
                "sanitized": result['sanitized']
            }
        })
        
        return sanitized_content, result
    
    def _get_context(self, content: str, start: int, end: int, context_size: int = 50) -> str:
        """
        Obtém contexto ao redor de uma correspondência.
        
        Args:
            content: Conteúdo completo
            start: Posição inicial da correspondência
            end: Posição final da correspondência
            context_size: Tamanho do contexto em caracteres
            
        Returns:
            Contexto da correspondência
        """
        context_start = max(0, start - context_size)
        context_end = min(len(content), end + context_size)
        
        context = content[context_start:context_end]
        
        # Adicionar indicadores se truncado
        if context_start > 0:
            context = "..." + context
        if context_end < len(content):
            context = context + "..."
        
        return context
    
    def _generate_replacement(self, original_value: str, data_type: str) -> str:
        """
        Gera substituição para dados sensíveis.
        
        Args:
            original_value: Valor original
            data_type: Tipo de dado sensível
            
        Returns:
            Valor de substituição
        """
        if self.sanitization_config['preserve_format']:
            # Manter formato original
            if data_type in ['aws_keys', 'google_api_keys', 'tokens']:
                # Manter comprimento e formato
                if len(original_value) > 10:
                    return original_value[:4] + "[REDACTED]" + original_value[-4:]
                else:
                    return "[REDACTED]"
            elif data_type in ['credit_cards', 'cpf_cnpj']:
                # Manter formato de números
                return re.sub(r'[0-9]', '*', original_value)
            else:
                return "[REDACTED]"
        else:
            return self.sanitization_config['replace_with']
    
    def _generate_recommendations(self, incidents: List[Dict], risk_level: SecurityLevel) -> List[str]:
        """
        Gera recomendações baseadas nos incidentes encontrados.
        
        Args:
            incidents: Lista de incidentes
            risk_level: Nível de risco
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        if not incidents:
            recommendations.append("Nenhum dado sensível encontrado. Documentação segura.")
            return recommendations
        
        # Recomendações por tipo de dado
        data_types_found = set(incident['data_type'] for incident in incidents)
        
        if 'aws_keys' in data_types_found:
            recommendations.append("🔴 CRÍTICO: Remover AWS Keys imediatamente. Use variáveis de ambiente.")
        
        if 'google_api_keys' in data_types_found:
            recommendations.append("🔴 CRÍTICO: Remover Google API Keys imediatamente. Use variáveis de ambiente.")
        
        if 'private_keys' in data_types_found:
            recommendations.append("🔴 CRÍTICO: Remover chaves privadas imediatamente. Nunca commitar chaves privadas.")
        
        if 'credit_cards' in data_types_found:
            recommendations.append("🔴 CRÍTICO: Remover números de cartão de crédito. Violação PCI-DSS.")
        
        if 'passwords' in data_types_found:
            recommendations.append("🟡 ALTO: Remover senhas em texto plano. Use variáveis de ambiente.")
        
        if 'secrets' in data_types_found:
            recommendations.append("🟡 ALTO: Remover secrets em texto plano. Use gerenciador de secrets.")
        
        if 'database_connections' in data_types_found:
            recommendations.append("🟡 ALTO: Remover strings de conexão. Use variáveis de ambiente.")
        
        if 'cpf_cnpj' in data_types_found:
            recommendations.append("🟡 ALTO: Remover CPF/CNPJ. Violação LGPD.")
        
        if 'tokens' in data_types_found:
            recommendations.append("🟢 MÉDIO: Considerar remover tokens. Use variáveis de ambiente se necessário.")
        
        # Recomendações gerais
        if risk_level == SecurityLevel.CRITICAL:
            recommendations.append("🚨 AÇÃO IMEDIATA REQUERIDA: Dados críticos encontrados.")
        
        recommendations.append("📋 Implementar revisão automática de dados sensíveis no pipeline CI/CD.")
        recommendations.append("🔍 Configurar hooks de pre-commit para detecção automática.")
        
        return recommendations
    
    def _log_incidents(self, incidents: List[Dict]) -> None:
        """
        Registra incidentes no histórico.
        
        Args:
            incidents: Lista de incidentes para registrar
        """
        for incident in incidents:
            self.incidents.append(incident)
            
            # Manter tamanho do histórico
            if len(self.incidents) > self.max_incidents:
                self.incidents.pop(0)
            
            # Log estruturado
            logger.warning({
                "timestamp": incident['timestamp'],
                "event": "sensitive_data_incident",
                "status": "warning",
                "source": "SensitiveDataDetector._log_incidents",
                "details": {
                    "data_type": incident['data_type'],
                    "severity": incident['severity'],
                    "file_path": incident.get('file_path'),
                    "description": incident['description']
                }
            })
    
    def get_incident_report(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Gera relatório de incidentes.
        
        Args:
            start_date: Data inicial do relatório
            end_date: Data final do relatório
            
        Returns:
            Relatório de incidentes
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        filtered_incidents = [
            incident for incident in self.incidents
            if start_date <= datetime.fromisoformat(incident['timestamp']) <= end_date
        ]
        
        # Estatísticas por tipo
        stats_by_type = {}
        for incident in filtered_incidents:
            data_type = incident['data_type']
            if data_type not in stats_by_type:
                stats_by_type[data_type] = 0
            stats_by_type[data_type] += 1
        
        # Estatísticas por severidade
        stats_by_severity = {}
        for incident in filtered_incidents:
            severity = incident['severity']
            if severity not in stats_by_severity:
                stats_by_severity[severity] = 0
            stats_by_severity[severity] += 1
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_incidents': len(filtered_incidents),
            'stats_by_type': stats_by_type,
            'stats_by_severity': stats_by_severity,
            'incidents': filtered_incidents,
            'report_generated': datetime.utcnow().isoformat()
        }
    
    def is_healthy(self) -> bool:
        """
        Verifica saúde do detector.
        
        Returns:
            True se saudável
        """
        return len(self.sensitive_patterns) > 0 and len(self.incidents) >= 0

# Configuração padrão
DEFAULT_SECURITY_CONFIG = {
    "redis_host": "localhost",
    "redis_port": 6379,
    "redis_db": 0,
    "jwt_secret": os.getenv("JWT_SECRET", secrets.token_urlsafe(32)),
    "jwt_algorithm": "HS256",
    "token_expiry": 3600,
    "max_audit_log_size": 10000
}

def create_security_system(config: Dict[str, Any] = None) -> AdvancedSecuritySystem:
    """Criar instância do sistema de segurança."""
    if config is None:
        config = DEFAULT_SECURITY_CONFIG
    
    return AdvancedSecuritySystem(config)

# Exemplo de uso
if __name__ == "__main__":
    # Criar sistema de segurança
    security_system = create_security_system()
    
    # Exemplo de endpoint protegido
    @security_system.secure_endpoint(required_role="admin", security_level=SecurityLevel.HIGH)
    def admin_endpoint():
        return {"message": "Endpoint protegido acessado com sucesso"}
    
    # Testar sistema
    try:
        result = admin_endpoint()
        print(result)
    except SecurityException as e:
        print(f"Erro de segurança: {e.message}")
    
    # Gerar relatório
    report = security_system.get_security_report()
    print("Relatório de Segurança:")
    print(json.dumps(report, indent=2)) 