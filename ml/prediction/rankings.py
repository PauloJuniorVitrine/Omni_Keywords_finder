"""
Sistema de Predição de Rankings usando Machine Learning
Prediz rankings futuros baseado em dados históricos e features relevantes
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RankingPredictor:
    """
    Sistema de predição de rankings para keywords
    """
    
    def __init__(self, model_path: str = "models/ranking_predictor.pkl"):
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
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para predição de rankings
        """
        features = data.copy()
        
        # Features temporais
        features['month'] = pd.to_datetime(features['date']).dt.month
        features['day_of_week'] = pd.to_datetime(features['date']).dt.dayofweek
        features['quarter'] = pd.to_datetime(features['date']).dt.quarter
        
        # Features de competição
        features['competition_level'] = features['competition_score'].fillna(0)
        features['competitor_count'] = features['competitor_count'].fillna(0)
        
        # Features de conteúdo
        features['content_length'] = features['content_length'].fillna(0)
        features['keyword_density'] = features['keyword_density'].fillna(0)
        features['title_optimization'] = features['title_optimization'].fillna(0)
        
        # Features técnicas
        features['page_speed'] = features['page_speed'].fillna(0)
        features['mobile_friendly'] = features['mobile_friendly'].fillna(0)
        features['ssl_secure'] = features['ssl_secure'].fillna(0)
        
        # Features de backlinks
        features['backlink_count'] = features['backlink_count'].fillna(0)
        features['domain_authority'] = features['domain_authority'].fillna(0)
        features['page_authority'] = features['page_authority'].fillna(0)
        
        # Features de engajamento
        features['click_through_rate'] = features['click_through_rate'].fillna(0)
        features['bounce_rate'] = features['bounce_rate'].fillna(0)
        features['time_on_page'] = features['time_on_page'].fillna(0)
        
        # Features de busca
        features['search_volume'] = features['search_volume'].fillna(0)
        features['keyword_difficulty'] = features['keyword_difficulty'].fillna(0)
        
        # Encoding de variáveis categóricas
        categorical_features = ['keyword_type', 'content_type', 'language']
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
    
    def train_model(self, training_data: pd.DataFrame) -> Dict:
        """
        Treina modelos de predição de rankings
        """
        logger.info("Iniciando treinamento dos modelos de predição de rankings")
        
        # Preparar dados
        features = self.prepare_features(training_data)
        
        # Features para treinamento
        feature_columns = [
            'month', 'day_of_week', 'quarter', 'competition_level', 'competitor_count',
            'content_length', 'keyword_density', 'title_optimization', 'page_speed',
            'mobile_friendly', 'ssl_secure', 'backlink_count', 'domain_authority',
            'page_authority', 'click_through_rate', 'bounce_rate', 'time_on_page',
            'search_volume', 'keyword_difficulty'
        ]
        
        # Adicionar features categóricas
        categorical_features = ['keyword_type', 'content_type', 'language']
        for feature in categorical_features:
            if feature in features.columns:
                feature_columns.append(feature)
        
        X = features[feature_columns]
        y = features['ranking_position']
        
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
        logger.info(f"MAE: {results[best_model_name]['mae']:.4f}")
        
        # Salvar modelo
        self.save_model()
        
        return results
    
    def predict_rankings(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prediz rankings futuros
        """
        if self.best_model is None:
            raise ValueError("Modelo não treinado. Execute train_model() primeiro.")
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para predição
        feature_columns = [
            'month', 'day_of_week', 'quarter', 'competition_level', 'competitor_count',
            'content_length', 'keyword_density', 'title_optimization', 'page_speed',
            'mobile_friendly', 'ssl_secure', 'backlink_count', 'domain_authority',
            'page_authority', 'click_through_rate', 'bounce_rate', 'time_on_page',
            'search_volume', 'keyword_difficulty'
        ]
        
        # Adicionar features categóricas
        categorical_features = ['keyword_type', 'content_type', 'language']
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
        
        # Adicionar predições aos dados
        data_clean['predicted_ranking'] = predictions
        data_clean['ranking_confidence'] = self._calculate_confidence(X_scaled)
        
        return data_clean
    
    def _calculate_confidence(self, X_scaled: np.ndarray) -> np.ndarray:
        """
        Calcula nível de confiança das predições
        """
        if hasattr(self.best_model, 'predict_proba'):
            # Para modelos que suportam probabilidades
            return np.max(self.best_model.predict_proba(X_scaled), axis=1)
        else:
            # Para modelos que não suportam probabilidades
            # Usar distância do centro dos dados como proxy de confiança
            return 1.0 - np.linalg.norm(X_scaled, axis=1) / np.max(np.linalg.norm(X_scaled, axis=1))
    
    def get_feature_importance(self) -> Dict:
        """
        Retorna importância das features
        """
        return self.feature_importance
    
    def save_model(self):
        """
        Salva modelo treinado
        """
        model_data = {
            'best_model': self.best_model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_importance': self.feature_importance
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
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")
    
    def predict_ranking_trends(self, keyword_data: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
        """
        Prediz tendências de ranking para os próximos dias
        """
        predictions = []
        
        for i in range(days_ahead):
            future_date = datetime.now() + timedelta(days=i)
            
            # Criar dados futuros
            future_data = keyword_data.copy()
            future_data['date'] = future_date
            
            # Predizer ranking
            pred = self.predict_rankings(future_data)
            predictions.append(pred)
        
        # Combinar predições
        all_predictions = pd.concat(predictions, ignore_index=True)
        
        # Calcular tendências
        all_predictions['trend'] = all_predictions.groupby('keyword')['predicted_ranking'].diff()
        all_predictions['trend_direction'] = np.where(all_predictions['trend'] < 0, 'improving', 'declining')
        
        return all_predictions
    
    def get_ranking_insights(self, predictions: pd.DataFrame) -> Dict:
        """
        Gera insights sobre as predições de ranking
        """
        insights = {
            'total_keywords': len(predictions),
            'improving_keywords': len(predictions[predictions['predicted_ranking'] < predictions['ranking_position']]),
            'declining_keywords': len(predictions[predictions['predicted_ranking'] > predictions['ranking_position']]),
            'stable_keywords': len(predictions[predictions['predicted_ranking'] == predictions['ranking_position']]),
            'avg_improvement': (predictions['ranking_position'] - predictions['predicted_ranking']).mean(),
            'high_confidence_predictions': len(predictions[predictions['ranking_confidence'] > 0.8]),
            'top_improving_keywords': predictions.nsmallest(10, 'predicted_ranking')[['keyword', 'predicted_ranking', 'ranking_confidence']],
            'keywords_at_risk': predictions.nlargest(10, 'predicted_ranking')[['keyword', 'predicted_ranking', 'ranking_confidence']]
        }
        
        return insights


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'keyword': [f'keyword_{i}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'ranking_position': np.random.randint(1, 101, n_samples),
        'competition_score': np.random.uniform(0, 1, n_samples),
        'competitor_count': np.random.randint(0, 50, n_samples),
        'content_length': np.random.randint(100, 5000, n_samples),
        'keyword_density': np.random.uniform(0.5, 5, n_samples),
        'title_optimization': np.random.uniform(0, 1, n_samples),
        'page_speed': np.random.uniform(0.5, 1, n_samples),
        'mobile_friendly': np.random.choice([0, 1], n_samples),
        'ssl_secure': np.random.choice([0, 1], n_samples),
        'backlink_count': np.random.randint(0, 1000, n_samples),
        'domain_authority': np.random.uniform(0, 100, n_samples),
        'page_authority': np.random.uniform(0, 100, n_samples),
        'click_through_rate': np.random.uniform(0, 0.1, n_samples),
        'bounce_rate': np.random.uniform(0, 1, n_samples),
        'time_on_page': np.random.uniform(0, 300, n_samples),
        'search_volume': np.random.randint(0, 10000, n_samples),
        'keyword_difficulty': np.random.uniform(0, 100, n_samples),
        'keyword_type': np.random.choice(['informational', 'transactional', 'navigational'], n_samples),
        'content_type': np.random.choice(['blog', 'product', 'landing'], n_samples),
        'language': np.random.choice(['pt', 'en', 'es'], n_samples)
    })
    
    # Inicializar preditor
    predictor = RankingPredictor()
    
    # Treinar modelo
    results = predictor.train_model(sample_data)
    
    # Fazer predições
    predictions = predictor.predict_rankings(sample_data.head(100))
    
    # Gerar insights
    insights = predictor.get_ranking_insights(predictions)
    
    print("=== INSIGHTS DE PREDIÇÃO DE RANKINGS ===")
    print(f"Total de keywords: {insights['total_keywords']}")
    print(f"Keywords melhorando: {insights['improving_keywords']}")
    print(f"Keywords declinando: {insights['declining_keywords']}")
    print(f"Melhoria média esperada: {insights['avg_improvement']:.2f} posições")
    print(f"Predições de alta confiança: {insights['high_confidence_predictions']}") 