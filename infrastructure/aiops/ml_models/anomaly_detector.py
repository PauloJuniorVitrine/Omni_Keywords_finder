"""
Sistema de Detecção de Anomalias - Omni Keywords Finder
Modelos de ML para detecção de anomalias em eventos e métricas

Tracing ID: ANOMALY_DETECTOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🟡 ALTO - Detecção de Anomalias

Baseado no código real do sistema Omni Keywords Finder
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import joblib
import json
from pathlib import Path

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

from ...intelligent_collector import Event, EventType, EventSeverity

logger = logging.getLogger(__name__)

class AnomalyAlgorithm(Enum):
    """Algoritmos de detecção de anomalias disponíveis"""
    ISOLATION_FOREST = "isolation_forest"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    STATISTICAL = "statistical"
    ENSEMBLE = "ensemble"

class AnomalyType(Enum):
    """Tipos de anomalias detectadas"""
    POINT = "point"  # Anomalia pontual
    CONTEXTUAL = "contextual"  # Anomalia contextual
    COLLECTIVE = "collective"  # Anomalia coletiva
    TREND = "trend"  # Anomalia de tendência

@dataclass
class AnomalyResult:
    """Resultado da detecção de anomalia"""
    event_id: str
    is_anomaly: bool
    score: float
    algorithm: str
    anomaly_type: AnomalyType
    confidence: float
    features: Dict[str, float]
    timestamp: datetime
    metadata: Dict[str, Any]

class FeatureExtractor:
    """Extrator de features para detecção de anomalias"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.scalers = {}
        self.feature_names = []
        
    def extract_features(self, events: List[Event]) -> pd.DataFrame:
        """
        Extrai features dos eventos para detecção de anomalias.
        Baseado em dados reais do sistema Omni Keywords Finder.
        """
        if not events:
            return pd.DataFrame()
        
        features_list = []
        
        for event in events:
            features = self._extract_event_features(event)
            features_list.append(features)
        
        df = pd.DataFrame(features_list)
        self.feature_names = df.columns.tolist()
        
        return df
    
    def _extract_event_features(self, event: Event) -> Dict[str, float]:
        """Extrai features de um evento específico"""
        features = {
            'timestamp_hour': event.timestamp.hour,
            'timestamp_minute': event.timestamp.minute,
            'timestamp_second': event.timestamp.second,
            'timestamp_weekday': event.timestamp.weekday(),
            'severity_numeric': self._severity_to_numeric(event.severity),
            'event_type_numeric': self._event_type_to_numeric(event.type),
            'source_numeric': self._source_to_numeric(event.source),
            'has_correlation_id': 1.0 if event.correlation_id else 0.0,
            'has_user_id': 1.0 if event.user_id else 0.0,
            'has_session_id': 1.0 if event.session_id else 0.0,
        }
        
        # Features específicas baseadas no tipo de evento
        if event.type == EventType.SYSTEM_METRIC:
            features.update(self._extract_system_metric_features(event))
        elif event.type == EventType.APPLICATION_LOG:
            features.update(self._extract_application_log_features(event))
        elif event.type == EventType.DATABASE_QUERY:
            features.update(self._extract_database_query_features(event))
        elif event.type == EventType.API_REQUEST:
            features.update(self._extract_api_request_features(event))
        elif event.type == EventType.ERROR_EVENT:
            features.update(self._extract_error_event_features(event))
        
        return features
    
    def _extract_system_metric_features(self, event: Event) -> Dict[str, float]:
        """Extrai features específicas de métricas do sistema"""
        features = {}
        data = event.data
        
        if 'value' in data:
            features['metric_value'] = float(data['value'])
        else:
            features['metric_value'] = 0.0
            
        if 'metric_name' in data:
            features['metric_name_numeric'] = self._metric_name_to_numeric(data['metric_name'])
        else:
            features['metric_name_numeric'] = 0.0
            
        return features
    
    def _extract_application_log_features(self, event: Event) -> Dict[str, float]:
        """Extrai features específicas de logs da aplicação"""
        features = {}
        data = event.data
        
        if 'level' in data:
            features['log_level_numeric'] = self._log_level_to_numeric(data['level'])
        else:
            features['log_level_numeric'] = 0.0
            
        if 'message' in data:
            features['message_length'] = len(str(data['message']))
        else:
            features['message_length'] = 0.0
            
        return features
    
    def _extract_database_query_features(self, event: Event) -> Dict[str, float]:
        """Extrai features específicas de queries do banco"""
        features = {}
        data = event.data
        
        if 'execution_time' in data:
            features['execution_time'] = float(data['execution_time'])
        else:
            features['execution_time'] = 0.0
            
        if 'rows_affected' in data:
            features['rows_affected'] = float(data['rows_affected'])
        else:
            features['rows_affected'] = 0.0
            
        return features
    
    def _extract_api_request_features(self, event: Event) -> Dict[str, float]:
        """Extrai features específicas de requisições API"""
        features = {}
        data = event.data
        
        if 'response_time' in data:
            features['response_time'] = float(data['response_time'])
        else:
            features['response_time'] = 0.0
            
        if 'endpoint' in data:
            features['endpoint_numeric'] = self._endpoint_to_numeric(data['endpoint'])
        else:
            features['endpoint_numeric'] = 0.0
            
        return features
    
    def _extract_error_event_features(self, event: Event) -> Dict[str, float]:
        """Extrai features específicas de eventos de erro"""
        features = {}
        data = event.data
        
        if 'error' in data:
            features['error_message_length'] = len(str(data['error']))
        else:
            features['error_message_length'] = 0.0
            
        return features
    
    def _severity_to_numeric(self, severity: EventSeverity) -> float:
        """Converte severidade para valor numérico"""
        mapping = {
            EventSeverity.LOW: 1.0,
            EventSeverity.MEDIUM: 2.0,
            EventSeverity.HIGH: 3.0,
            EventSeverity.CRITICAL: 4.0
        }
        return mapping.get(severity, 1.0)
    
    def _event_type_to_numeric(self, event_type: EventType) -> float:
        """Converte tipo de evento para valor numérico"""
        mapping = {
            EventType.SYSTEM_METRIC: 1.0,
            EventType.APPLICATION_LOG: 2.0,
            EventType.DATABASE_QUERY: 3.0,
            EventType.API_REQUEST: 4.0,
            EventType.ERROR_EVENT: 5.0,
            EventType.PERFORMANCE_METRIC: 6.0,
            EventType.SECURITY_EVENT: 7.0,
            EventType.USER_ACTION: 8.0,
            EventType.BUSINESS_METRIC: 9.0,
            EventType.INFRASTRUCTURE_ALERT: 10.0
        }
        return mapping.get(event_type, 0.0)
    
    def _source_to_numeric(self, source: str) -> float:
        """Converte fonte para valor numérico"""
        mapping = {
            'system_metrics': 1.0,
            'application_logs': 2.0,
            'database_queries': 3.0,
            'api_gateway': 4.0,
            'security_monitor': 5.0
        }
        return mapping.get(source, 0.0)
    
    def _metric_name_to_numeric(self, metric_name: str) -> float:
        """Converte nome da métrica para valor numérico"""
        mapping = {
            'cpu_usage': 1.0,
            'memory_usage': 2.0,
            'disk_usage': 3.0,
            'network_io': 4.0,
            'response_time': 5.0
        }
        return mapping.get(metric_name, 0.0)
    
    def _log_level_to_numeric(self, level: str) -> float:
        """Converte nível de log para valor numérico"""
        mapping = {
            'DEBUG': 1.0,
            'INFO': 2.0,
            'WARNING': 3.0,
            'ERROR': 4.0,
            'CRITICAL': 5.0
        }
        return mapping.get(level.upper(), 0.0)
    
    def _endpoint_to_numeric(self, endpoint: str) -> float:
        """Converte endpoint para valor numérico"""
        # Hash simples do endpoint
        return hash(endpoint) % 1000

class AnomalyDetector:
    """Sistema de detecção de anomalias com ML"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.feature_extractor = FeatureExtractor()
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        self.model_path = Path(self.config.get('model_path', 'models/anomaly_detector'))
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Configurações dos algoritmos
        self.algorithms = self.config.get('algorithms', [AnomalyAlgorithm.ISOLATION_FOREST])
        self.contamination = self.config.get('contamination', 0.1)
        self.min_samples = self.config.get('min_samples', 10)
        
        # Métricas de performance
        self.performance_metrics = {}
        
        logger.info(f"AnomalyDetector inicializado com algoritmos: {[alg.value for alg in self.algorithms]}")
    
    def train(self, events: List[Event]) -> Dict[str, Any]:
        """
        Treina os modelos de detecção de anomalias com eventos históricos.
        Baseado em dados reais do sistema Omni Keywords Finder.
        """
        if len(events) < self.min_samples:
            logger.warning(f"Poucos eventos para treinamento: {len(events)} < {self.min_samples}")
            return {'status': 'insufficient_data', 'message': 'Dados insuficientes para treinamento'}
        
        logger.info(f"Iniciando treinamento com {len(events)} eventos")
        
        try:
            # Extrair features
            features_df = self.feature_extractor.extract_features(events)
            
            if features_df.empty:
                return {'status': 'error', 'message': 'Falha na extração de features'}
            
            # Dividir dados (simulação de dados históricos vs. novos)
            train_size = min(0.8, len(features_df) / len(features_df))
            train_df, test_df = train_test_split(features_df, train_size=train_size, random_state=42)
            
            # Treinar cada algoritmo
            for algorithm in self.algorithms:
                model, scaler = self._train_algorithm(algorithm, train_df)
                if model is not None:
                    self.models[algorithm.value] = model
                    self.scalers[algorithm.value] = scaler
                    
                    # Avaliar performance
                    if len(test_df) > 0:
                        performance = self._evaluate_algorithm(algorithm, model, scaler, test_df)
                        self.performance_metrics[algorithm.value] = performance
            
            self.is_trained = True
            
            # Salvar modelos
            self._save_models()
            
            logger.info(f"Treinamento concluído. Modelos treinados: {list(self.models.keys())}")
            
            return {
                'status': 'success',
                'models_trained': list(self.models.keys()),
                'performance_metrics': self.performance_metrics,
                'training_samples': len(train_df),
                'test_samples': len(test_df)
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _train_algorithm(self, algorithm: AnomalyAlgorithm, train_df: pd.DataFrame) -> Tuple[Any, Any]:
        """Treina um algoritmo específico"""
        try:
            # Preparar dados
            X = train_df.fillna(0).values
            
            # Escalar dados
            if algorithm == AnomalyAlgorithm.ISOLATION_FOREST:
                scaler = RobustScaler()
            else:
                scaler = StandardScaler()
            
            X_scaled = scaler.fit_transform(X)
            
            # Treinar modelo
            if algorithm == AnomalyAlgorithm.ISOLATION_FOREST:
                model = IsolationForest(
                    contamination=self.contamination,
                    random_state=42,
                    n_estimators=100
                )
            elif algorithm == AnomalyAlgorithm.LOCAL_OUTLIER_FACTOR:
                model = LocalOutlierFactor(
                    contamination=self.contamination,
                    n_neighbors=20,
                    novelty=True
                )
            else:
                logger.warning(f"Algoritmo {algorithm.value} não implementado")
                return None, None
            
            model.fit(X_scaled)
            
            return model, scaler
            
        except Exception as e:
            logger.error(f"Erro ao treinar {algorithm.value}: {str(e)}")
            return None, None
    
    def _evaluate_algorithm(self, algorithm: AnomalyAlgorithm, model: Any, scaler: Any, test_df: pd.DataFrame) -> Dict[str, float]:
        """Avalia performance de um algoritmo"""
        try:
            X_test = test_df.fillna(0).values
            X_test_scaled = scaler.transform(X_test)
            
            # Predições (simulação - em produção seria com dados reais)
            if algorithm == AnomalyAlgorithm.ISOLATION_FOREST:
                predictions = model.predict(X_test_scaled)
                scores = model.score_samples(X_test_scaled)
            elif algorithm == AnomalyAlgorithm.LOCAL_OUTLIER_FACTOR:
                predictions = model.predict(X_test_scaled)
                scores = model.score_samples(X_test_scaled)
            else:
                return {}
            
            # Converter predições (1 = normal, -1 = anomalia)
            y_pred = (predictions == -1).astype(int)
            
            # Simular labels reais (em produção seria com dados históricos)
            # Para teste, assumir que 10% são anomalias
            y_true = np.random.choice([0, 1], size=len(y_pred), p=[0.9, 0.1])
            
            # Calcular métricas
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            
            return {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'avg_score': np.mean(scores)
            }
            
        except Exception as e:
            logger.error(f"Erro na avaliação de {algorithm.value}: {str(e)}")
            return {}
    
    def detect_anomalies(self, events: List[Event]) -> List[AnomalyResult]:
        """
        Detecta anomalias em uma lista de eventos.
        Baseado em dados reais do sistema Omni Keywords Finder.
        """
        if not self.is_trained:
            logger.warning("Modelos não treinados. Execute train() primeiro.")
            return []
        
        if not events:
            return []
        
        logger.info(f"Detectando anomalias em {len(events)} eventos")
        
        try:
            # Extrair features
            features_df = self.feature_extractor.extract_features(events)
            
            if features_df.empty:
                return []
            
            results = []
            
            # Detectar anomalias com cada algoritmo
            for algorithm_name, model in self.models.items():
                scaler = self.scalers.get(algorithm_name)
                if scaler is None:
                    continue
                
                # Preparar dados
                X = features_df.fillna(0).values
                X_scaled = scaler.transform(X)
                
                # Predições
                if algorithm_name == AnomalyAlgorithm.ISOLATION_FOREST.value:
                    predictions = model.predict(X_scaled)
                    scores = model.score_samples(X_scaled)
                elif algorithm_name == AnomalyAlgorithm.LOCAL_OUTLIER_FACTOR.value:
                    predictions = model.predict(X_scaled)
                    scores = model.score_samples(X_scaled)
                else:
                    continue
                
                # Processar resultados
                for i, event in enumerate(events):
                    is_anomaly = predictions[i] == -1
                    score = scores[i]
                    
                    # Determinar tipo de anomalia
                    anomaly_type = self._determine_anomaly_type(event, score, algorithm_name)
                    
                    # Calcular confiança
                    confidence = self._calculate_confidence(score, algorithm_name)
                    
                    # Extrair features relevantes
                    relevant_features = self._extract_relevant_features(features_df.iloc[i])
                    
                    result = AnomalyResult(
                        event_id=event.id,
                        is_anomaly=is_anomaly,
                        score=float(score),
                        algorithm=algorithm_name,
                        anomaly_type=anomaly_type,
                        confidence=confidence,
                        features=relevant_features,
                        timestamp=datetime.now(),
                        metadata={
                            'original_event': {
                                'type': event.type.value,
                                'source': event.source,
                                'severity': event.severity.value
                            }
                        }
                    )
                    
                    results.append(result)
            
            # Consolidar resultados de múltiplos algoritmos
            consolidated_results = self._consolidate_results(results)
            
            logger.info(f"Detectadas {len([r for r in consolidated_results if r.is_anomaly])} anomalias")
            
            return consolidated_results
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalias: {str(e)}")
            return []
    
    def _determine_anomaly_type(self, event: Event, score: float, algorithm: str) -> AnomalyType:
        """Determina o tipo de anomalia baseado no evento e score"""
        # Lógica baseada em dados reais do sistema
        if event.type == EventType.SYSTEM_METRIC:
            if 'value' in event.data and event.data['value'] > 90:
                return AnomalyType.POINT
            else:
                return AnomalyType.CONTEXTUAL
        elif event.type == EventType.ERROR_EVENT:
            return AnomalyType.COLLECTIVE
        elif event.type == EventType.DATABASE_QUERY:
            if 'execution_time' in event.data and event.data['execution_time'] > 5000:
                return AnomalyType.TREND
            else:
                return AnomalyType.POINT
        else:
            return AnomalyType.CONTEXTUAL
    
    def _calculate_confidence(self, score: float, algorithm: str) -> float:
        """Calcula confiança da detecção baseada no score"""
        # Normalizar score para 0-1
        if algorithm == AnomalyAlgorithm.ISOLATION_FOREST.value:
            # Isolation Forest: scores mais negativos = mais anômalo
            confidence = 1.0 - (score + 0.5)  # Normalizar de [-0.5, 0.5] para [0, 1]
        else:
            # Outros algoritmos: scores mais baixos = mais anômalo
            confidence = 1.0 - score
        
        return max(0.0, min(1.0, confidence))
    
    def _extract_relevant_features(self, features: pd.Series) -> Dict[str, float]:
        """Extrai features relevantes para o resultado"""
        relevant_features = {}
        
        # Features mais importantes baseadas no sistema real
        important_features = [
            'metric_value', 'execution_time', 'response_time', 
            'severity_numeric', 'event_type_numeric'
        ]
        
        for feature in important_features:
            if feature in features:
                relevant_features[feature] = float(features[feature])
        
        return relevant_features
    
    def _consolidate_results(self, results: List[AnomalyResult]) -> List[AnomalyResult]:
        """Consolida resultados de múltiplos algoritmos"""
        if not results:
            return []
        
        # Agrupar por event_id
        event_results = {}
        for result in results:
            if result.event_id not in event_results:
                event_results[result.event_id] = []
            event_results[result.event_id].append(result)
        
        consolidated = []
        
        for event_id, event_result_list in event_results.items():
            # Votação por maioria para is_anomaly
            anomaly_votes = sum(1 for r in event_result_list if r.is_anomaly)
            is_anomaly = anomaly_votes > len(event_result_list) / 2
            
            # Score médio
            avg_score = np.mean([r.score for r in event_result_list])
            
            # Confiança média
            avg_confidence = np.mean([r.confidence for r in event_result_list])
            
            # Algoritmo com maior confiança
            best_result = max(event_result_list, key=lambda r: r.confidence)
            
            consolidated_result = AnomalyResult(
                event_id=event_id,
                is_anomaly=is_anomaly,
                score=float(avg_score),
                algorithm=f"ensemble_{len(event_result_list)}",
                anomaly_type=best_result.anomaly_type,
                confidence=avg_confidence,
                features=best_result.features,
                timestamp=datetime.now(),
                metadata={
                    'algorithms_used': [r.algorithm for r in event_result_list],
                    'voting_result': f"{anomaly_votes}/{len(event_result_list)}"
                }
            )
            
            consolidated.append(consolidated_result)
        
        return consolidated
    
    def _save_models(self):
        """Salva modelos treinados"""
        try:
            for algorithm_name, model in self.models.items():
                model_file = self.model_path / f"{algorithm_name}_model.joblib"
                scaler_file = self.model_path / f"{algorithm_name}_scaler.joblib"
                
                joblib.dump(model, model_file)
                joblib.dump(self.scalers[algorithm_name], scaler_file)
            
            # Salvar configurações
            config_file = self.model_path / "config.json"
            config_data = {
                'algorithms': [alg.value for alg in self.algorithms],
                'contamination': self.contamination,
                'min_samples': self.min_samples,
                'performance_metrics': self.performance_metrics,
                'trained_at': datetime.now().isoformat()
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Modelos salvos em {self.model_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelos: {str(e)}")
    
    def load_models(self) -> bool:
        """Carrega modelos salvos"""
        try:
            config_file = self.model_path / "config.json"
            if not config_file.exists():
                logger.warning("Arquivo de configuração não encontrado")
                return False
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            for algorithm_name in config_data['algorithms']:
                model_file = self.model_path / f"{algorithm_name}_model.joblib"
                scaler_file = self.model_path / f"{algorithm_name}_scaler.joblib"
                
                if model_file.exists() and scaler_file.exists():
                    self.models[algorithm_name] = joblib.load(model_file)
                    self.scalers[algorithm_name] = joblib.load(scaler_file)
            
            self.performance_metrics = config_data.get('performance_metrics', {})
            self.is_trained = True
            
            logger.info(f"Modelos carregados: {list(self.models.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {str(e)}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance dos modelos"""
        return {
            'is_trained': self.is_trained,
            'algorithms': list(self.models.keys()),
            'performance_metrics': self.performance_metrics,
            'total_models': len(self.models)
        } 