import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 50,
    duration: '30s',
    thresholds: {
        http_req_duration: ['p(95)<1000'],
        http_req_failed: ['rate<0.01'],
    },
};

const API_URL = __ENV.API_URL || 'http://localhost:5000/api';

function randomKeyword(prefix = 'test_kw_load_') {
    return {
        termo: `${prefix}${Math.floor(Math.random()*100000)}`,
        volume_busca: Math.floor(Math.random()*1000)+1,
        cpc: Math.random()*10,
        concorrencia: Math.random(),
        intencao: 'informacional',
    };
}

export default function () {
    const url = `${API_URL}/processar_keywords`;
    const payload = JSON.stringify({
        keywords: [
            { termo: 'python carga', volume_busca: 100, cpc: 1.2, concorrencia: 0.3, intencao: 'informacional' },
            { termo: 'pytest carga', volume_busca: 80, cpc: 0.9, concorrencia: 0.2, intencao: 'informacional' }
        ],
        enriquecer: true,
        relatorio: true
    });
    const params = { headers: { 'Content-Type': 'application/json' } };
    const res = http.post(url, payload, params);
    check(res, {
        'status is 200': (r) => r.status === 200,
        'latency < 1000ms': (r) => r.timings.duration < 1000,
        'contém keywords': (r) => r.json('keywords') && r.json('keywords').length === 2,
    });
    sleep(1);
}

// Script baseline: 50 usuários simultâneos, 30s, payload realista. 