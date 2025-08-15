from flask import Blueprint, request, jsonify
from backend.app.models.notificacao import Notificacao
from backend.app.models import db
from datetime import datetime
from typing import Dict, List, Optional, Any

notificacoes_bp = Blueprint('notificacoes', __name__, url_prefix='/api/notificacoes')

@notificacoes_bp.route('', methods=['GET'])
def listar_notificacoes():
    """
    Listar notificações, com filtros opcionais (lida, tipo, usuario, limit).
    """
    query = Notificacao.query
    lida = request.args.get('lida')
    tipo = request.args.get('tipo')
    usuario = request.args.get('usuario')
    limit = int(request.args.get('limit', 20))
    if lida is not None:
        query = query.filter_by(lida=(lida == 'true'))
    if tipo:
        query = query.filter_by(tipo=tipo)
    if usuario:
        query = query.filter_by(usuario=usuario)
    notificacoes = query.order_by(Notificacao.timestamp.desc()).limit(limit).all()
    return jsonify([
        {
            'id': n.id,
            'titulo': n.titulo,
            'mensagem': n.mensagem,
            'tipo': n.tipo,
            'lida': n.lida,
            'usuario': n.usuario,
            'timestamp': n.timestamp.isoformat() + 'Z',
        } for n in notificacoes
    ])

@notificacoes_bp.route('', methods=['POST'])
def criar_notificacao():
    """
    Criar uma nova notificação.
    """
    data = request.get_json()
    if not data or not data.get('titulo') or not data.get('mensagem'):
        return jsonify({'erro': 'Título e mensagem são obrigatórios.'}), 400
    n = Notificacao(
        titulo=data['titulo'],
        mensagem=data['mensagem'],
        tipo=data.get('tipo', 'info'),
        usuario=data.get('usuario'),
        timestamp=datetime.utcnow(),
    )
    db.session.add(n)
    db.session.commit()
    return jsonify({'id': n.id}), 201

@notificacoes_bp.route('/<int:notificacao_id>', methods=['PATCH'])
def marcar_como_lida(notificacao_id):
    """
    Marcar notificação como lida.
    """
    n = Notificacao.query.get_or_404(notificacao_id)
    n.lida = True
    db.session.commit()
    return jsonify({'ok': True}) 