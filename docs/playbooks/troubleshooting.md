# Playbook de Troubleshooting — Omni Keywords Finder

## 1. Backend não sobe
- **Causas comuns:**
  - Porta ocupada
  - Variáveis de ambiente ausentes
  - Dependências não instaladas
- **Ações:**
  - Verifique logs em `logs/omni_keywords.log`
  - Rode `pip install -r requirements.txt`
  - Confirme `.env` preenchido

## 2. Testes falham
- **Causas comuns:**
  - Banco/Redis não iniciado
  - Dados de teste inconsistentes
  - Mudanças recentes sem atualizar testes
- **Ações:**
  - Rode `pytest -v` e analise o erro
  - Verifique dependências externas
  - Consulte `test-results/` para detalhes

## 3. Exportação não gera arquivo
- **Causas comuns:**
  - Permissão de escrita
  - Espaço em disco insuficiente
  - Dados inválidos
- **Ações:**
  - Verifique diretórios de saída
  - Cheque logs de erro
  - Rode exportação manualmente

## 4. Métricas/monitoramento não aparecem
- **Causas comuns:**
  - Blueprint não registrado
  - Porta/firewall bloqueando
  - Prometheus não configurado
- **Ações:**
  - Acesse `/metrics` diretamente
  - Verifique `docs/monitoramento.md`
  - Cheque logs do Prometheus

## 5. Links úteis
- [logs/omni_keywords.log](../../logs/omni_keywords.log)
- [docs/monitoramento.md](../monitoramento.md)
- [docs/security.md](../security.md)
- [docs/disaster_recovery.md](../disaster_recovery.md) 