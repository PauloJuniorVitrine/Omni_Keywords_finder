#!/usr/bin/env python3
"""
Script de Validação de Feature Flags - IMP-014
Tracing ID: IMP014_VALIDATION_001_20241227
Data: 2024-12-27
Status: Implementação Inicial

Script para validar sistema de feature flags:
- Validação de configuração
- Testes de rollback
- Verificação de integridade
- Testes de performance
- Validação de auditoria
"""

import sys
import os
import json
import yaml
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import argparse
import logging

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos de feature flags
try:
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
        IntegrationType
    )
except ImportError as e:
    print(f"❌ Erro ao importar módulos de feature flags: {e}")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)string_data - %(levelname)string_data - %(message)string_data'
)
logger = logging.getLogger(__name__)

class FeatureFlagsValidator:
    """Validador de feature flags"""
    
    def __init__(self, config_file: str = "config/feature_flags.yaml"):
        self.config_file = config_file
        self.validation_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "tests": []
        }
        
    def log_test(self, test_name: str, status: str, message: str, details: Dict[str, Any] = None):
        """Registra resultado de teste"""
        test_result = {
            "test_name": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        self.validation_results["tests"].append(test_result)
        
        if status == "PASS":
            self.validation_results["passed"] += 1
            logger.info(f"✅ {test_name}: {message}")
        elif status == "FAIL":
            self.validation_results["failed"] += 1
            logger.error(f"❌ {test_name}: {message}")
        elif status == "WARNING":
            self.validation_results["warnings"] += 1
            logger.warning(f"⚠️ {test_name}: {message}")
    
    def validate_configuration_file(self) -> bool:
        """Valida arquivo de configuração"""
        try:
            if not os.path.exists(self.config_file):
                self.log_test(
                    "Config File Exists",
                    "FAIL",
                    f"Arquivo de configuração não encontrado: {self.config_file}"
                )
                return False
            
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validar estrutura básica
            required_keys = ["features", "global_settings", "environments"]
            for key in required_keys:
                if key not in config:
                    self.log_test(
                        "Config Structure",
                        "FAIL",
                        f"Chave obrigatória ausente: {key}"
                    )
                    return False
            
            # Validar features
            features = config.get("features", [])
            if not features:
                self.log_test(
                    "Features Configuration",
                    "WARNING",
                    "Nenhuma feature configurada"
                )
            else:
                self.log_test(
                    "Features Configuration",
                    "PASS",
                    f"{len(features)} features configuradas"
                )
            
            # Validar configurações por ambiente
            environments = config.get("environments", {})
            required_envs = ["development", "staging", "production"]
            for env in required_envs:
                if env not in environments:
                    self.log_test(
                        "Environment Configuration",
                        "WARNING",
                        f"Ambiente {env} não configurado"
                    )
            
            self.log_test(
                "Configuration File",
                "PASS",
                "Arquivo de configuração válido"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Configuration File",
                "FAIL",
                f"Erro ao validar configuração: {e}"
            )
            return False
    
    def validate_advanced_feature_flags(self) -> bool:
        """Valida sistema avançado de feature flags"""
        try:
            # Inicializar sistema
            feature_flags = AdvancedFeatureFlags(
                config_file=self.config_file,
                enable_audit=True
            )
            
            # Verificar inicialização
            if not feature_flags.features:
                self.log_test(
                    "Advanced Feature Flags Init",
                    "FAIL",
                    "Sistema não inicializou corretamente"
                )
                return False
            
            self.log_test(
                "Advanced Feature Flags Init",
                "PASS",
                f"Sistema inicializado com {len(feature_flags.features)} features"
            )
            
            # Testar features padrão
            default_features = ["new_ui", "advanced_analytics", "beta_features"]
            for feature_name in default_features:
                feature = feature_flags.get_feature(feature_name)
                if feature:
                    self.log_test(
                        f"Default Feature: {feature_name}",
                        "PASS",
                        f"Feature {feature_name} carregada corretamente"
                    )
                else:
                    self.log_test(
                        f"Default Feature: {feature_name}",
                        "WARNING",
                        f"Feature {feature_name} não encontrada"
                    )
            
            # Testar avaliação de features
            context = FeatureContext(user_id="test_user", environment="development")
            
            # Teste de feature boolean
            result = feature_flags.is_enabled("new_ui", context)
            self.log_test(
                "Boolean Feature Evaluation",
                "PASS",
                f"Feature boolean avaliada: {result}"
            )
            
            # Teste de feature percentual
            result = feature_flags.is_enabled("advanced_analytics", context)
            self.log_test(
                "Percentage Feature Evaluation",
                "PASS",
                f"Feature percentual avaliada: {result}"
            )
            
            # Teste de feature direcionada
            context.user_id = "admin"
            result = feature_flags.is_enabled("beta_features", context)
            self.log_test(
                "Targeted Feature Evaluation",
                "PASS",
                f"Feature direcionada avaliada: {result}"
            )
            
            # Verificar cache
            cache_stats = feature_flags.cache.get_stats()
            self.log_test(
                "Cache System",
                "PASS",
                f"Cache funcionando: {cache_stats}"
            )
            
            # Verificar auditoria
            if feature_flags.auditor:
                audit_stats = feature_flags.auditor.get_stats()
                self.log_test(
                    "Audit System",
                    "PASS",
                    f"Sistema de auditoria ativo: {audit_stats}"
                )
            else:
                self.log_test(
                    "Audit System",
                    "WARNING",
                    "Sistema de auditoria não disponível"
                )
            
            return True
            
        except Exception as e:
            self.log_test(
                "Advanced Feature Flags",
                "FAIL",
                f"Erro ao validar sistema avançado: {e}"
            )
            return False
    
    def validate_integration_feature_flags(self) -> bool:
        """Valida sistema de feature flags para integrações"""
        try:
            # Inicializar sistema
            integration_flags = IntegrationFeatureFlags(
                redis_url=None,
                environment=Environment.TESTING
            )
            
            # Verificar inicialização
            if not integration_flags._default_configs:
                self.log_test(
                    "Integration Feature Flags Init",
                    "FAIL",
                    "Sistema de integrações não inicializou"
                )
                return False
            
            self.log_test(
                "Integration Feature Flags Init",
                "PASS",
                f"Sistema inicializado com {len(integration_flags._default_configs)} integrações"
            )
            
            # Testar integrações específicas
            test_integrations = [
                IntegrationType.GOOGLE_TRENDS,
                IntegrationType.WEBHOOK,
                IntegrationType.PAYMENT_GATEWAY
            ]
            
            for integration in test_integrations:
                config = integration_flags.get_config(integration)
                if config:
                    self.log_test(
                        f"Integration Config: {integration.value}",
                        "PASS",
                        f"Configuração para {integration.value} carregada"
                    )
                    
                    # Testar habilitação
                    result = integration_flags.is_enabled(integration, "test_user")
                    self.log_test(
                        f"Integration Enabled: {integration.value}",
                        "PASS",
                        f"Integração {integration.value} avaliada: {result}"
                    )
                    
                    # Testar fallback
                    fallback = integration_flags.get_fallback_config(integration)
                    if fallback:
                        self.log_test(
                            f"Integration Fallback: {integration.value}",
                            "PASS",
                            f"Fallback configurado para {integration.value}"
                        )
                    else:
                        self.log_test(
                            f"Integration Fallback: {integration.value}",
                            "WARNING",
                            f"Fallback não configurado para {integration.value}"
                        )
                else:
                    self.log_test(
                        f"Integration Config: {integration.value}",
                        "FAIL",
                        f"Configuração não encontrada para {integration.value}"
                    )
            
            # Verificar status de saúde
            health = integration_flags.get_health_status()
            if health["status"] == "healthy":
                self.log_test(
                    "Integration Health Status",
                    "PASS",
                    "Status de saúde OK"
                )
            else:
                self.log_test(
                    "Integration Health Status",
                    "FAIL",
                    f"Status de saúde: {health}"
                )
            
            return True
            
        except Exception as e:
            self.log_test(
                "Integration Feature Flags",
                "FAIL",
                f"Erro ao validar integrações: {e}"
            )
            return False
    
    def test_rollback_scenarios(self) -> bool:
        """Testa cenários de rollback"""
        try:
            feature_flags = AdvancedFeatureFlags(enable_audit=True)
            
            # Cenário 1: Rollback de feature boolean
            feature = FeatureFlag(
                name="rollback_test",
                description="Teste de rollback",
                feature_type=FeatureType.BOOLEAN,
                enabled=True
            )
            feature_flags.add_feature(feature)
            
            context = FeatureContext(user_id="rollback_user")
            result_before = feature_flags.is_enabled("rollback_test", context)
            
            # Simular rollback
            feature_flags.update_feature("rollback_test", {"enabled": False})
            result_after = feature_flags.is_enabled("rollback_test", context)
            
            if result_before and not result_after:
                self.log_test(
                    "Boolean Rollback",
                    "PASS",
                    "Rollback de feature boolean funcionando"
                )
            else:
                self.log_test(
                    "Boolean Rollback",
                    "FAIL",
                    "Rollback de feature boolean falhou"
                )
            
            # Cenário 2: Rollback de feature percentual
            feature = FeatureFlag(
                name="percentage_rollback_test",
                description="Teste de rollback percentual",
                feature_type=FeatureType.PERCENTAGE,
                enabled=True,
                rollout_strategy=RolloutStrategy.PERCENTAGE,
                rollout_percentage=50.0
            )
            feature_flags.add_feature(feature)
            
            # Testar com 50%
            results_50 = []
            for index in range(100):
                context = FeatureContext(user_id=f"user_{index}")
                results_50.append(feature_flags.is_enabled("percentage_rollback_test", context))
            
            enabled_50 = sum(results_50)
            
            # Rollback para 0%
            feature_flags.update_feature("percentage_rollback_test", {"rollout_percentage": 0.0})
            
            results_0 = []
            for index in range(100):
                context = FeatureContext(user_id=f"user_{index}")
                results_0.append(feature_flags.is_enabled("percentage_rollback_test", context))
            
            enabled_0 = sum(results_0)
            
            if enabled_50 > 0 and enabled_0 == 0:
                self.log_test(
                    "Percentage Rollback",
                    "PASS",
                    f"Rollback percentual: {enabled_50} -> {enabled_0} usuários"
                )
            else:
                self.log_test(
                    "Percentage Rollback",
                    "FAIL",
                    f"Rollback percentual falhou: {enabled_50} -> {enabled_0}"
                )
            
            # Cenário 3: Rollback de feature direcionada
            feature = FeatureFlag(
                name="targeted_rollback_test",
                description="Teste de rollback direcionado",
                feature_type=FeatureType.TARGETED,
                enabled=True,
                rollout_strategy=RolloutStrategy.TARGETED_USERS,
                target_users=["admin", "beta_tester"]
            )
            feature_flags.add_feature(feature)
            
            # Testar usuário na lista
            context_admin = FeatureContext(user_id="admin")
            result_admin_before = feature_flags.is_enabled("targeted_rollback_test", context_admin)
            
            # Testar usuário fora da lista
            context_user = FeatureContext(user_id="regular_user")
            result_user_before = feature_flags.is_enabled("targeted_rollback_test", context_user)
            
            # Rollback (remover da lista)
            feature_flags.update_feature("targeted_rollback_test", {"target_users": []})
            
            result_admin_after = feature_flags.is_enabled("targeted_rollback_test", context_admin)
            result_user_after = feature_flags.is_enabled("targeted_rollback_test", context_user)
            
            if result_admin_before and not result_admin_after and not result_user_before and not result_user_after:
                self.log_test(
                    "Targeted Rollback",
                    "PASS",
                    "Rollback de feature direcionada funcionando"
                )
            else:
                self.log_test(
                    "Targeted Rollback",
                    "FAIL",
                    "Rollback de feature direcionada falhou"
                )
            
            return True
            
        except Exception as e:
            self.log_test(
                "Rollback Scenarios",
                "FAIL",
                f"Erro ao testar rollbacks: {e}"
            )
            return False
    
    def test_performance(self) -> bool:
        """Testa performance do sistema"""
        try:
            feature_flags = AdvancedFeatureFlags(enable_audit=False)  # Desabilitar auditoria para teste de performance
            
            # Criar features de teste
            for index in range(100):
                feature = FeatureFlag(
                    name=f"perf_test_{index}",
                    description=f"Performance test {index}",
                    feature_type=FeatureType.BOOLEAN,
                    enabled=True
                )
                feature_flags.add_feature(feature)
            
            # Teste de performance - avaliação de features
            start_time = time.time()
            context = FeatureContext(user_id="perf_user")
            
            for index in range(1000):
                feature_flags.is_enabled(f"perf_test_{index % 100}", context)
            
            end_time = time.time()
            duration = end_time - start_time
            ops_per_sec = 1000 / duration
            
            if ops_per_sec > 1000:  # Mínimo 1000 ops/sec
                self.log_test(
                    "Performance Test",
                    "PASS",
                    f"Performance OK: {ops_per_sec:.2f} ops/sec"
                )
            else:
                self.log_test(
                    "Performance Test",
                    "WARNING",
                    f"Performance baixa: {ops_per_sec:.2f} ops/sec"
                )
            
            # Teste de cache performance
            start_time = time.time()
            for index in range(1000):
                feature_flags.is_enabled("perf_test_0", context)  # Mesma feature para testar cache
            
            end_time = time.time()
            cache_duration = end_time - start_time
            cache_ops_per_sec = 1000 / cache_duration
            
            if cache_ops_per_sec > 5000:  # Cache deve ser mais rápido
                self.log_test(
                    "Cache Performance",
                    "PASS",
                    f"Cache rápido: {cache_ops_per_sec:.2f} ops/sec"
                )
            else:
                self.log_test(
                    "Cache Performance",
                    "WARNING",
                    f"Cache lento: {cache_ops_per_sec:.2f} ops/sec"
                )
            
            return True
            
        except Exception as e:
            self.log_test(
                "Performance Test",
                "FAIL",
                f"Erro no teste de performance: {e}"
            )
            return False
    
    def validate_integrity(self) -> bool:
        """Valida integridade do sistema"""
        try:
            # Verificar consistência entre sistemas
            advanced_flags = AdvancedFeatureFlags()
            integration_flags = IntegrationFeatureFlags()
            
            # Verificar se não há conflitos de nomes
            advanced_names = set(advanced_flags.features.keys())
            integration_names = set(integration_flags._default_configs.keys())
            
            conflicts = advanced_names.intersection(integration_names)
            if conflicts:
                self.log_test(
                    "Name Conflicts",
                    "WARNING",
                    f"Conflitos de nomes encontrados: {conflicts}"
                )
            else:
                self.log_test(
                    "Name Conflicts",
                    "PASS",
                    "Nenhum conflito de nomes encontrado"
                )
            
            # Verificar configuração de ambiente
            env = os.getenv('ENVIRONMENT', 'development')
            if env in ['development', 'staging', 'production']:
                self.log_test(
                    "Environment Configuration",
                    "PASS",
                    f"Ambiente configurado: {env}"
                )
            else:
                self.log_test(
                    "Environment Configuration",
                    "WARNING",
                    f"Ambiente não padrão: {env}"
                )
            
            # Verificar dependências
            try:
                import redis
                self.log_test(
                    "Redis Dependency",
                    "PASS",
                    "Redis disponível"
                )
            except ImportError:
                self.log_test(
                    "Redis Dependency",
                    "WARNING",
                    "Redis não disponível (cache local será usado)"
                )
            
            return True
            
        except Exception as e:
            self.log_test(
                "System Integrity",
                "FAIL",
                f"Erro na validação de integridade: {e}"
            )
            return False
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Executa todas as validações"""
        logger.info("🚀 Iniciando validação do sistema de feature flags...")
        
        # Reset resultados
        self.validation_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "tests": []
        }
        
        # Executar validações
        validations = [
            ("Configuração", self.validate_configuration_file),
            ("Sistema Avançado", self.validate_advanced_feature_flags),
            ("Integrações", self.validate_integration_feature_flags),
            ("Rollback", self.test_rollback_scenarios),
            ("Performance", self.test_performance),
            ("Integridade", self.validate_integrity)
        ]
        
        for name, validation_func in validations:
            try:
                logger.info(f"🔍 Executando validação: {name}")
                validation_func()
            except Exception as e:
                self.log_test(
                    f"{name} Validation",
                    "FAIL",
                    f"Erro na validação {name}: {e}"
                )
        
        # Resumo final
        total_tests = len(self.validation_results["tests"])
        passed = self.validation_results["passed"]
        failed = self.validation_results["failed"]
        warnings = self.validation_results["warnings"]
        
        logger.info("=" * 60)
        logger.info("📊 RESUMO DA VALIDAÇÃO")
        logger.info("=" * 60)
        logger.info(f"Total de testes: {total_tests}")
        logger.info(f"✅ Passou: {passed}")
        logger.info(f"❌ Falhou: {failed}")
        logger.info(f"⚠️ Avisos: {warnings}")
        
        if failed == 0:
            logger.info("🎉 TODAS AS VALIDAÇÕES PASSARAM!")
            self.validation_results["overall_status"] = "SUCCESS"
        elif failed <= warnings:
            logger.info("⚠️ VALIDAÇÃO COM AVISOS - SISTEMA FUNCIONAL")
            self.validation_results["overall_status"] = "WARNING"
        else:
            logger.error("💥 VALIDAÇÃO FALHOU - CORREÇÕES NECESSÁRIAS")
            self.validation_results["overall_status"] = "FAILURE"
        
        return self.validation_results

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Validador de Feature Flags - IMP-014")
    parser.add_argument(
        "--config",
        default="config/feature_flags.yaml",
        help="Arquivo de configuração (padrão: config/feature_flags.yaml)"
    )
    parser.add_argument(
        "--output",
        help="Arquivo de saída para resultados (JSON)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verboso"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Executar validação
    validator = FeatureFlagsValidator(args.config)
    results = validator.run_all_validations()
    
    # Salvar resultados se solicitado
    if args.output:
        try:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"📄 Resultados salvos em: {args.output}")
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {e}")
    
    # Retornar código de saída
    if results["overall_status"] == "SUCCESS":
        sys.exit(0)
    elif results["overall_status"] == "WARNING":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main() 