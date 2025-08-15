from typing import Dict, List, Optional, Any
"""
🧪 Testes Unitários - Validador de Dependências
Tracing ID: INT-007-TEST
Data: 2024-12-19
Descrição: Testes para o script de validação de dependências
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from scripts.validate_dependencies import DependencyValidator

class TestDependencyValidator:
    """Testes para a classe DependencyValidator"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = DependencyValidator(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Testa inicialização do validador"""
        assert self.validator.project_root == Path(self.temp_dir)
        assert isinstance(self.validator.imports_found, dict)
        assert isinstance(self.validator.imports_used, dict)
        assert isinstance(self.validator.unused_imports, dict)
    
    def test_scan_python_files_empty_directory(self):
        """Testa escaneamento em diretório vazio"""
        files = self.validator.scan_python_files()
        assert files == []
    
    def test_scan_python_files_with_python_files(self):
        """Testa escaneamento com arquivos Python"""
        # Criar arquivos de teste
        test_file1 = Path(self.temp_dir) / "test1.py"
        test_file2 = Path(self.temp_dir) / "test2.py"
        test_file3 = Path(self.temp_dir) / "test3.txt"  # Não Python
        
        test_file1.write_text("# Test file 1")
        test_file2.write_text("# Test file 2")
        test_file3.write_text("# Not Python")
        
        files = self.validator.scan_python_files()
        assert len(files) == 2
        assert any("test1.py" in str(f) for f in files)
        assert any("test2.py" in str(f) for f in files)
        assert not any("test3.txt" in str(f) for f in files)
    
    def test_scan_python_files_ignores_directories(self):
        """Testa que diretórios especiais são ignorados"""
        # Criar diretórios que devem ser ignorados
        ignored_dirs = ["__pycache__", ".git", "venv", "node_modules"]
        for dir_name in ignored_dirs:
            (Path(self.temp_dir) / dir_name).mkdir()
            (Path(self.temp_dir) / dir_name / "test.py").write_text("# Test")
        
        # Criar arquivo Python válido
        (Path(self.temp_dir) / "valid.py").write_text("# Valid file")
        
        files = self.validator.scan_python_files()
        assert len(files) == 1
        assert "valid.py" in str(files[0])
    
    def test_extract_imports_simple_import(self):
        """Testa extração de imports simples"""
        content = "import os\nimport sys"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            
            imports = self.validator.extract_imports(Path(f.name))
            assert "os" in imports
            assert "sys" in imports
            assert len(imports) == 2
            
            os.unlink(f.name)
    
    def test_extract_imports_from_import(self):
        """Testa extração de imports from"""
        content = "from os import path\nfrom sys import version"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            
            imports = self.validator.extract_imports(Path(f.name))
            assert "os.path" in imports
            assert "sys.version" in imports
            assert len(imports) == 2
            
            os.unlink(f.name)
    
    def test_extract_imports_with_alias(self):
        """Testa extração de imports com alias"""
        content = "import os as operating_system\nfrom sys import version as ver"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            
            imports = self.validator.extract_imports(Path(f.name))
            assert "os" in imports
            assert "sys.version" in imports
            assert len(imports) == 2
            
            os.unlink(f.name)
    
    def test_extract_imports_invalid_syntax(self):
        """Testa extração com sintaxe inválida"""
        content = "import os\ninvalid syntax here"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            
            imports = self.validator.extract_imports(Path(f.name))
            # Deve retornar imports válidos encontrados antes do erro
            assert "os" in imports
            
            os.unlink(f.name)
    
    def test_extract_used_names_simple(self):
        """Testa extração de nomes utilizados simples"""
        content = "value = 1\ny = value + 2\nprint(result)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            
            used_names = self.validator.extract_used_names(Path(f.name))
            assert "value" in used_names
            assert "result" in used_names
            assert "print" in used_names
            
            os.unlink(f.name)
    
    def test_extract_used_names_attributes(self):
        """Testa extração de nomes com atributos"""
        content = "import os\npath = os.path.join('a', 'b')"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            
            used_names = self.validator.extract_used_names(Path(f.name))
            assert "os" in used_names
            assert "os.path" in used_names
            assert "os.path.join" in used_names
            assert "path" in used_names
            
            os.unlink(f.name)
    
    def test_is_import_used_direct(self):
        """Testa verificação de import usado diretamente"""
        used_names = {"os", "sys", "path"}
        assert self.validator._is_import_used("os", used_names) == True
        assert self.validator._is_import_used("sys", used_names) == True
        assert self.validator._is_import_used("path", used_names) == True
        assert self.validator._is_import_used("json", used_names) == False
    
    def test_is_import_used_module(self):
        """Testa verificação de import usado como módulo"""
        used_names = {"os.path", "sys.version"}
        assert self.validator._is_import_used("os", used_names) == True
        assert self.validator._is_import_used("sys", used_names) == True
        assert self.validator._is_import_used("os.path", used_names) == True
        assert self.validator._is_import_used("json", used_names) == False
    
    def test_is_import_used_partial(self):
        """Testa verificação de import parcial"""
        used_names = {"os.path.join", "sys.version_info"}
        assert self.validator._is_import_used("os", used_names) == True
        assert self.validator._is_import_used("os.path", used_names) == True
        assert self.validator._is_import_used("sys", used_names) == True
        assert self.validator._is_import_used("sys.version", used_names) == True
    
    @patch('builtins.open', new_callable=mock_open, read_data="os==1.0.0\nrequests>=2.0.0\nflask<3.0.0")
    def test_check_requirements_dependencies(self, mock_file):
        """Testa verificação de dependências no requirements.txt"""
        # Simular imports encontrados
        self.validator.imports_found = {
            "file1.py": {"os", "requests"},
            "file2.py": {"flask", "json"}
        }
        
        result = self.validator.check_requirements_dependencies()
        
        assert "os" in result["orphan_dependencies"]
        assert "requests" in result["orphan_dependencies"]
        assert "flask" in result["orphan_dependencies"]
        assert "json" in result["missing_dependencies"]
        assert result["total_requirements"] == 3
        assert result["used_dependencies"] == 4
    
    def test_check_requirements_dependencies_no_file(self):
        """Testa verificação quando requirements.txt não existe"""
        result = self.validator.check_requirements_dependencies()
        assert result == {}
    
    def test_generate_recommendations_with_issues(self):
        """Testa geração de recomendações com problemas"""
        self.validator.unused_imports = {
            "file1.py": {"unused1", "unused2"},
            "file2.py": {"unused3"}
        }
        self.validator.requirements_analysis = {
            "orphan_dependencies": ["orphan1", "orphan2"],
            "missing_dependencies": ["missing1"]
        }
        
        recommendations = self.validator._generate_recommendations()
        
        assert len(recommendations) == 3
        assert any("Remover 3 imports não utilizados" in rec for rec in recommendations)
        assert any("Considerar remover 2 dependências órfãs" in rec for rec in recommendations)
        assert any("Adicionar 1 dependências faltantes" in rec for rec in recommendations)
    
    def test_generate_recommendations_no_issues(self):
        """Testa geração de recomendações sem problemas"""
        self.validator.unused_imports = {}
        self.validator.requirements_analysis = {
            "orphan_dependencies": [],
            "missing_dependencies": []
        }
        
        recommendations = self.validator._generate_recommendations()
        
        assert len(recommendations) == 1
        assert "Nenhuma ação necessária" in recommendations[0]
    
    def test_generate_report(self):
        """Testa geração de relatório completo"""
        # Criar arquivo Python de teste
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("import os\nimport unused\nx = os.path.join('a', 'b')")
        
        # Criar requirements.txt de teste
        requirements_file = Path(self.temp_dir) / "requirements.txt"
        requirements_file.write_text("os==1.0.0\nunused==1.0.0\nmissing==1.0.0")
        
        report = self.validator.generate_report()
        
        assert "summary" in report
        assert "unused_imports" in report
        assert "requirements_analysis" in report
        assert "recommendations" in report
        
        summary = report["summary"]
        assert summary["total_files_analyzed"] == 1
        assert summary["total_imports_found"] == 2
        assert summary["total_unused_imports"] == 1
    
    def test_generate_report_with_output_file(self):
        """Testa geração de relatório com arquivo de saída"""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("import os\nx = 1")
        
        output_file = Path(self.temp_dir) / "report.json"
        report = self.validator.generate_report(str(output_file))
        
        assert output_file.exists()
        
        # Verificar conteúdo do arquivo
        with open(output_file, 'r') as f:
            saved_report = json.load(f)
        
        assert saved_report["summary"]["total_files_analyzed"] == 1

class TestDependencyValidatorIntegration:
    """Testes de integração para o validador"""
    
    def test_full_analysis_workflow(self):
        """Testa fluxo completo de análise"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar estrutura de teste
            test_dir = Path(temp_dir)
            
            # Arquivo com imports não utilizados
            (test_dir / "file1.py").write_text("""
import os
import unused_module
import sys

def test_function():
    return os.path.join('a', 'b')
""")
            
            # Arquivo com imports utilizados
            (test_dir / "file2.py").write_text("""
import json
import requests

def api_call():
    return requests.get('http://example.com')
""")
            
            # Requirements.txt
            (test_dir / "requirements.txt").write_text("""
os==1.0.0
requests==2.0.0
unused_package==1.0.0
""")
            
            validator = DependencyValidator(temp_dir)
            report = validator.generate_report()
            
            # Verificações
            assert report["summary"]["total_files_analyzed"] == 2
            assert report["summary"]["total_imports_found"] == 5  # os, unused_module, sys, json, requests
            assert report["summary"]["total_unused_imports"] == 2  # unused_module, sys
            
            # Verificar imports não utilizados
            unused = report["unused_imports"]
            assert "file1.py" in unused
            assert "unused_module" in unused["file1.py"]
            assert "sys" in unused["file1.py"]
            
            # Verificar dependências órfãs
            orphan_deps = report["requirements_analysis"]["orphan_dependencies"]
            assert "unused_package" in orphan_deps
            
            # Verificar dependências faltantes
            missing_deps = report["requirements_analysis"]["missing_dependencies"]
            assert "json" in missing_deps

if __name__ == "__main__":
    pytest.main([__file__]) 