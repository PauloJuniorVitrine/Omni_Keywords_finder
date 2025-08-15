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

const API_URL = __ENV.API_URL || 'http://localhost:5000/api';

export default function () {
    const url = `${API_URL}/governanca/logs?event=validacao_keywords`;
    const res = http.get(url);
    check(res, {
        'status is 200': (r) => r.status === 200,
        'latency < 1000ms': (r) => r.timings.duration < 1000,
        'is json': (r) => r.headers['Content-Type'].includes('application/json'),
    });
    sleep(1);
}
// Script stress: 400 usuários simultâneos, 30s, GET logs auditoria. 