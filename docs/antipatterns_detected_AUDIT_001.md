# Antipadrões Detectados — AUDIT_001

| Tipo                | Módulo/Arquivo                        | Exemplo/Comentário                                  |
|---------------------|---------------------------------------|-----------------------------------------------------|
| Duplicidade lógica  | keyword_utils.py vs. coletores        | Funções de normalização/validação não centralizadas |
| Dead code           | .bak ativos, código comentado         | Risco de divergência e confusão                     |
| SRP/DRY violado     | processador_keywords.py, handlers     | Múltiplas responsabilidades em um único módulo      |
| Falta de docstring  | Diversos                              | Funções públicas sem documentação                   |
| Falta de assertions | Funções críticas                      | Falta de validação explícita                        |
| Imports não usados  | Scripts, handlers                     | Limpeza recomendada                                 | 