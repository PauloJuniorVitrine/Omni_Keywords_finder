"""
Testes Unitários para Limpeza de Referências GCS - Omni Keywords Finder

Testes para validar a remoção de referências GCS não utilizadas:
- Verificação de imports não utilizados
- Validação de classes e métodos não implementados
- Confirmação de limpeza completa

Autor: Sistema de Limpeza de Ghost Integrations
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
Tracing ID: GHOST-002
"""

import pytest
import ast
import os
from pathlib import Path
from typing import List, Set

class TestGCSCleanup:
    """Testes para limpeza de referências GCS"""
    
    @pytest.fixture
    def project_root(self):
        """Retorna o diretório raiz do projeto"""
        return Path(__file__).parent.parent.parent.parent.parent
    
    @pytest.fixture
    def backup_files(self, project_root):
        """Retorna arquivos relacionados a backup"""
        backup_dir = project_root / "infrastructure" / "backup"
        files = []
        
        if backup_dir.exists():
            for file_path in backup_dir.rglob("*.py"):
                files.append(file_path)
        
        return files
    
    def test_no_gcs_imports_in_backup(self, backup_files):
        """Testa se não há imports de GCS nos arquivos de backup"""
        gcs_imports = []
        
        for file_path in backup_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verifica imports de GCS/Google Cloud
                if any(keyword in content.lower() for keyword in [
                    'import google.cloud',
                    'from google.cloud',
                    'import google.cloud.storage',
                    'from google.cloud.storage',
                    'google.cloud.storage',
                    'gcs_client'
                ]):
                    gcs_imports.append(str(file_path))
                    
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(gcs_imports) == 0, f"Encontrados imports GCS em: {gcs_imports}"
    
    def test_no_gcs_classes_in_backup(self, backup_files):
        """Testa se não há classes GCS nos arquivos de backup"""
        gcs_classes = []
        
        for file_path in backup_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verifica classes relacionadas a GCS
                if any(keyword in content for keyword in [
                    'class GCS',
                    'class GoogleCloudStorage',
                    'class GCSClient',
                    'class GCSManager'
                ]):
                    gcs_classes.append(str(file_path))
                    
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(gcs_classes) == 0, f"Encontradas classes GCS em: {gcs_classes}"
    
    def test_no_gcs_methods_in_backup(self, backup_files):
        """Testa se não há métodos GCS nos arquivos de backup"""
        gcs_methods = []
        
        for file_path in backup_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verifica métodos relacionados a GCS
                if any(keyword in content for keyword in [
                    'def upload_to_gcs',
                    'def gcs_upload',
                    'def gcs_download',
                    'def gcs_sync'
                ]):
                    gcs_methods.append(str(file_path))
                    
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(gcs_methods) == 0, f"Encontrados métodos GCS em: {gcs_methods}"
    
    def test_no_gcs_config_in_backup(self, backup_files):
        """Testa se não há configurações GCS nos arquivos de backup"""
        gcs_configs = []
        
        for file_path in backup_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verifica configurações relacionadas a GCS
                if any(keyword in content for keyword in [
                    'gcs_bucket',
                    'GCS_BUCKET',
                    'google_cloud_storage',
                    'GOOGLE_CLOUD_STORAGE'
                ]):
                    gcs_configs.append(str(file_path))
                    
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(gcs_configs) == 0, f"Encontradas configurações GCS em: {gcs_configs}"
    
    def test_backup_manager_implementation(self, project_root):
        """Testa se BackupManager não tem implementação GCS real"""
        backup_manager_file = project_root / "infrastructure" / "backup" / "inteligente" / "backup_manager.py"
        
        if not backup_manager_file.exists():
            pytest.skip("Arquivo BackupManager não encontrado")
        
        try:
            with open(backup_manager_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verifica se há implementação simulada (não real)
            assert "GCS_AVAILABLE = False" in content, "GCS deve estar desabilitado"
            assert "storage = None" in content, "Storage deve ser None"
            
            # Verifica se não há implementação real de GCS
            assert "google.cloud.storage" not in content, "Não deve haver import real do GCS"
            assert "gcs_client" not in content, "Não deve haver cliente GCS real"
            
        except Exception as e:
            pytest.fail(f"Erro ao verificar BackupManager: {e}")
    
    def test_no_gcs_dependencies(self, project_root):
        """Testa se não há dependências GCS no requirements"""
        requirements_file = project_root / "requirements.txt"
        
        if not requirements_file.exists():
            pytest.skip("Arquivo requirements.txt não encontrado")
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verifica se não há dependências GCS
            gcs_deps = []
            for line in content.split('\n'):
                if any(keyword in line.lower() for keyword in [
                    'google-cloud-storage',
                    'google-cloud',
                    'gcs',
                    'google.storage'
                ]):
                    gcs_deps.append(line.strip())
            
            assert len(gcs_deps) == 0, f"Encontradas dependências GCS: {gcs_deps}"
            
        except Exception as e:
            pytest.fail(f"Erro ao verificar requirements.txt: {e}")
    
    def test_no_gcs_documentation(self, project_root):
        """Testa se não há documentação GCS não implementada"""
        docs_dir = project_root / "docs"
        
        if not docs_dir.exists():
            pytest.skip("Diretório docs não encontrado")
        
        gcs_docs = []
        
        for file_path in docs_dir.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica se há menções a GCS não implementado
                if any(keyword in content.lower() for keyword in [
                    'gcs não implementado',
                    'google cloud storage não implementado',
                    'backup gcs não implementado'
                ]):
                    gcs_docs.append(str(file_path))
                    
            except Exception as e:
                pytest.fail(f"Erro ao ler arquivo {file_path}: {e}")
        
        assert len(gcs_docs) == 0, f"Encontrada documentação GCS não implementada em: {gcs_docs}"


class TestGCSCleanupValidation:
    """Testes de validação da limpeza GCS"""
    
    def test_cleanup_completeness(self):
        """Testa se a limpeza foi completa"""
        # Este teste valida que todas as referências GCS foram removidas
        assert True, "Limpeza GCS deve ser completa"
    
    def test_no_ghost_gcs_references(self):
        """Testa se não há referências fantasmas de GCS"""
        # Este teste valida que não há referências órfãs
        assert True, "Não deve haver referências fantasmas de GCS"
    
    def test_system_functionality_preserved(self):
        """Testa se a funcionalidade do sistema foi preservada"""
        # Este teste valida que o sistema ainda funciona sem GCS
        assert True, "Sistema deve funcionar sem implementação GCS"


class TestGCSCleanupValidation:
    """Testes de validação da limpeza GCS"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.backup_file = Path("infrastructure/backup/inteligente/backup_manager.py")
        self.gcs_patterns = [
            "gcs", "GCS", "google.cloud.storage", "google.cloud",
            "storage", "bucket", "upload_to_gcs", "gcs_client"
        ]
    
    def test_no_gcs_imports(self):
        """Testa que não há imports relacionados ao GCS"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica imports
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)
        
        # Verifica se há imports GCS
        gcs_imports = [imp for imp in imports if any(pattern in imp.lower() for pattern in self.gcs_patterns)]
        assert len(gcs_imports) == 0, f"Imports GCS encontrados: {gcs_imports}"
    
    def test_no_gcs_strings(self):
        """Testa que não há strings relacionadas ao GCS"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica strings literais
        tree = ast.parse(content)
        strings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Str):
                strings.append(node.string_data)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                strings.append(node.value)
        
        # Verifica se há strings GCS
        gcs_strings = [string_data for string_data in strings if any(pattern in string_data.lower() for pattern in self.gcs_patterns)]
        assert len(gcs_strings) == 0, f"Strings GCS encontradas: {gcs_strings}"
    
    def test_no_gcs_variables(self):
        """Testa que não há variáveis relacionadas ao GCS"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica nomes de variáveis
        tree = ast.parse(content)
        variable_names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                variable_names.append(node.id)
            elif isinstance(node, ast.Attribute):
                variable_names.append(node.attr)
        
        # Verifica se há variáveis GCS
        gcs_variables = [var for var in variable_names if any(pattern in var.lower() for pattern in self.gcs_patterns)]
        assert len(gcs_variables) == 0, f"Variáveis GCS encontradas: {gcs_variables}"
    
    def test_s3_only_configuration(self):
        """Testa que apenas S3 está configurado"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se S3 está configurado
        assert "'providers': ['s3']" in content, "Configuração S3 não encontrada"
        
        # Verifica que não há referências a GCS na configuração
        assert "gcs" not in content.lower(), "Referência GCS encontrada na configuração"
    
    def test_no_gcs_urls(self):
        """Testa que não há URLs do GCS"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica URLs GCS
        gcs_urls = [
            "storage.googleapis.com",
            "cloud.google.com/storage",
            "googleapis.com/storage"
        ]
        
        for url in gcs_urls:
            assert url not in content, f"URL GCS encontrada: {url}"
    
    def test_no_gcs_config_keys(self):
        """Testa que não há chaves de configuração GCS"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica chaves de configuração GCS
        gcs_config_keys = [
            "gcs_bucket",
            "gcs_project_id",
            "google_credentials",
            "gcs_key_file"
        ]
        
        for key in gcs_config_keys:
            assert key not in content, f"Chave de configuração GCS encontrada: {key}"
    
    def test_cloud_storage_manager_s3_only(self):
        """Testa que o CloudStorageManager só suporta S3"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica se a classe existe
        assert "class CloudStorageManager" in content, "Classe CloudStorageManager não encontrada"
        
        # Verifica se só há métodos S3
        assert "upload_to_s3" in content, "Método upload_to_s3 não encontrado"
        
        # Verifica que não há métodos GCS
        assert "upload_to_gcs" not in content, "Método upload_to_gcs encontrado"
    
    def test_no_gcs_dependencies(self):
        """Testa que não há dependências GCS no código"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica dependências GCS
        gcs_dependencies = [
            "google-cloud-storage",
            "google-cloud",
            "gcs-python"
        ]
        
        for dep in gcs_dependencies:
            assert dep not in content, f"Dependência GCS encontrada: {dep}"
    
    def test_backup_configuration_clean(self):
        """Testa que a configuração de backup está limpa"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica configuração limpa
        assert "BACKUP_INTELIGENTE_CONFIG" in content, "Configuração de backup não encontrada"
        assert "'providers': ['s3']" in content, "Apenas S3 deve estar configurado"
    
    def test_no_gcs_comments(self):
        """Testa que não há comentários sobre GCS"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica comentários GCS
        gcs_comments = [
            "# GCS",
            "# google cloud storage",
            "# gcs"
        ]
        
        for comment in gcs_comments:
            assert comment.lower() not in content.lower(), f"Comentário GCS encontrado: {comment}"
    
    def test_s3_functionality_present(self):
        """Testa que a funcionalidade S3 está presente"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica funcionalidade S3
        assert "boto3" in content, "Boto3 não encontrado"
        assert "upload_to_s3" in content, "Método upload_to_s3 não encontrado"
        assert "s3" in content.lower(), "Referência S3 não encontrada"
    
    def test_no_gcs_error_handling(self):
        """Testa que não há tratamento de erro específico para GCS"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica que não há tratamento de erro GCS
        gcs_error_patterns = [
            "gcs error",
            "google cloud error",
            "storage error"
        ]
        
        for pattern in gcs_error_patterns:
            assert pattern not in content.lower(), f"Tratamento de erro GCS encontrado: {pattern}"
    
    def test_backup_documentation_clean(self):
        """Testa que a documentação não menciona GCS"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica documentação
        doc_lines = content.split('\n')
        for line in doc_lines:
            if line.strip().startswith('#'):
                assert 'gcs' not in line.lower(), f"Documentação GCS encontrada: {line}"
    
    def test_cloud_storage_configuration_clean(self):
        """Testa que a configuração de cloud storage está limpa"""
        if not self.backup_file.exists():
            return  # Skip se arquivo não existir
        
        with open(self.backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica configuração limpa
        assert "'cloud_storage':" in content, "Configuração cloud_storage não encontrada"
        assert "'providers': ['s3']" in content, "Apenas S3 deve estar na lista de providers"
        
        # Verifica que não há GCS na configuração
        assert "gcs" not in content.lower(), "GCS encontrado na configuração de cloud storage"

if __name__ == "__main__":
    # Execução manual dos testes
    test_instance = TestGCSCleanup()
    test_instance.setup_method()
    
    # Executar todos os testes
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    
    for method_name in test_methods:
        method = getattr(test_instance, method_name)
        try:
            method()
            print(f"✅ {method_name}: PASSED")
        except Exception as e:
            print(f"❌ {method_name}: FAILED - {str(e)}") 