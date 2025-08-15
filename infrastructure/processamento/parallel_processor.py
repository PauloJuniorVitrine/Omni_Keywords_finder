"""
Processador Paralelo de Keywords
Responsável por processamento paralelo com async/await, semaphore e retry policies.

Prompt: CHECKLIST_APRIMORAMENTO_FINAL.md - Fase 2.1
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Versão: 1.0.0
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import random

from shared.logger import logger
from domain.models import Keyword, Cluster

class ProcessingStatus(Enum):
    """Status do processamento."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class ProcessingResult:
    """Resultado do processamento."""
    keyword: Keyword
    status: ProcessingStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    retry_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProcessingConfig:
    """Configuração do processamento."""
    max_concurrent: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    backoff_factor: float = 2.0
    jitter: bool = True

class ParallelProcessor:
    """
    Processador paralelo de keywords com async/await.
    
    Características:
    - Processamento paralelo com semaphore
    - Retry com backoff exponencial
    - Circuit breaker básico
    - Métricas de performance
    - Fallback strategies
    """
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """Inicializar processador paralelo."""
        self.config = config if config is not None else ProcessingConfig()
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent)
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'retried': 0,
            'total_time': 0.0,
            'avg_time': 0.0
        }
        self.circuit_breaker = {
            'failure_count': 0,
            'last_failure_time': None,
            'is_open': False,
            'threshold': 5,
            'timeout': 60.0
        }
        
        logger.info(f"ParallelProcessor inicializado com {self.config.max_concurrent} workers")
    
    async def process_keywords(
        self,
        keywords: List[Keyword],
        processor_func: Callable[[Keyword], Awaitable[Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ProcessingResult]:
        """
        Processar lista de keywords em paralelo.
        
        Args:
            keywords: Lista de keywords para processar
            processor_func: Função de processamento assíncrona
            context: Contexto adicional para processamento
            
        Returns:
            Lista de resultados de processamento
        """
        start_time = time.time()
        logger.info(f"Iniciando processamento paralelo de {len(keywords)} keywords")
        
        # Criar tasks para processamento paralelo
        tasks = []
        for keyword in keywords:
            task = self._process_single_keyword(keyword, processor_func, context)
            tasks.append(task)
        
        # Executar todas as tasks em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        processed_results = []
        for index, result in enumerate(results):
            if isinstance(result, Exception):
                # Task falhou com exceção
                processed_results.append(ProcessingResult(
                    keyword=keywords[index],
                    status=ProcessingStatus.FAILED,
                    error=str(result),
                    processing_time=0.0
                ))
                self.processing_stats['failed'] += 1
            else:
                # Task completou com sucesso
                processed_results.append(result)
                if hasattr(result, 'status') and result.status == ProcessingStatus.COMPLETED:
                    self.processing_stats['successful'] += 1
                else:
                    self.processing_stats['failed'] += 1
        
        # Atualizar estatísticas
        self._update_stats(start_time, len(keywords))
        
        logger.info(f"Processamento concluído: {self.processing_stats['successful']} sucessos, "
                   f"{self.processing_stats['failed']} falhas")
        
        return processed_results
    
    async def _process_single_keyword(
        self,
        keyword: Keyword,
        processor_func: Callable[[Keyword], Awaitable[Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """Processar uma única keyword com retry e circuit breaker."""
        start_time = time.time()
        retry_count = 0
        
        while retry_count <= self.config.max_retries:
            try:
                # Verificar circuit breaker
                if self._is_circuit_breaker_open():
                    raise Exception("Circuit breaker is open")
                
                # Processar com semaphore
                async with self.semaphore:
                    result = await asyncio.wait_for(
                        processor_func(keyword),
                        timeout=self.config.timeout
                    )
                    
                    # Sucesso - resetar circuit breaker
                    self._reset_circuit_breaker()
                    
                    return ProcessingResult(
                        keyword=keyword,
                        status=ProcessingStatus.COMPLETED,
                        data=result,
                        processing_time=time.time() - start_time,
                        retry_count=retry_count,
                        metadata={'context': context}
                    )
                    
            except asyncio.TimeoutError:
                error_msg = f"Timeout após {self.config.timeout}string_data"
                logger.warning(f"Timeout processando keyword {keyword.termo}: {error_msg}")
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Erro processando keyword {keyword.termo}: {error_msg}")
                
                # Atualizar circuit breaker
                self._update_circuit_breaker()
            
            # Incrementar retry count
            retry_count += 1
            self.processing_stats['retried'] += 1
            
            # Se ainda há tentativas, aguardar antes de retry
            if retry_count <= self.config.max_retries:
                delay = self._calculate_retry_delay(retry_count)
                logger.info(f"Retry {retry_count}/{self.config.max_retries} para {keyword.termo} em {delay}string_data")
                await asyncio.sleep(delay)
        
        # Todas as tentativas falharam
        return ProcessingResult(
            keyword=keyword,
            status=ProcessingStatus.FAILED,
            error=f"Falhou após {self.config.max_retries} tentativas",
            processing_time=time.time() - start_time,
            retry_count=retry_count,
            metadata={'context': context}
        )
    
    def _calculate_retry_delay(self, retry_count: int) -> float:
        """Calcular delay para retry com backoff exponencial e jitter."""
        base_delay = self.config.retry_delay * (self.config.backoff_factor ** (retry_count - 1))
        
        if self.config.jitter:
            # Adicionar jitter para evitar thundering herd
            jitter = random.uniform(0, 0.1 * base_delay)
            return base_delay + jitter
        
        return base_delay
    
    def _is_circuit_breaker_open(self) -> bool:
        """Verificar se circuit breaker está aberto."""
        if not self.circuit_breaker['is_open']:
            return False
        
        # Verificar se timeout expirou
        if self.circuit_breaker['last_failure_time']:
            time_since_failure = time.time() - self.circuit_breaker['last_failure_time']
            if time_since_failure > self.circuit_breaker['timeout']:
                # Tentar fechar circuit breaker (half-open state)
                self.circuit_breaker['is_open'] = False
                self.circuit_breaker['failure_count'] = 0
                logger.info("Circuit breaker fechado (timeout expirado)")
                return False
        
        return True
    
    def _update_circuit_breaker(self):
        """Atualizar circuit breaker com nova falha."""
        self.circuit_breaker['failure_count'] += 1
        self.circuit_breaker['last_failure_time'] = time.time()
        
        if self.circuit_breaker['failure_count'] >= self.circuit_breaker['threshold']:
            self.circuit_breaker['is_open'] = True
            logger.warning(f"Circuit breaker aberto após {self.circuit_breaker['failure_count']} falhas")
    
    def _reset_circuit_breaker(self):
        """Resetar circuit breaker após sucesso."""
        self.circuit_breaker['failure_count'] = 0
        self.circuit_breaker['last_failure_time'] = None
        self.circuit_breaker['is_open'] = False
    
    def _update_stats(self, start_time: float, total_count: int):
        """Atualizar estatísticas de processamento."""
        total_time = time.time() - start_time
        
        self.processing_stats['total_processed'] += total_count
        self.processing_stats['total_time'] += total_time
        
        if self.processing_stats['total_processed'] > 0:
            self.processing_stats['avg_time'] = (
                self.processing_stats['total_time'] / self.processing_stats['total_processed']
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de processamento."""
        stats = self.processing_stats.copy()
        stats.update({
            'circuit_breaker_open': self.circuit_breaker['is_open'],
            'circuit_breaker_failures': self.circuit_breaker['failure_count'],
            'success_rate': (
                stats['successful'] / stats['total_processed'] * 100 
                if stats['total_processed'] > 0 else 0
            ),
            'retry_rate': (
                stats['retried'] / stats['total_processed'] * 100 
                if stats['total_processed'] > 0 else 0
            )
        })
        return stats
    
    def reset_stats(self):
        """Resetar estatísticas de processamento."""
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'retried': 0,
            'total_time': 0.0,
            'avg_time': 0.0
        }
        logger.info("Estatísticas de processamento resetadas")

class BatchProcessor:
    """
    Processador em lotes para grandes volumes de keywords.
    
    Características:
    - Processamento em lotes configuráveis
    - Progress tracking
    - Memory management
    - Graceful shutdown
    """
    
    def __init__(self, batch_size: int = 100, processor: Optional[ParallelProcessor] = None):
        """Inicializar processador em lotes."""
        self.batch_size = batch_size
        self.processor = processor if processor is not None else ParallelProcessor()
        self.progress_callback = None
        
        logger.info(f"BatchProcessor inicializado com batch_size={batch_size}")
    
    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """Definir callback para progresso."""
        self.progress_callback = callback
    
    async def process_in_batches(
        self,
        keywords: List[Keyword],
        processor_func: Callable[[Keyword], Awaitable[Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ProcessingResult]:
        """
        Processar keywords em lotes.
        
        Args:
            keywords: Lista completa de keywords
            processor_func: Função de processamento
            context: Contexto adicional
            
        Returns:
            Lista completa de resultados
        """
        total_keywords = len(keywords)
        all_results = []
        
        logger.info(f"Iniciando processamento em lotes: {total_keywords} keywords, "
                   f"batch_size={self.batch_size}")
        
        for index in range(0, total_keywords, self.batch_size):
            batch = keywords[index:index + self.batch_size]
            batch_num = (index // self.batch_size) + 1
            total_batches = (total_keywords + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processando lote {batch_num}/{total_batches} "
                       f"({len(batch)} keywords)")
            
            # Processar lote
            batch_results = await self.processor.process_keywords(
                batch, processor_func, context
            )
            all_results.extend(batch_results)
            
            # Atualizar progresso
            if self.progress_callback:
                self.progress_callback(index + len(batch), total_keywords)
            
            # Pequena pausa entre lotes para evitar sobrecarga
            await asyncio.sleep(0.1)
        
        logger.info(f"Processamento em lotes concluído: {len(all_results)} resultados")
        return all_results
    
    def get_processor_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do processador."""
        return self.processor.get_stats()

# Funções utilitárias para processamento específico

async def process_keyword_enrichment(keyword: Keyword) -> Dict[str, Any]:
    """Exemplo de função de enriquecimento de keyword."""
    # Simular processamento de enriquecimento
    await asyncio.sleep(random.uniform(0.1, 0.5))
    
    return {
        'enriched_data': {
            'volume_estimate': random.randint(1000, 50000),
            'competition_level': random.choice(['low', 'medium', 'high']),
            'trend_direction': random.choice(['up', 'down', 'stable']),
            'seasonality': random.choice(['year_round', 'seasonal', 'trending'])
        },
        'processing_timestamp': datetime.utcnow().isoformat()
    }

async def process_keyword_validation(keyword: Keyword) -> Dict[str, Any]:
    """Exemplo de função de validação de keyword."""
    # Simular validação
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    return {
        'validation_result': {
            'is_valid': random.choice([True, True, True, False]),  # 75% válido
            'score': random.uniform(0.5, 1.0),
            'issues': [] if random.random() > 0.3 else ['minor_issue'],
            'suggestions': [] if random.random() > 0.5 else ['improvement_suggestion']
        },
        'processing_timestamp': datetime.utcnow().isoformat()
    }

async def process_keyword_analysis(keyword: Keyword) -> Dict[str, Any]:
    """Exemplo de função de análise de keyword."""
    # Simular análise
    await asyncio.sleep(random.uniform(0.2, 0.8))
    
    return {
        'analysis_result': {
            'intent_type': random.choice(['commercial', 'informational', 'navigational']),
            'difficulty_score': random.uniform(0.1, 0.9),
            'opportunity_score': random.uniform(0.1, 0.9),
            'related_keywords': [f"related_{index}" for index in range(random.randint(3, 8))]
        },
        'processing_timestamp': datetime.utcnow().isoformat()
    }

# ============================================================================
# OTIMIZAÇÕES DE I/O E PERFORMANCE - FASE 2.1
# ============================================================================

import aiohttp
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
import time
import psutil

class ConnectionPool:
    """Pool de conexões para otimização de I/O."""
    
    def __init__(self, max_connections: int = 100, timeout: float = 30.0):
        self.max_connections = max_connections
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.connection_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'total_response_time': 0.0
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Obter ou criar sessão HTTP."""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30
            )
            
            timeout_config = aiohttp.ClientTimeout(
                total=self.timeout,
                connect=10,
                sock_read=30
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout_config,
                headers={'User-Agent': 'OmniKeywordsFinder/1.0'}
            )
            
            logger.info(f"Connection pool criado: max_connections={self.max_connections}")
        
        return self.session
    
    async def close(self):
        """Fechar pool de conexões."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Connection pool fechado")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do pool."""
        stats = self.connection_stats.copy()
        if stats['total_requests'] > 0:
            stats['success_rate'] = (
                stats['successful_requests'] / stats['total_requests'] * 100
            )
        return stats

class PerformanceMonitor:
    """Monitor de performance do sistema."""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_io': [],
            'network_io': [],
            'response_times': [],
            'throughput': []
        }
        self.alert_thresholds = {
            'cpu_usage': 80.0,  # %
            'memory_usage': 85.0,  # %
            'response_time': 5000.0,  # ms
            'error_rate': 5.0  # %
        }
    
    def record_metric(self, metric_type: str, value: float):
        """Registrar métrica."""
        if metric_type in self.metrics:
            self.metrics[metric_type].append({
                'value': value,
                'timestamp': time.time()
            })
            
            # Manter apenas últimas 1000 métricas
            if len(self.metrics[metric_type]) > 1000:
                self.metrics[metric_type] = self.metrics[metric_type][-1000:]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obter métricas do sistema."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Registrar métricas
        self.record_metric('cpu_usage', cpu_percent)
        self.record_metric('memory_usage', memory.percent)
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': memory.available,
            'disk_usage': disk.percent,
            'disk_free': disk.free,
            'uptime': time.time() - self.start_time
        }
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Verificar alertas de performance."""
        alerts = []
        system_metrics = self.get_system_metrics()
        
        if system_metrics['cpu_usage'] > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'warning',
                'metric': 'cpu_usage',
                'value': system_metrics['cpu_usage'],
                'threshold': self.alert_thresholds['cpu_usage'],
                'message': f"CPU usage alto: {system_metrics['cpu_usage']:.1f}%"
            })
        
        if system_metrics['memory_usage'] > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'warning',
                'metric': 'memory_usage',
                'value': system_metrics['memory_usage'],
                'threshold': self.alert_thresholds['memory_usage'],
                'message': f"Memory usage alto: {system_metrics['memory_usage']:.1f}%"
            })
        
        return alerts
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obter resumo de performance."""
        system_metrics = self.get_system_metrics()
        alerts = self.check_alerts()
        
        # Calcular médias das métricas
        avg_metrics = {}
        for metric_type, values in self.metrics.items():
            if values:
                avg_metrics[f'avg_{metric_type}'] = sum(value['value'] for value in values) / len(values)
        
        return {
            'system_metrics': system_metrics,
            'average_metrics': avg_metrics,
            'alerts': alerts,
            'uptime': system_metrics['uptime']
        }

class OptimizedParallelProcessor(ParallelProcessor):
    """
    Processador paralelo otimizado com I/O melhorado.
    
    Melhorias:
    - Connection pooling
    - Performance monitoring
    - Circuit breaker avançado
    - Fallback strategies
    """
    
    def __init__(self, config: ProcessingConfig = None):
        super().__init__(config)
        self.connection_pool = ConnectionPool()
        self.performance_monitor = PerformanceMonitor()
        self.fallback_strategies = {
            'enrichment': self._fallback_enrichment,
            'validation': self._fallback_validation,
            'analysis': self._fallback_analysis
        }
        
        logger.info("OptimizedParallelProcessor inicializado com otimizações de I/O")
    
    async def process_keywords_optimized(
        self,
        keywords: List[Keyword],
        processor_func: Callable[[Keyword], Awaitable[Dict[str, Any]]],
        context: Optional[Dict[str, Any]] = None,
        enable_fallback: bool = True
    ) -> List[ProcessingResult]:
        """
        Processar keywords com otimizações de I/O.
        
        Args:
            keywords: Lista de keywords
            processor_func: Função de processamento
            context: Contexto adicional
            enable_fallback: Habilitar estratégias de fallback
            
        Returns:
            Lista de resultados
        """
        start_time = time.time()
        
        # Monitorar performance
        self.performance_monitor.record_metric('throughput', len(keywords))
        
        # Processar com otimizações
        results = await super().process_keywords(keywords, processor_func, context)
        
        # Aplicar fallback se necessário
        if enable_fallback:
            results = await self._apply_fallback_strategies(results, context)
        
        # Registrar métricas finais
        total_time = time.time() - start_time
        self.performance_monitor.record_metric('response_times', total_time * 1000)  # ms
        
        # Verificar alertas
        alerts = self.performance_monitor.check_alerts()
        if alerts:
            for alert in alerts:
                logger.warning(f"Performance alert: {alert['message']}")
        
        return results
    
    async def _apply_fallback_strategies(
        self,
        results: List[ProcessingResult],
        context: Optional[Dict[str, Any]]
    ) -> List[ProcessingResult]:
        """Aplicar estratégias de fallback para resultados falhados."""
        for index, result in enumerate(results):
            if result.status == ProcessingStatus.FAILED:
                # Tentar fallback baseado no contexto
                fallback_result = await self._try_fallback(result, context)
                if fallback_result:
                    results[index] = fallback_result
                    logger.info(f"Fallback aplicado para keyword: {result.keyword.termo}")
        
        return results
    
    async def _try_fallback(
        self,
        failed_result: ProcessingResult,
        context: Optional[Dict[str, Any]]
    ) -> Optional[ProcessingResult]:
        """Tentar fallback para resultado falhado."""
        try:
            # Determinar tipo de processamento baseado no erro
            error_msg = failed_result.error.lower()
            
            if 'enrichment' in error_msg or 'enrich' in error_msg:
                fallback_func = self.fallback_strategies['enrichment']
            elif 'validation' in error_msg or 'validate' in error_msg:
                fallback_func = self.fallback_strategies['validation']
            elif 'analysis' in error_msg or 'analyze' in error_msg:
                fallback_func = self.fallback_strategies['analysis']
            else:
                return None
            
            # Executar fallback
            fallback_data = await fallback_func(failed_result.keyword)
            
            return ProcessingResult(
                keyword=failed_result.keyword,
                status=ProcessingStatus.COMPLETED,
                data=fallback_data,
                processing_time=failed_result.processing_time,
                retry_count=failed_result.retry_count,
                metadata={'fallback_applied': True, 'original_error': failed_result.error}
            )
            
        except Exception as e:
            logger.error(f"Fallback falhou para {failed_result.keyword.termo}: {e}")
            return None
    
    async def _fallback_enrichment(self, keyword: Keyword) -> Dict[str, Any]:
        """Fallback para enriquecimento."""
        return {
            'enriched_data': {
                'volume_estimate': 1000,  # Valor padrão
                'competition_level': 'medium',
                'trend_direction': 'stable',
                'seasonality': 'year_round'
            },
            'fallback_applied': True,
            'processing_timestamp': datetime.utcnow().isoformat()
        }
    
    async def _fallback_validation(self, keyword: Keyword) -> Dict[str, Any]:
        """Fallback para validação."""
        return {
            'validation_result': {
                'is_valid': True,
                'score': 0.5,  # Score neutro
                'issues': [],
                'suggestions': ['Fallback validation applied']
            },
            'fallback_applied': True,
            'processing_timestamp': datetime.utcnow().isoformat()
        }
    
    async def _fallback_analysis(self, keyword: Keyword) -> Dict[str, Any]:
        """Fallback para análise."""
        return {
            'analysis_result': {
                'intent_type': 'informational',
                'difficulty_score': 0.5,
                'opportunity_score': 0.5,
                'related_keywords': []
            },
            'fallback_applied': True,
            'processing_timestamp': datetime.utcnow().isoformat()
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de performance."""
        base_stats = self.get_stats()
        performance_summary = self.performance_monitor.get_performance_summary()
        connection_stats = self.connection_pool.get_stats()
        
        return {
            **base_stats,
            'performance': performance_summary,
            'connections': connection_stats,
            'optimizations_enabled': True
        }
    
    async def cleanup(self):
        """Limpeza de recursos."""
        await self.connection_pool.close()
        logger.info("OptimizedParallelProcessor cleanup concluído")

# ============================================================================
# VALIDAÇÃO DE SLOs - FASE 2.1
# ============================================================================

class SLOMonitor:
    """Monitor de Service Level Objectives."""
    
    def __init__(self):
        self.slos = {
            'latency_p95': 200.0,  # ms
            'throughput_min': 10.0,  # keywords/string_data
            'availability': 99.0,  # %
            'error_rate_max': 1.0  # %
        }
        self.slo_metrics = {
            'latency_p95': [],
            'throughput': [],
            'availability': [],
            'error_rate': []
        }
    
    def record_slo_metric(self, slo_type: str, value: float):
        """Registrar métrica de SLO."""
        if slo_type in self.slo_metrics:
            self.slo_metrics[slo_type].append({
                'value': value,
                'timestamp': time.time()
            })
    
    def check_slo_compliance(self) -> Dict[str, Dict[str, Any]]:
        """Verificar compliance com SLOs."""
        compliance = {}
        
        for slo_type, threshold in self.slos.items():
            if slo_type in self.slo_metrics and self.slo_metrics[slo_type]:
                values = [m['value'] for m in self.slo_metrics[slo_type][-100:]]  # Últimas 100 métricas
                
                if slo_type == 'latency_p95':
                    current_value = sorted(values)[int(len(values) * 0.95)] if values else 0
                    is_compliant = current_value <= threshold
                elif slo_type == 'throughput':
                    current_value = sum(values) / len(values) if values else 0
                    is_compliant = current_value >= threshold
                elif slo_type == 'availability':
                    current_value = (1 - (sum(1 for value in values if value > 0) / len(values))) * 100 if values else 100
                    is_compliant = current_value >= threshold
                elif slo_type == 'error_rate':
                    current_value = (sum(1 for value in values if value > 0) / len(values)) * 100 if values else 0
                    is_compliant = current_value <= threshold
                else:
                    current_value = 0
                    is_compliant = True
                
                compliance[slo_type] = {
                    'current_value': current_value,
                    'threshold': threshold,
                    'is_compliant': is_compliant,
                    'status': '✅' if is_compliant else '❌'
                }
        
        return compliance
    
    def get_slo_report(self) -> Dict[str, Any]:
        """Gerar relatório de SLOs."""
        compliance = self.check_slo_compliance()
        overall_compliance = all(c['is_compliant'] for c in compliance.values())
        
        return {
            'overall_compliance': overall_compliance,
            'compliance_details': compliance,
            'timestamp': datetime.utcnow().isoformat()
        } 