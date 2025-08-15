"""
📄 API Documentation Generator
🎯 Objetivo: Gerar documentação automática para GraphQL, Protobuf e OpenAPI
📊 Tracing ID: API_DOCS_GENERATOR_20250127_001
📅 Data: 2025-01-27
🔧 Status: Implementação Inicial
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIDocMetadata:
    """Metadados para documentação de API"""
    name: str
    version: str
    description: str
    file_path: str
    api_type: str  # 'graphql', 'protobuf', 'openapi'
    endpoints_count: int
    types_count: int
    generated_at: datetime


@dataclass
class GraphQLType:
    """Representação de tipo GraphQL"""
    name: str
    kind: str  # 'Object', 'Input', 'Scalar', 'Enum'
    fields: List[Dict[str, Any]]
    description: Optional[str] = None


@dataclass
class ProtobufMessage:
    """Representação de mensagem Protobuf"""
    name: str
    fields: List[Dict[str, Any]]
    description: Optional[str] = None


@dataclass
class OpenAPIEndpoint:
    """Representação de endpoint OpenAPI"""
    path: str
    method: str
    summary: str
    parameters: List[Dict[str, Any]]
    responses: Dict[str, Any]
    request_body: Optional[Dict[str, Any]] = None


class APIDocsGenerator:
    """
    Gerador de documentação para diferentes tipos de API
    Suporta GraphQL, Protobuf e OpenAPI
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.graphql_files: List[Path] = []
        self.protobuf_files: List[Path] = []
        self.openapi_files: List[Path] = []
        self.output_dir = self.base_path / "docs" / "api"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações
        self.supported_extensions = {
            'graphql': ['.graphql', '.gql'],
            'protobuf': ['.proto'],
            'openapi': ['.yaml', '.yml', '.json']
        }
        
        logger.info(f"[INFO] [APIDocsGenerator] Inicializado em {self.base_path}")
    
    def discover_api_files(self) -> Dict[str, List[Path]]:
        """
        Descobre automaticamente arquivos de API no projeto
        """
        discovered_files = {
            'graphql': [],
            'protobuf': [],
            'openapi': []
        }
        
        for root, dirs, files in os.walk(self.base_path):
            # Ignorar diretórios virtuais e cache
            dirs[:] = [data for data in dirs if not data.startswith('.') and data not in ['__pycache__', 'node_modules']]
            
            for file in files:
                file_path = Path(root) / file
                
                # Detectar GraphQL
                if file.endswith(('.graphql', '.gql')):
                    discovered_files['graphql'].append(file_path)
                
                # Detectar Protobuf
                elif file.endswith('.proto'):
                    # Filtrar apenas arquivos do projeto (não de dependências)
                    if '.venv' not in str(file_path) and 'site-packages' not in str(file_path):
                        discovered_files['protobuf'].append(file_path)
                
                # Detectar OpenAPI
                elif file.endswith(('.yaml', '.yml', '.json')):
                    if self._is_openapi_file(file_path):
                        discovered_files['openapi'].append(file_path)
        
        self.graphql_files = discovered_files['graphql']
        self.protobuf_files = discovered_files['protobuf']
        self.openapi_files = discovered_files['openapi']
        
        logger.info(f"[INFO] [APIDocsGenerator] Descobertos: "
                   f"{len(self.graphql_files)} GraphQL, "
                   f"{len(self.protobuf_files)} Protobuf, "
                   f"{len(self.openapi_files)} OpenAPI")
        
        return discovered_files
    
    def _is_openapi_file(self, file_path: Path) -> bool:
        """Verifica se arquivo é OpenAPI válido"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar se contém indicadores de OpenAPI
            openapi_indicators = [
                'openapi:',
                '"openapi":',
                'swagger:',
                '"swagger":'
            ]
            
            return any(indicator in content for indicator in openapi_indicators)
        except Exception:
            return False
    
    def generate_graphql_docs(self, file_path: Path) -> Dict[str, Any]:
        """
        Gera documentação para arquivo GraphQL
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrair queries e mutations
            queries = self._extract_graphql_operations(content, 'query')
            mutations = self._extract_graphql_operations(content, 'mutation')
            subscriptions = self._extract_graphql_operations(content, 'subscription')
            
            # Extrair tipos (simplificado)
            types = self._extract_graphql_types(content)
            
            doc_data = {
                'file_path': str(file_path),
                'api_type': 'graphql',
                'queries': queries,
                'mutations': mutations,
                'subscriptions': subscriptions,
                'types': types,
                'metadata': {
                    'queries_count': len(queries),
                    'mutations_count': len(mutations),
                    'subscriptions_count': len(subscriptions),
                    'types_count': len(types),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            logger.info(f"[INFO] [APIDocsGenerator] GraphQL docs gerados para {file_path}")
            return doc_data
            
        except Exception as e:
            logger.error(f"[ERROR] [APIDocsGenerator] Erro ao processar GraphQL {file_path}: {e}")
            return {}
    
    def _extract_graphql_operations(self, content: str, operation_type: str) -> List[Dict[str, Any]]:
        """Extrai operações GraphQL do conteúdo"""
        operations = []
        
        # Padrão para encontrar operações
        pattern = rf'{operation_type}\string_data+(\w+)\string_data*\([^)]*\)\string_data*{{([^}}]+)}}'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            operation_name = match.group(1)
            operation_body = match.group(2)
            
            # Extrair campos solicitados
            fields = self._extract_graphql_fields(operation_body)
            
            operations.append({
                'name': operation_name,
                'type': operation_type,
                'fields': fields,
                'body': operation_body.strip()
            })
        
        return operations
    
    def _extract_graphql_fields(self, body: str) -> List[str]:
        """Extrai campos de uma operação GraphQL"""
        fields = []
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('{') and not line.startswith('}'):
                # Extrair nome do campo
                field_match = re.match(r'(\w+)', line)
                if field_match:
                    fields.append(field_match.group(1))
        
        return fields
    
    def _extract_graphql_types(self, content: str) -> List[Dict[str, Any]]:
        """Extrai tipos GraphQL (simplificado)"""
        types = []
        
        # Padrão para tipos
        type_pattern = r'type\string_data+(\w+)\string_data*{([^}]+)}'
        matches = re.finditer(type_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            type_name = match.group(1)
            type_body = match.group(2)
            
            types.append({
                'name': type_name,
                'kind': 'Object',
                'fields': self._extract_graphql_fields(type_body)
            })
        
        return types
    
    def generate_protobuf_docs(self, file_path: Path) -> Dict[str, Any]:
        """
        Gera documentação para arquivo Protobuf
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrair mensagens
            messages = self._extract_protobuf_messages(content)
            
            # Extrair serviços
            services = self._extract_protobuf_services(content)
            
            # Extrair enums
            enums = self._extract_protobuf_enums(content)
            
            doc_data = {
                'file_path': str(file_path),
                'api_type': 'protobuf',
                'messages': messages,
                'services': services,
                'enums': enums,
                'metadata': {
                    'messages_count': len(messages),
                    'services_count': len(services),
                    'enums_count': len(enums),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            logger.info(f"[INFO] [APIDocsGenerator] Protobuf docs gerados para {file_path}")
            return doc_data
            
        except Exception as e:
            logger.error(f"[ERROR] [APIDocsGenerator] Erro ao processar Protobuf {file_path}: {e}")
            return {}
    
    def _extract_protobuf_messages(self, content: str) -> List[Dict[str, Any]]:
        """Extrai mensagens Protobuf"""
        messages = []
        
        # Padrão para mensagens
        message_pattern = r'message\string_data+(\w+)\string_data*{([^}]+)}'
        matches = re.finditer(message_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            message_name = match.group(1)
            message_body = match.group(2)
            
            # Extrair campos
            fields = self._extract_protobuf_fields(message_body)
            
            messages.append({
                'name': message_name,
                'fields': fields
            })
        
        return messages
    
    def _extract_protobuf_fields(self, body: str) -> List[Dict[str, Any]]:
        """Extrai campos de mensagem Protobuf"""
        fields = []
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                # Padrão: tipo nome = número
                field_match = re.match(r'(\w+)\string_data+(\w+)\string_data*=\string_data*(\data+)', line)
                if field_match:
                    fields.append({
                        'type': field_match.group(1),
                        'name': field_match.group(2),
                        'number': int(field_match.group(3))
                    })
        
        return fields
    
    def _extract_protobuf_services(self, content: str) -> List[Dict[str, Any]]:
        """Extrai serviços Protobuf"""
        services = []
        
        # Padrão para serviços
        service_pattern = r'service\string_data+(\w+)\string_data*{([^}]+)}'
        matches = re.finditer(service_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            service_name = match.group(1)
            service_body = match.group(2)
            
            # Extrair métodos
            methods = self._extract_protobuf_methods(service_body)
            
            services.append({
                'name': service_name,
                'methods': methods
            })
        
        return services
    
    def _extract_protobuf_methods(self, body: str) -> List[Dict[str, Any]]:
        """Extrai métodos de serviço Protobuf"""
        methods = []
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//'):
                # Padrão: rpc nome (tipo) returns (tipo)
                method_match = re.match(r'rpc\string_data+(\w+)\string_data*\(([^)]+)\)\string_data*returns\string_data*\(([^)]+)\)', line)
                if method_match:
                    methods.append({
                        'name': method_match.group(1),
                        'input_type': method_match.group(2).strip(),
                        'output_type': method_match.group(3).strip()
                    })
        
        return methods
    
    def _extract_protobuf_enums(self, content: str) -> List[Dict[str, Any]]:
        """Extrai enums Protobuf"""
        enums = []
        
        # Padrão para enums
        enum_pattern = r'enum\string_data+(\w+)\string_data*{([^}]+)}'
        matches = re.finditer(enum_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            enum_name = match.group(1)
            enum_body = match.group(2)
            
            # Extrair valores
            values = self._extract_protobuf_enum_values(enum_body)
            
            enums.append({
                'name': enum_name,
                'values': values
            })
        
        return enums
    
    def _extract_protobuf_enum_values(self, body: str) -> List[Dict[str, Any]]:
        """Extrai valores de enum Protobuf"""
        values = []
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//'):
                # Padrão: NOME = número
                value_match = re.match(r'(\w+)\string_data*=\string_data*(\data+)', line)
                if value_match:
                    values.append({
                        'name': value_match.group(1),
                        'value': int(value_match.group(2))
                    })
        
        return values
    
    def generate_openapi_docs(self, file_path: Path) -> Dict[str, Any]:
        """
        Gera documentação para arquivo OpenAPI
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix in ['.yaml', '.yml']:
                    content = yaml.safe_load(f)
                else:
                    content = json.load(f)
            
            # Extrair informações básicas
            info = content.get('info', {})
            paths = content.get('paths', {})
            components = content.get('components', {})
            
            # Processar endpoints
            endpoints = self._extract_openapi_endpoints(paths)
            
            # Processar schemas
            schemas = self._extract_openapi_schemas(components)
            
            doc_data = {
                'file_path': str(file_path),
                'api_type': 'openapi',
                'info': info,
                'endpoints': endpoints,
                'schemas': schemas,
                'metadata': {
                    'title': info.get('title', 'Unknown API'),
                    'version': info.get('version', '1.0.0'),
                    'endpoints_count': len(endpoints),
                    'schemas_count': len(schemas),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            logger.info(f"[INFO] [APIDocsGenerator] OpenAPI docs gerados para {file_path}")
            return doc_data
            
        except Exception as e:
            logger.error(f"[ERROR] [APIDocsGenerator] Erro ao processar OpenAPI {file_path}: {e}")
            return {}
    
    def _extract_openapi_endpoints(self, paths: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai endpoints OpenAPI"""
        endpoints = []
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'parameters': operation.get('parameters', []),
                        'request_body': operation.get('requestBody'),
                        'responses': operation.get('responses', {}),
                        'tags': operation.get('tags', [])
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_openapi_schemas(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai schemas OpenAPI"""
        return components.get('schemas', {})
    
    def generate_all_docs(self) -> Dict[str, Any]:
        """
        Gera documentação para todos os tipos de API descobertos
        """
        # Descobrir arquivos
        discovered_files = self.discover_api_files()
        
        all_docs = {
            'graphql': [],
            'protobuf': [],
            'openapi': [],
            'metadata': {
                'total_files': sum(len(files) for files in discovered_files.values()),
                'generated_at': datetime.now().isoformat(),
                'generator_version': '1.0.0'
            }
        }
        
        # Processar GraphQL
        for file_path in self.graphql_files:
            doc_data = self.generate_graphql_docs(file_path)
            if doc_data:
                all_docs['graphql'].append(doc_data)
        
        # Processar Protobuf
        for file_path in self.protobuf_files:
            doc_data = self.generate_protobuf_docs(file_path)
            if doc_data:
                all_docs['protobuf'].append(doc_data)
        
        # Processar OpenAPI
        for file_path in self.openapi_files:
            doc_data = self.generate_openapi_docs(file_path)
            if doc_data:
                all_docs['openapi'].append(doc_data)
        
        # Salvar documentação
        self._save_documentation(all_docs)
        
        logger.info(f"[INFO] [APIDocsGenerator] Documentação completa gerada: "
                   f"{len(all_docs['graphql'])} GraphQL, "
                   f"{len(all_docs['protobuf'])} Protobuf, "
                   f"{len(all_docs['openapi'])} OpenAPI")
        
        return all_docs
    
    def _save_documentation(self, docs: Dict[str, Any]) -> None:
        """Salva documentação em arquivos"""
        # Salvar JSON completo
        json_file = self.output_dir / "api_documentation.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        
        # Salvar por tipo
        for api_type, type_docs in docs.items():
            if api_type != 'metadata' and type_docs:
                type_file = self.output_dir / f"{api_type}_documentation.json"
                with open(type_file, 'w', encoding='utf-8') as f:
                    json.dump(type_docs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[INFO] [APIDocsGenerator] Documentação salva em {self.output_dir}")
    
    def generate_markdown_summary(self) -> str:
        """
        Gera resumo em Markdown da documentação
        """
        docs = self.generate_all_docs()
        
        markdown = f"""# 📄 Documentação de APIs - Omni Keywords Finder

**Tracing ID**: `API_DOCS_GENERATOR_20250127_001`  
**Data**: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}  
**Versão**: 1.0

## 📊 Resumo Geral

- **Total de arquivos**: {docs['metadata']['total_files']}
- **GraphQL**: {len(docs['graphql'])} arquivos
- **Protobuf**: {len(docs['protobuf'])} arquivos  
- **OpenAPI**: {len(docs['openapi'])} arquivos

## 🔍 GraphQL

"""
        
        for doc in docs['graphql']:
            metadata = doc['metadata']
            markdown += f"""### {Path(doc['file_path']).name}

- **Queries**: {metadata['queries_count']}
- **Mutations**: {metadata['mutations_count']}
- **Subscriptions**: {metadata['subscriptions_count']}
- **Tipos**: {metadata['types_count']}

"""
        
        markdown += """## 🔧 Protobuf

"""
        
        for doc in docs['protobuf']:
            metadata = doc['metadata']
            markdown += f"""### {Path(doc['file_path']).name}

- **Mensagens**: {metadata['messages_count']}
- **Serviços**: {metadata['services_count']}
- **Enums**: {metadata['enums_count']}

"""
        
        markdown += """## 🌐 OpenAPI

"""
        
        for doc in docs['openapi']:
            metadata = doc['metadata']
            markdown += f"""### {metadata['title']} value{metadata['version']}

- **Endpoints**: {metadata['endpoints_count']}
- **Schemas**: {metadata['schemas_count']}

"""
        
        markdown += f"""
## 📁 Arquivos Gerados

- `docs/api/api_documentation.json` - Documentação completa
- `docs/api/graphql_documentation.json` - Apenas GraphQL
- `docs/api/protobuf_documentation.json` - Apenas Protobuf
- `docs/api/openapi_documentation.json` - Apenas OpenAPI

---
*Gerado automaticamente pelo APIDocsGenerator*
"""
        
        # Salvar markdown
        markdown_file = self.output_dir / "api_documentation_summary.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return markdown


def main():
    """Função principal para execução standalone"""
    generator = APIDocsGenerator()
    
    try:
        # Gerar documentação completa
        docs = generator.generate_all_docs()
        
        # Gerar resumo markdown
        summary = generator.generate_markdown_summary()
        
        print("✅ Documentação de APIs gerada com sucesso!")
        print(f"📁 Arquivos salvos em: {generator.output_dir}")
        print(f"📊 Total processado: {docs['metadata']['total_files']} arquivos")
        
    except Exception as e:
        logger.error(f"[ERROR] [APIDocsGenerator] Erro na execução: {e}")
        raise


if __name__ == "__main__":
    main() 