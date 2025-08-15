"""
Sistema de Métricas de Geração de Documentação Enterprise
Tracing ID: DOC_GENERATION_METRICS_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa um sistema completo de métricas para monitoramento
e análise da geração de documentação enterprise, incluindo qualidade,
tempo, custo e consumo de tokens.
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Tipos de métricas suportadas."""
    QUALITY = "quality"
    TIME = "time"
    COST = "cost"
    TOKENS = "tokens"
    PERFORMANCE = "performance"
    COVERAGE = "coverage"

class QualityMetric(Enum):
    """Métricas de qualidade específicas."""
    COMPLETENESS = "completeness"
    COHERENCE = "coherence"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    DOC_QUALITY_SCORE = "doc_quality_score"
    READABILITY = "readability"
    ACCURACY = "accuracy"

class TimeMetric(Enum):
    """Métricas de tempo específicas."""
    GENERATION_TIME = "generation_time"
    PROCESSING_TIME = "processing_time"
    VALIDATION_TIME = "validation_time"
    TOTAL_TIME = "total_time"

class CostMetric(Enum):
    """Métricas de custo específicas."""
    TOKEN_COST = "token_cost"
    API_COST = "api_cost"
    STORAGE_COST = "storage_cost"
    TOTAL_COST = "total_cost"

@dataclass
class MetricData:
    """Estrutura de dados para uma métrica individual."""
    metric_type: MetricType
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class GenerationSession:
    """Sessão de geração de documentação."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    file_path: Optional[str] = None
    module_name: Optional[str] = None
    function_name: Optional[str] = None
    metrics: List[MetricData] = None
    status: str = "running"
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        data['metrics'] = [metric.to_dict() for metric in self.metrics]
        return data

class DocGenerationMetrics:
    """
    Sistema principal de métricas de geração de documentação.
    
    Gerencia coleta, armazenamento e análise de métricas relacionadas
    à geração de documentação enterprise.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o sistema de métricas.
        
        Args:
            config: Configuração do sistema
        """
        self.config = config or {}
        self.sessions: Dict[str, GenerationSession] = {}
        self.metrics_history: List[MetricData] = []
        self.analysis_cache: Dict[str, Any] = {}
        
        # Configurações padrão
        self.max_history_size = self.config.get('max_history_size', 10000)
        self.storage_path = self.config.get('storage_path', 'logs/metrics')
        self.enable_persistence = self.config.get('enable_persistence', True)
        
        # Criar diretório de armazenamento se necessário
        if self.enable_persistence:
            Path(self.storage_path).mkdir(parents=True, exist_ok=True)
    
    def start_session(self, file_path: str = None, module_name: str = None, 
                     function_name: str = None) -> str:
        """
        Inicia uma nova sessão de geração.
        
        Args:
            file_path: Caminho do arquivo sendo documentado
            module_name: Nome do módulo
            function_name: Nome da função
            
        Returns:
            ID da sessão criada
        """
        session_id = self._generate_session_id()
        session = GenerationSession(
            session_id=session_id,
            start_time=datetime.utcnow(),
            file_path=file_path,
            module_name=module_name,
            function_name=function_name
        )
        
        self.sessions[session_id] = session
        logger.info(f"Sessão iniciada: {session_id} para {file_path or module_name}")
        
        return session_id
    
    def end_session(self, session_id: str, status: str = "completed", 
                   error_message: str = None) -> bool:
        """
        Finaliza uma sessão de geração.
        
        Args:
            session_id: ID da sessão
            status: Status final da sessão
            error_message: Mensagem de erro se houver
            
        Returns:
            True se a sessão foi finalizada com sucesso
        """
        if session_id not in self.sessions:
            logger.warning(f"Sessão não encontrada: {session_id}")
            return False
        
        session = self.sessions[session_id]
        session.end_time = datetime.utcnow()
        session.status = status
        session.error_message = error_message
        
        logger.info(f"Sessão finalizada: {session_id} - {status}")
        
        # Persistir sessão se habilitado
        if self.enable_persistence:
            self._persist_session(session)
        
        return True
    
    def add_metric(self, session_id: str, metric_type: MetricType, 
                  metric_name: str, value: float, unit: str = "", 
                  metadata: Dict[str, Any] = None) -> bool:
        """
        Adiciona uma métrica a uma sessão.
        
        Args:
            session_id: ID da sessão
            metric_type: Tipo da métrica
            metric_name: Nome da métrica
            value: Valor da métrica
            unit: Unidade da métrica
            metadata: Metadados adicionais
            
        Returns:
            True se a métrica foi adicionada com sucesso
        """
        if session_id not in self.sessions:
            logger.warning(f"Sessão não encontrada: {session_id}")
            return False
        
        metadata = metadata or {}
        metric = MetricData(
            metric_type=metric_type,
            metric_name=metric_name,
            value=value,
            unit=unit,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        
        session = self.sessions[session_id]
        session.metrics.append(metric)
        self.metrics_history.append(metric)
        
        # Limpar histórico se necessário
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
        
        logger.debug(f"Métrica adicionada: {session_id} - {metric_name}: {value}")
        return True
    
    def get_session_metrics(self, session_id: str) -> List[MetricData]:
        """
        Obtém todas as métricas de uma sessão.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Lista de métricas da sessão
        """
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id].metrics
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Obtém resumo de uma sessão.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Resumo da sessão
        """
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        summary = session.to_dict()
        
        # Calcular estatísticas das métricas
        if session.metrics:
            values = [m.value for m in session.metrics]
            summary['statistics'] = {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values)
            }
        
        return summary
    
    def _generate_session_id(self) -> str:
        """Gera ID único para sessão."""
        timestamp = datetime.utcnow().isoformat()
        random_component = str(hash(timestamp + str(len(self.sessions))))
        return f"session_{timestamp}_{random_component}"
    
    def _persist_session(self, session: GenerationSession) -> None:
        """Persiste sessão em arquivo."""
        try:
            file_path = Path(self.storage_path) / f"{session.session_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao persistir sessão {session.session_id}: {e}")

class MetricsCollector:
    """
    Coletor especializado de métricas.
    
    Responsável por coletar métricas específicas durante o processo
    de geração de documentação.
    """
    
    def __init__(self, metrics_system: DocGenerationMetrics):
        """
        Inicializa o coletor.
        
        Args:
            metrics_system: Sistema de métricas principal
        """
        self.metrics_system = metrics_system
        self.current_session_id: Optional[str] = None
        self.start_times: Dict[str, float] = {}
    
    def start_collection(self, file_path: str = None, module_name: str = None, 
                        function_name: str = None) -> str:
        """
        Inicia coleta de métricas.
        
        Args:
            file_path: Caminho do arquivo
            module_name: Nome do módulo
            function_name: Nome da função
            
        Returns:
            ID da sessão
        """
        self.current_session_id = self.metrics_system.start_session(
            file_path, module_name, function_name
        )
        return self.current_session_id
    
    def end_collection(self, status: str = "completed", error_message: str = None) -> bool:
        """
        Finaliza coleta de métricas.
        
        Args:
            status: Status final
            error_message: Mensagem de erro
            
        Returns:
            True se finalizado com sucesso
        """
        if not self.current_session_id:
            return False
        
        success = self.metrics_system.end_session(
            self.current_session_id, status, error_message
        )
        self.current_session_id = None
        self.start_times.clear()
        return success
    
    def start_timer(self, timer_name: str) -> None:
        """
        Inicia um timer específico.
        
        Args:
            timer_name: Nome do timer
        """
        self.start_times[timer_name] = time.time()
    
    def end_timer(self, timer_name: str, metric_name: str = None) -> Optional[float]:
        """
        Finaliza um timer e registra a métrica.
        
        Args:
            timer_name: Nome do timer
            metric_name: Nome da métrica (opcional)
            
        Returns:
            Tempo decorrido em segundos
        """
        if timer_name not in self.start_times:
            return None
        
        elapsed_time = time.time() - self.start_times[timer_name]
        metric_name = metric_name or f"{timer_name}_time"
        
        if self.current_session_id:
            self.metrics_system.add_metric(
                self.current_session_id,
                MetricType.TIME,
                metric_name,
                elapsed_time,
                "seconds"
            )
        
        del self.start_times[timer_name]
        return elapsed_time
    
    def record_quality_metric(self, metric_name: str, value: float, 
                            metadata: Dict[str, Any] = None) -> None:
        """
        Registra métrica de qualidade.
        
        Args:
            metric_name: Nome da métrica
            value: Valor da métrica
            metadata: Metadados adicionais
        """
        if self.current_session_id:
            self.metrics_system.add_metric(
                self.current_session_id,
                MetricType.QUALITY,
                metric_name,
                value,
                "score",
                metadata
            )
    
    def record_cost_metric(self, metric_name: str, value: float, 
                          currency: str = "USD", metadata: Dict[str, Any] = None) -> None:
        """
        Registra métrica de custo.
        
        Args:
            metric_name: Nome da métrica
            value: Valor do custo
            currency: Moeda
            metadata: Metadados adicionais
        """
        if self.current_session_id:
            metadata = metadata or {}
            metadata['currency'] = currency
            
            self.metrics_system.add_metric(
                self.current_session_id,
                MetricType.COST,
                metric_name,
                value,
                currency,
                metadata
            )
    
    def record_token_metric(self, metric_name: str, value: int, 
                           metadata: Dict[str, Any] = None) -> None:
        """
        Registra métrica de tokens.
        
        Args:
            metric_name: Nome da métrica
            value: Número de tokens
            metadata: Metadados adicionais
        """
        if self.current_session_id:
            self.metrics_system.add_metric(
                self.current_session_id,
                MetricType.TOKENS,
                metric_name,
                value,
                "tokens",
                metadata
            )

class MetricsAnalyzer:
    """
    Analisador de métricas de geração.
    
    Responsável por analisar métricas coletadas e gerar insights
    sobre performance, qualidade e otimizações.
    """
    
    def __init__(self, metrics_system: DocGenerationMetrics):
        """
        Inicializa o analisador.
        
        Args:
            metrics_system: Sistema de métricas principal
        """
        self.metrics_system = metrics_system
    
    def analyze_session(self, session_id: str) -> Dict[str, Any]:
        """
        Analisa uma sessão específica.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Análise detalhada da sessão
        """
        if session_id not in self.metrics_system.sessions:
            return {}
        
        session = self.metrics_system.sessions[session_id]
        metrics = session.metrics
        
        analysis = {
            'session_id': session_id,
            'file_path': session.file_path,
            'module_name': session.module_name,
            'function_name': session.function_name,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'status': session.status,
            'duration': self._calculate_duration(session),
            'metrics_summary': self._summarize_metrics(metrics),
            'performance_analysis': self._analyze_performance(metrics),
            'quality_analysis': self._analyze_quality(metrics),
            'cost_analysis': self._analyze_cost(metrics),
            'recommendations': self._generate_recommendations(metrics, session)
        }
        
        return analysis
    
    def analyze_trends(self, days: int = 30, metric_type: MetricType = None) -> Dict[str, Any]:
        """
        Analisa tendências das métricas.
        
        Args:
            days: Número de dias para análise
            metric_type: Tipo de métrica específica
            
        Returns:
            Análise de tendências
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_metrics = [
            m for m in self.metrics_system.metrics_history
            if m.timestamp >= cutoff_date
        ]
        
        if metric_type:
            recent_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
        
        analysis = {
            'period_days': days,
            'total_metrics': len(recent_metrics),
            'metric_type': metric_type.value if metric_type else "all",
            'trends': self._calculate_trends(recent_metrics),
            'statistics': self._calculate_statistics(recent_metrics),
            'anomalies': self._detect_anomalies(recent_metrics),
            'optimization_opportunities': self._identify_optimizations(recent_metrics)
        }
        
        return analysis
    
    def generate_report(self, session_ids: List[str] = None, 
                       include_trends: bool = True) -> Dict[str, Any]:
        """
        Gera relatório completo de métricas.
        
        Args:
            session_ids: IDs de sessões específicas
            include_trends: Incluir análise de tendências
            
        Returns:
            Relatório completo
        """
        sessions_to_analyze = session_ids or list(self.metrics_system.sessions.keys())
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'total_sessions': len(sessions_to_analyze),
            'sessions_analysis': {},
            'overall_statistics': {},
            'trends_analysis': None,
            'recommendations': []
        }
        
        # Analisar cada sessão
        for session_id in sessions_to_analyze:
            if session_id in self.metrics_system.sessions:
                report['sessions_analysis'][session_id] = self.analyze_session(session_id)
        
        # Estatísticas gerais
        all_metrics = []
        for session in self.metrics_system.sessions.values():
            all_metrics.extend(session.metrics)
        
        report['overall_statistics'] = self._calculate_overall_statistics(all_metrics)
        
        # Análise de tendências
        if include_trends:
            report['trends_analysis'] = self.analyze_trends()
        
        # Recomendações gerais
        report['recommendations'] = self._generate_global_recommendations(all_metrics)
        
        return report
    
    def _calculate_duration(self, session: GenerationSession) -> Optional[float]:
        """Calcula duração da sessão."""
        if not session.end_time:
            return None
        return (session.end_time - session.start_time).total_seconds()
    
    def _summarize_metrics(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Resume métricas por tipo."""
        summary = {}
        for metric_type in MetricType:
            type_metrics = [m for m in metrics if m.metric_type == metric_type]
            if type_metrics:
                values = [m.value for m in type_metrics]
                summary[metric_type.value] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values)
                }
        return summary
    
    def _analyze_performance(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Analisa métricas de performance."""
        time_metrics = [m for m in metrics if m.metric_type == MetricType.TIME]
        
        analysis = {
            'total_time': sum(m.value for m in time_metrics),
            'time_breakdown': {},
            'performance_score': 0.0
        }
        
        for metric in time_metrics:
            analysis['time_breakdown'][metric.metric_name] = metric.value
        
        # Calcular score de performance (quanto menor o tempo, melhor)
        if analysis['total_time'] > 0:
            # Score baseado em tempo total (assumindo que < 60s é excelente)
            analysis['performance_score'] = max(0, 100 - (analysis['total_time'] / 60) * 100)
        
        return analysis
    
    def _analyze_quality(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Analisa métricas de qualidade."""
        quality_metrics = [m for m in metrics if m.metric_type == MetricType.QUALITY]
        
        analysis = {
            'overall_quality_score': 0.0,
            'quality_breakdown': {},
            'quality_issues': []
        }
        
        if quality_metrics:
            values = [m.value for m in quality_metrics]
            analysis['overall_quality_score'] = statistics.mean(values)
            
            for metric in quality_metrics:
                analysis['quality_breakdown'][metric.metric_name] = metric.value
                
                # Identificar problemas de qualidade
                if metric.value < 0.7:  # Threshold de qualidade
                    analysis['quality_issues'].append({
                        'metric': metric.metric_name,
                        'value': metric.value,
                        'threshold': 0.7
                    })
        
        return analysis
    
    def _analyze_cost(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Analisa métricas de custo."""
        cost_metrics = [m for m in metrics if m.metric_type == MetricType.COST]
        
        analysis = {
            'total_cost': sum(m.value for m in cost_metrics),
            'cost_breakdown': {},
            'cost_efficiency': 0.0
        }
        
        for metric in cost_metrics:
            analysis['cost_breakdown'][metric.metric_name] = metric.value
        
        # Calcular eficiência de custo
        token_metrics = [m for m in metrics if m.metric_type == MetricType.TOKENS]
        total_tokens = sum(m.value for m in token_metrics)
        
        if total_tokens > 0:
            analysis['cost_efficiency'] = analysis['total_cost'] / total_tokens
        
        return analysis
    
    def _calculate_trends(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Calcula tendências das métricas."""
        if not metrics:
            return {}
        
        # Agrupar por dia
        daily_metrics = {}
        for metric in metrics:
            date_key = metric.timestamp.date().isoformat()
            if date_key not in daily_metrics:
                daily_metrics[date_key] = []
            daily_metrics[date_key].append(metric.value)
        
        # Calcular médias diárias
        daily_averages = {}
        for date, values in daily_metrics.items():
            daily_averages[date] = statistics.mean(values)
        
        # Calcular tendência linear simples
        dates = sorted(daily_averages.keys())
        values = [daily_averages[date] for date in dates]
        
        if len(values) > 1:
            # Calcular inclinação da linha de tendência
            x_values = list(range(len(values)))
            slope = self._calculate_slope(x_values, values)
            
            trend = {
                'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                'slope': slope,
                'daily_averages': daily_averages,
                'volatility': statistics.stdev(values) if len(values) > 1 else 0
            }
        else:
            trend = {
                'direction': 'insufficient_data',
                'slope': 0,
                'daily_averages': daily_averages,
                'volatility': 0
            }
        
        return trend
    
    def _calculate_slope(self, x_values: List[float], y_values: List[float]) -> float:
        """Calcula inclinação da linha de tendência."""
        n = len(x_values)
        if n < 2:
            return 0
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(value * result for value, result in zip(x_values, y_values))
        sum_x2 = sum(value * value for value in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def _calculate_statistics(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Calcula estatísticas das métricas."""
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'variance': statistics.variance(values) if len(values) > 1 else 0
        }
    
    def _detect_anomalies(self, metrics: List[MetricData]) -> List[Dict[str, Any]]:
        """Detecta anomalias nas métricas."""
        if not metrics:
            return []
        
        values = [m.value for m in metrics]
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        for metric in metrics:
            # Detectar valores que estão a mais de 2 desvios padrão da média
            if std_dev > 0 and abs(metric.value - mean) > 2 * std_dev:
                anomalies.append({
                    'metric': metric.metric_name,
                    'value': metric.value,
                    'expected_range': [mean - 2 * std_dev, mean + 2 * std_dev],
                    'timestamp': metric.timestamp.isoformat()
                })
        
        return anomalies
    
    def _identify_optimizations(self, metrics: List[MetricData]) -> List[Dict[str, Any]]:
        """Identifica oportunidades de otimização."""
        optimizations = []
        
        # Analisar métricas de tempo
        time_metrics = [m for m in metrics if m.metric_type == MetricType.TIME]
        if time_metrics:
            avg_time = statistics.mean([m.value for m in time_metrics])
            if avg_time > 60:  # Mais de 1 minuto
                optimizations.append({
                    'type': 'performance',
                    'issue': 'Tempo de geração alto',
                    'current_value': avg_time,
                    'recommendation': 'Otimizar algoritmos de geração ou usar cache',
                    'priority': 'high'
                })
        
        # Analisar métricas de custo
        cost_metrics = [m for m in metrics if m.metric_type == MetricType.COST]
        if cost_metrics:
            avg_cost = statistics.mean([m.value for m in cost_metrics])
            if avg_cost > 0.1:  # Mais de $0.10 por sessão
                optimizations.append({
                    'type': 'cost',
                    'issue': 'Custo por sessão alto',
                    'current_value': avg_cost,
                    'recommendation': 'Otimizar uso de tokens ou usar modelos mais eficientes',
                    'priority': 'medium'
                })
        
        # Analisar métricas de qualidade
        quality_metrics = [m for m in metrics if m.metric_type == MetricType.QUALITY]
        if quality_metrics:
            avg_quality = statistics.mean([m.value for m in quality_metrics])
            if avg_quality < 0.8:  # Qualidade abaixo de 80%
                optimizations.append({
                    'type': 'quality',
                    'issue': 'Qualidade da documentação baixa',
                    'current_value': avg_quality,
                    'recommendation': 'Melhorar prompts ou adicionar validação adicional',
                    'priority': 'high'
                })
        
        return optimizations
    
    def _generate_recommendations(self, metrics: List[MetricData], 
                                session: GenerationSession) -> List[str]:
        """Gera recomendações específicas para uma sessão."""
        recommendations = []
        
        # Análise de tempo
        time_metrics = [m for m in metrics if m.metric_type == MetricType.TIME]
        if time_metrics:
            total_time = sum(m.value for m in time_metrics)
            if total_time > 120:  # Mais de 2 minutos
                recommendations.append("Considerar otimização de performance para reduzir tempo de geração")
        
        # Análise de qualidade
        quality_metrics = [m for m in metrics if m.metric_type == MetricType.QUALITY]
        if quality_metrics:
            avg_quality = statistics.mean([m.value for m in quality_metrics])
            if avg_quality < 0.7:
                recommendations.append("Revisar qualidade da documentação gerada")
        
        # Análise de custo
        cost_metrics = [m for m in metrics if m.metric_type == MetricType.COST]
        if cost_metrics:
            total_cost = sum(m.value for m in cost_metrics)
            if total_cost > 0.05:  # Mais de $0.05
                recommendations.append("Otimizar uso de tokens para reduzir custos")
        
        return recommendations
    
    def _calculate_overall_statistics(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """Calcula estatísticas gerais de todas as métricas."""
        if not metrics:
            return {}
        
        stats = {}
        for metric_type in MetricType:
            type_metrics = [m for m in metrics if m.metric_type == metric_type]
            if type_metrics:
                values = [m.value for m in type_metrics]
                stats[metric_type.value] = {
                    'total_count': len(values),
                    'average': statistics.mean(values),
                    'total_value': sum(values)
                }
        
        return stats
    
    def _generate_global_recommendations(self, metrics: List[MetricData]) -> List[Dict[str, Any]]:
        """Gera recomendações globais baseadas em todas as métricas."""
        recommendations = []
        
        # Análise geral de performance
        time_metrics = [m for m in metrics if m.metric_type == MetricType.TIME]
        if time_metrics:
            avg_time = statistics.mean([m.value for m in time_metrics])
            if avg_time > 60:
                recommendations.append({
                    'category': 'performance',
                    'title': 'Otimizar Performance',
                    'description': f'Tempo médio de geração ({avg_time:.2f}string_data) está alto',
                    'action': 'Implementar cache e otimizações de algoritmo',
                    'priority': 'high'
                })
        
        # Análise geral de qualidade
        quality_metrics = [m for m in metrics if m.metric_type == MetricType.QUALITY]
        if quality_metrics:
            avg_quality = statistics.mean([m.value for m in quality_metrics])
            if avg_quality < 0.8:
                recommendations.append({
                    'category': 'quality',
                    'title': 'Melhorar Qualidade',
                    'description': f'Qualidade média ({avg_quality:.2f}) está abaixo do ideal',
                    'action': 'Revisar prompts e adicionar validação de qualidade',
                    'priority': 'high'
                })
        
        # Análise geral de custo
        cost_metrics = [m for m in metrics if m.metric_type == MetricType.COST]
        if cost_metrics:
            total_cost = sum(m.value for m in cost_metrics)
            if total_cost > 1.0:  # Mais de $1.00 total
                recommendations.append({
                    'category': 'cost',
                    'title': 'Reduzir Custos',
                    'description': f'Custo total ({total_cost:.2f}) está alto',
                    'action': 'Otimizar uso de tokens e considerar modelos mais eficientes',
                    'priority': 'medium'
                })
        
        return recommendations 