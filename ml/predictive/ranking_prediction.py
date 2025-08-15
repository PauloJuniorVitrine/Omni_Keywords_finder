# Ranking Prediction using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class RankingPredictor:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        self.scaler = StandardScaler()
        self.feature_names = []
        self.trained_models = {}
        self.feature_importance = {}
        
    def prepare_features(self, data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for ranking prediction"""
        features = []
        targets = []
        
        for entry in data:
            feature_vector = self._extract_features(entry)
            if feature_vector is not None:
                features.append(feature_vector)
                targets.append(entry.get('rank', 0))
        
        return np.array(features), np.array(targets)
    
    def _extract_features(self, entry: Dict[str, Any]) -> Optional[List[float]]:
        """Extract features from a data entry"""
        try:
            features = [
                entry.get('search_volume', 0),
                entry.get('competition', 0),
                entry.get('domain_authority', 0),
                entry.get('page_authority', 0),
                entry.get('backlinks', 0),
                entry.get('content_length', 0),
                entry.get('keyword_density', 0),
                entry.get('title_length', 0),
                entry.get('meta_description_length', 0),
                entry.get('internal_links', 0),
                entry.get('external_links', 0),
                entry.get('page_speed', 0),
                entry.get('mobile_friendly', 0),
                entry.get('ssl_secure', 0),
                entry.get('social_signals', 0),
                entry.get('time_on_page', 0),
                entry.get('bounce_rate', 0),
                entry.get('click_through_rate', 0)
            ]
            
            # Add time-based features
            if 'date' in entry:
                date = datetime.fromisoformat(entry['date'])
                features.extend([
                    date.weekday(),
                    date.month,
                    date.day,
                    date.hour
                ])
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def train_model(self, data: List[Dict[str, Any]], model_type: str = 'random_forest') -> Dict[str, Any]:
        """Train ranking prediction model"""
        if model_type not in self.models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Prepare features
        X, y = self.prepare_features(data)
        
        if len(X) == 0:
            return {'error': 'No valid data for training'}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        model = self.models[model_type]
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Get feature importance
        if hasattr(model, 'feature_importances_'):
            self.feature_importance[model_type] = model.feature_importances_
        
        # Store trained model
        self.trained_models[model_type] = model
        
        return {
            'model_type': model_type,
            'train_score': train_score,
            'test_score': test_score,
            'feature_count': X.shape[1],
            'sample_count': len(X)
        }
    
    def predict_ranking(self, features: Dict[str, Any], model_type: str = 'random_forest') -> Dict[str, Any]:
        """Predict ranking for given features"""
        if model_type not in self.trained_models:
            return {'error': f'Model {model_type} not trained'}
        
        # Extract features
        feature_vector = self._extract_features(features)
        if feature_vector is None:
            return {'error': 'Invalid features'}
        
        # Scale features
        feature_vector_scaled = self.scaler.transform([feature_vector])
        
        # Make prediction
        model = self.trained_models[model_type]
        predicted_rank = model.predict(feature_vector_scaled)[0]
        
        # Calculate confidence (simplified)
        confidence = self._calculate_prediction_confidence(feature_vector, model_type)
        
        return {
            'predicted_rank': max(1, int(predicted_rank)),
            'confidence': confidence,
            'model_type': model_type,
            'features_used': len(feature_vector)
        }
    
    def _calculate_prediction_confidence(self, features: List[float], model_type: str) -> float:
        """Calculate confidence in prediction"""
        # Simplified confidence calculation
        # In practice, you'd use model uncertainty or ensemble methods
        
        # Check feature completeness
        missing_features = sum(1 for f in features if f == 0)
        completeness = 1 - (missing_features / len(features))
        
        # Check feature values are in reasonable range
        reasonable_features = sum(1 for f in features if 0 <= f <= 1000)
        reasonableness = reasonable_features / len(features)
        
        confidence = (completeness + reasonableness) / 2
        return max(0.0, min(1.0, confidence))
    
    def predict_ranking_trend(self, keyword: str, historical_data: List[Dict[str, Any]], 
                            days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Predict ranking trend over time"""
        if not self.trained_models:
            return []
        
        predictions = []
        current_date = datetime.now()
        
        for day in range(days_ahead):
            future_date = current_date + timedelta(days=day)
            
            # Create feature vector for future date
            future_features = self._create_future_features(keyword, historical_data, future_date)
            
            # Predict ranking
            prediction = self.predict_ranking(future_features)
            
            if 'error' not in prediction:
                predictions.append({
                    'date': future_date.isoformat(),
                    'predicted_rank': prediction['predicted_rank'],
                    'confidence': prediction['confidence']
                })
        
        return predictions
    
    def _create_future_features(self, keyword: str, historical_data: List[Dict[str, Any]], 
                               future_date: datetime) -> Dict[str, Any]:
        """Create feature vector for future prediction"""
        # Use average of historical data as base
        if not historical_data:
            return {}
        
        # Calculate averages from historical data
        avg_features = {}
        numeric_fields = ['search_volume', 'competition', 'domain_authority', 'page_authority']
        
        for field in numeric_fields:
            values = [entry.get(field, 0) for entry in historical_data if entry.get(field) is not None]
            avg_features[field] = np.mean(values) if values else 0
        
        # Add time-based features
        avg_features['date'] = future_date.isoformat()
        
        # Add keyword-specific features
        avg_features['keyword'] = keyword
        
        return avg_features
    
    def get_feature_importance(self, model_type: str = 'random_forest') -> List[Dict[str, Any]]:
        """Get feature importance for trained model"""
        if model_type not in self.feature_importance:
            return []
        
        importance_scores = self.feature_importance[model_type]
        feature_names = self._get_feature_names()
        
        importance_list = []
        for i, score in enumerate(importance_scores):
            feature_name = feature_names[i] if i < len(feature_names) else f'feature_{i}'
            importance_list.append({
                'feature': feature_name,
                'importance': float(score)
            })
        
        # Sort by importance
        importance_list.sort(key=lambda x: x['importance'], reverse=True)
        return importance_list
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names"""
        return [
            'search_volume', 'competition', 'domain_authority', 'page_authority',
            'backlinks', 'content_length', 'keyword_density', 'title_length',
            'meta_description_length', 'internal_links', 'external_links',
            'page_speed', 'mobile_friendly', 'ssl_secure', 'social_signals',
            'time_on_page', 'bounce_rate', 'click_through_rate',
            'weekday', 'month', 'day', 'hour'
        ]
    
    def evaluate_model_performance(self, test_data: List[Dict[str, Any]], 
                                 model_type: str = 'random_forest') -> Dict[str, Any]:
        """Evaluate model performance on test data"""
        if model_type not in self.trained_models:
            return {'error': f'Model {model_type} not trained'}
        
        # Prepare test features
        X_test, y_true = self.prepare_features(test_data)
        
        if len(X_test) == 0:
            return {'error': 'No valid test data'}
        
        # Scale features
        X_test_scaled = self.scaler.transform(X_test)
        
        # Make predictions
        model = self.trained_models[model_type]
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        mse = np.mean((y_true - y_pred) ** 2)
        mae = np.mean(np.abs(y_true - y_pred))
        rmse = np.sqrt(mse)
        
        # Calculate ranking accuracy
        ranking_accuracy = self._calculate_ranking_accuracy(y_true, y_pred)
        
        return {
            'model_type': model_type,
            'mse': float(mse),
            'mae': float(mae),
            'rmse': float(rmse),
            'ranking_accuracy': ranking_accuracy,
            'test_samples': len(y_true)
        }
    
    def _calculate_ranking_accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate ranking accuracy"""
        # Consider prediction accurate if within 5 positions
        accurate_predictions = sum(1 for true, pred in zip(y_true, y_pred) 
                                 if abs(true - pred) <= 5)
        return accurate_predictions / len(y_true) if len(y_true) > 0 else 0.0
    
    def get_ranking_insights(self, keyword: str, current_rank: int, 
                           target_rank: int) -> Dict[str, Any]:
        """Get insights for improving ranking"""
        insights = {
            'current_rank': current_rank,
            'target_rank': target_rank,
            'rank_gap': current_rank - target_rank,
            'improvement_needed': current_rank > target_rank,
            'recommendations': []
        }
        
        if current_rank > target_rank:
            # Generate improvement recommendations
            insights['recommendations'] = self._generate_improvement_recommendations(
                keyword, current_rank, target_rank
            )
        
        return insights
    
    def _generate_improvement_recommendations(self, keyword: str, current_rank: int, 
                                           target_rank: int) -> List[str]:
        """Generate recommendations for improving ranking"""
        recommendations = []
        
        rank_gap = current_rank - target_rank
        
        if rank_gap > 10:
            recommendations.append("Focus on fundamental SEO improvements")
            recommendations.append("Improve content quality and relevance")
        elif rank_gap > 5:
            recommendations.append("Optimize on-page SEO elements")
            recommendations.append("Build quality backlinks")
        else:
            recommendations.append("Fine-tune existing optimizations")
            recommendations.append("Monitor competitor movements")
        
        recommendations.append("Track ranking progress regularly")
        recommendations.append("Analyze user behavior metrics")
        
        return recommendations
    
    def predict_competitor_impact(self, keyword: str, competitor_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict impact of competitor actions on ranking"""
        impact_analysis = {
            'keyword': keyword,
            'total_impact': 0,
            'action_impacts': []
        }
        
        for action in competitor_actions:
            action_type = action.get('type', '')
            impact_score = self._calculate_action_impact(action_type, action)
            
            impact_analysis['action_impacts'].append({
                'action_type': action_type,
                'impact_score': impact_score,
                'description': action.get('description', '')
            })
            
            impact_analysis['total_impact'] += impact_score
        
        return impact_analysis
    
    def _calculate_action_impact(self, action_type: str, action: Dict[str, Any]) -> float:
        """Calculate impact score for a competitor action"""
        impact_scores = {
            'content_update': 0.3,
            'backlink_building': 0.4,
            'technical_improvement': 0.2,
            'social_media': 0.1,
            'paid_advertising': 0.0  # No direct SEO impact
        }
        
        base_impact = impact_scores.get(action_type, 0.1)
        
        # Adjust based on action magnitude
        magnitude = action.get('magnitude', 1.0)
        return base_impact * magnitude

# Example usage
ranking_predictor = RankingPredictor()

# Sample training data
sample_data = [
    {
        'keyword': 'python programming',
        'rank': 5,
        'search_volume': 10000,
        'competition': 0.7,
        'domain_authority': 80,
        'page_authority': 75,
        'backlinks': 150,
        'content_length': 2000,
        'date': '2024-01-01'
    },
    # ... more data points
]

# Train model
training_result = ranking_predictor.train_model(sample_data, 'random_forest') 