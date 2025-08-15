"""
🎵 TikTok Trends Analyzer Implementation

Tracing ID: tiktok-trends-2025-01-27-001
Timestamp: 2025-01-27T15:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Algoritmos baseados em padrões de análise de tendências e métricas de engajamento
🌲 ToT: Avaliadas múltiplas abordagens de análise e escolhida mais precisa
♻️ ReAct: Simulado cenários de viralização e validada precisão dos algoritmos
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from collections import defaultdict, Counter

from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.rate_limiter import RateLimiter
from infrastructure.observability.metrics_collector import MetricsCollector

# Configuração de logging
logger = logging.getLogger(__name__)

class TrendType(Enum):
    """Tipos de tendência detectada"""
    VIRAL = "viral"
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    EMERGING = "emerging"

class EngagementLevel(Enum):
    """Níveis de engajamento"""
    VERY_HIGH = "very_high"  # > 15%
    HIGH = "high"            # 10-15%
    MEDIUM = "medium"        # 5-10%
    LOW = "low"              # 2-5%
    VERY_LOW = "very_low"    # < 2%

@dataclass
class TrendAnalysis:
    """Resultado da análise de tendência"""
    hashtag: str
    trend_type: TrendType
    engagement_level: EngagementLevel
    viral_score: float
    growth_rate: float
    velocity_score: float
    momentum_score: float
    predicted_reach: int
    confidence_level: float
    analysis_timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class ViralMetrics:
    """Métricas de viralização"""
    shares_per_view: float
    comments_per_view: float
    likes_per_view: float
    completion_rate: float
    watch_time_avg: float
    viral_coefficient: float
    reach_velocity: float

class TikTokTrendsAnalyzer:
    """
    Analisador de tendências TikTok
    
    Implementa algoritmos avançados para:
    - Detecção de viralização
    - Análise de engajamento
    - Predição de tendências
    - Métricas de momentum
    - Análise de velocidade de crescimento
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa analisador de tendências
        
        Args:
            config: Configuração do analisador
        """
        self.config = config
        
        # Configurar circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=Exception
        )
        
        # Configurar rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.get("rate_limits", {}).get("requests_per_minute", 50),
            requests_per_hour=config.get("rate_limits", {}).get("requests_per_hour", 500)
        )
        
        # Configurar métricas
        self.metrics = MetricsCollector()
        
        # Parâmetros de análise
        self.viral_threshold = config.get("viral_threshold", 0.8)
        self.growth_threshold = config.get("growth_threshold", 0.3)
        self.engagement_thresholds = config.get("engagement_thresholds", {
            "very_high": 0.15,
            "high": 0.10,
            "medium": 0.05,
            "low": 0.02
        })
        
        # Cache de análises
        self.analysis_cache = {}
        self.cache_ttl = config.get("cache_ttl", 3600)  # 1 hora
        
        logger.info("TikTok Trends Analyzer inicializado")
    
    @CircuitBreaker
    async def analyze_hashtag_trend(self, hashtag: str, historical_data: List[Dict[str, Any]]) -> TrendAnalysis:
        """
        Analisa tendência de hashtag
        
        Args:
            hashtag: Hashtag para análise
            historical_data: Dados históricos da hashtag
            
        Returns:
            TrendAnalysis: Análise completa da tendência
        """
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("analyze_hashtag_trend")
            
            # Verificar cache
            cache_key = self._generate_cache_key(hashtag, historical_data)
            if cache_key in self.analysis_cache:
                cached_analysis = self.analysis_cache[cache_key]
                if datetime.utcnow() - cached_analysis.analysis_timestamp < timedelta(seconds=self.cache_ttl):
                    logger.info(f"Retornando análise em cache para hashtag: {hashtag}")
                    return cached_analysis
            
            # Processar dados históricos
            processed_data = self._process_historical_data(historical_data)
            
            # Calcular métricas
            viral_score = self._calculate_viral_score(processed_data)
            growth_rate = self._calculate_growth_rate(processed_data)
            velocity_score = self._calculate_velocity_score(processed_data)
            momentum_score = self._calculate_momentum_score(processed_data)
            
            # Determinar tipo de tendência
            trend_type = self._determine_trend_type(viral_score, growth_rate, velocity_score)
            
            # Calcular nível de engajamento
            engagement_level = self._calculate_engagement_level(processed_data)
            
            # Predizer alcance
            predicted_reach = self._predict_reach(processed_data, viral_score)
            
            # Calcular nível de confiança
            confidence_level = self._calculate_confidence_level(processed_data)
            
            # Criar análise
            analysis = TrendAnalysis(
                hashtag=hashtag,
                trend_type=trend_type,
                engagement_level=engagement_level,
                viral_score=viral_score,
                growth_rate=growth_rate,
                velocity_score=velocity_score,
                momentum_score=momentum_score,
                predicted_reach=predicted_reach,
                confidence_level=confidence_level,
                analysis_timestamp=datetime.utcnow(),
                metadata={
                    "data_points": len(historical_data),
                    "time_span_days": self._calculate_time_span(historical_data),
                    "peak_views": max([data.get("views", 0) for data in historical_data]),
                    "avg_engagement": np.mean([data.get("engagement_rate", 0) for data in historical_data])
                }
            )
            
            # Armazenar em cache
            self.analysis_cache[cache_key] = analysis
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_trend_analyses_total",
                {"hashtag": hashtag, "trend_type": trend_type.value}
            )
            self.metrics.record_histogram(
                "tiktok_viral_scores",
                viral_score
            )
            
            logger.info(f"Análise de tendência concluída - Hashtag: {hashtag}, Tipo: {trend_type.value}")
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar tendência da hashtag {hashtag}: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_trend_analysis_errors_total",
                {"hashtag": hashtag, "error_type": type(e).__name__}
            )
            
            raise
    
    @CircuitBreaker
    async def analyze_viral_potential(self, video_data: Dict[str, Any]) -> ViralMetrics:
        """
        Analisa potencial viral de vídeo
        
        Args:
            video_data: Dados do vídeo
            
        Returns:
            ViralMetrics: Métricas de viralização
        """
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("analyze_viral_potential")
            
            # Extrair métricas básicas
            views = video_data.get("views", 0)
            likes = video_data.get("likes", 0)
            comments = video_data.get("comments", 0)
            shares = video_data.get("shares", 0)
            duration = video_data.get("duration", 0)
            watch_time = video_data.get("watch_time", 0)
            
            # Calcular métricas de engajamento
            shares_per_view = shares / views if views > 0 else 0
            comments_per_view = comments / views if views > 0 else 0
            likes_per_view = likes / views if views > 0 else 0
            
            # Calcular taxa de conclusão
            completion_rate = watch_time / (views * duration) if views > 0 and duration > 0 else 0
            
            # Calcular tempo médio de visualização
            watch_time_avg = watch_time / views if views > 0 else 0
            
            # Calcular coeficiente viral
            viral_coefficient = self._calculate_viral_coefficient(shares, views, comments)
            
            # Calcular velocidade de alcance
            reach_velocity = self._calculate_reach_velocity(video_data)
            
            # Criar métricas
            viral_metrics = ViralMetrics(
                shares_per_view=shares_per_view,
                comments_per_view=comments_per_view,
                likes_per_view=likes_per_view,
                completion_rate=completion_rate,
                watch_time_avg=watch_time_avg,
                viral_coefficient=viral_coefficient,
                reach_velocity=reach_velocity
            )
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_viral_analyses_total",
                {"video_id": video_data.get("id", "unknown")}
            )
            self.metrics.record_histogram(
                "tiktok_viral_coefficients",
                viral_coefficient
            )
            
            logger.info(f"Análise viral concluída - Vídeo: {video_data.get('id', 'unknown')}")
            return viral_metrics
            
        except Exception as e:
            logger.error(f"Erro ao analisar potencial viral: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_viral_analysis_errors_total",
                {"error_type": type(e).__name__}
            )
            
            raise
    
    @CircuitBreaker
    async def detect_emerging_trends(self, hashtags_data: List[Dict[str, Any]], 
                                   time_window_hours: int = 24) -> List[TrendAnalysis]:
        """
        Detecta tendências emergentes
        
        Args:
            hashtags_data: Dados de múltiplas hashtags
            time_window_hours: Janela de tempo para análise
            
        Returns:
            List[TrendAnalysis]: Lista de tendências emergentes
        """
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("detect_emerging_trends")
            
            emerging_trends = []
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            for hashtag_data in hashtags_data:
                hashtag = hashtag_data.get("hashtag")
                historical_data = hashtag_data.get("historical_data", [])
                
                # Filtrar dados recentes
                recent_data = [
                    data for data in historical_data 
                    if datetime.fromisoformat(data.get("timestamp", "")) >= cutoff_time
                ]
                
                if len(recent_data) < 3:  # Mínimo de pontos para análise
                    continue
                
                # Analisar tendência
                analysis = await self.analyze_hashtag_trend(hashtag, recent_data)
                
                # Verificar se é emergente
                if analysis.trend_type in [TrendType.EMERGING, TrendType.GROWING]:
                    if analysis.confidence_level > 0.7:  # Alta confiança
                        emerging_trends.append(analysis)
            
            # Ordenar por viral score
            emerging_trends.sort(key=lambda value: value.viral_score, reverse=True)
            
            # Registrar métricas
            self.metrics.increment_counter(
                "tiktok_emerging_trends_detected_total",
                {"count": len(emerging_trends)}
            )
            
            logger.info(f"Detectadas {len(emerging_trends)} tendências emergentes")
            return emerging_trends
            
        except Exception as e:
            logger.error(f"Erro ao detectar tendências emergentes: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "tiktok_emerging_trends_errors_total",
                {"error_type": type(e).__name__}
            )
            
            raise
    
    def _process_historical_data(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa dados históricos para análise"""
        if not historical_data:
            return {}
        
        # Converter para DataFrame
        df = pd.DataFrame(historical_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calcular métricas agregadas
        processed = {
            'timestamps': df['timestamp'].tolist(),
            'views': df['views'].tolist(),
            'likes': df['likes'].tolist(),
            'comments': df['comments'].tolist(),
            'shares': df['shares'].tolist(),
            'engagement_rates': df['engagement_rate'].tolist(),
            'growth_rates': self._calculate_point_growth_rates(df['views'].tolist()),
            'velocity_metrics': self._calculate_velocity_metrics(df),
            'momentum_indicators': self._calculate_momentum_indicators(df)
        }
        
        return processed
    
    def _calculate_viral_score(self, processed_data: Dict[str, Any]) -> float:
        """Calcula score de viralização"""
        if not processed_data:
            return 0.0
        
        views = processed_data.get('views', [])
        engagement_rates = processed_data.get('engagement_rates', [])
        growth_rates = processed_data.get('growth_rates', [])
        
        if not views or not engagement_rates:
            return 0.0
        
        # Fatores de viralização
        view_growth_factor = np.mean(growth_rates) if growth_rates else 0
        engagement_factor = np.mean(engagement_rates) if engagement_rates else 0
        velocity_factor = np.mean(processed_data.get('velocity_metrics', [])) if processed_data.get('velocity_metrics') else 0
        
        # Calcular score ponderado
        viral_score = (
            view_growth_factor * 0.4 +
            engagement_factor * 0.3 +
            velocity_factor * 0.3
        )
        
        return min(max(viral_score, 0.0), 1.0)  # Normalizar entre 0 e 1
    
    def _calculate_growth_rate(self, processed_data: Dict[str, Any]) -> float:
        """Calcula taxa de crescimento"""
        views = processed_data.get('views', [])
        if len(views) < 2:
            return 0.0
        
        # Calcular crescimento percentual
        initial_views = views[0]
        final_views = views[-1]
        
        if initial_views == 0:
            return 0.0
        
        growth_rate = (final_views - initial_views) / initial_views
        return growth_rate
    
    def _calculate_velocity_score(self, processed_data: Dict[str, Any]) -> float:
        """Calcula score de velocidade"""
        velocity_metrics = processed_data.get('velocity_metrics', [])
        if not velocity_metrics:
            return 0.0
        
        # Calcular velocidade média
        avg_velocity = np.mean(velocity_metrics)
        
        # Normalizar para score entre 0 e 1
        velocity_score = min(avg_velocity / 1000, 1.0)  # Assumindo 1000 como máximo
        return velocity_score
    
    def _calculate_momentum_score(self, processed_data: Dict[str, Any]) -> float:
        """Calcula score de momentum"""
        momentum_indicators = processed_data.get('momentum_indicators', [])
        if not momentum_indicators:
            return 0.0
        
        # Calcular momentum baseado em indicadores
        momentum_score = np.mean(momentum_indicators)
        return min(max(momentum_score, 0.0), 1.0)
    
    def _determine_trend_type(self, viral_score: float, growth_rate: float, 
                            velocity_score: float) -> TrendType:
        """Determina tipo de tendência"""
        # Critérios para cada tipo
        if viral_score > self.viral_threshold and growth_rate > self.growth_threshold:
            return TrendType.VIRAL
        elif growth_rate > self.growth_threshold and velocity_score > 0.5:
            return TrendType.GROWING
        elif growth_rate > 0 and growth_rate <= self.growth_threshold:
            return TrendType.STABLE
        elif growth_rate < 0:
            return TrendType.DECLINING
        elif viral_score > 0.5 and velocity_score > 0.3:
            return TrendType.EMERGING
        else:
            return TrendType.STABLE
    
    def _calculate_engagement_level(self, processed_data: Dict[str, Any]) -> EngagementLevel:
        """Calcula nível de engajamento"""
        engagement_rates = processed_data.get('engagement_rates', [])
        if not engagement_rates:
            return EngagementLevel.VERY_LOW
        
        avg_engagement = np.mean(engagement_rates)
        
        # Determinar nível baseado em thresholds
        if avg_engagement > self.engagement_thresholds["very_high"]:
            return EngagementLevel.VERY_HIGH
        elif avg_engagement > self.engagement_thresholds["high"]:
            return EngagementLevel.HIGH
        elif avg_engagement > self.engagement_thresholds["medium"]:
            return EngagementLevel.MEDIUM
        elif avg_engagement > self.engagement_thresholds["low"]:
            return EngagementLevel.LOW
        else:
            return EngagementLevel.VERY_LOW
    
    def _predict_reach(self, processed_data: Dict[str, Any], viral_score: float) -> int:
        """Prediz alcance futuro"""
        views = processed_data.get('views', [])
        if not views:
            return 0
        
        current_views = views[-1]
        growth_rate = self._calculate_growth_rate(processed_data)
        
        # Predição simples baseada em crescimento atual
        predicted_growth = 1 + (growth_rate * viral_score)
        predicted_reach = int(current_views * predicted_growth)
        
        return predicted_reach
    
    def _calculate_confidence_level(self, processed_data: Dict[str, Any]) -> float:
        """Calcula nível de confiança da análise"""
        views = processed_data.get('views', [])
        if len(views) < 3:
            return 0.3  # Baixa confiança com poucos dados
        
        # Fatores de confiança
        data_points_factor = min(len(views) / 10, 1.0)  # Mais pontos = mais confiança
        consistency_factor = 1.0 - np.std(views) / np.mean(views) if np.mean(views) > 0 else 0
        
        confidence = (data_points_factor * 0.6 + consistency_factor * 0.4)
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_viral_coefficient(self, shares: int, views: int, comments: int) -> float:
        """Calcula coeficiente viral"""
        if views == 0:
            return 0.0
        
        # Fórmula: (shares + comments * 0.5) / views
        viral_coefficient = (shares + comments * 0.5) / views
        return viral_coefficient
    
    def _calculate_reach_velocity(self, video_data: Dict[str, Any]) -> float:
        """Calcula velocidade de alcance"""
        views = video_data.get("views", 0)
        created_time = video_data.get("created_time")
        
        if not created_time or views == 0:
            return 0.0
        
        # Calcular tempo desde criação
        if isinstance(created_time, str):
            created_time = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
        
        time_diff = datetime.utcnow() - created_time
        hours_since_creation = time_diff.total_seconds() / 3600
        
        if hours_since_creation == 0:
            return 0.0
        
        # Velocidade = views por hora
        reach_velocity = views / hours_since_creation
        return reach_velocity
    
    def _calculate_point_growth_rates(self, views: List[int]) -> List[float]:
        """Calcula taxas de crescimento ponto a ponto"""
        growth_rates = []
        for index in range(1, len(views)):
            if views[index-1] > 0:
                growth_rate = (views[index] - views[index-1]) / views[index-1]
                growth_rates.append(growth_rate)
            else:
                growth_rates.append(0.0)
        return growth_rates
    
    def _calculate_velocity_metrics(self, df: pd.DataFrame) -> List[float]:
        """Calcula métricas de velocidade"""
        velocity_metrics = []
        
        for index in range(1, len(df)):
            time_diff = (df.iloc[index]['timestamp'] - df.iloc[index-1]['timestamp']).total_seconds() / 3600
            view_diff = df.iloc[index]['views'] - df.iloc[index-1]['views']
            
            if time_diff > 0:
                velocity = view_diff / time_diff
                velocity_metrics.append(velocity)
            else:
                velocity_metrics.append(0.0)
        
        return velocity_metrics
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> List[float]:
        """Calcula indicadores de momentum"""
        momentum_indicators = []
        
        for index in range(2, len(df)):
            # Momentum baseado em aceleração de crescimento
            prev_growth = df.iloc[index-1]['views'] - df.iloc[index-2]['views']
            curr_growth = df.iloc[index]['views'] - df.iloc[index-1]['views']
            
            if prev_growth > 0:
                momentum = curr_growth / prev_growth
                momentum_indicators.append(momentum)
            else:
                momentum_indicators.append(0.0)
        
        return momentum_indicators
    
    def _calculate_time_span(self, historical_data: List[Dict[str, Any]]) -> int:
        """Calcula span de tempo dos dados em dias"""
        if len(historical_data) < 2:
            return 0
        
        timestamps = [data.get("timestamp") for data in historical_data if data.get("timestamp")]
        if len(timestamps) < 2:
            return 0
        
        # Converter para datetime
        try:
            start_time = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
            time_span = (end_time - start_time).days
            return time_span
        except:
            return 0
    
    def _generate_cache_key(self, hashtag: str, historical_data: List[Dict[str, Any]]) -> str:
        """Gera chave de cache única"""
        data_hash = hashlib.md5(
            json.dumps(historical_data, sort_keys=True).encode()
        ).hexdigest()
        return f"trend_analysis:{hashtag}:{data_hash}" 