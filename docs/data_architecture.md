# Arquitetura de Dados

Este documento detalha a arquitetura de dados do Omni Keywords Finder.

## Modelos

### Keyword
```python
# models/keyword.py
@dataclass
class Keyword:
    id: str
    text: str
    volume: int
    difficulty: float
    cluster_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    def validate(self):
        if not self.text:
            raise ValueError("Text cannot be empty")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
        if not 0 <= self.difficulty <= 1:
            raise ValueError("Difficulty must be between 0 and 1")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "text": self.text,
            "volume": self.volume,
            "difficulty": self.difficulty,
            "cluster_id": self.cluster_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Keyword":
        return cls(
            id=data["id"],
            text=data["text"],
            volume=data["volume"],
            difficulty=data["difficulty"],
            cluster_id=data.get("cluster_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
```

### Cluster
```python
# models/cluster.py
@dataclass
class Cluster:
    id: int
    name: str
    keywords: List[Keyword]
    created_at: datetime
    updated_at: datetime

    def validate(self):
        if not self.name:
            raise ValueError("Name cannot be empty")
        if not self.keywords:
            raise ValueError("Cluster must have at least one keyword")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "keywords": [k.to_dict() for k in self.keywords],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Cluster":
        return cls(
            id=data["id"],
            name=data["name"],
            keywords=[Keyword.from_dict(k) for k in data["keywords"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
```

## Repositórios

### KeywordRepository
```python
# repositories/keyword_repository.py
class KeywordRepository:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache

    async def save(self, keyword: Keyword) -> Keyword:
        # Validar
        keyword.validate()
        
        # Salvar no banco
        await self.db.keywords.insert_one(keyword.to_dict())
        
        # Atualizar cache
        await self.cache.set(f"keyword:{keyword.id}", keyword.to_dict())
        
        return keyword

    async def get_by_id(self, id: str) -> Optional[Keyword]:
        # Tentar cache
        if cached := await self.cache.get(f"keyword:{id}"):
            return Keyword.from_dict(cached)
        
        # Buscar no banco
        if data := await self.db.keywords.find_one({"id": id}):
            keyword = Keyword.from_dict(data)
            await self.cache.set(f"keyword:{id}", data)
            return keyword
        
        return None

    async def get_by_text(self, text: str) -> Optional[Keyword]:
        if data := await self.db.keywords.find_one({"text": text}):
            return Keyword.from_dict(data)
        return None

    async def get_by_cluster(self, cluster_id: int) -> List[Keyword]:
        cursor = self.db.keywords.find({"cluster_id": cluster_id})
        return [Keyword.from_dict(doc) async for doc in cursor]
```

### ClusterRepository
```python
# repositories/cluster_repository.py
class ClusterRepository:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache

    async def save(self, cluster: Cluster) -> Cluster:
        # Validar
        cluster.validate()
        
        # Salvar no banco
        await self.db.clusters.insert_one(cluster.to_dict())
        
        # Atualizar cache
        await self.cache.set(f"cluster:{cluster.id}", cluster.to_dict())
        
        return cluster

    async def get_by_id(self, id: int) -> Optional[Cluster]:
        # Tentar cache
        if cached := await self.cache.get(f"cluster:{id}"):
            return Cluster.from_dict(cached)
        
        # Buscar no banco
        if data := await self.db.clusters.find_one({"id": id}):
            cluster = Cluster.from_dict(data)
            await self.cache.set(f"cluster:{id}", data)
            return cluster
        
        return None

    async def get_all(self) -> List[Cluster]:
        cursor = self.db.clusters.find()
        return [Cluster.from_dict(doc) async for doc in cursor]
```

## Cache

### RedisCache
```python
# cache/redis_cache.py
class RedisCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[Dict]:
        if data := await self.redis.get(key):
            return json.loads(data)
        return None

    async def set(self, key: str, value: Dict, ttl: int = 3600):
        await self.redis.set(
            key,
            json.dumps(value),
            ex=ttl
        )

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def clear(self):
        await self.redis.flushdb()
```

## Índices

### MongoDB
```python
# database/indexes.py
async def create_indexes(db: Database):
    # Keywords
    await db.keywords.create_index("id", unique=True)
    await db.keywords.create_index("text", unique=True)
    await db.keywords.create_index("cluster_id")
    await db.keywords.create_index("created_at")
    
    # Clusters
    await db.clusters.create_index("id", unique=True)
    await db.clusters.create_index("name")
    await db.clusters.create_index("created_at")
```

## Observações

1. Modelos validados
2. Cache eficiente
3. Índices otimizados
4. Transações atômicas
5. Backup automático
6. Monitoramento
7. Migrações
8. Versionamento
9. Documentação
10. Testes automatizados 