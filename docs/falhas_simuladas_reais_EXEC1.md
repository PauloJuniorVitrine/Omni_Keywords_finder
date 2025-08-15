# Relatório de Falhas Simuladas e Fallback Visual — EXEC1

## Cenários Simulados
- Endpoint ausente/indisponível: erro exibido ao usuário, loader removido, sem retry automático.
- Erro de CORS: erro genérico exibido, sem fallback especial.
- Timeout: erro exibido, loader removido.
- Token expirado/headers inválidos: erro 401/403 tratado e exibido.

## Fallback Visual
- Loader nunca congela.
- Mensagens de erro sempre exibidas.
- Não há retry automático, mas usuário pode tentar novamente.
- Não há rastreamento de erro no frontend.

## Resiliência
- Sistema nunca trava ou congela.
- Falhas sempre visíveis ao usuário.
- Ponto de melhoria: retry automático e rastreamento de erros. 