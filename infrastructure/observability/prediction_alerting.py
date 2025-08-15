"""
🔔 Advanced Prediction Alerting System
📅 Generated: 2025-01-27
🎯 Purpose: Multi-channel alerting for predictive monitoring with intelligent rules
📋 Tracing ID: PREDICTION_ALERTING_001_20250127
"""

import logging
import time
import json
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class PredictionAlertType(Enum):
    """Types of prediction alerts"""
    THRESHOLD_BREACH = "threshold_breach"
    TREND_ANOMALY = "trend_anomaly"
    SEASONAL_ANOMALY = "seasonal_anomaly"
    CAPACITY_WARNING = "capacity_warning"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MODEL_DRIFT = "model_drift"
    PREDICTION_ERROR = "prediction_error"
    CONFIDENCE_LOW = "confidence_low"


class PredictionAlertSeverity(Enum):
    """Prediction alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PredictionAlertConfig:
    """Configuration for prediction alerting"""
    enabled_channels: List[str] = field(default_factory=lambda: ["console"])
    alert_cooldown: int = 300  # seconds
    max_alerts_per_hour: int = 10
    alert_grouping: bool = True
    alert_grouping_window: int = 60  # seconds
    enable_escalation: bool = True
    escalation_delay: int = 1800  # 30 minutes
    escalation_levels: int = 3
    enable_suppression: bool = True
    suppression_rules: Dict[str, Any] = field(default_factory=dict)
    custom_handlers: Dict[str, Callable] = field(default_factory=dict)
    threshold_rules: Dict[str, Dict[str, float]] = field(default_factory=dict)
    trend_rules: Dict[str, Dict[str, float]] = field(default_factory=dict)
    confidence_rules: Dict[str, float] = field(default_factory=dict)


@dataclass
class PredictionAlertMessage:
    """Prediction alert message structure"""
    id: str
    metric_name: str
    alert_type: str
    severity: str
    current_value: float
    predicted_value: float
    threshold: float
    confidence: float
    message: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    channel: str = "console"
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class PredictionAlertGroup:
    """Group of related prediction alerts"""
    group_id: str
    metric_name: str
    alert_type: str
    severity: str
    alerts: List[PredictionAlertMessage] = field(default_factory=list)
    first_alert_time: float = field(default_factory=time.time)
    last_alert_time: float = field(default_factory=time.time)
    alert_count: int = 0


class PredictionAlertChannelHandler:
    """Base class for prediction alert channel handlers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
    
    async def send_alert(self, alert: PredictionAlertMessage) -> bool:
        """Send prediction alert through this channel"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if channel is available"""
        return self.enabled


class EmailPredictionAlertHandler(PredictionAlertChannelHandler):
    """Email prediction alert handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_server = config.get('smtp_server', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.from_email = config.get('from_email', 'predictions@omni-keywords-finder.com')
        self.to_emails = config.get('to_emails', [])
        self.use_tls = config.get('use_tls', True)
    
    async def send_alert(self, alert: PredictionAlertMessage) -> bool:
        """Send email prediction alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"🔮 Prediction Alert: {alert.metric_name} - {alert.severity.upper()}"
            
            body = self._format_email_body(alert)
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email prediction alert sent for {alert.metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email prediction alert: {e}")
            return False
    
    def _format_email_body(self, alert: PredictionAlertMessage) -> str:
        """Format email body"""
        return f"""
        <html>
        <body>
            <h2>🔮 Prediction Alert</h2>
            <p><strong>Metric:</strong> {alert.metric_name}</p>
            <p><strong>Type:</strong> {alert.alert_type}</p>
            <p><strong>Severity:</strong> {alert.severity}</p>
            <p><strong>Current Value:</strong> {alert.current_value}</p>
            <p><strong>Predicted Value:</strong> {alert.predicted_value}</p>
            <p><strong>Threshold:</strong> {alert.threshold}</p>
            <p><strong>Confidence:</strong> {alert.confidence:.2f}%</p>
            <p><strong>Time:</strong> {datetime.fromtimestamp(alert.timestamp)}</p>
            <p><strong>Message:</strong> {alert.message}</p>
        </body>
        </html>
        """


class SlackPredictionAlertHandler(PredictionAlertChannelHandler):
    """Slack prediction alert handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url', '')
        self.channel = config.get('channel', '#predictions')
        self.username = config.get('username', 'Prediction Bot')
        self.icon_emoji = config.get('icon_emoji', ':crystal_ball:')
    
    async def send_alert(self, alert: PredictionAlertMessage) -> bool:
        """Send Slack prediction alert"""
        try:
            payload = {
                'channel': self.channel,
                'username': self.username,
                'icon_emoji': self.icon_emoji,
                'attachments': [{
                    'color': self._get_severity_color(alert.severity),
                    'title': f"🔮 Prediction Alert: {alert.metric_name}",
                    'fields': [
                        {'title': 'Type', 'value': alert.alert_type, 'short': True},
                        {'title': 'Severity', 'value': alert.severity, 'short': True},
                        {'title': 'Current Value', 'value': str(alert.current_value), 'short': True},
                        {'title': 'Predicted Value', 'value': str(alert.predicted_value), 'short': True},
                        {'title': 'Threshold', 'value': str(alert.threshold), 'short': True},
                        {'title': 'Confidence', 'value': f"{alert.confidence:.2f}%", 'short': True},
                        {'title': 'Message', 'value': alert.message, 'short': False}
                    ],
                    'footer': f"Alert ID: {alert.id}",
                    'ts': alert.timestamp
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Slack prediction alert sent for {alert.metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack prediction alert: {e}")
            return False
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors = {
            'info': '#36a64f',
            'warning': '#ffa500',
            'critical': '#ff0000',
            'emergency': '#8b0000'
        }
        return colors.get(severity.lower(), '#808080')


class WebhookPredictionAlertHandler(PredictionAlertChannelHandler):
    """Webhook prediction alert handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url', '')
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        self.timeout = config.get('timeout', 10)
    
    async def send_alert(self, alert: PredictionAlertMessage) -> bool:
        """Send webhook prediction alert"""
        try:
            payload = {
                'alert_id': alert.id,
                'metric_name': alert.metric_name,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'current_value': alert.current_value,
                'predicted_value': alert.predicted_value,
                'threshold': alert.threshold,
                'confidence': alert.confidence,
                'message': alert.message,
                'timestamp': alert.timestamp,
                'metadata': alert.metadata
            }
            
            response = requests.post(
                self.webhook_url, 
                json=payload, 
                headers=self.headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            logger.info(f"Webhook prediction alert sent for {alert.metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook prediction alert: {e}")
            return False


class ConsolePredictionAlertHandler(PredictionAlertChannelHandler):
    """Console prediction alert handler"""
    
    async def send_alert(self, alert: PredictionAlertMessage) -> bool:
        """Send console prediction alert"""
        try:
            print(f"\n🔮 PREDICTION ALERT 🔮")
            print(f"ID: {alert.id}")
            print(f"Metric: {alert.metric_name}")
            print(f"Type: {alert.alert_type}")
            print(f"Severity: {alert.severity}")
            print(f"Current Value: {alert.current_value}")
            print(f"Predicted Value: {alert.predicted_value}")
            print(f"Threshold: {alert.threshold}")
            print(f"Confidence: {alert.confidence:.2f}%")
            print(f"Message: {alert.message}")
            print(f"Time: {datetime.fromtimestamp(alert.timestamp)}")
            print("-" * 50)
            
            logger.info(f"Console prediction alert sent for {alert.metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send console prediction alert: {e}")
            return False


class PredictionAlerting:
    """
    Advanced prediction alerting system with multi-channel support
    """
    
    def __init__(self, config: PredictionAlertConfig):
        self.config = config
        self.channel_handlers = self._setup_channel_handlers()
        self.alert_history = deque(maxlen=1000)
        self.alert_groups = {}
        self.suppression_rules = config.suppression_rules
        self.threshold_rules = config.threshold_rules
        self.trend_rules = config.trend_rules
        self.confidence_rules = config.confidence_rules
        self.lock = threading.RLock()
        self.escalation_timers = {}
        
        # Alert statistics
        self.stats = {
            'total_alerts': 0,
            'sent_alerts': 0,
            'failed_alerts': 0,
            'suppressed_alerts': 0,
            'escalated_alerts': 0
        }
    
    def _setup_channel_handlers(self) -> Dict[str, PredictionAlertChannelHandler]:
        """Setup channel handlers"""
        handlers = {}
        
        # Email handler
        if "email" in self.config.enabled_channels:
            email_config = {
                'enabled': True,
                'smtp_server': 'localhost',
                'smtp_port': 587,
                'use_tls': True
            }
            handlers["email"] = EmailPredictionAlertHandler(email_config)
        
        # Slack handler
        if "slack" in self.config.enabled_channels:
            slack_config = {
                'enabled': True,
                'webhook_url': '',
                'channel': '#predictions'
            }
            handlers["slack"] = SlackPredictionAlertHandler(slack_config)
        
        # Webhook handler
        if "webhook" in self.config.enabled_channels:
            webhook_config = {
                'enabled': True,
                'webhook_url': ''
            }
            handlers["webhook"] = WebhookPredictionAlertHandler(webhook_config)
        
        # Console handler (always available)
        handlers["console"] = ConsolePredictionAlertHandler({'enabled': True})
        
        return handlers
    
    def send_prediction_alert(self, metric_name: str, alert_type: str, severity: str,
                            current_value: float, predicted_value: float, threshold: float,
                            confidence: float, message: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send prediction alert"""
        alert_id = f"prediction_alert_{int(time.time() * 1000)}_{hash(metric_name)}"
        
        alert = PredictionAlertMessage(
            id=alert_id,
            metric_name=metric_name,
            alert_type=alert_type,
            severity=severity,
            current_value=current_value,
            predicted_value=predicted_value,
            threshold=threshold,
            confidence=confidence,
            message=message,
            timestamp=time.time(),
            metadata=metadata or {},
            priority=self._determine_priority(severity)
        )
        
        with self.lock:
            # Check suppression
            if self._should_suppress_alert(alert):
                self.stats['suppressed_alerts'] += 1
                logger.info(f"Prediction alert suppressed for {metric_name}")
                return alert_id
            
            # Check cooldown
            if self._is_in_cooldown(alert):
                logger.info(f"Prediction alert in cooldown for {metric_name}")
                return alert_id
            
            # Group alerts if enabled
            if self.config.alert_grouping:
                self._group_alert(alert)
            else:
                self._send_individual_alert(alert)
            
            # Update statistics
            self.stats['total_alerts'] += 1
            self.alert_history.append(alert)
        
        return alert_id
    
    def check_threshold_breach(self, metric_name: str, current_value: float, 
                              predicted_value: float, threshold: float) -> bool:
        """Check if threshold breach should trigger alert"""
        if metric_name in self.threshold_rules:
            rule = self.threshold_rules[metric_name]
            breach_threshold = rule.get('breach_threshold', threshold)
            return abs(predicted_value - current_value) > breach_threshold
        return abs(predicted_value - current_value) > threshold
    
    def check_trend_anomaly(self, metric_name: str, trend_direction: str, 
                           trend_strength: float) -> bool:
        """Check if trend anomaly should trigger alert"""
        if metric_name in self.trend_rules:
            rule = self.trend_rules[metric_name]
            min_strength = rule.get('min_strength', 0.7)
            return trend_strength > min_strength
        return trend_strength > 0.8
    
    def check_confidence_alert(self, metric_name: str, confidence: float) -> bool:
        """Check if low confidence should trigger alert"""
        if metric_name in self.confidence_rules:
            min_confidence = self.confidence_rules[metric_name]
            return confidence < min_confidence
        return confidence < 0.7
    
    def _should_suppress_alert(self, alert: PredictionAlertMessage) -> bool:
        """Check if alert should be suppressed"""
        for rule in self.suppression_rules.values():
            if self._matches_suppression_rule(alert, rule):
                return True
        return False
    
    def _matches_suppression_rule(self, alert: PredictionAlertMessage, rule: Dict[str, Any]) -> bool:
        """Check if alert matches suppression rule"""
        # Check metric name
        if 'metric_name' in rule and alert.metric_name != rule['metric_name']:
            return False
        
        # Check alert type
        if 'alert_type' in rule and alert.alert_type != rule['alert_type']:
            return False
        
        # Check severity
        if 'severity' in rule and alert.severity != rule['severity']:
            return False
        
        # Check time window
        if 'time_window' in rule:
            window_start = time.time() - rule['time_window']
            if alert.timestamp < window_start:
                return False
        
        return True
    
    def _is_in_cooldown(self, alert: PredictionAlertMessage) -> bool:
        """Check if alert is in cooldown period"""
        cooldown_key = f"{alert.metric_name}_{alert.alert_type}"
        
        # Check if we have a recent alert for this metric/type
        for recent_alert in reversed(list(self.alert_history)):
            if (recent_alert.metric_name == alert.metric_name and 
                recent_alert.alert_type == alert.alert_type):
                time_diff = alert.timestamp - recent_alert.timestamp
                if time_diff < self.config.alert_cooldown:
                    return True
        
        return False
    
    def _group_alert(self, alert: PredictionAlertMessage):
        """Group related prediction alerts"""
        group_key = f"{alert.metric_name}_{alert.alert_type}_{alert.severity}"
        
        if group_key not in self.alert_groups:
            self.alert_groups[group_key] = PredictionAlertGroup(
                group_id=group_key,
                metric_name=alert.metric_name,
                alert_type=alert.alert_type,
                severity=alert.severity
            )
        
        group = self.alert_groups[group_key]
        group.alerts.append(alert)
        group.last_alert_time = alert.timestamp
        group.alert_count += 1
        
        # Send grouped alert if window expired or count threshold reached
        if (alert.timestamp - group.first_alert_time > self.config.alert_grouping_window or
            group.alert_count >= 5):
            self._send_grouped_alert(group)
            # Reset group
            del self.alert_groups[group_key]
    
    def _send_grouped_alert(self, group: PredictionAlertGroup):
        """Send grouped prediction alert"""
        alert = group.alerts[-1]  # Use the latest alert as template
        alert.message = f"Multiple prediction alerts: {group.alert_count} alerts in {self.config.alert_grouping_window}s"
        alert.metadata['group_count'] = group.alert_count
        alert.metadata['group_duration'] = group.last_alert_time - group.first_alert_time
        
        self._send_individual_alert(alert)
    
    def _send_individual_alert(self, alert: PredictionAlertMessage):
        """Send individual prediction alert through all channels"""
        for channel, handler in self.channel_handlers.items():
            if handler.is_available():
                try:
                    # Run in thread pool for async support
                    loop = asyncio.get_event_loop()
                    success = loop.run_until_complete(handler.send_alert(alert))
                    
                    if success:
                        self.stats['sent_alerts'] += 1
                    else:
                        self.stats['failed_alerts'] += 1
                        alert.retry_count += 1
                        
                        # Retry logic
                        if alert.retry_count < alert.max_retries:
                            asyncio.create_task(self._retry_alert(alert, channel))
                            
                except Exception as e:
                    logger.error(f"Failed to send prediction alert through {channel}: {e}")
                    self.stats['failed_alerts'] += 1
    
    async def _retry_alert(self, alert: PredictionAlertMessage, channel: str):
        """Retry sending prediction alert"""
        await asyncio.sleep(2 ** alert.retry_count)  # Exponential backoff
        
        handler = self.channel_handlers.get(channel)
        if handler and handler.is_available():
            try:
                success = await handler.send_alert(alert)
                if success:
                    self.stats['sent_alerts'] += 1
                else:
                    self.stats['failed_alerts'] += 1
            except Exception as e:
                logger.error(f"Retry failed for prediction alert {alert.id}: {e}")
                self.stats['failed_alerts'] += 1
    
    def _determine_priority(self, severity: str) -> str:
        """Determine alert priority from severity"""
        priority_map = {
            'info': 'low',
            'warning': 'medium',
            'critical': 'high',
            'emergency': 'critical'
        }
        return priority_map.get(severity.lower(), 'medium')
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get prediction alert statistics"""
        with self.lock:
            return {
                'total_alerts': self.stats['total_alerts'],
                'sent_alerts': self.stats['sent_alerts'],
                'failed_alerts': self.stats['failed_alerts'],
                'suppressed_alerts': self.stats['suppressed_alerts'],
                'escalated_alerts': self.stats['escalated_alerts'],
                'success_rate': (self.stats['sent_alerts'] / max(self.stats['total_alerts'], 1)) * 100,
                'active_groups': len(self.alert_groups),
                'alert_history_size': len(self.alert_history)
            }
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent prediction alerts"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            recent_alerts = [
                {
                    'id': alert.id,
                    'metric_name': alert.metric_name,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'current_value': alert.current_value,
                    'predicted_value': alert.predicted_value,
                    'threshold': alert.threshold,
                    'confidence': alert.confidence,
                    'message': alert.message,
                    'timestamp': alert.timestamp,
                    'priority': alert.priority
                }
                for alert in self.alert_history
                if alert.timestamp >= cutoff_time
            ]
        
        return recent_alerts
    
    def add_suppression_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Add suppression rule"""
        with self.lock:
            self.suppression_rules[rule_name] = rule_config
    
    def remove_suppression_rule(self, rule_name: str):
        """Remove suppression rule"""
        with self.lock:
            self.suppression_rules.pop(rule_name, None)
    
    def add_threshold_rule(self, metric_name: str, rule_config: Dict[str, float]):
        """Add threshold rule for metric"""
        with self.lock:
            self.threshold_rules[metric_name] = rule_config
    
    def add_trend_rule(self, metric_name: str, rule_config: Dict[str, float]):
        """Add trend rule for metric"""
        with self.lock:
            self.trend_rules[metric_name] = rule_config
    
    def add_confidence_rule(self, metric_name: str, min_confidence: float):
        """Add confidence rule for metric"""
        with self.lock:
            self.confidence_rules[metric_name] = min_confidence
    
    def clear_alert_history(self):
        """Clear alert history"""
        with self.lock:
            self.alert_history.clear()
            self.alert_groups.clear()


# Global instance
_prediction_alerting_instance: Optional[PredictionAlerting] = None


def get_prediction_alerting(config: Optional[PredictionAlertConfig] = None) -> PredictionAlerting:
    """Get global prediction alerting instance"""
    global _prediction_alerting_instance
    
    if _prediction_alerting_instance is None:
        if config is None:
            config = PredictionAlertConfig()
        _prediction_alerting_instance = PredictionAlerting(config)
    
    return _prediction_alerting_instance


def send_prediction_alert(metric_name: str, alert_type: str, severity: str,
                         current_value: float, predicted_value: float, threshold: float,
                         confidence: float, message: str, metadata: Optional[Dict[str, Any]] = None,
                         config: Optional[PredictionAlertConfig] = None) -> str:
    """Send prediction alert"""
    alerting = get_prediction_alerting(config)
    return alerting.send_prediction_alert(metric_name, alert_type, severity, current_value, 
                                        predicted_value, threshold, confidence, message, metadata)


def get_prediction_alert_statistics(config: Optional[PredictionAlertConfig] = None) -> Dict[str, Any]:
    """Get prediction alert statistics"""
    alerting = get_prediction_alerting(config)
    return alerting.get_alert_statistics()


def get_recent_prediction_alerts(hours: int = 24, config: Optional[PredictionAlertConfig] = None) -> List[Dict[str, Any]]:
    """Get recent prediction alerts"""
    alerting = get_prediction_alerting(config)
    return alerting.get_recent_alerts(hours)


def check_threshold_breach(metric_name: str, current_value: float, predicted_value: float, 
                          threshold: float, config: Optional[PredictionAlertConfig] = None) -> bool:
    """Check if threshold breach should trigger alert"""
    alerting = get_prediction_alerting(config)
    return alerting.check_threshold_breach(metric_name, current_value, predicted_value, threshold)


def check_trend_anomaly(metric_name: str, trend_direction: str, trend_strength: float,
                       config: Optional[PredictionAlertConfig] = None) -> bool:
    """Check if trend anomaly should trigger alert"""
    alerting = get_prediction_alerting(config)
    return alerting.check_trend_anomaly(metric_name, trend_direction, trend_strength)


def check_confidence_alert(metric_name: str, confidence: float,
                          config: Optional[PredictionAlertConfig] = None) -> bool:
    """Check if low confidence should trigger alert"""
    alerting = get_prediction_alerting(config)
    return alerting.check_confidence_alert(metric_name, confidence) 