import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métricas customizadas
const errorRate = new Rate('errors');

// Configuração do teste
export const options = {
  stages: [
    { duration: '2m', target: 10 },  // Ramp up para 10 usuários
    { duration: '5m', target: 10 },  // Manter 10 usuários
    { duration: '2m', target: 50 },  // Ramp up para 50 usuários
    { duration: '5m', target: 50 },  // Manter 50 usuários
    { duration: '2m', target: 100 }, // Ramp up para 100 usuários
    { duration: '5m', target: 100 }, // Manter 100 usuários
    { duration: '2m', target: 0 },   // Ramp down para 0 usuários
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% das requisições devem ser < 500ms
    http_req_failed: ['rate<0.1'],    // Taxa de erro < 10%
    errors: ['rate<0.1'],             // Taxa de erro customizada < 10%
  },
};

// Configuração base
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'test-api-key';

// Headers padrão
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_KEY}`,
  'User-Agent': 'K6-Load-Test/1.0',
};

// Função para gerar dados de teste
function generateTestData() {
  return {
    keywords: [
      'python tutorial',
      'javascript guide',
      'machine learning',
      'data science',
      'web development',
      'mobile app development',
      'cloud computing',
      'artificial intelligence',
      'blockchain technology',
      'cybersecurity'
    ],
    volumes: [1000, 5000, 10000, 50000, 100000],
    difficulties: [0.1, 0.3, 0.5, 0.7, 0.9]
  };
}

// Função para selecionar dados aleatórios
function getRandomData(testData) {
  return {
    keyword: testData.keywords[Math.floor(Math.random() * testData.keywords.length)],
    volume: testData.volumes[Math.floor(Math.random() * testData.volumes.length)],
    difficulty: testData.difficulties[Math.floor(Math.random() * testData.difficulties.length)]
  };
}

// Cenário principal
export default function() {
  const testData = generateTestData();
  
  // 1. Health Check
  const healthCheck = check(http.get(`${BASE_URL}/health`, { headers }), {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  if (!healthCheck) {
    errorRate.add(1);
  }
  
  sleep(1);
  
  // 2. Processar Keywords
  const keywordData = getRandomData(testData);
  const processPayload = {
    keywords: [{
      termo: keywordData.keyword,
      volume_busca: keywordData.volume,
      cpc: Math.random() * 5,
      concorrencia: keywordData.difficulty
    }]
  };
  
  const processResponse = check(http.post(`${BASE_URL}/api/processar_keywords`, 
    JSON.stringify(processPayload), 
    { headers }
  ), {
    'process keywords status is 200': (r) => r.status === 200,
    'process keywords response time < 1000ms': (r) => r.timings.duration < 1000,
    'process keywords returns valid data': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.keywords && Array.isArray(data.keywords);
      } catch (e) {
        return false;
      }
    },
  });
  
  if (!processResponse) {
    errorRate.add(1);
  }
  
  sleep(2);
  
  // 3. Exportar Keywords
  const exportResponse = check(http.get(`${BASE_URL}/api/exportar_keywords?formato=json`, 
    { headers }
  ), {
    'export keywords status is 200': (r) => r.status === 200,
    'export keywords response time < 500ms': (r) => r.timings.duration < 500,
    'export keywords returns valid JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch (e) {
        return false;
      }
    },
  });
  
  if (!exportResponse) {
    errorRate.add(1);
  }
  
  sleep(1);
  
  // 4. Consultar Logs de Governança
  const logsResponse = check(http.get(`${BASE_URL}/api/governanca/logs`, 
    { headers }
  ), {
    'governance logs status is 200': (r) => r.status === 200,
    'governance logs response time < 300ms': (r) => r.timings.duration < 300,
  });
  
  if (!logsResponse) {
    errorRate.add(1);
  }
  
  sleep(1);
  
  // 5. Teste de API de Execuções
  const execucoesResponse = check(http.get(`${BASE_URL}/api/execucoes`, 
    { headers }
  ), {
    'execucoes status is 200': (r) => r.status === 200,
    'execucoes response time < 400ms': (r) => r.timings.duration < 400,
  });
  
  if (!execucoesResponse) {
    errorRate.add(1);
  }
  
  sleep(1);
  
  // 6. Teste de Métricas de Negócio
  const metricsResponse = check(http.get(`${BASE_URL}/api/business_metrics`, 
    { headers }
  ), {
    'business metrics status is 200': (r) => r.status === 200,
    'business metrics response time < 600ms': (r) => r.timings.duration < 600,
  });
  
  if (!metricsResponse) {
    errorRate.add(1);
  }
  
  sleep(1);
  
  // 7. Teste de Auditoria
  const auditResponse = check(http.get(`${BASE_URL}/api/auditoria`, 
    { headers }
  ), {
    'audit status is 200': (r) => r.status === 200,
    'audit response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  if (!auditResponse) {
    errorRate.add(1);
  }
  
  sleep(1);
  
  // 8. Teste de Webhooks
  const webhookPayload = {
    event: 'test_event',
    data: {
      keyword: keywordData.keyword,
      status: 'processed',
      timestamp: new Date().toISOString()
    }
  };
  
  const webhookResponse = check(http.post(`${BASE_URL}/api/webhooks`, 
    JSON.stringify(webhookPayload), 
    { headers }
  ), {
    'webhook status is 200': (r) => r.status === 200,
    'webhook response time < 300ms': (r) => r.timings.duration < 300,
  });
  
  if (!webhookResponse) {
    errorRate.add(1);
  }
  
  sleep(1);
  
  // 9. Teste de Analytics Avançado
  const analyticsPayload = {
    metrics: ['volume', 'difficulty', 'cpc'],
    filters: {
      date_range: 'last_30_days',
      min_volume: 1000
    }
  };
  
  const analyticsResponse = check(http.post(`${BASE_URL}/api/advanced_analytics`, 
    JSON.stringify(analyticsPayload), 
    { headers }
  ), {
    'analytics status is 200': (r) => r.status === 200,
    'analytics response time < 800ms': (r) => r.timings.duration < 800,
  });
  
  if (!analyticsResponse) {
    errorRate.add(1);
  }
  
  sleep(1);
  
  // 10. Teste de Cache
  const cacheResponse = check(http.get(`${BASE_URL}/api/caching/status`, 
    { headers }
  ), {
    'cache status is 200': (r) => r.status === 200,
    'cache response time < 100ms': (r) => r.timings.duration < 100,
  });
  
  if (!cacheResponse) {
    errorRate.add(1);
  }
  
  sleep(1);
}

// Função de setup (executada uma vez no início)
export function setup() {
  console.log('🚀 Starting Load Test for Omni Keywords Finder');
  console.log(`📍 Base URL: ${BASE_URL}`);
  console.log(`🔑 API Key: ${API_KEY ? 'Configured' : 'Not configured'}`);
  
  // Verificar se o sistema está online
  const healthResponse = http.get(`${BASE_URL}/health`);
  if (healthResponse.status !== 200) {
    throw new Error(`System is not healthy. Status: ${healthResponse.status}`);
  }
  
  console.log('✅ System is healthy and ready for load testing');
  return { baseUrl: BASE_URL, apiKey: API_KEY };
}

// Função de teardown (executada uma vez no final)
export function teardown(data) {
  console.log('🏁 Load test completed');
  console.log(`📍 Tested URL: ${data.baseUrl}`);
  console.log('📊 Check the results for performance analysis');
}

// Função para lidar com erros
export function handleSummary(data) {
  return {
    'k6-results.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

// Função auxiliar para formatação do resumo
function textSummary(data, options) {
  const { metrics, root_group } = data;
  const { http_req_duration, http_req_failed, http_reqs, vus } = metrics;
  
  return `
🚀 OMNİ KEYWORDS FINDER - LOAD TEST RESULTS
============================================

📊 Performance Metrics:
- Average Response Time: ${http_req_duration.avg.toFixed(2)}ms
- 95th Percentile: ${http_req_duration.values['p(95)'].toFixed(2)}ms
- 99th Percentile: ${http_req_duration.values['p(99)'].toFixed(2)}ms
- Total Requests: ${http_reqs.count}
- Failed Requests: ${http_req_failed.rate * 100}%
- Max Virtual Users: ${vus.max}

🎯 Thresholds:
- Response Time < 500ms: ${http_req_duration.values['p(95)'] < 500 ? '✅ PASS' : '❌ FAIL'}
- Error Rate < 10%: ${http_req_failed.rate < 0.1 ? '✅ PASS' : '❌ FAIL'}

📈 Recommendations:
${http_req_duration.values['p(95)'] > 500 ? '- ⚠️ Consider optimizing response times' : '- ✅ Response times are within acceptable limits'}
${http_req_failed.rate > 0.1 ? '- ⚠️ High error rate detected, investigate issues' : '- ✅ Error rate is acceptable'}

🏁 Test completed successfully!
`;
}

