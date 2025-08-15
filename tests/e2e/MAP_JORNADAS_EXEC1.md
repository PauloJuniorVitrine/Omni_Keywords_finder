# MAP_JORNADAS_EXEC1

## Jornadas E2E Críticas — Omni Keywords Finder

---

### Jornada 1: Processamento Completo de Keywords
- **Tipo:** Usuário autenticado (admin/analista)
- **Passos:**
  1. Login (se aplicável)
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
- **Passos:**
  1. Login
  2. Acesso à tela de exportação
  3. Seleção de formato (JSON/CSV)
  4. Download do arquivo
- **Ramificações:** formato inválido, arquivo vazio, erro de permissão

---

### Jornada 3: Gerenciamento de Regras de Governança
- **Tipo:** Admin
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
- **Passos:**
  1. Login
  2. Acesso à tela de logs
  3. Filtro por evento/data
  4. Visualização de detalhes
- **Ramificações:** filtro sem resultado, erro de permissão

---

### Jornada 5: Consulta de Tendências Externas
- **Tipo:** Usuário autenticado
- **Passos:**
  1. Login
  2. Acesso à tela de tendências
  3. Consulta de termo (Google Trends)
  4. Visualização dos resultados
- **Ramificações:** termo inválido, serviço externo indisponível

---

### Jornada 6: Dashboard e Métricas
- **Tipo:** Usuário autenticado
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

**Arquivo gerado automaticamente — EXEC1** 