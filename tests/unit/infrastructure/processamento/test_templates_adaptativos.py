"""
Testes Unitários - TemplatesAdaptativos
=======================================

Testes para o sistema de templates adaptativos por nicho.

Autor: Paulo Júnior
Data: 2024-12-20
Tracing ID: TEST-TEMP-ADAP-001
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List

from infrastructure.processamento.templates_adaptativos import (
    TemplatesAdaptativos,
    Nicho,
    TemplateResult,
    TemplateNicho
)
from domain.models import Keyword, IntencaoBusca


class TestTemplatesAdaptativos:
    """Testes para o TemplatesAdaptativos."""
    
    @pytest.fixture
    def templates(self):
        """Fixture para instanciar o sistema de templates."""
        return TemplatesAdaptativos()
    
    @pytest.fixture
    def keyword_exemplo(self):
        """Fixture com keyword de exemplo."""
        return Keyword(
            termo="smartphone android barato",
            volume_busca=1000,
            cpc=2.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.TRANSACIONAL
        )
    
    @pytest.fixture
    def keyword_saude(self):
        """Fixture com keyword de saúde."""
        return Keyword(
            termo="sintomas gripe tratamento",
            volume_busca=500,
            cpc=1.5,
            concorrencia=0.3,
            intencao=IntencaoBusca.INFORMACIONAL
        )
    
    def test_inicializacao(self, templates):
        """Testa inicialização do sistema de templates."""
        assert templates is not None
        assert hasattr(templates, 'templates_nicho')
        assert hasattr(templates, 'palavras_nicho')
        assert hasattr(templates, 'enable_deteccao_automatica')
        assert hasattr(templates, 'metricas')
        assert templates.metricas["total_aplicacoes"] == 0
    
    def test_carregar_templates_nicho(self, templates):
        """Testa carregamento de templates por nicho."""
        templates._carregar_templates_nicho()
        
        # Verificar se templates foram carregados
        assert len(templates.templates_nicho) > 0
        
        # Verificar nichos suportados
        nichos_suportados = [Nicho.ECOMMERCE, Nicho.SAUDE, Nicho.TECNOLOGIA, 
                           Nicho.EDUCACAO, Nicho.FINANCAS, Nicho.GENERICO]
        
        for nicho in nichos_suportados:
            assert nicho in templates.templates_nicho
    
    def test_carregar_palavras_nicho(self, templates):
        """Testa carregamento de palavras por nicho."""
        templates._carregar_palavras_nicho()
        
        # Verificar se palavras foram carregadas
        assert len(templates.palavras_nicho) > 0
        
        # Verificar nichos suportados
        nichos_suportados = [Nicho.ECOMMERCE, Nicho.SAUDE, Nicho.TECNOLOGIA, 
                           Nicho.EDUCACAO, Nicho.FINANCAS]
        
        for nicho in nichos_suportados:
            assert nicho in templates.palavras_nicho
            assert len(templates.palavras_nicho[nicho]) > 0
    
    @pytest.mark.parametrize("keyword,expected_nicho", [
        ("comprar smartphone online", Nicho.ECOMMERCE),
        ("sintomas gripe tratamento", Nicho.SAUDE),
        ("melhor software desenvolvimento", Nicho.TECNOLOGIA),
        ("curso python online", Nicho.EDUCACAO),
        ("investimento ações renda fixa", Nicho.FINANCAS),
        ("palavra genérica qualquer", Nicho.GENERICO),
    ])
    def test_detectar_nicho_automatico(self, templates, keyword, expected_nicho):
        """Testa detecção automática de nicho."""
        kw = Keyword(termo=keyword, volume_busca=100, cpc=1.0, concorrencia=0.5)
        resultado = templates.detectar_nicho_automatico(kw)
        assert resultado == expected_nicho
    
    def test_detectar_nicho_automatico_desabilitado(self, templates, keyword_exemplo):
        """Testa detecção automática desabilitada."""
        templates.enable_deteccao_automatica = False
        resultado = templates.detectar_nicho_automatico(keyword_exemplo)
        assert resultado == Nicho.GENERICO
    
    def test_obter_template_nicho(self, templates):
        """Testa obtenção de template por nicho."""
        template = templates.obter_template_nicho(Nicho.ECOMMERCE)
        
        assert isinstance(template, TemplateNicho)
        assert template.nicho == Nicho.ECOMMERCE
        assert template.nome is not None
        assert template.descricao is not None
        assert template.template is not None
        assert template.palavras_chave is not None
        assert template.score_adequacao > 0.0
    
    def test_obter_template_nicho_inexistente(self, templates):
        """Testa obtenção de template para nicho inexistente."""
        template = templates.obter_template_nicho(Nicho.GENERICO)
        
        assert isinstance(template, TemplateNicho)
        assert template.nicho == Nicho.GENERICO
    
    def test_aplicar_template_keyword(self, templates, keyword_exemplo):
        """Testa aplicação de template em keyword."""
        resultado = templates.aplicar_template_keyword(keyword_exemplo)
        
        assert isinstance(resultado, TemplateResult)
        assert resultado.keyword == keyword_exemplo
        assert resultado.template_aplicado is not None
        assert resultado.texto_gerado is not None
        assert resultado.score_adequacao > 0.0
        assert resultado.nicho_detectado is not None
        assert isinstance(resultado.metadados, dict)
    
    def test_aplicar_template_keyword_nicho_especifico(self, templates, keyword_exemplo):
        """Testa aplicação de template com nicho específico."""
        resultado = templates.aplicar_template_keyword(keyword_exemplo, Nicho.ECOMMERCE)
        
        assert isinstance(resultado, TemplateResult)
        assert resultado.nicho_detectado == Nicho.ECOMMERCE
        assert resultado.template_aplicado.nicho == Nicho.ECOMMERCE
    
    def test_aplicar_template_lista_keywords(self, templates):
        """Testa aplicação de template em lista de keywords."""
        keywords = [
            Keyword(termo="smartphone barato", volume_busca=100, cpc=1.0, concorrencia=0.5),
            Keyword(termo="curso python", volume_busca=200, cpc=1.5, concorrencia=0.4),
            Keyword(termo="investimento ações", volume_busca=300, cpc=2.0, concorrencia=0.6)
        ]
        
        resultados = templates.aplicar_template_lista(keywords)
        
        assert isinstance(resultados, list)
        assert len(resultados) == len(keywords)
        
        for resultado in resultados:
            assert isinstance(resultado, TemplateResult)
            assert resultado.keyword in keywords
            assert resultado.template_aplicado is not None
            assert resultado.texto_gerado is not None
    
    def test_aplicar_template_lista_vazia(self, templates):
        """Testa aplicação de template em lista vazia."""
        resultados = templates.aplicar_template_lista([])
        assert resultados == []
    
    def test_calcular_score_adequacao(self, templates, keyword_exemplo):
        """Testa cálculo de score de adequação."""
        template = templates.obter_template_nicho(Nicho.ECOMMERCE)
        score = templates.calcular_score_adequacao(keyword_exemplo, template)
        
        assert 0.0 <= score <= 1.0
    
    @pytest.mark.parametrize("keyword_termo,expected_score", [
        ("comprar smartphone", 0.8),  # Alto score para e-commerce
        ("sintomas gripe", 0.3),      # Baixo score para e-commerce
        ("curso online", 0.4),        # Médio score para e-commerce
    ])
    def test_score_adequacao_por_termo(self, templates, keyword_termo, expected_score):
        """Testa score de adequação por termo."""
        keyword = Keyword(termo=keyword_termo, volume_busca=100, cpc=1.0, concorrencia=0.5)
        template = templates.obter_template_nicho(Nicho.ECOMMERCE)
        score = templates.calcular_score_adequacao(keyword, template)
        
        # Score deve estar próximo do esperado (com tolerância)
        assert abs(score - expected_score) < 0.3
    
    def test_gerar_texto_template(self, templates, keyword_exemplo):
        """Testa geração de texto com template."""
        template = templates.obter_template_nicho(Nicho.ECOMMERCE)
        texto = templates.gerar_texto_template(keyword_exemplo, template)
        
        assert isinstance(texto, str)
        assert len(texto) > 0
        assert keyword_exemplo.termo.lower() in texto.lower()
    
    def test_gerar_texto_template_com_placeholder(self, templates):
        """Testa geração de texto com placeholders."""
        keyword = Keyword(termo="smartphone android", volume_busca=1000, cpc=2.0, concorrencia=0.5)
        template = templates.obter_template_nicho(Nicho.ECOMMERCE)
        texto = templates.gerar_texto_template(keyword, template)
        
        # Verificar se placeholders foram substituídos
        assert "{keyword}" not in texto
        assert "{volume}" not in texto
        assert "{cpc}" not in texto
        assert "{concorrencia}" not in texto
    
    def test_validar_qualidade_templates(self, templates):
        """Testa validação de qualidade dos templates."""
        # Criar resultados de exemplo
        keywords = [
            Keyword(termo="smartphone barato", volume_busca=100, cpc=1.0, concorrencia=0.5),
            Keyword(termo="curso python", volume_busca=200, cpc=1.5, concorrencia=0.4)
        ]
        
        resultados = templates.aplicar_template_lista(keywords)
        qualidade = templates.validar_qualidade_templates(resultados)
        
        assert isinstance(qualidade, dict)
        assert "total_keywords" in qualidade
        assert "score_adequacao_medio" in qualidade
        assert "distribuicao_adequacao" in qualidade
        assert "nichos_utilizados" in qualidade
        assert "status" in qualidade
        
        assert qualidade["total_keywords"] == 2
        assert 0.0 <= qualidade["score_adequacao_medio"] <= 1.0
    
    def test_validar_qualidade_templates_vazio(self, templates):
        """Testa validação de qualidade com lista vazia."""
        qualidade = templates.validar_qualidade_templates([])
        
        assert isinstance(qualidade, dict)
        assert qualidade["status"] == "empty"
        assert "message" in qualidade
    
    def test_obter_metricas(self, templates):
        """Testa obtenção de métricas."""
        # Simular algumas aplicações
        templates.metricas["total_aplicacoes"] = 10
        templates.metricas["total_keywords_processadas"] = 50
        templates.metricas["tempo_total_aplicacao"] = 5.0
        
        metricas = templates.obter_metricas()
        
        assert "total_aplicacoes" in metricas
        assert "total_keywords_processadas" in metricas
        assert "tempo_total_aplicacao" in metricas
        assert "tempo_medio_aplicacao" in metricas
        assert "keywords_por_aplicacao" in metricas
        
        assert metricas["tempo_medio_aplicacao"] == 0.5  # 5.0 / 10
        assert metricas["keywords_por_aplicacao"] == 5.0  # 50 / 10
    
    def test_resetar_metricas(self, templates):
        """Testa reset de métricas."""
        # Simular métricas existentes
        templates.metricas["total_aplicacoes"] = 15
        templates.metricas["total_keywords_processadas"] = 75
        
        templates.resetar_metricas()
        
        assert templates.metricas["total_aplicacoes"] == 0
        assert templates.metricas["total_keywords_processadas"] == 0
        assert templates.metricas["tempo_total_aplicacao"] == 0.0
        assert templates.metricas["ultima_aplicacao"] is None
    
    def test_aplicar_template_atualiza_metricas(self, templates, keyword_exemplo):
        """Testa se aplicação atualiza métricas."""
        metricas_iniciais = templates.metricas.copy()
        
        templates.aplicar_template_keyword(keyword_exemplo)
        
        # Verificar se métricas foram atualizadas
        assert templates.metricas["total_aplicacoes"] > metricas_iniciais["total_aplicacoes"]
        assert templates.metricas["total_keywords_processadas"] > metricas_iniciais["total_keywords_processadas"]
        assert templates.metricas["tempo_total_aplicacao"] > metricas_iniciais["tempo_total_aplicacao"]
        assert templates.metricas["ultima_aplicacao"] is not None
    
    def test_aplicar_template_com_erro(self, templates):
        """Testa aplicação com erro."""
        # Simular keyword inválida
        keyword_invalida = Mock()
        keyword_invalida.termo = None
        
        resultado = templates.aplicar_template_keyword(keyword_invalida)
        
        # Deve retornar resultado válido mesmo com erro
        assert isinstance(resultado, TemplateResult)
        assert resultado.keyword == keyword_invalida
        assert resultado.score_adequacao == 0.0
        assert "erro" in resultado.metadados
    
    def test_templates_por_nicho_completos(self, templates):
        """Testa se todos os templates por nicho estão completos."""
        nichos = [Nicho.ECOMMERCE, Nicho.SAUDE, Nicho.TECNOLOGIA, 
                 Nicho.EDUCACAO, Nicho.FINANCAS, Nicho.GENERICO]
        
        for nicho in nichos:
            template = templates.obter_template_nicho(nicho)
            
            # Verificar campos obrigatórios
            assert template.nicho == nicho
            assert template.nome is not None
            assert template.descricao is not None
            assert template.template is not None
            assert template.palavras_chave is not None
            assert template.score_adequacao > 0.0
    
    def test_consistencia_deteccao_nicho(self, templates):
        """Testa consistência na detecção de nicho."""
        keywords = [
            Keyword(termo="comprar smartphone", volume_busca=100, cpc=1.0, concorrencia=0.5),
            Keyword(termo="smartphone comprar", volume_busca=100, cpc=1.0, concorrencia=0.5),
            Keyword(termo="COMPRAR SMARTPHONE", volume_busca=100, cpc=1.0, concorrencia=0.5)
        ]
        
        nichos_detectados = []
        for keyword in keywords:
            nicho = templates.detectar_nicho_automatico(keyword)
            nichos_detectados.append(nicho)
        
        # Todos devem detectar o mesmo nicho
        assert len(set(nichos_detectados)) == 1
        assert nichos_detectados[0] == Nicho.ECOMMERCE
    
    def test_score_adequacao_por_intencao(self, templates):
        """Testa score de adequação por intenção de busca."""
        keywords = [
            Keyword(termo="comprar smartphone", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.TRANSACIONAL),
            Keyword(termo="melhor smartphone", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.COMPARACAO),
            Keyword(termo="smartphone preço", volume_busca=100, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
        ]
        
        template = templates.obter_template_nicho(Nicho.ECOMMERCE)
        scores = []
        
        for keyword in keywords:
            score = templates.calcular_score_adequacao(keyword, template)
            scores.append(score)
        
        # Scores devem ser diferentes por intenção
        assert len(set(scores)) > 1
    
    def test_geracao_texto_personalizada(self, templates):
        """Testa geração de texto personalizada por nicho."""
        keyword = Keyword(termo="smartphone android", volume_busca=1000, cpc=2.0, concorrencia=0.5)
        
        # Aplicar templates de nichos diferentes
        resultado_ecommerce = templates.aplicar_template_keyword(keyword, Nicho.ECOMMERCE)
        resultado_tecnologia = templates.aplicar_template_keyword(keyword, Nicho.TECNOLOGIA)
        
        # Textos devem ser diferentes
        assert resultado_ecommerce.texto_gerado != resultado_tecnologia.texto_gerado
        assert resultado_ecommerce.nicho_detectado == Nicho.ECOMMERCE
        assert resultado_tecnologia.nicho_detectado == Nicho.TECNOLOGIA 