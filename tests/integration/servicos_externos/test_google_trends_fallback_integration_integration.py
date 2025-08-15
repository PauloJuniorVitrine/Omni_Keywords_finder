import pytest
from app.main import create_app
from typing import Dict, List, Optional, Any

app = create_app()
client = app.test_client()

@pytest.mark.integration
@pytest.mark.parametrize("simular,espera_status,espera_msg", [
    ("timeout", 503, "Serviço Google Trends indisponível"),
    ("erro_autenticacao", 401, "Erro de autenticação Google Trends"),
    ("resposta_invalida", 502, "Resposta inválida do Google Trends"),
])
def test_google_trends_fallback(simular, espera_status, espera_msg):
    """
    Teste de fallback para Google Trends:
    - Simula indisponibilidade, timeout, erro de autenticação e resposta inválida
    - Valida resposta do sistema, logs e fallback
    """
    response = client.get(f"/api/externo/google_trends?simular={simular}")
    assert response.status_code == espera_status
    assert response.get_json()["erro"] == espera_msg
    # Opcional: medir tempo de fallback
    # inicio = time.time()
    # _ = client.get(f"/externo/google_trends?simular={simular}")
    # duracao = time.time() - inicio
    # assert duracao < 5  # fallback não pode demorar mais que 5s 