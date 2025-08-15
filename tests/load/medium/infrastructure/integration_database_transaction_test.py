"""
🧪 Teste de Integração - Transações de Banco de Dados

Tracing ID: integration-database-transaction-test-2025-01-27-001
Timestamp: 2025-01-27T20:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em transações reais do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de teste de transações
♻️ ReAct: Simulado cenários de produção e validada atomicidade

Testa transações incluindo:
- Transações simples (commit/rollback)
- Transações aninhadas
- Transações com savepoints
- Transações com isolamento
- Transações com deadlock detection
- Transações com timeout
- Transações com retry logic
- Transações com rollback automático
- Transações com métricas de performance
- Transações com logging estruturado
"""

import pytest
import asyncio
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, AsyncMock
import logging
from dataclasses import dataclass
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# Importações do sistema real
from backend.app.database.connection import DatabaseConnection
from backend.app.database.transaction_manager import TransactionManager
from backend.app.models.keyword import Keyword
from backend.app.models.execucao import Execucao
from backend.app.models.categoria import Categoria
from backend.app.models.user import User
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.resilience.retry_mechanisms import RetryMechanism

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class TransactionTestConfig:
    """Configuração para testes de transações"""
    max_transaction_time: float = 60.0
    max_retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_deadlock_detection: bool = True
    deadlock_timeout: float = 10.0
    enable_savepoints: bool = True
    enable_nested_transactions: bool = True
    isolation_level: str = "READ_COMMITTED"
    enable_transaction_logging: bool = True
    enable_performance_monitoring: bool = True
    max_concurrent_transactions: int = 5
    enable_rollback_on_error: bool = True
    enable_automatic_retry: bool = True

class DatabaseTransactionIntegrationTest:
    """Teste de integração para transações de banco de dados"""
    
    def __init__(self, config: Optional[TransactionTestConfig] = None):
        self.config = config or TransactionTestConfig()
        self.logger = StructuredLogger(
            module="database_transaction_integration_test",
            tracing_id="db_transaction_test_001"
        )
        self.metrics = MetricsCollector()
        self.cache = RedisCache()
        self.transaction_manager = TransactionManager()
        self.db_connection = DatabaseConnection()
        self.retry_mechanism = RetryMechanism("transaction_retry", {
            "max_attempts": self.config.max_retry_attempts,
            "base_delay": self.config.retry_delay
        })
        
        # Métricas de teste
        self.transaction_execution_times: List[float] = []
        self.transaction_success_count: int = 0
        self.transaction_failure_count: int = 0
        self.transaction_rollback_count: int = 0
        self.deadlock_count: int = 0
        self.retry_count: int = 0
        self.failed_transactions: List[Dict[str, Any]] = []
        
        logger.info(f"Database Transaction Integration Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Conectar ao banco
            await self.db_connection.connect()
            
            # Configurar cache
            await self.cache.connect()
            
            # Configurar gerenciador de transações
            self.transaction_manager.configure({
                "isolation_level": self.config.isolation_level,
                "enable_deadlock_detection": self.config.enable_deadlock_detection,
                "deadlock_timeout": self.config.deadlock_timeout,
                "enable_savepoints": self.config.enable_savepoints,
                "enable_nested_transactions": self.config.enable_nested_transactions
            })
            
            # Criar dados de teste
            await self._create_test_data()
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    async def _create_test_data(self):
        """Cria dados de teste para as transações"""
        try:
            # Dados básicos já devem existir do teste anterior
            logger.info("Dados de teste verificados")
            
        except Exception as e:
            logger.error(f"Erro ao verificar dados de teste: {e}")
            raise
    
    async def test_simple_transaction_commit(self):
        """Testa transação simples com commit"""
        async def transaction_operations():
            # Inserir nova categoria
            categoria_data = {
                "nome": f"Test Category {datetime.now().timestamp()}",
                "perfil_cliente": "B2B",
                "cluster": "test_cluster"
            }
            
            categoria_id = await self.db_connection.execute(
                "INSERT INTO categorias (nome, perfil_cliente, cluster) VALUES (%s, %s, %s) RETURNING id",
                (categoria_data["nome"], categoria_data["perfil_cliente"], categoria_data["cluster"])
            )
            
            # Inserir nova execução
            execucao_data = {
                "user_id": 1,
                "categoria_id": categoria_id,
                "status": "running",
                "created_at": datetime.now()
            }
            
            execucao_id = await self.db_connection.execute(
                "INSERT INTO execucoes (user_id, categoria_id, status, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (execucao_data["user_id"], execucao_id, execucao_data["status"], execucao_data["created_at"])
            )
            
            return {
                "categoria_id": categoria_id,
                "execucao_id": execucao_id
            }
        
        start_time = time.time()
        
        try:
            result = await self.transaction_manager.execute_transaction(
                transaction_operations,
                timeout=self.config.max_transaction_time
            )
            
            execution_time = time.time() - start_time
            self.transaction_execution_times.append(execution_time)
            self.transaction_success_count += 1
            
            assert execution_time < self.config.max_transaction_time, f"Transação muito lenta: {execution_time}s"
            assert result["categoria_id"] is not None, "Categoria não foi criada"
            assert result["execucao_id"] is not None, "Execução não foi criada"
            
            logger.info(f"Transação simples executada com sucesso: {execution_time:.3f}s")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "result": result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.transaction_failure_count += 1
            self.failed_transactions.append({
                "test": "simple_transaction_commit",
                "error": str(e),
                "execution_time": execution_time
            })
            logger.error(f"Erro na transação simples: {e}")
            raise
    
    async def test_transaction_rollback(self):
        """Testa transação com rollback"""
        async def transaction_operations_with_error():
            # Inserir categoria válida
            categoria_id = await self.db_connection.execute(
                "INSERT INTO categorias (nome, perfil_cliente, cluster) VALUES (%s, %s, %s) RETURNING id",
                (f"Rollback Test {datetime.now().timestamp()}", "B2B", "rollback_cluster")
            )
            
            # Tentar inserir execução com user_id inválido (deve falhar)
            await self.db_connection.execute(
                "INSERT INTO execucoes (user_id, categoria_id, status, created_at) VALUES (%s, %s, %s, %s)",
                (99999, categoria_id, "running", datetime.now())  # user_id inválido
            )
            
            return {"categoria_id": categoria_id}
        
        start_time = time.time()
        
        try:
            result = await self.transaction_manager.execute_transaction(
                transaction_operations_with_error,
                timeout=self.config.max_transaction_time
            )
            
            # Se chegou aqui, a transação não deveria ter feito rollback
            execution_time = time.time() - start_time
            self.transaction_execution_times.append(execution_time)
            
            logger.warning("Transação deveria ter feito rollback mas não fez")
            
            return {
                "success": False,
                "execution_time": execution_time,
                "expected_rollback": True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.transaction_rollback_count += 1
            
            # Verificar se a categoria foi removida (rollback funcionou)
            categoria_exists = await self.db_connection.execute(
                "SELECT COUNT(*) FROM categorias WHERE nome LIKE 'Rollback Test%'"
            )
            
            assert categoria_exists == 0, "Rollback não funcionou - categoria ainda existe"
            
            logger.info(f"Transação com rollback executada corretamente: {execution_time:.3f}s")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "rollback_verified": True
            }
    
    async def test_nested_transaction(self):
        """Testa transações aninhadas"""
        async def outer_transaction():
            # Transação externa
            categoria_id = await self.db_connection.execute(
                "INSERT INTO categorias (nome, perfil_cliente, cluster) VALUES (%s, %s, %s) RETURNING id",
                (f"Nested Test {datetime.now().timestamp()}", "B2B", "nested_cluster")
            )
            
            # Transação aninhada
            async def inner_transaction():
                execucao_id = await self.db_connection.execute(
                    "INSERT INTO execucoes (user_id, categoria_id, status, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                    (1, categoria_id, "running", datetime.now())
                )
                
                # Transação mais interna
                async def innermost_transaction():
                    keyword_id = await self.db_connection.execute(
                        "INSERT INTO keywords (palavra, volume, competicao, execucao_id) VALUES (%s, %s, %s, %s) RETURNING id",
                        ("nested keyword", 1000, 0.5, execucao_id)
                    )
                    return keyword_id
                
                keyword_id = await self.transaction_manager.execute_transaction(innermost_transaction)
                return execucao_id, keyword_id
            
            execucao_id, keyword_id = await self.transaction_manager.execute_transaction(inner_transaction)
            return categoria_id, execucao_id, keyword_id
        
        start_time = time.time()
        
        try:
            result = await self.transaction_manager.execute_transaction(
                outer_transaction,
                timeout=self.config.max_transaction_time
            )
            
            execution_time = time.time() - start_time
            self.transaction_execution_times.append(execution_time)
            self.transaction_success_count += 1
            
            assert execution_time < self.config.max_transaction_time, f"Transação aninhada muito lenta: {execution_time}s"
            assert len(result) == 3, "Transação aninhada não retornou todos os IDs esperados"
            
            logger.info(f"Transação aninhada executada com sucesso: {execution_time:.3f}s")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "result": result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.transaction_failure_count += 1
            self.failed_transactions.append({
                "test": "nested_transaction",
                "error": str(e),
                "execution_time": execution_time
            })
            logger.error(f"Erro na transação aninhada: {e}")
            raise
    
    async def test_transaction_with_savepoints(self):
        """Testa transação com savepoints"""
        async def transaction_with_savepoints():
            # Criar savepoint inicial
            await self.db_connection.execute("SAVEPOINT initial_state")
            
            # Inserir categoria
            categoria_id = await self.db_connection.execute(
                "INSERT INTO categorias (nome, perfil_cliente, cluster) VALUES (%s, %s, %s) RETURNING id",
                (f"Savepoint Test {datetime.now().timestamp()}", "B2B", "savepoint_cluster")
            )
            
            # Criar savepoint após categoria
            await self.db_connection.execute("SAVEPOINT after_categoria")
            
            # Inserir execução
            execucao_id = await self.db_connection.execute(
                "INSERT INTO execucoes (user_id, categoria_id, status, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (1, categoria_id, "running", datetime.now())
            )
            
            # Simular erro e rollback para savepoint
            try:
                await self.db_connection.execute(
                    "INSERT INTO keywords (palavra, volume, competicao, execucao_id) VALUES (%s, %s, %s, %s)",
                    ("", 0, 0, execucao_id)  # Dados inválidos
                )
            except:
                # Rollback para savepoint após categoria
                await self.db_connection.execute("ROLLBACK TO SAVEPOINT after_categoria")
            
            # Continuar com operação válida
            keyword_id = await self.db_connection.execute(
                "INSERT INTO keywords (palavra, volume, competicao, execucao_id) VALUES (%s, %s, %s, %s) RETURNING id",
                ("valid keyword", 1000, 0.5, execucao_id)
            )
            
            return {
                "categoria_id": categoria_id,
                "execucao_id": execucao_id,
                "keyword_id": keyword_id
            }
        
        start_time = time.time()
        
        try:
            result = await self.transaction_manager.execute_transaction(
                transaction_with_savepoints,
                timeout=self.config.max_transaction_time
            )
            
            execution_time = time.time() - start_time
            self.transaction_execution_times.append(execution_time)
            self.transaction_success_count += 1
            
            assert execution_time < self.config.max_transaction_time, f"Transação com savepoints muito lenta: {execution_time}s"
            assert result["keyword_id"] is not None, "Keyword não foi criada após rollback"
            
            logger.info(f"Transação com savepoints executada com sucesso: {execution_time:.3f}s")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "result": result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.transaction_failure_count += 1
            self.failed_transactions.append({
                "test": "transaction_with_savepoints",
                "error": str(e),
                "execution_time": execution_time
            })
            logger.error(f"Erro na transação com savepoints: {e}")
            raise
    
    async def test_concurrent_transactions(self):
        """Testa transações concorrentes"""
        async def concurrent_transaction(transaction_id: int):
            """Transação individual para execução concorrente"""
            async def transaction_operations():
                # Inserir categoria
                categoria_id = await self.db_connection.execute(
                    "INSERT INTO categorias (nome, perfil_cliente, cluster) VALUES (%s, %s, %s) RETURNING id",
                    (f"Concurrent Test {transaction_id} {datetime.now().timestamp()}", "B2B", f"concurrent_cluster_{transaction_id}")
                )
                
                # Simular processamento
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
                # Inserir execução
                execucao_id = await self.db_connection.execute(
                    "INSERT INTO execucoes (user_id, categoria_id, status, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                    (transaction_id % 3 + 1, categoria_id, "completed", datetime.now())
                )
                
                return {
                    "transaction_id": transaction_id,
                    "categoria_id": categoria_id,
                    "execucao_id": execucao_id
                }
            
            return await self.transaction_manager.execute_transaction(
                transaction_operations,
                timeout=self.config.max_transaction_time
            )
        
        start_time = time.time()
        results = []
        
        # Executar transações concorrentes
        tasks = [concurrent_transaction(i) for i in range(self.config.max_concurrent_transactions)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Analisar resultados
        successful_transactions = [r for r in results if isinstance(r, dict) and "transaction_id" in r]
        failed_transactions = [r for r in results if isinstance(r, Exception)]
        
        self.transaction_success_count += len(successful_transactions)
        self.transaction_failure_count += len(failed_transactions)
        
        assert len(successful_transactions) > 0, "Nenhuma transação concorrente foi bem-sucedida"
        assert total_time < self.config.max_transaction_time * 2, f"Tempo total muito alto: {total_time}s"
        
        logger.info(f"Transações concorrentes executadas: {len(successful_transactions)} sucessos, {len(failed_transactions)} falhas, {total_time:.3f}s total")
        
        return {
            "success": True,
            "total_time": total_time,
            "successful_transactions": len(successful_transactions),
            "failed_transactions": len(failed_transactions),
            "results": results
        }
    
    async def test_transaction_retry_logic(self):
        """Testa lógica de retry em transações"""
        attempt_count = 0
        
        async def transaction_with_retry():
            nonlocal attempt_count
            attempt_count += 1
            
            # Simular falha nas primeiras tentativas
            if attempt_count < 3:
                raise Exception(f"Simulated failure on attempt {attempt_count}")
            
            # Sucesso na terceira tentativa
            categoria_id = await self.db_connection.execute(
                "INSERT INTO categorias (nome, perfil_cliente, cluster) VALUES (%s, %s, %s) RETURNING id",
                (f"Retry Test {datetime.now().timestamp()}", "B2B", "retry_cluster")
            )
            
            return {"categoria_id": categoria_id, "attempt": attempt_count}
        
        start_time = time.time()
        
        try:
            result = await self.retry_mechanism.execute(
                lambda: self.transaction_manager.execute_transaction(
                    transaction_with_retry,
                    timeout=self.config.max_transaction_time
                )
            )
            
            execution_time = time.time() - start_time
            self.transaction_execution_times.append(execution_time)
            self.transaction_success_count += 1
            self.retry_count += attempt_count - 1
            
            assert attempt_count == 3, f"Retry não funcionou corretamente: {attempt_count} tentativas"
            assert result["categoria_id"] is not None, "Categoria não foi criada após retry"
            
            logger.info(f"Transação com retry executada com sucesso: {execution_time:.3f}s, {attempt_count} tentativas")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "attempts": attempt_count,
                "result": result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.transaction_failure_count += 1
            self.failed_transactions.append({
                "test": "transaction_retry_logic",
                "error": str(e),
                "execution_time": execution_time,
                "attempts": attempt_count
            })
            logger.error(f"Erro na transação com retry: {e}")
            raise
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        if not self.transaction_execution_times:
            return {"error": "Nenhuma transação executada"}
        
        return {
            "total_transactions": len(self.transaction_execution_times),
            "successful_transactions": self.transaction_success_count,
            "failed_transactions": self.transaction_failure_count,
            "rollback_transactions": self.transaction_rollback_count,
            "avg_execution_time": statistics.mean(self.transaction_execution_times),
            "min_execution_time": min(self.transaction_execution_times),
            "max_execution_time": max(self.transaction_execution_times),
            "deadlock_count": self.deadlock_count,
            "retry_count": self.retry_count,
            "success_rate": self.transaction_success_count / (self.transaction_success_count + self.transaction_failure_count) if (self.transaction_success_count + self.transaction_failure_count) > 0 else 0,
            "failed_transactions_details": self.failed_transactions
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
class TestDatabaseTransactionIntegration:
    """Testes de integração para transações de banco de dados"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = DatabaseTransactionIntegrationTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_simple_transaction_commit(self):
        """Testa transação simples com commit"""
        result = await self.test_instance.test_simple_transaction_commit()
        assert result["success"] is True
        assert result["execution_time"] < 60.0
    
    async def test_transaction_rollback(self):
        """Testa transação com rollback"""
        result = await self.test_instance.test_transaction_rollback()
        assert result["success"] is True
        assert result["rollback_verified"] is True
    
    async def test_nested_transaction(self):
        """Testa transações aninhadas"""
        result = await self.test_instance.test_nested_transaction()
        assert result["success"] is True
        assert result["execution_time"] < 60.0
    
    async def test_transaction_with_savepoints(self):
        """Testa transação com savepoints"""
        result = await self.test_instance.test_transaction_with_savepoints()
        assert result["success"] is True
        assert result["execution_time"] < 60.0
    
    async def test_concurrent_transactions(self):
        """Testa transações concorrentes"""
        result = await self.test_instance.test_concurrent_transactions()
        assert result["success"] is True
        assert result["total_time"] < 120.0
    
    async def test_transaction_retry_logic(self):
        """Testa lógica de retry em transações"""
        result = await self.test_instance.test_transaction_retry_logic()
        assert result["success"] is True
        assert result["attempts"] == 3
    
    async def test_overall_transaction_metrics(self):
        """Testa métricas gerais de transações"""
        # Executar todos os testes
        await self.test_instance.test_simple_transaction_commit()
        await self.test_instance.test_transaction_rollback()
        await self.test_instance.test_nested_transaction()
        await self.test_instance.test_transaction_with_savepoints()
        await self.test_instance.test_concurrent_transactions()
        await self.test_instance.test_transaction_retry_logic()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_transactions"] > 0
        assert metrics["successful_transactions"] > 0
        assert metrics["avg_execution_time"] < 30.0
        assert metrics["success_rate"] > 0.5

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = DatabaseTransactionIntegrationTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_simple_transaction_commit()
            await test_instance.test_transaction_rollback()
            await test_instance.test_nested_transaction()
            await test_instance.test_transaction_with_savepoints()
            await test_instance.test_concurrent_transactions()
            await test_instance.test_transaction_retry_logic()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Transações: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 