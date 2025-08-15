# INTEGRATION MAP — EXEC1

## Mapeamento de Fluxos de Integração Reais

| Endpoint/Fluxo                        | Camadas Tocadas         | Dependências Reais         | RISK_SCORE | Teste de Integração | Arquivo de Teste                      | Observações |
|----------------------------------------|-------------------------|----------------------------|------------|---------------------|---------------------------------------|-------------|
| /api/processar_keywords (POST)         | API, processamento      | Banco, logs                | 80         | Sim                | test_keywords.py                      | Sucesso, erros, edge cases |
| /api/exportar_keywords (GET)           | API, exportação         | Banco, logs                | 75         | Sim                | test_export.py                        | JSON, CSV, formato inválido |
| /api/governanca/logs (GET)             | API, governança         | Banco, logs, auth          | 85         | Sim                | test_governanca.py                    | Sucesso, parâmetros inválidos |
| /api/governanca/regras/upload (POST)   | API, governança         | Banco, logs                | 80         | Sim (JSON)         | test_governanca.py                    | Falta multipart/YAML |
| /api/governanca/regras/editar (POST)   | API, governança         | Banco, logs                | 75         | Sim                | test_governanca.py                    | Sucesso, payload inválido |
| /api/governanca/regras/atual (GET)     | API, governança         | Banco, logs                | 70         | Sim                | test_governanca.py                    | Estrutura do retorno |
| /api/test/reset (POST)                 | API, reset              | Banco, logs                | 60         | Sim                | test_reset.py                         | Reset funcional |
| /api/externo/google_trends (GET)       | API, integração externa | Google Trends, logs        | 90         | Sim                | test_externo.py                       | Sucesso, termo |
| /api/dashboard/metrics (GET)           | API, dashboard          | Banco, logs                | 70         | Sim                | test_dashboard_metrics.py              | Estrutura, tipos, dados |
| /api/test/timeout (GET)                | API, timeout            | Delay, logs                | 80         | Não                | —                                     | Gap: falta teste de timeout |
| /api/governanca/regras/upload (YAML)   | API, governança         | Banco, logs                | 80         | Não                | —                                     | Gap: upload multipart |
| Importação do app principal            | App                     | —                          | 30         | Sim                | test_import_app.py                    | Teste de importação básica |

---

- **RISK_SCORE**: (Camadas * 10) + (Serviços * 15) + (Frequência * 5) — estimado conforme criticidade e dependências reais.
- **Gaps identificados:**
  - Falta teste para `/api/test/timeout` (simulação de timeout real)
  - Falta teste para upload multipart/YAML em `/api/governanca/regras/upload`

---

**Gerado automaticamente em 2025-05-31T19:40Z — EXEC_ID: EXEC1** 