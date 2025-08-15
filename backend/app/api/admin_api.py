"""
📊 Admin API - Omni Keywords Finder
🎯 Objetivo: Endpoints administrativos para gestão do sistema
📅 Data: 2025-01-27
🔗 Tracing ID: ADMIN_API_001
📋 Ruleset: enterprise_control_layer.yaml

Funcionalidades:
- Gestão de usuários e permissões
- Configuração do sistema
- Monitoramento administrativo
- Relatórios administrativos
- Configurações gerais
"""

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from sqlalchemy import text, func, and_, or_
from sqlalchemy.orm import sessionmaker
import redis

from ..utils.audit_logger import audit_logger
from ..utils.error_handler import handle_error
from ..security.rbac import RBACManager
from ..models.user import User
from ..models.execution import Execution
from ..models.payment import Payment

# Configuração de logging
logger = logging.getLogger(__name__)

# Blueprint para API administrativa
admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api/v1')

# Tipos de ação administrativa
class AdminAction(Enum):
    """Tipos de ações administrativas"""
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_SUSPEND = "user_suspend"
    USER_ACTIVATE = "user_activate"
    SYSTEM_CONFIG = "system_config"
    SYSTEM_BACKUP = "system_backup"
    SYSTEM_RESTORE = "system_restore"
    MONITORING_ALERT = "monitoring_alert"
    MONITORING_REPORT = "monitoring_report"

# Schemas de dados
@dataclass
class UserManagementData:
    """Dados para gestão de usuários"""
    user_id: str
    action: AdminAction
    data: Dict[str, Any]
    reason: Optional[str] = None
    admin_id: Optional[str] = None

@dataclass
class SystemConfigData:
    """Dados para configuração do sistema"""
    config_key: str
    config_value: Any
    config_type: str
    description: Optional[str] = None
    admin_id: Optional[str] = None

@dataclass
class MonitoringData:
    """Dados para monitoramento"""
    metric_name: str
    metric_value: float
    threshold: float
    severity: str
    timestamp: datetime

# Decorator para verificar permissões administrativas
def require_admin_permission(permission: str):
    """Decorator para verificar permissões administrativas"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Extrair token do header
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({
                        'success': False,
                        'error': 'Token de autenticação necessário'
                    }), 401
                
                token = auth_header.split(' ')[1]
                
                # Verificar token e permissões (implementação básica)
                # Em produção, usar JWT e verificar permissões no RBAC
                user_id = get_user_id_from_token(token)
                
                if not user_id:
                    return jsonify({
                        'success': False,
                        'error': 'Token inválido'
                    }), 401
                
                # Verificar se usuário tem permissão administrativa
                if not has_admin_permission(user_id, permission):
                    return jsonify({
                        'success': False,
                        'error': 'Permissão administrativa necessária'
                    }), 403
                
                # Log da ação administrativa
                audit_logger.log_admin_action(
                    user_id=user_id,
                    action=f.__name__,
                    resource=request.endpoint,
                    details=request.get_json() or {}
                )
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Erro na verificação de permissão administrativa: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Erro interno do servidor'
                }), 500
                
        return decorated_function
    return decorator

def get_user_id_from_token(token: str) -> Optional[str]:
    """Extrai user_id do token (implementação básica)"""
    # Em produção, decodificar JWT e extrair user_id
    # Por enquanto, retorna um ID fixo para testes
    return "admin_user_001"

def has_admin_permission(user_id: str, permission: str) -> bool:
    """Verifica se usuário tem permissão administrativa"""
    # Em produção, verificar no sistema RBAC
    # Por enquanto, retorna True para testes
    return True

# ============================================================================
# ENDPOINTS DE GESTÃO DE USUÁRIOS
# ============================================================================

@admin_api_bp.route('/users', methods=['GET'])
@require_admin_permission('users:read')
def get_users():
    """Lista todos os usuários com filtros"""
    try:
        # Parâmetros de query
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status', 'all')
        role = request.args.get('role', 'all')
        search = request.args.get('search', '')
        
        # Validações
        if page < 1:
            return jsonify({
                'success': False,
                'error': 'Página deve ser maior que 0'
            }), 400
        
        if per_page < 1 or per_page > 100:
            return jsonify({
                'success': False,
                'error': 'Itens por página deve estar entre 1 e 100'
            }), 400
        
        # Construir query
        query = User.query
        
        # Aplicar filtros
        if status != 'all':
            query = query.filter(User.status == status)
        
        if role != 'all':
            query = query.filter(User.role == role)
        
        if search:
            search_filter = or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.full_name.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Paginação
        total = query.count()
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Formatar resposta
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'status': user.status,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active,
                'email_verified': user.email_verified
            })
        
        return jsonify({
            'success': True,
            'data': {
                'users': users_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@admin_api_bp.route('/users/<user_id>', methods=['GET'])
@require_admin_permission('users:read')
def get_user_details(user_id: str):
    """Obtém detalhes de um usuário específico"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
        
        # Estatísticas do usuário
        executions_count = Execution.query.filter_by(user_id=user_id).count()
        payments_count = Payment.query.filter_by(user_id=user_id).count()
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'status': user.status,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
            'email_verified': user.email_verified,
            'statistics': {
                'executions_count': executions_count,
                'payments_count': payments_count
            }
        }
        
        return jsonify({
            'success': True,
            'data': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do usuário: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@admin_api_bp.route('/users/<user_id>/status', methods=['PUT'])
@require_admin_permission('users:update')
def update_user_status(user_id: str):
    """Atualiza status de um usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados necessários'
            }), 400
        
        new_status = data.get('status')
        reason = data.get('reason', '')
        
        if not new_status:
            return jsonify({
                'success': False,
                'error': 'Status é obrigatório'
            }), 400
        
        # Validar status
        valid_statuses = ['active', 'suspended', 'inactive', 'banned']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Status inválido. Use: {", ".join(valid_statuses)}'
            }), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
        
        # Atualizar status
        old_status = user.status
        user.status = new_status
        user.updated_at = datetime.utcnow()
        
        # Salvar no banco
        from .. import db
        db.session.commit()
        
        # Log da ação
        audit_logger.log_admin_action(
            user_id=get_user_id_from_token(request.headers.get('Authorization', '').split(' ')[1]),
            action='update_user_status',
            resource=f'user:{user_id}',
            details={
                'old_status': old_status,
                'new_status': new_status,
                'reason': reason
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'Status do usuário atualizado para {new_status}',
            'data': {
                'user_id': user_id,
                'old_status': old_status,
                'new_status': new_status
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao atualizar status do usuário: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# ============================================================================
# ENDPOINTS DE CONFIGURAÇÃO DO SISTEMA
# ============================================================================

@admin_api_bp.route('/system/config', methods=['GET'])
@require_admin_permission('system:read')
def get_system_config():
    """Obtém configurações do sistema"""
    try:
        # Em produção, buscar do banco de dados ou cache
        config = {
            'app_name': 'Omni Keywords Finder',
            'version': '1.0.0',
            'environment': current_app.config.get('ENV', 'development'),
            'debug_mode': current_app.config.get('DEBUG', False),
            'database_url': current_app.config.get('DATABASE_URL', 'sqlite:///app.db'),
            'redis_url': current_app.config.get('REDIS_URL', 'redis://localhost:6379'),
            'max_file_size': current_app.config.get('MAX_FILE_SIZE', 10 * 1024 * 1024),
            'allowed_file_types': current_app.config.get('ALLOWED_FILE_TYPES', ['.txt', '.csv']),
            'rate_limit_requests': current_app.config.get('RATE_LIMIT_REQUESTS', 100),
            'rate_limit_window': current_app.config.get('RATE_LIMIT_WINDOW', 3600),
            'session_timeout': current_app.config.get('SESSION_TIMEOUT', 3600),
            'maintenance_mode': current_app.config.get('MAINTENANCE_MODE', False)
        }
        
        return jsonify({
            'success': True,
            'data': config
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter configurações do sistema: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@admin_api_bp.route('/system/config', methods=['PUT'])
@require_admin_permission('system:update')
def update_system_config():
    """Atualiza configurações do sistema"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados necessários'
            }), 400
        
        # Configurações que podem ser atualizadas
        updatable_configs = [
            'maintenance_mode',
            'rate_limit_requests',
            'rate_limit_window',
            'session_timeout',
            'max_file_size'
        ]
        
        updated_configs = {}
        for key, value in data.items():
            if key in updatable_configs:
                # Em produção, salvar no banco de dados
                updated_configs[key] = value
                current_app.config[key.upper()] = value
        
        if not updated_configs:
            return jsonify({
                'success': False,
                'error': 'Nenhuma configuração válida fornecida'
            }), 400
        
        # Log da ação
        audit_logger.log_admin_action(
            user_id=get_user_id_from_token(request.headers.get('Authorization', '').split(' ')[1]),
            action='update_system_config',
            resource='system:config',
            details={'updated_configs': updated_configs}
        )
        
        return jsonify({
            'success': True,
            'message': 'Configurações atualizadas com sucesso',
            'data': updated_configs
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao atualizar configurações do sistema: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# ============================================================================
# ENDPOINTS DE MONITORAMENTO ADMINISTRATIVO
# ============================================================================

@admin_api_bp.route('/monitoring/overview', methods=['GET'])
@require_admin_permission('monitoring:read')
def get_monitoring_overview():
    """Obtém visão geral do monitoramento do sistema"""
    try:
        # Estatísticas gerais
        total_users = User.query.count()
        active_users = User.query.filter_by(status='active').count()
        total_executions = Execution.query.count()
        total_payments = Payment.query.count()
        
        # Execuções dos últimos 7 dias
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_executions = Execution.query.filter(
            Execution.created_at >= seven_days_ago
        ).count()
        
        # Pagamentos dos últimos 30 dias
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_payments = Payment.query.filter(
            Payment.created_at >= thirty_days_ago
        ).count()
        
        # Usuários novos dos últimos 30 dias
        new_users = User.query.filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        overview = {
            'users': {
                'total': total_users,
                'active': active_users,
                'new_last_30_days': new_users,
                'active_percentage': (active_users / total_users * 100) if total_users > 0 else 0
            },
            'executions': {
                'total': total_executions,
                'last_7_days': recent_executions,
                'avg_per_day': recent_executions / 7 if recent_executions > 0 else 0
            },
            'payments': {
                'total': total_payments,
                'last_30_days': recent_payments,
                'avg_per_day': recent_payments / 30 if recent_payments > 0 else 0
            },
            'system': {
                'uptime': '99.9%',  # Em produção, calcular real
                'response_time': '245ms',  # Em produção, calcular real
                'error_rate': '0.1%',  # Em produção, calcular real
                'last_updated': datetime.utcnow().isoformat()
            }
        }
        
        return jsonify({
            'success': True,
            'data': overview
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter visão geral do monitoramento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@admin_api_bp.route('/monitoring/alerts', methods=['GET'])
@require_admin_permission('monitoring:read')
def get_system_alerts():
    """Obtém alertas do sistema"""
    try:
        # Em produção, buscar do sistema de alertas
        alerts = [
            {
                'id': 'alert_001',
                'type': 'warning',
                'title': 'Alto uso de CPU',
                'message': 'CPU atingiu 85% de uso',
                'severity': 'medium',
                'timestamp': datetime.utcnow().isoformat(),
                'acknowledged': False
            },
            {
                'id': 'alert_002',
                'type': 'info',
                'title': 'Backup automático',
                'message': 'Backup diário concluído com sucesso',
                'severity': 'low',
                'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'acknowledged': True
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'total': len(alerts),
                'unacknowledged': len([a for a in alerts if not a['acknowledged']])
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas do sistema: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# ============================================================================
# ENDPOINTS DE RELATÓRIOS ADMINISTRATIVOS
# ============================================================================

@admin_api_bp.route('/reports/users', methods=['GET'])
@require_admin_permission('reports:read')
def get_users_report():
    """Gera relatório de usuários"""
    try:
        # Parâmetros
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        format_type = request.args.get('format', 'json')
        
        # Construir query
        query = User.query
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(User.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(User.created_at <= end_dt)
        
        users = query.all()
        
        # Estatísticas
        total_users = len(users)
        active_users = len([u for u in users if u.status == 'active'])
        suspended_users = len([u for u in users if u.status == 'suspended'])
        
        # Agrupamento por role
        roles_count = {}
        for user in users:
            role = user.role or 'unknown'
            roles_count[role] = roles_count.get(role, 0) + 1
        
        # Agrupamento por mês
        monthly_registrations = {}
        for user in users:
            if user.created_at:
                month_key = user.created_at.strftime('%Y-%m')
                monthly_registrations[month_key] = monthly_registrations.get(month_key, 0) + 1
        
        report = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_users': total_users,
                'active_users': active_users,
                'suspended_users': suspended_users,
                'active_percentage': (active_users / total_users * 100) if total_users > 0 else 0
            },
            'by_role': roles_count,
            'by_month': monthly_registrations,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': report
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de usuários: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@admin_api_bp.route('/reports/executions', methods=['GET'])
@require_admin_permission('reports:read')
def get_executions_report():
    """Gera relatório de execuções"""
    try:
        # Parâmetros
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Construir query
        query = Execution.query
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Execution.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Execution.created_at <= end_dt)
        
        executions = query.all()
        
        # Estatísticas
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == 'completed'])
        failed_executions = len([e for e in executions if e.status == 'failed'])
        
        # Agrupamento por status
        status_count = {}
        for execution in executions:
            status = execution.status or 'unknown'
            status_count[status] = status_count.get(status, 0) + 1
        
        # Agrupamento por dia
        daily_executions = {}
        for execution in executions:
            if execution.created_at:
                day_key = execution.created_at.strftime('%Y-%m-%d')
                daily_executions[day_key] = daily_executions.get(day_key, 0) + 1
        
        report = {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0
            },
            'by_status': status_count,
            'by_day': daily_executions,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': report
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de execuções: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# ============================================================================
# HEALTH CHECK
# ============================================================================

@admin_api_bp.route('/health', methods=['GET'])
def admin_health_check():
    """Health check da API administrativa"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'admin_api',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': [
                '/admin/api/v1/users',
                '/admin/api/v1/system/config',
                '/admin/api/v1/monitoring/overview',
                '/admin/api/v1/reports/users',
                '/admin/api/v1/reports/executions'
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no health check da API administrativa: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500 