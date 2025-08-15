# 📋 IMP-010: Dockerfile Principal - Omni Keywords Finder
# 🎯 Objetivo: Containerização otimizada, segura e performática
# 📅 Criado: 2024-12-27
# 🔄 Versão: 2.0

# ========================================
# 🏗️ STAGE 1: BUILD STAGE
# ========================================
FROM python:3.11-slim as builder

# Definir variáveis de ambiente para build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema para build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .
COPY requirements-dev.txt .

# Instalar dependências Python
RUN pip install --user --no-cache-dir -r requirements.txt

# ========================================
# 🚀 STAGE 2: PRODUCTION STAGE
# ========================================
FROM python:3.11-slim as production

# Definir variáveis de ambiente para produção
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production \
    LOG_LEVEL=info

# Instalar dependências do sistema para produção
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar dependências Python do stage anterior
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Criar diretórios necessários
RUN mkdir -p \
    logs \
    infrastructure/ml/models \
    infrastructure/cache/dados \
    infrastructure/backup \
    && chown -R appuser:appuser /app

# Expor porta da aplicação
EXPOSE 8000

# Mudar para usuário não-root
USER appuser

# Adicionar diretório local ao PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ========================================
# 🧪 STAGE 3: TESTING STAGE
# ========================================
FROM production as testing

# Definir variáveis de ambiente para testes
ENV ENVIRONMENT=testing \
    LOG_LEVEL=debug \
    TEST_MODE=true

# Instalar dependências de desenvolvimento
RUN pip install --user --no-cache-dir -r requirements-dev.txt

# Comando para testes
CMD ["pytest", "tests/", "--cov=./", "--cov-report=xml", "--cov-report=html"]

# ========================================
# 🔧 STAGE 4: DEVELOPMENT STAGE
# ========================================
FROM production as development

# Definir variáveis de ambiente para desenvolvimento
ENV ENVIRONMENT=development \
    LOG_LEVEL=debug \
    DEBUG=true

# Instalar dependências de desenvolvimento
RUN pip install --user --no-cache-dir -r requirements-dev.txt

# Comando para desenvolvimento
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 