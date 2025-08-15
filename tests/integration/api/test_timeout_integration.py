import pytest
import requests
from typing import Dict, List, Optional, Any

def test_timeout_real(api_url):
    url = f"{api_url}/api/test/timeout"
    with pytest.raises(requests.exceptions.ReadTimeout):
        requests.get(url, timeout=5) 