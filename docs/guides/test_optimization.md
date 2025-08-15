# Guia de Otimização de Testes

Este documento detalha as estratégias de otimização de testes do Omni Keywords Finder.

## Testes Paralelos

### 1. Configuração

```python
# pytest.ini
[pytest]
addopts = -n auto --dist=loadfile
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### 2. Execução

```bash
# Executa testes em paralelo
pytest -n auto

# Executa com relatório
pytest -n auto --html=report.html

# Executa com cobertura
pytest -n auto --cov=src --cov-report=html
```

## Testes Otimizados

### 1. Unitários

```python
# tests/unit/test_keyword_extractor.py
import pytest
from src.ml.keyword_extractor import KeywordExtractor

@pytest.fixture
def extractor():
    return KeywordExtractor()

@pytest.mark.parametrize("text,expected", [
    (
        "Python é uma linguagem de programação",
        ["python", "linguagem", "programação"]
    ),
    (
        "Machine Learning é um campo da IA",
        ["machine", "learning", "campo", "ia"]
    )
])
def test_extract_keywords(extractor, text, expected):
    """Testa extração de keywords"""
    result = extractor.extract_keywords(text)
    assert len(result) == len(expected)
    assert all(k["text"] in expected for k in result)
```

### 2. Integração

```python
# tests/integration/test_api_ml.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_keyword_extraction_flow(client):
    """Testa fluxo completo"""
    # Prepara dados
    text = "Python é uma linguagem de programação"
    
    # Faz requisição
    response = client.post(
        "/api/v1/keywords",
        json={"text": text}
    )
    
    # Verifica resposta
    assert response.status_code == 200
    data = response.json()
    assert "keywords" in data
    assert len(data["keywords"]) > 0
```

## Testes de Performance

### 1. Carga

```python
# tests/performance/test_load.py
import pytest
import locust
from locust import HttpUser, task, between

class KeywordUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def extract_keywords(self):
        self.client.post(
            "/api/v1/keywords",
            json={"text": "Python é uma linguagem de programação"}
        )

@pytest.mark.performance
def test_api_load():
    """Testa carga da API"""
    locust.run(
        KeywordUser,
        host="http://localhost:8000",
        users=100,
        spawn_rate=10,
        time_limit="5m"
    )
```

### 2. Estresse

```python
# tests/performance/test_stress.py
import pytest
import locust
from locust import HttpUser, task, between

class KeywordUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    @task
    def extract_keywords(self):
        self.client.post(
            "/api/v1/keywords",
            json={"text": "Python é uma linguagem de programação"}
        )

@pytest.mark.performance
def test_api_stress():
    """Testa estresse da API"""
    locust.run(
        KeywordUser,
        host="http://localhost:8000",
        users=500,
        spawn_rate=50,
        time_limit="10m"
    )
```

## Testes de Cache

### 1. Redis

```python
# tests/cache/test_redis.py
import pytest
from src.cache.redis_cache import RedisCache

@pytest.fixture
def cache():
    return RedisCache()

@pytest.mark.asyncio
async def test_cache_operations(cache):
    """Testa operações de cache"""
    # Testa set
    await cache.set("test_key", "test_value")
    
    # Testa get
    value = await cache.get("test_key")
    assert value == "test_value"
    
    # Testa TTL
    await cache.set("expire_key", "expire_value", ttl=1)
    import time
    time.sleep(2)
    value = await cache.get("expire_key")
    assert value is None
```

### 2. Memória

```python
# tests/cache/test_memory.py
import pytest
from src.cache.memory_cache import MemoryCache

@pytest.fixture
def cache():
    return MemoryCache()

def test_memory_operations(cache):
    """Testa operações de cache em memória"""
    # Testa set
    cache.set("test_key", "test_value")
    
    # Testa get
    value = cache.get("test_key")
    assert value == "test_value"
    
    # Testa TTL
    cache.set("expire_key", "expire_value", ttl=1)
    import time
    time.sleep(2)
    value = cache.get("expire_key")
    assert value is None
```

## Testes de Banco

### 1. MongoDB

```python
# tests/db/test_mongodb.py
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from src.db.mongodb import get_database

@pytest.fixture
async def db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_db
    yield db
    await db.drop_collection("keywords")
    client.close()

@pytest.mark.asyncio
async def test_keyword_operations(db):
    """Testa operações no banco"""
    # Insere keyword
    result = await db.keywords.insert_one({
        "text": "test",
        "keywords": ["test"],
        "score": 1.0
    })
    assert result.inserted_id
    
    # Busca keyword
    doc = await db.keywords.find_one({"text": "test"})
    assert doc is not None
    assert doc["keywords"] == ["test"]
```

### 2. Índices

```python
# tests/db/test_indexes.py
import pytest
from src.db.indexes import IndexManager

@pytest.fixture
async def index_manager():
    return IndexManager("mongodb://localhost:27017")

@pytest.mark.asyncio
async def test_index_operations(index_manager):
    """Testa operações de índices"""
    # Cria índices
    await index_manager.create_indexes()
    
    # Lista índices
    indexes = await index_manager.get_indexes()
    assert len(indexes) > 0
    
    # Verifica índices específicos
    index_names = [idx["name"] for idx in indexes]
    assert "text_1" in index_names
    assert "created_at_-1_score_-1" in index_names
```

## Testes de API

### 1. Endpoints

```python
# tests/api/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Testa health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_keyword_extraction(client):
    """Testa extração de keywords"""
    response = client.post(
        "/api/v1/keywords",
        json={"text": "Python é uma linguagem de programação"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "keywords" in data
```

### 2. Middleware

```python
# tests/api/test_middleware.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_rate_limit(client):
    """Testa rate limiting"""
    # Faz requisições rápidas
    for _ in range(60):
        response = client.get("/health")
        assert response.status_code == 200
    
    # Deve bloquear
    response = client.get("/health")
    assert response.status_code == 429

def test_compression(client):
    """Testa compressão"""
    response = client.get(
        "/api/v1/keywords",
        headers={"Accept-Encoding": "gzip"}
    )
    assert response.status_code == 200
    assert response.headers["Content-Encoding"] == "gzip"
```

## Observações

- Executar em paralelo
- Usar fixtures
- Parametrizar testes
- Mockar dependências
- Limpar dados
- Isolar testes
- Medir cobertura
- Documentar casos
- Revisar periodicamente
- Manter histórico 