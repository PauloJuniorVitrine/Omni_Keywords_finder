"""
🧪 Validador de Documentação OpenAPI

Tracing ID: VALIDATE_DOCS_2025_001
Data/Hora: 2025-01-27 20:20:00 UTC
Versão: 1.0
Status: 🚀 IMPLEMENTAÇÃO

Valida se todos os endpoints têm documentação OpenAPI adequada.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict, Set, Any


class DocumentationValidator:
    """
    Validador de documentação OpenAPI para endpoints.
    """
    
    def __init__(self, api_dir: str = "backend/app/api"):
        """
        Inicializa o validador.
        
        Args:
            api_dir: Diretório contendo os arquivos de API
        """
        self.api_dir = Path(api_dir)
        self.endpoints_with_docs: Set[str] = set()
        self.endpoints_without_docs: Set[str] = set()
        self.validation_errors: List[str] = []
    
    def extract_endpoints_from_file(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """
        Extrai endpoints de um arquivo Python.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Lista de tuplas (rota, método, linha)
        """
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                # Padrões para diferentes frameworks
                patterns = [
                    r'@.*\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[[^\]]*\])?\)',
                    r'@.*\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)',
                    r'@app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)',
                    r'@bp\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]\)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        if len(match.groups()) == 1:
                            # Padrão route com methods
                            route = match.group(1)
                            # Extrai método da linha seguinte ou padrão
                            method = 'GET'  # padrão
                            if i < len(lines):
                                next_line = lines[i]
                                if 'methods=' in next_line:
                                    method_match = re.search(r'methods=\[([^\]]+)\]', next_line)
                                    if method_match:
                                        methods = method_match.group(1).upper().replace('"', '').replace("'", '')
                                        method = methods.split(',')[0].strip()
                        else:
                            # Padrão direto com método
                            method = match.group(1).upper()
                            route = match.group(2)
                        
                        endpoints.append((route, method, i))
                        break
                        
        except Exception as e:
            self.validation_errors.append(f"Erro ao processar {file_path}: {str(e)}")
        
        return endpoints
    
    def check_docstring_quality(self, file_path: Path, endpoint_info: Tuple[str, str, int]) -> bool:
        """
        Verifica se um endpoint tem documentação OpenAPI adequada.
        
        Args:
            file_path: Caminho do arquivo
            endpoint_info: Tupla (rota, método, linha)
            
        Returns:
            True se tem documentação adequada
        """
        route, method, line_number = endpoint_info
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Procura pela função do endpoint
            function_start = None
            for i in range(line_number, len(lines)):
                if re.match(r'^\s*def\s+\w+\(', lines[i]):
                    function_start = i
                    break
            
            if function_start is None:
                return False
            
            # Procura pela docstring
            docstring_start = None
            docstring_end = None
            
            for i in range(function_start + 1, len(lines)):
                line = lines[i].strip()
                
                if docstring_start is None:
                    if '"""' in line or "'''" in line:
                        docstring_start = i
                        if line.count('"""') >= 2 or line.count("'''") >= 2:
                            # Docstring em uma linha
                            docstring_end = i
                            break
                else:
                    if '"""' in line or "'''" in line:
                        docstring_end = i
                        break
            
            if docstring_start is None or docstring_end is None:
                return False
            
            # Extrai conteúdo da docstring
            docstring_lines = []
            for i in range(docstring_start, docstring_end + 1):
                line = lines[i]
                # Remove aspas e espaços
                if i == docstring_start:
                    line = re.sub(r'^\s*["\']{3}', '', line)
                if i == docstring_end:
                    line = re.sub(r'["\']{3}\s*$', '', line)
                docstring_lines.append(line)
            
            docstring_content = ''.join(docstring_lines)
            
            # Verifica se tem elementos OpenAPI
            required_elements = ['---', 'tags:', 'responses:']
            has_all_elements = all(element in docstring_content for element in required_elements)
            
            return has_all_elements
            
        except Exception as e:
            self.validation_errors.append(f"Erro ao verificar docstring em {file_path}:{line_number}: {str(e)}")
            return False
    
    def validate_all_endpoints(self) -> Dict[str, Any]:
        """
        Valida todos os endpoints do diretório de API.
        
        Returns:
            Relatório de validação
        """
        if not self.api_dir.exists():
            self.validation_errors.append(f"Diretório {self.api_dir} não encontrado")
            return self._generate_report()
        
        # Processa todos os arquivos Python
        for file_path in self.api_dir.glob('*.py'):
            if file_path.name.startswith('__'):
                continue
                
            endpoints = self.extract_endpoints_from_file(file_path)
            
            for endpoint_info in endpoints:
                route, method, line_number = endpoint_info
                endpoint_key = f"{route}:{method}"
                
                if self.check_docstring_quality(file_path, endpoint_info):
                    self.endpoints_with_docs.add(endpoint_key)
                else:
                    self.endpoints_without_docs.add(endpoint_key)
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict[str, Any]:
        """
        Gera relatório de validação.
        
        Returns:
            Dicionário com dados do relatório
        """
        total_endpoints = len(self.endpoints_with_docs) + len(self.endpoints_without_docs)
        coverage_percentage = (len(self.endpoints_with_docs) / total_endpoints * 100) if total_endpoints > 0 else 0.0
        
        return {
            'total_endpoints': total_endpoints,
            'endpoints_with_docs': len(self.endpoints_with_docs),
            'endpoints_without_docs': len(self.endpoints_without_docs),
            'coverage_percentage': round(coverage_percentage, 2),
            'validation_errors': self.validation_errors,
            'validated_docs': list(self.endpoints_with_docs),
            'missing_docs': list(self.endpoints_without_docs)
        }


if __name__ == "__main__":
    # Execução direta para teste
    validator = DocumentationValidator()
    report = validator.validate_all_endpoints()
    
    print("=== Relatório de Validação de Documentação ===")
    print(f"Total de endpoints: {report['total_endpoints']}")
    print(f"Com documentação: {report['endpoints_with_docs']}")
    print(f"Sem documentação: {report['endpoints_without_docs']}")
    print(f"Cobertura: {report['coverage_percentage']}%")
    
    if report['validation_errors']:
        print("\nErros de validação:")
        for error in report['validation_errors']:
            print(f"  - {error}")
    
    if report['missing_docs']:
        print("\nEndpoints sem documentação:")
        for endpoint in report['missing_docs']:
            print(f"  - {endpoint}") 