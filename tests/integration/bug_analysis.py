"""
Sistema de Análise de Bugs
Prompt: Testes de Integração - Fase 3
Ruleset: enterprise_control_layer.yaml
Data: 2025-01-27T16:05:00Z
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from collections import defaultdict, Counter

# Importações do sistema real
from infrastructure.logging.structured_logger import StructuredLogger
from infrastructure.monitoring.metrics_collector import MetricsCollector
from infrastructure.cache.redis_cache import RedisCache

class BugCategory(Enum):
    """Categorias de bugs."""
    API_ERROR = "api_error"
    TIMEOUT = "timeout"
    CONNECTION = "connection"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    CIRCUIT_BREAKER = "circuit_breaker"
    CACHE = "cache"
    DATABASE = "database"
    MEMORY = "memory"
    PERFORMANCE = "performance"
    SECURITY = "security"
    OTHER = "other"

class BugPattern(Enum):
    """Padrões de bugs identificados."""
    INTERMITTENT = "intermittent"
    REPRODUCIBLE = "reproducible"
    SEASONAL = "seasonal"
    CASCADING = "cascading"
    ISOLATED = "isolated"

@dataclass
class BugAnalysis:
    """Análise detalhada de um bug."""
    bug_id: str
    category: BugCategory
    pattern: BugPattern
    frequency: int
    impact_score: float
    root_cause: str
    affected_modules: List[str]
    time_distribution: Dict[str, int]
    user_impact_level: str
    resolution_priority: int
    suggested_tests: List[str]
    risk_score: float
    analysis_timestamp: datetime

@dataclass
class BugTrend:
    """Tendência de bugs ao longo do tempo."""
    category: BugCategory
    period: str
    total_occurrences: int
    trend_direction: str  # "increasing", "decreasing", "stable"
    average_frequency: float
    peak_times: List[str]
    correlation_factors: List[str]

class BugAnalysisSystem:
    """
    Sistema de análise de bugs que identifica padrões,
    tendências e gera insights para melhorar testes.
    """
    
    def __init__(self):
        """Inicialização do sistema de análise de bugs."""
        self.logger = StructuredLogger(
            module="bug_analysis",
            tracing_id="bug_analysis_001"
        )
        
        self.metrics = MetricsCollector()
        self.cache = RedisCache()
        
        # Configurações de análise
        self.analysis_window_days = 30
        self.min_frequency_threshold = 3
        self.correlation_threshold = 0.7
        
        # Armazenamento de análises
        self.bug_analyses: Dict[str, BugAnalysis] = {}
        self.bug_trends: Dict[str, BugTrend] = {}
        self.pattern_database: Dict[str, List[str]] = {}
        
        self.logger.info("Sistema de análise de bugs inicializado")
    
    async def analyze_bug_patterns(self, bug_reports: List[Dict[str, Any]]) -> List[BugAnalysis]:
        """
        Analisa padrões em relatórios de bugs.
        
        Args:
            bug_reports: Lista de relatórios de bugs
            
        Returns:
            Lista de análises de bugs
        """
        self.logger.info(f"Iniciando análise de {len(bug_reports)} bugs")
        
        analyses = []
        
        for bug_report in bug_reports:
            analysis = await self._analyze_single_bug(bug_report)
            if analysis:
                analyses.append(analysis)
                self.bug_analyses[analysis.bug_id] = analysis
        
        self.logger.info(f"Análise concluída: {len(analyses)} bugs analisados")
        return analyses
    
    async def _analyze_single_bug(self, bug_report: Dict[str, Any]) -> Optional[BugAnalysis]:
        """Analisa um bug individual."""
        try:
            # Categorizar bug
            category = self._categorize_bug(bug_report["error_message"])
            
            # Identificar padrão
            pattern = self._identify_pattern(bug_report)
            
            # Calcular impacto
            impact_score = self._calculate_impact_score(bug_report)
            
            # Identificar causa raiz
            root_cause = self._identify_root_cause(bug_report)
            
            # Identificar módulos afetados
            affected_modules = self._identify_affected_modules(bug_report)
            
            # Analisar distribuição temporal
            time_distribution = self._analyze_time_distribution(bug_report)
            
            # Calcular risco
            risk_score = self._calculate_risk_score(bug_report, impact_score)
            
            # Gerar sugestões de testes
            suggested_tests = self._generate_test_suggestions(bug_report, category)
            
            analysis = BugAnalysis(
                bug_id=bug_report["id"],
                category=category,
                pattern=pattern,
                frequency=bug_report.get("frequency", 1),
                impact_score=impact_score,
                root_cause=root_cause,
                affected_modules=affected_modules,
                time_distribution=time_distribution,
                user_impact_level=self._determine_user_impact(bug_report),
                resolution_priority=self._calculate_priority(impact_score, risk_score),
                suggested_tests=suggested_tests,
                risk_score=risk_score,
                analysis_timestamp=datetime.now()
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar bug {bug_report.get('id', 'unknown')}: {str(e)}")
            return None
    
    def _categorize_bug(self, error_message: str) -> BugCategory:
        """Categoriza bug baseado na mensagem de erro."""
        error_lower = error_message.lower()
        
        # Mapeamento de categorias
        category_mapping = {
            BugCategory.API_ERROR: ["api", "http", "rest", "endpoint"],
            BugCategory.TIMEOUT: ["timeout", "timed out", "expired"],
            BugCategory.CONNECTION: ["connection", "connect", "network"],
            BugCategory.VALIDATION: ["validation", "invalid", "format"],
            BugCategory.AUTHENTICATION: ["auth", "authentication", "unauthorized"],
            BugCategory.RATE_LIMIT: ["rate limit", "throttle", "quota"],
            BugCategory.CIRCUIT_BREAKER: ["circuit", "breaker", "open"],
            BugCategory.CACHE: ["cache", "redis", "memory"],
            BugCategory.DATABASE: ["database", "sql", "query"],
            BugCategory.MEMORY: ["memory", "out of memory", "heap"],
            BugCategory.PERFORMANCE: ["performance", "slow", "latency"],
            BugCategory.SECURITY: ["security", "vulnerability", "injection"]
        }
        
        for category, keywords in category_mapping.items():
            if any(keyword in error_lower for keyword in keywords):
                return category
        
        return BugCategory.OTHER
    
    def _identify_pattern(self, bug_report: Dict[str, Any]) -> BugPattern:
        """Identifica padrão do bug."""
        frequency = bug_report.get("frequency", 1)
        timestamp = bug_report.get("timestamp")
        
        if frequency > 10:
            return BugPattern.REPRODUCIBLE
        elif frequency > 3:
            return BugPattern.INTERMITTENT
        else:
            return BugPattern.ISOLATED
    
    def _calculate_impact_score(self, bug_report: Dict[str, Any]) -> float:
        """Calcula score de impacto do bug."""
        base_score = 0.0
        
        # Severidade
        severity = bug_report.get("severity", "low")
        severity_scores = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
        base_score += severity_scores.get(severity, 0.2)
        
        # Frequência
        frequency = bug_report.get("frequency", 1)
        if frequency > 10:
            base_score += 0.3
        elif frequency > 5:
            base_score += 0.2
        elif frequency > 1:
            base_score += 0.1
        
        # Impacto no usuário
        user_impact = bug_report.get("user_impact", "")
        if "failed" in user_impact.lower():
            base_score += 0.2
        if "unavailable" in user_impact.lower():
            base_score += 0.3
        
        return min(base_score, 1.0)
    
    def _identify_root_cause(self, bug_report: Dict[str, Any]) -> str:
        """Identifica causa raiz do bug."""
        error_message = bug_report.get("error_message", "")
        stack_trace = bug_report.get("stack_trace", "")
        
        # Análise baseada em palavras-chave
        if "timeout" in error_message.lower():
            return "Network timeout or service unresponsive"
        elif "connection" in error_message.lower():
            return "Network connectivity issues"
        elif "rate limit" in error_message.lower():
            return "API rate limiting exceeded"
        elif "authentication" in error_message.lower():
            return "Invalid or expired credentials"
        elif "validation" in error_message.lower():
            return "Invalid input data format"
        elif "circuit" in error_message.lower():
            return "Circuit breaker activated due to service failures"
        else:
            return "Unknown root cause - requires investigation"
    
    def _identify_affected_modules(self, bug_report: Dict[str, Any]) -> List[str]:
        """Identifica módulos afetados pelo bug."""
        modules = []
        
        # Módulo principal
        main_module = bug_report.get("module", "")
        if main_module:
            modules.append(main_module)
        
        # Módulos relacionados baseados no tipo de erro
        error_message = bug_report.get("error_message", "")
        
        if "api" in error_message.lower():
            modules.extend(["api_gateway", "external_apis"])
        
        if "cache" in error_message.lower():
            modules.extend(["cache_manager", "redis_client"])
        
        if "database" in error_message.lower():
            modules.extend(["database", "orm"])
        
        return list(set(modules))  # Remove duplicatas
    
    def _analyze_time_distribution(self, bug_report: Dict[str, Any]) -> Dict[str, int]:
        """Analisa distribuição temporal do bug."""
        # Simulação de distribuição temporal
        return {
            "morning": 5,
            "afternoon": 12,
            "evening": 8,
            "night": 3
        }
    
    def _determine_user_impact(self, bug_report: Dict[str, Any]) -> str:
        """Determina nível de impacto no usuário."""
        user_impact = bug_report.get("user_impact", "")
        
        if "failed" in user_impact.lower() and "critical" in user_impact.lower():
            return "critical"
        elif "failed" in user_impact.lower():
            return "high"
        elif "unavailable" in user_impact.lower():
            return "medium"
        else:
            return "low"
    
    def _calculate_priority(self, impact_score: float, risk_score: float) -> int:
        """Calcula prioridade de resolução."""
        # Prioridade 1-5 (1 = mais alta)
        combined_score = (impact_score + risk_score) / 2
        
        if combined_score > 0.8:
            return 1
        elif combined_score > 0.6:
            return 2
        elif combined_score > 0.4:
            return 3
        elif combined_score > 0.2:
            return 4
        else:
            return 5
    
    def _calculate_risk_score(self, bug_report: Dict[str, Any], impact_score: float) -> float:
        """Calcula score de risco do bug."""
        risk_score = impact_score
        
        # Fatores de risco adicionais
        severity = bug_report.get("severity", "low")
        if severity == "critical":
            risk_score += 0.3
        elif severity == "high":
            risk_score += 0.2
        
        # Frequência
        frequency = bug_report.get("frequency", 1)
        if frequency > 5:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_test_suggestions(self, bug_report: Dict[str, Any], category: BugCategory) -> List[str]:
        """Gera sugestões de testes baseadas no bug."""
        suggestions = []
        
        # Testes específicos por categoria
        if category == BugCategory.API_ERROR:
            suggestions.extend([
                "test_api_error_handling",
                "test_api_timeout_scenarios",
                "test_api_rate_limiting"
            ])
        elif category == BugCategory.TIMEOUT:
            suggestions.extend([
                "test_timeout_handling",
                "test_connection_timeout",
                "test_service_timeout"
            ])
        elif category == BugCategory.CONNECTION:
            suggestions.extend([
                "test_connection_failure",
                "test_network_unavailable",
                "test_connection_recovery"
            ])
        elif category == BugCategory.RATE_LIMIT:
            suggestions.extend([
                "test_rate_limit_exceeded",
                "test_rate_limit_recovery",
                "test_rate_limit_thresholds"
            ])
        elif category == BugCategory.CIRCUIT_BREAKER:
            suggestions.extend([
                "test_circuit_breaker_activation",
                "test_circuit_breaker_recovery",
                "test_circuit_breaker_states"
            ])
        
        # Testes gerais
        suggestions.extend([
            "test_error_logging",
            "test_error_metrics",
            "test_error_user_feedback"
        ])
        
        return suggestions
    
    async def analyze_bug_trends(self, time_period: str = "30d") -> List[BugTrend]:
        """
        Analisa tendências de bugs ao longo do tempo.
        
        Args:
            time_period: Período de análise (ex: "7d", "30d", "90d")
            
        Returns:
            Lista de tendências de bugs
        """
        self.logger.info(f"Analisando tendências de bugs para período: {time_period}")
        
        if not self.bug_analyses:
            return []
        
        # Agrupar bugs por categoria
        bugs_by_category = defaultdict(list)
        for analysis in self.bug_analyses.values():
            bugs_by_category[analysis.category].append(analysis)
        
        trends = []
        
        for category, analyses in bugs_by_category.items():
            trend = self._calculate_category_trend(category, analyses, time_period)
            if trend:
                trends.append(trend)
                self.bug_trends[f"{category.value}_{time_period}"] = trend
        
        self.logger.info(f"Análise de tendências concluída: {len(trends)} tendências identificadas")
        return trends
    
    def _calculate_category_trend(self, category: BugCategory, analyses: List[BugAnalysis], time_period: str) -> Optional[BugTrend]:
        """Calcula tendência para uma categoria específica."""
        if not analyses:
            return None
        
        # Calcular métricas
        total_occurrences = sum(analysis.frequency for analysis in analyses)
        average_frequency = total_occurrences / len(analyses)
        
        # Determinar direção da tendência
        recent_analyses = [
            a for a in analyses 
            if a.analysis_timestamp > datetime.now() - timedelta(days=7)
        ]
        
        if len(recent_analyses) > len(analyses) * 0.7:
            trend_direction = "increasing"
        elif len(recent_analyses) < len(analyses) * 0.3:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        # Identificar horários de pico
        peak_times = self._identify_peak_times(analyses)
        
        # Identificar fatores de correlação
        correlation_factors = self._identify_correlation_factors(analyses)
        
        return BugTrend(
            category=category,
            period=time_period,
            total_occurrences=total_occurrences,
            trend_direction=trend_direction,
            average_frequency=average_frequency,
            peak_times=peak_times,
            correlation_factors=correlation_factors
        )
    
    def _identify_peak_times(self, analyses: List[BugAnalysis]) -> List[str]:
        """Identifica horários de pico para bugs."""
        time_distributions = [analysis.time_distribution for analysis in analyses]
        
        if not time_distributions:
            return []
        
        # Calcular médias
        total_distribution = defaultdict(int)
        for dist in time_distributions:
            for time_period, count in dist.items():
                total_distribution[time_period] += count
        
        # Identificar picos (acima da média)
        total_count = sum(total_distribution.values())
        average_count = total_count / len(total_distribution)
        
        peak_times = [
            time_period for time_period, count in total_distribution.items()
            if count > average_count * 1.5
        ]
        
        return peak_times
    
    def _identify_correlation_factors(self, analyses: List[BugAnalysis]) -> List[str]:
        """Identifica fatores de correlação para bugs."""
        factors = []
        
        # Análise de módulos afetados
        all_modules = []
        for analysis in analyses:
            all_modules.extend(analysis.affected_modules)
        
        module_counts = Counter(all_modules)
        common_modules = [
            module for module, count in module_counts.items()
            if count > len(analyses) * 0.5
        ]
        
        if common_modules:
            factors.append(f"Common modules: {', '.join(common_modules)}")
        
        # Análise de padrões temporais
        if any(analysis.pattern == BugPattern.SEASONAL for analysis in analyses):
            factors.append("Seasonal pattern detected")
        
        if any(analysis.pattern == BugPattern.CASCADING for analysis in analyses):
            factors.append("Cascading failure pattern")
        
        return factors
    
    async def generate_insights_report(self) -> Dict[str, Any]:
        """
        Gera relatório de insights baseado na análise de bugs.
        
        Returns:
            Dicionário com insights e recomendações
        """
        self.logger.info("Gerando relatório de insights")
        
        if not self.bug_analyses:
            return {"message": "Nenhum bug analisado para gerar insights"}
        
        # Estatísticas gerais
        total_bugs = len(self.bug_analyses)
        critical_bugs = len([a for a in self.bug_analyses.values() if a.impact_score > 0.8])
        high_priority_bugs = len([a for a in self.bug_analyses.values() if a.resolution_priority <= 2])
        
        # Categorias mais comuns
        category_counts = Counter(analysis.category for analysis in self.bug_analyses.values())
        most_common_category = category_counts.most_common(1)[0] if category_counts else None
        
        # Padrões identificados
        pattern_counts = Counter(analysis.pattern for analysis in self.bug_analyses.values())
        
        # Módulos mais afetados
        all_modules = []
        for analysis in self.bug_analyses.values():
            all_modules.extend(analysis.affected_modules)
        module_counts = Counter(all_modules)
        most_affected_modules = module_counts.most_common(3)
        
        # Recomendações
        recommendations = self._generate_recommendations()
        
        # Insights de risco
        risk_insights = self._generate_risk_insights()
        
        report = {
            "summary": {
                "total_bugs_analyzed": total_bugs,
                "critical_bugs": critical_bugs,
                "high_priority_bugs": high_priority_bugs,
                "analysis_period": f"{self.analysis_window_days} days"
            },
            "categories": {
                "most_common": most_common_category[0].value if most_common_category else None,
                "distribution": {cat.value: count for cat, count in category_counts.items()}
            },
            "patterns": {
                "distribution": {pattern.value: count for pattern, count in pattern_counts.items()}
            },
            "modules": {
                "most_affected": [{"module": module, "count": count} for module, count in most_affected_modules]
            },
            "recommendations": recommendations,
            "risk_insights": risk_insights,
            "generated_at": datetime.now().isoformat()
        }
        
        self.logger.info("Relatório de insights gerado com sucesso")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []
        
        # Análise de categorias críticas
        critical_categories = [
            cat for cat, count in Counter(analysis.category for analysis in self.bug_analyses.values()).items()
            if count > len(self.bug_analyses) * 0.2
        ]
        
        for category in critical_categories:
            if category == BugCategory.API_ERROR:
                recommendations.append("Implementar testes mais robustos para APIs externas")
            elif category == BugCategory.TIMEOUT:
                recommendations.append("Ajustar timeouts e implementar retry logic")
            elif category == BugCategory.CONNECTION:
                recommendations.append("Melhorar tratamento de falhas de conexão")
            elif category == BugCategory.RATE_LIMIT:
                recommendations.append("Implementar rate limiting mais inteligente")
        
        # Recomendações gerais
        if len(self.bug_analyses) > 10:
            recommendations.append("Considerar implementar monitoramento proativo")
        
        if any(analysis.risk_score > 0.8 for analysis in self.bug_analyses.values()):
            recommendations.append("Priorizar correção de bugs de alto risco")
        
        return recommendations
    
    def _generate_risk_insights(self) -> Dict[str, Any]:
        """Gera insights sobre riscos."""
        high_risk_bugs = [a for a in self.bug_analyses.values() if a.risk_score > 0.7]
        
        return {
            "high_risk_count": len(high_risk_bugs),
            "average_risk_score": sum(a.risk_score for a in self.bug_analyses.values()) / len(self.bug_analyses),
            "risk_distribution": {
                "low": len([a for a in self.bug_analyses.values() if a.risk_score < 0.3]),
                "medium": len([a for a in self.bug_analyses.values() if 0.3 <= a.risk_score < 0.7]),
                "high": len([a for a in self.bug_analyses.values() if a.risk_score >= 0.7])
            },
            "top_risk_factors": self._identify_top_risk_factors()
        }
    
    def _identify_top_risk_factors(self) -> List[str]:
        """Identifica os principais fatores de risco."""
        factors = []
        
        # Bugs críticos
        critical_bugs = [a for a in self.bug_analyses.values() if a.impact_score > 0.8]
        if critical_bugs:
            factors.append(f"{len(critical_bugs)} bugs críticos identificados")
        
        # Padrões problemáticos
        if any(a.pattern == BugPattern.CASCADING for a in self.bug_analyses.values()):
            factors.append("Padrão de falha em cascata detectado")
        
        # Módulos com muitos bugs
        module_counts = Counter()
        for analysis in self.bug_analyses.values():
            for module in analysis.affected_modules:
                module_counts[module] += 1
        
        problematic_modules = [
            module for module, count in module_counts.items()
            if count > len(self.bug_analyses) * 0.3
        ]
        
        if problematic_modules:
            factors.append(f"Módulos problemáticos: {', '.join(problematic_modules)}")
        
        return factors
    
    async def get_analysis_status(self) -> Dict[str, Any]:
        """
        Retorna status do sistema de análise.
        
        Returns:
            Dicionário com status do sistema
        """
        return {
            "system_enabled": True,
            "total_bugs_analyzed": len(self.bug_analyses),
            "total_trends_identified": len(self.bug_trends),
            "analysis_window_days": self.analysis_window_days,
            "min_frequency_threshold": self.min_frequency_threshold,
            "correlation_threshold": self.correlation_threshold,
            "last_analysis": datetime.now().isoformat(),
            "system_health": "healthy"
        } 