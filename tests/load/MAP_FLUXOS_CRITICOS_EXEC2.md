# Mapeamento de Fluxos Críticos para Testes de Carga (EXEC2)

| Fluxo/Endpoint                        | Método | Tipo de Operação         | Justificativa de Criticidade                |
|---------------------------------------|--------|-------------------------|---------------------------------------------|
| /api/processar_keywords               | POST   | Processamento pesado     | Alta concorrência, payloads grandes         |
| /api/exportar_keywords                | GET    | Exportação de dados      | Volume de dados, uso frequente              |
| /api/governanca/logs                  | GET    | Busca filtrada/autenticação | Consulta intensiva, autenticação           |
| /api/governanca/regras/upload         | POST   | Upload de arquivos       | Escrita, validação de regras                |
| /api/test/timeout                     | GET    | Simulação de latência    | Teste de robustez sob timeout               |
| /api/test/reset                       | POST   | Reset de ambiente        | Isolamento e idempotência dos testes        |
| /externo/google_trends                | GET    | Integração externa       | Dependência de terceiros, fallback          |
| /api/execucoes/                       | POST   | Execução de prompt       | Crítico para geração de resultados, concorrência |
| /api/execucoes/lote                   | POST   | Execução em lote         | Processamento massivo, stress no banco      |
| /api/execucoes/agendadas              | POST   | Agendamento de execuções | Tarefas concorrentes, workers               |
| /api/execucoes/agendadas              | GET    | Listagem de agendadas    | Consulta concorrente, stress de leitura     |
| /api/rbac/usuarios                    | POST   | Criação de usuário       | Autenticação, escrita crítica               |
| /api/rbac/usuarios                    | GET    | Listagem de usuários     | Consulta concorrente, autenticação          |
| /api/payments/                        | POST   | Pagamento                | Operação sensível, integração externa       |
| /api/payments/webhook                 | POST   | Webhook de pagamento     | Concorrência, eventos externos              |

> Este documento é gerado automaticamente para rastreabilidade do ciclo de carga EXEC2. 