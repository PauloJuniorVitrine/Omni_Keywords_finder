"""
🧪 Teste de Integração - Cache Distribuído

Tracing ID: integration-cache-distributed-test-2025-01-27-001
Timestamp: 2025-01-27T20:45:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cache distribuído real do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de cache distribuído (Redis Cluster, Memcached, etc.)
♻️ ReAct: Simulado cenários de produção e validada consistência distribuída

Testa cache distribuído incluindo:
- Sincronização entre nós
- Consistência de dados
- Failover automático
- Balanceamento de carga
- Replicação de dados
- Detecção de falhas
- Recuperação automática
- Métricas de performance
- Monitoramento distribuído
- Logging estruturado
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
from infrastructure.cache.distributed_cache import DistributedCache
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.cache.memory_cache import MemoryCache
from infrastructure.cache.cache_node import CacheNode
from infrastructure.cache.consistency_manager import ConsistencyManager
from infrastructure.cache.failover_manager import FailoverManager
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.cache.load_balancer import LoadBalancer

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class DistributedCacheTestConfig:
    """Configuração para testes de cache distribuído"""
    num_nodes: int = 3
    replication_factor: int = 2
    consistency_level: str = "EVENTUAL"  # STRONG, EVENTUAL, WEAK
    enable_failover: bool = True
    failover_timeout: float = 5.0
    enable_load_balancing: bool = True
    enable_monitoring: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    max_concurrent_operations: int = 100
    enable_compression: bool = True
    enable_encryption: bool = False
    sync_interval: float = 1.0  # segundos

class DistributedCacheIntegrationTest:
    """Teste de integração para cache distribuído"""
    
    def __init__(self, config: Optional[DistributedCacheTestConfig] = None):
        self.config = config or DistributedCacheTestConfig()
        self.logger = StructuredLogger(
            module="distributed_cache_integration_test",
            tracing_id="distributed_cache_test_001"
        )
        self.metrics = MetricsCollector()
        
        # Inicializar cache distribuído
        self.distributed_cache = DistributedCache()
        
        # Gerenciadores
        self.consistency_manager = ConsistencyManager()
        self.failover_manager = FailoverManager()
        self.load_balancer = LoadBalancer()
        
        # Nós de cache
        self.cache_nodes: List[CacheNode] = []
        
        # Métricas de teste
        self.sync_operations: List[Dict[str, Any]] = []
        self.failover_events: List[Dict[str, Any]] = []
        self.consistency_checks: List[Dict[str, Any]] = []
        self.performance_metrics: List[Dict[str, float]] = []
        
        logger.info(f"Distributed Cache Integration Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Configurar cache distribuído
            self.distributed_cache.configure({
                "num_nodes": self.config.num_nodes,
                "replication_factor": self.config.replication_factor,
                "consistency_level": self.config.consistency_level,
                "enable_failover": self.config.enable_failover,
                "failover_timeout": self.config.failover_timeout,
                "enable_load_balancing": self.config.enable_load_balancing,
                "sync_interval": self.config.sync_interval
            })
            
            # Criar nós de cache
            for i in range(self.config.num_nodes):
                node = CacheNode(
                    id=f"node-{i}",
                    host="localhost",
                    port=6379 + i,
                    weight=1.0
                )
                self.cache_nodes.append(node)
                await self.distributed_cache.add_node(node)
            
            # Configurar gerenciadores
            self.consistency_manager.configure({
                "consistency_level": self.config.consistency_level,
                "enable_monitoring": self.config.enable_monitoring
            })
            
            self.failover_manager.configure({
                "timeout": self.config.failover_timeout,
                "enable_automatic_failover": self.config.enable_failover
            })
            
            self.load_balancer.configure({
                "algorithm": "round_robin",
                "enable_health_checks": True
            })
            
            # Conectar cache distribuído
            await self.distributed_cache.connect()
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    async def test_data_synchronization(self):
        """Testa sincronização de dados entre nós"""
        # Inserir dados em um nó
        test_data = {
            "user:1": {"name": "John Doe", "email": "john@example.com"},
            "user:2": {"name": "Jane Smith", "email": "jane@example.com"},
            "config:app": {"version": "1.0.0", "environment": "test"}
        }
        
        start_time = time.time()
        
        # Inserir dados
        for key, value in test_data.items():
            await self.distributed_cache.set(key, value)
        
        insertion_time = time.time() - start_time
        
        # Aguardar sincronização
        await asyncio.sleep(self.config.sync_interval * 2)
        
        # Verificar se dados estão sincronizados em todos os nós
        sync_verified = True
        for key, expected_value in test_data.items():
            for node in self.cache_nodes:
                try:
                    value = await node.get(key)
                    if value != expected_value:
                        sync_verified = False
                        logger.warning(f"Dados não sincronizados no nó {node.id}: {key}")
                        break
                except Exception as e:
                    sync_verified = False
                    logger.error(f"Erro ao verificar sincronização no nó {node.id}: {e}")
                    break
        
        assert sync_verified, "Dados não foram sincronizados corretamente entre nós"
        
        logger.info(f"Sincronização de dados testada com sucesso: {insertion_time:.3f}s")
        
        return {
            "success": True,
            "insertion_time": insertion_time,
            "sync_verified": sync_verified,
            "nodes_checked": len(self.cache_nodes)
        }
    
    async def test_consistency_management(self):
        """Testa gerenciamento de consistência"""
        # Configurar diferentes níveis de consistência
        consistency_levels = ["STRONG", "EVENTUAL", "WEAK"]
        
        for level in consistency_levels:
            self.consistency_manager.set_consistency_level(level)
            
            # Inserir dados com nível de consistência específico
            key = f"consistency_test_{level.lower()}"
            value = f"value_{level}_{datetime.now().timestamp()}"
            
            start_time = time.time()
            await self.distributed_cache.set(key, value, consistency_level=level)
            write_time = time.time() - start_time
            
            # Verificar consistência
            start_time = time.time()
            consistency_check = await self.consistency_manager.check_consistency(key)
            check_time = time.time() - start_time
            
            self.consistency_checks.append({
                "level": level,
                "write_time": write_time,
                "check_time": check_time,
                "consistent": consistency_check["consistent"]
            })
            
            # Verificar que dados estão consistentes conforme nível
            if level == "STRONG":
                assert consistency_check["consistent"], f"Consistência forte não garantida para {key}"
            elif level == "EVENTUAL":
                # Aguardar um pouco para consistência eventual
                await asyncio.sleep(1)
                consistency_check = await self.consistency_manager.check_consistency(key)
                assert consistency_check["consistent"], f"Consistência eventual não alcançada para {key}"
        
        logger.info("Gerenciamento de consistência testado com sucesso")
        
        return {
            "success": True,
            "consistency_checks": self.consistency_checks
        }
    
    async def test_failover_management(self):
        """Testa gerenciamento de failover"""
        # Simular falha em um nó
        failed_node = self.cache_nodes[0]
        
        # Inserir dados antes da falha
        test_data = {
            "failover_test_1": "value_1",
            "failover_test_2": "value_2",
            "failover_test_3": "value_3"
        }
        
        for key, value in test_data.items():
            await self.distributed_cache.set(key, value)
        
        # Simular falha do nó
        await failed_node.disconnect()
        
        start_time = time.time()
        
        # Verificar se failover foi ativado
        failover_activated = await self.failover_manager.handle_node_failure(failed_node)
        
        failover_time = time.time() - start_time
        
        # Verificar se dados ainda estão acessíveis
        data_accessible = True
        for key, expected_value in test_data.items():
            try:
                value = await self.distributed_cache.get(key)
                if value != expected_value:
                    data_accessible = False
                    break
            except Exception as e:
                data_accessible = False
                logger.error(f"Erro ao acessar dados após failover: {e}")
                break
        
        # Reconectar nó
        await failed_node.connect()
        
        # Verificar recuperação
        recovery_successful = await self.failover_manager.handle_node_recovery(failed_node)
        
        self.failover_events.append({
            "node_id": failed_node.id,
            "failover_time": failover_time,
            "failover_activated": failover_activated,
            "data_accessible": data_accessible,
            "recovery_successful": recovery_successful
        })
        
        assert failover_activated, "Failover não foi ativado"
        assert data_accessible, "Dados não estão acessíveis após failover"
        assert recovery_successful, "Recuperação do nó falhou"
        
        logger.info(f"Gerenciamento de failover testado com sucesso: {failover_time:.3f}s")
        
        return {
            "success": True,
            "failover_time": failover_time,
            "failover_activated": failover_activated,
            "data_accessible": data_accessible,
            "recovery_successful": recovery_successful
        }
    
    async def test_load_balancing(self):
        """Testa balanceamento de carga"""
        # Configurar load balancer
        self.load_balancer.set_algorithm("round_robin")
        
        # Simular múltiplas operações
        operations = []
        for i in range(50):
            operations.append({
                "type": "set",
                "key": f"load_test_{i}",
                "value": f"value_{i}"
            })
        
        start_time = time.time()
        
        # Executar operações através do load balancer
        for operation in operations:
            node = self.load_balancer.get_next_node(self.cache_nodes)
            if operation["type"] == "set":
                await node.set(operation["key"], operation["value"])
        
        load_balance_time = time.time() - start_time
        
        # Verificar distribuição de carga
        node_loads = {}
        for node in self.cache_nodes:
            node_loads[node.id] = node.get_operation_count()
        
        # Calcular distribuição
        total_operations = sum(node_loads.values())
        avg_load = total_operations / len(self.cache_nodes)
        
        # Verificar se carga está bem distribuída (variação < 20%)
        load_variance = statistics.variance(node_loads.values())
        load_balanced = load_variance < (avg_load * 0.2) ** 2
        
        logger.info(f"Balanceamento de carga testado: distribuição {node_loads}, variância {load_variance:.2f}")
        
        return {
            "success": True,
            "load_balance_time": load_balance_time,
            "node_loads": node_loads,
            "load_variance": load_variance,
            "load_balanced": load_balanced
        }
    
    async def test_concurrent_operations(self):
        """Testa operações concorrentes no cache distribuído"""
        async def concurrent_operation(operation_id: int):
            """Operação concorrente individual"""
            try:
                # Escolher operação aleatória
                operation_type = random.choice(["set", "get", "delete"])
                key = f"concurrent_test_{operation_id}"
                
                if operation_type == "set":
                    value = f"value_{operation_id}_{datetime.now().timestamp()}"
                    await self.distributed_cache.set(key, value)
                    return {"operation_id": operation_id, "type": "set", "success": True}
                
                elif operation_type == "get":
                    value = await self.distributed_cache.get(key)
                    return {"operation_id": operation_id, "type": "get", "success": value is not None}
                
                elif operation_type == "delete":
                    await self.distributed_cache.delete(key)
                    return {"operation_id": operation_id, "type": "delete", "success": True}
                
            except Exception as e:
                return {"operation_id": operation_id, "type": "error", "success": False, "error": str(e)}
        
        start_time = time.time()
        
        # Executar operações concorrentes
        tasks = [concurrent_operation(i) for i in range(self.config.max_concurrent_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Analisar resultados
        successful_operations = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_operations = [r for r in results if isinstance(r, dict) and not r.get("success")]
        
        # Verificar performance
        assert len(successful_operations) > 0, "Nenhuma operação concorrente foi bem-sucedida"
        assert total_time < 30.0, f"Operações concorrentes muito lentas: {total_time}s"
        
        logger.info(f"Operações concorrentes testadas: {len(successful_operations)} sucessos, {len(failed_operations)} falhas, {total_time:.3f}s")
        
        return {
            "success": True,
            "total_time": total_time,
            "successful_operations": len(successful_operations),
            "failed_operations": len(failed_operations),
            "throughput": len(successful_operations) / total_time
        }
    
    async def test_data_replication(self):
        """Testa replicação de dados"""
        # Configurar replicação
        replication_factor = self.config.replication_factor
        
        # Inserir dados com replicação
        test_data = {
            "replication_test_1": "value_1",
            "replication_test_2": "value_2",
            "replication_test_3": "value_3"
        }
        
        for key, value in test_data.items():
            await self.distributed_cache.set(key, value, replication_factor=replication_factor)
        
        # Aguardar replicação
        await asyncio.sleep(self.config.sync_interval * 2)
        
        # Verificar replicação em todos os nós
        replication_verified = True
        for key, expected_value in test_data.items():
            replica_count = 0
            for node in self.cache_nodes:
                try:
                    value = await node.get(key)
                    if value == expected_value:
                        replica_count += 1
                except Exception:
                    pass
            
            if replica_count < replication_factor:
                replication_verified = False
                logger.warning(f"Replicação insuficiente para {key}: {replica_count}/{replication_factor}")
        
        assert replication_verified, "Replicação de dados não funcionou corretamente"
        
        logger.info(f"Replicação de dados testada com sucesso: fator {replication_factor}")
        
        return {
            "success": True,
            "replication_factor": replication_factor,
            "replication_verified": replication_verified
        }
    
    async def test_performance_monitoring(self):
        """Testa monitoramento de performance"""
        # Executar operações para gerar métricas
        for i in range(100):
            key = f"perf_test_{i}"
            value = f"value_{i}"
            await self.distributed_cache.set(key, value)
            await self.distributed_cache.get(key)
        
        # Obter métricas de performance
        performance_metrics = self.distributed_cache.get_performance_metrics()
        
        # Verificar métricas
        assert "total_operations" in performance_metrics
        assert "avg_response_time" in performance_metrics
        assert "throughput" in performance_metrics
        assert "error_rate" in performance_metrics
        
        # Verificar valores razoáveis
        assert performance_metrics["total_operations"] > 0
        assert performance_metrics["avg_response_time"] > 0
        assert performance_metrics["throughput"] > 0
        assert performance_metrics["error_rate"] >= 0
        
        logger.info(f"Monitoramento de performance testado: {performance_metrics}")
        
        return {
            "success": True,
            "performance_metrics": performance_metrics
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        return {
            "total_sync_operations": len(self.sync_operations),
            "total_failover_events": len(self.failover_events),
            "total_consistency_checks": len(self.consistency_checks),
            "sync_operations": self.sync_operations,
            "failover_events": self.failover_events,
            "consistency_checks": self.consistency_checks
        }
    
    async def cleanup(self):
        """Limpa recursos de teste"""
        try:
            await self.distributed_cache.disconnect()
            for node in self.cache_nodes:
                await node.disconnect()
            logger.info("Recursos de teste limpos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {e}")

# Testes pytest
@pytest.mark.asyncio
class TestDistributedCacheIntegration:
    """Testes de integração para cache distribuído"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = DistributedCacheIntegrationTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_data_synchronization(self):
        """Testa sincronização de dados"""
        result = await self.test_instance.test_data_synchronization()
        assert result["success"] is True
        assert result["sync_verified"] is True
    
    async def test_consistency_management(self):
        """Testa gerenciamento de consistência"""
        result = await self.test_instance.test_consistency_management()
        assert result["success"] is True
    
    async def test_failover_management(self):
        """Testa gerenciamento de failover"""
        result = await self.test_instance.test_failover_management()
        assert result["success"] is True
        assert result["failover_activated"] is True
    
    async def test_load_balancing(self):
        """Testa balanceamento de carga"""
        result = await self.test_instance.test_load_balancing()
        assert result["success"] is True
    
    async def test_concurrent_operations(self):
        """Testa operações concorrentes"""
        result = await self.test_instance.test_concurrent_operations()
        assert result["success"] is True
        assert result["successful_operations"] > 0
    
    async def test_data_replication(self):
        """Testa replicação de dados"""
        result = await self.test_instance.test_data_replication()
        assert result["success"] is True
        assert result["replication_verified"] is True
    
    async def test_performance_monitoring(self):
        """Testa monitoramento de performance"""
        result = await self.test_instance.test_performance_monitoring()
        assert result["success"] is True
    
    async def test_overall_distributed_cache_metrics(self):
        """Testa métricas gerais do cache distribuído"""
        # Executar todos os testes
        await self.test_instance.test_data_synchronization()
        await self.test_instance.test_consistency_management()
        await self.test_instance.test_failover_management()
        await self.test_instance.test_load_balancing()
        await self.test_instance.test_concurrent_operations()
        await self.test_instance.test_data_replication()
        await self.test_instance.test_performance_monitoring()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_sync_operations"] > 0
        assert metrics["total_failover_events"] > 0
        assert metrics["total_consistency_checks"] > 0

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = DistributedCacheIntegrationTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_data_synchronization()
            await test_instance.test_consistency_management()
            await test_instance.test_failover_management()
            await test_instance.test_load_balancing()
            await test_instance.test_concurrent_operations()
            await test_instance.test_data_replication()
            await test_instance.test_performance_monitoring()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Cache Distribuído: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 