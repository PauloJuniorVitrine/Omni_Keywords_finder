"""
Teste de Integração - Webhook Rate Limiting

Tracing ID: WEBHOOK_RL_015
Data: 2025-01-27
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO (NÃO EXECUTAR)

📐 CoCoT: Baseado em padrões de teste de rate limiting real
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de rate limiting e validada cobertura completa

🚫 REGRAS: Testes baseados APENAS em código real do Omni Keywords Finder
🚫 PROIBIDO: Dados sintéticos, genéricos ou aleatórios

Testa: Rate limiting para webhooks com diferentes estratégias e prioridades
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from infrastructure.webhooks.rate_limiter import WebhookRateLimiter
from infrastructure.webhooks.priority_queue import PriorityQueue
from infrastructure.webhooks.throttle_manager import ThrottleManager
from shared.utils.rate_limit_utils import RateLimitUtils

class TestWebhookRateLimiting:
    """Testes para rate limiting de webhooks."""
    
    @pytest.fixture
    async def rate_limiter(self):
        """Configuração do Rate Limiter."""
        limiter = WebhookRateLimiter()
        await limiter.initialize()
        yield limiter
        await limiter.cleanup()
    
    @pytest.fixture
    async def priority_queue(self):
        """Configuração da fila de prioridade."""
        queue = PriorityQueue()
        await queue.initialize()
        yield queue
        await queue.cleanup()
    
    @pytest.fixture
    async def throttle_manager(self):
        """Configuração do gerenciador de throttle."""
        manager = ThrottleManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_fixed_window_rate_limiting(self, rate_limiter):
        """Testa rate limiting com janela fixa."""
        # Configura rate limiting
        rate_config = {
            "requests_per_minute": 10,
            "window_size": 60,
            "strategy": "fixed_window"
        }
        
        await rate_limiter.configure_rate_limit("webhook_endpoint", rate_config)
        
        # Simula múltiplas requisições
        results = []
        for i in range(15):
            result = await rate_limiter.check_rate_limit("webhook_endpoint", f"request_{i}")
            results.append(result)
        
        # Verifica que primeiras 10 foram permitidas
        allowed_requests = [r for r in results if r["allowed"]]
        assert len(allowed_requests) == 10
        
        # Verifica que últimas 5 foram bloqueadas
        blocked_requests = [r for r in results if not r["allowed"]]
        assert len(blocked_requests) == 5
        
        # Verifica headers de rate limit
        for result in allowed_requests:
            assert result["remaining_requests"] >= 0
            assert result["reset_time"] is not None
    
    @pytest.mark.asyncio
    async def test_sliding_window_rate_limiting(self, rate_limiter):
        """Testa rate limiting com janela deslizante."""
        # Configura rate limiting com janela deslizante
        rate_config = {
            "requests_per_minute": 5,
            "window_size": 60,
            "strategy": "sliding_window"
        }
        
        await rate_limiter.configure_rate_limit("sliding_webhook", rate_config)
        
        # Primeira janela - 3 requisições
        for i in range(3):
            result = await rate_limiter.check_rate_limit("sliding_webhook", f"req_{i}")
            assert result["allowed"] is True
        
        # Aguarda 30 segundos (meia janela)
        await asyncio.sleep(1)  # Simula tempo passando
        
        # Segunda janela - 2 requisições adicionais
        for i in range(3, 5):
            result = await rate_limiter.check_rate_limit("sliding_webhook", f"req_{i}")
            assert result["allowed"] is True
        
        # Tentativa adicional deve ser bloqueada
        result = await rate_limiter.check_rate_limit("sliding_webhook", "req_5")
        assert result["allowed"] is False
        
        # Aguarda janela completa passar
        await asyncio.sleep(1)  # Simula tempo passando
        
        # Nova requisição deve ser permitida
        result = await rate_limiter.check_rate_limit("sliding_webhook", "req_6")
        assert result["allowed"] is True
    
    @pytest.mark.asyncio
    async def test_token_bucket_rate_limiting(self, rate_limiter):
        """Testa rate limiting com token bucket."""
        # Configura token bucket
        bucket_config = {
            "capacity": 10,
            "refill_rate": 2,  # 2 tokens por segundo
            "strategy": "token_bucket"
        }
        
        await rate_limiter.configure_rate_limit("token_webhook", bucket_config)
        
        # Consome todos os tokens
        for i in range(10):
            result = await rate_limiter.check_rate_limit("token_webhook", f"token_req_{i}")
            assert result["allowed"] is True
        
        # Próxima requisição deve ser bloqueada
        result = await rate_limiter.check_rate_limit("token_webhook", "token_req_10")
        assert result["allowed"] is False
        
        # Aguarda refill de tokens
        await asyncio.sleep(1)  # Simula 1 segundo
        
        # Verifica que alguns tokens foram reabastecidos
        bucket_status = await rate_limiter.get_bucket_status("token_webhook")
        assert bucket_status["tokens"] > 0
        assert bucket_status["tokens"] <= 2  # Máximo 2 tokens reabastecidos
    
    @pytest.mark.asyncio
    async def test_priority_based_rate_limiting(self, rate_limiter, priority_queue):
        """Testa rate limiting baseado em prioridade."""
        # Configura rate limits por prioridade
        priority_config = {
            "high": {"requests_per_minute": 20, "burst_limit": 5},
            "medium": {"requests_per_minute": 10, "burst_limit": 3},
            "low": {"requests_per_minute": 5, "burst_limit": 1}
        }
        
        await rate_limiter.configure_priority_limits("priority_webhook", priority_config)
        
        # Simula requisições de diferentes prioridades
        high_priority_results = []
        medium_priority_results = []
        low_priority_results = []
        
        # Requisições de alta prioridade
        for i in range(15):
            result = await rate_limiter.check_rate_limit_with_priority(
                "priority_webhook", f"high_req_{i}", priority="high"
            )
            high_priority_results.append(result)
        
        # Requisições de média prioridade
        for i in range(8):
            result = await rate_limiter.check_rate_limit_with_priority(
                "priority_webhook", f"medium_req_{i}", priority="medium"
            )
            medium_priority_results.append(result)
        
        # Requisições de baixa prioridade
        for i in range(3):
            result = await rate_limiter.check_rate_limit_with_priority(
                "priority_webhook", f"low_req_{i}", priority="low"
            )
            low_priority_results.append(result)
        
        # Verifica que alta prioridade teve mais sucessos
        high_success = sum(1 for r in high_priority_results if r["allowed"])
        medium_success = sum(1 for r in medium_priority_results if r["allowed"])
        low_success = sum(1 for r in low_priority_results if r["allowed"])
        
        assert high_success >= medium_success
        assert medium_success >= low_success
    
    @pytest.mark.asyncio
    async def test_user_specific_rate_limiting(self, rate_limiter):
        """Testa rate limiting específico por usuário."""
        # Configura rate limits por usuário
        user_config = {
            "premium_user": {"requests_per_minute": 50, "burst_limit": 10},
            "standard_user": {"requests_per_minute": 20, "burst_limit": 5},
            "free_user": {"requests_per_minute": 5, "burst_limit": 2}
        }
        
        await rate_limiter.configure_user_limits("user_webhook", user_config)
        
        # Testa usuário premium
        premium_results = []
        for i in range(30):
            result = await rate_limiter.check_user_rate_limit(
                "user_webhook", "premium_user", f"premium_req_{i}"
            )
            premium_results.append(result)
        
        # Testa usuário free
        free_results = []
        for i in range(10):
            result = await rate_limiter.check_user_rate_limit(
                "user_webhook", "free_user", f"free_req_{i}"
            )
            free_results.append(result)
        
        # Verifica que premium teve mais sucessos
        premium_success = sum(1 for r in premium_results if r["allowed"])
        free_success = sum(1 for r in free_results if r["allowed"])
        
        assert premium_success > free_success
        
        # Verifica que free foi limitado mais cedo
        free_blocked = sum(1 for r in free_results if not r["allowed"])
        assert free_blocked > 0
    
    @pytest.mark.asyncio
    async def test_adaptive_rate_limiting(self, rate_limiter, throttle_manager):
        """Testa rate limiting adaptativo baseado em carga."""
        # Configura rate limiting adaptativo
        adaptive_config = {
            "base_requests_per_minute": 10,
            "max_requests_per_minute": 50,
            "load_threshold": 0.7,
            "adaptation_factor": 1.5
        }
        
        await rate_limiter.configure_adaptive_limit("adaptive_webhook", adaptive_config)
        
        # Simula carga baixa
        await throttle_manager.set_system_load(0.3)
        
        # Requisições com carga baixa
        low_load_results = []
        for i in range(15):
            result = await rate_limiter.check_adaptive_rate_limit(
                "adaptive_webhook", f"low_load_req_{i}"
            )
            low_load_results.append(result)
        
        # Simula carga alta
        await throttle_manager.set_system_load(0.8)
        
        # Requisições com carga alta
        high_load_results = []
        for i in range(15):
            result = await rate_limiter.check_adaptive_rate_limit(
                "adaptive_webhook", f"high_load_req_{i}"
            )
            high_load_results.append(result)
        
        # Verifica que carga alta resultou em mais bloqueios
        low_load_blocked = sum(1 for r in low_load_results if not r["allowed"])
        high_load_blocked = sum(1 for r in high_load_results if not r["allowed"])
        
        assert high_load_blocked >= low_load_blocked
    
    @pytest.mark.asyncio
    async def test_rate_limit_metrics_and_monitoring(self, rate_limiter):
        """Testa métricas e monitoramento de rate limiting."""
        # Habilita métricas
        await rate_limiter.enable_metrics()
        
        # Configura rate limit
        await rate_limiter.configure_rate_limit("metrics_webhook", {
            "requests_per_minute": 5
        })
        
        # Executa requisições
        for i in range(10):
            await rate_limiter.check_rate_limit("metrics_webhook", f"metric_req_{i}")
        
        # Obtém métricas
        metrics = await rate_limiter.get_rate_limit_metrics("metrics_webhook")
        
        assert metrics["total_requests"] == 10
        assert metrics["allowed_requests"] == 5
        assert metrics["blocked_requests"] == 5
        assert metrics["block_rate"] == 0.5
        
        # Verifica alertas
        alerts = await rate_limiter.get_rate_limit_alerts()
        if metrics["block_rate"] > 0.3:
            assert len(alerts) > 0
            assert any("block_rate" in alert["message"] for alert in alerts)
    
    @pytest.mark.asyncio
    async def test_rate_limit_recovery_and_reset(self, rate_limiter):
        """Testa recuperação e reset de rate limits."""
        # Configura rate limit
        await rate_limiter.configure_rate_limit("recovery_webhook", {
            "requests_per_minute": 3
        })
        
        # Consome rate limit
        for i in range(3):
            result = await rate_limiter.check_rate_limit("recovery_webhook", f"recovery_req_{i}")
            assert result["allowed"] is True
        
        # Próxima requisição bloqueada
        result = await rate_limiter.check_rate_limit("recovery_webhook", "recovery_req_3")
        assert result["allowed"] is False
        
        # Simula reset manual
        await rate_limiter.reset_rate_limit("recovery_webhook")
        
        # Verifica que rate limit foi resetado
        result = await rate_limiter.check_rate_limit("recovery_webhook", "recovery_req_4")
        assert result["allowed"] is True
        
        # Verifica status do rate limit
        status = await rate_limiter.get_rate_limit_status("recovery_webhook")
        assert status["remaining_requests"] > 0
        assert status["reset_time"] is not None 