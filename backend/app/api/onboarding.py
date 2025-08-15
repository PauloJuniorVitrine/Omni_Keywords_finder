"""
API de Onboarding - Omni Keywords Finder
APIs REST para gerenciamento do processo de onboarding

Tracing ID: ONBOARDING_API_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Backend de Onboarding

Baseado no código real do sistema Omni Keywords Finder
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models import User, Company, OnboardingSession, OnboardingStep
from ..services.onboarding_service import OnboardingService
from ..utils.validation import validate_email, validate_company_data
from ..utils.auth import get_current_user
from ..utils.logging import log_onboarding_event

# Configuração de logging
logger = logging.getLogger(__name__)

# Router principal
router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# Security
security = HTTPBearer()

# Modelos Pydantic para validação
class UserData(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    role: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip()

    @validator('email')
    def validate_email_format(cls, v):
        if not validate_email(v):
            raise ValueError('Formato de email inválido')
        return v.lower()

class CompanyData(BaseModel):
    name: str
    industry: str
    size: str
    website: Optional[str] = None
    country: str = "Brasil"

    @validator('name')
    def validate_company_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nome da empresa deve ter pelo menos 2 caracteres')
        return v.strip()

    @validator('industry')
    def validate_industry(cls, v):
        valid_industries = [
            'Tecnologia', 'E-commerce', 'Saúde', 'Educação', 'Finanças',
            'Marketing Digital', 'Consultoria', 'Varejo', 'Serviços', 'Manufatura'
        ]
        if v not in valid_industries:
            raise ValueError(f'Indústria deve ser uma das: {", ".join(valid_industries)}')
        return v

    @validator('size')
    def validate_size(cls, v):
        valid_sizes = ['1-10', '11-50', '51-200', '201-1000', '1000+']
        if v not in valid_sizes:
            raise ValueError(f'Tamanho deve ser um dos: {", ".join(valid_sizes)}')
        return v

    @validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            v = f'https://{v}'
        return v

class GoalsData(BaseModel):
    primary: List[str]
    secondary: List[str] = []
    timeframe: str
    budget: str
    priority: str

    @validator('primary')
    def validate_primary_goals(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Pelo menos um objetivo principal é obrigatório')
        
        valid_goals = [
            'increase-traffic', 'improve-rankings', 'generate-leads',
            'increase-sales', 'brand-awareness', 'competitor-analysis'
        ]
        
        for goal in v:
            if goal not in valid_goals:
                raise ValueError(f'Objetivo inválido: {goal}')
        
        return v

    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = ['1-3-months', '3-6-months', '6-12-months', '12+months']
        if v not in valid_timeframes:
            raise ValueError(f'Prazo deve ser um dos: {", ".join(valid_timeframes)}')
        return v

    @validator('budget')
    def validate_budget(cls, v):
        valid_budgets = ['low', 'medium', 'high', 'enterprise']
        if v not in valid_budgets:
            raise ValueError(f'Orçamento deve ser um dos: {", ".join(valid_budgets)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['high', 'medium', 'low']
        if v not in valid_priorities:
            raise ValueError(f'Prioridade deve ser uma das: {", ".join(valid_priorities)}')
        return v

class KeywordsData(BaseModel):
    initial: List[str]
    competitors: List[str] = []
    suggestions: List[str] = []

    @validator('initial')
    def validate_initial_keywords(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Pelo menos uma palavra-chave inicial é obrigatória')
        
        # Validar formato das palavras-chave
        for keyword in v:
            if not keyword or len(keyword.strip()) < 2:
                raise ValueError('Palavras-chave devem ter pelo menos 2 caracteres')
            if len(keyword) > 100:
                raise ValueError('Palavras-chave não podem ter mais de 100 caracteres')
        
        return [kw.strip().lower() for kw in v]

class OnboardingRequest(BaseModel):
    user: UserData
    company: CompanyData
    goals: GoalsData
    keywords: KeywordsData

class OnboardingResponse(BaseModel):
    session_id: str
    status: str
    current_step: str
    progress: int
    estimated_time: int
    next_step: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class OnboardingStepRequest(BaseModel):
    step: str
    data: Dict[str, Any]

class OnboardingStepResponse(BaseModel):
    step: str
    status: str
    data: Dict[str, Any]
    validation_errors: List[str] = []
    next_step: Optional[str] = None

# Endpoints
@router.post("/start", response_model=OnboardingResponse, status_code=status.HTTP_201_CREATED)
async def start_onboarding(
    request: OnboardingRequest,
    db: Session = Depends(get_db)
):
    """
    Inicia o processo de onboarding com dados completos
    """
    try:
        logger.info(f"Iniciando onboarding para usuário: {request.user.email}")
        
        # Criar serviço de onboarding
        onboarding_service = OnboardingService(db)
        
        # Validar dados completos
        validation_result = onboarding_service.validate_complete_data(request)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Dados de onboarding inválidos",
                    "errors": validation_result['errors']
                }
            )
        
        # Criar sessão de onboarding
        session_data = onboarding_service.create_onboarding_session(request)
        
        # Log do evento
        log_onboarding_event(
            session_id=session_data['session_id'],
            event_type="onboarding_started",
            user_email=request.user.email,
            company_name=request.company.name
        )
        
        logger.info(f"Onboarding iniciado com sucesso. Session ID: {session_data['session_id']}")
        
        return OnboardingResponse(
            session_id=session_data['session_id'],
            status="in_progress",
            current_step="welcome",
            progress=20,
            estimated_time=300,  # 5 minutos
            next_step="company",
            created_at=session_data['created_at'],
            updated_at=session_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar onboarding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/step", response_model=OnboardingStepResponse)
async def process_onboarding_step(
    request: OnboardingStepRequest,
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Processa um passo específico do onboarding
    """
    try:
        logger.info(f"Processando passo {request.step} para sessão {session_id}")
        
        # Validar sessão
        onboarding_service = OnboardingService(db)
        session = onboarding_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão de onboarding não encontrada"
            )
        
        # Processar passo
        step_result = onboarding_service.process_step(session_id, request.step, request.data)
        
        # Log do evento
        log_onboarding_event(
            session_id=session_id,
            event_type=f"step_{request.step}_completed",
            user_email=session.user_email,
            step_data=request.data
        )
        
        return OnboardingStepResponse(
            step=request.step,
            status=step_result['status'],
            data=step_result['data'],
            validation_errors=step_result.get('errors', []),
            next_step=step_result.get('next_step')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar passo {request.step}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/session/{session_id}", response_model=OnboardingResponse)
async def get_onboarding_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém o status atual de uma sessão de onboarding
    """
    try:
        onboarding_service = OnboardingService(db)
        session_data = onboarding_service.get_session_data(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão de onboarding não encontrada"
            )
        
        return OnboardingResponse(**session_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter sessão {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.put("/session/{session_id}/complete", response_model=OnboardingResponse)
async def complete_onboarding(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Finaliza o processo de onboarding
    """
    try:
        logger.info(f"Finalizando onboarding para sessão {session_id}")
        
        onboarding_service = OnboardingService(db)
        
        # Validar se todos os passos foram completados
        validation_result = onboarding_service.validate_completion(session_id)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Onboarding incompleto",
                    "missing_steps": validation_result['missing_steps']
                }
            )
        
        # Finalizar onboarding
        completion_data = onboarding_service.complete_onboarding(session_id)
        
        # Log do evento
        log_onboarding_event(
            session_id=session_id,
            event_type="onboarding_completed",
            user_email=completion_data['user_email'],
            completion_time=completion_data['completion_time']
        )
        
        logger.info(f"Onboarding finalizado com sucesso para sessão {session_id}")
        
        return OnboardingResponse(
            session_id=session_id,
            status="completed",
            current_step="finish",
            progress=100,
            estimated_time=0,
            next_step=None,
            created_at=completion_data['created_at'],
            updated_at=completion_data['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao finalizar onboarding {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/session/{session_id}")
async def cancel_onboarding(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancela uma sessão de onboarding
    """
    try:
        logger.info(f"Cancelando onboarding para sessão {session_id}")
        
        onboarding_service = OnboardingService(db)
        cancellation_data = onboarding_service.cancel_onboarding(session_id)
        
        # Log do evento
        log_onboarding_event(
            session_id=session_id,
            event_type="onboarding_cancelled",
            user_email=cancellation_data['user_email'],
            cancellation_reason=cancellation_data.get('reason', 'user_cancelled')
        )
        
        return {
            "message": "Onboarding cancelado com sucesso",
            "session_id": session_id,
            "cancelled_at": cancellation_data['cancelled_at']
        }
        
    except Exception as e:
        logger.error(f"Erro ao cancelar onboarding {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/analytics/summary")
async def get_onboarding_analytics(
    db: Session = Depends(get_db),
    days: int = 30
):
    """
    Obtém analytics do onboarding
    """
    try:
        onboarding_service = OnboardingService(db)
        analytics = onboarding_service.get_analytics(days)
        
        return {
            "period_days": days,
            "total_sessions": analytics['total_sessions'],
            "completed_sessions": analytics['completed_sessions'],
            "cancelled_sessions": analytics['cancelled_sessions'],
            "completion_rate": analytics['completion_rate'],
            "avg_completion_time": analytics['avg_completion_time'],
            "step_completion_rates": analytics['step_completion_rates'],
            "industry_distribution": analytics['industry_distribution'],
            "goal_distribution": analytics['goal_distribution']
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/validate/email")
async def validate_email_endpoint(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Valida se um email já está em uso
    """
    try:
        onboarding_service = OnboardingService(db)
        validation_result = onboarding_service.validate_email_availability(email)
        
        return {
            "email": email,
            "available": validation_result['available'],
            "message": validation_result['message']
        }
        
    except Exception as e:
        logger.error(f"Erro ao validar email {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/suggestions/industry/{industry}")
async def get_industry_suggestions(industry: str):
    """
    Obtém sugestões baseadas na indústria
    """
    try:
        suggestions = {
            'Tecnologia': [
                'software desenvolvimento',
                'sistema gestão',
                'tecnologia inovação',
                'startup tecnologia',
                'solução digital'
            ],
            'E-commerce': [
                'loja online',
                'ecommerce plataforma',
                'venda internet',
                'marketplace digital',
                'compras online'
            ],
            'Saúde': [
                'clínica médica',
                'consulta online',
                'exame laboratório',
                'plano saúde',
                'telemedicina'
            ],
            'Educação': [
                'curso online',
                'treinamento profissional',
                'educação digital',
                'certificação',
                'aprendizado online'
            ],
            'Finanças': [
                'investimento financeiro',
                'consultoria financeira',
                'planejamento financeiro',
                'gestão patrimonial',
                'financiamento'
            ],
            'Marketing Digital': [
                'agência marketing',
                'publicidade digital',
                'seo otimização',
                'tráfego orgânico',
                'conversão leads'
            ]
        }
        
        return {
            "industry": industry,
            "suggestions": suggestions.get(industry, [
                'palavra-chave principal',
                'termo busca',
                'otimização seo',
                'marketing digital',
                'solução problema'
            ])
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter sugestões para indústria {industry}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        ) 