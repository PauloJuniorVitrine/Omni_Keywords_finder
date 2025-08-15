# 🚀 **DOCUMENTAÇÃO PROTOBUF SCHEMA - ENTERPRISE**

**Tracing ID**: `PROTOBUF_SCHEMA_DOCS_20250127_001`  
**Data**: 2025-01-27  
**Versão**: 1.0  
**Status**: 🔧 **EM DESENVOLVIMENTO**

---

## 🎯 **OBJETIVO**
Gerar documentação automática para schemas Protobuf (.proto) com detecção automática, análise semântica e integração com o sistema de documentação enterprise.

---

## 📋 **ESTRUTURA DE DOCUMENTAÇÃO PROTOBUF**

### **Template para Schema Protobuf**

```markdown
## 🎯 **SCHEMA: {nome_do_schema}**

### **Metadados do Schema**
- **Arquivo**: `{caminho_completo}`
- **Última Atualização**: {data_hora}
- **Versão**: {versão_do_schema}
- **Sintaxe**: {proto2/proto3}
- **Namespace**: {namespace_do_schema}
- **Complexidade**: {baixa/média/alta}
- **Dependências**: {lista_de_dependências}

### **Descrição**
{descrição_detalhada_do_schema}

### **Mensagens Definidas**

#### **{NomeDaMensagem}**
```protobuf
message NomeDaMensagem {
  // Campo obrigatório
  string campo1 = 1;
  
  // Campo opcional
  optional int32 campo2 = 2;
  
  // Campo repetido
  repeated Tipo3 campo3 = 3;
  
  // Campo com valor padrão
  bool campo4 = 4 [default = true];
  
  // Campo com validação
  string campo5 = 5 [(validate.rules).string.min_len = 1];
}
```

**Descrição**: {descrição_da_mensagem}

**Campos**:
- **campo1** (`string`, tag: 1): {descrição_do_campo} (Obrigatório)
- **campo2** (`optional int32`, tag: 2): {descrição_do_campo} (Opcional)
- **campo3** (`repeated Tipo3`, tag: 3): {descrição_do_campo} (Lista)
- **campo4** (`bool`, tag: 4): {descrição_do_campo} (Padrão: true)
- **campo5** (`string`, tag: 5): {descrição_do_campo} (Validação: min_len=1)

**Validações**:
- Campo5: Mínimo 1 caractere
- Campo2: Deve ser positivo se presente

**Exemplo de Uso**:
```protobuf
// Exemplo de mensagem
NomeDaMensagem {
  campo1: "exemplo"
  campo2: 42
  campo3: [
    { subcampo: "item1" },
    { subcampo: "item2" }
  ]
  campo4: true
  campo5: "validado"
}
```

### **Enums Definidos**

#### **{NomeDoEnum}**
```protobuf
enum NomeDoEnum {
  // Valor padrão
  UNKNOWN = 0;
  
  // Valores específicos
  VALOR1 = 1;
  VALOR2 = 2;
  VALOR3 = 3;
}
```

**Descrição**: {descrição_do_enum}

**Valores**:
- `UNKNOWN` (0): Valor padrão/desconhecido
- `VALOR1` (1): {descrição_do_valor}
- `VALOR2` (2): {descrição_do_valor}
- `VALOR3` (3): {descrição_do_valor}

### **Serviços Definidos**

#### **{NomeDoServiço}**
```protobuf
service NomeDoServiço {
  // Método unário
  rpc MetodoUnario(RequestMessage) returns (ResponseMessage);
  
  // Método de streaming do servidor
  rpc MetodoStreamingServidor(RequestMessage) returns (stream ResponseMessage);
  
  // Método de streaming do cliente
  rpc MetodoStreamingCliente(stream RequestMessage) returns (ResponseMessage);
  
  // Método de streaming bidirecional
  rpc MetodoStreamingBidirecional(stream RequestMessage) returns (stream ResponseMessage);
}
```

**Descrição**: {descrição_do_serviço}

**Métodos**:
- **MetodoUnario**: {descrição_do_método}
  - **Request**: `RequestMessage`
  - **Response**: `ResponseMessage`
  - **Tipo**: Unário (request/response)

- **MetodoStreamingServidor**: {descrição_do_método}
  - **Request**: `RequestMessage`
  - **Response**: `stream ResponseMessage`
  - **Tipo**: Streaming do servidor

- **MetodoStreamingCliente**: {descrição_do_método}
  - **Request**: `stream RequestMessage`
  - **Response**: `ResponseMessage`
  - **Tipo**: Streaming do cliente

- **MetodoStreamingBidirecional**: {descrição_do_método}
  - **Request**: `stream RequestMessage`
  - **Response**: `stream ResponseMessage`
  - **Tipo**: Streaming bidirecional

### **Imports e Dependências**

#### **Imports**
```protobuf
syntax = "proto3";

package omni.keywords.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";
import "validate/validate.proto";
import "annotations/annotations.proto";
```

**Dependências Externas**:
- `google/protobuf/timestamp.proto`: Timestamps padrão
- `google/protobuf/empty.proto`: Mensagem vazia
- `validate/validate.proto`: Validações
- `annotations/annotations.proto`: Anotações HTTP

**Dependências Internas**:
- `common/types.proto`: Tipos comuns
- `models/keyword.proto`: Modelo de keyword

### **Validações e Constraints**

#### **Validações de Campo**
```protobuf
message ValidatedMessage {
  // String com validações
  string email = 1 [
    (validate.rules).string.email = true,
    (validate.rules).string.min_len = 5,
    (validate.rules).string.max_len = 100
  ];
  
  // Número com validações
  int32 age = 2 [
    (validate.rules).int32.gte = 0,
    (validate.rules).int32.lte = 150
  ];
  
  // Lista com validações
  repeated string tags = 3 [
    (validate.rules).repeated.min_items = 1,
    (validate.rules).repeated.max_items = 10
  ];
}
```

**Regras de Validação**:
- **email**: Deve ser email válido, 5-100 caracteres
- **age**: Deve estar entre 0 e 150
- **tags**: Deve ter 1-10 itens

### **Anotações HTTP (gRPC-Gateway)**

#### **Mapeamento REST**
```protobuf
service KeywordService {
  rpc GetKeyword(GetKeywordRequest) returns (Keyword) {
    option (google.api.http) = {
      get: "/v1/keywords/{id}"
    };
  }
  
  rpc CreateKeyword(CreateKeywordRequest) returns (Keyword) {
    option (google.api.http) = {
      post: "/v1/keywords"
      body: "*"
    };
  }
  
  rpc UpdateKeyword(UpdateKeywordRequest) returns (Keyword) {
    option (google.api.http) = {
      put: "/v1/keywords/{id}"
      body: "*"
    };
  }
  
  rpc DeleteKeyword(DeleteKeywordRequest) returns (google.protobuf.Empty) {
    option (google.api.http) = {
      delete: "/v1/keywords/{id}"
    };
  }
}
```

**Endpoints REST**:
- `GET /v1/keywords/{id}`: Buscar keyword por ID
- `POST /v1/keywords`: Criar nova keyword
- `PUT /v1/keywords/{id}`: Atualizar keyword
- `DELETE /v1/keywords/{id}`: Deletar keyword

### **Versionamento e Evolução**

#### **Política de Versionamento**
- **v1.0**: Schema inicial
- **v1.1**: Adicionado campo `created_at` (compatível)
- **v2.0**: Removido campo `legacy_field` (breaking change)

#### **Regras de Compatibilidade**
- **Campos Obrigatórios**: Nunca remover, apenas tornar opcional
- **Campos Opcionais**: Pode remover após 12 meses
- **Enums**: Pode adicionar valores, nunca remover
- **Serviços**: Pode adicionar métodos, nunca remover

#### **Migration Guide**
```markdown
## Migração v1.0 → v2.0

### Breaking Changes
- Removido campo `legacy_field` da mensagem `Keyword`
- Alterado tipo de `status` de `string` para `enum`

### Migração Automática
```python
def migrate_v1_to_v2(v1_message):
    v2_message = KeywordV2()
    v2_message.id = v1_message.id
    v2_message.term = v1_message.term
    # legacy_field removido
    v2_message.status = KeywordStatus.from_string(v1_message.status)
    return v2_message
```
```

### **Performance e Otimização**

#### **Tamanho de Mensagem**
- **Mensagem Pequena**: < 1KB
- **Mensagem Média**: 1KB - 10KB
- **Mensagem Grande**: > 10KB

#### **Otimizações Recomendadas**
- Usar `bytes` para dados binários
- Usar `repeated` com `packed=true` para números
- Evitar mensagens aninhadas profundas
- Usar `oneof` para campos mutuamente exclusivos

#### **Exemplo de Otimização**
```protobuf
// Antes (não otimizado)
message Keyword {
  repeated int32 volumes = 1;  // Não packed
  string large_text = 2;
}

// Depois (otimizado)
message Keyword {
  repeated int32 volumes = 1 [packed = true];  // Packed
  bytes large_text = 2;  // Bytes para texto grande
}
```

### **Testes e Validação**

#### **Testes Unitários**
```python
# tests/protobuf/test_keyword.py
def test_keyword_validation():
    """Testa validação de mensagem Keyword"""
    # Teste válido
    keyword = Keyword(
        id="1",
        term="test keyword",
        volume=1000
    )
    assert keyword.Validate() is None
    
    # Teste inválido
    invalid_keyword = Keyword(
        id="",  # ID vazio
        term="",  # Termo vazio
        volume=-1  # Volume negativo
    )
    with pytest.raises(ValidationError):
        invalid_keyword.Validate()
```

#### **Testes de Integração**
```python
# tests/integration/test_grpc_service.py
def test_keyword_service():
    """Testa serviço gRPC de keywords"""
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = KeywordServiceStub(channel)
        
        # Teste de criação
        request = CreateKeywordRequest(
            term="test keyword",
            volume=1000
        )
        response = stub.CreateKeyword(request)
        assert response.id is not None
        assert response.term == "test keyword"
```

### **Monitoramento e Métricas**

#### **Métricas Coletadas**
- **Tamanho de Mensagem**: Bytes por mensagem
- **Tempo de Serialização**: ms por operação
- **Tempo de Deserialização**: ms por operação
- **Taxa de Erro**: % de mensagens inválidas

#### **Alertas**
- **Large Messages**: > 100KB
- **Slow Serialization**: > 10ms
- **High Error Rate**: > 1%

---

## 🔍 **DETECÇÃO AUTOMÁTICA DE ARQUIVOS PROTOBUF**

### **Padrões de Arquivo**
```python
# Padrões para detecção automática
PROTOBUF_PATTERNS = [
    r'\.proto$',
    r'_pb\.py$',
    r'_grpc\.py$',
    r'protobuf/.*\.proto$',
    r'schemas/.*\.proto$',
    r'api/.*\.proto$'
]

# Arquivos específicos do projeto
PROJECT_PROTOBUF_FILES = [
    'api/proto/keyword.proto',
    'api/proto/nicho.proto',
    'api/proto/analytics.proto',
    'shared/protobuf/common.proto'
]
```

### **Estrutura de Diretórios**
```
📁 api/
  📁 proto/
    📄 keyword.proto
    📄 nicho.proto
    📄 analytics.proto
    📄 common.proto
  📁 generated/
    📄 keyword_pb2.py
    📄 keyword_pb2_grpc.py
    📄 nicho_pb2.py
    📄 nicho_pb2_grpc.py
📁 shared/
  📁 protobuf/
    📄 types.proto
    📄 errors.proto
📁 tests/
  📁 protobuf/
    📄 test_keyword.py
    📄 test_nicho.py
```

### **Análise de Schema**
```python
# Exemplo de análise automática
def analyze_protobuf_schema(file_path: str) -> Dict[str, Any]:
    """
    Analisa schema Protobuf e extrai informações
    
    Returns:
        Dicionário com informações do schema
    """
    return {
        'file_path': file_path,
        'syntax': extract_syntax(),
        'package': extract_package(),
        'messages': extract_messages(),
        'enums': extract_enums(),
        'services': extract_services(),
        'imports': extract_imports(),
        'validations': extract_validations()
    }
```

---

## 📊 **GERAÇÃO AUTOMÁTICA DE DOCUMENTAÇÃO**

### **Template de Geração**
```markdown
# 📋 **DOCUMENTAÇÃO PROTOBUF - {PROJECT_NAME}**

**Gerado automaticamente em**: {timestamp}
**Versão do Schema**: {schema_version}
**Total de Mensagens**: {total_messages}
**Total de Enums**: {total_enums}
**Total de Serviços**: {total_services}

## 📁 **Arquivos Analisados**
{lista_de_arquivos_analisados}

## 🎯 **Schemas Encontrados**
{lista_de_schemas_com_links}

## 📈 **Métricas de Complexidade**
- **Mensagens Simples**: {count}
- **Mensagens Complexas**: {count}
- **Serviços Unários**: {count}
- **Serviços Streaming**: {count}
- **Validações**: {count}

## 🔗 **Links Úteis**
- **Protobuf Compiler**: {url}
- **gRPC Documentation**: {url}
- **Generated Code**: {url}
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
    schema = load_protobuf_schema()
    
    # Analisar mensagens e serviços
    messages = analyze_schema_messages(schema)
    services = analyze_schema_services(schema)
    
    # Gerar documentação
    docs = generate_documentation(messages, services)
    
    # Salvar documentação
    save_documentation(docs)
    
    # Atualizar índices
    update_documentation_index(docs)
```

---

## 🎯 **EXEMPLOS PRÁTICOS**

### **Exemplo 1: Schema de Keywords**
```protobuf
// api/proto/keyword.proto
syntax = "proto3";

package omni.keywords.v1;

import "google/protobuf/timestamp.proto";
import "validate/validate.proto";

// Mensagem principal de keyword
message Keyword {
  string id = 1;
  string term = 2 [(validate.rules).string.min_len = 1];
  int32 volume = 3 [(validate.rules).int32.gte = 0];
  float difficulty = 4 [(validate.rules).float.gte = 0.0, (validate.rules).float.lte = 1.0];
  string category = 5;
  google.protobuf.Timestamp created_at = 6;
  google.protobuf.Timestamp updated_at = 7;
}

// Enum para status da keyword
enum KeywordStatus {
  UNKNOWN = 0;
  ACTIVE = 1;
  INACTIVE = 2;
  ARCHIVED = 3;
}

// Request para criar keyword
message CreateKeywordRequest {
  string term = 1 [(validate.rules).string.min_len = 1];
  int32 volume = 2 [(validate.rules).int32.gte = 0];
  float difficulty = 3 [(validate.rules).float.gte = 0.0, (validate.rules).float.lte = 1.0];
  string category = 4;
}

// Response para criar keyword
message CreateKeywordResponse {
  Keyword keyword = 1;
}

// Request para buscar keywords
message GetKeywordsRequest {
  string search = 1;
  int32 limit = 2 [(validate.rules).int32.gte = 1, (validate.rules).int32.lte = 100];
  string category = 3;
}

// Response para buscar keywords
message GetKeywordsResponse {
  repeated Keyword keywords = 1;
  int32 total_count = 2;
}

// Serviço de keywords
service KeywordService {
  rpc CreateKeyword(CreateKeywordRequest) returns (CreateKeywordResponse);
  rpc GetKeywords(GetKeywordsRequest) returns (GetKeywordsResponse);
  rpc GetKeyword(GetKeywordRequest) returns (Keyword);
  rpc UpdateKeyword(UpdateKeywordRequest) returns (Keyword);
  rpc DeleteKeyword(DeleteKeywordRequest) returns (google.protobuf.Empty);
}
```

### **Documentação Gerada**
```markdown
## 🎯 **SCHEMA: Keywords**

### **Metadados do Schema**
- **Arquivo**: `api/proto/keyword.proto`
- **Última Atualização**: 2025-01-27 10:30:00
- **Versão**: 1.0
- **Sintaxe**: proto3
- **Namespace**: omni.keywords.v1
- **Complexidade**: Média
- **Dependências**: google/protobuf/timestamp.proto, validate/validate.proto

### **Mensagens Definidas**

#### **Keyword**
```protobuf
message Keyword {
  string id = 1;
  string term = 2 [(validate.rules).string.min_len = 1];
  int32 volume = 3 [(validate.rules).int32.gte = 0];
  float difficulty = 4 [(validate.rules).float.gte = 0.0, (validate.rules).float.lte = 1.0];
  string category = 5;
  google.protobuf.Timestamp created_at = 6;
  google.protobuf.Timestamp updated_at = 7;
}
```

**Descrição**: Representa uma palavra-chave com métricas de SEO

**Campos**:
- **id** (`string`, tag: 1): Identificador único da keyword
- **term** (`string`, tag: 2): Termo da palavra-chave (Validação: min_len=1)
- **volume** (`int32`, tag: 3): Volume de buscas mensal (Validação: >= 0)
- **difficulty** (`float`, tag: 4): Dificuldade de rankeamento (Validação: 0.0-1.0)
- **category** (`string`, tag: 5): Categoria da keyword
- **created_at** (`google.protobuf.Timestamp`, tag: 6): Data de criação
- **updated_at** (`google.protobuf.Timestamp`, tag: 7): Data de última atualização

### **Enums Definidos**

#### **KeywordStatus**
```protobuf
enum KeywordStatus {
  UNKNOWN = 0;
  ACTIVE = 1;
  INACTIVE = 2;
  ARCHIVED = 3;
}
```

**Descrição**: Status da palavra-chave

**Valores**:
- `UNKNOWN` (0): Status desconhecido
- `ACTIVE` (1): Keyword ativa
- `INACTIVE` (2): Keyword inativa
- `ARCHIVED` (3): Keyword arquivada

### **Serviços Definidos**

#### **KeywordService**
```protobuf
service KeywordService {
  rpc CreateKeyword(CreateKeywordRequest) returns (CreateKeywordResponse);
  rpc GetKeywords(GetKeywordsRequest) returns (GetKeywordsResponse);
  rpc GetKeyword(GetKeywordRequest) returns (Keyword);
  rpc UpdateKeyword(UpdateKeywordRequest) returns (Keyword);
  rpc DeleteKeyword(DeleteKeywordRequest) returns (google.protobuf.Empty);
}
```

**Descrição**: Serviço para gerenciamento de keywords

**Métodos**:
- **CreateKeyword**: Cria uma nova keyword
- **GetKeywords**: Lista keywords com filtros
- **GetKeyword**: Busca keyword por ID
- **UpdateKeyword**: Atualiza keyword existente
- **DeleteKeyword**: Remove keyword
```

---

## 🔧 **INTEGRAÇÃO COM SISTEMA DE DOCUMENTAÇÃO**

### **Comandos de Geração**
```bash
# Gerar documentação para todos os schemas Protobuf
python -m shared.api_docs_generator --protobuf --all

# Gerar documentação para schema específico
python -m shared.api_docs_generator --protobuf --file api/proto/keyword.proto

# Validar e gerar documentação
python -m shared.api_docs_generator --protobuf --validate --generate
```

### **Integração com CI/CD**
```yaml
# .github/workflows/protobuf-docs.yml
name: Generate Protobuf Documentation

on:
  push:
    paths:
      - '**/*.proto'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate Protobuf Docs
        run: |
          python -m shared.api_docs_generator --protobuf --all
          python -m shared.api_docs_generator --validate
      - name: Commit Changes
        run: |
          git add docs/protobuf_schema_docs.md
          git commit -m "Update Protobuf documentation"
          git push
```

### **Monitoramento de Mudanças**
```python
# Monitoramento automático de mudanças
def monitor_protobuf_changes():
    """
    Monitora mudanças em arquivos Protobuf
    """
    protobuf_files = find_protobuf_files()
    
    for file_path in protobuf_files:
        if has_changed(file_path):
            generate_documentation(file_path)
            notify_team(f"Protobuf schema updated: {file_path}")
```

---

## 📝 **CHECKLIST DE QUALIDADE**

### **Antes de Finalizar Documentação**
- [ ] Todas as mensagens documentadas
- [ ] Todos os enums documentados
- [ ] Todos os serviços documentados
- [ ] Validações documentadas
- [ ] Exemplos de uso incluídos
- [ ] Versionamento documentado
- [ ] Performance documentada
- [ ] Testes referenciados

### **Validação Automática**
- [ ] Schema válido
- [ ] Tipos consistentes
- [ ] Validações implementadas
- [ ] Testes passando
- [ ] Documentação atualizada

---

## 📚 **REFERÊNCIAS**

- **API Docs Generator**: `shared/api_docs_generator.py`
- **Protobuf Schema**: `api/proto/keyword.proto`
- **Generated Code**: `api/generated/`
- **Testes**: `tests/protobuf/`

---

*Documentação gerada automaticamente pelo sistema de documentação enterprise*  
*Última atualização: 2025-01-27 10:30:00* 