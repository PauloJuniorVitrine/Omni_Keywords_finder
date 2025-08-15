# Guia de Testes

Este documento detalha as práticas de teste do Omni Keywords Finder.

## Testes Unitários

### 1. Python

```python
# tests/unit/test_keyword_service.py
import pytest
from application.services.keyword_service import KeywordService
from domain.entities.keyword import Keyword

def test_process_keyword():
    # Arrange
    service = KeywordService()
    text = "test keyword"
    
    # Act
    result = service.process_keyword(text)
    
    # Assert
    assert isinstance(result, Keyword)
    assert result.text == text
    assert result.cluster is None
    assert result.score == 0.0

def test_process_keyword_invalid():
    # Arrange
    service = KeywordService()
    text = ""
    
    # Act/Assert
    with pytest.raises(ValueError):
        service.process_keyword(text)
```

### 2. TypeScript

```typescript
// tests/unit/KeywordService.test.ts
import { KeywordService } from '../../src/services/KeywordService';

describe('KeywordService', () => {
  let service: KeywordService;
  
  beforeEach(() => {
    service = new KeywordService('http://api');
  });
  
  it('should process keyword', async () => {
    // Arrange
    const text = 'test keyword';
    
    // Act
    const result = await service.processKeyword(text);
    
    // Assert
    expect(result).toBeDefined();
    expect(result.text).toBe(text);
    expect(result.cluster).toBeNull();
    expect(result.score).toBe(0);
  });
  
  it('should throw error for invalid keyword', async () => {
    // Arrange
    const text = '';
    
    // Act/Assert
    await expect(service.processKeyword(text))
      .rejects
      .toThrow('Texto inválido');
  });
});
```

## Testes de Integração

### 1. API

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

def test_process_keyword():
    # Arrange
    client = TestClient(app)
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

def test_process_keyword_invalid():
    # Arrange
    client = TestClient(app)
    text = ""
    
    # Act
    response = client.post(
        "/keywords/process",
        json={"text": text}
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
```

### 2. Frontend

```typescript
// tests/integration/KeywordForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { KeywordForm } from '../../src/components/KeywordForm';

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
  
  it('should show error for invalid keyword', async () => {
    // Arrange
    render(<KeywordForm />);
    const input = screen.getByPlaceholderText('Digite uma keyword');
    
    // Act
    fireEvent.change(input, { target: { value: '' } });
    fireEvent.click(screen.getByText('Processar'));
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText('Texto inválido')).toBeInTheDocument();
    });
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
  
  it('should process keyword', () => {
    // Arrange
    const text = 'test keyword';
    
    // Act
    cy.get('[data-testid="keyword-input"]')
      .type(text);
    cy.get('[data-testid="submit-button"]')
      .click();
    
    // Assert
    cy.get('[data-testid="result"]')
      .should('contain', text);
  });
  
  it('should show error for invalid keyword', () => {
    // Act
    cy.get('[data-testid="submit-button"]')
      .click();
    
    // Assert
    cy.get('[data-testid="error"]')
      .should('contain', 'Texto inválido');
  });
});
```

### 2. Playwright

```typescript
// tests/e2e/keywords.spec.ts
import { test, expect } from '@playwright/test';

test('should process keyword', async ({ page }) => {
  // Arrange
  await page.goto('/');
  const text = 'test keyword';
  
  // Act
  await page.fill('[data-testid="keyword-input"]', text);
  await page.click('[data-testid="submit-button"]');
  
  // Assert
  await expect(page.locator('[data-testid="result"]'))
    .toContainText(text);
});

test('should show error for invalid keyword', async ({ page }) => {
  // Arrange
  await page.goto('/');
  
  // Act
  await page.click('[data-testid="submit-button"]');
  
  // Assert
  await expect(page.locator('[data-testid="error"]'))
    .toContainText('Texto inválido');
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
```

### 2. k6

```javascript
// tests/performance/k6.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export default function() {
  const response = http.post(
    'http://api/keywords/process',
    JSON.stringify({ text: 'test keyword' }),
    {
      headers: { 'Content-Type': 'application/json' }
    }
  );
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'has text': (r) => r.json('text') === 'test keyword'
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
    .venv/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

### 2. TypeScript

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

## Observações

- Manter alta cobertura
- Testar casos de erro
- Validar integrações
- Simular carga
- Documentar testes
- Automatizar execução
- Otimizar performance
- Manter compatibilidade
- Revisar periodicamente
- Manter histórico 