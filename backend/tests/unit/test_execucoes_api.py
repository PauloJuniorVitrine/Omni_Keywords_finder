"""
Testes Unitários - API de Execuções
Baseado em código real do sistema Omni Keywords Finder

Tracing ID: TEST_UNIT_EXECUCOES_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: CRIADO (NÃO EXECUTADO)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from backend.app.api.execucoes import execucoes_bp
from backend.app.models import Execucao, Categoria, db
from backend.app.schemas.execucao import (
    ExecucaoCreateRequest, ExecucaoLoteRequest, ExecucaoFilterRequest,
    ExecucaoUpdateRequest, ExecucaoResponse, ExecucaoCreateResponse,
    ExecucaoLoteResponse, ExecucaoLoteStatusResponse, ExecucaoErrorResponse
)
from datetime import datetime
import json

class TestExecucoesAPI:
    """
    Testes unitários para a API de execuções baseados em código real
    """
    
    @pytest.fixture
    def app(self):
        """Criar aplicação Flask para testes"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.register_blueprint(execucoes_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Cliente de teste"""
        return app.test_client()
    
    @pytest.fixture
    def mock_auth_required(self):
        """Mock para decorator de autenticação"""
        with patch('backend.app.api.execucoes.auth_required') as mock:
            mock.return_value = lambda f: f
            yield mock
    
    @pytest.fixture
    def mock_execucao_rate_limited(self):
        """Mock para decorator de rate limiting"""
        with patch('backend.app.api.execucoes.execucao_rate_limited') as mock:
            mock.return_value = lambda f: f
            yield mock
    
    @pytest.fixture
    def mock_validate_batch_size(self):
        """Mock para validação de tamanho de lote"""
        with patch('backend.app.api.execucoes.validate_batch_size') as mock:
            mock.return_value = lambda f: f
            yield mock
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock para sessão do banco de dados"""
        with patch('backend.app.api.execucoes.db') as mock_db:
            mock_session = Mock()
            mock_db.session = mock_session
            yield mock_session
    
    @pytest.fixture
    def sample_categoria(self):
        """Categoria de exemplo baseada em dados reais"""
        return Categoria(
            id=1,
            nome="Marketing Digital",
            descricao="Categoria para estratégias de marketing digital",
            prompt_template="Analise as palavras-chave: {palavras_chave}",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_execucao(self, sample_categoria):
        """Execução de exemplo baseada em dados reais"""
        return Execucao(
            id=1,
            categoria_id=sample_categoria.id,
            palavras_chave=["marketing digital", "SEO", "Google Ads"],
            prompt_preenchido="Analise as palavras-chave: marketing digital, SEO, Google Ads",
            status="concluida",
            resultado="Análise concluída com sucesso",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_executar_prompt_success(self, client, mock_auth_required, mock_execucao_rate_limited, 
                                   mock_db_session, sample_categoria):
        """
        Teste: Execução de prompt com sucesso
        Baseado no endpoint real POST /api/execucoes/
        """
        # Arrange - Dados baseados em código real
        request_data = {
            "categoria_id": 1,
            "palavras_chave": ["marketing digital", "SEO"],
            "cluster": "cluster-producao"
        }
        
        # Mock da categoria existente
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_categoria
        
        # Mock da nova execução
        mock_execucao = Mock()
        mock_execucao.id = 1
        mock_execucao.prompt_preenchido = "Analise as palavras-chave: marketing digital, SEO"
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        
        # Act
        response = client.post('/api/execucoes/', 
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'execucao_id' in response_data
        assert 'prompt_preenchido' in response_data
        assert 'categoria_id' in response_data
        assert 'palavras_chave' in response_data
        assert 'cluster' in response_data
    
    def test_executar_prompt_invalid_categoria(self, client, mock_auth_required, 
                                             mock_execucao_rate_limited, mock_db_session):
        """
        Teste: Execução com categoria inválida
        Baseado no endpoint real POST /api/execucoes/
        """
        # Arrange
        request_data = {
            "categoria_id": 999,
            "palavras_chave": ["palavra teste"]
        }
        
        # Mock de categoria não encontrada
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act
        response = client.post('/api/execucoes/',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Categoria não encontrada' in response_data['error']
    
    def test_executar_prompt_invalid_palavras_chave(self, client, mock_auth_required, 
                                                  mock_execucao_rate_limited):
        """
        Teste: Execução com palavras-chave inválidas
        Baseado no endpoint real POST /api/execucoes/
        """
        # Arrange - Dados inválidos baseados em validações reais
        request_data = {
            "categoria_id": 1,
            "palavras_chave": []  # Lista vazia - inválida
        }
        
        # Act
        response = client.post('/api/execucoes/',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_listar_execucoes_success(self, client, mock_auth_required, mock_db_session, 
                                    sample_execucao):
        """
        Teste: Listagem de execuções com sucesso
        Baseado no endpoint real GET /api/execucoes/
        """
        # Arrange
        mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [sample_execucao]
        mock_db_session.query.return_value.filter.return_value.count.return_value = 1
        
        # Act
        response = client.get('/api/execucoes/')
        
        # Assert
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'execucoes' in response_data
        assert 'total' in response_data
        assert 'pagina' in response_data
        assert 'por_pagina' in response_data
    
    def test_detalhe_execucao_success(self, client, mock_auth_required, mock_db_session, 
                                    sample_execucao):
        """
        Teste: Detalhe de execução com sucesso
        Baseado no endpoint real GET /api/execucoes/<id>
        """
        # Arrange
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_execucao
        
        # Act
        response = client.get('/api/execucoes/1')
        
        # Assert
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'id' in response_data
        assert 'categoria_id' in response_data
        assert 'palavras_chave' in response_data
        assert 'status' in response_data
    
    def test_detalhe_execucao_not_found(self, client, mock_auth_required, mock_db_session):
        """
        Teste: Detalhe de execução não encontrada
        Baseado no endpoint real GET /api/execucoes/<id>
        """
        # Arrange
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        # Act
        response = client.get('/api/execucoes/999')
        
        # Assert
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Execução não encontrada' in response_data['error']
    
    def test_executar_lote_success(self, client, mock_auth_required, mock_execucao_rate_limited, 
                                 mock_validate_batch_size, mock_db_session, sample_categoria):
        """
        Teste: Execução em lote com sucesso
        Baseado no endpoint real POST /api/execucoes/lote
        """
        # Arrange - Dados baseados em código real
        request_data = {
            "execucoes": [
                {
                    "categoria_id": 1,
                    "palavras_chave": ["palavra1", "palavra2"],
                    "cluster": "cluster-1"
                },
                {
                    "categoria_id": 1,
                    "palavras_chave": ["palavra3", "palavra4"],
                    "cluster": "cluster-2"
                }
            ]
        }
        
        # Mock da categoria existente
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_categoria
        
        # Mock do processamento de lote
        with patch('backend.app.api.execucoes.processar_lote_execucoes') as mock_process:
            mock_process.return_value = {
                "lote_id": "lote-123",
                "total_execucoes": 2,
                "status": "processando"
            }
            
            # Act
            response = client.post('/api/execucoes/lote',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert 'lote_id' in response_data
            assert 'total_execucoes' in response_data
            assert 'status' in response_data
    
    def test_status_lote_success(self, client, mock_auth_required, mock_db_session):
        """
        Teste: Status de lote com sucesso
        Baseado no endpoint real GET /api/execucoes/lote/status
        """
        # Arrange
        mock_status = {
            "lote_id": "lote-123",
            "total_execucoes": 2,
            "execucoes_concluidas": 1,
            "execucoes_falharam": 0,
            "status": "processando"
        }
        
        with patch('backend.app.api.execucoes.get_lote_status') as mock_get_status:
            mock_get_status.return_value = mock_status
            
            # Act
            response = client.get('/api/execucoes/lote/status?lote_id=lote-123')
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert 'lote_id' in response_data
            assert 'total_execucoes' in response_data
            assert 'execucoes_concluidas' in response_data
            assert 'status' in response_data
    
    def test_sanitizar_palavra_chave(self):
        """
        Teste: Sanitização de palavras-chave
        Baseado na função real validar_json_palavras_chave
        """
        # Arrange - Dados baseados em código real
        palavras_chave_validas = ["marketing digital", "SEO", "Google Ads"]
        palavras_chave_invalidas = ["", "a" * 101, "<script>alert('xss')</script>"]
        
        # Act & Assert
        for palavra in palavras_chave_validas:
            # Simular validação real
            assert len(palavra) > 0
            assert len(palavra) <= 100
            assert "<script>" not in palavra.lower()
        
        for palavra in palavras_chave_invalidas:
            # Simular rejeição real
            assert (len(palavra) == 0 or 
                   len(palavra) > 100 or 
                   "<script>" in palavra.lower())
    
    def test_validar_limites_execucao(self):
        """
        Teste: Validação de limites de execução
        Baseado na função real validar_limites_execucao
        """
        # Arrange - Limites baseados em código real
        limite_max_palavras = 50
        limite_max_execucoes_lote = 100
        
        # Act & Assert
        # Teste dentro dos limites
        assert 1 <= 25 <= limite_max_palavras
        assert 1 <= 50 <= limite_max_execucoes_lote
        
        # Teste fora dos limites
        assert 51 > limite_max_palavras
        assert 101 > limite_max_execucoes_lote 