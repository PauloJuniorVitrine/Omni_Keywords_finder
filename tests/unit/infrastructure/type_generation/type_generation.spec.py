from typing import Dict, List, Optional, Any
"""
Teste para geração automática de tipos TypeScript
Tracing ID: FIXTYPE-001
"""

import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# Adicionar caminho para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

class TestTypeGeneration:
    """Testes para geração automática de tipos TypeScript"""

    def test_openapi_schema_structure(self):
        """Testa estrutura do schema OpenAPI"""
        from backend.app.api.openapi import OPENAPI_SCHEMA
        
        # Verificar estrutura básica
        assert "openapi" in OPENAPI_SCHEMA
        assert "info" in OPENAPI_SCHEMA
        assert "paths" in OPENAPI_SCHEMA
        assert "components" in OPENAPI_SCHEMA
        
        # Verificar versão
        assert OPENAPI_SCHEMA["openapi"] == "3.0.3"
        
        # Verificar informações
        info = OPENAPI_SCHEMA["info"]
        assert info["title"] == "Omni Keywords Finder API"
        assert info["version"] == "1.0.0"

    def test_openapi_endpoints_coverage(self):
        """Testa cobertura de endpoints no OpenAPI"""
        from backend.app.api.openapi import OPENAPI_SCHEMA
        
        paths = OPENAPI_SCHEMA["paths"]
        
        # Verificar endpoints principais
        expected_endpoints = [
            "/api/nichos",
            "/api/nichos/{nicho_id}",
            "/api/categorias/{nicho_id}",
            "/api/execucoes",
            "/api/execucoes/agendar",
            "/api/logs/execucoes",
            "/api/logs/dashboard/metrics",
            "/api/clusters/sugerir",
            "/api/auth/login",
            "/api/auth/logout"
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in paths, f"Endpoint {endpoint} não encontrado no OpenAPI"

    def test_openapi_schemas_coverage(self):
        """Testa cobertura de schemas no OpenAPI"""
        from backend.app.api.openapi import OPENAPI_SCHEMA
        
        schemas = OPENAPI_SCHEMA["components"]["schemas"]
        
        # Verificar schemas principais
        expected_schemas = [
            "Nicho",
            "NichoInput", 
            "Categoria",
            "CategoriaInput",
            "Execucao",
            "ExecucaoInput",
            "ExecucaoAgendada",
            "ExecucaoAgendadaInput",
            "Log",
            "Cluster",
            "LoginInput",
            "LoginResponse",
            "DashboardMetrics"
        ]
        
        for schema in expected_schemas:
            assert schema in schemas, f"Schema {schema} não encontrado no OpenAPI"

    def test_typescript_generation_function(self):
        """Testa função de geração de tipos TypeScript"""
        from backend.app.api.openapi import generate_typescript_from_openapi, OPENAPI_SCHEMA
        
        # Gerar tipos TypeScript
        typescript_code = generate_typescript_from_openapi(OPENAPI_SCHEMA)
        
        # Verificar se o código foi gerado
        assert typescript_code is not None
        assert len(typescript_code) > 0
        
        # Verificar se contém interfaces esperadas
        assert "export interface Nicho" in typescript_code
        assert "export interface Categoria" in typescript_code
        assert "export interface Execucao" in typescript_code
        assert "export interface Log" in typescript_code

    def test_typescript_type_conversion(self):
        """Testa conversão de tipos OpenAPI para TypeScript"""
        from backend.app.api.openapi import get_typescript_type
        
        # Testar conversões básicas
        assert get_typescript_type({"type": "string"}) == "string"
        assert get_typescript_type({"type": "integer"}) == "number"
        assert get_typescript_type({"type": "number"}) == "number"
        assert get_typescript_type({"type": "boolean"}) == "boolean"
        
        # Testar array
        assert get_typescript_type({
            "type": "array",
            "items": {"type": "string"}
        }) == "string[]"
        
        # Testar objeto
        assert get_typescript_type({"type": "object"}) == "Record<string, any>"

    def test_schema_reference_extraction(self):
        """Testa extração de referências de schema"""
        from backend.app.api.openapi import get_schema_reference
        
        # Testar referência direta
        assert get_schema_reference({"$ref": "#/components/schemas/Nicho"}) == "Nicho"
        
        # Testar array de referência
        array_ref = {
            "type": "array",
            "items": {"$ref": "#/components/schemas/Categoria"}
        }
        assert get_schema_reference(array_ref) == "Categoria[]"
        
        # Testar schema sem referência
        assert get_schema_reference({"type": "string"}) == "any"

    def test_openapi_endpoint_registration(self):
        """Testa se endpoints OpenAPI estão registrados"""
        from backend.app.api.openapi import openapi_bp
        
        # Verificar se blueprint foi criado
        assert openapi_bp is not None
        assert openapi_bp.url_prefix == '/api/docs'
        
        # Verificar se rotas estão registradas
        routes = [rule.rule for rule in openapi_bp.url_map.iter_rules()]
        
        expected_routes = [
            '/api/docs/openapi.json',
            '/api/docs/swagger',
            '/api/docs/typescript'
        ]
        
        for route in expected_routes:
            assert route in routes, f"Rota {route} não encontrada"

    def test_openapi_json_endpoint(self):
        """Testa endpoint de especificação OpenAPI JSON"""
        from backend.app.api.openapi import get_openapi_spec
        
        # Simular request
        with patch('flask.jsonify') as mock_jsonify:
            get_openapi_spec()
            mock_jsonify.assert_called_once()

    def test_typescript_endpoint(self):
        """Testa endpoint de geração de tipos TypeScript"""
        from backend.app.api.openapi import generate_typescript_types
        
        # Simular request
        with patch('flask.jsonify') as mock_jsonify:
            generate_typescript_types()
            mock_jsonify.assert_called_once()
            
            # Verificar se retorna TypeScript
            call_args = mock_jsonify.call_args[0][0]
            assert "typescript" in call_args
            assert "generated_at" in call_args
            assert "version" in call_args

    def test_swagger_ui_endpoint(self):
        """Testa endpoint da interface Swagger UI"""
        from backend.app.api.openapi import get_swagger_ui
        
        # Simular request
        swagger_html = get_swagger_ui()
        
        # Verificar se retorna HTML
        assert swagger_html is not None
        assert "<!DOCTYPE html>" in swagger_html
        assert "Swagger UI" in swagger_html
        assert "swagger-ui" in swagger_html

    def test_npm_scripts_availability(self):
        """Testa se scripts npm estão disponíveis"""
        # Verificar se package.json tem scripts necessários
        package_json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'package.json')
        
        if os.path.exists(package_json_path):
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            scripts = package_data.get('scripts', {})
            
            # Verificar scripts de geração de tipos
            assert 'generate-types' in scripts
            assert 'generate-types:dev' in scripts
            assert 'generate-types:watch' in scripts
            assert 'api:docs' in scripts
            assert 'api:types' in scripts

    def test_openapi_schema_validation(self):
        """Testa validação do schema OpenAPI"""
        from backend.app.api.openapi import OPENAPI_SCHEMA
        
        # Verificar se todos os paths têm pelo menos um método
        for path, methods in OPENAPI_SCHEMA["paths"].items():
            assert len(methods) > 0, f"Path {path} não tem métodos definidos"
            
            # Verificar se métodos são válidos
            valid_methods = ["get", "post", "put", "delete", "patch"]
            for method in methods:
                assert method.lower() in valid_methods, f"Método {method} inválido em {path}"

    def test_openapi_security_schemes(self):
        """Testa esquemas de segurança OpenAPI"""
        from backend.app.api.openapi import OPENAPI_SCHEMA
        
        security_schemes = OPENAPI_SCHEMA["components"]["securitySchemes"]
        
        # Verificar se bearerAuth está definido
        assert "bearerAuth" in security_schemes
        
        bearer_auth = security_schemes["bearerAuth"]
        assert bearer_auth["type"] == "http"
        assert bearer_auth["scheme"] == "bearer"
        assert bearer_auth["bearerFormat"] == "JWT"

    def test_openapi_tags_organization(self):
        """Testa organização de tags OpenAPI"""
        from backend.app.api.openapi import OPENAPI_SCHEMA
        
        tags = OPENAPI_SCHEMA["tags"]
        
        # Verificar se tags estão definidas
        expected_tags = [
            "Nichos",
            "Categorias", 
            "Execuções",
            "Execuções Agendadas",
            "Logs",
            "Dashboard",
            "Clusters",
            "Autenticação"
        ]
        
        tag_names = [tag["name"] for tag in tags]
        for expected_tag in expected_tags:
            assert expected_tag in tag_names, f"Tag {expected_tag} não encontrada"

    def test_typescript_generation_error_handling(self):
        """Testa tratamento de erros na geração de tipos"""
        from backend.app.api.openapi import generate_typescript_types
        
        # Simular erro na geração
        with patch('backend.app.api.openapi.generate_typescript_from_openapi') as mock_generate:
            mock_generate.side_effect = Exception("Erro de teste")
            
            with patch('flask.jsonify') as mock_jsonify:
                generate_typescript_types()
                
                # Verificar se erro foi tratado
                call_args = mock_jsonify.call_args[0][0]
                assert "error" in call_args
                assert "Erro ao gerar tipos TypeScript" in call_args["error"]

    def test_openapi_schema_completeness(self):
        """Testa completude do schema OpenAPI"""
        from backend.app.api.openapi import OPENAPI_SCHEMA
        
        # Verificar se todos os schemas têm propriedades
        schemas = OPENAPI_SCHEMA["components"]["schemas"]
        
        for schema_name, schema_def in schemas.items():
            if "properties" in schema_def:
                # Verificar se propriedades não estão vazias
                assert len(schema_def["properties"]) > 0, f"Schema {schema_name} não tem propriedades"
                
                # Verificar se propriedades obrigatórias estão definidas
                if "required" in schema_def:
                    for required_prop in schema_def["required"]:
                        assert required_prop in schema_def["properties"], f"Propriedade obrigatória {required_prop} não definida em {schema_name}"

    def test_typescript_generation_format(self):
        """Testa formato da geração de tipos TypeScript"""
        from backend.app.api.openapi import generate_typescript_from_openapi, OPENAPI_SCHEMA
        
        typescript_code = generate_typescript_from_openapi(OPENAPI_SCHEMA)
        
        # Verificar cabeçalho
        assert "// Generated TypeScript types from OpenAPI specification" in typescript_code
        assert "// Omni Keywords Finder API" in typescript_code
        assert "// Generated at:" in typescript_code
        
        # Verificar se interfaces estão bem formatadas
        assert "export interface" in typescript_code
        assert "export type" in typescript_code
        
        # Verificar se não há erros de sintaxe básicos
        assert "{{" in typescript_code  # Interfaces devem ter chaves
        assert "}}" in typescript_code


if __name__ == '__main__':
    pytest.main([__file__]) 