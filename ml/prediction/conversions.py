"""
Sistema de Predição de Conversões usando Machine Learning
Prediz taxas de conversão e otimiza funil de conversão
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversionPredictor:
    """
    Sistema de predição de conversões para otimização de funil
    """
    
    def __init__(self, model_path: str = "models/conversion_predictor.pkl"):
        self.model_path = model_path
        self.models = {
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'logistic_regression': LogisticRegression(random_state=42)
        }
        self.best_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_importance = {}
        self.conversion_funnel = {}
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara features para predição de conversões
        """
        features = data.copy()
        
        # Features demográficas
        features['age_group'] = features['age_group'].fillna('unknown')
        features['gender'] = features['gender'].fillna('unknown')
        features['location'] = features['location'].fillna('unknown')
        features['device_type'] = features['device_type'].fillna('unknown')
        
        # Features de comportamento
        features['session_duration'] = features['session_duration'].fillna(0)
        features['pages_visited'] = features['pages_visited'].fillna(1)
        features['bounce_rate'] = features['bounce_rate'].fillna(0.5)
        features['time_on_page'] = features['time_on_page'].fillna(30)
        features['scroll_depth'] = features['scroll_depth'].fillna(0.5)
        
        # Features de engajamento
        features['clicks_on_cta'] = features['clicks_on_cta'].fillna(0)
        features['form_interactions'] = features['form_interactions'].fillna(0)
        features['video_watches'] = features['video_watches'].fillna(0)
        features['downloads'] = features['downloads'].fillna(0)
        features['social_shares'] = features['social_shares'].fillna(0)
        
        # Features de fonte de tráfego
        features['traffic_source'] = features['traffic_source'].fillna('direct')
        features['campaign_name'] = features['campaign_name'].fillna('organic')
        features['keyword'] = features['keyword'].fillna('unknown')
        features['ad_group'] = features['ad_group'].fillna('unknown')
        
        # Features de página
        features['page_type'] = features['page_type'].fillna('unknown')
        features['page_load_time'] = features['page_load_time'].fillna(3.0)
        features['mobile_friendly'] = features['mobile_friendly'].fillna(1)
        features['ssl_secure'] = features['ssl_secure'].fillna(1)
        
        # Features de conteúdo
        features['content_length'] = features['content_length'].fillna(500)
        features['has_video'] = features['has_video'].fillna(0)
        features['has_images'] = features['has_images'].fillna(1)
        features['has_testimonials'] = features['has_testimonials'].fillna(0)
        features['has_social_proof'] = features['has_social_proof'].fillna(0)
        
        # Features de preço e oferta
        features['price'] = features['price'].fillna(0)
        features['discount_percentage'] = features['discount_percentage'].fillna(0)
        features['free_shipping'] = features['free_shipping'].fillna(0)
        features['money_back_guarantee'] = features['money_back_guarantee'].fillna(0)
        
        # Features de urgência
        features['limited_time_offer'] = features['limited_time_offer'].fillna(0)
        features['stock_availability'] = features['stock_availability'].fillna(1)
        features['countdown_timer'] = features['countdown_timer'].fillna(0)
        
        # Features de confiança
        features['trust_badges'] = features['trust_badges'].fillna(0)
        features['security_indicators'] = features['security_indicators'].fillna(0)
        features['customer_reviews'] = features['customer_reviews'].fillna(0)
        features['rating_score'] = features['rating_score'].fillna(0)
        
        # Features de personalização
        features['personalized_content'] = features['personalized_content'].fillna(0)
        features['recommendation_engine'] = features['recommendation_engine'].fillna(0)
        features['dynamic_pricing'] = features['dynamic_pricing'].fillna(0)
        
        # Features de experiência do usuário
        features['checkout_steps'] = features['checkout_steps'].fillna(3)
        features['form_fields'] = features['form_fields'].fillna(5)
        features['payment_options'] = features['payment_options'].fillna(3)
        features['guest_checkout'] = features['guest_checkout'].fillna(1)
        
        # Features de retargeting
        features['retargeting_campaign'] = features['retargeting_campaign'].fillna(0)
        features['email_sequence'] = features['email_sequence'].fillna(0)
        features['abandoned_cart_recovery'] = features['abandoned_cart_recovery'].fillna(0)
        
        # Features temporais
        features['hour_of_day'] = pd.to_datetime(features['timestamp']).dt.hour
        features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
        features['month'] = pd.to_datetime(features['timestamp']).dt.month
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Encoding de variáveis categóricas
        categorical_features = [
            'age_group', 'gender', 'location', 'device_type', 'traffic_source',
            'campaign_name', 'keyword', 'ad_group', 'page_type'
        ]
        
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
    
    def analyze_conversion_funnel(self, data: pd.DataFrame) -> Dict:
        """
        Analisa o funil de conversão
        """
        logger.info("Analisando funil de conversão")
        
        # Estágios do funil
        funnel_stages = {
            'visitors': len(data),
            'engaged_visitors': len(data[data['session_duration'] > 60]),
            'page_viewers': len(data[data['pages_visited'] > 1]),
            'cta_clickers': len(data[data['clicks_on_cta'] > 0]),
            'form_starters': len(data[data['form_interactions'] > 0]),
            'form_completers': len(data[data['form_completed'] == 1]),
            'conversions': len(data[data['converted'] == 1])
        }
        
        # Calcular taxas de conversão entre estágios
        conversion_rates = {}
        stages = list(funnel_stages.keys())
        
        for i in range(len(stages) - 1):
            current_stage = stages[i]
            next_stage = stages[i + 1]
            rate = funnel_stages[next_stage] / funnel_stages[current_stage] if funnel_stages[current_stage] > 0 else 0
            conversion_rates[f"{current_stage}_to_{next_stage}"] = rate
        
        self.conversion_funnel = {
            'stages': funnel_stages,
            'conversion_rates': conversion_rates
        }
        
        return self.conversion_funnel
    
    def train_model(self, training_data: pd.DataFrame) -> Dict:
        """
        Treina modelos de predição de conversões
        """
        logger.info("Iniciando treinamento dos modelos de predição de conversões")
        
        # Analisar funil de conversão
        self.analyze_conversion_funnel(training_data)
        
        # Preparar dados
        features = self.prepare_features(training_data)
        
        # Features para treinamento
        feature_columns = [
            'age_group', 'gender', 'location', 'device_type', 'session_duration',
            'pages_visited', 'bounce_rate', 'time_on_page', 'scroll_depth',
            'clicks_on_cta', 'form_interactions', 'video_watches', 'downloads',
            'social_shares', 'traffic_source', 'campaign_name', 'keyword',
            'ad_group', 'page_type', 'page_load_time', 'mobile_friendly',
            'ssl_secure', 'content_length', 'has_video', 'has_images',
            'has_testimonials', 'has_social_proof', 'price', 'discount_percentage',
            'free_shipping', 'money_back_guarantee', 'limited_time_offer',
            'stock_availability', 'countdown_timer', 'trust_badges',
            'security_indicators', 'customer_reviews', 'rating_score',
            'personalized_content', 'recommendation_engine', 'dynamic_pricing',
            'checkout_steps', 'form_fields', 'payment_options', 'guest_checkout',
            'retargeting_campaign', 'email_sequence', 'abandoned_cart_recovery',
            'hour_of_day', 'day_of_week', 'month', 'is_weekend'
        ]
        
        X = features[feature_columns]
        y = features['converted']
        
        # Remover linhas com valores NaN
        mask = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[mask]
        y = y[mask]
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Treinar modelos
        results = {}
        for name, model in self.models.items():
            logger.info(f"Treinando modelo: {name}")
            
            # Treinar modelo
            model.fit(X_train, y_train)
            
            # Predições
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Métricas
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='roc_auc')
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'roc_auc': roc_auc,
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
        logger.info(f"ROC AUC: {results[best_model_name]['roc_auc']:.4f}")
        logger.info(f"F1 Score: {results[best_model_name]['f1']:.4f}")
        
        # Salvar modelo
        self.save_model()
        
        return results
    
    def predict_conversions(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prediz probabilidades de conversão
        """
        if self.best_model is None:
            raise ValueError("Modelo não treinado. Execute train_model() primeiro.")
        
        # Preparar features
        features = self.prepare_features(data)
        
        # Features para predição
        feature_columns = [
            'age_group', 'gender', 'location', 'device_type', 'session_duration',
            'pages_visited', 'bounce_rate', 'time_on_page', 'scroll_depth',
            'clicks_on_cta', 'form_interactions', 'video_watches', 'downloads',
            'social_shares', 'traffic_source', 'campaign_name', 'keyword',
            'ad_group', 'page_type', 'page_load_time', 'mobile_friendly',
            'ssl_secure', 'content_length', 'has_video', 'has_images',
            'has_testimonials', 'has_social_proof', 'price', 'discount_percentage',
            'free_shipping', 'money_back_guarantee', 'limited_time_offer',
            'stock_availability', 'countdown_timer', 'trust_badges',
            'security_indicators', 'customer_reviews', 'rating_score',
            'personalized_content', 'recommendation_engine', 'dynamic_pricing',
            'checkout_steps', 'form_fields', 'payment_options', 'guest_checkout',
            'retargeting_campaign', 'email_sequence', 'abandoned_cart_recovery',
            'hour_of_day', 'day_of_week', 'month', 'is_weekend'
        ]
        
        X = features[feature_columns]
        
        # Remover linhas com valores NaN
        mask = ~X.isnull().any(axis=1)
        X = X[mask]
        data_clean = data[mask].copy()
        
        # Normalizar features
        X_scaled = self.scaler.transform(X)
        
        # Predições
        conversion_probabilities = self.best_model.predict_proba(X_scaled)[:, 1]
        conversion_predictions = self.best_model.predict(X_scaled)
        
        # Adicionar predições aos dados
        data_clean['conversion_probability'] = conversion_probabilities
        data_clean['predicted_conversion'] = conversion_predictions
        data_clean['conversion_confidence'] = self._calculate_confidence(X_scaled)
        
        return data_clean
    
    def _calculate_confidence(self, X_scaled: np.ndarray) -> np.ndarray:
        """
        Calcula nível de confiança das predições
        """
        if hasattr(self.best_model, 'predict_proba'):
            probas = self.best_model.predict_proba(X_scaled)
            return np.max(probas, axis=1)
        else:
            return 1.0 - np.linalg.norm(X_scaled, axis=1) / np.max(np.linalg.norm(X_scaled, axis=1))
    
    def optimize_conversion_funnel(self, data: pd.DataFrame) -> Dict:
        """
        Otimiza o funil de conversão baseado nas predições
        """
        logger.info("Otimizando funil de conversão")
        
        # Fazer predições
        predictions = self.predict_conversions(data)
        
        # Identificar gargalos no funil
        bottlenecks = {}
        
        # Análise por estágio
        stages = ['visitors', 'engaged_visitors', 'page_viewers', 'cta_clickers', 'form_starters', 'form_completers']
        
        for i, stage in enumerate(stages[:-1]):
            next_stage = stages[i + 1]
            current_count = len(predictions[predictions[stage] == 1])
            next_count = len(predictions[predictions[next_stage] == 1])
            
            if current_count > 0:
                drop_rate = (current_count - next_count) / current_count
                bottlenecks[f"{stage}_to_{next_stage}"] = {
                    'drop_rate': drop_rate,
                    'current_count': current_count,
                    'next_count': next_count
                }
        
        # Recomendações de otimização
        recommendations = []
        
        # Otimização de CTA
        cta_clickers = predictions[predictions['clicks_on_cta'] > 0]
        if len(cta_clickers) > 0:
            avg_cta_prob = cta_clickers['conversion_probability'].mean()
            if avg_cta_prob < 0.3:
                recommendations.append({
                    'area': 'CTA Optimization',
                    'issue': 'Low conversion probability after CTA clicks',
                    'suggestion': 'Improve CTA design, placement, and messaging',
                    'priority': 'High'
                })
        
        # Otimização de formulários
        form_starters = predictions[predictions['form_interactions'] > 0]
        if len(form_starters) > 0:
            avg_form_prob = form_starters['conversion_probability'].mean()
            if avg_form_prob < 0.4:
                recommendations.append({
                    'area': 'Form Optimization',
                    'issue': 'Low conversion probability after form interactions',
                    'suggestion': 'Reduce form fields, improve UX, add progress indicators',
                    'priority': 'High'
                })
        
        # Otimização de página
        high_bounce = predictions[predictions['bounce_rate'] > 0.7]
        if len(high_bounce) > 0:
            recommendations.append({
                'area': 'Page Optimization',
                'issue': 'High bounce rate affecting conversions',
                'suggestion': 'Improve page load speed, content relevance, and user experience',
                'priority': 'Medium'
            })
        
        return {
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'conversion_opportunities': predictions[predictions['conversion_probability'] > 0.7]
        }
    
    def get_conversion_insights(self, predictions: pd.DataFrame) -> Dict:
        """
        Gera insights sobre as predições de conversão
        """
        insights = {
            'total_visitors': len(predictions),
            'predicted_conversions': predictions['predicted_conversion'].sum(),
            'conversion_rate': predictions['predicted_conversion'].mean(),
            'avg_conversion_probability': predictions['conversion_probability'].mean(),
            'high_probability_visitors': len(predictions[predictions['conversion_probability'] > 0.8]),
            'low_probability_visitors': len(predictions[predictions['conversion_probability'] < 0.2]),
            'top_conversion_factors': self._get_top_conversion_factors(),
            'conversion_by_source': predictions.groupby('traffic_source')['conversion_probability'].mean(),
            'conversion_by_device': predictions.groupby('device_type')['conversion_probability'].mean(),
            'conversion_by_time': predictions.groupby('hour_of_day')['conversion_probability'].mean()
        }
        
        return insights
    
    def _get_top_conversion_factors(self) -> Dict:
        """
        Identifica os principais fatores que influenciam conversões
        """
        if not self.feature_importance:
            return {}
        
        # Usar o melhor modelo para feature importance
        best_model_name = max(self.feature_importance.keys(), key=lambda k: 
                            self.feature_importance[k] if self.feature_importance[k] else {})
        
        if best_model_name in self.feature_importance:
            importance = self.feature_importance[best_model_name]
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_features[:10])
        
        return {}
    
    def save_model(self):
        """
        Salva modelo treinado
        """
        model_data = {
            'best_model': self.best_model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_importance': self.feature_importance,
            'conversion_funnel': self.conversion_funnel
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
            self.conversion_funnel = model_data['conversion_funnel']
            logger.info("Modelo carregado com sucesso")
        except FileNotFoundError:
            logger.warning("Modelo não encontrado. Execute train_model() primeiro.")


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'visitor_id': [f'visitor_{i}' for i in range(n_samples)],
        'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='H'),
        'converted': np.random.choice([0, 1], n_samples, p=[0.85, 0.15]),
        'age_group': np.random.choice(['18-24', '25-34', '35-44', '45-54', '55+'], n_samples),
        'gender': np.random.choice(['male', 'female', 'other'], n_samples),
        'location': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'PR'], n_samples),
        'device_type': np.random.choice(['desktop', 'mobile', 'tablet'], n_samples),
        'session_duration': np.random.exponential(300, n_samples),
        'pages_visited': np.random.poisson(3, n_samples),
        'bounce_rate': np.random.uniform(0.2, 0.8, n_samples),
        'time_on_page': np.random.exponential(60, n_samples),
        'scroll_depth': np.random.uniform(0.1, 1.0, n_samples),
        'clicks_on_cta': np.random.poisson(1, n_samples),
        'form_interactions': np.random.poisson(2, n_samples),
        'video_watches': np.random.poisson(0.5, n_samples),
        'downloads': np.random.poisson(0.2, n_samples),
        'social_shares': np.random.poisson(0.1, n_samples),
        'traffic_source': np.random.choice(['organic', 'paid', 'social', 'email', 'direct'], n_samples),
        'campaign_name': np.random.choice(['brand', 'generic', 'longtail', 'none'], n_samples),
        'keyword': np.random.choice(['keyword1', 'keyword2', 'keyword3', 'unknown'], n_samples),
        'ad_group': np.random.choice(['group1', 'group2', 'group3', 'none'], n_samples),
        'page_type': np.random.choice(['landing', 'product', 'blog', 'checkout'], n_samples),
        'page_load_time': np.random.exponential(2, n_samples),
        'mobile_friendly': np.random.choice([0, 1], n_samples),
        'ssl_secure': np.random.choice([0, 1], n_samples),
        'content_length': np.random.randint(100, 3000, n_samples),
        'has_video': np.random.choice([0, 1], n_samples),
        'has_images': np.random.choice([0, 1], n_samples),
        'has_testimonials': np.random.choice([0, 1], n_samples),
        'has_social_proof': np.random.choice([0, 1], n_samples),
        'price': np.random.uniform(0, 1000, n_samples),
        'discount_percentage': np.random.uniform(0, 50, n_samples),
        'free_shipping': np.random.choice([0, 1], n_samples),
        'money_back_guarantee': np.random.choice([0, 1], n_samples),
        'limited_time_offer': np.random.choice([0, 1], n_samples),
        'stock_availability': np.random.choice([0, 1], n_samples),
        'countdown_timer': np.random.choice([0, 1], n_samples),
        'trust_badges': np.random.randint(0, 5, n_samples),
        'security_indicators': np.random.randint(0, 3, n_samples),
        'customer_reviews': np.random.randint(0, 100, n_samples),
        'rating_score': np.random.uniform(0, 5, n_samples),
        'personalized_content': np.random.choice([0, 1], n_samples),
        'recommendation_engine': np.random.choice([0, 1], n_samples),
        'dynamic_pricing': np.random.choice([0, 1], n_samples),
        'checkout_steps': np.random.randint(1, 5, n_samples),
        'form_fields': np.random.randint(1, 10, n_samples),
        'payment_options': np.random.randint(1, 5, n_samples),
        'guest_checkout': np.random.choice([0, 1], n_samples),
        'retargeting_campaign': np.random.choice([0, 1], n_samples),
        'email_sequence': np.random.choice([0, 1], n_samples),
        'abandoned_cart_recovery': np.random.choice([0, 1], n_samples),
        'form_completed': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    })
    
    # Inicializar preditor
    predictor = ConversionPredictor()
    
    # Treinar modelo
    results = predictor.train_model(sample_data)
    
    # Fazer predições
    predictions = predictor.predict_conversions(sample_data.head(100))
    
    # Otimizar funil
    optimization = predictor.optimize_conversion_funnel(sample_data.head(100))
    
    # Gerar insights
    insights = predictor.get_conversion_insights(predictions)
    
    print("=== INSIGHTS DE PREDIÇÃO DE CONVERSÕES ===")
    print(f"Total de visitantes: {insights['total_visitors']}")
    print(f"Conversões previstas: {insights['predicted_conversions']}")
    print(f"Taxa de conversão: {insights['conversion_rate']:.2%}")
    print(f"Probabilidade média: {insights['avg_conversion_probability']:.2%}")
    print(f"Visitantes de alta probabilidade: {insights['high_probability_visitors']}")
    
    print("\n=== OTIMIZAÇÕES RECOMENDADAS ===")
    for rec in optimization['recommendations']:
        print(f"{rec['area']}: {rec['suggestion']} (Prioridade: {rec['priority']})") 