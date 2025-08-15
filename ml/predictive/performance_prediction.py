# Performance Prediction using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class PerformancePredictor:
    def __init__(self):
        self.models = {
            'ranking_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
            'traffic_predictor': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'conversion_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
            'engagement_predictor': LinearRegression()
        }
        self.scaler = StandardScaler()
        self.trained_models = {}
        self.performance_metrics = {}
        self.prediction_thresholds = {}
        
    def predict_performance(self, data: List[Dict[str, Any]], 
                          prediction_horizon: int = 30) -> Dict[str, Any]:
        """Predict overall performance metrics"""
        if not data:
            return {}
        
        # Prepare data
        df = self.prepare_performance_data(data)
        
        # Train models if not already trained
        if not self.trained_models:
            self._train_performance_models(df)
        
        # Generate predictions
        predictions = {
            'ranking_predictions': self._predict_rankings(df, prediction_horizon),
            'traffic_predictions': self._predict_traffic(df, prediction_horizon),
            'conversion_predictions': self._predict_conversions(df, prediction_horizon),
            'engagement_predictions': self._predict_engagement(df, prediction_horizon),
            'overall_performance_score': self._calculate_overall_performance(df, prediction_horizon)
        }
        
        # Generate insights
        insights = self._generate_performance_insights(predictions, df)
        
        return {
            'predictions': predictions,
            'insights': insights,
            'prediction_horizon': prediction_horizon,
            'model_confidence': self._calculate_model_confidence()
        }
    
    def prepare_performance_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare performance data for prediction"""
        df = pd.DataFrame(data)
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        
        # Add time-based features
        df = self._add_time_features(df)
        
        # Add performance indicators
        df = self._add_performance_indicators(df)
        
        # Add lag features
        df = self._add_lag_features(df)
        
        # Add rolling statistics
        df = self._add_rolling_features(df)
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        if 'date' not in df.columns:
            return df
        
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['weekday'] = df['date'].dt.weekday
        df['week'] = df['date'].dt.isocalendar().week
        df['quarter'] = df['date'].dt.quarter
        
        # Cyclical encoding
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['weekday_sin'] = np.sin(2 * np.pi * df['weekday'] / 7)
        df['weekday_cos'] = np.cos(2 * np.pi * df['weekday'] / 7)
        
        return df
    
    def _add_performance_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add performance indicators and ratios"""
        # SEO performance indicators
        if 'rank' in df.columns and 'search_volume' in df.columns:
            df['rank_traffic_ratio'] = df['search_volume'] / (df['rank'] + 1)
        
        if 'rank' in df.columns and 'clicks' in df.columns:
            df['click_through_rate'] = df['clicks'] / (df['search_volume'] + 1)
        
        # Engagement indicators
        if 'pageviews' in df.columns and 'visitors' in df.columns:
            df['pages_per_session'] = df['pageviews'] / (df['visitors'] + 1)
        
        if 'time_on_page' in df.columns:
            df['engagement_score'] = df['time_on_page'] * df.get('pages_per_session', 1)
        
        # Conversion indicators
        if 'conversions' in df.columns and 'visitors' in df.columns:
            df['conversion_rate'] = df['conversions'] / (df['visitors'] + 1)
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame, max_lags: int = 7) -> pd.DataFrame:
        """Add lag features for time series prediction"""
        performance_columns = ['rank', 'traffic', 'visitors', 'conversions', 'engagement_score']
        
        for col in performance_columns:
            if col in df.columns:
                for lag in range(1, max_lags + 1):
                    df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        return df
    
    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rolling window features"""
        performance_columns = ['rank', 'traffic', 'visitors', 'conversions', 'engagement_score']
        
        for col in performance_columns:
            if col in df.columns:
                # Rolling means
                df[f'{col}_rolling_mean_7'] = df[col].rolling(window=7, min_periods=1).mean()
                df[f'{col}_rolling_mean_30'] = df[col].rolling(window=30, min_periods=1).mean()
                
                # Rolling trends
                df[f'{col}_rolling_trend_7'] = df[col].rolling(window=7, min_periods=1).apply(
                    lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
                )
        
        return df
    
    def _train_performance_models(self, df: pd.DataFrame) -> None:
        """Train performance prediction models"""
        # Remove rows with NaN values
        df_clean = df.dropna()
        
        if len(df_clean) < 30:
            print("Insufficient data for training")
            return
        
        # Train ranking predictor
        if 'rank' in df_clean.columns:
            self._train_ranking_model(df_clean)
        
        # Train traffic predictor
        if 'traffic' in df_clean.columns:
            self._train_traffic_model(df_clean)
        
        # Train conversion predictor
        if 'conversions' in df_clean.columns:
            self._train_conversion_model(df_clean)
        
        # Train engagement predictor
        if 'engagement_score' in df_clean.columns:
            self._train_engagement_model(df_clean)
    
    def _train_ranking_model(self, df: pd.DataFrame) -> None:
        """Train ranking prediction model"""
        # Prepare features for ranking prediction
        feature_columns = [col for col in df.columns if col not in ['date', 'rank']]
        X = df[feature_columns].values
        y = df['rank'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        model = self.models['ranking_predictor']
        model.fit(X_train_scaled, y_train)
        
        # Store model
        self.trained_models['ranking_predictor'] = {
            'model': model,
            'feature_columns': feature_columns,
            'scaler': self.scaler,
            'train_score': model.score(X_train_scaled, y_train),
            'test_score': model.score(X_test_scaled, y_test)
        }
    
    def _train_traffic_model(self, df: pd.DataFrame) -> None:
        """Train traffic prediction model"""
        feature_columns = [col for col in df.columns if col not in ['date', 'traffic']]
        X = df[feature_columns].values
        y = df['traffic'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = self.models['traffic_predictor']
        model.fit(X_train_scaled, y_train)
        
        self.trained_models['traffic_predictor'] = {
            'model': model,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'train_score': model.score(X_train_scaled, y_train),
            'test_score': model.score(X_test_scaled, y_test)
        }
    
    def _train_conversion_model(self, df: pd.DataFrame) -> None:
        """Train conversion prediction model"""
        feature_columns = [col for col in df.columns if col not in ['date', 'conversions']]
        X = df[feature_columns].values
        y = df['conversions'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = self.models['conversion_predictor']
        model.fit(X_train_scaled, y_train)
        
        self.trained_models['conversion_predictor'] = {
            'model': model,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'train_score': model.score(X_train_scaled, y_train),
            'test_score': model.score(X_test_scaled, y_test)
        }
    
    def _train_engagement_model(self, df: pd.DataFrame) -> None:
        """Train engagement prediction model"""
        feature_columns = [col for col in df.columns if col not in ['date', 'engagement_score']]
        X = df[feature_columns].values
        y = df['engagement_score'].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = self.models['engagement_predictor']
        model.fit(X_train_scaled, y_train)
        
        self.trained_models['engagement_predictor'] = {
            'model': model,
            'feature_columns': feature_columns,
            'scaler': scaler,
            'train_score': model.score(X_train_scaled, y_train),
            'test_score': model.score(X_test_scaled, y_test)
        }
    
    def _predict_rankings(self, df: pd.DataFrame, horizon: int) -> List[Dict[str, Any]]:
        """Predict rankings for future periods"""
        if 'ranking_predictor' not in self.trained_models:
            return []
        
        model_info = self.trained_models['ranking_predictor']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        scaler = model_info['scaler']
        
        predictions = []
        current_date = df['date'].iloc[-1]
        
        # Get last known features
        last_features = self._get_last_features(df, feature_columns)
        
        for i in range(horizon):
            future_date = current_date + timedelta(days=i+1)
            
            # Create future feature vector
            future_features = self._create_future_features(
                future_date, last_features, feature_columns
            )
            
            if future_features is not None:
                # Scale features
                future_features_scaled = scaler.transform([future_features])
                
                # Make prediction
                predicted_rank = model.predict(future_features_scaled)[0]
                
                predictions.append({
                    'date': future_date.isoformat(),
                    'predicted_rank': max(1, int(predicted_rank)),
                    'confidence': self._calculate_prediction_confidence(i, model_info['test_score'])
                })
                
                # Update last features
                last_features = self._update_features_for_next_day(
                    last_features, predicted_rank, feature_columns, 'rank'
                )
        
        return predictions
    
    def _predict_traffic(self, df: pd.DataFrame, horizon: int) -> List[Dict[str, Any]]:
        """Predict traffic for future periods"""
        if 'traffic_predictor' not in self.trained_models:
            return []
        
        model_info = self.trained_models['traffic_predictor']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        scaler = model_info['scaler']
        
        predictions = []
        current_date = df['date'].iloc[-1]
        last_features = self._get_last_features(df, feature_columns)
        
        for i in range(horizon):
            future_date = current_date + timedelta(days=i+1)
            future_features = self._create_future_features(
                future_date, last_features, feature_columns
            )
            
            if future_features is not None:
                future_features_scaled = scaler.transform([future_features])
                predicted_traffic = model.predict(future_features_scaled)[0]
                
                predictions.append({
                    'date': future_date.isoformat(),
                    'predicted_traffic': max(0, int(predicted_traffic)),
                    'confidence': self._calculate_prediction_confidence(i, model_info['test_score'])
                })
                
                last_features = self._update_features_for_next_day(
                    last_features, predicted_traffic, feature_columns, 'traffic'
                )
        
        return predictions
    
    def _predict_conversions(self, df: pd.DataFrame, horizon: int) -> List[Dict[str, Any]]:
        """Predict conversions for future periods"""
        if 'conversion_predictor' not in self.trained_models:
            return []
        
        model_info = self.trained_models['conversion_predictor']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        scaler = model_info['scaler']
        
        predictions = []
        current_date = df['date'].iloc[-1]
        last_features = self._get_last_features(df, feature_columns)
        
        for i in range(horizon):
            future_date = current_date + timedelta(days=i+1)
            future_features = self._create_future_features(
                future_date, last_features, feature_columns
            )
            
            if future_features is not None:
                future_features_scaled = scaler.transform([future_features])
                predicted_conversions = model.predict(future_features_scaled)[0]
                
                predictions.append({
                    'date': future_date.isoformat(),
                    'predicted_conversions': max(0, int(predicted_conversions)),
                    'confidence': self._calculate_prediction_confidence(i, model_info['test_score'])
                })
                
                last_features = self._update_features_for_next_day(
                    last_features, predicted_conversions, feature_columns, 'conversions'
                )
        
        return predictions
    
    def _predict_engagement(self, df: pd.DataFrame, horizon: int) -> List[Dict[str, Any]]:
        """Predict engagement for future periods"""
        if 'engagement_predictor' not in self.trained_models:
            return []
        
        model_info = self.trained_models['engagement_predictor']
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        scaler = model_info['scaler']
        
        predictions = []
        current_date = df['date'].iloc[-1]
        last_features = self._get_last_features(df, feature_columns)
        
        for i in range(horizon):
            future_date = current_date + timedelta(days=i+1)
            future_features = self._create_future_features(
                future_date, last_features, feature_columns
            )
            
            if future_features is not None:
                future_features_scaled = scaler.transform([future_features])
                predicted_engagement = model.predict(future_features_scaled)[0]
                
                predictions.append({
                    'date': future_date.isoformat(),
                    'predicted_engagement': max(0, predicted_engagement),
                    'confidence': self._calculate_prediction_confidence(i, model_info['test_score'])
                })
                
                last_features = self._update_features_for_next_day(
                    last_features, predicted_engagement, feature_columns, 'engagement_score'
                )
        
        return predictions
    
    def _get_last_features(self, df: pd.DataFrame, feature_columns: List[str]) -> Dict[str, float]:
        """Get last known feature values"""
        last_row = df.iloc[-1]
        features = {}
        
        for col in feature_columns:
            if col in last_row:
                features[col] = last_row[col]
            else:
                features[col] = 0.0
        
        return features
    
    def _create_future_features(self, future_date: datetime, last_features: Dict[str, float],
                              feature_columns: List[str]) -> Optional[List[float]]:
        """Create feature vector for future date"""
        try:
            features = []
            
            for col in feature_columns:
                if 'year' in col:
                    features.append(future_date.year)
                elif 'month' in col and 'sin' not in col and 'cos' not in col:
                    features.append(future_date.month)
                elif 'day' in col and 'week' not in col:
                    features.append(future_date.day)
                elif 'weekday' in col and 'sin' not in col and 'cos' not in col:
                    features.append(future_date.weekday())
                elif 'week' in col:
                    features.append(future_date.isocalendar().week)
                elif 'quarter' in col:
                    features.append((future_date.month - 1) // 3 + 1)
                elif 'month_sin' in col:
                    features.append(np.sin(2 * np.pi * future_date.month / 12))
                elif 'month_cos' in col:
                    features.append(np.cos(2 * np.pi * future_date.month / 12))
                elif 'weekday_sin' in col:
                    features.append(np.sin(2 * np.pi * future_date.weekday() / 7))
                elif 'weekday_cos' in col:
                    features.append(np.cos(2 * np.pi * future_date.weekday() / 7))
                else:
                    features.append(last_features.get(col, 0.0))
            
            return features
            
        except Exception as e:
            print(f"Error creating future features: {e}")
            return None
    
    def _update_features_for_next_day(self, last_features: Dict[str, float], 
                                    prediction: float, feature_columns: List[str],
                                    target_col: str) -> Dict[str, float]:
        """Update features for next day's prediction"""
        updated_features = last_features.copy()
        
        # Update lag features
        for col in feature_columns:
            if f'{target_col}_lag_1' in col:
                # Shift lag features
                for lag in range(6, 0, -1):
                    old_lag = f'{target_col}_lag_{lag}'
                    new_lag = f'{target_col}_lag_{lag + 1}'
                    if old_lag in updated_features:
                        updated_features[new_lag] = updated_features[old_lag]
                
                # Set new lag_1 to current prediction
                updated_features[f'{target_col}_lag_1'] = prediction
        
        return updated_features
    
    def _calculate_prediction_confidence(self, days_ahead: int, model_score: float) -> float:
        """Calculate confidence in prediction"""
        # Base confidence from model performance
        base_confidence = model_score
        
        # Decay confidence with time
        decay_rate = 0.02  # 2% decay per day
        confidence = base_confidence * (1 - decay_rate * days_ahead)
        
        return max(0.1, min(1.0, confidence))
    
    def _calculate_overall_performance(self, df: pd.DataFrame, horizon: int) -> float:
        """Calculate overall performance score"""
        # This would combine all predictions into a single performance score
        # For now, return a simplified calculation
        
        if 'rank' in df.columns:
            current_rank = df['rank'].iloc[-1]
            # Better rank = higher performance
            rank_score = max(0, (100 - current_rank) / 100)
        else:
            rank_score = 0.5
        
        if 'traffic' in df.columns:
            current_traffic = df['traffic'].iloc[-1]
            # Normalize traffic score
            traffic_score = min(1.0, current_traffic / 10000)
        else:
            traffic_score = 0.5
        
        # Combine scores
        overall_score = (rank_score * 0.6 + traffic_score * 0.4)
        
        return overall_score
    
    def _generate_performance_insights(self, predictions: Dict[str, Any], df: pd.DataFrame) -> List[str]:
        """Generate insights from performance predictions"""
        insights = []
        
        # Ranking insights
        ranking_preds = predictions.get('ranking_predictions', [])
        if ranking_preds:
            current_rank = df['rank'].iloc[-1] if 'rank' in df.columns else 50
            predicted_rank = ranking_preds[-1]['predicted_rank']
            
            if predicted_rank < current_rank:
                insights.append(f"Expected ranking improvement from {current_rank} to {predicted_rank}")
            elif predicted_rank > current_rank:
                insights.append(f"Potential ranking decline from {current_rank} to {predicted_rank}")
        
        # Traffic insights
        traffic_preds = predictions.get('traffic_predictions', [])
        if traffic_preds:
            current_traffic = df['traffic'].iloc[-1] if 'traffic' in df.columns else 0
            predicted_traffic = traffic_preds[-1]['predicted_traffic']
            
            if predicted_traffic > current_traffic * 1.1:
                insights.append(f"Expected traffic growth of {((predicted_traffic/current_traffic)-1)*100:.1f}%")
            elif predicted_traffic < current_traffic * 0.9:
                insights.append(f"Potential traffic decline of {((current_traffic/predicted_traffic)-1)*100:.1f}%")
        
        # Overall performance insights
        overall_score = predictions.get('overall_performance_score', 0)
        if overall_score > 0.7:
            insights.append("Strong overall performance expected")
        elif overall_score < 0.3:
            insights.append("Performance improvement needed")
        
        return insights
    
    def _calculate_model_confidence(self) -> Dict[str, float]:
        """Calculate confidence for each model"""
        confidence = {}
        
        for model_name, model_info in self.trained_models.items():
            confidence[model_name] = model_info.get('test_score', 0.0)
        
        return confidence

# Example usage
performance_predictor = PerformancePredictor()

# Sample performance data
sample_data = [
    {
        'date': '2024-01-01',
        'rank': 10,
        'traffic': 1000,
        'visitors': 800,
        'conversions': 50,
        'engagement_score': 75
    },
    # ... more data points
]

# Predict performance
prediction_result = performance_predictor.predict_performance(sample_data, prediction_horizon=30) 