"""
Burst Handler - Omni Keywords Finder
Tracing ID: BURST_HANDLER_20250127_001

Sistema de burst allowance para permitir picos de tráfego legítimos
com detecção inteligente de padrões de uso.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import hashlib
import ipaddress

from fastapi import Request, HTTPException
import redis
import psutil

# Configuração de logging
logger = logging.getLogger(__name__)

class BurstType(Enum):
    """Tipos de burst"""
    LEGITIMATE = "legitimate"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"

@dataclass
class BurstConfig:
    """Configuração de burst allowance"""
    base_allowance: float  # Allowance base (ex: 2.0 = 200%)
    max_allowance: float  # Allowance máximo (ex: 5.0 = 500%)
    window_size: int  # Janela de tempo em segundos
    cooldown_period: int  # Período de cooldown após burst
    detection_threshold: int  # Threshold para detecção de burst
    whitelist_patterns: List[str] = field(default_factory=list)

@dataclass
class BurstEvent:
    """Evento de burst detectado"""
    identifier: str
    burst_type: BurstType
    request_count: int
    normal_limit: int
    burst_limit: int
    duration: float
    timestamp: float
    confidence: float
    metadata: Dict[str, Any]

class BurstHandler:
    """
    Handler de burst com detecção inteligente e allowance adaptativo
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_config: Optional[BurstConfig] = None,
        enable_learning: bool = True,
        learning_window: int = 1800,  # 30 minutos
        max_burst_history: int = 1000
    ):
        self.redis_url = redis_url
        self.enable_learning = enable_learning
        self.learning_window = learning_window
        self.max_burst_history = max_burst_history
        
        # Configuração padrão
        self.default_config = default_config or BurstConfig(
            base_allowance=2.0,  # 200% do limite normal
            max_allowance=5.0,   # 500% do limite normal
            window_size=60,      # 1 minuto
            cooldown_period=300, # 5 minutos
            detection_threshold=10
        )
        
        # Configurações por usuário/IP
        self.user_configs: Dict[str, BurstConfig] = {}
        self.ip_configs: Dict[str, BurstConfig] = {}
        
        # Estado do sistema
        self.is_running = False
        self.burst_history: deque = deque(maxlen=max_burst_history)
        self.active_bursts: Dict[str, BurstEvent] = {}
        self.cooldown_periods: Dict[str, float] = {}
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._stop_event = threading.Event()
        
        # Redis connection
        self._redis_client = None
        self._setup_redis()
        
        # Callbacks
        self._burst_detected_callbacks: List[Callable[[BurstEvent], None]] = []
        self._burst_ended_callbacks: List[Callable[[BurstEvent], None]] = []
        self._malicious_burst_callbacks: List[Callable[[BurstEvent], None]] = []
        
        logger.info("Burst handler initialized")
    
    def _setup_redis(self):
        """Configura conexão com Redis"""
        try:
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self._redis_client.ping()
            logger.info("Redis connection established for burst handler")
        except Exception as e:
            logger.warning(f"Redis connection failed for burst handler: {e}")
            self._redis_client = None
    
    def add_burst_detected_callback(self, callback: Callable[[BurstEvent], None]):
        """Adiciona callback para burst detectado"""
        self._burst_detected_callbacks.append(callback)
    
    def add_burst_ended_callback(self, callback: Callable[[BurstEvent], None]):
        """Adiciona callback para burst finalizado"""
        self._burst_ended_callbacks.append(callback)
    
    def add_malicious_burst_callback(self, callback: Callable[[BurstEvent], None]):
        """Adiciona callback para burst malicioso"""
        self._malicious_burst_callbacks.append(callback)
    
    def start_monitoring(self):
        """Inicia monitoramento de burst"""
        if self.is_running:
            logger.warning("Burst monitoring already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="BurstHandlerMonitor"
        )
        self._monitoring_thread.start()
        
        logger.info("Burst monitoring started")
    
    def stop_monitoring(self):
        """Para monitoramento de burst"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        
        logger.info("Burst monitoring stopped")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while not self._stop_event.is_set():
            try:
                # Limpar bursts expirados
                self._cleanup_expired_bursts()
                
                # Limpar cooldowns expirados
                self._cleanup_expired_cooldowns()
                
                # Analisar padrões de burst
                if self.enable_learning:
                    self._analyze_burst_patterns()
                
                # Aguardar próximo ciclo
                self._stop_event.wait(30)  # Verificar a cada 30 segundos
                
            except Exception as e:
                logger.error(f"Error in burst monitoring loop: {e}")
                self._stop_event.wait(60)
    
    def _cleanup_expired_bursts(self):
        """Remove bursts expirados"""
        current_time = time.time()
        expired_bursts = []
        
        with self._lock:
            for identifier, burst in self.active_bursts.items():
                if current_time - burst.timestamp > burst.duration:
                    expired_bursts.append(identifier)
            
            for identifier in expired_bursts:
                burst = self.active_bursts.pop(identifier)
                self._notify_burst_ended_callbacks(burst)
                logger.info(f"Burst ended for {identifier}: {burst.burst_type.value}")
    
    def _cleanup_expired_cooldowns(self):
        """Remove cooldowns expirados"""
        current_time = time.time()
        expired_cooldowns = []
        
        with self._lock:
            for identifier, cooldown_end in self.cooldown_periods.items():
                if current_time > cooldown_end:
                    expired_cooldowns.append(identifier)
            
            for identifier in expired_cooldowns:
                self.cooldown_periods.pop(identifier)
                logger.debug(f"Cooldown expired for {identifier}")
    
    def _analyze_burst_patterns(self):
        """Analisa padrões de burst para aprendizado"""
        try:
            with self._lock:
                if not self.burst_history:
                    return
                
                # Agrupar por identificador
                bursts_by_identifier = defaultdict(list)
                for burst in self.burst_history:
                    bursts_by_identifier[burst.identifier].append(burst)
                
                # Analisar padrões
                for identifier, bursts in bursts_by_identifier.items():
                    if len(bursts) < 3:  # Precisa de pelo menos 3 bursts para análise
                        continue
                    
                    # Calcular métricas
                    total_bursts = len(bursts)
                    legitimate_count = sum(1 for b in bursts if b.burst_type == BurstType.LEGITIMATE)
                    malicious_count = sum(1 for b in bursts if b.burst_type == BurstType.MALICIOUS)
                    
                    legitimate_ratio = legitimate_count / total_bursts
                    
                    # Ajustar configuração baseado no histórico
                    config = self._get_config_for_identifier(identifier)
                    
                    if legitimate_ratio > 0.8:  # 80% dos bursts são legítimos
                        # Aumentar allowance
                        new_allowance = min(config.base_allowance * 1.1, config.max_allowance)
                        config.base_allowance = new_allowance
                        logger.info(f"Increased burst allowance for {identifier}: {new_allowance:.2f}")
                    
                    elif legitimate_ratio < 0.3:  # 30% dos bursts são legítimos
                        # Diminuir allowance
                        new_allowance = max(config.base_allowance * 0.9, 1.0)
                        config.base_allowance = new_allowance
                        logger.info(f"Decreased burst allowance for {identifier}: {new_allowance:.2f}")
                    
                    self._set_config_for_identifier(identifier, config)
                    
        except Exception as e:
            logger.error(f"Error analyzing burst patterns: {e}")
    
    async def check_burst_allowance(
        self,
        identifier: str,
        current_request_count: int,
        normal_limit: int,
        request: Request
    ) -> Tuple[bool, int, BurstType]:
        """
        Verifica se deve permitir burst allowance
        
        Returns:
            (allowed, burst_limit, burst_type)
        """
        try:
            # Verificar se está em cooldown
            if self._is_in_cooldown(identifier):
                return False, normal_limit, BurstType.UNKNOWN
            
            # Obter configuração
            config = self._get_config_for_identifier(identifier)
            
            # Verificar se já está em burst ativo
            if identifier in self.active_bursts:
                burst = self.active_bursts[identifier]
                burst_limit = int(normal_limit * burst.confidence)
                return True, burst_limit, burst.burst_type
            
            # Verificar se deve iniciar burst
            if current_request_count >= config.detection_threshold:
                burst_type = await self._classify_burst(identifier, request)
                confidence = self._calculate_burst_confidence(burst_type, request)
                
                # Calcular burst limit
                burst_allowance = min(config.base_allowance * confidence, config.max_allowance)
                burst_limit = int(normal_limit * burst_allowance)
                
                # Criar evento de burst
                burst_event = BurstEvent(
                    identifier=identifier,
                    burst_type=burst_type,
                    request_count=current_request_count,
                    normal_limit=normal_limit,
                    burst_limit=burst_limit,
                    duration=config.window_size,
                    timestamp=time.time(),
                    confidence=confidence,
                    metadata=self._extract_burst_metadata(request)
                )
                
                # Registrar burst
                with self._lock:
                    self.active_bursts[identifier] = burst_event
                    self.burst_history.append(burst_event)
                
                # Notificar callbacks
                self._notify_burst_detected_callbacks(burst_event)
                
                if burst_type == BurstType.MALICIOUS:
                    self._notify_malicious_burst_callbacks(burst_event)
                
                logger.info(f"Burst detected for {identifier}: {burst_type.value}, limit: {burst_limit}")
                
                return True, burst_limit, burst_type
            
            return False, normal_limit, BurstType.UNKNOWN
            
        except Exception as e:
            logger.error(f"Error checking burst allowance: {e}")
            return False, normal_limit, BurstType.UNKNOWN
    
    async def _classify_burst(self, identifier: str, request: Request) -> BurstType:
        """Classifica o tipo de burst"""
        try:
            # Extrair características da requisição
            user_agent = request.headers.get('user-agent', '')
            referer = request.headers.get('referer', '')
            path = request.url.path
            method = request.method
            
            # Verificar padrões suspeitos
            suspicious_patterns = [
                'bot', 'crawler', 'spider', 'scraper',
                'curl', 'wget', 'python-requests'
            ]
            
            # Verificar user agent suspeito
            if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
                return BurstType.SUSPICIOUS
            
            # Verificar padrões de path suspeitos
            suspicious_paths = [
                '/api/', '/admin/', '/login', '/register',
                '/search', '/crawl', '/scrape'
            ]
            
            if any(suspicious_path in path for suspicious_path in suspicious_paths):
                return BurstType.SUSPICIOUS
            
            # Verificar histórico do identificador
            with self._lock:
                recent_bursts = [
                    b for b in self.burst_history[-10:]  # Últimos 10 bursts
                    if b.identifier == identifier
                ]
                
                if len(recent_bursts) >= 3:
                    malicious_count = sum(1 for b in recent_bursts if b.burst_type == BurstType.MALICIOUS)
                    if malicious_count >= 2:
                        return BurstType.MALICIOUS
            
            # Verificar padrões de tempo
            if self._is_rapid_fire(identifier):
                return BurstType.SUSPICIOUS
            
            # Verificar se é padrão conhecido legítimo
            if self._is_known_legitimate_pattern(request):
                return BurstType.LEGITIMATE
            
            # Padrão desconhecido
            return BurstType.UNKNOWN
            
        except Exception as e:
            logger.error(f"Error classifying burst: {e}")
            return BurstType.UNKNOWN
    
    def _calculate_burst_confidence(self, burst_type: BurstType, request: Request) -> float:
        """Calcula confiança do burst baseado no tipo e características"""
        base_confidence = {
            BurstType.LEGITIMATE: 1.0,
            BurstType.SUSPICIOUS: 0.7,
            BurstType.MALICIOUS: 0.3,
            BurstType.UNKNOWN: 0.5
        }
        
        confidence = base_confidence.get(burst_type, 0.5)
        
        # Ajustar baseado em características adicionais
        user_agent = request.headers.get('user-agent', '')
        
        # Navegadores conhecidos têm maior confiança
        known_browsers = ['chrome', 'firefox', 'safari', 'edge']
        if any(browser in user_agent.lower() for browser in known_browsers):
            confidence *= 1.2
        
        # Requisições com referer têm maior confiança
        if request.headers.get('referer'):
            confidence *= 1.1
        
        # Limitar confiança
        return min(confidence, 2.0)
    
    def _extract_burst_metadata(self, request: Request) -> Dict[str, Any]:
        """Extrai metadados da requisição para análise"""
        return {
            'user_agent': request.headers.get('user-agent', ''),
            'referer': request.headers.get('referer', ''),
            'path': request.url.path,
            'method': request.method,
            'ip': self._extract_client_ip(request),
            'timestamp': time.time()
        }
    
    def _extract_client_ip(self, request: Request) -> str:
        """Extrai IP do cliente"""
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        client_ip = request.client.host
        if client_ip:
            return client_ip
        
        return "unknown"
    
    def _is_rapid_fire(self, identifier: str) -> bool:
        """Verifica se há requisições muito rápidas"""
        try:
            if self._redis_client:
                # Usar Redis para verificar
                key = f"burst_rapid:{identifier}"
                recent_requests = self._redis_client.zrangebyscore(
                    key, time.time() - 10, time.time()  # Últimos 10 segundos
                )
                return len(recent_requests) > 20  # Mais de 20 requisições em 10s
            else:
                # Verificar em memória
                with self._lock:
                    recent_requests = [
                        req for req in self.burst_history[-50:]  # Últimas 50 entradas
                        if req.identifier == identifier and 
                        time.time() - req.timestamp < 10
                    ]
                    return len(recent_requests) > 20
                    
        except Exception as e:
            logger.error(f"Error checking rapid fire: {e}")
            return False
    
    def _is_known_legitimate_pattern(self, request: Request) -> bool:
        """Verifica se é um padrão legítimo conhecido"""
        # Verificar padrões de navegação normal
        path = request.url.path
        
        # Páginas de navegação normal
        legitimate_paths = [
            '/', '/home', '/dashboard', '/profile',
            '/products', '/services', '/about', '/contact'
        ]
        
        if any(legitimate_path in path for legitimate_path in legitimate_paths):
            return True
        
        # Verificar user agent de navegador
        user_agent = request.headers.get('user-agent', '').lower()
        browser_indicators = ['mozilla', 'chrome', 'safari', 'firefox', 'edge']
        
        if any(indicator in user_agent for indicator in browser_indicators):
            return True
        
        return False
    
    def _is_in_cooldown(self, identifier: str) -> bool:
        """Verifica se o identificador está em período de cooldown"""
        current_time = time.time()
        cooldown_end = self.cooldown_periods.get(identifier, 0)
        return current_time < cooldown_end
    
    def _get_config_for_identifier(self, identifier: str) -> BurstConfig:
        """Obtém configuração para um identificador"""
        if self._is_ip_address(identifier):
            return self.ip_configs.get(identifier, self.default_config)
        else:
            return self.user_configs.get(identifier, self.default_config)
    
    def _set_config_for_identifier(self, identifier: str, config: BurstConfig):
        """Define configuração para um identificador"""
        if self._is_ip_address(identifier):
            self.ip_configs[identifier] = config
        else:
            self.user_configs[identifier] = config
    
    def _is_ip_address(self, identifier: str) -> bool:
        """Verifica se o identificador é um endereço IP"""
        try:
            ipaddress.ip_address(identifier)
            return True
        except ValueError:
            return False
    
    def _notify_burst_detected_callbacks(self, burst: BurstEvent):
        """Notifica callbacks de burst detectado"""
        for callback in self._burst_detected_callbacks:
            try:
                callback(burst)
            except Exception as e:
                logger.error(f"Error in burst detected callback: {e}")
    
    def _notify_burst_ended_callbacks(self, burst: BurstEvent):
        """Notifica callbacks de burst finalizado"""
        for callback in self._burst_ended_callbacks:
            try:
                callback(burst)
            except Exception as e:
                logger.error(f"Error in burst ended callback: {e}")
    
    def _notify_malicious_burst_callbacks(self, burst: BurstEvent):
        """Notifica callbacks de burst malicioso"""
        for callback in self._malicious_burst_callbacks:
            try:
                callback(burst)
            except Exception as e:
                logger.error(f"Error in malicious burst callback: {e}")
    
    def force_cooldown(self, identifier: str, duration: int = 300):
        """Força período de cooldown para um identificador"""
        with self._lock:
            self.cooldown_periods[identifier] = time.time() + duration
            logger.info(f"Forced cooldown for {identifier}: {duration}s")
    
    def get_active_bursts(self) -> Dict[str, BurstEvent]:
        """Obtém bursts ativos"""
        with self._lock:
            return self.active_bursts.copy()
    
    def get_burst_history(self, limit: int = 100) -> List[BurstEvent]:
        """Obtém histórico de bursts"""
        with self._lock:
            return list(self.burst_history)[-limit:] if self.burst_history else []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do burst handler"""
        try:
            with self._lock:
                total_bursts = len(self.burst_history)
                active_bursts = len(self.active_bursts)
                
                burst_types = defaultdict(int)
                for burst in self.burst_history:
                    burst_types[burst.burst_type.value] += 1
                
                return {
                    'total_bursts': total_bursts,
                    'active_bursts': active_bursts,
                    'burst_types': dict(burst_types),
                    'cooldown_periods': len(self.cooldown_periods),
                    'user_configs': len(self.user_configs),
                    'ip_configs': len(self.ip_configs),
                    'is_running': self.is_running,
                    'redis_connected': self._redis_client is not None,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}

# Instância global do burst handler
_burst_handler: Optional[BurstHandler] = None

def get_burst_handler() -> BurstHandler:
    """Obtém instância global do burst handler"""
    global _burst_handler
    if _burst_handler is None:
        raise RuntimeError("Burst handler not initialized")
    return _burst_handler

def initialize_burst_handler(redis_url: str = "redis://localhost:6379", **kwargs) -> BurstHandler:
    """Inicializa burst handler global"""
    global _burst_handler
    if _burst_handler is None:
        _burst_handler = BurstHandler(redis_url, **kwargs)
    return _burst_handler

def shutdown_burst_handler():
    """Desliga burst handler global"""
    global _burst_handler
    if _burst_handler:
        _burst_handler.stop_monitoring()
        _burst_handler = None 