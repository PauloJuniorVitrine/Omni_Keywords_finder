"""
Sistema de Predição de Tráfego usando Machine Learning
Prediz volume de tráfego futuro baseado em dados históricos e fatores externos
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrafficPredictor:
    """
    Sistema de predição de tráfego para websites
    """
    
    def __init__(self, model_path: str = "models/traffic_predictor.pkl"):
        self.model_path = model_path
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression(),
            'ridge': Ridge(alpha=1.0)
        }
        self.best_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_importance = {}
        self.seasonal_patterns = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para predição de tráfego
        """
        features = data.copy()
        
        # Features temporais
        features['date'] = pd.to_datetime(features['date'])
        features['year'] = features['date'].dt.year
        features['month'] = features['date'].dt.month
        features['day'] = features['date'].dt.day
        features['day_of_week'] = features['date'].dt.dayofweek
        features['day_of_year'] = features['date'].dt.dayofyear
        features['week'] = features['date'].dt.isocalendar().week
        features['quarter'] = features['date'].dt.quarter
        
        # Features sazonais
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        features['is_holiday'] = self._is_holiday(features['date'])
        features['is_school_holiday'] = self._is_school_holiday(features['date'])
        
        # Features de ranking
        features['ranking_position'] = features['ranking_position'].fillna(100)
        features['ranking_change'] = features['ranking_change'].fillna(0)
        features['ranking_velocity'] = features['ranking_velocity'].fillna(0)
        
        # Features de conteúdo
        features['content_age_days'] = features['content_age_days'].fillna(0)
        features['content_updates'] = features['content_updates'].fillna(0)
        features['content_quality_score'] = features['content_quality_score'].fillna(0)
        
        # Features de marketing
        features['social_media_posts'] = features['social_media_posts'].fillna(0)
        features['email_campaigns'] = features['email_campaigns'].fillna(0)
        features['paid_ads_budget'] = features['paid_ads_budget'].fillna(0)
        features['backlink_acquisitions'] = features['backlink_acquisitions'].fillna(0)
        
        # Features de competição
        features['competitor_activity'] = features['competitor_activity'].fillna(0)
        features['market_share'] = features['market_share'].fillna(0)
        features['competition_intensity'] = features['competition_intensity'].fillna(0)
        
        # Features de eventos
        features['industry_events'] = features['industry_events'].fillna(0)
        features['product_launches'] = features['product_launches'].fillna(0)
        features['news_coverage'] = features['news_coverage'].fillna(0)
        
        # Features de performance técnica
        features['page_load_time'] = features['page_load_time'].fillna(3.0)
        features['mobile_performance'] = features['mobile_performance'].fillna(0.8)
        features['core_web_vitals'] = features['core_web_vitals'].fillna(0.8)
        
        # Features de engajamento
        features['bounce_rate'] = features['bounce_rate'].fillna(0.5)
        features['time_on_site'] = features['time_on_site'].fillna(120)
        features['pages_per_session'] = features['pages_per_session'].fillna(2.0)
        features['conversion_rate'] = features['conversion_rate'].fillna(0.02)
        
        # Features de busca
        features['search_volume'] = features['search_volume'].fillna(1000)
        features['keyword_difficulty'] = features['keyword_difficulty'].fillna(50)
        features['search_trend'] = features['search_trend'].fillna(0)
        
        # Features econômicas (se disponíveis)
        features['economic_index'] = features['economic_index'].fillna(100)
        features['consumer_confidence'] = features['consumer_confidence'].fillna(50)
        
        # Encoding de variáveis categóricas
        categorical_features = ['content_type', 'industry', 'target_audience']
        for feature in categorical_features:
            if feature in features.columns:
                if feature not in self.label_encoders:
                    self.label_encoders[feature] = LabelEncoder()
                    features[feature] = self.label_encoders[feature].fit_transform(
                        features[feature].fillna('unknown')
                    )
                else:
                    features[feature] = self.label_encoders[feature].transform(
                        features[feature].fillna('unknown')
                    )
        
        return features
    
    def _is_holiday(self, dates: pd.Series) -> pd.Series:
        """
        Identifica feriados (implementação simplificada)
        """
        # Feriados brasileiros principais (implementação básica)
        holidays = [
            '2024-01-01', '2024-04-21', '2024-05-01', '2024-09-07',
            '2024-10-12', '2024-11-02', '2024-11-15', '2024-12-25'
        ]
        holiday_dates = pd.to_datetime(holidays)
        return dates.isin(holiday_dates).astype(int)
    
    def _is_school_holiday(self, dates: pd.Series) -> pd.Series:
        """
        Identifica férias escolares (implementação simplificada)
        """
        # Férias escolares (janeiro, julho, dezembro)
        school_holidays = dates.dt.month.isin([1, 7, 12])
        return school_holidays.astype(int)
    
    def detect_seasonal_patterns(self, data: pd.DataFrame) -> Dict:
        """
        Detecta padrões sazonais nos dados de tráfego
        """
        logger.info("Detectando padrões sazonais")
        
        # Agrupar por diferentes períodos
        daily_avg = data.groupby(data['date'].dt.dayofweek)['traffic'].mean()
        monthly_avg = data.groupby(data['date'].dt.month)['traffic'].mean()
        quarterly_avg = data.groupby(data['date'].dt.quarter)['traffic'].mean()
        
        self.seasonal_patterns = {
            'daily': daily_avg.to_dict(),
            'monthly': monthly_avg.to_dict(),
            'quarterly': quarterly_avg.to_dict()
        }
        
        return self.seasonal_patterns
    
    def train_model(self, training_data: pd.DataFrame) -> Dict:
        """
        Treina modelos de predição de tráfego
        """
        logger.info("Iniciando treinamento dos modelos de predição de tráfego")
        
        # Detectar padrões sazonais
        self.detect_seasonal_patterns(training_data)
        
        # Preparar dados
        features = self.prepare_features(training_data)
        
        # Features para treinamento
        feature_columns = [
            'year', 'month', 'day', 'day_of_week', 'day_of_year', 'week', 'quarter',
            'is_weekend', 'is_holiday', 'is_school_holiday', 'ranking_position',
            'ranking_change', 'ranking_velocity', 'content_age_days', 'content_updates',
            'content_quality_score', 'social_media_posts', 'email_campaigns',
            'paid_ads_budget', 'backlink_acquisitions', 'competitor_activity',
            'market_share', 'competition_intensity', 'industry_events',
            'product_launches', 'news_coverage', 'page_load_time',
            'mobile_performance', 'core_web_vitals', 'bounce_rate',
            'time_on_site', 'pages_per_session', 'conversion_rate',
            'search_volume', 'keyword_difficulty', 'search_trend',
            'economic_index', 'consumer_confidence'
        ]
        
        # Adicionar features categóricas
        categorical_features = ['content_type', 'industry', 'target_audience']
        for feature in categorical_features:
            if feature in features.columns:
                feature_columns.append(feature)
        
        X = features[feature_columns]
        y = features['traffic']
        
        # Remover linhas com valores NaN
        mask = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[mask]
        y = y[mask]
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Treinar modelos
        results = {}
        for name, model in self.models.items():
            logger.info(f"Treinando modelo: {name}")
            
            # Treinar modelo
            model.fit(X_train, y_train)
            
            # Predições
            y_pred = model.predict(X_test)
            
            # Métricas
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
            
            results[name] = {
                'model': model,
                'mse': mse,
                'mae': mae,
                'r2': r2,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            # Feature importance (se disponível)
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = dict(zip(feature_columns, model.feature_importances_))
        
        # Selecionar melhor modelo
        best_model_name = max(results.keys(), key=lambda k: results[k]['cv_mean'])
        self.best_model = results[best_model_name]['model']
        
        logger.info(f"Melhor modelo: {best_model_name}")
        logger.info(f"R² Score: {results[best_model_name]['r2']:.4f}")
        logger.info(f"MAE: {results[best_model_name]['mae']:.2f}")
        
        # Salvar modelo
        self.save_model()
        
        return results
    
    def predict_traffic(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prediz tráfego futuro
        """
        if self.best_model is None:
            raise ValueError("Modelo não treinado. Execute train_model() primeiro.")
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para predição
        feature_columns = [
            'year', 'month', 'day', 'day_of_week', 'day_of_year', 'week', 'quarter',
            'is_weekend', 'is_holiday', 'is_school_holiday', 'ranking_position',
            'ranking_change', 'ranking_velocity', 'content_age_days', 'content_updates',
            'content_quality_score', 'social_media_posts', 'email_campaigns',
            'paid_ads_budget', 'backlink_acquisitions', 'competitor_activity',
            'market_share', 'competition_intensity', 'industry_events',
            'product_launches', 'news_coverage', 'page_load_time',
            'mobile_performance', 'core_web_vitals', 'bounce_rate',
            'time_on_site', 'pages_per_session', 'conversion_rate',
            'search_volume', 'keyword_difficulty', 'search_trend',
            'economic_index', 'consumer_confidence'
        ]
        
        # Adicionar features categóricas
        categorical_features = ['content_type', 'industry', 'target_audience']
        for feature in categorical_features:
            if feature in features.columns:
                feature_columns.append(feature)
        
        X = features[feature_columns]
        
        # Remover linhas com valores NaN
        mask = ~X.isnull().any(axis=1)
        X = X[mask]
        data_clean = data[mask].copy()
        
        # Normalizar features
        X_scaled = self.scaler.transform(X)
        
        # Predições
        predictions = self.best_model.predict(X_scaled)
        
        # Aplicar ajustes sazonais
        seasonal_adjustments = self._apply_seasonal_adjustments(data_clean)
        predictions = predictions * seasonal_adjustments
        
        # Adicionar predições aos dados
        data_clean['predicted_traffic'] = predictions
        data_clean['traffic_confidence'] = self._calculate_confidence(X_scaled)
        data_clean['seasonal_factor'] = seasonal_adjustments
        
        return data_clean
    
    def _apply_seasonal_adjustments(self, data: pd.DataFrame) -> np.ndarray:
        """
        Aplica ajustes sazonais às predições
        """
        adjustments = np.ones(len(data))
        
        for idx, row in data.iterrows():
            # Ajuste diário
            day_of_week = row['date'].dayofweek
            if day_of_week in self.seasonal_patterns['daily']:
                daily_factor = self.seasonal_patterns['daily'][day_of_week]
                adjustments[idx] *= daily_factor / np.mean(list(self.seasonal_patterns['daily'].values()))
            
            # Ajuste mensal
            month = row['date'].month
            if month in self.seasonal_patterns['monthly']:
                monthly_factor = self.seasonal_patterns['monthly'][month]
                adjustments[idx] *= monthly_factor / np.mean(list(self.seasonal_patterns['monthly'].values()))
        
        return adjustments
    
    def _calculate_confidence(self, X_scaled: np.ndarray) -> np.ndarray:
        """
        Calcula nível de confiança das predições
        """
        if hasattr(self.best_model, 'predict_proba'):
            return np.max(self.best_model.predict_proba(X_scaled), axis=1)
        else:
            return 1.0 - np.linalg.norm(X_scaled, axis=1) / np.max(np.linalg.norm(X_scaled, axis=1))
    
    def predict_traffic_trends(self, data: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
        """
        Prediz tendências de tráfego para os próximos dias
        """
        predictions = []
        
        for i in range(days_ahead):
            future_date = datetime.now() + timedelta(days=i)
            
            # Criar dados futuros
            future_data = data.copy()
            future_data['date'] = future_date
            
            # Predizer tráfego
            pred = self.predict_traffic(future_data)
            predictions.append(pred)
        
        # Combinar predições
        all_predictions = pd.concat(predictions, ignore_index=True)
        
        # Calcular tendências
        all_predictions['traffic_change'] = all_predictions.groupby('page_url')['predicted_traffic'].diff()
        all_predictions['growth_rate'] = all_predictions['traffic_change'] / all_predictions['predicted_traffic'].shift(1)
        
        return all_predictions
    
    def get_traffic_insights(self, predictions: pd.DataFrame) -> Dict:
        """
        Gera insights sobre as predições de tráfego
        """
        insights = {
            'total_pages': len(predictions),
            'total_predicted_traffic': predictions['predicted_traffic'].sum(),
            'avg_traffic_per_page': predictions['predicted_traffic'].mean(),
            'traffic_growth': (predictions['predicted_traffic'] - predictions['traffic']).sum(),
            'growth_rate': ((predictions['predicted_traffic'] - predictions['traffic']) / predictions['traffic']).mean(),
            'high_traffic_pages': predictions.nlargest(10, 'predicted_traffic')[['page_url', 'predicted_traffic', 'traffic_confidence']],
            'low_traffic_pages': predictions.nsmallest(10, 'predicted_traffic')[['page_url', 'predicted_traffic', 'traffic_confidence']],
            'seasonal_impact': predictions['seasonal_factor'].describe(),
            'confidence_distribution': predictions['traffic_confidence'].describe()
        }
        
        return insights
    
    def save_model(self):
        """
        Salva modelo treinado
        """
        model_data = {
            'best_model': self.best_model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_importance': self.feature_importance,
            'seasonal_patterns': self.seasonal_patterns
        }
        joblib.dump(model_data, self.model_path)
        logger.info(f"Modelo salvo em: {self.model_path}")
    
    def load_model(self):
        """
        Carrega modelo treinado
        """
        try:
            model_data = joblib.load(self.model_path)
            self.best_model = model_data['best_model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_importance = model_data['feature_importance']
            self.seasonal_patterns = model_data['seasonal_patterns']
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'page_url': [f'page_{i}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'traffic': np.random.poisson(1000, n_samples),
        'ranking_position': np.random.randint(1, 101, n_samples),
        'ranking_change': np.random.randint(-10, 11, n_samples),
        'ranking_velocity': np.random.uniform(-5, 5, n_samples),
        'content_age_days': np.random.randint(0, 365, n_samples),
        'content_updates': np.random.randint(0, 10, n_samples),
        'content_quality_score': np.random.uniform(0, 1, n_samples),
        'social_media_posts': np.random.randint(0, 5, n_samples),
        'email_campaigns': np.random.randint(0, 3, n_samples),
        'paid_ads_budget': np.random.uniform(0, 1000, n_samples),
        'backlink_acquisitions': np.random.randint(0, 20, n_samples),
        'competitor_activity': np.random.uniform(0, 1, n_samples),
        'market_share': np.random.uniform(0, 1, n_samples),
        'competition_intensity': np.random.uniform(0, 1, n_samples),
        'industry_events': np.random.randint(0, 2, n_samples),
        'product_launches': np.random.randint(0, 2, n_samples),
        'news_coverage': np.random.randint(0, 3, n_samples),
        'page_load_time': np.random.uniform(1, 5, n_samples),
        'mobile_performance': np.random.uniform(0.5, 1, n_samples),
        'core_web_vitals': np.random.uniform(0.5, 1, n_samples),
        'bounce_rate': np.random.uniform(0.2, 0.8, n_samples),
        'time_on_site': np.random.uniform(30, 300, n_samples),
        'pages_per_session': np.random.uniform(1, 5, n_samples),
        'conversion_rate': np.random.uniform(0.01, 0.05, n_samples),
        'search_volume': np.random.randint(100, 10000, n_samples),
        'keyword_difficulty': np.random.uniform(0, 100, n_samples),
        'search_trend': np.random.uniform(-0.2, 0.2, n_samples),
        'economic_index': np.random.uniform(80, 120, n_samples),
        'consumer_confidence': np.random.uniform(40, 60, n_samples),
        'content_type': np.random.choice(['blog', 'product', 'landing'], n_samples),
        'industry': np.random.choice(['tech', 'health', 'finance'], n_samples),
        'target_audience': np.random.choice(['b2b', 'b2c', 'mixed'], n_samples)
    })
    
    # Inicializar preditor
    predictor = TrafficPredictor()
    
    # Treinar modelo
    results = predictor.train_model(sample_data)
    
    # Fazer predições
    predictions = predictor.predict_traffic(sample_data.head(100))
    
    # Gerar insights
    insights = predictor.get_traffic_insights(predictions)
    
    print("=== INSIGHTS DE PREDIÇÃO DE TRÁFEGO ===")
    print(f"Total de páginas: {insights['total_pages']}")
    print(f"Tráfego total previsto: {insights['total_predicted_traffic']:.0f}")
    print(f"Tráfego médio por página: {insights['avg_traffic_per_page']:.0f}")
    print(f"Crescimento total esperado: {insights['traffic_growth']:.0f}")
    print(f"Taxa de crescimento média: {insights['growth_rate']:.2%}") 