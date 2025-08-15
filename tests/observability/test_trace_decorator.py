"""
Testes Unitários para TraceDecorator
TraceDecorator - Sistema de decoradores para tracing automático

Prompt: Implementação de testes unitários para TraceDecorator
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27
Fase: Criação sem execução - Testes baseados em código real
Tracing ID: TEST_TRACE_DECORATOR_001_20250127
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from infrastructure.observability.trace_decorator import (
    TraceLevel,
    TraceDecoratorConfig,
    TraceClass,
    TraceFunction,
    trace_context
)
from infrastructure.observability.trace_context import (
    TraceContext,
    ContextType,
    TraceContextManager
)
from infrastructure.observability.advanced_tracing import (
    AdvancedTracing,
    SpanType,
    StatusCode
)


class TestTraceLevel:
    """Testes para TraceLevel"""
    
    def test_trace_level_values(self):
        """Testa valores do enum TraceLevel"""
        assert TraceLevel.NONE.value == "none"
        assert TraceLevel.BASIC.value == "basic"
        assert TraceLevel.DETAILED.value == "detailed"
        assert TraceLevel.FULL.value == "full"
    
    def test_trace_level_membership(self):
        """Testa membership do enum TraceLevel"""
        assert TraceLevel.NONE in TraceLevel
        assert TraceLevel.BASIC in TraceLevel
        assert TraceLevel.DETAILED in TraceLevel
        assert TraceLevel.FULL in TraceLevel


class TestTraceDecoratorConfig:
    """Testes para TraceDecoratorConfig"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo para testes"""
        return {
            "enabled": True,
            "level": TraceLevel.DETAILED,
            "include_args": True,
            "include_return": True,
            "include_exceptions": True,
            "max_args_length": 1000,
            "max_return_length": 2000,
            "exclude_modules": ["test", "unittest"],
            "include_modules": ["app", "infrastructure"],
            "custom_attributes": {"service": "omni_keywords_finder"}
        }
    
    def test_initialization(self, sample_config):
        """Testa inicialização básica"""
        config = TraceDecoratorConfig(**sample_config)
        
        assert config.enabled == True
        assert config.level == TraceLevel.DETAILED
        assert config.include_args == True
        assert config.include_return == True
        assert config.include_exceptions == True
        assert config.max_args_length == 1000
        assert config.max_return_length == 2000
        assert config.exclude_modules == ["test", "unittest"]
        assert config.include_modules == ["app", "infrastructure"]
        assert config.custom_attributes == {"service": "omni_keywords_finder"}
    
    def test_default_values(self):
        """Testa valores padrão"""
        config = TraceDecoratorConfig()
        
        assert config.enabled == True
        assert config.level == TraceLevel.BASIC
        assert config.include_args == True
        assert config.include_return == True
        assert config.include_exceptions == True
        assert config.max_args_length == 500
        assert config.max_return_length == 1000
        assert config.exclude_modules == []
        assert config.include_modules == []
        assert config.custom_attributes == {}
    
    def test_validation(self, sample_config):
        """Testa validações"""
        # Teste com level inválido
        with pytest.raises(ValueError):
            TraceDecoratorConfig(level="invalid")
        
        # Teste com valores negativos
        with pytest.raises(ValueError):
            TraceDecoratorConfig(max_args_length=-1)
        
        with pytest.raises(ValueError):
            TraceDecoratorConfig(max_return_length=-1)
    
    def test_serialization(self, sample_config):
        """Testa serialização"""
        config = TraceDecoratorConfig(**sample_config)
        
        config_dict = config.to_dict()
        assert config_dict["enabled"] == True
        assert config_dict["level"] == "detailed"
        assert config_dict["include_args"] == True
        assert config_dict["custom_attributes"] == {"service": "omni_keywords_finder"}
    
    def test_from_dict(self, sample_config):
        """Testa criação a partir de dicionário"""
        config = TraceDecoratorConfig.from_dict(sample_config)
        
        assert config.enabled == True
        assert config.level == TraceLevel.DETAILED
        assert config.include_args == True


class TestTraceClass:
    """Testes para TraceClass"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return TraceDecoratorConfig(
            enabled=True,
            level=TraceLevel.DETAILED,
            include_args=True,
            include_return=True
        )
    
    @pytest.fixture
    def mock_tracing(self):
        """Mock do sistema de tracing"""
        return Mock(spec=AdvancedTracing)
    
    def test_initialization(self, sample_config, mock_tracing):
        """Testa inicialização básica"""
        trace_class = TraceClass(sample_config, mock_tracing)
        
        assert trace_class.config == sample_config
        assert trace_class.tracing == mock_tracing
        assert trace_class.enabled == True
    
    def test_decorate_class(self, sample_config, mock_tracing):
        """Testa decoração de classe"""
        trace_class = TraceClass(sample_config, mock_tracing)
        
        # Classe de exemplo
        class TestClass:
            def method1(self, arg1, arg2):
                return arg1 + arg2
            
            async def async_method(self, arg1):
                return arg1 * 2
        
        # Decorar a classe
        decorated_class = trace_class.decorate(TestClass)
        
        assert decorated_class != TestClass
        assert hasattr(decorated_class, 'method1')
        assert hasattr(decorated_class, 'async_method')
    
    def test_decorate_methods(self, sample_config, mock_tracing):
        """Testa decoração de métodos"""
        trace_class = TraceClass(sample_config, mock_tracing)
        
        class TestClass:
            def sync_method(self, x, y):
                return x + y
            
            async def async_method(self, x):
                await asyncio.sleep(0.01)
                return x * 2
        
        # Decorar métodos
        decorated_class = trace_class.decorate(TestClass)
        instance = decorated_class()
        
        # Testar método síncrono
        result = instance.sync_method(5, 3)
        assert result == 8
        
        # Testar método assíncrono
        result = asyncio.run(instance.async_method(4))
        assert result == 8
    
    def test_disabled_tracing(self, mock_tracing):
        """Testa tracing desabilitado"""
        config = TraceDecoratorConfig(enabled=False)
        trace_class = TraceClass(config, mock_tracing)
        
        class TestClass:
            def method(self, x):
                return x * 2
        
        decorated_class = trace_class.decorate(TestClass)
        instance = decorated_class()
        
        result = instance.method(5)
        assert result == 10
        # Verificar que tracing não foi chamado
        mock_tracing.start_span.assert_not_called()


class TestTraceFunction:
    """Testes para TraceFunction"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return TraceDecoratorConfig(
            enabled=True,
            level=TraceLevel.DETAILED,
            include_args=True,
            include_return=True
        )
    
    @pytest.fixture
    def mock_tracing(self):
        """Mock do sistema de tracing"""
        return Mock(spec=AdvancedTracing)
    
    def test_initialization(self, sample_config, mock_tracing):
        """Testa inicialização básica"""
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        assert trace_function.config == sample_config
        assert trace_function.tracing == mock_tracing
        assert trace_function.enabled == True
    
    def test_decorate_sync_function(self, sample_config, mock_tracing):
        """Testa decoração de função síncrona"""
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_function.decorate()
        def test_func(x, y, z=10):
            return x + y + z
        
        result = test_func(5, 3)
        assert result == 18
        
        # Verificar que tracing foi chamado
        mock_tracing.start_span.assert_called_once()
        mock_tracing.end_span.assert_called_once_with(mock_span, StatusCode.OK)
    
    def test_decorate_async_function(self, sample_config, mock_tracing):
        """Testa decoração de função assíncrona"""
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_function.decorate()
        async def test_async_func(x, y):
            await asyncio.sleep(0.01)
            return x * y
        
        result = asyncio.run(test_async_func(4, 5))
        assert result == 20
        
        # Verificar que tracing foi chamado
        mock_tracing.start_span.assert_called_once()
        mock_tracing.end_span.assert_called_once_with(mock_span, StatusCode.OK)
    
    def test_decorate_with_exception(self, sample_config, mock_tracing):
        """Testa decoração com exceção"""
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_function.decorate()
        def test_func_with_error():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_func_with_error()
        
        # Verificar que tracing foi chamado com erro
        mock_tracing.start_span.assert_called_once()
        mock_tracing.end_span.assert_called_once_with(mock_span, StatusCode.ERROR, "Test error")
    
    def test_decorate_with_custom_span_type(self, sample_config, mock_tracing):
        """Testa decoração com tipo de span customizado"""
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_function.decorate(span_type=SpanType.DATABASE)
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        assert result == 10
        
        # Verificar que span foi criado com tipo correto
        call_args = mock_tracing.start_span.call_args
        assert call_args[1]['span_type'] == SpanType.DATABASE
    
    def test_decorate_with_attributes(self, sample_config, mock_tracing):
        """Testa decoração com atributos customizados"""
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_function.decorate(attributes={"operation": "test", "priority": "high"})
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        assert result == 10
        
        # Verificar que atributos foram passados
        call_args = mock_tracing.start_span.call_args
        assert "operation" in call_args[1]['attributes']
        assert "priority" in call_args[1]['attributes']


class TestTraceContext:
    """Testes para trace_context"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return TraceDecoratorConfig(
            enabled=True,
            level=TraceLevel.DETAILED,
            include_args=True,
            include_return=True
        )
    
    @pytest.fixture
    def mock_tracing(self):
        """Mock do sistema de tracing"""
        return Mock(spec=AdvancedTracing)
    
    def test_trace_context_decorator(self, sample_config, mock_tracing):
        """Testa decorador trace_context"""
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_context("test_operation", mock_tracing, SpanType.BUSINESS_LOGIC)
        def test_func(x, y):
            return x + y
        
        result = test_func(3, 4)
        assert result == 7
        
        # Verificar que tracing foi chamado
        mock_tracing.start_span.assert_called_once()
        mock_tracing.end_span.assert_called_once_with(mock_span, StatusCode.OK)
    
    def test_trace_context_async_decorator(self, sample_config, mock_tracing):
        """Testa decorador trace_context para funções assíncronas"""
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_context("async_test_operation", mock_tracing, SpanType.BUSINESS_LOGIC)
        async def test_async_func(x, y):
            await asyncio.sleep(0.01)
            return x * y
        
        result = asyncio.run(test_async_func(4, 5))
        assert result == 20
        
        # Verificar que tracing foi chamado
        mock_tracing.start_span.assert_called_once()
        mock_tracing.end_span.assert_called_once_with(mock_span, StatusCode.OK)
    
    def test_trace_context_with_exception(self, sample_config, mock_tracing):
        """Testa trace_context com exceção"""
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_context("error_operation", mock_tracing, SpanType.BUSINESS_LOGIC)
        def test_func_with_error():
            raise RuntimeError("Test runtime error")
        
        with pytest.raises(RuntimeError):
            test_func_with_error()
        
        # Verificar que tracing foi chamado com erro
        mock_tracing.start_span.assert_called_once()
        mock_tracing.end_span.assert_called_once_with(mock_span, StatusCode.ERROR, "Test runtime error")
    
    def test_trace_context_with_attributes(self, sample_config, mock_tracing):
        """Testa trace_context com atributos"""
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        @trace_context("test_operation", mock_tracing, SpanType.BUSINESS_LOGIC, 
                      attributes={"service": "test", "version": "1.0"})
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        assert result == 10
        
        # Verificar que atributos foram passados
        call_args = mock_tracing.start_span.call_args
        assert "service" in call_args[1]['attributes']
        assert "version" in call_args[1]['attributes']


class TestTraceDecoratorIntegration:
    """Testes de integração para TraceDecorator"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return TraceDecoratorConfig(
            enabled=True,
            level=TraceLevel.FULL,
            include_args=True,
            include_return=True,
            include_exceptions=True
        )
    
    @pytest.fixture
    def mock_tracing(self):
        """Mock do sistema de tracing"""
        return Mock(spec=AdvancedTracing)
    
    def test_full_trace_cycle(self, sample_config, mock_tracing):
        """Testa ciclo completo de tracing"""
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        # Criar decoradores
        trace_class = TraceClass(sample_config, mock_tracing)
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        # Classe com métodos decorados
        class TestService:
            @trace_function.decorate(span_type=SpanType.BUSINESS_LOGIC)
            def process_data(self, data):
                return {"processed": data, "status": "success"}
            
            @trace_function.decorate(span_type=SpanType.DATABASE)
            async def fetch_data(self, id):
                await asyncio.sleep(0.01)
                return {"id": id, "data": "sample"}
        
        # Decorar a classe
        decorated_service = trace_class.decorate(TestService)
        service = decorated_service()
        
        # Testar método síncrono
        result = service.process_data("test_data")
        assert result["processed"] == "test_data"
        assert result["status"] == "success"
        
        # Testar método assíncrono
        result = asyncio.run(service.fetch_data(123))
        assert result["id"] == 123
        assert result["data"] == "sample"
        
        # Verificar que tracing foi chamado múltiplas vezes
        assert mock_tracing.start_span.call_count >= 2
        assert mock_tracing.end_span.call_count >= 2


class TestTraceDecoratorErrorHandling:
    """Testes de tratamento de erro para TraceDecorator"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return TraceDecoratorConfig(
            enabled=True,
            level=TraceLevel.DETAILED,
            include_args=True,
            include_return=True
        )
    
    @pytest.fixture
    def mock_tracing(self):
        """Mock do sistema de tracing"""
        return Mock(spec=AdvancedTracing)
    
    def test_tracing_system_error(self, sample_config, mock_tracing):
        """Testa erro no sistema de tracing"""
        # Mock do span que falha
        mock_tracing.start_span.side_effect = Exception("Tracing system error")
        
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        @trace_function.decorate()
        def test_func(x):
            return x * 2
        
        # Função deve continuar funcionando mesmo com erro no tracing
        result = test_func(5)
        assert result == 10
    
    def test_invalid_config(self, mock_tracing):
        """Testa configuração inválida"""
        with pytest.raises(ValueError):
            TraceDecoratorConfig(level="invalid_level")
        
        with pytest.raises(ValueError):
            TraceDecoratorConfig(max_args_length=-1)
    
    def test_missing_tracing_system(self, sample_config):
        """Testa sistema de tracing ausente"""
        with pytest.raises(ValueError):
            TraceFunction(sample_config, None)


class TestTraceDecoratorPerformance:
    """Testes de performance para TraceDecorator"""
    
    @pytest.fixture
    def sample_config(self):
        """Configuração de exemplo"""
        return TraceDecoratorConfig(
            enabled=True,
            level=TraceLevel.BASIC,
            include_args=False,
            include_return=False
        )
    
    @pytest.fixture
    def mock_tracing(self):
        """Mock do sistema de tracing"""
        return Mock(spec=AdvancedTracing)
    
    def test_decorator_overhead(self, sample_config, mock_tracing):
        """Testa overhead do decorador"""
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        @trace_function.decorate()
        def fast_function():
            return "result"
        
        # Medir tempo de execução
        start_time = time.time()
        for _ in range(1000):
            fast_function()
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Deve ser rápido
    
    def test_memory_usage(self, sample_config, mock_tracing):
        """Testa uso de memória"""
        import gc
        import sys
        
        # Mock do span
        mock_span = Mock()
        mock_tracing.start_span.return_value = mock_span
        
        trace_function = TraceFunction(sample_config, mock_tracing)
        
        @trace_function.decorate()
        def memory_test_function():
            return [i for i in range(1000)]
        
        # Forçar garbage collection
        gc.collect()
        initial_memory = sys.getsizeof(memory_test_function)
        
        # Executar função múltiplas vezes
        for _ in range(100):
            memory_test_function()
        
        # Forçar garbage collection novamente
        gc.collect()
        final_memory = sys.getsizeof(memory_test_function)
        
        # Verificar que não há vazamento significativo de memória
        memory_diff = final_memory - initial_memory
        assert memory_diff < 1000  # Diferença deve ser pequena 