# Validação de Cobertura de Interface — Omni Keywords Finder

| Ação/Endpoint                        | Entidade      | Status   | Feedback Visual |
|--------------------------------------|--------------|----------|-----------------|
| CRUD Usuários/Papéis/Permissões      | User/Role/Permission | Ausente  | Não aplicável   |
| Exportação CSV/JSON de Keywords      | Keyword      | Parcial  | Toast/Loader    |
| Logs de Governança                   | Log          | Coberto  | Badge/Toast     |
| Upload/Edição de Regras              | Rule         | Coberto  | Modal/Toast     |
| Simulação de Falhas de Integração    | Integração   | Ausente  | Não aplicável   |
| Drilldown em Cards do Dashboard      | Execução/Cluster | Parcial  | Loader/Badge    |
| Feedback visual para ações críticas  | Todas        | Coberto  | Toast/Modal     |
| Responsividade                       | Todas        | Parcial  | Não aplicável   |
| Acessibilidade                       | Todas        | Parcial  | Não aplicável   |

## Observações
- CRUD de administração e simulação de falhas ainda não possuem UI dedicada.
- Exportação CSV está disponível, mas não em todos os fluxos.
- Drilldown e responsividade precisam de ajustes para cobertura total.
- Feedback visual está presente em ações críticas, mas pode ser expandido.
- Acessibilidade e responsividade em evolução.

---

*Este relatório deve ser atualizado a cada release ou refatoração relevante.* 