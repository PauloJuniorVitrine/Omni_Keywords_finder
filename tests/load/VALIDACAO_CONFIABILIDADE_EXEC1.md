# VALIDACAO_CONFIABILIDADE_EXEC1

## Relatório de Validação de Confiabilidade Sistêmica

| Fluxo                     | Nível      | Classificação         | Métricas fora da margem | Causa-raiz / Observação                  | Impacto em produção |
|---------------------------|------------|----------------------|------------------------|------------------------------------------|--------------------|
| /processar_keywords       | baseline   |                      |                        |                                          |                    |
| /processar_keywords       | threshold  |                      |                        |                                          |                    |
| /processar_keywords       | stress     |                      |                        |                                          |                    |
| /exportar_keywords        | baseline   |                      |                        |                                          |                    |
| /exportar_keywords        | threshold  |                      |                        |                                          |                    |
| /exportar_keywords        | stress     |                      |                        |                                          |                    |
| /governanca/logs          | baseline   |                      |                        |                                          |                    |
| /governanca/logs          | threshold  |                      |                        |                                          |                    |
| /governanca/logs          | stress     |                      |                        |                                          |                    |
| /governanca/regras/upload | baseline   |                      |                        |                                          |                    |
| /governanca/regras/upload | threshold  |                      |                        |                                          |                    |
| /governanca/regras/upload | stress     |                      |                        |                                          |                    |
| /governanca/regras/editar | baseline   |                      |                        |                                          |                    |
| /governanca/regras/editar | threshold  |                      |                        |                                          |                    |
| /governanca/regras/editar | stress     |                      |                        |                                          |                    |
| /externo/google_trends    | baseline   |                      |                        |                                          |                    |
| /externo/google_trends    | threshold  |                      |                        |                                          |                    |
| /externo/google_trends    | stress     |                      |                        |                                          |                    |
| /test/reset               | baseline   |                      |                        |                                          |                    |
| /test/reset               | threshold  |                      |                        |                                          |                    |
| /test/reset               | stress     |                      |                        |                                          |                    |

---

- Classificação: ✅ Totalmente confiável | ⚠️ Confiável com risco | ❌ Não confiável
- Detalhe causas de falhas, efeitos de regressão e impacto estimado em produção.
- Use este relatório para atestar formalmente a robustez do sistema sob carga. 