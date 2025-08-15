"""
🧪 Teste de Validação Semântica

Tracing ID: SEMANTIC_VAL_2025_001
Data/Hora: 2025-01-27 20:25:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Validação semântica para garantir que testes estão testando funcionalidade real.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from unittest.mock import patch, MagicMock


class SemanticValidator:
    """
    Validador semântico para testes unitários.
    """
    
    def __init__(self):
        self.test_files: Set[str] = set()
        self.implementation_files: Set[str] = set()
        self.semantic_issues: List[Dict[str, Any]] = []
    
    def analyze_test_semantics(self, test_file: Path, impl_file: Path = None) -> Dict[str, Any]:
        """
        Analisa a semântica de um teste em relação à implementação.
        
        Args:
            test_file: Arquivo de teste
            impl_file: Arquivo de implementação (opcional)
            
        Returns:
            Relatório de análise semântica
        """
        issues = []
        
        try:
            # Analisa o arquivo de teste
            test_ast = self._parse_file(test_file)
            test_functions = self._extract_test_functions(test_ast)
            
            # Analisa o arquivo de implementação se fornecido
            impl_functions = []
            if impl_file and impl_file.exists():
                impl_ast = self._parse_file(impl_file)
                impl_functions = self._extract_implementation_functions(impl_ast)
            
            # Validações semânticas
            issues.extend(self._validate_test_data_realism(test_functions))
            issues.extend(self._validate_assertion_specificity(test_functions))
            issues.extend(self._validate_function_coverage(test_functions, impl_functions))
            issues.extend(self._validate_test_isolation(test_functions))
            
        except Exception as e:
            issues.append({
                'type': 'parsing_error',
                'severity': 'error',
                'message': f'Erro ao analisar arquivo: {str(e)}',
                'file': str(test_file)
            })
        
        return {
            'file': str(test_file),
            'total_issues': len(issues),
            'issues': issues,
            'semantic_score': self._calculate_semantic_score(issues)
        }
    
    def _parse_file(self, file_path: Path) -> ast.AST:
        """Parse um arquivo Python."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ast.parse(content)
    
    def _extract_test_functions(self, ast_tree: ast.AST) -> List[Dict[str, Any]]:
        """Extrai funções de teste do AST."""
        test_functions = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_functions.append({
                        'name': node.name,
                        'body': node.body,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
        
        return test_functions
    
    def _extract_implementation_functions(self, ast_tree: ast.AST) -> List[str]:
        """Extrai funções de implementação do AST."""
        functions = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('test_') and not node.name.startswith('_'):
                    functions.append(node.name)
        
        return functions
    
    def _validate_test_data_realism(self, test_functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida se os dados de teste são realistas."""
        issues = []
        
        for func in test_functions:
            func_code = ast.unparse(func['body'])
            
            # Verifica dados genéricos proibidos
            generic_patterns = [
                r'\'foo\'', r'"foo"',
                r'\'bar\'', r'"bar"',
                r'\'random\'', r'"random"',
                r'\'dummy\'', r'"dummy"',
                r'\'lorem\'', r'"lorem"',
                r'\'test_data\'', r'"test_data"',
                r'\'mock_data\'', r'"mock_data"'
            ]
            
            for pattern in generic_patterns:
                if re.search(pattern, func_code, re.IGNORECASE):
                    issues.append({
                        'type': 'generic_data',
                        'severity': 'error',
                        'message': f'Dados genéricos detectados em {func["name"]}',
                        'function': func['name'],
                        'line': func['lineno']
                    })
                    break
        
        return issues
    
    def _validate_assertion_specificity(self, test_functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida se as assertivas são específicas."""
        issues = []
        
        for func in test_functions:
            func_code = ast.unparse(func['body'])
            
            # Verifica assertivas genéricas
            generic_assertions = [
                r'assert\s+.*\.to(Be|Equal)\(\)',
                r'assert\s+.*==\s*[a-zA-Z_][a-zA-Z0-9_]*\s*$',
                r'assert\s+.*is\s*[a-zA-Z_][a-zA-Z0-9_]*\s*$',
                r'assert\s+.*in\s*[a-zA-Z_][a-zA-Z0-9_]*\s*$'
            ]
            
            for pattern in generic_assertions:
                if re.search(pattern, func_code):
                    issues.append({
                        'type': 'generic_assertion',
                        'severity': 'warning',
                        'message': f'Assertiva genérica detectada em {func["name"]}',
                        'function': func['name'],
                        'line': func['lineno']
                    })
        
        return issues
    
    def _validate_function_coverage(self, test_functions: List[Dict[str, Any]], impl_functions: List[str]) -> List[Dict[str, Any]]:
        """Valida cobertura de funções."""
        issues = []
        
        if not impl_functions:
            return issues
        
        # Extrai nomes de funções testadas
        tested_functions = set()
        for func in test_functions:
            func_code = ast.unparse(func['body'])
            
            # Procura por chamadas de funções da implementação
            for impl_func in impl_functions:
                if re.search(rf'\b{impl_func}\b', func_code):
                    tested_functions.add(impl_func)
        
        # Verifica funções não testadas
        untested = set(impl_functions) - tested_functions
        if untested:
            issues.append({
                'type': 'missing_coverage',
                'severity': 'warning',
                'message': f'Funções não testadas: {", ".join(untested)}',
                'untested_functions': list(untested)
            })
        
        return issues
    
    def _validate_test_isolation(self, test_functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida isolamento dos testes."""
        issues = []
        
        for func in test_functions:
            func_code = ast.unparse(func['body'])
            
            # Verifica dependências entre testes
            if re.search(r'global\s+', func_code):
                issues.append({
                    'type': 'global_dependency',
                    'severity': 'error',
                    'message': f'Uso de variável global em {func["name"]}',
                    'function': func['name'],
                    'line': func['lineno']
                })
            
            # Verifica mocks inadequados
            if re.search(r'MagicMock\(\)', func_code) and not re.search(r'assert_called', func_code):
                issues.append({
                    'type': 'unverified_mock',
                    'severity': 'warning',
                    'message': f'Mock não verificado em {func["name"]}',
                    'function': func['name'],
                    'line': func['lineno']
                })
        
        return issues
    
    def _calculate_semantic_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calcula score semântico baseado nos problemas encontrados."""
        if not issues:
            return 100.0
        
        error_count = sum(1 for issue in issues if issue['severity'] == 'error')
        warning_count = sum(1 for issue in issues if issue['severity'] == 'warning')
        
        # Penaliza mais os erros que warnings
        score = 100.0 - (error_count * 20) - (warning_count * 5)
        return max(0.0, score)


class TestSemanticValidator:
    """Testes para o validador semântico."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.validator = SemanticValidator()
    
    def test_validate_generic_data_detection(self):
        """Testa detecção de dados genéricos."""
        test_code = '''
def test_example():
    data = {'foo': 'bar', 'random': 'value'}
    result = process_data(data)
    assert result == 'expected'
'''
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = test_code
                
                result = self.validator.analyze_test_semantics(Path('test.py'))
                
                assert result['total_issues'] > 0
                assert any(issue['type'] == 'generic_data' for issue in result['issues'])
    
    def test_validate_realistic_data_acceptance(self):
        """Testa aceitação de dados realistas."""
        test_code = '''
def test_keyword_filtering():
    keywords = [
        {'termo': 'marketing digital', 'volume': 1500, 'cpc': 2.50},
        {'termo': 'seo otimizacao', 'volume': 800, 'cpc': 1.80}
    ]
    result = filter_keywords(keywords, volume_minimo=1000)
    assert len(result) == 1
    assert result[0]['termo'] == 'marketing digital'
'''
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = test_code
                
                result = self.validator.analyze_test_semantics(Path('test.py'))
                
                # Não deve ter problemas de dados genéricos
                generic_issues = [issue for issue in result['issues'] if issue['type'] == 'generic_data']
                assert len(generic_issues) == 0
    
    def test_validate_specific_assertions(self):
        """Testa validação de assertivas específicas."""
        test_code = '''
def test_calculation():
    result = calculate_score(100, 0.8)
    assert result == 80.0
    assert result > 0
    assert isinstance(result, float)
'''
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = test_code
                
                result = self.validator.analyze_test_semantics(Path('test.py'))
                
                # Deve ter score alto para assertivas específicas
                assert result['semantic_score'] >= 80.0


if __name__ == "__main__":
    pytest.main([__file__]) 