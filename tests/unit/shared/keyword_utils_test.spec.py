import pytest
from shared.keyword_utils import normalizar_termo, validar_termo
from typing import Dict, List, Optional, Any

@pytest.mark.parametrize("termo,remover_acentos,case_sensitive,esperado", [
    (" Teste ", False, False, "teste"),
    ("AÇÃO", True, False, "acao"),
    ("Ação", False, False, "ação"),
    ("ABC", False, True, "ABC"),
    ("   ", False, False, ""),
    ("palavra!", False, False, "palavra!"),
    (None, False, False, ""),
    (123, False, False, ""),
])
def test_normalizar_termo_parametrizado(termo, remover_acentos, case_sensitive, esperado):
    assert normalizar_termo(termo, remover_acentos, case_sensitive) == esperado

@pytest.mark.parametrize("termo,min_carac,max_carac,permitidos,esperado", [
    ("palavra", 2, 100, None, True),
    ("", 2, 100, None, False),
    (None, 2, 100, None, False),
    ("a", 2, 100, None, False),
    ("a"*101, 2, 100, None, False),
    ("abc", 2, 100, "abc", True),
    ("abc$", 2, 100, "abc", False),
])
def test_validar_termo_parametrizado(termo, min_carac, max_carac, permitidos, esperado):
    assert validar_termo(termo, min_carac, max_carac, permitidos) == esperado 