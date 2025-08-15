"""
Sistema de Análise Preditiva de Competição usando Machine Learning
Monitora movimentos de concorrentes e prediz estratégias futuras
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.cluster import KMeans
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitionAnalyzer:
    """
    Sistema de análise preditiva de competição
    """
    
    def __init__(self, model_path: str = "models/competition_analyzer.pkl"):
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
        self.competitor_clusters = {}
        self.threat_levels = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para análise de competição
        """
        features = data.copy()
        
        # Features de domínio
        features['domain_authority'] = features['domain_authority'].fillna(0)
        features['page_authority'] = features['page_authority'].fillna(0)
        features['spam_score'] = features['spam_score'].fillna(0)
        features['trust_flow'] = features['trust_flow'].fillna(0)
        features['citation_flow'] = features['citation_flow'].fillna(0)
        
        # Features de backlinks
        features['total_backlinks'] = features['total_backlinks'].fillna(0)
        features['unique_domains'] = features['unique_domains'].fillna(0)
        features['followed_backlinks'] = features['followed_backlinks'].fillna(0)
        features['nofollow_backlinks'] = features['nofollow_backlinks'].fillna(0)
        features['gov_backlinks'] = features['gov_backlinks'].fillna(0)
        features['edu_backlinks'] = features['edu_backlinks'].fillna(0)
        
        # Features de conteúdo
        features['content_length'] = features['content_length'].fillna(0)
        features['content_freshness'] = features['content_freshness'].fillna(0)
        features['content_quality_score'] = features['content_quality_score'].fillna(0)
        features['keyword_density'] = features['keyword_density'].fillna(0)
        features['content_updates_frequency'] = features['content_updates_frequency'].fillna(0)
        
        # Features de SEO técnico
        features['page_speed'] = features['page_speed'].fillna(3.0)
        features['mobile_friendly'] = features['mobile_friendly'].fillna(0)
        features['ssl_secure'] = features['ssl_secure'].fillna(0)
        features['structured_data'] = features['structured_data'].fillna(0)
        features['internal_links'] = features['internal_links'].fillna(0)
        features['external_links'] = features['external_links'].fillna(0)
        
        # Features de ranking
        features['ranking_position'] = features['ranking_position'].fillna(100)
        features['ranking_change'] = features['ranking_change'].fillna(0)
        features['ranking_velocity'] = features['ranking_velocity'].fillna(0)
        features['featured_snippets'] = features['featured_snippets'].fillna(0)
        features['local_pack'] = features['local_pack'].fillna(0)
        
        # Features de tráfego
        features['organic_traffic'] = features['organic_traffic'].fillna(0)
        features['traffic_change'] = features['traffic_change'].fillna(0)
        features['click_through_rate'] = features['click_through_rate'].fillna(0)
        features['bounce_rate'] = features['bounce_rate'].fillna(0.5)
        features['time_on_site'] = features['time_on_site'].fillna(60)
        
        # Features de marketing
        features['social_media_presence'] = features['social_media_presence'].fillna(0)
        features['email_marketing'] = features['email_marketing'].fillna(0)
        features['paid_advertising'] = features['paid_advertising'].fillna(0)
        features['influencer_marketing'] = features['influencer_marketing'].fillna(0)
        features['content_marketing'] = features['content_marketing'].fillna(0)
        
        # Features de negócio
        features['company_size'] = features['company_size'].fillna('unknown')
        features['industry'] = features['industry'].fillna('unknown')
        features['market_cap'] = features['market_cap'].fillna(0)
        features['revenue'] = features['revenue'].fillna(0)
        features['funding_rounds'] = features['funding_rounds'].fillna(0)
        
        # Features de atividade
        features['content_publishing_frequency'] = features['content_publishing_frequency'].fillna(0)
        features['link_building_activity'] = features['link_building_activity'].fillna(0)
        features['social_media_activity'] = features['social_media_activity'].fillna(0)
        features['product_updates'] = features['product_updates'].fillna(0)
        features['partnership_announcements'] = features['partnership_announcements'].fillna(0)
        
        # Features de ameaça
        features['keyword_overlap'] = features['keyword_overlap'].fillna(0)
        features['content_similarity'] = features['content_similarity'].fillna(0)
        features['backlink_competition'] = features['backlink_competition'].fillna(0)
        features['market_share_competition'] = features['market_share_competition'].fillna(0)
        features['talent_poaching'] = features['talent_poaching'].fillna(0)
        
        # Features temporais
        features['date'] = pd.to_datetime(features['date'])
        features['days_since_last_update'] = (datetime.now() - features['date']).dt.days
        features['update_frequency'] = features['update_frequency'].fillna(0)
        
        # Encoding de variáveis categóricas
        categorical_features = ['company_size', 'industry', 'competitor_type']
        for feature in categorical_features:
            if feature in features.columns:
                if feature not in self.label_encoders:
                    self.label_encoders[feature] = LabelEncoder()
                    features[feature] = self.label_encoders[feature].fit_transform(
                        features[feature]
                    )
                else:
                    features[feature] = self.label_encoders[feature].transform(
                        features[feature]
                    )
        
        return features
    
    def cluster_competitors(self, data: pd.DataFrame, n_clusters: int = 5) -> Dict:
        """
        Agrupa competidores em clusters baseado em características similares
        """
        logger.info("Agrupando competidores em clusters")
        
        # Preparar features para clustering
        features = self.prepare_features(data)
        
        # Features para clustering
        cluster_features = [
            'domain_authority', 'page_authority', 'total_backlinks', 'unique_domains',
            'content_quality_score', 'organic_traffic', 'ranking_position',
            'social_media_presence', 'content_publishing_frequency', 'market_cap'
        ]
        
        X_cluster = features[cluster_features].fillna(0)
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X_cluster)
        
        # Aplicar K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Adicionar labels aos dados
        features['cluster'] = cluster_labels
        
        # Analisar clusters
        cluster_analysis = {}
        for cluster_id in range(n_clusters):
            cluster_data = features[features['cluster'] == cluster_id]
            
            cluster_analysis[cluster_id] = {
                'size': len(cluster_data),
                'avg_domain_authority': cluster_data['domain_authority'].mean(),
                'avg_organic_traffic': cluster_data['organic_traffic'].mean(),
                'avg_ranking_position': cluster_data['ranking_position'].mean(),
                'threat_level': self._calculate_threat_level(cluster_data),
                'competitors': cluster_data['competitor_name'].tolist()
            }
        
        self.competitor_clusters = cluster_analysis
        
        return cluster_analysis
    
    def _calculate_threat_level(self, cluster_data: pd.DataFrame) -> str:
        """
        Calcula nível de ameaça de um cluster
        """
        avg_da = cluster_data['domain_authority'].mean()
        avg_traffic = cluster_data['organic_traffic'].mean()
        avg_ranking = cluster_data['ranking_position'].mean()
        
        threat_score = (avg_da / 100) * 0.4 + (avg_traffic / 10000) * 0.4 + (1 - avg_ranking / 100) * 0.2
        
        if threat_score > 0.7:
            return 'High'
        elif threat_score > 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def train_model(self, training_data: pd.DataFrame) -> Dict:
        """
        Treina modelos de análise preditiva de competição
        """
        logger.info("Iniciando treinamento dos modelos de análise de competição")
        
        # Agrupar competidores
        self.cluster_competitors(training_data)
        
        # Preparar dados
        features = self.prepare_features(training_data)
        
        # Features para treinamento
        feature_columns = [
            'domain_authority', 'page_authority', 'spam_score', 'trust_flow',
            'citation_flow', 'total_backlinks', 'unique_domains', 'followed_backlinks',
            'nofollow_backlinks', 'gov_backlinks', 'edu_backlinks', 'content_length',
            'content_freshness', 'content_quality_score', 'keyword_density',
            'content_updates_frequency', 'page_speed', 'mobile_friendly', 'ssl_secure',
            'structured_data', 'internal_links', 'external_links', 'ranking_position',
            'ranking_change', 'ranking_velocity', 'featured_snippets', 'local_pack',
            'organic_traffic', 'traffic_change', 'click_through_rate', 'bounce_rate',
            'time_on_site', 'social_media_presence', 'email_marketing', 'paid_advertising',
            'influencer_marketing', 'content_marketing', 'company_size', 'industry',
            'market_cap', 'revenue', 'funding_rounds', 'content_publishing_frequency',
            'link_building_activity', 'social_media_activity', 'product_updates',
            'partnership_announcements', 'keyword_overlap', 'content_similarity',
            'backlink_competition', 'market_share_competition', 'talent_poaching',
            'days_since_last_update', 'update_frequency'
        ]
        
        X = features[feature_columns]
        y = features['threat_score']  # Score de ameaça calculado
        
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
    
    def predict_competition_moves(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prediz próximos movimentos dos competidores
        """
        if self.best_model is None:
            raise ValueError("Modelo não treinado. Execute train_model() primeiro.")
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para predição
        feature_columns = [
            'domain_authority', 'page_authority', 'spam_score', 'trust_flow',
            'citation_flow', 'total_backlinks', 'unique_domains', 'followed_backlinks',
            'nofollow_backlinks', 'gov_backlinks', 'edu_backlinks', 'content_length',
            'content_freshness', 'content_quality_score', 'keyword_density',
            'content_updates_frequency', 'page_speed', 'mobile_friendly', 'ssl_secure',
            'structured_data', 'internal_links', 'external_links', 'ranking_position',
            'ranking_change', 'ranking_velocity', 'featured_snippets', 'local_pack',
            'organic_traffic', 'traffic_change', 'click_through_rate', 'bounce_rate',
            'time_on_site', 'social_media_presence', 'email_marketing', 'paid_advertising',
            'influencer_marketing', 'content_marketing', 'company_size', 'industry',
            'market_cap', 'revenue', 'funding_rounds', 'content_publishing_frequency',
            'link_building_activity', 'social_media_activity', 'product_updates',
            'partnership_announcements', 'keyword_overlap', 'content_similarity',
            'backlink_competition', 'market_share_competition', 'talent_poaching',
            'days_since_last_update', 'update_frequency'
        ]
        
        X = features[feature_columns]
        
        # Remover linhas com valores NaN
        mask = ~X.isnull().any(axis=1)
        X = X[mask]
        data_clean = data[mask].copy()
        
        # Normalizar features
        X_scaled = self.scaler.transform(X)
        
        # Predições
        threat_scores = self.best_model.predict(X_scaled)
        
        # Adicionar predições aos dados
        data_clean['predicted_threat_score'] = threat_scores
        data_clean['threat_level'] = self._score_to_threat_level(threat_scores)
        data_clean['predicted_moves'] = self._predict_moves(data_clean, threat_scores)
        
        return data_clean
    
    def _score_to_threat_level(self, scores: np.ndarray) -> List[str]:
        """
        Converte scores de ameaça em níveis de ameaça
        """
        levels = []
        for score in scores:
            if score > 0.7:
                levels.append('High')
            elif score > 0.4:
                levels.append('Medium')
            else:
                levels.append('Low')
        return levels
    
    def _predict_moves(self, data: pd.DataFrame, threat_scores: np.ndarray) -> List[str]:
        """
        Prediz próximos movimentos baseado no score de ameaça
        """
        moves = []
        for idx, score in enumerate(threat_scores):
            competitor_data = data.iloc[idx]
            
            if score > 0.8:
                moves.append('Aggressive content marketing and link building')
            elif score > 0.6:
                moves.append('Increased social media activity and partnerships')
            elif score > 0.4:
                moves.append('Content updates and technical improvements')
            else:
                moves.append('Maintain current strategy')
        
        return moves
    
    def detect_anomalies(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta movimentos anômalos dos competidores
        """
        logger.info("Detectando movimentos anômalos")
        
        # Calcular estatísticas por competidor
        competitor_stats = data.groupby('competitor_name').agg({
            'ranking_change': ['mean', 'std'],
            'traffic_change': ['mean', 'std'],
            'content_updates_frequency': ['mean', 'std'],
            'link_building_activity': ['mean', 'std']
        }).reset_index()
        
        # Detectar anomalias
        anomalies = []
        for _, row in data.iterrows():
            competitor = row['competitor_name']
            competitor_stat = competitor_stats[competitor_stats['competitor_name'] == competitor]
            
            if len(competitor_stat) > 0:
                # Verificar se ranking change é anômalo
                ranking_mean = competitor_stat[('ranking_change', 'mean')].iloc[0]
                ranking_std = competitor_stat[('ranking_change', 'std')].iloc[0]
                
                if abs(row['ranking_change'] - ranking_mean) > 2 * ranking_std:
                    anomalies.append({
                        'competitor': competitor,
                        'anomaly_type': 'ranking_change',
                        'value': row['ranking_change'],
                        'expected_range': f"{ranking_mean - 2*ranking_std:.1f} to {ranking_mean + 2*ranking_std:.1f}"
                    })
        
        return pd.DataFrame(anomalies)
    
    def get_competition_insights(self, predictions: pd.DataFrame) -> Dict:
        """
        Gera insights sobre a competição
        """
        insights = {
            'total_competitors': len(predictions),
            'high_threat_competitors': len(predictions[predictions['threat_level'] == 'High']),
            'medium_threat_competitors': len(predictions[predictions['threat_level'] == 'Medium']),
            'low_threat_competitors': len(predictions[predictions['threat_level'] == 'Low']),
            'avg_threat_score': predictions['predicted_threat_score'].mean(),
            'top_threats': predictions.nlargest(10, 'predicted_threat_score')[['competitor_name', 'predicted_threat_score', 'threat_level']],
            'competitors_by_cluster': predictions.groupby('cluster').size().to_dict(),
            'threat_by_industry': predictions.groupby('industry')['predicted_threat_score'].mean(),
            'threat_by_size': predictions.groupby('company_size')['predicted_threat_score'].mean()
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
            'competitor_clusters': self.competitor_clusters
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
            self.competitor_clusters = model_data['competitor_clusters']
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 500
    
    sample_data = pd.DataFrame({
        'competitor_name': [f'competitor_{i}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'threat_score': np.random.uniform(0, 1, n_samples),
        'domain_authority': np.random.uniform(0, 100, n_samples),
        'page_authority': np.random.uniform(0, 100, n_samples),
        'spam_score': np.random.uniform(0, 17, n_samples),
        'trust_flow': np.random.uniform(0, 100, n_samples),
        'citation_flow': np.random.uniform(0, 100, n_samples),
        'total_backlinks': np.random.randint(0, 10000, n_samples),
        'unique_domains': np.random.randint(0, 1000, n_samples),
        'followed_backlinks': np.random.randint(0, 8000, n_samples),
        'nofollow_backlinks': np.random.randint(0, 2000, n_samples),
        'gov_backlinks': np.random.randint(0, 50, n_samples),
        'edu_backlinks': np.random.randint(0, 30, n_samples),
        'content_length': np.random.randint(100, 5000, n_samples),
        'content_freshness': np.random.uniform(0, 1, n_samples),
        'content_quality_score': np.random.uniform(0, 1, n_samples),
        'keyword_density': np.random.uniform(0.5, 5, n_samples),
        'content_updates_frequency': np.random.uniform(0, 1, n_samples),
        'page_speed': np.random.uniform(1, 5, n_samples),
        'mobile_friendly': np.random.choice([0, 1], n_samples),
        'ssl_secure': np.random.choice([0, 1], n_samples),
        'structured_data': np.random.choice([0, 1], n_samples),
        'internal_links': np.random.randint(0, 100, n_samples),
        'external_links': np.random.randint(0, 50, n_samples),
        'ranking_position': np.random.randint(1, 101, n_samples),
        'ranking_change': np.random.randint(-20, 21, n_samples),
        'ranking_velocity': np.random.uniform(-5, 5, n_samples),
        'featured_snippets': np.random.choice([0, 1], n_samples),
        'local_pack': np.random.choice([0, 1], n_samples),
        'organic_traffic': np.random.randint(0, 50000, n_samples),
        'traffic_change': np.random.uniform(-0.5, 0.5, n_samples),
        'click_through_rate': np.random.uniform(0, 0.1, n_samples),
        'bounce_rate': np.random.uniform(0.2, 0.8, n_samples),
        'time_on_site': np.random.uniform(30, 300, n_samples),
        'social_media_presence': np.random.uniform(0, 1, n_samples),
        'email_marketing': np.random.uniform(0, 1, n_samples),
        'paid_advertising': np.random.uniform(0, 1, n_samples),
        'influencer_marketing': np.random.uniform(0, 1, n_samples),
        'content_marketing': np.random.uniform(0, 1, n_samples),
        'company_size': np.random.choice(['startup', 'sme', 'enterprise'], n_samples),
        'industry': np.random.choice(['tech', 'health', 'finance', 'ecommerce'], n_samples),
        'market_cap': np.random.uniform(0, 1000000000, n_samples),
        'revenue': np.random.uniform(0, 100000000, n_samples),
        'funding_rounds': np.random.randint(0, 10, n_samples),
        'content_publishing_frequency': np.random.uniform(0, 1, n_samples),
        'link_building_activity': np.random.uniform(0, 1, n_samples),
        'social_media_activity': np.random.uniform(0, 1, n_samples),
        'product_updates': np.random.uniform(0, 1, n_samples),
        'partnership_announcements': np.random.uniform(0, 1, n_samples),
        'keyword_overlap': np.random.uniform(0, 1, n_samples),
        'content_similarity': np.random.uniform(0, 1, n_samples),
        'backlink_competition': np.random.uniform(0, 1, n_samples),
        'market_share_competition': np.random.uniform(0, 1, n_samples),
        'talent_poaching': np.random.uniform(0, 1, n_samples),
        'update_frequency': np.random.uniform(0, 1, n_samples)
    })
    
    # Inicializar analisador
    analyzer = CompetitionAnalyzer()
    
    # Treinar modelo
    results = analyzer.train_model(sample_data)
    
    # Fazer predições
    predictions = analyzer.predict_competition_moves(sample_data.head(100))
    
    # Detectar anomalias
    anomalies = analyzer.detect_anomalies(sample_data.head(100))
    
    # Gerar insights
    insights = analyzer.get_competition_insights(predictions)
    
    print("=== INSIGHTS DE ANÁLISE DE COMPETIÇÃO ===")
    print(f"Total de competidores: {insights['total_competitors']}")
    print(f"Competidores de alta ameaça: {insights['high_threat_competitors']}")
    print(f"Competidores de média ameaça: {insights['medium_threat_competitors']}")
    print(f"Score de ameaça médio: {insights['avg_threat_score']:.3f}")
    
    print("\n=== ANOMALIAS DETECTADAS ===")
    if len(anomalies) > 0:
        for _, anomaly in anomalies.iterrows():
            print(f"{anomaly['competitor']}: {anomaly['anomaly_type']} = {anomaly['value']}")
    else:
        print("Nenhuma anomalia detectada") 