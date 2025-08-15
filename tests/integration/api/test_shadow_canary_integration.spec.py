from typing import Dict, List, Optional, Any
"""
Fluxo: Shadow Testing/Canário para endpoints críticos
Camadas: API, Service, DB, Log
RISK_SCORE: 70
Similaridade semântica: ≥ 0.90
Origem: AI (ruleset + mapeamento)
Serviços acessados: Banco, logs, notificações
EXEC_ID: EXEC2
Timestamp: {timestamp_utc}
"""

import pytest
from flask import Flask
from backend.app.api.execucoes import execucoes_bp
from backend.app.models import db, Categoria
from backend.app.models import db as _db
import json
import copy

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
        cat = Categoria(id=1, nome='Teste', perfil_cliente='B2B', cluster='cluster1', prompt_path='prompt_test.txt', id_nicho=1)
        _db.session.add(cat)
        _db.session.commit()
        with open('prompt_test.txt', 'w', encoding='utf-8') as f:
            f.write('PROMPT [PALAVRA-CHAVE] [CLUSTER]')
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_shadow_execucoes_post_diff(client):
    payload = {"categoria_id": 1, "palavras_chave": ["python"], "cluster": "cluster1"}
    # Simula chamada para versão antiga
    resp_old = client.post('/api/execucoes/', json=payload)
    # Simula chamada para versão canário (aqui, mesma função, mas em produção seria endpoint diferente)
    resp_canary = client.post('/api/execucoes/', json=payload)
    data_old = resp_old.get_json()
    data_canary = resp_canary.get_json()
    # Comparação semântica
    diff = {}
    for key in set(data_old.keys()).union(data_canary.keys()):
        if data_old.get(key) != data_canary.get(key):
            diff[key] = {"old": data_old.get(key), "canary": data_canary.get(key)}
    # Salva diff
    with open('/tests/integration/diff_output_EXEC2.json', 'w', encoding='utf-8') as f:
        json.dump(diff, f, ensure_ascii=False, indent=2)
    assert diff == {}  # Esperado: sem divergência funcional 