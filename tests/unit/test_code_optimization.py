"""
Testes Unitários para Otimização de Código - Omni Keywords Finder
Validação do script de otimização de código

Tracing ID: CODE_OPTIMIZATION_TESTING_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: 🔴 CRÍTICO - Testes de Otimização de Código

Baseado no código real do sistema Omni Keywords Finder
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys

# Importar o script de otimização
sys.path.append('scripts')
from code_optimization_analyzer import (
    CodeOptimizationAnalyzer,
    QueryAnalysis,
    CodeOptimization,
    OptimizationReport
)

class TestCodeOptimization:
    """
    Testes para validação da otimização de código
    Baseado no código real do sistema Omni Keywords Finder
    """
    
    @pytest.fixture
    def analyzer(self):
        """Criar instância do analisador de otimização"""
        return CodeOptimizationAnalyzer()
    
    @pytest.fixture
    def sample_code_files(self):
        """Criar arquivos de código de exemplo baseados no sistema real"""
        temp_dir = tempfile.mkdtemp()
        
        # Arquivo business_metrics_service.py (baseado no sistema real)
        business_metrics_code = '''
"""
Serviço de Métricas de Negócio - Omni Keywords Finder
"""
import sqlite3

class BusinessMetricsService:
    def get_metrics(self, metric_type, category):
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM business_metrics 
            WHERE metric_type = ? AND category = ?
            ORDER BY created_at DESC
        ''', (metric_type, category))
        return cursor.fetchall()
    
    def get_metrics_by_period(self, start_date, end_date):
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM business_metrics 
            WHERE start_date >= ? AND end_date <= ?
        ''', (start_date, end_date))
        return cursor.fetchall()
'''
        
        with open(os.path.join(temp_dir, 'business_metrics_service.py'), 'w') as f:
            f.write(business_metrics_code)
        
        # Arquivo payment_service.py (baseado no sistema real)
        payment_code = '''
"""
Serviço de Pagamentos - Omni Keywords Finder
"""
import sqlite3

class PaymentService:
    def get_payments(self, status, payment_method):
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM payments_v1 
            WHERE status = ? AND payment_method = ?
        ''', (status, payment_method))
        return cursor.fetchall()
    
    def get_payments_by_customer(self, customer_data):
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM payments_v1 
            WHERE customer_data LIKE ?
        ''', (f'%{customer_data}%',))
        return cursor.fetchall()
'''
        
        with open(os.path.join(temp_dir, 'payment_service.py'), 'w') as f:
            f.write(payment_code)
        
        # Arquivo execucao_model.py (baseado no sistema real)
        execucao_code = '''
"""
Modelo de Execução - Omni Keywords Finder
"""
from flask_sqlalchemy import SQLAlchemy

class Execucao(db.Model):
    __tablename__ = 'execucoes'
    
    id = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    status = db.Column(db.String(50))
    data_execucao = db.Column(db.DateTime)
    
    def get_by_categoria(self, categoria_id):
        return Execucao.query.filter_by(id_categoria=categoria_id).all()
    
    def get_by_status(self, status):
        return Execucao.query.filter_by(status=status).all()
'''
        
        with open(os.path.join(temp_dir, 'execucao_model.py'), 'w') as f:
            f.write(execucao_code)
        
        yield temp_dir
        
        # Limpar arquivos temporários
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_analyzer_initialization(self, analyzer):
        """Testar inicialização do analisador"""
        assert analyzer is not None
        assert len(analyzer.critical_files) > 0
        assert len(analyzer.system_queries) > 0
        assert len(analyzer.problematic_patterns) > 0
        
        # Verificar arquivos críticos
        expected_files = [
            "backend/app/services/business_metrics_service.py",
            "backend/app/services/payment_v1_service.py",
            "backend/app/models/business_metrics.py",
            "backend/app/models/user.py",
            "backend/app/models/execucao.py"
        ]
        
        for expected_file in expected_files:
            assert expected_file in analyzer.critical_files
    
    def test_query_type_detection(self, analyzer):
        """Testar detecção de tipos de query"""
        # Teste SELECT
        assert analyzer._determine_query_type("SELECT * FROM users") == "SELECT"
        assert analyzer._determine_query_type("select * from users") == "SELECT"
        
        # Teste INSERT
        assert analyzer._determine_query_type("INSERT INTO users VALUES (?)") == "INSERT"
        
        # Teste UPDATE
        assert analyzer._determine_query_type("UPDATE users SET name = ?") == "UPDATE"
        
        # Teste DELETE
        assert analyzer._determine_query_type("DELETE FROM users WHERE id = ?") == "DELETE"
        
        # Teste desconhecido
        assert analyzer._determine_query_type("CREATE TABLE users") == "UNKNOWN"
    
    def test_sql_query_extraction(self, analyzer):
        """Testar extração de queries SQL"""
        line = 'cursor.execute("SELECT * FROM users WHERE email = ?", (email,))'
        queries = analyzer._extract_sql_queries(line, 1, "test.py")
        
        assert len(queries) > 0
        assert queries[0].query_type == "SELECT"
        assert "SELECT * FROM users" in queries[0].query_text
        assert queries[0].line_number == 1
        assert queries[0].file_path == "test.py"
    
    def test_orm_query_extraction(self, analyzer):
        """Testar extração de queries ORM"""
        line = 'users = User.query.filter_by(email=email).all()'
        queries = analyzer._extract_orm_queries(line, 1, "test.py")
        
        assert len(queries) > 0
        assert queries[0].query_type == "ORM"
        assert queries[0].line_number == 1
        assert queries[0].file_path == "test.py"
    
    def test_performance_issue_detection(self, analyzer):
        """Testar detecção de problemas de performance"""
        # Criar query de teste
        query = QueryAnalysis(
            file_path="test.py",
            line_number=1,
            query_type="SELECT",
            query_text="SELECT * FROM users WHERE name LIKE '%john%' ORDER BY created_at DESC",
            context="test context",
            performance_issues=[],
            optimization_suggestions=[],
            estimated_improvement=0.0
        )
        
        # Analisar problemas
        issues = analyzer._analyze_query_performance(query)
        
        # Verificar problemas detectados
        assert len(issues) > 0
        assert any("SELECT *" in issue for issue in issues)
        assert any("LIKE com wildcard" in issue for issue in issues)
        assert any("ORDER BY sem LIMIT" in issue for issue in issues)
    
    def test_optimization_suggestions(self, analyzer):
        """Testar geração de sugestões de otimização"""
        # Criar query de teste
        query = QueryAnalysis(
            file_path="test.py",
            line_number=1,
            query_type="SELECT",
            query_text="SELECT * FROM business_metrics WHERE metric_type = ?",
            context="test context",
            performance_issues=[],
            optimization_suggestions=[],
            estimated_improvement=0.0
        )
        
        # Gerar sugestões
        suggestions = analyzer._generate_query_suggestions(query)
        
        # Verificar sugestões
        assert len(suggestions) > 0
        assert any("Especificar apenas as colunas necessárias" in suggestion for suggestion in suggestions)
        assert any("Usar índices em metric_type" in suggestion for suggestion in suggestions)
    
    def test_improvement_estimation(self, analyzer):
        """Testar estimativa de melhoria"""
        # Query com múltiplos problemas
        query = QueryAnalysis(
            file_path="test.py",
            line_number=1,
            query_type="SELECT",
            query_text="SELECT * FROM users WHERE name LIKE '%john%' ORDER BY created_at DESC",
            context="test context",
            performance_issues=[],
            optimization_suggestions=[],
            estimated_improvement=0.0
        )
        
        # Calcular melhoria
        improvement = analyzer._estimate_query_improvement(query)
        
        # Verificar que melhoria foi calculada
        assert improvement > 0.0
        assert improvement <= 0.8  # Máximo de 80%
    
    def test_file_analysis(self, analyzer, sample_code_files):
        """Testar análise de arquivo"""
        # Analisar arquivo de exemplo
        file_path = os.path.join(sample_code_files, 'business_metrics_service.py')
        queries = analyzer._analyze_file(file_path)
        
        # Verificar que queries foram encontradas
        assert len(queries) > 0
        
        # Verificar tipos de queries
        query_types = [q.query_type for q in queries]
        assert "SELECT" in query_types
    
    def test_optimization_identification(self, analyzer):
        """Testar identificação de otimizações"""
        optimizations = analyzer._identify_optimizations()
        
        # Verificar que otimizações foram identificadas
        assert len(optimizations) > 0
        
        # Verificar tipos de otimização
        optimization_types = [opt.optimization_type for opt in optimizations]
        assert "query_optimization" in optimization_types
        assert "index_optimization" in optimization_types
        
        # Verificar prioridades
        priorities = [opt.implementation_priority for opt in optimizations]
        assert "critical" in priorities
        assert "high" in priorities
    
    def test_recommendations_generation(self, analyzer):
        """Testar geração de recomendações"""
        recommendations = analyzer._generate_recommendations()
        
        # Verificar que recomendações foram geradas
        assert len(recommendations) > 0
        
        # Verificar tipos de recomendações
        expected_recommendations = [
            "Implementar cache Redis",
            "Usar paginação",
            "Adicionar índices compostos",
            "Implementar lazy loading",
            "Usar SELECT específico"
        ]
        
        for expected in expected_recommendations:
            assert any(expected.lower() in rec.lower() for rec in recommendations)
    
    def test_full_analysis(self, analyzer, sample_code_files):
        """Testar análise completa"""
        # Substituir arquivos críticos pelos de exemplo
        analyzer.critical_files = [
            os.path.join(sample_code_files, 'business_metrics_service.py'),
            os.path.join(sample_code_files, 'payment_service.py'),
            os.path.join(sample_code_files, 'execucao_model.py')
        ]
        
        # Executar análise completa
        report = analyzer.analyze_code_performance()
        
        # Verificar estrutura do relatório
        assert 'timestamp' in report
        assert 'summary' in report
        assert 'queries' in report
        assert 'optimizations' in report
        assert 'recommendations' in report
        
        # Verificar dados do resumo
        summary = report['summary']
        assert summary['files_analyzed'] > 0
        assert summary['queries_found'] >= 0
        assert summary['optimizations_identified'] > 0
        assert summary['estimated_performance_improvement'] >= 0.0
    
    def test_report_generation(self, analyzer, sample_code_files):
        """Testar geração de relatório"""
        # Substituir arquivos críticos pelos de exemplo
        analyzer.critical_files = [
            os.path.join(sample_code_files, 'business_metrics_service.py'),
            os.path.join(sample_code_files, 'payment_service.py')
        ]
        
        # Executar análise
        analyzer.analyze_code_performance()
        
        # Gerar relatório
        report_path = os.path.join(sample_code_files, 'optimization_report.json')
        report = analyzer.generate_optimization_report(report_path)
        
        # Verificar que arquivo foi criado
        assert os.path.exists(report_path)
        
        # Verificar conteúdo do relatório
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        assert 'report_metadata' in report_data
        assert 'summary' in report_data
        assert 'queries' in report_data
        assert 'optimizations' in report_data
        assert 'recommendations' in report_data
    
    def test_system_queries_analysis(self, analyzer):
        """Testar análise das queries específicas do sistema"""
        # Verificar queries do sistema
        system_queries = analyzer.system_queries
        
        # Verificar categorias
        assert "business_metrics" in system_queries
        assert "payments" in system_queries
        assert "executions" in system_queries
        assert "users" in system_queries
        
        # Verificar queries específicas
        business_queries = system_queries["business_metrics"]
        assert len(business_queries) > 0
        assert any("metric_type" in query for query in business_queries)
        assert any("category" in query for query in business_queries)
        
        payment_queries = system_queries["payments"]
        assert len(payment_queries) > 0
        assert any("status" in query for query in payment_queries)
        assert any("payment_method" in query for query in payment_queries)
    
    def test_problematic_patterns_detection(self, analyzer):
        """Testar detecção de padrões problemáticos"""
        patterns = analyzer.problematic_patterns
        
        # Verificar padrões críticos
        assert any("SELECT \\* FROM" in pattern for pattern in patterns)
        assert any("LIKE.*%" in pattern for pattern in patterns)
        assert any("ORDER BY.*DESC" in pattern for pattern in patterns)
        assert any("GROUP BY" in pattern for pattern in patterns)
        assert any("JOIN.*ON" in pattern for pattern in patterns)
    
    def test_improvement_calculation(self, analyzer):
        """Testar cálculo de melhoria estimada"""
        # Criar queries de teste com diferentes problemas
        test_queries = [
            QueryAnalysis(
                file_path="test1.py",
                line_number=1,
                query_type="SELECT",
                query_text="SELECT * FROM users",
                context="test",
                performance_issues=[],
                optimization_suggestions=[],
                estimated_improvement=0.2
            ),
            QueryAnalysis(
                file_path="test2.py",
                line_number=1,
                query_type="SELECT",
                query_text="SELECT * FROM users WHERE name LIKE '%john%'",
                context="test",
                performance_issues=[],
                optimization_suggestions=[],
                estimated_improvement=0.3
            )
        ]
        
        analyzer.queries_found = test_queries
        
        # Calcular melhoria total
        improvement = analyzer._calculate_estimated_improvement()
        
        # Verificar cálculo
        assert improvement > 0.0
        assert improvement <= 0.7  # Máximo de 70%
        assert improvement == 0.25  # Média das melhorias (0.2 + 0.3) / 2

if __name__ == "__main__":
    pytest.main([__file__]) 