# Fix Suggestions — EXEC1

## Fixes Recomendados

1. **Automatizar geração de tipos TS**
   - Adicionar script npm:
     ```json
     "scripts": {
       "generate:types": "openapi-typescript ../openapi.yaml --output app/types/api.d.ts"
     }
     ```
   - Integrar à pipeline CI/CD para garantir sincronização automática.

2. **Adicionar configuração explícita de CORS**
   - Usar flask_cors no backend:
     ```python
     from flask_cors import CORS
     CORS(app, origins=["http://localhost:3000"])  # Ajustar conforme ambiente
     ```

3. **Considerar rastreamento de erros no frontend**
   - Integrar Sentry ou similar para capturar falhas não tratadas.

## Observação
- Nenhum breaking change ou fix estrutural urgente detectado.
- Fixes são preventivos e de melhoria contínua. 