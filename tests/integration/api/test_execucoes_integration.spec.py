from typing import Dict, List, Optional, Any
"""
Fluxo: /api/execucoes/ (POST, GET, detalhes)
Camadas: API, Service, DB, Log
RISK_SCORE: 65
Similaridade semântica: ≥ 0.90
Origem: AI (ruleset + mapeamento)
Serviços acessados: Banco, logs, notificações
EXEC_ID: EXEC2
Timestamp: {timestamp_utc}
"""

import pytest
from flask import Flask
from backend.app.api.execucoes import execucoes_bp
from backend.app.models import db, Categoria, Execucao
from backend.app.models.user import User
from backend.app.models.notificacao import Notificacao
from backend.app.models import db as _db
from datetime import datetime
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

@pytest.fixture
def client(app):
    return app.test_client()

def test_execucoes_post_sucesso(client):
    payload = {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1"}
    resp = client.post('/api/execucoes/', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "execucao_id" in data
    assert data["categoria_id"] == 1
    assert data["palavras_chave"] == ["python"]
    assert data["cluster"] == "cluster1"
    assert "prompt_preenchido" in data

def test_execucoes_post_parametros_invalidos(client):
    # categoria_id ausente
    resp = client.post('/api/execucoes/', json={"palavras_chave": ["python"]})
    assert resp.status_code == 400
    # palavras_chave ausente
    resp = client.post('/api/execucoes/', json={"categoria_id": 1})
    assert resp.status_code == 400
    # categoria_id inválido
    resp = client.post('/api/execucoes/', json={"categoria_id": -1, "palavras_chave": ["python"]})
    assert resp.status_code == 400
    # palavras_chave inválidas
    resp = client.post('/api/execucoes/', json={"categoria_id": 1, "palavras_chave": []})
    assert resp.status_code == 400
    resp = client.post('/api/execucoes/', json={"categoria_id": 1, "palavras_chave": [""]})
    assert resp.status_code == 400

def test_execucoes_post_categoria_inexistente(client):
    resp = client.post('/api/execucoes/', json={"categoria_id": 999, "palavras_chave": ["python"]})
    assert resp.status_code == 404

def test_execucoes_post_prompt_ausente(client):
    # Remove arquivo de prompt
    import os
    os.remove('prompt_test.txt')
    resp = client.post('/api/execucoes/', json={"categoria_id": 1, "palavras_chave": ["python"]})
    assert resp.status_code == 404
    # Recria para outros testes
    with open('prompt_test.txt', 'w', encoding='utf-8') as f:
        f.write('PROMPT [PALAVRA-CHAVE] [CLUSTER]')

def test_execucoes_get_listar(client):
    # Cria execução
    client.post('/api/execucoes/', json={"categoria_id": 1, "palavras_chave": ["python"]})
    resp = client.get('/api/execucoes/?categoria_id=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id_categoria"] == 1

def test_execucoes_get_detalhe(client):
    # Cria execução
    post = client.post('/api/execucoes/', json={"categoria_id": 1, "palavras_chave": ["python"]})
    exec_id = post.get_json()["execucao_id"]
    resp = client.get(f'/api/execucoes/{exec_id}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == exec_id
    assert data["id_categoria"] == 1
    assert data["palavras_chave"] == ["python"]
    assert data["status"] == "executado"
    assert "data_execucao" in data 