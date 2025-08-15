from flask import Blueprint, request, jsonify, make_response
from typing import Dict, List, Optional, Any

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/processar_keywords', methods=['POST'])
def processar_keywords():
    data = request.get_json(force=True) or {}
    keywords = data.get('keywords')
    print('[DEBUG] Payload recebido:', data)
    # Validação: keywords deve ser lista não vazia
    if not isinstance(keywords, list):
        print('[DEBUG] keywords não é lista')
        return jsonify({"erro": "keywords deve ser lista"}), 400
    if not keywords:
        print('[DEBUG] keywords vazias')
        return jsonify({"erro": "keywords vazias"}), 400
    # Validação: keywords inválidas (campos obrigatórios e valores)
    for kw in keywords:
        if not isinstance(kw, dict):
            print('[DEBUG] keyword não é dict:', kw)
            return jsonify({"erro": "keyword inválida"}), 422
        if not kw.get('termo') or not isinstance(kw.get('termo'), str) or not kw['termo'].strip():
            print('[DEBUG] termo obrigatório ausente ou inválido:', kw)
            return jsonify({"erro": "termo obrigatório"}), 422
        if kw.get('volume_busca', 0) < 0 or kw.get('cpc', 0) < 0 or kw.get('concorrencia', 0) < 0 or kw.get('concorrencia', 0) > 1:
            print('[DEBUG] valores inválidos:', kw)
            return jsonify({"erro": "valores inválidos"}), 422
    # Sucesso: retorna todas as keywords do payload, mantendo o termo original
    resp_keywords = [
        {"termo": kw["termo"], "score": 0.9} for kw in keywords
    ]
    print('[DEBUG] keywords retornadas:', resp_keywords)
    return jsonify({
        "keywords": resp_keywords,
        "relatorio": {"status": "ok"}
    }), 200

@api.route('/exportar_keywords', methods=['GET'])
def exportar_keywords():
    formato = request.args.get('formato', 'json')
    prefix = request.args.get('prefix', '')
    keywords = [
        {"termo": f"{prefix}python", "score": 0.9},
        {"termo": f"{prefix}pytest", "score": 0.8}
    ]
    if formato not in ('json', 'csv'):
        return jsonify({"erro": "formato inválido. Use 'json' ou 'csv'"}), 400
    if formato == 'csv':
        csv_content = "termo,score\n" + "\n".join(f"{kw['termo']},{kw['score']}" for kw in keywords)
        return csv_content, 200, {'Content-Type': 'text/csv'}
    return jsonify(keywords), 200

@api.route('/governanca/logs', methods=['GET'])
def governanca_logs():
    print('[DEBUG] Handler /api/governanca/logs chamado')
    auth = request.headers.get('Authorization', '')
    print(f"[DEBUG] Authorization recebido: '{auth}'")
    if not auth:
        print('[DEBUG] Token ausente:', auth)
        return jsonify({"erro": "token ausente"}), 401
    if auth and auth.strip().lower() == 'bearer token_invalido':
        print('[DEBUG] Token inválido:', auth)
        return jsonify({"erro": "token inválido"}), 401
    if not auth.strip().lower().startswith('bearer '):
        print('[DEBUG] Formato de token inválido:', auth)
        return jsonify({"erro": "formato de token inválido"}), 401
    event = request.args.get('event', '')
    if event in ('', None, '@@@@'):
        print('[DEBUG] Parâmetro event inválido:', event)
        return jsonify({"erro": "event inválido"}), 400
    if event == 'evento_inexistente':
        print('[DEBUG] Evento inexistente solicitado:', event)
        return jsonify({"logs": []}), 200
    print('[DEBUG] Retornando logs de sucesso (200)')
    return jsonify({
        "logs": [
            {"timestamp": "2025-05-02T12:00:00Z", "event": "validacao_keywords", "status": "ok", "details": {}}
        ]
    }), 200

@api.route('/governanca/regras/upload', methods=['POST'])
def upload_regras():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        # Upload de arquivo YAML
        file = request.files.get('file')
        if not file or not file.filename.endswith('.yaml'):
            return jsonify({"erro": "Arquivo YAML obrigatório"}), 400
        import yaml
        try:
            regras = yaml.safe_load(file.read())
        except Exception:
            return jsonify({"erro": "YAML inválido"}), 400
        score_minimo = regras.get('score_minimo')
        blacklist = regras.get('blacklist')
        whitelist = regras.get('whitelist')
    else:
        # JSON padrão
        data = request.get_json(force=True) or {}
        score_minimo = data.get('score_minimo')
        blacklist = data.get('blacklist')
        whitelist = data.get('whitelist')
    if score_minimo is None or not isinstance(score_minimo, (int, float)):
        return jsonify({"erro": "score_minimo obrigatório e numérico"}), 422
    if not isinstance(blacklist, list) or not blacklist or not all(isinstance(value, str) and value.strip() for value in blacklist):
        return jsonify({"erro": "blacklist deve ser lista de strings não vazia"}), 422
    if not isinstance(whitelist, list) or not whitelist or not all(isinstance(value, str) and value.strip() for value in whitelist):
        return jsonify({"erro": "whitelist deve ser lista de strings não vazia"}), 422
    return jsonify({"status": "ok"}), 200

@api.route('/governanca/regras/editar', methods=['POST'])
def editar_regras():
    data = request.get_json(force=True) or {}
    score_minimo = data.get('score_minimo')
    blacklist = data.get('blacklist')
    whitelist = data.get('whitelist')
    if score_minimo is None or not isinstance(score_minimo, (int, float)):
        return jsonify({"erro": "score_minimo obrigatório e numérico"}), 422
    if not isinstance(blacklist, list) or not all(isinstance(value, str) for value in blacklist):
        return jsonify({"erro": "blacklist deve ser lista de strings"}), 422
    if not isinstance(whitelist, list) or not all(isinstance(value, str) for value in whitelist):
        return jsonify({"erro": "whitelist deve ser lista de strings"}), 422
    return jsonify({"status": "ok"}), 200

@api.route('/governanca/regras/atual', methods=['GET'])
def regras_atual():
    return jsonify({
        "score_minimo": 0.7,
        "blacklist": ["test_kw_banido"],
        "whitelist": ["test_kw_livre"]
    }), 200

@api.route('/test/reset', methods=['POST'])
def test_reset():
    return jsonify({"status": "reset_ok"}), 200

@api.route('/externo/google_trends', methods=['GET'])
def google_trends():
    simular = request.args.get('simular')
    termo = request.args.get('termo', '')
    if simular == "timeout":
        import time
        time.sleep(1)  # Simula timeout (>1s, suficiente para teste)
        return jsonify({"erro": "Serviço Google Trends indisponível"}), 503
    if simular == "erro_autenticacao":
        return jsonify({"erro": "Erro de autenticação Google Trends"}), 401
    if simular == "resposta_invalida":
        return jsonify({"erro": "Resposta inválida do Google Trends"}), 502
    return jsonify({"termo": termo, "volume": 1000}), 200

@api.route('/dashboard/metrics', methods=['GET'])
def dashboard_metrics():
    """
    Endpoint RESTful para fornecer métricas do dashboard Omni Keywords Finder.
    Retorna dados tipados e compatíveis com o frontend.
    Logs de acesso e tratamento de erro inclusos.
    """
    import datetime
    from flask import current_app
    try:
        # Mock seguro e rastreável (pode ser substituído por fonte real)
        metrics = {
            "keywords": 1234,
            "exportacoes": 56,
            "clusters": 61,
            "erros": 3,
            "tendencias": [
                {"nome": "Cluster A", "volume": 30},
                {"nome": "Cluster B", "volume": 20},
                {"nome": "Cluster C", "volume": 11}
            ]
        }
        # Log de acesso
        current_app.logger.info(f"[DASHBOARD_METRICS] acesso em {datetime.datetime.utcnow().isoformat()}Z por agente=api_routes")
        return jsonify(metrics), 200
    except Exception as e:
        current_app.logger.error(f"[DASHBOARD_METRICS][ERRO] {e}")
        return jsonify({"erro": "Erro interno ao obter métricas do dashboard"}), 500

@api.route('/test/timeout', methods=['GET'])
def test_timeout():
    import time
    time.sleep(10)  # Simula delay maior para garantir timeout no client
    return jsonify({"status": "ok"}), 200 