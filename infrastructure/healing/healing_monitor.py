"""
Healing Monitor - Monitoramento para Sistema de Auto-Cura

Tracing ID: HEALING_MONITOR_001_20250127
Versão: 1.0
Data: 2025-01-27
Objetivo: Monitorar serviços e coletar métricas para detecção de problemas

Este módulo implementa o monitoramento de serviços para o sistema de self-healing,
coletando métricas e verificando a saúde dos serviços.
"""

import asyncio
import logging
import time
import psutil
import aiohttp
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from .healing_config import HealingConfig
from .self_healing_service import ServiceStatus, ServiceInfo

logger = logging.getLogger(__name__)


@dataclass
class ServiceMetrics:
    """Métricas coletadas de um serviço"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    response_time: float
    error_rate: float
    active_connections: int
    timestamp: datetime
    additional_metrics: Dict[str, Any]


class HealingMonitor:
    """Monitor para coleta de métricas e verificação de saúde de serviços"""
    
    def __init__(self, config: HealingConfig):
        """
        Inicializa o monitor de healing
        
        Args:
            config: Configuração do sistema de healing
        """
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.session = None
        self.metrics_cache: Dict[str, ServiceMetrics] = {}
        self.health_cache: Dict[str, ServiceStatus] = {}
        self.cache_lock = threading.RLock()
        
        logger.info(f"[HEALING_MONITOR] Monitor inicializado com {config.max_workers} workers")
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def check_service_health(self, service_info: ServiceInfo) -> ServiceStatus:
        """
        Verifica a saúde de um serviço
        
        Args:
            service_info: Informações do serviço
            
        Returns:
            Status de saúde do serviço
        """
        try:
            # Verificar cache primeiro
            cache_key = f"{service_info.name}_{int(time.time() / 30)}"  # Cache de 30s
            with self.cache_lock:
                if cache_key in self.health_cache:
                    return self.health_cache[cache_key]
            
            # Realizar verificações de saúde
            checks = [
                self._check_process_health(service_info),
                self._check_endpoint_health(service_info),
                self._check_resource_health(service_info)
            ]
            
            # Executar verificações em paralelo
            results = await asyncio.gather(*checks, return_exceptions=True)
            
            # Determinar status baseado nos resultados
            status = self._determine_health_status(results)
            
            # Atualizar cache
            with self.cache_lock:
                self.health_cache[cache_key] = status
            
            return status
        
        except Exception as e:
            logger.error(f"[HEALING_MONITOR] Erro ao verificar saúde de {service_info.name}: {e}")
            return ServiceStatus.UNKNOWN
    
    async def collect_service_metrics(self, service_info: ServiceInfo) -> Dict[str, Any]:
        """
        Coleta métricas de um serviço
        
        Args:
            service_info: Informações do serviço
            
        Returns:
            Dicionário com métricas coletadas
        """
        try:
            # Verificar cache primeiro
            cache_key = f"{service_info.name}_{int(time.time() / 15)}"  # Cache de 15s
            with self.cache_lock:
                if cache_key in self.metrics_cache:
                    metrics = self.metrics_cache[cache_key]
                    return {
                        "cpu_usage": metrics.cpu_usage,
                        "memory_usage": metrics.memory_usage,
                        "disk_usage": metrics.disk_usage,
                        "network_io": metrics.network_io,
                        "response_time": metrics.response_time,
                        "error_rate": metrics.error_rate,
                        "active_connections": metrics.active_connections,
                        "timestamp": metrics.timestamp.isoformat(),
                        **metrics.additional_metrics
                    }
            
            # Coletar métricas em paralelo
            tasks = [
                self._collect_process_metrics(service_info),
                self._collect_endpoint_metrics(service_info),
                self._collect_system_metrics(service_info)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combinar métricas
            metrics = self._combine_metrics(results)
            
            # Armazenar no cache
            service_metrics = ServiceMetrics(
                cpu_usage=metrics.get("cpu_usage", 0.0),
                memory_usage=metrics.get("memory_usage", 0.0),
                disk_usage=metrics.get("disk_usage", 0.0),
                network_io=metrics.get("network_io", {}),
                response_time=metrics.get("response_time", 0.0),
                error_rate=metrics.get("error_rate", 0.0),
                active_connections=metrics.get("active_connections", 0),
                timestamp=datetime.now(),
                additional_metrics=metrics
            )
            
            with self.cache_lock:
                self.metrics_cache[cache_key] = service_metrics
            
            return metrics
        
        except Exception as e:
            logger.error(f"[HEALING_MONITOR] Erro ao coletar métricas de {service_info.name}: {e}")
            return {}
    
    async def _check_process_health(self, service_info: ServiceInfo) -> ServiceStatus:
        """Verifica saúde do processo do serviço"""
        try:
            # Encontrar processo do serviço
            process = await self._find_service_process(service_info.name)
            
            if not process:
                return ServiceStatus.FAILED
            
            # Verificar se processo está respondendo
            try:
                process.status()
                return ServiceStatus.HEALTHY
            except psutil.NoSuchProcess:
                return ServiceStatus.FAILED
            except psutil.AccessDenied:
                return ServiceStatus.DEGRADED
        
        except Exception as e:
            logger.debug(f"[HEALING_MONITOR] Erro ao verificar processo: {e}")
            return ServiceStatus.UNKNOWN
    
    async def _check_endpoint_health(self, service_info: ServiceInfo) -> ServiceStatus:
        """Verifica saúde do endpoint do serviço"""
        try:
            if not service_info.health_check_url:
                return ServiceStatus.UNKNOWN
            
            if not self.session:
                return ServiceStatus.UNKNOWN
            
            start_time = time.time()
            
            async with self.session.get(
                service_info.health_check_url,
                timeout=aiohttp.ClientTimeout(total=service_info.timeout)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    if response_time < 1.0:
                        return ServiceStatus.HEALTHY
                    else:
                        return ServiceStatus.DEGRADED
                elif response.status in [502, 503, 504]:
                    return ServiceStatus.FAILED
                else:
                    return ServiceStatus.DEGRADED
        
        except asyncio.TimeoutError:
            return ServiceStatus.FAILED
        except Exception as e:
            logger.debug(f"[HEALING_MONITOR] Erro ao verificar endpoint: {e}")
            return ServiceStatus.UNKNOWN
    
    async def _check_resource_health(self, service_info: ServiceInfo) -> ServiceStatus:
        """Verifica saúde dos recursos do sistema"""
        try:
            # Coletar métricas básicas do sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determinar status baseado nos recursos
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                return ServiceStatus.DEGRADED
            elif cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
                return ServiceStatus.DEGRADED
            else:
                return ServiceStatus.HEALTHY
        
        except Exception as e:
            logger.debug(f"[HEALING_MONITOR] Erro ao verificar recursos: {e}")
            return ServiceStatus.UNKNOWN
    
    async def _collect_process_metrics(self, service_info: ServiceInfo) -> Dict[str, Any]:
        """Coleta métricas do processo do serviço"""
        try:
            process = await self._find_service_process(service_info.name)
            
            if not process:
                return {}
            
            # Coletar métricas do processo
            with process.oneshot():
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                num_threads = process.num_threads()
                num_connections = len(process.connections())
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "memory_rss": memory_info.rss,
                "memory_vms": memory_info.vms,
                "num_threads": num_threads,
                "active_connections": num_connections,
                "process_id": process.pid
            }
        
        except Exception as e:
            logger.debug(f"[HEALING_MONITOR] Erro ao coletar métricas do processo: {e}")
            return {}
    
    async def _collect_endpoint_metrics(self, service_info: ServiceInfo) -> Dict[str, Any]:
        """Coleta métricas do endpoint do serviço"""
        try:
            if not service_info.health_check_url or not self.session:
                return {}
            
            # Coletar métricas de resposta
            response_times = []
            error_count = 0
            success_count = 0
            
            for _ in range(3):  # Fazer 3 tentativas
                try:
                    start_time = time.time()
                    
                    async with self.session.get(
                        service_info.health_check_url,
                        timeout=aiohttp.ClientTimeout(total=service_info.timeout)
                    ) as response:
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                        
                        if response.status == 200:
                            success_count += 1
                        else:
                            error_count += 1
                
                except Exception:
                    error_count += 1
            
            # Calcular métricas
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            total_requests = success_count + error_count
            error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "response_time": avg_response_time,
                "error_rate": error_rate,
                "success_count": success_count,
                "error_count": error_count,
                "total_requests": total_requests
            }
        
        except Exception as e:
            logger.debug(f"[HEALING_MONITOR] Erro ao coletar métricas do endpoint: {e}")
            return {}
    
    async def _collect_system_metrics(self, service_info: ServiceInfo) -> Dict[str, Any]:
        """Coleta métricas do sistema"""
        try:
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Métricas de rede
            network = psutil.net_io_counters()
            
            # Métricas de carga
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            return {
                "system_cpu_usage": cpu_percent,
                "system_cpu_count": cpu_count,
                "system_cpu_freq": cpu_freq.current if cpu_freq else 0,
                "system_memory_usage": memory.percent,
                "system_memory_available": memory.available,
                "system_swap_usage": swap.percent,
                "system_disk_usage": disk.percent,
                "system_disk_free": disk.free,
                "system_disk_io_read": disk_io.read_bytes if disk_io else 0,
                "system_disk_io_write": disk_io.write_bytes if disk_io else 0,
                "system_network_io": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "system_load_avg": {
                    "1min": load_avg[0],
                    "5min": load_avg[1],
                    "15min": load_avg[2]
                }
            }
        
        except Exception as e:
            logger.debug(f"[HEALING_MONITOR] Erro ao coletar métricas do sistema: {e}")
            return {}
    
    async def _find_service_process(self, service_name: str):
        """Encontra o processo de um serviço"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Verificar por nome do processo
                    if service_name.lower() in proc.info['name'].lower():
                        return proc
                    
                    # Verificar por linha de comando
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline']).lower()
                        if service_name.lower() in cmdline:
                            return proc
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return None
        
        except Exception as e:
            logger.debug(f"[HEALING_MONITOR] Erro ao encontrar processo: {e}")
            return None
    
    def _determine_health_status(self, check_results: List[ServiceStatus]) -> ServiceStatus:
        """Determina o status de saúde baseado nos resultados das verificações"""
        # Filtrar resultados válidos
        valid_results = [r for r in check_results if isinstance(r, ServiceStatus) and r != ServiceStatus.UNKNOWN]
        
        if not valid_results:
            return ServiceStatus.UNKNOWN
        
        # Se qualquer verificação indica falha, o serviço está falhado
        if ServiceStatus.FAILED in valid_results:
            return ServiceStatus.FAILED
        
        # Se qualquer verificação indica degradação, o serviço está degradado
        if ServiceStatus.DEGRADED in valid_results:
            return ServiceStatus.DEGRADED
        
        # Se todas as verificações indicam saúde, o serviço está saudável
        if all(r == ServiceStatus.HEALTHY for r in valid_results):
            return ServiceStatus.HEALTHY
        
        # Caso padrão
        return ServiceStatus.DEGRADED
    
    def _combine_metrics(self, metric_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combina métricas de diferentes fontes"""
        combined = {}
        
        for metrics in metric_results:
            if isinstance(metrics, dict):
                combined.update(metrics)
        
        return combined
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Obtém visão geral do sistema"""
        try:
            # Métricas básicas do sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Contar processos
            process_count = len(psutil.pids())
            
            # Informações de rede
            network = psutil.net_io_counters()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "memory_available": memory.available,
                    "disk_usage": disk.percent,
                    "disk_free": disk.free,
                    "process_count": process_count,
                    "network_io": {
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv
                    }
                },
                "cache": {
                    "health_cache_size": len(self.health_cache),
                    "metrics_cache_size": len(self.metrics_cache)
                }
            }
        
        except Exception as e:
            logger.error(f"[HEALING_MONITOR] Erro ao obter visão geral do sistema: {e}")
            return {}
    
    def clear_cache(self):
        """Limpa o cache de métricas e saúde"""
        with self.cache_lock:
            self.metrics_cache.clear()
            self.health_cache.clear()
        
        logger.info("[HEALING_MONITOR] Cache limpo")
    
    async def cleanup_old_cache(self):
        """Remove entradas antigas do cache"""
        current_time = time.time()
        
        with self.cache_lock:
            # Limpar cache de saúde (mais de 5 minutos)
            old_health_keys = [
                key for key in self.health_cache.keys()
                if current_time - int(key.split('_')[-1]) * 30 > 300
            ]
            for key in old_health_keys:
                del self.health_cache[key]
            
            # Limpar cache de métricas (mais de 2 minutos)
            old_metrics_keys = [
                key for key in self.metrics_cache.keys()
                if current_time - int(key.split('_')[-1]) * 15 > 120
            ]
            for key in old_metrics_keys:
                del self.metrics_cache[key]
        
        if old_health_keys or old_metrics_keys:
            logger.debug(f"[HEALING_MONITOR] Cache limpo: {len(old_health_keys)} health, {len(old_metrics_keys)} metrics") 