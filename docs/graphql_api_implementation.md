# GraphQL API Implementation - Omni Keywords Finder

## 📋 Visão Geral

Este documento descreve a implementação completa da API GraphQL para o sistema Omni Keywords Finder, complementar ao REST existente.

**Data de Implementação**: 2024-12-19  
**Versão**: 1.0.0  
**Status**: ✅ **IMPLEMENTADO**  

---

## 🎯 **Funcionalidades Implementadas**

### ✅ **1. Schema GraphQL Completo**
- **Arquivo**: `backend/app/api/graphql_schema.py`
- **Implementação**: Schema completo com tipos, queries, mutations e resolvers
- **Benefício**: API flexível e tipada

### ✅ **2. Endpoint GraphQL com Autenticação**
- **Arquivo**: `backend/app/api/graphql_endpoint.py`
- **Implementação**: Endpoint seguro com middleware de autenticação
- **Benefício**: Segurança e controle de acesso

### ✅ **3. Cliente GraphQL Frontend**
- **Arquivo**: `app/hooks/useGraphQL.ts`
- **Implementação**: Cliente otimizado com cache e deduplication
- **Benefício**: Performance e UX melhoradas

### ✅ **4. Componente de Exemplo**
- **Arquivo**: `app/components/shared/GraphQLExample.tsx`
- **Implementação**: Demonstração completa de uso
- **Benefício**: Facilita desenvolvimento e testes

---

## 🏗️ **Arquitetura do Sistema**

### **Backend (Python/Flask)**
```
backend/app/api/
├── graphql_schema.py      # Schema principal
├── graphql_endpoint.py    # Endpoints e middleware
└── requirements.txt       # Dependências GraphQL
```

### **Frontend (React/TypeScript)**
```
app/
├── hooks/
│   └── useGraphQL.ts      # Cliente GraphQL
└── components/shared/
    └── GraphQLExample.tsx # Componente de exemplo
```

---

## 📊 **Tipos GraphQL Implementados**

### **Tipos de Entidade**
```graphql
type Nicho {
  id: ID!
  nome: String!
  descricao: String
  ativo: Boolean!
  dataCriacao: DateTime!
  categorias: [Categoria!]!
}

type Categoria {
  id: ID!
  nome: String!
  descricao: String
  nichoId: ID!
  ativo: Boolean!
  nicho: Nicho!
}

type Execucao {
  id: ID!
  nichoId: ID!
  categoriaId: ID
  status: String!
  dataInicio: DateTime!
  dataFim: DateTime
  parametros: String
  resultado: String
  nicho: Nicho!
}

type Keyword {
  id: ID!
  keyword: String!
  volume: Int!
  dificuldade: Float!
  cpc: Float!
  categoria: String!
  nicho: String!
  dataColeta: DateTime!
  score: Float!
}

type Cluster {
  id: ID!
  nome: String!
  keywords: [Keyword!]!
  scoreMedio: Float!
  volumeTotal: Int!
  dataCriacao: DateTime!
}

type BusinessMetric {
  id: ID!
  nome: String!
  valor: Float!
  tipo: String!
  periodo: String!
  dataCalculo: DateTime!
  tendencia: String!
}
```

### **Inputs para Mutations**
```graphql
input NichoInput {
  nome: String!
  descricao: String
  ativo: Boolean
}

input CategoriaInput {
  nome: String!
  descricao: String
  nichoId: ID!
  ativo: Boolean
}

input ExecucaoInput {
  nichoId: ID!
  categoriaId: ID
  parametros: String
  agendada: Boolean
}

input KeywordFilterInput {
  nichoId: ID
  categoriaId: ID
  volumeMin: Int
  volumeMax: Int
  dificuldadeMin: Float
  dificuldadeMax: Float
  cpcMin: Float
  cpcMax: Float
  dataInicio: DateTime
  dataFim: DateTime
  limit: Int
  offset: Int
}
```

---

## 🔍 **Queries Implementadas**

### **Queries Básicas**
```graphql
# Buscar nichos
query GetNichos($ativo: Boolean) {
  nichos(ativo: $ativo) {
    id
    nome
    descricao
    ativo
    dataCriacao
    categorias {
      id
      nome
      descricao
      ativo
    }
  }
}

# Buscar nicho específico
query GetNicho($id: ID!) {
  nicho(id: $id) {
    id
    nome
    descricao
    ativo
    categorias {
      id
      nome
      ativo
    }
  }
}

# Buscar categorias
query GetCategorias($nichoId: ID, $ativo: Boolean) {
  categorias(nichoId: $nichoId, ativo: $ativo) {
    id
    nome
    descricao
    ativo
    nicho {
      id
      nome
    }
  }
}
```

### **Queries de Keywords**
```graphql
# Buscar keywords com filtros
query GetKeywords($filtros: KeywordFilterInput) {
  keywords(filtros: $filtros) {
    id
    keyword
    volume
    dificuldade
    cpc
    categoria
    nicho
    dataColeta
    score
  }
}

# Buscar keyword específica
query GetKeyword($id: ID!) {
  keyword(id: $id) {
    id
    keyword
    volume
    dificuldade
    cpc
    categoria
    nicho
    dataColeta
    score
  }
}
```

### **Queries de Execuções**
```graphql
# Buscar execuções
query GetExecucoes($nichoId: ID, $status: String, $limit: Int, $offset: Int) {
  execucoes(nichoId: $nichoId, status: $status, limit: $limit, offset: $offset) {
    id
    nichoId
    categoriaId
    status
    dataInicio
    dataFim
    parametros
    resultado
    nicho {
      id
      nome
    }
  }
}

# Buscar execuções agendadas
query GetExecucoesAgendadas($ativo: Boolean) {
  execucoesAgendadas(ativo: $ativo) {
    id
    nichoId
    categoriaId
    ativo
    proximaExecucao
    intervalo
    ultimaExecucao
  }
}
```

### **Queries de Métricas**
```graphql
# Buscar métricas de negócio
query GetBusinessMetrics($tipo: String, $periodo: String) {
  businessMetrics(tipo: $tipo, periodo: $periodo) {
    id
    nome
    valor
    tipo
    periodo
    dataCalculo
    tendencia
  }
}

# Buscar métricas de performance
query GetPerformanceMetrics($categoria: String, $ultimasHoras: Int) {
  performanceMetrics(categoria: $categoria, ultimasHoras: $ultimasHoras) {
    id
    nome
    valor
    unidade
    timestamp
    categoria
  }
}

# Estatísticas gerais
query GetEstatisticasGerais($periodo: String) {
  estatisticasGerais(periodo: $periodo)
}
```

---

## ✏️ **Mutations Implementadas**

### **Mutations de Nichos**
```graphql
# Criar nicho
mutation CreateNicho($input: NichoInput!) {
  createNicho(input: $input) {
    nicho {
      id
      nome
      descricao
      ativo
    }
    success
    message
  }
}

# Atualizar nicho
mutation UpdateNicho($id: ID!, $input: NichoInput!) {
  updateNicho(id: $id, input: $input) {
    nicho {
      id
      nome
      descricao
      ativo
    }
    success
    message
  }
}
```

### **Mutations de Execuções**
```graphql
# Criar execução
mutation CreateExecucao($input: ExecucaoInput!) {
  createExecucao(input: $input) {
    execucao {
      id
      nichoId
      status
      dataInicio
    }
    success
    message
  }
}
```

---

## 🎣 **Hooks Frontend Implementados**

### **Hooks de Query**
```typescript
// Hook genérico
const { data, loading, error, refetch } = useGraphQL(query, variables, options);

// Hooks especializados
const { data: nichos, loading, error } = useNichos(options);
const { data: keywords, loading, error } = useKeywords(filtros, options);
const { data: execucoes, loading, error } = useExecucoes(nichoId, options);
const { data: metrics, loading, error } = useBusinessMetrics(tipo, periodo, options);
```

### **Hooks de Mutation**
```typescript
// Hook genérico
const { execute, data, loading, error } = useGraphQLMutation(mutation);

// Hooks especializados
const { execute: createNicho, loading, error } = useCreateNicho();
const { execute: createExecucao, loading, error } = useCreateExecucao();
```

### **Hook de Subscription**
```typescript
const { data, loading, error } = useGraphQLSubscription(subscription, variables);
```

---

## 🔧 **Configurações e Opções**

### **Opções de Query**
```typescript
interface UseGraphQLOptions {
  skip?: boolean;                    // Pula a execução
  pollInterval?: number;             // Intervalo de polling (ms)
  errorPolicy?: 'none' | 'ignore' | 'all';  // Política de erro
  fetchPolicy?: 'cache-first' | 'cache-and-network' | 'network-only' | 'no-cache';  // Política de fetch
}
```

### **Configuração do Cliente**
```typescript
const config: GraphQLConfig = {
  endpoint: '/graphql/query',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  cacheTime: 5 * 60 * 1000,  // 5 minutos
  retryCount: 3,
  retryDelay: 1000,
};
```

---

## 🛡️ **Segurança e Autenticação**

### **Middleware de Autenticação**
- Verificação de token JWT
- Validação de usuário
- Controle de acesso por endpoint

### **Rate Limiting**
- Limitação de requisições por usuário
- Proteção contra abuso
- Configuração flexível

### **Logging e Auditoria**
- Log de todas as requisições GraphQL
- Rastreamento de performance
- Auditoria de segurança

---

## 📈 **Performance e Otimização**

### **Cache Inteligente**
- Cache em memória com TTL
- Deduplication de queries
- Invalidação automática

### **Query Optimization**
- Resolvers otimizados
- Lazy loading de relacionamentos
- Paginação eficiente

### **Error Handling**
- Retry automático com backoff
- Fallback para cache
- Error boundaries no frontend

---

## 🧪 **Testes e Validação**

### **Testes de Schema**
```python
# Teste de validação de schema
def test_schema_validation():
    schema = graphene.Schema(query=Query, mutation=Mutation)
    assert schema is not None
    assert hasattr(schema, 'introspect')
```

### **Testes de Resolvers**
```python
# Teste de resolver de nichos
def test_nichos_resolver():
    result = schema.execute('''
        query {
            nichos(ativo: true) {
                id
                nome
                ativo
            }
        }
    ''')
    assert result.data is not None
    assert 'nichos' in result.data
```

### **Testes de Frontend**
```typescript
// Teste de hook GraphQL
test('useNichos should fetch nichos', async () => {
  const { result } = renderHook(() => useNichos());
  
  await waitFor(() => {
    expect(result.current.loading).toBe(false);
  });
  
  expect(result.current.data).toBeDefined();
  expect(result.current.error).toBeNull();
});
```

---

## 📚 **Exemplos de Uso**

### **Exemplo 1: Buscar Nichos e Keywords**
```typescript
import { useNichos, useKeywords } from '../hooks/useGraphQL';

const MyComponent = () => {
  const { data: nichos, loading: nichosLoading } = useNichos();
  const { data: keywords, loading: keywordsLoading } = useKeywords(
    { nicho_id: selectedNicho, limit: 100 }
  );

  if (nichosLoading || keywordsLoading) {
    return <div>Carregando...</div>;
  }

  return (
    <div>
      <h2>Nichos</h2>
      {nichos?.nichos?.map(nicho => (
        <div key={nicho.id}>{nicho.nome}</div>
      ))}
      
      <h2>Keywords</h2>
      {keywords?.keywords?.map(keyword => (
        <div key={keyword.id}>{keyword.keyword}</div>
      ))}
    </div>
  );
};
```

### **Exemplo 2: Criar Nicho**
```typescript
import { useCreateNicho } from '../hooks/useGraphQL';

const CreateNichoForm = () => {
  const { execute: createNicho, loading, error } = useCreateNicho();
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const result = await createNicho({
        input: {
          nome,
          descricao,
          ativo: true,
        },
      });
      
      if (result.data?.createNicho?.success) {
        alert('Nicho criado com sucesso!');
        setNome('');
        setDescricao('');
      }
    } catch (error) {
      alert(`Erro: ${error}`);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={nome}
        onChange={(e) => setNome(e.target.value)}
        placeholder="Nome do nicho"
        required
      />
      <input
        value={descricao}
        onChange={(e) => setDescricao(e.target.value)}
        placeholder="Descrição"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Criando...' : 'Criar Nicho'}
      </button>
      {error && <div style={{ color: 'red' }}>{error.message}</div>}
    </form>
  );
};
```

---

## 🚀 **Endpoints Disponíveis**

### **Endpoints GraphQL**
- `POST /graphql/query` - Endpoint principal para queries e mutations
- `GET /graphql/schema` - Obter schema GraphQL
- `GET /graphql/health` - Health check
- `GET /graphql/playground` - GraphQL Playground (desenvolvimento)

### **Headers Necessários**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### **Exemplo de Requisição**
```bash
curl -X POST http://localhost:5000/graphql/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { nichos { id nome ativo } }"
  }'
```

---

## 📊 **Métricas e Monitoramento**

### **Métricas de Performance**
- Tempo de resposta das queries
- Taxa de cache hit/miss
- Número de requisições por minuto
- Erros por tipo

### **Logs Estruturados**
```json
{
  "timestamp": "2024-12-19T10:30:00Z",
  "level": "INFO",
  "module": "graphql",
  "message": "GraphQL Request: GetNichos",
  "data": {
    "execution_time": 0.125,
    "user_id": "123",
    "ip": "192.168.1.1",
    "query": "query GetNichos { ... }"
  }
}
```

---

## 🔄 **Integração com Sistema Existente**

### **Compatibilidade com REST**
- GraphQL complementa o REST existente
- Mesmos dados, diferentes interfaces
- Migração gradual possível

### **Reutilização de Serviços**
- Resolvers usam serviços existentes
- Cache compartilhado quando possível
- Autenticação unificada

---

## 🎯 **Benefícios Alcançados**

### **Para Desenvolvedores**
- ✅ Schema tipado e auto-documentado
- ✅ Queries flexíveis e eficientes
- ✅ Desenvolvimento mais rápido
- ✅ Menos over-fetching e under-fetching

### **Para Usuários**
- ✅ Interface mais responsiva
- ✅ Dados sempre atualizados
- ✅ Menor uso de banda
- ✅ Melhor experiência

### **Para Sistema**
- ✅ Performance otimizada
- ✅ Cache inteligente
- ✅ Monitoramento detalhado
- ✅ Escalabilidade melhorada

---

## ✅ **Checklist de Conclusão**

- [x] Schema GraphQL completo implementado
- [x] Endpoints seguros com autenticação
- [x] Cliente frontend otimizado
- [x] Cache inteligente e deduplication
- [x] Error handling robusto
- [x] Componente de exemplo criado
- [x] Documentação completa
- [x] Integração com sistema existente
- [x] Testes básicos implementados
- [x] Monitoramento e logs configurados

---

**Status**: ✅ **ITEM 13 COMPLETAMENTE IMPLEMENTADO**

A API GraphQL foi implementada com sucesso, fornecendo uma interface flexível e eficiente complementar ao REST existente, com todas as funcionalidades solicitadas e otimizações adicionais. 