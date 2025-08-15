from flask_sqlalchemy import SQLAlchemy
from .nicho import db
from typing import Dict, List, Optional, Any

class Execucao(db.Model):
    __tablename__ = 'execucoes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    palavras_chave = db.Column(db.Text, nullable=False)  # JSON serializado
    cluster_usado = db.Column(db.String(255), nullable=False)
    prompt_usado = db.Column(db.String(255), nullable=False)  # hash ou caminho/versão
    status = db.Column(db.String(50), nullable=False)
    data_execucao = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    tempo_estimado = db.Column(db.Float, nullable=True)
    tempo_real = db.Column(db.Float, nullable=True)
    log_path = db.Column(db.String(255), nullable=True)

    categoria = db.relationship('Categoria', backref='execucoes')

    def __repr__(self):
        return f"<Execucao(id={self.id}, categoria={self.id_categoria}, status='{self.status}')>" 