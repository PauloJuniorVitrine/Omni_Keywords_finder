from typing import Dict, List, Optional, Any
"""
Aplicação principal do sistema de geração de clusters e conteúdo SEO.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, get_flashed_messages, session, send_from_directory, make_response
from pathlib import Path
from shared.config import FlaskConfig, TEMPLATES_DIR, STATIC_DIR
from shared.logger import logger
import json
import re
from infrastructure.persistencia.blogs import salvar_blog, carregar_blogs
from flask_babel import Babel, _
from app.api.api_routes import api

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR)
)

# Carrega configurações
app.config.from_object(FlaskConfig)
app.config['BABEL_DEFAULT_LOCALE'] = 'pt'
babel = Babel(app)

# Cria diretório de uploads se não existir
Path(app.config["UPLOAD_FOLDER"]).mkdir(exist_ok=True)

CONFIG_PATH = Path("shared/config_ia.json")

app.register_blueprint(api)

@app.route("/")
def index():
    """Página inicial."""
    logger.info(
        "Acesso à página inicial",
        {
            "event": "page_view",
            "source": "main.index",
            "details": {"page": "index"}
        }
    )
    return render_template("index.html")

@app.route("/command/cadastro_blog", methods=["POST"])
def command_cadastro_blog():
    return cadastro_blog()

@app.route("/cadastro_blog", methods=["GET", "POST"])
def cadastro_blog_route():
    if request.method == "POST":
        return redirect("/command/cadastro_blog", code=307)
    return cadastro_blog()

@app.route("/configuracoes", methods=["GET", "POST"])
def configuracoes():
    feedback = None
    feedback_status = None
    config_data = {"api_key": "", "modelo": "deepseek", "fallback": False}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            pass
    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        modelo = request.form.get("modelo", "deepseek")
        fallback = bool(request.form.get("fallback"))
        if not api_key or not modelo:
            logger.warning(
                "Configuração inválida",
                {
                    "event": "configuracoes_invalido",
                    "source": "main.configuracoes",
                    "details": {"api_key": bool(api_key), "modelo": modelo}
                }
            )
            return render_template("configuracoes.html", feedback="Preencha todos os campos obrigatórios.", feedback_status="erro", **config_data)
        config_data = {"api_key": api_key, "modelo": modelo, "fallback": fallback}
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            logger.info(
                "Configurações salvas",
                {
                    "event": "configuracoes_salvas",
                    "source": "main.configuracoes",
                    "details": {"modelo": modelo, "fallback": fallback}
                }
            )
            feedback = "Configurações salvas com sucesso!"
            feedback_status = "sucesso"
        except Exception as e:
            logger.error(
                "Erro ao salvar configurações",
                {
                    "event": "configuracoes_erro",
                    "source": "main.configuracoes",
                    "error": str(e)
                }
            )
            feedback = "Erro ao salvar configurações. Tente novamente."
            feedback_status = "erro"
    return render_template("configuracoes.html", feedback=feedback, feedback_status=feedback_status, **config_data)

@app.route("/command/executar_busca", methods=["POST"])
def command_executar_busca():
    return executar_busca()

@app.route("/executar_busca", methods=["GET", "POST"])
def executar_busca_route():
    if request.method == "POST":
        return redirect("/command/executar_busca", code=307)
    return executar_busca()

@app.route("/query/blog_categorias")
def query_blog_categorias():
    return api_blog_categorias()

@app.route("/api/blog_categorias")
def api_blog_categorias_route():
    return redirect("/query/blog_categorias")

@app.route("/query/execucao_status")
def query_execucao_status():
    return api_execucao_status()

@app.route("/api/execucao_status")
def api_execucao_status_route():
    return redirect("/query/execucao_status")

@app.route("/command/executar_lote", methods=["POST"])
def command_executar_lote():
    return executar_lote()

@app.route("/executar_lote", methods=["GET", "POST"])
def executar_lote_route():
    if request.method == "POST":
        return redirect("/command/executar_lote", code=307)
    return executar_lote()

@app.route("/query/lote_status")
def query_lote_status():
    return api_lote_status()

@app.route("/api/lote_status")
def api_lote_status_route():
    return redirect("/query/lote_status")

@app.route("/query/painel")
def query_painel():
    return api_painel()

@app.route("/api/painel")
def api_painel_route():
    return redirect("/query/painel")

@app.route("/health")
def health_check():
    """Endpoint de verificação de saúde da aplicação."""
    return jsonify({"status": "healthy"})

@app.errorhandler(404)
def page_not_found(e):
    print('[DEBUG] Handler 404 acionado para:', request.path)
    logger.warning(
        "Página não encontrada",
        {
            "event": "page_not_found",
            "source": "main.page_not_found",
            "details": {"path": request.path}
        }
    )
    if request.path.startswith("/api/"):
        print('[DEBUG] Handler 404 retornando JSON para rota /api/')
        return make_response(jsonify({"erro": "endpoint não encontrado"}), 404)
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    print('[DEBUG] Handler 500 acionado para:', request.path)
    logger.error(
        "Erro interno do servidor",
        {
            "event": "server_error",
            "source": "main.internal_server_error",
            "error": str(e)
        }
    )
    if request.path.startswith("/api/"):
        print('[DEBUG] Handler 500 retornando JSON para rota /api/')
        return make_response(jsonify({"erro": "erro interno do servidor"}), 500)
    return render_template("500.html"), 500

def create_app():
    """
    Cria e configura a aplicação Flask para uso programático (testes, scripts, etc).
    """
    from flask import Flask
    from shared.config import FlaskConfig, TEMPLATES_DIR, STATIC_DIR
    from flask_babel import Babel
    from app.api.api_routes import api
    import pathlib
    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_DIR),
        static_folder=str(STATIC_DIR)
    )
    app.config.from_object(FlaskConfig)
    app.config['BABEL_DEFAULT_LOCALE'] = 'pt'
    Babel(app)
    pathlib.Path(app.config["UPLOAD_FOLDER"]).mkdir(exist_ok=True)
    app.register_blueprint(api)
    return app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 