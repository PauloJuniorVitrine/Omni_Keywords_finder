"""
Sistema de Detecção de Mudanças de Mercado usando Machine Learning
Monitora tendências, disrupções e mudanças no ambiente de mercado
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

class MarketChangeDetector:
    """
    Sistema de detecção de mudanças de mercado
    """
    
    def __init__(self, model_path: str = "models/market_change_detector.pkl"):
        self.model_path = model_path
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.market_baselines = {}
        self.change_patterns = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para detecção de mudanças de mercado
        """
        features = data.copy()
        
        # Features de volume de busca
        features['search_volume'] = features['search_volume'].fillna(0)
        features['search_volume_change'] = features['search_volume_change'].fillna(0)
        features['search_volume_trend'] = features['search_volume_trend'].fillna(0)
        features['search_volume_volatility'] = features['search_volume_volatility'].fillna(0)
        features['long_tail_ratio'] = features['long_tail_ratio'].fillna(0)
        
        # Features de intenção de busca
        features['commercial_intent'] = features['commercial_intent'].fillna(0.5)
        features['informational_intent'] = features['informational_intent'].fillna(0.3)
        features['navigational_intent'] = features['navigational_intent'].fillna(0.2)
        features['transactional_intent'] = features['transactional_intent'].fillna(0.4)
        features['intent_shift'] = features['intent_shift'].fillna(0)
        
        # Features de competição
        features['competitor_count'] = features['competitor_count'].fillna(10)
        features['competition_intensity'] = features['competition_intensity'].fillna(0.5)
        features['market_saturation'] = features['market_saturation'].fillna(0.6)
        features['barrier_to_entry'] = features['barrier_to_entry'].fillna(0.5)
        features['competitive_dynamics'] = features['competitive_dynamics'].fillna(0.5)
        
        # Features de preços
        features['cpc'] = features['cpc'].fillna(1.0)
        features['cpc_change'] = features['cpc_change'].fillna(0)
        features['cpm'] = features['cpm'].fillna(5.0)
        features['cpm_change'] = features['cpm_change'].fillna(0)
        features['price_volatility'] = features['price_volatility'].fillna(0)
        
        # Features de conversão
        features['conversion_rate'] = features['conversion_rate'].fillna(0.02)
        features['conversion_rate_change'] = features['conversion_rate_change'].fillna(0)
        features['customer_acquisition_cost'] = features['customer_acquisition_cost'].fillna(50)
        features['lifetime_value'] = features['lifetime_value'].fillna(200)
        features['roas'] = features['roas'].fillna(2.0)
        
        # Features de tecnologia
        features['technology_adoption'] = features['technology_adoption'].fillna(0.5)
        features['mobile_usage'] = features['mobile_usage'].fillna(0.6)
        features['voice_search_adoption'] = features['voice_search_adoption'].fillna(0.3)
        features['ai_adoption'] = features['ai_adoption'].fillna(0.4)
        features['automation_level'] = features['automation_level'].fillna(0.5)
        
        # Features de regulamentação
        features['regulatory_changes'] = features['regulatory_changes'].fillna(0)
        features['compliance_requirements'] = features['compliance_requirements'].fillna(0.3)
        features['privacy_regulations'] = features['privacy_regulations'].fillna(0.4)
        features['data_protection'] = features['data_protection'].fillna(0.5)
        features['regulatory_risk'] = features['regulatory_risk'].fillna(0.3)
        
        # Features econômicas
        features['economic_growth'] = features['economic_growth'].fillna(0.02)
        features['inflation_rate'] = features['inflation_rate'].fillna(0.03)
        features['interest_rate'] = features['interest_rate'].fillna(0.05)
        features['consumer_confidence'] = features['consumer_confidence'].fillna(50)
        features['unemployment_rate'] = features['unemployment_rate'].fillna(0.05)
        
        # Features de comportamento do consumidor
        features['consumer_preferences'] = features['consumer_preferences'].fillna(0.5)
        features['purchasing_power'] = features['purchasing_power'].fillna(0.7)
        features['brand_loyalty'] = features['brand_loyalty'].fillna(0.6)
        features['price_sensitivity'] = features['price_sensitivity'].fillna(0.5)
        features['convenience_preference'] = features['convenience_preference'].fillna(0.6)
        
        # Features de sazonalidade
        features['seasonal_factor'] = features['seasonal_factor'].fillna(1.0)
        features['holiday_impact'] = features['holiday_impact'].fillna(0)
        features['weather_impact'] = features['weather_impact'].fillna(0)
        features['event_impact'] = features['event_impact'].fillna(0)
        
        # Features de inovação
        features['innovation_rate'] = features['innovation_rate'].fillna(0.3)
        features['disruption_level'] = features['disruption_level'].fillna(0.2)
        features['new_entrants'] = features['new_entrants'].fillna(0)
        features['product_launches'] = features['product_launches'].fillna(0)
        features['technology_breakthroughs'] = features['technology_breakthroughs'].fillna(0)
        
        # Features de mídia e buzz
        features['media_coverage'] = features['media_coverage'].fillna(0)
        features['social_media_buzz'] = features['social_media_buzz'].fillna(0)
        features['influencer_mentions'] = features['influencer_mentions'].fillna(0)
        features['viral_content'] = features['viral_content'].fillna(0)
        features['brand_mentions'] = features['brand_mentions'].fillna(0)
        
        # Features de supply chain
        features['supply_chain_disruption'] = features['supply_chain_disruption'].fillna(0)
        features['raw_material_costs'] = features['raw_material_costs'].fillna(0)
        features['logistics_costs'] = features['logistics_costs'].fillna(0)
        features['inventory_levels'] = features['inventory_levels'].fillna(0.5)
        features['delivery_times'] = features['delivery_times'].fillna(3.0)
        
        # Features temporais
        features['date'] = pd.to_datetime(features['date'])
        features['day_of_week'] = features['date'].dt.dayofweek
        features['month'] = features['date'].dt.month
        features['quarter'] = features['date'].dt.quarter
        features['year'] = features['date'].dt.year
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Calcular métricas de tendência
        features = self._calculate_trend_metrics(features)
        
        return features
    
    def _calculate_trend_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula métricas de tendência para detecção de mudanças de mercado
        """
        # Agrupar por mercado/indústria para calcular tendências
        for group_name, group_data in data.groupby('market_segment'):
            if len(group_data) > 1:
                # Calcular médias móveis
                group_data = group_data.sort_values('date')
                
                # Search volume trends
                group_data['search_volume_ma_7'] = group_data['search_volume'].rolling(7, min_periods=1).mean()
                group_data['search_volume_ma_30'] = group_data['search_volume'].rolling(30, min_periods=1).mean()
                group_data['search_volume_std_7'] = group_data['search_volume'].rolling(7, min_periods=1).std()
                
                # CPC trends
                group_data['cpc_ma_7'] = group_data['cpc'].rolling(7, min_periods=1).mean()
                group_data['cpc_ma_30'] = group_data['cpc'].rolling(30, min_periods=1).mean()
                group_data['cpc_std_7'] = group_data['cpc'].rolling(7, min_periods=1).std()
                
                # Competition trends
                group_data['competition_ma_7'] = group_data['competition_intensity'].rolling(7, min_periods=1).mean()
                group_data['competition_ma_30'] = group_data['competition_intensity'].rolling(30, min_periods=1).mean()
                
                # Atualizar dados originais
                data.loc[group_data.index] = group_data
        
        # Preencher valores NaN
        trend_columns = ['search_volume_ma_7', 'search_volume_ma_30', 'search_volume_std_7',
                        'cpc_ma_7', 'cpc_ma_30', 'cpc_std_7',
                        'competition_ma_7', 'competition_ma_30']
        
        for col in trend_columns:
            if col in data.columns:
                data[col] = data[col].fillna(data[col].mean())
        
        return data
    
    def establish_market_baselines(self, data: pd.DataFrame) -> Dict:
        """
        Estabelece baselines para cada segmento de mercado
        """
        logger.info("Estabelecendo baselines de mercado")
        
        baselines = {}
        
        # Baselines por segmento de mercado
        for segment, group_data in data.groupby('market_segment'):
            if len(group_data) > 7:  # Pelo menos 7 dias de dados
                baselines[segment] = {}
                
                # Métricas principais
                metrics = ['search_volume', 'cpc', 'competition_intensity', 
                          'conversion_rate', 'technology_adoption']
                
                for metric in metrics:
                    if metric in group_data.columns:
                        recent_data = group_data.tail(90)[metric]  # Últimos 90 dias
                        if len(recent_data) > 0:
                            baselines[segment][metric] = {
                                'baseline': recent_data.mean(),
                                'std': recent_data.std(),
                                'min': recent_data.min(),
                                'max': recent_data.max(),
                                'trend': recent_data.diff().mean()
                            }
        
        self.market_baselines = baselines
        
        return baselines
    
    def detect_market_changes(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta mudanças anômalas no mercado
        """
        logger.info("Detectando mudanças de mercado")
        
        # Estabelecer baselines se não existirem
        if not self.market_baselines:
            self.establish_market_baselines(data)
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para detecção de mudanças
        change_features = [
            'search_volume_change', 'search_volume_trend', 'search_volume_volatility',
            'intent_shift', 'competition_intensity', 'market_saturation',
            'cpc_change', 'cpm_change', 'price_volatility', 'conversion_rate_change',
            'customer_acquisition_cost', 'roas', 'technology_adoption',
            'mobile_usage', 'voice_search_adoption', 'ai_adoption',
            'regulatory_changes', 'regulatory_risk', 'economic_growth',
            'inflation_rate', 'consumer_confidence', 'consumer_preferences',
            'purchasing_power', 'price_sensitivity', 'seasonal_factor',
            'innovation_rate', 'disruption_level', 'new_entrants',
            'media_coverage', 'social_media_buzz', 'supply_chain_disruption',
            'search_volume_ma_7', 'search_volume_ma_30', 'search_volume_std_7',
            'cpc_ma_7', 'cpc_ma_30', 'cpc_std_7',
            'competition_ma_7', 'competition_ma_30'
        ]
        
        # Filtrar features disponíveis
        available_features = [f for f in change_features if f in features.columns]
        X = features[available_features].fillna(0)
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Detectar mudanças
        change_scores = self.isolation_forest.fit_predict(X_scaled)
        change_scores = np.where(change_scores == -1, 1, 0)  # Converter para 0/1
        
        # Adicionar resultados aos dados
        features['market_change_detected'] = change_scores
        features['change_score'] = self.isolation_forest.decision_function(X_scaled)
        
        return features
    
    def classify_change_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica tipos de mudanças de mercado
        """
        logger.info("Classificando tipos de mudanças de mercado")
        
        # Detectar mudanças
        features = self.detect_market_changes(data)
        
        # Classificar tipos de mudança
        change_types = []
        impact_levels = []
        response_strategies = []
        
        for idx, row in features.iterrows():
            change_type = self._classify_change_type(row)
            impact_level = self._assess_market_impact(row)
            response_strategy = self._determine_response_strategy(row)
            
            change_types.append(change_type)
            impact_levels.append(impact_level)
            response_strategies.append(response_strategy)
        
        features['change_type'] = change_types
        features['impact_level'] = impact_levels
        features['response_strategy'] = response_strategies
        
        return features
    
    def _classify_change_type(self, row: pd.Series) -> str:
        """
        Classifica o tipo de mudança de mercado
        """
        # Mudanças de demanda
        if row['search_volume_change'] > 0.5:
            return 'Demand Surge'
        elif row['search_volume_change'] < -0.3:
            return 'Demand Decline'
        
        # Mudanças de competição
        elif row['competition_intensity'] > 0.8:
            return 'Competition Intensification'
        elif row['new_entrants'] > 0:
            return 'New Market Entrants'
        
        # Mudanças de preços
        elif row['cpc_change'] > 0.3:
            return 'Price Inflation'
        elif row['cpc_change'] < -0.2:
            return 'Price Deflation'
        
        # Mudanças tecnológicas
        elif row['technology_adoption'] > 0.8:
            return 'Technology Disruption'
        elif row['ai_adoption'] > 0.7:
            return 'AI Adoption Wave'
        elif row['voice_search_adoption'] > 0.6:
            return 'Voice Search Adoption'
        
        # Mudanças regulatórias
        elif row['regulatory_changes'] > 0:
            return 'Regulatory Changes'
        elif row['privacy_regulations'] > 0.7:
            return 'Privacy Regulation Impact'
        
        # Mudanças econômicas
        elif row['economic_growth'] < -0.02:
            return 'Economic Downturn'
        elif row['inflation_rate'] > 0.05:
            return 'Inflation Pressure'
        elif row['consumer_confidence'] < 40:
            return 'Consumer Confidence Drop'
        
        # Mudanças de comportamento
        elif row['consumer_preferences'] > 0.8:
            return 'Consumer Preference Shift'
        elif row['price_sensitivity'] > 0.8:
            return 'Price Sensitivity Increase'
        
        # Mudanças de inovação
        elif row['innovation_rate'] > 0.7:
            return 'Innovation Wave'
        elif row['disruption_level'] > 0.6:
            return 'Market Disruption'
        
        # Mudanças de supply chain
        elif row['supply_chain_disruption'] > 0:
            return 'Supply Chain Disruption'
        
        # Mudanças de mídia
        elif row['media_coverage'] > 0.7:
            return 'Media Attention Surge'
        elif row['social_media_buzz'] > 0.8:
            return 'Social Media Viral'
        
        else:
            return 'Minor Market Fluctuation'
    
    def _assess_market_impact(self, row: pd.Series) -> str:
        """
        Avalia o nível de impacto da mudança de mercado
        """
        # Calcular score de impacto
        impact_score = 0
        
        # Impacto de demanda
        if abs(row['search_volume_change']) > 0.5:
            impact_score += 3
        elif abs(row['search_volume_change']) > 0.3:
            impact_score += 2
        elif abs(row['search_volume_change']) > 0.1:
            impact_score += 1
        
        # Impacto de competição
        if row['competition_intensity'] > 0.8 or row['new_entrants'] > 0:
            impact_score += 3
        
        # Impacto de preços
        if abs(row['cpc_change']) > 0.3:
            impact_score += 2
        
        # Impacto tecnológico
        if row['technology_adoption'] > 0.8 or row['ai_adoption'] > 0.7:
            impact_score += 3
        
        # Impacto regulatório
        if row['regulatory_changes'] > 0 or row['privacy_regulations'] > 0.7:
            impact_score += 3
        
        # Impacto econômico
        if row['economic_growth'] < -0.02 or row['inflation_rate'] > 0.05:
            impact_score += 3
        
        # Impacto de inovação
        if row['innovation_rate'] > 0.7 or row['disruption_level'] > 0.6:
            impact_score += 3
        
        # Classificar impacto
        if impact_score >= 6:
            return 'High Market Impact'
        elif impact_score >= 4:
            return 'Medium Market Impact'
        elif impact_score >= 2:
            return 'Low Market Impact'
        else:
            return 'Minimal Market Impact'
    
    def _determine_response_strategy(self, row: pd.Series) -> str:
        """
        Determina estratégia de resposta à mudança de mercado
        """
        change_type = row['change_type']
        impact_level = row['impact_level']
        
        # Mudanças que requerem resposta imediata
        immediate_changes = [
            'Demand Surge', 'Demand Decline', 'Competition Intensification',
            'Technology Disruption', 'Regulatory Changes', 'Economic Downturn',
            'Market Disruption', 'Supply Chain Disruption'
        ]
        
        # Mudanças que requerem adaptação estratégica
        strategic_changes = [
            'New Market Entrants', 'AI Adoption Wave', 'Voice Search Adoption',
            'Privacy Regulation Impact', 'Consumer Preference Shift',
            'Innovation Wave', 'Media Attention Surge'
        ]
        
        if change_type in immediate_changes or impact_level == 'High Market Impact':
            return 'Immediate Strategic Response Required'
        elif change_type in strategic_changes or impact_level == 'Medium Market Impact':
            return 'Strategic Adaptation Needed'
        else:
            return 'Monitor and Gradual Adjustment'
    
    def generate_market_alerts(self, data: pd.DataFrame) -> List[Dict]:
        """
        Gera alertas sobre mudanças de mercado
        """
        logger.info("Gerando alertas de mudanças de mercado")
        
        alerts = []
        
        # Filtrar apenas mudanças detectadas
        changes = data[data['market_change_detected'] == 1]
        
        for idx, row in changes.iterrows():
            alert = {
                'timestamp': row['date'],
                'market_segment': row['market_segment'],
                'change_type': row['change_type'],
                'impact_level': row['impact_level'],
                'response_strategy': row['response_strategy'],
                'search_volume_change': row['search_volume_change'],
                'cpc_change': row['cpc_change'],
                'competition_intensity': row['competition_intensity'],
                'change_score': row['change_score'],
                'recommended_action': self._get_recommended_action(row)
            }
            
            alerts.append(alert)
        
        # Ordenar por impacto e score de mudança
        impact_order = {
            'High Market Impact': 3,
            'Medium Market Impact': 2,
            'Low Market Impact': 1,
            'Minimal Market Impact': 0
        }
        
        alerts.sort(key=lambda x: (impact_order[x['impact_level']], x['change_score']), reverse=True)
        
        return alerts
    
    def _get_recommended_action(self, row: pd.Series) -> str:
        """
        Gera ação recomendada baseada no tipo de mudança
        """
        change_type = row['change_type']
        
        if change_type == 'Demand Surge':
            return 'Scale up operations and increase marketing investment'
        elif change_type == 'Demand Decline':
            return 'Analyze market conditions and adjust strategy accordingly'
        elif change_type == 'Competition Intensification':
            return 'Strengthen competitive positioning and differentiate offerings'
        elif change_type == 'Technology Disruption':
            return 'Invest in new technologies and adapt business model'
        elif change_type == 'Regulatory Changes':
            return 'Review compliance requirements and adjust operations'
        elif change_type == 'Economic Downturn':
            return 'Optimize costs and focus on value propositions'
        elif change_type == 'Market Disruption':
            return 'Innovate and adapt business model to new market conditions'
        elif change_type == 'Supply Chain Disruption':
            return 'Diversify suppliers and optimize inventory management'
        elif change_type == 'Consumer Preference Shift':
            return 'Analyze new preferences and adjust product/service offerings'
        elif change_type == 'AI Adoption Wave':
            return 'Invest in AI capabilities and automation'
        else:
            return 'Monitor trends and maintain current strategy'
    
    def get_market_insights(self, data: pd.DataFrame) -> Dict:
        """
        Gera insights sobre mudanças de mercado
        """
        insights = {
            'total_changes_detected': len(data[data['market_change_detected'] == 1]),
            'change_detection_rate': data['market_change_detected'].mean(),
            'change_types_distribution': data['change_type'].value_counts().to_dict(),
            'impact_levels_distribution': data['impact_level'].value_counts().to_dict(),
            'response_strategies_distribution': data['response_strategy'].value_counts().to_dict(),
            'markets_with_changes': data[data['market_change_detected'] == 1]['market_segment'].nunique(),
            'avg_search_volume_change': data[data['market_change_detected'] == 1]['search_volume_change'].mean(),
            'avg_cpc_change': data[data['market_change_detected'] == 1]['cpc_change'].mean(),
            'avg_competition_intensity': data[data['market_change_detected'] == 1]['competition_intensity'].mean(),
            'immediate_response_needed': len(data[(data['market_change_detected'] == 1) & 
                                               (data['response_strategy'] == 'Immediate Strategic Response Required')]),
            'high_impact_changes': len(data[(data['market_change_detected'] == 1) & 
                                          (data['impact_level'] == 'High Market Impact')])
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
            'market_baselines': self.market_baselines
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
            self.market_baselines = model_data['market_baselines']
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'market_segment': [f'segment_{i % 10}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'search_volume': np.random.poisson(10000, n_samples),
        'search_volume_change': np.random.uniform(-0.8, 0.8, n_samples),
        'search_volume_trend': np.random.uniform(-0.2, 0.3, n_samples),
        'search_volume_volatility': np.random.uniform(0, 1, n_samples),
        'long_tail_ratio': np.random.uniform(0, 1, n_samples),
        'commercial_intent': np.random.uniform(0, 1, n_samples),
        'informational_intent': np.random.uniform(0, 1, n_samples),
        'navigational_intent': np.random.uniform(0, 1, n_samples),
        'transactional_intent': np.random.uniform(0, 1, n_samples),
        'intent_shift': np.random.uniform(-0.3, 0.3, n_samples),
        'competitor_count': np.random.randint(5, 100, n_samples),
        'competition_intensity': np.random.uniform(0, 1, n_samples),
        'market_saturation': np.random.uniform(0, 1, n_samples),
        'barrier_to_entry': np.random.uniform(0, 1, n_samples),
        'competitive_dynamics': np.random.uniform(0, 1, n_samples),
        'cpc': np.random.uniform(0.5, 10, n_samples),
        'cpc_change': np.random.uniform(-0.5, 0.5, n_samples),
        'cpm': np.random.uniform(2, 20, n_samples),
        'cpm_change': np.random.uniform(-0.3, 0.3, n_samples),
        'price_volatility': np.random.uniform(0, 1, n_samples),
        'conversion_rate': np.random.uniform(0.01, 0.05, n_samples),
        'conversion_rate_change': np.random.uniform(-0.3, 0.3, n_samples),
        'customer_acquisition_cost': np.random.uniform(20, 200, n_samples),
        'lifetime_value': np.random.uniform(100, 1000, n_samples),
        'roas': np.random.uniform(1, 5, n_samples),
        'technology_adoption': np.random.uniform(0, 1, n_samples),
        'mobile_usage': np.random.uniform(0.4, 0.9, n_samples),
        'voice_search_adoption': np.random.uniform(0, 1, n_samples),
        'ai_adoption': np.random.uniform(0, 1, n_samples),
        'automation_level': np.random.uniform(0, 1, n_samples),
        'regulatory_changes': np.random.randint(0, 2, n_samples),
        'compliance_requirements': np.random.uniform(0, 1, n_samples),
        'privacy_regulations': np.random.uniform(0, 1, n_samples),
        'data_protection': np.random.uniform(0, 1, n_samples),
        'regulatory_risk': np.random.uniform(0, 1, n_samples),
        'economic_growth': np.random.uniform(-0.05, 0.05, n_samples),
        'inflation_rate': np.random.uniform(0.01, 0.08, n_samples),
        'interest_rate': np.random.uniform(0.02, 0.08, n_samples),
        'consumer_confidence': np.random.uniform(30, 70, n_samples),
        'unemployment_rate': np.random.uniform(0.03, 0.08, n_samples),
        'consumer_preferences': np.random.uniform(0, 1, n_samples),
        'purchasing_power': np.random.uniform(0.5, 1.0, n_samples),
        'brand_loyalty': np.random.uniform(0.3, 0.9, n_samples),
        'price_sensitivity': np.random.uniform(0, 1, n_samples),
        'convenience_preference': np.random.uniform(0.4, 0.9, n_samples),
        'seasonal_factor': np.random.uniform(0.8, 1.2, n_samples),
        'holiday_impact': np.random.randint(0, 2, n_samples),
        'weather_impact': np.random.uniform(0, 1, n_samples),
        'event_impact': np.random.randint(0, 2, n_samples),
        'innovation_rate': np.random.uniform(0, 1, n_samples),
        'disruption_level': np.random.uniform(0, 1, n_samples),
        'new_entrants': np.random.randint(0, 3, n_samples),
        'product_launches': np.random.randint(0, 2, n_samples),
        'technology_breakthroughs': np.random.randint(0, 2, n_samples),
        'media_coverage': np.random.uniform(0, 1, n_samples),
        'social_media_buzz': np.random.uniform(0, 1, n_samples),
        'influencer_mentions': np.random.randint(0, 10, n_samples),
        'viral_content': np.random.randint(0, 2, n_samples),
        'brand_mentions': np.random.randint(0, 50, n_samples),
        'supply_chain_disruption': np.random.randint(0, 2, n_samples),
        'raw_material_costs': np.random.uniform(0, 1, n_samples),
        'logistics_costs': np.random.uniform(0, 1, n_samples),
        'inventory_levels': np.random.uniform(0, 1, n_samples),
        'delivery_times': np.random.uniform(1, 7, n_samples)
    })
    
    # Inicializar detector
    detector = MarketChangeDetector()
    
    # Classificar mudanças
    results = detector.classify_change_types(sample_data)
    
    # Gerar alertas
    alerts = detector.generate_market_alerts(results)
    
    # Gerar insights
    insights = detector.get_market_insights(results)
    
    print("=== INSIGHTS DE DETECÇÃO DE MUDANÇAS DE MERCADO ===")
    print(f"Total de mudanças detectadas: {insights['total_changes_detected']}")
    print(f"Taxa de detecção de mudanças: {insights['change_detection_rate']:.2%}")
    print(f"Segmentos com mudanças: {insights['markets_with_changes']}")
    print(f"Respostas imediatas necessárias: {insights['immediate_response_needed']}")
    print(f"Mudanças de alto impacto: {insights['high_impact_changes']}")
    
    print("\n=== DISTRIBUIÇÃO DE TIPOS DE MUDANÇA ===")
    for change_type, count in insights['change_types_distribution'].items():
        print(f"{change_type}: {count}")
    
    print("\n=== TOP 5 ALERTAS DE MERCADO ===")
    for alert in alerts[:5]:
        print(f"{alert['market_segment']} - {alert['change_type']} ({alert['impact_level']}): {alert['response_strategy']}") 