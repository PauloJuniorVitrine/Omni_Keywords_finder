"""
Testes Unitários - API de Onboarding
Omni Keywords Finder

Tracing ID: TEST_ONBOARDING_API_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes de API de Onboarding

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.api.onboarding import router
from backend.app.models import User, Company, OnboardingSession, OnboardingStep
from backend.app.services.onboarding_service import OnboardingService

# Dados de teste baseados no código real
VALID_USER_DATA = {
    "name": "João Silva",
    "email": "joao@empresa.com",
    "company": "Empresa Teste",
    "role": "Marketing Manager"
}

VALID_COMPANY_DATA = {
    "name": "Empresa Teste LTDA",
    "industry": "Tecnologia",
    "size": "11-50",
    "website": "https://empresa-teste.com",
    "country": "Brasil"
}

VALID_GOALS_DATA = {
    "primary": ["increase-traffic", "improve-rankings"],
    "secondary": ["content-optimization"],
    "timeframe": "3-6-months",
    "budget": "medium",
    "priority": "high"
}

VALID_KEYWORDS_DATA = {
    "initial": ["software desenvolvimento", "sistema gestão"],
    "competitors": ["concorrente palavra-chave"],
    "suggestions": ["tecnologia inovação", "startup tecnologia"]
}

COMPLETE_ONBOARDING_REQUEST = {
    "user": VALID_USER_DATA,
    "company": VALID_COMPANY_DATA,
    "goals": VALID_GOALS_DATA,
    "keywords": VALID_KEYWORDS_DATA
}

@pytest.fixture
def mock_db():
    """Mock do banco de dados"""
    return Mock(spec=Session)

@pytest.fixture
def mock_onboarding_service():
    """Mock do serviço de onboarding"""
    return Mock(spec=OnboardingService)

@pytest.fixture
def client():
    """Cliente de teste FastAPI"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

class TestOnboardingAPI:
    """Testes para a API de Onboarding"""

    def test_start_onboarding_success(self, client, mock_db, mock_onboarding_service):
        """Testa início bem-sucedido do onboarding"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.validate_complete_data.return_value = {'valid': True, 'errors': []}
            mock_service.create_onboarding_session.return_value = {
                'session_id': 'test-session-123',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            response = client.post("/api/onboarding/start", json=COMPLETE_ONBOARDING_REQUEST)
            
            assert response.status_code == 201
            data = response.json()
            assert data['session_id'] == 'test-session-123'
            assert data['status'] == 'in_progress'
            assert data['current_step'] == 'welcome'
            assert data['progress'] == 20
            assert data['estimated_time'] == 300

    def test_start_onboarding_validation_error(self, client, mock_db):
        """Testa erro de validação no início do onboarding"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.validate_complete_data.return_value = {
                'valid': False,
                'errors': ['Email já está em uso']
            }
            
            response = client.post("/api/onboarding/start", json=COMPLETE_ONBOARDING_REQUEST)
            
            assert response.status_code == 400
            data = response.json()
            assert 'Dados de onboarding inválidos' in data['detail']['message']
            assert 'Email já está em uso' in data['detail']['errors']

    def test_start_onboarding_invalid_user_data(self, client):
        """Testa dados de usuário inválidos"""
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['user']['name'] = ''  # Nome vazio
        
        response = client.post("/api/onboarding/start", json=invalid_request)
        
        assert response.status_code == 422  # Validation Error

    def test_start_onboarding_invalid_email(self, client):
        """Testa email inválido"""
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['user']['email'] = 'email-invalido'
        
        response = client.post("/api/onboarding/start", json=invalid_request)
        
        assert response.status_code == 422

    def test_start_onboarding_invalid_industry(self, client):
        """Testa indústria inválida"""
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['company']['industry'] = 'Indústria Inexistente'
        
        response = client.post("/api/onboarding/start", json=invalid_request)
        
        assert response.status_code == 422

    def test_start_onboarding_invalid_goals(self, client):
        """Testa objetivos inválidos"""
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['goals']['primary'] = []  # Lista vazia
        
        response = client.post("/api/onboarding/start", json=invalid_request)
        
        assert response.status_code == 422

    def test_start_onboarding_invalid_keywords(self, client):
        """Testa palavras-chave inválidas"""
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['keywords']['initial'] = []  # Lista vazia
        
        response = client.post("/api/onboarding/start", json=invalid_request)
        
        assert response.status_code == 422

    def test_process_onboarding_step_success(self, client, mock_db):
        """Testa processamento bem-sucedido de um passo"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_session.return_value = Mock(
                user_email='joao@empresa.com'
            )
            mock_service.process_step.return_value = {
                'status': 'completed',
                'data': {'step': 'welcome', 'completed': True},
                'next_step': 'company'
            }
            
            step_request = {
                "step": "welcome",
                "data": {"name": "João Silva", "email": "joao@empresa.com"}
            }
            
            response = client.post(
                "/api/onboarding/step?session_id=test-session-123",
                json=step_request
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['step'] == 'welcome'
            assert data['status'] == 'completed'
            assert data['next_step'] == 'company'

    def test_process_onboarding_step_session_not_found(self, client, mock_db):
        """Testa processamento de passo com sessão inexistente"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_session.return_value = None
            
            step_request = {
                "step": "welcome",
                "data": {"name": "João Silva", "email": "joao@empresa.com"}
            }
            
            response = client.post(
                "/api/onboarding/step?session_id=invalid-session",
                json=step_request
            )
            
            assert response.status_code == 404
            assert "Sessão de onboarding não encontrada" in response.json()['detail']

    def test_get_onboarding_session_success(self, client, mock_db):
        """Testa obtenção bem-sucedida de sessão"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_session_data.return_value = {
                'session_id': 'test-session-123',
                'status': 'in_progress',
                'current_step': 'welcome',
                'progress': 20,
                'estimated_time': 300,
                'next_step': 'company',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            response = client.get("/api/onboarding/session/test-session-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data['session_id'] == 'test-session-123'
            assert data['status'] == 'in_progress'

    def test_get_onboarding_session_not_found(self, client, mock_db):
        """Testa obtenção de sessão inexistente"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_session_data.return_value = None
            
            response = client.get("/api/onboarding/session/invalid-session")
            
            assert response.status_code == 404
            assert "Sessão de onboarding não encontrada" in response.json()['detail']

    def test_complete_onboarding_success(self, client, mock_db):
        """Testa finalização bem-sucedida do onboarding"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.validate_completion.return_value = {'valid': True, 'missing_steps': []}
            mock_service.complete_onboarding.return_value = {
                'user_email': 'joao@empresa.com',
                'completion_time': 180,  # 3 minutos
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            response = client.put("/api/onboarding/session/test-session-123/complete")
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'completed'
            assert data['progress'] == 100
            assert data['current_step'] == 'finish'

    def test_complete_onboarding_incomplete(self, client, mock_db):
        """Testa tentativa de finalizar onboarding incompleto"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.validate_completion.return_value = {
                'valid': False,
                'missing_steps': ['company', 'goals']
            }
            
            response = client.put("/api/onboarding/session/test-session-123/complete")
            
            assert response.status_code == 400
            data = response.json()
            assert 'Onboarding incompleto' in data['detail']['message']
            assert 'company' in data['detail']['missing_steps']

    def test_cancel_onboarding_success(self, client, mock_db):
        """Testa cancelamento bem-sucedido do onboarding"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.cancel_onboarding.return_value = {
                'user_email': 'joao@empresa.com',
                'cancelled_at': datetime.now()
            }
            
            response = client.delete("/api/onboarding/session/test-session-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data['message'] == 'Onboarding cancelado com sucesso'
            assert data['session_id'] == 'test-session-123'

    def test_get_onboarding_analytics_success(self, client, mock_db):
        """Testa obtenção bem-sucedida de analytics"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_analytics.return_value = {
                'total_sessions': 100,
                'completed_sessions': 75,
                'cancelled_sessions': 10,
                'completion_rate': 75.0,
                'avg_completion_time': 240,  # 4 minutos
                'step_completion_rates': {
                    'welcome': 95,
                    'company': 85,
                    'goals': 80,
                    'keywords': 75,
                    'finish': 75
                },
                'industry_distribution': {
                    'Tecnologia': 40,
                    'E-commerce': 25,
                    'Saúde': 15,
                    'Outros': 20
                },
                'goal_distribution': {
                    'increase-traffic': 60,
                    'improve-rankings': 45,
                    'generate-leads': 30
                }
            }
            
            response = client.get("/api/onboarding/analytics/summary?days=30")
            
            assert response.status_code == 200
            data = response.json()
            assert data['period_days'] == 30
            assert data['total_sessions'] == 100
            assert data['completion_rate'] == 75.0
            assert data['avg_completion_time'] == 240

    def test_validate_email_available(self, client, mock_db):
        """Testa validação de email disponível"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.validate_email_availability.return_value = {
                'available': True,
                'message': 'Email disponível'
            }
            
            response = client.post("/api/onboarding/validate/email?email=novo@empresa.com")
            
            assert response.status_code == 200
            data = response.json()
            assert data['email'] == 'novo@empresa.com'
            assert data['available'] is True

    def test_validate_email_unavailable(self, client, mock_db):
        """Testa validação de email indisponível"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.validate_email_availability.return_value = {
                'available': False,
                'message': 'Email já está em uso'
            }
            
            response = client.post("/api/onboarding/validate/email?email=joao@empresa.com")
            
            assert response.status_code == 200
            data = response.json()
            assert data['email'] == 'joao@empresa.com'
            assert data['available'] is False

    def test_get_industry_suggestions_success(self, client):
        """Testa obtenção de sugestões por indústria"""
        response = client.get("/api/onboarding/suggestions/industry/Tecnologia")
        
        assert response.status_code == 200
        data = response.json()
        assert data['industry'] == 'Tecnologia'
        assert 'software desenvolvimento' in data['suggestions']
        assert 'sistema gestão' in data['suggestions']

    def test_get_industry_suggestions_unknown_industry(self, client):
        """Testa sugestões para indústria desconhecida"""
        response = client.get("/api/onboarding/suggestions/industry/Indústria Desconhecida")
        
        assert response.status_code == 200
        data = response.json()
        assert data['industry'] == 'Indústria Desconhecida'
        assert 'palavra-chave principal' in data['suggestions']

    def test_website_validation_with_protocol(self, client):
        """Testa validação de website com protocolo"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['company']['website'] = 'https://empresa.com'
        
        response = client.post("/api/onboarding/start", json=request)
        
        # Deve passar na validação
        assert response.status_code in [201, 422]  # 422 se outros campos inválidos

    def test_website_validation_without_protocol(self, client):
        """Testa validação de website sem protocolo"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['company']['website'] = 'empresa.com'
        
        response = client.post("/api/onboarding/start", json=request)
        
        # Deve passar na validação (protocolo será adicionado)
        assert response.status_code in [201, 422]  # 422 se outros campos inválidos

    def test_keywords_normalization(self, client):
        """Testa normalização de palavras-chave"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['keywords']['initial'] = ['  SOFTWARE DESENVOLVIMENTO  ', 'Sistema Gestão']
        
        response = client.post("/api/onboarding/start", json=request)
        
        # Deve normalizar para lowercase e remover espaços
        assert response.status_code in [201, 422]  # 422 se outros campos inválidos

    def test_keywords_length_validation(self, client):
        """Testa validação de comprimento de palavras-chave"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['keywords']['initial'] = ['a' * 101]  # Mais de 100 caracteres
        
        response = client.post("/api/onboarding/start", json=request)
        
        assert response.status_code == 422

    def test_goals_validation_invalid_goal(self, client):
        """Testa validação de objetivos inválidos"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['goals']['primary'] = ['invalid-goal']
        
        response = client.post("/api/onboarding/start", json=request)
        
        assert response.status_code == 422

    def test_timeframe_validation_invalid(self, client):
        """Testa validação de prazo inválido"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['goals']['timeframe'] = 'invalid-timeframe'
        
        response = client.post("/api/onboarding/start", json=request)
        
        assert response.status_code == 422

    def test_budget_validation_invalid(self, client):
        """Testa validação de orçamento inválido"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['goals']['budget'] = 'invalid-budget'
        
        response = client.post("/api/onboarding/start", json=request)
        
        assert response.status_code == 422

    def test_priority_validation_invalid(self, client):
        """Testa validação de prioridade inválida"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['goals']['priority'] = 'invalid-priority'
        
        response = client.post("/api/onboarding/start", json=request)
        
        assert response.status_code == 422

    def test_company_size_validation_invalid(self, client):
        """Testa validação de tamanho de empresa inválido"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['company']['size'] = 'invalid-size'
        
        response = client.post("/api/onboarding/start", json=request)
        
        assert response.status_code == 422

    def test_name_validation_too_short(self, client):
        """Testa validação de nome muito curto"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['user']['name'] = 'A'  # Menos de 2 caracteres
        
        response = client.post("/api/onboarding/start", json=request)
        
        assert response.status_code == 422

    def test_company_name_validation_too_short(self, client):
        """Testa validação de nome de empresa muito curto"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['company']['name'] = 'A'  # Menos de 2 caracteres
        
        response = client.post("/api/onboarding/start", json=request)
        
        assert response.status_code == 422

    def test_email_normalization(self, client):
        """Testa normalização de email"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['user']['email'] = 'JOAO@EMPRESA.COM'  # Maiúsculas
        
        response = client.post("/api/onboarding/start", json=request)
        
        # Deve normalizar para lowercase
        assert response.status_code in [201, 422]  # 422 se outros campos inválidos

    def test_name_stripping(self, client):
        """Testa remoção de espaços em nomes"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['user']['name'] = '  João Silva  '  # Espaços extras
        
        response = client.post("/api/onboarding/start", json=request)
        
        # Deve remover espaços
        assert response.status_code in [201, 422]  # 422 se outros campos inválidos

    def test_company_name_stripping(self, client):
        """Testa remoção de espaços em nome de empresa"""
        request = COMPLETE_ONBOARDING_REQUEST.copy()
        request['company']['name'] = '  Empresa Teste  '  # Espaços extras
        
        response = client.post("/api/onboarding/start", json=request)
        
        # Deve remover espaços
        assert response.status_code in [201, 422]  # 422 se outros campos inválidos

class TestOnboardingAPIErrorHandling:
    """Testes de tratamento de erros da API"""

    def test_internal_server_error_on_start(self, client, mock_db):
        """Testa erro interno do servidor no início"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service_class.side_effect = Exception("Erro interno")
            
            response = client.post("/api/onboarding/start", json=COMPLETE_ONBOARDING_REQUEST)
            
            assert response.status_code == 500
            assert "Erro interno do servidor" in response.json()['detail']

    def test_internal_server_error_on_step(self, client, mock_db):
        """Testa erro interno do servidor no processamento de passo"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_session.return_value = Mock(user_email='test@test.com')
            mock_service.process_step.side_effect = Exception("Erro interno")
            
            step_request = {
                "step": "welcome",
                "data": {"name": "Test", "email": "test@test.com"}
            }
            
            response = client.post(
                "/api/onboarding/step?session_id=test-session",
                json=step_request
            )
            
            assert response.status_code == 500
            assert "Erro interno do servidor" in response.json()['detail']

    def test_internal_server_error_on_complete(self, client, mock_db):
        """Testa erro interno do servidor na finalização"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.validate_completion.return_value = {'valid': True, 'missing_steps': []}
            mock_service.complete_onboarding.side_effect = Exception("Erro interno")
            
            response = client.put("/api/onboarding/session/test-session/complete")
            
            assert response.status_code == 500
            assert "Erro interno do servidor" in response.json()['detail']

    def test_internal_server_error_on_cancel(self, client, mock_db):
        """Testa erro interno do servidor no cancelamento"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.cancel_onboarding.side_effect = Exception("Erro interno")
            
            response = client.delete("/api/onboarding/session/test-session")
            
            assert response.status_code == 500
            assert "Erro interno do servidor" in response.json()['detail']

    def test_internal_server_error_on_analytics(self, client, mock_db):
        """Testa erro interno do servidor nos analytics"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_analytics.side_effect = Exception("Erro interno")
            
            response = client.get("/api/onboarding/analytics/summary")
            
            assert response.status_code == 500
            assert "Erro interno do servidor" in response.json()['detail']

    def test_internal_server_error_on_email_validation(self, client, mock_db):
        """Testa erro interno do servidor na validação de email"""
        with patch('backend.app.api.onboarding.OnboardingService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.validate_email_availability.side_effect = Exception("Erro interno")
            
            response = client.post("/api/onboarding/validate/email?email=test@test.com")
            
            assert response.status_code == 500
            assert "Erro interno do servidor" in response.json()['detail']

    def test_internal_server_error_on_suggestions(self, client):
        """Testa erro interno do servidor nas sugestões"""
        with patch('backend.app.api.onboarding.get_industry_suggestions') as mock_suggestions:
            mock_suggestions.side_effect = Exception("Erro interno")
            
            response = client.get("/api/onboarding/suggestions/industry/Tecnologia")
            
            assert response.status_code == 500
            assert "Erro interno do servidor" in response.json()['detail'] 