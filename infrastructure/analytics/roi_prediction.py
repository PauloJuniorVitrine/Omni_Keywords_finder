"""
Sistema de ROI Prediction para Keywords
Tracing ID: LONGTAIL-045
Data: 2024-12-20
Descrição: Sistema de predição de ROI usando XGBoost e features avançadas
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ROIModelType(Enum):
    """Tipos de modelos de ROI"""
    XGBOOST = "xgboost"
    RANDOM_FOREST = "random_forest"
    LIGHTGBM = "lightgbm"
    ENSEMBLE = "ensemble"

@dataclass
class ROIFeatures:
    """Features para predição de ROI"""
    search_volume: float
    cpc: float
    competition: float
    keyword_length: int
    word_count: int
    has_brand: bool
    has_location: bool
    has_intent: bool
    seasonal_factor: float
    trend_score: float
    difficulty_score: float
    conversion_rate: float
    avg_position: float
    click_through_rate: float
    quality_score: float

@dataclass
class ROIPrediction:
    """Predição de ROI"""
    keyword: str
    predicted_roi: float
    confidence_score: float
    roi_range: Tuple[float, float]
    features: ROIFeatures
    model_used: str
    timestamp: datetime
    recommendations: List[str]

@dataclass
class ROIModelConfig:
    """Configuração do modelo de ROI"""
    model_type: ROIModelType
    target_roi_threshold: float = 2.0
    min_confidence: float = 0.7
    feature_importance_threshold: float = 0.05
    cross_validation_folds: int = 5
    hyperparameter_tuning: bool = True
    ensemble_method: str = "voting"
    prediction_horizon_days: int = 90

class ROIFeatureEngineer:
    """Engenheiro de features para ROI"""
    
    def __init__(self):
        self.brand_keywords = set()
        self.location_keywords = set()
        self.intent_keywords = set()
        self.seasonal_patterns = {}
        
    def load_reference_data(self, brand_file: str = None, location_file: str = None):
        """Carrega dados de referência para features"""
        # Carrega palavras-chave de marca
        if brand_file and Path(brand_file).exists():
            with open(brand_file, 'r') as f:
                self.brand_keywords = set(line.strip().lower() for line in f)
        
        # Carrega palavras-chave de localização
        if location_file and Path(location_file).exists():
            with open(location_file, 'r') as f:
                self.location_keywords = set(line.strip().lower() for line in f)
        
        # Palavras-chave de intenção
        self.intent_keywords = {
            'buy', 'purchase', 'order', 'shop', 'store', 'price', 'cost',
            'cheap', 'discount', 'sale', 'deal', 'offer', 'best', 'top',
            'review', 'compare', 'vs', 'versus', 'alternative', 'guide',
            'how to', 'tutorial', 'tips', 'advice', 'help'
        }
        
        # Padrões sazonais (exemplo)
        self.seasonal_patterns = {
            'christmas': [11, 12],
            'black_friday': [11],
            'summer': [6, 7, 8],
            'winter': [12, 1, 2],
            'back_to_school': [8, 9]
        }
    
    def extract_features(self, keyword_data: pd.DataFrame) -> pd.DataFrame:
        """Extrai features avançadas para predição de ROI"""
        logger.info("Extraindo features para predição de ROI...")
        
        features_df = keyword_data.copy()
        
        # Features básicas
        features_df['keyword_length'] = features_df['keyword'].str.len()
        features_df['word_count'] = features_df['keyword'].str.split().str.len()
        
        # Features de marca
        features_df['has_brand'] = features_df['keyword'].str.lower().apply(
            lambda value: any(brand in value for brand in self.brand_keywords)
        )
        
        # Features de localização
        features_df['has_location'] = features_df['keyword'].str.lower().apply(
            lambda value: any(loc in value for loc in self.location_keywords)
        )
        
        # Features de intenção
        features_df['has_intent'] = features_df['keyword'].str.lower().apply(
            lambda value: any(intent in value for intent in self.intent_keywords)
        )
        
        # Features sazonais
        current_month = datetime.now().month
        features_df['seasonal_factor'] = features_df['keyword'].apply(
            lambda value: self._calculate_seasonal_factor(value, current_month)
        )
        
        # Features de tendência (simuladas)
        features_df['trend_score'] = np.random.uniform(0.1, 1.0, len(features_df))
        
        # Features de dificuldade
        features_df['difficulty_score'] = self._calculate_difficulty_score(features_df)
        
        # Features de conversão (simuladas)
        features_df['conversion_rate'] = np.random.uniform(0.01, 0.15, len(features_df))
        
        # Features de posição média (simuladas)
        features_df['avg_position'] = np.random.uniform(1, 20, len(features_df))
        
        # Features de CTR (simuladas)
        features_df['click_through_rate'] = np.random.uniform(0.01, 0.10, len(features_df))
        
        # Score de qualidade composto
        features_df['quality_score'] = self._calculate_quality_score(features_df)
        
        # Features derivadas
        features_df['volume_cpc_ratio'] = features_df['search_volume'] / (features_df['cpc'] + 1e-6)
        features_df['competition_difficulty'] = features_df['competition'] * features_df['difficulty_score']
        features_df['conversion_potential'] = features_df['conversion_rate'] * features_df['trend_score']
        
        logger.info(f"Features extraídas: {features_df.shape}")
        return features_df
    
    def _calculate_seasonal_factor(self, keyword: str, current_month: int) -> float:
        """Calcula fator sazonal para keyword"""
        keyword_lower = keyword.lower()
        
        for season, months in self.seasonal_patterns.items():
            if season in keyword_lower:
                if current_month in months:
                    return 1.5  # Alta temporada
                else:
                    return 0.7  # Baixa temporada
        
        return 1.0  # Neutro
    
    def _calculate_difficulty_score(self, df: pd.DataFrame) -> pd.Series:
        """Calcula score de dificuldade baseado em múltiplos fatores"""
        # Fórmula de dificuldade
        difficulty = (
            df['competition'] * 0.4 +
            (df['cpc'] / 10) * 0.3 +
            (df['word_count'] / 10) * 0.2 +
            (1 - df['trend_score']) * 0.1
        )
        
        return np.clip(difficulty, 0.1, 1.0)
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> pd.Series:
        """Calcula score de qualidade composto"""
        quality = (
            df['search_volume'] * 0.3 +
            (1 - df['competition']) * 0.25 +
            df['conversion_rate'] * 0.2 +
            df['trend_score'] * 0.15 +
            (1 / (df['cpc'] + 1e-6)) * 0.1
        )
        
        # Normaliza para 0-1
        return (quality - quality.min()) / (quality.max() - quality.min() + 1e-6)

class ROICalculator:
    """Calculadora de ROI real"""
    
    def __init__(self, config: Dict[str, float]):
        self.config = config
    
    def calculate_roi(self, keyword_data: pd.DataFrame) -> pd.Series:
        """Calcula ROI real para keywords"""
        # Fórmula de ROI: (Receita - Custo) / Custo
        
        # Receita estimada
        revenue = (
            keyword_data['search_volume'] *
            keyword_data['click_through_rate'] *
            keyword_data['conversion_rate'] *
            keyword_data.get('avg_order_value', 100)  # Valor médio do pedido
        )
        
        # Custo estimado
        cost = (
            keyword_data['search_volume'] *
            keyword_data['click_through_rate'] *
            keyword_data['cpc']
        )
        
        # ROI
        roi = (revenue - cost) / (cost + 1e-6)
        
        return np.clip(roi, 0.0, 50.0)  # Limita ROI entre 0 e 50

class ROIModelTrainer:
    """Treinador de modelos de ROI"""
    
    def __init__(self, config: ROIModelConfig):
        self.config = config
        self.models = {}
        self.best_model = None
        self.feature_importance = {}
        
    def train(self, X_train: pd.DataFrame, y_train: pd.Series,
              X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Treina modelos de ROI"""
        logger.info("Treinando modelos de ROI...")
        
        results = {}
        
        if self.config.model_type == ROIModelType.XGBOOST:
            results['xgboost'] = self._train_xgboost(X_train, y_train, X_val, y_val)
        
        elif self.config.model_type == ROIModelType.RANDOM_FOREST:
            results['random_forest'] = self._train_random_forest(X_train, y_train, X_val, y_val)
        
        elif self.config.model_type == ROIModelType.LIGHTGBM:
            results['lightgbm'] = self._train_lightgbm(X_train, y_train, X_val, y_val)
        
        elif self.config.model_type == ROIModelType.ENSEMBLE:
            results = self._train_ensemble(X_train, y_train, X_val, y_val)
        
        # Seleciona melhor modelo
        best_score = 0
        for name, result in results.items():
            if result['val_score'] > best_score:
                best_score = result['val_score']
                self.best_model = result['model']
        
        logger.info(f"Melhor modelo: {best_score:.4f}")
        return results
    
    def _train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                       X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Treina modelo XGBoost"""
        try:
            import xgboost as xgb
            
            # Parâmetros otimizados para ROI
            params = {
                'objective': 'reg:squarederror',
                'n_estimators': 200,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'early_stopping_rounds': 20
            }
            
            # Treina modelo
            model = xgb.XGBRegressor(**params)
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False
            )
            
            # Avalia
            train_score = model.score(X_train, y_train)
            val_score = model.score(X_val, y_val)
            
            # Feature importance
            importance = dict(zip(X_train.columns, model.feature_importances_))
            
            return {
                'model': model,
                'train_score': train_score,
                'val_score': val_score,
                'feature_importance': importance
            }
            
        except ImportError:
            logger.warning("XGBoost não disponível, usando RandomForest")
            return self._train_random_forest(X_train, y_train, X_val, y_val)
    
    def _train_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series,
                            X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Treina modelo Random Forest"""
        from sklearn.ensemble import RandomForestRegressor
        
        params = {
            'n_estimators': 200,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42
        }
        
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        
        train_score = model.score(X_train, y_train)
        val_score = model.score(X_val, y_val)
        
        importance = dict(zip(X_train.columns, model.feature_importances_))
        
        return {
            'model': model,
            'train_score': train_score,
            'val_score': val_score,
            'feature_importance': importance
        }
    
    def _train_lightgbm(self, X_train: pd.DataFrame, y_train: pd.Series,
                        X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Treina modelo LightGBM"""
        try:
            import lightgbm as lgb
            
            params = {
                'objective': 'regression',
                'metric': 'rmse',
                'num_leaves': 31,
                'learning_rate': 0.1,
                'feature_fraction': 0.8,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': -1
            }
            
            train_data = lgb.Dataset(X_train, label=y_train)
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            
            model = lgb.train(
                params,
                train_data,
                valid_sets=[val_data],
                num_boost_round=200,
                early_stopping_rounds=20,
                verbose_eval=False
            )
            
            # Converte para formato sklearn
            from lightgbm import LGBMRegressor
            sklearn_model = LGBMRegressor()
            sklearn_model.fit(X_train, y_train)
            
            train_score = sklearn_model.score(X_train, y_train)
            val_score = sklearn_model.score(X_val, y_val)
            
            importance = dict(zip(X_train.columns, sklearn_model.feature_importances_))
            
            return {
                'model': sklearn_model,
                'train_score': train_score,
                'val_score': val_score,
                'feature_importance': importance
            }
            
        except ImportError:
            logger.warning("LightGBM não disponível, usando RandomForest")
            return self._train_random_forest(X_train, y_train, X_val, y_val)
    
    def _train_ensemble(self, X_train: pd.DataFrame, y_train: pd.Series,
                        X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Any]:
        """Treina ensemble de modelos"""
        from sklearn.ensemble import VotingRegressor
        
        # Treina modelos individuais
        xgb_result = self._train_xgboost(X_train, y_train, X_val, y_val)
        rf_result = self._train_random_forest(X_train, y_train, X_val, y_val)
        
        # Cria ensemble
        ensemble = VotingRegressor([
            ('xgboost', xgb_result['model']),
            ('random_forest', rf_result['model'])
        ])
        
        ensemble.fit(X_train, y_train)
        
        train_score = ensemble.score(X_train, y_train)
        val_score = ensemble.score(X_val, y_val)
        
        # Combina feature importance
        importance = {}
        for feature in X_train.columns:
            importance[feature] = (
                xgb_result['feature_importance'].get(feature, 0) * 0.6 +
                rf_result['feature_importance'].get(feature, 0) * 0.4
            )
        
        return {
            'ensemble': {
                'model': ensemble,
                'train_score': train_score,
                'val_score': val_score,
                'feature_importance': importance
            }
        }

class ROIPredictor:
    """Preditor de ROI"""
    
    def __init__(self, model: Any, feature_importance: Dict[str, float],
                 config: ROIModelConfig):
        self.model = model
        self.feature_importance = feature_importance
        self.config = config
        self.feature_engineer = ROIFeatureEngineer()
        
    def predict_roi(self, keyword_data: pd.DataFrame) -> List[ROIPrediction]:
        """Prediz ROI para keywords"""
        logger.info("Predizendo ROI para keywords...")
        
        # Extrai features
        features_df = self.feature_engineer.extract_features(keyword_data)
        
        # Seleciona features para predição
        feature_columns = [
            'search_volume', 'cpc', 'competition', 'keyword_length', 'word_count',
            'has_brand', 'has_location', 'has_intent', 'seasonal_factor',
            'trend_score', 'difficulty_score', 'conversion_rate',
            'avg_position', 'click_through_rate', 'quality_score',
            'volume_cpc_ratio', 'competition_difficulty', 'conversion_potential'
        ]
        
        X = features_df[feature_columns].fillna(0)
        
        # Predições
        predictions = self.model.predict(X)
        
        # Calcula intervalos de confiança (simplificado)
        confidence_scores = self._calculate_confidence_scores(X, predictions)
        
        # Gera resultados
        results = []
        for index, (_, row) in enumerate(keyword_data.iterrows()):
            roi_pred = predictions[index]
            confidence = confidence_scores[index]
            
            # Calcula intervalo de ROI
            roi_range = (
                max(0, roi_pred - roi_pred * 0.3),
                roi_pred + roi_pred * 0.3
            )
            
            # Features para este keyword
            features = ROIFeatures(
                search_volume=row['search_volume'],
                cpc=row['cpc'],
                competition=row['competition'],
                keyword_length=len(row['keyword']),
                word_count=len(row['keyword'].split()),
                has_brand=features_df.iloc[index]['has_brand'],
                has_location=features_df.iloc[index]['has_location'],
                has_intent=features_df.iloc[index]['has_intent'],
                seasonal_factor=features_df.iloc[index]['seasonal_factor'],
                trend_score=features_df.iloc[index]['trend_score'],
                difficulty_score=features_df.iloc[index]['difficulty_score'],
                conversion_rate=features_df.iloc[index]['conversion_rate'],
                avg_position=features_df.iloc[index]['avg_position'],
                click_through_rate=features_df.iloc[index]['click_through_rate'],
                quality_score=features_df.iloc[index]['quality_score']
            )
            
            # Recomendações
            recommendations = self._generate_recommendations(
                roi_pred, confidence, features
            )
            
            result = ROIPrediction(
                keyword=row['keyword'],
                predicted_roi=roi_pred,
                confidence_score=confidence,
                roi_range=roi_range,
                features=features,
                model_used=self.config.model_type.value,
                timestamp=datetime.now(),
                recommendations=recommendations
            )
            
            results.append(result)
        
        logger.info(f"ROI predito para {len(results)} keywords")
        return results
    
    def _calculate_confidence_scores(self, X: pd.DataFrame, predictions: np.ndarray) -> np.ndarray:
        """Calcula scores de confiança para predições"""
        # Implementação simplificada baseada na variância dos dados
        # Em produção, usar métodos como conformal prediction
        
        # Baseado na qualidade das features
        feature_quality = X['quality_score'].values
        volume_factor = np.log1p(X['search_volume'].values) / 10
        
        confidence = np.clip(
            feature_quality * 0.7 + volume_factor * 0.3,
            0.1, 1.0
        )
        
        return confidence
    
    def _generate_recommendations(self, roi: float, confidence: float, 
                                 features: ROIFeatures) -> List[str]:
        """Gera recomendações baseadas na predição"""
        recommendations = []
        
        if roi < self.config.target_roi_threshold:
            recommendations.append("ROI abaixo do threshold recomendado")
        
        if confidence < self.config.min_confidence:
            recommendations.append("Baixa confiança na predição")
        
        if features.competition > 0.8:
            recommendations.append("Alta competição - considere nichos alternativos")
        
        if features.cpc > 5.0:
            recommendations.append("CPC alto - avalie custo-benefício")
        
        if features.search_volume < 100:
            recommendations.append("Volume de busca baixo - potencial limitado")
        
        if features.trend_score > 0.8:
            recommendations.append("Tendência positiva - oportunidade de crescimento")
        
        if features.seasonal_factor > 1.2:
            recommendations.append("Fator sazonal favorável")
        
        if not recommendations:
            recommendations.append("Keyword com bom potencial de ROI")
        
        return recommendations

class ROIAnalytics:
    """Analytics avançados de ROI"""
    
    def __init__(self):
        self.historical_data = []
    
    def analyze_roi_trends(self, predictions: List[ROIPrediction]) -> Dict[str, Any]:
        """Analisa tendências de ROI"""
        logger.info("Analisando tendências de ROI...")
        
        roi_values = [p.predicted_roi for p in predictions]
        confidence_values = [p.confidence_score for p in predictions]
        
        analysis = {
            'total_keywords': len(predictions),
            'avg_roi': np.mean(roi_values),
            'median_roi': np.median(roi_values),
            'roi_std': np.std(roi_values),
            'avg_confidence': np.mean(confidence_values),
            'high_roi_keywords': len([r for r in roi_values if r > 5.0]),
            'low_roi_keywords': len([r for r in roi_values if r < 1.0]),
            'roi_distribution': {
                'excellent': len([r for r in roi_values if r > 10.0]),
                'good': len([r for r in roi_values if 5.0 <= r <= 10.0]),
                'moderate': len([r for r in roi_values if 2.0 <= r < 5.0]),
                'poor': len([r for r in roi_values if r < 2.0])
            }
        }
        
        return analysis
    
    def generate_roi_report(self, predictions: List[ROIPrediction]) -> Dict[str, Any]:
        """Gera relatório completo de ROI"""
        logger.info("Gerando relatório de ROI...")
        
        # Análise de tendências
        trends = self.analyze_roi_trends(predictions)
        
        # Top keywords por ROI
        top_keywords = sorted(predictions, key=lambda value: value.predicted_roi, reverse=True)[:10]
        
        # Keywords por confiança
        high_confidence = [p for p in predictions if p.confidence_score > 0.8]
        
        # Análise de features
        feature_analysis = self._analyze_features(predictions)
        
        report = {
            'summary': trends,
            'top_keywords': [
                {
                    'keyword': p.keyword,
                    'roi': p.predicted_roi,
                    'confidence': p.confidence_score,
                    'recommendations': p.recommendations
                }
                for p in top_keywords
            ],
            'high_confidence_keywords': len(high_confidence),
            'feature_analysis': feature_analysis,
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def _analyze_features(self, predictions: List[ROIPrediction]) -> Dict[str, Any]:
        """Analisa correlação entre features e ROI"""
        feature_data = {
            'search_volume': [p.features.search_volume for p in predictions],
            'cpc': [p.features.cpc for p in predictions],
            'competition': [p.features.competition for p in predictions],
            'trend_score': [p.features.trend_score for p in predictions],
            'quality_score': [p.features.quality_score for p in predictions]
        }
        
        roi_values = [p.predicted_roi for p in predictions]
        
        correlations = {}
        for feature, values in feature_data.items():
            correlation = np.corrcoef(values, roi_values)[0, 1]
            correlations[feature] = correlation if not np.isnan(correlation) else 0.0
        
        return {
            'correlations': correlations,
            'feature_insights': self._generate_feature_insights(correlations)
        }
    
    def _generate_feature_insights(self, correlations: Dict[str, float]) -> List[str]:
        """Gera insights baseados nas correlações"""
        insights = []
        
        for feature, corr in correlations.items():
            if abs(corr) > 0.3:
                if corr > 0:
                    insights.append(f"{feature} tem correlação positiva forte com ROI")
                else:
                    insights.append(f"{feature} tem correlação negativa forte com ROI")
        
        return insights

class ROIPredictionSystem:
    """Sistema principal de predição de ROI"""
    
    def __init__(self, config: ROIModelConfig):
        self.config = config
        self.feature_engineer = ROIFeatureEngineer()
        self.roi_calculator = ROICalculator({})
        self.trainer = ROIModelTrainer(config)
        self.predictor = None
        self.analytics = ROIAnalytics()
        
    def train_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Treina modelo de predição de ROI"""
        logger.info("Iniciando treinamento do modelo de ROI...")
        
        # Extrai features
        features_df = self.feature_engineer.extract_features(training_data)
        
        # Calcula ROI real (se disponível)
        if 'actual_roi' not in training_data.columns:
            training_data['actual_roi'] = self.roi_calculator.calculate_roi(training_data)
        
        # Seleciona features para treinamento
        feature_columns = [
            'search_volume', 'cpc', 'competition', 'keyword_length', 'word_count',
            'has_brand', 'has_location', 'has_intent', 'seasonal_factor',
            'trend_score', 'difficulty_score', 'conversion_rate',
            'avg_position', 'click_through_rate', 'quality_score',
            'volume_cpc_ratio', 'competition_difficulty', 'conversion_potential'
        ]
        
        X = features_df[feature_columns].fillna(0)
        result = training_data['actual_roi']
        
        # Split dos dados
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, result, test_size=0.2, random_state=42
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        # Treina modelo
        training_results = self.trainer.train(X_train, y_train, X_val, y_val)
        
        # Configura preditor
        best_result = None
        for name, result in training_results.items():
            if best_result is None or result['val_score'] > best_result['val_score']:
                best_result = result
        
        if best_result:
            self.predictor = ROIPredictor(
                best_result['model'],
                best_result['feature_importance'],
                self.config
            )
        
        logger.info("Modelo de ROI treinado com sucesso")
        return training_results
    
    def predict_roi(self, keyword_data: pd.DataFrame) -> List[ROIPrediction]:
        """Prediz ROI para keywords"""
        if self.predictor is None:
            raise ValueError("Modelo não treinado. Execute train_model() primeiro.")
        
        return self.predictor.predict_roi(keyword_data)
    
    def generate_report(self, predictions: List[ROIPrediction]) -> Dict[str, Any]:
        """Gera relatório completo"""
        return self.analytics.generate_roi_report(predictions)
    
    def save_model(self, filepath: str):
        """Salva modelo treinado"""
        if self.predictor is None:
            raise ValueError("Nenhum modelo para salvar")
        
        model_data = {
            'model': self.predictor.model,
            'feature_importance': self.predictor.feature_importance,
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Modelo salvo em: {filepath}")
    
    def load_model(self, filepath: str):
        """Carrega modelo treinado"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.predictor = ROIPredictor(
            model_data['model'],
            model_data['feature_importance'],
            model_data['config']
        )
        
        logger.info(f"Modelo carregado de: {filepath}")

# Função de conveniência para uso rápido
def predict_keyword_roi(keyword_data: pd.DataFrame, 
                       model_type: ROIModelType = ROIModelType.XGBOOST,
                       training_data: pd.DataFrame = None) -> List[ROIPrediction]:
    """
    Função de conveniência para predição de ROI
    
    Args:
        keyword_data: Dados das keywords para predição
        model_type: Tipo de modelo a usar
        training_data: Dados de treinamento (opcional)
    
    Returns:
        Lista de predições de ROI
    """
    config = ROIModelConfig(model_type=model_type)
    system = ROIPredictionSystem(config)
    
    # Se dados de treinamento fornecidos, treina modelo
    if training_data is not None:
        system.train_model(training_data)
    else:
        # Usa modelo pré-treinado ou treina com dados simulados
        simulated_data = _generate_simulated_training_data()
        system.train_model(simulated_data)
    
    # Prediz ROI
    predictions = system.predict_roi(keyword_data)
    
    return predictions

def _generate_simulated_training_data() -> pd.DataFrame:
    """Gera dados simulados para treinamento"""
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'keyword': [f"keyword_{index}" for index in range(n_samples)],
        'search_volume': np.random.randint(100, 10000, n_samples),
        'cpc': np.random.uniform(0.1, 10.0, n_samples),
        'competition': np.random.uniform(0.1, 1.0, n_samples),
        'conversion_rate': np.random.uniform(0.01, 0.15, n_samples),
        'avg_order_value': np.random.uniform(50, 500, n_samples)
    }
    
    # Calcula ROI real
    df = pd.DataFrame(data)
    revenue = df['search_volume'] * 0.05 * df['conversion_rate'] * df['avg_order_value']
    cost = df['search_volume'] * 0.05 * df['cpc']
    df['actual_roi'] = (revenue - cost) / (cost + 1e-6)
    
    return df

if __name__ == "__main__":
    # Exemplo de uso
    keyword_data = pd.DataFrame({
        'keyword': ['melhor smartphone 2024', 'comprar notebook barato', 'curso online python'],
        'search_volume': [5000, 3000, 8000],
        'cpc': [2.5, 1.8, 3.2],
        'competition': [0.7, 0.5, 0.8]
    })
    
    try:
        predictions = predict_keyword_roi(keyword_data)
        
        print("Predições de ROI:")
        for pred in predictions:
            print(f"Keyword: {pred.keyword}")
            print(f"ROI Predito: {pred.predicted_roi:.2f}")
            print(f"Confiança: {pred.confidence_score:.2f}")
            print(f"Recomendações: {pred.recommendations}")
            print("-" * 50)
        
        # Gera relatório
        system = ROIPredictionSystem(ROIModelConfig(model_type=ROIModelType.XGBOOST))
        report = system.generate_report(predictions)
        
        print(f"\nRelatório de ROI:")
        print(f"Total de keywords: {report['summary']['total_keywords']}")
        print(f"ROI médio: {report['summary']['avg_roi']:.2f}")
        print(f"Keywords com alto ROI: {report['summary']['high_roi_keywords']}")
        
    except Exception as e:
        print(f"Erro na predição: {e}") 