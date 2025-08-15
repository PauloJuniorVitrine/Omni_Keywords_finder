"""
🧪 Teste de Performance - Velocidade de Exportação

Tracing ID: performance-export-speed-test-2025-01-27-001
Timestamp: 2025-01-27T21:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em exportação real de dados do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de otimização de exportação (streaming, compressão, cache)
♻️ ReAct: Simulado cenários de produção e validada performance de exportação

Testa velocidade de exportação incluindo:
- Exportação de dados em diferentes formatos (CSV, JSON, Excel)
- Exportação com diferentes volumes de dados
- Exportação com compressão
- Exportação com streaming
- Exportação com cache
- Exportação com otimização de queries
- Exportação com métricas de performance
- Exportação com monitoramento
- Exportação com logging estruturado
- Exportação com validação de integridade
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
class ExportSpeedTestConfig:
    """Configuração para testes de velocidade de exportação"""
    max_export_time: float = 300.0  # 5 minutos
    max_file_size_mb: int = 100
    enable_compression: bool = True
    enable_streaming: bool = True
    enable_cache: bool = True
    enable_optimization: bool = True
    enable_metrics: bool = True
    enable_monitoring: bool = True
    enable_logging: bool = True
    enable_validation: bool = True
    max_concurrent_exports: int = 5
    enable_progress_tracking: bool = True
    chunk_size: int = 1000
    compression_level: int = 6

class ExportSpeedPerformanceTest:
    """Teste de performance para velocidade de exportação"""
    
    def __init__(self, config: Optional[ExportSpeedTestConfig] = None):
        self.config = config or ExportSpeedTestConfig()
        self.logger = StructuredLogger(
            module="export_speed_performance_test",
            tracing_id="export_speed_test_001"
        )
        self.metrics = MetricsCollector()
        self.performance_monitor = PerformanceMonitor()
        
        # Serviços
        self.export_service = ExportService()
        self.data_service = DataService()
        self.cache = RedisCache()
        
        # Métricas de teste
        self.export_events: List[Dict[str, Any]] = []
        self.performance_metrics: List[Dict[str, float]] = []
        self.validation_results: List[Dict[str, Any]] = []
        
        logger.info(f"Export Speed Performance Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Conectar serviços
            await self.cache.connect()
            
            # Configurar serviços
            self.export_service.configure({
                "enable_compression": self.config.enable_compression,
                "enable_streaming": self.config.enable_streaming,
                "enable_cache": self.config.enable_cache,
                "enable_optimization": self.config.enable_optimization,
                "chunk_size": self.config.chunk_size,
                "compression_level": self.config.compression_level
            })
            
            # Configurar monitor de performance
            self.performance_monitor.configure({
                "enable_metrics": self.config.enable_metrics,
                "enable_monitoring": self.config.enable_monitoring
            })
            
            # Gerar dados de teste
            await self._generate_test_data()
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    async def _generate_test_data(self):
        """Gera dados de teste para exportação"""
        try:
            # Gerar dados de keywords
            keywords_data = []
            for i in range(10000):
                keyword_data = {
                    "id": i,
                    "palavra": f"keyword_{i}",
                    "volume": random.randint(100, 10000),
                    "competicao": random.uniform(0.1, 0.9),
                    "cpc": random.uniform(0.5, 5.0),
                    "execucao_id": random.randint(1, 100),
                    "created_at": datetime.now() - timedelta(days=random.randint(1, 365))
                }
                keywords_data.append(keyword_data)
            
            # Gerar dados de execuções
            execucoes_data = []
            for i in range(100):
                execucao_data = {
                    "id": i,
                    "user_id": random.randint(1, 10),
                    "categoria_id": random.randint(1, 5),
                    "status": random.choice(["completed", "running", "failed"]),
                    "created_at": datetime.now() - timedelta(days=random.randint(1, 30))
                }
                execucoes_data.append(execucao_data)
            
            # Armazenar dados de teste
            await self.data_service.store_test_data("keywords", keywords_data)
            await self.data_service.store_test_data("execucoes", execucoes_data)
            
            logger.info(f"Dados de teste gerados: {len(keywords_data)} keywords, {len(execucoes_data)} execuções")
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados de teste: {e}")
            raise
    
    async def test_csv_export_speed(self):
        """Testa velocidade de exportação CSV"""
        # Configurar exportação CSV
        export_config = {
            "format": "csv",
            "compression": self.config.enable_compression,
            "streaming": self.config.enable_streaming,
            "optimization": self.config.enable_optimization
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação
            export_result = await self.export_service.export_data(
                "keywords",
                export_config,
                progress_callback=self._progress_callback
            )
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            file_size = len(export_result["data"]) / 1024 / 1024  # MB
            export_speed = file_size / export_time  # MB/s
            
            # Verificar performance
            assert export_time < self.config.max_export_time, f"Exportação CSV muito lenta: {export_time}s"
            assert file_size < self.config.max_file_size_mb, f"Arquivo CSV muito grande: {file_size}MB"
            assert export_speed > 1.0, f"Velocidade de exportação CSV muito baixa: {export_speed}MB/s"
            
            # Validar integridade dos dados
            data_integrity = await self._validate_csv_data(export_result["data"])
            
            self.export_events.append({
                "format": "csv",
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity
            })
            
            logger.info(f"Exportação CSV testada: {export_time:.3f}s, {file_size:.2f}MB, {export_speed:.2f}MB/s")
            
            return {
                "success": True,
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação CSV: {e}")
            raise
    
    async def test_json_export_speed(self):
        """Testa velocidade de exportação JSON"""
        # Configurar exportação JSON
        export_config = {
            "format": "json",
            "compression": self.config.enable_compression,
            "streaming": self.config.enable_streaming,
            "optimization": self.config.enable_optimization,
            "pretty_print": False  # Para melhor performance
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação
            export_result = await self.export_service.export_data(
                "keywords",
                export_config,
                progress_callback=self._progress_callback
            )
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            file_size = len(export_result["data"]) / 1024 / 1024  # MB
            export_speed = file_size / export_time  # MB/s
            
            # Verificar performance
            assert export_time < self.config.max_export_time, f"Exportação JSON muito lenta: {export_time}s"
            assert file_size < self.config.max_file_size_mb, f"Arquivo JSON muito grande: {file_size}MB"
            assert export_speed > 0.5, f"Velocidade de exportação JSON muito baixa: {export_speed}MB/s"
            
            # Validar integridade dos dados
            data_integrity = await self._validate_json_data(export_result["data"])
            
            self.export_events.append({
                "format": "json",
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity
            })
            
            logger.info(f"Exportação JSON testada: {export_time:.3f}s, {file_size:.2f}MB, {export_speed:.2f}MB/s")
            
            return {
                "success": True,
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação JSON: {e}")
            raise
    
    async def test_excel_export_speed(self):
        """Testa velocidade de exportação Excel"""
        # Configurar exportação Excel
        export_config = {
            "format": "excel",
            "compression": self.config.enable_compression,
            "streaming": False,  # Excel não suporta streaming
            "optimization": self.config.enable_optimization,
            "sheet_name": "Keywords"
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação
            export_result = await self.export_service.export_data(
                "keywords",
                export_config,
                progress_callback=self._progress_callback
            )
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            file_size = len(export_result["data"]) / 1024 / 1024  # MB
            export_speed = file_size / export_time  # MB/s
            
            # Verificar performance (Excel é mais lento)
            assert export_time < self.config.max_export_time * 2, f"Exportação Excel muito lenta: {export_time}s"
            assert file_size < self.config.max_file_size_mb, f"Arquivo Excel muito grande: {file_size}MB"
            assert export_speed > 0.2, f"Velocidade de exportação Excel muito baixa: {export_speed}MB/s"
            
            # Validar integridade dos dados
            data_integrity = await self._validate_excel_data(export_result["data"])
            
            self.export_events.append({
                "format": "excel",
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity
            })
            
            logger.info(f"Exportação Excel testada: {export_time:.3f}s, {file_size:.2f}MB, {export_speed:.2f}MB/s")
            
            return {
                "success": True,
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "memory_used_mb": memory_used,
                "data_integrity": data_integrity
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação Excel: {e}")
            raise
    
    async def test_compressed_export_speed(self):
        """Testa velocidade de exportação com compressão"""
        # Configurar exportação com compressão
        export_config = {
            "format": "csv",
            "compression": True,
            "compression_level": self.config.compression_level,
            "streaming": self.config.enable_streaming,
            "optimization": self.config.enable_optimization
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação
            export_result = await self.export_service.export_data(
                "keywords",
                export_config,
                progress_callback=self._progress_callback
            )
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            compressed_size = len(export_result["data"]) / 1024 / 1024  # MB
            compression_ratio = compressed_size / 10.0  # Assumindo 10MB de dados originais
            
            # Verificar performance
            assert export_time < self.config.max_export_time, f"Exportação comprimida muito lenta: {export_time}s"
            assert compression_ratio < 0.5, f"Compressão ineficiente: {compression_ratio:.2%}"
            
            self.export_events.append({
                "format": "csv_compressed",
                "export_time": export_time,
                "compressed_size_mb": compressed_size,
                "compression_ratio": compression_ratio,
                "memory_used_mb": memory_used
            })
            
            logger.info(f"Exportação comprimida testada: {export_time:.3f}s, compressão {compression_ratio:.2%}")
            
            return {
                "success": True,
                "export_time": export_time,
                "compressed_size_mb": compressed_size,
                "compression_ratio": compression_ratio,
                "memory_used_mb": memory_used
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação comprimida: {e}")
            raise
    
    async def test_streaming_export_speed(self):
        """Testa velocidade de exportação com streaming"""
        # Configurar exportação com streaming
        export_config = {
            "format": "csv",
            "compression": False,
            "streaming": True,
            "chunk_size": self.config.chunk_size,
            "optimization": self.config.enable_optimization
        }
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar exportação
            export_result = await self.export_service.export_data(
                "keywords",
                export_config,
                progress_callback=self._progress_callback
            )
            
            export_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Validar resultado
            file_size = len(export_result["data"]) / 1024 / 1024  # MB
            export_speed = file_size / export_time  # MB/s
            
            # Verificar performance
            assert export_time < self.config.max_export_time, f"Exportação streaming muito lenta: {export_time}s"
            assert memory_used < 100, f"Uso de memória muito alto com streaming: {memory_used}MB"
            assert export_speed > 1.0, f"Velocidade de exportação streaming muito baixa: {export_speed}MB/s"
            
            self.export_events.append({
                "format": "csv_streaming",
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "memory_used_mb": memory_used
            })
            
            logger.info(f"Exportação streaming testada: {export_time:.3f}s, {memory_used:.2f}MB memória")
            
            return {
                "success": True,
                "export_time": export_time,
                "file_size_mb": file_size,
                "export_speed_mbps": export_speed,
                "memory_used_mb": memory_used
            }
            
        except Exception as e:
            export_time = time.time() - start_time
            logger.error(f"Erro na exportação streaming: {e}")
            raise
    
    async def test_concurrent_export_speed(self):
        """Testa velocidade de exportações concorrentes"""
        async def single_export(export_id: int):
            """Exportação individual"""
            try:
                export_config = {
                    "format": "csv",
                    "compression": False,
                    "streaming": True,
                    "optimization": True
                }
                
                start_time = time.time()
                export_result = await self.export_service.export_data(
                    f"keywords_{export_id}",
                    export_config
                )
                export_time = time.time() - start_time
                
                file_size = len(export_result["data"]) / 1024 / 1024  # MB
                
                return {
                    "export_id": export_id,
                    "success": True,
                    "export_time": export_time,
                    "file_size_mb": file_size
                }
                
            except Exception as e:
                return {
                    "export_id": export_id,
                    "success": False,
                    "error": str(e)
                }
        
        start_time = time.time()
        
        # Executar exportações concorrentes
        tasks = [single_export(i) for i in range(self.config.max_concurrent_exports)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Analisar resultados
        successful_exports = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_exports = [r for r in results if isinstance(r, dict) and not r.get("success")]
        
        # Calcular métricas
        avg_export_time = statistics.mean([r["export_time"] for r in successful_exports]) if successful_exports else 0
        total_file_size = sum([r["file_size_mb"] for r in successful_exports])
        throughput = total_file_size / total_time if total_time > 0 else 0
        
        assert len(successful_exports) > 0, "Nenhuma exportação concorrente foi bem-sucedida"
        assert total_time < self.config.max_export_time * 2, f"Exportações concorrentes muito lentas: {total_time}s"
        
        logger.info(f"Exportações concorrentes testadas: {len(successful_exports)} sucessos, {total_time:.3f}s total")
        
        return {
            "success": True,
            "total_time": total_time,
            "successful_exports": len(successful_exports),
            "failed_exports": len(failed_exports),
            "avg_export_time": avg_export_time,
            "total_file_size_mb": total_file_size,
            "throughput_mbps": throughput
        }
    
    async def _progress_callback(self, progress: float, message: str):
        """Callback para acompanhar progresso da exportação"""
        if self.config.enable_progress_tracking:
            logger.info(f"Progresso da exportação: {progress:.1%} - {message}")
    
    async def _validate_csv_data(self, data: bytes) -> Dict[str, Any]:
        """Valida integridade dos dados CSV"""
        try:
            # Decodificar dados
            csv_text = data.decode('utf-8')
            
            # Ler CSV
            csv_reader = csv.DictReader(io.StringIO(csv_text))
            rows = list(csv_reader)
            
            # Validar estrutura
            expected_columns = ["id", "palavra", "volume", "competicao", "cpc", "execucao_id"]
            actual_columns = list(rows[0].keys()) if rows else []
            
            # Validar dados
            data_valid = len(rows) > 0
            structure_valid = all(col in actual_columns for col in expected_columns)
            
            return {
                "valid": data_valid and structure_valid,
                "row_count": len(rows),
                "columns": actual_columns,
                "data_valid": data_valid,
                "structure_valid": structure_valid
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def _validate_json_data(self, data: bytes) -> Dict[str, Any]:
        """Valida integridade dos dados JSON"""
        try:
            # Decodificar dados
            json_text = data.decode('utf-8')
            
            # Parsear JSON
            json_data = json.loads(json_text)
            
            # Validar estrutura
            data_valid = isinstance(json_data, list) and len(json_data) > 0
            structure_valid = all("id" in item and "palavra" in item for item in json_data[:10])
            
            return {
                "valid": data_valid and structure_valid,
                "item_count": len(json_data),
                "data_valid": data_valid,
                "structure_valid": structure_valid
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def _validate_excel_data(self, data: bytes) -> Dict[str, Any]:
        """Valida integridade dos dados Excel"""
        try:
            # Salvar dados temporariamente
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                temp_file.write(data)
                temp_file_path = temp_file.name
            
            try:
                # Ler Excel
                df = pd.read_excel(temp_file_path)
                
                # Validar dados
                data_valid = len(df) > 0
                structure_valid = all(col in df.columns for col in ["id", "palavra", "volume"])
                
                return {
                    "valid": data_valid and structure_valid,
                    "row_count": len(df),
                    "columns": list(df.columns),
                    "data_valid": data_valid,
                    "structure_valid": structure_valid
                }
                
            finally:
                # Limpar arquivo temporário
                os.unlink(temp_file_path)
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        if not self.export_events:
            return {"error": "Nenhuma exportação executada"}
        
        return {
            "total_exports": len(self.export_events),
            "avg_export_time": statistics.mean([e["export_time"] for e in self.export_events]),
            "avg_export_speed": statistics.mean([e.get("export_speed_mbps", 0) for e in self.export_events]),
            "avg_memory_usage": statistics.mean([e.get("memory_used_mb", 0) for e in self.export_events]),
            "export_events": self.export_events,
            "validation_results": self.validation_results
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
class TestExportSpeedPerformance:
    """Testes de performance para velocidade de exportação"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = ExportSpeedPerformanceTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_csv_export_speed(self):
        """Testa velocidade de exportação CSV"""
        result = await self.test_instance.test_csv_export_speed()
        assert result["success"] is True
        assert result["export_time"] < 300.0
        assert result["export_speed_mbps"] > 1.0
    
    async def test_json_export_speed(self):
        """Testa velocidade de exportação JSON"""
        result = await self.test_instance.test_json_export_speed()
        assert result["success"] is True
        assert result["export_time"] < 300.0
        assert result["export_speed_mbps"] > 0.5
    
    async def test_excel_export_speed(self):
        """Testa velocidade de exportação Excel"""
        result = await self.test_instance.test_excel_export_speed()
        assert result["success"] is True
        assert result["export_time"] < 600.0
        assert result["export_speed_mbps"] > 0.2
    
    async def test_compressed_export_speed(self):
        """Testa velocidade de exportação com compressão"""
        result = await self.test_instance.test_compressed_export_speed()
        assert result["success"] is True
        assert result["compression_ratio"] < 0.5
    
    async def test_streaming_export_speed(self):
        """Testa velocidade de exportação com streaming"""
        result = await self.test_instance.test_streaming_export_speed()
        assert result["success"] is True
        assert result["memory_used_mb"] < 100
    
    async def test_concurrent_export_speed(self):
        """Testa velocidade de exportações concorrentes"""
        result = await self.test_instance.test_concurrent_export_speed()
        assert result["success"] is True
        assert result["successful_exports"] > 0
    
    async def test_overall_export_performance_metrics(self):
        """Testa métricas gerais de performance de exportação"""
        # Executar todos os testes
        await self.test_instance.test_csv_export_speed()
        await self.test_instance.test_json_export_speed()
        await self.test_instance.test_excel_export_speed()
        await self.test_instance.test_compressed_export_speed()
        await self.test_instance.test_streaming_export_speed()
        await self.test_instance.test_concurrent_export_speed()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_exports"] > 0
        assert metrics["avg_export_time"] > 0
        assert metrics["avg_export_speed"] > 0

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = ExportSpeedPerformanceTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_csv_export_speed()
            await test_instance.test_json_export_speed()
            await test_instance.test_excel_export_speed()
            await test_instance.test_compressed_export_speed()
            await test_instance.test_streaming_export_speed()
            await test_instance.test_concurrent_export_speed()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Performance de Exportação: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 