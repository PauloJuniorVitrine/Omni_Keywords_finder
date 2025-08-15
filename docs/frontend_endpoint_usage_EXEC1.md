# Auditoria de Uso Real dos Endpoints REST no Frontend

| Endpoint                                | Uso Real no Frontend? | Localização/Componente                                 | Observações                                   |
|------------------------------------------|:---------------------:|--------------------------------------------------------|-----------------------------------------------|
| /api/execucoes/agendar                  |        ✅             | AgendarExecucao.tsx                                    | Agendamento de execuções                      |
| /api/execucoes/agendadas                |        ✅             | AgendarExecucao.tsx                                    | Listagem e cancelamento de execuções          |
| /api/execucoes/agendadas/{id}           |        ✅             | AgendarExecucao.tsx                                    | Cancelamento                                  |
| /api/categorias/1/                      |        ✅             | AgendarExecucao.tsx                                    | Listagem de categorias                        |
| /api/notificacoes                       |        ✅             | Notifications.tsx                                      | Listagem e PATCH                              |
| /governanca/regras/upload               |        ✅             | governanca/index.tsx                                   | Upload de regras                              |
| /governanca/logs                        |        ✅             | governanca/index.tsx, E2E                              | Consulta de logs                              |
| /processar_keywords                     |        ✅             | E2E, specs                                             | Testes E2E, specs                             |
| /exportar_keywords                      |        ✅             | E2E, specs                                             | Testes E2E, specs                             |

**Endpoints REST expostos, mas NÃO encontrados em uso direto no frontend:**

| Endpoint                                | Uso Real no Frontend? | Observações                                   |
|------------------------------------------|:---------------------:|-----------------------------------------------|
| /api/execucoes/lote                     |         ❌            | Usado apenas no backend/service layer         |
| /api/auth/login                         |         ❌            | Não encontrado em componentes, pode ser via SDK ou fluxo externo |
| /api/auth/logout                        |         ❌            | Idem acima                                    |
| /api/rbac/usuarios                      |         ❌            | Gestão administrativa, não exposto no dashboard padrão |
| /api/rbac/papeis                        |         ❌            | Idem acima                                    |
| /api/rbac/permissoes                    |         ❌            | Idem acima                                    |
| /api/nichos                             |         ❌            | Não encontrado em uso direto                  |
| /api/logs/execucoes                     |         ❌            | Não encontrado em uso direto                  |

**Resumo:**
- Todos os endpoints críticos para o fluxo de usuário estão em uso real no frontend.
- Endpoints administrativos não são consumidos diretamente pelo frontend padrão.
- Não há endpoints REST expostos sem uso funcional relevante no frontend principal. 