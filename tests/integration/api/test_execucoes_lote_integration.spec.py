from typing import Dict, List, Optional, Any
"""
Fluxo: /api/execucoes/lote (POST), /api/execucoes/lote/status (GET)
Camadas: API, Service, DB, Log, FS
RISK_SCORE: 70
Similaridade semântica: ≥ 0.90
Origem: AI (ruleset + mapeamento)
Serviços acessados: Banco, logs, notificações, arquivo
EXEC_ID: EXEC2
Timestamp: {timestamp_utc}
"""

import pytest
from flask import Flask
from backend.app.api.execucoes import execucoes_bp
from backend.app.models import db, Categoria, Execucao
from backend.app.models import db as _db
import os
import json

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _db.init_app(app)
    with app.app_context():
        _db.create_all()
        app.register_blueprint(execucoes_bp)
        # Categoria de teste
        cat = Categoria(id=1, nome='Teste', perfil_cliente='B2B', cluster='cluster1', prompt_path='prompt_test.txt', id_nicho=1)
        _db.session.add(cat)
        _db.session.commit()
        # Criar arquivo de prompt
        with open('prompt_test.txt', 'w', encoding='utf-8') as f:
            f.write('PROMPT [PALAVRA-CHAVE] [CLUSTER]')
        yield app
        _db.drop_all()
        if os.path.exists('prompt_test.txt'):
            os.remove('prompt_test.txt')

@pytest.fixture
def client(app):
    return app.test_client()

def test_execucoes_lote_post_sucesso(client):
    dados = [
        {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1"},
        {"categoria_id": 1, "palavras_chave": ["pytest"], "cluster": "cluster1"}
    ]
    resp = client.post('/api/execucoes/lote', json=dados)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "id_lote" in data
    assert "resultados" in data
    assert data["qtd_executada"] == 2
    assert all("execucao_id" in r or "erro" in r for r in data["resultados"])
    # Verifica side effect: arquivo de log
    log_path = data["log_path"]
    assert os.path.exists(log_path)
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert 'Execução Paralela de Lotes' in content

def test_execucoes_lote_post_parametros_invalidos(client):
    # Payload não lista
    resp = client.post('/api/execucoes/lote', json={"categoria_id": 1})
    assert resp.status_code == 400
    # Lista vazia
    resp = client.post('/api/execucoes/lote', json=[])
    assert resp.status_code == 400

def test_execucoes_lote_post_idempotente(client):
    dados = [{"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1"}]
    # Primeira execução
    resp1 = client.post('/api/execucoes/lote', json=dados)
    assert resp1.status_code == 200
    exec_id = resp1.get_json()["resultados"][0].get("execucao_id")
    # Segunda execução idêntica (deve ser idempotente)
    resp2 = client.post('/api/execucoes/lote', json=dados)
    assert resp2.status_code == 200
    result2 = resp2.get_json()["resultados"][0]
    assert result2.get("status") == "já executado"
    assert result2.get("execucao_id") == exec_id

def test_execucoes_lote_post_categoria_inexistente(client):
    dados = [{"categoria_id": 999, "palavras_chave": ["python"]}]
    resp = client.post('/api/execucoes/lote', json=dados)
    assert resp.status_code == 200
    result = resp.get_json()["resultados"][0]
    assert "erro" in result and "Categoria não encontrada" in result["erro"]

def test_execucoes_lote_post_prompt_ausente(client):
    # Remove arquivo de prompt
    os.remove('prompt_test.txt')
    dados = [{"categoria_id": 1, "palavras_chave": ["python"]}]
    resp = client.post('/api/execucoes/lote', json=dados)
    assert resp.status_code == 200
    result = resp.get_json()["resultados"][0]
    assert "erro" in result and "Arquivo de prompt não encontrado" in result["erro"]
    # Recria para outros testes
    with open('prompt_test.txt', 'w', encoding='utf-8') as f:
        f.write('PROMPT [PALAVRA-CHAVE] [CLUSTER]')

def test_execucoes_lote_status_get(client):
    # Executa lote
    dados = [
        {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1"},
        {"categoria_id": 1, "palavras_chave": ["pytest"], "cluster": "cluster1"}
    ]
    resp = client.post('/api/execucoes/lote', json=dados)
    assert resp.status_code == 200
    log_path = resp.get_json()["log_path"]
    id_lote = resp.get_json()["id_lote"]
    # Consulta status
    resp2 = client.get(f'/api/execucoes/lote/status?id_lote={id_lote}')
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert data["id_lote"] == id_lote
    assert data["total"] == 2
    assert "concluidos" in data and "erros" in data and "progresso" in data
    assert isinstance(data["itens"], list)
    # Edge case: log inexistente
    resp3 = client.get('/api/execucoes/lote/status?id_lote=inexistente')
    assert resp3.status_code == 404
    assert "erro" in resp3.get_json() 