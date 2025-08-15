# 🚀 Sistema de Preenchimento de Lacunas em Prompts

## 📋 Visão Geral

Sistema automatizado para preenchimento de lacunas específicas em prompts base (arquivos TXT) com dados coletados (keywords e clusters), gerando prompts personalizados prontos para uso com IA generativa.

**Escopo:** 15 nichos × 7 categorias = 105 prompts únicos

## 🎯 Funcionalidades

### ✅ **Implementadas (Fase 1)**
- ✅ Modelos de dados (SQLAlchemy)
- ✅ Serviço de preenchimento automático
- ✅ APIs REST (FastAPI)
- ✅ Validação de dados (Pydantic)
- ✅ Sistema de logs
- ✅ Script de migração (Alembic)
- ✅ Script de teste

### 🔄 **Próximas Fases**
- 🔄 Interface web (React)
- 🔄 Upload de arquivos TXT
- 🔄 Processamento em lote
- 🔄 Dashboard de estatísticas
- 🔄 Cache Redis
- 🔄 Testes automatizados

## 🛠️ Instalação

### **1. Dependências**

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Dependências principais:
# - FastAPI >= 0.104.0
# - SQLAlchemy >= 2.0.0
# - Pydantic >= 2.5.0
# - Alembic >= 1.11.0
```

### **2. Configuração do Banco**

```bash
# Executar migrações
cd backend
alembic upgrade head

# Ou criar tabelas manualmente
python -c "
from app.models.prompt_system import Base
from sqlalchemy import create_engine
engine = create_engine('sqlite:///db.sqlite3')
Base.metadata.create_all(engine)
"
```

### **3. Executar Testes**

```bash
# Testar sistema completo
python test_prompt_system.py

# Executar servidor de desenvolvimento
uvicorn app.main:app --reload --port 8000
```

## 📊 Estrutura do Sistema

### **Modelos de Dados**

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Nichos    │◄───┤  Categorias  │◄───┤ Prompts Base │
└─────────────┘    └──────────────┘    └──────────────┘
       │                    │                    │
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│DadosColetados│───►│PromptPreenchido│◄───┤  LogOperacao │
└─────────────┘    └──────────────┘    └──────────────┘
```

### **Fluxo de Processamento**

```
1. Upload TXT → PromptBase
2. Coleta Dados → DadosColetados  
3. Processamento → PromptPreenchido
4. Logs → LogOperacao
```

## 🔧 Uso da API

### **1. Criar Nicho**

```bash
curl -X POST "http://localhost:8000/api/prompt-system/nichos" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Saúde e Bem-estar",
    "descricao": "Conteúdo sobre saúde, fitness e bem-estar"
  }'
```

### **2. Criar Categoria**

```bash
curl -X POST "http://localhost:8000/api/prompt-system/categorias" \
  -H "Content-Type: application/json" \
  -d '{
    "nicho_id": 1,
    "nome": "Emagrecimento",
    "descricao": "Dicas e estratégias para emagrecimento saudável"
  }'
```

### **3. Upload Prompt Base**

```bash
curl -X POST "http://localhost:8000/api/prompt-system/prompts-base" \
  -F "categoria_id=1" \
  -F "arquivo=@prompt_base.txt"
```

### **4. Criar Dados Coletados**

```bash
curl -X POST "http://localhost:8000/api/prompt-system/dados-coletados" \
  -H "Content-Type: application/json" \
  -d '{
    "nicho_id": 1,
    "categoria_id": 1,
    "primary_keyword": "como emagrecer 5kg em 30 dias",
    "secondary_keywords": "dieta low carb, exercícios para emagrecer",
    "cluster_content": "Guia completo para emagrecer 5kg em 30 dias"
  }'
```

### **5. Processar Preenchimento**

```bash
curl -X POST "http://localhost:8000/api/prompt-system/processar/1/1"
```

## 📝 Placeholders Suportados

O sistema detecta e substitui automaticamente os seguintes placeholders:

| Placeholder | Descrição | Obrigatório |
|-------------|-----------|-------------|
| `[PALAVRA-CHAVE PRINCIPAL DO CLUSTER]` | Keyword principal | ✅ |
| `[PALAVRAS-CHAVE SECUNDÁRIAS]` | Keywords secundárias | ❌ |
| `[CLUSTER DE CONTEÚDO]` | Conteúdo do cluster | ✅ |

## 🔍 Validações

### **Dados Coletados**
- ✅ Palavra-chave principal: 1-255 caracteres
- ✅ Cluster de conteúdo: 1-2000 caracteres  
- ✅ Palavras-chave secundárias: até 1000 caracteres
- ✅ Nicho e categoria devem existir
- ✅ Categoria deve pertencer ao nicho

### **Prompts Base**
- ✅ Arquivo deve ser TXT
- ✅ Conteúdo não pode estar vazio
- ✅ Hash único para versionamento
- ✅ Uma categoria = um prompt base

## 📈 Métricas e Logs

### **Logs de Operação**
- ✅ Criação/atualização de entidades
- ✅ Processamento de preenchimento
- ✅ Tempo de execução
- ✅ Status de sucesso/erro

### **Métricas Disponíveis**
- ✅ Tempo médio de processamento
- ✅ Taxa de sucesso
- ✅ Quantidade de prompts por nicho
- ✅ Lacunas detectadas vs preenchidas

## 🚨 Tratamento de Erros

### **Erros Comuns**
- ❌ Prompt base não encontrado
- ❌ Dados coletados inválidos
- ❌ Lacunas não detectadas
- ❌ Arquivo não é TXT

### **Fallbacks**
- ✅ Rollback automático em falhas
- ✅ Logs detalhados para debugging
- ✅ Validação antes do processamento
- ✅ Status de processamento rastreável

## 🔮 Próximos Passos

### **Fase 2 - Interface Web**
- [ ] Dashboard de gestão
- [ ] Upload drag & drop
- [ ] Preview de prompts
- [ ] Estatísticas visuais

### **Fase 3 - Otimizações**
- [ ] Cache Redis
- [ ] Processamento paralelo
- [ ] Validação em tempo real
- [ ] Backup automático

### **Fase 4 - Integrações**
- [ ] Webhooks para notificações
- [ ] API externa para coleta
- [ ] Export para diferentes formatos
- [ ] Integração com IA generativa

## 🧪 Testes

### **Executar Testes**

```bash
# Teste unitário
python test_prompt_system.py

# Teste de integração
pytest tests/integration/test_prompt_system.py

# Teste de performance
python -m pytest tests/load/test_prompt_system.py
```

### **Cobertura de Testes**
- ✅ Modelos de dados
- ✅ Serviço de preenchimento
- ✅ Validação de dados
- ✅ Detecção de lacunas
- ✅ Processamento completo

## 📞 Suporte

Para dúvidas ou problemas:

1. **Logs**: Verificar `logs/` para detalhes de erro
2. **Documentação**: Este README e docstrings no código
3. **Issues**: Criar issue no repositório
4. **Testes**: Executar `test_prompt_system.py` para validação

---

**Versão:** 1.0.0  
**Data:** 2024-12-27  
**Status:** ✅ Implementação Base Concluída 