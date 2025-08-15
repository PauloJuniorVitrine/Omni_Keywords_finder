from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.app.models import db
from typing import Dict, List, Optional, Any

class Notificacao(db.Model):
    """
    Modelo de Notificação para alertas e eventos do sistema.
    """
    __tablename__ = 'notificacoes'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(128), nullable=False)
    mensagem = Column(String(512), nullable=False)
    tipo = Column(String(32), nullable=False, default='info')  # info, warning, error
    lida = Column(Boolean, default=False, nullable=False)
    usuario = Column(String(64), nullable=True)  # opcional: destinatário
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Notificacao {self.id} {self.titulo}>' 