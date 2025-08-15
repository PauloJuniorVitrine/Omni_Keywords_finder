from typing import Dict, List, Optional, Any
"""
Testes Unitários para Mutation Testing Runner
Tracing ID: TEST-001
Data: 2024-12-20
Versão: 1.0
"""

import pytest
import ast
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from tests.mutation.mutation_runner import (
    MutationRunner,
    MutationOperator,
    MutationVisitor,
    MutationResult,
    MutationReport
)


class TestMutationOperator:
    """Testes para operadores de mutação"""
    
    def test_change_http_method_get_to_post(self):
        """Testa mudança de método HTTP GET para POST"""
        operator = MutationOperator()
        
        # Cria AST para requests.get()
        code = "requests.get('https://api.example.com')"
        tree = ast.parse(code)
        node = tree.body[0].value
        
        mutations = operator.change_http_method(node)
        
        assert len(mutations) > 0
        assert any(isinstance(mut, ast.Call) for mut in mutations)
        assert any(hasattr(mut.func, 'attr') and mut.func.attr == 'post' for mut in mutations)
    
    def test_change_http_method_post_to_put(self):
        """Testa mudança de método HTTP POST para PUT"""
        operator = MutationOperator()
        
        code = "requests.post('https://api.example.com', json=data)"
        tree = ast.parse(code)
        node = tree.body[0].value
        
        mutations = operator.change_http_method(node)
        
        assert len(mutations) > 0
        assert any(hasattr(mut.func, 'attr') and mut.func.attr == 'put' for mut in mutations)
    
    def test_change_status_code_check_200_to_404(self):
        """Testa mudança de verificação de status code"""
        operator = MutationOperator()
        
        code = "response.status_code == 200"
        tree = ast.parse(code)
        node = tree.body[0].value
        
        mutations = operator.change_status_code_check(node)
        
        assert len(mutations) > 0
        assert any(mut.comparators[0].value == 404 for mut in mutations)
    
    def test_change_timeout_value(self):
        """Testa mudança de valores de timeout"""
        operator = MutationOperator()
        
        code = "timeout=30"
        tree = ast.parse(code)
        node = tree.body[0].value
        
        mutations = operator.change_timeout_value(node)
        
        assert len(mutations) > 0
        assert any(mut.value == 0 for mut in mutations)
        assert any(mut.value == 60 for mut in mutations)
    
    def test_change_retry_count(self):
        """Testa mudança de contadores de retry"""
        operator = MutationOperator()
        
        code = "retries=3"
        tree = ast.parse(code)
        node = tree.body[0].value
        
        mutations = operator.change_retry_count(node)
        
        assert len(mutations) > 0
        assert any(mut.value == 0 for mut in mutations)
        assert any(mut.value == 10 for mut in mutations)
    
    def test_change_api_endpoint(self):
        """Testa mudança de endpoints de API"""
        operator = MutationOperator()
        
        code = "'https://api.example.com/endpoint'"
        tree = ast.parse(code)
        node = tree.body[0].value
        
        mutations = operator.change_api_endpoint(node)
        
        assert len(mutations) > 0
        assert any('invalid-api.com' in mut.value for mut in mutations)


class TestMutationVisitor:
    """Testes para visitor de mutação"""
    
    def test_visitor_identifies_http_calls(self):
        """Testa se visitor identifica chamadas HTTP"""
        operator = MutationOperator()
        visitor = MutationVisitor(operator)
        
        code = """
        import requests
        response = requests.get('https://api.example.com')
        if response.status_code == 200:
            return response.json()
        """
        tree = ast.parse(code)
        
        visitor.visit(tree)
        
        assert len(visitor.mutations) > 0
        assert any('MUT_' in mut['id'] for mut in visitor.mutations)
    
    def test_visitor_identifies_status_checks(self):
        """Testa se visitor identifica verificações de status"""
        operator = MutationOperator()
        visitor = MutationVisitor(operator)
        
        code = "if response.status_code == 200: pass"
        tree = ast.parse(code)
        
        visitor.visit(tree)
        
        assert len(visitor.mutations) > 0
    
    def test_visitor_identifies_timeouts(self):
        """Testa se visitor identifica timeouts"""
        operator = MutationOperator()
        visitor = MutationVisitor(operator)
        
        code = "requests.get(url, timeout=30)"
        tree = ast.parse(code)
        
        visitor.visit(tree)
        
        assert len(visitor.mutations) > 0


class TestMutationResult:
    """Testes para resultados de mutação"""
    
    def test_mutation_result_creation(self):
        """Testa criação de resultado de mutação"""
        result = MutationResult(
            mutation_id="MUT_0001",
            original_code="requests.get(url)",
            mutated_code="requests.post(url)",
            test_result=False,
            killed=True,
            execution_time=1.5
        )
        
        assert result.mutation_id == "MUT_0001"
        assert result.killed is True
        assert result.execution_time == 1.5
    
    def test_mutation_result_with_error(self):
        """Testa resultado de mutação com erro"""
        result = MutationResult(
            mutation_id="MUT_0002",
            original_code="requests.get(url)",
            mutated_code="requests.invalid(url)",
            test_result=False,
            killed=False,
            execution_time=0.5,
            error_message="AttributeError: 'Session' object has no attribute 'invalid'"
        )
        
        assert result.error_message is not None
        assert "AttributeError" in result.error_message


class TestMutationReport:
    """Testes para relatórios de mutação"""
    
    def test_mutation_report_creation(self):
        """Testa criação de relatório de mutação"""
        results = [
            MutationResult("MUT_0001", "code1", "mut1", False, True, 1.0),
            MutationResult("MUT_0002", "code2", "mut2", True, False, 1.5)
        ]
        
        report = MutationReport(
            total_mutations=2,
            killed_mutations=1,
            survived_mutations=1,
            mutation_score=0.5,
            execution_time=2.5,
            timestamp=datetime.now(),
            details=results
        )
        
        assert report.total_mutations == 2
        assert report.killed_mutations == 1
        assert report.survived_mutations == 1
        assert report.mutation_score == 0.5
        assert len(report.details) == 2
    
    def test_mutation_score_calculation(self):
        """Testa cálculo do score de mutação"""
        results = [
            MutationResult("MUT_0001", "code1", "mut1", False, True, 1.0),
            MutationResult("MUT_0002", "code2", "mut2", False, True, 1.0),
            MutationResult("MUT_0003", "code3", "mut3", True, False, 1.0)
        ]
        
        report = MutationReport(
            total_mutations=3,
            killed_mutations=2,
            survived_mutations=1,
            mutation_score=2/3,
            execution_time=3.0,
            timestamp=datetime.now(),
            details=results
        )
        
        assert report.mutation_score == 2/3
        assert report.mutation_score == 0.6666666666666666


class TestMutationRunner:
    """Testes para runner de mutação"""
    
    @patch('tests.mutation.mutation_runner.Path')
    def test_find_integration_files(self, mock_path):
        """Testa busca por arquivos de integração"""
        mock_path.return_value.parent.glob.return_value = [
            Path("infrastructure/integrations/api_client.py"),
            Path("services/external_service.py")
        ]
        
        runner = MutationRunner()
        files = runner.find_integration_files()
        
        assert len(files) == 2
        assert any("api_client.py" in str(f) for f in files)
    
    @patch('subprocess.run')
    def test_run_tests_success(self, mock_run):
        """Testa execução de testes com sucesso"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        runner = MutationRunner()
        success, time, error = runner.run_tests("test_file.py")
        
        assert success is True
        assert error == ""
    
    @patch('subprocess.run')
    def test_run_tests_failure(self, mock_run):
        """Testa execução de testes com falha"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "AssertionError"
        
        runner = MutationRunner()
        success, time, error = runner.run_tests("test_file.py")
        
        assert success is False
        assert "AssertionError" in error
    
    @patch('subprocess.run')
    def test_run_tests_timeout(self, mock_run):
        """Testa timeout na execução de testes"""
        mock_run.side_effect = subprocess.TimeoutExpired("pytest", 30)
        
        runner = MutationRunner()
        success, time, error = runner.run_tests("test_file.py")
        
        assert success is False
        assert time == 30.0
        assert "timeout" in error.lower()
    
    def test_find_test_file_exact_match(self):
        """Testa busca por arquivo de teste com match exato"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "tests"
            test_dir.mkdir()
            
            # Cria arquivo de teste
            test_file = test_dir / "test_api_client.py"
            test_file.write_text("def test_something(): pass")
            
            runner = MutationRunner(test_dir=str(test_dir))
            source_file = Path("infrastructure/api_client.py")
            
            found_test = runner.find_test_file(source_file)
            
            assert found_test == test_file
    
    def test_find_test_file_subdirectory(self):
        """Testa busca por arquivo de teste em subdiretório"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "tests"
            test_dir.mkdir()
            
            # Cria subdiretório e arquivo de teste
            subdir = test_dir / "integration"
            subdir.mkdir()
            test_file = subdir / "test_api_client.py"
            test_file.write_text("def test_something(): pass")
            
            runner = MutationRunner(test_dir=str(test_dir))
            source_file = Path("infrastructure/api_client.py")
            
            found_test = runner.find_test_file(source_file)
            
            assert found_test == test_file
    
    def test_generate_mutations_for_integration_file(self):
        """Testa geração de mutações para arquivo de integração"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria arquivo de integração
            integration_file = Path(temp_dir) / "api_client.py"
            integration_file.write_text("""
import requests

def call_api(url):
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None
            """)
            
            runner = MutationRunner()
            mutations = runner.generate_mutations(integration_file)
            
            assert len(mutations) > 0
            assert any('MUT_' in mut['id'] for mut in mutations)
    
    @patch('tests.mutation.mutation_runner.MutationRunner.run_tests')
    @patch('tests.mutation.mutation_runner.MutationRunner.find_test_file')
    def test_run_mutation_testing_complete_flow(self, mock_find_test, mock_run_tests):
        """Testa fluxo completo de mutation testing"""
        # Mock do arquivo de teste
        mock_find_test.return_value = Path("test_file.py")
        
        # Mock de execução de testes (sucesso original, falha na mutação)
        mock_run_tests.side_effect = [
            (True, 1.0, ""),  # Teste original passa
            (False, 1.0, "AssertionError")  # Mutação falha (killed)
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cria arquivo de integração
            integration_file = Path(temp_dir) / "api_client.py"
            integration_file.write_text("""
import requests

def call_api(url):
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None
            """)
            
            runner = MutationRunner()
            
            # Mock para encontrar arquivos de integração
            with patch.object(runner, 'find_integration_files', return_value=[integration_file]):
                with patch.object(runner, 'generate_mutations', return_value=[{
                    'id': 'MUT_0001',
                    'node': ast.parse("requests.get(url)").body[0].value,
                    'mutation': ast.parse("requests.post(url)").body[0].value
                }]):
                    with patch.object(runner, 'create_mutation', return_value="temp_file.py"):
                        with patch('pathlib.Path.unlink'):
                            report = runner.run_mutation_testing()
            
            assert report.total_mutations > 0
            assert report.killed_mutations > 0
    
    def test_generate_report(self):
        """Testa geração de relatório"""
        with tempfile.TemporaryDirectory() as temp_dir:
            results = [
                MutationResult("MUT_0001", "code1", "mut1", False, True, 1.0),
                MutationResult("MUT_0002", "code2", "mut2", True, False, 1.5)
            ]
            
            report = MutationReport(
                total_mutations=2,
                killed_mutations=1,
                survived_mutations=1,
                mutation_score=0.5,
                execution_time=2.5,
                timestamp=datetime.now(),
                details=results
            )
            
            runner = MutationRunner()
            output_file = Path(temp_dir) / "mutation_report.json"
            
            runner.generate_report(report, str(output_file))
            
            assert output_file.exists()
            
            # Verifica conteúdo do relatório
            with open(output_file, 'r') as f:
                report_data = json.load(f)
            
            assert report_data['summary']['total_mutations'] == 2
            assert report_data['summary']['killed_mutations'] == 1
            assert report_data['summary']['mutation_score'] == 0.5
            assert len(report_data['details']) == 2


class TestMutationRunnerIntegration:
    """Testes de integração para mutation runner"""
    
    def test_mutation_operator_coverage(self):
        """Testa cobertura dos operadores de mutação"""
        operator = MutationOperator()
        
        # Testa todos os operadores com código real
        test_cases = [
            ("requests.get('https://api.example.com')", "change_http_method"),
            ("response.status_code == 200", "change_status_code_check"),
            ("timeout=30", "change_timeout_value"),
            ("retries=3", "change_retry_count"),
            ("'https://api.example.com/endpoint'", "change_api_endpoint")
        ]
        
        for code, operator_name in test_cases:
            tree = ast.parse(code)
            node = tree.body[0].value
            
            method = getattr(operator, operator_name)
            mutations = method(node)
            
            assert len(mutations) > 0, f"Operador {operator_name} não gerou mutações"
    
    def test_visitor_complete_parsing(self):
        """Testa parsing completo com visitor"""
        operator = MutationOperator()
        visitor = MutationVisitor(operator)
        
        # Código de integração real
        code = """
import requests
import time

class APIClient:
    def __init__(self, base_url, timeout=30, retries=3):
        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries
    
    def get_data(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, timeout=self.timeout)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise Exception(f"API error: {response.status_code}")
    
    def post_data(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data, timeout=self.timeout)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"API error: {response.status_code}")
        """
        
        tree = ast.parse(code)
        visitor.visit(tree)
        
        # Deve encontrar várias mutações
        assert len(visitor.mutations) > 0
        
        # Verifica tipos de mutações encontradas
        mutation_types = [type(mut['mutation']) for mut in visitor.mutations]
        assert ast.Call in mutation_types
        assert ast.Compare in mutation_types


if __name__ == "__main__":
    pytest.main([__file__, "-value"]) 