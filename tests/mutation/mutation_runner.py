"""
Mutation Testing Runner para Integrações Externas
Tracing ID: TEST-001
Data: 2024-12-20
Versão: 1.0
"""

import ast
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MutationResult:
    """Resultado de uma mutação específica"""
    mutation_id: str
    original_code: str
    mutated_code: str
    test_result: bool
    killed: bool
    execution_time: float
    error_message: Optional[str] = None


@dataclass
class MutationReport:
    """Relatório completo de mutation testing"""
    total_mutations: int
    killed_mutations: int
    survived_mutations: int
    mutation_score: float
    execution_time: float
    timestamp: datetime
    details: List[MutationResult]


class MutationOperator:
    """Operadores de mutação para integrações externas"""
    
    @staticmethod
    def change_http_method(node: ast.AST) -> List[ast.AST]:
        """Muda métodos HTTP (GET -> POST, POST -> PUT, etc.)"""
        mutations = []
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'attr') and node.func.attr in ['get', 'post', 'put', 'delete']:
                for method in ['get', 'post', 'put', 'delete']:
                    if method != node.func.attr:
                        new_node = ast.copy_location(ast.Call(
                            func=ast.Attribute(value=node.func.value, attr=method),
                            args=node.args,
                            keywords=node.keywords
                        ), node)
                        mutations.append(new_node)
        return mutations
    
    @staticmethod
    def change_status_code_check(node: ast.AST) -> List[ast.AST]:
        """Muda verificações de status code"""
        mutations = []
        if isinstance(node, ast.Compare):
            if isinstance(node.ops[0], ast.Eq):
                # 200 == response.status_code -> 404 == response.status_code
                for status in [200, 201, 400, 401, 403, 404, 500]:
                    new_node = ast.copy_location(ast.Compare(
                        left=node.left,
                        ops=[ast.Eq()],
                        comparators=[ast.Constant(value=status)]
                    ), node)
                    mutations.append(new_node)
        return mutations
    
    @staticmethod
    def change_timeout_value(node: ast.AST) -> List[ast.AST]:
        """Muda valores de timeout"""
        mutations = []
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if node.value > 0:  # Provavelmente um timeout
                for timeout in [0, 1, 5, 10, 30, 60]:
                    if timeout != node.value:
                        new_node = ast.copy_location(ast.Constant(value=timeout), node)
                        mutations.append(new_node)
        return mutations
    
    @staticmethod
    def change_retry_count(node: ast.AST) -> List[ast.AST]:
        """Muda contadores de retry"""
        mutations = []
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            if 0 <= node.value <= 5:  # Provavelmente um retry count
                for retry in [0, 1, 2, 3, 5, 10]:
                    if retry != node.value:
                        new_node = ast.copy_location(ast.Constant(value=retry), node)
                        mutations.append(new_node)
        return mutations
    
    @staticmethod
    def change_api_endpoint(node: ast.AST) -> List[ast.AST]:
        """Muda endpoints de API"""
        mutations = []
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any(keyword in node.value.lower() for keyword in ['api', 'endpoint', 'url']):
                # Muda para endpoints inválidos
                invalid_endpoints = [
                    'https://invalid-api.com',
                    'https://broken-endpoint.org',
                    'https://timeout-api.net'
                ]
                for endpoint in invalid_endpoints:
                    if endpoint != node.value:
                        new_node = ast.copy_location(ast.Constant(value=endpoint), node)
                        mutations.append(new_node)
        return mutations


class MutationVisitor(ast.NodeTransformer):
    """Visitor para aplicar mutações em AST"""
    
    def __init__(self, operator: MutationOperator):
        self.operator = operator
        self.mutations = []
        self.mutation_id = 0
    
    def visit(self, node: ast.AST) -> ast.AST:
        """Visita cada nó e aplica mutações"""
        # Aplica mutações específicas para integrações
        mutations = []
        
        # HTTP methods
        mutations.extend(self.operator.change_http_method(node))
        
        # Status codes
        mutations.extend(self.operator.change_status_code_check(node))
        
        # Timeouts
        mutations.extend(self.operator.change_timeout_value(node))
        
        # Retry counts
        mutations.extend(self.operator.change_retry_count(node))
        
        # API endpoints
        mutations.extend(self.operator.change_api_endpoint(node))
        
        # Adiciona mutações encontradas
        for mutation in mutations:
            self.mutations.append({
                'id': f"MUT_{self.mutation_id:04d}",
                'node': node,
                'mutation': mutation
            })
            self.mutation_id += 1
        
        return super().visit(node)


class MutationRunner:
    """Runner principal para mutation testing"""
    
    def __init__(self, test_dir: str = "tests", coverage_threshold: float = 0.8):
        self.test_dir = Path(test_dir)
        self.coverage_threshold = coverage_threshold
        self.operator = MutationOperator()
        self.results: List[MutationResult] = []
        
    def find_integration_files(self) -> List[Path]:
        """Encontra arquivos de integração para mutar"""
        integration_patterns = [
            "**/integrations/*.py",
            "**/api/*.py", 
            "**/services/*.py",
            "**/infrastructure/**/*.py"
        ]
        
        files = []
        for pattern in integration_patterns:
            files.extend(self.test_dir.parent.glob(pattern))
        
        return [f for f in files if f.is_file() and not f.name.startswith('test_')]
    
    def run_tests(self, test_file: str) -> Tuple[bool, float, str]:
        """Executa testes e retorna resultado"""
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-value", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30
            )
            execution_time = time.time() - start_time
            
            success = result.returncode == 0
            return success, execution_time, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, 30.0, "Test timeout"
        except Exception as e:
            return False, 0.0, str(e)
    
    def create_mutation(self, file_path: Path, mutation_info: Dict) -> str:
        """Cria uma mutação específica no arquivo"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        visitor = MutationVisitor(self.operator)
        
        # Aplica a mutação específica
        original_node = mutation_info['node']
        mutated_node = mutation_info['mutation']
        
        # Substitui o nó na AST
        for node in ast.walk(tree):
            if (isinstance(node, type(original_node)) and 
                ast.dump(node) == ast.dump(original_node)):
                # Encontra o nó pai e substitui
                for field_name, field_value in ast.iter_fields(node):
                    if field_value == original_node:
                        setattr(node, field_name, mutated_node)
                        break
        
        # Gera código mutado
        mutated_code = ast.unparse(tree)
        
        # Salva arquivo temporário
        temp_file = file_path.parent / f"temp_mutation_{mutation_info['id']}.py"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(mutated_code)
        
        return str(temp_file)
    
    def run_mutation_testing(self) -> MutationReport:
        """Executa mutation testing completo"""
        logger.info("🚀 Iniciando Mutation Testing para Integrações Externas")
        
        start_time = time.time()
        integration_files = self.find_integration_files()
        
        logger.info(f"📁 Encontrados {len(integration_files)} arquivos de integração")
        
        total_mutations = 0
        killed_mutations = 0
        survived_mutations = 0
        
        for file_path in integration_files:
            logger.info(f"🔍 Analisando: {file_path}")
            
            # Encontra testes correspondentes
            test_file = self.find_test_file(file_path)
            if not test_file:
                logger.warning(f"⚠️ Nenhum teste encontrado para {file_path}")
                continue
            
            # Executa testes originais
            original_success, original_time, original_error = self.run_tests(str(test_file))
            if not original_success:
                logger.warning(f"⚠️ Testes originais falharam para {file_path}")
                continue
            
            # Gera mutações
            mutations = self.generate_mutations(file_path)
            total_mutations += len(mutations)
            
            for mutation in mutations:
                logger.info(f"🧬 Aplicando mutação {mutation['id']}")
                
                # Cria arquivo mutado
                temp_file = self.create_mutation(file_path, mutation)
                
                try:
                    # Executa testes com mutação
                    mutated_success, mutated_time, mutated_error = self.run_tests(str(test_file))
                    
                    # Determina se mutação foi "killed"
                    killed = original_success and not mutated_success
                    
                    if killed:
                        killed_mutations += 1
                    else:
                        survived_mutations += 1
                    
                    # Registra resultado
                    result = MutationResult(
                        mutation_id=mutation['id'],
                        original_code=ast.unparse(mutation['node']),
                        mutated_code=ast.unparse(mutation['mutation']),
                        test_result=mutated_success,
                        killed=killed,
                        execution_time=mutated_time,
                        error_message=mutated_error if not mutated_success else None
                    )
                    self.results.append(result)
                    
                finally:
                    # Limpa arquivo temporário
                    Path(temp_file).unlink(missing_ok=True)
        
        execution_time = time.time() - start_time
        mutation_score = killed_mutations / total_mutations if total_mutations > 0 else 0.0
        
        report = MutationReport(
            total_mutations=total_mutations,
            killed_mutations=killed_mutations,
            survived_mutations=survived_mutations,
            mutation_score=mutation_score,
            execution_time=execution_time,
            timestamp=datetime.now(),
            details=self.results
        )
        
        logger.info(f"✅ Mutation Testing concluído")
        logger.info(f"📊 Score: {mutation_score:.2%} ({killed_mutations}/{total_mutations})")
        
        return report
    
    def find_test_file(self, source_file: Path) -> Optional[Path]:
        """Encontra arquivo de teste correspondente"""
        # Procura por padrões comuns de teste
        test_patterns = [
            f"test_{source_file.stem}.py",
            f"{source_file.stem}_test.py",
            f"test_{source_file.name}"
        ]
        
        for pattern in test_patterns:
            test_file = self.test_dir / pattern
            if test_file.exists():
                return test_file
        
        # Procura em subdiretórios
        for test_file in self.test_dir.rglob(f"test_{source_file.stem}.py"):
            return test_file
        
        return None
    
    def generate_mutations(self, file_path: Path) -> List[Dict]:
        """Gera lista de mutações para um arquivo"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        visitor = MutationVisitor(self.operator)
        visitor.visit(tree)
        
        return visitor.mutations
    
    def generate_report(self, report: MutationReport, output_file: str = "mutation_report.json"):
        """Gera relatório detalhado"""
        report_data = {
            "summary": {
                "total_mutations": report.total_mutations,
                "killed_mutations": report.killed_mutations,
                "survived_mutations": report.survived_mutations,
                "mutation_score": report.mutation_score,
                "execution_time": report.execution_time,
                "timestamp": report.timestamp.isoformat(),
                "coverage_threshold": self.coverage_threshold,
                "passed_threshold": report.mutation_score >= self.coverage_threshold
            },
            "details": [
                {
                    "mutation_id": result.mutation_id,
                    "killed": result.killed,
                    "execution_time": result.execution_time,
                    "error_message": result.error_message,
                    "original_code": result.original_code,
                    "mutated_code": result.mutated_code
                }
                for result in report.details
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {output_file}")
        
        # Log de sobreviventes para análise
        survivors = [r for r in report.details if not r.killed]
        if survivors:
            logger.warning(f"⚠️ {len(survivors)} mutações sobreviveram:")
            for survivor in survivors[:5]:  # Mostra apenas os primeiros 5
                logger.warning(f"   - {survivor.mutation_id}: {survivor.original_code} -> {survivor.mutated_code}")


def main():
    """Função principal para execução via CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mutation Testing para Integrações Externas")
    parser.add_argument("--test-dir", default="tests", help="Diretório de testes")
    parser.add_argument("--coverage-threshold", type=float, default=0.8, help="Threshold de cobertura")
    parser.add_argument("--output", default="mutation_report.json", help="Arquivo de saída")
    
    args = parser.parse_args()
    
    runner = MutationRunner(
        test_dir=args.test_dir,
        coverage_threshold=args.coverage_threshold
    )
    
    report = runner.run_mutation_testing()
    runner.generate_report(report, args.output)
    
    # Exit code baseado no threshold
    if report.mutation_score < args.coverage_threshold:
        logger.error(f"❌ Mutation score {report.mutation_score:.2%} abaixo do threshold {args.coverage_threshold:.2%}")
        sys.exit(1)
    else:
        logger.info(f"✅ Mutation score {report.mutation_score:.2%} acima do threshold {args.coverage_threshold:.2%}")
        sys.exit(0)


if __name__ == "__main__":
    main() 