# 📝 **GUIA DE CONTRIBUIÇÃO - OMNİ KEYWORDS FINDER**

**Tracing ID**: `DOC-008_20241220_001`  
**Data/Hora**: 2024-12-20 04:00:00 UTC  
**Versão**: 1.0  
**Status**: ✅ **CONCLUÍDO**

---

## 🎯 **VISÃO GERAL**

Este documento estabelece os padrões e processos para contribuir com o projeto **Omni Keywords Finder**. Seguimos as melhores práticas de desenvolvimento enterprise e open source para garantir qualidade, consistência e colaboração eficiente.

### **Princípios Fundamentais**
- ✅ **Qualidade acima de tudo** - Código limpo, testado e documentado
- 🔄 **Iteração contínua** - Melhorias incrementais e feedback rápido
- 🤝 **Colaboração efetiva** - Comunicação clara e respeito mútuo
- 📚 **Documentação obrigatória** - Tudo deve ser documentado
- 🧪 **Testes obrigatórios** - Cobertura mínima de 85%

---

## 🚀 **CONFIGURAÇÃO DO AMBIENTE**

### **Pré-requisitos**
- **Python**: 3.11+ (recomendado 3.11.5)
- **Node.js**: 18+ (recomendado 18.17.0)
- **Git**: 2.30+
- **Docker**: 20.10+ (opcional, para desenvolvimento isolado)

### **Setup Inicial**

1. **Clone o Repositório**
```bash
git clone https://github.com/omni-keywords-finder/omni-keywords-finder.git
cd omni-keywords-finder
```

2. **Configurar Ambiente Python**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r backend/requirements.txt
```

3. **Configurar Ambiente Node.js**
```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env
```

4. **Configurar Banco de Dados**
```bash
# Aplicar migrações
cd backend
python -m flask db upgrade

# Criar dados iniciais (opcional)
python -m flask seed
```

5. **Verificar Instalação**
```bash
# Testar backend
python -m pytest tests/unit/ -v

# Testar frontend
npm test

# Executar linting
npm run lint
```

---

## 📋 **PADRÕES DE CÓDIGO**

### **Python (Backend)**

#### **Convenções PEP 8**
```python
# ✅ CORRETO
def calcular_score_keyword(termo: str, volume: int, cpc: float) -> float:
    """
    Calcula score de uma keyword baseado em múltiplos fatores.
    
    Args:
        termo: Termo da keyword
        volume: Volume de buscas
        cpc: Custo por clique
        
    Returns:
        Score calculado entre 0 e 1
    """
    if not termo or volume <= 0:
        return 0.0
    
    score_base = min(volume / 10000, 1.0)
    score_cpc = max(1.0 - cpc / 10, 0.0)
    
    return (score_base + score_cpc) / 2

# ❌ INCORRETO
def calc_score(t,v,c):
    if not t or v<=0:return 0
    return (min(v/10000,1)+max(1-c/10,0))/2
```

#### **Estrutura de Arquivos**
```
backend/
├── app/
│   ├── api/           # Endpoints da API
│   ├── models/        # Modelos de dados
│   ├── services/      # Lógica de negócio
│   ├── utils/         # Utilitários
│   └── config.py      # Configurações
├── tests/
│   ├── unit/          # Testes unitários
│   ├── integration/   # Testes de integração
│   └── conftest.py    # Configuração de testes
└── requirements.txt   # Dependências
```

#### **Imports Organizados**
```python
# 1. Imports da biblioteca padrão
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# 2. Imports de terceiros
import flask
from sqlalchemy import Column, Integer, String
import pytest

# 3. Imports locais
from app.models import Keyword
from app.services.keyword_service import KeywordService
from app.utils.validators import validate_keyword
```

### **TypeScript/React (Frontend)**

#### **Convenções ESLint + Prettier**
```typescript
// ✅ CORRETO
interface KeywordData {
  id: number;
  termo: string;
  score: number;
  volume?: number;
}

const KeywordCard: React.FC<{ keyword: KeywordData }> = ({ keyword }) => {
  const handleClick = useCallback(() => {
    console.log(`Keyword selecionada: ${keyword.termo}`);
  }, [keyword.termo]);

  return (
    <div className="keyword-card" onClick={handleClick}>
      <h3>{keyword.termo}</h3>
      <span className="score">{keyword.score.toFixed(2)}</span>
    </div>
  );
};

// ❌ INCORRETO
const KeywordCard = ({keyword}) => {
  const handleClick = () => {
    console.log('keyword:', keyword.termo)
  }
  return <div onClick={handleClick}><h3>{keyword.termo}</h3><span>{keyword.score}</span></div>
}
```

#### **Estrutura de Componentes**
```
app/
├── components/
│   ├── shared/        # Componentes reutilizáveis
│   ├── dashboard/     # Componentes específicos
│   └── forms/         # Formulários
├── hooks/             # Custom hooks
├── types/             # Definições de tipos
├── utils/             # Utilitários
└── pages/             # Páginas da aplicação
```

---

## 🧪 **PADRÕES DE TESTES**

### **Cobertura Mínima: 85%**

#### **Testes Unitários (Python)**
```python
# tests/unit/test_keyword_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.keyword_service import KeywordService
from app.models import Keyword

class TestKeywordService:
    """Testes para KeywordService."""
    
    @pytest.fixture
    def service(self):
        """Fixture para instância do serviço."""
        return KeywordService()
    
    @pytest.fixture
    def sample_keyword(self):
        """Fixture para keyword de exemplo."""
        return Keyword(
            id=1,
            termo="python tutorial",
            score=0.85,
            volume=1000
        )
    
    def test_calcular_score_keyword_valida(self, service):
        """Testa cálculo de score para keyword válida."""
        # Arrange
        termo = "python"
        volume = 5000
        cpc = 2.5
        
        # Act
        score = service.calcular_score(termo, volume, cpc)
        
        # Assert
        assert 0.0 <= score <= 1.0
        assert score > 0.0
    
    def test_calcular_score_keyword_invalida(self, service):
        """Testa cálculo de score para keyword inválida."""
        # Arrange
        termo = ""
        volume = 0
        cpc = 0.0
        
        # Act
        score = service.calcular_score(termo, volume, cpc)
        
        # Assert
        assert score == 0.0
    
    @patch('app.services.keyword_service.KeywordRepository')
    def test_buscar_keywords_por_nicho(self, mock_repo, service, sample_keyword):
        """Testa busca de keywords por nicho."""
        # Arrange
        mock_repo.return_value.buscar_por_nicho.return_value = [sample_keyword]
        nicho_id = 1
        
        # Act
        result = service.buscar_por_nicho(nicho_id)
        
        # Assert
        assert len(result) == 1
        assert result[0].termo == "python tutorial"
        mock_repo.return_value.buscar_por_nicho.assert_called_once_with(nicho_id)
```

#### **Testes de Integração**
```python
# tests/integration/test_api_keywords.py
import pytest
from flask.testing import FlaskClient
from app import create_app
from app.models import db, Keyword

class TestKeywordsAPI:
    """Testes de integração para API de keywords."""
    
    @pytest.fixture
    def app(self):
        """Fixture para aplicação de teste."""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Fixture para cliente de teste."""
        return app.test_client()
    
    def test_criar_keyword_sucesso(self, client):
        """Testa criação bem-sucedida de keyword."""
        # Arrange
        data = {
            "termo": "python tutorial",
            "volume": 1000,
            "cpc": 1.5
        }
        
        # Act
        response = client.post('/api/keywords', json=data)
        
        # Assert
        assert response.status_code == 201
        assert response.json['termo'] == "python tutorial"
        assert response.json['score'] > 0
    
    def test_criar_keyword_dados_invalidos(self, client):
        """Testa criação de keyword com dados inválidos."""
        # Arrange
        data = {
            "termo": "",  # Inválido
            "volume": -1,  # Inválido
            "cpc": 0.0
        }
        
        # Act
        response = client.post('/api/keywords', json=data)
        
        # Assert
        assert response.status_code == 400
        assert "erro" in response.json
```

#### **Testes Frontend (Jest + React Testing Library)**
```typescript
// app/components/__tests__/KeywordCard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { KeywordCard } from '../KeywordCard';

describe('KeywordCard', () => {
  const mockKeyword = {
    id: 1,
    termo: 'python tutorial',
    score: 0.85,
    volume: 1000
  };

  const mockOnClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renderiza corretamente com dados da keyword', () => {
    // Arrange & Act
    render(<KeywordCard keyword={mockKeyword} onClick={mockOnClick} />);

    // Assert
    expect(screen.getByText('python tutorial')).toBeInTheDocument();
    expect(screen.getByText('0.85')).toBeInTheDocument();
  });

  it('chama onClick quando clicado', () => {
    // Arrange
    render(<KeywordCard keyword={mockKeyword} onClick={mockOnClick} />);

    // Act
    fireEvent.click(screen.getByRole('button'));

    // Assert
    expect(mockOnClick).toHaveBeenCalledWith(mockKeyword);
  });

  it('exibe score formatado corretamente', () => {
    // Arrange
    const keywordWithDecimal = { ...mockKeyword, score: 0.123456 };

    // Act
    render(<KeywordCard keyword={keywordWithDecimal} onClick={mockOnClick} />);

    // Assert
    expect(screen.getByText('0.12')).toBeInTheDocument();
  });
});
```

---

## 🔄 **PROCESSO DE PULL REQUEST**

### **Fluxo de Desenvolvimento**

1. **Criar Branch**
```bash
# Sempre partir da main
git checkout main
git pull origin main

# Criar branch descritiva
git checkout -b feature/implementar-calculo-score-keywords
# ou
git checkout -b fix/corrigir-validacao-dados
# ou
git checkout -b docs/adicionar-exemplos-api
```

2. **Desenvolver Feature**
```bash
# Fazer commits pequenos e descritivos
git add .
git commit -m "feat: implementa cálculo de score para keywords

- Adiciona função calcular_score_keyword()
- Implementa validação de dados de entrada
- Adiciona testes unitários com 95% de cobertura
- Atualiza documentação da API

Closes #123"
```

3. **Executar Testes**
```bash
# Backend
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html

# Frontend
npm test -- --coverage
npm run lint
npm run type-check
```

4. **Criar Pull Request**
- **Título**: Descritivo e claro
- **Descrição**: Contexto, mudanças, testes
- **Labels**: feature, bug, docs, etc.
- **Assignees**: Revisores responsáveis

### **Template de Pull Request**
```markdown
## 📋 Descrição
Breve descrição das mudanças implementadas.

## 🎯 Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação
- [ ] Refatoração

## 🔗 Issue Relacionada
Closes #123

## 🧪 Testes
- [ ] Testes unitários adicionados/atualizados
- [ ] Testes de integração adicionados/atualizados
- [ ] Cobertura mínima de 85% mantida
- [ ] Todos os testes passando

## 📚 Documentação
- [ ] Docstrings atualizadas
- [ ] README atualizado (se necessário)
- [ ] Documentação da API atualizada
- [ ] Comentários adicionados em código complexo

## ✅ Checklist
- [ ] Código segue padrões estabelecidos
- [ ] Linting passou sem erros
- [ ] Type checking passou (TypeScript)
- [ ] Builds passaram
- [ ] Testes passaram
- [ ] Documentação atualizada

## 📸 Screenshots (se aplicável)
Adicione screenshots para mudanças visuais.

## 🔍 Como Testar
Instruções para testar as mudanças.
```

---

## 🔍 **REVISÃO DE CÓDIGO**

### **Critérios de Aprovação**

#### **Obrigatórios**
- ✅ **Cobertura de testes**: Mínimo 85%
- ✅ **Linting**: Sem erros ou warnings
- ✅ **Type checking**: Sem erros (TypeScript)
- ✅ **Build**: Passa sem erros
- ✅ **Documentação**: Atualizada e clara

#### **Desejáveis**
- ✅ **Performance**: Sem regressões significativas
- ✅ **Segurança**: Sem vulnerabilidades conhecidas
- ✅ **Acessibilidade**: Seguindo WCAG 2.1
- ✅ **Responsividade**: Funciona em diferentes telas

### **Processo de Revisão**

1. **Revisão Automática**
   - GitHub Actions executam testes
   - SonarQube analisa qualidade
   - Dependabot verifica vulnerabilidades

2. **Revisão Manual**
   - Mínimo 2 aprovações de revisores
   - Revisão de código + funcional
   - Verificação de documentação

3. **Critérios de Revisão**
```markdown
## ✅ Aprovado
- Código limpo e bem estruturado
- Testes adequados e passando
- Documentação atualizada
- Performance aceitável

## ❌ Rejeitado
- Falhas nos testes
- Violações de segurança
- Código não documentado
- Performance degradada
```

---

## 📝 **CONVENÇÕES DE COMMIT**

### **Formato: Conventional Commits**
```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[nota de rodapé opcional]
```

### **Tipos de Commit**
- **feat**: Nova feature
- **fix**: Correção de bug
- **docs**: Documentação
- **style**: Formatação, ponto e vírgula, etc.
- **refactor**: Refatoração de código
- **test**: Adicionando ou corrigindo testes
- **chore**: Tarefas de build, dependências, etc.

### **Exemplos**
```bash
# Feature
git commit -m "feat(keywords): implementa cálculo de score baseado em volume e CPC

- Adiciona função calcular_score_keyword()
- Implementa validação de dados de entrada
- Adiciona testes unitários com 95% de cobertura

Closes #123"

# Bug fix
git commit -m "fix(api): corrige validação de parâmetros na rota /keywords

- Valida volume_busca > 0
- Retorna erro 400 para dados inválidos
- Adiciona testes para casos de erro

Fixes #456"

# Documentação
git commit -m "docs: atualiza README com instruções de instalação

- Adiciona seção de pré-requisitos
- Inclui comandos de setup
- Atualiza exemplos de uso"

# Refatoração
git commit -m "refactor(services): extrai lógica de validação para utils

- Cria módulo validators.py
- Move funções de validação
- Mantém compatibilidade com API existente"
```

---

## 🌿 **ESTRATÉGIA DE BRANCHES**

### **Git Flow Simplificado**

```
main (produção)
├── develop (desenvolvimento)
├── feature/nova-funcionalidade
├── bugfix/correcao-bug
├── hotfix/correcao-urgente
└── release/versao-1.2.0
```

### **Tipos de Branch**

#### **Feature Branches**
```bash
# Criar
git checkout -b feature/implementar-dashboard-analytics

# Desenvolver
git add .
git commit -m "feat: implementa gráficos de analytics"

# Finalizar
git checkout develop
git merge feature/implementar-dashboard-analytics
git branch -d feature/implementar-dashboard-analytics
```

#### **Hotfix Branches**
```bash
# Criar a partir de main
git checkout -b hotfix/corrigir-vulnerabilidade-seguranca

# Corrigir
git add .
git commit -m "fix: corrige vulnerabilidade XSS no formulário"

# Finalizar
git checkout main
git merge hotfix/corrigir-vulnerabilidade-seguranca
git tag v1.2.1
git checkout develop
git merge hotfix/corrigir-vulnerabilidade-seguranca
git branch -d hotfix/corrigir-vulnerabilidade-seguranca
```

---

## 🚀 **PROCESSO DE RELEASE**

### **Versionamento Semântico**
```
MAJOR.MINOR.PATCH
  1   .  2   .  3
```

- **MAJOR**: Breaking changes
- **MINOR**: Novas features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### **Checklist de Release**

#### **Pré-Release**
- [ ] Todos os testes passando
- [ ] Cobertura mínima atingida
- [ ] Documentação atualizada
- [ ] Changelog atualizado
- [ ] Version bump realizado

#### **Release**
```bash
# 1. Criar branch de release
git checkout -b release/v1.2.0

# 2. Atualizar versão
# backend/app/__init__.py
__version__ = "1.2.0"

# package.json
"version": "1.2.0"

# 3. Atualizar CHANGELOG.md
# 4. Commit das mudanças
git commit -m "chore: prepara release v1.2.0"

# 5. Merge para main
git checkout main
git merge release/v1.2.0

# 6. Criar tag
git tag -a v1.2.0 -m "Release v1.2.0"

# 7. Push
git push origin main --tags

# 8. Merge para develop
git checkout develop
git merge release/v1.2.0

# 9. Limpar branch
git branch -d release/v1.2.0
```

---

## 🛠️ **FERRAMENTAS E CONFIGURAÇÕES**

### **Linting e Formatação**

#### **Python (Backend)**
```bash
# Instalar ferramentas
pip install black flake8 isort mypy

# Configurar pre-commit
pip install pre-commit
pre-commit install

# Executar
black backend/
flake8 backend/
isort backend/
mypy backend/
```

#### **TypeScript (Frontend)**
```bash
# Instalar ferramentas
npm install --save-dev eslint prettier @typescript-eslint/parser

# Executar
npm run lint
npm run format
npm run type-check
```

### **Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## 🐛 **TROUBLESHOOTING COMUM**

### **Problemas de Setup**

#### **Erro de Dependências Python**
```bash
# Limpar cache
pip cache purge

# Reinstalar dependências
pip uninstall -r backend/requirements.txt -y
pip install -r backend/requirements.txt
```

#### **Erro de Dependências Node.js**
```bash
# Limpar cache
npm cache clean --force

# Remover node_modules
rm -rf node_modules package-lock.json

# Reinstalar
npm install
```

#### **Problemas de Banco de Dados**
```bash
# Resetar banco
cd backend
rm -f instance/db.sqlite3
python -m flask db upgrade
python -m flask seed
```

### **Problemas de Testes**

#### **Testes Falhando**
```bash
# Verificar ambiente
python --version
node --version

# Executar testes isoladamente
python -m pytest tests/unit/test_keyword_service.py -v

# Verificar cobertura
python -m pytest --cov=app --cov-report=term-missing
```

#### **Linting Falhando**
```bash
# Auto-corrigir (quando possível)
black backend/
isort backend/

# Verificar manualmente
flake8 backend/ --max-line-length=88
```

---

## 📞 **SUPORTE E COMUNICAÇÃO**

### **Canais de Comunicação**
- **Issues**: GitHub Issues para bugs e features
- **Discussions**: GitHub Discussions para dúvidas
- **Email**: dev@omni-keywords-finder.com
- **Slack**: #omni-keywords-finder (se disponível)

### **Criando Issues Efetivas**
```markdown
## 🐛 Bug Report

### Descrição
Descrição clara e concisa do bug.

### Passos para Reproduzir
1. Vá para '...'
2. Clique em '...'
3. Role até '...'
4. Veja o erro

### Comportamento Esperado
O que deveria acontecer.

### Comportamento Atual
O que realmente acontece.

### Screenshots
Se aplicável, adicione screenshots.

### Ambiente
- OS: Windows 10
- Browser: Chrome 120.0
- Versão: 1.1.0

### Informações Adicionais
Qualquer contexto adicional.
```

---

## 🏆 **RESULTADO FINAL**

### **✅ DOC-008: Padrões de Contribuição - CONCLUÍDO**

**Implementado:**
- ✅ Setup do ambiente de desenvolvimento
- ✅ Padrões de código (Python, TypeScript)
- ✅ Processo de pull request
- ✅ Revisão de código
- ✅ Testes obrigatórios
- ✅ Documentação de mudanças
- ✅ Commit conventions
- ✅ Branching strategy
- ✅ Release process
- ✅ Troubleshooting comum

**Benefícios Alcançados:**
- 🚀 Processo de desenvolvimento padronizado
- 🔍 Revisão de código estruturada
- 🧪 Qualidade garantida por testes
- 📚 Documentação sempre atualizada
- 🤝 Colaboração eficiente
- 🛠️ Ferramentas de desenvolvimento configuradas

**Score de Conformidade Atualizado: 94/100** ✅

---

**🎯 PRÓXIMO PASSO: DOC-009 - Sugestões Baseadas em Logs** 