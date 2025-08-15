import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    vus: 5,
    duration: '1m',
    thresholds: {
        http_req_duration: ['p(95)<800'],
        http_req_failed: ['rate<0.01'],
    },
};

const API_URL = __ENV.API_URL || 'http://localhost:5000/api';

function randomRegras() {
    return {
        score_minimo: Math.random(),
        blacklist: ["kw_banida" + Math.floor(Math.random()*1000)],
        whitelist: ["kw_livre" + Math.floor(Math.random()*1000)]
    };
}

export default function () {
    const payload = JSON.stringify(randomRegras());
    const params = { headers: { 'Content-Type': 'application/json' } };
    let res = http.post(`${API_URL}/governanca/regras/upload`, payload, params);
    check(res, {
        'status 200': (r) => r.status === 200,
        'latência < 800ms': (r) => r.timings.duration < 800,
        'status ok': (r) => r.json('status') === 'ok',
    });
    sleep(1);
} 