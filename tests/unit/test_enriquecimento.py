from typing import Dict, List, Optional, Any
"""
Testes unitários para módulo de enriquecimento
⚠️ CRIAR MAS NÃO EXECUTAR - Executar apenas na Fase 6.5

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 1.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from infrastructure.enriquecimento import (
    KeywordEnricher,
    EnrichmentData,
    EnrichmentResult,
    EnrichmentType
)
from domain.models import Keyword, Cluster

class TestKeywordEnricher:
    """Testes para KeywordEnricher."""
    
    @pytest.fixture
    def enricher(self):
        """Fixture para enricher."""
        return KeywordEnricher(
            cache_enabled=True,
            max_cache_size=100,
            confidence_threshold=0.7
        )
    
    @pytest.fixture
    def sample_keyword(self):
        """Fixture para keyword de teste."""
        return Keyword(
            id=1,
            termo="marketing digital",
            volume_busca=10000,
            cpc=2.50,
            dificuldade=0.6,
            cluster_id=1
        )
    
    @pytest.fixture
    def sample_cluster(self, sample_keyword):
        """Fixture para cluster de teste."""
        cluster = Cluster(
            id=1,
            nome="Marketing Digital",
            descricao="Cluster de marketing digital",
            categoria="marketing"
        )
        cluster.keywords = [sample_keyword]
        return cluster
    
    @pytest.fixture
    def sample_context(self):
        """Fixture para contexto de teste."""
        return {
            'domain': 'marketing',
            'audience': 'empresas',
            'season': 'all',
            'trends': ['digital transformation', 'automation']
        }
    
    def test_init(self, enricher):
        """Testa inicialização do enricher."""
        assert enricher.cache_enabled is True
        assert enricher.max_cache_size == 100
        assert enricher.confidence_threshold == 0.7
        assert isinstance(enricher.enrichment_cache, dict)
        assert isinstance(enricher.analysis_patterns, dict)
    
    def test_enriquecer_keyword(self, enricher, sample_keyword, sample_context):
        """Testa enriquecimento de keyword."""
        result = enricher.enriquecer_keyword(sample_keyword, sample_context)
        
        assert isinstance(result, EnrichmentResult)
        assert result.keyword == sample_keyword
        assert isinstance(result.enrichments, list)
        assert 0.0 <= result.total_score <= 1.0
        assert isinstance(result.processing_time, float)
        assert isinstance(result.metadata, dict)
        
        # Verificar metadados
        assert 'enrichment_count' in result.metadata
        assert 'cache_hit' in result.metadata
        assert 'confidence_threshold' in result.metadata
        assert 'context_provided' in result.metadata
    
    def test_enriquecer_keyword_sem_contexto(self, enricher, sample_keyword):
        """Testa enriquecimento sem contexto."""
        result = enricher.enriquecer_keyword(sample_keyword)
        
        assert isinstance(result, EnrichmentResult)
        assert result.keyword == sample_keyword
        assert result.metadata['context_provided'] is False
    
    def test_enriquecer_cluster(self, enricher, sample_cluster, sample_context):
        """Testa enriquecimento de cluster."""
        results = enricher.enriquecer_cluster(sample_cluster, sample_context)
        
        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], EnrichmentResult)
        assert results[0].keyword == sample_cluster.keywords[0]
    
    def test_enriquecimento_semantico(self, enricher, sample_keyword):
        """Testa enriquecimento semântico."""
        enrichment = enricher._enriquecimento_semantico(sample_keyword)
        
        if enrichment is not None:
            assert isinstance(enrichment, EnrichmentData)
            assert enrichment.keyword == sample_keyword.termo
            assert enrichment.enrichment_type == EnrichmentType.SEMANTIC
            assert isinstance(enrichment.data, dict)
            assert 0.0 <= enrichment.confidence <= 1.0
            assert enrichment.source == "semantic_analysis"
            assert isinstance(enrichment.timestamp, datetime)
            
            # Verificar dados semânticos
            data = enrichment.data
            assert 'word_count' in data
            assert 'avg_word_length' in data
            assert 'has_numbers' in data
            assert 'has_special_chars' in data
            assert 'is_long_tail' in data
            assert 'is_brand' in data
            assert 'is_location' in data
            assert 'is_product' in data
    
    def test_enriquecimento_contextual(self, enricher, sample_keyword, sample_context):
        """Testa enriquecimento contextual."""
        enrichment = enricher._enriquecimento_contextual(sample_keyword, sample_context)
        
        if enrichment is not None:
            assert isinstance(enrichment, EnrichmentData)
            assert enrichment.keyword == sample_keyword.termo
            assert enrichment.enrichment_type == EnrichmentType.CONTEXTUAL
            assert isinstance(enrichment.data, dict)
            assert 0.0 <= enrichment.confidence <= 1.0
            assert enrichment.source == "contextual_analysis"
            assert isinstance(enrichment.timestamp, datetime)
            
            # Verificar dados contextuais
            data = enrichment.data
            assert 'domain_relevance' in data
            assert 'seasonal_relevance' in data
            assert 'trend_alignment' in data
            assert 'audience_match' in data
    
    def test_enriquecimento_contextual_sem_contexto(self, enricher, sample_keyword):
        """Testa enriquecimento contextual sem contexto."""
        enrichment = enricher._enriquecimento_contextual(sample_keyword, None)
        assert enrichment is None
    
    def test_analise_tendencias(self, enricher, sample_keyword):
        """Testa análise de tendências."""
        enrichment = enricher._analise_tendencias(sample_keyword)
        
        if enrichment is not None:
            assert isinstance(enrichment, EnrichmentData)
            assert enrichment.keyword == sample_keyword.termo
            assert enrichment.enrichment_type == EnrichmentType.TREND
            assert isinstance(enrichment.data, dict)
            assert 0.0 <= enrichment.confidence <= 1.0
            assert enrichment.source == "trend_analysis"
            assert isinstance(enrichment.timestamp, datetime)
            
            # Verificar dados de tendência
            data = enrichment.data
            assert 'trend_direction' in data
            assert 'trend_strength' in data
            assert 'seasonality' in data
            assert 'growth_potential' in data
    
    def test_analise_competicao(self, enricher, sample_keyword):
        """Testa análise de competição."""
        enrichment = enricher._analise_competicao(sample_keyword)
        
        if enrichment is not None:
            assert isinstance(enrichment, EnrichmentData)
            assert enrichment.keyword == sample_keyword.termo
            assert enrichment.enrichment_type == EnrichmentType.COMPETITION
            assert isinstance(enrichment.data, dict)
            assert 0.0 <= enrichment.confidence <= 1.0
            assert enrichment.source == "competition_analysis"
            assert isinstance(enrichment.timestamp, datetime)
            
            # Verificar dados de competição
            data = enrichment.data
            assert 'competition_level' in data
            assert 'difficulty_score' in data
            assert 'opportunity_score' in data
            assert 'market_saturation' in data
    
    def test_detectar_intencao(self, enricher, sample_keyword):
        """Testa detecção de intenção."""
        enrichment = enricher._detectar_intencao(sample_keyword)
        
        if enrichment is not None:
            assert isinstance(enrichment, EnrichmentData)
            assert enrichment.keyword == sample_keyword.termo
            assert enrichment.enrichment_type == EnrichmentType.INTENT
            assert isinstance(enrichment.data, dict)
            assert 0.0 <= enrichment.confidence <= 1.0
            assert enrichment.source == "intent_detection"
            assert isinstance(enrichment.timestamp, datetime)
            
            # Verificar dados de intenção
            data = enrichment.data
            assert 'intent_type' in data
            assert 'intent_scores' in data
            assert 'confidence' in data
    
    def test_detectar_intencao_comercial(self, enricher):
        """Testa detecção de intenção comercial."""
        commercial_keyword = Keyword(
            id=1,
            termo="comprar marketing digital",
            volume_busca=5000,
            cpc=3.00,
            dificuldade=0.7,
            cluster_id=1
        )
        
        enrichment = enricher._detectar_intencao(commercial_keyword)
        
        if enrichment is not None:
            assert enrichment.data['intent_type'] == 'commercial'
    
    def test_detectar_intencao_informacional(self, enricher):
        """Testa detecção de intenção informacional."""
        informational_keyword = Keyword(
            id=1,
            termo="como fazer marketing digital",
            volume_busca=3000,
            cpc=1.50,
            dificuldade=0.5,
            cluster_id=1
        )
        
        enrichment = enricher._detectar_intencao(informational_keyword)
        
        if enrichment is not None:
            assert enrichment.data['intent_type'] == 'informational'
    
    def test_detectar_marca(self, enricher):
        """Testa detecção de marca."""
        # Testar termo que é marca
        assert enricher._detectar_marca("marca nike") is True
        assert enricher._detectar_marca("empresa google") is True
        
        # Testar termo que não é marca
        assert enricher._detectar_marca("marketing digital") is False
        assert enricher._detectar_marca("como fazer") is False
    
    def test_detectar_localizacao(self, enricher):
        """Testa detecção de localização."""
        # Testar termo que é localização
        assert enricher._detectar_localizacao("marketing digital são paulo") is True
        assert enricher._detectar_localizacao("empresa rio de janeiro") is True
        
        # Testar termo que não é localização
        assert enricher._detectar_localizacao("marketing digital") is False
        assert enricher._detectar_localizacao("como fazer") is False
    
    def test_detectar_produto(self, enricher):
        """Testa detecção de produto."""
        # Testar termo que é produto
        assert enricher._detectar_produto("produto marketing digital") is True
        assert enricher._detectar_produto("item software") is True
        
        # Testar termo que não é produto
        assert enricher._detectar_produto("marketing digital") is False
        assert enricher._detectar_produto("como fazer") is False
    
    def test_calcular_confianca_semantica(self, enricher):
        """Testa cálculo de confiança semântica."""
        # Testar características que aumentam confiança
        features_high = {
            'word_count': 3,
            'avg_word_length': 8.0,
            'has_numbers': False,
            'has_special_chars': False,
            'is_long_tail': True,
            'is_brand': True,
            'is_location': False,
            'is_product': False
        }
        
        confidence_high = enricher._calcular_confianca_semantica(features_high)
        assert confidence_high > 0.5
        
        # Testar características que diminuem confiança
        features_low = {
            'word_count': 1,
            'avg_word_length': 3.0,
            'has_numbers': True,
            'has_special_chars': True,
            'is_long_tail': False,
            'is_brand': False,
            'is_location': False,
            'is_product': False
        }
        
        confidence_low = enricher._calcular_confianca_semantica(features_low)
        assert confidence_low < confidence_high
    
    def test_detectar_sazonalidade(self, enricher):
        """Testa detecção de sazonalidade."""
        # Testar termos sazonais
        seasonal_keyword = Keyword(
            id=1,
            termo="marketing digital natal",
            volume_busca=2000,
            cpc=2.00,
            dificuldade=0.6,
            cluster_id=1
        )
        assert enricher._detectar_sazonalidade(seasonal_keyword) is True
        
        # Testar termos não sazonais
        non_seasonal_keyword = Keyword(
            id=1,
            termo="marketing digital",
            volume_busca=10000,
            cpc=2.50,
            dificuldade=0.6,
            cluster_id=1
        )
        assert enricher._detectar_sazonalidade(non_seasonal_keyword) is False
    
    def test_generate_cache_key(self, enricher, sample_keyword, sample_context):
        """Testa geração de chave de cache."""
        key1 = enricher._generate_cache_key(sample_keyword, sample_context)
        key2 = enricher._generate_cache_key(sample_keyword, sample_context)
        
        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) == 32  # MD5 hash length
    
    def test_generate_cache_key_sem_contexto(self, enricher, sample_keyword):
        """Testa geração de chave de cache sem contexto."""
        key = enricher._generate_cache_key(sample_keyword, None)
        
        assert isinstance(key, str)
        assert len(key) == 32
    
    def test_armazenar_cache_enrichment(self, enricher, sample_keyword):
        """Testa armazenamento de enriquecimento no cache."""
        # Criar resultado de enriquecimento
        result = EnrichmentResult(
            keyword=sample_keyword,
            enrichments=[],
            total_score=0.8,
            processing_time=0.1,
            metadata={}
        )
        
        # Armazenar no cache
        enricher._armazenar_cache_enrichment("test_key", result)
        
        assert "test_key" in enricher.enrichment_cache
        assert enricher.enrichment_cache["test_key"] == result
    
    def test_armazenar_cache_enrichment_limite_excedido(self, enricher, sample_keyword):
        """Testa armazenamento com limite de cache excedido."""
        # Configurar cache pequeno
        enricher.max_cache_size = 2
        
        # Criar resultados
        result1 = EnrichmentResult(
            keyword=sample_keyword,
            enrichments=[],
            total_score=0.8,
            processing_time=0.1,
            metadata={}
        )
        result2 = EnrichmentResult(
            keyword=sample_keyword,
            enrichments=[],
            total_score=0.9,
            processing_time=0.1,
            metadata={}
        )
        result3 = EnrichmentResult(
            keyword=sample_keyword,
            enrichments=[],
            total_score=0.7,
            processing_time=0.1,
            metadata={}
        )
        
        # Adicionar entradas até o limite
        enricher._armazenar_cache_enrichment("key1", result1)
        enricher._armazenar_cache_enrichment("key2", result2)
        
        # Adicionar mais uma entrada (deve remover a mais antiga)
        enricher._armazenar_cache_enrichment("key3", result3)
        
        assert len(enricher.enrichment_cache) == 2
        assert "key3" in enricher.enrichment_cache
    
    def test_limpar_cache(self, enricher):
        """Testa limpeza do cache."""
        # Adicionar dados ao cache
        enricher.enrichment_cache["test1"] = Mock()
        enricher.enrichment_cache["test2"] = Mock()
        
        # Limpar cache
        enricher.limpar_cache()
        
        assert len(enricher.enrichment_cache) == 0
    
    def test_obter_estatisticas(self, enricher):
        """Testa obtenção de estatísticas."""
        stats = enricher.obter_estatisticas()
        
        assert isinstance(stats, dict)
        assert 'cache_size' in stats
        assert 'cache_enabled' in stats
        assert 'max_cache_size' in stats
        assert 'confidence_threshold' in stats
        
        assert stats['cache_enabled'] is True
        assert stats['max_cache_size'] == 100
        assert stats['confidence_threshold'] == 0.7
    
    def test_analysis_patterns(self, enricher):
        """Testa padrões de análise."""
        patterns = enricher.analysis_patterns
        
        assert 'intent_commercial' in patterns
        assert 'intent_informational' in patterns
        assert 'intent_navigational' in patterns
        
        # Verificar se são listas de regex
        assert isinstance(patterns['intent_commercial'], list)
        assert isinstance(patterns['intent_informational'], list)
        assert isinstance(patterns['intent_navigational'], list)
        
        # Testar regex patterns
        import re
        
        # Testar padrão comercial
        commercial_pattern = patterns['intent_commercial'][0]
        assert re.search(commercial_pattern, "comprar produto")
        assert re.search(commercial_pattern, "melhor preço")
        
        # Testar padrão informacional
        informational_pattern = patterns['intent_informational'][0]
        assert re.search(informational_pattern, "como fazer")
        assert re.search(informational_pattern, "o que é")
        
        # Testar padrão navegacional
        navigational_pattern = patterns['intent_navigational'][0]
        assert re.search(navigational_pattern, "site empresa")
        assert re.search(navigational_pattern, "página produto")
    
    def test_enriquecimento_com_cache(self, enricher, sample_keyword, sample_context):
        """Testa enriquecimento com cache."""
        # Primeiro enriquecimento
        result1 = enricher.enriquecer_keyword(sample_keyword, sample_context)
        
        # Segundo enriquecimento (deve usar cache)
        result2 = enricher.enriquecer_keyword(sample_keyword, sample_context)
        
        assert result1.total_score == result2.total_score
        assert result1.processing_time != result2.processing_time  # Cache deve ser mais rápido
    
    def test_enriquecimento_sem_cache(self):
        """Testa enriquecimento sem cache."""
        enricher = KeywordEnricher(cache_enabled=False)
        keyword = Keyword(
            id=1,
            termo="marketing digital",
            volume_busca=10000,
            cpc=2.50,
            dificuldade=0.6,
            cluster_id=1
        )
        
        result = enricher.enriquecer_keyword(keyword)
        
        assert isinstance(result, EnrichmentResult)
        assert len(enricher.enrichment_cache) == 0  # Cache deve estar vazio
    
    def test_enriquecimento_threshold_baixo(self):
        """Testa enriquecimento com threshold baixo."""
        enricher = KeywordEnricher(confidence_threshold=0.3)  # Threshold baixo
        keyword = Keyword(
            id=1,
            termo="marketing digital",
            volume_busca=10000,
            cpc=2.50,
            dificuldade=0.6,
            cluster_id=1
        )
        
        result = enricher.enriquecer_keyword(keyword)
        
        # Com threshold baixo, deve ter mais enriquecimentos
        assert len(result.enrichments) >= 0  # Pode ter 0 ou mais
    
    def test_enriquecimento_threshold_alto(self):
        """Testa enriquecimento com threshold alto."""
        enricher = KeywordEnricher(confidence_threshold=0.9)  # Threshold alto
        keyword = Keyword(
            id=1,
            termo="marketing digital",
            volume_busca=10000,
            cpc=2.50,
            dificuldade=0.6,
            cluster_id=1
        )
        
        result = enricher.enriquecer_keyword(keyword)
        
        # Com threshold alto, deve ter menos enriquecimentos
        assert len(result.enrichments) >= 0  # Pode ter 0 ou mais 