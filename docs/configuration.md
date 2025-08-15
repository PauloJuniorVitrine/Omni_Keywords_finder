# Configuração do Projeto

Este documento detalha as configurações do Omni Keywords Finder.

## Ambiente

### 1. Variáveis de Ambiente

```bash
# .env
# Aplicação
APP_ENV=development
DEBUG=true
LOG_LEVEL=debug
API_VERSION=v1
API_PORT=8000
API_HOST=0.0.0.0

# Banco de Dados
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=omni_keywords
REDIS_URI=redis://localhost:6379

# Segurança
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
CORS_ORIGINS=http://localhost:3000

# ML
MODEL_PATH=models/keyword_finder
BATCH_SIZE=32
EMBEDDING_SIZE=768
```

### 2. Configuração Python

```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Aplicação
    app_env: str
    debug: bool
    log_level: str
    api_version: str
    api_port: int
    api_host: str

    # Banco de Dados
    mongodb_uri: str
    mongodb_db: str
    redis_uri: str

    # Segurança
    jwt_secret: str
    jwt_algorithm: str
    jwt_expiration: int
    cors_origins: List[str]

    # ML
    model_path: str
    batch_size: int
    embedding_size: int

    class Config:
        env_file = ".env"
```

## Banco de Dados

### 1. MongoDB

```python
# infrastructure/persistence/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import Settings

class MongoDB:
    def __init__(self, settings: Settings):
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_db]
    
    async def init(self):
        # Índices
        await self.db.keywords.create_index("text", unique=True)
        await self.db.keywords.create_index("cluster")
        await self.db.keywords.create_index("score")
        
        # Validação
        await self.db.command({
            "collMod": "keywords",
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["text", "cluster", "score"],
                    "properties": {
                        "text": {"bsonType": "string"},
                        "cluster": {"bsonType": "string"},
                        "score": {"bsonType": "double"}
                    }
                }
            }
        })
```

### 2. Redis

```python
# infrastructure/cache/redis.py
from redis import Redis
from config.settings import Settings

class RedisCache:
    def __init__(self, settings: Settings):
        self.client = Redis.from_url(settings.redis_uri)
        self.prefix = "omni:"
        self.ttl = 3600
    
    async def get(self, key: str) -> str:
        return await self.client.get(f"{self.prefix}{key}")
    
    async def set(self, key: str, value: str, ttl: int = None):
        await self.client.set(
            f"{self.prefix}{key}",
            value,
            ex=ttl or self.ttl
        )
```

## Logging

### 1. Configuração

```python
# config/logging.py
import structlog
from config.settings import Settings

def setup_logging(settings: Settings):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger()
    logger.setLevel(settings.log_level)
    return logger
```

### 2. Uso

```python
# infrastructure/monitoring/logging.py
import structlog
from fastapi import Request

logger = structlog.get_logger()

def log_request(request: Request):
    logger.info(
        "request_received",
        method=request.method,
        path=request.path,
        client=request.client,
        user=request.user
    )

def log_error(error: Exception):
    logger.error(
        "error_occurred",
        error=str(error),
        type=type(error).__name__
    )
```

## Segurança

### 1. JWT

```python
# infrastructure/security/jwt.py
from datetime import datetime, timedelta
from jose import jwt
from config.settings import Settings

class JWTManager:
    def __init__(self, settings: Settings):
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.expiration = settings.jwt_expiration
    
    def create_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=self.expiration)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret, algorithms=[self.algorithm])
```

### 2. CORS

```python
# config/cors.py
from fastapi.middleware.cors import CORSMiddleware
from config.settings import Settings

def setup_cors(app, settings: Settings):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

## ML

### 1. Modelo

```python
# infrastructure/ml/model.py
from transformers import AutoModel, AutoTokenizer
from config.settings import Settings

class KeywordModel:
    def __init__(self, settings: Settings):
        self.model = AutoModel.from_pretrained(settings.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(settings.model_path)
        self.batch_size = settings.batch_size
        self.embedding_size = settings.embedding_size
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Tokenizar
        tokens = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        
        # Gerar embeddings
        with torch.no_grad():
            outputs = self.model(**tokens)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings.tolist()
```

### 2. Cache

```python
# infrastructure/ml/cache.py
from infrastructure.cache.redis import RedisCache
from config.settings import Settings

class ModelCache:
    def __init__(self, settings: Settings):
        self.cache = RedisCache(settings)
        self.ttl = 86400  # 24 horas
    
    async def get_embedding(self, text: str) -> List[float]:
        key = f"embedding:{text}"
        cached = await self.cache.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_embedding(self, text: str, embedding: List[float]):
        key = f"embedding:{text}"
        await self.cache.set(key, json.dumps(embedding), self.ttl)
```

## Observações

- Validar configurações
- Documentar mudanças
- Testar ambientes
- Monitorar uso
- Manter segurança
- Otimizar performance
- Verificar logs
- Atualizar docs
- Manter histórico
- Revisar periodicamente 