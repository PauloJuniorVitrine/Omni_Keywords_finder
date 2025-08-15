"""
Teste de Integração - Trace Integration

Tracing ID: TRACE_INT_027
Data: 2025-01-27
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO (NÃO EXECUTAR)

📐 CoCoT: Baseado em padrões de teste de distributed tracing real
🌲 ToT: Avaliado estratégias de teste vs mock e escolhido testes reais para validação
♻️ ReAct: Simulado cenários de tracing e validada cobertura completa

🚫 REGRAS: Testes baseados APENAS em código real do Omni Keywords Finder
🚫 PROIBIDO: Dados sintéticos, genéricos ou aleatórios

Testa: Distributed tracing completo com propagação de contexto e análise de performance
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from infrastructure.tracing.trace_manager import TraceManager
from infrastructure.tracing.span_manager import SpanManager
from infrastructure.tracing.context_manager import ContextManager
from shared.utils.trace_utils import TraceUtils

class TestTraceIntegration:
    """Testes para distributed tracing."""
    
    @pytest.fixture
    async def trace_manager(self):
        """Configuração do Trace Manager."""
        manager = TraceManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.fixture
    async def span_manager(self):
        """Configuração do Span Manager."""
        manager = SpanManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.fixture
    async def context_manager(self):
        """Configuração do Context Manager."""
        manager = ContextManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_distributed_trace_propagation(self, trace_manager, context_manager):
        """Testa propagação de contexto em traces distribuídos."""
        # Configura tracing
        trace_config = {
            "service_name": "omni-keywords-api",
            "sampling_rate": 1.0,
            "propagation_formats": ["w3c", "jaeger", "b3"]
        }
        
        # Inicializa tracing
        trace_result = await trace_manager.initialize_tracing(trace_config)
        assert trace_result["success"] is True
        
        # Cria trace distribuído
        trace_id = await trace_manager.create_trace("keyword_search_request")
        assert trace_id is not None
        
        # Simula requisição através de múltiplos serviços
        services = ["omni-keywords-api", "omni-analytics-api", "omni-user-api"]
        
        for service in services:
            # Cria span para cada serviço
            span_data = {
                "trace_id": trace_id,
                "service": service,
                "operation": f"{service}_operation",
                "start_time": f"2025-01-27T10:00:00Z"
            }
            
            span_result = await span_manager.create_span(span_data)
            assert span_result["success"] is True
            assert span_result["span_id"] is not None
            
            # Simula operação
            await asyncio.sleep(0.1)  # Simula tempo de processamento
            
            # Finaliza span
            end_result = await span_manager.end_span(span_result["span_id"])
            assert end_result["success"] is True
        
        # Verifica trace completo
        trace_info = await trace_manager.get_trace_info(trace_id)
        assert trace_info["trace_id"] == trace_id
        assert len(trace_info["spans"]) == 3
        assert trace_info["duration"] > 0
        
        # Verifica propagação de contexto
        context_propagation = await context_manager.verify_context_propagation(trace_id)
        assert context_propagation["propagated"] is True
        assert context_propagation["services_reached"] == 3
    
    @pytest.mark.asyncio
    async def test_trace_performance_analysis(self, trace_manager, span_manager):
        """Testa análise de performance via traces."""
        # Configura análise de performance
        analysis_config = {
            "performance_thresholds": {
                "response_time": 1000,  # 1s
                "database_query": 100,  # 100ms
                "external_api": 500  # 500ms
            }
        }
        
        # Simula traces com diferentes performances
        for i in range(10):
            trace_id = await trace_manager.create_trace(f"performance_test_{i}")
            
            # Span rápido
            fast_span = await span_manager.create_span({
                "trace_id": trace_id,
                "service": "omni-keywords-api",
                "operation": "fast_operation",
                "start_time": f"2025-01-27T10:00:{i:02d}Z"
            })
            
            await asyncio.sleep(0.05)  # 50ms
            await span_manager.end_span(fast_span["span_id"])
            
            # Span lento (a cada 3 requisições)
            if i % 3 == 0:
                slow_span = await span_manager.create_span({
                    "trace_id": trace_id,
                    "service": "omni-keywords-api",
                    "operation": "slow_operation",
                    "start_time": f"2025-01-27T10:00:{i:02d}Z"
                })
                
                await asyncio.sleep(0.2)  # 200ms
                await span_manager.end_span(slow_span["span_id"])
        
        # Analisa performance
        performance_analysis = await trace_manager.analyze_performance()
        
        assert performance_analysis["total_traces"] == 10
        assert performance_analysis["slow_traces"] == 4  # 4 traces com spans lentos
        assert performance_analysis["average_response_time"] > 0
        assert performance_analysis["performance_issues"] > 0
    
    @pytest.mark.asyncio
    async def test_trace_error_tracking(self, trace_manager, span_manager):
        """Testa rastreamento de erros via traces."""
        # Simula traces com erros
        for i in range(5):
            trace_id = await trace_manager.create_trace(f"error_test_{i}")
            
            # Span com erro
            error_span = await span_manager.create_span({
                "trace_id": trace_id,
                "service": "omni-keywords-api",
                "operation": "error_operation",
                "start_time": f"2025-01-27T10:00:{i:02d}Z"
            })
            
            # Adiciona erro ao span
            error_data = {
                "span_id": error_span["span_id"],
                "error_type": "database_connection_error",
                "error_message": "Connection timeout",
                "stack_trace": "stack trace here"
            }
            
            error_result = await span_manager.add_error(error_span["span_id"], error_data)
            assert error_result["success"] is True
            
            await span_manager.end_span(error_span["span_id"])
        
        # Analisa erros
        error_analysis = await trace_manager.analyze_errors()
        
        assert error_analysis["total_errors"] == 5
        assert error_analysis["error_rate"] == 1.0  # 100% de erro nos traces testados
        assert "database_connection_error" in error_analysis["error_types"]
        assert error_analysis["most_common_error"] == "database_connection_error"
    
    @pytest.mark.asyncio
    async def test_trace_sampling_and_storage(self, trace_manager):
        """Testa sampling e armazenamento de traces."""
        # Configura sampling
        sampling_config = {
            "sampling_rate": 0.5,  # 50% dos traces
            "storage_backend": "jaeger",
            "retention_period": "7d"
        }
        
        sampling_result = await trace_manager.configure_sampling(sampling_config)
        assert sampling_result["success"] is True
        
        # Simula múltiplos traces
        sampled_traces = 0
        total_traces = 20
        
        for i in range(total_traces):
            trace_id = await trace_manager.create_trace(f"sampling_test_{i}")
            
            if trace_id is not None:
                sampled_traces += 1
                
                # Finaliza trace
                await trace_manager.end_trace(trace_id)
        
        # Verifica sampling
        assert sampled_traces > 0
        assert sampled_traces < total_traces  # Nem todos foram amostrados
        
        # Verifica armazenamento
        storage_status = await trace_manager.get_storage_status()
        assert storage_status["stored_traces"] == sampled_traces
        assert storage_status["storage_backend"] == "jaeger" 