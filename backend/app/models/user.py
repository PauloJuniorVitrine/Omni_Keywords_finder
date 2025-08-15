from backend.app.models import db
from sqlalchemy.orm import relationship
from typing import List
from backend.app.models.associations import user_roles

class User(db.Model):
    """Usuário do sistema, autenticável e associado a papéis (roles)."""
    __tablename__ = 'users'
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash: str = db.Column(db.String(128), nullable=False)
    ativo: bool = db.Column(db.Boolean, default=True)
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    provider: str = db.Column(db.String(32), nullable=True)  # Ex: 'google', 'github'
    provider_id: str = db.Column(db.String(128), nullable=True)  # ID do usuário no provedor externo

    def __repr__(self):
        return f'<User {self.username}>' 