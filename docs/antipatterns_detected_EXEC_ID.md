# Relatório de Antipadrões Detectados — EXEC_ID

## 1. Módulos Grandes
- `infrastructure/processamento/processador_keywords.py` (>600 linhas)
- `infrastructure/processamento/exportador_keywords.py` (>500 linhas)
- `infrastructure/processamento/clusterizador_semantico.py` (>400 linhas)

**Risco:** Baixa coesão, difícil manutenção, maior chance de bugs.

## 2. Arquivos de Backup/Versão
- `processador_keywords.py.bak_IMP002`
- `processador_keywords.py.bak_ENTERPRISE_AUDIT_v2`

**Risco:** Acúmulo técnico, confusão, risco de uso de versão desatualizada.

## 3. Sobreposição de Camadas
- Lógica de domínio presente em `infrastructure/processamento/`.

**Risco:** Viola o princípio de separação de responsabilidades (SRP, Clean Architecture).

## 4. Oportunidades de Modularização
- Handlers e processadores monolíticos podem ser divididos em módulos menores e reutilizáveis.

---

*Relatório gerado automaticamente. Atualize conforme novas evidências.* 