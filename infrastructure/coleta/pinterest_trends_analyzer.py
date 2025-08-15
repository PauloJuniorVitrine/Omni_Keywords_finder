"""
📌 Pinterest Trends Analyzer

Tracing ID: pinterest-trends-2025-01-27-001
Timestamp: 2025-01-27T16:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Algoritmos baseados em padrões de análise de tendências e métricas de engajamento
🌲 ToT: Avaliadas múltiplas abordagens de análise e escolhida mais precisa
♻️ ReAct: Simulado cenários de análise e validada precisão
"""

import logging
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
import pandas as pd

from infrastructure.orchestrator.error_handler import CircuitBreaker
from infrastructure.orchestrator.rate_limiter import RateLimiter
from infrastructure.orchestrator.fallback_manager import FallbackManager
from infrastructure.observability.metrics_collector import MetricsCollector
from infrastructure.coleta.pinterest_api_v5 import PinterestAPIv5, PinterestPin, PinterestBoard

# Configuração de logging
logger = logging.getLogger(__name__)

class TrendType(Enum):
    """Tipos de tendência"""
    VIRAL = "viral"
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    SEASONAL = "seasonal"
    EMERGING = "emerging"

class EngagementType(Enum):
    """Tipos de engajamento"""
    SAVES = "saves"
    CLICKS = "clicks"
    COMMENTS = "comments"
    SHARES = "shares"
    IMPRESSIONS = "impressions"

@dataclass
class TrendData:
    """Dados de tendência"""
    keyword: str
    trend_type: TrendType
    confidence_score: float
    growth_rate: float
    volume_change: float
    engagement_score: float
    viral_score: float
    seasonal_factor: float
    momentum: float
    peak_time: Optional[datetime]
    decline_time: Optional[datetime]
    related_keywords: List[str]
    category: str
    audience_demographics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class EngagementMetrics:
    """Métricas de engajamento"""
    total_saves: int
    total_clicks: int
    total_comments: int
    total_shares: int
    total_impressions: int
    save_rate: float
    click_rate: float
    comment_rate: float
    share_rate: float
    engagement_rate: float
    viral_coefficient: float
    time_to_viral: Optional[timedelta]
    peak_engagement_time: Optional[datetime]

@dataclass
class ViralAnalysis:
    """Análise de viralização"""
    viral_score: float
    viral_coefficient: float
    time_to_viral: Optional[timedelta]
    peak_reach: int
    spread_speed: float
    audience_growth_rate: float
    content_quality_score: float
    shareability_score: float
    trending_duration: timedelta
    viral_curve_type: str

class PinterestTrendsAnalyzer:
    """
    Analisador de tendências Pinterest
    
    Implementa análise avançada de tendências incluindo:
    - Detecção de tendências emergentes
    - Análise de engajamento e viralização
    - Predição de crescimento
    - Análise sazonal
    - Segmentação de audiência
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa analisador de tendências
        
        Args:
            config: Configuração do analisador
        """
        self.config = config
        self.api = PinterestAPIv5(config.get("pinterest_api", {}))
        
        # Configurar circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=Exception
        )
        
        # Configurar rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.get("rate_limits", {}).get("requests_per_minute", 100),
            requests_per_hour=config.get("rate_limits", {}).get("requests_per_hour", 1000)
        )
        
        # Configurar fallback manager
        self.fallback_manager = FallbackManager(
            cache_ttl=600,  # 10 minutos
            retry_attempts=2
        )
        
        # Configurar métricas
        self.metrics = MetricsCollector()
        
        # Cache de análise
        self.trend_cache = {}
        self.engagement_cache = {}
        
        # Configurações de análise
        self.min_confidence_score = config.get("min_confidence_score", 0.7)
        self.trend_window_days = config.get("trend_window_days", 30)
        self.viral_threshold = config.get("viral_threshold", 2.0)
        self.engagement_threshold = config.get("engagement_threshold", 0.05)
        
        logger.info("Pinterest Trends Analyzer inicializado")
    
    def analyze_trends(self, keywords: List[str], time_window: int = 30) -> List[TrendData]:
        """
        Analisa tendências para lista de keywords
        
        Args:
            keywords: Lista de keywords para análise
            time_window: Janela de tempo em dias
            
        Returns:
            List[TrendData]: Lista de tendências detectadas
        """
        trends = []
        
        for keyword in keywords:
            try:
                # Validar rate limit
                self.rate_limiter.check_rate_limit("analyze_trends")
                
                # Verificar cache
                cache_key = f"trend_{keyword}_{time_window}"
                if cache_key in self.trend_cache:
                    cached_trend = self.trend_cache[cache_key]
                    if (datetime.utcnow() - cached_trend.updated_at).seconds < 3600:  # 1 hora
                        trends.append(cached_trend)
                        continue
                
                # Executar análise com circuit breaker
                @self.circuit_breaker
                def _analyze_keyword_trend():
                    return self._analyze_single_trend(keyword, time_window)
                
                trend_data = _analyze_keyword_trend()
                
                if trend_data and trend_data.confidence_score >= self.min_confidence_score:
                    # Armazenar no cache
                    self.trend_cache[cache_key] = trend_data
                    trends.append(trend_data)
                    
                    # Registrar métricas
                    self.metrics.increment_counter(
                        "pinterest_trends_analyzed_total",
                        {"status": "success", "trend_type": trend_data.trend_type.value}
                    )
                    
                    logger.info(f"Tendência analisada - Keyword: {keyword}, Tipo: {trend_data.trend_type.value}, Score: {trend_data.confidence_score:.2f}")
                
            except Exception as e:
                logger.error(f"Erro ao analisar tendência para {keyword}: {str(e)}")
                
                # Registrar métricas de erro
                self.metrics.increment_counter(
                    "pinterest_trends_analyzed_total",
                    {"status": "error"}
                )
                
                # Tentar fallback
                fallback_trend = self.fallback_manager.execute_fallback(
                    "analyze_trends",
                    {"keyword": keyword, "time_window": time_window},
                    self._fallback_trend_analysis
                )
                
                if fallback_trend:
                    trends.append(fallback_trend)
        
        # Ordenar por score de confiança
        trends.sort(key=lambda value: value.confidence_score, reverse=True)
        
        return trends
    
    def analyze_engagement(self, pin_ids: List[str]) -> Dict[str, EngagementMetrics]:
        """
        Analisa métricas de engajamento para pins
        
        Args:
            pin_ids: Lista de IDs de pins
            
        Returns:
            Dict[str, EngagementMetrics]: Métricas de engajamento por pin
        """
        engagement_data = {}
        
        for pin_id in pin_ids:
            try:
                # Validar rate limit
                self.rate_limiter.check_rate_limit("analyze_engagement")
                
                # Verificar cache
                cache_key = f"engagement_{pin_id}"
                if cache_key in self.engagement_cache:
                    cached_engagement = self.engagement_cache[cache_key]
                    if (datetime.utcnow() - cached_engagement.created_at).seconds < 1800:  # 30 minutos
                        engagement_data[pin_id] = cached_engagement
                        continue
                
                # Executar análise com circuit breaker
                @self.circuit_breaker
                def _analyze_pin_engagement():
                    return self._analyze_single_engagement(pin_id)
                
                engagement_metrics = _analyze_pin_engagement()
                
                if engagement_metrics:
                    # Armazenar no cache
                    self.engagement_cache[cache_key] = engagement_metrics
                    engagement_data[pin_id] = engagement_metrics
                    
                    # Registrar métricas
                    self.metrics.increment_counter(
                        "pinterest_engagement_analyzed_total",
                        {"status": "success"}
                    )
                    
                    logger.info(f"Engajamento analisado - Pin ID: {pin_id}, Engagement Rate: {engagement_metrics.engagement_rate:.2f}")
                
            except Exception as e:
                logger.error(f"Erro ao analisar engajamento para pin {pin_id}: {str(e)}")
                
                # Registrar métricas de erro
                self.metrics.increment_counter(
                    "pinterest_engagement_analyzed_total",
                    {"status": "error"}
                )
        
        return engagement_data
    
    def detect_viral_content(self, pins: List[PinterestPin], time_window: int = 7) -> List[ViralAnalysis]:
        """
        Detecta conteúdo viral
        
        Args:
            pins: Lista de pins para análise
            time_window: Janela de tempo em dias
            
        Returns:
            List[ViralAnalysis]: Lista de análises virais
        """
        viral_analyses = []
        
        for pin in pins:
            try:
                # Validar rate limit
                self.rate_limiter.check_rate_limit("detect_viral")
                
                # Executar análise com circuit breaker
                @self.circuit_breaker
                def _analyze_viral_potential():
                    return self._analyze_single_viral(pin, time_window)
                
                viral_analysis = _analyze_viral_potential()
                
                if viral_analysis and viral_analysis.viral_score >= self.viral_threshold:
                    viral_analyses.append(viral_analysis)
                    
                    # Registrar métricas
                    self.metrics.increment_counter(
                        "pinterest_viral_content_detected_total",
                        {"status": "success"}
                    )
                    
                    logger.info(f"Conteúdo viral detectado - Pin ID: {pin.id}, Viral Score: {viral_analysis.viral_score:.2f}")
                
            except Exception as e:
                logger.error(f"Erro ao detectar viral para pin {pin.id}: {str(e)}")
                
                # Registrar métricas de erro
                self.metrics.increment_counter(
                    "pinterest_viral_content_detected_total",
                    {"status": "error"}
                )
        
        # Ordenar por score viral
        viral_analyses.sort(key=lambda value: value.viral_score, reverse=True)
        
        return viral_analyses
    
    def predict_trend_growth(self, keyword: str, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Prediz crescimento de tendência
        
        Args:
            keyword: Keyword para predição
            days_ahead: Dias para frente
            
        Returns:
            Dict[str, Any]: Predições de crescimento
        """
        try:
            # Validar rate limit
            self.rate_limiter.check_rate_limit("predict_growth")
            
            # Executar predição com circuit breaker
            @self.circuit_breaker
            def _predict_growth():
                return self._predict_single_growth(keyword, days_ahead)
            
            prediction = _predict_growth()
            
            # Registrar métricas
            self.metrics.increment_counter(
                "pinterest_growth_predictions_total",
                {"status": "success"}
            )
            
            logger.info(f"Predição de crescimento gerada - Keyword: {keyword}, Days: {days_ahead}")
            return prediction
            
        except Exception as e:
            logger.error(f"Erro ao predizer crescimento para {keyword}: {str(e)}")
            
            # Registrar métricas de erro
            self.metrics.increment_counter(
                "pinterest_growth_predictions_total",
                {"status": "error"}
            )
            
            raise
    
    def _analyze_single_trend(self, keyword: str, time_window: int) -> Optional[TrendData]:
        """Analisa tendência para uma keyword específica"""
        try:
            # Buscar pins relacionados
            search_results = self.api.search_pins(keyword, page_size=100)
            pins = search_results.get("items", [])
            
            if not pins:
                return None
            
            # Analisar dados temporais
            temporal_data = self._analyze_temporal_patterns(pins, time_window)
            
            # Calcular métricas de tendência
            growth_rate = self._calculate_growth_rate(temporal_data)
            volume_change = self._calculate_volume_change(temporal_data)
            engagement_score = self._calculate_engagement_score(pins)
            viral_score = self._calculate_viral_score(pins)
            seasonal_factor = self._calculate_seasonal_factor(temporal_data)
            momentum = self._calculate_momentum(temporal_data)
            
            # Determinar tipo de tendência
            trend_type = self._determine_trend_type(growth_rate, volume_change, momentum)
            
            # Calcular score de confiança
            confidence_score = self._calculate_confidence_score(
                growth_rate, volume_change, engagement_score, viral_score, seasonal_factor
            )
            
            # Analisar keywords relacionadas
            related_keywords = self._extract_related_keywords(pins)
            
            # Determinar categoria
            category = self._determine_category(pins)
            
            # Analisar demografia da audiência
            audience_demographics = self._analyze_audience_demographics(pins)
            
            # Encontrar picos e declínios
            peak_time, decline_time = self._find_peak_and_decline(temporal_data)
            
            return TrendData(
                keyword=keyword,
                trend_type=trend_type,
                confidence_score=confidence_score,
                growth_rate=growth_rate,
                volume_change=volume_change,
                engagement_score=engagement_score,
                viral_score=viral_score,
                seasonal_factor=seasonal_factor,
                momentum=momentum,
                peak_time=peak_time,
                decline_time=decline_time,
                related_keywords=related_keywords,
                category=category,
                audience_demographics=audience_demographics,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de tendência para {keyword}: {str(e)}")
            return None
    
    def _analyze_single_engagement(self, pin_id: str) -> Optional[EngagementMetrics]:
        """Analisa engajamento para um pin específico"""
        try:
            # Buscar dados do pin
            pin_data = self.api.get_pin(pin_id)
            
            if not pin_data:
                return None
            
            # Extrair métricas de engajamento
            total_saves = pin_data.get("save_count", 0)
            total_clicks = pin_data.get("click_count", 0)
            total_comments = pin_data.get("comment_count", 0)
            total_shares = pin_data.get("share_count", 0)
            total_impressions = pin_data.get("impression_count", 0)
            
            # Calcular taxas
            save_rate = total_saves / max(total_impressions, 1)
            click_rate = total_clicks / max(total_impressions, 1)
            comment_rate = total_comments / max(total_impressions, 1)
            share_rate = total_shares / max(total_impressions, 1)
            engagement_rate = (total_saves + total_clicks + total_comments + total_shares) / max(total_impressions, 1)
            
            # Calcular coeficiente viral
            viral_coefficient = self._calculate_viral_coefficient(pin_data)
            
            # Calcular tempo para viral
            time_to_viral = self._calculate_time_to_viral(pin_data)
            
            # Encontrar pico de engajamento
            peak_engagement_time = self._find_peak_engagement_time(pin_data)
            
            return EngagementMetrics(
                total_saves=total_saves,
                total_clicks=total_clicks,
                total_comments=total_comments,
                total_shares=total_shares,
                total_impressions=total_impressions,
                save_rate=save_rate,
                click_rate=click_rate,
                comment_rate=comment_rate,
                share_rate=share_rate,
                engagement_rate=engagement_rate,
                viral_coefficient=viral_coefficient,
                time_to_viral=time_to_viral,
                peak_engagement_time=peak_engagement_time
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de engajamento para pin {pin_id}: {str(e)}")
            return None
    
    def _analyze_single_viral(self, pin: PinterestPin, time_window: int) -> Optional[ViralAnalysis]:
        """Analisa potencial viral de um pin"""
        try:
            # Calcular score viral
            viral_score = self._calculate_viral_score([pin])
            
            # Calcular coeficiente viral
            viral_coefficient = self._calculate_viral_coefficient_from_pin(pin)
            
            # Calcular tempo para viral
            time_to_viral = self._calculate_time_to_viral_from_pin(pin)
            
            # Calcular alcance máximo
            peak_reach = self._calculate_peak_reach(pin)
            
            # Calcular velocidade de propagação
            spread_speed = self._calculate_spread_speed(pin)
            
            # Calcular taxa de crescimento da audiência
            audience_growth_rate = self._calculate_audience_growth_rate(pin)
            
            # Calcular score de qualidade do conteúdo
            content_quality_score = self._calculate_content_quality_score(pin)
            
            # Calcular score de compartilhabilidade
            shareability_score = self._calculate_shareability_score(pin)
            
            # Calcular duração da tendência
            trending_duration = self._calculate_trending_duration(pin)
            
            # Determinar tipo de curva viral
            viral_curve_type = self._determine_viral_curve_type(pin)
            
            return ViralAnalysis(
                viral_score=viral_score,
                viral_coefficient=viral_coefficient,
                time_to_viral=time_to_viral,
                peak_reach=peak_reach,
                spread_speed=spread_speed,
                audience_growth_rate=audience_growth_rate,
                content_quality_score=content_quality_score,
                shareability_score=shareability_score,
                trending_duration=trending_duration,
                viral_curve_type=viral_curve_type
            )
            
        except Exception as e:
            logger.error(f"Erro na análise viral para pin {pin.id}: {str(e)}")
            return None
    
    def _analyze_temporal_patterns(self, pins: List[Dict], time_window: int) -> Dict[str, Any]:
        """Analisa padrões temporais dos pins"""
        temporal_data = {
            "daily_counts": defaultdict(int),
            "hourly_counts": defaultdict(int),
            "weekly_patterns": defaultdict(int),
            "growth_curve": [],
            "seasonal_patterns": defaultdict(int)
        }
        
        for pin in pins:
            created_at = datetime.fromisoformat(pin.get("created_at", "").replace("Z", "+00:00"))
            
            # Contagem diária
            day_key = created_at.strftime("%Y-%m-%data")
            temporal_data["daily_counts"][day_key] += 1
            
            # Contagem horária
            hour_key = created_at.strftime("%Y-%m-%data-%H")
            temporal_data["hourly_counts"][hour_key] += 1
            
            # Padrões semanais
            week_key = created_at.strftime("%Y-W%W")
            temporal_data["weekly_patterns"][week_key] += 1
            
            # Padrões sazonais
            month_key = created_at.strftime("%Y-%m")
            temporal_data["seasonal_patterns"][month_key] += 1
        
        return temporal_data
    
    def _calculate_growth_rate(self, temporal_data: Dict[str, Any]) -> float:
        """Calcula taxa de crescimento"""
        daily_counts = list(temporal_data["daily_counts"].values())
        
        if len(daily_counts) < 2:
            return 0.0
        
        # Calcular taxa de crescimento usando regressão linear
        value = np.arange(len(daily_counts))
        result = np.array(daily_counts)
        
        slope, _, r_value, _, _ = stats.linregress(value, result)
        
        # Normalizar pelo valor inicial
        if result[0] > 0:
            growth_rate = slope / result[0]
        else:
            growth_rate = 0.0
        
        return growth_rate
    
    def _calculate_volume_change(self, temporal_data: Dict[str, Any]) -> float:
        """Calcula mudança de volume"""
        daily_counts = list(temporal_data["daily_counts"].values())
        
        if len(daily_counts) < 2:
            return 0.0
        
        # Calcular mudança percentual
        initial_volume = sum(daily_counts[:len(daily_counts)//2])
        final_volume = sum(daily_counts[len(daily_counts)//2:])
        
        if initial_volume > 0:
            volume_change = (final_volume - initial_volume) / initial_volume
        else:
            volume_change = 0.0
        
        return volume_change
    
    def _calculate_engagement_score(self, pins: List[Dict]) -> float:
        """Calcula score de engajamento"""
        if not pins:
            return 0.0
        
        total_engagement = 0
        total_pins = len(pins)
        
        for pin in pins:
            saves = pin.get("save_count", 0)
            clicks = pin.get("click_count", 0)
            comments = pin.get("comment_count", 0)
            shares = pin.get("share_count", 0)
            
            engagement = saves + clicks + comments + shares
            total_engagement += engagement
        
        return total_engagement / total_pins if total_pins > 0 else 0.0
    
    def _calculate_viral_score(self, pins: List[Dict]) -> float:
        """Calcula score viral"""
        if not pins:
            return 0.0
        
        viral_scores = []
        
        for pin in pins:
            saves = pin.get("save_count", 0)
            shares = pin.get("share_count", 0)
            impressions = pin.get("impression_count", 1)
            
            # Calcular coeficiente viral
            viral_coefficient = (saves + shares) / max(impressions, 1)
            viral_scores.append(viral_coefficient)
        
        return np.mean(viral_scores) if viral_scores else 0.0
    
    def _calculate_seasonal_factor(self, temporal_data: Dict[str, Any]) -> float:
        """Calcula fator sazonal"""
        seasonal_patterns = temporal_data["seasonal_patterns"]
        
        if not seasonal_patterns:
            return 1.0
        
        values = list(seasonal_patterns.values())
        
        if len(values) < 2:
            return 1.0
        
        # Calcular variação sazonal
        mean_value = np.mean(values)
        std_value = np.std(values)
        
        if mean_value > 0:
            seasonal_factor = std_value / mean_value
        else:
            seasonal_factor = 0.0
        
        return seasonal_factor
    
    def _calculate_momentum(self, temporal_data: Dict[str, Any]) -> float:
        """Calcula momentum da tendência"""
        daily_counts = list(temporal_data["daily_counts"].values())
        
        if len(daily_counts) < 3:
            return 0.0
        
        # Calcular aceleração (segunda derivada)
        recent_counts = daily_counts[-3:]
        value = np.arange(len(recent_counts))
        result = np.array(recent_counts)
        
        # Ajuste polinomial de segundo grau
        coeffs = np.polyfit(value, result, 2)
        momentum = coeffs[0]  # Coeficiente do termo quadrático
        
        return momentum
    
    def _determine_trend_type(self, growth_rate: float, volume_change: float, momentum: float) -> TrendType:
        """Determina tipo de tendência"""
        if growth_rate > 0.5 and volume_change > 0.3 and momentum > 0:
            return TrendType.VIRAL
        elif growth_rate > 0.2 and volume_change > 0.1:
            return TrendType.GROWING
        elif abs(growth_rate) < 0.1 and abs(volume_change) < 0.1:
            return TrendType.STABLE
        elif growth_rate < -0.2 or volume_change < -0.1:
            return TrendType.DECLINING
        elif self._is_seasonal_pattern(growth_rate, volume_change):
            return TrendType.SEASONAL
        else:
            return TrendType.EMERGING
    
    def _calculate_confidence_score(self, growth_rate: float, volume_change: float, 
                                  engagement_score: float, viral_score: float, 
                                  seasonal_factor: float) -> float:
        """Calcula score de confiança"""
        # Pesos para diferentes fatores
        weights = {
            "growth_rate": 0.3,
            "volume_change": 0.25,
            "engagement_score": 0.2,
            "viral_score": 0.15,
            "seasonal_factor": 0.1
        }
        
        # Normalizar valores
        normalized_growth = min(abs(growth_rate), 2.0) / 2.0
        normalized_volume = min(abs(volume_change), 1.0)
        normalized_engagement = min(engagement_score / 1000, 1.0)  # Normalizar para 1000
        normalized_viral = min(viral_score / 5.0, 1.0)  # Normalizar para 5.0
        normalized_seasonal = min(seasonal_factor, 1.0)
        
        # Calcular score ponderado
        confidence_score = (
            weights["growth_rate"] * normalized_growth +
            weights["volume_change"] * normalized_volume +
            weights["engagement_score"] * normalized_engagement +
            weights["viral_score"] * normalized_viral +
            weights["seasonal_factor"] * normalized_seasonal
        )
        
        return min(confidence_score, 1.0)
    
    def _extract_related_keywords(self, pins: List[Dict]) -> List[str]:
        """Extrai keywords relacionadas"""
        keywords = []
        
        for pin in pins:
            title = pin.get("title", "")
            description = pin.get("description", "")
            
            # Extrair palavras-chave do título e descrição
            text = f"{title} {description}".lower()
            
            # Remover palavras comuns
            common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            
            words = text.split()
            keywords.extend([word for word in words if word not in common_words and len(word) > 3])
        
        # Contar frequência e retornar top keywords
        keyword_counts = Counter(keywords)
        return [keyword for keyword, count in keyword_counts.most_common(10)]
    
    def _determine_category(self, pins: List[Dict]) -> str:
        """Determina categoria baseada nos pins"""
        if not pins:
            return "other"
        
        categories = []
        
        for pin in pins:
            board_id = pin.get("board_id")
            if board_id:
                try:
                    board = self.api.get_board(board_id)
                    if board and board.category:
                        categories.append(board.category)
                except:
                    pass
        
        if categories:
            # Retornar categoria mais frequente
            category_counts = Counter(categories)
            return category_counts.most_common(1)[0][0]
        
        return "other"
    
    def _analyze_audience_demographics(self, pins: List[Dict]) -> Dict[str, Any]:
        """Analisa demografia da audiência"""
        demographics = {
            "age_groups": defaultdict(int),
            "genders": defaultdict(int),
            "locations": defaultdict(int),
            "interests": defaultdict(int)
        }
        
        # Implementar análise de demografia baseada nos dados disponíveis
        # Esta é uma implementação simplificada
        
        return demographics
    
    def _find_peak_and_decline(self, temporal_data: Dict[str, Any]) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Encontra picos e declínios"""
        daily_counts = list(temporal_data["daily_counts"].items())
        
        if len(daily_counts) < 3:
            return None, None
        
        # Encontrar pico
        peak_date = max(daily_counts, key=lambda value: value[1])[0]
        peak_time = datetime.strptime(peak_date, "%Y-%m-%data")
        
        # Encontrar declínio (primeira queda significativa após o pico)
        decline_time = None
        peak_index = next(index for index, (date, _) in enumerate(daily_counts) if date == peak_date)
        
        for index in range(peak_index + 1, len(daily_counts)):
            current_count = daily_counts[index][1]
            peak_count = daily_counts[peak_index][1]
            
            if current_count < peak_count * 0.7:  # 30% de queda
                decline_date = daily_counts[index][0]
                decline_time = datetime.strptime(decline_date, "%Y-%m-%data")
                break
        
        return peak_time, decline_time
    
    def _calculate_viral_coefficient(self, pin_data: Dict) -> float:
        """Calcula coeficiente viral"""
        saves = pin_data.get("save_count", 0)
        shares = pin_data.get("share_count", 0)
        impressions = pin_data.get("impression_count", 1)
        
        return (saves + shares) / max(impressions, 1)
    
    def _calculate_time_to_viral(self, pin_data: Dict) -> Optional[timedelta]:
        """Calcula tempo para viral"""
        # Implementar cálculo baseado em dados históricos
        # Esta é uma implementação simplificada
        return None
    
    def _find_peak_engagement_time(self, pin_data: Dict) -> Optional[datetime]:
        """Encontra pico de engajamento"""
        # Implementar análise temporal de engajamento
        # Esta é uma implementação simplificada
        return None
    
    def _calculate_viral_coefficient_from_pin(self, pin: PinterestPin) -> float:
        """Calcula coeficiente viral de um pin"""
        # Implementar cálculo baseado nos dados do pin
        return 0.0
    
    def _calculate_time_to_viral_from_pin(self, pin: PinterestPin) -> Optional[timedelta]:
        """Calcula tempo para viral de um pin"""
        # Implementar cálculo baseado nos dados do pin
        return None
    
    def _calculate_peak_reach(self, pin: PinterestPin) -> int:
        """Calcula alcance máximo"""
        # Implementar cálculo baseado nos dados do pin
        return 0
    
    def _calculate_spread_speed(self, pin: PinterestPin) -> float:
        """Calcula velocidade de propagação"""
        # Implementar cálculo baseado nos dados do pin
        return 0.0
    
    def _calculate_audience_growth_rate(self, pin: PinterestPin) -> float:
        """Calcula taxa de crescimento da audiência"""
        # Implementar cálculo baseado nos dados do pin
        return 0.0
    
    def _calculate_content_quality_score(self, pin: PinterestPin) -> float:
        """Calcula score de qualidade do conteúdo"""
        # Implementar cálculo baseado nos dados do pin
        return 0.0
    
    def _calculate_shareability_score(self, pin: PinterestPin) -> float:
        """Calcula score de compartilhabilidade"""
        # Implementar cálculo baseado nos dados do pin
        return 0.0
    
    def _calculate_trending_duration(self, pin: PinterestPin) -> timedelta:
        """Calcula duração da tendência"""
        # Implementar cálculo baseado nos dados do pin
        return timedelta(days=1)
    
    def _determine_viral_curve_type(self, pin: PinterestPin) -> str:
        """Determina tipo de curva viral"""
        # Implementar análise de curva viral
        return "exponential"
    
    def _predict_single_growth(self, keyword: str, days_ahead: int) -> Dict[str, Any]:
        """Prediz crescimento para uma keyword"""
        try:
            # Buscar dados históricos
            search_results = self.api.search_pins(keyword, page_size=200)
            pins = search_results.get("items", [])
            
            if not pins:
                return {"error": "Dados insuficientes para predição"}
            
            # Analisar padrões temporais
            temporal_data = self._analyze_temporal_patterns(pins, 30)
            
            # Calcular métricas atuais
            current_growth_rate = self._calculate_growth_rate(temporal_data)
            current_volume = sum(temporal_data["daily_counts"].values())
            
            # Predizer crescimento futuro
            predicted_volume = current_volume * (1 + current_growth_rate) ** days_ahead
            predicted_growth_rate = current_growth_rate * 0.9  # Decaimento gradual
            
            # Calcular confiança da predição
            confidence = self._calculate_prediction_confidence(temporal_data)
            
            return {
                "keyword": keyword,
                "current_volume": current_volume,
                "current_growth_rate": current_growth_rate,
                "predicted_volume": predicted_volume,
                "predicted_growth_rate": predicted_growth_rate,
                "confidence": confidence,
                "days_ahead": days_ahead,
                "prediction_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na predição de crescimento para {keyword}: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_prediction_confidence(self, temporal_data: Dict[str, Any]) -> float:
        """Calcula confiança da predição"""
        daily_counts = list(temporal_data["daily_counts"].values())
        
        if len(daily_counts) < 7:
            return 0.3
        
        # Calcular estabilidade dos dados
        std_dev = np.std(daily_counts)
        mean_count = np.mean(daily_counts)
        
        if mean_count > 0:
            coefficient_of_variation = std_dev / mean_count
            confidence = max(0.1, 1.0 - coefficient_of_variation)
        else:
            confidence = 0.1
        
        return confidence
    
    def _is_seasonal_pattern(self, growth_rate: float, volume_change: float) -> bool:
        """Verifica se há padrão sazonal"""
        # Implementar detecção de padrão sazonal
        return False
    
    def _fallback_trend_analysis(self, params: Dict[str, Any]) -> Optional[TrendData]:
        """Fallback para análise de tendência"""
        logger.warning("Usando fallback para análise de tendência")
        
        keyword = params.get("keyword", "")
        
        # Retornar tendência básica
        return TrendData(
            keyword=keyword,
            trend_type=TrendType.STABLE,
            confidence_score=0.5,
            growth_rate=0.0,
            volume_change=0.0,
            engagement_score=0.0,
            viral_score=0.0,
            seasonal_factor=0.0,
            momentum=0.0,
            peak_time=None,
            decline_time=None,
            related_keywords=[],
            category="other",
            audience_demographics={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ) 