import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 400,
    duration: '30s',
    thresholds: {
        http_req_duration: ['p(95)<1000'],
        http_req_failed: ['rate<0.01'],
    },
};

export default function () {
    const url = 'http://localhost:5000/api/processar_keywords';
    const payload = JSON.stringify({
        keywords: [
            { termo: 'python carga', volume_busca: 100, cpc: 1.2, concorrencia: 0.3, intencao: 'informacional' },
            { termo: 'pytest carga', volume_busca: 80, cpc: 0.9, concorrencia: 0.2, intencao: 'informacional' }
        ]
    });
    const params = { headers: { 'Content-Type': 'application/json' } };
    const res = http.post(url, payload, params);
    check(res, {
        'status is 200': (r) => r.status === 200,
        'latency < 1000ms': (r) => r.timings.duration < 1000,
    });
    sleep(1);
}
// Script stress: 400 usuários simultâneos, 30s, payload realista. 