"""
Sistema de Detecção de Atualizações de Algoritmos usando Machine Learning
Monitora mudanças no Google e outros motores de busca
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlgorithmUpdateDetector:
    """
    Sistema de detecção de atualizações de algoritmos
    """
    
    def __init__(self, model_path: str = "models/algorithm_update_detector.pkl"):
        self.model_path = model_path
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.algorithm_baselines = {}
        self.update_patterns = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para detecção de atualizações de algoritmos
        """
        features = data.copy()
        
        # Features de ranking
        features['ranking_position'] = features['ranking_position'].fillna(100)
        features['ranking_change'] = features['ranking_change'].fillna(0)
        features['ranking_velocity'] = features['ranking_velocity'].fillna(0)
        features['ranking_acceleration'] = features['ranking_acceleration'].fillna(0)
        features['ranking_volatility'] = features['ranking_volatility'].fillna(0)
        features['ranking_consistency'] = features['ranking_consistency'].fillna(0.5)
        
        # Features de tráfego
        features['organic_traffic'] = features['organic_traffic'].fillna(0)
        features['traffic_change'] = features['traffic_change'].fillna(0)
        features['traffic_velocity'] = features['traffic_velocity'].fillna(0)
        features['traffic_acceleration'] = features['traffic_acceleration'].fillna(0)
        features['traffic_volatility'] = features['traffic_volatility'].fillna(0)
        
        # Features de SERP
        features['serp_features'] = features['serp_features'].fillna(0)
        features['featured_snippets'] = features['featured_snippets'].fillna(0)
        features['local_pack'] = features['local_pack'].fillna(0)
        features['knowledge_panel'] = features['knowledge_panel'].fillna(0)
        features['shopping_results'] = features['shopping_results'].fillna(0)
        features['video_results'] = features['video_results'].fillna(0)
        features['news_results'] = features['news_results'].fillna(0)
        features['image_results'] = features['image_results'].fillna(0)
        
        # Features de conteúdo
        features['content_quality_score'] = features['content_quality_score'].fillna(0.7)
        features['content_relevance'] = features['content_relevance'].fillna(0.7)
        features['content_freshness'] = features['content_freshness'].fillna(0.5)
        features['content_length'] = features['content_length'].fillna(800)
        features['content_depth'] = features['content_depth'].fillna(0.6)
        features['content_authority'] = features['content_authority'].fillna(0.6)
        
        # Features de SEO técnico
        features['page_speed'] = features['page_speed'].fillna(3.0)
        features['mobile_friendly'] = features['mobile_friendly'].fillna(1)
        features['ssl_secure'] = features['ssl_secure'].fillna(1)
        features['core_web_vitals'] = features['core_web_vitals'].fillna(0.8)
        features['structured_data'] = features['structured_data'].fillna(0)
        features['internal_linking'] = features['internal_linking'].fillna(0.6)
        features['external_linking'] = features['external_linking'].fillna(0.4)
        
        # Features de backlinks
        features['backlink_count'] = features['backlink_count'].fillna(0)
        features['backlink_quality'] = features['backlink_quality'].fillna(0.6)
        features['domain_authority'] = features['domain_authority'].fillna(0)
        features['page_authority'] = features['page_authority'].fillna(0)
        features['spam_score'] = features['spam_score'].fillna(0)
        features['trust_flow'] = features['trust_flow'].fillna(0)
        features['citation_flow'] = features['citation_flow'].fillna(0)
        
        # Features de user experience
        features['click_through_rate'] = features['click_through_rate'].fillna(0.05)
        features['bounce_rate'] = features['bounce_rate'].fillna(0.5)
        features['time_on_site'] = features['time_on_site'].fillna(120)
        features['pages_per_session'] = features['pages_per_session'].fillna(2.0)
        features['user_engagement'] = features['user_engagement'].fillna(0.6)
        features['user_satisfaction'] = features['user_satisfaction'].fillna(0.7)
        
        # Features de intenção
        features['search_intent_match'] = features['search_intent_match'].fillna(0.7)
        features['keyword_intent'] = features['keyword_intent'].fillna('informational')
        features['query_satisfaction'] = features['query_satisfaction'].fillna(0.7)
        features['result_relevance'] = features['result_relevance'].fillna(0.7)
        
        # Features de competição
        features['competitor_rankings'] = features['competitor_rankings'].fillna(0)
        features['competitor_traffic'] = features['competitor_traffic'].fillna(0)
        features['market_share_change'] = features['market_share_change'].fillna(0)
        features['competitive_position'] = features['competitive_position'].fillna(0.5)
        
        # Features de algoritmo específicas
        features['panda_score'] = features['panda_score'].fillna(0.7)
        features['penguin_score'] = features['penguin_score'].fillna(0.7)
        features['hummingbird_score'] = features['hummingbird_score'].fillna(0.7)
        features['pigeon_score'] = features['pigeon_score'].fillna(0.7)
        features['mobilegeddon_score'] = features['mobilegeddon_score'].fillna(0.7)
        features['rankbrain_score'] = features['rankbrain_score'].fillna(0.7)
        features['bert_score'] = features['bert_score'].fillna(0.7)
        features['core_updates_score'] = features['core_updates_score'].fillna(0.7)
        
        # Features de sinais de qualidade
        features['e_a_t_score'] = features['e_a_t_score'].fillna(0.7)  # Expertise, Authority, Trust
        features['y_my_yl_score'] = features['y_my_yl_score'].fillna(0.7)  # Your Money, Your Life
        features['helpful_content_score'] = features['helpful_content_score'].fillna(0.7)
        features['product_reviews_score'] = features['product_reviews_score'].fillna(0.7)
        features['link_spam_score'] = features['link_spam_score'].fillna(0.3)
        
        # Features de performance
        features['lcp_score'] = features['lcp_score'].fillna(0.8)  # Largest Contentful Paint
        features['fid_score'] = features['fid_score'].fillna(0.8)  # First Input Delay
        features['cls_score'] = features['cls_score'].fillna(0.8)  # Cumulative Layout Shift
        features['ttfb_score'] = features['ttfb_score'].fillna(0.8)  # Time to First Byte
        
        # Features de acessibilidade
        features['accessibility_score'] = features['accessibility_score'].fillna(0.7)
        features['mobile_usability'] = features['mobile_usability'].fillna(0.8)
        features['desktop_usability'] = features['desktop_usability'].fillna(0.8)
        
        # Features temporais
        features['date'] = pd.to_datetime(features['date'])
        features['day_of_week'] = features['date'].dt.dayofweek
        features['month'] = features['date'].dt.month
        features['quarter'] = features['date'].dt.quarter
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Calcular métricas de tendência
        features = self._calculate_trend_metrics(features)
        
        return features
    
    def _calculate_trend_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula métricas de tendência para detecção de atualizações
        """
        # Agrupar por keyword/domínio para calcular tendências
        for group_name, group_data in data.groupby(['keyword', 'domain']):
            if len(group_data) > 1:
                # Calcular médias móveis
                group_data = group_data.sort_values('date')
                
                # Ranking trends
                group_data['ranking_ma_7'] = group_data['ranking_position'].rolling(7, min_periods=1).mean()
                group_data['ranking_ma_30'] = group_data['ranking_position'].rolling(30, min_periods=1).mean()
                group_data['ranking_std_7'] = group_data['ranking_position'].rolling(7, min_periods=1).std()
                
                # Traffic trends
                group_data['traffic_ma_7'] = group_data['organic_traffic'].rolling(7, min_periods=1).mean()
                group_data['traffic_ma_30'] = group_data['organic_traffic'].rolling(30, min_periods=1).mean()
                group_data['traffic_std_7'] = group_data['organic_traffic'].rolling(7, min_periods=1).std()
                
                # SERP features trends
                group_data['serp_features_ma_7'] = group_data['serp_features'].rolling(7, min_periods=1).mean()
                group_data['serp_features_ma_30'] = group_data['serp_features'].rolling(30, min_periods=1).mean()
                
                # Atualizar dados originais
                data.loc[group_data.index] = group_data
        
        # Preencher valores NaN
        trend_columns = ['ranking_ma_7', 'ranking_ma_30', 'ranking_std_7',
                        'traffic_ma_7', 'traffic_ma_30', 'traffic_std_7',
                        'serp_features_ma_7', 'serp_features_ma_30']
        
        for col in trend_columns:
            if col in data.columns:
                data[col] = data[col].fillna(data[col].mean())
        
        return data
    
    def establish_algorithm_baselines(self, data: pd.DataFrame) -> Dict:
        """
        Estabelece baselines para cada algoritmo
        """
        logger.info("Estabelecendo baselines de algoritmos")
        
        baselines = {}
        
        # Baselines por domínio/keyword
        for (domain, keyword), group_data in data.groupby(['domain', 'keyword']):
            if len(group_data) > 7:  # Pelo menos 7 dias de dados
                baselines[f"{domain}_{keyword}"] = {}
                
                # Métricas principais
                metrics = ['ranking_position', 'organic_traffic', 'serp_features',
                          'content_quality_score', 'core_web_vitals']
                
                for metric in metrics:
                    if metric in group_data.columns:
                        recent_data = group_data.tail(30)[metric]  # Últimos 30 dias
                        if len(recent_data) > 0:
                            baselines[f"{domain}_{keyword}"][metric] = {
                                'baseline': recent_data.mean(),
                                'std': recent_data.std(),
                                'min': recent_data.min(),
                                'max': recent_data.max(),
                                'trend': recent_data.diff().mean()
                            }
        
        self.algorithm_baselines = baselines
        
        return baselines
    
    def detect_algorithm_updates(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta atualizações de algoritmos
        """
        logger.info("Detectando atualizações de algoritmos")
        
        # Estabelecer baselines se não existirem
        if not self.algorithm_baselines:
            self.establish_algorithm_baselines(data)
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para detecção de atualizações
        update_features = [
            'ranking_change', 'ranking_velocity', 'ranking_acceleration', 'ranking_volatility',
            'traffic_change', 'traffic_velocity', 'traffic_acceleration', 'traffic_volatility',
            'serp_features', 'featured_snippets', 'local_pack', 'knowledge_panel',
            'content_quality_score', 'content_relevance', 'content_freshness',
            'page_speed', 'mobile_friendly', 'core_web_vitals', 'structured_data',
            'backlink_quality', 'domain_authority', 'page_authority', 'spam_score',
            'click_through_rate', 'bounce_rate', 'time_on_site', 'user_engagement',
            'search_intent_match', 'query_satisfaction', 'result_relevance',
            'panda_score', 'penguin_score', 'hummingbird_score', 'pigeon_score',
            'mobilegeddon_score', 'rankbrain_score', 'bert_score', 'core_updates_score',
            'e_a_t_score', 'y_my_yl_score', 'helpful_content_score',
            'product_reviews_score', 'link_spam_score', 'lcp_score', 'fid_score',
            'cls_score', 'ttfb_score', 'accessibility_score', 'mobile_usability',
            'desktop_usability', 'ranking_ma_7', 'ranking_ma_30', 'ranking_std_7',
            'traffic_ma_7', 'traffic_ma_30', 'traffic_std_7',
            'serp_features_ma_7', 'serp_features_ma_30'
        ]
        
        # Filtrar features disponíveis
        available_features = [f for f in update_features if f in features.columns]
        X = features[available_features].fillna(0)
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Detectar atualizações
        update_scores = self.isolation_forest.fit_predict(X_scaled)
        update_scores = np.where(update_scores == -1, 1, 0)  # Converter para 0/1
        
        # Adicionar resultados aos dados
        features['algorithm_update_detected'] = update_scores
        features['update_score'] = self.isolation_forest.decision_function(X_scaled)
        
        return features
    
    def classify_update_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica tipos de atualizações de algoritmos
        """
        logger.info("Classificando tipos de atualizações de algoritmos")
        
        # Detectar atualizações
        features = self.detect_algorithm_updates(data)
        
        # Classificar tipos de atualização
        update_types = []
        impact_levels = []
        recovery_strategies = []
        
        for idx, row in features.iterrows():
            update_type = self._classify_update_type(row)
            impact_level = self._assess_update_impact(row)
            recovery_strategy = self._determine_recovery_strategy(row)
            
            update_types.append(update_type)
            impact_levels.append(impact_level)
            recovery_strategies.append(recovery_strategy)
        
        features['update_type'] = update_types
        features['impact_level'] = impact_levels
        features['recovery_strategy'] = recovery_strategies
        
        return features
    
    def _classify_update_type(self, row: pd.Series) -> str:
        """
        Classifica o tipo de atualização de algoritmo
        """
        # Atualizações de ranking
        if row['ranking_change'] < -20:
            return 'Major Ranking Drop'
        elif row['ranking_change'] < -10:
            return 'Moderate Ranking Drop'
        elif row['ranking_change'] > 20:
            return 'Major Ranking Boost'
        elif row['ranking_change'] > 10:
            return 'Moderate Ranking Boost'
        
        # Atualizações de tráfego
        elif row['traffic_change'] < -0.5:
            return 'Traffic Penalty'
        elif row['traffic_change'] > 0.5:
            return 'Traffic Boost'
        
        # Atualizações de SERP
        elif row['serp_features'] > 0.8:
            return 'SERP Features Boost'
        elif row['featured_snippets'] > 0:
            return 'Featured Snippets Update'
        elif row['local_pack'] > 0:
            return 'Local Pack Update'
        
        # Atualizações de conteúdo
        elif row['content_quality_score'] < 0.4:
            return 'Content Quality Penalty'
        elif row['content_quality_score'] > 0.9:
            return 'Content Quality Boost'
        elif row['helpful_content_score'] < 0.4:
            return 'Helpful Content Penalty'
        
        # Atualizações técnicas
        elif row['page_speed'] > 5:
            return 'Page Speed Penalty'
        elif row['core_web_vitals'] < 0.5:
            return 'Core Web Vitals Penalty'
        elif row['mobile_friendly'] == 0:
            return 'Mobile Penalty'
        
        # Atualizações de backlinks
        elif row['backlink_quality'] < 0.3:
            return 'Backlink Quality Penalty'
        elif row['spam_score'] > 0.7:
            return 'Spam Penalty'
        elif row['link_spam_score'] > 0.7:
            return 'Link Spam Penalty'
        
        # Atualizações de E-A-T
        elif row['e_a_t_score'] < 0.4:
            return 'E-A-T Penalty'
        elif row['y_my_yl_score'] < 0.4:
            return 'YMYL Penalty'
        
        # Atualizações de user experience
        elif row['user_engagement'] < 0.3:
            return 'User Experience Penalty'
        elif row['click_through_rate'] < 0.02:
            return 'CTR Penalty'
        elif row['bounce_rate'] > 0.8:
            return 'Bounce Rate Penalty'
        
        else:
            return 'Minor Algorithm Fluctuation'
    
    def _assess_update_impact(self, row: pd.Series) -> str:
        """
        Avalia o nível de impacto da atualização
        """
        # Calcular score de impacto
        impact_score = 0
        
        # Impacto de ranking
        if abs(row['ranking_change']) > 30:
            impact_score += 3
        elif abs(row['ranking_change']) > 20:
            impact_score += 2
        elif abs(row['ranking_change']) > 10:
            impact_score += 1
        
        # Impacto de tráfego
        if abs(row['traffic_change']) > 0.7:
            impact_score += 3
        elif abs(row['traffic_change']) > 0.5:
            impact_score += 2
        elif abs(row['traffic_change']) > 0.3:
            impact_score += 1
        
        # Impacto de SERP
        if row['serp_features'] > 0.8 or row['featured_snippets'] > 0:
            impact_score += 2
        
        # Impacto de qualidade
        if row['content_quality_score'] < 0.4 or row['helpful_content_score'] < 0.4:
            impact_score += 3
        
        # Impacto técnico
        if row['page_speed'] > 5 or row['core_web_vitals'] < 0.5:
            impact_score += 2
        
        # Impacto de backlinks
        if row['backlink_quality'] < 0.3 or row['spam_score'] > 0.7:
            impact_score += 3
        
        # Classificar impacto
        if impact_score >= 6:
            return 'High Algorithm Impact'
        elif impact_score >= 4:
            return 'Medium Algorithm Impact'
        elif impact_score >= 2:
            return 'Low Algorithm Impact'
        else:
            return 'Minimal Algorithm Impact'
    
    def _determine_recovery_strategy(self, row: pd.Series) -> str:
        """
        Determina estratégia de recuperação baseada no tipo de atualização
        """
        update_type = row['update_type']
        impact_level = row['impact_level']
        
        # Atualizações que requerem ação imediata
        immediate_updates = [
            'Major Ranking Drop', 'Traffic Penalty', 'Content Quality Penalty',
            'Helpful Content Penalty', 'Spam Penalty', 'Link Spam Penalty',
            'E-A-T Penalty', 'YMYL Penalty'
        ]
        
        # Atualizações que requerem otimização
        optimization_updates = [
            'Moderate Ranking Drop', 'Page Speed Penalty', 'Core Web Vitals Penalty',
            'Mobile Penalty', 'User Experience Penalty', 'CTR Penalty',
            'Bounce Rate Penalty'
        ]
        
        if update_type in immediate_updates or impact_level == 'High Algorithm Impact':
            return 'Immediate Recovery Action Required'
        elif update_type in optimization_updates or impact_level == 'Medium Algorithm Impact':
            return 'Optimization and Monitoring Needed'
        else:
            return 'Continue Monitoring and Gradual Improvement'
    
    def generate_algorithm_alerts(self, data: pd.DataFrame) -> List[Dict]:
        """
        Gera alertas sobre atualizações de algoritmos
        """
        logger.info("Gerando alertas de atualizações de algoritmos")
        
        alerts = []
        
        # Filtrar apenas atualizações detectadas
        updates = data[data['algorithm_update_detected'] == 1]
        
        for idx, row in updates.iterrows():
            alert = {
                'timestamp': row['date'],
                'domain': row['domain'],
                'keyword': row['keyword'],
                'update_type': row['update_type'],
                'impact_level': row['impact_level'],
                'recovery_strategy': row['recovery_strategy'],
                'ranking_change': row['ranking_change'],
                'traffic_change': row['traffic_change'],
                'serp_features': row['serp_features'],
                'update_score': row['update_score'],
                'recommended_action': self._get_recommended_action(row)
            }
            
            alerts.append(alert)
        
        # Ordenar por impacto e score de atualização
        impact_order = {
            'High Algorithm Impact': 3,
            'Medium Algorithm Impact': 2,
            'Low Algorithm Impact': 1,
            'Minimal Algorithm Impact': 0
        }
        
        alerts.sort(key=lambda x: (impact_order[x['impact_level']], x['update_score']), reverse=True)
        
        return alerts
    
    def _get_recommended_action(self, row: pd.Series) -> str:
        """
        Gera ação recomendada baseada no tipo de atualização
        """
        update_type = row['update_type']
        
        if update_type == 'Major Ranking Drop':
            return 'Conduct comprehensive SEO audit and fix critical issues'
        elif update_type == 'Traffic Penalty':
            return 'Analyze traffic patterns and improve user experience'
        elif update_type == 'Content Quality Penalty':
            return 'Improve content quality, depth, and relevance'
        elif update_type == 'Helpful Content Penalty':
            return 'Focus on creating genuinely helpful, user-focused content'
        elif update_type == 'Spam Penalty':
            return 'Remove spammy backlinks and improve link profile'
        elif update_type == 'Link Spam Penalty':
            return 'Audit and disavow toxic backlinks'
        elif update_type == 'E-A-T Penalty':
            return 'Improve expertise, authority, and trust signals'
        elif update_type == 'YMYL Penalty':
            return 'Enhance credibility and expertise for YMYL topics'
        elif update_type == 'Page Speed Penalty':
            return 'Optimize page speed and Core Web Vitals'
        elif update_type == 'Core Web Vitals Penalty':
            return 'Fix LCP, FID, and CLS issues'
        elif update_type == 'Mobile Penalty':
            return 'Improve mobile-friendliness and mobile UX'
        elif update_type == 'User Experience Penalty':
            return 'Enhance user engagement and satisfaction metrics'
        else:
            return 'Monitor performance and maintain current optimization'
    
    def get_algorithm_insights(self, data: pd.DataFrame) -> Dict:
        """
        Gera insights sobre atualizações de algoritmos
        """
        insights = {
            'total_updates_detected': len(data[data['algorithm_update_detected'] == 1]),
            'update_detection_rate': data['algorithm_update_detected'].mean(),
            'update_types_distribution': data['update_type'].value_counts().to_dict(),
            'impact_levels_distribution': data['impact_level'].value_counts().to_dict(),
            'recovery_strategies_distribution': data['recovery_strategy'].value_counts().to_dict(),
            'domains_affected': data[data['algorithm_update_detected'] == 1]['domain'].nunique(),
            'keywords_affected': data[data['algorithm_update_detected'] == 1]['keyword'].nunique(),
            'avg_ranking_change': data[data['algorithm_update_detected'] == 1]['ranking_change'].mean(),
            'avg_traffic_change': data[data['algorithm_update_detected'] == 1]['traffic_change'].mean(),
            'immediate_recovery_needed': len(data[(data['algorithm_update_detected'] == 1) & 
                                               (data['recovery_strategy'] == 'Immediate Recovery Action Required')]),
            'high_impact_updates': len(data[(data['algorithm_update_detected'] == 1) & 
                                          (data['impact_level'] == 'High Algorithm Impact')])
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
            'algorithm_baselines': self.algorithm_baselines
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
            self.algorithm_baselines = model_data['algorithm_baselines']
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'domain': [f'domain_{i % 20}' for i in range(n_samples)],
        'keyword': [f'keyword_{i % 50}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'ranking_position': np.random.randint(1, 101, n_samples),
        'ranking_change': np.random.randint(-40, 41, n_samples),
        'ranking_velocity': np.random.uniform(-15, 15, n_samples),
        'ranking_acceleration': np.random.uniform(-8, 8, n_samples),
        'ranking_volatility': np.random.uniform(0, 1, n_samples),
        'ranking_consistency': np.random.uniform(0, 1, n_samples),
        'organic_traffic': np.random.poisson(5000, n_samples),
        'traffic_change': np.random.uniform(-0.8, 0.8, n_samples),
        'traffic_velocity': np.random.uniform(-200, 200, n_samples),
        'traffic_acceleration': np.random.uniform(-100, 100, n_samples),
        'traffic_volatility': np.random.uniform(0, 1, n_samples),
        'serp_features': np.random.uniform(0, 1, n_samples),
        'featured_snippets': np.random.choice([0, 1], n_samples),
        'local_pack': np.random.choice([0, 1], n_samples),
        'knowledge_panel': np.random.choice([0, 1], n_samples),
        'shopping_results': np.random.choice([0, 1], n_samples),
        'video_results': np.random.choice([0, 1], n_samples),
        'news_results': np.random.choice([0, 1], n_samples),
        'image_results': np.random.choice([0, 1], n_samples),
        'content_quality_score': np.random.uniform(0.3, 1.0, n_samples),
        'content_relevance': np.random.uniform(0.4, 1.0, n_samples),
        'content_freshness': np.random.uniform(0, 1, n_samples),
        'content_length': np.random.randint(200, 3000, n_samples),
        'content_depth': np.random.uniform(0.3, 1.0, n_samples),
        'content_authority': np.random.uniform(0.4, 1.0, n_samples),
        'page_speed': np.random.uniform(1, 8, n_samples),
        'mobile_friendly': np.random.choice([0, 1], n_samples),
        'ssl_secure': np.random.choice([0, 1], n_samples),
        'core_web_vitals': np.random.uniform(0.3, 1.0, n_samples),
        'structured_data': np.random.choice([0, 1], n_samples),
        'internal_linking': np.random.uniform(0.3, 1.0, n_samples),
        'external_linking': np.random.uniform(0.2, 0.8, n_samples),
        'backlink_count': np.random.randint(0, 2000, n_samples),
        'backlink_quality': np.random.uniform(0.2, 1.0, n_samples),
        'domain_authority': np.random.uniform(0, 100, n_samples),
        'page_authority': np.random.uniform(0, 100, n_samples),
        'spam_score': np.random.uniform(0, 17, n_samples),
        'trust_flow': np.random.uniform(0, 100, n_samples),
        'citation_flow': np.random.uniform(0, 100, n_samples),
        'click_through_rate': np.random.uniform(0.02, 0.08, n_samples),
        'bounce_rate': np.random.uniform(0.3, 0.8, n_samples),
        'time_on_site': np.random.uniform(60, 300, n_samples),
        'pages_per_session': np.random.uniform(1, 5, n_samples),
        'user_engagement': np.random.uniform(0.3, 0.9, n_samples),
        'user_satisfaction': np.random.uniform(0.4, 0.9, n_samples),
        'search_intent_match': np.random.uniform(0.4, 1.0, n_samples),
        'keyword_intent': np.random.choice(['informational', 'transactional', 'navigational'], n_samples),
        'query_satisfaction': np.random.uniform(0.4, 1.0, n_samples),
        'result_relevance': np.random.uniform(0.4, 1.0, n_samples),
        'competitor_rankings': np.random.uniform(0, 1, n_samples),
        'competitor_traffic': np.random.uniform(0, 1, n_samples),
        'market_share_change': np.random.uniform(-0.3, 0.3, n_samples),
        'competitive_position': np.random.uniform(0, 1, n_samples),
        'panda_score': np.random.uniform(0.3, 1.0, n_samples),
        'penguin_score': np.random.uniform(0.3, 1.0, n_samples),
        'hummingbird_score': np.random.uniform(0.3, 1.0, n_samples),
        'pigeon_score': np.random.uniform(0.3, 1.0, n_samples),
        'mobilegeddon_score': np.random.uniform(0.3, 1.0, n_samples),
        'rankbrain_score': np.random.uniform(0.3, 1.0, n_samples),
        'bert_score': np.random.uniform(0.3, 1.0, n_samples),
        'core_updates_score': np.random.uniform(0.3, 1.0, n_samples),
        'e_a_t_score': np.random.uniform(0.3, 1.0, n_samples),
        'y_my_yl_score': np.random.uniform(0.3, 1.0, n_samples),
        'helpful_content_score': np.random.uniform(0.3, 1.0, n_samples),
        'product_reviews_score': np.random.uniform(0.3, 1.0, n_samples),
        'link_spam_score': np.random.uniform(0, 1, n_samples),
        'lcp_score': np.random.uniform(0.3, 1.0, n_samples),
        'fid_score': np.random.uniform(0.3, 1.0, n_samples),
        'cls_score': np.random.uniform(0.3, 1.0, n_samples),
        'ttfb_score': np.random.uniform(0.3, 1.0, n_samples),
        'accessibility_score': np.random.uniform(0.4, 1.0, n_samples),
        'mobile_usability': np.random.uniform(0.5, 1.0, n_samples),
        'desktop_usability': np.random.uniform(0.5, 1.0, n_samples)
    })
    
    # Inicializar detector
    detector = AlgorithmUpdateDetector()
    
    # Classificar atualizações
    results = detector.classify_update_types(sample_data)
    
    # Gerar alertas
    alerts = detector.generate_algorithm_alerts(results)
    
    # Gerar insights
    insights = detector.get_algorithm_insights(results)
    
    print("=== INSIGHTS DE DETECÇÃO DE ATUALIZAÇÕES DE ALGORITMOS ===")
    print(f"Total de atualizações detectadas: {insights['total_updates_detected']}")
    print(f"Taxa de detecção de atualizações: {insights['update_detection_rate']:.2%}")
    print(f"Domínios afetados: {insights['domains_affected']}")
    print(f"Keywords afetadas: {insights['keywords_affected']}")
    print(f"Recuperações imediatas necessárias: {insights['immediate_recovery_needed']}")
    print(f"Atualizações de alto impacto: {insights['high_impact_updates']}")
    
    print("\n=== DISTRIBUIÇÃO DE TIPOS DE ATUALIZAÇÃO ===")
    for update_type, count in insights['update_types_distribution'].items():
        print(f"{update_type}: {count}")
    
    print("\n=== TOP 5 ALERTAS DE ALGORITMO ===")
    for alert in alerts[:5]:
        print(f"{alert['domain']} - {alert['keyword']}: {alert['update_type']} ({alert['impact_level']})") 