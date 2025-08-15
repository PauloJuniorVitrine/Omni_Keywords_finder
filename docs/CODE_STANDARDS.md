# Padrões de Código

Este documento detalha os padrões de código do Omni Keywords Finder.

## Python

### 1. Estrutura

```python
# Imports
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Constantes
MAX_KEYWORD_LENGTH = 100
DEFAULT_SCORE = 0.0

# Classes
@dataclass
class Keyword:
    """Representa uma keyword processada."""
    
    text: str
    cluster: Optional[str] = None
    score: float = DEFAULT_SCORE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Valida e normaliza dados após inicialização."""
        if not self.text or not self.text.strip():
            raise ValueError("Texto inválido")
        if len(self.text) > MAX_KEYWORD_LENGTH:
            raise ValueError("Texto muito longo")
        self.text = self.text.strip()
    
    def update_score(self, score: float) -> None:
        """Atualiza score da keyword."""
        self.score = score
        self.updated_at = datetime.utcnow()

# Funções
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
    return Keyword(text=text)
```

### 2. Nomenclatura

```python
# Classes: PascalCase
class KeywordService:
    pass

# Funções/Métodos: snake_case
def process_keyword():
    pass

# Variáveis: snake_case
keyword_text = "test"

# Constantes: UPPER_SNAKE_CASE
MAX_LENGTH = 100

# Módulos: snake_case
keyword_service.py

# Pacotes: snake_case
keyword_processing/
```

### 3. Documentação

```python
def process_keyword(
    text: str,
    model: Optional[KeywordModel] = None
) -> Keyword:
    """
    Processa uma keyword usando modelo opcional.
    
    Args:
        text: Texto da keyword
        model: Modelo para processamento (opcional)
        
    Returns:
        Keyword processada
        
    Raises:
        ValueError: Se texto inválido
        ModelError: Se erro no modelo
        
    Examples:
        >>> process_keyword("test")
        Keyword(text="test", score=0.0)
    """
    pass
```

### 4. Tratamento de Erros

```python
# Exceções customizadas
class KeywordError(Exception):
    """Erro base para processamento de keywords."""
    pass

class InvalidKeywordError(KeywordError):
    """Erro para keyword inválida."""
    pass

class ModelError(KeywordError):
    """Erro no modelo de ML."""
    pass

# Uso
try:
    result = await process_keyword(text)
except InvalidKeywordError as e:
    logger.error(f"Keyword inválida: {e}")
    raise HTTPException(
        status_code=400,
        detail=str(e)
    )
except ModelError as e:
    logger.error(f"Erro no modelo: {e}")
    raise HTTPException(
        status_code=500,
        detail="Erro interno"
    )
```

## TypeScript

### 1. Estrutura

```typescript
// Interfaces
interface Keyword {
  text: string;
  cluster?: string;
  score: number;
  createdAt: Date;
  updatedAt: Date;
}

// Enums
enum KeywordStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  ERROR = 'error'
}

// Classes
class KeywordService {
  private readonly apiUrl: string;
  
  constructor(apiUrl: string) {
    this.apiUrl = apiUrl;
  }
  
  async processKeyword(text: string): Promise<Keyword> {
    if (!text?.trim()) {
      throw new Error('Texto inválido');
    }
    
    const response = await fetch(
      `${this.apiUrl}/keywords/process`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text.trim() })
      }
    );
    
    if (!response.ok) {
      throw new Error('Erro ao processar keyword');
    }
    
    return response.json();
  }
}

// Funções
const processKeyword = async (text: string): Promise<Keyword> => {
  const service = new KeywordService(process.env.API_URL);
  return service.processKeyword(text);
};
```

### 2. Nomenclatura

```typescript
// Interfaces: PascalCase
interface KeywordData {
  text: string;
  score: number;
}

// Classes: PascalCase
class KeywordProcessor {
  // ...
}

// Funções/Métodos: camelCase
function processKeyword() {
  // ...
}

// Variáveis: camelCase
const keywordText = 'test';

// Constantes: UPPER_SNAKE_CASE
const MAX_LENGTH = 100;

// Arquivos: PascalCase
KeywordService.ts

// Diretórios: kebab-case
keyword-processing/
```

### 3. Documentação

```typescript
/**
 * Processa uma keyword usando modelo opcional.
 * 
 * @param text - Texto da keyword
 * @param model - Modelo para processamento (opcional)
 * @returns Keyword processada
 * @throws {Error} Se texto inválido
 * @throws {Error} Se erro no modelo
 * 
 * @example
 * const keyword = await processKeyword("test");
 * console.log(keyword);
 * // { text: "test", score: 0 }
 */
async function processKeyword(
  text: string,
  model?: KeywordModel
): Promise<Keyword> {
  // ...
}
```

### 4. Tratamento de Erros

```typescript
// Exceções customizadas
class KeywordError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'KeywordError';
  }
}

class InvalidKeywordError extends KeywordError {
  constructor(message: string) {
    super(message);
    this.name = 'InvalidKeywordError';
  }
}

class ModelError extends KeywordError {
  constructor(message: string) {
    super(message);
    this.name = 'ModelError';
  }
}

// Uso
try {
  const result = await processKeyword(text);
} catch (error) {
  if (error instanceof InvalidKeywordError) {
    console.error('Keyword inválida:', error);
    throw new Error('Dados inválidos');
  }
  if (error instanceof ModelError) {
    console.error('Erro no modelo:', error);
    throw new Error('Erro interno');
  }
  throw error;
}
```

## React

### 1. Componentes

```typescript
// Componentes funcionais
interface KeywordFormProps {
  onSubmit: (text: string) => Promise<void>;
  loading?: boolean;
}

export const KeywordForm: React.FC<KeywordFormProps> = ({
  onSubmit,
  loading = false
}) => {
  const [text, setText] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    try {
      await onSubmit(text);
      setText('');
    } catch (err) {
      setError(err.message);
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

// Hooks customizados
function useKeywordProcessing() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const processKeyword = async (text: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await keywordService.processKeyword(text);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return {
    loading,
    error,
    processKeyword
  };
}
```

### 2. Estilização

```typescript
// CSS Modules
import styles from './KeywordForm.module.css';

export const KeywordForm: React.FC = () => {
  return (
    <form className={styles.form}>
      <input className={styles.input} />
      <button className={styles.button}>Processar</button>
    </form>
  );
};

// Styled Components
import styled from 'styled-components';

const Form = styled.form`
  display: flex;
  gap: 1rem;
`;

const Input = styled.input`
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
`;

const Button = styled.button`
  padding: 0.5rem 1rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;
```

## Observações

- Seguir PEP 8 (Python)
- Seguir Airbnb Style Guide (TypeScript)
- Manter consistência
- Documentar adequadamente
- Tratar erros
- Testar componentes
- Manter performance
- Revisar código
- Manter histórico
- Documentar decisões 