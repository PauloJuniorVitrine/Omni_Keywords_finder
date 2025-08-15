from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Pontos
=======================================

Testes abrangentes para o sistema de pontos e recompensas.

Autor: Paulo Júnior
Data: 2024-12-19
Tracing ID: GAMIFICATION_TEST_001
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from infrastructure.gamification.points_system import (
    PointsSystem, PointsManager, PointsTransaction, UserPoints,
    PointsType, PointsSource
)


class TestPointsSystem:
    """Testes para PointsSystem"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.points_system = PointsSystem()
    
    def test_initialization(self):
        """Testa inicialização do sistema de pontos"""
        assert self.points_system.users_points == {}
        assert self.points_system.transactions == []
        assert self.points_system.multipliers == {}
        assert len(self.points_system.level_thresholds) > 0
        assert self.points_system.default_points is not None
    
    def test_add_points_basic(self):
        """Testa adição básica de pontos"""
        transaction = self.points_system.add_points(
            user_id="user_123",
            points_type=PointsType.EXPERIENCE,
            source=PointsSource.KEYWORD_SEARCH,
            description="Teste de busca"
        )
        
        assert transaction is not None
        assert transaction.user_id == "user_123"
        assert transaction.points_type == PointsType.EXPERIENCE
        assert transaction.source == PointsSource.KEYWORD_SEARCH
        assert transaction.points_amount > 0
        
        # Verificar se usuário foi criado
        user_points = self.points_system.get_user_points("user_123")
        assert user_points is not None
        assert user_points.total_points > 0
        assert user_points.experience_points > 0
    
    def test_add_points_with_custom_amount(self):
        """Testa adição de pontos com quantidade customizada"""
        transaction = self.points_system.add_points(
            user_id="user_123",
            points_type=PointsType.ACHIEVEMENT,
            source=PointsSource.BADGE_EARNED,
            description="Badge conquistada",
            points_amount=150
        )
        
        assert transaction.points_amount == 150
        
        user_points = self.points_system.get_user_points("user_123")
        assert user_points.achievement_points == 150
        assert user_points.total_points == 150
    
    def test_add_points_with_multiplier(self):
        """Testa adição de pontos com multiplicador"""
        # Definir multiplicador
        self.points_system.set_multiplier("user_123", 2.0, 60)
        
        transaction = self.points_system.add_points(
            user_id="user_123",
            points_type=PointsType.EXPERIENCE,
            source=PointsSource.KEYWORD_SEARCH,
            description="Busca com multiplicador"
        )
        
        # Verificar se multiplicador foi aplicado
        assert transaction.multiplier == 2.0
        assert transaction.points_amount == 20  # 10 * 2.0
    
    def test_level_up(self):
        """Testa subida de nível"""
        # Adicionar pontos suficientes para subir de nível
        for index in range(10):
            self.points_system.add_points(
                user_id="user_123",
                points_type=PointsType.EXPERIENCE,
                source=PointsSource.KEYWORD_SEARCH,
                description=f"Busca {index+1}",
                points_amount=50
            )
        
        user_points = self.points_system.get_user_points("user_123")
        assert user_points.level > 1
    
    def test_get_user_transactions(self):
        """Testa obtenção de transações do usuário"""
        # Adicionar algumas transações
        for index in range(5):
            self.points_system.add_points(
                user_id="user_123",
                points_type=PointsType.EXPERIENCE,
                source=PointsSource.KEYWORD_SEARCH,
                description=f"Transação {index+1}"
            )
        
        transactions = self.points_system.get_user_transactions("user_123")
        assert len(transactions) == 5
        assert all(tx.user_id == "user_123" for tx in transactions)
    
    def test_get_leaderboard(self):
        """Testa obtenção de leaderboard"""
        # Adicionar pontos para múltiplos usuários
        users = ["user_1", "user_2", "user_3"]
        for index, user_id in enumerate(users):
            self.points_system.add_points(
                user_id=user_id,
                points_type=PointsType.EXPERIENCE,
                source=PointsSource.KEYWORD_SEARCH,
                description="Teste",
                points_amount=100 * (index + 1)
            )
        
        leaderboard = self.points_system.get_leaderboard()
        assert len(leaderboard) == 3
        
        # Verificar ordenação (maior pontuação primeiro)
        assert leaderboard[0]["points"] >= leaderboard[1]["points"]
        assert leaderboard[1]["points"] >= leaderboard[2]["points"]
    
    def test_multiplier_expiration(self):
        """Testa expiração de multiplicador"""
        # Definir multiplicador com duração curta
        self.points_system.set_multiplier("user_123", 2.0, 1)  # 1 minuto
        
        # Aguardar expiração
        import time
        time.sleep(1.1)
        
        # Verificar se multiplicador expirou
        multiplier = self.points_system.get_multiplier("user_123")
        assert multiplier == 1.0
    
    def test_reset_daily_points(self):
        """Testa reset de pontos diários"""
        # Adicionar pontos diários
        self.points_system.add_points(
            user_id="user_123",
            points_type=PointsType.DAILY,
            source=PointsSource.LOGIN_STREAK,
            description="Login streak"
        )
        
        user_points = self.points_system.get_user_points("user_123")
        assert user_points.daily_points > 0
        
        # Resetar pontos diários
        self.points_system.reset_daily_points()
        
        user_points = self.points_system.get_user_points("user_123")
        assert user_points.daily_points == 0
    
    def test_export_user_data(self):
        """Testa exportação de dados do usuário"""
        # Adicionar alguns pontos
        self.points_system.add_points(
            user_id="user_123",
            points_type=PointsType.EXPERIENCE,
            source=PointsSource.KEYWORD_SEARCH,
            description="Teste"
        )
        
        # Exportar dados
        data = self.points_system.export_user_data("user_123", "json")
        
        assert isinstance(data, dict)
        assert "user_points" in data
        assert "transactions" in data
        assert "exported_at" in data


class TestPointsManager:
    """Testes para PointsManager"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.points_system = PointsSystem()
        self.points_manager = PointsManager(self.points_system)
    
    def test_handle_keyword_search_event(self):
        """Testa handler de evento de busca de keywords"""
        event_data = {"query": "test", "results_count": 50}
        
        transaction = self.points_manager.handle_event(
            "keyword_search", "user_123", event_data
        )
        
        assert transaction is not None
        assert transaction.source == PointsSource.KEYWORD_SEARCH
        assert transaction.points_amount > 0
    
    def test_handle_execution_complete_event(self):
        """Testa handler de evento de execução completa"""
        event_data = {"execution_type": "keyword_analysis", "execution_time": 120}
        
        transaction = self.points_manager.handle_event(
            "execution_complete", "user_123", event_data
        )
        
        assert transaction is not None
        assert transaction.source == PointsSource.EXECUTION_COMPLETE
        assert transaction.points_amount > 0
    
    def test_handle_export_data_event(self):
        """Testa handler de evento de exportação"""
        event_data = {"export_format": "csv", "data_size": 1000}
        
        transaction = self.points_manager.handle_event(
            "export_data", "user_123", event_data
        )
        
        assert transaction is not None
        assert transaction.source == PointsSource.EXPORT_DATA
        assert transaction.points_amount > 0
    
    def test_handle_login_streak_event(self):
        """Testa handler de evento de streak de login"""
        event_data = {"streak_days": 7}
        
        transaction = self.points_manager.handle_event(
            "login_streak", "user_123", event_data
        )
        
        assert transaction is not None
        assert transaction.source == PointsSource.LOGIN_STREAK
        assert transaction.points_amount > 0
        assert transaction.multiplier > 1.0  # Deve ter bônus de streak
    
    def test_handle_unknown_event(self):
        """Testa handler de evento desconhecido"""
        transaction = self.points_manager.handle_event(
            "unknown_event", "user_123", {}
        )
        
        assert transaction is None


class TestPointsTransaction:
    """Testes para PointsTransaction"""
    
    def test_transaction_creation(self):
        """Testa criação de transação"""
        transaction = PointsTransaction(
            transaction_id="tx_123",
            user_id="user_123",
            points_type=PointsType.EXPERIENCE,
            points_amount=100,
            source=PointsSource.KEYWORD_SEARCH,
            description="Teste",
            timestamp=datetime.utcnow()
        )
        
        assert transaction.transaction_id == "tx_123"
        assert transaction.user_id == "user_123"
        assert transaction.points_amount == 100
    
    def test_transaction_to_dict(self):
        """Testa conversão de transação para dicionário"""
        transaction = PointsTransaction(
            transaction_id="tx_123",
            user_id="user_123",
            points_type=PointsType.EXPERIENCE,
            points_amount=100,
            source=PointsSource.KEYWORD_SEARCH,
            description="Teste",
            timestamp=datetime.utcnow()
        )
        
        data = transaction.to_dict()
        
        assert isinstance(data, dict)
        assert data["transaction_id"] == "tx_123"
        assert data["user_id"] == "user_123"
        assert data["points_amount"] == 100


class TestUserPoints:
    """Testes para UserPoints"""
    
    def test_user_points_creation(self):
        """Testa criação de pontos de usuário"""
        user_points = UserPoints(user_id="user_123")
        
        assert user_points.user_id == "user_123"
        assert user_points.total_points == 0
        assert user_points.level == 1
    
    def test_user_points_to_dict(self):
        """Testa conversão de pontos de usuário para dicionário"""
        user_points = UserPoints(
            user_id="user_123",
            total_points=500,
            level=5
        )
        
        data = user_points.to_dict()
        
        assert isinstance(data, dict)
        assert data["user_id"] == "user_123"
        assert data["total_points"] == 500
        assert data["level"] == 5


class TestErrorHandling:
    """Testes para tratamento de erros"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.points_system = PointsSystem()
    
    def test_add_points_invalid_user_id(self):
        """Testa adição de pontos com user_id inválido"""
        with pytest.raises(Exception):
            self.points_system.add_points(
                user_id="",
                points_type=PointsType.EXPERIENCE,
                source=PointsSource.KEYWORD_SEARCH,
                description="Teste"
            )
    
    def test_get_user_points_nonexistent(self):
        """Testa obtenção de pontos de usuário inexistente"""
        user_points = self.points_system.get_user_points("nonexistent_user")
        assert user_points is None
    
    def test_get_user_transactions_nonexistent(self):
        """Testa obtenção de transações de usuário inexistente"""
        transactions = self.points_system.get_user_transactions("nonexistent_user")
        assert len(transactions) == 0


class TestPerformance:
    """Testes de performance"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.points_system = PointsSystem()
    
    def test_bulk_points_addition(self):
        """Testa adição em massa de pontos"""
        import time
        
        start_time = time.time()
        
        # Adicionar 1000 pontos
        for index in range(1000):
            self.points_system.add_points(
                user_id=f"user_{index % 10}",  # 10 usuários diferentes
                points_type=PointsType.EXPERIENCE,
                source=PointsSource.KEYWORD_SEARCH,
                description=f"Bulk test {index}"
            )
        
        end_time = time.time()
        
        # Deve ser rápido (menos de 1 segundo)
        assert end_time - start_time < 1.0
        
        # Verificar se todos os usuários foram criados
        for index in range(10):
            user_points = self.points_system.get_user_points(f"user_{index}")
            assert user_points is not None
            assert user_points.total_points > 0


class TestGlobalInstances:
    """Testes para instâncias globais"""
    
    def test_get_points_system(self):
        """Testa obtenção de instância global do sistema de pontos"""
        from infrastructure.gamification.points_system import get_points_system
        
        points_system = get_points_system()
        assert points_system is not None
        assert isinstance(points_system, PointsSystem)
    
    def test_get_points_manager(self):
        """Testa obtenção de instância global do gerenciador de pontos"""
        from infrastructure.gamification.points_system import get_points_manager
        
        points_manager = get_points_manager()
        assert points_manager is not None
        assert isinstance(points_manager, PointsManager) 