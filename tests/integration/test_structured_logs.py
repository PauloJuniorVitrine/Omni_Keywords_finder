"""
🧪 Testes de Logs Estruturados

Tracing ID: structured-logs-tests-2025-01-27-001
Timestamp: 2025-01-27T19:30:00Z
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

📐 CoCoT: Testes baseados em cenários reais de logging
🌲 ToT: Avaliadas múltiplas estratégias de teste
♻️ ReAct: Simulado cenários de produção e validada funcionalidade

Testa sistema de logs estruturados incluindo:
- Testes de diferentes formatos (JSON, TEXT, GELF)
- Testes de diferentes destinos (console, file, syslog)
- Testes de contexto de log
- Testes de métricas de log
- Testes de performance
- Testes de integração
- Testes de decorators
- Testes de context managers
"""

import pytest
import json
import tempfile
import os
import time
import uuid
import logging
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
import threading
import queue

from infrastructure.logging.structured_logs import (
    StructuredLogger, LogLevel, LogFormat, LogDestination, LogContext, LogEntry,
    LogManager, get_logger, set_log_context, log_request, log_error, log_performance,
    log_circuit_breaker, log_cache, log_auth, log_audit, get_log_metrics,
    close_loggers, log_function, LogContextManager, JSONFormatter, GELFFormatter, TextFormatter
)

class TestLogLevel:
    """Testes de níveis de log"""
    
    def test_log_level_values(self):
        """Testa valores dos níveis de log"""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"
    
    def test_log_level_comparison(self):
        """Testa comparação de níveis de log"""
        assert LogLevel.DEBUG.value < LogLevel.INFO.value
        assert LogLevel.INFO.value < LogLevel.WARNING.value
        assert LogLevel.WARNING.value < LogLevel.ERROR.value
        assert LogLevel.ERROR.value < LogLevel.CRITICAL.value

class TestLogFormat:
    """Testes de formatos de log"""
    
    def test_log_format_values(self):
        """Testa valores dos formatos de log"""
        assert LogFormat.JSON.value == "json"
        assert LogFormat.TEXT.value == "text"
        assert LogFormat.GELF.value == "gelf"
        assert LogFormat.CUSTOM.value == "custom"

class TestLogDestination:
    """Testes de destinos de log"""
    
    def test_log_destination_values(self):
        """Testa valores dos destinos de log"""
        assert LogDestination.CONSOLE.value == "console"
        assert LogDestination.FILE.value == "file"
        assert LogDestination.SYSLOG.value == "syslog"
        assert LogDestination.HTTP.value == "http"
        assert LogDestination.KAFKA.value == "kafka"
        assert LogDestination.ELASTICSEARCH.value == "elasticsearch"

class TestLogContext:
    """Testes de contexto de log"""
    
    def test_log_context_creation(self):
        """Testa criação de contexto de log"""
        context = LogContext(
            request_id="req123",
            user_id="user456",
            endpoint="/api/test",
            method="GET"
        )
        
        assert context.request_id == "req123"
        assert context.user_id == "user456"
        assert context.endpoint == "/api/test"
        assert context.method == "GET"
        assert context.service_name == "omni-keywords-finder"
        assert context.service_version == "1.0.0"
        assert context.environment == "development"
    
    def test_log_context_defaults(self):
        """Testa valores padrão do contexto"""
        context = LogContext()
        
        assert context.request_id is None
        assert context.user_id is None
        assert context.service_name == "omni-keywords-finder"
        assert context.service_version == "1.0.0"
        assert context.environment == "development"
        assert context.hostname is not None
        assert isinstance(context.additional_data, dict)
    
    def test_log_context_asdict(self):
        """Testa conversão para dicionário"""
        context = LogContext(
            request_id="req123",
            user_id="user456",
            additional_data={"key": "value"}
        )
        
        context_dict = context.__dict__
        
        assert context_dict["request_id"] == "req123"
        assert context_dict["user_id"] == "user456"
        assert context_dict["additional_data"]["key"] == "value"

class TestLogEntry:
    """Testes de entrada de log"""
    
    def test_log_entry_creation(self):
        """Testa criação de entrada de log"""
        context = LogContext(request_id="req123")
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=LogLevel.INFO,
            message="Test message",
            context=context,
            logger_name="test_logger",
            module="test_module",
            function="test_function",
            line_number=42,
            thread_id=123,
            process_id=456
        )
        
        assert entry.level == LogLevel.INFO
        assert entry.message == "Test message"
        assert entry.context.request_id == "req123"
        assert entry.logger_name == "test_logger"
        assert entry.module == "test_module"
        assert entry.function == "test_function"
        assert entry.line_number == 42
        assert entry.thread_id == 123
        assert entry.process_id == 456
    
    def test_log_entry_to_dict(self):
        """Testa conversão para dicionário"""
        context = LogContext(request_id="req123")
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            level=LogLevel.INFO,
            message="Test message",
            context=context,
            logger_name="test_logger",
            module="test_module",
            function="test_function",
            line_number=42,
            thread_id=123,
            process_id=456
        )
        
        entry_dict = entry.to_dict()
        
        assert entry_dict["level"] == "INFO"
        assert entry_dict["message"] == "Test message"
        assert entry_dict["logger_name"] == "test_logger"
        assert entry_dict["module"] == "test_module"
        assert entry_dict["function"] == "test_function"
        assert entry_dict["line_number"] == 42
        assert entry_dict["thread_id"] == 123
        assert entry_dict["process_id"] == 456
        assert entry_dict["context"]["request_id"] == "req123"
    
    def test_log_entry_to_json(self):
        """Testa conversão para JSON"""
        context = LogContext(request_id="req123")
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            level=LogLevel.INFO,
            message="Test message",
            context=context,
            logger_name="test_logger",
            module="test_module",
            function="test_function",
            line_number=42,
            thread_id=123,
            process_id=456
        )
        
        json_str = entry.to_json()
        entry_dict = json.loads(json_str)
        
        assert entry_dict["level"] == "INFO"
        assert entry_dict["message"] == "Test message"
        assert entry_dict["logger_name"] == "test_logger"
    
    def test_log_entry_to_text(self):
        """Testa conversão para texto"""
        context = LogContext(request_id="req123")
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            level=LogLevel.INFO,
            message="Test message",
            context=context,
            logger_name="test_logger",
            module="test_module",
            function="test_function",
            line_number=42,
            thread_id=123,
            process_id=456
        )
        
        text = entry.to_text()
        
        assert "INFO" in text
        assert "Test message" in text
        assert "test_logger" in text
        assert "[req_id=req123]" in text
    
    def test_log_entry_to_gelf(self):
        """Testa conversão para GELF"""
        context = LogContext(
            request_id="req123",
            user_id="user456",
            hostname="test-host"
        )
        entry = LogEntry(
            timestamp=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            level=LogLevel.INFO,
            message="Test message",
            context=context,
            logger_name="test_logger",
            module="test_module",
            function="test_function",
            line_number=42,
            thread_id=123,
            process_id=456
        )
        
        gelf_str = entry.to_gelf()
        gelf_dict = json.loads(gelf_str)
        
        assert gelf_dict["version"] == "1.1"
        assert gelf_dict["host"] == "test-host"
        assert gelf_dict["short_message"] == "Test message"
        assert gelf_dict["level"] == 6  # INFO level
        assert gelf_dict["_logger_name"] == "test_logger"
        assert gelf_dict["_request_id"] == "req123"
        assert gelf_dict["_user_id"] == "user456"
    
    def test_log_entry_gelf_levels(self):
        """Testa níveis GELF"""
        context = LogContext()
        
        # Testar diferentes níveis
        levels = [
            (LogLevel.DEBUG, 7),
            (LogLevel.INFO, 6),
            (LogLevel.WARNING, 4),
            (LogLevel.ERROR, 3),
            (LogLevel.CRITICAL, 2)
        ]
        
        for level, expected_gelf_level in levels:
            entry = LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=level,
                message="Test message",
                context=context,
                logger_name="test_logger",
                module="test_module",
                function="test_function",
                line_number=42,
                thread_id=123,
                process_id=456
            )
            
            gelf_str = entry.to_gelf()
            gelf_dict = json.loads(gelf_str)
            
            assert gelf_dict["level"] == expected_gelf_level

class TestStructuredLogger:
    """Testes do logger estruturado"""
    
    def test_logger_creation(self):
        """Testa criação do logger"""
        logger = StructuredLogger(
            name="test_logger",
            level=LogLevel.DEBUG,
            format=LogFormat.JSON,
            destinations=[LogDestination.CONSOLE]
        )
        
        assert logger.name == "test_logger"
        assert logger.level == LogLevel.DEBUG
        assert logger.format == LogFormat.JSON
        assert LogDestination.CONSOLE in logger.destinations
    
    def test_logger_default_config(self):
        """Testa configuração padrão do logger"""
        logger = StructuredLogger("test_logger")
        
        assert logger.name == "test_logger"
        assert logger.level == LogLevel.INFO
        assert logger.format == LogFormat.JSON
        assert LogDestination.CONSOLE in logger.destinations
    
    def test_logger_context_management(self):
        """Testa gerenciamento de contexto"""
        logger = StructuredLogger("test_logger")
        
        # Definir contexto
        context = LogContext(request_id="req123", user_id="user456")
        logger.set_context(context)
        
        # Verificar contexto
        retrieved_context = logger.get_context()
        assert retrieved_context.request_id == "req123"
        assert retrieved_context.user_id == "user456"
    
    @patch('infrastructure.logging.structured_logs.logging.StreamHandler')
    def test_logger_console_destination(self, mock_handler):
        """Testa destino console"""
        mock_handler_instance = Mock()
        mock_handler.return_value = mock_handler_instance
        
        logger = StructuredLogger(
            "test_logger",
            destinations=[LogDestination.CONSOLE]
        )
        
        # Verificar se handler foi criado
        mock_handler.assert_called_once()
        mock_handler_instance.setFormatter.assert_called_once()
    
    def test_logger_file_destination(self):
        """Testa destino arquivo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            logger = StructuredLogger(
                "test_logger",
                destinations=[LogDestination.FILE],
                config={"log_file": log_file}
            )
            
            # Verificar se arquivo foi criado
            assert os.path.exists(log_file)
    
    def test_logger_basic_logging(self):
        """Testa logging básico"""
        logger = StructuredLogger("test_logger")
        
        # Testar diferentes níveis
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 5
        assert metrics["logs_by_level"]["DEBUG"] == 1
        assert metrics["logs_by_level"]["INFO"] == 1
        assert metrics["logs_by_level"]["WARNING"] == 1
        assert metrics["logs_by_level"]["ERROR"] == 1
        assert metrics["logs_by_level"]["CRITICAL"] == 1
    
    def test_logger_request_logging(self):
        """Testa logging de requisições"""
        logger = StructuredLogger("test_logger")
        
        # Log de requisição bem-sucedida
        logger.log_request("GET", "/api/users", 200, 0.123, 1024, 2048)
        
        # Log de requisição com erro
        logger.log_request("POST", "/api/users", 500, 0.456, 512, 128)
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 2
        assert metrics["errors"] == 1  # Status 500 é considerado erro
    
    def test_logger_error_logging(self):
        """Testa logging de erros"""
        logger = StructuredLogger("test_logger")
        
        # Criar exceção
        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.log_error(e, "TEST_ERROR")
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 1
        assert metrics["errors"] == 1
    
    def test_logger_performance_logging(self):
        """Testa logging de performance"""
        logger = StructuredLogger("test_logger")
        
        # Log de performance
        logger.log_performance("database_query", 0.123)
        logger.log_performance("api_call", 2.456)  # Deve ser warning
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 2
    
    def test_logger_circuit_breaker_logging(self):
        """Testa logging de circuit breaker"""
        logger = StructuredLogger("test_logger")
        
        # Log de circuit breaker
        logger.log_circuit_breaker("api_call", "closed")
        logger.log_circuit_breaker("api_call", "open")
        logger.log_circuit_breaker("api_call", "half_open")
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 3
    
    def test_logger_cache_logging(self):
        """Testa logging de cache"""
        logger = StructuredLogger("test_logger")
        
        # Log de cache
        logger.log_cache("get", "user:123", True)   # Hit
        logger.log_cache("get", "user:456", False)  # Miss
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 2
    
    def test_logger_auth_logging(self):
        """Testa logging de autenticação"""
        logger = StructuredLogger("test_logger")
        
        # Log de autenticação
        logger.log_auth("user123", "login", True)
        logger.log_auth("user456", "login", False)
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 2
        assert metrics["errors"] == 1  # Login falhou
    
    def test_logger_audit_logging(self):
        """Testa logging de auditoria"""
        logger = StructuredLogger("test_logger")
        
        # Log de auditoria
        logger.log_audit("user123", "create", "user")
        logger.log_audit("user456", "delete", "post")
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 2
    
    def test_logger_metrics(self):
        """Testa métricas do logger"""
        logger = StructuredLogger("test_logger")
        
        # Gerar alguns logs
        logger.info("Test message 1")
        logger.error("Test error 1")
        logger.info("Test message 2")
        logger.error("Test error 2")
        
        # Obter métricas
        metrics = logger.get_metrics()
        
        assert metrics["logger_name"] == "test_logger"
        assert metrics["total_logs"] == 4
        assert metrics["logs_by_level"]["INFO"] == 2
        assert metrics["logs_by_level"]["ERROR"] == 2
        assert metrics["errors"] == 2
        assert metrics["error_rate"] == 0.5
        assert metrics["last_log_time"] is not None
    
    def test_logger_close(self):
        """Testa fechamento do logger"""
        logger = StructuredLogger("test_logger")
        
        # Fazer alguns logs
        logger.info("Test message")
        
        # Fechar logger
        logger.close()
        
        # Verificar se worker foi parado
        assert logger._async_worker is None

class TestFormatters:
    """Testes dos formatadores"""
    
    def test_json_formatter(self):
        """Testa formatador JSON"""
        formatter = JSONFormatter()
        
        # Criar record mock
        record = Mock()
        record.created = time.time()
        record.levelname = "INFO"
        record.getMessage.return_value = "Test message"
        record.name = "test_logger"
        record.module = "test_module"
        record.funcName = "test_function"
        record.lineno = 42
        record.thread = 123
        record.process = 456
        record.context = LogContext(request_id="req123")
        record.extra_fields = {"key": "value"}
        
        # Formatar
        formatted = formatter.format(record)
        formatted_dict = json.loads(formatted)
        
        assert formatted_dict["level"] == "INFO"
        assert formatted_dict["message"] == "Test message"
        assert formatted_dict["logger_name"] == "test_logger"
        assert formatted_dict["module"] == "test_module"
        assert formatted_dict["function"] == "test_function"
        assert formatted_dict["line_number"] == 42
        assert formatted_dict["thread_id"] == 123
        assert formatted_dict["process_id"] == 456
        assert formatted_dict["context"]["request_id"] == "req123"
        assert formatted_dict["key"] == "value"
    
    def test_gelf_formatter(self):
        """Testa formatador GELF"""
        formatter = GELFFormatter()
        
        # Criar record mock
        record = Mock()
        record.created = time.time()
        record.levelno = logging.INFO
        record.getMessage.return_value = "Test message"
        record.name = "test_logger"
        record.module = "test_module"
        record.funcName = "test_function"
        record.lineno = 42
        record.thread = 123
        record.process = 456
        record.context = LogContext(
            request_id="req123",
            user_id="user456",
            hostname="test-host"
        )
        
        # Formatar
        formatted = formatter.format(record)
        formatted_dict = json.loads(formatted)
        
        assert formatted_dict["version"] == "1.1"
        assert formatted_dict["host"] == "test-host"
        assert formatted_dict["short_message"] == "Test message"
        assert formatted_dict["level"] == 6  # INFO level
        assert formatted_dict["_logger_name"] == "test_logger"
        assert formatted_dict["_request_id"] == "req123"
        assert formatted_dict["_user_id"] == "user456"
    
    def test_text_formatter(self):
        """Testa formatador de texto"""
        formatter = TextFormatter()
        
        # Criar record mock
        record = Mock()
        record.created = time.time()
        record.levelname = "INFO"
        record.getMessage.return_value = "Test message"
        record.name = "test_logger"
        record.context = LogContext(request_id="req123")
        
        # Formatar
        formatted = formatter.format(record)
        
        assert "INFO" in formatted
        assert "Test message" in formatted
        assert "test_logger" in formatted
        assert "[req_id=req123]" in formatted

class TestLogManager:
    """Testes do gerenciador de loggers"""
    
    def test_log_manager_creation(self):
        """Testa criação do gerenciador"""
        manager = LogManager()
        
        assert len(manager.loggers) == 0
        assert manager.default_config["level"] == LogLevel.INFO
        assert manager.default_config["format"] == LogFormat.JSON
    
    def test_log_manager_get_logger(self):
        """Testa obtenção de logger"""
        manager = LogManager()
        
        # Obter logger pela primeira vez
        logger1 = manager.get_logger("test_logger")
        assert "test_logger" in manager.loggers
        assert logger1.name == "test_logger"
        
        # Obter o mesmo logger novamente
        logger2 = manager.get_logger("test_logger")
        assert logger1 is logger2
    
    def test_log_manager_custom_config(self):
        """Testa configuração customizada"""
        manager = LogManager()
        
        config = {
            "level": LogLevel.DEBUG,
            "format": LogFormat.TEXT,
            "destinations": [LogDestination.CONSOLE]
        }
        
        logger = manager.get_logger("test_logger", config)
        
        assert logger.level == LogLevel.DEBUG
        assert logger.format == LogFormat.TEXT
        assert LogDestination.CONSOLE in logger.destinations
    
    def test_log_manager_set_default_config(self):
        """Testa configuração padrão"""
        manager = LogManager()
        
        new_config = {
            "level": LogLevel.WARNING,
            "format": LogFormat.GELF
        }
        
        manager.set_default_config(new_config)
        
        assert manager.default_config["level"] == LogLevel.WARNING
        assert manager.default_config["format"] == LogFormat.GELF
    
    def test_log_manager_get_all_metrics(self):
        """Testa obtenção de todas as métricas"""
        manager = LogManager()
        
        # Criar alguns loggers
        logger1 = manager.get_logger("logger1")
        logger2 = manager.get_logger("logger2")
        
        # Fazer alguns logs
        logger1.info("Test message 1")
        logger2.error("Test error 1")
        
        # Obter métricas
        all_metrics = manager.get_all_metrics()
        
        assert "logger1" in all_metrics
        assert "logger2" in all_metrics
        assert all_metrics["logger1"]["total_logs"] == 1
        assert all_metrics["logger2"]["total_logs"] == 1
        assert all_metrics["logger2"]["errors"] == 1
    
    def test_log_manager_close_all(self):
        """Testa fechamento de todos os loggers"""
        manager = LogManager()
        
        # Criar alguns loggers
        logger1 = manager.get_logger("logger1")
        logger2 = manager.get_logger("logger2")
        
        # Fazer alguns logs
        logger1.info("Test message")
        logger2.info("Test message")
        
        # Fechar todos
        manager.close_all()
        
        assert len(manager.loggers) == 0

class TestHelperFunctions:
    """Testes das funções helper"""
    
    def test_get_logger(self):
        """Testa função get_logger"""
        logger = get_logger("test_logger")
        
        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test_logger"
    
    def test_set_log_context(self):
        """Testa função set_log_context"""
        # Criar logger primeiro
        logger = get_logger("test_logger")
        
        # Definir contexto
        context = LogContext(request_id="req123", user_id="user456")
        set_log_context(context)
        
        # Verificar se contexto foi aplicado
        retrieved_context = logger.get_context()
        assert retrieved_context.request_id == "req123"
        assert retrieved_context.user_id == "user456"
    
    def test_log_request(self):
        """Testa função log_request"""
        log_request("GET", "/api/users", 200, 0.123)
        
        # Verificar se log foi criado
        metrics = get_log_metrics()
        assert any("http" in logger_name for logger_name in metrics.keys())
    
    def test_log_error(self):
        """Testa função log_error"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            log_error(e, "TEST_ERROR")
        
        # Verificar se log foi criado
        metrics = get_log_metrics()
        assert any("error" in logger_name for logger_name in metrics.keys())
    
    def test_log_performance(self):
        """Testa função log_performance"""
        log_performance("database_query", 0.123)
        
        # Verificar se log foi criado
        metrics = get_log_metrics()
        assert any("performance" in logger_name for logger_name in metrics.keys())
    
    def test_log_circuit_breaker(self):
        """Testa função log_circuit_breaker"""
        log_circuit_breaker("api_call", "open")
        
        # Verificar se log foi criado
        metrics = get_log_metrics()
        assert any("circuit_breaker" in logger_name for logger_name in metrics.keys())
    
    def test_log_cache(self):
        """Testa função log_cache"""
        log_cache("get", "user:123", True)
        
        # Verificar se log foi criado
        metrics = get_log_metrics()
        assert any("cache" in logger_name for logger_name in metrics.keys())
    
    def test_log_auth(self):
        """Testa função log_auth"""
        log_auth("user123", "login", True)
        
        # Verificar se log foi criado
        metrics = get_log_metrics()
        assert any("auth" in logger_name for logger_name in metrics.keys())
    
    def test_log_audit(self):
        """Testa função log_audit"""
        log_audit("user123", "create", "user")
        
        # Verificar se log foi criado
        metrics = get_log_metrics()
        assert any("audit" in logger_name for logger_name in metrics.keys())
    
    def test_get_log_metrics(self):
        """Testa função get_log_metrics"""
        # Criar alguns logs
        log_request("GET", "/api/users", 200, 0.123)
        log_error(ValueError("Test error"))
        
        # Obter métricas
        metrics = get_log_metrics()
        
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
    
    def test_close_loggers(self):
        """Testa função close_loggers"""
        # Criar alguns loggers
        get_logger("test_logger1")
        get_logger("test_logger2")
        
        # Fechar todos
        close_loggers()
        
        # Verificar se foram fechados
        metrics = get_log_metrics()
        assert len(metrics) == 0

class TestDecorators:
    """Testes de decorators"""
    
    def test_log_function_decorator(self):
        """Testa decorator log_function"""
        @log_function("test_function", LogLevel.INFO)
        def test_function():
            return "success"
        
        # Executar função
        result = test_function()
        
        assert result == "success"
        
        # Verificar se logs foram criados
        metrics = get_log_metrics()
        assert any("test_function" in logger_name for logger_name in metrics.keys())
    
    def test_log_function_decorator_with_error(self):
        """Testa decorator log_function com erro"""
        @log_function("test_function_error", LogLevel.INFO)
        def test_function_error():
            raise ValueError("Test error")
        
        # Executar função e capturar erro
        with pytest.raises(ValueError):
            test_function_error()
        
        # Verificar se logs foram criados
        metrics = get_log_metrics()
        assert any("test_function_error" in logger_name for logger_name in metrics.keys())

class TestContextManagers:
    """Testes de context managers"""
    
    def test_log_context_manager_success(self):
        """Testa LogContextManager com sucesso"""
        with LogContextManager("test_operation", "test_operation") as cm:
            time.sleep(0.001)  # Simular operação
        
        # Verificar se logs foram criados
        metrics = get_log_metrics()
        assert any("test_operation" in logger_name for logger_name in metrics.keys())
    
    def test_log_context_manager_error(self):
        """Testa LogContextManager com erro"""
        with pytest.raises(ValueError):
            with LogContextManager("test_operation_error", "test_operation_error"):
                raise ValueError("Test error")
        
        # Verificar se logs foram criados
        metrics = get_log_metrics()
        assert any("test_operation_error" in logger_name for logger_name in metrics.keys())

class TestPerformance:
    """Testes de performance"""
    
    def test_logger_performance(self):
        """Testa performance do logger"""
        logger = StructuredLogger("performance_test")
        
        start_time = time.time()
        
        # Fazer muitos logs
        for i in range(1000):
            logger.info(f"Test message {i}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 1000
        
        # Performance deve ser boa (menos de 1 segundo para 1000 logs)
        assert duration < 1.0
    
    def test_concurrent_logging(self):
        """Testa logging concorrente"""
        logger = StructuredLogger("concurrent_test")
        
        def log_worker(worker_id):
            for i in range(100):
                logger.info(f"Worker {worker_id} message {i}")
        
        # Executar múltiplos workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar todos terminarem
        for thread in threads:
            thread.join()
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 500  # 5 workers * 100 logs cada

class TestIntegration:
    """Testes de integração"""
    
    def test_full_logging_workflow(self):
        """Testa workflow completo de logging"""
        # Configurar contexto
        context = LogContext(
            request_id=str(uuid.uuid4()),
            user_id="user123",
            endpoint="/api/test",
            method="POST"
        )
        set_log_context(context)
        
        # Fazer diferentes tipos de logs
        log_request("POST", "/api/test", 200, 0.123, 1024, 2048)
        log_performance("database_query", 0.456)
        log_cache("get", "user:123", True)
        log_auth("user123", "login", True)
        log_audit("user123", "create", "post")
        
        # Simular erro
        try:
            raise ValueError("Integration test error")
        except ValueError as e:
            log_error(e, "INTEGRATION_ERROR")
        
        # Obter métricas
        metrics = get_log_metrics()
        
        # Verificar se todos os tipos de log foram criados
        logger_names = list(metrics.keys())
        assert any("http" in name for name in logger_names)
        assert any("performance" in name for name in logger_names)
        assert any("cache" in name for name in logger_names)
        assert any("auth" in name for name in logger_names)
        assert any("audit" in name for name in logger_names)
        assert any("error" in name for name in logger_names)
    
    def test_log_rotation(self):
        """Testa rotação de logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "rotation_test.log")
            
            # Configurar logger com rotação
            logger = StructuredLogger(
                "rotation_test",
                destinations=[LogDestination.FILE],
                config={
                    "log_file": log_file,
                    "max_file_size": 1024,  # 1KB
                    "backup_count": 3
                }
            )
            
            # Fazer logs até exceder o tamanho
            large_message = "x" * 100  # 100 bytes por mensagem
            for i in range(20):  # 2000 bytes total
                logger.info(large_message)
            
            # Verificar se arquivos de backup foram criados
            log_dir = os.path.dirname(log_file)
            log_files = [f for f in os.listdir(log_dir) if f.startswith("rotation_test.log")]
            assert len(log_files) > 1  # Arquivo original + backups

# Teste de funcionalidade
if __name__ == "__main__":
    # Teste básico
    logger = get_logger("test")
    logger.info("Teste de logs estruturados")
    
    # Teste de contexto
    context = LogContext(request_id="req123", user_id="user456")
    set_log_context(context)
    
    # Teste de diferentes tipos de log
    log_request("GET", "/api/test", 200, 0.123)
    log_performance("test_operation", 0.456)
    
    # Mostrar métricas
    metrics = get_log_metrics()
    print(f"Métricas: {json.dumps(metrics, indent=2)}")
    
    # Fechar loggers
    close_loggers() 