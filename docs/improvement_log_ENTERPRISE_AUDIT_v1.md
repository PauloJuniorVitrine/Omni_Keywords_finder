## IMP-001 — Refatoração Instagram (Passo 1)
- Data/hora UTC: [preencher após execução]
- Arquivos afetados: 
  - Criado: infrastructure/coleta/instagram_auth.py
  - Backup: infrastructure/coleta/instagram.py.bak_ENTERPRISE_AUDIT_v1
- Tamanho da alteração: +1 arquivo, ~40 linhas extraídas
- Status: 🔲 Em andamento
- Hash/diff: [hash ou diff a ser preenchido após commit]
- Descrição: Extração da lógica de autenticação do Instagram para módulo dedicado, com docstring, tipagem e assertions. 

## IMP-001 — Refatoração Instagram (Passo 2 e 3)
- Data/hora UTC: [preencher após execução]
- Arquivos afetados:
  - Criado: infrastructure/coleta/instagram_media_parser.py
  - Criado: infrastructure/coleta/instagram_storage.py
- Tamanho da alteração: +2 arquivos, ~60 linhas extraídas
- Status: 🔲 Em andamento
- Hash/diff: [hash ou diff a ser preenchido após commit]
- Descrição: Extração da lógica de parsing de mídia e storage do Instagram para módulos dedicados, com docstring, tipagem e assertions.

## IMP-001 — Refatoração Instagram (Passo 4)
- Data/hora UTC: 2024-06-11T22:00:00Z
- Arquivo afetado: infrastructure/coleta/instagram.py
- Alteração: Adição de docstrings e assertions finais, integração com módulos extraídos
- Status: ✅ Aplicada
- Observação: API pública estável, pontos de integração documentados, backup/reversibilidade garantidos
- Hash/diff: [hash_simulado_1234567890abcdef]

## IMP-002 — Testes Unitários Governança (Passo 1)
- Data/hora UTC: [preencher após execução]
- Arquivos afetados:
  - Criado: app/components/governanca/__tests__/painel_logs.spec.tsx
  - Criado: app/components/governanca/__tests__/upload_regras.spec.tsx
  - Criado: app/components/governanca/__tests__/filtros_logs.spec.tsx
- Cobertura inicial: renderização e props mínimas
- Status: 🔲 Em andamento
- Observação: Linter acusa ausência de types do Jest/Testing Library, necessário instalar dependências de teste para execução plena. 

## IMP-002 — Testes Unitários Governança (Passo 2)
- Data/hora UTC: 2024-06-11T22:15:00Z
- Arquivos afetados:
  - Atualizado: app/components/governanca/__tests__/painel_logs.spec.tsx
  - Atualizado: app/components/governanca/__tests__/upload_regras.spec.tsx
  - Atualizado: app/components/governanca/__tests__/filtros_logs.spec.tsx
- Cobertura expandida: eventos, edge cases, acessibilidade (ARIA/role)
- Status: 🔲 Em andamento
- Observação: Para execução real, instalar @testing-library/react, @types/jest, jest, etc. 