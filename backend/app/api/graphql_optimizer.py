#!/usr/bin/env python3
"""
⚡ GRAPHQL QUERY OPTIMIZER - OMNİ KEYWORDS FINDER

Tracing ID: GRAPHQL_OPTIMIZER_2025_001
Data/Hora: 2025-01-27 18:30:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Sistema de otimização de queries GraphQL com análise de complexidade.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re
from collections import defaultdict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)string_data] [%(levelname)string_data] [GRAPHQL_OPTIMIZER] %(message)string_data',
    handlers=[
        logging.FileHandler('logs/graphql_optimizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QueryComplexity(Enum):
    """Níveis de complexidade de query"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class OptimizationType(Enum):
    """Tipos de otimização"""
    CACHE = "cache"
    PAGINATION = "pagination"
    FIELD_SELECTION = "field_selection"
    DEPTH_LIMIT = "depth_limit"
    COMPLEXITY_LIMIT = "complexity_limit"

@dataclass
class QueryAnalysis:
    """Análise de query"""
    query: str
    operation_name: Optional[str]
    complexity_score: int
    complexity_level: QueryComplexity
    field_count: int
    depth: int
    has_pagination: bool
    has_fragments: bool
    has_variables: bool
    estimated_cost: float
    optimization_suggestions: List[str]
    execution_time: Optional[float] = None

@dataclass
class OptimizationResult:
    """Resultado de otimização"""
    original_query: str
    optimized_query: str
    optimizations_applied: List[OptimizationType]
    complexity_reduction: float
    estimated_improvement: float
    suggestions: List[str]

class GraphQLQueryAnalyzer:
    """Analisador de queries GraphQL"""
    
    def __init__(self):
        self.field_weights = {
            'nichos': 1,
            'categorias': 2,
            'execucoes': 3,
            'keywords': 5,
            'clusters': 4,
            'business_metrics': 2,
            'performance_metrics': 2,
            'logs': 3,
            'notificacoes': 1
        }
        
        self.depth_penalty = 1.5
        self.complexity_thresholds = {
            QueryComplexity.LOW: 10,
            QueryComplexity.MEDIUM: 25,
            QueryComplexity.HIGH: 50,
            QueryComplexity.CRITICAL: 100
        }
    
    def analyze_query(self, query: str, operation_name: Optional[str] = None) -> QueryAnalysis:
        """Analisa uma query GraphQL"""
        start_time = time.time()
        
        # Parse da query
        parsed = self._parse_query(query)
        
        # Calcula métricas
        field_count = self._count_fields(parsed)
        depth = self._calculate_depth(parsed)
        complexity_score = self._calculate_complexity(parsed, depth)
        complexity_level = self._get_complexity_level(complexity_score)
        estimated_cost = self._estimate_cost(complexity_score, depth)
        
        # Verifica características
        has_pagination = self._has_pagination(query)
        has_fragments = self._has_fragments(query)
        has_variables = self._has_variables(query)
        
        # Gera sugestões
        suggestions = self._generate_suggestions(
            complexity_score, depth, field_count, has_pagination
        )
        
        execution_time = time.time() - start_time
        
        return QueryAnalysis(
            query=query,
            operation_name=operation_name,
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            field_count=field_count,
            depth=depth,
            has_pagination=has_pagination,
            has_fragments=has_fragments,
            has_variables=has_variables,
            estimated_cost=estimated_cost,
            optimization_suggestions=suggestions,
            execution_time=execution_time
        )
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse básico da query"""
        # Remove comentários e espaços extras
        query = re.sub(r'#.*$', '', query, flags=re.MULTILINE)
        query = query.strip()
        
        # Extrai operação
        operation_match = re.search(r'(query|mutation|subscription)\string_data+(\w+)', query)
        operation_type = operation_match.group(1) if operation_match else 'query'
        operation_name = operation_match.group(2) if operation_match else None
        
        # Extrai campos
        fields = re.findall(r'(\w+)\string_data*\{', query)
        
        return {
            'type': operation_type,
            'name': operation_name,
            'fields': fields,
            'raw': query
        }
    
    def _count_fields(self, parsed: Dict[str, Any]) -> int:
        """Conta campos na query"""
        return len(parsed['fields'])
    
    def _calculate_depth(self, parsed: Dict[str, Any]) -> int:
        """Calcula profundidade da query"""
        query = parsed['raw']
        max_depth = 0
        current_depth = 0
        
        for char in query:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth -= 1
        
        return max_depth
    
    def _calculate_complexity(self, parsed: Dict[str, Any], depth: int) -> int:
        """Calcula score de complexidade"""
        base_score = 0
        
        # Score baseado nos campos
        for field in parsed['fields']:
            base_score += self.field_weights.get(field, 1)
        
        # Penalidade por profundidade
        depth_penalty = depth * self.depth_penalty
        
        return int(base_score + depth_penalty)
    
    def _get_complexity_level(self, score: int) -> QueryComplexity:
        """Determina nível de complexidade"""
        for level, threshold in self.complexity_thresholds.items():
            if score <= threshold:
                return level
        return QueryComplexity.CRITICAL
    
    def _estimate_cost(self, complexity: int, depth: int) -> float:
        """Estima custo de execução"""
        # Custo baseado em complexidade e profundidade
        base_cost = complexity * 0.1
        depth_cost = depth * 0.05
        return base_cost + depth_cost
    
    def _has_pagination(self, query: str) -> bool:
        """Verifica se query tem paginação"""
        pagination_patterns = [
            r'limit\string_data*:',
            r'offset\string_data*:',
            r'first\string_data*:',
            r'after\string_data*:',
            r'cursor\string_data*:'
        ]
        
        for pattern in pagination_patterns:
            if re.search(pattern, query):
                return True
        return False
    
    def _has_fragments(self, query: str) -> bool:
        """Verifica se query tem fragments"""
        return 'fragment' in query.lower()
    
    def _has_variables(self, query: str) -> bool:
        """Verifica se query tem variáveis"""
        return '$' in query
    
    def _generate_suggestions(self, complexity: int, depth: int, 
                            field_count: int, has_pagination: bool) -> List[str]:
        """Gera sugestões de otimização"""
        suggestions = []
        
        if complexity > 50:
            suggestions.append("Considerar quebrar a query em múltiplas queries menores")
        
        if depth > 5:
            suggestions.append("Limitar profundidade da query para melhorar performance")
        
        if field_count > 20:
            suggestions.append("Selecionar apenas campos necessários para reduzir overhead")
        
        if not has_pagination and field_count > 10:
            suggestions.append("Implementar paginação para queries com muitos campos")
        
        if complexity > 25:
            suggestions.append("Utilizar cache para queries complexas")
        
        return suggestions

class GraphQLQueryOptimizer:
    """Otimizador de queries GraphQL"""
    
    def __init__(self):
        self.analyzer = GraphQLQueryAnalyzer()
        self.max_complexity = 50
        self.max_depth = 5
        self.max_fields = 20
    
    def optimize_query(self, query: str, operation_name: Optional[str] = None) -> OptimizationResult:
        """Otimiza uma query GraphQL"""
        # Analisa query original
        analysis = self.analyzer.analyze_query(query, operation_name)
        
        # Aplica otimizações
        optimized_query = query
        optimizations_applied = []
        suggestions = []
        
        # Otimização 1: Limitar profundidade
        if analysis.depth > self.max_depth:
            optimized_query = self._limit_depth(optimized_query, self.max_depth)
            optimizations_applied.append(OptimizationType.DEPTH_LIMIT)
            suggestions.append(f"Profundidade limitada para {self.max_depth} níveis")
        
        # Otimização 2: Seleção de campos
        if analysis.field_count > self.max_fields:
            optimized_query = self._optimize_field_selection(optimized_query)
            optimizations_applied.append(OptimizationType.FIELD_SELECTION)
            suggestions.append("Campos otimizados para melhor performance")
        
        # Otimização 3: Adicionar paginação
        if not analysis.has_pagination and analysis.field_count > 10:
            optimized_query = self._add_pagination(optimized_query)
            optimizations_applied.append(OptimizationType.PAGINATION)
            suggestions.append("Paginação adicionada automaticamente")
        
        # Calcula melhoria
        optimized_analysis = self.analyzer.analyze_query(optimized_query, operation_name)
        complexity_reduction = (analysis.complexity_score - optimized_analysis.complexity_score) / analysis.complexity_score
        estimated_improvement = (analysis.estimated_cost - optimized_analysis.estimated_cost) / analysis.estimated_cost
        
        return OptimizationResult(
            original_query=query,
            optimized_query=optimized_query,
            optimizations_applied=optimizations_applied,
            complexity_reduction=complexity_reduction,
            estimated_improvement=estimated_improvement,
            suggestions=suggestions
        )
    
    def _limit_depth(self, query: str, max_depth: int) -> str:
        """Limita profundidade da query"""
        # Implementação básica - remove campos aninhados além da profundidade máxima
        lines = query.split('\n')
        optimized_lines = []
        current_depth = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Conta chaves abertas
            if '{' in stripped:
                current_depth += 1
            
            # Adiciona linha se dentro do limite
            if current_depth <= max_depth:
                optimized_lines.append(line)
            
            # Conta chaves fechadas
            if '}' in stripped:
                current_depth -= 1
        
        return '\n'.join(optimized_lines)
    
    def _optimize_field_selection(self, query: str) -> str:
        """Otimiza seleção de campos"""
        # Identifica campos essenciais
        essential_fields = ['id', 'nome', 'status', 'data_criacao']
        
        # Adiciona comentário com sugestão
        optimized_query = f"# Otimizado: Considere selecionar apenas campos essenciais: {', '.join(essential_fields)}\n{query}"
        
        return optimized_query
    
    def _add_pagination(self, query: str) -> str:
        """Adiciona paginação à query"""
        # Adiciona argumentos de paginação
        if 'query' in query and '(' not in query.split('query')[1].split('{')[0]:
            # Query sem argumentos
            query = query.replace('query', 'query($limit: Int = 10, $offset: Int = 0)')
        
        # Adiciona campos de paginação
        if '}' in query:
            # Adiciona antes do último }
            parts = query.rsplit('}', 1)
            pagination_fields = '''
                totalCount
                hasNextPage
                hasPreviousPage
            '''
            query = parts[0] + pagination_fields + '}' + parts[1]
        
        return query
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Valida query GraphQL"""
        analysis = self.analyzer.analyze_query(query)
        
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'analysis': analysis
        }
        
        # Verifica complexidade
        if analysis.complexity_level == QueryComplexity.CRITICAL:
            validation_result['warnings'].append(
                f"Query muito complexa (score: {analysis.complexity_score}). Considere otimizar."
            )
        
        # Verifica profundidade
        if analysis.depth > self.max_depth:
            validation_result['warnings'].append(
                f"Profundidade excessiva ({analysis.depth} níveis). Máximo recomendado: {self.max_depth}"
            )
        
        # Verifica número de campos
        if analysis.field_count > self.max_fields:
            validation_result['warnings'].append(
                f"Muitos campos ({analysis.field_count}). Considere paginação ou seleção específica."
            )
        
        # Verifica sintaxe básica
        if not self._validate_syntax(query):
            validation_result['valid'] = False
            validation_result['errors'].append("Erro de sintaxe na query")
        
        return validation_result
    
    def _validate_syntax(self, query: str) -> bool:
        """Valida sintaxe básica da query"""
        # Verifica chaves balanceadas
        open_braces = query.count('{')
        close_braces = query.count('}')
        
        if open_braces != close_braces:
            return False
        
        # Verifica parênteses balanceados
        open_parens = query.count('(')
        close_parens = query.count(')')
        
        if open_parens != close_parens:
            return False
        
        return True

class GraphQLPerformanceMonitor:
    """Monitor de performance GraphQL"""
    
    def __init__(self):
        self.query_stats: Dict[str, Dict[str, Any]] = {}
        self.slow_queries: List[Dict[str, Any]] = []
        self.error_queries: List[Dict[str, Any]] = []
        self.threshold_slow = 1.0  # 1 segundo
        self.threshold_complexity = 50
    
    def record_query(self, query: str, operation_name: Optional[str], 
                    execution_time: float, complexity_score: int, 
                    success: bool, error: Optional[str] = None) -> None:
        """Registra execução de query"""
        key = operation_name or self._generate_query_key(query)
        
        # Atualiza estatísticas
        if key not in self.query_stats:
            self.query_stats[key] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'complexity_score': complexity_score,
                'last_execution': None
            }
        
        stats = self.query_stats[key]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['min_time'] = min(stats['min_time'], execution_time)
        stats['max_time'] = max(stats['max_time'], execution_time)
        stats['last_execution'] = datetime.now().isoformat()
        
        # Registra queries lentas
        if execution_time > self.threshold_slow:
            self.slow_queries.append({
                'query': query,
                'operation_name': operation_name,
                'execution_time': execution_time,
                'complexity_score': complexity_score,
                'timestamp': datetime.now().isoformat()
            })
        
        # Registra queries com erro
        if not success:
            self.error_queries.append({
                'query': query,
                'operation_name': operation_name,
                'error': error,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        return {
            'total_queries': sum(stats['count'] for stats in self.query_stats.values()),
            'unique_queries': len(self.query_stats),
            'slow_queries': len(self.slow_queries),
            'error_queries': len(self.error_queries),
            'avg_execution_time': self._calculate_avg_execution_time(),
            'top_slow_queries': self._get_top_slow_queries(5),
            'query_stats': self.query_stats
        }
    
    def _generate_query_key(self, query: str) -> str:
        """Gera chave única para query"""
        import hashlib
        return hashlib.sha256(query.encode()).hexdigest()[:8]
    
    def _calculate_avg_execution_time(self) -> float:
        """Calcula tempo médio de execução"""
        if not self.query_stats:
            return 0.0
        
        total_time = sum(stats['total_time'] for stats in self.query_stats.values())
        total_count = sum(stats['count'] for stats in self.query_stats.values())
        
        return total_time / total_count if total_count > 0 else 0.0
    
    def _get_top_slow_queries(self, limit: int) -> List[Dict[str, Any]]:
        """Obtém top queries mais lentas"""
        sorted_queries = sorted(
            self.slow_queries,
            key=lambda value: value['execution_time'],
            reverse=True
        )
        
        return sorted_queries[:limit]

# Instâncias globais
graphql_analyzer = GraphQLQueryAnalyzer()
graphql_optimizer = GraphQLQueryOptimizer()
graphql_performance_monitor = GraphQLPerformanceMonitor()

def analyze_graphql_query(query: str, operation_name: Optional[str] = None) -> QueryAnalysis:
    """Função helper para análise de query"""
    return graphql_analyzer.analyze_query(query, operation_name)

def optimize_graphql_query(query: str, operation_name: Optional[str] = None) -> OptimizationResult:
    """Função helper para otimização de query"""
    return graphql_optimizer.optimize_query(query, operation_name)

def validate_graphql_query(query: str) -> Dict[str, Any]:
    """Função helper para validação de query"""
    return graphql_optimizer.validate_query(query)

def record_graphql_performance(query: str, operation_name: Optional[str], 
                             execution_time: float, complexity_score: int,
                             success: bool, error: Optional[str] = None) -> None:
    """Função helper para registrar performance"""
    graphql_performance_monitor.record_query(
        query, operation_name, execution_time, complexity_score, success, error
    )

def get_graphql_performance_report() -> Dict[str, Any]:
    """Função helper para obter relatório de performance"""
    return graphql_performance_monitor.get_performance_report() 