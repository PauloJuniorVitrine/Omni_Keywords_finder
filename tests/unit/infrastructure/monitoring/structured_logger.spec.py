from typing import Dict, List, Optional, Any
"""
Testes Unitários - Sistema de Logs Estruturados Avançados - IMP-013
Tracing ID: IMP013_LOGS_ESTRUTURADOS_001_20241227
Data: 2024-12-27
Status: Testes Unitários

Testes para validar:
- Formatação JSON estruturada
- Contexto rico
- Filtros de performance e segurança
- Decorators de performance
- Configuração por ambiente
"""

import json
import logging
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Adicionar path para importar o módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from infrastructure.logging.advanced_structured_logger import (
    AdvancedStructuredLogger,
    StructuredJSONFormatter,
    PerformanceFilter,
    SecurityFilter,
    LogContext,
    performance_logger,
    set_logging_context,
    clear_logging_context,
    get_logger,
    configure_logging_for_environment
)

class TestLogContext(unittest.TestCase):
    """Testes para a classe LogContext"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.context = LogContext()
    
    def test_log_context_initialization(self):
        """Testa inicialização do contexto de log"""
        self.assertIsNotNone(self.context.timestamp)
        self.assertEqual(self.context.service_name, "omni_keywords_finder")
        self.assertEqual(self.context.environment, "development")
        self.assertEqual(self.context.version, "1.0.0")
        self.assertIsInstance(self.context.custom_fields, dict)
    
    def test_log_context_with_custom_fields(self):
        """Testa contexto com campos customizados"""
        custom_fields = {"user_action": "login", "ip_address": "192.168.1.1"}
        context = LogContext(custom_fields=custom_fields)
        
        self.assertEqual(context.custom_fields["user_action"], "login")
        self.assertEqual(context.custom_fields["ip_address"], "192.168.1.1")

class TestStructuredJSONFormatter(unittest.TestCase):
    """Testes para o StructuredJSONFormatter"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.formatter = StructuredJSONFormatter()
        self.record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
    
    def test_format_basic_log(self):
        """Testa formatação básica de log"""
        formatted = self.formatter.format(self.record)
        log_data = json.loads(formatted)
        
        self.assertIn("timestamp", log_data)
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["module"], "test")
        self.assertEqual(log_data["line_number"], 10)
    
    def test_format_with_context(self):
        """Testa formatação com contexto"""
        with patch('infrastructure.logging.advanced_structured_logger.tracing_id_var') as mock_tracing:
            mock_tracing.get.return_value = "test-tracing-id"
            
            formatted = self.formatter.format(self.record)
            log_data = json.loads(formatted)
            
            self.assertEqual(log_data["tracing_id"], "test-tracing-id")
            self.assertEqual(log_data["service_name"], "omni_keywords_finder")
    
    def test_format_with_exception(self):
        """Testa formatação com exceção"""
        try:
            raise ValueError("Test exception")
        except ValueError:
            self.record.exc_info = sys.exc_info()
        
        formatted = self.formatter.format(self.record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data["error_code"], "EXCEPTION")
        self.assertIn("error_details", log_data)
        self.assertIn("stack_trace", log_data)
    
    def test_format_with_custom_fields(self):
        """Testa formatação com campos customizados"""
        self.record.custom_fields = {"user_id": "123", "action": "login"}
        
        formatted = self.formatter.format(self.record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data["user_id"], "123")
        self.assertEqual(log_data["action"], "login")

class TestPerformanceFilter(unittest.TestCase):
    """Testes para o PerformanceFilter"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.filter = PerformanceFilter(min_execution_time_ms=100.0)
        self.record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
    
    def test_filter_with_execution_time_above_threshold(self):
        """Testa filtro com tempo de execução acima do threshold"""
        self.record.execution_time_ms = 150.0
        
        result = self.filter.filter(self.record)
        self.assertTrue(result)
    
    def test_filter_with_execution_time_below_threshold(self):
        """Testa filtro com tempo de execução abaixo do threshold"""
        self.record.execution_time_ms = 50.0
        
        result = self.filter.filter(self.record)
        self.assertFalse(result)
    
    def test_filter_without_execution_time(self):
        """Testa filtro sem tempo de execução"""
        result = self.filter.filter(self.record)
        self.assertTrue(result)

class TestSecurityFilter(unittest.TestCase):
    """Testes para o SecurityFilter"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.filter = SecurityFilter(include_sensitive=False)
        self.record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
    
    def test_filter_sensitive_keywords(self):
        """Testa filtro de palavras sensíveis"""
        sensitive_messages = [
            "User password is invalid",
            "Token expired",
            "Secret key not found",
            "Auth failed",
            "API key missing"
        ]
        
        for message in sensitive_messages:
            self.record.msg = message
            result = self.filter.filter(self.record)
            self.assertFalse(result, f"Message should be filtered: {message}")
    
    def test_filter_normal_messages(self):
        """Testa filtro de mensagens normais"""
        normal_messages = [
            "User logged in successfully",
            "Data processed",
            "System started",
            "Configuration loaded"
        ]
        
        for message in normal_messages:
            self.record.msg = message
            result = self.filter.filter(self.record)
            self.assertTrue(result, f"Message should not be filtered: {message}")
    
    def test_filter_with_sensitive_included(self):
        """Testa filtro com sensíveis incluídos"""
        filter_with_sensitive = SecurityFilter(include_sensitive=True)
        self.record.msg = "User password is invalid"
        
        result = filter_with_sensitive.filter(self.record)
        self.assertTrue(result)

class TestAdvancedStructuredLogger(unittest.TestCase):
    """Testes para o AdvancedStructuredLogger"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.close()
        
        self.logger = AdvancedStructuredLogger(
            name="test_logger",
            log_level="INFO",
            log_file=self.temp_file.name,
            include_context=True,
            include_metadata=True
        )
    
    def tearDown(self):
        """Cleanup após cada teste"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_logger_initialization(self):
        """Testa inicialização do logger"""
        self.assertEqual(self.logger.name, "test_logger")
        self.assertIsNotNone(self.logger.logger)
        self.assertIsNotNone(self.logger.formatter)
    
    def test_info_log(self):
        """Testa log de informação"""
        self.logger.info("Test info message", {"user_id": "123"})
        
        with open(self.temp_file.name, 'r') as f:
            log_line = f.readline().strip()
        
        log_data = json.loads(log_line)
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test info message")
        self.assertEqual(log_data["user_id"], "123")
    
    def test_error_log_with_exception(self):
        """Testa log de erro com exceção"""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            self.logger.error("Test error", {"error_type": "ValueError"}, e)
        
        with open(self.temp_file.name, 'r') as f:
            log_line = f.readline().strip()
        
        log_data = json.loads(log_line)
        self.assertEqual(log_data["level"], "ERROR")
        self.assertEqual(log_data["error_code"], "EXCEPTION")
        self.assertIn("stack_trace", log_data)
    
    def test_performance_log(self):
        """Testa log de performance"""
        self.logger.performance("Test performance", 150.5, {"function": "test_func"})
        
        with open(self.temp_file.name, 'r') as f:
            log_line = f.readline().strip()
        
        log_data = json.loads(log_line)
        self.assertEqual(log_data["execution_time_ms"], 150.5)
        self.assertEqual(log_data["log_type"], "performance")
        self.assertEqual(log_data["function"], "test_func")
    
    def test_security_log(self):
        """Testa log de segurança"""
        self.logger.security("Test security event", "login_attempt", {"ip": "192.168.1.1"})
        
        with open(self.temp_file.name, 'r') as f:
            log_line = f.readline().strip()
        
        log_data = json.loads(log_line)
        self.assertEqual(log_data["event_type"], "login_attempt")
        self.assertEqual(log_data["log_type"], "security")
        self.assertEqual(log_data["ip"], "192.168.1.1")
    
    def test_business_log(self):
        """Testa log de negócio"""
        self.logger.business("Test business event", "user_registration", {"plan": "premium"})
        
        with open(self.temp_file.name, 'r') as f:
            log_line = f.readline().strip()
        
        log_data = json.loads(log_line)
        self.assertEqual(log_data["event_type"], "user_registration")
        self.assertEqual(log_data["log_type"], "business")
        self.assertEqual(log_data["plan"], "premium")

class TestPerformanceLoggerDecorator(unittest.TestCase):
    """Testes para o decorator performance_logger"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_performance_decorator_success(self):
        """Testa decorator de performance com sucesso"""
        @performance_logger
        def test_function():
            time.sleep(0.1)
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
    
    def test_performance_decorator_exception(self):
        """Testa decorator de performance com exceção"""
        @performance_logger
        def test_function():
            time.sleep(0.1)
            raise ValueError("Test exception")
        
        with self.assertRaises(ValueError):
            test_function()

class TestLoggingContext(unittest.TestCase):
    """Testes para contexto de logging"""
    
    def setUp(self):
        """Setup para cada teste"""
        clear_logging_context()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        clear_logging_context()
    
    def test_set_logging_context(self):
        """Testa definição de contexto de logging"""
        set_logging_context(
            tracing_id="test-tracing",
            user_id="test-user",
            request_id="test-request",
            session_id="test-session"
        )
    
    def test_clear_logging_context(self):
        """Testa limpeza de contexto de logging"""
        set_logging_context(tracing_id="test-tracing")
        clear_logging_context()

class TestLoggerConfiguration(unittest.TestCase):
    """Testes para configuração do logger"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_configure_logging_for_environment(self):
        """Testa configuração baseada em ambiente"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["LOG_LEVEL"] = "WARNING"
        os.environ["LOG_FILE"] = "/tmp/test.log"
        
        logger = configure_logging_for_environment()
        
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "omni_keywords_finder")
    
    def test_get_logger_singleton(self):
        """Testa singleton do logger global"""
        logger1 = get_logger()
        logger2 = get_logger()
        
        self.assertIs(logger1, logger2)

class TestLoggerIntegration(unittest.TestCase):
    """Testes de integração do sistema de logs"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Cleanup após cada teste"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_complete_logging_workflow(self):
        """Testa workflow completo de logging"""
        logger = AdvancedStructuredLogger(
            name="integration_test",
            log_file=self.temp_file.name
        )
        
        # Definir contexto
        set_logging_context(
            tracing_id="integration-tracing-id",
            user_id="integration-user"
        )
        
        # Logs de diferentes tipos
        logger.info("Integration test started")
        logger.business("User action", "test_action", {"action_type": "test"})
        logger.security("Security event", "test_security", {"event_id": "123"})
        logger.performance("Performance test", 200.0, {"test_name": "integration"})
        
        # Verificar se os logs foram escritos
        with open(self.temp_file.name, 'r') as f:
            log_lines = f.readlines()
        
        self.assertEqual(len(log_lines), 4)
        
        # Verificar formato JSON
        for line in log_lines:
            log_data = json.loads(line.strip())
            self.assertIn("timestamp", log_data)
            self.assertIn("level", log_data)
            self.assertIn("message", log_data)

if __name__ == '__main__':
    # Executar testes
    unittest.main(verbosity=2) 