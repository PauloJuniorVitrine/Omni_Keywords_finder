# Guia de Desenvolvimento

Este documento detalha as práticas de desenvolvimento do Omni Keywords Finder.

## Ambiente

### 1. Requisitos

- Python 3.9+
- Node.js 16+
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+

### 2. Configuração

```bash
# Clonar repositório
git clone https://github.com/your-org/omni-keywords-finder.git
cd omni-keywords-finder

# Criar ambiente Python
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências Python
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Instalar dependências Node
npm install
```

## Estrutura

### 1. Diretórios

```
omni-keywords-finder/
├── api/                 # API FastAPI
├── application/         # Casos de uso
├── domain/             # Entidades e regras
├── infrastructure/     # Implementações
├── frontend/           # Interface React
├── ml/                 # Modelos ML
├── tests/              # Testes
└── docs/               # Documentação
```

### 2. Arquivos

```
omni-keywords-finder/
├── .env.example        # Variáveis de ambiente
├── .gitignore         # Arquivos ignorados
├── docker-compose.yml # Containers
├── Dockerfile         # Imagem Docker
├── README.md          # Documentação
└── requirements.txt   # Dependências
```

## Desenvolvimento

### 1. Python

```python
# Estrutura de código
def process_keyword(text: str) -> Keyword:
    """
    Processa uma keyword.
    
    Args:
        text: Texto da keyword
        
    Returns:
        Keyword processada
        
    Raises:
        ValueError: Se texto inválido
    """
    if not text or not text.strip():
        raise ValueError("Texto inválido")
    
    return Keyword(text=text.strip())

# Tratamento de erros
try:
    result = await process_keyword(text)
except ValueError as e:
    logger.error(f"Erro ao processar keyword: {e}")
    raise HTTPException(
        status_code=400,
        detail=str(e)
    )

# Logging
logger.info(
    "Keyword processada",
    keyword=text,
    cluster=result.cluster,
    score=result.score
)
```

### 2. TypeScript

```typescript
// Estrutura de código
async function processKeyword(text: string): Promise<Keyword> {
  if (!text?.trim()) {
    throw new Error('Texto inválido');
  }
  
  return {
    text: text.trim(),
    cluster: null,
    score: 0
  };
}

// Tratamento de erros
try {
  const result = await processKeyword(text);
} catch (error) {
  console.error('Erro ao processar keyword:', error);
  throw new Error('Falha ao processar keyword');
}

// Logging
console.log('Keyword processada:', {
  text,
  cluster: result.cluster,
  score: result.score
});
```

## Testes

### 1. Python

```python
# Testes unitários
def test_process_keyword():
    # Arrange
    text = "test keyword"
    
    # Act
    result = process_keyword(text)
    
    # Assert
    assert result.text == text
    assert result.cluster is None
    assert result.score == 0

# Testes de integração
async def test_api_process_keyword():
    # Arrange
    client = TestClient(app)
    text = "test keyword"
    
    # Act
    response = await client.post(
        "/keywords/process",
        json={"text": text}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == text
```

### 2. TypeScript

```typescript
// Testes unitários
describe('KeywordService', () => {
  it('should process keyword', async () => {
    // Arrange
    const text = 'test keyword';
    
    // Act
    const result = await processKeyword(text);
    
    // Assert
    expect(result.text).toBe(text);
    expect(result.cluster).toBeNull();
    expect(result.score).toBe(0);
  });
});

// Testes de integração
describe('KeywordForm', () => {
  it('should submit keyword', async () => {
    // Arrange
    render(<KeywordForm />);
    const input = screen.getByPlaceholderText('Digite uma keyword');
    
    // Act
    fireEvent.change(input, { target: { value: 'test' } });
    fireEvent.click(screen.getByText('Processar'));
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText('Processado')).toBeInTheDocument();
    });
  });
});
```

## CI/CD

### 1. GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest
    
    - name: Run linting
      run: |
        flake8
        black --check .
        isort --check-only .
```

### 2. Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

## Observações

- Seguir padrões de código
- Manter documentação atualizada
- Testar adequadamente
- Revisar código
- Manter segurança
- Otimizar performance
- Manter compatibilidade
- Documentar práticas
- Revisar periodicamente
- Manter histórico 