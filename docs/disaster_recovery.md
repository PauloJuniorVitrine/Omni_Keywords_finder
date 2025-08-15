# Disaster Recovery e Backup

## Objetivo
Garantir a recuperação rápida e segura dos dados críticos do Omni Keywords Finder em caso de falha, perda ou desastre.

## Política Recomendada
- **Frequência:** Backup automático diário ou a cada release crítica.
- **Itens incluídos:** blogs, logs, uploads, relatórios de performance e negócio.
- **Retenção:** Manter pelo menos 7 versões recentes.

## Como Executar
- **Backup:**
```bash
python scripts/backup_restore.py backup
```
- **Restore:**
```bash
python scripts/backup_restore.py restore backups/backup_YYYYMMDDTHHMMSS.zip
```
- **Listar backups disponíveis:**
```bash
python scripts/backup_restore.py listar
```

## Localização dos Arquivos
- Backups são salvos em `backups/`.
- Logs de operação em `logs/backup_restore.log`.

## Métricas de Recuperação
- **RTO (Recovery Time Objective):** < 5 minutos
- **RPO (Recovery Point Objective):** < 24h (ajustável conforme frequência)

## Recomendações
- Automatize o agendamento do backup via cron/tarefa agendada.
- Teste o restore periodicamente em ambiente isolado.
- Armazene cópias externas (cloud, storage seguro) para proteção contra falhas locais.
- Documente o responsável e o procedimento de acionamento. 