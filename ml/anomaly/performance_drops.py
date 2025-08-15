"""
Sistema de Detecção de Quedas de Performance usando Machine Learning
Monitora e detecta anomalias em métricas de performance de SEO
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

class PerformanceDropDetector:
    """
    Sistema de detecção de quedas de performance
    """
    
    def __init__(self, model_path: str = "models/performance_drop_detector.pkl"):
        self.model_path = model_path
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.thresholds = {}
        self.performance_baselines = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para detecção de quedas de performance
        """
        features = data.copy()
        
        # Features de ranking
        features['ranking_position'] = features['ranking_position'].fillna(100)
        features['ranking_change'] = features['ranking_change'].fillna(0)
        features['ranking_velocity'] = features['ranking_velocity'].fillna(0)
        features['ranking_acceleration'] = features['ranking_acceleration'].fillna(0)
        
        # Features de tráfego
        features['organic_traffic'] = features['organic_traffic'].fillna(0)
        features['traffic_change'] = features['traffic_change'].fillna(0)
        features['traffic_velocity'] = features['traffic_velocity'].fillna(0)
        features['traffic_acceleration'] = features['traffic_acceleration'].fillna(0)
        
        # Features de conversão
        features['conversion_rate'] = features['conversion_rate'].fillna(0.02)
        features['conversion_change'] = features['conversion_change'].fillna(0)
        features['revenue'] = features['revenue'].fillna(0)
        features['revenue_change'] = features['revenue_change'].fillna(0)
        
        # Features de engajamento
        features['click_through_rate'] = features['click_through_rate'].fillna(0.05)
        features['bounce_rate'] = features['bounce_rate'].fillna(0.5)
        features['time_on_site'] = features['time_on_site'].fillna(120)
        features['pages_per_session'] = features['pages_per_session'].fillna(2.0)
        
        # Features de backlinks
        features['backlink_count'] = features['backlink_count'].fillna(0)
        features['backlink_change'] = features['backlink_change'].fillna(0)
        features['domain_authority'] = features['domain_authority'].fillna(0)
        features['page_authority'] = features['page_authority'].fillna(0)
        
        # Features de conteúdo
        features['content_age'] = features['content_age'].fillna(365)
        features['content_updates'] = features['content_updates'].fillna(0)
        features['content_quality_score'] = features['content_quality_score'].fillna(0.7)
        
        # Features técnicas
        features['page_speed'] = features['page_speed'].fillna(3.0)
        features['mobile_friendly'] = features['mobile_friendly'].fillna(1)
        features['ssl_secure'] = features['ssl_secure'].fillna(1)
        features['core_web_vitals'] = features['core_web_vitals'].fillna(0.8)
        
        # Features de competição
        features['competitor_activity'] = features['competitor_activity'].fillna(0)
        features['market_share'] = features['market_share'].fillna(0.1)
        features['competition_intensity'] = features['competition_intensity'].fillna(0.5)
        
        # Features temporais
        features['date'] = pd.to_datetime(features['date'])
        features['day_of_week'] = features['date'].dt.dayofweek
        features['month'] = features['date'].dt.month
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Calcular métricas de tendência
        features = self._calculate_trend_metrics(features)
        
        return features
    
    def _calculate_trend_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula métricas de tendência para detecção de anomalias
        """
        # Agrupar por keyword/page para calcular tendências
        for group_name, group_data in data.groupby(['keyword', 'page_url']):
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
                
                # Conversion trends
                group_data['conversion_ma_7'] = group_data['conversion_rate'].rolling(7, min_periods=1).mean()
                group_data['conversion_ma_30'] = group_data['conversion_rate'].rolling(30, min_periods=1).mean()
                
                # Atualizar dados originais
                data.loc[group_data.index] = group_data
        
        # Preencher valores NaN
        trend_columns = ['ranking_ma_7', 'ranking_ma_30', 'ranking_std_7', 
                        'traffic_ma_7', 'traffic_ma_30', 'traffic_std_7',
                        'conversion_ma_7', 'conversion_ma_30']
        
        for col in trend_columns:
            if col in data.columns:
                data[col] = data[col].fillna(data[col].mean())
        
        return data
    
    def establish_baselines(self, data: pd.DataFrame) -> Dict:
        """
        Estabelece baselines de performance para cada métrica
        """
        logger.info("Estabelecendo baselines de performance")
        
        baselines = {}
        
        # Baselines por métrica
        metrics = ['ranking_position', 'organic_traffic', 'conversion_rate', 
                  'click_through_rate', 'bounce_rate', 'time_on_site']
        
        for metric in metrics:
            if metric in data.columns:
                # Calcular estatísticas
                mean_val = data[metric].mean()
                std_val = data[metric].std()
                median_val = data[metric].median()
                
                baselines[metric] = {
                    'mean': mean_val,
                    'std': std_val,
                    'median': median_val,
                    'lower_bound': mean_val - 2 * std_val,
                    'upper_bound': mean_val + 2 * std_val
                }
        
        # Baselines por keyword/page
        keyword_baselines = {}
        for (keyword, page_url), group_data in data.groupby(['keyword', 'page_url']):
            if len(group_data) > 7:  # Pelo menos 7 dias de dados
                keyword_baselines[f"{keyword}_{page_url}"] = {}
                
                for metric in metrics:
                    if metric in group_data.columns:
                        recent_data = group_data.tail(30)[metric]  # Últimos 30 dias
                        if len(recent_data) > 0:
                            keyword_baselines[f"{keyword}_{page_url}"][metric] = {
                                'baseline': recent_data.mean(),
                                'std': recent_data.std(),
                                'min': recent_data.min(),
                                'max': recent_data.max()
                            }
        
        self.performance_baselines = {
            'global': baselines,
            'keyword_specific': keyword_baselines
        }
        
        return self.performance_baselines
    
    def detect_anomalies(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta anomalias usando Isolation Forest
        """
        logger.info("Detectando anomalias de performance")
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para detecção de anomalias
        anomaly_features = [
            'ranking_position', 'ranking_change', 'ranking_velocity', 'ranking_acceleration',
            'organic_traffic', 'traffic_change', 'traffic_velocity', 'traffic_acceleration',
            'conversion_rate', 'conversion_change', 'revenue', 'revenue_change',
            'click_through_rate', 'bounce_rate', 'time_on_site', 'pages_per_session',
            'backlink_count', 'backlink_change', 'domain_authority', 'page_authority',
            'content_age', 'content_updates', 'content_quality_score',
            'page_speed', 'mobile_friendly', 'ssl_secure', 'core_web_vitals',
            'competitor_activity', 'market_share', 'competition_intensity',
            'ranking_ma_7', 'ranking_ma_30', 'ranking_std_7',
            'traffic_ma_7', 'traffic_ma_30', 'traffic_std_7',
            'conversion_ma_7', 'conversion_ma_30'
        ]
        
        # Filtrar features disponíveis
        available_features = [f for f in anomaly_features if f in features.columns]
        X = features[available_features].fillna(0)
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Detectar anomalias
        anomaly_scores = self.isolation_forest.fit_predict(X_scaled)
        anomaly_scores = np.where(anomaly_scores == -1, 1, 0)  # Converter para 0/1
        
        # Adicionar resultados aos dados
        features['anomaly_detected'] = anomaly_scores
        features['anomaly_score'] = self.isolation_forest.decision_function(X_scaled)
        
        return features
    
    def classify_performance_drops(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica tipos de quedas de performance
        """
        logger.info("Classificando tipos de quedas de performance")
        
        # Estabelecer baselines se não existirem
        if not self.performance_baselines:
            self.establish_baselines(data)
        
        # Preparar dados
        features = self.prepare_features(data)
        
        # Detectar anomalias
        features = self.detect_anomalies(features)
        
        # Classificar tipos de queda
        drop_types = []
        severity_levels = []
        root_causes = []
        
        for idx, row in features.iterrows():
            drop_type = self._classify_drop_type(row)
            severity = self._calculate_severity(row)
            root_cause = self._identify_root_cause(row)
            
            drop_types.append(drop_type)
            severity_levels.append(severity)
            root_causes.append(root_cause)
        
        features['drop_type'] = drop_types
        features['severity_level'] = severity_levels
        features['root_cause'] = root_causes
        
        return features
    
    def _classify_drop_type(self, row: pd.Series) -> str:
        """
        Classifica o tipo de queda de performance
        """
        # Verificar ranking drops
        if row['ranking_change'] > 10:
            return 'Ranking Drop'
        elif row['traffic_change'] < -0.3:
            return 'Traffic Drop'
        elif row['conversion_change'] < -0.2:
            return 'Conversion Drop'
        elif row['revenue_change'] < -0.25:
            return 'Revenue Drop'
        elif row['bounce_rate'] > 0.8:
            return 'Engagement Drop'
        else:
            return 'Minor Fluctuation'
    
    def _calculate_severity(self, row: pd.Series) -> str:
        """
        Calcula o nível de severidade da queda
        """
        # Calcular score de severidade
        severity_score = 0
        
        # Ranking severity
        if row['ranking_change'] > 20:
            severity_score += 3
        elif row['ranking_change'] > 10:
            severity_score += 2
        elif row['ranking_change'] > 5:
            severity_score += 1
        
        # Traffic severity
        if row['traffic_change'] < -0.5:
            severity_score += 3
        elif row['traffic_change'] < -0.3:
            severity_score += 2
        elif row['traffic_change'] < -0.1:
            severity_score += 1
        
        # Conversion severity
        if row['conversion_change'] < -0.4:
            severity_score += 3
        elif row['conversion_change'] < -0.2:
            severity_score += 2
        elif row['conversion_change'] < -0.1:
            severity_score += 1
        
        # Classificar severidade
        if severity_score >= 6:
            return 'Critical'
        elif severity_score >= 4:
            return 'High'
        elif severity_score >= 2:
            return 'Medium'
        else:
            return 'Low'
    
    def _identify_root_cause(self, row: pd.Series) -> str:
        """
        Identifica a causa raiz da queda de performance
        """
        # Verificar causas técnicas
        if row['page_speed'] > 5:
            return 'Technical Issues - Slow Page Speed'
        elif row['mobile_friendly'] == 0:
            return 'Technical Issues - Not Mobile Friendly'
        elif row['ssl_secure'] == 0:
            return 'Technical Issues - No SSL'
        elif row['core_web_vitals'] < 0.5:
            return 'Technical Issues - Poor Core Web Vitals'
        
        # Verificar causas de conteúdo
        elif row['content_age'] > 365:
            return 'Content Issues - Outdated Content'
        elif row['content_quality_score'] < 0.5:
            return 'Content Issues - Low Quality Content'
        elif row['content_updates'] == 0:
            return 'Content Issues - No Recent Updates'
        
        # Verificar causas de competição
        elif row['competitor_activity'] > 0.8:
            return 'Competition Issues - High Competitor Activity'
        elif row['competition_intensity'] > 0.8:
            return 'Competition Issues - Intense Competition'
        
        # Verificar causas de backlinks
        elif row['backlink_change'] < -10:
            return 'Backlink Issues - Lost Backlinks'
        elif row['domain_authority'] < 20:
            return 'Backlink Issues - Low Domain Authority'
        
        # Verificar causas de algoritmo
        elif row['ranking_velocity'] < -5:
            return 'Algorithm Issues - Algorithm Update Impact'
        
        else:
            return 'Unknown - Requires Investigation'
    
    def generate_alerts(self, data: pd.DataFrame) -> List[Dict]:
        """
        Gera alertas baseados nas anomalias detectadas
        """
        logger.info("Gerando alertas de performance")
        
        alerts = []
        
        # Filtrar apenas anomalias detectadas
        anomalies = data[data['anomaly_detected'] == 1]
        
        for idx, row in anomalies.iterrows():
            alert = {
                'timestamp': row['date'],
                'keyword': row['keyword'],
                'page_url': row['page_url'],
                'drop_type': row['drop_type'],
                'severity_level': row['severity_level'],
                'root_cause': row['root_cause'],
                'ranking_change': row['ranking_change'],
                'traffic_change': row['traffic_change'],
                'conversion_change': row['conversion_change'],
                'anomaly_score': row['anomaly_score'],
                'recommended_action': self._get_recommended_action(row)
            }
            
            alerts.append(alert)
        
        # Ordenar por severidade e score de anomalia
        alerts.sort(key=lambda x: (x['severity_level'], x['anomaly_score']), reverse=True)
        
        return alerts
    
    def _get_recommended_action(self, row: pd.Series) -> str:
        """
        Gera ação recomendada baseada na causa raiz
        """
        root_cause = row['root_cause']
        
        if 'Technical Issues' in root_cause:
            return 'Immediate technical audit and optimization required'
        elif 'Content Issues' in root_cause:
            return 'Content update and optimization needed'
        elif 'Competition Issues' in root_cause:
            return 'Competitive analysis and strategy adjustment required'
        elif 'Backlink Issues' in root_cause:
            return 'Backlink audit and link building strategy needed'
        elif 'Algorithm Issues' in root_cause:
            return 'Algorithm update analysis and adaptation required'
        else:
            return 'Comprehensive audit and investigation needed'
    
    def get_performance_insights(self, data: pd.DataFrame) -> Dict:
        """
        Gera insights sobre as quedas de performance
        """
        insights = {
            'total_anomalies': len(data[data['anomaly_detected'] == 1]),
            'anomaly_rate': data['anomaly_detected'].mean(),
            'drop_types_distribution': data['drop_type'].value_counts().to_dict(),
            'severity_distribution': data['severity_level'].value_counts().to_dict(),
            'root_causes_distribution': data['root_cause'].value_counts().to_dict(),
            'avg_ranking_change': data[data['anomaly_detected'] == 1]['ranking_change'].mean(),
            'avg_traffic_change': data[data['anomaly_detected'] == 1]['traffic_change'].mean(),
            'avg_conversion_change': data[data['anomaly_detected'] == 1]['conversion_change'].mean(),
            'critical_issues': len(data[(data['anomaly_detected'] == 1) & (data['severity_level'] == 'Critical')]),
            'high_priority_issues': len(data[(data['anomaly_detected'] == 1) & (data['severity_level'] == 'High')])
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
            'performance_baselines': self.performance_baselines
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
            self.performance_baselines = model_data['performance_baselines']
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
        'page_url': [f'page_{i % 20}' for i in range(n_samples)],
        'date': pd.date_range('2024-01-01', periods=n_samples, freq='D'),
        'ranking_position': np.random.randint(1, 101, n_samples),
        'ranking_change': np.random.randint(-30, 31, n_samples),
        'ranking_velocity': np.random.uniform(-10, 10, n_samples),
        'ranking_acceleration': np.random.uniform(-5, 5, n_samples),
        'organic_traffic': np.random.poisson(1000, n_samples),
        'traffic_change': np.random.uniform(-0.8, 0.5, n_samples),
        'traffic_velocity': np.random.uniform(-100, 100, n_samples),
        'traffic_acceleration': np.random.uniform(-50, 50, n_samples),
        'conversion_rate': np.random.uniform(0.01, 0.05, n_samples),
        'conversion_change': np.random.uniform(-0.5, 0.3, n_samples),
        'revenue': np.random.uniform(0, 10000, n_samples),
        'revenue_change': np.random.uniform(-0.6, 0.4, n_samples),
        'click_through_rate': np.random.uniform(0.02, 0.08, n_samples),
        'bounce_rate': np.random.uniform(0.3, 0.8, n_samples),
        'time_on_site': np.random.uniform(60, 300, n_samples),
        'pages_per_session': np.random.uniform(1, 5, n_samples),
        'backlink_count': np.random.randint(0, 1000, n_samples),
        'backlink_change': np.random.randint(-50, 51, n_samples),
        'domain_authority': np.random.uniform(0, 100, n_samples),
        'page_authority': np.random.uniform(0, 100, n_samples),
        'content_age': np.random.randint(1, 1000, n_samples),
        'content_updates': np.random.randint(0, 10, n_samples),
        'content_quality_score': np.random.uniform(0.3, 1.0, n_samples),
        'page_speed': np.random.uniform(1, 8, n_samples),
        'mobile_friendly': np.random.choice([0, 1], n_samples),
        'ssl_secure': np.random.choice([0, 1], n_samples),
        'core_web_vitals': np.random.uniform(0.3, 1.0, n_samples),
        'competitor_activity': np.random.uniform(0, 1, n_samples),
        'market_share': np.random.uniform(0, 1, n_samples),
        'competition_intensity': np.random.uniform(0, 1, n_samples)
    })
    
    # Inicializar detector
    detector = PerformanceDropDetector()
    
    # Classificar quedas de performance
    results = detector.classify_performance_drops(sample_data)
    
    # Gerar alertas
    alerts = detector.generate_alerts(results)
    
    # Gerar insights
    insights = detector.get_performance_insights(results)
    
    print("=== INSIGHTS DE DETECÇÃO DE QUEDAS DE PERFORMANCE ===")
    print(f"Total de anomalias detectadas: {insights['total_anomalies']}")
    print(f"Taxa de anomalias: {insights['anomaly_rate']:.2%}")
    print(f"Issues críticos: {insights['critical_issues']}")
    print(f"Issues de alta prioridade: {insights['high_priority_issues']}")
    
    print("\n=== DISTRIBUIÇÃO DE TIPOS DE QUEDA ===")
    for drop_type, count in insights['drop_types_distribution'].items():
        print(f"{drop_type}: {count}")
    
    print("\n=== TOP 5 ALERTAS CRÍTICAS ===")
    for alert in alerts[:5]:
        print(f"{alert['keyword']} - {alert['drop_type']} ({alert['severity_level']}): {alert['root_cause']}") 