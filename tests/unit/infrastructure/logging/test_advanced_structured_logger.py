"""
🔧 Testes Avançados - Sistema de Logs Estruturados Avançados - Omni Keywords Finder

Tracing ID: TEST_ADVANCED_STRUCTURED_LOGGER_001
Data/Hora: 2025-01-27 17:00:00 UTC
Versão: 1.0
Status: 🚀 EM IMPLEMENTAÇÃO

Objetivo: Testes avançados para o sistema de logging estruturado com cobertura de:
- Integração com structlog e ELK Stack
- Concorrência e thread safety
- Falhas e recuperação
- Observabilidade e métricas
- Edge cases e cenários extremos
"""

import pytest
import json
import time
import threading
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
import requests

from infrastructure.logging.advanced_structured_logger import (
    AdvancedStructuredLogger, LogContext, LogMetrics, ELKStackIntegration,
    LogCategory, get_logger, set_correlation_id, set_user_context,
    clear_context, log_function_call, log_info, log_warning, log_error,
    log_critical, log_audit, log_security, log_performance
)


class TestAdvancedStructuredLogger:
    """Testes para AdvancedStructuredLogger."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Diretório temporário para logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Limpeza
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def logger(self, temp_log_dir):
        """Instância de logger para testes."""
        return AdvancedStructuredLogger(
            log_dir=temp_log_dir,
            log_level="DEBUG",
            enable_json=True,
            enable_console=True,
            enable_file=True,
            max_file_size=1024 * 1024,  # 1MB
            backup_count=3,
            enable_elk=False  # Desabilita ELK para testes
        )
    
    def test_initialization_success(self, temp_log_dir):
        """Testa inicialização bem-sucedida."""
        logger = AdvancedStructuredLogger(log_dir=temp_log_dir)
        
        assert logger.log_dir == temp_log_dir
        assert logger.log_level == "INFO"
        assert logger.enable_json is True
        assert logger.enable_console is True
        assert logger.enable_file is True
        assert logger.metrics is not None
        assert logger.elk_integration is not None
    
    def test_structlog_configuration(self, logger):
        """Testa configuração do structlog."""
        # Verifica se structlog foi configurado
        assert structlog.get_config() is not None
        
        # Verifica se logger foi criado
        assert logger.logger is not None
    
    def test_file_handlers_setup(self, logger, temp_log_dir):
        """Testa configuração dos file handlers."""
        # Verifica se arquivos de log foram criados
        log_files = os.listdir(temp_log_dir)
        assert len(log_files) > 0
        
        # Verifica se há arquivos para diferentes níveis
        expected_files = ["app.log", "error.log", "audit.log"]
        for expected_file in expected_files:
            assert any(expected_file in f for f in log_files)
    
    def test_correlation_id_management(self, logger):
        """Testa gerenciamento de correlation ID."""
        correlation_id = "test-correlation-123"
        logger.set_correlation_id(correlation_id)
        
        # Verifica se correlation ID foi definido
        assert logger.correlation_id == correlation_id
        
        # Testa limpeza
        logger.clear_context()
        assert logger.correlation_id is None
    
    def test_user_context_management(self, logger):
        """Testa gerenciamento de contexto de usuário."""
        user_id = "user123"
        request_id = "req456"
        session_id = "sess789"
        
        logger.set_user_context(user_id, request_id, session_id)
        
        assert logger.user_id == user_id
        assert logger.request_id == request_id
        assert logger.session_id == session_id
        
        # Testa limpeza
        logger.clear_context()
        assert logger.user_id is None
        assert logger.request_id is None
        assert logger.session_id is None
    
    def test_log_with_context(self, logger):
        """Testa logging com contexto."""
        correlation_id = "test-correlation-123"
        user_id = "user123"
        
        logger.set_correlation_id(correlation_id)
        logger.set_user_context(user_id)
        
        # Log com contexto
        logger.log_with_context(
            level="INFO",
            message="Test message",
            category=LogCategory.SYSTEM,
            custom_field="test_value"
        )
        
        # Verifica se log foi gerado
        metrics = logger.get_metrics()
        assert metrics["total_logs"] > 0
        assert metrics["logs_by_level"]["INFO"] > 0
    
    def test_log_rotation(self, logger, temp_log_dir):
        """Testa rotação de logs."""
        # Gera logs suficientes para triggerar rotação
        large_message = "x" * 1000  # 1KB por mensagem
        
        for i in range(1000):  # 1000 mensagens de 1KB = 1MB
            logger.log_with_context(
                level="INFO",
                message=f"{large_message}_{i}",
                category=LogCategory.SYSTEM
            )
        
        # Verifica se arquivos de backup foram criados
        log_files = os.listdir(temp_log_dir)
        backup_files = [f for f in log_files if ".1" in f or ".2" in f]
        assert len(backup_files) > 0
    
    def test_log_categories(self, logger):
        """Testa diferentes categorias de log."""
        categories = [
            LogCategory.SYSTEM,
            LogCategory.API,
            LogCategory.DATABASE,
            LogCategory.CACHE,
            LogCategory.SECURITY,
            LogCategory.PERFORMANCE,
            LogCategory.BUSINESS,
            LogCategory.ERROR,
            LogCategory.AUDIT
        ]
        
        for category in categories:
            logger.log_with_context(
                level="INFO",
                message=f"Test {category.value}",
                category=category
            )
        
        # Verifica métricas por categoria
        metrics = logger.get_metrics()
        for category in categories:
            assert metrics["logs_by_category"][category.value] > 0
    
    def test_log_levels(self, logger):
        """Testa diferentes níveis de log."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            logger.log_with_context(
                level=level,
                message=f"Test {level}",
                category=LogCategory.SYSTEM
            )
        
        # Verifica métricas por nível
        metrics = logger.get_metrics()
        for level in levels:
            assert metrics["logs_by_level"][level] > 0
    
    def test_performance_metrics(self, logger):
        """Testa métricas de performance."""
        # Simula operação com tempo de execução
        start_time = time.time()
        time.sleep(0.1)  # Simula processamento
        execution_time = (time.time() - start_time) * 1000  # ms
        
        logger.log_with_context(
            level="INFO",
            message="Performance test",
            category=LogCategory.PERFORMANCE,
            execution_time_ms=execution_time
        )
        
        # Verifica se métricas foram registradas
        metrics = logger.get_metrics()
        assert metrics["avg_response_time"] > 0
    
    def test_error_logging(self, logger):
        """Testa logging de erros."""
        try:
            raise ValueError("Test error")
        except Exception as e:
            logger.log_with_context(
                level="ERROR",
                message="Error occurred",
                category=LogCategory.ERROR,
                error_code="TEST_ERROR",
                error_details=str(e),
                stack_trace=traceback.format_exc()
            )
        
        # Verifica se erro foi registrado
        metrics = logger.get_metrics()
        assert metrics["errors"] > 0
        assert metrics["error_rate"] > 0


class TestELKStackIntegration:
    """Testes para integração com ELK Stack."""
    
    @pytest.fixture
    def elk_integration(self):
        """Instância de ELKStackIntegration para testes."""
        return ELKStackIntegration(
            elasticsearch_url="http://localhost:9200",
            logstash_url="http://localhost:5044"
        )
    
    @patch('infrastructure.logging.advanced_structured_logger.requests.Session')
    def test_send_to_elasticsearch_success(self, mock_session, elk_integration):
        """Testa envio bem-sucedido para Elasticsearch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response
        
        log_data = {"message": "test", "level": "INFO"}
        result = elk_integration.send_to_elasticsearch(log_data)
        
        assert result is True
        mock_session.return_value.post.assert_called_once()
    
    @patch('infrastructure.logging.advanced_structured_logger.requests.Session')
    def test_send_to_elasticsearch_failure(self, mock_session, elk_integration):
        """Testa falha no envio para Elasticsearch."""
        mock_session.return_value.post.side_effect = Exception("Connection error")
        
        log_data = {"message": "test", "level": "INFO"}
        result = elk_integration.send_to_elasticsearch(log_data)
        
        assert result is False
    
    @patch('infrastructure.logging.advanced_structured_logger.requests.Session')
    def test_send_to_logstash_success(self, mock_session, elk_integration):
        """Testa envio bem-sucedido para Logstash."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response
        
        log_data = {"message": "test", "level": "INFO"}
        result = elk_integration.send_to_logstash(log_data)
        
        assert result is True
        mock_session.return_value.post.assert_called_once()
    
    def test_elk_disabled(self):
        """Testa comportamento quando ELK está desabilitado."""
        elk_integration = ELKStackIntegration()
        
        log_data = {"message": "test", "level": "INFO"}
        result_es = elk_integration.send_to_elasticsearch(log_data)
        result_ls = elk_integration.send_to_logstash(log_data)
        
        assert result_es is False
        assert result_ls is False


class TestLogMetrics:
    """Testes para LogMetrics."""
    
    @pytest.fixture
    def metrics(self):
        """Instância de LogMetrics para testes."""
        return LogMetrics()
    
    def test_record_log(self, metrics):
        """Testa registro de métricas de log."""
        metrics.record_log("INFO", "SYSTEM", 100, 0.5)
        
        assert metrics.total_logs == 1
        assert metrics.logs_by_level["INFO"] == 1
        assert metrics.logs_by_category["SYSTEM"] == 1
        assert metrics.avg_log_size == 100
    
    def test_record_error(self, metrics):
        """Testa registro de erro."""
        metrics.record_log("ERROR", "ERROR", 200, 1.0)
        
        assert metrics.errors == 1
        assert metrics.error_rate == 100.0
    
    def test_record_warning(self, metrics):
        """Testa registro de warning."""
        metrics.record_log("WARNING", "SYSTEM", 150, 0.3)
        
        assert metrics.warnings == 1
    
    def test_average_calculation(self, metrics):
        """Testa cálculo de médias."""
        for i in range(10):
            metrics.record_log("INFO", "SYSTEM", 100 + i, 0.1 + i * 0.1)
        
        assert metrics.total_logs == 10
        assert metrics.avg_log_size > 100
        assert metrics.avg_response_time > 0
    
    def test_get_stats(self, metrics):
        """Testa obtenção de estatísticas."""
        metrics.record_log("INFO", "SYSTEM", 100, 0.5)
        metrics.record_log("ERROR", "ERROR", 200, 1.0)
        
        stats = metrics.get_stats()
        
        assert stats["total_logs"] == 2
        assert stats["errors"] == 1
        assert stats["error_rate"] == 50.0
        assert "logs_by_level" in stats
        assert "logs_by_category" in stats


class TestAdvancedStructuredLoggerConcurrency:
    """Testes de concorrência para AdvancedStructuredLogger."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Diretório temporário para logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def logger(self, temp_log_dir):
        """Instância de logger para testes."""
        return AdvancedStructuredLogger(
            log_dir=temp_log_dir,
            log_level="DEBUG",
            enable_elk=False
        )
    
    def test_concurrent_logging(self, logger):
        """Testa logging concorrente."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(100):
                    logger.log_with_context(
                        level="INFO",
                        message=f"Worker {worker_id} - Message {i}",
                        category=LogCategory.SYSTEM
                    )
                results.append(f"worker_{worker_id}_completed")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(results) == 5
        
        # Verifica se todos os logs foram registrados
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 500  # 5 workers * 100 messages
    
    def test_concurrent_context_management(self, logger):
        """Testa gerenciamento concorrente de contexto."""
        results = []
        
        def context_worker(worker_id):
            try:
                correlation_id = f"corr_{worker_id}"
                user_id = f"user_{worker_id}"
                
                logger.set_correlation_id(correlation_id)
                logger.set_user_context(user_id)
                
                # Verifica se contexto foi definido corretamente
                assert logger.correlation_id == correlation_id
                assert logger.user_id == user_id
                
                logger.log_with_context(
                    level="INFO",
                    message=f"Context test from worker {worker_id}",
                    category=LogCategory.SYSTEM
                )
                
                results.append(f"worker_{worker_id}_success")
            except Exception as e:
                results.append(f"worker_{worker_id}_error: {e}")
        
        threads = [threading.Thread(target=context_worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verifica se todos os workers completaram com sucesso
        success_count = len([r for r in results if "success" in r])
        assert success_count == 10


class TestAdvancedStructuredLoggerEdgeCases:
    """Testes para edge cases e cenários extremos."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Diretório temporário para logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def logger(self, temp_log_dir):
        """Instância de logger para testes."""
        return AdvancedStructuredLogger(
            log_dir=temp_log_dir,
            log_level="DEBUG",
            enable_elk=False
        )
    
    def test_large_message_logging(self, logger):
        """Testa logging de mensagens muito grandes."""
        large_message = "x" * 100000  # 100KB
        
        logger.log_with_context(
            level="INFO",
            message=large_message,
            category=LogCategory.SYSTEM
        )
        
        # Verifica se log foi processado sem erro
        metrics = logger.get_metrics()
        assert metrics["total_logs"] > 0
    
    def test_special_characters_in_message(self, logger):
        """Testa mensagens com caracteres especiais."""
        special_messages = [
            "Mensagem com acentos: áéíóú",
            "Mensagem com emojis: 🚀📊💻",
            "Mensagem com quebras de linha:\nlinha1\nlinha2",
            "Mensagem com aspas: \"teste\" e 'teste'",
            "Mensagem com caracteres especiais: !@#$%^&*()",
            "Mensagem com unicode: \u00e1\u00e9\u00ed\u00f3\u00fa"
        ]
        
        for message in special_messages:
            logger.log_with_context(
                level="INFO",
                message=message,
                category=LogCategory.SYSTEM
            )
        
        # Verifica se todos os logs foram processados
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == len(special_messages)
    
    def test_very_frequent_logging(self, logger):
        """Testa logging muito frequente."""
        start_time = time.time()
        
        for i in range(10000):  # 10k logs
            logger.log_with_context(
                level="INFO",
                message=f"Frequent log {i}",
                category=LogCategory.SYSTEM
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verifica se todos foram processados
        metrics = logger.get_metrics()
        assert metrics["total_logs"] == 10000
        
        # Verifica se performance é aceitável (< 30 segundos)
        assert duration < 30.0
    
    def test_log_directory_permissions(self):
        """Testa comportamento com problemas de permissão."""
        # Tenta usar diretório sem permissão de escrita
        read_only_dir = "/tmp/readonly_test_dir"
        os.makedirs(read_only_dir, exist_ok=True)
        os.chmod(read_only_dir, 0o444)  # Somente leitura
        
        try:
            logger = AdvancedStructuredLogger(log_dir=read_only_dir)
            # Deve falhar graciosamente ou usar fallback
            assert logger is not None
        except Exception:
            # É aceitável falhar se não conseguir criar arquivos
            pass
        finally:
            os.chmod(read_only_dir, 0o755)
            shutil.rmtree(read_only_dir)


class TestAdvancedStructuredLoggerIntegration:
    """Testes de integração para AdvancedStructuredLogger."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Diretório temporário para logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def logger(self, temp_log_dir):
        """Instância de logger para testes."""
        return AdvancedStructuredLogger(
            log_dir=temp_log_dir,
            log_level="DEBUG",
            enable_elk=False
        )
    
    def test_log_function_call_decorator(self, logger):
        """Testa decorator de logging de função."""
        @log_function_call(category=LogCategory.API)
        def test_function(param1, param2):
            time.sleep(0.1)  # Simula processamento
            return param1 + param2
        
        result = test_function(1, 2)
        
        assert result == 3
        
        # Verifica se log foi gerado
        metrics = logger.get_metrics()
        assert metrics["total_logs"] > 0
    
    def test_global_logger_functions(self):
        """Testa funções globais de logging."""
        # Testa funções de logging global
        log_info("Test info message")
        log_warning("Test warning message")
        log_error("Test error message")
        log_critical("Test critical message")
        log_audit("Test audit message")
        log_security("Test security message")
        log_performance("Test performance message")
        
        # Verifica se logs foram gerados (via get_logger)
        logger = get_logger()
        metrics = logger.get_metrics()
        assert metrics["total_logs"] >= 7
    
    def test_correlation_id_global_functions(self):
        """Testa funções globais de correlation ID."""
        correlation_id = "global-test-123"
        user_id = "global-user-456"
        
        set_correlation_id(correlation_id)
        set_user_context(user_id)
        
        # Verifica se contexto foi definido
        logger = get_logger()
        assert logger.correlation_id == correlation_id
        assert logger.user_id == user_id
        
        # Testa limpeza
        clear_context()
        assert logger.correlation_id is None
        assert logger.user_id is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 