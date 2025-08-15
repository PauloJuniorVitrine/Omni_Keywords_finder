# Script para Reorganizar Estrutura de Testes - Clean Architecture
# ===============================================================
#
# Reorganiza os testes unitários seguindo o padrão Clean Architecture:
# - domain/ - Entidades e regras de negócio
# - application/ - Casos de uso e serviços
# - infrastructure/ - Implementações técnicas
# - interface/ - Controllers e APIs
#
# Autor: Paulo Júnior
# Data: 2024-12-20
# Tracing ID: REORG-TESTS-PS-001

Write-Host "🔄 REORGANIZAÇÃO DE ESTRUTURA DE TESTES" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$baseDir = "tests/unit"
$stats = @{
    'moved' = 0
    'skipped' = 0
    'errors' = 0
}

# Mapeamento de arquivos para diretórios Clean Architecture
$mapping = @{
    # Domain Layer
    'test_models.py' = 'domain/models.spec.py'
    'test_entities.py' = 'domain/entities.spec.py'
    
    # Application Layer
    'test_orchestrator.py' = 'application/orchestrator.spec.py'
    'test_gerador_prompt.py' = 'application/prompt_generator.spec.py'
    'test_gerar_relatorio_negocio.py' = 'application/business_report.spec.py'
    'test_ml_adaptativo_unit.py' = 'application/ml_adaptive.spec.py'
    
    # Infrastructure Layer - Validators
    'test_validador_keywords.py' = 'infrastructure/validators/validador_keywords.spec.py'
    'test_google_keyword_planner_validator.py' = 'infrastructure/validators/google_keyword_planner_validator.spec.py'
    'test_validador_semantico_avancado.py' = 'infrastructure/validators/semantic_validator.spec.py'
    'test_credential_validator.py' = 'infrastructure/validators/credential_validator.spec.py'
    
    # Infrastructure Layer - Processors
    'test_processador_keywords.py' = 'infrastructure/processors/processador_keywords.spec.py'
    'test_parallel_processor.py' = 'infrastructure/processors/parallel_processor.spec.py'
    'test_placeholder_unification_system.py' = 'infrastructure/processors/placeholder_unification.spec.py'
    'test_hybrid_lacuna_detector.py' = 'infrastructure/processors/lacuna_detector.spec.py'
    
    # Infrastructure Layer - Collectors
    'test_google_related.py' = 'infrastructure/collectors/google_related.spec.py'
    'test_google_suggest.py' = 'infrastructure/collectors/google_suggest.spec.py'
    'test_google_trends.py' = 'infrastructure/collectors/google_trends.spec.py'
    'test_google_paa.py' = 'infrastructure/collectors/google_paa.spec.py'
    'test_facebook_api.py' = 'infrastructure/collectors/facebook_api.spec.py'
    'test_linkedin_api.py' = 'infrastructure/collectors/linkedin_api.spec.py'
    'test_twitter_api.py' = 'infrastructure/collectors/twitter_api.spec.py'
    'test_instagram.py' = 'infrastructure/collectors/instagram.spec.py'
    'test_pinterest.py' = 'infrastructure/collectors/pinterest.spec.py'
    'test_reddit.py' = 'infrastructure/collectors/reddit.spec.py'
    'test_tiktok.py' = 'infrastructure/collectors/tiktok.spec.py'
    'test_youtube.py' = 'infrastructure/collectors/youtube.spec.py'
    'test_amazon_coletor.py' = 'infrastructure/collectors/amazon_collector.spec.py'
    'test_gsc.py' = 'infrastructure/collectors/gsc.spec.py'
    'test_discord.py' = 'infrastructure/collectors/discord.spec.py'
    
    # Infrastructure Layer - Exporters
    'test_exportador_keywords.py' = 'infrastructure/exporters/keywords_exporter.spec.py'
    'test_exportador_keywords_csv.py' = 'infrastructure/exporters/csv_exporter.spec.py'
    'test_template_exporter.py' = 'infrastructure/exporters/template_exporter.spec.py'
    
    # Infrastructure Layer - Cache
    'test_cache_distributed.py' = 'infrastructure/cache/distributed_cache.spec.py'
    'test_intelligent_cache.py' = 'infrastructure/cache/intelligent_cache.spec.py'
    'test_intelligent_cache_imp012.py' = 'infrastructure/cache/intelligent_cache_v2.spec.py'
    'test_advanced_caching.py' = 'infrastructure/cache/advanced_caching.spec.py'
    'test_distributed_cache.py' = 'infrastructure/cache/distributed_cache_v2.spec.py'
    
    # Infrastructure Layer - Rate Limiting
    'test_rate_limiting.py' = 'infrastructure/rate_limiting/rate_limiter.spec.py'
    'test_adaptive_rate_limiter.py' = 'infrastructure/rate_limiting/adaptive_rate_limiter.spec.py'
    'test_advanced_rate_limiting.py' = 'infrastructure/rate_limiting/advanced_rate_limiting.spec.py'
    'test_execucao_rate_limiting.py' = 'infrastructure/rate_limiting/execution_rate_limiting.spec.py'
    'test_external_rate_limiter.py' = 'infrastructure/rate_limiting/external_rate_limiter.spec.py'
    
    # Infrastructure Layer - Analytics
    'test_analisador_semantico.py' = 'infrastructure/analytics/semantic_analyzer.spec.py'
    'test_advanced_analytics_system.py' = 'infrastructure/analytics/advanced_analytics.spec.py'
    'test_business_metrics.py' = 'infrastructure/analytics/business_metrics.spec.py'
    'test_custom_metrics.py' = 'infrastructure/analytics/custom_metrics.spec.py'
    'test_metrics_exporter.py' = 'infrastructure/analytics/metrics_exporter.spec.py'
    
    # Infrastructure Layer - ML
    'test_ml_embeddings.py' = 'infrastructure/ml/embeddings.spec.py'
    'test_clusterizador_semantico.py' = 'infrastructure/ml/semantic_clusterizer.spec.py'
    
    # Infrastructure Layer - Security
    'test_vault_manager.py' = 'infrastructure/security/vault_manager.spec.py'
    'test_payment_security_logger.py' = 'infrastructure/security/payment_security_logger.spec.py'
    'test_payment_validation.py' = 'infrastructure/security/payment_validation.spec.py'
    'test_rbac_sanitization.py' = 'infrastructure/security/rbac_sanitization.spec.py'
    'test_rbac_integrity.py' = 'infrastructure/security/rbac_integrity.spec.py'
    
    # Infrastructure Layer - Monitoring
    'test_slo_dashboard.py' = 'infrastructure/monitoring/slo_dashboard.spec.py'
    'test_alert_manager.py' = 'infrastructure/monitoring/alert_manager.spec.py'
    'test_advanced_logging.py' = 'infrastructure/monitoring/advanced_logging.spec.py'
    'test_advanced_structured_logger.py' = 'infrastructure/monitoring/structured_logger.spec.py'
    
    # Infrastructure Layer - Backup
    'test_backup_restore.py' = 'infrastructure/backup/backup_restore.spec.py'
    'test_auto_backup.py' = 'infrastructure/backup/auto_backup.spec.py'
    
    # Infrastructure Layer - Notifications
    'test_advanced_notification_system.py' = 'infrastructure/notifications/advanced_notifications.spec.py'
    'test_webhook_system.py' = 'infrastructure/notifications/webhook_system.spec.py'
    'test_webhooks_secure.py' = 'infrastructure/notifications/secure_webhooks.spec.py'
    
    # Infrastructure Layer - Feature Flags
    'test_feature_flags.py' = 'infrastructure/feature_flags/feature_flags.spec.py'
    'test_advanced_feature_flags.py' = 'infrastructure/feature_flags/advanced_feature_flags.spec.py'
    'test_feature_flags_rollback_imp014.py' = 'infrastructure/feature_flags/feature_flags_rollback.spec.py'
    
    # Infrastructure Layer - Audit
    'test_audit_system.py' = 'infrastructure/audit/audit_system.spec.py'
    'test_advanced_audit_system.py' = 'infrastructure/audit/advanced_audit_system.spec.py'
    'test_auditoria_release.py' = 'infrastructure/audit/release_audit.spec.py'
    'test_compliance_framework.py' = 'infrastructure/audit/compliance_framework.spec.py'
    'test_compliance_monitoring.py' = 'infrastructure/audit/compliance_monitoring.spec.py'
    
    # Infrastructure Layer - Payments
    'test_payment_v1.py' = 'infrastructure/payments/payment_v1.spec.py'
    'test_payments_integration.py' = 'infrastructure/payments/payments_integration.spec.py'
    'test_external_consumption_validation.py' = 'infrastructure/payments/external_consumption.spec.py'
    
    # Infrastructure Layer - Resilience
    'test_resilience.py' = 'infrastructure/resilience/resilience.spec.py'
    'test_failover.py' = 'infrastructure/resilience/failover.spec.py'
    'test_load_balancing.py' = 'infrastructure/resilience/load_balancing.spec.py'
    'test_connection_pooling.py' = 'infrastructure/resilience/connection_pooling.spec.py'
    
    # Infrastructure Layer - Database
    'test_database_optimization.py' = 'infrastructure/database/optimization.spec.py'
    'test_blogs_persistencia.py' = 'infrastructure/database/blogs_persistence.spec.py'
    
    # Infrastructure Layer - CDN
    'test_cdn_invalidation.py' = 'infrastructure/cdn/invalidation.spec.py'
    
    # Infrastructure Layer - Anomaly Detection
    'test_anomaly_detection.py' = 'infrastructure/anomaly_detection/anomaly_detection.spec.py'
    
    # Infrastructure Layer - GraphQL
    'test_graphql_implementation.py' = 'infrastructure/graphql/implementation.spec.py'
    
    # Infrastructure Layer - Progress Tracking
    'test_progress_tracking.py' = 'infrastructure/progress_tracking/progress_tracking.spec.py'
    
    # Infrastructure Layer - Error Handling
    'test_error_handler.py' = 'infrastructure/error_handling/error_handler.spec.py'
    'test_execucao_validation.py' = 'infrastructure/error_handling/execution_validation.spec.py'
    
    # Infrastructure Layer - Utils
    'test_utils.py' = 'infrastructure/utils/utils.spec.py'
    'test_utils_keywords_test.spec.py' = 'infrastructure/utils/keywords_utils.spec.py'
    'test_hmac_utils_test.spec.py' = 'infrastructure/utils/hmac_utils.spec.py'
    'test_ip_whitelist_test.spec.py' = 'infrastructure/utils/ip_whitelist.spec.py'
    'test_monitoramento_observabilidade_test.spec.py' = 'infrastructure/utils/monitoring_utils.spec.py'
    
    # Infrastructure Layer - Configuration
    'test_config_versioning.py' = 'infrastructure/configuration/versioning.spec.py'
    'test_cors_config.py' = 'infrastructure/configuration/cors_config.spec.py'
    
    # Infrastructure Layer - Type Generation
    'test_type_generation.py' = 'infrastructure/type_generation/type_generation.spec.py'
    'test_orphan_endpoints.py' = 'infrastructure/type_generation/orphan_endpoints.spec.py'
    
    # Interface Layer
    'test_dashboard.py' = 'interface/dashboard.spec.py'
    'test_websocket_docs.py' = 'interface/websocket_docs.spec.py'
}

# Função para verificar se arquivo deve ser pulado
function Should-SkipFile {
    param([string]$filename)
    
    $skipPatterns = @(
        '^\.',           # Arquivos ocultos
        '\.pyc$',        # Arquivos compilados
        '__pycache__',   # Cache do Python
        '\.log$',        # Arquivos de log
        '\.tmp$',        # Arquivos temporários
        '\.bak$'         # Arquivos de backup
    )
    
    foreach ($pattern in $skipPatterns) {
        if ($filename -match $pattern) {
            return $true
        }
    }
    return $false
}

# Função para mover arquivo
function Move-TestFile {
    param([string]$source, [string]$destination)
    
    try {
        $sourcePath = Join-Path $baseDir $source
        $destPath = Join-Path $baseDir $destination
        
        if (Test-Path $sourcePath) {
            # Criar diretório de destino se não existir
            $destDir = Split-Path $destPath -Parent
            if (!(Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                Write-Host "✅ Diretório criado: $destDir" -ForegroundColor Green
            }
            
            # Verificar se arquivo de destino já existe
            if (Test-Path $destPath) {
                Write-Host "⚠️  Arquivo já existe: $destination" -ForegroundColor Yellow
                $stats.skipped++
                return $false
            }
            
            # Mover arquivo
            Move-Item $sourcePath $destPath -Force
            Write-Host "✅ Movido: $source -> $destination" -ForegroundColor Green
            $stats.moved++
            return $true
        } else {
            Write-Host "⚠️  Arquivo não encontrado: $source" -ForegroundColor Yellow
            $stats.skipped++
            return $false
        }
    }
    catch {
        Write-Host "❌ Erro ao mover $source`: $($_.Exception.Message)" -ForegroundColor Red
        $stats.errors++
        return $false
    }
}

# Função para criar arquivos __init__.py
function Create-InitFiles {
    $initDirs = @(
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
    )
    
    foreach ($dir in $initDirs) {
        $initFile = Join-Path $baseDir $dir "__init__.py"
        if (!(Test-Path $initFile)) {
            $initDir = Split-Path $initFile -Parent
            if (!(Test-Path $initDir)) {
                New-Item -ItemType Directory -Path $initDir -Force | Out-Null
            }
            New-Item -ItemType File -Path $initFile -Force | Out-Null
            Write-Host "✅ __init__.py criado: $initFile" -ForegroundColor Green
        }
    }
}

# Função para exibir estatísticas
function Show-Stats {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "📊 ESTATÍSTICAS DA REORGANIZAÇÃO" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "✅ Arquivos movidos: $($stats.moved)" -ForegroundColor Green
    Write-Host "⏭️  Arquivos pulados: $($stats.skipped)" -ForegroundColor Yellow
    Write-Host "❌ Erros: $($stats.errors)" -ForegroundColor Red
    Write-Host "📁 Total processado: $($stats.moved + $stats.skipped + $stats.errors)" -ForegroundColor White
    
    if ($stats.errors -eq 0) {
        Write-Host ""
        Write-Host "🎉 Reorganização concluída com sucesso!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Reorganização concluída com $($stats.errors) erros." -ForegroundColor Yellow
    }
}

# Executar reorganização
Write-Host "🔄 Iniciando reorganização da estrutura de testes..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Processar arquivos na raiz do diretório de testes
$testFiles = Get-ChildItem -Path $baseDir -File | Where-Object { $_.Name -like "test_*.py" }

foreach ($file in $testFiles) {
    $filename = $file.Name
    
    # Pular arquivos que devem ser ignorados
    if (Should-SkipFile $filename) {
        Write-Host "⏭️  Pulando: $filename" -ForegroundColor Yellow
        $stats.skipped++
        continue
    }
    
    # Verificar se arquivo está no mapeamento
    if ($mapping.ContainsKey($filename)) {
        $destination = $mapping[$filename]
        Move-TestFile $filename $destination
    } else {
        Write-Host "⚠️  Arquivo não mapeado: $filename" -ForegroundColor Yellow
        $stats.skipped++
    }
}

# Criar arquivos __init__.py nos diretórios
Create-InitFiles

# Exibir estatísticas
Show-Stats

Write-Host ""
Write-Host "Processo concluido!" -ForegroundColor Green
Write-Host "Verifique a nova estrutura em $baseDir" -ForegroundColor Cyan 