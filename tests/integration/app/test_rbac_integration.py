import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from backend.app.models import db
from backend.app.models.user import User
from backend.app.models.role import Role
from backend.app.models.permission import Permission
from backend.app.api.rbac import rbac_bp
from typing import Dict, List, Optional, Any

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    JWTManager(app)
    app.register_blueprint(rbac_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_rbac(app):
    with app.app_context():
        db.create_all()
        admin_role = Role(nome='admin', descricao='Administrador')
        gestor_role = Role(nome='gestor', descricao='Gestor')
        perm_usuarios = Permission(nome='gerenciar_usuarios', descricao='CRUD usuários')
        admin_role.permissions.append(perm_usuarios)
        user_admin = User(username='admin', email='admin@ex.com', senha_hash='hash', ativo=True)
        user_admin.roles.append(admin_role)
        user_gestor = User(username='gestor', email='gestor@ex.com', senha_hash='hash', ativo=True)
        user_gestor.roles.append(gestor_role)
        db.session.add_all([admin_role, gestor_role, perm_usuarios, user_admin, user_gestor])
        db.session.commit()
        yield
        db.drop_all()

def get_token(client, username):
    user = User.query.filter_by(username=username).first()
    return create_access_token(identity=str(user.id))

def test_listar_usuarios_admin(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'admin')
        rv = client.get('/api/rbac/usuarios', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200

def test_listar_usuarios_negado(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'gestor')
        rv = client.get('/api/rbac/usuarios', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200  # gestor pode listar
        # Testar acesso negado para criar
        rv2 = client.post('/api/rbac/usuarios', json={
            'username': 'novo', 'email': 'novo@ex.com', 'senha': '123'
        }, headers={'Authorization': f'Bearer {token}'})
        assert rv2.status_code == 403

def test_criar_usuario_admin(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'admin')
        rv = client.post('/api/rbac/usuarios', json={
            'username': 'novo', 'email': 'novo@ex.com', 'senha': '123'
        }, headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 201

def test_criar_usuario_duplicado(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'admin')
        rv = client.post('/api/rbac/usuarios', json={
            'username': 'admin', 'email': 'admin2@ex.com', 'senha': '123'
        }, headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 409

def test_editar_usuario_admin(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'admin')
        user = User.query.filter_by(username='gestor').first()
        rv = client.put(f'/api/rbac/usuarios/{user.id}', json={'email': 'novo@ex.com'}, headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200

def test_remover_usuario_admin(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'admin')
        user = User.query.filter_by(username='gestor').first()
        rv = client.delete(f'/api/rbac/usuarios/{user.id}', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 204

def test_listar_papeis_admin(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'admin')
        rv = client.get('/api/rbac/papeis', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200

def test_criar_papel_negado(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'gestor')
        rv = client.post('/api/rbac/papeis', json={'nome': 'novo', 'descricao': 'desc'}, headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 403

def test_criar_permissao_admin(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'admin')
        rv = client.post('/api/rbac/permissoes', json={'nome': 'nova', 'descricao': 'desc'}, headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 201

def test_editar_permissao_negado(client, app, setup_rbac):
    with app.app_context():
        token = get_token(client, 'gestor')
        perm = Permission.query.first()
        rv = client.put(f'/api/rbac/permissoes/{perm.id}', json={'descricao': 'nova'}, headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 403 