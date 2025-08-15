# 🎵 **TikTok API Setup**

**Tracing ID**: `tiktok-setup-2025-01-27-001`  
**Timestamp**: 2025-01-27T15:00:00Z  
**Versão**: 1.0  
**Status**: 📋 **DOCUMENTAÇÃO**

---

## 📋 **RESUMO EXECUTIVO**

### **Objetivo**
Implementar integração completa com TikTok for Developers API para análise de tendências, hashtags e engajamento no sistema Omni Keywords Finder.

### **Métricas Alvo**
- **Taxa de Descoberta**: > 85%
- **Tempo de Análise**: < 5s
- **Precisão de Tendências**: > 90%
- **Cobertura de Testes**: 90%

---

## 🚀 **SETUP INICIAL**

### **1.1 Criar Conta TikTok Developer**

#### **Passos**
1. Acessar [TikTok for Developers](https://developers.tiktok.com/)
2. Criar conta de desenvolvedor
3. Configurar aplicação
4. Obter credenciais de API
5. Configurar permissões

#### **Requisitos**
- Conta TikTok válida
- Aplicação aprovada pela TikTok
- Compliance com políticas da plataforma
- Documentação de uso de dados

### **1.2 Configurar Aplicação**

#### **Credenciais Necessárias**
```bash
# TikTok for Developers
TIKTOK_CLIENT_KEY=your_client_key_here
TIKTOK_CLIENT_SECRET=your_client_secret_here
TIKTOK_REDIRECT_URI=https://api.omni-keywords.com/auth/tiktok/callback

# Web Scraping Fallback
TIKTOK_SCRAPER_USER_AGENT=Mozilla/5.0 (compatible; OmniKeywordsBot/1.0)
TIKTOK_SCRAPER_DELAY=2.0
```

#### **Configurações de Ambiente**
```yaml
# config/tiktok.yaml
environment: production  # ou sandbox
api_version: v1.3
rate_limits:
  requests_per_minute: 100
  requests_per_hour: 1000
  requests_per_day: 10000

scraping:
  enabled: true
  user_agent: "Mozilla/5.0 (compatible; OmniKeywordsBot/1.0)"
  delay_seconds: 2.0
  max_retries: 3
  timeout_seconds: 30

features:
  video_analysis: true
  hashtag_trends: true
  user_engagement: true
  comment_analysis: true
```

---

## 🔧 **INTEGRAÇÃO TÉCNICA**

### **2.1 TikTok for Developers API**

#### **Instalação**
```bash
pip install tiktok-api-python
# ou
pip install requests
```

#### **Configuração Básica**
```python
import requests

# Configuração
TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"
CLIENT_KEY = "your_client_key"
CLIENT_SECRET = "your_client_secret"

# Headers padrão
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

### **2.2 Endpoints Principais**

#### **Autenticação OAuth 2.0**
```python
# POST /oauth/token/
auth_data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "grant_type": "authorization_code",
    "code": authorization_code,
    "redirect_uri": REDIRECT_URI
}
```

#### **Busca de Vídeos**
```python
# GET /video/query/
video_params = {
    "fields": ["id", "title", "description", "duration", "cover_image_url", "video_url", "statistics"],
    "query": "keyword_search",
    "max_count": 20
}
```

#### **Análise de Hashtags**
```python
# GET /hashtag/search/
hashtag_params = {
    "query": "trending_hashtag",
    "fields": ["id", "name", "title", "description", "video_count"]
}
```

#### **Dados de Usuário**
```python
# GET /user/info/
user_params = {
    "fields": ["open_id", "union_id", "avatar_url", "display_name", "bio_description", "profile_deep_link", "is_verified", "follower_count", "following_count", "likes_count"]
}
```

---

## 🔒 **SEGURANÇA E COMPLIANCE**

### **3.1 OAuth 2.0 Implementation**

#### **Fluxo de Autenticação**
```python
def get_tiktok_auth_url():
    """
    Gera URL de autorização TikTok
    """
    auth_url = "https://www.tiktok.com/v2/auth/authorize/"
    params = {
        "client_key": CLIENT_KEY,
        "scope": "user.info.basic,video.list,hashtag.search",
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": generate_random_state()
    }
    
    return f"{auth_url}?{urlencode(params)}"

def exchange_code_for_token(authorization_code):
    """
    Troca código de autorização por access token
    """
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data)
    return response.json()
```

### **3.2 Rate Limiting**

#### **Implementação de Rate Limiting**
```python
class TikTokRateLimiter:
    """
    Rate limiter específico para TikTok API
    """
    def __init__(self):
        self.requests_per_minute = 100
        self.requests_per_hour = 1000
        self.requests_per_day = 10000
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
            raise RateLimitExceeded("TikTok API rate limit exceeded")
        
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

class TikTokScraper:
    """
    Scraper de fallback para TikTok
    """
    def __init__(self, config):
        self.user_agent = config.get("user_agent")
        self.delay = config.get("delay_seconds", 2.0)
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
    
    def scrape_hashtag_page(self, hashtag):
        """
        Scrapa página de hashtag
        """
        url = f"https://www.tiktok.com/tag/{hashtag}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extrair dados (implementação específica)
                data = self._extract_hashtag_data(soup)
                
                # Delay aleatório
                time.sleep(self.delay + random.uniform(0, 1))
                
                return data
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Backoff exponencial
    
    def _extract_hashtag_data(self, soup):
        """
        Extrai dados da página de hashtag
        """
        data = {
            "hashtag": "",
            "video_count": 0,
            "trending_videos": [],
            "related_hashtags": []
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
    "client_key": "test_client_key",
    "client_secret": "test_client_secret",
    "access_token": "test_access_token"
}

TEST_VIDEOS = [
    {
        "id": "test_video_001",
        "title": "Test Video 1",
        "description": "Test description",
        "hashtags": ["#test", "#demo"]
    },
    {
        "id": "test_video_002", 
        "title": "Test Video 2",
        "description": "Another test",
        "hashtags": ["#test", "#example"]
    }
]
```

### **4.2 Cenários de Teste**

#### **Fluxos Principais**
1. **Autenticação OAuth 2.0**
   - Gerar URL de autorização
   - Trocar código por token
   - Validar token

2. **Busca de Vídeos**
   - Buscar por keyword
   - Filtrar por hashtag
   - Analisar estatísticas

3. **Análise de Hashtags**
   - Buscar hashtags
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
- Precisão de análise de hashtags
- Tempo de detecção de viralização
- Engajamento médio por vídeo

#### **KPIs Técnicos**
- Taxa de sucesso da API
- Tempo de resposta
- Taxa de fallback para scraping
- Uso de rate limits

### **5.2 Alertas**

#### **Alertas Críticos**
```yaml
alerts:
  - name: "tiktok_api_down"
    condition: "up{job='tiktok_api'} == 0"
    severity: "critical"
    
  - name: "tiktok_high_error_rate"
    condition: "rate(tiktok_errors_total[5m]) > 0.1"
    severity: "warning"
    
  - name: "tiktok_rate_limit_exceeded"
    condition: "rate(tiktok_rate_limit_exceeded_total[5m]) > 0"
    severity: "warning"
    
  - name: "tiktok_scraper_high_usage"
    condition: "rate(tiktok_scraper_requests_total[5m]) > 10"
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
1. **Rate Limiting**: TikTok tem limites rigorosos de API
2. **Mudanças na API**: TikTok pode alterar endpoints
3. **Políticas de Uso**: Restrições de scraping podem mudar
4. **Captcha/Detecção**: TikTok pode detectar automação

### **Mitigações**
1. **Rate limiting inteligente** para respeitar limites
2. **Versioning** da API para compatibilidade
3. **Web scraping ético** com delays e user agents
4. **Fallback robusto** para diferentes cenários

---

## 📚 **REFERÊNCIAS**

### **Documentação Oficial**
- [TikTok for Developers](https://developers.tiktok.com/)
- [API Reference](https://developers.tiktok.com/doc/login-kit-web)
- [OAuth 2.0 Guide](https://developers.tiktok.com/doc/oauth-2-0)

### **Boas Práticas**
- [TikTok Community Guidelines](https://www.tiktok.com/community-guidelines)
- [API Rate Limiting](https://developers.tiktok.com/doc/rate-limits)
- [Web Scraping Ethics](https://www.scrapingbee.com/blog/web-scraping-ethics/)

---

**Documento criado em**: 2025-01-27T15:00:00Z  
**Próxima revisão**: Após implementação  
**Responsável**: Backend Team  
**Versão**: 1.0 