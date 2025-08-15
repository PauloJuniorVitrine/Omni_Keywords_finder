from typing import Dict, List, Optional, Any
"""
Testes unitários para Feature Flags Expandidas
Tracing ID: FEATURE_FLAGS_001
Data: 2024-12-19
Versão: 1.0

Testes para validação do sistema de feature flags:
- Configuração de flags
- Avaliação de contexto
- Decoradores
- Cache e performance
- Métricas e auditoria
"""

import pytest
import time
import os
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request, g
import sys
import tempfile

# Adicionar caminho do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.config.feature_flags import (
    FeatureFlagConfig,
    FeatureFlagType,
    FeatureFlagScope,
    FeatureFlagContext,
    FeatureFlagEvaluator,
    FeatureFlagManager,
    feature_flag,
    feature_flag_value,
    is_feature_enabled,
    get_feature_value,
    create_context_from_request
)


class TestFeatureFlagConfig:
    """Testes para configuração de feature flags."""
    
    def test_feature_flag_config_default(self):
        """Testa configuração padrão."""
        config = FeatureFlagConfig(
            name="test_flag",
            description="Test flag"
        )
        
        assert config.name == "test_flag"
        assert config.description == "Test flag"
        assert config.type == FeatureFlagType.BOOLEAN
        assert config.enabled == False
        assert config.default_value == False
        assert config.scope == FeatureFlagScope.GLOBAL
    
    def test_feature_flag_config_custom(self):
        """Testa configuração customizada."""
        config = FeatureFlagConfig(
            name="custom_flag",
            description="Custom flag",
            type=FeatureFlagType.PERCENTAGE,
            enabled=True,
            default_value=50,
            scope=FeatureFlagScope.USER,
            target_users=["user1", "user2"],
            percentage_rollout=75
        )
        
        assert config.name == "custom_flag"
        assert config.type == FeatureFlagType.PERCENTAGE
        assert config.enabled == True
        assert config.default_value == 50
        assert config.scope == FeatureFlagScope.USER
        assert config.target_users == ["user1", "user2"]
        assert config.percentage_rollout == 75


class TestFeatureFlagContext:
    """Testes para contexto de feature flags."""
    
    def test_feature_flag_context_default(self):
        """Testa contexto padrão."""
        context = FeatureFlagContext()
        
        assert context.user_id is None
        assert context.user_email is None
        assert context.user_role is None
        assert context.ip_address is None
        assert context.environment is None
    
    def test_feature_flag_context_custom(self):
        """Testa contexto customizado."""
        context = FeatureFlagContext(
            user_id="user123",
            user_email="user@example.com",
            user_role="admin",
            ip_address="192.168.1.1",
            environment="production"
        )
        
        assert context.user_id == "user123"
        assert context.user_email == "user@example.com"
        assert context.user_role == "admin"
        assert context.ip_address == "192.168.1.1"
        assert context.environment == "production"


class TestFeatureFlagEvaluator:
    """Testes para avaliador de feature flags."""
    
    @pytest.fixture
    def evaluator(self):
        """Fixture para avaliador."""
        return FeatureFlagEvaluator()
    
    @pytest.fixture
    def boolean_config(self):
        """Fixture para configuração booleana."""
        return FeatureFlagConfig(
            name="test_boolean",
            description="Test boolean flag",
            type=FeatureFlagType.BOOLEAN,
            enabled=True,
            default_value=False
        )
    
    @pytest.fixture
    def context(self):
        """Fixture para contexto."""
        return FeatureFlagContext(
            user_id="user123",
            ip_address="192.168.1.1",
            environment="development"
        )
    
    def test_evaluator_initialization(self, evaluator):
        """Testa inicialização do avaliador."""
        assert evaluator.cache == {}
        assert evaluator.metrics == {}
    
    def test_evaluate_boolean_flag_enabled(self, evaluator, boolean_config, context):
        """Testa avaliação de flag booleana habilitada."""
        result = evaluator.evaluate("test_boolean", context, boolean_config)
        assert result == True
    
    def test_evaluate_boolean_flag_disabled(self, evaluator, context):
        """Testa avaliação de flag booleana desabilitada."""
        config = FeatureFlagConfig(
            name="test_boolean",
            description="Test boolean flag",
            type=FeatureFlagType.BOOLEAN,
            enabled=False,
            default_value=False
        )
        
        result = evaluator.evaluate("test_boolean", context, config)
        assert result == False
    
    def test_evaluate_user_scope_flag(self, evaluator, context):
        """Testa avaliação de flag com escopo de usuário."""
        config = FeatureFlagConfig(
            name="user_flag",
            description="User scope flag",
            type=FeatureFlagType.BOOLEAN,
            enabled=True,
            scope=FeatureFlagScope.USER,
            target_users=["user123", "user456"]
        )
        
        result = evaluator.evaluate("user_flag", context, config)
        assert result == True
    
    def test_evaluate_environment_scope_flag(self, evaluator, context):
        """Testa avaliação de flag com escopo de ambiente."""
        config = FeatureFlagConfig(
            name="env_flag",
            description="Environment scope flag",
            type=FeatureFlagType.BOOLEAN,
            enabled=True,
            scope=FeatureFlagScope.ENVIRONMENT,
            target_environments=["development", "staging"]
        )
        
        result = evaluator.evaluate("env_flag", context, config)
        assert result == True
    
    def test_evaluate_ip_scope_flag(self, evaluator, context):
        """Testa avaliação de flag com escopo de IP."""
        config = FeatureFlagConfig(
            name="ip_flag",
            description="IP scope flag",
            type=FeatureFlagType.BOOLEAN,
            enabled=True,
            scope=FeatureFlagScope.IP,
            target_ips=["192.168.1.1", "10.0.0.1"]
        )
        
        result = evaluator.evaluate("ip_flag", context, config)
        assert result == True
    
    def test_evaluate_percentage_flag(self, evaluator, context):
        """Testa avaliação de flag percentual."""
        config = FeatureFlagConfig(
            name="percentage_flag",
            description="Percentage flag",
            type=FeatureFlagType.PERCENTAGE,
            enabled=True,
            default_value=0.0,
            percentage_rollout=50
        )
        
        result = evaluator.evaluate("percentage_flag", context, config)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
    
    def test_evaluate_string_flag(self, evaluator, context):
        """Testa avaliação de flag string."""
        config = FeatureFlagConfig(
            name="string_flag",
            description="String flag",
            type=FeatureFlagType.STRING,
            enabled=True,
            default_value="default",
            custom_rules={
                "admin_value": "admin",
                "premium_value": "premium"
            }
        )
        
        # Testar com usuário admin
        context.user_role = "admin"
        result = evaluator.evaluate("string_flag", context, config)
        assert result == "admin"
        
        # Testar com usuário premium
        context.user_role = "premium"
        result = evaluator.evaluate("string_flag", context, config)
        assert result == "premium"
        
        # Testar com usuário normal
        context.user_role = "user"
        result = evaluator.evaluate("string_flag", context, config)
        assert result == "default"
    
    def test_evaluate_number_flag(self, evaluator, context):
        """Testa avaliação de flag numérica."""
        config = FeatureFlagConfig(
            name="number_flag",
            description="Number flag",
            type=FeatureFlagType.NUMBER,
            enabled=True,
            default_value=100,
            custom_rules={"multiplier": 2.0}
        )
        
        result = evaluator.evaluate("number_flag", context, config)
        assert result == 200  # 100 * 2.0
    
    def test_evaluate_json_flag(self, evaluator, context):
        """Testa avaliação de flag JSON."""
        config = FeatureFlagConfig(
            name="json_flag",
            description="JSON flag",
            type=FeatureFlagType.JSON,
            enabled=True,
            default_value={"base": "value"}
        )
        
        result = evaluator.evaluate("json_flag", context, config)
        assert isinstance(result, dict)
        assert result["base"] == "value"
        assert result["user_role"] == "user123"
        assert result["environment"] == "development"
    
    def test_cache_functionality(self, evaluator, boolean_config, context):
        """Testa funcionalidade de cache."""
        # Primeira avaliação
        result1 = evaluator.evaluate("test_boolean", context, boolean_config)
        
        # Segunda avaliação (deve usar cache)
        result2 = evaluator.evaluate("test_boolean", context, boolean_config)
        
        assert result1 == result2
        
        # Verificar se cache foi usado
        cache_key = evaluator._generate_cache_key("test_boolean", context)
        assert cache_key in evaluator.cache
    
    def test_cache_expiration(self, evaluator, boolean_config, context):
        """Testa expiração do cache."""
        # Primeira avaliação
        evaluator.evaluate("test_boolean", context, boolean_config)
        
        # Simular passagem do tempo
        cache_key = evaluator._generate_cache_key("test_boolean", context)
        evaluator.cache_timestamps[cache_key] = time.time() - 400  # 400 segundos atrás
        
        # Verificar se cache expirou
        assert not evaluator._is_cache_valid(cache_key, 300)  # TTL de 300 segundos
    
    def test_custom_rules_evaluation(self, evaluator, context):
        """Testa avaliação de regras customizadas."""
        config = FeatureFlagConfig(
            name="custom_flag",
            description="Custom flag",
            type=FeatureFlagType.BOOLEAN,
            enabled=True,
            custom_rules={
                "time_based": {
                    "start_time": "2024-01-01T00:00:00",
                    "end_time": "2024-12-31T23:59:59"
                },
                "user_attributes": {
                    "roles": ["admin", "premium"]
                }
            }
        )
        
        # Testar com usuário admin
        context.user_role = "admin"
        result = evaluator.evaluate("custom_flag", context, config)
        assert result == True
        
        # Testar com usuário normal
        context.user_role = "user"
        result = evaluator.evaluate("custom_flag", context, config)
        assert result == False


class TestFeatureFlagManager:
    """Testes para gerenciador de feature flags."""
    
    @pytest.fixture
    def manager(self):
        """Fixture para gerenciador."""
        return FeatureFlagManager()
    
    @pytest.fixture
    def context(self):
        """Fixture para contexto."""
        return FeatureFlagContext(
            user_id="user123",
            ip_address="192.168.1.1",
            environment="development"
        )
    
    def test_manager_initialization(self, manager):
        """Testa inicialização do gerenciador."""
        assert len(manager.flags) > 0  # Deve ter flags padrão
        assert "advanced_analytics" in manager.flags
        assert "beta_features" in manager.flags
    
    def test_add_flag(self, manager):
        """Testa adição de flag."""
        config = FeatureFlagConfig(
            name="test_flag",
            description="Test flag",
            enabled=True
        )
        
        manager.add_flag(config)
        assert "test_flag" in manager.flags
        assert manager.flags["test_flag"] == config
    
    def test_remove_flag(self, manager):
        """Testa remoção de flag."""
        flag_name = "advanced_analytics"
        assert flag_name in manager.flags
        
        manager.remove_flag(flag_name)
        assert flag_name not in manager.flags
    
    def test_get_flag(self, manager):
        """Testa obtenção de flag."""
        flag = manager.get_flag("advanced_analytics")
        assert flag is not None
        assert flag.name == "advanced_analytics"
        
        # Flag inexistente
        flag = manager.get_flag("inexistent_flag")
        assert flag is None
    
    def test_is_enabled(self, manager, context):
        """Testa verificação se flag está habilitada."""
        # Flag habilitada para usuário admin
        context.user_role = "admin"
        assert manager.is_enabled("advanced_analytics", context) == True
        
        # Flag desabilitada para usuário normal
        context.user_role = "user"
        assert manager.is_enabled("advanced_analytics", context) == False
    
    def test_get_value(self, manager, context):
        """Testa obtenção de valor de flag."""
        # Flag booleana
        context.user_role = "admin"
        value = manager.get_value("advanced_analytics", context)
        assert value == True
        
        # Flag com valor padrão
        value = manager.get_value("inexistent_flag", context, default="default")
        assert value == "default"
    
    def test_get_metrics(self, manager, context):
        """Testa obtenção de métricas."""
        # Fazer algumas avaliações
        manager.is_enabled("advanced_analytics", context)
        manager.get_value("beta_features", context)
        
        metrics = manager.get_metrics()
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
    
    def test_clear_cache(self, manager):
        """Testa limpeza de cache."""
        # Fazer algumas avaliações para popular cache
        context = FeatureFlagContext(user_id="user123")
        manager.is_enabled("advanced_analytics", context)
        
        # Verificar se cache foi populado
        assert len(manager.evaluator.cache) > 0
        
        # Limpar cache
        manager.clear_cache()
        assert len(manager.evaluator.cache) == 0


class TestFeatureFlagDecorators:
    """Testes para decoradores de feature flags."""
    
    @pytest.fixture
    def app(self):
        """Fixture para aplicação Flask."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    def test_feature_flag_decorator_enabled(self, app):
        """Testa decorador com flag habilitada."""
        @app.route('/test')
        @feature_flag("advanced_analytics")
        def test_route():
            return {"status": "ok"}
        
        with app.test_request_context('/test'):
            # Simular usuário admin
            g.user_role = "admin"
            
            response = test_route()
            assert response[0]["status"] == "ok"
    
    def test_feature_flag_decorator_disabled(self, app):
        """Testa decorador com flag desabilitada."""
        @app.route('/test')
        @feature_flag("advanced_analytics")
        def test_route():
            return {"status": "ok"}
        
        with app.test_request_context('/test'):
            # Simular usuário normal
            g.user_role = "user"
            
            response = test_route()
            assert response[0]["error"] == "Feature não disponível"
            assert response[1] == 403
    
    def test_feature_flag_value_decorator(self, app):
        """Testa decorador de valor de flag."""
        @app.route('/test')
        @feature_flag_value("api_rate_limit", default=100)
        def test_route():
            return {"rate_limit": g.feature_flags.get("api_rate_limit", 100)}
        
        with app.test_request_context('/test'):
            response = test_route()
            assert "rate_limit" in response[0]
            assert isinstance(response[0]["rate_limit"], (int, float))


class TestFeatureFlagUtilities:
    """Testes para funções utilitárias."""
    
    def test_is_feature_enabled(self):
        """Testa função is_feature_enabled."""
        context = FeatureFlagContext(user_role="admin")
        result = is_feature_enabled("advanced_analytics", context)
        assert isinstance(result, bool)
    
    def test_get_feature_value(self):
        """Testa função get_feature_value."""
        context = FeatureFlagContext(user_role="admin")
        value = get_feature_value("api_rate_limit", context, default=100)
        assert isinstance(value, (int, float))
    
    def test_create_context_from_request(self):
        """Testa criação de contexto a partir de requisição."""
        app = Flask(__name__)
        
        with app.test_request_context('/test', headers={'User-Agent': 'Test'}):
            context = create_context_from_request(request, user_id="user123")
            
            assert context.user_id == "user123"
            assert context.ip_address == "127.0.0.1"
            assert context.user_agent == "Test"
            assert context.environment == "development"


class TestFeatureFlagEnvironmentConfiguration:
    """Testes para configuração por ambiente."""
    
    def test_configure_feature_flags_for_environment_production(self):
        """Testa configuração para ambiente de produção."""
        from backend.app.config.feature_flags import configure_feature_flags_for_environment
        
        manager = FeatureFlagManager()
        
        # Configurar para produção
        configure_feature_flags_for_environment("production")
        
        # Verificar configurações
        beta_flag = manager.get_flag("beta_features")
        new_ui_flag = manager.get_flag("new_ui")
        
        assert beta_flag.enabled == False
        assert new_ui_flag.percentage_rollout == 10
    
    def test_configure_feature_flags_for_environment_staging(self):
        """Testa configuração para ambiente de staging."""
        from backend.app.config.feature_flags import configure_feature_flags_for_environment
        
        manager = FeatureFlagManager()
        
        # Configurar para staging
        configure_feature_flags_for_environment("staging")
        
        # Verificar configurações
        beta_flag = manager.get_flag("beta_features")
        new_ui_flag = manager.get_flag("new_ui")
        
        assert beta_flag.enabled == True
        assert new_ui_flag.percentage_rollout == 50
    
    def test_configure_feature_flags_for_environment_development(self):
        """Testa configuração para ambiente de desenvolvimento."""
        from backend.app.config.feature_flags import configure_feature_flags_for_environment
        
        manager = FeatureFlagManager()
        
        # Configurar para desenvolvimento
        configure_feature_flags_for_environment("development")
        
        # Verificar configurações
        beta_flag = manager.get_flag("beta_features")
        new_ui_flag = manager.get_flag("new_ui")
        
        assert beta_flag.enabled == True
        assert new_ui_flag.percentage_rollout == 100


if __name__ == '__main__':
    pytest.main([__file__]) 