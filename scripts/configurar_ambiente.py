from typing import Dict, List, Optional, Any
#!/usr/bin/env python3
"""
Script de Configuração de Ambiente - Sistema de Cauda Longa

Tracing ID: CONFIG_ENV_20241220_001
Data/Hora: 2024-12-20 18:50:00 UTC
Versão: 1.0
Status: ✅ IMPLEMENTADO

Este script configura as variáveis de ambiente necessárias
para o funcionamento do sistema de cauda longa.
"""

import os
import json
from pathlib import Path
from datetime import datetime

def criar_env_template():
    """Cria arquivo .env.template com todas as variáveis necessárias."""
    template = """# Configuração do Sistema de Cauda Longa
# Gerado automaticamente em: {timestamp}

# ========================================
# CONFIGURAÇÕES GERAIS
# ========================================
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///omni_keywords_finder.db

# ========================================
# CONFIGURAÇÕES DE CAUDA LONGA
# ========================================

# Machine Learning
ML_MODEL_PATH=infrastructure/ml/models/
ML_TRAINING_INTERVAL=3600
ML_CONFIDENCE_THRESHOLD=0.7
ML_MAX_ROLLBACK_ATTEMPTS=3

# A/B Testing
AB_TESTING_DB_PATH=ab_testing.db
AB_TESTING_DEFAULT_DURATION=7
AB_TESTING_DEFAULT_SAMPLE_SIZE=1000
AB_TESTING_SIGNIFICANCE_LEVEL=0.05

# Monitoramento
MONITORING_INTERVAL_COLETA=5
MONITORING_INTERVAL_ANALISE=30
MONITORING_ALERTAS_ATIVOS=True
MONITORING_THRESHOLD_LATENCIA=5.0
MONITORING_THRESHOLD_THROUGHPUT=100

# Cache
CACHE_TIPO=hibrido
CACHE_TAMANHO_MAXIMO_MB=100
CACHE_TTL_PADRAO_MINUTOS=60
CACHE_COMPRESSAO=True
CACHE_PERSISTENCIA=True

# Feedback
FEEDBACK_AUTO_PROCESSAMENTO=True
FEEDBACK_THRESHOLD_IMPACTO=0.5
FEEDBACK_MAX_ACOES_PENDENTES=50

# Auditoria
AUDIT_INTERVALO_AUDITORIA=3600
AUDIT_RETENCAO_LOGS_DIAS=30
AUDIT_NIVEL_DETALHE=info

# ========================================
# CONFIGURAÇÕES DE SEGURANÇA
# ========================================
RATE_LIMIT_REQUESTS_PER_MINUTE=300
RATE_LIMIT_REQUESTS_PER_HOUR=5000
RATE_LIMIT_BURST_LIMIT=50

# ========================================
# CONFIGURAÇÕES DE LOG
# ========================================
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/cauda_longa.log

# ========================================
# CONFIGURAÇÕES DE PERFORMANCE
# ========================================
MAX_WORKERS=4
THREAD_POOL_SIZE=10
ASYNC_TIMEOUT=30

# ========================================
# CONFIGURAÇÕES DE BACKUP
# ========================================
BACKUP_AUTOMATICO=True
BACKUP_INTERVALO_HORAS=24
BACKUP_RETENCAO_DIAS=7

# ========================================
# CONFIGURAÇÕES DE NOTIFICAÇÕES
# ========================================
NOTIFICACOES_EMAIL=False
NOTIFICACOES_SLACK=False
NOTIFICACOES_WEBHOOK=False

# ========================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO
# ========================================
DEBUG_MODE=True
TEST_MODE=False
MOCK_EXTERNAL_APIS=True
""".format(timestamp=datetime.now().isoformat())
    
    with open(".env.template", "w", encoding="utf-8") as f:
        f.write(template)
    
    print("✅ .env.template criado")

def criar_env_desenvolvimento():
    """Cria arquivo .env para desenvolvimento."""
    env_dev = """# Configuração de Desenvolvimento - Sistema de Cauda Longa
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-2024
DATABASE_URL=sqlite:///dev_omni_keywords_finder.db

# Cauda Longa - Desenvolvimento
ML_MODEL_PATH=infrastructure/ml/models/
ML_TRAINING_INTERVAL=1800
ML_CONFIDENCE_THRESHOLD=0.6
ML_MAX_ROLLBACK_ATTEMPTS=2

AB_TESTING_DB_PATH=dev_ab_testing.db
AB_TESTING_DEFAULT_DURATION=3
AB_TESTING_DEFAULT_SAMPLE_SIZE=100
AB_TESTING_SIGNIFICANCE_LEVEL=0.1

MONITORING_INTERVAL_COLETA=10
MONITORING_INTERVAL_ANALISE=60
MONITORING_ALERTAS_ATIVOS=False
MONITORING_THRESHOLD_LATENCIA=10.0
MONITORING_THRESHOLD_THROUGHPUT=50

CACHE_TIPO=memoria
CACHE_TAMANHO_MAXIMO_MB=50
CACHE_TTL_PADRAO_MINUTOS=30
CACHE_COMPRESSAO=False
CACHE_PERSISTENCIA=False

FEEDBACK_AUTO_PROCESSAMENTO=True
FEEDBACK_THRESHOLD_IMPACTO=0.3
FEEDBACK_MAX_ACOES_PENDENTES=20

AUDIT_INTERVALO_AUDITORIA=7200
AUDIT_RETENCAO_LOGS_DIAS=7
AUDIT_NIVEL_DETALHE=debug

# Segurança - Desenvolvimento
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
RATE_LIMIT_REQUESTS_PER_HOUR=10000
RATE_LIMIT_BURST_LIMIT=100

# Log - Desenvolvimento
LOG_LEVEL=DEBUG
LOG_FORMAT=text
LOG_FILE=logs/dev_cauda_longa.log

# Performance - Desenvolvimento
MAX_WORKERS=2
THREAD_POOL_SIZE=5
ASYNC_TIMEOUT=60

# Backup - Desenvolvimento
BACKUP_AUTOMATICO=False
BACKUP_INTERVALO_HORAS=168
BACKUP_RETENCAO_DIAS=3

# Notificações - Desenvolvimento
NOTIFICACOES_EMAIL=False
NOTIFICACOES_SLACK=False
NOTIFICACOES_WEBHOOK=False

# Desenvolvimento
DEBUG_MODE=True
TEST_MODE=True
MOCK_EXTERNAL_APIS=True
"""
    
    with open(".env.development", "w", encoding="utf-8") as f:
        f.write(env_dev)
    
    print("✅ .env.development criado")

def criar_env_producao():
    """Cria arquivo .env para produção."""
    env_prod = """# Configuração de Produção - Sistema de Cauda Longa
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
DATABASE_URL=postgresql://user:pass@localhost/omni_keywords_finder

# Cauda Longa - Produção
ML_MODEL_PATH=/opt/omni/ml/models/
ML_TRAINING_INTERVAL=7200
ML_CONFIDENCE_THRESHOLD=0.8
ML_MAX_ROLLBACK_ATTEMPTS=1

AB_TESTING_DB_PATH=/var/lib/omni/ab_testing.db
AB_TESTING_DEFAULT_DURATION=14
AB_TESTING_DEFAULT_SAMPLE_SIZE=5000
AB_TESTING_SIGNIFICANCE_LEVEL=0.05

MONITORING_INTERVAL_COLETA=5
MONITORING_INTERVAL_ANALISE=30
MONITORING_ALERTAS_ATIVOS=True
MONITORING_THRESHOLD_LATENCIA=3.0
MONITORING_THRESHOLD_THROUGHPUT=200

CACHE_TIPO=hibrido
CACHE_TAMANHO_MAXIMO_MB=500
CACHE_TTL_PADRAO_MINUTOS=120
CACHE_COMPRESSAO=True
CACHE_PERSISTENCIA=True

FEEDBACK_AUTO_PROCESSAMENTO=True
FEEDBACK_THRESHOLD_IMPACTO=0.7
FEEDBACK_MAX_ACOES_PENDENTES=100

AUDIT_INTERVALO_AUDITORIA=1800
AUDIT_RETENCAO_LOGS_DIAS=90
AUDIT_NIVEL_DETALHE=info

# Segurança - Produção
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_BURST_LIMIT=10

# Log - Produção
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/omni/cauda_longa.log

# Performance - Produção
MAX_WORKERS=8
THREAD_POOL_SIZE=20
ASYNC_TIMEOUT=15

# Backup - Produção
BACKUP_AUTOMATICO=True
BACKUP_INTERVALO_HORAS=6
BACKUP_RETENCAO_DIAS=30

# Notificações - Produção
NOTIFICACOES_EMAIL=True
NOTIFICACOES_SLACK=True
NOTIFICACOES_WEBHOOK=True

# Produção
DEBUG_MODE=False
TEST_MODE=False
MOCK_EXTERNAL_APIS=False
"""
    
    with open(".env.production", "w", encoding="utf-8") as f:
        f.write(env_prod)
    
    print("✅ .env.production criado")

def criar_diretorios():
    """Cria diretórios necessários."""
    diretorios = [
        "logs",
        "infrastructure/ml/models",
        "infrastructure/cache/dados",
        "infrastructure/ab_testing/dados",
        "infrastructure/monitoring/dados",
        "infrastructure/feedback/dados",
        "infrastructure/audit/dados",
        "backups",
        "config"
    ]
    
    for diretorio in diretorios:
        Path(diretorio).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {diretorio}")

def criar_config_docker():
    """Cria arquivo docker-compose.yml para desenvolvimento."""
    docker_compose = """version: '3.8'

services:
  omni-keywords-finder:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
    volumes:
      - .:/app
      - ./logs:/app/logs
      - ./infrastructure:/app/infrastructure
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: omni_keywords_finder
      POSTGRES_USER: omni_user
      POSTGRES_PASSWORD: omni_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    print("✅ docker-compose.yml criado")

def criar_dockerfile():
    """Cria Dockerfile para o projeto."""
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -result \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements_cauda_longa.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements_cauda_longa.txt

# Copiar código
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs infrastructure/ml/models infrastructure/cache/dados

# Expor porta
EXPOSE 5000

# Comando padrão
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    print("✅ Dockerfile criado")

def main():
    """Função principal."""
    print("🔧 CONFIGURAÇÃO DE AMBIENTE - SISTEMA DE CAUDA LONGA")
    print("=" * 60)
    
    # Criar diretórios
    print("\n📁 Criando diretórios...")
    criar_diretorios()
    
    # Criar arquivos de ambiente
    print("\n⚙️ Criando arquivos de ambiente...")
    criar_env_template()
    criar_env_desenvolvimento()
    criar_env_producao()
    
    # Criar arquivos Docker
    print("\n🐳 Criando arquivos Docker...")
    criar_config_docker()
    criar_dockerfile()
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("\n📋 Próximos passos:")
    print("1. Copiar .env.development para .env")
    print("2. Ajustar configurações conforme necessário")
    print("3. Instalar dependências: pip install -r requirements_cauda_longa.txt")
    print("4. Executar: docker-compose up -data")
    print("5. Testar endpoints: http://localhost:5000/api/cauda-longa/health")

if __name__ == "__main__":
    main() 