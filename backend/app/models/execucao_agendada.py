from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.app.models import db
from typing import Dict, List, Optional, Any

class ExecucaoAgendada(db.Model):
    """
    Modelo de Execução Agendada para prompts a serem executados futuramente.
    """
    __tablename__ = 'execucoes_agendadas'

    id = Column(Integer, primary_key=True)
    categoria_id = Column(Integer, nullable=False)
    palavras_chave = Column(Text, nullable=False)  # JSON serializado
    cluster = Column(String(255), nullable=True)
    data_agendada = Column(DateTime, nullable=False)
    status = Column(String(32), nullable=False, default='pendente')  # pendente, executando, concluida, cancelada, erro
    usuario = Column(String(64), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    executado_em = Column(DateTime, nullable=True)
    erro = Column(Text, nullable=True)

    def __repr__(self):
        return f'<ExecucaoAgendada {self.id} {self.status}>' 