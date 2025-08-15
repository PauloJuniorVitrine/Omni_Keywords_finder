# 📺 **YouTube Data API v3 Setup Guide**

**Tracing ID**: `youtube-setup-2025-01-27-001`  
**Versão**: 1.0  
**Responsável**: Backend Team  
**Data**: 2025-01-27T10:30:00Z

---

## 🎯 **OBJETIVO**

Configurar integração real com YouTube Data API v3 para o sistema Omni Keywords Finder, permitindo coleta de dados de vídeos, comentários, tendências e análise de engajamento.

---

## 📋 **REQUISITOS E LIMITAÇÕES**

### **📐 CoCoT - Fundamentos Técnicos**
- **API Version**: YouTube Data API v3 (atual)
- **Autenticação**: OAuth 2.0 com PKCE
- **Rate Limits**: 10,000 unidades por dia
- **Quota**: Gerenciada por operação (search=100, videos=1, etc.)
- **Endpoints**: RESTful com JSON responses
- **Documentação**: [YouTube Data API v3](https://developers.google.com/youtube/v3)

### **🌲 ToT - Alternativas Avaliadas**
1. **YouTube Data API v3** ✅ **ESCOLHIDA**
   - Vantagens: Oficial, estável, bem documentada
   - Desvantagens: Rate limits, custo por operação
   
2. **Web Scraping** ❌ **REJEITADA**
   - Vantagens: Sem limites, sem custo
   - Desvantagens: Instável, anti-ético, viola ToS
   
3. **YouTube Analytics API** ❌ **REJEITADA**
   - Vantagens: Dados detalhados
   - Desvantagens: Apenas para canais próprios

### **♻️ ReAct - Simulação de Impacto**
- **Cenário 1**: 1000 buscas/dia = 100,000 unidades (10% da quota)
- **Cenário 2**: 500 vídeos + 2000 comentários = 2,500 unidades (25% da quota)
- **Cenário 3**: Análise de tendências = 5,000 unidades (50% da quota)
- **Resultado**: Viável com gestão inteligente de quota

---

## 🔧 **CONFIGURAÇÃO PASSO A PASSO**

### **Fase 1: Setup Google Cloud Project**

#### **1.1 Criar Projeto no Google Cloud**
```bash
# Acessar Google Cloud Console
https://console.cloud.google.com/

# Criar novo projeto
Project Name: omni-keywords-youtube
Project ID: omni-keywords-youtube-2025
```

#### **1.2 Habilitar APIs Necessárias**
```bash
# YouTube Data API v3
gcloud services enable youtube.googleapis.com

# Google OAuth2 API
gcloud services enable oauth2.googleapis.com

# Google+ API (se necessário)
gcloud services enable plus.googleapis.com
```

#### **1.3 Configurar Billing**
- Associar conta de billing ao projeto
- Configurar alertas de quota
- Definir limites de gastos

### **Fase 2: Configuração OAuth 2.0**

#### **2.1 Criar Credenciais OAuth 2.0**
```bash
# Acessar Google Cloud Console > APIs & Services > Credentials
# Criar credenciais OAuth 2.0 Client ID

# Tipo: Web application
# Nome: Omni Keywords YouTube API
# Authorized JavaScript origins:
#   - https://api.omni-keywords.com
#   - http://localhost:5000 (desenvolvimento)

# Authorized redirect URIs:
#   - https://api.omni-keywords.com/auth/youtube/callback
#   - http://localhost:5000/auth/youtube/callback (desenvolvimento)
```

#### **2.2 Configurar Scopes**
```yaml
# Scopes necessários
scopes:
  - https://www.googleapis.com/auth/youtube.readonly
  - https://www.googleapis.com/auth/youtube.force-ssl
  - https://www.googleapis.com/auth/youtube
```

### **Fase 3: Configuração de Quota**

#### **3.1 Configurar Quotas Diárias**
```yaml
# Quotas padrão (pode ser aumentada via solicitação)
daily_quotas:
  default: 10,000 units
  search_requests: 100 units each
  video_requests: 1 unit each
  channel_requests: 1 unit each
  comment_requests: 1 unit each
  playlist_requests: 1 unit each
  subscription_requests: 1 unit each
  activity_requests: 1 unit each
  caption_requests: 200 units each
```

#### **3.2 Configurar Rate Limiting**
```yaml
# Rate limits por segundo
rate_limits:
  requests_per_second: 300
  requests_per_100_seconds: 300
  requests_per_100_seconds_per_user: 300
```

### **Fase 4: Configuração do Sistema**

#### **4.1 Variáveis de Ambiente**
```bash
# .env
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REDIRECT_URI=https://api.omni-keywords.com/auth/youtube/callback
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_QUOTA_LIMIT=10000
YOUTUBE_CACHE_TTL=3600
```

#### **4.2 Configuração de Cache**
```yaml
# config/youtube.yaml
cache:
  strategy: intelligent
  default_ttl: 3600  # 1 hora
  max_ttl: 86400     # 24 horas
  min_ttl: 300       # 5 minutos
  redis_url: redis://localhost:6379
  compression: true

quota_management:
  daily_limit: 10000
  warning_threshold: 0.8
  critical_threshold: 0.95
  reset_time: "00:00"
  timezone: "UTC"
```

---

## 🔍 **ENDPOINTS PRINCIPAIS**

### **Search API**
```python
# Buscar vídeos
GET https://www.googleapis.com/youtube/v3/search
Params:
  - part: snippet
  - q: query_string
  - type: video
  - maxResults: 50
  - order: relevance|date|rating|viewCount|title|videoCount
  - publishedAfter: RFC3339
  - regionCode: ISO3166-1
```

### **Videos API**
```python
# Obter detalhes de vídeo
GET https://www.googleapis.com/youtube/v3/videos
Params:
  - part: snippet,statistics,contentDetails
  - id: video_id
```

### **CommentThreads API**
```python
# Obter comentários
GET https://www.googleapis.com/youtube/v3/commentThreads
Params:
  - part: snippet,replies
  - videoId: video_id
  - maxResults: 100
  - order: relevance|time
```

### **Trending Videos API**
```python
# Obter vídeos em tendência
GET https://www.googleapis.com/youtube/v3/videos
Params:
  - part: snippet,statistics,contentDetails
  - chart: mostPopular
  - regionCode: BR
  - videoCategoryId: category_id
```

---

## 📊 **MÉTRICAS E MONITORAMENTO**

### **Métricas a Coletar**
- **Views por vídeo**
- **Likes e dislikes**
- **Comentários e respostas**
- **Duração do vídeo**
- **Data de publicação**
- **Categoria do vídeo**
- **Tags e descrição**
- **Engajamento (likes + comentários / views)**

### **Alertas Configurados**
```yaml
alerts:
  quota_warning:
    threshold: 80%
    action: notify_team
    
  quota_critical:
    threshold: 95%
    action: stop_requests
    
  quota_exhausted:
    threshold: 100%
    action: enable_fallback
    
  rate_limit_exceeded:
    threshold: 1
    action: retry_with_backoff
```

---

## 🛡️ **SEGURANÇA E COMPLIANCE**

### **OAuth 2.0 Security**
- **PKCE**: Habilitado para aplicações web
- **State Parameter**: Obrigatório para prevenir CSRF
- **Refresh Tokens**: Gerenciamento automático
- **Token Storage**: Criptografado em banco de dados

### **Rate Limiting**
- **Token Bucket**: Implementado para controle de taxa
- **Circuit Breaker**: Para falhas em cascata
- **Retry Logic**: Com backoff exponencial
- **Fallback Strategy**: Cache + web scraping

### **Data Privacy**
- **GDPR Compliance**: Dados anonimizados
- **Data Retention**: 30 dias para dados temporários
- **Access Logs**: Mantidos por 90 dias
- **Audit Trail**: Todas as operações logadas

---

## 🧪 **TESTES E VALIDAÇÃO**

### **Testes de Integração**
```python
# tests/integration/test_youtube_api.py
def test_youtube_search_integration():
    """Testa busca de vídeos."""
    api = YouTubeDataAPI()
    results = api.search_videos("python tutorial", max_results=5)
    assert len(results) > 0
    assert all(hasattr(r, 'video_id') for r in results)

def test_youtube_video_details():
    """Testa obtenção de detalhes de vídeo."""
    api = YouTubeDataAPI()
    video = api.get_video_details("dQw4w9WgXcQ")
    assert video.view_count > 0
    assert video.title is not None

def test_youtube_comments():
    """Testa obtenção de comentários."""
    api = YouTubeDataAPI()
    comments = api.get_video_comments("dQw4w9WgXcQ", max_results=10)
    assert len(comments) >= 0  # Pode ser 0 se vídeo não tem comentários
```

### **Testes de Quota**
```python
def test_quota_management():
    """Testa gestão de quota."""
    manager = YouTubeQuotaManager()
    assert manager.check_quota_available("search")
    assert manager.reserve_quota("search")
    assert not manager.check_quota_available("search")  # Se quota = 1
```

---

## 🚀 **DEPLOYMENT**

### **Ambiente de Desenvolvimento**
```bash
# Instalar dependências
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Configurar variáveis de ambiente
export YOUTUBE_CLIENT_ID="your_dev_client_id"
export YOUTUBE_CLIENT_SECRET="your_dev_client_secret"

# Testar conexão
python -c "from infrastructure.coleta.youtube_data_api import create_youtube_data_client; client = create_youtube_data_client(); print('YouTube API conectada!')"
```

### **Ambiente de Produção**
```bash
# Usar credenciais de produção
export YOUTUBE_CLIENT_ID="your_prod_client_id"
export YOUTUBE_CLIENT_SECRET="your_prod_client_secret"

# Configurar Redis para cache
docker run -d -p 6379:6379 redis:alpine

# Monitorar logs
tail -f logs/youtube_api.log
```

---

## 📈 **MÉTRICAS DE SUCESSO**

### **KPIs Técnicos**
- **Uptime**: > 99.9%
- **Response Time**: < 500ms
- **Cache Hit Rate**: > 80%
- **Quota Utilization**: < 90%
- **Error Rate**: < 1%

### **KPIs de Negócio**
- **Vídeos Analisados**: > 10,000/dia
- **Keywords Extraídas**: > 50,000/dia
- **Tendências Detectadas**: > 100/dia
- **Precisão de Análise**: > 95%

---

## 🔄 **MANUTENÇÃO**

### **Rotinas Diárias**
- Monitorar uso de quota
- Verificar logs de erro
- Atualizar cache expirado
- Backup de dados críticos

### **Rotinas Semanais**
- Análise de performance
- Otimização de queries
- Limpeza de cache antigo
- Atualização de dependências

### **Rotinas Mensais**
- Revisão de quotas
- Análise de tendências
- Otimização de algoritmos
- Auditoria de segurança

---

## 📞 **SUPORTE**

### **Contatos**
- **Desenvolvedor**: Backend Team
- **Email**: backend@omni-keywords.com
- **Slack**: #youtube-api-support
- **Documentação**: [YouTube Data API v3](https://developers.google.com/youtube/v3)

### **Recursos Úteis**
- [YouTube Data API v3 Reference](https://developers.google.com/youtube/v3/docs)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Quota Calculator](https://developers.google.com/youtube/v3/getting-started#quota)
- [Error Codes](https://developers.google.com/youtube/v3/docs/errors)

---

**Documento criado em**: 2025-01-27T10:30:00Z  
**Próxima revisão**: 2025-02-27T10:30:00Z  
**Responsável**: Backend Team  
**Versão**: 1.0 