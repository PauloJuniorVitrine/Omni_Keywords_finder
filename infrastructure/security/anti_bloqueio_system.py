"""
Sistema Anti-Bloqueio Avançado - Omni Keywords Finder
Tracing ID: ANTI_BLOQUEIO_20241219_001
Data: 2024-12-19
Versão: 1.0

Implementa estratégias avançadas para evitar bloqueios:
- Rotação de User Agents
- Pool de Proxies Inteligente
- Fingerprinting Evasion
- Behavioral Mimicking
- IP Rotation
- Request Pattern Randomization
- Fallback Strategies
- Geodistributed Requests
"""

import time
import random
import hashlib
import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
from datetime import datetime, timedelta
import socket
import ssl
import urllib.parse
from fake_useragent import UserAgent
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis não disponível. Cache será limitado à memória local.")

try:
    from infrastructure.observability.telemetry import get_telemetry_manager
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logging.warning("Telemetria não disponível. Métricas serão limitadas.")


class BlockingType(Enum):
    """Tipos de bloqueio detectados."""
    RATE_LIMIT = "rate_limit"
    IP_BAN = "ip_ban"
    USER_AGENT_BAN = "user_agent_ban"
    CAPTCHA = "captcha"
    GEO_BLOCK = "geo_block"
    BEHAVIORAL_DETECTION = "behavioral_detection"
    FINGERPRINT_DETECTION = "fingerprint_detection"
    UNKNOWN = "unknown"


class EvasionStrategy(Enum):
    """Estratégias de evasão."""
    USER_AGENT_ROTATION = "user_agent_rotation"
    PROXY_ROTATION = "proxy_rotation"
    IP_ROTATION = "ip_rotation"
    REQUEST_RANDOMIZATION = "request_randomization"
    BEHAVIORAL_MIMICKING = "behavioral_mimicking"
    FINGERPRINT_EVASION = "fingerprint_evasion"
    GEO_DISTRIBUTION = "geo_distribution"
    TIMING_RANDOMIZATION = "timing_randomization"


@dataclass
class ProxyConfig:
    """Configuração de proxy."""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    country: Optional[str] = None
    speed: Optional[float] = None
    last_used: Optional[float] = None
    success_rate: float = 1.0
    fail_count: int = 0
    is_active: bool = True


@dataclass
class UserAgentConfig:
    """Configuração de User Agent."""
    user_agent: str
    browser: str
    version: str
    platform: str
    language: str
    accept_encoding: str
    accept_language: str
    last_used: Optional[float] = None
    success_rate: float = 1.0
    fail_count: int = 0
    is_active: bool = True


@dataclass
class RequestPattern:
    """Padrão de requisição para behavioral mimicking."""
    method: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    timing: Dict[str, float]
    mouse_movements: List[Tuple[float, float]]
    scroll_patterns: List[float]
    click_patterns: List[Tuple[float, float, float]]


@dataclass
class BlockingEvent:
    """Evento de bloqueio detectado."""
    blocking_type: BlockingType
    timestamp: float
    url: str
    user_agent: str
    proxy: Optional[str]
    ip_address: str
    response_code: int
    response_text: str
    headers: Dict[str, str]
    request_data: Dict[str, Any]
    strategy_used: EvasionStrategy
    severity: float = 1.0


class UserAgentRotator:
    """
    Sistema de rotação inteligente de User Agents.
    """
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self.user_agents: List[UserAgentConfig] = []
        self.current_index = 0
        self.lock = threading.Lock()
        self.last_rotation = time.time()
        self.rotation_interval = 300  # 5 minutos
        
        # User Agents realistas
        self._initialize_user_agents()
        
    def _initialize_user_agents(self):
        """Inicializa lista de User Agents realistas."""
        self.user_agents = [
            UserAgentConfig(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser="Chrome",
                version="120.0.0.0",
                platform="Windows",
                language="en-US,en;q=0.9",
                accept_encoding="gzip, deflate, br",
                accept_language="en-US,en;q=0.9"
            ),
            UserAgentConfig(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser="Chrome",
                version="120.0.0.0",
                platform="MacOS",
                language="en-US,en;q=0.9",
                accept_encoding="gzip, deflate, br",
                accept_language="en-US,en;q=0.9"
            ),
            UserAgentConfig(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                browser="Firefox",
                version="121.0",
                platform="Windows",
                language="en-US,en;q=0.5",
                accept_encoding="gzip, deflate, br",
                accept_language="en-US,en;q=0.5"
            ),
            UserAgentConfig(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                browser="Safari",
                version="17.1",
                platform="MacOS",
                language="en-US,en;q=0.9",
                accept_encoding="gzip, deflate, br",
                accept_language="en-US,en;q=0.9"
            ),
            UserAgentConfig(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                browser="Chrome",
                version="120.0.0.0",
                platform="Linux",
                language="en-US,en;q=0.9",
                accept_encoding="gzip, deflate, br",
                accept_language="en-US,en;q=0.9"
            )
        ]
    
    def get_user_agent(self) -> UserAgentConfig:
        """Obtém um User Agent da lista com rotação inteligente."""
        with self.lock:
            # Verifica se precisa rotacionar
            if time.time() - self.last_rotation > self.rotation_interval:
                self.current_index = (self.current_index + 1) % len(self.user_agents)
                self.last_rotation = time.time()
            
            # Seleciona User Agent baseado em sucesso
            available_agents = [ua for ua in self.user_agents if ua.is_active]
            if not available_agents:
                # Reativa todos se nenhum estiver disponível
                for ua in self.user_agents:
                    ua.is_active = True
                available_agents = self.user_agents
            
            # Seleciona baseado em taxa de sucesso
            best_agent = max(available_agents, key=lambda ua: ua.success_rate)
            best_agent.last_used = time.time()
            
            return best_agent
    
    def mark_success(self, user_agent: str):
        """Marca sucesso para um User Agent."""
        with self.lock:
            for ua in self.user_agents:
                if ua.user_agent == user_agent:
                    ua.success_rate = min(1.0, ua.success_rate + 0.1)
                    ua.fail_count = max(0, ua.fail_count - 1)
                    break
    
    def mark_failure(self, user_agent: str):
        """Marca falha para um User Agent."""
        with self.lock:
            for ua in self.user_agents:
                if ua.user_agent == user_agent:
                    ua.success_rate = max(0.0, ua.success_rate - 0.2)
                    ua.fail_count += 1
                    
                    # Desativa se muitas falhas
                    if ua.fail_count >= 5:
                        ua.is_active = False
                    break


class ProxyRotator:
    """
    Sistema de rotação inteligente de proxies.
    """
    
    def __init__(self, proxy_list: List[Dict[str, Any]] = None):
        self.proxies: List[ProxyConfig] = []
        self.current_index = 0
        self.lock = threading.Lock()
        self.last_rotation = time.time()
        self.rotation_interval = 60  # 1 minuto
        
        if proxy_list:
            self._initialize_proxies(proxy_list)
        else:
            self._load_default_proxies()
    
    def _initialize_proxies(self, proxy_list: List[Dict[str, Any]]):
        """Inicializa lista de proxies."""
        for proxy_data in proxy_list:
            proxy = ProxyConfig(
                host=proxy_data["host"],
                port=proxy_data["port"],
                username=proxy_data.get("username"),
                password=proxy_data.get("password"),
                protocol=proxy_data.get("protocol", "http"),
                country=proxy_data.get("country"),
                speed=proxy_data.get("speed")
            )
            self.proxies.append(proxy)
    
    def _load_default_proxies(self):
        """Carrega proxies padrão (vazio para desenvolvimento)."""
        # Em produção, carregaria de serviço de proxy
        pass
    
    def get_proxy(self) -> Optional[ProxyConfig]:
        """Obtém um proxy da lista com rotação inteligente."""
        with self.lock:
            if not self.proxies:
                return None
            
            # Verifica se precisa rotacionar
            if time.time() - self.last_rotation > self.rotation_interval:
                self.current_index = (self.current_index + 1) % len(self.proxies)
                self.last_rotation = time.time()
            
            # Seleciona proxy baseado em sucesso
            available_proxies = [p for p in self.proxies if p.is_active]
            if not available_proxies:
                # Reativa todos se nenhum estiver disponível
                for proxy in self.proxies:
                    proxy.is_active = True
                available_proxies = self.proxies
            
            # Seleciona baseado em taxa de sucesso e velocidade
            best_proxy = max(available_proxies, 
                           key=lambda p: p.success_rate * (p.speed or 1.0))
            best_proxy.last_used = time.time()
            
            return best_proxy
    
    def mark_success(self, proxy_host: str):
        """Marca sucesso para um proxy."""
        with self.lock:
            for proxy in self.proxies:
                if proxy.host == proxy_host:
                    proxy.success_rate = min(1.0, proxy.success_rate + 0.1)
                    proxy.fail_count = max(0, proxy.fail_count - 1)
                    break
    
    def mark_failure(self, proxy_host: str):
        """Marca falha para um proxy."""
        with self.lock:
            for proxy in self.proxies:
                if proxy.host == proxy_host:
                    proxy.success_rate = max(0.0, proxy.success_rate - 0.2)
                    proxy.fail_count += 1
                    
                    # Desativa se muitas falhas
                    if proxy.fail_count >= 3:
                        proxy.is_active = False
                    break


class BehavioralMimicker:
    """
    Sistema de imitação de comportamento humano.
    """
    
    def __init__(self):
        self.patterns: Dict[str, RequestPattern] = {}
        self.session_data: Dict[str, Any] = {}
        
    def generate_human_headers(self, user_agent_config: UserAgentConfig) -> Dict[str, str]:
        """Gera headers que simulam comportamento humano."""
        headers = {
            "User-Agent": user_agent_config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": user_agent_config.accept_language,
            "Accept-Encoding": user_agent_config.accept_encoding,
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        # Adiciona headers específicos do browser
        if "Chrome" in user_agent_config.browser:
            headers.update({
                "Sec-Ch-Ua": '"Not_A Brand";value="8", "Chromium";value="120", "Google Chrome";value="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": f'"{user_agent_config.platform}"'
            })
        
        return headers
    
    def generate_random_delay(self, base_delay: float = 1.0) -> float:
        """Gera delay aleatório que simula comportamento humano."""
        # Distribuição normal com média base_delay e desvio padrão 0.3
        delay = random.gauss(base_delay, 0.3)
        return max(0.1, delay)  # Mínimo 0.1 segundos
    
    def simulate_mouse_movement(self) -> List[Tuple[float, float]]:
        """Simula movimento do mouse."""
        movements = []
        value, result = random.randint(0, 1920), random.randint(0, 1080)
        
        for _ in range(random.randint(3, 8)):
            value += random.randint(-50, 50)
            result += random.randint(-50, 50)
            movements.append((value, result))
        
        return movements
    
    def simulate_scroll_pattern(self) -> List[float]:
        """Simula padrão de scroll."""
        scrolls = []
        current_scroll = 0
        
        for _ in range(random.randint(2, 5)):
            scroll_amount = random.randint(100, 500)
            current_scroll += scroll_amount
            scrolls.append(current_scroll)
        
        return scrolls


class FingerprintEvader:
    """
    Sistema de evasão de fingerprinting.
    """
    
    def __init__(self):
        self.canvas_fingerprints: Set[str] = set()
        self.webgl_fingerprints: Set[str] = set()
        self.audio_fingerprints: Set[str] = set()
        
    def generate_canvas_fingerprint(self) -> str:
        """Gera fingerprint de canvas único."""
        # Simula canvas fingerprint único
        components = [
            str(random.randint(1000, 9999)),  # Canvas width
            str(random.randint(1000, 9999)),  # Canvas height
            str(random.randint(1, 100)),      # Color depth
            str(random.randint(1, 100))       # Pixel depth
        ]
        return hashlib.md5("".join(components).encode()).hexdigest()
    
    def generate_webgl_fingerprint(self) -> str:
        """Gera fingerprint de WebGL único."""
        # Simula WebGL fingerprint único
        components = [
            f"vendor_{random.randint(1, 10)}",
            f"renderer_{random.randint(1, 10)}",
            str(random.randint(1000, 9999))   # Max texture size
        ]
        return hashlib.md5("".join(components).encode()).hexdigest()
    
    def generate_audio_fingerprint(self) -> str:
        """Gera fingerprint de áudio único."""
        # Simula audio fingerprint único
        components = [
            str(random.randint(1, 100)),      # Sample rate
            str(random.randint(1, 100)),      # Channel count
            str(random.randint(1, 100))       # Buffer size
        ]
        return hashlib.md5("".join(components).encode()).hexdigest()


class AntiBloqueioSystem:
    """
    Sistema principal de anti-bloqueio.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.user_agent_rotator = UserAgentRotator()
        self.proxy_rotator = ProxyRotator()
        self.behavioral_mimicker = BehavioralMimicker()
        self.fingerprint_evader = FingerprintEvader()
        
        # Cache de bloqueios
        self.blocking_events: List[BlockingEvent] = []
        self.blocked_domains: Set[str] = set()
        self.blocked_ips: Set[str] = set()
        
        # Métricas
        self.request_count = 0
        self.blocking_count = 0
        self.success_count = 0
        
        # Telemetria
        if TELEMETRY_AVAILABLE:
            self.telemetry = get_telemetry_manager()
        else:
            self.telemetry = None
        
        # Redis para cache distribuído
        if REDIS_AVAILABLE:
            self.redis_client = redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0)
            )
        else:
            self.redis_client = None
    
    async def make_request(self, url: str, method: str = "GET", 
                          headers: Optional[Dict[str, str]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          timeout: int = 30) -> Tuple[bool, Dict[str, Any]]:
        """
        Faz requisição com proteção anti-bloqueio.
        
        Args:
            url: URL da requisição
            method: Método HTTP
            headers: Headers customizados
            data: Dados da requisição
            timeout: Timeout em segundos
            
        Returns:
            Tuple (sucesso, dados_resposta)
        """
        self.request_count += 1
        
        # Verifica se domínio está bloqueado
        domain = self._extract_domain(url)
        if domain in self.blocked_domains:
            return False, {"error": "Domain blocked", "domain": domain}
        
        # Obtém User Agent
        user_agent_config = self.user_agent_rotator.get_user_agent()
        
        # Obtém proxy
        proxy_config = self.proxy_rotator.get_proxy()
        
        # Gera headers humanos
        human_headers = self.behavioral_mimicker.generate_human_headers(user_agent_config)
        if headers:
            human_headers.update(headers)
        
        # Gera delay humano
        delay = self.behavioral_mimicker.generate_random_delay()
        await asyncio.sleep(delay)
        
        try:
            # Configura proxy
            proxy_url = None
            if proxy_config:
                if proxy_config.username and proxy_config.password:
                    proxy_url = f"{proxy_config.protocol}://{proxy_config.username}:{proxy_config.password}@{proxy_config.host}:{proxy_config.port}"
                else:
                    proxy_url = f"{proxy_config.protocol}://{proxy_config.host}:{proxy_config.port}"
            
            # Faz requisição
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=human_headers,
                    data=data,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    
                    response_data = {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "text": await response.text(),
                        "url": str(response.url)
                    }
                    
                    # Verifica se foi bloqueado
                    if self._is_blocked(response_data):
                        blocking_event = BlockingEvent(
                            blocking_type=self._detect_blocking_type(response_data),
                            timestamp=time.time(),
                            url=url,
                            user_agent=user_agent_config.user_agent,
                            proxy=proxy_url,
                            ip_address=self._get_client_ip(),
                            response_code=response.status,
                            response_text=response_data["text"],
                            headers=response_data["headers"],
                            request_data={"method": method, "data": data},
                            strategy_used=EvasionStrategy.USER_AGENT_ROTATION
                        )
                        
                        self._handle_blocking_event(blocking_event)
                        
                        # Marca falhas
                        self.user_agent_rotator.mark_failure(user_agent_config.user_agent)
                        if proxy_config:
                            self.proxy_rotator.mark_failure(proxy_config.host)
                        
                        return False, response_data
                    
                    # Sucesso
                    self.success_count += 1
                    self.user_agent_rotator.mark_success(user_agent_config.user_agent)
                    if proxy_config:
                        self.proxy_rotator.mark_success(proxy_config.host)
                    
                    return True, response_data
                    
        except Exception as e:
            # Erro de conexão
            if proxy_config:
                self.proxy_rotator.mark_failure(proxy_config.host)
            
            return False, {"error": str(e)}
    
    def _extract_domain(self, url: str) -> str:
        """Extrai domínio da URL."""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc
        except:
            return url
    
    def _is_blocked(self, response_data: Dict[str, Any]) -> bool:
        """Verifica se a resposta indica bloqueio."""
        status = response_data.get("status", 200)
        text = response_data.get("text", "").lower()
        headers = response_data.get("headers", {})
        
        # Códigos de status que indicam bloqueio
        blocking_statuses = [403, 429, 503, 509]
        if status in blocking_statuses:
            return True
        
        # Textos que indicam bloqueio
        blocking_texts = [
            "blocked", "forbidden", "rate limit", "too many requests",
            "captcha", "robot", "bot", "suspicious", "unusual activity",
            "temporarily unavailable", "service unavailable"
        ]
        
        for blocking_text in blocking_texts:
            if blocking_text in text:
                return True
        
        # Headers que indicam bloqueio
        blocking_headers = [
            "value-ratelimit-remaining",
            "retry-after",
            "value-blocked"
        ]
        
        for header in blocking_headers:
            if header in headers:
                return True
        
        return False
    
    def _detect_blocking_type(self, response_data: Dict[str, Any]) -> BlockingType:
        """Detecta o tipo de bloqueio."""
        status = response_data.get("status", 200)
        text = response_data.get("text", "").lower()
        
        if status == 429:
            return BlockingType.RATE_LIMIT
        elif status == 403:
            return BlockingType.IP_BAN
        elif "captcha" in text:
            return BlockingType.CAPTCHA
        elif "geo" in text or "location" in text:
            return BlockingType.GEO_BLOCK
        elif "fingerprint" in text or "browser" in text:
            return BlockingType.FINGERPRINT_DETECTION
        else:
            return BlockingType.UNKNOWN
    
    def _handle_blocking_event(self, event: BlockingEvent):
        """Processa evento de bloqueio."""
        self.blocking_count += 1
        self.blocking_events.append(event)
        
        # Adiciona domínio à lista de bloqueados se necessário
        if event.blocking_type in [BlockingType.IP_BAN, BlockingType.GEO_BLOCK]:
            domain = self._extract_domain(event.url)
            self.blocked_domains.add(domain)
        
        # Log do evento
        logging.warning(f"Blocking event detected: {event.blocking_type.value} for {event.url}")
        
        # Telemetria
        if self.telemetry:
            self.telemetry.record_event("blocking_detected", {
                "blocking_type": event.blocking_type.value,
                "url": event.url,
                "severity": event.severity
            })
    
    def _get_client_ip(self) -> str:
        """Obtém IP do cliente (simulado)."""
        return "127.0.0.1"  # Em produção, obteria IP real
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema."""
        return {
            "total_requests": self.request_count,
            "successful_requests": self.success_count,
            "blocked_requests": self.blocking_count,
            "success_rate": self.success_count / max(1, self.request_count),
            "blocked_domains": len(self.blocked_domains),
            "blocked_ips": len(self.blocked_ips),
            "recent_blocking_events": len([e for e in self.blocking_events 
                                         if time.time() - e.timestamp < 3600])
        }
    
    def add_proxy(self, proxy_data: Dict[str, Any]):
        """Adiciona proxy à lista."""
        proxy = ProxyConfig(
            host=proxy_data["host"],
            port=proxy_data["port"],
            username=proxy_data.get("username"),
            password=proxy_data.get("password"),
            protocol=proxy_data.get("protocol", "http"),
            country=proxy_data.get("country")
        )
        self.proxy_rotator.proxies.append(proxy)
    
    def remove_blocked_domain(self, domain: str):
        """Remove domínio da lista de bloqueados."""
        self.blocked_domains.discard(domain)
    
    def clear_blocking_history(self):
        """Limpa histórico de bloqueios."""
        self.blocking_events.clear()
        self.blocked_domains.clear()
        self.blocked_ips.clear()


# Instância global
_anti_bloqueio_system = None

def get_anti_bloqueio_system() -> AntiBloqueioSystem:
    """Obtém instância global do sistema anti-bloqueio."""
    global _anti_bloqueio_system
    if _anti_bloqueio_system is None:
        _anti_bloqueio_system = AntiBloqueioSystem()
    return _anti_bloqueio_system

def initialize_anti_bloqueio_system(config: Optional[Dict[str, Any]] = None) -> AntiBloqueioSystem:
    """Inicializa sistema anti-bloqueio com configuração."""
    global _anti_bloqueio_system
    _anti_bloqueio_system = AntiBloqueioSystem(config)
    return _anti_bloqueio_system


# Decorator para proteção automática
def anti_bloqueio_protected(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator para proteção automática contra bloqueios.
    
    Args:
        max_retries: Número máximo de tentativas
        base_delay: Delay base entre tentativas
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            system = get_anti_bloqueio_system()
            
            for attempt in range(max_retries):
                try:
                    # Faz requisição protegida
                    if "url" in kwargs:
                        success, result = await system.make_request(
                            url=kwargs["url"],
                            method=kwargs.get("method", "GET"),
                            headers=kwargs.get("headers"),
                            data=kwargs.get("data"),
                            timeout=kwargs.get("timeout", 30)
                        )
                        
                        if success:
                            return result
                        else:
                            # Aguarda antes da próxima tentativa
                            delay = base_delay * (2 ** attempt)
                            await asyncio.sleep(delay)
                    else:
                        # Se não é requisição HTTP, executa função normalmente
                        return await func(*args, **kwargs)
                        
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
            
            return None
        
        return wrapper
    return decorator 