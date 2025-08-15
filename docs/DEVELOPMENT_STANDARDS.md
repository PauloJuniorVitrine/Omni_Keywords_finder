# 📋 **STANDARDS DE DESENVOLVIMENTO - OMNİ KEYWORDS FINDER**

## **📋 CONTROLE DE EXECUÇÃO**

**Tracing ID**: DEV_STANDARDS_20250127_001  
**Data de Criação**: 2025-01-27  
**Versão**: 2.0.0  
**Status**: ✅ CONCLUÍDO  
**Responsável**: AI Assistant  

---

## **🎯 VISÃO GERAL**

Este documento define os padrões e convenções de desenvolvimento que devem ser seguidos por toda a equipe do projeto Omni Keywords Finder. Estes standards garantem consistência, qualidade e manutenibilidade do código.

---

## **📝 CONVENÇÕES DE NOMEAÇÃO**

### **Python**

#### **Arquivos e Diretórios**
```python
# ✅ CORRETO
user_management.py
keyword_analyzer.py
api_controllers/
database_models/
test_user_management.py

# ❌ INCORRETO
UserManagement.py
keywordAnalyzer.py
apiControllers/
databaseModels/
testUserManagement.py
```

#### **Variáveis e Funções**
```python
# ✅ CORRETO
def analyze_keyword(keyword: str) -> dict:
    search_volume = get_search_volume(keyword)
    difficulty_score = calculate_difficulty(keyword)
    return {
        'keyword': keyword,
        'volume': search_volume,
        'difficulty': difficulty_score
    }

# ❌ INCORRETO
def analyzeKeyword(keyword: str) -> dict:
    searchVolume = getSearchVolume(keyword)
    difficultyScore = calculateDifficulty(keyword)
    return {
        'keyword': keyword,
        'volume': searchVolume,
        'difficulty': difficultyScore
    }
```

#### **Classes**
```python
# ✅ CORRETO
class KeywordAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = self._initialize_client()
    
    def analyze_keyword(self, keyword: str) -> KeywordAnalysis:
        pass

# ❌ INCORRETO
class keywordAnalyzer:
    def __init__(self, apiKey: str):
        self.apiKey = apiKey
        self.client = self._initializeClient()
    
    def analyzeKeyword(self, keyword: str) -> keywordAnalysis:
        pass
```

#### **Constantes**
```python
# ✅ CORRETO
MAX_KEYWORD_LENGTH = 100
DEFAULT_LANGUAGE = 'pt-BR'
SUPPORTED_MARKETS = ['BR', 'US', 'ES']

# ❌ INCORRETO
maxKeywordLength = 100
defaultLanguage = 'pt-BR'
supportedMarkets = ['BR', 'US', 'ES']
```

### **JavaScript/TypeScript**

#### **Arquivos e Diretórios**
```typescript
// ✅ CORRETO
userManagement.ts
keywordAnalyzer.ts
apiControllers/
databaseModels/
UserManagement.test.ts

// ❌ INCORRETO
user_management.ts
keyword_analyzer.ts
api-controllers/
database-models/
userManagement.test.ts
```

#### **Variáveis e Funções**
```typescript
// ✅ CORRETO
const analyzeKeyword = (keyword: string): KeywordAnalysis => {
    const searchVolume = getSearchVolume(keyword);
    const difficultyScore = calculateDifficulty(keyword);
    return {
        keyword,
        volume: searchVolume,
        difficulty: difficultyScore
    };
};

// ❌ INCORRETO
const analyze_keyword = (keyword: string): keyword_analysis => {
    const search_volume = get_search_volume(keyword);
    const difficulty_score = calculate_difficulty(keyword);
    return {
        keyword,
        volume: search_volume,
        difficulty: difficulty_score
    };
};
```

#### **Classes**
```typescript
// ✅ CORRETO
class KeywordAnalyzer {
    private apiKey: string;
    private client: ApiClient;

    constructor(apiKey: string) {
        this.apiKey = apiKey;
        this.client = this.initializeClient();
    }

    public analyzeKeyword(keyword: string): KeywordAnalysis {
        // Implementation
    }
}

// ❌ INCORRETO
class keyword_analyzer {
    private api_key: string;
    private client: api_client;

    constructor(api_key: string) {
        this.api_key = api_key;
        this.client = this.initialize_client();
    }

    public analyze_keyword(keyword: string): keyword_analysis {
        // Implementation
    }
}
```

---

## **🏗️ ARQUITETURA E ESTRUTURA**

### **Organização de Diretórios**
```
omni_keywords_finder/
├── app/                          # Aplicação principal
│   ├── api/                      # APIs e endpoints
│   │   ├── controllers/          # Controladores
│   │   ├── middlewares/          # Middlewares
│   │   ├── routes/               # Definição de rotas
│   │   └── validators/           # Validações
│   ├── components/               # Componentes React
│   ├── services/                 # Serviços de negócio
│   ├── models/                   # Modelos de dados
│   ├── utils/                    # Utilitários
│   └── config/                   # Configurações
├── tests/                        # Testes
│   ├── unit/                     # Testes unitários
│   ├── integration/              # Testes de integração
│   ├── e2e/                      # Testes end-to-end
│   └── fixtures/                 # Dados de teste
├── docs/                         # Documentação
├── scripts/                      # Scripts de automação
├── infrastructure/               # Infraestrutura
└── config/                       # Configurações do projeto
```

### **Padrões de Arquitetura**

#### **Clean Architecture**
```python
# ✅ ESTRUTURA CORRETA
app/
├── domain/                       # Entidades e regras de negócio
│   ├── entities/
│   ├── value_objects/
│   └── services/
├── application/                  # Casos de uso
│   ├── use_cases/
│   ├── interfaces/
│   └── dto/
├── infrastructure/               # Implementações externas
│   ├── database/
│   ├── external_apis/
│   └── messaging/
└── presentation/                 # Controllers e APIs
    ├── controllers/
    ├── middlewares/
    └── serializers/
```

#### **Dependency Injection**
```python
# ✅ CORRETO
class KeywordAnalysisService:
    def __init__(
        self,
        keyword_repository: KeywordRepository,
        external_api_client: ExternalApiClient,
        cache_service: CacheService
    ):
        self.keyword_repository = keyword_repository
        self.external_api_client = external_api_client
        self.cache_service = cache_service

# ❌ INCORRETO
class KeywordAnalysisService:
    def __init__(self):
        self.keyword_repository = KeywordRepository()
        self.external_api_client = ExternalApiClient()
        self.cache_service = CacheService()
```

---

## **📚 DOCUMENTAÇÃO**

### **Docstrings Python**
```python
def analyze_keyword(
    keyword: str,
    language: str = 'pt-BR',
    market: str = 'BR'
) -> KeywordAnalysis:
    """
    Analisa uma palavra-chave e retorna métricas de SEO.
    
    Args:
        keyword (str): Palavra-chave para análise
        language (str, optional): Idioma da análise. Defaults to 'pt-BR'.
        market (str, optional): Mercado alvo. Defaults to 'BR'.
    
    Returns:
        KeywordAnalysis: Objeto contendo análise da palavra-chave
        
    Raises:
        ValueError: Se a palavra-chave estiver vazia
        ApiError: Se houver erro na API externa
        
    Example:
        >>> analysis = analyze_keyword("marketing digital")
        >>> print(analysis.search_volume)
        5400
    """
    if not keyword.strip():
        raise ValueError("Keyword não pode estar vazia")
    
    # Implementation...
```

### **JSDoc TypeScript**
```typescript
/**
 * Analisa uma palavra-chave e retorna métricas de SEO
 * @param keyword - Palavra-chave para análise
 * @param language - Idioma da análise (padrão: 'pt-BR')
 * @param market - Mercado alvo (padrão: 'BR')
 * @returns Objeto contendo análise da palavra-chave
 * @throws {Error} Se a palavra-chave estiver vazia
 * @throws {ApiError} Se houver erro na API externa
 * 
 * @example
 * ```typescript
 * const analysis = await analyzeKeyword("marketing digital");
 * console.log(analysis.searchVolume); // 5400
 * ```
 */
async function analyzeKeyword(
    keyword: string,
    language: string = 'pt-BR',
    market: string = 'BR'
): Promise<KeywordAnalysis> {
    if (!keyword.trim()) {
        throw new Error('Keyword não pode estar vazia');
    }
    
    // Implementation...
}
```

### **README.md**
```markdown
# Omni Keywords Finder

Sistema avançado de análise e descoberta de palavras-chave otimizadas para SEO.

## 🚀 Instalação

```bash
git clone https://github.com/your-org/omni-keywords-finder.git
cd omni-keywords-finder
pip install -r requirements.txt
```

## 📖 Uso

```python
from app.services.keyword_analyzer import KeywordAnalyzer

analyzer = KeywordAnalyzer(api_key="your-api-key")
analysis = analyzer.analyze_keyword("marketing digital")
print(analysis.search_volume)
```

## 🧪 Testes

```bash
pytest tests/
```

## 📚 Documentação

Veja a [documentação completa](docs/README.md) para mais detalhes.
```

---

## **🧪 TESTES**

### **Estrutura de Testes**
```python
# ✅ ESTRUTURA CORRETA
tests/
├── unit/
│   ├── test_keyword_analyzer.py
│   ├── test_user_service.py
│   └── test_utils.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database_operations.py
│   └── test_external_apis.py
├── e2e/
│   ├── test_user_workflow.py
│   └── test_keyword_analysis_flow.py
└── fixtures/
    ├── sample_keywords.json
    ├── test_users.json
    └── mock_responses.json
```

### **Padrões de Teste**
```python
# ✅ TESTE CORRETO
import pytest
from unittest.mock import Mock, patch
from app.services.keyword_analyzer import KeywordAnalyzer
from app.exceptions import ApiError

class TestKeywordAnalyzer:
    """Testes para o serviço de análise de palavras-chave."""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture para criar instância do analisador."""
        return KeywordAnalyzer(api_key="test-key")
    
    @pytest.fixture
    def mock_api_client(self):
        """Fixture para mock do cliente da API."""
        with patch('app.services.keyword_analyzer.ExternalApiClient') as mock:
            yield mock
    
    def test_analyze_keyword_success(self, analyzer, mock_api_client):
        """Testa análise bem-sucedida de palavra-chave."""
        # Arrange
        keyword = "marketing digital"
        expected_response = {
            "search_volume": 5400,
            "difficulty": 75,
            "cpc": 2.45
        }
        mock_api_client.return_value.get_keyword_data.return_value = expected_response
        
        # Act
        result = analyzer.analyze_keyword(keyword)
        
        # Assert
        assert result.search_volume == 5400
        assert result.difficulty == 75
        assert result.cpc == 2.45
        mock_api_client.return_value.get_keyword_data.assert_called_once_with(keyword)
    
    def test_analyze_keyword_empty_string(self, analyzer):
        """Testa erro ao analisar palavra-chave vazia."""
        # Arrange
        keyword = ""
        
        # Act & Assert
        with pytest.raises(ValueError, match="Keyword não pode estar vazia"):
            analyzer.analyze_keyword(keyword)
    
    def test_analyze_keyword_api_error(self, analyzer, mock_api_client):
        """Testa tratamento de erro da API externa."""
        # Arrange
        keyword = "marketing digital"
        mock_api_client.return_value.get_keyword_data.side_effect = ApiError("API indisponível")
        
        # Act & Assert
        with pytest.raises(ApiError, match="API indisponível"):
            analyzer.analyze_keyword(keyword)
```

### **Cobertura de Testes**
```python
# ✅ CONFIGURAÇÃO CORRETA
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

---

## **🔒 SEGURANÇA**

### **Validação de Entrada**
```python
# ✅ VALIDAÇÃO CORRETA
from pydantic import BaseModel, validator
from typing import List

class KeywordAnalysisRequest(BaseModel):
    keyword: str
    language: str = 'pt-BR'
    market: str = 'BR'
    include_competitors: bool = True
    
    @validator('keyword')
    def validate_keyword(cls, v):
        if not v or not v.strip():
            raise ValueError('Keyword não pode estar vazia')
        if len(v) > 100:
            raise ValueError('Keyword não pode ter mais de 100 caracteres')
        if not v.replace(' ', '').isalnum():
            raise ValueError('Keyword deve conter apenas letras, números e espaços')
        return v.strip()
    
    @validator('language')
    def validate_language(cls, v):
        allowed_languages = ['pt-BR', 'en-US', 'es-ES']
        if v not in allowed_languages:
            raise ValueError(f'Idioma deve ser um dos: {allowed_languages}')
        return v
```

### **Sanitização de Dados**
```python
# ✅ SANITIZAÇÃO CORRETA
import html
import re
from typing import Any

def sanitize_input(data: Any) -> Any:
    """Sanitiza dados de entrada para prevenir XSS."""
    if isinstance(data, str):
        # Remove scripts e tags HTML
        data = re.sub(r'<script.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
        data = re.sub(r'<.*?>', '', data)
        # Escapa caracteres especiais
        data = html.escape(data)
        return data.strip()
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data
```

### **Autenticação e Autorização**
```python
# ✅ AUTENTICAÇÃO CORRETA
from functools import wraps
from flask import request, jsonify
import jwt

def require_auth(f):
    """Decorator para requerer autenticação."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        try:
            # Remove 'Bearer ' prefix
            token = token.split(' ')[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated

def require_role(role):
    """Decorator para requerer role específica."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'error': 'Usuário não autenticado'}), 401
            
            if role not in request.user.get('roles', []):
                return jsonify({'error': 'Permissão insuficiente'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator
```

---

## **📊 PERFORMANCE**

### **Otimização de Queries**
```python
# ✅ QUERY OTIMIZADA
from sqlalchemy.orm import joinedload, selectinload

class KeywordRepository:
    def get_keywords_with_analysis(self, user_id: int) -> List[Keyword]:
        """Busca palavras-chave com análises usando eager loading."""
        return (
            self.session.query(Keyword)
            .options(
                joinedload(Keyword.analyses),
                selectinload(Keyword.competitors)
            )
            .filter(Keyword.user_id == user_id)
            .all()
        )
    
    def get_keywords_paginated(self, user_id: int, page: int = 1, per_page: int = 20):
        """Busca palavras-chave com paginação."""
        return (
            self.session.query(Keyword)
            .filter(Keyword.user_id == user_id)
            .order_by(Keyword.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
```

### **Cache Strategy**
```python
# ✅ CACHE CORRETO
import redis
from functools import wraps
import json

class CacheService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def cache_result(self, key: str, ttl: int = 3600):
        """Decorator para cachear resultados de funções."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Gera chave única baseada nos argumentos
                cache_key = f"{key}:{hash(str(args) + str(kwargs))}"
                
                # Tenta buscar do cache
                cached_result = self.redis.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
                
                # Executa função e cacheia resultado
                result = func(*args, **kwargs)
                self.redis.setex(cache_key, ttl, json.dumps(result))
                
                return result
            return wrapper
        return decorator

# Uso
@cache_service.cache_result("keyword_analysis", ttl=1800)
def analyze_keyword(keyword: str) -> dict:
    # Implementation...
    pass
```

---

## **🔧 CONFIGURAÇÃO E DEPLOYMENT**

### **Variáveis de Ambiente**
```python
# ✅ CONFIGURAÇÃO CORRETA
# .env.example
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379/0
API_KEY_GOOGLE=your-google-api-key
API_KEY_SEMRUSH=your-semrush-api-key
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### **Configuração por Ambiente**
```python
# ✅ CONFIGURAÇÃO CORRETA
import os
from typing import Dict, Any

class Config:
    """Configuração base."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuração para produção."""
    DEBUG = False
    TESTING = False
    
    @classmethod
    def init_app(cls, app):
        # Configurações específicas de produção
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            file_handler = RotatingFileHandler(
                'logs/omni_keywords_finder.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Omni Keywords Finder startup')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

---

## **📝 LOGGING**

### **Configuração de Logs**
```python
# ✅ LOGGING CORRETO
import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    """Logger estruturado para o sistema."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter estruturado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def log_event(self, event: str, data: Dict[str, Any], level: str = 'info'):
        """Loga evento estruturado."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event,
            'data': data,
            'level': level
        }
        
        getattr(self.logger, level)(json.dumps(log_data))
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Loga requisição da API."""
        self.log_event('api_request', {
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration_ms': round(duration * 1000, 2)
        })
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Loga erro com contexto."""
        self.log_event('error', {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }, level='error')

# Uso
logger = StructuredLogger('keyword_analyzer')
logger.log_api_request('POST', '/api/keywords/analyze', 200, 0.5)
```

---

## **🚀 CI/CD**

### **GitHub Actions**
```yaml
# ✅ WORKFLOW CORRETO
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 app/ tests/
        black --check app/ tests/
        isort --check-only app/ tests/
    
    - name: Run security scan
      run: |
        bandit -r app/ -f json -o bandit-report.json
        safety check
    
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
        coverage report --fail-under=85
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.ECR_REGISTRY }}/omni-keywords-finder:${{ github.sha }}
          ${{ secrets.ECR_REGISTRY }}/omni-keywords-finder:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

---

## **📋 CHECKLIST DE QUALIDADE**

### **Antes do Commit**
- [ ] Código segue padrões de estilo (black, flake8, isort)
- [ ] Testes unitários passam
- [ ] Cobertura de testes >= 85%
- [ ] Documentação atualizada
- [ ] Logs estruturados implementados
- [ ] Tratamento de erros adequado
- [ ] Validação de entrada implementada
- [ ] Performance considerada
- [ ] Segurança verificada

### **Antes do Merge**
- [ ] Code review aprovado por 2 reviewers
- [ ] Todos os checks CI passam
- [ ] Testes de integração passam
- [ ] Security scan limpo
- [ ] Performance tests passam
- [ ] Documentação atualizada
- [ ] Changelog atualizado

---

**🎯 STATUS**: ✅ **STANDARDS DE DESENVOLVIMENTO CONCLUÍDOS**  
**📅 Próxima Ação**: Implementação dos scripts de automação  
**👨‍💻 Responsável**: AI Assistant  
**📊 Progresso**: 100% da documentação 