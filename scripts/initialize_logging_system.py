#!/usr/bin/env python3
"""
Script de Inicialização do Sistema de Logging - Fase 3.1 COMPLETA
Tracing ID: CHECKLIST_FINAL_20250127_003
Data: 2025-01-27
Status: IMPLEMENTAÇÃO COMPLETA

Script para inicializar o sistema completo de logging:
- structlog para logging estruturado
- Correlation IDs automáticos
- Log rotation configurável
- Integração ELK Stack
- Performance otimizada
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Verificar se todas as dependências estão instaladas."""
    required_packages = [
        'structlog',
        'requests',
        'psutil',
        'yaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANDO")
    
    if missing_packages:
        print(f"\n❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install " + " ".join(missing_packages))
        return False
    
    return True

def initialize_logging_system():
    """Inicializar sistema de logging completo."""
    try:
        print("🚀 Inicializando sistema de logging estruturado...")
        
        # Importar módulos de logging
        from infrastructure.logging.advanced_structured_logger import (
            get_logger, log_info, LogCategory
        )
        from infrastructure.logging.log_rotation_config import get_log_rotator
        from infrastructure.logging.elk_stack_config import get_elk_manager
        
        # Obter instâncias
        logger = get_logger()
        rotator = get_log_rotator()
        elk_manager = get_elk_manager()
        
        print("✅ Sistema de logging estruturado inicializado")
        print("✅ Rotador de logs inicializado")
        print("✅ Configuração ELK Stack carregada")
        
        # Log de inicialização
        log_info(
            "Sistema de logging completo inicializado via script",
            LogCategory.SYSTEM,
            script_name="initialize_logging_system.py",
            timestamp=datetime.now().isoformat()
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar sistema de logging: {e}")
        return False

def test_logging_functionality():
    """Testar funcionalidades do sistema de logging."""
    try:
        print("\n🧪 Testando funcionalidades do sistema de logging...")
        
        from infrastructure.logging.advanced_structured_logger import (
            get_logger, log_info, log_warning, log_error, log_audit,
            log_security, log_performance, LogCategory, set_correlation_id
        )
        
        logger = get_logger()
        
        # Teste 1: Log básico
        print("📝 Teste 1: Log básico")
        log_info("Teste de log básico", LogCategory.SYSTEM)
        
        # Teste 2: Log com correlation ID
        print("📝 Teste 2: Log com correlation ID")
        correlation_id = f"test-{int(time.time())}"
        set_correlation_id(correlation_id)
        log_info("Teste com correlation ID", LogCategory.API)
        
        # Teste 3: Diferentes categorias
        print("📝 Teste 3: Diferentes categorias")
        log_warning("Teste de warning", LogCategory.SECURITY)
        log_error("Teste de erro", LogCategory.ERROR)
        log_audit("Teste de auditoria")
        log_security("Teste de segurança")
        log_performance("Teste de performance")
        
        # Teste 4: Métricas
        print("📝 Teste 4: Métricas")
        metrics = logger.get_metrics()
        print(f"   Total de logs: {metrics['total_logs']}")
        print(f"   Logs por nível: {metrics['logs_by_level']}")
        print(f"   Taxa de erro: {metrics['error_rate']:.2f}%")
        
        print("✅ Todos os testes passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        return False

def test_log_rotation():
    """Testar funcionalidade de rotação de logs."""
    try:
        print("\n🔄 Testando rotação de logs...")
        
        from infrastructure.logging.log_rotation_config import get_log_rotator
        
        rotator = get_log_rotator()
        
        # Teste 1: Estatísticas de logs
        print("📊 Teste 1: Estatísticas de logs")
        stats = rotator.get_log_stats()
        print(f"   Total de arquivos: {stats['total_files']}")
        print(f"   Tamanho total: {stats['total_size_gb']:.2f} GB")
        
        # Teste 2: Uso de disco
        print("📊 Teste 2: Uso de disco")
        disk_usage = rotator.get_disk_usage()
        print(f"   Uso de disco: {disk_usage['usage_percent']:.2f}%")
        print(f"   Espaço livre: {disk_usage['free_gb']:.2f} GB")
        
        # Teste 3: Alerta de uso de disco
        print("📊 Teste 3: Alerta de uso de disco")
        alert = rotator.check_disk_usage_alert()
        print(f"   Alerta necessário: {alert}")
        
        print("✅ Testes de rotação passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos testes de rotação: {e}")
        return False

def test_elk_configuration():
    """Testar configuração do ELK Stack."""
    try:
        print("\n🔍 Testando configuração ELK Stack...")
        
        from infrastructure.logging.elk_stack_config import get_elk_manager
        
        elk_manager = get_elk_manager()
        
        # Teste 1: Configuração
        print("⚙️ Teste 1: Configuração")
        print(f"   Elasticsearch: {elk_manager.config.elasticsearch.url}")
        print(f"   Logstash: {elk_manager.config.logstash.url}")
        print(f"   Kibana: {elk_manager.config.kibana.url}")
        print(f"   Habilitado: {elk_manager.config.enabled}")
        
        # Teste 2: Geração de configurações
        print("⚙️ Teste 2: Geração de configurações")
        elasticsearch_config = elk_manager.generate_elasticsearch_config()
        logstash_config = elk_manager.generate_logstash_config()
        dashboards = elk_manager.generate_kibana_dashboards()
        alert_rules = elk_manager.generate_alert_rules()
        
        print(f"   Config Elasticsearch: {len(elasticsearch_config)} caracteres")
        print(f"   Config Logstash: {len(logstash_config)} caracteres")
        print(f"   Dashboards: {len(dashboards)}")
        print(f"   Regras de alerta: {len(alert_rules)}")
        
        # Teste 3: Salvar configurações
        print("⚙️ Teste 3: Salvar configurações")
        elk_manager.save_configs()
        print("   Configurações salvas em config/elk_stack/")
        
        print("✅ Testes de configuração ELK passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos testes de configuração ELK: {e}")
        return False

def create_sample_logs():
    """Criar logs de exemplo para demonstração."""
    try:
        print("\n📝 Criando logs de exemplo...")
        
        from infrastructure.logging.advanced_structured_logger import (
            get_logger, log_info, log_warning, log_error, log_audit,
            log_security, log_performance, LogCategory, set_correlation_id
        )
        
        logger = get_logger()
        
        # Simular diferentes cenários
        scenarios = [
            {
                "correlation_id": "user-session-123",
                "user_id": "user123",
                "message": "Usuário fez login",
                "category": LogCategory.SECURITY
            },
            {
                "correlation_id": "api-call-456",
                "user_id": "user123",
                "message": "API chamada: /api/keywords/search",
                "category": LogCategory.API
            },
            {
                "correlation_id": "db-operation-789",
                "user_id": "user123",
                "message": "Query executada: SELECT keywords",
                "category": LogCategory.DATABASE
            },
            {
                "correlation_id": "cache-hit-101",
                "user_id": "user123",
                "message": "Cache hit: keywords_user123",
                "category": LogCategory.CACHE
            },
            {
                "correlation_id": "performance-202",
                "user_id": "user123",
                "message": "Tempo de resposta: 150ms",
                "category": LogCategory.PERFORMANCE
            }
        ]
        
        for scenario in scenarios:
            set_correlation_id(scenario["correlation_id"])
            log_info(
                scenario["message"],
                scenario["category"],
                user_id=scenario["user_id"],
                timestamp=datetime.now().isoformat()
            )
        
        print(f"✅ {len(scenarios)} logs de exemplo criados!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar logs de exemplo: {e}")
        return False

def generate_report():
    """Gerar relatório do sistema de logging."""
    try:
        print("\n📊 Gerando relatório do sistema...")
        
        from infrastructure.logging.advanced_structured_logger import get_logger
        from infrastructure.logging.log_rotation_config import get_log_rotator
        from infrastructure.logging.elk_stack_config import get_elk_manager
        
        logger = get_logger()
        rotator = get_log_rotator()
        elk_manager = get_elk_manager()
        
        # Coletar dados
        metrics = logger.get_metrics()
        disk_usage = rotator.get_disk_usage()
        log_stats = rotator.get_log_stats()
        
        # Criar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "status": "operational",
                "version": "3.1.0",
                "environment": os.getenv("ENVIRONMENT", "development")
            },
            "logging": {
                "total_logs": metrics["total_logs"],
                "logs_by_level": metrics["logs_by_level"],
                "logs_by_category": metrics["logs_by_category"],
                "error_rate": metrics["error_rate"],
                "avg_log_size": metrics["avg_log_size"],
                "avg_response_time": metrics["avg_response_time"]
            },
            "storage": {
                "disk_usage_percent": disk_usage["usage_percent"],
                "free_space_gb": disk_usage["free_gb"],
                "log_files_count": log_stats["total_files"],
                "log_size_gb": log_stats["total_size_gb"]
            },
            "elk_stack": {
                "enabled": elk_manager.config.enabled,
                "elasticsearch_url": elk_manager.config.elasticsearch.url,
                "logstash_url": elk_manager.config.logstash.url,
                "kibana_url": elk_manager.config.kibana.url
            }
        }
        
        # Salvar relatório
        report_file = Path("logs/logging_system_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Relatório salvo em: {report_file}")
        
        # Exibir resumo
        print("\n📋 RESUMO DO SISTEMA:")
        print(f"   Logs totais: {report['logging']['total_logs']}")
        print(f"   Taxa de erro: {report['logging']['error_rate']:.2f}%")
        print(f"   Uso de disco: {report['storage']['disk_usage_percent']:.2f}%")
        print(f"   ELK Stack: {'✅ Habilitado' if report['elk_stack']['enabled'] else '❌ Desabilitado'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return False

def main():
    """Função principal."""
    print("=" * 60)
    print("🚀 SISTEMA DE LOGGING ESTRUTURADO - INICIALIZAÇÃO")
    print("=" * 60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Versão: 3.1.0")
    print("=" * 60)
    
    # Verificar dependências
    print("\n1️⃣ Verificando dependências...")
    if not check_dependencies():
        print("❌ Falha na verificação de dependências")
        sys.exit(1)
    
    # Inicializar sistema
    print("\n2️⃣ Inicializando sistema...")
    if not initialize_logging_system():
        print("❌ Falha na inicialização do sistema")
        sys.exit(1)
    
    # Testar funcionalidades
    print("\n3️⃣ Testando funcionalidades...")
    if not test_logging_functionality():
        print("❌ Falha nos testes de funcionalidade")
        sys.exit(1)
    
    # Testar rotação
    print("\n4️⃣ Testando rotação de logs...")
    if not test_log_rotation():
        print("❌ Falha nos testes de rotação")
        sys.exit(1)
    
    # Testar configuração ELK
    print("\n5️⃣ Testando configuração ELK...")
    if not test_elk_configuration():
        print("❌ Falha nos testes de configuração ELK")
        sys.exit(1)
    
    # Criar logs de exemplo
    print("\n6️⃣ Criando logs de exemplo...")
    if not create_sample_logs():
        print("❌ Falha na criação de logs de exemplo")
        sys.exit(1)
    
    # Gerar relatório
    print("\n7️⃣ Gerando relatório...")
    if not generate_report():
        print("❌ Falha na geração do relatório")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ SISTEMA DE LOGGING ESTRUTURADO INICIALIZADO COM SUCESSO!")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. Configure as variáveis de ambiente para ELK Stack")
    print("   2. Execute: docker-compose -f config/elk_stack/docker-compose.yml up")
    print("   3. Acesse Kibana em: http://localhost:5601")
    print("   4. Importe os dashboards de: config/elk_stack/kibana_dashboards.json")
    print("\n📚 DOCUMENTAÇÃO:")
    print("   - Logs: logs/")
    print("   - Configuração ELK: config/elk_stack/")
    print("   - Relatório: logs/logging_system_report.json")
    print("=" * 60)

if __name__ == "__main__":
    main() 