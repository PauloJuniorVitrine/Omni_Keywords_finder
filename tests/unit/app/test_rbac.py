"""
🧪 Teste Unitário - test_rbac.py

Tracing ID: TEST_RBAC_2025_001
Data/Hora: 2025-01-27 20:40:00 UTC
Versão: 1.0
Status: 🔧 CORRIGIDO

Testes unitários para RBAC (Role-Based Access Control) sem logs proibidos.
"""

import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from backend.app.models.user import User
from backend.app.models.role import Role
from backend.app.models.permission import Permission
from backend.app.utils.auth_utils import role_required, permission_required
from backend.app.models import db
from typing import Dict, List, Optional, Any

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    JWTManager(app)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_users(app):
    with app.app_context():
        db.create_all()
        admin_role = Role(nome='admin', descricao='Administrador')
        gestor_role = Role(nome='gestor', descricao='Gestor')
        perm_usuarios = Permission(nome='gerenciar_usuarios', descricao='CRUD usuários')
        admin_role.permissions.append(perm_usuarios)
        user_admin = User(username='admin', email='admin@ex.com', senha_hash='hash_segura_2025', ativo=True)
        user_admin.roles.append(admin_role)
        user_gestor = User(username='gestor', email='gestor@ex.com', senha_hash='hash_segura_2025', ativo=True)
        user_gestor.roles.append(gestor_role)
        user_inativo = User(username='inativo', email='inativo@ex.com', senha_hash='hash_segura_2025', ativo=False)
        db.session.add_all([admin_role, gestor_role, perm_usuarios, user_admin, user_gestor, user_inativo])
        db.session.commit()
        yield
        db.drop_all()

@pytest.mark.usefixtures('setup_users')
def test_role_required_access_granted(app):
    """Testa acesso concedido para usuário com role adequada."""
    with app.app_context():
        @app.route('/admin')
        @role_required('admin')
        def admin_only():
            return 'ok', 200
        client = app.test_client()
        token = create_access_token(identity=str(User.query.filter_by(username='admin').first().id))
        rv = client.get('/admin', headers={'Authorization': f'Bearer {token}'})
        
        # Verifica status code e dados da resposta
        assert rv.status_code == 200, f"Esperado 200, obtido {rv.status_code}. Resposta: {rv.data.decode()}"
        assert rv.data.decode() == 'ok'

@pytest.mark.usefixtures('setup_users')
def test_role_required_access_denied(app):
    """Testa acesso negado para usuário sem role adequada."""
    with app.app_context():
        @app.route('/admin')
        @role_required('admin')
        def admin_only():
            return 'ok', 200
        client = app.test_client()
        token = create_access_token(identity=str(User.query.filter_by(username='gestor').first().id))
        rv = client.get('/admin', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 403

@pytest.mark.usefixtures('setup_users')
def test_permission_required_access_granted(app):
    """Testa acesso concedido para usuário com permissão adequada."""
    with app.app_context():
        @app.route('/usuarios')
        @permission_required('gerenciar_usuarios')
        def usuarios():
            return 'ok', 200
        client = app.test_client()
        token = create_access_token(identity=str(User.query.filter_by(username='admin').first().id))
        rv = client.get('/usuarios', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200

@pytest.mark.usefixtures('setup_users')
def test_permission_required_access_denied(app):
    """Testa acesso negado para usuário sem permissão adequada."""
    with app.app_context():
        @app.route('/usuarios')
        @permission_required('gerenciar_usuarios')
        def usuarios():
            return 'ok', 200
        client = app.test_client()
        token = create_access_token(identity=str(User.query.filter_by(username='gestor').first().id))
        rv = client.get('/usuarios', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 403

@pytest.mark.usefixtures('setup_users')
def test_inactive_user_denied(app):
    """Testa acesso negado para usuário inativo."""
    with app.app_context():
        @app.route('/admin')
        @role_required('admin')
        def admin_only():
            return 'ok', 200
        client = app.test_client()
        token = create_access_token(identity=str(User.query.filter_by(username='inativo').first().id))
        rv = client.get('/admin', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 403 