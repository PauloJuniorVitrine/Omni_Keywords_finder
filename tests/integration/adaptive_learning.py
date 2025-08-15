"""
Sistema de Aprendizado Adaptativo
Prompt: Testes de Integração - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T16:00:00Z
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Importações do sistema real
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.cache.redis_cache import RedisCache

class BugSeverity(Enum):
    """Severidade dos bugs detectados."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TestType(Enum):
    """Tipos de teste gerados."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    MUTATION = "mutation"
    SHADOW = "shadow"

@dataclass
class BugReport:
    """Relatório de bug de produção."""
    id: str
    timestamp: datetime
    severity: BugSeverity
    module: str
    error_message: str
    stack_trace: str
    user_impact: str
    reproduction_steps: List[str]
    environment: Dict[str, Any]
    frequency: int = 1
    resolved: bool = False
    test_generated: bool = False

@dataclass
class TestCase:
    """Caso de teste gerado automaticamente."""
    id: str
    bug_id: str
    test_type: TestType
    description: str
    code: str
    expected_result: str
    generated_at: datetime
    executed: bool = False
    passed: bool = False
    execution_time: Optional[float] = None

class AdaptiveLearningSystem:
    """
    Sistema de aprendizado adaptativo que coleta bugs de produção
    e gera testes automaticamente.
    """
    
    def __init__(self):
        """Inicialização do sistema de aprendizado adaptativo."""
        self.logger = StructuredLogger(
            module="adaptive_learning",
            tracing_id="adaptive_001"
        )
        
        self.metrics = MetricsCollector()
        self.cache = RedisCache()
        
        # Configurações do sistema
        self.bug_collection_enabled = True
        self.auto_test_generation_enabled = True
        self.test_reinforcement_enabled = True
        self.feedback_loop_enabled = True
        
        # Armazenamento local (em produção seria banco de dados)
        self.bug_reports: Dict[str, BugReport] = {}
        self.generated_tests: Dict[str, TestCase] = {}
        self.failed_tests: List[str] = []
        
        self.logger.info("Sistema de aprendizado adaptativo inicializado")
    
    async def collect_production_bugs(self, log_file_path: str) -> List[BugReport]:
        """
        Coleta bugs de produção a partir de logs de erro.
        
        Args:
            log_file_path: Caminho para o arquivo de log
            
        Returns:
            Lista de relatórios de bugs coletados
        """
        self.logger.info(f"Iniciando coleta de bugs de produção: {log_file_path}")
        
        try:
            # Simular leitura de logs de produção
            bugs = await self._parse_error_logs(log_file_path)
            
            # Processar e categorizar bugs
            for bug in bugs:
                await self._process_bug_report(bug)
            
            self.logger.info(f"Coleta concluída: {len(bugs)} bugs encontrados")
            return bugs
            
        except Exception as e:
            self.logger.error(f"Erro na coleta de bugs: {str(e)}")
            return []
    
    async def _parse_error_logs(self, log_file_path: str) -> List[BugReport]:
        """Parse de logs de erro para extrair bugs."""
        # Simulação de logs de erro reais
        error_logs = [
            {
                "timestamp": "2025-01-27T10:30:00Z",
                "level": "ERROR",
                "module": "instagram_collector",
                "message": "API rate limit exceeded",
                "stack_trace": "Traceback (most recent call last):\n  File 'collector.py', line 45, in api_request\n    raise RateLimitError('API rate limit exceeded')",
                "user_impact": "Instagram data collection failed",
                "environment": {"api_version": "v1", "rate_limit": "1000/hour"}
            },
            {
                "timestamp": "2025-01-27T11:15:00Z", 
                "level": "ERROR",
                "module": "cache_manager",
                "message": "Redis connection timeout",
                "stack_trace": "Traceback (most recent call last):\n  File 'cache.py', line 23, in get\n    raise ConnectionError('Redis timeout')",
                "user_impact": "Cache operations failed",
                "environment": {"redis_host": "localhost", "timeout": "5s"}
            },
            {
                "timestamp": "2025-01-27T12:00:00Z",
                "level": "ERROR", 
                "module": "circuit_breaker",
                "message": "Circuit breaker opened unexpectedly",
                "stack_trace": "Traceback (most recent call last):\n  File 'circuit.py', line 67, in execute\n    raise CircuitOpenError('Circuit breaker opened')",
                "user_impact": "Service unavailable",
                "environment": {"failure_threshold": 3, "recovery_timeout": 60}
            }
        ]
        
        bugs = []
        for i, log in enumerate(error_logs):
            bug = BugReport(
                id=f"bug_{i+1}_{int(time.time())}",
                timestamp=datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00")),
                severity=self._determine_severity(log["message"]),
                module=log["module"],
                error_message=log["message"],
                stack_trace=log["stack_trace"],
                user_impact=log["user_impact"],
                reproduction_steps=self._generate_reproduction_steps(log),
                environment=log["environment"]
            )
            bugs.append(bug)
        
        return bugs
    
    def _determine_severity(self, error_message: str) -> BugSeverity:
        """Determina a severidade do bug baseado na mensagem de erro."""
        critical_keywords = ["timeout", "connection", "circuit", "rate limit"]
        high_keywords = ["api", "authentication", "authorization"]
        medium_keywords = ["validation", "format", "parsing"]
        
        error_lower = error_message.lower()
        
        if any(keyword in error_lower for keyword in critical_keywords):
            return BugSeverity.CRITICAL
        elif any(keyword in error_lower for keyword in high_keywords):
            return BugSeverity.HIGH
        elif any(keyword in error_lower for keyword in medium_keywords):
            return BugSeverity.MEDIUM
        else:
            return BugSeverity.LOW
    
    def _generate_reproduction_steps(self, log: Dict[str, Any]) -> List[str]:
        """Gera passos de reprodução baseados no log de erro."""
        module = log["module"]
        message = log["message"]
        
        steps = [
            f"1. Acessar módulo {module}",
            f"2. Executar operação que gera erro: {message}",
            f"3. Verificar se erro é reproduzível",
            f"4. Documentar ambiente: {log['environment']}"
        ]
        
        return steps
    
    async def _process_bug_report(self, bug: BugReport):
        """Processa um relatório de bug."""
        # Verificar se bug já existe
        existing_bug = self.bug_reports.get(bug.id)
        if existing_bug:
            existing_bug.frequency += 1
            self.logger.info(f"Bug {bug.id} frequência aumentada para {existing_bug.frequency}")
        else:
            self.bug_reports[bug.id] = bug
            self.logger.info(f"Novo bug registrado: {bug.id} - {bug.severity.value}")
        
        # Gerar teste automaticamente se habilitado
        if self.auto_test_generation_enabled:
            await self._generate_test_for_bug(bug)
    
    async def _generate_test_for_bug(self, bug: BugReport):
        """Gera teste automático para um bug."""
        self.logger.info(f"Gerando teste para bug: {bug.id}")
        
        # Determinar tipo de teste baseado na severidade
        if bug.severity in [BugSeverity.CRITICAL, BugSeverity.HIGH]:
            test_type = TestType.INTEGRATION
        else:
            test_type = TestType.UNIT
        
        # Gerar código de teste
        test_code = self._generate_test_code(bug, test_type)
        
        # Criar caso de teste
        test_case = TestCase(
            id=f"test_{bug.id}_{int(time.time())}",
            bug_id=bug.id,
            test_type=test_type,
            description=f"Teste gerado automaticamente para bug: {bug.error_message}",
            code=test_code,
            expected_result=f"Erro {bug.error_message} deve ser tratado adequadamente",
            generated_at=datetime.now()
        )
        
        self.generated_tests[test_case.id] = test_case
        bug.test_generated = True
        
        self.logger.info(f"Teste gerado: {test_case.id}")
    
    def _generate_test_code(self, bug: BugReport, test_type: TestType) -> str:
        """Gera código de teste baseado no bug."""
        module = bug.module
        error_message = bug.error_message
        
        if test_type == TestType.INTEGRATION:
            return f"""
@pytest.mark.asyncio
async def test_{module}_error_handling_{bug.id}():
    \"\"\"
    Teste de integração para erro: {error_message}
    Bug ID: {bug.id}
    \"\"\"
    # Arrange
    collector = {module.capitalize()}Collector(
        api_key="test_key",
        cache=cache,
        logger=logger,
        circuit_breaker=circuit_breaker,
        rate_limiter=rate_limiter
    )
    
    # Mock do erro específico
    with patch.object(collector, '_make_api_request') as mock_api:
        mock_api.side_effect = Exception("{error_message}")
        
        # Act
        try:
            result = await collector.collect_data("test_user")
        except Exception as e:
            result = None
        
        # Assert
        assert result is None
        # Verificar se erro foi logado adequadamente
        error_logs = logger.get_recent_logs(level="ERROR")
        assert any("{error_message}" in log["message"] for log in error_logs)
"""
        else:
            return f"""
def test_{module}_unit_error_handling_{bug.id}():
    \"\"\"
    Teste unitário para erro: {error_message}
    Bug ID: {bug.id}
    \"\"\"
    # Arrange
    error_handler = ErrorHandler()
    
    # Act
    result = error_handler.handle_error("{error_message}")
    
    # Assert
    assert result is not None
    assert result.error_type == "{error_message}"
"""
    
    async def analyze_error_patterns(self) -> Dict[str, Any]:
        """
        Analisa padrões de erro para identificar tendências.
        
        Returns:
            Dicionário com análise de padrões
        """
        self.logger.info("Iniciando análise de padrões de erro")
        
        if not self.bug_reports:
            return {"message": "Nenhum bug coletado para análise"}
        
        # Análise por severidade
        severity_counts = {}
        for bug in self.bug_reports.values():
            severity = bug.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Análise por módulo
        module_counts = {}
        for bug in self.bug_reports.values():
            module = bug.module
            module_counts[module] = module_counts.get(module, 0) + 1
        
        # Análise temporal
        recent_bugs = [
            bug for bug in self.bug_reports.values()
            if bug.timestamp > datetime.now() - timedelta(days=7)
        ]
        
        analysis = {
            "total_bugs": len(self.bug_reports),
            "recent_bugs": len(recent_bugs),
            "severity_distribution": severity_counts,
            "module_distribution": module_counts,
            "most_frequent_error": self._find_most_frequent_error(),
            "critical_bugs": len([b for b in self.bug_reports.values() if b.severity == BugSeverity.CRITICAL]),
            "tests_generated": len(self.generated_tests),
            "tests_executed": len([t for t in self.generated_tests.values() if t.executed]),
            "tests_passed": len([t for t in self.generated_tests.values() if t.passed])
        }
        
        self.logger.info(f"Análise concluída: {analysis['total_bugs']} bugs analisados")
        return analysis
    
    def _find_most_frequent_error(self) -> str:
        """Encontra o erro mais frequente."""
        error_counts = {}
        for bug in self.bug_reports.values():
            error = bug.error_message
            error_counts[error] = error_counts.get(error, 0) + 1
        
        if error_counts:
            return max(error_counts, key=error_counts.get)
        return "Nenhum erro encontrado"
    
    async def reinforce_failed_tests(self) -> List[str]:
        """
        Reforça testes que falharam anteriormente.
        
        Returns:
            Lista de IDs de testes reforçados
        """
        self.logger.info("Iniciando reforço de testes falhados")
        
        reinforced_tests = []
        
        for test_id in self.failed_tests:
            if test_id in self.generated_tests:
                test = self.generated_tests[test_id]
                
                # Gerar teste reforçado
                reinforced_code = self._generate_reinforced_test(test)
                
                # Criar novo teste reforçado
                reinforced_test = TestCase(
                    id=f"reinforced_{test_id}_{int(time.time())}",
                    bug_id=test.bug_id,
                    test_type=test.test_type,
                    description=f"Teste reforçado para: {test.description}",
                    code=reinforced_code,
                    expected_result=test.expected_result,
                    generated_at=datetime.now()
                )
                
                self.generated_tests[reinforced_test.id] = reinforced_test
                reinforced_tests.append(reinforced_test.id)
                
                self.logger.info(f"Teste reforçado gerado: {reinforced_test.id}")
        
        return reinforced_tests
    
    def _generate_reinforced_test(self, original_test: TestCase) -> str:
        """Gera teste reforçado baseado no teste original que falhou."""
        # Adicionar mais validações e cenários de edge case
        reinforced_code = original_test.code.replace(
            "# Assert",
            """# Assert - Validações reforçadas
        assert result is None
        
        # Validações adicionais para teste reforçado
        error_logs = logger.get_recent_logs(level="ERROR")
        assert len(error_logs) > 0
        
        # Verificar se erro foi categorizado corretamente
        assert any("ERROR" in log["level"] for log in error_logs)
        
        # Verificar se métricas foram atualizadas
        metrics = metrics_collector.get_metrics("error_handling")
        assert metrics["total_errors"] > 0
        
        # Verificar se circuit breaker foi ativado se aplicável
        if hasattr(collector, 'circuit_breaker'):
            circuit_status = collector.circuit_breaker.get_status()
            assert circuit_status["failure_count"] > 0"""
        )
        
        return reinforced_code
    
    async def create_feedback_loop(self) -> Dict[str, Any]:
        """
        Cria loop de feedback para melhorar geração de testes.
        
        Returns:
            Dicionário com métricas do feedback loop
        """
        self.logger.info("Iniciando feedback loop")
        
        # Analisar performance dos testes gerados
        executed_tests = [t for t in self.generated_tests.values() if t.executed]
        passed_tests = [t for t in executed_tests if t.passed]
        failed_tests = [t for t in executed_tests if not t.passed]
        
        # Calcular métricas
        total_executed = len(executed_tests)
        success_rate = len(passed_tests) / total_executed if total_executed > 0 else 0
        
        # Identificar padrões de falha
        failure_patterns = self._analyze_failure_patterns(failed_tests)
        
        # Ajustar estratégia de geração
        adjustments = self._adjust_generation_strategy(success_rate, failure_patterns)
        
        feedback_metrics = {
            "total_executed": total_executed,
            "success_rate": success_rate,
            "failure_patterns": failure_patterns,
            "adjustments_made": adjustments,
            "recommendations": self._generate_recommendations(success_rate)
        }
        
        self.logger.info(f"Feedback loop concluído: {success_rate:.2%} taxa de sucesso")
        return feedback_metrics
    
    def _analyze_failure_patterns(self, failed_tests: List[TestCase]) -> Dict[str, Any]:
        """Analisa padrões de falha nos testes."""
        patterns = {
            "module_failures": {},
            "error_type_failures": {},
            "test_type_failures": {}
        }
        
        for test in failed_tests:
            # Análise por módulo
            bug = self.bug_reports.get(test.bug_id)
            if bug:
                module = bug.module
                patterns["module_failures"][module] = patterns["module_failures"].get(module, 0) + 1
            
            # Análise por tipo de teste
            test_type = test.test_type.value
            patterns["test_type_failures"][test_type] = patterns["test_type_failures"].get(test_type, 0) + 1
        
        return patterns
    
    def _adjust_generation_strategy(self, success_rate: float, failure_patterns: Dict[str, Any]) -> List[str]:
        """Ajusta estratégia de geração baseado no feedback."""
        adjustments = []
        
        if success_rate < 0.7:
            adjustments.append("Aumentar validações nos testes gerados")
            adjustments.append("Incluir mais cenários de edge case")
        
        if failure_patterns.get("test_type_failures", {}).get("unit", 0) > 0:
            adjustments.append("Melhorar geração de testes unitários")
        
        if failure_patterns.get("module_failures", {}).get("instagram_collector", 0) > 0:
            adjustments.append("Reforçar testes para Instagram collector")
        
        return adjustments
    
    def _generate_recommendations(self, success_rate: float) -> List[str]:
        """Gera recomendações baseadas na taxa de sucesso."""
        recommendations = []
        
        if success_rate < 0.5:
            recommendations.append("Revisar critérios de geração de testes")
            recommendations.append("Implementar validação manual antes da execução")
        elif success_rate < 0.8:
            recommendations.append("Ajustar parâmetros de geração")
            recommendations.append("Adicionar mais contexto aos testes")
        else:
            recommendations.append("Sistema funcionando bem - manter configuração atual")
        
        return recommendations
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Retorna status completo do sistema de aprendizado adaptativo.
        
        Returns:
            Dicionário com status do sistema
        """
        return {
            "system_enabled": True,
            "bug_collection_enabled": self.bug_collection_enabled,
            "auto_test_generation_enabled": self.auto_test_generation_enabled,
            "test_reinforcement_enabled": self.test_reinforcement_enabled,
            "feedback_loop_enabled": self.feedback_loop_enabled,
            "total_bugs_collected": len(self.bug_reports),
            "total_tests_generated": len(self.generated_tests),
            "total_tests_executed": len([t for t in self.generated_tests.values() if t.executed]),
            "total_tests_passed": len([t for t in self.generated_tests.values() if t.passed]),
            "failed_tests_count": len(self.failed_tests),
            "last_analysis": datetime.now().isoformat(),
            "system_health": "healthy"
        } 