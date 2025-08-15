"""
Sistema de Feedback Loop - Omni Keywords Finder
Tracing ID: ML_ADAPTATIVE_20241219_001
Data: 2024-12-19
Versão: 1.0

Implementa feedback loop para aprendizado contínuo:
- Coleta de feedback de usuários
- Adaptação automática de modelos
- Aprendizado incremental
- Detecção de drift de dados
- Retreinamento automático
- Validação de performance
"""

import numpy as np
import pandas as pd
import time
import logging
import json
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta

try:
    from sklearn.metrics import silhouette_score, calinski_harabasz_score
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn não disponível. Feedback loop será limitado.")

try:
    from infrastructure.observability.telemetry import get_telemetry_manager
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logging.warning("Telemetria não disponível. Métricas serão limitadas.")


class FeedbackType(Enum):
    """Tipos de feedback disponíveis."""
    USER_RATING = "user_rating"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"
    DWELL_TIME = "dwell_time"
    BOUNCE_RATE = "bounce_rate"
    MANUAL_CORRECTION = "manual_correction"
    AUTOMATIC_DETECTION = "automatic_detection"


class DriftType(Enum):
    """Tipos de drift detectados."""
    CONCEPT_DRIFT = "concept_drift"
    DATA_DRIFT = "data_drift"
    LABEL_DRIFT = "label_drift"
    COVARIATE_DRIFT = "covariate_drift"


@dataclass
class FeedbackData:
    """Dados de feedback."""
    feedback_type: FeedbackType
    value: float
    timestamp: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    model_version: Optional[str] = None
    prediction_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DriftDetection:
    """Detecção de drift."""
    drift_type: DriftType
    severity: float  # 0.0 a 1.0
    timestamp: float
    features_affected: List[str]
    confidence: float
    description: str


@dataclass
class FeedbackLoopConfig:
    """Configuração do feedback loop."""
    feedback_window_size: int = 1000  # Número de feedbacks para análise
    feedback_retention_days: int = 30
    drift_detection_threshold: float = 0.1
    performance_degradation_threshold: float = 0.05
    retraining_threshold: float = 0.15
    min_feedback_for_analysis: int = 100
    feedback_weight_decay: float = 0.95
    enable_automatic_retraining: bool = True
    enable_drift_detection: bool = True
    enable_performance_monitoring: bool = True
    feedback_storage_path: str = "data/feedback"


class FeedbackLoop:
    """
    Sistema de feedback loop para aprendizado contínuo.
    """
    
    def __init__(self, config: Optional[FeedbackLoopConfig] = None):
        self.config = config or FeedbackLoopConfig()
        self.feedback_buffer = deque(maxlen=self.config.feedback_window_size)
        self.performance_history = deque(maxlen=1000)
        self.drift_detections = []
        self.model_versions = {}
        self.feedback_weights = defaultdict(float)
        self._lock = threading.RLock()
        self._last_analysis = time.time()
        self._last_retraining = time.time()
        
        # Configurar telemetria
        if TELEMETRY_AVAILABLE:
            self.telemetry = get_telemetry_manager()
        else:
            self.telemetry = None
        
        self.logger = logging.getLogger(__name__)
        
        # Criar diretório de armazenamento
        Path(self.config.feedback_storage_path).mkdir(parents=True, exist_ok=True)
    
    def add_feedback(self, feedback: FeedbackData) -> None:
        """
        Adiciona feedback ao sistema.
        
        Args:
            feedback: Dados de feedback
        """
        with self._lock:
            self.feedback_buffer.append(feedback)
            
            # Aplicar peso temporal (feedback mais recente tem mais peso)
            weight = self.config.feedback_weight_decay ** (
                (time.time() - feedback.timestamp) / (24 * 3600)  # Dias
            )
            self.feedback_weights[feedback.feedback_type] += weight
            
            # Registrar métricas
            if self.telemetry:
                self.telemetry.record_metric(
                    "feedback_received",
                    1,
                    {"feedback_type": feedback.feedback_type.value}
                )
                
                self.telemetry.record_metric(
                    "feedback_value",
                    feedback.value,
                    {"feedback_type": feedback.feedback_type.value}
                )
            
            # Verificar se deve fazer análise
            if len(self.feedback_buffer) >= self.config.min_feedback_for_analysis:
                self._trigger_analysis()
    
    def _trigger_analysis(self) -> None:
        """Dispara análise de feedback."""
        current_time = time.time()
        
        # Evitar análises muito frequentes
        if current_time - self._last_analysis < 300:  # 5 minutos
            return
        
        self._last_analysis = current_time
        
        # Executar análise em thread separada
        thread = threading.Thread(target=self._analyze_feedback)
        thread.daemon = True
        thread.start()
    
    def _analyze_feedback(self) -> None:
        """Analisa feedback coletado."""
        try:
            # Converter feedback para DataFrame
            feedback_df = self._feedback_to_dataframe()
            
            if feedback_df.empty:
                return
            
            # Análise de performance
            if self.config.enable_performance_monitoring:
                self._analyze_performance(feedback_df)
            
            # Detecção de drift
            if self.config.enable_drift_detection:
                self._detect_drift(feedback_df)
            
            # Verificar necessidade de retreinamento
            if self.config.enable_automatic_retraining:
                self._check_retraining_needs(feedback_df)
            
            # Salvar feedback processado
            self._save_feedback_analysis(feedback_df)
            
        except Exception as e:
            self.logger.error(f"Erro na análise de feedback: {e}")
    
    def _feedback_to_dataframe(self) -> pd.DataFrame:
        """
        Converte buffer de feedback para DataFrame.
        
        Returns:
            DataFrame com feedback
        """
        if not self.feedback_buffer:
            return pd.DataFrame()
        
        data = []
        for feedback in self.feedback_buffer:
            data.append({
                'feedback_type': feedback.feedback_type.value,
                'value': feedback.value,
                'timestamp': feedback.timestamp,
                'user_id': feedback.user_id,
                'session_id': feedback.session_id,
                'model_version': feedback.model_version,
                'prediction_id': feedback.prediction_id,
                'metadata': json.dumps(feedback.metadata) if feedback.metadata else None
            })
        
        return pd.DataFrame(data)
    
    def _analyze_performance(self, feedback_df: pd.DataFrame) -> None:
        """
        Analisa performance baseada no feedback.
        
        Args:
            feedback_df: DataFrame com feedback
        """
        # Calcular métricas por tipo de feedback
        performance_metrics = {}
        
        for feedback_type in FeedbackType:
            type_data = feedback_df[feedback_df['feedback_type'] == feedback_type.value]
            
            if not type_data.empty:
                performance_metrics[feedback_type.value] = {
                    'mean': type_data['value'].mean(),
                    'std': type_data['value'].std(),
                    'count': len(type_data),
                    'trend': self._calculate_trend(type_data['value'])
                }
        
        # Detectar degradação de performance
        for metric_name, metrics in performance_metrics.items():
            if 'trend' in metrics and metrics['trend'] < -self.config.performance_degradation_threshold:
                self.logger.warning(f"Degradação de performance detectada em {metric_name}: {metrics['trend']:.3f}")
                
                # Registrar alerta
                if self.telemetry:
                    self.telemetry.record_metric(
                        "performance_degradation_detected",
                        1,
                        {"metric": metric_name, "trend": metrics['trend']}
                    )
        
        # Armazenar métricas
        self.performance_history.append({
            'timestamp': time.time(),
            'metrics': performance_metrics
        })
    
    def _calculate_trend(self, values: pd.Series) -> float:
        """
        Calcula tendência dos valores.
        
        Args:
            values: Série de valores
            
        Returns:
            Coeficiente de tendência
        """
        if len(values) < 2:
            return 0.0
        
        # Usar regressão linear simples
        value = np.arange(len(values))
        result = values.values
        
        try:
            slope = np.polyfit(value, result, 1)[0]
            return slope
        except:
            return 0.0
    
    def _detect_drift(self, feedback_df: pd.DataFrame) -> None:
        """
        Detecta drift nos dados.
        
        Args:
            feedback_df: DataFrame com feedback
        """
        # Detectar concept drift (mudança na distribuição de feedback)
        if len(feedback_df) >= 100:
            recent_feedback = feedback_df.tail(50)
            older_feedback = feedback_df.head(50)
            
            # Comparar distribuições
            for feedback_type in FeedbackType:
                recent_values = recent_feedback[
                    recent_feedback['feedback_type'] == feedback_type.value
                ]['value']
                older_values = older_feedback[
                    older_feedback['feedback_type'] == feedback_type.value
                ]['value']
                
                if len(recent_values) > 10 and len(older_values) > 10:
                    drift_score = self._calculate_distribution_drift(
                        recent_values, older_values
                    )
                    
                    if drift_score > self.config.drift_detection_threshold:
                        drift_detection = DriftDetection(
                            drift_type=DriftType.CONCEPT_DRIFT,
                            severity=drift_score,
                            timestamp=time.time(),
                            features_affected=[feedback_type.value],
                            confidence=min(drift_score * 2, 1.0),
                            description=f"Concept drift detectado em {feedback_type.value}"
                        )
                        
                        self.drift_detections.append(drift_detection)
                        
                        self.logger.warning(f"Drift detectado: {drift_detection.description}")
                        
                        # Registrar métricas
                        if self.telemetry:
                            self.telemetry.record_metric(
                                "drift_detected",
                                1,
                                {
                                    "drift_type": drift_detection.drift_type.value,
                                    "severity": drift_detection.severity,
                                    "features": ",".join(drift_detection.features_affected)
                                }
                            )
    
    def _calculate_distribution_drift(self, recent: pd.Series, older: pd.Series) -> float:
        """
        Calcula score de drift entre duas distribuições.
        
        Args:
            recent: Valores recentes
            older: Valores antigos
            
        Returns:
            Score de drift (0.0 a 1.0)
        """
        try:
            # Usar teste de Kolmogorov-Smirnov
            from scipy.stats import ks_2samp
            
            statistic, p_value = ks_2samp(recent, older)
            return 1.0 - p_value  # Quanto menor o p-value, maior o drift
            
        except ImportError:
            # Fallback simples: diferença de médias normalizada
            recent_mean = recent.mean()
            older_mean = older.mean()
            recent_std = recent.std()
            
            if recent_std > 0:
                return abs(recent_mean - older_mean) / recent_std
            else:
                return 0.0
    
    def _check_retraining_needs(self, feedback_df: pd.DataFrame) -> None:
        """
        Verifica se é necessário retreinamento.
        
        Args:
            feedback_df: DataFrame com feedback
        """
        current_time = time.time()
        
        # Evitar retreinamento muito frequente
        if current_time - self._last_retraining < 3600:  # 1 hora
            return
        
        # Verificar critérios de retreinamento
        retraining_score = 0.0
        
        # 1. Drift detectado
        recent_drifts = [
            drift for drift in self.drift_detections
            if current_time - drift.timestamp < 86400  # Últimas 24h
        ]
        
        if recent_drifts:
            max_drift_severity = max(drift.severity for drift in recent_drifts)
            retraining_score += max_drift_severity
        
        # 2. Degradação de performance
        if len(self.performance_history) >= 2:
            recent_performance = self.performance_history[-1]['metrics']
            older_performance = self.performance_history[-2]['metrics']
            
            for metric_name in recent_performance:
                if metric_name in older_performance:
                    recent_mean = recent_performance[metric_name]['mean']
                    older_mean = older_performance[metric_name]['mean']
                    
                    if older_mean > 0:
                        degradation = (older_mean - recent_mean) / older_mean
                        if degradation > 0:
                            retraining_score += degradation
        
        # 3. Volume de feedback
        feedback_volume = len(feedback_df)
        if feedback_volume > 1000:
            retraining_score += 0.1
        
        # Decidir retreinamento
        if retraining_score > self.config.retraining_threshold:
            self.logger.info(f"Retreinamento necessário. Score: {retraining_score:.3f}")
            
            # Disparar retreinamento
            self._trigger_retraining()
            
            self._last_retraining = current_time
    
    def _trigger_retraining(self) -> None:
        """Dispara processo de retreinamento."""
        # Executar em thread separada
        thread = threading.Thread(target=self._execute_retraining)
        thread.daemon = True
        thread.start()
    
    def _execute_retraining(self) -> None:
        """Executa retreinamento do modelo."""
        try:
            self.logger.info("Iniciando retreinamento do modelo...")
            
            # Aqui você integraria com o sistema de modelos adaptativos
            # Por exemplo:
            # from infrastructure.ml.adaptativo.modelo_adaptativo import get_adaptive_model
            # model = get_adaptive_model()
            # model.fit(new_data)
            
            # Registrar métricas
            if self.telemetry:
                self.telemetry.record_metric(
                    "model_retraining_triggered",
                    1,
                    {"reason": "feedback_loop"}
                )
            
            self.logger.info("Retreinamento concluído")
            
        except Exception as e:
            self.logger.error(f"Erro no retreinamento: {e}")
    
    def _save_feedback_analysis(self, feedback_df: pd.DataFrame) -> None:
        """
        Salva análise de feedback.
        
        Args:
            feedback_df: DataFrame com feedback
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path(self.config.feedback_storage_path) / f"feedback_analysis_{timestamp}.json"
        
        analysis_data = {
            'timestamp': timestamp,
            'feedback_count': len(feedback_df),
            'feedback_types': feedback_df['feedback_type'].value_counts().to_dict(),
            'performance_metrics': self._get_latest_performance_metrics(),
            'drift_detections': [
                asdict(drift) for drift in self.drift_detections[-10:]  # Últimas 10
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
    
    def _get_latest_performance_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas de performance mais recentes.
        
        Returns:
            Dicionário com métricas
        """
        if not self.performance_history:
            return {}
        
        return self.performance_history[-1]['metrics']
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo do feedback coletado.
        
        Returns:
            Dicionário com resumo
        """
        with self._lock:
            feedback_df = self._feedback_to_dataframe()
            
            if feedback_df.empty:
                return {"error": "Nenhum feedback coletado"}
            
            summary = {
                'total_feedback': len(feedback_df),
                'feedback_types': feedback_df['feedback_type'].value_counts().to_dict(),
                'feedback_window': len(self.feedback_buffer),
                'performance_history_count': len(self.performance_history),
                'drift_detections_count': len(self.drift_detections),
                'last_analysis': datetime.fromtimestamp(self._last_analysis).isoformat(),
                'last_retraining': datetime.fromtimestamp(self._last_retraining).isoformat()
            }
            
            # Adicionar métricas de performance se disponíveis
            if self.performance_history:
                summary['latest_performance'] = self._get_latest_performance_metrics()
            
            # Adicionar drift recente se disponível
            recent_drifts = [
                drift for drift in self.drift_detections
                if time.time() - drift.timestamp < 86400  # Últimas 24h
            ]
            
            if recent_drifts:
                summary['recent_drifts'] = [
                    {
                        'type': drift.drift_type.value,
                        'severity': drift.severity,
                        'description': drift.description
                    }
                    for drift in recent_drifts
                ]
            
            return summary
    
    def clear_old_feedback(self) -> None:
        """Remove feedback antigo baseado na configuração de retenção."""
        with self._lock:
            cutoff_time = time.time() - (self.config.feedback_retention_days * 24 * 3600)
            
            # Remover feedback antigo do buffer
            self.feedback_buffer = deque(
                [f for f in self.feedback_buffer if f.timestamp > cutoff_time],
                maxlen=self.config.feedback_window_size
            )
            
            # Remover detecções de drift antigas
            self.drift_detections = [
                drift for drift in self.drift_detections
                if drift.timestamp > cutoff_time
            ]
            
            # Remover histórico de performance antigo
            self.performance_history = deque(
                [p for p in self.performance_history if p['timestamp'] > cutoff_time],
                maxlen=1000
            )
            
            self.logger.info(f"Feedback antigo removido. Cutoff: {cutoff_time}")


# Instância global do feedback loop
feedback_loop = FeedbackLoop()


def get_feedback_loop() -> FeedbackLoop:
    """Retorna a instância global do feedback loop."""
    return feedback_loop


def initialize_feedback_loop(config: Optional[FeedbackLoopConfig] = None) -> FeedbackLoop:
    """
    Inicializa e retorna o sistema de feedback loop.
    
    Args:
        config: Configuração do feedback loop
        
    Returns:
        Instância configurada do FeedbackLoop
    """
    global feedback_loop
    feedback_loop = FeedbackLoop(config)
    return feedback_loop


# Funções de conveniência
def add_user_feedback(feedback_type: FeedbackType, value: float, 
                     user_id: Optional[str] = None, **kwargs) -> None:
    """
    Adiciona feedback de usuário.
    
    Args:
        feedback_type: Tipo de feedback
        value: Valor do feedback
        user_id: ID do usuário
        **kwargs: Argumentos adicionais
    """
    feedback = FeedbackData(
        feedback_type=feedback_type,
        value=value,
        timestamp=time.time(),
        user_id=user_id,
        **kwargs
    )
    
    feedback_loop.add_feedback(feedback)


def get_feedback_summary() -> Dict[str, Any]:
    """
    Retorna resumo do feedback.
    
    Returns:
        Dicionário com resumo
    """
    return feedback_loop.get_feedback_summary() 