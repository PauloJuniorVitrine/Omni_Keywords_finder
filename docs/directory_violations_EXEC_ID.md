# Relatório de Violações de Localização Arquitetural — EXEC_ID

## Pontos de Atenção
- Lógica de domínio identificada em `infrastructure/processamento/`.
- Garantir que entidades de domínio permaneçam em `/domain`.
- Controladores HTTP e handlers de API devem estar em `/app/api`.

*Atualize este relatório conforme novas violações forem detectadas.* 