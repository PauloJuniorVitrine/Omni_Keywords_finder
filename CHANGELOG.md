# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2024-03-20

### Adicionado
- Sistema base de processamento de keywords
- API REST com FastAPI
- Interface web com React/TypeScript
- Pipeline de ML para análise semântica
- Cache distribuído com Redis
- Testes unitários, integração e E2E
- CI/CD com GitHub Actions
- Monitoramento com Prometheus
- Logs estruturados com OpenTelemetry

### Alterado
- Otimização de performance em processamento de keywords
- Refatoração da arquitetura para Clean Architecture
- Melhorias na interface do usuário
- Atualização de dependências

### Corrigido
- Bugs no processamento assíncrono
- Problemas de validação de dados
- Erros de cache em alta carga
- Falhas na interface mobile

## [0.9.0] - 2024-03-10

### Adicionado
- Autenticação OAuth2
- Rate limiting
- Circuit breakers
- Validação multi-camada

### Alterado
- Melhorias na estrutura de testes
- Otimização de queries
- Refatoração de componentes

### Corrigido
- Memory leaks
- Race conditions
- Problemas de concorrência

## [0.8.0] - 2024-03-01

### Adicionado
- Sistema de enriquecimento semântico
- Pipeline assíncrono de processamento
- Cache multi-camada

### Alterado
- Melhorias de escalabilidade
- Otimização de recursos
- Refatoração de serviços

### Corrigido
- Bugs em processamento em lote
- Problemas de performance
- Erros de validação

## [0.7.0] - 2024-02-20

### Adicionado
- Sistema de clustering
- Análise semântica
- Visualizações avançadas

### Alterado
- Melhorias na arquitetura
- Refatoração da UI
- Otimização de queries

### Corrigido
- Bugs de interface
- Problemas de performance
- Erros de validação

## [0.6.0] - 2024-02-10

### Adicionado
- Sistema base de keywords
- API REST inicial
- Testes unitários básicos
- CI inicial

### Alterado
- Estrutura do projeto
- Organização de código
- Documentação

### Corrigido
- Bugs iniciais
- Problemas de configuração
- Erros de build

## [v1] - 2024-06-13
### Nova feature
- Geração dos artefatos:
  - interface_diagnostico_v1.md
  - interface_proposta_v1.md
  - interface_fluxo_ux_v1.json
  - interface_benchmarking_comparativo_v1.md
- Diagnóstico completo, proposta de interface, benchmarking visual e rastreabilidade conforme CoCoT, ToT, CRISP.

## [v1.1.0] - 2024-05-27
### Adicionado
- Integração de pagamentos (Stripe/PayPal) com retries, fallback e logging estruturado
- Cliente REST para consumo de API externa com robustez e fallback
- Endpoints REST para pagamentos e consumo externo
- Testes unitários para todos os fluxos críticos (não executados)
- Documentação de integração com Prometheus/Sentry/OpenTelemetry
- Recomendações de segurança: segregação de tokens, HMAC, whitelist de IPs
- Diagrama de fluxo das integrações externas

## [ENTERPRISE_AUDIT_v2] - YYYY-MM-DD
### Alterações
- IMP-001: Ajuste de normalização de termos em `processador_keywords.py`.
- Docstrings atualizadas para explicitar restrições de caracteres.
- Testes unitários em `test_processador_keywords.py` revisados para refletir as novas regras.
- Todos os testes unitários passaram após ajustes.
- IMP-002: Adicionado teste edge para critério `min_palavras` em `ValidadorKeywords`.
- Cobertura de casos-limite: mínimo, abaixo, acima, hífens, pontuação e espaços extras.
- Todos os testes unitários passaram após inclusão do teste.
- IMP-003: Documentação aprimorada do parâmetro `paralelizar` em ProcessadorKeywords e ClusterizadorSemantico.
- Docstrings detalhadas, exemplos de uso e limitações incluídos em docs/explanation.md e código-fonte.
- IMP-004: Ampliada cobertura de teste para duplicidade em Categoria (Blog), cobrindo edge cases (case-insensitive, espaços, acentos).
- Teste unitário criado em tests/unit/blogs/test_categoria.py.
- Todos os testes unitários passaram após inclusão do teste.
- IMP-005: Validação uniforme de termos vazios em Keyword (None, vazio, só espaços) com ValueError padronizado.
- Teste unitário criado/ajustado em tests/unit/test_models.py.
- Todos os testes unitários passaram após ajuste.

## [2025-05-30] v1.1.0
- Correção dos testes dos handlers de processamento (Normalizador, Limpeza, Validação, Enriquecimento)
- Ajuste do retorno do ValidacaoHandler para desempacotamento correto
- Cobertura de edge/failure cases e entradas inválidas
- Todos os testes unitários passaram

## [Data: 2025-05-30]
### Correções
- Logger (shared/logger.py) agora aceita dicionários e strings, serializando dicionários para JSON e evitando erro de formatação.
- Clusterizador (infrastructure/processamento/clusterizador_semantico.py) garante retorno consistente de lista de objetos Cluster.
- Teste de benchmark (tests/unit/processamento/test_benchmark_performance.py) ajustado para iterar sobre resultado['clusters'].
- Todos os testes unitários de performance passaram sem erros de logger ou de acesso a atributos.

## [v1.2.0] - 2024-06-27
### Adicionado
- Componente GlobalSearchBar reutilizável com autocomplete, debounce e acessibilidade
- Componente AdvancedFilters reutilizável para nicho, categoria, status e data
- Integração incremental de busca global e filtros avançados nas páginas principais
- Testes unitários e de integração para busca global e filtros
- Feedback visual (Skeleton/Loader) durante busca/filtragem

### Alterado
- Documentação inline e exemplos de uso atualizados

## [v1.2.1] - 2025-05-31
### Adicionado
- Teste real de integração para timeout: tests/integration/api/test_timeout_integration.spec.py
- Teste real de integração para upload multipart/YAML: tests/integration/api/test_governanca_upload_yaml_integration.spec.py
- Fixture global api_url em tests/integration/conftest.py

## [vX.Y.Z] - YYYY-MM-DD
### Experiência do Usuário Aprimorada
- Integração incremental dos componentes OnboardingGuide (tutorial interativo), HelpCenter (central de ajuda/FAQ) e FeedbackModal (envio de feedback).
- Botões fixos para acesso rápido à ajuda e feedback em toda a aplicação.
- Onboarding exibido automaticamente no primeiro acesso, com persistência via localStorage.
- Exemplos de uso e instruções documentados no README.
- Testes unitários para todos os novos componentes, cobrindo renderização, navegação, acessibilidade e callbacks.
- Boas práticas de acessibilidade aplicadas: labels, roles, navegação por teclado, foco visível.

### Analytics e Telemetria
- Integração incremental do Plausible Analytics para coleta privativa de métricas de uso e eventos customizados.
- Hook useAnalyticsEvent para disparo de eventos em ações-chave (feedback, ajuda, onboarding, exportação).
- Script de analytics carregado automaticamente no frontend, com configuração de domínio.
- Documentação de uso, privacidade e exemplos no README.
- Boas práticas de anonimização e respeito à privacidade do usuário.

## [vRBAC-1] - 2024-06-13
### Adicionado
- Autenticação JWT (Flask-JWT-Extended)
- Endpoints de login/logout (/api/auth/login, /api/auth/logout)
- Integração inicial RBAC (seed de papéis e permissões)

## [vRBAC-2] - 2024-06-13
### Adicionado
- Endpoints REST para CRUD de usuários, papéis e permissões (/api/rbac/usuarios, /api/rbac/papeis, /api/rbac/permissoes)
- Integração do blueprint RBAC ao app principal

## [vRBAC-3] - 2024-06-13
### Adicionado
- Decorators @role_required e @permission_required em backend/app/utils/auth_utils.py
- Logging estruturado de tentativas de acesso negadas

## [vRBAC-4] - 2024-06-13
### Alterado
- Endpoints de usuários, papéis e permissões agora protegidos por @role_required (admin ou gestor)

## [vRBAC-5] - 2024-06-13
### Adicionado
- Testes unitários (tests/unit/app/test_rbac.py) para decorators RBAC e edge cases
- Testes de integração (tests/integration/app/test_rbac_integration.py) para endpoints RBAC

## [vRBAC-6] - 2024-06-13
### Validado
- Testes unitários e de integração RBAC aprovados
- Cobertura de edge/failure cases garantida
- Ambiente de testes 100% funcional

## [vRBAC-7] - 2024-06-13
### Atualizado
- Documentação OpenAPI, README, architecture.md e changelog revisados
- Logs de decisão e execução registrados
- Conformidade final do ciclo RBAC

## [v1.3.0] - 2024-06-27
### Adicionado
- ThemeProvider global para alternância de tema (light/dark/high-contrast) com persistência
- Tokens de cor e estrutura de temas em `ui/theme/theme_v1.ts`
- Botão ThemeToggle acessível com tooltip e integração incremental
- Testes unitários para ThemeProvider e ThemeToggle
- Feedback visual e acessibilidade aprimorados

### Alterado
- Integração incremental de dark mode e alto contraste em toda a aplicação
- Documentação inline e exemplos de uso atualizados

## [STEP-004] - 2024-06-27
### Adicionado
- Módulo `keyword_classification_rules_v1.py` para classificação customizável de palavras-chave em primárias e secundárias.
- Testes unitários para diferentes regras e cenários.
- Documentação e exemplos no README.

## [STEP-002] - 2024-06-27
### Adicionado
- Módulo `async_coletor_v1.py` para coleta assíncrona/paralela de palavras-chave.
- Módulo `cache_keywords_v1.py` para cache assíncrono de resultados de coleta.
- Testes unitários para ambos os módulos.
- Documentação e exemplos no README.

## [STEP-003] - 2024-06-27
### Adicionado
- Módulo `ranking_explain_v1.py` para explicabilidade do ranking de palavras-chave.
- Módulo `ranking_feedback_v1.py` para feedback do usuário e influência no ranking.
- Testes unitários para ambos os módulos.
- Documentação e exemplos no README.

## [STEP-005] - 2024-06-27
### Adicionado
- Módulo `keyword_gap_suggestion_v1.py` para sugestão automática de lacunas e validação semântica entre primárias e secundárias.
- Testes unitários para detecção de lacunas, sugestão e validação semântica.
- Documentação e exemplos no README.

## [STEP-006] - 2024-06-27
### Adicionado
- Módulo `export_templates_v1.py` para templates customizáveis e exportação incremental de arquivos CSV/TXT.
- Testes unitários para diferentes templates, incremental e edge cases.
- Documentação e exemplos no README.

## [STEP-008] - 2024-06-27
### Adicionado
- Módulo `export_integrity_notify_v1.py` para assinatura digital/hash (SHA-256) e notificações (email/webhook) de exportação.
- Testes unitários para geração/verificação de hash, simulação de notificações e edge cases.
- Documentação e exemplos no README.

## [STEP-009] - 2024-06-27
### Adicionado
- Dashboard de monitoramento (app/pages/dashboard/monitoramento_v1.tsx) para status de execuções, falhas, exportações e métricas em tempo real.
- API pública REST (backend/app/api/public_api_v1.py) para consulta de execuções, exportações e métricas, com autenticação por token.
- Testes unitários para endpoints públicos e dashboard.
- Documentação e exemplos no README.

## [STEP-010] - 2024-06-27
### Adicionado
- Utilitário de internacionalização (i18n) para frontend (app/i18n/i18n_v1.ts) com suporte a pt-BR e en-US.
- Módulo de limpeza automática de arquivos antigos (backend/app/services/cleanup_v1.py) com suporte a dry-run, filtro por tipo e dias.
- Testes unitários para tradução, fallback, limpeza real e dry-run.
- Documentação e exemplos no README.

## [STEP-011] - 2024-06-27
### Adicionado
- Módulo de processamento distribuído (backend/app/services/distributed_processing_v1.py) com tasks Celery para coleta, processamento e exportação.
- Utilitário de performance (backend/app/services/performance_utils_v1.py) para profiling e otimização de funções.
- Testes de carga/performance para execução paralela, profiling e edge cases.
- Documentação e exemplos no README.

---

## Notas

- Todas as datas estão em UTC
- Versões seguem SemVer
- Mudanças são categorizadas como:
  - Adicionado: novas features
  - Alterado: mudanças em features existentes
  - Corrigido: correções de bugs
  - Removido: features removidas
  - Depreciado: features marcadas para remoção
  - Segurança: correções de vulnerabilidades 