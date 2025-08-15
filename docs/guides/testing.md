# Guia de Testes

Este documento detalha as estratégias de otimização de testes do Omni Keywords Finder.

## Tipos de Testes

1. **Unitários**
   - Funções isoladas
   - Classes individuais
   - Módulos independentes

2. **Integração**
   - Interação entre módulos
   - Comunicação com serviços
   - Fluxos completos

3. **E2E**
   - Fluxos completos
   - Interface do usuário
   - Cenários reais

4. **Performance**
   - Carga
   - Estresse
   - Latência

## Estrutura de Testes

```
tests/
├── unit/                    # Testes unitários
│   ├── api/                # Testes da API
│   ├── ml/                 # Testes do ML
│   └── utils/              # Testes de utilitários
├── integration/            # Testes de integração
│   ├── api_ml/            # API + ML
│   └── api_db/            # API + Banco
├── e2e/                    # Testes end-to-end
│   ├── flows/             # Fluxos completos
│   └── ui/                # Interface
└── performance/           # Testes de performance
    ├── load/              # Testes de carga
    └── stress/            # Testes de estresse
```

## Testes Unitários

### 1. Keywords

```python
# tests/unit/test_keywords.py
import pytest
from datetime import datetime
from src.models.keyword import Keyword
from src.services.keyword_service import KeywordService

@pytest.fixture
def keyword_service():
    return KeywordService()

@pytest.fixture
def sample_keyword():
    return Keyword(
        text="test keyword",
        language="en",
        created_at=datetime.utcnow()
    )

def test_create_keyword(keyword_service, sample_keyword):
    """Testa criação de keyword"""
    result = keyword_service.create(sample_keyword)
    assert result.text == sample_keyword.text
    assert result.language == sample_keyword.language
    assert result.created_at is not None

def test_get_keyword(keyword_service, sample_keyword):
    """Testa obtenção de keyword"""
    created = keyword_service.create(sample_keyword)
    result = keyword_service.get(created.id)
    assert result.id == created.id
    assert result.text == created.text

def test_update_keyword(keyword_service, sample_keyword):
    """Testa atualização de keyword"""
    created = keyword_service.create(sample_keyword)
    created.text = "updated keyword"
    result = keyword_service.update(created)
    assert result.text == "updated keyword"

def test_delete_keyword(keyword_service, sample_keyword):
    """Testa remoção de keyword"""
    created = keyword_service.create(sample_keyword)
    keyword_service.delete(created.id)
    result = keyword_service.get(created.id)
    assert result is None
```

### 2. Usuários

```python
# tests/unit/test_users.py
import pytest
from datetime import datetime
from src.models.user import User
from src.services.user_service import UserService

@pytest.fixture
def user_service():
    return UserService()

@pytest.fixture
def sample_user():
    return User(
        email="test@example.com",
        name="Test User",
        created_at=datetime.utcnow()
    )

def test_create_user(user_service, sample_user):
    """Testa criação de usuário"""
    result = user_service.create(sample_user)
    assert result.email == sample_user.email
    assert result.name == sample_user.name
    assert result.created_at is not None

def test_get_user(user_service, sample_user):
    """Testa obtenção de usuário"""
    created = user_service.create(sample_user)
    result = user_service.get(created.id)
    assert result.id == created.id
    assert result.email == created.email

def test_update_user(user_service, sample_user):
    """Testa atualização de usuário"""
    created = user_service.create(sample_user)
    created.name = "Updated User"
    result = user_service.update(created)
    assert result.name == "Updated User"

def test_delete_user(user_service, sample_user):
    """Testa remoção de usuário"""
    created = user_service.create(sample_user)
    user_service.delete(created.id)
    result = user_service.get(created.id)
    assert result is None
```

## Testes de Integração

### 1. API

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from datetime import datetime

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_keyword():
    return {
        "text": "test keyword",
        "language": "en",
        "created_at": datetime.utcnow().isoformat()
    }

def test_create_keyword(client, sample_keyword):
    """Testa criação de keyword via API"""
    response = client.post("/keywords", json=sample_keyword)
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == sample_keyword["text"]
    assert data["language"] == sample_keyword["language"]

def test_get_keyword(client, sample_keyword):
    """Testa obtenção de keyword via API"""
    created = client.post("/keywords", json=sample_keyword).json()
    response = client.get(f"/keywords/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["text"] == created["text"]

def test_update_keyword(client, sample_keyword):
    """Testa atualização de keyword via API"""
    created = client.post("/keywords", json=sample_keyword).json()
    created["text"] = "updated keyword"
    response = client.put(f"/keywords/{created['id']}", json=created)
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "updated keyword"

def test_delete_keyword(client, sample_keyword):
    """Testa remoção de keyword via API"""
    created = client.post("/keywords", json=sample_keyword).json()
    response = client.delete(f"/keywords/{created['id']}")
    assert response.status_code == 204
    response = client.get(f"/keywords/{created['id']}")
    assert response.status_code == 404
```

### 2. Serviços

```python
# tests/integration/test_services.py
import pytest
from datetime import datetime
from src.models.keyword import Keyword
from src.models.user import User
from src.services.keyword_service import KeywordService
from src.services.user_service import UserService

@pytest.fixture
def keyword_service():
    return KeywordService()

@pytest.fixture
def user_service():
    return UserService()

@pytest.fixture
def sample_keyword():
    return Keyword(
        text="test keyword",
        language="en",
        created_at=datetime.utcnow()
    )

@pytest.fixture
def sample_user():
    return User(
        email="test@example.com",
        name="Test User",
        created_at=datetime.utcnow()
    )

def test_keyword_user_integration(
    keyword_service,
    user_service,
    sample_keyword,
    sample_user
):
    """Testa integração entre keyword e usuário"""
    user = user_service.create(sample_user)
    keyword = keyword_service.create(sample_keyword)
    
    keyword.user_id = user.id
    updated = keyword_service.update(keyword)
    
    assert updated.user_id == user.id
    
    user_keywords = keyword_service.get_by_user(user.id)
    assert len(user_keywords) == 1
    assert user_keywords[0].id == keyword.id
```

## Testes de Carga

### 1. Performance

```python
# tests/load/test_performance.py
import pytest
import asyncio
from datetime import datetime
from src.models.keyword import Keyword
from src.services.keyword_service import KeywordService

@pytest.fixture
def keyword_service():
    return KeywordService()

@pytest.fixture
def sample_keywords():
    return [
        Keyword(
            text=f"test keyword {i}",
            language="en",
            created_at=datetime.utcnow()
        )
        for i in range(1000)
    ]

@pytest.mark.asyncio
async def test_bulk_create(keyword_service, sample_keywords):
    """Testa criação em massa"""
    start = datetime.utcnow()
    
    for keyword in sample_keywords:
        await keyword_service.create(keyword)
        
    end = datetime.utcnow()
    duration = (end - start).total_seconds()
    
    assert duration < 10  # Máximo 10 segundos

@pytest.mark.asyncio
async def test_concurrent_operations(
    keyword_service,
    sample_keywords
):
    """Testa operações concorrentes"""
    start = datetime.utcnow()
    
    tasks = []
    for keyword in sample_keywords:
        tasks.append(keyword_service.create(keyword))
        
    await asyncio.gather(*tasks)
    
    end = datetime.utcnow()
    duration = (end - start).total_seconds()
    
    assert duration < 5  # Máximo 5 segundos
```

### 2. Estresse

```python
# tests/load/test_stress.py
import pytest
import asyncio
from datetime import datetime
from src.models.keyword import Keyword
from src.services.keyword_service import KeywordService

@pytest.fixture
def keyword_service():
    return KeywordService()

@pytest.fixture
def sample_keywords():
    return [
        Keyword(
            text=f"test keyword {i}",
            language="en",
            created_at=datetime.utcnow()
        )
        for i in range(10000)
    ]

@pytest.mark.asyncio
async def test_stress_create(keyword_service, sample_keywords):
    """Testa criação sob estresse"""
    start = datetime.utcnow()
    
    for keyword in sample_keywords:
        await keyword_service.create(keyword)
        
    end = datetime.utcnow()
    duration = (end - start).total_seconds()
    
    assert duration < 60  # Máximo 60 segundos

@pytest.mark.asyncio
async def test_stress_concurrent(
    keyword_service,
    sample_keywords
):
    """Testa concorrência sob estresse"""
    start = datetime.utcnow()
    
    tasks = []
    for keyword in sample_keywords:
        tasks.append(keyword_service.create(keyword))
        
    await asyncio.gather(*tasks)
    
    end = datetime.utcnow()
    duration = (end - start).total_seconds()
    
    assert duration < 30  # Máximo 30 segundos
```

## Testes E2E

### 1. Fluxos

```python
# tests/e2e/test_flows.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from datetime import datetime

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_user():
    return {
        "email": "test@example.com",
        "name": "Test User",
        "created_at": datetime.utcnow().isoformat()
    }

@pytest.fixture
def sample_keyword():
    return {
        "text": "test keyword",
        "language": "en",
        "created_at": datetime.utcnow().isoformat()
    }

def test_user_keyword_flow(client, sample_user, sample_keyword):
    """Testa fluxo completo de usuário e keyword"""
    # Cria usuário
    user_response = client.post("/users", json=sample_user)
    assert user_response.status_code == 201
    user = user_response.json()
    
    # Cria keyword
    keyword_response = client.post("/keywords", json=sample_keyword)
    assert keyword_response.status_code == 201
    keyword = keyword_response.json()
    
    # Associa keyword ao usuário
    keyword["user_id"] = user["id"]
    update_response = client.put(
        f"/keywords/{keyword['id']}",
        json=keyword
    )
    assert update_response.status_code == 200
    
    # Verifica associação
    get_response = client.get(f"/keywords/{keyword['id']}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["user_id"] == user["id"]
    
    # Remove keyword
    delete_response = client.delete(f"/keywords/{keyword['id']}")
    assert delete_response.status_code == 204
    
    # Remove usuário
    user_delete = client.delete(f"/users/{user['id']}")
    assert user_delete.status_code == 204
```

### 2. Cenários

```python
# tests/e2e/test_scenarios.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from datetime import datetime

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_users():
    return [
        {
            "email": f"test{i}@example.com",
            "name": f"Test User {i}",
            "created_at": datetime.utcnow().isoformat()
        }
        for i in range(5)
    ]

@pytest.fixture
def sample_keywords():
    return [
        {
            "text": f"test keyword {i}",
            "language": "en",
            "created_at": datetime.utcnow().isoformat()
        }
        for i in range(10)
    ]

def test_multi_user_scenario(
    client,
    sample_users,
    sample_keywords
):
    """Testa cenário com múltiplos usuários"""
    # Cria usuários
    users = []
    for user in sample_users:
        response = client.post("/users", json=user)
        assert response.status_code == 201
        users.append(response.json())
    
    # Cria keywords
    keywords = []
    for keyword in sample_keywords:
        response = client.post("/keywords", json=keyword)
        assert response.status_code == 201
        keywords.append(response.json())
    
    # Associa keywords aos usuários
    for i, keyword in enumerate(keywords):
        keyword["user_id"] = users[i % len(users)]["id"]
        response = client.put(
            f"/keywords/{keyword['id']}",
            json=keyword
        )
        assert response.status_code == 200
    
    # Verifica associações
    for user in users:
        response = client.get(f"/users/{user['id']}/keywords")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    # Limpa dados
    for keyword in keywords:
        response = client.delete(f"/keywords/{keyword['id']}")
        assert response.status_code == 204
    
    for user in users:
        response = client.delete(f"/users/{user['id']}")
        assert response.status_code == 204
```

## Observações

- Testar unidades
- Testar integrações
- Testar carga
- Testar E2E
- Manter cobertura
- Documentar testes
- Automatizar execução
- Monitorar resultados
- Ajustar thresholds
- Manter logs 