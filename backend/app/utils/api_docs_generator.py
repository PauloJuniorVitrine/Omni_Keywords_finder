"""
Gerador Automático de Documentação OpenAPI - Omni Keywords Finder
Gera documentação OpenAPI baseada nos endpoints e schemas existentes
Prompt: Documentação de API
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
"""

import os
import inspect
import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import json
from datetime import datetime
from flask import Blueprint
from pydantic import BaseModel
import re

class APIDocsGenerator:
    """Gerador automático de documentação OpenAPI"""
    
    def __init__(self, app_dir: str = "backend/app"):
        self.app_dir = Path(app_dir)
        self.api_dir = self.app_dir / "api"
        self.schemas_dir = self.app_dir / "schemas"
        self.openapi_spec = self._create_base_spec()
        
    def _create_base_spec(self) -> Dict[str, Any]:
        """Cria especificação OpenAPI base"""
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "Omni Keywords Finder API",
                "description": self._get_api_description(),
                "version": "2.0.0",
                "contact": {
                    "name": "Omni Keywords Finder Support",
                    "email": "support@omnikeywordsfinder.com",
                    "url": "https://omnikeywordsfinder.com/support"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            "servers": [
                {
                    "url": "https://api.omnikeywordsfinder.com/v1",
                    "description": "Production server"
                },
                {
                    "url": "https://staging-api.omnikeywordsfinder.com/v1",
                    "description": "Staging server"
                },
                {
                    "url": "http://localhost:8000/v1",
                    "description": "Local development server"
                }
            ],
            "security": [
                {"bearerAuth": []}
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT token obtido através do endpoint /auth/login"
                    }
                },
                "schemas": {},
                "responses": {
                    "UnauthorizedError": {
                        "description": "Não autorizado",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "ValidationError": {
                        "description": "Dados de entrada inválidos",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ValidationError"
                                }
                            }
                        }
                    },
                    "InternalServerError": {
                        "description": "Erro interno do servidor",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "RateLimitError": {
                        "description": "Limite de taxa excedido",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                }
            },
            "tags": []
        }
    
    def _get_api_description(self) -> str:
        """Retorna descrição detalhada da API"""
        return """
# Omni Keywords Finder API v2.0.0

API completa para o sistema Omni Keywords Finder - uma plataforma avançada de análise e descoberta de palavras-chave.

## Funcionalidades Principais

### 🔐 Autenticação e Autorização
- Autenticação JWT Bearer Token
- Sistema RBAC (Role-Based Access Control)
- OAuth2 com Google e GitHub
- Rate limiting por usuário e endpoint

### 📊 Execuções e Análises
- Execução de prompts personalizados
- Processamento em lote de palavras-chave
- Análise semântica avançada
- Clustering inteligente de resultados

### 💳 Sistema de Pagamentos
- Integração com Stripe
- Múltiplos métodos de pagamento (cartão, PIX, boleto)
- Webhooks seguros para notificações
- Sistema de reembolsos

### 🔗 Consumo Externo
- APIs para integração com sistemas externos
- Rate limiting diferenciado por tipo de cliente
- Validação robusta de entrada
- Logs de segurança estruturados

### 📈 Métricas e Auditoria
- Métricas de negócio em tempo real
- Sistema de auditoria completo
- Relatórios exportáveis
- Dashboards interativos

### 🛡️ Segurança
- Validação e sanitização de entrada
- Prevenção de ataques (XSS, SQLi, CSRF)
- Logs de segurança estruturados
- Monitoramento de anomalias

## Autenticação

Esta API utiliza autenticação JWT Bearer Token. Para obter um token:

1. Faça login através do endpoint `/auth/login`
2. Use o token retornado no header `Authorization: Bearer <token>`

## Rate Limiting

- **Usuários Free**: 100 requests/hora
- **Usuários Basic**: 1.000 requests/hora
- **Usuários Premium**: 10.000 requests/hora
- **Usuários Enterprise**: 100.000 requests/hora

## Códigos de Erro Padronizados

Todos os endpoints retornam respostas de erro padronizadas com:
- `error_code`: Código único do erro
- `message`: Descrição humanamente legível
- `details`: Detalhes técnicos (quando aplicável)
- `timestamp`: Timestamp ISO 8601
- `request_id`: ID único da requisição

## Suporte

- **Email**: support@omnikeywordsfinder.com
- **Documentação**: https://docs.omnikeywordsfinder.com
- **Status**: https://status.omnikeywordsfinder.com
- **GitHub**: https://github.com/omnikeywordsfinder/api

## Changelog

### v2.0.0 (2025-01-27)
- ✅ Sistema de tratamento de erros padronizado
- ✅ Documentação OpenAPI completa
- ✅ Schemas Pydantic para todos os endpoints
- ✅ Middleware de segurança aprimorado
- ✅ Logs estruturados e auditoria
- ✅ Rate limiting inteligente
- ✅ Validação robusta de entrada
"""
    
    def generate_documentation(self) -> Dict[str, Any]:
        """Gera documentação OpenAPI completa"""
        print("🔍 Analisando endpoints da API...")
        
        # Analisar blueprints da API
        self._analyze_api_blueprints()
        
        # Analisar schemas Pydantic
        self._analyze_pydantic_schemas()
        
        # Adicionar schemas de erro padronizados
        self._add_error_schemas()
        
        # Adicionar tags organizadas
        self._add_organized_tags()
        
        print(f"✅ Documentação gerada com {len(self.openapi_spec['paths'])} endpoints")
        return self.openapi_spec
    
    def _analyze_api_blueprints(self):
        """Analisa blueprints da API para extrair endpoints"""
        if not self.api_dir.exists():
            print(f"⚠️ Diretório de API não encontrado: {self.api_dir}")
            return
        
        # Listar arquivos de API
        api_files = list(self.api_dir.glob("*.py"))
        
        for api_file in api_files:
            if api_file.name.startswith("__"):
                continue
                
            print(f"📄 Analisando: {api_file.name}")
            self._analyze_api_file(api_file)
    
    def _analyze_api_file(self, api_file: Path):
        """Analisa arquivo de API individual"""
        try:
            # Importar módulo dinamicamente
            module_name = f"backend.app.api.{api_file.stem}"
            module = importlib.import_module(module_name)
            
            # Encontrar blueprints
            blueprints = []
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, Blueprint):
                    blueprints.append(obj)
            
            # Analisar cada blueprint
            for blueprint in blueprints:
                self._analyze_blueprint(blueprint)
                
        except Exception as e:
            print(f"❌ Erro ao analisar {api_file.name}: {e}")
    
    def _analyze_blueprint(self, blueprint: Blueprint):
        """Analisa blueprint para extrair endpoints"""
        blueprint_name = blueprint.name
        url_prefix = blueprint.url_prefix or ""
        
        print(f"  🔗 Blueprint: {blueprint_name} (prefix: {url_prefix})")
        
        # Analisar rotas do blueprint
        for rule in blueprint.url_map.iter_rules():
            endpoint = rule.endpoint
            methods = list(rule.methods - {'HEAD', 'OPTIONS'})
            
            # Obter função do endpoint
            view_func = blueprint.view_functions.get(endpoint)
            if not view_func:
                continue
            
            # Analisar função do endpoint
            self._analyze_endpoint_function(view_func, rule, methods, url_prefix)
    
    def _analyze_endpoint_function(self, func, rule, methods: List[str], url_prefix: str):
        """Analisa função de endpoint para extrair documentação"""
        # Obter docstring
        docstring = func.__doc__ or ""
        
        # Extrair informações do docstring
        endpoint_info = self._parse_docstring(docstring)
        
        # Construir path completo
        full_path = f"{url_prefix}{rule.rule}"
        
        # Adicionar ao OpenAPI spec
        if full_path not in self.openapi_spec["paths"]:
            self.openapi_spec["paths"][full_path] = {}
        
        for method in methods:
            method_lower = method.lower()
            
            # Criar especificação do endpoint
            endpoint_spec = self._create_endpoint_spec(
                func, method_lower, endpoint_info, full_path
            )
            
            self.openapi_spec["paths"][full_path][method_lower] = endpoint_spec
    
    def _parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """Extrai informações do docstring do endpoint"""
        info = {
            "summary": "",
            "description": "",
            "tags": [],
            "request_body": None,
            "responses": {}
        }
        
        if not docstring:
            return info
        
        lines = docstring.strip().split('\n')
        
        # Primeira linha como summary
        if lines:
            info["summary"] = lines[0].strip()
        
        # Procurar por tags
        for line in lines:
            if line.strip().startswith("tags:"):
                tags_str = line.split(":", 1)[1].strip()
                info["tags"] = [tag.strip() for tag in tags_str.split(",")]
                break
        
        # Procurar por requestBody
        for line in lines:
            if "requestBody:" in line:
                info["request_body"] = self._parse_request_body(lines)
                break
        
        # Procurar por responses
        for line in lines:
            if "responses:" in line:
                info["responses"] = self._parse_responses(lines)
                break
        
        return info
    
    def _parse_request_body(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Extrai especificação do request body do docstring"""
        # Implementação simplificada - em produção seria mais robusta
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object"
                    }
                }
            }
        }
    
    def _parse_responses(self, lines: List[str]) -> Dict[str, Any]:
        """Extrai especificações de resposta do docstring"""
        responses = {}
        
        # Respostas padrão
        responses["200"] = {
            "description": "Sucesso",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object"
                    }
                }
            }
        }
        
        responses["400"] = {
            "$ref": "#/components/responses/ValidationError"
        }
        
        responses["401"] = {
            "$ref": "#/components/responses/UnauthorizedError"
        }
        
        responses["500"] = {
            "$ref": "#/components/responses/InternalServerError"
        }
        
        return responses
    
    def _create_endpoint_spec(self, func, method: str, endpoint_info: Dict[str, Any], path: str) -> Dict[str, Any]:
        """Cria especificação completa do endpoint"""
        # Determinar tag baseada no path
        tag = self._determine_tag_from_path(path)
        
        spec = {
            "tags": [tag],
            "summary": endpoint_info.get("summary", f"{method.upper()} {path}"),
            "description": endpoint_info.get("description", ""),
            "operationId": f"{method}_{path.replace('/', '_').replace('-', '_')}",
            "responses": endpoint_info.get("responses", {})
        }
        
        # Adicionar request body se necessário
        if method in ["post", "put", "patch"] and endpoint_info.get("request_body"):
            spec["requestBody"] = endpoint_info["request_body"]
        
        # Adicionar parâmetros de path
        path_params = self._extract_path_parameters(path)
        if path_params:
            spec["parameters"] = path_params
        
        # Adicionar segurança se necessário
        if self._requires_auth(path, method):
            spec["security"] = [{"bearerAuth": []}]
        
        return spec
    
    def _determine_tag_from_path(self, path: str) -> str:
        """Determina tag baseada no path do endpoint"""
        if path.startswith("/auth"):
            return "Authentication"
        elif path.startswith("/execucoes"):
            return "Executions"
        elif path.startswith("/payments"):
            return "Payments"
        elif path.startswith("/rbac"):
            return "RBAC"
        elif path.startswith("/auditoria"):
            return "Audit"
        elif path.startswith("/business_metrics"):
            return "Business Metrics"
        elif path.startswith("/consumo_externo"):
            return "External Consumption"
        elif path.startswith("/webhooks"):
            return "Webhooks"
        else:
            return "General"
    
    def _extract_path_parameters(self, path: str) -> List[Dict[str, Any]]:
        """Extrai parâmetros de path do endpoint"""
        params = []
        
        # Procurar por parâmetros como <int:user_id>
        matches = re.findall(r'<(\w+):(\w+)>', path)
        
        for param_type, param_name in matches:
            param_spec = {
                "name": param_name,
                "in": "path",
                "required": True,
                "description": f"{param_name} identifier"
            }
            
            if param_type == "int":
                param_spec["schema"] = {"type": "integer"}
            elif param_type == "float":
                param_spec["schema"] = {"type": "number", "format": "float"}
            else:
                param_spec["schema"] = {"type": "string"}
            
            params.append(param_spec)
        
        return params
    
    def _requires_auth(self, path: str, method: str) -> bool:
        """Determina se endpoint requer autenticação"""
        # Endpoints que não requerem auth
        public_endpoints = [
            "/auth/login",
            "/auth/register",
            "/auth/oauth2/login",
            "/auth/oauth2/callback",
            "/health",
            "/docs"
        ]
        
        return path not in public_endpoints
    
    def _analyze_pydantic_schemas(self):
        """Analisa schemas Pydantic para adicionar ao OpenAPI"""
        if not self.schemas_dir.exists():
            print(f"⚠️ Diretório de schemas não encontrado: {self.schemas_dir}")
            return
        
        print("📋 Analisando schemas Pydantic...")
        
        # Listar arquivos de schema
        schema_files = list(self.schemas_dir.glob("*.py"))
        
        for schema_file in schema_files:
            if schema_file.name.startswith("__"):
                continue
                
            print(f"  📄 Analisando schema: {schema_file.name}")
            self._analyze_schema_file(schema_file)
    
    def _analyze_schema_file(self, schema_file: Path):
        """Analisa arquivo de schema individual"""
        try:
            # Importar módulo dinamicamente
            module_name = f"backend.app.schemas.{schema_file.stem}"
            module = importlib.import_module(module_name)
            
            # Encontrar classes que herdam de BaseModel
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseModel) and 
                    obj != BaseModel):
                    self._add_pydantic_schema(name, obj)
                    
        except Exception as e:
            print(f"❌ Erro ao analisar schema {schema_file.name}: {e}")
    
    def _add_pydantic_schema(self, name: str, schema_class):
        """Adiciona schema Pydantic ao OpenAPI spec"""
        try:
            # Converter schema Pydantic para OpenAPI
            schema_dict = schema_class.model_json_schema()
            
            # Adicionar ao components.schemas
            self.openapi_spec["components"]["schemas"][name] = schema_dict
            
        except Exception as e:
            print(f"❌ Erro ao adicionar schema {name}: {e}")
    
    def _add_error_schemas(self):
        """Adiciona schemas de erro padronizados"""
        error_schemas = {
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "error_code": {
                        "type": "string",
                        "description": "Código único do erro",
                        "example": "VALIDATION_ERROR"
                    },
                    "message": {
                        "type": "string",
                        "description": "Descrição humanamente legível do erro",
                        "example": "Dados de entrada inválidos"
                    },
                    "details": {
                        "type": "object",
                        "description": "Detalhes técnicos do erro (opcional)",
                        "additionalProperties": True
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Timestamp ISO 8601 do erro",
                        "example": "2025-01-27T10:30:00Z"
                    },
                    "request_id": {
                        "type": "string",
                        "description": "ID único da requisição",
                        "example": "req_123456789"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path do endpoint",
                        "example": "/api/auth/login"
                    },
                    "method": {
                        "type": "string",
                        "description": "Método HTTP",
                        "example": "POST"
                    }
                },
                "required": ["success", "error_code", "message", "timestamp"]
            },
            "ValidationError": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "error_code": {
                        "type": "string",
                        "example": "VALIDATION_ERROR"
                    },
                    "message": {
                        "type": "string",
                        "example": "Dados de entrada inválidos"
                    },
                    "details": {
                        "type": "object",
                        "properties": {
                            "validation_errors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "field": {
                                            "type": "string",
                                            "description": "Campo com erro"
                                        },
                                        "value": {
                                            "description": "Valor fornecido"
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "Mensagem de erro"
                                        },
                                        "suggestion": {
                                            "type": "string",
                                            "description": "Sugestão de correção"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time"
                    }
                },
                "required": ["success", "error_code", "message", "timestamp"]
            }
        }
        
        for schema_name, schema_def in error_schemas.items():
            self.openapi_spec["components"]["schemas"][schema_name] = schema_def
    
    def _add_organized_tags(self):
        """Adiciona tags organizadas para a documentação"""
        tags = [
            {
                "name": "Authentication",
                "description": "Endpoints de autenticação e autorização"
            },
            {
                "name": "Executions",
                "description": "Execução de prompts e processamento de palavras-chave"
            },
            {
                "name": "Payments",
                "description": "Sistema de pagamentos e transações"
            },
            {
                "name": "RBAC",
                "description": "Controle de acesso baseado em roles"
            },
            {
                "name": "Audit",
                "description": "Sistema de auditoria e logs"
            },
            {
                "name": "Business Metrics",
                "description": "Métricas de negócio e KPIs"
            },
            {
                "name": "External Consumption",
                "description": "APIs para consumo externo"
            },
            {
                "name": "Webhooks",
                "description": "Webhooks para notificações"
            },
            {
                "name": "General",
                "description": "Endpoints gerais do sistema"
            }
        ]
        
        self.openapi_spec["tags"] = tags
    
    def save_documentation(self, output_path: str = "docs/api/swagger_generated.yaml"):
        """Salva documentação gerada em arquivo"""
        # Gerar documentação
        docs = self.generate_documentation()
        
        # Salvar em YAML
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(docs, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"✅ Documentação salva em: {output_path}")
        
        # Salvar também em JSON
        json_path = output_path.replace('.yaml', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Documentação JSON salva em: {json_path}")
        
        return output_path

def generate_api_documentation():
    """Função principal para gerar documentação da API"""
    print("🚀 Iniciando geração de documentação OpenAPI...")
    
    generator = APIDocsGenerator()
    output_path = generator.save_documentation()
    
    print(f"🎉 Documentação gerada com sucesso!")
    print(f"📁 Arquivo: {output_path}")
    
    return output_path

if __name__ == "__main__":
    generate_api_documentation() 