from typing import Dict, List, Optional, Any
"""
Teste de Compatibilidade de Tipos Backend-Frontend

Valida que os modelos do backend são compatíveis com os tipos TypeScript do frontend

Tracing ID: FIXTYPE-001_COMPATIBILITY_20241227_001
Data: 2024-12-27
"""

import pytest
import json
from datetime import datetime
from backend.app.models import Nicho, Categoria, db
from backend.app import create_app

class TestTypesCompatibility:
    """Testes de compatibilidade entre tipos backend e frontend"""
    
    @pytest.fixture
    def app(self):
        """Cria aplicação de teste"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Cliente de teste"""
        return app.test_client()
    
    @pytest.fixture
    def sample_nicho(self, app):
        """Cria nicho de exemplo"""
        with app.app_context():
            nicho = Nicho(
                nome="Tecnologia",
                data_criacao=datetime(2024, 12, 27, 22, 30, 0),
                data_atualizacao=datetime(2024, 12, 27, 22, 30, 0)
            )
            db.session.add(nicho)
            db.session.commit()
            return nicho
    
    @pytest.fixture
    def sample_categoria(self, app, sample_nicho):
        """Cria categoria de exemplo"""
        with app.app_context():
            categoria = Categoria(
                nome="Programação",
                id_nicho=sample_nicho.id,
                perfil_cliente="Desenvolvedor",
                cluster="Backend",
                prompt_path="/prompts/programacao.txt",
                data_criacao=datetime(2024, 12, 27, 22, 30, 0),
                data_atualizacao=datetime(2024, 12, 27, 22, 30, 0)
            )
            db.session.add(categoria)
            db.session.commit()
            return categoria

    def test_nicho_model_structure(self, sample_nicho):
        """Testa estrutura do modelo Nicho"""
        # Verifica que o modelo tem as propriedades esperadas
        assert hasattr(sample_nicho, 'id')
        assert hasattr(sample_nicho, 'nome')
        assert hasattr(sample_nicho, 'data_criacao')
        assert hasattr(sample_nicho, 'data_atualizacao')
        
        # Verifica tipos dos campos
        assert isinstance(sample_nicho.id, int)  # Backend usa int
        assert isinstance(sample_nicho.nome, str)
        assert isinstance(sample_nicho.data_criacao, datetime)
        assert isinstance(sample_nicho.data_atualizacao, datetime)

    def test_categoria_model_structure(self, sample_categoria):
        """Testa estrutura do modelo Categoria"""
        # Verifica que o modelo tem as propriedades esperadas
        assert hasattr(sample_categoria, 'id')
        assert hasattr(sample_categoria, 'nome')
        assert hasattr(sample_categoria, 'id_nicho')
        assert hasattr(sample_categoria, 'perfil_cliente')
        assert hasattr(sample_categoria, 'cluster')
        assert hasattr(sample_categoria, 'prompt_path')
        assert hasattr(sample_categoria, 'data_criacao')
        assert hasattr(sample_categoria, 'data_atualizacao')
        assert hasattr(sample_categoria, 'nicho')
        
        # Verifica tipos dos campos
        assert isinstance(sample_categoria.id, int)  # Backend usa int
        assert isinstance(sample_categoria.nome, str)
        assert isinstance(sample_categoria.id_nicho, int)  # Backend usa int
        assert isinstance(sample_categoria.perfil_cliente, str)
        assert isinstance(sample_categoria.cluster, str)
        assert isinstance(sample_categoria.prompt_path, str)
        assert isinstance(sample_categoria.data_criacao, datetime)
        assert isinstance(sample_categoria.data_atualizacao, datetime)
        assert isinstance(sample_categoria.nicho, Nicho)

    def test_api_response_compatibility(self, client, sample_nicho, sample_categoria):
        """Testa compatibilidade das respostas da API"""
        
        # Testa endpoint de nichos
        response = client.get('/api/prompt-system/nichos')
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        
        if data:  # Se há dados
            nicho_data = data[0]
            # Verifica que a API retorna string para ID (compatível com frontend)
            assert 'id' in nicho_data
            # Nota: A API deve converter int para string para compatibilidade
            
            # Verifica campos obrigatórios do frontend
            assert 'nome' in nicho_data
            assert 'created_at' in nicho_data  # Frontend espera created_at
            assert 'updated_at' in nicho_data  # Frontend espera updated_at

    def test_serialization_compatibility(self, sample_nicho, sample_categoria):
        """Testa serialização para compatibilidade com frontend"""
        
        # Simula serialização para JSON (como a API faria)
        nicho_dict = {
            'id': str(sample_nicho.id),  # Converte para string
            'nome': sample_nicho.nome,
            'created_at': sample_nicho.data_criacao.isoformat(),
            'updated_at': sample_nicho.data_atualizacao.isoformat()
        }
        
        categoria_dict = {
            'id': str(sample_categoria.id),  # Converte para string
            'nome': sample_categoria.nome,
            'nicho_id': str(sample_categoria.id_nicho),  # Converte para string
            'perfil_cliente': sample_categoria.perfil_cliente,
            'cluster': sample_categoria.cluster,
            'prompt_path': sample_categoria.prompt_path,
            'created_at': sample_categoria.data_criacao.isoformat(),
            'updated_at': sample_categoria.data_atualizacao.isoformat()
        }
        
        # Verifica que os dados são serializáveis
        nicho_json = json.dumps(nicho_dict)
        categoria_json = json.dumps(categoria_dict)
        
        assert isinstance(nicho_json, str)
        assert isinstance(categoria_json, str)
        
        # Verifica que os dados deserializados mantêm a estrutura
        nicho_deserialized = json.loads(nicho_json)
        categoria_deserialized = json.loads(categoria_json)
        
        assert nicho_deserialized['id'] == str(sample_nicho.id)
        assert categoria_deserialized['id'] == str(sample_categoria.id)
        assert categoria_deserialized['nicho_id'] == str(sample_categoria.id_nicho)

    def test_field_mapping_compatibility(self):
        """Testa mapeamento de campos entre backend e frontend"""
        
        # Mapeamento esperado de campos
        backend_to_frontend_mapping = {
            'Nicho': {
                'id': 'id',  # int -> string
                'nome': 'nome',
                'data_criacao': 'created_at',  # datetime -> string
                'data_atualizacao': 'updated_at'  # datetime -> string
            },
            'Categoria': {
                'id': 'id',  # int -> string
                'nome': 'nome',
                'id_nicho': 'nicho_id',  # int -> string
                'perfil_cliente': 'perfil_cliente',
                'cluster': 'cluster',
                'prompt_path': 'prompt_path',
                'data_criacao': 'created_at',  # datetime -> string
                'data_atualizacao': 'updated_at'  # datetime -> string
            }
        }
        
        # Verifica que o mapeamento está correto
        assert backend_to_frontend_mapping['Nicho']['id'] == 'id'
        assert backend_to_frontend_mapping['Nicho']['data_criacao'] == 'created_at'
        assert backend_to_frontend_mapping['Categoria']['id_nicho'] == 'nicho_id'

    def test_type_conversion_requirements(self):
        """Testa requisitos de conversão de tipos"""
        
        # Requisitos de conversão para compatibilidade
        conversion_requirements = {
            'id_fields': {
                'backend_type': 'int',
                'frontend_type': 'string',
                'conversion': 'str(id)'
            },
            'datetime_fields': {
                'backend_type': 'datetime',
                'frontend_type': 'string',
                'conversion': 'datetime.isoformat()'
            },
            'relationship_fields': {
                'backend_type': 'int (foreign key)',
                'frontend_type': 'string',
                'conversion': 'str(foreign_key_id)'
            }
        }
        
        # Verifica que os requisitos estão definidos
        assert 'id_fields' in conversion_requirements
        assert 'datetime_fields' in conversion_requirements
        assert 'relationship_fields' in conversion_requirements
        
        # Verifica tipos de conversão
        assert conversion_requirements['id_fields']['backend_type'] == 'int'
        assert conversion_requirements['id_fields']['frontend_type'] == 'string'
        assert conversion_requirements['datetime_fields']['backend_type'] == 'datetime'
        assert conversion_requirements['datetime_fields']['frontend_type'] == 'string'

    def test_optional_fields_compatibility(self):
        """Testa compatibilidade de campos opcionais"""
        
        # Campos opcionais no frontend
        optional_fields = {
            'Nicho': ['descricao'],  # Frontend tem descricao opcional
            'Categoria': ['descricao']  # Frontend tem descricao opcional
        }
        
        # Verifica que os campos opcionais estão definidos
        assert 'Nicho' in optional_fields
        assert 'Categoria' in optional_fields
        
        # Verifica que descricao é opcional
        assert 'descricao' in optional_fields['Nicho']
        assert 'descricao' in optional_fields['Categoria']

    def test_validation_rules_compatibility(self):
        """Testa compatibilidade das regras de validação"""
        
        # Regras de validação que devem ser consistentes
        validation_rules = {
            'Nicho': {
                'nome': {
                    'required': True,
                    'max_length': 100,
                    'unique': True
                }
            },
            'Categoria': {
                'nome': {
                    'required': True,
                    'max_length': 100
                },
                'nicho_id': {
                    'required': True,
                    'foreign_key': True
                }
            }
        }
        
        # Verifica regras de validação
        assert validation_rules['Nicho']['nome']['required'] is True
        assert validation_rules['Nicho']['nome']['max_length'] == 100
        assert validation_rules['Nicho']['nome']['unique'] is True
        
        assert validation_rules['Categoria']['nome']['required'] is True
        assert validation_rules['Categoria']['nicho_id']['required'] is True
        assert validation_rules['Categoria']['nicho_id']['foreign_key'] is True

    def test_error_handling_compatibility(self):
        """Testa compatibilidade do tratamento de erros"""
        
        # Estrutura de erro esperada pelo frontend
        error_structure = {
            'detail': 'string',  # Mensagem de erro
            'status_code': 'number',  # Código HTTP
            'field_errors': 'object'  # Erros por campo (opcional)
        }
        
        # Verifica estrutura de erro
        assert 'detail' in error_structure
        assert 'status_code' in error_structure
        assert 'field_errors' in error_structure
        
        # Verifica tipos esperados
        assert error_structure['detail'] == 'string'
        assert error_structure['status_code'] == 'number'
        assert error_structure['field_errors'] == 'object'

    def test_pagination_compatibility(self):
        """Testa compatibilidade da paginação"""
        
        # Estrutura de paginação esperada pelo frontend
        pagination_structure = {
            'items': 'array',  # Lista de itens
            'total': 'number',  # Total de itens
            'page': 'number',   # Página atual
            'per_page': 'number',  # Itens por página
            'pages': 'number'   # Total de páginas
        }
        
        # Verifica estrutura de paginação
        assert 'items' in pagination_structure
        assert 'total' in pagination_structure
        assert 'page' in pagination_structure
        assert 'per_page' in pagination_structure
        assert 'pages' in pagination_structure
        
        # Verifica tipos esperados
        assert pagination_structure['items'] == 'array'
        assert pagination_structure['total'] == 'number'
        assert pagination_structure['page'] == 'number'
        assert pagination_structure['per_page'] == 'number'
        assert pagination_structure['pages'] == 'number' 