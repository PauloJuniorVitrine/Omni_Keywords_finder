# Diagnóstico Completo — Omni Keywords Finder (v1)

## 1. Mapeamento Funcional
- Módulos: dashboard, governança, processamento, ML, logs
- Endpoints: /api/v1/keywords/extract, /api/v1/keywords, /api/v1/users, /api/v1/models
- Ações: CRUD, eventos, processamento, comunicação externa
- Funções: puras, assíncronas, sensíveis a permissão, mudas
- Estado: backend (Flask/FastAPI), frontend (React)

## 2. Entidades + Permissões
- Entidades: Keyword, User, Model, Regra de Governança, Log
- Permissões: Admin (total), User (restrito), Guest (visualização)
- Expressão visual: botões desabilitados, feedback imediato, rotas protegidas

## 3. Diagnóstico de UI/UX Atual
- Clareza: modular, navegação clara
- Estética: grids, cards, responsividade parcial
- Performance: backend assíncrono, cache
- Acessibilidade: WCAG 2.1 parcial
- Consistência: componentes reutilizáveis, duplicidade de feedbacks

## 4. Gaps Funcionais
- Falta de interface para fallback, logs detalhados
- Ausência de feedback para erros silenciosos
- Falta de loaders/microinterações em uploads/exportações
- Status persistente ausente em operações longas

## 5. Análise CoCoT (Exemplo)
| Elemento | Comprovação | Causalidade | Contexto | Tendência |
|----------|-------------|-------------|----------|-----------|
| Upload   | Código+E2E  | Ação crítica| Admin    | SaaS      |
| Loader   | Logs+UX     | Async       | Export   | Moderno   |
| Badge    | API+Logs    | Status      | Logs     | Notion    |

## 6. Árvore de Pensamento (ToT)
- T-UX-001: Governança
  - T-UX-002: Upload de regras
    - T-UX-003: Validação
      - T-UX-004: Feedback visual
    - T-UX-005: Confirmação
      - T-UX-006: Modal
  - T-UX-007: Logs
    - T-UX-008: Filtro
      - T-UX-009: Campo filtro

## 7. Comportamentos Dinâmicos
- WebSocket/polling: logs em tempo real
- Triggers: upload, exportação
- Loader, badge, animação

## 8. Segurança Visual
- Confirmação obrigatória para ações críticas
- Feedback imediato para falhas
- Rollback/bloqueio temporário

## 9. Matriz de Navegação
| Origem     | Ação           | Destino      |
|------------|----------------|--------------|
| /dashboard | Clicar em Card | /detalhe     |
| /governanca| Upload Regras  | /logs        |
| /logs      | Exportar       | /exportacao  |

## 10. Fricções Cognitivas
- Formulários extensos
- Falta de feedback em uploads
- Navegação ambígua
- Correções: agrupamento, microinterações, tooltips

## 11. Simulação de Fluxo Real
- Jornada: Upload → Validação → Confirmação → Logs
  - Erro: permissão (feedback)
  - Ausência: loader
  - Decisão ambígua: exportação sem confirmação

## 12. Falhas Críticas
- Timeout: loader + fallback
- Permissão: banner persistente
- Autenticação: redirecionamento + toast

## 13. Benchmarking Visual
- Stripe: feedbacks, loaders, badges
- Supabase: painel técnico, tabelas
- Notion: clareza, agrupamento
- Recomendações: badges, loaders, agrupamento, feedbacks persistentes 