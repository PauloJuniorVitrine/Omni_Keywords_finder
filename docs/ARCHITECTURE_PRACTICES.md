# Práticas de Arquitetura

Este documento detalha as práticas de arquitetura do Omni Keywords Finder.

## Visão Geral

### 1. Camadas

```
┌─────────────────┐
│      API        │
├─────────────────┤
│   Aplicação     │
├─────────────────┤
│     Domínio     │
├─────────────────┤
│ Infraestrutura  │
└─────────────────┘
```

### 2. Componentes

```
┌─────────────────────────────────────────┐
│               Frontend                  │
├─────────────────────────────────────────┤
│                API                      │
├─────────────────────────────────────────┤
│              Serviços                   │
├─────────────────────────────────────────┤
│              Domínio                    │
├─────────────────────────────────────────┤
│           Infraestrutura                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │ MongoDB │  │ Redis   │  │   ML    │  │
│  └─────────┘  └─────────┘  └─────────┘  │
└─────────────────────────────────────────┘
```

## Domínio

### 1. Entidades

```python
# domain/entities/keyword.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Keyword:
    """Representa uma keyword processada."""
    
    text: str
    embedding: List[float]
    cluster: Optional[str] = None
    score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_score(self, score: float) -> None:
        """Atualiza score da keyword."""
        self.score = score
        self.updated_at = datetime.utcnow()
    
    def assign_cluster(self, cluster: str) -> None:
        """Atribui cluster à keyword."""
        self.cluster = cluster
        self.updated_at = datetime.utcnow()

@dataclass
class Cluster:
    """Representa um cluster de keywords."""
    
    name: str
    keywords: List[Keyword] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_keyword(self, keyword: Keyword) -> None:
        """Adiciona keyword ao cluster."""
        self.keywords.append(keyword)
        self.updated_at = datetime.utcnow()
    
    def remove_keyword(self, keyword: Keyword) -> None:
        """Remove keyword do cluster."""
        self.keywords.remove(keyword)
        self.updated_at = datetime.utcnow()
```

### 2. Repositórios

```python
# domain/repositories/keyword_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.keyword import Keyword

class KeywordRepository(ABC):
    """Interface para repositório de keywords."""
    
    @abstractmethod
    async def save(self, keyword: Keyword) -> Keyword:
        """Salva uma keyword."""
        pass
    
    @abstractmethod
    async def find_by_text(self, text: str) -> Optional[Keyword]:
        """Busca keyword por texto."""
        pass
    
    @abstractmethod
    async def find_by_cluster(self, cluster: str) -> List[Keyword]:
        """Busca keywords por cluster."""
        pass
    
    @abstractmethod
    async def delete(self, keyword: Keyword) -> None:
        """Remove uma keyword."""
        pass

class ClusterRepository(ABC):
    """Interface para repositório de clusters."""
    
    @abstractmethod
    async def save(self, cluster: Cluster) -> Cluster:
        """Salva um cluster."""
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Cluster]:
        """Busca cluster por nome."""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[Cluster]:
        """Lista todos os clusters."""
        pass
    
    @abstractmethod
    async def delete(self, cluster: Cluster) -> None:
        """Remove um cluster."""
        pass
```

## Aplicação

### 1. Serviços

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

### 2. Casos de Uso

```python
# application/use_cases/process_keyword.py
from typing import Optional
from domain.entities.keyword import Keyword
from domain.repositories.keyword_repository import KeywordRepository
from infrastructure.ml.model import KeywordModel

class ProcessKeywordUseCase:
    def __init__(
        self,
        repository: KeywordRepository,
        model: KeywordModel
    ):
        self.repository = repository
        self.model = model
    
    async def execute(self, text: str) -> Keyword:
        # Validar entrada
        if not text or not text.strip():
            raise ValueError("Texto inválido")
        
        # Gerar embedding
        embedding = await self.model.generate_embedding(text)
        
        # Salvar keyword
        keyword = Keyword(
            text=text,
            embedding=embedding
        )
        return await self.repository.save(keyword)

class FindClustersUseCase:
    def __init__(
        self,
        repository: KeywordRepository
    ):
        self.repository = repository
    
    async def execute(self, keyword: Keyword) -> List[str]:
        # Buscar keywords similares
        similar_keywords = await self.repository.find_similar(keyword)
        
        # Extrair clusters
        clusters = set()
        for similar in similar_keywords:
            if similar.cluster:
                clusters.add(similar.cluster)
        
        return list(clusters)
```

## Infraestrutura

### 1. Persistência

```python
# infrastructure/persistence/mongodb.py
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from domain.entities.keyword import Keyword
from domain.repositories.keyword_repository import KeywordRepository
from monitoring.metrics import track_api_request
from monitoring.logging import log_request

class MongoDBKeywordRepository(KeywordRepository):
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
        self.db = client.keywords
        self.collection = self.db.keywords
    
    async def save(self, keyword: Keyword) -> Keyword:
        start_time = time.time()
        try:
            document = {
                "text": keyword.text,
                "embedding": keyword.embedding,
                "cluster": keyword.cluster,
                "score": keyword.score,
                "created_at": keyword.created_at,
                "updated_at": keyword.updated_at
            }
            
            result = await self.collection.insert_one(document)
            keyword.id = str(result.inserted_id)
            
            track_api_request(
                endpoint="/keywords",
                method="POST",
                status=200,
                duration=time.time() - start_time
            )
            
            return keyword
        except Exception as e:
            track_api_request(
                endpoint="/keywords",
                method="POST",
                status=500,
                duration=time.time() - start_time
            )
            log_request(
                method="POST",
                path="/keywords",
                client="mongodb",
                user=None,
                duration=time.time() - start_time,
                status=500,
                error=str(e)
            )
            raise
```

### 2. ML

```python
# infrastructure/ml/model.py
from typing import List
import torch
from transformers import AutoTokenizer, AutoModel
from monitoring.metrics import track_model_prediction
from monitoring.logging import log_model_prediction

class KeywordModel:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path).to(self.device)
    
    async def generate_embedding(self, text: str) -> List[float]:
        start_time = time.time()
        try:
            # Tokenizar
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(self.device)
            
            # Gerar embedding
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            # Converter para lista
            embedding = embeddings[0].cpu().numpy().tolist()
            
            track_model_prediction(
                model="keyword",
                status="success",
                duration=time.time() - start_time
            )
            
            return embedding
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
```

## API

### 1. Rotas

```python
# api/routes/keywords.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from domain.entities.keyword import Keyword
from application.use_cases.process_keyword import ProcessKeywordUseCase
from api.dependencies import get_keyword_use_case
from monitoring.metrics import track_api_request
from monitoring.logging import log_request

router = APIRouter()

@router.post("/process", response_model=Keyword)
async def process_keyword(
    text: str,
    use_case: ProcessKeywordUseCase = Depends(get_keyword_use_case)
):
    start_time = time.time()
    try:
        keyword = await use_case.execute(text)
        
        track_api_request(
            endpoint="/keywords/process",
            method="POST",
            status=200,
            duration=time.time() - start_time
        )
        
        return keyword
    except ValueError as e:
        track_api_request(
            endpoint="/keywords/process",
            method="POST",
            status=400,
            duration=time.time() - start_time
        )
        log_request(
            method="POST",
            path="/keywords/process",
            client=None,
            user=None,
            duration=time.time() - start_time,
            status=400,
            error=str(e)
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        track_api_request(
            endpoint="/keywords/process",
            method="POST",
            status=500,
            duration=time.time() - start_time
        )
        log_request(
            method="POST",
            path="/keywords/process",
            client=None,
            user=None,
            duration=time.time() - start_time,
            status=500,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Erro interno"
        )
```

### 2. Middlewares

```python
# api/middlewares/auth.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from config.settings import settings
from monitoring.metrics import track_api_request
from monitoring.logging import log_request

security = HTTPBearer()

async def verify_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    start_time = time.time()
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        track_api_request(
            endpoint="/auth",
            method="GET",
            status=200,
            duration=time.time() - start_time
        )
        
        return payload
    except Exception as e:
        track_api_request(
            endpoint="/auth",
            method="GET",
            status=401,
            duration=time.time() - start_time
        )
        log_request(
            method="GET",
            path="/auth",
            client=request.client.host,
            user=None,
            duration=time.time() - start_time,
            status=401,
            error=str(e)
        )
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas"
        )
```

## Frontend

### 1. Componentes

```typescript
// src/components/KeywordForm.tsx
import React, { useState } from 'react';
import { useKeywordProcessing } from '../hooks/useKeywordProcessing';
import { trackEvent } from '../utils/analytics';

export const KeywordForm: React.FC = () => {
  const [text, setText] = useState('');
  const { processKeyword, loading, error } = useKeywordProcessing();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      trackEvent('keyword_submit', { text });
      await processKeyword(text);
      setText('');
    } catch (err) {
      trackEvent('keyword_error', { error: err.message });
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Digite uma keyword"
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Processando...' : 'Processar'}
      </button>
      {error && <div className="error">{error}</div>}
    </form>
  );
};
```

### 2. Serviços

```typescript
// src/services/KeywordService.ts
import { Keyword } from '../types/Keyword';
import { trackPerformance } from '../utils/performance';

export class KeywordService {
  private readonly apiUrl: string;
  
  constructor(apiUrl: string) {
    this.apiUrl = apiUrl;
  }
  
  async processKeyword(text: string): Promise<Keyword> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(
        `${this.apiUrl}/keywords/process`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text })
        }
      );
      
      if (!response.ok) {
        throw new Error('Erro ao processar keyword');
      }
      
      const keyword = await response.json();
      
      trackPerformance('keyword_processing', performance.now() - startTime);
      
      return keyword;
    } catch (error) {
      trackPerformance('keyword_error', performance.now() - startTime);
      throw error;
    }
  }
}
```

## Observações

- Seguir princípios SOLID
- Manter coesão
- Reduzir acoplamento
- Documentar decisões
- Testar adequadamente
- Monitorar sistema
- Otimizar performance
- Garantir segurança
- Revisar código
- Manter histórico 