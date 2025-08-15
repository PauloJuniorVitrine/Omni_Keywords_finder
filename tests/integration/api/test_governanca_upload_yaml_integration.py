import io
import pytest
import requests
from typing import Dict, List, Optional, Any

def test_upload_yaml_real(api_url):
    url = f"{api_url}/api/governanca/regras/upload"
    yaml_content = """
    score_minimo: 0.7
    blacklist:
      - kw_banida
    whitelist:
      - kw_livre
    """
    files = {"file": ("regras.yaml", io.BytesIO(yaml_content.encode()), "application/value-yaml")}
    response = requests.post(url, files=files)
    assert response.status_code in (200, 201)
    assert "yaml" in response.text.lower() or response.json().get("status") == "ok" 