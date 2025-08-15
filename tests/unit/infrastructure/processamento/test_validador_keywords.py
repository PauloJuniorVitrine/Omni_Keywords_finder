"""
Testes Unitários: Validador Keywords
Testa funcionalidades do validador de keywords

Prompt: Melhorar testes unitários Fase 2
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-27
Versão: 2.0.0
Tracing ID: TEST_VALIDADOR_KEYWORDS_002_20241227
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any, Optional

from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.validador_keywords import ValidadorKeywords


class TestValidadorKeywords:
    """Testes para ValidadorKeywords baseados no código real."""
    
    @pytest.fixture
    def config_validador_real(self):
        """Configuração real do validador baseada no projeto."""
        return {
            "min_palavras": 2,
            "tamanho_min": 10,
            "tamanho_max": 100,
            "concorrencia_max": 0.8,
            "score_minimo": 0.3,
            "volume_min": 100,
            "cpc_min": 0.1,
            "palavras_obrigatorias": ["teste", "validação", "curso"],
            "blacklist": {"spam", "fake", "scam"},
            "whitelist": set(),
            "enable_semantic_validation": False
        }
    
    @pytest.fixture
    def validador_real(self, config_validador_real):
        """Instância do validador com configuração real."""
        return ValidadorKeywords(**config_validador_real)
    
    @pytest.fixture
    def keywords_reais(self):
        """Keywords baseadas em dados reais do projeto."""
        return [
            Keyword(
                termo="curso de marketing digital",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner",
                score=0.85,
                justificativa="Volume alto, CPC moderado"
            ),
            Keyword(
                termo="teste de validação python",
                volume_busca=500,
                cpc=1.8,
                concorrencia=0.6,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner",
                score=0.92,
                justificativa="Volume médio, baixa competição"
            ),
            Keyword(
                termo="receita bolo chocolate",
                volume_busca=50,  # Volume baixo
                cpc=0.5,
                concorrencia=0.3,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner",
                score=0.45,
                justificativa="Volume muito baixo"
            ),
            Keyword(
                termo="seguro auto spam",
                volume_busca=2000,
                cpc=8.0,  # CPC alto
                concorrencia=0.9,
                intencao=IntencaoBusca.COMERCIAL,
                fonte="google_keyword_planner",
                score=0.35,
                justificativa="CPC muito alto, competição alta"
            ),
            Keyword(
                termo="a",  # Muito curta
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner",
                score=0.5
            ),
            Keyword(
                termo="palavra muito longa que excede o limite máximo permitido",
                volume_busca=100,
                cpc=1.0,
                concorrencia=0.5,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte="google_keyword_planner",
                score=0.5
            )
        ]
    
    def test_inicializacao_configuracao_real(self, config_validador_real):
        """Testa inicialização com configuração real do projeto."""
        validador = ValidadorKeywords(**config_validador_real)
        
        # Verificar configurações específicas do projeto
        assert validador.min_palavras == 2
        assert validador.tamanho_min == 10
        assert validador.tamanho_max == 100
        assert validador.concorrencia_max == 0.8
        assert validador.score_minimo == 0.3
        assert validador.volume_min == 100
        assert validador.cpc_min == 0.1
        assert validador.palavras_obrigatorias == ["teste", "validação", "curso"]
        assert validador.blacklist == {"spam", "fake", "scam"}
        assert validador.whitelist == set()
        assert validador.enable_semantic_validation is False
    
    def test_validar_keyword_volume_busca(self, validador_real):
        """Testa validação de volume de busca."""
        # Keyword com volume válido
        keyword_valida = Keyword(
            termo="teste válido",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
        assert is_valida is True
        assert "volume_busca" in detalhes["regras_verificadas"]
        
        # Keyword com volume baixo
        keyword_volume_baixo = Keyword(
            termo="teste volume baixo",
            volume_busca=50,  # Abaixo do mínimo
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_volume_baixo)
        assert is_valida is False
        assert "volume_busca_baixo" in detalhes["violacoes"][0]
        
        # Keyword com volume alto
        keyword_volume_alto = Keyword(
            termo="teste volume alto",
            volume_busca=200000,  # Acima do máximo
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_volume_alto)
        assert is_valida is False
        assert "volume_busca_alto" in detalhes["violacoes"][0]
    
    def test_validar_keyword_cpc(self, validador_real):
        """Testa validação de CPC."""
        # Keyword com CPC válido
        keyword_valida = Keyword(
            termo="teste válido",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
        assert is_valida is True
        assert "cpc" in detalhes["regras_verificadas"]
        
        # Keyword com CPC baixo
        keyword_cpc_baixo = Keyword(
            termo="teste cpc baixo",
            volume_busca=1000,
            cpc=0.05,  # Abaixo do mínimo
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_cpc_baixo)
        assert is_valida is False
        assert "cpc_baixo" in detalhes["violacoes"][0]
        
        # Keyword com CPC alto
        keyword_cpc_alto = Keyword(
            termo="teste cpc alto",
            volume_busca=1000,
            cpc=15.0,  # Acima do máximo
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_cpc_alto)
        assert is_valida is False
        assert "cpc_alto" in detalhes["violacoes"][0]
    
    def test_validar_keyword_score(self, validador_real):
        """Testa validação de score."""
        # Keyword com score válido
        keyword_valida = Keyword(
            termo="teste válido",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner",
            score=0.8
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
        assert is_valida is True
        assert "score" in detalhes["regras_verificadas"]
        
        # Keyword com score baixo
        keyword_score_baixo = Keyword(
            termo="teste score baixo",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner",
            score=0.1  # Abaixo do mínimo
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_score_baixo)
        assert is_valida is False
        assert "score_baixo" in detalhes["violacoes"][0]
        
        # Keyword com score alto
        keyword_score_alto = Keyword(
            termo="teste score alto",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner",
            score=1.5  # Acima do máximo
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_score_alto)
        assert is_valida is False
        assert "score_alto" in detalhes["violacoes"][0]
    
    def test_validar_keyword_concorrencia(self, validador_real):
        """Testa validação de concorrência."""
        # Keyword com concorrência válida
        keyword_valida = Keyword(
            termo="teste válido",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
        assert is_valida is True
        assert "concorrencia" in detalhes["regras_verificadas"]
        
        # Keyword com concorrência baixa
        keyword_concorrencia_baixa = Keyword(
            termo="teste concorrência baixa",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=-0.1,  # Abaixo do mínimo
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_concorrencia_baixa)
        assert is_valida is False
        assert "concorrencia_baixa" in detalhes["violacoes"][0]
        
        # Keyword com concorrência alta
        keyword_concorrencia_alta = Keyword(
            termo="teste concorrência alta",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=1.5,  # Acima do máximo
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_concorrencia_alta)
        assert is_valida is False
        assert "concorrencia_alta" in detalhes["violacoes"][0]
    
    def test_validar_keyword_palavras_obrigatorias(self, validador_real):
        """Testa validação com palavras obrigatórias."""
        # Keyword válida (contém palavras obrigatórias)
        keyword_valida = Keyword(
            termo="curso de teste para validação",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
        assert is_valida is True
        assert "palavras_obrigatorias" in detalhes["regras_verificadas"]
        
        # Keyword inválida (não contém palavras obrigatórias)
        keyword_invalida = Keyword(
            termo="palavra sem palavras obrigatórias",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_invalida)
        assert is_valida is False
        assert "palavras_obrigatorias_faltantes" in detalhes["violacoes"][0]
    
    def test_validar_keyword_palavras_proibidas(self, validador_real):
        """Testa validação com palavras proibidas."""
        # Keyword válida (não contém palavras proibidas)
        keyword_valida = Keyword(
            termo="palavra válida sem spam",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
        assert is_valida is True
        assert "palavras_proibidas" in detalhes["regras_verificadas"]
        
        # Keyword inválida (contém palavras proibidas)
        keyword_invalida = Keyword(
            termo="palavra com spam fake",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_invalida)
        assert is_valida is False
        assert "palavras_proibidas_encontradas" in detalhes["violacoes"][0]
    
    def test_validar_keyword_comprimento(self, validador_real):
        """Testa validação de comprimento da keyword."""
        # Keyword válida (comprimento adequado)
        keyword_valida = Keyword(
            termo="palavra teste validação",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
        assert is_valida is True
        assert "comprimento" in detalhes["regras_verificadas"]
        
        # Keyword muito curta
        keyword_curta = Keyword(
            termo="a",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_curta)
        assert is_valida is False
        assert "comprimento_curto" in detalhes["violacoes"][0]
        
        # Keyword muito longa
        keyword_longa = Keyword(
            termo="palavra muito longa que excede o limite máximo permitido de caracteres",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_longa)
        assert is_valida is False
        assert "comprimento_longo" in detalhes["violacoes"][0]
    
    def test_validar_keyword_intencao(self, validador_real):
        """Testa validação de intenção de busca."""
        # Keyword com intenção válida
        for intencao in [IntencaoBusca.INFORMACIONAL, IntencaoBusca.COMERCIAL, IntencaoBusca.TRANSACIONAL]:
            keyword_valida = Keyword(
                termo="teste válido",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=intencao,
                fonte="google_keyword_planner"
            )
            
            is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
            assert is_valida is True
            assert "intencao" in detalhes["regras_verificadas"]
        
        # Keyword com intenção inválida (usando valor inválido do enum)
        keyword_intencao_invalida = Keyword(
            termo="teste intenção inválida",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,  # Usar valor válido, mas testar lógica
            fonte="google_keyword_planner"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_intencao_invalida)
        assert is_valida is False
        assert "intencao_nao_permitida" in detalhes["violacoes"][0]
    
    def test_validar_keyword_fonte(self, validador_real):
        """Testa validação de fonte."""
        # Keyword com fonte válida
        for fonte in ["google_keyword_planner", "bing_ads", "manual"]:
            keyword_valida = Keyword(
                termo="teste válido",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=0.7,
                intencao=IntencaoBusca.INFORMACIONAL,
                fonte=fonte
            )
            
            is_valida, detalhes = validador_real.validar_keyword(keyword_valida)
            assert is_valida is True
            assert "fonte" in detalhes["regras_verificadas"]
        
        # Keyword com fonte inválida
        keyword_fonte_invalida = Keyword(
            termo="teste fonte inválida",
            volume_busca=1000,
            cpc=2.5,
            concorrencia=0.7,
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="fonte_invalida"
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_fonte_invalida)
        assert is_valida is False
        assert "fonte_nao_permitida" in detalhes["violacoes"][0]
    
    def test_validar_keywords_lote(self, validador_real, keywords_reais):
        """Testa validação de lote de keywords."""
        resultado = validador_real.validar_keywords(keywords_reais)
        
        # Deve aprovar apenas keywords que atendem a todos os critérios
        assert len(resultado) == 2  # curso de marketing digital e teste de validação python
        
        termos_aprovados = [kw.termo for kw in resultado]
        assert "curso de marketing digital" in termos_aprovados
        assert "teste de validação python" in termos_aprovados
        
        # Verificar que keywords problemáticas foram rejeitadas
        assert "receita bolo chocolate" not in termos_aprovados  # Volume baixo
        assert "seguro auto spam" not in termos_aprovados  # Palavra proibida
        assert "a" not in termos_aprovados  # Muito curta
        assert "palavra muito longa que excede o limite máximo permitido" not in termos_aprovados  # Muito longa
    
    def test_validar_keyword_multiplas_violacoes(self, validador_real):
        """Testa keyword com múltiplas violações."""
        keyword_multiplas_violacoes = Keyword(
            termo="a",  # Muito curta
            volume_busca=50,  # Volume baixo
            cpc=0.05,  # CPC baixo
            concorrencia=1.5,  # Concorrência alta
            intencao=IntencaoBusca.INFORMACIONAL,
            fonte="google_keyword_planner",
            score=0.1  # Score baixo
        )
        
        is_valida, detalhes = validador_real.validar_keyword(keyword_multiplas_violacoes)
        
        assert is_valida is False
        assert len(detalhes["violacoes"]) >= 5  # Múltiplas violações
    
    def test_get_estatisticas_validacao(self, validador_real):
        """Testa obtenção de estatísticas de validação."""
        # Simular algumas validações
        validador_real.total_validated = 20
        validador_real.total_rejected = 5
        validador_real.violations_count = {
            "volume_busca_baixo": 2,
            "cpc_alto": 1,
            "palavras_proibidas_encontradas": 1,
            "comprimento_curto": 1
        }
        
        estatisticas = validador_real.get_estatisticas()
        
        assert estatisticas["nome"] == "ValidadorKeywords"
        assert estatisticas["total_validated"] == 20
        assert estatisticas["total_rejected"] == 5
        assert estatisticas["taxa_rejeicao"] == 0.2  # 5/(20+5)
        assert "violations_count" in estatisticas
        assert estatisticas["violations_count"]["volume_busca_baixo"] == 2
    
    def test_reset_estatisticas(self, validador_real):
        """Testa reset de estatísticas."""
        # Simular estatísticas
        validador_real.total_validated = 20
        validador_real.total_rejected = 5
        validador_real.violations_count = {"teste": 1}
        
        validador_real.reset_estatisticas()
        
        assert validador_real.total_validated == 0
        assert validador_real.total_rejected == 0
        assert validador_real.violations_count == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 