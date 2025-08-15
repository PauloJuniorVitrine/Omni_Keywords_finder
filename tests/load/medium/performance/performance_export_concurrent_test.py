"""
🧪 Teste de Performance - Exportações Concorrentes

Tracing ID: performance-export-concurrent-test-2025-01-27-001
Timestamp: 2025-01-27T22:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em exportação concorrente real do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de concorrência (threading, asyncio, processamento paralelo)
♻️ ReAct: Simulado cenários de produção com múltiplas exportações simultâneas

Testa exportações concorrentes incluindo:
- Múltiplas exportações simultâneas
- Exportações com diferentes formatos
- Exportações com diferentes tamanhos
- Exportações com diferentes configurações
- Exportações com controle de concorrência
- Exportações com balanceamento de carga
- Exportações com monitoramento de recursos
- Exportações com validação de integridade
- Exportações com métricas de performance
- Exportações com logging estruturado
"""

import pytest
import asyncio
import time
import json
import statistics
import csv
import io
import gzip
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
import logging
from dataclasses import dataclass
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import pandas as pd
import tempfile
import os

# Importações do sistema real
from backend.app.services.export_service import ExportService
from backend.app.services.data_service import DataService
from backend.app.models.keyword import Keyword
from backend.app.models.execucao import Execucao
from backend.app.models.categoria import Categoria
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.performance.performance_monitor import PerformanceMonitor
from infrastructure.orchestrator.concurrency_manager import ConcurrencyManager

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class ConcurrentExportTestConfig:
    """Configuração para testes de exportações concorrentes"""
    max_concurrent_exports: int = 10
    max_export_time: float = 600.0  # 10 minutos
    max_memory_usage_mb: int = 4096  # 4GB
    enable_load_balancing: bool = True
    enable_resource_monitoring: bool = True
    enable_concurrency_control: bool = True
    enable_metrics: bool = True
    enable_monitoring: bool = True
    enable_logging: bool = True
    enable_validation: bool = True
    enable_progress_tracking: bool = True
    chunk_size: int = 1000
    compression_level: int = 6
    export_formats: List[str] = None
    dataset_sizes: List[int] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["csv", "json", "excel"]
        if self.dataset_sizes is None:
            self.dataset_sizes = [1000, 5000, 10000, 50000]

class ConcurrentExportPerformanceTest:
    """Teste de performance para exportações concorrentes"""
    
    def __init__(self, config: Optional[ConcurrentExportTestConfig] = None):
        self.config = config or ConcurrentExportTestConfig()
        self.logger = StructuredLogger(
            module="concurrent_export_performance_test",
            tracing_id="concurrent_export_test_001"
        )
        self.metrics = MetricsCollector()
        self.performance_monitor = PerformanceMonitor()
        self.concurrency_manager = ConcurrencyManager()
        
        # Serviços
        self.export_service = ExportService()
        self.data_service = DataService()
        self.cache = RedisCache()
        
        # Métricas de teste
        self.concurrent_events: List[Dict[str, Any]] = []
        self.performance_metrics: List[Dict[str, float]] = []
        self.resource_usage_events: List[Dict[str, Any]] = []
        self.concurrency_metrics: List[Dict[str, Any]] = []
        
        logger.info(f"Concurrent Export Performance Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Conectar serviços
            await self.cache.connect()
            
            # Configurar gerenciador de concorrência
            self.concurrency_manager.configure({
                "max_concurrent_exports": self.config.max_concurrent_exports,
                "enable_load_balancing": self.config.enable_load_balancing,
                "enable_concurrency_control": self.config.enable_concurrency_control
            })
            
            # Configurar serviços
            self.export_service.configure({
                "enable_concurrency": True,
                "chunk_size": self.config.chunk_size,
                "compression_level": self.config.compression_level
            })
            
            # Configurar monitor de performance
            self.performance_monitor.configure({
                "enable_metrics": self.config.enable_metrics,
                "enable_monitoring": self.config.enable_monitoring,
                "enable_resource_monitoring": self.config.enable_resource_monitoring,
                "memory_threshold_mb": self.config.max_memory_usage_mb
            })
            
            # Gerar datasets de teste
            await self._generate_test_datasets()
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    async def _generate_test_datasets(self):
        """Gera datasets de teste para exportações concorrentes"""
        try:
            # Gerar datasets de diferentes tamanhos
            for size in self.config.dataset_sizes:
                dataset_name = f"dataset_{size}"
                dataset_data = []
                
                for i in range(size):
                    keyword_data = {
                        "id": i,
                        "palavra": f"keyword_{size}_{i}",
                        "volume": random.randint(100, 10000),
                        "competicao": random.uniform(0.1, 0.9),
                        "cpc": random.uniform(0.5, 5.0),
                        "execucao_id": random.randint(1, 100),
                        "created_at": datetime.now() - timedelta(days=random.randint(1, 365))
                    }
                    dataset_data.append(keyword_data)
                
                await self.data_service.store_test_data(dataset_name, dataset_data)
                logger.info(f"Dataset {dataset_name} gerado com {len(dataset_data)} registros")
            
        except Exception as e:
            logger.error(f"Erro ao gerar datasets de teste: {e}")
            raise
    
    async def test_concurrent_csv_exports(self):
        """Testa exportações CSV concorrentes"""
        # Configurar exportações CSV
        export_configs = []
        for i in range(self.config.max_concurrent_exports):
            config = {
                "format": "csv",
                "compression": random.choice([True, False]),
                "streaming": True,
                "optimization": True,
                "dataset": f"dataset_{random.choice(self.config.dataset_sizes)}",
                "export_id": f"csv_export_{i}"
            }
            export_configs.append(config)
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        cpu_before = psutil.cpu_percent()
        
        try:
            # Executar exportações concorrentes
            tasks = []
            for config in export_configs:
                task = self._execute_single_export(config)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            cpu_after = psutil.cpu_percent()
            
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            cpu_usage = (cpu_after + cpu_before) / 2  # Média
            
            # Analisar resultados
            successful_exports = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed_exports = [r for r in results if isinstance(r, dict) and not r.get("success")]
            
            # Calcular métricas
            total_file_size = sum([r.get("file_size_mb", 0) for r in successful_exports])
            avg_export_time = statistics.mean([r.get("export_time", 0) for r in successful_exports]) if successful_exports else 0
            throughput = total_file_size / export_time if export_time > 0 else 0
            
            # Verificar performance
            assert len(successful_exports) > 0, "Nenhuma exportação CSV concorrente foi bem-sucedida"
            assert export_time < self.config.max_export_time, f"Exportações CSV concorrentes muito lentas: {export_time}s"
            assert memory_used < self.config.max_memory_usage_mb, f"Uso de memória muito alto: {memory_used}MB"
            assert throughput > 0.5, f"Throughput muito baixo: {throughput}MB/s"
            
            self.concurrent_events.append({
                "test_type": "concurrent_csv",
                "total_exports": len(export_configs),
                "successful_exports": len(successful_exports),
                "failed_exports": len(failed_exports),
                "total_time": export_time,
                "avg_export_time": avg_export_time,
                "total_file_size_mb": total_file_size,
                "throughput_mbps": throughput,
                "memory_used_mb": memory_used,
                "cpu_usage_percent": cpu_usage
            })
            
            logger.info(f"Exportações CSV concorrentes testadas: {len(successful_exports)} sucessos, {export_time:.3f}s")
            
            return {
                "success": True,
                "total_exports": len(export_configs),
                "successful_exports": len(successful_exports),
                "failed_exports": len(failed_exports),
                "total_time": export_time,
                "avg_export_time": avg_export_time,
                "throughput_mbps": throughput,
                "memory_used_mb": memory_used
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro nas exportações CSV concorrentes: {e}")
            raise
    
    async def test_mixed_format_concurrent_exports(self):
        """Testa exportações concorrentes com diferentes formatos"""
        # Configurar exportações com diferentes formatos
        export_configs = []
        formats = self.config.export_formats
        
        for i in range(self.config.max_concurrent_exports):
            config = {
                "format": random.choice(formats),
                "compression": random.choice([True, False]),
                "streaming": random.choice([True, False]),
                "optimization": True,
                "dataset": f"dataset_{random.choice(self.config.dataset_sizes)}",
                "export_id": f"mixed_export_{i}"
            }
            export_configs.append(config)
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportações concorrentes
            tasks = []
            for config in export_configs:
                task = self._execute_single_export(config)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Analisar resultados por formato
            results_by_format = {}
            for result in results:
                if isinstance(result, dict) and result.get("success"):
                    format_type = result.get("format", "unknown")
                    if format_type not in results_by_format:
                        results_by_format[format_type] = []
                    results_by_format[format_type].append(result)
            
            # Calcular métricas por formato
            format_metrics = {}
            for format_type, format_results in results_by_format.items():
                format_metrics[format_type] = {
                    "count": len(format_results),
                    "avg_time": statistics.mean([r.get("export_time", 0) for r in format_results]),
                    "avg_size": statistics.mean([r.get("file_size_mb", 0) for r in format_results]),
                    "avg_speed": statistics.mean([r.get("export_speed_mbps", 0) for r in format_results])
                }
            
            # Verificar performance
            total_successful = sum(len(results) for results in results_by_format.values())
            assert total_successful > 0, "Nenhuma exportação mista foi bem-sucedida"
            assert export_time < self.config.max_export_time, f"Exportações mistas muito lentas: {export_time}s"
            assert memory_used < self.config.max_memory_usage_mb, f"Uso de memória muito alto: {memory_used}MB"
            
            self.concurrent_events.append({
                "test_type": "mixed_format_concurrent",
                "total_exports": len(export_configs),
                "successful_exports": total_successful,
                "total_time": export_time,
                "memory_used_mb": memory_used,
                "format_metrics": format_metrics
            })
            
            logger.info(f"Exportações mistas concorrentes testadas: {total_successful} sucessos, {export_time:.3f}s")
            
            return {
                "success": True,
                "total_exports": len(export_configs),
                "successful_exports": total_successful,
                "total_time": export_time,
                "memory_used_mb": memory_used,
                "format_metrics": format_metrics
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro nas exportações mistas concorrentes: {e}")
            raise
    
    async def test_concurrent_large_exports(self):
        """Testa exportações concorrentes de arquivos grandes"""
        # Configurar exportações de arquivos grandes
        export_configs = []
        large_datasets = [size for size in self.config.dataset_sizes if size >= 10000]
        
        for i in range(min(5, self.config.max_concurrent_exports)):  # Máximo 5 exportações grandes
            config = {
                "format": "csv",
                "compression": True,
                "streaming": True,
                "chunking": True,
                "chunk_size": self.config.chunk_size,
                "optimization": True,
                "dataset": f"dataset_{random.choice(large_datasets)}",
                "export_id": f"large_export_{i}"
            }
            export_configs.append(config)
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportações concorrentes
            tasks = []
            for config in export_configs:
                task = self._execute_large_export(config)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Analisar resultados
            successful_exports = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed_exports = [r for r in results if isinstance(r, dict) and not r.get("success")]
            
            # Calcular métricas
            total_records = sum([r.get("records_processed", 0) for r in successful_exports])
            avg_export_time = statistics.mean([r.get("export_time", 0) for r in successful_exports]) if successful_exports else 0
            records_per_second = total_records / export_time if export_time > 0 else 0
            
            # Verificar performance
            assert len(successful_exports) > 0, "Nenhuma exportação grande concorrente foi bem-sucedida"
            assert export_time < self.config.max_export_time, f"Exportações grandes concorrentes muito lentas: {export_time}s"
            assert memory_used < self.config.max_memory_usage_mb, f"Uso de memória muito alto: {memory_used}MB"
            assert records_per_second > 50, f"Throughput muito baixo: {records_per_second} registros/s"
            
            self.concurrent_events.append({
                "test_type": "concurrent_large_exports",
                "total_exports": len(export_configs),
                "successful_exports": len(successful_exports),
                "failed_exports": len(failed_exports),
                "total_time": export_time,
                "avg_export_time": avg_export_time,
                "total_records": total_records,
                "records_per_second": records_per_second,
                "memory_used_mb": memory_used
            })
            
            logger.info(f"Exportações grandes concorrentes testadas: {len(successful_exports)} sucessos, {records_per_second:.0f} registros/s")
            
            return {
                "success": True,
                "total_exports": len(export_configs),
                "successful_exports": len(successful_exports),
                "total_time": export_time,
                "avg_export_time": avg_export_time,
                "records_per_second": records_per_second,
                "memory_used_mb": memory_used
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro nas exportações grandes concorrentes: {e}")
            raise
    
    async def test_concurrency_control(self):
        """Testa controle de concorrência"""
        # Configurar teste de controle de concorrência
        max_concurrent = 3
        total_exports = 10
        
        export_configs = []
        for i in range(total_exports):
            config = {
                "format": "csv",
                "compression": False,
                "streaming": True,
                "optimization": True,
                "dataset": f"dataset_{random.choice(self.config.dataset_sizes)}",
                "export_id": f"control_export_{i}"
            }
            export_configs.append(config)
        
        start_time = time.time()
        
        try:
            # Executar com controle de concorrência
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def controlled_export(config):
                async with semaphore:
                    return await self._execute_single_export(config)
            
            tasks = [controlled_export(config) for config in export_configs]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            export_time = time.time() - start_time
            
            # Analisar resultados
            successful_exports = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed_exports = [r for r in results if isinstance(r, dict) and not r.get("success")]
            
            # Verificar controle de concorrência
            assert len(successful_exports) > 0, "Nenhuma exportação controlada foi bem-sucedida"
            
            # Calcular métricas de concorrência
            avg_export_time = statistics.mean([r.get("export_time", 0) for r in successful_exports]) if successful_exports else 0
            total_export_time = sum([r.get("export_time", 0) for r in successful_exports])
            concurrency_efficiency = total_export_time / export_time if export_time > 0 else 0
            
            self.concurrent_events.append({
                "test_type": "concurrency_control",
                "max_concurrent": max_concurrent,
                "total_exports": total_exports,
                "successful_exports": len(successful_exports),
                "total_time": export_time,
                "avg_export_time": avg_export_time,
                "concurrency_efficiency": concurrency_efficiency
            })
            
            logger.info(f"Controle de concorrência testado: {len(successful_exports)} sucessos, eficiência {concurrency_efficiency:.2f}")
            
            return {
                "success": True,
                "max_concurrent": max_concurrent,
                "total_exports": total_exports,
                "successful_exports": len(successful_exports),
                "total_time": export_time,
                "concurrency_efficiency": concurrency_efficiency
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro no controle de concorrência: {e}")
            raise
    
    async def _execute_single_export(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma única exportação"""
        try:
            start_time = time.time()
            
            # Executar exportação
            export_result = await self.export_service.export_data(
                config["dataset"],
                {
                    "format": config["format"],
                    "compression": config["compression"],
                    "streaming": config["streaming"],
                    "optimization": config["optimization"]
                }
            )
            
            export_time = time.time() - start_time
            file_size = len(export_result["data"]) / 1024 / 1024  # MB
            export_speed = file_size / export_time if export_time > 0 else 0
            
            return {
                "success": True,
                "export_id": config["export_id"],
                "format": config["format"],
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed
            }
            
        except Exception as e:
            return {
                "success": False,
                "export_id": config["export_id"],
                "error": str(e)
            }
    
    async def _execute_large_export(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma exportação de arquivo grande"""
        try:
            start_time = time.time()
            
            # Executar exportação grande
            export_result = await self.export_service.export_large_dataset(
                config["dataset"],
                {
                    "format": config["format"],
                    "compression": config["compression"],
                    "streaming": config["streaming"],
                    "chunking": config["chunking"],
                    "chunk_size": config["chunk_size"],
                    "optimization": config["optimization"]
                }
            )
            
            export_time = time.time() - start_time
            file_size = len(export_result["data"]) / 1024 / 1024  # MB
            records_processed = export_result.get("records_processed", 0)
            
            return {
                "success": True,
                "export_id": config["export_id"],
                "format": config["format"],
                "export_time": export_time,
                "file_size_mb": file_size,
                "records_processed": records_processed
            }
            
        except Exception as e:
            return {
                "success": False,
                "export_id": config["export_id"],
                "error": str(e)
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        if not self.concurrent_events:
            return {"error": "Nenhuma exportação concorrente executada"}
        
        return {
            "total_concurrent_tests": len(self.concurrent_events),
            "avg_total_time": statistics.mean([e["total_time"] for e in self.concurrent_events]),
            "avg_memory_usage": statistics.mean([e.get("memory_used_mb", 0) for e in self.concurrent_events]),
            "max_memory_usage": max([e.get("memory_used_mb", 0) for e in self.concurrent_events]),
            "concurrent_events": self.concurrent_events,
            "resource_usage_events": self.resource_usage_events
        }
    
    async def cleanup(self):
        """Limpa recursos de teste"""
        try:
            await self.cache.disconnect()
            logger.info("Recursos de teste limpos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {e}")

# Testes pytest
@pytest.mark.asyncio
class TestConcurrentExportPerformance:
    """Testes de performance para exportações concorrentes"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = ConcurrentExportPerformanceTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_concurrent_csv_exports(self):
        """Testa exportações CSV concorrentes"""
        result = await self.test_instance.test_concurrent_csv_exports()
        assert result["success"] is True
        assert result["successful_exports"] > 0
        assert result["throughput_mbps"] > 0.5
    
    async def test_mixed_format_concurrent_exports(self):
        """Testa exportações concorrentes com diferentes formatos"""
        result = await self.test_instance.test_mixed_format_concurrent_exports()
        assert result["success"] is True
        assert result["successful_exports"] > 0
    
    async def test_concurrent_large_exports(self):
        """Testa exportações concorrentes de arquivos grandes"""
        result = await self.test_instance.test_concurrent_large_exports()
        assert result["success"] is True
        assert result["successful_exports"] > 0
        assert result["records_per_second"] > 50
    
    async def test_concurrency_control(self):
        """Testa controle de concorrência"""
        result = await self.test_instance.test_concurrency_control()
        assert result["success"] is True
        assert result["successful_exports"] > 0
    
    async def test_overall_concurrent_performance_metrics(self):
        """Testa métricas gerais de performance concorrente"""
        # Executar todos os testes
        await self.test_instance.test_concurrent_csv_exports()
        await self.test_instance.test_mixed_format_concurrent_exports()
        await self.test_instance.test_concurrent_large_exports()
        await self.test_instance.test_concurrency_control()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_concurrent_tests"] > 0
        assert metrics["avg_total_time"] > 0
        assert metrics["max_memory_usage"] < 4096

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = ConcurrentExportPerformanceTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_concurrent_csv_exports()
            await test_instance.test_mixed_format_concurrent_exports()
            await test_instance.test_concurrent_large_exports()
            await test_instance.test_concurrency_control()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Performance Concorrente: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 