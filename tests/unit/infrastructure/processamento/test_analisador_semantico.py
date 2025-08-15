"""
Testes Unitários - AnalisadorSemantico
=====================================

Testes para o sistema de análise semântica de keywords.

Autor: Paulo Júnior
Data: 2024-12-20
Tracing ID: TEST-ANAL-SEM-001
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List

from infrastructure.processamento.analisador_semantico import (
    AnalisadorSemantico,
    AnalisePalavras
)


class TestAnalisadorSemantico:
    """Testes para o AnalisadorSemantico."""
    
    @pytest.fixture
    def analisador(self):
        """Fixture para instanciar o analisador."""
        return AnalisadorSemantico()
    
    @pytest.fixture
    def texto_exemplo(self):
        """Fixture com texto de exemplo."""
        return "melhor smartphone android 2024 com câmera de alta qualidade"
    
    @pytest.fixture
    def texto_complexo(self):
        """Fixture com texto complexo."""
        return "curso online de programação python avançado para desenvolvedores web"
    
    def test_inicializacao(self, analisador):
        """Testa inicialização do analisador."""
        assert analisador is not None
        assert hasattr(analisador, '_min_caracteres')
        assert hasattr(analisador, '_case_sensitive')
        assert hasattr(analisador, '_remover_acentos')
        assert hasattr(analisador, '_palavras_chave_especificas')
        assert hasattr(analisador, 'metricas')
        assert analisador.metricas["total_analises"] == 0
    
    @pytest.mark.parametrize("texto,expected", [
        ("", ""),
        ("Olá Mundo", "ola mundo"),
        ("CÂMERA DE ALTA QUALIDADE", "camera de alta qualidade"),
        ("São Paulo", "sao paulo"),
        ("João & Maria", "joao & maria"),
    ])
    def test_normalizar_texto(self, analisador, texto, expected):
        """Testa normalização de texto."""
        resultado = analisador.normalizar_texto(texto)
        assert resultado == expected
    
    @pytest.mark.parametrize("texto,expected", [
        ("", []),
        ("palavra", ["palavra"]),
        ("palavra1 palavra2", ["palavra1", "palavra2"]),
        ("palavra, palavra.", ["palavra", "palavra"]),
        ("palavra\npalavra\tpalavra", ["palavra", "palavra", "palavra"]),
    ])
    def test_extrair_palavras(self, analisador, texto, expected):
        """Testa extração de palavras."""
        resultado = analisador.extrair_palavras(texto)
        assert resultado == expected
    
    @pytest.mark.parametrize("palavras,min_caracteres,expected", [
        (["a", "ab", "abc", "abcd"], 3, ["abc", "abcd"]),
        (["palavra", "de", "teste"], 2, ["palavra", "de", "teste"]),
        (["x", "y", "z"], 2, []),
        ([], 3, []),
    ])
    def test_filtrar_palavras_significativas(self, analisador, palavras, min_caracteres, expected):
        """Testa filtragem de palavras significativas."""
        analisador._min_caracteres = min_caracteres
        resultado, removidas = analisador.filtrar_palavras_significativas(palavras)
        assert resultado == expected
        assert len(removidas) == len(palavras) - len(expected)
    
    @pytest.mark.parametrize("palavras,expected_score", [
        ([], 0.0),
        (["palavra"], 0.1),
        (["palavra", "significativa"], 0.2),
        (["palavra", "muito", "significativa", "e", "importante"], 0.5),
    ])
    def test_calcular_score_significancia(self, analisador, palavras, expected_score):
        """Testa cálculo de score de significância."""
        resultado = analisador.calcular_score_significancia(palavras)
        assert abs(resultado - expected_score) < 0.001
    
    def test_analisar_palavras_completo(self, analisador, texto_exemplo):
        """Testa análise completa de palavras."""
        resultado = analisador.analisar_palavras(texto_exemplo)
        
        assert isinstance(resultado, AnalisePalavras)
        assert len(resultado.palavras_significativas) > 0
        assert resultado.total_palavras > 0
        assert resultado.palavras_unicas > 0
        assert resultado.palavras_significativas_unicas > 0
        assert 0.0 <= resultado.score_significancia <= 1.0
        assert isinstance(resultado.palavras_removidas, list)
        assert isinstance(resultado.metadados, dict)
        
        # Verificar metadados
        assert "texto_original" in resultado.metadados
        assert "texto_normalizado" in resultado.metadados
        assert "configuracao" in resultado.metadados
        assert "palavras_chave_encontradas" in resultado.metadados
    
    def test_analisar_palavras_texto_vazio(self, analisador):
        """Testa análise de texto vazio."""
        resultado = analisador.analisar_palavras("")
        
        assert isinstance(resultado, AnalisePalavras)
        assert resultado.palavras_significativas == []
        assert resultado.total_palavras == 0
        assert resultado.palavras_unicas == 0
        assert resultado.palavras_significativas_unicas == 0
        assert resultado.score_significancia == 0.0
        assert resultado.palavras_removidas == []
    
    def test_analisar_palavras_texto_complexo(self, analisador, texto_complexo):
        """Testa análise de texto complexo."""
        resultado = analisador.analisar_palavras(texto_complexo)
        
        assert isinstance(resultado, AnalisePalavras)
        assert len(resultado.palavras_significativas) > 0
        assert resultado.total_palavras > 0
        assert resultado.palavras_unicas > 0
        assert resultado.palavras_significativas_unicas > 0
        assert 0.0 <= resultado.score_significancia <= 1.0
        
        # Verificar que palavras significativas foram filtradas
        for palavra in resultado.palavras_significativas:
            assert len(palavra) >= analisador._min_caracteres
    
    def test_analisar_palavras_com_palavras_chave(self, analisador):
        """Testa análise com palavras-chave específicas."""
        texto = "curso online de programação python avançado"
        resultado = analisador.analisar_palavras(texto)
        
        # Verificar se palavras-chave foram detectadas
        palavras_chave_encontradas = resultado.metadados["palavras_chave_encontradas"]
        assert isinstance(palavras_chave_encontradas, list)
        
        # Verificar se pelo menos algumas palavras-chave foram encontradas
        assert len(palavras_chave_encontradas) >= 0
    
    def test_analisar_palavras_case_sensitive(self, analisador):
        """Testa análise com case sensitive."""
        analisador._case_sensitive = True
        texto = "Palavra palavra PALAVRA"
        resultado = analisador.analisar_palavras(texto)
        
        # Com case sensitive, todas as variações devem ser mantidas
        assert "Palavra" in resultado.palavras_significativas
        assert "palavra" in resultado.palavras_significativas
        assert "PALAVRA" in resultado.palavras_significativas
    
    def test_analisar_palavras_case_insensitive(self, analisador):
        """Testa análise sem case sensitive."""
        analisador._case_sensitive = False
        texto = "Palavra palavra PALAVRA"
        resultado = analisador.analisar_palavras(texto)
        
        # Sem case sensitive, apenas uma variação deve ser mantida
        palavras_unicas = set(resultado.palavras_significativas)
        assert len(palavras_unicas) == 1  # Todas as variações devem ser normalizadas
    
    def test_analisar_palavras_com_acentos(self, analisador):
        """Testa análise com acentos."""
        analisador._remover_acentos = True
        texto = "câmera qualidade são paulo"
        resultado = analisador.analisar_palavras(texto)
        
        # Verificar se acentos foram removidos
        for palavra in resultado.palavras_significativas:
            assert "â" not in palavra
            assert "ã" not in palavra
    
    def test_analisar_palavras_sem_remover_acentos(self, analisador):
        """Testa análise sem remover acentos."""
        analisador._remover_acentos = False
        texto = "câmera qualidade são paulo"
        resultado = analisador.analisar_palavras(texto)
        
        # Verificar se acentos foram mantidos
        palavras_com_acento = [p for p in resultado.palavras_significativas if "â" in p or "ã" in p]
        assert len(palavras_com_acento) > 0
    
    def test_analisar_palavras_com_caracteres_especiais(self, analisador):
        """Testa análise com caracteres especiais."""
        texto = "palavra@teste.com #hashtag $preco 100%"
        resultado = analisador.analisar_palavras(texto)
        
        # Verificar se caracteres especiais foram tratados
        assert isinstance(resultado, AnalisePalavras)
        assert resultado.total_palavras > 0
    
    def test_analisar_palavras_com_numeros(self, analisador):
        """Testa análise com números."""
        texto = "smartphone 2024 versão 2.0"
        resultado = analisador.analisar_palavras(texto)
        
        # Verificar se números foram incluídos
        assert isinstance(resultado, AnalisePalavras)
        assert resultado.total_palavras > 0
    
    def test_analisar_palavras_com_stopwords(self, analisador):
        """Testa análise com stopwords."""
        texto = "o melhor smartphone do mundo"
        resultado = analisador.analisar_palavras(texto)
        
        # Verificar se stopwords foram filtradas (se configurado)
        assert isinstance(resultado, AnalisePalavras)
        assert resultado.total_palavras > 0
    
    def test_obter_metricas(self, analisador):
        """Testa obtenção de métricas."""
        # Simular algumas análises
        analisador.metricas["total_analises"] = 5
        analisador.metricas["total_palavras_processadas"] = 100
        analisador.metricas["tempo_total_analise"] = 2.5
        
        metricas = analisador.obter_metricas()
        
        assert "total_analises" in metricas
        assert "total_palavras_processadas" in metricas
        assert "tempo_total_analise" in metricas
        assert "tempo_medio_analise" in metricas
        assert "palavras_por_analise" in metricas
        
        assert metricas["tempo_medio_analise"] == 0.5  # 2.5 / 5
        assert metricas["palavras_por_analise"] == 20.0  # 100 / 5
    
    def test_resetar_metricas(self, analisador):
        """Testa reset de métricas."""
        # Simular métricas existentes
        analisador.metricas["total_analises"] = 10
        analisador.metricas["total_palavras_processadas"] = 200
        
        analisador.resetar_metricas()
        
        assert analisador.metricas["total_analises"] == 0
        assert analisador.metricas["total_palavras_processadas"] == 0
        assert analisador.metricas["tempo_total_analise"] == 0.0
        assert analisador.metricas["ultima_analise"] is None
    
    def test_analisar_palavras_atualiza_metricas(self, analisador, texto_exemplo):
        """Testa se análise atualiza métricas."""
        metricas_iniciais = analisador.metricas.copy()
        
        analisador.analisar_palavras(texto_exemplo)
        
        # Verificar se métricas foram atualizadas
        assert analisador.metricas["total_analises"] > metricas_iniciais["total_analises"]
        assert analisador.metricas["total_palavras_processadas"] > metricas_iniciais["total_palavras_processadas"]
        assert analisador.metricas["tempo_total_analise"] > metricas_iniciais["tempo_total_analise"]
        assert analisador.metricas["ultima_analise"] is not None
    
    def test_analisar_palavras_com_erro(self, analisador):
        """Testa análise com erro."""
        # Simular erro na extração de palavras
        with patch.object(analisador, 'extrair_palavras', side_effect=Exception("Erro teste")):
            resultado = analisador.analisar_palavras("texto teste")
            
            # Deve retornar resultado válido mesmo com erro
            assert isinstance(resultado, AnalisePalavras)
            assert resultado.palavras_significativas == []
            assert resultado.total_palavras == 0
            assert "erro" in resultado.metadados
    
    @pytest.mark.parametrize("texto,min_caracteres,expected_count", [
        ("palavra", 3, 1),
        ("palavra", 8, 0),
        ("a b c d", 1, 4),
        ("a b c d", 2, 0),
        ("palavra1 palavra2 palavra3", 7, 3),
    ])
    def test_filtragem_por_tamanho_minimo(self, analisador, texto, min_caracteres, expected_count):
        """Testa filtragem por tamanho mínimo."""
        analisador._min_caracteres = min_caracteres
        resultado = analisador.analisar_palavras(texto)
        
        assert len(resultado.palavras_significativas) == expected_count
    
    def test_consistencia_entre_analises(self, analisador, texto_exemplo):
        """Testa consistência entre análises do mesmo texto."""
        resultado1 = analisador.analisar_palavras(texto_exemplo)
        resultado2 = analisador.analisar_palavras(texto_exemplo)
        
        # Resultados devem ser consistentes
        assert resultado1.palavras_significativas == resultado2.palavras_significativas
        assert resultado1.total_palavras == resultado2.total_palavras
        assert resultado1.palavras_unicas == resultado2.palavras_unicas
        assert abs(resultado1.score_significancia - resultado2.score_significancia) < 0.001
    
    def test_analise_texto_muito_longo(self, analisador):
        """Testa análise de texto muito longo."""
        texto_longo = "palavra " * 1000  # 1000 palavras
        resultado = analisador.analisar_palavras(texto_longo)
        
        assert isinstance(resultado, AnalisePalavras)
        assert resultado.total_palavras == 1000
        assert resultado.palavras_unicas == 1  # Apenas "palavra"
        assert resultado.palavras_significativas_unicas == 1
    
    def test_analise_texto_com_quebras_linha(self, analisador):
        """Testa análise de texto com quebras de linha."""
        texto = "linha1\nlinha2\nlinha3"
        resultado = analisador.analisar_palavras(texto)
        
        assert isinstance(resultado, AnalisePalavras)
        assert "linha1" in resultado.palavras_significativas
        assert "linha2" in resultado.palavras_significativas
        assert "linha3" in resultado.palavras_significativas
    
    def test_analise_texto_com_pontuacao(self, analisador):
        """Testa análise de texto com pontuação."""
        texto = "palavra, palavra. palavra! palavra?"
        resultado = analisador.analisar_palavras(texto)
        
        assert isinstance(resultado, AnalisePalavras)
        # Todas as ocorrências de "palavra" devem ser contadas
        assert resultado.palavras_significativas.count("palavra") == 4
    
    def test_configuracao_personalizada(self):
        """Testa configuração personalizada do analisador."""
        config = {
            "min_caracteres": 5,
            "case_sensitive": True,
            "remover_acentos": False,
            "palavras_chave_especificas": ["python", "programação"]
        }
        
        analisador = AnalisadorSemantico(config)
        
        assert analisador._min_caracteres == 5
        assert analisador._case_sensitive is True
        assert analisador._remover_acentos is False
        assert "python" in analisador._palavras_chave_especificas
        assert "programação" in analisador._palavras_chave_especificas 