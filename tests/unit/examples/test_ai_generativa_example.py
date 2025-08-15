from typing import Dict, List, Optional, Any
"""
Testes Unitários para Exemplo de IA Generativa
=============================================

Testes abrangentes para o exemplo prático do sistema de IA Generativa.

Tracing ID: AI_GEN_EXAMPLE_TEST_001
Data: 2024-12-19
Autor: Sistema de Testes
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from examples.ai_generativa_example import AIGenerativaExample


class TestAIGenerativaExample:
    """Testes para o exemplo de IA Generativa."""
    
    @pytest.fixture
    def example(self):
        """Cria instância do exemplo para testes."""
        return AIGenerativaExample()
    
    @pytest.mark.asyncio
    async def test_setup_system(self, example):
        """Testa configuração do sistema."""
        await example.setup_system()
        
        assert example.optimizer is not None
        assert example.template_generator is not None
        assert example.feedback_analyzer is not None
        assert example.telemetry_manager is not None
        assert example.tracing_manager is not None
    
    @pytest.mark.asyncio
    async def test_mock_provider_creation(self, example):
        """Testa criação do provedor mock."""
        provider = example._create_mock_provider()
        
        assert provider is not None
        assert hasattr(provider, 'generate_response')
        assert hasattr(provider, 'analyze_sentiment')
        assert hasattr(provider, 'extract_keywords')
    
    @pytest.mark.asyncio
    async def test_mock_generate_response(self, example):
        """Testa geração de resposta mock."""
        provider = example._create_mock_provider()
        
        # Testar diferentes tipos de prompts
        test_cases = [
            ("Pesquise palavras-chave", "pesquise"),
            ("Analise concorrência", "analise"),
            ("Gere ideias", "gere"),
            ("Otimize SEO", "otimize"),
            ("Identifique tendências", "identifique"),
            ("Prompt genérico", "genérico")
        ]
        
        for prompt, expected_keyword in test_cases:
            result = await provider.generate_response(prompt)
            
            assert isinstance(result, str)
            assert len(result) > 0
            
            if expected_keyword != "genérico":
                assert expected_keyword in result.lower()
    
    @pytest.mark.asyncio
    async def test_mock_analyze_sentiment(self, example):
        """Testa análise de sentimento mock."""
        provider = example._create_mock_provider()
        
        # Testar sentimento positivo
        positive_text = "Este é um excelente prompt muito útil"
        sentiment = await provider.analyze_sentiment(positive_text)
        assert sentiment > 0
        
        # Testar sentimento negativo
        negative_text = "Este é um prompt ruim e confuso"
        sentiment = await provider.analyze_sentiment(negative_text)
        assert sentiment < 0
        
        # Testar sentimento neutro
        neutral_text = "Este é um prompt normal"
        sentiment = await provider.analyze_sentiment(neutral_text)
        assert sentiment == 0.0
    
    @pytest.mark.asyncio
    async def test_mock_extract_keywords(self, example):
        """Testa extração de keywords mock."""
        provider = example._create_mock_provider()
        
        text = "Este é um texto com palavras relevantes e importantes"
        keywords = await provider.extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert all(isinstance(kw, str) for kw in keywords)
    
    @pytest.mark.asyncio
    async def test_demonstrate_prompt_optimization(self, example):
        """Testa demonstração de otimização de prompts."""
        await example.setup_system()
        
        # Verificar que há prompts de exemplo
        assert len(example.example_prompts) > 0
        
        # Executar demonstração
        await example.demonstrate_prompt_optimization()
        
        # Verificar que otimizador foi usado
        assert example.optimizer is not None
    
    @pytest.mark.asyncio
    async def test_demonstrate_template_generation(self, example):
        """Testa demonstração de geração de templates."""
        await example.setup_system()
        
        # Executar demonstração
        await example.demonstrate_template_generation()
        
        # Verificar que gerador de templates foi usado
        assert example.template_generator is not None
    
    @pytest.mark.asyncio
    async def test_demonstrate_feedback_analysis(self, example):
        """Testa demonstração de análise de feedback."""
        await example.setup_system()
        
        # Verificar que há feedbacks de exemplo
        assert len(example.example_feedbacks) > 0
        
        # Executar demonstração
        await example.demonstrate_feedback_analysis()
        
        # Verificar que analisador de feedback foi usado
        assert example.feedback_analyzer is not None
    
    @pytest.mark.asyncio
    async def test_demonstrate_integration(self, example):
        """Testa demonstração de integração."""
        await example.setup_system()
        
        # Executar demonstração
        await example.demonstrate_integration()
        
        # Verificar que todos os componentes foram usados
        assert example.optimizer is not None
        assert example.template_generator is not None
        assert example.feedback_analyzer is not None
    
    @pytest.mark.asyncio
    async def test_demonstrate_statistics(self, example):
        """Testa demonstração de estatísticas."""
        await example.setup_system()
        
        # Executar demonstração
        await example.demonstrate_statistics()
        
        # Verificar que todos os componentes foram usados
        assert example.optimizer is not None
        assert example.template_generator is not None
        assert example.feedback_analyzer is not None
    
    @pytest.mark.asyncio
    async def test_run_demonstration(self, example):
        """Testa execução completa da demonstração."""
        # Executar demonstração completa
        await example.run_demonstration()
        
        # Verificar que todos os componentes foram inicializados
        assert example.optimizer is not None
        assert example.template_generator is not None
        assert example.feedback_analyzer is not None
    
    @pytest.mark.asyncio
    async def test_example_prompts_content(self, example):
        """Testa conteúdo dos prompts de exemplo."""
        assert len(example.example_prompts) == 5
        
        expected_keywords = [
            "pesquise", "palavras-chave", "marketing",
            "analise", "concorrência", "e-commerce",
            "gere", "ideias", "conteúdo", "blog",
            "otimize", "SEO", "página",
            "identifique", "tendências", "redes sociais"
        ]
        
        all_prompts = " ".join(example.example_prompts).lower()
        for keyword in expected_keywords:
            assert keyword in all_prompts
    
    @pytest.mark.asyncio
    async def test_example_feedbacks_content(self, example):
        """Testa conteúdo dos feedbacks de exemplo."""
        assert len(example.example_feedbacks) == 3
        
        # Verificar estrutura dos feedbacks
        for feedback in example.example_feedbacks:
            assert "prompt_id" in feedback
            assert "user_id" in feedback
            assert "rating" in feedback
            assert "comment" in feedback
            assert "keywords_generated" in feedback
            assert "keywords_used" in feedback
            
            # Verificar tipos de dados
            assert isinstance(feedback["rating"], int)
            assert isinstance(feedback["comment"], str)
            assert isinstance(feedback["keywords_generated"], int)
            assert isinstance(feedback["keywords_used"], int)
            
            # Verificar valores válidos
            assert 1 <= feedback["rating"] <= 5
            assert feedback["keywords_generated"] > 0
            assert feedback["keywords_used"] <= feedback["keywords_generated"]


class TestIntegration:
    """Testes de integração."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Testa workflow completo do exemplo."""
        example = AIGenerativaExample()
        
        # Executar demonstração completa
        await example.run_demonstration()
        
        # Verificar que todos os componentes funcionaram
        assert example.optimizer is not None
        assert example.template_generator is not None
        assert example.feedback_analyzer is not None
        
        # Verificar que telemetria foi registrada
        assert example.telemetry_manager is not None
        
        # Verificar que tracing foi usado
        assert example.tracing_manager is not None
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Testa tratamento de erros."""
        example = AIGenerativaExample()
        
        # Simular erro no provedor
        with patch.object(example, '_create_mock_provider') as mock_create:
            mock_provider = MagicMock()
            mock_provider.generate_response = AsyncMock(side_effect=Exception("API Error"))
            mock_create.return_value = mock_provider
            
            # A demonstração deve falhar graciosamente
            with pytest.raises(Exception):
                await example.run_demonstration()


class TestPerformance:
    """Testes de performance."""
    
    @pytest.mark.asyncio
    async def test_demonstration_performance(self):
        """Testa performance da demonstração."""
        import time
        
        example = AIGenerativaExample()
        
        start_time = time.time()
        await example.run_demonstration()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Demonstração deve ser rápida (com mocks)
        assert duration < 10.0  # Máximo 10 segundos
    
    @pytest.mark.asyncio
    async def test_mock_provider_performance(self):
        """Testa performance do provedor mock."""
        import time
        
        example = AIGenerativaExample()
        provider = example._create_mock_provider()
        
        # Testar performance de geração de resposta
        start_time = time.time()
        for _ in range(10):
            await provider.generate_response("Teste de performance")
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Deve ser rápido
        assert duration < 2.0  # Máximo 2 segundos para 10 chamadas


class TestEdgeCases:
    """Testes de casos extremos."""
    
    @pytest.mark.asyncio
    async def test_empty_prompts(self, example):
        """Testa com prompts vazios."""
        await example.setup_system()
        
        # Substituir prompts de exemplo por vazios
        original_prompts = example.example_prompts
        example.example_prompts = ["", "   ", "\n\n"]
        
        # Deve funcionar sem erro
        await example.demonstrate_prompt_optimization()
        
        # Restaurar prompts originais
        example.example_prompts = original_prompts
    
    @pytest.mark.asyncio
    async def test_empty_feedbacks(self, example):
        """Testa com feedbacks vazios."""
        await example.setup_system()
        
        # Substituir feedbacks de exemplo por vazios
        original_feedbacks = example.example_feedbacks
        example.example_feedbacks = []
        
        # Deve funcionar sem erro
        await example.demonstrate_feedback_analysis()
        
        # Restaurar feedbacks originais
        example.example_feedbacks = original_feedbacks
    
    @pytest.mark.asyncio
    async def test_large_prompts(self, example):
        """Testa com prompts muito grandes."""
        await example.setup_system()
        
        # Criar prompt muito grande
        large_prompt = "A" * 10000  # 10k caracteres
        
        # Deve funcionar sem erro
        result, metrics = await example.optimizer.optimize_prompt(large_prompt)
        
        assert isinstance(result, str)
        assert isinstance(metrics, object)  # PromptMetrics


if __name__ == "__main__":
    pytest.main([__file__]) 