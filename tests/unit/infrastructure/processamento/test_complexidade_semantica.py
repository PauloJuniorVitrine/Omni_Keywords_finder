"""
Testes Unitários - CalculadorComplexidadeSemantica
=================================================

Testes para o sistema de cálculo de complexidade semântica de keywords.

Autor: Paulo Júnior
Data: 2024-12-20
Tracing ID: TEST-COMP-SEM-001
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List

from infrastructure.processamento.complexidade_semantica import (
    CalculadorComplexidadeSemantica,
    ComplexidadeSemantica
)


class TestCalculadorComplexidadeSemantica:
    """Testes para o CalculadorComplexidadeSemantica."""
    
    @pytest.fixture
    def calculador(self):
        """Fixture para instanciar o calculador."""
        return CalculadorComplexidadeSemantica()
    
    @pytest.fixture
    def texto_simples(self):
        """Fixture com texto simples."""
        return "smartphone barato"
    
    @pytest.fixture
    def texto_complexo(self):
        """Fixture com texto complexo."""
        return "smartphone android de alta performance com câmera profissional"
    
    @pytest.fixture
    def texto_tecnico(self):
        """Fixture com texto técnico."""
        return "processador qualcomm snapdragon 8 gen 2 com gpu adreno 740"
    
    def test_inicializacao(self, calculador):
        """Testa inicialização do calculador."""
        assert calculador is not None
        assert hasattr(calculador, '_min_caracteres')
        assert hasattr(calculador, '_palavras_tecnicas')
        assert hasattr(calculador, '_palavras_complexas')
        assert hasattr(calculador, 'metricas')
        assert calculador.metricas["total_analises"] == 0
    
    @pytest.mark.parametrize("texto,expected", [
        ("", []),
        ("palavra", ["palavra"]),
        ("palavra1 palavra2", ["palavra1", "palavra2"]),
        ("palavra, palavra.", ["palavra", "palavra"]),
        ("palavra\npalavra\tpalavra", ["palavra", "palavra", "palavra"]),
    ])
    def test_extrair_palavras(self, calculador, texto, expected):
        """Testa extração de palavras."""
        resultado = calculador.extrair_palavras(texto)
        assert resultado == expected
    
    @pytest.mark.parametrize("palavras,expected", [
        ([], 0.0),
        (["palavra"], 0.1),
        (["palavra", "simples"], 0.2),
        (["palavra", "muito", "complexa"], 0.3),
    ])
    def test_calcular_densidade_semantica(self, calculador, palavras, expected):
        """Testa cálculo de densidade semântica."""
        resultado = calculador.calcular_densidade_semantica(palavras)
        assert abs(resultado - expected) < 0.001
    
    @pytest.mark.parametrize("palavras,expected", [
        ([], 0),
        (["palavra"], 6),
        (["palavra", "complexa"], 13),
        (["a", "b", "c"], 3),
    ])
    def test_calcular_caracteres_significativos(self, calculador, palavras, expected):
        """Testa cálculo de caracteres significativos."""
        resultado = calculador.calcular_caracteres_significativos(palavras)
        assert resultado == expected
    
    @pytest.mark.parametrize("palavras,expected", [
        ([], 0.0),
        (["palavra"], 0.1),
        (["palavra", "técnica"], 0.2),
        (["processador", "qualcomm", "snapdragon"], 0.3),
    ])
    def test_calcular_complexidade_tecnica(self, calculador, palavras, expected):
        """Testa cálculo de complexidade técnica."""
        resultado = calculador.calcular_complexidade_tecnica(palavras)
        assert abs(resultado - expected) < 0.001
    
    @pytest.mark.parametrize("palavras,expected", [
        ([], 0.0),
        (["palavra"], 0.1),
        (["palavra", "complexa"], 0.2),
        (["palavra", "muito", "complexa"], 0.3),
    ])
    def test_calcular_complexidade_linguistica(self, calculador, palavras, expected):
        """Testa cálculo de complexidade linguística."""
        resultado = calculador.calcular_complexidade_linguistica(palavras)
        assert abs(resultado - expected) < 0.001
    
    @pytest.mark.parametrize("palavras,expected", [
        ([], 0.0),
        (["palavra"], 0.1),
        (["palavra", "longa"], 0.2),
        (["palavra", "muito", "longa"], 0.3),
    ])
    def test_calcular_complexidade_estrutural(self, calculador, palavras, expected):
        """Testa cálculo de complexidade estrutural."""
        resultado = calculador.calcular_complexidade_estrutural(palavras)
        assert abs(resultado - expected) < 0.001
    
    @pytest.mark.parametrize("score,expected_nivel", [
        (0.0, "baixa"),
        (0.3, "baixa"),
        (0.5, "média"),
        (0.7, "alta"),
        (0.9, "muito alta"),
        (1.0, "muito alta"),
    ])
    def test_classificar_nivel_complexidade(self, calculador, score, expected_nivel):
        """Testa classificação de nível de complexidade."""
        resultado = calculador.classificar_nivel_complexidade(score)
        assert resultado == expected_nivel
    
    def test_analisar_complexidade_completo(self, calculador, texto_complexo):
        """Testa análise completa de complexidade."""
        resultado = calculador.analisar_complexidade(texto_complexo)
        
        assert isinstance(resultado, ComplexidadeSemantica)
        assert 0.0 <= resultado.score_complexidade <= 1.0
        assert 0.0 <= resultado.densidade_semantica <= 1.0
        assert resultado.palavras_unicas > 0
        assert resultado.total_palavras > 0
        assert resultado.caracteres_significativos > 0
        assert isinstance(resultado.nivel_complexidade, str)
        assert isinstance(resultado.fatores_complexidade, dict)
        assert isinstance(resultado.metadados, dict)
        
        # Verificar metadados
        assert "texto_original" in resultado.metadados
        assert "texto_normalizado" in resultado.metadados
        assert "configuracao" in resultado.metadados
    
    def test_analisar_complexidade_texto_vazio(self, calculador):
        """Testa análise de texto vazio."""
        resultado = calculador.analisar_complexidade("")
        
        assert isinstance(resultado, ComplexidadeSemantica)
        assert resultado.score_complexidade == 0.0
        assert resultado.densidade_semantica == 0.0
        assert resultado.palavras_unicas == 0
        assert resultado.total_palavras == 0
        assert resultado.caracteres_significativos == 0
        assert resultado.nivel_complexidade == "baixa"
        assert resultado.fatores_complexidade == {}
    
    def test_analisar_complexidade_texto_simples(self, calculador, texto_simples):
        """Testa análise de texto simples."""
        resultado = calculador.analisar_complexidade(texto_simples)
        
        assert isinstance(resultado, ComplexidadeSemantica)
        assert resultado.score_complexidade < 0.5  # Deve ser baixa
        assert resultado.nivel_complexidade == "baixa"
        assert resultado.total_palavras == 2
        assert resultado.palavras_unicas == 2
    
    def test_analisar_complexidade_texto_tecnico(self, calculador, texto_tecnico):
        """Testa análise de texto técnico."""
        resultado = calculador.analisar_complexidade(texto_tecnico)
        
        assert isinstance(resultado, ComplexidadeSemantica)
        assert resultado.score_complexidade > 0.5  # Deve ser alta
        assert resultado.nivel_complexidade in ["alta", "muito alta"]
        assert resultado.total_palavras > 0
        assert resultado.palavras_unicas > 0
    
    def test_analisar_complexidade_com_palavras_tecnicas(self, calculador):
        """Testa análise com palavras técnicas."""
        texto = "processador qualcomm snapdragon 8 gen 2"
        resultado = calculador.analisar_complexidade(texto)
        
        # Verificar se complexidade técnica foi detectada
        fatores = resultado.fatores_complexidade
        assert "complexidade_tecnica" in fatores
        assert fatores["complexidade_tecnica"] > 0.0
    
    def test_analisar_complexidade_com_palavras_complexas(self, calculador):
        """Testa análise com palavras complexas."""
        texto = "sophisticated technological advancement"
        resultado = calculador.analisar_complexidade(texto)
        
        # Verificar se complexidade linguística foi detectada
        fatores = resultado.fatores_complexidade
        assert "complexidade_linguistica" in fatores
        assert fatores["complexidade_linguistica"] > 0.0
    
    def test_analisar_complexidade_com_estrutura_complexa(self, calculador):
        """Testa análise com estrutura complexa."""
        texto = "smartphone android de alta performance com câmera profissional e processador avançado"
        resultado = calculador.analisar_complexidade(texto)
        
        # Verificar se complexidade estrutural foi detectada
        fatores = resultado.fatores_complexidade
        assert "complexidade_estrutural" in fatores
        assert fatores["complexidade_estrutural"] > 0.0
    
    def test_obter_metricas(self, calculador):
        """Testa obtenção de métricas."""
        # Simular algumas análises
        calculador.metricas["total_analises"] = 8
        calculador.metricas["total_textos_processados"] = 8
        calculador.metricas["tempo_total_analise"] = 4.0
        
        metricas = calculador.obter_metricas()
        
        assert "total_analises" in metricas
        assert "total_textos_processados" in metricas
        assert "tempo_total_analise" in metricas
        assert "tempo_medio_analise" in metricas
        assert "textos_por_analise" in metricas
        
        assert metricas["tempo_medio_analise"] == 0.5  # 4.0 / 8
        assert metricas["textos_por_analise"] == 1.0  # 8 / 8
    
    def test_resetar_metricas(self, calculador):
        """Testa reset de métricas."""
        # Simular métricas existentes
        calculador.metricas["total_analises"] = 15
        calculador.metricas["total_textos_processados"] = 15
        
        calculador.resetar_metricas()
        
        assert calculador.metricas["total_analises"] == 0
        assert calculador.metricas["total_textos_processados"] == 0
        assert calculador.metricas["tempo_total_analise"] == 0.0
        assert calculador.metricas["ultima_analise"] is None
    
    def test_analisar_complexidade_atualiza_metricas(self, calculador, texto_complexo):
        """Testa se análise atualiza métricas."""
        metricas_iniciais = calculador.metricas.copy()
        
        calculador.analisar_complexidade(texto_complexo)
        
        # Verificar se métricas foram atualizadas
        assert calculador.metricas["total_analises"] > metricas_iniciais["total_analises"]
        assert calculador.metricas["total_textos_processados"] > metricas_iniciais["total_textos_processados"]
        assert calculador.metricas["tempo_total_analise"] > metricas_iniciais["tempo_total_analise"]
        assert calculador.metricas["ultima_analise"] is not None
    
    def test_analisar_complexidade_com_erro(self, calculador):
        """Testa análise com erro."""
        # Simular erro na extração de palavras
        with patch.object(calculador, 'extrair_palavras', side_effect=Exception("Erro teste")):
            resultado = calculador.analisar_complexidade("texto teste")
            
            # Deve retornar resultado válido mesmo com erro
            assert isinstance(resultado, ComplexidadeSemantica)
            assert resultado.score_complexidade == 0.0
            assert resultado.nivel_complexidade == "erro"
            assert "erro" in resultado.metadados
    
    @pytest.mark.parametrize("texto,expected_complexity", [
        ("palavra", "baixa"),
        ("palavra complexa", "média"),
        ("processador qualcomm snapdragon", "alta"),
        ("sophisticated technological advancement", "muito alta"),
    ])
    def test_classificacao_por_texto(self, calculador, texto, expected_complexity):
        """Testa classificação por tipo de texto."""
        resultado = calculador.analisar_complexidade(texto)
        assert resultado.nivel_complexidade == expected_complexity
    
    def test_consistencia_entre_analises(self, calculador, texto_complexo):
        """Testa consistência entre análises do mesmo texto."""
        resultado1 = calculador.analisar_complexidade(texto_complexo)
        resultado2 = calculador.analisar_complexidade(texto_complexo)
        
        # Resultados devem ser consistentes
        assert abs(resultado1.score_complexidade - resultado2.score_complexidade) < 0.001
        assert resultado1.nivel_complexidade == resultado2.nivel_complexidade
        assert resultado1.total_palavras == resultado2.total_palavras
        assert resultado1.palavras_unicas == resultado2.palavras_unicas
    
    def test_analise_texto_muito_longo(self, calculador):
        """Testa análise de texto muito longo."""
        texto_longo = "palavra " * 500  # 500 palavras
        resultado = calculador.analisar_complexidade(texto_longo)
        
        assert isinstance(resultado, ComplexidadeSemantica)
        assert resultado.total_palavras == 500
        assert resultado.palavras_unicas == 1  # Apenas "palavra"
        assert resultado.score_complexidade < 0.5  # Deve ser baixa para texto repetitivo
    
    def test_analise_texto_com_caracteres_especiais(self, calculador):
        """Testa análise com caracteres especiais."""
        texto = "smartphone@teste.com #hashtag $preco 100%"
        resultado = calculador.analisar_complexidade(texto)
        
        assert isinstance(resultado, ComplexidadeSemantica)
        assert resultado.total_palavras > 0
    
    def test_analise_texto_com_numeros(self, calculador):
        """Testa análise com números."""
        texto = "smartphone 2024 versão 2.0 com 128GB"
        resultado = calculador.analisar_complexidade(texto)
        
        assert isinstance(resultado, ComplexidadeSemantica)
        assert resultado.total_palavras > 0
    
    def test_analise_texto_com_acentos(self, calculador):
        """Testa análise com acentos."""
        texto = "câmera de alta qualidade são paulo"
        resultado = calculador.analisar_complexidade(texto)
        
        assert isinstance(resultado, ComplexidadeSemantica)
        assert resultado.total_palavras > 0
    
    def test_configuracao_personalizada(self):
        """Testa configuração personalizada do calculador."""
        config = {
            "min_caracteres": 5,
            "palavras_tecnicas": ["python", "javascript"],
            "palavras_complexas": ["sophisticated", "advanced"]
        }
        
        calculador = CalculadorComplexidadeSemantica(config)
        
        assert calculador._min_caracteres == 5
        assert "python" in calculador._palavras_tecnicas
        assert "javascript" in calculador._palavras_tecnicas
        assert "sophisticated" in calculador._palavras_complexas
        assert "advanced" in calculador._palavras_complexas
    
    def test_fatores_complexidade_completos(self, calculador, texto_complexo):
        """Testa se todos os fatores de complexidade estão presentes."""
        resultado = calculador.analisar_complexidade(texto_complexo)
        
        fatores = resultado.fatores_complexidade
        assert "densidade_semantica" in fatores
        assert "complexidade_tecnica" in fatores
        assert "complexidade_linguistica" in fatores
        assert "complexidade_estrutural" in fatores
        
        # Verificar valores dos fatores
        for fator, valor in fatores.items():
            assert 0.0 <= valor <= 1.0
    
    def test_relacao_entre_fatores_e_score(self, calculador, texto_complexo):
        """Testa relação entre fatores e score final."""
        resultado = calculador.analisar_complexidade(texto_complexo)
        
        fatores = resultado.fatores_complexidade
        score_calculado = (
            fatores["densidade_semantica"] * 0.25 +
            fatores["complexidade_tecnica"] * 0.25 +
            fatores["complexidade_linguistica"] * 0.25 +
            fatores["complexidade_estrutural"] * 0.25
        )
        
        # Score calculado deve ser próximo ao score final
        assert abs(resultado.score_complexidade - score_calculado) < 0.1 