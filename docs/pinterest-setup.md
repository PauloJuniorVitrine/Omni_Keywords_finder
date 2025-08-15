# 📌 **Pinterest API v5 Setup Guide**

**Tracing ID**: `pinterest-setup-2025-01-27-001`  
**Timestamp**: 2025-01-27T16:00:00Z  
**Versão**: 1.0  
**Status**: 📋 **DOCUMENTAÇÃO**

---

## 📋 **RESUMO EXECUTIVO**

### **Objetivo**
Implementar integração completa com Pinterest API v5 para análise de pins, boards, tendências e engajamento no sistema Omni Keywords Finder.

### **Métricas Alvo**
- **Taxa de Descoberta**: > 80%
- **Tempo de Análise**: < 3s
- **Precisão de Tendências**: > 85%
- **Cobertura de Testes**: 90%

---

## 🚀 **SETUP INICIAL**

### **1.1 Criar Conta Pinterest Developer**

#### **Passos**
1. Acessar [Pinterest for Developers](https://developers.pinterest.com/)
2. Criar conta de desenvolvedor
3. Configurar aplicação
4. Obter credenciais de API
5. Configurar permissões

#### **Requisitos**
- Conta Pinterest válida
- Aplicação aprovada pela Pinterest
- Compliance com políticas da plataforma
- Documentação de uso de dados

### **1.2 Configurar Aplicação**

#### **Credenciais Necessárias**
```bash
# Pinterest API v5
PINTEREST_APP_ID=your_app_id_here
PINTEREST_APP_SECRET=your_app_secret_here
PINTEREST_REDIRECT_URI=https://api.omni-keywords.com/auth/pinterest/callback

# Web Scraping Fallback
PINTEREST_SCRAPER_USER_AGENT=Mozilla/5.0 (compatible; OmniKeywordsBot/1.0)
PINTEREST_SCRAPER_DELAY=1.5
```

#### **Configurações de Ambiente**
```yaml
# config/pinterest.yaml
environment: production  # ou sandbox
api_version: v5
rate_limits:
  requests_per_minute: 1000
  requests_per_hour: 10000
  requests_per_day: 100000

scraping:
  enabled: true
  user_agent: "Mozilla/5.0 (compatible; OmniKeywordsBot/1.0)"
  delay_seconds: 1.5
  max_retries: 3
  timeout_seconds: 30

features:
  pin_analysis: true
  board_analysis: true
  trend_detection: true
  save_analysis: true
```

---

## 🔧 **INTEGRAÇÃO TÉCNICA**

### **2.1 Pinterest API v5**

#### **Instalação**
```bash
pip install pinterest-api-sdk
# ou
pip install requests
```

#### **Configuração Básica**
```python
import requests

# Configuração
PINTEREST_API_BASE = "https://api.pinterest.com/v5"
APP_ID = "your_app_id"
APP_SECRET = "your_app_secret"

# Headers padrão
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

### **2.2 Endpoints Principais**

#### **Autenticação OAuth 2.0**
```python
# POST /oauth/token
auth_data = {
    "grant_type": "authorization_code",
    "code": authorization_code,
    "redirect_uri": REDIRECT_URI,
    "client_id": APP_ID,
    "client_secret": APP_SECRET
}
```

#### **Busca de Pins**
```python
# GET /pins/search
pin_params = {
    "query": "keyword_search",
    "bookmark": "bookmark_token",
    "page_size": 25
}
```

#### **Análise de Boards**
```python
# GET /boards/{board_id}
board_params = {
    "fields": ["id", "name", "description", "pin_count", "follower_count"]
}
```

#### **Dados de Usuário**
```python
# GET /user_account
user_params = {
    "fields": ["username", "about", "website", "profile_image"]
}
```

---

## 🔒 **SEGURANÇA E COMPLIANCE**

### **3.1 OAuth 2.0 Implementation**

#### **Fluxo de Autenticação**
```python
def get_pinterest_auth_url():
    """
    Gera URL de autorização Pinterest
    """
    auth_url = "https://www.pinterest.com/oauth/"
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "boards:read,pins:read,user_accounts:read",
        "response_type": "code",
        "state": generate_random_state()
    }
    
    return f"{auth_url}?{urlencode(params)}"

def exchange_code_for_token(authorization_code):
    """
    Troca código de autorização por access token
    """
    token_url = "https://api.pinterest.com/v5/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": APP_ID,
        "client_secret": APP_SECRET
    }
    
    response = requests.post(token_url, data=data)
    return response.json()
```

### **3.2 Rate Limiting**

#### **Implementação de Rate Limiting**
```python
class PinterestRateLimiter:
    """
    Rate limiter específico para Pinterest API v5
    """
    def __init__(self):
        self.requests_per_minute = 1000
        self.requests_per_hour = 10000
        self.requests_per_day = 100000
        self.request_times = []
    
    def check_rate_limit(self):
        """
        Verifica se pode fazer requisição
        """
        now = time.time()
        
        # Limpar requisições antigas
        self.request_times = [t for t in self.request_times if now - t < 86400]  # 24h
        
        # Verificar limites
        requests_last_minute = len([t for t in self.request_times if now - t < 60])
        requests_last_hour = len([t for t in self.request_times if now - t < 3600])
        requests_last_day = len(self.request_times)
        
        if (requests_last_minute >= self.requests_per_minute or
            requests_last_hour >= self.requests_per_hour or
            requests_last_day >= self.requests_per_day):
            raise RateLimitExceeded("Pinterest API rate limit exceeded")
        
        # Adicionar requisição atual
        self.request_times.append(now)
```

### **3.3 Web Scraping Fallback**

#### **Scraper Robusto**
```python
import requests
from bs4 import BeautifulSoup
import time
import random

class PinterestScraper:
    """
    Scraper de fallback para Pinterest
    """
    def __init__(self, config):
        self.user_agent = config.get("user_agent")
        self.delay = config.get("delay_seconds", 1.5)
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("timeout_seconds", 30)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
    
    def scrape_search_page(self, query):
        """
        Scrapa página de busca
        """
        url = f"https://www.pinterest.com/search/pins/?q={quote(query)}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extrair dados (implementação específica)
                data = self._extract_search_data(soup)
                
                # Delay aleatório
                time.sleep(self.delay + random.uniform(0, 0.5))
                
                return data
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Backoff exponencial
    
    def _extract_search_data(self, soup):
        """
        Extrai dados da página de busca
        """
        data = {
            "query": "",
            "total_pins": 0,
            "trending_pins": [],
            "related_boards": []
        }
        
        # Implementar extração específica baseada na estrutura HTML
        # Esta é uma implementação simplificada
        
        return data
```

---

## 🧪 **TESTES E VALIDAÇÃO**

### **4.1 Testes de Sandbox**

#### **Credenciais de Teste**
```python
TEST_CREDENTIALS = {
    "app_id": "test_app_id",
    "app_secret": "test_app_secret",
    "access_token": "test_access_token"
}

TEST_PINS = [
    {
        "id": "test_pin_001",
        "title": "Test Pin 1",
        "description": "Test description",
        "board_id": "test_board_001"
    },
    {
        "id": "test_pin_002", 
        "title": "Test Pin 2",
        "description": "Another test",
        "board_id": "test_board_002"
    }
]
```

### **4.2 Cenários de Teste**

#### **Fluxos Principais**
1. **Autenticação OAuth 2.0**
   - Gerar URL de autorização
   - Trocar código por token
   - Validar token

2. **Busca de Pins**
   - Buscar por keyword
   - Filtrar por board
   - Analisar estatísticas

3. **Análise de Boards**
   - Buscar boards
   - Analisar tendências
   - Calcular engajamento

4. **Fallback Web Scraping**
   - Simular falha de API
   - Ativar scraper
   - Validar dados extraídos

---

## 📊 **MONITORAMENTO E MÉTRICAS**

### **5.1 Métricas Essenciais**

#### **KPIs de Negócio**
- Taxa de descoberta de tendências
- Precisão de análise de pins
- Tempo de detecção de viralização
- Engajamento médio por pin

#### **KPIs Técnicos**
- Taxa de sucesso da API
- Tempo de resposta
- Taxa de fallback para scraping
- Uso de rate limits

### **5.2 Alertas**

#### **Alertas Críticos**
```yaml
alerts:
  - name: "pinterest_api_down"
    condition: "up{job='pinterest_api'} == 0"
    severity: "critical"
    
  - name: "pinterest_high_error_rate"
    condition: "rate(pinterest_errors_total[5m]) > 0.1"
    severity: "warning"
    
  - name: "pinterest_rate_limit_exceeded"
    condition: "rate(pinterest_rate_limit_exceeded_total[5m]) > 0"
    severity: "warning"
    
  - name: "pinterest_scraper_high_usage"
    condition: "rate(pinterest_scraper_requests_total[5m]) > 10"
    severity: "info"
```

---

## 🔄 **FLUXO DE IMPLEMENTAÇÃO**

### **Fase 1: Setup Básico (2-3 dias)**
- [x] Criar conta developer
- [x] Configurar aplicação
- [x] Implementar OAuth 2.0
- [x] Testes de autenticação

### **Fase 2: API Integration (3-5 dias)**
- [ ] Implementar endpoints principais
- [ ] Configurar rate limiting
- [ ] Implementar cache
- [ ] Testes de integração

### **Fase 3: Web Scraping Fallback (2-3 dias)**
- [ ] Implementar scraper
- [ ] Configurar fallback
- [ ] Testes de resiliência
- [ ] Validação de dados

### **Fase 4: Análise Avançada (3-5 dias)**
- [ ] Implementar análise de tendências
- [ ] Algoritmo de detecção viral
- [ ] Métricas de engajamento
- [ ] Testes de performance

---

## 📝 **CHECKLIST DE IMPLEMENTAÇÃO**

### **Setup**
- [ ] Conta developer criada
- [ ] Aplicação configurada
- [ ] Credenciais obtidas
- [ ] OAuth 2.0 implementado

### **Desenvolvimento**
- [ ] API endpoints implementados
- [ ] Rate limiting configurado
- [ ] Web scraping fallback
- [ ] Cache implementado

### **Testes**
- [ ] Testes de autenticação
- [ ] Testes de integração
- [ ] Testes de fallback
- [ ] Testes de performance

### **Produção**
- [ ] Ambiente configurado
- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Documentação atualizada

---

## 🚨 **RISCOS E MITIGAÇÕES**

### **Riscos Identificados**
1. **Rate Limiting**: Pinterest tem limites rigorosos de API
2. **Mudanças na API**: Pinterest pode alterar endpoints
3. **Políticas de Uso**: Restrições de scraping podem mudar
4. **Captcha/Detecção**: Pinterest pode detectar automação

### **Mitigações**
1. **Rate limiting inteligente** para respeitar limites
2. **Versioning** da API para compatibilidade
3. **Web scraping ético** com delays e user agents
4. **Fallback robusto** para diferentes cenários

---

## 📚 **REFERÊNCIAS**

### **Documentação Oficial**
- [Pinterest for Developers](https://developers.pinterest.com/)
- [API Reference v5](https://developers.pinterest.com/docs/api/v5/)
- [OAuth 2.0 Guide](https://developers.pinterest.com/docs/api/v5/#tag/OAuth-2.0)

### **Boas Práticas**
- [Pinterest Community Guidelines](https://policy.pinterest.com/en/community-guidelines)
- [API Rate Limiting](https://developers.pinterest.com/docs/api/v5/#section/Rate-Limiting)
- [Web Scraping Ethics](https://www.scrapingbee.com/blog/web-scraping-ethics/)

---

**Documento criado em**: 2025-01-27T16:00:00Z  
**Próxima revisão**: Após implementação  
**Responsável**: Backend Team  
**Versão**: 1.0 