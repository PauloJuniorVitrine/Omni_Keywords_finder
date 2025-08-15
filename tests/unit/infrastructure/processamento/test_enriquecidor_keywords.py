from typing import Dict, List, Optional, Any
"""
Testes unitários para o módulo EnriquecidorKeywords.
Testa cálculo de scores, geração de justificativas e processamento paralelo.
"""
import pytest
from datetime import datetime
from domain.models import Keyword, IntencaoBusca
from infrastructure.processamento.enriquecidor_keywords import EnriquecidorKeywords


class TestEnriquecidorKeywords:
    """Testes para a classe EnriquecidorKeywords."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.enriquecidor = EnriquecidorKeywords()
        self.enriquecidor_custom = EnriquecidorKeywords(
            pesos_score={
                "volume": 0.5,
                "cpc": 0.3,
                "intention": 0.1,
                "competition": 0.1
            },
            paralelizar=True,
            max_workers=2
        )
        
    def test_inicializacao_padrao(self):
        """Testa inicialização com configurações padrão."""
        enriquecidor = EnriquecidorKeywords()
        
        assert enriquecidor.pesos == {
            "volume": 0.4,
            "cpc": 0.2,
            "intention": 0.2,
            "competition": 0.2
        }
        assert enriquecidor.paralelizar is False
        assert enriquecidor.max_workers == 4
        assert enriquecidor._ultimos_erros == []
        
    def test_inicializacao_customizada(self):
        """Testa inicialização com configurações customizadas."""
        pesos = {
            "volume": 0.6,
            "cpc": 0.2,
            "intention": 0.1,
            "competition": 0.1
        }
        
        enriquecidor = EnriquecidorKeywords(
            pesos_score=pesos,
            paralelizar=True,
            max_workers=8
        )
        
        assert enriquecidor.pesos == pesos
        assert enriquecidor.paralelizar is True
        assert enriquecidor.max_workers == 8
        
    def test_normalizar_intencao(self):
        """Testa normalização de intenção de busca."""
        # Teste todas as intenções
        assert self.enriquecidor._normalizar_intencao(IntencaoBusca.INFORMACIONAL) == 0.3
        assert self.enriquecidor._normalizar_intencao(IntencaoBusca.NAVEGACIONAL) == 0.2
        assert self.enriquecidor._normalizar_intencao(IntencaoBusca.COMPARACAO) == 0.4
        assert self.enriquecidor._normalizar_intencao(IntencaoBusca.COMERCIAL) == 0.7
        assert self.enriquecidor._normalizar_intencao(IntencaoBusca.TRANSACIONAL) == 1.0
        
    def test_calcular_score_keyword_valida(self):
        """Testa cálculo de score para keyword válida."""
        keyword = Keyword(
            termo="palavra chave",
            volume_busca=5000,
            cpc=2.5,
            concorrencia=0.3,
            intencao=IntencaoBusca.TRANSACIONAL
        )
        
        score = self.enriquecidor.calcular_score(keyword)
        
        # Verificar que o score está entre 0 e 1
        assert 0.0 <= score <= 1.0
        
        # Verificar cálculo esperado
        volume_norm = min(5000 / 10000, 1.0)  # 0.5
        cpc_norm = min(2.5 / 10, 1.0)  # 0.25
        intencao_norm = 1.0  # TRANSACIONAL
        competicao_norm = 1 - 0.3  # 0.7
        
        score_esperado = (
            volume_norm * 0.4 +
            cpc_norm * 0.2 +
            intencao_norm * 0.2 +
            competicao_norm * 0.2
        )
        
        assert abs(score - score_esperado) < 0.01
        
    def test_calcular_score_valores_limite(self):
        """Testa cálculo de score com valores limite."""
        # Volume zero
        keyword_volume_zero = Keyword(
            termo="teste",
            volume_busca=0,
            cpc=1.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        score = self.enriquecidor.calcular_score(keyword_volume_zero)
        assert score == 0.0
        
        # CPC zero
        keyword_cpc_zero = Keyword(
            termo="teste",
            volume_busca=1000,
            cpc=0.0,
            concorrencia=0.5,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        score = self.enriquecidor.calcular_score(keyword_cpc_zero)
        assert score > 0.0  # Ainda tem outros fatores
        
        # Concorrência máxima
        keyword_concorrencia_max = Keyword(
            termo="teste",
            volume_busca=1000,
            cpc=1.0,
            concorrencia=1.0,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        score = self.enriquecidor.calcular_score(keyword_concorrencia_max)
        assert score < 0.5  # Score menor devido à alta concorrência
        
    def test_calcular_score_valores_extremos(self):
        """Testa cálculo de score com valores extremos."""
        # Valores muito altos
        keyword_extrema = Keyword(
            termo="teste",
            volume_busca=50000,  # Muito alto
            cpc=15.0,  # Muito alto
            concorrencia=0.1,  # Muito baixo
            intencao=IntencaoBusca.TRANSACIONAL
        )
        
        score = self.enriquecidor.calcular_score(keyword_extrema)
        assert 0.0 <= score <= 1.0  # Deve estar normalizado
        
        # Valores negativos (devem ser tratados)
        keyword_negativa = Keyword(
            termo="teste",
            volume_busca=-100,
            cpc=-1.0,
            concorrencia=-0.1,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        score = self.enriquecidor.calcular_score(keyword_negativa)
        assert score == 0.0
        
    def test_gerar_justificativa(self):
        """Testa geração de justificativa."""
        keyword = Keyword(
            termo="palavra chave",
            volume_busca=1500,
            cpc=3.5,
            concorrencia=0.2,
            intencao=IntencaoBusca.TRANSACIONAL
        )
        
        score = 0.75
        justificativa = self.enriquecidor.gerar_justificativa(keyword, score)
        
        assert "Score 0.750" in justificativa
        assert "volume alto (1500)" in justificativa
        assert "CPC alto (3.50)" in justificativa
        assert "baixa concorrência" in justificativa
        
    def test_gerar_justificativa_valores_medios(self):
        """Testa geração de justificativa com valores médios."""
        keyword = Keyword(
            termo="palavra chave",
            volume_busca=500,
            cpc=1.2,
            concorrencia=0.6,
            intencao=IntencaoBusca.INFORMACIONAL
        )
        
        score = 0.45
        justificativa = self.enriquecidor.gerar_justificativa(keyword, score)
        
        assert "volume médio (500)" in justificativa
        assert "CPC médio (1.20)" in justificativa
        assert "concorrência média" in justificativa
        
    def test_gerar_justificativa_valores_baixos(self):
        """Testa geração de justificativa com valores baixos."""
        keyword = Keyword(
            termo="palavra chave",
            volume_busca=50,
            cpc=0.3,
            concorrencia=0.9,
            intencao=IntencaoBusca.NAVEGACIONAL
        )
        
        score = 0.15
        justificativa = self.enriquecidor.gerar_justificativa(keyword, score)
        
        assert "volume baixo (50)" in justificativa
        assert "CPC baixo (0.30)" in justificativa
        assert "alta concorrência" in justificativa
        
    def test_enriquecer_keyword(self):
        """Testa enriquecimento de keyword individual."""
        keyword = Keyword(
            termo="palavra chave",
            volume_busca=1000,
            cpc=2.0,
            concorrencia=0.4,
            intencao=IntencaoBusca.COMERCIAL,
            fonte="teste",
            data_coleta=datetime.utcnow()
        )
        
        keyword_enriquecida = self.enriquecidor.enriquecer_keyword(keyword)
        
        assert keyword_enriquecida is not None
        assert keyword_enriquecida.termo == keyword.termo
        assert keyword_enriquecida.volume_busca == keyword.volume_busca
        assert keyword_enriquecida.cpc == keyword.cpc
        assert keyword_enriquecida.concorrencia == keyword.concorrencia
        assert keyword_enriquecida.intencao == keyword.intencao
        assert keyword_enriquecida.fonte == keyword.fonte
        assert keyword_enriquecida.data_coleta == keyword.data_coleta
        
        # Verificar que score e justificativa foram adicionados
        assert hasattr(keyword_enriquecida, 'score')
        assert hasattr(keyword_enriquecida, 'justificativa')
        assert 0.0 <= keyword_enriquecida.score <= 1.0
        assert len(keyword_enriquecida.justificativa) > 0
        
    def test_enriquecer_keyword_erro(self):
        """Testa enriquecimento com erro."""
        # Keyword com dados inválidos que causam erro
        keyword_invalida = Keyword(
            termo="",  # Termo vazio pode causar erro
            volume_busca=1000,
            cpc=2.0,
            concorrencia=0.4,
            intencao=IntencaoBusca.COMERCIAL
        )
        
        # Mock para simular erro
        original_calcular_score = self.enriquecidor.calcular_score
        self.enriquecidor.calcular_score = lambda kw: 1/0  # Força erro
        
        keyword_enriquecida = self.enriquecidor.enriquecer_keyword(keyword_invalida)
        
        assert keyword_enriquecida is None
        assert len(self.enriquecidor._ultimos_erros) == 1
        
        # Restaurar método original
        self.enriquecidor.calcular_score = original_calcular_score
        
    def test_enriquecer_lista_sequencial(self):
        """Testa enriquecimento sequencial de lista."""
        keywords = [
            Keyword(termo="palavra 1", volume_busca=1000, cpc=2.0, concorrencia=0.4, intencao=IntencaoBusca.INFORMACIONAL),
            Keyword(termo="palavra 2", volume_busca=2000, cpc=3.0, concorrencia=0.3, intencao=IntencaoBusca.COMERCIAL),
            Keyword(termo="palavra 3", volume_busca=3000, cpc=4.0, concorrencia=0.2, intencao=IntencaoBusca.TRANSACIONAL)
        ]
        
        keywords_enriquecidas = self.enriquecidor.enriquecer_lista(keywords)
        
        assert len(keywords_enriquecidas) == 3
        for kw in keywords_enriquecidas:
            assert hasattr(kw, 'score')
            assert hasattr(kw, 'justificativa')
            assert 0.0 <= kw.score <= 1.0
            assert len(kw.justificativa) > 0
            
    def test_enriquecer_lista_paralelo(self):
        """Testa enriquecimento paralelo de lista."""
        keywords = [
            Keyword(termo=f"palavra {index}", volume_busca=1000+index*100, cpc=1.0+index*0.5, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)
            for index in range(15)  # Mais de 10 para ativar paralelização
        ]
        
        keywords_enriquecidas = self.enriquecidor_custom.enriquecer_lista(keywords)
        
        assert len(keywords_enriquecidas) == 15
        for kw in keywords_enriquecidas:
            assert hasattr(kw, 'score')
            assert hasattr(kw, 'justificativa')
            
    def test_enriquecer_lista_vazia(self):
        """Testa enriquecimento de lista vazia."""
        keywords_enriquecidas = self.enriquecidor.enriquecer_lista([])
        assert keywords_enriquecidas == []
        
    def test_enriquecer_lista_com_erros(self):
        """Testa enriquecimento de lista com alguns erros."""
        keywords = [
            Keyword(termo="palavra válida", volume_busca=1000, cpc=2.0, concorrencia=0.4, intencao=IntencaoBusca.INFORMACIONAL),
            Keyword(termo="", volume_busca=2000, cpc=3.0, concorrencia=0.3, intencao=IntencaoBusca.COMERCIAL),  # Inválida
            Keyword(termo="outra válida", volume_busca=3000, cpc=4.0, concorrencia=0.2, intencao=IntencaoBusca.TRANSACIONAL)
        ]
        
        # Mock para simular erro na segunda keyword
        original_enriquecer_keyword = self.enriquecidor.enriquecer_keyword
        call_count = 0
        
        def mock_enriquecer_keyword(kw):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Segunda keyword
                return None
            return original_enriquecer_keyword(kw)
        
        self.enriquecidor.enriquecer_keyword = mock_enriquecer_keyword
        
        keywords_enriquecidas = self.enriquecidor.enriquecer_lista(keywords)
        
        assert len(keywords_enriquecidas) == 2  # Apenas as válidas
        assert len(self.enriquecidor._ultimos_erros) == 1
        
        # Restaurar método original
        self.enriquecidor.enriquecer_keyword = original_enriquecer_keyword
        
    def test_obter_erros(self):
        """Testa obtenção de erros."""
        # Simular alguns erros
        self.enriquecidor._ultimos_erros = [
            {"termo": "erro1", "erro": "teste1"},
            {"termo": "erro2", "erro": "teste2"}
        ]
        
        erros = self.enriquecidor.obter_erros()
        
        assert len(erros) == 2
        assert erros[0]["termo"] == "erro1"
        assert erros[1]["termo"] == "erro2"
        
        # Verificar que é uma cópia
        erros.append({"termo": "erro3", "erro": "teste3"})
        assert len(self.enriquecidor._ultimos_erros) == 2  # Original não alterado
        
    def test_obter_configuracao(self):
        """Testa obtenção da configuração atual."""
        config = self.enriquecidor.obter_configuracao()
        
        assert config["pesos_score"] == {
            "volume": 0.4,
            "cpc": 0.2,
            "intention": 0.2,
            "competition": 0.2
        }
        assert config["paralelizar"] is False
        assert config["max_workers"] == 4
        
        # Verificar que é uma cópia
        config["pesos_score"]["volume"] = 0.9
        assert self.enriquecidor.pesos["volume"] == 0.4  # Original não alterado
        
    def test_atualizar_pesos_validos(self):
        """Testa atualização de pesos válidos."""
        novos_pesos = {
            "volume": 0.5,
            "cpc": 0.2,
            "intention": 0.2,
            "competition": 0.1
        }
        
        sucesso = self.enriquecidor.atualizar_pesos(novos_pesos)
        
        assert sucesso is True
        assert self.enriquecidor.pesos == novos_pesos
        
    def test_atualizar_pesos_invalidos(self):
        """Testa atualização de pesos inválidos."""
        novos_pesos = {
            "volume": 0.5,
            "cpc": 0.2,
            "intention": 0.2,
            "competition": 0.5  # Soma > 1.0
        }
        
        sucesso = self.enriquecidor.atualizar_pesos(novos_pesos)
        
        # Deve aceitar mas com warning
        assert sucesso is True
        assert self.enriquecidor.pesos == novos_pesos
        
    def test_atualizar_pesos_erro(self):
        """Testa atualização de pesos com erro."""
        # Mock para simular erro
        original_logger_error = self.enriquecidor.__class__.__module__ + ".logger.error"
        
        novos_pesos = {"invalid": "data"}
        
        sucesso = self.enriquecidor.atualizar_pesos(novos_pesos)
        
        assert sucesso is False
        
    def test_pesos_diferentes_afetam_score(self):
        """Testa que pesos diferentes resultam em scores diferentes."""
        keyword = Keyword(
            termo="palavra chave",
            volume_busca=5000,
            cpc=2.0,
            concorrencia=0.3,
            intencao=IntencaoBusca.TRANSACIONAL
        )
        
        # Score com pesos padrão
        score_padrao = self.enriquecidor.calcular_score(keyword)
        
        # Score com pesos customizados (mais peso no volume)
        enriquecidor_volume = EnriquecidorKeywords(pesos_score={
            "volume": 0.8,
            "cpc": 0.1,
            "intention": 0.05,
            "competition": 0.05
        })
        
        score_volume = enriquecidor_volume.calcular_score(keyword)
        
        # Os scores devem ser diferentes
        assert abs(score_padrao - score_volume) > 0.01 