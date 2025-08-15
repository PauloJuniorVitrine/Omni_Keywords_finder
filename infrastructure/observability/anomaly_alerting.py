"""
🔔 Advanced Anomaly Alerting System
📅 Generated: 2025-01-27
🎯 Purpose: Multi-channel anomaly alerting with intelligent routing
📋 Tracing ID: ANOMALY_ALERTING_001_20250127
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


class AlertChannel(Enum):
    """Supported alert channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    CONSOLE = "console"
    LOG = "log"


class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class AlertConfig:
    """Configuration for anomaly alerting"""
    enabled_channels: List[AlertChannel] = field(default_factory=lambda: [AlertChannel.CONSOLE])
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


@dataclass
class AlertMessage:
    """Alert message structure"""
    id: str
    metric_name: str
    anomaly_type: str
    severity: str
    value: float
    threshold: float
    message: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: AlertPriority = AlertPriority.MEDIUM
    channel: AlertChannel = AlertChannel.CONSOLE
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class AlertGroup:
    """Group of related alerts"""
    group_id: str
    metric_name: str
    anomaly_type: str
    severity: str
    alerts: List[AlertMessage] = field(default_factory=list)
    first_alert_time: float = field(default_factory=time.time)
    last_alert_time: float = field(default_factory=time.time)
    alert_count: int = 0


class AlertChannelHandler:
    """Base class for alert channel handlers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
    
    async def send_alert(self, alert: AlertMessage) -> bool:
        """Send alert through this channel"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if channel is available"""
        return self.enabled


class EmailAlertHandler(AlertChannelHandler):
    """Email alert handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_server = config.get('smtp_server', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.from_email = config.get('from_email', 'alerts@omni-keywords-finder.com')
        self.to_emails = config.get('to_emails', [])
        self.use_tls = config.get('use_tls', True)
    
    async def send_alert(self, alert: AlertMessage) -> bool:
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"🚨 Anomaly Alert: {alert.metric_name} - {alert.severity.upper()}"
            
            body = self._format_email_body(alert)
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent for {alert.metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _format_email_body(self, alert: AlertMessage) -> str:
        """Format email body"""
        return f"""
        <html>
        <body>
            <h2>🚨 Anomaly Alert</h2>
            <p><strong>Metric:</strong> {alert.metric_name}</p>
            <p><strong>Type:</strong> {alert.anomaly_type}</p>
            <p><strong>Severity:</strong> {alert.severity}</p>
            <p><strong>Value:</strong> {alert.value}</p>
            <p><strong>Threshold:</strong> {alert.threshold}</p>
            <p><strong>Time:</strong> {datetime.fromtimestamp(alert.timestamp)}</p>
            <p><strong>Message:</strong> {alert.message}</p>
        </body>
        </html>
        """


class SlackAlertHandler(AlertChannelHandler):
    """Slack alert handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url', '')
        self.channel = config.get('channel', '#alerts')
        self.username = config.get('username', 'Anomaly Bot')
        self.icon_emoji = config.get('icon_emoji', ':warning:')
    
    async def send_alert(self, alert: AlertMessage) -> bool:
        """Send Slack alert"""
        try:
            payload = {
                'channel': self.channel,
                'username': self.username,
                'icon_emoji': self.icon_emoji,
                'attachments': [{
                    'color': self._get_severity_color(alert.severity),
                    'title': f"🚨 Anomaly Alert: {alert.metric_name}",
                    'fields': [
                        {'title': 'Type', 'value': alert.anomaly_type, 'short': True},
                        {'title': 'Severity', 'value': alert.severity, 'short': True},
                        {'title': 'Value', 'value': str(alert.value), 'short': True},
                        {'title': 'Threshold', 'value': str(alert.threshold), 'short': True},
                        {'title': 'Message', 'value': alert.message, 'short': False}
                    ],
                    'footer': f"Alert ID: {alert.id}",
                    'ts': alert.timestamp
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Slack alert sent for {alert.metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors = {
            'low': '#36a64f',
            'medium': '#ffa500',
            'high': '#ff0000',
            'critical': '#8b0000',
            'emergency': '#ff00ff'
        }
        return colors.get(severity.lower(), '#808080')


class WebhookAlertHandler(AlertChannelHandler):
    """Webhook alert handler"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url', '')
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        self.timeout = config.get('timeout', 10)
    
    async def send_alert(self, alert: AlertMessage) -> bool:
        """Send webhook alert"""
        try:
            payload = {
                'alert_id': alert.id,
                'metric_name': alert.metric_name,
                'anomaly_type': alert.anomaly_type,
                'severity': alert.severity,
                'value': alert.value,
                'threshold': alert.threshold,
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
            
            logger.info(f"Webhook alert sent for {alert.metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False


class ConsoleAlertHandler(AlertChannelHandler):
    """Console alert handler"""
    
    async def send_alert(self, alert: AlertMessage) -> bool:
        """Send console alert"""
        try:
            print(f"\n🚨 ANOMALY ALERT 🚨")
            print(f"ID: {alert.id}")
            print(f"Metric: {alert.metric_name}")
            print(f"Type: {alert.anomaly_type}")
            print(f"Severity: {alert.severity}")
            print(f"Value: {alert.value}")
            print(f"Threshold: {alert.threshold}")
            print(f"Message: {alert.message}")
            print(f"Time: {datetime.fromtimestamp(alert.timestamp)}")
            print("-" * 50)
            
            logger.info(f"Console alert sent for {alert.metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send console alert: {e}")
            return False


class AnomalyAlerting:
    """
    Advanced anomaly alerting system with multi-channel support
    """
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.channel_handlers = self._setup_channel_handlers()
        self.alert_history = deque(maxlen=1000)
        self.alert_groups = {}
        self.suppression_rules = config.suppression_rules
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
    
    def _setup_channel_handlers(self) -> Dict[AlertChannel, AlertChannelHandler]:
        """Setup channel handlers"""
        handlers = {}
        
        # Email handler
        if AlertChannel.EMAIL in self.config.enabled_channels:
            email_config = {
                'enabled': True,
                'smtp_server': 'localhost',
                'smtp_port': 587,
                'use_tls': True
            }
            handlers[AlertChannel.EMAIL] = EmailAlertHandler(email_config)
        
        # Slack handler
        if AlertChannel.SLACK in self.config.enabled_channels:
            slack_config = {
                'enabled': True,
                'webhook_url': '',
                'channel': '#alerts'
            }
            handlers[AlertChannel.SLACK] = SlackAlertHandler(slack_config)
        
        # Webhook handler
        if AlertChannel.WEBHOOK in self.config.enabled_channels:
            webhook_config = {
                'enabled': True,
                'webhook_url': ''
            }
            handlers[AlertChannel.WEBHOOK] = WebhookAlertHandler(webhook_config)
        
        # Console handler (always available)
        handlers[AlertChannel.CONSOLE] = ConsoleAlertHandler({'enabled': True})
        
        return handlers
    
    def send_alert(self, metric_name: str, anomaly_type: str, severity: str, 
                  value: float, threshold: float, message: str, 
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """Send anomaly alert"""
        alert_id = f"alert_{int(time.time() * 1000)}_{hash(metric_name)}"
        
        alert = AlertMessage(
            id=alert_id,
            metric_name=metric_name,
            anomaly_type=anomaly_type,
            severity=severity,
            value=value,
            threshold=threshold,
            message=message,
            timestamp=time.time(),
            metadata=metadata or {},
            priority=self._determine_priority(severity)
        )
        
        with self.lock:
            # Check suppression
            if self._should_suppress_alert(alert):
                self.stats['suppressed_alerts'] += 1
                logger.info(f"Alert suppressed for {metric_name}")
                return alert_id
            
            # Check cooldown
            if self._is_in_cooldown(alert):
                logger.info(f"Alert in cooldown for {metric_name}")
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
    
    def _should_suppress_alert(self, alert: AlertMessage) -> bool:
        """Check if alert should be suppressed"""
        for rule in self.suppression_rules.values():
            if self._matches_suppression_rule(alert, rule):
                return True
        return False
    
    def _matches_suppression_rule(self, alert: AlertMessage, rule: Dict[str, Any]) -> bool:
        """Check if alert matches suppression rule"""
        # Check metric name
        if 'metric_name' in rule and alert.metric_name != rule['metric_name']:
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
    
    def _is_in_cooldown(self, alert: AlertMessage) -> bool:
        """Check if alert is in cooldown period"""
        cooldown_key = f"{alert.metric_name}_{alert.anomaly_type}"
        
        # Check if we have a recent alert for this metric/type
        for recent_alert in reversed(list(self.alert_history)):
            if (recent_alert.metric_name == alert.metric_name and 
                recent_alert.anomaly_type == alert.anomaly_type):
                time_diff = alert.timestamp - recent_alert.timestamp
                if time_diff < self.config.alert_cooldown:
                    return True
        
        return False
    
    def _group_alert(self, alert: AlertMessage):
        """Group related alerts"""
        group_key = f"{alert.metric_name}_{alert.anomaly_type}_{alert.severity}"
        
        if group_key not in self.alert_groups:
            self.alert_groups[group_key] = AlertGroup(
                group_id=group_key,
                metric_name=alert.metric_name,
                anomaly_type=alert.anomaly_type,
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
    
    def _send_grouped_alert(self, group: AlertGroup):
        """Send grouped alert"""
        alert = group.alerts[-1]  # Use the latest alert as template
        alert.message = f"Multiple anomalies detected: {group.alert_count} alerts in {self.config.alert_grouping_window}s"
        alert.metadata['group_count'] = group.alert_count
        alert.metadata['group_duration'] = group.last_alert_time - group.first_alert_time
        
        self._send_individual_alert(alert)
    
    def _send_individual_alert(self, alert: AlertMessage):
        """Send individual alert through all channels"""
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
                    logger.error(f"Failed to send alert through {channel}: {e}")
                    self.stats['failed_alerts'] += 1
    
    async def _retry_alert(self, alert: AlertMessage, channel: AlertChannel):
        """Retry sending alert"""
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
                logger.error(f"Retry failed for alert {alert.id}: {e}")
                self.stats['failed_alerts'] += 1
    
    def _determine_priority(self, severity: str) -> AlertPriority:
        """Determine alert priority from severity"""
        priority_map = {
            'low': AlertPriority.LOW,
            'medium': AlertPriority.MEDIUM,
            'high': AlertPriority.HIGH,
            'critical': AlertPriority.CRITICAL,
            'emergency': AlertPriority.EMERGENCY
        }
        return priority_map.get(severity.lower(), AlertPriority.MEDIUM)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
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
        """Get recent alerts"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            recent_alerts = [
                {
                    'id': alert.id,
                    'metric_name': alert.metric_name,
                    'anomaly_type': alert.anomaly_type,
                    'severity': alert.severity,
                    'value': alert.value,
                    'threshold': alert.threshold,
                    'message': alert.message,
                    'timestamp': alert.timestamp,
                    'priority': alert.priority.value
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
    
    def clear_alert_history(self):
        """Clear alert history"""
        with self.lock:
            self.alert_history.clear()
            self.alert_groups.clear()


# Global instance
_alerting_instance: Optional[AnomalyAlerting] = None


def get_anomaly_alerting(config: Optional[AlertConfig] = None) -> AnomalyAlerting:
    """Get global anomaly alerting instance"""
    global _alerting_instance
    
    if _alerting_instance is None:
        if config is None:
            config = AlertConfig()
        _alerting_instance = AnomalyAlerting(config)
    
    return _alerting_instance


def send_anomaly_alert(metric_name: str, anomaly_type: str, severity: str,
                      value: float, threshold: float, message: str,
                      metadata: Optional[Dict[str, Any]] = None,
                      config: Optional[AlertConfig] = None) -> str:
    """Send anomaly alert"""
    alerting = get_anomaly_alerting(config)
    return alerting.send_alert(metric_name, anomaly_type, severity, value, threshold, message, metadata)


def get_alert_statistics(config: Optional[AlertConfig] = None) -> Dict[str, Any]:
    """Get alert statistics"""
    alerting = get_anomaly_alerting(config)
    return alerting.get_alert_statistics()


def get_recent_alerts(hours: int = 24, config: Optional[AlertConfig] = None) -> List[Dict[str, Any]]:
    """Get recent alerts"""
    alerting = get_anomaly_alerting(config)
    return alerting.get_recent_alerts(hours) 