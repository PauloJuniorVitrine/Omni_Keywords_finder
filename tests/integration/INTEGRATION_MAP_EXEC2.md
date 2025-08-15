# INTEGRATION MAP — EXEC2

## Mapeamento de Fluxos de Integração Reais

| Endpoint/Fluxo                        | Camadas Tocadas         | Dependências Reais         | Freq. Uso | RISK_SCORE | Teste Integração | Arquivo de Teste                              | Observações |
|----------------------------------------|-------------------------|----------------------------|-----------|------------|------------------|-----------------------------------------------|-------------|
| /api/execucoes/ (POST)                 | API, Service, DB, Log   | Banco, logs, notificação   | Alta      | 65         | Sim              | test_execucoes_integration.py                 | Ponta a ponta, sucesso/falha/edge |
| /api/execucoes/lote (POST)             | API, Service, DB, Log   | Banco, logs, notificação   | Alta      | 70         | Sim              | test_execucoes_lote_integration.py            | Paralelismo, idempotência, side effects |
| /api/execucoes/lote/status (GET)       | API, Service, FS, Log   | Banco, logs, arquivo       | Média     | 55         | Sim              | test_execucoes_lote_integration.py            | Progresso, leitura de log |
| /api/execucoes_agendadas/agendar (POST)| API, Service, DB, Log   | Banco, logs, notificação   | Média     | 60         | Sim              | test_execucoes_agendadas_integration.py       | Agendamento, fallback, erro |
| /api/execucoes_agendadas/agendadas (GET)| API, Service, DB, Log  | Banco, logs                | Média     | 55         | Sim              | test_execucoes_agendadas_integration.py       | Listagem, filtros |
| /api/payments/create (POST)            | API, Service, Log       | Banco, logs                | Baixa     | 40         | Sim              | test_payments_integration.py                  | Simulação, status |
| /api/payments/webhook (POST)           | API, Service, Security  | Banco, logs, HMAC, IP      | Média     | 65         | Sim              | test_payments_integration.py                  | Cobertura de assinatura e IP |
| /api/auth/oauth2/callback/<provider>   | API, Service, OAuth     | Banco, logs, OAuth2        | Média     | 60         | Sim              | test_oauth2_integration.py                    | Google, GitHub, erro |
| /api/rbac/usuarios (CRUD)              | API, Service, DB, Auth  | Banco, logs, JWT           | Média     | 60         | Sim              | test_rbac_integration.py                      | Permissões, roles, erros |
| /api/notificacoes (GET, POST)          | API, Service, DB, Log   | Banco, logs                | Média     | 50         | Sim              | test_notificacoes_integration.py              | Notificações, filtros |
| /api/categorias, /api/nichos, /api/clusters | API, Service, DB, Log| Banco, logs                | Média     | 45         | Sim              | test_categorias_nichos_clusters_integration.py| Listagem, filtros |
| /api/governanca/logs (GET)             | API, governança         | Banco, logs, auth          | Média     | 70         | Sim              | test_governanca.py                            | Logs, parâmetros inválidos |
| /api/governanca/regras/upload (POST)   | API, governança         | Banco, logs                | Média     | 65         | Sim              | test_governanca.py                            | JSON, multipart |
| /api/governanca/regras/editar (POST)   | API, governança         | Banco, logs                | Média     | 60         | Sim              | test_governanca.py                            | Sucesso, payload inválido |
| /api/governanca/regras/atual (GET)     | API, governança         | Banco, logs                | Média     | 60         | Sim              | test_governanca.py                            | Estrutura do retorno |
| /api/externo/google_trends (GET)       | API, Service, Externo   | Google Trends, logs        | Baixa     | 55         | Sim              | test_externo.py                               | Timeout, erro externo |
| /api/processar_keywords (POST)         | API, processamento      | Banco, logs                | Alta      | 80         | Sim              | test_keywords.py                              | Sucesso, erros, edge cases |
| /api/exportar_keywords (GET)           | API, exportação         | Banco, logs                | Média     | 75         | Sim              | test_export.py                                | JSON, CSV, formato inválido |
| /api/dashboard/metrics (GET)           | API, dashboard          | Banco, logs                | Média     | 70         | Sim              | test_dashboard_metrics.py                      | Estrutura, tipos, dados |
| /api/test/reset (POST)                 | API, reset              | Banco, logs                | Baixa     | 60         | Sim              | test_reset.py                                 | Reset funcional |
| /api/test/timeout (GET)                | API, timeout            | Delay, logs                | Baixa     | 50         | Sim              | test_timeout_integration.py                   | Timeout, fallback |
| Shadow/Canário                         | API, Service, DB        | Banco, logs, versões       | Média     | 60         | Sim              | test_shadow_canario_integration.py            | Comparação entre versões |

---

- **RISK_SCORE**: (Camadas * 10) + (Serviços * 15) + (Frequência * 5) — estimado conforme criticidade e dependências reais.
- **Gaps identificados:**
  - Falta teste real para `/api/execucoes/` (POST, GET, lote, status)
  - Falta teste para jobs agendados (`processar_execucoes_agendadas`)
  - Falta teste para side effects de lote e paralelismo
  - Falta shadow testing e comparação canário
  - Falta teste para `/api/test/timeout`

---

**Gerado automaticamente em {timestamp_utc} — EXEC_ID: EXEC2** 