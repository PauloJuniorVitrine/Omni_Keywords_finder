#!/usr/bin/env python3
"""
🎯 MAPEAMENTO DE FUNCIONALIDADES CRÍTICAS - OMNİ KEYWORDS FINDER
📐 CoCoT: Comprovação, Causalidade, Contexto, Tendência
🌲 ToT: Múltiplas abordagens de análise
♻️ ReAct: Simulação e reflexão sobre impactos
🖼️ Visual: Representações de relacionamentos

Tracing ID: CRITICAL_FEATURES_MAPPER_20250127_001
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
from collections import defaultdict, Counter
import networkx as nx
import matplotlib.pyplot as plt

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CriticalFeature:
    """Funcionalidade crítica identificada"""
    name: str
    type: str  # api, service, function, class, module
    file_path: str
    line_number: int
    criticality_score: float  # 0.0 a 1.0
    impact_areas: List[str]  # performance, security, availability, data_integrity
    dependencies: List[str]
    dependents: List[str]
    complexity: int
    usage_frequency: int
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str = ""
    recommendations: List[str] = field(default_factory=list)

@dataclass
class CriticalFeaturesResult:
    """Resultado do mapeamento de funcionalidades críticas"""
    total_features: int
    critical_features: int
    high_risk_features: int
    critical_apis: int
    critical_services: int
    critical_functions: int
    critical_classes: int
    dependency_graph: Dict[str, List[str]]
    impact_analysis: Dict[str, Dict[str, float]]
    recommendations: List[str]
    risk_assessment: Dict[str, int]
    critical_paths: List[List[str]]

class CriticalFeaturesMapper:
    """
    📐 CoCoT - Mapeador de Funcionalidades Críticas Avançado
    
    Comprovação: Baseado em análise de dependências e impacto
    Causalidade: Identifica funcionalidades essenciais
    Contexto: Considera arquitetura e padrões do projeto
    Tendência: Aplica técnicas modernas de análise de sistemas
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.features: Dict[str, CriticalFeature] = {}
        self.dependency_graph = nx.DiGraph()
        self.usage_patterns: Dict[str, int] = Counter()
        self.impact_scores: Dict[str, float] = {}
        
        # Padrões de funcionalidades críticas
        self.critical_patterns = {
            "api": [
                r'@app\.route',
                r'@api\.',
                r'@router\.',
                r'def.*_api',
                r'class.*API',
                r'class.*Controller'
            ],
            "service": [
                r'class.*Service',
                r'class.*Manager',
                r'class.*Handler',
                r'def.*_service',
                r'def.*_manager'
            ],
            "database": [
                r'class.*Model',
                r'class.*Repository',
                r'def.*_query',
                r'def.*_save',
                r'def.*_delete',
                r'def.*_update'
            ],
            "security": [
                r'def.*_auth',
                r'def.*_login',
                r'def.*_logout',
                r'def.*_validate',
                r'class.*Auth',
                r'class.*Security'
            ],
            "core": [
                r'def.*main',
                r'def.*run',
                r'def.*start',
                r'def.*init',
                r'class.*Core',
                r'class.*Engine'
            ]
        }
        
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
    
    def map_critical_features(self) -> CriticalFeaturesResult:
        """
        🌲 ToT - Mapeamento Completo de Funcionalidades Críticas
        
        Abordagem 1: Análise de dependências (ESCOLHIDA)
        Abordagem 2: Análise de performance
        Abordagem 3: Análise de negócio
        """
        logger.info("🔍 Iniciando mapeamento de funcionalidades críticas...")
        
        # Etapa 1: Scan de arquivos Python
        python_files = self._get_python_files()
        logger.info(f"📁 Encontrados {len(python_files)} arquivos Python")
        
        # Etapa 2: Identificação de funcionalidades críticas
        for file_path in python_files:
            try:
                self._analyze_file_critical_features(file_path)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar {file_path}: {e}")
        
        # Etapa 3: Análise de dependências
        self._analyze_dependencies()
        
        # Etapa 4: Cálculo de scores de criticidade
        self._calculate_criticality_scores()
        
        # Etapa 5: Identificação de caminhos críticos
        critical_paths = self._identify_critical_paths()
        
        # Etapa 6: Geração de resultado
        result = self._generate_mapping_result(critical_paths)
        
        logger.info(f"✅ Mapeamento concluído. {len(self.features)} funcionalidades críticas identificadas")
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
    
    def _analyze_file_critical_features(self, file_path: Path):
        """
        ♻️ ReAct - Análise de Funcionalidades Críticas por Arquivo
        
        Simulação: Identificação de padrões críticos
        Efeitos: Mapeamento de funcionalidades essenciais
        Ganhos: Visibilidade completa do sistema
        Riscos: Falsos positivos (mitigável com validação)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Analisar diferentes tipos de funcionalidades críticas
            self._analyze_critical_apis(tree, file_path)
            self._analyze_critical_services(tree, file_path)
            self._analyze_critical_functions(tree, file_path)
            self._analyze_critical_classes(tree, file_path)
            self._analyze_critical_modules(tree, file_path)
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar AST de {file_path}: {e}")
    
    def _analyze_critical_apis(self, tree: ast.AST, file_path: Path):
        """Análise de APIs críticas"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Verificar se é API
                if any(re.search(pattern, node.name) for pattern in self.critical_patterns["api"]):
                    feature = CriticalFeature(
                        name=node.name,
                        type="api",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        criticality_score=0.0,  # Será calculado depois
                        impact_areas=["availability", "performance"],
                        dependencies=[],
                        dependents=[],
                        complexity=self._calculate_complexity(node),
                        usage_frequency=0,
                        risk_level="HIGH",
                        description=f"API endpoint: {node.name}"
                    )
                    self.features[f"api:{node.name}:{file_path}"] = feature
                    self.dependency_graph.add_node(f"api:{node.name}:{file_path}")
            
            elif isinstance(node, ast.ClassDef):
                # Verificar se é classe de API
                if any(re.search(pattern, node.name) for pattern in self.critical_patterns["api"]):
                    feature = CriticalFeature(
                        name=node.name,
                        type="api",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        criticality_score=0.0,
                        impact_areas=["availability", "performance"],
                        dependencies=[],
                        dependents=[],
                        complexity=self._calculate_complexity(node),
                        usage_frequency=0,
                        risk_level="HIGH",
                        description=f"API class: {node.name}"
                    )
                    self.features[f"api:{node.name}:{file_path}"] = feature
                    self.dependency_graph.add_node(f"api:{node.name}:{file_path}")
    
    def _analyze_critical_services(self, tree: ast.AST, file_path: Path):
        """Análise de serviços críticos"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Verificar se é serviço
                if any(re.search(pattern, node.name) for pattern in self.critical_patterns["service"]):
                    feature = CriticalFeature(
                        name=node.name,
                        type="service",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        criticality_score=0.0,
                        impact_areas=["availability", "data_integrity"],
                        dependencies=[],
                        dependents=[],
                        complexity=self._calculate_complexity(node),
                        usage_frequency=0,
                        risk_level="HIGH",
                        description=f"Service: {node.name}"
                    )
                    self.features[f"service:{node.name}:{file_path}"] = feature
                    self.dependency_graph.add_node(f"service:{node.name}:{file_path}")
    
    def _analyze_critical_functions(self, tree: ast.AST, file_path: Path):
        """Análise de funções críticas"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Verificar se é função crítica
                critical_patterns = (
                    self.critical_patterns["database"] +
                    self.critical_patterns["security"] +
                    self.critical_patterns["core"]
                )
                
                if any(re.search(pattern, node.name) for pattern in critical_patterns):
                    # Determinar tipo e áreas de impacto
                    feature_type = "function"
                    impact_areas = ["performance"]
                    
                    if any(re.search(pattern, node.name) for pattern in self.critical_patterns["database"]):
                        feature_type = "database"
                        impact_areas = ["data_integrity", "performance"]
                    elif any(re.search(pattern, node.name) for pattern in self.critical_patterns["security"]):
                        feature_type = "security"
                        impact_areas = ["security", "availability"]
                    elif any(re.search(pattern, node.name) for pattern in self.critical_patterns["core"]):
                        feature_type = "core"
                        impact_areas = ["availability", "performance"]
                    
                    feature = CriticalFeature(
                        name=node.name,
                        type=feature_type,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        criticality_score=0.0,
                        impact_areas=impact_areas,
                        dependencies=[],
                        dependents=[],
                        complexity=self._calculate_complexity(node),
                        usage_frequency=0,
                        risk_level="MEDIUM",
                        description=f"Critical function: {node.name}"
                    )
                    self.features[f"{feature_type}:{node.name}:{file_path}"] = feature
                    self.dependency_graph.add_node(f"{feature_type}:{node.name}:{file_path}")
    
    def _analyze_critical_classes(self, tree: ast.AST, file_path: Path):
        """Análise de classes críticas"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Verificar se é classe crítica
                critical_patterns = (
                    self.critical_patterns["database"] +
                    self.critical_patterns["security"] +
                    self.critical_patterns["core"]
                )
                
                if any(re.search(pattern, node.name) for pattern in critical_patterns):
                    # Determinar tipo e áreas de impacto
                    feature_type = "class"
                    impact_areas = ["performance"]
                    
                    if any(re.search(pattern, node.name) for pattern in self.critical_patterns["database"]):
                        feature_type = "database"
                        impact_areas = ["data_integrity", "performance"]
                    elif any(re.search(pattern, node.name) for pattern in self.critical_patterns["security"]):
                        feature_type = "security"
                        impact_areas = ["security", "availability"]
                    elif any(re.search(pattern, node.name) for pattern in self.critical_patterns["core"]):
                        feature_type = "core"
                        impact_areas = ["availability", "performance"]
                    
                    feature = CriticalFeature(
                        name=node.name,
                        type=feature_type,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        criticality_score=0.0,
                        impact_areas=impact_areas,
                        dependencies=[],
                        dependents=[],
                        complexity=self._calculate_complexity(node),
                        usage_frequency=0,
                        risk_level="MEDIUM",
                        description=f"Critical class: {node.name}"
                    )
                    self.features[f"{feature_type}:{node.name}:{file_path}"] = feature
                    self.dependency_graph.add_node(f"{feature_type}:{node.name}:{file_path}")
    
    def _analyze_critical_modules(self, tree: ast.AST, file_path: Path):
        """Análise de módulos críticos"""
        # Verificar se o arquivo inteiro é crítico
        file_name = file_path.name
        if any(keyword in file_name.lower() for keyword in ['main', 'core', 'engine', 'api', 'service']):
            feature = CriticalFeature(
                name=file_name,
                type="module",
                file_path=str(file_path),
                line_number=1,
                criticality_score=0.0,
                impact_areas=["availability", "performance"],
                dependencies=[],
                dependents=[],
                complexity=0,
                usage_frequency=0,
                risk_level="HIGH",
                description=f"Critical module: {file_name}"
            )
            self.features[f"module:{file_name}:{file_path}"] = feature
            self.dependency_graph.add_node(f"module:{file_name}:{file_path}")
    
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
    
    def _analyze_dependencies(self):
        """
        🖼️ Visual - Análise de Dependências
        
        Representa relacionamentos entre funcionalidades críticas
        """
        logger.info("🔗 Analisando dependências entre funcionalidades críticas...")
        
        # Analisar imports e chamadas entre funcionalidades críticas
        for feature_id, feature in self.features.items():
            # Buscar dependências no código
            dependencies = self._find_dependencies(feature)
            feature.dependencies = dependencies
            
            # Adicionar edges ao grafo
            for dep in dependencies:
                if dep in self.features:
                    self.dependency_graph.add_edge(dep, feature_id)
        
        # Calcular dependentes (reverse dependencies)
        for feature_id, feature in self.features.items():
            dependents = list(self.dependency_graph.predecessors(feature_id))
            feature.dependents = dependents
    
    def _find_dependencies(self, feature: CriticalFeature) -> List[str]:
        """Encontra dependências de uma funcionalidade"""
        dependencies = []
        
        try:
            with open(feature.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Buscar imports e chamadas
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Verificar se é funcionalidade crítica
                        for feature_id in self.features.keys():
                            if alias.name in feature_id:
                                dependencies.append(feature_id)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        full_name = f"{module}.{alias.name}" if module else alias.name
                        # Verificar se é funcionalidade crítica
                        for feature_id in self.features.keys():
                            if full_name in feature_id or alias.name in feature_id:
                                dependencies.append(feature_id)
                
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # Verificar se é chamada para funcionalidade crítica
                        for feature_id in self.features.keys():
                            if node.func.id in feature_id:
                                dependencies.append(feature_id)
        
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar dependências de {feature.name}: {e}")
        
        return dependencies
    
    def _calculate_criticality_scores(self):
        """Calcula scores de criticidade baseado em múltiplos fatores"""
        logger.info("📊 Calculando scores de criticidade...")
        
        for feature_id, feature in self.features.items():
            score = 0.0
            
            # Fator 1: Tipo de funcionalidade
            type_scores = {
                "api": 0.9,
                "service": 0.8,
                "database": 0.7,
                "security": 0.9,
                "core": 0.8,
                "function": 0.5,
                "class": 0.6,
                "module": 0.7
            }
            score += type_scores.get(feature.type, 0.5) * 0.3
            
            # Fator 2: Complexidade
            complexity_score = min(feature.complexity / 10.0, 1.0)
            score += complexity_score * 0.2
            
            # Fator 3: Número de dependentes
            dependents_score = min(len(feature.dependents) / 10.0, 1.0)
            score += dependents_score * 0.3
            
            # Fator 4: Número de dependências
            dependencies_score = min(len(feature.dependencies) / 5.0, 1.0)
            score += dependencies_score * 0.1
            
            # Fator 5: Áreas de impacto
            impact_areas_score = len(feature.impact_areas) / 4.0
            score += impact_areas_score * 0.1
            
            # Normalizar score
            feature.criticality_score = min(score, 1.0)
            
            # Atualizar nível de risco
            if feature.criticality_score >= 0.8:
                feature.risk_level = "CRITICAL"
            elif feature.criticality_score >= 0.6:
                feature.risk_level = "HIGH"
            elif feature.criticality_score >= 0.4:
                feature.risk_level = "MEDIUM"
            else:
                feature.risk_level = "LOW"
    
    def _identify_critical_paths(self) -> List[List[str]]:
        """Identifica caminhos críticos no grafo de dependências"""
        logger.info("🛤️ Identificando caminhos críticos...")
        
        critical_paths = []
        
        try:
            # Encontrar componentes fortemente conectados
            sccs = list(nx.strongly_connected_components(self.dependency_graph))
            
            # Identificar caminhos críticos
            for scc in sccs:
                if len(scc) > 1:  # Componente com múltiplos nós
                    # Calcular criticidade do componente
                    component_score = sum(
                        self.features[node_id].criticality_score 
                        for node_id in scc 
                        if node_id in self.features
                    ) / len(scc)
                    
                    if component_score >= 0.7:  # Componente crítico
                        critical_paths.append(list(scc))
            
            # Encontrar caminhos longos com alta criticidade
            for source in self.dependency_graph.nodes():
                for target in self.dependency_graph.nodes():
                    if source != target:
                        try:
                            path = nx.shortest_path(self.dependency_graph, source, target)
                            if len(path) >= 3:  # Caminho longo
                                path_score = sum(
                                    self.features[node_id].criticality_score 
                                    for node_id in path 
                                    if node_id in self.features
                                ) / len(path)
                                
                                if path_score >= 0.6:  # Caminho crítico
                                    critical_paths.append(path)
                        except nx.NetworkXNoPath:
                            continue
        
        except Exception as e:
            logger.warning(f"⚠️ Erro ao identificar caminhos críticos: {e}")
        
        return critical_paths
    
    def _generate_mapping_result(self, critical_paths: List[List[str]]) -> CriticalFeaturesResult:
        """Gera resultado do mapeamento"""
        # Estatísticas
        total_features = len(self.features)
        critical_features = len([f for f in self.features.values() if f.criticality_score >= 0.7])
        high_risk_features = len([f for f in self.features.values() if f.risk_level in ["HIGH", "CRITICAL"]])
        
        # Por tipo
        critical_apis = len([f for f in self.features.values() if f.type == "api" and f.criticality_score >= 0.7])
        critical_services = len([f for f in self.features.values() if f.type == "service" and f.criticality_score >= 0.7])
        critical_functions = len([f for f in self.features.values() if f.type == "function" and f.criticality_score >= 0.7])
        critical_classes = len([f for f in self.features.values() if f.type == "class" and f.criticality_score >= 0.7])
        
        # Grafo de dependências
        dependency_graph = {}
        for feature_id, feature in self.features.items():
            dependency_graph[feature_id] = feature.dependencies
        
        # Análise de impacto
        impact_analysis = {}
        for feature_id, feature in self.features.items():
            impact_analysis[feature_id] = {
                "availability": 0.0,
                "performance": 0.0,
                "security": 0.0,
                "data_integrity": 0.0
            }
            
            for area in feature.impact_areas:
                if area in impact_analysis[feature_id]:
                    impact_analysis[feature_id][area] = feature.criticality_score
        
        # Recomendações
        recommendations = self._generate_recommendations()
        
        # Avaliação de risco
        risk_assessment = {
            "LOW": len([f for f in self.features.values() if f.risk_level == "LOW"]),
            "MEDIUM": len([f for f in self.features.values() if f.risk_level == "MEDIUM"]),
            "HIGH": len([f for f in self.features.values() if f.risk_level == "HIGH"]),
            "CRITICAL": len([f for f in self.features.values() if f.risk_level == "CRITICAL"])
        }
        
        return CriticalFeaturesResult(
            total_features=total_features,
            critical_features=critical_features,
            high_risk_features=high_risk_features,
            critical_apis=critical_apis,
            critical_services=critical_services,
            critical_functions=critical_functions,
            critical_classes=critical_classes,
            dependency_graph=dependency_graph,
            impact_analysis=impact_analysis,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            critical_paths=critical_paths
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Por criticidade
        critical_features = [f for f in self.features.values() if f.criticality_score >= 0.8]
        if critical_features:
            recommendations.append(f"🚨 {len(critical_features)} funcionalidades críticas identificadas - priorizar monitoramento")
        
        # Por complexidade
        high_complexity = [f for f in self.features.values() if f.complexity > 10]
        if high_complexity:
            recommendations.append(f"⚠️ {len(high_complexity)} funcionalidades com alta complexidade - considerar refatoração")
        
        # Por dependências
        high_dependencies = [f for f in self.features.values() if len(f.dependents) > 5]
        if high_dependencies:
            recommendations.append(f"🔗 {len(high_dependencies)} funcionalidades com muitas dependências - risco de cascata")
        
        # Por tipo
        apis = [f for f in self.features.values() if f.type == "api"]
        if apis:
            recommendations.append(f"🌐 {len(apis)} APIs críticas - implementar rate limiting e monitoramento")
        
        services = [f for f in self.features.values() if f.type == "service"]
        if services:
            recommendations.append(f"⚙️ {len(services)} serviços críticos - implementar circuit breakers")
        
        return recommendations
    
    def save_mapping_results(self, result: CriticalFeaturesResult, output_file: str):
        """Salva resultados do mapeamento"""
        logger.info(f"💾 Salvando resultados em {output_file}...")
        
        # Converter para formato serializável
        result_data = {
            "metadata": {
                "tracing_id": "CRITICAL_FEATURES_MAPPER_20250127_001",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "project": "Omni Keywords Finder"
            },
            "summary": {
                "total_features": result.total_features,
                "critical_features": result.critical_features,
                "high_risk_features": result.high_risk_features,
                "critical_apis": result.critical_apis,
                "critical_services": result.critical_services,
                "critical_functions": result.critical_functions,
                "critical_classes": result.critical_classes
            },
            "critical_features_details": {
                feature_id: {
                    "name": feature.name,
                    "type": feature.type,
                    "file_path": feature.file_path,
                    "line_number": feature.line_number,
                    "criticality_score": feature.criticality_score,
                    "impact_areas": feature.impact_areas,
                    "dependencies": feature.dependencies,
                    "dependents": feature.dependents,
                    "complexity": feature.complexity,
                    "risk_level": feature.risk_level,
                    "description": feature.description
                }
                for feature_id, feature in self.features.items()
                if feature.criticality_score >= 0.5  # Apenas funcionalidades relevantes
            },
            "dependency_graph": result.dependency_graph,
            "impact_analysis": result.impact_analysis,
            "critical_paths": result.critical_paths,
            "recommendations": result.recommendations,
            "risk_assessment": result.risk_assessment
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Resultados salvos em {output_file}")

def main():
    """
    🎯 Função principal do mapeamento
    
    Executa mapeamento completo seguindo abordagens:
    - CoCoT: Análise fundamentada
    - ToT: Múltiplas estratégias
    - ReAct: Simulação de impactos
    - Visual: Representações claras
    """
    logger.info("🚀 Iniciando Mapeamento de Funcionalidades Críticas")
    logger.info("📐 CoCoT: Análise fundamentada em boas práticas")
    logger.info("🌲 ToT: Múltiplas estratégias de análise")
    logger.info("♻️ ReAct: Simulação de impactos e riscos")
    logger.info("🖼️ Visual: Representações claras dos resultados")
    
    # Configuração
    project_root = os.getcwd()
    output_file = "critical_features_mapping_results.json"
    
    try:
        # Inicializar mapeador
        mapper = CriticalFeaturesMapper(project_root)
        
        # Executar mapeamento
        logger.info("🔍 Etapa 1: Mapeando funcionalidades críticas...")
        result = mapper.map_critical_features()
        
        # Salvar resultados
        logger.info("💾 Etapa 2: Salvando resultados...")
        mapper.save_mapping_results(result, output_file)
        
        # Exibir resumo
        logger.info("🎯 RESUMO DO MAPEAMENTO:")
        logger.info(f"   📊 Total de funcionalidades: {result.total_features}")
        logger.info(f"   🚨 Funcionalidades críticas: {result.critical_features}")
        logger.info(f"   ⚠️ Funcionalidades de alto risco: {result.high_risk_features}")
        logger.info(f"   🌐 APIs críticas: {result.critical_apis}")
        logger.info(f"   ⚙️ Serviços críticos: {result.critical_services}")
        logger.info(f"   🔧 Funções críticas: {result.critical_functions}")
        logger.info(f"   🏗️ Classes críticas: {result.critical_classes}")
        logger.info(f"   🛤️ Caminhos críticos: {len(result.critical_paths)}")
        logger.info(f"   📋 Recomendações: {len(result.recommendations)}")
        
        logger.info("✅ Mapeamento de funcionalidades críticas concluído com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro durante mapeamento: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 