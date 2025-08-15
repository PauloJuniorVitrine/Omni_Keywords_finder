from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Feature Flags Avançados - IMP-014
Tracing ID: IMP014_FEATURE_FLAGS_001_20241227
Data: 2024-12-27
Status: Testes Unitários

Testes para validar:
- Criação e gerenciamento de feature flags
- Estratégias de rollout
- Cache inteligente
- Auditoria
- Decorators
- Configuração por arquivo
"""

import json
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Adicionar path para importar o módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.feature_flags.advanced_feature_flags import (
    AdvancedFeatureFlags,
    FeatureFlag,
    FeatureContext,
    FeatureType,
    RolloutStrategy,
    FeatureFlagCache,
    FeatureFlagAuditor,
    feature_flag,
    is_feature_enabled,
    get_feature_flags
)

class TestFeatureFlag(unittest.TestCase):
    """Testes para a classe FeatureFlag"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.feature = FeatureFlag(
            name="test_feature",
            description="Feature de teste",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
    
    def test_feature_flag_initialization(self):
        """Testa inicialização de feature flag"""
        self.assertEqual(self.feature.name, "test_feature")
        self.assertEqual(self.feature.description, "Feature de teste")
        self.assertEqual(self.feature.feature_type, FeatureType.BOOLEAN)
        self.assertTrue(self.feature.enabled)
        self.assertIsNotNone(self.feature.created_at)
        self.assertIsNotNone(self.feature.updated_at)
    
    def test_feature_flag_with_metadata(self):
        """Testa feature flag com metadados"""
        metadata = {"category": "test", "priority": "high"}
        feature = FeatureFlag(
            name="test_metadata",
            description="Feature com metadados",
            feature_type=FeatureType.PERCENTAGE,
            metadata=metadata
        )
        
        self.assertEqual(feature.metadata["category"], "test")
        self.assertEqual(feature.metadata["priority"], "high")
    
    def test_feature_flag_with_dates(self):
        """Testa feature flag com datas"""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        
        feature = FeatureFlag(
            name="test_dates",
            description="Feature com datas",
            feature_type=FeatureType.TIME_BASED,
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertEqual(feature.start_date, start_date)
        self.assertEqual(feature.end_date, end_date)

class TestFeatureContext(unittest.TestCase):
    """Testes para a classe FeatureContext"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.context = FeatureContext(
            user_id="user123",
            environment="production"
        )
    
    def test_feature_context_initialization(self):
        """Testa inicialização de contexto"""
        self.assertEqual(self.context.user_id, "user123")
        self.assertEqual(self.context.environment, "production")
        self.assertIsInstance(self.context.user_attributes, dict)
        self.assertIsInstance(self.context.request_attributes, dict)
    
    def test_feature_context_with_attributes(self):
        """Testa contexto com atributos"""
        user_attrs = {"role": "admin", "plan": "premium"}
        request_attrs = {"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"}
        
        context = FeatureContext(
            user_id="user456",
            user_attributes=user_attrs,
            request_attributes=request_attrs
        )
        
        self.assertEqual(context.user_attributes["role"], "admin")
        self.assertEqual(context.request_attributes["ip"], "192.168.1.1")

class TestFeatureFlagCache(unittest.TestCase):
    """Testes para o FeatureFlagCache"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.cache = FeatureFlagCache(ttl_seconds=1, max_size=2)
        self.feature = FeatureFlag(
            name="cache_test",
            description="Feature para teste de cache",
            feature_type=FeatureType.BOOLEAN
        )
    
    def test_cache_set_and_get(self):
        """Testa set e get do cache"""
        self.cache.set("test_key", self.feature)
        cached_feature = self.cache.get("test_key")
        
        self.assertIsNotNone(cached_feature)
        self.assertEqual(cached_feature.name, "cache_test")
    
    def test_cache_expiration(self):
        """Testa expiração do cache"""
        self.cache.set("expire_test", self.feature)
        
        # Aguardar expiração
        time.sleep(1.1)
        
        cached_feature = self.cache.get("expire_test")
        self.assertIsNone(cached_feature)
    
    def test_cache_max_size(self):
        """Testa limite máximo do cache"""
        feature1 = FeatureFlag(name="feature1", description="Test 1", feature_type=FeatureType.BOOLEAN)
        feature2 = FeatureFlag(name="feature2", description="Test 2", feature_type=FeatureType.BOOLEAN)
        feature3 = FeatureFlag(name="feature3", description="Test 3", feature_type=FeatureType.BOOLEAN)
        
        self.cache.set("key1", feature1)
        self.cache.set("key2", feature2)
        self.cache.set("key3", feature3)  # Deve remover key1
        
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNotNone(self.cache.get("key2"))
        self.assertIsNotNone(self.cache.get("key3"))
    
    def test_cache_clear(self):
        """Testa limpeza do cache"""
        self.cache.set("test_key", self.feature)
        self.cache.clear()
        
        cached_feature = self.cache.get("test_key")
        self.assertIsNone(cached_feature)
    
    def test_cache_stats(self):
        """Testa estatísticas do cache"""
        self.cache.set("test_key", self.feature)
        stats = self.cache.get_stats()
        
        self.assertEqual(stats["size"], 1)
        self.assertEqual(stats["max_size"], 2)
        self.assertIn("test_key", stats["keys"])

class TestFeatureFlagAuditor(unittest.TestCase):
    """Testes para o FeatureFlagAuditor"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.logger = MagicMock()
        self.auditor = FeatureFlagAuditor(self.logger)
        self.context = FeatureContext(user_id="user123")
    
    def test_log_evaluation(self):
        """Testa registro de avaliação"""
        evaluation = FeatureEvaluation(
            feature_name="test_feature",
            enabled=True,
            context=self.context,
            evaluation_time=datetime.utcnow()
        )
        
        self.auditor.log_evaluation(evaluation)
        
        self.assertEqual(len(self.auditor.evaluations), 1)
        self.assertEqual(self.auditor.evaluations[0].feature_name, "test_feature")
    
    def test_get_evaluations_filtered(self):
        """Testa obtenção de avaliações filtradas"""
        # Criar múltiplas avaliações
        for index in range(5):
            evaluation = FeatureEvaluation(
                feature_name=f"feature_{index}",
                enabled=True,
                context=self.context,
                evaluation_time=datetime.utcnow()
            )
            self.auditor.log_evaluation(evaluation)
        
        # Filtrar por feature
        filtered = self.auditor.get_evaluations(feature_name="feature_0")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].feature_name, "feature_0")
        
        # Filtrar por usuário
        filtered = self.auditor.get_evaluations(user_id="user123")
        self.assertEqual(len(filtered), 5)
    
    def test_get_stats(self):
        """Testa estatísticas de auditoria"""
        # Criar avaliações com diferentes resultados
        for index in range(3):
            evaluation = FeatureEvaluation(
                feature_name="test_feature",
                enabled=index < 2,  # 2 habilitadas, 1 desabilitada
                context=self.context,
                evaluation_time=datetime.utcnow()
            )
            self.auditor.log_evaluation(evaluation)
        
        stats = self.auditor.get_stats()
        
        self.assertEqual(stats["total_evaluations"], 3)
        self.assertEqual(stats["feature_stats"]["test_feature"]["enabled"], 2)
        self.assertEqual(stats["feature_stats"]["test_feature"]["disabled"], 1)

class TestAdvancedFeatureFlags(unittest.TestCase):
    """Testes para o AdvancedFeatureFlags"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.close()
        
        self.feature_flags = AdvancedFeatureFlags(
            config_file=self.temp_file.name,
            enable_audit=True
        )
    
    def tearDown(self):
        """Cleanup após cada teste"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_initialization(self):
        """Testa inicialização do sistema"""
        self.assertIsNotNone(self.feature_flags.features)
        self.assertIsNotNone(self.feature_flags.cache)
        self.assertIsNotNone(self.feature_flags.logger)
    
    def test_load_default_configuration(self):
        """Testa carregamento de configuração padrão"""
        features = self.feature_flags.list_features()
        
        # Verificar se features padrão foram carregadas
        feature_names = [f.name for f in features]
        self.assertIn("new_ui", feature_names)
        self.assertIn("advanced_analytics", feature_names)
        self.assertIn("beta_features", feature_names)
    
    def test_is_enabled_boolean_feature(self):
        """Testa feature boolean habilitada"""
        # Criar feature boolean habilitada
        feature = FeatureFlag(
            name="test_boolean",
            description="Test boolean",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
        self.feature_flags.add_feature(feature)
        
        context = FeatureContext(user_id="user123")
        result = self.feature_flags.is_enabled("test_boolean", context)
        
        self.assertTrue(result)
    
    def test_is_enabled_boolean_feature_disabled(self):
        """Testa feature boolean desabilitada"""
        feature = FeatureFlag(
            name="test_boolean_disabled",
            description="Test boolean disabled",
            feature_type=FeatureType.BOOLEAN,
            enabled=False
        )
        self.feature_flags.add_feature(feature)
        
        context = FeatureContext(user_id="user123")
        result = self.feature_flags.is_enabled("test_boolean_disabled", context)
        
        self.assertFalse(result)
    
    def test_is_enabled_percentage_feature(self):
        """Testa feature com rollout por porcentagem"""
        feature = FeatureFlag(
            name="test_percentage",
            description="Test percentage",
            feature_type=FeatureType.PERCENTAGE,
            enabled=True,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50.0
        )
        self.feature_flags.add_feature(feature)
        
        context = FeatureContext(user_id="user123")
        result = self.feature_flags.is_enabled("test_percentage", context)
        
        # Resultado deve ser determinístico para o mesmo user_id
        self.assertIsInstance(result, bool)
    
    def test_is_enabled_targeted_users(self):
        """Testa feature com usuários específicos"""
        feature = FeatureFlag(
            name="test_targeted",
            description="Test targeted",
            feature_type=FeatureType.TARGETED,
            enabled=True,
            rollout_strategy=RolloutStrategy.TARGETED_USERS,
            target_users=["user123", "admin"]
        )
        self.feature_flags.add_feature(feature)
        
        # Usuário na lista
        context1 = FeatureContext(user_id="user123")
        result1 = self.feature_flags.is_enabled("test_targeted", context1)
        self.assertTrue(result1)
        
        # Usuário fora da lista
        context2 = FeatureContext(user_id="user456")
        result2 = self.feature_flags.is_enabled("test_targeted", context2)
        self.assertFalse(result2)
    
    def test_is_enabled_targeted_environments(self):
        """Testa feature com ambientes específicos"""
        feature = FeatureFlag(
            name="test_env",
            description="Test environment",
            feature_type=FeatureType.TARGETED,
            enabled=True,
            rollout_strategy=RolloutStrategy.TARGETED_ENVIRONMENTS,
            target_environments=["production", "staging"]
        )
        self.feature_flags.add_feature(feature)
        
        # Ambiente na lista
        context1 = FeatureContext(environment="production")
        result1 = self.feature_flags.is_enabled("test_env", context1)
        self.assertTrue(result1)
        
        # Ambiente fora da lista
        context2 = FeatureContext(environment="development")
        result2 = self.feature_flags.is_enabled("test_env", context2)
        self.assertFalse(result2)
    
    def test_is_enabled_time_based_feature(self):
        """Testa feature com datas"""
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow() + timedelta(days=1)
        
        feature = FeatureFlag(
            name="test_time",
            description="Test time based",
            feature_type=FeatureType.TIME_BASED,
            enabled=True,
            start_date=start_date,
            end_date=end_date
        )
        self.feature_flags.add_feature(feature)
        
        context = FeatureContext(user_id="user123")
        result = self.feature_flags.is_enabled("test_time", context)
        
        self.assertTrue(result)
    
    def test_is_enabled_feature_not_found(self):
        """Testa feature não encontrada"""
        context = FeatureContext(user_id="user123")
        result = self.feature_flags.is_enabled("non_existent", context)
        
        self.assertFalse(result)
    
    def test_add_feature(self):
        """Testa adição de feature"""
        feature = FeatureFlag(
            name="new_feature",
            description="New feature",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
        
        self.feature_flags.add_feature(feature)
        
        added_feature = self.feature_flags.get_feature("new_feature")
        self.assertIsNotNone(added_feature)
        self.assertEqual(added_feature.name, "new_feature")
    
    def test_update_feature(self):
        """Testa atualização de feature"""
        feature = FeatureFlag(
            name="update_test",
            description="Update test",
            feature_type=FeatureType.BOOLEAN,
            enabled=False
        )
        self.feature_flags.add_feature(feature)
        
        # Atualizar
        updates = {"enabled": True, "description": "Updated description"}
        self.feature_flags.update_feature("update_test", updates)
        
        updated_feature = self.feature_flags.get_feature("update_test")
        self.assertTrue(updated_feature.enabled)
        self.assertEqual(updated_feature.description, "Updated description")
    
    def test_delete_feature(self):
        """Testa remoção de feature"""
        feature = FeatureFlag(
            name="delete_test",
            description="Delete test",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
        self.feature_flags.add_feature(feature)
        
        # Verificar se existe
        self.assertIsNotNone(self.feature_flags.get_feature("delete_test"))
        
        # Remover
        self.feature_flags.delete_feature("delete_test")
        
        # Verificar se foi removida
        self.assertIsNone(self.feature_flags.get_feature("delete_test"))
    
    def test_get_stats(self):
        """Testa estatísticas do sistema"""
        # Adicionar algumas features
        for index in range(3):
            feature = FeatureFlag(
                name=f"stats_test_{index}",
                description=f"Stats test {index}",
                feature_type=FeatureType.BOOLEAN,
                enabled=index < 2
            )
            self.feature_flags.add_feature(feature)
        
        stats = self.feature_flags.get_stats()
        
        self.assertEqual(stats["total_features"], 6)  # 3 padrão + 3 adicionadas
        self.assertEqual(stats["enabled_features"], 5)  # 2 padrão + 2 adicionadas
        self.assertIn("cache_stats", stats)
        self.assertIn("audit_stats", stats)

class TestFeatureFlagDecorator(unittest.TestCase):
    """Testes para o decorator feature_flag"""
    
    def test_feature_flag_decorator_enabled(self):
        """Testa decorator com feature habilitada"""
        @feature_flag("test_decorator", fallback=False)
        def test_function():
            return "enabled"
        
        # Mock do sistema de feature flags
        with patch('infrastructure.feature_flags.advanced_feature_flags.AdvancedFeatureFlags') as mock_class:
            mock_instance = MagicMock()
            mock_instance.is_enabled.return_value = True
            mock_class.return_value = mock_instance
            
            result = test_function()
            self.assertEqual(result, "enabled")
    
    def test_feature_flag_decorator_disabled(self):
        """Testa decorator com feature desabilitada"""
        @feature_flag("test_decorator", fallback="disabled")
        def test_function():
            return "enabled"
        
        # Mock do sistema de feature flags
        with patch('infrastructure.feature_flags.advanced_feature_flags.AdvancedFeatureFlags') as mock_class:
            mock_instance = MagicMock()
            mock_instance.is_enabled.return_value = False
            mock_class.return_value = mock_instance
            
            result = test_function()
            self.assertEqual(result, "disabled")

class TestFeatureFlagsIntegration(unittest.TestCase):
    """Testes de integração do sistema de feature flags"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.close()
        
        self.feature_flags = AdvancedFeatureFlags(
            config_file=self.temp_file.name,
            enable_audit=True
        )
    
    def tearDown(self):
        """Cleanup após cada teste"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_complete_workflow(self):
        """Testa workflow completo"""
        # 1. Adicionar feature
        feature = FeatureFlag(
            name="workflow_test",
            description="Workflow test",
            feature_type=FeatureType.PERCENTAGE,
            enabled=True,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=25.0
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Verificar se foi adicionada
        added_feature = self.feature_flags.get_feature("workflow_test")
        self.assertIsNotNone(added_feature)
        
        # 3. Testar avaliação
        context = FeatureContext(user_id="workflow_user")
        result = self.feature_flags.is_enabled("workflow_test", context)
        self.assertIsInstance(result, bool)
        
        # 4. Verificar auditoria
        if self.feature_flags.auditor:
            evaluations = self.feature_flags.auditor.get_evaluations(feature_name="workflow_test")
            self.assertEqual(len(evaluations), 1)
            self.assertEqual(evaluations[0].feature_name, "workflow_test")
        
        # 5. Verificar cache
        cache_stats = self.feature_flags.cache.get_stats()
        self.assertGreaterEqual(cache_stats["size"], 0)
        
        # 6. Atualizar feature
        self.feature_flags.update_feature("workflow_test", {"rollout_percentage": 50.0})
        updated_feature = self.feature_flags.get_feature("workflow_test")
        self.assertEqual(updated_feature.rollout_percentage, 50.0)
        
        # 7. Verificar estatísticas
        stats = self.feature_flags.get_stats()
        self.assertGreaterEqual(stats["total_features"], 1)
    
    def test_multiple_evaluations(self):
        """Testa múltiplas avaliações"""
        feature = FeatureFlag(
            name="multi_test",
            description="Multiple evaluations test",
            feature_type=FeatureType.PERCENTAGE,
            enabled=True,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50.0
        )
        self.feature_flags.add_feature(feature)
        
        # Múltiplas avaliações
        results = []
        for index in range(10):
            context = FeatureContext(user_id=f"user_{index}")
            result = self.feature_flags.is_enabled("multi_test", context)
            results.append(result)
        
        # Verificar que alguns estão habilitados e outros não
        self.assertIn(True, results)
        self.assertIn(False, results)
        
        # Verificar auditoria
        if self.feature_flags.auditor:
            evaluations = self.feature_flags.auditor.get_evaluations(feature_name="multi_test")
            self.assertEqual(len(evaluations), 10)

if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2) 