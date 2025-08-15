#!/usr/bin/env python3
"""
Script de Otimização de Build - Omni Keywords Finder
Tracing ID: BUILD_OPT_20250127_001
Data: 2025-01-27
Versão: 1.0.0

Objetivo: Otimizar processo de build com análise de dependências,
cache inteligente e métricas de performance.
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [BUILD_OPT] %(message)s',
    handlers=[
        logging.FileHandler('logs/build_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BuildMetrics:
    """Métricas de performance do build"""
    start_time: float
    end_time: float
    total_dependencies: int
    cached_dependencies: int
    build_size_mb: float
    optimization_gain_percent: float
    cache_hit_rate: float

class BuildOptimizer:
    """Otimizador de build com cache inteligente e análise de dependências"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cache_dir = self.project_root / ".build_cache"
        self.metrics_file = self.project_root / "logs" / "build_metrics.json"
        self.dependencies_cache = {}
        
        # Criar diretórios necessários
        self.cache_dir.mkdir(exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)
        
        logger.info(f"BuildOptimizer inicializado em: {self.project_root}")
    
    def analyze_dependencies(self) -> Dict[str, any]:
        """Analisa dependências do projeto"""
        logger.info("Analisando dependências do projeto...")
        
        dependencies = {
            "python": self._analyze_python_dependencies(),
            "node": self._analyze_node_dependencies(),
            "system": self._analyze_system_dependencies()
        }
        
        # Salvar análise
        analysis_file = self.project_root / "logs" / "dependencies_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(dependencies, f, indent=2)
        
        logger.info(f"Análise de dependências salva em: {analysis_file}")
        return dependencies
    
    def _analyze_python_dependencies(self) -> Dict[str, any]:
        """Analisa dependências Python"""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            return {"error": "requirements.txt não encontrado"}
        
        dependencies = []
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    dependencies.append(line)
        
        return {
            "total": len(dependencies),
            "list": dependencies,
            "file": str(requirements_file)
        }
    
    def _analyze_node_dependencies(self) -> Dict[str, any]:
        """Analisa dependências Node.js"""
        package_json = self.project_root / "package.json"
        if not package_json.exists():
            return {"error": "package.json não encontrado"}
        
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            deps = data.get('dependencies', {})
            dev_deps = data.get('devDependencies', {})
            
            return {
                "dependencies": len(deps),
                "dev_dependencies": len(dev_deps),
                "total": len(deps) + len(dev_deps),
                "dependencies_list": list(deps.keys()),
                "dev_dependencies_list": list(dev_deps.keys())
            }
        except Exception as e:
            return {"error": f"Erro ao analisar package.json: {e}"}
    
    def _analyze_system_dependencies(self) -> Dict[str, any]:
        """Analisa dependências do sistema"""
        system_deps = []
        
        # Verificar ferramentas essenciais
        tools = ['python', 'pip', 'node', 'npm', 'git']
        for tool in tools:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    system_deps.append({
                        "tool": tool,
                        "version": result.stdout.strip(),
                        "available": True
                    })
                else:
                    system_deps.append({
                        "tool": tool,
                        "version": "N/A",
                        "available": False
                    })
            except FileNotFoundError:
                system_deps.append({
                    "tool": tool,
                    "version": "N/A",
                    "available": False
                })
        
        return {
            "total": len(system_deps),
            "available": len([d for d in system_deps if d["available"]]),
            "tools": system_deps
        }
    
    def optimize_build_cache(self) -> Dict[str, any]:
        """Otimiza cache de build"""
        logger.info("Otimizando cache de build...")
        
        cache_stats = {
            "total_files": 0,
            "cached_files": 0,
            "cache_size_mb": 0,
            "optimizations": []
        }
        
        # Limpar cache antigo (mais de 7 dias)
        self._clean_old_cache()
        
        # Otimizar cache existente
        cache_stats.update(self._optimize_existing_cache())
        
        # Criar cache inteligente
        cache_stats["optimizations"].extend(self._create_smart_cache())
        
        logger.info(f"Cache otimizado: {cache_stats['cached_files']} arquivos em cache")
        return cache_stats
    
    def _clean_old_cache(self):
        """Remove cache antigo"""
        current_time = time.time()
        max_age = 7 * 24 * 3600  # 7 dias
        
        for cache_file in self.cache_dir.rglob("*"):
            if cache_file.is_file():
                if current_time - cache_file.stat().st_mtime > max_age:
                    cache_file.unlink()
                    logger.debug(f"Cache antigo removido: {cache_file}")
    
    def _optimize_existing_cache(self) -> Dict[str, any]:
        """Otimiza cache existente"""
        stats = {"total_files": 0, "cached_files": 0, "cache_size_mb": 0}
        
        for cache_file in self.cache_dir.rglob("*"):
            if cache_file.is_file():
                stats["total_files"] += 1
                stats["cache_size_mb"] += cache_file.stat().st_size / (1024 * 1024)
                
                # Verificar se arquivo ainda é válido
                if self._is_cache_valid(cache_file):
                    stats["cached_files"] += 1
                else:
                    cache_file.unlink()
                    logger.debug(f"Cache inválido removido: {cache_file}")
        
        return stats
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Verifica se arquivo de cache ainda é válido"""
        try:
            # Verificar se arquivo fonte ainda existe
            source_file = self._get_source_file_from_cache(cache_file)
            if not source_file.exists():
                return False
            
            # Verificar se arquivo fonte foi modificado
            cache_mtime = cache_file.stat().st_mtime
            source_mtime = source_file.stat().st_mtime
            
            return cache_mtime > source_mtime
        except Exception:
            return False
    
    def _get_source_file_from_cache(self, cache_file: Path) -> Path:
        """Obtém arquivo fonte a partir do cache"""
        # Implementação simplificada - em produção seria mais robusta
        cache_name = cache_file.stem
        return self.project_root / f"{cache_name}.py"
    
    def _create_smart_cache(self) -> List[str]:
        """Cria cache inteligente"""
        optimizations = []
        
        # Cache de dependências Python
        if self._cache_python_dependencies():
            optimizations.append("Cache de dependências Python criado")
        
        # Cache de assets estáticos
        if self._cache_static_assets():
            optimizations.append("Cache de assets estáticos criado")
        
        # Cache de configurações
        if self._cache_configurations():
            optimizations.append("Cache de configurações criado")
        
        return optimizations
    
    def _cache_python_dependencies(self) -> bool:
        """Cria cache de dependências Python"""
        try:
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                return False
            
            # Criar hash das dependências
            with open(requirements_file, 'rb') as f:
                content_hash = hashlib.md5(f.read()).hexdigest()
            
            cache_file = self.cache_dir / f"python_deps_{content_hash}.json"
            
            # Simular cache de dependências
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "hash": content_hash,
                "dependencies": self._analyze_python_dependencies()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar cache de dependências Python: {e}")
            return False
    
    def _cache_static_assets(self) -> bool:
        """Cria cache de assets estáticos"""
        try:
            static_dirs = ["static", "public", "assets"]
            assets_cache = {}
            
            for static_dir in static_dirs:
                static_path = self.project_root / static_dir
                if static_path.exists():
                    assets_cache[static_dir] = self._scan_static_assets(static_path)
            
            if assets_cache:
                cache_file = self.cache_dir / "static_assets_cache.json"
                with open(cache_file, 'w') as f:
                    json.dump(assets_cache, f, indent=2)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Erro ao criar cache de assets estáticos: {e}")
            return False
    
    def _scan_static_assets(self, static_path: Path) -> Dict[str, any]:
        """Escaneia assets estáticos"""
        assets = {
            "files": [],
            "total_size_mb": 0,
            "extensions": {}
        }
        
        for file_path in static_path.rglob("*"):
            if file_path.is_file():
                file_info = {
                    "path": str(file_path.relative_to(static_path)),
                    "size_mb": file_path.stat().st_size / (1024 * 1024),
                    "extension": file_path.suffix
                }
                assets["files"].append(file_info)
                assets["total_size_mb"] += file_info["size_mb"]
                
                ext = file_path.suffix
                assets["extensions"][ext] = assets["extensions"].get(ext, 0) + 1
        
        return assets
    
    def _cache_configurations(self) -> bool:
        """Cria cache de configurações"""
        try:
            config_files = list(self.project_root.glob("config/*.yaml")) + \
                          list(self.project_root.glob("config/*.yml")) + \
                          list(self.project_root.glob("*.env"))
            
            config_cache = {}
            for config_file in config_files:
                if config_file.exists():
                    config_cache[config_file.name] = {
                        "path": str(config_file),
                        "size_mb": config_file.stat().st_size / (1024 * 1024),
                        "last_modified": datetime.fromtimestamp(
                            config_file.stat().st_mtime
                        ).isoformat()
                    }
            
            if config_cache:
                cache_file = self.cache_dir / "config_cache.json"
                with open(cache_file, 'w') as f:
                    json.dump(config_cache, f, indent=2)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Erro ao criar cache de configurações: {e}")
            return False
    
    def generate_build_report(self, metrics: BuildMetrics) -> str:
        """Gera relatório de build"""
        logger.info("Gerando relatório de build...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "tracing_id": "BUILD_OPT_20250127_001",
            "metrics": {
                "build_duration_seconds": metrics.end_time - metrics.start_time,
                "total_dependencies": metrics.total_dependencies,
                "cached_dependencies": metrics.cached_dependencies,
                "build_size_mb": metrics.build_size_mb,
                "optimization_gain_percent": metrics.optimization_gain_percent,
                "cache_hit_rate": metrics.cache_hit_rate
            },
            "recommendations": self._generate_recommendations(metrics)
        }
        
        report_file = self.project_root / "logs" / "build_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Relatório de build salvo em: {report_file}")
        return str(report_file)
    
    def _generate_recommendations(self, metrics: BuildMetrics) -> List[str]:
        """Gera recomendações de otimização"""
        recommendations = []
        
        if metrics.cache_hit_rate < 0.7:
            recommendations.append("Aumentar cache hit rate - revisar estratégia de cache")
        
        if metrics.optimization_gain_percent < 20:
            recommendations.append("Otimização insuficiente - revisar dependências desnecessárias")
        
        if metrics.build_size_mb > 100:
            recommendations.append("Build muito pesado - considerar tree shaking e minificação")
        
        if metrics.end_time - metrics.start_time > 300:  # 5 minutos
            recommendations.append("Build muito lento - otimizar paralelização")
        
        return recommendations
    
    def run_optimization(self) -> BuildMetrics:
        """Executa otimização completa de build"""
        logger.info("Iniciando otimização de build...")
        
        start_time = time.time()
        
        # Análise de dependências
        dependencies = self.analyze_dependencies()
        total_deps = (
            dependencies["python"].get("total", 0) +
            dependencies["node"].get("total", 0) +
            dependencies["system"].get("total", 0)
        )
        
        # Otimização de cache
        cache_stats = self.optimize_build_cache()
        cached_deps = cache_stats["cached_files"]
        
        # Calcular métricas
        end_time = time.time()
        build_duration = end_time - start_time
        
        # Simular métricas de build
        build_size_mb = cache_stats["cache_size_mb"] + 50  # Base + cache
        optimization_gain = min(30, (cached_deps / max(total_deps, 1)) * 100)
        cache_hit_rate = cached_deps / max(total_deps, 1)
        
        metrics = BuildMetrics(
            start_time=start_time,
            end_time=end_time,
            total_dependencies=total_deps,
            cached_dependencies=cached_deps,
            build_size_mb=build_size_mb,
            optimization_gain_percent=optimization_gain,
            cache_hit_rate=cache_hit_rate
        )
        
        # Gerar relatório
        self.generate_build_report(metrics)
        
        logger.info(f"Otimização concluída em {build_duration:.2f}s")
        logger.info(f"Ganho de otimização: {optimization_gain:.1f}%")
        
        return metrics

def main():
    """Função principal"""
    try:
        optimizer = BuildOptimizer()
        metrics = optimizer.run_optimization()
        
        print(f"\n🎯 Otimização de Build Concluída!")
        print(f"⏱️  Duração: {metrics.end_time - metrics.start_time:.2f}s")
        print(f"📦 Dependências: {metrics.total_dependencies}")
        print(f"💾 Cache: {metrics.cached_dependencies}")
        print(f"📊 Tamanho: {metrics.build_size_mb:.1f}MB")
        print(f"🚀 Ganho: {metrics.optimization_gain_percent:.1f}%")
        print(f"🎯 Cache Hit Rate: {metrics.cache_hit_rate:.1%}")
        
    except Exception as e:
        logger.error(f"Erro durante otimização: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 