from typing import Dict, List, Optional, Any
"""
Testes Unitários para LogAnalyzer

Tracing ID: TEST_LOG_ANALYZER_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação Inicial

Responsável: Sistema de Documentação Enterprise
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, timedelta
from shared.log_analyzer import (
    LogAnalyzer,
    LogEntry,
    LogSeverity,
    FailureType,
    FailurePattern,
    PerformanceIssue,
    ImprovementSuggestion
)


class TestLogAnalyzer:
    """Testes para LogAnalyzer"""
    
    def setup_method(self):
        """Configuração inicial para cada teste"""
        self.analyzer = LogAnalyzer()
        
        # Logs de exemplo para testes
        self.sample_logs = [
            "2025-01-27 10:00:00 ERROR [shared.trigger_config_validator] validate_sensitive_files:15: File not found: config/secrets.json tracing_id=TRACE_001",
            "2025-01-27 10:01:00 ERROR [shared.trigger_config_validator] validate_sensitive_files:15: File not found: config/secrets.json tracing_id=TRACE_002",
            "2025-01-27 10:02:00 ERROR [infrastructure.ml.semantic_embeddings] generate_embedding:45: Timeout after 30s tracing_id=TRACE_003",
            "2025-01-27 10:03:00 INFO [shared.trigger_config_validator] validate_patterns:30: Validation completed duration=1500 memory=50 cpu=25",
            "2025-01-27 10:04:00 INFO [shared.trigger_config_validator] validate_patterns:30: Validation completed duration=1800 memory=55 cpu=30",
            "2025-01-27 10:05:00 ERROR [shared.trigger_config_validator] validate_semantic_threshold:60: Invalid threshold value: 1.5 tracing_id=TRACE_004",
            "2025-01-27 10:06:00 WARNING [infrastructure.ml.semantic_embeddings] calculate_similarity:80: High memory usage: 200MB",
            "2025-01-27 10:07:00 ERROR [database.connection] execute_query:25: Database connection timeout tracing_id=TRACE_005",
            "2025-01-27 10:08:00 ERROR [security.auth] validate_token:15: Unauthorized access attempt tracing_id=TRACE_006"
        ]
    
    def test_init(self):
        """Teste de inicialização do analisador"""
        analyzer = LogAnalyzer()
        
        assert analyzer.logs_directory == Path("logs")
        assert analyzer.log_entries == []
        assert analyzer.failure_patterns == []
        assert analyzer.performance_issues == []
        assert analyzer.improvement_suggestions == []
    
    def test_init_with_custom_directory(self):
        """Teste de inicialização com diretório customizado"""
        analyzer = LogAnalyzer("/custom/logs")
        
        assert analyzer.logs_directory == Path("/custom/logs")
    
    def test_parse_log_line_valid(self):
        """Teste de parse de linha de log válida"""
        log_line = "2025-01-27 10:00:00 ERROR [shared.trigger_config_validator] validate_sensitive_files:15: File not found tracing_id=TRACE_001"
        
        entry = self.analyzer._parse_log_line(log_line)
        
        assert entry is not None
        assert entry.timestamp == datetime(2025, 1, 27, 10, 0, 0)
        assert entry.severity == LogSeverity.ERROR
        assert "File not found" in entry.message
        assert entry.module == "shared.trigger_config_validator"
        assert entry.function == "validate_sensitive_files"
        assert entry.line == 15
        assert entry.tracing_id == "TRACE_001"
    
    def test_parse_log_line_invalid_timestamp(self):
        """Teste de parse de linha com timestamp inválido"""
        log_line = "invalid-timestamp ERROR [module] function:10: message"
        
        entry = self.analyzer._parse_log_line(log_line)
        
        assert entry is None
    
    def test_parse_log_line_empty(self):
        """Teste de parse de linha vazia"""
        entry = self.analyzer._parse_log_line("")
        
        assert entry is None
    
    def test_parse_log_line_with_metrics(self):
        """Teste de parse de linha com métricas"""
        log_line = "2025-01-27 10:00:00 INFO [module] function:10: Operation completed duration=1500 memory=50 cpu=25"
        
        entry = self.analyzer._parse_log_line(log_line)
        
        assert entry is not None
        assert entry.metrics is not None
        assert entry.metrics['duration'] == 1500.0
        assert entry.metrics['memory'] == 50.0
        assert entry.metrics['cpu'] == 25.0
    
    def test_classify_failure_null_pointer(self):
        """Teste de classificação de falha NullPointer"""
        message = "Cannot access attribute 'value' of None"
        failure_type = self.analyzer._classify_failure(message)
        
        assert failure_type == FailureType.NULL_POINTER
    
    def test_classify_failure_timeout(self):
        """Teste de classificação de falha Timeout"""
        message = "Operation timed out after 30 seconds"
        failure_type = self.analyzer._classify_failure(message)
        
        assert failure_type == FailureType.TIMEOUT
    
    def test_classify_failure_validation(self):
        """Teste de classificação de falha Validation"""
        message = "Invalid input validation failed"
        failure_type = self.analyzer._classify_failure(message)
        
        assert failure_type == FailureType.VALIDATION_ERROR
    
    def test_classify_failure_security(self):
        """Teste de classificação de falha Security"""
        message = "Unauthorized access attempt detected"
        failure_type = self.analyzer._classify_failure(message)
        
        assert failure_type == FailureType.SECURITY_ERROR
    
    def test_classify_failure_unknown(self):
        """Teste de classificação de falha desconhecida"""
        message = "Some random error message"
        failure_type = self.analyzer._classify_failure(message)
        
        assert failure_type == FailureType.UNKNOWN
    
    def test_analyze_failures_no_errors(self):
        """Teste de análise de falhas sem erros"""
        # Adicionar apenas logs INFO
        self.analyzer.log_entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py"
            )
        ]
        
        patterns = self.analyzer.analyze_failures()
        
        assert patterns == []
    
    def test_analyze_failures_single_error(self):
        """Teste de análise de falhas com erro único"""
        # Adicionar apenas um erro
        self.analyzer.log_entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.ERROR,
                message="File not found",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py"
            )
        ]
        
        patterns = self.analyzer.analyze_failures()
        
        # Deve retornar vazio pois precisa de pelo menos 2 ocorrências
        assert patterns == []
    
    def test_analyze_failures_multiple_errors(self):
        """Teste de análise de falhas com múltiplos erros"""
        # Adicionar múltiplos erros do mesmo tipo
        self.analyzer.log_entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.ERROR,
                message="File not found: config/secrets.json",
                module="shared.trigger_config_validator",
                function="validate_sensitive_files",
                line=15,
                file_path="shared/trigger_config_validator.py"
            ),
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.ERROR,
                message="File not found: config/secrets.json",
                module="shared.trigger_config_validator",
                function="validate_sensitive_files",
                line=15,
                file_path="shared/trigger_config_validator.py"
            )
        ]
        
        patterns = self.analyzer.analyze_failures()
        
        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern.failure_type == FailureType.VALIDATION_ERROR
        assert pattern.frequency == 2
        assert "shared.trigger_config_validator" in pattern.affected_modules
        assert "validate_sensitive_files" in pattern.affected_functions
    
    def test_analyze_failure_pattern(self):
        """Teste de análise de padrão de falha específico"""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.ERROR,
                message="Timeout after 30s",
                module="infrastructure.ml.semantic_embeddings",
                function="generate_embedding",
                line=45,
                file_path="infrastructure/ml/semantic_embeddings.py"
            ),
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.ERROR,
                message="Timeout after 30s",
                module="infrastructure.ml.semantic_embeddings",
                function="generate_embedding",
                line=45,
                file_path="infrastructure/ml/semantic_embeddings.py"
            )
        ]
        
        pattern = self.analyzer._analyze_failure_pattern(FailureType.TIMEOUT, entries)
        
        assert pattern is not None
        assert pattern.failure_type == FailureType.TIMEOUT
        assert pattern.frequency == 2
        assert "infrastructure.ml.semantic_embeddings" in pattern.affected_modules
        assert "generate_embedding" in pattern.affected_functions
        assert "Timeout after 30s" in pattern.common_message
        assert len(pattern.suggestions) > 0
        assert pattern.priority_score > 0
    
    def test_generate_failure_suggestions(self):
        """Teste de geração de sugestões para falhas"""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.ERROR,
                message="Cannot access attribute of None",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py"
            )
        ]
        
        suggestions = self.analyzer._generate_failure_suggestions(FailureType.NULL_POINTER, entries)
        
        assert len(suggestions) > 0
        assert any("validação defensiva" in suggestion.lower() for suggestion in suggestions)
    
    def test_calculate_failure_priority(self):
        """Teste de cálculo de prioridade de falha"""
        frequency = 10
        failure_type = FailureType.SECURITY_ERROR
        affected_modules = ["security.auth", "security.validator"]
        
        priority = self.analyzer._calculate_failure_priority(frequency, failure_type, affected_modules)
        
        assert 0.0 <= priority <= 1.0
        assert priority > 0.5  # Security errors devem ter alta prioridade
    
    def test_analyze_performance_issues_no_metrics(self):
        """Teste de análise de performance sem métricas"""
        # Adicionar logs sem métricas
        self.analyzer.log_entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py"
            )
        ]
        
        issues = self.analyzer.analyze_performance_issues()
        
        assert issues == []
    
    def test_analyze_performance_issues_fast_operation(self):
        """Teste de análise de performance com operação rápida"""
        # Adicionar logs com métricas de operação rápida
        self.analyzer.log_entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py",
                metrics={"duration": 500}  # < 1000ms
            )
        ]
        
        issues = self.analyzer.analyze_performance_issues()
        
        assert issues == []
    
    def test_analyze_performance_issues_slow_operation(self):
        """Teste de análise de performance com operação lenta"""
        # Adicionar logs com métricas de operação lenta
        self.analyzer.log_entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py",
                metrics={"duration": 2000}  # > 1000ms
            ),
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py",
                metrics={"duration": 2500}
            ),
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py",
                metrics={"duration": 3000}
            )
        ]
        
        issues = self.analyzer.analyze_performance_issues()
        
        assert len(issues) == 1
        issue = issues[0]
        assert issue.operation == "test.test_func"
        assert issue.avg_duration > 2000
        assert issue.frequency == 3
        assert len(issue.suggestions) > 0
        assert issue.priority_score > 0
    
    def test_analyze_performance_operation(self):
        """Teste de análise de operação de performance específica"""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py",
                metrics={"duration": 2000, "memory": 150, "cpu": 85}
            ),
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py",
                metrics={"duration": 2500, "memory": 160, "cpu": 90}
            )
        ]
        
        issue = self.analyzer._analyze_performance_operation("test.test_func", entries)
        
        assert issue is not None
        assert issue.operation == "test.test_func"
        assert issue.avg_duration > 2000
        assert issue.max_duration > 2000
        assert issue.frequency == 2
        assert "test" in issue.affected_modules
        assert len(issue.bottleneck_factors) > 0
        assert len(issue.suggestions) > 0
        assert issue.priority_score > 0
    
    def test_identify_bottleneck_factors(self):
        """Teste de identificação de fatores de bottleneck"""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.INFO,
                message="Operation completed",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py",
                metrics={"duration": 2000, "memory": 150, "cpu": 85}
            )
        ]
        
        factors = self.analyzer._identify_bottleneck_factors(entries)
        
        assert "Alto uso de memória" in factors
        assert "Alto uso de CPU" in factors
    
    def test_generate_performance_suggestions(self):
        """Teste de geração de sugestões de performance"""
        avg_duration = 3000
        max_duration = 12000
        bottleneck_factors = ["Alto uso de memória", "Alto uso de CPU"]
        
        suggestions = self.analyzer._generate_performance_suggestions(avg_duration, max_duration, bottleneck_factors)
        
        assert len(suggestions) > 0
        assert any("cache" in suggestion.lower() for suggestion in suggestions)
        assert any("timeout" in suggestion.lower() for suggestion in suggestions)
    
    def test_calculate_performance_priority(self):
        """Teste de cálculo de prioridade de performance"""
        avg_duration = 3000
        max_duration = 12000
        frequency = 20
        
        priority = self.analyzer._calculate_performance_priority(avg_duration, max_duration, frequency)
        
        assert 0.0 <= priority <= 1.0
        assert priority > 0.5  # Operação lenta deve ter alta prioridade
    
    def test_extract_suggestions(self):
        """Teste de extração de sugestões"""
        # Configurar padrões de falha e problemas de performance
        self.analyzer.failure_patterns = [
            FailurePattern(
                failure_type=FailureType.VALIDATION_ERROR,
                frequency=5,
                affected_modules=["shared.trigger_config_validator"],
                affected_functions=["validate_sensitive_files"],
                common_message="File not found",
                avg_timestamp=datetime.now(),
                severity_distribution={LogSeverity.ERROR: 5},
                suggestions=["Implementar validação defensiva"],
                priority_score=0.8
            )
        ]
        
        self.analyzer.performance_issues = [
            PerformanceIssue(
                operation="test.test_func",
                avg_duration=2500,
                max_duration=5000,
                frequency=10,
                affected_modules=["test"],
                bottleneck_factors=["Alto uso de memória"],
                suggestions=["Implementar cache"],
                priority_score=0.7
            )
        ]
        
        suggestions = self.analyzer.extract_suggestions()
        
        assert len(suggestions) == 2
        assert all(isinstance(string_data, ImprovementSuggestion) for string_data in suggestions)
        assert suggestions[0].priority_score > suggestions[1].priority_score  # Ordenadas por prioridade
    
    def test_create_failure_suggestion(self):
        """Teste de criação de sugestão baseada em falha"""
        pattern = FailurePattern(
            failure_type=FailureType.SECURITY_ERROR,
            frequency=10,
            affected_modules=["security.auth"],
            affected_functions=["validate_token"],
            common_message="Unauthorized access",
            avg_timestamp=datetime.now(),
            severity_distribution={LogSeverity.ERROR: 10},
            suggestions=["Implementar autenticação robusta"],
            priority_score=0.9
        )
        
        suggestion = self.analyzer._create_failure_suggestion(pattern)
        
        assert isinstance(suggestion, ImprovementSuggestion)
        assert "SECURITY_ERROR" in suggestion.title
        assert suggestion.impact_level == "ALTO"
        assert suggestion.urgency_level == "ALTA"
        assert suggestion.priority_score == 0.9
        assert len(suggestion.evidence) > 0
        assert len(suggestion.implementation_steps) > 0
    
    def test_create_performance_suggestion(self):
        """Teste de criação de sugestão baseada em performance"""
        issue = PerformanceIssue(
            operation="test.test_func",
            avg_duration=3000,
            max_duration=8000,
            frequency=15,
            affected_modules=["test"],
            bottleneck_factors=["Alto uso de memória"],
            suggestions=["Implementar cache"],
            priority_score=0.8
        )
        
        suggestion = self.analyzer._create_performance_suggestion(issue)
        
        assert isinstance(suggestion, ImprovementSuggestion)
        assert "test.test_func" in suggestion.title
        assert suggestion.impact_level == "ALTO"
        assert suggestion.effort_level == "MÉDIO"
        assert suggestion.priority_score == 0.8
        assert len(suggestion.evidence) > 0
        assert len(suggestion.implementation_steps) > 0
    
    def test_prioritize_improvements(self):
        """Teste de priorização de melhorias"""
        # Configurar sugestões de teste
        self.analyzer.improvement_suggestions = [
            ImprovementSuggestion(
                title="Sugestão 1",
                description="Descrição 1",
                affected_files=["file1.py"],
                affected_functions=["func1"],
                impact_level="ALTO",
                effort_level="BAIXO",
                urgency_level="ALTA",
                roi_score=0.8,
                priority_score=0.7,
                evidence=["Evidência 1"],
                implementation_steps=["Passo 1"]
            ),
            ImprovementSuggestion(
                title="Sugestão 2",
                description="Descrição 2",
                affected_files=["file2.py"],
                affected_functions=["func2"],
                impact_level="MÉDIO",
                effort_level="ALTO",
                urgency_level="BAIXA",
                roi_score=0.5,
                priority_score=0.6,
                evidence=["Evidência 2"],
                implementation_steps=["Passo 2"]
            )
        ]
        
        prioritized = self.analyzer.prioritize_improvements()
        
        assert len(prioritized) == 2
        assert prioritized[0].priority_score >= prioritized[1].priority_score  # Ordenadas por prioridade
    
    def test_calculate_final_priority_score(self):
        """Teste de cálculo de score final de priorização"""
        suggestion = ImprovementSuggestion(
            title="Test Suggestion",
            description="Test Description",
            affected_files=["test.py"],
            affected_functions=["test_func"],
            impact_level="ALTO",
            effort_level="BAIXO",
            urgency_level="ALTA",
            roi_score=0.8,
            priority_score=0.7,
            evidence=["Evidence"],
            implementation_steps=["Step"]
        )
        
        final_score = self.analyzer._calculate_final_priority_score(suggestion)
        
        assert 0.0 <= final_score <= 1.0
        assert final_score > 0.5  # Alta prioridade deve ter score alto
    
    def test_generate_report(self):
        """Teste de geração de relatório"""
        # Configurar dados de teste
        self.analyzer.log_entries = [
            LogEntry(
                timestamp=datetime.now(),
                severity=LogSeverity.ERROR,
                message="Test error",
                module="test",
                function="test_func",
                line=10,
                file_path="test.py"
            )
        ]
        
        self.analyzer.failure_patterns = [
            FailurePattern(
                failure_type=FailureType.VALIDATION_ERROR,
                frequency=5,
                affected_modules=["test"],
                affected_functions=["test_func"],
                common_message="Test error",
                avg_timestamp=datetime.now(),
                severity_distribution={LogSeverity.ERROR: 5},
                suggestions=["Test suggestion"],
                priority_score=0.8
            )
        ]
        
        self.analyzer.improvement_suggestions = [
            ImprovementSuggestion(
                title="Test Suggestion",
                description="Test Description",
                affected_files=["test.py"],
                affected_functions=["test_func"],
                impact_level="ALTO",
                effort_level="BAIXO",
                urgency_level="ALTA",
                roi_score=0.8,
                priority_score=0.8,
                evidence=["Evidence"],
                implementation_steps=["Step"]
            )
        ]
        
        report = self.analyzer.generate_report()
        
        assert "RELATÓRIO DE ANÁLISE DE LOGS" in report
        assert "RESUMO EXECUTIVO" in report
        assert "TOP 5 SUGESTÕES PRIORITÁRIAS" in report
        assert "Test Suggestion" in report
    
    def test_save_report(self):
        """Teste de salvamento de relatório"""
        # Configurar dados de teste
        self.analyzer.improvement_suggestions = [
            ImprovementSuggestion(
                title="Test Suggestion",
                description="Test Description",
                affected_files=["test.py"],
                affected_functions=["test_func"],
                impact_level="ALTO",
                effort_level="BAIXO",
                urgency_level="ALTA",
                roi_score=0.8,
                priority_score=0.8,
                evidence=["Evidence"],
                implementation_steps=["Step"]
            )
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_report.md")
            
            self.analyzer.save_report(output_path)
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "RELATÓRIO DE ANÁLISE DE LOGS" in content
    
    @patch('pathlib.Path.exists', return_value=False)
    def test_load_logs_directory_not_found(self, mock_exists):
        """Teste de carregamento de logs com diretório não encontrado"""
        entries_loaded = self.analyzer.load_logs()
        
        assert entries_loaded == 0
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.rglob', return_value=[])
    def test_load_logs_no_files(self, mock_rglob, mock_exists):
        """Teste de carregamento de logs sem arquivos"""
        entries_loaded = self.analyzer.load_logs()
        
        assert entries_loaded == 0


class TestLogEntry:
    """Testes para LogEntry"""
    
    def test_log_entry_creation(self):
        """Teste de criação de LogEntry"""
        entry = LogEntry(
            timestamp=datetime.now(),
            severity=LogSeverity.ERROR,
            message="Test message",
            module="test_module",
            function="test_function",
            line=10,
            file_path="test.py",
            tracing_id="TRACE_001",
            session_id="SESSION_001",
            user_id="USER_001",
            metrics={"duration": 1000}
        )
        
        assert entry.timestamp is not None
        assert entry.severity == LogSeverity.ERROR
        assert entry.message == "Test message"
        assert entry.module == "test_module"
        assert entry.function == "test_function"
        assert entry.line == 10
        assert entry.file_path == "test.py"
        assert entry.tracing_id == "TRACE_001"
        assert entry.session_id == "SESSION_001"
        assert entry.user_id == "USER_001"
        assert entry.metrics == {"duration": 1000}


class TestFailurePattern:
    """Testes para FailurePattern"""
    
    def test_failure_pattern_creation(self):
        """Teste de criação de FailurePattern"""
        pattern = FailurePattern(
            failure_type=FailureType.VALIDATION_ERROR,
            frequency=5,
            affected_modules=["test_module"],
            affected_functions=["test_function"],
            common_message="Test error",
            avg_timestamp=datetime.now(),
            severity_distribution={LogSeverity.ERROR: 5},
            suggestions=["Test suggestion"],
            priority_score=0.8
        )
        
        assert pattern.failure_type == FailureType.VALIDATION_ERROR
        assert pattern.frequency == 5
        assert pattern.affected_modules == ["test_module"]
        assert pattern.affected_functions == ["test_function"]
        assert pattern.common_message == "Test error"
        assert pattern.suggestions == ["Test suggestion"]
        assert pattern.priority_score == 0.8


class TestPerformanceIssue:
    """Testes para PerformanceIssue"""
    
    def test_performance_issue_creation(self):
        """Teste de criação de PerformanceIssue"""
        issue = PerformanceIssue(
            operation="test.test_func",
            avg_duration=2000,
            max_duration=5000,
            frequency=10,
            affected_modules=["test"],
            bottleneck_factors=["High memory usage"],
            suggestions=["Implement cache"],
            priority_score=0.7
        )
        
        assert issue.operation == "test.test_func"
        assert issue.avg_duration == 2000
        assert issue.max_duration == 5000
        assert issue.frequency == 10
        assert issue.affected_modules == ["test"]
        assert issue.bottleneck_factors == ["High memory usage"]
        assert issue.suggestions == ["Implement cache"]
        assert issue.priority_score == 0.7


class TestImprovementSuggestion:
    """Testes para ImprovementSuggestion"""
    
    def test_improvement_suggestion_creation(self):
        """Teste de criação de ImprovementSuggestion"""
        suggestion = ImprovementSuggestion(
            title="Test Suggestion",
            description="Test Description",
            affected_files=["test.py"],
            affected_functions=["test_func"],
            impact_level="ALTO",
            effort_level="BAIXO",
            urgency_level="ALTA",
            roi_score=0.8,
            priority_score=0.8,
            evidence=["Evidence"],
            implementation_steps=["Step"]
        )
        
        assert suggestion.title == "Test Suggestion"
        assert suggestion.description == "Test Description"
        assert suggestion.affected_files == ["test.py"]
        assert suggestion.affected_functions == ["test_func"]
        assert suggestion.impact_level == "ALTO"
        assert suggestion.effort_level == "BAIXO"
        assert suggestion.urgency_level == "ALTA"
        assert suggestion.roi_score == 0.8
        assert suggestion.priority_score == 0.8
        assert suggestion.evidence == ["Evidence"]
        assert suggestion.implementation_steps == ["Step"]


if __name__ == "__main__":
    pytest.main([__file__]) 