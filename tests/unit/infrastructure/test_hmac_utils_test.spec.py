import pytest
from infrastructure.security import hmac_utils
from typing import Dict, List, Optional, Any

@pytest.mark.parametrize("secret,payload,expected", [
    ("chave123", b"mensagem", hmac_utils.generate_hmac_signature("chave123", b"mensagem")),
    ("outra-chave", b"", hmac_utils.generate_hmac_signature("outra-chave", b"")),
])
def test_generate_hmac_signature(secret, payload, expected):
    assert hmac_utils.generate_hmac_signature(secret, payload) == expected

def test_validate_hmac_signature_sucesso():
    secret = "segredo"
    payload = b"dados"
    signature = hmac_utils.generate_hmac_signature(secret, payload)
    assert hmac_utils.validate_hmac_signature(secret, payload, signature)

def test_validate_hmac_signature_falha():
    secret = "segredo"
    payload = b"dados"
    signature = hmac_utils.generate_hmac_signature(secret, payload)
    assert not hmac_utils.validate_hmac_signature(secret, payload, signature + "value")
    assert not hmac_utils.validate_hmac_signature(secret, b"outros", signature)
    assert not hmac_utils.validate_hmac_signature("errado", payload, signature) 