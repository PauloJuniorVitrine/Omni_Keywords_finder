from typing import Dict, List, Optional, Any
"""
Testes Unitários - Progress Tracking
===================================

Testes para o sistema de tracking de progresso dos usuários.

Autor: Paulo Júnior
Data: 2025-01-27
Tracing ID: TEST_PROGRESS_TRACKING_001
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'infrastructure'))

from gamification.progress_tracking import (
    ProgressTracker,
    Milestone,
    UserJourney,
    ProgressAnalytics,
    ProgressType,
    MilestoneStatus
)


class TestMilestone:
    """Testes para a classe Milestone"""
    
    def test_milestone_creation(self):
        """Testa criação de milestone"""
        milestone = Milestone(
            milestone_id="test_milestone",
            name="Test Milestone",
            description="Test description",
            progress_type=ProgressType.USER_JOURNEY,
            target_value=100.0
        )
        
        assert milestone.milestone_id == "test_milestone"
        assert milestone.name == "Test Milestone"
        assert milestone.description == "Test description"
        assert milestone.progress_type == ProgressType.USER_JOURNEY
        assert milestone.target_value == 100.0
        assert milestone.current_value == 0.0
        assert milestone.status == MilestoneStatus.LOCKED
    
    def test_milestone_to_dict(self):
        """Testa conversão para dicionário"""
        milestone = Milestone(
            milestone_id="test_milestone",
            name="Test Milestone",
            description="Test description",
            progress_type=ProgressType.MILESTONE,
            target_value=50.0,
            current_value=25.0,
            status=MilestoneStatus.IN_PROGRESS,
            rewards=[{"type": "points", "value": 100}],
            criteria=["Complete task"]
        )
        
        data = milestone.to_dict()
        
        assert data["milestone_id"] == "test_milestone"
        assert data["name"] == "Test Milestone"
        assert data["progress_type"] == "milestone"
        assert data["target_value"] == 50.0
        assert data["current_value"] == 25.0
        assert data["status"] == "in_progress"
        assert data["progress_percentage"] == 50.0
        assert len(data["rewards"]) == 1
        assert len(data["criteria"]) == 1
    
    def test_milestone_progress_percentage(self):
        """Testa cálculo de porcentagem de progresso"""
        milestone = Milestone(
            milestone_id="test",
            name="Test",
            description="Test",
            progress_type=ProgressType.MILESTONE,
            target_value=100.0,
            current_value=75.0
        )
        
        data = milestone.to_dict()
        assert data["progress_percentage"] == 75.0
    
    def test_milestone_zero_target(self):
        """Testa milestone com target zero"""
        milestone = Milestone(
            milestone_id="test",
            name="Test",
            description="Test",
            progress_type=ProgressType.MILESTONE,
            target_value=0.0,
            current_value=10.0
        )
        
        data = milestone.to_dict()
        assert data["progress_percentage"] == 0.0


class TestUserJourney:
    """Testes para a classe UserJourney"""
    
    def test_user_journey_creation(self):
        """Testa criação de user journey"""
        milestones = [
            Milestone(
                milestone_id="milestone1",
                name="Milestone 1",
                description="First milestone",
                progress_type=ProgressType.USER_JOURNEY,
                target_value=10.0
            ),
            Milestone(
                milestone_id="milestone2",
                name="Milestone 2",
                description="Second milestone",
                progress_type=ProgressType.USER_JOURNEY,
                target_value=20.0
            )
        ]
        
        journey = UserJourney(
            journey_id="test_journey",
            user_id="user123",
            journey_name="Test Journey",
            description="Test journey description",
            milestones=milestones
        )
        
        assert journey.journey_id == "test_journey"
        assert journey.user_id == "user123"
        assert journey.journey_name == "Test Journey"
        assert len(journey.milestones) == 2
        assert journey.total_stages == 2
        assert journey.current_stage == 0
    
    def test_user_journey_to_dict(self):
        """Testa conversão para dicionário"""
        journey = UserJourney(
            journey_id="test_journey",
            user_id="user123",
            journey_name="Test Journey",
            description="Test description",
            milestones=[],
            current_stage=1,
            total_stages=3
        )
        
        data = journey.to_dict()
        
        assert data["journey_id"] == "test_journey"
        assert data["user_id"] == "user123"
        assert data["journey_name"] == "Test Journey"
        assert data["current_stage"] == 1
        assert data["total_stages"] == 3
        assert data["progress_percentage"] == 33.33333333333333
    
    def test_user_journey_progress_percentage(self):
        """Testa cálculo de porcentagem de progresso da journey"""
        journey = UserJourney(
            journey_id="test",
            user_id="user123",
            journey_name="Test",
            description="Test",
            milestones=[],
            current_stage=2,
            total_stages=4
        )
        
        data = journey.to_dict()
        assert data["progress_percentage"] == 50.0


class TestProgressAnalytics:
    """Testes para a classe ProgressAnalytics"""
    
    def test_progress_analytics_creation(self):
        """Testa criação de analytics"""
        analytics = ProgressAnalytics(
            user_id="user123",
            total_milestones=10,
            completed_milestones=7,
            total_journeys=3,
            completed_journeys=2,
            average_completion_time=2.5,
            engagement_score=85.0,
            progress_trend="excellent",
            recommendations=["Keep it up!", "Try new features"]
        )
        
        assert analytics.user_id == "user123"
        assert analytics.total_milestones == 10
        assert analytics.completed_milestones == 7
        assert analytics.engagement_score == 85.0
        assert analytics.progress_trend == "excellent"
        assert len(analytics.recommendations) == 2
    
    def test_progress_analytics_to_dict(self):
        """Testa conversão para dicionário"""
        analytics = ProgressAnalytics(
            user_id="user123",
            total_milestones=8,
            completed_milestones=6,
            total_journeys=2,
            completed_journeys=1
        )
        
        data = analytics.to_dict()
        
        assert data["user_id"] == "user123"
        assert data["total_milestones"] == 8
        assert data["completed_milestones"] == 6
        assert data["completion_rate"] == 75.0
        assert data["progress_trend"] == "stable"
    
    def test_progress_analytics_completion_rate(self):
        """Testa cálculo de taxa de conclusão"""
        analytics = ProgressAnalytics(
            user_id="user123",
            total_milestones=0,
            completed_milestones=0
        )
        
        data = analytics.to_dict()
        assert data["completion_rate"] == 0.0


class TestProgressTracker:
    """Testes para a classe ProgressTracker"""
    
    @pytest.fixture
    def progress_tracker(self):
        """Fixture para criar progress tracker"""
        return ProgressTracker(
            redis_config=None,
            enable_observability=False,
            enable_notifications=False
        )
    
    def test_progress_tracker_initialization(self, progress_tracker):
        """Testa inicialização do progress tracker"""
        assert progress_tracker.user_journeys == {}
        assert progress_tracker.user_milestones == {}
        assert progress_tracker.progress_analytics == {}
        assert len(progress_tracker.default_milestones) == 5
    
    def test_create_user_journey(self, progress_tracker):
        """Testa criação de user journey"""
        journey_id = progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        assert journey_id is not None
        assert journey_id.startswith("journey_")
        
        # Verificar se foi adicionada
        user_journeys = progress_tracker.user_journeys.get("user123", [])
        assert len(user_journeys) == 1
        assert user_journeys[0].journey_id == journey_id
        assert user_journeys[0].journey_name == "Test Journey"
    
    def test_create_user_journey_with_custom_milestones(self, progress_tracker):
        """Testa criação de journey com milestones customizados"""
        custom_milestones = [
            Milestone(
                milestone_id="custom1",
                name="Custom 1",
                description="Custom milestone",
                progress_type=ProgressType.MILESTONE,
                target_value=50.0
            )
        ]
        
        journey_id = progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Custom Journey",
            description="Custom description",
            milestones=custom_milestones
        )
        
        user_journeys = progress_tracker.user_journeys.get("user123", [])
        journey = user_journeys[0]
        
        assert len(journey.milestones) == 1
        assert journey.milestones[0].milestone_id == "custom1"
        assert journey.total_stages == 1
    
    def test_update_progress_success(self, progress_tracker):
        """Testa atualização de progresso com sucesso"""
        # Criar journey primeiro
        journey_id = progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        # Atualizar progresso do primeiro milestone
        result = progress_tracker.update_progress(
            user_id="user123",
            milestone_id="first_login",
            progress_value=1.0
        )
        
        assert result is True
        
        # Verificar se milestone foi atualizado
        milestone = progress_tracker._find_milestone("user123", "first_login")
        assert milestone is not None
        assert milestone.current_value == 1.0
        assert milestone.status == MilestoneStatus.COMPLETED
    
    def test_update_progress_milestone_not_found(self, progress_tracker):
        """Testa atualização de progresso com milestone inexistente"""
        result = progress_tracker.update_progress(
            user_id="user123",
            milestone_id="nonexistent",
            progress_value=1.0
        )
        
        assert result is False
    
    def test_update_progress_partial_completion(self, progress_tracker):
        """Testa atualização parcial de progresso"""
        # Criar journey
        progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        # Atualizar progresso parcial
        result = progress_tracker.update_progress(
            user_id="user123",
            milestone_id="keyword_master",
            progress_value=500.0  # Metade do target (1000)
        )
        
        assert result is True
        
        # Verificar status
        milestone = progress_tracker._find_milestone("user123", "keyword_master")
        assert milestone.current_value == 500.0
        assert milestone.status == MilestoneStatus.IN_PROGRESS
    
    def test_get_user_progress(self, progress_tracker):
        """Testa obtenção de progresso do usuário"""
        # Criar journey
        progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        # Atualizar progresso
        progress_tracker.update_progress(
            user_id="user123",
            milestone_id="first_login",
            progress_value=1.0
        )
        
        # Obter progresso
        progress_data = progress_tracker.get_user_progress("user123")
        
        assert progress_data["user_id"] == "user123"
        assert len(progress_data["journeys"]) == 1
        assert len(progress_data["milestones"]) == 0  # Milestones estão dentro da journey
        assert progress_data["analytics"] is not None
    
    def test_get_user_progress_empty(self, progress_tracker):
        """Testa obtenção de progresso de usuário sem dados"""
        progress_data = progress_tracker.get_user_progress("nonexistent")
        
        assert progress_data["user_id"] == "nonexistent"
        assert len(progress_data["journeys"]) == 0
        assert len(progress_data["milestones"]) == 0
        assert progress_data["analytics"] is None
    
    def test_get_progress_analytics(self, progress_tracker):
        """Testa obtenção de analytics"""
        # Criar journey e atualizar progresso
        progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        progress_tracker.update_progress(
            user_id="user123",
            milestone_id="first_login",
            progress_value=1.0
        )
        
        analytics = progress_tracker.get_progress_analytics("user123")
        
        assert analytics is not None
        assert analytics.user_id == "user123"
        assert analytics.total_milestones > 0
        assert analytics.completed_milestones > 0
    
    def test_get_progress_analytics_nonexistent(self, progress_tracker):
        """Testa obtenção de analytics de usuário inexistente"""
        analytics = progress_tracker.get_progress_analytics("nonexistent")
        assert analytics is None
    
    def test_find_milestone(self, progress_tracker):
        """Testa busca de milestone"""
        # Criar journey
        progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        # Buscar milestone existente
        milestone = progress_tracker._find_milestone("user123", "first_login")
        assert milestone is not None
        assert milestone.milestone_id == "first_login"
        
        # Buscar milestone inexistente
        milestone = progress_tracker._find_milestone("user123", "nonexistent")
        assert milestone is None
    
    def test_generate_recommendations(self, progress_tracker):
        """Testa geração de recomendações"""
        # Testar diferentes níveis de engajamento
        recommendations = progress_tracker._generate_recommendations("user123", 20.0, 2, 10)
        assert len(recommendations) == 2
        assert "tutorial" in recommendations[0].lower()
        
        recommendations = progress_tracker._generate_recommendations("user123", 70.0, 7, 10)
        assert len(recommendations) == 2
        assert "recursos avançados" in recommendations[0].lower()
        
        recommendations = progress_tracker._generate_recommendations("user123", 90.0, 9, 10)
        assert len(recommendations) == 2
        assert "parabéns" in recommendations[0].lower()
    
    def test_export_progress_report(self, progress_tracker):
        """Testa exportação de relatório"""
        # Criar dados de progresso
        progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        # Exportar relatório JSON
        report = progress_tracker.export_progress_report("user123", "json")
        assert report is not None
        assert isinstance(report, str)
        
        # Verificar se é JSON válido
        data = json.loads(report)
        assert data["user_id"] == "user123"
    
    def test_export_progress_report_invalid_format(self, progress_tracker):
        """Testa exportação com formato inválido"""
        report = progress_tracker.export_progress_report("user123", "invalid")
        assert report == "Formato não suportado"
    
    def test_get_leaderboard_progress(self, progress_tracker):
        """Testa obtenção de leaderboard"""
        # Criar dados para múltiplos usuários
        for index in range(3):
            user_id = f"user{index}"
            progress_tracker.create_user_journey(
                user_id=user_id,
                journey_name=f"Journey {index}",
                description=f"Description {index}"
            )
            
            # Atualizar progresso
            progress_tracker.update_progress(
                user_id=user_id,
                milestone_id="first_login",
                progress_value=1.0
            )
        
        # Obter leaderboard
        leaderboard = progress_tracker.get_leaderboard_progress(limit=10)
        
        assert len(leaderboard) == 3
        assert all("user_id" in entry for entry in leaderboard)
        assert all("engagement_score" in entry for entry in leaderboard)
    
    def test_get_leaderboard_progress_with_limit(self, progress_tracker):
        """Testa leaderboard com limite"""
        # Criar dados
        for index in range(5):
            user_id = f"user{index}"
            progress_tracker.create_user_journey(
                user_id=user_id,
                journey_name=f"Journey {index}",
                description=f"Description {index}"
            )
        
        # Obter leaderboard com limite
        leaderboard = progress_tracker.get_leaderboard_progress(limit=3)
        assert len(leaderboard) == 3
    
    @patch('infrastructure.gamification.progress_tracking.redis')
    def test_redis_integration(self, mock_redis, progress_tracker):
        """Testa integração com Redis"""
        # Mock Redis client
        mock_redis_client = Mock()
        mock_redis.Redis.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True
        
        # Criar tracker com Redis
        tracker_with_redis = ProgressTracker(
            redis_config={"host": "localhost", "port": 6379},
            enable_observability=False
        )
        
        # Criar journey
        journey_id = tracker_with_redis.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        # Verificar se Redis foi chamado
        assert mock_redis_client.setex.called
    
    def test_notification_callbacks(self, progress_tracker):
        """Testa callbacks de notificação"""
        notifications = []
        
        def notification_callback(user_id, milestone):
            notifications.append({"user_id": user_id, "milestone": milestone})
        
        # Adicionar callback
        progress_tracker.add_notification_callback(notification_callback)
        
        # Criar journey e completar milestone
        progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Test Journey",
            description="Test description"
        )
        
        progress_tracker.update_progress(
            user_id="user123",
            milestone_id="first_login",
            progress_value=1.0
        )
        
        # Verificar se notificação foi chamada
        assert len(notifications) == 1
        assert notifications[0]["user_id"] == "user123"
        assert notifications[0]["milestone"].milestone_id == "first_login"
    
    def test_thread_safety(self, progress_tracker):
        """Testa thread safety"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                # Criar journey
                journey_id = progress_tracker.create_user_journey(
                    user_id=f"user{thread_id}",
                    journey_name=f"Journey {thread_id}",
                    description=f"Description {thread_id}"
                )
                
                # Atualizar progresso
                success = progress_tracker.update_progress(
                    user_id=f"user{thread_id}",
                    milestone_id="first_login",
                    progress_value=1.0
                )
                
                results.append({"thread_id": thread_id, "success": success})
            except Exception as e:
                errors.append({"thread_id": thread_id, "error": str(e)})
        
        # Criar múltiplas threads
        threads = []
        for index in range(10):
            thread = threading.Thread(target=worker, args=(index,))
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert len(results) == 10
        assert len(errors) == 0
        assert all(r["success"] for r in results)


class TestProgressTrackerIntegration:
    """Testes de integração do Progress Tracker"""
    
    @pytest.fixture
    def progress_tracker(self):
        """Fixture para progress tracker"""
        return ProgressTracker(
            redis_config=None,
            enable_observability=False,
            enable_notifications=True
        )
    
    def test_complete_user_journey_flow(self, progress_tracker):
        """Testa fluxo completo de user journey"""
        # 1. Criar journey
        journey_id = progress_tracker.create_user_journey(
            user_id="user123",
            journey_name="Complete Journey",
            description="Test complete journey flow"
        )
        
        # 2. Verificar journey criada
        user_journeys = progress_tracker.user_journeys.get("user123", [])
        assert len(user_journeys) == 1
        
        journey = user_journeys[0]
        assert journey.journey_id == journey_id
        assert len(journey.milestones) == 5  # Milestones padrão
        
        # 3. Atualizar progresso de múltiplos milestones
        milestones_to_update = ["first_login", "first_search", "first_export"]
        
        for milestone_id in milestones_to_update:
            success = progress_tracker.update_progress(
                user_id="user123",
                milestone_id=milestone_id,
                progress_value=1.0
            )
            assert success is True
        
        # 4. Verificar analytics atualizados
        analytics = progress_tracker.get_progress_analytics("user123")
        assert analytics is not None
        assert analytics.completed_milestones >= 3
        assert analytics.engagement_score > 0
        
        # 5. Verificar progresso completo
        progress_data = progress_tracker.get_user_progress("user123")
        assert progress_data["user_id"] == "user123"
        assert len(progress_data["journeys"]) == 1
        assert progress_data["analytics"] is not None
        
        # 6. Exportar relatório
        report = progress_tracker.export_progress_report("user123", "json")
        assert report is not None
        
        report_data = json.loads(report)
        assert report_data["user_id"] == "user123"
    
    def test_multiple_users_scenario(self, progress_tracker):
        """Testa cenário com múltiplos usuários"""
        users = ["user1", "user2", "user3"]
        
        # Criar journeys para todos os usuários
        for user_id in users:
            progress_tracker.create_user_journey(
                user_id=user_id,
                journey_name=f"Journey for {user_id}",
                description=f"Description for {user_id}"
            )
            
            # Atualizar progresso com valores diferentes
            progress_value = users.index(user_id) + 1
            progress_tracker.update_progress(
                user_id=user_id,
                milestone_id="first_login",
                progress_value=progress_value
            )
        
        # Verificar que todos os usuários têm dados
        for user_id in users:
            progress_data = progress_tracker.get_user_progress(user_id)
            assert progress_data["user_id"] == user_id
            assert len(progress_data["journeys"]) == 1
        
        # Verificar leaderboard
        leaderboard = progress_tracker.get_leaderboard_progress()
        assert len(leaderboard) == 3
        
        # Verificar ordenação (maior engagement primeiro)
        engagement_scores = [entry["engagement_score"] for entry in leaderboard]
        assert engagement_scores == sorted(engagement_scores, reverse=True)


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 