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
const PREFIX = 'test_kw_load_';

export default function () {
    const url_json = `${API_URL}/exportar_keywords?formato=json`;
    const url_csv = `${API_URL}/exportar_keywords?formato=csv`;
    const res_json = http.get(url_json);
    check(res_json, {
        'status is 200 (json)': (r) => r.status === 200,
        'latency < 1000ms (json)': (r) => r.timings.duration < 1000,
        'is json': (r) => r.headers['Content-Type'].includes('application/json'),
    });
    const res_csv = http.get(url_csv);
    check(res_csv, {
        'status is 200 (csv)': (r) => r.status === 200,
        'latency < 1000ms (csv)': (r) => r.timings.duration < 1000,
        'is csv': (r) => r.headers['Content-Type'].includes('text/csv'),
    });
    sleep(1);
}
// Script stress: 400 usuários simultâneos, 30s, GET JSON/CSV. 