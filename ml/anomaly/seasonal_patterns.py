"""
Sistema de Detecção de Padrões Sazonais usando Machine Learning
Identifica tendências cíclicas e sazonais em dados de SEO
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.decomposition import PCA
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeasonalPatternDetector:
    """
    Sistema de detecção de padrões sazonais
    """
    
    def __init__(self, model_path: str = "models/seasonal_pattern_detector.pkl"):
        self.model_path = model_path
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.seasonal_baselines = {}
        self.pattern_components = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para detecção de padrões sazonais
        """
        features = data.copy()
        
        # Features temporais básicas
        features['date'] = pd.to_datetime(features['date'])
        features['year'] = features['date'].dt.year
        features['month'] = features['date'].dt.month
        features['day'] = features['date'].dt.day
        features['day_of_week'] = features['date'].dt.dayofweek
        features['day_of_year'] = features['date'].dt.dayofyear
        features['week'] = features['date'].dt.isocalendar().week
        features['quarter'] = features['date'].dt.quarter
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Features sazonais
        features['is_holiday'] = self._is_holiday(features['date'])
        features['is_school_holiday'] = self._is_school_holiday(features['date'])
        features['is_vacation_season'] = self._is_vacation_season(features['date'])
        features['is_shopping_season'] = self._is_shopping_season(features['date'])
        features['is_tax_season'] = self._is_tax_season(features['date'])
        
        # Features de métricas
        features['search_volume'] = features['search_volume'].fillna(0)
        features['organic_traffic'] = features['organic_traffic'].fillna(0)
        features['conversion_rate'] = features['conversion_rate'].fillna(0.02)
        features['click_through_rate'] = features['click_through_rate'].fillna(0.05)
        features['bounce_rate'] = features['bounce_rate'].fillna(0.5)
        features['time_on_site'] = features['time_on_site'].fillna(120)
        features['pages_per_session'] = features['pages_per_session'].fillna(2.0)
        
        # Features de ranking
        features['ranking_position'] = features['ranking_position'].fillna(100)
        features['ranking_change'] = features['ranking_change'].fillna(0)
        features['ranking_volatility'] = features['ranking_volatility'].fillna(0)
        
        # Features de preços
        features['cpc'] = features['cpc'].fillna(1.0)
        features['cpm'] = features['cpm'].fillna(5.0)
        features['price_volatility'] = features['price_volatility'].fillna(0)
        
        # Features de competição
        features['competition_intensity'] = features['competition_intensity'].fillna(0.5)
        features['competitor_activity'] = features['competitor_activity'].fillna(0)
        features['market_saturation'] = features['market_saturation'].fillna(0.6)
        
        # Features de conteúdo
        features['content_publishing_frequency'] = features['content_publishing_frequency'].fillna(0)
        features['content_updates'] = features['content_updates'].fillna(0)
        features['content_quality_score'] = features['content_quality_score'].fillna(0.7)
        
        # Features de marketing
        features['social_media_activity'] = features['social_media_activity'].fillna(0)
        features['email_campaigns'] = features['email_campaigns'].fillna(0)
        features['paid_advertising'] = features['paid_advertising'].fillna(0)
        features['influencer_marketing'] = features['influencer_marketing'].fillna(0)
        
        # Features de eventos
        features['industry_events'] = features['industry_events'].fillna(0)
        features['product_launches'] = features['product_launches'].fillna(0)
        features['news_coverage'] = features['news_coverage'].fillna(0)
        features['viral_content'] = features['viral_content'].fillna(0)
        
        # Features de clima (se disponíveis)
        features['weather_impact'] = features['weather_impact'].fillna(0)
        features['temperature'] = features['temperature'].fillna(20)
        features['precipitation'] = features['precipitation'].fillna(0)
        
        # Features econômicas
        features['economic_index'] = features['economic_index'].fillna(100)
        features['consumer_confidence'] = features['consumer_confidence'].fillna(50)
        features['unemployment_rate'] = features['unemployment_rate'].fillna(0.05)
        features['inflation_rate'] = features['inflation_rate'].fillna(0.03)
        
        # Calcular métricas sazonais
        features = self._calculate_seasonal_metrics(features)
        
        return features
    
    def _is_holiday(self, dates: pd.Series) -> pd.Series:
        """
        Identifica feriados brasileiros
        """
        # Feriados brasileiros principais
        holidays = [
            '2024-01-01', '2024-04-21', '2024-05-01', '2024-09-07',
            '2024-10-12', '2024-11-02', '2024-11-15', '2024-12-25'
        ]
        holiday_dates = pd.to_datetime(holidays)
        return dates.isin(holiday_dates).astype(int)
    
    def _is_school_holiday(self, dates: pd.Series) -> pd.Series:
        """
        Identifica férias escolares
        """
        # Férias escolares (janeiro, julho, dezembro)
        school_holidays = dates.dt.month.isin([1, 7, 12])
        return school_holidays.astype(int)
    
    def _is_vacation_season(self, dates: pd.Series) -> pd.Series:
        """
        Identifica temporada de férias
        """
        # Temporadas de férias (dezembro-janeiro, julho)
        vacation_season = dates.dt.month.isin([12, 1, 7])
        return vacation_season.astype(int)
    
    def _is_shopping_season(self, dates: pd.Series) -> pd.Series:
        """
        Identifica temporada de compras
        """
        # Black Friday, Natal, etc. (novembro-dezembro)
        shopping_season = dates.dt.month.isin([11, 12])
        return shopping_season.astype(int)
    
    def _is_tax_season(self, dates: pd.Series) -> pd.Series:
        """
        Identifica temporada de impostos
        """
        # Temporada de impostos (março-abril)
        tax_season = dates.dt.month.isin([3, 4])
        return tax_season.astype(int)
    
    def _calculate_seasonal_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula métricas sazonais
        """
        # Agrupar por keyword/domínio para calcular padrões sazonais
        for group_name, group_data in data.groupby(['keyword', 'domain']):
            if len(group_data) > 30:  # Pelo menos 30 dias de dados
                # Calcular médias móveis sazonais
                group_data = group_data.sort_values('date')
                
                # Médias móveis por período
                group_data['search_volume_ma_7'] = group_data['search_volume'].rolling(7, min_periods=1).mean()
                group_data['search_volume_ma_30'] = group_data['search_volume'].rolling(30, min_periods=1).mean()
                group_data['search_volume_ma_90'] = group_data['search_volume'].rolling(90, min_periods=1).mean()
                
                # Volatilidade sazonal
                group_data['search_volume_std_7'] = group_data['search_volume'].rolling(7, min_periods=1).std()
                group_data['search_volume_std_30'] = group_data['search_volume'].rolling(30, min_periods=1).std()
                
                # Tendências sazonais
                group_data['search_volume_trend_7'] = group_data['search_volume'].rolling(7, min_periods=1).apply(
                    lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
                )
                
                # Atualizar dados originais
                data.loc[group_data.index] = group_data
        
        # Preencher valores NaN
        seasonal_columns = ['search_volume_ma_7', 'search_volume_ma_30', 'search_volume_ma_90',
                           'search_volume_std_7', 'search_volume_std_30', 'search_volume_trend_7']
        
        for col in seasonal_columns:
            if col in data.columns:
                data[col] = data[col].fillna(data[col].mean())
        
        return data
    
    def establish_seasonal_baselines(self, data: pd.DataFrame) -> Dict:
        """
        Estabelece baselines sazonais
        """
        logger.info("Estabelecendo baselines sazonais")
        
        baselines = {}
        
        # Baselines por mês
        monthly_baselines = {}
        for month in range(1, 13):
            month_data = data[data['month'] == month]
            if len(month_data) > 0:
                monthly_baselines[month] = {
                    'avg_search_volume': month_data['search_volume'].mean(),
                    'avg_traffic': month_data['organic_traffic'].mean(),
                    'avg_conversion_rate': month_data['conversion_rate'].mean(),
                    'avg_cpc': month_data['cpc'].mean(),
                    'avg_competition': month_data['competition_intensity'].mean()
                }
        
        # Baselines por dia da semana
        daily_baselines = {}
        for day in range(7):
            day_data = data[data['day_of_week'] == day]
            if len(day_data) > 0:
                daily_baselines[day] = {
                    'avg_search_volume': day_data['search_volume'].mean(),
                    'avg_traffic': day_data['organic_traffic'].mean(),
                    'avg_conversion_rate': day_data['conversion_rate'].mean()
                }
        
        # Baselines por trimestre
        quarterly_baselines = {}
        for quarter in range(1, 5):
            quarter_data = data[data['quarter'] == quarter]
            if len(quarter_data) > 0:
                quarterly_baselines[quarter] = {
                    'avg_search_volume': quarter_data['search_volume'].mean(),
                    'avg_traffic': quarter_data['organic_traffic'].mean(),
                    'avg_conversion_rate': quarter_data['conversion_rate'].mean(),
                    'avg_cpc': quarter_data['cpc'].mean()
                }
        
        self.seasonal_baselines = {
            'monthly': monthly_baselines,
            'daily': daily_baselines,
            'quarterly': quarterly_baselines
        }
        
        return self.seasonal_baselines
    
    def detect_seasonal_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta padrões sazonais
        """
        logger.info("Detectando padrões sazonais")
        
        # Estabelecer baselines se não existirem
        if not self.seasonal_baselines:
            self.establish_seasonal_baselines(data)
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para detecção de padrões
        pattern_features = [
            'month', 'day_of_week', 'day_of_year', 'week', 'quarter',
            'is_weekend', 'is_holiday', 'is_school_holiday', 'is_vacation_season',
            'is_shopping_season', 'is_tax_season', 'search_volume',
            'organic_traffic', 'conversion_rate', 'click_through_rate',
            'bounce_rate', 'time_on_site', 'pages_per_session',
            'ranking_position', 'ranking_change', 'ranking_volatility',
            'cpc', 'cpm', 'price_volatility', 'competition_intensity',
            'competitor_activity', 'market_saturation', 'content_publishing_frequency',
            'content_updates', 'content_quality_score', 'social_media_activity',
            'email_campaigns', 'paid_advertising', 'influencer_marketing',
            'industry_events', 'product_launches', 'news_coverage',
            'viral_content', 'weather_impact', 'temperature', 'precipitation',
            'economic_index', 'consumer_confidence', 'unemployment_rate',
            'inflation_rate', 'search_volume_ma_7', 'search_volume_ma_30',
            'search_volume_ma_90', 'search_volume_std_7', 'search_volume_std_30',
            'search_volume_trend_7'
        ]
        
        # Filtrar features disponíveis
        available_features = [f for f in pattern_features if f in features.columns]
        X = features[available_features].fillna(0)
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Detectar padrões
        pattern_scores = self.isolation_forest.fit_predict(X_scaled)
        pattern_scores = np.where(pattern_scores == -1, 1, 0)  # Converter para 0/1
        
        # Adicionar resultados aos dados
        features['seasonal_pattern_detected'] = pattern_scores
        features['pattern_score'] = self.isolation_forest.decision_function(X_scaled)
        
        return features
    
    def classify_pattern_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica tipos de padrões sazonais
        """
        logger.info("Classificando tipos de padrões sazonais")
        
        # Detectar padrões
        features = self.detect_seasonal_patterns(data)
        
        # Classificar tipos de padrão
        pattern_types = []
        seasonality_levels = []
        prediction_confidence = []
        
        for idx, row in features.iterrows():
            pattern_type = self._classify_pattern_type(row)
            seasonality_level = self._assess_seasonality_level(row)
            confidence = self._calculate_prediction_confidence(row)
            
            pattern_types.append(pattern_type)
            seasonality_levels.append(seasonality_level)
            prediction_confidence.append(confidence)
        
        features['pattern_type'] = pattern_types
        features['seasonality_level'] = seasonality_levels
        features['prediction_confidence'] = prediction_confidence
        
        return features
    
    def _classify_pattern_type(self, row: pd.Series) -> str:
        """
        Classifica o tipo de padrão sazonal
        """
        # Padrões mensais
        if row['month'] in [12, 1] and row['is_shopping_season'] == 1:
            return 'Holiday Shopping Season'
        elif row['month'] in [7] and row['is_vacation_season'] == 1:
            return 'Summer Vacation Season'
        elif row['month'] in [3, 4] and row['is_tax_season'] == 1:
            return 'Tax Season'
        elif row['month'] in [1, 7, 12] and row['is_school_holiday'] == 1:
            return 'School Holiday Season'
        
        # Padrões semanais
        elif row['is_weekend'] == 1:
            return 'Weekend Pattern'
        elif row['day_of_week'] == 0:  # Segunda-feira
            return 'Monday Effect'
        elif row['day_of_week'] == 4:  # Sexta-feira
            return 'Friday Effect'
        
        # Padrões de feriados
        elif row['is_holiday'] == 1:
            return 'Holiday Effect'
        
        # Padrões de clima
        elif row['weather_impact'] > 0.7:
            return 'Weather Impact'
        elif row['temperature'] > 30:
            return 'Hot Weather Pattern'
        elif row['temperature'] < 10:
            return 'Cold Weather Pattern'
        elif row['precipitation'] > 0.5:
            return 'Rainy Weather Pattern'
        
        # Padrões econômicos
        elif row['consumer_confidence'] < 40:
            return 'Low Consumer Confidence'
        elif row['inflation_rate'] > 0.05:
            return 'High Inflation Period'
        elif row['unemployment_rate'] > 0.08:
            return 'High Unemployment Period'
        
        # Padrões de competição
        elif row['competition_intensity'] > 0.8:
            return 'High Competition Period'
        elif row['competitor_activity'] > 0.7:
            return 'Competitor Activity Surge'
        
        # Padrões de marketing
        elif row['paid_advertising'] > 0.8:
            return 'High Advertising Period'
        elif row['social_media_activity'] > 0.8:
            return 'Social Media Campaign'
        elif row['influencer_marketing'] > 0.7:
            return 'Influencer Marketing Period'
        
        # Padrões de eventos
        elif row['industry_events'] > 0:
            return 'Industry Event Period'
        elif row['product_launches'] > 0:
            return 'Product Launch Period'
        elif row['news_coverage'] > 0.7:
            return 'High Media Coverage'
        elif row['viral_content'] > 0:
            return 'Viral Content Period'
        
        else:
            return 'Normal Seasonal Pattern'
    
    def _assess_seasonality_level(self, row: pd.Series) -> str:
        """
        Avalia o nível de sazonalidade
        """
        # Calcular score de sazonalidade
        seasonality_score = 0
        
        # Sazonalidade temporal
        if row['is_holiday'] == 1 or row['is_vacation_season'] == 1:
            seasonality_score += 3
        elif row['is_shopping_season'] == 1 or row['is_tax_season'] == 1:
            seasonality_score += 2
        elif row['is_weekend'] == 1:
            seasonality_score += 1
        
        # Sazonalidade de métricas
        if abs(row['search_volume_trend_7']) > 0.1:
            seasonality_score += 2
        if row['search_volume_std_7'] > row['search_volume_ma_7'] * 0.3:
            seasonality_score += 2
        
        # Sazonalidade de comportamento
        if row['weather_impact'] > 0.7:
            seasonality_score += 2
        if row['consumer_confidence'] < 40 or row['consumer_confidence'] > 70:
            seasonality_score += 1
        
        # Classificar sazonalidade
        if seasonality_score >= 6:
            return 'High Seasonality'
        elif seasonality_score >= 4:
            return 'Medium Seasonality'
        elif seasonality_score >= 2:
            return 'Low Seasonality'
        else:
            return 'Minimal Seasonality'
    
    def _calculate_prediction_confidence(self, row: pd.Series) -> float:
        """
        Calcula confiança da predição sazonal
        """
        # Fatores que aumentam confiança
        confidence_factors = []
        
        # Padrões históricos consistentes
        if row['search_volume_std_7'] < row['search_volume_ma_7'] * 0.2:
            confidence_factors.append(0.3)
        
        # Padrões temporais claros
        if row['is_holiday'] == 1 or row['is_vacation_season'] == 1:
            confidence_factors.append(0.4)
        elif row['is_shopping_season'] == 1:
            confidence_factors.append(0.3)
        
        # Padrões de comportamento consistentes
        if row['weather_impact'] > 0.7:
            confidence_factors.append(0.2)
        
        # Calcular confiança total
        if confidence_factors:
            confidence = min(sum(confidence_factors), 1.0)
        else:
            confidence = 0.1
        
        return confidence
    
    def generate_seasonal_forecasts(self, data: pd.DataFrame, days_ahead: int = 90) -> pd.DataFrame:
        """
        Gera previsões sazonais
        """
        logger.info("Gerando previsões sazonais")
        
        forecasts = []
        
        # Agrupar por keyword/domínio
        for (keyword, domain), group_data in data.groupby(['keyword', 'domain']):
            if len(group_data) > 30:  # Pelo menos 30 dias de dados
                # Preparar dados históricos
                historical_data = group_data.sort_values('date')
                
                # Calcular padrões sazonais
                seasonal_patterns = self._extract_seasonal_patterns(historical_data)
                
                # Gerar previsões
                for i in range(days_ahead):
                    future_date = datetime.now() + timedelta(days=i)
                    
                    # Calcular previsão baseada em padrões sazonais
                    forecast = self._calculate_seasonal_forecast(
                        future_date, seasonal_patterns, historical_data
                    )
                    
                    forecast['keyword'] = keyword
                    forecast['domain'] = domain
                    forecast['date'] = future_date
                    forecast['forecast_type'] = 'seasonal'
                    
                    forecasts.append(forecast)
        
        return pd.DataFrame(forecasts)
    
    def _extract_seasonal_patterns(self, data: pd.DataFrame) -> Dict:
        """
        Extrai padrões sazonais dos dados históricos
        """
        patterns = {}
        
        # Padrões mensais
        monthly_avg = data.groupby(data['date'].dt.month).agg({
            'search_volume': 'mean',
            'organic_traffic': 'mean',
            'conversion_rate': 'mean',
            'cpc': 'mean'
        }).to_dict()
        
        # Padrões semanais
        weekly_avg = data.groupby(data['date'].dt.dayofweek).agg({
            'search_volume': 'mean',
            'organic_traffic': 'mean',
            'conversion_rate': 'mean'
        }).to_dict()
        
        # Padrões de feriados
        holiday_avg = data[data['is_holiday'] == 1].agg({
            'search_volume': 'mean',
            'organic_traffic': 'mean',
            'conversion_rate': 'mean'
        }).to_dict()
        
        patterns = {
            'monthly': monthly_avg,
            'weekly': weekly_avg,
            'holiday': holiday_avg
        }
        
        return patterns
    
    def _calculate_seasonal_forecast(self, date: datetime, patterns: Dict, historical_data: pd.DataFrame) -> Dict:
        """
        Calcula previsão sazonal para uma data específica
        """
        month = date.month
        day_of_week = date.weekday()
        is_holiday = date in pd.to_datetime(['2024-01-01', '2024-04-21', '2024-05-01', '2024-09-07',
                                           '2024-10-12', '2024-11-02', '2024-11-15', '2024-12-25'])
        
        # Calcular previsões baseadas em padrões
        forecast = {}
        
        # Previsão de volume de busca
        if 'search_volume' in patterns['monthly'] and month in patterns['monthly']['search_volume']:
            monthly_factor = patterns['monthly']['search_volume'][month]
            weekly_factor = patterns['weekly']['search_volume'].get(day_of_week, 1.0)
            holiday_factor = patterns['holiday']['search_volume'] if is_holiday else 1.0
            
            base_volume = historical_data['search_volume'].mean()
            forecast['predicted_search_volume'] = base_volume * monthly_factor * weekly_factor * holiday_factor
        else:
            forecast['predicted_search_volume'] = historical_data['search_volume'].mean()
        
        # Previsão de tráfego
        if 'organic_traffic' in patterns['monthly'] and month in patterns['monthly']['organic_traffic']:
            monthly_factor = patterns['monthly']['organic_traffic'][month]
            weekly_factor = patterns['weekly']['organic_traffic'].get(day_of_week, 1.0)
            holiday_factor = patterns['holiday']['organic_traffic'] if is_holiday else 1.0
            
            base_traffic = historical_data['organic_traffic'].mean()
            forecast['predicted_traffic'] = base_traffic * monthly_factor * weekly_factor * holiday_factor
        else:
            forecast['predicted_traffic'] = historical_data['organic_traffic'].mean()
        
        # Previsão de conversão
        if 'conversion_rate' in patterns['monthly'] and month in patterns['monthly']['conversion_rate']:
            monthly_factor = patterns['monthly']['conversion_rate'][month]
            weekly_factor = patterns['weekly']['conversion_rate'].get(day_of_week, 1.0)
            holiday_factor = patterns['holiday']['conversion_rate'] if is_holiday else 1.0
            
            base_conversion = historical_data['conversion_rate'].mean()
            forecast['predicted_conversion_rate'] = base_conversion * monthly_factor * weekly_factor * holiday_factor
        else:
            forecast['predicted_conversion_rate'] = historical_data['conversion_rate'].mean()
        
        return forecast
    
    def get_seasonal_insights(self, data: pd.DataFrame) -> Dict:
        """
        Gera insights sobre padrões sazonais
        """
        insights = {
            'total_patterns_detected': len(data[data['seasonal_pattern_detected'] == 1]),
            'pattern_detection_rate': data['seasonal_pattern_detected'].mean(),
            'pattern_types_distribution': data['pattern_type'].value_counts().to_dict(),
            'seasonality_levels_distribution': data['seasonality_level'].value_counts().to_dict(),
            'keywords_with_patterns': data[data['seasonal_pattern_detected'] == 1]['keyword'].nunique(),
            'domains_with_patterns': data[data['seasonal_pattern_detected'] == 1]['domain'].nunique(),
            'avg_prediction_confidence': data['prediction_confidence'].mean(),
            'high_seasonality_patterns': len(data[(data['seasonal_pattern_detected'] == 1) & 
                                                (data['seasonality_level'] == 'High Seasonality')]),
            'monthly_patterns': data.groupby('month')['seasonal_pattern_detected'].sum().to_dict(),
            'weekly_patterns': data.groupby('day_of_week')['seasonal_pattern_detected'].sum().to_dict()
        }
        
        return insights
    
    def save_model(self):
        """
        Salva modelo treinado
        """
        model_data = {
            'isolation_forest': self.isolation_forest,
            'classifier': self.classifier,
            'scaler': self.scaler,
            'seasonal_baselines': self.seasonal_baselines
        }
        joblib.dump(model_data, self.model_path)
        logger.info(f"Modelo salvo em: {self.model_path}")
    
    def load_model(self):
        """
        Carrega modelo treinado
        """
        try:
            model_data = joblib.load(self.model_path)
            self.isolation_forest = model_data['isolation_forest']
            self.classifier = model_data['classifier']
            self.scaler = model_data['scaler']
            self.seasonal_baselines = model_data['seasonal_baselines']
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'keyword': [f'keyword_{i % 50}' for i in range(n_samples)],
        'domain': [f'domain_{i % 20}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'search_volume': np.random.poisson(5000, n_samples),
        'organic_traffic': np.random.poisson(3000, n_samples),
        'conversion_rate': np.random.uniform(0.01, 0.05, n_samples),
        'click_through_rate': np.random.uniform(0.02, 0.08, n_samples),
        'bounce_rate': np.random.uniform(0.3, 0.8, n_samples),
        'time_on_site': np.random.uniform(60, 300, n_samples),
        'pages_per_session': np.random.uniform(1, 5, n_samples),
        'ranking_position': np.random.randint(1, 101, n_samples),
        'ranking_change': np.random.randint(-20, 21, n_samples),
        'ranking_volatility': np.random.uniform(0, 1, n_samples),
        'cpc': np.random.uniform(0.5, 10, n_samples),
        'cpm': np.random.uniform(2, 20, n_samples),
        'price_volatility': np.random.uniform(0, 1, n_samples),
        'competition_intensity': np.random.uniform(0, 1, n_samples),
        'competitor_activity': np.random.uniform(0, 1, n_samples),
        'market_saturation': np.random.uniform(0, 1, n_samples),
        'content_publishing_frequency': np.random.uniform(0, 1, n_samples),
        'content_updates': np.random.randint(0, 10, n_samples),
        'content_quality_score': np.random.uniform(0.3, 1.0, n_samples),
        'social_media_activity': np.random.uniform(0, 1, n_samples),
        'email_campaigns': np.random.uniform(0, 1, n_samples),
        'paid_advertising': np.random.uniform(0, 1, n_samples),
        'influencer_marketing': np.random.uniform(0, 1, n_samples),
        'industry_events': np.random.randint(0, 2, n_samples),
        'product_launches': np.random.randint(0, 2, n_samples),
        'news_coverage': np.random.uniform(0, 1, n_samples),
        'viral_content': np.random.randint(0, 2, n_samples),
        'weather_impact': np.random.uniform(0, 1, n_samples),
        'temperature': np.random.uniform(10, 35, n_samples),
        'precipitation': np.random.uniform(0, 1, n_samples),
        'economic_index': np.random.uniform(80, 120, n_samples),
        'consumer_confidence': np.random.uniform(30, 70, n_samples),
        'unemployment_rate': np.random.uniform(0.03, 0.08, n_samples),
        'inflation_rate': np.random.uniform(0.01, 0.08, n_samples)
    })
    
    # Inicializar detector
    detector = SeasonalPatternDetector()
    
    # Classificar padrões
    results = detector.classify_pattern_types(sample_data)
    
    # Gerar previsões
    forecasts = detector.generate_seasonal_forecasts(sample_data.head(100))
    
    # Gerar insights
    insights = detector.get_seasonal_insights(results)
    
    print("=== INSIGHTS DE DETECÇÃO DE PADRÕES SAZONAIS ===")
    print(f"Total de padrões detectados: {insights['total_patterns_detected']}")
    print(f"Taxa de detecção de padrões: {insights['pattern_detection_rate']:.2%}")
    print(f"Keywords com padrões: {insights['keywords_with_patterns']}")
    print(f"Domínios com padrões: {insights['domains_with_patterns']}")
    print(f"Confiança média de predição: {insights['avg_prediction_confidence']:.2f}")
    print(f"Padrões de alta sazonalidade: {insights['high_seasonality_patterns']}")
    
    print("\n=== DISTRIBUIÇÃO DE TIPOS DE PADRÃO ===")
    for pattern_type, count in insights['pattern_types_distribution'].items():
        print(f"{pattern_type}: {count}")
    
    print("\n=== PADRÕES MENSAIS ===")
    for month, count in insights['monthly_patterns'].items():
        month_name = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                     'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][month-1]
        print(f"{month_name}: {count} padrões") 