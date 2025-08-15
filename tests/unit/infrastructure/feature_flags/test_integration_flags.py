"""
Testes Unitários - Feature Flags para Integrações

Tracing ID: FF-001-TEST
Data/Hora: 2024-12-19 23:50:00 UTC
Versão: 1.0
Status: Implementação Inicial

Testes unitários para o sistema de feature flags de integrações externas.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Importar módulos a serem testados
from infrastructure.feature_flags.integration_flags import (
    IntegrationFeatureFlags,
    FeatureFlagConfig,
    Environment,
    IntegrationType,
    RolloutStrategy,
    get_integration_flags,
    is_integration_enabled,
    get_integration_fallback
)

class TestEnvironment:
    """Testes para enum Environment"""
    
    def test_environment_values(self):
        """Testa valores do enum Environment"""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TESTING.value == "testing"

class TestIntegrationType:
    """Testes para enum IntegrationType"""
    
    def test_integration_type_values(self):
        """Testa valores do enum IntegrationType"""
        assert IntegrationType.GOOGLE_TRENDS.value == "google_trends"
        assert IntegrationType.GOOGLE_SEARCH_CONSOLE.value == "google_search_console"
        assert IntegrationType.SEMRUSH.value == "semrush"
        assert IntegrationType.WEBHOOK.value == "webhook"
        assert IntegrationType.PAYMENT_GATEWAY.value == "payment_gateway"

class TestRolloutStrategy:
    """Testes para enum RolloutStrategy"""
    
    def test_rollout_strategy_values(self):
        """Testa valores do enum RolloutStrategy"""
        assert RolloutStrategy.IMMEDIATE.value == "immediate"
        assert RolloutStrategy.PERCENTAGE.value == "percentage"
        assert RolloutStrategy.GRADUAL.value == "gradual"
        assert RolloutStrategy.CANARY.value == "canary"
        assert RolloutStrategy.A_B_TEST.value == "a_b_test"

class TestFeatureFlagConfig:
    """Testes para FeatureFlagConfig"""
    
    def test_feature_flag_config_creation(self):
        """Testa criação de FeatureFlagConfig"""
        config = FeatureFlagConfig(
            name="test_flag",
            integration_type=IntegrationType.GOOGLE_TRENDS
        )
        
        assert config.name == "test_flag"
        assert config.integration_type == IntegrationType.GOOGLE_TRENDS
        assert config.enabled is False
        assert config.rollout_strategy == RolloutStrategy.IMMEDIATE
        assert config.rollout_percentage == 100.0
        assert config.fallback_enabled is True
        assert config.environment == Environment.DEVELOPMENT
        assert config.created_at is not None
        assert config.updated_at is not None

    def test_feature_flag_config_with_custom_values(self):
        """Testa criação com valores customizados"""
        now = datetime.utcnow()
        config = FeatureFlagConfig(
            name="custom_flag",
            integration_type=IntegrationType.WEBHOOK,
            enabled=True,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50.0,
            rollout_start_time=now,
            rollout_end_time=now + timedelta(hours=1),
            fallback_enabled=False,
            fallback_config={"provider": "mock"},
            environment=Environment.PRODUCTION,
            metadata={"owner": "test-team"}
        )
        
        assert config.name == "custom_flag"
        assert config.integration_type == IntegrationType.WEBHOOK
        assert config.enabled is True
        assert config.rollout_strategy == RolloutStrategy.PERCENTAGE
        assert config.rollout_percentage == 50.0
        assert config.rollout_start_time == now
        assert config.rollout_end_time == now + timedelta(hours=1)
        assert config.fallback_enabled is False
        assert config.fallback_config == {"provider": "mock"}
        assert config.environment == Environment.PRODUCTION
        assert config.metadata == {"owner": "test-team"}

class TestIntegrationFeatureFlags:
    """Testes para IntegrationFeatureFlags"""
    
    @pytest.fixture
    def feature_flags(self):
        """Fixture para instância de feature flags"""
        return IntegrationFeatureFlags(
            redis_url=None,
            environment=Environment.TESTING
        )
    
    @pytest.fixture
    def mock_redis(self):
        """Fixture para mock do Redis"""
        with patch('infrastructure.feature_flags.integration_flags.redis') as mock_redis:
            mock_client = Mock()
            mock_redis.from_url.return_value = mock_client
            yield mock_client
    
    def test_initialization(self, feature_flags):
        """Testa inicialização do sistema"""
        assert feature_flags.environment == Environment.TESTING
        assert feature_flags.cache_ttl == 300
        assert feature_flags.redis_client is None
        assert len(feature_flags._default_configs) > 0

    def test_initialization_with_redis(self, mock_redis):
        """Testa inicialização com Redis"""
        feature_flags = IntegrationFeatureFlags(
            redis_url="redis://localhost:6379",
            environment=Environment.DEVELOPMENT
        )
        
        assert feature_flags.redis_client is not None
        mock_redis.ping.assert_called_once()

    def test_initialization_redis_failure(self):
        """Testa inicialização com falha no Redis"""
        with patch('infrastructure.feature_flags.integration_flags.redis') as mock_redis:
            mock_redis.from_url.side_effect = Exception("Connection failed")
            
            feature_flags = IntegrationFeatureFlags(
                redis_url="redis://localhost:6379",
                environment=Environment.DEVELOPMENT
            )
            
            assert feature_flags.redis_client is None

    def test_get_default_fallback_config(self, feature_flags):
        """Testa obtenção de configuração de fallback padrão"""
        # Teste para Google Trends
        fallback = feature_flags._get_default_fallback_config(IntegrationType.GOOGLE_TRENDS)
        assert fallback["fallback_provider"] == "mock_data"
        assert fallback["cache_duration"] == 3600
        assert fallback["retry_attempts"] == 3
        
        # Teste para Webhook
        fallback = feature_flags._get_default_fallback_config(IntegrationType.WEBHOOK)
        assert fallback["fallback_provider"] == "queue_system"
        assert fallback["retry_attempts"] == 5
        assert fallback["retry_delay"] == 60
        
        # Teste para integração não mapeada
        fallback = feature_flags._get_default_fallback_config(IntegrationType.ANALYTICS)
        assert fallback["fallback_provider"] == "mock_data"

    def test_get_config(self, feature_flags):
        """Testa obtenção de configuração"""
        config = feature_flags.get_config(IntegrationType.GOOGLE_TRENDS)
        
        assert config is not None
        assert config.name == "google_trends_feature_flag"
        assert config.integration_type == IntegrationType.GOOGLE_TRENDS
        assert config.environment == Environment.TESTING

    def test_get_config_with_string(self, feature_flags):
        """Testa obtenção de configuração com string"""
        config = feature_flags.get_config("google_trends")
        
        assert config is not None
        assert config.integration_type == IntegrationType.GOOGLE_TRENDS

    def test_get_config_not_found(self, feature_flags):
        """Testa obtenção de configuração inexistente"""
        # Simular configuração não encontrada
        feature_flags._default_configs = {}
        
        config = feature_flags.get_config(IntegrationType.GOOGLE_TRENDS)
        assert config is None

    def test_is_enabled_immediate_strategy(self, feature_flags):
        """Testa verificação de habilitação com estratégia imediata"""
        # Configurar flag habilitado
        feature_flags._default_configs["google_trends"].enabled = True
        feature_flags._default_configs["google_trends"].rollout_strategy = RolloutStrategy.IMMEDIATE
        
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS)
        assert result is True

    def test_is_enabled_disabled_flag(self, feature_flags):
        """Testa verificação de flag desabilitado"""
        # Configurar flag desabilitado
        feature_flags._default_configs["google_trends"].enabled = False
        
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS)
        assert result is False

    def test_is_enabled_percentage_strategy(self, feature_flags):
        """Testa verificação com estratégia de porcentagem"""
        # Configurar flag com 50% de rollout
        feature_flags._default_configs["google_trends"].enabled = True
        feature_flags._default_configs["google_trends"].rollout_strategy = RolloutStrategy.PERCENTAGE
        feature_flags._default_configs["google_trends"].rollout_percentage = 50.0
        
        # Teste sem user_id (deve retornar False para < 100%)
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS)
        assert result is False
        
        # Teste com user_id específico
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS, user_id="test_user")
        # Resultado pode variar dependendo do hash, mas deve ser consistente
        assert isinstance(result, bool)

    def test_is_enabled_gradual_strategy(self, feature_flags):
        """Testa verificação com estratégia gradual"""
        now = datetime.utcnow()
        
        # Configurar rollout gradual
        feature_flags._default_configs["google_trends"].enabled = True
        feature_flags._default_configs["google_trends"].rollout_strategy = RolloutStrategy.GRADUAL
        feature_flags._default_configs["google_trends"].rollout_percentage = 50.0
        feature_flags._default_configs["google_trends"].rollout_start_time = now - timedelta(hours=1)
        feature_flags._default_configs["google_trends"].rollout_end_time = now + timedelta(hours=1)
        
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS)
        assert isinstance(result, bool)

    def test_is_enabled_canary_strategy(self, feature_flags):
        """Testa verificação com estratégia canary"""
        # Configurar rollout canary
        feature_flags._default_configs["google_trends"].enabled = True
        feature_flags._default_configs["google_trends"].rollout_strategy = RolloutStrategy.CANARY
        
        # Teste sem user_id
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS)
        assert result is False
        
        # Teste com user_id canary
        context = {"canary_users": ["canary_user"]}
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS, user_id="canary_user", context=context)
        assert result is True
        
        # Teste com user_id não canary
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS, user_id="regular_user", context=context)
        assert result is False

    def test_is_enabled_ab_test_strategy(self, feature_flags):
        """Testa verificação com estratégia A/B test"""
        # Configurar A/B test
        feature_flags._default_configs["google_trends"].enabled = True
        feature_flags._default_configs["google_trends"].rollout_strategy = RolloutStrategy.A_B_TEST
        
        # Teste sem user_id
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS)
        assert result is False
        
        # Teste com user_id
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS, user_id="test_user")
        assert isinstance(result, bool)

    def test_check_percentage_rollout(self, feature_flags):
        """Testa verificação de rollout por porcentagem"""
        config = FeatureFlagConfig(
            name="test",
            integration_type=IntegrationType.GOOGLE_TRENDS,
            rollout_percentage=50.0
        )
        
        # Teste sem user_id
        result = feature_flags._check_percentage_rollout(config, None)
        assert result is False  # 50% < 100%
        
        # Teste com user_id
        result = feature_flags._check_percentage_rollout(config, "test_user")
        assert isinstance(result, bool)

    def test_check_gradual_rollout(self, feature_flags):
        """Testa verificação de rollout gradual"""
        now = datetime.utcnow()
        
        # Configuração sem tempos definidos
        config = FeatureFlagConfig(
            name="test",
            integration_type=IntegrationType.GOOGLE_TRENDS
        )
        result = feature_flags._check_gradual_rollout(config)
        assert result is True
        
        # Configuração com tempos definidos
        config.rollout_start_time = now - timedelta(hours=1)
        config.rollout_end_time = now + timedelta(hours=1)
        config.rollout_percentage = 50.0
        
        result = feature_flags._check_gradual_rollout(config)
        assert isinstance(result, bool)

    def test_check_canary_rollout(self, feature_flags):
        """Testa verificação de rollout canary"""
        config = FeatureFlagConfig(
            name="test",
            integration_type=IntegrationType.GOOGLE_TRENDS
        )
        
        # Teste sem user_id
        result = feature_flags._check_canary_rollout(config, None, {})
        assert result is False
        
        # Teste com user_id canary
        context = {"canary_users": ["canary_user"]}
        result = feature_flags._check_canary_rollout(config, "canary_user", context)
        assert result is True
        
        # Teste com user_id não canary
        result = feature_flags._check_canary_rollout(config, "regular_user", context)
        assert result is False

    def test_check_ab_test_rollout(self, feature_flags):
        """Testa verificação de rollout A/B test"""
        config = FeatureFlagConfig(
            name="test",
            integration_type=IntegrationType.GOOGLE_TRENDS
        )
        
        # Teste sem user_id
        result = feature_flags._check_ab_test_rollout(config, None)
        assert result is False
        
        # Teste com user_id
        result = feature_flags._check_ab_test_rollout(config, "test_user")
        assert isinstance(result, bool)

    def test_update_config(self, feature_flags):
        """Testa atualização de configuração"""
        # Obter configuração original
        original_config = feature_flags.get_config(IntegrationType.GOOGLE_TRENDS)
        original_enabled = original_config.enabled
        
        # Atualizar configuração
        updates = {"enabled": not original_enabled}
        result = feature_flags.update_config(IntegrationType.GOOGLE_TRENDS, updates)
        
        assert result is True
        
        # Verificar se foi atualizada
        updated_config = feature_flags.get_config(IntegrationType.GOOGLE_TRENDS)
        assert updated_config.enabled != original_enabled

    def test_update_config_invalid_integration(self, feature_flags):
        """Testa atualização de configuração inválida"""
        # Simular configuração não encontrada
        feature_flags._default_configs = {}
        
        result = feature_flags.update_config(IntegrationType.GOOGLE_TRENDS, {"enabled": True})
        assert result is False

    def test_get_fallback_config(self, feature_flags):
        """Testa obtenção de configuração de fallback"""
        # Configurar fallback habilitado
        feature_flags._default_configs["google_trends"].fallback_enabled = True
        feature_flags._default_configs["google_trends"].fallback_config = {"provider": "mock"}
        
        fallback = feature_flags.get_fallback_config(IntegrationType.GOOGLE_TRENDS)
        assert fallback == {"provider": "mock"}
        
        # Configurar fallback desabilitado
        feature_flags._default_configs["google_trends"].fallback_enabled = False
        
        fallback = feature_flags.get_fallback_config(IntegrationType.GOOGLE_TRENDS)
        assert fallback is None

    def test_get_all_configs(self, feature_flags):
        """Testa obtenção de todas as configurações"""
        configs = feature_flags.get_all_configs()
        
        assert isinstance(configs, dict)
        assert len(configs) > 0
        
        # Verificar se todas as integrações estão presentes
        for integration in IntegrationType:
            assert integration.value in configs

    def test_get_health_status(self, feature_flags):
        """Testa obtenção de status de saúde"""
        status = feature_flags.get_health_status()
        
        assert status["status"] == "healthy"
        assert status["environment"] == Environment.TESTING.value
        assert status["redis_status"] == "disconnected"
        assert "total_configs" in status
        assert "enabled_configs" in status
        assert "cache_ttl" in status
        assert "timestamp" in status

    def test_get_health_status_with_redis(self, mock_redis):
        """Testa status de saúde com Redis"""
        feature_flags = IntegrationFeatureFlags(
            redis_url="redis://localhost:6379",
            environment=Environment.DEVELOPMENT
        )
        
        status = feature_flags.get_health_status()
        assert status["redis_status"] == "connected"

    def test_cache_operations(self, feature_flags):
        """Testa operações de cache"""
        # Testar cache válido
        cache_key = "test_key"
        feature_flags._cache_timestamp[cache_key] = datetime.utcnow()
        
        result = feature_flags._is_cache_valid(cache_key)
        assert result is True
        
        # Testar cache expirado
        feature_flags._cache_timestamp[cache_key] = datetime.utcnow() - timedelta(hours=1)
        
        result = feature_flags._is_cache_valid(cache_key)
        assert result is False

    def test_redis_operations(self, mock_redis):
        """Testa operações com Redis"""
        feature_flags = IntegrationFeatureFlags(
            redis_url="redis://localhost:6379",
            environment=Environment.DEVELOPMENT
        )
        
        config = FeatureFlagConfig(
            name="test",
            integration_type=IntegrationType.GOOGLE_TRENDS
        )
        
        # Testar salvamento no Redis
        feature_flags._save_to_redis("test_key", config)
        mock_redis.setex.assert_called_once()
        
        # Testar obtenção do Redis
        mock_redis.get.return_value = json.dumps({
            "name": "test",
            "integration_type": "google_trends",
            "enabled": False,
            "rollout_strategy": "immediate",
            "rollout_percentage": 100.0,
            "rollout_start_time": None,
            "rollout_end_time": None,
            "fallback_enabled": True,
            "fallback_config": None,
            "environment": "development",
            "metadata": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        result = feature_flags._get_from_redis("test_key")
        assert result is not None
        assert result.name == "test"

class TestGlobalFunctions:
    """Testes para funções globais"""
    
    @patch('infrastructure.feature_flags.integration_flags._integration_flags')
    def test_get_integration_flags(self, mock_global_flags):
        """Testa obtenção de instância global"""
        # Simular instância global
        mock_global_flags.return_value = Mock()
        
        result = get_integration_flags()
        assert result is not None

    @patch('infrastructure.feature_flags.integration_flags.get_integration_flags')
    def test_is_integration_enabled(self, mock_get_flags):
        """Testa função de conveniência is_integration_enabled"""
        mock_flags = Mock()
        mock_get_flags.return_value = mock_flags
        mock_flags.is_enabled.return_value = True
        
        result = is_integration_enabled(IntegrationType.GOOGLE_TRENDS, "user123")
        
        assert result is True
        mock_flags.is_enabled.assert_called_once_with(IntegrationType.GOOGLE_TRENDS, "user123", None)

    @patch('infrastructure.feature_flags.integration_flags.get_integration_flags')
    def test_get_integration_fallback(self, mock_get_flags):
        """Testa função de conveniência get_integration_fallback"""
        mock_flags = Mock()
        mock_get_flags.return_value = mock_flags
        mock_flags.get_fallback_config.return_value = {"provider": "mock"}
        
        result = get_integration_fallback(IntegrationType.GOOGLE_TRENDS)
        
        assert result == {"provider": "mock"}
        mock_flags.get_fallback_config.assert_called_once_with(IntegrationType.GOOGLE_TRENDS)

class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def test_is_enabled_with_exception(self, feature_flags):
        """Testa tratamento de exceção em is_enabled"""
        # Simular exceção
        with patch.object(feature_flags, 'get_config', side_effect=Exception("Test error")):
            result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS)
            assert result is False

    def test_get_config_with_exception(self, feature_flags):
        """Testa tratamento de exceção em get_config"""
        # Simular exceção
        with patch.object(feature_flags, '_initialize_default_configs', side_effect=Exception("Test error")):
            result = feature_flags.get_config(IntegrationType.GOOGLE_TRENDS)
            assert result is None

    def test_update_config_with_exception(self, feature_flags):
        """Testa tratamento de exceção em update_config"""
        # Simular exceção
        with patch.object(feature_flags, 'get_config', side_effect=Exception("Test error")):
            result = feature_flags.update_config(IntegrationType.GOOGLE_TRENDS, {"enabled": True})
            assert result is False

    def test_health_status_with_exception(self, feature_flags):
        """Testa tratamento de exceção em get_health_status"""
        # Simular exceção
        with patch.object(feature_flags, 'get_all_configs', side_effect=Exception("Test error")):
            status = feature_flags.get_health_status()
            assert status["status"] == "unhealthy"
            assert "error" in status

class TestIntegrationScenarios:
    """Testes para cenários de integração"""
    
    def test_google_trends_integration_scenario(self, feature_flags):
        """Testa cenário completo para integração Google Trends"""
        # Configurar para desenvolvimento
        feature_flags.environment = Environment.DEVELOPMENT
        feature_flags._default_configs["google_trends"].enabled = True
        feature_flags._default_configs["google_trends"].rollout_strategy = RolloutStrategy.PERCENTAGE
        feature_flags._default_configs["google_trends"].rollout_percentage = 25.0
        
        # Verificar habilitação
        result = feature_flags.is_enabled(IntegrationType.GOOGLE_TRENDS, "user123")
        assert isinstance(result, bool)
        
        # Verificar fallback
        fallback = feature_flags.get_fallback_config(IntegrationType.GOOGLE_TRENDS)
        assert fallback is not None
        assert fallback["fallback_provider"] == "mock_data"

    def test_webhook_integration_scenario(self, feature_flags):
        """Testa cenário completo para integração Webhook"""
        # Configurar para produção
        feature_flags.environment = Environment.PRODUCTION
        feature_flags._default_configs["webhook"].enabled = True
        feature_flags._default_configs["webhook"].rollout_strategy = RolloutStrategy.CANARY
        
        # Verificar habilitação para usuário canary
        context = {"canary_users": ["admin_user"]}
        result = feature_flags.is_enabled(IntegrationType.WEBHOOK, "admin_user", context)
        assert result is True
        
        # Verificar habilitação para usuário regular
        result = feature_flags.is_enabled(IntegrationType.WEBHOOK, "regular_user", context)
        assert result is False

    def test_payment_gateway_integration_scenario(self, feature_flags):
        """Testa cenário completo para integração Payment Gateway"""
        # Configurar para staging
        feature_flags.environment = Environment.STAGING
        feature_flags._default_configs["payment_gateway"].enabled = True
        feature_flags._default_configs["payment_gateway"].rollout_strategy = RolloutStrategy.A_B_TEST
        
        # Verificar habilitação
        result_a = feature_flags.is_enabled(IntegrationType.PAYMENT_GATEWAY, "user_a")
        result_b = feature_flags.is_enabled(IntegrationType.PAYMENT_GATEWAY, "user_b")
        
        # Ambos devem ser booleanos
        assert isinstance(result_a, bool)
        assert isinstance(result_b, bool)
        
        # Verificar fallback
        fallback = feature_flags.get_fallback_config(IntegrationType.PAYMENT_GATEWAY)
        assert fallback is not None
        assert fallback["fallback_provider"] == "alternative_gateway" 