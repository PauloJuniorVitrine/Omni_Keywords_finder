"""
API Routes para Sistema de Alertas Inteligentes
Integração com sistema principal Omni Keywords Finder

Prompt: Implementação de sistema de alertas inteligentes
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Tracing ID: ALERTS_API_ROUTES_20250127_001
"""

from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import json
from dataclasses import asdict

# Importar módulos do sistema de alertas existente
from ..monitoring.alerting_system import AlertingSystem
from ..monitoring.alert_optimizer import AlertOptimizer
from ..utils.response_utils import create_response, create_error_response
from ..utils.validation_utils import validate_request_data
from ..utils.auth_utils import require_auth

# Configurar logging
logger = logging.getLogger(__name__)

# Criar blueprint para alertas
alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')

# Instâncias dos sistemas
alerting_system = AlertingSystem()
alert_optimizer = AlertOptimizer()

@alerts_bp.route('/dashboard', methods=['GET'])
@cross_origin()
@require_auth
def get_alerts_dashboard():
    """
    Endpoint para obter dados do dashboard de alertas inteligentes
    """
    try:
        # Parâmetros de query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        severity = request.args.getlist('severity')
        source = request.args.getlist('source')
        status = request.args.getlist('status')
        alert_type = request.args.getlist('type')
        user_impact = request.args.get('user_impact', type=lambda v: v.lower() == 'true' if v else None)
        
        # Obter alertas do sistema
        alerts = alerting_system.get_alerts(
            page=page,
            per_page=per_page,
            severity=severity if severity else None,
            source=source if source else None,
            status=status if status else None,
            alert_type=alert_type if alert_type else None,
            user_impact=user_impact
        )
        
        # Obter estatísticas
        statistics = alerting_system.get_statistics()
        
        # Obter grupos de alertas
        groups = alert_optimizer.get_alert_groups()
        
        # Calcular métricas de redução
        total_alerts = statistics.get('total_alerts', 0)
        suppressed_alerts = statistics.get('suppressed_alerts', 0)
        grouped_alerts = statistics.get('grouped_alerts', 0)
        
        reduction_percentage = 0
        if total_alerts > 0:
            reduction_percentage = ((suppressed_alerts + grouped_alerts) / total_alerts) * 100
        
        # Preparar resposta
        dashboard_data = {
            'alerts': [asdict(alert) for alert in alerts['items']],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': alerts['total'],
                'pages': alerts['pages']
            },
            'statistics': {
                'total_alerts': total_alerts,
                'active_alerts': statistics.get('active_alerts', 0),
                'suppressed_alerts': suppressed_alerts,
                'grouped_alerts': grouped_alerts,
                'resolved_alerts': statistics.get('resolved_alerts', 0),
                'reduction_percentage': round(reduction_percentage, 1),
                'average_response_time': statistics.get('average_response_time', 0),
                'top_sources': statistics.get('top_sources', []),
                'severity_distribution': statistics.get('severity_distribution', [])
            },
            'groups': [asdict(group) for group in groups],
            'filters': {
                'severity': severity,
                'source': source,
                'status': status,
                'type': alert_type,
                'user_impact': user_impact
            }
        }
        
        logger.info(f"Dashboard de alertas carregado - {len(alerts['items'])} alertas, {len(groups)} grupos")
        
        return create_response(
            success=True,
            data=dashboard_data,
            message="Dashboard de alertas carregado com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard de alertas: {str(e)}")
        return create_error_response(
            message="Erro ao carregar dashboard de alertas",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/alerts', methods=['GET'])
@cross_origin()
@require_auth
def get_alerts():
    """
    Endpoint para listar alertas com filtros
    """
    try:
        # Parâmetros de query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        severity = request.args.getlist('severity')
        source = request.args.getlist('source')
        status = request.args.getlist('status')
        alert_type = request.args.getlist('type')
        user_impact = request.args.get('user_impact', type=lambda v: v.lower() == 'true' if v else None)
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Obter alertas
        alerts = alerting_system.get_alerts(
            page=page,
            per_page=per_page,
            severity=severity if severity else None,
            source=source if source else None,
            status=status if status else None,
            alert_type=alert_type if alert_type else None,
            user_impact=user_impact,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return create_response(
            success=True,
            data={
                'alerts': [asdict(alert) for alert in alerts['items']],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': alerts['total'],
                    'pages': alerts['pages']
                }
            },
            message=f"{len(alerts['items'])} alertas encontrados"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar alertas: {str(e)}")
        return create_error_response(
            message="Erro ao listar alertas",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/alerts/<alert_id>', methods=['GET'])
@cross_origin()
@require_auth
def get_alert_details(alert_id: str):
    """
    Endpoint para obter detalhes de um alerta específico
    """
    try:
        alert = alerting_system.get_alert_by_id(alert_id)
        
        if not alert:
            return create_error_response(
                message="Alerta não encontrado",
                status_code=404
            )
        
        return create_response(
            success=True,
            data=asdict(alert),
            message="Detalhes do alerta carregados com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do alerta {alert_id}: {str(e)}")
        return create_error_response(
            message="Erro ao obter detalhes do alerta",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
@cross_origin()
@require_auth
def acknowledge_alert(alert_id: str):
    """
    Endpoint para reconhecer um alerta
    """
    try:
        # Obter dados do request
        data = request.get_json() or {}
        user_id = data.get('user_id', 'system')
        comment = data.get('comment', '')
        
        # Reconhecer alerta
        success = alerting_system.acknowledge_alert(
            alert_id=alert_id,
            user_id=user_id,
            comment=comment
        )
        
        if not success:
            return create_error_response(
                message="Erro ao reconhecer alerta",
                status_code=400
            )
        
        logger.info(f"Alerta {alert_id} reconhecido por {user_id}")
        
        return create_response(
            success=True,
            message="Alerta reconhecido com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao reconhecer alerta {alert_id}: {str(e)}")
        return create_error_response(
            message="Erro ao reconhecer alerta",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/alerts/<alert_id>/resolve', methods=['POST'])
@cross_origin()
@require_auth
def resolve_alert(alert_id: str):
    """
    Endpoint para resolver um alerta
    """
    try:
        # Obter dados do request
        data = request.get_json() or {}
        user_id = data.get('user_id', 'system')
        resolution_notes = data.get('resolution_notes', '')
        
        # Resolver alerta
        success = alerting_system.resolve_alert(
            alert_id=alert_id,
            user_id=user_id,
            resolution_notes=resolution_notes
        )
        
        if not success:
            return create_error_response(
                message="Erro ao resolver alerta",
                status_code=400
            )
        
        logger.info(f"Alerta {alert_id} resolvido por {user_id}")
        
        return create_response(
            success=True,
            message="Alerta resolvido com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao resolver alerta {alert_id}: {str(e)}")
        return create_error_response(
            message="Erro ao resolver alerta",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/groups', methods=['GET'])
@cross_origin()
@require_auth
def get_alert_groups():
    """
    Endpoint para listar grupos de alertas
    """
    try:
        # Parâmetros de query
        active_only = request.args.get('active_only', 'true', type=lambda v: v.lower() == 'true')
        
        # Obter grupos
        groups = alert_optimizer.get_alert_groups(active_only=active_only)
        
        return create_response(
            success=True,
            data=[asdict(group) for group in groups],
            message=f"{len(groups)} grupos de alertas encontrados"
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar grupos de alertas: {str(e)}")
        return create_error_response(
            message="Erro ao listar grupos de alertas",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/groups/<group_id>', methods=['GET'])
@cross_origin()
@require_auth
def get_group_details(group_id: str):
    """
    Endpoint para obter detalhes de um grupo específico
    """
    try:
        group = alert_optimizer.get_group_by_id(group_id)
        
        if not group:
            return create_error_response(
                message="Grupo não encontrado",
                status_code=404
            )
        
        return create_response(
            success=True,
            data=asdict(group),
            message="Detalhes do grupo carregados com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do grupo {group_id}: {str(e)}")
        return create_error_response(
            message="Erro ao obter detalhes do grupo",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/optimization/config', methods=['GET'])
@cross_origin()
@require_auth
def get_optimization_config():
    """
    Endpoint para obter configurações de otimização
    """
    try:
        config = alert_optimizer.get_config()
        
        return create_response(
            success=True,
            data=config,
            message="Configurações de otimização carregadas com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao carregar configurações de otimização: {str(e)}")
        return create_error_response(
            message="Erro ao carregar configurações de otimização",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/optimization/config', methods=['PUT'])
@cross_origin()
@require_auth
def update_optimization_config():
    """
    Endpoint para atualizar configurações de otimização
    """
    try:
        # Validar dados de entrada
        data = request.get_json()
        if not data:
            return create_error_response(
                message="Dados de configuração não fornecidos",
                status_code=400
            )
        
        # Validar campos obrigatórios
        required_fields = ['enabled', 'grouping_window_minutes', 'suppression_threshold']
        for field in required_fields:
            if field not in data:
                return create_error_response(
                    message=f"Campo obrigatório não fornecido: {field}",
                    status_code=400
                )
        
        # Atualizar configuração
        success = alert_optimizer.update_config(
            enabled=data['enabled'],
            grouping_window_minutes=data['grouping_window_minutes'],
            suppression_threshold=data['suppression_threshold'],
            max_alerts_per_group=data.get('max_alerts_per_group', 10),
            pattern_detection_window=data.get('pattern_detection_window', 60)
        )
        
        if not success:
            return create_error_response(
                message="Erro ao atualizar configurações",
                status_code=400
            )
        
        logger.info("Configurações de otimização atualizadas")
        
        return create_response(
            success=True,
            message="Configurações de otimização atualizadas com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao atualizar configurações de otimização: {str(e)}")
        return create_error_response(
            message="Erro ao atualizar configurações de otimização",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/optimization/run', methods=['POST'])
@cross_origin()
@require_auth
def run_optimization():
    """
    Endpoint para executar otimização manual
    """
    try:
        # Executar otimização
        result = alert_optimizer.run_optimization()
        
        return create_response(
            success=True,
            data=result,
            message="Otimização executada com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao executar otimização: {str(e)}")
        return create_error_response(
            message="Erro ao executar otimização",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/statistics', methods=['GET'])
@cross_origin()
@require_auth
def get_alert_statistics():
    """
    Endpoint para obter estatísticas detalhadas
    """
    try:
        # Parâmetros de query
        time_range = request.args.get('time_range', '24h')  # 1h, 24h, 7d, 30d
        
        # Obter estatísticas
        statistics = alerting_system.get_statistics(time_range=time_range)
        
        return create_response(
            success=True,
            data=statistics,
            message="Estatísticas carregadas com sucesso"
        )
        
    except Exception as e:
        logger.error(f"Erro ao carregar estatísticas: {str(e)}")
        return create_error_response(
            message="Erro ao carregar estatísticas",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/export', methods=['POST'])
@cross_origin()
@require_auth
def export_alerts():
    """
    Endpoint para exportar alertas
    """
    try:
        # Obter dados do request
        data = request.get_json() or {}
        format_type = data.get('format', 'json')  # json, csv, excel
        filters = data.get('filters', {})
        
        # Exportar alertas
        export_data = alerting_system.export_alerts(
            format_type=format_type,
            filters=filters
        )
        
        return create_response(
            success=True,
            data=export_data,
            message=f"Alertas exportados em formato {format_type}"
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar alertas: {str(e)}")
        return create_error_response(
            message="Erro ao exportar alertas",
            error=str(e),
            status_code=500
        )

@alerts_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """
    Endpoint de health check para o sistema de alertas
    """
    try:
        # Verificar status dos sistemas
        alerting_status = alerting_system.get_status()
        optimizer_status = alert_optimizer.get_status()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'systems': {
                'alerting_system': alerting_status,
                'alert_optimizer': optimizer_status
            }
        }
        
        return create_response(
            success=True,
            data=health_data,
            message="Sistema de alertas funcionando normalmente"
        )
        
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return create_error_response(
            message="Erro no sistema de alertas",
            error=str(e),
            status_code=500
        )

# Registrar blueprint no app principal
def init_alerts_routes(app):
    """
    Inicializar rotas de alertas no app Flask
    """
    app.register_blueprint(alerts_bp)
    logger.info("Rotas de alertas registradas com sucesso") 