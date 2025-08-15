#!/usr/bin/env python3
"""
📦 Script de Otimização de Requirements
======================================

Objetivo: Otimizar requirements.txt removendo duplicatas e organizando dependências

Tracing ID: OPTIMIZE_REQS_20250127_001
Data: 2025-01-27
Versão: 1.0.0
Status: 🔴 CRÍTICO

Funcionalidades:
- Remoção de dependências duplicadas
- Organização por categorias
- Validação de versões
- Geração de requirements otimizados
- Criação de requirements-minimal.txt
"""

import os
import sys
import re
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from collections import defaultdict

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(name)s] %(message)s - %(asctime)s',
    handlers=[
        logging.FileHandler('logs/requirements_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Dependency:
    """Informações sobre uma dependência"""
    name: str
    version: str
    category: str
    is_duplicate: bool
    is_essential: bool
    usage_count: int

@dataclass
class OptimizationReport:
    """Relatório de otimização"""
    timestamp: str
    original_dependencies: int
    optimized_dependencies: int
    removed_duplicates: int
    reorganized_categories: int
    estimated_savings: int

class RequirementsOptimizer:
    """Otimizador de requirements"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.requirements_file = self.project_root / "requirements.txt"
        self.dependencies = []
        self.categories = {
            "CORE_FRAMEWORK": [],
            "HTTP_NETWORKING": [],
            "DATA_PROCESSING": [],
            "WEB_SCRAPING": [],
            "NLP_TEXT": [],
            "DATABASE_ORM": [],
            "AUTH_SECURITY": [],
            "CACHE_QUEUE": [],
            "MONITORING": [],
            "BACKUP_STORAGE": [],
            "NOTIFICATIONS": [],
            "EXPORT_TEMPLATES": [],
            "GOOGLE_APIS": [],
            "IMAGE_PROCESSING": [],
            "SCHEDULING": [],
            "INTERNATIONALIZATION": [],
            "GRAPHQL": [],
            "MACHINE_LEARNING": [],
            "VISUALIZATION": [],
            "SECURITY_VALIDATION": [],
            "TESTING": [],
            "MUTATION_TESTING": [],
            "LOAD_TESTING": [],
            "CHAOS_ENGINEERING": [],
            "HYPOTHESIS_TESTING": [],
            "TEST_REPORTING": [],
            "ENVIRONMENT_MANAGEMENT": [],
            "DEVELOPMENT_TOOLS": [],
            "DOCUMENTATION": [],
            "PERFORMANCE_PROFILING": [],
            "CONFIGURATION_MANAGEMENT": [],
            "UTILITIES": []
        }
        
        # Mapeamento de dependências para categorias
        self.category_mapping = {
            # Core Framework
            "flask": "CORE_FRAMEWORK",
            "fastapi": "CORE_FRAMEWORK",
            "uvicorn": "CORE_FRAMEWORK",
            "werkzeug": "CORE_FRAMEWORK",
            "itsdangerous": "CORE_FRAMEWORK",
            "click": "CORE_FRAMEWORK",
            "jinja2": "CORE_FRAMEWORK",
            "python-dotenv": "CORE_FRAMEWORK",
            "flask-cors": "CORE_FRAMEWORK",
            "flask-sqlalchemy": "CORE_FRAMEWORK",
            "flask-migrate": "CORE_FRAMEWORK",
            "flask-babel": "CORE_FRAMEWORK",
            "flask-limiter": "CORE_FRAMEWORK",
            "flask-swagger-ui": "CORE_FRAMEWORK",
            "flask-graphql": "CORE_FRAMEWORK",
            
            # HTTP and Networking
            "requests": "HTTP_NETWORKING",
            "aiohttp": "HTTP_NETWORKING",
            "httpx": "HTTP_NETWORKING",
            "requests-oauthlib": "HTTP_NETWORKING",
            "urllib3": "HTTP_NETWORKING",
            "certifi": "HTTP_NETWORKING",
            
            # Data Processing
            "pandas": "DATA_PROCESSING",
            "numpy": "DATA_PROCESSING",
            "scikit-learn": "DATA_PROCESSING",
            "openpyxl": "DATA_PROCESSING",
            "python-dateutil": "DATA_PROCESSING",
            "pyyaml": "DATA_PROCESSING",
            "scipy": "DATA_PROCESSING",
            "joblib": "DATA_PROCESSING",
            
            # Web Scraping
            "beautifulsoup4": "WEB_SCRAPING",
            "lxml": "WEB_SCRAPING",
            "youtube-transcript-api": "WEB_SCRAPING",
            "selenium": "WEB_SCRAPING",
            "webdriver-manager": "WEB_SCRAPING",
            
            # NLP and Text Processing
            "nltk": "NLP_TEXT",
            "textblob": "NLP_TEXT",
            "spacy": "NLP_TEXT",
            "sentence-transformers": "NLP_TEXT",
            "transformers": "NLP_TEXT",
            "torch": "NLP_TEXT",
            "tokenizers": "NLP_TEXT",
            
            # Database and ORM
            "sqlalchemy": "DATABASE_ORM",
            "alembic": "DATABASE_ORM",
            "pydantic": "DATABASE_ORM",
            "psycopg2-binary": "DATABASE_ORM",
            "pymongo": "DATABASE_ORM",
            "redis": "DATABASE_ORM",
            "aioredis": "DATABASE_ORM",
            
            # Authentication and Security
            "flask-jwt-extended": "AUTH_SECURITY",
            "python-jose": "AUTH_SECURITY",
            "passlib": "AUTH_SECURITY",
            "authlib": "AUTH_SECURITY",
            "cryptography": "AUTH_SECURITY",
            "bcrypt": "AUTH_SECURITY",
            "python-multipart": "AUTH_SECURITY",
            
            # Cache and Queue
            "celery": "CACHE_QUEUE",
            "kombu": "CACHE_QUEUE",
            "billiard": "CACHE_QUEUE",
            
            # Monitoring
            "opentelemetry-api": "MONITORING",
            "opentelemetry-sdk": "MONITORING",
            "opentelemetry-exporter-jaeger": "MONITORING",
            "opentelemetry-exporter-prometheus": "MONITORING",
            "opentelemetry-instrumentation-flask": "MONITORING",
            "opentelemetry-instrumentation-fastapi": "MONITORING",
            "prometheus-client": "MONITORING",
            "prometheus_flask_exporter": "MONITORING",
            "sentry-sdk": "MONITORING",
            "structlog": "MONITORING",
            "python-json-logger": "MONITORING",
            "watchdog": "MONITORING",
            
            # Backup and Storage
            "boto3": "BACKUP_STORAGE",
            "azure-storage-blob": "BACKUP_STORAGE",
            "google-cloud-storage": "BACKUP_STORAGE",
            "paramiko": "BACKUP_STORAGE",
            "schedule": "BACKUP_STORAGE",
            "psutil": "BACKUP_STORAGE",
            
            # Notifications
            "websockets": "NOTIFICATIONS",
            "asyncio-mqtt": "NOTIFICATIONS",
            "paho-mqtt": "NOTIFICATIONS",
            
            # Export and Templates
            "python-pptx": "EXPORT_TEMPLATES",
            "reportlab": "EXPORT_TEMPLATES",
            "markdown": "EXPORT_TEMPLATES",
            "mako": "EXPORT_TEMPLATES",
            
            # Google APIs
            "google-api-python-client": "GOOGLE_APIS",
            "google-auth-httplib2": "GOOGLE_APIS",
            "google-auth-oauthlib": "GOOGLE_APIS",
            "google-auth": "GOOGLE_APIS",
            
            # Image Processing
            "pillow": "IMAGE_PROCESSING",
            
            # Scheduling
            "apscheduler": "SCHEDULING",
            
            # Internationalization
            "flask_babel": "INTERNATIONALIZATION",
            "babel": "INTERNATIONALIZATION",
            
            # GraphQL
            "graphene": "GRAPHQL",
            "graphql-core": "GRAPHQL",
            
            # Machine Learning
            "tensorflow": "MACHINE_LEARNING",
            "keras": "MACHINE_LEARNING",
            "prophet": "MACHINE_LEARNING",
            "statsmodels": "MACHINE_LEARNING",
            
            # Visualization
            "matplotlib": "VISUALIZATION",
            "seaborn": "VISUALIZATION",
            "plotly": "VISUALIZATION",
            "dash": "VISUALIZATION",
            "dash-bootstrap-components": "VISUALIZATION",
            
            # Security and Validation
            "pip-audit": "SECURITY_VALIDATION",
            "safety": "SECURITY_VALIDATION",
            "bandit": "SECURITY_VALIDATION",
            "semgrep": "SECURITY_VALIDATION",
            "pylint": "SECURITY_VALIDATION",
            "flake8": "SECURITY_VALIDATION",
            "black": "SECURITY_VALIDATION",
            "isort": "SECURITY_VALIDATION",
            "mypy": "SECURITY_VALIDATION",
            
            # Testing
            "pytest": "TESTING",
            "pytest-cov": "TESTING",
            "pytest-asyncio": "TESTING",
            "pytest-html": "TESTING",
            "pytest-xdist": "TESTING",
            "pytest-timeout": "TESTING",
            "pytest-mock": "TESTING",
            "pytest-playwright": "TESTING",
            "playwright": "TESTING",
            "pytest-axe": "TESTING",
            "freezegun": "TESTING",
            "faker": "TESTING",
            "factory-boy": "TESTING",
            "responses": "TESTING",
            "httpretty": "TESTING",
            "coverage": "TESTING",
            "coverage-badge": "TESTING",
            
            # Development Tools
            "ipython": "DEVELOPMENT_TOOLS",
            "ipdb": "DEVELOPMENT_TOOLS",
            "memory-profiler": "DEVELOPMENT_TOOLS",
            "line-profiler": "DEVELOPMENT_TOOLS",
            "pre-commit": "DEVELOPMENT_TOOLS",
            "nodemon": "DEVELOPMENT_TOOLS",
            
            # Documentation
            "sphinx": "DOCUMENTATION",
            "sphinx-rtd-theme": "DOCUMENTATION",
            "myst-parser": "DOCUMENTATION",
            
            # Performance and Profiling
            "py-spy": "PERFORMANCE_PROFILING",
            "pyinstrument": "PERFORMANCE_PROFILING",
            "scalene": "PERFORMANCE_PROFILING",
            
            # Configuration Management
            "configparser": "CONFIGURATION_MANAGEMENT",
            "python-decouple": "CONFIGURATION_MANAGEMENT",
            
            # Utilities
            "rich": "UTILITIES",
            "tqdm": "UTILITIES",
            "colorama": "UTILITIES",
            "tabulate": "UTILITIES"
        }
        
        # Dependências essenciais para produção
        self.essential_deps = {
            "flask", "fastapi", "uvicorn", "requests", "pandas", "numpy",
            "sqlalchemy", "alembic", "pydantic", "psycopg2-binary", "redis",
            "celery", "python-dotenv", "click", "jinja2", "werkzeug",
            "itsdangerous", "flask-cors", "flask-sqlalchemy", "flask-migrate",
            "beautifulsoup4", "lxml", "nltk", "spacy", "scikit-learn",
            "opentelemetry-api", "opentelemetry-sdk", "prometheus-client",
            "sentry-sdk", "structlog", "boto3", "cryptography", "bcrypt",
            "flask-jwt-extended", "passlib", "authlib", "websockets",
            "apscheduler", "flask_babel", "graphene", "matplotlib",
            "pytest", "coverage", "black", "flake8", "mypy"
        }
    
    def parse_requirements_file(self) -> List[Dependency]:
        """Analisa o arquivo requirements.txt"""
        logger.info("📋 Analisando arquivo requirements.txt...")
        
        if not self.requirements_file.exists():
            logger.error(f"❌ Arquivo {self.requirements_file} não encontrado")
            return []
        
        dependencies = []
        current_category = "UTILITIES"  # Categoria padrão
        
        with open(self.requirements_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Pular linhas vazias e comentários
                if not line or line.startswith('#'):
                    # Detectar mudança de categoria
                    if "CORE FRAMEWORK" in line.upper():
                        current_category = "CORE_FRAMEWORK"
                    elif "HTTP" in line.upper() and "NETWORKING" in line.upper():
                        current_category = "HTTP_NETWORKING"
                    elif "DATA PROCESSING" in line.upper():
                        current_category = "DATA_PROCESSING"
                    elif "WEB SCRAPING" in line.upper():
                        current_category = "WEB_SCRAPING"
                    elif "NLP" in line.upper() and "TEXT" in line.upper():
                        current_category = "NLP_TEXT"
                    elif "DATABASE" in line.upper() and "ORM" in line.upper():
                        current_category = "DATABASE_ORM"
                    elif "AUTH" in line.upper() and "SECURITY" in line.upper():
                        current_category = "AUTH_SECURITY"
                    elif "CACHE" in line.upper() and "QUEUE" in line.upper():
                        current_category = "CACHE_QUEUE"
                    elif "MONITORING" in line.upper():
                        current_category = "MONITORING"
                    elif "BACKUP" in line.upper() and "STORAGE" in line.upper():
                        current_category = "BACKUP_STORAGE"
                    elif "NOTIFICATIONS" in line.upper():
                        current_category = "NOTIFICATIONS"
                    elif "EXPORT" in line.upper() and "TEMPLATES" in line.upper():
                        current_category = "EXPORT_TEMPLATES"
                    elif "GOOGLE" in line.upper() and "APIS" in line.upper():
                        current_category = "GOOGLE_APIS"
                    elif "IMAGE" in line.upper() and "PROCESSING" in line.upper():
                        current_category = "IMAGE_PROCESSING"
                    elif "SCHEDULING" in line.upper():
                        current_category = "SCHEDULING"
                    elif "INTERNATIONALIZATION" in line.upper():
                        current_category = "INTERNATIONALIZATION"
                    elif "GRAPHQL" in line.upper():
                        current_category = "GRAPHQL"
                    elif "MACHINE" in line.upper() and "LEARNING" in line.upper():
                        current_category = "MACHINE_LEARNING"
                    elif "VISUALIZATION" in line.upper():
                        current_category = "VISUALIZATION"
                    elif "SECURITY" in line.upper() and "VALIDATION" in line.upper():
                        current_category = "SECURITY_VALIDATION"
                    elif "TESTING" in line.upper():
                        current_category = "TESTING"
                    elif "DEVELOPMENT" in line.upper() and "TOOLS" in line.upper():
                        current_category = "DEVELOPMENT_TOOLS"
                    elif "DOCUMENTATION" in line.upper():
                        current_category = "DOCUMENTATION"
                    elif "PERFORMANCE" in line.upper() and "PROFILING" in line.upper():
                        current_category = "PERFORMANCE_PROFILING"
                    elif "CONFIGURATION" in line.upper() and "MANAGEMENT" in line.upper():
                        current_category = "CONFIGURATION_MANAGEMENT"
                    continue
                
                # Extrair dependência
                dep_match = re.match(r'^([a-zA-Z0-9_-]+)(.*)$', line)
                if dep_match:
                    name = dep_match.group(1).lower()
                    version = dep_match.group(2).strip()
                    
                    # Determinar categoria
                    category = self.category_mapping.get(name, current_category)
                    
                    # Verificar se é essencial
                    is_essential = name in self.essential_deps
                    
                    dependency = Dependency(
                        name=name,
                        version=version,
                        category=category,
                        is_duplicate=False,
                        is_essential=is_essential,
                        usage_count=1
                    )
                    
                    dependencies.append(dependency)
        
        self.dependencies = dependencies
        logger.info(f"📊 Encontradas {len(dependencies)} dependências")
        return dependencies
    
    def remove_duplicates(self) -> List[Dependency]:
        """Remove dependências duplicadas"""
        logger.info("🔍 Removendo dependências duplicadas...")
        
        seen_deps = {}
        unique_deps = []
        removed_count = 0
        
        for dep in self.dependencies:
            if dep.name in seen_deps:
                # Incrementar contador de uso
                seen_deps[dep.name].usage_count += 1
                seen_deps[dep.name].is_duplicate = True
                removed_count += 1
                logger.info(f"🗑️ Removida duplicata: {dep.name}")
            else:
                seen_deps[dep.name] = dep
                unique_deps.append(dep)
        
        self.dependencies = unique_deps
        logger.info(f"✅ Removidas {removed_count} dependências duplicadas")
        return unique_deps
    
    def organize_by_categories(self) -> Dict[str, List[Dependency]]:
        """Organiza dependências por categorias"""
        logger.info("📂 Organizando dependências por categorias...")
        
        for dep in self.dependencies:
            category = dep.category
            if category in self.categories:
                self.categories[category].append(dep)
            else:
                self.categories["UTILITIES"].append(dep)
        
        # Remover categorias vazias
        self.categories = {k: v for k, v in self.categories.items() if v}
        
        logger.info(f"📂 Organizadas em {len(self.categories)} categorias")
        return self.categories
    
    def create_optimized_requirements(self) -> str:
        """Cria requirements.txt otimizado"""
        logger.info("📝 Criando requirements.txt otimizado...")
        
        # Criar backup
        backup_path = self.project_root / f"requirements_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        shutil.copy2(self.requirements_file, backup_path)
        logger.info(f"💾 Backup criado: {backup_path}")
        
        # Gerar novo arquivo
        optimized_content = self._generate_requirements_content()
        
        with open(self.requirements_file, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
        
        logger.info(f"✅ Requirements.txt otimizado criado")
        return str(self.requirements_file)
    
    def _generate_requirements_content(self) -> str:
        """Gera conteúdo do requirements.txt otimizado"""
        content = f"""# ============================================================================
# OMNİ KEYWORDS FINDER - REQUIREMENTS.TXT OTIMIZADO
# ============================================================================
# Tracing ID: OPTIMIZE_REQS_20250127_001
# Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Versão: 4.0.0
# Status: ✅ OTIMIZADO E ORGANIZADO
# ============================================================================
# Total de dependências: {len(self.dependencies)}
# Dependências removidas: {sum(1 for d in self.dependencies if d.is_duplicate)}
# ============================================================================

"""
        
        # Adicionar dependências por categoria
        for category_name, deps in self.categories.items():
            if not deps:
                continue
            
            # Converter nome da categoria para formato legível
            readable_name = category_name.replace('_', ' ').title()
            
            content += f"# ============================================================================\n"
            content += f"# {readable_name} - OTIMIZADO\n"
            content += f"# ============================================================================\n"
            
            # Ordenar dependências por nome
            sorted_deps = sorted(deps, key=lambda x: x.name)
            
            for dep in sorted_deps:
                duplicate_marker = "  # DUPLICATA REMOVIDA" if dep.is_duplicate else ""
                essential_marker = "  # ESSENCIAL" if dep.is_essential else ""
                content += f"{dep.name}{dep.version}{duplicate_marker}{essential_marker}\n"
            
            content += "\n"
        
        # Adicionar notas importantes
        content += f"""# ============================================================================
# NOTAS IMPORTANTES - OTIMIZAÇÃO CONCLUÍDA
# ============================================================================
# 1. Dependências duplicadas foram removidas
# 2. Organização por categorias otimizada
# 3. Dependências essenciais marcadas
# 4. Backup criado antes da otimização
# 5. Para produção, use apenas dependências essenciais
# 6. Execute auditoria semanal: pip-audit && safety check
# 7. Modelos SpaCy devem ser instalados separadamente:
#    python -m spacy download pt_core_news_lg
#    python -m spacy download en_core_web_lg
# 8. Para desenvolvimento completo, use: pip install -r requirements-dev.txt
# 9. Para produção, use: pip install -r requirements.txt
# 10. Execute testes após instalação: pytest tests/ -v
# ============================================================================
"""
        
        return content
    
    def create_minimal_requirements(self) -> str:
        """Cria requirements-minimal.txt para produção"""
        logger.info("📦 Criando requirements-minimal.txt...")
        
        minimal_file = self.project_root / "requirements-minimal.txt"
        
        minimal_content = f"""# ============================================================================
# OMNİ KEYWORDS FINDER - REQUIREMENTS-MINIMAL.TXT
# ============================================================================
# Tracing ID: OPTIMIZE_REQS_20250127_001
# Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Versão: 1.0.0
# Status: ✅ MÍNIMO PARA PRODUÇÃO
# ============================================================================
# Apenas dependências essenciais para produção
# Total: {len([d for d in self.dependencies if d.is_essential])} dependências
# ============================================================================

"""
        
        # Adicionar apenas dependências essenciais
        essential_deps = [d for d in self.dependencies if d.is_essential]
        sorted_essential = sorted(essential_deps, key=lambda x: x.name)
        
        for dep in sorted_essential:
            minimal_content += f"{dep.name}{dep.version}  # ESSENCIAL\n"
        
        minimal_content += f"""
# ============================================================================
# NOTAS PARA PRODUÇÃO
# ============================================================================
# 1. Apenas dependências essenciais incluídas
# 2. Instale com: pip install -r requirements-minimal.txt
# 3. Para desenvolvimento, use requirements.txt completo
# 4. Execute auditoria: pip-audit
# 5. Teste antes do deploy
# ============================================================================
"""
        
        with open(minimal_file, 'w', encoding='utf-8') as f:
            f.write(minimal_content)
        
        logger.info(f"✅ Requirements-minimal.txt criado")
        return str(minimal_file)
    
    def create_validation_script(self) -> str:
        """Cria script de validação de dependências"""
        logger.info("🔍 Criando script de validação...")
        
        validation_script = self.project_root / "scripts" / "validate_dependencies.py"
        validation_script.parent.mkdir(exist_ok=True)
        
        script_content = f'''#!/usr/bin/env python3
"""
🔍 Script de Validação de Dependências
=====================================

Objetivo: Validar dependências do projeto Omni Keywords Finder

Tracing ID: VALIDATE_DEPS_20250127_001
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Versão: 1.0.0
Status: 🔴 CRÍTICO
"""

import subprocess
import sys
import json
from pathlib import Path

def validate_dependencies():
    """Valida dependências do projeto"""
    print("🔍 Validando dependências...")
    
    # Verificar se pip está disponível
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ pip não está disponível")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar pip: {{e}}")
        return False
    
    # Verificar dependências instaladas
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            installed_packages = json.loads(result.stdout)
            print(f"✅ {{len(installed_packages)}} pacotes instalados")
        else:
            print("❌ Erro ao listar pacotes instalados")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar pacotes instalados: {{e}}")
        return False
    
    # Verificar vulnerabilidades
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'audit'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Nenhuma vulnerabilidade encontrada")
        else:
            print("⚠️ Vulnerabilidades encontradas:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar auditoria: {{e}}")
        return False
    
    print("✅ Validação concluída com sucesso!")
    return True

if __name__ == "__main__":
    success = validate_dependencies()
    sys.exit(0 if success else 1)
'''
        
        with open(validation_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Tornar executável
        validation_script.chmod(0o755)
        
        logger.info(f"✅ Script de validação criado: {validation_script}")
        return str(validation_script)
    
    def generate_report(self) -> str:
        """Gera relatório de otimização"""
        logger.info("📊 Gerando relatório de otimização...")
        
        report_path = self.project_root / "docs" / "RELATORIO_OTIMIZACAO_REQUIREMENTS.md"
        report_path.parent.mkdir(exist_ok=True)
        
        total_deps = len(self.dependencies)
        duplicate_deps = sum(1 for d in self.dependencies if d.is_duplicate)
        essential_deps = sum(1 for d in self.dependencies if d.is_essential)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 📦 Relatório de Otimização de Requirements\n\n")
            f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Tracing ID**: OPTIMIZE_REQS_20250127_001\n")
            f.write(f"**Status**: ✅ CONCLUÍDO\n\n")
            
            f.write("## 📊 Resumo Executivo\n\n")
            f.write(f"- **Total de dependências**: {total_deps}\n")
            f.write(f"- **Dependências duplicadas removidas**: {duplicate_deps}\n")
            f.write(f"- **Dependências essenciais**: {essential_deps}\n")
            f.write(f"- **Categorias organizadas**: {len(self.categories)}\n\n")
            
            f.write("## 📂 Organização por Categorias\n\n")
            
            for category_name, deps in self.categories.items():
                readable_name = category_name.replace('_', ' ').title()
                essential_count = sum(1 for d in deps if d.is_essential)
                
                f.write(f"### {readable_name}\n\n")
                f.write(f"- **Total**: {len(deps)} dependências\n")
                f.write(f"- **Essenciais**: {essential_count}\n\n")
                
                for dep in sorted(deps, key=lambda x: x.name):
                    essential_marker = " ✅" if dep.is_essential else ""
                    f.write(f"- `{dep.name}{dep.version}`{essential_marker}\n")
                
                f.write("\n")
            
            f.write("## 🎯 Dependências Essenciais\n\n")
            essential_deps = [d for d in self.dependencies if d.is_essential]
            for dep in sorted(essential_deps, key=lambda x: x.name):
                f.write(f"- `{dep.name}{dep.version}`\n")
        
        logger.info(f"✅ Relatório salvo em: {report_path}")
        return str(report_path)

def main():
    """Função principal"""
    logger.info("🚀 Iniciando otimização de requirements...")
    
    # Configurar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Inicializar otimizador
    optimizer = RequirementsOptimizer(".")
    
    try:
        # Executar otimização
        optimizer.parse_requirements_file()
        optimizer.remove_duplicates()
        optimizer.organize_by_categories()
        
        # Criar arquivos otimizados
        optimized_file = optimizer.create_optimized_requirements()
        minimal_file = optimizer.create_minimal_requirements()
        validation_script = optimizer.create_validation_script()
        
        # Gerar relatório
        report_path = optimizer.generate_report()
        
        logger.info("✅ Otimização de requirements concluída com sucesso!")
        logger.info(f"📊 Relatório gerado: {report_path}")
        logger.info(f"📦 Requirements otimizado: {optimized_file}")
        logger.info(f"📦 Requirements minimal: {minimal_file}")
        logger.info(f"🔍 Script de validação: {validation_script}")
        
    except Exception as e:
        logger.error(f"❌ Erro durante otimização: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 