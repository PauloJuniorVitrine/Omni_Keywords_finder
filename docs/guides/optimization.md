# Guia de Otimização

Este documento detalha as estratégias de otimização e redução de atrasos do Omni Keywords Finder.

## Estratégias de Otimização

### 1. Caching

```python
# src/cache/redis_cache.py
from redis import Redis
from typing import Any, Optional
import json

class RedisCache:
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis = Redis(host=host, port=port, decode_responses=True)
        
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        data = self.redis.get(key)
        return json.loads(data) if data else None
        
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Salva valor no cache com TTL"""
        self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
```

### 2. Paralelização

```python
# src/ml/parallel_processor.py
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any
import asyncio

class ParallelProcessor:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def process_batch(self, items: List[Any], func: callable):
        """Processa itens em paralelo"""
        loop = asyncio.get_event_loop()
        tasks = []
        
        for item in items:
            task = loop.run_in_executor(
                self.executor,
                func,
                item
            )
            tasks.append(task)
            
        return await asyncio.gather(*tasks)
```

### 3. Otimização de Banco

```python
# src/db/optimized_queries.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any

class OptimizedQueries:
    def __init__(self, connection_string: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.keywords_db
        
    async def bulk_insert(self, items: List[Dict[str, Any]]):
        """Insere múltiplos itens otimizado"""
        await self.db.keywords.insert_many(items)
        
    async def find_with_index(self, query: Dict[str, Any]):
        """Busca otimizada com índices"""
        return await self.db.keywords.find(query).hint("text_1").to_list(None)
```

## Otimizações de Frontend

### 1. Code Splitting

```typescript
// src/frontend/App.tsx
import React, { lazy, Suspense } from 'react';

const KeywordExtractor = lazy(() => import('./components/KeywordExtractor'));
const KeywordList = lazy(() => import('./components/KeywordList'));

export const App: React.FC = () => {
  return (
    <Suspense fallback={<div>Carregando...</div>}>
      <KeywordExtractor />
      <KeywordList />
    </Suspense>
  );
};
```

### 2. Memoização

```typescript
// src/frontend/components/KeywordList.tsx
import React, { useMemo } from 'react';
import { Keyword } from '../types/Keyword';

interface Props {
  keywords: Keyword[];
}

export const KeywordList: React.FC<Props> = ({ keywords }) => {
  const sortedKeywords = useMemo(() => {
    return [...keywords].sort((a, b) => b.score - a.score);
  }, [keywords]);

  return (
    <div className="keyword-list">
      {sortedKeywords.map(keyword => (
        <KeywordItem key={keyword.text} keyword={keyword} />
      ))}
    </div>
  );
};
```

## Otimizações de API

### 1. Rate Limiting

```python
# src/api/rate_limit.py
from fastapi import Request, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, requests_per_minute: int = 60):
        super().__init__()
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Limpa requisições antigas
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < 60
        ]
        
        # Verifica limite
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
            
        # Registra requisição
        self.requests[client_ip].append(now)
        
        return await call_next(request)
```

### 2. Compressão

```python
# src/api/compression.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# Adiciona compressão
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000  # Comprime respostas > 1KB
)
```

## Otimizações de ML

### 1. Batch Processing

```python
# src/ml/batch_processor.py
from typing import List, Any
import numpy as np

class BatchProcessor:
    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size
        
    def process_batch(self, items: List[Any]) -> List[Any]:
        """Processa itens em lotes"""
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = self._process_single_batch(batch)
            results.extend(batch_results)
            
        return results
        
    def _process_single_batch(self, batch: List[Any]) -> List[Any]:
        """Processa um único lote"""
        # Implementação específica
        pass
```

### 2. Modelo Otimizado

```python
# src/ml/optimized_model.py
import torch
from transformers import AutoModel, AutoTokenizer

class OptimizedModel:
    def __init__(self, model_name: str):
        self.model = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Otimizações
        self.model.eval()  # Modo avaliação
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            
    @torch.no_grad()  # Desativa gradientes
    def predict(self, text: str):
        """Predição otimizada"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
            
        outputs = self.model(**inputs)
        return outputs
```

## Otimizações de Infraestrutura

### 1. Load Balancing

```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
      
  api:
    build: ./api
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### 2. Auto Scaling

```yaml
# kubernetes/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: omni-keywords/api:latest
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Observações

- Monitorar performance
- Ajustar parâmetros
- Testar otimizações
- Documentar mudanças
- Revisar periodicamente
- Manter histórico
- Validar resultados
- Otimizar continuamente
- Compartilhar aprendizados
- Aplicar melhorias 