from typing import Dict, List, Optional, Any
"""
Sistema de Gamificação - Omni Keywords Finder
============================================

Este módulo implementa um sistema completo de gamificação para aumentar
o engajamento dos usuários e motivar o uso da plataforma.

Características:
- Sistema de pontos e recompensas
- Badges e conquistas
- Leaderboards e rankings
- Desafios personalizados
- Progress tracking
- Integração com analytics

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: GAMIFICATION_001
"""

from .points_system import PointsSystem, PointsManager
from .badges_system import BadgesSystem, Badge, BadgeType
from .leaderboards import LeaderboardsSystem, Leaderboard
from .challenges import ChallengesSystem, Challenge, ChallengeType
from .rewards import RewardsSystem, Reward, RewardType
from .progress_tracking import ProgressTracker, UserProgress

__all__ = [
    'PointsSystem', 'PointsManager',
    'BadgesSystem', 'Badge', 'BadgeType',
    'LeaderboardsSystem', 'Leaderboard',
    'ChallengesSystem', 'Challenge', 'ChallengeType',
    'RewardsSystem', 'Reward', 'RewardType',
    'ProgressTracker', 'UserProgress'
] 