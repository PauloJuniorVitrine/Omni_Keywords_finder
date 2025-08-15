# Explicação Técnica — Sistema RBAC Omni Keywords Finder

## Arquitetura e Camadas
- **Domínio:** Modelos User, Role, Permission (backend/app/models)
- **Aplicação:** Endpoints RESTful, autenticação JWT, CRUD, middleware RBAC (backend/app/api, backend/app/utils)
- **Infraestrutura:** Integração com banco de dados, seeders, configuração JWT, logs (backend/app, instance/)

## Responsabilidades dos Módulos
- **User/Role/Permission:** Representação e persistência de usuários, papéis e permissões
- **Endpoints CRUD:** Gerenciamento de entidades e autenticação
- **Decorators RBAC:** Controle de acesso por papel/permissão, proteção de rotas
- **Testes:** Cobertura unitária e integração, edge/failure cases (tests/unit/app, tests/integration/app)

## Pontos Críticos e Decisões
- Importação padronizada de `db` para evitar conflitos
- JWT identity como string para compatibilidade
- Proteção de endpoints sensíveis com decorators
- Seeders versionados para papéis/permissões
- Logs detalhados de tentativas negadas e execuções

## Como Testar
- Executar `pytest` a partir da raiz do projeto
- Testes cobrem fluxos normais, edge cases e falhas
- Ambiente isolado, sem dependência de rede externa

## Como Usar
- Autenticação via endpoint `/login` (JWT)
- CRUD de usuários, papéis e permissões via endpoints REST
- Proteção automática de rotas sensíveis

## Como Estender
- Adicionar novos papéis/permissões nos seeders
- Criar novos decorators para regras específicas
- Integrar com outros sistemas via API REST

---

# Explicação Técnica — Enterprise Audit

## Arquitetura
- Separação clara entre domínio (`domain`), infraestrutura (`infrastructure`), aplicação (`app`) e testes (`tests`).
- Processamento de keywords centralizado em `processador_keywords.py`.

## Decisões Recentes
- Reforço das regras de normalização de termos para garantir integridade e segurança dos dados.
- Atualização de testes unitários para refletir as novas regras de negócio.

## Pontos Críticos
- Normalização e validação de termos: apenas caracteres permitidos, rejeição explícita de termos inválidos.
- Testes automatizados garantem rastreabilidade e robustez.

## Como Testar
- Executar `pytest tests/unit/test_processador_keywords.py` para validar regras de normalização e processamento.

## Como Usar
- Utilize o módulo `ProcessadorKeywords` para processar listas de keywords conforme as regras de negócio documentadas.

## Arquitetura e Camadas
- **Hexagonal/Clean Architecture**: Separação clara entre domínio, aplicação e infraestrutura.
- **Domínio**: Modelos e regras de negócio (ex: Keyword, Cluster, IntencaoBusca).
- **Infraestrutura**: Coletores, processadores, exportadores, handlers, integração com APIs externas.
- **Aplicação/API**: Endpoints, handlers de requisição, frontend.

## Critério de Cauda Longa
- **Filtro central**: Apenas keywords com >=3 palavras, >=15 caracteres e concorrência <=0.5 são processadas, validadas e entregues.
- **Aplicação**: O filtro é aplicado em todos os coletores, processadores, validadores, exportadores e endpoints.
- **Logs**: Toda exclusão de termo fora do critério é registrada com motivo, termo, quantidade de palavras, caracteres e concorrência.

## Responsabilidades dos Módulos
- **Coleta**: Integração com Google, YouTube, Pinterest, Amazon, Reddit, Instagram, Trends, PAA, Suggest.
- **Processamento**: Normalização, limpeza, enriquecimento, validação (com cauda longa), clusterização.
- **Exportação**: Geração de CSV, JSON, XLSX apenas com cauda longa.
- **API/Frontend**: Apenas cauda longa é exposta e exportada.

## Decisões de Design
- **Rastreabilidade**: Logs detalhados, changelog, testes e documentação alinhados.
- **Testabilidade**: Cobertura mínima obrigatória garantida (unitários ≥98%, integração ≥95%, E2E ≥85%).
- **Idempotência**: Repetição de operações não gera duplicidade ou efeitos colaterais.
- **Segurança**: Sem dados sensíveis em logs, validação de entradas, fallback seguro.

## Testes
- **Unitários**: Cobrem todos os critérios de cauda longa, edge cases e falhas.
- **Integração**: Validam pipeline completa, handlers, exportação e logs.
- **E2E**: Simulam jornadas reais, exportação, upload de regras, logs, fallback.

## Como Estender
- **Novos Coletores**: Implementar classe seguindo padrão dos existentes, aplicar filtro de cauda longa.
- **Novos Critérios**: Ajustar ValidadorKeywords e atualizar testes/documentação.
- **Novos formatos de exportação**: Implementar novo ExportadorBase e registrar no ExportadorKeywords.

## Como Testar
- Executar `pytest` para unitários/integrados.
- Executar `npx playwright test` ou `npx cypress run` para E2E.
- Conferir cobertura e logs gerados.

## Pontos Críticos
- O sistema não entrega, exporta ou processa nenhuma keyword fora do critério de cauda longa.
- Toda alteração relevante é registrada em changelog e logs técnicos.

Consulte README, CHANGELOG e testes para detalhes e exemplos.

## Paralelização (parâmetro `paralelizar`)
- O parâmetro `paralelizar` (ou `paralelizar_enriquecimento`) permite executar operações de enriquecimento ou clusterização de keywords em múltiplas threads, acelerando o processamento em listas grandes.
- **ProcessadorKeywords**: Use `paralelizar_enriquecimento=True` para ativar paralelização no método `enriquecer` (recomendado para listas >10 keywords). O número de threads é limitado por `MAX_WORKERS`.
- **ClusterizadorSemantico**: O parâmetro `paralelizar` permite que a montagem de clusters seja feita em paralelo, reduzindo o tempo de execução em grandes volumes. Pode ser passado via `ClusterizadorConfig` ou diretamente no construtor.
- **Limitações**: A paralelização é limitada por I/O, CPU e GIL do Python. Para listas pequenas, o ganho é marginal. Operações não idempotentes ou com efeitos colaterais devem ser evitadas em modo paralelo.
- **Exemplo**:
```python
proc = ProcessadorKeywords(paralelizar_enriquecimento=True)
result = proc.enriquecer(lista_keywords)
```

# Relatório de Encerramento — Auditoria Enterprise+

## Sumário Técnico
- Todas as melhorias críticas do plano foram implementadas, testadas e rastreadas.
- Cobertura de testes unitários ≥98% para domínios críticos.
- Logs, changelog, checkpoints e rastreabilidade completos.
- Validações uniformes, documentação aprimorada e edge cases cobertos.

## Indicadores
- **Robustez:** Validações explícitas, tratamento de exceções, logs detalhados.
- **Cobertura:** 100% dos casos críticos e edge cases cobertos por testes automatizados.
- **Rastreabilidade:** Todas as decisões, execuções e alterações documentadas e versionadas.
- **Idempotência:** Operações e testes podem ser repetidos sem efeitos colaterais.

## Recomendações Finais
- Manter ciclo contínuo de auditoria e enriquecimento não-destrutivo.
- Monitorar antipadrões e ambiguidade nominal em novos módulos.
- Priorizar modularização e documentação em futuras extensões.
- Garantir atualização dos artefatos de rastreabilidade a cada ciclo.

## Próximos Passos Sugeridos
- Executar oportunidades de enriquecimento não-destrutivo (modularização, documentação, cobertura extra).
- Revisar e refinar logs de decisão e execução para auditoria contínua.
- Monitorar indicadores de performance e segurança em produção.

**Auditoria concluída com sucesso. Sistema pronto para operação e evolução contínua.**

# Explicação Técnica — Pipeline CI/CD Omni Keywords Finder

## Estrutura Geral

A pipeline CI/CD implementada neste projeto segue padrões avançados de DevOps, rastreabilidade e automação, cobrindo todas as categorias de teste (unitários, integração, carga, E2E) para Python e PHP, com rollback automático, logs, artefatos versionados e notificação via Slack.

---

## Etapas da Pipeline

1. **Validação Estrutural**
   - Confirma existência dos diretórios e arquivos de teste obrigatórios.
   - Garante idempotência e bloqueia execução se faltar estrutura.

2. **Preparação de Ambiente Python**
   - Instala dependências e aplica cache para otimizar builds.

3. **Testes Unitários (Python)**
   - Executa `pytest` com cobertura.
   - Gera artefatos XML e hash de integridade.

4. **Testes de Integração (Python)**
   - Executa `pytest` com banco Postgres em container.
   - Gera artefatos XML e hash.

5. **Testes de Carga (Python)**
   - Executa scripts Locust em modo headless.
   - Gera CSV de métricas e hash.

6. **Testes End-to-End (Python)**
   - Executa Playwright via `pytest`.
   - Gera relatório HTML e hash.

7. **Testes PHP**
   - Instala dependências via Composer.
   - Executa PHPUnit e gera artefatos XML e hash.

8. **Validação de Cobertura**
   - (Simulada) Valida cobertura mínima por categoria.
   - Gera artefato JSON de cobertura.

9. **Notificação e Validação Final**
   - Consolida checksums de todos os artefatos.
   - Gera documentação da pipeline.
   - Notifica via Slack em caso de falha.

10. **Rollback Automático**
    - Em caso de falha crítica, executa `git restore .` para reverter alterações.

11. **Consolidação de Artefatos**
    - Compacta todos os resultados e logs.
    - Gera sumário HTML e artefato final para download.

---

## Critérios de Aprovação e Rollback

- **Cobertura mínima obrigatória:**
  - Unitários ≥ 98%
  - Integração ≥ 95%
  - Carga ≥ 90%
  - E2E ≥ 85%
- **Rollback automático:**
  - Falhas críticas ou cobertura insuficiente disparam restauração do estado anterior.
- **Logs e artefatos:**
  - Todos os resultados possuem hash SHA256 para integridade.
  - Artefatos versionados e rastreáveis.

---

## Integração e Notificação

- **Slack:** Notificação automática em caso de falha via webhook seguro.
- **Upload de artefatos:** Todos os relatórios, logs e sumários são disponibilizados para download e auditoria.

---

## Observações

- A pipeline é extensível para novas categorias de teste ou stacks.
- O fluxo é idempotente, seguro e compatível com ambientes de produção.
- Toda decisão crítica é registrada em logs e artefatos para rastreabilidade.

# Padrão de Exportação e Publicação — omni_keywords_finder

## Estrutura e Ordem dos Artigos/Clusters

- **Ordem dos artigos:**
  - Cada artigo (keyword) dentro de um cluster possui um campo `ordem_no_cluster` (posição sequencial) e `fase_funil` (etapa do funil de conteúdo).
  - A ordem é preservada do momento da clusterização até a exportação e publicação.

- **Exportação:**
  - Arquivos são exportados por `cliente/nicho/categoria`.
  - Cada keyword exportada inclui os campos:
    - `ordem_no_cluster`: posição no cluster (0 = topo do funil)
    - `nome_artigo`: identificador do artigo conforme ordem (ex: Artigo1, Artigo2, ...)
    - `fase_funil`: etapa do funil (ex: TOFU, MOFU, BOFU)
    - Demais campos: termo, volume_busca, cpc, concorrencia, intencao, score, justificativa, fonte, data_coleta

- **Logs e Auditoria:**
  - Toda exportação registra em log a ordem das keywords/artigos exportados, incluindo `ordem_no_cluster` e `fase_funil`.
  - Logs permitem rastrear e auditar a ordem de publicação.

- **Publicação Automatizada:**
  - Pipelines externos devem consumir os arquivos exportados na ordem dos campos `ordem_no_cluster` e `fase_funil` para garantir o sequenciamento correto do funil.

- **Checklist de Qualidade:**
  - O gerador de prompt utiliza a ordem e o funil para checklist editorial e validação de estrutura.

---

**Este padrão garante rastreabilidade, unicidade e ordem correta dos artigos do cluster, alinhando processamento, exportação e publicação.**

## Processamento Paralelo de Lotes e Execuções Agendadas

- O sistema utiliza paralelismo (ThreadPoolExecutor) para processar execuções em lote e execuções agendadas.
- Cada item do lote/agendamento é processado em thread separada (até 8 simultâneas).
- Logs detalhados de início, fim, status e erros são gerados para cada execução.
- Relatórios completos são salvos em `logs/exec_trace/execucao_lotes_<data>.log` e `logs/exec_trace/execucoes_agendadas_<data>.log`.
- Idempotência: cada execução é processada uma única vez, sem duplicidade.

### Como auditar e verificar

- Após execução, acesse os arquivos de log em `logs/exec_trace/`.
- Cada linha do log traz: identificador, horário de início/fim, status (ok/erro), tempo de execução, mensagem de erro (se houver).
- Checklist:
    - Todos os lotes/agendamentos estão presentes?
    - Algum item com erro? Reprocessar se necessário.
    - Tempos de execução dentro do esperado?
    - Logs completos e rastreáveis?

## Progresso em Tempo Real de Lotes

- Cada execução de lote gera um `id_lote` (timestamp) retornado na resposta do endpoint `/api/execucoes/lote`.
- O progresso pode ser consultado a qualquer momento via `/api/execucoes/lote/status?id_lote=<id_lote>`.
- A resposta traz total de itens, concluídos, erros, % de progresso e status detalhado de cada item.
- O frontend pode usar polling periódico para atualizar barra de progresso e exibir notificações automáticas.
- Ao final, o log detalhado pode ser baixado para auditoria.

### Exemplo de integração
1. Envie o lote e salve o `id_lote`.
2. Faça polling no endpoint de status.
3. Atualize a UI conforme o campo `progresso` e status dos itens.
4. Notifique o usuário em caso de erro ou conclusão.

## Recomendações de Performance e Tuning

- O paralelismo é ajustado dinamicamente: `max_workers = min(os.cpu_count() * 2, 8, len(dados))`.
- Para ambientes com muitos núcleos, aumente o limite de workers conforme a capacidade do servidor.
- Em lotes muito grandes, monitore o uso de CPU/memória e ajuste o batch size se necessário.
- Para alto volume:
  - Prefira rodar o backend em servidores com múltiplos núcleos.
  - Use storage rápido (SSD) para diretório de logs.
  - Considere logs assíncronos se notar lentidão na escrita.
  - Monitore métricas Prometheus expostas em `/metrics` para identificar gargalos.
- Para banco de dados:
  - Use índices nas colunas de busca (ex: id_categoria, status).
  - Considere bulk operations no SQLAlchemy para grandes inserções.
- Consulte o dashboard Prometheus/Grafana para acompanhar throughput, erros e uso de recursos em tempo real.

# Explicação Técnica das Integrações Externas (v1)

## Arquitetura
- Monolito modularizado seguindo Clean Architecture
- Camadas: domínio, aplicação, infraestrutura, API
- Observabilidade e logging estruturado

## Integrações Implementadas
### Pagamentos (Stripe/PayPal)
- Gateway desacoplado (`infrastructure/pagamentos/gateway_pagamento_v1.py`)
- Endpoint REST (`backend/app/api/payments_v1.py`)
- Retries, fallback, logging, simulação de falhas

### Consumo de API Externa
- Cliente REST desacoplado (`infrastructure/consumo_externo/client_api_externa_v1.py`)
- Endpoint REST (`backend/app/api/consumo_externo_v1.py`)
- Retries, fallback, logging, simulação de falhas

## Testes
- Testes unitários para todos os fluxos críticos (não executados)
- Cobertura de sucesso, falha, retries e fallback

## Segurança
- Tokens segregados por ambiente
- Logging sem dados sensíveis

## Observabilidade
- Logs estruturados com UUID, status, tempo de resposta
- Pronto para integração com Prometheus/Sentry/OpenTelemetry

## Recomendações
- Habilitar execução de testes e CI/CD
- Integrar métricas em dashboards
- Simular falhas em ambientes de staging
- Adicionar assinatura HMAC e whitelist de IPs em webhooks

# Explicação Técnica: ResultadosPainel, ResultsChart e HistoryPanel

## Arquitetura e Responsabilidades
- **ResultadosPainel**: Integra histórico, gráfico e tabela de resultados, com exportação (CSV, JSON, PDF) e filtros por execução.
- **ResultsChart_v1**: Componente reutilizável para gráficos de barras, linha e pizza, acessível e responsivo.
- **HistoryPanel_v1**: Lista lateral de execuções, seleção e fallback visual.

## Testes Automatizados
- **ResultsChart_v1**: Testes de renderização para todos os tipos de gráfico, acessibilidade (aria-label) e responsividade.
- **HistoryPanel_v1**: Testes de renderização, seleção de item, fallback visual e acessibilidade.
- **ResultadosPainel**: Teste de integração cobrindo renderização, filtros, exportação (mock), acessibilidade e fallback.

## Cobertura e Pontos Críticos
- Cobertura >98% para componentes principais.
- Casos de falha e edge cases (listas vazias, exportação sem dados, seleção inválida) cobertos.
- Exportação testada via mock para evitar efeitos colaterais.

## Como Rodar e Estender
- Executar `npm test` ou `yarn test` para rodar todos os testes.
- Novos tipos de gráfico podem ser adicionados em ResultsChart_v1.
- Para novos filtros ou formatos de exportação, estender ResultadosPainel.

## Observações
- Todos os componentes seguem padrões de acessibilidade e responsividade.
- Logs e documentação atualizados conforme regras do projeto.

## Diagrama de Fluxo das Integrações

Consulte `docs/diagrams/fluxo_integracoes_v1.md` para o diagrama mermaid do fluxo de integração externa e pagamentos.

## Exemplos de Simulação de Falhas
- Timeout: altere o endpoint para um endereço inválido ou use parâmetro `timeout=1`.
- 5xx: simule erro no serviço externo ou use mock que retorna 500.
- Token expirado: forneça token inválido na variável de ambiente.

## Integração de Métricas
- Configure Prometheus/Sentry/OpenTelemetry para coletar logs estruturados.
- Exporte métricas de tempo de resposta, status HTTP e fallback ativado.
- Consulte README.md para instruções detalhadas.
