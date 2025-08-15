from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Exemplo de Uso - Sistema de Versionamento de Configurações

Este script demonstra o uso completo do sistema de versionamento
de configurações do Omni Keywords Finder, incluindo:
- Criação de configurações
- Versionamento e rollback
- Comparação de versões
- Aprovação de mudanças
- Exportação e importação
- Backup e restauração

Autor: Sistema Omni Keywords Finder
Data: 2024-12-19
Versão: 1.0.0
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Importa o sistema de versionamento
from shared.config_versioning import (
    ConfigVersioningSystem,
    ConfigStatus,
    ConfigType,
    create_config_version,
    get_active_config,
    activate_config_version,
    rollback_config,
    export_config,
    import_config
)


def print_separator(title: str):
    """Imprime separador com título"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_config_info(version, title: str = "Configuração"):
    """Imprime informações de uma configuração"""
    print(f"\n{title}:")
    print(f"  ID: {version.id}")
    print(f"  Nome: {version.config_name}")
    print(f"  Tipo: {version.config_type.value}")
    print(f"  Status: {version.status.value}")
    print(f"  Criado por: {version.created_by}")
    print(f"  Criado em: {version.created_at}")
    if version.description:
        print(f"  Descrição: {version.description}")
    if version.tags:
        print(f"  Tags: {', '.join(version.tags)}")


def main():
    """Função principal do exemplo"""
    print("🚀 Sistema de Versionamento de Configurações - Exemplo de Uso")
    print("=" * 70)
    
    # Configuração temporária para o exemplo
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    backup_dir = Path(tempfile.mkdtemp())
    
    try:
        # Inicializa o sistema
        print_separator("1. INICIALIZAÇÃO DO SISTEMA")
        system = ConfigVersioningSystem(db_path=db_path, backup_dir=str(backup_dir))
        print(f"✅ Sistema inicializado com sucesso")
        print(f"   Banco de dados: {db_path}")
        print(f"   Diretório de backup: {backup_dir}")
        
        # Configurações de exemplo
        print_separator("2. CONFIGURAÇÕES DE EXEMPLO")
        
        # Configuração inicial do banco de dados
        db_config_v1 = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "omni_keywords_dev",
                "pool_size": 5,
                "timeout": 30
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "ttl": 3600
            }
        }
        
        # Configuração atualizada
        db_config_v2 = {
            "database": {
                "host": "prod-db.example.com",
                "port": 5432,
                "name": "omni_keywords_prod",
                "pool_size": 20,  # Aumentado
                "timeout": 60     # Aumentado
            },
            "redis": {
                "host": "prod-redis.example.com",  # Mudado
                "port": 6379,
                "db": 0,
                "ttl": 7200  # Aumentado
            },
            "monitoring": {  # Nova seção
                "enabled": True,
                "interval": 30,
                "alerts": ["email", "slack"]
            }
        }
        
        # Configuração com problemas (para rollback)
        db_config_v3 = {
            "database": {
                "host": "wrong-host.example.com",  # Host incorreto
                "port": 5432,
                "name": "omni_keywords_prod",
                "pool_size": 50,  # Muito alto
                "timeout": 120    # Muito alto
            },
            "redis": {
                "host": "prod-redis.example.com",
                "port": 6379,
                "db": 0,
                "ttl": 7200
            },
            "monitoring": {
                "enabled": True,
                "interval": 30,
                "alerts": ["email", "slack"]
            }
        }
        
        print("📋 Configurações de exemplo criadas:")
        print("   - db_config_v1: Configuração inicial (desenvolvimento)")
        print("   - db_config_v2: Configuração atualizada (produção)")
        print("   - db_config_v3: Configuração com problemas (para rollback)")
        
        # Criação de versões
        print_separator("3. CRIAÇÃO DE VERSÕES")
        
        # Versão 1 - Configuração inicial
        version1 = system.create_version(
            config_name="database_config",
            config_type=ConfigType.SYSTEM,
            content=db_config_v1,
            created_by="dev_team",
            description="Configuração inicial para desenvolvimento",
            tags=["development", "initial", "database"]
        )
        print_config_info(version1, "Versão 1 - Desenvolvimento")
        
        # Versão 2 - Configuração atualizada
        version2 = system.create_version(
            config_name="database_config",
            config_type=ConfigType.SYSTEM,
            content=db_config_v2,
            created_by="devops_team",
            description="Configuração para produção com monitoramento",
            tags=["production", "monitoring", "database"]
        )
        print_config_info(version2, "Versão 2 - Produção")
        
        # Versão 3 - Configuração com problemas
        version3 = system.create_version(
            config_name="database_config",
            config_type=ConfigType.SYSTEM,
            content=db_config_v3,
            created_by="devops_team",
            description="Configuração com problemas (host incorreto)",
            tags=["production", "problematic", "database"]
        )
        print_config_info(version3, "Versão 3 - Com Problemas")
        
        # Ativação de versões
        print_separator("4. ATIVAÇÃO DE VERSÕES")
        
        # Ativa versão 1 (desenvolvimento)
        print("🔄 Ativando versão 1 (desenvolvimento)...")
        success = system.activate_version(version1.id, "admin")
        if success:
            print("✅ Versão 1 ativada com sucesso")
        else:
            print("❌ Falha ao ativar versão 1")
        
        # Verifica configuração ativa
        active_config = system.get_active_version("database_config")
        print_config_info(active_config, "Configuração Ativa Atual")
        
        # Ativa versão 2 (produção)
        print("\n🔄 Ativando versão 2 (produção)...")
        success = system.activate_version(version2.id, "admin")
        if success:
            print("✅ Versão 2 ativada com sucesso")
        else:
            print("❌ Falha ao ativar versão 2")
        
        # Verifica configuração ativa
        active_config = system.get_active_version("database_config")
        print_config_info(active_config, "Configuração Ativa Atual")
        
        # Comparação de versões
        print_separator("5. COMPARAÇÃO DE VERSÕES")
        
        print("🔍 Comparando versão 1 com versão 2...")
        comparison = system.compare_versions(version1.id, version2.id)
        
        print(f"📊 Resumo das mudanças:")
        print(f"   - Chaves adicionadas: {comparison['summary']['added_keys']}")
        print(f"   - Chaves removidas: {comparison['summary']['removed_keys']}")
        print(f"   - Chaves modificadas: {comparison['summary']['modified_keys']}")
        print(f"   - Chaves inalteradas: {comparison['summary']['unchanged_keys']}")
        
        print(f"\n📝 Mudanças detalhadas:")
        changes = comparison['changes']
        if changes['added']:
            print(f"   ➕ Adicionadas: {', '.join(changes['added'])}")
        if changes['modified']:
            print(f"   🔄 Modificadas: {', '.join(changes['modified'])}")
        if changes['removed']:
            print(f"   ➖ Removidas: {', '.join(changes['removed'])}")
        
        # Simulação de problema e rollback
        print_separator("6. SIMULAÇÃO DE PROBLEMA E ROLLBACK")
        
        # Ativa versão problemática
        print("⚠️  Ativando versão problemática (versão 3)...")
        system.activate_version(version3.id, "admin")
        
        print("🚨 Problema detectado: Host incorreto e configurações inadequadas!")
        print("   - Host: wrong-host.example.com (incorreto)")
        print("   - Pool size: 50 (muito alto)")
        print("   - Timeout: 120s (muito alto)")
        
        # Faz rollback para versão estável
        print("\n🔄 Executando rollback para versão estável (versão 2)...")
        success = system.rollback_to_version("database_config", version2.id, "admin")
        
        if success:
            print("✅ Rollback executado com sucesso!")
            
            # Verifica configuração após rollback
            active_config = system.get_active_version("database_config")
            print_config_info(active_config, "Configuração Após Rollback")
            
            print(f"📋 Configuração restaurada:")
            print(f"   - Host: {active_config.content['database']['host']}")
            print(f"   - Pool size: {active_config.content['database']['pool_size']}")
            print(f"   - Timeout: {active_config.content['database']['timeout']}")
        else:
            print("❌ Falha no rollback")
        
        # Sistema de aprovação
        print_separator("7. SISTEMA DE APROVAÇÃO")
        
        # Cria nova versão para aprovação
        new_config = {
            "database": {
                "host": "new-prod-db.example.com",
                "port": 5432,
                "name": "omni_keywords_prod_v2",
                "pool_size": 25,
                "timeout": 45
            },
            "redis": {
                "host": "new-prod-redis.example.com",
                "port": 6379,
                "db": 0,
                "ttl": 7200
            },
            "monitoring": {
                "enabled": True,
                "interval": 15,
                "alerts": ["email", "slack", "pagerduty"]
            },
            "security": {  # Nova seção
                "ssl_enabled": True,
                "encryption": "AES-256",
                "audit_logging": True
            }
        }
        
        version_pending = system.create_version(
            config_name="database_config",
            config_type=ConfigType.SYSTEM,
            content=new_config,
            created_by="security_team",
            description="Configuração com melhorias de segurança",
            tags=["production", "security", "database"]
        )
        
        print_config_info(version_pending, "Nova Versão - Aguardando Aprovação")
        
        # Marca para aprovação
        system.update_status(version_pending.id, ConfigStatus.PENDING_APPROVAL)
        
        # Simula processo de aprovação
        print("\n📋 Processo de aprovação:")
        print("   1. Versão criada e marcada para aprovação")
        print("   2. Revisão técnica realizada")
        print("   3. Testes de segurança aprovados")
        print("   4. Aprovação final concedida")
        
        # Aprova versão
        success = system.approve_version(
            version_pending.id,
            approver="senior_architect",
            approved=True,
            comments="Configuração revisada e aprovada. Melhorias de segurança implementadas."
        )
        
        if success:
            print("✅ Versão aprovada com sucesso!")
            
            # Ativa versão aprovada
            system.activate_version(version_pending.id, "admin")
            active_config = system.get_active_version("database_config")
            print_config_info(active_config, "Configuração Ativa - Pós Aprovação")
        else:
            print("❌ Falha na aprovação")
        
        # Exportação e importação
        print_separator("8. EXPORTAÇÃO E IMPORTAÇÃO")
        
        # Exporta configuração ativa
        print("📤 Exportando configuração ativa...")
        exported_json = system.export_configuration(active_config.id, "json")
        exported_yaml = system.export_configuration(active_config.id, "yaml")
        
        print(f"✅ Exportação JSON: {len(exported_json)} caracteres")
        print(f"✅ Exportação YAML: {len(exported_yaml)} caracteres")
        
        # Salva arquivo de exemplo
        export_file = backup_dir / "config_export_example.json"
        with open(export_file, 'w') as f:
            f.write(exported_json)
        print(f"💾 Arquivo salvo: {export_file}")
        
        # Importa configuração
        print("\n📥 Importando configuração...")
        imported_version = system.import_configuration(
            exported_json,
            "json",
            "import_user"
        )
        
        print_config_info(imported_version, "Versão Importada")
        
        # Backup e restauração
        print_separator("9. BACKUP E RESTAURAÇÃO")
        
        # Cria backup
        print("💾 Criando backup do sistema...")
        backup_file = system.create_backup()
        print(f"✅ Backup criado: {backup_file}")
        
        # Verifica arquivo de backup
        backup_size = Path(backup_file).stat().st_size
        print(f"📊 Tamanho do backup: {backup_size:,} bytes")
        
        # Simula restauração (criando novo sistema)
        print("\n🔄 Simulando restauração...")
        new_system = ConfigVersioningSystem(
            db_path=db_path + "_restored",
            backup_dir=str(backup_dir)
        )
        
        restored_count = new_system.restore_from_backup(backup_file, "restore_user")
        print(f"✅ {restored_count} versões restauradas")
        
        # Verifica restauração
        restored_versions = new_system.get_version_history("database_config")
        print(f"📋 Versões restauradas: {len(restored_versions)}")
        
        # Estatísticas do sistema
        print_separator("10. ESTATÍSTICAS DO SISTEMA")
        
        stats = system.get_statistics()
        
        print("📊 Estatísticas gerais:")
        print(f"   - Total de versões: {stats['total_versions']}")
        print(f"   - Configurações únicas: {stats['unique_configurations']}")
        print(f"   - Pendentes de aprovação: {stats['pending_approvals']}")
        print(f"   - Última atividade: {stats['last_activity']}")
        
        print("\n📈 Distribuição por status:")
        for status, count in stats['status_distribution'].items():
            print(f"   - {status}: {count}")
        
        print("\n🏷️  Distribuição por tipo:")
        for config_type, count in stats['type_distribution'].items():
            print(f"   - {config_type}: {count}")
        
        # Histórico de versões
        print_separator("11. HISTÓRICO DE VERSÕES")
        
        history = system.get_version_history("database_config")
        print(f"📋 Histórico completo ({len(history)} versões):")
        
        for index, version in enumerate(history, 1):
            print(f"\n   {index}. Versão {version.version}")
            print(f"      Status: {version.status.value}")
            print(f"      Criado por: {version.created_by}")
            print(f"      Criado em: {version.created_at}")
            if version.description:
                print(f"      Descrição: {version.description}")
            if version.tags:
                print(f"      Tags: {', '.join(version.tags)}")
        
        # Demonstração das funções de conveniência
        print_separator("12. FUNÇÕES DE CONVENIÊNCIA")
        
        print("🔧 Usando funções de conveniência...")
        
        # Obtém configuração ativa
        active_config_dict = get_active_config("database_config")
        if active_config_dict:
            print(f"✅ Configuração ativa obtida: {len(active_config_dict)} seções")
        
        # Cria nova configuração usando função de conveniência
        simple_config = {
            "api": {
                "rate_limit": 1000,
                "timeout": 30
            }
        }
        
        simple_version = create_config_version(
            config_name="api_config",
            config_type=ConfigType.SYSTEM,
            content=simple_config,
            created_by="example_user",
            description="Configuração simples de API"
        )
        
        print(f"✅ Nova configuração criada: {simple_version.id}")
        
        # Ativa usando função de conveniência
        success = activate_config_version(simple_version.id, "admin")
        if success:
            print("✅ Configuração ativada com sucesso")
        
        # Exporta usando função de conveniência
        exported = export_config(simple_version.id, "json")
        print(f"✅ Configuração exportada: {len(exported)} caracteres")
        
        print_separator("13. CONCLUSÃO")
        
        print("🎉 Exemplo concluído com sucesso!")
        print("\n📋 Resumo do que foi demonstrado:")
        print("   ✅ Criação e versionamento de configurações")
        print("   ✅ Ativação e desativação de versões")
        print("   ✅ Comparação detalhada entre versões")
        print("   ✅ Sistema de aprovação e workflow")
        print("   ✅ Rollback para versões anteriores")
        print("   ✅ Exportação em múltiplos formatos")
        print("   ✅ Importação de configurações")
        print("   ✅ Backup e restauração automática")
        print("   ✅ Estatísticas e histórico completo")
        print("   ✅ Funções de conveniência")
        
        print("\n🚀 O sistema está pronto para uso em produção!")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpeza
        print_separator("LIMPEZA")
        print("🧹 Limpando arquivos temporários...")
        
        try:
            # Remove banco de dados
            Path(db_path).unlink()
            Path(db_path + "_restored").unlink()
            
            # Remove diretório de backup
            shutil.rmtree(backup_dir)
            
            print("✅ Limpeza concluída")
        except Exception as e:
            print(f"⚠️  Erro na limpeza: {e}")


if __name__ == "__main__":
    main() 