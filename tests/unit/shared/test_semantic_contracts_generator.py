"""
Testes Unitários para SemanticContractsGenerator

Tracing ID: TEST_SEMANTIC_CONTRACTS_GENERATOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação Inicial

Responsável: Sistema de Documentação Enterprise
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from shared.semantic_contracts_generator import (
    SemanticContractsGenerator,
    FunctionInfo,
    ModuleInfo,
    SemanticContract
)


class TestSemanticContractsGenerator:
    """Testes para SemanticContractsGenerator"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.generator = SemanticContractsGenerator()
        
        # Código Python de exemplo para testes
        self.sample_module_code = '''
"""
Trigger Config Validator - Sistema de Validação de Configurações

Responsável: Sistema de Documentação Enterprise
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severidade da validação"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Resultado de uma validação"""
    is_valid: bool
    severity: ValidationSeverity
    message: str
    details: Optional[Dict[str, Any]] = None


class TriggerConfigValidator:
    """
    Validador de configurações de trigger para documentação enterprise
    
    Responsabilidades:
    - Validar arquivos sensíveis
    - Validar padrões de auto-rerun
    - Validar configurações de threshold
    """
    
    def __init__(self, config_path: str = "docs/trigger_config.json"):
        """
        Inicializa o validador
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = Path(config_path)
        self.config = None
        self.validation_results = []
    
    def validate_sensitive_files(self) -> ValidationResult:
        """
        Valida a lista de arquivos sensíveis
        
        Returns:
            ValidationResult com status da validação
        """
        if not self.config:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Configuração não carregada"
            )
        
        # Lógica de validação aqui
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message="Validação bem-sucedida"
        )
    
    def calculate_complexity(self, data: List[str]) -> str:
        """
        Calcula complexidade baseada nos dados
        
        Args:
            data: Lista de dados para análise
            
        Returns:
            String indicando complexidade (Baixa/Média/Alta)
            
        Raises:
            ValueError: Se dados estiverem vazios
        """
        if not data:
            raise ValueError("Dados não podem estar vazios")
        
        if len(data) < 5:
            return "Baixa"
        elif len(data) < 15:
            return "Média"
        else:
            return "Alta"
'''
    
    def test_init(self):
        """Teste de inicialização do gerador"""
        generator = SemanticContractsGenerator()
        
        assert generator.project_root == Path(".")
        assert generator.generated_contracts == []
        assert generator.embedding_service is None  # Sem dependência real
    
    def test_init_with_custom_root(self):
        """Teste de inicialização com raiz customizada"""
        generator = SemanticContractsGenerator("/custom/path")
        
        assert generator.project_root == Path("/custom/path")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_analyze_module_success(self, mock_exists, mock_file):
        """Teste de análise bem-sucedida de módulo"""
        mock_file.return_value.read.return_value = self.sample_module_code
        
        module_info = self.generator.analyze_module("shared/trigger_config_validator.py")
        
        assert module_info.name == "trigger_config_validator"
        assert "Sistema de Validação" in module_info.purpose
        assert "json" in module_info.dependencies
        assert len(module_info.functions) >= 3  # __init__, validate_sensitive_files, calculate_complexity
        assert "TriggerConfigValidator" in module_info.classes
        assert "ValidationSeverity" in module_info.classes
    
    @patch('pathlib.Path.exists', return_value=False)
    def test_analyze_module_not_found(self, mock_exists):
        """Teste de análise com módulo não encontrado"""
        with pytest.raises(FileNotFoundError):
            self.generator.analyze_module("nonexistent_module.py")
    
    def test_extract_module_purpose(self):
        """Teste de extração de propósito do módulo"""
        purpose = self.generator._extract_module_purpose(self.sample_module_code)
        
        assert "Sistema de Validação" in purpose
    
    def test_extract_module_purpose_no_docstring(self):
        """Teste de extração de propósito sem docstring"""
        code_without_docstring = "import json\n\ndef test():\n    pass"
        purpose = self.generator._extract_module_purpose(code_without_docstring)
        
        assert purpose == "Módulo Python"
    
    def test_extract_module_responsibility(self):
        """Teste de extração de responsabilidade do módulo"""
        responsibility = self.generator._extract_module_responsibility(self.sample_module_code)
        
        assert "Funcionalidade específica" in responsibility
    
    def test_extract_dependencies(self):
        """Teste de extração de dependências"""
        dependencies = self.generator._extract_dependencies(self.sample_module_code)
        
        assert "json" in dependencies
        assert "re" in dependencies
        assert "typing" in dependencies
        assert "pathlib" in dependencies
        assert "logging" in dependencies
        assert "dataclasses" in dependencies
        assert "enum" in dependencies
    
    def test_extract_dependencies_no_imports(self):
        """Teste de extração de dependências sem imports"""
        code_without_imports = "def test():\n    pass"
        dependencies = self.generator._extract_dependencies(code_without_imports)
        
        assert dependencies == []
    
    def test_extract_functions(self):
        """Teste de extração de funções"""
        import ast
        tree = ast.parse(self.sample_module_code)
        
        functions = self.generator._extract_functions(tree, "test_module", "test_path.py")
        
        assert len(functions) >= 3
        function_names = [f.name for f in functions]
        assert "__init__" in function_names
        assert "validate_sensitive_files" in function_names
        assert "calculate_complexity" in function_names
    
    def test_analyze_function(self):
        """Teste de análise de função específica"""
        import ast
        tree = ast.parse(self.sample_module_code)
        
        # Encontrar função __init__
        init_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                init_func = node
                break
        
        assert init_func is not None
        
        func_info = self.generator._analyze_function(init_func, "test_module", "test_path.py")
        
        assert func_info.name == "__init__"
        assert func_info.module == "test_module"
        assert "Inicializa o validador" in func_info.purpose
        assert "config_path" in func_info.parameters
        assert func_info.complexity in ["Baixa", "Média", "Alta"]
    
    def test_get_function_signature(self):
        """Teste de geração de assinatura de função"""
        import ast
        tree = ast.parse("def test_function(param1: str, param2: int = 10) -> bool:\n    pass")
        func_node = tree.body[0]
        
        signature = self.generator._get_function_signature(func_node)
        
        assert "def test_function" in signature
        assert "param1" in signature
        assert "param2" in signature
    
    def test_extract_exceptions(self):
        """Teste de extração de exceções"""
        import ast
        code_with_exceptions = '''
def test_function():
    if error_condition:
        raise ValueError("Erro de validação")
    if another_error:
        raise RuntimeError("Erro de runtime")
'''
        tree = ast.parse(code_with_exceptions)
        func_node = tree.body[0]
        
        exceptions = self.generator._extract_exceptions(func_node)
        
        assert "ValueError" in exceptions
        assert "RuntimeError" in exceptions
    
    def test_calculate_complexity(self):
        """Teste de cálculo de complexidade"""
        import ast
        simple_func = ast.parse("def simple():\n    pass").body[0]
        medium_func = ast.parse("def medium():\n    if value:\n        for index in range(10):\n            pass").body[0]
        complex_func = ast.parse("""
def complex():
    if value:
        for index in range(10):
            if result:
                while data:
                    try:
                        pass
                    except:
                        pass
        if a:
            pass
    if b:
        pass
""").body[0]
        
        assert self.generator._calculate_complexity(simple_func) == "Baixa"
        assert self.generator._calculate_complexity(medium_func) == "Média"
        assert self.generator._calculate_complexity(complex_func) == "Alta"
    
    def test_extract_function_purpose(self):
        """Teste de extração de propósito de função"""
        docstring = """
        Valida a lista de arquivos sensíveis
        
        Args:
            config: Configuração a ser validada
            
        Returns:
            ValidationResult com status da validação
        """
        
        purpose = self.generator._extract_function_purpose(docstring)
        
        assert "Valida a lista de arquivos sensíveis" in purpose
    
    def test_extract_function_purpose_empty(self):
        """Teste de extração de propósito sem docstring"""
        purpose = self.generator._extract_function_purpose("")
        
        assert purpose == "Função sem documentação"
    
    def test_extract_classes(self):
        """Teste de extração de classes"""
        import ast
        tree = ast.parse(self.sample_module_code)
        
        classes = self.generator._extract_classes(tree)
        
        assert "ValidationSeverity" in classes
        assert "ValidationResult" in classes
        assert "TriggerConfigValidator" in classes
    
    def test_calculate_basic_similarity(self):
        """Teste de cálculo de similaridade básica"""
        module_info = ModuleInfo(
            name="test_module",
            path="test_path.py",
            purpose="Módulo de teste bem documentado",
            responsibility="Testar funcionalidades",
            dependencies=["json", "re"],
            functions=[
                FunctionInfo(
                    name="test_func",
                    module="test_module",
                    path="test_path.py:10",
                    line=10,
                    docstring="Função de teste bem documentada",
                    signature="def test_func():",
                    parameters=[],
                    return_type="None",
                    exceptions=[],
                    complexity="Baixa",
                    purpose="Testar funcionalidade"
                )
            ],
            classes=["TestClass"],
            version="1.0",
            last_updated="2025-01-27 10:00:00"
        )
        
        similarity = self.generator._calculate_basic_similarity(module_info)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # Deve ter score decente para módulo bem documentado
    
    def test_calculate_basic_quality_metrics(self):
        """Teste de cálculo de métricas básicas de qualidade"""
        module_info = ModuleInfo(
            name="test_module",
            path="test_path.py",
            purpose="Módulo de teste",
            responsibility="Testar",
            dependencies=[],
            functions=[
                FunctionInfo(
                    name="test_func",
                    module="test_module",
                    path="test_path.py:10",
                    line=10,
                    docstring="Função documentada",
                    signature="def test_func():",
                    parameters=[],
                    return_type="None",
                    exceptions=[],
                    complexity="Baixa",
                    purpose="Testar"
                )
            ],
            classes=[],
            version="1.0",
            last_updated="2025-01-27 10:00:00"
        )
        
        metrics = self.generator._calculate_basic_quality_metrics(module_info)
        
        assert "completude" in metrics
        assert "coerencia" in metrics
        assert "similaridade_semantica" in metrics
        assert "clareza" in metrics
        assert "rastreabilidade" in metrics
        
        for metric, value in metrics.items():
            assert 0.0 <= value <= 1.0
    
    def test_find_test_references(self):
        """Teste de busca de referências aos testes"""
        module_info = ModuleInfo(
            name="trigger_config_validator",
            path="shared/trigger_config_validator.py",
            purpose="Teste",
            responsibility="Teste",
            dependencies=[],
            functions=[],
            classes=[],
            version="1.0",
            last_updated="2025-01-27 10:00:00"
        )
        
        with patch('pathlib.Path.exists', return_value=True):
            references = self.generator.find_test_references(module_info)
            
            # Deve retornar dicionário mesmo sem testes encontrados
            assert isinstance(references, dict)
    
    @patch('shared.semantic_contracts_generator.SemanticContractsGenerator.analyze_module')
    @patch('shared.semantic_contracts_generator.SemanticContractsGenerator.calculate_semantic_similarity')
    @patch('shared.semantic_contracts_generator.SemanticContractsGenerator.calculate_quality_metrics')
    @patch('shared.semantic_contracts_generator.SemanticContractsGenerator.find_test_references')
    def test_generate_module_docs(self, mock_find_tests, mock_quality, mock_similarity, mock_analyze):
        """Teste de geração de documentação de módulo"""
        # Mock das funções
        mock_analyze.return_value = ModuleInfo(
            name="test_module",
            path="test_path.py",
            purpose="Teste",
            responsibility="Teste",
            dependencies=[],
            functions=[],
            classes=[],
            version="1.0",
            last_updated="2025-01-27 10:00:00"
        )
        mock_similarity.return_value = 0.85
        mock_quality.return_value = {
            "completude": 0.9,
            "coerencia": 0.8,
            "similaridade_semantica": 0.85,
            "clareza": 0.7,
            "rastreabilidade": 0.8
        }
        mock_find_tests.return_value = {"unit": "tests/unit/test_module.py"}
        
        contract = self.generator.generate_module_docs("test_module.py")
        
        assert isinstance(contract, SemanticContract)
        assert contract.module_info.name == "test_module"
        assert contract.semantic_similarity == 0.85
        assert len(contract.quality_metrics) == 5
        assert contract in self.generator.generated_contracts
    
    @patch('shared.semantic_contracts_generator.SemanticContractsGenerator.analyze_module')
    def test_generate_function_docs_found(self, mock_analyze):
        """Teste de geração de documentação de função encontrada"""
        mock_analyze.return_value = ModuleInfo(
            name="test_module",
            path="test_path.py",
            purpose="Teste",
            responsibility="Teste",
            dependencies=[],
            functions=[
                FunctionInfo(
                    name="test_func",
                    module="test_module",
                    path="test_path.py:10",
                    line=10,
                    docstring="Função de teste",
                    signature="def test_func():",
                    parameters=[],
                    return_type="None",
                    exceptions=[],
                    complexity="Baixa",
                    purpose="Testar"
                )
            ],
            classes=[],
            version="1.0",
            last_updated="2025-01-27 10:00:00"
        )
        
        func_info = self.generator.generate_function_docs("test_module.py", "test_func")
        
        assert func_info is not None
        assert func_info.name == "test_func"
    
    @patch('shared.semantic_contracts_generator.SemanticContractsGenerator.analyze_module')
    def test_generate_function_docs_not_found(self, mock_analyze):
        """Teste de geração de documentação de função não encontrada"""
        mock_analyze.return_value = ModuleInfo(
            name="test_module",
            path="test_path.py",
            purpose="Teste",
            responsibility="Teste",
            dependencies=[],
            functions=[],
            classes=[],
            version="1.0",
            last_updated="2025-01-27 10:00:00"
        )
        
        func_info = self.generator.generate_function_docs("test_module.py", "nonexistent_func")
        
        assert func_info is None
    
    def test_generate_markdown_documentation(self):
        """Teste de geração de documentação Markdown"""
        contract = SemanticContract(
            module_info=ModuleInfo(
                name="test_module",
                path="test_path.py",
                purpose="Módulo de teste",
                responsibility="Testar funcionalidades",
                dependencies=["json", "re"],
                functions=[
                    FunctionInfo(
                        name="test_func",
                        module="test_module",
                        path="test_path.py:10",
                        line=10,
                        docstring="Função de teste",
                        signature="def test_func():",
                        parameters=[],
                        return_type="None",
                        exceptions=[],
                        complexity="Baixa",
                        purpose="Testar"
                    )
                ],
                classes=["TestClass"],
                version="1.0",
                last_updated="2025-01-27 10:00:00"
            ),
            functions=[
                FunctionInfo(
                    name="test_func",
                    module="test_module",
                    path="test_path.py:10",
                    line=10,
                    docstring="Função de teste",
                    signature="def test_func():",
                    parameters=[],
                    return_type="None",
                    exceptions=[],
                    complexity="Baixa",
                    purpose="Testar"
                )
            ],
            semantic_similarity=0.85,
            quality_metrics={
                "completude": 0.9,
                "coerencia": 0.8,
                "similaridade_semantica": 0.85,
                "clareza": 0.7,
                "rastreabilidade": 0.8
            },
            test_references={"test_func": "tests/unit/test_module.py::test_test_func"}
        )
        
        markdown = self.generator.generate_markdown_documentation(contract)
        
        assert "## 📦 **MÓDULO: test_module**" in markdown
        assert "### **Metadados**" in markdown
        assert "### **Interface Pública**" in markdown
        assert "### **Contratos de Função**" in markdown
        assert "### **Métricas de Qualidade**" in markdown
        assert "test_func" in markdown
        assert "0.85" in markdown
    
    def test_save_documentation(self):
        """Teste de salvamento de documentação"""
        contract = SemanticContract(
            module_info=ModuleInfo(
                name="test_module",
                path="test_path.py",
                purpose="Teste",
                responsibility="Teste",
                dependencies=[],
                functions=[],
                classes=[],
                version="1.0",
                last_updated="2025-01-27 10:00:00"
            ),
            functions=[],
            semantic_similarity=0.85,
            quality_metrics={},
            test_references={}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_contract.md")
            
            self.generator.save_documentation(contract, output_path)
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "## 📦 **MÓDULO: test_module**" in content


class TestFunctionInfo:
    """Testes para FunctionInfo"""
    
    def test_function_info_creation(self):
        """Teste de criação de FunctionInfo"""
        func_info = FunctionInfo(
            name="test_func",
            module="test_module",
            path="test_path.py:10",
            line=10,
            docstring="Função de teste",
            signature="def test_func():",
            parameters=[],
            return_type="None",
            exceptions=[],
            complexity="Baixa",
            purpose="Testar"
        )
        
        assert func_info.name == "test_func"
        assert func_info.module == "test_module"
        assert func_info.path == "test_path.py:10"
        assert func_info.line == 10
        assert func_info.docstring == "Função de teste"
        assert func_info.signature == "def test_func():"
        assert func_info.parameters == []
        assert func_info.return_type == "None"
        assert func_info.exceptions == []
        assert func_info.complexity == "Baixa"
        assert func_info.purpose == "Testar"


class TestModuleInfo:
    """Testes para ModuleInfo"""
    
    def test_module_info_creation(self):
        """Teste de criação de ModuleInfo"""
        module_info = ModuleInfo(
            name="test_module",
            path="test_path.py",
            purpose="Módulo de teste",
            responsibility="Testar funcionalidades",
            dependencies=["json", "re"],
            functions=[],
            classes=["TestClass"],
            version="1.0",
            last_updated="2025-01-27 10:00:00"
        )
        
        assert module_info.name == "test_module"
        assert module_info.path == "test_path.py"
        assert module_info.purpose == "Módulo de teste"
        assert module_info.responsibility == "Testar funcionalidades"
        assert module_info.dependencies == ["json", "re"]
        assert module_info.functions == []
        assert module_info.classes == ["TestClass"]
        assert module_info.version == "1.0"
        assert module_info.last_updated == "2025-01-27 10:00:00"


class TestSemanticContract:
    """Testes para SemanticContract"""
    
    def test_semantic_contract_creation(self):
        """Teste de criação de SemanticContract"""
        module_info = ModuleInfo(
            name="test_module",
            path="test_path.py",
            purpose="Teste",
            responsibility="Teste",
            dependencies=[],
            functions=[],
            classes=[],
            version="1.0",
            last_updated="2025-01-27 10:00:00"
        )
        
        contract = SemanticContract(
            module_info=module_info,
            functions=[],
            semantic_similarity=0.85,
            quality_metrics={"completude": 0.9},
            test_references={"unit": "tests/unit/test_module.py"}
        )
        
        assert contract.module_info == module_info
        assert contract.functions == []
        assert contract.semantic_similarity == 0.85
        assert contract.quality_metrics == {"completude": 0.9}
        assert contract.test_references == {"unit": "tests/unit/test_module.py"}


if __name__ == "__main__":
    pytest.main([__file__]) 