# Trend Prediction
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

class TrendPrediction:
    def __init__(self):
        self.historical_data = {}
        self.trend_models = {}
        self.seasonal_patterns = {}
        
    def add_historical_data(self, keyword: str, data: List[Dict[str, Any]]) -> None:
        """Add historical data for a keyword"""
        self.historical_data[keyword] = data
        
    def predict_trend(self, keyword: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict trend for a keyword"""
        if keyword not in self.historical_data:
            return {}
        
        data = self.historical_data[keyword]
        if len(data) < 7:  # Need at least a week of data
            return {}
        
        # Prepare features for prediction
        X, y = self._prepare_features(data)
        
        if len(X) == 0:
            return {}
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Make predictions
        future_features = self._generate_future_features(len(data), days_ahead)
        predictions = model.predict(future_features)
        
        # Calculate trend direction
        trend_direction = self._calculate_trend_direction(predictions)
        
        return {
            'keyword': keyword,
            'predictions': predictions.tolist(),
            'trend_direction': trend_direction,
            'confidence_score': self._calculate_confidence(model, X, y),
            'seasonal_factors': self._analyze_seasonality(data),
            'growth_rate': self._calculate_growth_rate(predictions)
        }
    
    def _prepare_features(self, data: List[Dict[str, Any]]) -> tuple:
        """Prepare features for trend prediction"""
        X = []
        y = []
        
        for i in range(len(data) - 1):
            features = [
                data[i].get('search_volume', 0),
                data[i].get('rank', 0),
                data[i].get('competition', 0),
                i,  # Time index
                data[i].get('day_of_week', 0),
                data[i].get('month', 0)
            ]
            X.append(features)
            y.append(data[i + 1].get('search_volume', 0))
        
        return np.array(X), np.array(y)
    
    def _generate_future_features(self, current_length: int, days_ahead: int) -> np.ndarray:
        """Generate features for future predictions"""
        features = []
        
        for i in range(days_ahead):
            future_date = datetime.now() + timedelta(days=i)
            feature = [
                0,  # Placeholder for search_volume
                0,  # Placeholder for rank
                0,  # Placeholder for competition
                current_length + i,  # Time index
                future_date.weekday(),  # Day of week
                future_date.month  # Month
            ]
            features.append(feature)
        
        return np.array(features)
    
    def _calculate_trend_direction(self, predictions: np.ndarray) -> str:
        """Calculate trend direction based on predictions"""
        if len(predictions) < 2:
            return "stable"
        
        # Calculate slope
        x = np.arange(len(predictions))
        slope = np.polyfit(x, predictions, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_confidence(self, model, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate confidence score for predictions"""
        # Simple R-squared based confidence
        y_pred = model.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        return max(0.0, min(1.0, r_squared))
    
    def _analyze_seasonality(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal patterns in the data"""
        if len(data) < 30:  # Need at least a month of data
            return {}
        
        # Group by day of week
        daily_patterns = {}
        for entry in data:
            day = entry.get('day_of_week', 0)
            volume = entry.get('search_volume', 0)
            
            if day not in daily_patterns:
                daily_patterns[day] = []
            daily_patterns[day].append(volume)
        
        # Calculate average volume by day
        daily_averages = {
            day: np.mean(volumes) for day, volumes in daily_patterns.items()
        }
        
        return {
            'daily_patterns': daily_averages,
            'peak_day': max(daily_averages, key=daily_averages.get),
            'low_day': min(daily_averages, key=daily_averages.get)
        }
    
    def _calculate_growth_rate(self, predictions: np.ndarray) -> float:
        """Calculate growth rate from predictions"""
        if len(predictions) < 2:
            return 0.0
        
        initial_value = predictions[0]
        final_value = predictions[-1]
        
        if initial_value == 0:
            return 0.0
        
        growth_rate = ((final_value - initial_value) / initial_value) * 100
        return growth_rate
    
    def predict_market_trends(self, keywords: List[str]) -> Dict[str, Any]:
        """Predict overall market trends"""
        market_predictions = []
        
        for keyword in keywords:
            prediction = self.predict_trend(keyword, days_ahead=30)
            if prediction:
                market_predictions.append(prediction)
        
        if not market_predictions:
            return {}
        
        # Aggregate market insights
        trend_directions = [p['trend_direction'] for p in market_predictions]
        confidence_scores = [p['confidence_score'] for p in market_predictions]
        growth_rates = [p['growth_rate'] for p in market_predictions]
        
        return {
            'overall_trend': self._aggregate_trend_direction(trend_directions),
            'average_confidence': np.mean(confidence_scores),
            'average_growth_rate': np.mean(growth_rates),
            'trending_keywords': [p['keyword'] for p in market_predictions if p['trend_direction'] == 'increasing'],
            'declining_keywords': [p['keyword'] for p in market_predictions if p['trend_direction'] == 'decreasing']
        }
    
    def _aggregate_trend_direction(self, directions: List[str]) -> str:
        """Aggregate multiple trend directions"""
        increasing_count = directions.count('increasing')
        decreasing_count = directions.count('decreasing')
        stable_count = directions.count('stable')
        
        total = len(directions)
        
        if increasing_count / total > 0.5:
            return 'increasing'
        elif decreasing_count / total > 0.5:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_seasonal_recommendations(self, keyword: str) -> Dict[str, Any]:
        """Get seasonal recommendations for a keyword"""
        if keyword not in self.historical_data:
            return {}
        
        data = self.historical_data[keyword]
        seasonality = self._analyze_seasonality(data)
        
        if not seasonality:
            return {}
        
        recommendations = {
            'best_days_to_publish': [seasonality['peak_day']],
            'worst_days_to_publish': [seasonality['low_day']],
            'seasonal_timing': self._get_seasonal_timing(data),
            'content_strategy': self._get_content_strategy(seasonality)
        }
        
        return recommendations
    
    def _get_seasonal_timing(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get seasonal timing recommendations"""
        # Analyze monthly patterns
        monthly_patterns = {}
        for entry in data:
            month = entry.get('month', 0)
            volume = entry.get('search_volume', 0)
            
            if month not in monthly_patterns:
                monthly_patterns[month] = []
            monthly_patterns[month].append(volume)
        
        monthly_averages = {
            month: np.mean(volumes) for month, volumes in monthly_patterns.items()
        }
        
        return {
            'peak_months': [m for m, v in monthly_averages.items() if v > np.mean(list(monthly_averages.values()))],
            'low_months': [m for m, v in monthly_averages.items() if v < np.mean(list(monthly_averages.values()))]
        }
    
    def _get_content_strategy(self, seasonality: Dict[str, Any]) -> List[str]:
        """Get content strategy recommendations based on seasonality"""
        strategies = []
        
        if seasonality.get('peak_day') is not None:
            strategies.append(f"Publish content on day {seasonality['peak_day']} for maximum visibility")
        
        if seasonality.get('low_day') is not None:
            strategies.append(f"Avoid publishing on day {seasonality['low_day']} due to low engagement")
        
        strategies.append("Monitor seasonal patterns and adjust content calendar accordingly")
        
        return strategies

# Example usage
trend_prediction = TrendPrediction()

# Add sample historical data
sample_data = [
    {'date': '2024-01-01', 'search_volume': 1000, 'rank': 5, 'competition': 0.3, 'day_of_week': 0, 'month': 1},
    {'date': '2024-01-02', 'search_volume': 1100, 'rank': 4, 'competition': 0.3, 'day_of_week': 1, 'month': 1},
    # ... more data points
]

trend_prediction.add_historical_data("python programming", sample_data) 