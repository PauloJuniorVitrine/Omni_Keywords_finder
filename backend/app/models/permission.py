from backend.app.models import db
from sqlalchemy.orm import relationship
from typing import List
from backend.app.models.associations import role_permissions

class Permission(db.Model):
    """Permissão granular de acesso a operações do sistema."""
    __tablename__ = 'permissions'
    id: int = db.Column(db.Integer, primary_key=True)
    nome: str = db.Column(db.String(64), unique=True, nullable=False)
    descricao: str = db.Column(db.String(255))
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')

    def __repr__(self):
        return f'<Permission {self.nome}>' 