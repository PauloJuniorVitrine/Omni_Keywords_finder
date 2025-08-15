"""
Testes Unitários - Serviço de Onboarding
Omni Keywords Finder

Tracing ID: TEST_ONBOARDING_SERVICE_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Testes de Serviço de Onboarding

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.services.onboarding_service import OnboardingService
from backend.app.models import User, Company, OnboardingSession, OnboardingStep
from backend.app.exceptions import OnboardingException

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
def onboarding_service(mock_db):
    """Instância do serviço de onboarding"""
    return OnboardingService(mock_db)

@pytest.fixture
def mock_user():
    """Mock de usuário"""
    user = Mock(spec=User)
    user.id = 1
    user.name = "João Silva"
    user.email = "joao@empresa.com"
    user.company = "Empresa Teste"
    user.role = "Marketing Manager"
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    return user

@pytest.fixture
def mock_company():
    """Mock de empresa"""
    company = Mock(spec=Company)
    company.id = 1
    company.name = "Empresa Teste LTDA"
    company.industry = "Tecnologia"
    company.size = "11-50"
    company.website = "https://empresa-teste.com"
    company.country = "Brasil"
    company.user_id = 1
    company.created_at = datetime.now()
    company.updated_at = datetime.now()
    return company

@pytest.fixture
def mock_session():
    """Mock de sessão de onboarding"""
    session = Mock(spec=OnboardingSession)
    session.session_id = "test-session-123"
    session.user_id = 1
    session.company_id = 1
    session.status = "in_progress"
    session.current_step = "welcome"
    session.progress = 20
    session.estimated_time = 300
    session.created_at = datetime.now()
    session.updated_at = datetime.now()
    return session

class TestOnboardingService:
    """Testes para o Serviço de Onboarding"""

    def test_validate_complete_data_success(self, onboarding_service, mock_db):
        """Testa validação bem-sucedida de dados completos"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = onboarding_service.validate_complete_data(COMPLETE_ONBOARDING_REQUEST)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_validate_complete_data_email_already_exists(self, onboarding_service, mock_db, mock_user):
        """Testa validação com email já existente"""
        # Mock para email já existente
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = onboarding_service.validate_complete_data(COMPLETE_ONBOARDING_REQUEST)
        
        assert result['valid'] is False
        assert 'Email já está em uso' in result['errors']

    def test_validate_complete_data_invalid_user_name(self, onboarding_service, mock_db):
        """Testa validação com nome de usuário inválido"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['user']['name'] = 'A'  # Nome muito curto
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Nome do usuário deve ter pelo menos 2 caracteres' in result['errors']

    def test_validate_complete_data_invalid_email(self, onboarding_service, mock_db):
        """Testa validação com email inválido"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['user']['email'] = 'email-invalido'
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Email do usuário inválido' in result['errors']

    def test_validate_complete_data_invalid_company_name(self, onboarding_service, mock_db):
        """Testa validação com nome de empresa inválido"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['company']['name'] = 'A'  # Nome muito curto
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Nome da empresa deve ter pelo menos 2 caracteres' in result['errors']

    def test_validate_complete_data_invalid_industry(self, onboarding_service, mock_db):
        """Testa validação com indústria inválida"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['company']['industry'] = 'Indústria Inexistente'
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Indústria deve ser uma das:' in result['errors'][0]

    def test_validate_complete_data_invalid_company_size(self, onboarding_service, mock_db):
        """Testa validação com tamanho de empresa inválido"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['company']['size'] = 'invalid-size'
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Tamanho deve ser um dos:' in result['errors'][0]

    def test_validate_complete_data_empty_goals(self, onboarding_service, mock_db):
        """Testa validação com objetivos vazios"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['goals']['primary'] = []
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Pelo menos um objetivo principal é obrigatório' in result['errors']

    def test_validate_complete_data_invalid_goal(self, onboarding_service, mock_db):
        """Testa validação com objetivo inválido"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['goals']['primary'] = ['invalid-goal']
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Objetivo inválido: invalid-goal' in result['errors']

    def test_validate_complete_data_invalid_timeframe(self, onboarding_service, mock_db):
        """Testa validação com prazo inválido"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['goals']['timeframe'] = 'invalid-timeframe'
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Prazo deve ser um dos:' in result['errors'][0]

    def test_validate_complete_data_invalid_budget(self, onboarding_service, mock_db):
        """Testa validação com orçamento inválido"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['goals']['budget'] = 'invalid-budget'
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Orçamento deve ser um dos:' in result['errors'][0]

    def test_validate_complete_data_invalid_priority(self, onboarding_service, mock_db):
        """Testa validação com prioridade inválida"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['goals']['priority'] = 'invalid-priority'
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Prioridade deve ser uma das:' in result['errors'][0]

    def test_validate_complete_data_empty_keywords(self, onboarding_service, mock_db):
        """Testa validação com palavras-chave vazias"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['keywords']['initial'] = []
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Pelo menos uma palavra-chave inicial é obrigatória' in result['errors']

    def test_validate_complete_data_invalid_keyword_length(self, onboarding_service, mock_db):
        """Testa validação com palavra-chave muito longa"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['keywords']['initial'] = ['a' * 101]  # Mais de 100 caracteres
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Palavras-chave não podem ter mais de 100 caracteres' in result['errors']

    def test_validate_complete_data_short_keyword(self, onboarding_service, mock_db):
        """Testa validação com palavra-chave muito curta"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        invalid_request = COMPLETE_ONBOARDING_REQUEST.copy()
        invalid_request['keywords']['initial'] = ['a']  # Menos de 2 caracteres
        
        result = onboarding_service.validate_complete_data(invalid_request)
        
        assert result['valid'] is False
        assert 'Palavras-chave devem ter pelo menos 2 caracteres' in result['errors']

    def test_create_onboarding_session_success(self, onboarding_service, mock_db, mock_user, mock_company):
        """Testa criação bem-sucedida de sessão de onboarding"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock para flush (obter ID do usuário)
        mock_db.flush.return_value = None
        
        # Mock para commit
        mock_db.commit.return_value = None
        
        result = onboarding_service.create_onboarding_session(COMPLETE_ONBOARDING_REQUEST)
        
        assert 'session_id' in result
        assert 'user_id' in result
        assert 'company_id' in result
        assert 'created_at' in result
        assert 'updated_at' in result
        
        # Verificar se os métodos do banco foram chamados
        assert mock_db.add.call_count >= 3  # User, Company, Session, Steps
        assert mock_db.commit.called

    def test_create_onboarding_session_integrity_error(self, onboarding_service, mock_db):
        """Testa criação de sessão com erro de integridade"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock para flush com erro de integridade
        mock_db.flush.side_effect = IntegrityError("", "", "")
        
        with pytest.raises(OnboardingException) as exc_info:
            onboarding_service.create_onboarding_session(COMPLETE_ONBOARDING_REQUEST)
        
        assert "Erro ao criar sessão de onboarding" in str(exc_info.value)
        assert mock_db.rollback.called

    def test_create_onboarding_session_general_error(self, onboarding_service, mock_db):
        """Testa criação de sessão com erro geral"""
        # Mock para email não existente
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock para flush com erro geral
        mock_db.flush.side_effect = Exception("Erro geral")
        
        with pytest.raises(OnboardingException) as exc_info:
            onboarding_service.create_onboarding_session(COMPLETE_ONBOARDING_REQUEST)
        
        assert "Erro interno do servidor" in str(exc_info.value)
        assert mock_db.rollback.called

    def test_get_session_success(self, onboarding_service, mock_db, mock_session):
        """Testa obtenção bem-sucedida de sessão"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        result = onboarding_service.get_session("test-session-123")
        
        assert result == mock_session

    def test_get_session_not_found(self, onboarding_service, mock_db):
        """Testa obtenção de sessão inexistente"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = onboarding_service.get_session("invalid-session")
        
        assert result is None

    def test_get_session_data_success(self, onboarding_service, mock_db, mock_session, mock_user, mock_company):
        """Testa obtenção bem-sucedida de dados da sessão"""
        # Mock para sessão
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_session,  # get_session
            mock_user,     # query User
            mock_company   # query Company
        ]
        
        # Mock para passos completados
        mock_completed_steps = Mock()
        mock_completed_steps.count.return_value = 2  # 2 passos completados
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        
        result = onboarding_service.get_session_data("test-session-123")
        
        assert result is not None
        assert result['session_id'] == "test-session-123"
        assert result['status'] == "in_progress"
        assert result['current_step'] == "welcome"
        assert result['progress'] == 40  # 2/5 * 100
        assert result['user_email'] == "joao@empresa.com"
        assert result['company_name'] == "Empresa Teste LTDA"

    def test_get_session_data_not_found(self, onboarding_service, mock_db):
        """Testa obtenção de dados de sessão inexistente"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = onboarding_service.get_session_data("invalid-session")
        
        assert result is None

    def test_process_step_success(self, onboarding_service, mock_db, mock_session):
        """Testa processamento bem-sucedido de passo"""
        # Mock para sessão
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        # Mock para passo
        mock_step = Mock(spec=OnboardingStep)
        mock_step.status = 'pending'
        mock_step.updated_at = datetime.now()
        
        # Mock para query de passos
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_session,  # get_session
            mock_step      # query OnboardingStep
        ]
        
        # Mock para commit
        mock_db.commit.return_value = None
        
        step_data = {
            "name": "João Silva",
            "email": "joao@empresa.com"
        }
        
        result = onboarding_service.process_step("test-session-123", "welcome", step_data)
        
        assert result['status'] == 'completed'
        assert result['data'] == step_data
        assert result['next_step'] == 'company'
        assert result['progress'] == 40  # 2/5 * 100

    def test_process_step_session_not_found(self, onboarding_service, mock_db):
        """Testa processamento de passo com sessão inexistente"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(OnboardingException) as exc_info:
            onboarding_service.process_step("invalid-session", "welcome", {})
        
        assert "Sessão não encontrada" in str(exc_info.value)

    def test_process_step_session_not_in_progress(self, onboarding_service, mock_db, mock_session):
        """Testa processamento de passo com sessão não em progresso"""
        mock_session.status = 'completed'
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        with pytest.raises(OnboardingException) as exc_info:
            onboarding_service.process_step("test-session-123", "welcome", {})
        
        assert "Sessão não está em progresso" in str(exc_info.value)

    def test_process_step_invalid_step(self, onboarding_service, mock_db, mock_session):
        """Testa processamento de passo inválido"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        with pytest.raises(OnboardingException) as exc_info:
            onboarding_service.process_step("test-session-123", "invalid-step", {})
        
        assert "Passo inválido: invalid-step" in str(exc_info.value)

    def test_process_step_validation_error(self, onboarding_service, mock_db, mock_session):
        """Testa processamento de passo com erro de validação"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        # Dados inválidos para o passo 'goals'
        invalid_goals_data = {
            "primary": []  # Lista vazia
        }
        
        result = onboarding_service.process_step("test-session-123", "goals", invalid_goals_data)
        
        assert result['status'] == 'error'
        assert 'Pelo menos um objetivo principal é obrigatório' in result['errors']

    def test_validate_completion_success(self, onboarding_service, mock_db):
        """Testa validação bem-sucedida de conclusão"""
        # Mock para passos completados
        mock_completed_step1 = Mock()
        mock_completed_step1.step_name = 'welcome'
        mock_completed_step2 = Mock()
        mock_completed_step2.step_name = 'company'
        mock_completed_step3 = Mock()
        mock_completed_step3.step_name = 'goals'
        mock_completed_step4 = Mock()
        mock_completed_step4.step_name = 'keywords'
        mock_completed_step5 = Mock()
        mock_completed_step5.step_name = 'finish'
        
        mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_completed_step1, mock_completed_step2, mock_completed_step3,
            mock_completed_step4, mock_completed_step5
        ]
        
        result = onboarding_service.validate_completion("test-session-123")
        
        assert result['valid'] is True
        assert len(result['missing_steps']) == 0
        assert len(result['completed_steps']) == 5

    def test_validate_completion_incomplete(self, onboarding_service, mock_db):
        """Testa validação de conclusão incompleta"""
        # Mock para apenas 2 passos completados
        mock_completed_step1 = Mock()
        mock_completed_step1.step_name = 'welcome'
        mock_completed_step2 = Mock()
        mock_completed_step2.step_name = 'company'
        
        mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_completed_step1, mock_completed_step2
        ]
        
        result = onboarding_service.validate_completion("test-session-123")
        
        assert result['valid'] is False
        assert len(result['missing_steps']) == 3
        assert 'goals' in result['missing_steps']
        assert 'keywords' in result['missing_steps']
        assert 'finish' in result['missing_steps']

    def test_complete_onboarding_success(self, onboarding_service, mock_db, mock_session, mock_user):
        """Testa finalização bem-sucedida do onboarding"""
        # Mock para sessão
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_session,  # get_session
            mock_user      # query User
        ]
        
        # Mock para validação de conclusão
        with patch.object(onboarding_service, 'validate_completion') as mock_validate:
            mock_validate.return_value = {
                'valid': True,
                'missing_steps': [],
                'completed_steps': ['welcome', 'company', 'goals', 'keywords', 'finish']
            }
            
            # Mock para commit
            mock_db.commit.return_value = None
            
            result = onboarding_service.complete_onboarding("test-session-123")
            
            assert 'user_email' in result
            assert 'completion_time' in result
            assert 'created_at' in result
            assert 'updated_at' in result
            assert result['user_email'] == "joao@empresa.com"
            
            # Verificar se o status foi atualizado
            assert mock_session.status == 'completed'
            assert mock_session.current_step == 'finish'
            assert mock_session.progress == 100

    def test_complete_onboarding_session_not_found(self, onboarding_service, mock_db):
        """Testa finalização com sessão inexistente"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(OnboardingException) as exc_info:
            onboarding_service.complete_onboarding("invalid-session")
        
        assert "Sessão não encontrada" in str(exc_info.value)

    def test_complete_onboarding_incomplete(self, onboarding_service, mock_db, mock_session):
        """Testa finalização de onboarding incompleto"""
        # Mock para sessão
        mock_db.query.return_value.filter.return_value.first.return_value = mock_session
        
        # Mock para validação de conclusão incompleta
        with patch.object(onboarding_service, 'validate_completion') as mock_validate:
            mock_validate.return_value = {
                'valid': False,
                'missing_steps': ['goals', 'keywords'],
                'completed_steps': ['welcome', 'company']
            }
            
            with pytest.raises(OnboardingException) as exc_info:
                onboarding_service.complete_onboarding("test-session-123")
            
            assert "Onboarding incompleto" in str(exc_info.value)

    def test_cancel_onboarding_success(self, onboarding_service, mock_db, mock_session, mock_user):
        """Testa cancelamento bem-sucedido do onboarding"""
        # Mock para sessão
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_session,  # get_session
            mock_user      # query User
        ]
        
        # Mock para commit
        mock_db.commit.return_value = None
        
        result = onboarding_service.cancel_onboarding("test-session-123", "user_cancelled")
        
        assert 'user_email' in result
        assert 'cancelled_at' in result
        assert 'reason' in result
        assert result['user_email'] == "joao@empresa.com"
        assert result['reason'] == "user_cancelled"
        
        # Verificar se o status foi atualizado
        assert mock_session.status == 'cancelled'

    def test_cancel_onboarding_session_not_found(self, onboarding_service, mock_db):
        """Testa cancelamento com sessão inexistente"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(OnboardingException) as exc_info:
            onboarding_service.cancel_onboarding("invalid-session")
        
        assert "Sessão não encontrada" in str(exc_info.value)

    def test_validate_email_availability_available(self, onboarding_service, mock_db):
        """Testa validação de email disponível"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = onboarding_service.validate_email_availability("novo@empresa.com")
        
        assert result['available'] is True
        assert result['message'] == 'Email disponível'

    def test_validate_email_availability_unavailable(self, onboarding_service, mock_db, mock_user):
        """Testa validação de email indisponível"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = onboarding_service.validate_email_availability("joao@empresa.com")
        
        assert result['available'] is False
        assert result['message'] == 'Email já está em uso'

    def test_get_analytics_success(self, onboarding_service, mock_db):
        """Testa obtenção bem-sucedida de analytics"""
        # Mock para sessões
        mock_session1 = Mock()
        mock_session1.created_at = datetime.now()
        mock_session1.status = 'completed'
        mock_session1.updated_at = datetime.now()
        
        mock_session2 = Mock()
        mock_session2.created_at = datetime.now()
        mock_session2.status = 'cancelled'
        mock_session2.updated_at = datetime.now()
        
        # Mock para passos
        mock_step1 = Mock()
        mock_step1.step_name = 'welcome'
        mock_step1.status = 'completed'
        mock_step1.data = {'primary': ['increase-traffic']}
        
        mock_step2 = Mock()
        mock_step2.step_name = 'goals'
        mock_step2.status = 'completed'
        mock_step2.data = {'primary': ['improve-rankings']}
        
        # Mock para empresas
        mock_company1 = Mock()
        mock_company1.industry = 'Tecnologia'
        mock_company1.created_at = datetime.now()
        
        mock_company2 = Mock()
        mock_company2.industry = 'E-commerce'
        mock_company2.created_at = datetime.now()
        
        # Configurar mocks
        mock_db.query.return_value.filter.return_value.count.side_effect = [2, 1, 1]  # total, completed, cancelled
        mock_db.query.return_value.filter.return_value.all.side_effect = [
            [mock_session1, mock_session2],  # sessions
            [mock_step1, mock_step2],        # steps
            [mock_company1, mock_company2]   # companies
        ]
        
        result = onboarding_service.get_analytics(30)
        
        assert result['total_sessions'] == 2
        assert result['completed_sessions'] == 1
        assert result['cancelled_sessions'] == 1
        assert result['completion_rate'] == 50.0
        assert 'Tecnologia' in result['industry_distribution']
        assert 'E-commerce' in result['industry_distribution']

    def test_get_analytics_empty_data(self, onboarding_service, mock_db):
        """Testa analytics com dados vazios"""
        # Mock para dados vazios
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = onboarding_service.get_analytics(30)
        
        assert result['total_sessions'] == 0
        assert result['completed_sessions'] == 0
        assert result['cancelled_sessions'] == 0
        assert result['completion_rate'] == 0
        assert result['avg_completion_time'] == 0

    def test_get_analytics_error(self, onboarding_service, mock_db):
        """Testa analytics com erro"""
        # Mock para erro
        mock_db.query.return_value.filter.return_value.count.side_effect = Exception("Erro de banco")
        
        result = onboarding_service.get_analytics(30)
        
        # Deve retornar dados vazios em caso de erro
        assert result['total_sessions'] == 0
        assert result['completed_sessions'] == 0
        assert result['cancelled_sessions'] == 0
        assert result['completion_rate'] == 0

class TestOnboardingServicePrivateMethods:
    """Testes para métodos privados do serviço"""

    def test_validate_step_data_welcome(self, onboarding_service):
        """Testa validação de dados do passo welcome"""
        result = onboarding_service._validate_step_data('welcome', {})
        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_validate_step_data_company_valid(self, onboarding_service):
        """Testa validação de dados válidos do passo company"""
        company_data = {
            'name': 'Empresa Teste',
            'industry': 'Tecnologia'
        }
        
        result = onboarding_service._validate_step_data('company', company_data)
        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_validate_step_data_company_invalid_name(self, onboarding_service):
        """Testa validação de dados inválidos do passo company"""
        company_data = {
            'name': 'A',  # Nome muito curto
            'industry': 'Tecnologia'
        }
        
        result = onboarding_service._validate_step_data('company', company_data)
        assert result['valid'] is False
        assert 'Nome da empresa deve ter pelo menos 2 caracteres' in result['errors']

    def test_validate_step_data_company_invalid_industry(self, onboarding_service):
        """Testa validação de indústria inválida no passo company"""
        company_data = {
            'name': 'Empresa Teste',
            'industry': 'Indústria Inexistente'
        }
        
        result = onboarding_service._validate_step_data('company', company_data)
        assert result['valid'] is False
        assert 'Indústria deve ser uma das:' in result['errors'][0]

    def test_validate_step_data_goals_valid(self, onboarding_service):
        """Testa validação de dados válidos do passo goals"""
        goals_data = {
            'primary': ['increase-traffic', 'improve-rankings']
        }
        
        result = onboarding_service._validate_step_data('goals', goals_data)
        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_validate_step_data_goals_empty(self, onboarding_service):
        """Testa validação de objetivos vazios no passo goals"""
        goals_data = {
            'primary': []
        }
        
        result = onboarding_service._validate_step_data('goals', goals_data)
        assert result['valid'] is False
        assert 'Pelo menos um objetivo principal é obrigatório' in result['errors']

    def test_validate_step_data_goals_invalid(self, onboarding_service):
        """Testa validação de objetivo inválido no passo goals"""
        goals_data = {
            'primary': ['invalid-goal']
        }
        
        result = onboarding_service._validate_step_data('goals', goals_data)
        assert result['valid'] is False
        assert 'Objetivo inválido: invalid-goal' in result['errors']

    def test_validate_step_data_keywords_valid(self, onboarding_service):
        """Testa validação de dados válidos do passo keywords"""
        keywords_data = {
            'initial': ['software desenvolvimento', 'sistema gestão']
        }
        
        result = onboarding_service._validate_step_data('keywords', keywords_data)
        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_validate_step_data_keywords_empty(self, onboarding_service):
        """Testa validação de palavras-chave vazias no passo keywords"""
        keywords_data = {
            'initial': []
        }
        
        result = onboarding_service._validate_step_data('keywords', keywords_data)
        assert result['valid'] is False
        assert 'Pelo menos uma palavra-chave inicial é obrigatória' in result['errors']

    def test_validate_step_data_keywords_too_long(self, onboarding_service):
        """Testa validação de palavra-chave muito longa no passo keywords"""
        keywords_data = {
            'initial': ['a' * 101]  # Mais de 100 caracteres
        }
        
        result = onboarding_service._validate_step_data('keywords', keywords_data)
        assert result['valid'] is False
        assert 'Palavras-chave não podem ter mais de 100 caracteres' in result['errors']

    def test_validate_step_data_keywords_too_short(self, onboarding_service):
        """Testa validação de palavra-chave muito curta no passo keywords"""
        keywords_data = {
            'initial': ['a']  # Menos de 2 caracteres
        }
        
        result = onboarding_service._validate_step_data('keywords', keywords_data)
        assert result['valid'] is False
        assert 'Palavras-chave devem ter pelo menos 2 caracteres' in result['errors']

    def test_get_next_step_valid(self, onboarding_service):
        """Testa obtenção do próximo passo válido"""
        next_step = onboarding_service._get_next_step('welcome')
        assert next_step == 'company'
        
        next_step = onboarding_service._get_next_step('company')
        assert next_step == 'goals'
        
        next_step = onboarding_service._get_next_step('goals')
        assert next_step == 'keywords'
        
        next_step = onboarding_service._get_next_step('keywords')
        assert next_step == 'finish'

    def test_get_next_step_last_step(self, onboarding_service):
        """Testa obtenção do próximo passo no último passo"""
        next_step = onboarding_service._get_next_step('finish')
        assert next_step is None

    def test_get_next_step_invalid_step(self, onboarding_service):
        """Testa obtenção do próximo passo com passo inválido"""
        next_step = onboarding_service._get_next_step('invalid-step')
        assert next_step is None

    def test_calculate_progress(self, onboarding_service, mock_db):
        """Testa cálculo de progresso"""
        # Mock para 2 passos completados
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        
        progress = onboarding_service._calculate_progress("test-session-123")
        assert progress == 40  # 2/5 * 100

    def test_calculate_progress_all_completed(self, onboarding_service, mock_db):
        """Testa cálculo de progresso com todos os passos completados"""
        # Mock para 5 passos completados
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        progress = onboarding_service._calculate_progress("test-session-123")
        assert progress == 100

    def test_calculate_progress_error(self, onboarding_service, mock_db):
        """Testa cálculo de progresso com erro"""
        # Mock para erro
        mock_db.query.return_value.filter.return_value.count.side_effect = Exception("Erro")
        
        progress = onboarding_service._calculate_progress("test-session-123")
        assert progress == 0 