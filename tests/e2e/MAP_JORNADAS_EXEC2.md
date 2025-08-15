# MAP_JORNADAS_EXEC2

## Jornadas E2E Críticas — Omni Keywords Finder (v2)

---

### Jornada 1: Processamento Completo de Keywords
- **Tipo:** Usuário autenticado (admin/analista)
- **Perfis envolvidos:** admin, analista
- **Passos:**
  1. Login
  2. Acesso à página de processamento
  3. Upload/entrada de lista de keywords
  4. Execução do processamento (pipeline: normalização, limpeza, validação, enriquecimento)
  5. Visualização do relatório/resultados
  6. Download/exportação dos resultados
- **Ramificações:** keywords inválidas, erro de processamento, timeout
- **Side effects:** logs, persistência, geração de arquivos

---

### Jornada 2: Exportação de Keywords
- **Tipo:** Usuário autenticado
- **Perfis envolvidos:** admin, analista
- **Passos:**
  1. Login
  2. Acesso à tela de exportação
  3. Seleção de formato (JSON/CSV)
  4. Download do arquivo
- **Ramificações:** formato inválido, arquivo vazio, erro de permissão

---

### Jornada 3: Gerenciamento de Regras de Governança
- **Tipo:** Admin
- **Perfis envolvidos:** admin
- **Passos:**
  1. Login
  2. Acesso à tela de regras
  3. Upload de nova blacklist/whitelist
  4. Edição de regras existentes
  5. Consulta de regras atuais
- **Ramificações:** upload inválido, regra duplicada, rollback

---

### Jornada 4: Consulta de Logs/Auditoria
- **Tipo:** Admin/analista
- **Perfis envolvidos:** admin, analista
- **Passos:**
  1. Login
  2. Acesso à tela de logs
  3. Filtro por evento/data
  4. Visualização de detalhes
- **Ramificações:** filtro sem resultado, erro de permissão

---

### Jornada 5: Consulta de Tendências Externas
- **Tipo:** Usuário autenticado
- **Perfis envolvidos:** admin, analista
- **Passos:**
  1. Login
  2. Acesso à tela de tendências
  3. Consulta de termo (Google Trends)
  4. Visualização dos resultados
- **Ramificações:** termo inválido, serviço externo indisponível

---

### Jornada 6: Dashboard e Métricas
- **Tipo:** Usuário autenticado
- **Perfis envolvidos:** admin, analista
- **Passos:**
  1. Login
  2. Acesso ao dashboard
  3. Visualização de métricas agregadas
- **Ramificações:** erro de carregamento, dados inconsistentes

---

## Perfis Envolvidos
- Usuário autenticado (analista)
- Admin
- Anônimo (para rotas públicas, se houver)

---

**Arquivo gerado automaticamente — EXEC2**

# Mapeamento de Jornadas Reais para Testes E2E (EXEC2)

| Jornada                                 | Tipo                | Perfis Envolvidos         | Ramificações/Condições Especiais                | Passos Mínimos/Variações                  |
|-----------------------------------------|---------------------|---------------------------|-------------------------------------------------|-------------------------------------------|
| Processar Keywords                      | Processamento       | Usuário autenticado       | Payloads grandes, concorrência, erro de validação| Login → Upload payload → Processar → Validar resposta/erro |
| Exportar Keywords                       | Exportação          | Usuário autenticado       | Volume de dados, download parcial/total         | Login → Acessar exportação → Baixar arquivo → Validar conteúdo |
| Consultar Logs de Governança            | Consulta/Busca      | Admin, Usuário            | Filtros, autenticação, paginação                | Login → Acessar logs → Filtrar → Validar resultados |
| Upload de Regras de Governança          | Upload/Validação    | Admin                     | Arquivo inválido, validação de regras           | Login (admin) → Upload arquivo → Validar sucesso/erro |
| Simular Timeout                         | Robustez/Timeout    | Usuário, Anônimo          | Timeout, fallback, erro de rede                 | Acessar endpoint → Esperar resposta/timeout → Validar fallback |
| Reset de Ambiente                       | Reset/Isolamento    | Admin, Usuário            | Idempotência, ambiente limpo                    | Login → Reset ambiente → Validar estado inicial |
| Integração Google Trends                | Integração Externa  | Usuário                   | Falha externa, fallback local                   | Login → Consultar trends → Validar resposta/fallback |
| Execução de Prompt                      | Execução/Concorrência| Usuário autenticado      | Execução paralela, erro de prompt               | Login → Submeter prompt → Validar execução/erro |
| Execução em Lote                        | Execução em Massa   | Usuário autenticado       | Stress no banco, múltiplos prompts              | Login → Submeter lote → Validar execuções |
| Agendamento de Execuções                | Agendamento         | Usuário autenticado       | Tarefas concorrentes, workers                   | Login → Agendar execução → Validar agendamento |
| Listagem de Execuções Agendadas         | Consulta            | Usuário autenticado       | Consulta concorrente, paginação                 | Login → Listar agendadas → Validar lista |
| Criação de Usuário                      | Cadastro            | Admin                     | Dados inválidos, duplicidade, autenticação      | Login (admin) → Criar usuário → Validar sucesso/erro |
| Listagem de Usuários                    | Consulta            | Admin, Usuário            | Filtros, autenticação, paginação                | Login → Listar usuários → Validar lista |
| Pagamento                               | Pagamento           | Usuário autenticado       | Integração externa, erro de pagamento           | Login → Iniciar pagamento → Validar sucesso/erro |
| Webhook de Pagamento                    | Webhook/Eventos     | Sistema externo           | Concorrência, eventos duplicados                | Simular webhook → Validar processamento/log |

> Este documento é gerado automaticamente para rastreabilidade do ciclo E2E EXEC2. 