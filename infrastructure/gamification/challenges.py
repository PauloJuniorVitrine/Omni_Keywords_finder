"""
Sistema de Desafios e Missões
=============================

Este módulo implementa o sistema de desafios e missões para gamificação,
incluindo diferentes tipos de desafios, progresso e recompensas.

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: GAMIFICATION_005
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict

# Integração com observabilidade
try:
    from infrastructure.observability.telemetry import TelemetryManager
    from infrastructure.observability.metrics import MetricsManager
    from infrastructure.observability.tracing import TracingManager
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# Cache Redis para persistência
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChallengeType(Enum):
    """Tipos de desafios"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ACHIEVEMENT = "achievement"
    EVENT = "event"
    CUSTOM = "custom"


class ChallengeStatus(Enum):
    """Status de um desafio"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class ChallengeCriteria:
    """Critérios para completar um desafio"""
    criteria_type: str
    target_value: Union[int, float, str]
    current_value: Union[int, float, str] = 0
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_completed(self) -> bool:
        """Verifica se o critério foi completado"""
        if isinstance(self.target_value, (int, float)):
            return self.current_value >= self.target_value
        else:
            return self.current_value == self.target_value
    
    def get_progress(self) -> float:
        """Retorna progresso do critério (0.0 a 1.0)"""
        if isinstance(self.target_value, (int, float)) and self.target_value > 0:
            return min(self.current_value / self.target_value, 1.0)
        return 1.0 if self.is_completed() else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "criteria_type": self.criteria_type,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "description": self.description,
            "metadata": self.metadata,
            "is_completed": self.is_completed(),
            "progress": self.get_progress()
        }


@dataclass
class Challenge:
    """Definição de um desafio"""
    challenge_id: str
    name: str
    description: str
    challenge_type: ChallengeType
    criteria: List[ChallengeCriteria]
    points_reward: int = 0
    badge_reward: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_participants: Optional[int] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "challenge_id": self.challenge_id,
            "name": self.name,
            "description": self.description,
            "challenge_type": self.challenge_type.value,
            "criteria": [c.to_dict() for c in self.criteria],
            "points_reward": self.points_reward,
            "badge_reward": self.badge_reward,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "max_participants": self.max_participants,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    def is_available(self) -> bool:
        """Verifica se o desafio está disponível"""
        now = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def is_completed(self) -> bool:
        """Verifica se o desafio foi completado"""
        return all(criteria.is_completed() for criteria in self.criteria)
    
    def get_overall_progress(self) -> float:
        """Retorna progresso geral do desafio"""
        if not self.criteria:
            return 1.0
        
        total_progress = sum(criteria.get_progress() for criteria in self.criteria)
        return total_progress / len(self.criteria)


@dataclass
class UserChallenge:
    """Desafio de um usuário"""
    user_id: str
    challenge_id: str
    status: ChallengeStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "user_id": self.user_id,
            "challenge_id": self.challenge_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.progress,
            "metadata": self.metadata
        }


class ChallengesSystem:
    """
    Sistema de desafios e missões.
    
    Características:
    - Múltiplos tipos de desafios
    - Critérios customizáveis
    - Progresso em tempo real
    - Recompensas automáticas
    - Integração com outros sistemas
    """
    
    def __init__(self, 
                 redis_config: Optional[Dict[str, Any]] = None,
                 enable_observability: bool = True):
        """
        Inicializa o sistema de desafios.
        
        Args:
            redis_config: Configuração do Redis para cache
            enable_observability: Habilita integração com observabilidade
        """
        self.challenges: Dict[str, Challenge] = {}
        self.user_challenges: Dict[str, List[UserChallenge]] = defaultdict(list)
        self.criteria_handlers: Dict[str, Callable] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Redis para cache distribuído
        self.redis_client = None
        if REDIS_AVAILABLE and redis_config:
            try:
                self.redis_client = redis.Redis(**redis_config)
                self.redis_client.ping()
                logger.info("Redis conectado para sistema de desafios")
            except Exception as e:
                logger.warning(f"Falha ao conectar Redis: {e}")
        
        # Observabilidade
        self.telemetry = None
        self.metrics = None
        self.tracing = None
        
        if enable_observability and OBSERVABILITY_AVAILABLE:
            try:
                self.telemetry = TelemetryManager()
                self.metrics = MetricsManager()
                self.tracing = TracingManager()
                logger.info("Observabilidade integrada ao sistema de desafios")
            except Exception as e:
                logger.warning(f"Falha ao integrar observabilidade: {e}")
        
        # Configurar handlers padrão
        self._setup_default_handlers()
        
        # Criar desafios padrão
        self._create_default_challenges()
        
        logger.info("Sistema de Desafios inicializado")
    
    def _setup_default_handlers(self):
        """Configura handlers padrão para critérios"""
        self.criteria_handlers = {
            "keyword_searches": self._get_keyword_searches_count,
            "executions_completed": self._get_executions_completed_count,
            "exports_made": self._get_exports_made_count,
            "login_streak": self._get_login_streak_days,
            "features_used": self._get_features_used_count,
            "referrals_made": self._get_referrals_made_count,
            "social_shares": self._get_social_shares_count,
            "total_points": self._get_total_points,
            "level_reached": self._get_user_level,
            "daily_goals": self._get_daily_goals_completed,
            "weekly_goals": self._get_weekly_goals_completed
        }
    
    def _create_default_challenges(self):
        """Cria desafios padrão do sistema"""
        now = datetime.utcnow()
        
        default_challenges = [
            # Desafios Diários
            Challenge(
                challenge_id="daily_search_10",
                name="Buscador Diário",
                description="Realize 10 buscas de keywords hoje",
                challenge_type=ChallengeType.DAILY,
                criteria=[
                    ChallengeCriteria(
                        criteria_type="keyword_searches",
                        target_value=10,
                        description="Realizar 10 buscas de keywords"
                    )
                ],
                points_reward=50,
                start_date=now.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=now.replace(hour=23, minute=59, second=59, microsecond=999999)
            ),
            
            Challenge(
                challenge_id="daily_execution_3",
                name="Executor Diário",
                description="Complete 3 execuções hoje",
                challenge_type=ChallengeType.DAILY,
                criteria=[
                    ChallengeCriteria(
                        criteria_type="executions_completed",
                        target_value=3,
                        description="Completar 3 execuções"
                    )
                ],
                points_reward=100,
                start_date=now.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date=now.replace(hour=23, minute=59, second=59, microsecond=999999)
            ),
            
            # Desafios Semanais
            Challenge(
                challenge_id="weekly_points_500",
                name="Coletor Semanal",
                description="Acumule 500 pontos esta semana",
                challenge_type=ChallengeType.WEEKLY,
                criteria=[
                    ChallengeCriteria(
                        criteria_type="total_points",
                        target_value=500,
                        description="Acumular 500 pontos"
                    )
                ],
                points_reward=200,
                start_date=now - timedelta(days=now.weekday()),
                end_date=now + timedelta(days=6-now.weekday())
            ),
            
            # Desafios de Conquista
            Challenge(
                challenge_id="achievement_level_5",
                name="Nível 5",
                description="Alcance o nível 5",
                challenge_type=ChallengeType.ACHIEVEMENT,
                criteria=[
                    ChallengeCriteria(
                        criteria_type="level_reached",
                        target_value=5,
                        description="Alcançar nível 5"
                    )
                ],
                points_reward=300,
                badge_reward="level_5_badge"
            ),
            
            Challenge(
                challenge_id="achievement_100_searches",
                name="Centenário de Buscas",
                description="Realize 100 buscas de keywords",
                challenge_type=ChallengeType.ACHIEVEMENT,
                criteria=[
                    ChallengeCriteria(
                        criteria_type="keyword_searches",
                        target_value=100,
                        description="Realizar 100 buscas de keywords"
                    )
                ],
                points_reward=500,
                badge_reward="search_master_badge"
            )
        ]
        
        for challenge in default_challenges:
            self.challenges[challenge.challenge_id] = challenge
    
    def create_challenge(self, challenge: Challenge) -> str:
        """
        Cria um novo desafio.
        
        Args:
            challenge: Definição do desafio
            
        Returns:
            ID do desafio criado
        """
        with self._lock:
            if challenge.challenge_id in self.challenges:
                raise ValueError(f"Desafio já existe: {challenge.challenge_id}")
            
            self.challenges[challenge.challenge_id] = challenge
            logger.info(f"[CHALLENGES] Desafio criado: {challenge.challenge_id} - {challenge.name}")
            return challenge.challenge_id
    
    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        """
        Retorna um desafio por ID.
        
        Args:
            challenge_id: ID do desafio
            
        Returns:
            Desafio ou None
        """
        with self._lock:
            return self.challenges.get(challenge_id)
    
    def list_challenges(self, 
                       challenge_type: Optional[ChallengeType] = None,
                       active_only: bool = True,
                       available_only: bool = True) -> List[Challenge]:
        """
        Lista desafios com filtros.
        
        Args:
            challenge_type: Filtrar por tipo
            active_only: Apenas desafios ativos
            available_only: Apenas desafios disponíveis
            
        Returns:
            Lista de desafios
        """
        with self._lock:
            filtered_challenges = []
            
            for challenge in self.challenges.values():
                if active_only and not challenge.is_active:
                    continue
                
                if available_only and not challenge.is_available():
                    continue
                
                if challenge_type and challenge.challenge_type != challenge_type:
                    continue
                
                filtered_challenges.append(challenge)
            
            return filtered_challenges
    
    def start_challenge(self, user_id: str, challenge_id: str) -> Optional[UserChallenge]:
        """
        Inicia um desafio para um usuário.
        
        Args:
            user_id: ID do usuário
            challenge_id: ID do desafio
            
        Returns:
            UserChallenge criada ou None
        """
        with self._lock:
            challenge = self.challenges.get(challenge_id)
            if not challenge:
                logger.warning(f"[CHALLENGES] Desafio não encontrado: {challenge_id}")
                return None
            
            if not challenge.is_available():
                logger.warning(f"[CHALLENGES] Desafio não disponível: {challenge_id}")
                return None
            
            # Verificar se já foi iniciado
            if self._has_user_challenge(user_id, challenge_id):
                logger.info(f"[CHALLENGES] Desafio já iniciado: {user_id} - {challenge_id}")
                return None
            
            # Criar user challenge
            user_challenge = UserChallenge(
                user_id=user_id,
                challenge_id=challenge_id,
                status=ChallengeStatus.ACTIVE,
                started_at=datetime.utcnow()
            )
            
            # Adicionar à lista do usuário
            self.user_challenges[user_id].append(user_challenge)
            
            # Cache no Redis
            if self.redis_client:
                self._cache_user_challenges(user_id)
            
            logger.info(f"[CHALLENGES] Desafio iniciado: {user_id} - {challenge.name}")
            return user_challenge
    
    def update_challenge_progress(self, 
                                 user_id: str,
                                 challenge_id: str,
                                 event_data: Dict[str, Any]) -> Optional[UserChallenge]:
        """
        Atualiza progresso de um desafio.
        
        Args:
            user_id: ID do usuário
            challenge_id: ID do desafio
            event_data: Dados do evento
            
        Returns:
            UserChallenge atualizada ou None
        """
        with self._lock:
            challenge = self.challenges.get(challenge_id)
            if not challenge:
                return None
            
            user_challenge = self._get_user_challenge(user_id, challenge_id)
            if not user_challenge or user_challenge.status != ChallengeStatus.ACTIVE:
                return None
            
            # Atualizar critérios
            self._update_challenge_criteria(challenge, user_id, event_data)
            
            # Atualizar progresso
            user_challenge.progress = challenge.get_overall_progress()
            
            # Verificar se foi completado
            if challenge.is_completed():
                user_challenge.status = ChallengeStatus.COMPLETED
                user_challenge.completed_at = datetime.utcnow()
                
                # Métricas
                if self.metrics:
                    self.metrics.increment_counter(
                        "challenge_completed_total",
                        1,
                        {"user_id": user_id, "challenge_id": challenge_id}
                    )
                
                logger.info(f"[CHALLENGES] Desafio completado: {user_id} - {challenge.name}")
            
            # Cache no Redis
            if self.redis_client:
                self._cache_user_challenges(user_id)
            
            return user_challenge
    
    def get_user_challenges(self, user_id: str) -> List[UserChallenge]:
        """
        Retorna desafios de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de desafios do usuário
        """
        with self._lock:
            # Tentar cache primeiro
            if self.redis_client:
                cached = self._get_cached_user_challenges(user_id)
                if cached:
                    return cached
            
            return self.user_challenges.get(user_id, [])
    
    def get_user_challenge_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Retorna progresso de desafios de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Progresso detalhado dos desafios
        """
        with self._lock:
            progress = {
                "total_challenges": len(self.challenges),
                "active_challenges": 0,
                "completed_challenges": 0,
                "challenges_by_type": defaultdict(int),
                "progress_details": []
            }
            
            user_challenges = self.get_user_challenges(user_id)
            user_challenge_ids = {uc.challenge_id for uc in user_challenges}
            
            for challenge in self.challenges.values():
                if not challenge.is_active or not challenge.is_available():
                    continue
                
                user_challenge = self._get_user_challenge(user_id, challenge.challenge_id)
                
                if user_challenge:
                    if user_challenge.status == ChallengeStatus.ACTIVE:
                        progress["active_challenges"] += 1
                    elif user_challenge.status == ChallengeStatus.COMPLETED:
                        progress["completed_challenges"] += 1
                    
                    progress["challenges_by_type"][challenge.challenge_type.value] += 1
                
                # Atualizar critérios para progresso atual
                self._update_challenge_criteria(challenge, user_id, {})
                
                progress["progress_details"].append({
                    "challenge_id": challenge.challenge_id,
                    "name": challenge.name,
                    "type": challenge.challenge_type.value,
                    "is_started": challenge.challenge_id in user_challenge_ids,
                    "status": user_challenge.status.value if user_challenge else "not_started",
                    "overall_progress": challenge.get_overall_progress(),
                    "criteria_progress": [c.to_dict() for c in challenge.criteria]
                })
            
            return progress
    
    def _has_user_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Verifica se usuário tem um desafio específico"""
        user_challenges = self.user_challenges.get(user_id, [])
        return any(uc.challenge_id == challenge_id for uc in user_challenges)
    
    def _get_user_challenge(self, user_id: str, challenge_id: str) -> Optional[UserChallenge]:
        """Retorna desafio específico de um usuário"""
        user_challenges = self.user_challenges.get(user_id, [])
        for uc in user_challenges:
            if uc.challenge_id == challenge_id:
                return uc
        return None
    
    def _update_challenge_criteria(self, challenge: Challenge, user_id: str, event_data: Dict[str, Any]):
        """Atualiza critérios de um desafio"""
        for criteria in challenge.criteria:
            handler = self.criteria_handlers.get(criteria.criteria_type)
            if handler:
                try:
                    current_value = handler(user_id, event_data)
                    criteria.current_value = current_value
                except Exception as e:
                    logger.warning(f"Erro ao atualizar critério {criteria.criteria_type}: {e}")
    
    # Handlers padrão para critérios
    def _get_keyword_searches_count(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de buscas de keywords"""
        return event_data.get("keyword_searches_count", 0)
    
    def _get_executions_completed_count(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de execuções completadas"""
        return event_data.get("executions_completed_count", 0)
    
    def _get_exports_made_count(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de exportações"""
        return event_data.get("exports_made_count", 0)
    
    def _get_login_streak_days(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna dias de streak de login"""
        return event_data.get("login_streak_days", 0)
    
    def _get_features_used_count(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de features usadas"""
        return event_data.get("features_used_count", 0)
    
    def _get_referrals_made_count(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de referências"""
        return event_data.get("referrals_made_count", 0)
    
    def _get_social_shares_count(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de compartilhamentos sociais"""
        return event_data.get("social_shares_count", 0)
    
    def _get_total_points(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna total de pontos"""
        return event_data.get("total_points", 0)
    
    def _get_user_level(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna nível do usuário"""
        return event_data.get("user_level", 1)
    
    def _get_daily_goals_completed(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de metas diárias completadas"""
        return event_data.get("daily_goals_completed", 0)
    
    def _get_weekly_goals_completed(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de metas semanais completadas"""
        return event_data.get("weekly_goals_completed", 0)
    
    def _cache_user_challenges(self, user_id: str):
        """Cache desafios do usuário no Redis"""
        if not self.redis_client:
            return
        
        try:
            user_challenges = self.user_challenges.get(user_id, [])
            cache_key = f"user_challenges:{user_id}"
            cache_data = json.dumps([uc.to_dict() for uc in user_challenges])
            self.redis_client.setex(cache_key, 3600, cache_data)  # 1 hora
        except Exception as e:
            logger.warning(f"Erro ao cachear desafios: {e}")
    
    def _get_cached_user_challenges(self, user_id: str) -> Optional[List[UserChallenge]]:
        """Obtém desafios do usuário do cache"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"user_challenges:{user_id}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data_list = json.loads(cached_data)
                return [UserChallenge(**data) for data in data_list]
        except Exception as e:
            logger.warning(f"Erro ao obter cache de desafios: {e}")
        
        return None


# Instância global
_challenges_system = None


def get_challenges_system() -> ChallengesSystem:
    """Retorna instância global do sistema de desafios"""
    global _challenges_system
    if _challenges_system is None:
        _challenges_system = ChallengesSystem()
    return _challenges_system 