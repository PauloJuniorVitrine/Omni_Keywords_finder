"""
Sistema de Métricas Avançado - Omni Keywords Finder
Tracing ID: OBSERVABILITY_20241219_001
Data: 2024-12-19
Versão: 1.0

Implementa sistema de métricas com:
- Integração com Prometheus
- Métricas customizadas de negócio
- Alertas inteligentes
- Dashboards automáticos
- Análise de performance
"""

import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Union
from threading import Lock

try:
    from prometheus_client import (
        Counter, Gauge, Histogram, Summary, 
        start_http_server, generate_latest, CONTENT_TYPE_LATEST
    )
    from prometheus_client.core import CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus não disponível. Métricas serão limitadas.")


class MetricsManager:
    """
    Gerenciador de métricas avançado com suporte a métricas customizadas
    e integração com Prometheus.
    """
    
    def __init__(self, service_name: str = "omni-keywords-finder"):
        self.service_name = service_name
        self.registry = CollectorRegistry()
        self._initialized = False
        self._lock = Lock()
        
        # Configurações
        self.config = {
            "prometheus_port": 9090,
            "metrics_prefix": "omni_keywords_finder",
            "environment": "development",
            "enable_default_metrics": True
        }
        
        # Métricas customizadas
        self.metrics = {}
        
        if PROMETHEUS_AVAILABLE:
            self._setup_metrics()
    
    def _setup_metrics(self) -> None:
        """Configura o sistema de métricas."""
        try:
            # Iniciar servidor Prometheus
            start_http_server(self.config["prometheus_port"], registry=self.registry)
            
            # Criar métricas padrão
            if self.config["enable_default_metrics"]:
                self._create_default_metrics()
            
            # Criar métricas de negócio
            self._create_business_metrics()
            
            self._initialized = True
            logging.info(f"Métricas inicializadas na porta {self.config['prometheus_port']}")
            
        except Exception as e:
            logging.error(f"Erro ao configurar métricas: {e}")
            raise
    
    def _create_default_metrics(self) -> None:
        """Cria métricas padrão do sistema."""
        prefix = self.config["metrics_prefix"]
        
        # Métricas HTTP
        self.metrics["http_requests_total"] = Counter(
            f"{prefix}_http_requests_total",
            "Total de requisições HTTP",
            ["method", "endpoint", "status_code"],
            registry=self.registry
        )
        
        self.metrics["http_request_duration_seconds"] = Histogram(
            f"{prefix}_http_request_duration_seconds",
            "Duração das requisições HTTP",
            ["method", "endpoint"],
            registry=self.registry
        )
        
        # Métricas de erro
        self.metrics["errors_total"] = Counter(
            f"{prefix}_errors_total",
            "Total de erros",
            ["error_type", "service"],
            registry=self.registry
        )
        
        # Métricas de performance
        self.metrics["memory_usage_bytes"] = Gauge(
            f"{prefix}_memory_usage_bytes",
            "Uso de memória em bytes",
            ["service"],
            registry=self.registry
        )
        
        self.metrics["cpu_usage_percent"] = Gauge(
            f"{prefix}_cpu_usage_percent",
            "Uso de CPU em percentual",
            ["service"],
            registry=self.registry
        )
        
        # Métricas de conexão
        self.metrics["active_connections"] = Gauge(
            f"{prefix}_active_connections",
            "Conexões ativas",
            ["connection_type"],
            registry=self.registry
        )
    
    def _create_business_metrics(self) -> None:
        """Cria métricas específicas do negócio."""
        prefix = self.config["metrics_prefix"]
        
        # Métricas de keywords
        self.metrics["keywords_processed_total"] = Counter(
            f"{prefix}_keywords_processed_total",
            "Total de keywords processadas",
            ["source", "status", "niche"],
            registry=self.registry
        )
        
        self.metrics["keywords_processing_duration_seconds"] = Histogram(
            f"{prefix}_keywords_processing_duration_seconds",
            "Duração do processamento de keywords",
            ["source", "niche"],
            registry=self.registry
        )
        
        # Métricas de cache
        self.metrics["cache_hits_total"] = Counter(
            f"{prefix}_cache_hits_total",
            "Total de cache hits",
            ["cache_type", "key_pattern"],
            registry=self.registry
        )
        
        self.metrics["cache_misses_total"] = Counter(
            f"{prefix}_cache_misses_total",
            "Total de cache misses",
            ["cache_type", "key_pattern"],
            registry=self.registry
        )
        
        # Métricas de execução
        self.metrics["executions_total"] = Counter(
            f"{prefix}_executions_total",
            "Total de execuções",
            ["execution_type", "status"],
            registry=self.registry
        )
        
        self.metrics["execution_duration_seconds"] = Histogram(
            f"{prefix}_execution_duration_seconds",
            "Duração das execuções",
            ["execution_type"],
            registry=self.registry
        )
        
        # Métricas de agendamento
        self.metrics["scheduled_executions_total"] = Counter(
            f"{prefix}_scheduled_executions_total",
            "Total de execuções agendadas",
            ["schedule_type", "status"],
            registry=self.registry
        )
        
        # Métricas de API externa
        self.metrics["external_api_calls_total"] = Counter(
            f"{prefix}_external_api_calls_total",
            "Total de chamadas para APIs externas",
            ["api_name", "endpoint", "status"],
            registry=self.registry
        )
        
        self.metrics["external_api_duration_seconds"] = Histogram(
            f"{prefix}_external_api_duration_seconds",
            "Duração das chamadas para APIs externas",
            ["api_name", "endpoint"],
            registry=self.registry
        )
        
        # Métricas de usuário
        self.metrics["active_users"] = Gauge(
            f"{prefix}_active_users",
            "Usuários ativos",
            ["user_type"],
            registry=self.registry
        )
        
        self.metrics["user_actions_total"] = Counter(
            f"{prefix}_user_actions_total",
            "Total de ações de usuário",
            ["action_type", "user_type"],
            registry=self.registry
        )
    
    def record_http_request(self, method: str, endpoint: str, 
                           status_code: int, duration: float) -> None:
        """
        Registra métrica de requisição HTTP.
        
        Args:
            method: Método HTTP
            endpoint: Endpoint da requisição
            status_code: Código de status
            duration: Duração da requisição
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["http_requests_total"].labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            self.metrics["http_request_duration_seconds"].labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    def record_error(self, error_type: str, service: str, 
                    error_message: Optional[str] = None) -> None:
        """
        Registra métrica de erro.
        
        Args:
            error_type: Tipo do erro
            service: Serviço onde ocorreu o erro
            error_message: Mensagem do erro (opcional)
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["errors_total"].labels(
                error_type=error_type,
                service=service
            ).inc()
    
    def record_keyword_processed(self, source: str, status: str, 
                               niche: str, count: int = 1) -> None:
        """
        Registra keywords processadas.
        
        Args:
            source: Fonte das keywords
            status: Status do processamento
            niche: Nicho das keywords
            count: Quantidade processada
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["keywords_processed_total"].labels(
                source=source,
                status=status,
                niche=niche
            ).inc(count)
    
    def record_keyword_processing_duration(self, source: str, niche: str, 
                                         duration: float) -> None:
        """
        Registra duração do processamento de keywords.
        
        Args:
            source: Fonte das keywords
            niche: Nicho das keywords
            duration: Duração do processamento
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["keywords_processing_duration_seconds"].labels(
                source=source,
                niche=niche
            ).observe(duration)
    
    def record_cache_hit(self, cache_type: str, key_pattern: str) -> None:
        """
        Registra cache hit.
        
        Args:
            cache_type: Tipo do cache
            key_pattern: Padrão da chave
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["cache_hits_total"].labels(
                cache_type=cache_type,
                key_pattern=key_pattern
            ).inc()
    
    def record_cache_miss(self, cache_type: str, key_pattern: str) -> None:
        """
        Registra cache miss.
        
        Args:
            cache_type: Tipo do cache
            key_pattern: Padrão da chave
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["cache_misses_total"].labels(
                cache_type=cache_type,
                key_pattern=key_pattern
            ).inc()
    
    def record_execution(self, execution_type: str, status: str, 
                        duration: Optional[float] = None) -> None:
        """
        Registra execução.
        
        Args:
            execution_type: Tipo da execução
            status: Status da execução
            duration: Duração da execução (opcional)
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["executions_total"].labels(
                execution_type=execution_type,
                status=status
            ).inc()
            
            if duration is not None:
                self.metrics["execution_duration_seconds"].labels(
                    execution_type=execution_type
                ).observe(duration)
    
    def record_external_api_call(self, api_name: str, endpoint: str, 
                                status: str, duration: Optional[float] = None) -> None:
        """
        Registra chamada para API externa.
        
        Args:
            api_name: Nome da API
            endpoint: Endpoint chamado
            status: Status da chamada
            duration: Duração da chamada (opcional)
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["external_api_calls_total"].labels(
                api_name=api_name,
                endpoint=endpoint,
                status=status
            ).inc()
            
            if duration is not None:
                self.metrics["external_api_duration_seconds"].labels(
                    api_name=api_name,
                    endpoint=endpoint
                ).observe(duration)
    
    def set_active_users(self, user_type: str, count: int) -> None:
        """
        Define número de usuários ativos.
        
        Args:
            user_type: Tipo de usuário
            count: Número de usuários ativos
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["active_users"].labels(
                user_type=user_type
            ).set(count)
    
    def record_user_action(self, action_type: str, user_type: str) -> None:
        """
        Registra ação de usuário.
        
        Args:
            action_type: Tipo da ação
            user_type: Tipo de usuário
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["user_actions_total"].labels(
                action_type=action_type,
                user_type=user_type
            ).inc()
    
    def set_memory_usage(self, service: str, bytes_used: int) -> None:
        """
        Define uso de memória.
        
        Args:
            service: Nome do serviço
            bytes_used: Bytes utilizados
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["memory_usage_bytes"].labels(
                service=service
            ).set(bytes_used)
    
    def set_cpu_usage(self, service: str, percent_used: float) -> None:
        """
        Define uso de CPU.
        
        Args:
            service: Nome do serviço
            percent_used: Percentual de CPU utilizado
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["cpu_usage_percent"].labels(
                service=service
            ).set(percent_used)
    
    def set_active_connections(self, connection_type: str, count: int) -> None:
        """
        Define número de conexões ativas.
        
        Args:
            connection_type: Tipo de conexão
            count: Número de conexões ativas
        """
        if not self._initialized:
            return
        
        with self._lock:
            self.metrics["active_connections"].labels(
                connection_type=connection_type
            ).set(count)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo das métricas atuais.
        
        Returns:
            Dicionário com resumo das métricas
        """
        if not self._initialized:
            return {}
        
        summary = {
            "service": self.service_name,
            "environment": self.config["environment"],
            "metrics_count": len(self.metrics),
            "prometheus_endpoint": f"http://localhost:{self.config['prometheus_port']}/metrics"
        }
        
        return summary
    
    def generate_metrics(self) -> str:
        """
        Gera métricas no formato Prometheus.
        
        Returns:
            String com métricas no formato Prometheus
        """
        if not self._initialized:
            return ""
        
        return generate_latest(self.registry)


# Instância global do gerenciador de métricas
metrics_manager = MetricsManager()


def get_metrics_manager() -> MetricsManager:
    """Retorna a instância global do gerenciador de métricas."""
    return metrics_manager


def initialize_metrics(service_name: str = "omni-keywords-finder") -> MetricsManager:
    """
    Inicializa e retorna o sistema de métricas.
    
    Args:
        service_name: Nome do serviço
        
    Returns:
        Instância configurada do MetricsManager
    """
    global metrics_manager
    metrics_manager = MetricsManager(service_name)
    return metrics_manager


# Funções de conveniência
def record_http_request(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """Registra requisição HTTP."""
    metrics_manager.record_http_request(method, endpoint, status_code, duration)


def record_error(error_type: str, service: str, error_message: Optional[str] = None) -> None:
    """Registra erro."""
    metrics_manager.record_error(error_type, service, error_message)


def record_keyword_processed(source: str, status: str, niche: str, count: int = 1) -> None:
    """Registra keywords processadas."""
    metrics_manager.record_keyword_processed(source, status, niche, count)


def record_cache_hit(cache_type: str, key_pattern: str) -> None:
    """Registra cache hit."""
    metrics_manager.record_cache_hit(cache_type, key_pattern)


def record_cache_miss(cache_type: str, key_pattern: str) -> None:
    """Registra cache miss."""
    metrics_manager.record_cache_miss(cache_type, key_pattern) 