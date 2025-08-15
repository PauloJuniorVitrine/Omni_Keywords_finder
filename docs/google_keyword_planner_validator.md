# 🔍 **Google Keyword Planner Validator**

## 📋 **Visão Geral**

O **Google Keyword Planner Validator** é um sistema avançado de validação de keywords que utiliza o Google Keyword Planner como fonte de validação principal. Este validador integra-se ao sistema Omni Keywords Finder para fornecer métricas precisas e validação de qualidade baseada em dados reais do Google.

---

## 🎯 **Objetivos**

### **Validação Inteligente**
- **Validação via API oficial** (Google Ads API)
- **Fallback para web scraping** quando API não está disponível
- **Cache inteligente** para otimizar custos e performance
- **Rate limiting** para evitar bloqueios

### **Métricas de Qualidade**
- **Volume de busca** mensal
- **Nível de competição** (LOW, MEDIUM, HIGH)
- **CPC** (Cost Per Click)
- **Índice de competição** (0-100)
- **Lances sugeridos** (mínimo e máximo)

---

## 🏗️ **Arquitetura**

### **Estrutura de Validadores**

```
ValidadorAvancado (Orquestrador)
├── GoogleKeywordPlannerValidator
│   ├── API Validator (Google Ads API)
│   ├── Web Scraping Validator (Fallback)
│   └── Cache Manager
└── Outros Validadores (Futuros)
```

### **Estratégias de Validação**

#### **1. Cascata**
- Cada validador filtra o resultado do anterior
- Máxima precisão, menor volume de saída
- Ideal para validação rigorosa

#### **2. Paralela**
- Todos os validadores executam simultaneamente
- União de todos os aprovados
- Ideal para máxima cobertura

#### **3. Consenso**
- Keyword deve ser aprovada pela maioria dos validadores
- Equilibra precisão e cobertura
- Ideal para validação balanceada

---

## ⚙️ **Configuração**

### **Arquivo de Configuração**

```yaml
# config/google_keyword_planner.yaml
validacao:
  estrategia_padrao: "cascata"
  timeout_segundos: 300
  max_retries: 3
  
  google_keyword_planner:
    enabled: true
    api_enabled: true
    scraping_enabled: true
    cache_enabled: true
    rate_limiting_enabled: true
    
    # Configurações de API
    api:
      client_id: "${GOOGLE_CLIENT_ID}"
      client_secret: "${GOOGLE_CLIENT_SECRET}"
      refresh_token: "${GOOGLE_REFRESH_TOKEN}"
      customer_id: "${GOOGLE_CUSTOMER_ID}"
    
    # Critérios de Validação
    criterios:
      min_search_volume: 100
      max_cpc: 5.0
      reject_high_competition: true
```

### **Variáveis de Ambiente**

```bash
# Google Ads API
export GOOGLE_CLIENT_ID="your_client_id"
export GOOGLE_CLIENT_SECRET="your_client_secret"
export GOOGLE_REFRESH_TOKEN="your_refresh_token"
export GOOGLE_CUSTOMER_ID="your_customer_id"
```

---

## 🚀 **Uso**

### **Uso Básico**

```python
from infrastructure.processamento.processador_keywords import ProcessadorKeywords
from domain.models import Keyword, IntencaoBusca

# Carregar configuração
config = carregar_configuracao()

# Criar processador
processador = ProcessadorKeywords(config=config)

# Criar keywords
keywords = [
    Keyword(
        termo="marketing digital",
        volume_busca=1000,
        cpc=2.5,
        concorrencia=0.7,
        intencao=IntencaoBusca.COMERCIAL,
        fonte="exemplo"
    )
]

# Processar com validação
keywords_aprovadas = processador.processar_keywords(
    keywords, 
    estrategia_validacao="cascata"
)

# Verificar resultados
for kw in keywords_aprovadas:
    print(f"✅ {kw.termo} - Score: {getattr(kw, 'score_qualidade', 'N/A')}")
```

### **Uso Avançado**

```python
from infrastructure.validacao import ValidadorAvancado

# Criar validador avançado
validador = ValidadorAvancado(config.get("validacao", {}))

# Validação paralela
keywords_paralelas = validador.validar_keywords(
    keywords, 
    estrategia="paralela"
)

# Validação por consenso
keywords_consenso = validador.validar_keywords(
    keywords, 
    estrategia="consenso"
)

# Obter estatísticas
estatisticas = validador.get_estatisticas()
print(f"Taxa de aprovação: {estatisticas['validador_avancado']['overall_approval_rate']:.2%}")
```

### **Obter Métricas Específicas**

```python
from infrastructure.validacao.google_keyword_planner_validator import GoogleKeywordPlannerValidator

# Criar validador Google
google_config = config.get("validacao", {}).get("google_keyword_planner", {})
validador = GoogleKeywordPlannerValidator(google_config)

# Obter métricas
metricas = validador.obter_metricas("marketing digital")

if metricas:
    print(f"Volume: {metricas['search_volume']}")
    print(f"Competição: {metricas['competition']}")
    print(f"CPC: ${metricas['cpc']}")
```

---

## 📊 **Métricas e Score de Qualidade**

### **Cálculo do Score**

O sistema calcula um **score de qualidade** (0-100) baseado em:

```python
# Fatores de qualidade
volume_score = min(40, (search_volume / 10000) * 40)  # 0-40 pontos
competition_score = {"LOW": 30, "MEDIUM": 20, "HIGH": 10}  # 0-30 pontos
cpc_score = max(0, 30 - (cpc * 3))  # 0-30 pontos

total_score = volume_score + competition_score + cpc_score
```

### **Critérios de Validação**

- **Volume mínimo**: 100 buscas/mês
- **CPC máximo**: $5.00
- **Competição**: Rejeita HIGH se configurado
- **Índice de competição**: 0-100

---

## 🔧 **Configuração da API Google Ads**

### **1. Criar Projeto no Google Cloud**

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a Google Ads API

### **2. Configurar OAuth 2.0**

1. Vá para "APIs & Services" > "Credentials"
2. Crie credenciais OAuth 2.0
3. Configure URIs de redirecionamento
4. Baixe o arquivo JSON de credenciais

### **3. Obter Refresh Token**

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configurar escopo
SCOPES = ['https://www.googleapis.com/auth/adwords']

# Executar fluxo OAuth
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json', SCOPES)
credentials = flow.run_local_server(port=0)

# Salvar refresh token
print(f"Refresh Token: {credentials.refresh_token}")
```

### **4. Configurar Customer ID**

1. Acesse [Google Ads](https://ads.google.com/)
2. Vá para "Tools & Settings" > "Setup" > "Account access"
3. Copie o Customer ID (formato: XXX-XXX-XXXX)

---

## 🛠️ **Troubleshooting**

### **Problemas Comuns**

#### **1. Erro de Autenticação**
```
Erro: Invalid credentials
Solução: Verificar refresh_token e customer_id
```

#### **2. Rate Limiting**
```
Erro: Quota exceeded
Solução: Aumentar delay entre requests
```

#### **3. API Indisponível**
```
Erro: API not available
Solução: Fallback automático para web scraping
```

#### **4. Selenium Issues**
```
Erro: WebDriver not found
Solução: Instalar ChromeDriver
```

### **Logs e Debug**

```python
import logging

# Configurar logging detalhado
logging.basicConfig(level=logging.DEBUG)

# Verificar logs do validador
logger.info({
    "event": "debug_validacao",
    "details": {
        "keywords_processadas": len(keywords),
        "estrategia": estrategia,
        "config": config
    }
})
```

---

## 📈 **Monitoramento e Métricas**

### **Métricas Disponíveis**

```python
# Métricas do processador
metricas = processador.get_metricas_completas()

print(f"Total execuções: {metricas['processador']['total_execucoes']}")
print(f"Keywords processadas: {metricas['processador']['total_keywords_processadas']}")
print(f"Taxa aprovação: {metricas['processador']['total_keywords_aprovadas'] / metricas['processador']['total_keywords_processadas']:.2%}")

# Métricas do validador
estatisticas = validador.get_estatisticas()
print(f"Tempo execução: {estatisticas['validador_avancado']['total_execution_time']:.2f}s")
```

### **Alertas e Thresholds**

```yaml
monitoramento:
  alert_threshold:
    error_rate: 0.05  # 5%
    timeout_rate: 0.10  # 10%
    cache_hit_rate: 0.80  # 80%
```

---

## 🔒 **Segurança**

### **Boas Práticas**

1. **Credenciais seguras**
   - Use variáveis de ambiente
   - Nunca commite credenciais
   - Rotacione tokens regularmente

2. **Rate Limiting**
   - Configure delays apropriados
   - Monitore uso da API
   - Implemente backoff exponencial

3. **Cache seguro**
   - Configure TTL apropriado
   - Limpe cache regularmente
   - Monitore uso de memória

---

## 🚀 **Roadmap**

### **Versão 1.1**
- [ ] Suporte a múltiplas contas Google Ads
- [ ] Validação em lote otimizada
- [ ] Métricas avançadas de competição

### **Versão 1.2**
- [ ] Integração com outros validadores
- [ ] Machine Learning para otimização
- [ ] Dashboard de métricas

### **Versão 2.0**
- [ ] API REST para validação
- [ ] Webhooks para notificações
- [ ] Interface web completa

---

## 📞 **Suporte**

### **Documentação**
- [Arquitetura do Sistema](../architecture.md)
- [Guia de Configuração](../guides/configuration.md)
- [API Reference](../api.md)

### **Issues e Bugs**
- Reporte issues no GitHub
- Inclua logs e configuração
- Forneça exemplos reproduzíveis

### **Comunidade**
- Discord: [Link do servidor]
- Email: support@omnikeywords.com
- GitHub: [Issues](https://github.com/omnikeywords/issues)

---

## 📄 **Licença**

Este projeto está licenciado sob a MIT License. Veja o arquivo [LICENSE](../../LICENSE) para detalhes.

---

**Desenvolvido com ❤️ pela equipe Omni Keywords Finder** 