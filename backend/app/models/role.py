from backend.app.models import db
from sqlalchemy.orm import relationship
from typing import List
from backend.app.models.associations import role_permissions, user_roles

class Role(db.Model):
    """Papel de acesso, agrupando permissões e usuários."""
    __tablename__ = 'roles'
    id: int = db.Column(db.Integer, primary_key=True)
    nome: str = db.Column(db.String(64), unique=True, nullable=False)
    descricao: str = db.Column(db.String(255))
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    users = relationship('User', secondary=user_roles, back_populates='roles')

    def __repr__(self):
        return f'<Role {self.nome}>' 