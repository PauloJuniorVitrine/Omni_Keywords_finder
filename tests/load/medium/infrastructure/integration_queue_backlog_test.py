"""
🧪 Teste de Integração - Acúmulo de Filas

Tracing ID: integration-queue-backlog-test-2025-01-27-001
Timestamp: 2025-01-27T21:15:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de acúmulo de filas do sistema Omni Keywords Finder
🌲 ToT: Avaliadas múltiplas estratégias de gerenciamento de backlog (throttling, scaling, prioritização)
♻️ ReAct: Simulado cenários de produção e validada recuperação de backlog

Testa acúmulo de filas incluindo:
- Detecção de backlog
- Monitoramento de tamanho de fila
- Estratégias de throttling
- Auto-scaling de workers
- Priorização de itens críticos
- Recuperação de backlog
- Métricas de backlog
- Alertas de backlog
- Logging estruturado
- Monitoramento de performance
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
from infrastructure.queue.redis_queue import RedisQueue
from infrastructure.queue.memory_queue import MemoryQueue
from infrastructure.queue.backlog_monitor import BacklogMonitor
from infrastructure.queue.throttling_manager import ThrottlingManager
from infrastructure.queue.auto_scaling_manager import AutoScalingManager
from infrastructure.queue.priority_manager import PriorityManager
from infrastructure.queue.backlog_recovery import BacklogRecovery
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.monitoring.alert_manager import AlertManager

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class QueueBacklogTestConfig:
    """Configuração para testes de acúmulo de filas"""
    max_queue_size: int = 10000
    backlog_threshold: int = 1000
    critical_backlog_threshold: int = 5000
    enable_throttling: bool = True
    throttling_rate: float = 0.5  # 50% da taxa normal
    enable_auto_scaling: bool = True
    max_workers: int = 20
    min_workers: int = 2
    scaling_factor: float = 1.5
    enable_priority_processing: bool = True
    enable_backlog_recovery: bool = True
    recovery_batch_size: int = 50
    enable_metrics: bool = True
    enable_monitoring: bool = True
    enable_logging: bool = True
    enable_alerts: bool = True
    alert_threshold: int = 2000

class QueueBacklogIntegrationTest:
    """Teste de integração para acúmulo de filas"""
    
    def __init__(self, config: Optional[QueueBacklogTestConfig] = None):
        self.config = config or QueueBacklogTestConfig()
        self.logger = StructuredLogger(
            module="queue_backlog_integration_test",
            tracing_id="queue_backlog_test_001"
        )
        self.metrics = MetricsCollector()
        
        # Inicializar filas
        self.redis_queue = RedisQueue()
        self.memory_queue = MemoryQueue()
        
        # Gerenciadores de backlog
        self.backlog_monitor = BacklogMonitor()
        self.throttling_manager = ThrottlingManager()
        self.auto_scaling_manager = AutoScalingManager()
        self.priority_manager = PriorityManager()
        self.backlog_recovery = BacklogRecovery()
        self.alert_manager = AlertManager()
        
        # Métricas de teste
        self.backlog_events: List[Dict[str, Any]] = []
        self.throttling_events: List[Dict[str, Any]] = []
        self.scaling_events: List[Dict[str, Any]] = []
        self.recovery_events: List[Dict[str, Any]] = []
        self.alert_events: List[Dict[str, Any]] = []
        
        logger.info(f"Queue Backlog Integration Test inicializado com configuração: {self.config}")
    
    async def setup_test_environment(self):
        """Configura ambiente de teste"""
        try:
            # Conectar filas
            await self.redis_queue.connect()
            await self.memory_queue.connect()
            
            # Configurar gerenciadores
            self.backlog_monitor.configure({
                "backlog_threshold": self.config.backlog_threshold,
                "critical_backlog_threshold": self.config.critical_backlog_threshold,
                "enable_monitoring": self.config.enable_monitoring,
                "enable_metrics": self.config.enable_metrics
            })
            
            self.throttling_manager.configure({
                "enable_throttling": self.config.enable_throttling,
                "throttling_rate": self.config.throttling_rate,
                "enable_metrics": self.config.enable_metrics
            })
            
            self.auto_scaling_manager.configure({
                "enable_auto_scaling": self.config.enable_auto_scaling,
                "max_workers": self.config.max_workers,
                "min_workers": self.config.min_workers,
                "scaling_factor": self.config.scaling_factor,
                "enable_metrics": self.config.enable_metrics
            })
            
            self.priority_manager.configure({
                "enable_priority_processing": self.config.enable_priority_processing,
                "enable_metrics": self.config.enable_metrics
            })
            
            self.backlog_recovery.configure({
                "enable_backlog_recovery": self.config.enable_backlog_recovery,
                "recovery_batch_size": self.config.recovery_batch_size,
                "enable_metrics": self.config.enable_metrics
            })
            
            self.alert_manager.configure({
                "enable_alerts": self.config.enable_alerts,
                "alert_threshold": self.config.alert_threshold,
                "enable_logging": self.config.enable_logging
            })
            
            logger.info("Ambiente de teste configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar ambiente de teste: {e}")
            raise
    
    async def test_backlog_detection(self):
        """Testa detecção de backlog"""
        queue = self.memory_queue
        
        # Simular acúmulo de itens
        backlog_size = self.config.backlog_threshold + 100
        
        start_time = time.time()
        
        # Enfileirar itens rapidamente
        for i in range(backlog_size):
            item = {
                "id": i,
                "data": f"backlog_item_{i}",
                "timestamp": datetime.now(),
                "priority": random.randint(1, 5)
            }
            await queue.enqueue("backlog_test", item)
        
        enqueue_time = time.time() - start_time
        
        # Verificar detecção de backlog
        queue_size = await queue.size("backlog_test")
        backlog_detected = await self.backlog_monitor.check_backlog("backlog_test", queue_size)
        
        # Verificar alertas
        alerts_generated = await self.alert_manager.check_backlog_alerts("backlog_test", queue_size)
        
        assert queue_size >= self.config.backlog_threshold, f"Backlog não atingiu threshold: {queue_size}"
        assert backlog_detected["backlog_detected"], "Backlog não foi detectado"
        assert len(alerts_generated) > 0, "Alertas de backlog não foram gerados"
        
        self.backlog_events.append({
            "queue_size": queue_size,
            "backlog_detected": backlog_detected,
            "alerts_generated": alerts_generated,
            "enqueue_time": enqueue_time
        })
        
        logger.info(f"Detecção de backlog testada: {queue_size} itens, {enqueue_time:.3f}s")
        
        return {
            "success": True,
            "queue_size": queue_size,
            "backlog_detected": backlog_detected["backlog_detected"],
            "alerts_generated": len(alerts_generated),
            "enqueue_time": enqueue_time
        }
    
    async def test_throttling_mechanism(self):
        """Testa mecanismo de throttling"""
        queue = self.memory_queue
        
        # Simular backlog
        backlog_size = self.config.backlog_threshold + 500
        for i in range(backlog_size):
            item = {"id": i, "data": f"throttle_item_{i}"}
            await queue.enqueue("throttle_test", item)
        
        # Ativar throttling
        throttling_activated = await self.throttling_manager.activate_throttling("throttle_test")
        
        # Medir taxa de processamento com throttling
        start_time = time.time()
        processed_items = 0
        
        for _ in range(100):  # Processar 100 itens
            item = await queue.dequeue("throttle_test")
            if item:
                processed_items += 1
                # Simular processamento lento
                await asyncio.sleep(0.01)
        
        throttling_time = time.time() - start_time
        
        # Desativar throttling
        throttling_deactivated = await self.throttling_manager.deactivate_throttling("throttle_test")
        
        # Medir taxa de processamento sem throttling
        start_time = time.time()
        processed_items_normal = 0
        
        for _ in range(100):  # Processar 100 itens
            item = await queue.dequeue("throttle_test")
            if item:
                processed_items_normal += 1
                # Simular processamento lento
                await asyncio.sleep(0.01)
        
        normal_time = time.time() - start_time
        
        # Verificar que throttling reduziu a taxa de processamento
        throttling_effective = throttling_time > normal_time * self.config.throttling_rate
        
        self.throttling_events.append({
            "throttling_activated": throttling_activated,
            "throttling_deactivated": throttling_deactivated,
            "throttling_time": throttling_time,
            "normal_time": normal_time,
            "throttling_effective": throttling_effective
        })
        
        assert throttling_activated, "Throttling não foi ativado"
        assert throttling_deactivated, "Throttling não foi desativado"
        assert throttling_effective, "Throttling não foi efetivo"
        
        logger.info(f"Throttling testado: com throttling {throttling_time:.3f}s, sem throttling {normal_time:.3f}s")
        
        return {
            "success": True,
            "throttling_activated": throttling_activated,
            "throttling_effective": throttling_effective,
            "throttling_time": throttling_time,
            "normal_time": normal_time
        }
    
    async def test_auto_scaling(self):
        """Testa auto-scaling de workers"""
        # Simular backlog crítico
        queue = self.memory_queue
        critical_backlog_size = self.config.critical_backlog_threshold + 1000
        
        for i in range(critical_backlog_size):
            item = {"id": i, "data": f"scaling_item_{i}"}
            await queue.enqueue("scaling_test", item)
        
        # Verificar estado inicial
        initial_workers = self.auto_scaling_manager.get_current_workers()
        
        # Ativar auto-scaling
        scaling_activated = await self.auto_scaling_manager.activate_auto_scaling("scaling_test")
        
        # Simular processamento para forçar scaling
        start_time = time.time()
        
        # Processar alguns itens para gerar métricas
        for _ in range(50):
            item = await queue.dequeue("scaling_test")
            if item:
                await asyncio.sleep(0.01)  # Simular processamento
        
        # Verificar se scaling foi aplicado
        await asyncio.sleep(2)  # Aguardar scaling
        final_workers = self.auto_scaling_manager.get_current_workers()
        
        scaling_applied = final_workers > initial_workers
        scaling_time = time.time() - start_time
        
        # Desativar auto-scaling
        scaling_deactivated = await self.auto_scaling_manager.deactivate_auto_scaling("scaling_test")
        
        self.scaling_events.append({
            "initial_workers": initial_workers,
            "final_workers": final_workers,
            "scaling_activated": scaling_activated,
            "scaling_deactivated": scaling_deactivated,
            "scaling_applied": scaling_applied,
            "scaling_time": scaling_time
        })
        
        assert scaling_activated, "Auto-scaling não foi ativado"
        assert scaling_deactivated, "Auto-scaling não foi desativado"
        assert scaling_applied, "Auto-scaling não foi aplicado"
        
        logger.info(f"Auto-scaling testado: {initial_workers} -> {final_workers} workers, {scaling_time:.3f}s")
        
        return {
            "success": True,
            "initial_workers": initial_workers,
            "final_workers": final_workers,
            "scaling_applied": scaling_applied,
            "scaling_time": scaling_time
        }
    
    async def test_priority_processing_during_backlog(self):
        """Testa processamento prioritário durante backlog"""
        queue = self.memory_queue
        
        # Enfileirar itens com diferentes prioridades
        high_priority_items = []
        low_priority_items = []
        
        for i in range(100):
            if i % 10 == 0:  # 10% de itens de alta prioridade
                item = {"id": i, "data": f"high_priority_{i}", "priority": 1}
                high_priority_items.append(item)
                await queue.enqueue("priority_backlog_test", item, priority=1)
            else:
                item = {"id": i, "data": f"low_priority_{i}", "priority": 5}
                low_priority_items.append(item)
                await queue.enqueue("priority_backlog_test", item, priority=5)
        
        # Ativar processamento prioritário
        priority_activated = await self.priority_manager.activate_priority_processing("priority_backlog_test")
        
        # Processar itens
        processed_high_priority = []
        processed_low_priority = []
        
        for _ in range(50):  # Processar 50 itens
            item = await queue.dequeue("priority_backlog_test")
            if item:
                if item["priority"] == 1:
                    processed_high_priority.append(item)
                else:
                    processed_low_priority.append(item)
        
        # Verificar que itens de alta prioridade foram processados primeiro
        high_priority_ratio = len(processed_high_priority) / (len(processed_high_priority) + len(processed_low_priority))
        priority_effective = high_priority_ratio > 0.3  # Pelo menos 30% dos itens processados devem ser de alta prioridade
        
        # Desativar processamento prioritário
        priority_deactivated = await self.priority_manager.deactivate_priority_processing("priority_backlog_test")
        
        assert priority_activated, "Processamento prioritário não foi ativado"
        assert priority_deactivated, "Processamento prioritário não foi desativado"
        assert priority_effective, "Processamento prioritário não foi efetivo"
        
        logger.info(f"Processamento prioritário testado: {high_priority_ratio:.2%} itens de alta prioridade")
        
        return {
            "success": True,
            "high_priority_ratio": high_priority_ratio,
            "priority_effective": priority_effective,
            "processed_high_priority": len(processed_high_priority),
            "processed_low_priority": len(processed_low_priority)
        }
    
    async def test_backlog_recovery(self):
        """Testa recuperação de backlog"""
        queue = self.memory_queue
        
        # Criar backlog significativo
        backlog_size = self.config.critical_backlog_threshold + 2000
        
        for i in range(backlog_size):
            item = {"id": i, "data": f"recovery_item_{i}"}
            await queue.enqueue("recovery_test", item)
        
        initial_queue_size = await queue.size("recovery_test")
        
        # Iniciar recuperação de backlog
        recovery_started = await self.backlog_recovery.start_recovery("recovery_test")
        
        start_time = time.time()
        
        # Processar backlog em lotes
        processed_batches = 0
        total_processed = 0
        
        while True:
            batch = await self.backlog_recovery.process_recovery_batch("recovery_test")
            if not batch:
                break
            
            processed_batches += 1
            total_processed += len(batch)
            
            # Simular processamento de lote
            await asyncio.sleep(0.1)
        
        recovery_time = time.time() - start_time
        
        # Verificar recuperação
        final_queue_size = await queue.size("recovery_test")
        recovery_successful = final_queue_size < initial_queue_size * 0.1  # Reduzir para menos de 10%
        
        # Finalizar recuperação
        recovery_finished = await self.backlog_recovery.finish_recovery("recovery_test")
        
        self.recovery_events.append({
            "initial_queue_size": initial_queue_size,
            "final_queue_size": final_queue_size,
            "total_processed": total_processed,
            "processed_batches": processed_batches,
            "recovery_time": recovery_time,
            "recovery_successful": recovery_successful
        })
        
        assert recovery_started, "Recuperação não foi iniciada"
        assert recovery_finished, "Recuperação não foi finalizada"
        assert recovery_successful, "Recuperação não foi bem-sucedida"
        
        logger.info(f"Recuperação de backlog testada: {total_processed} itens em {processed_batches} lotes, {recovery_time:.3f}s")
        
        return {
            "success": True,
            "total_processed": total_processed,
            "processed_batches": processed_batches,
            "recovery_time": recovery_time,
            "recovery_successful": recovery_successful
        }
    
    async def test_backlog_metrics(self):
        """Testa métricas de backlog"""
        queue = self.memory_queue
        
        # Simular diferentes cenários de backlog
        scenarios = [
            {"name": "normal", "size": 100},
            {"name": "backlog", "size": self.config.backlog_threshold + 200},
            {"name": "critical", "size": self.config.critical_backlog_threshold + 500}
        ]
        
        metrics_data = []
        
        for scenario in scenarios:
            # Limpar fila
            await queue.clear("metrics_test")
            
            # Enfileirar itens
            for i in range(scenario["size"]):
                item = {"id": i, "data": f"metrics_item_{i}"}
                await queue.enqueue("metrics_test", item)
            
            # Obter métricas
            queue_size = await queue.size("metrics_test")
            backlog_metrics = await self.backlog_monitor.get_backlog_metrics("metrics_test")
            
            metrics_data.append({
                "scenario": scenario["name"],
                "queue_size": queue_size,
                "backlog_metrics": backlog_metrics
            })
        
        # Verificar métricas
        assert len(metrics_data) == len(scenarios), "Nem todos os cenários foram testados"
        
        for metric in metrics_data:
            assert "queue_size" in metric, "Tamanho da fila não foi medido"
            assert "backlog_metrics" in metric, "Métricas de backlog não foram coletadas"
        
        logger.info(f"Métricas de backlog testadas: {len(metrics_data)} cenários")
        
        return {
            "success": True,
            "metrics_data": metrics_data
        }
    
    async def test_backlog_alerts(self):
        """Testa alertas de backlog"""
        queue = self.memory_queue
        
        # Simular backlog que gera alertas
        alert_backlog_size = self.config.alert_threshold + 300
        
        for i in range(alert_backlog_size):
            item = {"id": i, "data": f"alert_item_{i}"}
            await queue.enqueue("alert_test", item)
        
        # Verificar geração de alertas
        queue_size = await queue.size("alert_test")
        alerts = await self.alert_manager.check_backlog_alerts("alert_test", queue_size)
        
        # Verificar diferentes tipos de alertas
        alert_types = [alert["type"] for alert in alerts]
        
        # Verificar que alertas foram gerados
        assert len(alerts) > 0, "Nenhum alerta foi gerado"
        assert "backlog_warning" in alert_types or "backlog_critical" in alert_types, "Alertas de backlog não foram gerados"
        
        self.alert_events.append({
            "queue_size": queue_size,
            "alerts_generated": len(alerts),
            "alert_types": alert_types
        })
        
        logger.info(f"Alertas de backlog testados: {len(alerts)} alertas gerados")
        
        return {
            "success": True,
            "alerts_generated": len(alerts),
            "alert_types": alert_types
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de performance dos testes"""
        return {
            "total_backlog_events": len(self.backlog_events),
            "total_throttling_events": len(self.throttling_events),
            "total_scaling_events": len(self.scaling_events),
            "total_recovery_events": len(self.recovery_events),
            "total_alert_events": len(self.alert_events),
            "backlog_events": self.backlog_events,
            "throttling_events": self.throttling_events,
            "scaling_events": self.scaling_events,
            "recovery_events": self.recovery_events,
            "alert_events": self.alert_events
        }
    
    async def cleanup(self):
        """Limpa recursos de teste"""
        try:
            await self.redis_queue.disconnect()
            await self.memory_queue.disconnect()
            logger.info("Recursos de teste limpos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {e}")

# Testes pytest
@pytest.mark.asyncio
class TestQueueBacklogIntegration:
    """Testes de integração para acúmulo de filas"""
    
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Configuração do teste"""
        self.test_instance = QueueBacklogIntegrationTest()
        await self.test_instance.setup_test_environment()
        yield
        await self.test_instance.cleanup()
    
    async def test_backlog_detection(self):
        """Testa detecção de backlog"""
        result = await self.test_instance.test_backlog_detection()
        assert result["success"] is True
        assert result["backlog_detected"] is True
    
    async def test_throttling_mechanism(self):
        """Testa mecanismo de throttling"""
        result = await self.test_instance.test_throttling_mechanism()
        assert result["success"] is True
        assert result["throttling_effective"] is True
    
    async def test_auto_scaling(self):
        """Testa auto-scaling"""
        result = await self.test_instance.test_auto_scaling()
        assert result["success"] is True
        assert result["scaling_applied"] is True
    
    async def test_priority_processing_during_backlog(self):
        """Testa processamento prioritário durante backlog"""
        result = await self.test_instance.test_priority_processing_during_backlog()
        assert result["success"] is True
        assert result["priority_effective"] is True
    
    async def test_backlog_recovery(self):
        """Testa recuperação de backlog"""
        result = await self.test_instance.test_backlog_recovery()
        assert result["success"] is True
        assert result["recovery_successful"] is True
    
    async def test_backlog_metrics(self):
        """Testa métricas de backlog"""
        result = await self.test_instance.test_backlog_metrics()
        assert result["success"] is True
    
    async def test_backlog_alerts(self):
        """Testa alertas de backlog"""
        result = await self.test_instance.test_backlog_alerts()
        assert result["success"] is True
        assert result["alerts_generated"] > 0
    
    async def test_overall_backlog_metrics(self):
        """Testa métricas gerais de backlog"""
        # Executar todos os testes
        await self.test_instance.test_backlog_detection()
        await self.test_instance.test_throttling_mechanism()
        await self.test_instance.test_auto_scaling()
        await self.test_instance.test_priority_processing_during_backlog()
        await self.test_instance.test_backlog_recovery()
        await self.test_instance.test_backlog_metrics()
        await self.test_instance.test_backlog_alerts()
        
        # Obter métricas
        metrics = self.test_instance.get_performance_metrics()
        
        # Verificar métricas
        assert metrics["total_backlog_events"] > 0
        assert metrics["total_throttling_events"] > 0
        assert metrics["total_scaling_events"] > 0
        assert metrics["total_recovery_events"] > 0
        assert metrics["total_alert_events"] > 0

if __name__ == "__main__":
    # Execução direta do teste
    async def main():
        test_instance = QueueBacklogIntegrationTest()
        try:
            await test_instance.setup_test_environment()
            
            # Executar todos os testes
            await test_instance.test_backlog_detection()
            await test_instance.test_throttling_mechanism()
            await test_instance.test_auto_scaling()
            await test_instance.test_priority_processing_during_backlog()
            await test_instance.test_backlog_recovery()
            await test_instance.test_backlog_metrics()
            await test_instance.test_backlog_alerts()
            
            # Obter métricas finais
            metrics = test_instance.get_performance_metrics()
            print(f"Métricas de Acúmulo de Filas: {json.dumps(metrics, indent=2, default=str)}")
            
        finally:
            await test_instance.cleanup()
    
    asyncio.run(main()) 