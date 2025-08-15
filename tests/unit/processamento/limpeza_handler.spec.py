import pytest
from infrastructure.processamento.limpeza_handler import LimpezaHandler
from domain.models import Keyword, IntencaoBusca
from unittest.mock import MagicMock
from typing import Dict, List, Optional, Any

class TestLimpezaHandler:
    """
    Testes para LimpezaHandler.handle
    - Sucesso: keywords válidas, múltiplas regras
    - Edge: termos vazios, duplicados, campos limite
    - Exceção: keyword inválida, lista vazia, erro no validador
    """
    def make_kw(self, termo, volume=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL):
        return Keyword(termo=termo, volume_busca=volume, cpc=cpc, concorrencia=concorrencia, intencao=intencao)

    def test_limpeza_sucesso(self):
        handler = LimpezaHandler()
        kws = [self.make_kw('valid'), self.make_kw('outro')]
        out = handler.handle(kws, {})
        assert len(out) == 2
        assert all(isinstance(key, Keyword) for key in out)

    def test_limpeza_remove_invalida(self):
        handler = LimpezaHandler()
        # volume_busca negativo é inválido
        kws = [self.make_kw('ok'), self.make_kw('bad', volume=-1)]
        out = handler.handle(kws, {})
        assert len(out) == 1
        assert out[0].termo == 'ok'

    def test_limpeza_termo_vazio(self):
        handler = LimpezaHandler()
        # termo vazio não pode ser criado (raise ValueError)
        with pytest.raises(ValueError):
            self.make_kw('')

    def test_limpeza_lista_vazia(self):
        handler = LimpezaHandler()
        out = handler.handle([], {})
        assert out == []

    def test_limpeza_validador_customizado(self):
        handler = LimpezaHandler()
        validador = MagicMock()
        validador.validar_keyword.side_effect = lambda kw: (kw.termo == 'ok', None)
        kws = [self.make_kw('ok'), self.make_kw('fail')]
        out = handler.handle(kws, {"validador": validador})
        assert len(out) == 1
        assert out[0].termo == 'ok'
        validador.validar_keyword.assert_called()

    def test_limpeza_erro_validador(self, caplog):
        handler = LimpezaHandler()
        validador = MagicMock()
        validador.validar_keyword.side_effect = Exception('erro simulado')
        kws = [self.make_kw('ok')]
        with caplog.at_level('ERROR'):
            out = handler.handle(kws, {"validador": validador})
        assert out == []
        assert any('erro_limpeza_keyword' in r.message for r in caplog.records)

    def test_limpeza_limites_campos(self):
        handler = LimpezaHandler()
        # concorrencia no limite
        k1 = self.make_kw('a', concorrencia=0)
        k2 = self.make_kw('b', concorrencia=1)
        # cpc e volume_busca no limite
        k3 = self.make_kw('c', cpc=0, volume=0)
        out = handler.handle([k1, k2, k3], {})
        assert len(out) == 3 