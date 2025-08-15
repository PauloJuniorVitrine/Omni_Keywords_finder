"""
Sistema de Progress Tracking - Omni Keywords Finder
==================================================

Este módulo implementa o sistema de tracking de progresso dos usuários,
incluindo user journeys, milestones, analytics e notificações.

Autor: Paulo Júnior
Data: 2025-01-27
Tracing ID: PROGRESS_TRACKING_001
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
import uuid

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


class ProgressType(Enum):
    """Tipos de progresso"""
    USER_JOURNEY = "user_journey"
    MILESTONE = "milestone"
    ACHIEVEMENT = "achievement"
    SKILL = "skill"
    LEVEL = "level"
    CUSTOM = "custom"


class MilestoneStatus(Enum):
    """Status dos milestones"""
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Milestone:
    """Milestone de progresso"""
    milestone_id: str
    name: str
    description: str
    progress_type: ProgressType
    target_value: float
    current_value: float = 0.0
    status: MilestoneStatus = MilestoneStatus.LOCKED
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    criteria: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "milestone_id": self.milestone_id,
            "name": self.name,
            "description": self.description,
            "progress_type": self.progress_type.value,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "status": self.status.value,
            "rewards": self.rewards,
            "criteria": self.criteria,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "progress_percentage": (self.current_value / self.target_value * 100) if self.target_value > 0 else 0
        }


@dataclass
class UserJourney:
    """Journey do usuário"""
    journey_id: str
    user_id: str
    journey_name: str
    description: str
    milestones: List[Milestone] = field(default_factory=list)
    current_stage: int = 0
    total_stages: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "journey_id": self.journey_id,
            "user_id": self.user_id,
            "journey_name": self.journey_name,
            "description": self.description,
            "milestones": [m.to_dict() for m in self.milestones],
            "current_stage": self.current_stage,
            "total_stages": self.total_stages,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "progress_percentage": (self.current_stage / self.total_stages * 100) if self.total_stages > 0 else 0
        }


@dataclass
class ProgressAnalytics:
    """Analytics de progresso"""
    user_id: str
    total_milestones: int = 0
    completed_milestones: int = 0
    total_journeys: int = 0
    completed_journeys: int = 0
    average_completion_time: float = 0.0
    engagement_score: float = 0.0
    last_activity: datetime = field(default_factory=datetime.utcnow)
    progress_trend: str = "stable"
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "user_id": self.user_id,
            "total_milestones": self.total_milestones,
            "completed_milestones": self.completed_milestones,
            "total_journeys": self.total_journeys,
            "completed_journeys": self.completed_journeys,
            "average_completion_time": self.average_completion_time,
            "engagement_score": self.engagement_score,
            "last_activity": self.last_activity.isoformat(),
            "progress_trend": self.progress_trend,
            "recommendations": self.recommendations,
            "completion_rate": (self.completed_milestones / self.total_milestones * 100) if self.total_milestones > 0 else 0
        }


class ProgressTracker:
    """
    Sistema principal de tracking de progresso
    
    Características:
    - Thread-safe para alta concorrência
    - Cache distribuído com Redis
    - Integração com observabilidade
    - Analytics em tempo real
    - Notificações automáticas
    """
    
    def __init__(self, 
                 redis_config: Optional[Dict[str, Any]] = None,
                 enable_observability: bool = True,
                 enable_notifications: bool = True):
        """
        Inicializa o progress tracker
        
        Args:
            redis_config: Configuração do Redis
            enable_observability: Habilita integração com observabilidade
            enable_notifications: Habilita notificações automáticas
        """
        self.user_journeys: Dict[str, List[UserJourney]] = defaultdict(list)
        self.user_milestones: Dict[str, List[Milestone]] = defaultdict(list)
        self.progress_analytics: Dict[str, ProgressAnalytics] = {}
        self.notification_callbacks: List[Callable] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Redis para cache distribuído
        self.redis_client = None
        if REDIS_AVAILABLE and redis_config:
            try:
                self.redis_client = redis.Redis(**redis_config)
                self.redis_client.ping()
                logger.info("Redis conectado para cache distribuído")
            except Exception as e:
                logger.warning(f"Falha ao conectar Redis: {e}")
        
        # Observabilidade
        self.telemetry = None
        self.tracing = None
        self.metrics = None
        
        if enable_observability and OBSERVABILITY_AVAILABLE:
            try:
                self.telemetry = TelemetryManager()
                self.tracing = TracingManager()
                self.metrics = MetricsManager()
                logger.info("Observabilidade integrada ao Progress Tracking")
            except Exception as e:
                logger.warning(f"Falha ao integrar observabilidade: {e}")
        
        # Notificações
        self.enable_notifications = enable_notifications
        
        # Milestones padrão
        self._init_default_milestones()
        
        logger.info("Progress Tracker inicializado")
    
    def _init_default_milestones(self):
        """Inicializa milestones padrão"""
        self.default_milestones = [
            Milestone(
                milestone_id="first_login",
                name="Primeiro Login",
                description="Realizar o primeiro login na plataforma",
                progress_type=ProgressType.USER_JOURNEY,
                target_value=1.0,
                rewards=[{"type": "points", "value": 10, "description": "10 pontos"}],
                criteria=["Realizar primeiro login"]
            ),
            Milestone(
                milestone_id="first_search",
                name="Primeira Busca",
                description="Realizar a primeira busca de keywords",
                progress_type=ProgressType.USER_JOURNEY,
                target_value=1.0,
                rewards=[{"type": "points", "value": 25, "description": "25 pontos"}],
                criteria=["Realizar primeira busca de keywords"]
            ),
            Milestone(
                milestone_id="first_export",
                name="Primeira Exportação",
                description="Exportar resultados pela primeira vez",
                progress_type=ProgressType.USER_JOURNEY,
                target_value=1.0,
                rewards=[{"type": "points", "value": 50, "description": "50 pontos"}],
                criteria=["Exportar resultados"]
            ),
            Milestone(
                milestone_id="keyword_master",
                name="Mestre das Keywords",
                description="Analisar mais de 1000 keywords",
                progress_type=ProgressType.MILESTONE,
                target_value=1000.0,
                rewards=[{"type": "badge", "value": "keyword_master", "description": "Badge Mestre das Keywords"}],
                criteria=["Analisar 1000 keywords"]
            ),
            Milestone(
                milestone_id="daily_streak",
                name="Sequência Diária",
                description="Fazer login por 7 dias consecutivos",
                progress_type=ProgressType.MILESTONE,
                target_value=7.0,
                rewards=[{"type": "points", "value": 100, "description": "100 pontos"}],
                criteria=["Login por 7 dias consecutivos"]
            )
        ]
    
    def create_user_journey(self,
                           user_id: str,
                           journey_name: str,
                           description: str,
                           milestones: Optional[List[Milestone]] = None) -> str:
        """
        Cria uma nova journey para o usuário
        
        Args:
            user_id: ID do usuário
            journey_name: Nome da journey
            description: Descrição da journey
            milestones: Lista de milestones (opcional)
            
        Returns:
            ID da journey criada
        """
        with self._lock:
            journey_id = f"journey_{uuid.uuid4().hex[:8]}"
            
            # Usar milestones padrão se não fornecidos
            if milestones is None:
                milestones = [m for m in self.default_milestones]
            
            journey = UserJourney(
                journey_id=journey_id,
                user_id=user_id,
                journey_name=journey_name,
                description=description,
                milestones=milestones,
                total_stages=len(milestones)
            )
            
            self.user_journeys[user_id].append(journey)
            
            # Persistir no Redis
            if self.redis_client:
                self._save_journey_to_redis(journey)
            
            # Métricas
            if self.metrics:
                self.metrics.increment_counter("progress_journeys_created")
            
            logger.info(f"Journey criada: {journey_id} para usuário {user_id}")
            return journey_id
    
    def update_progress(self,
                       user_id: str,
                       milestone_id: str,
                       progress_value: float,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Atualiza o progresso de um milestone
        
        Args:
            user_id: ID do usuário
            milestone_id: ID do milestone
            progress_value: Valor do progresso
            metadata: Metadados adicionais
            
        Returns:
            True se atualizado com sucesso
        """
        with self._lock:
            # Encontrar milestone
            milestone = self._find_milestone(user_id, milestone_id)
            if not milestone:
                logger.warning(f"Milestone {milestone_id} não encontrado para usuário {user_id}")
                return False
            
            # Atualizar progresso
            old_value = milestone.current_value
            milestone.current_value = min(progress_value, milestone.target_value)
            
            # Verificar se completou
            if milestone.current_value >= milestone.target_value and milestone.status != MilestoneStatus.COMPLETED:
                milestone.status = MilestoneStatus.COMPLETED
                milestone.completed_at = datetime.utcnow()
                
                # Notificar conclusão
                if self.enable_notifications:
                    self._notify_milestone_completed(user_id, milestone)
                
                # Métricas
                if self.metrics:
                    self.metrics.increment_counter("progress_milestones_completed")
            
            # Atualizar status
            elif milestone.current_value > 0 and milestone.status == MilestoneStatus.LOCKED:
                milestone.status = MilestoneStatus.IN_PROGRESS
            
            # Atualizar metadados
            if metadata:
                milestone.metadata.update(metadata)
            
            # Persistir no Redis
            if self.redis_client:
                self._save_milestone_to_redis(user_id, milestone)
            
            # Atualizar analytics
            self._update_analytics(user_id)
            
            logger.info(f"Progresso atualizado: {milestone_id} para {user_id} - {old_value} -> {milestone.current_value}")
            return True
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém progresso completo do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados de progresso do usuário
        """
        with self._lock:
            journeys = self.user_journeys.get(user_id, [])
            milestones = self.user_milestones.get(user_id, [])
            analytics = self.progress_analytics.get(user_id)
            
            return {
                "user_id": user_id,
                "journeys": [counter.to_dict() for counter in journeys],
                "milestones": [m.to_dict() for m in milestones],
                "analytics": analytics.to_dict() if analytics else None,
                "last_updated": datetime.utcnow().isoformat()
            }
    
    def get_progress_analytics(self, user_id: str) -> Optional[ProgressAnalytics]:
        """
        Obtém analytics de progresso do usuário
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Analytics de progresso
        """
        with self._lock:
            return self.progress_analytics.get(user_id)
    
    def add_notification_callback(self, callback: Callable[[str, Milestone], None]):
        """
        Adiciona callback para notificações
        
        Args:
            callback: Função de callback
        """
        self.notification_callbacks.append(callback)
    
    def _find_milestone(self, user_id: str, milestone_id: str) -> Optional[Milestone]:
        """Encontra milestone específico"""
        # Buscar em journeys
        for journey in self.user_journeys.get(user_id, []):
            for milestone in journey.milestones:
                if milestone.milestone_id == milestone_id:
                    return milestone
        
        # Buscar em milestones independentes
        for milestone in self.user_milestones.get(user_id, []):
            if milestone.milestone_id == milestone_id:
                return milestone
        
        return None
    
    def _update_analytics(self, user_id: str):
        """Atualiza analytics do usuário"""
        journeys = self.user_journeys.get(user_id, [])
        milestones = self.user_milestones.get(user_id, [])
        
        # Calcular estatísticas
        total_milestones = sum(len(counter.milestones) for counter in journeys) + len(milestones)
        completed_milestones = sum(
            sum(1 for m in counter.milestones if m.status == MilestoneStatus.COMPLETED)
            for counter in journeys
        ) + sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED)
        
        total_journeys = len(journeys)
        completed_journeys = sum(1 for counter in journeys if counter.completed_at is not None)
        
        # Calcular tempo médio de conclusão
        completion_times = []
        for journey in journeys:
            if journey.completed_at:
                completion_time = (journey.completed_at - journey.started_at).total_seconds() / 3600  # horas
                completion_times.append(completion_time)
        
        average_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0.0
        
        # Calcular score de engajamento
        engagement_score = min(100.0, (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0.0)
        
        # Determinar tendência
        progress_trend = "stable"
        if engagement_score > 80:
            progress_trend = "excellent"
        elif engagement_score > 60:
            progress_trend = "good"
        elif engagement_score > 40:
            progress_trend = "fair"
        else:
            progress_trend = "needs_improvement"
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(user_id, engagement_score, completed_milestones, total_milestones)
        
        # Criar/atualizar analytics
        analytics = ProgressAnalytics(
            user_id=user_id,
            total_milestones=total_milestones,
            completed_milestones=completed_milestones,
            total_journeys=total_journeys,
            completed_journeys=completed_journeys,
            average_completion_time=average_completion_time,
            engagement_score=engagement_score,
            last_activity=datetime.utcnow(),
            progress_trend=progress_trend,
            recommendations=recommendations
        )
        
        self.progress_analytics[user_id] = analytics
    
    def _generate_recommendations(self, user_id: str, engagement_score: float, completed: int, total: int) -> List[str]:
        """Gera recomendações personalizadas"""
        recommendations = []
        
        if engagement_score < 30:
            recommendations.append("Complete o tutorial para entender melhor a plataforma")
            recommendations.append("Tente fazer sua primeira busca de keywords")
        
        elif engagement_score < 60:
            recommendations.append("Explore diferentes tipos de análise de keywords")
            recommendations.append("Experimente exportar seus resultados")
        
        elif engagement_score < 80:
            recommendations.append("Tente usar recursos avançados como clustering")
            recommendations.append("Participe de desafios para ganhar mais pontos")
        
        else:
            recommendations.append("Parabéns! Você está dominando a plataforma")
            recommendations.append("Ajude outros usuários compartilhando suas experiências")
        
        return recommendations
    
    def _notify_milestone_completed(self, user_id: str, milestone: Milestone):
        """Notifica conclusão de milestone"""
        for callback in self.notification_callbacks:
            try:
                callback(user_id, milestone)
            except Exception as e:
                logger.error(f"Erro no callback de notificação: {e}")
    
    def _save_journey_to_redis(self, journey: UserJourney):
        """Salva journey no Redis"""
        try:
            key = f"progress:journey:{journey.journey_id}"
            self.redis_client.setex(key, 86400, json.dumps(journey.to_dict()))  # 24h TTL
        except Exception as e:
            logger.error(f"Erro ao salvar journey no Redis: {e}")
    
    def _save_milestone_to_redis(self, user_id: str, milestone: Milestone):
        """Salva milestone no Redis"""
        try:
            key = f"progress:milestone:{user_id}:{milestone.milestone_id}"
            self.redis_client.setex(key, 86400, json.dumps(milestone.to_dict()))  # 24h TTL
        except Exception as e:
            logger.error(f"Erro ao salvar milestone no Redis: {e}")
    
    def export_progress_report(self, user_id: str, format: str = "json") -> str:
        """
        Exporta relatório de progresso
        
        Args:
            user_id: ID do usuário
            format: Formato do relatório (json, csv)
            
        Returns:
            Relatório em formato solicitado
        """
        progress_data = self.get_user_progress(user_id)
        
        if format == "json":
            return json.dumps(progress_data, indent=2, ensure_ascii=False)
        elif format == "csv":
            # Implementar conversão para CSV
            return "Formato CSV não implementado ainda"
        else:
            return "Formato não suportado"
    
    def get_leaderboard_progress(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retorna leaderboard baseado em progresso
        
        Args:
            limit: Limite de usuários
            
        Returns:
            Lista de usuários ordenados por progresso
        """
        with self._lock:
            leaderboard = []
            
            for user_id, analytics in self.progress_analytics.items():
                leaderboard.append({
                    "user_id": user_id,
                    "engagement_score": analytics.engagement_score,
                    "completed_milestones": analytics.completed_milestones,
                    "total_milestones": analytics.total_milestones,
                    "completion_rate": analytics.completed_milestones / analytics.total_milestones * 100 if analytics.total_milestones > 0 else 0,
                    "last_activity": analytics.last_activity.isoformat()
                })
            
            # Ordenar por engagement score (maior primeiro)
            leaderboard.sort(key=lambda value: value["engagement_score"], reverse=True)
            
            return leaderboard[:limit]


# Instância global
_progress_tracker = None


def get_progress_tracker() -> ProgressTracker:
    """Retorna instância global do progress tracker"""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker()
    return _progress_tracker 