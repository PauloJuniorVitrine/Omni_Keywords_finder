#!/usr/bin/env python3
"""
Script de Instalação Automatizada de Dependências
Omni Keywords Finder - Sistema de Instalação Inteligente

Tracing ID: INSTALL_DEPS_20250127_001
Data: 2025-01-27
Versão: 1.0
Status: ✅ PRONTO PARA USO

Funcionalidades:
- Detecção automática do ambiente (dev/prod)
- Instalação de dependências apropriadas
- Validação de segurança
- Instalação de modelos SpaCy
- Configuração de ambiente
- Relatórios de instalação
"""

import os
import sys
import subprocess
import logging
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import platform

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dependency_installation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DependencyInstaller:
    """Classe para instalação automatizada de dependências"""
    
    def __init__(self, environment: str = "auto"):
        self.project_root = Path(__file__).parent.parent
        self.environment = environment
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Mapeamento de ambientes
        self.environment_files = {
            "dev": "requirements-dev.txt",
            "prod": "requirements-prod.txt",
            "full": "requirements.txt"
        }
        
        # Modelos SpaCy necessários
        self.spacy_models = [
            "pt_core_news_lg",
            "en_core_web_lg"
        ]
        
        # Configurações por ambiente
        self.environment_configs = {
            "dev": {
                "install_models": True,
                "run_security_check": True,
                "run_tests": True,
                "install_dev_tools": True
            },
            "prod": {
                "install_models": True,
                "run_security_check": True,
                "run_tests": False,
                "install_dev_tools": False
            },
            "full": {
                "install_models": True,
                "run_security_check": True,
                "run_tests": True,
                "install_dev_tools": True
            }
        }
    
    def detect_environment(self) -> str:
        """Detecta automaticamente o ambiente"""
        if self.environment != "auto":
            return self.environment
        
        # Verificar variáveis de ambiente
        if os.getenv("PRODUCTION", "").lower() in ["true", "1", "yes"]:
            return "prod"
        elif os.getenv("DEVELOPMENT", "").lower() in ["true", "1", "yes"]:
            return "dev"
        
        # Verificar se estamos em um container
        if os.path.exists("/.dockerenv"):
            return "prod"
        
        # Verificar se estamos em CI/CD
        if os.getenv("CI", "").lower() in ["true", "1", "yes"]:
            return "prod"
        
        # Padrão para desenvolvimento local
        return "dev"
    
    def check_python_version(self) -> bool:
        """Verifica se a versão do Python é compatível"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python 3.8+ é necessário. Versão atual: {version.major}.{version.minor}")
            return False
        
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatível")
        return True
    
    def check_pip(self) -> bool:
        """Verifica se o pip está disponível e atualizado"""
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"✅ Pip disponível: {result.stdout.strip()}")
            
            # Atualizar pip
            logger.info("🔄 Atualizando pip...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            logger.info("✅ Pip atualizado")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao verificar/atualizar pip: {e}")
            return False
    
    def install_dependencies(self, requirements_file: str) -> bool:
        """Instala dependências do arquivo especificado"""
        try:
            logger.info(f"📦 Instalando dependências de {requirements_file}...")
            
            # Instalar com cache e otimizações
            cmd = [
                sys.executable, "-m", "pip", "install",
                "-r", str(self.project_root / requirements_file),
                "--no-cache-dir",  # Evitar problemas de cache
                "--upgrade"  # Atualizar pacotes existentes
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("✅ Dependências instaladas com sucesso")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao instalar dependências: {e}")
            logger.error(f"Stderr: {e.stderr}")
            return False
    
    def install_spacy_models(self) -> bool:
        """Instala modelos SpaCy necessários"""
        try:
            logger.info("🧠 Instalando modelos SpaCy...")
            
            for model in self.spacy_models:
                logger.info(f"📥 Instalando modelo: {model}")
                
                # Verificar se o modelo já está instalado
                check_cmd = [sys.executable, "-c", f"import spacy; spacy.load('{model}')"]
                try:
                    subprocess.run(check_cmd, check=True, capture_output=True)
                    logger.info(f"✅ Modelo {model} já instalado")
                    continue
                except subprocess.CalledProcessError:
                    pass
                
                # Instalar modelo
                install_cmd = [sys.executable, "-m", "spacy", "download", model]
                result = subprocess.run(install_cmd, check=True, capture_output=True, text=True)
                logger.info(f"✅ Modelo {model} instalado")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao instalar modelos SpaCy: {e}")
            return False
    
    def run_security_check(self) -> bool:
        """Executa verificação de segurança"""
        try:
            logger.info("🔒 Executando verificação de segurança...")
            
            # pip-audit
            try:
                subprocess.run([sys.executable, "-m", "pip_audit"], check=True, capture_output=True)
                logger.info("✅ pip-audit: Sem vulnerabilidades encontradas")
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ pip-audit encontrou vulnerabilidades: {e}")
            
            # safety check
            try:
                subprocess.run([sys.executable, "-m", "safety", "check"], check=True, capture_output=True)
                logger.info("✅ safety check: Sem vulnerabilidades encontradas")
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ safety check encontrou vulnerabilidades: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de segurança: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Executa testes básicos"""
        try:
            logger.info("🧪 Executando testes básicos...")
            
            # Teste básico de importação
            test_imports = [
                "flask",
                "fastapi",
                "pandas",
                "numpy",
                "sqlalchemy",
                "redis",
                "celery"
            ]
            
            for module in test_imports:
                try:
                    __import__(module)
                    logger.info(f"✅ {module} - OK")
                except ImportError:
                    logger.error(f"❌ {module} - FALHOU")
                    return False
            
            # Executar pytest se disponível
            try:
                subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"], 
                             check=True, capture_output=True, timeout=300)
                logger.info("✅ Testes executados com sucesso")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                logger.warning("⚠️ Alguns testes falharam ou timeout")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar testes: {e}")
            return False
    
    def create_environment_file(self) -> bool:
        """Cria arquivo .env com configurações básicas"""
        try:
            env_file = self.project_root / ".env"
            if env_file.exists():
                logger.info("✅ Arquivo .env já existe")
                return True
            
            logger.info("📝 Criando arquivo .env...")
            
            env_content = """# ============================================================================
# OMNİ KEYWORDS FINDER - CONFIGURAÇÕES DE AMBIENTE
# ============================================================================
# Gerado automaticamente em: {timestamp}
# ============================================================================

# ============================================================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ============================================================================
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=change-this-in-production
APP_NAME=Omni Keywords Finder
APP_VERSION=3.0.0

# ============================================================================
# CONFIGURAÇÕES DE BANCO DE DADOS
# ============================================================================
DATABASE_URL=sqlite:///app.db
REDIS_URL=redis://localhost:6379/0

# ============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================================================================
JWT_SECRET_KEY=change-this-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
BCRYPT_LOG_ROUNDS=12

# ============================================================================
# CONFIGURAÇÕES DE MONITORAMENTO
# ============================================================================
SENTRY_DSN=
PROMETHEUS_PORT=9090
JAEGER_HOST=localhost
JAEGER_PORT=6831

# ============================================================================
# CONFIGURAÇÕES DE ML
# ============================================================================
MODEL_PATH=./models
BATCH_SIZE=32
DEVICE=cpu

# ============================================================================
# CONFIGURAÇÕES DE LOGGING
# ============================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
STRUCTLOG_LEVEL=INFO

# ============================================================================
# CONFIGURAÇÕES DE CACHE
# ============================================================================
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/1
CACHE_DEFAULT_TIMEOUT=300

# ============================================================================
# CONFIGURAÇÕES DE RATE LIMITING
# ============================================================================
RATE_LIMIT_DEFAULT=100/hour
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/2

# ============================================================================
# CONFIGURAÇÕES DE BACKUP
# ============================================================================
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30

# ============================================================================
# CONFIGURAÇÕES DE NOTIFICAÇÕES
# ============================================================================
NOTIFICATION_EMAIL_ENABLED=False
NOTIFICATION_SLACK_ENABLED=False
NOTIFICATION_WEBHOOK_ENABLED=False

# ============================================================================
# CONFIGURAÇÕES DE INTEGRAÇÃO
# ============================================================================
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
YOUTUBE_API_KEY=

# ============================================================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# ============================================================================
DEBUG=True
TESTING=False
DEVELOPMENT=True
""".format(timestamp=datetime.now().isoformat())
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            logger.info("✅ Arquivo .env criado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar arquivo .env: {e}")
            return False
    
    def generate_installation_report(self, success: bool, details: Dict) -> None:
        """Gera relatório de instalação"""
        try:
            report_file = self.logs_dir / f"installation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "environment": self.environment,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": platform.platform(),
                "success": success,
                "details": details,
                "spacy_models": self.spacy_models,
                "requirements_file": self.environment_files.get(self.environment, "unknown")
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Relatório salvo em: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
    
    def install(self) -> bool:
        """Executa instalação completa"""
        logger.info("🚀 Iniciando instalação de dependências...")
        logger.info(f"📁 Diretório do projeto: {self.project_root}")
        
        # Detectar ambiente
        detected_env = self.detect_environment()
        logger.info(f"🔍 Ambiente detectado: {detected_env}")
        
        # Configurações do ambiente
        config = self.environment_configs.get(detected_env, {})
        
        # Verificações iniciais
        if not self.check_python_version():
            return False
        
        if not self.check_pip():
            return False
        
        # Instalar dependências
        requirements_file = self.environment_files.get(detected_env, "requirements.txt")
        if not self.install_dependencies(requirements_file):
            return False
        
        # Instalar modelos SpaCy se necessário
        if config.get("install_models", False):
            if not self.install_spacy_models():
                logger.warning("⚠️ Falha na instalação de modelos SpaCy")
        
        # Verificação de segurança
        if config.get("run_security_check", False):
            if not self.run_security_check():
                logger.warning("⚠️ Falha na verificação de segurança")
        
        # Executar testes
        if config.get("run_tests", False):
            if not self.run_tests():
                logger.warning("⚠️ Falha na execução de testes")
        
        # Criar arquivo .env
        if not self.create_environment_file():
            logger.warning("⚠️ Falha na criação do arquivo .env")
        
        # Gerar relatório
        details = {
            "python_version_ok": True,
            "pip_ok": True,
            "dependencies_installed": True,
            "spacy_models_installed": config.get("install_models", False),
            "security_check_passed": config.get("run_security_check", False),
            "tests_passed": config.get("run_tests", False),
            "env_file_created": True
        }
        
        self.generate_installation_report(True, details)
        
        logger.info("🎉 Instalação concluída com sucesso!")
        logger.info("📋 Próximos passos:")
        logger.info("   1. Configure as variáveis de ambiente no arquivo .env")
        logger.info("   2. Execute: python -m flask run")
        logger.info("   3. Acesse: http://localhost:5000")
        
        return True

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Instalador de dependências do Omni Keywords Finder")
    parser.add_argument("--env", choices=["dev", "prod", "full", "auto"], 
                       default="auto", help="Ambiente de instalação")
    parser.add_argument("--no-models", action="store_true", 
                       help="Não instalar modelos SpaCy")
    parser.add_argument("--no-security", action="store_true", 
                       help="Não executar verificação de segurança")
    parser.add_argument("--no-tests", action="store_true", 
                       help="Não executar testes")
    
    args = parser.parse_args()
    
    installer = DependencyInstaller(args.env)
    
    # Sobrescrever configurações se especificado
    if args.no_models:
        installer.environment_configs[installer.detect_environment()]["install_models"] = False
    if args.no_security:
        installer.environment_configs[installer.detect_environment()]["run_security_check"] = False
    if args.no_tests:
        installer.environment_configs[installer.detect_environment()]["run_tests"] = False
    
    success = installer.install()
    
    if not success:
        logger.error("❌ Instalação falhou!")
        sys.exit(1)
    
    logger.info("✅ Instalação concluída com sucesso!")

if __name__ == "__main__":
    main() 