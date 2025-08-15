# Práticas de Teste

Este documento detalha as práticas de teste do Omni Keywords Finder.

## Testes Unitários

### 1. Python

```python
# tests/unit/test_keyword_service.py
import pytest
from unittest.mock import Mock, patch
from domain.entities.keyword import Keyword
from application.services.keyword_service import KeywordService

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_model():
    return Mock()

@pytest.fixture
def service(mock_repository, mock_model):
    return KeywordService(mock_repository, mock_model)

def test_process_keyword(service, mock_repository, mock_model):
    # Arrange
    text = "test keyword"
    mock_model.generate_embedding.return_value = [0.1, 0.2, 0.3]
    mock_repository.save.return_value = Keyword(
        text=text,
        cluster="cluster1",
        score=0.8
    )
    
    # Act
    result = service.process_keyword(text)
    
    # Assert
    assert result.text == text
    assert result.cluster == "cluster1"
    assert result.score == 0.8
    mock_model.generate_embedding.assert_called_once_with(text)
    mock_repository.save.assert_called_once()

def test_process_keyword_invalid(service):
    # Arrange
    text = ""
    
    # Act & Assert
    with pytest.raises(ValueError, match="Texto inválido"):
        service.process_keyword(text)

@pytest.mark.asyncio
async def test_process_keyword_async(service, mock_repository, mock_model):
    # Arrange
    text = "test keyword"
    mock_model.generate_embedding.return_value = [0.1, 0.2, 0.3]
    mock_repository.save.return_value = Keyword(
        text=text,
        cluster="cluster1",
        score=0.8
    )
    
    # Act
    result = await service.process_keyword(text)
    
    # Assert
    assert result.text == text
    assert result.cluster == "cluster1"
    assert result.score == 0.8
```

### 2. TypeScript

```typescript
// tests/unit/KeywordService.test.ts
import { KeywordService } from '../../src/services/KeywordService';
import { Keyword } from '../../src/types/Keyword';

describe('KeywordService', () => {
  let service: KeywordService;
  let mockFetch: jest.Mock;
  
  beforeEach(() => {
    mockFetch = jest.fn();
    global.fetch = mockFetch;
    service = new KeywordService('http://api.test');
  });
  
  it('should process keyword successfully', async () => {
    // Arrange
    const text = 'test keyword';
    const expected: Keyword = {
      text,
      cluster: 'cluster1',
      score: 0.8,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(expected)
    });
    
    // Act
    const result = await service.processKeyword(text);
    
    // Assert
    expect(result).toEqual(expected);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://api.test/keywords/process',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      }
    );
  });
  
  it('should throw error on invalid response', async () => {
    // Arrange
    const text = 'test keyword';
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500
    });
    
    // Act & Assert
    await expect(service.processKeyword(text))
      .rejects
      .toThrow('Erro ao processar keyword');
  });
});
```

## Testes de Integração

### 1. API

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from api.app import app
from domain.entities.keyword import Keyword

@pytest.fixture
def client():
    return TestClient(app)

def test_process_keyword(client):
    # Arrange
    text = "test keyword"
    
    # Act
    response = client.post(
        "/keywords/process",
        json={"text": text}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == text
    assert "cluster" in data
    assert "score" in data

def test_process_keyword_invalid(client):
    # Arrange
    text = ""
    
    # Act
    response = client.post(
        "/keywords/process",
        json={"text": text}
    )
    
    # Assert
    assert response.status_code == 400
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_process_keyword_async(client):
    # Arrange
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

### 2. Frontend

```typescript
// tests/integration/KeywordForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { KeywordForm } from '../../src/components/KeywordForm';

describe('KeywordForm', () => {
  const mockOnSubmit = jest.fn();
  
  beforeEach(() => {
    mockOnSubmit.mockClear();
  });
  
  it('should submit keyword successfully', async () => {
    // Arrange
    render(<KeywordForm onSubmit={mockOnSubmit} />);
    const input = screen.getByPlaceholderText('Digite uma keyword');
    const button = screen.getByText('Processar');
    
    // Act
    fireEvent.change(input, { target: { value: 'test keyword' } });
    fireEvent.click(button);
    
    // Assert
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('test keyword');
    });
    expect(input).toHaveValue('');
  });
  
  it('should show error message on failure', async () => {
    // Arrange
    mockOnSubmit.mockRejectedValueOnce(new Error('Erro ao processar'));
    render(<KeywordForm onSubmit={mockOnSubmit} />);
    const input = screen.getByPlaceholderText('Digite uma keyword');
    const button = screen.getByText('Processar');
    
    // Act
    fireEvent.change(input, { target: { value: 'test keyword' } });
    fireEvent.click(button);
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText('Erro ao processar')).toBeInTheDocument();
    });
  });
  
  it('should disable form while processing', async () => {
    // Arrange
    render(<KeywordForm onSubmit={mockOnSubmit} loading={true} />);
    const input = screen.getByPlaceholderText('Digite uma keyword');
    const button = screen.getByText('Processando...');
    
    // Assert
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });
});
```

## Testes E2E

### 1. Cypress

```typescript
// cypress/integration/keywords.spec.ts
describe('Keywords', () => {
  beforeEach(() => {
    cy.visit('/');
  });
  
  it('should process keyword successfully', () => {
    // Arrange
    const text = 'test keyword';
    
    // Act
    cy.get('[data-testid="keyword-input"]')
      .type(text);
    cy.get('[data-testid="submit-button"]')
      .click();
    
    // Assert
    cy.get('[data-testid="result-text"]')
      .should('contain', text);
    cy.get('[data-testid="result-cluster"]')
      .should('exist');
    cy.get('[data-testid="result-score"]')
      .should('exist');
  });
  
  it('should show error on invalid input', () => {
    // Act
    cy.get('[data-testid="submit-button"]')
      .click();
    
    // Assert
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain', 'Texto inválido');
  });
  
  it('should show loading state', () => {
    // Arrange
    const text = 'test keyword';
    
    // Act
    cy.get('[data-testid="keyword-input"]')
      .type(text);
    cy.get('[data-testid="submit-button"]')
      .click();
    
    // Assert
    cy.get('[data-testid="loading-spinner"]')
      .should('be.visible');
    cy.get('[data-testid="submit-button"]')
      .should('be.disabled');
  });
});
```

### 2. Playwright

```typescript
// tests/e2e/keywords.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Keywords', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });
  
  test('should process keyword successfully', async ({ page }) => {
    // Arrange
    const text = 'test keyword';
    
    // Act
    await page.fill('[data-testid="keyword-input"]', text);
    await page.click('[data-testid="submit-button"]');
    
    // Assert
    await expect(page.locator('[data-testid="result-text"]'))
      .toContainText(text);
    await expect(page.locator('[data-testid="result-cluster"]'))
      .toBeVisible();
    await expect(page.locator('[data-testid="result-score"]'))
      .toBeVisible();
  });
  
  test('should show error on invalid input', async ({ page }) => {
    // Act
    await page.click('[data-testid="submit-button"]');
    
    // Assert
    await expect(page.locator('[data-testid="error-message"]'))
      .toBeVisible();
    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('Texto inválido');
  });
  
  test('should show loading state', async ({ page }) => {
    // Arrange
    const text = 'test keyword';
    
    // Act
    await page.fill('[data-testid="keyword-input"]', text);
    await page.click('[data-testid="submit-button"]');
    
    // Assert
    await expect(page.locator('[data-testid="loading-spinner"]'))
      .toBeVisible();
    await expect(page.locator('[data-testid="submit-button"]'))
      .toBeDisabled();
  });
});
```

## Testes de Performance

### 1. Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class KeywordUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def process_keyword(self):
        self.client.post(
            "/keywords/process",
            json={"text": "test keyword"}
        )
    
    @task
    def get_keyword(self):
        self.client.get("/keywords/test%20keyword")
```

### 2. k6

```javascript
// tests/performance/k6.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 20 },
    { duration: '30s', target: 0 }
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01']
  }
};

export default function() {
  const response = http.post(
    'http://api.test/keywords/process',
    JSON.stringify({ text: 'test keyword' }),
    {
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'has cluster': (r) => r.json('cluster') !== null,
    'has score': (r) => r.json('score') !== null
  });
  
  sleep(1);
}
```

## Cobertura

### 1. Python

```ini
# .coveragerc
[run]
source = .
omit =
    tests/*
    venv/*
    .venv/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    raise ImportError
```

### 2. TypeScript

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/serviceWorker.ts'
  ]
};
```

## Observações

- Manter cobertura alta
- Testar casos de erro
- Validar integrações
- Simular carga
- Documentar testes
- Automatizar execução
- Otimizar performance
- Manter histórico
- Revisar periodicamente
- Documentar práticas 