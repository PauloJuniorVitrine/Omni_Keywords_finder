#!/usr/bin/env python3
"""
Script para Reorganizar Estrutura de Testes - Clean Architecture
===============================================================

Reorganiza os testes unitários seguindo o padrão Clean Architecture:
- domain/ - Entidades e regras de negócio
- application/ - Casos de uso e serviços
- infrastructure/ - Implementações técnicas
- interface/ - Controllers e APIs

Autor: Paulo Júnior
Data: 2024-12-20
Tracing ID: REORG-TESTS-001
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple

class TestReorganizer:
    """Reorganizador de estrutura de testes."""
    
    def __init__(self, base_dir: str = "tests/unit"):
        self.base_dir = Path(base_dir)
        self.mapping = self._create_mapping()
        self.stats = {
            'moved': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def _create_mapping(self) -> Dict[str, str]:
        """Cria mapeamento de arquivos para diretórios Clean Architecture."""
        return {
            # Domain Layer
            'test_models.py': 'domain/models.spec.py',
            'test_entities.py': 'domain/entities.spec.py',
            
            # Application Layer
            'test_orchestrator.py': 'application/orchestrator.spec.py',
            'test_gerador_prompt.py': 'application/prompt_generator.spec.py',
            'test_gerar_relatorio_negocio.py': 'application/business_report.spec.py',
            'test_ml_adaptativo_unit.py': 'application/ml_adaptive.spec.py',
            
            # Infrastructure Layer - Validators
            'test_validador_keywords.py': 'infrastructure/validators/validador_keywords.spec.py',
            'test_google_keyword_planner_validator.py': 'infrastructure/validators/google_keyword_planner_validator.spec.py',
            'test_validador_semantico_avancado.py': 'infrastructure/validators/semantic_validator.spec.py',
            'test_credential_validator.py': 'infrastructure/validators/credential_validator.spec.py',
            
            # Infrastructure Layer - Processors
            'test_processador_keywords.py': 'infrastructure/processors/processador_keywords.spec.py',
            'test_parallel_processor.py': 'infrastructure/processors/parallel_processor.spec.py',
            'test_placeholder_unification_system.py': 'infrastructure/processors/placeholder_unification.spec.py',
            'test_hybrid_lacuna_detector.py': 'infrastructure/processors/lacuna_detector.spec.py',
            
            # Infrastructure Layer - Collectors
            'test_google_related.py': 'infrastructure/collectors/google_related.spec.py',
            'test_google_suggest.py': 'infrastructure/collectors/google_suggest.spec.py',
            'test_google_trends.py': 'infrastructure/collectors/google_trends.spec.py',
            'test_google_paa.py': 'infrastructure/collectors/google_paa.spec.py',
            'test_facebook_api.py': 'infrastructure/collectors/facebook_api.spec.py',
            'test_linkedin_api.py': 'infrastructure/collectors/linkedin_api.spec.py',
            'test_twitter_api.py': 'infrastructure/collectors/twitter_api.spec.py',
            'test_instagram.py': 'infrastructure/collectors/instagram.spec.py',
            'test_pinterest.py': 'infrastructure/collectors/pinterest.spec.py',
            'test_reddit.py': 'infrastructure/collectors/reddit.spec.py',
            'test_tiktok.py': 'infrastructure/collectors/tiktok.spec.py',
            'test_youtube.py': 'infrastructure/collectors/youtube.spec.py',
            'test_amazon_coletor.py': 'infrastructure/collectors/amazon_collector.spec.py',
            'test_gsc.py': 'infrastructure/collectors/gsc.spec.py',
            'test_discord.py': 'infrastructure/collectors/discord.spec.py',
            
            # Infrastructure Layer - Exporters
            'test_exportador_keywords.py': 'infrastructure/exporters/keywords_exporter.spec.py',
            'test_exportador_keywords_csv.py': 'infrastructure/exporters/csv_exporter.spec.py',
            'test_template_exporter.py': 'infrastructure/exporters/template_exporter.spec.py',
            
            # Infrastructure Layer - Cache
            'test_cache_distributed.py': 'infrastructure/cache/distributed_cache.spec.py',
            'test_intelligent_cache.py': 'infrastructure/cache/intelligent_cache.spec.py',
            'test_intelligent_cache_imp012.py': 'infrastructure/cache/intelligent_cache_v2.spec.py',
            'test_advanced_caching.py': 'infrastructure/cache/advanced_caching.spec.py',
            'test_distributed_cache.py': 'infrastructure/cache/distributed_cache_v2.spec.py',
            
            # Infrastructure Layer - Rate Limiting
            'test_rate_limiting.py': 'infrastructure/rate_limiting/rate_limiter.spec.py',
            'test_adaptive_rate_limiter.py': 'infrastructure/rate_limiting/adaptive_rate_limiter.spec.py',
            'test_advanced_rate_limiting.py': 'infrastructure/rate_limiting/advanced_rate_limiting.spec.py',
            'test_execucao_rate_limiting.py': 'infrastructure/rate_limiting/execution_rate_limiting.spec.py',
            'test_external_rate_limiter.py': 'infrastructure/rate_limiting/external_rate_limiter.spec.py',
            
            # Infrastructure Layer - Analytics
            'test_analisador_semantico.py': 'infrastructure/analytics/semantic_analyzer.spec.py',
            'test_advanced_analytics_system.py': 'infrastructure/analytics/advanced_analytics.spec.py',
            'test_business_metrics.py': 'infrastructure/analytics/business_metrics.spec.py',
            'test_custom_metrics.py': 'infrastructure/analytics/custom_metrics.spec.py',
            'test_metrics_exporter.py': 'infrastructure/analytics/metrics_exporter.spec.py',
            
            # Infrastructure Layer - ML
            'test_ml_embeddings.py': 'infrastructure/ml/embeddings.spec.py',
            'test_clusterizador_semantico.py': 'infrastructure/ml/semantic_clusterizer.spec.py',
            
            # Infrastructure Layer - Security
            'test_vault_manager.py': 'infrastructure/security/vault_manager.spec.py',
            'test_payment_security_logger.py': 'infrastructure/security/payment_security_logger.spec.py',
            'test_payment_validation.py': 'infrastructure/security/payment_validation.spec.py',
            'test_rbac_sanitization.py': 'infrastructure/security/rbac_sanitization.spec.py',
            'test_rbac_integrity.py': 'infrastructure/security/rbac_integrity.spec.py',
            
            # Infrastructure Layer - Monitoring
            'test_slo_dashboard.py': 'infrastructure/monitoring/slo_dashboard.spec.py',
            'test_alert_manager.py': 'infrastructure/monitoring/alert_manager.spec.py',
            'test_advanced_logging.py': 'infrastructure/monitoring/advanced_logging.spec.py',
            'test_advanced_structured_logger.py': 'infrastructure/monitoring/structured_logger.spec.py',
            
            # Infrastructure Layer - Backup
            'test_backup_restore.py': 'infrastructure/backup/backup_restore.spec.py',
            'test_auto_backup.py': 'infrastructure/backup/auto_backup.spec.py',
            
            # Infrastructure Layer - Notifications
            'test_advanced_notification_system.py': 'infrastructure/notifications/advanced_notifications.spec.py',
            'test_webhook_system.py': 'infrastructure/notifications/webhook_system.spec.py',
            'test_webhooks_secure.py': 'infrastructure/notifications/secure_webhooks.spec.py',
            
            # Infrastructure Layer - Feature Flags
            'test_feature_flags.py': 'infrastructure/feature_flags/feature_flags.spec.py',
            'test_advanced_feature_flags.py': 'infrastructure/feature_flags/advanced_feature_flags.spec.py',
            'test_feature_flags_rollback_imp014.py': 'infrastructure/feature_flags/feature_flags_rollback.spec.py',
            
            # Infrastructure Layer - Audit
            'test_audit_system.py': 'infrastructure/audit/audit_system.spec.py',
            'test_advanced_audit_system.py': 'infrastructure/audit/advanced_audit_system.spec.py',
            'test_auditoria_release.py': 'infrastructure/audit/release_audit.spec.py',
            'test_compliance_framework.py': 'infrastructure/audit/compliance_framework.spec.py',
            'test_compliance_monitoring.py': 'infrastructure/audit/compliance_monitoring.spec.py',
            
            # Infrastructure Layer - Payments
            'test_payment_v1.py': 'infrastructure/payments/payment_v1.spec.py',
            'test_payments_integration.py': 'infrastructure/payments/payments_integration.spec.py',
            'test_external_consumption_validation.py': 'infrastructure/payments/external_consumption.spec.py',
            
            # Infrastructure Layer - Resilience
            'test_resilience.py': 'infrastructure/resilience/resilience.spec.py',
            'test_failover.py': 'infrastructure/resilience/failover.spec.py',
            'test_load_balancing.py': 'infrastructure/resilience/load_balancing.spec.py',
            'test_connection_pooling.py': 'infrastructure/resilience/connection_pooling.spec.py',
            
            # Infrastructure Layer - Database
            'test_database_optimization.py': 'infrastructure/database/optimization.spec.py',
            'test_blogs_persistencia.py': 'infrastructure/database/blogs_persistence.spec.py',
            
            # Infrastructure Layer - CDN
            'test_cdn_invalidation.py': 'infrastructure/cdn/invalidation.spec.py',
            
            # Infrastructure Layer - Anomaly Detection
            'test_anomaly_detection.py': 'infrastructure/anomaly_detection/anomaly_detection.spec.py',
            
            # Infrastructure Layer - GraphQL
            'test_graphql_implementation.py': 'infrastructure/graphql/implementation.spec.py',
            
            # Infrastructure Layer - Progress Tracking
            'test_progress_tracking.py': 'infrastructure/progress_tracking/progress_tracking.spec.py',
            
            # Infrastructure Layer - Error Handling
            'test_error_handler.py': 'infrastructure/error_handling/error_handler.spec.py',
            'test_execucao_validation.py': 'infrastructure/error_handling/execution_validation.spec.py',
            
            # Infrastructure Layer - Utils
            'test_utils.py': 'infrastructure/utils/utils.spec.py',
            'test_utils_keywords_test.spec.py': 'infrastructure/utils/keywords_utils.spec.py',
            'test_hmac_utils_test.spec.py': 'infrastructure/utils/hmac_utils.spec.py',
            'test_ip_whitelist_test.spec.py': 'infrastructure/utils/ip_whitelist.spec.py',
            'test_monitoramento_observabilidade_test.spec.py': 'infrastructure/utils/monitoring_utils.spec.py',
            
            # Infrastructure Layer - Configuration
            'test_config_versioning.py': 'infrastructure/configuration/versioning.spec.py',
            'test_cors_config.py': 'infrastructure/configuration/cors_config.spec.py',
            
            # Infrastructure Layer - Type Generation
            'test_type_generation.py': 'infrastructure/type_generation/type_generation.spec.py',
            'test_orphan_endpoints.py': 'infrastructure/type_generation/orphan_endpoints.spec.py',
            
            # Interface Layer
            'test_dashboard.py': 'interface/dashboard.spec.py',
            'test_websocket_docs.py': 'interface/websocket_docs.spec.py',
            
            # Keep existing organized structure
            'conftest.py': 'conftest.py',
            '__init__.py': '__init__.py'
        }
    
    def _should_skip_file(self, filename: str) -> bool:
        """Verifica se o arquivo deve ser pulado."""
        skip_patterns = [
            r'^\.',  # Arquivos ocultos
            r'\.pyc$',  # Arquivos compilados
            r'__pycache__',  # Cache do Python
            r'\.log$',  # Arquivos de log
            r'\.tmp$',  # Arquivos temporários
            r'\.bak$',  # Arquivos de backup
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, filename):
                return True
        return False
    
    def _create_directory(self, dir_path: Path) -> None:
        """Cria diretório se não existir."""
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Diretório criado: {dir_path}")
        except Exception as e:
            print(f"❌ Erro ao criar diretório {dir_path}: {e}")
            self.stats['errors'] += 1
    
    def _move_file(self, source: Path, destination: Path) -> bool:
        """Move arquivo de teste para nova localização."""
        try:
            # Criar diretório de destino se não existir
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Verificar se arquivo de destino já existe
            if destination.exists():
                print(f"⚠️  Arquivo já existe: {destination}")
                return False
            
            # Mover arquivo
            shutil.move(str(source), str(destination))
            print(f"✅ Movido: {source.name} -> {destination}")
            self.stats['moved'] += 1
            return True
            
        except Exception as e:
            print(f"❌ Erro ao mover {source}: {e}")
            self.stats['errors'] += 1
            return False
    
    def reorganize(self) -> None:
        """Executa a reorganização da estrutura de testes."""
        print("🔄 Iniciando reorganização da estrutura de testes...")
        print("=" * 60)
        
        # Processar arquivos na raiz do diretório de testes
        for file_path in self.base_dir.iterdir():
            if not file_path.is_file():
                continue
                
            filename = file_path.name
            
            # Pular arquivos que devem ser ignorados
            if self._should_skip_file(filename):
                print(f"⏭️  Pulando: {filename}")
                self.stats['skipped'] += 1
                continue
            
            # Verificar se arquivo está no mapeamento
            if filename in self.mapping:
                destination = self.base_dir / self.mapping[filename]
                self._move_file(file_path, destination)
            else:
                print(f"⚠️  Arquivo não mapeado: {filename}")
                self.stats['skipped'] += 1
        
        # Criar arquivos __init__.py nos diretórios
        self._create_init_files()
        
        # Exibir estatísticas
        self._print_stats()
    
    def _create_init_files(self) -> None:
        """Cria arquivos __init__.py nos diretórios organizados."""
        init_dirs = [
            'domain',
            'application', 
            'infrastructure/validators',
            'infrastructure/processors',
            'infrastructure/collectors',
            'infrastructure/exporters',
            'infrastructure/cache',
            'infrastructure/rate_limiting',
            'infrastructure/analytics',
            'infrastructure/ml',
            'infrastructure/security',
            'infrastructure/monitoring',
            'infrastructure/backup',
            'infrastructure/notifications',
            'infrastructure/feature_flags',
            'infrastructure/audit',
            'infrastructure/payments',
            'infrastructure/resilience',
            'infrastructure/database',
            'infrastructure/cdn',
            'infrastructure/anomaly_detection',
            'infrastructure/graphql',
            'infrastructure/progress_tracking',
            'infrastructure/error_handling',
            'infrastructure/utils',
            'infrastructure/configuration',
            'infrastructure/type_generation',
            'interface'
        ]
        
        for dir_name in init_dirs:
            init_file = self.base_dir / dir_name / '__init__.py'
            if not init_file.exists():
                init_file.parent.mkdir(parents=True, exist_ok=True)
                init_file.touch()
                print(f"✅ __init__.py criado: {init_file}")
    
    def _print_stats(self) -> None:
        """Exibe estatísticas da reorganização."""
        print("\n" + "=" * 60)
        print("📊 ESTATÍSTICAS DA REORGANIZAÇÃO")
        print("=" * 60)
        print(f"✅ Arquivos movidos: {self.stats['moved']}")
        print(f"⏭️  Arquivos pulados: {self.stats['skipped']}")
        print(f"❌ Erros: {self.stats['errors']}")
        print(f"📁 Total processado: {sum(self.stats.values())}")
        
        if self.stats['errors'] == 0:
            print("\n🎉 Reorganização concluída com sucesso!")
        else:
            print(f"\n⚠️  Reorganização concluída com {self.stats['errors']} erros.")
    
    def create_structure_documentation(self) -> None:
        """Cria documentação da nova estrutura."""
        doc_content = """# Estrutura de Testes - Clean Architecture

## 📁 Organização por Camadas

### 🏗️ Domain Layer
```
tests/unit/domain/
├── models.spec.py          # Testes das entidades de domínio
└── entities.spec.py        # Testes das regras de negócio
```

### 🔧 Application Layer
```
tests/unit/application/
├── orchestrator.spec.py           # Testes do orquestrador principal
├── prompt_generator.spec.py       # Testes do gerador de prompts
├── business_report.spec.py        # Testes de relatórios de negócio
└── ml_adaptive.spec.py           # Testes de ML adaptativo
```

### 🏗️ Infrastructure Layer
```
tests/unit/infrastructure/
├── validators/                    # Validadores
│   ├── validador_keywords.spec.py
│   ├── google_keyword_planner_validator.spec.py
│   ├── semantic_validator.spec.py
│   └── credential_validator.spec.py
├── processors/                    # Processadores
│   ├── processador_keywords.spec.py
│   ├── parallel_processor.spec.py
│   ├── placeholder_unification.spec.py
│   └── lacuna_detector.spec.py
├── collectors/                    # Coletores de dados
│   ├── google_related.spec.py
│   ├── google_suggest.spec.py
│   ├── google_trends.spec.py
│   ├── facebook_api.spec.py
│   ├── linkedin_api.spec.py
│   ├── twitter_api.spec.py
│   └── ...
├── exporters/                     # Exportadores
│   ├── keywords_exporter.spec.py
│   ├── csv_exporter.spec.py
│   └── template_exporter.spec.py
├── cache/                         # Sistema de cache
│   ├── distributed_cache.spec.py
│   ├── intelligent_cache.spec.py
│   └── advanced_caching.spec.py
├── rate_limiting/                 # Rate limiting
│   ├── rate_limiter.spec.py
│   ├── adaptive_rate_limiter.spec.py
│   └── advanced_rate_limiting.spec.py
├── analytics/                     # Analytics
│   ├── semantic_analyzer.spec.py
│   ├── business_metrics.spec.py
│   └── metrics_exporter.spec.py
├── ml/                           # Machine Learning
│   ├── embeddings.spec.py
│   └── semantic_clusterizer.spec.py
├── security/                     # Segurança
│   ├── vault_manager.spec.py
│   ├── payment_security_logger.spec.py
│   └── rbac_sanitization.spec.py
├── monitoring/                   # Monitoramento
│   ├── slo_dashboard.spec.py
│   ├── alert_manager.spec.py
│   └── advanced_logging.spec.py
├── backup/                       # Backup
│   ├── backup_restore.spec.py
│   └── auto_backup.spec.py
├── notifications/                # Notificações
│   ├── advanced_notifications.spec.py
│   ├── webhook_system.spec.py
│   └── secure_webhooks.spec.py
├── feature_flags/                # Feature Flags
│   ├── feature_flags.spec.py
│   ├── advanced_feature_flags.spec.py
│   └── feature_flags_rollback.spec.py
├── audit/                        # Auditoria
│   ├── audit_system.spec.py
│   ├── advanced_audit_system.spec.py
│   └── compliance_framework.spec.py
├── payments/                     # Pagamentos
│   ├── payment_v1.spec.py
│   ├── payments_integration.spec.py
│   └── external_consumption.spec.py
├── resilience/                   # Resiliência
│   ├── resilience.spec.py
│   ├── failover.spec.py
│   └── load_balancing.spec.py
├── database/                     # Banco de dados
│   ├── optimization.spec.py
│   └── blogs_persistence.spec.py
├── cdn/                          # CDN
│   └── invalidation.spec.py
├── anomaly_detection/            # Detecção de anomalias
│   └── anomaly_detection.spec.py
├── graphql/                      # GraphQL
│   └── implementation.spec.py
├── progress_tracking/            # Acompanhamento de progresso
│   └── progress_tracking.spec.py
├── error_handling/               # Tratamento de erros
│   ├── error_handler.spec.py
│   └── execution_validation.spec.py
├── utils/                        # Utilitários
│   ├── utils.spec.py
│   ├── keywords_utils.spec.py
│   └── hmac_utils.spec.py
├── configuration/                # Configuração
│   ├── versioning.spec.py
│   └── cors_config.spec.py
└── type_generation/              # Geração de tipos
    ├── type_generation.spec.py
    └── orphan_endpoints.spec.py
```

### 🌐 Interface Layer
```
tests/unit/interface/
├── dashboard.spec.py             # Testes do dashboard
└── websocket_docs.spec.py        # Testes da documentação WebSocket
```

## 🎯 Benefícios da Nova Estrutura

1. **Organização Clara**: Separação por responsabilidades
2. **Facilita Manutenção**: Localização rápida de testes
3. **Escalabilidade**: Estrutura preparada para crescimento
4. **Padrão Clean Architecture**: Seguindo boas práticas
5. **Nomenclatura Consistente**: Arquivos .spec.py para testes

## 📋 Convenções

- **Arquivos de teste**: Sufixo `.spec.py`
- **Organização**: Por camada e funcionalidade
- **Nomenclatura**: Descritiva e consistente
- **Estrutura**: Hierárquica e lógica

## 🚀 Como Usar

```bash
# Executar todos os testes
python -m pytest tests/unit/

# Executar testes de uma camada específica
python -m pytest tests/unit/domain/
python -m pytest tests/unit/infrastructure/validators/
python -m pytest tests/unit/application/

# Executar testes de uma funcionalidade específica
python -m pytest tests/unit/infrastructure/collectors/google_related.spec.py
```
"""
        
        doc_file = self.base_dir / "STRUCTURE_DOCUMENTATION.md"
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"📚 Documentação criada: {doc_file}")


def main():
    """Função principal."""
    print("🔄 REORGANIZAÇÃO DE ESTRUTURA DE TESTES")
    print("=" * 60)
    
    reorganizer = TestReorganizer()
    
    # Executar reorganização
    reorganizer.reorganize()
    
    # Criar documentação
    reorganizer.create_structure_documentation()
    
    print("\n🎉 Processo concluído!")
    print("📁 Verifique a nova estrutura em tests/unit/")
    print("📚 Consulte STRUCTURE_DOCUMENTATION.md para detalhes")


if __name__ == "__main__":
    main() 