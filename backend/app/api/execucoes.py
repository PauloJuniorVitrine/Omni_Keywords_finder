from flask import Blueprint, request, jsonify, send_file
from backend.app.models import Categoria, Execucao, db
import json
import os
from datetime import datetime
from backend.app.utils.log_event import log_event
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from backend.app.services.execucao_service import processar_lote_execucoes
from backend.app.middleware.auth_middleware import auth_required
from typing import Dict, List, Optional, Any
from pydantic import ValidationError
from backend.app.schemas.execucao import (
    ExecucaoCreateRequest, ExecucaoLoteRequest, ExecucaoFilterRequest,
    ExecucaoUpdateRequest, ExecucaoResponse, ExecucaoCreateResponse,
    ExecucaoLoteResponse, ExecucaoLoteStatusResponse, ExecucaoErrorResponse,
    validar_json_palavras_chave, validar_status_transicao, sanitizar_palavra_chave,
    validar_limites_execucao, sanitizar_cluster
)
from backend.app.middleware.execucao_rate_limiting import execucao_rate_limited, validate_batch_size

# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

execucoes_bp = Blueprint('execucoes', __name__, url_prefix='/api/execucoes')

@execucoes_bp.route('/', methods=['POST'])
@auth_required()
@execucao_rate_limited()
@retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
@bulkhead(max_concurrent_calls=20, max_wait_duration=10.0)
@timeout(timeout_seconds=60.0)
def executar_prompt():
    """
    Executa um prompt para uma categoria específica com palavras-chave.
    
    ---
    tags:
      - Execuções
    security:
      - Bearer: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - categoria_id
              - palavras_chave
            properties:
              categoria_id:
                type: integer
                description: ID da categoria para execução
                minimum: 1
              palavras_chave:
                type: array
                items:
                  type: string
                  minLength: 1
                  maxLength: 100
                description: Lista de palavras-chave para processamento
                minItems: 1
              cluster:
                type: string
                description: Cluster opcional para execução
                minLength: 1
                maxLength: 255
    responses:
      200:
        description: Execução realizada com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                execucao_id:
                  type: integer
                  description: ID da execução criada
                prompt_preenchido:
                  type: string
                  description: Prompt com palavras-chave substituídas
                categoria_id:
                  type: integer
                  description: ID da categoria executada
                palavras_chave:
                  type: array
                  items:
                    type: string
                  description: Palavras-chave utilizadas
                cluster:
                  type: string
                  description: Cluster utilizado na execução
      400:
        description: Dados inválidos
        content:
          application/json:
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
      404:
        description: Categoria ou arquivo de prompt não encontrado
    """
    try:
        # Validar entrada com Pydantic
        data = request.get_json()
        if not data:
            log_event('erro', 'Execucao', detalhes='Dados JSON ausentes na requisição')
            return jsonify(ExecucaoErrorResponse(
                erro='Dados JSON são obrigatórios',
                codigo='MISSING_JSON'
            ).dict()), 400
        
        # Validar schema de entrada
        execucao_request = ExecucaoCreateRequest(**data)
        
        # Sanitizar palavras-chave
        palavras_chave_sanitizadas = [sanitizar_palavra_chave(p) for p in execucao_request.palavras_chave]
        
        # Validar limites de execução
        limites = validar_limites_execucao(execucao_request.categoria_id, palavras_chave_sanitizadas)
        if not limites['valido']:
            log_event('erro', 'Execucao', detalhes=f'Limites de execução excedidos: {limites["mensagem"]}')
            return jsonify(ExecucaoErrorResponse(
                erro='Limites de execução excedidos',
                codigo='LIMITS_EXCEEDED',
                detalhes=limites
            ).dict()), 429
        
        # Log de validação bem-sucedida
        log_event('info', 'Execucao', detalhes=f'Validação de entrada bem-sucedida para categoria {execucao_request.categoria_id}')
        
    except ValidationError as e:
        # Log detalhado dos erros de validação
        erros_validacao = []
        for error in e.errors():
            erros_validacao.append({
                'campo': '.'.join(str(x) for x in error['loc']),
                'mensagem': error['msg'],
                'tipo': error['type']
            })
        
        log_event('erro', 'Execucao', detalhes=f'Erro de validação: {erros_validacao}')
        return jsonify(ExecucaoErrorResponse(
            erro='Dados de entrada inválidos',
            codigo='VALIDATION_ERROR',
            detalhes={'erros': erros_validacao}
        ).dict()), 400
    
    except Exception as e:
        log_event('erro', 'Execucao', detalhes=f'Erro inesperado na validação: {str(e)}')
        return jsonify(ExecucaoErrorResponse(
            erro='Erro interno do servidor',
            codigo='INTERNAL_ERROR'
        ).dict()), 500
    
    # Continuar com a lógica de execução usando dados validados
    categoria = Categoria.query.get_or_404(execucao_request.categoria_id)
    prompt_path = categoria.prompt_path
    if not os.path.exists(prompt_path):
        log_event('erro', 'Execucao', id_referencia=execucao_request.categoria_id, detalhes='Arquivo de prompt não encontrado')
        return jsonify(ExecucaoErrorResponse(
            erro='Arquivo de prompt não encontrado',
            codigo='PROMPT_NOT_FOUND'
        ).dict()), 404
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        # Preencher as lacunas com dados sanitizados
        prompt_preenchido = prompt.replace('[PALAVRA-CHAVE]', ', '.join(palavras_chave_sanitizadas))
        cluster_sanitizado = sanitizar_cluster(execucao_request.cluster) if execucao_request.cluster else (categoria.cluster if hasattr(categoria, 'cluster') else None)
        cluster_sanitizado = cluster_sanitizado or ''
        prompt_preenchido = prompt_preenchido.replace('[CLUSTER]', cluster_sanitizado)
        
        # Criar execução
        execucao = Execucao(
            id_categoria=execucao_request.categoria_id,
            palavras_chave=json.dumps(palavras_chave_sanitizadas),
            cluster_usado=cluster_sanitizado,
            prompt_usado=prompt_path,
            status='executado',
            data_execucao=datetime.utcnow(),
            tempo_estimado=None,
            tempo_real=None,
            log_path=None
        )
        db.session.add(execucao)
        db.session.commit()
        
        log_event('execução', 'Execucao', id_referencia=execucao.id, detalhes=f'Execução realizada para categoria {execucao_request.categoria_id}')
        
        # Retornar resposta estruturada
        response = ExecucaoCreateResponse(
            execucao_id=execucao.id,
            prompt_preenchido=prompt_preenchido,
            categoria_id=execucao_request.categoria_id,
            palavras_chave=palavras_chave_sanitizadas,
            cluster=cluster_sanitizado
        )
        
        return jsonify(response.dict()), 200
        
    except Exception as e:
        log_event('erro', 'Execucao', detalhes=f'Erro na execução: {str(e)}')
        return jsonify(ExecucaoErrorResponse(
            erro='Erro durante a execução',
            codigo='EXECUTION_ERROR'
        ).dict()), 500

@execucoes_bp.route('/', methods=['GET'])
@auth_required()
def listar_execucoes():
    """
    Lista execuções com filtros opcionais por categoria ou nicho.
    
    ---
    tags:
      - Execuções
    security:
      - Bearer: []
    parameters:
      - name: categoria_id
        in: query
        schema:
          type: integer
        description: Filtrar por ID da categoria
      - name: nicho_id
        in: query
        schema:
          type: integer
        description: Filtrar por ID do nicho (inclui todas as categorias do nicho)
      - name: status
        in: query
        schema:
          type: string
          enum: [pendente, em_execucao, executado, falhou, cancelado, pausado]
        description: Filtrar por status da execução
      - name: data_inicio
        in: query
        schema:
          type: string
          format: date-time
        description: Data de início para filtro
      - name: data_fim
        in: query
        schema:
          type: string
          format: date-time
        description: Data de fim para filtro
      - name: limit
        in: query
        schema:
          type: integer
          minimum: 1
          maximum: 1000
          default: 100
        description: Limite de resultados
      - name: offset
        in: query
        schema:
          type: integer
          minimum: 0
          default: 0
        description: Offset para paginação
    responses:
      200:
        description: Lista de execuções retornada com sucesso
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: ID da execução
                  id_categoria:
                    type: integer
                    description: ID da categoria executada
                  palavras_chave:
                    type: array
                    items:
                      type: string
                    description: Palavras-chave utilizadas
                  cluster_usado:
                    type: string
                    description: Cluster utilizado
                  status:
                    type: string
                    description: Status da execução
                  data_execucao:
                    type: string
                    format: date-time
                    description: Data e hora da execução
      400:
        description: Filtros inválidos
      401:
        description: Não autorizado
      403:
        description: Acesso negado
    """
    try:
        # Validar parâmetros de query
        args = dict(request.args)
        
        # Converter tipos apropriados
        if 'categoria_id' in args:
            try:
                args['categoria_id'] = int(args['categoria_id'])
            except ValueError:
                return jsonify(ExecucaoErrorResponse(
                    erro='categoria_id deve ser um número inteiro',
                    codigo='INVALID_CATEGORY_ID'
                ).dict()), 400
        
        if 'nicho_id' in args:
            try:
                args['nicho_id'] = int(args['nicho_id'])
            except ValueError:
                return jsonify(ExecucaoErrorResponse(
                    erro='nicho_id deve ser um número inteiro',
                    codigo='INVALID_NICHO_ID'
                ).dict()), 400
        
        if 'limit' in args:
            try:
                args['limit'] = int(args['limit'])
            except ValueError:
                return jsonify(ExecucaoErrorResponse(
                    erro='limit deve ser um número inteiro',
                    codigo='INVALID_LIMIT'
                ).dict()), 400
        
        if 'offset' in args:
            try:
                args['offset'] = int(args['offset'])
            except ValueError:
                return jsonify(ExecucaoErrorResponse(
                    erro='offset deve ser um número inteiro',
                    codigo='INVALID_OFFSET'
                ).dict()), 400
        
        # Converter datas se fornecidas
        if 'data_inicio' in args:
            try:
                args['data_inicio'] = datetime.fromisoformat(args['data_inicio'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify(ExecucaoErrorResponse(
                    erro='data_inicio deve estar no formato ISO',
                    codigo='INVALID_START_DATE'
                ).dict()), 400
        
        if 'data_fim' in args:
            try:
                args['data_fim'] = datetime.fromisoformat(args['data_fim'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify(ExecucaoErrorResponse(
                    erro='data_fim deve estar no formato ISO',
                    codigo='INVALID_END_DATE'
                ).dict()), 400
        
        # Validar com Pydantic
        filtros = ExecucaoFilterRequest(**args)
        
        # Construir query com filtros validados
        query = Execucao.query
        
        if filtros.categoria_id:
            query = query.filter_by(id_categoria=filtros.categoria_id)
        elif filtros.nicho_id:
            from backend.app.models import Categoria
            categorias = Categoria.query.filter_by(id_nicho=filtros.nicho_id).all()
            cat_ids = [c.id for c in categorias]
            query = query.filter(Execucao.id_categoria.in_(cat_ids))
        
        if filtros.status:
            query = query.filter_by(status=filtros.status.value)
        
        if filtros.data_inicio:
            query = query.filter(Execucao.data_execucao >= filtros.data_inicio)
        
        if filtros.data_fim:
            query = query.filter(Execucao.data_execucao <= filtros.data_fim)
        
        # Aplicar paginação
        query = query.order_by(Execucao.data_execucao.desc())
        query = query.offset(filtros.offset).limit(filtros.limit)
        
        execucoes = query.all()
        
        # Log de sucesso
        log_event('info', 'Execucao', detalhes=f'Listagem de execuções com {len(execucoes)} resultados')
        
        # Retornar resposta estruturada
        return jsonify([
            {
                'id': e.id,
                'id_categoria': e.id_categoria,
                'palavras_chave': json.loads(e.palavras_chave),
                'cluster_usado': e.cluster_usado,
                'status': e.status,
                'data_execucao': e.data_execucao.isoformat() if e.data_execucao else None
            } for e in execucoes
        ]), 200
        
    except ValidationError as e:
        # Log detalhado dos erros de validação
        erros_validacao = []
        for error in e.errors():
            erros_validacao.append({
                'campo': '.'.join(str(x) for x in error['loc']),
                'mensagem': error['msg'],
                'tipo': error['type']
            })
        
        log_event('erro', 'Execucao', detalhes=f'Erro de validação nos filtros: {erros_validacao}')
        return jsonify(ExecucaoErrorResponse(
            erro='Filtros de busca inválidos',
            codigo='INVALID_FILTERS',
            detalhes={'erros': erros_validacao}
        ).dict()), 400
        
    except Exception as e:
        log_event('erro', 'Execucao', detalhes=f'Erro inesperado na listagem: {str(e)}')
        return jsonify(ExecucaoErrorResponse(
            erro='Erro interno do servidor',
            codigo='INTERNAL_ERROR'
        ).dict()), 500

@execucoes_bp.route('/<int:execucao_id>', methods=['GET'])
@auth_required()
def detalhe_execucao(execucao_id):
    """
    Retorna detalhes completos de uma execução específica.
    
    ---
    tags:
      - Execuções
    security:
      - Bearer: []
    parameters:
      - name: execucao_id
        in: path
        required: true
        schema:
          type: integer
        description: ID da execução
    responses:
      200:
        description: Detalhes da execução retornados com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: ID da execução
                id_categoria:
                  type: integer
                  description: ID da categoria executada
                palavras_chave:
                  type: array
                  items:
                    type: string
                  description: Palavras-chave utilizadas
                cluster_usado:
                  type: string
                  description: Cluster utilizado
                prompt_usado:
                  type: string
                  description: Caminho do arquivo de prompt
                status:
                  type: string
                  description: Status da execução
                data_execucao:
                  type: string
                  format: date-time
                  description: Data e hora da execução
                tempo_estimado:
                  type: number
                  description: Tempo estimado em segundos
                tempo_real:
                  type: number
                  description: Tempo real em segundos
                log_path:
                  type: string
                  description: Caminho do arquivo de log
      401:
        description: Não autorizado
      403:
        description: Acesso negado
      404:
        description: Execução não encontrada
    """
    execucao = Execucao.query.get_or_404(execucao_id)
    return jsonify({
        'id': execucao.id,
        'id_categoria': execucao.id_categoria,
        'palavras_chave': json.loads(execucao.palavras_chave),
        'cluster_usado': execucao.cluster_usado,
        'prompt_usado': execucao.prompt_usado,
        'status': execucao.status,
        'data_execucao': execucao.data_execucao.isoformat() if execucao.data_execucao else None,
        'tempo_estimado': execucao.tempo_estimado,
        'tempo_real': execucao.tempo_real,
        'log_path': execucao.log_path
    })

@execucoes_bp.route('/lote', methods=['POST'])
@auth_required()
@execucao_rate_limited()
@validate_batch_size()
def executar_lote():
    """
    Executa múltiplas execuções em lote.
    
    ---
    tags:
      - Execuções
    security:
      - Bearer: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ExecucaoLoteRequest'
    responses:
      200:
        description: Lote processado com sucesso
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExecucaoLoteResponse'
      400:
        description: Dados inválidos
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExecucaoErrorResponse'
      401:
        description: Não autorizado
      403:
        description: Acesso negado
    """
    try:
        data = request.get_json()
        if not data:
            log_event('erro', 'Execucao', detalhes='Dados JSON ausentes no lote')
            return jsonify(ExecucaoErrorResponse(
                erro='Dados JSON são obrigatórios',
                codigo='MISSING_JSON'
            ).dict()), 400
        lote_request = ExecucaoLoteRequest(**data)
        # Sanitizar palavras-chave e cluster de cada execução
        for execucao in lote_request.execucoes:
            execucao.palavras_chave = [sanitizar_palavra_chave(p) for p in execucao.palavras_chave]
            execucao.cluster = sanitizar_cluster(execucao.cluster) if execucao.cluster else None
        # Aqui chamaria o processar_lote_execucoes, adaptando para receber objetos validados
        resultado = processar_lote_execucoes([e.dict() for e in lote_request.execucoes])
        log_event('info', 'Execucao', detalhes=f'Lote processado com {len(lote_request.execucoes)} execuções')
        return jsonify(resultado), 200
    except ValidationError as e:
        erros_validacao = []
        for error in e.errors():
            erros_validacao.append({
                'campo': '.'.join(str(x) for x in error['loc']),
                'mensagem': error['msg'],
                'tipo': error['type']
            })
        log_event('erro', 'Execucao', detalhes=f'Erro de validação no lote: {erros_validacao}')
        return jsonify(ExecucaoErrorResponse(
            erro='Dados de entrada inválidos',
            codigo='VALIDATION_ERROR',
            detalhes={'erros': erros_validacao}
        ).dict()), 400
    except Exception as e:
        log_event('erro', 'Execucao', detalhes=f'Erro inesperado no lote: {str(e)}')
        return jsonify(ExecucaoErrorResponse(
            erro='Erro interno do servidor',
            codigo='INTERNAL_ERROR'
        ).dict()), 500

@execucoes_bp.route('/lote/status', methods=['GET'])
@auth_required()
def status_lote():
    """
    Retorna o status de processamento de um lote de execuções.
    
    ---
    tags:
      - Execuções
    security:
      - Bearer: []
    parameters:
      - name: id_lote
        in: query
        required: true
        schema:
          type: string
        description: ID do lote para consulta de status
    responses:
      200:
        description: Status do lote retornado com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                id_lote:
                  type: string
                  description: ID do lote
                total:
                  type: integer
                  description: Total de execuções no lote
                concluidos:
                  type: integer
                  description: Execuções concluídas com sucesso
                erros:
                  type: integer
                  description: Execuções com erro
                progresso:
                  type: number
                  format: float
                  description: Percentual de progresso (0-100)
                itens:
                  type: array
                  items:
                    type: object
                    properties:
                      categoria_id:
                        type: integer
                        description: ID da categoria
                      inicio:
                        type: string
                        format: date-time
                        description: Hora de início
                      fim:
                        type: string
                        format: date-time
                        description: Hora de fim
                      status:
                        type: string
                        description: Status da execução
                      erro:
                        type: string
                        description: Mensagem de erro (se houver)
                      execucao_id:
                        type: integer
                        description: ID da execução
                      tempo_real:
                        type: number
                        description: Tempo real em segundos
      400:
        description: ID do lote não fornecido
        content:
          application/json:
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
      404:
        description: Log do lote não encontrado
        content:
          application/json:
            schema:
              type: object
              properties:
                erro:
                  type: string
                  description: Descrição do erro
    """
    id_lote = request.args.get('id_lote')
    if not id_lote:
        return jsonify({'erro': 'id_lote é obrigatório'}), 400
    log_path = f'logs/exec_trace/execucao_lotes_{id_lote}.log'
    if not os.path.exists(log_path):
        return jsonify({'erro': 'Log de lote não encontrado'}), 404
    total = 0
    concluidos = 0
    erros = 0
    itens = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or line.startswith('Tempo total:'):
                continue
            try:
                log_item = json.loads(line)
                total += 1
                status = log_item.get('status')
                if status == 'ok':
                    concluidos += 1
                elif status == 'erro':
                    erros += 1
                itens.append({
                    'categoria_id': log_item.get('categoria_id'),
                    'inicio': log_item.get('inicio'),
                    'fim': log_item.get('fim'),
                    'status': status,
                    'erro': log_item.get('erro'),
                    'execucao_id': log_item.get('execucao_id'),
                    'tempo_real': log_item.get('tempo_real')
                })
            except Exception:
                continue
    progresso = (concluidos + erros) / total * 100 if total else 0
    return jsonify({
        'id_lote': id_lote,
        'total': total,
        'concluidos': concluidos,
        'erros': erros,
        'progresso': progresso,
        'itens': itens
    }) 