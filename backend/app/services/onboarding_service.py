"""
Serviço de Onboarding - Omni Keywords Finder
Lógica de negócio para gerenciamento do processo de onboarding

Tracing ID: ONBOARDING_SERVICE_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Serviço de Onboarding

Baseado no código real do sistema Omni Keywords Finder
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_, or_, func, desc

from ..models import User, Company, OnboardingSession, OnboardingStep
from ..utils.validation import validate_email, validate_company_data
from ..utils.logging import log_onboarding_event
from ..utils.security import hash_password, generate_session_token
from ..exceptions import OnboardingException, ValidationException

# Integração com padrões de resiliência da Fase 1
from infrastructure.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, circuit_breaker
from infrastructure.resilience.retry_strategy import RetryConfig, RetryStrategy, retry
from infrastructure.resilience.bulkhead import BulkheadConfig, bulkhead
from infrastructure.resilience.timeout_manager import TimeoutConfig, timeout

# Configuração de logging
logger = logging.getLogger(__name__)

class OnboardingService:
    """
    Serviço para gerenciamento do processo de onboarding
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.steps = ['welcome', 'company', 'goals', 'keywords', 'finish']
        self.step_weights = {
            'welcome': 20,
            'company': 25,
            'goals': 25,
            'keywords': 20,
            'finish': 10
        }
        
        # Configurações de resiliência da Fase 1
        self._setup_resilience_patterns()

    def _setup_resilience_patterns(self):
        """Configura os padrões de resiliência da Fase 1"""
        # Circuit Breaker para operações de banco
        self.db_circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                name="onboarding_db",
                fallback_function=self._fallback_db_error
            )
        )
        
        # Configurações de retry
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
        
        # Configurações de bulkhead
        self.bulkhead_config = BulkheadConfig(
            max_concurrent_calls=20,
            max_wait_duration=10.0,
            max_failure_count=5,
            name="onboarding_service"
        )
        
        # Configurações de timeout
        self.timeout_config = TimeoutConfig(
            timeout_seconds=60.0,
            name="onboarding_service"
        )

    def _fallback_db_error(self, *args, **kwargs):
        """Fallback quando operações de banco falham"""
        logger.warning("Operação de banco falhou, usando fallback")
        return {"error": "Banco indisponível", "fallback": True}
    
    def validate_complete_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados completos de onboarding
        """
        errors = []
        
        try:
            # Validar dados do usuário
            user_data = request_data.get('user', {})
            if not user_data.get('name') or len(user_data['name'].strip()) < 2:
                errors.append('Nome do usuário deve ter pelo menos 2 caracteres')
            
            if not user_data.get('email') or not validate_email(user_data['email']):
                errors.append('Email do usuário inválido')
            
            # Verificar se email já está em uso
            existing_user = self.db.query(User).filter(
                User.email == user_data.get('email', '').lower()
            ).first()
            if existing_user:
                errors.append('Email já está em uso')
            
            # Validar dados da empresa
            company_data = request_data.get('company', {})
            if not company_data.get('name') or len(company_data['name'].strip()) < 2:
                errors.append('Nome da empresa deve ter pelo menos 2 caracteres')
            
            valid_industries = [
                'Tecnologia', 'E-commerce', 'Saúde', 'Educação', 'Finanças',
                'Marketing Digital', 'Consultoria', 'Varejo', 'Serviços', 'Manufatura'
            ]
            if company_data.get('industry') not in valid_industries:
                errors.append(f'Indústria deve ser uma das: {", ".join(valid_industries)}')
            
            valid_sizes = ['1-10', '11-50', '51-200', '201-1000', '1000+']
            if company_data.get('size') not in valid_sizes:
                errors.append(f'Tamanho deve ser um dos: {", ".join(valid_sizes)}')
            
            # Validar objetivos
            goals_data = request_data.get('goals', {})
            if not goals_data.get('primary') or len(goals_data['primary']) == 0:
                errors.append('Pelo menos um objetivo principal é obrigatório')
            
            valid_goals = [
                'increase-traffic', 'improve-rankings', 'generate-leads',
                'increase-sales', 'brand-awareness', 'competitor-analysis'
            ]
            for goal in goals_data.get('primary', []):
                if goal not in valid_goals:
                    errors.append(f'Objetivo inválido: {goal}')
            
            valid_timeframes = ['1-3-months', '3-6-months', '6-12-months', '12+months']
            if goals_data.get('timeframe') not in valid_timeframes:
                errors.append(f'Prazo deve ser um dos: {", ".join(valid_timeframes)}')
            
            valid_budgets = ['low', 'medium', 'high', 'enterprise']
            if goals_data.get('budget') not in valid_budgets:
                errors.append(f'Orçamento deve ser um dos: {", ".join(valid_budgets)}')
            
            valid_priorities = ['high', 'medium', 'low']
            if goals_data.get('priority') not in valid_priorities:
                errors.append(f'Prioridade deve ser uma das: {", ".join(valid_priorities)}')
            
            # Validar palavras-chave
            keywords_data = request_data.get('keywords', {})
            if not keywords_data.get('initial') or len(keywords_data['initial']) == 0:
                errors.append('Pelo menos uma palavra-chave inicial é obrigatória')
            
            for keyword in keywords_data.get('initial', []):
                if not keyword or len(keyword.strip()) < 2:
                    errors.append('Palavras-chave devem ter pelo menos 2 caracteres')
                if len(keyword) > 100:
                    errors.append('Palavras-chave não podem ter mais de 100 caracteres')
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Erro na validação de dados: {str(e)}")
            errors.append('Erro interno na validação')
            return {
                'valid': False,
                'errors': errors
            }
    
    @retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
    @bulkhead(max_concurrent_calls=20, max_wait_duration=10.0)
    @timeout(timeout_seconds=60.0)
    def create_onboarding_session(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova sessão de onboarding com padrões de resiliência
        """
        try:
            # Gerar ID único da sessão
            session_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Criar usuário
            user_data = request_data['user']
            user = User(
                name=user_data['name'].strip(),
                email=user_data['email'].lower(),
                company=user_data.get('company'),
                role=user_data.get('role'),
                created_at=now,
                updated_at=now
            )
            self.db.add(user)
            self.db.flush()  # Para obter o ID do usuário
            
            # Criar empresa
            company_data = request_data['company']
            company = Company(
                name=company_data['name'].strip(),
                industry=company_data['industry'],
                size=company_data['size'],
                website=company_data.get('website'),
                country=company_data.get('country', 'Brasil'),
                user_id=user.id,
                created_at=now,
                updated_at=now
            )
            self.db.add(company)
            
            # Criar sessão de onboarding
            session = OnboardingSession(
                session_id=session_id,
                user_id=user.id,
                company_id=company.id,
                status='in_progress',
                current_step='welcome',
                progress=20,
                estimated_time=300,  # 5 minutos
                created_at=now,
                updated_at=now
            )
            self.db.add(session)
            
            # Criar passos de onboarding
            for step in self.steps:
                step_data = OnboardingStep(
                    session_id=session_id,
                    step_name=step,
                    status='pending',
                    data={},
                    created_at=now,
                    updated_at=now
                )
                self.db.add(step_data)
            
            # Salvar dados iniciais
            self._save_step_data(session_id, 'welcome', {
                'user': user_data,
                'company': company_data,
                'goals': request_data['goals'],
                'keywords': request_data['keywords']
            })
            
            self.db.commit()
            
            logger.info(f"Sessão de onboarding criada: {session_id}")
            
            return {
                'session_id': session_id,
                'user_id': user.id,
                'company_id': company.id,
                'created_at': now,
                'updated_at': now
            }
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Erro de integridade ao criar sessão: {str(e)}")
            raise OnboardingException("Erro ao criar sessão de onboarding")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar sessão de onboarding: {str(e)}")
            raise OnboardingException("Erro interno do servidor")
    
    def get_session(self, session_id: str) -> Optional[OnboardingSession]:
        """
        Obtém uma sessão de onboarding
        """
        try:
            return self.db.query(OnboardingSession).filter(
                OnboardingSession.session_id == session_id
            ).first()
        except Exception as e:
            logger.error(f"Erro ao obter sessão {session_id}: {str(e)}")
            return None
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém dados completos de uma sessão
        """
        try:
            session = self.get_session(session_id)
            if not session:
                return None
            
            # Buscar dados do usuário e empresa
            user = self.db.query(User).filter(User.id == session.user_id).first()
            company = self.db.query(Company).filter(Company.id == session.company_id).first()
            
            # Calcular progresso atual
            completed_steps = self.db.query(OnboardingStep).filter(
                and_(
                    OnboardingStep.session_id == session_id,
                    OnboardingStep.status == 'completed'
                )
            ).count()
            
            progress = min(100, (completed_steps / len(self.steps)) * 100)
            
            return {
                'session_id': session.session_id,
                'status': session.status,
                'current_step': session.current_step,
                'progress': int(progress),
                'estimated_time': session.estimated_time,
                'next_step': self._get_next_step(session.current_step),
                'user_email': user.email if user else None,
                'company_name': company.name if company else None,
                'created_at': session.created_at,
                'updated_at': session.updated_at
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados da sessão {session_id}: {str(e)}")
            return None
    
    def process_step(self, session_id: str, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um passo específico do onboarding
        """
        try:
            # Validar sessão
            session = self.get_session(session_id)
            if not session:
                raise OnboardingException("Sessão não encontrada")
            
            if session.status != 'in_progress':
                raise OnboardingException("Sessão não está em progresso")
            
            # Validar passo
            if step not in self.steps:
                raise OnboardingException(f"Passo inválido: {step}")
            
            # Validar dados do passo
            validation_result = self._validate_step_data(step, data)
            if not validation_result['valid']:
                return {
                    'status': 'error',
                    'errors': validation_result['errors'],
                    'data': data
                }
            
            # Salvar dados do passo
            self._save_step_data(session_id, step, data)
            
            # Atualizar status do passo
            step_record = self.db.query(OnboardingStep).filter(
                and_(
                    OnboardingStep.session_id == session_id,
                    OnboardingStep.step_name == step
                )
            ).first()
            
            if step_record:
                step_record.status = 'completed'
                step_record.updated_at = datetime.now()
            
            # Atualizar sessão
            next_step = self._get_next_step(step)
            progress = self._calculate_progress(session_id)
            
            session.current_step = next_step or 'finish'
            session.progress = progress
            session.updated_at = datetime.now()
            
            # Se chegou ao fim, marcar como completada
            if not next_step:
                session.status = 'completed'
            
            self.db.commit()
            
            logger.info(f"Passo {step} processado para sessão {session_id}")
            
            return {
                'status': 'completed',
                'data': data,
                'next_step': next_step,
                'progress': progress
            }
            
        except OnboardingException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao processar passo {step}: {str(e)}")
            raise OnboardingException("Erro interno do servidor")
    
    def validate_completion(self, session_id: str) -> Dict[str, Any]:
        """
        Valida se o onboarding está completo
        """
        try:
            # Verificar se todos os passos foram completados
            completed_steps = self.db.query(OnboardingStep).filter(
                and_(
                    OnboardingStep.session_id == session_id,
                    OnboardingStep.status == 'completed'
                )
            ).all()
            
            completed_step_names = [step.step_name for step in completed_steps]
            missing_steps = [step for step in self.steps if step not in completed_step_names]
            
            return {
                'valid': len(missing_steps) == 0,
                'missing_steps': missing_steps,
                'completed_steps': completed_step_names
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar conclusão da sessão {session_id}: {str(e)}")
            return {
                'valid': False,
                'missing_steps': self.steps,
                'error': str(e)
            }
    
    def complete_onboarding(self, session_id: str) -> Dict[str, Any]:
        """
        Finaliza o processo de onboarding
        """
        try:
            session = self.get_session(session_id)
            if not session:
                raise OnboardingException("Sessão não encontrada")
            
            # Validar se está completo
            validation_result = self.validate_completion(session_id)
            if not validation_result['valid']:
                raise OnboardingException(f"Onboarding incompleto: {validation_result['missing_steps']}")
            
            # Atualizar status
            now = datetime.now()
            session.status = 'completed'
            session.current_step = 'finish'
            session.progress = 100
            session.updated_at = now
            
            # Calcular tempo de conclusão
            completion_time = int((now - session.created_at).total_seconds())
            
            # Buscar dados do usuário
            user = self.db.query(User).filter(User.id == session.user_id).first()
            
            self.db.commit()
            
            logger.info(f"Onboarding finalizado para sessão {session_id}")
            
            return {
                'user_email': user.email if user else None,
                'completion_time': completion_time,
                'created_at': session.created_at,
                'updated_at': now
            }
            
        except OnboardingException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao finalizar onboarding {session_id}: {str(e)}")
            raise OnboardingException("Erro interno do servidor")
    
    def cancel_onboarding(self, session_id: str, reason: str = 'user_cancelled') -> Dict[str, Any]:
        """
        Cancela uma sessão de onboarding
        """
        try:
            session = self.get_session(session_id)
            if not session:
                raise OnboardingException("Sessão não encontrada")
            
            # Atualizar status
            now = datetime.now()
            session.status = 'cancelled'
            session.updated_at = now
            
            # Buscar dados do usuário
            user = self.db.query(User).filter(User.id == session.user_id).first()
            
            self.db.commit()
            
            logger.info(f"Onboarding cancelado para sessão {session_id}")
            
            return {
                'user_email': user.email if user else None,
                'cancelled_at': now,
                'reason': reason
            }
            
        except OnboardingException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao cancelar onboarding {session_id}: {str(e)}")
            raise OnboardingException("Erro interno do servidor")
    
    def validate_email_availability(self, email: str) -> Dict[str, Any]:
        """
        Valida se um email está disponível
        """
        try:
            email = email.lower().strip()
            
            # Verificar se já existe
            existing_user = self.db.query(User).filter(User.email == email).first()
            
            if existing_user:
                return {
                    'available': False,
                    'message': 'Email já está em uso'
                }
            else:
                return {
                    'available': True,
                    'message': 'Email disponível'
                }
                
        except Exception as e:
            logger.error(f"Erro ao validar email {email}: {str(e)}")
            return {
                'available': False,
                'message': 'Erro ao validar email'
            }
    
    def get_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtém analytics do onboarding
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Estatísticas gerais
            total_sessions = self.db.query(OnboardingSession).filter(
                OnboardingSession.created_at >= start_date
            ).count()
            
            completed_sessions = self.db.query(OnboardingSession).filter(
                and_(
                    OnboardingSession.created_at >= start_date,
                    OnboardingSession.status == 'completed'
                )
            ).count()
            
            cancelled_sessions = self.db.query(OnboardingSession).filter(
                and_(
                    OnboardingSession.created_at >= start_date,
                    OnboardingSession.status == 'cancelled'
                )
            ).count()
            
            # Taxa de conclusão
            completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # Tempo médio de conclusão
            completed_sessions_data = self.db.query(OnboardingSession).filter(
                and_(
                    OnboardingSession.created_at >= start_date,
                    OnboardingSession.status == 'completed'
                )
            ).all()
            
            total_completion_time = 0
            for session in completed_sessions_data:
                completion_time = (session.updated_at - session.created_at).total_seconds()
                total_completion_time += completion_time
            
            avg_completion_time = int(total_completion_time / len(completed_sessions_data)) if completed_sessions_data else 0
            
            # Taxa de conclusão por passo
            step_completion_rates = {}
            for step in self.steps:
                step_completed = self.db.query(OnboardingStep).filter(
                    and_(
                        OnboardingStep.created_at >= start_date,
                        OnboardingStep.step_name == step,
                        OnboardingStep.status == 'completed'
                    )
                ).count()
                
                step_total = self.db.query(OnboardingStep).filter(
                    and_(
                        OnboardingStep.created_at >= start_date,
                        OnboardingStep.step_name == step
                    )
                ).count()
                
                step_completion_rates[step] = (step_completed / step_total * 100) if step_total > 0 else 0
            
            # Distribuição por indústria
            industry_distribution = {}
            companies = self.db.query(Company).filter(Company.created_at >= start_date).all()
            for company in companies:
                industry = company.industry
                industry_distribution[industry] = industry_distribution.get(industry, 0) + 1
            
            # Distribuição por objetivos
            goal_distribution = {}
            for step in self.db.query(OnboardingStep).filter(
                and_(
                    OnboardingStep.created_at >= start_date,
                    OnboardingStep.step_name == 'goals',
                    OnboardingStep.status == 'completed'
                )
            ).all():
                if step.data and 'primary' in step.data:
                    for goal in step.data['primary']:
                        goal_distribution[goal] = goal_distribution.get(goal, 0) + 1
            
            return {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'cancelled_sessions': cancelled_sessions,
                'completion_rate': round(completion_rate, 2),
                'avg_completion_time': avg_completion_time,
                'step_completion_rates': step_completion_rates,
                'industry_distribution': industry_distribution,
                'goal_distribution': goal_distribution
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter analytics: {str(e)}")
            return {
                'total_sessions': 0,
                'completed_sessions': 0,
                'cancelled_sessions': 0,
                'completion_rate': 0,
                'avg_completion_time': 0,
                'step_completion_rates': {},
                'industry_distribution': {},
                'goal_distribution': {}
            }
    
    def _validate_step_data(self, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados específicos de cada passo
        """
        errors = []
        
        try:
            if step == 'welcome':
                # Validação básica já feita no início
                pass
                
            elif step == 'company':
                if not data.get('name') or len(data['name'].strip()) < 2:
                    errors.append('Nome da empresa deve ter pelo menos 2 caracteres')
                
                valid_industries = [
                    'Tecnologia', 'E-commerce', 'Saúde', 'Educação', 'Finanças',
                    'Marketing Digital', 'Consultoria', 'Varejo', 'Serviços', 'Manufatura'
                ]
                if data.get('industry') not in valid_industries:
                    errors.append(f'Indústria deve ser uma das: {", ".join(valid_industries)}')
                
            elif step == 'goals':
                if not data.get('primary') or len(data['primary']) == 0:
                    errors.append('Pelo menos um objetivo principal é obrigatório')
                
                valid_goals = [
                    'increase-traffic', 'improve-rankings', 'generate-leads',
                    'increase-sales', 'brand-awareness', 'competitor-analysis'
                ]
                for goal in data.get('primary', []):
                    if goal not in valid_goals:
                        errors.append(f'Objetivo inválido: {goal}')
                
            elif step == 'keywords':
                if not data.get('initial') or len(data['initial']) == 0:
                    errors.append('Pelo menos uma palavra-chave inicial é obrigatória')
                
                for keyword in data.get('initial', []):
                    if not keyword or len(keyword.strip()) < 2:
                        errors.append('Palavras-chave devem ter pelo menos 2 caracteres')
                    if len(keyword) > 100:
                        errors.append('Palavras-chave não podem ter mais de 100 caracteres')
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Erro na validação do passo {step}: {str(e)}")
            return {
                'valid': False,
                'errors': ['Erro interno na validação']
            }
    
    def _save_step_data(self, session_id: str, step: str, data: Dict[str, Any]):
        """
        Salva dados de um passo específico
        """
        try:
            step_record = self.db.query(OnboardingStep).filter(
                and_(
                    OnboardingStep.session_id == session_id,
                    OnboardingStep.step_name == step
                )
            ).first()
            
            if step_record:
                step_record.data = data
                step_record.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados do passo {step}: {str(e)}")
            raise
    
    def _get_next_step(self, current_step: str) -> Optional[str]:
        """
        Obtém o próximo passo baseado no passo atual
        """
        try:
            current_index = self.steps.index(current_step)
            if current_index < len(self.steps) - 1:
                return self.steps[current_index + 1]
            return None
        except ValueError:
            return None
    
    def _calculate_progress(self, session_id: str) -> int:
        """
        Calcula o progresso atual do onboarding
        """
        try:
            completed_steps = self.db.query(OnboardingStep).filter(
                and_(
                    OnboardingStep.session_id == session_id,
                    OnboardingStep.status == 'completed'
                )
            ).count()
            
            return min(100, int((completed_steps / len(self.steps)) * 100))
            
        except Exception as e:
            logger.error(f"Erro ao calcular progresso: {str(e)}")
            return 0 