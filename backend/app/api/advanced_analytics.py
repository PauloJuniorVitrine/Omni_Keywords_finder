"""
API para Analytics Avançado - Omni Keywords Finder

Endpoints para análise avançada de performance, eficiência de clusters,
comportamento do usuário e insights preditivos usando Machine Learning.

Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 15
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19

Funcionalidades:
- Métricas de performance de keywords
- Análise de eficiência de clusters
- Análise de comportamento do usuário
- Insights preditivos com ML
- Exportação de dados
- Personalização de dashboards
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import uuid
import pandas as pd
import numpy as np
from functools import wraps
import io
import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# Importar sistema de analytics
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from infrastructure.analytics.advanced_analytics_system import (
    AdvancedAnalyticsSystem,
    KeywordPerformance,
    ClusterEfficiency,
    UserBehavior,
    PredictiveInsight,
    AnalyticsData,
    create_analytics_system
)

# Blueprint para analytics avançado
advanced_analytics_bp = Blueprint('advanced_analytics', __name__, url_prefix='/api/v1/analytics')

# Sistema de analytics global
analytics_system = None

def get_analytics_system() -> AdvancedAnalyticsSystem:
    """Obtém instância do sistema de analytics"""
    global analytics_system
    if analytics_system is None:
        analytics_system = create_analytics_system()
    return analytics_system

def require_auth(f):
    """Decorator para autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implementar autenticação real aqui
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Token de autenticação necessário'}), 401
        
        # Validação básica - em produção usar JWT ou similar
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def get_user_id_from_request() -> str:
    """Extrai user_id do request"""
    # Em produção, extrair do token JWT
    return request.headers.get('X-User-ID', 'anonymous')

def validate_time_range(time_range: str) -> bool:
    """Valida o range de tempo"""
    valid_ranges = ['1d', '7d', '30d', '90d']
    return time_range in valid_ranges

def validate_export_format(format_type: str) -> bool:
    """Valida o formato de exportação"""
    valid_formats = ['csv', 'json', 'pdf', 'excel']
    return format_type in valid_formats

# Endpoint principal para analytics avançado
@advanced_analytics_bp.route('/advanced', methods=['GET'])
@require_auth
def get_advanced_analytics():
    """Obtém dados de analytics avançado"""
    try:
        # Parâmetros de query
        time_range = request.args.get('timeRange', '7d')
        category = request.args.get('category', 'all')
        nicho = request.args.get('nicho', 'all')
        
        # Validação de parâmetros
        if not validate_time_range(time_range):
            return jsonify({
                'success': False,
                'error': 'Range de tempo inválido. Use: 1d, 7d, 30d, 90d'
            }), 400
        
        # Obter sistema de analytics
        system = get_analytics_system()
        
        # Buscar dados
        analytics_data = system.get_analytics_data(
            time_range=time_range,
            category=category,
            nicho=nicho
        )
        
        if analytics_data:
            return jsonify({
                'success': True,
                'data': analytics_data.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Nenhum dado encontrado para os filtros especificados'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Erro ao obter analytics avançado: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para métricas de performance de keywords
@advanced_analytics_bp.route('/keywords/performance', methods=['GET'])
@require_auth
def get_keywords_performance():
    """Obtém métricas de performance de keywords"""
    try:
        time_range = request.args.get('timeRange', '7d')
        category = request.args.get('category', 'all')
        nicho = request.args.get('nicho', 'all')
        limit = int(request.args.get('limit', 100))
        
        if not validate_time_range(time_range):
            return jsonify({
                'success': False,
                'error': 'Range de tempo inválido'
            }), 400
        
        system = get_analytics_system()
        performance_data = system.get_keywords_performance(
            time_range=time_range,
            category=category,
            nicho=nicho,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in performance_data]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter performance de keywords: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para eficiência de clusters
@advanced_analytics_bp.route('/clusters/efficiency', methods=['GET'])
@require_auth
def get_clusters_efficiency():
    """Obtém métricas de eficiência de clusters"""
    try:
        time_range = request.args.get('timeRange', '7d')
        category = request.args.get('category', 'all')
        nicho = request.args.get('nicho', 'all')
        limit = int(request.args.get('limit', 50))
        
        if not validate_time_range(time_range):
            return jsonify({
                'success': False,
                'error': 'Range de tempo inválido'
            }), 400
        
        system = get_analytics_system()
        efficiency_data = system.get_clusters_efficiency(
            time_range=time_range,
            category=category,
            nicho=nicho,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in efficiency_data]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter eficiência de clusters: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para comportamento do usuário
@advanced_analytics_bp.route('/user/behavior', methods=['GET'])
@require_auth
def get_user_behavior():
    """Obtém dados de comportamento do usuário"""
    try:
        time_range = request.args.get('timeRange', '7d')
        user_id = request.args.get('user_id')
        action_type = request.args.get('action_type')
        limit = int(request.args.get('limit', 1000))
        
        if not validate_time_range(time_range):
            return jsonify({
                'success': False,
                'error': 'Range de tempo inválido'
            }), 400
        
        system = get_analytics_system()
        behavior_data = system.get_user_behavior(
            time_range=time_range,
            user_id=user_id,
            action_type=action_type,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in behavior_data]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter comportamento do usuário: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para insights preditivos
@advanced_analytics_bp.route('/predictive/insights', methods=['GET'])
@require_auth
def get_predictive_insights():
    """Obtém insights preditivos"""
    try:
        insight_type = request.args.get('type')
        confidence_threshold = float(request.args.get('confidence', 0.7))
        limit = int(request.args.get('limit', 10))
        
        system = get_analytics_system()
        insights = system.get_predictive_insights(
            insight_type=insight_type,
            confidence_threshold=confidence_threshold,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in insights]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter insights preditivos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para métricas resumidas
@advanced_analytics_bp.route('/summary', methods=['GET'])
@require_auth
def get_analytics_summary():
    """Obtém métricas resumidas de analytics"""
    try:
        time_range = request.args.get('timeRange', '7d')
        category = request.args.get('category', 'all')
        nicho = request.args.get('nicho', 'all')
        
        if not validate_time_range(time_range):
            return jsonify({
                'success': False,
                'error': 'Range de tempo inválido'
            }), 400
        
        system = get_analytics_system()
        summary = system.get_summary_metrics(
            time_range=time_range,
            category=category,
            nicho=nicho
        )
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter métricas resumidas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para exportação de dados
@advanced_analytics_bp.route('/export', methods=['POST'])
@require_auth
def export_analytics_data():
    """Exporta dados de analytics em diferentes formatos"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados de exportação necessários'
            }), 400
        
        format_type = data.get('format', 'csv')
        time_range = data.get('timeRange', '7d')
        category = data.get('category', 'all')
        nicho = data.get('nicho', 'all')
        metrics = data.get('metrics', ['performance', 'efficiency', 'behavior'])
        
        # Validações
        if not validate_export_format(format_type):
            return jsonify({
                'success': False,
                'error': 'Formato de exportação inválido'
            }), 400
        
        if not validate_time_range(time_range):
            return jsonify({
                'success': False,
                'error': 'Range de tempo inválido'
            }), 400
        
        system = get_analytics_system()
        
        # Gerar dados para exportação
        export_data = system.export_analytics_data(
            format_type=format_type,
            time_range=time_range,
            category=category,
            nicho=nicho,
            metrics=metrics
        )
        
        if format_type == 'csv':
            return send_file(
                io.BytesIO(export_data.encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'analytics_{time_range}_{datetime.now().strftime("%Y%m%data")}.csv'
            )
        elif format_type == 'json':
            return send_file(
                io.BytesIO(export_data.encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'analytics_{time_range}_{datetime.now().strftime("%Y%m%data")}.json'
            )
        elif format_type == 'excel':
            return send_file(
                io.BytesIO(export_data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'analytics_{time_range}_{datetime.now().strftime("%Y%m%data")}.xlsx'
            )
        elif format_type == 'pdf':
            return send_file(
                io.BytesIO(export_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'analytics_{time_range}_{datetime.now().strftime("%Y%m%data")}.pdf'
            )
        
    except Exception as e:
        current_app.logger.error(f"Erro na exportação: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro na exportação',
            'message': str(e)
        }), 500

# Endpoint para personalização de dashboard
@advanced_analytics_bp.route('/dashboard/customize', methods=['POST'])
@require_auth
def customize_dashboard():
    """Personaliza configurações do dashboard"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados de personalização necessários'
            }), 400
        
        user_id = get_user_id_from_request()
        widgets = data.get('widgets', [])
        settings = data.get('settings', {})
        
        system = get_analytics_system()
        success = system.save_dashboard_customization(
            user_id=user_id,
            widgets=widgets,
            settings=settings
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Personalização salva com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao salvar personalização'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Erro na personalização: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para obter configurações personalizadas
@advanced_analytics_bp.route('/dashboard/customize', methods=['GET'])
@require_auth
def get_dashboard_customization():
    """Obtém configurações personalizadas do dashboard"""
    try:
        user_id = get_user_id_from_request()
        
        system = get_analytics_system()
        customization = system.get_dashboard_customization(user_id=user_id)
        
        return jsonify({
            'success': True,
            'data': customization
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter personalização: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para gerar novos insights preditivos
@advanced_analytics_bp.route('/predictive/generate', methods=['POST'])
@require_auth
def generate_predictive_insights():
    """Gera novos insights preditivos"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Parâmetros necessários'
            }), 400
        
        insight_types = data.get('types', ['keyword_trend', 'cluster_performance'])
        force_regeneration = data.get('force_regeneration', False)
        
        system = get_analytics_system()
        insights = system.generate_predictive_insights(
            insight_types=insight_types,
            force_regeneration=force_regeneration
        )
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in insights],
            'message': f'{len(insights)} novos insights gerados'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Endpoint para métricas em tempo real
@advanced_analytics_bp.route('/realtime', methods=['GET'])
@require_auth
def get_realtime_metrics():
    """Obtém métricas em tempo real"""
    try:
        system = get_analytics_system()
        realtime_data = system.get_realtime_metrics()
        
        return jsonify({
            'success': True,
            'data': realtime_data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter métricas em tempo real: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

# Health check
@advanced_analytics_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do sistema de analytics"""
    try:
        system = get_analytics_system()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'features': [
                'keyword_performance_analysis',
                'cluster_efficiency_analysis',
                'user_behavior_analysis',
                'predictive_insights',
                'data_export',
                'dashboard_customization'
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500 