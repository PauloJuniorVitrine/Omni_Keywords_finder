from typing import Dict, List, Optional, Any
"""
Exemplo Prático - Sistema de Backup Inteligente

Demonstração completa do uso do sistema de backup inteligente
com todas as funcionalidades avançadas.

Autor: Sistema de Exemplos
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: EXAMPLE_BACKUP_INTELIGENTE_001
"""

import os
import tempfile
import shutil
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# Importar sistema de backup inteligente
from infrastructure.backup.inteligente.backup_manager import (
    BackupInteligenteManager,
    BackupType,
    BackupStatus
)
from infrastructure.backup.inteligente.restore_manager import (
    RestoreInteligenteManager,
    RestoreType,
    RestoreStatus
)

class BackupInteligenteExample:
    """Exemplo prático do sistema de backup inteligente"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_manager = None
        self.restore_manager = None
        self.example_data = {}
        
    def setup_example_environment(self):
        """Configura ambiente de exemplo"""
        print("🔧 Configurando ambiente de exemplo...")
        
        # Criar estrutura de dados de exemplo
        self.example_data = {
            'backend': {
                'app.py': 'print("Hello from Omni Keywords Finder")',
                'config.py': 'DEBUG = True\nAPI_KEY = "example_key"',
                'models.py': 'class User:\n    def __init__(self):\n        pass',
                'database': {
                    'users.db': 'SQLite database content',
                    'logs.db': 'Logs database content'
                }
            },
            'frontend': {
                'index.html': '<html><body><h1>Omni Keywords Finder</h1></body></html>',
                'style.css': 'body { font-family: Arial; }',
                'script.js': 'console.log("Frontend loaded");'
            },
            'data': {
                'keywords.json': json.dumps({
                    'keywords': ['python', 'javascript', 'machine learning'],
                    'count': 3,
                    'last_updated': datetime.now().isoformat()
                }, indent=2),
                'analytics.csv': 'date,keywords,clicks\n2024-12-19,100,50\n2024-12-20,150,75'
            },
            'logs': {
                'app.log': '2024-12-19 10:00:00 INFO: Application started\n2024-12-19 10:01:00 INFO: Backup system initialized',
                'error.log': '2024-12-19 09:59:00 ERROR: Connection timeout\n2024-12-19 10:00:30 ERROR: Database connection failed'
            },
            'docs': {
                'README.md': '# Omni Keywords Finder\n\nSistema avançado de busca de keywords.',
                'API.md': '# API Documentation\n\n## Endpoints\n- GET /keywords\n- POST /search'
            }
        }
        
        # Criar arquivos de exemplo
        self._create_example_files()
        
        # Configurar managers
        self._setup_managers()
        
        print("✅ Ambiente configurado com sucesso!")
    
    def _create_example_files(self):
        """Cria arquivos de exemplo"""
        for category, items in self.example_data.items():
            category_path = os.path.join(self.temp_dir, category)
            os.makedirs(category_path, exist_ok=True)
            
            for item_name, content in items.items():
                if isinstance(content, dict):
                    # Subdiretório
                    subdir_path = os.path.join(category_path, item_name)
                    os.makedirs(subdir_path, exist_ok=True)
                    for subitem_name, subcontent in content.items():
                        subitem_path = os.path.join(subdir_path, subitem_name)
                        with open(subitem_path, 'w') as f:
                            f.write(subcontent)
                else:
                    # Arquivo
                    item_path = os.path.join(category_path, item_name)
                    with open(item_path, 'w') as f:
                        f.write(content)
    
    def _setup_managers(self):
        """Configura managers de backup e restore"""
        # Configurar diretório de backup
        backup_dir = os.path.join(self.temp_dir, "backups_inteligentes")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Mock das configurações para usar arquivos de exemplo
        with open(os.path.join(self.temp_dir, 'config.json'), 'w') as f:
            json.dump({
                'critical_files': [
                    os.path.join(self.temp_dir, 'backend'),
                    os.path.join(self.temp_dir, 'frontend'),
                    os.path.join(self.temp_dir, 'data'),
                    os.path.join(self.temp_dir, 'logs'),
                    os.path.join(self.temp_dir, 'docs')
                ]
            }, f)
        
        # Inicializar managers
        self.backup_manager = BackupInteligenteManager()
        self.backup_manager.backup_dir = Path(backup_dir)
        
        # Sobrescrever método para usar arquivos de exemplo
        def get_files_to_backup():
            files = []
            for root, dirs, filenames in os.walk(self.temp_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if not self.backup_manager._should_exclude(file_path):
                        files.append(file_path)
            return files
        
        self.backup_manager._get_files_to_backup = get_files_to_backup
        
        self.restore_manager = RestoreInteligenteManager()
        self.restore_manager.backup_dir = Path(backup_dir)
    
    def demonstrate_full_backup(self):
        """Demonstra backup completo"""
        print("\n🔄 Demonstração: Backup Completo")
        print("=" * 50)
        
        start_time = time.time()
        
        # Criar backup completo
        backup = self.backup_manager.create_backup(BackupType.FULL)
        
        if backup and backup.status == BackupStatus.COMPLETED:
            duration = time.time() - start_time
            
            print(f"✅ Backup completo criado com sucesso!")
            print(f"📊 Estatísticas:")
            print(f"   - ID: {backup.backup_id}")
            print(f"   - Tipo: {backup.backup_type.value}")
            print(f"   - Arquivos: {backup.file_count}")
            print(f"   - Tamanho original: {backup.size_bytes / 1024:.1f} KB")
            print(f"   - Tamanho comprimido: {backup.compressed_size_bytes / 1024:.1f} KB")
            print(f"   - Taxa de compressão: {backup.compression_ratio:.1f}%")
            print(f"   - Duração: {duration:.2f} segundos")
            print(f"   - Status: {backup.status.value}")
            
            return backup
        else:
            print("❌ Falha na criação do backup completo")
            if backup:
                print(f"   Erro: {backup.error_message}")
            return None
    
    def demonstrate_incremental_backup(self):
        """Demonstra backup incremental"""
        print("\n🔄 Demonstração: Backup Incremental")
        print("=" * 50)
        
        # Modificar alguns arquivos para simular mudanças
        print("📝 Simulando mudanças nos arquivos...")
        
        # Modificar arquivo existente
        app_py_path = os.path.join(self.temp_dir, 'backend', 'app.py')
        with open(app_py_path, 'a') as f:
            f.write('\n# New feature added\nprint("New functionality")')
        
        # Adicionar novo arquivo
        new_file_path = os.path.join(self.temp_dir, 'backend', 'new_module.py')
        with open(new_file_path, 'w') as f:
            f.write('def new_function():\n    return "New function"')
        
        # Deletar arquivo
        old_file_path = os.path.join(self.temp_dir, 'docs', 'old_doc.txt')
        with open(old_file_path, 'w') as f:
            f.write('This file will be deleted')
        os.remove(old_file_path)
        
        start_time = time.time()
        
        # Criar backup incremental
        backup = self.backup_manager.create_backup(BackupType.INCREMENTAL)
        
        if backup and backup.status == BackupStatus.COMPLETED:
            duration = time.time() - start_time
            
            print(f"✅ Backup incremental criado com sucesso!")
            print(f"📊 Estatísticas:")
            print(f"   - ID: {backup.backup_id}")
            print(f"   - Tipo: {backup.backup_type.value}")
            print(f"   - Arquivos: {backup.file_count}")
            print(f"   - Tamanho original: {backup.size_bytes / 1024:.1f} KB")
            print(f"   - Tamanho comprimido: {backup.compressed_size_bytes / 1024:.1f} KB")
            print(f"   - Taxa de compressão: {backup.compression_ratio:.1f}%")
            print(f"   - Duração: {duration:.2f} segundos")
            
            return backup
        else:
            print("❌ Falha na criação do backup incremental")
            if backup:
                print(f"   Erro: {backup.error_message}")
            return None
    
    def demonstrate_backup_validation(self, backup):
        """Demonstra validação de backup"""
        print("\n🔍 Demonstração: Validação de Backup")
        print("=" * 50)
        
        if not backup:
            print("❌ Nenhum backup para validar")
            return False
        
        print(f"🔍 Validando backup: {backup.backup_id}")
        
        is_valid = self.backup_manager.validate_backup(backup.backup_id)
        
        if is_valid:
            print("✅ Backup validado com sucesso!")
            print("   - Integridade verificada")
            print("   - Checksum confirmado")
            print("   - Arquivo ZIP válido")
            return True
        else:
            print("❌ Falha na validação do backup")
            return False
    
    def demonstrate_backup_listing(self):
        """Demonstra listagem de backups"""
        print("\n📋 Demonstração: Listagem de Backups")
        print("=" * 50)
        
        backups = self.backup_manager.list_backups()
        
        if backups:
            print(f"📊 Total de backups: {len(backups)}")
            print("\n📋 Lista de backups:")
            for index, backup in enumerate(backups, 1):
                print(f"   {index}. {backup['id']}")
                print(f"      Tipo: {backup['type']}")
                print(f"      Status: {backup['status']}")
                print(f"      Tamanho: {backup['size_mb']} MB")
                print(f"      Arquivos: {backup['file_count']}")
                print(f"      Compressão: {backup['compression_ratio']}")
                print(f"      Criptografado: {'Sim' if backup['encrypted'] else 'Não'}")
                print()
        else:
            print("📭 Nenhum backup encontrado")
    
    def demonstrate_backup_statistics(self):
        """Demonstra estatísticas de backup"""
        print("\n📈 Demonstração: Estatísticas de Backup")
        print("=" * 50)
        
        stats = self.backup_manager.get_backup_stats()
        
        if stats:
            print("📊 Estatísticas gerais:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
        else:
            print("📭 Nenhuma estatística disponível")
    
    def demonstrate_full_restore(self, backup):
        """Demonstra restore completo"""
        print("\n🔄 Demonstração: Restore Completo")
        print("=" * 50)
        
        if not backup:
            print("❌ Nenhum backup para restaurar")
            return None
        
        # Criar diretório de destino para restore
        restore_dir = os.path.join(self.temp_dir, "restore_destination")
        os.makedirs(restore_dir, exist_ok=True)
        
        print(f"🔄 Restaurando backup: {backup.backup_id}")
        print(f"📁 Destino: {restore_dir}")
        
        start_time = time.time()
        
        # Executar restore
        restore = self.restore_manager.restore_backup(
            backup.backup_id, restore_dir, RestoreType.FULL
        )
        
        if restore and restore.status == RestoreStatus.COMPLETED:
            duration = time.time() - start_time
            
            print(f"✅ Restore concluído com sucesso!")
            print(f"📊 Estatísticas:")
            print(f"   - ID: {restore.restore_id}")
            print(f"   - Tipo: {restore.restore_type.value}")
            print(f"   - Arquivos restaurados: {restore.files_restored}")
            print(f"   - Tamanho total: {restore.total_size_bytes / 1024:.1f} KB")
            print(f"   - Duração: {restore.duration_seconds:.2f} segundos")
            print(f"   - Status: {restore.status.value}")
            
            # Verificar arquivos restaurados
            self._verify_restored_files(restore_dir)
            
            return restore
        else:
            print("❌ Falha no restore")
            if restore:
                print(f"   Erro: {restore.error_message}")
            return None
    
    def demonstrate_selective_restore(self, backup):
        """Demonstra restore seletivo"""
        print("\n🔄 Demonstração: Restore Seletivo")
        print("=" * 50)
        
        if not backup:
            print("❌ Nenhum backup para restaurar")
            return None
        
        # Criar diretório de destino para restore seletivo
        selective_restore_dir = os.path.join(self.temp_dir, "selective_restore")
        os.makedirs(selective_restore_dir, exist_ok=True)
        
        print(f"🔄 Restaurando apenas arquivos do backend...")
        
        start_time = time.time()
        
        # Executar restore seletivo
        restore = self.restore_manager.restore_backup(
            backup.backup_id, selective_restore_dir, 
            RestoreType.SELECTIVE, ["backend"]
        )
        
        if restore and restore.status == RestoreStatus.COMPLETED:
            duration = time.time() - start_time
            
            print(f"✅ Restore seletivo concluído!")
            print(f"📊 Estatísticas:")
            print(f"   - Arquivos restaurados: {restore.files_restored}")
            print(f"   - Duração: {duration:.2f} segundos")
            
            # Verificar se apenas arquivos do backend foram restaurados
            backend_files = []
            for root, dirs, files in os.walk(selective_restore_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), selective_restore_dir)
                    backend_files.append(rel_path)
            
            print(f"📁 Arquivos restaurados:")
            for file in backend_files:
                print(f"   - {file}")
            
            return restore
        else:
            print("❌ Falha no restore seletivo")
            return None
    
    def _verify_restored_files(self, restore_dir):
        """Verifica arquivos restaurados"""
        print(f"🔍 Verificando arquivos restaurados em: {restore_dir}")
        
        expected_files = [
            'backend/app.py',
            'backend/config.py',
            'backend/models.py',
            'backend/database/users.db',
            'backend/database/logs.db',
            'frontend/index.html',
            'frontend/style.css',
            'frontend/script.js',
            'data/keywords.json',
            'data/analytics.csv',
            'logs/app.log',
            'logs/error.log',
            'docs/README.md',
            'docs/API.md'
        ]
        
        restored_files = []
        for root, dirs, files in os.walk(restore_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), restore_dir)
                restored_files.append(rel_path)
        
        print(f"📊 Arquivos esperados: {len(expected_files)}")
        print(f"📊 Arquivos restaurados: {len(restored_files)}")
        
        missing_files = set(expected_files) - set(restored_files)
        if missing_files:
            print(f"⚠️ Arquivos não encontrados: {len(missing_files)}")
            for file in missing_files:
                print(f"   - {file}")
        else:
            print("✅ Todos os arquivos foram restaurados corretamente!")
    
    def demonstrate_restore_statistics(self):
        """Demonstra estatísticas de restore"""
        print("\n📈 Demonstração: Estatísticas de Restore")
        print("=" * 50)
        
        stats = self.restore_manager.get_restore_stats()
        
        if stats:
            print("📊 Estatísticas de restore:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
        else:
            print("📭 Nenhuma estatística de restore disponível")
    
    def demonstrate_cleanup(self):
        """Demonstra limpeza de backups antigos"""
        print("\n🧹 Demonstração: Limpeza de Backups Antigos")
        print("=" * 50)
        
        print("🧹 Executando limpeza de backups antigos...")
        
        # Simular backups antigos modificando timestamps
        for backup in self.backup_manager.backup_history:
            # Tornar backup antigo (30 dias atrás)
            old_timestamp = (datetime.now() - timedelta(days=30)).isoformat()
            backup.timestamp = old_timestamp
        
        # Executar limpeza
        self.backup_manager.cleanup_old_backups()
        
        print("✅ Limpeza concluída!")
        
        # Mostrar backups restantes
        remaining_backups = self.backup_manager.list_backups()
        print(f"📊 Backups restantes: {len(remaining_backups)}")
    
    def run_complete_demonstration(self):
        """Executa demonstração completa"""
        print("🚀 INICIANDO DEMONSTRAÇÃO COMPLETA DO SISTEMA DE BACKUP INTELIGENTE")
        print("=" * 80)
        
        try:
            # Configurar ambiente
            self.setup_example_environment()
            
            # Demonstração 1: Backup Completo
            full_backup = self.demonstrate_full_backup()
            
            # Demonstração 2: Validação
            if full_backup:
                self.demonstrate_backup_validation(full_backup)
            
            # Demonstração 3: Backup Incremental
            incremental_backup = self.demonstrate_incremental_backup()
            
            # Demonstração 4: Listagem
            self.demonstrate_backup_listing()
            
            # Demonstração 5: Estatísticas
            self.demonstrate_backup_statistics()
            
            # Demonstração 6: Restore Completo
            if full_backup:
                full_restore = self.demonstrate_full_restore(full_backup)
            
            # Demonstração 7: Restore Seletivo
            if full_backup:
                selective_restore = self.demonstrate_selective_restore(full_backup)
            
            # Demonstração 8: Estatísticas de Restore
            self.demonstrate_restore_statistics()
            
            # Demonstração 9: Limpeza
            self.demonstrate_cleanup()
            
            print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 80)
            print("✅ Todas as funcionalidades foram demonstradas:")
            print("   - Backup completo com compressão e criptografia")
            print("   - Backup incremental com detecção de mudanças")
            print("   - Validação de integridade de backups")
            print("   - Restore completo e seletivo")
            print("   - Estatísticas e relatórios")
            print("   - Limpeza automática de backups antigos")
            
        except Exception as e:
            print(f"❌ Erro durante a demonstração: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Limpeza final
            print(f"\n🧹 Limpando arquivos temporários...")
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print("✅ Limpeza concluída!")

def main():
    """Função principal"""
    print("🔧 Sistema de Backup Inteligente - Exemplo Prático")
    print("=" * 60)
    
    # Criar e executar demonstração
    example = BackupInteligenteExample()
    example.run_complete_demonstration()

if __name__ == "__main__":
    main()




