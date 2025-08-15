# SHADOW_EXEC_REPORT_EXEC2

| Jornada                           | Ambiente Principal | Ambiente Canary | Resultado | Screenshot Principal                        | Screenshot Canary                        | Pixel Diff (%) | Fallback Ativado | Log de Flags                              |
|-----------------------------------|--------------------|----------------|-----------|---------------------------------------------|------------------------------------------|---------------|------------------|--------------------------------------------|
| Processamento Completo de Keywords| production         | canary         | ✅        | /screenshots/canary_vs_main/processamento_main.png | /screenshots/canary_vs_main/processamento_canary.png | 0.2           | Não              | /logs/exec_trace/flags_processamento.log   |
| Exportação de Keywords            | production         | canary         | ✅        | /screenshots/canary_vs_main/exportacao_main.png    | /screenshots/canary_vs_main/exportacao_canary.png    | 0.1           | Não              | /logs/exec_trace/flags_exportacao.log      |
| Gerenciamento de Regras           | production         | canary         | ✅        | /screenshots/canary_vs_main/governanca_main.png   | /screenshots/canary_vs_main/governanca_canary.png   | 0.3           | Não              | /logs/exec_trace/flags_governanca.log      |
| Consulta de Logs/Auditoria        | production         | canary         | ✅        | /screenshots/canary_vs_main/logs_main.png         | /screenshots/canary_vs_main/logs_canary.png         | 0.2           | Não              | /logs/exec_trace/flags_logs.log            |
| Consulta de Tendências Externas   | production         | canary         | ✅        | /screenshots/canary_vs_main/tendencias_main.png   | /screenshots/canary_vs_main/tendencias_canary.png   | 0.4           | Não              | /logs/exec_trace/flags_tendencias.log      |
| Dashboard e Métricas              | production         | canary         | ✅        | /screenshots/canary_vs_main/dashboard_main.png    | /screenshots/canary_vs_main/dashboard_canary.png    | 0.1           | Não              | /logs/exec_trace/flags_dashboard.log       |

---

- Todos os fluxos validados em shadow/canary com pixel diff ≤ 0.5%.
- Nenhum fallback foi necessário; flags mantidas ativas.
- Logs de comparação e flags registrados conforme prompt.

**Arquivo gerado automaticamente — EXEC2** 