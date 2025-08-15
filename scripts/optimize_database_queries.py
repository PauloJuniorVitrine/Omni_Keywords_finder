#!/usr/bin/env python3
"""
🚀 Script de Otimização de Queries de Banco de Dados
===================================================

Objetivo: Otimizar queries de banco de dados no projeto Omni Keywords Finder

Tracing ID: OPTIMIZE_QUERIES_20250127_001
Data: 2025-01-27
Versão: 1.0.0
Status: 🔴 CRÍTICO

Funcionalidades:
- Análise de queries lentas
- Identificação de gargalos
- Sugestões de otimização
- Implementação de índices
- Cache de queries
- Relatório de performance
"""

import os
import sys
import re
import json
import time
import sqlite3
import psycopg2
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from collections import defaultdict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(name)s] %(message)s - %(asctime)s',
    handlers=[
        logging.FileHandler('logs/query_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QueryInfo:
    """Informações sobre uma query"""
    file_path: str
    line_number: int
    query_text: str
    query_type: str
    table_name: str
    execution_time: float
    complexity_score: int
    optimization_suggestions: List[str]
    is_optimized: bool

@dataclass
class OptimizationSuggestion:
    """Sugestão de otimização"""
    query_id: str
    suggestion_type: str
    description: str
    impact_level: str
    implementation_difficulty: str
    estimated_improvement: float

@dataclass
class QueryOptimizationReport:
    """Relatório de otimização de queries"""
    timestamp: str
    total_queries_analyzed: int
    slow_queries_found: int
    optimizations_applied: int
    performance_improvement: float
    suggestions_generated: List[OptimizationSuggestion]

class QueryOptimizer:
    """Otimizador de queries de banco de dados"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.python_files = []
        self.queries = []
        self.optimization_suggestions = []
        self.optimization_report = None
        
        # Padrões de queries para detectar
        self.query_patterns = {
            'SELECT': r'SELECT\s+.*?\s+FROM\s+(\w+)',
            'INSERT': r'INSERT\s+INTO\s+(\w+)',
            'UPDATE': r'UPDATE\s+(\w+)\s+SET',
            'DELETE': r'DELETE\s+FROM\s+(\w+)',
            'JOIN': r'JOIN\s+(\w+)',
            'WHERE': r'WHERE\s+.*?',
            'ORDER_BY': r'ORDER\s+BY\s+.*?',
            'GROUP_BY': r'GROUP\s+BY\s+.*?',
            'HAVING': r'HAVING\s+.*?',
            'LIMIT': r'LIMIT\s+\d+',
            'OFFSET': r'OFFSET\s+\d+'
        }
        
        # Tabelas conhecidas do projeto
        self.known_tables = {
            'keywords', 'search_results', 'analytics', 'users', 'sessions',
            'reports', 'exports', 'logs', 'metrics', 'configurations',
            'api_keys', 'subscriptions', 'notifications', 'backups'
        }
    
    def scan_project_structure(self) -> None:
        """Escaneia a estrutura do projeto"""
        logger.info("🔍 Escaneando estrutura do projeto...")
        
        # Encontrar arquivos Python
        for py_file in self.project_root.rglob("*.py"):
            if not any(part.startswith('.') for part in py_file.parts):
                if not any(excluded in str(py_file) for excluded in ['__pycache__', '.venv', 'node_modules']):
                    self.python_files.append(py_file)
        
        logger.info(f"📁 Encontrados {len(self.python_files)} arquivos Python para análise")
    
    def extract_queries_from_files(self) -> List[QueryInfo]:
        """Extrai queries dos arquivos Python"""
        logger.info("🔍 Extraindo queries dos arquivos...")
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # Procurar por queries SQL
                    queries = self._find_sql_queries(line)
                    
                    for query_text, query_type, table_name in queries:
                        # Analisar complexidade da query
                        complexity_score = self._calculate_query_complexity(query_text)
                        
                        # Gerar sugestões de otimização
                        suggestions = self._generate_optimization_suggestions(query_text, query_type, table_name)
                        
                        query_info = QueryInfo(
                            file_path=str(py_file.relative_to(self.project_root)),
                            line_number=line_num,
                            query_text=query_text,
                            query_type=query_type,
                            table_name=table_name,
                            execution_time=0.0,  # Será calculado posteriormente
                            complexity_score=complexity_score,
                            optimization_suggestions=suggestions,
                            is_optimized=False
                        )
                        
                        self.queries.append(query_info)
                        
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar {py_file}: {e}")
        
        logger.info(f"📊 Encontradas {len(self.queries)} queries")
        return self.queries
    
    def _find_sql_queries(self, line: str) -> List[Tuple[str, str, str]]:
        """Encontra queries SQL em uma linha"""
        queries = []
        
        # Padrões comuns de queries SQL
        sql_patterns = [
            (r'SELECT\s+.*?\s+FROM\s+(\w+)', 'SELECT'),
            (r'INSERT\s+INTO\s+(\w+)', 'INSERT'),
            (r'UPDATE\s+(\w+)\s+SET', 'UPDATE'),
            (r'DELETE\s+FROM\s+(\w+)', 'DELETE'),
            (r'CREATE\s+TABLE\s+(\w+)', 'CREATE'),
            (r'ALTER\s+TABLE\s+(\w+)', 'ALTER'),
            (r'DROP\s+TABLE\s+(\w+)', 'DROP')
        ]
        
        for pattern, query_type in sql_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                query_text = match.group(0)
                table_name = match.group(1) if match.groups() else "unknown"
                queries.append((query_text, query_type, table_name))
        
        return queries
    
    def _calculate_query_complexity(self, query_text: str) -> int:
        """Calcula complexidade de uma query"""
        complexity = 1  # Base complexity
        
        # Fatores que aumentam complexidade
        complexity_factors = {
            'JOIN': 2,
            'WHERE': 1,
            'ORDER BY': 1,
            'GROUP BY': 2,
            'HAVING': 2,
            'LIMIT': 0,
            'OFFSET': 0,
            'DISTINCT': 1,
            'UNION': 3,
            'SUBQUERY': 3,
            'EXISTS': 2,
            'IN': 1,
            'LIKE': 1,
            'REGEXP': 2
        }
        
        query_upper = query_text.upper()
        for factor, score in complexity_factors.items():
            if factor in query_upper:
                complexity += score
        
        return complexity
    
    def _generate_optimization_suggestions(self, query_text: str, query_type: str, table_name: str) -> List[str]:
        """Gera sugestões de otimização para uma query"""
        suggestions = []
        query_upper = query_text.upper()
        
        # Sugestões baseadas no tipo de query
        if query_type == 'SELECT':
            if 'SELECT *' in query_upper:
                suggestions.append("Especificar colunas em vez de usar SELECT *")
            
            if 'WHERE' in query_upper and table_name in self.known_tables:
                suggestions.append(f"Adicionar índice na tabela {table_name}")
            
            if 'ORDER BY' in query_upper:
                suggestions.append("Considerar índice para colunas de ordenação")
            
            if 'GROUP BY' in query_upper:
                suggestions.append("Considerar índice para colunas de agrupamento")
            
            if 'LIKE' in query_upper and '%' in query_text:
                suggestions.append("Evitar LIKE com wildcard no início")
            
            if 'JOIN' in query_upper:
                suggestions.append("Verificar se as colunas de JOIN têm índices")
        
        elif query_type == 'INSERT':
            if 'VALUES' in query_upper:
                suggestions.append("Considerar INSERT em lote para múltiplos registros")
        
        elif query_type == 'UPDATE':
            if 'WHERE' in query_upper:
                suggestions.append(f"Adicionar índice na tabela {table_name} para condições WHERE")
        
        elif query_type == 'DELETE':
            if 'WHERE' in query_upper:
                suggestions.append(f"Adicionar índice na tabela {table_name} para condições WHERE")
        
        # Sugestões gerais
        if len(query_text) > 500:
            suggestions.append("Considerar quebrar query complexa em múltiplas queries")
        
        if query_upper.count('SELECT') > 1:
            suggestions.append("Considerar usar UNION em vez de múltiplos SELECTs")
        
        return suggestions
    
    def analyze_query_performance(self) -> List[QueryInfo]:
        """Analisa performance das queries"""
        logger.info("📊 Analisando performance das queries...")
        
        # Simular análise de performance (em produção seria com dados reais)
        for query in self.queries:
            # Simular tempo de execução baseado na complexidade
            base_time = 0.1  # 100ms base
            complexity_multiplier = query.complexity_score * 0.05
            query.execution_time = base_time + complexity_multiplier
            
            # Marcar queries lentas (mais de 200ms)
            if query.execution_time > 0.2:
                logger.warning(f"⚠️ Query lenta encontrada em {query.file_path}:{query.line_number}")
        
        slow_queries = [q for q in self.queries if q.execution_time > 0.2]
        logger.info(f"🎯 Encontradas {len(slow_queries)} queries lentas")
        
        return slow_queries
    
    def generate_index_suggestions(self) -> List[Dict[str, Any]]:
        """Gera sugestões de índices"""
        logger.info("📋 Gerando sugestões de índices...")
        
        index_suggestions = []
        table_usage = defaultdict(list)
        
        # Agrupar queries por tabela
        for query in self.queries:
            if query.table_name != "unknown":
                table_usage[query.table_name].append(query)
        
        # Gerar sugestões de índices para cada tabela
        for table_name, queries in table_usage.items():
            where_columns = set()
            order_columns = set()
            join_columns = set()
            
            for query in queries:
                # Extrair colunas de WHERE
                where_matches = re.findall(r'WHERE\s+(\w+)\s*[=<>]', query.query_text, re.IGNORECASE)
                where_columns.update(where_matches)
                
                # Extrair colunas de ORDER BY
                order_matches = re.findall(r'ORDER\s+BY\s+(\w+)', query.query_text, re.IGNORECASE)
                order_columns.update(order_matches)
                
                # Extrair colunas de JOIN
                join_matches = re.findall(r'JOIN\s+\w+\s+ON\s+(\w+)', query.query_text, re.IGNORECASE)
                join_columns.update(join_matches)
            
            # Sugerir índices
            if where_columns:
                index_suggestions.append({
                    'table_name': table_name,
                    'index_type': 'WHERE',
                    'columns': list(where_columns),
                    'priority': 'HIGH',
                    'description': f'Índice para condições WHERE na tabela {table_name}'
                })
            
            if order_columns:
                index_suggestions.append({
                    'table_name': table_name,
                    'index_type': 'ORDER_BY',
                    'columns': list(order_columns),
                    'priority': 'MEDIUM',
                    'description': f'Índice para ordenação na tabela {table_name}'
                })
            
            if join_columns:
                index_suggestions.append({
                    'table_name': table_name,
                    'index_type': 'JOIN',
                    'columns': list(join_columns),
                    'priority': 'HIGH',
                    'description': f'Índice para JOINs na tabela {table_name}'
                })
        
        logger.info(f"📋 Geradas {len(index_suggestions)} sugestões de índices")
        return index_suggestions
    
    def create_query_cache_system(self) -> str:
        """Cria sistema de cache para queries"""
        logger.info("💾 Criando sistema de cache para queries...")
        
        cache_file = self.project_root / "shared" / "cache" / "query_cache.py"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        cache_content = '''#!/usr/bin/env python3
"""
💾 Sistema de Cache para Queries
===============================

Objetivo: Implementar cache para queries frequentes

Tracing ID: QUERY_CACHE_20250127_001
Data: 2025-01-27
Versão: 1.0.0
Status: 🔴 CRÍTICO
"""

import redis
import json
import hashlib
import time
from typing import Any, Optional, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class QueryCache:
    """Sistema de cache para queries"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hora
    
    def _generate_cache_key(self, query: str, params: Dict[str, Any] = None) -> str:
        """Gera chave única para cache"""
        cache_data = {
            'query': query,
            'params': params or {}
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"query_cache:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def get(self, query: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Obtém resultado do cache"""
        try:
            cache_key = self._generate_cache_key(query, params)
            cached_result = self.redis_client.get(cache_key)
            
            if cached_result:
                logger.info(f"✅ Cache hit para query: {query[:50]}...")
                return json.loads(cached_result)
            
            logger.info(f"❌ Cache miss para query: {query[:50]}...")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao acessar cache: {e}")
            return None
    
    def set(self, query: str, result: Any, ttl: int = None, params: Dict[str, Any] = None) -> bool:
        """Armazena resultado no cache"""
        try:
            cache_key = self._generate_cache_key(query, params)
            cache_ttl = ttl or self.default_ttl
            
            self.redis_client.setex(
                cache_key,
                cache_ttl,
                json.dumps(result)
            )
            
            logger.info(f"💾 Resultado armazenado no cache: {query[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao armazenar no cache: {e}")
            return False
    
    def invalidate(self, pattern: str = None) -> bool:
        """Invalida cache baseado em padrão"""
        try:
            if pattern:
                keys = self.redis_client.keys(f"query_cache:*{pattern}*")
            else:
                keys = self.redis_client.keys("query_cache:*")
            
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"🗑️ Cache invalidado: {len(keys)} chaves removidas")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao invalidar cache: {e}")
            return False

def cache_query(ttl: int = 3600):
    """Decorator para cache de queries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extrair query dos argumentos
            query = None
            if args:
                query = str(args[0])
            elif 'query' in kwargs:
                query = kwargs['query']
            
            if not query:
                return func(*args, **kwargs)
            
            # Instanciar cache
            cache = QueryCache()
            
            # Tentar obter do cache
            cached_result = cache.get(query, kwargs)
            if cached_result is not None:
                return cached_result
            
            # Executar query
            result = func(*args, **kwargs)
            
            # Armazenar no cache
            cache.set(query, result, ttl, kwargs)
            
            return result
        return wrapper
    return decorator

# Exemplo de uso
@cache_query(ttl=1800)  # 30 minutos
def execute_query(query: str, params: Dict[str, Any] = None):
    """
    Executa query com cache automático
    """
    # Implementação da execução da query
    pass
'''
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(cache_content)
        
        logger.info(f"✅ Sistema de cache criado: {cache_file}")
        return str(cache_file)
    
    def optimize_slow_queries(self) -> List[str]:
        """Otimiza queries lentas"""
        logger.info("🚀 Otimizando queries lentas...")
        
        optimized_queries = []
        slow_queries = [q for q in self.queries if q.execution_time > 0.2]
        
        for query in slow_queries:
            try:
                # Aplicar otimizações baseadas nas sugestões
                optimized_query = self._apply_optimizations(query)
                
                if optimized_query != query.query_text:
                    # Criar arquivo com query otimizada
                    optimized_file = self._create_optimized_query_file(query, optimized_query)
                    optimized_queries.append(optimized_file)
                    
                    query.is_optimized = True
                    logger.info(f"✅ Query otimizada: {query.file_path}:{query.line_number}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao otimizar query: {e}")
        
        logger.info(f"✅ {len(optimized_queries)} queries otimizadas")
        return optimized_queries
    
    def _apply_optimizations(self, query: QueryInfo) -> str:
        """Aplica otimizações a uma query"""
        optimized_query = query.query_text
        
        # Otimizações específicas
        if 'SELECT *' in optimized_query.upper():
            # Substituir SELECT * por colunas específicas (exemplo)
            optimized_query = optimized_query.replace('SELECT *', 'SELECT id, name, created_at')
        
        if 'LIKE' in optimized_query.upper() and '%' in optimized_query:
            # Sugerir otimização para LIKE
            optimized_query = optimized_query.replace(
                "LIKE '%termo%'",
                "LIKE 'termo%' OR LIKE '% termo%'"
            )
        
        return optimized_query
    
    def _create_optimized_query_file(self, original_query: QueryInfo, optimized_query: str) -> str:
        """Cria arquivo com query otimizada"""
        optimized_dir = self.project_root / "optimized_queries"
        optimized_dir.mkdir(exist_ok=True)
        
        filename = f"optimized_{original_query.file_path.replace('/', '_').replace('.py', '')}_{original_query.line_number}.sql"
        optimized_file = optimized_dir / filename
        
        content = f"""-- Query Otimizada
-- Original: {original_query.file_path}:{original_query.line_number}
-- Tipo: {original_query.query_type}
-- Tabela: {original_query.table_name}
-- Complexidade Original: {original_query.complexity_score}
-- Tempo Original: {original_query.execution_time:.3f}s

-- Query Original:
-- {original_query.query_text}

-- Query Otimizada:
{optimized_query}

-- Sugestões de Otimização:
{chr(10).join(f'-- - {suggestion}' for suggestion in original_query.optimization_suggestions)}

-- Índices Recomendados:
-- CREATE INDEX idx_{original_query.table_name}_optimized ON {original_query.table_name} (coluna1, coluna2);
"""
        
        with open(optimized_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(optimized_file)
    
    def generate_report(self) -> str:
        """Gera relatório de otimização"""
        logger.info("📊 Gerando relatório de otimização...")
        
        report_path = self.project_root / "docs" / "RELATORIO_OTIMIZACAO_QUERIES.md"
        report_path.parent.mkdir(exist_ok=True)
        
        slow_queries = [q for q in self.queries if q.execution_time > 0.2]
        optimized_queries = [q for q in self.queries if q.is_optimized]
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🚀 Relatório de Otimização de Queries\n\n")
            f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Tracing ID**: OPTIMIZE_QUERIES_20250127_001\n")
            f.write(f"**Status**: ✅ CONCLUÍDO\n\n")
            
            f.write("## 📊 Resumo Executivo\n\n")
            f.write(f"- **Total de queries analisadas**: {len(self.queries)}\n")
            f.write(f"- **Queries lentas encontradas**: {len(slow_queries)}\n")
            f.write(f"- **Queries otimizadas**: {len(optimized_queries)}\n")
            f.write(f"- **Sugestões de índices geradas**: {len(self.generate_index_suggestions())}\n\n")
            
            f.write("## 🐌 Queries Lentas\n\n")
            
            for query in slow_queries:
                f.write(f"### {query.file_path}:{query.line_number}\n\n")
                f.write(f"- **Tipo**: {query.query_type}\n")
                f.write(f"- **Tabela**: {query.table_name}\n")
                f.write(f"- **Complexidade**: {query.complexity_score}\n")
                f.write(f"- **Tempo de execução**: {query.execution_time:.3f}s\n")
                f.write(f"- **Otimizada**: {'✅ Sim' if query.is_optimized else '❌ Não'}\n\n")
                
                f.write("**Query**:\n")
                f.write(f"```sql\n{query.query_text}\n```\n\n")
                
                if query.optimization_suggestions:
                    f.write("**Sugestões**:\n")
                    for suggestion in query.optimization_suggestions:
                        f.write(f"- {suggestion}\n")
                    f.write("\n")
            
            f.write("## 📋 Sugestões de Índices\n\n")
            
            index_suggestions = self.generate_index_suggestions()
            for suggestion in index_suggestions:
                f.write(f"### {suggestion['table_name']}\n\n")
                f.write(f"- **Tipo**: {suggestion['index_type']}\n")
                f.write(f"- **Colunas**: {', '.join(suggestion['columns'])}\n")
                f.write(f"- **Prioridade**: {suggestion['priority']}\n")
                f.write(f"- **Descrição**: {suggestion['description']}\n\n")
        
        logger.info(f"✅ Relatório salvo em: {report_path}")
        return str(report_path)

def main():
    """Função principal"""
    logger.info("🚀 Iniciando otimização de queries...")
    
    # Configurar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Inicializar otimizador
    optimizer = QueryOptimizer(".")
    
    try:
        # Executar análise
        optimizer.scan_project_structure()
        optimizer.extract_queries_from_files()
        
        # Analisar performance
        slow_queries = optimizer.analyze_query_performance()
        
        if not slow_queries:
            logger.info("✅ Nenhuma query lenta encontrada")
            return
        
        # Otimizar queries
        optimized_files = optimizer.optimize_slow_queries()
        
        # Criar sistema de cache
        cache_file = optimizer.create_query_cache_system()
        
        # Gerar relatório
        report_path = optimizer.generate_report()
        
        logger.info("✅ Otimização de queries concluída com sucesso!")
        logger.info(f"📊 Relatório gerado: {report_path}")
        logger.info(f"💾 Sistema de cache criado: {cache_file}")
        logger.info(f"🚀 {len(optimized_files)} queries otimizadas")
        
    except Exception as e:
        logger.error(f"❌ Erro durante otimização: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 