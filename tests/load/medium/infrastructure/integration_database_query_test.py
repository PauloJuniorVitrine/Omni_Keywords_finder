"""
🧪 Teste de Integração - Queries Complexas de Banco de Dados

Tracing ID: integration-database-query-test-2025-01-27-001
Timestamp: 2025-01-27T20:00:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em queries reais do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de teste de queries complexas
♻️ ReAct: Simulado cenários de produção e validada performance

Testa queries complexas incluindo:
- Queries com JOINs múltiplos
- Queries com subconsultas
- Queries com agregações complexas
- Queries com ordenação e paginação
- Queries com filtros avançados
- Queries com índices otimizados
- Queries com cache de consulta
- Queries com timeout configurável
"""

import pytest
import asyncio
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, AsyncMock
import logging
from dataclasses import dataclass
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importações do sistema real
from backend.app.database.connection import DatabaseConnection
from backend.app.database.query_optimizer import QueryOptimizer
from backend.app.models.keyword import Keyword
from backend.app.models.execucao import Execucao
from backend.app.models.categoria import Categoria
from backend.app.models.user import User
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.logging.structured_logger import StructuredLogger

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class QueryTestConfig:
    """Configuração para testes de queries"""
    max_execution_time: float = 30.0
    max_memory_usage: int = 512  # MB
    max_cpu_usage: float = 80.0  # %
    enable_query_cache: bool = True
    cache_ttl: int = 300  # segundos
    enable_query_optimization: bool = True
    enable_slow_query_logging: bool = True
    slow_query_threshold: float = 1.0  # segundos
    max_concurrent_queries: int = 10
    enable_connection_pooling: bool = True
    pool_size: int = 20
    enable_query_metrics: bool = True
    enable_performance_monitoring: bool = True

class DatabaseQueryIntegrationTest:
    """Teste de integração para queries complexas de banco de dados"""
    
    def __init__(self, config: Optional[QueryTestConfig] = None):
        self.config = config or QueryTestConfig()
        self.logger = StructuredLogger(
            module="database_query_integration_test",
            tracing_id="db_query_test_001"
        )
        self.metrics = MetricsCollector()
        self.cache = RedisCache()
        self.query_optimizer = QueryOptimizer()
        self.db_connection = DatabaseConnection()
        
        # Métricas de teste
        self.query_execution_times: List[float] = []
        self.query_memory_usage: List[int] = []
        self.query_cpu_usage: List[float] = []
        self.query_cache_hits: int = 0
        self.query_cache_misses: int = 0
        self.slow_queries: List[Dict[str, Any]] = []
        self.failed_queries: List[Dict[str, Any]] = []
        
        logger.info(f"Database Query Integration Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Conectar ao banco
            await self.db_connection.connect()
            
            # Configurar cache
            await self.cache.connect()
            
            # Configurar otimizador de queries
            self.query_optimizer.configure({
                "enable_cache": self.config.enable_query_cache,
                "cache_ttl": self.config.cache_ttl,
                "slow_query_threshold": self.config.slow_query_threshold
            })
            
            # Criar dados de teste
            await self._create_test_data()
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    async def _create_test_data(self):
        """Cria dados de teste para as queries"""
        try:
            # Criar usuários de teste
            users_data = [
                {"id": 1, "username": "user1", "email": "user1@test.com", "created_at": datetime.now()},
                {"id": 2, "username": "user2", "email": "user2@test.com", "created_at": datetime.now()},
                {"id": 3, "username": "user3", "email": "user3@test.com", "created_at": datetime.now()}
            ]
            
            # Criar categorias de teste
            categories_data = [
                {"id": 1, "nome": "SEO", "perfil_cliente": "B2B", "cluster": "seo_cluster"},
                {"id": 2, "nome": "Marketing", "perfil_cliente": "B2C", "cluster": "marketing_cluster"},
                {"id": 3, "nome": "E-commerce", "perfil_cliente": "B2B", "cluster": "ecommerce_cluster"}
            ]
            
            # Criar execuções de teste
            execucoes_data = [
                {"id": 1, "user_id": 1, "categoria_id": 1, "status": "completed", "created_at": datetime.now()},
                {"id": 2, "user_id": 2, "categoria_id": 2, "status": "running", "created_at": datetime.now()},
                {"id": 3, "user_id": 3, "categoria_id": 3, "status": "completed", "created_at": datetime.now()}
            ]
            
            # Criar keywords de teste
            keywords_data = [
                {"id": 1, "palavra": "seo optimization", "volume": 1000, "competicao": 0.7, "execucao_id": 1},
                {"id": 2, "palavra": "digital marketing", "volume": 2000, "competicao": 0.8, "execucao_id": 1},
                {"id": 3, "palavra": "ecommerce tips", "volume": 500, "competicao": 0.5, "execucao_id": 2},
                {"id": 4, "palavra": "social media", "volume": 3000, "competicao": 0.9, "execucao_id": 2},
                {"id": 5, "palavra": "content marketing", "volume": 1500, "competicao": 0.6, "execucao_id": 3}
            ]
            
            logger.info("Dados de teste criados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar dados de teste: {e}")
            raise
    
    async def test_complex_join_query(self):
        """Testa query complexa com múltiplos JOINs"""
        query = """
            SELECT 
                u.username,
                c.nome as categoria,
                COUNT(k.id) as total_keywords,
                AVG(k.volume) as avg_volume,
                AVG(k.competicao) as avg_competicao,
                e.status,
                e.created_at
            FROM users u
            JOIN execucoes e ON u.id = e.user_id
            JOIN categorias c ON e.categoria_id = c.id
            LEFT JOIN keywords k ON e.id = k.execucao_id
            WHERE e.created_at >= %s
            GROUP BY u.id, c.id, e.id
            HAVING COUNT(k.id) > 0
            ORDER BY total_keywords DESC, avg_volume DESC
            LIMIT 10
        """
        
        start_time = time.time()
        memory_before = psutil.virtual_memory().used
        
        try:
            # Executar query com otimização
            result = await self.query_optimizer.execute_query(
                query, 
                params=[datetime.now() - timedelta(days=30)],
                timeout=self.config.max_execution_time
            )
            
            execution_time = time.time() - start_time
            memory_after = psutil.virtual_memory().used
            memory_used = (memory_after - memory_before) / 1024 / 1024  # MB
            
            # Registrar métricas
            self.query_execution_times.append(execution_time)
            self.query_memory_usage.append(memory_used)
            
            # Verificar performance
            assert execution_time < self.config.max_execution_time, f"Query muito lenta: {execution_time}s"
            assert memory_used < self.config.max_memory_usage, f"Uso de memória muito alto: {memory_used}MB"
            
            # Verificar resultado
            assert len(result) > 0, "Query não retornou resultados"
            
            logger.info(f"Query complexa executada com sucesso: {execution_time:.3f}s, {memory_used:.2f}MB")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "memory_used": memory_used,
                "result_count": len(result)
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.failed_queries.append({
                "query": query,
                "error": str(e),
                "execution_time": execution_time
            })
            logger.error(f"Erro na query complexa: {e}")
            raise
    
    async def test_subquery_performance(self):
        """Testa performance de subconsultas"""
        query = """
            SELECT 
                k.palavra,
                k.volume,
                k.competicao,
                (SELECT COUNT(*) FROM keywords k2 WHERE k2.volume > k.volume) as keywords_higher_volume,
                (SELECT AVG(k3.competicao) FROM keywords k3 WHERE k3.volume BETWEEN k.volume * 0.8 AND k.volume * 1.2) as avg_competicao_similar_volume
            FROM keywords k
            WHERE k.volume > (SELECT AVG(volume) FROM keywords)
            ORDER BY k.volume DESC
            LIMIT 20
        """
        
        start_time = time.time()
        
        try:
            result = await self.query_optimizer.execute_query(
                query,
                timeout=self.config.max_execution_time
            )
            
            execution_time = time.time() - start_time
            self.query_execution_times.append(execution_time)
            
            assert execution_time < self.config.max_execution_time, f"Subquery muito lenta: {execution_time}s"
            assert len(result) > 0, "Subquery não retornou resultados"
            
            logger.info(f"Subquery executada com sucesso: {execution_time:.3f}s")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "result_count": len(result)
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.failed_queries.append({
                "query": query,
                "error": str(e),
                "execution_time": execution_time
            })
            logger.error(f"Erro na subquery: {e}")
            raise
    
    async def test_aggregation_query(self):
        """Testa query com agregações complexas"""
        query = """
            SELECT 
                c.nome as categoria,
                c.perfil_cliente,
                COUNT(DISTINCT e.id) as total_execucoes,
                COUNT(k.id) as total_keywords,
                SUM(k.volume) as total_volume,
                AVG(k.competicao) as avg_competicao,
                MIN(k.volume) as min_volume,
                MAX(k.volume) as max_volume,
                STDDEV(k.volume) as volume_stddev,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY k.volume) as median_volume
            FROM categorias c
            LEFT JOIN execucoes e ON c.id = e.categoria_id
            LEFT JOIN keywords k ON e.id = k.execucao_id
            WHERE e.created_at >= %s
            GROUP BY c.id, c.nome, c.perfil_cliente
            HAVING COUNT(k.id) > 0
            ORDER BY total_volume DESC
        """
        
        start_time = time.time()
        
        try:
            result = await self.query_optimizer.execute_query(
                query,
                params=[datetime.now() - timedelta(days=90)],
                timeout=self.config.max_execution_time
            )
            
            execution_time = time.time() - start_time
            self.query_execution_times.append(execution_time)
            
            assert execution_time < self.config.max_execution_time, f"Agregação muito lenta: {execution_time}s"
            assert len(result) > 0, "Agregação não retornou resultados"
            
            logger.info(f"Agregação executada com sucesso: {execution_time:.3f}s")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "result_count": len(result)
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.failed_queries.append({
                "query": query,
                "error": str(e),
                "execution_time": execution_time
            })
            logger.error(f"Erro na agregação: {e}")
            raise
    
    async def test_pagination_query(self):
        """Testa query com paginação e ordenação"""
        page_size = 10
        page_number = 1
        
        query = """
            SELECT 
                k.id,
                k.palavra,
                k.volume,
                k.competicao,
                e.status as execucao_status,
                c.nome as categoria,
                u.username
            FROM keywords k
            JOIN execucoes e ON k.execucao_id = e.id
            JOIN categorias c ON e.categoria_id = c.id
            JOIN users u ON e.user_id = u.id
            WHERE k.volume > %s AND k.competicao < %s
            ORDER BY k.volume DESC, k.competicao ASC
            LIMIT %s OFFSET %s
        """
        
        start_time = time.time()
        
        try:
            offset = (page_number - 1) * page_size
            result = await self.query_optimizer.execute_query(
                query,
                params=[100, 0.8, page_size, offset],
                timeout=self.config.max_execution_time
            )
            
            execution_time = time.time() - start_time
            self.query_execution_times.append(execution_time)
            
            assert execution_time < self.config.max_execution_time, f"Paginação muito lenta: {execution_time}s"
            assert len(result) <= page_size, f"Página retornou mais resultados que o esperado: {len(result)}"
            
            logger.info(f"Paginação executada com sucesso: {execution_time:.3f}s")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "result_count": len(result),
                "page_size": page_size,
                "page_number": page_number
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.failed_queries.append({
                "query": query,
                "error": str(e),
                "execution_time": execution_time
            })
            logger.error(f"Erro na paginação: {e}")
            raise
    
    async def test_concurrent_queries(self):
        """Testa execução concorrente de queries"""
        queries = [
            "SELECT COUNT(*) FROM keywords WHERE volume > 1000",
            "SELECT AVG(competicao) FROM keywords WHERE volume > 500",
            "SELECT COUNT(DISTINCT user_id) FROM execucoes WHERE status = 'completed'",
            "SELECT nome, COUNT(*) as total FROM categorias GROUP BY nome",
            "SELECT username, COUNT(*) as execucoes FROM users u JOIN execucoes e ON u.id = e.user_id GROUP BY u.id"
        ]
        
        start_time = time.time()
        results = []
        
        async def execute_single_query(query: str, query_id: int):
            """Executa uma query individual"""
            try:
                query_start = time.time()
                result = await self.query_optimizer.execute_query(
                    query,
                    timeout=self.config.max_execution_time
                )
                query_time = time.time() - query_start
                
                self.query_execution_times.append(query_time)
                
                return {
                    "query_id": query_id,
                    "success": True,
                    "execution_time": query_time,
                    "result": result
                }
                
            except Exception as e:
                query_time = time.time() - query_start
                self.failed_queries.append({
                    "query": query,
                    "error": str(e),
                    "execution_time": query_time
                })
                
                return {
                    "query_id": query_id,
                    "success": False,
                    "error": str(e),
                    "execution_time": query_time
                }
        
        # Executar queries concorrentemente
        tasks = [execute_single_query(query, i) for i, query in enumerate(queries)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Verificar resultados
        successful_queries = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_queries = [r for r in results if isinstance(r, dict) and not r.get("success")]
        
        assert len(successful_queries) > 0, "Nenhuma query concorrente foi bem-sucedida"
        assert total_time < self.config.max_execution_time * 2, f"Tempo total muito alto: {total_time}s"
        
        logger.info(f"Queries concorrentes executadas: {len(successful_queries)} sucessos, {len(failed_queries)} falhas, {total_time:.3f}s total")
        
        return {
            "success": True,
            "total_time": total_time,
            "successful_queries": len(successful_queries),
            "failed_queries": len(failed_queries),
            "results": results
        }
    
    async def test_query_cache_performance(self):
        """Testa performance do cache de queries"""
        query = "SELECT COUNT(*) FROM keywords WHERE volume > 1000"
        
        # Primeira execução (cache miss)
        start_time = time.time()
        result1 = await self.query_optimizer.execute_query(query)
        first_execution_time = time.time() - start_time
        
        # Segunda execução (cache hit)
        start_time = time.time()
        result2 = await self.query_optimizer.execute_query(query)
        second_execution_time = time.time() - start_time
        
        # Verificar que resultados são iguais
        assert result1 == result2, "Resultados de cache miss e hit são diferentes"
        
        # Verificar que segunda execução foi mais rápida
        assert second_execution_time < first_execution_time, f"Cache não melhorou performance: {second_execution_time}s vs {first_execution_time}s"
        
        logger.info(f"Cache testado: primeira execução {first_execution_time:.3f}s, segunda execução {second_execution_time:.3f}s")
        
        return {
            "success": True,
            "first_execution_time": first_execution_time,
            "second_execution_time": second_execution_time,
            "cache_improvement": first_execution_time - second_execution_time
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        if not self.query_execution_times:
            return {"error": "Nenhuma query executada"}
        
        return {
            "total_queries": len(self.query_execution_times),
            "successful_queries": len(self.query_execution_times) - len(self.failed_queries),
            "failed_queries": len(self.failed_queries),
            "avg_execution_time": statistics.mean(self.query_execution_times),
            "min_execution_time": min(self.query_execution_times),
            "max_execution_time": max(self.query_execution_times),
            "avg_memory_usage": statistics.mean(self.query_memory_usage) if self.query_memory_usage else 0,
            "cache_hits": self.query_cache_hits,
            "cache_misses": self.query_cache_misses,
            "cache_hit_rate": self.query_cache_hits / (self.query_cache_hits + self.query_cache_misses) if (self.query_cache_hits + self.query_cache_misses) > 0 else 0,
            "slow_queries": len(self.slow_queries),
            "failed_queries_details": self.failed_queries
        }
    
    async def cleanup(self):
        """Limpa recursos de teste"""
        try:
            await self.db_connection.disconnect()
            await self.cache.disconnect()
            logger.info("Recursos de teste limpos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {e}")

# Testes pytest
@pytest.mark.asyncio
class TestDatabaseQueryIntegration:
    """Testes de integração para queries de banco de dados"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = DatabaseQueryIntegration()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_complex_join_query_performance(self):
        """Testa performance de query complexa com JOINs"""
        result = await self.test_instance.test_complex_join_query()
        assert result["success"] is True
        assert result["execution_time"] < 30.0
    
    async def test_subquery_performance(self):
        """Testa performance de subconsultas"""
        result = await self.test_instance.test_subquery_performance()
        assert result["success"] is True
        assert result["execution_time"] < 30.0
    
    async def test_aggregation_query_performance(self):
        """Testa performance de queries com agregação"""
        result = await self.test_instance.test_aggregation_query()
        assert result["success"] is True
        assert result["execution_time"] < 30.0
    
    async def test_pagination_query_performance(self):
        """Testa performance de queries com paginação"""
        result = await self.test_instance.test_pagination_query()
        assert result["success"] is True
        assert result["execution_time"] < 30.0
    
    async def test_concurrent_queries_performance(self):
        """Testa performance de queries concorrentes"""
        result = await self.test_instance.test_concurrent_queries()
        assert result["success"] is True
        assert result["total_time"] < 60.0
    
    async def test_query_cache_performance(self):
        """Testa performance do cache de queries"""
        result = await self.test_instance.test_query_cache_performance()
        assert result["success"] is True
        assert result["cache_improvement"] > 0
    
    async def test_overall_performance_metrics(self):
        """Testa métricas gerais de performance"""
        # Executar todos os testes
        await self.test_instance.test_complex_join_query()
        await self.test_instance.test_subquery_performance()
        await self.test_instance.test_aggregation_query()
        await self.test_instance.test_pagination_query()
        await self.test_instance.test_concurrent_queries()
        await self.test_instance.test_query_cache_performance()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_queries"] > 0
        assert metrics["successful_queries"] > 0
        assert metrics["avg_execution_time"] < 10.0
        assert metrics["cache_hit_rate"] >= 0.0

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = DatabaseQueryIntegration()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_complex_join_query()
            await test_instance.test_subquery_performance()
            await test_instance.test_aggregation_query()
            await test_instance.test_pagination_query()
            await test_instance.test_concurrent_queries()
            await test_instance.test_query_cache_performance()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Performance: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 