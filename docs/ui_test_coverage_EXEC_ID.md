# Cobertura de Testes Visuais e E2E — Omni Keywords Finder

## Cobertura Atual

| Fluxo/Teste                        | Tipo         | Status   | Observações                |
|------------------------------------|--------------|----------|----------------------------|
| CRUD Usuários/Papéis/Permissões    | E2E          | Ausente  | UI não implementada        |
| Exportação CSV/JSON de Keywords    | E2E/Visual   | Parcial  | Cobertura parcial          |
| Logs de Governança                 | E2E/Visual   | Coberto  | Feedback visual validado   |
| Upload/Edição de Regras            | E2E/Visual   | Coberto  | Testes de erro/sucesso     |
| Simulação de Falhas de Integração  | E2E/Visual   | Ausente  | UI não implementada        |
| Drilldown em Cards do Dashboard    | E2E/Visual   | Parcial  | Cobertura parcial          |
| Feedback visual para ações críticas| Visual       | Coberto  | Toasts, modais, loaders    |
| Responsividade                     | Visual/E2E   | Parcial  | Testes em progresso        |
| Acessibilidade                     | Visual/E2E   | Parcial  | Testes em progresso        |

## Gaps Identificados
- Falta de testes E2E para CRUD de administração e simulação de falhas.
- Exportação, drilldown, responsividade e acessibilidade com cobertura parcial.
- Necessidade de snapshots visuais para todos os estados críticos.

## Recomendações
- Implementar testes E2E para fluxos ausentes.
- Expandir testes de responsividade e acessibilidade.
- Automatizar geração e validação de snapshots visuais.
- Revisar cobertura a cada release.

---

*Este relatório deve ser atualizado a cada ciclo de testes ou refatoração relevante.* 