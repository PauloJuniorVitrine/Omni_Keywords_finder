"""
🚨 Sistema de Alertas Inteligentes - Omni Keywords Finder
🔔 Alertas baseados em predições, thresholds dinâmicos e notificações
🔄 Versão: 1.0
📅 Data: 2024-12-19
👤 Autor: Paulo Júnior
🔗 Tracing ID: PREDICTION_20241219_003
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import asyncio
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Observability
from infrastructure.observability.telemetry import TelemetryManager
from infrastructure.observability.tracing import TracingManager
from infrastructure.observability.metrics import MetricsManager

# Notifications
try:
    from infrastructure.notifications.avancado.notification_manager import NotificationManager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Níveis de severidade de alerta"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(Enum):
    """Tipos de alerta"""
    TREND_CHANGE = "trend_change"
    THRESHOLD_BREACH = "threshold_breach"
    ANOMALY_DETECTED = "anomaly_detected"
    PREDICTION_ALERT = "prediction_alert"
    VOLATILITY_SPIKE = "volatility_spike"
    SEASONALITY_CHANGE = "seasonality_change"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class AlertStatus(Enum):
    """Status do alerta"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """Regra de alerta"""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    conditions: Dict[str, Any]
    actions: List[str]
    enabled: bool = True
    cooldown_minutes: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alerta gerado"""
    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    keyword: str
    current_value: float
    threshold_value: float
    confidence: float
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertNotification:
    """Notificação de alerta"""
    alert_id: str
    channel: str
    message: str
    recipients: List[str]
    sent_at: datetime
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)


class AlertSystem:
    """
    🚨 Sistema Inteligente de Alertas
    
    Características:
    - Alertas baseados em predições e thresholds dinâmicos
    - Múltiplos canais de notificação
    - Sistema de cooldown e supressão
    - Integração com observabilidade
    - Dashboard de alertas em tempo real
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o sistema de alertas
        
        Args:
            config: Configurações do sistema
        """
        self.config = config or self._default_config()
        self.telemetry = TelemetryManager()
        self.tracing = TracingManager()
        self.metrics = MetricsManager()
        
        # Sistema de notificações
        self.notification_manager = None
        if NOTIFICATIONS_AVAILABLE:
            self.notification_manager = NotificationManager()
        
        # Estado do sistema
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        self.alert_history: List[Alert] = []
        self.notifications: List[AlertNotification] = []
        
        # Cache e controle
        self.alert_cache = {}
        self.suppression_rules = {}
        self.cooldown_timestamps = {}
        
        # Carrega regras padrão
        self._load_default_rules()
        
        logger.info(f"🚨 AlertSystem inicializado com {len(self.alert_rules)} regras")
    
    def _default_config(self) -> Dict:
        """Configuração padrão"""
        return {
            'alert_retention_days': 90,
            'max_active_alerts': 1000,
            'notification_channels': ['email', 'slack', 'websocket'],
            'default_cooldown_minutes': 30,
            'thresholds': {
                'trend_change': {
                    'critical': 0.5,   # 50% de mudança
                    'high': 0.3,       # 30% de mudança
                    'medium': 0.15,    # 15% de mudança
                    'low': 0.05        # 5% de mudança
                },
                'volatility': {
                    'critical': 2.0,   # 2x desvio padrão
                    'high': 1.5,
                    'medium': 1.0,
                    'low': 0.5
                },
                'confidence': {
                    'critical': 0.9,
                    'high': 0.8,
                    'medium': 0.6,
                    'low': 0.4
                }
            },
            'email_config': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_email': 'alerts@omnikeywords.com'
            },
            'slack_config': {
                'webhook_url': '',
                'channel': '#alerts'
            }
        }
    
    def _load_default_rules(self):
        """Carrega regras de alerta padrão"""
        default_rules = [
            AlertRule(
                name="Trend Change Critical",
                alert_type=AlertType.TREND_CHANGE,
                severity=AlertSeverity.CRITICAL,
                conditions={
                    'change_percentage': 0.5,
                    'confidence_min': 0.8,
                    'timeframe': '7d'
                },
                actions=['email', 'slack', 'websocket'],
                cooldown_minutes=60
            ),
            AlertRule(
                name="Threshold Breach High",
                alert_type=AlertType.THRESHOLD_BREACH,
                severity=AlertSeverity.HIGH,
                conditions={
                    'threshold_type': 'absolute',
                    'threshold_value': 1000,
                    'direction': 'above'
                },
                actions=['email', 'slack'],
                cooldown_minutes=30
            ),
            AlertRule(
                name="Anomaly Detected",
                alert_type=AlertType.ANOMALY_DETECTED,
                severity=AlertSeverity.MEDIUM,
                conditions={
                    'anomaly_score_threshold': 2.0,
                    'confidence_min': 0.6
                },
                actions=['email'],
                cooldown_minutes=15
            ),
            AlertRule(
                name="Volatility Spike",
                alert_type=AlertType.VOLATILITY_SPIKE,
                severity=AlertSeverity.HIGH,
                conditions={
                    'volatility_threshold': 1.5,
                    'timeframe': '24h'
                },
                actions=['slack'],
                cooldown_minutes=30
            )
        ]
        
        self.alert_rules.extend(default_rules)
    
    def add_alert_rule(self, rule: AlertRule):
        """
        Adiciona nova regra de alerta
        
        Args:
            rule: Regra de alerta
        """
        with self.tracing.start_span("add_alert_rule"):
            try:
                # Validação
                if not rule.name or not rule.conditions:
                    raise ValueError("Regra deve ter nome e condições")
                
                # Verifica se já existe
                existing_rule = next((r for r in self.alert_rules if r.name == rule.name), None)
                if existing_rule:
                    logger.warning(f"⚠️ Regra {rule.name} já existe. Atualizando...")
                    self.alert_rules.remove(existing_rule)
                
                self.alert_rules.append(rule)
                
                self.metrics.increment_counter("alert_rule_added")
                logger.info(f"✅ Regra de alerta adicionada: {rule.name}")
                
            except Exception as e:
                self.metrics.increment_counter("alert_rule_error")
                logger.error(f"❌ Erro ao adicionar regra: {e}")
    
    def remove_alert_rule(self, rule_name: str):
        """
        Remove regra de alerta
        
        Args:
            rule_name: Nome da regra
        """
        with self.tracing.start_span("remove_alert_rule"):
            try:
                rule = next((r for r in self.alert_rules if r.name == rule_name), None)
                if rule:
                    self.alert_rules.remove(rule)
                    self.metrics.increment_counter("alert_rule_removed")
                    logger.info(f"✅ Regra removida: {rule_name}")
                else:
                    logger.warning(f"⚠️ Regra não encontrada: {rule_name}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao remover regra: {e}")
    
    def evaluate_predictions(self, predictions: List[Dict]) -> List[Alert]:
        """
        Avalia predições e gera alertas
        
        Args:
            predictions: Lista de predições
            
        Returns:
            Lista de alertas gerados
        """
        with self.tracing.start_span("evaluate_predictions"):
            try:
                generated_alerts = []
                
                for pred in predictions:
                    # Verifica cooldown
                    if self._is_in_cooldown(pred.get('keyword', '')):
                        continue
                    
                    # Avalia cada regra
                    for rule in self.alert_rules:
                        if not rule.enabled:
                            continue
                        
                        alert = self._evaluate_rule(rule, pred)
                        if alert:
                            generated_alerts.append(alert)
                
                # Adiciona alertas ao sistema
                self.alerts.extend(generated_alerts)
                
                # Limita número de alertas ativos
                self._cleanup_old_alerts()
                
                # Envia notificações
                if generated_alerts:
                    asyncio.create_task(self._send_notifications(generated_alerts))
                
                self.metrics.increment_counter("alerts_generated", len(generated_alerts))
                logger.info(f"✅ {len(generated_alerts)} alertas gerados")
                
                return generated_alerts
                
            except Exception as e:
                self.metrics.increment_counter("alert_evaluation_error")
                logger.error(f"❌ Erro na avaliação de predições: {e}")
                return []
    
    def _evaluate_rule(self, rule: AlertRule, prediction: Dict) -> Optional[Alert]:
        """Avalia uma regra contra uma predição"""
        try:
            conditions = rule.conditions
            
            if rule.alert_type == AlertType.TREND_CHANGE:
                return self._evaluate_trend_change(rule, prediction)
            elif rule.alert_type == AlertType.THRESHOLD_BREACH:
                return self._evaluate_threshold_breach(rule, prediction)
            elif rule.alert_type == AlertType.ANOMALY_DETECTED:
                return self._evaluate_anomaly(rule, prediction)
            elif rule.alert_type == AlertType.VOLATILITY_SPIKE:
                return self._evaluate_volatility(rule, prediction)
            else:
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Erro na avaliação da regra {rule.name}: {e}")
            return None
    
    def _evaluate_trend_change(self, rule: AlertRule, prediction: Dict) -> Optional[Alert]:
        """Avalia mudança de tendência"""
        try:
            conditions = rule.conditions
            current_value = prediction.get('current_value', 0)
            predicted_value = prediction.get('predicted_value', 0)
            confidence = prediction.get('confidence', 0)
            
            if current_value <= 0:
                return None
            
            change_percentage = abs(predicted_value - current_value) / current_value
            threshold = conditions.get('change_percentage', 0.1)
            confidence_min = conditions.get('confidence_min', 0.5)
            
            if change_percentage >= threshold and confidence >= confidence_min:
                direction = "up" if predicted_value > current_value else "down"
                message = f"Tendência crítica detectada: {direction} {change_percentage:.1%} em {prediction.get('timeframe', '30d')}"
                
                return Alert(
                    id=self._generate_alert_id(),
                    rule_name=rule.name,
                    alert_type=rule.alert_type,
                    severity=rule.severity,
                    message=message,
                    keyword=prediction.get('keyword', ''),
                    current_value=current_value,
                    threshold_value=threshold,
                    confidence=confidence,
                    timestamp=datetime.now(),
                    metadata={
                        'change_percentage': change_percentage,
                        'direction': direction,
                        'predicted_value': predicted_value
                    }
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na avaliação de tendência: {e}")
            return None
    
    def _evaluate_threshold_breach(self, rule: AlertRule, prediction: Dict) -> Optional[Alert]:
        """Avalia violação de threshold"""
        try:
            conditions = rule.conditions
            current_value = prediction.get('current_value', 0)
            threshold_value = conditions.get('threshold_value', 0)
            threshold_type = conditions.get('threshold_type', 'absolute')
            direction = conditions.get('direction', 'above')
            
            # Calcula threshold se for relativo
            if threshold_type == 'relative':
                historical_avg = prediction.get('metadata', {}).get('historical_average', 0)
                threshold_value = historical_avg * threshold_value
            
            # Verifica violação
            breached = False
            if direction == 'above' and current_value > threshold_value:
                breached = True
            elif direction == 'below' and current_value < threshold_value:
                breached = True
            
            if breached:
                message = f"Threshold violado: {current_value:.2f} {direction} {threshold_value:.2f}"
                
                return Alert(
                    id=self._generate_alert_id(),
                    rule_name=rule.name,
                    alert_type=rule.alert_type,
                    severity=rule.severity,
                    message=message,
                    keyword=prediction.get('keyword', ''),
                    current_value=current_value,
                    threshold_value=threshold_value,
                    confidence=prediction.get('confidence', 0),
                    timestamp=datetime.now(),
                    metadata={
                        'threshold_type': threshold_type,
                        'direction': direction
                    }
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na avaliação de threshold: {e}")
            return None
    
    def _evaluate_anomaly(self, rule: AlertRule, prediction: Dict) -> Optional[Alert]:
        """Avalia detecção de anomalia"""
        try:
            conditions = rule.conditions
            anomaly_score = prediction.get('metadata', {}).get('anomaly_score', 0)
            confidence = prediction.get('confidence', 0)
            
            score_threshold = conditions.get('anomaly_score_threshold', 2.0)
            confidence_min = conditions.get('confidence_min', 0.5)
            
            if anomaly_score >= score_threshold and confidence >= confidence_min:
                message = f"Anomalia detectada: score {anomaly_score:.2f} (threshold: {score_threshold})"
                
                return Alert(
                    id=self._generate_alert_id(),
                    rule_name=rule.name,
                    alert_type=rule.alert_type,
                    severity=rule.severity,
                    message=message,
                    keyword=prediction.get('keyword', ''),
                    current_value=prediction.get('current_value', 0),
                    threshold_value=score_threshold,
                    confidence=confidence,
                    timestamp=datetime.now(),
                    metadata={
                        'anomaly_score': anomaly_score,
                        'score_threshold': score_threshold
                    }
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na avaliação de anomalia: {e}")
            return None
    
    def _evaluate_volatility(self, rule: AlertRule, prediction: Dict) -> Optional[Alert]:
        """Avalia spike de volatilidade"""
        try:
            conditions = rule.conditions
            volatility = prediction.get('metadata', {}).get('volatility', 0)
            historical_volatility = prediction.get('metadata', {}).get('historical_volatility', 1)
            
            if historical_volatility > 0:
                volatility_ratio = volatility / historical_volatility
                threshold = conditions.get('volatility_threshold', 1.5)
                
                if volatility_ratio >= threshold:
                    message = f"Spike de volatilidade: {volatility_ratio:.2f}value normal"
                    
                    return Alert(
                        id=self._generate_alert_id(),
                        rule_name=rule.name,
                        alert_type=rule.alert_type,
                        severity=rule.severity,
                        message=message,
                        keyword=prediction.get('keyword', ''),
                        current_value=prediction.get('current_value', 0),
                        threshold_value=threshold,
                        confidence=prediction.get('confidence', 0),
                        timestamp=datetime.now(),
                        metadata={
                            'volatility_ratio': volatility_ratio,
                            'current_volatility': volatility,
                            'historical_volatility': historical_volatility
                        }
                    )
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Erro na avaliação de volatilidade: {e}")
            return None
    
    def _is_in_cooldown(self, keyword: str) -> bool:
        """Verifica se keyword está em cooldown"""
        if keyword not in self.cooldown_timestamps:
            return False
        
        last_alert = self.cooldown_timestamps[keyword]
        cooldown_minutes = self.config.get('default_cooldown_minutes', 30)
        
        return (datetime.now() - last_alert).total_seconds() < cooldown_minutes * 60
    
    def _generate_alert_id(self) -> str:
        """Gera ID único para alerta"""
        return f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.alerts)}"
    
    def _cleanup_old_alerts(self):
        """Remove alertas antigos"""
        try:
            max_alerts = self.config.get('max_active_alerts', 1000)
            
            if len(self.alerts) > max_alerts:
                # Remove alertas mais antigos
                self.alerts.sort(key=lambda value: value.timestamp)
                removed_alerts = self.alerts[:-max_alerts]
                self.alerts = self.alerts[-max_alerts:]
                
                # Move para histórico
                self.alert_history.extend(removed_alerts)
                
                logger.info(f"🧹 {len(removed_alerts)} alertas antigos removidos")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro na limpeza de alertas: {e}")
    
    async def _send_notifications(self, alerts: List[Alert]):
        """Envia notificações para alertas"""
        try:
            for alert in alerts:
                for action in self._get_alert_actions(alert):
                    await self._send_notification(alert, action)
                    
        except Exception as e:
            logger.error(f"❌ Erro no envio de notificações: {e}")
    
    def _get_alert_actions(self, alert: Alert) -> List[str]:
        """Obtém ações para um alerta"""
        rule = next((r for r in self.alert_rules if r.name == alert.rule_name), None)
        return rule.actions if rule else []
    
    async def _send_notification(self, alert: Alert, channel: str):
        """Envia notificação por canal específico"""
        try:
            if channel == 'email':
                await self._send_email_notification(alert)
            elif channel == 'slack':
                await self._send_slack_notification(alert)
            elif channel == 'websocket':
                await self._send_websocket_notification(alert)
            else:
                logger.warning(f"⚠️ Canal não suportado: {channel}")
                
        except Exception as e:
            logger.error(f"❌ Erro no envio de notificação {channel}: {e}")
    
    async def _send_email_notification(self, alert: Alert):
        """Envia notificação por email"""
        try:
            email_config = self.config.get('email_config', {})
            
            if not email_config.get('username') or not email_config.get('password'):
                logger.warning("⚠️ Configuração de email incompleta")
                return
            
            # Cria mensagem
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = email_config.get('to_email', 'admin@omnikeywords.com')
            msg['Subject'] = f"🚨 Alerta: {alert.severity.value.upper()} - {alert.keyword}"
            
            body = f"""
            🚨 ALERTA DETECTADO
            
            Keyword: {alert.keyword}
            Severidade: {alert.severity.value.upper()}
            Tipo: {alert.alert_type.value}
            Mensagem: {alert.message}
            
            Valor Atual: {alert.current_value:.2f}
            Threshold: {alert.threshold_value:.2f}
            Confiança: {alert.confidence:.2f}
            
            Timestamp: {alert.timestamp}
            
            ---
            Omni Keywords Finder - Sistema de Alertas
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Envia email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email enviado para alerta {alert.id}")
            
        except Exception as e:
            logger.error(f"❌ Erro no envio de email: {e}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Envia notificação para Slack"""
        try:
            slack_config = self.config.get('slack_config', {})
            
            if not slack_config.get('webhook_url'):
                logger.warning("⚠️ Webhook do Slack não configurado")
                return
            
            # Usa notification manager se disponível
            if self.notification_manager:
                await self.notification_manager.send_notification(
                    channel='slack',
                    message=alert.message,
                    recipients=[slack_config.get('channel', '#alerts')],
                    metadata={
                        'alert_id': alert.id,
                        'severity': alert.severity.value,
                        'keyword': alert.keyword
                    }
                )
            else:
                logger.warning("⚠️ NotificationManager não disponível")
                
        except Exception as e:
            logger.error(f"❌ Erro no envio para Slack: {e}")
    
    async def _send_websocket_notification(self, alert: Alert):
        """Envia notificação via WebSocket"""
        try:
            if self.notification_manager:
                await self.notification_manager.send_notification(
                    channel='websocket',
                    message=alert.message,
                    recipients=['all'],  # Broadcast para todos
                    metadata={
                        'alert_id': alert.id,
                        'severity': alert.severity.value,
                        'keyword': alert.keyword,
                        'timestamp': alert.timestamp.isoformat()
                    }
                )
            else:
                logger.warning("⚠️ NotificationManager não disponível")
                
        except Exception as e:
            logger.error(f"❌ Erro no envio WebSocket: {e}")
    
    def acknowledge_alert(self, alert_id: str, user: str):
        """
        Reconhece um alerta
        
        Args:
            alert_id: ID do alerta
            user: Usuário que reconheceu
        """
        try:
            alert = next((a for a in self.alerts if a.id == alert_id), None)
            if alert:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.now()
                
                self.metrics.increment_counter("alert_acknowledged")
                logger.info(f"✅ Alerta {alert_id} reconhecido por {user}")
            else:
                logger.warning(f"⚠️ Alerta não encontrado: {alert_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao reconhecer alerta: {e}")
    
    def resolve_alert(self, alert_id: str, user: str):
        """
        Resolve um alerta
        
        Args:
            alert_id: ID do alerta
            user: Usuário que resolveu
        """
        try:
            alert = next((a for a in self.alerts if a.id == alert_id), None)
            if alert:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                
                # Move para histórico
                self.alerts.remove(alert)
                self.alert_history.append(alert)
                
                self.metrics.increment_counter("alert_resolved")
                logger.info(f"✅ Alerta {alert_id} resolvido por {user}")
            else:
                logger.warning(f"⚠️ Alerta não encontrado: {alert_id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao resolver alerta: {e}")
    
    def get_active_alerts(self, filters: Optional[Dict] = None) -> List[Alert]:
        """
        Obtém alertas ativos com filtros
        
        Args:
            filters: Filtros opcionais
            
        Returns:
            Lista de alertas ativos
        """
        try:
            alerts = self.alerts.copy()
            
            if filters:
                if 'severity' in filters:
                    alerts = [a for a in alerts if a.severity == filters['severity']]
                
                if 'alert_type' in filters:
                    alerts = [a for a in alerts if a.alert_type == filters['alert_type']]
                
                if 'keyword' in filters:
                    alerts = [a for a in alerts if a.keyword == filters['keyword']]
                
                if 'status' in filters:
                    alerts = [a for a in alerts if a.status == filters['status']]
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter alertas: {e}")
            return []
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas dos alertas"""
        try:
            total_alerts = len(self.alerts) + len(self.alert_history)
            
            # Por severidade
            severity_stats = {}
            for severity in AlertSeverity:
                count = len([a for a in self.alerts if a.severity == severity])
                severity_stats[severity.value] = count
            
            # Por tipo
            type_stats = {}
            for alert_type in AlertType:
                count = len([a for a in self.alerts if a.alert_type == alert_type])
                type_stats[alert_type.value] = count
            
            # Por status
            status_stats = {}
            for status in AlertStatus:
                count = len([a for a in self.alerts if a.status == status])
                status_stats[status.value] = count
            
            # Alertas nas últimas 24h
            last_24h = datetime.now() - timedelta(hours=24)
            recent_alerts = [a for a in self.alerts if a.timestamp > last_24h]
            
            return {
                'total_alerts': total_alerts,
                'active_alerts': len(self.alerts),
                'resolved_alerts': len(self.alert_history),
                'recent_alerts_24h': len(recent_alerts),
                'severity_distribution': severity_stats,
                'type_distribution': type_stats,
                'status_distribution': status_stats,
                'alert_rules_count': len(self.alert_rules),
                'enabled_rules_count': len([r for r in self.alert_rules if r.enabled])
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    def export_alerts(self, filepath: str, format: str = 'json'):
        """
        Exporta alertas para arquivo
        
        Args:
            filepath: Caminho do arquivo
            format: Formato (json, csv)
        """
        try:
            all_alerts = self.alerts + self.alert_history
            
            if format == 'json':
                data = []
                for alert in all_alerts:
                    data.append({
                        'id': alert.id,
                        'rule_name': alert.rule_name,
                        'alert_type': alert.alert_type.value,
                        'severity': alert.severity.value,
                        'message': alert.message,
                        'keyword': alert.keyword,
                        'current_value': alert.current_value,
                        'threshold_value': alert.threshold_value,
                        'confidence': alert.confidence,
                        'timestamp': alert.timestamp.isoformat(),
                        'status': alert.status.value,
                        'acknowledged_by': alert.acknowledged_by,
                        'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                        'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                        'metadata': alert.metadata
                    })
                
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            elif format == 'csv':
                df = pd.DataFrame([
                    {
                        'id': alert.id,
                        'rule_name': alert.rule_name,
                        'alert_type': alert.alert_type.value,
                        'severity': alert.severity.value,
                        'message': alert.message,
                        'keyword': alert.keyword,
                        'current_value': alert.current_value,
                        'threshold_value': alert.threshold_value,
                        'confidence': alert.confidence,
                        'timestamp': alert.timestamp,
                        'status': alert.status.value
                    }
                    for alert in all_alerts
                ])
                
                df.to_csv(filepath, index=False)
            
            logger.info(f"✅ Alertas exportados para {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro na exportação: {e}")


# Função de conveniência
def create_alert_system(config: Optional[Dict] = None) -> AlertSystem:
    """
    Função de conveniência para criar sistema de alertas
    
    Args:
        config: Configurações opcionais
        
    Returns:
        Sistema de alertas configurado
    """
    return AlertSystem(config) 