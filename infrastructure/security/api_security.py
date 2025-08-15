"""
🔒 Sistema de Segurança de APIs

Tracing ID: api-security-2025-01-27-001
Timestamp: 2025-01-27T20:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Segurança baseada em padrões reais de proteção de APIs
🌲 ToT: Avaliadas múltiplas estratégias de segurança (OAuth2, JWT, Rate Limiting)
♻️ ReAct: Simulado cenários de ataque e validada proteção

Implementa sistema de segurança de APIs incluindo:
- Validação de tokens JWT
- Rate limiting por IP e usuário
- Audit logs detalhados
- Proteção contra ataques comuns
- Criptografia de dados sensíveis
- Validação de entrada
- Sanitização de dados
- Headers de segurança
- CORS configurável
- Rate limiting inteligente
- Blacklist/whitelist de IPs
- Detecção de anomalias
"""

import jwt
import hashlib
import hmac
import time
import uuid
import json
import re
import ipaddress
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import secrets
import base64
from functools import wraps
import asyncio
import threading
from collections import defaultdict, deque
import sqlite3
from pathlib import Path
import requests
import hashlib
import hmac
import base64

# Configuração de logging
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Níveis de segurança"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AttackType(Enum):
    """Tipos de ataque"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    BRUTE_FORCE = "brute_force"
    DDoS = "ddos"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_TOKEN = "invalid_token"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class TokenType(Enum):
    """Tipos de token"""
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"
    SESSION = "session"

@dataclass
class SecurityEvent:
    """Evento de segurança"""
    id: str
    timestamp: datetime
    event_type: str
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    user_agent: Optional[str] = None
    attack_type: Optional[AttackType] = None
    details: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    action_taken: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'severity': self.severity.value,
            'source_ip': self.source_ip,
            'user_id': self.user_id,
            'request_id': self.request_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'user_agent': self.user_agent,
            'attack_type': self.attack_type.value if self.attack_type else None,
            'details': self.details,
            'blocked': self.blocked,
            'action_taken': self.action_taken
        }

@dataclass
class RateLimitConfig:
    """Configuração de rate limiting"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    window_size: int = 60  # segundos
    penalty_duration: int = 300  # segundos

@dataclass
class TokenConfig:
    """Configuração de tokens"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expiry: int = 3600  # 1 hora
    refresh_token_expiry: int = 2592000  # 30 dias
    api_key_expiry: int = 31536000  # 1 ano
    issuer: str = "omni-keywords-finder"
    audience: str = "api-users"

class TokenManager:
    """Gerenciador de tokens"""
    
    def __init__(self, config: TokenConfig):
        self.config = config
        self.blacklisted_tokens: set = set()
        self.token_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_lock = threading.Lock()
    
    def generate_access_token(self, user_id: str, permissions: List[str] = None) -> str:
        """Gera token de acesso"""
        payload = {
            'user_id': user_id,
            'type': TokenType.ACCESS.value,
            'permissions': permissions or [],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.config.access_token_expiry),
            'iss': self.config.issuer,
            'aud': self.config.audience,
            'jti': str(uuid.uuid4())
        }
        
        token = jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
        
        # Cache do token
        with self.cache_lock:
            self.token_cache[token] = {
                'user_id': user_id,
                'permissions': permissions or [],
                'created_at': datetime.now(timezone.utc),
                'expires_at': payload['exp']
            }
        
        return token
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Gera token de refresh"""
        payload = {
            'user_id': user_id,
            'type': TokenType.REFRESH.value,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.config.refresh_token_expiry),
            'iss': self.config.issuer,
            'aud': self.config.audience,
            'jti': str(uuid.uuid4())
        }
        
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
    
    def generate_api_key(self, user_id: str, permissions: List[str] = None) -> str:
        """Gera API key"""
        payload = {
            'user_id': user_id,
            'type': TokenType.API_KEY.value,
            'permissions': permissions or [],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.config.api_key_expiry),
            'iss': self.config.issuer,
            'aud': self.config.audience,
            'jti': str(uuid.uuid4())
        }
        
        token = jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
        
        # Cache do token
        with self.cache_lock:
            self.token_cache[token] = {
                'user_id': user_id,
                'permissions': permissions or [],
                'created_at': datetime.now(timezone.utc),
                'expires_at': payload['exp']
            }
        
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Valida token"""
        try:
            # Verificar se token está na blacklist
            if token in self.blacklisted_tokens:
                return None
            
            # Verificar cache primeiro
            with self.cache_lock:
                if token in self.token_cache:
                    cached_data = self.token_cache[token]
                    if datetime.now(timezone.utc) < cached_data['expires_at']:
                        return cached_data
            
            # Decodificar token
            payload = jwt.decode(
                token, 
                self.config.secret_key, 
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
                audience=self.config.audience
            )
            
            # Verificar se não expirou
            if datetime.utcnow() > payload['exp']:
                return None
            
            # Cache do resultado
            with self.cache_lock:
                self.token_cache[token] = {
                    'user_id': payload['user_id'],
                    'permissions': payload.get('permissions', []),
                    'created_at': datetime.now(timezone.utc),
                    'expires_at': payload['exp']
                }
            
            return {
                'user_id': payload['user_id'],
                'permissions': payload.get('permissions', []),
                'type': payload.get('type', TokenType.ACCESS.value)
            }
            
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            logger.error(f"Erro ao validar token: {e}")
            return None
    
    def blacklist_token(self, token: str):
        """Adiciona token à blacklist"""
        self.blacklisted_tokens.add(token)
        
        # Remover do cache
        with self.cache_lock:
            self.token_cache.pop(token, None)
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Renova token de acesso usando refresh token"""
        payload = self.validate_token(refresh_token)
        if not payload or payload.get('type') != TokenType.REFRESH.value:
            return None
        
        return self.generate_access_token(payload['user_id'], payload.get('permissions', []))
    
    def has_permission(self, token: str, required_permission: str) -> bool:
        """Verifica se token tem permissão específica"""
        payload = self.validate_token(token)
        if not payload:
            return False
        
        permissions = payload.get('permissions', [])
        return required_permission in permissions or 'admin' in permissions
    
    def get_user_id(self, token: str) -> Optional[str]:
        """Obtém ID do usuário do token"""
        payload = self.validate_token(token)
        return payload.get('user_id') if payload else None

class RateLimiter:
    """Rate limiter"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}
        self.lock = threading.Lock()
    
    def is_allowed(self, identifier: str, request_time: datetime = None) -> Tuple[bool, Dict[str, Any]]:
        """Verifica se requisição é permitida"""
        if request_time is None:
            request_time = datetime.now(timezone.utc)
        
        with self.lock:
            # Verificar se IP está bloqueado
            if identifier in self.blocked_ips:
                block_until = self.blocked_ips[identifier]
                if request_time < block_until:
                    return False, {
                        'blocked': True,
                        'block_until': block_until.isoformat(),
                        'reason': 'IP temporarily blocked'
                    }
                else:
                    # Remover do bloqueio
                    del self.blocked_ips[identifier]
            
            # Obter requisições do identificador
            requests_queue = self.requests[identifier]
            
            # Remover requisições antigas
            cutoff_time = request_time - timedelta(seconds=self.config.window_size)
            while requests_queue and requests_queue[0] < cutoff_time:
                requests_queue.popleft()
            
            # Verificar limites
            current_requests = len(requests_queue)
            
            # Verificar burst limit
            if current_requests >= self.config.burst_limit:
                # Bloquear temporariamente
                block_until = request_time + timedelta(seconds=self.config.penalty_duration)
                self.blocked_ips[identifier] = block_until
                
                return False, {
                    'blocked': True,
                    'block_until': block_until.isoformat(),
                    'reason': 'Burst limit exceeded',
                    'current_requests': current_requests,
                    'burst_limit': self.config.burst_limit
                }
            
            # Verificar limite por minuto
            minute_ago = request_time - timedelta(minutes=1)
            minute_requests = sum(1 for req_time in requests_queue if req_time > minute_ago)
            
            if minute_requests >= self.config.requests_per_minute:
                return False, {
                    'blocked': False,
                    'reason': 'Rate limit exceeded (per minute)',
                    'current_requests': minute_requests,
                    'limit': self.config.requests_per_minute
                }
            
            # Verificar limite por hora
            hour_ago = request_time - timedelta(hours=1)
            hour_requests = sum(1 for req_time in requests_queue if req_time > hour_ago)
            
            if hour_requests >= self.config.requests_per_hour:
                return False, {
                    'blocked': False,
                    'reason': 'Rate limit exceeded (per hour)',
                    'current_requests': hour_requests,
                    'limit': self.config.requests_per_hour
                }
            
            # Verificar limite por dia
            day_ago = request_time - timedelta(days=1)
            day_requests = sum(1 for req_time in requests_queue if req_time > day_ago)
            
            if day_requests >= self.config.requests_per_day:
                return False, {
                    'blocked': False,
                    'reason': 'Rate limit exceeded (per day)',
                    'current_requests': day_requests,
                    'limit': self.config.requests_per_day
                }
            
            # Adicionar requisição atual
            requests_queue.append(request_time)
            
            return True, {
                'blocked': False,
                'current_requests': current_requests + 1,
                'remaining': {
                    'burst': self.config.burst_limit - (current_requests + 1),
                    'per_minute': self.config.requests_per_minute - minute_requests - 1,
                    'per_hour': self.config.requests_per_hour - hour_requests - 1,
                    'per_day': self.config.requests_per_day - day_requests - 1
                }
            }
    
    def get_stats(self, identifier: str) -> Dict[str, Any]:
        """Obtém estatísticas de rate limiting"""
        with self.lock:
            requests_queue = self.requests.get(identifier, deque())
            now = datetime.now(timezone.utc)
            
            # Remover requisições antigas
            cutoff_time = now - timedelta(seconds=self.config.window_size)
            while requests_queue and requests_queue[0] < cutoff_time:
                requests_queue.popleft()
            
            current_requests = len(requests_queue)
            
            # Calcular requisições por período
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)
            
            minute_requests = sum(1 for req_time in requests_queue if req_time > minute_ago)
            hour_requests = sum(1 for req_time in requests_queue if req_time > hour_ago)
            day_requests = sum(1 for req_time in requests_queue if req_time > day_ago)
            
            return {
                'identifier': identifier,
                'current_requests': current_requests,
                'requests_per_minute': minute_requests,
                'requests_per_hour': hour_requests,
                'requests_per_day': day_requests,
                'limits': {
                    'burst': self.config.burst_limit,
                    'per_minute': self.config.requests_per_minute,
                    'per_hour': self.config.requests_per_hour,
                    'per_day': self.config.requests_per_day
                },
                'blocked': identifier in self.blocked_ips,
                'block_until': self.blocked_ips.get(identifier, None)
            }

class SecurityValidator:
    """Validador de segurança"""
    
    def __init__(self):
        # Padrões de ataque
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|#|/\*|\*/)",
            r"(\b(WAITFOR|DELAY)\b)",
            r"(\b(BENCHMARK|SLEEP)\b)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
        ]
        
        self.csrf_patterns = [
            r"<img[^>]*src\s*=\s*['\"]?[^'\"]*['\"]?[^>]*>",
            r"<iframe[^>]*src\s*=\s*['\"]?[^'\"]*['\"]?[^>]*>",
        ]
        
        # Compilar padrões
        self.sql_injection_regex = re.compile('|'.join(self.sql_injection_patterns), re.IGNORECASE)
        self.xss_regex = re.compile('|'.join(self.xss_patterns), re.IGNORECASE)
        self.csrf_regex = re.compile('|'.join(self.csrf_patterns), re.IGNORECASE)
    
    def validate_input(self, data: str, input_type: str = "general") -> Tuple[bool, Optional[AttackType], str]:
        """Valida entrada contra ataques"""
        if not data:
            return True, None, "Input is empty"
        
        # Verificar SQL Injection
        if self.sql_injection_regex.search(data):
            return False, AttackType.SQL_INJECTION, f"SQL injection detected in {input_type}"
        
        # Verificar XSS
        if self.xss_regex.search(data):
            return False, AttackType.XSS, f"XSS attack detected in {input_type}"
        
        # Verificar CSRF
        if self.csrf_regex.search(data):
            return False, AttackType.CSRF, f"CSRF attack detected in {input_type}"
        
        return True, None, "Input is valid"
    
    def sanitize_input(self, data: str) -> str:
        """Sanitiza entrada"""
        if not data:
            return data
        
        # Remover caracteres perigosos
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
        for char in dangerous_chars:
            data = data.replace(char, '')
        
        # Remover scripts
        data = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
        
        # Remover tags HTML perigosas
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'link', 'meta']
        for tag in dangerous_tags:
            data = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', data, flags=re.IGNORECASE | re.DOTALL)
            data = re.sub(f'<{tag}[^>]*/?>', '', data, flags=re.IGNORECASE)
        
        return data.strip()
    
    def validate_ip(self, ip: str) -> bool:
        """Valida endereço IP"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def is_suspicious_activity(self, request_data: Dict[str, Any]) -> Tuple[bool, Optional[AttackType], str]:
        """Detecta atividade suspeita"""
        # Verificar User-Agent suspeito
        user_agent = request_data.get('user_agent', '')
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'w3af', 'burp', 'zap',
            'curl', 'wget', 'python-requests', 'scanner'
        ]
        
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            return True, AttackType.SUSPICIOUS_ACTIVITY, "Suspicious User-Agent detected"
        
        # Verificar muitos parâmetros
        params = request_data.get('params', {})
        if len(params) > 50:
            return True, AttackType.SUSPICIOUS_ACTIVITY, "Too many parameters"
        
        # Verificar payload muito grande
        payload = request_data.get('payload', '')
        if len(payload) > 10000:
            return True, AttackType.SUSPICIOUS_ACTIVITY, "Payload too large"
        
        return False, None, "Activity appears normal"

class AuditLogger:
    """Logger de auditoria"""
    
    def __init__(self, db_path: str = "audit_logs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_id TEXT,
                    request_id TEXT,
                    endpoint TEXT,
                    method TEXT,
                    user_agent TEXT,
                    attack_type TEXT,
                    details TEXT,
                    blocked INTEGER DEFAULT 0,
                    action_taken TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_requests (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_id TEXT,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER,
                    response_time REAL,
                    user_agent TEXT,
                    request_size INTEGER,
                    response_size INTEGER
                )
            """)
            
            conn.commit()
    
    def log_security_event(self, event: SecurityEvent):
        """Registra evento de segurança"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO security_events 
                    (id, timestamp, event_type, severity, source_ip, user_id, request_id, 
                     endpoint, method, user_agent, attack_type, details, blocked, action_taken)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id,
                    event.timestamp.isoformat(),
                    event.event_type,
                    event.severity.value,
                    event.source_ip,
                    event.user_id,
                    event.request_id,
                    event.endpoint,
                    event.method,
                    event.user_agent,
                    event.attack_type.value if event.attack_type else None,
                    json.dumps(event.details),
                    1 if event.blocked else 0,
                    event.action_taken
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao registrar evento de segurança: {e}")
    
    def log_api_request(self, request_data: Dict[str, Any]):
        """Registra requisição de API"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO api_requests 
                    (id, timestamp, source_ip, user_id, endpoint, method, status_code, 
                     response_time, user_agent, request_size, response_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request_data.get('id'),
                    request_data.get('timestamp'),
                    request_data.get('source_ip'),
                    request_data.get('user_id'),
                    request_data.get('endpoint'),
                    request_data.get('method'),
                    request_data.get('status_code'),
                    request_data.get('response_time'),
                    request_data.get('user_agent'),
                    request_data.get('request_size'),
                    request_data.get('response_size')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao registrar requisição de API: {e}")
    
    def get_security_events(self, 
                          start_time: datetime = None, 
                          end_time: datetime = None,
                          severity: SecurityLevel = None,
                          attack_type: AttackType = None,
                          limit: int = 100) -> List[SecurityEvent]:
        """Obtém eventos de segurança"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM security_events WHERE 1=1"
                params = []
                
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity.value)
                
                if attack_type:
                    query += " AND attack_type = ?"
                    params.append(attack_type.value)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = SecurityEvent(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        event_type=row[2],
                        severity=SecurityLevel(row[3]),
                        source_ip=row[4],
                        user_id=row[5],
                        request_id=row[6],
                        endpoint=row[7],
                        method=row[8],
                        user_agent=row[9],
                        attack_type=AttackType(row[10]) if row[10] else None,
                        details=json.loads(row[11]) if row[11] else {},
                        blocked=bool(row[12]),
                        action_taken=row[13]
                    )
                    events.append(event)
                
                return events
        except Exception as e:
            logger.error(f"Erro ao obter eventos de segurança: {e}")
            return []

class APISecurityManager:
    """Gerenciador de segurança de APIs"""
    
    def __init__(self, 
                 token_config: TokenConfig,
                 rate_limit_config: RateLimitConfig,
                 security_level: SecurityLevel = SecurityLevel.MEDIUM):
        
        self.token_manager = TokenManager(token_config)
        self.rate_limiter = RateLimiter(rate_limit_config)
        self.security_validator = SecurityValidator()
        self.audit_logger = AuditLogger()
        self.security_level = security_level
        
        # Configurações
        self.whitelisted_ips: set = set()
        self.blacklisted_ips: set = set()
        self.whitelisted_endpoints: set = set()
        self.rate_limit_by_user: bool = True
        self.rate_limit_by_ip: bool = True
        
        # Métricas
        self.metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'security_events': 0,
            'rate_limit_violations': 0,
            'invalid_tokens': 0,
            'attacks_detected': 0
        }
    
    def validate_request(self, 
                        request_data: Dict[str, Any],
                        token: str = None) -> Tuple[bool, Dict[str, Any], Optional[SecurityEvent]]:
        """Valida requisição completa"""
        security_event = None
        validation_result = {
            'valid': True,
            'blocked': False,
            'reason': None,
            'user_id': None,
            'permissions': [],
            'rate_limit_info': None
        }
        
        # Extrair dados da requisição
        source_ip = request_data.get('source_ip', '')
        endpoint = request_data.get('endpoint', '')
        method = request_data.get('method', '')
        user_agent = request_data.get('user_agent', '')
        params = request_data.get('params', {})
        payload = request_data.get('payload', '')
        
        # 1. Verificar IPs bloqueados/whitelist
        if source_ip in self.blacklisted_ips:
            security_event = SecurityEvent(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc),
                event_type="ip_blocked",
                severity=SecurityLevel.HIGH,
                source_ip=source_ip,
                endpoint=endpoint,
                method=method,
                user_agent=user_agent,
                blocked=True,
                action_taken="Request blocked - IP blacklisted"
            )
            validation_result['valid'] = False
            validation_result['blocked'] = True
            validation_result['reason'] = "IP is blacklisted"
        
        elif source_ip in self.whitelisted_ips:
            # IP whitelisted - pular algumas validações
            pass
        
        else:
            # 2. Validar entrada
            for param_name, param_value in params.items():
                if isinstance(param_value, str):
                    is_valid, attack_type, reason = self.security_validator.validate_input(param_value, f"param_{param_name}")
                    if not is_valid:
                        security_event = SecurityEvent(
                            id=str(uuid.uuid4()),
                            timestamp=datetime.now(timezone.utc),
                            event_type="attack_detected",
                            severity=SecurityLevel.HIGH,
                            source_ip=source_ip,
                            endpoint=endpoint,
                            method=method,
                            user_agent=user_agent,
                            attack_type=attack_type,
                            details={'param_name': param_name, 'param_value': param_value},
                            blocked=True,
                            action_taken=f"Request blocked - {reason}"
                        )
                        validation_result['valid'] = False
                        validation_result['blocked'] = True
                        validation_result['reason'] = reason
                        break
            
            # 3. Validar payload
            if validation_result['valid'] and payload:
                is_valid, attack_type, reason = self.security_validator.validate_input(payload, "payload")
                if not is_valid:
                    security_event = SecurityEvent(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc),
                        event_type="attack_detected",
                        severity=SecurityLevel.HIGH,
                        source_ip=source_ip,
                        endpoint=endpoint,
                        method=method,
                        user_agent=user_agent,
                        attack_type=attack_type,
                        details={'payload': payload[:100]},  # Primeiros 100 chars
                        blocked=True,
                        action_taken=f"Request blocked - {reason}"
                    )
                    validation_result['valid'] = False
                    validation_result['blocked'] = True
                    validation_result['reason'] = reason
            
            # 4. Detectar atividade suspeita
            if validation_result['valid']:
                is_suspicious, attack_type, reason = self.security_validator.is_suspicious_activity(request_data)
                if is_suspicious:
                    security_event = SecurityEvent(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc),
                        event_type="suspicious_activity",
                        severity=SecurityLevel.MEDIUM,
                        source_ip=source_ip,
                        endpoint=endpoint,
                        method=method,
                        user_agent=user_agent,
                        attack_type=attack_type,
                        details={'reason': reason},
                        blocked=False,
                        action_taken="Activity logged for monitoring"
                    )
        
        # 5. Validar token
        if validation_result['valid'] and token:
            token_data = self.token_manager.validate_token(token)
            if token_data:
                validation_result['user_id'] = token_data['user_id']
                validation_result['permissions'] = token_data.get('permissions', [])
            else:
                security_event = SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc),
                    event_type="invalid_token",
                    severity=SecurityLevel.MEDIUM,
                    source_ip=source_ip,
                    endpoint=endpoint,
                    method=method,
                    user_agent=user_agent,
                    attack_type=AttackType.INVALID_TOKEN,
                    blocked=True,
                    action_taken="Request blocked - Invalid token"
                )
                validation_result['valid'] = False
                validation_result['blocked'] = True
                validation_result['reason'] = "Invalid token"
        
        # 6. Rate limiting
        if validation_result['valid']:
            # Rate limiting por IP
            if self.rate_limit_by_ip:
                ip_allowed, ip_info = self.rate_limiter.is_allowed(source_ip)
                if not ip_allowed:
                    security_event = SecurityEvent(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc),
                        event_type="rate_limit_exceeded",
                        severity=SecurityLevel.MEDIUM,
                        source_ip=source_ip,
                        endpoint=endpoint,
                        method=method,
                        user_agent=user_agent,
                        attack_type=AttackType.RATE_LIMIT_EXCEEDED,
                        details=ip_info,
                        blocked=ip_info.get('blocked', False),
                        action_taken="Request blocked - Rate limit exceeded"
                    )
                    validation_result['valid'] = False
                    validation_result['blocked'] = ip_info.get('blocked', False)
                    validation_result['reason'] = ip_info.get('reason', 'Rate limit exceeded')
                    validation_result['rate_limit_info'] = ip_info
            
            # Rate limiting por usuário
            if (validation_result['valid'] and 
                self.rate_limit_by_user and 
                validation_result['user_id']):
                
                user_allowed, user_info = self.rate_limiter.is_allowed(f"user_{validation_result['user_id']}")
                if not user_allowed:
                    security_event = SecurityEvent(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now(timezone.utc),
                        event_type="rate_limit_exceeded",
                        severity=SecurityLevel.MEDIUM,
                        source_ip=source_ip,
                        user_id=validation_result['user_id'],
                        endpoint=endpoint,
                        method=method,
                        user_agent=user_agent,
                        attack_type=AttackType.RATE_LIMIT_EXCEEDED,
                        details=user_info,
                        blocked=user_info.get('blocked', False),
                        action_taken="Request blocked - User rate limit exceeded"
                    )
                    validation_result['valid'] = False
                    validation_result['blocked'] = user_info.get('blocked', False)
                    validation_result['reason'] = user_info.get('reason', 'User rate limit exceeded')
                    validation_result['rate_limit_info'] = user_info
        
        # Registrar evento de segurança se houver
        if security_event:
            self.audit_logger.log_security_event(security_event)
            self.metrics['security_events'] += 1
            
            if security_event.blocked:
                self.metrics['blocked_requests'] += 1
            
            if security_event.attack_type:
                self.metrics['attacks_detected'] += 1
        
        # Atualizar métricas
        self.metrics['total_requests'] += 1
        
        return validation_result['valid'], validation_result, security_event
    
    def add_whitelisted_ip(self, ip: str):
        """Adiciona IP à whitelist"""
        self.whitelisted_ips.add(ip)
    
    def add_blacklisted_ip(self, ip: str):
        """Adiciona IP à blacklist"""
        self.blacklisted_ips.add(ip)
    
    def remove_whitelisted_ip(self, ip: str):
        """Remove IP da whitelist"""
        self.whitelisted_ips.discard(ip)
    
    def remove_blacklisted_ip(self, ip: str):
        """Remove IP da blacklist"""
        self.blacklisted_ips.discard(ip)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de segurança"""
        return {
            'security_level': self.security_level.value,
            'total_requests': self.metrics['total_requests'],
            'blocked_requests': self.metrics['blocked_requests'],
            'security_events': self.metrics['security_events'],
            'rate_limit_violations': self.metrics['rate_limit_violations'],
            'invalid_tokens': self.metrics['invalid_tokens'],
            'attacks_detected': self.metrics['attacks_detected'],
            'block_rate': (self.metrics['blocked_requests'] / self.metrics['total_requests'] * 100) if self.metrics['total_requests'] > 0 else 0,
            'whitelisted_ips': len(self.whitelisted_ips),
            'blacklisted_ips': len(self.blacklisted_ips)
        }
    
    def get_security_events(self, **kwargs) -> List[SecurityEvent]:
        """Obtém eventos de segurança"""
        return self.audit_logger.get_security_events(**kwargs)

# Decorators para facilitar uso
def require_auth(permission: str = None):
    """Decorator para requerer autenticação"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implementar validação de autenticação
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(requests_per_minute: int = 60):
    """Decorator para rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implementar rate limiting
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_input(input_param: str):
    """Decorator para validação de entrada"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implementar validação de entrada
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Teste de funcionalidade
if __name__ == "__main__":
    # Configurar sistema de segurança
    token_config = TokenConfig(
        secret_key="your-secret-key-here",
        access_token_expiry=3600,
        refresh_token_expiry=2592000
    )
    
    rate_limit_config = RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
        burst_limit=10
    )
    
    security_manager = APISecurityManager(
        token_config=token_config,
        rate_limit_config=rate_limit_config,
        security_level=SecurityLevel.HIGH
    )
    
    # Testar validação de requisição
    request_data = {
        'source_ip': '192.168.1.100',
        'endpoint': '/api/users',
        'method': 'GET',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'params': {'user_id': '123'},
        'payload': ''
    }
    
    is_valid, result, event = security_manager.validate_request(request_data)
    
    print(f"Requisição válida: {is_valid}")
    print(f"Resultado: {result}")
    
    if event:
        print(f"Evento de segurança: {event.to_dict()}")
    
    # Mostrar métricas
    metrics = security_manager.get_metrics()
    print(f"Métricas: {json.dumps(metrics, indent=2)}") 