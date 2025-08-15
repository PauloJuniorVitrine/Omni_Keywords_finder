from typing import Dict, List, Optional, Any
"""
Testes unitários para ValidadorSemanticoAvancado
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 1.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from infrastructure.processamento.validador_semantico_avancado import (
    ValidadorSemanticoAvancado,
    ValidationResult,
    SemanticContext,
    ValidationSeverity
)
from domain.models import Keyword, Cluster

class TestValidadorSemanticoAvancado:
    """Testes para ValidadorSemanticoAvancado."""
    
    @pytest.fixture
    def validador(self):
        """Fixture para validador."""
        return ValidadorSemanticoAvancado(
            cache_enabled=False,
            similarity_threshold=0.7
        )
    
    @pytest.fixture
    def context(self):
        """Fixture para contexto semântico."""
        return SemanticContext(
            primary_keyword="marketing digital",
            secondary_keywords=["seo", "ads", "social media"],
            cluster_content="Estratégias de marketing digital para empresas",
            intent="commercial",
            funnel_stage="consideration",
            domain="marketing"
        )
    
    @pytest.fixture
    def valid_prompt(self):
        """Fixture para prompt válido."""
        return """
        Você deve gerar um artigo sobre marketing digital.
        
        Palavra-chave principal: marketing digital
        Palavras-chave secundárias: seo, ads, social media
        
        O artigo deve incluir:
        - Introdução sobre marketing digital
        - Estratégias de SEO
        - Campanhas de Google Ads
        - Marketing em redes sociais
        - Conclusão com call-to-action
        
        Estrutura:
        <h1>Marketing Digital: Guia Completo</h1>
        <h2>O que é Marketing Digital</h2>
        <h3>Estratégias de SEO</h3>
        <h3>Google Ads</h3>
        <h3>Redes Sociais</h3>
        <h2>Conclusão</h2>
        """
    
    def test_init(self, validador):
        """Testa inicialização do validador."""
        assert validador.model_name == "all-MiniLM-L6-v2"
        assert validador.cache_enabled is False
        assert validador.similarity_threshold == 0.7
        assert validador.context_weight == 0.3
        assert isinstance(validador.validation_cache, dict)
        assert isinstance(validador.embedding_cache, dict)
    
    def test_validar_prompt_semantico_basico(self, validador, valid_prompt):
        """Testa validação semântica básica."""
        result = validador.validar_prompt_semantico(valid_prompt)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.issues, list)
        assert isinstance(result.suggestions, list)
        assert isinstance(result.metadata, dict)
    
    def test_validar_prompt_muito_curto(self, validador):
        """Testa validação de prompt muito curto."""
        short_prompt = "Texto curto"
        result = validador.validar_prompt_semantico(short_prompt)
        
        assert result.is_valid is False
        assert result.score < 1.0
        
        # Verificar se há issue de prompt muito curto
        short_issues = [index for index in result.issues if index['type'] == 'prompt_too_short']
        assert len(short_issues) > 0
    
    def test_validar_prompt_com_placeholders(self, validador):
        """Testa validação de prompt com placeholders não preenchidos."""
        prompt_with_placeholders = """
        Artigo sobre {primary_keyword}
        Incluir {secondary_keywords}
        Cluster: {cluster_id}
        """
        result = validador.validar_prompt_semantico(prompt_with_placeholders)
        
        assert result.is_valid is False
        assert result.score < 1.0
        
        # Verificar se há issue de placeholders não preenchidos
        placeholder_issues = [index for index in result.issues if index['type'] == 'unfilled_placeholders']
        assert len(placeholder_issues) > 0
    
    def test_validar_prompt_com_contexto(self, validador, valid_prompt, context):
        """Testa validação com contexto semântico."""
        result = validador.validar_prompt_semantico(valid_prompt, context)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert 0.0 <= result.score <= 1.0
    
    def test_validar_prompt_sem_contexto(self, validador, valid_prompt):
        """Testa validação sem contexto semântico."""
        result = validador.validar_prompt_semantico(valid_prompt, context=None)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
    
    def test_validar_prompt_strict_mode(self, validador, valid_prompt):
        """Testa validação em modo estrito."""
        result = validador.validar_prompt_semantico(valid_prompt, strict_mode=True)
        
        assert isinstance(result, ValidationResult)
        # Em modo estrito, o threshold é mais alto
        if result.is_valid:
            assert result.score >= 0.8
    
    def test_cache_functionality(self):
        """Testa funcionalidade de cache."""
        validador = ValidadorSemanticoAvancado(cache_enabled=True)
        prompt = "Teste de cache"
        
        # Primeira validação
        result1 = validador.validar_prompt_semantico(prompt)
        
        # Segunda validação (deve usar cache)
        result2 = validador.validar_prompt_semantico(prompt)
        
        assert result1.score == result2.score
        assert result1.is_valid == result2.is_valid
    
    def test_limpar_cache(self, validador):
        """Testa limpeza do cache."""
        # Adicionar dados ao cache
        validador.validation_cache['test'] = 'data'
        validador.embedding_cache['test'] = 'data'
        
        # Limpar cache
        validador.limpar_cache()
        
        assert len(validador.validation_cache) == 0
        assert len(validador.embedding_cache) == 0
    
    def test_obter_estatisticas(self, validador):
        """Testa obtenção de estatísticas."""
        stats = validador.obter_estatisticas()
        
        assert isinstance(stats, dict)
        assert 'cache_size' in stats
        assert 'embedding_cache_size' in stats
        assert 'nlp_available' in stats
        assert 'model_name' in stats
        assert 'similarity_threshold' in stats
    
    def test_validar_contextual_missing_primary_keyword(self, validador, context):
        """Testa validação contextual com palavra-chave principal ausente."""
        prompt_without_primary = """
        Artigo sobre SEO e marketing.
        Incluir estratégias de otimização.
        """
        result = validador.validar_prompt_semantico(prompt_without_primary, context)
        
        # Deve ter issue de palavra-chave principal ausente
        missing_primary_issues = [index for index in result.issues if index['type'] == 'missing_primary_keyword']
        assert len(missing_primary_issues) > 0
    
    def test_validar_contextual_missing_secondary_keywords(self, validador, context):
        """Testa validação contextual com palavras-chave secundárias ausentes."""
        prompt_without_secondary = """
        Artigo sobre marketing digital.
        Foco em estratégias gerais.
        """
        result = validador.validar_prompt_semantico(prompt_without_secondary, context)
        
        # Deve ter issue de palavras-chave secundárias ausentes
        missing_secondary_issues = [index for index in result.issues if index['type'] == 'missing_secondary_keywords']
        assert len(missing_secondary_issues) > 0
    
    def test_validar_coerencia_repeticao_excessiva(self, validador):
        """Testa validação de coerência com repetição excessiva."""
        repetitive_prompt = """
        marketing marketing marketing marketing marketing
        digital digital digital digital digital digital
        estratégia estratégia estratégia estratégia
        """
        result = validador.validar_prompt_semantico(repetitive_prompt)
        
        # Deve ter issue de repetição excessiva
        repetition_issues = [index for index in result.issues if index['type'] == 'excessive_repetition']
        assert len(repetition_issues) > 0
    
    def test_validar_coerencia_sem_estrutura(self, validador):
        """Testa validação de coerência sem estrutura de títulos."""
        unstructured_prompt = """
        Artigo sobre marketing digital sem estrutura.
        Apenas texto contínuo sem títulos ou subtítulos.
        Conteúdo sem organização adequada.
        """
        result = validador.validar_prompt_semantico(unstructured_prompt)
        
        # Deve ter issue de estrutura ausente
        structure_issues = [index for index in result.issues if index['type'] == 'missing_headings']
        assert len(structure_issues) > 0
    
    def test_gerar_sugestoes(self, validador):
        """Testa geração de sugestões."""
        # Prompt com problemas
        problematic_prompt = "Texto curto"
        result = validador.validar_prompt_semantico(problematic_prompt)
        
        assert len(result.suggestions) > 0
        assert all(isinstance(string_data, str) for string_data in result.suggestions)
    
    def test_gerar_sugestoes_score_baixo(self, validador):
        """Testa geração de sugestões para score baixo."""
        # Mock de resultado com score baixo
        issues = [{'type': 'prompt_too_short'}]
        suggestions = validador._gerar_sugestoes(issues, 0.3)
        
        assert "Considere revisar completamente o prompt" in suggestions
    
    @patch('infrastructure.processamento.validador_semantico_avancado.NLP_AVAILABLE', True)
    def test_validar_semantico_com_nlp(self, validador, valid_prompt, context):
        """Testa validação semântica com NLP disponível."""
        # Mock do modelo de embeddings
        with patch.object(validador, '_get_embedding') as mock_embedding:
            mock_embedding.return_value = [0.1] * 384  # Embedding simulado
            
            result = validador.validar_prompt_semantico(valid_prompt, context)
            
            assert isinstance(result, ValidationResult)
            assert mock_embedding.called
    
    def test_validar_semantico_sem_nlp(self, validador, valid_prompt, context):
        """Testa validação semântica sem NLP disponível."""
        with patch('infrastructure.processamento.validador_semantico_avancado.NLP_AVAILABLE', False):
            result = validador.validar_prompt_semantico(valid_prompt, context)
            
            assert isinstance(result, ValidationResult)
            # Deve funcionar mesmo sem NLP
    
    def test_generate_cache_key(self, validador, context):
        """Testa geração de chave de cache."""
        prompt = "Teste de cache"
        strict_mode = True
        
        key1 = validador._generate_cache_key(prompt, context, strict_mode)
        key2 = validador._generate_cache_key(prompt, context, strict_mode)
        
        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) == 32  # MD5 hash length
    
    def test_get_embedding_cache(self, validador):
        """Testa cache de embeddings."""
        text = "Teste de embedding"
        
        # Primeira chamada
        embedding1 = validador._get_embedding(text)
        
        # Segunda chamada (deve usar cache)
        embedding2 = validador._get_embedding(text)
        
        # Verificar se o embedding foi armazenado no cache
        text_hash = validador._generate_cache_key(text, None, False)
        assert text_hash in validador.embedding_cache
    
    def test_validation_metadata(self, validador, valid_prompt):
        """Testa metadados da validação."""
        result = validador.validar_prompt_semantico(valid_prompt)
        
        metadata = result.metadata
        assert 'validation_time' in metadata
        assert 'prompt_length' in metadata
        assert 'word_count' in metadata
        assert 'nlp_available' in metadata
        assert 'cache_hit' in metadata
        assert 'strict_mode' in metadata
        
        assert isinstance(metadata['validation_time'], float)
        assert isinstance(metadata['prompt_length'], int)
        assert isinstance(metadata['word_count'], int)
        assert isinstance(metadata['nlp_available'], bool)
        assert isinstance(metadata['cache_hit'], bool)
        assert isinstance(metadata['strict_mode'], bool)
    
    def test_validation_severity_levels(self, validador):
        """Testa níveis de severidade."""
        # Prompt com erro crítico
        short_prompt = "Curto"
        result = validador.validar_prompt_semantico(short_prompt)
        
        error_issues = [index for index in result.issues if index['severity'] == ValidationSeverity.ERROR]
        warning_issues = [index for index in result.issues if index['severity'] == ValidationSeverity.WARNING]
        
        assert len(error_issues) > 0 or len(warning_issues) > 0
    
    def test_validation_patterns(self, validador):
        """Testa padrões de validação."""
        patterns = validador.validation_patterns
        
        assert 'keyword_density' in patterns
        assert 'placeholder_format' in patterns
        assert 'html_tags' in patterns
        assert 'url_pattern' in patterns
        assert 'email_pattern' in patterns
        
        # Testar regex patterns
        import re
        
        # Testar placeholder format
        test_placeholder = "{primary_keyword}"
        assert re.search(patterns['placeholder_format'], test_placeholder)
        
        # Testar HTML tags
        test_html = "<h1>Título</h1>"
        assert re.search(patterns['html_tags'], test_html)
        
        # Testar URL pattern
        test_url = "https://example.com"
        assert re.search(patterns['url_pattern'], test_url)
        
        # Testar email pattern
        test_email = "test@example.com"
        assert re.search(patterns['email_pattern'], test_email) 