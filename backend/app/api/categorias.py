from flask import Blueprint, request, jsonify
from backend.app.models import Categoria, Nicho
from backend.app.main import db
import os
from werkzeug.utils import secure_filename
from backend.app.utils.log_event import log_event
from typing import Dict, List, Optional, Any

categorias_bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')

UPLOAD_FOLDER = 'backend/prompts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@categorias_bp.route('/<int:nicho_id>/', methods=['GET'])
def listar_categorias(nicho_id):
    categorias = Categoria.query.filter_by(id_nicho=nicho_id).all()
    return jsonify([
        {
            'id': c.id,
            'nome': c.nome,
            'perfil_cliente': c.perfil_cliente,
            'cluster': c.cluster,
            'prompt_path': c.prompt_path
        } for c in categorias
    ])

@categorias_bp.route('/<int:nicho_id>/', methods=['POST'])
def criar_categoria(nicho_id):
    if Categoria.query.filter_by(id_nicho=nicho_id).count() >= 7:
        log_event('erro', 'Categoria', id_referencia=nicho_id, detalhes='Limite de 7 categorias por nicho atingido')
        return jsonify({'erro': 'Limite de 7 categorias por nicho atingido'}), 400
    data = request.form or request.get_json()
    nome = data.get('nome')
    perfil_cliente = data.get('perfil_cliente')
    cluster = data.get('cluster')
    prompt_file = request.files.get('prompt')
    if not all([nome, perfil_cliente, cluster, prompt_file]):
        log_event('erro', 'Categoria', id_referencia=nicho_id, detalhes='Campos obrigatórios ou arquivo de prompt ausente')
        return jsonify({'erro': 'Todos os campos e o arquivo de prompt são obrigatórios'}), 400
    # Validação de campos
    if not isinstance(nome, str) or len(nome) < 3 or len(nome) > 100:
        log_event('erro', 'Categoria', id_referencia=nicho_id, detalhes='Nome inválido')
        return jsonify({'erro': 'Nome deve ter entre 3 e 100 caracteres'}), 400
    if not isinstance(perfil_cliente, str) or len(perfil_cliente) < 3 or len(perfil_cliente) > 255:
        log_event('erro', 'Categoria', id_referencia=nicho_id, detalhes='Perfil de cliente inválido')
        return jsonify({'erro': 'Perfil de cliente deve ter entre 3 e 255 caracteres'}), 400
    if not isinstance(cluster, str) or len(cluster) < 1 or len(cluster) > 255:
        log_event('erro', 'Categoria', id_referencia=nicho_id, detalhes='Cluster inválido')
        return jsonify({'erro': 'Cluster deve ter entre 1 e 255 caracteres'}), 400
    # Validação de extensão e tamanho
    if not prompt_file.filename.lower().endswith('.txt'):
        log_event('erro', 'Categoria', id_referencia=nicho_id, detalhes='Arquivo de prompt não é .txt')
        return jsonify({'erro': 'O arquivo de prompt deve ser .txt'}), 400
    prompt_file.seek(0, os.SEEK_END)
    tamanho = prompt_file.tell()
    prompt_file.seek(0)
    if tamanho > 100 * 1024:
        log_event('erro', 'Categoria', id_referencia=nicho_id, detalhes='Arquivo de prompt excede 100KB')
        return jsonify({'erro': 'O arquivo de prompt deve ter no máximo 100KB'}), 400
    filename = secure_filename(prompt_file.filename)
    prompt_path = os.path.join(UPLOAD_FOLDER, filename)
    prompt_file.save(prompt_path)
    # Validação: só pode haver as lacunas [PALAVRA-CHAVE] e [CLUSTER] em branco
    with open(prompt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    import re
    lacunas = re.findall(r'\[([A-Z\-]+)\]', content)
    lacunas_unicas = set(lacunas)
    if not lacunas_unicas.issubset({'PALAVRA-CHAVE', 'CLUSTER'}):
        os.remove(prompt_path)
        log_event('erro', 'Categoria', id_referencia=nicho_id, detalhes='Prompt inválido: lacunas não permitidas')
        return jsonify({'erro': 'O prompt só pode conter as lacunas [PALAVRA-CHAVE] e [CLUSTER] em branco'}), 400
    categoria = Categoria(
        nome=nome,
        id_nicho=nicho_id,
        perfil_cliente=perfil_cliente,
        cluster=cluster,
        prompt_path=prompt_path
    )
    db.session.add(categoria)
    db.session.commit()
    log_event('criação', 'Categoria', id_referencia=categoria.id, detalhes=f'Categoria criada: {nome}')
    return jsonify({'id': categoria.id, 'nome': categoria.nome}), 201

@categorias_bp.route('/<int:categoria_id>', methods=['PUT'])
def editar_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    data = request.get_json()
    nome = data.get('nome')
    perfil_cliente = data.get('perfil_cliente')
    cluster = data.get('cluster')
    if not all([nome, perfil_cliente, cluster]):
        log_event('erro', 'Categoria', id_referencia=categoria_id, detalhes='Campos obrigatórios ausentes (edição)')
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
    if not isinstance(nome, str) or len(nome) < 3 or len(nome) > 100:
        log_event('erro', 'Categoria', id_referencia=categoria_id, detalhes='Nome inválido (edição)')
        return jsonify({'erro': 'Nome deve ter entre 3 e 100 caracteres'}), 400
    if not isinstance(perfil_cliente, str) or len(perfil_cliente) < 3 or len(perfil_cliente) > 255:
        log_event('erro', 'Categoria', id_referencia=categoria_id, detalhes='Perfil de cliente inválido (edição)')
        return jsonify({'erro': 'Perfil de cliente deve ter entre 3 e 255 caracteres'}), 400
    if not isinstance(cluster, str) or len(cluster) < 1 or len(cluster) > 255:
        log_event('erro', 'Categoria', id_referencia=categoria_id, detalhes='Cluster inválido (edição)')
        return jsonify({'erro': 'Cluster deve ter entre 1 e 255 caracteres'}), 400
    categoria.nome = nome
    categoria.perfil_cliente = perfil_cliente
    categoria.cluster = cluster
    db.session.commit()
    log_event('alteração', 'Categoria', id_referencia=categoria.id, detalhes=f'Categoria alterada: {nome}')
    return jsonify({'id': categoria.id, 'nome': categoria.nome})

@categorias_bp.route('/<int:categoria_id>', methods=['DELETE'])
def remover_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    db.session.delete(categoria)
    db.session.commit()
    log_event('deleção', 'Categoria', id_referencia=categoria.id, detalhes=f'Categoria removida: {categoria.nome}')
    return '', 204 