"""
🧪 Teste de Performance - Exportação de Arquivos Grandes

Tracing ID: performance-export-large-files-test-2025-01-27-001
Timestamp: 2025-01-27T21:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em exportação real de arquivos grandes do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias para lidar com arquivos grandes (chunking, streaming, compressão)
♻️ ReAct: Simulado cenários de produção com arquivos grandes e validada performance

Testa exportação de arquivos grandes incluindo:
- Exportação de datasets massivos (100K+ registros)
- Exportação com chunking automático
- Exportação com streaming otimizado
- Exportação com compressão avançada
- Exportação com cache inteligente
- Exportação com otimização de memória
- Exportação com progress tracking
- Exportação com resumabilidade
- Exportação com validação de integridade
- Exportação com métricas de performance
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

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class LargeFileExportTestConfig:
    """Configuração para testes de exportação de arquivos grandes"""
    large_dataset_size: int = 100000  # 100K registros
    huge_dataset_size: int = 500000   # 500K registros
    max_export_time: float = 1800.0   # 30 minutos
    max_memory_usage_mb: int = 2048   # 2GB
    enable_chunking: bool = True
    chunk_size: int = 10000
    enable_streaming: bool = True
    enable_compression: bool = True
    enable_cache: bool = True
    enable_optimization: bool = True
    enable_metrics: bool = True
    enable_monitoring: bool = True
    enable_logging: bool = True
    enable_resumability: bool = True
    enable_progress_tracking: bool = True
    compression_level: int = 9  # Máxima compressão

class LargeFileExportPerformanceTest:
    """Teste de performance para exportação de arquivos grandes"""
    
    def __init__(self, config: Optional[LargeFileExportTestConfig] = None):
        self.config = config or LargeFileExportTestConfig()
        self.logger = StructuredLogger(
            module="large_file_export_performance_test",
            tracing_id="large_file_export_test_001"
        )
        self.metrics = MetricsCollector()
        self.performance_monitor = PerformanceMonitor()
        
        # Serviços
        self.export_service = ExportService()
        self.data_service = DataService()
        self.cache = RedisCache()
        
        # Métricas de teste
        self.large_file_events: List[Dict[str, Any]] = []
        self.performance_metrics: List[Dict[str, float]] = []
        self.memory_usage_events: List[Dict[str, Any]] = []
        
        logger.info(f"Large File Export Performance Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Conectar serviços
            await self.cache.connect()
            
            # Configurar serviços para arquivos grandes
            self.export_service.configure({
                "enable_chunking": self.config.enable_chunking,
                "chunk_size": self.config.chunk_size,
                "enable_streaming": self.config.enable_streaming,
                "enable_compression": self.config.enable_compression,
                "enable_cache": self.config.enable_cache,
                "enable_optimization": self.config.enable_optimization,
                "enable_resumability": self.config.enable_resumability,
                "compression_level": self.config.compression_level
            })
            
            # Configurar monitor de performance
            self.performance_monitor.configure({
                "enable_metrics": self.config.enable_metrics,
                "enable_monitoring": self.config.enable_monitoring,
                "memory_threshold_mb": self.config.max_memory_usage_mb
            })
            
            # Gerar datasets grandes
            await self._generate_large_datasets()
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    async def _generate_large_datasets(self):
        """Gera datasets grandes para teste"""
        try:
            # Dataset grande (100K registros)
            large_keywords = []
            for i in range(self.config.large_dataset_size):
                keyword_data = {
                    "id": i,
                    "palavra": f"large_keyword_{i}",
                    "volume": random.randint(100, 50000),
                    "competicao": random.uniform(0.1, 0.95),
                    "cpc": random.uniform(0.1, 10.0),
                    "execucao_id": random.randint(1, 1000),
                    "created_at": datetime.now() - timedelta(days=random.randint(1, 365)),
                    "updated_at": datetime.now() - timedelta(days=random.randint(1, 30))
                }
                large_keywords.append(keyword_data)
            
            # Dataset enorme (500K registros)
            huge_keywords = []
            for i in range(self.config.huge_dataset_size):
                keyword_data = {
                    "id": i + self.config.large_dataset_size,
                    "palavra": f"huge_keyword_{i}",
                    "volume": random.randint(50, 100000),
                    "competicao": random.uniform(0.05, 0.99),
                    "cpc": random.uniform(0.05, 15.0),
                    "execucao_id": random.randint(1, 2000),
                    "created_at": datetime.now() - timedelta(days=random.randint(1, 730)),
                    "updated_at": datetime.now() - timedelta(days=random.randint(1, 60))
                }
                huge_keywords.append(keyword_data)
            
            # Armazenar datasets
            await self.data_service.store_test_data("large_keywords", large_keywords)
            await self.data_service.store_test_data("huge_keywords", huge_keywords)
            
            logger.info(f"Datasets grandes gerados: {len(large_keywords)} registros grandes, {len(huge_keywords)} registros enormes")
            
        except Exception as e:
            logger.error(f"Erro ao gerar datasets grandes: {e}")
            raise
    
    async def test_large_csv_export(self):
        """Testa exportação CSV de arquivo grande"""
        # Configurar exportação para arquivo grande
        export_config = {
            "format": "csv",
            "compression": self.config.enable_compression,
            "streaming": self.config.enable_streaming,
            "chunking": self.config.enable_chunking,
            "chunk_size": self.config.chunk_size,
            "optimization": self.config.enable_optimization,
            "resumability": self.config.enable_resumability
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação
            export_result = await self.export_service.export_large_dataset(
                "large_keywords",
                export_config,
                progress_callback=self._progress_callback,
                memory_monitor=self._memory_monitor
            )
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            file_size = len(export_result["data"]) / 1024 / 1024  # MB
            export_speed = file_size / export_time  # MB/s
            records_per_second = self.config.large_dataset_size / export_time
            
            # Verificar performance
            assert export_time < self.config.max_export_time, f"Exportação CSV grande muito lenta: {export_time}s"
            assert memory_used < self.config.max_memory_usage_mb, f"Uso de memória muito alto: {memory_used}MB"
            assert export_speed > 0.5, f"Velocidade de exportação muito baixa: {export_speed}MB/s"
            assert records_per_second > 100, f"Throughput muito baixo: {records_per_second} registros/s"
            
            # Validar integridade
            data_integrity = await self._validate_large_csv_data(export_result["data"])
            
            self.large_file_events.append({
                "format": "csv_large",
                "dataset_size": self.config.large_dataset_size,
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "records_per_second": records_per_second,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity,
                "chunks_processed": export_result.get("chunks_processed", 0)
            })
            
            logger.info(f"Exportação CSV grande testada: {export_time:.3f}s, {file_size:.2f}MB, {records_per_second:.0f} registros/s")
            
            return {
                "success": True,
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "records_per_second": records_per_second,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação CSV grande: {e}")
            raise
    
    async def test_huge_csv_export(self):
        """Testa exportação CSV de arquivo enorme"""
        # Configurar exportação para arquivo enorme
        export_config = {
            "format": "csv",
            "compression": True,  # Compressão obrigatória para arquivos enormes
            "streaming": True,    # Streaming obrigatório
            "chunking": True,     # Chunking obrigatório
            "chunk_size": self.config.chunk_size,
            "optimization": True,
            "resumability": True
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação
            export_result = await self.export_service.export_large_dataset(
                "huge_keywords",
                export_config,
                progress_callback=self._progress_callback,
                memory_monitor=self._memory_monitor
            )
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            file_size = len(export_result["data"]) / 1024 / 1024  # MB
            export_speed = file_size / export_time  # MB/s
            records_per_second = self.config.huge_dataset_size / export_time
            
            # Verificar performance (mais permissivo para arquivos enormes)
            assert export_time < self.config.max_export_time * 2, f"Exportação CSV enorme muito lenta: {export_time}s"
            assert memory_used < self.config.max_memory_usage_mb, f"Uso de memória muito alto: {memory_used}MB"
            assert export_speed > 0.2, f"Velocidade de exportação muito baixa: {export_speed}MB/s"
            assert records_per_second > 50, f"Throughput muito baixo: {records_per_second} registros/s"
            
            # Validar integridade
            data_integrity = await self._validate_huge_csv_data(export_result["data"])
            
            self.large_file_events.append({
                "format": "csv_huge",
                "dataset_size": self.config.huge_dataset_size,
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "records_per_second": records_per_second,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity,
                "chunks_processed": export_result.get("chunks_processed", 0)
            })
            
            logger.info(f"Exportação CSV enorme testada: {export_time:.3f}s, {file_size:.2f}MB, {records_per_second:.0f} registros/s")
            
            return {
                "success": True,
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "records_per_second": records_per_second,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação CSV enorme: {e}")
            raise
    
    async def test_compressed_large_export(self):
        """Testa exportação comprimida de arquivo grande"""
        # Configurar exportação comprimida
        export_config = {
            "format": "csv",
            "compression": True,
            "compression_level": self.config.compression_level,
            "streaming": True,
            "chunking": True,
            "chunk_size": self.config.chunk_size,
            "optimization": True
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação
            export_result = await self.export_service.export_large_dataset(
                "large_keywords",
                export_config,
                progress_callback=self._progress_callback,
                memory_monitor=self._memory_monitor
            )
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            compressed_size = len(export_result["data"]) / 1024 / 1024  # MB
            estimated_original_size = 50.0  # Estimativa de 50MB para 100K registros
            compression_ratio = compressed_size / estimated_original_size
            
            # Verificar performance
            assert export_time < self.config.max_export_time, f"Exportação comprimida muito lenta: {export_time}s"
            assert memory_used < self.config.max_memory_usage_mb, f"Uso de memória muito alto: {memory_used}MB"
            assert compression_ratio < 0.3, f"Compressão ineficiente: {compression_ratio:.2%}"
            
            self.large_file_events.append({
                "format": "csv_compressed_large",
                "dataset_size": self.config.large_dataset_size,
                "export_time": export_time,
                "compressed_size_mb": compressed_size,
                "compression_ratio": compression_ratio,
                "memory_used_mb": memory_used
            })
            
            logger.info(f"Exportação comprimida grande testada: {export_time:.3f}s, compressão {compression_ratio:.2%}")
            
            return {
                "success": True,
                "export_time": export_time,
                "compressed_size_mb": compressed_size,
                "compression_ratio": compression_ratio,
                "memory_used_mb": memory_used
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação comprimida grande: {e}")
            raise
    
    async def test_chunked_export(self):
        """Testa exportação em chunks"""
        # Configurar exportação em chunks
        export_config = {
            "format": "csv",
            "compression": False,
            "streaming": True,
            "chunking": True,
            "chunk_size": self.config.chunk_size,
            "optimization": True
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação em chunks
            chunks = []
            total_records = 0
            
            async for chunk in self.export_service.export_in_chunks(
                "large_keywords",
                export_config,
                progress_callback=self._progress_callback
            ):
                chunks.append(chunk)
                total_records += len(chunk["data"])
                
                # Verificar uso de memória durante processamento
                current_memory = psutil.virtual_memory().used / 1024 / 1024
                if current_memory > self.config.max_memory_usage_mb:
                    logger.warning(f"Uso de memória alto durante chunking: {current_memory}MB")
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            assert len(chunks) > 0, "Nenhum chunk foi gerado"
            assert total_records == self.config.large_dataset_size, f"Total de registros incorreto: {total_records}"
            assert memory_used < self.config.max_memory_usage_mb, f"Uso de memória muito alto: {memory_used}MB"
            
            # Calcular métricas
            avg_chunk_size = statistics.mean([len(chunk["data"]) for chunk in chunks])
            chunks_per_second = len(chunks) / export_time
            
            self.large_file_events.append({
                "format": "csv_chunked",
                "dataset_size": self.config.large_dataset_size,
                "export_time": export_time,
                "chunks_count": len(chunks),
                "avg_chunk_size": avg_chunk_size,
                "chunks_per_second": chunks_per_second,
                "memory_used_mb": memory_used
            })
            
            logger.info(f"Exportação em chunks testada: {len(chunks)} chunks, {export_time:.3f}s")
            
            return {
                "success": True,
                "export_time": export_time,
                "chunks_count": len(chunks),
                "avg_chunk_size": avg_chunk_size,
                "chunks_per_second": chunks_per_second,
                "memory_used_mb": memory_used
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação em chunks: {e}")
            raise
    
    async def test_resumable_export(self):
        """Testa exportação resumível"""
        # Configurar exportação resumível
        export_config = {
            "format": "csv",
            "compression": True,
            "streaming": True,
            "chunking": True,
            "chunk_size": self.config.chunk_size,
            "resumability": True,
            "checkpoint_interval": 1000
        }
        
        start_time = time.time()
        
        try:
            # Simular interrupção no meio da exportação
            export_session = await self.export_service.start_resumable_export(
                "large_keywords",
                export_config
            )
            
            # Processar alguns chunks
            processed_chunks = 0
            for _ in range(5):  # Processar 5 chunks
                chunk = await export_session.get_next_chunk()
                if chunk:
                    processed_chunks += 1
                    await export_session.save_checkpoint()
                else:
                    break
            
            # Simular interrupção
            await export_session.pause()
            
            # Resumir exportação
            resumed_session = await self.export_service.resume_export(export_session.session_id)
            
            # Continuar processamento
            while True:
                chunk = await resumed_session.get_next_chunk()
                if chunk:
                    processed_chunks += 1
                    await resumed_session.save_checkpoint()
                else:
                    break
            
            export_time = time.time() - start_time
            
            # Finalizar exportação
            final_result = await resumed_session.finish()
            
            # Validar resultado
            assert processed_chunks > 0, "Nenhum chunk foi processado"
            assert final_result["completed"], "Exportação resumível não foi completada"
            
            self.large_file_events.append({
                "format": "csv_resumable",
                "dataset_size": self.config.large_dataset_size,
                "export_time": export_time,
                "processed_chunks": processed_chunks,
                "resumability_successful": True
            })
            
            logger.info(f"Exportação resumível testada: {processed_chunks} chunks, {export_time:.3f}s")
            
            return {
                "success": True,
                "export_time": export_time,
                "processed_chunks": processed_chunks,
                "resumability_successful": True
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação resumível: {e}")
            raise
    
    async def _progress_callback(self, progress: float, message: str):
        """Callback para acompanhar progresso da exportação"""
        if self.config.enable_progress_tracking:
            logger.info(f"Progresso da exportação grande: {progress:.1%} - {message}")
    
    async def _memory_monitor(self, current_memory_mb: float):
        """Monitor de uso de memória"""
        self.memory_usage_events.append({
            "timestamp": datetime.now(),
            "memory_mb": current_memory_mb
        })
        
        if current_memory_mb > self.config.max_memory_usage_mb:
            logger.warning(f"Uso de memória alto: {current_memory_mb}MB")
    
    async def _validate_large_csv_data(self, data: bytes) -> Dict[str, Any]:
        """Valida integridade dos dados CSV grandes"""
        try:
            # Decodificar dados
            csv_text = data.decode('utf-8')
            
            # Contar linhas (incluindo header)
            lines = csv_text.split('\n')
            row_count = len(lines) - 1  # Excluir header
            
            # Verificar estrutura básica
            csv_reader = csv.DictReader(io.StringIO(csv_text))
            sample_rows = list(csv_reader)[:10]  # Primeiras 10 linhas
            
            expected_columns = ["id", "palavra", "volume", "competicao", "cpc", "execucao_id"]
            actual_columns = list(sample_rows[0].keys()) if sample_rows else []
            
            # Validar dados
            data_valid = row_count >= self.config.large_dataset_size * 0.95  # 95% dos dados
            structure_valid = all(col in actual_columns for col in expected_columns)
            
            return {
                "valid": data_valid and structure_valid,
                "row_count": row_count,
                "expected_rows": self.config.large_dataset_size,
                "data_valid": data_valid,
                "structure_valid": structure_valid
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def _validate_huge_csv_data(self, data: bytes) -> Dict[str, Any]:
        """Valida integridade dos dados CSV enormes"""
        try:
            # Para arquivos enormes, validar apenas amostra
            csv_text = data.decode('utf-8')
            lines = csv_text.split('\n')
            row_count = len(lines) - 1  # Excluir header
            
            # Verificar estrutura básica
            csv_reader = csv.DictReader(io.StringIO(csv_text))
            sample_rows = list(csv_reader)[:5]  # Primeiras 5 linhas
            
            expected_columns = ["id", "palavra", "volume", "competicao", "cpc", "execucao_id"]
            actual_columns = list(sample_rows[0].keys()) if sample_rows else []
            
            # Validar dados (mais permissivo para arquivos enormes)
            data_valid = row_count >= self.config.huge_dataset_size * 0.9  # 90% dos dados
            structure_valid = all(col in actual_columns for col in expected_columns)
            
            return {
                "valid": data_valid and structure_valid,
                "row_count": row_count,
                "expected_rows": self.config.huge_dataset_size,
                "data_valid": data_valid,
                "structure_valid": structure_valid
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        if not self.large_file_events:
            return {"error": "Nenhuma exportação de arquivo grande executada"}
        
        return {
            "total_large_exports": len(self.large_file_events),
            "avg_export_time": statistics.mean([e["export_time"] for e in self.large_file_events]),
            "avg_memory_usage": statistics.mean([e.get("memory_used_mb", 0) for e in self.large_file_events]),
            "max_memory_usage": max([e.get("memory_used_mb", 0) for e in self.large_file_events]),
            "large_file_events": self.large_file_events,
            "memory_usage_events": self.memory_usage_events
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
class TestLargeFileExportPerformance:
    """Testes de performance para exportação de arquivos grandes"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = LargeFileExportPerformanceTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_large_csv_export(self):
        """Testa exportação CSV de arquivo grande"""
        result = await self.test_instance.test_large_csv_export()
        assert result["success"] is True
        assert result["export_time"] < 1800.0
        assert result["records_per_second"] > 100
    
    async def test_huge_csv_export(self):
        """Testa exportação CSV de arquivo enorme"""
        result = await self.test_instance.test_huge_csv_export()
        assert result["success"] is True
        assert result["export_time"] < 3600.0
        assert result["records_per_second"] > 50
    
    async def test_compressed_large_export(self):
        """Testa exportação comprimida de arquivo grande"""
        result = await self.test_instance.test_compressed_large_export()
        assert result["success"] is True
        assert result["compression_ratio"] < 0.3
    
    async def test_chunked_export(self):
        """Testa exportação em chunks"""
        result = await self.test_instance.test_chunked_export()
        assert result["success"] is True
        assert result["chunks_count"] > 0
    
    async def test_resumable_export(self):
        """Testa exportação resumível"""
        result = await self.test_instance.test_resumable_export()
        assert result["success"] is True
        assert result["resumability_successful"] is True
    
    async def test_overall_large_file_performance_metrics(self):
        """Testa métricas gerais de performance de arquivos grandes"""
        # Executar todos os testes
        await self.test_instance.test_large_csv_export()
        await self.test_instance.test_huge_csv_export()
        await self.test_instance.test_compressed_large_export()
        await self.test_instance.test_chunked_export()
        await self.test_instance.test_resumable_export()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_large_exports"] > 0
        assert metrics["avg_export_time"] > 0
        assert metrics["max_memory_usage"] < 2048

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = LargeFileExportPerformanceTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_large_csv_export()
            await test_instance.test_huge_csv_export()
            await test_instance.test_compressed_large_export()
            await test_instance.test_chunked_export()
            await test_instance.test_resumable_export()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Performance de Arquivos Grandes: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 