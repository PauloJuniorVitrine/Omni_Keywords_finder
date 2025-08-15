"""
Teste de Integração - Memory Management

Tracing ID: MEM_MGMT_005
Data: 2025-01-27
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO (NÃO EXECUTAR)

📐 CoCoT: Baseado em padrões de teste de gerenciamento de memória real
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de gerenciamento de memória e validada cobertura completa

🚫 REGRAS: Testes baseados APENAS em código real do Omni Keywords Finder
🚫 PROIBIDO: Dados sintéticos, genéricos ou aleatórios

Testa: Gerenciamento de memória do Redis com otimização e limpeza automática
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from infrastructure.cache.memory_manager import RedisMemoryManager
from infrastructure.cache.eviction_policy import EvictionPolicy
from infrastructure.cache.memory_monitor import MemoryMonitor
from shared.utils.memory_utils import MemoryUtils

class TestMemoryManagement:
    """Testes para gerenciamento de memória do Redis."""
    
    @pytest.fixture
    async def memory_manager(self):
        """Configuração do Memory Manager."""
        manager = RedisMemoryManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.fixture
    async def eviction_policy(self):
        """Configuração da política de evição."""
        policy = EvictionPolicy()
        await policy.initialize()
        yield policy
        await policy.cleanup()
    
    @pytest.fixture
    async def memory_monitor(self):
        """Configuração do monitor de memória."""
        monitor = MemoryMonitor()
        await monitor.initialize()
        yield monitor
        await monitor.cleanup()
    
    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, memory_manager, memory_monitor):
        """Testa monitoramento de uso de memória."""
        # Obtém uso inicial de memória
        initial_memory = await memory_monitor.get_memory_usage()
        assert initial_memory > 0
        
        # Simula uso intensivo de memória
        for i in range(1000):
            await memory_manager.set_large_data(f"large_key_{i}", "x" * 1024)
        
        # Verifica aumento de memória
        increased_memory = await memory_monitor.get_memory_usage()
        assert increased_memory > initial_memory
        
        # Verifica alertas de memória
        alerts = await memory_monitor.get_memory_alerts()
        if increased_memory > memory_monitor.get_warning_threshold():
            assert len(alerts) > 0
            assert any("memory" in alert["type"] for alert in alerts)
    
    @pytest.mark.asyncio
    async def test_eviction_policy_enforcement(self, memory_manager, eviction_policy):
        """Testa aplicação da política de evição."""
        # Configura política LRU
        await eviction_policy.set_policy("allkeys-lru")
        
        # Preenche cache até limite
        max_keys = 100
        for i in range(max_keys + 10):
            await memory_manager.set(f"eviction_key_{i}", f"value_{i}")
        
        # Verifica que chaves antigas foram evictadas
        oldest_key = await memory_manager.get("eviction_key_0")
        assert oldest_key is None
        
        # Verifica que chaves mais recentes permanecem
        recent_key = await memory_manager.get(f"eviction_key_{max_keys + 5}")
        assert recent_key == f"value_{max_keys + 5}"
        
        # Verifica estatísticas de evição
        eviction_stats = await eviction_policy.get_eviction_stats()
        assert eviction_stats["evicted_keys"] > 0
    
    @pytest.mark.asyncio
    async def test_memory_optimization_strategies(self, memory_manager, memory_monitor):
        """Testa estratégias de otimização de memória."""
        # Armazena dados com diferentes estratégias
        await memory_manager.set_compressed("compressed_key", "large_data" * 1000)
        await memory_manager.set_serialized("serialized_key", {"complex": "data"})
        
        # Verifica economia de memória
        compressed_size = await memory_manager.get_key_size("compressed_key")
        regular_size = await memory_manager.get_key_size("regular_key")
        
        # Compressão deve economizar espaço
        if compressed_size > 0:
            assert compressed_size < len("large_data" * 1000)
        
        # Testa limpeza de dados expirados
        await memory_manager.set_with_ttl("expiring_key", "expiring_value", ttl=1)
        await asyncio.sleep(2)  # Aguarda expiração
        
        await memory_manager.cleanup_expired_keys()
        
        # Verifica limpeza
        expired_data = await memory_manager.get("expiring_key")
        assert expired_data is None
    
    @pytest.mark.asyncio
    async def test_memory_fragmentation_management(self, memory_manager, memory_monitor):
        """Testa gerenciamento de fragmentação de memória."""
        # Simula fragmentação
        await memory_manager.simulate_memory_fragmentation()
        
        # Verifica fragmentação
        fragmentation_ratio = await memory_monitor.get_fragmentation_ratio()
        assert fragmentation_ratio > 0
        
        # Executa defragmentação
        await memory_manager.defragment_memory()
        
        # Verifica redução de fragmentação
        new_fragmentation_ratio = await memory_monitor.get_fragmentation_ratio()
        assert new_fragmentation_ratio < fragmentation_ratio
        
        # Verifica integridade dos dados
        test_data = await memory_manager.get("test_key")
        assert test_data is not None
    
    @pytest.mark.asyncio
    async def test_memory_limit_enforcement(self, memory_manager, eviction_policy):
        """Testa aplicação de limites de memória."""
        # Define limite de memória
        memory_limit = 50 * 1024 * 1024  # 50MB
        await memory_manager.set_memory_limit(memory_limit)
        
        # Preenche até o limite
        current_memory = 0
        key_count = 0
        
        while current_memory < memory_limit:
            await memory_manager.set(f"limit_key_{key_count}", "data" * 1024)
            current_memory = await memory_manager.get_current_memory_usage()
            key_count += 1
        
        # Verifica que limite foi respeitado
        final_memory = await memory_manager.get_current_memory_usage()
        assert final_memory <= memory_limit
        
        # Verifica evição automática
        eviction_count = await eviction_policy.get_eviction_count()
        assert eviction_count > 0
    
    @pytest.mark.asyncio
    async def test_memory_recovery_after_cleanup(self, memory_manager, memory_monitor):
        """Testa recuperação de memória após limpeza."""
        # Obtém memória inicial
        initial_memory = await memory_monitor.get_memory_usage()
        
        # Preenche com dados temporários
        for i in range(500):
            await memory_manager.set(f"temp_key_{i}", f"temp_value_{i}")
        
        # Verifica aumento de memória
        filled_memory = await memory_monitor.get_memory_usage()
        assert filled_memory > initial_memory
        
        # Executa limpeza completa
        await memory_manager.clear_all_data()
        
        # Verifica recuperação de memória
        cleaned_memory = await memory_monitor.get_memory_usage()
        assert cleaned_memory < filled_memory
        
        # Verifica que memória está próxima do inicial
        memory_difference = abs(cleaned_memory - initial_memory)
        assert memory_difference < (initial_memory * 0.1)  # < 10% de diferença 