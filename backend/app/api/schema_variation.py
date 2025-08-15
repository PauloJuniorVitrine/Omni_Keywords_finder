"""
Schema Variation System - Backend
================================

Sistema de variação de schemas baseado em feature flags para permitir
diferentes versões de APIs dinamicamente.

Tracing ID: SCHEMA_VARIATION_BACKEND_20250127_001
Prompt: CHECKLIST_AJUSTES_FINOS_INTERFACE.md - Item 6.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import json
import logging
from typing import Dict, Any, Optional, Union, List
from functools import wraps
from datetime import datetime
import hashlib

from flask import request, jsonify, current_app
from marshmallow import Schema, fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from infrastructure.feature_flags.conditional_flags import ConditionalFeatureFlags
from infrastructure.observability.opentelemetry_config import get_tracer

# Configuração de logging
logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class SchemaVersion:
    """Representa uma versão de schema com metadados."""
    
    def __init__(self, version: str, schema: Schema, description: str = "", 
                 deprecated: bool = False, breaking_changes: List[str] = None):
        self.version = version
        self.schema = schema
        self.description = description
        self.deprecated = deprecated
        self.breaking_changes = breaking_changes or []
        self.created_at = datetime.utcnow()
        self.hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Gera hash único para o schema."""
        schema_str = str(self.schema.__class__.__name__) + str(self.schema.fields)
        return hashlib.md5(schema_str.encode()).hexdigest()[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "version": self.version,
            "description": self.description,
            "deprecated": self.deprecated,
            "breaking_changes": self.breaking_changes,
            "created_at": self.created_at.isoformat(),
            "hash": self.hash
        }


class SchemaVariationManager:
    """Gerencia variações de schemas baseadas em feature flags."""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, SchemaVersion]] = {}
        self.feature_flags = ConditionalFeatureFlags()
        self._setup_default_schemas()
    
    def _setup_default_schemas(self):
        """Configura schemas padrão do sistema."""
        # Schema padrão para Keywords
        class KeywordSchemaV1(Schema):
            id = fields.Int(dump_only=True)
            keyword = fields.Str(required=True, validate=lambda value: len(value) > 0)
            volume = fields.Int(allow_none=True)
            difficulty = fields.Float(allow_none=True)
            created_at = fields.DateTime(dump_only=True)
        
        class KeywordSchemaV2(Schema):
            id = fields.Int(dump_only=True)
            keyword = fields.Str(required=True, validate=lambda value: len(value) > 0)
            volume = fields.Int(allow_none=True)
            difficulty = fields.Float(allow_none=True)
            cpc = fields.Float(allow_none=True)  # Novo campo
            competition = fields.Str(allow_none=True)  # Novo campo
            created_at = fields.DateTime(dump_only=True)
            updated_at = fields.DateTime(dump_only=True)  # Novo campo
        
        # Schema padrão para Nichos
        class NichoSchemaV1(Schema):
            id = fields.Int(dump_only=True)
            nome = fields.Str(required=True)
            descricao = fields.Str(allow_none=True)
            ativo = fields.Bool(default=True)
        
        class NichoSchemaV2(Schema):
            id = fields.Int(dump_only=True)
            nome = fields.Str(required=True)
            descricao = fields.Str(allow_none=True)
            ativo = fields.Bool(default=True)
            categoria = fields.Str(allow_none=True)  # Novo campo
            prioridade = fields.Int(default=0)  # Novo campo
            metadata = fields.Dict(allow_none=True)  # Novo campo
        
        # Registrar schemas
        self.register_schema("keywords", "v1", KeywordSchemaV1(), 
                           "Schema padrão para keywords")
        self.register_schema("keywords", "v2", KeywordSchemaV2(), 
                           "Schema expandido para keywords com CPC e competição")
        self.register_schema("nichos", "v1", NichoSchemaV1(), 
                           "Schema padrão para nichos")
        self.register_schema("nichos", "v2", NichoSchemaV2(), 
                           "Schema expandido para nichos com categorias")
    
    def register_schema(self, resource: str, version: str, schema: Schema, 
                       description: str = "", deprecated: bool = False,
                       breaking_changes: List[str] = None) -> None:
        """Registra uma nova versão de schema."""
        with tracer.start_as_current_span("register_schema") as span:
            span.set_attribute("resource", resource)
            span.set_attribute("version", version)
            
            if resource not in self.schemas:
                self.schemas[resource] = {}
            
            schema_version = SchemaVersion(
                version=version,
                schema=schema,
                description=description,
                deprecated=deprecated,
                breaking_changes=breaking_changes
            )
            
            self.schemas[resource][version] = schema_version
            logger.info(f"Schema registrado: {resource} value{version} - {description}")
    
    def get_schema(self, resource: str, context: Dict[str, Any] = None) -> Schema:
        """Obtém schema baseado em feature flags e contexto."""
        with tracer.start_as_current_span("get_schema") as span:
            span.set_attribute("resource", resource)
            span.set_attribute("context", str(context))
            
            if resource not in self.schemas:
                raise ValueError(f"Recurso '{resource}' não encontrado")
            
            # Determinar versão baseada em feature flags
            version = self._determine_version(resource, context)
            span.set_attribute("selected_version", version)
            
            if version not in self.schemas[resource]:
                raise ValueError(f"Versão '{version}' não encontrada para '{resource}'")
            
            schema_version = self.schemas[resource][version]
            
            # Log de deprecação se necessário
            if schema_version.deprecated:
                logger.warning(f"Usando schema depreciado: {resource} value{version}")
            
            return schema_version.schema
    
    def _determine_version(self, resource: str, context: Dict[str, Any] = None) -> str:
        """Determina versão baseada em feature flags e contexto."""
        context = context or {}
        
        # Verificar feature flags específicas
        if self.feature_flags.is_enabled("schema_v2_enabled", context):
            return "v2"
        
        # Verificar flags por recurso
        resource_flag = f"{resource}_schema_v2"
        if self.feature_flags.is_enabled(resource_flag, context):
            return "v2"
        
        # Verificar contexto de usuário
        user_tier = context.get("user_tier", "basic")
        if user_tier in ["premium", "enterprise"]:
            premium_flag = f"{resource}_premium_schema"
            if self.feature_flags.is_enabled(premium_flag, context):
                return "v2"
        
        # Padrão: versão mais antiga estável
        return "v1"
    
    def get_available_versions(self, resource: str) -> List[Dict[str, Any]]:
        """Retorna versões disponíveis para um recurso."""
        if resource not in self.schemas:
            return []
        
        return [schema_version.to_dict() 
                for schema_version in self.schemas[resource].values()]
    
    def validate_data(self, resource: str, data: Dict[str, Any], 
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Valida dados usando schema apropriado."""
        with tracer.start_as_current_span("validate_data") as span:
            span.set_attribute("resource", resource)
            
            schema = self.get_schema(resource, context)
            
            try:
                validated_data = schema.load(data)
                span.set_attribute("validation_success", True)
                return validated_data
            except ValidationError as e:
                span.set_attribute("validation_success", False)
                span.set_attribute("validation_errors", str(e.messages))
                raise e
    
    def serialize_data(self, resource: str, data: Union[Dict, List], 
                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Serializa dados usando schema apropriado."""
        with tracer.start_as_current_span("serialize_data") as span:
            span.set_attribute("resource", resource)
            
            schema = self.get_schema(resource, context)
            
            try:
                serialized_data = schema.dump(data, many=isinstance(data, list))
                span.set_attribute("serialization_success", True)
                return serialized_data
            except Exception as e:
                span.set_attribute("serialization_success", False)
                span.set_attribute("serialization_error", str(e))
                raise e


# Instância global
schema_manager = SchemaVariationManager()


def schema_variation(resource: str):
    """Decorator para aplicar variação de schema em endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            with tracer.start_as_current_span("schema_variation_decorator") as span:
                span.set_attribute("resource", resource)
                span.set_attribute("endpoint", f.__name__)
                
                # Extrair contexto da request
                context = {
                    "user_id": getattr(request, 'user_id', None),
                    "user_tier": getattr(request, 'user_tier', 'basic'),
                    "headers": dict(request.headers),
                    "query_params": dict(request.args)
                }
                
                span.set_attribute("context", str(context))
                
                try:
                    # Executar função original
                    result = f(*args, **kwargs)
                    
                    # Aplicar serialização se necessário
                    if isinstance(result, (dict, list)):
                        serialized_result = schema_manager.serialize_data(
                            resource, result, context
                        )
                        span.set_attribute("schema_version_used", 
                                         schema_manager._determine_version(resource, context))
                        return jsonify(serialized_result)
                    
                    return result
                    
                except Exception as e:
                    span.set_attribute("error", str(e))
                    logger.error(f"Erro no schema variation: {e}")
                    raise
                
        return decorated_function
    return decorator


def validate_schema_input(resource: str):
    """Decorator para validar input usando schema apropriado."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            with tracer.start_as_current_span("validate_schema_input") as span:
                span.set_attribute("resource", resource)
                span.set_attribute("endpoint", f.__name__)
                
                # Extrair dados da request
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()
                
                # Extrair contexto
                context = {
                    "user_id": getattr(request, 'user_id', None),
                    "user_tier": getattr(request, 'user_tier', 'basic'),
                    "headers": dict(request.headers)
                }
                
                try:
                    # Validar dados
                    validated_data = schema_manager.validate_data(resource, data, context)
                    
                    # Substituir dados originais pelos validados
                    if request.is_json:
                        request._cached_json = validated_data
                    else:
                        request.form = type('FormData', (), validated_data)()
                    
                    span.set_attribute("validation_success", True)
                    return f(*args, **kwargs)
                    
                except ValidationError as e:
                    span.set_attribute("validation_success", False)
                    span.set_attribute("validation_errors", str(e.messages))
                    return jsonify({
                        "error": "Dados inválidos",
                        "details": e.messages,
                        "schema_version": schema_manager._determine_version(resource, context)
                    }), 400
                
        return decorated_function
    return decorator


# Endpoints para gerenciamento de schemas
def register_schema_endpoints(app):
    """Registra endpoints para gerenciamento de schemas."""
    
    @app.route('/api/schemas/<resource>/versions', methods=['GET'])
    def get_schema_versions(resource):
        """Retorna versões disponíveis de schema para um recurso."""
        try:
            versions = schema_manager.get_available_versions(resource)
            return jsonify({
                "resource": resource,
                "versions": versions,
                "current_default": schema_manager._determine_version(resource)
            })
        except Exception as e:
            logger.error(f"Erro ao obter versões de schema: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/schemas/<resource>/validate', methods=['POST'])
    def validate_schema_data(resource):
        """Valida dados usando schema apropriado."""
        try:
            data = request.get_json()
            context = {
                "user_id": getattr(request, 'user_id', None),
                "user_tier": getattr(request, 'user_tier', 'basic')
            }
            
            validated_data = schema_manager.validate_data(resource, data, context)
            version = schema_manager._determine_version(resource, context)
            
            return jsonify({
                "valid": True,
                "data": validated_data,
                "schema_version": version
            })
        except ValidationError as e:
            return jsonify({
                "valid": False,
                "errors": e.messages,
                "schema_version": schema_manager._determine_version(resource, {})
            }), 400
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/schemas/status', methods=['GET'])
    def get_schema_status():
        """Retorna status geral dos schemas."""
        try:
            status = {}
            for resource in schema_manager.schemas:
                status[resource] = {
                    "available_versions": list(schema_manager.schemas[resource].keys()),
                    "default_version": schema_manager._determine_version(resource),
                    "total_versions": len(schema_manager.schemas[resource])
                }
            
            return jsonify({
                "schemas": status,
                "total_resources": len(status),
                "feature_flags_enabled": {
                    "schema_v2_enabled": schema_manager.feature_flags.is_enabled("schema_v2_enabled"),
                    "keywords_schema_v2": schema_manager.feature_flags.is_enabled("keywords_schema_v2"),
                    "nichos_schema_v2": schema_manager.feature_flags.is_enabled("nichos_schema_v2")
                }
            })
        except Exception as e:
            logger.error(f"Erro ao obter status dos schemas: {e}")
            return jsonify({"error": str(e)}), 500


# Exemplo de uso em endpoints existentes
@schema_variation("keywords")
def get_keywords_example():
    """Exemplo de endpoint usando variação de schema."""
    # Simular dados de keywords
    keywords_data = [
        {
            "id": 1,
            "keyword": "python development",
            "volume": 1000,
            "difficulty": 0.7,
            "cpc": 2.5,  # Campo v2
            "competition": "high",  # Campo v2
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()  # Campo v2
        }
    ]
    
    return keywords_data


@validate_schema_input("nichos")
@schema_variation("nichos")
def create_nicho_example():
    """Exemplo de endpoint com validação de input e variação de schema."""
    # Dados já validados pelo decorator
    nicho_data = {
        "id": 1,
        "nome": "Tecnologia",
        "descricao": "Nicho de tecnologia",
        "ativo": True,
        "categoria": "tech",  # Campo v2
        "prioridade": 1,  # Campo v2
        "metadata": {"color": "blue"}  # Campo v2
    }
    
    return nicho_data


if __name__ == "__main__":
    # Testes unitários (não executar)
    print("Schema Variation System - Backend")
    print("Versões disponíveis para keywords:")
    print(schema_manager.get_available_versions("keywords"))
    print("\nVersões disponíveis para nichos:")
    print(schema_manager.get_available_versions("nichos"))
