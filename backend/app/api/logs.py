from flask import Blueprint, request, jsonify
from backend.app.models import Log, db
from datetime import datetime
from backend.app.utils.log_event import log_event
from typing import Dict, List, Optional, Any

logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')

@logs_bp.route('/execucoes', methods=['GET'])
def listar_logs_execucoes():
    tipo_operacao = request.args.get('tipo_operacao')
    entidade = request.args.get('entidade')
    id_referencia = request.args.get('id_referencia', type=int)
    usuario = request.args.get('usuario')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    query = Log.query
    if tipo_operacao:
        query = query.filter_by(tipo_operacao=tipo_operacao)
    if entidade:
        query = query.filter_by(entidade=entidade)
    if id_referencia:
        query = query.filter_by(id_referencia=id_referencia)
    if usuario:
        query = query.filter_by(usuario=usuario)
    if data_inicio:
        dt_inicio = datetime.fromisoformat(data_inicio)
        query = query.filter(Log.timestamp >= dt_inicio)
    if data_fim:
        dt_fim = datetime.fromisoformat(data_fim)
        query = query.filter(Log.timestamp <= dt_fim)
    logs = query.order_by(Log.timestamp.desc()).all()
    log_event('consulta', 'Log', detalhes=f'Consulta de logs: tipo_operacao={tipo_operacao}, entidade={entidade}, usuario={usuario}')
    return jsonify([
        {
            'id': list_data.id,
            'tipo_operacao': list_data.tipo_operacao,
            'entidade': list_data.entidade,
            'id_referencia': list_data.id_referencia,
            'usuario': list_data.usuario,
            'timestamp': list_data.timestamp.isoformat() if list_data.timestamp else None,
            'detalhes': list_data.detalhes
        } for list_data in logs
    ])

@logs_bp.route('/dashboard/metrics', methods=['GET'])
def dashboard_metrics():
    from backend.app.models import Nicho, Categoria, Execucao, Log
    from datetime import datetime, timedelta
    # Filtros opcionais
    nicho_id = request.args.get('nicho_id', type=int)
    categoria_id = request.args.get('categoria_id', type=int)
    dias = request.args.get('dias', type=int, default=7)
    dt_inicio = datetime.utcnow() - timedelta(days=dias)
    # Execuções
    exec_query = Execucao.query.filter(Execucao.data_execucao >= dt_inicio)
    if categoria_id:
        exec_query = exec_query.filter_by(id_categoria=categoria_id)
    elif nicho_id:
        categorias = Categoria.query.filter_by(id_nicho=nicho_id).all()
        cat_ids = [c.id for c in categorias]
        exec_query = exec_query.filter(Execucao.id_categoria.in_(cat_ids))
    execucoes = exec_query.all()
    total_execucoes = len(execucoes)
    tempo_medio = (sum([e.tempo_real or 0 for e in execucoes]) / total_execucoes) if total_execucoes else 0
    # Clusters
    total_clusters = Categoria.query.count()
    # Erros
    erro_query = Log.query.filter(Log.timestamp >= dt_inicio, Log.tipo_operacao == 'erro')
    if categoria_id:
        erro_query = erro_query.filter(Log.entidade == 'Categoria', Log.id_referencia == categoria_id)
    elif nicho_id:
        erro_query = erro_query.filter(Log.entidade == 'Nicho', Log.id_referencia == nicho_id)
    total_erros = erro_query.count()
    # Logs recentes
    logs = Log.query.order_by(Log.timestamp.desc()).limit(10).all()
    logs_serializados = [
        {
            'id': list_data.id,
            'tipo_operacao': list_data.tipo_operacao,
            'entidade': list_data.entidade,
            'id_referencia': list_data.id_referencia,
            'usuario': list_data.usuario,
            'timestamp': list_data.timestamp.isoformat() if list_data.timestamp else None,
            'detalhes': list_data.detalhes
        } for list_data in logs
    ]
    return jsonify({
        'total_execucoes': total_execucoes,
        'tempo_medio_execucao': tempo_medio,
        'total_clusters': total_clusters,
        'total_erros': total_erros,
        'logs_recentes': logs_serializados
    }) 