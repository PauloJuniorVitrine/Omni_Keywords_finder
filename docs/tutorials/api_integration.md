# 🔌 **TUTORIAL DE INTEGRAÇÃO VIA API - OMNİ KEYWORDS FINDER**

## 📋 **Visão Geral**

Este tutorial guia você através da integração completa com a API do Omni Keywords Finder, incluindo autenticação, endpoints principais e casos de uso práticos.

---

## 🔑 **1. AUTENTICAÇÃO E CONFIGURAÇÃO**

### **1.1 Obtenção de Credenciais**

#### **Criar Conta e Gerar API Key**
1. Acesse [app.omnikeywords.com](https://app.omnikeywords.com)
2. Faça login ou crie uma conta
3. Vá para **Settings > API Keys**
4. Clique em **Generate New Key**
5. Copie a chave gerada (formato: `oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

#### **Configuração de Permissões**
```json
{
  "api_key": "oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "permissions": {
    "read_keywords": true,
    "write_keywords": true,
    "read_rankings": true,
    "write_rankings": true,
    "read_competitors": true,
    "write_competitors": true,
    "read_reports": true,
    "write_reports": true
  },
  "rate_limits": {
    "requests_per_minute": 1000,
    "requests_per_hour": 50000,
    "requests_per_day": 1000000
  }
}
```

### **1.2 Configuração Inicial**

#### **Python SDK**
```python
# Instalação
pip install omnikeywords

# Configuração básica
from omnikeywords import OmniKeywords

# Inicialização com API key
client = OmniKeywords(
    api_key="oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    environment="production"  # ou "sandbox" para testes
)

# Verificação de conectividade
try:
    account_info = client.get_account_info()
    print(f"Conectado como: {account_info.email}")
    print(f"Plano: {account_info.plan}")
    print(f"Limite de requests: {account_info.rate_limit}")
except Exception as e:
    print(f"Erro de conexão: {e}")
```

#### **JavaScript/Node.js SDK**
```javascript
// Instalação
npm install omnikeywords

// Configuração básica
const OmniKeywords = require('omnikeywords');

const client = new OmniKeywords({
  apiKey: 'oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
  environment: 'production' // ou 'sandbox' para testes
});

// Verificação de conectividade
async function testConnection() {
  try {
    const accountInfo = await client.getAccountInfo();
    console.log(`Conectado como: ${accountInfo.email}`);
    console.log(`Plano: ${accountInfo.plan}`);
    console.log(`Limite de requests: ${accountInfo.rateLimit}`);
  } catch (error) {
    console.error(`Erro de conexão: ${error.message}`);
  }
}

testConnection();
```

#### **cURL (HTTP Requests Diretos)**
```bash
# Teste de conectividade
curl -X GET "https://api.omnikeywords.com/v1/account/info" \
  -H "Authorization: Bearer oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json"
```

---

## 🔍 **2. PESQUISA DE KEYWORDS**

### **2.1 Pesquisa Básica de Keywords**

#### **Python**
```python
# Pesquisa básica
keywords = client.search_keywords(
    query="ferramenta seo",
    country="BR",
    language="pt",
    search_volume_min=1000,
    difficulty_max=70
)

print(f"Keywords encontradas: {len(keywords)}")
for keyword in keywords[:5]:
    print(f"- {keyword.keyword}: {keyword.search_volume} buscas/mês")
```

#### **JavaScript**
```javascript
// Pesquisa básica
async function searchKeywords() {
  const keywords = await client.searchKeywords({
    query: 'ferramenta seo',
    country: 'BR',
    language: 'pt',
    searchVolumeMin: 1000,
    difficultyMax: 70
  });

  console.log(`Keywords encontradas: ${keywords.length}`);
  keywords.slice(0, 5).forEach(keyword => {
    console.log(`- ${keyword.keyword}: ${keyword.searchVolume} buscas/mês`);
  });
}

searchKeywords();
```

#### **cURL**
```bash
curl -X POST "https://api.omnikeywords.com/v1/keywords/search" \
  -H "Authorization: Bearer oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ferramenta seo",
    "country": "BR",
    "language": "pt",
    "search_volume_min": 1000,
    "difficulty_max": 70
  }'
```

### **2.2 Pesquisa Avançada com Filtros**

#### **Python**
```python
# Pesquisa avançada
advanced_keywords = client.search_keywords_advanced(
    seed_keywords=["seo", "otimização google"],
    filters={
        "search_volume": {"min": 1000, "max": 100000},
        "difficulty": {"min": 0, "max": 70},
        "cpc": {"min": 0.5, "max": 10.0},
        "competition": {"min": 0, "max": 0.8}
    },
    include_related=True,
    include_questions=True,
    include_long_tail=True,
    max_results=1000
)

# Análise dos resultados
for keyword in advanced_keywords:
    print(f"Keyword: {keyword.keyword}")
    print(f"  Volume: {keyword.search_volume}")
    print(f"  Dificuldade: {keyword.difficulty}")
    print(f"  CPC: ${keyword.cpc}")
    print(f"  Competição: {keyword.competition}")
    print("---")
```

#### **JavaScript**
```javascript
// Pesquisa avançada
async function searchAdvancedKeywords() {
  const advancedKeywords = await client.searchKeywordsAdvanced({
    seedKeywords: ['seo', 'otimização google'],
    filters: {
      searchVolume: { min: 1000, max: 100000 },
      difficulty: { min: 0, max: 70 },
      cpc: { min: 0.5, max: 10.0 },
      competition: { min: 0, max: 0.8 }
    },
    includeRelated: true,
    includeQuestions: true,
    includeLongTail: true,
    maxResults: 1000
  });

  advancedKeywords.forEach(keyword => {
    console.log(`Keyword: ${keyword.keyword}`);
    console.log(`  Volume: ${keyword.searchVolume}`);
    console.log(`  Dificuldade: ${keyword.difficulty}`);
    console.log(`  CPC: $${keyword.cpc}`);
    console.log(`  Competição: ${keyword.competition}`);
    console.log('---');
  });
}

searchAdvancedKeywords();
```

### **2.3 Análise de Concorrentes**

#### **Python**
```python
# Análise de keywords de concorrentes
competitor_keywords = client.analyze_competitor_keywords(
    domain="concorrente.com",
    analysis_type="ranking_keywords",
    filters={
        "search_volume_min": 1000,
        "difficulty_max": 80,
        "position_max": 20
    }
)

print(f"Keywords do concorrente: {len(competitor_keywords)}")
for keyword in competitor_keywords[:10]:
    print(f"- {keyword.keyword}: posição {keyword.position}")
```

#### **JavaScript**
```javascript
// Análise de keywords de concorrentes
async function analyzeCompetitorKeywords() {
  const competitorKeywords = await client.analyzeCompetitorKeywords({
    domain: 'concorrente.com',
    analysisType: 'ranking_keywords',
    filters: {
      searchVolumeMin: 1000,
      difficultyMax: 80,
      positionMax: 20
    }
  });

  console.log(`Keywords do concorrente: ${competitorKeywords.length}`);
  competitorKeywords.slice(0, 10).forEach(keyword => {
    console.log(`- ${keyword.keyword}: posição ${keyword.position}`);
  });
}

analyzeCompetitorKeywords();
```

---

## 📊 **3. TRACKING DE RANKINGS**

### **3.1 Configuração de Tracking**

#### **Python**
```python
# Configurar tracking de rankings
tracking_config = client.setup_ranking_tracking(
    domain="seudominio.com",
    keywords=[
        "ferramenta seo",
        "otimização google",
        "keyword research"
    ],
    search_engines=["google", "bing"],
    locations=["BR", "US"],
    devices=["desktop", "mobile"],
    tracking_frequency="daily"
)

print(f"Tracking configurado para {len(tracking_config.keywords)} keywords")
print(f"ID do tracking: {tracking_config.tracking_id}")
```

#### **JavaScript**
```javascript
// Configurar tracking de rankings
async function setupRankingTracking() {
  const trackingConfig = await client.setupRankingTracking({
    domain: 'seudominio.com',
    keywords: [
      'ferramenta seo',
      'otimização google',
      'keyword research'
    ],
    searchEngines: ['google', 'bing'],
    locations: ['BR', 'US'],
    devices: ['desktop', 'mobile'],
    trackingFrequency: 'daily'
  });

  console.log(`Tracking configurado para ${trackingConfig.keywords.length} keywords`);
  console.log(`ID do tracking: ${trackingConfig.trackingId}`);
}

setupRankingTracking();
```

### **3.2 Obtenção de Dados de Ranking**

#### **Python**
```python
# Obter rankings atuais
rankings = client.get_rankings(
    tracking_id="track_xxxxxxxxxxxxxxxx",
    date_range="last_30_days",
    include_history=True
)

# Análise dos rankings
for ranking in rankings:
    print(f"Keyword: {ranking.keyword}")
    print(f"  Posição atual: {ranking.current_position}")
    print(f"  Posição anterior: {ranking.previous_position}")
    print(f"  Mudança: {ranking.position_change}")
    print(f"  Data: {ranking.date}")
    print("---")
```

#### **JavaScript**
```javascript
// Obter rankings atuais
async function getRankings() {
  const rankings = await client.getRankings({
    trackingId: 'track_xxxxxxxxxxxxxxxx',
    dateRange: 'last_30_days',
    includeHistory: true
  });

  rankings.forEach(ranking => {
    console.log(`Keyword: ${ranking.keyword}`);
    console.log(`  Posição atual: ${ranking.currentPosition}`);
    console.log(`  Posição anterior: ${ranking.previousPosition}`);
    console.log(`  Mudança: ${ranking.positionChange}`);
    console.log(`  Data: ${ranking.date}`);
    console.log('---');
  });
}

getRankings();
```

---

## 📈 **4. RELATÓRIOS E ANÁLISES**

### **4.1 Geração de Relatórios**

#### **Python**
```python
# Gerar relatório completo
report = client.generate_report(
    report_type="seo_performance",
    date_range="last_30_days",
    include_sections=[
        "keyword_performance",
        "ranking_changes",
        "competitor_analysis",
        "recommendations"
    ],
    format="json"  # ou "pdf", "csv", "excel"
)

# Salvar relatório
with open("relatorio_seo.json", "w") as f:
    json.dump(report, f, indent=2)

print("Relatório gerado com sucesso!")
```

#### **JavaScript**
```javascript
// Gerar relatório completo
async function generateReport() {
  const report = await client.generateReport({
    reportType: 'seo_performance',
    dateRange: 'last_30_days',
    includeSections: [
      'keyword_performance',
      'ranking_changes',
      'competitor_analysis',
      'recommendations'
    ],
    format: 'json' // ou 'pdf', 'csv', 'excel'
  });

  // Salvar relatório
  const fs = require('fs');
  fs.writeFileSync('relatorio_seo.json', JSON.stringify(report, null, 2));
  
  console.log('Relatório gerado com sucesso!');
}

generateReport();
```

### **4.2 Análise de Performance**

#### **Python**
```python
# Análise de performance de keywords
performance_analysis = client.analyze_keyword_performance(
    keywords=["keyword1", "keyword2", "keyword3"],
    metrics=[
        "search_volume",
        "ranking_position",
        "click_through_rate",
        "conversion_rate"
    ],
    date_range="last_90_days"
)

# Visualização dos dados
import matplotlib.pyplot as plt

for keyword, data in performance_analysis.items():
    plt.plot(data.dates, data.search_volumes, label=keyword)

plt.title("Performance de Keywords")
plt.xlabel("Data")
plt.ylabel("Volume de Busca")
plt.legend()
plt.show()
```

#### **JavaScript**
```javascript
// Análise de performance de keywords
async function analyzeKeywordPerformance() {
  const performanceAnalysis = await client.analyzeKeywordPerformance({
    keywords: ['keyword1', 'keyword2', 'keyword3'],
    metrics: [
      'search_volume',
      'ranking_position',
      'click_through_rate',
      'conversion_rate'
    ],
    dateRange: 'last_90_days'
  });

  // Visualização com Chart.js
  const ctx = document.getElementById('performanceChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: performanceAnalysis.dates,
      datasets: Object.keys(performanceAnalysis.keywords).map(keyword => ({
        label: keyword,
        data: performanceAnalysis.keywords[keyword].searchVolumes
      }))
    }
  });
}

analyzeKeywordPerformance();
```

---

## 🔔 **5. WEBHOOKS E NOTIFICAÇÕES**

### **5.1 Configuração de Webhooks**

#### **Python**
```python
# Configurar webhook
webhook_config = client.setup_webhook(
    url="https://seudominio.com/webhook/omnikeywords",
    events=[
        "ranking_change",
        "new_keyword",
        "competitor_move",
        "report_ready"
    ],
    secret="seu_secret_webhook",
    retry_attempts=3
)

print(f"Webhook configurado: {webhook_config.webhook_id}")
```

#### **JavaScript**
```javascript
// Configurar webhook
async function setupWebhook() {
  const webhookConfig = await client.setupWebhook({
    url: 'https://seudominio.com/webhook/omnikeywords',
    events: [
      'ranking_change',
      'new_keyword',
      'competitor_move',
      'report_ready'
    ],
    secret: 'seu_secret_webhook',
    retryAttempts: 3
  });

  console.log(`Webhook configurado: ${webhookConfig.webhook_id}`);
}

setupWebhook();
```

### **5.2 Processamento de Webhooks**

#### **Python (Flask)**
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhook/omnikeywords', methods=['POST'])
def webhook_handler():
    # Verificar assinatura
    signature = request.headers.get('X-Omni-Signature')
    payload = request.get_data()
    
    expected_signature = hmac.new(
        b'seu_secret_webhook',
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Processar evento
    event_data = request.json
    event_type = event_data['event_type']
    
    if event_type == 'ranking_change':
        handle_ranking_change(event_data)
    elif event_type == 'new_keyword':
        handle_new_keyword(event_data)
    
    return jsonify({'status': 'success'}), 200

def handle_ranking_change(data):
    print(f"Ranking mudou para {data['keyword']}: {data['old_position']} -> {data['new_position']}")

def handle_new_keyword(data):
    print(f"Nova keyword descoberta: {data['keyword']}")

if __name__ == '__main__':
    app.run(debug=True)
```

#### **JavaScript (Express)**
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

app.post('/webhook/omnikeywords', (req, res) => {
  // Verificar assinatura
  const signature = req.headers['x-omi-signature'];
  const payload = JSON.stringify(req.body);
  
  const expectedSignature = crypto
    .createHmac('sha256', 'seu_secret_webhook')
    .update(payload)
    .digest('hex');
  
  if (signature !== expectedSignature) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Processar evento
  const eventData = req.body;
  const eventType = eventData.event_type;
  
  switch (eventType) {
    case 'ranking_change':
      handleRankingChange(eventData);
      break;
    case 'new_keyword':
      handleNewKeyword(eventData);
      break;
  }
  
  res.json({ status: 'success' });
});

function handleRankingChange(data) {
  console.log(`Ranking mudou para ${data.keyword}: ${data.old_position} -> ${data.new_position}`);
}

function handleNewKeyword(data) {
  console.log(`Nova keyword descoberta: ${data.keyword}`);
}

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

---

## 🛠️ **6. CASOS DE USO PRÁTICOS**

### **6.1 Dashboard de SEO Automático**

#### **Python**
```python
# Dashboard de SEO automático
class SEODashboard:
    def __init__(self, api_key):
        self.client = OmniKeywords(api_key=api_key)
    
    def get_dashboard_data(self):
        """Obter dados para dashboard"""
        return {
            "keywords": self.get_keyword_summary(),
            "rankings": self.get_ranking_summary(),
            "competitors": self.get_competitor_summary(),
            "recommendations": self.get_recommendations()
        }
    
    def get_keyword_summary(self):
        """Resumo de keywords"""
        keywords = self.client.get_tracked_keywords()
        return {
            "total": len(keywords),
            "top_performers": [k for k in keywords if k.position <= 10],
            "needs_attention": [k for k in keywords if k.position > 20]
        }
    
    def get_ranking_summary(self):
        """Resumo de rankings"""
        rankings = self.client.get_rankings(date_range="last_7_days")
        improvements = [r for r in rankings if r.position_change > 0]
        declines = [r for r in rankings if r.position_change < 0]
        
        return {
            "improvements": len(improvements),
            "declines": len(declines),
            "stable": len(rankings) - len(improvements) - len(declines)
        }
    
    def get_competitor_summary(self):
        """Resumo de concorrentes"""
        competitors = self.client.get_competitors()
        return {
            "total": len(competitors),
            "threats": [c for c in competitors if c.threat_level == "high"],
            "opportunities": [c for c in competitors if c.opportunity_score > 0.7]
        }
    
    def get_recommendations(self):
        """Obter recomendações"""
        return self.client.get_recommendations(
            analysis_type="seo_optimization",
            priority="high"
        )

# Uso do dashboard
dashboard = SEODashboard("oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
data = dashboard.get_dashboard_data()
print("Dados do dashboard:", data)
```

#### **JavaScript**
```javascript
// Dashboard de SEO automático
class SEODashboard {
  constructor(apiKey) {
    this.client = new OmniKeywords({ apiKey });
  }
  
  async getDashboardData() {
    return {
      keywords: await this.getKeywordSummary(),
      rankings: await this.getRankingSummary(),
      competitors: await this.getCompetitorSummary(),
      recommendations: await this.getRecommendations()
    };
  }
  
  async getKeywordSummary() {
    const keywords = await this.client.getTrackedKeywords();
    return {
      total: keywords.length,
      topPerformers: keywords.filter(k => k.position <= 10),
      needsAttention: keywords.filter(k => k.position > 20)
    };
  }
  
  async getRankingSummary() {
    const rankings = await this.client.getRankings({ dateRange: 'last_7_days' });
    const improvements = rankings.filter(r => r.positionChange > 0);
    const declines = rankings.filter(r => r.positionChange < 0);
    
    return {
      improvements: improvements.length,
      declines: declines.length,
      stable: rankings.length - improvements.length - declines.length
    };
  }
  
  async getCompetitorSummary() {
    const competitors = await this.client.getCompetitors();
    return {
      total: competitors.length,
      threats: competitors.filter(c => c.threatLevel === 'high'),
      opportunities: competitors.filter(c => c.opportunityScore > 0.7)
    };
  }
  
  async getRecommendations() {
    return await this.client.getRecommendations({
      analysisType: 'seo_optimization',
      priority: 'high'
    });
  }
}

// Uso do dashboard
const dashboard = new SEODashboard('oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx');
dashboard.getDashboardData().then(data => {
  console.log('Dados do dashboard:', data);
});
```

### **6.2 Sistema de Alertas Inteligentes**

#### **Python**
```python
# Sistema de alertas inteligentes
class SEOAlertSystem:
    def __init__(self, api_key):
        self.client = OmniKeywords(api_key=api_key)
        self.alert_rules = []
    
    def add_alert_rule(self, rule):
        """Adicionar regra de alerta"""
        self.alert_rules.append(rule)
    
    def check_alerts(self):
        """Verificar alertas"""
        alerts = []
        
        for rule in self.alert_rules:
            if rule['type'] == 'ranking_drop':
                alerts.extend(self.check_ranking_drops(rule))
            elif rule['type'] == 'competitor_move':
                alerts.extend(self.check_competitor_moves(rule))
            elif rule['type'] == 'new_keyword':
                alerts.extend(self.check_new_keywords(rule))
        
        return alerts
    
    def check_ranking_drops(self, rule):
        """Verificar quedas de ranking"""
        rankings = self.client.get_rankings(date_range="last_24_hours")
        alerts = []
        
        for ranking in rankings:
            if (ranking.position_change < rule['threshold'] and 
                ranking.keyword in rule['keywords']):
                alerts.append({
                    'type': 'ranking_drop',
                    'keyword': ranking.keyword,
                    'old_position': ranking.previous_position,
                    'new_position': ranking.current_position,
                    'severity': 'high' if abs(ranking.position_change) > 10 else 'medium'
                })
        
        return alerts
    
    def check_competitor_moves(self, rule):
        """Verificar movimentos de concorrentes"""
        competitors = self.client.get_competitors()
        alerts = []
        
        for competitor in competitors:
            if competitor.domain in rule['competitors']:
                recent_moves = competitor.get_recent_moves(days=7)
                for move in recent_moves:
                    if move.position_change > rule['threshold']:
                        alerts.append({
                            'type': 'competitor_move',
                            'competitor': competitor.domain,
                            'keyword': move.keyword,
                            'position_change': move.position_change,
                            'severity': 'high'
                        })
        
        return alerts
    
    def check_new_keywords(self, rule):
        """Verificar novas keywords"""
        new_keywords = self.client.get_new_keywords(
            search_volume_min=rule['min_volume'],
            difficulty_max=rule['max_difficulty']
        )
        
        return [{
            'type': 'new_keyword',
            'keyword': kw.keyword,
            'search_volume': kw.search_volume,
            'difficulty': kw.difficulty,
            'severity': 'medium'
        } for kw in new_keywords]

# Configuração do sistema de alertas
alert_system = SEOAlertSystem("oki_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Adicionar regras
alert_system.add_alert_rule({
    'type': 'ranking_drop',
    'keywords': ['palavra-chave-critica'],
    'threshold': -5
})

alert_system.add_alert_rule({
    'type': 'competitor_move',
    'competitors': ['concorrente.com'],
    'threshold': 10
})

alert_system.add_alert_rule({
    'type': 'new_keyword',
    'min_volume': 1000,
    'max_difficulty': 60
})

# Verificar alertas
alerts = alert_system.check_alerts()
for alert in alerts:
    print(f"ALERTA: {alert['type']} - {alert.get('keyword', alert.get('competitor', 'N/A'))}")
```

---

## 🔧 **7. TRATAMENTO DE ERROS E LIMITES**

### **7.1 Tratamento de Erros**

#### **Python**
```python
import time
from omnikeywords.exceptions import (
    RateLimitExceeded,
    InvalidAPIKey,
    QuotaExceeded,
    ServerError
)

def safe_api_call(func, *args, **kwargs):
    """Chamada segura da API com retry"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RateLimitExceeded:
            if attempt < max_retries - 1:
                print(f"Rate limit excedido. Aguardando {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise
        except InvalidAPIKey:
            print("API key inválida. Verifique suas credenciais.")
            raise
        except QuotaExceeded:
            print("Quota excedida. Considere fazer upgrade do plano.")
            raise
        except ServerError:
            if attempt < max_retries - 1:
                print(f"Erro do servidor. Tentativa {attempt + 1}/{max_retries}")
                time.sleep(retry_delay)
            else:
                raise
        except Exception as e:
            print(f"Erro inesperado: {e}")
            raise

# Uso
try:
    keywords = safe_api_call(client.search_keywords, "ferramenta seo")
    print(f"Keywords encontradas: {len(keywords)}")
except Exception as e:
    print(f"Falha na busca: {e}")
```

#### **JavaScript**
```javascript
// Tratamento de erros com retry
async function safeApiCall(apiFunction, ...args) {
  const maxRetries = 3;
  let retryDelay = 1000;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await apiFunction(...args);
    } catch (error) {
      if (error.name === 'RateLimitExceeded') {
        if (attempt < maxRetries - 1) {
          console.log(`Rate limit excedido. Aguardando ${retryDelay}ms...`);
          await new Promise(resolve => setTimeout(resolve, retryDelay));
          retryDelay *= 2;
        } else {
          throw error;
        }
      } else if (error.name === 'InvalidAPIKey') {
        console.log('API key inválida. Verifique suas credenciais.');
        throw error;
      } else if (error.name === 'QuotaExceeded') {
        console.log('Quota excedida. Considere fazer upgrade do plano.');
        throw error;
      } else if (error.name === 'ServerError') {
        if (attempt < maxRetries - 1) {
          console.log(`Erro do servidor. Tentativa ${attempt + 1}/${maxRetries}`);
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        } else {
          throw error;
        }
      } else {
        console.log(`Erro inesperado: ${error.message}`);
        throw error;
      }
    }
  }
}

// Uso
async function searchKeywordsSafely() {
  try {
    const keywords = await safeApiCall(client.searchKeywords, 'ferramenta seo');
    console.log(`Keywords encontradas: ${keywords.length}`);
  } catch (error) {
    console.log(`Falha na busca: ${error.message}`);
  }
}

searchKeywordsSafely();
```

### **7.2 Monitoramento de Rate Limits**

#### **Python**
```python
class RateLimitMonitor:
    def __init__(self):
        self.requests_this_minute = 0
        self.requests_this_hour = 0
        self.last_reset_minute = time.time()
        self.last_reset_hour = time.time()
    
    def can_make_request(self):
        """Verificar se pode fazer request"""
        current_time = time.time()
        
        # Reset contadores
        if current_time - self.last_reset_minute >= 60:
            self.requests_this_minute = 0
            self.last_reset_minute = current_time
        
        if current_time - self.last_reset_hour >= 3600:
            self.requests_this_hour = 0
            self.last_reset_hour = current_time
        
        # Verificar limites
        if self.requests_this_minute >= 1000:
            return False, "Rate limit por minuto excedido"
        
        if self.requests_this_hour >= 50000:
            return False, "Rate limit por hora excedido"
        
        return True, "OK"
    
    def record_request(self):
        """Registrar request feito"""
        self.requests_this_minute += 1
        self.requests_this_hour += 1
    
    def get_status(self):
        """Obter status atual"""
        return {
            "requests_this_minute": self.requests_this_minute,
            "requests_this_hour": self.requests_this_hour,
            "remaining_minute": 1000 - self.requests_this_minute,
            "remaining_hour": 50000 - self.requests_this_hour
        }

# Uso do monitor
rate_monitor = RateLimitMonitor()

def monitored_api_call(func, *args, **kwargs):
    can_request, message = rate_monitor.can_make_request()
    if not can_request:
        raise Exception(f"Rate limit: {message}")
    
    result = func(*args, **kwargs)
    rate_monitor.record_request()
    return result

# Verificar status
status = rate_monitor.get_status()
print(f"Requests restantes (minuto): {status['remaining_minute']}")
print(f"Requests restantes (hora): {status['remaining_hour']}")
```

---

## 📚 **8. RECURSOS ADICIONAIS**

### **8.1 Documentação Completa**
- [API Reference](../api/endpoints.md)
- [Authentication Guide](../api/authentication.md)
- [Rate Limiting](../api/rate_limiting.md)
- [Error Codes](../api/error_codes.md)

### **8.2 Exemplos de Código**
- [Exemplos Python](https://github.com/omnikeywords/python-examples)
- [Exemplos JavaScript](https://github.com/omnikeywords/javascript-examples)
- [Exemplos cURL](https://github.com/omnikeywords/curl-examples)

### **8.3 Ferramentas de Desenvolvimento**
- [Postman Collection](../api/postman_collection.json)
- [SDK Downloads](https://omnikeywords.com/sdk)
- [API Playground](https://playground.omnikeywords.com)

### **8.4 Suporte**
- [FAQ](../troubleshooting/faq.md)
- [Debug Guide](../troubleshooting/debug_guide.md)
- [Community Forum](https://community.omnikeywords.com)
- [Email Support](mailto:api-support@omnikeywords.com)

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Configure** sua API key e teste a conectividade
2. **Implemente** a pesquisa básica de keywords
3. **Configure** o tracking de rankings
4. **Integre** webhooks para notificações
5. **Desenvolva** seu dashboard personalizado
6. **Implemente** o sistema de alertas

---

**💡 Dica**: Use o ambiente sandbox para testes antes de usar em produção. O sandbox tem limites menores mas permite desenvolvimento seguro.

---

*Última atualização: 2025-01-27*  
*Versão: 1.0.0* 