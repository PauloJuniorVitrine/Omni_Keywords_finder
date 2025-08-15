# Guia de Contribuição

## Visão Geral

Este guia descreve o processo de contribuição para o Omni Keywords Finder.

## Pré-requisitos

- Git
- Python 3.8+
- Docker
- Editor de código (VS Code recomendado)
- Conta no GitHub

## Processo de Contribuição

### 1. Fork e Clone

```bash
# Fork no GitHub
# Clone seu fork
git clone https://github.com/your-username/omni_keywords_finder.git
cd omni_keywords_finder

# Adicione upstream
git remote add upstream https://github.com/original-org/omni_keywords_finder.git
```

### 2. Branch

```bash
# Crie uma branch
git checkout -b feature/nova-funcionalidade

# Ou para correção
git checkout -b fix/correcao-bug
```

### 3. Desenvolvimento

1. Instale dependências:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

2. Configure ambiente:
```bash
cp .env.example .env
# Edite .env
```

3. Execute testes:
```bash
pytest
```

### 4. Commits

```bash
# Adicione mudanças
git add .

# Commit
git commit -m "feat: adiciona nova funcionalidade"

# Push
git push origin feature/nova-funcionalidade
```

### 5. Pull Request

1. Crie PR no GitHub
2. Preencha o template
3. Aguarde review

## Padrões de Código

### 1. Python

- PEP 8
- Docstrings
- Type hints
- Testes unitários

```python
def process_text(text: str) -> List[str]:
    """
    Processa texto e retorna keywords.

    Args:
        text: Texto para processar

    Returns:
        Lista de keywords encontradas
    """
    # Implementação
    pass
```

### 2. JavaScript

- ESLint
- Prettier
- JSDoc
- Testes Jest

```javascript
/**
 * Processa texto e retorna keywords
 * @param {string} text - Texto para processar
 * @returns {string[]} Lista de keywords
 */
function processText(text) {
    // Implementação
}
```

### 3. Git

- Conventional Commits
- Branch naming
- PR description

```bash
# Tipos de commit
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: tarefas gerais
```

## Testes

### 1. Unitários

```bash
# Execute todos
pytest

# Execute específico
pytest tests/test_keywords.py

# Com coverage
pytest --cov=src
```

### 2. Integração

```bash
# Execute todos
pytest tests/integration/

# Execute específico
pytest tests/integration/test_api.py
```

### 3. E2E

```bash
# Execute todos
pytest tests/e2e/

# Execute específico
pytest tests/e2e/test_workflow.py
```

## Documentação

### 1. Código

- Docstrings
- Comentários
- README

### 2. API

- OpenAPI/Swagger
- Exemplos
- Erros

### 3. Guias

- Instalação
- Uso
- Troubleshooting

## Review

### 1. Checklist

- [ ] Código segue padrões
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Sem conflitos
- [ ] PR descrição clara

### 2. Processo

1. Self-review
2. Peer review
3. CI/CD
4. Merge

## CI/CD

### 1. GitHub Actions

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test
        run: pytest
```

### 2. Verificações

- Lint
- Testes
- Coverage
- Build

## Comunicação

### 1. Issues

- Template
- Labels
- Assignees

### 2. Discussões

- GitHub Discussions
- Slack
- Email

### 3. Reuniões

- Weekly sync
- Planning
- Review

## Licença

- MIT License
- Copyright notice
- Contribuição = aceitação

## Código de Conduta

- Respeito
- Inclusão
- Profissionalismo

## Agradecimentos

- Contribuidores
- Mantenedores
- Comunidade 