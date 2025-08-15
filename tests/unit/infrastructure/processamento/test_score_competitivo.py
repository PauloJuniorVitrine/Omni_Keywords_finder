"""
Testes Unitários - CalculadorScoreCompetitivo
============================================

Testes para o sistema de cálculo de score competitivo de keywords.

Autor: Paulo Júnior
Data: 2024-12-20
Tracing ID: TEST-SCORE-COMP-001
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List

from infrastructure.processamento.score_competitivo import (
    CalculadorScoreCompetitivo,
    ScoreCompetitivo,
    NivelCompetitividade
)


class TestCalculadorScoreCompetitivo:
    """Testes para o CalculadorScoreCompetitivo."""
    
    @pytest.fixture
    def calculador(self):
        """Fixture para instanciar o calculador."""
        return CalculadorScoreCompetitivo()
    
    @pytest.fixture
    def keyword_exemplo(self):
        """Fixture com keyword de exemplo."""
        return "melhor smartphone 2024"
    
    @pytest.fixture
    def dados_mercado_exemplo(self):
        """Fixture com dados de mercado de exemplo."""
        return {
            "volume": 5000,
            "cpc": 2.50,
            "concorrencia": 0.7
        }
    
    def test_inicializacao(self, calculador):
        """Testa inicialização do calculador."""
        assert calculador is not None
        assert hasattr(calculador, 'configuracoes_nicho')
        assert hasattr(calculador, 'metricas')
        assert calculador.metricas["total_calculos"] == 0
    
    @pytest.mark.parametrize("volume,max_volume,expected", [
        (0, 1000, 0.0),
        (100, 1000, 0.1),
        (500, 1000, 0.5),
        (1000, 1000, 1.0),
        (1500, 1000, 1.0),  # Limite máximo
    ])
    def test_normalizar_volume(self, calculador, volume, max_volume, expected):
        """Testa normalização de volume."""
        resultado = calculador.normalizar_volume(volume, max_volume)
        assert resultado == expected
    
    @pytest.mark.parametrize("cpc,max_cpc,expected", [
        (0.0, 10.0, 0.0),
        (2.5, 10.0, 0.25),
        (5.0, 10.0, 0.5),
        (10.0, 10.0, 1.0),
        (15.0, 10.0, 1.0),  # Limite máximo
    ])
    def test_normalizar_cpc(self, calculador, cpc, max_cpc, expected):
        """Testa normalização de CPC."""
        resultado = calculador.normalizar_cpc(cpc, max_cpc)
        assert resultado == expected
    
    @pytest.mark.parametrize("concorrencia,max_concorrencia,expected", [
        (0.0, 1.0, 0.0),
        (0.3, 1.0, 0.3),
        (0.7, 1.0, 0.7),
        (1.0, 1.0, 1.0),
        (1.5, 1.0, 1.0),  # Limite máximo
    ])
    def test_normalizar_concorrencia(self, calculador, concorrencia, max_concorrencia, expected):
        """Testa normalização de concorrência."""
        resultado = calculador.normalizar_concorrencia(concorrencia, max_concorrencia)
        assert resultado == expected
    
    @pytest.mark.parametrize("keyword,expected_nicho", [
        ("comprar smartphone online", "e-commerce"),
        ("sintomas gripe tratamento", "saude"),
        ("melhor software desenvolvimento", "tecnologia"),
        ("curso python online", "educacao"),
        ("investimento ações renda fixa", "financas"),
        ("palavra genérica qualquer", "padrao"),
    ])
    def test_detectar_nicho(self, calculador, keyword, expected_nicho):
        """Testa detecção automática de nicho."""
        resultado = calculador.detectar_nicho(keyword)
        assert resultado == expected_nicho
    
    def test_obter_configuracao_nicho(self, calculador):
        """Testa obtenção de configuração por nicho."""
        config = calculador.obter_configuracao_nicho("e-commerce")
        assert config is not None
        assert "peso_volume" in config
        assert "peso_cpc" in config
        assert "peso_concorrencia" in config
        assert "max_volume" in config
        assert "max_cpc" in config
        assert "max_concorrencia" in config
    
    def test_obter_configuracao_nicho_inexistente(self, calculador):
        """Testa obtenção de configuração para nicho inexistente."""
        config = calculador.obter_configuracao_nicho("nicho_inexistente")
        assert config is not None
        # Deve retornar configuração padrão
    
    @pytest.mark.parametrize("volume,cpc,concorrencia,config_nicho", [
        (1000, 2.0, 0.5, {
            "max_volume": 10000,
            "max_cpc": 10.0,
            "max_concorrencia": 1.0
        }),
        (500, 1.5, 0.3, {
            "max_volume": 5000,
            "max_cpc": 5.0,
            "max_concorrencia": 0.8
        }),
    ])
    def test_calcular_fatores_competitivos(self, calculador, volume, cpc, concorrencia, config_nicho):
        """Testa cálculo de fatores competitivos."""
        fatores = calculador.calcular_fatores_competitivos(volume, cpc, concorrencia, config_nicho)
        
        assert "volume_normalizado" in fatores
        assert "cpc_normalizado" in fatores
        assert "concorrencia_normalizada" in fatores
        assert "concorrencia_invertida" in fatores
        
        # Verificar valores normalizados
        assert 0.0 <= fatores["volume_normalizado"] <= 1.0
        assert 0.0 <= fatores["cpc_normalizado"] <= 1.0
        assert 0.0 <= fatores["concorrencia_normalizada"] <= 1.0
        assert 0.0 <= fatores["concorrencia_invertida"] <= 1.0
        
        # Verificar relação entre concorrência e concorrência invertida
        assert abs(fatores["concorrencia_normalizada"] + fatores["concorrencia_invertida"] - 1.0) < 0.001
    
    @pytest.mark.parametrize("fatores,config_nicho", [
        ({
            "volume_normalizado": 0.5,
            "cpc_normalizado": 0.3,
            "concorrencia_normalizada": 0.4,
            "concorrencia_invertida": 0.6
        }, {
            "peso_volume": 0.4,
            "peso_cpc": 0.4,
            "peso_concorrencia": 0.2
        }),
        ({
            "volume_normalizado": 0.8,
            "cpc_normalizado": 0.6,
            "concorrencia_normalizada": 0.2,
            "concorrencia_invertida": 0.8
        }, {
            "peso_volume": 0.3,
            "peso_cpc": 0.5,
            "peso_concorrencia": 0.2
        }),
    ])
    def test_calcular_score_competitivo(self, calculador, fatores, config_nicho):
        """Testa cálculo do score competitivo."""
        score = calculador.calcular_score_competitivo(fatores, config_nicho)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # Verificar se o cálculo está correto
        expected_score = (
            fatores["volume_normalizado"] * config_nicho["peso_volume"] +
            fatores["cpc_normalizado"] * config_nicho["peso_cpc"] +
            fatores["concorrencia_invertida"] * config_nicho["peso_concorrencia"]
        )
        assert abs(score - expected_score) < 0.001
    
    @pytest.mark.parametrize("score,config_nicho,expected_nivel", [
        (0.1, {"threshold_baixa": 0.25, "threshold_media": 0.55, "threshold_alta": 0.8}, NivelCompetitividade.BAIXA),
        (0.4, {"threshold_baixa": 0.25, "threshold_media": 0.55, "threshold_alta": 0.8}, NivelCompetitividade.MEDIA),
        (0.7, {"threshold_baixa": 0.25, "threshold_media": 0.55, "threshold_alta": 0.8}, NivelCompetitividade.ALTA),
        (0.9, {"threshold_baixa": 0.25, "threshold_media": 0.55, "threshold_alta": 0.8}, NivelCompetitividade.MUITO_ALTA),
    ])
    def test_classificar_competitividade(self, calculador, score, config_nicho, expected_nivel):
        """Testa classificação de competitividade."""
        nivel = calculador.classificar_competitividade(score, config_nicho)
        assert nivel == expected_nivel
    
    def test_calcular_score_completo(self, calculador, keyword_exemplo, dados_mercado_exemplo):
        """Testa cálculo completo de score competitivo."""
        resultado = calculador.calcular_score(
            keyword_exemplo,
            dados_mercado_exemplo["volume"],
            dados_mercado_exemplo["cpc"],
            dados_mercado_exemplo["concorrencia"]
        )
        
        assert isinstance(resultado, ScoreCompetitivo)
        assert resultado.metadados["keyword"] == keyword_exemplo
        assert 0.0 <= resultado.score_final <= 1.0
        assert isinstance(resultado.nivel_competitividade, NivelCompetitividade)
        assert 0.0 <= resultado.volume_normalizado <= 1.0
        assert 0.0 <= resultado.cpc_normalizado <= 1.0
        assert 0.0 <= resultado.concorrencia_normalizada <= 1.0
        assert isinstance(resultado.fatores_competitivos, dict)
        assert isinstance(resultado.metadados, dict)
        
        # Verificar metadados
        assert "keyword" in resultado.metadados
        assert "nicho_detectado" in resultado.metadados
        assert "valores_originais" in resultado.metadados
    
    def test_calcular_score_com_metadados(self, calculador, keyword_exemplo, dados_mercado_exemplo):
        """Testa cálculo de score com metadados adicionais."""
        metadados = {
            "fonte": "google_keyword_planner",
            "data_coleta": "2024-12-20",
            "regiao": "BR"
        }
        
        resultado = calculador.calcular_score(
            keyword_exemplo,
            dados_mercado_exemplo["volume"],
            dados_mercado_exemplo["cpc"],
            dados_mercado_exemplo["concorrencia"],
            metadados
        )
        
        assert resultado.metadados["metadados_entrada"] == metadados
    
    def test_gerar_relatorio_competitividade(self, calculador):
        """Testa geração de relatório de competitividade."""
        # Criar scores de exemplo
        scores = [
            ScoreCompetitivo(
                score_final=0.8,
                nivel_competitividade=NivelCompetitividade.ALTA,
                volume_normalizado=0.7,
                cpc_normalizado=0.6,
                concorrencia_normalizada=0.3,
                fatores_competitivos={},
                metadados={"keyword": "teste1", "nicho_detectado": "tecnologia"}
            ),
            ScoreCompetitivo(
                score_final=0.4,
                nivel_competitividade=NivelCompetitividade.MEDIA,
                volume_normalizado=0.5,
                cpc_normalizado=0.4,
                concorrencia_normalizada=0.6,
                fatores_competitivos={},
                metadados={"keyword": "teste2", "nicho_detectado": "e-commerce"}
            )
        ]
        
        relatorio = calculador.gerar_relatorio_competitividade(scores)
        
        assert "estatisticas_gerais" in relatorio
        assert "distribuicao_niveis" in relatorio
        assert "distribuicao_nichos" in relatorio
        assert "top_keywords" in relatorio
        
        # Verificar estatísticas
        stats = relatorio["estatisticas_gerais"]
        assert stats["total_keywords"] == 2
        assert stats["score_medio"] == 0.6  # (0.8 + 0.4) / 2
        assert stats["score_maximo"] == 0.8
        assert stats["score_minimo"] == 0.4
    
    def test_gerar_relatorio_vazio(self, calculador):
        """Testa geração de relatório com lista vazia."""
        relatorio = calculador.gerar_relatorio_competitividade([])
        assert "erro" in relatorio
        assert relatorio["erro"] == "Nenhuma keyword para análise"
    
    def test_obter_metricas(self, calculador):
        """Testa obtenção de métricas."""
        # Simular alguns cálculos
        calculador.metricas["total_calculos"] = 10
        calculador.metricas["total_keywords_processadas"] = 50
        calculador.metricas["tempo_total_calculo"] = 5.0
        
        metricas = calculador.obter_metricas()
        
        assert "total_calculos" in metricas
        assert "total_keywords_processadas" in metricas
        assert "tempo_total_calculo" in metricas
        assert "tempo_medio_calculo" in metricas
        assert "keywords_por_calculo" in metricas
        
        assert metricas["tempo_medio_calculo"] == 0.5  # 5.0 / 10
        assert metricas["keywords_por_calculo"] == 5.0  # 50 / 10
    
    def test_resetar_metricas(self, calculador):
        """Testa reset de métricas."""
        # Simular métricas existentes
        calculador.metricas["total_calculos"] = 10
        calculador.metricas["total_keywords_processadas"] = 50
        
        calculador.resetar_metricas()
        
        assert calculador.metricas["total_calculos"] == 0
        assert calculador.metricas["total_keywords_processadas"] == 0
        assert calculador.metricas["tempo_total_calculo"] == 0.0
        assert calculador.metricas["ultimo_calculo"] is None
    
    @pytest.mark.parametrize("keyword,volume,cpc,concorrencia", [
        ("smartphone barato", 1000, 1.5, 0.4),
        ("curso online python", 500, 2.0, 0.6),
        ("investimento renda fixa", 2000, 3.0, 0.3),
    ])
    def test_fluxo_completo_calculo(self, calculador, keyword, volume, cpc, concorrencia):
        """Testa fluxo completo de cálculo."""
        resultado = calculador.calcular_score(keyword, volume, cpc, concorrencia)
        
        # Verificar estrutura do resultado
        assert isinstance(resultado, ScoreCompetitivo)
        assert resultado.metadados["keyword"] == keyword
        assert 0.0 <= resultado.score_final <= 1.0
        
        # Verificar que métricas foram atualizadas
        assert calculador.metricas["total_calculos"] > 0
        assert calculador.metricas["total_keywords_processadas"] > 0
        assert calculador.metricas["tempo_total_calculo"] > 0.0
    
    def test_tratamento_erro_calculo(self, calculador):
        """Testa tratamento de erro durante cálculo."""
        # Simular erro na detecção de nicho
        with patch.object(calculador, 'detectar_nicho', side_effect=Exception("Erro teste")):
            resultado = calculador.calcular_score("teste", 100, 1.0, 0.5)
            
            # Deve retornar resultado válido mesmo com erro
            assert isinstance(resultado, ScoreCompetitivo)
            assert resultado.metadados["keyword"] == "teste"
    
    def test_configuracoes_nicho_completas(self, calculador):
        """Testa se todas as configurações de nicho estão completas."""
        nichos = ["e-commerce", "saude", "tecnologia", "educacao", "financas"]
        
        for nicho in nichos:
            config = calculador.obter_configuracao_nicho(nicho)
            
            # Verificar campos obrigatórios
            campos_obrigatorios = [
                "peso_volume", "peso_cpc", "peso_concorrencia",
                "max_volume", "max_cpc", "max_concorrencia",
                "threshold_baixa", "threshold_media", "threshold_alta"
            ]
            
            for campo in campos_obrigatorios:
                assert campo in config, f"Campo {campo} ausente na configuração do nicho {nicho}"
                assert config[campo] is not None, f"Campo {campo} é None na configuração do nicho {nicho}"
    
    def test_consistencia_niveis_competitividade(self, calculador):
        """Testa consistência dos níveis de competitividade."""
        config_padrao = calculador.obter_configuracao_nicho("e-commerce")
        
        # Testar todos os níveis possíveis
        scores_teste = [0.1, 0.4, 0.7, 0.9]
        niveis_esperados = [
            NivelCompetitividade.BAIXA,
            NivelCompetitividade.MEDIA,
            NivelCompetitividade.ALTA,
            NivelCompetitividade.MUITO_ALTA
        ]
        
        for score, nivel_esperado in zip(scores_teste, niveis_esperados):
            nivel = calculador.classificar_competitividade(score, config_padrao)
            assert nivel == nivel_esperado, f"Score {score} deveria ser {nivel_esperado}, mas foi {nivel}" 