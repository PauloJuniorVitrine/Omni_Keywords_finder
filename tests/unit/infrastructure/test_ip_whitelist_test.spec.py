import pytest
from infrastructure.security import ip_whitelist
from typing import Dict, List, Optional, Any

def test_ip_allowed_sucesso():
    assert ip_whitelist.is_ip_allowed("192.168.0.1", "192.168.0.1,10.0.0.1")
    assert ip_whitelist.is_ip_allowed("10.0.0.1", "192.168.0.1,10.0.0.1")

def test_ip_allowed_falha():
    assert not ip_whitelist.is_ip_allowed("127.0.0.1", "192.168.0.1,10.0.0.1")
    assert not ip_whitelist.is_ip_allowed("", "192.168.0.1,10.0.0.1")
    assert not ip_whitelist.is_ip_allowed("192.168.0.1", "")
    assert not ip_whitelist.is_ip_allowed("192.168.0.1", None) 