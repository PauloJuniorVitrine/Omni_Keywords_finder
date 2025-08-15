"""
Testes Unitários para Gerador Prompt
Gerador de Prompts para Keywords e Clusters - Omni Keywords Finder

Prompt: Implementação de testes unitários para gerador de prompts
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from infrastructure.processamento.gerador_prompt import GeradorPrompt
from domain.models import Keyword, Cluster, IntencaoBusca


class TestGeradorPrompt:
    """Testes para GeradorPrompt"""
    
    @pytest.fixture
    def sample_template(self):
        """Template de exemplo para testes"""
        return """
        # {primary_keyword}
        
        ## Introdução
        Este é um artigo sobre {primary_keyword}.
        
        ## Palavras-chave Secundárias
        {secondary_keywords}
        
        ## Cluster
        {cluster}
        
        ## Conclusão
        {primary_keyword} é importante para o seu negócio.
        
        ### FAQ
        1. O que é {primary_keyword}?
        2. Como usar {primary_keyword}?
        3. Benefícios de {primary_keyword}
        4. Melhores práticas para {primary_keyword}
        5. Exemplos de {primary_keyword}
        6. Dicas sobre {primary_keyword}
        7. Problemas comuns de {primary_keyword}
        8. Soluções para {primary_keyword}
        """
    
    @pytest.fixture
    def sample_keyword(self):
        """Keyword de exemplo para testes"""
        return Keyword(
            termo="palavra chave teste",
            volume_busca=1000,
            cpc=1.50,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            score=85.5,
            justificativa="Teste de keyword",
            fonte="google_ads",
            data_coleta=datetime.now()
        )
    
    @pytest.fixture
    def sample_secondary_keywords(self):
        """Keywords secundárias de exemplo para testes"""
        return [
            Keyword(
                termo="keyword secundária 1",
                volume_busca=500,
                cpc=1.00,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL,
                score=75.0,
                justificativa="Primeira secundária",
                fonte="google_trends",
                data_coleta=datetime.now()
            ),
            Keyword(
                termo="keyword secundária 2",
                volume_busca=300,
                cpc=0.75,
                concorrencia=0.3,
                intencao=IntencaoBusca.TRANSACIONAL,
                score=80.0,
                justificativa="Segunda secundária",
                fonte="google_suggest",
                data_coleta=datetime.now()
            )
        ]
    
    @pytest.fixture
    def sample_cluster(self):
        """Cluster de exemplo para testes"""
        cluster = Mock(spec=Cluster)
        cluster.id = "cluster_teste_123"
        return cluster
    
    @pytest.fixture
    def gerador_prompt(self, sample_template):
        """Instância do GeradorPrompt para testes"""
        return GeradorPrompt(template=sample_template)
    
    def test_gerador_prompt_initialization_with_template(self, sample_template):
        """Testa inicialização com template string"""
        gerador = GeradorPrompt(template=sample_template)
        
        assert gerador.template == sample_template
        assert gerador.separador_secundarias == ", "
        assert gerador.callback is None
    
    def test_gerador_prompt_initialization_with_template_path(self):
        """Testa inicialização com arquivo de template"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            template_content = "Template de teste: {primary_keyword}"
            f.write(template_content)
            template_path = f.name
        
        try:
            gerador = GeradorPrompt(template_path=template_path)
            assert gerador.template == template_content
        finally:
            os.unlink(template_path)
    
    def test_gerador_prompt_initialization_with_custom_separator(self, sample_template):
        """Testa inicialização com separador customizado"""
        gerador = GeradorPrompt(
            template=sample_template,
            separador_secundarias=" | "
        )
        
        assert gerador.separador_secundarias == " | "
    
    def test_gerador_prompt_initialization_with_callback(self, sample_template):
        """Testa inicialização com callback"""
        callback = Mock()
        gerador = GeradorPrompt(
            template=sample_template,
            callback=callback
        )
        
        assert gerador.callback == callback
    
    def test_gerador_prompt_initialization_without_template(self):
        """Testa inicialização sem template (deve falhar)"""
        with pytest.raises(ValueError, match="É obrigatório fornecer template ou template_path"):
            GeradorPrompt()
    
    def test_gerador_prompt_initialization_with_invalid_template_path(self):
        """Testa inicialização com caminho de template inválido"""
        with pytest.raises(FileNotFoundError):
            GeradorPrompt(template_path="/caminho/inexistente/template.txt")
    
    def test_formatar_lista_empty(self, gerador_prompt):
        """Testa formatação de lista vazia"""
        result = gerador_prompt._formatar_lista([])
        assert result == ""
    
    def test_formatar_lista_default(self, gerador_prompt):
        """Testa formatação de lista com formato padrão"""
        itens = ["item1", "item2", "item3"]
        result = gerador_prompt._formatar_lista(itens)
        assert result == "item1, item2, item3"
    
    def test_formatar_lista_numerada(self, gerador_prompt):
        """Testa formatação de lista numerada"""
        itens = ["item1", "item2", "item3"]
        result = gerador_prompt._formatar_lista(itens, formato="numerada")
        expected = "1. item1\n2. item2\n3. item3"
        assert result == expected
    
    def test_formatar_lista_tabela(self, gerador_prompt):
        """Testa formatação de lista em tabela"""
        itens = ["item1", "item2", "item3"]
        result = gerador_prompt._formatar_lista(itens, formato="tabela")
        expected = "| item1 |\n| item2 |\n| item3 |"
        assert result == expected
    
    def test_formatar_lista_custom_separator(self, sample_template):
        """Testa formatação com separador customizado"""
        gerador = GeradorPrompt(
            template=sample_template,
            separador_secundarias=" | "
        )
        itens = ["item1", "item2", "item3"]
        result = gerador._formatar_lista(itens)
        assert result == "item1 | item2 | item3"
    
    def test_placeholders_nao_substituidos(self, gerador_prompt):
        """Testa detecção de placeholders não substituídos"""
        prompt = "Texto com {placeholder1} e {placeholder2} e texto normal"
        placeholders = gerador_prompt._placeholders_nao_substituidos(prompt)
        assert placeholders == ["placeholder1", "placeholder2"]
    
    def test_placeholders_nao_substituidos_none(self, gerador_prompt):
        """Testa detecção quando não há placeholders"""
        prompt = "Texto sem placeholders"
        placeholders = gerador_prompt._placeholders_nao_substituidos(prompt)
        assert placeholders == []
    
    def test_gerar_prompt_basic(self, gerador_prompt, sample_keyword, sample_secondary_keywords):
        """Testa geração básica de prompt"""
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=sample_secondary_keywords
        )
        
        assert isinstance(result, str)
        assert sample_keyword.termo in result
        assert "keyword secundária 1" in result
        assert "keyword secundária 2" in result
        assert "cluster" in result  # placeholder não substituído
    
    def test_gerar_prompt_with_cluster(self, gerador_prompt, sample_keyword, sample_secondary_keywords, sample_cluster):
        """Testa geração de prompt com cluster"""
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=sample_secondary_keywords,
            cluster=sample_cluster
        )
        
        assert isinstance(result, str)
        assert sample_keyword.termo in result
        assert sample_cluster.id in result
    
    def test_gerar_prompt_with_extras(self, gerador_prompt, sample_keyword, sample_secondary_keywords):
        """Testa geração de prompt com dados extras"""
        extras = {
            "dominio": "ecommerce",
            "categoria": "eletronicos",
            "regiao": "brasil"
        }
        
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=sample_secondary_keywords,
            extras=extras
        )
        
        assert isinstance(result, str)
        assert sample_keyword.termo in result
    
    def test_gerar_prompt_with_formato_secundarias(self, gerador_prompt, sample_keyword, sample_secondary_keywords):
        """Testa geração de prompt com formato específico para secundárias"""
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=sample_secondary_keywords,
            formato_secundarias="numerada"
        )
        
        assert isinstance(result, str)
        assert "1. keyword secundária 1" in result
        assert "2. keyword secundária 2" in result
    
    def test_gerar_prompt_with_relatorio(self, gerador_prompt, sample_keyword, sample_secondary_keywords):
        """Testa geração de prompt com relatório"""
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=sample_secondary_keywords,
            relatorio=True
        )
        
        assert isinstance(result, str)
        # Verificar se contém o bloco JSON de resumo
        assert "Resumo e Checklist:" in result
        assert "checklist" in result
        assert "aqr" in result
    
    def test_gerar_prompt_with_callback(self, sample_template, sample_keyword, sample_secondary_keywords):
        """Testa geração de prompt com callback"""
        callback = Mock()
        gerador = GeradorPrompt(template=sample_template, callback=callback)
        
        result = gerador.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=sample_secondary_keywords
        )
        
        assert isinstance(result, str)
        callback.assert_called_once()
        
        # Verificar dados passados para callback
        call_args = callback.call_args[0][0]
        assert call_args["primary_keyword"] == sample_keyword.termo
        assert len(call_args["secondary_keywords"]) == 2
        assert "prompt_final" in call_args
    
    def test_gerar_prompt_without_primary_keyword(self, gerador_prompt, sample_secondary_keywords):
        """Testa geração sem keyword principal (deve falhar)"""
        with pytest.raises(ValueError, match="primary_keyword é obrigatório"):
            gerador_prompt.gerar_prompt(
                primary_keyword=None,
                secondary_keywords=sample_secondary_keywords
            )
    
    def test_gerar_prompt_with_invalid_primary_keyword(self, gerador_prompt, sample_secondary_keywords):
        """Testa geração com keyword principal inválido (deve falhar)"""
        with pytest.raises(ValueError, match="deve ser Keyword"):
            gerador_prompt.gerar_prompt(
                primary_keyword="string_invalida",
                secondary_keywords=sample_secondary_keywords
            )
    
    def test_gerar_prompt_with_none_secondary_keywords(self, gerador_prompt, sample_keyword):
        """Testa geração com keywords secundárias None"""
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=None
        )
        
        assert isinstance(result, str)
        assert sample_keyword.termo in result
    
    def test_gerar_prompt_with_empty_secondary_keywords(self, gerador_prompt, sample_keyword):
        """Testa geração com keywords secundárias vazias"""
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=[]
        )
        
        assert isinstance(result, str)
        assert sample_keyword.termo in result
    
    def test_validar_aqr_accuracy_pass(self, gerador_prompt, sample_keyword):
        """Testa validação AQR com accuracy passando"""
        prompt = f"Este é um texto sobre {sample_keyword.termo} que é muito importante."
        
        result = gerador_prompt._validar_aqr(prompt, sample_keyword)
        
        assert result["accuracy"] is True
        assert result["score_aqr"] > 0
    
    def test_validar_aqr_accuracy_fail(self, gerador_prompt, sample_keyword):
        """Testa validação AQR com accuracy falhando"""
        prompt = "Este é um texto sem a keyword principal."
        
        result = gerador_prompt._validar_aqr(prompt, sample_keyword)
        
        assert result["accuracy"] is False
        assert "Termo principal não encontrado" in result["observacoes"]
    
    def test_validar_aqr_quality_pass(self, gerador_prompt, sample_keyword):
        """Testa validação AQR com quality passando"""
        prompt = f"""
        # {sample_keyword.termo}
        
        ## Introdução
        Introdução sobre {sample_keyword.termo}.
        
        ### Seção 1
        Conteúdo da seção.
        
        ## Conclusão
        Conclusão sobre {sample_keyword.termo}.
        
        ### FAQ
        1. Pergunta 1?
        2. Pergunta 2?
        3. Pergunta 3?
        4. Pergunta 4?
        5. Pergunta 5?
        6. Pergunta 6?
        7. Pergunta 7?
        8. Pergunta 8?
        """
        
        result = gerador_prompt._validar_aqr(prompt, sample_keyword)
        
        assert result["quality"] is True
    
    def test_validar_aqr_quality_fail(self, gerador_prompt, sample_keyword):
        """Testa validação AQR com quality falhando"""
        prompt = f"Texto simples sobre {sample_keyword.termo} sem estrutura adequada."
        
        result = gerador_prompt._validar_aqr(prompt, sample_keyword)
        
        assert result["quality"] is False
        assert "Estrutura editorial incompleta" in result["observacoes"]
    
    def test_validar_aqr_reliability_pass(self, gerador_prompt, sample_keyword):
        """Testa validação AQR com reliability passando"""
        prompt = f"Texto sobre {sample_keyword.termo} com repetição moderada."
        
        result = gerador_prompt._validar_aqr(prompt, sample_keyword)
        
        assert result["reliability"] is True
    
    def test_validar_aqr_reliability_fail(self, gerador_prompt, sample_keyword):
        """Testa validação AQR com reliability falhando"""
        # Criar texto com repetição excessiva
        prompt = f"{sample_keyword.termo} " * 50  # Repetição excessiva
        
        result = gerador_prompt._validar_aqr(prompt, sample_keyword, repeticao_max=0.01)
        
        assert result["reliability"] is False
        assert "Repetição excessiva" in result["observacoes"]
    
    def test_validar_aqr_with_contradiction(self, gerador_prompt, sample_keyword):
        """Testa validação AQR com contradição detectada"""
        prompt = f"Texto sobre {sample_keyword.termo} que é contradiz o que foi dito antes."
        
        result = gerador_prompt._validar_aqr(prompt, sample_keyword)
        
        assert result["reliability"] is False
        assert "Possível contradição" in result["observacoes"]
    
    def test_validar_aqr_score_calculation(self, gerador_prompt, sample_keyword):
        """Testa cálculo do score AQR"""
        prompt = f"""
        # {sample_keyword.termo}
        
        ## Introdução
        Introdução sobre {sample_keyword.termo}.
        
        ## Conclusão
        Conclusão sobre {sample_keyword.termo}.
        
        ### FAQ
        1. Pergunta 1?
        2. Pergunta 2?
        3. Pergunta 3?
        4. Pergunta 4?
        5. Pergunta 5?
        6. Pergunta 6?
        7. Pergunta 7?
        8. Pergunta 8?
        """
        
        result = gerador_prompt._validar_aqr(prompt, sample_keyword)
        
        assert 0 <= result["score_aqr"] <= 1
        assert isinstance(result["score_aqr"], float)


class TestGeradorPromptIntegration:
    """Testes de integração para GeradorPrompt"""
    
    @pytest.fixture
    def complex_template(self):
        """Template complexo para testes de integração"""
        return """
        # {primary_keyword}
        
        Meta descrição: Guia completo sobre {primary_keyword} para {dominio}.
        
        ## Introdução
        {primary_keyword} é essencial para {categoria}.
        
        ## Palavras-chave Relacionadas
        {secondary_keywords}
        
        ## Cluster: {cluster}
        
        ### Benefícios
        - Benefício 1
        - Benefício 2
        
        ## Conclusão
        {primary_keyword} oferece vantagens significativas.
        
        ### CTA
        Clique aqui para saber mais sobre {primary_keyword}.
        
        ### FAQ
        1. O que é {primary_keyword}?
        2. Como usar {primary_keyword}?
        3. Benefícios de {primary_keyword}?
        4. Melhores práticas para {primary_keyword}?
        5. Exemplos de {primary_keyword}?
        6. Dicas sobre {primary_keyword}?
        7. Problemas comuns de {primary_keyword}?
        8. Soluções para {primary_keyword}?
        """
    
    @pytest.fixture
    def sample_keyword(self):
        """Keyword de exemplo para testes"""
        return Keyword(
            termo="otimização SEO",
            volume_busca=2000,
            cpc=2.50,
            concorrencia=0.8,
            intencao=IntencaoBusca.INFORMACIONAL,
            score=90.0,
            justificativa="Keyword principal para SEO",
            fonte="google_ads",
            data_coleta=datetime.now()
        )
    
    @pytest.fixture
    def sample_secondary_keywords(self):
        """Keywords secundárias de exemplo para testes"""
        return [
            Keyword(
                termo="SEO técnico",
                volume_busca=800,
                cpc=1.80,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                score=85.0,
                justificativa="SEO técnico",
                fonte="google_trends",
                data_coleta=datetime.now()
            ),
            Keyword(
                termo="otimização on-page",
                volume_busca=600,
                cpc=1.50,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL,
                score=82.0,
                justificativa="Otimização on-page",
                fonte="google_suggest",
                data_coleta=datetime.now()
            )
        ]
    
    @pytest.fixture
    def sample_cluster(self):
        """Cluster de exemplo para testes"""
        cluster = Mock(spec=Cluster)
        cluster.id = "seo_otimizacao_001"
        return cluster
    
    @pytest.fixture
    def gerador_prompt(self, complex_template):
        """Instância do GeradorPrompt para testes"""
        return GeradorPrompt(template=complex_template)
    
    def test_complete_prompt_generation(self, gerador_prompt, sample_keyword, sample_secondary_keywords, sample_cluster):
        """Testa geração completa de prompt"""
        extras = {
            "dominio": "marketing digital",
            "categoria": "SEO"
        }
        
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=sample_secondary_keywords,
            cluster=sample_cluster,
            extras=extras,
            formato_secundarias="numerada",
            relatorio=True
        )
        
        assert isinstance(result, str)
        
        # Verificar se todos os elementos estão presentes
        assert sample_keyword.termo in result
        assert "SEO técnico" in result
        assert "otimização on-page" in result
        assert sample_cluster.id in result
        assert "marketing digital" in result
        assert "SEO" in result
        
        # Verificar formato numerado das secundárias
        assert "1. SEO técnico" in result
        assert "2. otimização on-page" in result
        
        # Verificar estrutura do prompt
        assert "# " in result  # H1
        assert "## " in result  # H2
        assert "### " in result  # H3
        assert "FAQ" in result
        assert "CTA" in result
        
        # Verificar bloco JSON
        assert "Resumo e Checklist:" in result
        assert "checklist" in result
        assert "aqr" in result


class TestGeradorPromptErrorHandling:
    """Testes de tratamento de erros para GeradorPrompt"""
    
    @pytest.fixture
    def invalid_template(self):
        """Template inválido para testes"""
        return "Template com placeholder inválido: {invalid_placeholder"
    
    @pytest.fixture
    def sample_keyword(self):
        """Keyword de exemplo para testes"""
        return Keyword(
            termo="teste",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL,
            score=80.0,
            justificativa="Teste",
            fonte="test",
            data_coleta=datetime.now()
        )
    
    def test_gerar_prompt_with_invalid_template(self, invalid_template, sample_keyword):
        """Testa geração com template inválido"""
        gerador = GeradorPrompt(template=invalid_template)
        
        # Deve funcionar mesmo com template inválido
        result = gerador.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=[]
        )
        
        assert isinstance(result, str)
    
    def test_gerar_prompt_with_callback_error(self, sample_keyword):
        """Testa geração com erro no callback"""
        def error_callback(data):
            raise Exception("Erro no callback")
        
        gerador = GeradorPrompt(
            template="Template simples: {primary_keyword}",
            callback=error_callback
        )
        
        # Deve funcionar mesmo com erro no callback
        result = gerador.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=[]
        )
        
        assert isinstance(result, str)


class TestGeradorPromptPerformance:
    """Testes de performance para GeradorPrompt"""
    
    @pytest.fixture
    def large_template(self):
        """Template grande para testes de performance"""
        template = "# {primary_keyword}\n\n"
        for i in range(100):
            template += f"## Seção {i}\n"
            template += f"Conteúdo da seção {i} sobre {{primary_keyword}}.\n\n"
        template += "## Conclusão\n{primary_keyword} é importante.\n"
        return template
    
    @pytest.fixture
    def sample_keyword(self):
        """Keyword de exemplo para testes"""
        return Keyword(
            termo="keyword teste",
            volume_busca=100,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL,
            score=80.0,
            justificativa="Teste",
            fonte="test",
            data_coleta=datetime.now()
        )
    
    @pytest.fixture
    def gerador_prompt(self, large_template):
        """Instância do GeradorPrompt para testes"""
        return GeradorPrompt(template=large_template)
    
    def test_large_template_performance(self, gerador_prompt, sample_keyword):
        """Testa performance com template grande"""
        import time
        
        start_time = time.time()
        
        result = gerador_prompt.gerar_prompt(
            primary_keyword=sample_keyword,
            secondary_keywords=[],
            relatorio=True
        )
        
        end_time = time.time()
        
        # Verificar performance (deve ser rápido)
        processing_time = end_time - start_time
        assert processing_time < 5.0  # Menos de 5 segundos
        
        # Verificar resultado
        assert isinstance(result, str)
        assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__]) 