from backend.app.models import Log, db
from datetime import datetime
from flask import g
from typing import Dict, List, Optional, Any

def log_event(tipo_operacao: str, entidade: str, id_referencia: int = None, usuario: str = None, detalhes: str = None):
    """
    Registra um evento de log estruturado no banco de dados.
    Parâmetros:
        tipo_operacao (str): Tipo da operação (criação, alteração, deleção, execução, erro, etc).
        entidade (str): Nome da entidade relacionada (ex: Nicho, Categoria, Execucao).
        id_referencia (int, opcional): ID da entidade relacionada.
        usuario (str, opcional): Usuário responsável pela ação.
        detalhes (str, opcional): Detalhes adicionais do evento.
    """
    log = Log(
        tipo_operacao=tipo_operacao,
        entidade=entidade,
        id_referencia=id_referencia,
        usuario=usuario or getattr(g, 'current_user', None),
        timestamp=datetime.utcnow(),
        detalhes=detalhes
    )
    db.session.add(log)
    db.session.commit()
    return log 