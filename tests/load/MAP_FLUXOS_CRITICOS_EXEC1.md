# Mapeamento de Fluxos Críticos para Testes de Carga (EXEC1)

| Fluxo/Endpoint                        | Método | Tipo de Operação         | Justificativa de Criticidade                |
|---------------------------------------|--------|-------------------------|---------------------------------------------|
| /api/processar_keywords               | POST   | Processamento pesado     | Alta concorrência, payloads grandes         |
| /api/exportar_keywords                | GET    | Exportação de dados      | Volume de dados, uso frequente              |
| /api/governanca/logs                  | GET    | Busca filtrada/autenticação | Consulta intensiva, autenticação           |
| /api/governanca/regras/upload         | POST   | Upload de arquivos       | Escrita, validação de regras                |
| /api/test/timeout                     | GET    | Simulação de latência    | Teste de robustez sob timeout               |
| /api/test/reset                       | POST   | Reset de ambiente        | Isolamento e idempotência dos testes        |
| /externo/google_trends                | GET    | Integração externa       | Dependência de terceiros, fallback          |

> Este documento é gerado automaticamente para rastreabilidade do ciclo de carga. 