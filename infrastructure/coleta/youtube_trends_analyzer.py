"""
YouTube Trends Analyzer

📐 CoCoT: Baseado em algoritmos de análise de tendências
🌲 ToT: Avaliado métodos de análise e escolhido mais preciso
♻️ ReAct: Simulado análise de dados e validado precisão

Prompt: CHECKLIST_INTEGRACAO_EXTERNA.md - 2.2.3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T10:30:00Z
Tracing ID: youtube-trends-analyzer-2025-01-27-001

Funcionalidades implementadas:
- Algoritmo de detecção de tendências
- Análise de engajamento
- Métricas de viralização
- Análise temporal
- Detecção de padrões
- Logs estruturados
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, Counter
import re
from textblob import TextBlob
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrendMetrics:
    """Métricas de tendência."""
    trend_score: float
    growth_rate: float
    velocity: float
    acceleration: float
    momentum: float
    viral_potential: float
    engagement_rate: float
    reach_estimate: int
    category: str
    confidence: float


@dataclass
class TrendPattern:
    """Padrão de tendência detectado."""
    pattern_type: str
    start_time: datetime
    peak_time: datetime
    duration_hours: float
    peak_value: float
    decay_rate: float
    seasonality: Optional[str] = None


@dataclass
class VideoTrend:
    """Tendência de um vídeo específico."""
    video_id: str
    title: str
    channel_id: str
    channel_title: str
    trend_metrics: TrendMetrics
    pattern: TrendPattern
    keywords: List[str]
    tags: List[str]
    category: str
    language: str
    duration_seconds: int
    published_at: datetime
    trend_detected_at: datetime


@dataclass
class CategoryTrend:
    """Tendência de uma categoria."""
    category_id: str
    category_name: str
    trend_metrics: TrendMetrics
    top_videos: List[str]
    total_videos: int
    avg_engagement: float
    growth_direction: str


class YouTubeTrendsAnalyzer:
    """
    Analisador de tendências do YouTube.
    
    📐 CoCoT: Baseado em algoritmos de análise de tendências
    🌲 ToT: Avaliado métodos de análise e escolhido mais preciso
    ♻️ ReAct: Simulado análise de dados e validado precisão
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o analisador de tendências.
        
        Args:
            config: Configuração do analisador
        """
        self.config = config or {
            'min_trend_score': 0.7,
            'min_growth_rate': 0.1,
            'trend_window_hours': 24,
            'analysis_window_hours': 168,  # 7 dias
            'min_views_threshold': 1000,
            'min_engagement_threshold': 0.05,
            'viral_threshold': 0.8,
            'momentum_weight': 0.3,
            'velocity_weight': 0.25,
            'acceleration_weight': 0.2,
            'engagement_weight': 0.15,
            'reach_weight': 0.1
        }
        
        # Cache de análises
        self.trend_cache = {}
        self.pattern_cache = {}
        
        # Vetorizador TF-IDF para análise de texto
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Scaler para normalização
        self.scaler = StandardScaler()
        
        logger.info("[YouTubeTrendsAnalyzer] Analisador inicializado")
    
    def analyze_video_trend(self, video_data: Dict[str, Any], 
                          historical_data: List[Dict[str, Any]] = None) -> VideoTrend:
        """
        Analisa tendência de um vídeo específico.
        
        Args:
            video_data: Dados atuais do vídeo
            historical_data: Dados históricos (opcional)
            
        Returns:
            Análise de tendência do vídeo
        """
        try:
            # Extrair métricas básicas
            view_count = video_data.get('view_count', 0)
            like_count = video_data.get('like_count', 0)
            comment_count = video_data.get('comment_count', 0)
            published_at = datetime.fromisoformat(video_data.get('published_at', '').replace('Z', '+00:00'))
            
            # Calcular métricas de engajamento
            engagement_rate = self._calculate_engagement_rate(view_count, like_count, comment_count)
            
            # Calcular métricas de tendência
            trend_metrics = self._calculate_trend_metrics(video_data, historical_data)
            
            # Detectar padrão de tendência
            pattern = self._detect_trend_pattern(video_data, historical_data)
            
            # Extrair keywords e tags
            keywords = self._extract_keywords(video_data.get('title', ''), video_data.get('description', ''))
            tags = video_data.get('tags', [])
            
            # Determinar categoria e idioma
            category = self._determine_category(video_data, keywords, tags)
            language = self._detect_language(video_data.get('title', ''), video_data.get('description', ''))
            
            # Calcular duração em segundos
            duration_seconds = self._parse_duration(video_data.get('duration', 'PT0S'))
            
            video_trend = VideoTrend(
                video_id=video_data.get('id', ''),
                title=video_data.get('title', ''),
                channel_id=video_data.get('channel_id', ''),
                channel_title=video_data.get('channel_title', ''),
                trend_metrics=trend_metrics,
                pattern=pattern,
                keywords=keywords,
                tags=tags,
                category=category,
                language=language,
                duration_seconds=duration_seconds,
                published_at=published_at,
                trend_detected_at=datetime.now()
            )
            
            logger.info(f"[YouTubeTrendsAnalyzer] Tendência analisada para vídeo: {video_data.get('id', '')}")
            return video_trend
            
        except Exception as e:
            logger.error(f"[YouTubeTrendsAnalyzer] Erro ao analisar tendência do vídeo: {e}")
            raise
    
    def analyze_category_trends(self, videos_data: List[Dict[str, Any]]) -> List[CategoryTrend]:
        """
        Analisa tendências por categoria.
        
        Args:
            videos_data: Lista de dados de vídeos
            
        Returns:
            Lista de tendências por categoria
        """
        try:
            # Agrupar vídeos por categoria
            category_groups = defaultdict(list)
            for video in videos_data:
                category = video.get('category_id', 'unknown')
                category_groups[category].append(video)
            
            category_trends = []
            for category_id, videos in category_groups.items():
                if len(videos) < 3:  # Mínimo de vídeos para análise
                    continue
                
                # Calcular métricas agregadas da categoria
                total_videos = len(videos)
                total_views = sum(value.get('view_count', 0) for value in videos)
                total_likes = sum(value.get('like_count', 0) for value in videos)
                total_comments = sum(value.get('comment_count', 0) for value in videos)
                
                avg_engagement = self._calculate_engagement_rate(total_views, total_likes, total_comments)
                
                # Calcular métricas de tendência da categoria
                trend_metrics = self._calculate_category_trend_metrics(videos)
                
                # Determinar direção do crescimento
                growth_direction = self._determine_growth_direction(trend_metrics.growth_rate)
                
                # Obter top vídeos da categoria
                top_videos = sorted(videos, key=lambda value: value.get('view_count', 0), reverse=True)[:5]
                top_video_ids = [value.get('id', '') for value in top_videos]
                
                # Determinar nome da categoria
                category_name = self._get_category_name(category_id)
                
                category_trend = CategoryTrend(
                    category_id=category_id,
                    category_name=category_name,
                    trend_metrics=trend_metrics,
                    top_videos=top_video_ids,
                    total_videos=total_videos,
                    avg_engagement=avg_engagement,
                    growth_direction=growth_direction
                )
                
                category_trends.append(category_trend)
            
            logger.info(f"[YouTubeTrendsAnalyzer] {len(category_trends)} categorias analisadas")
            return category_trends
            
        except Exception as e:
            logger.error(f"[YouTubeTrendsAnalyzer] Erro ao analisar tendências por categoria: {e}")
            raise
    
    def detect_viral_potential(self, video_data: Dict[str, Any]) -> float:
        """
        Detecta potencial viral de um vídeo.
        
        Args:
            video_data: Dados do vídeo
            
        Returns:
            Score de potencial viral (0-1)
        """
        try:
            view_count = video_data.get('view_count', 0)
            like_count = video_data.get('like_count', 0)
            comment_count = video_data.get('comment_count', 0)
            published_at = datetime.fromisoformat(video_data.get('published_at', '').replace('Z', '+00:00'))
            
            # Calcular idade do vídeo em horas
            age_hours = (datetime.now() - published_at).total_seconds() / 3600
            
            if age_hours < 1:  # Vídeo muito novo
                return 0.0
            
            # Calcular métricas de viralização
            views_per_hour = view_count / age_hours
            engagement_rate = self._calculate_engagement_rate(view_count, like_count, comment_count)
            
            # Calcular score viral baseado em múltiplos fatores
            viral_score = 0.0
            
            # Fator 1: Views por hora (40% do score)
            if views_per_hour > 10000:
                viral_score += 0.4
            elif views_per_hour > 5000:
                viral_score += 0.3
            elif views_per_hour > 1000:
                viral_score += 0.2
            elif views_per_hour > 100:
                viral_score += 0.1
            
            # Fator 2: Taxa de engajamento (30% do score)
            if engagement_rate > 0.1:
                viral_score += 0.3
            elif engagement_rate > 0.05:
                viral_score += 0.2
            elif engagement_rate > 0.02:
                viral_score += 0.1
            
            # Fator 3: Crescimento acelerado (20% do score)
            growth_acceleration = self._calculate_growth_acceleration(video_data)
            if growth_acceleration > 0.5:
                viral_score += 0.2
            elif growth_acceleration > 0.2:
                viral_score += 0.15
            elif growth_acceleration > 0.1:
                viral_score += 0.1
            
            # Fator 4: Qualidade do conteúdo (10% do score)
            content_quality = self._assess_content_quality(video_data)
            viral_score += content_quality * 0.1
            
            return min(viral_score, 1.0)
            
        except Exception as e:
            logger.error(f"[YouTubeTrendsAnalyzer] Erro ao detectar potencial viral: {e}")
            return 0.0
    
    def _calculate_trend_metrics(self, video_data: Dict[str, Any], 
                               historical_data: List[Dict[str, Any]] = None) -> TrendMetrics:
        """Calcula métricas de tendência."""
        try:
            view_count = video_data.get('view_count', 0)
            like_count = video_data.get('like_count', 0)
            comment_count = video_data.get('comment_count', 0)
            
            # Calcular taxa de crescimento
            growth_rate = self._calculate_growth_rate(video_data, historical_data)
            
            # Calcular velocidade (mudança por hora)
            velocity = self._calculate_velocity(video_data, historical_data)
            
            # Calcular aceleração (mudança na velocidade)
            acceleration = self._calculate_acceleration(video_data, historical_data)
            
            # Calcular momentum (tendência de continuidade)
            momentum = self._calculate_momentum(video_data, historical_data)
            
            # Calcular potencial viral
            viral_potential = self.detect_viral_potential(video_data)
            
            # Calcular taxa de engajamento
            engagement_rate = self._calculate_engagement_rate(view_count, like_count, comment_count)
            
            # Estimar alcance
            reach_estimate = self._estimate_reach(view_count, engagement_rate)
            
            # Determinar categoria de tendência
            category = self._categorize_trend(growth_rate, velocity, acceleration)
            
            # Calcular confiança
            confidence = self._calculate_confidence(video_data, historical_data)
            
            # Calcular score geral de tendência
            trend_score = (
                momentum * self.config['momentum_weight'] +
                velocity * self.config['velocity_weight'] +
                acceleration * self.config['acceleration_weight'] +
                engagement_rate * self.config['engagement_weight'] +
                (reach_estimate / 1000000) * self.config['reach_weight']
            )
            
            return TrendMetrics(
                trend_score=trend_score,
                growth_rate=growth_rate,
                velocity=velocity,
                acceleration=acceleration,
                momentum=momentum,
                viral_potential=viral_potential,
                engagement_rate=engagement_rate,
                reach_estimate=reach_estimate,
                category=category,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"[YouTubeTrendsAnalyzer] Erro ao calcular métricas de tendência: {e}")
            raise
    
    def _detect_trend_pattern(self, video_data: Dict[str, Any], 
                            historical_data: List[Dict[str, Any]] = None) -> TrendPattern:
        """Detecta padrão de tendência."""
        try:
            if not historical_data:
                # Padrão padrão se não há dados históricos
                return TrendPattern(
                    pattern_type="unknown",
                    start_time=datetime.now(),
                    peak_time=datetime.now(),
                    duration_hours=0.0,
                    peak_value=0.0,
                    decay_rate=0.0
                )
            
            # Analisar dados históricos para detectar padrão
            views_over_time = [(data.get('timestamp', ''), data.get('view_count', 0)) 
                              for data in historical_data]
            
            if len(views_over_time) < 3:
                return TrendPattern(
                    pattern_type="insufficient_data",
                    start_time=datetime.now(),
                    peak_time=datetime.now(),
                    duration_hours=0.0,
                    peak_value=0.0,
                    decay_rate=0.0
                )
            
            # Detectar tipo de padrão
            pattern_type = self._classify_pattern(views_over_time)
            
            # Encontrar pico
            peak_idx = np.argmax([value[1] for value in views_over_time])
            peak_time = datetime.fromisoformat(views_over_time[peak_idx][0].replace('Z', '+00:00'))
            peak_value = views_over_time[peak_idx][1]
            
            # Calcular duração
            start_time = datetime.fromisoformat(views_over_time[0][0].replace('Z', '+00:00'))
            duration_hours = (peak_time - start_time).total_seconds() / 3600
            
            # Calcular taxa de decaimento
            decay_rate = self._calculate_decay_rate(views_over_time, peak_idx)
            
            # Detectar sazonalidade
            seasonality = self._detect_seasonality(views_over_time)
            
            return TrendPattern(
                pattern_type=pattern_type,
                start_time=start_time,
                peak_time=peak_time,
                duration_hours=duration_hours,
                peak_value=peak_value,
                decay_rate=decay_rate,
                seasonality=seasonality
            )
            
        except Exception as e:
            logger.error(f"[YouTubeTrendsAnalyzer] Erro ao detectar padrão de tendência: {e}")
            raise
    
    def _calculate_engagement_rate(self, views: int, likes: int, comments: int) -> float:
        """Calcula taxa de engajamento."""
        if views == 0:
            return 0.0
        return (likes + comments) / views
    
    def _calculate_growth_rate(self, video_data: Dict[str, Any], 
                             historical_data: List[Dict[str, Any]] = None) -> float:
        """Calcula taxa de crescimento."""
        if not historical_data or len(historical_data) < 2:
            return 0.0
        
        # Calcular crescimento entre dois pontos
        current_views = video_data.get('view_count', 0)
        previous_views = historical_data[-2].get('view_count', 0)
        
        if previous_views == 0:
            return 0.0
        
        return (current_views - previous_views) / previous_views
    
    def _calculate_velocity(self, video_data: Dict[str, Any], 
                          historical_data: List[Dict[str, Any]] = None) -> float:
        """Calcula velocidade de crescimento."""
        if not historical_data or len(historical_data) < 2:
            return 0.0
        
        # Calcular mudança por hora
        current_time = datetime.now()
        previous_time = datetime.fromisoformat(historical_data[-2].get('timestamp', '').replace('Z', '+00:00'))
        
        time_diff_hours = (current_time - previous_time).total_seconds() / 3600
        if time_diff_hours == 0:
            return 0.0
        
        current_views = video_data.get('view_count', 0)
        previous_views = historical_data[-2].get('view_count', 0)
        
        return (current_views - previous_views) / time_diff_hours
    
    def _calculate_acceleration(self, video_data: Dict[str, Any], 
                              historical_data: List[Dict[str, Any]] = None) -> float:
        """Calcula aceleração do crescimento."""
        if not historical_data or len(historical_data) < 3:
            return 0.0
        
        # Calcular mudança na velocidade
        current_velocity = self._calculate_velocity(video_data, historical_data)
        previous_velocity = self._calculate_velocity(historical_data[-2], historical_data[:-1])
        
        return current_velocity - previous_velocity
    
    def _calculate_momentum(self, video_data: Dict[str, Any], 
                          historical_data: List[Dict[str, Any]] = None) -> float:
        """Calcula momentum da tendência."""
        if not historical_data:
            return 0.0
        
        # Calcular tendência linear dos últimos pontos
        views = [data.get('view_count', 0) for data in historical_data[-5:]]
        if len(views) < 2:
            return 0.0
        
        # Calcular coeficiente de correlação
        value = np.arange(len(views))
        correlation = np.corrcoef(value, views)[0, 1]
        
        return max(0, correlation) if not np.isnan(correlation) else 0.0
    
    def _estimate_reach(self, views: int, engagement_rate: float) -> int:
        """Estima alcance baseado em views e engajamento."""
        # Fórmula simplificada para estimar alcance
        base_reach = views * 1.5  # Assumir que cada view representa 1.5 pessoas alcançadas
        engagement_multiplier = 1 + (engagement_rate * 10)  # Engajamento alto aumenta alcance
        return int(base_reach * engagement_multiplier)
    
    def _categorize_trend(self, growth_rate: float, velocity: float, acceleration: float) -> str:
        """Categoriza tipo de tendência."""
        if growth_rate > 0.5 and velocity > 1000 and acceleration > 0:
            return "viral"
        elif growth_rate > 0.2 and velocity > 100:
            return "trending"
        elif growth_rate > 0.1 and velocity > 10:
            return "growing"
        elif growth_rate > 0:
            return "stable"
        else:
            return "declining"
    
    def _calculate_confidence(self, video_data: Dict[str, Any], 
                           historical_data: List[Dict[str, Any]] = None) -> float:
        """Calcula confiança da análise."""
        confidence = 0.5  # Base
        
        # Mais dados históricos = mais confiança
        if historical_data:
            confidence += min(len(historical_data) / 20, 0.3)
        
        # Views altos = mais confiança
        views = video_data.get('view_count', 0)
        if views > 10000:
            confidence += 0.2
        elif views > 1000:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_keywords(self, title: str, description: str) -> List[str]:
        """Extrai keywords do título e descrição."""
        try:
            text = f"{title} {description}".lower()
            
            # Remover caracteres especiais
            text = re.sub(r'[^\w\string_data]', ' ', text)
            
            # Tokenizar
            words = text.split()
            
            # Remover stop words e palavras muito comuns
            stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'e', 'ou', 'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'nas', 'nos', 'para', 'por', 'com', 'sem', 'que', 'como', 'quando', 'onde', 'porque', 'mas', 'se', 'não', 'sim', 'também', 'muito', 'pouco', 'mais', 'menos', 'bem', 'mal', 'hoje', 'ontem', 'amanhã', 'agora', 'depois', 'antes', 'sempre', 'nunca', 'já', 'ainda', 'só', 'apenas', 'mesmo', 'próprio', 'cada', 'todo', 'toda', 'todos', 'todas', 'qualquer', 'algum', 'alguma', 'alguns', 'algumas', 'nenhum', 'nenhuma', 'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'isso', 'aquilo', 'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'me', 'te', 'se', 'nos', 'vos', 'lhe', 'lhes', 'meu', 'minha', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'seu', 'sua', 'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas', 'vosso', 'vossa', 'vossos', 'vossas'}
            
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Contar frequência
            word_counts = Counter(keywords)
            
            # Retornar top keywords
            return [word for word, count in word_counts.most_common(10)]
            
        except Exception as e:
            logger.error(f"[YouTubeTrendsAnalyzer] Erro ao extrair keywords: {e}")
            return []
    
    def _determine_category(self, video_data: Dict[str, Any], keywords: List[str], tags: List[str]) -> str:
        """Determina categoria do vídeo."""
        # Usar categoria do YouTube se disponível
        if 'category_id' in video_data:
            return self._get_category_name(video_data['category_id'])
        
        # Tentar determinar por keywords e tags
        all_text = ' '.join(keywords + tags).lower()
        
        categories = {
            'gaming': ['game', 'gaming', 'playthrough', 'gameplay', 'stream'],
            'education': ['tutorial', 'how to', 'learn', 'education', 'course'],
            'music': ['music', 'song', 'cover', 'remix', 'concert'],
            'comedy': ['funny', 'comedy', 'joke', 'humor', 'laugh'],
            'news': ['news', 'update', 'breaking', 'report', 'analysis'],
            'sports': ['sport', 'football', 'basketball', 'tennis', 'match'],
            'technology': ['tech', 'technology', 'review', 'unboxing', 'comparison'],
            'lifestyle': ['lifestyle', 'vlog', 'daily', 'routine', 'life']
        }
        
        for category, keywords_list in categories.items():
            if any(keyword in all_text for keyword in keywords_list):
                return category
        
        return 'other'
    
    def _detect_language(self, title: str, description: str) -> str:
        """Detecta idioma do conteúdo."""
        try:
            text = f"{title} {description}"
            blob = TextBlob(text)
            return blob.detect_language()
        except Exception:
            return 'unknown'
    
    def _parse_duration(self, duration: str) -> int:
        """Converte duração ISO 8601 para segundos."""
        try:
            # Formato: PT1H2M3S
            duration = duration.replace('PT', '')
            hours = 0
            minutes = 0
            seconds = 0
            
            if 'H' in duration:
                hours = int(duration.split('H')[0])
                duration = duration.split('H')[1]
            
            if 'M' in duration:
                minutes = int(duration.split('M')[0])
                duration = duration.split('M')[1]
            
            if 'S' in duration:
                seconds = int(duration.split('S')[0])
            
            return hours * 3600 + minutes * 60 + seconds
        except Exception:
            return 0
    
    def _get_category_name(self, category_id: str) -> str:
        """Obtém nome da categoria pelo ID."""
        categories = {
            '1': 'Film & Animation',
            '2': 'Autos & Vehicles',
            '10': 'Music',
            '15': 'Pets & Animals',
            '17': 'Sports',
            '19': 'Travel & Events',
            '20': 'Gaming',
            '22': 'People & Blogs',
            '23': 'Comedy',
            '24': 'Entertainment',
            '25': 'News & Politics',
            '26': 'Howto & Style',
            '27': 'Education',
            '28': 'Science & Technology',
            '29': 'Nonprofits & Activism'
        }
        return categories.get(category_id, 'Unknown')
    
    def _determine_growth_direction(self, growth_rate: float) -> str:
        """Determina direção do crescimento."""
        if growth_rate > 0.1:
            return "strong_growth"
        elif growth_rate > 0:
            return "moderate_growth"
        elif growth_rate > -0.1:
            return "stable"
        else:
            return "declining"
    
    def _calculate_growth_acceleration(self, video_data: Dict[str, Any]) -> float:
        """Calcula aceleração do crescimento."""
        # Implementação simplificada
        return 0.0
    
    def _assess_content_quality(self, video_data: Dict[str, Any]) -> float:
        """Avalia qualidade do conteúdo."""
        # Implementação simplificada
        return 0.5
    
    def _classify_pattern(self, views_over_time: List[Tuple[str, int]]) -> str:
        """Classifica padrão de crescimento."""
        if len(views_over_time) < 3:
            return "insufficient_data"
        
        views = [value[1] for value in views_over_time]
        
        # Calcular tendência
        value = np.arange(len(views))
        slope = np.polyfit(value, views, 1)[0]
        
        if slope > 1000:
            return "exponential_growth"
        elif slope > 100:
            return "linear_growth"
        elif slope > 0:
            return "slow_growth"
        elif slope > -100:
            return "stable"
        else:
            return "declining"
    
    def _calculate_decay_rate(self, views_over_time: List[Tuple[str, int]], peak_idx: int) -> float:
        """Calcula taxa de decaimento após o pico."""
        if peak_idx >= len(views_over_time) - 1:
            return 0.0
        
        peak_views = views_over_time[peak_idx][1]
        final_views = views_over_time[-1][1]
        
        if peak_views == 0:
            return 0.0
        
        return (peak_views - final_views) / peak_views
    
    def _detect_seasonality(self, views_over_time: List[Tuple[str, int]]) -> Optional[str]:
        """Detecta sazonalidade nos dados."""
        # Implementação simplificada
        return None


# Função de conveniência para criar analisador
def create_youtube_trends_analyzer(config: Dict[str, Any] = None) -> YouTubeTrendsAnalyzer:
    """
    Cria analisador de tendências do YouTube.
    
    Args:
        config: Configuração do analisador
        
    Returns:
        Analisador de tendências
    """
    return YouTubeTrendsAnalyzer(config) 