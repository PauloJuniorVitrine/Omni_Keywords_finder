# 🚀 **DOCUMENTAÇÃO GRAPHQL SCHEMA - ENTERPRISE**

**Tracing ID**: `GRAPHQL_SCHEMA_DOCS_20250127_001`  
**Data**: 2025-01-27  
**Versão**: 1.0  
**Status**: Documentação Automática de GraphQL

---

## 🎯 **OBJETIVO**
Este documento define a estrutura para detecção automática de arquivos GraphQL e geração de documentação Markdown integrada com os schemas existentes no sistema Omni Keywords Finder.

---

## 📋 **ESTRUTURA DE DOCUMENTAÇÃO GRAPHQL**

### **Template para Schema GraphQL**

```markdown
## 🎯 **SCHEMA: {nome_do_schema}**

### **Metadados do Schema**
- **Arquivo**: `{caminho_completo}`
- **Última Atualização**: {data_hora}
- **Versão**: {versão_do_schema}
- **Tipo**: {Query/Mutation/Subscription}
- **Complexidade**: {baixa/média/alta}
- **Autenticação**: {requerida/opcional/não_requerida}

### **Descrição**
{descrição_detalhada_do_schema}

### **Tipos Definidos**

#### **{NomeDoTipo}**
```graphql
type NomeDoTipo {
  campo1: Tipo1!
  campo2: Tipo2
  campo3: [Tipo3]
}
```

**Descrição**: {descrição_do_tipo}

**Campos**:
- **campo1** (`Tipo1!`): {descrição_do_campo} (Obrigatório)
- **campo2** (`Tipo2`): {descrição_do_campo} (Opcional)
- **campo3** (`[Tipo3]`): {descrição_do_campo} (Lista)

**Resolvers**:
- `resolver1`: {descrição_do_resolver}
- `resolver2`: {descrição_do_resolver}

### **Queries Disponíveis**

#### **queryName**
```graphql
query queryName($param1: Tipo1!, $param2: Tipo2) {
  campo1
  campo2 {
    subcampo1
    subcampo2
  }
}
```

**Parâmetros**:
- `param1` (`Tipo1!`): {descrição_do_parâmetro} (Obrigatório)
- `param2` (`Tipo2`): {descrição_do_parâmetro} (Opcional)

**Retorno**: `TipoRetorno`

**Exemplo de Uso**:
```graphql
query GetKeywords($search: String!, $limit: Int) {
  keywords(search: $search, limit: $limit) {
    id
    term
    volume
    difficulty
  }
}
```

**Variáveis**:
```json
{
  "search": "digital marketing",
  "limit": 10
}
```

**Resposta**:
```json
{
  "data": {
    "keywords": [
      {
        "id": "1",
        "term": "digital marketing",
        "volume": 10000,
        "difficulty": 0.7
      }
    ]
  }
}
```

### **Mutations Disponíveis**

#### **mutationName**
```graphql
mutation mutationName($input: InputType!) {
  campo1
  campo2
}
```

**Input**:
```graphql
input InputType {
  campo1: Tipo1!
  campo2: Tipo2
}
```

**Retorno**: `MutationResult`

**Exemplo de Uso**:
```graphql
mutation CreateKeyword($input: CreateKeywordInput!) {
  createKeyword(input: $input) {
    id
    term
    createdAt
  }
}
```

**Variáveis**:
```json
{
  "input": {
    "term": "new keyword",
    "category": "marketing"
  }
}
```

### **Subscriptions Disponíveis**

#### **subscriptionName**
```graphql
subscription subscriptionName($filter: FilterType) {
  evento1
  evento2
}
```

**Filtros**:
- `filter` (`FilterType`): {descrição_do_filtro}

**Eventos**:
- `evento1`: {descrição_do_evento}
- `evento2`: {descrição_do_evento}

### **Autenticação e Autorização**

#### **Níveis de Acesso**
- **Público**: {queries/mutations_públicas}
- **Usuário**: {queries/mutations_para_usuários_autenticados}
- **Admin**: {queries/mutations_para_administradores}

#### **Tokens Necessários**
- **Bearer Token**: Para operações autenticadas
- **API Key**: Para operações de alta frequência
- **JWT**: Para operações de usuário

### **Rate Limiting**
- **Queries**: {limite_por_minuto}
- **Mutations**: {limite_por_minuto}
- **Subscriptions**: {limite_por_conexão}

### **Error Handling**

#### **Códigos de Erro**
- `UNAUTHENTICATED`: Usuário não autenticado
- `UNAUTHORIZED`: Usuário sem permissão
- `VALIDATION_ERROR`: Dados de entrada inválidos
- `NOT_FOUND`: Recurso não encontrado
- `INTERNAL_ERROR`: Erro interno do servidor

#### **Estrutura de Erro**
```json
{
  "errors": [
    {
      "message": "Descrição do erro",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": ["campo1"],
      "extensions": {
        "code": "ERROR_CODE",
        "details": "Detalhes adicionais"
      }
    }
  ]
}
```

### **Performance e Otimização**

#### **Dataloaders**
- `UserLoader`: Carregamento em lote de usuários
- `KeywordLoader`: Carregamento em lote de keywords
- `CategoryLoader`: Carregamento em lote de categorias

#### **Cache**
- **Query Cache**: 5 minutos para queries estáticas
- **Field Cache**: 1 minuto para campos computados
- **Result Cache**: 10 minutos para resultados complexos

### **Testes e Validação**

#### **Testes Unitários**
- `tests/graphql/test_queries.py`: Testes de queries
- `tests/graphql/test_mutations.py`: Testes de mutations
- `tests/graphql/test_subscriptions.py`: Testes de subscriptions

#### **Testes de Integração**
- `tests/integration/test_graphql_api.py`: Testes de integração
- `tests/integration/test_auth.py`: Testes de autenticação

#### **Validação de Schema**
```bash
# Validar schema
python -m graphql.validation.validate_schema

# Testar queries
python -m graphql.validation.test_queries
```

### **Monitoramento e Métricas**

#### **Métricas Coletadas**
- **Query Performance**: Tempo de execução por query
- **Error Rate**: Taxa de erro por operação
- **Usage Patterns**: Padrões de uso mais comuns
- **Cache Hit Rate**: Taxa de acerto do cache

#### **Alertas**
- **High Error Rate**: > 5% de erros
- **Slow Queries**: > 2000ms de execução
- **Cache Miss**: < 80% de hit rate

### **Versionamento e Evolução**

#### **Breaking Changes**
- **v1.0**: Schema inicial
- **v1.1**: Adicionado campo `createdAt` em Keyword
- **v2.0**: Removido campo `legacyField` (breaking change)

#### **Deprecation Policy**
- **Soft Deprecation**: Campo marcado como deprecated por 6 meses
- **Hard Deprecation**: Campo removido após 12 meses
- **Migration Guide**: Guia de migração para cada breaking change

---

## 🔍 **DETECÇÃO AUTOMÁTICA DE ARQUIVOS GRAPHQL**

### **Padrões de Arquivo**
```python
# Padrões para detecção automática
GRAPHQL_PATTERNS = [
    r'\.graphql$',
    r'\.gql$',
    r'_schema\.py$',
    r'graphql/.*\.py$',
    r'queries/.*\.graphql$',
    r'mutations/.*\.graphql$',
    r'subscriptions/.*\.graphql$'
]

# Arquivos específicos do projeto
PROJECT_GRAPHQL_FILES = [
    'app/queries/keywords.graphql',
    'app/queries/nichos.graphql',
    'backend/app/api/graphql_schema.py',
    'backend/app/api/resolvers.py'
]
```

### **Estrutura de Diretórios**
```
📁 app/
  📁 queries/
    📄 keywords.graphql
    📄 nichos.graphql
    📄 analytics.graphql
  📁 mutations/
    📄 create_keyword.graphql
    📄 update_keyword.graphql
  📁 subscriptions/
    📄 keyword_updates.graphql
📁 backend/
  📁 app/
    📁 api/
      📄 graphql_schema.py
      📄 resolvers.py
      📄 types.py
    📁 models/
      📄 keyword.py
      📄 nicho.py
```

### **Análise de Schema**
```python
# Exemplo de análise automática
def analyze_graphql_schema(file_path: str) -> Dict[str, Any]:
    """
    Analisa schema GraphQL e extrai informações
    
    Returns:
        Dicionário com informações do schema
    """
    return {
        'file_path': file_path,
        'types': extract_types(),
        'queries': extract_queries(),
        'mutations': extract_mutations(),
        'subscriptions': extract_subscriptions(),
        'complexity': calculate_complexity(),
        'auth_requirements': extract_auth_requirements()
    }
```

---

## 📊 **GERAÇÃO AUTOMÁTICA DE DOCUMENTAÇÃO**

### **Template de Geração**
```markdown
# 📋 **DOCUMENTAÇÃO GRAPHQL - {PROJECT_NAME}**

**Gerado automaticamente em**: {timestamp}
**Versão do Schema**: {schema_version}
**Total de Tipos**: {total_types}
**Total de Queries**: {total_queries}
**Total de Mutations**: {total_mutations}

## 📁 **Arquivos Analisados**
{lista_de_arquivos_analisados}

## 🎯 **Schemas Encontrados**
{lista_de_schemas_com_links}

## 📈 **Métricas de Complexidade**
- **Tipos Simples**: {count}
- **Tipos Complexos**: {count}
- **Queries Simples**: {count}
- **Queries Complexas**: {count}
- **Mutations Críticas**: {count}

## 🔗 **Links Úteis**
- **GraphQL Playground**: {url}
- **Schema Introspection**: {url}
- **Documentação da API**: {url}
- **Testes**: {url}
```

### **Integração com Schema Existente**
```python
# Exemplo de integração
def integrate_with_existing_schema():
    """
    Integra documentação com schema existente
    """
    # Carregar schema existente
    schema = load_graphql_schema()
    
    # Analisar tipos
    types = analyze_schema_types(schema)
    
    # Gerar documentação
    docs = generate_documentation(types)
    
    # Salvar documentação
    save_documentation(docs)
    
    # Atualizar índices
    update_documentation_index(docs)
```

---

## 🎯 **EXEMPLOS PRÁTICOS**

### **Exemplo 1: Schema de Keywords**
```graphql
# app/queries/keywords.graphql
type Keyword {
  id: ID!
  term: String!
  volume: Int
  difficulty: Float
  category: Category
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Category {
  id: ID!
  name: String!
  keywords: [Keyword!]!
}

type Query {
  keywords(search: String, limit: Int, category: String): [Keyword!]!
  keyword(id: ID!): Keyword
  categories: [Category!]!
}

type Mutation {
  createKeyword(input: CreateKeywordInput!): Keyword!
  updateKeyword(id: ID!, input: UpdateKeywordInput!): Keyword!
  deleteKeyword(id: ID!): Boolean!
}

input CreateKeywordInput {
  term: String!
  category: String
  volume: Int
  difficulty: Float
}

input UpdateKeywordInput {
  term: String
  category: String
  volume: Int
  difficulty: Float
}
```

### **Documentação Gerada**
```markdown
## 🎯 **SCHEMA: Keywords**

### **Metadados do Schema**
- **Arquivo**: `app/queries/keywords.graphql`
- **Última Atualização**: 2025-01-27 10:30:00
- **Versão**: 1.0
- **Tipo**: Query/Mutation
- **Complexidade**: Média
- **Autenticação**: Requerida para mutations

### **Tipos Definidos**

#### **Keyword**
```graphql
type Keyword {
  id: ID!
  term: String!
  volume: Int
  difficulty: Float
  category: Category
  createdAt: DateTime!
  updatedAt: DateTime!
}
```

**Descrição**: Representa uma palavra-chave com métricas de SEO

**Campos**:
- **id** (`ID!`): Identificador único da keyword (Obrigatório)
- **term** (`String!`): Termo da palavra-chave (Obrigatório)
- **volume** (`Int`): Volume de buscas mensal (Opcional)
- **difficulty** (`Float`): Dificuldade de rankeamento (Opcional)
- **category** (`Category`): Categoria da keyword (Opcional)
- **createdAt** (`DateTime!`): Data de criação (Obrigatório)
- **updatedAt** (`DateTime!`): Data de última atualização (Obrigatório)

### **Queries Disponíveis**

#### **keywords**
```graphql
query GetKeywords($search: String, $limit: Int, $category: String) {
  keywords(search: $search, limit: $limit, category: $category) {
    id
    term
    volume
    difficulty
    category {
      name
    }
  }
}
```

**Parâmetros**:
- `search` (`String`): Termo de busca (Opcional)
- `limit` (`Int`): Limite de resultados (Opcional)
- `category` (`String`): Filtro por categoria (Opcional)

**Retorno**: `[Keyword!]!`

### **Mutations Disponíveis**

#### **createKeyword**
```graphql
mutation CreateKeyword($input: CreateKeywordInput!) {
  createKeyword(input: $input) {
    id
    term
    createdAt
  }
}
```

**Input**:
```graphql
input CreateKeywordInput {
  term: String!
  category: String
  volume: Int
  difficulty: Float
}
```

**Retorno**: `Keyword!`
```

---

## 🔧 **INTEGRAÇÃO COM SISTEMA DE DOCUMENTAÇÃO**

### **Comandos de Geração**
```bash
# Gerar documentação para todos os schemas GraphQL
python -m shared.api_docs_generator --graphql --all

# Gerar documentação para schema específico
python -m shared.api_docs_generator --graphql --file app/queries/keywords.graphql

# Validar e gerar documentação
python -m shared.api_docs_generator --graphql --validate --generate
```

### **Integração com CI/CD**
```yaml
# .github/workflows/graphql-docs.yml
name: Generate GraphQL Documentation

on:
  push:
    paths:
      - '**/*.graphql'
      - '**/*_schema.py'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate GraphQL Docs
        run: |
          python -m shared.api_docs_generator --graphql --all
          python -m shared.api_docs_generator --validate
      - name: Commit Changes
        run: |
          git add docs/graphql_schema_docs.md
          git commit -m "Update GraphQL documentation"
          git push
```

### **Monitoramento de Mudanças**
```python
# Monitoramento automático de mudanças
def monitor_graphql_changes():
    """
    Monitora mudanças em arquivos GraphQL
    """
    graphql_files = find_graphql_files()
    
    for file_path in graphql_files:
        if has_changed(file_path):
            generate_documentation(file_path)
            notify_team(f"GraphQL schema updated: {file_path}")
```

---

## 📝 **CHECKLIST DE QUALIDADE**

### **Antes de Finalizar Documentação**
- [ ] Todos os tipos documentados
- [ ] Todas as queries documentadas
- [ ] Todas as mutations documentadas
- [ ] Exemplos de uso incluídos
- [ ] Códigos de erro documentados
- [ ] Autenticação documentada
- [ ] Performance documentada
- [ ] Testes referenciados

### **Validação Automática**
- [ ] Schema válido
- [ ] Tipos consistentes
- [ ] Resolvers implementados
- [ ] Testes passando
- [ ] Documentação atualizada

---

## 📚 **REFERÊNCIAS**

- **API Docs Generator**: `shared/api_docs_generator.py`
- **GraphQL Schema**: `app/queries/keywords.graphql`
- **Resolvers**: `backend/app/api/resolvers.py`
- **Testes**: `tests/graphql/`

---

*Documentação gerada automaticamente pelo sistema de documentação enterprise*  
*Última atualização: 2025-01-27 10:30:00* 