# MAPEAMENTO DE FLUXOS CRÍTICOS — CARGA LOCUST v1

| Endpoint                        | Método | Baseline | Threshold | Stress | Observações |
|---------------------------------|--------|----------|-----------|--------|-------------|
| /api/processar_keywords         | POST   | Sim      | Sim       | Sim    | Payload real, sem mocks |
| /api/exportar_keywords          | GET    | Sim      | Sim       | Sim    | Parâmetros reais |
| /api/governanca/logs            | GET    | Sim      | Sim       | Sim    | Header auth real |
| /api/governanca/regras/upload   | POST   | Sim      | Sim       | Sim    | Payload real, sem mocks |
| /api/governanca/regras/editar   | POST   | Sim      | Sim       | Sim    | Payload real, sem mocks |
| /api/governanca/regras/atual    | GET    | Sim      | Sim       | Sim    | |
| /api/externo/google_trends      | GET    | Sim      | Sim       | Sim    | Parâmetro termo real |
| /api/dashboard/metrics          | GET    | Sim      | Sim       | Sim    | |
| /api/test/reset                 | POST   | Sim      | Sim       | Sim    | |
| /api/test/timeout               | GET    | Sim      | Sim       | Sim    | |

**Todos os fluxos críticos REST estão cobertos por scripts Locust reais, sem uso de mocks ou dados sintéticos.**

- Scripts seguem padrão baseline, threshold e stress.
- Versionamento incremental (_v1).
- Documentação inline e nomes explícitos.
- Pronto para execução de carga real.

_Responsável: IA-Cursor_
_Data/Hora: [preencher na execução]_ 