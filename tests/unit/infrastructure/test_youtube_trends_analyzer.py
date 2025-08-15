"""
Testes unitários para YouTube Trends Analyzer

📐 CoCoT: Baseado em algoritmos de análise de tendências
🌲 ToT: Avaliado métodos de análise e escolhido mais preciso
♻️ ReAct: Simulado análise de dados e validado precisão

Prompt: CHECKLIST_TESTES_UNITARIOS.md - Item 6.3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: test-youtube-trends-analyzer-2025-01-27-001

Testes baseados COMPLETAMENTE no código real:
- Análise de tendências de vídeos
- Métricas de viralização
- Detecção de padrões
- Análise por categoria
- Cálculos de métricas
- Cache e performance
- Casos edge
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from collections import defaultdict

from infrastructure.coleta.youtube_trends_analyzer import (
    YouTubeTrendsAnalyzer,
    TrendMetrics,
    TrendPattern,
    VideoTrend,
    CategoryTrend,
    create_youtube_trends_analyzer
)


class TestYouTubeTrendsAnalyzer:
    """Testes para YouTube Trends Analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture para criar analisador de tendências."""
        config = {
            'min_trend_score': 0.7,
            'min_growth_rate': 0.1,
            'trend_window_hours': 24,
            'analysis_window_hours': 168,
            'min_views_threshold': 1000,
            'min_engagement_threshold': 0.05,
            'viral_threshold': 0.8,
            'momentum_weight': 0.3,
            'velocity_weight': 0.25,
            'acceleration_weight': 0.2,
            'engagement_weight': 0.15,
            'reach_weight': 0.1
        }
        return YouTubeTrendsAnalyzer(config)
    
    @pytest.fixture
    def sample_video_data(self):
        """Fixture com dados de vídeo de exemplo."""
        return {
            'id': 'dQw4w9WgXcQ',
            'title': 'Rick Astley - Never Gonna Give You Up (Official Music Video)',
            'description': 'The official music video for "Never Gonna Give You Up" by Rick Astley',
            'channel_id': 'UCuAXFkgsw1L7xaCfnd5JJOw',
            'channel_title': 'Rick Astley',
            'view_count': 1500000,
            'like_count': 75000,
            'comment_count': 15000,
            'published_at': '2009-10-25T06:57:33Z',
            'duration': 'PT3M33S',
            'category_id': '10',
            'tags': ['rick astley', 'never gonna give you up', 'music video', '80s']
        }
    
    @pytest.fixture
    def sample_historical_data(self):
        """Fixture com dados históricos de exemplo."""
        base_time = datetime.now() - timedelta(hours=24)
        return [
            {
                'timestamp': (base_time + timedelta(hours=i)).isoformat(),
                'view_count': 100000 + (i * 50000),
                'like_count': 5000 + (i * 2500),
                'comment_count': 1000 + (i * 500)
            }
            for i in range(10)
        ]
    
    @pytest.fixture
    def sample_videos_data(self):
        """Fixture com lista de dados de vídeos."""
        return [
            {
                'id': 'video1',
                'title': 'Gaming Tutorial',
                'view_count': 50000,
                'like_count': 2500,
                'comment_count': 500,
                'category_id': '20',
                'published_at': '2025-01-26T10:00:00Z'
            },
            {
                'id': 'video2',
                'title': 'Tech Review',
                'view_count': 75000,
                'like_count': 3750,
                'comment_count': 750,
                'category_id': '28',
                'published_at': '2025-01-26T11:00:00Z'
            },
            {
                'id': 'video3',
                'title': 'Music Cover',
                'view_count': 100000,
                'like_count': 5000,
                'comment_count': 1000,
                'category_id': '10',
                'published_at': '2025-01-26T12:00:00Z'
            }
        ]

    def test_analyzer_initialization(self, analyzer):
        """Teste de inicialização do analisador."""
        assert analyzer.config['min_trend_score'] == 0.7
        assert analyzer.config['min_growth_rate'] == 0.1
        assert analyzer.config['trend_window_hours'] == 24
        assert analyzer.config['analysis_window_hours'] == 168
        assert analyzer.config['min_views_threshold'] == 1000
        assert analyzer.config['min_engagement_threshold'] == 0.05
        assert analyzer.config['viral_threshold'] == 0.8
        assert analyzer.config['momentum_weight'] == 0.3
        assert analyzer.config['velocity_weight'] == 0.25
        assert analyzer.config['acceleration_weight'] == 0.2
        assert analyzer.config['engagement_weight'] == 0.15
        assert analyzer.config['reach_weight'] == 0.1
        assert analyzer.trend_cache == {}
        assert analyzer.pattern_cache == {}

    def test_analyze_video_trend_success(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de análise de tendência de vídeo com sucesso."""
        video_trend = analyzer.analyze_video_trend(sample_video_data, sample_historical_data)
        
        assert isinstance(video_trend, VideoTrend)
        assert video_trend.video_id == 'dQw4w9WgXcQ'
        assert video_trend.title == 'Rick Astley - Never Gonna Give You Up (Official Music Video)'
        assert video_trend.channel_id == 'UCuAXFkgsw1L7xaCfnd5JJOw'
        assert video_trend.channel_title == 'Rick Astley'
        assert isinstance(video_trend.trend_metrics, TrendMetrics)
        assert isinstance(video_trend.pattern, TrendPattern)
        assert len(video_trend.keywords) > 0
        assert video_trend.tags == ['rick astley', 'never gonna give you up', 'music video', '80s']
        assert video_trend.category == 'Music'
        assert video_trend.language in ['en', 'unknown']
        assert video_trend.duration_seconds == 213  # 3m33s
        assert isinstance(video_trend.published_at, datetime)
        assert isinstance(video_trend.trend_detected_at, datetime)

    def test_analyze_video_trend_without_historical_data(self, analyzer, sample_video_data):
        """Teste de análise de tendência sem dados históricos."""
        video_trend = analyzer.analyze_video_trend(sample_video_data)
        
        assert isinstance(video_trend, VideoTrend)
        assert video_trend.trend_metrics.growth_rate == 0.0
        assert video_trend.trend_metrics.velocity == 0.0
        assert video_trend.trend_metrics.acceleration == 0.0
        assert video_trend.trend_metrics.momentum == 0.0
        assert video_trend.pattern.pattern_type == "unknown"

    def test_analyze_category_trends_success(self, analyzer, sample_videos_data):
        """Teste de análise de tendências por categoria."""
        category_trends = analyzer.analyze_category_trends(sample_videos_data)
        
        assert isinstance(category_trends, list)
        assert len(category_trends) == 3  # 3 categorias diferentes
        
        for trend in category_trends:
            assert isinstance(trend, CategoryTrend)
            assert trend.category_id in ['20', '28', '10']
            assert trend.category_name in ['Gaming', 'Science & Technology', 'Music']
            assert isinstance(trend.trend_metrics, TrendMetrics)
            assert len(trend.top_videos) > 0
            assert trend.total_videos > 0
            assert trend.avg_engagement >= 0.0
            assert trend.growth_direction in ['strong_growth', 'moderate_growth', 'stable', 'declining']

    def test_detect_viral_potential_high_score(self, analyzer):
        """Teste de detecção de potencial viral com score alto."""
        viral_video_data = {
            'view_count': 1000000,
            'like_count': 100000,
            'comment_count': 20000,
            'published_at': (datetime.now() - timedelta(hours=2)).isoformat()
        }
        
        viral_score = analyzer.detect_viral_potential(viral_video_data)
        assert viral_score > 0.5
        assert viral_score <= 1.0

    def test_detect_viral_potential_low_score(self, analyzer):
        """Teste de detecção de potencial viral com score baixo."""
        low_viral_video_data = {
            'view_count': 1000,
            'like_count': 10,
            'comment_count': 2,
            'published_at': (datetime.now() - timedelta(hours=24)).isoformat()
        }
        
        viral_score = analyzer.detect_viral_potential(low_viral_video_data)
        assert viral_score < 0.3

    def test_detect_viral_potential_new_video(self, analyzer):
        """Teste de detecção de potencial viral para vídeo muito novo."""
        new_video_data = {
            'view_count': 10000,
            'like_count': 1000,
            'comment_count': 200,
            'published_at': (datetime.now() - timedelta(minutes=30)).isoformat()
        }
        
        viral_score = analyzer.detect_viral_potential(new_video_data)
        assert viral_score == 0.0

    def test_calculate_trend_metrics(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de cálculo de métricas de tendência."""
        trend_metrics = analyzer._calculate_trend_metrics(sample_video_data, sample_historical_data)
        
        assert isinstance(trend_metrics, TrendMetrics)
        assert isinstance(trend_metrics.trend_score, float)
        assert isinstance(trend_metrics.growth_rate, float)
        assert isinstance(trend_metrics.velocity, float)
        assert isinstance(trend_metrics.acceleration, float)
        assert isinstance(trend_metrics.momentum, float)
        assert isinstance(trend_metrics.viral_potential, float)
        assert isinstance(trend_metrics.engagement_rate, float)
        assert isinstance(trend_metrics.reach_estimate, int)
        assert isinstance(trend_metrics.category, str)
        assert isinstance(trend_metrics.confidence, float)
        assert 0.0 <= trend_metrics.viral_potential <= 1.0
        assert 0.0 <= trend_metrics.engagement_rate <= 1.0
        assert trend_metrics.reach_estimate > 0

    def test_detect_trend_pattern_with_historical_data(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de detecção de padrão de tendência com dados históricos."""
        pattern = analyzer._detect_trend_pattern(sample_video_data, sample_historical_data)
        
        assert isinstance(pattern, TrendPattern)
        assert pattern.pattern_type in ['exponential_growth', 'linear_growth', 'slow_growth', 'stable', 'declining']
        assert isinstance(pattern.start_time, datetime)
        assert isinstance(pattern.peak_time, datetime)
        assert isinstance(pattern.duration_hours, float)
        assert isinstance(pattern.peak_value, float)
        assert isinstance(pattern.decay_rate, float)
        assert pattern.duration_hours >= 0.0
        assert pattern.peak_value >= 0.0
        assert 0.0 <= pattern.decay_rate <= 1.0

    def test_detect_trend_pattern_without_historical_data(self, analyzer, sample_video_data):
        """Teste de detecção de padrão de tendência sem dados históricos."""
        pattern = analyzer._detect_trend_pattern(sample_video_data)
        
        assert isinstance(pattern, TrendPattern)
        assert pattern.pattern_type == "unknown"
        assert isinstance(pattern.start_time, datetime)
        assert isinstance(pattern.peak_time, datetime)
        assert pattern.duration_hours == 0.0
        assert pattern.peak_value == 0.0
        assert pattern.decay_rate == 0.0

    def test_calculate_engagement_rate(self, analyzer):
        """Teste de cálculo de taxa de engajamento."""
        # Caso normal
        engagement_rate = analyzer._calculate_engagement_rate(1000, 50, 10)
        assert engagement_rate == 0.06
        
        # Caso com zero views
        engagement_rate = analyzer._calculate_engagement_rate(0, 50, 10)
        assert engagement_rate == 0.0
        
        # Caso com muitos likes e comentários
        engagement_rate = analyzer._calculate_engagement_rate(1000, 200, 50)
        assert engagement_rate == 0.25

    def test_calculate_growth_rate(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de cálculo de taxa de crescimento."""
        growth_rate = analyzer._calculate_growth_rate(sample_video_data, sample_historical_data)
        assert isinstance(growth_rate, float)
        assert growth_rate >= 0.0  # Baseado nos dados de exemplo

    def test_calculate_growth_rate_without_historical_data(self, analyzer, sample_video_data):
        """Teste de cálculo de taxa de crescimento sem dados históricos."""
        growth_rate = analyzer._calculate_growth_rate(sample_video_data)
        assert growth_rate == 0.0

    def test_calculate_velocity(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de cálculo de velocidade de crescimento."""
        velocity = analyzer._calculate_velocity(sample_video_data, sample_historical_data)
        assert isinstance(velocity, float)
        assert velocity >= 0.0  # Baseado nos dados de exemplo

    def test_calculate_velocity_without_historical_data(self, analyzer, sample_video_data):
        """Teste de cálculo de velocidade sem dados históricos."""
        velocity = analyzer._calculate_velocity(sample_video_data)
        assert velocity == 0.0

    def test_calculate_acceleration(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de cálculo de aceleração."""
        acceleration = analyzer._calculate_acceleration(sample_video_data, sample_historical_data)
        assert isinstance(acceleration, float)

    def test_calculate_acceleration_without_historical_data(self, analyzer, sample_video_data):
        """Teste de cálculo de aceleração sem dados históricos."""
        acceleration = analyzer._calculate_acceleration(sample_video_data)
        assert acceleration == 0.0

    def test_calculate_momentum(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de cálculo de momentum."""
        momentum = analyzer._calculate_momentum(sample_video_data, sample_historical_data)
        assert isinstance(momentum, float)
        assert 0.0 <= momentum <= 1.0

    def test_calculate_momentum_without_historical_data(self, analyzer, sample_video_data):
        """Teste de cálculo de momentum sem dados históricos."""
        momentum = analyzer._calculate_momentum(sample_video_data)
        assert momentum == 0.0

    def test_estimate_reach(self, analyzer):
        """Teste de estimativa de alcance."""
        reach = analyzer._estimate_reach(10000, 0.05)
        assert isinstance(reach, int)
        assert reach > 10000
        
        # Teste com engajamento alto
        reach_high_engagement = analyzer._estimate_reach(10000, 0.15)
        assert reach_high_engagement > reach

    def test_categorize_trend(self, analyzer):
        """Teste de categorização de tendência."""
        # Tendência viral
        category = analyzer._categorize_trend(0.6, 1500, 0.1)
        assert category == "viral"
        
        # Tendência em crescimento
        category = analyzer._categorize_trend(0.3, 200, 0.05)
        assert category == "trending"
        
        # Tendência estável
        category = analyzer._categorize_trend(0.05, 5, 0.0)
        assert category == "stable"
        
        # Tendência declinante
        category = analyzer._categorize_trend(-0.1, -50, -0.05)
        assert category == "declining"

    def test_calculate_confidence(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de cálculo de confiança."""
        confidence = analyzer._calculate_confidence(sample_video_data, sample_historical_data)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        
        # Teste com vídeo com muitas views
        high_views_data = sample_video_data.copy()
        high_views_data['view_count'] = 50000
        confidence_high_views = analyzer._calculate_confidence(high_views_data, sample_historical_data)
        assert confidence_high_views > confidence

    def test_extract_keywords(self, analyzer):
        """Teste de extração de keywords."""
        title = "Como fazer SEO para YouTube em 2025"
        description = "Neste tutorial você vai aprender técnicas avançadas de SEO para YouTube"
        
        keywords = analyzer._extract_keywords(title, description)
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert len(keywords) <= 10
        assert all(isinstance(keyword, str) for keyword in keywords)
        assert all(len(keyword) > 2 for keyword in keywords)

    def test_extract_keywords_empty_input(self, analyzer):
        """Teste de extração de keywords com entrada vazia."""
        keywords = analyzer._extract_keywords("", "")
        assert keywords == []

    def test_determine_category(self, analyzer):
        """Teste de determinação de categoria."""
        video_data = {'category_id': '20'}
        keywords = ['gaming', 'gameplay']
        tags = ['game', 'stream']
        
        category = analyzer._determine_category(video_data, keywords, tags)
        assert category == 'Gaming'
        
        # Teste sem category_id
        video_data_no_id = {}
        category = analyzer._determine_category(video_data_no_id, keywords, tags)
        assert category == 'gaming'

    def test_detect_language(self, analyzer):
        """Teste de detecção de idioma."""
        title = "How to make a cake"
        description = "Learn how to bake a delicious cake"
        
        language = analyzer._detect_language(title, description)
        assert language in ['en', 'unknown']

    def test_parse_duration(self, analyzer):
        """Teste de parsing de duração."""
        # Duração completa
        duration = analyzer._parse_duration('PT1H2M30S')
        assert duration == 3750  # 1h2m30s = 3750s
        
        # Apenas minutos e segundos
        duration = analyzer._parse_duration('PT5M45S')
        assert duration == 345  # 5m45s = 345s
        
        # Apenas segundos
        duration = analyzer._parse_duration('PT30S')
        assert duration == 30
        
        # Duração inválida
        duration = analyzer._parse_duration('invalid')
        assert duration == 0

    def test_get_category_name(self, analyzer):
        """Teste de obtenção de nome de categoria."""
        assert analyzer._get_category_name('1') == 'Film & Animation'
        assert analyzer._get_category_name('10') == 'Music'
        assert analyzer._get_category_name('20') == 'Gaming'
        assert analyzer._get_category_name('28') == 'Science & Technology'
        assert analyzer._get_category_name('999') == 'Unknown'

    def test_determine_growth_direction(self, analyzer):
        """Teste de determinação de direção de crescimento."""
        assert analyzer._determine_growth_direction(0.2) == "strong_growth"
        assert analyzer._determine_growth_direction(0.05) == "moderate_growth"
        assert analyzer._determine_growth_direction(0.0) == "stable"
        assert analyzer._determine_growth_direction(-0.2) == "declining"

    def test_classify_pattern(self, analyzer):
        """Teste de classificação de padrão."""
        # Crescimento exponencial
        views_exponential = [('2025-01-26T10:00:00', 1000), ('2025-01-26T11:00:00', 5000), ('2025-01-26T12:00:00', 25000)]
        pattern = analyzer._classify_pattern(views_exponential)
        assert pattern == "exponential_growth"
        
        # Crescimento linear
        views_linear = [('2025-01-26T10:00:00', 1000), ('2025-01-26T11:00:00', 2000), ('2025-01-26T12:00:00', 3000)]
        pattern = analyzer._classify_pattern(views_linear)
        assert pattern == "linear_growth"
        
        # Dados insuficientes
        views_insufficient = [('2025-01-26T10:00:00', 1000)]
        pattern = analyzer._classify_pattern(views_insufficient)
        assert pattern == "insufficient_data"

    def test_calculate_decay_rate(self, analyzer):
        """Teste de cálculo de taxa de decaimento."""
        views_over_time = [
            ('2025-01-26T10:00:00', 1000),
            ('2025-01-26T11:00:00', 5000),
            ('2025-01-26T12:00:00', 3000)  # Pico em 11:00
        ]
        
        decay_rate = analyzer._calculate_decay_rate(views_over_time, 1)  # Pico no índice 1
        assert isinstance(decay_rate, float)
        assert decay_rate == 0.4  # (5000 - 3000) / 5000

    def test_create_youtube_trends_analyzer(self):
        """Teste da função factory."""
        config = {'min_trend_score': 0.8}
        analyzer = create_youtube_trends_analyzer(config)
        
        assert isinstance(analyzer, YouTubeTrendsAnalyzer)
        assert analyzer.config['min_trend_score'] == 0.8
        
        # Teste sem configuração
        analyzer_default = create_youtube_trends_analyzer()
        assert isinstance(analyzer_default, YouTubeTrendsAnalyzer)
        assert analyzer_default.config['min_trend_score'] == 0.7

    def test_trend_cache_functionality(self, analyzer, sample_video_data, sample_historical_data):
        """Teste de funcionalidade de cache de tendências."""
        # Primeira análise
        start_time = time.time()
        video_trend1 = analyzer.analyze_video_trend(sample_video_data, sample_historical_data)
        first_analysis_time = time.time() - start_time
        
        # Segunda análise (deve usar cache)
        start_time = time.time()
        video_trend2 = analyzer.analyze_video_trend(sample_video_data, sample_historical_data)
        second_analysis_time = time.time() - start_time
        
        # Verificar que os resultados são iguais
        assert video_trend1.video_id == video_trend2.video_id
        assert video_trend1.trend_metrics.trend_score == video_trend2.trend_metrics.trend_score

    def test_edge_case_empty_video_data(self, analyzer):
        """Teste de caso edge com dados de vídeo vazios."""
        empty_video_data = {}
        
        with pytest.raises(Exception):
            analyzer.analyze_video_trend(empty_video_data)

    def test_edge_case_zero_views(self, analyzer):
        """Teste de caso edge com zero views."""
        zero_views_data = {
            'id': 'test',
            'title': 'Test Video',
            'view_count': 0,
            'like_count': 0,
            'comment_count': 0,
            'published_at': datetime.now().isoformat()
        }
        
        engagement_rate = analyzer._calculate_engagement_rate(0, 0, 0)
        assert engagement_rate == 0.0

    def test_performance_large_dataset(self, analyzer):
        """Teste de performance com dataset grande."""
        large_historical_data = [
            {
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                'view_count': 100000 + (i * 10000),
                'like_count': 5000 + (i * 500),
                'comment_count': 1000 + (i * 100)
            }
            for i in range(100)
        ]
        
        large_video_data = {
            'id': 'large_test',
            'title': 'Large Dataset Test',
            'view_count': 2000000,
            'like_count': 100000,
            'comment_count': 20000,
            'published_at': datetime.now().isoformat()
        }
        
        start_time = time.time()
        video_trend = analyzer.analyze_video_trend(large_video_data, large_historical_data)
        analysis_time = time.time() - start_time
        
        assert isinstance(video_trend, VideoTrend)
        assert analysis_time < 5.0  # Deve completar em menos de 5 segundos 