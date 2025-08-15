"""
Testes Unitários para GapDetector
=================================

Testes para o sistema de detecção de lacunas semânticas e estruturais.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from infrastructure.analysis.gap_detector import (
    GapDetector,
    GapType,
    GapSeverity,
    GapDetection,
    GapAnalysisResult
)


class TestGapDetector:
    """Testes para GapDetector."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Cria diretório temporário para projeto de teste."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir()
            yield project_dir
    
    @pytest.fixture
    def gap_detector(self, temp_project_dir):
        """Cria instância do GapDetector para testes."""
        return GapDetector(
            project_root=str(temp_project_dir),
            enable_nlp=False,  # Desabilitar NLP para testes
            confidence_threshold=0.7
        )
    
    @pytest.fixture
    def sample_python_file(self, temp_project_dir):
        """Cria arquivo Python de exemplo para testes."""
        file_path = temp_project_dir / "test_module.py"
        content = '''
"""
Módulo de teste para análise de lacunas.
"""

import os
import sys
from typing import List, Dict

def test_function_without_type_hint(param):
    """Função sem type hints."""
    return param * 2

def test_function_with_type_hint(param: int) -> int:
    """Função com type hints."""
    return param * 2

class TestClass:
    """Classe de teste."""
    
    def __init__(self):
        self.value = 42
    
    def method_without_docstring(self):
        return self.value
'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        detector = GapDetector()
        
        assert detector.project_root == Path(".")
        assert detector.enable_nlp is False  # NLP desabilitado por padrão
        assert detector.confidence_threshold == 0.7
        assert len(detector.exclude_patterns) > 0
        assert len(detector.include_patterns) > 0
    
    def test_init_custom_values(self, temp_project_dir):
        """Testa inicialização com valores customizados."""
        detector = GapDetector(
            project_root=str(temp_project_dir),
            exclude_patterns=[r'test'],
            include_patterns=[r'\.py$'],
            enable_nlp=True,
            confidence_threshold=0.8
        )
        
        assert detector.project_root == temp_project_dir
        assert detector.exclude_patterns == [r'test']
        assert detector.include_patterns == [r'\.py$']
        assert detector.confidence_threshold == 0.8
    
    def test_find_files_to_analyze_empty_project(self, gap_detector):
        """Testa busca de arquivos em projeto vazio."""
        files = gap_detector._find_files_to_analyze()
        assert len(files) == 0
    
    def test_find_files_to_analyze_with_python_files(self, gap_detector, sample_python_file):
        """Testa busca de arquivos Python."""
        files = gap_detector._find_files_to_analyze()
        assert len(files) == 1
        assert files[0].name == "test_module.py"
    
    def test_should_exclude_file(self, gap_detector):
        """Testa exclusão de arquivos."""
        # Arquivo que deve ser excluído
        excluded_file = Path("__pycache__/test.py")
        assert gap_detector._should_exclude_file(excluded_file) is True
        
        # Arquivo que não deve ser excluído
        included_file = Path("src/test.py")
        assert gap_detector._should_exclude_file(included_file) is False
    
    def test_analyze_file_success(self, gap_detector, sample_python_file):
        """Testa análise bem-sucedida de arquivo."""
        gaps = gap_detector._analyze_file(sample_python_file)
        
        # Deve encontrar algumas lacunas
        assert isinstance(gaps, list)
        assert len(gaps) > 0
        
        # Verificar tipos de lacunas encontradas
        gap_types = [gap.gap_type for gap in gaps]
        assert GapType.MISSING_TYPE_HINTS in gap_types
        assert GapType.MISSING_DOCUMENTATION in gap_types
    
    def test_analyze_file_syntax_error(self, gap_detector, temp_project_dir):
        """Testa análise de arquivo com erro de sintaxe."""
        # Criar arquivo com sintaxe inválida
        invalid_file = temp_project_dir / "invalid.py"
        with open(invalid_file, 'w') as f:
            f.write("def invalid syntax here")
        
        gaps = gap_detector._analyze_file(invalid_file)
        
        assert len(gaps) > 0
        assert any(gap.gap_type == GapType.MISSING_VALIDATION for gap in gaps)
    
    def test_analyze_ast_tree(self, gap_detector, temp_project_dir):
        """Testa análise da árvore AST."""
        # Criar arquivo com funções sem type hints
        file_path = temp_project_dir / "test_ast.py"
        content = '''
def function_without_type_hint(param):
    return param

def function_with_type_hint(param: int) -> int:
    return param

class ClassWithoutDocstring:
    def method_without_type_hint(self, param):
        return param
'''
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        import ast
        tree = ast.parse(content)
        gaps = gap_detector._analyze_ast_tree(tree, file_path)
        
        # Deve encontrar lacunas de type hints
        assert len(gaps) > 0
        assert any(gap.gap_type == GapType.MISSING_TYPE_HINTS for gap in gaps)
    
    def test_analyze_patterns(self, gap_detector, temp_project_dir):
        """Testa análise de padrões."""
        # Criar arquivo com linhas longas
        file_path = temp_project_dir / "test_patterns.py"
        long_line = "x" * 150  # Linha muito longa
        content = f'''
def test_function():
    {long_line}
    return True
'''
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        gaps = gap_detector._analyze_patterns(content, file_path)
        
        # Deve encontrar lacuna de linha muito longa
        assert len(gaps) > 0
        assert any(gap.gap_type == GapType.MISSING_VALIDATION for gap in gaps)
    
    def test_analyze_documentation(self, gap_detector, temp_project_dir):
        """Testa análise de documentação."""
        # Criar arquivo sem docstring
        file_path = temp_project_dir / "test_docs.py"
        content = '''
import os

def test_function():
    return True
'''
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        gaps = gap_detector._analyze_documentation(content, file_path)
        
        # Deve encontrar lacuna de documentação
        assert len(gaps) > 0
        assert any(gap.gap_type == GapType.MISSING_DOCUMENTATION for gap in gaps)
    
    def test_analyze_test_coverage(self, gap_detector, temp_project_dir):
        """Testa análise de cobertura de testes."""
        # Criar arquivo sem teste correspondente
        file_path = temp_project_dir / "module_without_test.py"
        with open(file_path, 'w') as f:
            f.write("def test_function(): pass")
        
        gaps = gap_detector._analyze_test_coverage(file_path)
        
        # Deve encontrar lacuna de teste
        assert len(gaps) > 0
        assert any(gap.gap_type == GapType.MISSING_TEST for gap in gaps)
    
    def test_analyze_test_coverage_with_test(self, gap_detector, temp_project_dir):
        """Testa análise de cobertura com teste existente."""
        # Criar arquivo principal
        main_file = temp_project_dir / "main_module.py"
        with open(main_file, 'w') as f:
            f.write("def main_function(): pass")
        
        # Criar arquivo de teste
        test_dir = temp_project_dir / "tests"
        test_dir.mkdir()
        test_file = test_dir / "test_main_module.py"
        with open(test_file, 'w') as f:
            f.write("def test_main_function(): pass")
        
        gaps = gap_detector._analyze_test_coverage(main_file)
        
        # Não deve encontrar lacuna de teste
        assert len(gaps) == 0
    
    def test_analyze_dependency_gaps(self, gap_detector):
        """Testa análise de lacunas de dependências."""
        gaps = gap_detector._analyze_dependency_gaps()
        
        # Deve encontrar lacunas de configuração
        assert isinstance(gaps, list)
        assert any(gap.gap_type == GapType.MISSING_CONFIG for gap in gaps)
    
    def test_analyze_structural_gaps(self, gap_detector):
        """Testa análise de lacunas estruturais."""
        gaps = gap_detector._analyze_structural_gaps()
        
        # Deve encontrar lacunas estruturais
        assert isinstance(gaps, list)
        assert any(gap.gap_type == GapType.MISSING_CONFIG for gap in gaps)
    
    def test_get_file_hash(self, gap_detector, temp_project_dir):
        """Testa cálculo de hash de arquivo."""
        # Criar arquivo de teste
        file_path = temp_project_dir / "test_hash.py"
        content = "test content"
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        hash1 = gap_detector._get_file_hash(file_path)
        hash2 = gap_detector._get_file_hash(file_path)
        
        # Hash deve ser consistente
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
    
    def test_extract_import_name(self, gap_detector):
        """Testa extração de nome de import."""
        # Teste import simples
        import_line = "import os"
        name = gap_detector._extract_import_name(import_line)
        assert name == "os"
        
        # Teste from import
        from_line = "from typing import List"
        name = gap_detector._extract_import_name(from_line)
        assert name == "typing"
        
        # Teste linha inválida
        invalid_line = "def function(): pass"
        name = gap_detector._extract_import_name(invalid_line)
        assert name is None
    
    def test_is_import_used(self, gap_detector):
        """Testa verificação de uso de import."""
        content = "import os\nos.path.join('test', 'file')"
        
        # Import usado
        assert gap_detector._is_import_used(content, "os") is True
        
        # Import não usado
        assert gap_detector._is_import_used(content, "sys") is False
    
    def test_find_test_file(self, gap_detector, temp_project_dir):
        """Testa busca de arquivo de teste."""
        # Criar arquivo principal
        main_file = temp_project_dir / "main.py"
        with open(main_file, 'w') as f:
            f.write("def main(): pass")
        
        # Sem teste
        test_file = gap_detector._find_test_file(main_file)
        assert test_file is None
        
        # Com teste
        test_dir = temp_project_dir / "tests"
        test_dir.mkdir()
        test_file_path = test_dir / "test_main.py"
        with open(test_file_path, 'w') as f:
            f.write("def test_main(): pass")
        
        found_test = gap_detector._find_test_file(main_file)
        assert found_test == test_file_path
    
    def test_get_test_file_path(self, gap_detector, temp_project_dir):
        """Testa geração de caminho de teste."""
        file_path = temp_project_dir / "module.py"
        test_path = gap_detector._get_test_file_path(file_path)
        assert test_path == "tests/test_module.py"
    
    def test_count_gaps_by_severity(self, gap_detector):
        """Testa contagem de gaps por severidade."""
        gaps = [
            GapDetection(GapType.MISSING_TEST, GapSeverity.CRITICAL, "test.py"),
            GapDetection(GapType.MISSING_DOCUMENTATION, GapSeverity.HIGH, "test.py"),
            GapDetection(GapType.MISSING_TYPE_HINTS, GapSeverity.MEDIUM, "test.py"),
            GapDetection(GapType.MISSING_LOGGING, GapSeverity.LOW, "test.py")
        ]
        
        counts = gap_detector._count_gaps_by_severity(gaps)
        
        assert counts[GapSeverity.CRITICAL] == 1
        assert counts[GapSeverity.HIGH] == 1
        assert counts[GapSeverity.MEDIUM] == 1
        assert counts[GapSeverity.LOW] == 1
    
    def test_calculate_coverage_score(self, gap_detector):
        """Testa cálculo de score de cobertura."""
        # Cobertura completa
        score = gap_detector._calculate_coverage_score(10, 10)
        assert score == 1.0
        
        # Cobertura parcial
        score = gap_detector._calculate_coverage_score(5, 10)
        assert score == 0.5
        
        # Sem arquivos
        score = gap_detector._calculate_coverage_score(0, 0)
        assert score == 0.0
    
    def test_calculate_quality_score(self, gap_detector):
        """Testa cálculo de score de qualidade."""
        # Sem gaps
        score = gap_detector._calculate_quality_score([])
        assert score == 1.0
        
        # Com gaps
        gaps = [
            GapDetection(GapType.MISSING_TEST, GapSeverity.CRITICAL, "test.py"),
            GapDetection(GapType.MISSING_DOCUMENTATION, GapSeverity.HIGH, "test.py")
        ]
        score = gap_detector._calculate_quality_score(gaps)
        assert score < 1.0
        assert score > 0.0
    
    def test_analyze_project_integration(self, gap_detector, sample_python_file):
        """Testa análise completa do projeto."""
        result = gap_detector.analyze_project()
        
        assert isinstance(result, GapAnalysisResult)
        assert result.total_gaps >= 0
        assert result.files_analyzed >= 1
        assert result.processing_time > 0
        assert 0.0 <= result.coverage_score <= 1.0
        assert 0.0 <= result.quality_score <= 1.0
    
    def test_generate_report(self, gap_detector, sample_python_file):
        """Testa geração de relatório."""
        result = gap_detector.analyze_project()
        report = gap_detector.generate_report(result)
        
        assert isinstance(report, str)
        assert "Relatório de Análise de Lacunas" in report
        assert str(result.total_gaps) in report
    
    def test_clear_cache(self, gap_detector, sample_python_file):
        """Testa limpeza de cache."""
        # Executar análise para popular cache
        gap_detector.analyze_project()
        
        # Verificar que cache foi populado
        assert len(gap_detector.analysis_cache) > 0
        assert len(gap_detector.file_hashes) > 0
        
        # Limpar cache
        gap_detector.clear_cache()
        
        # Verificar que cache foi limpo
        assert len(gap_detector.analysis_cache) == 0
        assert len(gap_detector.file_hashes) == 0


class TestGapDetection:
    """Testes para GapDetection."""
    
    def test_gap_detection_creation(self):
        """Testa criação de GapDetection."""
        gap = GapDetection(
            gap_type=GapType.MISSING_TEST,
            severity=GapSeverity.HIGH,
            file_path="test.py",
            line_number=10,
            description="Teste sem cobertura",
            suggestion="Criar teste unitário",
            confidence=0.8
        )
        
        assert gap.gap_type == GapType.MISSING_TEST
        assert gap.severity == GapSeverity.HIGH
        assert gap.file_path == "test.py"
        assert gap.line_number == 10
        assert gap.description == "Teste sem cobertura"
        assert gap.suggestion == "Criar teste unitário"
        assert gap.confidence == 0.8


class TestGapAnalysisResult:
    """Testes para GapAnalysisResult."""
    
    def test_gap_analysis_result_creation(self):
        """Testa criação de GapAnalysisResult."""
        gaps = [
            GapDetection(GapType.MISSING_TEST, GapSeverity.HIGH, "test.py")
        ]
        
        result = GapAnalysisResult(
            gaps=gaps,
            total_gaps=1,
            critical_gaps=0,
            high_gaps=1,
            medium_gaps=0,
            low_gaps=0,
            info_gaps=0,
            processing_time=1.5,
            files_analyzed=5,
            coverage_score=0.8,
            quality_score=0.9,
            metadata={"test": "data"}
        )
        
        assert result.total_gaps == 1
        assert result.high_gaps == 1
        assert result.processing_time == 1.5
        assert result.files_analyzed == 5
        assert result.coverage_score == 0.8
        assert result.quality_score == 0.9 