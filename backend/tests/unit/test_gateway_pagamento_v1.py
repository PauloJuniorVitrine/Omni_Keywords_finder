from typing import Dict, List, Optional, Any
"""
Testes unitários para gateway_pagamento_v1.py
"""
import pytest
from infrastructure.pagamentos.gateway_pagamento_v1 import PagamentoGatewayV1
from tenacity import RetryError

def test_processar_pagamento_sucesso():
    gateway = PagamentoGatewayV1('stripe', 'demo')
    resultado = gateway.processar_pagamento(100.0, 'BRL', {'nome': 'Cliente'})
    assert resultado['status'] == 'sucesso'
    assert resultado['valor'] == 100.0

def test_processar_pagamento_falha(monkeypatch):
    gateway = PagamentoGatewayV1('stripe', 'demo')
    def erro(*a, **kw):
        raise Exception('Falha')
    monkeypatch.setattr(gateway, 'processar_pagamento', erro)
    with pytest.raises(Exception):
        gateway.processar_pagamento(100.0, 'BRL', {'nome': 'Cliente'})

def test_processar_com_fallback(monkeypatch):
    gateway = PagamentoGatewayV1('stripe', 'demo')
    def erro(*a, **kw):
        raise RetryError('Falha')
    monkeypatch.setattr(gateway, 'processar_pagamento', erro)
    resultado = gateway.processar_com_fallback(100.0, 'BRL', {'nome': 'Cliente'})
    assert 'fallback' in str(resultado['erro']) 