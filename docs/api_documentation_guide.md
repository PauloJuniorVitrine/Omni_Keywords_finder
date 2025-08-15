# 📚 Guia de Documentação de APIs - OpenAPI

**Tracing ID:** `API_DOCS_GUIDE_2025_001`  
**Data/Hora:** 2025-01-27 20:25:00 UTC  
**Versão:** 1.0  
**Status:** 🚀 IMPLEMENTAÇÃO  

---

## 🎯 **OBJETIVO**

Este guia estabelece padrões para documentação automática de endpoints da API usando especificação OpenAPI 3.0, garantindo consistência e qualidade na documentação.

---

## 📋 **ESTRUTURA OBRIGATÓRIA DE DOCUMENTAÇÃO**

### **Template Base para Endpoints**

```python
@bp.route('/endpoint', methods=['GET'])
@auth_required()
def nome_endpoint():
    """
    Descrição clara e concisa do que o endpoint faz.
    
    ---
    tags:
      - Nome do Grupo
    security:
      - Bearer: []
    parameters:
      - name: parametro
        in: query|path|header
        required: true|false
        schema:
          type: string|integer|boolean|array
        description: Descrição do parâmetro
    requestBody:
      required: true|false
      content:
        application/json:
          schema:
            type: object
            required:
              - campo_obrigatorio
            properties:
              campo_obrigatorio:
                type: string
                description: Descrição do campo
                minLength: 3
                maxLength: 100
              campo_opcional:
                type: integer
                description: Descrição do campo opcional
                minimum: 1
    responses:
      200:
        description: Sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                campo:
                  type: string
                  description: Descrição do campo de resposta
      400:
        description: Dados inválidos
        content:
          application/json:
            schema:
              type: object
              properties:
                erro:
                  type: string
                  description: Descrição do erro
      401:
        description: Não autorizado
      403:
        description: Acesso negado
      404:
        description: Recurso não encontrado
      409:
        description: Conflito
      500:
        description: Erro interno do servidor
    """
    # Implementação do endpoint
    pass
```

---

## 🏷️ **TAGS PADRÃO**

Use as seguintes tags para organizar endpoints:

- **Nichos** - Gerenciamento de nichos
- **Categorias** - Gerenciamento de categorias
- **Execuções** - Execução de prompts e coleta
- **Autenticação** - Login, logout, tokens
- **Usuários** - Gerenciamento de usuários
- **Analytics** - Métricas e relatórios
- **Webhooks** - Integrações externas
- **Templates** - Gerenciamento de templates
- **Notificações** - Sistema de notificações
- **Pagamentos** - Processamento de pagamentos

---

## 🔒 **SEGURANÇA**

### **Endpoints Públicos**
```yaml
security: []
```

### **Endpoints Autenticados**
```yaml
security:
  - Bearer: []
```

### **Endpoints com Roles Específicos**
```yaml
security:
  - Bearer: []
  - AdminRole: []
```

---

## 📝 **EXEMPLOS PRÁTICOS**

### **Exemplo 1: GET com Parâmetros de Query**

```python
@bp.route('/usuarios', methods=['GET'])
@auth_required()
def listar_usuarios():
    """
    Lista usuários com filtros opcionais.
    
    ---
    tags:
      - Usuários
    security:
      - Bearer: []
    parameters:
      - name: ativo
        in: query
        schema:
          type: boolean
        description: Filtrar por status ativo
      - name: role
        in: query
        schema:
          type: string
          enum: [admin, user, moderator]
        description: Filtrar por role
      - name: limit
        in: query
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 20
        description: Limite de resultados
    responses:
      200:
        description: Lista de usuários retornada com sucesso
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: ID do usuário
                  nome:
                    type: string
                    description: Nome completo
                  email:
                    type: string
                    format: email
                    description: Email do usuário
                  ativo:
                    type: boolean
                    description: Status do usuário
      401:
        description: Não autorizado
      403:
        description: Acesso negado
    """
```

### **Exemplo 2: POST com Request Body Complexo**

```python
@bp.route('/execucoes/lote', methods=['POST'])
@auth_required()
def executar_lote():
    """
    Executa múltiplas execuções em lote.
    
    ---
    tags:
      - Execuções
    security:
      - Bearer: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: array
            items:
              type: object
              required:
                - categoria_id
                - palavras_chave
              properties:
                categoria_id:
                  type: integer
                  description: ID da categoria
                  minimum: 1
                palavras_chave:
                  type: array
                  items:
                    type: string
                    minLength: 1
                    maxLength: 100
                  description: Lista de palavras-chave
                  minItems: 1
                cluster:
                  type: string
                  description: Cluster opcional
                  minLength: 1
                  maxLength: 255
                prioridade:
                  type: string
                  enum: [baixa, media, alta]
                  default: media
                  description: Prioridade da execução
    responses:
      200:
        description: Lote processado com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                id_lote:
                  type: string
                  description: ID único do lote
                total:
                  type: integer
                  description: Total de execuções
                status:
                  type: string
                  enum: [pendente, processando, concluido, erro]
                  description: Status do processamento
      400:
        description: Dados inválidos
        content:
          application/json:
            schema:
              type: object
              properties:
                erro:
                  type: string
                  description: Descrição do erro
                detalhes:
                  type: array
                  items:
                    type: object
                    properties:
                      indice:
                        type: integer
                        description: Índice do item com erro
                      erro:
                        type: string
                        description: Erro específico do item
      401:
        description: Não autorizado
      403:
        description: Acesso negado
    """
```

### **Exemplo 3: PUT com Path Parameters**

```python
@bp.route('/nichos/<int:nicho_id>', methods=['PUT'])
@auth_required()
def editar_nicho(nicho_id):
    """
    Edita um nicho existente.
    
    ---
    tags:
      - Nichos
    security:
      - Bearer: []
    parameters:
      - name: nicho_id
        in: path
        required: true
        schema:
          type: integer
          minimum: 1
        description: ID do nicho a ser editado
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - nome
            properties:
              nome:
                type: string
                description: Novo nome do nicho
                minLength: 3
                maxLength: 100
              descricao:
                type: string
                description: Descrição opcional
                maxLength: 500
              ativo:
                type: boolean
                description: Status do nicho
                default: true
    responses:
      200:
        description: Nicho editado com sucesso
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  description: ID do nicho
                nome:
                  type: string
                  description: Nome atualizado
                descricao:
                  type: string
                  description: Descrição atualizada
                ativo:
                  type: boolean
                  description: Status atualizado
                data_atualizacao:
                  type: string
                  format: date-time
                  description: Data da última atualização
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
      403:
        description: Acesso negado
      404:
        description: Nicho não encontrado
      409:
        description: Nome já existe
    """
```

---

## 🔧 **VALIDAÇÃO AUTOMÁTICA**

### **Executar Validação**

```bash
# Validação manual
python scripts/validate_documentation.py

# Validação com diretório específico
API_DIR=backend/app/api python scripts/validate_documentation.py

# Validação em CI/CD
python -m pytest tests/unit/backend/test_documentation.py -v
```

### **Códigos de Saída**

- **0**: Cobertura ≥ 90% (Sucesso)
- **1**: Cobertura 70-89% (Aviso)
- **2**: Cobertura < 70% (Falha)

---

## 📊 **MÉTRICAS DE QUALIDADE**

### **Cobertura Mínima**
- **Crítico**: < 70%
- **Atenção**: 70-89%
- **Adequado**: ≥ 90%

### **Elementos Obrigatórios**
- ✅ Descrição clara
- ✅ Tags apropriadas
- ✅ Security definido
- ✅ Responses documentados
- ✅ Schema de request/response

### **Elementos Recomendados**
- ✅ Exemplos de uso
- ✅ Validações (minLength, maxLength, etc.)
- ✅ Enum para valores fixos
- ✅ Format para tipos especiais (email, date-time)

---

## 🚀 **GERAÇÃO AUTOMÁTICA**

### **Swagger UI**

Acesse a documentação interativa em:
```
http://localhost:8000/api/docs/swagger
```

### **OpenAPI JSON**

Especificação completa em:
```
http://localhost:8000/api/docs/swagger.json
```

### **Geração de Clientes**

```bash
# Gerar cliente TypeScript
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/api/docs/swagger.json \
  -g typescript-fetch \
  -o ./generated/typescript-client

# Gerar cliente Python
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/api/docs/swagger.json \
  -g python \
  -o ./generated/python-client
```

---

## 🛠️ **FERRAMENTAS DE DESENVOLVIMENTO**

### **VS Code Extensions**
- **OpenAPI (Swagger) Editor**
- **REST Client**
- **Thunder Client**

### **CLI Tools**
- **openapi-generator-cli**
- **swagger-codegen**
- **spectral** (validação de regras)

---

## 📝 **CHECKLIST DE REVISÃO**

Antes de fazer commit, verifique:

- [ ] Endpoint tem docstring completa
- [ ] Tags estão corretas
- [ ] Security está definido
- [ ] Parameters estão documentados
- [ ] Request body tem schema
- [ ] Responses estão completos
- [ ] Códigos de erro estão cobertos
- [ ] Validações estão especificadas
- [ ] Exemplos estão claros
- [ ] Teste de documentação passa

---

## 🔄 **MANUTENÇÃO**

### **Atualizações Regulares**
- Revisar documentação a cada release
- Validar consistência com implementação
- Atualizar exemplos conforme necessário
- Verificar compatibilidade com clientes gerados

### **Versionamento**
- Manter compatibilidade backward
- Documentar breaking changes
- Usar versionamento semântico
- Manter changelog atualizado

---

**📞 Suporte:** Para dúvidas sobre documentação, consulte a equipe de desenvolvimento ou abra uma issue no repositório. 