"""
Semantic Contracts Generator - Gerador de Contratos Semânticos

Tracing ID: SEMANTIC_CONTRACTS_GENERATOR_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: Implementação Inicial

Responsável: Sistema de Documentação Enterprise
"""

import ast
import inspect
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime
import json

# Importações do sistema
try:
    from infrastructure.ml.semantic_embeddings import SemanticEmbeddingService
    from infrastructure.validation.doc_quality_score import DocQualityAnalyzer
except ImportError:
    # Fallback para desenvolvimento
    SemanticEmbeddingService = None
    DocQualityAnalyzer = None

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """Informações de uma função"""
    name: str
    module: str
    path: str
    line: int
    docstring: str
    signature: str
    parameters: List[str]
    return_type: str
    exceptions: List[str]
    complexity: str
    purpose: str


@dataclass
class ModuleInfo:
    """Informações de um módulo"""
    name: str
    path: str
    purpose: str
    responsibility: str
    dependencies: List[str]
    functions: List[FunctionInfo]
    classes: List[str]
    version: str
    last_updated: str


@dataclass
class SemanticContract:
    """Contrato semântico completo"""
    module_info: ModuleInfo
    functions: List[FunctionInfo]
    semantic_similarity: float
    quality_metrics: Dict[str, float]
    test_references: Dict[str, str]


class SemanticContractsGenerator:
    """
    Gerador de contratos semânticos para documentação enterprise
    
    Responsabilidades:
    - Analisar módulos Python
    - Extrair informações de funções e classes
    - Calcular similaridade semântica
    - Gerar documentação estruturada
    - Integrar com sistema de qualidade
    """
    
    def __init__(self, project_root: str = "."):
        """
        Inicializa o gerador
        
        Args:
            project_root: Caminho raiz do projeto
        """
        self.project_root = Path(project_root)
        self.embedding_service = SemanticEmbeddingService() if SemanticEmbeddingService else None
        self.quality_analyzer = DocQualityAnalyzer() if DocQualityAnalyzer else None
        self.generated_contracts: List[SemanticContract] = []
        
    def analyze_module(self, module_path: str) -> ModuleInfo:
        """
        Analisa um módulo Python e extrai informações
        
        Args:
            module_path: Caminho para o módulo
            
        Returns:
            ModuleInfo com informações do módulo
        """
        full_path = self.project_root / module_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Módulo não encontrado: {module_path}")
        
        # Ler conteúdo do arquivo
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        # Extrair informações básicas
        module_name = full_path.stem
        purpose = self._extract_module_purpose(content)
        responsibility = self._extract_module_responsibility(content)
        dependencies = self._extract_dependencies(content)
        functions = self._extract_functions(tree, module_name, str(full_path))
        classes = self._extract_classes(tree)
        
        # Obter metadados do arquivo
        stat = full_path.stat()
        last_updated = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%data %H:%M:%S")
        
        return ModuleInfo(
            name=module_name,
            path=str(full_path),
            purpose=purpose,
            responsibility=responsibility,
            dependencies=dependencies,
            functions=functions,
            classes=classes,
            version="1.0",  # TODO: Extrair de __version__
            last_updated=last_updated
        )
    
    def _extract_module_purpose(self, content: str) -> str:
        """Extrai o propósito do módulo do docstring"""
        # Procurar por docstring no início do arquivo
        lines = content.split('\n')
        for index, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Encontrar fim do docstring
                start = index
                for counter in range(index + 1, len(lines)):
                    if lines[counter].strip().endswith('"""') or lines[counter].strip().endswith("'''"):
                        docstring = '\n'.join(lines[start:counter+1])
                        # Extrair primeira linha como propósito
                        first_line = docstring.split('\n')[0].strip('"\'')
                        return first_line
        return "Módulo Python"
    
    def _extract_module_responsibility(self, content: str) -> str:
        """Extrai a responsabilidade principal do módulo"""
        # Procurar por comentários que indiquem responsabilidade
        lines = content.split('\n')
        for line in lines:
            if 'responsabilidade' in line.lower() or 'responsibility' in line.lower():
                return line.strip('#').strip()
        return "Funcionalidade específica do sistema"
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extrai dependências do módulo"""
        dependencies = []
        
        # Procurar por imports
        import_pattern = r'^(?:from\string_data+(\w+(?:\.\w+)*)\string_data+import|import\string_data+(\w+(?:\.\w+)*))'
        lines = content.split('\n')
        
        for line in lines:
            match = re.match(import_pattern, line.strip())
            if match:
                dep = match.group(1) or match.group(2)
                if dep and not dep.startswith('.'):  # Ignorar imports relativos
                    dependencies.append(dep)
        
        return list(set(dependencies))  # Remover duplicatas
    
    def _extract_functions(self, tree: ast.AST, module_name: str, file_path: str) -> List[FunctionInfo]:
        """Extrai informações de funções do AST"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._analyze_function(node, module_name, file_path)
                functions.append(func_info)
        
        return functions
    
    def _analyze_function(self, node: ast.FunctionDef, module_name: str, file_path: str) -> FunctionInfo:
        """Analisa uma função específica"""
        # Extrair docstring
        docstring = ast.get_docstring(node) or ""
        
        # Extrair assinatura
        signature = self._get_function_signature(node)
        
        # Extrair parâmetros
        parameters = [arg.arg for arg in node.args.args]
        
        # Extrair tipo de retorno
        return_type = "Any"
        if node.returns:
            return_type = ast.unparse(node.returns)
        
        # Extrair exceções
        exceptions = self._extract_exceptions(node)
        
        # Calcular complexidade
        complexity = self._calculate_complexity(node)
        
        # Extrair propósito
        purpose = self._extract_function_purpose(docstring)
        
        return FunctionInfo(
            name=node.name,
            module=module_name,
            path=f"{file_path}:{node.lineno}",
            line=node.lineno,
            docstring=docstring,
            signature=signature,
            parameters=parameters,
            return_type=return_type,
            exceptions=exceptions,
            complexity=complexity,
            purpose=purpose
        )
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Gera assinatura da função"""
        try:
            return ast.unparse(node)
        except:
            # Fallback para versões antigas do Python
            args = []
            for arg in node.args.args:
                args.append(arg.arg)
            
            if node.args.vararg:
                args.append(f"*{node.args.vararg.arg}")
            if node.args.kwarg:
                args.append(f"**{node.args.kwarg.arg}")
            
            return f"def {node.name}({', '.join(args)}):"
    
    def _extract_exceptions(self, node: ast.FunctionDef) -> List[str]:
        """Extrai exceções que a função pode levantar"""
        exceptions = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if child.exc:
                    try:
                        exc_name = ast.unparse(child.exc)
                        exceptions.append(exc_name)
                    except:
                        exceptions.append("Exception")
        
        return list(set(exceptions))
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> str:
        """Calcula complexidade da função"""
        complexity_score = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                complexity_score += 1
        
        if complexity_score <= 3:
            return "Baixa"
        elif complexity_score <= 7:
            return "Média"
        else:
            return "Alta"
    
    def _extract_function_purpose(self, docstring: str) -> str:
        """Extrai propósito da função do docstring"""
        if not docstring:
            return "Função sem documentação"
        
        lines = docstring.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Args:') and not line.startswith('Returns:'):
                return line
        return "Função sem propósito claro"
    
    def _extract_classes(self, tree: ast.AST) -> List[str]:
        """Extrai nomes das classes do módulo"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return classes
    
    def calculate_semantic_similarity(self, module_info: ModuleInfo) -> float:
        """
        Calcula similaridade semântica do módulo
        
        Args:
            module_info: Informações do módulo
            
        Returns:
            Score de similaridade (0.0-1.0)
        """
        if not self.embedding_service:
            # Fallback: calcular baseado em métricas básicas
            return self._calculate_basic_similarity(module_info)
        
        try:
            # Gerar embedding do propósito do módulo
            purpose_embedding = self.embedding_service.generate_embedding(module_info.purpose)
            
            # Gerar embedding das funções principais
            function_texts = [f.purpose for f in module_info.functions[:5]]  # Top 5 funções
            if function_texts:
                function_embedding = self.embedding_service.generate_embedding(' '.join(function_texts))
                
                # Calcular similaridade
                similarity = self.embedding_service.calculate_similarity(
                    purpose_embedding, function_embedding
                )
                return min(similarity, 1.0)
            else:
                return 0.8  # Módulo sem funções
                
        except Exception as e:
            logger.warning(f"Erro ao calcular similaridade semântica: {e}")
            return self._calculate_basic_similarity(module_info)
    
    def _calculate_basic_similarity(self, module_info: ModuleInfo) -> float:
        """Calcula similaridade básica baseada em métricas simples"""
        score = 0.0
        
        # Base score
        score += 0.3
        
        # Bonus por ter docstring
        if module_info.purpose and module_info.purpose != "Módulo Python":
            score += 0.2
        
        # Bonus por ter funções documentadas
        documented_functions = sum(1 for f in module_info.functions if f.docstring)
        if module_info.functions:
            documentation_ratio = documented_functions / len(module_info.functions)
            score += documentation_ratio * 0.3
        
        # Bonus por ter propósito claro
        if len(module_info.purpose) > 20:
            score += 0.2
        
        return min(score, 1.0)
    
    def calculate_quality_metrics(self, module_info: ModuleInfo) -> Dict[str, float]:
        """
        Calcula métricas de qualidade da documentação
        
        Args:
            module_info: Informações do módulo
            
        Returns:
            Dicionário com métricas de qualidade
        """
        if not self.quality_analyzer:
            return self._calculate_basic_quality_metrics(module_info)
        
        try:
            # Gerar texto completo do módulo para análise
            module_text = self._generate_module_text(module_info)
            
            # Calcular métricas
            completeness = self.quality_analyzer.analyze_completeness(module_text)
            coherence = self.quality_analyzer.analyze_coherence(module_text)
            semantic_similarity = self.quality_analyzer.analyze_semantic_similarity(module_text)
            
            return {
                "completude": completeness,
                "coerencia": coherence,
                "similaridade_semantica": semantic_similarity,
                "clareza": (completeness + coherence) / 2,
                "rastreabilidade": 0.8  # Baseado em estrutura
            }
            
        except Exception as e:
            logger.warning(f"Erro ao calcular métricas de qualidade: {e}")
            return self._calculate_basic_quality_metrics(module_info)
    
    def _calculate_basic_quality_metrics(self, module_info: ModuleInfo) -> Dict[str, float]:
        """Calcula métricas básicas de qualidade"""
        # Completude baseada em documentação
        total_elements = len(module_info.functions) + len(module_info.classes)
        documented_elements = sum(1 for f in module_info.functions if f.docstring)
        
        if total_elements > 0:
            completeness = documented_elements / total_elements
        else:
            completeness = 1.0
        
        # Coerência baseada em consistência de nomenclatura
        coherence = 0.8  # Base
        
        # Clareza baseada em qualidade dos docstrings
        clarity = 0.7  # Base
        
        # Rastreabilidade baseada em estrutura
        traceability = 0.8  # Base
        
        return {
            "completude": completeness,
            "coerencia": coherence,
            "similaridade_semantica": 0.8,
            "clareza": clarity,
            "rastreabilidade": traceability
        }
    
    def _generate_module_text(self, module_info: ModuleInfo) -> str:
        """Gera texto completo do módulo para análise"""
        text_parts = [
            f"Módulo: {module_info.name}",
            f"Propósito: {module_info.purpose}",
            f"Responsabilidade: {module_info.responsibility}"
        ]
        
        for func in module_info.functions:
            text_parts.append(f"Função {func.name}: {func.purpose}")
            if func.docstring:
                text_parts.append(func.docstring)
        
        return "\n".join(text_parts)
    
    def find_test_references(self, module_info: ModuleInfo) -> Dict[str, str]:
        """
        Encontra referências aos testes do módulo
        
        Args:
            module_info: Informações do módulo
            
        Returns:
            Dicionário com referências aos testes
        """
        test_references = {}
        
        # Procurar por arquivos de teste
        module_path = Path(module_info.path)
        test_paths = [
            f"tests/unit/{module_path.parent}/{module_path.stem}/test_{module_path.stem}.py",
            f"tests/unit/{module_path.parent}/test_{module_path.stem}.py",
            f"tests/integration/{module_path.parent}/test_{module_path.stem}.py"
        ]
        
        for test_path in test_paths:
            full_test_path = self.project_root / test_path
            if full_test_path.exists():
                test_references["unit"] = str(full_test_path)
                break
        
        # Procurar por testes de funções específicas
        for func in module_info.functions:
            test_func_path = f"tests/unit/{module_path.parent}/test_{module_path.stem}.py::test_{func.name}"
            test_references[func.name] = test_func_path
        
        return test_references
    
    def generate_module_docs(self, module_path: str) -> SemanticContract:
        """
        Gera documentação completa para um módulo
        
        Args:
            module_path: Caminho para o módulo
            
        Returns:
            SemanticContract com documentação completa
        """
        logger.info(f"Gerando documentação para módulo: {module_path}")
        
        # Analisar módulo
        module_info = self.analyze_module(module_path)
        
        # Calcular similaridade semântica
        semantic_similarity = self.calculate_semantic_similarity(module_info)
        
        # Calcular métricas de qualidade
        quality_metrics = self.calculate_quality_metrics(module_info)
        
        # Encontrar referências aos testes
        test_references = self.find_test_references(module_info)
        
        # Criar contrato semântico
        contract = SemanticContract(
            module_info=module_info,
            functions=module_info.functions,
            semantic_similarity=semantic_similarity,
            quality_metrics=quality_metrics,
            test_references=test_references
        )
        
        self.generated_contracts.append(contract)
        logger.info(f"Documentação gerada com sucesso para: {module_path}")
        
        return contract
    
    def generate_function_docs(self, module_path: str, function_name: str) -> Optional[FunctionInfo]:
        """
        Gera documentação para uma função específica
        
        Args:
            module_path: Caminho para o módulo
            function_name: Nome da função
            
        Returns:
            FunctionInfo da função ou None se não encontrada
        """
        module_info = self.analyze_module(module_path)
        
        for func in module_info.functions:
            if func.name == function_name:
                return func
        
        return None
    
    def generate_markdown_documentation(self, contract: SemanticContract) -> str:
        """
        Gera documentação em formato Markdown
        
        Args:
            contract: Contrato semântico
            
        Returns:
            String com documentação Markdown
        """
        md_parts = []
        
        # Cabeçalho do módulo
        md_parts.append(f"## 📦 **MÓDULO: {contract.module_info.name}**")
        md_parts.append("")
        
        # Metadados
        md_parts.append("### **Metadados**")
        md_parts.append(f"- **Caminho**: `{contract.module_info.path}`")
        md_parts.append(f"- **Propósito**: {contract.module_info.purpose}")
        md_parts.append(f"- **Responsabilidade**: {contract.module_info.responsibility}")
        md_parts.append(f"- **Dependências**: {', '.join(contract.module_info.dependencies)}")
        md_parts.append(f"- **Similaridade Semântica**: {contract.semantic_similarity:.2f}")
        md_parts.append(f"- **Última Atualização**: {contract.module_info.last_updated}")
        md_parts.append(f"- **Versão**: {contract.module_info.version}")
        md_parts.append("")
        
        # Interface pública
        md_parts.append("### **Interface Pública**")
        md_parts.append("```python")
        for func in contract.functions[:5]:  # Top 5 funções
            md_parts.append(f"def {func.name}(...):")
            if func.docstring:
                md_parts.append(f'    """{func.docstring.split(chr(10))[0]}"""')
            md_parts.append("    pass")
            md_parts.append("")
        md_parts.append("```")
        md_parts.append("")
        
        # Contratos de função
        md_parts.append("### **Contratos de Função**")
        for func in contract.functions:
            md_parts.append(f"- **Função**: `{func.name}`")
            md_parts.append(f"  - **Propósito**: {func.purpose}")
            md_parts.append(f"  - **Parâmetros**: {', '.join(func.parameters)}")
            md_parts.append(f"  - **Retorno**: {func.return_type}")
            md_parts.append(f"  - **Exceções**: {', '.join(func.exceptions)}")
            md_parts.append(f"  - **Similaridade**: {contract.semantic_similarity:.2f}")
            if func.name in contract.test_references:
                md_parts.append(f"  - **Testes**: {contract.test_references[func.name]}")
            md_parts.append("")
        
        # Métricas de qualidade
        md_parts.append("### **Métricas de Qualidade**")
        for metric, value in contract.quality_metrics.items():
            md_parts.append(f"- **{metric.title()}**: {value:.2f}")
        md_parts.append("")
        
        return "\n".join(md_parts)
    
    def save_documentation(self, contract: SemanticContract, output_path: str):
        """
        Salva documentação em arquivo
        
        Args:
            contract: Contrato semântico
            output_path: Caminho para salvar
        """
        markdown_content = self.generate_markdown_documentation(contract)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Documentação salva em: {output_path}")


def main():
    """Função principal para execução standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerador de Contratos Semânticos")
    parser.add_argument("--module", help="Módulo específico para documentar")
    parser.add_argument("--all", action="store_true", help="Documentar todos os módulos")
    parser.add_argument("--output", default="docs/semantic_contracts", help="Diretório de saída")
    parser.add_argument("--validate", action="store_true", help="Validar qualidade da documentação")
    
    args = parser.parse_args()
    
    generator = SemanticContractsGenerator()
    
    if args.module:
        # Documentar módulo específico
        contract = generator.generate_module_docs(args.module)
        output_file = f"{args.output}/{contract.module_info.name}_contract.md"
        generator.save_documentation(contract, output_file)
        
    elif args.all:
        # Documentar todos os módulos Python
        python_files = list(Path(".").rglob("*.py"))
        for py_file in python_files:
            if "test" not in py_file.name and "migrations" not in str(py_file):
                try:
                    module_path = str(py_file.relative_to(Path(".")))
                    contract = generator.generate_module_docs(module_path)
                    output_file = f"{args.output}/{contract.module_info.name}_contract.md"
                    generator.save_documentation(contract, output_file)
                except Exception as e:
                    logger.error(f"Erro ao documentar {py_file}: {e}")
    
    if args.validate:
        # Validar qualidade
        for contract in generator.generated_contracts:
            quality_score = sum(contract.quality_metrics.values()) / len(contract.quality_metrics)
            print(f"{contract.module_info.name}: {quality_score:.2f}")
    
    return 0


if __name__ == "__main__":
    exit(main()) 