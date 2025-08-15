from typing import Dict, List, Optional, Any
"""
Testes Unitários para Sistema de Métricas de Geração de Documentação
Tracing ID: TEST_DOC_GENERATION_METRICS_001_20250127
Data: 2025-01-27
Versão: 1.0

Este módulo implementa testes unitários abrangentes para o sistema
de métricas de geração de documentação enterprise.
"""

import pytest
import tempfile
import shutil
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar o sistema a ser testado
from shared.doc_generation_metrics import (
    DocGenerationMetrics, MetricsCollector, MetricsAnalyzer,
    MetricType, QualityMetric, TimeMetric, CostMetric,
    MetricData, GenerationSession
)

class TestDocGenerationMetrics:
    """
    Testes para DocGenerationMetrics.
    
    Cobre funcionalidades principais do sistema de métricas.
    """
    
    @pytest.fixture
    def metrics_system(self):
        """Cria instância do sistema de métricas para testes."""
        return DocGenerationMetrics({
            'max_history_size': 100,
            'enable_persistence': False
        })
    
    @pytest.fixture
    def temp_storage_path(self):
        """Cria diretório temporário para armazenamento."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        metrics = DocGenerationMetrics()
        
        assert metrics.config == {}
        assert len(metrics.sessions) == 0
        assert len(metrics.metrics_history) == 0
        assert len(metrics.analysis_cache) == 0
        assert metrics.max_history_size == 10000
        assert metrics.storage_path == 'logs/metrics'
        assert metrics.enable_persistence == True
    
    def test_init_custom_values(self):
        """Testa inicialização com valores customizados."""
        config = {
            'max_history_size': 500,
            'storage_path': '/custom/path',
            'enable_persistence': False
        }
        metrics = DocGenerationMetrics(config)
        
        assert metrics.config == config
        assert metrics.max_history_size == 500
        assert metrics.storage_path == '/custom/path'
        assert metrics.enable_persistence == False
    
    def test_start_session(self, metrics_system):
        """Testa início de sessão."""
        session_id = metrics_system.start_session(
            file_path="test.py",
            module_name="test_module",
            function_name="test_function"
        )
        
        assert session_id in metrics_system.sessions
        session = metrics_system.sessions[session_id]
        assert session.file_path == "test.py"
        assert session.module_name == "test_module"
        assert session.function_name == "test_function"
        assert session.status == "running"
        assert session.end_time is None
    
    def test_start_session_minimal_params(self, metrics_system):
        """Testa início de sessão com parâmetros mínimos."""
        session_id = metrics_system.start_session()
        
        assert session_id in metrics_system.sessions
        session = metrics_system.sessions[session_id]
        assert session.file_path is None
        assert session.module_name is None
        assert session.function_name is None
    
    def test_end_session_success(self, metrics_system):
        """Testa finalização de sessão com sucesso."""
        session_id = metrics_system.start_session()
        
        success = metrics_system.end_session(session_id, "completed")
        
        assert success == True
        session = metrics_system.sessions[session_id]
        assert session.status == "completed"
        assert session.end_time is not None
        assert session.error_message is None
    
    def test_end_session_with_error(self, metrics_system):
        """Testa finalização de sessão com erro."""
        session_id = metrics_system.start_session()
        
        success = metrics_system.end_session(
            session_id, 
            "failed", 
            "Erro de teste"
        )
        
        assert success == True
        session = metrics_system.sessions[session_id]
        assert session.status == "failed"
        assert session.error_message == "Erro de teste"
    
    def test_end_session_not_found(self, metrics_system):
        """Testa finalização de sessão inexistente."""
        success = metrics_system.end_session("invalid_session_id")
        
        assert success == False
    
    def test_add_metric_success(self, metrics_system):
        """Testa adição de métrica com sucesso."""
        session_id = metrics_system.start_session()
        
        success = metrics_system.add_metric(
            session_id,
            MetricType.QUALITY,
            "completeness",
            0.85,
            "score",
            {"source": "test"}
        )
        
        assert success == True
        session = metrics_system.sessions[session_id]
        assert len(session.metrics) == 1
        
        metric = session.metrics[0]
        assert metric.metric_type == MetricType.QUALITY
        assert metric.metric_name == "completeness"
        assert metric.value == 0.85
        assert metric.unit == "score"
        assert metric.metadata["source"] == "test"
    
    def test_add_metric_session_not_found(self, metrics_system):
        """Testa adição de métrica em sessão inexistente."""
        success = metrics_system.add_metric(
            "invalid_session_id",
            MetricType.QUALITY,
            "test",
            1.0
        )
        
        assert success == False
    
    def test_get_session_metrics(self, metrics_system):
        """Testa obtenção de métricas de sessão."""
        session_id = metrics_system.start_session()
        
        # Adicionar algumas métricas
        metrics_system.add_metric(session_id, MetricType.QUALITY, "test1", 1.0)
        metrics_system.add_metric(session_id, MetricType.TIME, "test2", 2.0)
        
        metrics = metrics_system.get_session_metrics(session_id)
        
        assert len(metrics) == 2
        assert metrics[0].metric_name == "test1"
        assert metrics[1].metric_name == "test2"
    
    def test_get_session_metrics_not_found(self, metrics_system):
        """Testa obtenção de métricas de sessão inexistente."""
        metrics = metrics_system.get_session_metrics("invalid_session_id")
        
        assert metrics == []
    
    def test_get_session_summary(self, metrics_system):
        """Testa obtenção de resumo de sessão."""
        session_id = metrics_system.start_session("test.py")
        
        # Adicionar métricas
        metrics_system.add_metric(session_id, MetricType.QUALITY, "test", 0.8)
        metrics_system.add_metric(session_id, MetricType.TIME, "test", 1.5)
        
        # Finalizar sessão
        metrics_system.end_session(session_id)
        
        summary = metrics_system.get_session_summary(session_id)
        
        assert summary['session_id'] == session_id
        assert summary['file_path'] == "test.py"
        assert summary['status'] == "completed"
        assert 'statistics' in summary
        assert summary['statistics']['count'] == 2
        assert summary['statistics']['mean'] == 1.15
    
    def test_get_session_summary_not_found(self, metrics_system):
        """Testa obtenção de resumo de sessão inexistente."""
        summary = metrics_system.get_session_summary("invalid_session_id")
        
        assert summary == {}
    
    def test_history_size_limit(self, metrics_system):
        """Testa limite de tamanho do histórico."""
        # Configurar limite baixo
        metrics_system.max_history_size = 3
        
        session_id = metrics_system.start_session()
        
        # Adicionar mais métricas que o limite
        for index in range(5):
            metrics_system.add_metric(session_id, MetricType.QUALITY, f"test{index}", index)
        
        # Deve manter apenas as últimas 3
        assert len(metrics_system.metrics_history) == 3
        assert metrics_system.metrics_history[-1].value == 4
    
    def test_persistence_enabled(self, temp_storage_path):
        """Testa persistência habilitada."""
        config = {
            'storage_path': temp_storage_path,
            'enable_persistence': True
        }
        metrics = DocGenerationMetrics(config)
        
        session_id = metrics.start_session("test.py")
        metrics.add_metric(session_id, MetricType.QUALITY, "test", 0.8)
        metrics.end_session(session_id)
        
        # Verificar se arquivo foi criado
        storage_path = Path(temp_storage_path)
        json_files = list(storage_path.glob("*.json"))
        assert len(json_files) == 1
        
        # Verificar conteúdo do arquivo
        with open(json_files[0], 'r') as f:
            data = json.load(f)
            assert data['session_id'] == session_id
            assert data['file_path'] == "test.py"
            assert len(data['metrics']) == 1
    
    def test_persistence_disabled(self, temp_storage_path):
        """Testa persistência desabilitada."""
        config = {
            'storage_path': temp_storage_path,
            'enable_persistence': False
        }
        metrics = DocGenerationMetrics(config)
        
        session_id = metrics.start_session("test.py")
        metrics.add_metric(session_id, MetricType.QUALITY, "test", 0.8)
        metrics.end_session(session_id)
        
        # Verificar que nenhum arquivo foi criado
        storage_path = Path(temp_storage_path)
        json_files = list(storage_path.glob("*.json"))
        assert len(json_files) == 0

class TestMetricsCollector:
    """
    Testes para MetricsCollector.
    
    Cobre funcionalidades de coleta de métricas.
    """
    
    @pytest.fixture
    def collector(self):
        """Cria instância do coletor para testes."""
        metrics_system = DocGenerationMetrics({'enable_persistence': False})
        return MetricsCollector(metrics_system)
    
    def test_init(self, collector):
        """Testa inicialização do coletor."""
        assert collector.metrics_system is not None
        assert collector.current_session_id is None
        assert len(collector.start_times) == 0
    
    def test_start_collection(self, collector):
        """Testa início de coleta."""
        session_id = collector.start_collection(
            file_path="test.py",
            module_name="test_module",
            function_name="test_function"
        )
        
        assert session_id is not None
        assert collector.current_session_id == session_id
        
        # Verificar se sessão foi criada no sistema
        assert session_id in collector.metrics_system.sessions
    
    def test_end_collection_success(self, collector):
        """Testa finalização de coleta com sucesso."""
        session_id = collector.start_collection()
        
        success = collector.end_collection("completed")
        
        assert success == True
        assert collector.current_session_id is None
        assert len(collector.start_times) == 0
        
        # Verificar se sessão foi finalizada
        session = collector.metrics_system.sessions[session_id]
        assert session.status == "completed"
    
    def test_end_collection_with_error(self, collector):
        """Testa finalização de coleta com erro."""
        session_id = collector.start_collection()
        
        success = collector.end_collection("failed", "Erro de teste")
        
        assert success == True
        session = collector.metrics_system.sessions[session_id]
        assert session.status == "failed"
        assert session.error_message == "Erro de teste"
    
    def test_end_collection_no_session(self, collector):
        """Testa finalização de coleta sem sessão ativa."""
        success = collector.end_collection()
        
        assert success == False
    
    def test_start_timer(self, collector):
        """Testa início de timer."""
        collector.start_timer("test_timer")
        
        assert "test_timer" in collector.start_times
        assert isinstance(collector.start_times["test_timer"], float)
    
    def test_end_timer_success(self, collector):
        """Testa finalização de timer com sucesso."""
        collector.start_collection()
        collector.start_timer("test_timer")
        
        # Aguardar um pouco
        time.sleep(0.1)
        
        elapsed = collector.end_timer("test_timer", "test_metric")
        
        assert elapsed is not None
        assert elapsed > 0
        assert "test_timer" not in collector.start_times
        
        # Verificar se métrica foi registrada
        session = collector.metrics_system.sessions[collector.current_session_id]
        assert len(session.metrics) == 1
        assert session.metrics[0].metric_name == "test_metric"
        assert session.metrics[0].metric_type == MetricType.TIME
    
    def test_end_timer_not_found(self, collector):
        """Testa finalização de timer inexistente."""
        elapsed = collector.end_timer("invalid_timer")
        
        assert elapsed is None
    
    def test_end_timer_no_session(self, collector):
        """Testa finalização de timer sem sessão ativa."""
        collector.start_timer("test_timer")
        
        elapsed = collector.end_timer("test_timer")
        
        assert elapsed is not None
        assert elapsed > 0
        # Não deve registrar métrica sem sessão ativa
        assert len(collector.metrics_system.sessions) == 0
    
    def test_record_quality_metric(self, collector):
        """Testa registro de métrica de qualidade."""
        collector.start_collection()
        
        collector.record_quality_metric("completeness", 0.85, {"source": "test"})
        
        session = collector.metrics_system.sessions[collector.current_session_id]
        assert len(session.metrics) == 1
        
        metric = session.metrics[0]
        assert metric.metric_type == MetricType.QUALITY
        assert metric.metric_name == "completeness"
        assert metric.value == 0.85
        assert metric.unit == "score"
        assert metric.metadata["source"] == "test"
    
    def test_record_cost_metric(self, collector):
        """Testa registro de métrica de custo."""
        collector.start_collection()
        
        collector.record_cost_metric("api_cost", 0.05, "USD", {"provider": "openai"})
        
        session = collector.metrics_system.sessions[collector.current_session_id]
        assert len(session.metrics) == 1
        
        metric = session.metrics[0]
        assert metric.metric_type == MetricType.COST
        assert metric.metric_name == "api_cost"
        assert metric.value == 0.05
        assert metric.unit == "USD"
        assert metric.metadata["currency"] == "USD"
        assert metric.metadata["provider"] == "openai"
    
    def test_record_token_metric(self, collector):
        """Testa registro de métrica de tokens."""
        collector.start_collection()
        
        collector.record_token_metric("input_tokens", 150, {"model": "gpt-4"})
        
        session = collector.metrics_system.sessions[collector.current_session_id]
        assert len(session.metrics) == 1
        
        metric = session.metrics[0]
        assert metric.metric_type == MetricType.TOKENS
        assert metric.metric_name == "input_tokens"
        assert metric.value == 150
        assert metric.unit == "tokens"
        assert metric.metadata["model"] == "gpt-4"

class TestMetricsAnalyzer:
    """
    Testes para MetricsAnalyzer.
    
    Cobre funcionalidades de análise de métricas.
    """
    
    @pytest.fixture
    def analyzer(self):
        """Cria instância do analisador para testes."""
        metrics_system = DocGenerationMetrics({'enable_persistence': False})
        return MetricsAnalyzer(metrics_system)
    
    @pytest.fixture
    def sample_session(self, analyzer):
        """Cria sessão de exemplo com métricas."""
        session_id = analyzer.metrics_system.start_session("test.py")
        
        # Adicionar métricas de qualidade
        analyzer.metrics_system.add_metric(
            session_id, MetricType.QUALITY, "completeness", 0.85
        )
        analyzer.metrics_system.add_metric(
            session_id, MetricType.QUALITY, "coherence", 0.92
        )
        
        # Adicionar métricas de tempo
        analyzer.metrics_system.add_metric(
            session_id, MetricType.TIME, "generation_time", 2.5
        )
        analyzer.metrics_system.add_metric(
            session_id, MetricType.TIME, "validation_time", 0.8
        )
        
        # Adicionar métricas de custo
        analyzer.metrics_system.add_metric(
            session_id, MetricType.COST, "token_cost", 0.03
        )
        analyzer.metrics_system.add_metric(
            session_id, MetricType.COST, "api_cost", 0.02
        )
        
        # Adicionar métricas de tokens
        analyzer.metrics_system.add_metric(
            session_id, MetricType.TOKENS, "input_tokens", 150
        )
        analyzer.metrics_system.add_metric(
            session_id, MetricType.TOKENS, "output_tokens", 200
        )
        
        analyzer.metrics_system.end_session(session_id)
        
        return session_id
    
    def test_init(self, analyzer):
        """Testa inicialização do analisador."""
        assert analyzer.metrics_system is not None
    
    def test_analyze_session(self, analyzer, sample_session):
        """Testa análise de sessão."""
        analysis = analyzer.analyze_session(sample_session)
        
        assert analysis['session_id'] == sample_session
        assert analysis['file_path'] == "test.py"
        assert analysis['status'] == "completed"
        assert analysis['duration'] is not None
        assert 'metrics_summary' in analysis
        assert 'performance_analysis' in analysis
        assert 'quality_analysis' in analysis
        assert 'cost_analysis' in analysis
        assert 'recommendations' in analysis
    
    def test_analyze_session_not_found(self, analyzer):
        """Testa análise de sessão inexistente."""
        analysis = analyzer.analyze_session("invalid_session_id")
        
        assert analysis == {}
    
    def test_analyze_trends(self, analyzer):
        """Testa análise de tendências."""
        # Criar métricas históricas
        for index in range(5):
            session_id = analyzer.metrics_system.start_session(f"test{index}.py")
            analyzer.metrics_system.add_metric(
                session_id, MetricType.QUALITY, "completeness", 0.8 + (index * 0.02)
            )
            analyzer.metrics_system.end_session(session_id)
        
        trends = analyzer.analyze_trends(days=30, metric_type=MetricType.QUALITY)
        
        assert trends['period_days'] == 30
        assert trends['total_metrics'] >= 5
        assert trends['metric_type'] == "quality"
        assert 'trends' in trends
        assert 'statistics' in trends
        assert 'anomalies' in trends
        assert 'optimization_opportunities' in trends
    
    def test_analyze_trends_no_metrics(self, analyzer):
        """Testa análise de tendências sem métricas."""
        trends = analyzer.analyze_trends(days=30)
        
        assert trends['period_days'] == 30
        assert trends['total_metrics'] == 0
        assert trends['metric_type'] == "all"
    
    def test_generate_report(self, analyzer, sample_session):
        """Testa geração de relatório."""
        report = analyzer.generate_report([sample_session], include_trends=False)
        
        assert report['generated_at'] is not None
        assert report['total_sessions'] == 1
        assert sample_session in report['sessions_analysis']
        assert 'overall_statistics' in report
        assert report['trends_analysis'] is None
        assert 'recommendations' in report
    
    def test_generate_report_with_trends(self, analyzer, sample_session):
        """Testa geração de relatório com tendências."""
        report = analyzer.generate_report([sample_session], include_trends=True)
        
        assert report['trends_analysis'] is not None
        assert 'trends' in report['trends_analysis']
    
    def test_generate_report_all_sessions(self, analyzer, sample_session):
        """Testa geração de relatório com todas as sessões."""
        report = analyzer.generate_report()
        
        assert report['total_sessions'] >= 1
        assert sample_session in report['sessions_analysis']
    
    def test_calculate_duration(self, analyzer):
        """Testa cálculo de duração."""
        session_id = analyzer.metrics_system.start_session()
        
        # Aguardar um pouco
        time.sleep(0.1)
        
        analyzer.metrics_system.end_session(session_id)
        session = analyzer.metrics_system.sessions[session_id]
        
        duration = analyzer._calculate_duration(session)
        
        assert duration is not None
        assert duration > 0
    
    def test_calculate_duration_no_end_time(self, analyzer):
        """Testa cálculo de duração sem tempo de fim."""
        session_id = analyzer.metrics_system.start_session()
        session = analyzer.metrics_system.sessions[session_id]
        
        duration = analyzer._calculate_duration(session)
        
        assert duration is None
    
    def test_summarize_metrics(self, analyzer, sample_session):
        """Testa resumo de métricas."""
        session = analyzer.metrics_system.sessions[sample_session]
        summary = analyzer._summarize_metrics(session.metrics)
        
        assert 'quality' in summary
        assert 'time' in summary
        assert 'cost' in summary
        assert 'tokens' in summary
        
        # Verificar estatísticas de qualidade
        quality_stats = summary['quality']
        assert quality_stats['count'] == 2
        assert quality_stats['mean'] == 0.885  # (0.85 + 0.92) / 2
    
    def test_analyze_performance(self, analyzer, sample_session):
        """Testa análise de performance."""
        session = analyzer.metrics_system.sessions[sample_session]
        analysis = analyzer._analyze_performance(session.metrics)
        
        assert analysis['total_time'] == 3.3  # 2.5 + 0.8
        assert 'time_breakdown' in analysis
        assert 'performance_score' in analysis
        assert analysis['time_breakdown']['generation_time'] == 2.5
        assert analysis['time_breakdown']['validation_time'] == 0.8
    
    def test_analyze_quality(self, analyzer, sample_session):
        """Testa análise de qualidade."""
        session = analyzer.metrics_system.sessions[sample_session]
        analysis = analyzer._analyze_quality(session.metrics)
        
        assert analysis['overall_quality_score'] == 0.885
        assert 'quality_breakdown' in analysis
        assert 'quality_issues' in analysis
        assert analysis['quality_breakdown']['completeness'] == 0.85
        assert analysis['quality_breakdown']['coherence'] == 0.92
    
    def test_analyze_quality_with_issues(self, analyzer):
        """Testa análise de qualidade com problemas."""
        session_id = analyzer.metrics_system.start_session()
        analyzer.metrics_system.add_metric(
            session_id, MetricType.QUALITY, "completeness", 0.6  # Baixo
        )
        analyzer.metrics_system.add_metric(
            session_id, MetricType.QUALITY, "coherence", 0.8  # OK
        )
        analyzer.metrics_system.end_session(session_id)
        
        session = analyzer.metrics_system.sessions[session_id]
        analysis = analyzer._analyze_quality(session.metrics)
        
        assert len(analysis['quality_issues']) == 1
        assert analysis['quality_issues'][0]['metric'] == "completeness"
        assert analysis['quality_issues'][0]['value'] == 0.6
    
    def test_analyze_cost(self, analyzer, sample_session):
        """Testa análise de custo."""
        session = analyzer.metrics_system.sessions[sample_session]
        analysis = analyzer._analyze_cost(session.metrics)
        
        assert analysis['total_cost'] == 0.05  # 0.03 + 0.02
        assert 'cost_breakdown' in analysis
        assert 'cost_efficiency' in analysis
        assert analysis['cost_breakdown']['token_cost'] == 0.03
        assert analysis['cost_breakdown']['api_cost'] == 0.02
    
    def test_detect_anomalies(self, analyzer):
        """Testa detecção de anomalias."""
        # Criar métricas com anomalia
        for index in range(10):
            session_id = analyzer.metrics_system.start_session(f"test{index}.py")
            # Valor normal: 0.8
            value = 0.8 if index < 9 else 2.0  # Anomalia no último
            analyzer.metrics_system.add_metric(
                session_id, MetricType.QUALITY, "completeness", value
            )
            analyzer.metrics_system.end_session(session_id)
        
        # Obter métricas históricas
        metrics = analyzer.metrics_system.metrics_history
        anomalies = analyzer._detect_anomalies(metrics)
        
        assert len(anomalies) == 1
        assert anomalies[0]['value'] == 2.0
        assert anomalies[0]['metric'] == "completeness"
    
    def test_identify_optimizations(self, analyzer):
        """Testa identificação de otimizações."""
        # Criar métricas que indicam problemas
        session_id = analyzer.metrics_system.start_session()
        analyzer.metrics_system.add_metric(
            session_id, MetricType.TIME, "generation_time", 120  # Alto
        )
        analyzer.metrics_system.add_metric(
            session_id, MetricType.COST, "api_cost", 0.15  # Alto
        )
        analyzer.metrics_system.add_metric(
            session_id, MetricType.QUALITY, "completeness", 0.6  # Baixo
        )
        analyzer.metrics_system.end_session(session_id)
        
        # Obter métricas históricas
        metrics = analyzer.metrics_system.metrics_history
        optimizations = analyzer._identify_optimizations(metrics)
        
        assert len(optimizations) >= 2  # Pelo menos performance e qualidade
        assert any(opt['type'] == 'performance' for opt in optimizations)
        assert any(opt['type'] == 'quality' for opt in optimizations)
    
    def test_generate_recommendations(self, analyzer, sample_session):
        """Testa geração de recomendações."""
        session = analyzer.metrics_system.sessions[sample_session]
        recommendations = analyzer._generate_recommendations(session.metrics, session)
        
        assert isinstance(recommendations, list)
        # Pode ter recomendações ou não, dependendo dos valores
    
    def test_generate_global_recommendations(self, analyzer, sample_session):
        """Testa geração de recomendações globais."""
        session = analyzer.metrics_system.sessions[sample_session]
        recommendations = analyzer._generate_global_recommendations(session.metrics)
        
        assert isinstance(recommendations, list)
        # Pode ter recomendações ou não, dependendo dos valores

class TestMetricsIntegration:
    """
    Testes de integração para o sistema completo de métricas.
    
    Testa workflows completos e cenários reais de uso.
    """
    
    @pytest.fixture
    def integrated_system(self):
        """Cria sistema integrado para testes."""
        metrics_system = DocGenerationMetrics({'enable_persistence': False})
        collector = MetricsCollector(metrics_system)
        analyzer = MetricsAnalyzer(metrics_system)
        return metrics_system, collector, analyzer
    
    def test_full_workflow(self, integrated_system):
        """Testa workflow completo de métricas."""
        metrics_system, collector, analyzer = integrated_system
        
        # 1. Iniciar coleta
        session_id = collector.start_collection("test.py", "test_module", "test_function")
        
        # 2. Registrar métricas durante o processo
        collector.start_timer("generation")
        time.sleep(0.1)  # Simular trabalho
        collector.end_timer("generation", "generation_time")
        
        collector.record_quality_metric("completeness", 0.85)
        collector.record_quality_metric("coherence", 0.92)
        
        collector.record_cost_metric("api_cost", 0.03, "USD")
        collector.record_token_metric("input_tokens", 150)
        
        # 3. Finalizar coleta
        collector.end_collection("completed")
        
        # 4. Analisar resultados
        analysis = analyzer.analyze_session(session_id)
        
        # Verificações
        assert analysis['session_id'] == session_id
        assert analysis['file_path'] == "test.py"
        assert analysis['status'] == "completed"
        assert analysis['duration'] > 0
        
        # Verificar métricas
        metrics_summary = analysis['metrics_summary']
        assert 'quality' in metrics_summary
        assert 'time' in metrics_summary
        assert 'cost' in metrics_summary
        assert 'tokens' in metrics_summary
        
        # Verificar análises específicas
        assert analysis['performance_analysis']['total_time'] > 0
        assert analysis['quality_analysis']['overall_quality_score'] == 0.885
        assert analysis['cost_analysis']['total_cost'] == 0.03
    
    def test_multiple_sessions_analysis(self, integrated_system):
        """Testa análise de múltiplas sessões."""
        metrics_system, collector, analyzer = integrated_system
        
        # Criar múltiplas sessões
        session_ids = []
        for index in range(3):
            session_id = collector.start_collection(f"test{index}.py")
            collector.record_quality_metric("completeness", 0.8 + (index * 0.05))
            collector.record_cost_metric("api_cost", 0.02 + (index * 0.01))
            collector.end_collection("completed")
            session_ids.append(session_id)
        
        # Gerar relatório
        report = analyzer.generate_report(session_ids)
        
        assert report['total_sessions'] == 3
        assert len(report['sessions_analysis']) == 3
        assert 'overall_statistics' in report
        assert 'recommendations' in report
        
        # Verificar estatísticas gerais
        overall_stats = report['overall_statistics']
        assert 'quality' in overall_stats
        assert 'cost' in overall_stats
    
    def test_error_handling_robustness(self, integrated_system):
        """Testa robustez no tratamento de erros."""
        metrics_system, collector, analyzer = integrated_system
        
        # Testar com dados inválidos
        session_id = collector.start_collection()
        
        # Adicionar métricas com valores extremos
        collector.record_quality_metric("test", float('inf'))
        collector.record_cost_metric("test", -1.0)
        
        collector.end_collection("completed")
        
        # Análise não deve falhar
        analysis = analyzer.analyze_session(session_id)
        assert isinstance(analysis, dict)
        assert 'metrics_summary' in analysis
    
    def test_performance_with_large_dataset(self, integrated_system):
        """Testa performance com grande volume de dados."""
        metrics_system, collector, analyzer = integrated_system
        
        # Criar muitas sessões rapidamente
        start_time = time.time()
        
        for index in range(100):
            session_id = collector.start_collection(f"test{index}.py")
            collector.record_quality_metric("completeness", 0.8)
            collector.record_cost_metric("api_cost", 0.02)
            collector.end_collection("completed")
        
        creation_time = time.time() - start_time
        
        # Deve ser rápido (< 5 segundos para 100 sessões)
        assert creation_time < 5.0
        
        # Análise de tendências deve ser rápida
        start_time = time.time()
        trends = analyzer.analyze_trends(days=30)
        analysis_time = time.time() - start_time
        
        # Deve ser rápido (< 1 segundo)
        assert analysis_time < 1.0
        assert trends['total_metrics'] >= 100

if __name__ == "__main__":
    pytest.main([__file__]) 