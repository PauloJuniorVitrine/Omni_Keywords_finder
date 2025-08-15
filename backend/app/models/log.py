from flask_sqlalchemy import SQLAlchemy
from .nicho import db
from typing import Dict, List, Optional, Any

class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacao = db.Column(db.String(50), nullable=False)
    entidade = db.Column(db.String(50), nullable=False)
    id_referencia = db.Column(db.Integer, nullable=True)
    usuario = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    detalhes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Log(id={self.id}, tipo_operacao='{self.tipo_operacao}', entidade='{self.entidade}')>" 