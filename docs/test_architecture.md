# Arquitetura de Testes

Este documento detalha a arquitetura de testes do Omni Keywords Finder.

## Estratégia de Testes

### Testes Unitários
```python
# tests/unit/test_keyword.py
def test_keyword_creation():
    keyword = Keyword(
        text="seo optimization",
        volume=1000,
        difficulty=0.5,
        language="en"
    )
    assert keyword.text == "seo optimization"
    assert keyword.volume == 1000
    assert keyword.difficulty == 0.5
    assert keyword.language == "en"

def test_keyword_validation():
    with pytest.raises(ValueError):
        Keyword(
            text="",
            volume=1000,
            difficulty=0.5,
            language="en"
        )
```

### Testes de Integração
```python
# tests/integration/test_keyword_processor.py
def test_keyword_processing():
    processor = KeywordProcessor()
    result = processor.process("seo optimization")
    assert result.text == "seo optimization"
    assert result.volume > 0
    assert 0 <= result.difficulty <= 1

def test_cluster_creation():
    service = ClusterService()
    keywords = [
        Keyword(text="seo", volume=1000, difficulty=0.5),
        Keyword(text="optimization", volume=800, difficulty=0.6)
    ]
    cluster = service.create_cluster(keywords)
    assert len(cluster.keywords) == 2
    assert cluster.score > 0
```

### Testes E2E
```typescript
// tests/e2e/keywords.test.ts
describe('Keywords Flow', () => {
  it('should process and display keywords', async () => {
    await page.goto('/keywords');
    await page.fill('[data-testid="keyword-input"]', 'seo optimization');
    await page.click('[data-testid="process-button"]');
    await expect(page.locator('[data-testid="keyword-list"]'))
      .toContainText('seo optimization');
  });
});
```

### Testes de Carga
```python
# tests/load/locustfile.py
class KeywordUser(HttpUser):
    @task
    def process_keyword(self):
        self.client.post("/keywords/process", json={
            "text": "seo optimization"
        })

    @task
    def get_clusters(self):
        self.client.get("/clusters")
```

## Cobertura

### Backend
```python
# pytest.ini
[pytest]
addopts = --cov=app --cov-report=html
testpaths = tests
python_files = test_*.py
```

### Frontend
```json
// jest.config.js
{
  "collectCoverageFrom": [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts"
  ],
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    }
  }
}
```

## Mocks e Fixtures

### Backend
```python
# tests/fixtures/keywords.py
@pytest.fixture
def keyword_data():
    return {
        "text": "seo optimization",
        "volume": 1000,
        "difficulty": 0.5,
        "language": "en"
    }

@pytest.fixture
def mock_ml_model():
    with patch('app.ml.MLModel') as mock:
        mock.vectorize.return_value = [0.1, 0.2, 0.3]
        yield mock
```

### Frontend
```typescript
// tests/mocks/api.ts
export const mockApi = {
  processKeyword: jest.fn().mockResolvedValue({
    text: "seo optimization",
    volume: 1000,
    difficulty: 0.5
  }),
  getClusters: jest.fn().mockResolvedValue([
    {
      id: "1",
      name: "SEO Cluster",
      keywords: []
    }
  ])
};
```

## CI/CD

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install
      - name: Run tests
        run: |
          pytest
          npm test
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Observações

1. Cobertura mínima de 80%
2. Testes automatizados
3. Mocks e fixtures
4. CI/CD integrado
5. Relatórios de cobertura
6. Testes de performance
7. Testes de segurança
8. Testes de acessibilidade
9. Testes de integração
10. Documentação atualizada 