import pytest
from flask import Flask
from backend.app.api.payments import payments_bp
from unittest.mock import patch
from typing import Dict, List, Optional, Any

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(payments_bp)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_payment_success(client):
    resp = client.post('/api/payments/create', json={'valor': 100, 'metodo': 'stripe'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['status'] == 'pending'
    assert data['metodo'] == 'stripe'

def test_webhook_valid_signature(client):
    import hmac, hashlib, os
    payload = b'{"id":123,"status":"paid"}'
    secret = 'testsecret'
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    with patch.dict(os.environ, {'STRIPE_WEBHOOK_SECRET': secret}):
        resp = client.post('/api/payments/webhook', data=payload, headers={'X-Signature': signature})
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'ok'

def test_webhook_invalid_signature(client):
    payload = b'{"id":123,"status":"paid"}'
    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'testsecret'}):
        resp = client.post('/api/payments/webhook', data=payload, headers={'X-Signature': 'invalid'})
        assert resp.status_code == 400
        assert 'erro' in resp.get_json()

def test_webhook_ip_not_allowed(client, monkeypatch):
    import hmac, hashlib, os
    payload = b'{"id":123,"status":"paid"}'
    secret = 'testsecret'
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    with patch.dict(os.environ, {'STRIPE_WEBHOOK_SECRET': secret, 'WEBHOOK_ALLOWED_IPS': '1.2.3.4'}):
        # Simula IP remoto diferente
        monkeypatch.setattr('flask.Request.remote_addr', '5.6.7.8')
        resp = client.post('/api/payments/webhook', data=payload, headers={'X-Signature': signature})
        assert resp.status_code == 403
        assert 'erro' in resp.get_json() 