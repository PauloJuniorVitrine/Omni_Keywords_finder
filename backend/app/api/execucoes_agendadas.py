from flask import Blueprint, request, jsonify
from backend.app.models.execucao_agendada import ExecucaoAgendada
from backend.app.models import db
from datetime import datetime
import json
from backend.app.utils.log_event import log_event
from typing import Dict, List, Optional, Any

execucoes_agendadas_bp = Blueprint('execucoes_agendadas', __name__, url_prefix='/api/execucoes')

@execucoes_agendadas_bp.route('/agendar', methods=['POST'])
def agendar_execucao():
    """
    Agenda uma execução futura de prompt.
    """
    data = request.get_json()
    categoria_id = data.get('categoria_id')
    palavras_chave = data.get('palavras_chave')
    cluster = data.get('cluster')
    data_agendada = data.get('data_agendada')
    usuario = data.get('usuario')
    if not categoria_id or not palavras_chave or not data_agendada:
        log_event('erro', 'ExecucaoAgendada', detalhes='Campos obrigatórios ausentes no agendamento')
        log_event(
            titulo='Erro ao agendar execução',
            mensagem='Campos obrigatórios ausentes.',
            tipo='error',
            usuario=usuario
        )
        return jsonify({'erro': 'categoria_id, palavras_chave e data_agendada são obrigatórios'}), 400
    try:
        dt_agendada = datetime.fromisoformat(data_agendada)
    except Exception:
        return jsonify({'erro': 'data_agendada inválida (formato ISO esperado)'}), 400
    agendamento = ExecucaoAgendada(
        categoria_id=categoria_id,
        palavras_chave=json.dumps(palavras_chave),
        cluster=cluster,
        data_agendada=dt_agendada,
        status='pendente',
        usuario=usuario,
        criado_em=datetime.utcnow()
    )
    db.session.add(agendamento)
    db.session.commit()
    log_event('agendamento', 'ExecucaoAgendada', id_referencia=agendamento.id, detalhes=f'Execução agendada para {dt_agendada}')
    log_event(
        titulo='Execução agendada',
        mensagem=f'Execução agendada para {dt_agendada.strftime("%data/%m/%Y %H:%M")}',
        tipo='info',
        usuario=usuario
    )
    return jsonify({'id': agendamento.id}), 201

@execucoes_agendadas_bp.route('/agendadas', methods=['GET'])
def listar_agendadas():
    """
    Lista execuções agendadas, com filtros opcionais (status, usuario, data).
    """
    status = request.args.get('status')
    usuario = request.args.get('usuario')
    query = ExecucaoAgendada.query
    if status:
        query = query.filter_by(status=status)
    if usuario:
        query = query.filter_by(usuario=usuario)
    agendadas = query.order_by(ExecucaoAgendada.data_agendada.asc()).all()
    return jsonify([
        {
            'id': a.id,
            'categoria_id': a.categoria_id,
            'palavras_chave': json.loads(a.palavras_chave),
            'cluster': a.cluster,
            'data_agendada': a.data_agendada.isoformat(),
            'status': a.status,
            'usuario': a.usuario,
            'criado_em': a.criado_em.isoformat(),
            'executado_em': a.executado_em.isoformat() if a.executado_em else None,
            'erro': a.erro
        } for a in agendadas
    ])

@execucoes_agendadas_bp.route('/agendadas/<int:agendamento_id>', methods=['DELETE'])
def cancelar_agendamento(agendamento_id):
    """
    Cancela um agendamento futuro.
    """
    agendamento = ExecucaoAgendada.query.get_or_404(agendamento_id)
    if agendamento.status not in ['pendente', 'erro']:
        return jsonify({'erro': 'Só é possível cancelar agendamentos pendentes ou com erro.'}), 400
    agendamento.status = 'cancelada'
    db.session.commit()
    log_event('cancelamento', 'ExecucaoAgendada', id_referencia=agendamento.id, detalhes='Agendamento cancelado')
    log_event(
        titulo='Agendamento cancelado',
        mensagem=f'Execução agendada para {agendamento.data_agendada.strftime("%data/%m/%Y %H:%M")} foi cancelada.',
        tipo='warning',
        usuario=agendamento.usuario
    )
    return jsonify({'ok': True}) 