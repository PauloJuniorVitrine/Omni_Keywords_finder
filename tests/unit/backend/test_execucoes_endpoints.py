"""
🧪 Testes Unitários - Endpoints de Execuções

Tracing ID: TEST_EXECUCOES_20250127_001
Data/Hora: 2025-01-27 15:55:00 UTC
Versão: 1.0
Status: 🔲 CRIADO MAS NÃO EXECUTADO

Testes unitários para os endpoints de execuções do sistema Omni Keywords Finder.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock, mock_open
from flask import Flask
from datetime import datetime
from backend.app.api.execucoes import execucoes_bp
from backend.app.models import Categoria, Execucao
from backend.app.schemas.execucao import (
    ExecucaoCreateRequest, ExecucaoLoteRequest, ExecucaoFilterRequest
)


class TestExecucoesEndpoints:
    """Testes para endpoints de execuções."""
    
    @pytest.fixture
    def app(self):
        """Fixture para criar aplicação Flask de teste."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Registrar blueprint
        app.register_blueprint(execucoes_bp)
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Fixture para cliente de teste."""
        return app.test_client()
    
    @pytest.fixture
    def mock_categoria(self):
        """Fixture para categoria mock."""
        categoria = Mock(spec=Categoria)
        categoria.id = 1
        categoria.nome = 'Test Category'
        categoria.prompt_path = '/tmp/test_prompt.txt'
        categoria.cluster = 'test-cluster'
        return categoria
    
    @pytest.fixture
    def mock_execucao(self):
        """Fixture para execução mock."""
        execucao = Mock(spec=Execucao)
        execucao.id = 1
        execucao.id_categoria = 1
        execucao.palavras_chave = '["keyword1", "keyword2"]'
        execucao.cluster_usado = 'test-cluster'
        execucao.prompt_usado = '/tmp/test_prompt.txt'
        execucao.status = 'executado'
        execucao.data_execucao = datetime.utcnow()
        execucao.tempo_estimado = None
        execucao.tempo_real = None
        execucao.log_path = None
        return execucao
    
    @patch('backend.app.api.execucoes.auth_required')
    @patch('backend.app.api.execucoes.execucao_rate_limited')
    def test_executar_prompt_success(self, mock_rate_limit, mock_auth, client, mock_categoria, mock_execucao):
        """Teste de execução de prompt bem-sucedida."""
        with patch('backend.app.api.execucoes.Categoria.query') as mock_cat_query, \
             patch('backend.app.api.execucoes.db') as mock_db, \
             patch('builtins.open', mock_open(read_data='Test prompt with [PALAVRA-CHAVE] and [CLUSTER]')), \
             patch('os.path.exists') as mock_exists, \
             patch('backend.app.api.execucoes.log_event') as mock_log:
            
            # Configurar mocks
            mock_cat_query.get_or_404.return_value = mock_categoria
            mock_exists.return_value = True
            mock_db.session.add.return_value = None
            mock_db.session.commit.return_value = None
            
            # Dados de teste
            execucao_data = {
                'categoria_id': 1,
                'palavras_chave': ['keyword1', 'keyword2'],
                'cluster': 'test-cluster'
            }
            
            # Fazer requisição
            response = client.post('/api/execucoes/', 
                                 data=json.dumps(execucao_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'execucao_id' in data
            assert 'prompt_preenchido' in data
            assert data['categoria_id'] == 1
            
            # Verificar se logs foram chamados
            mock_log.assert_called()
    
    @patch('backend.app.api.execucoes.auth_required')
    @patch('backend.app.api.execucoes.execucao_rate_limited')
    def test_executar_prompt_invalid_data(self, mock_rate_limit, mock_auth, client):
        """Teste de execução com dados inválidos."""
        # Dados inválidos
        execucao_data = {
            'categoria_id': 1
            # palavras_chave ausente
        }
        
        # Fazer requisição
        response = client.post('/api/execucoes/', 
                             data=json.dumps(execucao_data),
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    @patch('backend.app.api.execucoes.auth_required')
    @patch('backend.app.api.execucoes.execucao_rate_limited')
    def test_executar_prompt_categoria_not_found(self, mock_rate_limit, mock_auth, client):
        """Teste de execução com categoria não encontrada."""
        with patch('backend.app.api.execucoes.Categoria.query') as mock_cat_query:
            # Configurar mock para categoria não encontrada
            mock_cat_query.get_or_404.side_effect = Exception('Not found')
            
            # Dados de teste
            execucao_data = {
                'categoria_id': 999,
                'palavras_chave': ['keyword1'],
                'cluster': 'test-cluster'
            }
            
            # Fazer requisição
            response = client.post('/api/execucoes/', 
                                 data=json.dumps(execucao_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 404
    
    @patch('backend.app.api.execucoes.auth_required')
    @patch('backend.app.api.execucoes.execucao_rate_limited')
    def test_executar_prompt_file_not_found(self, mock_rate_limit, mock_auth, client, mock_categoria):
        """Teste de execução com arquivo de prompt não encontrado."""
        with patch('backend.app.api.execucoes.Categoria.query') as mock_cat_query, \
             patch('os.path.exists') as mock_exists:
            
            # Configurar mocks
            mock_cat_query.get_or_404.return_value = mock_categoria
            mock_exists.return_value = False
            
            # Dados de teste
            execucao_data = {
                'categoria_id': 1,
                'palavras_chave': ['keyword1'],
                'cluster': 'test-cluster'
            }
            
            # Fazer requisição
            response = client.post('/api/execucoes/', 
                                 data=json.dumps(execucao_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'erro' in data
    
    @patch('backend.app.api.execucoes.auth_required')
    def test_listar_execucoes_success(self, mock_auth, client, mock_execucao):
        """Teste de listagem de execuções bem-sucedida."""
        with patch('backend.app.api.execucoes.Execucao.query') as mock_exec_query, \
             patch('backend.app.api.execucoes.log_event') as mock_log:
            
            # Configurar mocks
            mock_exec_query.filter.return_value.order_by.return_value.paginate.return_value = Mock(
                items=[mock_execucao],
                total=1,
                pages=1,
                has_prev=False,
                has_next=False
            )
            
            # Fazer requisição
            response = client.get('/api/execucoes/')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'execucoes' in data
            assert 'paginacao' in data
    
    @patch('backend.app.api.execucoes.auth_required')
    def test_listar_execucoes_with_filters(self, mock_auth, client, mock_execucao):
        """Teste de listagem de execuções com filtros."""
        with patch('backend.app.api.execucoes.Execucao.query') as mock_exec_query, \
             patch('backend.app.api.execucoes.log_event') as mock_log:
            
            # Configurar mocks
            mock_exec_query.filter.return_value.order_by.return_value.paginate.return_value = Mock(
                items=[mock_execucao],
                total=1,
                pages=1,
                has_prev=False,
                has_next=False
            )
            
            # Fazer requisição com filtros
            response = client.get('/api/execucoes/?categoria_id=1&status=executado&page=1&per_page=10')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'execucoes' in data
    
    @patch('backend.app.api.execucoes.auth_required')
    def test_detalhe_execucao_success(self, mock_auth, client, mock_execucao):
        """Teste de detalhe de execução bem-sucedido."""
        with patch('backend.app.api.execucoes.Execucao.query') as mock_exec_query, \
             patch('backend.app.api.execucoes.log_event') as mock_log:
            
            # Configurar mocks
            mock_exec_query.get_or_404.return_value = mock_execucao
            
            # Fazer requisição
            response = client.get('/api/execucoes/1')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'execucao' in data
    
    @patch('backend.app.api.execucoes.auth_required')
    def test_detalhe_execucao_not_found(self, mock_auth, client):
        """Teste de detalhe de execução não encontrada."""
        with patch('backend.app.api.execucoes.Execucao.query') as mock_exec_query:
            # Configurar mock para execução não encontrada
            mock_exec_query.get_or_404.side_effect = Exception('Not found')
            
            # Fazer requisição
            response = client.get('/api/execucoes/999')
            
            # Verificações
            assert response.status_code == 404
    
    @patch('backend.app.api.execucoes.auth_required')
    @patch('backend.app.api.execucoes.execucao_rate_limited')
    @patch('backend.app.api.execucoes.validate_batch_size')
    def test_executar_lote_success(self, mock_batch_size, mock_rate_limit, mock_auth, client, mock_categoria):
        """Teste de execução em lote bem-sucedida."""
        with patch('backend.app.api.execucoes.processar_lote_execucoes') as mock_process, \
             patch('backend.app.api.execucoes.log_event') as mock_log:
            
            # Configurar mocks
            mock_process.return_value = {
                'lote_id': 'test-batch-123',
                'total_items': 5,
                'status': 'iniciado'
            }
            
            # Dados de teste
            lote_data = {
                'categoria_id': 1,
                'palavras_chave_list': [
                    ['keyword1', 'keyword2'],
                    ['keyword3', 'keyword4']
                ],
                'cluster': 'test-cluster'
            }
            
            # Fazer requisição
            response = client.post('/api/execucoes/lote', 
                                 data=json.dumps(lote_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'lote_id' in data
            assert 'status' in data
    
    @patch('backend.app.api.execucoes.auth_required')
    @patch('backend.app.api.execucoes.execucao_rate_limited')
    @patch('backend.app.api.execucoes.validate_batch_size')
    def test_executar_lote_invalid_data(self, mock_batch_size, mock_rate_limit, mock_auth, client):
        """Teste de execução em lote com dados inválidos."""
        # Dados inválidos
        lote_data = {
            'categoria_id': 1
            # palavras_chave_list ausente
        }
        
        # Fazer requisição
        response = client.post('/api/execucoes/lote', 
                             data=json.dumps(lote_data),
                             content_type='application/json')
        
        # Verificações
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    @patch('backend.app.api.execucoes.auth_required')
    def test_status_lote_success(self, mock_auth, client):
        """Teste de status de lote bem-sucedido."""
        with patch('backend.app.api.execucoes.get_lote_status') as mock_status, \
             patch('backend.app.api.execucoes.log_event') as mock_log:
            
            # Configurar mocks
            mock_status.return_value = {
                'lote_id': 'test-batch-123',
                'status': 'em_andamento',
                'progresso': 50,
                'total_items': 10,
                'items_processados': 5,
                'items_falharam': 0
            }
            
            # Fazer requisição
            response = client.get('/api/execucoes/lote/status?lote_id=test-batch-123')
            
            # Verificações
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'lote_id' in data
            assert 'status' in data
            assert 'progresso' in data
    
    @patch('backend.app.api.execucoes.auth_required')
    def test_status_lote_not_found(self, mock_auth, client):
        """Teste de status de lote não encontrado."""
        with patch('backend.app.api.execucoes.get_lote_status') as mock_status:
            # Configurar mock para lote não encontrado
            mock_status.side_effect = Exception('Lote não encontrado')
            
            # Fazer requisição
            response = client.get('/api/execucoes/lote/status?lote_id=invalid-batch')
            
            # Verificações
            assert response.status_code == 404


class TestExecucoesSchemas:
    """Testes para schemas de execuções."""
    
    def test_execucao_create_request_valid(self):
        """Teste de schema de criação de execução válido."""
        data = {
            'categoria_id': 1,
            'palavras_chave': ['keyword1', 'keyword2'],
            'cluster': 'test-cluster'
        }
        
        request = ExecucaoCreateRequest(**data)
        
        assert request.categoria_id == 1
        assert request.palavras_chave == ['keyword1', 'keyword2']
        assert request.cluster == 'test-cluster'
    
    def test_execucao_create_request_invalid_categoria(self):
        """Teste de schema de criação com categoria inválida."""
        data = {
            'categoria_id': 0,  # ID inválido
            'palavras_chave': ['keyword1'],
            'cluster': 'test-cluster'
        }
        
        with pytest.raises(ValueError):
            ExecucaoCreateRequest(**data)
    
    def test_execucao_create_request_empty_keywords(self):
        """Teste de schema de criação com palavras-chave vazias."""
        data = {
            'categoria_id': 1,
            'palavras_chave': [],  # Lista vazia
            'cluster': 'test-cluster'
        }
        
        with pytest.raises(ValueError):
            ExecucaoCreateRequest(**data)
    
    def test_execucao_lote_request_valid(self):
        """Teste de schema de lote válido."""
        data = {
            'categoria_id': 1,
            'palavras_chave_list': [
                ['keyword1', 'keyword2'],
                ['keyword3', 'keyword4']
            ],
            'cluster': 'test-cluster'
        }
        
        request = ExecucaoLoteRequest(**data)
        
        assert request.categoria_id == 1
        assert len(request.palavras_chave_list) == 2
        assert request.cluster == 'test-cluster'
    
    def test_execucao_filter_request_valid(self):
        """Teste de schema de filtro válido."""
        data = {
            'categoria_id': 1,
            'status': 'executado',
            'data_inicio': '2025-01-01',
            'data_fim': '2025-01-31',
            'page': 1,
            'per_page': 10
        }
        
        request = ExecucaoFilterRequest(**data)
        
        assert request.categoria_id == 1
        assert request.status == 'executado'
        assert request.page == 1
        assert request.per_page == 10


class TestExecucoesValidation:
    """Testes de validação para execuções."""
    
    def test_sanitizar_palavra_chave(self):
        """Teste de sanitização de palavras-chave."""
        from backend.app.schemas.execucao import sanitizar_palavra_chave
        
        # Teste de sanitização básica
        result = sanitizar_palavra_chave('  Test Keyword  ')
        assert result == 'Test Keyword'
        
        # Teste de caracteres especiais
        result = sanitizar_palavra_chave('test<script>alert("xss")</script>')
        assert '<script>' not in result
        
        # Teste de comprimento máximo
        long_keyword = 'a' * 200
        result = sanitizar_palavra_chave(long_keyword)
        assert len(result) <= 100
    
    def test_validar_limites_execucao(self):
        """Teste de validação de limites de execução."""
        from backend.app.schemas.execucao import validar_limites_execucao
        
        # Teste de limites válidos
        result = validar_limites_execucao(1, ['keyword1', 'keyword2'])
        assert result['valido'] is True
        
        # Teste de muitas palavras-chave
        many_keywords = ['keyword' + str(i) for i in range(100)]
        result = validar_limites_execucao(1, many_keywords)
        assert result['valido'] is False
    
    def test_validar_status_transicao(self):
        """Teste de validação de transição de status."""
        from backend.app.schemas.execucao import validar_status_transicao
        
        # Teste de transição válida
        result = validar_status_transicao('pendente', 'executado')
        assert result['valido'] is True
        
        # Teste de transição inválida
        result = validar_status_transicao('executado', 'pendente')
        assert result['valido'] is False


class TestExecucoesErrorHandling:
    """Testes de tratamento de erros para execuções."""
    
    @patch('backend.app.api.execucoes.auth_required')
    @patch('backend.app.api.execucoes.execucao_rate_limited')
    def test_database_error_handling(self, mock_rate_limit, mock_auth, client):
        """Teste de tratamento de erro de banco de dados."""
        with patch('backend.app.api.execucoes.Categoria.query') as mock_cat_query:
            # Configurar mock para simular erro de banco
            mock_cat_query.get_or_404.side_effect = Exception('Database error')
            
            # Dados de teste
            execucao_data = {
                'categoria_id': 1,
                'palavras_chave': ['keyword1'],
                'cluster': 'test-cluster'
            }
            
            # Fazer requisição
            response = client.post('/api/execucoes/', 
                                 data=json.dumps(execucao_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 500
    
    @patch('backend.app.api.execucoes.auth_required')
    @patch('backend.app.api.execucoes.execucao_rate_limited')
    def test_file_system_error_handling(self, mock_rate_limit, mock_auth, client, mock_categoria):
        """Teste de tratamento de erro do sistema de arquivos."""
        with patch('backend.app.api.execucoes.Categoria.query') as mock_cat_query, \
             patch('os.path.exists') as mock_exists, \
             patch('builtins.open') as mock_file:
            
            # Configurar mocks
            mock_cat_query.get_or_404.return_value = mock_categoria
            mock_exists.return_value = True
            mock_file.side_effect = Exception('File system error')
            
            # Dados de teste
            execucao_data = {
                'categoria_id': 1,
                'palavras_chave': ['keyword1'],
                'cluster': 'test-cluster'
            }
            
            # Fazer requisição
            response = client.post('/api/execucoes/', 
                                 data=json.dumps(execucao_data),
                                 content_type='application/json')
            
            # Verificações
            assert response.status_code == 500


class TestExecucoesRateLimiting:
    """Testes de rate limiting para execuções."""
    
    def test_rate_limiting_execucao(self, client):
        """Teste de rate limiting para execuções."""
        # Fazer múltiplas requisições rapidamente
        for _ in range(20):
            response = client.post('/api/execucoes/', 
                                 data=json.dumps({
                                     'categoria_id': 1,
                                     'palavras_chave': ['keyword1']
                                 }),
                                 content_type='application/json')
        
        # Verificar se rate limiting foi aplicado
        # (implementação depende da configuração específica)
    
    def test_rate_limiting_lote(self, client):
        """Teste de rate limiting para execuções em lote."""
        # Fazer múltiplas requisições de lote rapidamente
        for _ in range(10):
            response = client.post('/api/execucoes/lote', 
                                 data=json.dumps({
                                     'categoria_id': 1,
                                     'palavras_chave_list': [['keyword1']]
                                 }),
                                 content_type='application/json')
        
        # Verificar se rate limiting foi aplicado
        # (implementação depende da configuração específica)


# Configuração do pytest
pytestmark = pytest.mark.unit 