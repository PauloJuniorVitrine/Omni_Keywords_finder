"""
template_export.py

API REST para Sistema de Templates de Exportação - Omni Keywords Finder

Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 10
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19

Endpoints:
- GET /api/templates - Listar templates
- POST /api/templates - Criar template
- GET /api/templates/{id} - Obter template
- PUT /api/templates/{id} - Atualizar template
- DELETE /api/templates/{id} - Deletar template
- POST /api/templates/{id}/export - Exportar com template
- GET /api/templates/{id}/preview - Preview do template
- POST /api/templates/{id}/version - Criar versão
- GET /api/templates/{id}/variables - Obter variáveis
"""

from flask import Blueprint, request, jsonify, send_file
from typing import Dict, List, Any, Optional
import logging
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Importar sistema de templates
try:
    from infrastructure.processamento.template_exporter import (
        template_exporter, TemplateFormat, TemplateType, TemplateVariable, ExportData
    )
    TEMPLATE_SYSTEM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Template system not available: {e}")
    TEMPLATE_SYSTEM_AVAILABLE = False

logger = logging.getLogger(__name__)

# Blueprint para templates
template_bp = Blueprint('templates', __name__, url_prefix='/api/templates')

@template_bp.route('/', methods=['GET'])
def list_templates():
    """
    Lista todos os templates disponíveis
    
    Query Parameters:
    - format: Formato do template (html, pptx, md, json)
    - type: Tipo do template (keywords_report, clusters_report, etc.)
    - active_only: Apenas templates ativos (default: true)
    
    Returns:
    - Lista de templates com configurações
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        # Parâmetros de filtro
        format_param = request.args.get('format')
        type_param = request.args.get('type')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # Converter parâmetros para enums
        format_enum = None
        if format_param:
            try:
                format_enum = TemplateFormat(format_param)
            except ValueError:
                return jsonify({
                    'error': 'Invalid format parameter',
                    'valid_formats': [f.value for f in TemplateFormat]
                }), 400
        
        type_enum = None
        if type_param:
            try:
                type_enum = TemplateType(type_param)
            except ValueError:
                return jsonify({
                    'error': 'Invalid type parameter',
                    'valid_types': [t.value for t in TemplateType]
                }), 400
        
        # Listar templates
        templates = template_exporter.list_templates(
            format=format_enum,
            type=type_enum,
            active_only=active_only
        )
        
        # Converter para dict
        templates_data = []
        for template in templates:
            template_dict = {
                'id': template.name,  # Usar nome como ID temporário
                'name': template.name,
                'description': template.description,
                'format': template.format.value,
                'type': template.type.value,
                'version': template.version,
                'author': template.author,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat(),
                'is_active': template.is_active,
                'is_default': template.is_default,
                'metadata': template.metadata
            }
            templates_data.append(template_dict)
        
        return jsonify({
            'templates': templates_data,
            'total': len(templates_data),
            'filters': {
                'format': format_param,
                'type': type_param,
                'active_only': active_only
            }
        })
    
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/', methods=['POST'])
def create_template():
    """
    Cria novo template
    
    Request Body:
    {
        "name": "Nome do template",
        "description": "Descrição do template",
        "format": "html|pptx|md|json",
        "type": "keywords_report|clusters_report|...",
        "content": "Conteúdo do template",
        "author": "Autor do template",
        "variables": [
            {
                "name": "var_name",
                "type": "string",
                "description": "Descrição da variável",
                "required": false,
                "default_value": null
            }
        ],
        "is_default": false
    }
    
    Returns:
    - Configuração do template criado
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['name', 'description', 'format', 'type', 'content', 'author']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validar formato
        try:
            format_enum = TemplateFormat(data['format'])
        except ValueError:
            return jsonify({
                'error': 'Invalid format',
                'valid_formats': [f.value for f in TemplateFormat]
            }), 400
        
        # Validar tipo
        try:
            type_enum = TemplateType(data['type'])
        except ValueError:
            return jsonify({
                'error': 'Invalid type',
                'valid_types': [t.value for t in TemplateType]
            }), 400
        
        # Processar variáveis
        variables = None
        if 'variables' in data and data['variables']:
            variables = []
            for var_data in data['variables']:
                try:
                    variable = TemplateVariable(**var_data)
                    variables.append(variable)
                except Exception as e:
                    return jsonify({
                        'error': f'Invalid variable definition: {str(e)}'
                    }), 400
        
        # Criar template
        config = template_exporter.create_template(
            name=data['name'],
            description=data['description'],
            format=format_enum,
            type=type_enum,
            content=data['content'],
            author=data['author'],
            variables=variables,
            is_default=data.get('is_default', False)
        )
        
        return jsonify({
            'message': 'Template created successfully',
            'template': {
                'name': config.name,
                'description': config.description,
                'format': config.format.value,
                'type': config.type.value,
                'version': config.version,
                'author': config.author,
                'created_at': config.created_at.isoformat(),
                'updated_at': config.updated_at.isoformat(),
                'is_active': config.is_active,
                'is_default': config.is_default
            }
        }), 201
    
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/<template_id>', methods=['GET'])
def get_template(template_id: str):
    """
    Obtém configuração de template específico
    
    Returns:
    - Configuração completa do template
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        config = template_exporter.get_template_config(template_id)
        if not config:
            return jsonify({
                'error': 'Template not found',
                'template_id': template_id
            }), 404
        
        return jsonify({
            'template': {
                'id': template_id,
                'name': config.name,
                'description': config.description,
                'format': config.format.value,
                'type': config.type.value,
                'version': config.version,
                'author': config.author,
                'created_at': config.created_at.isoformat(),
                'updated_at': config.updated_at.isoformat(),
                'is_active': config.is_active,
                'is_default': config.is_default,
                'metadata': config.metadata
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/<template_id>', methods=['PUT'])
def update_template(template_id: str):
    """
    Atualiza template existente
    
    Request Body:
    {
        "content": "Novo conteúdo (opcional)",
        "description": "Nova descrição (opcional)",
        "is_active": true/false (opcional),
        "variables": [...] (opcional)
    }
    
    Returns:
    - Configuração atualizada do template
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        data = request.get_json()
        
        # Processar variáveis se fornecidas
        variables = None
        if 'variables' in data and data['variables']:
            variables = []
            for var_data in data['variables']:
                try:
                    variable = TemplateVariable(**var_data)
                    variables.append(variable)
                except Exception as e:
                    return jsonify({
                        'error': f'Invalid variable definition: {str(e)}'
                    }), 400
        
        # Atualizar template
        config = template_exporter.update_template(
            template_id=template_id,
            content=data.get('content'),
            variables=variables,
            description=data.get('description'),
            is_active=data.get('is_active')
        )
        
        return jsonify({
            'message': 'Template updated successfully',
            'template': {
                'id': template_id,
                'name': config.name,
                'description': config.description,
                'format': config.format.value,
                'type': config.type.value,
                'version': config.version,
                'author': config.author,
                'created_at': config.created_at.isoformat(),
                'updated_at': config.updated_at.isoformat(),
                'is_active': config.is_active,
                'is_default': config.is_default
            }
        })
    
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/<template_id>', methods=['DELETE'])
def delete_template(template_id: str):
    """
    Deleta template (marca como inativo)
    
    Returns:
    - Confirmação de exclusão
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        # Marcar como inativo em vez de deletar fisicamente
        config = template_exporter.update_template(
            template_id=template_id,
            is_active=False
        )
        
        return jsonify({
            'message': 'Template deleted successfully',
            'template_id': template_id
        })
    
    except ValueError as e:
        return jsonify({
            'error': 'Template not found',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/<template_id>/export', methods=['POST'])
def export_with_template(template_id: str):
    """
    Exporta dados usando template específico
    
    Request Body:
    {
        "data": {
            "keywords": [...],
            "clusters": [...],
            "performance_metrics": {...},
            "business_metrics": {...},
            "audit_logs": [...],
            "custom_data": {...}
        },
        "custom_variables": {...} (opcional),
        "output_filename": "nome_arquivo" (opcional)
    }
    
    Returns:
    - Arquivo exportado para download
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'error': 'Missing required field: data'
            }), 400
        
        # Criar objeto ExportData
        export_data = ExportData(
            keywords=data['data'].get('keywords', []),
            clusters=data['data'].get('clusters', []),
            performance_metrics=data['data'].get('performance_metrics', {}),
            business_metrics=data['data'].get('business_metrics', {}),
            audit_logs=data['data'].get('audit_logs', []),
            custom_data=data['data'].get('custom_data', {})
        )
        
        # Gerar nome do arquivo
        output_filename = data.get('output_filename')
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"export_{template_id}_{timestamp}"
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
            output_path = tmp_file.name
        
        # Exportar com template
        try:
            final_path = template_exporter.export_with_template(
                template_id=template_id,
                data=export_data,
                output_path=output_path,
                custom_variables=data.get('custom_variables')
            )
            
            # Obter extensão do arquivo
            file_ext = Path(final_path).suffix
            if not output_filename.endswith(file_ext):
                output_filename += file_ext
            
            # Enviar arquivo
            return send_file(
                final_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/octet-stream'
            )
        
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(output_path)
            except:
                pass
    
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error exporting with template: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/<template_id>/preview', methods=['GET'])
def preview_template(template_id: str):
    """
    Gera preview do template com dados de exemplo
    
    Query Parameters:
    - sample_data: true/false (usar dados de exemplo)
    
    Returns:
    - Preview renderizado do template
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        use_sample_data = request.args.get('sample_data', 'true').lower() == 'true'
        
        if use_sample_data:
            # Dados de exemplo
            sample_data = ExportData(
                keywords=[
                    {'termo': 'palavra chave 1', 'volume': 1000, 'dificuldade': 'média'},
                    {'termo': 'palavra chave 2', 'volume': 500, 'dificuldade': 'baixa'},
                    {'termo': 'palavra chave 3', 'volume': 2000, 'dificuldade': 'alta'}
                ],
                clusters=[
                    {'nome': 'Cluster A', 'keywords': ['kw1', 'kw2'], 'volume_total': 1500},
                    {'nome': 'Cluster B', 'keywords': ['kw3'], 'volume_total': 2000}
                ],
                performance_metrics={
                    'response_time': 150,
                    'throughput': 1000,
                    'error_rate': 0.5
                },
                business_metrics={
                    'roi': 150.0,
                    'conversions': 25,
                    'revenue': 50000.0
                },
                audit_logs=[
                    {'event': 'export', 'timestamp': datetime.now().isoformat(), 'user': 'admin'}
                ]
            )
        else:
            # Dados vazios
            sample_data = ExportData()
        
        # Gerar preview
        preview_content = template_exporter.preview_template(
            template_id=template_id,
            data=sample_data
        )
        
        # Obter configuração do template para determinar tipo de resposta
        config = template_exporter.get_template_config(template_id)
        if not config:
            return jsonify({
                'error': 'Template not found',
                'template_id': template_id
            }), 404
        
        # Retornar baseado no formato
        if config.format == TemplateFormat.HTML:
            return preview_content, 200, {'Content-Type': 'text/html'}
        elif config.format == TemplateFormat.MARKDOWN:
            return preview_content, 200, {'Content-Type': 'text/markdown'}
        elif config.format == TemplateFormat.JSON:
            return jsonify(preview_content), 200
        else:
            return preview_content, 200, {'Content-Type': 'text/plain'}
    
    except ValueError as e:
        return jsonify({
            'error': 'Template not found',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/<template_id>/version', methods=['POST'])
def create_template_version(template_id: str):
    """
    Cria nova versão do template
    
    Request Body:
    {
        "version_name": "2.0.0"
    }
    
    Returns:
    - ID da nova versão criada
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        data = request.get_json()
        
        if 'version_name' not in data:
            return jsonify({
                'error': 'Missing required field: version_name'
            }), 400
        
        # Criar nova versão
        new_template_id = template_exporter.create_template_version(
            template_id=template_id,
            version_name=data['version_name']
        )
        
        return jsonify({
            'message': 'Template version created successfully',
            'original_template_id': template_id,
            'new_template_id': new_template_id,
            'version_name': data['version_name']
        }), 201
    
    except ValueError as e:
        return jsonify({
            'error': 'Template not found',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error creating template version: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/<template_id>/variables', methods=['GET'])
def get_template_variables(template_id: str):
    """
    Obtém variáveis do template
    
    Returns:
    - Lista de variáveis do template
    """
    if not TEMPLATE_SYSTEM_AVAILABLE:
        return jsonify({
            'error': 'Template system not available',
            'message': 'Template export system is not properly configured'
        }), 503
    
    try:
        variables = template_exporter.get_template_variables(template_id)
        
        variables_data = []
        for var in variables:
            var_dict = {
                'name': var.name,
                'type': var.type,
                'description': var.description,
                'required': var.required,
                'default_value': var.default_value,
                'validation_rules': var.validation_rules
            }
            variables_data.append(var_dict)
        
        return jsonify({
            'template_id': template_id,
            'variables': variables_data,
            'total': len(variables_data)
        })
    
    except Exception as e:
        logger.error(f"Error getting template variables: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@template_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """
    Obtém formatos suportados
    
    Returns:
    - Lista de formatos suportados
    """
    return jsonify({
        'formats': [
            {
                'value': f.value,
                'name': f.name,
                'description': f'Template {f.value.upper()}'
            }
            for f in TemplateFormat
        ]
    })

@template_bp.route('/types', methods=['GET'])
def get_supported_types():
    """
    Obtém tipos suportados
    
    Returns:
    - Lista de tipos suportados
    """
    return jsonify({
        'types': [
            {
                'value': t.value,
                'name': t.name,
                'description': t.value.replace('_', ' ').title()
            }
            for t in TemplateType
        ]
    })

# Registrar blueprint
def init_template_api(app):
    """Inicializa API de templates"""
    app.register_blueprint(template_bp)
    logger.info("Template export API initialized") 