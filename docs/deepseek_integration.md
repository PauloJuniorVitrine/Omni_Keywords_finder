# 🔮 Integração com DeepSeek

## Visão Geral

O **Omni Keywords Finder** agora possui suporte completo para o **DeepSeek** como provedor principal de IA Generativa. O DeepSeek é um modelo de linguagem avançado especializado em programação e análise técnica, oferecendo excelente performance para otimização de prompts.

## 🚀 Configuração

### 1. Configuração de Ambiente

```bash
# Variável de ambiente para API Key do DeepSeek
export DEEPSEEK_API_KEY="sua-api-key-aqui"
```

### 2. Configuração no Cursor

O arquivo `.cursor/config.json` já está configurado com DeepSeek como provedor padrão:

```json
{
  "providers": {
    "deepseek": {
      "apiKey": "sua-api-key-aqui",
      "apiBaseUrl": "https://api.deepseek.com/v1",
      "model": "deepseek-coder-v2.0"
    }
  },
  "defaultProvider": "deepseek"
}
```

### 3. Configuração no Sistema

O arquivo `shared/config.py` inclui suporte para DeepSeek:

```python
class APIConfig:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
```

## 🔧 Uso no Sistema de IA Generativa

### Criação do Otimizador

```python
from infrastructure.ai.generativa.prompt_optimizer import create_prompt_optimizer

# Criar otimizador com DeepSeek (padrão)
optimizer = await create_prompt_optimizer()

# Ou especificar explicitamente
optimizer = await create_prompt_optimizer(
    provider_type="deepseek",
    api_key="sua-api-key",
    model="deepseek-coder-v2.0"
)
```

### Otimização de Prompts

```python
# Otimizar prompt usando DeepSeek
original_prompt = "Pesquise palavras-chave para blog de tecnologia"
optimized_prompt, metrics = await optimizer.optimize_prompt(
    original_prompt,
    strategy=OptimizationStrategy.HYBRID,
    context={"domain": "technology", "language": "português"}
)

print(f"Score: {metrics.overall_score:.2f}")
print(f"Tempo: {metrics.response_time:.2f}s")
```

## 📊 Comparação de Provedores

### Vantagens do DeepSeek

| Aspecto | DeepSeek | OpenAI | Claude |
|---------|----------|--------|--------|
| **Especialização** | Programação | Geral | Geral |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Custo** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Velocidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Precisão Técnica** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### Casos de Uso Ideais

#### ✅ DeepSeek é Ideal Para:
- **Análise de código** e otimização técnica
- **Prompts relacionados a programação**
- **Análise de dados estruturados**
- **Otimização de performance**
- **Projetos com orçamento limitado**

#### 🔄 Outros Provedores Para:
- **Conteúdo criativo** (OpenAI/Claude)
- **Análise de sentimento** (Claude)
- **Geração de texto longo** (GPT-4)

## 🧪 Testes

### Executar Testes Específicos

```bash
# Testes do provedor DeepSeek
pytest tests/unit/infrastructure/ai/generativa/test_prompt_optimizer.py::TestDeepSeekProvider -v

# Testes de integração
pytest tests/unit/infrastructure/ai/generativa/test_prompt_optimizer.py::TestProviderIntegration -v
```

### Exemplo de Teste

```python
import pytest
from infrastructure.ai.generativa.prompt_optimizer import DeepSeekProvider

@pytest.mark.asyncio
async def test_deepseek_optimization():
    provider = DeepSeekProvider("test-key", "deepseek-coder-v2.0")
    
    # Testar otimização
    result = await provider.generate_response("Otimize este prompt")
    assert isinstance(result, str)
    assert len(result) > 0
```

## 🔄 Fallback Automático

O sistema implementa fallback automático entre provedores:

```python
# Configuração de fallback
class FallbackConfig:
    ENABLED: bool = True
    MAX_ATTEMPTS: int = 3
    MODELS_PRIORITY: List[str] = ["deepseek", "openai", "claude"]
    TIMEOUT_MULTIPLIER: float = 1.5
```

### Fluxo de Fallback

1. **Tenta DeepSeek** (provedor principal)
2. **Se falhar, tenta OpenAI**
3. **Se falhar, tenta Claude**
4. **Se todos falharem, usa cache ou erro**

## 📈 Métricas e Monitoramento

### Telemetria Integrada

```python
# Métricas automáticas registradas
telemetry_manager.record_metric(
    "deepseek_api_calls",
    count,
    {"model": "deepseek-coder-v2.0", "operation": "optimization"}
)
```

### Dashboards Disponíveis

- **Taxa de sucesso** por provedor
- **Tempo de resposta** médio
- **Custo por operação**
- **Erros e fallbacks**

## 🛠️ Configuração Avançada

### Modelos Disponíveis

```python
# Modelos DeepSeek suportados
DEEPSEEK_MODELS = {
    "deepseek-coder-v2.0": "Modelo principal para programação",
    "deepseek-chat": "Modelo para conversação geral",
    "deepseek-coder": "Modelo legado para programação"
}
```

### Configuração de Rate Limiting

```python
# Rate limiting específico para DeepSeek
DEEPSEEK_RATE_LIMIT = {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "tokens_per_minute": 100000
}
```

## 🔒 Segurança

### Boas Práticas

1. **Nunca commitar API keys** no código
2. **Usar variáveis de ambiente** para configuração
3. **Implementar rate limiting** para evitar custos excessivos
4. **Monitorar uso** através de telemetria
5. **Implementar fallback** para alta disponibilidade

### Validação de API Key

```python
async def validate_deepseek_key(api_key: str) -> bool:
    """Valida se a API key do DeepSeek é válida."""
    try:
        provider = DeepSeekProvider(api_key)
        response = await provider.generate_response("test", max_tokens=5)
        return True
    except Exception:
        return False
```

## 🚀 Exemplo Completo

```python
import asyncio
from infrastructure.ai.generativa.prompt_optimizer import create_prompt_optimizer
from infrastructure.ai.generativa.prompt_optimizer import OptimizationStrategy

async def exemplo_completo_deepseek():
    """Exemplo completo de uso do DeepSeek."""
    
    # 1. Criar otimizador
    optimizer = await create_prompt_optimizer(
        provider_type="deepseek",
        api_key="sua-api-key-aqui"
    )
    
    # 2. Otimizar prompt
    prompt_original = "Analise performance de código Python"
    
    resultado, metricas = await optimizer.optimize_prompt(
        prompt_original,
        strategy=OptimizationStrategy.HYBRID,
        context={"language": "python", "focus": "performance"}
    )
    
    # 3. Exibir resultados
    print(f"Prompt Original: {prompt_original}")
    print(f"Prompt Otimizado: {resultado}")
    print(f"Score: {metricas.overall_score:.2f}")
    print(f"Tempo: {metricas.response_time:.2f}s")
    
    # 4. Limpar recursos
    await optimizer.close()

# Executar exemplo
if __name__ == "__main__":
    asyncio.run(exemplo_completo_deepseek())
```

## 📚 Recursos Adicionais

### Documentação Oficial
- [DeepSeek API Documentation](https://platform.deepseek.com/docs)
- [Modelos Disponíveis](https://platform.deepseek.com/models)
- [Rate Limits](https://platform.deepseek.com/limits)

### Exemplos no Projeto
- `examples/ai_generativa_example.py` - Exemplo completo
- `tests/unit/infrastructure/ai/generativa/test_prompt_optimizer.py` - Testes

### Suporte
- **Issues**: Criar issue no GitHub do projeto
- **Documentação**: Verificar `docs/` para mais informações
- **Configuração**: Verificar `shared/config.py` para opções

---

**🎯 Resultado**: O DeepSeek está totalmente integrado como provedor principal do sistema de IA Generativa, oferecendo excelente performance para otimização de prompts com foco em programação e análise técnica. 