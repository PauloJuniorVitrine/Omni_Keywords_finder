"""
🔍 Advanced Anomaly Detection System
📅 Generated: 2025-01-27
🎯 Purpose: Multi-algorithm anomaly detection with configurable thresholds
📋 Tracing ID: ANOMALY_DETECTION_001_20250127
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

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies"""
    SPIKE = "spike"
    DROP = "drop"
    TREND = "trend"
    SEASONAL = "seasonal"
    PATTERN = "pattern"
    THRESHOLD = "threshold"
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"


class AnomalySeverity(Enum):
    """Anomaly severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection"""
    algorithm: str = "statistical"
    window_size: int = 100
    threshold_multiplier: float = 2.0
    min_data_points: int = 10
    confidence_level: float = 0.95
    enable_seasonal: bool = True
    enable_trend: bool = True
    enable_pattern: bool = True
    alert_on_anomaly: bool = True
    auto_adjust_thresholds: bool = True
    learning_rate: float = 0.1
    max_anomalies_per_hour: int = 10
    cooldown_period: int = 300  # seconds
    custom_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyResult:
    """Result of anomaly detection"""
    is_anomaly: bool
    anomaly_type: Optional[AnomalyType] = None
    severity: AnomalySeverity = AnomalySeverity.LOW
    confidence: float = 0.0
    score: float = 0.0
    threshold: float = 0.0
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class AnomalyAlert:
    """Anomaly alert information"""
    metric_name: str
    value: float
    threshold: float
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    message: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class AnomalyDetector:
    """
    Advanced anomaly detection system with multiple algorithms
    """
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.data_buffer = deque(maxlen=config.window_size)
        self.anomaly_history = deque(maxlen=1000)
        self.last_alert_time = defaultdict(float)
        self.lock = threading.RLock()
        self.algorithms = self._setup_algorithms()
        
    def _setup_algorithms(self) -> Dict[str, Callable]:
        """Setup available anomaly detection algorithms"""
        return {
            "statistical": self._statistical_detection,
            "zscore": self._zscore_detection,
            "iqr": self._iqr_detection,
            "mad": self._mad_detection,
            "exponential": self._exponential_detection,
            "seasonal": self._seasonal_detection,
            "trend": self._trend_detection,
            "pattern": self._pattern_detection,
            "threshold": self._threshold_detection,
            "ensemble": self._ensemble_detection
        }
    
    def add_data_point(self, value: float, timestamp: Optional[float] = None):
        """
        Add a new data point for analysis
        
        Args:
            value: Data point value
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self.lock:
            self.data_buffer.append((timestamp, value))
    
    def detect_anomaly(self, value: float, metric_name: str = "unknown") -> AnomalyResult:
        """
        Detect anomaly in a data point
        
        Args:
            value: Data point value to analyze
            metric_name: Name of the metric for alerting
            
        Returns:
            Anomaly detection result
        """
        with self.lock:
            # Add data point to buffer
            self.add_data_point(value)
            
            # Check if we have enough data
            if len(self.data_buffer) < self.config.min_data_points:
                return AnomalyResult(
                    is_anomaly=False,
                    message=f"Insufficient data points ({len(self.data_buffer)} < {self.config.min_data_points})"
                )
            
            # Run selected algorithm
            algorithm_func = self.algorithms.get(self.config.algorithm)
            if algorithm_func is None:
                logger.error(f"Unknown algorithm: {self.config.algorithm}")
                return AnomalyResult(is_anomaly=False, message="Unknown algorithm")
            
            try:
                result = algorithm_func(value, metric_name)
                
                # Store anomaly if detected
                if result.is_anomaly:
                    self.anomaly_history.append({
                        'timestamp': time.time(),
                        'value': value,
                        'metric_name': metric_name,
                        'result': result
                    })
                
                return result
                
            except Exception as e:
                logger.error(f"Error in anomaly detection: {e}")
                return AnomalyResult(
                    is_anomaly=False,
                    message=f"Detection error: {str(e)}"
                )
    
    def _statistical_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Statistical anomaly detection using mean and standard deviation"""
        if len(self.data_buffer) < 2:
            return AnomalyResult(is_anomaly=False, message="Insufficient data")
        
        # Extract values from buffer
        values = [point[1] for point in self.data_buffer]
        
        # Calculate statistics
        mean = statistics.mean(values[:-1])  # Exclude current value
        std = statistics.stdev(values[:-1]) if len(values) > 2 else 0
        
        if std == 0:
            return AnomalyResult(is_anomaly=False, message="No variance in data")
        
        # Calculate z-score
        z_score = abs((value - mean) / std)
        threshold = self.config.threshold_multiplier
        
        is_anomaly = z_score > threshold
        confidence = min(z_score / threshold, 1.0)
        
        # Determine severity
        if z_score > threshold * 3:
            severity = AnomalySeverity.CRITICAL
        elif z_score > threshold * 2:
            severity = AnomalySeverity.HIGH
        elif z_score > threshold * 1.5:
            severity = AnomalySeverity.MEDIUM
        else:
            severity = AnomalySeverity.LOW
        
        # Determine anomaly type
        if value > mean + threshold * std:
            anomaly_type = AnomalyType.SPIKE
        elif value < mean - threshold * std:
            anomaly_type = AnomalyType.DROP
        else:
            anomaly_type = AnomalyType.STATISTICAL
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            score=z_score,
            threshold=threshold,
            message=f"Z-score: {z_score:.2f}, Threshold: {threshold:.2f}"
        )
    
    def _zscore_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Z-score based anomaly detection"""
        return self._statistical_detection(value, metric_name)
    
    def _iqr_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Interquartile range based anomaly detection"""
        if len(self.data_buffer) < 4:
            return AnomalyResult(is_anomaly=False, message="Insufficient data for IQR")
        
        values = [point[1] for point in self.data_buffer[:-1]]  # Exclude current value
        values.sort()
        
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        
        if iqr == 0:
            return AnomalyResult(is_anomaly=False, message="No variance in data")
        
        lower_bound = q1 - self.config.threshold_multiplier * iqr
        upper_bound = q3 + self.config.threshold_multiplier * iqr
        
        is_anomaly = value < lower_bound or value > upper_bound
        
        if is_anomaly:
            if value > upper_bound:
                anomaly_type = AnomalyType.SPIKE
                distance = (value - upper_bound) / iqr
            else:
                anomaly_type = AnomalyType.DROP
                distance = (lower_bound - value) / iqr
            
            confidence = min(distance / self.config.threshold_multiplier, 1.0)
            
            if distance > self.config.threshold_multiplier * 2:
                severity = AnomalySeverity.HIGH
            elif distance > self.config.threshold_multiplier * 1.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
        else:
            anomaly_type = None
            confidence = 0.0
            severity = AnomalySeverity.LOW
            distance = 0.0
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            score=distance,
            threshold=self.config.threshold_multiplier,
            message=f"IQR: {iqr:.2f}, Bounds: [{lower_bound:.2f}, {upper_bound:.2f}]"
        )
    
    def _mad_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Median Absolute Deviation based anomaly detection"""
        if len(self.data_buffer) < 3:
            return AnomalyResult(is_anomaly=False, message="Insufficient data for MAD")
        
        values = [point[1] for point in self.data_buffer[:-1]]  # Exclude current value
        median = statistics.median(values)
        
        # Calculate MAD
        mad_values = [abs(v - median) for v in values]
        mad = statistics.median(mad_values)
        
        if mad == 0:
            return AnomalyResult(is_anomaly=False, message="No variance in data")
        
        # Calculate modified z-score
        modified_z_score = abs((value - median) / mad)
        threshold = self.config.threshold_multiplier
        
        is_anomaly = modified_z_score > threshold
        confidence = min(modified_z_score / threshold, 1.0)
        
        # Determine severity and type
        if is_anomaly:
            if value > median:
                anomaly_type = AnomalyType.SPIKE
            else:
                anomaly_type = AnomalyType.DROP
            
            if modified_z_score > threshold * 3:
                severity = AnomalySeverity.CRITICAL
            elif modified_z_score > threshold * 2:
                severity = AnomalySeverity.HIGH
            elif modified_z_score > threshold * 1.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
        else:
            anomaly_type = None
            severity = AnomalySeverity.LOW
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            score=modified_z_score,
            threshold=threshold,
            message=f"MAD: {mad:.2f}, Modified Z-score: {modified_z_score:.2f}"
        )
    
    def _exponential_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Exponential smoothing based anomaly detection"""
        if len(self.data_buffer) < 2:
            return AnomalyResult(is_anomaly=False, message="Insufficient data")
        
        values = [point[1] for point in self.data_buffer[:-1]]  # Exclude current value
        
        # Calculate exponential moving average
        alpha = self.config.learning_rate
        ema = values[0]
        for v in values[1:]:
            ema = alpha * v + (1 - alpha) * ema
        
        # Calculate prediction error
        error = abs(value - ema)
        
        # Calculate error statistics
        errors = []
        for i in range(1, len(values)):
            pred_error = abs(values[i] - (alpha * values[i-1] + (1 - alpha) * ema))
            errors.append(pred_error)
        
        if not errors:
            return AnomalyResult(is_anomaly=False, message="Insufficient error data")
        
        error_mean = statistics.mean(errors)
        error_std = statistics.stdev(errors) if len(errors) > 1 else 0
        
        if error_std == 0:
            return AnomalyResult(is_anomaly=False, message="No error variance")
        
        # Calculate anomaly score
        score = (error - error_mean) / error_std
        threshold = self.config.threshold_multiplier
        
        is_anomaly = abs(score) > threshold
        confidence = min(abs(score) / threshold, 1.0)
        
        if is_anomaly:
            if value > ema:
                anomaly_type = AnomalyType.SPIKE
            else:
                anomaly_type = AnomalyType.DROP
            
            if abs(score) > threshold * 3:
                severity = AnomalySeverity.CRITICAL
            elif abs(score) > threshold * 2:
                severity = AnomalySeverity.HIGH
            elif abs(score) > threshold * 1.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
        else:
            anomaly_type = None
            severity = AnomalySeverity.LOW
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            score=abs(score),
            threshold=threshold,
            message=f"EMA: {ema:.2f}, Error: {error:.2f}, Score: {score:.2f}"
        )
    
    def _seasonal_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Seasonal pattern based anomaly detection"""
        if not self.config.enable_seasonal:
            return AnomalyResult(is_anomaly=False, message="Seasonal detection disabled")
        
        if len(self.data_buffer) < 24:  # Need at least 24 data points for basic seasonality
            return AnomalyResult(is_anomaly=False, message="Insufficient data for seasonal analysis")
        
        # Simple seasonal detection based on time of day
        current_time = datetime.fromtimestamp(self.data_buffer[-1][0])
        hour = current_time.hour
        
        # Group values by hour
        hourly_values = defaultdict(list)
        for timestamp, val in self.data_buffer[:-1]:  # Exclude current value
            dt = datetime.fromtimestamp(timestamp)
            hourly_values[dt.hour].append(val)
        
        if hour not in hourly_values or len(hourly_values[hour]) < 2:
            return AnomalyResult(is_anomaly=False, message="Insufficient seasonal data")
        
        # Calculate seasonal statistics
        seasonal_values = hourly_values[hour]
        seasonal_mean = statistics.mean(seasonal_values)
        seasonal_std = statistics.stdev(seasonal_values) if len(seasonal_values) > 1 else 0
        
        if seasonal_std == 0:
            return AnomalyResult(is_anomaly=False, message="No seasonal variance")
        
        # Calculate seasonal z-score
        seasonal_z_score = abs((value - seasonal_mean) / seasonal_std)
        threshold = self.config.threshold_multiplier
        
        is_anomaly = seasonal_z_score > threshold
        confidence = min(seasonal_z_score / threshold, 1.0)
        
        if is_anomaly:
            if value > seasonal_mean:
                anomaly_type = AnomalyType.SEASONAL
            else:
                anomaly_type = AnomalyType.SEASONAL
            
            if seasonal_z_score > threshold * 2:
                severity = AnomalySeverity.HIGH
            elif seasonal_z_score > threshold * 1.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
        else:
            anomaly_type = None
            severity = AnomalySeverity.LOW
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            score=seasonal_z_score,
            threshold=threshold,
            message=f"Seasonal Z-score: {seasonal_z_score:.2f}, Hour: {hour}"
        )
    
    def _trend_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Trend based anomaly detection"""
        if not self.config.enable_trend:
            return AnomalyResult(is_anomaly=False, message="Trend detection disabled")
        
        if len(self.data_buffer) < 10:
            return AnomalyResult(is_anomaly=False, message="Insufficient data for trend analysis")
        
        # Calculate trend using linear regression
        values = [point[1] for point in self.data_buffer[:-1]]  # Exclude current value
        timestamps = [point[0] for point in self.data_buffer[:-1]]
        
        if len(values) < 2:
            return AnomalyResult(is_anomaly=False, message="Insufficient trend data")
        
        # Simple linear trend calculation
        n = len(values)
        x_mean = statistics.mean(timestamps)
        y_mean = statistics.mean(values)
        
        numerator = sum((timestamps[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((timestamps[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return AnomalyResult(is_anomaly=False, message="No trend variance")
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Predict expected value
        current_timestamp = self.data_buffer[-1][0]
        expected_value = slope * current_timestamp + intercept
        
        # Calculate prediction error
        error = abs(value - expected_value)
        
        # Calculate error statistics
        errors = []
        for i in range(1, len(values)):
            pred = slope * timestamps[i] + intercept
            pred_error = abs(values[i] - pred)
            errors.append(pred_error)
        
        if not errors:
            return AnomalyResult(is_anomaly=False, message="Insufficient error data")
        
        error_mean = statistics.mean(errors)
        error_std = statistics.stdev(errors) if len(errors) > 1 else 0
        
        if error_std == 0:
            return AnomalyResult(is_anomaly=False, message="No error variance")
        
        # Calculate trend anomaly score
        score = (error - error_mean) / error_std
        threshold = self.config.threshold_multiplier
        
        is_anomaly = abs(score) > threshold
        confidence = min(abs(score) / threshold, 1.0)
        
        if is_anomaly:
            if value > expected_value:
                anomaly_type = AnomalyType.TREND
            else:
                anomaly_type = AnomalyType.TREND
            
            if abs(score) > threshold * 2:
                severity = AnomalySeverity.HIGH
            elif abs(score) > threshold * 1.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
        else:
            anomaly_type = None
            severity = AnomalySeverity.LOW
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            score=abs(score),
            threshold=threshold,
            message=f"Trend slope: {slope:.4f}, Expected: {expected_value:.2f}, Error: {error:.2f}"
        )
    
    def _pattern_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Pattern based anomaly detection"""
        if not self.config.enable_pattern:
            return AnomalyResult(is_anomaly=False, message="Pattern detection disabled")
        
        if len(self.data_buffer) < 20:
            return AnomalyResult(is_anomaly=False, message="Insufficient data for pattern analysis")
        
        # Simple pattern detection based on recent values
        recent_values = [point[1] for point in list(self.data_buffer)[-10:-1]]  # Last 9 values
        
        if len(recent_values) < 3:
            return AnomalyResult(is_anomaly=False, message="Insufficient pattern data")
        
        # Check for unusual patterns
        pattern_score = 0.0
        
        # Check for sudden changes
        if len(recent_values) >= 2:
            recent_change = abs(recent_values[-1] - recent_values[-2])
            avg_change = statistics.mean([abs(recent_values[i] - recent_values[i-1]) 
                                        for i in range(1, len(recent_values))])
            
            if avg_change > 0:
                pattern_score += (recent_change / avg_change - 1) * 0.5
        
        # Check for value outside recent range
        recent_min = min(recent_values)
        recent_max = max(recent_values)
        recent_range = recent_max - recent_min
        
        if recent_range > 0:
            if value < recent_min:
                pattern_score += (recent_min - value) / recent_range
            elif value > recent_max:
                pattern_score += (value - recent_max) / recent_range
        
        threshold = self.config.threshold_multiplier
        is_anomaly = pattern_score > threshold
        confidence = min(pattern_score / threshold, 1.0)
        
        if is_anomaly:
            if value > recent_max:
                anomaly_type = AnomalyType.PATTERN
            else:
                anomaly_type = AnomalyType.PATTERN
            
            if pattern_score > threshold * 2:
                severity = AnomalySeverity.HIGH
            elif pattern_score > threshold * 1.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
        else:
            anomaly_type = None
            severity = AnomalySeverity.LOW
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            score=pattern_score,
            threshold=threshold,
            message=f"Pattern score: {pattern_score:.2f}, Recent range: [{recent_min:.2f}, {recent_max:.2f}]"
        )
    
    def _threshold_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Simple threshold based anomaly detection"""
        # Check custom rules first
        if metric_name in self.config.custom_rules:
            rule = self.config.custom_rules[metric_name]
            min_threshold = rule.get('min', float('-inf'))
            max_threshold = rule.get('max', float('inf'))
            
            if value < min_threshold or value > max_threshold:
                if value > max_threshold:
                    anomaly_type = AnomalyType.THRESHOLD
                    severity = AnomalySeverity.HIGH
                    message = f"Value {value:.2f} exceeds max threshold {max_threshold:.2f}"
                else:
                    anomaly_type = AnomalyType.THRESHOLD
                    severity = AnomalySeverity.HIGH
                    message = f"Value {value:.2f} below min threshold {min_threshold:.2f}"
                
                return AnomalyResult(
                    is_anomaly=True,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    confidence=1.0,
                    score=1.0,
                    threshold=1.0,
                    message=message
                )
        
        return AnomalyResult(is_anomaly=False, message="No threshold violation")
    
    def _ensemble_detection(self, value: float, metric_name: str) -> AnomalyResult:
        """Ensemble anomaly detection using multiple algorithms"""
        algorithms = ["statistical", "iqr", "mad", "exponential"]
        results = []
        
        for algo in algorithms:
            try:
                # Temporarily change algorithm
                original_algo = self.config.algorithm
                self.config.algorithm = algo
                
                # Run detection
                result = self.algorithms[algo](value, metric_name)
                results.append(result)
                
                # Restore original algorithm
                self.config.algorithm = original_algo
                
            except Exception as e:
                logger.warning(f"Error in ensemble algorithm {algo}: {e}")
                continue
        
        if not results:
            return AnomalyResult(is_anomaly=False, message="No ensemble results")
        
        # Count anomalies
        anomaly_count = sum(1 for r in results if r.is_anomaly)
        total_count = len(results)
        
        # Calculate ensemble score
        ensemble_score = anomaly_count / total_count
        threshold = 0.5  # At least 50% of algorithms must detect anomaly
        
        is_anomaly = ensemble_score >= threshold
        confidence = ensemble_score
        
        if is_anomaly:
            # Determine overall severity and type
            severities = [r.severity for r in results if r.is_anomaly]
            types = [r.anomaly_type for r in results if r.is_anomaly]
            
            # Most common severity
            severity = max(set(severities), key=severities.count) if severities else AnomalySeverity.MEDIUM
            
            # Most common type
            anomaly_type = max(set(types), key=types.count) if types else AnomalyType.STATISTICAL
            
            message = f"Ensemble: {anomaly_count}/{total_count} algorithms detected anomaly"
        else:
            severity = AnomalySeverity.LOW
            anomaly_type = None
            message = f"Ensemble: {anomaly_count}/{total_count} algorithms detected anomaly"
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=confidence,
            score=ensemble_score,
            threshold=threshold,
            message=message
        )
    
    def should_alert(self, metric_name: str, severity: AnomalySeverity) -> bool:
        """Check if an alert should be sent based on cooldown and limits"""
        if not self.config.alert_on_anomaly:
            return False
        
        current_time = time.time()
        last_alert = self.last_alert_time[metric_name]
        
        # Check cooldown period
        if current_time - last_alert < self.config.cooldown_period:
            return False
        
        # Check hourly limit
        hour_ago = current_time - 3600
        recent_alerts = sum(1 for alert in self.anomaly_history 
                          if alert['metric_name'] == metric_name and 
                          alert['timestamp'] > hour_ago)
        
        if recent_alerts >= self.config.max_anomalies_per_hour:
            return False
        
        return True
    
    def get_anomaly_history(self, metric_name: Optional[str] = None, 
                          hours: int = 24) -> List[Dict[str, Any]]:
        """Get anomaly history for analysis"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            if metric_name:
                history = [alert for alert in self.anomaly_history
                          if alert['metric_name'] == metric_name and 
                          alert['timestamp'] > cutoff_time]
            else:
                history = [alert for alert in self.anomaly_history
                          if alert['timestamp'] > cutoff_time]
        
        return history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get anomaly detection statistics"""
        with self.lock:
            total_anomalies = len(self.anomaly_history)
            
            if total_anomalies == 0:
                return {
                    'total_anomalies': 0,
                    'anomaly_rate': 0.0,
                    'severity_distribution': {},
                    'type_distribution': {},
                    'recent_anomalies': 0
                }
            
            # Calculate anomaly rate
            if len(self.data_buffer) > 0:
                anomaly_rate = total_anomalies / len(self.data_buffer)
            else:
                anomaly_rate = 0.0
            
            # Severity distribution
            severity_counts = defaultdict(int)
            type_counts = defaultdict(int)
            
            for alert in self.anomaly_history:
                severity_counts[alert['result'].severity.value] += 1
                if alert['result'].anomaly_type:
                    type_counts[alert['result'].anomaly_type.value] += 1
            
            # Recent anomalies (last hour)
            hour_ago = time.time() - 3600
            recent_anomalies = sum(1 for alert in self.anomaly_history
                                 if alert['timestamp'] > hour_ago)
            
            return {
                'total_anomalies': total_anomalies,
                'anomaly_rate': anomaly_rate,
                'severity_distribution': dict(severity_counts),
                'type_distribution': dict(type_counts),
                'recent_anomalies': recent_anomalies,
                'data_points': len(self.data_buffer)
            }
    
    def reset(self):
        """Reset the anomaly detector state"""
        with self.lock:
            self.data_buffer.clear()
            self.anomaly_history.clear()
            self.last_alert_time.clear()


# Global anomaly detector instance
_anomaly_detector: Optional[AnomalyDetector] = None


def get_anomaly_detector(config: Optional[AnomalyConfig] = None) -> AnomalyDetector:
    """Get global anomaly detector instance"""
    global _anomaly_detector
    if _anomaly_detector is None:
        if config is None:
            config = AnomalyConfig()
        _anomaly_detector = AnomalyDetector(config)
    return _anomaly_detector


def detect_anomaly(value: float, metric_name: str = "unknown", 
                  config: Optional[AnomalyConfig] = None) -> AnomalyResult:
    """Global function to detect anomalies"""
    detector = get_anomaly_detector(config)
    return detector.detect_anomaly(value, metric_name)


def add_data_point(value: float, timestamp: Optional[float] = None,
                  config: Optional[AnomalyConfig] = None):
    """Global function to add data points"""
    detector = get_anomaly_detector(config)
    detector.add_data_point(value, timestamp)


def get_anomaly_statistics(config: Optional[AnomalyConfig] = None) -> Dict[str, Any]:
    """Global function to get anomaly statistics"""
    detector = get_anomaly_detector(config)
    return detector.get_statistics() 