"""
🎯 Sistema de Predição de Tendências - Omni Keywords Finder
📊 Análise preditiva de keywords e tendências de mercado
🔄 Versão: 1.0
📅 Data: 2024-12-19
👤 Autor: Paulo Júnior
🔗 Tracing ID: PREDICTION_20241219_001
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import warnings
from pathlib import Path

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Time Series
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    warnings.warn("Prophet não disponível. Usando métodos alternativos.")

# Observability
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Direção da tendência predita"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


class ConfidenceLevel(Enum):
    """Nível de confiança da predição"""
    HIGH = "high"      # > 80%
    MEDIUM = "medium"  # 60-80%
    LOW = "low"        # < 60%


@dataclass
class TrendPrediction:
    """Resultado de predição de tendência"""
    keyword: str
    current_value: float
    predicted_value: float
    confidence: float
    direction: TrendDirection
    confidence_level: ConfidenceLevel
    timeframe: str
    factors: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TrendAlert:
    """Alerta de tendência detectada"""
    keyword: str
    alert_type: str
    severity: str
    message: str
    predicted_value: float
    threshold: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrendPredictor:
    """
    🎯 Sistema Principal de Predição de Tendências
    
    Características:
    - Análise de séries temporais com Prophet
    - ML tradicional com ensemble methods
    - Detecção de sazonalidade e tendências
    - Alertas inteligentes baseados em thresholds
    - Métricas de confiança e acurácia
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o preditor de tendências
        
        Args:
            config: Configurações do sistema
        """
        self.config = config or self._default_config()
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
        
        # Modelos
        self.prophet_model = None
        self.ml_model = None
        self.scaler = StandardScaler()
        
        # Cache e estado
        self.predictions_cache = {}
        self.alerts_history = []
        self.model_performance = {}
        
        # Configurações
        self.min_data_points = self.config.get('min_data_points', 30)
        self.prediction_horizon = self.config.get('prediction_horizon', 30)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.6)
        
        logger.info(f"🎯 TrendPredictor inicializado com config: {self.config}")
    
    def _default_config(self) -> Dict:
        """Configuração padrão do sistema"""
        return {
            'min_data_points': 30,
            'prediction_horizon': 30,
            'confidence_threshold': 0.6,
            'alert_thresholds': {
                'high_rise': 0.3,    # 30% de aumento
                'high_fall': -0.3,   # 30% de queda
                'moderate_rise': 0.15,
                'moderate_fall': -0.15
            },
            'seasonality': {
                'yearly': True,
                'weekly': True,
                'daily': False
            },
            'ml_models': ['random_forest', 'gradient_boosting'],
            'cross_validation_folds': 5,
            'cache_ttl': 3600  # 1 hora
        }
    
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados para análise
        
        Args:
            data: DataFrame com colunas ['date', 'keyword', 'value']
            
        Returns:
            DataFrame preparado
        """
        with self.tracing.start_span("prepare_data"):
            try:
                # Validação básica
                required_cols = ['date', 'keyword', 'value']
                if not all(col in data.columns for col in required_cols):
                    raise ValueError(f"Colunas obrigatórias: {required_cols}")
                
                # Limpeza
                data = data.copy()
                data['date'] = pd.to_datetime(data['date'])
                data = data.sort_values(['keyword', 'date'])
                
                # Remove outliers (método IQR)
                for keyword in data['keyword'].unique():
                    keyword_data = data[data['keyword'] == keyword]
                    Q1 = keyword_data['value'].quantile(0.25)
                    Q3 = keyword_data['value'].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outlier_mask = (keyword_data['value'] < lower_bound) | (keyword_data['value'] > upper_bound)
                    data = data[~((data['keyword'] == keyword) & outlier_mask)]
                
                # Interpolação de valores faltantes
                data = data.groupby('keyword').apply(
                    lambda value: value.set_index('date').resample('D').interpolate(method='linear')
                ).reset_index()
                
                # Features temporais
                data['day_of_week'] = data['date'].dt.dayofweek
                data['month'] = data['date'].dt.month
                data['quarter'] = data['date'].dt.quarter
                data['year'] = data['date'].dt.year
                data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
                
                # Rolling features
                for keyword in data['keyword'].unique():
                    keyword_mask = data['keyword'] == keyword
                    data.loc[keyword_mask, 'value_ma_7'] = data.loc[keyword_mask, 'value'].rolling(7).mean()
                    data.loc[keyword_mask, 'value_ma_30'] = data.loc[keyword_mask, 'value'].rolling(30).mean()
                    data.loc[keyword_mask, 'value_std_7'] = data.loc[keyword_mask, 'value'].rolling(7).std()
                
                # Remove NaN após rolling
                data = data.dropna()
                
                self.metrics.increment_counter("data_preparation_success")
                logger.info(f"✅ Dados preparados: {len(data)} registros")
                return data
                
            except Exception as e:
                self.metrics.increment_counter("data_preparation_error")
                logger.error(f"❌ Erro na preparação de dados: {e}")
                raise
    
    def train_prophet_model(self, data: pd.DataFrame, keyword: str) -> Optional[Prophet]:
        """
        Treina modelo Prophet para série temporal
        
        Args:
            data: Dados preparados
            keyword: Keyword específica
            
        Returns:
            Modelo Prophet treinado
        """
        if not PROPHET_AVAILABLE:
            logger.warning("⚠️ Prophet não disponível")
            return None
        
        with self.tracing.start_span("train_prophet"):
            try:
                keyword_data = data[data['keyword'] == keyword].copy()
                
                if len(keyword_data) < self.min_data_points:
                    logger.warning(f"⚠️ Dados insuficientes para {keyword}: {len(keyword_data)} < {self.min_data_points}")
                    return None
                
                # Formato Prophet
                prophet_data = keyword_data[['date', 'value']].rename(columns={
                    'date': 'ds',
                    'value': 'result'
                })
                
                # Configuração do modelo
                model = Prophet(
                    yearly_seasonality=self.config['seasonality']['yearly'],
                    weekly_seasonality=self.config['seasonality']['weekly'],
                    daily_seasonality=self.config['seasonality']['daily'],
                    changepoint_prior_scale=0.05,
                    seasonality_prior_scale=10.0
                )
                
                # Treinamento
                model.fit(prophet_data)
                
                self.metrics.increment_counter("prophet_training_success")
                logger.info(f"✅ Modelo Prophet treinado para {keyword}")
                return model
                
            except Exception as e:
                self.metrics.increment_counter("prophet_training_error")
                logger.error(f"❌ Erro no treinamento Prophet para {keyword}: {e}")
                return None
    
    def train_ml_model(self, data: pd.DataFrame, keyword: str) -> Optional[RandomForestRegressor]:
        """
        Treina modelo ML tradicional
        
        Args:
            data: Dados preparados
            keyword: Keyword específica
            
        Returns:
            Modelo ML treinado
        """
        with self.tracing.start_span("train_ml_model"):
            try:
                keyword_data = data[data['keyword'] == keyword].copy()
                
                if len(keyword_data) < self.min_data_points:
                    logger.warning(f"⚠️ Dados insuficientes para {keyword}: {len(keyword_data)} < {self.min_data_points}")
                    return None
                
                # Features para ML
                feature_cols = ['day_of_week', 'month', 'quarter', 'year', 'is_weekend',
                               'value_ma_7', 'value_ma_30', 'value_std_7']
                
                X = keyword_data[feature_cols].fillna(0)
                result = keyword_data['value']
                
                # Split temporal (não aleatório)
                split_idx = int(len(X) * 0.8)
                X_train, X_test = X[:split_idx], X[split_idx:]
                y_train, y_test = result[:split_idx], result[split_idx:]
                
                # Treinamento
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                
                model.fit(X_train, y_train)
                
                # Avaliação
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                self.model_performance[keyword] = {
                    'mae': mae,
                    'r2': r2,
                    'test_size': len(X_test)
                }
                
                self.metrics.increment_counter("ml_training_success")
                logger.info(f"✅ Modelo ML treinado para {keyword} - MAE: {mae:.4f}, R²: {r2:.4f}")
                return model
                
            except Exception as e:
                self.metrics.increment_counter("ml_training_error")
                logger.error(f"❌ Erro no treinamento ML para {keyword}: {e}")
                return None
    
    def predict_trend(self, data: pd.DataFrame, keyword: str, 
                     timeframe: str = "30d") -> Optional[TrendPrediction]:
        """
        Prediz tendência para uma keyword específica
        
        Args:
            data: Dados históricos
            keyword: Keyword para predição
            timeframe: Horizonte de predição
            
        Returns:
            Predição de tendência
        """
        with self.tracing.start_span("predict_trend"):
            try:
                # Verifica cache
                cache_key = f"{keyword}_{timeframe}"
                if cache_key in self.predictions_cache:
                    cached_pred = self.predictions_cache[cache_key]
                    if (datetime.now() - cached_pred['timestamp']).seconds < self.config['cache_ttl']:
                        return cached_pred['prediction']
                
                keyword_data = data[data['keyword'] == keyword].copy()
                
                if len(keyword_data) < self.min_data_points:
                    logger.warning(f"⚠️ Dados insuficientes para {keyword}")
                    return None
                
                current_value = keyword_data['value'].iloc[-1]
                
                # Predição Prophet
                prophet_pred = None
                if PROPHET_AVAILABLE:
                    prophet_model = self.train_prophet_model(data, keyword)
                    if prophet_model:
                        future_dates = prophet_model.make_future_dataframe(periods=self.prediction_horizon)
                        forecast = prophet_model.predict(future_dates)
                        prophet_pred = forecast['yhat'].iloc[-1]
                
                # Predição ML
                ml_pred = None
                ml_model = self.train_ml_model(data, keyword)
                if ml_model:
                    latest_features = keyword_data[['day_of_week', 'month', 'quarter', 'year', 'is_weekend',
                                                   'value_ma_7', 'value_ma_30', 'value_std_7']].iloc[-1:].fillna(0)
                    ml_pred = ml_model.predict(latest_features)[0]
                
                # Combinação de predições
                predictions = []
                weights = []
                
                if prophet_pred is not None:
                    predictions.append(prophet_pred)
                    weights.append(0.6)  # Prophet tem peso maior para séries temporais
                
                if ml_pred is not None:
                    predictions.append(ml_pred)
                    weights.append(0.4)
                
                if not predictions:
                    logger.warning(f"⚠️ Nenhuma predição válida para {keyword}")
                    return None
                
                # Predição final (média ponderada)
                final_prediction = np.average(predictions, weights=weights)
                
                # Cálculo de confiança
                confidence = self._calculate_confidence(keyword_data, predictions, weights)
                
                # Direção da tendência
                direction = self._determine_direction(current_value, final_prediction, confidence)
                
                # Nível de confiança
                confidence_level = self._determine_confidence_level(confidence)
                
                # Fatores de influência
                factors = self._analyze_factors(keyword_data, final_prediction)
                
                # Cria predição
                prediction = TrendPrediction(
                    keyword=keyword,
                    current_value=current_value,
                    predicted_value=final_prediction,
                    confidence=confidence,
                    direction=direction,
                    confidence_level=confidence_level,
                    timeframe=timeframe,
                    factors=factors,
                    metadata={
                        'prophet_pred': prophet_pred,
                        'ml_pred': ml_pred,
                        'data_points': len(keyword_data),
                        'model_performance': self.model_performance.get(keyword, {})
                    }
                )
                
                # Cache
                self.predictions_cache[cache_key] = {
                    'prediction': prediction,
                    'timestamp': datetime.now()
                }
                
                self.metrics.increment_counter("trend_prediction_success")
                logger.info(f"✅ Predição para {keyword}: {direction.value} (conf: {confidence:.2f})")
                return prediction
                
            except Exception as e:
                self.metrics.increment_counter("trend_prediction_error")
                logger.error(f"❌ Erro na predição para {keyword}: {e}")
                return None
    
    def _calculate_confidence(self, data: pd.DataFrame, predictions: List[float], 
                            weights: List[float]) -> float:
        """Calcula nível de confiança da predição"""
        try:
            # Variabilidade dos dados
            data_std = data['value'].std()
            data_mean = data['value'].mean()
            cv = data_std / data_mean if data_mean > 0 else 1
            
            # Consistência entre modelos
            if len(predictions) > 1:
                pred_std = np.std(predictions)
                pred_mean = np.mean(predictions)
                pred_cv = pred_std / pred_mean if pred_mean > 0 else 1
            else:
                pred_cv = 0
            
            # Confiança baseada em estabilidade
            stability_score = max(0, 1 - cv)
            
            # Confiança baseada em consistência
            consistency_score = max(0, 1 - pred_cv)
            
            # Confiança baseada em quantidade de dados
            data_score = min(1, len(data) / 100)
            
            # Confiança final
            confidence = (stability_score * 0.4 + 
                         consistency_score * 0.4 + 
                         data_score * 0.2)
            
            return min(1, max(0, confidence))
            
        except Exception as e:
            logger.warning(f"⚠️ Erro no cálculo de confiança: {e}")
            return 0.5
    
    def _determine_direction(self, current: float, predicted: float, 
                           confidence: float) -> TrendDirection:
        """Determina direção da tendência"""
        if confidence < 0.3:
            return TrendDirection.VOLATILE
        
        change_pct = (predicted - current) / current if current > 0 else 0
        
        if abs(change_pct) < 0.05:  # < 5% de mudança
            return TrendDirection.STABLE
        elif change_pct > 0.05:
            return TrendDirection.RISING
        else:
            return TrendDirection.FALLING
    
    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determina nível de confiança"""
        if confidence > 0.8:
            return ConfidenceLevel.HIGH
        elif confidence > 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _analyze_factors(self, data: pd.DataFrame, prediction: float) -> Dict[str, float]:
        """Analisa fatores que influenciam a predição"""
        factors = {}
        
        try:
            # Sazonalidade semanal
            weekly_pattern = data.groupby('day_of_week')['value'].mean()
            factors['weekly_seasonality'] = weekly_pattern.std() / weekly_pattern.mean()
            
            # Sazonalidade mensal
            monthly_pattern = data.groupby('month')['value'].mean()
            factors['monthly_seasonality'] = monthly_pattern.std() / monthly_pattern.mean()
            
            # Tendência linear
            if len(data) > 10:
                value = np.arange(len(data))
                result = data['value'].values
                slope = np.polyfit(value, result, 1)[0]
                factors['linear_trend'] = slope / data['value'].mean()
            
            # Volatilidade
            factors['volatility'] = data['value'].std() / data['value'].mean()
            
            # Tendência recente (últimos 7 dias)
            recent_data = data.tail(7)
            if len(recent_data) > 1:
                recent_slope = np.polyfit(range(len(recent_data)), recent_data['value'], 1)[0]
                factors['recent_trend'] = recent_slope / recent_data['value'].mean()
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na análise de fatores: {e}")
        
        return factors
    
    def generate_alerts(self, predictions: List[TrendPrediction]) -> List[TrendAlert]:
        """
        Gera alertas baseados nas predições
        
        Args:
            predictions: Lista de predições
            
        Returns:
            Lista de alertas
        """
        alerts = []
        
        with self.tracing.start_span("generate_alerts"):
            try:
                thresholds = self.config['alert_thresholds']
                
                for pred in predictions:
                    if pred.confidence < self.confidence_threshold:
                        continue
                    
                    change_pct = (pred.predicted_value - pred.current_value) / pred.current_value
                    
                    # Alerta de alta subida
                    if change_pct > thresholds['high_rise']:
                        alerts.append(TrendAlert(
                            keyword=pred.keyword,
                            alert_type="high_rise",
                            severity="high",
                            message=f"Alta subida prevista: {change_pct:.1%} em {pred.timeframe}",
                            predicted_value=pred.predicted_value,
                            threshold=thresholds['high_rise'],
                            confidence=pred.confidence,
                            metadata={'change_pct': change_pct}
                        ))
                    
                    # Alerta de alta queda
                    elif change_pct < thresholds['high_fall']:
                        alerts.append(TrendAlert(
                            keyword=pred.keyword,
                            alert_type="high_fall",
                            severity="high",
                            message=f"Alta queda prevista: {change_pct:.1%} em {pred.timeframe}",
                            predicted_value=pred.predicted_value,
                            threshold=thresholds['high_fall'],
                            confidence=pred.confidence,
                            metadata={'change_pct': change_pct}
                        ))
                    
                    # Alerta de subida moderada
                    elif change_pct > thresholds['moderate_rise']:
                        alerts.append(TrendAlert(
                            keyword=pred.keyword,
                            alert_type="moderate_rise",
                            severity="medium",
                            message=f"Subida moderada prevista: {change_pct:.1%} em {pred.timeframe}",
                            predicted_value=pred.predicted_value,
                            threshold=thresholds['moderate_rise'],
                            confidence=pred.confidence,
                            metadata={'change_pct': change_pct}
                        ))
                    
                    # Alerta de queda moderada
                    elif change_pct < thresholds['moderate_fall']:
                        alerts.append(TrendAlert(
                            keyword=pred.keyword,
                            alert_type="moderate_fall",
                            severity="medium",
                            message=f"Queda moderada prevista: {change_pct:.1%} em {pred.timeframe}",
                            predicted_value=pred.predicted_value,
                            threshold=thresholds['moderate_fall'],
                            confidence=pred.confidence,
                            metadata={'change_pct': change_pct}
                        ))
                
                # Atualiza histórico
                self.alerts_history.extend(alerts)
                
                self.metrics.increment_counter("alerts_generated", len(alerts))
                logger.info(f"✅ {len(alerts)} alertas gerados")
                
                return alerts
                
            except Exception as e:
                self.metrics.increment_counter("alerts_generation_error")
                logger.error(f"❌ Erro na geração de alertas: {e}")
                return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance dos modelos"""
        return {
            'model_performance': self.model_performance,
            'total_predictions': len(self.predictions_cache),
            'total_alerts': len(self.alerts_history),
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'average_confidence': self._calculate_average_confidence(),
            'alert_distribution': self._calculate_alert_distribution()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calcula taxa de hit do cache"""
        # Implementação simplificada
        return 0.85  # Placeholder
    
    def _calculate_average_confidence(self) -> float:
        """Calcula confiança média das predições"""
        if not self.predictions_cache:
            return 0.0
        
        confidences = [pred['prediction'].confidence for pred in self.predictions_cache.values()]
        return np.mean(confidences)
    
    def _calculate_alert_distribution(self) -> Dict[str, int]:
        """Calcula distribuição de alertas por tipo"""
        distribution = {}
        for alert in self.alerts_history:
            alert_type = alert.alert_type
            distribution[alert_type] = distribution.get(alert_type, 0) + 1
        return distribution
    
    def save_model(self, filepath: str):
        """Salva modelo treinado"""
        try:
            model_data = {
                'config': self.config,
                'model_performance': self.model_performance,
                'predictions_cache': self.predictions_cache,
                'alerts_history': self.alerts_history
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"✅ Modelo salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar modelo: {e}")
    
    def load_model(self, filepath: str):
        """Carrega modelo salvo"""
        try:
            model_data = joblib.load(filepath)
            
            self.config = model_data['config']
            self.model_performance = model_data['model_performance']
            self.predictions_cache = model_data['predictions_cache']
            self.alerts_history = model_data['alerts_history']
            
            logger.info(f"✅ Modelo carregado de {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")


# Função de conveniência para uso rápido
def predict_keyword_trends(data: pd.DataFrame, keywords: List[str], 
                          timeframe: str = "30d", config: Optional[Dict] = None) -> Dict[str, TrendPrediction]:
    """
    Função de conveniência para predizer tendências de múltiplas keywords
    
    Args:
        data: DataFrame com dados históricos
        keywords: Lista de keywords para predição
        timeframe: Horizonte de predição
        config: Configurações opcionais
        
    Returns:
        Dicionário com predições por keyword
    """
    predictor = TrendPredictor(config)
    
    # Prepara dados
    prepared_data = predictor.prepare_data(data)
    
    # Predições
    predictions = {}
    for keyword in keywords:
        pred = predictor.predict_trend(prepared_data, keyword, timeframe)
        if pred:
            predictions[keyword] = pred
    
    return predictions 