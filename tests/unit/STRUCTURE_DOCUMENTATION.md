# Estrutura de Testes - Clean Architecture

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
