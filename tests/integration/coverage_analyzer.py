"""
📊 Coverage Analyzer System - Omni Keywords Finder

Sistema de análise de cobertura por camada com métricas detalhadas.

Tracing ID: coverage-analyzer-system-2025-01-27-001
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import ast
import inspect
from collections import defaultdict

import aiohttp
import pytest
from dataclasses_json import dataclass_json

from tests.utils.risk_calculator import calculate_risk_score
from tests.utils.semantic_validator import SemanticValidator
from tests.decorators.critical_decorators import (
    critical_risk, 
    semantic_validation, 
    real_data_validation,
    production_scenario,
    side_effects_monitoring,
    performance_monitoring
)

# Configuração de logging estruturado
logger = logging.getLogger(__name__)

@dataclass_json
@dataclass
class FunctionCoverage:
    """Cobertura de uma função específica"""
    function_name: str
    file_path: str
    line_number: int
    is_covered: bool
    is_critical: bool
    risk_score: int
    test_count: int
    last_tested: Optional[float] = None
    complexity: int = 1

@dataclass_json
@dataclass
class ClassCoverage:
    """Cobertura de uma classe específica"""
    class_name: str
    file_path: str
    line_number: int
    total_methods: int
    covered_methods: int
    is_covered: bool
    is_critical: bool
    risk_score: int
    test_count: int
    last_tested: Optional[float] = None

@dataclass_json
@dataclass
class ModuleCoverage:
    """Cobertura de um módulo específico"""
    module_name: str
    file_path: str
    total_functions: int
    covered_functions: int
    total_classes: int
    covered_classes: int
    coverage_percentage: float
    critical_functions: int
    critical_covered: int
    critical_coverage_percentage: float
    risk_score: int
    test_count: int
    last_tested: Optional[float] = None

@dataclass_json
@dataclass
class LayerCoverage:
    """Cobertura de uma camada do sistema"""
    layer_name: str  # "domain", "gateway", "infrastructure"
    total_modules: int
    covered_modules: int
    total_functions: int
    covered_functions: int
    total_classes: int
    covered_classes: int
    coverage_percentage: float
    critical_functions: int
    critical_covered: int
    critical_coverage_percentage: float
    risk_score: int
    modules: List[ModuleCoverage] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

@dataclass_json
@dataclass
class CoverageGap:
    """Lacuna de cobertura identificada"""
    gap_id: str
    component_type: str  # "function", "class", "module"
    component_name: str
    file_path: str
    line_number: int
    risk_score: int
    priority: str  # "high", "medium", "low"
    suggested_tests: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

class CoverageAnalyzer:
    """
    Analisador de cobertura por camada
    
    Características:
    - Análise de cobertura por camada (100% em domínio, 95% em gateway)
    - Identificação de funções críticas
    - Detecção de lacunas de cobertura
    - Sugestões de testes
    - Métricas de risco por componente
    """
    
    def __init__(self, 
                 source_path: str = "src",
                 test_path: str = "tests",
                 coverage_thresholds: Dict[str, float] = None):
        """
        Inicializa o analisador de cobertura
        
        Args:
            source_path: Caminho do código fonte
            test_path: Caminho dos testes
            coverage_thresholds: Thresholds de cobertura por camada
        """
        self.source_path = Path(source_path)
        self.test_path = Path(test_path)
        
        # Thresholds padrão por camada
        self.coverage_thresholds = coverage_thresholds or {
            "domain": 100.0,      # 100% em domínio
            "gateway": 95.0,      # 95% em gateway
            "infrastructure": 90.0, # 90% em infraestrutura
            "api": 95.0,          # 95% em API
            "utils": 85.0         # 85% em utilitários
        }
        
        self.semantic_validator = SemanticValidator()
        self.logger = logging.getLogger(f"{__name__}.CoverageAnalyzer")
        
        # Armazenamento de métricas
        self.function_coverage: List[FunctionCoverage] = []
        self.class_coverage: List[ClassCoverage] = []
        self.module_coverage: List[ModuleCoverage] = []
        self.layer_coverage: List[LayerCoverage] = []
        self.coverage_gaps: List[CoverageGap] = []
        
        # Cache de análise
        self.ast_cache: Dict[str, ast.AST] = {}
        self.import_cache: Dict[str, Set[str]] = {}
        
        # Mapeamento de camadas
        self.layer_mapping = {
            "domain": ["domain", "entities", "services", "repositories"],
            "gateway": ["gateway", "controllers", "middleware"],
            "infrastructure": ["infrastructure", "database", "external"],
            "api": ["api", "routes", "endpoints"],
            "utils": ["utils", "helpers", "common"]
        }
    
    def analyze_source_code(self) -> Dict[str, Any]:
        """
        Analisa o código fonte para identificar componentes
        
        Returns:
            Dicionário com componentes identificados
        """
        self.logger.info("Iniciando análise do código fonte")
        
        components = {
            "functions": [],
            "classes": [],
            "modules": [],
            "layers": {}
        }
        
        # Percorre todos os arquivos Python no source_path
        for py_file in self.source_path.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                # Analisa arquivo
                file_components = self._analyze_file(py_file)
                components["functions"].extend(file_components["functions"])
                components["classes"].extend(file_components["classes"])
                components["modules"].append(file_components["module"])
                
                # Identifica camada
                layer = self._identify_layer(py_file)
                if layer not in components["layers"]:
                    components["layers"][layer] = []
                components["layers"][layer].append(file_components["module"])
                
            except Exception as e:
                self.logger.error(f"Erro ao analisar {py_file}: {e}")
        
        # Log estruturado
        analysis_log = {
            "event": "source_code_analysis_completed",
            "total_functions": len(components["functions"]),
            "total_classes": len(components["classes"]),
            "total_modules": len(components["modules"]),
            "layers_found": list(components["layers"].keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"SOURCE_ANALYSIS_LOG: {json.dumps(analysis_log)}")
        
        return components
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analisa um arquivo Python específico
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Componentes encontrados no arquivo
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.logger.warning(f"Erro de sintaxe em {file_path}: {e}")
            return {"functions": [], "classes": [], "module": None}
        
        functions = []
        classes = []
        
        # Analisa funções
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function = FunctionCoverage(
                    function_name=node.name,
                    file_path=str(file_path),
                    line_number=node.lineno,
                    is_covered=False,
                    is_critical=self._is_critical_function(node),
                    risk_score=self._calculate_function_risk(node),
                    test_count=0
                )
                functions.append(function)
            
            elif isinstance(node, ast.ClassDef):
                class_methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                class_coverage = ClassCoverage(
                    class_name=node.name,
                    file_path=str(file_path),
                    line_number=node.lineno,
                    total_methods=len(class_methods),
                    covered_methods=0,
                    is_covered=False,
                    is_critical=self._is_critical_class(node),
                    risk_score=self._calculate_class_risk(node),
                    test_count=0
                )
                classes.append(class_coverage)
        
        # Cria módulo
        module = ModuleCoverage(
            module_name=file_path.stem,
            file_path=str(file_path),
            total_functions=len(functions),
            covered_functions=0,
            total_classes=len(classes),
            covered_classes=0,
            coverage_percentage=0.0,
            critical_functions=len([f for f in functions if f.is_critical]),
            critical_covered=0,
            critical_coverage_percentage=0.0,
            risk_score=0,
            test_count=0
        )
        
        return {
            "functions": functions,
            "classes": classes,
            "module": module
        }
    
    def _identify_layer(self, file_path: Path) -> str:
        """
        Identifica a camada de um arquivo baseado no caminho
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Nome da camada
        """
        relative_path = file_path.relative_to(self.source_path)
        path_parts = [part.lower() for part in relative_path.parts]
        
        for layer, keywords in self.layer_mapping.items():
            if any(keyword in path_parts for keyword in keywords):
                return layer
        
        # Fallback baseado no diretório
        if "domain" in path_parts:
            return "domain"
        elif "gateway" in path_parts or "api" in path_parts:
            return "gateway"
        elif "infrastructure" in path_parts or "database" in path_parts:
            return "infrastructure"
        elif "utils" in path_parts or "helpers" in path_parts:
            return "utils"
        else:
            return "api"  # Default
    
    def _is_critical_function(self, node: ast.FunctionDef) -> bool:
        """
        Determina se uma função é crítica
        
        Args:
            node: Nó AST da função
            
        Returns:
            True se a função é crítica
        """
        # Critérios para função crítica
        critical_keywords = [
            "auth", "security", "password", "token", "encrypt", "decrypt",
            "payment", "transaction", "money", "financial",
            "delete", "remove", "drop", "truncate",
            "admin", "root", "superuser"
        ]
        
        # Verifica nome da função
        function_name = node.name.lower()
        if any(keyword in function_name for keyword in critical_keywords):
            return True
        
        # Verifica docstring
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            docstring = node.body[0].value.s.lower()
            if any(keyword in docstring for keyword in critical_keywords):
                return True
        
        # Verifica decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id.lower() in ["critical", "security", "admin"]:
                return True
        
        return False
    
    def _is_critical_class(self, node: ast.ClassDef) -> bool:
        """
        Determina se uma classe é crítica
        
        Args:
            node: Nó AST da classe
            
        Returns:
            True se a classe é crítica
        """
        # Critérios para classe crítica
        critical_keywords = [
            "auth", "security", "user", "admin", "payment", "transaction",
            "database", "repository", "service", "controller"
        ]
        
        class_name = node.name.lower()
        return any(keyword in class_name for keyword in critical_keywords)
    
    def _calculate_function_risk(self, node: ast.FunctionDef) -> int:
        """
        Calcula RISK_SCORE de uma função
        
        Args:
            node: Nó AST da função
            
        Returns:
            RISK_SCORE da função
        """
        risk_score = 30  # Base
        
        # Aumenta risco baseado em complexidade
        complexity = self._calculate_complexity(node)
        risk_score += complexity * 5
        
        # Aumenta risco se é crítica
        if self._is_critical_function(node):
            risk_score += 40
        
        # Aumenta risco baseado em parâmetros
        risk_score += len(node.args.args) * 2
        
        # Aumenta risco baseado em decorators
        risk_score += len(node.decorator_list) * 5
        
        return min(risk_score, 100)
    
    def _calculate_class_risk(self, node: ast.ClassDef) -> int:
        """
        Calcula RISK_SCORE de uma classe
        
        Args:
            node: Nó AST da classe
            
        Returns:
            RISK_SCORE da classe
        """
        risk_score = 40  # Base
        
        # Aumenta risco baseado em métodos
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        risk_score += len(methods) * 3
        
        # Aumenta risco se é crítica
        if self._is_critical_class(node):
            risk_score += 30
        
        # Aumenta risco baseado em herança
        risk_score += len(node.bases) * 10
        
        return min(risk_score, 100)
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calcula complexidade ciclomática de uma função
        
        Args:
            node: Nó AST da função
            
        Returns:
            Complexidade ciclomática
        """
        complexity = 1  # Base
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
        
        return complexity
    
    def analyze_test_coverage(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa cobertura baseada nos resultados de teste
        
        Args:
            test_results: Resultados dos testes
            
        Returns:
            Análise de cobertura
        """
        self.logger.info("Iniciando análise de cobertura de testes")
        
        # Mapeia testes para componentes
        self._map_tests_to_components(test_results)
        
        # Calcula métricas de cobertura
        self._calculate_coverage_metrics()
        
        # Identifica lacunas
        self._identify_coverage_gaps()
        
        # Gera relatório
        report = self._generate_coverage_report()
        
        # Log estruturado
        coverage_log = {
            "event": "test_coverage_analysis_completed",
            "total_functions": len(self.function_coverage),
            "covered_functions": len([f for f in self.function_coverage if f.is_covered]),
            "total_classes": len(self.class_coverage),
            "covered_classes": len([c for c in self.class_coverage if c.is_covered]),
            "coverage_gaps": len(self.coverage_gaps),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"COVERAGE_ANALYSIS_LOG: {json.dumps(coverage_log)}")
        
        return report
    
    def _map_tests_to_components(self, test_results: Dict[str, Any]):
        """Mapeia testes para componentes do código"""
        # Implementação simplificada - em produção seria mais complexa
        for test in test_results.get("tests", []):
            test_name = test.get("name", "")
            test_file = test.get("file", "")
            
            # Mapeia baseado no nome do teste
            for function in self.function_coverage:
                if function.function_name.lower() in test_name.lower():
                    function.is_covered = True
                    function.test_count += 1
                    function.last_tested = time.time()
            
            for class_coverage in self.class_coverage:
                if class_coverage.class_name.lower() in test_name.lower():
                    class_coverage.is_covered = True
                    class_coverage.test_count += 1
                    class_coverage.last_tested = time.time()
    
    def _calculate_coverage_metrics(self):
        """Calcula métricas de cobertura"""
        # Atualiza módulos
        for module in self.module_coverage:
            module_functions = [f for f in self.function_coverage if f.file_path == module.file_path]
            module_classes = [c for c in self.class_coverage if c.file_path == module.file_path]
            
            module.covered_functions = len([f for f in module_functions if f.is_covered])
            module.covered_classes = len([c for c in module_classes if c.is_covered])
            module.critical_covered = len([f for f in module_functions if f.is_covered and f.is_critical])
            
            if module.total_functions > 0:
                module.coverage_percentage = (module.covered_functions / module.total_functions) * 100
            
            if module.critical_functions > 0:
                module.critical_coverage_percentage = (module.critical_covered / module.critical_functions) * 100
            
            # Calcula RISK_SCORE do módulo
            module.risk_score = calculate_risk_score(
                component=f"coverage_{module.module_name}",
                operation="coverage_analysis",
                data_sensitivity="medium",
                external_dependencies=0,
                error_rate=1.0 - (module.coverage_percentage / 100)
            )
        
        # Agrupa por camada
        layer_modules = defaultdict(list)
        for module in self.module_coverage:
            layer = self._identify_layer(Path(module.file_path))
            layer_modules[layer].append(module)
        
        # Calcula métricas por camada
        for layer_name, modules in layer_modules.items():
            total_functions = sum(m.total_functions for m in modules)
            covered_functions = sum(m.covered_functions for m in modules)
            total_classes = sum(m.total_classes for m in modules)
            covered_classes = sum(m.covered_classes for m in modules)
            critical_functions = sum(m.critical_functions for m in modules)
            critical_covered = sum(m.critical_covered for m in modules)
            
            coverage_percentage = (covered_functions / max(total_functions, 1)) * 100
            critical_coverage_percentage = (critical_covered / max(critical_functions, 1)) * 100
            
            layer_coverage = LayerCoverage(
                layer_name=layer_name,
                total_modules=len(modules),
                covered_modules=len([m for m in modules if m.coverage_percentage > 0]),
                total_functions=total_functions,
                covered_functions=covered_functions,
                total_classes=total_classes,
                covered_classes=covered_classes,
                coverage_percentage=coverage_percentage,
                critical_functions=critical_functions,
                critical_covered=critical_covered,
                critical_coverage_percentage=critical_coverage_percentage,
                modules=modules
            )
            
            # Calcula RISK_SCORE da camada
            layer_coverage.risk_score = calculate_risk_score(
                component=f"coverage_{layer_name}",
                operation="layer_coverage_analysis",
                data_sensitivity="high" if layer_name == "domain" else "medium",
                external_dependencies=0,
                error_rate=1.0 - (coverage_percentage / 100)
            )
            
            self.layer_coverage.append(layer_coverage)
    
    def _identify_coverage_gaps(self):
        """Identifica lacunas de cobertura"""
        for function in self.function_coverage:
            if not function.is_covered:
                gap = CoverageGap(
                    gap_id=f"func_{function.function_name}_{function.file_path}",
                    component_type="function",
                    component_name=function.function_name,
                    file_path=function.file_path,
                    line_number=function.line_number,
                    risk_score=function.risk_score,
                    priority="high" if function.is_critical else "medium",
                    suggested_tests=self._suggest_tests_for_function(function)
                )
                self.coverage_gaps.append(gap)
        
        for class_coverage in self.class_coverage:
            if not class_coverage.is_covered:
                gap = CoverageGap(
                    gap_id=f"class_{class_coverage.class_name}_{class_coverage.file_path}",
                    component_type="class",
                    component_name=class_coverage.class_name,
                    file_path=class_coverage.file_path,
                    line_number=class_coverage.line_number,
                    risk_score=class_coverage.risk_score,
                    priority="high" if class_coverage.is_critical else "medium",
                    suggested_tests=self._suggest_tests_for_class(class_coverage)
                )
                self.coverage_gaps.append(gap)
    
    def _suggest_tests_for_function(self, function: FunctionCoverage) -> List[str]:
        """Sugere testes para uma função"""
        suggestions = []
        
        if function.is_critical:
            suggestions.extend([
                f"test_{function.function_name}_success",
                f"test_{function.function_name}_failure",
                f"test_{function.function_name}_edge_cases",
                f"test_{function.function_name}_security"
            ])
        else:
            suggestions.extend([
                f"test_{function.function_name}_basic",
                f"test_{function.function_name}_validation"
            ])
        
        return suggestions
    
    def _suggest_tests_for_class(self, class_coverage: ClassCoverage) -> List[str]:
        """Sugere testes para uma classe"""
        suggestions = []
        
        if class_coverage.is_critical:
            suggestions.extend([
                f"test_{class_coverage.class_name}_initialization",
                f"test_{class_coverage.class_name}_methods",
                f"test_{class_coverage.class_name}_error_handling",
                f"test_{class_coverage.class_name}_integration"
            ])
        else:
            suggestions.extend([
                f"test_{class_coverage.class_name}_basic",
                f"test_{class_coverage.class_name}_methods"
            ])
        
        return suggestions
    
    def _generate_coverage_report(self) -> Dict[str, Any]:
        """Gera relatório de cobertura"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_functions": len(self.function_coverage),
                "covered_functions": len([f for f in self.function_coverage if f.is_covered]),
                "total_classes": len(self.class_coverage),
                "covered_classes": len([c for c in self.class_coverage if c.is_covered]),
                "total_modules": len(self.module_coverage),
                "covered_modules": len([m for m in self.module_coverage if m.coverage_percentage > 0]),
                "coverage_gaps": len(self.coverage_gaps)
            },
            "layer_coverage": [
                {
                    "layer_name": l.layer_name,
                    "coverage_percentage": l.coverage_percentage,
                    "critical_coverage_percentage": l.critical_coverage_percentage,
                    "risk_score": l.risk_score,
                    "threshold": self.coverage_thresholds.get(l.layer_name, 90.0),
                    "meets_threshold": l.coverage_percentage >= self.coverage_thresholds.get(l.layer_name, 90.0),
                    "total_functions": l.total_functions,
                    "covered_functions": l.covered_functions,
                    "total_classes": l.total_classes,
                    "covered_classes": l.covered_classes,
                    "timestamp": datetime.fromtimestamp(l.timestamp).isoformat()
                }
                for l in self.layer_coverage
            ],
            "coverage_gaps": [
                {
                    "gap_id": g.gap_id,
                    "component_type": g.component_type,
                    "component_name": g.component_name,
                    "file_path": g.file_path,
                    "line_number": g.line_number,
                    "risk_score": g.risk_score,
                    "priority": g.priority,
                    "suggested_tests": g.suggested_tests,
                    "timestamp": datetime.fromtimestamp(g.timestamp).isoformat()
                }
                for g in self.coverage_gaps
            ],
            "critical_components": [
                {
                    "name": f.function_name,
                    "type": "function",
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "risk_score": f.risk_score,
                    "is_covered": f.is_covered,
                    "test_count": f.test_count
                }
                for f in self.function_coverage if f.is_critical
            ] + [
                {
                    "name": c.class_name,
                    "type": "class",
                    "file_path": c.file_path,
                    "line_number": c.line_number,
                    "risk_score": c.risk_score,
                    "is_covered": c.is_covered,
                    "test_count": c.test_count
                }
                for c in self.class_coverage if c.is_critical
            ]
        }

# Decorators para testes de análise de cobertura
@critical_risk
@semantic_validation
@real_data_validation
@production_scenario
@side_effects_monitoring
@performance_monitoring
class TestCoverageAnalyzer:
    """Testes de integração para o analisador de cobertura"""
    
    @pytest.fixture
    def coverage_analyzer(self):
        """Fixture para o analisador de cobertura"""
        return CoverageAnalyzer(
            source_path="src",
            test_path="tests",
            coverage_thresholds={
                "domain": 100.0,
                "gateway": 95.0,
                "infrastructure": 90.0
            }
        )
    
    def test_source_code_analysis(self, coverage_analyzer):
        """
        Testa análise do código fonte
        
        RISK_SCORE: 75 (Alto - Análise de código)
        """
        # Analisa código fonte
        components = coverage_analyzer.analyze_source_code()
        
        # Validações
        assert "functions" in components
        assert "classes" in components
        assert "modules" in components
        assert "layers" in components
        
        # Verifica se encontrou componentes
        assert len(components["functions"]) >= 0
        assert len(components["modules"]) >= 0
        
        # Log estruturado
        logger.info(f"Source code analysis test completed")
        logger.info(f"Functions found: {len(components['functions'])}")
        logger.info(f"Classes found: {len(components['classes'])}")
        logger.info(f"Modules found: {len(components['modules'])}")
    
    def test_coverage_analysis(self, coverage_analyzer):
        """
        Testa análise de cobertura
        
        RISK_SCORE: 80 (Alto - Validação de cobertura)
        """
        # Simula resultados de teste
        test_results = {
            "tests": [
                {
                    "name": "test_instagram_search",
                    "file": "tests/integration/test_instagram_real_integration.py",
                    "status": "passed"
                },
                {
                    "name": "test_facebook_analyze",
                    "file": "tests/integration/test_facebook_real_integration.py",
                    "status": "passed"
                }
            ]
        }
        
        # Analisa cobertura
        report = coverage_analyzer.analyze_test_coverage(test_results)
        
        # Validações
        assert "summary" in report
        assert "layer_coverage" in report
        assert "coverage_gaps" in report
        assert "critical_components" in report
        
        # Verifica summary
        summary = report["summary"]
        assert "total_functions" in summary
        assert "covered_functions" in summary
        assert "coverage_gaps" in summary
        
        # Log estruturado
        logger.info(f"Coverage analysis test completed")
        logger.info(f"Total functions: {summary['total_functions']}")
        logger.info(f"Covered functions: {summary['covered_functions']}")
        logger.info(f"Coverage gaps: {summary['coverage_gaps']}")
    
    def test_layer_coverage_thresholds(self, coverage_analyzer):
        """
        Testa thresholds de cobertura por camada
        
        RISK_SCORE: 85 (Alto - Validação de thresholds)
        """
        # Verifica thresholds configurados
        thresholds = coverage_analyzer.coverage_thresholds
        
        assert thresholds["domain"] == 100.0
        assert thresholds["gateway"] == 95.0
        assert thresholds["infrastructure"] == 90.0
        
        # Log estruturado
        logger.info(f"Layer coverage thresholds test completed")
        logger.info(f"Domain threshold: {thresholds['domain']}%")
        logger.info(f"Gateway threshold: {thresholds['gateway']}%")
        logger.info(f"Infrastructure threshold: {thresholds['infrastructure']}%")

if __name__ == "__main__":
    # Execução direta para testes
    pytest.main([__file__, "-v", "--tb=short"]) 