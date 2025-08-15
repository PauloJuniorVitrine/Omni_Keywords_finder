# Arquitetura de API

Este documento detalha a arquitetura de API do Omni Keywords Finder.

## Endpoints

### Keywords
```python
# api/keywords.py
@router.post("/keywords/process")
async def process_keywords(
    request: Request,
    keywords: List[str],
    service: KeywordService = Depends(get_keyword_service)
) -> List[Dict]:
    """Processa uma lista de keywords."""
    try:
        results = await service.process_keywords(keywords)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/keywords/{text}")
async def get_keyword(
    text: str,
    service: KeywordService = Depends(get_keyword_service)
) -> Dict:
    """Busca uma keyword pelo texto."""
    if keyword := await service.get_by_text(text):
        return keyword.to_dict()
    raise HTTPException(
        status_code=404,
        detail="Keyword not found"
    )

@router.get("/keywords/cluster/{cluster_id}")
async def get_keywords_by_cluster(
    cluster_id: int,
    service: KeywordService = Depends(get_keyword_service)
) -> List[Dict]:
    """Busca keywords por cluster."""
    keywords = await service.get_by_cluster(cluster_id)
    return [k.to_dict() for k in keywords]
```

### Clusters
```python
# api/clusters.py
@router.post("/clusters")
async def create_cluster(
    request: Request,
    cluster: ClusterCreate,
    service: ClusterService = Depends(get_cluster_service)
) -> Dict:
    """Cria um novo cluster."""
    try:
        result = await service.create_cluster(cluster)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/clusters/{id}")
async def get_cluster(
    id: int,
    service: ClusterService = Depends(get_cluster_service)
) -> Dict:
    """Busca um cluster pelo ID."""
    if cluster := await service.get_by_id(id):
        return cluster.to_dict()
    raise HTTPException(
        status_code=404,
        detail="Cluster not found"
    )

@router.get("/clusters")
async def get_all_clusters(
    service: ClusterService = Depends(get_cluster_service)
) -> List[Dict]:
    """Lista todos os clusters."""
    clusters = await service.get_all()
    return [c.to_dict() for c in clusters]
```

## Middlewares

### Rate Limiting
```python
# api/middlewares/rate_limit.py
class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def __call__(
        self,
        request: Request,
        call_next
    ) -> Response:
        # Gerar chave
        key = f"rate:{request.client.host}:{request.url.path}"
        
        # Verificar limite
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, 60)
        
        if current > 100:  # 100 requests/min
            raise HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        return await call_next(request)
```

### Authentication
```python
# api/middlewares/auth.py
class AuthMiddleware:
    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret

    async def __call__(
        self,
        request: Request,
        call_next
    ) -> Response:
        # Verificar token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        
        token = auth.split(" ")[1]
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"]
            )
            request.state.user = payload
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        
        return await call_next(request)
```

### Logging
```python
# api/middlewares/logging.py
class LoggingMiddleware:
    def __init__(self, logger: Logger):
        self.logger = logger

    async def __call__(
        self,
        request: Request,
        call_next
    ) -> Response:
        # Log request
        self.logger.info(
            "Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            self.logger.info(
                "Request completed",
                extra={
                    "status_code": response.status_code,
                    "duration": time.time() - request.state.start_time
                }
            )
            
            return response
        except Exception as e:
            # Log error
            self.logger.error(
                "Request failed",
                extra={
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            raise
```

## Schemas

### Request/Response
```python
# api/schemas.py
class KeywordCreate(BaseModel):
    text: str
    volume: int
    difficulty: float

    @validator("text")
    def validate_text(cls, v):
        if not v:
            raise ValueError("Text cannot be empty")
        return v

    @validator("volume")
    def validate_volume(cls, v):
        if v < 0:
            raise ValueError("Volume cannot be negative")
        return v

    @validator("difficulty")
    def validate_difficulty(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Difficulty must be between 0 and 1")
        return v

class ClusterCreate(BaseModel):
    name: str
    keywords: List[KeywordCreate]

    @validator("name")
    def validate_name(cls, v):
        if not v:
            raise ValueError("Name cannot be empty")
        return v

    @validator("keywords")
    def validate_keywords(cls, v):
        if not v:
            raise ValueError("Cluster must have at least one keyword")
        return v
```

## Observações

1. Endpoints RESTful
2. Middlewares eficientes
3. Validação rigorosa
4. Rate limiting
5. Autenticação segura
6. Logging detalhado
7. Tratamento de erros
8. Documentação OpenAPI
9. Testes automatizados
10. Monitoramento 