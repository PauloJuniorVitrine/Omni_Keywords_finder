from typing import Dict, List, Optional, Any
"""
🧪 Testes Unitários - API Documentation Generator
🎯 Objetivo: Validar funcionalidades do gerador de documentação de APIs
📊 Tracing ID: TEST_API_DOCS_GENERATOR_20250127_001
📅 Data: 2025-01-27
🔧 Status: Implementação Inicial
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

from shared.api_docs_generator import (
    APIDocsGenerator,
    APIDocMetadata,
    GraphQLType,
    ProtobufMessage,
    OpenAPIEndpoint
)


class TestAPIDocsGenerator:
    """Testes para APIDocsGenerator"""
    
    @pytest.fixture
    def temp_dir(self):
        """Cria diretório temporário para testes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Instância do gerador para testes"""
        return APIDocsGenerator(str(temp_dir))
    
    @pytest.fixture
    def sample_graphql_content(self):
        """Conteúdo de exemplo GraphQL"""
        return '''
        query GetKeywords($filtros: KeywordFilterInput) {
          keywords(filtros: $filtros) {
            id
            keyword
            volume
            dificuldade
            cpc
            categoria
            nicho
            dataColeta
            score
          }
        }

        mutation CreateNicho($input: NichoInput!) {
          createNicho(input: $input) {
            nicho {
              id
              nome
              descricao
              ativo
              dataCriacao
            }
            success
            message
          }
        }

        type Keyword {
          id: ID!
          keyword: String!
          volume: Int
          dificuldade: Float
          cpc: Float
          categoria: String
          nicho: String
          dataColeta: String
          score: Float
        }
        '''
    
    @pytest.fixture
    def sample_protobuf_content(self):
        """Conteúdo de exemplo Protobuf"""
        return '''
        syntax = "proto3";

        package omni_keywords;

        message Keyword {
          string id = 1;
          string keyword = 2;
          int32 volume = 3;
          float dificuldade = 4;
          float cpc = 5;
          string categoria = 6;
          string nicho = 7;
          string data_coleta = 8;
          float score = 9;
        }

        message Nicho {
          string id = 1;
          string nome = 2;
          string descricao = 3;
          bool ativo = 4;
          string data_criacao = 5;
        }

        service KeywordService {
          rpc GetKeywords(KeywordRequest) returns (KeywordResponse);
          rpc CreateKeyword(CreateKeywordRequest) returns (CreateKeywordResponse);
        }

        enum KeywordStatus {
          ACTIVE = 0;
          INACTIVE = 1;
          PENDING = 2;
        }
        '''
    
    @pytest.fixture
    def sample_openapi_content(self):
        """Conteúdo de exemplo OpenAPI"""
        return {
            "openapi": "3.0.1",
            "info": {
                "title": "Omni Keywords Finder API",
                "version": "1.0.0",
                "description": "API REST para governança, processamento e exportação de keywords"
            },
            "paths": {
                "/processar_keywords": {
                    "post": {
                        "summary": "Processa lista de keywords",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "keywords": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "termo": {"type": "string"},
                                                        "volume_busca": {"type": "integer"},
                                                        "cpc": {"type": "number"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Sucesso",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "keywords": {"type": "array"},
                                                "relatorio": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Keyword": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "keyword": {"type": "string"},
                            "volume": {"type": "integer"},
                            "score": {"type": "number"}
                        }
                    }
                }
            }
        }
    
    def test_init(self, temp_dir):
        """Testa inicialização do gerador"""
        generator = APIDocsGenerator(str(temp_dir))
        
        assert generator.base_path == temp_dir
        assert generator.output_dir == temp_dir / "docs" / "api"
        assert generator.graphql_files == []
        assert generator.protobuf_files == []
        assert generator.openapi_files == []
        assert generator.supported_extensions == {
            'graphql': ['.graphql', '.gql'],
            'protobuf': ['.proto'],
            'openapi': ['.yaml', '.yml', '.json']
        }
    
    def test_is_openapi_file_valid(self, generator):
        """Testa detecção de arquivo OpenAPI válido"""
        content = 'openapi: 3.0.1\ninfo:\n  title: Test API'
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = generator._is_openapi_file(Path('test.yaml'))
            assert result is True
    
    def test_is_openapi_file_invalid(self, generator):
        """Testa detecção de arquivo OpenAPI inválido"""
        content = 'This is not an OpenAPI file'
        
        with patch('builtins.open', mock_open(read_data=content)):
            result = generator._is_openapi_file(Path('test.txt'))
            assert result is False
    
    def test_is_openapi_file_error(self, generator):
        """Testa tratamento de erro na detecção OpenAPI"""
        with patch('builtins.open', side_effect=Exception("File not found")):
            result = generator._is_openapi_file(Path('nonexistent.yaml'))
            assert result is False
    
    def test_extract_graphql_operations(self, generator, sample_graphql_content):
        """Testa extração de operações GraphQL"""
        queries = generator._extract_graphql_operations(sample_graphql_content, 'query')
        mutations = generator._extract_graphql_operations(sample_graphql_content, 'mutation')
        
        assert len(queries) == 1
        assert queries[0]['name'] == 'GetKeywords'
        assert queries[0]['type'] == 'query'
        assert 'id' in queries[0]['fields']
        assert 'keyword' in queries[0]['fields']
        
        assert len(mutations) == 1
        assert mutations[0]['name'] == 'CreateNicho'
        assert mutations[0]['type'] == 'mutation'
        assert 'id' in mutations[0]['fields']
        assert 'nome' in mutations[0]['fields']
    
    def test_extract_graphql_fields(self, generator):
        """Testa extração de campos GraphQL"""
        body = '''
        id
        keyword
        volume
        dificuldade
        cpc
        categoria
        nicho
        dataColeta
        score
        '''
        
        fields = generator._extract_graphql_fields(body)
        
        expected_fields = ['id', 'keyword', 'volume', 'dificuldade', 'cpc', 'categoria', 'nicho', 'dataColeta', 'score']
        assert fields == expected_fields
    
    def test_extract_graphql_types(self, generator, sample_graphql_content):
        """Testa extração de tipos GraphQL"""
        types = generator._extract_graphql_types(sample_graphql_content)
        
        assert len(types) == 1
        assert types[0]['name'] == 'Keyword'
        assert types[0]['kind'] == 'Object'
        assert 'id' in types[0]['fields']
        assert 'keyword' in types[0]['fields']
    
    def test_generate_graphql_docs(self, generator, sample_graphql_content, temp_dir):
        """Testa geração de documentação GraphQL"""
        graphql_file = temp_dir / "test.graphql"
        with open(graphql_file, 'w') as f:
            f.write(sample_graphql_content)
        
        doc_data = generator.generate_graphql_docs(graphql_file)
        
        assert doc_data['file_path'] == str(graphql_file)
        assert doc_data['api_type'] == 'graphql'
        assert len(doc_data['queries']) == 1
        assert len(doc_data['mutations']) == 1
        assert len(doc_data['types']) == 1
        assert doc_data['metadata']['queries_count'] == 1
        assert doc_data['metadata']['mutations_count'] == 1
        assert doc_data['metadata']['types_count'] == 1
    
    def test_extract_protobuf_messages(self, generator, sample_protobuf_content):
        """Testa extração de mensagens Protobuf"""
        messages = generator._extract_protobuf_messages(sample_protobuf_content)
        
        assert len(messages) == 2
        assert messages[0]['name'] == 'Keyword'
        assert messages[1]['name'] == 'Nicho'
        
        # Verificar campos da primeira mensagem
        keyword_fields = messages[0]['fields']
        assert len(keyword_fields) == 9
        assert keyword_fields[0]['name'] == 'id'
        assert keyword_fields[0]['type'] == 'string'
        assert keyword_fields[0]['number'] == 1
    
    def test_extract_protobuf_fields(self, generator):
        """Testa extração de campos Protobuf"""
        body = '''
        string id = 1;
        string keyword = 2;
        int32 volume = 3;
        float dificuldade = 4;
        float cpc = 5;
        '''
        
        fields = generator._extract_protobuf_fields(body)
        
        assert len(fields) == 5
        assert fields[0]['type'] == 'string'
        assert fields[0]['name'] == 'id'
        assert fields[0]['number'] == 1
        assert fields[1]['type'] == 'string'
        assert fields[1]['name'] == 'keyword'
        assert fields[1]['number'] == 2
    
    def test_extract_protobuf_services(self, generator, sample_protobuf_content):
        """Testa extração de serviços Protobuf"""
        services = generator._extract_protobuf_services(sample_protobuf_content)
        
        assert len(services) == 1
        assert services[0]['name'] == 'KeywordService'
        assert len(services[0]['methods']) == 2
        
        methods = services[0]['methods']
        assert methods[0]['name'] == 'GetKeywords'
        assert methods[0]['input_type'] == 'KeywordRequest'
        assert methods[0]['output_type'] == 'KeywordResponse'
    
    def test_extract_protobuf_methods(self, generator):
        """Testa extração de métodos Protobuf"""
        body = '''
        rpc GetKeywords(KeywordRequest) returns (KeywordResponse);
        rpc CreateKeyword(CreateKeywordRequest) returns (CreateKeywordResponse);
        rpc UpdateKeyword(UpdateKeywordRequest) returns (UpdateKeywordResponse);
        '''
        
        methods = generator._extract_protobuf_methods(body)
        
        assert len(methods) == 3
        assert methods[0]['name'] == 'GetKeywords'
        assert methods[0]['input_type'] == 'KeywordRequest'
        assert methods[0]['output_type'] == 'KeywordResponse'
    
    def test_extract_protobuf_enums(self, generator, sample_protobuf_content):
        """Testa extração de enums Protobuf"""
        enums = generator._extract_protobuf_enums(sample_protobuf_content)
        
        assert len(enums) == 1
        assert enums[0]['name'] == 'KeywordStatus'
        assert len(enums[0]['values']) == 3
        
        values = enums[0]['values']
        assert values[0]['name'] == 'ACTIVE'
        assert values[0]['value'] == 0
        assert values[1]['name'] == 'INACTIVE'
        assert values[1]['value'] == 1
    
    def test_extract_protobuf_enum_values(self, generator):
        """Testa extração de valores de enum Protobuf"""
        body = '''
        ACTIVE = 0;
        INACTIVE = 1;
        PENDING = 2;
        DELETED = 3;
        '''
        
        values = generator._extract_protobuf_enum_values(body)
        
        assert len(values) == 4
        assert values[0]['name'] == 'ACTIVE'
        assert values[0]['value'] == 0
        assert values[3]['name'] == 'DELETED'
        assert values[3]['value'] == 3
    
    def test_generate_protobuf_docs(self, generator, sample_protobuf_content, temp_dir):
        """Testa geração de documentação Protobuf"""
        proto_file = temp_dir / "test.proto"
        with open(proto_file, 'w') as f:
            f.write(sample_protobuf_content)
        
        doc_data = generator.generate_protobuf_docs(proto_file)
        
        assert doc_data['file_path'] == str(proto_file)
        assert doc_data['api_type'] == 'protobuf'
        assert len(doc_data['messages']) == 2
        assert len(doc_data['services']) == 1
        assert len(doc_data['enums']) == 1
        assert doc_data['metadata']['messages_count'] == 2
        assert doc_data['metadata']['services_count'] == 1
        assert doc_data['metadata']['enums_count'] == 1
    
    def test_extract_openapi_endpoints(self, generator, sample_openapi_content):
        """Testa extração de endpoints OpenAPI"""
        paths = sample_openapi_content['paths']
        endpoints = generator._extract_openapi_endpoints(paths)
        
        assert len(endpoints) == 1
        endpoint = endpoints[0]
        assert endpoint['path'] == '/processar_keywords'
        assert endpoint['method'] == 'POST'
        assert endpoint['summary'] == 'Processa lista de keywords'
        assert 'requestBody' in endpoint
        assert 'responses' in endpoint
    
    def test_extract_openapi_schemas(self, generator, sample_openapi_content):
        """Testa extração de schemas OpenAPI"""
        components = sample_openapi_content['components']
        schemas = generator._extract_openapi_schemas(components)
        
        assert 'Keyword' in schemas
        keyword_schema = schemas['Keyword']
        assert keyword_schema['type'] == 'object'
        assert 'properties' in keyword_schema
    
    def test_generate_openapi_docs(self, generator, sample_openapi_content, temp_dir):
        """Testa geração de documentação OpenAPI"""
        openapi_file = temp_dir / "test.yaml"
        with open(openapi_file, 'w') as f:
            yaml.dump(sample_openapi_content, f)
        
        doc_data = generator.generate_openapi_docs(openapi_file)
        
        assert doc_data['file_path'] == str(openapi_file)
        assert doc_data['api_type'] == 'openapi'
        assert doc_data['info']['title'] == 'Omni Keywords Finder API'
        assert doc_data['info']['version'] == '1.0.0'
        assert len(doc_data['endpoints']) == 1
        assert len(doc_data['schemas']) == 1
        assert doc_data['metadata']['endpoints_count'] == 1
        assert doc_data['metadata']['schemas_count'] == 1
    
    def test_discover_api_files(self, generator, temp_dir):
        """Testa descoberta de arquivos de API"""
        # Criar arquivos de teste
        (temp_dir / "app" / "queries").mkdir(parents=True)
        (temp_dir / "backend" / "proto").mkdir(parents=True)
        
        # GraphQL
        graphql_file = temp_dir / "app" / "queries" / "test.graphql"
        with open(graphql_file, 'w') as f:
            f.write("query Test { id }")
        
        # Protobuf
        proto_file = temp_dir / "backend" / "proto" / "test.proto"
        with open(proto_file, 'w') as f:
            f.write("message Test { string id = 1; }")
        
        # OpenAPI
        openapi_file = temp_dir / "openapi.yaml"
        with open(openapi_file, 'w') as f:
            f.write("openapi: 3.0.1\ninfo:\n  title: Test API")
        
        discovered_files = generator.discover_api_files()
        
        assert len(discovered_files['graphql']) == 1
        assert len(discovered_files['protobuf']) == 1
        assert len(discovered_files['openapi']) == 1
        
        assert discovered_files['graphql'][0].name == 'test.graphql'
        assert discovered_files['protobuf'][0].name == 'test.proto'
        assert discovered_files['openapi'][0].name == 'openapi.yaml'
    
    def test_generate_all_docs(self, generator, temp_dir):
        """Testa geração de toda documentação"""
        # Criar arquivos de teste
        (temp_dir / "app" / "queries").mkdir(parents=True)
        
        # GraphQL
        graphql_file = temp_dir / "app" / "queries" / "test.graphql"
        with open(graphql_file, 'w') as f:
            f.write("query Test { id }")
        
        # OpenAPI
        openapi_file = temp_dir / "openapi.yaml"
        with open(openapi_file, 'w') as f:
            f.write("openapi: 3.0.1\ninfo:\n  title: Test API")
        
        all_docs = generator.generate_all_docs()
        
        assert 'graphql' in all_docs
        assert 'protobuf' in all_docs
        assert 'openapi' in all_docs
        assert 'metadata' in all_docs
        
        assert len(all_docs['graphql']) == 1
        assert len(all_docs['openapi']) == 1
        assert all_docs['metadata']['total_files'] == 2
    
    def test_save_documentation(self, generator, temp_dir):
        """Testa salvamento de documentação"""
        docs = {
            'graphql': [{'test': 'data'}],
            'openapi': [{'test': 'data'}],
            'protobuf': [],
            'metadata': {'total_files': 2}
        }
        
        generator._save_documentation(docs)
        
        # Verificar se arquivos foram criados
        assert (generator.output_dir / "api_documentation.json").exists()
        assert (generator.output_dir / "graphql_documentation.json").exists()
        assert (generator.output_dir / "openapi_documentation.json").exists()
        assert not (generator.output_dir / "protobuf_documentation.json").exists()
    
    def test_generate_markdown_summary(self, generator, temp_dir):
        """Testa geração de resumo Markdown"""
        # Criar arquivo de teste
        (temp_dir / "app" / "queries").mkdir(parents=True)
        graphql_file = temp_dir / "app" / "queries" / "test.graphql"
        with open(graphql_file, 'w') as f:
            f.write("query Test { id }")
        
        summary = generator.generate_markdown_summary()
        
        assert "Documentação de APIs - Omni Keywords Finder" in summary
        assert "GraphQL" in summary
        assert "test.graphql" in summary
        assert "Queries: 1" in summary
        
        # Verificar se arquivo foi salvo
        assert (generator.output_dir / "api_documentation_summary.md").exists()
    
    def test_generate_graphql_docs_error_handling(self, generator):
        """Testa tratamento de erro na geração GraphQL"""
        with patch('builtins.open', side_effect=Exception("File not found")):
            doc_data = generator.generate_graphql_docs(Path("nonexistent.graphql"))
            assert doc_data == {}
    
    def test_generate_protobuf_docs_error_handling(self, generator):
        """Testa tratamento de erro na geração Protobuf"""
        with patch('builtins.open', side_effect=Exception("File not found")):
            doc_data = generator.generate_protobuf_docs(Path("nonexistent.proto"))
            assert doc_data == {}
    
    def test_generate_openapi_docs_error_handling(self, generator):
        """Testa tratamento de erro na geração OpenAPI"""
        with patch('builtins.open', side_effect=Exception("File not found")):
            doc_data = generator.generate_openapi_docs(Path("nonexistent.yaml"))
            assert doc_data == {}
    
    def test_main_function(self, temp_dir):
        """Testa função main"""
        with patch('shared.api_docs_generator.APIDocsGenerator') as mock_generator:
            mock_instance = MagicMock()
            mock_generator.return_value = mock_instance
            
            mock_instance.generate_all_docs.return_value = {
                'metadata': {'total_files': 1}
            }
            mock_instance.generate_markdown_summary.return_value = "# Test"
            mock_instance.output_dir = temp_dir / "docs" / "api"
            
            from shared.api_docs_generator import main
            main()
            
            mock_instance.generate_all_docs.assert_called_once()
            mock_instance.generate_markdown_summary.assert_called_once()


class TestAPIDocMetadata:
    """Testes para APIDocMetadata"""
    
    def test_metadata_creation(self):
        """Testa criação de metadados"""
        metadata = APIDocMetadata(
            name="Test API",
            version="1.0.0",
            description="Test description",
            file_path="/test/path",
            api_type="graphql",
            endpoints_count=5,
            types_count=3,
            generated_at=datetime.now()
        )
        
        assert metadata.name == "Test API"
        assert metadata.version == "1.0.0"
        assert metadata.api_type == "graphql"
        assert metadata.endpoints_count == 5
        assert metadata.types_count == 3


class TestGraphQLType:
    """Testes para GraphQLType"""
    
    def test_graphql_type_creation(self):
        """Testa criação de tipo GraphQL"""
        fields = [{"name": "id", "type": "ID!"}]
        graphql_type = GraphQLType(
            name="TestType",
            kind="Object",
            fields=fields,
            description="Test description"
        )
        
        assert graphql_type.name == "TestType"
        assert graphql_type.kind == "Object"
        assert graphql_type.fields == fields
        assert graphql_type.description == "Test description"


class TestProtobufMessage:
    """Testes para ProtobufMessage"""
    
    def test_protobuf_message_creation(self):
        """Testa criação de mensagem Protobuf"""
        fields = [{"name": "id", "type": "string", "number": 1}]
        message = ProtobufMessage(
            name="TestMessage",
            fields=fields,
            description="Test description"
        )
        
        assert message.name == "TestMessage"
        assert message.fields == fields
        assert message.description == "Test description"


class TestOpenAPIEndpoint:
    """Testes para OpenAPIEndpoint"""
    
    def test_openapi_endpoint_creation(self):
        """Testa criação de endpoint OpenAPI"""
        endpoint = OpenAPIEndpoint(
            path="/test",
            method="GET",
            summary="Test endpoint",
            parameters=[],
            responses={},
            request_body=None
        )
        
        assert endpoint.path == "/test"
        assert endpoint.method == "GET"
        assert endpoint.summary == "Test endpoint"
        assert endpoint.parameters == []
        assert endpoint.responses == {}


if __name__ == "__main__":
    pytest.main([__file__]) 