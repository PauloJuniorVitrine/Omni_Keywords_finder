# 🧪 Testes de Performance - Sistema de Credenciais

## 📋 Visão Geral

Este diretório contém testes de performance abrangentes para o sistema de validação de credenciais, garantindo que o sistema mantenha alta performance sob diferentes cargas e cenários.

## 🎯 Objetivos

- **Validação de Performance**: Garantir que as validações de credenciais sejam rápidas e eficientes
- **Testes de Carga**: Verificar comportamento sob alta demanda
- **Testes de Estresse**: Identificar limites do sistema
- **Benchmarks**: Estabelecer métricas de referência
- **Monitoramento**: Coletar métricas detalhadas de performance

## 📁 Estrutura dos Arquivos

```
tests/performance/
├── README.md                           # Esta documentação
├── test_credential_performance.py      # Testes principais de performance
└── test_load_testing.py               # Testes de carga específicos
```

## 🚀 Como Executar

### Execução Manual

```bash
# Executar todos os testes de performance
python -m pytest tests/performance/ -v -m performance

# Executar testes específicos
python -m pytest tests/performance/test_credential_performance.py -v

# Executar com relatório HTML
python -m pytest tests/performance/ --html=performance_report.html --self-contained-html

# Executar com timeout específico
python -m pytest tests/performance/ --timeout=600
```

### Usando o Script Automatizado

```bash
# Executar todos os testes de performance
python scripts/run_performance_tests.py

# Executar testes com marcador específico
python scripts/run_performance_tests.py --marker performance

# Executar teste específico
python scripts/run_performance_tests.py --test-file tests/performance/test_credential_performance.py

# Executar com timeout personalizado
python scripts/run_performance_tests.py --timeout 600 --verbose
```

## 📊 Tipos de Testes

### 1. Testes de Performance Básica
- **Validação Única**: Testa tempo de resposta para uma validação
- **Validação em Lote**: Testa performance com múltiplas credenciais
- **Validação Concorrente**: Testa com requisições simultâneas
- **Validação Mista**: Testa diferentes providers simultaneamente

### 2. Testes de Carga
- **Alta Carga**: 1000+ requisições simultâneas
- **Teste de Estresse**: Execução prolongada com diferentes cenários
- **Teste de Memória**: Detecção de vazamentos de memória

### 3. Testes de Benchmark
- **Métricas de Referência**: Estabelece baseline de performance
- **Comparação de Versões**: Compara performance entre releases
- **Relatórios Detalhados**: Gera relatórios em JSON e HTML

## 📈 Métricas Coletadas

### Performance
- **Tempo de Resposta**: Tempo médio, mínimo, máximo
- **Throughput**: Requisições por segundo (RPS)
- **Percentis**: P95, P99 de tempo de resposta
- **Taxa de Erro**: Porcentagem de falhas

### Recursos do Sistema
- **Uso de Memória**: MB consumidos
- **Uso de CPU**: Percentual de utilização
- **Threads**: Número de threads ativos
- **Arquivos Abertos**: Contagem de handles

### Específicas do Sistema
- **Tempo de Criptografia**: Operações de criptografia/descriptografia
- **Tempo de Validação**: Validação de credenciais
- **Rate Limiting**: Eficiência do rate limiting

## 🎛️ Configurações

### Limites de Performance
```python
performance_thresholds = {
    "single_validation_max_ms": 100,    # 100ms para validação única
    "batch_validation_max_ms": 500,     # 500ms para lote de 10
    "concurrent_validation_max_ms": 2000, # 2s para 50 concorrentes
    "memory_usage_max_mb": 100,         # 100MB máximo
    "cpu_usage_max_percent": 80,        # 80% máximo
    "throughput_min_rps": 10,           # 10 requisições/segundo mínimo
}
```

### Timeouts
- **Teste Individual**: 300 segundos (5 minutos)
- **Teste de Carga**: 600 segundos (10 minutos)
- **Teste de Estresse**: 1800 segundos (30 minutos)

## 📊 Interpretação dos Resultados

### ✅ Performance Adequada
- Tempo de resposta < 100ms para validação única
- Throughput > 10 RPS
- Uso de memória < 100MB
- Taxa de erro < 1%

### ⚠️ Performance Precisa de Atenção
- Tempo de resposta entre 100-500ms
- Throughput entre 5-10 RPS
- Uso de memória entre 100-200MB
- Taxa de erro entre 1-5%

### ❌ Performance Crítica
- Tempo de resposta > 500ms
- Throughput < 5 RPS
- Uso de memória > 200MB
- Taxa de erro > 5%

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Testes Falhando por Timeout
```bash
# Aumentar timeout
python -m pytest tests/performance/ --timeout=600

# Verificar se o backend está rodando
curl http://localhost:5000/health
```

#### 2. Falhas de Memória
```bash
# Verificar uso de memória do sistema
python -c "import psutil; print(psutil.virtual_memory())"

# Executar com menos concorrência
python scripts/run_performance_tests.py --workers 2
```

#### 3. Falhas de Rede
```bash
# Verificar conectividade
ping localhost

# Verificar portas
netstat -an | grep 5000
```

### Logs e Debugging

```bash
# Executar com logs detalhados
python -m pytest tests/performance/ -v -s --log-cli-level=DEBUG

# Salvar logs em arquivo
python -m pytest tests/performance/ --log-file=performance.log
```

## 📋 Checklist de Execução

### Pré-requisitos
- [ ] Backend rodando na porta 5000
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Ambiente virtual ativo
- [ ] Memória livre > 500MB
- [ ] CPU disponível > 50%

### Execução
- [ ] Executar testes básicos de performance
- [ ] Executar testes de carga
- [ ] Executar testes de estresse
- [ ] Gerar relatórios
- [ ] Analisar métricas
- [ ] Documentar resultados

### Pós-execução
- [ ] Verificar relatórios HTML
- [ ] Analisar métricas JSON
- [ ] Comparar com baseline anterior
- [ ] Identificar gargalos
- [ ] Propor otimizações

## 🔄 Integração com CI/CD

### GitHub Actions
```yaml
- name: Performance Tests
  run: |
    python scripts/run_performance_tests.py --marker performance
    python scripts/run_performance_tests.py --marker load
```

### Jenkins Pipeline
```groovy
stage('Performance Tests') {
    steps {
        sh 'python scripts/run_performance_tests.py'
        publishHTML([
            allowMissing: false,
            alwaysLinkToLastBuild: true,
            keepAll: true,
            reportDir: 'performance_results',
            reportFiles: '*.html',
            reportName: 'Performance Report'
        ])
    }
}
```

## 📚 Referências

- [Pytest Performance Testing](https://pytest.org/en/stable/)
- [Performance Testing Best Practices](https://www.guru99.com/performance-testing.html)
- [Load Testing with Python](https://locust.io/)
- [System Monitoring with psutil](https://psutil.readthedocs.io/)

## 🤝 Contribuição

Para adicionar novos testes de performance:

1. Crie um novo arquivo em `tests/performance/`
2. Use os marcadores apropriados (`@pytest.mark.performance`, `@pytest.mark.load`)
3. Implemente métricas de coleta
4. Adicione documentação
5. Execute testes localmente
6. Submeta pull request

## 📞 Suporte

Para dúvidas sobre testes de performance:
- Consulte esta documentação
- Verifique os logs de execução
- Analise os relatórios gerados
- Entre em contato com a equipe de QA 