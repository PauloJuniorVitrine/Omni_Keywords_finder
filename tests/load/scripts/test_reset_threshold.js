import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    vus: 50,
    duration: '3m',
    thresholds: {
        http_req_duration: ['p(95)<1000'],
        http_req_failed: ['rate<0.01'],
    },
};

const API_URL = __ENV.API_URL || 'http://localhost:5000/api';

export default function () {
    let res = http.post(`${API_URL}/test/reset`, null, { headers: { 'Content-Type': 'application/json' } });
    check(res, {
        'status 200': (r) => r.status === 200,
        'latência < 1000ms': (r) => r.timings.duration < 1000,
        'reset ok': (r) => r.json('status') === 'reset_ok',
    });
    sleep(0.5);
} 