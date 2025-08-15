# Guia de Performance

Este documento detalha as estratégias de otimização de performance do Omni Keywords Finder.

## Métricas de Performance

### 1. Latência

```python
# src/monitoring/latency.py
from prometheus_client import Histogram
import time
from functools import wraps

# Métricas
api_latency = Histogram(
    'api_latency_seconds',
    'Latência das requisições',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

def measure_latency(endpoint: str):
    """Decorator para medir latência"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                api_latency.labels(endpoint=endpoint).observe(duration)
        return wrapper
    return decorator
```

### 2. Throughput

```python
# src/monitoring/throughput.py
from prometheus_client import Counter
from datetime import datetime, timedelta
from collections import deque

class ThroughputMonitor:
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.requests = deque(maxlen=window_size)
        self.counter = Counter(
            'api_requests_total',
            'Total de requisições',
            ['endpoint']
        )
        
    def record_request(self, endpoint: str):
        """Registra requisição"""
        now = datetime.now()
        self.requests.append(now)
        self.counter.labels(endpoint=endpoint).inc()
        
    def get_throughput(self) -> float:
        """Calcula throughput atual"""
        if not self.requests:
            return 0.0
            
        window_start = datetime.now() - timedelta(seconds=self.window_size)
        recent_requests = sum(1 for t in self.requests if t > window_start)
        return recent_requests / self.window_size
```

## Otimizações de Código

### 1. Algoritmos

```python
# src/ml/optimized_algorithms.py
from typing import List, Dict, Any
import numpy as np
from collections import Counter

class KeywordExtractor:
    def __init__(self):
        self.stop_words = set(['a', 'o', 'e', 'de', 'da', 'do'])
        
    def extract_keywords(self, text: str) -> List[Dict[str, Any]]:
        """Extrai keywords otimizado"""
        # Tokenização rápida
        words = text.lower().split()
        
        # Remove stop words
        words = [w for w in words if w not in self.stop_words]
        
        # Contagem otimizada
        word_counts = Counter(words)
        
        # Normalização
        total = sum(word_counts.values())
        keywords = [
            {
                'text': word,
                'score': count / total
            }
            for word, count in word_counts.most_common(10)
        ]
        
        return keywords
```

### 2. Estruturas de Dados

```python
# src/utils/optimized_structures.py
from typing import Any, Dict, List
from collections import OrderedDict
import heapq

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        
    def get(self, key: str) -> Any:
        """Obtém valor com LRU"""
        if key not in self.cache:
            return None
            
        value = self.cache.pop(key)
        self.cache[key] = value
        return value
        
    def put(self, key: str, value: Any):
        """Insere valor com LRU"""
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
            
        self.cache[key] = value

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0
        
    def push(self, item: Any, priority: float):
        """Insere item com prioridade"""
        heapq.heappush(self.heap, (priority, self.count, item))
        self.count += 1
        
    def pop(self) -> Any:
        """Remove item com maior prioridade"""
        return heapq.heappop(self.heap)[2]
```

## Otimizações de Banco

### 1. Índices

```python
# src/db/indexes.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any

class IndexManager:
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.keywords_db
        
    async def create_indexes(self):
        """Cria índices otimizados"""
        # Índice para busca por texto
        await self.db.keywords.create_index(
            [("text", 1)],
            background=True
        )
        
        # Índice composto para busca por data e score
        await self.db.keywords.create_index(
            [
                ("created_at", -1),
                ("score", -1)
            ],
            background=True
        )
        
    async def get_indexes(self) -> List[Dict[str, Any]]:
        """Lista índices existentes"""
        return await self.db.keywords.list_indexes()
```

### 2. Queries

```python
# src/db/optimized_queries.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any
from datetime import datetime, timedelta

class QueryOptimizer:
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.keywords_db
        
    async def find_recent_keywords(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Busca keywords recentes otimizada"""
        return await self.db.keywords.find(
            {
                "created_at": {
                    "$gte": datetime.now() - timedelta(days=7)
                }
            }
        ).sort("score", -1).limit(limit).to_list(None)
        
    async def aggregate_keywords(
        self,
        pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Agregação otimizada"""
        return await self.db.keywords.aggregate(pipeline).to_list(None)
```

## Otimizações de Cache

### 1. Redis

```python
# src/cache/redis.py
from typing import Dict, Any, Optional
from redis import Redis
import json
from datetime import datetime, timedelta

class RedisCache:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None
    ):
        self.redis = Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Obtém valor do cache"""
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
        
    def set(
        self,
        key: str,
        value: Dict[str, Any],
        expire: Optional[int] = None
    ):
        """Define valor no cache"""
        self.redis.set(
            key,
            json.dumps(value),
            ex=expire
        )
        
    def delete(self, key: str):
        """Remove valor do cache"""
        self.redis.delete(key)
        
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        return bool(self.redis.exists(key))
```

### 2. Memória

```python
# src/cache/memory.py
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import threading
import time

class MemoryCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Obtém valor do cache"""
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if item["expire"] and item["expire"] < time.time():
                    del self._cache[key]
                    return None
                return item["value"]
            return None
            
    def set(
        self,
        key: str,
        value: Dict[str, Any],
        expire: Optional[int] = None
    ):
        """Define valor no cache"""
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expire": time.time() + expire if expire else None
            }
            
    def delete(self, key: str):
        """Remove valor do cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                
    def exists(self, key: str) -> bool:
        """Verifica se chave existe"""
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if item["expire"] and item["expire"] < time.time():
                    del self._cache[key]
                    return False
                return True
            return False
```

## Otimizações de Rede

### 1. HTTP

```python
# src/api/http_optimized.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Compressão
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configuração do servidor
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        loop="uvloop",
        http="httptools"
    )
```

### 2. WebSocket

```python
# src/api/websocket_optimized.py
from fastapi import FastAPI, WebSocket
from typing import List
import asyncio
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """Gerencia conexão"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        """Remove conexão"""
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: str):
        """Broadcast otimizado"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except Exception:
        manager.disconnect(websocket)
```

## Otimização

### 1. Queries

```python
# src/optimization/queries.py
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import asyncio

class QueryOptimizer:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        
    async def create_indexes(self):
        """Cria índices"""
        # Índice para keywords
        await self.db.keywords.create_index(
            [("text", "text")],
            name="text_search"
        )
        
        # Índice para usuários
        await self.db.users.create_index(
            [("email", 1)],
            unique=True
        )
        
        # Índice para modelos
        await self.db.models.create_index(
            [("name", 1), ("version", 1)],
            unique=True
        )
        
    async def optimize_query(
        self,
        collection: str,
        query: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """Otimiza query"""
        cursor = self.db[collection].find(
            query,
            projection=projection
        )
        
        if sort:
            cursor = cursor.sort(sort)
            
        if skip:
            cursor = cursor.skip(skip)
            
        if limit:
            cursor = cursor.limit(limit)
            
        return await cursor.to_list(length=None)
```

### 2. Processamento

```python
# src/optimization/processing.py
from typing import Dict, Any, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from functools import partial

class ProcessingOptimizer:
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        )
        
    async def process_batch(
        self,
        items: List[Any],
        func: callable,
        batch_size: int = 100
    ) -> List[Any]:
        """Processa em lotes"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            tasks = [
                asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    partial(func, item)
                )
                for item in batch
            ]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
        return results
        
    async def process_parallel(
        self,
        items: List[Any],
        func: callable,
        num_workers: Optional[int] = None
    ) -> List[Any]:
        """Processa em paralelo"""
        if num_workers is None:
            num_workers = multiprocessing.cpu_count()
            
        chunk_size = len(items) // num_workers
        chunks = [
            items[i:i + chunk_size]
            for i in range(0, len(items), chunk_size)
        ]
        
        tasks = [
            asyncio.get_event_loop().run_in_executor(
                self.thread_pool,
                partial(self._process_chunk, func, chunk)
            )
            for chunk in chunks
        ]
        
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]
        
    def _process_chunk(
        self,
        func: callable,
        chunk: List[Any]
    ) -> List[Any]:
        """Processa chunk"""
        return [func(item) for item in chunk]
```

## Compressão

### 1. Dados

```python
# src/optimization/compression.py
from typing import Dict, Any, Optional
import zlib
import json
import base64

class DataCompressor:
    @staticmethod
    def compress(data: Dict[str, Any]) -> str:
        """Comprime dados"""
        json_str = json.dumps(data)
        compressed = zlib.compress(json_str.encode())
        return base64.b64encode(compressed).decode()
        
    @staticmethod
    def decompress(data: str) -> Dict[str, Any]:
        """Descomprime dados"""
        compressed = base64.b64decode(data)
        json_str = zlib.decompress(compressed).decode()
        return json.loads(json_str)
```

### 2. Respostas

```python
# src/optimization/responses.py
from typing import Dict, Any, Optional
from fastapi import Response
import gzip
import json

class ResponseCompressor:
    @staticmethod
    def compress_response(
        data: Dict[str, Any],
        response: Response
    ) -> Response:
        """Comprime resposta"""
        json_str = json.dumps(data)
        compressed = gzip.compress(json_str.encode())
        
        response.body = compressed
        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Length"] = str(len(compressed))
        
        return response
```

## Paginação

### 1. Cursor

```python
# src/optimization/pagination.py
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

class CursorPaginator:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        
    async def paginate(
        self,
        collection: str,
        query: Dict[str, Any],
        cursor: Optional[str] = None,
        limit: int = 20,
        sort: List[tuple] = [("_id", 1)]
    ) -> Dict[str, Any]:
        """Pagina resultados"""
        if cursor:
            query["_id"] = {"$gt": cursor}
            
        cursor = self.db[collection].find(
            query
        ).sort(sort).limit(limit + 1)
        
        items = await cursor.to_list(length=limit + 1)
        
        has_more = len(items) > limit
        if has_more:
            items = items[:-1]
            
        next_cursor = items[-1]["_id"] if items else None
        
        return {
            "items": items,
            "next_cursor": next_cursor,
            "has_more": has_more
        }
```

### 2. Offset

```python
# src/optimization/offset.py
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

class OffsetPaginator:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        
    async def paginate(
        self,
        collection: str,
        query: Dict[str, Any],
        page: int = 1,
        limit: int = 20,
        sort: List[tuple] = [("_id", 1)]
    ) -> Dict[str, Any]:
        """Pagina resultados"""
        skip = (page - 1) * limit
        
        cursor = self.db[collection].find(
            query
        ).sort(sort).skip(skip).limit(limit + 1)
        
        items = await cursor.to_list(length=limit + 1)
        
        has_more = len(items) > limit
        if has_more:
            items = items[:-1]
            
        total = await self.db[collection].count_documents(query)
        
        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "has_more": has_more
        }
```

## Observações

- Usar cache
- Otimizar queries
- Processar em lotes
- Comprimir dados
- Paginar resultados
- Monitorar performance
- Ajustar índices
- Limpar dados
- Manter logs
- Documentar mudanças 