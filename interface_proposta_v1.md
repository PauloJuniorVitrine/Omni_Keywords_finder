# Proposta de Interface — Omni Keywords Finder (v1)

## 1. Layout Geral
- Dashboard com cards informativos, tabelas filtráveis, navegação lateral
- Header: botões de ação (upload, exportar, treinar modelo)
- Modo escuro/claro, responsivo, acessível (WCAG 2.1)

## 2. Interações e Feedbacks
- Botão "Upload Regras": fade-in, layer 2, modal de confirmação
- Loader animado em operações assíncronas
- Toasts/banners para feedback imediato
- Badges de status em logs e operações
- Tooltips explicativos em campos críticos

## 3. Transições e Estados
- Animações de entrada/saída (fade, slide)
- Loader persistente em operações longas
- Feedback visual para erros, timeouts, permissões
- Rollback visual em falhas críticas

## 4. Vinculação Técnica
- Hooks para endpoints: upload, exportação, logs, modelos
- Estado global sincronizado (React Context/Redux)
- Proteção de rotas e ações por role/token

## 5. Metadados de Prototipação
- Posição: header, sidebar, cards
- Layer: 1 (base), 2 (modais), 3 (feedbacks)
- Animações: fade-in, slide, badge pulse
- Delay: loaders (300ms), feedbacks (persistente até ação)

## 6. Microalívios Cognitivos
- Agrupamento progressivo de formulários
- Tooltips e microinterações em campos obrigatórios
- Etapas visuais para uploads/exportações

## 7. Benchmarking Visual
- Adotar badges e loaders (Stripe)
- Tabelas e navegação lateral (Supabase)
- Clareza e agrupamento (Notion)

## 8. Segurança Visual
- Modal de confirmação para ações críticas
- Feedback persistente para erros de permissão
- Loader e rollback para falhas de backend

## 9. Acessibilidade
- Labels ARIA, navegação por teclado, contraste alto
- Mensagens de erro legíveis e persistentes 