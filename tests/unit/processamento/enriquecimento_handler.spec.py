import pytest
from infrastructure.processamento.enriquecimento_handler import EnriquecimentoHandler
from domain.models import Keyword, IntencaoBusca
from unittest.mock import MagicMock
from typing import Dict, List, Optional, Any

class TestEnriquecimentoHandler:
    """
    Testes para EnriquecimentoHandler.handle
    - Sucesso: score e justificativa calculados
    - Edge: lista vazia, pesos ausentes, campos limite
    - Exceção: erro no cálculo de score
    """
    def make_kw(self, termo, volume=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL):
        return Keyword(termo=termo, volume_busca=volume, cpc=cpc, concorrencia=concorrencia, intencao=intencao)

    def test_enriquecimento_sucesso(self):
        handler = EnriquecimentoHandler()
        kws = [self.make_kw('valid')]
        out = handler.handle(kws, {"pesos": {"volume": 0.5, "cpc": 0.2, "intencao": 0.2, "concorrencia": 0.1}})
        assert len(out) == 1
        assert out[0].score > 0
        assert 'Score calculado' in out[0].justificativa

    def test_enriquecimento_pesos_ausentes(self):
        handler = EnriquecimentoHandler()
        kws = [self.make_kw('valid')]
        out = handler.handle(kws, {})
        assert len(out) == 1
        assert out[0].score > 0

    def test_enriquecimento_lista_vazia(self):
        handler = EnriquecimentoHandler()
        out = handler.handle([], {"pesos": {"volume": 0.5}})
        assert out == []

    def test_enriquecimento_erro_score(self, caplog):
        handler = EnriquecimentoHandler()
        kw = self.make_kw('valid')
        # Força erro no cálculo de score
        kw.calcular_score = MagicMock(side_effect=Exception('erro simulado'))
        with caplog.at_level('ERROR'):
            out = handler.handle([kw], {"pesos": {}})
        assert out == []
        assert any('erro_enriquecimento' in r.message for r in caplog.records)

    def test_enriquecimento_limites_campos(self):
        handler = EnriquecimentoHandler()
        k1 = self.make_kw('a', concorrencia=0)
        k2 = self.make_kw('b', concorrencia=1)
        k3 = self.make_kw('c', cpc=0, volume=0)
        out = handler.handle([k1, k2, k3], {"pesos": {}})
        assert len(out) == 3 