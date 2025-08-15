"""
Sistema de Detecção de Movimentos de Competidores usando Machine Learning
Monitora mudanças estratégicas e movimentos de concorrentes
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

class CompetitorMoveDetector:
    """
    Sistema de detecção de movimentos de competidores
    """
    
    def __init__(self, model_path: str = "models/competitor_move_detector.pkl"):
        self.model_path = model_path
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.competitor_baselines = {}
        self.move_patterns = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para detecção de movimentos de competidores
        """
        features = data.copy()
        
        # Features de ranking
        features['ranking_position'] = features['ranking_position'].fillna(100)
        features['ranking_change'] = features['ranking_change'].fillna(0)
        features['ranking_velocity'] = features['ranking_velocity'].fillna(0)
        features['ranking_acceleration'] = features['ranking_acceleration'].fillna(0)
        features['ranking_volatility'] = features['ranking_volatility'].fillna(0)
        
        # Features de tráfego
        features['organic_traffic'] = features['organic_traffic'].fillna(0)
        features['traffic_change'] = features['traffic_change'].fillna(0)
        features['traffic_velocity'] = features['traffic_velocity'].fillna(0)
        features['traffic_acceleration'] = features['traffic_acceleration'].fillna(0)
        features['traffic_volatility'] = features['traffic_volatility'].fillna(0)
        
        # Features de backlinks
        features['backlink_count'] = features['backlink_count'].fillna(0)
        features['backlink_change'] = features['backlink_change'].fillna(0)
        features['backlink_velocity'] = features['backlink_velocity'].fillna(0)
        features['unique_domains'] = features['unique_domains'].fillna(0)
        features['domain_authority'] = features['domain_authority'].fillna(0)
        features['page_authority'] = features['page_authority'].fillna(0)
        
        # Features de conteúdo
        features['content_publishing_frequency'] = features['content_publishing_frequency'].fillna(0)
        features['content_updates'] = features['content_updates'].fillna(0)
        features['content_length'] = features['content_length'].fillna(500)
        features['content_quality_score'] = features['content_quality_score'].fillna(0.7)
        features['content_freshness'] = features['content_freshness'].fillna(0.5)
        
        # Features de marketing
        features['social_media_activity'] = features['social_media_activity'].fillna(0)
        features['email_campaigns'] = features['email_campaigns'].fillna(0)
        features['paid_advertising'] = features['paid_advertising'].fillna(0)
        features['influencer_marketing'] = features['influencer_marketing'].fillna(0)
        features['content_marketing'] = features['content_marketing'].fillna(0)
        
        # Features de SEO técnico
        features['page_speed'] = features['page_speed'].fillna(3.0)
        features['mobile_friendly'] = features['mobile_friendly'].fillna(1)
        features['ssl_secure'] = features['ssl_secure'].fillna(1)
        features['structured_data'] = features['structured_data'].fillna(0)
        features['internal_links'] = features['internal_links'].fillna(0)
        features['external_links'] = features['external_links'].fillna(0)
        
        # Features de engajamento
        features['click_through_rate'] = features['click_through_rate'].fillna(0.05)
        features['bounce_rate'] = features['bounce_rate'].fillna(0.5)
        features['time_on_site'] = features['time_on_site'].fillna(120)
        features['pages_per_session'] = features['pages_per_session'].fillna(2.0)
        
        # Features de negócio
        features['product_updates'] = features['product_updates'].fillna(0)
        features['partnership_announcements'] = features['partnership_announcements'].fillna(0)
        features['funding_rounds'] = features['funding_rounds'].fillna(0)
        features['hiring_activity'] = features['hiring_activity'].fillna(0)
        features['market_expansion'] = features['market_expansion'].fillna(0)
        
        # Features de atividade
        features['website_changes'] = features['website_changes'].fillna(0)
        features['brand_mentions'] = features['brand_mentions'].fillna(0)
        features['press_releases'] = features['press_releases'].fillna(0)
        features['conference_participation'] = features['conference_participation'].fillna(0)
        features['award_announcements'] = features['award_announcements'].fillna(0)
        
        # Features de competição direta
        features['keyword_overlap'] = features['keyword_overlap'].fillna(0)
        features['content_similarity'] = features['content_similarity'].fillna(0)
        features['backlink_competition'] = features['backlink_competition'].fillna(0)
        features['market_share_competition'] = features['market_share_competition'].fillna(0)
        features['talent_poaching'] = features['talent_poaching'].fillna(0)
        
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
        Calcula métricas de tendência para detecção de movimentos
        """
        # Agrupar por competidor para calcular tendências
        for group_name, group_data in data.groupby('competitor_name'):
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
                
                # Backlink trends
                group_data['backlink_ma_7'] = group_data['backlink_count'].rolling(7, min_periods=1).mean()
                group_data['backlink_ma_30'] = group_data['backlink_count'].rolling(30, min_periods=1).mean()
                
                # Atualizar dados originais
                data.loc[group_data.index] = group_data
        
        # Preencher valores NaN
        trend_columns = ['ranking_ma_7', 'ranking_ma_30', 'ranking_std_7', 
                        'traffic_ma_7', 'traffic_ma_30', 'traffic_std_7',
                        'backlink_ma_7', 'backlink_ma_30']
        
        for col in trend_columns:
            if col in data.columns:
                data[col] = data[col].fillna(data[col].mean())
        
        return data
    
    def establish_competitor_baselines(self, data: pd.DataFrame) -> Dict:
        """
        Estabelece baselines para cada competidor
        """
        logger.info("Estabelecendo baselines dos competidores")
        
        baselines = {}
        
        # Baselines por competidor
        for competitor, group_data in data.groupby('competitor_name'):
            if len(group_data) > 7:  # Pelo menos 7 dias de dados
                baselines[competitor] = {}
                
                # Métricas principais
                metrics = ['ranking_position', 'organic_traffic', 'backlink_count', 
                          'content_publishing_frequency', 'social_media_activity']
                
                for metric in metrics:
                    if metric in group_data.columns:
                        recent_data = group_data.tail(30)[metric]  # Últimos 30 dias
                        if len(recent_data) > 0:
                            baselines[competitor][metric] = {
                                'baseline': recent_data.mean(),
                                'std': recent_data.std(),
                                'min': recent_data.min(),
                                'max': recent_data.max(),
                                'trend': recent_data.diff().mean()
                            }
        
        self.competitor_baselines = baselines
        
        return baselines
    
    def detect_moves(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta movimentos anômalos dos competidores
        """
        logger.info("Detectando movimentos de competidores")
        
        # Estabelecer baselines se não existirem
        if not self.competitor_baselines:
            self.establish_competitor_baselines(data)
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para detecção de movimentos
        move_features = [
            'ranking_change', 'ranking_velocity', 'ranking_acceleration', 'ranking_volatility',
            'traffic_change', 'traffic_velocity', 'traffic_acceleration', 'traffic_volatility',
            'backlink_change', 'backlink_velocity', 'content_publishing_frequency',
            'content_updates', 'social_media_activity', 'email_campaigns', 'paid_advertising',
            'influencer_marketing', 'content_marketing', 'product_updates',
            'partnership_announcements', 'funding_rounds', 'hiring_activity',
            'market_expansion', 'website_changes', 'brand_mentions', 'press_releases',
            'conference_participation', 'award_announcements', 'keyword_overlap',
            'content_similarity', 'backlink_competition', 'market_share_competition',
            'talent_poaching', 'ranking_ma_7', 'ranking_ma_30', 'ranking_std_7',
            'traffic_ma_7', 'traffic_ma_30', 'traffic_std_7',
            'backlink_ma_7', 'backlink_ma_30'
        ]
        
        # Filtrar features disponíveis
        available_features = [f for f in move_features if f in features.columns]
        X = features[available_features].fillna(0)
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Detectar movimentos
        move_scores = self.isolation_forest.fit_predict(X_scaled)
        move_scores = np.where(move_scores == -1, 1, 0)  # Converter para 0/1
        
        # Adicionar resultados aos dados
        features['move_detected'] = move_scores
        features['move_score'] = self.isolation_forest.decision_function(X_scaled)
        
        return features
    
    def classify_move_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica tipos de movimentos dos competidores
        """
        logger.info("Classificando tipos de movimentos")
        
        # Detectar movimentos
        features = self.detect_moves(data)
        
        # Classificar tipos de movimento
        move_types = []
        strategic_impacts = []
        response_priorities = []
        
        for idx, row in features.iterrows():
            move_type = self._classify_move_type(row)
            strategic_impact = self._assess_strategic_impact(row)
            response_priority = self._determine_response_priority(row)
            
            move_types.append(move_type)
            strategic_impacts.append(strategic_impact)
            response_priorities.append(response_priority)
        
        features['move_type'] = move_types
        features['strategic_impact'] = strategic_impacts
        features['response_priority'] = response_priorities
        
        return features
    
    def _classify_move_type(self, row: pd.Series) -> str:
        """
        Classifica o tipo de movimento do competidor
        """
        # Movimentos de ranking
        if row['ranking_change'] < -10:
            return 'Aggressive Ranking Push'
        elif row['ranking_change'] > 10:
            return 'Ranking Decline'
        
        # Movimentos de tráfego
        elif row['traffic_change'] > 0.5:
            return 'Traffic Surge'
        elif row['traffic_change'] < -0.3:
            return 'Traffic Drop'
        
        # Movimentos de backlinks
        elif row['backlink_change'] > 50:
            return 'Aggressive Link Building'
        elif row['backlink_change'] < -20:
            return 'Backlink Loss'
        
        # Movimentos de conteúdo
        elif row['content_publishing_frequency'] > 0.8:
            return 'Content Blitz'
        elif row['content_updates'] > 5:
            return 'Content Refresh'
        
        # Movimentos de marketing
        elif row['social_media_activity'] > 0.8:
            return 'Social Media Campaign'
        elif row['paid_advertising'] > 0.7:
            return 'Paid Advertising Push'
        elif row['influencer_marketing'] > 0.6:
            return 'Influencer Partnership'
        
        # Movimentos de negócio
        elif row['product_updates'] > 0:
            return 'Product Launch/Update'
        elif row['partnership_announcements'] > 0:
            return 'Strategic Partnership'
        elif row['funding_rounds'] > 0:
            return 'Funding Round'
        elif row['hiring_activity'] > 0.7:
            return 'Team Expansion'
        elif row['market_expansion'] > 0:
            return 'Market Expansion'
        
        # Movimentos de SEO técnico
        elif row['website_changes'] > 0.5:
            return 'Website Redesign/Update'
        
        else:
            return 'Minor Activity'
    
    def _assess_strategic_impact(self, row: pd.Series) -> str:
        """
        Avalia o impacto estratégico do movimento
        """
        # Calcular score de impacto
        impact_score = 0
        
        # Impacto de ranking
        if abs(row['ranking_change']) > 20:
            impact_score += 3
        elif abs(row['ranking_change']) > 10:
            impact_score += 2
        elif abs(row['ranking_change']) > 5:
            impact_score += 1
        
        # Impacto de tráfego
        if abs(row['traffic_change']) > 0.5:
            impact_score += 3
        elif abs(row['traffic_change']) > 0.3:
            impact_score += 2
        elif abs(row['traffic_change']) > 0.1:
            impact_score += 1
        
        # Impacto de backlinks
        if abs(row['backlink_change']) > 100:
            impact_score += 3
        elif abs(row['backlink_change']) > 50:
            impact_score += 2
        elif abs(row['backlink_change']) > 20:
            impact_score += 1
        
        # Impacto de marketing
        if row['paid_advertising'] > 0.8 or row['influencer_marketing'] > 0.8:
            impact_score += 2
        
        # Impacto de negócio
        if row['product_updates'] > 0 or row['funding_rounds'] > 0:
            impact_score += 3
        
        # Classificar impacto
        if impact_score >= 6:
            return 'High Strategic Impact'
        elif impact_score >= 4:
            return 'Medium Strategic Impact'
        elif impact_score >= 2:
            return 'Low Strategic Impact'
        else:
            return 'Minimal Strategic Impact'
    
    def _determine_response_priority(self, row: pd.Series) -> str:
        """
        Determina a prioridade de resposta ao movimento
        """
        move_type = row['move_type']
        strategic_impact = row['strategic_impact']
        
        # Movimentos críticos que requerem resposta imediata
        critical_moves = [
            'Aggressive Ranking Push', 'Aggressive Link Building', 'Content Blitz',
            'Paid Advertising Push', 'Product Launch/Update', 'Strategic Partnership',
            'Funding Round', 'Market Expansion'
        ]
        
        # Movimentos importantes que requerem monitoramento
        important_moves = [
            'Traffic Surge', 'Social Media Campaign', 'Influencer Partnership',
            'Team Expansion', 'Website Redesign/Update'
        ]
        
        if move_type in critical_moves or strategic_impact == 'High Strategic Impact':
            return 'Immediate Response Required'
        elif move_type in important_moves or strategic_impact == 'Medium Strategic Impact':
            return 'Monitor and Plan Response'
        else:
            return 'Continue Monitoring'
    
    def generate_competitor_alerts(self, data: pd.DataFrame) -> List[Dict]:
        """
        Gera alertas sobre movimentos de competidores
        """
        logger.info("Gerando alertas de movimentos de competidores")
        
        alerts = []
        
        # Filtrar apenas movimentos detectados
        moves = data[data['move_detected'] == 1]
        
        for idx, row in moves.iterrows():
            alert = {
                'timestamp': row['date'],
                'competitor': row['competitor_name'],
                'move_type': row['move_type'],
                'strategic_impact': row['strategic_impact'],
                'response_priority': row['response_priority'],
                'ranking_change': row['ranking_change'],
                'traffic_change': row['traffic_change'],
                'backlink_change': row['backlink_change'],
                'move_score': row['move_score'],
                'recommended_response': self._get_recommended_response(row)
            }
            
            alerts.append(alert)
        
        # Ordenar por prioridade e score de movimento
        priority_order = {
            'Immediate Response Required': 3,
            'Monitor and Plan Response': 2,
            'Continue Monitoring': 1
        }
        
        alerts.sort(key=lambda x: (priority_order[x['response_priority']], x['move_score']), reverse=True)
        
        return alerts
    
    def _get_recommended_response(self, row: pd.Series) -> str:
        """
        Gera resposta recomendada baseada no tipo de movimento
        """
        move_type = row['move_type']
        
        if move_type == 'Aggressive Ranking Push':
            return 'Analyze their strategy and consider competitive content creation'
        elif move_type == 'Aggressive Link Building':
            return 'Audit their backlink profile and identify link building opportunities'
        elif move_type == 'Content Blitz':
            return 'Increase content production and improve content quality'
        elif move_type == 'Paid Advertising Push':
            return 'Review PPC strategy and consider competitive bidding'
        elif move_type == 'Product Launch/Update':
            return 'Analyze their product changes and consider feature parity'
        elif move_type == 'Strategic Partnership':
            return 'Identify potential partnership opportunities in the market'
        elif move_type == 'Funding Round':
            return 'Prepare for increased competition and market pressure'
        elif move_type == 'Market Expansion':
            return 'Analyze their expansion strategy and consider market positioning'
        else:
            return 'Continue monitoring and maintain current strategy'
    
    def get_competitor_insights(self, data: pd.DataFrame) -> Dict:
        """
        Gera insights sobre movimentos de competidores
        """
        insights = {
            'total_moves_detected': len(data[data['move_detected'] == 1]),
            'move_detection_rate': data['move_detected'].mean(),
            'move_types_distribution': data['move_type'].value_counts().to_dict(),
            'strategic_impact_distribution': data['strategic_impact'].value_counts().to_dict(),
            'response_priority_distribution': data['response_priority'].value_counts().to_dict(),
            'competitors_with_moves': data[data['move_detected'] == 1]['competitor_name'].nunique(),
            'avg_ranking_change': data[data['move_detected'] == 1]['ranking_change'].mean(),
            'avg_traffic_change': data[data['move_detected'] == 1]['traffic_change'].mean(),
            'avg_backlink_change': data[data['move_detected'] == 1]['backlink_change'].mean(),
            'immediate_response_needed': len(data[(data['move_detected'] == 1) & 
                                               (data['response_priority'] == 'Immediate Response Required')]),
            'high_impact_moves': len(data[(data['move_detected'] == 1) & 
                                        (data['strategic_impact'] == 'High Strategic Impact')])
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
            'competitor_baselines': self.competitor_baselines
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
            self.competitor_baselines = model_data['competitor_baselines']
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'competitor_name': [f'competitor_{i % 20}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'ranking_position': np.random.randint(1, 101, n_samples),
        'ranking_change': np.random.randint(-30, 31, n_samples),
        'ranking_velocity': np.random.uniform(-10, 10, n_samples),
        'ranking_acceleration': np.random.uniform(-5, 5, n_samples),
        'ranking_volatility': np.random.uniform(0, 1, n_samples),
        'organic_traffic': np.random.poisson(5000, n_samples),
        'traffic_change': np.random.uniform(-0.8, 0.8, n_samples),
        'traffic_velocity': np.random.uniform(-200, 200, n_samples),
        'traffic_acceleration': np.random.uniform(-100, 100, n_samples),
        'traffic_volatility': np.random.uniform(0, 1, n_samples),
        'backlink_count': np.random.randint(0, 5000, n_samples),
        'backlink_change': np.random.randint(-100, 101, n_samples),
        'backlink_velocity': np.random.uniform(-50, 50, n_samples),
        'unique_domains': np.random.randint(0, 500, n_samples),
        'domain_authority': np.random.uniform(0, 100, n_samples),
        'page_authority': np.random.uniform(0, 100, n_samples),
        'content_publishing_frequency': np.random.uniform(0, 1, n_samples),
        'content_updates': np.random.randint(0, 10, n_samples),
        'content_length': np.random.randint(200, 3000, n_samples),
        'content_quality_score': np.random.uniform(0.3, 1.0, n_samples),
        'content_freshness': np.random.uniform(0, 1, n_samples),
        'social_media_activity': np.random.uniform(0, 1, n_samples),
        'email_campaigns': np.random.uniform(0, 1, n_samples),
        'paid_advertising': np.random.uniform(0, 1, n_samples),
        'influencer_marketing': np.random.uniform(0, 1, n_samples),
        'content_marketing': np.random.uniform(0, 1, n_samples),
        'page_speed': np.random.uniform(1, 8, n_samples),
        'mobile_friendly': np.random.choice([0, 1], n_samples),
        'ssl_secure': np.random.choice([0, 1], n_samples),
        'structured_data': np.random.choice([0, 1], n_samples),
        'internal_links': np.random.randint(0, 100, n_samples),
        'external_links': np.random.randint(0, 50, n_samples),
        'click_through_rate': np.random.uniform(0.02, 0.08, n_samples),
        'bounce_rate': np.random.uniform(0.3, 0.8, n_samples),
        'time_on_site': np.random.uniform(60, 300, n_samples),
        'pages_per_session': np.random.uniform(1, 5, n_samples),
        'product_updates': np.random.randint(0, 3, n_samples),
        'partnership_announcements': np.random.randint(0, 2, n_samples),
        'funding_rounds': np.random.randint(0, 2, n_samples),
        'hiring_activity': np.random.uniform(0, 1, n_samples),
        'market_expansion': np.random.randint(0, 2, n_samples),
        'website_changes': np.random.uniform(0, 1, n_samples),
        'brand_mentions': np.random.randint(0, 20, n_samples),
        'press_releases': np.random.randint(0, 3, n_samples),
        'conference_participation': np.random.randint(0, 2, n_samples),
        'award_announcements': np.random.randint(0, 2, n_samples),
        'keyword_overlap': np.random.uniform(0, 1, n_samples),
        'content_similarity': np.random.uniform(0, 1, n_samples),
        'backlink_competition': np.random.uniform(0, 1, n_samples),
        'market_share_competition': np.random.uniform(0, 1, n_samples),
        'talent_poaching': np.random.uniform(0, 1, n_samples)
    })
    
    # Inicializar detector
    detector = CompetitorMoveDetector()
    
    # Classificar movimentos
    results = detector.classify_move_types(sample_data)
    
    # Gerar alertas
    alerts = detector.generate_competitor_alerts(results)
    
    # Gerar insights
    insights = detector.get_competitor_insights(results)
    
    print("=== INSIGHTS DE DETECÇÃO DE MOVIMENTOS DE COMPETIDORES ===")
    print(f"Total de movimentos detectados: {insights['total_moves_detected']}")
    print(f"Taxa de detecção de movimentos: {insights['move_detection_rate']:.2%}")
    print(f"Competidores com movimentos: {insights['competitors_with_moves']}")
    print(f"Respostas imediatas necessárias: {insights['immediate_response_needed']}")
    print(f"Movimentos de alto impacto: {insights['high_impact_moves']}")
    
    print("\n=== DISTRIBUIÇÃO DE TIPOS DE MOVIMENTO ===")
    for move_type, count in insights['move_types_distribution'].items():
        print(f"{move_type}: {count}")
    
    print("\n=== TOP 5 ALERTAS DE COMPETIDORES ===")
    for alert in alerts[:5]:
        print(f"{alert['competitor']} - {alert['move_type']} ({alert['response_priority']}): {alert['strategic_impact']}") 