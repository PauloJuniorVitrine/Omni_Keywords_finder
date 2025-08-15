import pytest
from infrastructure.processamento.normalizador_handler import NormalizadorHandler
from domain.models import Keyword, IntencaoBusca
from typing import Dict, List, Optional, Any

class TestNormalizadorHandler:
    """
    Testes para NormalizadorHandler.handle
    - Sucesso: normalização básica, remoção de duplicatas
    - Edge: termos vazios, apenas espaços, acentos, case
    - Exceção: lista vazia, keyword sem termo
    """
    def make_kw(self, termo):
        return Keyword(termo=termo, volume_busca=10, cpc=1.0, concorrencia=0.5, intencao=IntencaoBusca.INFORMACIONAL)

    def test_normalizacao_sucesso(self):
        handler = NormalizadorHandler(remover_acentos=False)
        kws = [self.make_kw(' Teste '), self.make_kw('teste'), self.make_kw('TESTE')]
        out = handler.handle(kws, {})
        assert len(out) == 1
        assert out[0].termo == 'teste'

    def test_normalizacao_case_sensitive(self):
        handler = NormalizadorHandler(case_sensitive=True)
        kws = [self.make_kw('A'), self.make_kw('a')]
        out = handler.handle(kws, {})
        assert len(out) == 2

    def test_normalizacao_remove_acentos(self):
        handler = NormalizadorHandler(remover_acentos=True)
        kws = [self.make_kw('ação'), self.make_kw('acao')]
        out = handler.handle(kws, {})
        assert len(out) == 1
        assert out[0].termo == 'acao'

    def test_normalizacao_termo_vazio(self):
        handler = NormalizadorHandler()
        kws = [self.make_kw(''), self.make_kw('ok')]
        out = handler.handle(kws, {})
        assert len(out) == 1
        assert out[0].termo == 'ok'

    def test_normalizacao_lista_vazia(self):
        handler = NormalizadorHandler()
        out = handler.handle([], {})
        assert out == [] 