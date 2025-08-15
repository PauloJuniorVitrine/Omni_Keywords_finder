"""
Testes Unitários para Validation Service
Serviço de Validação Avançada - Omni Keywords Finder

Prompt: Implementação de testes unitários para serviço de validação
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import re
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from backend.app.services.validation_service import (
    ValidationService,
    DataQualityValidator,
    PromptQualityValidator,
    ValidationResult,
    ValidationSeverity
)
from backend.app.models.prompt_system import (
    Nicho,
    Categoria,
    DadosColetados,
    PromptBase,
    PromptPreenchido,
    LogOperacao
)


class TestValidationSeverity:
    """Testes para enum ValidationSeverity"""
    
    def test_validation_severity_values(self):
        """Testa valores do enum ValidationSeverity"""
        assert ValidationSeverity.INFO.value == "info"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.CRITICAL.value == "critical"


class TestValidationResult:
    """Testes para ValidationResult"""
    
    def test_validation_result_creation(self):
        """Testa criação de ValidationResult"""
        result = ValidationResult(
            is_valid=True,
            score=0.85,
            issues=[{"type": "test", "severity": ValidationSeverity.INFO, "message": "Test"}],
            suggestions=["Suggestion 1", "Suggestion 2"],
            metadata={"key": "value"}
        )
        
        assert result.is_valid is True
        assert result.score == 0.85
        assert len(result.issues) == 1
        assert len(result.suggestions) == 2
        assert result.metadata["key"] == "value"
    
    def test_validation_result_invalid(self):
        """Testa criação de ValidationResult inválido"""
        result = ValidationResult(
            is_valid=False,
            score=0.3,
            issues=[{"type": "error", "severity": ValidationSeverity.ERROR, "message": "Error"}],
            suggestions=["Fix this"],
            metadata={"error_count": 1}
        )
        
        assert result.is_valid is False
        assert result.score == 0.3
        assert len(result.issues) == 1
        assert result.issues[0]["severity"] == ValidationSeverity.ERROR


class TestDataQualityValidator:
    """Testes para DataQualityValidator"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def data_validator(self, mock_db):
        """Instância do DataQualityValidator para testes"""
        return DataQualityValidator(mock_db)
    
    def test_validate_primary_keyword_valid(self, data_validator, mock_db):
        """Testa validação de palavra-chave principal válida"""
        # Mock do nicho
        mock_nicho = Mock()
        mock_nicho.nome = "Tecnologia"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_nicho
        
        # Mock de dados existentes (nenhum)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = data_validator.validate_primary_keyword("software development", 1)
        
        assert result.is_valid is True
        assert result.score >= 0.7
        assert len(result.issues) == 0
        assert "keyword_length" in result.metadata
    
    def test_validate_primary_keyword_empty(self, data_validator, mock_db):
        """Testa validação de palavra-chave vazia"""
        result = data_validator.validate_primary_keyword("", 1)
        
        assert result.is_valid is False
        assert result.score < 0.7
        assert any(issue["type"] == "empty_keyword" for issue in result.issues)
        assert any("não pode estar vazia" in issue["message"] for issue in result.issues)
    
    def test_validate_primary_keyword_too_long(self, data_validator, mock_db):
        """Testa validação de palavra-chave muito longa"""
        long_keyword = "a" * 300
        
        result = data_validator.validate_primary_keyword(long_keyword, 1)
        
        assert result.is_valid is True  # Ainda válida, mas com warning
        assert any(issue["type"] == "keyword_too_long" for issue in result.issues)
        assert any("muito longa" in issue["message"] for issue in result.issues)
    
    def test_validate_primary_keyword_duplicate(self, data_validator, mock_db):
        """Testa validação de palavra-chave duplicada"""
        # Mock de dados existentes
        mock_existing = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing
        
        result = data_validator.validate_primary_keyword("existing_keyword", 1)
        
        assert result.is_valid is True  # Ainda válida, mas com warning
        assert any(issue["type"] == "duplicate_keyword" for issue in result.issues)
        assert any("já existe" in issue["message"] for issue in result.issues)
    
    def test_validate_primary_keyword_low_relevance(self, data_validator, mock_db):
        """Testa validação de palavra-chave com baixa relevância"""
        # Mock do nicho
        mock_nicho = Mock()
        mock_nicho.nome = "Saúde"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_nicho
        
        result = data_validator.validate_primary_keyword("unrelated_keyword", 1)
        
        assert result.is_valid is True  # Ainda válida, mas com warning
        assert any(issue["type"] == "low_relevance" for issue in result.issues)
        assert any("Baixa relevância" in issue["message"] for issue in result.issues)
    
    def test_validate_secondary_keywords_empty(self, data_validator):
        """Testa validação de palavras-chave secundárias vazias"""
        result = data_validator.validate_secondary_keywords("")
        
        assert result.is_valid is True
        assert result.score == 1.0
        assert len(result.issues) == 0
        assert result.metadata["keyword_count"] == 0
    
    def test_validate_secondary_keywords_valid(self, data_validator):
        """Testa validação de palavras-chave secundárias válidas"""
        keywords = "marketing, digital, vendas, conversão"
        
        result = data_validator.validate_secondary_keywords(keywords)
        
        assert result.is_valid is True
        assert result.score >= 0.8
        assert result.metadata["keyword_count"] == 4
    
    def test_validate_secondary_keywords_too_many(self, data_validator):
        """Testa validação de muitas palavras-chave secundárias"""
        keywords = ", ".join([f"keyword_{i}" for i in range(25)])
        
        result = data_validator.validate_secondary_keywords(keywords)
        
        assert result.is_valid is True  # Ainda válida, mas com warning
        assert any(issue["type"] == "too_many_keywords" for issue in result.issues)
        assert any("Muitas palavras-chave" in issue["message"] for issue in result.issues)
    
    def test_validate_secondary_keywords_duplicates(self, data_validator):
        """Testa validação de palavras-chave secundárias duplicadas"""
        keywords = "marketing, digital, marketing, vendas, digital"
        
        result = data_validator.validate_secondary_keywords(keywords)
        
        assert result.is_valid is True  # Ainda válida, mas com warning
        assert any(issue["type"] == "duplicate_secondary_keywords" for issue in result.issues)
        assert any("duplicadas" in issue["message"] for issue in result.issues)
    
    def test_validate_secondary_keywords_short(self, data_validator):
        """Testa validação de palavras-chave secundárias muito curtas"""
        keywords = "a, bb, marketing, digital"
        
        result = data_validator.validate_secondary_keywords(keywords)
        
        assert result.is_valid is True  # Ainda válida, mas com info
        assert any(issue["type"] == "short_keywords" for issue in result.issues)
        assert any("muito curtas" in issue["message"] for issue in result.issues)
    
    def test_validate_cluster_content_valid(self, data_validator):
        """Testa validação de conteúdo de cluster válido"""
        content = "Este é um conteúdo de cluster muito útil e informativo que contém informações relevantes sobre o tópico em questão."
        
        result = data_validator.validate_cluster_content(content)
        
        assert result.is_valid is True
        assert result.score >= 0.7
        assert result.metadata["content_length"] == len(content)
        assert result.metadata["word_count"] > 10
    
    def test_validate_cluster_content_empty(self, data_validator):
        """Testa validação de conteúdo de cluster vazio"""
        result = data_validator.validate_cluster_content("")
        
        assert result.is_valid is False
        assert result.score < 0.7
        assert any(issue["type"] == "empty_content" for issue in result.issues)
        assert any("não pode estar vazio" in issue["message"] for issue in result.issues)
    
    def test_validate_cluster_content_too_short(self, data_validator):
        """Testa validação de conteúdo de cluster muito curto"""
        content = "Conteúdo curto"
        
        result = data_validator.validate_cluster_content(content)
        
        assert result.is_valid is True  # Ainda válido, mas com warning
        assert any(issue["type"] == "content_too_short" for issue in result.issues)
        assert any("muito curto" in issue["message"] for issue in result.issues)
    
    def test_validate_cluster_content_too_long(self, data_validator):
        """Testa validação de conteúdo de cluster muito longo"""
        content = "a" * 2500
        
        result = data_validator.validate_cluster_content(content)
        
        assert result.is_valid is True  # Ainda válido, mas com warning
        assert any(issue["type"] == "content_too_long" for issue in result.issues)
        assert any("muito longo" in issue["message"] for issue in result.issues)
    
    def test_validate_cluster_content_insufficient_words(self, data_validator):
        """Testa validação de conteúdo com poucas palavras"""
        content = "Palavra1 palavra2 palavra3 palavra4 palavra5"
        
        result = data_validator.validate_cluster_content(content)
        
        assert result.is_valid is True  # Ainda válido, mas com warning
        assert any(issue["type"] == "insufficient_words" for issue in result.issues)
        assert any("Poucas palavras" in issue["message"] for issue in result.issues)
    
    def test_check_keyword_relevance_high(self, data_validator):
        """Testa verificação de relevância alta"""
        relevance = data_validator._check_keyword_relevance("software", "Tecnologia")
        
        assert relevance >= 0.6
    
    def test_check_keyword_relevance_low(self, data_validator):
        """Testa verificação de relevância baixa"""
        relevance = data_validator._check_keyword_relevance("unrelated", "Saúde")
        
        assert relevance == 0.3  # Relevância mínima


class TestPromptQualityValidator:
    """Testes para PromptQualityValidator"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def prompt_validator(self, mock_db):
        """Instância do PromptQualityValidator para testes"""
        return PromptQualityValidator(mock_db)
    
    def test_validate_prompt_integrity_valid(self, prompt_validator):
        """Testa validação de integridade de prompt válido"""
        original = "Crie um artigo sobre [tema] para o nicho [nicho]"
        filled = "Crie um artigo sobre marketing digital para o nicho tecnologia"
        
        result = prompt_validator.validate_prompt_integrity(original, filled)
        
        assert result.is_valid is True
        assert result.score >= 0.8
        assert result.metadata["gaps_filled"] == 2
        assert result.metadata["total_gaps"] == 2
    
    def test_validate_prompt_integrity_unfilled_gaps(self, prompt_validator):
        """Testa validação de prompt com lacunas não preenchidas"""
        original = "Crie um artigo sobre [tema] para o nicho [nicho]"
        filled = "Crie um artigo sobre marketing digital para o nicho [nicho]"
        
        result = prompt_validator.validate_prompt_integrity(original, filled)
        
        assert result.is_valid is False
        assert result.score < 0.8
        assert any(issue["type"] == "unfilled_gaps" for issue in result.issues)
        assert any("Lacunas não preenchidas" in issue["message"] for issue in result.issues)
    
    def test_validate_prompt_integrity_content_modified(self, prompt_validator):
        """Testa validação de prompt com conteúdo modificado"""
        original = "Crie um artigo sobre [tema] para o nicho [nicho]"
        filled = "Escreva um texto sobre marketing digital para o nicho tecnologia"
        
        result = prompt_validator.validate_prompt_integrity(original, filled)
        
        assert result.is_valid is True  # Ainda válido, mas com warning
        assert any(issue["type"] == "content_modified" for issue in result.issues)
        assert any("Conteúdo original foi modificado" in issue["message"] for issue in result.issues)
    
    def test_validate_prompt_integrity_too_long(self, prompt_validator):
        """Testa validação de prompt muito longo"""
        original = "Crie um artigo sobre [tema]"
        filled = "a" * 12000
        
        result = prompt_validator.validate_prompt_integrity(original, filled)
        
        assert result.is_valid is True  # Ainda válido, mas com warning
        assert any(issue["type"] == "prompt_too_long" for issue in result.issues)
        assert any("muito longo" in issue["message"] for issue in result.issues)
    
    def test_validate_prompt_integrity_too_short(self, prompt_validator):
        """Testa validação de prompt muito curto"""
        original = "Crie um artigo muito detalhado sobre [tema] para o nicho [nicho] com muitas informações"
        filled = "Crie um artigo sobre marketing"
        
        result = prompt_validator.validate_prompt_integrity(original, filled)
        
        assert result.is_valid is True  # Ainda válido, mas com warning
        assert any(issue["type"] == "prompt_too_short" for issue in result.issues)
        assert any("menor que o original" in issue["message"] for issue in result.issues)
    
    def test_validate_semantic_consistency_valid(self, prompt_validator):
        """Testa validação de consistência semântica válida"""
        # Mock dos dados coletados
        mock_dados = Mock()
        mock_dados.primary_keyword = "marketing digital"
        mock_dados.secondary_keywords = "vendas, conversão, leads"
        mock_dados.cluster_content = "Marketing digital é uma estratégia importante para empresas"
        
        prompt = "Crie um artigo sobre marketing digital que inclua estratégias de vendas e conversão de leads"
        
        result = prompt_validator.validate_semantic_consistency(prompt, mock_dados)
        
        assert result.is_valid is True
        assert result.score >= 0.8
        assert result.metadata["primary_keyword_present"] is True
        assert result.metadata["secondary_keywords_used"] >= 2
    
    def test_validate_semantic_consistency_missing_primary(self, prompt_validator):
        """Testa validação de consistência semântica sem palavra-chave principal"""
        # Mock dos dados coletados
        mock_dados = Mock()
        mock_dados.primary_keyword = "marketing digital"
        mock_dados.secondary_keywords = "vendas, conversão"
        mock_dados.cluster_content = "Marketing digital é importante"
        
        prompt = "Crie um artigo sobre estratégias de negócio"
        
        result = prompt_validator.validate_semantic_consistency(prompt, mock_dados)
        
        assert result.is_valid is True  # Ainda válido, mas com warning
        assert any(issue["type"] == "missing_primary_keyword" for issue in result.issues)
        assert any("Palavra-chave principal não encontrada" in issue["message"] for issue in result.issues)
    
    def test_validate_semantic_consistency_missing_secondary(self, prompt_validator):
        """Testa validação de consistência semântica sem palavras-chave secundárias"""
        # Mock dos dados coletados
        mock_dados = Mock()
        mock_dados.primary_keyword = "marketing digital"
        mock_dados.secondary_keywords = "vendas, conversão, leads"
        mock_dados.cluster_content = "Marketing digital é importante"
        
        prompt = "Crie um artigo sobre marketing digital"
        
        result = prompt_validator.validate_semantic_consistency(prompt, mock_dados)
        
        assert result.is_valid is True  # Ainda válido, mas com info
        assert any(issue["type"] == "missing_secondary_keywords" for issue in result.issues)
        assert any("secundárias não encontradas" in issue["message"] for issue in result.issues)
    
    def test_validate_semantic_consistency_low_cluster_usage(self, prompt_validator):
        """Testa validação de consistência semântica com pouco uso do cluster"""
        # Mock dos dados coletados
        mock_dados = Mock()
        mock_dados.primary_keyword = "marketing digital"
        mock_dados.secondary_keywords = "vendas, conversão"
        mock_dados.cluster_content = "Marketing digital é uma estratégia muito importante para empresas modernas"
        
        prompt = "Crie um artigo sobre marketing digital"
        
        result = prompt_validator.validate_semantic_consistency(prompt, mock_dados)
        
        assert result.is_valid is True  # Ainda válido, mas com info
        assert any(issue["type"] == "low_cluster_content_usage" for issue in result.issues)
        assert any("Pouco conteúdo do cluster" in issue["message"] for issue in result.issues)


class TestValidationService:
    """Testes para ValidationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def validation_service(self, mock_db):
        """Instância do ValidationService para testes"""
        return ValidationService(mock_db)
    
    @pytest.fixture
    def sample_dados_coletados(self):
        """Dados coletados de exemplo para testes"""
        dados = Mock()
        dados.primary_keyword = "marketing digital"
        dados.secondary_keywords = "vendas, conversão, leads"
        dados.cluster_content = "Marketing digital é uma estratégia importante para empresas"
        dados.nicho_id = 1
        return dados
    
    def test_validate_dados_coletados_valid(self, validation_service, sample_dados_coletados, mock_db):
        """Testa validação de dados coletados válidos"""
        # Mock do nicho
        mock_nicho = Mock()
        mock_nicho.nome = "Marketing"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_nicho
        
        result = validation_service.validate_dados_coletados(sample_dados_coletados)
        
        assert result.is_valid is True
        assert result.score >= 0.7
        assert result.metadata["validation_count"] == 3
        assert len(result.metadata["component_scores"]) == 3
    
    def test_validate_dados_coletados_invalid(self, validation_service, mock_db):
        """Testa validação de dados coletados inválidos"""
        # Dados inválidos
        dados = Mock()
        dados.primary_keyword = ""
        dados.secondary_keywords = ""
        dados.cluster_content = ""
        dados.nicho_id = 1
        
        result = validation_service.validate_dados_coletados(dados)
        
        assert result.is_valid is False
        assert result.score < 0.7
        assert len(result.issues) > 0
    
    def test_validate_prompt_preenchido_valid(self, validation_service, mock_db):
        """Testa validação de prompt preenchido válido"""
        # Mock dos dados coletados
        mock_dados = Mock()
        mock_dados.primary_keyword = "marketing digital"
        mock_dados.secondary_keywords = "vendas, conversão"
        mock_dados.cluster_content = "Marketing digital é importante"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_dados
        
        # Mock do prompt preenchido
        prompt = Mock()
        prompt.prompt_original = "Crie um artigo sobre [tema] para [nicho]"
        prompt.prompt_preenchido = "Crie um artigo sobre marketing digital para tecnologia"
        prompt.dados_coletados_id = 1
        
        result = validation_service.validate_prompt_preenchido(prompt)
        
        assert result.is_valid is True
        assert result.score >= 0.8
        assert "integrity_score" in result.metadata
        assert "semantic_score" in result.metadata
    
    def test_validate_prompt_preenchido_missing_data(self, validation_service, mock_db):
        """Testa validação de prompt preenchido sem dados coletados"""
        # Mock sem dados coletados
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        prompt = Mock()
        prompt.dados_coletados_id = 999
        
        result = validation_service.validate_prompt_preenchido(prompt)
        
        assert result.is_valid is False
        assert result.score == 0.0
        assert any(issue["type"] == "missing_data" for issue in result.issues)
        assert any("Dados coletados não encontrados" in issue["message"] for issue in result.issues)
    
    def test_get_validation_report(self, validation_service, mock_db):
        """Testa geração de relatório de validação"""
        # Mock de dados coletados
        mock_dados1 = Mock()
        mock_dados1.id = 1
        mock_dados1.primary_keyword = "marketing"
        mock_dados1.secondary_keywords = "vendas"
        mock_dados1.cluster_content = "Conteúdo válido"
        mock_dados1.nicho_id = 1
        
        mock_dados2 = Mock()
        mock_dados2.id = 2
        mock_dados2.primary_keyword = ""
        mock_dados2.secondary_keywords = ""
        mock_dados2.cluster_content = ""
        mock_dados2.nicho_id = 1
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_dados1, mock_dados2]
        
        # Mock do nicho
        mock_nicho = Mock()
        mock_nicho.nome = "Marketing"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_nicho
        
        report = validation_service.get_validation_report(nicho_id=1)
        
        assert report["total_dados"] == 2
        assert "average_score" in report
        assert "valid_count" in report
        assert "invalid_count" in report
        assert len(report["results"]) == 2
    
    def test_get_validation_report_empty(self, validation_service, mock_db):
        """Testa geração de relatório de validação vazio"""
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        report = validation_service.get_validation_report()
        
        assert report["total_dados"] == 0
        assert report["average_score"] == 0
        assert report["valid_count"] == 0
        assert report["invalid_count"] == 0
        assert len(report["results"]) == 0


class TestValidationServiceIntegration:
    """Testes de integração para ValidationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def validation_service(self, mock_db):
        """Instância do ValidationService para testes"""
        return ValidationService(mock_db)
    
    def test_full_validation_workflow(self, validation_service, mock_db):
        """Testa fluxo completo de validação"""
        # Mock do nicho
        mock_nicho = Mock()
        mock_nicho.nome = "Marketing"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_nicho
        
        # Dados coletados válidos
        dados = Mock()
        dados.primary_keyword = "marketing digital"
        dados.secondary_keywords = "vendas, conversão, leads"
        dados.cluster_content = "Marketing digital é uma estratégia importante para empresas modernas"
        dados.nicho_id = 1
        
        # Validar dados coletados
        dados_result = validation_service.validate_dados_coletados(dados)
        
        assert dados_result.is_valid is True
        assert dados_result.score >= 0.7
        
        # Mock dos dados coletados para prompt
        mock_db.query.return_value.filter.return_value.first.return_value = dados
        
        # Prompt preenchido válido
        prompt = Mock()
        prompt.prompt_original = "Crie um artigo sobre [tema] para o nicho [nicho]"
        prompt.prompt_preenchido = "Crie um artigo sobre marketing digital para o nicho marketing"
        prompt.dados_coletados_id = 1
        
        # Validar prompt preenchido
        prompt_result = validation_service.validate_prompt_preenchido(prompt)
        
        assert prompt_result.is_valid is True
        assert prompt_result.score >= 0.8


class TestValidationServiceErrorHandling:
    """Testes de tratamento de erros para ValidationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def validation_service(self, mock_db):
        """Instância do ValidationService para testes"""
        return ValidationService(mock_db)
    
    def test_database_error_handling(self, validation_service, mock_db):
        """Testa tratamento de erro de banco de dados"""
        # Simular erro de banco
        mock_db.query.side_effect = Exception("Database error")
        
        dados = Mock()
        dados.primary_keyword = "test"
        dados.nicho_id = 1
        
        # Deve levantar exceção
        with pytest.raises(Exception):
            validation_service.validate_dados_coletados(dados)


class TestValidationServicePerformance:
    """Testes de performance para ValidationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados"""
        return Mock()
    
    @pytest.fixture
    def validation_service(self, mock_db):
        """Instância do ValidationService para testes"""
        return ValidationService(mock_db)
    
    def test_multiple_validations_performance(self, validation_service, mock_db):
        """Testa performance de múltiplas validações"""
        import time
        
        # Mock do nicho
        mock_nicho = Mock()
        mock_nicho.nome = "Marketing"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_nicho
        
        start_time = time.time()
        
        # Executar múltiplas validações
        for i in range(100):
            dados = Mock()
            dados.primary_keyword = f"keyword_{i}"
            dados.secondary_keywords = f"secondary_{i}, another_{i}"
            dados.cluster_content = f"Content for keyword {i} with relevant information"
            dados.nicho_id = 1
            
            result = validation_service.validate_dados_coletados(dados)
            assert result.is_valid is True
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        assert end_time - start_time < 5.0  # Menos de 5 segundos para 100 validações


if __name__ == "__main__":
    pytest.main([__file__]) 