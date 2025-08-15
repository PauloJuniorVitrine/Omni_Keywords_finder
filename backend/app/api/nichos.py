from flask import Blueprint, request, jsonify
from backend.app.models import Nicho, db
from backend.app.utils.log_event import log_event
from backend.app.middleware.auth_middleware import auth_required
from typing import Dict, List, Optional, Any

nichos_bp = Blueprint('nichos', __name__, url_prefix='/api/nichos')

@nichos_bp.route('/', methods=['GET'])
@auth_required()
def listar_nichos():
    """
    Lista todos os nichos disponíveis.
    
    ---
    tags:
      - Nichos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de nichos retornada com sucesso
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: ID único do nicho
              nome:
                type: string
                description: Nome do nicho
      401:
        description: Não autorizado
      403:
        description: Acesso negado
    """
    nichos = Nicho.query.all()
    return jsonify([{'id': n.id, 'nome': n.nome} for n in nichos])

@nichos_bp.route('/', methods=['POST'])
@auth_required()
def criar_nicho():
    """
    Cria um novo nicho.
    
    ---
    tags:
      - Nichos
    security:
      - Bearer: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - nome
            properties:
              nome:
                type: string
                description: Nome do nicho
                minLength: 3
                maxLength: 100
    responses:
      201:
        description: Nicho criado com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID do nicho criado
            nome:
              type: string
              description: Nome do nicho
      400:
        description: Dados inválidos
        schema:
          type: object
          properties:
            erro:
              type: string
              description: Descrição do erro
      401:
        description: Não autorizado
      403:
        description: Acesso negado
      409:
        description: Nicho já existe
    """
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        log_event('erro', 'Nicho', detalhes='Nome obrigatório não informado')
        return jsonify({'erro': 'Nome é obrigatório'}), 400
    if not isinstance(nome, str) or len(nome) < 3 or len(nome) > 100:
        log_event('erro', 'Nicho', detalhes='Nome inválido')
        return jsonify({'erro': 'Nome deve ter entre 3 e 100 caracteres'}), 400
    if Nicho.query.filter_by(nome=nome).first():
        log_event('erro', 'Nicho', detalhes=f'Nicho já existe: {nome}')
        return jsonify({'erro': 'Nicho já existe'}), 409
    nicho = Nicho(nome=nome)
    db.session.add(nicho)
    db.session.commit()
    log_event('criação', 'Nicho', id_referencia=nicho.id, detalhes=f'Nicho criado: {nome}')
    return jsonify({'id': nicho.id, 'nome': nicho.nome}), 201

@nichos_bp.route('/<int:nicho_id>', methods=['PUT'])
@auth_required()
def editar_nicho(nicho_id):
    """
    Edita um nicho existente.
    
    ---
    tags:
      - Nichos
    security:
      - Bearer: []
    parameters:
      - name: nicho_id
        in: path
        required: true
        schema:
          type: integer
        description: ID do nicho a ser editado
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - nome
            properties:
              nome:
                type: string
                description: Novo nome do nicho
                minLength: 3
                maxLength: 100
    responses:
      200:
        description: Nicho editado com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
              description: ID do nicho
            nome:
              type: string
              description: Nome atualizado do nicho
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
      403:
        description: Acesso negado
      404:
        description: Nicho não encontrado
      409:
        description: Nicho já existe
    """
    nicho = Nicho.query.get_or_404(nicho_id)
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        log_event('erro', 'Nicho', id_referencia=nicho_id, detalhes='Nome obrigatório não informado (edição)')
        return jsonify({'erro': 'Nome é obrigatório'}), 400
    if not isinstance(nome, str) or len(nome) < 3 or len(nome) > 100:
        log_event('erro', 'Nicho', id_referencia=nicho_id, detalhes='Nome inválido (edição)')
        return jsonify({'erro': 'Nome deve ter entre 3 e 100 caracteres'}), 400
    if Nicho.query.filter(Nicho.nome == nome, Nicho.id != nicho_id).first():
        log_event('erro', 'Nicho', id_referencia=nicho_id, detalhes=f'Nicho já existe: {nome} (edição)')
        return jsonify({'erro': 'Nicho já existe'}), 409
    nicho.nome = nome
    db.session.commit()
    log_event('alteração', 'Nicho', id_referencia=nicho.id, detalhes=f'Nicho alterado para: {nome}')
    return jsonify({'id': nicho.id, 'nome': nicho.nome})

@nichos_bp.route('/<int:nicho_id>', methods=['DELETE'])
@auth_required()
def remover_nicho(nicho_id):
    """
    Remove um nicho existente.
    
    ---
    tags:
      - Nichos
    security:
      - Bearer: []
    parameters:
      - name: nicho_id
        in: path
        required: true
        schema:
          type: integer
        description: ID do nicho a ser removido
    responses:
      204:
        description: Nicho removido com sucesso
      401:
        description: Não autorizado
      403:
        description: Acesso negado
      404:
        description: Nicho não encontrado
    """
    nicho = Nicho.query.get_or_404(nicho_id)
    db.session.delete(nicho)
    db.session.commit()
    log_event('deleção', 'Nicho', id_referencia=nicho.id, detalhes=f'Nicho removido: {nicho.nome}')
    return '', 204 