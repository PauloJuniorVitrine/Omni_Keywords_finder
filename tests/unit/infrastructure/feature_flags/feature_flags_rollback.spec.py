from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Testes de Rollback para Feature Flags - IMP-014
Tracing ID: IMP014_ROLLBACK_TESTS_001_20241227
Data: 2024-12-27
Status: Implementação Inicial

Testes específicos para cenários de rollback:
- Rollback de features boolean
- Rollback de features percentuais
- Rollback de features direcionadas
- Rollback de integrações
- Validação de consistência
"""

import unittest
import tempfile
import os
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Adicionar path do projeto
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infrastructure.feature_flags.advanced_feature_flags import (
    AdvancedFeatureFlags,
    FeatureFlag,
    FeatureContext,
    FeatureType,
    RolloutStrategy
)
from infrastructure.feature_flags.integration_flags import (
    IntegrationFeatureFlags,
    Environment,
    IntegrationType,
    RolloutStrategy as IntegrationRolloutStrategy
)

class TestFeatureFlagsRollback(unittest.TestCase):
    """Testes de rollback para feature flags"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.close()
        
        self.feature_flags = AdvancedFeatureFlags(
            config_file=self.temp_file.name,
            enable_audit=True
        )
        
        self.integration_flags = IntegrationFeatureFlags(
            redis_url=None,
            environment=Environment.TESTING
        )
    
    def tearDown(self):
        """Cleanup após cada teste"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_boolean_feature_rollback(self):
        """Testa rollback de feature boolean"""
        # 1. Criar feature habilitada
        feature = FeatureFlag(
            name="test_boolean_rollback",
            description="Teste de rollback boolean",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Verificar que está habilitada
        context = FeatureContext(user_id="test_user")
        result_before = self.feature_flags.is_enabled("test_boolean_rollback", context)
        self.assertTrue(result_before, "Feature deve estar habilitada inicialmente")
        
        # 3. Executar rollback (desabilitar)
        self.feature_flags.update_feature("test_boolean_rollback", {"enabled": False})
        
        # 4. Verificar que foi desabilitada
        result_after = self.feature_flags.is_enabled("test_boolean_rollback", context)
        self.assertFalse(result_after, "Feature deve estar desabilitada após rollback")
        
        # 5. Verificar que cache foi limpo
        cache_stats = self.feature_flags.cache.get_stats()
        self.assertEqual(cache_stats["size"], 0, "Cache deve estar vazio após rollback")
    
    def test_percentage_feature_rollback(self):
        """Testa rollback de feature percentual"""
        # 1. Criar feature com 50% de rollout
        feature = FeatureFlag(
            name="test_percentage_rollback",
            description="Teste de rollback percentual",
            feature_type=FeatureType.PERCENTAGE,
            enabled=True,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=50.0
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Testar distribuição com 50%
        results_50 = []
        for index in range(100):
            context = FeatureContext(user_id=f"user_{index}")
            results_50.append(self.feature_flags.is_enabled("test_percentage_rollback", context))
        
        enabled_50 = sum(results_50)
        self.assertGreater(enabled_50, 0, "Deve ter usuários habilitados com 50%")
        self.assertLess(enabled_50, 100, "Não deve ter todos os usuários habilitados com 50%")
        
        # 3. Executar rollback para 0%
        self.feature_flags.update_feature("test_percentage_rollback", {"rollout_percentage": 0.0})
        
        # 4. Testar distribuição com 0%
        results_0 = []
        for index in range(100):
            context = FeatureContext(user_id=f"user_{index}")
            results_0.append(self.feature_flags.is_enabled("test_percentage_rollback", context))
        
        enabled_0 = sum(results_0)
        self.assertEqual(enabled_0, 0, "Nenhum usuário deve estar habilitado com 0%")
        
        # 5. Verificar consistência de hash
        # Mesmo usuário deve ter resultado consistente
        context = FeatureContext(user_id="consistent_user")
        result1 = self.feature_flags.is_enabled("test_percentage_rollback", context)
        result2 = self.feature_flags.is_enabled("test_percentage_rollback", context)
        self.assertEqual(result1, result2, "Resultado deve ser consistente para mesmo usuário")
    
    def test_targeted_users_rollback(self):
        """Testa rollback de feature direcionada a usuários"""
        # 1. Criar feature para usuários específicos
        feature = FeatureFlag(
            name="test_targeted_rollback",
            description="Teste de rollback direcionado",
            feature_type=FeatureType.TARGETED,
            enabled=True,
            rollout_strategy=RolloutStrategy.TARGETED_USERS,
            target_users=["admin", "beta_tester", "power_user"]
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Testar usuários na lista
        context_admin = FeatureContext(user_id="admin")
        result_admin_before = self.feature_flags.is_enabled("test_targeted_rollback", context_admin)
        self.assertTrue(result_admin_before, "Admin deve estar habilitado")
        
        context_beta = FeatureContext(user_id="beta_tester")
        result_beta_before = self.feature_flags.is_enabled("test_targeted_rollback", context_beta)
        self.assertTrue(result_beta_before, "Beta tester deve estar habilitado")
        
        # 3. Testar usuário fora da lista
        context_regular = FeatureContext(user_id="regular_user")
        result_regular_before = self.feature_flags.is_enabled("test_targeted_rollback", context_regular)
        self.assertFalse(result_regular_before, "Usuário regular não deve estar habilitado")
        
        # 4. Executar rollback (remover da lista)
        self.feature_flags.update_feature("test_targeted_rollback", {"target_users": []})
        
        # 5. Verificar que todos foram desabilitados
        result_admin_after = self.feature_flags.is_enabled("test_targeted_rollback", context_admin)
        result_beta_after = self.feature_flags.is_enabled("test_targeted_rollback", context_beta)
        result_regular_after = self.feature_flags.is_enabled("test_targeted_rollback", context_regular)
        
        self.assertFalse(result_admin_after, "Admin deve estar desabilitado após rollback")
        self.assertFalse(result_beta_after, "Beta tester deve estar desabilitado após rollback")
        self.assertFalse(result_regular_after, "Usuário regular deve continuar desabilitado")
    
    def test_targeted_environments_rollback(self):
        """Testa rollback de feature direcionada a ambientes"""
        # 1. Criar feature para ambientes específicos
        feature = FeatureFlag(
            name="test_env_rollback",
            description="Teste de rollback por ambiente",
            feature_type=FeatureType.TARGETED,
            enabled=True,
            rollout_strategy=RolloutStrategy.TARGETED_ENVIRONMENTS,
            target_environments=["staging", "production"]
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Testar ambiente na lista
        context_staging = FeatureContext(environment="staging")
        result_staging_before = self.feature_flags.is_enabled("test_env_rollback", context_staging)
        self.assertTrue(result_staging_before, "Staging deve estar habilitado")
        
        # 3. Testar ambiente fora da lista
        context_dev = FeatureContext(environment="development")
        result_dev_before = self.feature_flags.is_enabled("test_env_rollback", context_dev)
        self.assertFalse(result_dev_before, "Development não deve estar habilitado")
        
        # 4. Executar rollback (remover da lista)
        self.feature_flags.update_feature("test_env_rollback", {"target_environments": []})
        
        # 5. Verificar que todos foram desabilitados
        result_staging_after = self.feature_flags.is_enabled("test_env_rollback", context_staging)
        result_dev_after = self.feature_flags.is_enabled("test_env_rollback", context_dev)
        
        self.assertFalse(result_staging_after, "Staging deve estar desabilitado após rollback")
        self.assertFalse(result_dev_after, "Development deve continuar desabilitado")
    
    def test_gradual_rollback(self):
        """Testa rollback de feature gradual"""
        # 1. Criar feature gradual
        start_date = datetime.utcnow() - timedelta(days=15)  # 15 dias atrás
        feature = FeatureFlag(
            name="test_gradual_rollback",
            description="Teste de rollback gradual",
            feature_type=FeatureType.GRADUAL,
            enabled=True,
            rollout_strategy=RolloutStrategy.GRADUAL,
            rollout_percentage=100.0,
            start_date=start_date
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Testar distribuição gradual
        results_gradual = []
        for index in range(100):
            context = FeatureContext(user_id=f"user_{index}")
            results_gradual.append(self.feature_flags.is_enabled("test_gradual_rollback", context))
        
        enabled_gradual = sum(results_gradual)
        self.assertGreater(enabled_gradual, 0, "Deve ter usuários habilitados com rollout gradual")
        
        # 3. Executar rollback (desabilitar)
        self.feature_flags.update_feature("test_gradual_rollback", {"enabled": False})
        
        # 4. Verificar que todos foram desabilitados
        results_after = []
        for index in range(100):
            context = FeatureContext(user_id=f"user_{index}")
            results_after.append(self.feature_flags.is_enabled("test_gradual_rollback", context))
        
        enabled_after = sum(results_after)
        self.assertEqual(enabled_after, 0, "Nenhum usuário deve estar habilitado após rollback")
    
    def test_integration_rollback(self):
        """Testa rollback de integrações"""
        # 1. Configurar integração habilitada
        self.integration_flags._default_configs["google_trends"].enabled = True
        self.integration_flags._default_configs["google_trends"].rollout_strategy = IntegrationRolloutStrategy.IMMEDIATE
        
        # 2. Verificar que está habilitada
        result_before = self.integration_flags.is_enabled(IntegrationType.GOOGLE_TRENDS, "test_user")
        self.assertTrue(result_before, "Integração deve estar habilitada inicialmente")
        
        # 3. Executar rollback (desabilitar)
        self.integration_flags.update_config(IntegrationType.GOOGLE_TRENDS, {"enabled": False})
        
        # 4. Verificar que foi desabilitada
        result_after = self.integration_flags.is_enabled(IntegrationType.GOOGLE_TRENDS, "test_user")
        self.assertFalse(result_after, "Integração deve estar desabilitada após rollback")
        
        # 5. Verificar fallback
        fallback = self.integration_flags.get_fallback_config(IntegrationType.GOOGLE_TRENDS)
        self.assertIsNotNone(fallback, "Fallback deve estar disponível")
        self.assertEqual(fallback["fallback_provider"], "mock_data", "Fallback deve ser mock_data")
    
    def test_percentage_integration_rollback(self):
        """Testa rollback de integração percentual"""
        # 1. Configurar integração com 50% de rollout
        self.integration_flags._default_configs["webhook"].enabled = True
        self.integration_flags._default_configs["webhook"].rollout_strategy = IntegrationRolloutStrategy.PERCENTAGE
        self.integration_flags._default_configs["webhook"].rollout_percentage = 50.0
        
        # 2. Testar distribuição com 50%
        results_50 = []
        for index in range(100):
            results_50.append(self.integration_flags.is_enabled(IntegrationType.WEBHOOK, f"user_{index}"))
        
        enabled_50 = sum(results_50)
        self.assertGreater(enabled_50, 0, "Deve ter usuários habilitados com 50%")
        self.assertLess(enabled_50, 100, "Não deve ter todos os usuários habilitados com 50%")
        
        # 3. Executar rollback para 0%
        self.integration_flags.update_config(IntegrationType.WEBHOOK, {"rollout_percentage": 0.0})
        
        # 4. Testar distribuição com 0%
        results_0 = []
        for index in range(100):
            results_0.append(self.integration_flags.is_enabled(IntegrationType.WEBHOOK, f"user_{index}"))
        
        enabled_0 = sum(results_0)
        self.assertEqual(enabled_0, 0, "Nenhum usuário deve estar habilitado com 0%")
    
    def test_canary_rollback(self):
        """Testa rollback de integração canary"""
        # 1. Configurar integração canary
        self.integration_flags._default_configs["payment_gateway"].enabled = True
        self.integration_flags._default_configs["payment_gateway"].rollout_strategy = IntegrationRolloutStrategy.CANARY
        
        # 2. Testar usuário canary
        context = {"canary_users": ["canary_user"]}
        result_canary = self.integration_flags.is_enabled(IntegrationType.PAYMENT_GATEWAY, "canary_user", context)
        self.assertTrue(result_canary, "Usuário canary deve estar habilitado")
        
        # 3. Testar usuário regular
        result_regular = self.integration_flags.is_enabled(IntegrationType.PAYMENT_GATEWAY, "regular_user", context)
        self.assertFalse(result_regular, "Usuário regular não deve estar habilitado")
        
        # 4. Executar rollback (desabilitar)
        self.integration_flags.update_config(IntegrationType.PAYMENT_GATEWAY, {"enabled": False})
        
        # 5. Verificar que todos foram desabilitados
        result_canary_after = self.integration_flags.is_enabled(IntegrationType.PAYMENT_GATEWAY, "canary_user", context)
        result_regular_after = self.integration_flags.is_enabled(IntegrationType.PAYMENT_GATEWAY, "regular_user", context)
        
        self.assertFalse(result_canary_after, "Usuário canary deve estar desabilitado após rollback")
        self.assertFalse(result_regular_after, "Usuário regular deve continuar desabilitado")
    
    def test_ab_test_rollback(self):
        """Testa rollback de A/B test"""
        # 1. Configurar A/B test
        self.integration_flags._default_configs["analytics"].enabled = True
        self.integration_flags._default_configs["analytics"].rollout_strategy = IntegrationRolloutStrategy.A_B_TEST
        
        # 2. Testar distribuição A/B
        results_a = []
        results_b = []
        for index in range(100):
            result = self.integration_flags.is_enabled(IntegrationType.ANALYTICS, f"user_{index}")
            if result:
                results_a.append(f"user_{index}")
            else:
                results_b.append(f"user_{index}")
        
        # Deve ter usuários em ambos os grupos
        self.assertGreater(len(results_a), 0, "Deve ter usuários no grupo A")
        self.assertGreater(len(results_b), 0, "Deve ter usuários no grupo B")
        
        # 3. Executar rollback (desabilitar)
        self.integration_flags.update_config(IntegrationType.ANALYTICS, {"enabled": False})
        
        # 4. Verificar que todos foram desabilitados
        results_after = []
        for index in range(100):
            results_after.append(self.integration_flags.is_enabled(IntegrationType.ANALYTICS, f"user_{index}"))
        
        enabled_after = sum(results_after)
        self.assertEqual(enabled_after, 0, "Nenhum usuário deve estar habilitado após rollback")
    
    def test_rollback_consistency(self):
        """Testa consistência de rollback"""
        # 1. Criar feature
        feature = FeatureFlag(
            name="consistency_test",
            description="Teste de consistência",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Verificar estado inicial
        context = FeatureContext(user_id="test_user")
        initial_state = self.feature_flags.is_enabled("consistency_test", context)
        self.assertTrue(initial_state, "Estado inicial deve ser True")
        
        # 3. Executar múltiplos rollbacks
        rollback_states = []
        for index in range(5):
            # Alternar entre habilitado/desabilitado
            new_state = (index % 2) == 0
            self.feature_flags.update_feature("consistency_test", {"enabled": new_state})
            
            # Verificar estado
            current_state = self.feature_flags.is_enabled("consistency_test", context)
            rollback_states.append(current_state)
            
            # Aguardar um pouco para garantir que cache foi atualizado
            time.sleep(0.1)
        
        # 4. Verificar que estados alternaram corretamente
        expected_states = [False, True, False, True, False]
        self.assertEqual(rollback_states, expected_states, "Estados devem alternar corretamente")
    
    def test_rollback_performance(self):
        """Testa performance de rollback"""
        # 1. Criar múltiplas features
        for index in range(50):
            feature = FeatureFlag(
                name=f"perf_test_{index}",
                description=f"Performance test {index}",
                feature_type=FeatureType.BOOLEAN,
                enabled=True
            )
            self.feature_flags.add_feature(feature)
        
        # 2. Medir tempo de rollback
        start_time = time.time()
        
        # Executar rollback em todas as features
        for index in range(50):
            self.feature_flags.update_feature(f"perf_test_{index}", {"enabled": False})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 3. Verificar performance
        self.assertLess(duration, 1.0, f"Rollback deve ser rápido: {duration:.3f}string_data")
        
        # 4. Verificar que todas foram desabilitadas
        context = FeatureContext(user_id="test_user")
        for index in range(50):
            result = self.feature_flags.is_enabled(f"perf_test_{index}", context)
            self.assertFalse(result, f"Feature {index} deve estar desabilitada")
    
    def test_rollback_audit_trail(self):
        """Testa rastreamento de auditoria durante rollback"""
        # 1. Criar feature com auditoria
        feature = FeatureFlag(
            name="audit_rollback_test",
            description="Teste de auditoria de rollback",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Verificar estado inicial
        context = FeatureContext(user_id="audit_user")
        self.feature_flags.is_enabled("audit_rollback_test", context)
        
        # 3. Executar rollback
        self.feature_flags.update_feature("audit_rollback_test", {"enabled": False})
        
        # 4. Verificar estado após rollback
        self.feature_flags.is_enabled("audit_rollback_test", context)
        
        # 5. Verificar auditoria
        if self.feature_flags.auditor:
            evaluations = self.feature_flags.auditor.get_evaluations(feature_name="audit_rollback_test")
            self.assertGreaterEqual(len(evaluations), 2, "Deve ter pelo menos 2 avaliações registradas")
            
            # Verificar que há avaliações com resultados diferentes
            results = [eval.enabled for eval in evaluations]
            self.assertIn(True, results, "Deve ter avaliação com resultado True")
            self.assertIn(False, results, "Deve ter avaliação com resultado False")
    
    def test_rollback_cache_invalidation(self):
        """Testa invalidação de cache durante rollback"""
        # 1. Criar feature
        feature = FeatureFlag(
            name="cache_rollback_test",
            description="Teste de cache de rollback",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
        self.feature_flags.add_feature(feature)
        
        # 2. Fazer avaliação para popular cache
        context = FeatureContext(user_id="cache_user")
        self.feature_flags.is_enabled("cache_rollback_test", context)
        
        # 3. Verificar que cache foi populado
        cache_stats_before = self.feature_flags.cache.get_stats()
        self.assertGreater(cache_stats_before["size"], 0, "Cache deve estar populado")
        
        # 4. Executar rollback
        self.feature_flags.update_feature("cache_rollback_test", {"enabled": False})
        
        # 5. Verificar que cache foi limpo
        cache_stats_after = self.feature_flags.cache.get_stats()
        self.assertEqual(cache_stats_after["size"], 0, "Cache deve estar vazio após rollback")
        
        # 6. Verificar nova avaliação
        result = self.feature_flags.is_enabled("cache_rollback_test", context)
        self.assertFalse(result, "Resultado deve ser False após rollback")

class TestRollbackScenarios(unittest.TestCase):
    """Testes de cenários de rollback"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.feature_flags = AdvancedFeatureFlags(enable_audit=True)
    
    def test_emergency_rollback_scenario(self):
        """Testa cenário de rollback de emergência"""
        # 1. Simular feature crítica habilitada
        critical_feature = FeatureFlag(
            name="critical_payment_feature",
            description="Feature crítica de pagamento",
            feature_type=FeatureType.BOOLEAN,
            enabled=True
        )
        self.feature_flags.add_feature(critical_feature)
        
        # 2. Simular uso em produção
        users = [f"user_{index}" for index in range(1000)]
        enabled_users = []
        
        for user_id in users:
            context = FeatureContext(user_id=user_id)
            if self.feature_flags.is_enabled("critical_payment_feature", context):
                enabled_users.append(user_id)
        
        self.assertEqual(len(enabled_users), 1000, "Todos os usuários devem estar habilitados")
        
        # 3. Simular problema detectado - rollback de emergência
        self.feature_flags.update_feature("critical_payment_feature", {"enabled": False})
        
        # 4. Verificar que todos foram desabilitados
        disabled_users = []
        for user_id in users:
            context = FeatureContext(user_id=user_id)
            if not self.feature_flags.is_enabled("critical_payment_feature", context):
                disabled_users.append(user_id)
        
        self.assertEqual(len(disabled_users), 1000, "Todos os usuários devem estar desabilitados")
        
        # 5. Verificar tempo de resposta do rollback
        start_time = time.time()
        for user_id in users[:100]:  # Testar com 100 usuários
            context = FeatureContext(user_id=user_id)
            self.feature_flags.is_enabled("critical_payment_feature", context)
        end_time = time.time()
        
        duration = end_time - start_time
        self.assertLess(duration, 0.1, f"Rollback deve ser instantâneo: {duration:.3f}string_data")
    
    def test_gradual_rollback_scenario(self):
        """Testa cenário de rollback gradual"""
        # 1. Simular feature com rollout gradual
        gradual_feature = FeatureFlag(
            name="gradual_rollback_test",
            description="Teste de rollback gradual",
            feature_type=FeatureType.PERCENTAGE,
            enabled=True,
            rollout_strategy=RolloutStrategy.PERCENTAGE,
            rollout_percentage=75.0
        )
        self.feature_flags.add_feature(gradual_feature)
        
        # 2. Simular distribuição inicial
        users = [f"user_{index}" for index in range(1000)]
        enabled_before = []
        
        for user_id in users:
            context = FeatureContext(user_id=user_id)
            if self.feature_flags.is_enabled("gradual_rollback_test", context):
                enabled_before.append(user_id)
        
        # 3. Executar rollback gradual (reduzir para 25%)
        self.feature_flags.update_feature("gradual_rollback_test", {"rollout_percentage": 25.0})
        
        # 4. Verificar nova distribuição
        enabled_after = []
        for user_id in users:
            context = FeatureContext(user_id=user_id)
            if self.feature_flags.is_enabled("gradual_rollback_test", context):
                enabled_after.append(user_id)
        
        # 5. Verificar que número de usuários habilitados diminuiu
        self.assertLess(len(enabled_after), len(enabled_before), "Número de usuários deve diminuir")
        
        # 6. Verificar consistência (mesmo usuário deve manter resultado)
        for user_id in enabled_before:
            if user_id in enabled_after:
                # Usuário que estava habilitado deve continuar habilitado
                context = FeatureContext(user_id=user_id)
                result = self.feature_flags.is_enabled("gradual_rollback_test", context)
                self.assertTrue(result, f"Usuário {user_id} deve manter estado habilitado")
    
    def test_targeted_rollback_scenario(self):
        """Testa cenário de rollback direcionado"""
        # 1. Simular feature para usuários premium
        premium_feature = FeatureFlag(
            name="premium_rollback_test",
            description="Teste de rollback premium",
            feature_type=FeatureType.TARGETED,
            enabled=True,
            rollout_strategy=RolloutStrategy.TARGETED_USERS,
            target_users=["premium_1", "premium_2", "premium_3", "vip_user"]
        )
        self.feature_flags.add_feature(premium_feature)
        
        # 2. Testar usuários premium
        premium_users = ["premium_1", "premium_2", "premium_3", "vip_user"]
        regular_users = ["user_1", "user_2", "user_3", "user_4"]
        
        # Verificar estado inicial
        for user_id in premium_users:
            context = FeatureContext(user_id=user_id)
            result = self.feature_flags.is_enabled("premium_rollback_test", context)
            self.assertTrue(result, f"Usuário premium {user_id} deve estar habilitado")
        
        for user_id in regular_users:
            context = FeatureContext(user_id=user_id)
            result = self.feature_flags.is_enabled("premium_rollback_test", context)
            self.assertFalse(result, f"Usuário regular {user_id} não deve estar habilitado")
        
        # 3. Executar rollback seletivo (remover apenas alguns usuários)
        self.feature_flags.update_feature("premium_rollback_test", {
            "target_users": ["vip_user"]  # Manter apenas VIP
        })
        
        # 4. Verificar novo estado
        for user_id in ["premium_1", "premium_2", "premium_3"]:
            context = FeatureContext(user_id=user_id)
            result = self.feature_flags.is_enabled("premium_rollback_test", context)
            self.assertFalse(result, f"Usuário {user_id} deve estar desabilitado após rollback")
        
        # VIP deve continuar habilitado
        context = FeatureContext(user_id="vip_user")
        result = self.feature_flags.is_enabled("premium_rollback_test", context)
        self.assertTrue(result, "VIP deve continuar habilitado")
        
        # Usuários regulares devem continuar desabilitados
        for user_id in regular_users:
            context = FeatureContext(user_id=user_id)
            result = self.feature_flags.is_enabled("premium_rollback_test", context)
            self.assertFalse(result, f"Usuário regular {user_id} deve continuar desabilitado")

if __name__ == "__main__":
    # Executar testes
    unittest.main(verbosity=2) 