"""
Log Analyzer - Analisador de Logs para Sugestões de Melhoria

Tracing ID: LOG_ANALYZER_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação Inicial

Responsável: Sistema de Documentação Enterprise
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogSeverity(Enum):
    """Severidade do log"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class FailureType(Enum):
    """Tipos de falha"""
    NULL_POINTER = "NullPointerException"
    TIMEOUT = "TimeoutException"
    MEMORY_LEAK = "MemoryLeak"
    VALIDATION_ERROR = "ValidationError"
    PERMISSION_ERROR = "PermissionError"
    NETWORK_ERROR = "NetworkError"
    DATABASE_ERROR = "DatabaseError"
    SECURITY_ERROR = "SecurityError"
    PERFORMANCE_ISSUE = "PerformanceIssue"
    UNKNOWN = "Unknown"


@dataclass
class LogEntry:
    """Entrada de log"""
    timestamp: datetime
    severity: LogSeverity
    message: str
    module: str
    function: str
    line: int
    file_path: str
    tracing_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    stack_trace: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None


@dataclass
class FailurePattern:
    """Padrão de falha identificado"""
    failure_type: FailureType
    frequency: int
    affected_modules: List[str]
    affected_functions: List[str]
    common_message: str
    avg_timestamp: datetime
    severity_distribution: Dict[LogSeverity, int]
    suggestions: List[str]
    priority_score: float


@dataclass
class PerformanceIssue:
    """Problema de performance identificado"""
    operation: str
    avg_duration: float
    max_duration: float
    frequency: int
    affected_modules: List[str]
    bottleneck_factors: List[str]
    suggestions: List[str]
    priority_score: float


@dataclass
class SecurityIssue:
    """Problema de segurança identificado"""
    vulnerability_type: str
    cvss_score: float
    frequency: int
    affected_modules: List[str]
    attack_vector: str
    risk_level: str
    suggestions: List[str]
    priority_score: float


@dataclass
class ImprovementSuggestion:
    """Sugestão de melhoria baseada em logs"""
    title: str
    description: str
    affected_files: List[str]
    affected_functions: List[str]
    impact_level: str
    effort_level: str
    urgency_level: str
    roi_score: float
    priority_score: float
    evidence: List[str]
    implementation_steps: List[str]


class LogAnalyzer:
    """
    Analisador de logs para extrair sugestões de melhoria
    
    Responsabilidades:
    - Analisar logs de falhas
    - Identificar padrões de problemas
    - Extrair sugestões de melhoria
    - Priorizar melhorias baseadas em dados reais
    """
    
    def __init__(self, logs_directory: str = "logs"):
        """
        Inicializa o analisador
        
        Args:
            logs_directory: Diretório contendo os logs
        """
        self.logs_directory = Path(logs_directory)
        self.log_entries: List[LogEntry] = []
        self.failure_patterns: List[FailurePattern] = []
        self.performance_issues: List[PerformanceIssue] = []
        self.security_issues: List[SecurityIssue] = []
        self.improvement_suggestions: List[ImprovementSuggestion] = []
        
        # Padrões de regex para análise
        self.patterns = {
            'timestamp': r'(\data{4}-\data{2}-\data{2} \data{2}:\data{2}:\data{2})',
            'severity': r'(ERROR|WARNING|INFO|DEBUG)',
            'module': r'\[([^\]]+)\]',
            'function': r'([a-zA-Z_][a-zA-Z0-9_]*)\(',
            'line': r':(\data+):',
            'file_path': r'([a-zA-Z0-9_/\\]+\.py)',
            'tracing_id': r'tracing_id=([a-zA-Z0-9_-]+)',
            'session_id': r'session_id=([a-zA-Z0-9_-]+)',
            'user_id': r'user_id=([a-zA-Z0-9_-]+)',
            'duration': r'duration=(\data+(?:\.\data+)?)',
            'memory': r'memory=(\data+(?:\.\data+)?)',
            'cpu': r'cpu=(\data+(?:\.\data+)?)',
        }
    
    def load_logs(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> int:
        """
        Carrega logs do diretório especificado
        
        Args:
            start_date: Data de início para filtro
            end_date: Data de fim para filtro
            
        Returns:
            Número de entradas de log carregadas
        """
        if not self.logs_directory.exists():
            logger.warning(f"Diretório de logs não encontrado: {self.logs_directory}")
            return 0
        
        log_files = list(self.logs_directory.rglob("*.log"))
        total_entries = 0
        
        for log_file in log_files:
            try:
                entries = self._parse_log_file(log_file, start_date, end_date)
                self.log_entries.extend(entries)
                total_entries += len(entries)
                logger.info(f"Carregados {len(entries)} entradas de {log_file}")
            except Exception as e:
                logger.error(f"Erro ao carregar {log_file}: {e}")
        
        logger.info(f"Total de entradas carregadas: {total_entries}")
        return total_entries
    
    def _parse_log_file(self, log_file: Path, start_date: Optional[datetime], end_date: Optional[datetime]) -> List[LogEntry]:
        """Parse de um arquivo de log específico"""
        entries = []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = self._parse_log_line(line.strip())
                    if entry:
                        # Aplicar filtros de data
                        if start_date and entry.timestamp < start_date:
                            continue
                        if end_date and entry.timestamp > end_date:
                            continue
                        entries.append(entry)
                except Exception as e:
                    logger.warning(f"Erro ao parsear linha {line_num} em {log_file}: {e}")
        
        return entries
    
    def _parse_log_line(self, line: str) -> Optional[LogEntry]:
        """Parse de uma linha de log"""
        if not line:
            return None
        
        # Extrair timestamp
        timestamp_match = re.search(self.patterns['timestamp'], line)
        if not timestamp_match:
            return None
        
        try:
            timestamp = datetime.strptime(timestamp_match.group(1), "%Y-%m-%data %H:%M:%S")
        except ValueError:
            return None
        
        # Extrair severidade
        severity_match = re.search(self.patterns['severity'], line)
        severity = LogSeverity(severity_match.group(1)) if severity_match else LogSeverity.INFO
        
        # Extrair módulo
        module_match = re.search(self.patterns['module'], line)
        module = module_match.group(1) if module_match else "unknown"
        
        # Extrair função
        function_match = re.search(self.patterns['function'], line)
        function = function_match.group(1) if function_match else "unknown"
        
        # Extrair linha
        line_match = re.search(self.patterns['line'], line)
        line_number = int(line_match.group(1)) if line_match else 0
        
        # Extrair caminho do arquivo
        file_match = re.search(self.patterns['file_path'], line)
        file_path = file_match.group(1) if file_match else "unknown"
        
        # Extrair IDs
        tracing_match = re.search(self.patterns['tracing_id'], line)
        tracing_id = tracing_match.group(1) if tracing_match else None
        
        session_match = re.search(self.patterns['session_id'], line)
        session_id = session_match.group(1) if session_match else None
        
        user_match = re.search(self.patterns['user_id'], line)
        user_id = user_match.group(1) if user_match else None
        
        # Extrair métricas
        metrics = {}
        duration_match = re.search(self.patterns['duration'], line)
        if duration_match:
            metrics['duration'] = float(duration_match.group(1))
        
        memory_match = re.search(self.patterns['memory'], line)
        if memory_match:
            metrics['memory'] = float(memory_match.group(1))
        
        cpu_match = re.search(self.patterns['cpu'], line)
        if cpu_match:
            metrics['cpu'] = float(cpu_match.group(1))
        
        # Extrair mensagem (tudo após o padrão de timestamp)
        message = line[line.find(timestamp_match.group(1)) + len(timestamp_match.group(1)):].strip()
        message = re.sub(r'\[[^\]]*\]', '', message).strip()  # Remover colchetes
        
        return LogEntry(
            timestamp=timestamp,
            severity=severity,
            message=message,
            module=module,
            function=function,
            line=line_number,
            file_path=file_path,
            tracing_id=tracing_id,
            session_id=session_id,
            user_id=user_id,
            metrics=metrics if metrics else None
        )
    
    def analyze_failures(self) -> List[FailurePattern]:
        """
        Analisa padrões de falha nos logs
        
        Returns:
            Lista de padrões de falha identificados
        """
        error_entries = [entry for entry in self.log_entries if entry.severity == LogSeverity.ERROR]
        
        if not error_entries:
            logger.info("Nenhuma falha encontrada nos logs")
            return []
        
        # Agrupar por tipo de falha
        failure_groups = defaultdict(list)
        
        for entry in error_entries:
            failure_type = self._classify_failure(entry.message)
            failure_groups[failure_type].append(entry)
        
        # Analisar cada grupo
        for failure_type, entries in failure_groups.items():
            pattern = self._analyze_failure_pattern(failure_type, entries)
            if pattern:
                self.failure_patterns.append(pattern)
        
        logger.info(f"Identificados {len(self.failure_patterns)} padrões de falha")
        return self.failure_patterns
    
    def _classify_failure(self, message: str) -> FailureType:
        """Classifica o tipo de falha baseado na mensagem"""
        message_lower = message.lower()
        
        if 'null' in message_lower or 'none' in message_lower:
            return FailureType.NULL_POINTER
        elif 'timeout' in message_lower or 'timed out' in message_lower:
            return FailureType.TIMEOUT
        elif 'memory' in message_lower or 'out of memory' in message_lower:
            return FailureType.MEMORY_LEAK
        elif 'validation' in message_lower or 'invalid' in message_lower:
            return FailureType.VALIDATION_ERROR
        elif 'permission' in message_lower or 'access denied' in message_lower:
            return FailureType.PERMISSION_ERROR
        elif 'network' in message_lower or 'connection' in message_lower:
            return FailureType.NETWORK_ERROR
        elif 'database' in message_lower or 'sql' in message_lower:
            return FailureType.DATABASE_ERROR
        elif 'security' in message_lower or 'unauthorized' in message_lower:
            return FailureType.SECURITY_ERROR
        else:
            return FailureType.UNKNOWN
    
    def _analyze_failure_pattern(self, failure_type: FailureType, entries: List[LogEntry]) -> Optional[FailurePattern]:
        """Analisa padrão específico de falha"""
        if len(entries) < 2:  # Mínimo 2 ocorrências para ser um padrão
            return None
        
        # Estatísticas básicas
        frequency = len(entries)
        affected_modules = list(set(entry.module for entry in entries))
        affected_functions = list(set(entry.function for entry in entries))
        
        # Mensagem mais comum
        messages = [entry.message for entry in entries]
        common_message = Counter(messages).most_common(1)[0][0]
        
        # Timestamp médio
        avg_timestamp = entries[len(entries) // 2].timestamp
        
        # Distribuição de severidade
        severity_distribution = Counter(entry.severity for entry in entries)
        
        # Gerar sugestões
        suggestions = self._generate_failure_suggestions(failure_type, entries)
        
        # Calcular score de prioridade
        priority_score = self._calculate_failure_priority(frequency, failure_type, affected_modules)
        
        return FailurePattern(
            failure_type=failure_type,
            frequency=frequency,
            affected_modules=affected_modules,
            affected_functions=affected_functions,
            common_message=common_message,
            avg_timestamp=avg_timestamp,
            severity_distribution=dict(severity_distribution),
            suggestions=suggestions,
            priority_score=priority_score
        )
    
    def _generate_failure_suggestions(self, failure_type: FailureType, entries: List[LogEntry]) -> List[str]:
        """Gera sugestões baseadas no tipo de falha"""
        suggestions = []
        
        if failure_type == FailureType.NULL_POINTER:
            suggestions.extend([
                "Implementar validação defensiva de parâmetros",
                "Adicionar verificações de None antes de acessar atributos",
                "Usar operador de coalescência nula (??) quando apropriado"
            ])
        elif failure_type == FailureType.TIMEOUT:
            suggestions.extend([
                "Implementar timeout configurável para operações",
                "Usar operações assíncronas para operações longas",
                "Implementar retry mechanism com backoff exponencial"
            ])
        elif failure_type == FailureType.MEMORY_LEAK:
            suggestions.extend([
                "Implementar context managers para recursos",
                "Verificar referências circulares",
                "Usar generators para processamento de grandes volumes"
            ])
        elif failure_type == FailureType.VALIDATION_ERROR:
            suggestions.extend([
                "Melhorar validação de entrada de dados",
                "Implementar logging estruturado com contexto",
                "Adicionar validação em múltiplas camadas"
            ])
        elif failure_type == FailureType.DATABASE_ERROR:
            suggestions.extend([
                "Implementar connection pooling",
                "Otimizar queries com índices apropriados",
                "Implementar retry mechanism para deadlocks"
            ])
        
        return suggestions
    
    def _calculate_failure_priority(self, frequency: int, failure_type: FailureType, affected_modules: List[str]) -> float:
        """Calcula score de prioridade para falha"""
        # Base score baseado na frequência
        base_score = min(frequency / 10.0, 1.0)
        
        # Multiplicador baseado no tipo de falha
        type_multipliers = {
            FailureType.SECURITY_ERROR: 2.0,
            FailureType.MEMORY_LEAK: 1.8,
            FailureType.DATABASE_ERROR: 1.5,
            FailureType.TIMEOUT: 1.3,
            FailureType.NULL_POINTER: 1.2,
            FailureType.VALIDATION_ERROR: 1.1,
            FailureType.PERMISSION_ERROR: 1.0,
            FailureType.NETWORK_ERROR: 0.9,
            FailureType.UNKNOWN: 0.8
        }
        
        type_multiplier = type_multipliers.get(failure_type, 1.0)
        
        # Multiplicador baseado no número de módulos afetados
        module_multiplier = min(len(affected_modules) / 5.0, 1.5)
        
        return min(base_score * type_multiplier * module_multiplier, 1.0)
    
    def analyze_performance_issues(self) -> List[PerformanceIssue]:
        """
        Analisa problemas de performance nos logs
        
        Returns:
            Lista de problemas de performance identificados
        """
        performance_entries = [entry for entry in self.log_entries if entry.metrics and 'duration' in entry.metrics]
        
        if not performance_entries:
            logger.info("Nenhuma métrica de performance encontrada nos logs")
            return []
        
        # Agrupar por operação
        operation_groups = defaultdict(list)
        
        for entry in performance_entries:
            operation = f"{entry.module}.{entry.function}"
            operation_groups[operation].append(entry)
        
        # Analisar cada operação
        for operation, entries in operation_groups.items():
            if len(entries) >= 3:  # Mínimo 3 medições para análise
                issue = self._analyze_performance_operation(operation, entries)
                if issue:
                    self.performance_issues.append(issue)
        
        logger.info(f"Identificados {len(self.performance_issues)} problemas de performance")
        return self.performance_issues
    
    def _analyze_performance_operation(self, operation: str, entries: List[LogEntry]) -> Optional[PerformanceIssue]:
        """Analisa performance de uma operação específica"""
        durations = [entry.metrics['duration'] for entry in entries if entry.metrics and 'duration' in entry.metrics]
        
        if not durations:
            return None
        
        avg_duration = statistics.mean(durations)
        max_duration = max(durations)
        
        # Considerar problema se média > 1000ms ou máximo > 5000ms
        if avg_duration < 1000 and max_duration < 5000:
            return None
        
        affected_modules = list(set(entry.module for entry in entries))
        frequency = len(entries)
        
        # Identificar fatores de bottleneck
        bottleneck_factors = self._identify_bottleneck_factors(entries)
        
        # Gerar sugestões
        suggestions = self._generate_performance_suggestions(avg_duration, max_duration, bottleneck_factors)
        
        # Calcular score de prioridade
        priority_score = self._calculate_performance_priority(avg_duration, max_duration, frequency)
        
        return PerformanceIssue(
            operation=operation,
            avg_duration=avg_duration,
            max_duration=max_duration,
            frequency=frequency,
            affected_modules=affected_modules,
            bottleneck_factors=bottleneck_factors,
            suggestions=suggestions,
            priority_score=priority_score
        )
    
    def _identify_bottleneck_factors(self, entries: List[LogEntry]) -> List[str]:
        """Identifica fatores de bottleneck"""
        factors = []
        
        # Verificar uso de memória
        memory_entries = [entry for entry in entries if entry.metrics and 'memory' in entry.metrics]
        if memory_entries:
            avg_memory = statistics.mean(entry.metrics['memory'] for entry in memory_entries)
            if avg_memory > 100:  # > 100MB
                factors.append("Alto uso de memória")
        
        # Verificar uso de CPU
        cpu_entries = [entry for entry in entries if entry.metrics and 'cpu' in entry.metrics]
        if cpu_entries:
            avg_cpu = statistics.mean(entry.metrics['cpu'] for entry in cpu_entries)
            if avg_cpu > 80:  # > 80%
                factors.append("Alto uso de CPU")
        
        # Verificar padrões de operação
        if len(entries) > 10:
            factors.append("Operação executada frequentemente")
        
        return factors
    
    def _generate_performance_suggestions(self, avg_duration: float, max_duration: float, bottleneck_factors: List[str]) -> List[str]:
        """Gera sugestões de otimização de performance"""
        suggestions = []
        
        if avg_duration > 2000:
            suggestions.append("Implementar cache para resultados frequentes")
            suggestions.append("Otimizar algoritmos com complexidade O(n²) ou pior")
        
        if max_duration > 10000:
            suggestions.append("Implementar timeout para operações longas")
            suggestions.append("Usar operações assíncronas")
        
        if "Alto uso de memória" in bottleneck_factors:
            suggestions.append("Implementar streaming para grandes volumes de dados")
            suggestions.append("Otimizar estruturas de dados")
        
        if "Alto uso de CPU" in bottleneck_factors:
            suggestions.append("Implementar paralelização de operações")
            suggestions.append("Otimizar loops e algoritmos")
        
        return suggestions
    
    def _calculate_performance_priority(self, avg_duration: float, max_duration: float, frequency: int) -> float:
        """Calcula score de prioridade para problema de performance"""
        # Base score baseado na duração média
        duration_score = min(avg_duration / 5000.0, 1.0)
        
        # Multiplicador baseado na duração máxima
        max_duration_multiplier = min(max_duration / 10000.0, 1.5)
        
        # Multiplicador baseado na frequência
        frequency_multiplier = min(frequency / 50.0, 1.3)
        
        return min(duration_score * max_duration_multiplier * frequency_multiplier, 1.0)
    
    def extract_suggestions(self) -> List[ImprovementSuggestion]:
        """
        Extrai sugestões de melhoria baseadas na análise
        
        Returns:
            Lista de sugestões de melhoria
        """
        suggestions = []
        
        # Sugestões baseadas em falhas
        for pattern in self.failure_patterns:
            if pattern.priority_score > 0.5:  # Apenas falhas com alta prioridade
                suggestion = self._create_failure_suggestion(pattern)
                suggestions.append(suggestion)
        
        # Sugestões baseadas em performance
        for issue in self.performance_issues:
            if issue.priority_score > 0.5:  # Apenas problemas com alta prioridade
                suggestion = self._create_performance_suggestion(issue)
                suggestions.append(suggestion)
        
        # Ordenar por prioridade
        suggestions.sort(key=lambda value: value.priority_score, reverse=True)
        
        self.improvement_suggestions = suggestions
        logger.info(f"Extraídas {len(suggestions)} sugestões de melhoria")
        return suggestions
    
    def _create_failure_suggestion(self, pattern: FailurePattern) -> ImprovementSuggestion:
        """Cria sugestão baseada em padrão de falha"""
        title = f"Corrigir {pattern.failure_type.value} em {', '.join(pattern.affected_modules)}"
        
        description = f"Identificado padrão de {pattern.failure_type.value} com {pattern.frequency} ocorrências"
        
        affected_files = list(set(f"{module}.py" for module in pattern.affected_modules))
        
        impact_level = "ALTO" if pattern.priority_score > 0.7 else "MÉDIO" if pattern.priority_score > 0.4 else "BAIXO"
        effort_level = "BAIXO" if pattern.failure_type in [FailureType.NULL_POINTER, FailureType.VALIDATION_ERROR] else "MÉDIO"
        urgency_level = "ALTA" if pattern.failure_type == FailureType.SECURITY_ERROR else "MÉDIA"
        
        roi_score = pattern.priority_score * 0.8  # ROI baseado na prioridade
        
        evidence = [
            f"{pattern.frequency} ocorrências de {pattern.failure_type.value}",
            f"Módulos afetados: {', '.join(pattern.affected_modules)}",
            f"Mensagem comum: {pattern.common_message}"
        ]
        
        implementation_steps = [
            "Analisar código dos módulos afetados",
            "Implementar correções sugeridas",
            "Adicionar testes para cenários de falha",
            "Monitorar redução de falhas após correção"
        ]
        
        return ImprovementSuggestion(
            title=title,
            description=description,
            affected_files=affected_files,
            affected_functions=pattern.affected_functions,
            impact_level=impact_level,
            effort_level=effort_level,
            urgency_level=urgency_level,
            roi_score=roi_score,
            priority_score=pattern.priority_score,
            evidence=evidence,
            implementation_steps=implementation_steps
        )
    
    def _create_performance_suggestion(self, issue: PerformanceIssue) -> ImprovementSuggestion:
        """Cria sugestão baseada em problema de performance"""
        title = f"Otimizar performance de {issue.operation}"
        
        description = f"Operação {issue.operation} tem duração média de {issue.avg_duration:.0f}ms"
        
        affected_files = list(set(f"{module}.py" for module in issue.affected_modules))
        
        impact_level = "ALTO" if issue.priority_score > 0.7 else "MÉDIO" if issue.priority_score > 0.4 else "BAIXO"
        effort_level = "MÉDIO" if issue.avg_duration > 2000 else "BAIXO"
        urgency_level = "MÉDIA" if issue.max_duration > 10000 else "BAIXA"
        
        roi_score = issue.priority_score * 0.6  # ROI menor para performance
        
        evidence = [
            f"Duração média: {issue.avg_duration:.0f}ms",
            f"Duração máxima: {issue.max_duration:.0f}ms",
            f"Frequência: {issue.frequency} execuções",
            f"Fatores de bottleneck: {', '.join(issue.bottleneck_factors)}"
        ]
        
        implementation_steps = [
            "Analisar código da operação",
            "Implementar otimizações sugeridas",
            "Adicionar métricas de performance",
            "Validar melhoria com testes de carga"
        ]
        
        return ImprovementSuggestion(
            title=title,
            description=description,
            affected_files=affected_files,
            affected_functions=[issue.operation.split('.')[-1]],
            impact_level=impact_level,
            effort_level=effort_level,
            urgency_level=urgency_level,
            roi_score=roi_score,
            priority_score=issue.priority_score,
            evidence=evidence,
            implementation_steps=implementation_steps
        )
    
    def prioritize_improvements(self) -> List[ImprovementSuggestion]:
        """
        Prioriza melhorias baseadas em múltiplos critérios
        
        Returns:
            Lista de sugestões priorizadas
        """
        if not self.improvement_suggestions:
            self.extract_suggestions()
        
        # Calcular score final de priorização
        for suggestion in self.improvement_suggestions:
            final_score = self._calculate_final_priority_score(suggestion)
            suggestion.priority_score = final_score
        
        # Ordenar por score final
        prioritized_suggestions = sorted(
            self.improvement_suggestions,
            key=lambda value: value.priority_score,
            reverse=True
        )
        
        logger.info(f"Priorizadas {len(prioritized_suggestions)} sugestões de melhoria")
        return prioritized_suggestions
    
    def _calculate_final_priority_score(self, suggestion: ImprovementSuggestion) -> float:
        """Calcula score final de priorização"""
        # Mapear níveis para valores numéricos
        impact_values = {"ALTO": 1.0, "MÉDIO": 0.6, "BAIXO": 0.3}
        effort_values = {"BAIXO": 1.0, "MÉDIO": 0.7, "ALTO": 0.4}
        urgency_values = {"ALTA": 1.0, "MÉDIA": 0.6, "BAIXA": 0.3}
        
        impact_score = impact_values.get(suggestion.impact_level, 0.5)
        effort_score = effort_values.get(suggestion.effort_level, 0.7)
        urgency_score = urgency_values.get(suggestion.urgency_level, 0.6)
        
        # Fórmula de priorização: (Impacto * Urgência) / Esforço * ROI
        final_score = (impact_score * urgency_score) / effort_score * suggestion.roi_score
        
        return min(final_score, 1.0)
    
    def generate_report(self) -> str:
        """
        Gera relatório completo de análise
        
        Returns:
            String com relatório formatado
        """
        if not self.improvement_suggestions:
            self.prioritize_improvements()
        
        report_parts = []
        
        # Cabeçalho
        report_parts.append("# 📊 RELATÓRIO DE ANÁLISE DE LOGS")
        report_parts.append(f"**Data**: {datetime.now().strftime('%Y-%m-%data %H:%M:%S')}")
        report_parts.append(f"**Total de Logs**: {len(self.log_entries)}")
        report_parts.append(f"**Período**: {min(e.timestamp for e in self.log_entries)} a {max(e.timestamp for e in self.log_entries)}")
        report_parts.append("")
        
        # Resumo executivo
        report_parts.append("## 📋 RESUMO EXECUTIVO")
        report_parts.append(f"- **Padrões de Falha Identificados**: {len(self.failure_patterns)}")
        report_parts.append(f"- **Problemas de Performance**: {len(self.performance_issues)}")
        report_parts.append(f"- **Sugestões de Melhoria**: {len(self.improvement_suggestions)}")
        report_parts.append("")
        
        # Top 5 sugestões prioritárias
        report_parts.append("## 🎯 TOP 5 SUGESTÕES PRIORITÁRIAS")
        for index, suggestion in enumerate(self.improvement_suggestions[:5], 1):
            report_parts.append(f"### {index}. {suggestion.title}")
            report_parts.append(f"**Descrição**: {suggestion.description}")
            report_parts.append(f"**Impacto**: {suggestion.impact_level}")
            report_parts.append(f"**Esforço**: {suggestion.effort_level}")
            report_parts.append(f"**Urgência**: {suggestion.urgency_level}")
            report_parts.append(f"**Score de Prioridade**: {suggestion.priority_score:.2f}")
            report_parts.append("")
        
        # Análise detalhada de falhas
        if self.failure_patterns:
            report_parts.append("## 🚨 ANÁLISE DETALHADA DE FALHAS")
            for pattern in sorted(self.failure_patterns, key=lambda value: value.priority_score, reverse=True):
                report_parts.append(f"### {pattern.failure_type.value}")
                report_parts.append(f"- **Frequência**: {pattern.frequency} ocorrências")
                report_parts.append(f"- **Módulos Afetados**: {', '.join(pattern.affected_modules)}")
                report_parts.append(f"- **Score de Prioridade**: {pattern.priority_score:.2f}")
                report_parts.append(f"- **Sugestões**:")
                for suggestion in pattern.suggestions:
                    report_parts.append(f"  - {suggestion}")
                report_parts.append("")
        
        # Análise de performance
        if self.performance_issues:
            report_parts.append("## ⚡ ANÁLISE DE PERFORMANCE")
            for issue in sorted(self.performance_issues, key=lambda value: value.priority_score, reverse=True):
                report_parts.append(f"### {issue.operation}")
                report_parts.append(f"- **Duração Média**: {issue.avg_duration:.0f}ms")
                report_parts.append(f"- **Duração Máxima**: {issue.max_duration:.0f}ms")
                report_parts.append(f"- **Frequência**: {issue.frequency} execuções")
                report_parts.append(f"- **Score de Prioridade**: {issue.priority_score:.2f}")
                report_parts.append(f"- **Sugestões**:")
                for suggestion in issue.suggestions:
                    report_parts.append(f"  - {suggestion}")
                report_parts.append("")
        
        return "\n".join(report_parts)
    
    def save_report(self, output_path: str):
        """
        Salva relatório em arquivo
        
        Args:
            output_path: Caminho para salvar o relatório
        """
        report_content = self.generate_report()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Relatório salvo em: {output_path}")


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analisador de Logs")
    parser.add_argument("--logs-dir", default="logs", help="Diretório de logs")
    parser.add_argument("--output", default="docs/log_analysis_report.md", help="Arquivo de saída")
    parser.add_argument("--days", type=int, default=7, help="Número de dias para analisar")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.logs_dir)
    
    # Definir período de análise
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    # Carregar e analisar logs
    entries_loaded = analyzer.load_logs(start_date, end_date)
    
    if entries_loaded == 0:
        print("Nenhum log encontrado para análise")
        return 1
    
    # Executar análises
    analyzer.analyze_failures()
    analyzer.analyze_performance_issues()
    analyzer.prioritize_improvements()
    
    # Gerar e salvar relatório
    analyzer.save_report(args.output)
    
    print(f"Análise concluída. Relatório salvo em: {args.output}")
    return 0


if __name__ == "__main__":
    exit(main()) 