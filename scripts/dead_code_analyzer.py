#!/usr/bin/env python3
"""
🎯 ANÁLISE COMPLETA DE CÓDIGO MORTO - OMNİ KEYWORDS FINDER
📐 CoCoT: Comprovação, Causalidade, Contexto, Tendência
🌲 ToT: Múltiplas abordagens de análise
♻️ ReAct: Simulação e reflexão sobre impactos
🖼️ Visual: Representações de relacionamentos

Tracing ID: DEAD_CODE_ANALYSIS_20250127_001
Data: 2025-01-27
Versão: 1.0.0
Status: ✅ CRIAÇÃO DE SCRIPT
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from collections import defaultdict

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CodeElement:
    """Elemento de código identificado"""
    name: str
    type: str  # function, class, variable, import, module
    file_path: str
    line_number: int
    is_used: bool = False
    usage_count: int = 0
    usage_locations: List[str] = field(default_factory=list)
    complexity: int = 0
    size: int = 0
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL

@dataclass
class DeadCodeResult:
    """Resultado da análise de código morto"""
    total_elements: int
    used_elements: int
    dead_elements: int
    dead_functions: int
    dead_classes: int
    dead_imports: int
    dead_variables: int
    dead_modules: int
    recommendations: List[str]
    risk_assessment: Dict[str, int]
    optimization_potential: float
    dead_code_by_file: Dict[str, List[CodeElement]]

class DeadCodeAnalyzer:
    """
    📐 CoCoT - Analisador de Código Morto Avançado
    
    Comprovação: Baseado em análise estática e AST parsing
    Causalidade: Identifica elementos não utilizados
    Contexto: Considera arquitetura e padrões do projeto
    Tendência: Aplica técnicas modernas de análise de código
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.code_elements: Dict[str, CodeElement] = {}
        self.usage_map: Dict[str, Set[str]] = defaultdict(set)
        self.import_map: Dict[str, Set[str]] = defaultdict(set)
        self.function_calls: Set[str] = set()
        self.class_instantiations: Set[str] = set()
        self.variable_references: Set[str] = set()
        
        # Padrões de exclusão
        self.exclude_patterns = [
            r'__init__\.py$',
            r'__pycache__',
            r'\.pyc$',
            r'\.git',
            r'node_modules',
            r'\.venv',
            r'tests?/',
            r'docs/',
            r'logs/',
            r'\.env'
        ]
        
        # Padrões de código crítico (não remover)
        self.critical_patterns = [
            r'main\(\)',
            r'__main__',
            r'if __name__ == "__main__"',
            r'@app\.route',
            r'@api\.',
            r'def test_',
            r'class Test',
            r'def setUp',
            r'def tearDown'
        ]
    
    def analyze_project(self) -> DeadCodeResult:
        """
        🌲 ToT - Análise Completa do Projeto
        
        Abordagem 1: Análise AST por arquivo
        Abordagem 2: Cross-reference analysis
        Abordagem 3: Import dependency analysis
        Abordagem 4: Usage pattern analysis
        """
        logger.info("🔍 Iniciando análise de código morto...")
        
        # Etapa 1: Scan de arquivos Python
        python_files = self._get_python_files()
        logger.info(f"📁 Encontrados {len(python_files)} arquivos Python")
        
        # Etapa 2: Análise AST de cada arquivo
        for file_path in python_files:
            try:
                self._analyze_file_ast(file_path)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar {file_path}: {e}")
        
        # Etapa 3: Análise de cross-references
        self._analyze_cross_references()
        
        # Etapa 4: Identificação de código morto
        dead_elements = self._identify_dead_code()
        
        # Etapa 5: Geração de relatório
        result = self._generate_analysis_result(dead_elements)
        
        logger.info(f"✅ Análise concluída. {len(dead_elements)} elementos mortos identificados")
        return result
    
    def _get_python_files(self) -> List[Path]:
        """Obtém lista de arquivos Python para análise"""
        python_files = []
        
        for file_path in self.project_root.rglob("*.py"):
            # Verificar padrões de exclusão
            if any(re.search(pattern, str(file_path)) for pattern in self.exclude_patterns):
                continue
            
            python_files.append(file_path)
        
        return python_files
    
    def _analyze_file_ast(self, file_path: Path):
        """
        ♻️ ReAct - Análise AST de Arquivo
        
        Simulação: Parse completo do AST
        Efeitos: Identificação de todos os elementos
        Ganhos: Análise precisa e completa
        Riscos: Complexidade de parsing (mitigável com tratamento de erros)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Analisar diferentes tipos de elementos
            self._analyze_imports(tree, file_path)
            self._analyze_functions(tree, file_path)
            self._analyze_classes(tree, file_path)
            self._analyze_variables(tree, file_path)
            self._analyze_calls_and_references(tree, file_path)
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar AST de {file_path}: {e}")
    
    def _analyze_imports(self, tree: ast.AST, file_path: Path):
        """Análise de imports"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    element = CodeElement(
                        name=alias.name,
                        type="import",
                        file_path=str(file_path),
                        line_number=node.lineno
                    )
                    self.code_elements[f"import:{alias.name}:{file_path}"] = element
                    self.import_map[alias.name].add(str(file_path))
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    element = CodeElement(
                        name=full_name,
                        type="import",
                        file_path=str(file_path),
                        line_number=node.lineno
                    )
                    self.code_elements[f"import:{full_name}:{file_path}"] = element
                    self.import_map[full_name].add(str(file_path))
    
    def _analyze_functions(self, tree: ast.AST, file_path: Path):
        """Análise de funções"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calcular complexidade
                complexity = self._calculate_complexity(node)
                
                element = CodeElement(
                    name=node.name,
                    type="function",
                    file_path=str(file_path),
                    line_number=node.lineno,
                    complexity=complexity,
                    size=len(ast.unparse(node).split('\n'))
                )
                
                # Verificar se é crítica
                if any(re.search(pattern, node.name) for pattern in self.critical_patterns):
                    element.risk_level = "CRITICAL"
                
                self.code_elements[f"function:{node.name}:{file_path}"] = element
    
    def _analyze_classes(self, tree: ast.AST, file_path: Path):
        """Análise de classes"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Calcular complexidade
                complexity = self._calculate_complexity(node)
                
                element = CodeElement(
                    name=node.name,
                    type="class",
                    file_path=str(file_path),
                    line_number=node.lineno,
                    complexity=complexity,
                    size=len(ast.unparse(node).split('\n'))
                )
                
                # Verificar se é crítica
                if any(re.search(pattern, node.name) for pattern in self.critical_patterns):
                    element.risk_level = "CRITICAL"
                
                self.code_elements[f"class:{node.name}:{file_path}"] = element
    
    def _analyze_variables(self, tree: ast.AST, file_path: Path):
        """Análise de variáveis"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        element = CodeElement(
                            name=target.id,
                            type="variable",
                            file_path=str(file_path),
                            line_number=node.lineno
                        )
                        self.code_elements[f"variable:{target.id}:{file_path}"] = element
    
    def _analyze_calls_and_references(self, tree: ast.AST, file_path: Path):
        """Análise de chamadas e referências"""
        for node in ast.walk(tree):
            # Chamadas de função
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    self.function_calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    self.function_calls.add(f"{node.func.value.id}.{node.func.attr}")
            
            # Instanciação de classes
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                # Verificar se é instanciação de classe
                if node.func.id in [elem.name for elem in self.code_elements.values() if elem.type == "class"]:
                    self.class_instantiations.add(node.func.id)
            
            # Referências de variáveis
            elif isinstance(node, ast.Name):
                self.variable_references.add(node.id)
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calcula complexidade ciclomática"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
        
        return complexity
    
    def _analyze_cross_references(self):
        """
        🖼️ Visual - Análise de Cross-References
        
        Representa relacionamentos entre elementos
        """
        logger.info("🔗 Analisando cross-references...")
        
        # Mapear usos de funções
        for func_call in self.function_calls:
            for element_id, element in self.code_elements.items():
                if element.type == "function" and element.name == func_call:
                    element.is_used = True
                    element.usage_count += 1
        
        # Mapear instanciações de classes
        for class_inst in self.class_instantiations:
            for element_id, element in self.code_elements.items():
                if element.type == "class" and element.name == class_inst:
                    element.is_used = True
                    element.usage_count += 1
        
        # Mapear referências de variáveis
        for var_ref in self.variable_references:
            for element_id, element in self.code_elements.items():
                if element.type == "variable" and element.name == var_ref:
                    element.is_used = True
                    element.usage_count += 1
    
    def _identify_dead_code(self) -> List[CodeElement]:
        """Identifica código morto"""
        dead_elements = []
        
        for element_id, element in self.code_elements.items():
            # Verificar se é código morto
            if not element.is_used and element.usage_count == 0:
                # Excluir elementos críticos
                if element.risk_level != "CRITICAL":
                    dead_elements.append(element)
        
        return dead_elements
    
    def _generate_analysis_result(self, dead_elements: List[CodeElement]) -> DeadCodeResult:
        """Gera resultado da análise"""
        # Estatísticas
        total_elements = len(self.code_elements)
        used_elements = len([elem for elem in self.code_elements.values() if elem.is_used])
        dead_elements_count = len(dead_elements)
        
        # Por tipo
        dead_functions = len([elem for elem in dead_elements if elem.type == "function"])
        dead_classes = len([elem for elem in dead_elements if elem.type == "class"])
        dead_imports = len([elem for elem in dead_elements if elem.type == "import"])
        dead_variables = len([elem for elem in dead_elements if elem.type == "variable"])
        dead_modules = len([elem for elem in dead_elements if elem.type == "module"])
        
        # Recomendações
        recommendations = self._generate_recommendations(dead_elements)
        
        # Avaliação de risco
        risk_assessment = {
            "LOW": len([elem for elem in dead_elements if elem.risk_level == "LOW"]),
            "MEDIUM": len([elem for elem in dead_elements if elem.risk_level == "MEDIUM"]),
            "HIGH": len([elem for elem in dead_elements if elem.risk_level == "HIGH"]),
            "CRITICAL": len([elem for elem in dead_elements if elem.risk_level == "CRITICAL"])
        }
        
        # Potencial de otimização
        optimization_potential = (dead_elements_count / total_elements * 100) if total_elements > 0 else 0
        
        # Agrupar por arquivo
        dead_code_by_file = defaultdict(list)
        for element in dead_elements:
            dead_code_by_file[element.file_path].append(element)
        
        return DeadCodeResult(
            total_elements=total_elements,
            used_elements=used_elements,
            dead_elements=dead_elements_count,
            dead_functions=dead_functions,
            dead_classes=dead_classes,
            dead_imports=dead_imports,
            dead_variables=dead_variables,
            dead_modules=dead_modules,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            optimization_potential=optimization_potential,
            dead_code_by_file=dict(dead_code_by_file)
        )
    
    def _generate_recommendations(self, dead_elements: List[CodeElement]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Por tipo de elemento
        dead_functions = [elem for elem in dead_elements if elem.type == "function"]
        if dead_functions:
            recommendations.append(f"🔧 Remover {len(dead_functions)} funções não utilizadas")
        
        dead_classes = [elem for elem in dead_elements if elem.type == "class"]
        if dead_classes:
            recommendations.append(f"🏗️ Remover {len(dead_classes)} classes não utilizadas")
        
        dead_imports = [elem for elem in dead_elements if elem.type == "import"]
        if dead_imports:
            recommendations.append(f"📦 Remover {len(dead_imports)} imports não utilizados")
        
        dead_variables = [elem for elem in dead_elements if elem.type == "variable"]
        if dead_variables:
            recommendations.append(f"📝 Remover {len(dead_variables)} variáveis não utilizadas")
        
        # Por complexidade
        high_complexity = [elem for elem in dead_elements if elem.complexity > 10]
        if high_complexity:
            recommendations.append(f"⚠️ {len(high_complexity)} elementos mortos com alta complexidade")
        
        # Por tamanho
        large_elements = [elem for elem in dead_elements if elem.size > 50]
        if large_elements:
            recommendations.append(f"📏 {len(large_elements)} elementos mortos com mais de 50 linhas")
        
        return recommendations
    
    def save_analysis_results(self, result: DeadCodeResult, output_file: str):
        """Salva resultados da análise"""
        logger.info(f"💾 Salvando resultados em {output_file}...")
        
        # Converter para formato serializável
        result_data = {
            "metadata": {
                "tracing_id": "DEAD_CODE_ANALYSIS_20250127_001",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "project": "Omni Keywords Finder"
            },
            "summary": {
                "total_elements": result.total_elements,
                "used_elements": result.used_elements,
                "dead_elements": result.dead_elements,
                "dead_functions": result.dead_functions,
                "dead_classes": result.dead_classes,
                "dead_imports": result.dead_imports,
                "dead_variables": result.dead_variables,
                "dead_modules": result.dead_modules,
                "optimization_potential": result.optimization_potential
            },
            "dead_code_details": {
                file_path: [
                    {
                        "name": elem.name,
                        "type": elem.type,
                        "line_number": elem.line_number,
                        "complexity": elem.complexity,
                        "size": elem.size,
                        "risk_level": elem.risk_level
                    }
                    for elem in elements
                ]
                for file_path, elements in result.dead_code_by_file.items()
            },
            "recommendations": result.recommendations,
            "risk_assessment": result.risk_assessment
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Resultados salvos em {output_file}")

def main():
    """
    🎯 Função principal da análise
    
    Executa análise completa seguindo abordagens:
    - CoCoT: Análise fundamentada
    - ToT: Múltiplas estratégias
    - ReAct: Simulação de impactos
    - Visual: Representações claras
    """
    logger.info("🚀 Iniciando Análise Completa de Código Morto")
    logger.info("📐 CoCoT: Análise fundamentada em boas práticas")
    logger.info("🌲 ToT: Múltiplas estratégias de análise")
    logger.info("♻️ ReAct: Simulação de impactos e riscos")
    logger.info("🖼️ Visual: Representações claras dos resultados")
    
    # Configuração
    project_root = os.getcwd()
    output_file = "dead_code_analysis_results.json"
    
    try:
        # Inicializar analisador
        analyzer = DeadCodeAnalyzer(project_root)
        
        # Executar análise
        logger.info("🔍 Etapa 1: Analisando projeto...")
        result = analyzer.analyze_project()
        
        # Salvar resultados
        logger.info("💾 Etapa 2: Salvando resultados...")
        analyzer.save_analysis_results(result, output_file)
        
        # Exibir resumo
        logger.info("🎯 RESUMO DA ANÁLISE:")
        logger.info(f"   📊 Total de elementos: {result.total_elements}")
        logger.info(f"   ✅ Elementos utilizados: {result.used_elements}")
        logger.info(f"   ❌ Elementos mortos: {result.dead_elements}")
        logger.info(f"   🔧 Funções mortas: {result.dead_functions}")
        logger.info(f"   🏗️ Classes mortas: {result.dead_classes}")
        logger.info(f"   📦 Imports mortos: {result.dead_imports}")
        logger.info(f"   📝 Variáveis mortas: {result.dead_variables}")
        logger.info(f"   🎯 Potencial de otimização: {result.optimization_potential:.1f}%")
        logger.info(f"   📋 Recomendações: {len(result.recommendations)}")
        
        logger.info("✅ Análise de código morto concluída com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro durante análise: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 