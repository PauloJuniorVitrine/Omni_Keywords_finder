# Práticas de Desenvolvimento

Este documento detalha as práticas de desenvolvimento do Omni Keywords Finder.

## Ambiente

### 1. Requisitos

```bash
# requirements.txt
fastapi==0.68.1
uvicorn==0.15.0
pydantic==1.8.2
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.5
sqlalchemy==1.4.23
pymongo==3.12.0
redis==3.5.3
prometheus-client==0.11.0
structlog==21.1.0
opentelemetry-api==1.7.1
opentelemetry-sdk==1.7.1
opentelemetry-instrumentation-fastapi==0.24b0
pytest==6.2.5
pytest-asyncio==0.15.1
pytest-cov==2.12.1
black==21.7b0
isort==5.9.3
flake8==3.9.2
mypy==0.910
```

### 2. Configuração

```python
# config/settings.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Aplicação
    APP_NAME: str = "Omni Keywords Finder"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # API
    API_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Banco de Dados
    MONGODB_URL: str
    REDIS_URL: str
    
    # ML
    MODEL_PATH: str
    BATCH_SIZE: int = 32
    DEVICE: str = "cpu"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Estrutura

### 1. Diretórios

```
omni-keywords-finder/
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── routes/
│   ├── middlewares/
│   └── dependencies/
├── application/
│   ├── __init__.py
│   ├── services/
│   └── use_cases/
├── domain/
│   ├── __init__.py
│   ├── entities/
│   └── repositories/
├── infrastructure/
│   ├── __init__.py
│   ├── persistence/
│   └── ml/
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/
│   ├── __init__.py
│   └── settings.py
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py
│   ├── logging.py
│   └── tracing.py
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── docs/
│   ├── api.md
│   ├── architecture.md
│   └── development.md
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

### 2. Código

```python
# api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from monitoring.tracing import setup_tracing
from api.routes import keywords, clusters

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Tracing
setup_tracing(app)

# Rotas
app.include_router(
    keywords.router,
    prefix=f"{settings.API_PREFIX}/keywords",
    tags=["keywords"]
)
app.include_router(
    clusters.router,
    prefix=f"{settings.API_PREFIX}/clusters",
    tags=["clusters"]
)
```

## Desenvolvimento

### 1. Código

```python
# application/services/keyword_service.py
from typing import List, Optional
from domain.entities.keyword import Keyword
from domain.repositories.keyword_repository import KeywordRepository
from infrastructure.ml.model import KeywordModel
from monitoring.metrics import track_model_prediction
from monitoring.logging import log_model_prediction

class KeywordService:
    def __init__(
        self,
        repository: KeywordRepository,
        model: KeywordModel
    ):
        self.repository = repository
        self.model = model
    
    async def process_keyword(self, text: str) -> Keyword:
        # Validar entrada
        if not text or not text.strip():
            raise ValueError("Texto inválido")
        
        # Gerar embedding
        start_time = time.time()
        try:
            embedding = await self.model.generate_embedding(text)
            track_model_prediction(
                model="keyword",
                status="success",
                duration=time.time() - start_time
            )
        except Exception as e:
            track_model_prediction(
                model="keyword",
                status="error",
                duration=time.time() - start_time
            )
            log_model_prediction(
                model="keyword",
                input_text=text,
                duration=time.time() - start_time,
                status="error",
                error=str(e)
            )
            raise
        
        # Salvar keyword
        keyword = Keyword(
            text=text,
            embedding=embedding
        )
        return await self.repository.save(keyword)
```

### 2. Testes

```python
# tests/unit/test_keyword_service.py
import pytest
from unittest.mock import Mock, patch
from domain.entities.keyword import Keyword
from application.services.keyword_service import KeywordService

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_model():
    return Mock()

@pytest.fixture
def service(mock_repository, mock_model):
    return KeywordService(mock_repository, mock_model)

def test_process_keyword(service, mock_repository, mock_model):
    # Arrange
    text = "test keyword"
    mock_model.generate_embedding.return_value = [0.1, 0.2, 0.3]
    mock_repository.save.return_value = Keyword(
        text=text,
        embedding=[0.1, 0.2, 0.3]
    )
    
    # Act
    result = service.process_keyword(text)
    
    # Assert
    assert result.text == text
    assert result.embedding == [0.1, 0.2, 0.3]
    mock_model.generate_embedding.assert_called_once_with(text)
    mock_repository.save.assert_called_once()
```

## CI/CD

### 1. GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=./ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

### 2. Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Observações

- Seguir padrões
- Manter documentação
- Testar adequadamente
- Otimizar performance
- Garantir segurança
- Monitorar sistema
- Revisar código
- Manter histórico
- Documentar decisões
- Revisar periodicamente 