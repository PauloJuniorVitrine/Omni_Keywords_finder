# Traffic Forecasting using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class TrafficForecaster:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        self.scaler = StandardScaler()
        self.trained_models = {}
        self.seasonal_patterns = {}
        self.trend_components = {}
        
    def prepare_traffic_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare traffic data for forecasting"""
        df = pd.DataFrame(data)
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        
        # Add time-based features
        df = self._add_time_features(df)
        
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
        
        # Cyclical encoding for periodic features
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['weekday_sin'] = np.sin(2 * np.pi * df['weekday'] / 7)
        df['weekday_cos'] = np.cos(2 * np.pi * df['weekday'] / 7)
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame, max_lags: int = 7) -> pd.DataFrame:
        """Add lag features for time series forecasting"""
        traffic_columns = ['traffic', 'visitors', 'pageviews', 'sessions']
        
        for col in traffic_columns:
            if col in df.columns:
                for lag in range(1, max_lags + 1):
                    df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        return df
    
    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rolling window features"""
        traffic_columns = ['traffic', 'visitors', 'pageviews', 'sessions']
        
        for col in traffic_columns:
            if col in df.columns:
                # Rolling means
                df[f'{col}_rolling_mean_7'] = df[col].rolling(window=7, min_periods=1).mean()
                df[f'{col}_rolling_mean_30'] = df[col].rolling(window=30, min_periods=1).mean()
                
                # Rolling standard deviations
                df[f'{col}_rolling_std_7'] = df[col].rolling(window=7, min_periods=1).std()
                
                # Rolling trends
                df[f'{col}_rolling_trend_7'] = df[col].rolling(window=7, min_periods=1).apply(
                    lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
                )
        
        return df
    
    def train_forecasting_model(self, data: List[Dict[str, Any]], 
                              target_column: str = 'traffic',
                              model_type: str = 'random_forest') -> Dict[str, Any]:
        """Train traffic forecasting model"""
        if model_type not in self.models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Prepare data
        df = self.prepare_traffic_data(data)
        
        # Remove rows with NaN values
        df = df.dropna()
        
        if len(df) < 30:  # Need at least 30 days of data
            return {'error': 'Insufficient data for training'}
        
        # Prepare features and target
        feature_columns = [col for col in df.columns if col not in ['date', target_column]]
        X = df[feature_columns].values
        y = df[target_column].values
        
        # Split data (time series split)
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        model = self.models[model_type]
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        # Calculate predictions
        y_train_pred = model.predict(X_train_scaled)
        y_test_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        train_rmse = np.sqrt(np.mean((y_train - y_train_pred) ** 2))
        test_rmse = np.sqrt(np.mean((y_test - y_test_pred) ** 2))
        
        # Store trained model
        self.trained_models[model_type] = {
            'model': model,
            'feature_columns': feature_columns,
            'target_column': target_column
        }
        
        return {
            'model_type': model_type,
            'train_score': train_score,
            'test_score': test_score,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'feature_count': len(feature_columns),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
    
    def forecast_traffic(self, days_ahead: int = 30, 
                       model_type: str = 'random_forest') -> List[Dict[str, Any]]:
        """Forecast traffic for future days"""
        if model_type not in self.trained_models:
            return []
        
        model_info = self.trained_models[model_type]
        model = model_info['model']
        feature_columns = model_info['feature_columns']
        target_column = model_info['target_column']
        
        forecasts = []
        current_date = datetime.now()
        
        # Get last known data for initial features
        last_features = self._get_last_known_features(feature_columns)
        
        for day in range(days_ahead):
            future_date = current_date + timedelta(days=day)
            
            # Create feature vector for future date
            future_features = self._create_future_features(
                future_date, last_features, feature_columns, target_column
            )
            
            if future_features is not None:
                # Scale features
                future_features_scaled = self.scaler.transform([future_features])
                
                # Make prediction
                prediction = model.predict(future_features_scaled)[0]
                
                # Calculate confidence interval (simplified)
                confidence = self._calculate_forecast_confidence(day, prediction)
                
                forecasts.append({
                    'date': future_date.isoformat(),
                    'predicted_traffic': max(0, int(prediction)),
                    'confidence': confidence,
                    'model_type': model_type
                })
                
                # Update last features for next iteration
                last_features = self._update_features_for_next_day(
                    last_features, prediction, feature_columns, target_column
                )
        
        return forecasts
    
    def _get_last_known_features(self, feature_columns: List[str]) -> Dict[str, float]:
        """Get last known feature values"""
        # This would typically come from the most recent data
        # For now, return default values
        default_features = {}
        for col in feature_columns:
            if 'lag' in col:
                default_features[col] = 1000  # Default traffic value
            elif 'rolling' in col:
                default_features[col] = 1000
            elif 'sin' in col or 'cos' in col:
                default_features[col] = 0.0
            else:
                default_features[col] = 0.0
        
        return default_features
    
    def _create_future_features(self, future_date: datetime, last_features: Dict[str, float],
                              feature_columns: List[str], target_column: str) -> Optional[List[float]]:
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
                    # Use last known value for other features
                    features.append(last_features.get(col, 0.0))
            
            return features
            
        except Exception as e:
            print(f"Error creating future features: {e}")
            return None
    
    def _update_features_for_next_day(self, last_features: Dict[str, float], 
                                    prediction: float, feature_columns: List[str],
                                    target_column: str) -> Dict[str, float]:
        """Update features for next day's forecast"""
        updated_features = last_features.copy()
        
        # Update lag features
        for col in feature_columns:
            if 'lag_1' in col:
                # Shift lag features
                for lag in range(6, 0, -1):
                    old_lag = f'{target_column}_lag_{lag}'
                    new_lag = f'{target_column}_lag_{lag + 1}'
                    if old_lag in updated_features:
                        updated_features[new_lag] = updated_features[old_lag]
                
                # Set new lag_1 to current prediction
                updated_features[f'{target_column}_lag_1'] = prediction
        
        return updated_features
    
    def _calculate_forecast_confidence(self, days_ahead: int, prediction: float) -> float:
        """Calculate confidence in forecast"""
        # Confidence decreases with time
        base_confidence = 0.9
        decay_rate = 0.02  # 2% decay per day
        
        confidence = base_confidence * (1 - decay_rate * days_ahead)
        return max(0.1, min(1.0, confidence))
    
    def analyze_seasonal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal patterns in traffic data"""
        df = pd.DataFrame(data)
        
        if 'date' not in df.columns or 'traffic' not in df.columns:
            return {}
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Monthly patterns
        monthly_patterns = df.groupby(df['date'].dt.month)['traffic'].agg(['mean', 'std']).to_dict()
        
        # Weekly patterns
        weekly_patterns = df.groupby(df['date'].dt.weekday)['traffic'].agg(['mean', 'std']).to_dict()
        
        # Quarterly patterns
        quarterly_patterns = df.groupby(df['date'].dt.quarter)['traffic'].agg(['mean', 'std']).to_dict()
        
        # Identify peak and low periods
        peak_month = max(monthly_patterns['mean'].items(), key=lambda x: x[1])[0]
        low_month = min(monthly_patterns['mean'].items(), key=lambda x: x[1])[0]
        
        peak_weekday = max(weekly_patterns['mean'].items(), key=lambda x: x[1])[0]
        low_weekday = min(weekly_patterns['mean'].items(), key=lambda x: x[1])[0]
        
        return {
            'monthly_patterns': monthly_patterns,
            'weekly_patterns': weekly_patterns,
            'quarterly_patterns': quarterly_patterns,
            'peak_month': peak_month,
            'low_month': low_month,
            'peak_weekday': peak_weekday,
            'low_weekday': low_weekday,
            'seasonality_strength': self._calculate_seasonality_strength(df)
        }
    
    def _calculate_seasonality_strength(self, df: pd.DataFrame) -> float:
        """Calculate strength of seasonality"""
        # Simplified seasonality strength calculation
        monthly_means = df.groupby(df['date'].dt.month)['traffic'].mean()
        overall_mean = df['traffic'].mean()
        
        if overall_mean > 0:
            seasonality_strength = monthly_means.std() / overall_mean
        else:
            seasonality_strength = 0.0
        
        return min(1.0, seasonality_strength)
    
    def detect_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect trends in traffic data"""
        df = pd.DataFrame(data)
        
        if 'date' not in df.columns or 'traffic' not in df.columns:
            return {}
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate trend using linear regression
        x = np.arange(len(df))
        y = df['traffic'].values
        
        if len(x) > 1:
            slope, intercept = np.polyfit(x, y, 1)
            trend_direction = 'increasing' if slope > 0 else 'decreasing'
            trend_strength = abs(slope) / np.mean(y) if np.mean(y) > 0 else 0
        else:
            slope = 0
            trend_direction = 'stable'
            trend_strength = 0
        
        # Calculate growth rate
        if len(df) > 1:
            first_value = df['traffic'].iloc[0]
            last_value = df['traffic'].iloc[-1]
            if first_value > 0:
                growth_rate = ((last_value - first_value) / first_value) * 100
            else:
                growth_rate = 0
        else:
            growth_rate = 0
        
        return {
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'slope': slope,
            'growth_rate': growth_rate,
            'data_points': len(df)
        }
    
    def get_forecast_insights(self, forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get insights from traffic forecasts"""
        if not forecasts:
            return {}
        
        traffic_values = [f['predicted_traffic'] for f in forecasts]
        
        # Calculate forecast statistics
        avg_traffic = np.mean(traffic_values)
        max_traffic = max(traffic_values)
        min_traffic = min(traffic_values)
        
        # Identify peak and low days
        peak_day = max(forecasts, key=lambda x: x['predicted_traffic'])
        low_day = min(forecasts, key=lambda x: x['predicted_traffic'])
        
        # Calculate trend in forecast
        if len(traffic_values) > 1:
            forecast_trend = np.polyfit(range(len(traffic_values)), traffic_values, 1)[0]
            trend_direction = 'increasing' if forecast_trend > 0 else 'decreasing'
        else:
            forecast_trend = 0
            trend_direction = 'stable'
        
        return {
            'forecast_period': len(forecasts),
            'average_traffic': int(avg_traffic),
            'max_traffic': max_traffic,
            'min_traffic': min_traffic,
            'traffic_range': max_traffic - min_traffic,
            'peak_day': peak_day,
            'low_day': low_day,
            'forecast_trend': forecast_trend,
            'trend_direction': trend_direction,
            'confidence_range': {
                'min': min(f['confidence'] for f in forecasts),
                'max': max(f['confidence'] for f in forecasts),
                'average': np.mean([f['confidence'] for f in forecasts])
            }
        }

# Example usage
traffic_forecaster = TrafficForecaster()

# Sample traffic data
sample_data = [
    {
        'date': '2024-01-01',
        'traffic': 1000,
        'visitors': 800,
        'pageviews': 1500
    },
    # ... more data points
]

# Train model
training_result = traffic_forecaster.train_forecasting_model(sample_data)

# Generate forecast
forecasts = traffic_forecaster.forecast_traffic(days_ahead=30) 