"""
Multi-Gateway Strategy System
Tracing ID: ARCH-002
Prompt: INTEGRATION_EXTERNAL_CHECKLIST_V2.md
Ruleset: enterprise_control_layer.yaml
Data/Hora: 2024-12-20 01:15:00 UTC

Sistema de estratégia multi-gateway para integrações externas enterprise
com fallback automático, load balancing inteligente e métricas por gateway.
"""

import json
import logging
import time
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import aiohttp
from datetime import datetime, timedelta
import statistics

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GatewayStatus(Enum):
    """Status do gateway"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    FAILED = "failed"


class LoadBalancingStrategy(Enum):
    """Estratégias de load balancing"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    FAILURE_RATE = "failure_rate"


class FallbackStrategy(Enum):
    """Estratégias de fallback"""
    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    CIRCUIT_BREAKER = "circuit_breaker"
    HEALTH_CHECK = "health_check"


@dataclass
class GatewayMetrics:
    """Métricas do gateway"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    last_response_time: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    uptime_percentage: float = 100.0
    error_rate: float = 0.0
    throughput: float = 0.0  # requests per second
    
    def update_metrics(self, success: bool, response_time: float):
        """Atualiza métricas do gateway"""
        self.total_requests += 1
        self.total_response_time += response_time
        self.last_response_time = response_time
        
        if success:
            self.successful_requests += 1
            self.consecutive_successes += 1
            self.consecutive_failures = 0
            self.last_success_time = datetime.now()
        else:
            self.failed_requests += 1
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            self.last_failure_time = datetime.now()
        
        # Calcular métricas derivadas
        self.average_response_time = self.total_response_time / self.total_requests
        self.error_rate = (self.failed_requests / self.total_requests) * 100 if self.total_requests > 0 else 0
        self.uptime_percentage = (self.successful_requests / self.total_requests) * 100 if self.total_requests > 0 else 100


@dataclass
class GatewayConfig:
    """Configuração do gateway"""
    name: str
    endpoint: str
    api_key: str
    secret_key: Optional[str] = None
    weight: int = 1
    priority: int = 1
    timeout: int = 30
    retry_attempts: int = 3
    health_check_interval: int = 60
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 300
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayHealth:
    """Status de saúde do gateway"""
    gateway_name: str
    status: GatewayStatus
    last_check: datetime
    response_time: float
    error_message: Optional[str] = None
    is_available: bool = True


class BaseGateway(ABC):
    """Classe base para gateways de pagamento"""
    
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.metrics = GatewayMetrics()
        self.status = GatewayStatus.ACTIVE
        self.last_health_check = None
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = None
        
    @abstractmethod
    async def process_payment(self, payment_data: Dict) -> Dict:
        """Processa pagamento no gateway"""
        pass
    
    @abstractmethod
    async def health_check(self) -> GatewayHealth:
        """Executa health check do gateway"""
        pass
    
    def update_circuit_breaker(self, success: bool):
        """Atualiza circuit breaker"""
        if success:
            self.circuit_breaker_failures = 0
            self.status = GatewayStatus.ACTIVE
        else:
            self.circuit_breaker_failures += 1
            self.circuit_breaker_last_failure = datetime.now()
            
            if self.circuit_breaker_failures >= self.config.circuit_breaker_threshold:
                self.status = GatewayStatus.FAILED
                logger.warning(f"[MultiGateway] Circuit breaker ativado para {self.config.name}")


class StripeGateway(BaseGateway):
    """Gateway Stripe"""
    
    async def process_payment(self, payment_data: Dict) -> Dict:
        """Processa pagamento no Stripe"""
        start_time = time.time()
        success = False
        
        try:
            # Simular processamento do Stripe
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.config.endpoint}/v1/charges",
                    json=payment_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        success = True
                    else:
                        result = {"error": f"HTTP {response.status}"}
                        
        except Exception as e:
            result = {"error": str(e)}
            logger.error(f"[MultiGateway] Erro no Stripe: {e}")
        
        response_time = time.time() - start_time
        self.metrics.update_metrics(success, response_time)
        self.update_circuit_breaker(success)
        
        return {
            "gateway": "stripe",
            "success": success,
            "result": result,
            "response_time": response_time
        }
    
    async def health_check(self) -> GatewayHealth:
        """Health check do Stripe"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.config.api_key}"}
                
                async with session.get(
                    f"{self.config.endpoint}/v1/account",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return GatewayHealth(
                            gateway_name=self.config.name,
                            status=GatewayStatus.ACTIVE,
                            last_check=datetime.now(),
                            response_time=response_time,
                            is_available=True
                        )
                    else:
                        return GatewayHealth(
                            gateway_name=self.config.name,
                            status=GatewayStatus.DEGRADED,
                            last_check=datetime.now(),
                            response_time=response_time,
                            error_message=f"HTTP {response.status}",
                            is_available=False
                        )
                        
        except Exception as e:
            response_time = time.time() - start_time
            return GatewayHealth(
                gateway_name=self.config.name,
                status=GatewayStatus.FAILED,
                last_check=datetime.now(),
                response_time=response_time,
                error_message=str(e),
                is_available=False
            )


class PayPalGateway(BaseGateway):
    """Gateway PayPal"""
    
    async def process_payment(self, payment_data: Dict) -> Dict:
        """Processa pagamento no PayPal"""
        start_time = time.time()
        success = False
        
        try:
            # Simular processamento do PayPal
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    f"{self.config.endpoint}/v1/payments/payment",
                    json=payment_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        success = True
                    else:
                        result = {"error": f"HTTP {response.status}"}
                        
        except Exception as e:
            result = {"error": str(e)}
            logger.error(f"[MultiGateway] Erro no PayPal: {e}")
        
        response_time = time.time() - start_time
        self.metrics.update_metrics(success, response_time)
        self.update_circuit_breaker(success)
        
        return {
            "gateway": "paypal",
            "success": success,
            "result": result,
            "response_time": response_time
        }
    
    async def health_check(self) -> GatewayHealth:
        """Health check do PayPal"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.config.api_key}"}
                
                async with session.get(
                    f"{self.config.endpoint}/v1/identity/openidconnect/userinfo",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return GatewayHealth(
                            gateway_name=self.config.name,
                            status=GatewayStatus.ACTIVE,
                            last_check=datetime.now(),
                            response_time=response_time,
                            is_available=True
                        )
                    else:
                        return GatewayHealth(
                            gateway_name=self.config.name,
                            status=GatewayStatus.DEGRADED,
                            last_check=datetime.now(),
                            response_time=response_time,
                            error_message=f"HTTP {response.status}",
                            is_available=False
                        )
                        
        except Exception as e:
            response_time = time.time() - start_time
            return GatewayHealth(
                gateway_name=self.config.name,
                status=GatewayStatus.FAILED,
                last_check=datetime.now(),
                response_time=response_time,
                error_message=str(e),
                is_available=False
            )


class MultiGatewayManager:
    """
    Gerenciador de múltiplos gateways com estratégias avançadas
    """
    
    def __init__(self, config: Dict):
        """
        Inicializa o gerenciador de gateways
        
        Args:
            config: Configuração dos gateways
        """
        self.config = config
        self.gateways: Dict[str, BaseGateway] = {}
        self.load_balancing_strategy = LoadBalancingStrategy(
            config.get("load_balancing_strategy", "weighted_round_robin")
        )
        self.fallback_strategy = FallbackStrategy(
            config.get("fallback_strategy", "immediate")
        )
        self.current_gateway_index = 0
        self.gateway_weights = {}
        self.health_check_interval = config.get("health_check_interval", 60)
        self.health_check_task = None
        
        self._initialize_gateways()
        self._start_health_check()
    
    def _initialize_gateways(self):
        """Inicializa os gateways baseado na configuração"""
        gateway_configs = self.config.get("gateways", {})
        
        for name, gateway_config in gateway_configs.items():
            if not gateway_config.get("enabled", True):
                continue
                
            config = GatewayConfig(
                name=name,
                endpoint=gateway_config["endpoint"],
                api_key=gateway_config["api_key"],
                secret_key=gateway_config.get("secret_key"),
                weight=gateway_config.get("weight", 1),
                priority=gateway_config.get("priority", 1),
                timeout=gateway_config.get("timeout", 30),
                retry_attempts=gateway_config.get("retry_attempts", 3),
                health_check_interval=gateway_config.get("health_check_interval", 60),
                circuit_breaker_threshold=gateway_config.get("circuit_breaker_threshold", 5),
                circuit_breaker_timeout=gateway_config.get("circuit_breaker_timeout", 300),
                enabled=gateway_config.get("enabled", True),
                metadata=gateway_config.get("metadata", {})
            )
            
            # Criar gateway baseado no tipo
            gateway_type = gateway_config.get("type", "stripe")
            if gateway_type == "stripe":
                gateway = StripeGateway(config)
            elif gateway_type == "paypal":
                gateway = PayPalGateway(config)
            else:
                logger.warning(f"[MultiGateway] Tipo de gateway desconhecido: {gateway_type}")
                continue
            
            self.gateways[name] = gateway
            self.gateway_weights[name] = config.weight
    
    def _start_health_check(self):
        """Inicia health check periódico"""
        if self.health_check_task is None:
            self.health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self):
        """Loop de health check"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"[MultiGateway] Erro no health check loop: {e}")
                await asyncio.sleep(10)
    
    async def _perform_health_checks(self):
        """Executa health checks em todos os gateways"""
        health_tasks = []
        
        for gateway in self.gateways.values():
            health_tasks.append(gateway.health_check())
        
        health_results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        for index, (name, gateway) in enumerate(self.gateways.items()):
            if isinstance(health_results[index], Exception):
                logger.error(f"[MultiGateway] Erro no health check de {name}: {health_results[index]}")
                gateway.status = GatewayStatus.FAILED
            else:
                health = health_results[index]
                gateway.status = health.status
                gateway.last_health_check = health.last_check
                
                if not health.is_available:
                    logger.warning(f"[MultiGateway] Gateway {name} não disponível: {health.error_message}")
    
    def _select_gateway_round_robin(self) -> Optional[BaseGateway]:
        """Seleciona gateway usando round robin"""
        available_gateways = [g for g in self.gateways.values() if g.status == GatewayStatus.ACTIVE]
        
        if not available_gateways:
            return None
        
        gateway = available_gateways[self.current_gateway_index % len(available_gateways)]
        self.current_gateway_index += 1
        return gateway
    
    def _select_gateway_weighted_round_robin(self) -> Optional[BaseGateway]:
        """Seleciona gateway usando weighted round robin"""
        available_gateways = []
        weights = []
        
        for name, gateway in self.gateways.items():
            if gateway.status == GatewayStatus.ACTIVE:
                available_gateways.append(gateway)
                weights.append(self.gateway_weights.get(name, 1))
        
        if not available_gateways:
            return None
        
        # Seleção baseada em peso
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(available_gateways)
        
        rand = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for index, weight in enumerate(weights):
            cumulative_weight += weight
            if rand <= cumulative_weight:
                return available_gateways[index]
        
        return available_gateways[-1]
    
    def _select_gateway_least_connections(self) -> Optional[BaseGateway]:
        """Seleciona gateway com menos conexões"""
        available_gateways = [g for g in self.gateways.values() if g.status == GatewayStatus.ACTIVE]
        
        if not available_gateways:
            return None
        
        return min(available_gateways, key=lambda g: g.metrics.total_requests)
    
    def _select_gateway_response_time(self) -> Optional[BaseGateway]:
        """Seleciona gateway com menor tempo de resposta"""
        available_gateways = [g for g in self.gateways.values() if g.status == GatewayStatus.ACTIVE]
        
        if not available_gateways:
            return None
        
        return min(available_gateways, key=lambda g: g.metrics.average_response_time)
    
    def _select_gateway_failure_rate(self) -> Optional[BaseGateway]:
        """Seleciona gateway com menor taxa de falha"""
        available_gateways = [g for g in self.gateways.values() if g.status == GatewayStatus.ACTIVE]
        
        if not available_gateways:
            return None
        
        return min(available_gateways, key=lambda g: g.metrics.error_rate)
    
    def select_gateway(self) -> Optional[BaseGateway]:
        """Seleciona gateway baseado na estratégia configurada"""
        if self.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._select_gateway_round_robin()
        elif self.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._select_gateway_weighted_round_robin()
        elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._select_gateway_least_connections()
        elif self.load_balancing_strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return self._select_gateway_response_time()
        elif self.load_balancing_strategy == LoadBalancingStrategy.FAILURE_RATE:
            return self._select_gateway_failure_rate()
        else:
            return self._select_gateway_round_robin()
    
    async def process_payment(self, payment_data: Dict) -> Dict:
        """
        Processa pagamento usando estratégia multi-gateway
        
        Args:
            payment_data: Dados do pagamento
            
        Returns:
            Dict: Resultado do processamento
        """
        logger.info(f"[MultiGateway] Processando pagamento com estratégia: {self.load_balancing_strategy.value}")
        
        # Selecionar gateway primário
        primary_gateway = self.select_gateway()
        
        if not primary_gateway:
            return {
                "success": False,
                "error": "Nenhum gateway disponível",
                "gateways_tried": []
            }
        
        # Tentar gateway primário
        result = await primary_gateway.process_payment(payment_data)
        gateways_tried = [primary_gateway.config.name]
        
        if result["success"]:
            return {
                "success": True,
                "gateway_used": primary_gateway.config.name,
                "result": result["result"],
                "response_time": result["response_time"],
                "gateways_tried": gateways_tried
            }
        
        # Fallback se necessário
        if self.fallback_strategy != FallbackStrategy.IMMEDIATE:
            logger.warning(f"[MultiGateway] Gateway primário falhou, tentando fallback")
            
            # Tentar outros gateways
            for gateway in self.gateways.values():
                if gateway == primary_gateway or gateway.status != GatewayStatus.ACTIVE:
                    continue
                
                gateways_tried.append(gateway.config.name)
                result = await gateway.process_payment(payment_data)
                
                if result["success"]:
                    return {
                        "success": True,
                        "gateway_used": gateway.config.name,
                        "result": result["result"],
                        "response_time": result["response_time"],
                        "gateways_tried": gateways_tried
                    }
        
        return {
            "success": False,
            "error": "Todos os gateways falharam",
            "gateways_tried": gateways_tried,
            "last_error": result.get("result", {}).get("error", "Unknown error")
        }
    
    def get_gateway_metrics(self) -> Dict[str, Dict]:
        """Obtém métricas de todos os gateways"""
        metrics = {}
        
        for name, gateway in self.gateways.items():
            metrics[name] = {
                "status": gateway.status.value,
                "total_requests": gateway.metrics.total_requests,
                "successful_requests": gateway.metrics.successful_requests,
                "failed_requests": gateway.metrics.failed_requests,
                "average_response_time": gateway.metrics.average_response_time,
                "error_rate": gateway.metrics.error_rate,
                "uptime_percentage": gateway.metrics.uptime_percentage,
                "consecutive_failures": gateway.metrics.consecutive_failures,
                "last_health_check": gateway.last_health_check.isoformat() if gateway.last_health_check else None
            }
        
        return metrics
    
    def get_overall_metrics(self) -> Dict:
        """Obtém métricas gerais do sistema"""
        total_requests = sum(g.metrics.total_requests for g in self.gateways.values())
        total_successful = sum(g.metrics.successful_requests for g in self.gateways.values())
        total_failed = sum(g.metrics.failed_requests for g in self.gateways.values())
        
        active_gateways = sum(1 for g in self.gateways.values() if g.status == GatewayStatus.ACTIVE)
        total_gateways = len(self.gateways)
        
        return {
            "total_requests": total_requests,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "overall_success_rate": (total_successful / total_requests * 100) if total_requests > 0 else 0,
            "active_gateways": active_gateways,
            "total_gateways": total_gateways,
            "availability_percentage": (active_gateways / total_gateways * 100) if total_gateways > 0 else 0,
            "load_balancing_strategy": self.load_balancing_strategy.value,
            "fallback_strategy": self.fallback_strategy.value
        }
    
    async def shutdown(self):
        """Desliga o gerenciador de gateways"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass


# Funções de conveniência para uso global
async def create_multi_gateway_manager(config: Dict) -> MultiGatewayManager:
    """
    Função de conveniência para criar gerenciador de gateways
    
    Args:
        config: Configuração dos gateways
        
    Returns:
        MultiGatewayManager: Gerenciador configurado
    """
    return MultiGatewayManager(config)


async def process_payment_multi_gateway(payment_data: Dict, config: Dict) -> Dict:
    """
    Função de conveniência para processar pagamento
    
    Args:
        payment_data: Dados do pagamento
        config: Configuração dos gateways
        
    Returns:
        Dict: Resultado do processamento
    """
    manager = MultiGatewayManager(config)
    try:
        result = await manager.process_payment(payment_data)
        return result
    finally:
        await manager.shutdown()


if __name__ == "__main__":
    # Exemplo de uso
    config = {
        "load_balancing_strategy": "weighted_round_robin",
        "fallback_strategy": "immediate",
        "health_check_interval": 60,
        "gateways": {
            "stripe": {
                "type": "stripe",
                "endpoint": "https://api.stripe.com",
                "api_key": "sk_test_...",
                "weight": 2,
                "priority": 1,
                "enabled": True
            },
            "paypal": {
                "type": "paypal",
                "endpoint": "https://api.paypal.com",
                "api_key": "paypal_key_...",
                "weight": 1,
                "priority": 2,
                "enabled": True
            }
        }
    }
    
    async def main():
        manager = MultiGatewayManager(config)
        
        # Exemplo de processamento
        payment_data = {
            "amount": 1000,
            "currency": "usd",
            "description": "Test payment"
        }
        
        result = await manager.process_payment(payment_data)
        print(json.dumps(result, indent=2))
        
        # Métricas
        metrics = manager.get_gateway_metrics()
        print(json.dumps(metrics, indent=2))
        
        await manager.shutdown()
    
    asyncio.run(main()) 