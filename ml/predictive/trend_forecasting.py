# Trend Forecasting using Machine Learning
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class TrendForecaster:
    def __init__(self):
        self.models = {
            'trend_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
            'seasonal_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
            'cyclical_predictor': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        self.scaler = StandardScaler()
        self.trained_models = {}
        self.trend_patterns = {}
        self.seasonal_components = {}
        
    def analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in data and identify patterns"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        
        if 'date' not in df.columns:
            return {}
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Analyze different types of trends
        trend_analysis = {
            'overall_trend': self._analyze_overall_trend(df),
            'seasonal_trends': self._analyze_seasonal_trends(df),
            'cyclical_trends': self._analyze_cyclical_trends(df),
            'trend_breakpoints': self._detect_trend_breakpoints(df),
            'trend_strength': self._calculate_trend_strength(df)
        }
        
        return trend_analysis
    
    def _analyze_overall_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze overall trend in the data"""
        if len(df) < 2:
            return {}
        
        # Get the main metric column (assume first numeric column after date)
        metric_cols = df.select_dtypes(include=[np.number]).columns
        if len(metric_cols) == 0:
            return {}
        
        metric_col = metric_cols[0]
        y = df[metric_col].values
        x = np.arange(len(y))
        
        # Fit linear trend
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate trend statistics
        trend_line = slope * x + intercept
        residuals = y - trend_line
        r_squared = 1 - (np.sum(residuals**2) / np.sum((y - np.mean(y))**2))
        
        # Determine trend direction
        if slope > 0.01 * np.mean(y):
            direction = 'increasing'
        elif slope < -0.01 * np.mean(y):
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'trend_strength': abs(slope) / np.mean(y) if np.mean(y) > 0 else 0,
            'data_points': len(y)
        }
    
    def _analyze_seasonal_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal patterns in the data"""
        if len(df) < 30:  # Need at least a month of data
            return {}
        
        metric_cols = df.select_dtypes(include=[np.number]).columns
        if len(metric_cols) == 0:
            return {}
        
        metric_col = metric_cols[0]
        
        # Add time components
        df['month'] = df['date'].dt.month
        df['weekday'] = df['date'].dt.weekday
        df['quarter'] = df['date'].dt.quarter
        
        # Analyze monthly patterns
        monthly_patterns = df.groupby('month')[metric_col].agg(['mean', 'std']).to_dict()
        
        # Analyze weekly patterns
        weekly_patterns = df.groupby('weekday')[metric_col].agg(['mean', 'std']).to_dict()
        
        # Analyze quarterly patterns
        quarterly_patterns = df.groupby('quarter')[metric_col].agg(['mean', 'std']).to_dict()
        
        # Identify peak and low seasons
        monthly_means = {k: v['mean'] for k, v in monthly_patterns.items()}
        peak_month = max(monthly_means.items(), key=lambda x: x[1])[0]
        low_month = min(monthly_means.items(), key=lambda x: x[1])[0]
        
        return {
            'monthly_patterns': monthly_patterns,
            'weekly_patterns': weekly_patterns,
            'quarterly_patterns': quarterly_patterns,
            'peak_month': peak_month,
            'low_month': low_month,
            'seasonality_strength': self._calculate_seasonality_strength(df, metric_col)
        }
    
    def _analyze_cyclical_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cyclical patterns in the data"""
        if len(df) < 50:  # Need sufficient data for cyclical analysis
            return {}
        
        metric_cols = df.select_dtypes(include=[np.number]).columns
        if len(metric_cols) == 0:
            return {}
        
        metric_col = metric_cols[0]
        y = df[metric_col].values
        
        # Detect cycles using autocorrelation
        autocorr = self._calculate_autocorrelation(y)
        
        # Find dominant cycles
        dominant_cycles = self._find_dominant_cycles(autocorr)
        
        # Calculate cyclical strength
        cyclical_strength = self._calculate_cyclical_strength(y)
        
        return {
            'autocorrelation': autocorr[:20].tolist(),  # First 20 lags
            'dominant_cycles': dominant_cycles,
            'cyclical_strength': cyclical_strength,
            'has_cycles': len(dominant_cycles) > 0
        }
    
    def _calculate_autocorrelation(self, y: np.ndarray, max_lag: int = 20) -> np.ndarray:
        """Calculate autocorrelation for time series"""
        n = len(y)
        autocorr = np.zeros(max_lag)
        
        for lag in range(1, max_lag + 1):
            if lag < n:
                # Calculate autocorrelation for this lag
                numerator = np.sum((y[lag:] - np.mean(y)) * (y[:-lag] - np.mean(y)))
                denominator = np.sum((y - np.mean(y)) ** 2)
                
                if denominator > 0:
                    autocorr[lag - 1] = numerator / denominator
        
        return autocorr
    
    def _find_dominant_cycles(self, autocorr: np.ndarray) -> List[int]:
        """Find dominant cycles from autocorrelation"""
        dominant_cycles = []
        
        # Find peaks in autocorrelation
        for i in range(1, len(autocorr) - 1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.3:
                dominant_cycles.append(i + 1)
        
        return dominant_cycles
    
    def _calculate_cyclical_strength(self, y: np.ndarray) -> float:
        """Calculate strength of cyclical patterns"""
        # Simplified cyclical strength calculation
        # In practice, you'd use more sophisticated methods like FFT
        
        # Calculate variance explained by linear trend
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        trend_line = slope * x + intercept
        trend_variance = np.var(trend_line)
        total_variance = np.var(y)
        
        if total_variance > 0:
            cyclical_strength = 1 - (trend_variance / total_variance)
        else:
            cyclical_strength = 0
        
        return max(0, min(1, cyclical_strength))
    
    def _detect_trend_breakpoints(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect breakpoints in trends"""
        if len(df) < 10:
            return []
        
        metric_cols = df.select_dtypes(include=[np.number]).columns
        if len(metric_cols) == 0:
            return []
        
        metric_col = metric_cols[0]
        y = df[metric_col].values
        
        breakpoints = []
        
        # Simple breakpoint detection using rolling statistics
        window_size = min(7, len(y) // 4)
        
        for i in range(window_size, len(y) - window_size):
            before_mean = np.mean(y[i-window_size:i])
            after_mean = np.mean(y[i:i+window_size])
            
            # Check for significant change
            change_ratio = abs(after_mean - before_mean) / before_mean if before_mean > 0 else 0
            
            if change_ratio > 0.2:  # 20% change threshold
                breakpoints.append({
                    'index': i,
                    'date': df['date'].iloc[i].isoformat(),
                    'change_ratio': change_ratio,
                    'before_value': before_mean,
                    'after_value': after_mean
                })
        
        return breakpoints
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate overall trend strength"""
        metric_cols = df.select_dtypes(include=[np.number]).columns
        if len(metric_cols) == 0:
            return 0.0
        
        metric_col = metric_cols[0]
        y = df[metric_col].values
        
        if len(y) < 2:
            return 0.0
        
        # Calculate trend strength using linear regression
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        
        # Normalize slope by mean value
        if np.mean(y) > 0:
            normalized_slope = abs(slope) / np.mean(y)
        else:
            normalized_slope = 0
        
        return min(1.0, normalized_slope)
    
    def _calculate_seasonality_strength(self, df: pd.DataFrame, metric_col: str) -> float:
        """Calculate strength of seasonality"""
        # Calculate variance explained by seasonal patterns
        df['month'] = df['date'].dt.month
        
        # Calculate seasonal means
        seasonal_means = df.groupby('month')[metric_col].mean()
        overall_mean = df[metric_col].mean()
        
        if overall_mean > 0:
            seasonal_variance = np.var(seasonal_means)
            total_variance = np.var(df[metric_col])
            
            if total_variance > 0:
                seasonality_strength = seasonal_variance / total_variance
            else:
                seasonality_strength = 0
        else:
            seasonality_strength = 0
        
        return min(1.0, seasonality_strength)
    
    def forecast_trends(self, data: List[Dict[str, Any]], 
                      forecast_periods: int = 30) -> Dict[str, Any]:
        """Forecast trends for future periods"""
        if not data:
            return {}
        
        # Analyze current trends
        trend_analysis = self.analyze_trends(data)
        
        # Prepare forecasting data
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        metric_cols = df.select_dtypes(include=[np.number]).columns
        if len(metric_cols) == 0:
            return {}
        
        metric_col = metric_cols[0]
        
        # Generate forecasts
        forecasts = {
            'trend_forecast': self._forecast_trend_component(df, metric_col, forecast_periods),
            'seasonal_forecast': self._forecast_seasonal_component(df, metric_col, forecast_periods),
            'combined_forecast': self._forecast_combined(df, metric_col, forecast_periods),
            'confidence_intervals': self._calculate_confidence_intervals(df, metric_col, forecast_periods)
        }
        
        return {
            'trend_analysis': trend_analysis,
            'forecasts': forecasts,
            'forecast_periods': forecast_periods
        }
    
    def _forecast_trend_component(self, df: pd.DataFrame, metric_col: str, 
                                forecast_periods: int) -> List[Dict[str, Any]]:
        """Forecast trend component"""
        y = df[metric_col].values
        x = np.arange(len(y))
        
        # Fit trend model
        slope, intercept = np.polyfit(x, y, 1)
        
        forecasts = []
        current_date = df['date'].iloc[-1]
        
        for i in range(forecast_periods):
            future_x = len(y) + i
            trend_value = slope * future_x + intercept
            
            forecast_date = current_date + timedelta(days=i+1)
            
            forecasts.append({
                'date': forecast_date.isoformat(),
                'trend_value': max(0, trend_value),
                'component': 'trend'
            })
        
        return forecasts
    
    def _forecast_seasonal_component(self, df: pd.DataFrame, metric_col: str,
                                   forecast_periods: int) -> List[Dict[str, Any]]:
        """Forecast seasonal component"""
        # Calculate seasonal patterns
        df['month'] = df['date'].dt.month
        monthly_patterns = df.groupby('month')[metric_col].mean()
        
        forecasts = []
        current_date = df['date'].iloc[-1]
        
        for i in range(forecast_periods):
            forecast_date = current_date + timedelta(days=i+1)
            month = forecast_date.month
            
            seasonal_value = monthly_patterns.get(month, df[metric_col].mean())
            
            forecasts.append({
                'date': forecast_date.isoformat(),
                'seasonal_value': seasonal_value,
                'component': 'seasonal'
            })
        
        return forecasts
    
    def _forecast_combined(self, df: pd.DataFrame, metric_col: str,
                          forecast_periods: int) -> List[Dict[str, Any]]:
        """Forecast combined trend and seasonal components"""
        trend_forecast = self._forecast_trend_component(df, metric_col, forecast_periods)
        seasonal_forecast = self._forecast_seasonal_component(df, metric_col, forecast_periods)
        
        combined_forecasts = []
        
        for i in range(forecast_periods):
            trend_val = trend_forecast[i]['trend_value']
            seasonal_val = seasonal_forecast[i]['seasonal_value']
            
            # Combine trend and seasonal components
            combined_value = trend_val * 0.7 + seasonal_val * 0.3
            
            combined_forecasts.append({
                'date': trend_forecast[i]['date'],
                'combined_value': max(0, combined_value),
                'trend_component': trend_val,
                'seasonal_component': seasonal_val,
                'component': 'combined'
            })
        
        return combined_forecasts
    
    def _calculate_confidence_intervals(self, df: pd.DataFrame, metric_col: str,
                                      forecast_periods: int) -> List[Dict[str, Any]]:
        """Calculate confidence intervals for forecasts"""
        y = df[metric_col].values
        
        # Calculate forecast uncertainty
        residuals = y - np.mean(y)
        forecast_std = np.std(residuals)
        
        confidence_intervals = []
        current_date = df['date'].iloc[-1]
        
        for i in range(forecast_periods):
            forecast_date = current_date + timedelta(days=i+1)
            
            # Uncertainty increases with forecast horizon
            uncertainty_factor = 1 + (i * 0.1)
            
            confidence_intervals.append({
                'date': forecast_date.isoformat(),
                'lower_bound': max(0, np.mean(y) - 2 * forecast_std * uncertainty_factor),
                'upper_bound': np.mean(y) + 2 * forecast_std * uncertainty_factor,
                'confidence_level': 0.95
            })
        
        return confidence_intervals
    
    def get_trend_insights(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """Get insights from trend analysis"""
        insights = []
        
        # Overall trend insights
        overall_trend = trend_analysis.get('overall_trend', {})
        if overall_trend:
            direction = overall_trend.get('direction', 'unknown')
            strength = overall_trend.get('trend_strength', 0)
            
            if direction == 'increasing':
                insights.append(f"Strong upward trend detected (strength: {strength:.2f})")
            elif direction == 'decreasing':
                insights.append(f"Downward trend detected (strength: {strength:.2f})")
            else:
                insights.append("Stable trend with minimal change")
        
        # Seasonal insights
        seasonal_trends = trend_analysis.get('seasonal_trends', {})
        if seasonal_trends:
            seasonality_strength = seasonal_trends.get('seasonality_strength', 0)
            if seasonality_strength > 0.3:
                insights.append(f"Strong seasonal patterns detected (strength: {seasonality_strength:.2f})")
            
            peak_month = seasonal_trends.get('peak_month')
            if peak_month:
                insights.append(f"Peak performance typically occurs in month {peak_month}")
        
        # Cyclical insights
        cyclical_trends = trend_analysis.get('cyclical_trends', {})
        if cyclical_trends:
            has_cycles = cyclical_trends.get('has_cycles', False)
            if has_cycles:
                dominant_cycles = cyclical_trends.get('dominant_cycles', [])
                insights.append(f"Cyclical patterns detected with cycles of {dominant_cycles} periods")
        
        # Breakpoint insights
        breakpoints = trend_analysis.get('trend_breakpoints', [])
        if breakpoints:
            insights.append(f"Detected {len(breakpoints)} significant trend changes")
        
        return insights

# Example usage
trend_forecaster = TrendForecaster()

# Sample trend data
sample_data = [
    {
        'date': '2024-01-01',
        'search_volume': 1000,
        'rank': 10
    },
    # ... more data points
]

# Analyze trends
trend_analysis = trend_forecaster.analyze_trends(sample_data)

# Forecast trends
forecast_result = trend_forecaster.forecast_trends(sample_data, forecast_periods=30) 