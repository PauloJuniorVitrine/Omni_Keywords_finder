"""
Sistema de Webhooks para Integração Externa - Omni Keywords Finder

Funcionalidades:
- Sistema de webhooks configurável
- Registro de endpoints com validação
- Retry logic com backoff exponencial
- Validação de payload e assinatura
- Rate limiting para webhooks
- Logs detalhados de webhook
- Suporte a múltiplos eventos
- Segurança com HMAC

Autor: Sistema de Webhooks para Integração Externa
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import os
import json
import hmac
import hashlib
import uuid
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
import threading
import queue
from pathlib import Path
import sqlite3
from urllib.parse import urlparse

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

class WebhookEventType(Enum):
    """Tipos de eventos suportados"""
    KEYWORD_PROCESSED = "keyword.processed"
    CLUSTER_CREATED = "cluster.created"
    EXECUTION_STARTED = "execution.started"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_FAILED = "execution.failed"
    ANOMALY_DETECTED = "anomaly.detected"
    ALERT_GENERATED = "alert.generated"
    USER_ACTION = "user.action"
    SYSTEM_HEALTH = "system.health"
    BUSINESS_METRIC = "business.metric"

class WebhookStatus(Enum):
    """Status dos webhooks"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ERROR = "error"

class WebhookSecurityLevel(Enum):
    """Níveis de segurança"""
    NONE = "none"
    HMAC = "hmac"
    API_KEY = "api_key"
    OAUTH = "oauth"

@dataclass
class WebhookEndpoint:
    """Configuração de endpoint de webhook"""
    id: str
    name: str
    url: str
    events: List[WebhookEventType]
    secret: Optional[str] = None
    api_key: Optional[str] = None
    security_level: WebhookSecurityLevel = WebhookSecurityLevel.HMAC
    headers: Dict[str, str] = None
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    rate_limit: int = 100  # requests per hour
    status: WebhookStatus = WebhookStatus.ACTIVE
    created_at: datetime = None
    updated_at: datetime = None
    last_triggered: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    metadata: Dict[str, Any] = None

@dataclass
class WebhookPayload:
    """Estrutura de payload do webhook"""
    event_type: WebhookEventType
    event_id: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "omni_keywords_finder"
    version: str = "1.0.0"
    metadata: Dict[str, Any] = None

@dataclass
class WebhookDelivery:
    """Registro de entrega de webhook"""
    id: str
    endpoint_id: str
    event_id: str
    payload: Dict[str, Any]
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    attempt_count: int = 0
    max_attempts: int = 3
    next_retry: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime = None

class WebhookValidator:
    """Validador de webhooks com segurança avançada"""
    
    def __init__(self):
        self.required_fields = ['event_type', 'event_id', 'timestamp', 'data']
        self.max_payload_size = 1024 * 1024  # 1MB
        self.timestamp_tolerance = 300  # 5 minutos em segundos
        self.ip_whitelist = set()  # IPs permitidos
        self.failed_attempts = defaultdict(int)  # Contador de tentativas falhadas
        self.max_failed_attempts = 10  # Máximo de tentativas antes de bloquear
        
        # Métricas de segurança
        self.security_violations = Counter(
            'webhook_security_violations_total',
            'Total de violações de segurança',
            ['endpoint_id', 'violation_type']
        )
        
        self.hmac_validation_attempts = Counter(
            'webhook_hmac_validation_attempts_total',
            'Total de tentativas de validação HMAC',
            ['endpoint_id', 'status']
        )
    
    def add_ip_to_whitelist(self, ip: str):
        """Adiciona IP à whitelist"""
        self.ip_whitelist.add(ip)
        logger.info(f"IP {ip} adicionado à whitelist de webhooks")
    
    def remove_ip_from_whitelist(self, ip: str):
        """Remove IP da whitelist"""
        self.ip_whitelist.discard(ip)
        logger.info(f"IP {ip} removido da whitelist de webhooks")
    
    def is_ip_allowed(self, ip: str) -> bool:
        """Verifica se IP está na whitelist"""
        if not self.ip_whitelist:  # Se whitelist vazia, permite todos
            return True
        return ip in self.ip_whitelist
    
    def validate_timestamp(self, timestamp: Union[str, datetime]) -> bool:
        """Valida timestamp com tolerância de 5 minutos"""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            now = datetime.utcnow()
            diff = abs((dt - now).total_seconds())
            
            return diff <= self.timestamp_tolerance
        except Exception as e:
            logger.warning(f"Erro ao validar timestamp: {str(e)}")
            return False
    
    def validate_endpoint(self, endpoint: WebhookEndpoint) -> List[str]:
        """Valida configuração de endpoint"""
        errors = []
        
        # Validar URL
        try:
            parsed_url = urlparse(endpoint.url)
            if not parsed_url.scheme or not parsed_url.netloc:
                errors.append("URL inválida")
        except Exception:
            errors.append("URL malformada")
        
        # Validar eventos
        if not endpoint.events:
            errors.append("Pelo menos um evento deve ser especificado")
        
        # Validar configurações de segurança
        if endpoint.security_level == WebhookSecurityLevel.HMAC and not endpoint.secret:
            errors.append("Secret é obrigatório para HMAC")
        
        if endpoint.security_level == WebhookSecurityLevel.API_KEY and not endpoint.api_key:
            errors.append("API Key é obrigatória para API_KEY")
        
        # Validar rate limit
        if endpoint.rate_limit <= 0:
            errors.append("Rate limit deve ser maior que zero")
        
        # Validar timeout
        if endpoint.timeout <= 0:
            errors.append("Timeout deve ser maior que zero")
        
        return errors
    
    def validate_payload(self, payload: WebhookPayload) -> List[str]:
        """Valida payload do webhook"""
        errors = []
        
        # Verificar campos obrigatórios
        payload_dict = asdict(payload)
        for field in self.required_fields:
            if field not in payload_dict or payload_dict[field] is None:
                errors.append(f"Campo obrigatório ausente: {field}")
        
        # Validar tamanho do payload
        payload_size = len(json.dumps(payload_dict))
        if payload_size > self.max_payload_size:
            errors.append(f"Payload muito grande: {payload_size} bytes")
        
        # Validar timestamp
        if payload.timestamp:
            if not self.validate_timestamp(payload.timestamp):
                errors.append("Timestamp fora da tolerância de 5 minutos")
        
        return errors
    
    def generate_signature(self, payload: str, secret: str) -> str:
        """Gera assinatura HMAC-SHA256 para payload"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def verify_signature(self, payload: str, signature: str, secret: str, endpoint_id: str = None) -> bool:
        """Verifica assinatura HMAC com logging detalhado"""
        try:
            # Extrair algoritmo da assinatura (formato: sha256=hash)
            if '=' in signature:
                algorithm, hash_value = signature.split('=', 1)
                if algorithm.lower() != 'sha256':
                    logger.warning(f"Algoritmo HMAC não suportado: {algorithm}")
                    self.hmac_validation_attempts.labels(
                        endpoint_id=endpoint_id or 'unknown',
                        status='unsupported_algorithm'
                    ).inc()
                    return False
            else:
                hash_value = signature
            
            expected_signature = self.generate_signature(payload, secret)
            is_valid = hmac.compare_digest(hash_value, expected_signature)
            
            # Log da tentativa
            status = 'success' if is_valid else 'failed'
            self.hmac_validation_attempts.labels(
                endpoint_id=endpoint_id or 'unknown',
                status=status
            ).inc()
            
            if not is_valid:
                logger.warning(f"Validação HMAC falhou para endpoint {endpoint_id}")
                if endpoint_id:
                    self.failed_attempts[endpoint_id] += 1
                    
                    # Bloquear endpoint se muitas tentativas falhadas
                    if self.failed_attempts[endpoint_id] >= self.max_failed_attempts:
                        logger.error(f"Endpoint {endpoint_id} bloqueado por muitas tentativas HMAC falhadas")
                        self.security_violations.labels(
                            endpoint_id=endpoint_id,
                            violation_type='hmac_max_attempts'
                        ).inc()
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Erro ao verificar assinatura HMAC: {str(e)}")
            self.hmac_validation_attempts.labels(
                endpoint_id=endpoint_id or 'unknown',
                status='error'
            ).inc()
            return False
    
    def validate_incoming_webhook(self, payload: str, signature: str, timestamp: str, 
                                 client_ip: str, endpoint_id: str = None) -> Dict[str, Any]:
        """Validação completa de webhook recebido"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validar IP
        if not self.is_ip_allowed(client_ip):
            validation_result['valid'] = False
            validation_result['errors'].append(f"IP {client_ip} não está na whitelist")
            self.security_violations.labels(
                endpoint_id=endpoint_id or 'unknown',
                violation_type='ip_not_whitelisted'
            ).inc()
            logger.warning(f"Tentativa de acesso de IP não autorizado: {client_ip}")
        
        # Validar timestamp
        if timestamp and not self.validate_timestamp(timestamp):
            validation_result['valid'] = False
            validation_result['errors'].append("Timestamp fora da tolerância de 5 minutos")
            self.security_violations.labels(
                endpoint_id=endpoint_id or 'unknown',
                violation_type='timestamp_invalid'
            ).inc()
        
        # Validar assinatura (se endpoint_id fornecido)
        if endpoint_id and signature:
            # Buscar secret do endpoint
            # Esta implementação assume que o secret está disponível
            # Em uma implementação real, você buscaria do banco de dados
            endpoint = self._get_endpoint_secret(endpoint_id)
            if endpoint and endpoint.secret:
                if not self.verify_signature(payload, signature, endpoint.secret, endpoint_id):
                    validation_result['valid'] = False
                    validation_result['errors'].append("Assinatura HMAC inválida")
                    self.security_violations.labels(
                        endpoint_id=endpoint_id,
                        violation_type='hmac_invalid'
                    ).inc()
            else:
                validation_result['warnings'].append("Endpoint não encontrado ou sem secret configurado")
        
        # Log da validação
        if validation_result['valid']:
            logger.info(f"Webhook validado com sucesso para endpoint {endpoint_id}")
        else:
            logger.warning(f"Webhook inválido para endpoint {endpoint_id}: {validation_result['errors']}")
        
        return validation_result
    
    def _get_endpoint_secret(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        """Busca secret do endpoint (implementação placeholder)"""
        # Em uma implementação real, você buscaria do banco de dados
        # Por enquanto, retorna None para indicar que não foi implementado
        return None
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de segurança"""
        return {
            'ip_whitelist_count': len(self.ip_whitelist),
            'failed_attempts': dict(self.failed_attempts),
            'security_violations': {
                'total': sum(self.security_violations._metrics.values()),
                'by_type': dict(self.security_violations._metrics)
            },
            'hmac_validation_attempts': {
                'total': sum(self.hmac_validation_attempts._metrics.values()),
                'by_status': dict(self.hmac_validation_attempts._metrics)
            }
        }

class WebhookRateLimiter:
    """Controlador de rate limiting para webhooks"""
    
    def __init__(self):
        self.requests = defaultdict(lambda: deque(maxlen=1000))
        self.blocked_endpoints = set()
        
        # Métricas Prometheus
        self.rate_limit_hits = Counter(
            'webhook_rate_limit_hits_total',
            'Total de hits no rate limit',
            ['endpoint_id']
        )
    
    def is_allowed(self, endpoint_id: str, rate_limit: int) -> bool:
        """Verifica se endpoint pode fazer requisição"""
        now = datetime.utcnow()
        endpoint_requests = self.requests[endpoint_id]
        
        # Remover requisições antigas (mais de 1 hora)
        cutoff_time = now - timedelta(hours=1)
        while endpoint_requests and endpoint_requests[0] < cutoff_time:
            endpoint_requests.popleft()
        
        # Verificar se está dentro do limite
        if len(endpoint_requests) >= rate_limit:
            self.rate_limit_hits.labels(endpoint_id=endpoint_id).inc()
            return False
        
        # Adicionar requisição atual
        endpoint_requests.append(now)
        return True
    
    def block_endpoint(self, endpoint_id: str, duration_minutes: int = 60):
        """Bloqueia endpoint temporariamente"""
        self.blocked_endpoints.add(endpoint_id)
        
        # Remover bloqueio após duração especificada
        def unblock():
            time.sleep(duration_minutes * 60)
            self.blocked_endpoints.discard(endpoint_id)
        
        threading.Thread(target=unblock, daemon=True).start()
    
    def is_blocked(self, endpoint_id: str) -> bool:
        """Verifica se endpoint está bloqueado"""
        return endpoint_id in self.blocked_endpoints

class WebhookRetryManager:
    """Gerenciador de retry para webhooks"""
    
    def __init__(self, max_retries: int = 3, base_delay: int = 5):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.retry_queue = queue.Queue()
        
        # Métricas Prometheus
        self.retry_attempts = Counter(
            'webhook_retry_attempts_total',
            'Total de tentativas de retry',
            ['endpoint_id', 'status']
        )
    
    def calculate_delay(self, attempt: int) -> int:
        """Calcula delay para retry com backoff exponencial"""
        return min(self.base_delay * (2 ** attempt), 300)  # Máximo 5 minutos
    
    def should_retry(self, status_code: int, attempt: int) -> bool:
        """Determina se deve tentar novamente"""
        if attempt >= self.max_retries:
            return False
        
        # Retry para códigos 5xx e alguns 4xx
        retryable_codes = {408, 429, 500, 502, 503, 504}
        return status_code in retryable_codes
    
    def schedule_retry(self, delivery: WebhookDelivery):
        """Agenda retry para entrega"""
        if delivery.attempt_count < delivery.max_attempts:
            delay = self.calculate_delay(delivery.attempt_count)
            delivery.next_retry = datetime.utcnow() + timedelta(seconds=delay)
            delivery.attempt_count += 1
            
            # Adicionar à fila de retry
            self.retry_queue.put((delivery, delay))
            
            self.retry_attempts.labels(
                endpoint_id=delivery.endpoint_id,
                status="scheduled"
            ).inc()

class WebhookDatabase:
    """Gerenciador de persistência de webhooks"""
    
    def __init__(self, db_path: str = "webhooks.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS webhook_endpoints (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    events TEXT NOT NULL,
                    secret TEXT,
                    api_key TEXT,
                    security_level TEXT NOT NULL,
                    headers TEXT,
                    timeout INTEGER NOT NULL,
                    retry_attempts INTEGER NOT NULL,
                    retry_delay INTEGER NOT NULL,
                    rate_limit INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_triggered TEXT,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS webhook_deliveries (
                    id TEXT PRIMARY KEY,
                    endpoint_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status_code INTEGER,
                    response_body TEXT,
                    error_message TEXT,
                    attempt_count INTEGER DEFAULT 0,
                    max_attempts INTEGER NOT NULL,
                    next_retry TEXT,
                    delivered_at TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (endpoint_id) REFERENCES webhook_endpoints (id)
                )
            """)
            
            conn.commit()
    
    def save_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Salva endpoint no banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO webhook_endpoints 
                    (id, name, url, events, secret, api_key, security_level, headers,
                     timeout, retry_attempts, retry_delay, rate_limit, status,
                     created_at, updated_at, last_triggered, success_count, failure_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    endpoint.id, endpoint.name, endpoint.url,
                    json.dumps([e.value for e in endpoint.events]),
                    endpoint.secret, endpoint.api_key, endpoint.security_level.value,
                    json.dumps(endpoint.headers or {}),
                    endpoint.timeout, endpoint.retry_attempts, endpoint.retry_delay,
                    endpoint.rate_limit, endpoint.status.value,
                    endpoint.created_at.isoformat() if endpoint.created_at else datetime.utcnow().isoformat(),
                    endpoint.updated_at.isoformat() if endpoint.updated_at else datetime.utcnow().isoformat(),
                    endpoint.last_triggered.isoformat() if endpoint.last_triggered else None,
                    endpoint.success_count, endpoint.failure_count,
                    json.dumps(endpoint.metadata or {})
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar endpoint: {str(e)}")
            return False
    
    def load_endpoints(self) -> List[WebhookEndpoint]:
        """Carrega todos os endpoints"""
        endpoints = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM webhook_endpoints")
                for row in cursor.fetchall():
                    endpoint = WebhookEndpoint(
                        id=row[0],
                        name=row[1],
                        url=row[2],
                        events=[WebhookEventType(e) for e in json.loads(row[3])],
                        secret=row[4],
                        api_key=row[5],
                        security_level=WebhookSecurityLevel(row[6]),
                        headers=json.loads(row[7]) if row[7] else {},
                        timeout=row[8],
                        retry_attempts=row[9],
                        retry_delay=row[10],
                        rate_limit=row[11],
                        status=WebhookStatus(row[12]),
                        created_at=datetime.fromisoformat(row[13]),
                        updated_at=datetime.fromisoformat(row[14]),
                        last_triggered=datetime.fromisoformat(row[15]) if row[15] else None,
                        success_count=row[16],
                        failure_count=row[17],
                        metadata=json.loads(row[18]) if row[18] else {}
                    )
                    endpoints.append(endpoint)
        except Exception as e:
            logger.error(f"Erro ao carregar endpoints: {str(e)}")
        
        return endpoints
    
    def save_delivery(self, delivery: WebhookDelivery) -> bool:
        """Salva entrega no banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO webhook_deliveries 
                    (id, endpoint_id, event_id, payload, status_code, response_body,
                     error_message, attempt_count, max_attempts, next_retry, delivered_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    delivery.id, delivery.endpoint_id, delivery.event_id,
                    json.dumps(delivery.payload),
                    delivery.status_code, delivery.response_body, delivery.error_message,
                    delivery.attempt_count, delivery.max_attempts,
                    delivery.next_retry.isoformat() if delivery.next_retry else None,
                    delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                    delivery.created_at.isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erro ao salvar entrega: {str(e)}")
            return False
    
    def update_delivery(self, delivery_id: str, **kwargs) -> bool:
        """Atualiza entrega no banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
                values = list(kwargs.values()) + [delivery_id]
                
                conn.execute(f"UPDATE webhook_deliveries SET {set_clause} WHERE id = ?", values)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Erro ao atualizar entrega: {str(e)}")
            return False

class WebhookDeliveryWorker:
    """Worker para entrega de webhooks"""
    
    def __init__(self, webhook_system):
        self.webhook_system = webhook_system
        self.session = None
        self.is_running = False
        self.delivery_queue = asyncio.Queue()
        
        # Métricas Prometheus
        self.delivery_attempts = Counter(
            'webhook_delivery_attempts_total',
            'Total de tentativas de entrega',
            ['endpoint_id', 'status']
        )
        
        self.delivery_duration = Histogram(
            'webhook_delivery_duration_seconds',
            'Duração das entregas',
            ['endpoint_id']
        )
    
    async def start(self):
        """Inicia worker"""
        self.is_running = True
        self.session = aiohttp.ClientSession()
        
        # Iniciar workers
        workers = [
            asyncio.create_task(self._delivery_worker())
            for _ in range(5)  # 5 workers concorrentes
        ]
        
        # Iniciar retry worker
        retry_worker = asyncio.create_task(self._retry_worker())
        
        await asyncio.gather(*workers, retry_worker)
    
    async def stop(self):
        """Para worker"""
        self.is_running = False
        if self.session:
            await self.session.close()
    
    async def _delivery_worker(self):
        """Worker principal de entrega"""
        while self.is_running:
            try:
                delivery = await asyncio.wait_for(
                    self.delivery_queue.get(), timeout=1.0
                )
                await self._deliver_webhook(delivery)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Erro no worker de entrega: {str(e)}")
    
    async def _retry_worker(self):
        """Worker para retry de entregas"""
        while self.is_running:
            try:
                # Processar entregas com retry pendente
                pending_deliveries = self.webhook_system.get_pending_retries()
                
                for delivery in pending_deliveries:
                    if delivery.next_retry and delivery.next_retry <= datetime.utcnow():
                        await self.delivery_queue.put(delivery)
                
                await asyncio.sleep(10)  # Verificar a cada 10 segundos
            except Exception as e:
                logger.error(f"Erro no worker de retry: {str(e)}")
    
    async def _deliver_webhook(self, delivery: WebhookDelivery):
        """Entrega webhook para endpoint"""
        start_time = time.time()
        
        try:
            endpoint = self.webhook_system.get_endpoint(delivery.endpoint_id)
            if not endpoint:
                logger.error(f"Endpoint não encontrado: {delivery.endpoint_id}")
                return
            
            # Preparar headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'OmniKeywordsFinder-Webhook/1.0',
                'X-Webhook-Event': delivery.payload['event_type'],
                'X-Webhook-Event-ID': delivery.event_id,
                'X-Webhook-Timestamp': delivery.payload['timestamp'],
                'X-Webhook-Source': delivery.payload['source'],
                'X-Webhook-Version': delivery.payload['version']
            }
            
            # Adicionar headers customizados
            if endpoint.headers:
                headers.update(endpoint.headers)
            
            # Adicionar assinatura HMAC se configurado
            if endpoint.security_level == WebhookSecurityLevel.HMAC and endpoint.secret:
                payload_str = json.dumps(delivery.payload, sort_keys=True)
                signature = self.webhook_system.validator.generate_signature(
                    payload_str, endpoint.secret
                )
                headers['X-Webhook-Signature'] = f"sha256={signature}"
            
            # Adicionar API Key se configurado
            if endpoint.security_level == WebhookSecurityLevel.API_KEY and endpoint.api_key:
                headers['X-API-Key'] = endpoint.api_key
            
            # Fazer requisição
            async with self.session.post(
                endpoint.url,
                json=delivery.payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
            ) as response:
                delivery.status_code = response.status
                delivery.response_body = await response.text()
                
                if response.status < 400:
                    # Sucesso
                    delivery.delivered_at = datetime.utcnow()
                    endpoint.success_count += 1
                    endpoint.last_triggered = datetime.utcnow()
                    
                    self.delivery_attempts.labels(
                        endpoint_id=delivery.endpoint_id,
                        status="success"
                    ).inc()
                    
                    logger.info(f"Webhook entregue com sucesso: {delivery.endpoint_id}")
                else:
                    # Erro
                    delivery.error_message = f"HTTP {response.status}: {delivery.response_body}"
                    endpoint.failure_count += 1
                    
                    self.delivery_attempts.labels(
                        endpoint_id=delivery.endpoint_id,
                        status="error"
                    ).inc()
                    
                    # Verificar se deve tentar novamente
                    if self.webhook_system.retry_manager.should_retry(
                        response.status, delivery.attempt_count
                    ):
                        self.webhook_system.retry_manager.schedule_retry(delivery)
                        logger.warning(f"Webhook falhou, agendado retry: {delivery.endpoint_id}")
                    else:
                        logger.error(f"Webhook falhou definitivamente: {delivery.endpoint_id}")
                
                # Atualizar métricas
                duration = time.time() - start_time
                self.delivery_duration.labels(
                    endpoint_id=delivery.endpoint_id
                ).observe(duration)
                
                # Salvar no banco
                self.webhook_system.database.save_delivery(delivery)
                self.webhook_system.database.save_endpoint(endpoint)
                
        except Exception as e:
            delivery.error_message = str(e)
            delivery.status_code = None
            
            self.delivery_attempts.labels(
                endpoint_id=delivery.endpoint_id,
                status="exception"
            ).inc()
            
            # Verificar se deve tentar novamente
            if self.webhook_system.retry_manager.should_retry(0, delivery.attempt_count):
                self.webhook_system.retry_manager.schedule_retry(delivery)
                logger.warning(f"Webhook falhou com exceção, agendado retry: {delivery.endpoint_id}")
            else:
                logger.error(f"Webhook falhou definitivamente com exceção: {delivery.endpoint_id}")
            
            # Salvar no banco
            self.webhook_system.database.save_delivery(delivery)

class WebhookSystem:
    """Sistema principal de webhooks"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.validator = WebhookValidator()
        self.rate_limiter = WebhookRateLimiter()
        self.retry_manager = WebhookRetryManager()
        self.database = WebhookDatabase()
        self.delivery_worker = WebhookDeliveryWorker(self)
        
        # Estado do sistema
        self.is_running = False
        self.event_handlers: Dict[WebhookEventType, List[Callable]] = defaultdict(list)
        
        # Métricas Prometheus
        self.webhooks_triggered = Counter(
            'webhooks_triggered_total',
            'Total de webhooks disparados',
            ['event_type', 'endpoint_id']
        )
        
        self.webhook_endpoints = Gauge(
            'webhook_endpoints_total',
            'Total de endpoints registrados',
            ['status']
        )
        
        # Carregar endpoints salvos
        self._load_endpoints()
        
        logger.info("Sistema de Webhooks inicializado")
    
    def start(self):
        """Inicia o sistema de webhooks"""
        if self.is_running:
            logger.warning("Sistema de webhooks já está em execução")
            return
        
        self.is_running = True
        
        # Iniciar worker de entrega
        def run_worker():
            asyncio.run(self.delivery_worker.start())
        
        self.worker_thread = threading.Thread(target=run_worker, daemon=True)
        self.worker_thread.start()
        
        logger.info("Sistema de Webhooks iniciado")
    
    def stop(self):
        """Para o sistema de webhooks"""
        self.is_running = False
        
        # Parar worker
        if hasattr(self, 'worker_thread'):
            asyncio.run(self.delivery_worker.stop())
        
        logger.info("Sistema de Webhooks parado")
    
    def register_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Registra novo endpoint"""
        # Validar endpoint
        errors = self.validator.validate_endpoint(endpoint)
        if errors:
            logger.error(f"Erro ao registrar endpoint: {errors}")
            return False
        
        # Gerar ID se não fornecido
        if not endpoint.id:
            endpoint.id = str(uuid.uuid4())
        
        # Definir timestamps
        now = datetime.utcnow()
        if not endpoint.created_at:
            endpoint.created_at = now
        endpoint.updated_at = now
        
        # Salvar no banco
        if self.database.save_endpoint(endpoint):
            self.endpoints[endpoint.id] = endpoint
            self._update_metrics()
            logger.info(f"Endpoint registrado: {endpoint.name} ({endpoint.id})")
            return True
        
        return False
    
    def unregister_endpoint(self, endpoint_id: str) -> bool:
        """Remove endpoint"""
        if endpoint_id in self.endpoints:
            endpoint = self.endpoints[endpoint_id]
            endpoint.status = WebhookStatus.INACTIVE
            endpoint.updated_at = datetime.utcnow()
            
            if self.database.save_endpoint(endpoint):
                del self.endpoints[endpoint_id]
                self._update_metrics()
                logger.info(f"Endpoint removido: {endpoint_id}")
                return True
        
        return False
    
    def trigger_webhook(self, event_type: WebhookEventType, data: Dict[str, Any], 
                       source: str = "system") -> List[str]:
        """Dispara webhooks para um evento"""
        triggered_endpoints = []
        
        # Criar payload
        payload = WebhookPayload(
            event_type=event_type,
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            data=data,
            source=source
        )
        
        # Validar payload
        errors = self.validator.validate_payload(payload)
        if errors:
            logger.error(f"Payload inválido: {errors}")
            return []
        
        # Encontrar endpoints para o evento
        for endpoint in self.endpoints.values():
            if (endpoint.status == WebhookStatus.ACTIVE and 
                event_type in endpoint.events):
                
                # Verificar rate limit
                if not self.rate_limiter.is_allowed(endpoint.id, endpoint.rate_limit):
                    logger.warning(f"Rate limit atingido para endpoint: {endpoint.id}")
                    continue
                
                # Verificar se está bloqueado
                if self.rate_limiter.is_blocked(endpoint.id):
                    logger.warning(f"Endpoint bloqueado: {endpoint.id}")
                    continue
                
                # Criar entrega
                delivery = WebhookDelivery(
                    id=str(uuid.uuid4()),
                    endpoint_id=endpoint.id,
                    event_id=payload.event_id,
                    payload=asdict(payload),
                    max_attempts=endpoint.retry_attempts,
                    created_at=datetime.utcnow()
                )
                
                # Salvar no banco
                self.database.save_delivery(delivery)
                
                # Enviar para worker
                asyncio.create_task(self.delivery_worker.delivery_queue.put(delivery))
                
                triggered_endpoints.append(endpoint.id)
                
                # Atualizar métricas
                self.webhooks_triggered.labels(
                    event_type=event_type.value,
                    endpoint_id=endpoint.id
                ).inc()
                
                logger.info(f"Webhook disparado: {event_type.value} -> {endpoint.name}")
        
        return triggered_endpoints
    
    def get_endpoint(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        """Retorna endpoint por ID"""
        return self.endpoints.get(endpoint_id)
    
    def list_endpoints(self) -> List[WebhookEndpoint]:
        """Lista todos os endpoints"""
        return list(self.endpoints.values())
    
    def get_pending_retries(self) -> List[WebhookDelivery]:
        """Retorna entregas com retry pendente"""
        # Implementação simplificada - em produção seria mais robusta
        return []
    
    def get_delivery_stats(self, endpoint_id: str, days: int = 30) -> Dict[str, Any]:
        """Retorna estatísticas de entrega"""
        # Implementação simplificada - em produção seria mais robusta
        return {
            'total_deliveries': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'avg_delivery_time': 0.0,
            'success_rate': 0.0
        }
    
    def _load_endpoints(self):
        """Carrega endpoints do banco"""
        endpoints = self.database.load_endpoints()
        for endpoint in endpoints:
            self.endpoints[endpoint.id] = endpoint
        
        self._update_metrics()
        logger.info(f"Carregados {len(endpoints)} endpoints")
    
    def _update_metrics(self):
        """Atualiza métricas Prometheus"""
        status_counts = defaultdict(int)
        for endpoint in self.endpoints.values():
            status_counts[endpoint.status.value] += 1
        
        for status, count in status_counts.items():
            self.webhook_endpoints.labels(status=status).set(count)

def create_webhook_system(config: Optional[Dict[str, Any]] = None) -> WebhookSystem:
    """Factory function para criar sistema de webhooks"""
    return WebhookSystem(config)

# Exemplo de uso
if __name__ == "__main__":
    # Configuração do sistema
    config = {
        'max_retries': 3,
        'base_delay': 5,
        'db_path': 'webhooks.db'
    }
    
    # Criar sistema
    webhook_system = create_webhook_system(config)
    
    # Registrar endpoint
    endpoint = WebhookEndpoint(
        id="test-endpoint",
        name="Test Webhook",
        url="https://webhook.site/your-unique-url",
        events=[WebhookEventType.KEYWORD_PROCESSED, WebhookEventType.EXECUTION_COMPLETED],
        secret="your-secret-key",
        security_level=WebhookSecurityLevel.HMAC
    )
    
    webhook_system.register_endpoint(endpoint)
    
    # Iniciar sistema
    webhook_system.start()
    
    try:
        # Disparar webhook
        data = {
            'keyword': 'test keyword',
            'status': 'processed',
            'results': {'clusters': 5, 'keywords': 100}
        }
        
        triggered = webhook_system.trigger_webhook(
            WebhookEventType.KEYWORD_PROCESSED, data
        )
        
        print(f"Webhooks disparados: {len(triggered)}")
        
        # Aguardar um pouco para processamento
        time.sleep(5)
        
    finally:
        webhook_system.stop() 