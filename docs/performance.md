# Performance — Teste de Carga Extremo

## Objetivo
Avaliar a robustez do sistema Omni Keywords Finder sob cenários de uso extremo:
- Processamento e exportação de 100.000 keywords de cauda longa
- Execução concorrente de múltiplas exportações
- Medição de latência, throughput, uso de CPU e memória

## Como Executar

1. Certifique-se de que as dependências estão instaladas (`psutil`, etc).
2. Execute o script:
```bash
python tests/load/scripts/teste_extremo.py
```
3. O relatório será salvo em `test-results/relatorio_performance_extremo.txt`.

## Métricas Coletadas
- **Tempo total de execução**
- **Latência por exportação**
- **Throughput (exportações/s)**
- **Uso de CPU (%) antes/depois**
- **Uso de memória (MB) antes/depois**
- **Status e arquivos gerados por exportação**

## Interpretação dos Resultados
- **Tempo total**: Quanto menor, melhor. Ideal < 5 minutos para 100k keywords.
- **CPU/Memória**: Deve permanecer estável e sem picos excessivos.
- **Status**: Todos devem ser `success`.
- **Arquivos**: Todos os arquivos de exportação devem ser gerados corretamente.

## Recomendações
- Se o tempo ou uso de recursos for alto, avalie:
  - Aumentar paralelismo (CONCURRENCY)
  - Otimizar I/O de disco
  - Ajustar chunking de exportação
  - Monitorar gargalos em logs

## Observações
- Este teste não deve ser executado em ambiente de produção.
- Use para validar escalabilidade antes de releases críticos. 