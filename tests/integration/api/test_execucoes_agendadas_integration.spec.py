from typing import Dict, List, Optional, Any
"""
Fluxo: /api/execucoes_agendadas/agendar (POST), /api/execucoes_agendadas/agendadas (GET), job agendado
Camadas: API, Service, DB, Log
RISK_SCORE: 60
Similaridade semântica: ≥ 0.90
Origem: AI (ruleset + mapeamento)
Serviços acessados: Banco, logs, notificações
EXEC_ID: EXEC2
Timestamp: {timestamp_utc}
"""

import pytest
from flask import Flask
from backend.app.api.execucoes_agendadas import execucoes_agendadas_bp
from backend.app.models import db, Categoria, ExecucaoAgendada, Execucao
from backend.app.models import db as _db
from datetime import datetime, timedelta
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
        app.register_blueprint(execucoes_agendadas_bp)
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

def test_agendar_execucao_sucesso(client):
    data_agendada = (datetime.utcnow() + timedelta(seconds=1)).isoformat()
    payload = {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1", "data_agendada": data_agendada, "usuario": "tester"}
    resp = client.post('/api/execucoes_agendadas/agendar', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert "id" in data

def test_agendar_execucao_parametros_invalidos(client):
    # categoria_id ausente
    resp = client.post('/api/execucoes_agendadas/agendar', json={"palavras_chave": ["python"]})
    assert resp.status_code == 400
    # palavras_chave ausente
    resp = client.post('/api/execucoes_agendadas/agendar', json={"categoria_id": 1})
    assert resp.status_code == 400
    # data_agendada inválida
    resp = client.post('/api/execucoes_agendadas/agendar', json={"categoria_id": 1, "palavras_chave": ["python"], "data_agendada": "invalid"})
    assert resp.status_code == 400

def test_listar_agendadas(client):
    # Agenda execução
    data_agendada = (datetime.utcnow() + timedelta(seconds=1)).isoformat()
    payload = {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1", "data_agendada": data_agendada, "usuario": "tester"}
    client.post('/api/execucoes_agendadas/agendar', json=payload)
    resp = client.get('/api/execucoes_agendadas/agendadas')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["categoria_id"] == 1
    assert data[0]["usuario"] == "tester"

def test_job_agendado_manual(client, app):
    # Agenda execução para agora
    data_agendada = (datetime.utcnow() - timedelta(seconds=1)).isoformat()
    payload = {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1", "data_agendada": data_agendada, "usuario": "tester"}
    client.post('/api/execucoes_agendadas/agendar', json=payload)
    # Executa job manualmente
    from backend.app.services.execucao_service import processar_execucoes_agendadas
    with app.app_context():
        processar_execucoes_agendadas()
        # Verifica se execução foi criada
        execs = Execucao.query.all()
        assert len(execs) >= 1
        ags = ExecucaoAgendada.query.all()
        assert ags[0].status == 'concluida' 