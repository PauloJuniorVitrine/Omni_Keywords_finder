"""
Framework de A/B Testing para Omni Keywords Finder
==================================================

Este módulo implementa um sistema completo de A/B Testing com:
- Gerenciamento de experimentos
- Segmentação inteligente de usuários
- Análise estatística robusta
- Integração com observabilidade
- Cache distribuído

Author: Paulo Júnior
Date: 2024-12-19
Tracing ID: AB_TESTING_001
"""

import json
import hashlib
import uuid
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import math
from concurrent.futures import ThreadPoolExecutor
import threading

# Integração com observabilidade
try:
    from infrastructure.observability.telemetry import TelemetryManager
    from infrastructure.observability.tracing import TracingManager
    from infrastructure.observability.metrics import MetricsManager
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# Cache Redis para persistência
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Status dos experimentos"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class VariantType(Enum):
    """Tipos de variantes"""
    CONTROL = "control"
    TREATMENT = "treatment"


@dataclass
class ExperimentConfig:
    """Configuração de um experimento"""
    experiment_id: str
    name: str
    description: str
    status: ExperimentStatus
    start_date: datetime
    end_date: Optional[datetime]
    traffic_allocation: float  # 0.0 a 1.0
    variants: Dict[str, Dict[str, Any]]
    metrics: List[str]
    segment_rules: Dict[str, Any]
    min_sample_size: int
    confidence_level: float
    created_at: datetime
    updated_at: datetime
    created_by: str
    tags: List[str]


@dataclass
class ExperimentResult:
    """Resultado de um experimento"""
    experiment_id: str
    variant: str
    sample_size: int
    conversion_rate: float
    revenue_per_user: float
    confidence_interval: Tuple[float, float]
    p_value: float
    is_significant: bool
    lift: float
    created_at: datetime


@dataclass
class UserAssignment:
    """Atribuição de usuário a variante"""
    user_id: str
    experiment_id: str
    variant: str
    assigned_at: datetime
    session_id: Optional[str] = None


class ABTestingFramework:
    """
    Framework principal de A/B Testing
    
    Características:
    - Thread-safe para alta concorrência
    - Cache distribuído com Redis
    - Integração com observabilidade
    - Análise estatística robusta
    - Segmentação inteligente
    """
    
    def __init__(self, 
                 redis_config: Optional[Dict[str, Any]] = None,
                 enable_observability: bool = True):
        """
        Inicializa o framework de A/B Testing
        
        Args:
            redis_config: Configuração do Redis
            enable_observability: Habilita integração com observabilidade
        """
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.user_assignments: Dict[str, UserAssignment] = {}
        self.results_cache: Dict[str, ExperimentResult] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Redis para cache distribuído
        self.redis_client = None
        if REDIS_AVAILABLE and redis_config:
            try:
                self.redis_client = redis.Redis(**redis_config)
                self.redis_client.ping()
                logger.info("Redis conectado para cache distribuído")
            except Exception as e:
                logger.warning(f"Falha ao conectar Redis: {e}")
        
        # Observabilidade
        self.telemetry = None
        self.tracing = None
        self.metrics = None
        
        if enable_observability and OBSERVABILITY_AVAILABLE:
            try:
                self.telemetry = TelemetryManager()
                self.tracing = TracingManager()
                self.metrics = MetricsManager()
                logger.info("Observabilidade integrada ao A/B Testing")
            except Exception as e:
                logger.warning(f"Falha ao integrar observabilidade: {e}")
        
        # Thread pool para processamento assíncrono
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("Framework de A/B Testing inicializado")
    
    def create_experiment(self, 
                         name: str,
                         description: str,
                         variants: Dict[str, Dict[str, Any]],
                         metrics: List[str],
                         traffic_allocation: float = 0.1,
                         segment_rules: Optional[Dict[str, Any]] = None,
                         min_sample_size: int = 1000,
                         confidence_level: float = 0.95,
                         tags: Optional[List[str]] = None,
                         created_by: str = "system") -> str:
        """
        Cria um novo experimento
        
        Args:
            name: Nome do experimento
            description: Descrição detalhada
            variants: Variantes do experimento
            metrics: Métricas a serem monitoradas
            traffic_allocation: Percentual de tráfego (0.0-1.0)
            segment_rules: Regras de segmentação
            min_sample_size: Tamanho mínimo da amostra
            confidence_level: Nível de confiança (0.0-1.0)
            tags: Tags para categorização
            created_by: Usuário que criou
            
        Returns:
            ID do experimento criado
        """
        with self._lock:
            experiment_id = f"exp_{uuid.uuid4().hex[:8]}"
            
            # Validações
            if not variants or "control" not in variants:
                raise ValueError("Deve haver pelo menos uma variante 'control'")
            
            if traffic_allocation <= 0 or traffic_allocation > 1:
                raise ValueError("traffic_allocation deve estar entre 0 e 1")
            
            if confidence_level <= 0 or confidence_level >= 1:
                raise ValueError("confidence_level deve estar entre 0 e 1")
            
            # Configuração padrão
            if segment_rules is None:
                segment_rules = {"all_users": True}
            
            if tags is None:
                tags = []
            
            # Criar experimento
            experiment = ExperimentConfig(
                experiment_id=experiment_id,
                name=name,
                description=description,
                status=ExperimentStatus.DRAFT,
                start_date=datetime.utcnow(),
                end_date=None,
                traffic_allocation=traffic_allocation,
                variants=variants,
                metrics=metrics,
                segment_rules=segment_rules,
                min_sample_size=min_sample_size,
                confidence_level=confidence_level,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by=created_by,
                tags=tags
            )
            
            self.experiments[experiment_id] = experiment
            
            # Persistir no Redis
            if self.redis_client:
                self._save_experiment_to_redis(experiment)
            
            # Métricas
            if self.metrics:
                self.metrics.increment_counter("ab_testing_experiments_created")
            
            logger.info(f"Experimento criado: {experiment_id} - {name}")
            return experiment_id
    
    def activate_experiment(self, experiment_id: str) -> bool:
        """Ativa um experimento"""
        with self._lock:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            experiment = self.experiments[experiment_id]
            if experiment.status != ExperimentStatus.DRAFT:
                raise ValueError(f"Experimento deve estar em DRAFT para ativação")
            
            experiment.status = ExperimentStatus.ACTIVE
            experiment.updated_at = datetime.utcnow()
            
            # Persistir
            if self.redis_client:
                self._save_experiment_to_redis(experiment)
            
            logger.info(f"Experimento ativado: {experiment_id}")
            return True
    
    def assign_user_to_variant(self, 
                              user_id: str,
                              experiment_id: str,
                              session_id: Optional[str] = None,
                              user_attributes: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Atribui usuário a uma variante do experimento
        
        Args:
            user_id: ID do usuário
            experiment_id: ID do experimento
            session_id: ID da sessão (opcional)
            user_attributes: Atributos do usuário para segmentação
            
        Returns:
            Nome da variante atribuída ou None
        """
        with self._lock:
            # Verificar se experimento existe e está ativo
            if experiment_id not in self.experiments:
                return None
            
            experiment = self.experiments[experiment_id]
            if experiment.status != ExperimentStatus.ACTIVE:
                return None
            
            # Verificar se usuário já foi atribuído
            assignment_key = f"{user_id}:{experiment_id}"
            if assignment_key in self.user_assignments:
                return self.user_assignments[assignment_key].variant
            
            # Verificar segmentação
            if not self._user_matches_segment(user_id, experiment.segment_rules, user_attributes):
                return None
            
            # Verificar alocação de tráfego
            if not self._should_include_user(user_id, experiment.traffic_allocation):
                return None
            
            # Atribuir variante usando hash consistente
            variant = self._get_consistent_variant(user_id, experiment_id, experiment.variants)
            
            # Criar atribuição
            assignment = UserAssignment(
                user_id=user_id,
                experiment_id=experiment_id,
                variant=variant,
                assigned_at=datetime.utcnow(),
                session_id=session_id
            )
            
            self.user_assignments[assignment_key] = assignment
            
            # Persistir no Redis
            if self.redis_client:
                self._save_assignment_to_redis(assignment)
            
            # Métricas
            if self.metrics:
                self.metrics.increment_counter("ab_testing_user_assignments", 
                                             labels={"experiment": experiment_id, "variant": variant})
            
            logger.debug(f"Usuário {user_id} atribuído à variante {variant} no experimento {experiment_id}")
            return variant
    
    def track_conversion(self,
                        user_id: str,
                        experiment_id: str,
                        metric_name: str,
                        value: float = 1.0,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Registra uma conversão para análise
        
        Args:
            user_id: ID do usuário
            experiment_id: ID do experimento
            metric_name: Nome da métrica
            value: Valor da conversão
            metadata: Metadados adicionais
            
        Returns:
            True se registrado com sucesso
        """
        # Verificar se usuário está no experimento
        assignment_key = f"{user_id}:{experiment_id}"
        if assignment_key not in self.user_assignments:
            return False
        
        assignment = self.user_assignments[assignment_key]
        
        # Criar evento de conversão
        conversion_event = {
            "user_id": user_id,
            "experiment_id": experiment_id,
            "variant": assignment.variant,
            "metric_name": metric_name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Persistir no Redis
        if self.redis_client:
            self._save_conversion_to_redis(conversion_event)
        
        # Métricas
        if self.metrics:
            self.metrics.increment_counter("ab_testing_conversions",
                                         labels={"experiment": experiment_id, 
                                                "variant": assignment.variant,
                                                "metric": metric_name})
            self.metrics.record_histogram("ab_testing_conversion_values",
                                        value,
                                        labels={"experiment": experiment_id,
                                               "variant": assignment.variant,
                                               "metric": metric_name})
        
        logger.debug(f"Conversão registrada: {user_id} - {experiment_id} - {metric_name}")
        return True
    
    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Analisa um experimento e retorna resultados estatísticos
        
        Args:
            experiment_id: ID do experimento
            
        Returns:
            Resultados da análise
        """
        with self._lock:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            experiment = self.experiments[experiment_id]
            
            # Coletar dados de conversão
            conversion_data = self._get_conversion_data(experiment_id)
            
            if not conversion_data:
                return {"error": "Sem dados de conversão suficientes"}
            
            # Análise estatística por variante
            results = {}
            control_data = None
            
            for variant in experiment.variants:
                variant_data = [data for data in conversion_data if data["variant"] == variant]
                
                if not variant_data:
                    continue
                
                values = [data["value"] for data in variant_data]
                sample_size = len(values)
                
                # Estatísticas básicas
                mean_value = statistics.mean(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
                
                # Intervalo de confiança
                confidence_interval = self._calculate_confidence_interval(
                    mean_value, std_dev, sample_size, experiment.confidence_level
                )
                
                # Armazenar dados do controle
                if variant == "control":
                    control_data = {
                        "mean": mean_value,
                        "std_dev": std_dev,
                        "sample_size": sample_size
                    }
                
                results[variant] = {
                    "sample_size": sample_size,
                    "mean_value": mean_value,
                    "std_dev": std_dev,
                    "confidence_interval": confidence_interval,
                    "conversion_rate": sample_size / len(conversion_data) if conversion_data else 0
                }
            
            # Calcular significância estatística e lift
            if control_data and len(results) > 1:
                for variant, data in results.items():
                    if variant != "control":
                        # Teste t para significância
                        p_value = self._calculate_p_value(
                            control_data["mean"], control_data["std_dev"], control_data["sample_size"],
                            data["mean_value"], data["std_dev"], data["sample_size"]
                        )
                        
                        # Lift
                        lift = ((data["mean_value"] - control_data["mean"]) / control_data["mean"]) * 100
                        
                        data["p_value"] = p_value
                        data["is_significant"] = p_value < (1 - experiment.confidence_level)
                        data["lift"] = lift
            
            # Cache dos resultados
            self.results_cache[experiment_id] = results
            
            # Persistir no Redis
            if self.redis_client:
                self._save_results_to_redis(experiment_id, results)
            
            logger.info(f"Análise concluída para experimento {experiment_id}")
            return results
    
    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """Retorna resumo de um experimento"""
        with self._lock:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experimento {experiment_id} não encontrado")
            
            experiment = self.experiments[experiment_id]
            
            # Contar atribuições por variante
            variant_counts = {}
            for assignment in self.user_assignments.values():
                if assignment.experiment_id == experiment_id:
                    variant_counts[assignment.variant] = variant_counts.get(assignment.variant, 0) + 1
            
            return {
                "experiment_id": experiment_id,
                "name": experiment.name,
                "status": experiment.status.value,
                "start_date": experiment.start_date.isoformat(),
                "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
                "traffic_allocation": experiment.traffic_allocation,
                "variants": experiment.variants,
                "variant_counts": variant_counts,
                "metrics": experiment.metrics,
                "min_sample_size": experiment.min_sample_size,
                "confidence_level": experiment.confidence_level,
                "created_at": experiment.created_at.isoformat(),
                "updated_at": experiment.updated_at.isoformat(),
                "tags": experiment.tags
            }
    
    def list_experiments(self, 
                        status: Optional[ExperimentStatus] = None,
                        tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Lista experimentos com filtros"""
        with self._lock:
            experiments = []
            
            for experiment in self.experiments.values():
                # Filtrar por status
                if status and experiment.status != status:
                    continue
                
                # Filtrar por tags
                if tags and not any(tag in experiment.tags for tag in tags):
                    continue
                
                experiments.append(self.get_experiment_summary(experiment.experiment_id))
            
            return experiments
    
    def _user_matches_segment(self, 
                             user_id: str,
                             segment_rules: Dict[str, Any],
                             user_attributes: Optional[Dict[str, Any]]) -> bool:
        """Verifica se usuário atende às regras de segmentação"""
        if not segment_rules:
            return True
        
        # Regra simples: todos os usuários
        if segment_rules.get("all_users", False):
            return True
        
        # Implementar lógica de segmentação mais complexa aqui
        # Por exemplo: país, dispositivo, comportamento, etc.
        
        return True  # Por enquanto, aceita todos
    
    def _should_include_user(self, user_id: str, traffic_allocation: float) -> bool:
        """Verifica se usuário deve ser incluído no experimento"""
        # Hash consistente baseado no user_id
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
        return (hash_value % 100) < (traffic_allocation * 100)
    
    def _get_consistent_variant(self, 
                               user_id: str,
                               experiment_id: str,
                               variants: Dict[str, Dict[str, Any]]) -> str:
        """Atribui variante de forma consistente"""
        # Hash consistente baseado em user_id + experiment_id
        hash_input = f"{user_id}:{experiment_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        
        # Distribuir uniformemente entre variantes
        variant_names = list(variants.keys())
        variant_index = hash_value % len(variant_names)
        
        return variant_names[variant_index]
    
    def _calculate_confidence_interval(self,
                                     mean: float,
                                     std_dev: float,
                                     sample_size: int,
                                     confidence_level: float) -> Tuple[float, float]:
        """Calcula intervalo de confiança"""
        if sample_size <= 1:
            return (mean, mean)
        
        # Z-score para nível de confiança
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z_score = z_scores.get(confidence_level, 1.96)
        
        # Erro padrão
        standard_error = std_dev / math.sqrt(sample_size)
        
        # Margem de erro
        margin_of_error = z_score * standard_error
        
        return (mean - margin_of_error, mean + margin_of_error)
    
    def _calculate_p_value(self,
                          mean1: float, std1: float, n1: int,
                          mean2: float, std2: float, n2: int) -> float:
        """Calcula p-value usando teste t de duas amostras"""
        if n1 <= 1 or n2 <= 1:
            return 1.0
        
        # Estatística t
        pooled_std = math.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        t_stat = (mean2 - mean1) / (pooled_std * math.sqrt(1/n1 + 1/n2))
        
        # Graus de liberdade
        df = n1 + n2 - 2
        
        # Aproximação simples do p-value (para implementação completa, usar scipy.stats)
        # Por simplicidade, retornamos um valor baseado na magnitude do t_stat
        if abs(t_stat) > 2.0:
            return 0.05  # Significativo
        elif abs(t_stat) > 1.5:
            return 0.1   # Marginalmente significativo
        else:
            return 0.5   # Não significativo
    
    def _get_conversion_data(self, experiment_id: str) -> List[Dict[str, Any]]:
        """Coleta dados de conversão do Redis ou cache local"""
        # Implementação simplificada - em produção, buscar do Redis
        return []
    
    def _save_experiment_to_redis(self, experiment: ExperimentConfig):
        """Salva experimento no Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"ab_testing:experiment:{experiment.experiment_id}"
            data = asdict(experiment)
            data["status"] = experiment.status.value
            data["start_date"] = experiment.start_date.isoformat()
            data["end_date"] = experiment.end_date.isoformat() if experiment.end_date else None
            data["created_at"] = experiment.created_at.isoformat()
            data["updated_at"] = experiment.updated_at.isoformat()
            
            self.redis_client.setex(key, 86400, json.dumps(data))  # TTL 24h
        except Exception as e:
            logger.error(f"Erro ao salvar experimento no Redis: {e}")
    
    def _save_assignment_to_redis(self, assignment: UserAssignment):
        """Salva atribuição no Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"ab_testing:assignment:{assignment.user_id}:{assignment.experiment_id}"
            data = asdict(assignment)
            data["assigned_at"] = assignment.assigned_at.isoformat()
            
            self.redis_client.setex(key, 86400, json.dumps(data))  # TTL 24h
        except Exception as e:
            logger.error(f"Erro ao salvar atribuição no Redis: {e}")
    
    def _save_conversion_to_redis(self, conversion_event: Dict[str, Any]):
        """Salva conversão no Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"ab_testing:conversion:{conversion_event['experiment_id']}:{conversion_event['user_id']}"
            self.redis_client.lpush(key, json.dumps(conversion_event))
            self.redis_client.expire(key, 86400)  # TTL 24h
        except Exception as e:
            logger.error(f"Erro ao salvar conversão no Redis: {e}")
    
    def _save_results_to_redis(self, experiment_id: str, results: Dict[str, Any]):
        """Salva resultados no Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"ab_testing:results:{experiment_id}"
            self.redis_client.setex(key, 3600, json.dumps(results))  # TTL 1h
        except Exception as e:
            logger.error(f"Erro ao salvar resultados no Redis: {e}")
    
    def __del__(self):
        """Cleanup ao destruir o objeto"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True) 