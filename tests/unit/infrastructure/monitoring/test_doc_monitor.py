from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Monitoramento de Documentação
============================================================

Tracing ID: TEST_DOC_MONITOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação

Objetivo: Validar funcionalidades do sistema de monitoramento de documentação
enterprise, incluindo detecção de mudanças, geração de alertas e métricas.
"""

import os
import json
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Adicionar diretório raiz ao path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from infrastructure.monitoring.doc_monitor import (
    DocumentationMonitor,
    DocumentChangeHandler,
    FileChange,
    MonitoringAlert,
    MonitoringReport,
    start_documentation_monitoring
)


class TestDocumentationMonitor:
    """Testes para a classe DocumentationMonitor"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(self.docs_dir)
        
        # Criar arquivo de configuração temporário
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        config = {
            "watch_paths": [self.docs_dir],
            "semantic_threshold": 0.85,
            "quality_threshold": 0.80,
            "alert_cooldown_minutes": 30
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        
        # Mock dos serviços dependentes
        self.mock_embedding_service = Mock()
        self.mock_quality_analyzer = Mock()
        self.mock_metrics_collector = Mock()
        
        # Inicializar monitor com mocks
        with patch('infrastructure.monitoring.doc_monitor.SemanticEmbeddingService', return_value=self.mock_embedding_service), \
             patch('infrastructure.monitoring.doc_monitor.DocQualityAnalyzer', return_value=self.mock_quality_analyzer), \
             patch('infrastructure.monitoring.doc_monitor.MetricsCollector', return_value=self.mock_metrics_collector):
            
            self.monitor = DocumentationMonitor(
                docs_path=self.docs_dir,
                config_path=self.config_file,
                alert_threshold=0.85,
                check_interval=1
            )
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'monitor') and self.monitor.is_monitoring:
            self.monitor.stop_monitoring()
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Teste de inicialização do monitor"""
        assert self.monitor.docs_path == Path(self.docs_dir)
        assert self.monitor.config_path == self.config_file
        assert self.monitor.alert_threshold == 0.85
        assert self.monitor.check_interval == 1
        assert not self.monitor.is_monitoring
        assert self.monitor.tracing_id.startswith("DOC_MONITOR_")
    
    def test_calculate_file_hash(self):
        """Teste de cálculo de hash de arquivo"""
        # Criar arquivo de teste
        test_file = os.path.join(self.docs_dir, "test.md")
        content = "# Test Document\n\nThis is a test document."
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Calcular hash
        hash_result = self.monitor.calculate_file_hash(test_file)
        
        # Verificar que hash foi calculado
        assert isinstance(hash_result, str)
        assert len(hash_result) == 32  # MD5 hash length
        assert hash_result != ""
    
    def test_calculate_file_hash_nonexistent(self):
        """Teste de cálculo de hash para arquivo inexistente"""
        nonexistent_file = os.path.join(self.docs_dir, "nonexistent.md")
        hash_result = self.monitor.calculate_file_hash(nonexistent_file)
        
        # Deve retornar hash vazio para arquivo inexistente
        assert hash_result == ""
    
    def test_get_file_info(self):
        """Teste de obtenção de informações do arquivo"""
        # Criar arquivo de teste
        test_file = os.path.join(self.docs_dir, "test.md")
        content = "# Test Document\n\nThis is a test document."
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Obter informações
        file_info = self.monitor.get_file_info(test_file)
        
        # Verificar informações
        assert file_info['file_path'] == test_file
        assert file_info['file_size'] == len(content)
        assert file_info['file_hash'] != ""
        assert file_info['last_modified'] > 0
        assert file_info['extension'] == '.md'
    
    def test_analyze_file_quality(self):
        """Teste de análise de qualidade do arquivo"""
        # Configurar mock
        self.mock_quality_analyzer.calculate_doc_quality_score.return_value = 0.85
        
        # Criar arquivo de teste
        test_file = os.path.join(self.docs_dir, "test.md")
        content = "# Test Document\n\nThis is a test document."
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Analisar qualidade
        quality_score = self.monitor.analyze_file_quality(test_file)
        
        # Verificar resultado
        assert quality_score == 0.85
        self.mock_quality_analyzer.calculate_doc_quality_score.assert_called_once()
    
    def test_scan_file_security(self):
        """Teste de escaneamento de segurança do arquivo"""
        # Criar arquivo com dados sensíveis
        test_file = os.path.join(self.docs_dir, "test.md")
        content = "# Test Document\n\nAPI_KEY=sk-1234567890abcdef\nPassword: secret123"
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Escanear segurança
        security_issues = self.monitor.scan_file_security(test_file)
        
        # Verificar que problemas foram detectados
        assert isinstance(security_issues, list)
        # Deve detectar pelo menos a API key e password
        assert len(security_issues) >= 2
    
    def test_calculate_semantic_similarity(self):
        """Teste de cálculo de similaridade semântica"""
        # Configurar mock
        self.mock_embedding_service.calculate_similarity.return_value = 0.92
        
        # Criar arquivo de teste
        test_file = os.path.join(self.docs_dir, "test.md")
        content = "# Test Document\n\nThis is a test document."
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Calcular similaridade
        similarity = self.monitor.calculate_semantic_similarity(test_file)
        
        # Verificar resultado
        assert similarity == 0.92
        self.mock_embedding_service.calculate_similarity.assert_called_once()
    
    def test_handle_file_change_created(self):
        """Teste de tratamento de arquivo criado"""
        # Criar arquivo
        test_file = os.path.join(self.docs_dir, "new_file.md")
        content = "# New File\n\nThis is a new file."
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Simular mudança
        self.monitor.handle_file_change(test_file, 'created')
        
        # Verificar que mudança foi registrada
        assert len(self.monitor.change_history) > 0
        last_change = self.monitor.change_history[-1]
        assert last_change.file_path == test_file
        assert last_change.change_type == 'created'
    
    def test_handle_file_change_modified(self):
        """Teste de tratamento de arquivo modificado"""
        # Criar arquivo inicial
        test_file = os.path.join(self.docs_dir, "test.md")
        initial_content = "# Test Document\n\nInitial content."
        with open(test_file, 'w') as f:
            f.write(initial_content)
        
        # Simular primeira mudança
        self.monitor.handle_file_change(test_file, 'created')
        
        # Modificar arquivo
        modified_content = "# Test Document\n\nModified content."
        with open(test_file, 'w') as f:
            f.write(modified_content)
        
        # Simular modificação
        self.monitor.handle_file_change(test_file, 'modified')
        
        # Verificar que mudança foi registrada
        assert len(self.monitor.change_history) >= 2
        last_change = self.monitor.change_history[-1]
        assert last_change.file_path == test_file
        assert last_change.change_type == 'modified'
    
    def test_generate_alerts_for_change(self):
        """Teste de geração de alertas para mudança"""
        # Criar mudança de teste
        change = FileChange(
            timestamp=datetime.now().isoformat(),
            file_path=os.path.join(self.docs_dir, "test.md"),
            change_type='modified',
            file_hash="abc123",
            file_size=100,
            quality_score=0.70,  # Abaixo do threshold
            security_issues=[{"type": "api_key", "severity": "high"}],
            semantic_similarity=0.80
        )
        
        # Gerar alertas
        self.monitor.generate_alerts_for_change(change)
        
        # Verificar que alertas foram gerados
        assert len(self.monitor.alert_history) > 0
        
        # Verificar alerta de qualidade
        quality_alerts = [a for a in self.monitor.alert_history if a.category == 'quality']
        assert len(quality_alerts) > 0
        
        # Verificar alerta de segurança
        security_alerts = [a for a in self.monitor.alert_history if a.category == 'security']
        assert len(security_alerts) > 0
    
    def test_collect_change_metrics(self):
        """Teste de coleta de métricas de mudança"""
        # Criar mudança de teste
        change = FileChange(
            timestamp=datetime.now().isoformat(),
            file_path=os.path.join(self.docs_dir, "test.md"),
            change_type='modified',
            file_hash="abc123",
            file_size=100,
            quality_score=0.85,
            security_issues=[],
            semantic_similarity=0.90
        )
        
        # Coletar métricas
        self.monitor.collect_change_metrics(change)
        
        # Verificar que métricas foram coletadas
        self.mock_metrics_collector.record_document_change.assert_called_once()
    
    def test_detect_divergences(self):
        """Teste de detecção de divergências"""
        # Configurar mocks
        self.mock_embedding_service.calculate_similarity.return_value = 0.75  # Abaixo do threshold
        
        # Criar arquivo de teste
        test_file = os.path.join(self.docs_dir, "test.md")
        content = "# Test Document\n\nThis is a test document."
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Simular mudança
        self.monitor.handle_file_change(test_file, 'created')
        
        # Detectar divergências
        divergences = self.monitor.detect_divergences()
        
        # Verificar que divergências foram detectadas
        assert isinstance(divergences, list)
    
    def test_generate_monitoring_report(self):
        """Teste de geração de relatório de monitoramento"""
        # Simular algumas mudanças e alertas
        change = FileChange(
            timestamp=datetime.now().isoformat(),
            file_path=os.path.join(self.docs_dir, "test.md"),
            change_type='created',
            file_hash="abc123",
            file_size=100,
            quality_score=0.85,
            security_issues=[],
            semantic_similarity=0.90
        )
        self.monitor.change_history.append(change)
        
        alert = MonitoringAlert(
            timestamp=datetime.now().isoformat(),
            alert_id="test_alert_001",
            severity="medium",
            category="quality",
            message="Test alert",
            file_path=os.path.join(self.docs_dir, "test.md")
        )
        self.monitor.alert_history.append(alert)
        
        # Configurar mocks para métricas
        self.mock_metrics_collector.get_quality_metrics.return_value = {"avg_quality": 0.85}
        self.mock_metrics_collector.get_performance_metrics.return_value = {"avg_generation_time": 2.5}
        
        # Gerar relatório
        report = self.monitor.generate_monitoring_report(duration=60.0)
        
        # Verificar relatório
        assert isinstance(report, MonitoringReport)
        assert report.monitoring_id.startswith("MONITOR_REPORT_")
        assert report.duration == 60.0
        assert report.files_monitored >= 0
        assert report.changes_detected >= 1
        assert report.alerts_generated >= 1
        assert len(report.changes) >= 1
        assert len(report.alerts) >= 1
        assert isinstance(report.metrics, dict)
    
    def test_save_report(self):
        """Teste de salvamento de relatório"""
        # Criar relatório de teste
        report = MonitoringReport(
            timestamp=datetime.now().isoformat(),
            monitoring_id="test_report_001",
            duration=60.0,
            files_monitored=1,
            changes_detected=1,
            alerts_generated=1,
            quality_score=0.85,
            security_score=0.90,
            compliance_score=0.95,
            changes=[],
            alerts=[],
            metrics={}
        )
        
        # Salvar relatório
        output_path = os.path.join(self.temp_dir, "test_report.json")
        self.monitor.save_report(report, output_path)
        
        # Verificar que arquivo foi criado
        assert os.path.exists(output_path)
        
        # Verificar conteúdo
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['monitoring_id'] == "test_report_001"
        assert saved_data['duration'] == 60.0
    
    @patch('infrastructure.monitoring.doc_monitor.Observer')
    def test_start_monitoring(self, mock_observer):
        """Teste de início de monitoramento"""
        # Configurar mock
        mock_observer_instance = Mock()
        mock_observer.return_value = mock_observer_instance
        
        # Iniciar monitoramento
        self.monitor.start_monitoring()
        
        # Verificar que monitoramento foi iniciado
        assert self.monitor.is_monitoring
        mock_observer_instance.schedule.assert_called()
        mock_observer_instance.start.assert_called()
    
    @patch('infrastructure.monitoring.doc_monitor.Observer')
    def test_stop_monitoring(self, mock_observer):
        """Teste de parada de monitoramento"""
        # Configurar mock
        mock_observer_instance = Mock()
        mock_observer.return_value = mock_observer_instance
        
        # Iniciar e parar monitoramento
        self.monitor.start_monitoring()
        self.monitor.stop_monitoring()
        
        # Verificar que monitoramento foi parado
        assert not self.monitor.is_monitoring
        mock_observer_instance.stop.assert_called()
        mock_observer_instance.join.assert_called()
    
    def test_get_current_status(self):
        """Teste de obtenção de status atual"""
        # Obter status
        status = self.monitor.get_current_status()
        
        # Verificar estrutura do status
        assert isinstance(status, dict)
        assert 'monitoring_active' in status
        assert 'files_monitored' in status
        assert 'changes_detected' in status
        assert 'alerts_generated' in status
        assert 'last_check' in status
        assert 'uptime' in status
    
    def test_resolve_alert(self):
        """Teste de resolução de alerta"""
        # Criar alerta de teste
        alert = MonitoringAlert(
            timestamp=datetime.now().isoformat(),
            alert_id="test_alert_001",
            severity="medium",
            category="quality",
            message="Test alert",
            file_path=os.path.join(self.docs_dir, "test.md")
        )
        self.monitor.alert_history.append(alert)
        
        # Resolver alerta
        result = self.monitor.resolve_alert("test_alert_001")
        
        # Verificar que alerta foi resolvido
        assert result is True
        resolved_alert = next((a for a in self.monitor.alert_history if a.alert_id == "test_alert_001"), None)
        assert resolved_alert is not None
        assert resolved_alert.resolved is True
    
    def test_resolve_nonexistent_alert(self):
        """Teste de resolução de alerta inexistente"""
        # Tentar resolver alerta inexistente
        result = self.monitor.resolve_alert("nonexistent_alert")
        
        # Verificar que retorna False
        assert result is False


class TestDocumentChangeHandler:
    """Testes para a classe DocumentChangeHandler"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(self.docs_dir)
        
        # Mock do monitor
        self.mock_monitor = Mock()
        self.mock_monitor.tracing_id = "TEST_MONITOR_001"
        
        # Criar handler
        self.handler = DocumentChangeHandler(self.mock_monitor)
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_should_monitor_file_markdown(self):
        """Teste de verificação de arquivo markdown"""
        file_path = os.path.join(self.docs_dir, "test.md")
        result = self.handler._should_monitor_file(file_path)
        assert result is True
    
    def test_should_monitor_file_python(self):
        """Teste de verificação de arquivo python"""
        file_path = os.path.join(self.docs_dir, "test.py")
        result = self.handler._should_monitor_file(file_path)
        assert result is True
    
    def test_should_monitor_file_excluded_extension(self):
        """Teste de verificação de arquivo com extensão excluída"""
        file_path = os.path.join(self.docs_dir, "test.txt")
        result = self.handler._should_monitor_file(file_path)
        assert result is False
    
    def test_should_monitor_file_excluded_pattern(self):
        """Teste de verificação de arquivo com padrão excluído"""
        file_path = os.path.join(self.docs_dir, "node_modules", "test.md")
        result = self.handler._should_monitor_file(file_path)
        assert result is False
    
    def test_on_created(self):
        """Teste de evento de criação de arquivo"""
        # Criar evento mock
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = os.path.join(self.docs_dir, "test.md")
        
        # Configurar mock para retornar True
        with patch.object(self.handler, '_should_monitor_file', return_value=True):
            self.handler.on_created(mock_event)
            
            # Verificar que monitor foi chamado
            self.mock_monitor.handle_file_change.assert_called_once_with(
                mock_event.src_path, 'created'
            )
    
    def test_on_modified(self):
        """Teste de evento de modificação de arquivo"""
        # Criar evento mock
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = os.path.join(self.docs_dir, "test.md")
        
        # Configurar mock para retornar True
        with patch.object(self.handler, '_should_monitor_file', return_value=True):
            self.handler.on_modified(mock_event)
            
            # Verificar que monitor foi chamado
            self.mock_monitor.handle_file_change.assert_called_once_with(
                mock_event.src_path, 'modified'
            )
    
    def test_on_deleted(self):
        """Teste de evento de exclusão de arquivo"""
        # Criar evento mock
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = os.path.join(self.docs_dir, "test.md")
        
        # Configurar mock para retornar True
        with patch.object(self.handler, '_should_monitor_file', return_value=True):
            self.handler.on_deleted(mock_event)
            
            # Verificar que monitor foi chamado
            self.mock_monitor.handle_file_change.assert_called_once_with(
                mock_event.src_path, 'deleted'
            )
    
    def test_ignore_directory_events(self):
        """Teste de ignorar eventos de diretório"""
        # Criar evento mock de diretório
        mock_event = Mock()
        mock_event.is_directory = True
        mock_event.src_path = os.path.join(self.docs_dir, "subdir")
        
        # Chamar todos os handlers
        self.handler.on_created(mock_event)
        self.handler.on_modified(mock_event)
        self.handler.on_deleted(mock_event)
        
        # Verificar que monitor não foi chamado
        self.mock_monitor.handle_file_change.assert_not_called()


class TestStartDocumentationMonitoring:
    """Testes para função de conveniência"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Configuração de teste
        config = {
            "watch_paths": [self.temp_dir],
            "semantic_threshold": 0.85,
            "quality_threshold": 0.80,
            "alert_cooldown_minutes": 30
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('infrastructure.monitoring.doc_monitor.DocumentationMonitor')
    def test_start_monitoring_with_config(self, mock_monitor_class):
        """Teste de início de monitoramento com configuração"""
        # Configurar mock
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor
        
        # Iniciar monitoramento
        result = start_documentation_monitoring(self.config_file)
        
        # Verificar que monitor foi criado e iniciado
        mock_monitor_class.assert_called_once()
        mock_monitor.start_monitoring.assert_called_once()
        assert result == mock_monitor
    
    @patch('infrastructure.monitoring.doc_monitor.DocumentationMonitor')
    def test_start_monitoring_without_config(self, mock_monitor_class):
        """Teste de início de monitoramento sem configuração"""
        # Configurar mock
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor
        
        # Iniciar monitoramento sem config
        result = start_documentation_monitoring()
        
        # Verificar que monitor foi criado com configuração padrão
        mock_monitor_class.assert_called_once()
        mock_monitor.start_monitoring.assert_called_once()
        assert result == mock_monitor
    
    @patch('infrastructure.monitoring.doc_monitor.DocumentationMonitor')
    def test_start_monitoring_nonexistent_config(self, mock_monitor_class):
        """Teste de início de monitoramento com config inexistente"""
        # Configurar mock
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor
        
        # Iniciar monitoramento com config inexistente
        result = start_documentation_monitoring("nonexistent_config.json")
        
        # Verificar que monitor foi criado com configuração padrão
        mock_monitor_class.assert_called_once()
        mock_monitor.start_monitoring.assert_called_once()
        assert result == mock_monitor


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-value"]) 