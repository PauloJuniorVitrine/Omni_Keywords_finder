# Guia de Desenvolvimento

## Visão Geral

Este guia descreve os padrões e práticas de desenvolvimento do Omni Keywords Finder.

## Ambiente de Desenvolvimento

### 1. Configuração

```bash
# Clone o repositório
git clone https://github.com/your-org/omni_keywords_finder.git
cd omni_keywords_finder

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. IDE

#### VS Code
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm
- Enable PEP 8
- Enable Black
- Enable Pylint
- Enable MyPy

## Padrões de Código

### 1. Python

#### PEP 8
```python
# Nomes
def process_text(text: str) -> List[str]:
    """Processa texto."""
    return [word for word in text.split()]

# Classes
class KeywordExtractor:
    """Extrator de keywords."""
    
    def __init__(self, model: Model):
        self.model = model
    
    def extract(self, text: str) -> List[str]:
        """Extrai keywords."""
        return self.model.predict(text)
```

#### Type Hints
```python
from typing import List, Dict, Optional

def process_data(
    data: List[Dict[str, str]],
    limit: Optional[int] = None
) -> List[str]:
    """Processa dados."""
    return [item["text"] for item in data[:limit]]
```

#### Docstrings
```python
def train_model(
    data: List[Dict[str, str]],
    epochs: int = 10
) -> Model:
    """
    Treina modelo de extração.

    Args:
        data: Lista de textos e keywords
        epochs: Número de épocas

    Returns:
        Modelo treinado

    Raises:
        ValueError: Se dados inválidos
    """
    pass
```

### 2. JavaScript

#### ESLint
```javascript
// .eslintrc.js
module.exports = {
    extends: [
        'airbnb-base',
        'plugin:prettier/recommended'
    ],
    rules: {
        'no-console': 'warn',
        'no-unused-vars': 'error'
    }
};
```

#### Prettier
```javascript
// .prettierrc
{
    "singleQuote": true,
    "trailingComma": "es5",
    "printWidth": 80
}
```

#### JSDoc
```javascript
/**
 * Processa texto e retorna keywords
 * @param {string} text - Texto para processar
 * @param {number} [limit=10] - Limite de keywords
 * @returns {Promise<string[]>} Lista de keywords
 * @throws {Error} Se texto inválido
 */
async function processText(text, limit = 10) {
    // Implementação
}
```

## Testes

### 1. Unitários

#### Python
```python
# tests/test_keywords.py
import pytest
from src.keywords import KeywordExtractor

def test_extract_keywords():
    extractor = KeywordExtractor()
    text = "Python é uma linguagem de programação"
    keywords = extractor.extract(text)
    assert len(keywords) > 0
    assert "Python" in keywords
```

#### JavaScript
```javascript
// tests/keywords.test.js
import { processText } from '../src/keywords';

describe('processText', () => {
    it('should extract keywords', async () => {
        const text = 'Python é uma linguagem de programação';
        const keywords = await processText(text);
        expect(keywords).toContain('Python');
    });
});
```

### 2. Integração

#### Python
```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_extract_keywords():
    response = client.post(
        "/api/v1/keywords/extract",
        json={"text": "Python é uma linguagem"}
    )
    assert response.status_code == 200
    assert "keywords" in response.json()
```

#### JavaScript
```javascript
// tests/integration/api.test.js
import request from 'supertest';
import app from '../src/app';

describe('API', () => {
    it('should extract keywords', async () => {
        const response = await request(app)
            .post('/api/v1/keywords/extract')
            .send({ text: 'Python é uma linguagem' });
        expect(response.status).toBe(200);
        expect(response.body).toHaveProperty('keywords');
    });
});
```

## Git

### 1. Commits

```bash
# Tipos
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: tarefas gerais

# Exemplo
git commit -m "feat: adiciona extração de keywords em português"
```

### 2. Branches

```bash
# Nomenclatura
feature/nova-funcionalidade
fix/correcao-bug
docs/atualizacao
refactor/otimizacao

# Exemplo
git checkout -b feature/keywords-pt
```

### 3. PR

```markdown
# Descrição
Adiciona extração de keywords em português

# Mudanças
- Implementa processamento de texto em PT
- Adiciona suporte a acentuação
- Atualiza documentação

# Testes
- [x] Unitários
- [x] Integração
- [x] E2E

# Checklist
- [ ] Código segue padrões
- [ ] Testes passam
- [ ] Documentação atualizada
```

## CI/CD

### 1. GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest
          pylint src
          mypy src
```

### 2. GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - lint
  - type-check

test:
  stage: test
  script:
    - pytest

lint:
  stage: lint
  script:
    - pylint src

type-check:
  stage: type-check
  script:
    - mypy src
```

## Documentação

### 1. Código

```python
def process_text(text: str) -> List[str]:
    """
    Processa texto e retorna keywords.

    Args:
        text: Texto para processar

    Returns:
        Lista de keywords encontradas

    Examples:
        >>> process_text("Python é uma linguagem")
        ['Python', 'linguagem']
    """
    pass
```

### 2. API

```python
@app.post("/api/v1/keywords/extract")
async def extract_keywords(
    request: KeywordRequest
) -> KeywordResponse:
    """
    Extrai keywords de um texto.

    Args:
        request: Requisição com texto

    Returns:
        Resposta com keywords

    Raises:
        HTTPException: Se texto inválido
    """
    pass
```

## Debugging

### 1. Python

```python
import logging
import pdb

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"Processando dados: {data}")
    # Código
    pdb.set_trace()  # Breakpoint
```

### 2. JavaScript

```javascript
// Logging
console.debug('Processando dados:', data);

// Debugger
debugger;  // Breakpoint
```

## Performance

### 1. Profiling

#### Python
```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    # Código
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

#### JavaScript
```javascript
console.time('process');
// Código
console.timeEnd('process');
```

### 2. Otimização

#### Python
```python
# Cache
from functools import lru_cache

@lru_cache(maxsize=128)
def process_text(text):
    return [word for word in text.split()]

# Async
async def process_batch(texts):
    return await asyncio.gather(
        *[process_text(text) for text in texts]
    )
```

#### JavaScript
```javascript
// Cache
const cache = new Map();

function processText(text) {
    if (cache.has(text)) {
        return cache.get(text);
    }
    const result = text.split(' ');
    cache.set(text, result);
    return result;
}

// Async
async function processBatch(texts) {
    return Promise.all(texts.map(processText));
}
```

## Segurança

### 1. Validação

#### Python
```python
from pydantic import BaseModel, validator

class KeywordRequest(BaseModel):
    text: str
    language: str

    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Texto não pode ser vazio')
        return v
```

#### JavaScript
```javascript
// Validação
function validateRequest(request) {
    if (!request.text?.trim()) {
        throw new Error('Texto não pode ser vazio');
    }
    return request;
}
```

### 2. Sanitização

#### Python
```python
import html

def sanitize_text(text: str) -> str:
    """Sanitiza texto."""
    return html.escape(text.strip())
```

#### JavaScript
```javascript
function sanitizeText(text) {
    return text.trim().replace(/[<>]/g, '');
}
```

## Contatos

### 1. Suporte
- Email: support@example.com
- Slack: #omni-keywords-dev
- Jira: OMNI-KW

### 2. Mentores
- João Silva (joao@example.com)
- Maria Santos (maria@example.com) 