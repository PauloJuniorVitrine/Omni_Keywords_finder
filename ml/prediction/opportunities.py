"""
Sistema de Identificação de Oportunidades usando Machine Learning
Descobre keywords e nichos promissores baseado em análise preditiva
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

class OpportunityFinder:
    """
    Sistema de identificação de oportunidades de mercado
    """
    
    def __init__(self, model_path: str = "models/opportunity_finder.pkl"):
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
        self.opportunity_clusters = {}
        self.market_gaps = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para identificação de oportunidades
        """
        features = data.copy()
        
        # Features de volume de busca
        features['search_volume'] = features['search_volume'].fillna(0)
        features['search_volume_trend'] = features['search_volume_trend'].fillna(0)
        features['seasonal_search_pattern'] = features['seasonal_search_pattern'].fillna(0)
        features['long_tail_ratio'] = features['long_tail_ratio'].fillna(0)
        features['question_keywords'] = features['question_keywords'].fillna(0)
        
        # Features de dificuldade
        features['keyword_difficulty'] = features['keyword_difficulty'].fillna(50)
        features['competition_level'] = features['competition_level'].fillna(0.5)
        features['competitor_count'] = features['competitor_count'].fillna(10)
        features['domain_authority_avg'] = features['domain_authority_avg'].fillna(30)
        features['backlink_competition'] = features['backlink_competition'].fillna(0.5)
        
        # Features de intenção
        features['commercial_intent'] = features['commercial_intent'].fillna(0.5)
        features['informational_intent'] = features['informational_intent'].fillna(0.3)
        features['navigational_intent'] = features['navigational_intent'].fillna(0.2)
        features['transactional_intent'] = features['transactional_intent'].fillna(0.4)
        
        # Features de monetização
        features['cpc'] = features['cpc'].fillna(1.0)
        features['cpm'] = features['cpm'].fillna(5.0)
        features['revenue_potential'] = features['revenue_potential'].fillna(0)
        features['conversion_rate_estimate'] = features['conversion_rate_estimate'].fillna(0.02)
        features['lifetime_value'] = features['lifetime_value'].fillna(0)
        
        # Features de conteúdo
        features['content_gap_score'] = features['content_gap_score'].fillna(0.5)
        features['content_quality_avg'] = features['content_quality_avg'].fillna(0.6)
        features['content_freshness'] = features['content_freshness'].fillna(0.5)
        features['content_length_avg'] = features['content_length_avg'].fillna(800)
        features['multimedia_content'] = features['multimedia_content'].fillna(0.3)
        
        # Features de ranking
        features['avg_ranking_position'] = features['avg_ranking_position'].fillna(50)
        features['ranking_volatility'] = features['ranking_volatility'].fillna(0.3)
        features['featured_snippets_opportunity'] = features['featured_snippets_opportunity'].fillna(0.2)
        features['local_pack_opportunity'] = features['local_pack_opportunity'].fillna(0.1)
        
        # Features de nicho
        features['niche_saturation'] = features['niche_saturation'].fillna(0.6)
        features['niche_growth_rate'] = features['niche_growth_rate'].fillna(0.1)
        features['niche_competition_intensity'] = features['niche_competition_intensity'].fillna(0.5)
        features['niche_market_size'] = features['niche_market_size'].fillna(1000000)
        
        # Features de tendências
        features['trend_growth_rate'] = features['trend_growth_rate'].fillna(0.05)
        features['trend_consistency'] = features['trend_consistency'].fillna(0.7)
        features['trend_predictability'] = features['trend_predictability'].fillna(0.6)
        features['seasonal_opportunity'] = features['seasonal_opportunity'].fillna(0.3)
        
        # Features de tecnologia
        features['voice_search_compatibility'] = features['voice_search_compatibility'].fillna(0.4)
        features['mobile_optimization_gap'] = features['mobile_optimization_gap'].fillna(0.3)
        features['technical_seo_opportunity'] = features['technical_seo_opportunity'].fillna(0.4)
        features['page_speed_improvement'] = features['page_speed_improvement'].fillna(0.2)
        
        # Features de mercado
        features['market_maturity'] = features['market_maturity'].fillna(0.6)
        features['market_penetration'] = features['market_penetration'].fillna(0.4)
        features['market_innovation_rate'] = features['market_innovation_rate'].fillna(0.3)
        features['regulatory_environment'] = features['regulatory_environment'].fillna(0.5)
        
        # Features de custo
        features['acquisition_cost'] = features['acquisition_cost'].fillna(50)
        features['content_creation_cost'] = features['content_creation_cost'].fillna(500)
        features['link_building_cost'] = features['link_building_cost'].fillna(200)
        features['technical_implementation_cost'] = features['technical_implementation_cost'].fillna(1000)
        
        # Features de risco
        features['algorithm_risk'] = features['algorithm_risk'].fillna(0.3)
        features['competition_risk'] = features['competition_risk'].fillna(0.4)
        features['market_risk'] = features['market_risk'].fillna(0.3)
        features['technical_risk'] = features['technical_risk'].fillna(0.2)
        
        # Features temporais
        features['date'] = pd.to_datetime(features['date'])
        features['days_since_trend_start'] = (datetime.now() - features['date']).dt.days
        features['trend_duration'] = features['trend_duration'].fillna(30)
        
        # Encoding de variáveis categóricas
        categorical_features = ['keyword_type', 'niche_category', 'market_segment', 'geographic_region']
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
    
    def calculate_opportunity_score(self, data: pd.DataFrame) -> pd.Series:
        """
        Calcula score de oportunidade baseado em múltiplos fatores
        """
        # Fatores de oportunidade (pesos)
        weights = {
            'search_volume': 0.15,
            'keyword_difficulty': -0.10,  # Negativo porque menor dificuldade = melhor
            'cpc': 0.12,
            'content_gap_score': 0.10,
            'trend_growth_rate': 0.08,
            'niche_growth_rate': 0.08,
            'revenue_potential': 0.10,
            'technical_seo_opportunity': 0.05,
            'seasonal_opportunity': 0.05,
            'market_penetration': -0.05,  # Negativo porque menor penetração = mais oportunidade
            'acquisition_cost': -0.05,  # Negativo porque menor custo = melhor
            'algorithm_risk': -0.05  # Negativo porque menor risco = melhor
        }
        
        opportunity_score = pd.Series(0.0, index=data.index)
        
        for feature, weight in weights.items():
            if feature in data.columns:
                # Normalizar feature para 0-1
                feature_min = data[feature].min()
                feature_max = data[feature].max()
                if feature_max > feature_min:
                    normalized_feature = (data[feature] - feature_min) / (feature_max - feature_min)
                else:
                    normalized_feature = 0.5
                
                opportunity_score += weight * normalized_feature
        
        # Normalizar score final para 0-100
        opportunity_score = (opportunity_score - opportunity_score.min()) / (opportunity_score.max() - opportunity_score.min()) * 100
        
        return opportunity_score
    
    def cluster_opportunities(self, data: pd.DataFrame, n_clusters: int = 5) -> Dict:
        """
        Agrupa oportunidades em clusters baseado em características similares
        """
        logger.info("Agrupando oportunidades em clusters")
        
        # Preparar features para clustering
        features = self.prepare_features(data)
        
        # Features para clustering
        cluster_features = [
            'search_volume', 'keyword_difficulty', 'cpc', 'content_gap_score',
            'trend_growth_rate', 'niche_growth_rate', 'revenue_potential',
            'market_penetration', 'acquisition_cost'
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
                'avg_search_volume': cluster_data['search_volume'].mean(),
                'avg_keyword_difficulty': cluster_data['keyword_difficulty'].mean(),
                'avg_cpc': cluster_data['cpc'].mean(),
                'avg_revenue_potential': cluster_data['revenue_potential'].mean(),
                'opportunity_type': self._classify_opportunity_type(cluster_data),
                'keywords': cluster_data['keyword'].tolist()
            }
        
        self.opportunity_clusters = cluster_analysis
        
        return cluster_analysis
    
    def _classify_opportunity_type(self, cluster_data: pd.DataFrame) -> str:
        """
        Classifica o tipo de oportunidade baseado nas características do cluster
        """
        avg_volume = cluster_data['search_volume'].mean()
        avg_difficulty = cluster_data['keyword_difficulty'].mean()
        avg_cpc = cluster_data['cpc'].mean()
        
        if avg_volume > 10000 and avg_difficulty < 30:
            return 'High Volume, Low Competition'
        elif avg_cpc > 5 and avg_volume > 1000:
            return 'High Value, Moderate Volume'
        elif avg_difficulty < 20 and avg_volume > 500:
            return 'Easy Wins'
        elif avg_volume > 5000 and avg_difficulty < 50:
            return 'Balanced Opportunity'
        else:
            return 'Niche Opportunity'
    
    def train_model(self, training_data: pd.DataFrame) -> Dict:
        """
        Treina modelos de identificação de oportunidades
        """
        logger.info("Iniciando treinamento dos modelos de identificação de oportunidades")
        
        # Calcular scores de oportunidade
        training_data['opportunity_score'] = self.calculate_opportunity_score(training_data)
        
        # Agrupar oportunidades
        self.cluster_opportunities(training_data)
        
        # Preparar dados
        features = self.prepare_features(training_data)
        
        # Features para treinamento
        feature_columns = [
            'search_volume', 'search_volume_trend', 'seasonal_search_pattern',
            'long_tail_ratio', 'question_keywords', 'keyword_difficulty',
            'competition_level', 'competitor_count', 'domain_authority_avg',
            'backlink_competition', 'commercial_intent', 'informational_intent',
            'navigational_intent', 'transactional_intent', 'cpc', 'cpm',
            'revenue_potential', 'conversion_rate_estimate', 'lifetime_value',
            'content_gap_score', 'content_quality_avg', 'content_freshness',
            'content_length_avg', 'multimedia_content', 'avg_ranking_position',
            'ranking_volatility', 'featured_snippets_opportunity',
            'local_pack_opportunity', 'niche_saturation', 'niche_growth_rate',
            'niche_competition_intensity', 'niche_market_size', 'trend_growth_rate',
            'trend_consistency', 'trend_predictability', 'seasonal_opportunity',
            'voice_search_compatibility', 'mobile_optimization_gap',
            'technical_seo_opportunity', 'page_speed_improvement',
            'market_maturity', 'market_penetration', 'market_innovation_rate',
            'regulatory_environment', 'acquisition_cost', 'content_creation_cost',
            'link_building_cost', 'technical_implementation_cost',
            'algorithm_risk', 'competition_risk', 'market_risk', 'technical_risk',
            'trend_duration'
        ]
        
        X = features[feature_columns]
        y = features['opportunity_score']
        
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
    
    def find_opportunities(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica oportunidades de mercado
        """
        if self.best_model is None:
            raise ValueError("Modelo não treinado. Execute train_model() primeiro.")
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para predição
        feature_columns = [
            'search_volume', 'search_volume_trend', 'seasonal_search_pattern',
            'long_tail_ratio', 'question_keywords', 'keyword_difficulty',
            'competition_level', 'competitor_count', 'domain_authority_avg',
            'backlink_competition', 'commercial_intent', 'informational_intent',
            'navigational_intent', 'transactional_intent', 'cpc', 'cpm',
            'revenue_potential', 'conversion_rate_estimate', 'lifetime_value',
            'content_gap_score', 'content_quality_avg', 'content_freshness',
            'content_length_avg', 'multimedia_content', 'avg_ranking_position',
            'ranking_volatility', 'featured_snippets_opportunity',
            'local_pack_opportunity', 'niche_saturation', 'niche_growth_rate',
            'niche_competition_intensity', 'niche_market_size', 'trend_growth_rate',
            'trend_consistency', 'trend_predictability', 'seasonal_opportunity',
            'voice_search_compatibility', 'mobile_optimization_gap',
            'technical_seo_opportunity', 'page_speed_improvement',
            'market_maturity', 'market_penetration', 'market_innovation_rate',
            'regulatory_environment', 'acquisition_cost', 'content_creation_cost',
            'link_building_cost', 'technical_implementation_cost',
            'algorithm_risk', 'competition_risk', 'market_risk', 'technical_risk',
            'trend_duration'
        ]
        
        X = features[feature_columns]
        
        # Remover linhas com valores NaN
        mask = ~X.isnull().any(axis=1)
        X = X[mask]
        data_clean = data[mask].copy()
        
        # Normalizar features
        X_scaled = self.scaler.transform(X)
        
        # Predições
        opportunity_scores = self.best_model.predict(X_scaled)
        
        # Adicionar predições aos dados
        data_clean['predicted_opportunity_score'] = opportunity_scores
        data_clean['opportunity_level'] = self._score_to_opportunity_level(opportunity_scores)
        data_clean['recommended_action'] = self._get_recommended_action(data_clean, opportunity_scores)
        
        return data_clean
    
    def _score_to_opportunity_level(self, scores: np.ndarray) -> List[str]:
        """
        Converte scores de oportunidade em níveis
        """
        levels = []
        for score in scores:
            if score > 80:
                levels.append('Exceptional')
            elif score > 60:
                levels.append('High')
            elif score > 40:
                levels.append('Medium')
            elif score > 20:
                levels.append('Low')
            else:
                levels.append('Poor')
        return levels
    
    def _get_recommended_action(self, data: pd.DataFrame, scores: np.ndarray) -> List[str]:
        """
        Gera ações recomendadas baseadas no score de oportunidade
        """
        actions = []
        for idx, score in enumerate(scores):
            row = data.iloc[idx]
            
            if score > 80:
                actions.append('Immediate action - High priority opportunity')
            elif score > 60:
                actions.append('Strategic planning - Develop content strategy')
            elif score > 40:
                actions.append('Monitor and evaluate - Track performance')
            elif score > 20:
                actions.append('Low priority - Consider if resources available')
            else:
                actions.append('Avoid - Not worth the investment')
        
        return actions
    
    def identify_market_gaps(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica gaps de mercado baseado em análise de conteúdo
        """
        logger.info("Identificando gaps de mercado")
        
        # Filtrar keywords com alto gap de conteúdo
        high_gap = data[data['content_gap_score'] > 0.7].copy()
        
        # Calcular potencial de cada gap
        high_gap['gap_potential'] = (
            high_gap['search_volume'] * 
            high_gap['cpc'] * 
            (1 - high_gap['keyword_difficulty'] / 100) *
            high_gap['content_gap_score']
        )
        
        # Ordenar por potencial
        high_gap = high_gap.sort_values('gap_potential', ascending=False)
        
        return high_gap
    
    def get_opportunity_insights(self, opportunities: pd.DataFrame) -> Dict:
        """
        Gera insights sobre as oportunidades identificadas
        """
        insights = {
            'total_opportunities': len(opportunities),
            'exceptional_opportunities': len(opportunities[opportunities['opportunity_level'] == 'Exceptional']),
            'high_opportunities': len(opportunities[opportunities['opportunity_level'] == 'High']),
            'medium_opportunities': len(opportunities[opportunities['opportunity_level'] == 'Medium']),
            'avg_opportunity_score': opportunities['predicted_opportunity_score'].mean(),
            'top_opportunities': opportunities.nlargest(10, 'predicted_opportunity_score')[['keyword', 'predicted_opportunity_score', 'opportunity_level']],
            'opportunities_by_type': opportunities.groupby('keyword_type')['predicted_opportunity_score'].mean(),
            'opportunities_by_niche': opportunities.groupby('niche_category')['predicted_opportunity_score'].mean(),
            'revenue_potential_total': opportunities['revenue_potential'].sum(),
            'avg_acquisition_cost': opportunities['acquisition_cost'].mean()
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
            'opportunity_clusters': self.opportunity_clusters
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
            self.opportunity_clusters = model_data['opportunity_clusters']
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'keyword': [f'keyword_{i}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'search_volume': np.random.poisson(5000, n_samples),
        'search_volume_trend': np.random.uniform(-0.2, 0.3, n_samples),
        'seasonal_search_pattern': np.random.uniform(0, 1, n_samples),
        'long_tail_ratio': np.random.uniform(0, 1, n_samples),
        'question_keywords': np.random.uniform(0, 1, n_samples),
        'keyword_difficulty': np.random.uniform(0, 100, n_samples),
        'competition_level': np.random.uniform(0, 1, n_samples),
        'competitor_count': np.random.randint(0, 100, n_samples),
        'domain_authority_avg': np.random.uniform(0, 100, n_samples),
        'backlink_competition': np.random.uniform(0, 1, n_samples),
        'commercial_intent': np.random.uniform(0, 1, n_samples),
        'informational_intent': np.random.uniform(0, 1, n_samples),
        'navigational_intent': np.random.uniform(0, 1, n_samples),
        'transactional_intent': np.random.uniform(0, 1, n_samples),
        'cpc': np.random.uniform(0.5, 10, n_samples),
        'cpm': np.random.uniform(2, 20, n_samples),
        'revenue_potential': np.random.uniform(0, 50000, n_samples),
        'conversion_rate_estimate': np.random.uniform(0.01, 0.05, n_samples),
        'lifetime_value': np.random.uniform(0, 1000, n_samples),
        'content_gap_score': np.random.uniform(0, 1, n_samples),
        'content_quality_avg': np.random.uniform(0, 1, n_samples),
        'content_freshness': np.random.uniform(0, 1, n_samples),
        'content_length_avg': np.random.randint(200, 3000, n_samples),
        'multimedia_content': np.random.uniform(0, 1, n_samples),
        'avg_ranking_position': np.random.randint(1, 101, n_samples),
        'ranking_volatility': np.random.uniform(0, 1, n_samples),
        'featured_snippets_opportunity': np.random.uniform(0, 1, n_samples),
        'local_pack_opportunity': np.random.uniform(0, 1, n_samples),
        'niche_saturation': np.random.uniform(0, 1, n_samples),
        'niche_growth_rate': np.random.uniform(-0.1, 0.3, n_samples),
        'niche_competition_intensity': np.random.uniform(0, 1, n_samples),
        'niche_market_size': np.random.uniform(100000, 10000000, n_samples),
        'trend_growth_rate': np.random.uniform(-0.1, 0.3, n_samples),
        'trend_consistency': np.random.uniform(0, 1, n_samples),
        'trend_predictability': np.random.uniform(0, 1, n_samples),
        'seasonal_opportunity': np.random.uniform(0, 1, n_samples),
        'voice_search_compatibility': np.random.uniform(0, 1, n_samples),
        'mobile_optimization_gap': np.random.uniform(0, 1, n_samples),
        'technical_seo_opportunity': np.random.uniform(0, 1, n_samples),
        'page_speed_improvement': np.random.uniform(0, 1, n_samples),
        'market_maturity': np.random.uniform(0, 1, n_samples),
        'market_penetration': np.random.uniform(0, 1, n_samples),
        'market_innovation_rate': np.random.uniform(0, 1, n_samples),
        'regulatory_environment': np.random.uniform(0, 1, n_samples),
        'acquisition_cost': np.random.uniform(10, 200, n_samples),
        'content_creation_cost': np.random.uniform(100, 2000, n_samples),
        'link_building_cost': np.random.uniform(50, 500, n_samples),
        'technical_implementation_cost': np.random.uniform(500, 5000, n_samples),
        'algorithm_risk': np.random.uniform(0, 1, n_samples),
        'competition_risk': np.random.uniform(0, 1, n_samples),
        'market_risk': np.random.uniform(0, 1, n_samples),
        'technical_risk': np.random.uniform(0, 1, n_samples),
        'trend_duration': np.random.randint(1, 365, n_samples),
        'keyword_type': np.random.choice(['informational', 'transactional', 'navigational'], n_samples),
        'niche_category': np.random.choice(['tech', 'health', 'finance', 'lifestyle'], n_samples),
        'market_segment': np.random.choice(['b2b', 'b2c', 'enterprise'], n_samples),
        'geographic_region': np.random.choice(['global', 'north_america', 'europe', 'asia'], n_samples)
    })
    
    # Inicializar finder
    finder = OpportunityFinder()
    
    # Treinar modelo
    results = finder.train_model(sample_data)
    
    # Encontrar oportunidades
    opportunities = finder.find_opportunities(sample_data.head(100))
    
    # Identificar gaps de mercado
    market_gaps = finder.identify_market_gaps(sample_data.head(100))
    
    # Gerar insights
    insights = finder.get_opportunity_insights(opportunities)
    
    print("=== INSIGHTS DE IDENTIFICAÇÃO DE OPORTUNIDADES ===")
    print(f"Total de oportunidades: {insights['total_opportunities']}")
    print(f"Oportunidades excepcionais: {insights['exceptional_opportunities']}")
    print(f"Oportunidades altas: {insights['high_opportunities']}")
    print(f"Score médio de oportunidade: {insights['avg_opportunity_score']:.2f}")
    print(f"Potencial total de receita: R$ {insights['revenue_potential_total']:,.2f}")
    print(f"Custo médio de aquisição: R$ {insights['avg_acquisition_cost']:.2f}")
    
    print("\n=== TOP 5 OPORTUNIDADES ===")
    for _, opp in insights['top_opportunities'].head().iterrows():
        print(f"{opp['keyword']}: {opp['predicted_opportunity_score']:.1f} ({opp['opportunity_level']})") 