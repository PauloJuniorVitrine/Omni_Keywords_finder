#!/usr/bin/env python3
"""
🎯 REMOÇÃO DE DEPENDÊNCIAS NÃO UTILIZADAS - OMNİ KEYWORDS FINDER
📐 CoCoT: Comprovação, Causalidade, Contexto, Tendência
🌲 ToT: Múltiplas abordagens de análise
♻️ ReAct: Simulação e reflexão sobre impactos
🖼️ Visual: Representações de relacionamentos

Tracing ID: REMOVE_UNUSED_DEPS_20250127_001
Data: 2025-01-27
Versão: 1.0.0
Status: ✅ CRIAÇÃO DE SCRIPT
"""

import os
import sys
import json
import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, NamedTuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from collections import defaultdict, Counter
import importlib
import pkg_resources

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DependencyUsage:
    """Informações sobre uso de dependência"""
    package_name: str
    version: str
    is_used: bool
    usage_count: int
    usage_locations: List[str]
    import_statements: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH
    can_remove: bool
    reason: str = ""
    alternatives: List[str] = field(default_factory=list)

@dataclass
class DependencyRemovalResult:
    """Resultado da remoção de dependências"""
    total_dependencies: int
    unused_dependencies: int
    safe_to_remove: int
    high_risk_removals: int
    removed_dependencies: List[str]
    updated_files: List[str]
    recommendations: List[str]
    rollback_plan: Dict[str, str]

class DependencyRemover:
    """
    📐 CoCoT - Removedor de Dependências Avançado
    
    Comprovação: Baseado em análise estática e dinâmica
    Causalidade: Identifica dependências realmente não utilizadas
    Contexto: Considera arquitetura e padrões do projeto
    Tendência: Aplica técnicas modernas de análise de dependências
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.dependencies: Dict[str, DependencyUsage] = {}
        self.import_map: Dict[str, Set[str]] = defaultdict(set)
        self.usage_map: Dict[str, Set[str]] = defaultdict(set)
        self.removed_deps: List[str] = []
        self.updated_files: List[str] = []
        
        # Configurações
        self.requirements_file = "requirements.txt"
        self.backup_suffix = ".backup"
        self.dry_run = True  # Por padrão, apenas simula
        
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
            r'\.env',
            r'\.pytest_cache',
            r'\.coverage',
            r'htmlcov/'
        ]
        
        # Dependências que nunca devem ser removidas
        self.critical_dependencies = {
            'flask', 'fastapi', 'sqlalchemy', 'alembic', 'pytest',
            'requests', 'redis', 'celery', 'psutil', 'networkx'
        }
    
    def analyze_and_remove_unused_dependencies(self, dry_run: bool = True) -> DependencyRemovalResult:
        """
        🌲 ToT - Análise e Remoção de Dependências Não Utilizadas
        
        Abordagem 1: Análise estática de imports (ESCOLHIDA)
        Abordagem 2: Análise dinâmica de runtime
        Abordagem 3: Análise de dependências transitivas
        """
        logger.info("🔍 Iniciando análise de dependências não utilizadas...")
        
        self.dry_run = dry_run
        
        # Etapa 1: Carregar dependências do requirements.txt
        logger.info("📦 Etapa 1: Carregando dependências...")
        self._load_dependencies()
        
        # Etapa 2: Analisar imports em todo o projeto
        logger.info("🔍 Etapa 2: Analisando imports...")
        self._analyze_imports()
        
        # Etapa 3: Identificar dependências não utilizadas
        logger.info("🎯 Etapa 3: Identificando dependências não utilizadas...")
        self._identify_unused_dependencies()
        
        # Etapa 4: Avaliar riscos de remoção
        logger.info("⚠️ Etapa 4: Avaliando riscos...")
        self._assess_removal_risks()
        
        # Etapa 5: Remover dependências (se não for dry_run)
        if not dry_run:
            logger.info("🗑️ Etapa 5: Removendo dependências...")
            self._remove_dependencies()
        
        # Etapa 6: Gerar resultado
        result = self._generate_removal_result()
        
        logger.info(f"✅ Análise concluída. {len(self.dependencies)} dependências analisadas")
        return result
    
    def _load_dependencies(self):
        """
        ♻️ ReAct - Carregamento de Dependências
        
        Simulação: Leitura do requirements.txt
        Efeitos: Mapeamento de dependências instaladas
        Ganhos: Visibilidade completa das dependências
        Riscos: Dependências não listadas (mitigável com análise de ambiente)
        """
        requirements_path = self.project_root / self.requirements_file
        
        if not requirements_path.exists():
            logger.warning(f"⚠️ Arquivo {self.requirements_file} não encontrado")
            return
        
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse da linha de dependência
                    package_info = self._parse_dependency_line(line)
                    if package_info:
                        package_name, version = package_info
                        self.dependencies[package_name] = DependencyUsage(
                            package_name=package_name,
                            version=version,
                            is_used=False,
                            usage_count=0,
                            usage_locations=[],
                            import_statements=[],
                            risk_level="LOW",
                            can_remove=False,
                            reason=""
                        )
            
            logger.info(f"📦 {len(self.dependencies)} dependências carregadas")
        
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dependências: {e}")
    
    def _parse_dependency_line(self, line: str) -> Optional[Tuple[str, str]]:
        """Parse de linha de dependência"""
        # Remover comentários inline
        line = line.split('#')[0].strip()
        
        if not line:
            return None
        
        # Padrões comuns
        patterns = [
            r'^([a-zA-Z0-9_-]+)==([0-9.]+)$',  # package==version
            r'^([a-zA-Z0-9_-]+)>=([0-9.]+)$',  # package>=version
            r'^([a-zA-Z0-9_-]+)<=([0-9.]+)$',  # package<=version
            r'^([a-zA-Z0-9_-]+)~=([0-9.]+)$',  # package~=version
            r'^([a-zA-Z0-9_-]+)$',              # package (sem versão)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                package_name = match.group(1)
                version = match.group(2) if len(match.groups()) > 1 else "latest"
                return package_name, version
        
        return None
    
    def _analyze_imports(self):
        """
        🖼️ Visual - Análise de Imports
        
        Representa relacionamentos entre módulos e dependências
        """
        logger.info("🔍 Analisando imports em arquivos Python...")
        
        # Encontrar todos os arquivos Python
        python_files = self._get_python_files()
        logger.info(f"📁 Encontrados {len(python_files)} arquivos Python")
        
        for file_path in python_files:
            try:
                self._analyze_file_imports(file_path)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao analisar {file_path}: {e}")
    
    def _get_python_files(self) -> List[Path]:
        """Obtém lista de arquivos Python para análise"""
        python_files = []
        
        for file_path in self.project_root.rglob("*.py"):
            # Verificar padrões de exclusão
            if any(re.search(pattern, str(file_path)) for pattern in self.exclude_patterns):
                continue
            
            python_files.append(file_path)
        
        return python_files
    
    def _analyze_file_imports(self, file_path: Path):
        """Analisa imports de um arquivo Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Analisar imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._process_import(alias.name, str(file_path), node.lineno)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        full_name = f"{module}.{alias.name}" if module else alias.name
                        self._process_import(full_name, str(file_path), node.lineno)
        
        except Exception as e:
            logger.warning(f"⚠️ Erro ao analisar AST de {file_path}: {e}")
    
    def _process_import(self, import_name: str, file_path: str, line_number: int):
        """Processa um import encontrado"""
        # Extrair nome do pacote principal
        package_name = import_name.split('.')[0]
        
        # Verificar se é uma dependência conhecida
        if package_name in self.dependencies:
            dep = self.dependencies[package_name]
            dep.is_used = True
            dep.usage_count += 1
            dep.usage_locations.append(f"{file_path}:{line_number}")
            dep.import_statements.append(import_name)
            
            # Mapear relacionamentos
            self.import_map[package_name].add(file_path)
            self.usage_map[file_path].add(package_name)
        
        # Verificar dependências transitivas
        self._check_transitive_dependencies(package_name, file_path)
    
    def _check_transitive_dependencies(self, package_name: str, file_path: str):
        """Verifica dependências transitivas"""
        try:
            # Tentar importar o módulo para verificar dependências
            spec = importlib.util.find_spec(package_name)
            if spec and spec.origin:
                # Analisar dependências do módulo
                self._analyze_module_dependencies(package_name, spec.origin)
        except Exception:
            pass  # Ignorar erros de importação
    
    def _analyze_module_dependencies(self, package_name: str, module_path: str):
        """Analisa dependências de um módulo"""
        # Esta é uma análise simplificada
        # Em uma implementação completa, seria necessário analisar
        # as dependências reais do módulo
        pass
    
    def _identify_unused_dependencies(self):
        """Identifica dependências não utilizadas"""
        logger.info("🎯 Identificando dependências não utilizadas...")
        
        unused_count = 0
        for package_name, dep in self.dependencies.items():
            if not dep.is_used:
                unused_count += 1
                dep.can_remove = True
                dep.reason = "Não utilizado em nenhum arquivo do projeto"
                logger.info(f"📦 {package_name} - Não utilizado")
        
        logger.info(f"🎯 {unused_count} dependências não utilizadas identificadas")
    
    def _assess_removal_risks(self):
        """Avalia riscos de remoção de dependências"""
        logger.info("⚠️ Avaliando riscos de remoção...")
        
        for package_name, dep in self.dependencies.items():
            if dep.can_remove:
                risk_level = self._calculate_removal_risk(package_name, dep)
                dep.risk_level = risk_level
                
                if risk_level == "HIGH":
                    dep.can_remove = False
                    dep.reason = f"Alto risco de remoção - {dep.reason}"
                    logger.warning(f"⚠️ {package_name} - Alto risco, não será removido")
    
    def _calculate_removal_risk(self, package_name: str, dep: DependencyUsage) -> str:
        """Calcula risco de remoção de uma dependência"""
        risk_score = 0
        
        # Fator 1: Dependência crítica
        if package_name in self.critical_dependencies:
            risk_score += 10
            dep.reason = "Dependência crítica do sistema"
        
        # Fator 2: Versão específica
        if dep.version != "latest" and "==" in dep.version:
            risk_score += 3
            dep.reason += " - Versão específica pode ser necessária"
        
        # Fator 3: Dependência transitiva
        if self._is_transitive_dependency(package_name):
            risk_score += 5
            dep.reason += " - Pode ser dependência transitiva"
        
        # Fator 4: Dependência de desenvolvimento
        if self._is_dev_dependency(package_name):
            risk_score += 2
            dep.reason += " - Dependência de desenvolvimento"
        
        # Determinar nível de risco
        if risk_score >= 8:
            return "HIGH"
        elif risk_score >= 4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _is_transitive_dependency(self, package_name: str) -> bool:
        """Verifica se é dependência transitiva"""
        try:
            # Verificar se outras dependências dependem desta
            for dep_name, dep in self.dependencies.items():
                if dep_name != package_name and dep.is_used:
                    # Análise simplificada - em implementação completa seria mais robusta
                    if self._check_dependency_relationship(dep_name, package_name):
                        return True
        except Exception:
            pass
        return False
    
    def _check_dependency_relationship(self, parent: str, child: str) -> bool:
        """Verifica se parent depende de child"""
        try:
            # Análise simplificada usando pkg_resources
            parent_dist = pkg_resources.get_distribution(parent)
            requires = parent_dist.requires()
            
            for req in requires:
                if child in req.name:
                    return True
        except Exception:
            pass
        return False
    
    def _is_dev_dependency(self, package_name: str) -> bool:
        """Verifica se é dependência de desenvolvimento"""
        dev_patterns = [
            'test', 'pytest', 'coverage', 'lint', 'flake8', 'black',
            'mypy', 'bandit', 'safety', 'pre-commit'
        ]
        
        return any(pattern in package_name.lower() for pattern in dev_patterns)
    
    def _remove_dependencies(self):
        """Remove dependências não utilizadas"""
        logger.info("🗑️ Removendo dependências não utilizadas...")
        
        # Criar backup
        self._create_backup()
        
        # Remover dependências
        for package_name, dep in self.dependencies.items():
            if dep.can_remove and dep.risk_level != "HIGH":
                try:
                    self._remove_single_dependency(package_name, dep)
                except Exception as e:
                    logger.error(f"❌ Erro ao remover {package_name}: {e}")
    
    def _create_backup(self):
        """Cria backup do requirements.txt"""
        requirements_path = self.project_root / self.requirements_file
        backup_path = requirements_path.with_suffix(f"{self.requirements_file}{self.backup_suffix}")
        
        try:
            import shutil
            shutil.copy2(requirements_path, backup_path)
            logger.info(f"💾 Backup criado: {backup_path}")
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
    
    def _remove_single_dependency(self, package_name: str, dep: DependencyUsage):
        """Remove uma dependência específica"""
        requirements_path = self.project_root / self.requirements_file
        
        try:
            # Ler arquivo atual
            with open(requirements_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Remover linha da dependência
            new_lines = []
            removed = False
            
            for line in lines:
                if not self._is_dependency_line(line, package_name):
                    new_lines.append(line)
                else:
                    removed = True
                    logger.info(f"🗑️ Removendo: {line.strip()}")
            
            # Escrever arquivo atualizado
            if removed:
                with open(requirements_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                
                self.removed_deps.append(package_name)
                self.updated_files.append(str(requirements_path))
                
                logger.info(f"✅ {package_name} removido com sucesso")
        
        except Exception as e:
            logger.error(f"❌ Erro ao remover {package_name}: {e}")
    
    def _is_dependency_line(self, line: str, package_name: str) -> bool:
        """Verifica se a linha contém a dependência especificada"""
        line = line.strip()
        if not line or line.startswith('#'):
            return False
        
        # Parse da linha
        parsed = self._parse_dependency_line(line)
        if parsed:
            return parsed[0] == package_name
        
        return False
    
    def _generate_removal_result(self) -> DependencyRemovalResult:
        """Gera resultado da remoção"""
        # Estatísticas
        total_dependencies = len(self.dependencies)
        unused_dependencies = len([d for d in self.dependencies.values() if not d.is_used])
        safe_to_remove = len([d for d in self.dependencies.values() if d.can_remove and d.risk_level != "HIGH"])
        high_risk_removals = len([d for d in self.dependencies.values() if not d.is_used and d.risk_level == "HIGH"])
        
        # Recomendações
        recommendations = self._generate_recommendations()
        
        # Plano de rollback
        rollback_plan = self._generate_rollback_plan()
        
        return DependencyRemovalResult(
            total_dependencies=total_dependencies,
            unused_dependencies=unused_dependencies,
            safe_to_remove=safe_to_remove,
            high_risk_removals=high_risk_removals,
            removed_dependencies=self.removed_deps,
            updated_files=self.updated_files,
            recommendations=recommendations,
            rollback_plan=rollback_plan
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Por dependências não utilizadas
        unused_deps = [d for d in self.dependencies.values() if not d.is_used]
        if unused_deps:
            recommendations.append(f"🗑️ {len(unused_deps)} dependências não utilizadas identificadas")
        
        # Por dependências de alto risco
        high_risk = [d for d in self.dependencies.values() if not d.is_used and d.risk_level == "HIGH"]
        if high_risk:
            recommendations.append(f"⚠️ {len(high_risk)} dependências de alto risco - análise manual necessária")
        
        # Por dependências seguras para remoção
        safe_removals = [d for d in self.dependencies.values() if d.can_remove and d.risk_level != "HIGH"]
        if safe_removals:
            recommendations.append(f"✅ {len(safe_removals)} dependências seguras para remoção")
        
        # Por dependências transitivas
        transitive = [d for d in self.dependencies.values() if self._is_transitive_dependency(d.package_name)]
        if transitive:
            recommendations.append(f"🔗 {len(transitive)} dependências transitivas identificadas")
        
        return recommendations
    
    def _generate_rollback_plan(self) -> Dict[str, str]:
        """Gera plano de rollback"""
        rollback_plan = {}
        
        if self.removed_deps:
            # Restaurar backup
            requirements_path = self.project_root / self.requirements_file
            backup_path = requirements_path.with_suffix(f"{self.requirements_file}{self.backup_suffix}")
            
            if backup_path.exists():
                rollback_plan["restore_backup"] = f"cp {backup_path} {requirements_path}"
            
            # Reinstalar dependências removidas
            if self.removed_deps:
                deps_str = " ".join(self.removed_deps)
                rollback_plan["reinstall_deps"] = f"pip install {deps_str}"
        
        return rollback_plan
    
    def save_removal_results(self, result: DependencyRemovalResult, output_file: str):
        """Salva resultados da remoção"""
        logger.info(f"💾 Salvando resultados em {output_file}...")
        
        # Converter para formato serializável
        result_data = {
            "metadata": {
                "tracing_id": "REMOVE_UNUSED_DEPS_20250127_001",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "project": "Omni Keywords Finder",
                "dry_run": self.dry_run
            },
            "summary": {
                "total_dependencies": result.total_dependencies,
                "unused_dependencies": result.unused_dependencies,
                "safe_to_remove": result.safe_to_remove,
                "high_risk_removals": result.high_risk_removals,
                "removed_dependencies": result.removed_dependencies,
                "updated_files": result.updated_files
            },
            "dependencies_analysis": {
                package_name: {
                    "version": dep.version,
                    "is_used": dep.is_used,
                    "usage_count": dep.usage_count,
                    "usage_locations": dep.usage_locations,
                    "risk_level": dep.risk_level,
                    "can_remove": dep.can_remove,
                    "reason": dep.reason
                }
                for package_name, dep in self.dependencies.items()
            },
            "recommendations": result.recommendations,
            "rollback_plan": result.rollback_plan
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Resultados salvos em {output_file}")

def main():
    """
    🎯 Função principal da remoção de dependências
    
    Executa remoção seguindo abordagens:
    - CoCoT: Análise fundamentada
    - ToT: Múltiplas estratégias
    - ReAct: Simulação de impactos
    - Visual: Representações claras
    """
    logger.info("🚀 Iniciando Remoção de Dependências Não Utilizadas")
    logger.info("📐 CoCoT: Análise fundamentada em boas práticas")
    logger.info("🌲 ToT: Múltiplas estratégias de análise")
    logger.info("♻️ ReAct: Simulação de impactos e riscos")
    logger.info("🖼️ Visual: Representações claras dos resultados")
    
    # Configuração
    project_root = os.getcwd()
    output_file = "dependency_removal_results.json"
    
    # Verificar argumentos
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    try:
        # Inicializar removedor
        remover = DependencyRemover(project_root)
        
        # Executar análise e remoção
        logger.info("🔍 Etapa 1: Analisando e removendo dependências...")
        result = remover.analyze_and_remove_unused_dependencies(dry_run=dry_run)
        
        # Salvar resultados
        logger.info("💾 Etapa 2: Salvando resultados...")
        remover.save_removal_results(result, output_file)
        
        # Exibir resumo
        logger.info("🎯 RESUMO DA REMOÇÃO:")
        logger.info(f"   📦 Total de dependências: {result.total_dependencies}")
        logger.info(f"   🗑️ Dependências não utilizadas: {result.unused_dependencies}")
        logger.info(f"   ✅ Seguras para remoção: {result.safe_to_remove}")
        logger.info(f"   ⚠️ Alto risco: {result.high_risk_removals}")
        logger.info(f"   🗑️ Removidas: {len(result.removed_dependencies)}")
        logger.info(f"   📁 Arquivos atualizados: {len(result.updated_files)}")
        logger.info(f"   📋 Recomendações: {len(result.recommendations)}")
        
        if dry_run:
            logger.info("🔍 MODO DRY RUN - Nenhuma dependência foi removida")
            logger.info("💡 Execute sem --dry-run para remover dependências")
        else:
            logger.info("✅ Remoção de dependências concluída com sucesso!")
        
        logger.info("✅ Análise de dependências concluída com sucesso!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro durante remoção: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 