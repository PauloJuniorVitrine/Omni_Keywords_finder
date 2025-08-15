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

export default function () {
    const url = 'http://localhost:5000/api/externo/google_trends?termo=python+carga';
    const res = http.get(url);
    check(res, {
        'status is 200': (r) => r.status === 200,
        'latency < 1000ms': (r) => r.timings.duration < 1000,
        'is json': (r) => r.headers['Content-Type'].includes('application/json'),
    });
    sleep(1);
}
// Script baseline: 50 usuários simultâneos, 30s, GET Google Trends. 