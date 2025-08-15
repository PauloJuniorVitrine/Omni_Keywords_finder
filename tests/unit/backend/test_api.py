"""
Testes unitários para backend/app/api/
Tracing ID: BACKEND_TESTS_API_001_20250127
"""

import pytest
import json
from unittest.mock import patch, Mock
from flask import url_for
from backend.app.models import Nicho, Categoria, Execucao, Keyword

class TestAuthAPI:
    """Testes para APIs de autenticação."""
    
    def test_login_success(self, client):
        """Testa login bem-sucedido."""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        with patch('backend.app.api.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "user_id": 1,
                "email": "test@example.com",
                "role": "admin"
            }
            
            response = client.post('/api/auth/login', 
                                data=json.dumps(login_data),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'token' in data
            assert 'user' in data
    
    def test_login_invalid_credentials(self, client):
        """Testa login com credenciais inválidas."""
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        with patch('backend.app.api.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_register_success(self, client):
        """Testa registro bem-sucedido."""
        register_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "name": "New User"
        }
        
        with patch('backend.app.api.auth.create_user') as mock_create:
            mock_create.return_value = {
                "user_id": 2,
                "email": "newuser@example.com",
                "name": "New User"
            }
            
            response = client.post('/api/auth/register',
                                data=json.dumps(register_data),
                                content_type='application/json')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'user_id' in data
            assert 'email' in data
    
    def test_register_duplicate_email(self, client):
        """Testa registro com email duplicado."""
        register_data = {
            "email": "existing@example.com",
            "password": "password123",
            "name": "Existing User"
        }
        
        with patch('backend.app.api.auth.create_user') as mock_create:
            mock_create.side_effect = Exception("Email already exists")
            
            response = client.post('/api/auth/register',
                                data=json.dumps(register_data),
                                content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_refresh_token(self, client, auth_headers):
        """Testa refresh de token."""
        with patch('backend.app.api.auth.refresh_token') as mock_refresh:
            mock_refresh.return_value = {
                "new_token": "new.jwt.token",
                "expires_in": 3600
            }
            
            response = client.post('/api/auth/refresh',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'new_token' in data
    
    def test_logout(self, client, auth_headers):
        """Testa logout."""
        with patch('backend.app.api.auth.logout_user') as mock_logout:
            mock_logout.return_value = True
            
            response = client.post('/api/auth/logout',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data

class TestNichoAPI:
    """Testes para APIs de nichos."""
    
    def test_get_nichos(self, client, sample_nichos):
        """Testa listagem de nichos."""
        with patch('backend.app.api.nichos.get_nichos') as mock_get:
            mock_get.return_value = [
                {
                    "id": 1,
                    "nome": "Marketing Digital",
                    "descricao": "Estratégias de marketing online",
                    "ativo": True
                }
            ]
            
            response = client.get('/api/nichos')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['nome'] == "Marketing Digital"
    
    def test_get_nicho_by_id(self, client):
        """Testa busca de nicho por ID."""
        nicho_data = {
            "id": 1,
            "nome": "Marketing Digital",
            "descricao": "Estratégias de marketing online",
            "ativo": True
        }
        
        with patch('backend.app.api.nichos.get_nicho_by_id') as mock_get:
            mock_get.return_value = nicho_data
            
            response = client.get('/api/nichos/1')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == 1
            assert data['nome'] == "Marketing Digital"
    
    def test_get_nicho_not_found(self, client):
        """Testa busca de nicho inexistente."""
        with patch('backend.app.api.nichos.get_nicho_by_id') as mock_get:
            mock_get.return_value = None
            
            response = client.get('/api/nichos/999')
            assert response.status_code == 404
    
    def test_create_nicho(self, client, auth_headers):
        """Testa criação de nicho."""
        nicho_data = {
            "nome": "Novo Nicho",
            "descricao": "Descrição do novo nicho",
            "ativo": True
        }
        
        with patch('backend.app.api.nichos.create_nicho') as mock_create:
            mock_create.return_value = {
                "id": 2,
                **nicho_data
            }
            
            response = client.post('/api/nichos',
                                data=json.dumps(nicho_data),
                                content_type='application/json',
                                headers=auth_headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['nome'] == "Novo Nicho"
            assert data['id'] == 2
    
    def test_create_nicho_validation_error(self, client, auth_headers):
        """Testa criação de nicho com dados inválidos."""
        invalid_data = {
            "nome": "",  # Nome vazio
            "descricao": "Descrição válida"
        }
        
        response = client.post('/api/nichos',
                            data=json.dumps(invalid_data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_nicho(self, client, auth_headers):
        """Testa atualização de nicho."""
        update_data = {
            "nome": "Nicho Atualizado",
            "descricao": "Descrição atualizada"
        }
        
        with patch('backend.app.api.nichos.update_nicho') as mock_update:
            mock_update.return_value = {
                "id": 1,
                **update_data,
                "ativo": True
            }
            
            response = client.put('/api/nichos/1',
                               data=json.dumps(update_data),
                               content_type='application/json',
                               headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['nome'] == "Nicho Atualizado"
    
    def test_delete_nicho(self, client, auth_headers):
        """Testa exclusão de nicho."""
        with patch('backend.app.api.nichos.delete_nicho') as mock_delete:
            mock_delete.return_value = True
            
            response = client.delete('/api/nichos/1',
                                  headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_get_nicho_keywords(self, client):
        """Testa busca de keywords por nicho."""
        keywords_data = [
            {
                "id": 1,
                "palavra": "marketing digital",
                "volume": 1000,
                "competicao": "baixa"
            }
        ]
        
        with patch('backend.app.api.nichos.get_nicho_keywords') as mock_get:
            mock_get.return_value = keywords_data
            
            response = client.get('/api/nichos/1/keywords')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['palavra'] == "marketing digital"

class TestCategoriaAPI:
    """Testes para APIs de categorias."""
    
    def test_get_categorias(self, client):
        """Testa listagem de categorias."""
        with patch('backend.app.api.categorias.get_categorias') as mock_get:
            mock_get.return_value = [
                {
                    "id": 1,
                    "nome": "SEO",
                    "descricao": "Otimização para motores de busca",
                    "ativo": True
                }
            ]
            
            response = client.get('/api/categorias')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['nome'] == "SEO"
    
    def test_create_categoria(self, client, auth_headers):
        """Testa criação de categoria."""
        categoria_data = {
            "nome": "Nova Categoria",
            "descricao": "Descrição da nova categoria",
            "ativo": True
        }
        
        with patch('backend.app.api.categorias.create_categoria') as mock_create:
            mock_create.return_value = {
                "id": 2,
                **categoria_data
            }
            
            response = client.post('/api/categorias',
                                data=json.dumps(categoria_data),
                                content_type='application/json',
                                headers=auth_headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['nome'] == "Nova Categoria"
    
    def test_update_categoria(self, client, auth_headers):
        """Testa atualização de categoria."""
        update_data = {
            "nome": "Categoria Atualizada",
            "descricao": "Descrição atualizada"
        }
        
        with patch('backend.app.api.categorias.update_categoria') as mock_update:
            mock_update.return_value = {
                "id": 1,
                **update_data,
                "ativo": True
            }
            
            response = client.put('/api/categorias/1',
                               data=json.dumps(update_data),
                               content_type='application/json',
                               headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['nome'] == "Categoria Atualizada"
    
    def test_delete_categoria(self, client, auth_headers):
        """Testa exclusão de categoria."""
        with patch('backend.app.api.categorias.delete_categoria') as mock_delete:
            mock_delete.return_value = True
            
            response = client.delete('/api/categorias/1',
                                  headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data

class TestExecucaoAPI:
    """Testes para APIs de execuções."""
    
    def test_get_execucoes(self, client):
        """Testa listagem de execuções."""
        with patch('backend.app.api.execucoes.get_execucoes') as mock_get:
            mock_get.return_value = [
                {
                    "id": 1,
                    "nicho_id": 1,
                    "status": "concluido",
                    "total_keywords": 100,
                    "keywords_processadas": 100,
                    "keywords_validas": 95
                }
            ]
            
            response = client.get('/api/execucoes')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['status'] == "concluido"
    
    def test_create_execucao(self, client, auth_headers):
        """Testa criação de execução."""
        execucao_data = {
            "nicho_id": 1,
            "total_keywords": 100
        }
        
        with patch('backend.app.api.execucoes.create_execucao') as mock_create:
            mock_create.return_value = {
                "id": 1,
                **execucao_data,
                "status": "em_execucao",
                "keywords_processadas": 0,
                "keywords_validas": 0
            }
            
            response = client.post('/api/execucoes',
                                data=json.dumps(execucao_data),
                                content_type='application/json',
                                headers=auth_headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['nicho_id'] == 1
            assert data['status'] == "em_execucao"
    
    def test_get_execucao_status(self, client):
        """Testa busca de status de execução."""
        status_data = {
            "id": 1,
            "status": "em_execucao",
            "progresso": 50.0,
            "keywords_processadas": 50,
            "total_keywords": 100
        }
        
        with patch('backend.app.api.execucoes.get_execucao_status') as mock_get:
            mock_get.return_value = status_data
            
            response = client.get('/api/execucoes/1/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['progresso'] == 50.0
    
    def test_cancel_execucao(self, client, auth_headers):
        """Testa cancelamento de execução."""
        with patch('backend.app.api.execucoes.cancel_execucao') as mock_cancel:
            mock_cancel.return_value = True
            
            response = client.post('/api/execucoes/1/cancel',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
    
    def test_get_execucao_results(self, client):
        """Testa busca de resultados de execução."""
        results_data = [
            {
                "keyword": "marketing digital",
                "conteudo_gerado": "Conteúdo sobre marketing digital",
                "qualidade": 0.85
            }
        ]
        
        with patch('backend.app.api.execucoes.get_execucao_results') as mock_get:
            mock_get.return_value = results_data
            
            response = client.get('/api/execucoes/1/results')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['keyword'] == "marketing digital"

class TestKeywordAPI:
    """Testes para APIs de keywords."""
    
    def test_get_keywords(self, client):
        """Testa listagem de keywords."""
        with patch('backend.app.api.keywords.get_keywords') as mock_get:
            mock_get.return_value = [
                {
                    "id": 1,
                    "palavra": "marketing digital",
                    "volume": 1000,
                    "competicao": "baixa",
                    "cpc": 2.50
                }
            ]
            
            response = client.get('/api/keywords')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['palavra'] == "marketing digital"
    
    def test_search_keywords(self, client):
        """Testa busca de keywords."""
        search_data = {
            "query": "marketing",
            "nicho_id": 1,
            "min_volume": 500
        }
        
        with patch('backend.app.api.keywords.search_keywords') as mock_search:
            mock_search.return_value = [
                {
                    "id": 1,
                    "palavra": "marketing digital",
                    "volume": 1000,
                    "competicao": "baixa"
                }
            ]
            
            response = client.post('/api/keywords/search',
                                data=json.dumps(search_data),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
    
    def test_get_keyword_analytics(self, client):
        """Testa busca de analytics de keyword."""
        analytics_data = {
            "keyword": "marketing digital",
            "volume_trend": [1000, 1100, 1200],
            "competition_trend": ["baixa", "baixa", "média"],
            "cpc_trend": [2.50, 2.60, 2.70]
        }
        
        with patch('backend.app.api.keywords.get_keyword_analytics') as mock_get:
            mock_get.return_value = analytics_data
            
            response = client.get('/api/keywords/1/analytics')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'volume_trend' in data
            assert 'competition_trend' in data

class TestReportAPI:
    """Testes para APIs de relatórios."""
    
    def test_get_execucao_report(self, client):
        """Testa geração de relatório de execução."""
        report_data = {
            "execucao_id": 1,
            "total_keywords": 100,
            "keywords_processadas": 95,
            "keywords_validas": 90,
            "tempo_total": "2h 30m",
            "qualidade_media": 0.85
        }
        
        with patch('backend.app.api.reports.generate_execucao_report') as mock_generate:
            mock_generate.return_value = report_data
            
            response = client.get('/api/reports/execucao/1')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['total_keywords'] == 100
            assert data['qualidade_media'] == 0.85
    
    def test_get_nicho_report(self, client):
        """Testa geração de relatório de nicho."""
        report_data = {
            "nicho_id": 1,
            "total_keywords": 500,
            "execucoes_count": 5,
            "qualidade_media": 0.82,
            "tempo_medio_execucao": "3h 15m"
        }
        
        with patch('backend.app.api.reports.generate_nicho_report') as mock_generate:
            mock_generate.return_value = report_data
            
            response = client.get('/api/reports/nicho/1')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['total_keywords'] == 500
            assert data['execucoes_count'] == 5
    
    def test_export_report_csv(self, client):
        """Testa exportação de relatório em CSV."""
        csv_data = "keyword,volume,competicao,cpc\nmarketing digital,1000,baixa,2.50"
        
        with patch('backend.app.api.reports.export_report_csv') as mock_export:
            mock_export.return_value = csv_data
            
            response = client.get('/api/reports/export/1?format=csv')
            assert response.status_code == 200
            assert response.content_type == 'text/csv'
            assert 'marketing digital' in response.data.decode()
    
    def test_export_report_pdf(self, client):
        """Testa exportação de relatório em PDF."""
        pdf_data = b"%PDF-1.4\n%Test PDF content"
        
        with patch('backend.app.api.reports.export_report_pdf') as mock_export:
            mock_export.return_value = pdf_data
            
            response = client.get('/api/reports/export/1?format=pdf')
            assert response.status_code == 200
            assert response.content_type == 'application/pdf'

class TestWebhookAPI:
    """Testes para APIs de webhooks."""
    
    def test_webhook_google_search_console(self, client):
        """Testa webhook do Google Search Console."""
        webhook_data = {
            "keyword": "marketing digital",
            "volume": 1000,
            "competition": "low",
            "cpc": 2.50
        }
        
        with patch('backend.app.api.webhooks.process_gsc_webhook') as mock_process:
            mock_process.return_value = {"status": "processed"}
            
            response = client.post('/api/webhooks/gsc',
                                data=json.dumps(webhook_data),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == "processed"
    
    def test_webhook_openai(self, client):
        """Testa webhook do OpenAI."""
        webhook_data = {
            "keyword": "marketing digital",
            "conteudo_gerado": "Conteúdo sobre marketing digital",
            "qualidade": 0.85
        }
        
        with patch('backend.app.api.webhooks.process_openai_webhook') as mock_process:
            mock_process.return_value = {"status": "processed"}
            
            response = client.post('/api/webhooks/openai',
                                data=json.dumps(webhook_data),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == "processed"

class TestAPIErrorHandling:
    """Testes para tratamento de erros das APIs."""
    
    def test_400_bad_request(self, client):
        """Testa erro 400 - Bad Request."""
        invalid_data = {"invalid": "data"}
        
        response = client.post('/api/nichos',
                            data=json.dumps(invalid_data),
                            content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_401_unauthorized(self, client):
        """Testa erro 401 - Unauthorized."""
        response = client.get('/api/nichos/1')
        assert response.status_code == 401
    
    def test_403_forbidden(self, client, auth_headers):
        """Testa erro 403 - Forbidden."""
        # Simular usuário sem permissão
        with patch('backend.app.api.auth.check_permission') as mock_check:
            mock_check.return_value = False
            
            response = client.delete('/api/nichos/1',
                                  headers=auth_headers)
            
            assert response.status_code == 403
    
    def test_404_not_found(self, client):
        """Testa erro 404 - Not Found."""
        response = client.get('/api/nichos/999')
        assert response.status_code == 404
    
    def test_500_internal_server_error(self, client):
        """Testa erro 500 - Internal Server Error."""
        with patch('backend.app.api.nichos.get_nichos') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            response = client.get('/api/nichos')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

class TestAPIPerformance:
    """Testes para performance das APIs."""
    
    def test_api_response_time(self, client):
        """Testa tempo de resposta das APIs."""
        import time
        
        # Teste de health check
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.1  # Deve responder em menos de 100ms
    
    def test_api_concurrent_requests(self, client):
        """Testa requisições concorrentes."""
        import concurrent.futures
        import time
        
        def make_request():
            return client.get('/')
        
        # Fazer 5 requisições simultâneas
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in futures]
        end_time = time.time()
        
        # Todas as respostas devem ser 200
        assert all(r.status_code == 200 for r in responses)
        # Deve completar em menos de 1 segundo
        assert (end_time - start_time) < 1.0
    
    def test_api_memory_usage(self, client):
        """Testa uso de memória das APIs."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # Fazer múltiplas requisições
        for _ in range(10):
            response = client.get('/')
            assert response.status_code == 200
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Aumento de memória deve ser razoável (< 10MB)
        assert memory_increase < 10 * 1024 * 1024  # 10MB
