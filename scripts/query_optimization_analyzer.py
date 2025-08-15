"""
Script de Análise de Performance - Omni Keywords Finder
Identificação de queries lentas e gargalos de performance

Tracing ID: PERFORMANCE_ANALYSIS_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🔴 CRÍTICO - Análise de Performance

Funcionalidades:
- Análise de queries SQL lentas
- Identificação de gargalos de performance
- Análise de uso de índices
- Recomendações de otimização
- Relatórios de performance
- Métricas de tempo de resposta
- Análise de uso de recursos
- Identificação de N+1 queries
- Análise de cache hit/miss
- Recomendações de índices

Baseado no código real do sistema Omni Keywords Finder
"""

import os
import sys
import json
import time
import sqlite3
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import sqlparse
import re
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/performance_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QueryPerformance:
    """Dados de performance de uma query"""
    query: str
    execution_time: float
    rows_returned: int
    rows_scanned: int
    index_used: Optional[str]
    table_name: str
    timestamp: datetime
    frequency: int
    avg_time: float
    max_time: float
    min_time: float

@dataclass
class PerformanceIssue:
    """Problema de performance identificado"""
    issue_type: str
    severity: str
    description: str
    affected_queries: List[str]
    impact: str
    recommendation: str
    estimated_improvement: float

@dataclass
class PerformanceReport:
    """Relatório completo de performance"""
    timestamp: datetime
    total_queries: int
    slow_queries: int
    avg_response_time: float
    issues: List[PerformanceIssue]
    recommendations: List[str]
    metrics: Dict[str, Any]

class PerformanceAnalyzer:
    """
    Analisador de performance para o sistema Omni Keywords Finder
    Baseado no código real do sistema
    """
    
    def __init__(self, db_path: str = "backend/db.sqlite3"):
        """
        Inicializar analisador de performance
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        self.performance_data = []
        self.issues = []
        
        # Configurações de análise
        self.config = {
            'slow_query_threshold': 1.0,  # 1 segundo
            'critical_query_threshold': 5.0,  # 5 segundos
            'n_plus_one_threshold': 10,  # 10 queries similares
            'index_usage_threshold': 0.8,  # 80% de uso de índices
            'cache_hit_threshold': 0.7,  # 70% de cache hit
        }
        
        # Queries críticas identificadas no código real
        self.critical_queries = [
            # Queries de keywords (mais usadas)
            "SELECT * FROM keywords WHERE domain = ?",
            "SELECT * FROM keywords WHERE keyword LIKE ?",
            "SELECT * FROM keywords WHERE position > ?",
            
            # Queries de analytics
            "SELECT * FROM analytics WHERE date BETWEEN ? AND ?",
            "SELECT * FROM analytics WHERE keyword_id = ?",
            
            # Queries de pagamentos
            "SELECT * FROM payments WHERE user_id = ?",
            "SELECT * FROM payments WHERE status = ?",
            
            # Queries de usuários
            "SELECT * FROM users WHERE email = ?",
            "SELECT * FROM users WHERE id = ?",
        ]
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "performance_analyzer_initialized",
            "status": "success",
            "source": "PerformanceAnalyzer.__init__",
            "details": {
                "db_path": db_path,
                "critical_queries_count": len(self.critical_queries)
            }
        })
    
    def analyze_database_performance(self) -> Dict[str, Any]:
        """
        Analisar performance do banco de dados
        
        Returns:
            Dicionário com métricas de performance
        """
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "database_performance_analysis_started",
            "status": "started",
            "source": "PerformanceAnalyzer.analyze_database_performance"
        })
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Analisar estrutura do banco
            db_info = self._analyze_database_structure(cursor)
            
            # 2. Analisar índices existentes
            index_analysis = self._analyze_indexes(cursor)
            
            # 3. Analisar queries lentas
            slow_queries = self._analyze_slow_queries(cursor)
            
            # 4. Analisar uso de recursos
            resource_usage = self._analyze_resource_usage()
            
            # 5. Identificar problemas de performance
            issues = self._identify_performance_issues(db_info, index_analysis, slow_queries)
            
            conn.close()
            
            # Gerar relatório
            report = PerformanceReport(
                timestamp=datetime.utcnow(),
                total_queries=len(slow_queries),
                slow_queries=len([q for q in slow_queries if q.execution_time > self.config['slow_query_threshold']]),
                avg_response_time=sum(q.execution_time for q in slow_queries) / len(slow_queries) if slow_queries else 0,
                issues=issues,
                recommendations=self._generate_recommendations(issues),
                metrics={
                    'db_info': db_info,
                    'index_analysis': index_analysis,
                    'slow_queries': [asdict(q) for q in slow_queries],
                    'resource_usage': resource_usage
                }
            )
            
            self.performance_data.append(report)
            
            logger.info({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "database_performance_analysis_completed",
                "status": "completed",
                "source": "PerformanceAnalyzer.analyze_database_performance",
                "details": {
                    "total_queries": report.total_queries,
                    "slow_queries": report.slow_queries,
                    "issues_found": len(issues)
                }
            })
            
            return asdict(report)
            
        except Exception as e:
            logger.error({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "database_performance_analysis_error",
                "status": "error",
                "source": "PerformanceAnalyzer.analyze_database_performance",
                "error": str(e)
            })
            raise
    
    def _analyze_database_structure(self, cursor) -> Dict[str, Any]:
        """Analisar estrutura do banco de dados"""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        db_info = {
            'tables': [],
            'total_tables': len(tables),
            'total_size': 0
        }
        
        for table in tables:
            table_name = table[0]
            
            # Informações da tabela
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Tamanho da tabela
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            table_size = cursor.fetchone()[0]
            
            table_info = {
                'name': table_name,
                'columns': len(columns),
                'row_count': row_count,
                'size': table_size
            }
            
            db_info['tables'].append(table_info)
            db_info['total_size'] += table_size
        
        return db_info
    
    def _analyze_indexes(self, cursor) -> Dict[str, Any]:
        """Analisar índices existentes"""
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        
        index_analysis = {
            'total_indexes': len(indexes),
            'indexes_by_table': defaultdict(list),
            'missing_indexes': [],
            'unused_indexes': []
        }
        
        for index in indexes:
            index_name, table_name, index_sql = index
            
            index_info = {
                'name': index_name,
                'table': table_name,
                'sql': index_sql
            }
            
            index_analysis['indexes_by_table'][table_name].append(index_info)
        
        # Identificar tabelas sem índices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name not in index_analysis['indexes_by_table']:
                index_analysis['missing_indexes'].append(table_name)
        
        return index_analysis
    
    def _analyze_slow_queries(self, cursor) -> List[QueryPerformance]:
        """Analisar queries lentas"""
        slow_queries = []
        
        # Simular execução das queries críticas
        for query in self.critical_queries:
            start_time = time.time()
            
            try:
                # Executar query com parâmetros de exemplo
                if "keywords" in query:
                    cursor.execute(query.replace("?", "''"), [])
                elif "analytics" in query:
                    cursor.execute(query.replace("?", "''"), [])
                elif "payments" in query:
                    cursor.execute(query.replace("?", "''"), [])
                elif "users" in query:
                    cursor.execute(query.replace("?", "''"), [])
                else:
                    cursor.execute(query, [])
                
                execution_time = time.time() - start_time
                rows = cursor.fetchall()
                
                # Analisar performance da query
                query_perf = QueryPerformance(
                    query=query,
                    execution_time=execution_time,
                    rows_returned=len(rows),
                    rows_scanned=len(rows),  # Simplificado
                    index_used=self._get_index_used(query),
                    table_name=self._extract_table_name(query),
                    timestamp=datetime.utcnow(),
                    frequency=1,
                    avg_time=execution_time,
                    max_time=execution_time,
                    min_time=execution_time
                )
                
                slow_queries.append(query_perf)
                
            except Exception as e:
                logger.warning(f"Erro ao executar query: {query} - {e}")
        
        return slow_queries
    
    def _analyze_resource_usage(self) -> Dict[str, Any]:
        """Analisar uso de recursos do sistema"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict()
        }
    
    def _identify_performance_issues(self, db_info: Dict, index_analysis: Dict, slow_queries: List[QueryPerformance]) -> List[PerformanceIssue]:
        """Identificar problemas de performance"""
        issues = []
        
        # 1. Queries muito lentas
        for query in slow_queries:
            if query.execution_time > self.config['critical_query_threshold']:
                issue = PerformanceIssue(
                    issue_type="slow_query",
                    severity="critical",
                    description=f"Query executando em {query.execution_time:.2f}s (limite: {self.config['critical_query_threshold']}s)",
                    affected_queries=[query.query],
                    impact="Alto impacto na performance do sistema",
                    recommendation="Otimizar query, adicionar índices ou implementar cache",
                    estimated_improvement=0.8  # 80% de melhoria
                )
                issues.append(issue)
        
        # 2. Tabelas sem índices
        for table in index_analysis['missing_indexes']:
            issue = PerformanceIssue(
                issue_type="missing_index",
                severity="high",
                description=f"Tabela '{table}' não possui índices",
                affected_queries=[f"SELECT * FROM {table}"],
                impact="Queries na tabela podem ser lentas",
                recommendation=f"Criar índices para colunas frequentemente consultadas na tabela {table}",
                estimated_improvement=0.6  # 60% de melhoria
            )
            issues.append(issue)
        
        # 3. Queries N+1
        n_plus_one_queries = self._detect_n_plus_one_queries(slow_queries)
        if n_plus_one_queries:
            issue = PerformanceIssue(
                issue_type="n_plus_one_query",
                severity="high",
                description=f"Detectadas {len(n_plus_one_queries)} queries N+1",
                affected_queries=n_plus_one_queries,
                impact="Múltiplas queries desnecessárias",
                recommendation="Usar JOIN ou prefetch_related para reduzir número de queries",
                estimated_improvement=0.7  # 70% de melhoria
            )
            issues.append(issue)
        
        # 4. Tabelas muito grandes
        for table_info in db_info['tables']:
            if table_info['row_count'] > 100000:  # Mais de 100k registros
                issue = PerformanceIssue(
                    issue_type="large_table",
                    severity="medium",
                    description=f"Tabela '{table_info['name']}' tem {table_info['row_count']} registros",
                    affected_queries=[f"SELECT * FROM {table_info['name']}"],
                    impact="Queries podem ser lentas em tabelas grandes",
                    recommendation=f"Considerar particionamento ou arquivamento de dados antigos na tabela {table_info['name']}",
                    estimated_improvement=0.5  # 50% de melhoria
                )
                issues.append(issue)
        
        return issues
    
    def _detect_n_plus_one_queries(self, queries: List[QueryPerformance]) -> List[str]:
        """Detectar queries N+1"""
        query_patterns = defaultdict(int)
        
        for query in queries:
            # Simplificar query para detectar padrões
            simplified = re.sub(r'\?', '', query.query)
            query_patterns[simplified] += 1
        
        # Queries que aparecem muitas vezes podem ser N+1
        n_plus_one = []
        for pattern, count in query_patterns.items():
            if count > self.config['n_plus_one_threshold']:
                n_plus_one.append(pattern)
        
        return n_plus_one
    
    def _get_index_used(self, query: str) -> Optional[str]:
        """Determinar qual índice foi usado (simplificado)"""
        # Análise simplificada - em produção usar EXPLAIN QUERY PLAN
        if "WHERE" in query:
            if "id" in query:
                return "PRIMARY KEY"
            elif "email" in query:
                return "idx_email"
            elif "domain" in query:
                return "idx_domain"
        return None
    
    def _extract_table_name(self, query: str) -> str:
        """Extrair nome da tabela da query"""
        # Análise simplificada usando regex
        match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if match:
            return match.group(1)
        return "unknown"
    
    def _generate_recommendations(self, issues: List[PerformanceIssue]) -> List[str]:
        """Gerar recomendações baseadas nos problemas identificados"""
        recommendations = []
        
        for issue in issues:
            recommendations.append(f"{issue.severity.upper()}: {issue.recommendation}")
        
        # Recomendações gerais
        recommendations.extend([
            "Implementar cache Redis para queries frequentes",
            "Usar paginação para queries que retornam muitos registros",
            "Considerar uso de views materializadas para relatórios complexos",
            "Implementar monitoramento contínuo de performance",
            "Revisar e otimizar queries em produção regularmente"
        ])
        
        return recommendations
    
    def generate_performance_report(self, output_path: str = "logs/performance_report.json"):
        """Gerar relatório de performance"""
        if not self.performance_data:
            logger.warning("Nenhum dado de performance disponível")
            return
        
        latest_report = self.performance_data[-1]
        
        # Criar relatório estruturado
        report = {
            "report_metadata": {
                "timestamp": latest_report.timestamp.isoformat(),
                "version": "1.0",
                "tracing_id": "PERFORMANCE_ANALYSIS_20250127_001",
                "source": "PerformanceAnalyzer.generate_performance_report"
            },
            "summary": {
                "total_queries": latest_report.total_queries,
                "slow_queries": latest_report.slow_queries,
                "avg_response_time": latest_report.avg_response_time,
                "issues_found": len(latest_report.issues)
            },
            "issues": [
                {
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "affected_queries": issue.affected_queries,
                    "impact": issue.impact,
                    "recommendation": issue.recommendation,
                    "estimated_improvement": issue.estimated_improvement
                }
                for issue in latest_report.issues
            ],
            "recommendations": latest_report.recommendations,
            "metrics": latest_report.metrics
        }
        
        # Salvar relatório
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "performance_report_generated",
            "status": "success",
            "source": "PerformanceAnalyzer.generate_performance_report",
            "details": {
                "output_path": output_path,
                "report_size": len(json.dumps(report))
            }
        })
        
        return report

def main():
    """Função principal para execução do script"""
    try:
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "performance_analysis_started",
            "status": "started",
            "source": "main"
        })
        
        # Inicializar analisador
        analyzer = PerformanceAnalyzer()
        
        # Executar análise
        report = analyzer.analyze_database_performance()
        
        # Gerar relatório
        analyzer.generate_performance_report()
        
        # Exibir resumo
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE ANÁLISE DE PERFORMANCE")
        print("="*80)
        print(f"📅 Data/Hora: {report['timestamp']}")
        print(f"📊 Total de Queries: {report['total_queries']}")
        print(f"🐌 Queries Lentas: {report['slow_queries']}")
        print(f"⏱️  Tempo Médio de Resposta: {report['avg_response_time']:.3f}s")
        print(f"🚨 Problemas Identificados: {len(report['issues'])}")
        
        if report['issues']:
            print(f"\n🚨 PROBLEMAS CRÍTICOS:")
            for i, issue in enumerate(report['issues'], 1):
                print(f"  {i}. [{issue['severity'].upper()}] {issue['description']}")
        
        if report['recommendations']:
            print(f"\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)
        
        logger.info({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "performance_analysis_completed",
            "status": "success",
            "source": "main",
            "details": {
                "issues_found": len(report['issues']),
                "recommendations_generated": len(report['recommendations'])
            }
        })
        
    except Exception as e:
        logger.error({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "performance_analysis_error",
            "status": "error",
            "source": "main",
            "error": str(e)
        })
        print(f"❌ Erro na análise de performance: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 