from flask import Blueprint, request, jsonify
from backend.app.models import Categoria, Execucao
from backend.app.utils.log_event import log_event
from typing import Dict, List, Optional, Any

clusters_bp = Blueprint('clusters', __name__, url_prefix='/api/clusters')

@clusters_bp.route('/sugerir', methods=['GET'])
def sugerir_clusters():
    """
    Sugere clusters relevantes com base na categoria e/ou palavras-chave.
    """
    categoria_id = request.args.get('categoria_id', type=int)
    palavras_chave = request.args.get('palavras_chave')
    if not categoria_id:
        return jsonify({'erro': 'categoria_id é obrigatório'}), 400
    # Busca clusters mais usados para a categoria
    clusters = (
        Execucao.query
        .filter_by(id_categoria=categoria_id)
        .with_entities(Execucao.cluster_usado)
        .distinct()
        .all()
    )
    clusters_list = [c[0] for c in clusters if c[0]]
    # Se houver palavras-chave, pode-se filtrar execuções que contenham alguma delas (heurística simples)
    if palavras_chave:
        import json
        palavras = [p.strip().lower() for p in palavras_chave.split(',') if p.strip()]
        execs = (
            Execucao.query
            .filter_by(id_categoria=categoria_id)
            .all()
        )
        clusters_filtrados = set()
        for e in execs:
            try:
                kws = json.loads(e.palavras_chave)
                if any(p in (kw.lower() for kw in kws) for p in palavras):
                    if e.cluster_usado:
                        clusters_filtrados.add(e.cluster_usado)
            except Exception:
                continue
        if clusters_filtrados:
            clusters_list = list(clusters_filtrados) + [c for c in clusters_list if c not in clusters_filtrados]
    # Limitar a 5 sugestões
    clusters_list = clusters_list[:5]
    log_event('sugestao', 'Cluster', detalhes=f'Sugestão de clusters para categoria {categoria_id}: {clusters_list}')
    return jsonify({'sugestoes': clusters_list}) 