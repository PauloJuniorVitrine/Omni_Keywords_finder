"""
📊 Analisador de Séries Temporais - Omni Keywords Finder
🔍 Detecção de padrões, sazonalidade e decomposição temporal
🔄 Versão: 1.0
📅 Data: 2024-12-19
👤 Autor: Paulo Júnior
🔗 Tracing ID: PREDICTION_20241219_002
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import warnings
from scipy import stats
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import seaborn as sns

# Statsmodels para decomposição
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller, kpss
    from statsmodels.tsa.arima.model import ARIMA
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn("Statsmodels não disponível. Funcionalidades limitadas.")

# Observability
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeasonalityType(Enum):
    """Tipos de sazonalidade detectados"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    NONE = "none"


class TrendType(Enum):
    """Tipos de tendência detectados"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    CYCLICAL = "cyclical"
    RANDOM = "random"


@dataclass
class SeasonalityPattern:
    """Padrão de sazonalidade detectado"""
    type: SeasonalityType
    strength: float  # 0-1, força da sazonalidade
    period: int      # Período em dias
    confidence: float
    pattern: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Análise de tendência"""
    type: TrendType
    slope: float
    strength: float  # 0-1
    confidence: float
    changepoints: List[datetime] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeSeriesDecomposition:
    """Decomposição de série temporal"""
    trend: pd.Series
    seasonal: pd.Series
    residual: pd.Series
    original: pd.Series
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetection:
    """Detecção de anomalias"""
    anomalies: List[datetime]
    scores: List[float]
    threshold: float
    method: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class TimeSeriesAnalyzer:
    """
    📊 Analisador Avançado de Séries Temporais
    
    Funcionalidades:
    - Detecção de sazonalidade
    - Análise de tendências
    - Decomposição temporal
    - Detecção de anomalias
    - Testes de estacionariedade
    - Análise de correlação
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o analisador
        
        Args:
            config: Configurações do sistema
        """
        self.config = config or self._default_config()
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
        
        # Cache de análises
        self.analysis_cache = {}
        
        logger.info(f"📊 TimeSeriesAnalyzer inicializado com config: {self.config}")
    
    def _default_config(self) -> Dict:
        """Configuração padrão"""
        return {
            'min_periods': {
                'daily': 7,
                'weekly': 28,
                'monthly': 90,
                'quarterly': 365,
                'yearly': 730
            },
            'seasonality_threshold': 0.3,
            'trend_threshold': 0.1,
            'anomaly_threshold': 2.0,  # Desvios padrão
            'changepoint_sensitivity': 0.1,
            'correlation_threshold': 0.7,
            'decomposition_period': None,  # Auto-detect
            'smoothing_window': 7
        }
    
    def analyze_series(self, data: pd.Series, 
                      name: str = "series") -> Dict[str, Any]:
        """
        Análise completa de série temporal
        
        Args:
            data: Série temporal
            name: Nome da série
            
        Returns:
            Dicionário com todas as análises
        """
        with self.tracing.start_span("analyze_series"):
            try:
                # Verifica cache
                cache_key = f"{name}_{hash(str(data.index[-10:]))}"
                if cache_key in self.analysis_cache:
                    return self.analysis_cache[cache_key]
                
                # Validação
                if len(data) < 10:
                    logger.warning(f"⚠️ Série muito curta: {len(data)} pontos")
                    return {}
                
                # Remove valores nulos
                data_clean = data.dropna()
                if len(data_clean) < len(data) * 0.8:
                    logger.warning(f"⚠️ Muitos valores nulos: {len(data) - len(data_clean)}")
                
                # Análises
                results = {
                    'basic_stats': self._basic_statistics(data_clean),
                    'stationarity': self._test_stationarity(data_clean),
                    'seasonality': self._detect_seasonality(data_clean),
                    'trend': self._analyze_trend(data_clean),
                    'decomposition': self._decompose_series(data_clean),
                    'anomalies': self._detect_anomalies(data_clean),
                    'correlation': self._analyze_correlation(data_clean),
                    'metadata': {
                        'series_name': name,
                        'length': len(data_clean),
                        'date_range': f"{data_clean.index.min()} to {data_clean.index.max()}",
                        'analysis_timestamp': datetime.now()
                    }
                }
                
                # Cache
                self.analysis_cache[cache_key] = results
                
                self.metrics.increment_counter("series_analysis_success")
                logger.info(f"✅ Análise completa para {name}")
                return results
                
            except Exception as e:
                self.metrics.increment_counter("series_analysis_error")
                logger.error(f"❌ Erro na análise de {name}: {e}")
                return {}
    
    def _basic_statistics(self, data: pd.Series) -> Dict[str, float]:
        """Estatísticas básicas da série"""
        try:
            return {
                'mean': data.mean(),
                'median': data.median(),
                'std': data.std(),
                'min': data.min(),
                'max': data.max(),
                'skewness': data.skew(),
                'kurtosis': data.kurtosis(),
                'cv': data.std() / data.mean() if data.mean() > 0 else 0,
                'iqr': data.quantile(0.75) - data.quantile(0.25)
            }
        except Exception as e:
            logger.warning(f"⚠️ Erro nas estatísticas básicas: {e}")
            return {}
    
    def _test_stationarity(self, data: pd.Series) -> Dict[str, Any]:
        """Testa estacionariedade da série"""
        if not STATSMODELS_AVAILABLE:
            return {'available': False}
        
        try:
            results = {}
            
            # Teste ADF (Augmented Dickey-Fuller)
            adf_result = adfuller(data.dropna())
            results['adf'] = {
                'statistic': adf_result[0],
                'pvalue': adf_result[1],
                'critical_values': adf_result[4],
                'is_stationary': adf_result[1] < 0.05
            }
            
            # Teste KPSS
            kpss_result = kpss(data.dropna())
            results['kpss'] = {
                'statistic': kpss_result[0],
                'pvalue': kpss_result[1],
                'critical_values': kpss_result[3],
                'is_stationary': kpss_result[1] > 0.05
            }
            
            # Conclusão
            adf_stationary = results['adf']['is_stationary']
            kpss_stationary = results['kpss']['is_stationary']
            
            results['conclusion'] = {
                'is_stationary': adf_stationary and kpss_stationary,
                'confidence': 'high' if adf_stationary and kpss_stationary else 'low'
            }
            
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ Erro no teste de estacionariedade: {e}")
            return {'error': str(e)}
    
    def _detect_seasonality(self, data: pd.Series) -> List[SeasonalityPattern]:
        """Detecta padrões sazonais"""
        patterns = []
        
        try:
            # Análise de autocorrelação
            autocorr = data.autocorr(lag=1)
            
            # Testa diferentes períodos
            periods_to_test = [7, 14, 30, 90, 180, 365]
            
            for period in periods_to_test:
                if len(data) < period * 2:
                    continue
                
                # Calcula autocorrelação para o período
                if len(data) > period:
                    lagged_corr = data.autocorr(lag=period)
                    
                    # Força da sazonalidade
                    strength = abs(lagged_corr) if not pd.isna(lagged_corr) else 0
                    
                    if strength > self.config['seasonality_threshold']:
                        # Determina tipo de sazonalidade
                        if period <= 7:
                            seasonality_type = SeasonalityType.DAILY
                        elif period <= 14:
                            seasonality_type = SeasonalityType.WEEKLY
                        elif period <= 90:
                            seasonality_type = SeasonalityType.MONTHLY
                        elif period <= 180:
                            seasonality_type = SeasonalityType.QUARTERLY
                        else:
                            seasonality_type = SeasonalityType.YEARLY
                        
                        # Calcula padrão sazonal
                        pattern = self._calculate_seasonal_pattern(data, period)
                        
                        patterns.append(SeasonalityPattern(
                            type=seasonality_type,
                            strength=strength,
                            period=period,
                            confidence=min(1.0, strength * 2),
                            pattern=pattern,
                            metadata={
                                'autocorr': lagged_corr,
                                'data_points': len(data)
                            }
                        ))
            
            # Ordena por força
            patterns.sort(key=lambda value: value.strength, reverse=True)
            
            return patterns
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na detecção de sazonalidade: {e}")
            return []
    
    def _calculate_seasonal_pattern(self, data: pd.Series, period: int) -> Dict[str, float]:
        """Calcula padrão sazonal para um período"""
        try:
            pattern = {}
            
            # Agrupa por posição no período
            for index in range(period):
                if index < len(data):
                    # Média dos valores na posição index de cada período
                    values_at_position = []
                    for counter in range(index, len(data), period):
                        values_at_position.append(data.iloc[counter])
                    
                    if values_at_position:
                        pattern[f'pos_{index}'] = np.mean(values_at_position)
            
            return pattern
            
        except Exception as e:
            logger.warning(f"⚠️ Erro no cálculo do padrão sazonal: {e}")
            return {}
    
    def _analyze_trend(self, data: pd.Series) -> TrendAnalysis:
        """Analisa tendência da série"""
        try:
            # Regressão linear
            value = np.arange(len(data))
            result = data.values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(value, result)
            
            # Força da tendência (R²)
            strength = r_value ** 2
            
            # Tipo de tendência
            if abs(slope) < self.config['trend_threshold']:
                trend_type = TrendType.STABLE
            elif slope > 0:
                trend_type = TrendType.INCREASING
            else:
                trend_type = TrendType.DECREASING
            
            # Detecta changepoints
            changepoints = self._detect_changepoints(data)
            
            # Confiança baseada em p-value
            confidence = 1 - p_value if p_value < 1 else 0
            
            return TrendAnalysis(
                type=trend_type,
                slope=slope,
                strength=strength,
                confidence=confidence,
                changepoints=changepoints,
                metadata={
                    'r_squared': strength,
                    'p_value': p_value,
                    'std_error': std_err
                }
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na análise de tendência: {e}")
            return TrendAnalysis(
                type=TrendType.RANDOM,
                slope=0,
                strength=0,
                confidence=0
            )
    
    def _detect_changepoints(self, data: pd.Series) -> List[datetime]:
        """Detecta pontos de mudança na série"""
        try:
            changepoints = []
            
            # Método simples: detecta mudanças significativas na média móvel
            window = max(7, len(data) // 20)
            ma = data.rolling(window=window, center=True).mean()
            
            # Calcula diferenças
            diff = ma.diff()
            
            # Threshold baseado no desvio padrão
            threshold = diff.std() * self.config['changepoint_sensitivity']
            
            # Encontra pontos onde a diferença excede o threshold
            changepoint_indices = np.where(np.abs(diff) > threshold)[0]
            
            for idx in changepoint_indices:
                if idx < len(data.index):
                    changepoints.append(data.index[idx])
            
            return changepoints
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na detecção de changepoints: {e}")
            return []
    
    def _decompose_series(self, data: pd.Series) -> Optional[TimeSeriesDecomposition]:
        """Decompõe série em tendência, sazonalidade e resíduos"""
        if not STATSMODELS_AVAILABLE:
            return None
        
        try:
            # Determina período para decomposição
            period = self.config['decomposition_period']
            if period is None:
                # Auto-detecta período
                seasonality_patterns = self._detect_seasonality(data)
                if seasonality_patterns:
                    period = seasonality_patterns[0].period
                else:
                    period = 7  # Default
            
            # Decomposição
            decomposition = seasonal_decompose(
                data, 
                period=min(period, len(data) // 2),
                extrapolate_trend='freq'
            )
            
            return TimeSeriesDecomposition(
                trend=decomposition.trend,
                seasonal=decomposition.seasonal,
                residual=decomposition.resid,
                original=data,
                metadata={
                    'period': period,
                    'method': 'seasonal_decompose'
                }
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na decomposição: {e}")
            return None
    
    def _detect_anomalies(self, data: pd.Series) -> AnomalyDetection:
        """Detecta anomalias na série"""
        try:
            anomalies = []
            scores = []
            
            # Método 1: Z-score
            z_scores = np.abs(stats.zscore(data.dropna()))
            threshold = self.config['anomaly_threshold']
            
            anomaly_indices = np.where(z_scores > threshold)[0]
            
            for idx in anomaly_indices:
                if idx < len(data.index):
                    anomalies.append(data.index[idx])
                    scores.append(z_scores[idx])
            
            # Método 2: IQR
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            iqr_anomalies = data[(data < lower_bound) | (data > upper_bound)]
            
            # Combina resultados
            all_anomalies = list(set(anomalies + list(iqr_anomalies.index)))
            
            return AnomalyDetection(
                anomalies=all_anomalies,
                scores=scores,
                threshold=threshold,
                method="zscore_iqr",
                metadata={
                    'zscore_anomalies': len(anomalies),
                    'iqr_anomalies': len(iqr_anomalies),
                    'total_anomalies': len(all_anomalies)
                }
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na detecção de anomalias: {e}")
            return AnomalyDetection(
                anomalies=[],
                scores=[],
                threshold=self.config['anomaly_threshold'],
                method="error"
            )
    
    def _analyze_correlation(self, data: pd.Series) -> Dict[str, float]:
        """Analisa correlações temporais"""
        try:
            correlations = {}
            
            # Autocorrelação em diferentes lags
            for lag in [1, 7, 14, 30]:
                if len(data) > lag:
                    corr = data.autocorr(lag=lag)
                    if not pd.isna(corr):
                        correlations[f'lag_{lag}'] = corr
            
            # Correlação com tendência temporal
            value = np.arange(len(data))
            trend_corr = np.corrcoef(value, data.values)[0, 1]
            correlations['trend'] = trend_corr if not np.isnan(trend_corr) else 0
            
            return correlations
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na análise de correlação: {e}")
            return {}
    
    def plot_analysis(self, data: pd.Series, analysis: Dict[str, Any], 
                     save_path: Optional[str] = None):
        """
        Gera gráficos da análise
        
        Args:
            data: Série temporal
            analysis: Resultado da análise
            save_path: Caminho para salvar gráfico
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'Análise de Série Temporal: {analysis.get("metadata", {}).get("series_name", "Unknown")}')
            
            # Gráfico original
            axes[0, 0].plot(data.index, data.values)
            axes[0, 0].set_title('Série Original')
            axes[0, 0].grid(True)
            
            # Decomposição
            if 'decomposition' in analysis and analysis['decomposition']:
                decomp = analysis['decomposition']
                axes[0, 1].plot(decomp.trend.index, decomp.trend.values, label='Tendência')
                axes[0, 1].plot(decomp.seasonal.index, decomp.seasonal.values, label='Sazonalidade')
                axes[0, 1].set_title('Decomposição')
                axes[0, 1].legend()
                axes[0, 1].grid(True)
            
            # Anomalias
            if 'anomalies' in analysis and analysis['anomalies'].anomalies:
                axes[1, 0].plot(data.index, data.values, 'b-', label='Dados')
                anomaly_dates = analysis['anomalies'].anomalies
                anomaly_values = [data.get(date, 0) for date in anomaly_dates]
                axes[1, 0].scatter(anomaly_dates, anomaly_values, color='red', 
                                 label='Anomalias', string_data=50)
                axes[1, 0].set_title('Detecção de Anomalias')
                axes[1, 0].legend()
                axes[1, 0].grid(True)
            
            # Autocorrelação
            if 'correlation' in analysis:
                lags = [int(key.split('_')[1]) for key in analysis['correlation'].keys() if key.startswith('lag_')]
                corrs = [analysis['correlation'][f'lag_{lag}'] for lag in lags]
                axes[1, 1].bar(lags, corrs)
                axes[1, 1].set_title('Autocorrelação')
                axes[1, 1].set_xlabel('Lag')
                axes[1, 1].set_ylabel('Correlação')
                axes[1, 1].grid(True)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"✅ Gráfico salvo em {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de gráfico: {e}")
    
    def get_summary_report(self, analysis: Dict[str, Any]) -> str:
        """Gera relatório resumido da análise"""
        try:
            report = []
            metadata = analysis.get('metadata', {})
            
            report.append(f"📊 RELATÓRIO DE ANÁLISE TEMPORAL")
            report.append(f"📅 Série: {metadata.get('series_name', 'Unknown')}")
            report.append(f"📈 Período: {metadata.get('date_range', 'Unknown')}")
            report.append(f"📊 Pontos: {metadata.get('length', 0)}")
            report.append("")
            
            # Estatísticas básicas
            if 'basic_stats' in analysis:
                stats = analysis['basic_stats']
                report.append("📈 ESTATÍSTICAS BÁSICAS:")
                report.append(f"   Média: {stats.get('mean', 0):.2f}")
                report.append(f"   Mediana: {stats.get('median', 0):.2f}")
                report.append(f"   Desvio Padrão: {stats.get('std', 0):.2f}")
                report.append(f"   CV: {stats.get('cv', 0):.2f}")
                report.append("")
            
            # Estacionariedade
            if 'stationarity' in analysis and analysis['stationarity'].get('available', False):
                stationarity = analysis['stationarity']
                conclusion = stationarity.get('conclusion', {})
                report.append("🔄 ESTACIONARIEDADE:")
                report.append(f"   ADF p-value: {stationarity.get('adf', {}).get('pvalue', 0):.4f}")
                report.append(f"   KPSS p-value: {stationarity.get('kpss', {}).get('pvalue', 0):.4f}")
                report.append(f"   Conclusão: {'Estacionária' if conclusion.get('is_stationary', False) else 'Não estacionária'}")
                report.append("")
            
            # Sazonalidade
            if 'seasonality' in analysis and analysis['seasonality']:
                report.append("🌊 SAZONALIDADE:")
                for pattern in analysis['seasonality'][:3]:  # Top 3
                    report.append(f"   {pattern.type.value.title()}: força={pattern.strength:.2f}, período={pattern.period}")
                report.append("")
            
            # Tendência
            if 'trend' in analysis:
                trend = analysis['trend']
                report.append("📈 TENDÊNCIA:")
                report.append(f"   Tipo: {trend.type.value}")
                report.append(f"   Inclinação: {trend.slope:.4f}")
                report.append(f"   Força: {trend.strength:.2f}")
                report.append(f"   Changepoints: {len(trend.changepoints)}")
                report.append("")
            
            # Anomalias
            if 'anomalies' in analysis:
                anomalies = analysis['anomalies']
                report.append("🚨 ANOMALIAS:")
                report.append(f"   Total: {len(anomalies.anomalies)}")
                report.append(f"   Método: {anomalies.method}")
                report.append(f"   Threshold: {anomalies.threshold}")
                report.append("")
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"❌ Erro na geração do relatório: {e}")
            return "Erro na geração do relatório"


# Função de conveniência
def analyze_keyword_timeseries(data: pd.DataFrame, keyword: str) -> Dict[str, Any]:
    """
    Função de conveniência para análise de série temporal de keyword
    
    Args:
        data: DataFrame com colunas ['date', 'keyword', 'value']
        keyword: Keyword específica
        
    Returns:
        Resultado da análise
    """
    analyzer = TimeSeriesAnalyzer()
    
    # Filtra dados da keyword
    keyword_data = data[data['keyword'] == keyword].set_index('date')['value']
    
    # Análise
    return analyzer.analyze_series(keyword_data, keyword) 