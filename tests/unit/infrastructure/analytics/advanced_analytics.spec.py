from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Analytics Avançado

Testes abrangentes para todas as funcionalidades do sistema de analytics avançado,
incluindo métricas de performance, eficiência de clusters, comportamento do usuário
e insights preditivos.

Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 15
Ruleset: enterprise_control_layer.yaml
Data: 2024-12-19
"""

import pytest
import tempfile
import os
import json
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd

# Importar sistema de analytics
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.analytics.advanced_analytics_system import (
    AdvancedAnalyticsSystem,
    KeywordPerformance,
    ClusterEfficiency,
    UserBehavior,
    PredictiveInsight,
    AnalyticsData,
    InsightType,
    TrendDirection,
    create_analytics_system
)

class TestAdvancedAnalyticsSystem:
    """Testes para o sistema de analytics avançado"""
    
    @pytest.fixture
    def temp_db(self):
        """Fixture para banco de dados temporário"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Limpar após os testes
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def analytics_system(self, temp_db):
        """Fixture para sistema de analytics com banco temporário"""
        with patch('infrastructure.analytics.advanced_analytics_system.ANALYTICS_DB_PATH', temp_db):
            system = AdvancedAnalyticsSystem()
            yield system
    
    @pytest.fixture
    def sample_keywords(self):
        """Dados de exemplo para keywords"""
        return [
            KeywordPerformance(
                id="test_1",
                termo="teste keyword 1",
                volume_busca=1000,
                cpc=2.5,
                concorrencia=50,
                score_qualidade=8.5,
                tempo_processamento=1500,
                status="success",
                categoria="ecommerce",
                nicho="nicho_1",
                data_processamento=(datetime.now() - timedelta(days=1)).isoformat(),
                roi_estimado=150.0,
                conversao_estimada=5.2
            ),
            KeywordPerformance(
                id="test_2",
                termo="teste keyword 2",
                volume_busca=2000,
                cpc=1.8,
                concorrencia=30,
                score_qualidade=7.8,
                tempo_processamento=1200,
                status="success",
                categoria="saas",
                nicho="nicho_2",
                data_processamento=(datetime.now() - timedelta(days=2)).isoformat(),
                roi_estimado=200.0,
                conversao_estimada=8.1
            )
        ]
    
    @pytest.fixture
    def sample_clusters(self):
        """Dados de exemplo para clusters"""
        return [
            ClusterEfficiency(
                id="cluster_1",
                nome="Cluster Teste 1",
                keywords_count=15,
                score_medio=8.2,
                diversidade_semantica=0.75,
                coesao_interna=0.85,
                tempo_geracao=12.5,
                qualidade_geral=8.5,
                categoria="ecommerce",
                nicho="nicho_1",
                data_criacao=(datetime.now() - timedelta(days=1)).isoformat(),
                keywords=[]
            ),
            ClusterEfficiency(
                id="cluster_2",
                nome="Cluster Teste 2",
                keywords_count=25,
                score_medio=7.9,
                diversidade_semantica=0.68,
                coesao_interna=0.78,
                tempo_geracao=18.2,
                qualidade_geral=7.8,
                categoria="saas",
                nicho="nicho_2",
                data_criacao=(datetime.now() - timedelta(days=2)).isoformat(),
                keywords=[]
            )
        ]
    
    @pytest.fixture
    def sample_behavior(self):
        """Dados de exemplo para comportamento do usuário"""
        return [
            UserBehavior(
                user_id="user_1",
                session_id="session_1",
                timestamp=(datetime.now() - timedelta(hours=1)).isoformat(),
                action_type="search",
                action_details={},
                duration=300,
                success=True,
                device_type="desktop",
                browser="chrome",
                location="BR"
            ),
            UserBehavior(
                user_id="user_2",
                session_id="session_2",
                timestamp=(datetime.now() - timedelta(hours=2)).isoformat(),
                action_type="export",
                action_details={},
                duration=180,
                success=True,
                device_type="mobile",
                browser="safari",
                location="US"
            )
        ]
    
    def test_init_database(self, temp_db):
        """Testa inicialização do banco de dados"""
        with patch('infrastructure.analytics.advanced_analytics_system.ANALYTICS_DB_PATH', temp_db):
            system = AdvancedAnalyticsSystem()
            
            # Verificar se as tabelas foram criadas
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'keywords_performance',
                'clusters_efficiency', 
                'user_behavior',
                'predictive_insights',
                'dashboard_customization'
            ]
            
            for table in expected_tables:
                assert table in tables
            
            conn.close()
    
    def test_generate_sample_data(self, analytics_system):
        """Testa geração de dados de exemplo"""
        # Verificar se dados foram gerados
        keywords = analytics_system.get_keywords_performance()
        clusters = analytics_system.get_clusters_efficiency()
        behavior = analytics_system.get_user_behavior()
        
        assert len(keywords) > 0
        assert len(clusters) > 0
        assert len(behavior) > 0
    
    def test_get_keywords_performance(self, analytics_system, sample_keywords):
        """Testa obtenção de performance de keywords"""
        # Inserir dados de teste
        conn = sqlite3.connect(analytics_system.db_path)
        cursor = conn.cursor()
        
        for keyword in sample_keywords:
            cursor.execute('''
                INSERT INTO keywords_performance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                keyword.id, keyword.termo, keyword.volume_busca, keyword.cpc,
                keyword.concorrencia, keyword.score_qualidade, keyword.tempo_processamento,
                keyword.status, keyword.categoria, keyword.nicho, keyword.data_processamento,
                keyword.roi_estimado, keyword.conversao_estimada
            ))
        
        conn.commit()
        conn.close()
        
        # Testar busca sem filtros
        keywords = analytics_system.get_keywords_performance()
        assert len(keywords) >= 2
        
        # Testar busca com filtro de categoria
        keywords = analytics_system.get_keywords_performance(category='ecommerce')
        assert all(key.categoria == 'ecommerce' for key in keywords)
        
        # Testar busca com limite
        keywords = analytics_system.get_keywords_performance(limit=1)
        assert len(keywords) <= 1
    
    def test_get_clusters_efficiency(self, analytics_system, sample_clusters):
        """Testa obtenção de eficiência de clusters"""
        # Inserir dados de teste
        conn = sqlite3.connect(analytics_system.db_path)
        cursor = conn.cursor()
        
        for cluster in sample_clusters:
            cursor.execute('''
                INSERT INTO clusters_efficiency VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cluster.id, cluster.nome, cluster.keywords_count, cluster.score_medio,
                cluster.diversidade_semantica, cluster.coesao_interna, cluster.tempo_geracao,
                cluster.qualidade_geral, cluster.categoria, cluster.nicho, cluster.data_criacao
            ))
        
        conn.commit()
        conn.close()
        
        # Testar busca sem filtros
        clusters = analytics_system.get_clusters_efficiency()
        assert len(clusters) >= 2
        
        # Testar busca com filtro de categoria
        clusters = analytics_system.get_clusters_efficiency(category='ecommerce')
        assert all(c.categoria == 'ecommerce' for c in clusters)
        
        # Testar busca com limite
        clusters = analytics_system.get_clusters_efficiency(limit=1)
        assert len(clusters) <= 1
    
    def test_get_user_behavior(self, analytics_system, sample_behavior):
        """Testa obtenção de comportamento do usuário"""
        # Inserir dados de teste
        conn = sqlite3.connect(analytics_system.db_path)
        cursor = conn.cursor()
        
        for behavior in sample_behavior:
            cursor.execute('''
                INSERT INTO user_behavior VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()), behavior.user_id, behavior.session_id, behavior.timestamp,
                behavior.action_type, json.dumps(behavior.action_details), behavior.duration,
                behavior.success, behavior.device_type, behavior.browser, behavior.location
            ))
        
        conn.commit()
        conn.close()
        
        # Testar busca sem filtros
        behavior_data = analytics_system.get_user_behavior()
        assert len(behavior_data) >= 2
        
        # Testar busca com filtro de usuário
        behavior_data = analytics_system.get_user_behavior(user_id='user_1')
        assert all(b.user_id == 'user_1' for b in behavior_data)
        
        # Testar busca com filtro de ação
        behavior_data = analytics_system.get_user_behavior(action_type='search')
        assert all(b.action_type == 'search' for b in behavior_data)
    
    def test_calculate_summary_metrics(self, analytics_system, sample_keywords, sample_clusters, sample_behavior):
        """Testa cálculo de métricas resumidas"""
        summary = analytics_system.calculate_summary_metrics(sample_keywords, sample_clusters, sample_behavior)
        
        assert 'total_keywords' in summary
        assert 'total_clusters' in summary
        assert 'avg_processing_time' in summary
        assert 'success_rate' in summary
        assert 'avg_roi' in summary
        assert 'user_engagement_score' in summary
        assert 'cluster_quality_score' in summary
        
        assert summary['total_keywords'] == 2
        assert summary['total_clusters'] == 2
        assert summary['success_rate'] == 100.0  # Todos os keywords têm status 'success'
        assert summary['user_engagement_score'] == 100.0  # Todas as ações têm success=True
    
    def test_get_analytics_data(self, analytics_system):
        """Testa obtenção de dados completos de analytics"""
        data = analytics_system.get_analytics_data('7d')
        
        assert data is not None
        assert hasattr(data, 'keywords_performance')
        assert hasattr(data, 'clusters_efficiency')
        assert hasattr(data, 'user_behavior')
        assert hasattr(data, 'predictive_insights')
        assert hasattr(data, 'summary_metrics')
        
        # Verificar se to_dict() funciona
        data_dict = data.to_dict()
        assert isinstance(data_dict, dict)
        assert 'keywords_performance' in data_dict
        assert 'summary_metrics' in data_dict
    
    def test_generate_predictive_insights(self, analytics_system):
        """Testa geração de insights preditivos"""
        insights = analytics_system.generate_predictive_insights(['keyword_trend'])
        
        assert isinstance(insights, list)
        
        if len(insights) > 0:
            insight = insights[0]
            assert isinstance(insight, PredictiveInsight)
            assert insight.type == InsightType.KEYWORD_TREND
            assert 0 <= insight.confidence <= 1
            assert insight.trend in [TrendDirection.UP, TrendDirection.DOWN, TrendDirection.STABLE]
    
    def test_generate_keyword_trend_insight(self, analytics_system):
        """Testa geração específica de insight de tendência de keywords"""
        insight = analytics_system._generate_keyword_trend_insight()
        
        if insight is not None:
            assert insight.type == InsightType.KEYWORD_TREND
            assert insight.title == "Tendência de Volume e ROI de Keywords"
            assert len(insight.factors) > 0
            assert len(insight.recommendations) > 0
            assert insight.created_at is not None
    
    def test_generate_cluster_performance_insight(self, analytics_system):
        """Testa geração específica de insight de performance de clusters"""
        insight = analytics_system._generate_cluster_performance_insight()
        
        if insight is not None:
            assert insight.type == InsightType.CLUSTER_PERFORMANCE
            assert insight.title == "Performance dos Clusters Semânticos"
            assert len(insight.factors) > 0
            assert len(insight.recommendations) > 0
    
    def test_generate_user_engagement_insight(self, analytics_system):
        """Testa geração específica de insight de engajamento do usuário"""
        insight = analytics_system._generate_user_engagement_insight()
        
        if insight is not None:
            assert insight.type == InsightType.USER_ENGAGEMENT
            assert insight.title == "Engajamento dos Usuários"
            assert len(insight.factors) > 0
            assert len(insight.recommendations) > 0
    
    def test_generate_revenue_forecast_insight(self, analytics_system):
        """Testa geração específica de insight de previsão de receita"""
        insight = analytics_system._generate_revenue_forecast_insight()
        
        if insight is not None:
            assert insight.type == InsightType.REVENUE_FORECAST
            assert insight.title == "Previsão de Receita"
            assert len(insight.factors) > 0
            assert len(insight.recommendations) > 0
    
    def test_save_and_get_insight(self, analytics_system):
        """Testa salvamento e recuperação de insights"""
        insight = PredictiveInsight(
            id="test_insight",
            type=InsightType.KEYWORD_TREND,
            title="Test Insight",
            description="Test description",
            confidence=0.8,
            predicted_value=100.0,
            current_value=90.0,
            trend=TrendDirection.UP,
            timeframe="30 dias",
            factors=["factor1", "factor2"],
            recommendations=["rec1", "rec2"],
            created_at=datetime.now().isoformat()
        )
        
        # Salvar insight
        analytics_system._save_insight(insight)
        
        # Recuperar insights
        insights = analytics_system.get_predictive_insights()
        
        # Verificar se o insight foi salvo
        saved_insight = next((index for index in insights if index.id == "test_insight"), None)
        assert saved_insight is not None
        assert saved_insight.title == "Test Insight"
        assert saved_insight.confidence == 0.8
    
    def test_export_analytics_data_csv(self, analytics_system):
        """Testa exportação para CSV"""
        data = analytics_system.get_analytics_data('7d')
        csv_data = analytics_system._export_to_csv(data, ['performance', 'efficiency'])
        
        assert csv_data is not None
        assert 'Keywords Performance' in csv_data
        assert 'Clusters Efficiency' in csv_data
        assert 'ID,Termo,Volume,CPC,ROI,Status,Categoria' in csv_data
    
    def test_export_analytics_data_json(self, analytics_system):
        """Testa exportação para JSON"""
        data = analytics_system.get_analytics_data('7d')
        json_data = analytics_system._export_to_json(data, ['performance'])
        
        assert json_data is not None
        parsed_data = json.loads(json_data)
        assert 'keywords_performance' in parsed_data
        assert 'summary_metrics' in parsed_data
        assert 'export_timestamp' in parsed_data
    
    def test_export_analytics_data_excel(self, analytics_system):
        """Testa exportação para Excel"""
        data = analytics_system.get_analytics_data('7d')
        excel_data = analytics_system._export_to_excel(data, ['performance'])
        
        assert excel_data is not None
        assert len(excel_data) > 0  # Verificar se não está vazio
    
    def test_save_and_get_dashboard_customization(self, analytics_system):
        """Testa salvamento e recuperação de personalização do dashboard"""
        user_id = "test_user"
        widgets = ["widget1", "widget2"]
        settings = {"setting1": "value1"}
        
        # Salvar personalização
        success = analytics_system.save_dashboard_customization(user_id, widgets, settings)
        assert success is True
        
        # Recuperar personalização
        customization = analytics_system.get_dashboard_customization(user_id)
        assert customization['widgets'] == widgets
        assert customization['settings'] == settings
    
    def test_get_dashboard_customization_default(self, analytics_system):
        """Testa recuperação de personalização padrão para usuário inexistente"""
        customization = analytics_system.get_dashboard_customization("nonexistent_user")
        
        assert 'widgets' in customization
        assert 'settings' in customization
        assert 'keywords_performance' in customization['widgets']
    
    def test_get_realtime_metrics(self, analytics_system):
        """Testa obtenção de métricas em tempo real"""
        metrics = analytics_system.get_realtime_metrics()
        
        assert isinstance(metrics, dict)
        assert 'active_users' in metrics
        assert 'keywords_processed' in metrics
        assert 'clusters_generated' in metrics
        assert 'success_rate' in metrics
        assert 'avg_response_time' in metrics
        assert 'timestamp' in metrics
    
    def test_validate_time_range(self, analytics_system):
        """Testa validação de range de tempo"""
        from infrastructure.analytics.advanced_analytics_system import validate_time_range
        
        assert validate_time_range('1d') is True
        assert validate_time_range('7d') is True
        assert validate_time_range('30d') is True
        assert validate_time_range('90d') is True
        assert validate_time_range('invalid') is False
        assert validate_time_range('5d') is False
    
    def test_validate_export_format(self, analytics_system):
        """Testa validação de formato de exportação"""
        from infrastructure.analytics.advanced_analytics_system import validate_export_format
        
        assert validate_export_format('csv') is True
        assert validate_export_format('json') is True
        assert validate_export_format('excel') is True
        assert validate_export_format('pdf') is True
        assert validate_export_format('invalid') is False
    
    def test_create_analytics_system(self):
        """Testa factory function"""
        system = create_analytics_system()
        assert isinstance(system, AdvancedAnalyticsSystem)
    
    def test_keyword_performance_to_dict(self, sample_keywords):
        """Testa conversão de KeywordPerformance para dict"""
        keyword = sample_keywords[0]
        keyword_dict = keyword.to_dict()
        
        assert isinstance(keyword_dict, dict)
        assert keyword_dict['id'] == keyword.id
        assert keyword_dict['termo'] == keyword.termo
        assert keyword_dict['volume_busca'] == keyword.volume_busca
        assert keyword_dict['roi_estimado'] == keyword.roi_estimado
    
    def test_cluster_efficiency_to_dict(self, sample_clusters):
        """Testa conversão de ClusterEfficiency para dict"""
        cluster = sample_clusters[0]
        cluster_dict = cluster.to_dict()
        
        assert isinstance(cluster_dict, dict)
        assert cluster_dict['id'] == cluster.id
        assert cluster_dict['nome'] == cluster.nome
        assert cluster_dict['qualidade_geral'] == cluster.qualidade_geral
        assert isinstance(cluster_dict['keywords'], list)
    
    def test_user_behavior_to_dict(self, sample_behavior):
        """Testa conversão de UserBehavior para dict"""
        behavior = sample_behavior[0]
        behavior_dict = behavior.to_dict()
        
        assert isinstance(behavior_dict, dict)
        assert behavior_dict['user_id'] == behavior.user_id
        assert behavior_dict['action_type'] == behavior.action_type
        assert behavior_dict['success'] == behavior.success
    
    def test_predictive_insight_to_dict(self):
        """Testa conversão de PredictiveInsight para dict"""
        insight = PredictiveInsight(
            id="test",
            type=InsightType.KEYWORD_TREND,
            title="Test",
            description="Test",
            confidence=0.8,
            predicted_value=100.0,
            current_value=90.0,
            trend=TrendDirection.UP,
            timeframe="30 dias",
            factors=["factor1"],
            recommendations=["rec1"],
            created_at=datetime.now().isoformat()
        )
        
        insight_dict = insight.to_dict()
        
        assert isinstance(insight_dict, dict)
        assert insight_dict['id'] == insight.id
        assert insight_dict['type'] == insight.type.value
        assert insight_dict['trend'] == insight.trend.value
        assert insight_dict['confidence'] == insight.confidence
    
    def test_error_handling_database_connection(self, temp_db):
        """Testa tratamento de erro na conexão com banco"""
        # Simular erro de permissão
        with patch('sqlite3.connect', side_effect=sqlite3.OperationalError("database is locked")):
            with pytest.raises(sqlite3.OperationalError):
                with patch('infrastructure.analytics.advanced_analytics_system.ANALYTICS_DB_PATH', temp_db):
                    system = AdvancedAnalyticsSystem()
    
    def test_error_handling_empty_data(self, analytics_system):
        """Testa tratamento de dados vazios"""
        # Testar com dados vazios
        summary = analytics_system.calculate_summary_metrics([], [], [])
        
        assert summary['total_keywords'] == 0
        assert summary['total_clusters'] == 0
        assert summary['success_rate'] == 0
        assert summary['avg_roi'] == 0
    
    def test_error_handling_export_invalid_format(self, analytics_system):
        """Testa tratamento de formato de exportação inválido"""
        data = analytics_system.get_analytics_data('7d')
        
        with pytest.raises(ValueError):
            analytics_system._export_to_csv(data, ['invalid_metric'])
    
    @patch('numpy.mean')
    def test_error_handling_numpy_operations(self, mock_mean, analytics_system):
        """Testa tratamento de erros em operações numpy"""
        mock_mean.side_effect = Exception("numpy error")
        
        # Deve retornar valores padrão em caso de erro
        summary = analytics_system.calculate_summary_metrics([], [], [])
        assert summary['avg_processing_time'] == 0
        assert summary['avg_roi'] == 0

if __name__ == '__main__':
    pytest.main([__file__]) 