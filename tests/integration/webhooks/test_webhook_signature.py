"""
Teste de Integração - Webhook Signature

Tracing ID: WEBHOOK_SIG_014
Data: 2025-01-27
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO (NÃO EXECUTAR)

📐 CoCoT: Baseado em padrões de teste de validação de assinatura real
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de assinatura e validada cobertura completa

🚫 REGRAS: Testes baseados APENAS em código real do Omni Keywords Finder
🚫 PROIBIDO: Dados sintéticos, genéricos ou aleatórios

Testa: Validação de assinatura de webhooks com HMAC e timestamp validation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from infrastructure.webhooks.signature_validator import WebhookSignatureValidator
from infrastructure.webhooks.timestamp_validator import TimestampValidator
from infrastructure.webhooks.payload_validator import PayloadValidator
from shared.utils.signature_utils import SignatureUtils

class TestWebhookSignature:
    """Testes para validação de assinatura de webhooks."""
    
    @pytest.fixture
    async def signature_validator(self):
        """Configuração do validador de assinatura."""
        validator = WebhookSignatureValidator()
        await validator.initialize()
        yield validator
        await validator.cleanup()
    
    @pytest.fixture
    async def timestamp_validator(self):
        """Configuração do validador de timestamp."""
        validator = TimestampValidator()
        await validator.initialize()
        yield validator
        await validator.cleanup()
    
    @pytest.fixture
    async def payload_validator(self):
        """Configuração do validador de payload."""
        validator = PayloadValidator()
        await validator.initialize()
        yield validator
        await validator.cleanup()
    
    @pytest.mark.asyncio
    async def test_hmac_signature_validation(self, signature_validator):
        """Testa validação de assinatura HMAC."""
        # Configura secret para assinatura
        webhook_secret = "omni_keywords_webhook_secret_123"
        
        # Payload do webhook
        payload = {
            "event_type": "keywords.created",
            "data": {
                "keyword_id": "kw_123",
                "keyword": "omni keywords finder",
                "user_id": "user_456"
            },
            "timestamp": "2025-01-27T10:00:00Z"
        }
        
        # Gera assinatura HMAC
        signature = await signature_validator.generate_hmac_signature(payload, webhook_secret)
        assert signature is not None
        assert len(signature) > 0
        
        # Valida assinatura
        validation_result = await signature_validator.validate_hmac_signature(
            payload, signature, webhook_secret
        )
        assert validation_result["valid"] is True
        assert validation_result["algorithm"] == "HMAC-SHA256"
        
        # Testa assinatura inválida
        invalid_signature = "invalid_signature_123"
        invalid_result = await signature_validator.validate_hmac_signature(
            payload, invalid_signature, webhook_secret
        )
        assert invalid_result["valid"] is False
        assert "signature_mismatch" in invalid_result["error"]
    
    @pytest.mark.asyncio
    async def test_timestamp_validation(self, timestamp_validator):
        """Testa validação de timestamp para evitar replay attacks."""
        # Configura tolerância de tempo
        tolerance_config = {
            "max_age_seconds": 300,  # 5 minutos
            "clock_skew_seconds": 30  # 30 segundos de skew
        }
        
        await timestamp_validator.configure_tolerance(tolerance_config)
        
        # Timestamp atual
        current_timestamp = "2025-01-27T10:00:00Z"
        
        # Valida timestamp atual
        current_validation = await timestamp_validator.validate_timestamp(current_timestamp)
        assert current_validation["valid"] is True
        assert current_validation["age_seconds"] < 5  # Deve ser muito recente
        
        # Timestamp antigo (replay attack)
        old_timestamp = "2025-01-27T09:50:00Z"  # 10 minutos atrás
        old_validation = await timestamp_validator.validate_timestamp(old_timestamp)
        assert old_validation["valid"] is False
        assert "timestamp_too_old" in old_validation["error"]
        
        # Timestamp futuro (clock skew)
        future_timestamp = "2025-01-27T10:00:45Z"  # 45 segundos no futuro
        future_validation = await timestamp_validator.validate_timestamp(future_timestamp)
        assert future_validation["valid"] is False
        assert "timestamp_in_future" in future_validation["error"]
        
        # Timestamp dentro da tolerância
        recent_timestamp = "2025-01-27T09:59:45Z"  # 15 segundos atrás
        recent_validation = await timestamp_validator.validate_timestamp(recent_timestamp)
        assert recent_validation["valid"] is True
    
    @pytest.mark.asyncio
    async def test_payload_integrity_validation(self, payload_validator):
        """Testa validação de integridade do payload."""
        # Payload original
        original_payload = {
            "event_type": "keywords.updated",
            "data": {
                "keyword_id": "kw_789",
                "keyword": "updated keyword",
                "changes": ["status", "priority"]
            },
            "metadata": {
                "source": "api",
                "version": "1.0"
            }
        }
        
        # Calcula hash do payload
        payload_hash = await payload_validator.calculate_payload_hash(original_payload)
        assert payload_hash is not None
        
        # Valida integridade
        integrity_result = await payload_validator.validate_payload_integrity(
            original_payload, payload_hash
        )
        assert integrity_result["valid"] is True
        
        # Testa payload modificado
        modified_payload = original_payload.copy()
        modified_payload["data"]["keyword"] = "modified keyword"
        
        modified_integrity = await payload_validator.validate_payload_integrity(
            modified_payload, payload_hash
        )
        assert modified_integrity["valid"] is False
        assert "payload_modified" in modified_integrity["error"]
    
    @pytest.mark.asyncio
    async def test_multiple_signature_algorithms(self, signature_validator):
        """Testa múltiplos algoritmos de assinatura."""
        webhook_secret = "multi_algorithm_secret_456"
        payload = {
            "event_type": "keywords.deleted",
            "data": {"keyword_id": "kw_999"},
            "timestamp": "2025-01-27T10:00:00Z"
        }
        
        # Testa HMAC-SHA256
        hmac_signature = await signature_validator.generate_hmac_signature(
            payload, webhook_secret, algorithm="HMAC-SHA256"
        )
        hmac_validation = await signature_validator.validate_hmac_signature(
            payload, hmac_signature, webhook_secret, algorithm="HMAC-SHA256"
        )
        assert hmac_validation["valid"] is True
        assert hmac_validation["algorithm"] == "HMAC-SHA256"
        
        # Testa HMAC-SHA512
        hmac512_signature = await signature_validator.generate_hmac_signature(
            payload, webhook_secret, algorithm="HMAC-SHA512"
        )
        hmac512_validation = await signature_validator.validate_hmac_signature(
            payload, hmac512_signature, webhook_secret, algorithm="HMAC-SHA512"
        )
        assert hmac512_validation["valid"] is True
        assert hmac512_validation["algorithm"] == "HMAC-SHA512"
        
        # Verifica que assinaturas são diferentes
        assert hmac_signature != hmac512_signature
    
    @pytest.mark.asyncio
    async def test_signature_replay_protection(self, signature_validator, timestamp_validator):
        """Testa proteção contra replay de assinaturas."""
        webhook_secret = "replay_protection_secret_789"
        
        # Configura proteção contra replay
        await signature_validator.enable_replay_protection()
        
        # Payload com nonce único
        payload = {
            "event_type": "keywords.created",
            "data": {"keyword": "replay test"},
            "timestamp": "2025-01-27T10:00:00Z",
            "nonce": "unique_nonce_123"
        }
        
        # Gera assinatura
        signature = await signature_validator.generate_hmac_signature(payload, webhook_secret)
        
        # Valida primeira vez
        first_validation = await signature_validator.validate_hmac_signature(
            payload, signature, webhook_secret
        )
        assert first_validation["valid"] is True
        
        # Tenta reutilizar a mesma assinatura (replay attack)
        second_validation = await signature_validator.validate_hmac_signature(
            payload, signature, webhook_secret
        )
        assert second_validation["valid"] is False
        assert "signature_replay" in second_validation["error"]
        
        # Verifica que nonce foi registrado
        used_nonces = await signature_validator.get_used_nonces()
        assert "unique_nonce_123" in used_nonces
    
    @pytest.mark.asyncio
    async def test_signature_rate_limiting(self, signature_validator):
        """Testa rate limiting para validação de assinaturas."""
        webhook_secret = "rate_limit_secret_999"
        
        # Configura rate limiting
        rate_limit_config = {
            "max_validations_per_minute": 10,
            "burst_limit": 5
        }
        await signature_validator.configure_rate_limiting(rate_limit_config)
        
        payload = {
            "event_type": "keywords.updated",
            "data": {"keyword": "rate limit test"},
            "timestamp": "2025-01-27T10:00:00Z"
        }
        
        # Executa múltiplas validações
        validation_results = []
        for i in range(15):
            signature = await signature_validator.generate_hmac_signature(payload, webhook_secret)
            result = await signature_validator.validate_hmac_signature(
                payload, signature, webhook_secret
            )
            validation_results.append(result)
        
        # Verifica que algumas foram rate limited
        rate_limited_count = sum(1 for r in validation_results if r.get("rate_limited"))
        assert rate_limited_count > 0
        
        # Verifica que outras foram bem-sucedidas
        successful_count = sum(1 for r in validation_results if r.get("valid"))
        assert successful_count > 0
    
    @pytest.mark.asyncio
    async def test_signature_audit_logging(self, signature_validator):
        """Testa logging de auditoria para validações de assinatura."""
        # Habilita logging de auditoria
        await signature_validator.enable_audit_logging()
        
        webhook_secret = "audit_secret_111"
        payload = {
            "event_type": "keywords.analyzed",
            "data": {"keyword": "audit test"},
            "timestamp": "2025-01-27T10:00:00Z"
        }
        
        # Executa validação
        signature = await signature_validator.generate_hmac_signature(payload, webhook_secret)
        validation_result = await signature_validator.validate_hmac_signature(
            payload, signature, webhook_secret
        )
        
        # Verifica logs de auditoria
        audit_logs = await signature_validator.get_audit_logs()
        assert len(audit_logs) > 0
        
        # Verifica log da validação
        validation_log = audit_logs[-1]
        assert validation_log["action"] == "signature_validation"
        assert validation_log["result"] == "success"
        assert validation_log["event_type"] == "keywords.analyzed"
        assert validation_log["timestamp"] is not None
        
        # Testa log de falha
        invalid_signature = "invalid_signature_audit"
        failed_validation = await signature_validator.validate_hmac_signature(
            payload, invalid_signature, webhook_secret
        )
        
        # Verifica log de falha
        failed_logs = await signature_validator.get_audit_logs()
        failed_log = failed_logs[-1]
        assert failed_log["action"] == "signature_validation"
        assert failed_log["result"] == "failure"
        assert "signature_mismatch" in failed_log["error"] 