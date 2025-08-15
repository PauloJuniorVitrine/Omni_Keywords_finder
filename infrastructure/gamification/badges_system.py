"""
Sistema de Badges e Conquistas
==============================

Este módulo implementa o sistema de badges e conquistas para gamificação,
incluindo diferentes tipos de badges, critérios de desbloqueio e progresso.

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: GAMIFICATION_003
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


class BadgeType(Enum):
    """Tipos de badges"""
    ACHIEVEMENT = "achievement"
    MILESTONE = "milestone"
    COLLECTION = "collection"
    EVENT = "event"
    SPECIAL = "special"
    SEASONAL = "seasonal"


class BadgeRarity(Enum):
    """Raridade das badges"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class BadgeCriteria:
    """Critérios para desbloquear uma badge"""
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
class Badge:
    """Definição de uma badge"""
    badge_id: str
    name: str
    description: str
    badge_type: BadgeType
    rarity: BadgeRarity
    criteria: List[BadgeCriteria]
    icon_url: Optional[str] = None
    points_reward: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "badge_id": self.badge_id,
            "name": self.name,
            "description": self.description,
            "badge_type": self.badge_type.value,
            "rarity": self.rarity.value,
            "criteria": [c.to_dict() for c in self.criteria],
            "icon_url": self.icon_url,
            "points_reward": self.points_reward,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    def is_unlocked(self) -> bool:
        """Verifica se a badge foi desbloqueada"""
        return all(criteria.is_completed() for criteria in self.criteria)
    
    def get_overall_progress(self) -> float:
        """Retorna progresso geral da badge"""
        if not self.criteria:
            return 1.0
        
        total_progress = sum(criteria.get_progress() for criteria in self.criteria)
        return total_progress / len(self.criteria)


@dataclass
class UserBadge:
    """Badge de um usuário"""
    user_id: str
    badge_id: str
    unlocked_at: datetime
    progress: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "user_id": self.user_id,
            "badge_id": self.badge_id,
            "unlocked_at": self.unlocked_at.isoformat(),
            "progress": self.progress,
            "metadata": self.metadata
        }


class BadgesSystem:
    """
    Sistema de badges e conquistas.
    
    Características:
    - Múltiplos tipos de badges
    - Critérios customizáveis
    - Progresso em tempo real
    - Integração com pontos
    - Sistema de raridade
    """
    
    def __init__(self, 
                 redis_config: Optional[Dict[str, Any]] = None,
                 enable_observability: bool = True):
        """
        Inicializa o sistema de badges.
        
        Args:
            redis_config: Configuração do Redis para cache
            enable_observability: Habilita integração com observabilidade
        """
        self.badges: Dict[str, Badge] = {}
        self.user_badges: Dict[str, List[UserBadge]] = defaultdict(list)
        self.criteria_handlers: Dict[str, Callable] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Redis para cache distribuído
        self.redis_client = None
        if REDIS_AVAILABLE and redis_config:
            try:
                self.redis_client = redis.Redis(**redis_config)
                self.redis_client.ping()
                logger.info("Redis conectado para sistema de badges")
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
                logger.info("Observabilidade integrada ao sistema de badges")
            except Exception as e:
                logger.warning(f"Falha ao integrar observabilidade: {e}")
        
        # Configurar handlers padrão
        self._setup_default_handlers()
        
        # Criar badges padrão
        self._create_default_badges()
        
        logger.info("Sistema de Badges inicializado")
    
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
            "challenges_completed": self._get_challenges_completed_count,
            "total_points": self._get_total_points,
            "level_reached": self._get_user_level,
            "daily_goals": self._get_daily_goals_completed,
            "weekly_goals": self._get_weekly_goals_completed
        }
    
    def _create_default_badges(self):
        """Cria badges padrão do sistema"""
        default_badges = [
            # Badges de Primeiros Passos
            Badge(
                badge_id="first_search",
                name="Primeira Busca",
                description="Realizou sua primeira busca de keywords",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.COMMON,
                criteria=[
                    BadgeCriteria(
                        criteria_type="keyword_searches",
                        target_value=1,
                        description="Realizar 1 busca de keywords"
                    )
                ],
                points_reward=50
            ),
            
            Badge(
                badge_id="first_execution",
                name="Primeira Execução",
                description="Completou sua primeira execução de análise",
                badge_type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.COMMON,
                criteria=[
                    BadgeCriteria(
                        criteria_type="executions_completed",
                        target_value=1,
                        description="Completar 1 execução"
                    )
                ],
                points_reward=100
            ),
            
            # Badges de Milestone
            Badge(
                badge_id="search_master",
                name="Mestre das Buscas",
                description="Realizou 100 buscas de keywords",
                badge_type=BadgeType.MILESTONE,
                rarity=BadgeRarity.UNCOMMON,
                criteria=[
                    BadgeCriteria(
                        criteria_type="keyword_searches",
                        target_value=100,
                        description="Realizar 100 buscas de keywords"
                    )
                ],
                points_reward=200
            ),
            
            Badge(
                badge_id="execution_expert",
                name="Especialista em Execuções",
                description="Completou 50 execuções",
                badge_type=BadgeType.MILESTONE,
                rarity=BadgeRarity.UNCOMMON,
                criteria=[
                    BadgeCriteria(
                        criteria_type="executions_completed",
                        target_value=50,
                        description="Completar 50 execuções"
                    )
                ],
                points_reward=500
            ),
            
            # Badges de Coleção
            Badge(
                badge_id="feature_explorer",
                name="Explorador de Features",
                description="Usou 5 features diferentes",
                badge_type=BadgeType.COLLECTION,
                rarity=BadgeRarity.RARE,
                criteria=[
                    BadgeCriteria(
                        criteria_type="features_used",
                        target_value=5,
                        description="Usar 5 features diferentes"
                    )
                ],
                points_reward=300
            ),
            
            # Badges de Evento
            Badge(
                badge_id="login_streak_7",
                name="Consistente",
                description="Manteve login por 7 dias consecutivos",
                badge_type=BadgeType.EVENT,
                rarity=BadgeRarity.UNCOMMON,
                criteria=[
                    BadgeCriteria(
                        criteria_type="login_streak",
                        target_value=7,
                        description="Login por 7 dias consecutivos"
                    )
                ],
                points_reward=150
            ),
            
            # Badges Especiais
            Badge(
                badge_id="points_collector",
                name="Coletor de Pontos",
                description="Acumulou 1000 pontos",
                badge_type=BadgeType.SPECIAL,
                rarity=BadgeRarity.EPIC,
                criteria=[
                    BadgeCriteria(
                        criteria_type="total_points",
                        target_value=1000,
                        description="Acumular 1000 pontos"
                    )
                ],
                points_reward=1000
            ),
            
            Badge(
                badge_id="level_10",
                name="Nível 10",
                description="Alcançou o nível 10",
                badge_type=BadgeType.MILESTONE,
                rarity=BadgeRarity.RARE,
                criteria=[
                    BadgeCriteria(
                        criteria_type="level_reached",
                        target_value=10,
                        description="Alcançar nível 10"
                    )
                ],
                points_reward=750
            )
        ]
        
        for badge in default_badges:
            self.badges[badge.badge_id] = badge
    
    def create_badge(self, badge: Badge) -> str:
        """
        Cria uma nova badge.
        
        Args:
            badge: Definição da badge
            
        Returns:
            ID da badge criada
        """
        with self._lock:
            if badge.badge_id in self.badges:
                raise ValueError(f"Badge já existe: {badge.badge_id}")
            
            self.badges[badge.badge_id] = badge
            logger.info(f"[BADGES] Badge criada: {badge.badge_id} - {badge.name}")
            return badge.badge_id
    
    def get_badge(self, badge_id: str) -> Optional[Badge]:
        """
        Retorna uma badge por ID.
        
        Args:
            badge_id: ID da badge
            
        Returns:
            Badge ou None
        """
        with self._lock:
            return self.badges.get(badge_id)
    
    def list_badges(self, 
                   badge_type: Optional[BadgeType] = None,
                   rarity: Optional[BadgeRarity] = None,
                   active_only: bool = True) -> List[Badge]:
        """
        Lista badges com filtros.
        
        Args:
            badge_type: Filtrar por tipo
            rarity: Filtrar por raridade
            active_only: Apenas badges ativas
            
        Returns:
            Lista de badges
        """
        with self._lock:
            filtered_badges = []
            
            for badge in self.badges.values():
                if active_only and not badge.is_active:
                    continue
                
                if badge_type and badge.badge_type != badge_type:
                    continue
                
                if rarity and badge.rarity != rarity:
                    continue
                
                filtered_badges.append(badge)
            
            return filtered_badges
    
    def check_user_progress(self, user_id: str, event_data: Dict[str, Any]) -> List[Badge]:
        """
        Verifica progresso do usuário e retorna badges desbloqueadas.
        
        Args:
            user_id: ID do usuário
            event_data: Dados do evento
            
        Returns:
            Lista de badges desbloqueadas
        """
        with self._lock:
            unlocked_badges = []
            
            for badge in self.badges.values():
                if not badge.is_active:
                    continue
                
                # Verificar se já foi desbloqueada
                if self._has_user_badge(user_id, badge.badge_id):
                    continue
                
                # Atualizar critérios
                self._update_badge_criteria(badge, user_id, event_data)
                
                # Verificar se foi desbloqueada
                if badge.is_unlocked():
                    unlocked_badges.append(badge)
            
            return unlocked_badges
    
    def unlock_badge(self, user_id: str, badge_id: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[UserBadge]:
        """
        Desbloqueia uma badge para um usuário.
        
        Args:
            user_id: ID do usuário
            badge_id: ID da badge
            metadata: Metadados adicionais
            
        Returns:
            UserBadge criada ou None
        """
        with self._lock:
            badge = self.badges.get(badge_id)
            if not badge:
                logger.warning(f"[BADGES] Badge não encontrada: {badge_id}")
                return None
            
            if not badge.is_active:
                logger.warning(f"[BADGES] Badge inativa: {badge_id}")
                return None
            
            # Verificar se já foi desbloqueada
            if self._has_user_badge(user_id, badge_id):
                logger.info(f"[BADGES] Badge já desbloqueada: {user_id} - {badge_id}")
                return None
            
            # Criar user badge
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge_id,
                unlocked_at=datetime.utcnow(),
                progress=badge.get_overall_progress(),
                metadata=metadata or {}
            )
            
            # Adicionar à lista do usuário
            self.user_badges[user_id].append(user_badge)
            
            # Cache no Redis
            if self.redis_client:
                self._cache_user_badges(user_id)
            
            # Métricas
            if self.metrics:
                self.metrics.increment_counter(
                    "badge_unlocked_total",
                    1,
                    {"user_id": user_id, "badge_id": badge_id, "rarity": badge.rarity.value}
                )
            
            logger.info(f"[BADGES] Badge desbloqueada: {user_id} - {badge.name}")
            return user_badge
    
    def get_user_badges(self, user_id: str) -> List[UserBadge]:
        """
        Retorna badges de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Lista de badges do usuário
        """
        with self._lock:
            # Tentar cache primeiro
            if self.redis_client:
                cached = self._get_cached_user_badges(user_id)
                if cached:
                    return cached
            
            return self.user_badges.get(user_id, [])
    
    def get_user_badge_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Retorna progresso de badges de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Progresso detalhado das badges
        """
        with self._lock:
            progress = {
                "total_badges": len(self.badges),
                "unlocked_badges": 0,
                "badges_by_type": defaultdict(int),
                "badges_by_rarity": defaultdict(int),
                "progress_details": []
            }
            
            user_badges = self.get_user_badges(user_id)
            unlocked_badge_ids = {ub.badge_id for ub in user_badges}
            
            for badge in self.badges.values():
                if not badge.is_active:
                    continue
                
                is_unlocked = badge.badge_id in unlocked_badge_ids
                if is_unlocked:
                    progress["unlocked_badges"] += 1
                    progress["badges_by_type"][badge.badge_type.value] += 1
                    progress["badges_by_rarity"][badge.rarity.value] += 1
                
                # Atualizar critérios para progresso atual
                self._update_badge_criteria(badge, user_id, {})
                
                progress["progress_details"].append({
                    "badge_id": badge.badge_id,
                    "name": badge.name,
                    "type": badge.badge_type.value,
                    "rarity": badge.rarity.value,
                    "is_unlocked": is_unlocked,
                    "overall_progress": badge.get_overall_progress(),
                    "criteria_progress": [c.to_dict() for c in badge.criteria]
                })
            
            return progress
    
    def get_badge_leaderboard(self, badge_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retorna leaderboard de uma badge específica.
        
        Args:
            badge_id: ID da badge
            limit: Limite de usuários
            
        Returns:
            Lista de usuários ordenados por data de desbloqueio
        """
        with self._lock:
            leaderboard = []
            
            for user_id, user_badges in self.user_badges.items():
                for user_badge in user_badges:
                    if user_badge.badge_id == badge_id:
                        leaderboard.append({
                            "user_id": user_id,
                            "unlocked_at": user_badge.unlocked_at.isoformat(),
                            "progress": user_badge.progress
                        })
                        break
            
            # Ordenar por data de desbloqueio (mais antigo primeiro)
            leaderboard.sort(key=lambda value: value["unlocked_at"])
            
            return leaderboard[:limit]
    
    def _has_user_badge(self, user_id: str, badge_id: str) -> bool:
        """Verifica se usuário tem uma badge específica"""
        user_badges = self.user_badges.get(user_id, [])
        return any(ub.badge_id == badge_id for ub in user_badges)
    
    def _update_badge_criteria(self, badge: Badge, user_id: str, event_data: Dict[str, Any]):
        """Atualiza critérios de uma badge"""
        for criteria in badge.criteria:
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
        # Implementação simplificada - em produção seria integrada com analytics
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
    
    def _get_challenges_completed_count(self, user_id: str, event_data: Dict[str, Any]) -> int:
        """Retorna número de desafios completados"""
        return event_data.get("challenges_completed_count", 0)
    
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
    
    def _cache_user_badges(self, user_id: str):
        """Cache badges do usuário no Redis"""
        if not self.redis_client:
            return
        
        try:
            user_badges = self.user_badges.get(user_id, [])
            cache_key = f"user_badges:{user_id}"
            cache_data = json.dumps([ub.to_dict() for ub in user_badges])
            self.redis_client.setex(cache_key, 3600, cache_data)  # 1 hora
        except Exception as e:
            logger.warning(f"Erro ao cachear badges: {e}")
    
    def _get_cached_user_badges(self, user_id: str) -> Optional[List[UserBadge]]:
        """Obtém badges do usuário do cache"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"user_badges:{user_id}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data_list = json.loads(cached_data)
                return [UserBadge(**data) for data in data_list]
        except Exception as e:
            logger.warning(f"Erro ao obter cache de badges: {e}")
        
        return None


# Instância global
_badges_system = None


def get_badges_system() -> BadgesSystem:
    """Retorna instância global do sistema de badges"""
    global _badges_system
    if _badges_system is None:
        _badges_system = BadgesSystem()
    return _badges_system 