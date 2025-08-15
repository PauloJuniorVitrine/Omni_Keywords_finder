"""
Testes unitários para MultiGatewayManager
Tracing ID: ARCH-002
Prompt: INTEGRATION_EXTERNAL_CHECKLIST_V2.md
Ruleset: enterprise_control_layer.yaml
Data/Hora: 2024-12-20 01:15:00 UTC

Testes unitários abrangentes para o sistema de estratégia multi-gateway.
"""

import pytest
import json
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Optional
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from infrastructure.payments.multi_gateway import (
    MultiGatewayManager,
    StripeGateway,
    PayPalGateway,
    GatewayConfig,
    GatewayMetrics,
    GatewayStatus,
    LoadBalancingStrategy,
    FallbackStrategy,
    GatewayHealth
)


class TestGatewayConfig:
    """Testes para GatewayConfig"""
    
    def test_gateway_config_creation(self):
        """Testa criação de configuração de gateway"""
        config = GatewayConfig(
            name="test_gateway",
            endpoint="https://api.test.com",
            api_key="test_key",
            secret_key="test_secret",
            weight=2,
            priority=1
        )
        
        assert config.name == "test_gateway"
        assert config.endpoint == "https://api.test.com"
        assert config.api_key == "test_key"
        assert config.secret_key == "test_secret"
        assert config.weight == 2
        assert config.priority == 1
        assert config.enabled is True
    
    def test_gateway_config_defaults(self):
        """Testa valores padrão da configuração"""
        config = GatewayConfig(
            name="test_gateway",
            endpoint="https://api.test.com",
            api_key="test_key"
        )
        
        assert config.secret_key is None
        assert config.weight == 1
        assert config.priority == 1
        assert config.timeout == 30
        assert config.retry_attempts == 3
        assert config.enabled is True


class TestGatewayMetrics:
    """Testes para GatewayMetrics"""
    
    def test_gateway_metrics_initialization(self):
        """Testa inicialização das métricas"""
        metrics = GatewayMetrics()
        
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 0.0
        assert metrics.error_rate == 0.0
        assert metrics.uptime_percentage == 100.0
    
    def test_update_metrics_success(self):
        """Testa atualização de métricas com sucesso"""
        metrics = GatewayMetrics()
        metrics.update_metrics(success=True, response_time=1.5)
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 1.5
        assert metrics.consecutive_successes == 1
        assert metrics.consecutive_failures == 0
        assert metrics.error_rate == 0.0
        assert metrics.uptime_percentage == 100.0
    
    def test_update_metrics_failure(self):
        """Testa atualização de métricas com falha"""
        metrics = GatewayMetrics()
        metrics.update_metrics(success=False, response_time=2.0)
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1
        assert metrics.average_response_time == 2.0
        assert metrics.consecutive_successes == 0
        assert metrics.consecutive_failures == 1
        assert metrics.error_rate == 100.0
        assert metrics.uptime_percentage == 0.0
    
    def test_update_metrics_mixed(self):
        """Testa atualização de métricas mistas"""
        metrics = GatewayMetrics()
        
        # Sucesso
        metrics.update_metrics(success=True, response_time=1.0)
        # Falha
        metrics.update_metrics(success=False, response_time=2.0)
        # Sucesso
        metrics.update_metrics(success=True, response_time=1.5)
        
        assert metrics.total_requests == 3
        assert metrics.successful_requests == 2
        assert metrics.failed_requests == 1
        assert metrics.average_response_time == 1.5
        assert metrics.error_rate == 33.33
        assert metrics.uptime_percentage == 66.67


class TestStripeGateway:
    """Testes para StripeGateway"""
    
    def setup_method(self):
        """Setup para cada teste"""
        config = GatewayConfig(
            name="stripe_test",
            endpoint="https://api.stripe.com",
            api_key="sk_test_123"
        )
        self.gateway = StripeGateway(config)
    
    @patch('aiohttp.ClientSession')
    async def test_process_payment_success(self, mock_session):
        """Testa processamento de pagamento com sucesso"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"id": "ch_123", "status": "succeeded"})
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        payment_data = {"amount": 1000, "currency": "usd"}
        result = await self.gateway.process_payment(payment_data)
        
        assert result["gateway"] == "stripe"
        assert result["success"] is True
        assert result["result"]["id"] == "ch_123"
        assert "response_time" in result
    
    @patch('aiohttp.ClientSession')
    async def test_process_payment_failure(self, mock_session):
        """Testa processamento de pagamento com falha"""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={"error": "Invalid amount"})
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        payment_data = {"amount": -1000, "currency": "usd"}
        result = await self.gateway.process_payment(payment_data)
        
        assert result["gateway"] == "stripe"
        assert result["success"] is False
        assert "error" in result["result"]
    
    @patch('aiohttp.ClientSession')
    async def test_process_payment_exception(self, mock_session):
        """Testa processamento de pagamento com exceção"""
        mock_session.side_effect = Exception("Network error")
        
        payment_data = {"amount": 1000, "currency": "usd"}
        result = await self.gateway.process_payment(payment_data)
        
        assert result["gateway"] == "stripe"
        assert result["success"] is False
        assert "error" in result["result"]
    
    @patch('aiohttp.ClientSession')
    async def test_health_check_success(self, mock_session):
        """Testa health check com sucesso"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"id": "acct_123"})
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        health = await self.gateway.health_check()
        
        assert health.gateway_name == "stripe_test"
        assert health.status == GatewayStatus.ACTIVE
        assert health.is_available is True
        assert health.error_message is None
    
    @patch('aiohttp.ClientSession')
    async def test_health_check_failure(self, mock_session):
        """Testa health check com falha"""
        mock_response = AsyncMock()
        mock_response.status = 401
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        health = await self.gateway.health_check()
        
        assert health.gateway_name == "stripe_test"
        assert health.status == GatewayStatus.DEGRADED
        assert health.is_available is False
        assert "HTTP 401" in health.error_message
    
    def test_circuit_breaker_success(self):
        """Testa circuit breaker com sucesso"""
        self.gateway.circuit_breaker_failures = 3
        self.gateway.status = GatewayStatus.FAILED
        
        self.gateway.update_circuit_breaker(success=True)
        
        assert self.gateway.circuit_breaker_failures == 0
        assert self.gateway.status == GatewayStatus.ACTIVE
    
    def test_circuit_breaker_failure(self):
        """Testa circuit breaker com falha"""
        self.gateway.circuit_breaker_failures = 4
        self.gateway.config.circuit_breaker_threshold = 5
        
        self.gateway.update_circuit_breaker(success=False)
        
        assert self.gateway.circuit_breaker_failures == 5
        assert self.gateway.status == GatewayStatus.FAILED


class TestPayPalGateway:
    """Testes para PayPalGateway"""
    
    def setup_method(self):
        """Setup para cada teste"""
        config = GatewayConfig(
            name="paypal_test",
            endpoint="https://api.paypal.com",
            api_key="paypal_key_123"
        )
        self.gateway = PayPalGateway(config)
    
    @patch('aiohttp.ClientSession')
    async def test_process_payment_success(self, mock_session):
        """Testa processamento de pagamento com sucesso"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"id": "PAY-123", "state": "approved"})
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        payment_data = {"amount": 1000, "currency": "usd"}
        result = await self.gateway.process_payment(payment_data)
        
        assert result["gateway"] == "paypal"
        assert result["success"] is True
        assert result["result"]["id"] == "PAY-123"
    
    @patch('aiohttp.ClientSession')
    async def test_health_check_success(self, mock_session):
        """Testa health check com sucesso"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"user_id": "user123"})
        
        mock_session_instance = AsyncMock()
        mock_session_instance.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        health = await self.gateway.health_check()
        
        assert health.gateway_name == "paypal_test"
        assert health.status == GatewayStatus.ACTIVE
        assert health.is_available is True


class TestMultiGatewayManager:
    """Testes para MultiGatewayManager"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.config = {
            "load_balancing_strategy": "weighted_round_robin",
            "fallback_strategy": "immediate",
            "health_check_interval": 60,
            "gateways": {
                "stripe": {
                    "type": "stripe",
                    "endpoint": "https://api.stripe.com",
                    "api_key": "sk_test_123",
                    "weight": 2,
                    "priority": 1,
                    "enabled": True
                },
                "paypal": {
                    "type": "paypal",
                    "endpoint": "https://api.paypal.com",
                    "api_key": "paypal_key_123",
                    "weight": 1,
                    "priority": 2,
                    "enabled": True
                }
            }
        }
    
    @patch('infrastructure.payments.multi_gateway.asyncio.create_task')
    def test_initialization(self, mock_create_task):
        """Testa inicialização do gerenciador"""
        manager = MultiGatewayManager(self.config)
        
        assert len(manager.gateways) == 2
        assert "stripe" in manager.gateways
        assert "paypal" in manager.gateways
        assert manager.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN
        assert manager.fallback_strategy == FallbackStrategy.IMMEDIATE
        assert manager.gateway_weights["stripe"] == 2
        assert manager.gateway_weights["paypal"] == 1
    
    def test_select_gateway_round_robin(self):
        """Testa seleção de gateway com round robin"""
        manager = MultiGatewayManager(self.config)
        manager.load_balancing_strategy = LoadBalancingStrategy.ROUND_ROBIN
        
        # Configurar gateways como ativos
        for gateway in manager.gateways.values():
            gateway.status = GatewayStatus.ACTIVE
        
        gateway1 = manager.select_gateway()
        gateway2 = manager.select_gateway()
        
        assert gateway1 is not None
        assert gateway2 is not None
        assert gateway1 != gateway2
    
    def test_select_gateway_weighted_round_robin(self):
        """Testa seleção de gateway com weighted round robin"""
        manager = MultiGatewayManager(self.config)
        manager.load_balancing_strategy = LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN
        
        # Configurar gateways como ativos
        for gateway in manager.gateways.values():
            gateway.status = GatewayStatus.ACTIVE
        
        # Testar múltiplas seleções
        selections = []
        for _ in range(10):
            gateway = manager.select_gateway()
            selections.append(gateway.config.name)
        
        # Verificar que Stripe (peso 2) é selecionado mais vezes que PayPal (peso 1)
        stripe_count = selections.count("stripe")
        paypal_count = selections.count("paypal")
        
        assert stripe_count > paypal_count
    
    def test_select_gateway_least_connections(self):
        """Testa seleção de gateway com least connections"""
        manager = MultiGatewayManager(self.config)
        manager.load_balancing_strategy = LoadBalancingStrategy.LEAST_CONNECTIONS
        
        # Configurar gateways como ativos
        for gateway in manager.gateways.values():
            gateway.status = GatewayStatus.ACTIVE
        
        # Configurar métricas diferentes
        stripe_gateway = manager.gateways["stripe"]
        paypal_gateway = manager.gateways["paypal"]
        
        stripe_gateway.metrics.total_requests = 10
        paypal_gateway.metrics.total_requests = 5
        
        selected_gateway = manager.select_gateway()
        assert selected_gateway == paypal_gateway
    
    def test_select_gateway_response_time(self):
        """Testa seleção de gateway com response time"""
        manager = MultiGatewayManager(self.config)
        manager.load_balancing_strategy = LoadBalancingStrategy.RESPONSE_TIME
        
        # Configurar gateways como ativos
        for gateway in manager.gateways.values():
            gateway.status = GatewayStatus.ACTIVE
        
        # Configurar métricas diferentes
        stripe_gateway = manager.gateways["stripe"]
        paypal_gateway = manager.gateways["paypal"]
        
        stripe_gateway.metrics.average_response_time = 2.0
        paypal_gateway.metrics.average_response_time = 1.0
        
        selected_gateway = manager.select_gateway()
        assert selected_gateway == paypal_gateway
    
    def test_select_gateway_failure_rate(self):
        """Testa seleção de gateway com failure rate"""
        manager = MultiGatewayManager(self.config)
        manager.load_balancing_strategy = LoadBalancingStrategy.FAILURE_RATE
        
        # Configurar gateways como ativos
        for gateway in manager.gateways.values():
            gateway.status = GatewayStatus.ACTIVE
        
        # Configurar métricas diferentes
        stripe_gateway = manager.gateways["stripe"]
        paypal_gateway = manager.gateways["paypal"]
        
        stripe_gateway.metrics.error_rate = 10.0
        paypal_gateway.metrics.error_rate = 5.0
        
        selected_gateway = manager.select_gateway()
        assert selected_gateway == paypal_gateway
    
    def test_select_gateway_no_available(self):
        """Testa seleção quando nenhum gateway está disponível"""
        manager = MultiGatewayManager(self.config)
        
        # Configurar todos os gateways como inativos
        for gateway in manager.gateways.values():
            gateway.status = GatewayStatus.FAILED
        
        selected_gateway = manager.select_gateway()
        assert selected_gateway is None
    
    @patch('infrastructure.payments.multi_gateway.asyncio.create_task')
    async def test_process_payment_success(self, mock_create_task):
        """Testa processamento de pagamento com sucesso"""
        manager = MultiGatewayManager(self.config)
        
        # Mock do gateway
        mock_gateway = Mock()
        mock_gateway.config.name = "stripe"
        mock_gateway.status = GatewayStatus.ACTIVE
        mock_gateway.process_payment = AsyncMock(return_value={
            "gateway": "stripe",
            "success": True,
            "result": {"id": "ch_123"},
            "response_time": 1.5
        })
        
        manager.gateways["stripe"] = mock_gateway
        
        with patch.object(manager, 'select_gateway', return_value=mock_gateway):
            result = await manager.process_payment({"amount": 1000})
            
            assert result["success"] is True
            assert result["gateway_used"] == "stripe"
            assert result["result"]["id"] == "ch_123"
            assert result["gateways_tried"] == ["stripe"]
    
    @patch('infrastructure.payments.multi_gateway.asyncio.create_task')
    async def test_process_payment_fallback(self, mock_create_task):
        """Testa processamento de pagamento com fallback"""
        manager = MultiGatewayManager(self.config)
        manager.fallback_strategy = FallbackStrategy.IMMEDIATE
        
        # Mock dos gateways
        mock_stripe = Mock()
        mock_stripe.config.name = "stripe"
        mock_stripe.status = GatewayStatus.ACTIVE
        mock_stripe.process_payment = AsyncMock(return_value={
            "gateway": "stripe",
            "success": False,
            "result": {"error": "Stripe failed"},
            "response_time": 1.0
        })
        
        mock_paypal = Mock()
        mock_paypal.config.name = "paypal"
        mock_paypal.status = GatewayStatus.ACTIVE
        mock_paypal.process_payment = AsyncMock(return_value={
            "gateway": "paypal",
            "success": True,
            "result": {"id": "PAY-123"},
            "response_time": 2.0
        })
        
        manager.gateways["stripe"] = mock_stripe
        manager.gateways["paypal"] = mock_paypal
        
        with patch.object(manager, 'select_gateway', side_effect=[mock_stripe, mock_paypal]):
            result = await manager.process_payment({"amount": 1000})
            
            assert result["success"] is True
            assert result["gateway_used"] == "paypal"
            assert result["result"]["id"] == "PAY-123"
            assert result["gateways_tried"] == ["stripe", "paypal"]
    
    @patch('infrastructure.payments.multi_gateway.asyncio.create_task')
    async def test_process_payment_all_failed(self, mock_create_task):
        """Testa processamento quando todos os gateways falham"""
        manager = MultiGatewayManager(self.config)
        
        # Mock dos gateways
        mock_gateway = Mock()
        mock_gateway.config.name = "stripe"
        mock_gateway.status = GatewayStatus.ACTIVE
        mock_gateway.process_payment = AsyncMock(return_value={
            "gateway": "stripe",
            "success": False,
            "result": {"error": "Gateway failed"},
            "response_time": 1.0
        })
        
        manager.gateways["stripe"] = mock_gateway
        
        with patch.object(manager, 'select_gateway', return_value=mock_gateway):
            result = await manager.process_payment({"amount": 1000})
            
            assert result["success"] is False
            assert "Todos os gateways falharam" in result["error"]
            assert result["gateways_tried"] == ["stripe"]
    
    def test_get_gateway_metrics(self):
        """Testa obtenção de métricas dos gateways"""
        manager = MultiGatewayManager(self.config)
        
        # Configurar métricas de teste
        stripe_gateway = manager.gateways["stripe"]
        stripe_gateway.metrics.total_requests = 100
        stripe_gateway.metrics.successful_requests = 95
        stripe_gateway.metrics.failed_requests = 5
        stripe_gateway.metrics.average_response_time = 1.5
        stripe_gateway.status = GatewayStatus.ACTIVE
        
        metrics = manager.get_gateway_metrics()
        
        assert "stripe" in metrics
        assert "paypal" in metrics
        assert metrics["stripe"]["total_requests"] == 100
        assert metrics["stripe"]["successful_requests"] == 95
        assert metrics["stripe"]["error_rate"] == 5.0
        assert metrics["stripe"]["status"] == "active"
    
    def test_get_overall_metrics(self):
        """Testa obtenção de métricas gerais"""
        manager = MultiGatewayManager(self.config)
        
        # Configurar métricas de teste
        stripe_gateway = manager.gateways["stripe"]
        paypal_gateway = manager.gateways["paypal"]
        
        stripe_gateway.metrics.total_requests = 100
        stripe_gateway.metrics.successful_requests = 95
        stripe_gateway.status = GatewayStatus.ACTIVE
        
        paypal_gateway.metrics.total_requests = 50
        paypal_gateway.metrics.successful_requests = 45
        paypal_gateway.status = GatewayStatus.ACTIVE
        
        overall_metrics = manager.get_overall_metrics()
        
        assert overall_metrics["total_requests"] == 150
        assert overall_metrics["total_successful"] == 140
        assert overall_metrics["total_failed"] == 10
        assert overall_metrics["overall_success_rate"] == 93.33
        assert overall_metrics["active_gateways"] == 2
        assert overall_metrics["total_gateways"] == 2
        assert overall_metrics["availability_percentage"] == 100.0
    
    @patch('infrastructure.payments.multi_gateway.asyncio.create_task')
    async def test_shutdown(self, mock_create_task):
        """Testa desligamento do gerenciador"""
        manager = MultiGatewayManager(self.config)
        
        # Mock da task
        mock_task = AsyncMock()
        manager.health_check_task = mock_task
        
        await manager.shutdown()
        
        mock_task.cancel.assert_called_once()


class TestConvenienceFunctions:
    """Testes para funções de conveniência"""
    
    @patch('infrastructure.payments.multi_gateway.MultiGatewayManager')
    async def test_create_multi_gateway_manager(self, mock_manager_class):
        """Testa função de conveniência create_multi_gateway_manager"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        config = {"test": "config"}
        result = await create_multi_gateway_manager(config)
        
        mock_manager_class.assert_called_once_with(config)
        assert result == mock_manager
    
    @patch('infrastructure.payments.multi_gateway.MultiGatewayManager')
    async def test_process_payment_multi_gateway(self, mock_manager_class):
        """Testa função de conveniência process_payment_multi_gateway"""
        mock_manager = Mock()
        mock_manager.process_payment = AsyncMock(return_value={"success": True})
        mock_manager.shutdown = AsyncMock()
        mock_manager_class.return_value = mock_manager
        
        payment_data = {"amount": 1000}
        config = {"test": "config"}
        
        result = await process_payment_multi_gateway(payment_data, config)
        
        mock_manager_class.assert_called_once_with(config)
        mock_manager.process_payment.assert_called_once_with(payment_data)
        mock_manager.shutdown.assert_called_once()
        assert result == {"success": True}


class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_gateway_config_invalid_type(self):
        """Testa configuração com tipo de gateway inválido"""
        config = {
            "gateways": {
                "invalid": {
                    "type": "invalid_type",
                    "endpoint": "https://api.test.com",
                    "api_key": "test_key"
                }
            }
        }
        
        manager = MultiGatewayManager(config)
        assert len(manager.gateways) == 0
    
    def test_gateway_config_disabled(self):
        """Testa configuração com gateway desabilitado"""
        config = {
            "gateways": {
                "stripe": {
                    "type": "stripe",
                    "endpoint": "https://api.stripe.com",
                    "api_key": "sk_test_123",
                    "enabled": False
                }
            }
        }
        
        manager = MultiGatewayManager(config)
        assert len(manager.gateways) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 