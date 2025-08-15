from flask_sqlalchemy import SQLAlchemy
from .nicho import db
from typing import Dict, List, Optional, Any

class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    id_nicho = db.Column(db.Integer, db.ForeignKey('nichos.id'), nullable=False)
    perfil_cliente = db.Column(db.String(255), nullable=False)
    cluster = db.Column(db.String(255), nullable=False)
    prompt_path = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), nullable=False)

    nicho = db.relationship('Nicho', backref='categorias')

    def __repr__(self):
        return f"<Categoria(id={self.id}, nome='{self.nome}', nicho={self.id_nicho})>" 