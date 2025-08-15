import hmac, hashlib
from typing import Dict, List, Optional, Any

def generate_hmac_signature(secret: str, payload: bytes) -> str:
    """Gera assinatura HMAC SHA256."""
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

def validate_hmac_signature(secret: str, payload: bytes, signature: str) -> bool:
    """Valida assinatura HMAC SHA256."""
    expected = generate_hmac_signature(secret, payload)
    return hmac.compare_digest(signature, expected) 