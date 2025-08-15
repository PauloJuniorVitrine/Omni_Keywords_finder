import pytest
from shared.keyword_utils import normalizar_termo, validar_termo
from typing import Dict, List, Optional, Any

class TestNormalizarTermo:
    """
    Testes para normalizar_termo
    - Sucesso: strip, lower, acentos, case
    - Edge: string vazia, apenas espaços, caracteres especiais
    - Exceção: entrada não-string (deve retornar string vazia)
    """
    def test_normalizacao_basica(self):
        assert normalizar_termo(' Teste ') == 'teste'
        assert normalizar_termo('AÇÃO', remover_acentos=True) == 'acao'
        assert normalizar_termo('Ação', remover_acentos=False) == 'ação'
        assert normalizar_termo('ABC', case_sensitive=True) == 'ABC'

    def test_normalizacao_espacos_e_vazio(self):
        assert normalizar_termo('   ') == ''
        assert normalizar_termo('') == ''

    def test_normalizacao_caracteres_especiais(self):
        assert normalizar_termo('palavra!') == 'palavra!'
        assert normalizar_termo('palavra?') == 'palavra?'

    def test_normalizacao_nao_string(self):
        assert normalizar_termo(None) == ''
        assert normalizar_termo(123) == ''

class TestValidarTermo:
    """
    Testes para validar_termo
    - Sucesso: termo válido
    - Edge: termo vazio, nulo, inválido, tamanho limite
    - Exceção: caracteres não permitidos
    """
    def test_validar_termo_sucesso(self):
        assert validar_termo('palavra')
        assert validar_termo('ok', min_caracteres=2)

    def test_validar_termo_vazio(self):
        assert not validar_termo('')
        assert not validar_termo(None)

    def test_validar_termo_tamanho(self):
        assert not validar_termo('a', min_caracteres=2)
        assert not validar_termo('a'*101)

    def test_validar_termo_caracteres(self):
        assert not validar_termo('palavra$', caracteres_permitidos='abcdefghijklmnopqrstuvwxyz')
        assert validar_termo('abc', caracteres_permitidos='abc') 