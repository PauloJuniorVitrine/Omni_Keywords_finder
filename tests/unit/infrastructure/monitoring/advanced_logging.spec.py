"""
Testes para Sistema de Logging Estruturado Avançado - Fase 3.1
Tracing ID: CHECKLIST_FINAL_20250127_003
Data: 2025-01-27
Status: IMPLEMENTAÇÃO COMPLETA

Testes para validar:
- structlog para logging estruturado
- Correlation IDs automáticos
- Log rotation configurável
- Integração ELK Stack
- Performance otimizada
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import time
import uuid

# Importar módulos de teste
try:
    from infrastructure.logging.advanced_structured_logger import (
        AdvancedStructuredLogger,
        LogCategory,
        LogMetrics,
        ELKStackIntegration,
        get_logger,
        set_correlation_id,
        set_user_context,
        clear_context,
        log_info,
        log_warning,
        log_error,
        log_critical,
        log_audit,
        log_security,
        log_performance,
        log_function_call
    )
    from infrastructure.logging.log_rotation_config import (
        LogRotator,
        LogRotationConfig,
        get_log_rotator
    )
    from infrastructure.logging.elk_stack_config import (
        ELKStackConfig,
        ElasticsearchConfig,
        LogstashConfig,
        KibanaConfig,
        ELKStackManager,
        get_elk_manager
    )
    ADVANCED_LOGGING_AVAILABLE = True
except ImportError:
    ADVANCED_LOGGING_AVAILABLE = False

@pytest.mark.skipif(not ADVANCED_LOGGING_AVAILABLE, reason="Sistema avançado de logging não disponível")
class TestAdvancedStructuredLogger:
    """Testes para o sistema de logging estruturado avançado."""
    
    def setup_method(self):
        """Configurar para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuração de teste
        self.config = {
            'log_dir': str(self.log_dir),
            'log_level': 'DEBUG',
            'enable_json': True,
            'enable_console': False,
            'enable_file': True,
            'enable_elk': False
        }
        
        self.logger = AdvancedStructuredLogger(**self.config)
    
    def teardown_method(self):
        """Limpar após cada teste."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_initialization(self):
        """Testar inicialização do logger."""
        assert self.logger is not None
        assert self.logger.log_dir == self.log_dir
        assert self.logger.log_level == 'DEBUG'
        assert self.logger.enable_json is True
        assert self.logger.enable_file is True
    
    def test_correlation_id_setting(self):
        """Testar definição de correlation ID."""
        correlation_id = str(uuid.uuid4())
        self.logger.set_correlation_id(correlation_id)
        
        # Verificar se foi definido no contexto
        from infrastructure.logging.advanced_structured_logger import correlation_id_var
        assert correlation_id_var.get() == correlation_id
    
    def test_user_context_setting(self):
        """Testar definição de contexto do usuário."""
        user_id = "user123"
        request_id = "req456"
        session_id = "sess789"
        
        self.logger.set_user_context(user_id, request_id, session_id)
        
        # Verificar se foram definidos no contexto
        from infrastructure.logging.advanced_structured_logger import (
            user_id_var, request_id_var, session_id_var
        )
        assert user_id_var.get() == user_id
        assert request_id_var.get() == request_id
        assert session_id_var.get() == session_id
    
    def test_log_with_context(self):
        """Testar log com contexto."""
        correlation_id = str(uuid.uuid4())
        self.logger.set_correlation_id(correlation_id)
        
        # Fazer log
        self.logger.log_with_context(
            level="info",
            message="Test message",
            category=LogCategory.SYSTEM,
            test_field="test_value"
        )
        
        # Verificar se o arquivo de log foi criado
        log_files = list(self.log_dir.glob("*.log"))
        assert len(log_files) > 0
        
        # Verificar conteúdo do log
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            log_data = json.loads(log_content.strip())
            
            assert log_data['message'] == "Test message"
            assert log_data['correlation_id'] == correlation_id
            assert log_data['category'] == 'system'
            assert log_data['test_field'] == 'test_value'
    
    def test_log_categories(self):
        """Testar diferentes categorias de log."""
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
            self.logger.log_with_context(
                level="info",
                message=f"Test {category.value}",
                category=category
            )
        
        # Verificar se todos os logs foram criados
        log_files = list(self.log_dir.glob("*.log"))
        assert len(log_files) > 0
    
    def test_log_levels(self):
        """Testar diferentes níveis de log."""
        levels = ["debug", "info", "warning", "error", "critical"]
        
        for level in levels:
            self.logger.log_with_context(
                level=level,
                message=f"Test {level}",
                category=LogCategory.SYSTEM
            )
        
        # Verificar se todos os logs foram criados
        log_files = list(self.log_dir.glob("*.log"))
        assert len(log_files) > 0
    
    def test_log_function_call_decorator(self):
        """Testar decorator de log de função."""
        @log_function_call(LogCategory.SYSTEM)
        def test_function(arg1, arg2, kwarg1="default"):
            time.sleep(0.1)  # Simular processamento
            return arg1 + arg2
        
        # Chamar função
        result = test_function(1, 2, kwarg1="test")
        
        assert result == 3
        
        # Verificar se os logs foram criados
        log_files = list(self.log_dir.glob("*.log"))
        assert len(log_files) > 0
    
    def test_log_function_call_decorator_with_error(self):
        """Testar decorator de log de função com erro."""
        @log_function_call(LogCategory.SYSTEM)
        def test_function_with_error():
            raise ValueError("Test error")
        
        # Chamar função que gera erro
        with pytest.raises(ValueError):
            test_function_with_error()
        
        # Verificar se os logs de erro foram criados
        log_files = list(self.log_dir.glob("*.log"))
        assert len(log_files) > 0

@pytest.mark.skipif(not ADVANCED_LOGGING_AVAILABLE, reason="Sistema avançado de logging não disponível")
class TestLogMetrics:
    """Testes para métricas de logging."""
    
    def setup_method(self):
        """Configurar para cada teste."""
        self.metrics = LogMetrics()
    
    def test_record_log(self):
        """Testar registro de métricas de log."""
        self.metrics.record_log("info", "system", 100, 50.0)
        self.metrics.record_log("error", "api", 200, 100.0)
        self.metrics.record_log("warning", "database", 150, 75.0)
        
        stats = self.metrics.get_stats()
        
        assert stats['total_logs'] == 3
        assert stats['logs_by_level']['info'] == 1
        assert stats['logs_by_level']['error'] == 1
        assert stats['logs_by_level']['warning'] == 1
        assert stats['errors'] == 1
        assert stats['warnings'] == 1
        assert stats['avg_log_size'] > 0
        assert stats['avg_response_time'] > 0
        assert stats['error_rate'] == (1/3) * 100
    
    def test_error_rate_calculation(self):
        """Testar cálculo da taxa de erro."""
        # Sem logs
        stats = self.metrics.get_stats()
        assert stats['error_rate'] == 0
        
        # Com logs mas sem erros
        self.metrics.record_log("info", "system", 100)
        stats = self.metrics.get_stats()
        assert stats['error_rate'] == 0
        
        # Com erros
        self.metrics.record_log("error", "api", 100)
        stats = self.metrics.get_stats()
        assert stats['error_rate'] == 50.0

@pytest.mark.skipif(not ADVANCED_LOGGING_AVAILABLE, reason="Sistema avançado de logging não disponível")
class TestELKStackIntegration:
    """Testes para integração ELK Stack."""
    
    def setup_method(self):
        """Configurar para cada teste."""
        self.elk_integration = ELKStackIntegration()
    
    @patch('requests.Session.post')
    def test_send_to_elasticsearch_success(self, mock_post):
        """Testar envio bem-sucedido para Elasticsearch."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        # Configurar URL
        self.elk_integration.elasticsearch_url = "http://localhost:9200"
        
        log_data = {"message": "test", "level": "info"}
        result = self.elk_integration.send_to_elasticsearch(log_data)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_send_to_elasticsearch_failure(self, mock_post):
        """Testar falha no envio para Elasticsearch."""
        mock_post.side_effect = Exception("Connection error")
        
        log_data = {"message": "test", "level": "info"}
        result = self.elk_integration.send_to_elasticsearch(log_data)
        
        assert result is False
    
    @patch('requests.Session.post')
    def test_send_to_logstash_success(self, mock_post):
        """Testar envio bem-sucedido para Logstash."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Configurar URL
        self.elk_integration.logstash_url = "http://localhost:5044"
        
        log_data = {"message": "test", "level": "info"}
        result = self.elk_integration.send_to_logstash(log_data)
        
        assert result is True
        mock_post.assert_called_once()

@pytest.mark.skipif(not ADVANCED_LOGGING_AVAILABLE, reason="Sistema avançado de logging não disponível")
class TestLogRotation:
    """Testes para rotação de logs."""
    
    def setup_method(self):
        """Configurar para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = LogRotationConfig(
            max_file_size=1024,  # 1KB para teste
            backup_count=3,
            compress_old_logs=True,
            retention_days=1
        )
        
        self.rotator = LogRotator(self.config)
        self.rotator.log_dir = self.log_dir
    
    def teardown_method(self):
        """Limpar após cada teste."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_rotate_log_file(self):
        """Testar rotação de arquivo de log."""
        # Criar arquivo de log grande
        log_file = self.log_dir / "test.log"
        with open(log_file, 'w') as f:
            f.write("x" * 2048)  # 2KB
        
        # Rotacionar
        result = self.rotator.rotate_log_file(log_file)
        
        assert result is True
        
        # Verificar se arquivo foi rotacionado
        backup_files = list(self.log_dir.glob("test_*"))
        assert len(backup_files) > 0
    
    def test_compress_log_file(self):
        """Testar compressão de arquivo de log."""
        # Criar arquivo de log
        log_file = self.log_dir / "test.log"
        with open(log_file, 'w') as f:
            f.write("Test log content" * 100)
        
        # Comprimir
        self.rotator._compress_log_file(log_file)
        
        # Verificar se arquivo comprimido foi criado
        compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
        assert compressed_file.exists()
        
        # Verificar se arquivo original foi removido
        assert not log_file.exists()
    
    def test_cleanup_old_logs(self):
        """Testar limpeza de logs antigos."""
        # Criar arquivo de log antigo
        old_log = self.log_dir / "old.log"
        with open(old_log, 'w') as f:
            f.write("Old log content")
        
        # Modificar timestamp para ser antigo
        old_timestamp = time.time() - (2 * 24 * 3600)  # 2 dias atrás
        os.utime(old_log, (old_timestamp, old_timestamp))
        
        # Limpar logs antigos
        self.rotator.cleanup_old_logs()
        
        # Verificar se arquivo antigo foi removido
        assert not old_log.exists()
    
    def test_get_disk_usage(self):
        """Testar obtenção de uso de disco."""
        usage = self.rotator.get_disk_usage()
        
        assert 'total_gb' in usage
        assert 'used_gb' in usage
        assert 'free_gb' in usage
        assert 'usage_percent' in usage
        assert 'log_dir_size_gb' in usage
        assert usage['usage_percent'] >= 0
        assert usage['usage_percent'] <= 100

@pytest.mark.skipif(not ADVANCED_LOGGING_AVAILABLE, reason="Sistema avançado de logging não disponível")
class TestELKStackConfig:
    """Testes para configuração ELK Stack."""
    
    def setup_method(self):
        """Configurar para cada teste."""
        self.config = ELKStackConfig(
            elasticsearch=ElasticsearchConfig(
                host="localhost",
                port=9200,
                username="test_user",
                password="test_pass"
            ),
            logstash=LogstashConfig(
                host="localhost",
                port=5044
            ),
            kibana=KibanaConfig(
                host="localhost",
                port=5601
            ),
            enabled=True,
            environment="test"
        )
        
        self.manager = ELKStackManager(self.config)
    
    def test_elasticsearch_config(self):
        """Testar configuração do Elasticsearch."""
        assert self.config.elasticsearch.host == "localhost"
        assert self.config.elasticsearch.port == 9200
        assert self.config.elasticsearch.url == "http://test_user:test_pass@localhost:9200"
        
        # Testar nome do índice
        index_name = self.config.elasticsearch.get_index_name("2025.01.27")
        assert index_name == "omni-keywords-logs-2025.01.27"
    
    def test_logstash_config(self):
        """Testar configuração do Logstash."""
        assert self.config.logstash.host == "localhost"
        assert self.config.logstash.port == 5044
        assert self.config.logstash.url == "http://localhost:5044"
    
    def test_kibana_config(self):
        """Testar configuração do Kibana."""
        assert self.config.kibana.host == "localhost"
        assert self.config.kibana.port == 5601
        assert self.config.kibana.url == "http://localhost:5601"
    
    def test_generate_elasticsearch_config(self):
        """Testar geração de configuração do Elasticsearch."""
        config_yaml = self.manager.generate_elasticsearch_config()
        
        assert "cluster.name" in config_yaml
        assert "node.name" in config_yaml
        assert "path.data" in config_yaml
        assert "network.host" in config_yaml
        assert "http.port" in config_yaml
    
    def test_generate_logstash_config(self):
        """Testar geração de configuração do Logstash."""
        config_yaml = self.manager.generate_logstash_config()
        
        assert "input" in config_yaml
        assert "filter" in config_yaml
        assert "output" in config_yaml
        assert "beats" in config_yaml
        assert "elasticsearch" in config_yaml
    
    def test_generate_kibana_dashboards(self):
        """Testar geração de dashboards do Kibana."""
        dashboards = self.manager.generate_kibana_dashboards()
        
        assert "system_overview" in dashboards
        assert "performance_monitoring" in dashboards
        assert "error_analysis" in dashboards
        
        # Verificar estrutura do dashboard
        system_dashboard = dashboards["system_overview"]
        assert "title" in system_dashboard
        assert "panels" in system_dashboard
        assert len(system_dashboard["panels"]) > 0
    
    def test_generate_alert_rules(self):
        """Testar geração de regras de alerta."""
        rules = self.manager.generate_alert_rules()
        
        assert len(rules) > 0
        
        # Verificar estrutura da regra
        rule = rules[0]
        assert "name" in rule
        assert "description" in rule
        assert "condition" in rule
        assert "action" in rule

@pytest.mark.skipif(not ADVANCED_LOGGING_AVAILABLE, reason="Sistema avançado de logging não disponível")
class TestIntegration:
    """Testes de integração do sistema de logging."""
    
    def setup_method(self):
        """Configurar para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar variáveis de ambiente para teste
        os.environ['LOG_MAX_FILE_SIZE'] = '1024'
        os.environ['LOG_BACKUP_COUNT'] = '3'
        os.environ['LOG_COMPRESS'] = 'true'
        os.environ['LOG_RETENTION_DAYS'] = '1'
        os.environ['LOG_CLEANUP_INTERVAL'] = '1'
        os.environ['LOG_MONITOR_DISK'] = 'true'
        os.environ['LOG_MAX_DISK_USAGE'] = '80.0'
    
    def teardown_method(self):
        """Limpar após cada teste."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_logging_workflow(self):
        """Testar workflow completo de logging."""
        # Obter instâncias
        logger = get_logger()
        rotator = get_log_rotator()
        elk_manager = get_elk_manager()
        
        # Configurar diretório de logs
        logger.log_dir = self.log_dir
        rotator.log_dir = self.log_dir
        
        # Fazer logs
        correlation_id = str(uuid.uuid4())
        set_correlation_id(correlation_id)
        
        log_info("Test info message", LogCategory.SYSTEM)
        log_warning("Test warning message", LogCategory.API)
        log_error("Test error message", LogCategory.ERROR)
        
        # Verificar se logs foram criados
        log_files = list(self.log_dir.glob("*.log"))
        assert len(log_files) > 0
        
        # Verificar métricas
        metrics = logger.get_metrics()
        assert metrics['total_logs'] >= 3
        
        # Verificar estatísticas de rotação
        rotation_stats = rotator.get_log_stats()
        assert rotation_stats['total_files'] > 0
        
        # Verificar uso de disco
        disk_usage = rotator.get_disk_usage()
        assert disk_usage['usage_percent'] >= 0
        assert disk_usage['usage_percent'] <= 100

if __name__ == "__main__":
    pytest.main([__file__]) 