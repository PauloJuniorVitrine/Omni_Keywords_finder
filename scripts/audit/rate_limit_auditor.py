"""
Rate Limits Auditor - Omni Keywords Finder

Tracing ID: FF-003
Data/Hora: 2024-12-20 00:05:00 UTC
Versão: 1.0
Status: Implementação Inicial

Sistema de auditoria de rate limits para integrações externas,
permitindo simulação de throttling, relatórios de compliance e alertas de aproximação de limites.
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics

# Configuração de logging
logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Tipos de rate limit"""
    REQUESTS_PER_SECOND = "requests_per_second"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    BANDWIDTH_PER_SECOND = "bandwidth_per_second"
    CONCURRENT_CONNECTIONS = "concurrent_connections"

class RateLimitStatus(Enum):
    """Status do rate limit"""
    NORMAL = "normal"
    APPROACHING = "approaching"
    THROTTLED = "throttled"
    EXCEEDED = "exceeded"
    BLOCKED = "blocked"

class IntegrationType(Enum):
    """Tipos de integração"""
    GOOGLE_TRENDS = "google_trends"
    GOOGLE_SEARCH_CONSOLE = "google_search_console"
    SEMRUSH = "semrush"
    AHREFS = "ahrefs"
    MAJESTIC = "majestic"
    WEBHOOK = "webhook"
    PAYMENT_GATEWAY = "payment_gateway"
    NOTIFICATION = "notification"

@dataclass
class RateLimitConfig:
    """Configuração de rate limit"""
    integration_type: IntegrationType
    rate_limit_type: RateLimitType
    limit_value: int
    window_seconds: int
    burst_limit: Optional[int] = None
    soft_limit_percentage: float = 0.8
    hard_limit_percentage: float = 1.0
    retry_after_seconds: int = 60
    penalty_seconds: int = 300
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

@dataclass
class RateLimitUsage:
    """Uso atual do rate limit"""
    integration_type: IntegrationType
    rate_limit_type: RateLimitType
    current_usage: int
    limit_value: int
    window_start: datetime
    window_end: datetime
    usage_percentage: float
    status: RateLimitStatus
    last_request_time: datetime
    throttled_requests: int = 0
    blocked_requests: int = 0
    retry_after: Optional[datetime] = None

@dataclass
class RateLimitViolation:
    """Violação de rate limit"""
    integration_type: IntegrationType
    rate_limit_type: RateLimitType
    violation_time: datetime
    limit_value: int
    actual_usage: int
    violation_percentage: float
    penalty_applied: bool
    retry_after: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class RateLimitAuditor:
    """
    Auditor de rate limits para integrações externas
    """
    
    def __init__(self):
        """Inicializa o auditor de rate limits"""
        self.rate_limits: Dict[str, RateLimitConfig] = {}
        self.current_usage: Dict[str, RateLimitUsage] = {}
        self.violations: List[RateLimitViolation] = []
        self.alerts: List[Dict[str, Any]] = []
        self.lock = threading.RLock()
        
        # Configurações padrão por integração
        self._initialize_default_limits()
        
        # Iniciar monitoramento
        self._start_monitoring()
        
        logger.info("[FF-003] Rate Limit Auditor inicializado")

    def _initialize_default_limits(self):
        """Inicializa rate limits padrão por integração"""
        default_limits = {
            IntegrationType.GOOGLE_TRENDS: [
                {
                    "rate_limit_type": RateLimitType.REQUESTS_PER_MINUTE,
                    "limit_value": 100,
                    "window_seconds": 60,
                    "burst_limit": 150,
                    "soft_limit_percentage": 0.8,
                    "hard_limit_percentage": 1.0,
                    "retry_after_seconds": 60
                },
                {
                    "rate_limit_type": RateLimitType.REQUESTS_PER_DAY,
                    "limit_value": 10000,
                    "window_seconds": 86400,
                    "burst_limit": 12000,
                    "soft_limit_percentage": 0.9,
                    "hard_limit_percentage": 1.0,
                    "retry_after_seconds": 3600
                }
            ],
            IntegrationType.GOOGLE_SEARCH_CONSOLE: [
                {
                    "rate_limit_type": RateLimitType.REQUESTS_PER_MINUTE,
                    "limit_value": 50,
                    "window_seconds": 60,
                    "burst_limit": 75,
                    "soft_limit_percentage": 0.8,
                    "hard_limit_percentage": 1.0,
                    "retry_after_seconds": 120
                }
            ],
            IntegrationType.SEMRUSH: [
                {
                    "rate_limit_type": RateLimitType.REQUESTS_PER_MINUTE,
                    "limit_value": 30,
                    "window_seconds": 60,
                    "burst_limit": 45,
                    "soft_limit_percentage": 0.8,
                    "hard_limit_percentage": 1.0,
                    "retry_after_seconds": 300
                },
                {
                    "rate_limit_type": RateLimitType.REQUESTS_PER_DAY,
                    "limit_value": 5000,
                    "window_seconds": 86400,
                    "burst_limit": 6000,
                    "soft_limit_percentage": 0.9,
                    "hard_limit_percentage": 1.0,
                    "retry_after_seconds": 7200
                }
            ],
            IntegrationType.WEBHOOK: [
                {
                    "rate_limit_type": RateLimitType.REQUESTS_PER_SECOND,
                    "limit_value": 10,
                    "window_seconds": 1,
                    "burst_limit": 20,
                    "soft_limit_percentage": 0.7,
                    "hard_limit_percentage": 1.0,
                    "retry_after_seconds": 30
                }
            ],
            IntegrationType.PAYMENT_GATEWAY: [
                {
                    "rate_limit_type": RateLimitType.REQUESTS_PER_MINUTE,
                    "limit_value": 100,
                    "window_seconds": 60,
                    "burst_limit": 150,
                    "soft_limit_percentage": 0.8,
                    "hard_limit_percentage": 1.0,
                    "retry_after_seconds": 60
                }
            ]
        }
        
        for integration, limits in default_limits.items():
            for limit_config in limits:
                key = f"{integration.value}_{limit_config['rate_limit_type'].value}"
                self.rate_limits[key] = RateLimitConfig(
                    integration_type=integration,
                    **limit_config,
                    metadata={
                        "description": f"Rate limit para {integration.value} - {limit_config['rate_limit_type'].value}",
                        "owner": "api-team",
                        "priority": "high"
                    }
                )

    def _start_monitoring(self):
        """Inicia monitoramento de rate limits"""
        def monitor_limits():
            while True:
                try:
                    self._check_all_limits()
                    time.sleep(30)  # Verificar a cada 30 segundos
                except Exception as e:
                    logger.error(f"[FF-003] Erro no monitoramento de rate limits: {e}")
                    time.sleep(60)
        
        # Iniciar thread de monitoramento
        monitor_thread = threading.Thread(target=monitor_limits, daemon=True)
        monitor_thread.start()
        logger.info("[FF-003] Monitoramento de rate limits iniciado")

    def _check_all_limits(self):
        """Verifica todos os rate limits"""
        with self.lock:
            for key, usage in self.current_usage.items():
                try:
                    self._check_rate_limit_status(key, usage)
                except Exception as e:
                    logger.error(f"[FF-003] Erro ao verificar rate limit {key}: {e}")

    def _check_rate_limit_status(self, key: str, usage: RateLimitUsage):
        """Verifica status de um rate limit específico"""
        config = self.rate_limits.get(key)
        if not config:
            return
        
        # Calcular uso atual
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=config.window_seconds)
        
        # Atualizar janela de tempo
        if usage.window_start < window_start:
            usage.window_start = window_start
            usage.window_end = now
            usage.current_usage = 0
            usage.throttled_requests = 0
            usage.blocked_requests = 0
        
        # Determinar status
        usage_percentage = usage.current_usage / config.limit_value
        
        if usage_percentage >= config.hard_limit_percentage:
            usage.status = RateLimitStatus.EXCEEDED
            usage.retry_after = now + timedelta(seconds=config.retry_after_seconds)
        elif usage_percentage >= config.soft_limit_percentage:
            usage.status = RateLimitStatus.APPROACHING
            usage.retry_after = None
        else:
            usage.status = RateLimitStatus.NORMAL
            usage.retry_after = None
        
        usage.usage_percentage = usage_percentage
        
        # Verificar se precisa gerar alerta
        if usage.status == RateLimitStatus.APPROACHING:
            self._generate_alert(key, usage, "approaching_limit")
        elif usage.status == RateLimitStatus.EXCEEDED:
            self._generate_alert(key, usage, "limit_exceeded")

    def _generate_alert(self, key: str, usage: RateLimitUsage, alert_type: str):
        """Gera alerta de rate limit"""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "key": key,
            "integration_type": usage.integration_type.value,
            "rate_limit_type": usage.rate_limit_type.value,
            "alert_type": alert_type,
            "current_usage": usage.current_usage,
            "limit_value": usage.limit_value,
            "usage_percentage": usage.usage_percentage,
            "status": usage.status.value,
            "retry_after": usage.retry_after.isoformat() if usage.retry_after else None
        }
        
        self.alerts.append(alert)
        logger.warning(f"[FF-003] Alerta de rate limit: {alert_type} para {key}")

    def check_rate_limit(self, integration_type: IntegrationType, 
                        rate_limit_type: RateLimitType = RateLimitType.REQUESTS_PER_MINUTE) -> bool:
        """
        Verifica se uma requisição pode ser feita
        
        Args:
            integration_type: Tipo de integração
            rate_limit_type: Tipo de rate limit
            
        Returns:
            True se permitido, False se bloqueado
        """
        try:
            key = f"{integration_type.value}_{rate_limit_type.value}"
            
            with self.lock:
                config = self.rate_limits.get(key)
                if not config:
                    logger.warning(f"[FF-003] Rate limit não configurado para {key}")
                    return True  # Permitir se não configurado
                
                usage = self.current_usage.get(key)
                if not usage:
                    # Inicializar uso
                    now = datetime.utcnow()
                    usage = RateLimitUsage(
                        integration_type=integration_type,
                        rate_limit_type=rate_limit_type,
                        current_usage=0,
                        limit_value=config.limit_value,
                        window_start=now,
                        window_end=now + timedelta(seconds=config.window_seconds),
                        usage_percentage=0.0,
                        status=RateLimitStatus.NORMAL,
                        last_request_time=now
                    )
                    self.current_usage[key] = usage
                
                # Verificar se está bloqueado
                if usage.status == RateLimitStatus.EXCEEDED:
                    if usage.retry_after and datetime.utcnow() < usage.retry_after:
                        usage.blocked_requests += 1
                        return False
                    else:
                        # Resetar após período de retry
                        usage.status = RateLimitStatus.NORMAL
                        usage.retry_after = None
                
                # Verificar se está throttled
                if usage.status == RateLimitStatus.APPROACHING:
                    usage.throttled_requests += 1
                    # Ainda permitir, mas com throttling
                
                # Incrementar uso
                usage.current_usage += 1
                usage.last_request_time = datetime.utcnow()
                
                # Verificar se excedeu limite
                if usage.current_usage > config.limit_value:
                    self._record_violation(integration_type, rate_limit_type, usage, config)
                    usage.status = RateLimitStatus.EXCEEDED
                    usage.retry_after = datetime.utcnow() + timedelta(seconds=config.retry_after_seconds)
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"[FF-003] Erro ao verificar rate limit: {e}")
            return True  # Permitir em caso de erro

    def _record_violation(self, integration_type: IntegrationType, 
                         rate_limit_type: RateLimitType, 
                         usage: RateLimitUsage, 
                         config: RateLimitConfig):
        """Registra violação de rate limit"""
        violation = RateLimitViolation(
            integration_type=integration_type,
            rate_limit_type=rate_limit_type,
            violation_time=datetime.utcnow(),
            limit_value=config.limit_value,
            actual_usage=usage.current_usage,
            violation_percentage=(usage.current_usage / config.limit_value) * 100,
            penalty_applied=True,
            retry_after=datetime.utcnow() + timedelta(seconds=config.retry_after_seconds),
            metadata={
                "window_start": usage.window_start.isoformat(),
                "window_end": usage.window_end.isoformat(),
                "throttled_requests": usage.throttled_requests,
                "blocked_requests": usage.blocked_requests
            }
        )
        
        self.violations.append(violation)
        logger.error(f"[FF-003] Violação de rate limit registrada: {integration_type.value}")

    def simulate_throttling(self, integration_type: IntegrationType, 
                          rate_limit_type: RateLimitType = RateLimitType.REQUESTS_PER_MINUTE,
                          requests_count: int = 100) -> Dict[str, Any]:
        """
        Simula throttling de rate limits
        
        Args:
            integration_type: Tipo de integração
            rate_limit_type: Tipo de rate limit
            requests_count: Número de requisições para simular
            
        Returns:
            Resultado da simulação
        """
        try:
            results = {
                "integration_type": integration_type.value,
                "rate_limit_type": rate_limit_type.value,
                "requests_count": requests_count,
                "allowed_requests": 0,
                "blocked_requests": 0,
                "throttled_requests": 0,
                "violations": 0,
                "simulation_time": 0,
                "requests_per_second": 0,
                "details": []
            }
            
            start_time = time.time()
            
            for index in range(requests_count):
                request_start = time.time()
                
                # Verificar rate limit
                allowed = self.check_rate_limit(integration_type, rate_limit_type)
                
                request_time = time.time() - request_start
                
                request_detail = {
                    "request_id": index + 1,
                    "timestamp": datetime.utcnow().isoformat(),
                    "allowed": allowed,
                    "request_time": request_time
                }
                
                if allowed:
                    results["allowed_requests"] += 1
                else:
                    results["blocked_requests"] += 1
                
                results["details"].append(request_detail)
                
                # Pequena pausa entre requisições
                time.sleep(0.01)
            
            end_time = time.time()
            results["simulation_time"] = end_time - start_time
            results["requests_per_second"] = requests_count / results["simulation_time"]
            
            # Contar violações
            key = f"{integration_type.value}_{rate_limit_type.value}"
            usage = self.current_usage.get(key)
            if usage:
                results["throttled_requests"] = usage.throttled_requests
                results["violations"] = len([value for value in self.violations 
                                           if value.integration_type == integration_type and 
                                           value.rate_limit_type == rate_limit_type])
            
            return results
            
        except Exception as e:
            logger.error(f"[FF-003] Erro na simulação de throttling: {e}")
            return {
                "error": str(e),
                "integration_type": integration_type.value,
                "rate_limit_type": rate_limit_type.value
            }

    def get_rate_limit_config(self, integration_type: IntegrationType, 
                             rate_limit_type: RateLimitType) -> Optional[RateLimitConfig]:
        """Obtém configuração de rate limit"""
        key = f"{integration_type.value}_{rate_limit_type.value}"
        return self.rate_limits.get(key)

    def get_current_usage(self, integration_type: IntegrationType, 
                         rate_limit_type: RateLimitType) -> Optional[RateLimitUsage]:
        """Obtém uso atual de rate limit"""
        key = f"{integration_type.value}_{rate_limit_type.value}"
        return self.current_usage.get(key)

    def get_all_usage(self) -> Dict[str, RateLimitUsage]:
        """Obtém uso de todos os rate limits"""
        return self.current_usage.copy()

    def get_violations(self, integration_type: Optional[IntegrationType] = None, 
                      days: int = 7) -> List[RateLimitViolation]:
        """Obtém violações de rate limit"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        violations = [
            value for value in self.violations
            if value.violation_time >= cutoff_time
        ]
        
        if integration_type:
            violations = [
                value for value in violations
                if value.integration_type == integration_type
            ]
        
        return violations

    def get_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtém alertas de rate limit"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) >= cutoff_time
        ]

    def update_rate_limit_config(self, integration_type: IntegrationType, 
                                rate_limit_type: RateLimitType, 
                                updates: Dict[str, Any]) -> bool:
        """
        Atualiza configuração de rate limit
        
        Args:
            integration_type: Tipo de integração
            rate_limit_type: Tipo de rate limit
            updates: Atualizações a serem aplicadas
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            key = f"{integration_type.value}_{rate_limit_type.value}"
            
            with self.lock:
                config = self.rate_limits.get(key)
                if not config:
                    return False
                
                # Aplicar atualizações
                for update_key, value in updates.items():
                    if hasattr(config, update_key):
                        setattr(config, update_key, value)
                
                config.updated_at = datetime.utcnow()
                
                logger.info(f"[FF-003] Configuração de rate limit atualizada: {key}")
                return True
                
        except Exception as e:
            logger.error(f"[FF-003] Erro ao atualizar configuração de rate limit: {e}")
            return False

    def get_compliance_report(self) -> Dict[str, Any]:
        """Gera relatório de compliance de rate limits"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_integrations": len(set(usage.integration_type for usage in self.current_usage.values())),
                "total_rate_limits": len(self.rate_limits),
                "active_violations": len([value for value in self.violations 
                                        if value.violation_time >= datetime.utcnow() - timedelta(hours=1)]),
                "total_violations_24h": len([value for value in self.violations 
                                           if value.violation_time >= datetime.utcnow() - timedelta(hours=24)]),
                "total_alerts_24h": len(self.get_alerts(24))
            },
            "integrations": {}
        }
        
        for integration in IntegrationType:
            integration_usage = [
                usage for usage in self.current_usage.values()
                if usage.integration_type == integration
            ]
            
            if integration_usage:
                report["integrations"][integration.value] = {
                    "rate_limits": len(integration_usage),
                    "total_usage": sum(usage.current_usage for usage in integration_usage),
                    "violations_24h": len([value for value in self.violations 
                                         if value.integration_type == integration and 
                                         value.violation_time >= datetime.utcnow() - timedelta(hours=24)]),
                    "alerts_24h": len([a for a in self.get_alerts(24) 
                                     if a["integration_type"] == integration.value])
                }
        
        return report

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos rate limits"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "rate_limits": {},
            "summary": {
                "total_rate_limits": len(self.rate_limits),
                "active_usage": len(self.current_usage),
                "total_violations": len(self.violations),
                "total_alerts": len(self.alerts),
                "average_usage_percentage": 0.0
            }
        }
        
        total_usage_percentage = 0.0
        usage_count = 0
        
        for key, usage in self.current_usage.items():
            metrics["rate_limits"][key] = {
                "integration_type": usage.integration_type.value,
                "rate_limit_type": usage.rate_limit_type.value,
                "current_usage": usage.current_usage,
                "limit_value": usage.limit_value,
                "usage_percentage": usage.usage_percentage,
                "status": usage.status.value,
                "throttled_requests": usage.throttled_requests,
                "blocked_requests": usage.blocked_requests,
                "last_request_time": usage.last_request_time.isoformat(),
                "retry_after": usage.retry_after.isoformat() if usage.retry_after else None
            }
            
            total_usage_percentage += usage.usage_percentage
            usage_count += 1
        
        if usage_count > 0:
            metrics["summary"]["average_usage_percentage"] = total_usage_percentage / usage_count
        
        return metrics

    def get_health_status(self) -> Dict[str, Any]:
        """Obtém status de saúde do sistema de rate limits"""
        try:
            # Verificar se há muitas violações recentes
            recent_violations = len([value for value in self.violations 
                                   if value.violation_time >= datetime.utcnow() - timedelta(hours=1)])
            
            # Verificar se há muitos alertas recentes
            recent_alerts = len(self.get_alerts(1))
            
            # Determinar status geral
            if recent_violations > 10 or recent_alerts > 20:
                status = "unhealthy"
            elif recent_violations > 5 or recent_alerts > 10:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "total_rate_limits": len(self.rate_limits),
                "active_usage": len(self.current_usage),
                "recent_violations_1h": recent_violations,
                "recent_alerts_1h": recent_alerts,
                "total_violations_24h": len([value for value in self.violations 
                                           if value.violation_time >= datetime.utcnow() - timedelta(hours=24)]),
                "total_alerts_24h": len(self.get_alerts(24)),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[FF-003] Erro ao obter status de saúde: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Instância global
_rate_limit_auditor: Optional[RateLimitAuditor] = None

def get_rate_limit_auditor() -> RateLimitAuditor:
    """Obtém instância global do auditor de rate limits"""
    global _rate_limit_auditor
    
    if _rate_limit_auditor is None:
        _rate_limit_auditor = RateLimitAuditor()
    
    return _rate_limit_auditor

def check_rate_limit(integration_type: Union[str, IntegrationType], 
                    rate_limit_type: Union[str, RateLimitType] = RateLimitType.REQUESTS_PER_MINUTE) -> bool:
    """
    Função de conveniência para verificar rate limit
    
    Args:
        integration_type: Tipo de integração
        rate_limit_type: Tipo de rate limit
        
    Returns:
        True se permitido, False se bloqueado
    """
    auditor = get_rate_limit_auditor()
    
    if isinstance(integration_type, str):
        integration_type = IntegrationType(integration_type)
    if isinstance(rate_limit_type, str):
        rate_limit_type = RateLimitType(rate_limit_type)
    
    return auditor.check_rate_limit(integration_type, rate_limit_type)

def simulate_throttling(integration_type: Union[str, IntegrationType], 
                       rate_limit_type: Union[str, RateLimitType] = RateLimitType.REQUESTS_PER_MINUTE,
                       requests_count: int = 100) -> Dict[str, Any]:
    """
    Função de conveniência para simular throttling
    
    Args:
        integration_type: Tipo de integração
        rate_limit_type: Tipo de rate limit
        requests_count: Número de requisições para simular
        
    Returns:
        Resultado da simulação
    """
    auditor = get_rate_limit_auditor()
    
    if isinstance(integration_type, str):
        integration_type = IntegrationType(integration_type)
    if isinstance(rate_limit_type, str):
        rate_limit_type = RateLimitType(rate_limit_type)
    
    return auditor.simulate_throttling(integration_type, rate_limit_type, requests_count) 