"""
🔍 Predictive Monitoring System
📅 Generated: 2025-01-27
🎯 Purpose: Predictive monitoring with trend analysis and early warnings
📋 Tracing ID: PREDICTIVE_MONITORING_001_20250127
"""

import logging
import time
import numpy as np
import statistics
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
from collections import deque, defaultdict
import threading
from datetime import datetime, timedelta
import warnings

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of predictions"""
    TREND = "trend"
    SEASONAL = "seasonal"
    CYCLICAL = "cyclical"
    THRESHOLD_BREACH = "threshold_breach"
    ANOMALY = "anomaly"
    CAPACITY = "capacity"
    PERFORMANCE = "performance"
    RESOURCE = "resource"


class PredictionConfidence(Enum):
    """Prediction confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AlertLevel(Enum):
    """Alert levels for predictions"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PredictionConfig:
    """Configuration for predictive monitoring"""
    window_size: int = 100
    prediction_horizon: int = 24  # hours
    confidence_threshold: float = 0.7
    trend_sensitivity: float = 0.1
    seasonal_periods: List[int] = field(default_factory=lambda: [24, 168])  # hours
    enable_trend_analysis: bool = True
    enable_seasonal_analysis: bool = True
    enable_capacity_planning: bool = True
    enable_performance_prediction: bool = True
    alert_on_prediction: bool = True
    auto_adjust_thresholds: bool = True
    learning_rate: float = 0.1
    min_data_points: int = 50
    max_prediction_age: int = 3600  # seconds
    custom_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """Result of predictive analysis"""
    metric_name: str
    prediction_type: PredictionType
    predicted_value: float
    confidence: PredictionConfidence
    alert_level: AlertLevel
    prediction_time: float
    horizon_hours: int
    current_value: float
    trend_direction: str
    trend_strength: float
    seasonal_factor: float
    capacity_utilization: float
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    direction: str  # "increasing", "decreasing", "stable"
    strength: float  # 0.0 to 1.0
    slope: float
    r_squared: float
    p_value: float
    confidence_interval: Tuple[float, float]


@dataclass
class SeasonalAnalysis:
    """Seasonal analysis result"""
    seasonal_period: int
    seasonal_strength: float
    seasonal_pattern: List[float]
    seasonal_factor: float
    confidence: float


class PredictiveMonitor:
    """
    Advanced predictive monitoring system
    """
    
    def __init__(self, config: PredictionConfig):
        self.config = config
        self.data_buffer = defaultdict(lambda: deque(maxlen=config.window_size))
        self.predictions = defaultdict(list)
        self.trend_models = {}
        self.seasonal_models = {}
        self.capacity_models = {}
        self.lock = threading.RLock()
        self.alert_handlers = []
        
    def add_data_point(self, metric_name: str, value: float, timestamp: Optional[float] = None):
        """
        Add a new data point for analysis
        
        Args:
            metric_name: Name of the metric
            value: Data point value
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self.lock:
            self.data_buffer[metric_name].append((timestamp, value))
    
    def predict_metric(self, metric_name: str, horizon_hours: Optional[int] = None) -> Optional[PredictionResult]:
        """
        Predict future value for a metric
        
        Args:
            metric_name: Name of the metric to predict
            horizon_hours: Prediction horizon in hours
            
        Returns:
            Prediction result or None if insufficient data
        """
        if horizon_hours is None:
            horizon_hours = self.config.prediction_horizon
        
        with self.lock:
            data_points = self.data_buffer[metric_name]
            
            if len(data_points) < self.config.min_data_points:
                return None
            
            # Get current value
            current_value = data_points[-1][1] if data_points else 0.0
            
            # Perform trend analysis
            trend_analysis = self._analyze_trend(metric_name)
            
            # Perform seasonal analysis
            seasonal_analysis = self._analyze_seasonal(metric_name)
            
            # Make prediction
            prediction = self._make_prediction(
                metric_name, current_value, trend_analysis, 
                seasonal_analysis, horizon_hours
            )
            
            # Store prediction
            if prediction:
                self.predictions[metric_name].append(prediction)
                
                # Clean old predictions
                cutoff_time = time.time() - self.config.max_prediction_age
                self.predictions[metric_name] = [
                    p for p in self.predictions[metric_name] 
                    if p.prediction_time > cutoff_time
                ]
            
            return prediction
    
    def _analyze_trend(self, metric_name: str) -> TrendAnalysis:
        """Analyze trend in metric data"""
        if not self.config.enable_trend_analysis:
            return TrendAnalysis("stable", 0.0, 0.0, 0.0, 1.0, (0.0, 0.0))
        
        data_points = self.data_buffer[metric_name]
        if len(data_points) < 10:
            return TrendAnalysis("stable", 0.0, 0.0, 0.0, 1.0, (0.0, 0.0))
        
        # Extract timestamps and values
        timestamps = [point[0] for point in data_points]
        values = [point[1] for point in data_points]
        
        # Normalize timestamps
        min_time = min(timestamps)
        normalized_times = [(t - min_time) / 3600 for t in timestamps]  # Convert to hours
        
        # Calculate linear regression
        n = len(values)
        x_mean = statistics.mean(normalized_times)
        y_mean = statistics.mean(values)
        
        numerator = sum((normalized_times[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((normalized_times[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return TrendAnalysis("stable", 0.0, 0.0, 0.0, 1.0, (0.0, 0.0))
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Calculate R-squared
        y_pred = [slope * x + intercept for x in normalized_times]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        # Determine trend direction and strength
        if abs(slope) < self.config.trend_sensitivity:
            direction = "stable"
            strength = 0.0
        else:
            direction = "increasing" if slope > 0 else "decreasing"
            strength = min(abs(slope) / self.config.trend_sensitivity, 1.0)
        
        # Calculate confidence interval (simplified)
        std_error = (ss_res / (n - 2)) ** 0.5 if n > 2 else 0.0
        confidence_interval = (slope - 2 * std_error, slope + 2 * std_error)
        
        return TrendAnalysis(
            direction=direction,
            strength=strength,
            slope=slope,
            r_squared=r_squared,
            p_value=0.05,  # Simplified
            confidence_interval=confidence_interval
        )
    
    def _analyze_seasonal(self, metric_name: str) -> SeasonalAnalysis:
        """Analyze seasonal patterns in metric data"""
        if not self.config.enable_seasonal_analysis:
            return SeasonalAnalysis(24, 0.0, [], 1.0, 0.0)
        
        data_points = self.data_buffer[metric_name]
        if len(data_points) < 48:  # Need at least 2 days of hourly data
            return SeasonalAnalysis(24, 0.0, [], 1.0, 0.0)
        
        # Group data by hour of day
        hourly_data = defaultdict(list)
        for timestamp, value in data_points:
            dt = datetime.fromtimestamp(timestamp)
            hour = dt.hour
            hourly_data[hour].append(value)
        
        if len(hourly_data) < 12:  # Need data for most hours
            return SeasonalAnalysis(24, 0.0, [], 1.0, 0.0)
        
        # Calculate seasonal pattern
        seasonal_pattern = []
        for hour in range(24):
            if hour in hourly_data:
                seasonal_pattern.append(statistics.mean(hourly_data[hour]))
            else:
                seasonal_pattern.append(0.0)
        
        # Calculate seasonal strength
        overall_mean = statistics.mean(seasonal_pattern)
        if overall_mean == 0:
            seasonal_strength = 0.0
        else:
            seasonal_variance = statistics.variance(seasonal_pattern)
            total_variance = statistics.variance([point[1] for point in data_points])
            seasonal_strength = seasonal_variance / total_variance if total_variance > 0 else 0.0
        
        # Get current seasonal factor
        current_hour = datetime.fromtimestamp(data_points[-1][0]).hour
        current_seasonal_factor = seasonal_pattern[current_hour] / overall_mean if overall_mean > 0 else 1.0
        
        return SeasonalAnalysis(
            seasonal_period=24,
            seasonal_strength=seasonal_strength,
            seasonal_pattern=seasonal_pattern,
            seasonal_factor=current_seasonal_factor,
            confidence=min(seasonal_strength, 1.0)
        )
    
    def _make_prediction(self, metric_name: str, current_value: float, 
                        trend_analysis: TrendAnalysis, seasonal_analysis: SeasonalAnalysis,
                        horizon_hours: int) -> Optional[PredictionResult]:
        """Make prediction based on trend and seasonal analysis"""
        
        # Calculate trend component
        trend_component = trend_analysis.slope * horizon_hours
        
        # Calculate seasonal component
        seasonal_component = seasonal_analysis.seasonal_factor
        
        # Make prediction
        predicted_value = current_value + trend_component
        predicted_value *= seasonal_component
        
        # Determine prediction type
        if trend_analysis.strength > 0.5:
            prediction_type = PredictionType.TREND
        elif seasonal_analysis.seasonal_strength > 0.3:
            prediction_type = PredictionType.SEASONAL
        else:
            prediction_type = PredictionType.THRESHOLD_BREACH
        
        # Calculate confidence
        confidence_score = (trend_analysis.r_squared + seasonal_analysis.confidence) / 2
        if confidence_score > 0.8:
            confidence = PredictionConfidence.VERY_HIGH
        elif confidence_score > 0.6:
            confidence = PredictionConfidence.HIGH
        elif confidence_score > 0.4:
            confidence = PredictionConfidence.MEDIUM
        else:
            confidence = PredictionConfidence.LOW
        
        # Determine alert level
        alert_level = self._determine_alert_level(
            metric_name, current_value, predicted_value, 
            trend_analysis, seasonal_analysis
        )
        
        # Create prediction result
        result = PredictionResult(
            metric_name=metric_name,
            prediction_type=prediction_type,
            predicted_value=predicted_value,
            confidence=confidence,
            alert_level=alert_level,
            prediction_time=time.time(),
            horizon_hours=horizon_hours,
            current_value=current_value,
            trend_direction=trend_analysis.direction,
            trend_strength=trend_analysis.strength,
            seasonal_factor=seasonal_analysis.seasonal_factor,
            capacity_utilization=0.0,  # Will be calculated separately
            message=self._generate_prediction_message(
                metric_name, predicted_value, current_value, 
                trend_analysis, seasonal_analysis, horizon_hours
            ),
            metadata={
                'trend_slope': trend_analysis.slope,
                'trend_r_squared': trend_analysis.r_squared,
                'seasonal_strength': seasonal_analysis.seasonal_strength,
                'confidence_score': confidence_score
            }
        )
        
        return result
    
    def _determine_alert_level(self, metric_name: str, current_value: float, 
                              predicted_value: float, trend_analysis: TrendAnalysis,
                              seasonal_analysis: SeasonalAnalysis) -> AlertLevel:
        """Determine alert level based on prediction"""
        
        # Check custom rules first
        if metric_name in self.config.custom_rules:
            rule = self.config.custom_rules[metric_name]
            thresholds = rule.get('thresholds', {})
            
            if predicted_value > thresholds.get('critical', float('inf')):
                return AlertLevel.CRITICAL
            elif predicted_value > thresholds.get('warning', float('inf')):
                return AlertLevel.WARNING
            elif predicted_value > thresholds.get('info', float('inf')):
                return AlertLevel.INFO
        
        # Default logic based on trend and seasonal analysis
        change_percent = abs(predicted_value - current_value) / current_value if current_value != 0 else 0
        
        if change_percent > 0.5:  # 50% change
            return AlertLevel.CRITICAL
        elif change_percent > 0.2:  # 20% change
            return AlertLevel.WARNING
        elif change_percent > 0.1:  # 10% change
            return AlertLevel.INFO
        else:
            return AlertLevel.INFO
    
    def _generate_prediction_message(self, metric_name: str, predicted_value: float,
                                   current_value: float, trend_analysis: TrendAnalysis,
                                   seasonal_analysis: SeasonalAnalysis, 
                                   horizon_hours: int) -> str:
        """Generate human-readable prediction message"""
        
        change = predicted_value - current_value
        change_percent = (change / current_value * 100) if current_value != 0 else 0
        
        message_parts = []
        
        # Trend information
        if trend_analysis.strength > 0.3:
            if trend_analysis.direction == "increasing":
                message_parts.append(f"Trending upward (slope: {trend_analysis.slope:.4f})")
            elif trend_analysis.direction == "decreasing":
                message_parts.append(f"Trending downward (slope: {trend_analysis.slope:.4f})")
        
        # Seasonal information
        if seasonal_analysis.seasonal_strength > 0.3:
            message_parts.append(f"Seasonal pattern detected (strength: {seasonal_analysis.seasonal_strength:.2f})")
        
        # Prediction summary
        if change_percent > 0:
            message_parts.append(f"Predicted {change_percent:.1f}% increase in {horizon_hours}h")
        else:
            message_parts.append(f"Predicted {abs(change_percent):.1f}% decrease in {horizon_hours}h")
        
        return ". ".join(message_parts)
    
    def predict_capacity_utilization(self, metric_name: str, 
                                   capacity_limit: float) -> Optional[PredictionResult]:
        """Predict capacity utilization"""
        if not self.config.enable_capacity_planning:
            return None
        
        prediction = self.predict_metric(metric_name)
        if not prediction:
            return None
        
        # Calculate capacity utilization
        utilization = (prediction.predicted_value / capacity_limit) * 100
        prediction.capacity_utilization = utilization
        
        # Update alert level based on capacity
        if utilization > 90:
            prediction.alert_level = AlertLevel.CRITICAL
        elif utilization > 75:
            prediction.alert_level = AlertLevel.WARNING
        elif utilization > 60:
            prediction.alert_level = AlertLevel.INFO
        
        # Update message
        prediction.message += f". Capacity utilization: {utilization:.1f}%"
        
        return prediction
    
    def predict_performance_degradation(self, metric_name: str, 
                                      baseline_performance: float) -> Optional[PredictionResult]:
        """Predict performance degradation"""
        if not self.config.enable_performance_prediction:
            return None
        
        prediction = self.predict_metric(metric_name)
        if not prediction:
            return None
        
        # Calculate performance degradation
        degradation = ((baseline_performance - prediction.predicted_value) / baseline_performance) * 100
        
        # Update alert level based on degradation
        if degradation > 50:
            prediction.alert_level = AlertLevel.CRITICAL
        elif degradation > 25:
            prediction.alert_level = AlertLevel.WARNING
        elif degradation > 10:
            prediction.alert_level = AlertLevel.INFO
        
        # Update message
        prediction.message += f". Performance degradation: {degradation:.1f}%"
        
        return prediction
    
    def add_alert_handler(self, handler: Callable[[PredictionResult], None]):
        """Add alert handler for predictions"""
        self.alert_handlers.append(handler)
    
    def trigger_alerts(self, prediction: PredictionResult):
        """Trigger alerts for prediction"""
        if not self.config.alert_on_prediction:
            return
        
        # Check if alert should be triggered
        if prediction.alert_level in [AlertLevel.WARNING, AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
            for handler in self.alert_handlers:
                try:
                    handler(prediction)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
    
    def get_prediction_history(self, metric_name: str, 
                             hours: int = 24) -> List[PredictionResult]:
        """Get prediction history for analysis"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            return [p for p in self.predictions[metric_name] 
                   if p.prediction_time > cutoff_time]
    
    def get_metrics_with_predictions(self) -> List[str]:
        """Get list of metrics that have predictions"""
        with self.lock:
            return list(self.predictions.keys())
    
    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        with self.lock:
            total_predictions = sum(len(predictions) for predictions in self.predictions.values())
            
            if total_predictions == 0:
                return {
                    'total_predictions': 0,
                    'metrics_monitored': len(self.data_buffer),
                    'alert_distribution': {},
                    'confidence_distribution': {},
                    'prediction_types': {}
                }
            
            # Calculate distributions
            alert_counts = defaultdict(int)
            confidence_counts = defaultdict(int)
            type_counts = defaultdict(int)
            
            for predictions in self.predictions.values():
                for prediction in predictions:
                    alert_counts[prediction.alert_level.value] += 1
                    confidence_counts[prediction.confidence.value] += 1
                    type_counts[prediction.prediction_type.value] += 1
            
            return {
                'total_predictions': total_predictions,
                'metrics_monitored': len(self.data_buffer),
                'alert_distribution': dict(alert_counts),
                'confidence_distribution': dict(confidence_counts),
                'prediction_types': dict(type_counts)
            }
    
    def validate_prediction(self, metric_name: str, actual_value: float, 
                          prediction_time: float) -> Dict[str, Any]:
        """Validate a prediction against actual value"""
        with self.lock:
            # Find the closest prediction
            predictions = self.predictions[metric_name]
            if not predictions:
                return {'error': 'No predictions found'}
            
            # Find prediction closest to the validation time
            closest_prediction = min(predictions, 
                                   key=lambda p: abs(p.prediction_time - prediction_time))
            
            # Calculate error metrics
            absolute_error = abs(actual_value - closest_prediction.predicted_value)
            relative_error = absolute_error / actual_value if actual_value != 0 else 0
            percentage_error = relative_error * 100
            
            return {
                'prediction_time': closest_prediction.prediction_time,
                'predicted_value': closest_prediction.predicted_value,
                'actual_value': actual_value,
                'absolute_error': absolute_error,
                'relative_error': relative_error,
                'percentage_error': percentage_error,
                'confidence': closest_prediction.confidence.value,
                'prediction_type': closest_prediction.prediction_type.value
            }
    
    def reset(self):
        """Reset the predictive monitor state"""
        with self.lock:
            self.data_buffer.clear()
            self.predictions.clear()
            self.trend_models.clear()
            self.seasonal_models.clear()
            self.capacity_models.clear()


# Global predictive monitor instance
_predictive_monitor: Optional[PredictiveMonitor] = None


def get_predictive_monitor(config: Optional[PredictionConfig] = None) -> PredictiveMonitor:
    """Get global predictive monitor instance"""
    global _predictive_monitor
    if _predictive_monitor is None:
        if config is None:
            config = PredictionConfig()
        _predictive_monitor = PredictiveMonitor(config)
    return _predictive_monitor


def add_prediction_data(metric_name: str, value: float, 
                       timestamp: Optional[float] = None,
                       config: Optional[PredictionConfig] = None):
    """Global function to add prediction data"""
    monitor = get_predictive_monitor(config)
    monitor.add_data_point(metric_name, value, timestamp)


def predict_metric(metric_name: str, horizon_hours: Optional[int] = None,
                  config: Optional[PredictionConfig] = None) -> Optional[PredictionResult]:
    """Global function to predict metric"""
    monitor = get_predictive_monitor(config)
    return monitor.predict_metric(metric_name, horizon_hours)


def predict_capacity(metric_name: str, capacity_limit: float,
                    config: Optional[PredictionConfig] = None) -> Optional[PredictionResult]:
    """Global function to predict capacity utilization"""
    monitor = get_predictive_monitor(config)
    return monitor.predict_capacity_utilization(metric_name, capacity_limit)


def predict_performance(metric_name: str, baseline_performance: float,
                       config: Optional[PredictionConfig] = None) -> Optional[PredictionResult]:
    """Global function to predict performance degradation"""
    monitor = get_predictive_monitor(config)
    return monitor.predict_performance_degradation(metric_name, baseline_performance)


def get_prediction_statistics(config: Optional[PredictionConfig] = None) -> Dict[str, Any]:
    """Global function to get prediction statistics"""
    monitor = get_predictive_monitor(config)
    return monitor.get_prediction_statistics()


def validate_prediction(metric_name: str, actual_value: float, prediction_time: float,
                       config: Optional[PredictionConfig] = None) -> Dict[str, Any]:
    """Global function to validate prediction"""
    monitor = get_predictive_monitor(config)
    return monitor.validate_prediction(metric_name, actual_value, prediction_time) 