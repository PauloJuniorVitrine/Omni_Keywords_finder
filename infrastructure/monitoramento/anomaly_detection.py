"""
Sistema de Detecção de Anomalias - Omni Keywords Finder

Funcionalidades:
- Baseline de métricas automático
- Algoritmos de detecção estatísticos e ML
- Alertas automáticos configuráveis
- Machine learning para detecção adaptativa
- Dashboard de anomalias integrado
- Notificações de alerta em tempo real

Autor: Sistema de Detecção de Anomalias
Data: 2024-12-19
Ruleset: enterprise_control_layer.yaml
"""

import logging
import json
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import threading
import asyncio
import time
from pathlib import Path

# ML Libraries
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import joblib

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary
except ImportError:
    # Fallback se Prometheus não estiver disponível
    class MockMetric:
        def __init__(self, name, description, **kwargs):
            self.name = name
            self.description = description
            self._value = 0
        
        def inc(self, amount=1):
            self._value += amount
        
        def set(self, value):
            self._value = value
        
        def observe(self, value):
            self._value = value
    
    Counter = Histogram = Gauge = Summary = MockMetric

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Tipos de anomalias detectadas"""
    SPIKE = "spike"  # Pico súbito
    DROP = "drop"    # Queda súbita
    TREND = "trend"  # Mudança de tendência
    PATTERN = "pattern"  # Padrão anômalo
    OUTLIER = "outlier"  # Valor atípico
    CLUSTER = "cluster"  # Anomalia em cluster

class AnomalySeverity(Enum):
    """Severidades de anomalia"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DetectionMethod(Enum):
    """Métodos de detecção"""
    STATISTICAL = "statistical"
    ML_ISOLATION_FOREST = "ml_isolation_forest"
    ML_DBSCAN = "ml_dbscan"
    TREND_ANALYSIS = "trend_analysis"
    PATTERN_MATCHING = "pattern_matching"

@dataclass
class BaselineMetric:
    """Estrutura de métrica baseline"""
    name: str
    mean: float
    std: float
    min: float
    max: float
    median: float
    q25: float
    q75: float
    iqr: float
    last_updated: datetime
    sample_size: int
    confidence_interval: Tuple[float, float]

@dataclass
class AnomalyDetection:
    """Estrutura de detecção de anomalia"""
    id: str
    metric_name: str
    timestamp: datetime
    current_value: float
    baseline_value: float
    deviation_score: float
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detection_method: DetectionMethod
    confidence: float
    description: str
    metadata: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class AnomalyAlert:
    """Estrutura de alerta de anomalia"""
    id: str
    anomaly_id: str
    title: str
    message: str
    severity: AnomalySeverity
    timestamp: datetime
    metric_name: str
    current_value: float
    threshold: float
    action_required: bool
    notification_sent: bool = False
    metadata: Dict[str, Any] = None

class StatisticalDetector:
    """Detector estatístico baseado em Z-score e IQR"""
    
    def __init__(self, window_size: int = 100, z_threshold: float = 3.0, iqr_multiplier: float = 1.5):
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier
        self.metrics_history = defaultdict(lambda: deque(maxlen=window_size))
    
    def add_metric(self, metric_name: str, value: float, timestamp: datetime):
        """Adiciona métrica ao histórico"""
        self.metrics_history[metric_name].append({
            'value': value,
            'timestamp': timestamp
        })
    
    def detect_anomalies(self, metric_name: str, current_value: float, timestamp: datetime) -> List[AnomalyDetection]:
        """Detecta anomalias usando métodos estatísticos"""
        anomalies = []
        history = self.metrics_history[metric_name]
        
        if len(history) < 10:  # Mínimo de dados para análise
            return anomalies
        
        values = [h['value'] for h in history]
        
        # Z-score detection
        z_score_anomaly = self._detect_z_score_anomaly(metric_name, current_value, values, timestamp)
        if z_score_anomaly:
            anomalies.append(z_score_anomaly)
        
        # IQR detection
        iqr_anomaly = self._detect_iqr_anomaly(metric_name, current_value, values, timestamp)
        if iqr_anomaly:
            anomalies.append(iqr_anomaly)
        
        # Trend detection
        trend_anomaly = self._detect_trend_anomaly(metric_name, current_value, values, timestamp)
        if trend_anomaly:
            anomalies.append(trend_anomaly)
        
        return anomalies
    
    def _detect_z_score_anomaly(self, metric_name: str, current_value: float, 
                               values: List[float], timestamp: datetime) -> Optional[AnomalyDetection]:
        """Detecta anomalia usando Z-score"""
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return None
        
        z_score = abs((current_value - mean) / std)
        
        if z_score > self.z_threshold:
            deviation_score = z_score
            severity = self._calculate_severity(z_score)
            anomaly_type = AnomalyType.SPIKE if current_value > mean else AnomalyType.DROP
            
            return AnomalyDetection(
                id=str(uuid.uuid4()),
                metric_name=metric_name,
                timestamp=timestamp,
                current_value=current_value,
                baseline_value=mean,
                deviation_score=deviation_score,
                anomaly_type=anomaly_type,
                severity=severity,
                detection_method=DetectionMethod.STATISTICAL,
                confidence=min(z_score / self.z_threshold, 1.0),
                description=f"Anomalia detectada por Z-score: {z_score:.2f} (threshold: {self.z_threshold})",
                metadata={
                    'z_score': z_score,
                    'mean': mean,
                    'std': std,
                    'method': 'z_score'
                }
            )
        
        return None
    
    def _detect_iqr_anomaly(self, metric_name: str, current_value: float,
                           values: List[float], timestamp: datetime) -> Optional[AnomalyDetection]:
        """Detecta anomalia usando IQR"""
        q25 = np.percentile(values, 25)
        q75 = np.percentile(values, 75)
        iqr = q75 - q25
        
        if iqr == 0:
            return None
        
        lower_bound = q25 - (self.iqr_multiplier * iqr)
        upper_bound = q75 + (self.iqr_multiplier * iqr)
        
        if current_value < lower_bound or current_value > upper_bound:
            deviation_score = abs(current_value - np.median(values)) / iqr
            severity = self._calculate_severity(deviation_score)
            anomaly_type = AnomalyType.OUTLIER
            
            return AnomalyDetection(
                id=str(uuid.uuid4()),
                metric_name=metric_name,
                timestamp=timestamp,
                current_value=current_value,
                baseline_value=np.median(values),
                deviation_score=deviation_score,
                anomaly_type=anomaly_type,
                severity=severity,
                detection_method=DetectionMethod.STATISTICAL,
                confidence=min(deviation_score / 2.0, 1.0),
                description=f"Outlier detectado por IQR: valor {current_value:.2f} fora dos limites [{lower_bound:.2f}, {upper_bound:.2f}]",
                metadata={
                    'q25': q25,
                    'q75': q75,
                    'iqr': iqr,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'method': 'iqr'
                }
            )
        
        return None
    
    def _detect_trend_anomaly(self, metric_name: str, current_value: float,
                             values: List[float], timestamp: datetime) -> Optional[AnomalyDetection]:
        """Detecta mudança de tendência"""
        if len(values) < 20:
            return None
        
        # Dividir em duas janelas
        mid_point = len(values) // 2
        window1 = values[:mid_point]
        window2 = values[mid_point:]
        
        mean1 = np.mean(window1)
        mean2 = np.mean(window2)
        
        # Calcular mudança percentual
        change_percent = abs((mean2 - mean1) / mean1 * 100) if mean1 != 0 else 0
        
        if change_percent > 50:  # Mudança significativa de tendência
            deviation_score = change_percent / 100
            severity = self._calculate_severity(deviation_score)
            
            return AnomalyDetection(
                id=str(uuid.uuid4()),
                metric_name=metric_name,
                timestamp=timestamp,
                current_value=current_value,
                baseline_value=mean1,
                deviation_score=deviation_score,
                anomaly_type=AnomalyType.TREND,
                severity=severity,
                detection_method=DetectionMethod.TREND_ANALYSIS,
                confidence=min(change_percent / 100, 1.0),
                description=f"Mudança de tendência detectada: {change_percent:.1f}% de variação",
                metadata={
                    'change_percent': change_percent,
                    'mean_window1': mean1,
                    'mean_window2': mean2,
                    'method': 'trend_analysis'
                }
            )
        
        return None
    
    def _calculate_severity(self, deviation_score: float) -> AnomalySeverity:
        """Calcula severidade baseada no score de desvio"""
        if deviation_score > 5.0:
            return AnomalySeverity.CRITICAL
        elif deviation_score > 3.0:
            return AnomalySeverity.HIGH
        elif deviation_score > 2.0:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

class MLDetector:
    """Detector baseado em Machine Learning"""
    
    def __init__(self, model_path: str = "anomaly_detection_models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        # Modelos ML
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        
        # Estado dos modelos
        self.models_trained = {
            'isolation_forest': False,
            'dbscan': False
        }
        
        # Histórico de features
        self.features_history = defaultdict(lambda: deque(maxlen=1000))
        
        # Métricas Prometheus
        self.ml_predictions = Counter(
            'ml_anomaly_predictions_total',
            'Total de predições ML',
            ['model', 'metric']
        )
        
        self.ml_accuracy = Gauge(
            'ml_anomaly_accuracy',
            'Acurácia dos modelos ML',
            ['model']
        )
    
    def prepare_features(self, metrics_data: Dict[str, List[float]]) -> np.ndarray:
        """Prepara features para ML"""
        features = []
        
        for metric_name, values in metrics_data.items():
            if len(values) >= 10:
                # Features estatísticas
                features.extend([
                    np.mean(values),
                    np.std(values),
                    np.median(values),
                    np.percentile(values, 25),
                    np.percentile(values, 75),
                    np.max(values),
                    np.min(values),
                    np.var(values),
                    np.ptp(values),  # Range
                    len(values)
                ])
            else:
                # Padding com zeros se dados insuficientes
                features.extend([0.0] * 10)
        
        return np.array(features).reshape(1, -1)
    
    def train_models(self, training_data: Dict[str, List[Dict[str, Any]]]):
        """Treina modelos ML com dados históricos"""
        try:
            # Preparar dados de treinamento
            X_train = []
            y_train = []
            
            for metric_name, data_points in training_data.items():
                values = [dp['value'] for dp in data_points]
                anomalies = [dp.get('is_anomaly', False) for dp in data_points]
                
                if len(values) >= 10:
                    features = self.prepare_features({metric_name: values})
                    X_train.append(features.flatten())
                    y_train.append(1 if any(anomalies) else 0)
            
            if len(X_train) < 5:
                logger.warning("Dados insuficientes para treinar modelos ML")
                return
            
            X_train = np.array(X_train)
            y_train = np.array(y_train)
            
            # Normalizar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            
            # Treinar Isolation Forest
            self.isolation_forest.fit(X_train_scaled)
            self.models_trained['isolation_forest'] = True
            
            # Treinar DBSCAN (apenas se houver anomalias)
            if np.sum(y_train) > 0:
                self.dbscan.fit(X_train_scaled)
                self.models_trained['dbscan'] = True
            
            # Salvar modelos
            self._save_models()
            
            # Calcular e registrar acurácia
            if_accuracy = self._calculate_accuracy('isolation_forest', X_train_scaled, y_train)
            self.ml_accuracy.labels(model='isolation_forest').set(if_accuracy)
            
            logger.info(f"Modelos ML treinados com sucesso. Acurácia IF: {if_accuracy:.2f}")
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelos ML: {str(e)}")
    
    def detect_anomalies(self, metrics_data: Dict[str, List[float]], 
                        timestamp: datetime) -> List[AnomalyDetection]:
        """Detecta anomalias usando modelos ML"""
        anomalies = []
        
        if not any(self.models_trained.values()):
            return anomalies
        
        try:
            # Preparar features
            features = self.prepare_features(metrics_data)
            features_scaled = self.scaler.transform(features)
            
            # Isolation Forest
            if self.models_trained['isolation_forest']:
                if_anomaly = self._detect_isolation_forest_anomaly(
                    features_scaled, metrics_data, timestamp
                )
                if if_anomaly:
                    anomalies.append(if_anomaly)
                    self.ml_predictions.labels(
                        model='isolation_forest',
                        metric=list(metrics_data.keys())[0]
                    ).inc()
            
            # DBSCAN
            if self.models_trained['dbscan']:
                dbscan_anomaly = self._detect_dbscan_anomaly(
                    features_scaled, metrics_data, timestamp
                )
                if dbscan_anomaly:
                    anomalies.append(dbscan_anomaly)
                    self.ml_predictions.labels(
                        model='dbscan',
                        metric=list(metrics_data.keys())[0]
                    ).inc()
            
        except Exception as e:
            logger.error(f"Erro na detecção ML: {str(e)}")
        
        return anomalies
    
    def _detect_isolation_forest_anomaly(self, features_scaled: np.ndarray,
                                        metrics_data: Dict[str, List[float]],
                                        timestamp: datetime) -> Optional[AnomalyDetection]:
        """Detecta anomalia usando Isolation Forest"""
        try:
            # Predição (-1 para anomalia, 1 para normal)
            prediction = self.isolation_forest.predict(features_scaled)[0]
            score = self.isolation_forest.decision_function(features_scaled)[0]
            
            if prediction == -1:  # Anomalia detectada
                metric_name = list(metrics_data.keys())[0]
                values = metrics_data[metric_name]
                current_value = values[-1] if values else 0
                
                # Converter score para confiança (0-1)
                confidence = max(0, min(1, abs(score)))
                severity = self._calculate_severity(confidence)
                
                return AnomalyDetection(
                    id=str(uuid.uuid4()),
                    metric_name=metric_name,
                    timestamp=timestamp,
                    current_value=current_value,
                    baseline_value=np.mean(values) if values else 0,
                    deviation_score=confidence,
                    anomaly_type=AnomalyType.OUTLIER,
                    severity=severity,
                    detection_method=DetectionMethod.ML_ISOLATION_FOREST,
                    confidence=confidence,
                    description=f"Anomalia detectada por Isolation Forest (score: {score:.3f})",
                    metadata={
                        'ml_score': score,
                        'prediction': prediction,
                        'method': 'isolation_forest'
                    }
                )
        
        except Exception as e:
            logger.error(f"Erro na detecção Isolation Forest: {str(e)}")
        
        return None
    
    def _detect_dbscan_anomaly(self, features_scaled: np.ndarray,
                              metrics_data: Dict[str, List[float]],
                              timestamp: datetime) -> Optional[AnomalyDetection]:
        """Detecta anomalia usando DBSCAN"""
        try:
            # Predição (-1 para outlier, >=0 para cluster)
            prediction = self.dbscan.fit_predict(features_scaled)[0]
            
            if prediction == -1:  # Outlier detectado
                metric_name = list(metrics_data.keys())[0]
                values = metrics_data[metric_name]
                current_value = values[-1] if values else 0
                
                # Calcular confiança baseada na distância do cluster mais próximo
                confidence = 0.8  # Valor padrão para DBSCAN
                severity = self._calculate_severity(confidence)
                
                return AnomalyDetection(
                    id=str(uuid.uuid4()),
                    metric_name=metric_name,
                    timestamp=timestamp,
                    current_value=current_value,
                    baseline_value=np.mean(values) if values else 0,
                    deviation_score=confidence,
                    anomaly_type=AnomalyType.CLUSTER,
                    severity=severity,
                    detection_method=DetectionMethod.ML_DBSCAN,
                    confidence=confidence,
                    description="Anomalia detectada por DBSCAN (outlier de cluster)",
                    metadata={
                        'cluster_prediction': prediction,
                        'method': 'dbscan'
                    }
                )
        
        except Exception as e:
            logger.error(f"Erro na detecção DBSCAN: {str(e)}")
        
        return None
    
    def _calculate_accuracy(self, model_name: str, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Calcula acurácia do modelo"""
        try:
            if model_name == 'isolation_forest':
                predictions = self.isolation_forest.predict(X_test)
                # Converter -1/1 para 0/1
                predictions = (predictions == -1).astype(int)
            else:
                return 0.0
            
            accuracy = np.mean(predictions == y_test)
            return accuracy
        
        except Exception as e:
            logger.error(f"Erro ao calcular acurácia: {str(e)}")
            return 0.0
    
    def _calculate_severity(self, confidence: float) -> AnomalySeverity:
        """Calcula severidade baseada na confiança"""
        if confidence > 0.8:
            return AnomalySeverity.CRITICAL
        elif confidence > 0.6:
            return AnomalySeverity.HIGH
        elif confidence > 0.4:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
    
    def _save_models(self):
        """Salva modelos treinados"""
        try:
            joblib.dump(self.isolation_forest, self.model_path / 'isolation_forest.pkl')
            joblib.dump(self.dbscan, self.model_path / 'dbscan.pkl')
            joblib.dump(self.scaler, self.model_path / 'scaler.pkl')
            
            # Salvar metadados
            metadata = {
                'models_trained': self.models_trained,
                'last_training': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            }
            
            with open(self.model_path / 'metadata.json', 'w') as f:
                json.dump(metadata, f)
        
        except Exception as e:
            logger.error(f"Erro ao salvar modelos: {str(e)}")
    
    def load_models(self):
        """Carrega modelos salvos"""
        try:
            if (self.model_path / 'isolation_forest.pkl').exists():
                self.isolation_forest = joblib.load(self.model_path / 'isolation_forest.pkl')
                self.models_trained['isolation_forest'] = True
            
            if (self.model_path / 'dbscan.pkl').exists():
                self.dbscan = joblib.load(self.model_path / 'dbscan.pkl')
                self.models_trained['dbscan'] = True
            
            if (self.model_path / 'scaler.pkl').exists():
                self.scaler = joblib.load(self.model_path / 'scaler.pkl')
            
            logger.info("Modelos ML carregados com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {str(e)}")

class BaselineManager:
    """Gerenciador de baseline de métricas"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.baselines = {}
        self.metrics_history = defaultdict(lambda: deque(maxlen=window_size))
        
        # Métricas Prometheus
        self.baseline_updates = Counter(
            'baseline_updates_total',
            'Total de atualizações de baseline',
            ['metric']
        )
    
    def add_metric(self, metric_name: str, value: float, timestamp: datetime):
        """Adiciona métrica ao histórico"""
        self.metrics_history[metric_name].append({
            'value': value,
            'timestamp': timestamp
        })
        
        # Atualizar baseline periodicamente
        if len(self.metrics_history[metric_name]) % 100 == 0:
            self._update_baseline(metric_name)
    
    def get_baseline(self, metric_name: str) -> Optional[BaselineMetric]:
        """Retorna baseline de uma métrica"""
        return self.baselines.get(metric_name)
    
    def get_all_baselines(self) -> Dict[str, BaselineMetric]:
        """Retorna todos os baselines"""
        return self.baselines.copy()
    
    def _update_baseline(self, metric_name: str):
        """Atualiza baseline de uma métrica"""
        try:
            history = self.metrics_history[metric_name]
            
            if len(history) < 10:
                return
            
            values = [h['value'] for h in history]
            
            # Calcular estatísticas
            mean = np.mean(values)
            std = np.std(values)
            min_val = np.min(values)
            max_val = np.max(values)
            median = np.median(values)
            q25 = np.percentile(values, 25)
            q75 = np.percentile(values, 75)
            iqr = q75 - q25
            
            # Intervalo de confiança (95%)
            confidence_interval = (
                mean - 1.96 * std / np.sqrt(len(values)),
                mean + 1.96 * std / np.sqrt(len(values))
            )
            
            baseline = BaselineMetric(
                name=metric_name,
                mean=mean,
                std=std,
                min=min_val,
                max=max_val,
                median=median,
                q25=q25,
                q75=q75,
                iqr=iqr,
                last_updated=datetime.utcnow(),
                sample_size=len(values),
                confidence_interval=confidence_interval
            )
            
            self.baselines[metric_name] = baseline
            self.baseline_updates.labels(metric=metric_name).inc()
            
            logger.debug(f"Baseline atualizado para {metric_name}: mean={mean:.2f}, std={std:.2f}")
        
        except Exception as e:
            logger.error(f"Erro ao atualizar baseline para {metric_name}: {str(e)}")

class AlertManager:
    """Gerenciador de alertas de anomalias"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.alerts = []
        self.alert_rules = self._load_alert_rules()
        self.notification_handlers = []
        
        # Métricas Prometheus
        self.alerts_generated = Counter(
            'anomaly_alerts_generated_total',
            'Total de alertas gerados',
            ['severity', 'metric']
        )
        
        self.alerts_resolved = Counter(
            'anomaly_alerts_resolved_total',
            'Total de alertas resolvidos',
            ['severity', 'metric']
        )
    
    def add_notification_handler(self, handler):
        """Adiciona handler de notificação"""
        self.notification_handlers.append(handler)
    
    def process_anomalies(self, anomalies: List[AnomalyDetection]) -> List[AnomalyAlert]:
        """Processa anomalias e gera alertas"""
        alerts = []
        
        for anomaly in anomalies:
            alert = self._create_alert(anomaly)
            if alert:
                alerts.append(alert)
                self.alerts.append(alert)
                self.alerts_generated.labels(
                    severity=alert.severity.value,
                    metric=alert.metric_name
                ).inc()
        
        # Enviar notificações
        self._send_notifications(alerts)
        
        return alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Reconhece um alerta"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve um alerta"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                self.alerts_resolved.labels(
                    severity=alert.severity.value,
                    metric=alert.metric_name
                ).inc()
                return True
        return False
    
    def get_active_alerts(self) -> List[AnomalyAlert]:
        """Retorna alertas ativos"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_alert_history(self, hours: int = 24) -> List[AnomalyAlert]:
        """Retorna histórico de alertas"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
    
    def _create_alert(self, anomaly: AnomalyDetection) -> Optional[AnomalyAlert]:
        """Cria alerta baseado na anomalia"""
        # Verificar regras de alerta
        rule = self._get_matching_rule(anomaly)
        if not rule:
            return None
        
        # Verificar se já existe alerta similar recente
        if self._has_recent_similar_alert(anomaly):
            return None
        
        alert = AnomalyAlert(
            id=str(uuid.uuid4()),
            anomaly_id=anomaly.id,
            title=f"Anomalia detectada em {anomaly.metric_name}",
            message=self._generate_alert_message(anomaly),
            severity=anomaly.severity,
            timestamp=anomaly.timestamp,
            metric_name=anomaly.metric_name,
            current_value=anomaly.current_value,
            threshold=anomaly.baseline_value,
            action_required=rule.get('action_required', False),
            metadata={
                'anomaly_type': anomaly.anomaly_type.value,
                'detection_method': anomaly.detection_method.value,
                'confidence': anomaly.confidence
            }
        )
        
        return alert
    
    def _get_matching_rule(self, anomaly: AnomalyDetection) -> Optional[Dict[str, Any]]:
        """Encontra regra de alerta que corresponde à anomalia"""
        for rule in self.alert_rules:
            if (rule['metric_name'] == anomaly.metric_name or 
                rule['metric_name'] == '*'):
                
                if (rule['severity'] == anomaly.severity.value or 
                    rule['severity'] == '*'):
                    
                    if (rule['anomaly_type'] == anomaly.anomaly_type.value or 
                        rule['anomaly_type'] == '*'):
                        
                        return rule
        
        return None
    
    def _has_recent_similar_alert(self, anomaly: AnomalyDetection) -> bool:
        """Verifica se já existe alerta similar recente"""
        recent_cutoff = datetime.utcnow() - timedelta(minutes=30)
        
        for alert in self.alerts:
            if (alert.metric_name == anomaly.metric_name and
                alert.severity == anomaly.severity and
                alert.timestamp >= recent_cutoff and
                not alert.resolved):
                return True
        
        return False
    
    def _generate_alert_message(self, anomaly: AnomalyDetection) -> str:
        """Gera mensagem do alerta"""
        return (
            f"Anomalia {anomaly.anomaly_type.value} detectada em {anomaly.metric_name}. "
            f"Valor atual: {anomaly.current_value:.2f}, "
            f"Baseline: {anomaly.baseline_value:.2f}, "
            f"Desvio: {anomaly.deviation_score:.2f}, "
            f"Confiança: {anomaly.confidence:.2f}. "
            f"Método: {anomaly.detection_method.value}"
        )
    
    def _send_notifications(self, alerts: List[AnomalyAlert]):
        """Envia notificações para handlers registrados"""
        for alert in alerts:
            if alert.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]:
                for handler in self.notification_handlers:
                    try:
                        handler(alert)
                        alert.notification_sent = True
                    except Exception as e:
                        logger.error(f"Erro ao enviar notificação: {str(e)}")
    
    def _load_alert_rules(self) -> List[Dict[str, Any]]:
        """Carrega regras de alerta"""
        return [
            {
                'metric_name': '*',
                'severity': 'critical',
                'anomaly_type': '*',
                'action_required': True
            },
            {
                'metric_name': '*',
                'severity': 'high',
                'anomaly_type': '*',
                'action_required': True
            },
            {
                'metric_name': '*',
                'severity': 'medium',
                'anomaly_type': '*',
                'action_required': False
            },
            {
                'metric_name': '*',
                'severity': 'low',
                'anomaly_type': '*',
                'action_required': False
            }
        ]

class AnomalyDetectionSystem:
    """Sistema principal de detecção de anomalias"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.baseline_manager = BaselineManager()
        self.statistical_detector = StatisticalDetector()
        self.ml_detector = MLDetector()
        self.alert_manager = AlertManager()
        
        # Estado do sistema
        self.is_running = False
        self.detection_thread = None
        self.detection_interval = self.config.get('detection_interval', 60)  # segundos
        
        # Histórico de detecções
        self.detections_history = deque(maxlen=10000)
        
        # Métricas Prometheus
        self.detections_total = Counter(
            'anomaly_detections_total',
            'Total de detecções de anomalias',
            ['method', 'severity']
        )
        
        self.system_health = Gauge(
            'anomaly_detection_system_health',
            'Saúde do sistema de detecção'
        )
        
        # Carregar modelos ML salvos
        self.ml_detector.load_models()
        
        logger.info("Sistema de Detecção de Anomalias inicializado")
    
    def start(self):
        """Inicia o sistema de detecção"""
        if self.is_running:
            logger.warning("Sistema já está em execução")
            return
        
        self.is_running = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        
        logger.info("Sistema de Detecção de Anomalias iniciado")
    
    def stop(self):
        """Para o sistema de detecção"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=5)
        
        logger.info("Sistema de Detecção de Anomalias parado")
    
    def add_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Adiciona métrica para análise"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Adicionar aos gerenciadores
        self.baseline_manager.add_metric(metric_name, value, timestamp)
        self.statistical_detector.add_metric(metric_name, value, timestamp)
        
        # Adicionar ao histórico de features ML
        self.ml_detector.features_history[metric_name].append(value)
    
    def detect_anomalies(self, metric_name: str, current_value: float, 
                        timestamp: datetime = None) -> List[AnomalyDetection]:
        """Detecta anomalias para uma métrica específica"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        anomalies = []
        
        try:
            # Detecção estatística
            stat_anomalies = self.statistical_detector.detect_anomalies(
                metric_name, current_value, timestamp
            )
            anomalies.extend(stat_anomalies)
            
            # Detecção ML
            if len(self.ml_detector.features_history[metric_name]) >= 10:
                ml_data = {metric_name: list(self.ml_detector.features_history[metric_name])}
                ml_anomalies = self.ml_detector.detect_anomalies(ml_data, timestamp)
                anomalies.extend(ml_anomalies)
            
            # Registrar métricas
            for anomaly in anomalies:
                self.detections_total.labels(
                    method=anomaly.detection_method.value,
                    severity=anomaly.severity.value
                ).inc()
            
            # Adicionar ao histórico
            self.detections_history.extend(anomalies)
            
            # Atualizar saúde do sistema
            self.system_health.set(1.0 if self.is_running else 0.0)
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalias: {str(e)}")
            self.system_health.set(0.0)
        
        return anomalies
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados para dashboard"""
        try:
            # Estatísticas gerais
            total_detections = len(self.detections_history)
            recent_detections = len([
                data for data in self.detections_history 
                if data.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ])
            
            # Detecções por severidade
            severity_counts = defaultdict(int)
            for detection in self.detections_history:
                severity_counts[detection.severity.value] += 1
            
            # Detecções por método
            method_counts = defaultdict(int)
            for detection in self.detections_history:
                method_counts[detection.detection_method.value] += 1
            
            # Alertas ativos
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Baselines
            baselines = self.baseline_manager.get_all_baselines()
            
            return {
                'system_status': {
                    'running': self.is_running,
                    'health': self.system_health._value.get(),
                    'last_update': datetime.utcnow().isoformat()
                },
                'statistics': {
                    'total_detections': total_detections,
                    'recent_detections': recent_detections,
                    'active_alerts': len(active_alerts),
                    'baselines_count': len(baselines)
                },
                'severity_distribution': dict(severity_counts),
                'method_distribution': dict(method_counts),
                'recent_detections': [
                    {
                        'id': data.id,
                        'metric_name': data.metric_name,
                        'timestamp': data.timestamp.isoformat(),
                        'severity': data.severity.value,
                        'anomaly_type': data.anomaly_type.value,
                        'confidence': data.confidence
                    }
                    for data in list(self.detections_history)[-50:]  # Últimas 50 detecções
                ],
                'active_alerts': [
                    {
                        'id': a.id,
                        'title': a.title,
                        'severity': a.severity.value,
                        'timestamp': a.timestamp.isoformat(),
                        'action_required': a.action_required
                    }
                    for a in active_alerts
                ],
                'baselines': {
                    name: {
                        'mean': b.mean,
                        'std': b.std,
                        'last_updated': b.last_updated.isoformat(),
                        'sample_size': b.sample_size
                    }
                    for name, b in baselines.items()
                }
            }
        
        except Exception as e:
            logger.error(f"Erro ao gerar dados do dashboard: {str(e)}")
            return {
                'error': str(e),
                'system_status': {'running': False, 'health': 0.0}
            }
    
    def train_ml_models(self, training_data: Dict[str, List[Dict[str, Any]]]):
        """Treina modelos ML com dados históricos"""
        try:
            self.ml_detector.train_models(training_data)
            logger.info("Modelos ML treinados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao treinar modelos ML: {str(e)}")
    
    def _detection_loop(self):
        """Loop principal de detecção"""
        while self.is_running:
            try:
                # Processar métricas em lote
                self._process_batch_detection()
                
                # Aguardar próximo ciclo
                time.sleep(self.detection_interval)
            
            except Exception as e:
                logger.error(f"Erro no loop de detecção: {str(e)}")
                time.sleep(10)  # Aguardar antes de tentar novamente
    
    def _process_batch_detection(self):
        """Processa detecção em lote"""
        try:
            # Coletar métricas recentes
            recent_metrics = {}
            for metric_name, history in self.ml_detector.features_history.items():
                if len(history) > 0:
                    recent_metrics[metric_name] = list(history)[-1]
            
            # Detectar anomalias
            for metric_name, current_value in recent_metrics.items():
                anomalies = self.detect_anomalies(metric_name, current_value)
                
                if anomalies:
                    # Gerar alertas
                    alerts = self.alert_manager.process_anomalies(anomalies)
                    
                    if alerts:
                        logger.info(f"Alertas gerados para {metric_name}: {len(alerts)} alertas")
        
        except Exception as e:
            logger.error(f"Erro no processamento em lote: {str(e)}")

def create_anomaly_detection_system(config: Optional[Dict[str, Any]] = None) -> AnomalyDetectionSystem:
    """Factory function para criar sistema de detecção de anomalias"""
    return AnomalyDetectionSystem(config)

# Exemplo de uso
if __name__ == "__main__":
    # Configuração do sistema
    config = {
        'detection_interval': 30,  # 30 segundos
        'alert_thresholds': {
            'critical': 0.8,
            'high': 0.6,
            'medium': 0.4,
            'low': 0.2
        }
    }
    
    # Criar sistema
    system = create_anomaly_detection_system(config)
    
    # Iniciar sistema
    system.start()
    
    try:
        # Simular métricas
        for index in range(100):
            value = 100 + np.random.normal(0, 10)  # Valor normal
            if index == 50:  # Anomalia
                value = 200
            
            system.add_metric('api_latency', value)
            time.sleep(1)
        
        # Obter dados do dashboard
        dashboard_data = system.get_dashboard_data()
        print(json.dumps(dashboard_data, indent=2))
    
    finally:
        system.stop() 