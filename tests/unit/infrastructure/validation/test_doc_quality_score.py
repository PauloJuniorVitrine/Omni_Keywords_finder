from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de DocQualityScore
Tracing ID: TEST_DOC_QUALITY_SCORE_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa testes unitários abrangentes para o sistema
de DocQualityScore, cobrindo todos os cenários de uso e
validações de qualidade enterprise.
"""

import pytest
import tempfile
import shutil
import json
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar o sistema a ser testado
from infrastructure.validation.doc_quality_score import DocQualityAnalyzer, DocQualityMetrics
from infrastructure.ml.semantic_embeddings import SemanticEmbeddingService

class TestDocQualityAnalyzer:
    """
    Testes para DocQualityAnalyzer.
    
    Cobre todos os métodos públicos e cenários de erro.
    """
    
    @pytest.fixture
    def temp_output_dir(self):
        """Cria diretório temporário para saída de testes."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_semantic_service(self):
        """Cria mock do serviço semântico."""
        mock_service = Mock(spec=SemanticEmbeddingService)
        mock_service.validate_semantic_consistency.return_value = True
        mock_service.model_name = 'all-MiniLM-L6-v2'
        return mock_service
    
    @pytest.fixture
    def doc_analyzer(self, temp_output_dir, mock_semantic_service):
        """Cria instância do analisador para testes."""
        return DocQualityAnalyzer(
            semantic_service=mock_semantic_service,
            output_dir=temp_output_dir,
            threshold=0.85
        )
    
    @pytest.fixture
    def sample_python_code(self):
        """Código Python de exemplo para testes."""
        return '''
def calculate_keyword_score(termo: str, volume: int, dificuldade: float) -> float:
    """
    Calcula score de uma keyword baseado em volume e dificuldade.
    
    Args:
        termo: Termo da keyword
        volume: Volume de busca mensal
        dificuldade: Dificuldade de ranking (0-100)
    
    Returns:
        Score calculado (0-100)
    
    Raises:
        ValueError: Se parâmetros inválidos
    """
    if not termo or volume < 0 or dificuldade < 0:
        raise ValueError("Parâmetros inválidos")
    
    score = (volume * 0.7) + ((100 - dificuldade) * 0.3)
    return min(100.0, max(0.0, score))
'''
    
    @pytest.fixture
    def sample_python_doc(self):
        """Documentação Python de exemplo para testes."""
        return '''
def calculate_keyword_score(termo: str, volume: int, dificuldade: float) -> float:
    """
    Calcula score de uma keyword baseado em volume e dificuldade.
    
    Args:
        termo: Termo da keyword
        volume: Volume de busca mensal
        dificuldade: Dificuldade de ranking (0-100)
    
    Returns:
        Score calculado (0-100)
    
    Raises:
        ValueError: Se parâmetros inválidos
    
    Examples:
        >>> calculate_keyword_score("python tutorial", 1000, 30)
        85.0
    """
'''
    
    @pytest.fixture
    def sample_typescript_code(self):
        """Código TypeScript de exemplo para testes."""
        return '''
interface KeywordData {
    termo: string;
    volume: number;
    dificuldade: number;
}

function calculateKeywordScore(data: KeywordData): number {
    const { termo, volume, dificuldade } = data;
    
    if (!termo || volume < 0 || dificuldade < 0) {
        throw new Error("Parâmetros inválidos");
    }
    
    const score = (volume * 0.7) + ((100 - dificuldade) * 0.3);
    return Math.min(100.0, Math.max(0.0, score));
}
'''
    
    @pytest.fixture
    def sample_typescript_doc(self):
        """Documentação TypeScript de exemplo para testes."""
        return '''
/**
 * Calcula score de uma keyword baseado em volume e dificuldade.
 * 
 * @param data - Dados da keyword
 * @param data.termo - Termo da keyword
 * @param data.volume - Volume de busca mensal
 * @param data.dificuldade - Dificuldade de ranking (0-100)
 * 
 * @returns Score calculado (0-100)
 * 
 * @throws {Error} Se parâmetros inválidos
 * 
 * @example
 * ```typescript
 * const score = calculateKeywordScore({
 *   termo: "python tutorial",
 *   volume: 1000,
 *   dificuldade: 30
 * });
 * // score = 85.0
 * ```
 */
function calculateKeywordScore(data: KeywordData): number {
'''
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        analyzer = DocQualityAnalyzer()
        
        assert analyzer.threshold == 0.85
        assert analyzer.semantic_service is not None
        assert isinstance(analyzer.semantic_service, SemanticEmbeddingService)
        assert "quality_reports" in analyzer.output_dir
    
    def test_init_custom_values(self, temp_output_dir, mock_semantic_service):
        """Testa inicialização com valores customizados."""
        analyzer = DocQualityAnalyzer(
            semantic_service=mock_semantic_service,
            output_dir=temp_output_dir,
            threshold=0.9
        )
        
        assert analyzer.threshold == 0.9
        assert analyzer.semantic_service == mock_semantic_service
        assert analyzer.output_dir == temp_output_dir
    
    def test_analyze_completeness_python_complete(self, doc_analyzer, sample_python_code, sample_python_doc):
        """Testa análise de completude para Python com documentação completa."""
        completeness = doc_analyzer.analyze_completeness(sample_python_code, sample_python_doc, 'python')
        
        # Deve ter alta completude (docstring, parâmetros, retorno, raises, examples)
        assert 0.8 <= completeness <= 1.0
    
    def test_analyze_completeness_python_incomplete(self, doc_analyzer, sample_python_code):
        """Testa análise de completude para Python com documentação incompleta."""
        incomplete_doc = '''
def calculate_keyword_score(termo: str, volume: int, dificuldade: float) -> float:
    """Calcula score."""
    pass
'''
        completeness = doc_analyzer.analyze_completeness(sample_python_code, incomplete_doc, 'python')
        
        # Deve ter baixa completude (apenas docstring básica)
        assert 0.0 <= completeness <= 0.5
    
    def test_analyze_completeness_typescript_complete(self, doc_analyzer, sample_typescript_code, sample_typescript_doc):
        """Testa análise de completude para TypeScript com documentação completa."""
        completeness = doc_analyzer.analyze_completeness(sample_typescript_code, sample_typescript_doc, 'typescript')
        
        # Deve ter alta completude (JSDoc, parâmetros, retorno, throws, example)
        assert 0.8 <= completeness <= 1.0
    
    def test_analyze_completeness_unsupported_language(self, doc_analyzer, sample_python_code, sample_python_doc):
        """Testa análise de completude para linguagem não suportada."""
        completeness = doc_analyzer.analyze_completeness(sample_python_code, sample_python_doc, 'rust')
        
        # Deve retornar score neutro para linguagens não suportadas
        assert completeness == 0.5
    
    def test_analyze_coherence_high_quality(self, doc_analyzer):
        """Testa análise de coerência para documentação de alta qualidade."""
        high_quality_doc = '''
Calcula score de uma keyword baseado em volume e dificuldade.

Args:
    termo: Termo da keyword para análise
    volume: Volume de busca mensal da keyword
    dificuldade: Dificuldade de ranking da keyword (0-100)

Returns:
    Score calculado da keyword (0-100)

Examples:
    >>> calculate_keyword_score("python tutorial", 1000, 30)
    85.0

Note:
    O score é calculado usando uma fórmula ponderada que considera
    tanto o volume de busca quanto a dificuldade de ranking.
'''
        coherence = doc_analyzer.analyze_coherence(high_quality_doc)
        
        # Deve ter alta coerência (terminologia consistente, estrutura clara, exemplos)
        assert 0.8 <= coherence <= 1.0
    
    def test_analyze_coherence_low_quality(self, doc_analyzer):
        """Testa análise de coerência para documentação de baixa qualidade."""
        low_quality_doc = '''
Calcula algo.

Args:
    value: coisa
    result: outra coisa

Returns:
    resultado
'''
        coherence = doc_analyzer.analyze_coherence(low_quality_doc)
        
        # Deve ter baixa coerência (terminologia inconsistente, estrutura pobre)
        assert 0.0 <= coherence <= 0.5
    
    def test_analyze_coherence_empty_doc(self, doc_analyzer):
        """Testa análise de coerência para documentação vazia."""
        coherence = doc_analyzer.analyze_coherence("")
        
        # Deve retornar 0 para documentação vazia
        assert coherence == 0.0
    
    def test_analyze_semantic_similarity_consistent(self, doc_analyzer, sample_python_code, sample_python_doc, mock_semantic_service):
        """Testa análise de similaridade semântica para código e documentação consistentes."""
        mock_semantic_service.validate_semantic_consistency.return_value = True
        
        similarity = doc_analyzer.analyze_semantic_similarity(sample_python_code, sample_python_doc)
        
        # Deve retornar 1.0 quando consistente
        assert similarity == 1.0
        mock_semantic_service.validate_semantic_consistency.assert_called_once()
    
    def test_analyze_semantic_similarity_inconsistent(self, doc_analyzer, sample_python_code, sample_python_doc, mock_semantic_service):
        """Testa análise de similaridade semântica para código e documentação inconsistentes."""
        mock_semantic_service.validate_semantic_consistency.return_value = False
        
        similarity = doc_analyzer.analyze_semantic_similarity(sample_python_code, sample_python_doc)
        
        # Deve retornar 0.5 quando inconsistente
        assert similarity == 0.5
    
    def test_analyze_semantic_similarity_error(self, doc_analyzer, sample_python_code, sample_python_doc, mock_semantic_service):
        """Testa análise de similaridade semântica com erro no serviço."""
        mock_semantic_service.validate_semantic_consistency.side_effect = Exception("Erro no serviço")
        
        similarity = doc_analyzer.analyze_semantic_similarity(sample_python_code, sample_python_doc)
        
        # Deve retornar 0.5 em caso de erro
        assert similarity == 0.5
    
    def test_calculate_doc_quality_score_high_quality(self, doc_analyzer):
        """Testa cálculo de DocQualityScore para documentação de alta qualidade."""
        completeness = 0.9
        coherence = 0.85
        semantic_similarity = 0.95
        
        score = doc_analyzer.calculate_doc_quality_score(completeness, coherence, semantic_similarity)
        
        # Fórmula: ((0.9 * 4) + (0.85 * 3) + (0.95 * 3)) / 10 = 0.9
        expected_score = ((completeness * 4) + (coherence * 3) + (semantic_similarity * 3)) / 10
        assert abs(score - expected_score) < 0.01
        assert score > 0.85  # Deve ser aceitável
    
    def test_calculate_doc_quality_score_low_quality(self, doc_analyzer):
        """Testa cálculo de DocQualityScore para documentação de baixa qualidade."""
        completeness = 0.3
        coherence = 0.4
        semantic_similarity = 0.5
        
        score = doc_analyzer.calculate_doc_quality_score(completeness, coherence, semantic_similarity)
        
        # Fórmula: ((0.3 * 4) + (0.4 * 3) + (0.5 * 3)) / 10 = 0.39
        expected_score = ((completeness * 4) + (coherence * 3) + (semantic_similarity * 3)) / 10
        assert abs(score - expected_score) < 0.01
        assert score < 0.85  # Deve ser inaceitável
    
    def test_calculate_doc_quality_score_boundaries(self, doc_analyzer):
        """Testa cálculo de DocQualityScore nos limites (0 e 1)."""
        # Teste com valores mínimos
        score_min = doc_analyzer.calculate_doc_quality_score(0.0, 0.0, 0.0)
        assert score_min == 0.0
        
        # Teste com valores máximos
        score_max = doc_analyzer.calculate_doc_quality_score(1.0, 1.0, 1.0)
        assert score_max == 1.0
    
    def test_analyze_documentation_complete(self, doc_analyzer, sample_python_code, sample_python_doc):
        """Testa análise completa de documentação."""
        metrics = doc_analyzer.analyze_documentation(
            code=sample_python_code,
            doc=sample_python_doc,
            source_file="test_file.py",
            language="python",
            function_name="calculate_keyword_score",
            module_name="keyword_utils"
        )
        
        # Verificar que métricas foram criadas
        assert isinstance(metrics, DocQualityMetrics)
        assert metrics.source_file == "test_file.py"
        assert metrics.function_name == "calculate_keyword_score"
        assert metrics.module_name == "keyword_utils"
        assert 0.0 <= metrics.completeness <= 1.0
        assert 0.0 <= metrics.coherence <= 1.0
        assert 0.0 <= metrics.semantic_similarity <= 1.0
        assert 0.0 <= metrics.doc_quality_score <= 1.0
        assert metrics.timestamp is not None
        
        # Verificar que foi adicionado ao histórico
        assert len(doc_analyzer.analysis_history) == 1
        assert doc_analyzer.analysis_history[0] == metrics
    
    def test_save_quality_report_success(self, doc_analyzer, sample_python_code, sample_python_doc):
        """Testa salvamento de relatório de qualidade com sucesso."""
        metrics = doc_analyzer.analyze_documentation(
            code=sample_python_code,
            doc=sample_python_doc,
            source_file="test_file.py",
            language="python"
        )
        
        exec_id = "TEST_001"
        report_path = doc_analyzer.save_quality_report(metrics, exec_id)
        
        # Verificar que arquivo foi criado
        assert Path(report_path).exists()
        assert report_path.endswith(".md")
        assert exec_id in report_path
        
        # Verificar conteúdo do relatório
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Relatório de Qualidade de Documentação" in content
            assert exec_id in content
            assert "test_file.py" in content
            assert str(metrics.doc_quality_score) in content
    
    def test_save_quality_report_error(self, doc_analyzer, sample_python_code, sample_python_doc):
        """Testa salvamento de relatório de qualidade com erro."""
        metrics = doc_analyzer.analyze_documentation(
            code=sample_python_code,
            doc=sample_python_doc,
            source_file="test_file.py",
            language="python"
        )
        
        # Forçar erro criando diretório inválido
        doc_analyzer.output_dir = "/invalid/path/that/does/not/exist"
        
        with pytest.raises(Exception):
            doc_analyzer.save_quality_report(metrics, "TEST_001")
    
    def test_get_analysis_summary_empty(self, doc_analyzer):
        """Testa resumo de análises quando não há histórico."""
        summary = doc_analyzer.get_analysis_summary()
        
        assert summary["message"] == "Nenhuma análise realizada ainda"
    
    def test_get_analysis_summary_with_data(self, doc_analyzer, sample_python_code, sample_python_doc):
        """Testa resumo de análises com dados no histórico."""
        # Adicionar algumas análises
        for index in range(3):
            metrics = doc_analyzer.analyze_documentation(
                code=sample_python_code,
                doc=sample_python_doc,
                source_file=f"test_file_{index}.py",
                language="python"
            )
        
        summary = doc_analyzer.get_analysis_summary()
        
        assert summary["total_analyses"] == 3
        assert summary["threshold"] == 0.85
        assert "avg_score" in summary
        assert "min_score" in summary
        assert "max_score" in summary
        assert "acceptable_count" in summary
        assert "acceptance_rate" in summary

class TestDocQualityMetrics:
    """
    Testes para DocQualityMetrics.
    
    Cobre funcionalidades da estrutura de dados.
    """
    
    def test_metrics_creation(self):
        """Testa criação de métricas."""
        metrics = DocQualityMetrics(
            completeness=0.8,
            coherence=0.9,
            semantic_similarity=0.85,
            doc_quality_score=0.85,
            timestamp="2025-01-27T10:00:00",
            source_file="test.py",
            function_name="test_func",
            module_name="test_module"
        )
        
        assert metrics.completeness == 0.8
        assert metrics.coherence == 0.9
        assert metrics.semantic_similarity == 0.85
        assert metrics.doc_quality_score == 0.85
        assert metrics.timestamp == "2025-01-27T10:00:00"
        assert metrics.source_file == "test.py"
        assert metrics.function_name == "test_func"
        assert metrics.module_name == "test_module"
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        metrics = DocQualityMetrics(
            completeness=0.8,
            coherence=0.9,
            semantic_similarity=0.85,
            doc_quality_score=0.85,
            timestamp="2025-01-27T10:00:00",
            source_file="test.py"
        )
        
        data = metrics.to_dict()
        
        assert isinstance(data, dict)
        assert data["completeness"] == 0.8
        assert data["coherence"] == 0.9
        assert data["semantic_similarity"] == 0.85
        assert data["doc_quality_score"] == 0.85
        assert data["timestamp"] == "2025-01-27T10:00:00"
        assert data["source_file"] == "test.py"
    
    def test_is_acceptable_high_score(self):
        """Testa verificação de aceitabilidade com score alto."""
        metrics = DocQualityMetrics(
            completeness=0.9,
            coherence=0.9,
            semantic_similarity=0.9,
            doc_quality_score=0.9,
            timestamp="2025-01-27T10:00:00",
            source_file="test.py"
        )
        
        assert metrics.is_acceptable(0.85) == True
        assert metrics.is_acceptable(0.95) == False
    
    def test_is_acceptable_low_score(self):
        """Testa verificação de aceitabilidade com score baixo."""
        metrics = DocQualityMetrics(
            completeness=0.5,
            coherence=0.5,
            semantic_similarity=0.5,
            doc_quality_score=0.5,
            timestamp="2025-01-27T10:00:00",
            source_file="test.py"
        )
        
        assert metrics.is_acceptable(0.85) == False
        assert metrics.is_acceptable(0.4) == True
    
    def test_is_acceptable_default_threshold(self):
        """Testa verificação de aceitabilidade com threshold padrão."""
        metrics = DocQualityMetrics(
            completeness=0.9,
            coherence=0.9,
            semantic_similarity=0.9,
            doc_quality_score=0.9,
            timestamp="2025-01-27T10:00:00",
            source_file="test.py"
        )
        
        assert metrics.is_acceptable() == True  # Threshold padrão é 0.85

class TestDocQualityAnalyzerIntegration:
    """
    Testes de integração para DocQualityAnalyzer.
    
    Testa cenários mais complexos e interações entre componentes.
    """
    
    @pytest.fixture
    def real_semantic_service(self):
        """Cria serviço semântico real para testes de integração."""
        return SemanticEmbeddingService(threshold=0.85)
    
    @pytest.fixture
    def integration_analyzer(self, temp_output_dir, real_semantic_service):
        """Cria analisador com serviço real para testes de integração."""
        return DocQualityAnalyzer(
            semantic_service=real_semantic_service,
            output_dir=temp_output_dir,
            threshold=0.85
        )
    
    def test_full_workflow_high_quality(self, integration_analyzer):
        """Testa workflow completo com documentação de alta qualidade."""
        code = '''
def process_keywords(keywords: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Processa lista de keywords aplicando configurações específicas.
    
    Args:
        keywords: Lista de keywords para processar
        config: Configurações de processamento
    
    Returns:
        Lista de keywords processadas com métricas
    
    Raises:
        ValueError: Se keywords estiver vazia
        KeyError: Se configuração obrigatória estiver faltando
    
    Examples:
        >>> config = {"min_volume": 100, "max_difficulty": 50}
        >>> keywords = ["python tutorial", "machine learning"]
        >>> result = process_keywords(keywords, config)
        >>> len(result) == 2
        True
    """
    if not keywords:
        raise ValueError("Lista de keywords não pode estar vazia")
    
    if "min_volume" not in config:
        raise KeyError("Configuração 'min_volume' é obrigatória")
    
    processed = []
    for keyword in keywords:
        # Processar keyword
        processed.append({"keyword": keyword, "status": "processed"})
    
    return processed
'''
        
        doc = '''
def process_keywords(keywords: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Processa lista de keywords aplicando configurações específicas.
    
    Args:
        keywords: Lista de keywords para processar
        config: Configurações de processamento
    
    Returns:
        Lista de keywords processadas com métricas
    
    Raises:
        ValueError: Se keywords estiver vazia
        KeyError: Se configuração obrigatória estiver faltando
    
    Examples:
        >>> config = {"min_volume": 100, "max_difficulty": 50}
        >>> keywords = ["python tutorial", "machine learning"]
        >>> result = process_keywords(keywords, config)
        >>> len(result) == 2
        True
    """
'''
        
        # Executar análise completa
        metrics = integration_analyzer.analyze_documentation(
            code=code,
            doc=doc,
            source_file="keyword_processor.py",
            language="python",
            function_name="process_keywords",
            module_name="keyword_processing"
        )
        
        # Verificar que análise foi bem-sucedida
        assert metrics.doc_quality_score > 0.7  # Deve ter boa qualidade
        assert metrics.completeness > 0.8  # Deve ter boa completude
        assert metrics.coherence > 0.8  # Deve ter boa coerência
        assert metrics.semantic_similarity > 0.8  # Deve ter boa similaridade
    
    def test_multiple_languages_support(self, integration_analyzer):
        """Testa suporte a múltiplas linguagens."""
        python_code = '''
def python_function():
    """Python function."""
    pass
'''
        
        typescript_code = '''
function typescriptFunction(): void {
    // TypeScript function
}
'''
        
        python_doc = '''
def python_function():
    """
    Python function.
    
    Returns:
        None
    """
'''
        
        typescript_doc = '''
/**
 * TypeScript function.
 * 
 * @returns void
 */
function typescriptFunction(): void {
'''
        
        # Analisar Python
        python_metrics = integration_analyzer.analyze_documentation(
            code=python_code,
            doc=python_doc,
            source_file="python_file.py",
            language="python"
        )
        
        # Analisar TypeScript
        typescript_metrics = integration_analyzer.analyze_documentation(
            code=typescript_code,
            doc=typescript_doc,
            source_file="typescript_file.ts",
            language="typescript"
        )
        
        # Verificar que ambas as análises foram executadas
        assert python_metrics.doc_quality_score >= 0.0
        assert typescript_metrics.doc_quality_score >= 0.0
        assert len(integration_analyzer.analysis_history) == 2
    
    def test_error_handling_robustness(self, integration_analyzer):
        """Testa robustez no tratamento de erros."""
        # Teste com código malformado
        malformed_code = '''
def broken_function(
    # Comentário sem fechar
    param1: str,
    param2: int
'''
        
        doc = '''
def broken_function(param1: str, param2: int):
    """
    Function documentation.
    """
'''
        
        # Deve não falhar mesmo com código malformado
        metrics = integration_analyzer.analyze_documentation(
            code=malformed_code,
            doc=doc,
            source_file="broken_file.py",
            language="python"
        )
        
        # Deve retornar métricas válidas mesmo com erro
        assert isinstance(metrics, DocQualityMetrics)
        assert 0.0 <= metrics.doc_quality_score <= 1.0

if __name__ == "__main__":
    pytest.main([__file__]) 