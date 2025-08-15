"""
Sistema de IP Whitelist Avançado - Omni Keywords Finder

Funcionalidades:
- Validação de IPs por integração
- Suporte a CIDR ranges
- Cache de IPs válidos no Redis
- Configuração por ambiente
- Logging de tentativas de acesso
- Sistema de alertas para IPs suspeitos
- Métricas de segurança
- Integração com observabilidade

Autor: Sistema de IP Whitelist Avançado
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: IP_WHITELIST_001
"""

import os
import json
import ipaddress
import redis
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
import asyncio
from pathlib import Path

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary
except ImportError:
    # Fallback se Prometheus não estiver disponível
    class MockMetric:
        def __init__(self, name, description, **kwargs):
            self.name = name
            self.description = description
            self._value = 0
        
        def inc(self, amount=1):
            self._value += amount
        
        def set(self, value):
            self._value = value
        
        def observe(self, value):
            self._value = value
    
    Counter = Histogram = Gauge = Summary = MockMetric

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPWhitelistStatus(Enum):
    """Status do IP na whitelist"""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"

class IntegrationType(Enum):
    """Tipos de integração suportados"""
    WEBHOOK = "webhook"
    API = "api"
    ADMIN = "admin"
    MONITORING = "monitoring"
    BACKUP = "backup"
    PAYMENT = "payment"
    ANALYTICS = "analytics"

@dataclass
class IPWhitelistEntry:
    """Entrada na whitelist de IPs"""
    ip_range: str  # IP único ou CIDR range
    integration: IntegrationType
    description: str
    added_by: str
    added_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = None

@dataclass
class IPAccessAttempt:
    """Registro de tentativa de acesso"""
    ip: str
    integration: IntegrationType
    timestamp: datetime
    status: IPWhitelistStatus
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    source: str = "ip_whitelist"
    metadata: Dict[str, Any] = None

class IPWhitelistManager:
    """Gerenciador avançado de IP whitelist"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.whitelist_entries: Dict[IntegrationType, Set[ipaddress.IPv4Network]] = defaultdict(set)
        self.suspicious_ips: Set[str] = set()
        self.blocked_ips: Set[str] = set()
        self.access_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Cache Redis
        self.redis_client = self._init_redis()
        
        # Métricas Prometheus
        self.access_attempts = Counter(
            'ip_whitelist_access_attempts_total',
            'Total de tentativas de acesso por IP',
            ['ip', 'integration', 'status']
        )
        
        self.suspicious_ips_gauge = Gauge(
            'ip_whitelist_suspicious_ips_total',
            'Total de IPs suspeitos'
        )
        
        self.blocked_ips_gauge = Gauge(
            'ip_whitelist_blocked_ips_total',
            'Total de IPs bloqueados'
        )
        
        self.whitelist_size = Gauge(
            'ip_whitelist_entries_total',
            'Total de entradas na whitelist',
            ['integration']
        )
        
        # Carregar configuração inicial
        self._load_whitelist()
        self._start_cleanup_thread()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão do sistema"""
        return {
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', 6379)),
                'db': int(os.getenv('REDIS_DB', 0)),
                'password': os.getenv('REDIS_PASSWORD'),
                'enabled': os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
            },
            'cache': {
                'ttl_seconds': 3600,  # 1 hora
                'max_entries': 10000
            },
            'security': {
                'max_suspicious_attempts': 5,
                'suspicious_timeout_minutes': 30,
                'block_timeout_hours': 24,
                'alert_threshold': 10
            },
            'logging': {
                'log_all_attempts': True,
                'log_suspicious_only': False
            }
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Inicializa conexão Redis"""
        if not self.config['redis']['enabled']:
            return None
        
        try:
            return redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                password=self.config['redis']['password'],
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis não disponível: {str(e)}")
            return None
    
    def add_ip_to_whitelist(self, ip_range: str, integration: IntegrationType, 
                           description: str, added_by: str, 
                           expires_at: Optional[datetime] = None) -> bool:
        """Adiciona IP ou range à whitelist"""
        try:
            # Validar formato do IP/range
            if '/' in ip_range:
                network = ipaddress.IPv4Network(ip_range, strict=False)
            else:
                network = ipaddress.IPv4Network(f"{ip_range}/32", strict=False)
            
            # Adicionar à whitelist
            self.whitelist_entries[integration].add(network)
            
            # Criar entrada
            entry = IPWhitelistEntry(
                ip_range=ip_range,
                integration=integration,
                description=description,
                added_by=added_by,
                added_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            # Salvar no Redis se disponível
            if self.redis_client:
                self._save_entry_to_redis(entry)
            
            # Atualizar métricas
            self.whitelist_size.labels(integration=integration.value).set(
                len(self.whitelist_entries[integration])
            )
            
            logger.info(f"IP {ip_range} adicionado à whitelist para {integration.value}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar IP {ip_range}: {str(e)}")
            return False
    
    def remove_ip_from_whitelist(self, ip_range: str, integration: IntegrationType) -> bool:
        """Remove IP ou range da whitelist"""
        try:
            # Validar formato do IP/range
            if '/' in ip_range:
                network = ipaddress.IPv4Network(ip_range, strict=False)
            else:
                network = ipaddress.IPv4Network(f"{ip_range}/32", strict=False)
            
            # Remover da whitelist
            if network in self.whitelist_entries[integration]:
                self.whitelist_entries[integration].remove(network)
                
                # Remover do Redis se disponível
                if self.redis_client:
                    self._remove_entry_from_redis(ip_range, integration)
                
                # Atualizar métricas
                self.whitelist_size.labels(integration=integration.value).set(
                    len(self.whitelist_entries[integration])
                )
                
                logger.info(f"IP {ip_range} removido da whitelist para {integration.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao remover IP {ip_range}: {str(e)}")
            return False
    
    def is_ip_allowed(self, ip: str, integration: IntegrationType, 
                     user_agent: Optional[str] = None,
                     request_path: Optional[str] = None) -> bool:
        """Verifica se IP está permitido para a integração"""
        try:
            # Validar formato do IP
            ip_obj = ipaddress.IPv4Address(ip)
            
            # Verificar se está bloqueado
            if ip in self.blocked_ips:
                self._log_access_attempt(ip, integration, IPWhitelistStatus.BLOCKED, 
                                       user_agent, request_path)
                return False
            
            # Verificar se está na whitelist
            is_allowed = False
            for network in self.whitelist_entries[integration]:
                if ip_obj in network:
                    is_allowed = True
                    break
            
            # Se não há whitelist configurada, permitir todos
            if not self.whitelist_entries[integration]:
                is_allowed = True
            
            # Registrar tentativa
            status = IPWhitelistStatus.ALLOWED if is_allowed else IPWhitelistStatus.BLOCKED
            self._log_access_attempt(ip, integration, status, user_agent, request_path)
            
            # Verificar comportamento suspeito
            if not is_allowed:
                self._check_suspicious_behavior(ip, integration)
            
            return is_allowed
            
        except Exception as e:
            logger.error(f"Erro ao verificar IP {ip}: {str(e)}")
            self._log_access_attempt(ip, integration, IPWhitelistStatus.UNKNOWN, 
                                   user_agent, request_path)
            return False
    
    def _check_suspicious_behavior(self, ip: str, integration: IntegrationType):
        """Verifica comportamento suspeito do IP"""
        # Contar tentativas recentes
        recent_attempts = 0
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        for attempt in self.access_history[ip]:
            if (attempt.timestamp > cutoff_time and 
                attempt.integration == integration and
                attempt.status == IPWhitelistStatus.BLOCKED):
                recent_attempts += 1
        
        # Marcar como suspeito se muitas tentativas
        if recent_attempts >= self.config['security']['max_suspicious_attempts']:
            self.suspicious_ips.add(ip)
            self.suspicious_ips_gauge.set(len(self.suspicious_ips))
            
            logger.warning(f"IP {ip} marcado como suspeito para {integration.value}")
            
            # Alertar se ultrapassar threshold
            if recent_attempts >= self.config['security']['alert_threshold']:
                self._send_alert(ip, integration, recent_attempts)
    
    def _log_access_attempt(self, ip: str, integration: IntegrationType, 
                           status: IPWhitelistStatus,
                           user_agent: Optional[str] = None,
                           request_path: Optional[str] = None):
        """Registra tentativa de acesso"""
        attempt = IPAccessAttempt(
            ip=ip,
            integration=integration,
            timestamp=datetime.utcnow(),
            status=status,
            user_agent=user_agent,
            request_path=request_path
        )
        
        # Adicionar ao histórico
        self.access_history[ip].append(attempt)
        
        # Atualizar métricas
        self.access_attempts.labels(
            ip=ip,
            integration=integration.value,
            status=status.value
        ).inc()
        
        # Log detalhado se configurado
        if self.config['logging']['log_all_attempts'] or (
            self.config['logging']['log_suspicious_only'] and 
            status != IPWhitelistStatus.ALLOWED
        ):
            logger.info(f"Acesso {status.value}: {ip} -> {integration.value}")
    
    def _send_alert(self, ip: str, integration: IntegrationType, attempts: int):
        """Envia alerta de segurança"""
        alert_message = f"ALERTA: IP {ip} com {attempts} tentativas suspeitas para {integration.value}"
        logger.error(alert_message)
        
        # Aqui você pode integrar com sistemas de alerta (Slack, email, etc.)
        # Por enquanto, apenas log
    
    def get_whitelist_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da whitelist"""
        stats = {
            'total_entries': sum(len(entries) for entries in self.whitelist_entries.values()),
            'entries_by_integration': {
                integration.value: len(entries) 
                for integration, entries in self.whitelist_entries.items()
            },
            'suspicious_ips_count': len(self.suspicious_ips),
            'blocked_ips_count': len(self.blocked_ips),
            'recent_access_attempts': {}
        }
        
        # Estatísticas de tentativas recentes
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        for ip, attempts in self.access_history.items():
            recent = [a for a in attempts if a.timestamp > cutoff_time]
            if recent:
                stats['recent_access_attempts'][ip] = {
                    'total': len(recent),
                    'allowed': len([a for a in recent if a.status == IPWhitelistStatus.ALLOWED]),
                    'blocked': len([a for a in recent if a.status == IPWhitelistStatus.BLOCKED]),
                    'suspicious': len([a for a in recent if a.status == IPWhitelistStatus.SUSPICIOUS])
                }
        
        return stats
    
    def _save_entry_to_redis(self, entry: IPWhitelistEntry):
        """Salva entrada no Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"ip_whitelist:{entry.integration.value}:{entry.ip_range}"
            data = asdict(entry)
            data['added_at'] = data['added_at'].isoformat()
            if data['expires_at']:
                data['expires_at'] = data['expires_at'].isoformat()
            
            self.redis_client.setex(
                key,
                self.config['cache']['ttl_seconds'],
                json.dumps(data)
            )
        except Exception as e:
            logger.warning(f"Erro ao salvar no Redis: {str(e)}")
    
    def _remove_entry_from_redis(self, ip_range: str, integration: IntegrationType):
        """Remove entrada do Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"ip_whitelist:{integration.value}:{ip_range}"
            self.redis_client.delete(key)
        except Exception as e:
            logger.warning(f"Erro ao remover do Redis: {str(e)}")
    
    def _load_whitelist(self):
        """Carrega whitelist do Redis"""
        if not self.redis_client:
            return
        
        try:
            # Buscar todas as chaves de whitelist
            keys = self.redis_client.keys("ip_whitelist:*")
            
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    entry_data = json.loads(data)
                    
                    # Verificar se não expirou
                    if entry_data.get('expires_at'):
                        expires_at = datetime.fromisoformat(entry_data['expires_at'])
                        if expires_at < datetime.utcnow():
                            self.redis_client.delete(key)
                            continue
                    
                    # Adicionar à whitelist
                    integration = IntegrationType(entry_data['integration'])
                    ip_range = entry_data['ip_range']
                    
                    if '/' in ip_range:
                        network = ipaddress.IPv4Network(ip_range, strict=False)
                    else:
                        network = ipaddress.IPv4Network(f"{ip_range}/32", strict=False)
                    
                    self.whitelist_entries[integration].add(network)
            
            logger.info(f"Whitelist carregada: {sum(len(entries) for entries in self.whitelist_entries.values())} entradas")
            
        except Exception as e:
            logger.error(f"Erro ao carregar whitelist: {str(e)}")
    
    def _start_cleanup_thread(self):
        """Inicia thread de limpeza"""
        def cleanup_worker():
            while True:
                try:
                    self._cleanup_expired_entries()
                    self._cleanup_old_history()
                    time.sleep(300)  # Executar a cada 5 minutos
                except Exception as e:
                    logger.error(f"Erro no cleanup: {str(e)}")
        
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
    
    def _cleanup_expired_entries(self):
        """Remove entradas expiradas"""
        current_time = datetime.utcnow()
        
        for integration, networks in self.whitelist_entries.items():
            expired_networks = set()
            for network in networks:
                # Verificar expiração no Redis
                if self.redis_client:
                    key = f"ip_whitelist:{integration.value}:{network}"
                    data = self.redis_client.get(key)
                    if data:
                        entry_data = json.loads(data)
                        if entry_data.get('expires_at'):
                            expires_at = datetime.fromisoformat(entry_data['expires_at'])
                            if expires_at < current_time:
                                expired_networks.add(network)
                                self.redis_client.delete(key)
            
            # Remover redes expiradas
            for network in expired_networks:
                networks.discard(network)
    
    def _cleanup_old_history(self):
        """Remove histórico antigo"""
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        
        for ip, attempts in self.access_history.items():
            # Manter apenas tentativas recentes
            recent_attempts = [a for a in attempts if a.timestamp > cutoff_time]
            self.access_history[ip] = deque(recent_attempts, maxlen=1000)

def create_ip_whitelist_manager(config: Optional[Dict[str, Any]] = None) -> IPWhitelistManager:
    """Factory para criar gerenciador de IP whitelist"""
    return IPWhitelistManager(config) 