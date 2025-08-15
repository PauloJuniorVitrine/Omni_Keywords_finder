from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Otimização de Prompts
=====================================================

Testes abrangentes para o sistema de IA Generativa de otimização de prompts.

Tracing ID: AI_GEN_TEST_001
Data: 2024-12-19
Autor: Sistema de Testes
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from infrastructure.ai.generativa.prompt_optimizer import (
    PromptOptimizer,
    OpenAIProvider,
    ClaudeProvider,
    OptimizationStrategy,
    PromptMetrics,
    PromptFeedback,
    PromptTemplate,
    PromptQuality,
    DeepSeekProvider
)
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager


class TestOpenAIProvider:
    """Testes para o provedor OpenAI."""
    
    @pytest.fixture
    def provider(self):
        """Cria instância do provedor OpenAI para testes."""
        return OpenAIProvider("test-api-key", "gpt-4")
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, provider):
        """Testa geração de resposta bem-sucedida."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "choices": [{"message": {"content": "Resposta de teste"}}]
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await provider.generate_response("Teste de prompt")
            
            assert result == "Resposta de teste"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_error(self, provider):
        """Testa erro na geração de resposta."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="OpenAI API error: 400"):
                await provider.generate_response("Teste de prompt")
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, provider):
        """Testa análise de sentimento."""
        with patch.object(provider, 'generate_response') as mock_generate:
            mock_generate.return_value = "0.8"
            
            result = await provider.analyze_sentiment("Texto positivo")
            
            assert result == 0.8
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_invalid_response(self, provider):
        """Testa análise de sentimento com resposta inválida."""
        with patch.object(provider, 'generate_response') as mock_generate:
            mock_generate.return_value = "inválido"
            
            result = await provider.analyze_sentiment("Texto")
            
            assert result == 0.0
    
    @pytest.mark.asyncio
    async def test_extract_keywords(self, provider):
        """Testa extração de keywords."""
        with patch.object(provider, 'generate_response') as mock_generate:
            mock_generate.return_value = "palavra1, palavra2, palavra3"
            
            result = await provider.extract_keywords("Texto com palavras-chave")
            
            assert result == ["palavra1", "palavra2", "palavra3"]
            mock_generate.assert_called_once()


class TestClaudeProvider:
    """Testes para o provedor Claude."""
    
    @pytest.fixture
    def provider(self):
        """Cria instância do provedor Claude para testes."""
        return ClaudeProvider("test-api-key", "claude-3-sonnet-20240229")
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, provider):
        """Testa geração de resposta bem-sucedida."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "content": [{"text": "Resposta de teste"}]
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await provider.generate_response("Teste de prompt")
            
            assert result == "Resposta de teste"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_error(self, provider):
        """Testa erro na geração de resposta."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="Claude API error: 400"):
                await provider.generate_response("Teste de prompt")


class TestDeepSeekProvider:
    """Testes para o provedor DeepSeek."""
    
    @pytest.fixture
    def provider(self):
        """Cria instância do provedor DeepSeek para testes."""
        return DeepSeekProvider("test-api-key", "deepseek-coder-v2.0")
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, provider):
        """Testa geração de resposta bem-sucedida."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "choices": [{"message": {"content": "Resposta DeepSeek"}}]
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await provider.generate_response("Teste de prompt")
            
            assert result == "Resposta DeepSeek"
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_response_error(self, provider):
        """Testa erro na geração de resposta."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="DeepSeek API error: 400"):
                await provider.generate_response("Teste de prompt")
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, provider):
        """Testa análise de sentimento."""
        with patch.object(provider, 'generate_response') as mock_generate:
            mock_generate.return_value = "0.7"
            
            result = await provider.analyze_sentiment("Texto positivo")
            
            assert result == 0.7
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_keywords(self, provider):
        """Testa extração de keywords."""
        with patch.object(provider, 'generate_response') as mock_generate:
            mock_generate.return_value = "palavra1, palavra2, palavra3"
            
            result = await provider.extract_keywords("Texto com palavras-chave")
            
            assert result == ["palavra1", "palavra2", "palavra3"]
            mock_generate.assert_called_once()


class TestPromptMetrics:
    """Testes para métricas de prompt."""
    
    def test_overall_score_calculation(self):
        """Testa cálculo do score geral."""
        metrics = PromptMetrics(
            response_time=2.0,
            token_usage=500,
            relevance_score=0.8,
            diversity_score=0.7,
            user_satisfaction=0.9,
            conversion_rate=0.6
        )
        
        score = metrics.overall_score
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Score deve ser positivo para métricas boas
    
    def test_overall_score_with_poor_metrics(self):
        """Testa score geral com métricas ruins."""
        metrics = PromptMetrics(
            response_time=10.0,  # Muito lento
            token_usage=2000,    # Muitos tokens
            relevance_score=0.2, # Baixa relevância
            diversity_score=0.1, # Baixa diversidade
            user_satisfaction=0.1, # Baixa satisfação
            conversion_rate=0.1   # Baixa conversão
        )
        
        score = metrics.overall_score
        
        assert 0.0 <= score <= 1.0
        assert score < 0.5  # Score deve ser baixo para métricas ruins


class TestPromptFeedback:
    """Testes para feedback de prompt."""
    
    def test_satisfaction_score_calculation(self):
        """Testa cálculo do score de satisfação."""
        feedback = PromptFeedback(
            prompt_id="test_prompt",
            user_id="test_user",
            rating=5,
            comment="Excelente prompt!",
            keywords_generated=20,
            keywords_used=18
        )
        
        score = feedback.satisfaction_score
        
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Score alto para feedback positivo
    
    def test_satisfaction_score_with_low_usage(self):
        """Testa score de satisfação com baixo uso."""
        feedback = PromptFeedback(
            prompt_id="test_prompt",
            user_id="test_user",
            rating=3,
            comment="Prompt ok",
            keywords_generated=20,
            keywords_used=5  # Baixo uso
        )
        
        score = feedback.satisfaction_score
        
        assert 0.0 <= score <= 1.0
        assert score < 0.6  # Score menor devido ao baixo uso


class TestPromptTemplate:
    """Testes para template de prompt."""
    
    def test_template_creation(self):
        """Testa criação de template."""
        template = PromptTemplate(
            id="test_template",
            name="Template de Teste",
            template="Teste {variable}",
            variables=["variable"],
            category="test"
        )
        
        assert template.id == "test_template"
        assert template.name == "Template de Teste"
        assert template.variables == ["variable"]
        assert template.category == "test"


class TestPromptOptimizer:
    """Testes para o otimizador de prompts."""
    
    @pytest.fixture
    def mock_provider(self):
        """Cria provedor mock para testes."""
        provider = MagicMock()
        provider.generate_response = AsyncMock(return_value="Prompt otimizado")
        provider.analyze_sentiment = AsyncMock(return_value=0.8)
        provider.extract_keywords = AsyncMock(return_value=["keyword1", "keyword2"])
        return provider
    
    @pytest.fixture
    def optimizer(self, mock_provider):
        """Cria otimizador para testes."""
        return PromptOptimizer(mock_provider)
    
    @pytest.mark.asyncio
    async def test_optimize_prompt_performance_based(self, optimizer):
        """Testa otimização baseada em performance."""
        original_prompt = "Prompt original para teste"
        
        result, metrics = await optimizer.optimize_prompt(
            original_prompt,
            strategy=OptimizationStrategy.PERFORMANCE_BASED
        )
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
        assert metrics.response_time > 0
    
    @pytest.mark.asyncio
    async def test_optimize_prompt_feedback_based(self, optimizer):
        """Testa otimização baseada em feedback."""
        original_prompt = "Prompt original para teste"
        
        result, metrics = await optimizer.optimize_prompt(
            original_prompt,
            strategy=OptimizationStrategy.FEEDBACK_BASED
        )
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
    
    @pytest.mark.asyncio
    async def test_optimize_prompt_semantic_based(self, optimizer):
        """Testa otimização baseada em semântica."""
        original_prompt = "Prompt original para teste"
        
        result, metrics = await optimizer.optimize_prompt(
            original_prompt,
            strategy=OptimizationStrategy.SEMANTIC_BASED
        )
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
    
    @pytest.mark.asyncio
    async def test_optimize_prompt_hybrid(self, optimizer):
        """Testa otimização híbrida."""
        original_prompt = "Prompt original para teste"
        
        result, metrics = await optimizer.optimize_prompt(
            original_prompt,
            strategy=OptimizationStrategy.HYBRID
        )
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
    
    @pytest.mark.asyncio
    async def test_optimize_prompt_with_context(self, optimizer):
        """Testa otimização com contexto."""
        original_prompt = "Prompt original"
        context = {"topic": "tecnologia", "language": "português"}
        
        result, metrics = await optimizer.optimize_prompt(
            original_prompt,
            context=context
        )
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, optimizer):
        """Testa funcionalidade de cache."""
        original_prompt = "Prompt para cache"
        
        # Primeira otimização
        result1, metrics1 = await optimizer.optimize_prompt(original_prompt)
        
        # Segunda otimização (deve usar cache)
        result2, metrics2 = await optimizer.optimize_prompt(original_prompt)
        
        assert result1 == result2
        assert metrics1.overall_score == metrics2.overall_score
    
    @pytest.mark.asyncio
    async def test_add_feedback(self, optimizer):
        """Testa adição de feedback."""
        feedback = PromptFeedback(
            prompt_id="test_prompt",
            user_id="test_user",
            rating=4,
            comment="Bom prompt",
            keywords_generated=15,
            keywords_used=12
        )
        
        await optimizer.add_feedback(feedback)
        
        # Verificar se feedback foi adicionado
        assert len(optimizer.feedback_history) > 0
    
    @pytest.mark.asyncio
    async def test_get_optimization_stats(self, optimizer):
        """Testa obtenção de estatísticas."""
        # Adicionar algumas otimizações
        await optimizer.optimize_prompt("Prompt 1")
        await optimizer.optimize_prompt("Prompt 2")
        
        stats = await optimizer.get_optimization_stats()
        
        assert "total_optimizations" in stats
        assert "average_score" in stats
        assert "cache_hit_rate" in stats
        assert "most_used_strategy" in stats
        assert stats["total_optimizations"] >= 2
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, optimizer):
        """Testa limpeza de cache."""
        # Adicionar otimização para popular cache
        await optimizer.optimize_prompt("Prompt para cache")
        
        # Verificar que cache não está vazio
        assert len(optimizer.prompt_cache) > 0
        
        # Limpar cache
        await optimizer.clear_cache()
        
        # Verificar que cache está vazio
        assert len(optimizer.prompt_cache) == 0
    
    @pytest.mark.asyncio
    async def test_close_optimizer(self, optimizer):
        """Testa fechamento do otimizador."""
        # Simular sessão
        optimizer.llm_provider.session = AsyncMock()
        
        await optimizer.close()
        
        # Verificar se sessão foi fechada
        optimizer.llm_provider.session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_invalid_optimization_strategy(self, optimizer):
        """Testa estratégia de otimização inválida."""
        original_prompt = "Prompt original"
        
        with pytest.raises(ValueError, match="Estratégia não suportada"):
            await optimizer.optimize_prompt(
                original_prompt,
                strategy="invalid_strategy"
            )
    
    @pytest.mark.asyncio
    async def test_evaluate_prompt_metrics(self, optimizer):
        """Testa avaliação de métricas de prompt."""
        prompt = "Prompt para avaliação"
        
        metrics = await optimizer._evaluate_prompt(prompt)
        
        assert isinstance(metrics, PromptMetrics)
        assert metrics.response_time > 0
        assert metrics.token_usage > 0
        assert 0.0 <= metrics.relevance_score <= 1.0
        assert 0.0 <= metrics.diversity_score <= 1.0
        assert 0.0 <= metrics.user_satisfaction <= 1.0
        assert 0.0 <= metrics.conversion_rate <= 1.0
    
    @pytest.mark.asyncio
    async def test_calculate_relevance_score(self, optimizer):
        """Testa cálculo de score de relevância."""
        prompt = "Prompt original"
        response = "Resposta relevante"
        
        score = await optimizer._calculate_relevance_score(prompt, response)
        
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_calculate_diversity_score(self, optimizer):
        """Testa cálculo de score de diversidade."""
        response = "Resposta com palavras diversas e variadas"
        
        score = optimizer._calculate_diversity_score(response)
        
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_estimate_user_satisfaction(self, optimizer):
        """Testa estimativa de satisfação do usuário."""
        prompt = "Prompt claro e útil"
        response = "Resposta satisfatória"
        
        score = await optimizer._estimate_user_satisfaction(prompt, response)
        
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_estimate_conversion_rate(self, optimizer):
        """Testa estimativa de taxa de conversão."""
        prompt = "Prompt orientado para ação"
        context = {"goal": "conversion"}
        
        rate = await optimizer._estimate_conversion_rate(prompt, context)
        
        assert 0.0 <= rate <= 1.0
    
    def test_generate_cache_key(self, optimizer):
        """Testa geração de chave de cache."""
        prompt = "Prompt de teste"
        strategy = OptimizationStrategy.HYBRID
        context = {"key": "value"}
        
        key1 = optimizer._generate_cache_key(prompt, strategy, context)
        key2 = optimizer._generate_cache_key(prompt, strategy, context)
        
        assert key1 == key2  # Mesma entrada deve gerar mesma chave
        
        # Diferentes entradas devem gerar chaves diferentes
        key3 = optimizer._generate_cache_key("Prompt diferente", strategy, context)
        assert key1 != key3


class TestIntegration:
    """Testes de integração."""
    
    @pytest.mark.asyncio
    async def test_full_optimization_workflow(self):
        """Testa workflow completo de otimização."""
        # Criar provedor mock
        provider = MagicMock()
        provider.generate_response = AsyncMock(return_value="Prompt otimizado com sucesso")
        provider.analyze_sentiment = AsyncMock(return_value=0.7)
        provider.extract_keywords = AsyncMock(return_value=["keyword1", "keyword2"])
        
        # Criar otimizador
        optimizer = PromptOptimizer(provider)
        
        # Executar otimização
        original_prompt = "Pesquise palavras-chave sobre tecnologia"
        result, metrics = await optimizer.optimize_prompt(
            original_prompt,
            strategy=OptimizationStrategy.HYBRID,
            context={"domain": "technology"}
        )
        
        # Verificar resultados
        assert result == "Prompt otimizado com sucesso"
        assert isinstance(metrics, PromptMetrics)
        assert metrics.overall_score > 0
        
        # Adicionar feedback
        feedback = PromptFeedback(
            prompt_id="test_prompt",
            user_id="test_user",
            rating=4,
            comment="Funcionou bem",
            keywords_generated=20,
            keywords_used=15
        )
        await optimizer.add_feedback(feedback)
        
        # Verificar estatísticas
        stats = await optimizer.get_optimization_stats()
        assert stats["total_optimizations"] >= 1
        
        # Limpar recursos
        await optimizer.close()
    
    @pytest.mark.asyncio
    async def test_multiple_optimization_strategies(self):
        """Testa múltiplas estratégias de otimização."""
        provider = MagicMock()
        provider.generate_response = AsyncMock(return_value="Prompt otimizado")
        provider.analyze_sentiment = AsyncMock(return_value=0.6)
        provider.extract_keywords = AsyncMock(return_value=["test"])
        
        optimizer = PromptOptimizer(provider)
        
        original_prompt = "Prompt de teste"
        
        # Testar todas as estratégias
        strategies = [
            OptimizationStrategy.PERFORMANCE_BASED,
            OptimizationStrategy.FEEDBACK_BASED,
            OptimizationStrategy.SEMANTIC_BASED,
            OptimizationStrategy.HYBRID
        ]
        
        results = []
        for strategy in strategies:
            result, metrics = await optimizer.optimize_prompt(original_prompt, strategy=strategy)
            results.append((strategy, result, metrics))
        
        # Verificar que todas as estratégias produziram resultados
        assert len(results) == len(strategies)
        for strategy, result, metrics in results:
            assert result == "Prompt otimizado"
            assert isinstance(metrics, PromptMetrics)
        
        await optimizer.close()


# Testes de performance
class TestPerformance:
    """Testes de performance."""
    
    @pytest.mark.asyncio
    async def test_optimization_performance(self):
        """Testa performance da otimização."""
        provider = MagicMock()
        provider.generate_response = AsyncMock(return_value="Prompt otimizado")
        provider.analyze_sentiment = AsyncMock(return_value=0.5)
        provider.extract_keywords = AsyncMock(return_value=["test"])
        
        optimizer = PromptOptimizer(provider)
        
        start_time = datetime.now()
        
        # Executar múltiplas otimizações
        for index in range(10):
            await optimizer.optimize_prompt(f"Prompt {index}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Verificar que não demorou muito (deve ser rápido com mocks)
        assert duration < 5.0  # Máximo 5 segundos para 10 otimizações
        
        await optimizer.close()
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Testa performance do cache."""
        provider = MagicMock()
        provider.generate_response = AsyncMock(return_value="Prompt otimizado")
        provider.analyze_sentiment = AsyncMock(return_value=0.5)
        provider.extract_keywords = AsyncMock(return_value=["test"])
        
        optimizer = PromptOptimizer(provider)
        
        # Primeira otimização (sem cache)
        start_time = datetime.now()
        await optimizer.optimize_prompt("Prompt para cache")
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Segunda otimização (com cache)
        start_time = datetime.now()
        await optimizer.optimize_prompt("Prompt para cache")
        second_duration = (datetime.now() - start_time).total_seconds()
        
        # Cache deve ser mais rápido
        assert second_duration < first_duration
        
        await optimizer.close()


# Testes de edge cases
class TestEdgeCases:
    """Testes de casos extremos."""
    
    @pytest.mark.asyncio
    async def test_empty_prompt(self, mock_provider):
        """Testa otimização de prompt vazio."""
        optimizer = PromptOptimizer(mock_provider)
        
        result, metrics = await optimizer.optimize_prompt("")
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
        
        await optimizer.close()
    
    @pytest.mark.asyncio
    async def test_very_long_prompt(self, mock_provider):
        """Testa otimização de prompt muito longo."""
        optimizer = PromptOptimizer(mock_provider)
        
        long_prompt = "A" * 10000  # Prompt de 10k caracteres
        
        result, metrics = await optimizer.optimize_prompt(long_prompt)
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
        
        await optimizer.close()
    
    @pytest.mark.asyncio
    async def test_special_characters_prompt(self, mock_provider):
        """Testa otimização de prompt com caracteres especiais."""
        optimizer = PromptOptimizer(mock_provider)
        
        special_prompt = "Prompt com @#$%^&*()_+-=[]{}|;':\",./<>?"
        
        result, metrics = await optimizer.optimize_prompt(special_prompt)
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
        
        await optimizer.close()
    
    @pytest.mark.asyncio
    async def test_unicode_prompt(self, mock_provider):
        """Testa otimização de prompt com caracteres Unicode."""
        optimizer = PromptOptimizer(mock_provider)
        
        unicode_prompt = "Prompt com çãõéêíóôúñ"
        
        result, metrics = await optimizer.optimize_prompt(unicode_prompt)
        
        assert result == "Prompt otimizado"
        assert isinstance(metrics, PromptMetrics)
        
        await optimizer.close()


class TestProviderIntegration:
    """Testes de integração entre provedores."""
    
    @pytest.mark.asyncio
    async def test_deepseek_as_default_provider(self):
        """Testa DeepSeek como provedor padrão."""
        from infrastructure.ai.generativa.prompt_optimizer import create_prompt_optimizer
        
        # Testar criação com DeepSeek como padrão
        optimizer = await create_prompt_optimizer()
        
        # Verificar que o provedor é DeepSeek
        assert isinstance(optimizer.llm_provider, DeepSeekProvider)
        assert optimizer.llm_provider.model == "deepseek-coder-v2.0"
        
        await optimizer.close()
    
    @pytest.mark.asyncio
    async def test_provider_comparison(self):
        """Testa comparação entre diferentes provedores."""
        from infrastructure.ai.generativa.prompt_optimizer import create_prompt_optimizer
        
        providers = ["deepseek", "openai", "claude"]
        
        for provider_type in providers:
            optimizer = await create_prompt_optimizer(provider_type=provider_type)
            
            # Verificar que o provedor correto foi criado
            if provider_type == "deepseek":
                assert isinstance(optimizer.llm_provider, DeepSeekProvider)
            elif provider_type == "openai":
                assert isinstance(optimizer.llm_provider, OpenAIProvider)
            elif provider_type == "claude":
                assert isinstance(optimizer.llm_provider, ClaudeProvider)
            
            await optimizer.close()
    
    @pytest.mark.asyncio
    async def test_invalid_provider(self):
        """Testa provedor inválido."""
        from infrastructure.ai.generativa.prompt_optimizer import create_prompt_optimizer
        
        with pytest.raises(ValueError, match="Provedor não suportado"):
            await create_prompt_optimizer(provider_type="invalid_provider")


if __name__ == "__main__":
    pytest.main([__file__]) 