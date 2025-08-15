#!/usr/bin/env python3
"""
Testes Unitários - TikTok Trends Analyzer
========================================

Tracing ID: TEST_TIKTOK_TRENDS_ANALYZER_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Testes para: infrastructure/coleta/tiktok_trends_analyzer.py
Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 6.1
Ruleset: enterprise_control_layer.yaml
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import hashlib

from infrastructure.coleta.tiktok_trends_analyzer import (
    TikTokTrendsAnalyzer, TrendType, EngagementLevel, TrendAnalysis, ViralMetrics
)


class TestTikTokTrendsAnalyzer:
    @pytest.fixture
    def config(self):
        return {
            "rate_limits": {
                "requests_per_minute": 50,
                "requests_per_hour": 500
            },
            "viral_threshold": 0.8,
            "growth_threshold": 0.3,
            "engagement_thresholds": {
                "very_high": 0.15,
                "high": 0.10,
                "medium": 0.05,
                "low": 0.02
            },
            "cache_ttl": 3600
        }

    @pytest.fixture
    def analyzer(self, config):
        return TikTokTrendsAnalyzer(config)

    @pytest.fixture
    def sample_historical_data(self):
        return [
            {
                "timestamp": "2025-01-27T10:00:00Z",
                "views": 1000,
                "likes": 100,
                "comments": 50,
                "shares": 25,
                "engagement_rate": 0.175
            },
            {
                "timestamp": "2025-01-27T11:00:00Z",
                "views": 2000,
                "likes": 250,
                "comments": 120,
                "shares": 60,
                "engagement_rate": 0.215
            },
            {
                "timestamp": "2025-01-27T12:00:00Z",
                "views": 5000,
                "likes": 750,
                "comments": 400,
                "shares": 200,
                "engagement_rate": 0.270
            }
        ]

    @pytest.fixture
    def sample_video_data(self):
        return {
            "id": "video123",
            "views": 10000,
            "likes": 1500,
            "comments": 800,
            "shares": 400,
            "duration": 30,
            "watch_time": 250000,
            "created_time": "2025-01-27T10:00:00Z"
        }

    def test_trend_type_enum(self):
        """Testa enum TrendType."""
        assert TrendType.VIRAL.value == "viral"
        assert TrendType.GROWING.value == "growing"
        assert TrendType.STABLE.value == "stable"
        assert TrendType.DECLINING.value == "declining"
        assert TrendType.EMERGING.value == "emerging"

    def test_engagement_level_enum(self):
        """Testa enum EngagementLevel."""
        assert EngagementLevel.VERY_HIGH.value == "very_high"
        assert EngagementLevel.HIGH.value == "high"
        assert EngagementLevel.MEDIUM.value == "medium"
        assert EngagementLevel.LOW.value == "low"
        assert EngagementLevel.VERY_LOW.value == "very_low"

    def test_trend_analysis_dataclass(self):
        """Testa criação de objeto TrendAnalysis."""
        analysis = TrendAnalysis(
            hashtag="#test",
            trend_type=TrendType.VIRAL,
            engagement_level=EngagementLevel.HIGH,
            viral_score=0.85,
            growth_rate=0.5,
            velocity_score=0.7,
            momentum_score=0.6,
            predicted_reach=10000,
            confidence_level=0.9,
            analysis_timestamp=datetime.utcnow(),
            metadata={"data_points": 10, "time_span_days": 7}
        )
        
        assert analysis.hashtag == "#test"
        assert analysis.trend_type == TrendType.VIRAL
        assert analysis.engagement_level == EngagementLevel.HIGH
        assert analysis.viral_score == 0.85
        assert analysis.growth_rate == 0.5
        assert analysis.velocity_score == 0.7
        assert analysis.momentum_score == 0.6
        assert analysis.predicted_reach == 10000
        assert analysis.confidence_level == 0.9
        assert "data_points" in analysis.metadata

    def test_viral_metrics_dataclass(self):
        """Testa criação de objeto ViralMetrics."""
        metrics = ViralMetrics(
            shares_per_view=0.04,
            comments_per_view=0.08,
            likes_per_view=0.15,
            completion_rate=0.83,
            watch_time_avg=25.0,
            viral_coefficient=0.12,
            reach_velocity=1000.0
        )
        
        assert metrics.shares_per_view == 0.04
        assert metrics.comments_per_view == 0.08
        assert metrics.likes_per_view == 0.15
        assert metrics.completion_rate == 0.83
        assert metrics.watch_time_avg == 25.0
        assert metrics.viral_coefficient == 0.12
        assert metrics.reach_velocity == 1000.0

    def test_analyzer_initialization(self, config):
        """Testa inicialização do TikTokTrendsAnalyzer."""
        analyzer = TikTokTrendsAnalyzer(config)
        
        assert analyzer.config == config
        assert analyzer.viral_threshold == 0.8
        assert analyzer.growth_threshold == 0.3
        assert analyzer.engagement_thresholds["very_high"] == 0.15
        assert analyzer.engagement_thresholds["high"] == 0.10
        assert analyzer.engagement_thresholds["medium"] == 0.05
        assert analyzer.engagement_thresholds["low"] == 0.02
        assert analyzer.cache_ttl == 3600
        assert analyzer.analysis_cache == {}
        assert analyzer.circuit_breaker is not None
        assert analyzer.rate_limiter is not None
        assert analyzer.metrics is not None

    @pytest.mark.asyncio
    async def test_analyze_hashtag_trend_success(self, analyzer, sample_historical_data):
        """Testa análise bem-sucedida de tendência de hashtag."""
        with patch.object(analyzer.rate_limiter, 'check_rate_limit'):
            with patch.object(analyzer.metrics, 'increment_counter'):
                with patch.object(analyzer.metrics, 'record_histogram'):
                    analysis = await analyzer.analyze_hashtag_trend("#test", sample_historical_data)
        
        assert analysis.hashtag == "#test"
        assert analysis.trend_type in [TrendType.VIRAL, TrendType.GROWING, TrendType.STABLE, TrendType.DECLINING, TrendType.EMERGING]
        assert analysis.engagement_level in [EngagementLevel.VERY_HIGH, EngagementLevel.HIGH, EngagementLevel.MEDIUM, EngagementLevel.LOW, EngagementLevel.VERY_LOW]
        assert 0.0 <= analysis.viral_score <= 1.0
        assert analysis.growth_rate > 0  # Dados crescentes
        assert 0.0 <= analysis.velocity_score <= 1.0
        assert 0.0 <= analysis.momentum_score <= 1.0
        assert analysis.predicted_reach > 0
        assert 0.0 <= analysis.confidence_level <= 1.0
        assert analysis.analysis_timestamp is not None
        assert "data_points" in analysis.metadata
        assert "time_span_days" in analysis.metadata
        assert "peak_views" in analysis.metadata
        assert "avg_engagement" in analysis.metadata

    @pytest.mark.asyncio
    async def test_analyze_hashtag_trend_cache_hit(self, analyzer, sample_historical_data):
        """Testa retorno de análise em cache."""
        # Primeira análise para popular cache
        with patch.object(analyzer.rate_limiter, 'check_rate_limit'):
            with patch.object(analyzer.metrics, 'increment_counter'):
                with patch.object(analyzer.metrics, 'record_histogram'):
                    first_analysis = await analyzer.analyze_hashtag_trend("#test", sample_historical_data)
        
        # Segunda análise deve retornar do cache
        with patch.object(analyzer.rate_limiter, 'check_rate_limit'):
            with patch.object(analyzer.metrics, 'increment_counter'):
                with patch.object(analyzer.metrics, 'record_histogram'):
                    second_analysis = await analyzer.analyze_hashtag_trend("#test", sample_historical_data)
        
        assert first_analysis.hashtag == second_analysis.hashtag
        assert first_analysis.trend_type == second_analysis.trend_type
        assert first_analysis.viral_score == second_analysis.viral_score

    @pytest.mark.asyncio
    async def test_analyze_hashtag_trend_empty_data(self, analyzer):
        """Testa análise com dados vazios."""
        with patch.object(analyzer.rate_limiter, 'check_rate_limit'):
            analysis = await analyzer.analyze_hashtag_trend("#test", [])
        
        assert analysis.hashtag == "#test"
        assert analysis.viral_score == 0.0
        assert analysis.growth_rate == 0.0
        assert analysis.velocity_score == 0.0
        assert analysis.momentum_score == 0.0
        assert analysis.predicted_reach == 0
        assert analysis.confidence_level == 0.3  # Baixa confiança com poucos dados

    @pytest.mark.asyncio
    async def test_analyze_viral_potential_success(self, analyzer, sample_video_data):
        """Testa análise bem-sucedida de potencial viral."""
        with patch.object(analyzer.rate_limiter, 'check_rate_limit'):
            with patch.object(analyzer.metrics, 'increment_counter'):
                with patch.object(analyzer.metrics, 'record_histogram'):
                    metrics = await analyzer.analyze_viral_potential(sample_video_data)
        
        assert metrics.shares_per_view == 0.04  # 400 / 10000
        assert metrics.comments_per_view == 0.08  # 800 / 10000
        assert metrics.likes_per_view == 0.15  # 1500 / 10000
        assert metrics.completion_rate == 0.83  # 250000 / (10000 * 30)
        assert metrics.watch_time_avg == 25.0  # 250000 / 10000
        assert metrics.viral_coefficient > 0
        assert metrics.reach_velocity > 0

    @pytest.mark.asyncio
    async def test_analyze_viral_potential_zero_views(self, analyzer):
        """Testa análise viral com zero visualizações."""
        video_data = {
            "id": "video123",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "duration": 30,
            "watch_time": 0,
            "created_time": "2025-01-27T10:00:00Z"
        }
        
        with patch.object(analyzer.rate_limiter, 'check_rate_limit'):
            with patch.object(analyzer.metrics, 'increment_counter'):
                with patch.object(analyzer.metrics, 'record_histogram'):
                    metrics = await analyzer.analyze_viral_potential(video_data)
        
        assert metrics.shares_per_view == 0.0
        assert metrics.comments_per_view == 0.0
        assert metrics.likes_per_view == 0.0
        assert metrics.completion_rate == 0.0
        assert metrics.watch_time_avg == 0.0
        assert metrics.viral_coefficient == 0.0
        assert metrics.reach_velocity == 0.0

    @pytest.mark.asyncio
    async def test_detect_emerging_trends_success(self, analyzer):
        """Testa detecção bem-sucedida de tendências emergentes."""
        hashtags_data = [
            {
                "hashtag": "#trending1",
                "historical_data": [
                    {"timestamp": "2025-01-27T10:00:00Z", "views": 1000, "engagement_rate": 0.1},
                    {"timestamp": "2025-01-27T11:00:00Z", "views": 2000, "engagement_rate": 0.15},
                    {"timestamp": "2025-01-27T12:00:00Z", "views": 5000, "engagement_rate": 0.2}
                ]
            },
            {
                "hashtag": "#trending2",
                "historical_data": [
                    {"timestamp": "2025-01-27T10:00:00Z", "views": 500, "engagement_rate": 0.05},
                    {"timestamp": "2025-01-27T11:00:00Z", "views": 600, "engagement_rate": 0.06},
                    {"timestamp": "2025-01-27T12:00:00Z", "views": 700, "engagement_rate": 0.07}
                ]
            }
        ]
        
        with patch.object(analyzer.rate_limiter, 'check_rate_limit'):
            with patch.object(analyzer.metrics, 'increment_counter'):
                trends = await analyzer.detect_emerging_trends(hashtags_data, time_window_hours=24)
        
        assert isinstance(trends, list)
        # Pelo menos uma tendência deve ser detectada (primeira tem crescimento forte)
        assert len(trends) >= 1
        assert all(trend.trend_type in [TrendType.EMERGING, TrendType.GROWING] for trend in trends)
        assert all(trend.confidence_level > 0.7 for trend in trends)

    @pytest.mark.asyncio
    async def test_detect_emerging_trends_insufficient_data(self, analyzer):
        """Testa detecção com dados insuficientes."""
        hashtags_data = [
            {
                "hashtag": "#insufficient",
                "historical_data": [
                    {"timestamp": "2025-01-27T10:00:00Z", "views": 1000, "engagement_rate": 0.1}
                ]
            }
        ]
        
        with patch.object(analyzer.rate_limiter, 'check_rate_limit'):
            with patch.object(analyzer.metrics, 'increment_counter'):
                trends = await analyzer.detect_emerging_trends(hashtags_data, time_window_hours=24)
        
        assert len(trends) == 0  # Dados insuficientes (menos de 3 pontos)

    def test_process_historical_data(self, analyzer, sample_historical_data):
        """Testa processamento de dados históricos."""
        processed = analyzer._process_historical_data(sample_historical_data)
        
        assert "timestamps" in processed
        assert "views" in processed
        assert "likes" in processed
        assert "comments" in processed
        assert "shares" in processed
        assert "engagement_rates" in processed
        assert "growth_rates" in processed
        assert "velocity_metrics" in processed
        assert "momentum_indicators" in processed
        
        assert len(processed["views"]) == 3
        assert len(processed["growth_rates"]) == 2  # n-1 pontos
        assert len(processed["velocity_metrics"]) == 2  # n-1 pontos
        assert len(processed["momentum_indicators"]) == 1  # n-2 pontos

    def test_process_historical_data_empty(self, analyzer):
        """Testa processamento de dados históricos vazios."""
        processed = analyzer._process_historical_data([])
        assert processed == {}

    def test_calculate_viral_score(self, analyzer):
        """Testa cálculo de viral score."""
        processed_data = {
            "views": [1000, 2000, 5000],
            "engagement_rates": [0.1, 0.15, 0.2],
            "growth_rates": [1.0, 1.5],
            "velocity_metrics": [1000, 3000]
        }
        
        viral_score = analyzer._calculate_viral_score(processed_data)
        
        assert 0.0 <= viral_score <= 1.0
        assert viral_score > 0  # Dados com crescimento

    def test_calculate_viral_score_empty_data(self, analyzer):
        """Testa cálculo de viral score com dados vazios."""
        viral_score = analyzer._calculate_viral_score({})
        assert viral_score == 0.0

    def test_calculate_growth_rate(self, analyzer):
        """Testa cálculo de taxa de crescimento."""
        processed_data = {
            "views": [1000, 2000, 5000]
        }
        
        growth_rate = analyzer._calculate_growth_rate(processed_data)
        
        assert growth_rate == 4.0  # (5000 - 1000) / 1000

    def test_calculate_growth_rate_insufficient_data(self, analyzer):
        """Testa cálculo de taxa de crescimento com dados insuficientes."""
        growth_rate = analyzer._calculate_growth_rate({"views": [1000]})
        assert growth_rate == 0.0

    def test_calculate_growth_rate_zero_initial(self, analyzer):
        """Testa cálculo de taxa de crescimento com zero inicial."""
        growth_rate = analyzer._calculate_growth_rate({"views": [0, 1000]})
        assert growth_rate == 0.0

    def test_calculate_velocity_score(self, analyzer):
        """Testa cálculo de velocity score."""
        processed_data = {
            "velocity_metrics": [500, 1000, 1500]
        }
        
        velocity_score = analyzer._calculate_velocity_score(processed_data)
        
        assert 0.0 <= velocity_score <= 1.0
        assert velocity_score > 0

    def test_calculate_velocity_score_empty_data(self, analyzer):
        """Testa cálculo de velocity score com dados vazios."""
        velocity_score = analyzer._calculate_velocity_score({})
        assert velocity_score == 0.0

    def test_calculate_momentum_score(self, analyzer):
        """Testa cálculo de momentum score."""
        processed_data = {
            "momentum_indicators": [1.2, 1.5, 1.8]
        }
        
        momentum_score = analyzer._calculate_momentum_score(processed_data)
        
        assert 0.0 <= momentum_score <= 1.0
        assert momentum_score > 0

    def test_calculate_momentum_score_empty_data(self, analyzer):
        """Testa cálculo de momentum score com dados vazios."""
        momentum_score = analyzer._calculate_momentum_score({})
        assert momentum_score == 0.0

    def test_determine_trend_type_viral(self, analyzer):
        """Testa determinação de tipo viral."""
        trend_type = analyzer._determine_trend_type(
            viral_score=0.9,  # > 0.8
            growth_rate=0.5,  # > 0.3
            velocity_score=0.7
        )
        assert trend_type == TrendType.VIRAL

    def test_determine_trend_type_growing(self, analyzer):
        """Testa determinação de tipo growing."""
        trend_type = analyzer._determine_trend_type(
            viral_score=0.5,  # < 0.8
            growth_rate=0.5,  # > 0.3
            velocity_score=0.7  # > 0.5
        )
        assert trend_type == TrendType.GROWING

    def test_determine_trend_type_stable(self, analyzer):
        """Testa determinação de tipo stable."""
        trend_type = analyzer._determine_trend_type(
            viral_score=0.3,
            growth_rate=0.2,  # > 0, <= 0.3
            velocity_score=0.3
        )
        assert trend_type == TrendType.STABLE

    def test_determine_trend_type_declining(self, analyzer):
        """Testa determinação de tipo declining."""
        trend_type = analyzer._determine_trend_type(
            viral_score=0.3,
            growth_rate=-0.1,  # < 0
            velocity_score=0.3
        )
        assert trend_type == TrendType.DECLINING

    def test_determine_trend_type_emerging(self, analyzer):
        """Testa determinação de tipo emerging."""
        trend_type = analyzer._determine_trend_type(
            viral_score=0.6,  # > 0.5
            growth_rate=0.2,
            velocity_score=0.4  # > 0.3
        )
        assert trend_type == TrendType.EMERGING

    def test_calculate_engagement_level_very_high(self, analyzer):
        """Testa cálculo de nível de engajamento muito alto."""
        processed_data = {
            "engagement_rates": [0.18, 0.20, 0.22]  # > 0.15
        }
        
        engagement_level = analyzer._calculate_engagement_level(processed_data)
        assert engagement_level == EngagementLevel.VERY_HIGH

    def test_calculate_engagement_level_high(self, analyzer):
        """Testa cálculo de nível de engajamento alto."""
        processed_data = {
            "engagement_rates": [0.12, 0.13, 0.14]  # > 0.10, <= 0.15
        }
        
        engagement_level = analyzer._calculate_engagement_level(processed_data)
        assert engagement_level == EngagementLevel.HIGH

    def test_calculate_engagement_level_medium(self, analyzer):
        """Testa cálculo de nível de engajamento médio."""
        processed_data = {
            "engagement_rates": [0.07, 0.08, 0.09]  # > 0.05, <= 0.10
        }
        
        engagement_level = analyzer._calculate_engagement_level(processed_data)
        assert engagement_level == EngagementLevel.MEDIUM

    def test_calculate_engagement_level_low(self, analyzer):
        """Testa cálculo de nível de engajamento baixo."""
        processed_data = {
            "engagement_rates": [0.03, 0.04]  # > 0.02, <= 0.05
        }
        
        engagement_level = analyzer._calculate_engagement_level(processed_data)
        assert engagement_level == EngagementLevel.LOW

    def test_calculate_engagement_level_very_low(self, analyzer):
        """Testa cálculo de nível de engajamento muito baixo."""
        processed_data = {
            "engagement_rates": [0.01, 0.015]  # <= 0.02
        }
        
        engagement_level = analyzer._calculate_engagement_level(processed_data)
        assert engagement_level == EngagementLevel.VERY_LOW

    def test_calculate_engagement_level_empty_data(self, analyzer):
        """Testa cálculo de nível de engajamento com dados vazios."""
        engagement_level = analyzer._calculate_engagement_level({})
        assert engagement_level == EngagementLevel.VERY_LOW

    def test_predict_reach(self, analyzer):
        """Testa predição de alcance."""
        processed_data = {
            "views": [1000, 2000, 5000]
        }
        
        predicted_reach = analyzer._predict_reach(processed_data, viral_score=0.8)
        
        assert predicted_reach > 5000  # Deve ser maior que o último valor

    def test_predict_reach_empty_data(self, analyzer):
        """Testa predição de alcance com dados vazios."""
        predicted_reach = analyzer._predict_reach({}, viral_score=0.8)
        assert predicted_reach == 0

    def test_calculate_confidence_level(self, analyzer):
        """Testa cálculo de nível de confiança."""
        processed_data = {
            "views": [1000, 2000, 3000, 4000, 5000]  # 5 pontos
        }
        
        confidence_level = analyzer._calculate_confidence_level(processed_data)
        
        assert 0.0 <= confidence_level <= 1.0
        assert confidence_level > 0.3  # Mais de 3 pontos

    def test_calculate_confidence_level_insufficient_data(self, analyzer):
        """Testa cálculo de nível de confiança com dados insuficientes."""
        confidence_level = analyzer._calculate_confidence_level({"views": [1000, 2000]})
        assert confidence_level == 0.3  # Baixa confiança

    def test_calculate_viral_coefficient(self, analyzer):
        """Testa cálculo de coeficiente viral."""
        coefficient = analyzer._calculate_viral_coefficient(shares=100, views=1000, comments=50)
        
        # (100 + 50 * 0.5) / 1000 = 125 / 1000 = 0.125
        assert coefficient == 0.125

    def test_calculate_viral_coefficient_zero_views(self, analyzer):
        """Testa cálculo de coeficiente viral com zero visualizações."""
        coefficient = analyzer._calculate_viral_coefficient(shares=100, views=0, comments=50)
        assert coefficient == 0.0

    def test_calculate_reach_velocity(self, analyzer):
        """Testa cálculo de velocidade de alcance."""
        video_data = {
            "views": 10000,
            "created_time": "2025-01-27T10:00:00Z"
        }
        
        with patch('infrastructure.coleta.tiktok_trends_analyzer.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2025, 1, 27, 12, 0, 0)  # 2 horas depois
            velocity = analyzer._calculate_reach_velocity(video_data)
        
        assert velocity == 5000.0  # 10000 views / 2 horas

    def test_calculate_reach_velocity_zero_views(self, analyzer):
        """Testa cálculo de velocidade de alcance com zero visualizações."""
        video_data = {
            "views": 0,
            "created_time": "2025-01-27T10:00:00Z"
        }
        
        velocity = analyzer._calculate_reach_velocity(video_data)
        assert velocity == 0.0

    def test_calculate_point_growth_rates(self, analyzer):
        """Testa cálculo de taxas de crescimento ponto a ponto."""
        views = [1000, 2000, 5000]
        growth_rates = analyzer._calculate_point_growth_rates(views)
        
        assert len(growth_rates) == 2
        assert growth_rates[0] == 1.0  # (2000 - 1000) / 1000
        assert growth_rates[1] == 1.5  # (5000 - 2000) / 2000

    def test_calculate_point_growth_rates_zero_previous(self, analyzer):
        """Testa cálculo de taxas de crescimento com zero anterior."""
        views = [0, 1000, 2000]
        growth_rates = analyzer._calculate_point_growth_rates(views)
        
        assert len(growth_rates) == 2
        assert growth_rates[0] == 0.0  # Divisão por zero
        assert growth_rates[1] == 1.0  # (2000 - 1000) / 1000

    def test_calculate_velocity_metrics(self, analyzer):
        """Testa cálculo de métricas de velocidade."""
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(['2025-01-27T10:00:00Z', '2025-01-27T11:00:00Z', '2025-01-27T12:00:00Z']),
            'views': [1000, 2000, 5000]
        })
        
        velocity_metrics = analyzer._calculate_velocity_metrics(df)
        
        assert len(velocity_metrics) == 2
        assert velocity_metrics[0] == 1000.0  # (2000 - 1000) / 1 hora
        assert velocity_metrics[1] == 3000.0  # (5000 - 2000) / 1 hora

    def test_calculate_momentum_indicators(self, analyzer):
        """Testa cálculo de indicadores de momentum."""
        df = pd.DataFrame({
            'views': [1000, 2000, 5000, 8000]
        })
        
        momentum_indicators = analyzer._calculate_momentum_indicators(df)
        
        assert len(momentum_indicators) == 2
        assert momentum_indicators[0] == 1.5  # (5000 - 2000) / (2000 - 1000)
        assert momentum_indicators[1] == 1.0  # (8000 - 5000) / (5000 - 2000)

    def test_calculate_time_span(self, analyzer, sample_historical_data):
        """Testa cálculo de span de tempo."""
        time_span = analyzer._calculate_time_span(sample_historical_data)
        
        assert time_span == 0  # Mesmo dia

    def test_calculate_time_span_insufficient_data(self, analyzer):
        """Testa cálculo de span de tempo com dados insuficientes."""
        time_span = analyzer._calculate_time_span([{"timestamp": "2025-01-27T10:00:00Z"}])
        assert time_span == 0

    def test_generate_cache_key(self, analyzer, sample_historical_data):
        """Testa geração de chave de cache."""
        cache_key = analyzer._generate_cache_key("#test", sample_historical_data)
        
        assert cache_key.startswith("trend_analysis:#test:")
        assert len(cache_key) > 20  # Deve ter hash

    def test_generate_cache_key_different_data(self, analyzer):
        """Testa geração de chaves de cache diferentes para dados diferentes."""
        data1 = [{"timestamp": "2025-01-27T10:00:00Z", "views": 1000}]
        data2 = [{"timestamp": "2025-01-27T10:00:00Z", "views": 2000}]
        
        key1 = analyzer._generate_cache_key("#test", data1)
        key2 = analyzer._generate_cache_key("#test", data2)
        
        assert key1 != key2

    def test_edge_cases(self, analyzer):
        """Testa casos edge."""
        # Teste com dados muito grandes
        large_data = [{"timestamp": "2025-01-27T10:00:00Z", "views": 1000000000, "engagement_rate": 0.5}]
        
        processed = analyzer._process_historical_data(large_data)
        assert "views" in processed
        assert processed["views"][0] == 1000000000

        # Teste com dados negativos
        negative_data = [{"timestamp": "2025-01-27T10:00:00Z", "views": -1000, "engagement_rate": -0.1}]
        
        processed = analyzer._process_historical_data(negative_data)
        assert "views" in processed
        assert processed["views"][0] == -1000


if __name__ == "__main__":
    pytest.main([__file__]) 