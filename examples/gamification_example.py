"""
Exemplo Prático - Sistema de Gamificação
========================================

Este exemplo demonstra o uso completo do sistema de gamificação do Omni Keywords Finder,
incluindo pontos, badges, leaderboards, desafios e recompensas.

Características demonstradas:
- Sistema de pontos e recompensas
- Badges e conquistas
- Leaderboards e rankings
- Desafios e missões
- Progress tracking
- Integração entre sistemas

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: GAMIFICATION_EXAMPLE_001
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import random

# Imports do sistema de gamificação
from infrastructure.gamification.points_system import (
    PointsSystem, PointsManager, PointsType, PointsSource
)
from infrastructure.gamification.badges_system import (
    BadgesSystem, BadgeType, BadgeRarity
)
from infrastructure.gamification.leaderboards import (
    LeaderboardsSystem, LeaderboardType, LeaderboardPeriod
)
from infrastructure.gamification.challenges import (
    ChallengesSystem, ChallengeType, ChallengeStatus
)
from infrastructure.gamification.rewards import (
    RewardsSystem, RewardType, RewardStatus
)
from infrastructure.gamification.progress_tracking import (
    ProgressTracker, ProgressType, GoalStatus
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GamificationExample:
    """
    Exemplo prático do sistema de gamificação.
    
    Demonstra todas as funcionalidades implementadas:
    - Sistema de pontos
    - Badges e conquistas
    - Leaderboards
    - Desafios
    - Recompensas
    - Progress tracking
    """
    
    def __init__(self):
        """Inicializa o exemplo."""
        self.points_system = PointsSystem()
        self.points_manager = PointsManager(self.points_system)
        self.badges_system = BadgesSystem()
        self.leaderboards_system = LeaderboardsSystem()
        self.challenges_system = ChallengesSystem()
        self.rewards_system = RewardsSystem()
        self.progress_tracker = ProgressTracker()
        
        # Dados simulados para demonstração
        self.simulated_users = []
        self.simulated_events = []
        
        logger.info("[GAMIFICATION_EXAMPLE] Sistema inicializado")
    
    def setup_simulated_data(self):
        """Configura dados simulados para demonstração."""
        logger.info("[GAMIFICATION_EXAMPLE] Configurando dados simulados...")
        
        # Criar usuários simulados
        for index in range(50):
            user = {
                "user_id": f"user_{index:03d}",
                "signup_date": datetime.now() - timedelta(days=random.randint(1, 365)),
                "plan": random.choice(["free", "premium", "enterprise"]),
                "country": random.choice(["BR", "US", "CA", "UK", "DE"]),
                "source": random.choice(["organic", "paid", "referral", "social"])
            }
            self.simulated_users.append(user)
        
        # Criar eventos simulados
        event_types = [
            "keyword_search",
            "execution_complete",
            "export_data",
            "login_streak",
            "feature_usage",
            "referral",
            "social_share"
        ]
        
        for _ in range(500):
            user = random.choice(self.simulated_users)
            event_type = random.choice(event_types)
            
            event_data = self._generate_event_data(event_type, user)
            
            event = {
                "event_type": event_type,
                "user_id": user["user_id"],
                "data": event_data,
                "timestamp": datetime.now() - timedelta(
                    hours=random.randint(0, 24),
                    minutes=random.randint(0, 60)
                )
            }
            self.simulated_events.append(event)
        
        logger.info(f"[GAMIFICATION_EXAMPLE] Dados simulados criados: {len(self.simulated_users)} usuários, {len(self.simulated_events)} eventos")
    
    def _generate_event_data(self, event_type: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """Gera dados específicos para cada tipo de evento."""
        if event_type == "keyword_search":
            return {
                "query": random.choice(["seo", "marketing", "digital", "content", "analytics"]),
                "results_count": random.randint(10, 500),
                "search_time": random.randint(1, 30)
            }
        elif event_type == "execution_complete":
            return {
                "execution_type": random.choice(["keyword_analysis", "competitor_analysis", "trend_analysis"]),
                "execution_time": random.randint(30, 300),
                "keywords_processed": random.randint(10, 1000),
                "success_rate": random.uniform(0.8, 1.0)
            }
        elif event_type == "export_data":
            return {
                "export_format": random.choice(["csv", "json", "xlsx"]),
                "data_size": random.randint(100, 10000)
            }
        elif event_type == "login_streak":
            return {
                "streak_days": random.randint(1, 30)
            }
        elif event_type == "feature_usage":
            return {
                "feature": random.choice(["dashboard", "reports", "alerts", "api", "integrations"]),
                "usage_duration": random.randint(10, 600)
            }
        elif event_type == "referral":
            return {
                "referred_user": f"user_{random.randint(1000, 9999)}"
            }
        elif event_type == "social_share":
            return {
                "platform": random.choice(["twitter", "linkedin", "facebook", "instagram"])
            }
        else:
            return {"timestamp": datetime.now().isoformat()}
    
    def demonstrate_points_system(self):
        """Demonstra o sistema de pontos."""
        logger.info("[GAMIFICATION_EXAMPLE] Demonstrando sistema de pontos...")
        
        # Simular eventos para gerar pontos
        for event in self.simulated_events[:100]:  # Primeiros 100 eventos
            self.points_manager.handle_event(
                event["event_type"],
                event["user_id"],
                event["data"]
            )
        
        # Obter pontos de alguns usuários
        print("\n💰 SISTEMA DE PONTOS:")
        print("=" * 50)
        
        for index, user in enumerate(self.simulated_users[:5]):
            user_points = self.points_system.get_user_points(user["user_id"])
            if user_points:
                print(f"Usuário {user['user_id']}:")
                print(f"  Total: {user_points.total_points} pontos")
                print(f"  Nível: {user_points.level}")
                print(f"  Experiência: {user_points.experience_points} pontos")
                print(f"  Conquistas: {user_points.achievement_points} pontos")
                print()
        
        # Leaderboard de pontos
        leaderboard = self.points_system.get_leaderboard(limit=10)
        print("🏆 TOP 10 - RANKING DE PONTOS:")
        for index, entry in enumerate(leaderboard[:5], 1):
            print(f"  {index}. {entry['user_id']}: {entry['points']} pontos (Nível {entry['level']})")
        
        logger.info("[GAMIFICATION_EXAMPLE] Sistema de pontos demonstrado")
    
    def demonstrate_badges_system(self):
        """Demonstra o sistema de badges."""
        logger.info("[GAMIFICATION_EXAMPLE] Demonstrando sistema de badges...")
        
        print("\n🏅 SISTEMA DE BADGES:")
        print("=" * 50)
        
        # Listar badges disponíveis
        badges = self.badges_system.list_badges()
        print(f"Badges disponíveis: {len(badges)}")
        
        for badge in badges[:5]:  # Primeiras 5 badges
            print(f"  {badge.name} ({badge.rarity.value})")
            print(f"    {badge.description}")
            print(f"    Recompensa: {badge.points_reward} pontos")
            print()
        
        # Simular progresso para desbloquear badges
        for user in self.simulated_users[:10]:
            # Simular dados de progresso
            event_data = {
                "keyword_searches_count": random.randint(1, 200),
                "executions_completed_count": random.randint(1, 100),
                "exports_made_count": random.randint(1, 50),
                "login_streak_days": random.randint(1, 30),
                "features_used_count": random.randint(1, 10),
                "total_points": random.randint(100, 2000),
                "user_level": random.randint(1, 20)
            }
            
            # Verificar progresso
            unlocked_badges = self.badges_system.check_user_progress(user["user_id"], event_data)
            
            if unlocked_badges:
                for badge in unlocked_badges:
                    user_badge = self.badges_system.unlock_badge(user["user_id"], badge.badge_id)
                    if user_badge:
                        print(f"🎉 {user['user_id']} desbloqueou: {badge.name}!")
        
        # Progresso de badges de um usuário
        if self.simulated_users:
            progress = self.badges_system.get_user_badge_progress(self.simulated_users[0]["user_id"])
            print(f"\n📊 Progresso de Badges - {self.simulated_users[0]['user_id']}:")
            print(f"  Badges desbloqueadas: {progress['unlocked_badges']}/{progress['total_badges']}")
            print(f"  Por tipo: {dict(progress['badges_by_type'])}")
            print(f"  Por raridade: {dict(progress['badges_by_rarity'])}")
        
        logger.info("[GAMIFICATION_EXAMPLE] Sistema de badges demonstrado")
    
    def demonstrate_leaderboards_system(self):
        """Demonstra o sistema de leaderboards."""
        logger.info("[GAMIFICATION_EXAMPLE] Demonstrando sistema de leaderboards...")
        
        print("\n📊 SISTEMA DE LEADERBOARDS:")
        print("=" * 50)
        
        # Listar leaderboards disponíveis
        leaderboards = self.leaderboards_system.list_leaderboards()
        print(f"Leaderboards disponíveis: {len(leaderboards)}")
        
        for leaderboard in leaderboards[:3]:  # Primeiros 3 leaderboards
            print(f"  {leaderboard.name} ({leaderboard.period.value})")
            print(f"    {leaderboard.description}")
            print()
        
        # Simular dados para leaderboards
        user_data = {}
        for user in self.simulated_users[:20]:
            user_data[user["user_id"]] = {
                "total_points": random.randint(100, 5000),
                "user_level": random.randint(1, 50),
                "badges_count": random.randint(0, 20),
                "login_count": random.randint(10, 100),
                "executions_completed": random.randint(5, 200),
                "keyword_searches": random.randint(20, 1000),
                "exports_made": random.randint(1, 50),
                "login_streak_days": random.randint(1, 30)
            }
        
        # Atualizar scores nos leaderboards
        for leaderboard in leaderboards[:3]:
            updated_entries = self.leaderboards_system.update_scores_from_data(
                leaderboard.leaderboard_id, user_data
            )
            print(f"✅ {leaderboard.name}: {len(updated_entries)} entradas atualizadas")
        
        # Mostrar top 5 de cada leaderboard
        for leaderboard in leaderboards[:3]:
            top_entries = self.leaderboards_system.get_top_users(leaderboard.leaderboard_id, limit=5)
            print(f"\n🏆 {leaderboard.name} - TOP 5:")
            for index, entry in enumerate(top_entries, 1):
                print(f"  {index}. {entry.user_id}: {entry.score}")
        
        logger.info("[GAMIFICATION_EXAMPLE] Sistema de leaderboards demonstrado")
    
    def demonstrate_challenges_system(self):
        """Demonstra o sistema de desafios."""
        logger.info("[GAMIFICATION_EXAMPLE] Demonstrando sistema de desafios...")
        
        print("\n🎯 SISTEMA DE DESAFIOS:")
        print("=" * 50)
        
        # Listar desafios disponíveis
        challenges = self.challenges_system.list_challenges()
        print(f"Desafios disponíveis: {len(challenges)}")
        
        for challenge in challenges[:3]:  # Primeiros 3 desafios
            print(f"  {challenge.name} ({challenge.challenge_type.value})")
            print(f"    {challenge.description}")
            print(f"    Recompensa: {challenge.points_reward} pontos")
            print()
        
        # Simular início de desafios
        for user in self.simulated_users[:10]:
            for challenge in challenges[:2]:  # Primeiros 2 desafios
                user_challenge = self.challenges_system.start_challenge(user["user_id"], challenge.challenge_id)
                if user_challenge:
                    print(f"🚀 {user['user_id']} iniciou: {challenge.name}")
        
        # Simular progresso nos desafios
        for user in self.simulated_users[:5]:
            event_data = {
                "keyword_searches_count": random.randint(1, 50),
                "executions_completed_count": random.randint(1, 20),
                "exports_made_count": random.randint(1, 10),
                "total_points": random.randint(100, 1000),
                "user_level": random.randint(1, 10)
            }
            
            for challenge in challenges[:2]:
                updated_challenge = self.challenges_system.update_challenge_progress(
                    user["user_id"], challenge.challenge_id, event_data
                )
                if updated_challenge and updated_challenge.status == ChallengeStatus.COMPLETED:
                    print(f"🎉 {user['user_id']} completou: {challenge.name}!")
        
        # Progresso de desafios de um usuário
        if self.simulated_users:
            progress = self.challenges_system.get_user_challenge_progress(self.simulated_users[0]["user_id"])
            print(f"\n📈 Progresso de Desafios - {self.simulated_users[0]['user_id']}:")
            print(f"  Desafios ativos: {progress['active_challenges']}")
            print(f"  Desafios completados: {progress['completed_challenges']}")
            print(f"  Por tipo: {dict(progress['challenges_by_type'])}")
        
        logger.info("[GAMIFICATION_EXAMPLE] Sistema de desafios demonstrado")
    
    def demonstrate_rewards_system(self):
        """Demonstra o sistema de recompensas."""
        logger.info("[GAMIFICATION_EXAMPLE] Demonstrando sistema de recompensas...")
        
        print("\n🎁 SISTEMA DE RECOMPENSAS:")
        print("=" * 50)
        
        # Listar recompensas disponíveis
        rewards = self.rewards_system.list_rewards()
        print(f"Recompensas disponíveis: {len(rewards)}")
        
        for reward in rewards[:3]:  # Primeiras 3 recompensas
            print(f"  {reward.name} ({reward.reward_type.value})")
            print(f"    {reward.description}")
            print(f"    Valor: {reward.value}")
            print()
        
        # Simular reivindicação de recompensas
        for user in self.simulated_users[:10]:
            available_rewards = self.rewards_system.get_available_rewards(user["user_id"])
            
            for reward in available_rewards[:2]:  # Primeiras 2 recompensas disponíveis
                user_reward = self.rewards_system.claim_reward(user["user_id"], reward.reward_id)
                if user_reward:
                    print(f"🎁 {user['user_id']} reivindicou: {reward.name}")
        
        # Estatísticas de recompensas
        if rewards:
            stats = self.rewards_system.get_reward_stats(rewards[0].reward_id)
            print(f"\n📊 Estatísticas - {rewards[0].name}:")
            print(f"  Total de reivindicações: {stats['total_claims']}")
            print(f"  Reivindicações recentes: {stats['recent_claims']}")
            print(f"  Disponível: {stats['is_available']}")
        
        logger.info("[GAMIFICATION_EXAMPLE] Sistema de recompensas demonstrado")
    
    def demonstrate_progress_tracking(self):
        """Demonstra o sistema de progress tracking."""
        logger.info("[GAMIFICATION_EXAMPLE] Demonstrando progress tracking...")
        
        print("\n📈 PROGRESS TRACKING:")
        print("=" * 50)
        
        # Simular progresso para alguns usuários
        for user in self.simulated_users[:10]:
            # Registrar login
            self.progress_tracker.record_login(user["user_id"])
            
            # Atualizar progresso
            self.progress_tracker.update_progress(
                user["user_id"],
                ProgressType.POINTS,
                random.randint(50, 500)
            )
            
            self.progress_tracker.update_progress(
                user["user_id"],
                ProgressType.LEVEL,
                random.randint(1, 10)
            )
            
            self.progress_tracker.update_progress(
                user["user_id"],
                ProgressType.BADGES,
                random.randint(0, 5)
            )
        
        # Mostrar resumo de progresso
        print("📊 RESUMO DE PROGRESSO:")
        for user in self.simulated_users[:5]:
            summary = self.progress_tracker.get_progress_summary(user["user_id"])
            print(f"\n{user['user_id']}:")
            print(f"  Pontos: {summary['total_points']}")
            print(f"  Nível: {summary['current_level']}")
            print(f"  Badges: {summary['badges_count']}")
            print(f"  Streak de login: {summary['login_streak']} dias")
            print(f"  Execuções: {summary['total_executions']}")
            print(f"  Buscas: {summary['total_searches']}")
        
        # Criar e acompanhar metas
        for user in self.simulated_users[:3]:
            # Meta de pontos
            points_goal = {
                "goal_id": f"points_goal_{user['user_id']}",
                "name": "Meta de Pontos",
                "description": "Acumular 1000 pontos",
                "progress_type": ProgressType.POINTS,
                "target_value": 1000
            }
            
            self.progress_tracker.create_goal(user["user_id"], points_goal)
            
            # Atualizar progresso da meta
            self.progress_tracker.update_goal_progress(
                user["user_id"],
                points_goal["goal_id"],
                random.randint(100, 800)
            )
        
        # Mostrar metas de um usuário
        if self.simulated_users:
            goals = self.progress_tracker.get_user_goals(self.simulated_users[0]["user_id"])
            print(f"\n🎯 Metas de {self.simulated_users[0]['user_id']}:")
            for goal in goals:
                print(f"  {goal.name}: {goal.current_value}/{goal.target_value} ({goal.get_progress():.1%})")
        
        logger.info("[GAMIFICATION_EXAMPLE] Progress tracking demonstrado")
    
    def demonstrate_integration(self):
        """Demonstra a integração entre os sistemas."""
        logger.info("[GAMIFICATION_EXAMPLE] Demonstrando integração entre sistemas...")
        
        print("\n🔗 INTEGRAÇÃO ENTRE SISTEMAS:")
        print("=" * 50)
        
        # Simular um fluxo completo de gamificação
        user_id = self.simulated_users[0]["user_id"]
        
        print(f"👤 Usuário: {user_id}")
        
        # 1. Usuário faz login
        self.progress_tracker.record_login(user_id)
        print("✅ Login registrado")
        
        # 2. Usuário faz busca de keywords
        search_event = {
            "query": "seo marketing",
            "results_count": 150
        }
        
        points_transaction = self.points_manager.handle_event(
            "keyword_search", user_id, search_event
        )
        print(f"💰 Pontos ganhos: {points_transaction.points_amount}")
        
        # 3. Atualizar progress tracking
        self.progress_tracker.update_progress(
            user_id, ProgressType.POINTS, points_transaction.points_amount
        )
        
        # 4. Verificar badges
        unlocked_badges = self.badges_system.check_user_progress(user_id, {
            "keyword_searches_count": 1,
            "total_points": points_transaction.points_amount
        })
        
        if unlocked_badges:
            for badge in unlocked_badges:
                user_badge = self.badges_system.unlock_badge(user_id, badge.badge_id)
                print(f"🏅 Badge desbloqueada: {badge.name}")
        
        # 5. Atualizar leaderboards
        self.leaderboards_system.update_score(
            "total_points_all_time", user_id, points_transaction.points_amount
        )
        
        # 6. Verificar desafios
        user_challenges = self.challenges_system.get_user_challenges(user_id)
        for user_challenge in user_challenges:
            if user_challenge.status == ChallengeStatus.ACTIVE:
                updated_challenge = self.challenges_system.update_challenge_progress(
                    user_id, user_challenge.challenge_id, {
                        "keyword_searches_count": 1,
                        "total_points": points_transaction.points_amount
                    }
                )
                
                if updated_challenge and updated_challenge.status == ChallengeStatus.COMPLETED:
                    print(f"🎯 Desafio completado!")
        
        # 7. Verificar recompensas disponíveis
        available_rewards = self.rewards_system.get_available_rewards(user_id)
        if available_rewards:
            reward = available_rewards[0]
            user_reward = self.rewards_system.claim_reward(user_id, reward.reward_id)
            if user_reward:
                print(f"🎁 Recompensa reivindicada: {reward.name}")
        
        # 8. Resumo final
        summary = self.progress_tracker.get_progress_summary(user_id)
        print(f"\n📊 Resumo Final:")
        print(f"  Pontos totais: {summary['total_points']}")
        print(f"  Nível: {summary['current_level']}")
        print(f"  Badges: {summary['badges_count']}")
        print(f"  Streak de login: {summary['login_streak']} dias")
        
        logger.info("[GAMIFICATION_EXAMPLE] Integração demonstrada")
    
    def run_complete_demonstration(self):
        """Executa demonstração completa do sistema."""
        logger.info("[GAMIFICATION_EXAMPLE] Iniciando demonstração completa...")
        
        print("🎮 DEMONSTRAÇÃO COMPLETA - SISTEMA DE GAMIFICAÇÃO")
        print("=" * 80)
        
        try:
            # Setup de dados simulados
            self.setup_simulated_data()
            
            # Demonstrações
            self.demonstrate_points_system()
            self.demonstrate_badges_system()
            self.demonstrate_leaderboards_system()
            self.demonstrate_challenges_system()
            self.demonstrate_rewards_system()
            self.demonstrate_progress_tracking()
            self.demonstrate_integration()
            
            print("\n✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 80)
            print("🎮 Sistema de Gamificação implementado e funcionando")
            print("💰 Sistema de pontos com multiplicadores e níveis")
            print("🏅 Badges e conquistas com progresso em tempo real")
            print("📊 Leaderboards com rankings dinâmicos")
            print("🎯 Desafios e missões personalizáveis")
            print("🎁 Sistema de recompensas com claims")
            print("📈 Progress tracking com metas e estatísticas")
            print("🔗 Integração completa entre todos os sistemas")
            
        except Exception as e:
            logger.error(f"[GAMIFICATION_EXAMPLE] Erro na demonstração: {e}")
            print(f"\n❌ ERRO NA DEMONSTRAÇÃO: {e}")


def main():
    """Função principal para executar o exemplo."""
    print("🎮 EXEMPLO PRÁTICO - SISTEMA DE GAMIFICAÇÃO")
    print("=" * 60)
    
    example = GamificationExample()
    example.run_complete_demonstration()


if __name__ == "__main__":
    main() 