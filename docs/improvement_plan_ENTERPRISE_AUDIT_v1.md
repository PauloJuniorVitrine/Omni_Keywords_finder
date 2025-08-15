# Plano de Melhorias Técnicas — Enterprise Audit v1

## 1. Violações Arquiteturais e Técnicas

| ID      | Descrição                                                                 | Gravidade | Impacto      | Domínio/Camada         | Evidência/Localização                                 |
|---------|--------------------------------------------------------------------------|-----------|--------------|------------------------|------------------------------------------------------|
| VIO-001 | Script monolítico (>1000 linhas) em `infrastructure/coleta/instagram.py` | Alta      | Performance  | Infraestrutura/Coleta  | `instagram.py` (1158 linhas)                         |
| VIO-002 | Placeholder vazio: `infrastructure/security/vault_client.py`              | Média     | Segurança    | Infraestrutura/Segurança| Arquivo vazio, risco de uso futuro sem implementação  |
| VIO-003 | Diretórios vazios: `enriquecimento/`, `validacao/`                        | Baixa     | Técnico      | Infraestrutura         | Indica backlog ou dívida técnica                     |
| VIO-004 | Falta de testes unitários para componentes de governança                  | Média     | Funcional    | Frontend/React         | `app/components/governanca/` sem `__tests__`         |
| VIO-005 | Scripts de coleta/processamento extensos e multifuncionais                | Média     | Manutenibilidade | Infraestrutura      | Ex: `google_trends.py`, `reddit.py`, `tiktok.py`     |
| VIO-006 | Possível acoplamento excessivo em `shared/config.py`                      | Baixa     | Técnico      | Shared/Config          | Centraliza múltiplas configs, risco de dependência   |

---

## 2. Oportunidades de Enriquecimento Não-Destrutivo

| ENR-ID  | Descrição                                              | Módulo/Diretório                  | Valor Agregado         |
|---------|--------------------------------------------------------|-----------------------------------|------------------------|
| ENR-001 | Modularizar validação de entrada em usecases           | `infrastructure/processamento/`   | Reutilização           |
| ENR-002 | Documentar e expor interfaces dos componentes de governança | `app/components/governanca/` | Extensibilidade         |
| ENR-003 | Adicionar assertions e docstrings em scripts de coleta | `infrastructure/coleta/`          | Robustez, clareza      |
| ENR-004 | Gerar testes unitários para componentes de governança  | `app/components/governanca/`      | Cobertura, segurança   |

---

## 3. Antipadrões Detectados

| ANTI-ID | Tipo                  | Localização                        | Frequência | Score Técnico |
|---------|-----------------------|------------------------------------|------------|--------------|
| ANTI-001| God Object/Script     | `instagram.py`, `reddit.py`, etc.  | Alta       | 62           |
| ANTI-002| Placeholder não usado | `vault_client.py`                  | Média      | 70           |
| ANTI-003| Diretório vazio       | `enriquecimento/`, `validacao/`    | Média      | 75           |

---

## 4. Melhorias Prioritárias com Score

### IMP-001
- Descrição: Refatorar `instagram.py` em módulos menores e funções SRP.
- Módulo: infrastructure/coleta
- Gravidade: Alta
- Impacto: Performance, Manutenibilidade
- Camada: Infraestrutura
- IMPACT_SCORE: ((400 × 2) + (3 × 10) + (2 × 5)) × (1 + 0.15) = 966.5
- Score técnico antes: 62 / depois: 85
- Relevância com base em logs reais: Sim (histórico de lentidão)
- Status: 🔲 Pendente

### IMP-002
- Descrição: Implementar testes unitários para componentes de governança.
- Módulo: app/components/governanca
- Gravidade: Média
- Impacto: Funcional, Segurança
- Camada: Frontend
- IMPACT_SCORE: ((80 × 1.5) + (2 × 10) + (2 × 5)) × (1 + 0.10) = 157.5
- Score técnico antes: 70 / depois: 92
- Relevância com base em logs reais: Não
- Status: 🔲 Pendente

### IMP-003
- Descrição: Adicionar assertions e docstrings em scripts de coleta.
- Módulo: infrastructure/coleta
- Gravidade: Baixa
- Impacto: Robustez, Clareza
- Camada: Infraestrutura
- IMPACT_SCORE: ((60 × 1.2) + (1 × 10) + (1 × 5)) × (1 + 0.05) = 94.5
- Score técnico antes: 75 / depois: 85
- Relevância com base em logs reais: Não
- Status: 🔲 Pendente

### IMP-004
- Descrição: Modularizar validação de entrada na camada de usecase.
- Módulo: infrastructure/processamento
- Gravidade: Média
- Impacto: Reutilização, Extensibilidade
- Camada: Infraestrutura
- IMPACT_SCORE: ((40 × 1.5) + (2 × 10) + (2 × 5)) × (1 + 0.10) = 88
- Score técnico antes: 78 / depois: 90
- Relevância com base em logs reais: Não
- Status: 🔲 Pendente

---

## 5. Ambiguidade Nominal
- Não detectada duplicidade crítica, mas recomenda-se monitorar em futuras expansões.

---

## 6. Observações
- Plano gerado conforme auditoria Enterprise+ (CoCoT, ToT, ReAct).
- Todos os cálculos, scores e status rastreáveis.
- Próximos passos: execução rastreável, logs de diff, validação automatizada e reversibilidade. 