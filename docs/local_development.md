# Guia de Desenvolvimento Local

Este documento detalha o processo de desenvolvimento local do Omni Keywords Finder.

## Ambiente

### 1. Requisitos

```bash
# Requisitos mínimos
- Python 3.9+
- Node.js 16+
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+
```

### 2. Configuração

```bash
# Clonar repositório
git clone https://github.com/your-org/omni-keywords-finder.git
cd omni-keywords-finder

# Criar ambiente virtual Python
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências Python
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Instalar dependências Node
npm install
```

## Banco de Dados

### 1. MongoDB

```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secret

volumes:
  mongodb_data:
```

### 2. Redis

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:6.2
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## API

### 1. Configuração

```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Ambiente
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "debug"
    
    # API
    API_VERSION: str = "v1"
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    
    # Banco de Dados
    MONGODB_URI: str = "mongodb://admin:secret@localhost:27017"
    MONGODB_DB: str = "omni_keywords"
    REDIS_URI: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
```

### 2. Execução

```bash
# Iniciar serviços
docker-compose up -d

# Executar API
uvicorn app.main:app --reload --port 8000

# Executar testes
pytest

# Executar linting
flake8
black .
isort .
mypy .
```

## Frontend

### 1. Configuração

```typescript
// src/config/settings.ts
export const settings = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  environment: process.env.NODE_ENV || 'development',
  debug: process.env.NODE_ENV !== 'production'
};
```

### 2. Execução

```bash
# Executar em desenvolvimento
npm run dev

# Executar testes
npm test

# Executar linting
npm run lint
npm run format

# Build
npm run build
```

## ML

### 1. Configuração

```python
# ml/config.py
from pathlib import Path

class MLConfig:
    MODEL_PATH = Path("models/keyword_finder")
    BATCH_SIZE = 32
    EMBEDDING_SIZE = 768
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
```

### 2. Execução

```bash
# Treinar modelo
python -m ml.train

# Avaliar modelo
python -m ml.evaluate

# Gerar embeddings
python -m ml.generate_embeddings
```

## Debugging

### 1. Python

```python
# config/logging.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
```

### 2. TypeScript

```typescript
// src/config/logging.ts
export const logger = {
  debug: (message: string, ...args: any[]) => {
    if (process.env.NODE_ENV !== 'production') {
      console.debug(message, ...args);
    }
  },
  info: (message: string, ...args: any[]) => {
    console.info(message, ...args);
  },
  error: (message: string, ...args: any[]) => {
    console.error(message, ...args);
  }
};
```

## Observações

- Manter ambiente atualizado
- Seguir padrões de código
- Documentar mudanças
- Testar localmente
- Verificar logs
- Manter segurança
- Otimizar performance
- Revisar periodicamente
- Manter compatibilidade
- Documentar práticas 