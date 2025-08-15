#!/usr/bin/env python3
"""
Script principal para configurar dependências de forma limpa
Tracing ID: CLEANUP_DEPENDENCIES_20250127_005
Data: 2025-01-27
Versão: 1.0.0
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

def run_command(command, description):
    """Executa um comando e trata erros."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} - Sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro:")
        print(f"   Comando: {command}")
        print(f"   Erro: {e.stderr}")
        return False

def check_python_version():
    """Verifica a versão do Python."""
    print("🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} não é suportado!")
        print("   Requerido: Python 3.8+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK!")
    return True

def check_node_version():
    """Verifica a versão do Node.js."""
    print("🟢 Verificando versão do Node.js...")
    
    result = run_command("node --version", "Verificando Node.js")
    if not result:
        print("❌ Node.js não está instalado!")
        print("   Instale Node.js 18+ em: https://nodejs.org/")
        return False
    
    return True

def install_python_dependencies():
    """Instala dependências Python."""
    print("\n📦 INSTALANDO DEPENDÊNCIAS PYTHON")
    print("=" * 50)
    
    # Instala dependências de produção
    if not run_command("pip install -r requirements.txt", "Instalando dependências de produção"):
        return False
    
    # Pergunta se quer instalar dependências de desenvolvimento
    response = input("\n❓ Instalar dependências de desenvolvimento? (y/N): ").lower()
    if response in ['y', 'yes']:
        if not run_command("pip install -r requirements-dev.txt", "Instalando dependências de desenvolvimento"):
            return False
    
    return True

def install_node_dependencies():
    """Instala dependências Node.js."""
    print("\n📦 INSTALANDO DEPENDÊNCIAS NODE.JS")
    print("=" * 50)
    
    if not run_command("npm install", "Instalando dependências Node.js"):
        return False
    
    return True

def install_spacy_models():
    """Instala modelos SpaCy."""
    print("\n🧠 INSTALANDO MODELOS SPACY")
    print("=" * 50)
    
    # Executa o script de instalação de modelos
    if not run_command("python install_spacy_models.py", "Instalando modelos SpaCy"):
        return False
    
    return True

def run_audit():
    """Executa auditoria de segurança."""
    print("\n🔍 EXECUTANDO AUDITORIA DE SEGURANÇA")
    print("=" * 50)
    
    # Executa o script de auditoria
    if not run_command("python audit_dependencies.py", "Executando auditoria"):
        return False
    
    return True

def create_environment_file():
    """Cria arquivo .env de exemplo."""
    print("\n⚙️  CRIANDO ARQUIVO DE CONFIGURAÇÃO")
    print("=" * 50)
    
    env_example = """# ============================================================================
# OMNİ KEYWORDS FINDER - CONFIGURAÇÃO DE AMBIENTE
# ============================================================================
# Copie este arquivo para .env e configure as variáveis

# ============================================================================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ============================================================================
DATABASE_URL=postgresql://user:password@localhost:5432/omni_keywords
DATABASE_TEST_URL=postgresql://user:password@localhost:5432/omni_keywords_test

# ============================================================================
# CONFIGURAÇÕES DO REDIS
# ============================================================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================================================================
SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this-in-production

# ============================================================================
# CONFIGURAÇÕES DE API
# ============================================================================
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=false
API_RELOAD=false

# ============================================================================
# CONFIGURAÇÕES DE LOG
# ============================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# ============================================================================
# CONFIGURAÇÕES DE CACHE
# ============================================================================
CACHE_TTL_DEFAULT=3600
CACHE_TTL_KEYWORDS=86400
CACHE_TTL_METRICS=43200
CACHE_TTL_TRENDS=21600
CACHE_MAX_MEMORY_MB=100
CACHE_COMPRESSION_THRESHOLD=1024

# ============================================================================
# CONFIGURAÇÕES DE RATE LIMITING
# ============================================================================
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST_LIMIT=50
RATE_LIMIT_WINDOW_SIZE=60

# ============================================================================
# CONFIGURAÇÕES DE MONITORAMENTO
# ============================================================================
SENTRY_DSN=your-sentry-dsn-here
PROMETHEUS_ENABLED=true
JAEGER_ENABLED=true

# ============================================================================
# CONFIGURAÇÕES DE BACKUP
# ============================================================================
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30

# ============================================================================
# CONFIGURAÇÕES DE NOTIFICAÇÕES
# ============================================================================
SLACK_WEBHOOK_URL=your-slack-webhook-url
DISCORD_WEBHOOK_URL=your-discord-webhook-url
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# ============================================================================
# CONFIGURAÇÕES DE GOOGLE APIS
# ============================================================================
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# ============================================================================
# CONFIGURAÇÕES DE AMBIENTE
# ============================================================================
ENVIRONMENT=development
DEBUG=true
TESTING=false
"""
    
    with open(".env.example", "w") as f:
        f.write(env_example)
    
    print("✅ Arquivo .env.example criado!")
    print("   Copie para .env e configure as variáveis")
    
    return True

def main():
    """Função principal."""
    print("🚀 CONFIGURADOR DE DEPENDÊNCIAS - OMNİ KEYWORDS FINDER")
    print("=" * 70)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Verifica versões
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    # Instala dependências Python
    if not install_python_dependencies():
        print("\n❌ Falha na instalação de dependências Python!")
        sys.exit(1)
    
    # Instala dependências Node.js
    if not install_node_dependencies():
        print("\n❌ Falha na instalação de dependências Node.js!")
        sys.exit(1)
    
    # Instala modelos SpaCy
    if not install_spacy_models():
        print("\n❌ Falha na instalação de modelos SpaCy!")
        sys.exit(1)
    
    # Cria arquivo de configuração
    create_environment_file()
    
    # Executa auditoria
    run_audit()
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print("✅ Todas as dependências foram instaladas")
    print("✅ Modelos SpaCy foram configurados")
    print("✅ Arquivo de configuração foi criado")
    print("✅ Auditoria de segurança foi executada")
    print("\n📝 PRÓXIMOS PASSOS:")
    print("   1. Configure o arquivo .env com suas credenciais")
    print("   2. Configure o banco de dados PostgreSQL")
    print("   3. Configure o Redis")
    print("   4. Execute: python -m pytest tests/")
    print("   5. Execute: npm run dev")
    print("\n🔗 DOCUMENTAÇÃO:")
    print("   - README.md: Guia de instalação")
    print("   - docs/: Documentação técnica")
    print("   - .env.example: Configurações de exemplo")

if __name__ == "__main__":
    main() 