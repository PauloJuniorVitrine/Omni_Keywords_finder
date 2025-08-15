from flask import Flask, jsonify
from flask_cors import CORS
from backend.app.config import Config
from backend.app.models import db, Nicho, Categoria, Execucao, Log
from backend.app.utils.log_event import log_event
from backend.app.api.execucoes_agendadas import execucoes_agendadas_bp
from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.api.auth import auth_bp, init_jwt
from backend.app.api.rbac import rbac_bp
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import json
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram

# Importar sistema de auditoria
import sys
from typing import Dict, List, Optional, Any
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from infrastructure.security.audit_middleware import FlaskAuditMiddleware
from infrastructure.security.advanced_audit import AdvancedAuditSystem

# Importar sistema de rate limiting
from infrastructure.security.rate_limiting_middleware import configure_flask_rate_limiting
from infrastructure.security.rate_limiting import RateLimitConfig, RateLimitStrategy

# 🎯 FASE 4 - INTEGRAÇÃO COM OBSERVABILIDADE AVANÇADA
# Importar sistema de observabilidade
from infrastructure.observability.advanced_tracing import AdvancedTracing
from infrastructure.observability.trace_context import TraceContext
from infrastructure.observability.trace_decorator import trace_function
from infrastructure.observability.trace_config import TraceConfig
from infrastructure.observability.anomaly_detection import AnomalyDetector
from infrastructure.observability.anomaly_alerting import AnomalyAlerting
from infrastructure.observability.anomaly_config import AnomalyConfig
from infrastructure.observability.predictive_monitoring import PredictiveMonitor
from infrastructure.observability.prediction_models import PredictionModels
from infrastructure.observability.prediction_alerting import PredictionAlerting
from infrastructure.observability.prediction_config import PredictionConfig

# Inicialização do app Flask
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# 🎯 FASE 4 - INICIALIZAÇÃO DO SISTEMA DE OBSERVABILIDADE
def initialize_observability_system():
    """
    Inicializa o sistema completo de observabilidade da Fase 4
    """
    try:
        # Configuração de tracing
        trace_config = TraceConfig(
            service_name="omni-keywords-finder-backend",
            environment=os.getenv('FLASK_ENV', 'development'),
            sampling_rate=0.1,
            backends=['jaeger', 'zipkin'],
            enable_auto_instrumentation=True
        )
        
        # Inicializar distributed tracing
        tracing = AdvancedTracing(trace_config)
        tracing.initialize()
        
        # Inicializar contexto de trace
        trace_context = TraceContext()
        trace_context.initialize()
        
        # Configuração de detecção de anomalias
        anomaly_config = AnomalyConfig(
            algorithms=['statistical', 'iqr', 'mad', 'exponential_smoothing'],
            metrics=['response_time', 'error_rate', 'throughput', 'memory_usage'],
            alert_channels=['email', 'slack', 'webhook'],
            cooldown_period=300,
            suppression_enabled=True
        )
        
        # Inicializar detecção de anomalias
        anomaly_detection = AnomalyDetection(anomaly_config)
        anomaly_detection.initialize()
        
        # Inicializar sistema de alertas para anomalias
        anomaly_alerting = AnomalyAlerting(anomaly_config)
        anomaly_alerting.initialize()
        
        # Configuração de monitoramento preditivo
        prediction_config = PredictionConfig(
            models=['linear_regression', 'random_forest', 'lstm'],
            metrics=['response_time', 'error_rate', 'throughput'],
            prediction_horizon=3600,
            confidence_threshold=0.8,
            alert_channels=['email', 'slack', 'webhook']
        )
        
        # Inicializar monitoramento preditivo
        predictive_monitoring = PredictiveMonitoring(prediction_config)
        predictive_monitoring.initialize()
        
        # Inicializar modelos preditivos
        prediction_models = PredictionModels(prediction_config)
        prediction_models.initialize()
        
        # Inicializar sistema de alertas preditivos
        prediction_alerting = PredictionAlerting(prediction_config)
        prediction_alerting.initialize()
        
        log_event("INFO", "observability", "Sistema de observabilidade Fase 4 inicializado com sucesso")
        return True
        
    except Exception as e:
        log_event("ERROR", "observability", f"Erro ao inicializar observabilidade: {str(e)}")
        return False

# Configuração CORS segura por ambiente
def get_cors_origins():
    """Retorna origens CORS baseadas no ambiente"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        # Em produção, apenas origens específicas
        return [
            'https://omni-keywords-finder.com',
            'https://www.omni-keywords-finder.com',
            'https://app.omni-keywords-finder.com'
        ]
    elif env == 'staging':
        # Em staging, origens de teste
        return [
            'https://staging.omni-keywords-finder.com',
            'https://test.omni-keywords-finder.com'
        ]
    else:
        # Em desenvolvimento, localhost
        return [
            'http://localhost:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3000',
            'http://127.0.0.1:3001'
        ]

# Aplicar CORS com configuração segura
CORS(app, 
     origins=get_cors_origins(),
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=[
         'Content-Type', 
         'Authorization', 
         'X-Requested-With',
         'X-API-Key',
         'X-Client-Version',
         'X-Request-ID',
         'traceparent',  # 🎯 FASE 4 - Headers de tracing
         'tracestate'
     ],
     expose_headers=[
         'X-Request-ID',
         'X-Rate-Limit-Remaining',
         'X-Rate-Limit-Reset',
         'traceparent',  # 🎯 FASE 4 - Headers de tracing
         'tracestate'
     ],
     supports_credentials=True,
     max_age=3600)

# Configuração de Rate Limiting Uniforme
def get_rate_limit_config():
    """Retorna configuração de rate limiting baseada no ambiente"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        # Em produção, limites mais restritivos
        return RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_limit=10,
            window_size=60,
            cooldown_period=300,
            adaptive_enabled=True,
            learning_period=3600,
            anomaly_threshold=2.0,
            whitelist_ips=[],
            blacklist_ips=[],
            alert_threshold=100,
            alert_cooldown=3600
        )
    elif env == 'staging':
        # Em staging, limites moderados
        return RateLimitConfig(
            requests_per_minute=120,
            requests_per_hour=2000,
            requests_per_day=20000,
            burst_limit=20,
            window_size=60,
            cooldown_period=300,
            adaptive_enabled=True,
            learning_period=3600,
            anomaly_threshold=2.5,
            whitelist_ips=[],
            blacklist_ips=[],
            alert_threshold=200,
            alert_cooldown=3600
        )
    else:
        # Em desenvolvimento, limites mais permissivos
        return RateLimitConfig(
            requests_per_minute=300,
            requests_per_hour=5000,
            requests_per_day=50000,
            burst_limit=50,
            window_size=60,
            cooldown_period=300,
            adaptive_enabled=False,
            learning_period=3600,
            anomaly_threshold=3.0,
            whitelist_ips=[],
            blacklist_ips=[],
            alert_threshold=500,
            alert_cooldown=3600
        )

# Aplicar Rate Limiting Uniforme
rate_limit_config = get_rate_limit_config()
rate_limit_middleware = configure_flask_rate_limiting(app, rate_limit_config)

# 🎯 FASE 4 - INICIALIZAR SISTEMA DE OBSERVABILIDADE
observability_initialized = initialize_observability_system()
if not observability_initialized:
    log_event("WARNING", "observability", "Sistema de observabilidade não inicializado - continuando sem observabilidade")

# Inicializar sistema de auditoria
audit_system = AdvancedAuditSystem()
audit_middleware = FlaskAuditMiddleware(app, audit_system)

# Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Omni Keywords Finder backend', version='1.0.0')

# Métricas customizadas
lote_exec_counter = Counter('lote_execucoes_total', 'Total de execuções de lotes')
lote_exec_error_counter = Counter('lote_execucoes_erro_total', 'Total de erros em execuções de lotes')
lote_exec_duration = Histogram('lote_execucoes_duracao_segundos', 'Duração das execuções de lotes')
agendada_exec_counter = Counter('agendada_execucoes_total', 'Total de execuções agendadas')
agendada_exec_error_counter = Counter('agendada_execucoes_erro_total', 'Total de erros em execuções agendadas')
agendada_exec_duration = Histogram('agendada_execucoes_duracao_segundos', 'Duração das execuções agendadas')

# Métricas de rate limiting
rate_limit_counter = Counter('rate_limit_hits_total', 'Total de hits no rate limit', ['endpoint', 'ip'])
rate_limit_exceeded_counter = Counter('rate_limit_exceeded_total', 'Total de rate limits excedidos', ['endpoint', 'ip'])

# Importação dos blueprints
from backend.app.api.nichos import nichos_bp
from backend.app.api.categorias import categorias_bp
from backend.app.api.execucoes import execucoes_bp
from backend.app.api.logs import logs_bp
from backend.app.api.notificacoes import notificacoes_bp
from backend.app.api.clusters import clusters_bp
from backend.app.api.auditoria import auditoria_bp
from backend.app.api.openapi import openapi_bp
from backend.app.api.business_metrics import business_metrics_bp

# Configuração do Swagger UI
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Omni Keywords Finder API",
        'deepLinking': True,
        'displayOperationId': True,
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'docExpansion': 'list',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'syntaxHighlight.theme': 'monokai',
        'tryItOutEnabled': True,
        'requestInterceptor': 'function(request) { console.log("Request:", request); return request; }',
        'responseInterceptor': 'function(response) { console.log("Response:", response); return response; }'
    }
)

app.register_blueprint(nichos_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(execucoes_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(notificacoes_bp)
app.register_blueprint(business_metrics_bp)
app.register_blueprint(execucoes_agendadas_bp)
app.register_blueprint(clusters_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(rbac_bp)
app.register_blueprint(auditoria_bp)
app.register_blueprint(openapi_bp)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Inicialização do APScheduler
scheduler = BackgroundScheduler()

def processar_execucoes_agendadas_job():
    from backend.app.services.execucao_service import processar_execucoes_agendadas
    processar_execucoes_agendadas()

scheduler.add_job(processar_execucoes_agendadas_job, 'interval', seconds=30)
scheduler.start()

@app.route('/')
@trace_function(operation_name="health_check", service_name="omni-keywords-finder-backend")
def health():
    return {'status': 'ok'}

@app.errorhandler(400)
@trace_function(operation_name="bad_request_handler", service_name="omni-keywords-finder-backend")
def bad_request(e):
    log_event('erro', 'Global', detalhes=f'400 Bad Request: {str(e)}')
    return jsonify({'erro': 'Requisição inválida', 'detalhes': str(e)}), 400

@app.errorhandler(404)
def page_not_found(e):
    log_event('erro', 'Global', detalhes=f'404 Not Found: {str(e)}')
    return jsonify({'erro': 'Recurso não encontrado'}), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handler para erro 429 (Rate Limit Exceeded)"""
    from flask import request
    log_event('erro', 'Rate Limiting', detalhes=f'429 Rate Limit Exceeded: {request.remote_addr}')
    
    # Registrar métrica
    rate_limit_exceeded_counter.labels(
        endpoint=request.endpoint or request.path,
        ip=request.remote_addr
    ).inc()
    
    return jsonify({
        'erro': 'Rate limit excedido',
        'mensagem': 'Muitas requisições. Tente novamente mais tarde.',
        'retry_after': 60
    }), 429

@app.errorhandler(500)
@trace_function(operation_name="internal_server_error_handler", service_name="omni-keywords-finder-backend")
def internal_server_error(e):
    log_event('erro', 'Global', detalhes=f'500 Internal Server Error: {str(e)}')
    return jsonify({'erro': 'Erro interno do servidor'}), 500

init_jwt(app)

if __name__ == '__main__':
    app.run(debug=True) 