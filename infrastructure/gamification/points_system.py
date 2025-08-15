"""
Sistema de Pontos e Recompensas
===============================

Este módulo implementa o sistema de pontos e recompensas para gamificação,
incluindo diferentes tipos de pontos, multiplicadores e recompensas.

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: GAMIFICATION_002
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
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


class PointsType(Enum):
    """Tipos de pontos disponíveis"""
    EXPERIENCE = "experience"
    ACHIEVEMENT = "achievement"
    DAILY = "daily"
    WEEKLY = "weekly"
    BONUS = "bonus"
    REFERRAL = "referral"
    SOCIAL = "social"


class PointsSource(Enum):
    """Fontes de pontos"""
    KEYWORD_SEARCH = "keyword_search"
    EXECUTION_COMPLETE = "execution_complete"
    EXPORT_DATA = "export_data"
    LOGIN_STREAK = "login_streak"
    FEATURE_USAGE = "feature_usage"
    REFERRAL = "referral"
    SOCIAL_SHARE = "social_share"
    CHALLENGE_COMPLETE = "challenge_complete"
    BADGE_EARNED = "badge_earned"
    DAILY_GOAL = "daily_goal"


@dataclass
class PointsTransaction:
    """Transação de pontos"""
    transaction_id: str
    user_id: str
    points_type: PointsType
    points_amount: int
    source: PointsSource
    description: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    multiplier: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "points_type": self.points_type.value,
            "points_amount": self.points_amount,
            "source": self.source.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "multiplier": self.multiplier
        }


@dataclass
class UserPoints:
    """Pontos de um usuário"""
    user_id: str
    total_points: int = 0
    experience_points: int = 0
    achievement_points: int = 0
    daily_points: int = 0
    weekly_points: int = 0
    bonus_points: int = 0
    referral_points: int = 0
    social_points: int = 0
    level: int = 1
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "user_id": self.user_id,
            "total_points": self.total_points,
            "experience_points": self.experience_points,
            "achievement_points": self.achievement_points,
            "daily_points": self.daily_points,
            "weekly_points": self.weekly_points,
            "bonus_points": self.bonus_points,
            "referral_points": self.referral_points,
            "social_points": self.social_points,
            "level": self.level,
            "last_updated": self.last_updated.isoformat()
        }


class PointsSystem:
    """
    Sistema principal de pontos e recompensas.
    
    Características:
    - Múltiplos tipos de pontos
    - Sistema de multiplicadores
    - Transações rastreáveis
    - Níveis de usuário
    - Integração com observabilidade
    """
    
    def __init__(self, 
                 redis_config: Optional[Dict[str, Any]] = None,
                 enable_observability: bool = True):
        """
        Inicializa o sistema de pontos.
        
        Args:
            redis_config: Configuração do Redis para cache
            enable_observability: Habilita integração com observabilidade
        """
        self.users_points: Dict[str, UserPoints] = {}
        self.transactions: List[PointsTransaction] = []
        self.multipliers: Dict[str, float] = {}
        self.level_thresholds: Dict[int, int] = self._generate_level_thresholds()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Redis para cache distribuído
        self.redis_client = None
        if REDIS_AVAILABLE and redis_config:
            try:
                self.redis_client = redis.Redis(**redis_config)
                self.redis_client.ping()
                logger.info("Redis conectado para sistema de pontos")
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
                logger.info("Observabilidade integrada ao sistema de pontos")
            except Exception as e:
                logger.warning(f"Falha ao integrar observabilidade: {e}")
        
        # Configurações padrão
        self.default_points = {
            PointsSource.KEYWORD_SEARCH: 10,
            PointsSource.EXECUTION_COMPLETE: 50,
            PointsSource.EXPORT_DATA: 25,
            PointsSource.LOGIN_STREAK: 5,
            PointsSource.FEATURE_USAGE: 15,
            PointsSource.REFERRAL: 100,
            PointsSource.SOCIAL_SHARE: 20,
            PointsSource.CHALLENGE_COMPLETE: 200,
            PointsSource.BADGE_EARNED: 150,
            PointsSource.DAILY_GOAL: 75
        }
        
        logger.info("Sistema de Pontos inicializado")
    
    def _generate_level_thresholds(self) -> Dict[int, int]:
        """Gera thresholds de níveis"""
        thresholds = {}
        for level in range(1, 101):  # 100 níveis
            if level == 1:
                thresholds[level] = 0
            else:
                # Fórmula exponencial para aumentar dificuldade
                thresholds[level] = int(100 * (level ** 1.5))
        return thresholds
    
    def add_points(self, 
                   user_id: str,
                   points_type: PointsType,
                   source: PointsSource,
                   description: str,
                   points_amount: Optional[int] = None,
                   multiplier: float = 1.0,
                   metadata: Optional[Dict[str, Any]] = None) -> PointsTransaction:
        """
        Adiciona pontos para um usuário.
        
        Args:
            user_id: ID do usuário
            points_type: Tipo de pontos
            source: Fonte dos pontos
            description: Descrição da transação
            points_amount: Quantidade de pontos (usa padrão se None)
            multiplier: Multiplicador de pontos
            metadata: Metadados adicionais
            
        Returns:
            Transação criada
        """
        with self._lock:
            try:
                # Usar pontos padrão se não especificado
                if points_amount is None:
                    points_amount = self.default_points.get(source, 10)
                
                # Aplicar multiplicador
                final_points = int(points_amount * multiplier)
                
                # Criar transação
                transaction = PointsTransaction(
                    transaction_id=f"tx_{int(time.time())}_{user_id}",
                    user_id=user_id,
                    points_type=points_type,
                    points_amount=final_points,
                    source=source,
                    description=description,
                    timestamp=datetime.utcnow(),
                    metadata=metadata or {},
                    multiplier=multiplier
                )
                
                # Atualizar pontos do usuário
                self._update_user_points(user_id, points_type, final_points)
                
                # Adicionar transação
                self.transactions.append(transaction)
                
                # Verificar level up
                self._check_level_up(user_id)
                
                # Cache no Redis
                if self.redis_client:
                    self._cache_user_points(user_id)
                
                # Métricas
                if self.metrics:
                    self.metrics.increment_counter(
                        "points_earned_total",
                        final_points,
                        {"user_id": user_id, "points_type": points_type.value, "source": source.value}
                    )
                
                logger.info(f"[POINTS] {user_id} ganhou {final_points} pontos ({points_type.value})")
                return transaction
                
            except Exception as e:
                logger.error(f"[POINTS] Erro ao adicionar pontos: {e}")
                raise
    
    def _update_user_points(self, user_id: str, points_type: PointsType, amount: int):
        """Atualiza pontos do usuário"""
        if user_id not in self.users_points:
            self.users_points[user_id] = UserPoints(user_id=user_id)
        
        user_points = self.users_points[user_id]
        
        # Atualizar pontos específicos
        if points_type == PointsType.EXPERIENCE:
            user_points.experience_points += amount
        elif points_type == PointsType.ACHIEVEMENT:
            user_points.achievement_points += amount
        elif points_type == PointsType.DAILY:
            user_points.daily_points += amount
        elif points_type == PointsType.WEEKLY:
            user_points.weekly_points += amount
        elif points_type == PointsType.BONUS:
            user_points.bonus_points += amount
        elif points_type == PointsType.REFERRAL:
            user_points.referral_points += amount
        elif points_type == PointsType.SOCIAL:
            user_points.social_points += amount
        
        # Atualizar total
        user_points.total_points += amount
        user_points.last_updated = datetime.utcnow()
    
    def _check_level_up(self, user_id: str):
        """Verifica se o usuário subiu de nível"""
        user_points = self.users_points[user_id]
        current_level = user_points.level
        
        # Verificar próximo nível
        for level, threshold in self.level_thresholds.items():
            if level > current_level and user_points.total_points >= threshold:
                user_points.level = level
                logger.info(f"[POINTS] {user_id} subiu para nível {level}!")
                
                # Métricas
                if self.metrics:
                    self.metrics.increment_counter(
                        "level_up_total",
                        1,
                        {"user_id": user_id, "level": str(level)}
                    )
                break
    
    def get_user_points(self, user_id: str) -> Optional[UserPoints]:
        """
        Retorna pontos de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Pontos do usuário ou None
        """
        with self._lock:
            # Tentar cache primeiro
            if self.redis_client:
                cached = self._get_cached_user_points(user_id)
                if cached:
                    return cached
            
            return self.users_points.get(user_id)
    
    def get_user_level(self, user_id: str) -> int:
        """
        Retorna nível de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Nível do usuário
        """
        user_points = self.get_user_points(user_id)
        return user_points.level if user_points else 1
    
    def get_user_transactions(self, 
                             user_id: str,
                             limit: int = 50,
                             points_type: Optional[PointsType] = None) -> List[PointsTransaction]:
        """
        Retorna transações de um usuário.
        
        Args:
            user_id: ID do usuário
            limit: Limite de transações
            points_type: Filtrar por tipo de pontos
            
        Returns:
            Lista de transações
        """
        with self._lock:
            user_transactions = [
                tx for tx in self.transactions 
                if tx.user_id == user_id
            ]
            
            if points_type:
                user_transactions = [
                    tx for tx in user_transactions
                    if tx.points_type == points_type
                ]
            
            # Ordenar por timestamp (mais recente primeiro)
            user_transactions.sort(key=lambda value: value.timestamp, reverse=True)
            
            return user_transactions[:limit]
    
    def get_leaderboard(self, 
                       points_type: Optional[PointsType] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retorna leaderboard de pontos.
        
        Args:
            points_type: Tipo de pontos para ranking
            limit: Limite de usuários
            
        Returns:
            Lista de usuários ordenados por pontos
        """
        with self._lock:
            leaderboard = []
            
            for user_id, user_points in self.users_points.items():
                if points_type:
                    if points_type == PointsType.EXPERIENCE:
                        points = user_points.experience_points
                    elif points_type == PointsType.ACHIEVEMENT:
                        points = user_points.achievement_points
                    elif points_type == PointsType.DAILY:
                        points = user_points.daily_points
                    elif points_type == PointsType.WEEKLY:
                        points = user_points.weekly_points
                    elif points_type == PointsType.BONUS:
                        points = user_points.bonus_points
                    elif points_type == PointsType.REFERRAL:
                        points = user_points.referral_points
                    elif points_type == PointsType.SOCIAL:
                        points = user_points.social_points
                    else:
                        points = user_points.total_points
                else:
                    points = user_points.total_points
                
                leaderboard.append({
                    "user_id": user_id,
                    "points": points,
                    "level": user_points.level,
                    "last_updated": user_points.last_updated.isoformat()
                })
            
            # Ordenar por pontos (maior primeiro)
            leaderboard.sort(key=lambda value: value["points"], reverse=True)
            
            return leaderboard[:limit]
    
    def set_multiplier(self, user_id: str, multiplier: float, duration_minutes: int = 60):
        """
        Define multiplicador de pontos para um usuário.
        
        Args:
            user_id: ID do usuário
            multiplier: Multiplicador (ex: 2.0 = dobro de pontos)
            duration_minutes: Duração em minutos
        """
        with self._lock:
            expiry_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
            self.multipliers[user_id] = {
                "multiplier": multiplier,
                "expires_at": expiry_time
            }
            
            logger.info(f"[POINTS] Multiplicador {multiplier}value definido para {user_id} por {duration_minutes} minutos")
    
    def get_multiplier(self, user_id: str) -> float:
        """
        Retorna multiplicador ativo de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Multiplicador ativo ou 1.0
        """
        with self._lock:
            if user_id not in self.multipliers:
                return 1.0
            
            multiplier_data = self.multipliers[user_id]
            if datetime.utcnow() > multiplier_data["expires_at"]:
                # Multiplicador expirado
                del self.multipliers[user_id]
                return 1.0
            
            return multiplier_data["multiplier"]
    
    def reset_daily_points(self):
        """Reseta pontos diários de todos os usuários"""
        with self._lock:
            for user_points in self.users_points.values():
                user_points.daily_points = 0
                user_points.last_updated = datetime.utcnow()
            
            logger.info("[POINTS] Pontos diários resetados")
    
    def reset_weekly_points(self):
        """Reseta pontos semanais de todos os usuários"""
        with self._lock:
            for user_points in self.users_points.values():
                user_points.weekly_points = 0
                user_points.last_updated = datetime.utcnow()
            
            logger.info("[POINTS] Pontos semanais resetados")
    
    def export_user_data(self, user_id: str, format: str = "json") -> Union[str, Dict[str, Any]]:
        """
        Exporta dados de pontos de um usuário.
        
        Args:
            user_id: ID do usuário
            format: Formato de exportação (json, csv)
            
        Returns:
            Dados exportados
        """
        user_points = self.get_user_points(user_id)
        if not user_points:
            return {} if format == "json" else ""
        
        transactions = self.get_user_transactions(user_id, limit=1000)
        
        data = {
            "user_points": user_points.to_dict(),
            "transactions": [tx.to_dict() for tx in transactions],
            "exported_at": datetime.utcnow().isoformat()
        }
        
        if format == "json":
            return data
        elif format == "csv":
            return self._export_to_csv(data)
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _export_to_csv(self, data: Dict[str, Any]) -> str:
        """Exporta dados para CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "transaction_id", "user_id", "points_type", "points_amount",
            "source", "description", "timestamp", "multiplier"
        ])
        
        # Dados
        for tx in data["transactions"]:
            writer.writerow([
                tx["transaction_id"], tx["user_id"], tx["points_type"],
                tx["points_amount"], tx["source"], tx["description"],
                tx["timestamp"], tx["multiplier"]
            ])
        
        return output.getvalue()
    
    def _cache_user_points(self, user_id: str):
        """Cache pontos do usuário no Redis"""
        if not self.redis_client:
            return
        
        try:
            user_points = self.users_points.get(user_id)
            if user_points:
                cache_key = f"user_points:{user_id}"
                cache_data = json.dumps(user_points.to_dict())
                self.redis_client.setex(cache_key, 3600, cache_data)  # 1 hora
        except Exception as e:
            logger.warning(f"Erro ao cachear pontos: {e}")
    
    def _get_cached_user_points(self, user_id: str) -> Optional[UserPoints]:
        """Obtém pontos do usuário do cache"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"user_points:{user_id}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return UserPoints(**data)
        except Exception as e:
            logger.warning(f"Erro ao obter cache de pontos: {e}")
        
        return None


class PointsManager:
    """
    Gerenciador de pontos com funcionalidades avançadas.
    
    Características:
    - Gerenciamento de eventos
    - Cálculo automático de pontos
    - Integração com outros sistemas
    """
    
    def __init__(self, points_system: PointsSystem):
        """
        Inicializa o gerenciador.
        
        Args:
            points_system: Sistema de pontos
        """
        self.points_system = points_system
        self.event_handlers = self._setup_event_handlers()
        
        logger.info("Gerenciador de Pontos inicializado")
    
    def _setup_event_handlers(self) -> Dict[str, callable]:
        """Configura handlers de eventos"""
        return {
            "keyword_search": self._handle_keyword_search,
            "execution_complete": self._handle_execution_complete,
            "export_data": self._handle_export_data,
            "login_streak": self._handle_login_streak,
            "feature_usage": self._handle_feature_usage,
            "referral": self._handle_referral,
            "social_share": self._handle_social_share,
            "challenge_complete": self._handle_challenge_complete,
            "badge_earned": self._handle_badge_earned,
            "daily_goal": self._handle_daily_goal
        }
    
    def handle_event(self, event_type: str, user_id: str, event_data: Dict[str, Any]) -> Optional[PointsTransaction]:
        """
        Processa um evento e adiciona pontos automaticamente.
        
        Args:
            event_type: Tipo do evento
            user_id: ID do usuário
            event_data: Dados do evento
            
        Returns:
            Transação criada ou None
        """
        handler = self.event_handlers.get(event_type)
        if handler:
            return handler(user_id, event_data)
        else:
            logger.warning(f"Handler não encontrado para evento: {event_type}")
            return None
    
    def _handle_keyword_search(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para busca de keywords"""
        multiplier = self.points_system.get_multiplier(user_id)
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.EXPERIENCE,
            source=PointsSource.KEYWORD_SEARCH,
            description=f"Busca de keywords: {event_data.get('query', 'N/A')}",
            multiplier=multiplier,
            metadata=event_data
        )
    
    def _handle_execution_complete(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para execução completa"""
        multiplier = self.points_system.get_multiplier(user_id)
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.EXPERIENCE,
            source=PointsSource.EXECUTION_COMPLETE,
            description=f"Execução completa: {event_data.get('execution_type', 'N/A')}",
            multiplier=multiplier,
            metadata=event_data
        )
    
    def _handle_export_data(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para exportação de dados"""
        multiplier = self.points_system.get_multiplier(user_id)
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.EXPERIENCE,
            source=PointsSource.EXPORT_DATA,
            description=f"Exportação: {event_data.get('export_format', 'N/A')}",
            multiplier=multiplier,
            metadata=event_data
        )
    
    def _handle_login_streak(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para streak de login"""
        streak_days = event_data.get('streak_days', 1)
        bonus_multiplier = min(streak_days * 0.1, 1.0)  # Máximo 100% de bônus
        
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.DAILY,
            source=PointsSource.LOGIN_STREAK,
            description=f"Login streak: {streak_days} dias",
            multiplier=1.0 + bonus_multiplier,
            metadata=event_data
        )
    
    def _handle_feature_usage(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para uso de features"""
        multiplier = self.points_system.get_multiplier(user_id)
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.EXPERIENCE,
            source=PointsSource.FEATURE_USAGE,
            description=f"Uso de feature: {event_data.get('feature', 'N/A')}",
            multiplier=multiplier,
            metadata=event_data
        )
    
    def _handle_referral(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para referências"""
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.REFERRAL,
            source=PointsSource.REFERRAL,
            description=f"Referência: {event_data.get('referred_user', 'N/A')}",
            metadata=event_data
        )
    
    def _handle_social_share(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para compartilhamento social"""
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.SOCIAL,
            source=PointsSource.SOCIAL_SHARE,
            description=f"Compartilhamento: {event_data.get('platform', 'N/A')}",
            metadata=event_data
        )
    
    def _handle_challenge_complete(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para desafio completo"""
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.ACHIEVEMENT,
            source=PointsSource.CHALLENGE_COMPLETE,
            description=f"Desafio completo: {event_data.get('challenge_name', 'N/A')}",
            metadata=event_data
        )
    
    def _handle_badge_earned(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para badge conquistada"""
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.ACHIEVEMENT,
            source=PointsSource.BADGE_EARNED,
            description=f"Badge conquistada: {event_data.get('badge_name', 'N/A')}",
            metadata=event_data
        )
    
    def _handle_daily_goal(self, user_id: str, event_data: Dict[str, Any]) -> PointsTransaction:
        """Handler para meta diária"""
        return self.points_system.add_points(
            user_id=user_id,
            points_type=PointsType.DAILY,
            source=PointsSource.DAILY_GOAL,
            description=f"Meta diária: {event_data.get('goal_name', 'N/A')}",
            metadata=event_data
        )


# Instância global
_points_system = None
_points_manager = None


def get_points_system() -> PointsSystem:
    """Retorna instância global do sistema de pontos"""
    global _points_system
    if _points_system is None:
        _points_system = PointsSystem()
    return _points_system


def get_points_manager() -> PointsManager:
    """Retorna instância global do gerenciador de pontos"""
    global _points_manager
    if _points_manager is None:
        _points_manager = PointsManager(get_points_system())
    return _points_manager 