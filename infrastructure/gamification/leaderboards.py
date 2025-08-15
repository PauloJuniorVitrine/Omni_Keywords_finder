"""
Sistema de Leaderboards e Rankings
==================================

Este módulo implementa o sistema de leaderboards e rankings para gamificação,
incluindo diferentes tipos de rankings, atualizações em tempo real e competições.

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: GAMIFICATION_004
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
import heapq

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


class LeaderboardType(Enum):
    """Tipos de leaderboard"""
    POINTS = "points"
    LEVEL = "level"
    BADGES = "badges"
    ACTIVITY = "activity"
    STREAK = "streak"
    CUSTOM = "custom"


class LeaderboardPeriod(Enum):
    """Períodos de leaderboard"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"
    SEASONAL = "seasonal"


@dataclass
class LeaderboardEntry:
    """Entrada em um leaderboard"""
    user_id: str
    score: Union[int, float]
    rank: int = 0
    previous_rank: Optional[int] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "user_id": self.user_id,
            "score": self.score,
            "rank": self.rank,
            "previous_rank": self.previous_rank,
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class Leaderboard:
    """Definição de um leaderboard"""
    leaderboard_id: str
    name: str
    description: str
    leaderboard_type: LeaderboardType
    period: LeaderboardPeriod
    max_entries: int = 1000
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    reset_schedule: Optional[str] = None  # Cron expression
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "leaderboard_id": self.leaderboard_id,
            "name": self.name,
            "description": self.description,
            "leaderboard_type": self.leaderboard_type.value,
            "period": self.period.value,
            "max_entries": self.max_entries,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "reset_schedule": self.reset_schedule,
            "metadata": self.metadata
        }


class LeaderboardsSystem:
    """
    Sistema de leaderboards e rankings.
    
    Características:
    - Múltiplos tipos de leaderboard
    - Atualizações em tempo real
    - Rankings históricos
    - Competições sazonais
    - Integração com outros sistemas
    """
    
    def __init__(self, 
                 redis_config: Optional[Dict[str, Any]] = None,
                 enable_observability: bool = True):
        """
        Inicializa o sistema de leaderboards.
        
        Args:
            redis_config: Configuração do Redis para cache
            enable_observability: Habilita integração com observabilidade
        """
        self.leaderboards: Dict[str, Leaderboard] = {}
        self.entries: Dict[str, List[LeaderboardEntry]] = defaultdict(list)
        self.score_handlers: Dict[str, Callable] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Redis para cache distribuído
        self.redis_client = None
        if REDIS_AVAILABLE and redis_config:
            try:
                self.redis_client = redis.Redis(**redis_config)
                self.redis_client.ping()
                logger.info("Redis conectado para sistema de leaderboards")
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
                logger.info("Observabilidade integrada ao sistema de leaderboards")
            except Exception as e:
                logger.warning(f"Falha ao integrar observabilidade: {e}")
        
        # Configurar handlers padrão
        self._setup_default_handlers()
        
        # Criar leaderboards padrão
        self._create_default_leaderboards()
        
        logger.info("Sistema de Leaderboards inicializado")
    
    def _setup_default_handlers(self):
        """Configura handlers padrão para scores"""
        self.score_handlers = {
            "total_points": self._get_total_points_score,
            "user_level": self._get_user_level_score,
            "badges_count": self._get_badges_count_score,
            "activity_score": self._get_activity_score,
            "login_streak": self._get_login_streak_score,
            "executions_completed": self._get_executions_completed_score,
            "keyword_searches": self._get_keyword_searches_score,
            "exports_made": self._get_exports_made_score
        }
    
    def _create_default_leaderboards(self):
        """Cria leaderboards padrão do sistema"""
        default_leaderboards = [
            # Leaderboard de Pontos
            Leaderboard(
                leaderboard_id="total_points_all_time",
                name="Ranking Geral de Pontos",
                description="Ranking geral baseado no total de pontos acumulados",
                leaderboard_type=LeaderboardType.POINTS,
                period=LeaderboardPeriod.ALL_TIME,
                max_entries=1000
            ),
            
            Leaderboard(
                leaderboard_id="total_points_monthly",
                name="Ranking Mensal de Pontos",
                description="Ranking mensal baseado em pontos ganhos no mês",
                leaderboard_type=LeaderboardType.POINTS,
                period=LeaderboardPeriod.MONTHLY,
                max_entries=500,
                reset_schedule="0 0 1 * *"  # Primeiro dia do mês
            ),
            
            # Leaderboard de Níveis
            Leaderboard(
                leaderboard_id="user_level_all_time",
                name="Ranking de Níveis",
                description="Ranking baseado no nível atual dos usuários",
                leaderboard_type=LeaderboardType.LEVEL,
                period=LeaderboardPeriod.ALL_TIME,
                max_entries=1000
            ),
            
            # Leaderboard de Badges
            Leaderboard(
                leaderboard_id="badges_count_all_time",
                name="Ranking de Badges",
                description="Ranking baseado no número de badges conquistadas",
                leaderboard_type=LeaderboardType.BADGES,
                period=LeaderboardPeriod.ALL_TIME,
                max_entries=500
            ),
            
            # Leaderboard de Atividade
            Leaderboard(
                leaderboard_id="activity_weekly",
                name="Ranking de Atividade Semanal",
                description="Ranking baseado na atividade semanal",
                leaderboard_type=LeaderboardType.ACTIVITY,
                period=LeaderboardPeriod.WEEKLY,
                max_entries=300,
                reset_schedule="0 0 * * 0"  # Domingo à meia-noite
            ),
            
            # Leaderboard de Streak
            Leaderboard(
                leaderboard_id="login_streak_all_time",
                name="Ranking de Streak de Login",
                description="Ranking baseado no streak de login mais longo",
                leaderboard_type=LeaderboardType.STREAK,
                period=LeaderboardPeriod.ALL_TIME,
                max_entries=200
            )
        ]
        
        for leaderboard in default_leaderboards:
            self.leaderboards[leaderboard.leaderboard_id] = leaderboard
    
    def create_leaderboard(self, leaderboard: Leaderboard) -> str:
        """
        Cria um novo leaderboard.
        
        Args:
            leaderboard: Definição do leaderboard
            
        Returns:
            ID do leaderboard criado
        """
        with self._lock:
            if leaderboard.leaderboard_id in self.leaderboards:
                raise ValueError(f"Leaderboard já existe: {leaderboard.leaderboard_id}")
            
            self.leaderboards[leaderboard.leaderboard_id] = leaderboard
            logger.info(f"[LEADERBOARD] Leaderboard criado: {leaderboard.leaderboard_id} - {leaderboard.name}")
            return leaderboard.leaderboard_id
    
    def get_leaderboard(self, leaderboard_id: str) -> Optional[Leaderboard]:
        """
        Retorna um leaderboard por ID.
        
        Args:
            leaderboard_id: ID do leaderboard
            
        Returns:
            Leaderboard ou None
        """
        with self._lock:
            return self.leaderboards.get(leaderboard_id)
    
    def list_leaderboards(self, 
                         leaderboard_type: Optional[LeaderboardType] = None,
                         period: Optional[LeaderboardPeriod] = None,
                         active_only: bool = True) -> List[Leaderboard]:
        """
        Lista leaderboards com filtros.
        
        Args:
            leaderboard_type: Filtrar por tipo
            period: Filtrar por período
            active_only: Apenas leaderboards ativos
            
        Returns:
            Lista de leaderboards
        """
        with self._lock:
            filtered_leaderboards = []
            
            for leaderboard in self.leaderboards.values():
                if active_only and not leaderboard.is_active:
                    continue
                
                if leaderboard_type and leaderboard.leaderboard_type != leaderboard_type:
                    continue
                
                if period and leaderboard.period != period:
                    continue
                
                filtered_leaderboards.append(leaderboard)
            
            return filtered_leaderboards
    
    def update_score(self, 
                    leaderboard_id: str,
                    user_id: str,
                    score: Union[int, float],
                    metadata: Optional[Dict[str, Any]] = None) -> Optional[LeaderboardEntry]:
        """
        Atualiza score de um usuário em um leaderboard.
        
        Args:
            leaderboard_id: ID do leaderboard
            user_id: ID do usuário
            score: Novo score
            metadata: Metadados adicionais
            
        Returns:
            Entrada atualizada ou None
        """
        with self._lock:
            leaderboard = self.leaderboards.get(leaderboard_id)
            if not leaderboard:
                logger.warning(f"[LEADERBOARD] Leaderboard não encontrado: {leaderboard_id}")
                return None
            
            if not leaderboard.is_active:
                logger.warning(f"[LEADERBOARD] Leaderboard inativo: {leaderboard_id}")
                return None
            
            # Encontrar entrada existente
            existing_entry = None
            entries = self.entries[leaderboard_id]
            
            for entry in entries:
                if entry.user_id == user_id:
                    existing_entry = entry
                    break
            
            if existing_entry:
                # Atualizar entrada existente
                previous_rank = existing_entry.rank
                existing_entry.score = score
                existing_entry.last_updated = datetime.utcnow()
                if metadata:
                    existing_entry.metadata.update(metadata)
            else:
                # Criar nova entrada
                existing_entry = LeaderboardEntry(
                    user_id=user_id,
                    score=score,
                    last_updated=datetime.utcnow(),
                    metadata=metadata or {}
                )
                entries.append(existing_entry)
            
            # Reordenar leaderboard
            self._reorder_leaderboard(leaderboard_id)
            
            # Cache no Redis
            if self.redis_client:
                self._cache_leaderboard(leaderboard_id)
            
            # Métricas
            if self.metrics:
                self.metrics.increment_counter(
                    "leaderboard_score_updated_total",
                    1,
                    {"leaderboard_id": leaderboard_id, "user_id": user_id}
                )
            
            logger.info(f"[LEADERBOARD] Score atualizado: {leaderboard_id} - {user_id}: {score}")
            return existing_entry
    
    def get_leaderboard_entries(self, 
                               leaderboard_id: str,
                               limit: int = 100,
                               offset: int = 0) -> List[LeaderboardEntry]:
        """
        Retorna entradas de um leaderboard.
        
        Args:
            leaderboard_id: ID do leaderboard
            limit: Limite de entradas
            offset: Offset para paginação
            
        Returns:
            Lista de entradas ordenadas
        """
        with self._lock:
            # Tentar cache primeiro
            if self.redis_client:
                cached = self._get_cached_leaderboard(leaderboard_id)
                if cached:
                    return cached[offset:offset + limit]
            
            entries = self.entries.get(leaderboard_id, [])
            return entries[offset:offset + limit]
    
    def get_user_rank(self, leaderboard_id: str, user_id: str) -> Optional[int]:
        """
        Retorna rank de um usuário em um leaderboard.
        
        Args:
            leaderboard_id: ID do leaderboard
            user_id: ID do usuário
            
        Returns:
            Rank do usuário ou None
        """
        with self._lock:
            entries = self.entries.get(leaderboard_id, [])
            
            for entry in entries:
                if entry.user_id == user_id:
                    return entry.rank
            
            return None
    
    def get_user_entry(self, leaderboard_id: str, user_id: str) -> Optional[LeaderboardEntry]:
        """
        Retorna entrada de um usuário em um leaderboard.
        
        Args:
            leaderboard_id: ID do leaderboard
            user_id: ID do usuário
            
        Returns:
            Entrada do usuário ou None
        """
        with self._lock:
            entries = self.entries.get(leaderboard_id, [])
            
            for entry in entries:
                if entry.user_id == user_id:
                    return entry
            
            return None
    
    def get_top_users(self, 
                     leaderboard_id: str,
                     limit: int = 10) -> List[LeaderboardEntry]:
        """
        Retorna top usuários de um leaderboard.
        
        Args:
            leaderboard_id: ID do leaderboard
            limit: Limite de usuários
            
        Returns:
            Lista dos top usuários
        """
        return self.get_leaderboard_entries(leaderboard_id, limit=limit)
    
    def get_leaderboard_stats(self, leaderboard_id: str) -> Dict[str, Any]:
        """
        Retorna estatísticas de um leaderboard.
        
        Args:
            leaderboard_id: ID do leaderboard
            
        Returns:
            Estatísticas do leaderboard
        """
        with self._lock:
            entries = self.entries.get(leaderboard_id, [])
            
            if not entries:
                return {
                    "total_entries": 0,
                    "average_score": 0,
                    "highest_score": 0,
                    "lowest_score": 0,
                    "last_updated": None
                }
            
            scores = [entry.score for entry in entries]
            
            stats = {
                "total_entries": len(entries),
                "average_score": sum(scores) / len(scores),
                "highest_score": max(scores),
                "lowest_score": min(scores),
                "last_updated": max(entry.last_updated for entry in entries).isoformat()
            }
            
            return stats
    
    def reset_leaderboard(self, leaderboard_id: str) -> bool:
        """
        Reseta um leaderboard.
        
        Args:
            leaderboard_id: ID do leaderboard
            
        Returns:
            True se resetado com sucesso
        """
        with self._lock:
            if leaderboard_id not in self.leaderboards:
                logger.warning(f"[LEADERBOARD] Leaderboard não encontrado: {leaderboard_id}")
                return False
            
            # Limpar entradas
            self.entries[leaderboard_id] = []
            
            # Limpar cache
            if self.redis_client:
                try:
                    cache_key = f"leaderboard:{leaderboard_id}"
                    self.redis_client.delete(cache_key)
                except Exception as e:
                    logger.warning(f"Erro ao limpar cache: {e}")
            
            logger.info(f"[LEADERBOARD] Leaderboard resetado: {leaderboard_id}")
            return True
    
    def update_scores_from_data(self, 
                               leaderboard_id: str,
                               user_data: Dict[str, Any]) -> List[LeaderboardEntry]:
        """
        Atualiza scores baseado em dados de usuários.
        
        Args:
            leaderboard_id: ID do leaderboard
            user_data: Dados dos usuários
            
        Returns:
            Lista de entradas atualizadas
        """
        with self._lock:
            leaderboard = self.leaderboards.get(leaderboard_id)
            if not leaderboard:
                return []
            
            handler = self.score_handlers.get(leaderboard.leaderboard_type.value)
            if not handler:
                logger.warning(f"Handler não encontrado para tipo: {leaderboard.leaderboard_type.value}")
                return []
            
            updated_entries = []
            
            for user_id, data in user_data.items():
                try:
                    score = handler(user_id, data)
                    entry = self.update_score(leaderboard_id, user_id, score, data)
                    if entry:
                        updated_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Erro ao atualizar score para {user_id}: {e}")
            
            return updated_entries
    
    def _reorder_leaderboard(self, leaderboard_id: str):
        """Reordena um leaderboard"""
        entries = self.entries[leaderboard_id]
        
        # Ordenar por score (decrescente)
        entries.sort(key=lambda value: value.score, reverse=True)
        
        # Atualizar ranks
        for index, entry in enumerate(entries):
            entry.previous_rank = entry.rank
            entry.rank = index + 1
    
    # Handlers padrão para scores
    def _get_total_points_score(self, user_id: str, data: Dict[str, Any]) -> int:
        """Retorna score baseado em pontos totais"""
        return data.get("total_points", 0)
    
    def _get_user_level_score(self, user_id: str, data: Dict[str, Any]) -> int:
        """Retorna score baseado no nível do usuário"""
        return data.get("user_level", 1)
    
    def _get_badges_count_score(self, user_id: str, data: Dict[str, Any]) -> int:
        """Retorna score baseado no número de badges"""
        return data.get("badges_count", 0)
    
    def _get_activity_score(self, user_id: str, data: Dict[str, Any]) -> int:
        """Retorna score baseado na atividade"""
        # Fórmula: (logins * 10) + (executions * 5) + (searches * 2)
        logins = data.get("login_count", 0)
        executions = data.get("executions_completed", 0)
        searches = data.get("keyword_searches", 0)
        
        return (logins * 10) + (executions * 5) + (searches * 2)
    
    def _get_login_streak_score(self, user_id: str, data: Dict[str, Any]) -> int:
        """Retorna score baseado no streak de login"""
        return data.get("login_streak_days", 0)
    
    def _get_executions_completed_score(self, user_id: str, data: Dict[str, Any]) -> int:
        """Retorna score baseado em execuções completadas"""
        return data.get("executions_completed", 0)
    
    def _get_keyword_searches_score(self, user_id: str, data: Dict[str, Any]) -> int:
        """Retorna score baseado em buscas de keywords"""
        return data.get("keyword_searches", 0)
    
    def _get_exports_made_score(self, user_id: str, data: Dict[str, Any]) -> int:
        """Retorna score baseado em exportações"""
        return data.get("exports_made", 0)
    
    def _cache_leaderboard(self, leaderboard_id: str):
        """Cache leaderboard no Redis"""
        if not self.redis_client:
            return
        
        try:
            entries = self.entries.get(leaderboard_id, [])
            cache_key = f"leaderboard:{leaderboard_id}"
            cache_data = json.dumps([entry.to_dict() for entry in entries])
            self.redis_client.setex(cache_key, 1800, cache_data)  # 30 minutos
        except Exception as e:
            logger.warning(f"Erro ao cachear leaderboard: {e}")
    
    def _get_cached_leaderboard(self, leaderboard_id: str) -> Optional[List[LeaderboardEntry]]:
        """Obtém leaderboard do cache"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"leaderboard:{leaderboard_id}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data_list = json.loads(cached_data)
                return [LeaderboardEntry(**data) for data in data_list]
        except Exception as e:
            logger.warning(f"Erro ao obter cache de leaderboard: {e}")
        
        return None


# Instância global
_leaderboards_system = None


def get_leaderboards_system() -> LeaderboardsSystem:
    """Retorna instância global do sistema de leaderboards"""
    global _leaderboards_system
    if _leaderboards_system is None:
        _leaderboards_system = LeaderboardsSystem()
    return _leaderboards_system 