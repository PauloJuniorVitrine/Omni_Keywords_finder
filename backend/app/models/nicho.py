from flask_sqlalchemy import SQLAlchemy
from typing import Dict, List, Optional, Any

db = SQLAlchemy()

class Nicho(db.Model):
    __tablename__ = 'nichos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    data_criacao = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)

    def __repr__(self):
        return f"<Nicho(id={self.id}, nome='{self.nome}')>" 