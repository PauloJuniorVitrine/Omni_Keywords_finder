# Plano de Melhorias Técnicas — Enterprise Audit v2

## 1. Melhorias Críticas e Desalinhamentos Semânticos

| ID      | Descrição                                                                 | Módulo/Diretório                        | Gravidade | Impacto      | Camada         | IMPACT_SCORE | Score Antes/Depois | Logs Reais | Status |
|---------|--------------------------------------------------------------------------|-----------------------------------------|-----------|--------------|----------------|--------------|--------------------|------------|--------|
| IMP-001 | Ajustar docstring/lógica de `normalizar` para restrição de caracteres    | infrastructure/processamento            | Média     | Técnico      | Infraestrutura | 82           | 78 / 90            | Não        | 🔲     |
| IMP-002 | Adicionar teste edge para critério `min_palavras` em ValidadorKeywords   | infrastructure/processamento            | Média     | Funcional    | Infraestrutura | 75           | 80 / 92            | Não        | 🔲     |
| IMP-003 | Atualizar documentação de uso do parâmetro `paralelizar`                | infrastructure/processamento            | Baixa     | Técnico      | Infraestrutura | 60           | 85 / 90            | Não        | 🔲     |
| IMP-004 | Ampliar cobertura de teste para duplicidade em Categoria                | domain/models.py                        | Média     | Funcional    | Domínio        | 70           | 80 / 93            | Não        | 🔲     |
| IMP-005 | Uniformizar validação de termos vazios em Keyword                       | domain/models.py                        | Média     | Técnico      | Domínio        | 68           | 82 / 94            | Não        | 🔲     |

---

## 2. Oportunidades de Enriquecimento Não-Destrutivo

| ENR-ID  | Descrição                                              | Módulo/Diretório                  | Valor Agregado         | Status |
|---------|--------------------------------------------------------|-----------------------------------|------------------------|--------|
| ENR-001 | Modularizar validação de entrada em usecases           | infrastructure/processamento/     | Reutilização           | 🔲     |
| ENR-002 | Documentar e expor interfaces dos componentes de governança | app/components/governanca/   | Extensibilidade         | 🔲     |
| ENR-003 | Adicionar assertions e docstrings em scripts de coleta | infrastructure/coleta/            | Robustez, clareza      | 🔲     |
| ENR-004 | Gerar testes unitários para componentes de governança  | app/components/governanca/        | Cobertura, segurança   | 🔲     |

---

## 3. Antipadrões Detectados

| ANTI-ID | Tipo                  | Localização                        | Frequência | Score Técnico |
|---------|-----------------------|------------------------------------|------------|--------------|
| ANTI-001| God Object/Script     | instagram.py, reddit.py, etc.      | Alta       | 62           |
| ANTI-002| Placeholder não usado | vault_client.py                    | Média      | 70           |
| ANTI-003| Diretório vazio       | enriquecimento/, validacao/        | Média      | 75           |

---

## 4. Ambiguidade Nominal
- Monitorar termos como "handler", "processador", "validador" para evitar dispersão semântica futura.

---

## 5. Observações
- IMPACT_SCORE calculado conforme fórmula do prompt.
- Status inicial: 🔲 Pendente | ✅ Aplicada | 🔶 Pendente de Testes
- Todos os cálculos, scores e status rastreáveis.
- Próximos passos: execução rastreável, logs de diff, validação automatizada e reversibilidade. 