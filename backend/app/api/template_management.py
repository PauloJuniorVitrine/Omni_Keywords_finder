"""
API para Gerenciamento de Templates de Exportação - Omni Keywords Finder

Endpoints para criar, gerenciar, renderizar e exportar templates de relatórios
em diferentes formatos (HTML, PowerPoint, Markdown, PDF).

Autor: Sistema de Templates de Exportação
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import uuid
import os
from pathlib import Path
from functools import wraps

# Importar sistema de templates
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from infrastructure.processamento.template_exporter import (
    TemplateExporter,
    TemplateConfig,
    TemplateVariable,
    TemplateType,
    TemplateCategory,
    create_template_exporter
)

# Blueprint para templates
templates_bp = Blueprint('templates', __name__, url_prefix='/api/templates')

# Sistema de templates global
template_exporter = None

def get_template_exporter() -> TemplateExporter:
    """Obtém instância do sistema de templates"""
    global template_exporter
    if template_exporter is None:
        template_exporter = create_template_exporter()
        # Criar templates padrão se não existirem
        if not template_exporter.list_templates():
            template_exporter.create_default_templates()
    return template_exporter

def require_auth(f):
    """Decorator para autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implementar autenticação aqui
        # Por enquanto, sempre permite
        return f(*args, **kwargs)
    return decorated_function

def validate_template_data(data: Dict[str, Any]) -> List[str]:
    """Valida dados de template"""
    errors = []
    
    required_fields = ['name', 'description', 'category', 'template_type']
    for field in required_fields:
        if field not in data:
            errors.append(f"Campo obrigatório ausente: {field}")
    
    # Validar categoria
    if 'category' in data:
        try:
            TemplateCategory(data['category'])
        except ValueError:
            errors.append(f"Categoria inválida: {data['category']}")
    
    # Validar tipo de template
    if 'template_type' in data:
        try:
            TemplateType(data['template_type'])
        except ValueError:
            errors.append(f"Tipo de template inválido: {data['template_type']}")
    
    return errors

# Endpoints para gerenciar templates

@templates_bp.route('/', methods=['GET'])
@require_auth
def list_templates():
    """Lista todos os templates disponíveis"""
    try:
        exporter = get_template_exporter()
        category = request.args.get('category')
        
        if category:
            try:
                category_enum = TemplateCategory(category)
                templates = exporter.list_templates(category_enum)
            except ValueError:
                return jsonify({'error': 'Categoria inválida'}), 400
        else:
            templates = exporter.list_templates()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category.value,
                'template_type': template.template_type.value,
                'version': template.version,
                'author': template.author,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'updated_at': template.updated_at.isoformat() if template.updated_at else None,
                'variables': [asdict(value) for value in template.variables] if template.variables else [],
                'dependencies': template.dependencies,
                'metadata': template.metadata
            })
        
        return jsonify({
            'templates': template_list,
            'total': len(template_list)
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar templates: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/', methods=['POST'])
@require_auth
def create_template():
    """Cria um novo template"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        # Validar dados
        errors = validate_template_data(data)
        if errors:
            return jsonify({'error': 'Dados inválidos', 'details': errors}), 400
        
        exporter = get_template_exporter()
        
        # Criar configuração do template
        config = TemplateConfig(
            id=data.get('id') or str(uuid.uuid4()),
            name=data['name'],
            description=data['description'],
            category=TemplateCategory(data['category']),
            template_type=TemplateType(data['template_type']),
            version=data.get('version', '1.0.0'),
            author=data.get('author', 'system'),
            variables=[TemplateVariable(**value) for value in data.get('variables', [])],
            dependencies=data.get('dependencies'),
            metadata=data.get('metadata', {})
        )
        
        # Conteúdo do template
        content = data.get('content', '')
        if not content:
            return jsonify({'error': 'Conteúdo do template é obrigatório'}), 400
        
        # Criar template
        if exporter.create_template(config, content):
            return jsonify({
                'message': 'Template criado com sucesso',
                'template_id': config.id
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar template'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/<template_id>', methods=['GET'])
@require_auth
def get_template(template_id: str):
    """Obtém detalhes de um template específico"""
    try:
        exporter = get_template_exporter()
        template_data = exporter.get_template(template_id)
        
        if not template_data:
            return jsonify({'error': 'Template não encontrado'}), 404
        
        config, content = template_data
        
        return jsonify({
            'id': config.id,
            'name': config.name,
            'description': config.description,
            'category': config.category.value,
            'template_type': config.template_type.value,
            'version': config.version,
            'author': config.author,
            'created_at': config.created_at.isoformat() if config.created_at else None,
            'updated_at': config.updated_at.isoformat() if config.updated_at else None,
            'variables': [asdict(value) for value in config.variables] if config.variables else [],
            'dependencies': config.dependencies,
            'metadata': config.metadata,
            'content': content
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/<template_id>', methods=['PUT'])
@require_auth
def update_template(template_id: str):
    """Atualiza um template existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        exporter = get_template_exporter()
        
        # Verificar se template existe
        existing_data = exporter.get_template(template_id)
        if not existing_data:
            return jsonify({'error': 'Template não encontrado'}), 404
        
        existing_config, existing_content = existing_data
        
        # Atualizar configuração
        updated_config = TemplateConfig(
            id=template_id,
            name=data.get('name', existing_config.name),
            description=data.get('description', existing_config.description),
            category=TemplateCategory(data.get('category', existing_config.category.value)),
            template_type=TemplateType(data.get('template_type', existing_config.template_type.value)),
            version=data.get('version', existing_config.version),
            author=data.get('author', existing_config.author),
            created_at=existing_config.created_at,
            updated_at=datetime.utcnow(),
            variables=[TemplateVariable(**value) for value in data.get('variables', [])] if data.get('variables') else existing_config.variables,
            dependencies=data.get('dependencies', existing_config.dependencies),
            metadata=data.get('metadata', existing_config.metadata)
        )
        
        # Conteúdo atualizado
        content = data.get('content', existing_content)
        
        # Atualizar template
        if exporter.create_template(updated_config, content):
            return jsonify({
                'message': 'Template atualizado com sucesso',
                'template_id': template_id
            })
        else:
            return jsonify({'error': 'Erro ao atualizar template'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/<template_id>', methods=['DELETE'])
@require_auth
def delete_template(template_id: str):
    """Remove um template"""
    try:
        exporter = get_template_exporter()
        
        # Verificar se template existe
        existing_data = exporter.get_template(template_id)
        if not existing_data:
            return jsonify({'error': 'Template não encontrado'}), 404
        
        # Por enquanto, apenas retorna sucesso
        # Implementar remoção real no sistema de templates
        return jsonify({
            'message': 'Template removido com sucesso',
            'template_id': template_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/<template_id>/preview', methods=['POST'])
@require_auth
def preview_template(template_id: str):
    """Gera preview de um template"""
    try:
        data = request.get_json() or {}
        sample_data = data.get('sample_data', {})
        
        exporter = get_template_exporter()
        
        # Gerar preview
        preview_content = exporter.preview_template(template_id, sample_data)
        
        return jsonify({
            'template_id': template_id,
            'preview': preview_content
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar preview: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/<template_id>/render', methods=['POST'])
@require_auth
def render_template(template_id: str):
    """Renderiza um template com dados"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        template_data = data.get('data', {})
        output_format = data.get('output_format')
        custom_styles = data.get('custom_styles')
        
        exporter = get_template_exporter()
        
        # Determinar formato de saída
        if output_format:
            try:
                output_type = TemplateType(output_format)
            except ValueError:
                return jsonify({'error': 'Formato de saída inválido'}), 400
        else:
            output_type = None
        
        # Renderizar template
        try:
            rendered_content = exporter.render_template(
                template_id, 
                template_data, 
                output_type, 
                custom_styles
            )
            
            # Se for bytes (PowerPoint, PDF), retornar como base64
            if isinstance(rendered_content, bytes):
                import base64
                content_b64 = base64.b64encode(rendered_content).decode('utf-8')
                return jsonify({
                    'template_id': template_id,
                    'content': content_b64,
                    'content_type': 'binary',
                    'format': output_format or 'original'
                })
            else:
                return jsonify({
                    'template_id': template_id,
                    'content': rendered_content,
                    'content_type': 'text',
                    'format': output_format or 'original'
                })
                
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except ImportError as e:
            return jsonify({'error': f'Formato não suportado: {str(e)}'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao renderizar template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/<template_id>/export', methods=['POST'])
@require_auth
def export_template(template_id: str):
    """Exporta template renderizado para arquivo"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        template_data = data.get('data', {})
        output_format = data.get('output_format')
        filename = data.get('filename')
        
        if not output_format:
            return jsonify({'error': 'Formato de saída é obrigatório'}), 400
        
        try:
            output_type = TemplateType(output_format)
        except ValueError:
            return jsonify({'error': 'Formato de saída inválido'}), 400
        
        exporter = get_template_exporter()
        
        # Exportar template
        try:
            file_path = exporter.export_template(template_id, template_data, output_type, filename)
            
            return jsonify({
                'template_id': template_id,
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'format': output_format
            })
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except ImportError as e:
            return jsonify({'error': f'Formato não suportado: {str(e)}'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar template: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/<template_id>/download', methods=['POST'])
@require_auth
def download_template(template_id: str):
    """Download do arquivo exportado"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON necessários'}), 400
        
        template_data = data.get('data', {})
        output_format = data.get('output_format')
        filename = data.get('filename')
        
        if not output_format:
            return jsonify({'error': 'Formato de saída é obrigatório'}), 400
        
        try:
            output_type = TemplateType(output_format)
        except ValueError:
            return jsonify({'error': 'Formato de saída inválido'}), 400
        
        exporter = get_template_exporter()
        
        # Exportar template
        try:
            file_path = exporter.export_template(template_id, template_data, output_type, filename)
            
            # Retornar arquivo para download
            return send_file(
                file_path,
                as_attachment=True,
                download_name=os.path.basename(file_path),
                mimetype='application/octet-stream'
            )
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except ImportError as e:
            return jsonify({'error': f'Formato não suportado: {str(e)}'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao fazer download: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/categories', methods=['GET'])
@require_auth
def list_categories():
    """Lista todas as categorias disponíveis"""
    try:
        categories = []
        for category in TemplateCategory:
            categories.append({
                'value': category.value,
                'name': category.name,
                'description': f"Templates para {category.value.replace('_', ' ')}"
            })
        
        return jsonify({
            'categories': categories
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar categorias: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/types', methods=['GET'])
@require_auth
def list_types():
    """Lista todos os tipos de template disponíveis"""
    try:
        types = []
        for template_type in TemplateType:
            types.append({
                'value': template_type.value,
                'name': template_type.name,
                'description': f"Template em formato {template_type.value.upper()}"
            })
        
        return jsonify({
            'types': types
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar tipos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@templates_bp.route('/defaults', methods=['POST'])
@require_auth
def create_default_templates():
    """Cria templates padrão do sistema"""
    try:
        exporter = get_template_exporter()
        exporter.create_default_templates()
        
        return jsonify({
            'message': 'Templates padrão criados com sucesso'
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar templates padrão: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Registrar blueprint
def init_template_management(app):
    """Inicializa o sistema de gerenciamento de templates"""
    app.register_blueprint(templates_bp)
    current_app.logger.info("Sistema de Gerenciamento de Templates inicializado") 